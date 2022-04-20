# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesforceevent',
            name='virtual_contact',
            field=models.ForeignKey(related_name='events', to='salesforce_icmo.SalesforceVirtualContact'),
        ),
    ]
