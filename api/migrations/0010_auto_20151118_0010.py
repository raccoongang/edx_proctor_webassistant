# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_eventsession_hash_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='email',
            field=models.EmailField(max_length=60, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='user_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='username',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
