# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0008_auto_20160202_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='mql_to_sql_conversion',
            field=models.DecimalField(default=Decimal('10'), verbose_name='MQL to SQL Conversion', max_digits=4, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='program',
            name='sql_to_sale_conversion',
            field=models.DecimalField(default=Decimal('15'), verbose_name='SQL to Sale Conversion', max_digits=4, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='program',
            name='touches_per_contact',
            field=models.PositiveSmallIntegerField(default=10),
        ),
        migrations.AlterField(
            model_name='program',
            name='touches_to_mql_conversion',
            field=models.DecimalField(default=Decimal('1'), verbose_name='Touches to MQL Conversion', max_digits=4, decimal_places=1),
        ),
    ]
