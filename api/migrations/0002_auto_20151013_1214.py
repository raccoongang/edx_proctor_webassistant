# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='courseId',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='exam',
            name='examEndDate',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='exam',
            name='examId',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='exam',
            name='examStartDate',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='exam',
            name='firstName',
            field=models.CharField(max_length=60, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='exam',
            name='lastName',
            field=models.CharField(max_length=60, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='exam',
            name='noOfStudents',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
