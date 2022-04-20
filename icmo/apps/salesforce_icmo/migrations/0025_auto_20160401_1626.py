# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0024_auto_20160331_2348'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salesforcerevenueplanmapentry',
            options={'ordering': ('revenue_plan', 'segment_value', 'source_value')},
        ),
        migrations.AddField(
            model_name='salesforceaccount',
            name='sfdc_name',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='salesforceconnection',
            name='salesforce_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='salesforcelead',
            name='sfdc_company',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='salesforcelead',
            name='sfdc_name',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='salesforceopportunity',
            name='sfdc_name',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='salesforcerevenueplanmapentry',
            unique_together=set([('connection', 'salesforce_revenue_plan', 'segment_value', 'source_value')]),
        ),
    ]
