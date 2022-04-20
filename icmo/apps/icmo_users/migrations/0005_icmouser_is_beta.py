# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('icmo_users', '0004_auto_20150922_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='icmouser',
            name='is_beta',
            field=models.BooleanField(default=False, help_text=b'Designates whether this user can see beta features', verbose_name='Sees Beta Features'),
            preserve_default=True,
        ),
    ]
