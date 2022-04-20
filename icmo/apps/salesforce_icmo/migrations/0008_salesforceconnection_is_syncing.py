# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0007_auto_20160226_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesforceconnection',
            name='is_syncing',
            field=models.BooleanField(default=False),
        ),
    ]
