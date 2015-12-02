# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0017_auto_20151202_1100'),
    ]

    operations = [
        migrations.CreateModel(
            name='Journaling',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(db_index=True, choices=[(10, 'API Request from edX'), (5, 'Exam attempt'), (3, 'Start event session'), (7, "Proctor's comment"), (9, 'Call to edX API'), (6, 'Exam status change'), (4, 'Event session status change'), (2, "Proctor's logout"), (1, "Proctor's login"), (8, 'Bulk exam status change')])),
                ('note', models.TextField(null=True, blank=True)),
                ('proctor_ip', models.GenericIPAddressField(null=True, blank=True)),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(blank=True, to='api.EventSession', null=True)),
                ('exam', models.ForeignKey(blank=True, to='api.Exam', null=True)),
                ('proctor', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
