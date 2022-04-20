# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_auto_20151207_1749'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyusergroup',
            name='reports',
            field=models.CharField(default=b'none', max_length=50, choices=[(b'none', b'None'), (b'view', b'View'), (b'change', b'Change')]),
        ),
    ]
