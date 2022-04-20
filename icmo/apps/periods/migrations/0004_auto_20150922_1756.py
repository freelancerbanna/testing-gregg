# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0003_auto_20150922_1747'),
    ]

    operations = [
        migrations.RenameField(
            model_name='period',
            old_name='total_sales_value_actual',
            new_name='sales_revenue_actual',
        ),
        migrations.RenameField(
            model_name='period',
            old_name='total_sales_value_actual_currency',
            new_name='sales_revenue_actual_currency',
        ),
        migrations.RenameField(
            model_name='period',
            old_name='total_sales_value_plan',
            new_name='sales_revenue_plan',
        ),
        migrations.RenameField(
            model_name='period',
            old_name='total_sales_value_plan_currency',
            new_name='sales_revenue_plan_currency',
        ),
        migrations.RenameField(
            model_name='period',
            old_name='total_sales_value_variance',
            new_name='sales_revenue_variance',
        ),
        migrations.RenameField(
            model_name='period',
            old_name='total_sales_value_variance_currency',
            new_name='sales_revenue_variance_currency',
        ),
    ]
