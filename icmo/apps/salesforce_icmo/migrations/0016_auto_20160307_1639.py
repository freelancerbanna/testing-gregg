# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0015_auto_20160307_1604'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesforcelead',
            name='sfdc_lead_source',
        ),
        migrations.RemoveField(
            model_name='salesforceopportunity',
            name='sfdc_lead_source',
        ),
        migrations.AddField(
            model_name='salesforceaccount',
            name='campaign_field_value',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='salesforcelead',
            name='campaign_field_value',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='salesforceopportunity',
            name='campaign_field_value',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
