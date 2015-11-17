# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20151116_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsession',
            name='hash_key',
            field=models.CharField(db_index=True, max_length=128, null=True, blank=True),
        ),
    ]
