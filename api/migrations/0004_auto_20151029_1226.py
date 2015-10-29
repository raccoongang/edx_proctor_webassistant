# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0003_auto_20151013_1359'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.CharField(max_length=64)),
                ('object_type', models.CharField(max_length=64, choices=[(b'edxorg', 'Organization'), (b'edxcourse', 'Course'), (b'edxcourserun', 'Courserun')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sso_id', models.IntegerField()),
                ('email', models.EmailField(max_length=254)),
                ('first_name', models.CharField(max_length=60, null=True, blank=True)),
                ('last_name', models.CharField(max_length=60, null=True, blank=True)),
            ],
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='courseId',
            new_name='course_id',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='examCode',
            new_name='exam_code',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='examEndDate',
            new_name='exam_end_date',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='examId',
            new_name='exam_id',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='examName',
            new_name='exam_name',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='examPassword',
            new_name='exam_password',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='examSponsor',
            new_name='exam_sponsor',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='examStartDate',
            new_name='exam_start_date',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='firstName',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='lastName',
            new_name='last_name',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='noOfStudents',
            new_name='no_of_students',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='reviewedExam',
            new_name='reviewed_exam',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='reviewerNotes',
            new_name='reviewer_notes',
        ),
        migrations.RenameField(
            model_name='exam',
            old_name='ssiProduct',
            new_name='ssi_product',
        ),
        migrations.AddField(
            model_name='exam',
            name='course_identify',
            field=models.CharField(db_index=True, max_length=64, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='course_organization',
            field=models.CharField(db_index=True, max_length=64, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='course_run',
            field=models.CharField(db_index=True, max_length=64, null=True, blank=True),
        ),
    ]
