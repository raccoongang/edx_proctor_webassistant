# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_exam_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='attempt_status',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
