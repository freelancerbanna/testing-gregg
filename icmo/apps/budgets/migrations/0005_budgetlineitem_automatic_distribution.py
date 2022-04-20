# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0004_auto_20150922_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetlineitem',
            name='automatic_distribution',
            field=models.BooleanField(default=True),
        ),
    ]
