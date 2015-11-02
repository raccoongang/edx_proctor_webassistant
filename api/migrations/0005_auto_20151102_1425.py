# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20151029_1226'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exam',
            old_name='examStatus',
            new_name='exam_status',
        ),
    ]
