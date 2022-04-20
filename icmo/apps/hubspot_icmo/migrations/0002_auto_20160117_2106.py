# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hubspot_icmo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hubspotcontact',
            name='conversion_event_name',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='hubspotcontact',
            name='hs_first_conversion_event_name',
            field=models.URLField(max_length=2048, blank=True),
        ),
        migrations.AddField(
            model_name='hubspotcontact',
            name='hs_recent_conversion_event_name',
            field=models.URLField(max_length=2048, blank=True),
        ),
        migrations.AddField(
            model_name='hubspotcontact',
            name='original_campaign',
            field=models.CharField(default=b'Unknown', max_length=255),
        ),
        migrations.AddField(
            model_name='hubspotcontact',
            name='original_source',
            field=models.CharField(default=b'Unknown', max_length=255),
        ),
    ]
