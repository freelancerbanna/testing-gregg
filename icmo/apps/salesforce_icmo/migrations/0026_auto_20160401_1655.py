# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0025_auto_20160401_1626'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salesforcevirtualcontact',
            options={'ordering': ('created_date',)},
        ),
    ]
