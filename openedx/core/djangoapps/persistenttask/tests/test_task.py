u"""
Testing persistent tasks
"""

from __future__ import print_function

from celery import task
from django.test import TestCase

from ..models import FailedTask
from ..task import ReapplicableTask


class ReapplicableTaskTestCase(TestCase):
    """
    Test that persistent tasks save the appropriate values when needed.
    """

    def setUp(self):
        @task(base=ReapplicableTask)
        def exampletask(exception=None):
            u"""
            A simple task for testing persistence
            """
            if exception:
                raise ValueError(u'The example task failed')
            return
        self.exampletask = exampletask
        super(ReapplicableTaskTestCase, self).setUp()

    def test_exampletask_without_failure(self):
        result = self.exampletask.delay()
        result.wait()
        self.assertEqual(result.status, u'SUCCESS')
        self.assertFalse(FailedTask.objects.exists())

    def test_exampletask_with_failure(self):
        result = self.exampletask.delay(exception=True)
        with self.assertRaises(ValueError):
            result.wait()
        self.assertEqual(result.status, u'FAILURE')
        failed_task_object = FailedTask.objects.get()
        # Assert that we get the kind of data we expect
        self.assertEqual(
            failed_task_object.task_name,
            u'openedx.core.djangoapps.persistenttask.tests.test_task.exampletask'
        )
        self.assertEqual(failed_task_object.argstring, u'[]')
        self.assertEqual(failed_task_object.args, [])
        self.assertEqual(failed_task_object.kwargstring, u'{"exception": true}')
        self.assertEqual(failed_task_object.kwargs, {u'exception': True})
        self.assertEqual(failed_task_object.exc, u"ValueError(u'The example task failed',)")
        # einfo contains the traceback
        self.assertIn(u"raise ValueError(u'The example task failed')\n", failed_task_object.einfo)
        self.assertIsNone(failed_task_object.datetime_resolved)

    def test_retried_task_does_not_persist(self):
        result = self.exampletask.delay(exception=True, _persistent_task_retry=True)
        with self.assertRaises(ValueError):
            result.wait()
        self.assertEqual(result.status, u'FAILURE')
        self.assertFalse(FailedTask.objects.exists())

    def test_persists_when_called_with_wrong_args(self):
        result = self.exampletask.delay(err=True)
        with self.assertRaises(TypeError):
            result.wait()
        self.assertEqual(result.status, u'FAILURE')
        self.assertTrue(FailedTask.objects.exists())
