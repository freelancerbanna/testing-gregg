# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('revenues', '0004_auto_20150930_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='prev_annual',
            field=djmoney.models.fields.MoneyField(decimal_places=0, default=Decimal('0'), editable=False, max_digits=10, verbose_name=b'Last Years Annual Sales', default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='segment',
            name='prev_annual_currency',
            field=djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='segment',
            name='prev_average_sale',
            field=djmoney.models.fields.MoneyField(default=Decimal('0'), verbose_name=b'Last Years Average Sale', max_digits=10, decimal_places=0, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='segment',
            name='prev_average_sale_currency',
            field=djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='segment',
            name='prev_q1',
            field=djmoney.models.fields.MoneyField(default=Decimal('0'), verbose_name=b'Last Years Q1 Sales', max_digits=10, decimal_places=0, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='segment',
            name='prev_q1_currency',
            field=djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='segment',
            name='prev_q2',
            field=djmoney.models.fields.MoneyField(default=Decimal('0'), verbose_name=b'Last Years Q2 Sales', max_digits=10, decimal_places=0, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='segment',
            name='prev_q2_currency',
            field=djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='segment',
            name='prev_q3',
            field=djmoney.models.fields.MoneyField(default=Decimal('0'), verbose_name=b'Last Years Q3 Sales', max_digits=10, decimal_places=0, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='segment',
            name='prev_q3_currency',
            field=djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='segment',
            name='prev_q4',
            field=djmoney.models.fields.MoneyField(default=Decimal('0'), verbose_name=b'Last Years Q4 Sales', max_digits=10, decimal_places=0, default_currency=b'USD'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='segment',
            name='prev_q4_currency',
            field=djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')]),
            preserve_default=True,
        ),
    ]
