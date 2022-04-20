# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0026_auto_20160401_1655'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salesforceevent',
            options={'ordering': ('event_date',)},
        ),
        migrations.AlterField(
            model_name='salesforcevirtualcontact',
            name='salesforce_account',
            field=models.ForeignKey(related_name='virtual_contact', to='salesforce_icmo.SalesforceAccount', null=True),
        ),
        migrations.AlterField(
            model_name='salesforcevirtualcontact',
            name='salesforce_opportunity',
            field=models.ForeignKey(related_name='virtual_contact', to='salesforce_icmo.SalesforceOpportunity', null=True),
        ),
    ]
