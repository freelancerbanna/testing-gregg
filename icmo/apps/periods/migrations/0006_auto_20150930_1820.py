# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0005_auto_20150922_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='average_sale_actual',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=2, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='average_sale_plan',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=2, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='average_sale_variance',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=2, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_mql_actual',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=2, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_mql_plan',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=2, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_mql_variance',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=2, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_sql_actual',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=2, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_sql_plan',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=2, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='cost_per_sql_variance',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=2, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_actual',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='period',
            name='touches_plan',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
