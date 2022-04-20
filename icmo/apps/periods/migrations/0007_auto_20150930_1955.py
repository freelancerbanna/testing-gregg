# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0006_auto_20150930_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='period',
            name='contacts_to_mql_conversion_actual',
            field=core.fields.PercentField(default=0, verbose_name=b'Contacts to MQL Conversion Actual', max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='period',
            name='contacts_to_mql_conversion_plan',
            field=core.fields.PercentField(default=0, verbose_name=b'Contacts to MQL Conversion Plan', max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='period',
            name='contacts_to_mql_conversion_variance',
            field=core.fields.PercentField(default=0, verbose_name=b'Contacts to MQL Conversion Variance', max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_to_mql_conversion_actual',
            field=core.fields.PercentField(default=0, verbose_name=b'Touches to MQL Conversion Actual', max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_to_mql_conversion_plan',
            field=core.fields.PercentField(default=0, verbose_name=b'Touches to MQL Conversion Plan', max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_to_mql_conversion_variance',
            field=core.fields.PercentField(default=0, verbose_name=b'Touches to MQL Conversion Variance', max_digits=4, decimal_places=1),
            preserve_default=True,
        ),
    ]
