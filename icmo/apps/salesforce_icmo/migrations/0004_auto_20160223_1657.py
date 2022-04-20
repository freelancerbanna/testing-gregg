# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0003_auto_20160223_1605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesforceconnection',
            name='segment_field',
        ),
        migrations.RemoveField(
            model_name='salesforceconnection',
            name='segment_field_type',
        ),
        migrations.AddField(
            model_name='salesforceconnection',
            name='account_segment_field',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salesforceconnection',
            name='account_segment_field_type',
            field=models.CharField(default='', max_length=255, choices=[(b'text_match', b'Text Match'), (b'numeric', b'Numeric')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salesforceconnection',
            name='lead_segment_field',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salesforceconnection',
            name='lead_segment_field_type',
            field=models.CharField(default='', max_length=255, choices=[(b'text_match', b'Text Match'), (b'numeric', b'Numeric')]),
            preserve_default=False,
        ),
    ]
