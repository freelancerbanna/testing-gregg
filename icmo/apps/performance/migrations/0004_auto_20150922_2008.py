# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('performance', '0003_auto_20150922_1753'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campaign',
            old_name='fiscal_year_salefs_revenue',
            new_name='fiscal_year_sales_revenue',
        ),
        migrations.RenameField(
            model_name='campaign',
            old_name='fiscal_year_salefs_revenue_currency',
            new_name='fiscal_year_sales_revenue_currency',
        ),
    ]
