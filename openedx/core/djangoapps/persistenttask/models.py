"""
Models to support persistent tasks.
"""

import json

from django.db import models


class FailedTask(models.Model):
    """
    Representation of tasks that have failed
    """
    task_name = models.CharField(max_length=255)
    task_id = models.CharField(max_length=255)
    argstring = models.CharField(max_length=4096, blank=True)
    kwargstring = models.CharField(max_length=4096, blank=True)
    exc = models.CharField(max_length=255)
    einfo = models.TextField()
    datetime_failed = models.DateTimeField()
    datetime_resolved = models.DateTimeField(blank=True, null=True, default=None, db_index=True)

    def __unicode__(self):
        return u'FailedTask: {task_name}, args={args}, kwargs={kwargs} ({resolution})'.format(
            task_name=self.task_name,
            args=self.args,
            kwargs=self.kwargs,
            resolution=u"not resolved" if self.datetime_resolved is None else "resolved"
        )

    @property
    def args(self):
        """
        Getter for positional arguments provided to the task.
        """
        return json.loads(self.argstring)

    @args.setter
    def args(self, value):
        """
        Setter for positional arguments provided to the task.
        """
        if not isinstance(value, (list, tuple)):
            raise TypeError(u'Value must be a JSON-serializable list or tuple')
        self.argstring = json.dumps(value)

    @property
    def kwargs(self):
        """
        Getter for keyword arguments provided to the task.
        """
        return json.loads(self.kwargstring)

    @kwargs.setter
    def kwargs(self, value):
        """
        Setter for keyword arguments provided to the task.
        """
        if not isinstance(value, dict):
            raise TypeError(u'Value must be a JSON-serializable dict')
        self.kwargstring = json.dumps(value)
