# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0011_salesforcevirtualcontact_salesforce_opportunity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesforcevirtualcontact',
            name='salesforce_opportunity',
            field=models.OneToOneField(related_name='virtual_contact', null=True, to='salesforce_icmo.SalesforceOpportunity'),
        ),
    ]
