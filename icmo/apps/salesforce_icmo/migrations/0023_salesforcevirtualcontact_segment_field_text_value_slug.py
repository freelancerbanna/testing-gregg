# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0022_auto_20160314_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesforcevirtualcontact',
            name='segment_field_text_value_slug',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
