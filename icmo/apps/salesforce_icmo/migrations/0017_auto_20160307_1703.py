# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0016_auto_20160307_1639'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salesforcevirtualcontact',
            old_name='lead_source',
            new_name='campaign_field_value',
        ),
        migrations.RenameField(
            model_name='salesforcevirtualcontact',
            old_name='lead_source_slug',
            new_name='campaign_field_value_slug',
        ),
    ]
