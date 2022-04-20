# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0005_budgetlineitem_automatic_distribution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budgetlineitem',
            name='apr_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='apr_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='apr_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='aug_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='aug_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='aug_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='dec_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='dec_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='dec_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='feb_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='feb_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='feb_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='fiscal_year_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='fiscal_year_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='fiscal_year_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='jan_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='jan_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='jan_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='jul_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='jul_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='jul_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='jun_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='jun_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='jun_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='mar_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='mar_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='mar_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='may_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='may_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='may_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='nov_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='nov_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='nov_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='oct_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='oct_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='oct_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q1_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q1_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q1_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q2_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q2_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q2_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q3_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q3_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q3_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q4_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q4_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='q4_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='sep_actual',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='sep_plan',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='budgetlineitem',
            name='sep_variance',
            field=core.fields.DecimalMoneyField(default=Decimal('0'), max_digits=12, decimal_places=2, default_currency=b'USD'),
        ),
    ]
