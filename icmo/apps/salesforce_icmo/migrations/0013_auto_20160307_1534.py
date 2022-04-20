# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0012_auto_20160304_2353'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesforceconnection',
            name='lead_source_field',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='salesforceconnection',
            name='opportunity_source_field',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='salesforceconnection',
            name='source_fallback_to_lead_source',
            field=models.BooleanField(default=True),
        ),
    ]
