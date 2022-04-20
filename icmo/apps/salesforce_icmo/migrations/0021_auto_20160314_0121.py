# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0020_auto_20160314_0021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesforcevirtualcontacthistory',
            name='order',
            field=models.PositiveSmallIntegerField(default=0, null=True, blank=True),
        ),
    ]
