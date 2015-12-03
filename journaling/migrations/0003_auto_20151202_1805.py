# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('journaling', '0002_auto_20151202_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journaling',
            name='proctor',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
