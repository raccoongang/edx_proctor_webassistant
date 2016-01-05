# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('person', '0001_initial'),
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
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_org', models.CharField(max_length=60)),
                ('course_id', models.CharField(max_length=60)),
                ('course_run', models.CharField(max_length=60)),
                ('display_name', models.CharField(max_length=60)),
                ('course_name', models.CharField(max_length=128, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('testing_center', models.CharField(max_length=128)),
                ('course_event_id', models.CharField(max_length=128, null=True, blank=True)),
                ('status', models.CharField(default=b'in_progress', max_length=11, choices=[(b'in_progress', 'In progress'), (b'archived', 'Archived')])),
                ('hash_key', models.CharField(db_index=True, max_length=128, null=True, blank=True)),
                ('notify', models.TextField(null=True, blank=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('exam_name', models.CharField(max_length=128, null=True, blank=True)),
                ('course', models.ForeignKey(to='proctoring.Course')),
                ('proctor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exam_code', models.CharField(unique=True, max_length=60)),
                ('organization', models.CharField(max_length=60)),
                ('duration', models.IntegerField()),
                ('reviewed_exam', models.CharField(max_length=60)),
                ('reviewer_notes', models.CharField(max_length=60, null=True, blank=True)),
                ('exam_password', models.CharField(max_length=60)),
                ('exam_sponsor', models.CharField(max_length=60)),
                ('exam_name', models.CharField(max_length=60)),
                ('ssi_product', models.CharField(max_length=60)),
                ('exam_start_date', models.DateTimeField(null=True, blank=True)),
                ('exam_end_date', models.DateTimeField(null=True, blank=True)),
                ('actual_start_date', models.DateTimeField(null=True, blank=True)),
                ('actual_end_date', models.DateTimeField(null=True, blank=True)),
                ('no_of_students', models.IntegerField(null=True, blank=True)),
                ('exam_id', models.CharField(max_length=64, null=True, blank=True)),
                ('course_identify', models.CharField(max_length=64, null=True, blank=True)),
                ('first_name', models.CharField(max_length=60, null=True, blank=True)),
                ('last_name', models.CharField(max_length=60, null=True, blank=True)),
                ('email', models.EmailField(max_length=60, null=True, blank=True)),
                ('user_id', models.IntegerField(null=True, blank=True)),
                ('username', models.CharField(max_length=50, null=True, blank=True)),
                ('exam_status', models.CharField(default=b'new', max_length=8, choices=[(b'new', 'Not started'), (b'started', 'Started'), (b'failed', 'Failed'), (b'finished', 'Finished')])),
                ('attempt_status', models.CharField(max_length=20, null=True, blank=True)),
                ('course', models.ForeignKey(to='proctoring.Course')),
                ('event', models.ForeignKey(blank=True, to='proctoring.EventSession', null=True)),
                ('proctor', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('student', models.ForeignKey(to='person.Student')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='exam',
            field=models.ForeignKey(to='proctoring.Exam'),
        ),
        migrations.CreateModel(
            name='ArchivedEventSession',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('proctoring.eventsession',),
        ),
        migrations.CreateModel(
            name='InProgressEventSession',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('proctoring.eventsession',),
        ),
    ]
