# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0005_auto_20160125_2320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='budget',
            field=djmoney.models.fields.MoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD'),
        ),
    ]
