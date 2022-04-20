# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal
import core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce_icmo', '0021_auto_20160314_0121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesforcerevenueplancampaignmonthperformance',
            name='sales_revenue',
            field=core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=13, decimal_places=0, default_currency=b'USD'),
        ),
    ]
