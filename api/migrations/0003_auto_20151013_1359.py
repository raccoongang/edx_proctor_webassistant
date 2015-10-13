# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20151013_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='examCode',
            field=models.CharField(unique=True, max_length=60),
        ),
    ]
