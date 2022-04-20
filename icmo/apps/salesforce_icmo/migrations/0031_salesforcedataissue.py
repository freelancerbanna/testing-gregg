# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0030_salesforceconnection_salesforce_timezone'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesforceDataIssue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.CharField(max_length=50, choices=[(b'info', b'Info'), (b'info', b'Warning'), (b'info', b'Error')])),
                ('message', models.TextField()),
                ('connection', models.ForeignKey(to='salesforce_icmo.SalesforceConnection')),
                ('salesforce_account', models.ForeignKey(blank=True, to='salesforce_icmo.SalesforceAccount', null=True)),
                ('salesforce_lead', models.ForeignKey(blank=True, to='salesforce_icmo.SalesforceLead', null=True)),
                ('salesforce_opportunity', models.ForeignKey(blank=True, to='salesforce_icmo.SalesforceOpportunity', null=True)),
                ('virtual_contact', models.ForeignKey(blank=True, to='salesforce_icmo.SalesforceVirtualContact', null=True)),
            ],
        ),
    ]
