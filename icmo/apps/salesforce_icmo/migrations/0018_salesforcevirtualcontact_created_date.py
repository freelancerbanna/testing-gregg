# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0017_auto_20160307_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesforcevirtualcontact',
            name='created_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
