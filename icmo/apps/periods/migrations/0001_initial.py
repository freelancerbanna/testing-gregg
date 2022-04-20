# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.models
import dirtyfields.dirtyfields
import djmoney.models.fields
import django_extensions.db.fields
from decimal import Decimal
import core.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('revenues', '0001_initial'),
        ('budgets', '0002_budgetlineitem_company'),
        ('companies', '0002_auto_20150908_2126'),
        ('leads', '0001_initial'),
        ('performance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('period', models.CharField(db_index=True, max_length=10, choices=[(b'jan', b'jan'), (b'feb', b'feb'), (b'mar', b'mar'), (b'apr', b'apr'), (b'may', b'may'), (b'jun', b'jun'), (b'jul', b'jul'), (b'aug', b'aug'), (b'sep', b'sep'), (b'oct', b'oct'), (b'nov', b'nov'), (b'dec', b'dec'), (b'q1', b'q1'), (b'q2', b'q2'), (b'q3', b'q3'), (b'q4', b'q4'), (b'year', b'year')])),
                ('period_type', models.CharField(max_length=50, choices=[(b'month', b'Month'), (b'quarter', b'Quarter'), (b'year', b'Fiscal Year')])),
                ('resolution', models.CharField(max_length=100, choices=[(b'campaign', b'Campaign'), (b'custom_budget_line_item', b'Custom Budget Line Item'), (b'program', b'Program'), (b'segment', b'Segment'), (b'revenue_plan', b'Revenue Plan'), (b'company', b'Company')])),
                ('budget_plan_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('budget_plan', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('budget_actual_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('budget_actual', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('budget_variance_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('budget_variance', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('achieved_revenue_plan_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('achieved_revenue_plan', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('achieved_revenue_actual_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('achieved_revenue_actual', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('achieved_revenue_variance_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('achieved_revenue_variance', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('roi_plan', models.SmallIntegerField(default=0, editable=False)),
                ('roi_actual', models.SmallIntegerField(default=0, editable=False)),
                ('roi_variance', models.SmallIntegerField(default=0, editable=False)),
                ('contacts_plan', models.IntegerField(default=0)),
                ('mql_plan', models.IntegerField(default=0, verbose_name=b'MQLs Plan')),
                ('sql_plan', models.IntegerField(default=0, verbose_name=b'SQLs Plan')),
                ('sales_plan', models.IntegerField(default=0)),
                ('total_sales_value_plan_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('total_sales_value_plan', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('touches_plan', models.PositiveIntegerField(default=0, editable=False)),
                ('cost_per_mql_plan_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('cost_per_mql_plan', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('cost_per_sql_plan_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('cost_per_sql_plan', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('average_sale_plan_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('average_sale_plan', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('touches_to_mql_conversion_plan', core.fields.PercentField(default=0, verbose_name=b'MQL to SQL Conversion Plan', max_digits=4, decimal_places=1)),
                ('mql_to_sql_conversion_plan', core.fields.PercentField(default=0, verbose_name=b'MQL to SQL Conversion Plan', max_digits=4, decimal_places=1)),
                ('sql_to_sale_conversion_plan', core.fields.PercentField(default=0, verbose_name=b'SQL to Sale Conversion Plan', max_digits=4, decimal_places=1)),
                ('touches_per_contact_plan', models.PositiveSmallIntegerField(default=0)),
                ('contacts_actual', models.IntegerField(default=0)),
                ('mql_actual', models.IntegerField(default=0, verbose_name=b'MQLs Actual')),
                ('sql_actual', models.IntegerField(default=0, verbose_name=b'SQLs Actual')),
                ('sales_actual', models.IntegerField(default=0)),
                ('total_sales_value_actual_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('total_sales_value_actual', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('touches_actual', models.PositiveIntegerField(default=0, editable=False)),
                ('cost_per_mql_actual_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('cost_per_mql_actual', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('cost_per_sql_actual_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('cost_per_sql_actual', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('average_sale_actual_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('average_sale_actual', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('touches_to_mql_conversion_actual', core.fields.PercentField(default=0, verbose_name=b'MQL to SQL Conversion Actual', max_digits=4, decimal_places=1)),
                ('mql_to_sql_conversion_actual', core.fields.PercentField(default=0, verbose_name=b'MQL to SQL Conversion Actual', max_digits=4, decimal_places=1)),
                ('sql_to_sale_conversion_actual', core.fields.PercentField(default=0, verbose_name=b'SQL to Sale Conversion Actual', max_digits=4, decimal_places=1)),
                ('touches_per_contact_actual', models.PositiveSmallIntegerField(default=0)),
                ('contacts_variance', models.IntegerField(default=0)),
                ('mql_variance', models.IntegerField(default=0, verbose_name=b'MQLs Variance')),
                ('sql_variance', models.IntegerField(default=0, verbose_name=b'SQLs Variance')),
                ('sales_variance', models.IntegerField(default=0)),
                ('total_sales_value_variance_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('total_sales_value_variance', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('touches_variance', models.PositiveIntegerField(default=0)),
                ('cost_per_mql_variance_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('cost_per_mql_variance', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('cost_per_sql_variance_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('cost_per_sql_variance', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('average_sale_variance_currency', djmoney.models.fields.CurrencyField(default=b'USD', max_length=3, editable=False, choices=[(b'USD', 'US Dollar')])),
                ('average_sale_variance', core.fields.DefaultMoneyField(default=Decimal('0'), max_digits=10, decimal_places=0, default_currency=b'USD')),
                ('touches_to_mql_conversion_variance', core.fields.PercentField(default=0, verbose_name=b'MQL to SQL Conversion Variance', max_digits=4, decimal_places=1)),
                ('mql_to_sql_conversion_variance', core.fields.PercentField(default=0, verbose_name=b'MQL to SQL Conversion Variance', max_digits=4, decimal_places=1)),
                ('sql_to_sale_conversion_variance', core.fields.PercentField(default=0, verbose_name=b'SQL to Sale Conversion Variance', max_digits=4, decimal_places=1)),
                ('touches_per_contact_variance', models.PositiveSmallIntegerField(default=0)),
                ('campaign', models.ForeignKey(blank=True, to='performance.Campaign', null=True)),
                ('company', models.ForeignKey(to='companies.Company')),
                ('custom_budget_line_item', models.ForeignKey(related_name='+', blank=True, to='budgets.BudgetLineItem', null=True)),
                ('program', models.ForeignKey(blank=True, to='leads.Program', null=True)),
                ('revenue_plan', models.ForeignKey(blank=True, to='revenues.RevenuePlan', null=True)),
                ('segment', models.ForeignKey(blank=True, to='revenues.Segment', null=True)),
            ],
            options={
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, core.models.DenormalizedIcmoParentsMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='period',
            unique_together=set([('company', 'revenue_plan', 'segment', 'program', 'custom_budget_line_item', 'campaign', 'period_type', 'period')]),
        ),
    ]
