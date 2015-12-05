# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20151202_1100'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('event_status', models.CharField(max_length=60)),
                ('event_start', models.IntegerField()),
                ('event_finish', models.IntegerField()),
                ('duration', models.IntegerField(null=True, blank=True)),
                ('exam', models.ForeignKey(to='api.Exam')),
            ],
        ),
        migrations.AlterField(
            model_name='permission',
            name='object_type',
            field=models.CharField(max_length=64, choices=[(b'edxorg', 'Organization'), (b'edxcourse', 'Course'), (b'*', b'*'), (b'edxcourserun', 'Courserun')]),
        ),
    ]
