# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Journaling',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('journaling_type', models.IntegerField(db_index=True, choices=[(1, "Proctor's login"), (2, "Proctor's logout"), (3, 'Start event session'), (4, 'Event session status change'), (5, 'Exam attempt'), (6, 'Exam status change'), (7, "Proctor's comment"), (8, 'Bulk exam status change'), (9, 'Call to edX API'), (10, 'API Request from edX')])),
                ('note', models.TextField(null=True, blank=True)),
                ('proctor_ip', models.GenericIPAddressField(null=True, blank=True)),
                ('datetime', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
