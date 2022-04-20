# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0009_salesforceleadhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesforceVirtualContactHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=255)),
                ('status_source', models.CharField(max_length=255, choices=[(b'lead', b'Lead'), (b'opportunity', b'Opportunity')])),
                ('updated', models.DateTimeField()),
                ('connection', models.ForeignKey(related_name='virtual_contacts_history', to='salesforce_icmo.SalesforceConnection')),
                ('virtual_contact', models.ForeignKey(related_name='history', to='salesforce_icmo.SalesforceVirtualContact')),
            ],
        ),
    ]
