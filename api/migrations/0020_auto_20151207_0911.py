# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_permission_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventsession',
            name='status',
            field=models.CharField(default=b'in_progress', max_length=11, choices=[(b'in_progress', 'In progress'), (b'archived', 'Archived')]),
        ),
    ]
