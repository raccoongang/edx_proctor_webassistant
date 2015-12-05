# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_auto_20151205_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='role',
            field=models.CharField(default=b'proctor', max_length=10, choices=[(b'proctor', 'Proctor'), (b'instructor', 'Instructor')]),
        ),
    ]
