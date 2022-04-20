# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0028_auto_20160402_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesforceopportunity',
            name='sfdc_account_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
