# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('periods', '0004_auto_20150922_1756'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='period',
            name='achieved_revenue_actual',
        ),
        migrations.RemoveField(
            model_name='period',
            name='achieved_revenue_actual_currency',
        ),
        migrations.RemoveField(
            model_name='period',
            name='achieved_revenue_plan',
        ),
        migrations.RemoveField(
            model_name='period',
            name='achieved_revenue_plan_currency',
        ),
        migrations.RemoveField(
            model_name='period',
            name='achieved_revenue_variance',
        ),
        migrations.RemoveField(
            model_name='period',
            name='achieved_revenue_variance_currency',
        ),
    ]
