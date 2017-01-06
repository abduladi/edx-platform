u"""
Celery utility code for persistent tasks.
"""

from datetime import datetime
import json

from celery import Task
import pytz
import six

from .models import FailedTask


def serialize_args(args):
    u"""
    Combine arglist into a json string.
    """
    if not isinstance(args, (tuple, list)):
        raise TypeError(u'Args must be a tuple or list')
    return json.dumps(args)


def serialize_kwargs(kwargs):
    u"""
    Combine kwarg dict into a json string
    """
    if not isinstance(kwargs, dict):
        raise TypeError(u'Kwargs must be a dict')
    return json.dumps(kwargs)


# pylint: disable=abstract-method
class ReapplicableTask(Task):
    u"""
    Custom Celery Task base class that persists task data on failure.
    """
    persistent_retry_attribute = u'_persistent_task_retry'

    def __call__(self, *args, **kwargs):
        if hasattr(self, self.persistent_retry_attribute):
            # The task is instantiated once per worker, not once per invocation,
            # so we need to manually clean up any stale persistent retry
            # attributes before we call the task.
            delattr(self, self.persistent_retry_attribute)
        if self.persistent_retry_attribute in kwargs:
            setattr(self, self.persistent_retry_attribute, kwargs.pop(self.persistent_retry_attribute))
        super(ReapplicableTask, self).__call__(*args, **kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        u"""
        If the task fails, persist a record of the task.
        """
        if not getattr(self, self.persistent_retry_attribute, False):
            FailedTask.objects.create(
                task_name=self.name,
                task_id=task_id,
                argstring=serialize_args(args),
                kwargstring=serialize_kwargs(kwargs),
                exc=repr(exc),
                einfo=six.text_type(einfo),
                datetime_failed=pytz.utc.localize(datetime.utcnow()),
            )
