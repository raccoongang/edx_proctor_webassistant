# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_auto_20151216_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsession',
            name='course_name',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='eventsession',
            name='exam_name',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]
