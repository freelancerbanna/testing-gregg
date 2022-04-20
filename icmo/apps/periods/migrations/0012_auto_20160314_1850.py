# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0011_auto_20160314_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='contacts_to_mql_conversion_actual',
            field=core.fields.PercentField(default=0, verbose_name=b'Contacts to MQL Conversion Actual', max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='contacts_to_mql_conversion_plan',
            field=core.fields.PercentField(default=0, verbose_name=b'Contacts to MQL Conversion Plan', max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='contacts_to_mql_conversion_variance',
            field=core.fields.PercentField(default=0, verbose_name=b'Contacts to MQL Conversion Variance', max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='mql_to_sql_conversion_actual',
            field=core.fields.PercentField(default=0, verbose_name=b'MQL to SQL Conversion Actual', max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='mql_to_sql_conversion_plan',
            field=core.fields.PercentField(default=0, verbose_name=b'MQL to SQL Conversion Plan', max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='mql_to_sql_conversion_variance',
            field=core.fields.PercentField(default=0, verbose_name=b'MQL to SQL Conversion Variance', max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='sql_to_sale_conversion_actual',
            field=core.fields.PercentField(default=0, verbose_name=b'SQL to Sale Conversion Actual', max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='sql_to_sale_conversion_plan',
            field=core.fields.PercentField(default=0, verbose_name=b'SQL to Sale Conversion Plan', max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='sql_to_sale_conversion_variance',
            field=core.fields.PercentField(default=0, verbose_name=b'SQL to Sale Conversion Variance', max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_to_mql_conversion_actual',
            field=core.fields.PercentField(default=0, verbose_name=b'Touches to MQL Conversion Actual', max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_to_mql_conversion_plan',
            field=core.fields.PercentField(default=0, verbose_name=b'Touches to MQL Conversion Plan', max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_to_mql_conversion_variance',
            field=core.fields.PercentField(default=0, verbose_name=b'Touches to MQL Conversion Variance', max_digits=8, decimal_places=1),
        ),
    ]
