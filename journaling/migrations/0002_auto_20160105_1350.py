# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('proctoring', '0001_initial'),
        ('journaling', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='journaling',
            name='event',
            field=models.ForeignKey(blank=True, to='proctoring.EventSession', null=True),
        ),
        migrations.AddField(
            model_name='journaling',
            name='exam',
            field=models.ForeignKey(blank=True, to='proctoring.Exam', null=True),
        ),
        migrations.AddField(
            model_name='journaling',
            name='proctor',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
