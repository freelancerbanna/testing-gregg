# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0018_salesforcevirtualcontact_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesforceconnection',
            name='sfdc_end_statuses',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.CharField(max_length=255, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='salesforceconnection',
            name='sfdc_statuses_to_ignore',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.CharField(max_length=255, blank=True), blank=True),
        ),
    ]
