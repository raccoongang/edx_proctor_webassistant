# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journaling', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journaling',
            name='proctor',
            field=models.ForeignKey(blank=True, to='default.UserSocialAuth', null=True),
        ),
    ]
