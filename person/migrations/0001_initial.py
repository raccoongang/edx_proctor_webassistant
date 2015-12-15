# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.CharField(max_length=64)),
                ('object_type', models.CharField(max_length=64, choices=[(b'edxorg', 'Organization'), (b'edxcourse', 'Course'), (b'*', b'*'), (b'edxcourserun', 'Courserun')])),
                ('role', models.CharField(default=b'proctor', max_length=10, choices=[(b'proctor', 'Proctor'), (b'instructor', 'Instructor')])),
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
    ]
