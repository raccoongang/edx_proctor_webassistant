# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_eventsession_course_run'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventsession',
            name='testing_center',
            field=models.CharField(max_length=128),
        ),
    ]
