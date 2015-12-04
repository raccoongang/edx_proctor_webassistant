# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journaling', '0003_auto_20151202_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journaling',
            name='type',
            field=models.IntegerField(db_index=True, choices=[(1, "Proctor's login"), (2, "Proctor's logout"), (3, 'Start event session'), (4, 'Event session status change'), (5, 'Exam attempt'), (6, 'Exam status change'), (7, "Proctor's comment"), (8, 'Bulk exam status change'), (9, 'Call to edX API'), (10, 'API Request from edX')]),
        ),
    ]
