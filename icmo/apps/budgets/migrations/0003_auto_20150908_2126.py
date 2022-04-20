# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('revenues', '0001_initial'),
        ('budgets', '0002_budgetlineitem_company'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('leads', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetlineitem',
            name='modified_by',
            field=models.ForeignKey(related_name='budgetlineitem_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='budgetlineitem',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', blank=True, to='budgets.BudgetLineItem', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='budgetlineitem',
            name='program',
            field=models.OneToOneField(null=True, blank=True, to='leads.Program'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='budgetlineitem',
            name='revenue_plan',
            field=models.ForeignKey(to='revenues.RevenuePlan'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='budgetlineitem',
            name='segment',
            field=models.ForeignKey(to='revenues.Segment'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='budgetlineitem',
            unique_together=set([('slug', 'segment')]),
        ),
    ]
