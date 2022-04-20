# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('icmo_users', '0002_auto_20150908_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='icmouser',
            name='company',
            field=models.CharField(default='', help_text=b'Company Name Override', max_length=255, blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='icmouser',
            name='last_revenue_plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='revenues.RevenuePlan', null=True),
            preserve_default=True,
        ),
    ]
