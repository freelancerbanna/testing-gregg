# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0011_auto_20160314_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='apr_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='apr_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='aug_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='aug_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='dec_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='dec_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='feb_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='feb_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='fiscal_year_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='fiscal_year_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jan_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jan_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jul_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jul_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jun_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jun_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='mar_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='mar_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='may_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='may_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='nov_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='nov_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='oct_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='oct_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q1_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q1_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q2_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q2_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q3_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q3_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q4_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q4_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='sep_mql_to_sql_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='sep_sql_to_sale_conversion',
            field=core.fields.PercentField(default=0, max_digits=8, decimal_places=1),
        ),
    ]
