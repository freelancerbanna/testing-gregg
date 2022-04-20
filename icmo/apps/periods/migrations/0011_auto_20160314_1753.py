# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0010_auto_20160304_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='average_sale_actual',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='average_sale_plan',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='average_sale_variance',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='budget_actual',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='budget_plan',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='budget_variance',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_mql_actual',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_mql_plan',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_mql_variance',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_sql_actual',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_sql_plan',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_sql_variance',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='sales_revenue_actual',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='sales_revenue_plan',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='period',
            name='sales_revenue_variance',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
    ]
