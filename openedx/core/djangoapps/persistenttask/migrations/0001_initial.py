# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FailedTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_name', models.CharField(max_length=255)),
                ('task_id', models.CharField(max_length=255)),
                ('argstring', models.CharField(max_length=4096, blank=True)),
                ('kwargstring', models.CharField(max_length=4096, blank=True)),
                ('exc', models.CharField(max_length=255)),
                ('einfo', models.TextField()),
                ('datetime_failed', models.DateTimeField()),
                ('datetime_resolved', models.DateTimeField(default=None, null=True, db_index=True, blank=True)),
            ],
        ),
    ]
