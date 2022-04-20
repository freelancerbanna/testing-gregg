# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='demoaccount',
            name='password',
            field=models.CharField(default=b'icmo', max_length=255),
            preserve_default=True,
        ),
    ]
