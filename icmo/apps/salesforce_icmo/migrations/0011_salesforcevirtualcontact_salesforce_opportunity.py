# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0010_salesforcevirtualcontacthistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesforcevirtualcontact',
            name='salesforce_opportunity',
            field=models.OneToOneField(related_name='virtual_contact_from_opportunity', null=True, to='salesforce_icmo.SalesforceAccount'),
        ),
    ]
