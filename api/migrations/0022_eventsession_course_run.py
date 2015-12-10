# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_inprogresseventsession'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsession',
            name='course_run',
            field=models.CharField(db_index=True, max_length=64, null=True, blank=True),
        ),
    ]
