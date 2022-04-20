# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models
import dirtyfields.dirtyfields
import django_extensions.db.fields
from decimal import Decimal
import django.utils.timezone
from django.conf import settings
import django.core.validators
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('revenues', '0001_initial'),
        ('companies', '0002_auto_20150908_2126'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('name', models.CharField(max_length=150)),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from=b'name', editable=False, blank=True)),
                ('touches_per_contact', models.PositiveSmallIntegerField(default=10, validators=[django.core.validators.MinValueValidator(1)])),
                ('touches_to_mql_conversion', models.DecimalField(default=Decimal('1'), verbose_name='Touches to MQL Conversion', max_digits=4, decimal_places=1, validators=[django.core.validators.MinValueValidator(Decimal('0.1'))])),
                ('mql_to_sql_conversion', models.DecimalField(default=Decimal('10'), verbose_name='MQL to SQL Conversion', max_digits=4, decimal_places=1, validators=[django.core.validators.MinValueValidator(Decimal('0.1'))])),
                ('sql_to_sale_conversion', models.DecimalField(default=Decimal('15'), verbose_name='SQL to Sale Conversion', max_digits=4, decimal_places=1, validators=[django.core.validators.MinValueValidator(Decimal('0.1'))])),
                ('cost_per_mql_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('cost_per_mql', djmoney.models.fields.MoneyField(default=Decimal('100'), max_digits=10, decimal_places=2, default_currency=b'USD')),
                ('marketing_mix', models.PositiveSmallIntegerField(default=0)),
                ('marketing_mix_locked', models.BooleanField(default=False)),
                ('goal_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('goal', djmoney.models.fields.MoneyField(decimal_places=0, default=Decimal('0'), editable=False, max_digits=10, verbose_name=b'Sales Goal', default_currency=b'USD')),
                ('sales', models.PositiveIntegerField(default=0, editable=False)),
                ('sql', models.PositiveIntegerField(default=0, editable=False)),
                ('mql', models.PositiveIntegerField(default=0, editable=False)),
                ('contacts', models.PositiveIntegerField(default=0, editable=False)),
                ('touches', models.PositiveIntegerField(default=0, editable=False)),
                ('budget_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('budget', djmoney.models.fields.MoneyField(default=Decimal('0'), editable=False, max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('cost_per_sql_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('cost_per_sql', djmoney.models.fields.MoneyField(default=Decimal('0'), editable=False, max_digits=10, decimal_places=2, default_currency=b'USD')),
                ('roi', models.SmallIntegerField(default=0, editable=False)),
                ('company', models.ForeignKey(to='companies.Company')),
                ('modified_by', models.ForeignKey(related_name='program_last_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('revenue_plan', models.ForeignKey(to='revenues.RevenuePlan')),
                ('segment', models.ForeignKey(related_name='programs', to='revenues.Segment')),
            ],
            options={
            },
            bases=(core.models.DenormalizedIcmoParentsMixin, dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='program',
            unique_together=set([('slug', 'segment')]),
        ),
    ]
