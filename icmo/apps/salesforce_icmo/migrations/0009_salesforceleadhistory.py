# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0008_salesforceconnection_is_syncing'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesforceLeadHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sfdc_id', models.CharField(max_length=255)),
                ('sfdc_field', models.CharField(max_length=255)),
                ('sfdc_old_value', models.CharField(max_length=255, blank=True)),
                ('sfdc_new_value', models.CharField(max_length=255, blank=True)),
                ('sfdc_created_date', models.DateTimeField()),
                ('sfdc_is_deleted', models.BooleanField()),
                ('connection', models.ForeignKey(related_name='lead_history', to='salesforce_icmo.SalesforceConnection')),
                ('salesforce_lead', models.ForeignKey(related_name='history', to='salesforce_icmo.SalesforceLead')),
            ],
        ),
    ]
