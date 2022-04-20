# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0014_salesforceconnection_account_source_field'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salesforceconnection',
            old_name='account_source_field',
            new_name='account_campaign_field',
        ),
        migrations.RenameField(
            model_name='salesforceconnection',
            old_name='source_fallback_to_lead_source',
            new_name='campaign_fallback_to_lead_source',
        ),
        migrations.RenameField(
            model_name='salesforceconnection',
            old_name='lead_source_field',
            new_name='lead_campaign_field',
        ),
        migrations.RenameField(
            model_name='salesforceconnection',
            old_name='opportunity_source_field',
            new_name='opportunity_campaign_field',
        ),
    ]
