# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0002_auto_20150922_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='contacts_to_mql_conversion',
            field=core.fields.PercentField(default=0, verbose_name=b'Contacts to MQL Conversion', max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
    ]
