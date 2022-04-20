# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0027_auto_20160401_2227'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesforceaccount',
            name='sfdc_is_deleted',
        ),
        migrations.RemoveField(
            model_name='salesforcelead',
            name='sfdc_is_deleted',
        ),
        migrations.RemoveField(
            model_name='salesforceopportunity',
            name='sfdc_is_deleted',
        ),
    ]
