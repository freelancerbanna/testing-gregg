# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0013_auto_20160307_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesforceconnection',
            name='account_source_field',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
