# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
        ('budgets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetlineitem',
            name='company',
            field=models.ForeignKey(to='companies.Company'),
            preserve_default=True,
        ),
    ]
