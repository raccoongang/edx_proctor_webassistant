# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20151122_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='event',
            field=models.ForeignKey(blank=True, to='api.EventSession', null=True),
        ),
    ]
