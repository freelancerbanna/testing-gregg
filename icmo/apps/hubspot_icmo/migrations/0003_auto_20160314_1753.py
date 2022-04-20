# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('hubspot_icmo', '0002_auto_20160117_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hubspotdeal',
            name='amount',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=2, default_currency=b'USD'),
        ),
        migrations.AlterField(
            model_name='hubspotrevenueplancampaignmonthperformance',
            name='sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
    ]
