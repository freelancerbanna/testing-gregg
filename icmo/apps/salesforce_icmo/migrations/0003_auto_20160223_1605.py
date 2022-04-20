# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0002_auto_20160209_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesforceconnection',
            name='segment_field',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='salesforceconnection',
            name='segment_field_type',
            field=models.CharField(blank=True, max_length=255, choices=[(b'text_match', b'Text Match'), (b'numeric', b'Numeric')]),
        ),
    ]
