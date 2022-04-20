# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0004_auto_20160223_1657'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salesforceaccount',
            old_name='sfdc_industry',
            new_name='segment_field_text_value',
        ),
        migrations.RenameField(
            model_name='salesforcelead',
            old_name='sfdc_industry',
            new_name='segment_field_text_value',
        ),
        migrations.RenameField(
            model_name='salesforcevirtualcontact',
            old_name='industry',
            new_name='segment_field_text_value',
        ),
        migrations.RemoveField(
            model_name='salesforceaccount',
            name='sfdc_annual_revenue',
        ),
        migrations.RemoveField(
            model_name='salesforcelead',
            name='sfdc_annual_revenue',
        ),
        migrations.RemoveField(
            model_name='salesforcerevenueplan',
            name='segment_mapping_field',
        ),
        migrations.RemoveField(
            model_name='salesforcerevenueplansegmentmap',
            name='mapping_field',
        ),
        migrations.RemoveField(
            model_name='salesforcevirtualcontact',
            name='annual_revenue',
        ),
        migrations.AddField(
            model_name='salesforceaccount',
            name='segment_field_numeric_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2),
        ),
        migrations.AddField(
            model_name='salesforcelead',
            name='segment_field_numeric_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2),
        ),
        migrations.AddField(
            model_name='salesforcevirtualcontact',
            name='segment_field_numeric_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2),
        ),
    ]
