# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20151211_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='actual_end_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='actual_start_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
