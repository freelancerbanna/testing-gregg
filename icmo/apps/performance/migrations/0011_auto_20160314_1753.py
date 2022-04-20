# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0010_remove_campaign_sep_touches_per_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='apr_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='apr_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='aug_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='aug_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='dec_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='dec_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='feb_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='feb_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='fiscal_year_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='fiscal_year_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jan_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jan_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jul_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jul_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jun_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='jun_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='mar_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='mar_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='may_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='may_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='nov_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='nov_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='oct_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='oct_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q1_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q1_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q2_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q2_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q3_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q3_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q4_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='q4_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='sep_average_sale',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='sep_sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
    ]
