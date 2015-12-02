# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_exam_attempt_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsession',
            name='comment',
            field=models.TextField(null=True, blank=True),
        ),
    ]
