# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0003_auto_20150922_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='gantttask',
            name='completed_date',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
