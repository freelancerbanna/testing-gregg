# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demos', '0002_demoaccount_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='demoaccount',
            name='template',
            field=models.CharField(default=b'10M', max_length=255, choices=[(b'10M', b'$10 Million Company')]),
            preserve_default=True,
        ),
    ]
