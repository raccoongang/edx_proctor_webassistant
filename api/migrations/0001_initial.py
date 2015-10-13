# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('examCode', models.CharField(max_length=60)),
                ('organization', models.CharField(max_length=60)),
                ('duration', models.IntegerField()),
                ('reviewedExam', models.CharField(max_length=60)),
                ('reviewerNotes', models.CharField(max_length=60)),
                ('examPassword', models.CharField(max_length=60)),
                ('examSponsor', models.CharField(max_length=60)),
                ('examName', models.CharField(max_length=60)),
                ('ssiProduct', models.CharField(max_length=60)),
                ('examStartDate', models.DateTimeField()),
                ('examEndDate', models.DateTimeField()),
                ('noOfStudents', models.IntegerField()),
                ('examId', models.CharField(max_length=64)),
                ('courseId', models.CharField(max_length=64)),
                ('firstName', models.CharField(max_length=60)),
                ('lastName', models.CharField(max_length=60)),
                ('examStatus', models.CharField(default=b'new', max_length=8, choices=[(b'new', 'Not started'), (b'started', 'Started'), (b'failed', 'Failed'), (b'finished', 'Finished')])),
            ],
        ),
    ]
