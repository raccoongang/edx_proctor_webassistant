# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_exam_proctor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='reviewer_notes',
            field=models.CharField(max_length=60, null=True, blank=True),
        ),
    ]
