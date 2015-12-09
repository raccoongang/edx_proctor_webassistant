# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_auto_20151207_0911'),
    ]

    operations = [
        migrations.CreateModel(
            name='InProgressEventSession',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('api.eventsession',),
        ),
    ]
