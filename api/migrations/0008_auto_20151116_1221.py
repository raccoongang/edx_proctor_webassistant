# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0007_auto_20151103_1330'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('testing_center', models.CharField(max_length=64)),
                ('course_id', models.CharField(max_length=128, null=True, blank=True)),
                ('course_event_id', models.CharField(max_length=128, null=True, blank=True)),
                ('status', models.CharField(default=b'in_progress', max_length=11, choices=[(b'in_progress', 'In progress'), (b'finished', 'Finished')])),
                ('notify', models.TextField(null=True, blank=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('proctor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='exam',
            name='proctor',
        ),
    ]
