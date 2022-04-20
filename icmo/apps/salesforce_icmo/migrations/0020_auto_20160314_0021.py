# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0019_auto_20160313_0518'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesforcevirtualcontacthistory',
            name='is_virtual',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='salesforcevirtualcontacthistory',
            name='order',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
