# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models
import dirtyfields.dirtyfields
import djmoney.models.fields
import django_extensions.db.fields
from decimal import Decimal
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RevenuePlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('name', models.CharField(default='Revenue Plan 2015', max_length=150)),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from=b'name', editable=False, blank=True)),
                ('plan_year', models.IntegerField(default=2015, choices=[(2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020)])),
                ('is_default', models.BooleanField(default=False)),
                ('plan_type', models.CharField(default=b'draft', max_length=20, choices=[(b'draft', b'Draft'), (b'published', b'Published'), (b'archived', b'Archived')])),
                ('company', models.ForeignKey(to='companies.Company')),
                ('modified_by', models.ForeignKey(related_name='revenueplan_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_revenueplan', 'View revenue plan'),),
            },
            bases=(core.models.DenormalizedIcmoParentsMixin, dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('name', models.CharField(max_length=150)),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from=b'name', editable=False, blank=True)),
                ('average_sale_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('average_sale', djmoney.models.fields.MoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('goal_q1_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('goal_q1', djmoney.models.fields.MoneyField(default=Decimal('0'), verbose_name=b'Q1 Sales Goal', max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('goal_q2_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('goal_q2', djmoney.models.fields.MoneyField(default=Decimal('0'), verbose_name=b'Q2 Sales Goal', max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('goal_q3_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('goal_q3', djmoney.models.fields.MoneyField(default=Decimal('0'), verbose_name=b'Q3 Sales Goal', max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('goal_q4_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('goal_q4', djmoney.models.fields.MoneyField(default=Decimal('0'), verbose_name=b'Q4 Sales Goal', max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('goal_annual_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('goal_annual', djmoney.models.fields.MoneyField(decimal_places=0, default=Decimal('0'), editable=False, max_digits=10, verbose_name='Annual Sales Goal', default_currency=b'USD')),
                ('company', models.ForeignKey(to='companies.Company')),
                ('modified_by', models.ForeignKey(related_name='segment_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('revenue_plan', models.ForeignKey(to='revenues.RevenuePlan')),
            ],
            options={
                'ordering': ('-goal_annual',),
            },
            bases=(core.models.DenormalizedIcmoParentsMixin, dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='segment',
            unique_together=set([('slug', 'revenue_plan')]),
        ),
        migrations.AlterUniqueTogether(
            name='revenueplan',
            unique_together=set([('slug', 'company')]),
        ),
    ]
