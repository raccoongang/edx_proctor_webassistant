# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_exam_proctor'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='eventsession',
            unique_together=set([('course_id', 'course_event_id')]),
        ),
    ]
