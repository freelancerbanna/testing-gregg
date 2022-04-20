# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0006_auto_20160224_0110'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salesforceconnection',
            old_name='lead_segment_field_type',
            new_name='segment_field_type',
        ),
        migrations.RemoveField(
            model_name='salesforceconnection',
            name='account_segment_field_type',
        ),
        migrations.AddField(
            model_name='salesforceconnection',
            name='opportunity_segment_field',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='salesforceopportunity',
            name='segment_field_numeric_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2),
        ),
        migrations.AddField(
            model_name='salesforceopportunity',
            name='segment_field_text_value',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
