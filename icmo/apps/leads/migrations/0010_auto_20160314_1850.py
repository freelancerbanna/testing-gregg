# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0009_auto_20160204_0310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, verbose_name=b'Contacts to MQL Conversion', max_digits=8, decimal_places=1),
        ),
    ]
