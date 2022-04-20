# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0031_salesforcedataissue'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesforceconnection',
            name='currency_conversion',
            field=models.BooleanField(default=False, help_text=b'Enable this if you are using currency conversion in your Salesforce account.'),
        ),
        migrations.AddField(
            model_name='salesforceconnection',
            name='take_oldest_opportunity_date',
            field=models.BooleanField(default=True, help_text=b'Sometimes the close date on an opportunity may be set to a date earlier than the create date, for example when recording past sales.  When enabled this will ensure that the SQL (and the MQL if virtual) will be set to the same date as the Close Date if it is earlier.'),
        ),
        migrations.AlterField(
            model_name='salesforceconnection',
            name='salesforce_url',
            field=models.URLField(help_text=b'The base URL of your salesforce account', blank=True),
        ),
    ]
