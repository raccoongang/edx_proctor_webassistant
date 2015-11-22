# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20151120_1126'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='eventsession',
            unique_together=set([]),
        ),
    ]
