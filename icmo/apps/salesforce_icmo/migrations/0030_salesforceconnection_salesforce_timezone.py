# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0029_auto_20160402_2050'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesforceconnection',
            name='salesforce_timezone',
            field=models.CharField(default='UTC', max_length=50),
            preserve_default=False,
        ),
    ]
