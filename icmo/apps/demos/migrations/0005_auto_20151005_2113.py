# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demos', '0004_auto_20150922_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demoaccount',
            name='template',
            field=models.CharField(default=b'10M', max_length=255, choices=[(b'10M', b'$10 Million Company'), (b'4M', b'$4 Million Company')]),
            preserve_default=True,
        ),
    ]
