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
                ('firstName', models.CharField(max_length=60, null=True, blank=True)),
                ('lastName', models.CharField(max_length=60, null=True, blank=True)),
            ],
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
