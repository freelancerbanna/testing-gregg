from __future__ import division

from collections import OrderedDict
from decimal import Decimal

from dirtyfields import DirtyFieldsMixin
from django.db import models
from django.db.models import Sum, Avg
from django.utils.functional import cached_property
from django_extensions.db.models import TimeStampedModel

from budgets.models import BudgetLineItem
from companies.models import Company
from core import calculators as calc
from core.fields import DefaultMoneyField, PercentField
from core.helpers import MONTHS_3, QUARTERS, round_to_two_decimal_places
from core.models import DenormalizedIcmoParentsMixin, ICMO_LEVELS
from leads.models import Program
from performance.models import Campaign
from revenues.models import RevenuePlan
from revenues.models import Segment


class ResolutionTypes(object):
    CAMPAIGN = 'campaign'
    CUSTOM_BUDGET_LINE_ITEM = 'custom_budget_line_item'
    PROGRAM = 'program'
    # category = 'category'
    SEGMENT = 'segment'
    REVENUE_PLAN = 'revenue_plan'
    COMPANY = 'company'

    choices = (
        (CAMPAIGN, 'Campaign'),
        (CUSTOM_BUDGET_LINE_ITEM, 'Custom Budget Line Item'),
        (PROGRAM, 'Program'),
        (SEGMENT, 'Segment'),
        (REVENUE_PLAN, 'Revenue Plan'),
        (COMPANY, 'Company'),
    )


RESOLUTION_TO_CLASS_MAP = dict(
    campaign=Campaign,
    custom_budget_line_item=BudgetLineItem,
    program=Program,
    segment=Segment,
    revenue_plan=RevenuePlan,
    company=Company
)


class PeriodTypes(object):
    MONTH = 'month'
    QUARTER = 'quarter'
    YEAR = 'year'
    choices = (
        (MONTH, 'Month'),
        (QUARTER, 'Quarter'),
        (YEAR, 'Year'),
    )


PERIOD_CHOICES = (
    ('jan', 'jan'), ('feb', 'feb'), ('mar', 'mar'), ('apr', 'apr'), ('may', 'may'),
    ('jun', 'jun'), ('jul', 'jul'), ('aug', 'aug'), ('sep', 'sep'), ('oct', 'oct'),
    ('nov', 'nov'), ('dec', 'dec'),
    ('q1', 'q1'), ('q2', 'q2'), ('q3', 'q3'), ('q4', 'q4'),
    ('year', 'year')
)
RESOLUTION_VALUES = dict(
    campaign=['performance_actuals'],
    custom_budget_line_item=['budget_actuals', 'budget_plans'],
    program=['budget_actuals', 'budget_plans', 'performance_plans', 'performance_actuals'],
    segment=['budget_plans', 'budget_actuals', 'performance_plans', 'performance_actuals'],
    revenue_plan=['budget_plans', 'budget_actuals', 'performance_plans', 'performance_actuals'],
    company=['budget_plans', 'budget_actuals', 'performance_plans', 'performance_actuals'],
)


class Period(DirtyFieldsMixin, DenormalizedIcmoParentsMixin, TimeStampedModel):
    class Meta:
        ordering = ('order',)

    is_attached = True

    unique_id = models.CharField(max_length=255, unique=True)

    order = models.PositiveSmallIntegerField(default=0)

    # FINANCIAL'S
    period = models.CharField(max_length=10, db_index=True, choices=PERIOD_CHOICES)
    period_type = models.CharField(max_length=50, choices=PeriodTypes.choices)
    company = models.ForeignKey('companies.Company')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan', blank=True, null=True)
    segment = models.ForeignKey('revenues.Segment', blank=True, null=True)
    # category = models.ForeignKey('budgets.BudgetLineItem', blank=True, null=True)
    program = models.ForeignKey('leads.Program', blank=True, null=True)
    custom_budget_line_item = models.ForeignKey('budgets.BudgetLineItem', related_name='+',
                                                blank=True, null=True)
    campaign = models.ForeignKey('performance.Campaign', blank=True, null=True)

    resolution = models.CharField(max_length=100, choices=ResolutionTypes.choices)

    budget_plan = DefaultMoneyField()
    budget_actual = DefaultMoneyField()
    budget_variance = DefaultMoneyField()

    roi_plan = models.IntegerField(default=0, editable=False)
    roi_actual = models.IntegerField(default=0, editable=False)
    roi_variance = models.IntegerField(default=0, editable=False)

    # PERFORMANCE METRICS
    # PLAN
    contacts_plan = models.IntegerField(default=0)
    mql_plan = models.IntegerField('MQLs Plan', default=0)
    sql_plan = models.IntegerField('SQLs Plan', default=0)
    sales_plan = models.IntegerField(default=0)
    sales_revenue_plan = DefaultMoneyField()
    touches_plan = models.IntegerField(default=0)

    cost_per_mql_plan = DefaultMoneyField(decimal_places=2)
    cost_per_sql_plan = DefaultMoneyField(decimal_places=2)
    average_sale_plan = DefaultMoneyField(decimal_places=2)
    touches_to_mql_conversion_plan = PercentField('Touches to MQL Conversion Plan')
    contacts_to_mql_conversion_plan = PercentField('Contacts to MQL Conversion Plan')
    mql_to_sql_conversion_plan = PercentField('MQL to SQL Conversion Plan')
    sql_to_sale_conversion_plan = PercentField('SQL to Sale Conversion Plan')
    touches_per_contact_plan = models.IntegerField(default=0)

    # ACTUAL
    contacts_actual = models.IntegerField(default=0)
    mql_actual = models.IntegerField('MQLs Actual', default=0)
    sql_actual = models.IntegerField('SQLs Actual', default=0)
    sales_actual = models.IntegerField(default=0)
    sales_revenue_actual = DefaultMoneyField()
    touches_actual = models.IntegerField(default=0)

    cost_per_mql_actual = DefaultMoneyField(decimal_places=2)
    cost_per_sql_actual = DefaultMoneyField(decimal_places=2)
    average_sale_actual = DefaultMoneyField(decimal_places=2)
    touches_to_mql_conversion_actual = PercentField('Touches to MQL Conversion Actual')
    contacts_to_mql_conversion_actual = PercentField('Contacts to MQL Conversion Actual')
    mql_to_sql_conversion_actual = PercentField('MQL to SQL Conversion Actual')
    sql_to_sale_conversion_actual = PercentField('SQL to Sale Conversion Actual')
    touches_per_contact_actual = models.IntegerField(default=0)

    # VARIANCE
    contacts_variance = models.IntegerField(default=0)
    mql_variance = models.IntegerField('MQLs Variance', default=0)
    sql_variance = models.IntegerField('SQLs Variance', default=0)
    sales_variance = models.IntegerField(default=0)
    sales_revenue_variance = DefaultMoneyField()
    touches_variance = models.IntegerField(default=0)

    cost_per_mql_variance = DefaultMoneyField(decimal_places=2)
    cost_per_sql_variance = DefaultMoneyField(decimal_places=2)
    average_sale_variance = DefaultMoneyField(decimal_places=2)
    touches_to_mql_conversion_variance = PercentField('Touches to MQL Conversion Variance')
    contacts_to_mql_conversion_variance = PercentField('Contacts to MQL Conversion Variance')
    mql_to_sql_conversion_variance = PercentField('MQL to SQL Conversion Variance')
    sql_to_sale_conversion_variance = PercentField('SQL to Sale Conversion Variance')
    touches_per_contact_variance = models.IntegerField(default=0)

    def recalc(self):
        # Compute Other Fields
        self.cost_per_mql_actual = calc.cost_per_mql(self.budget_actual, self.mql_actual)
        self.cost_per_sql_actual = calc.cost_per_sql(self.budget_actual, self.sql_actual)
        self.average_sale_actual = calc.average_sale(self.sales_revenue_actual, self.sales_actual)
        self.touches_to_mql_conversion_actual = calc.touches_to_mql_conversion(self.mql_actual,
                                                                               self.touches_actual)
        self.contacts_to_mql_conversion_actual = calc.contacts_to_mql_conversion(self.mql_actual,
                                                                                 self.contacts_actual)
        self.mql_to_sql_conversion_actual = calc.mql_to_sql_conversion(self.sql_actual,
                                                                       self.mql_actual)
        self.sql_to_sale_conversion_actual = calc.sql_to_sale_conversion(self.sales_actual,
                                                                         self.sql_actual)
        self.touches_per_contact_actual = calc.touches_per_contact(self.touches_actual,
                                                                   self.contacts_actual)
        self.roi_actual = calc.roi(self.sales_revenue_actual, self.budget_actual)
        # Compute Variance Fields
        for field in self.icmo_fields:
            setattr(self, "%s_variance" % field,
                    getattr(self, "%s_plan" % field) - getattr(self, "%s_actual" % field))

    def set_aggregate_values(self, aggregates):
        for key, value in aggregates.items():
            field_name, agtype = key.split('__')
            if not value:
                value = 0
            if agtype == 'avg':
                value = Decimal(value)
            setattr(self, field_name, value)
        return True

    def merge_aggregate_values(self, list_of_aggregates):
        output = dict()
        for aggregates in list_of_aggregates:
            for key, value in aggregates.items():
                if not value:
                    # If there are no records to aggregate the values will all be None
                    value = Decimal(0)
                if key in output:
                    if key.endswith('__sum'):
                        output[key] += value
                    elif key.endswith('__avg'):
                        output[key] = round_to_two_decimal_places((output[key] + Decimal(value)) / 2)
                    else:
                        raise ValueError("Unknown aggregate in %s" % key)
                else:
                    output[key] = value
        return output

    def get_aggregate_values(self, qs, resolution_to_aggregate):
        aggregate_fields = []

        if 'budget_plans' in RESOLUTION_VALUES[resolution_to_aggregate]:
            aggregate_fields.append(Sum('budget_plan'))

        if 'budget_actuals' in RESOLUTION_VALUES[resolution_to_aggregate]:
            aggregate_fields.append(Sum('budget_actual'))

        if 'performance_plans' in RESOLUTION_VALUES[resolution_to_aggregate]:
            aggregate_fields.extend([
                Sum('contacts_plan'),
                Sum('mql_plan'),
                Sum('sql_plan'),
                Sum('sales_plan'),
                Sum('touches_plan'),
                Sum('sales_revenue_plan'),
                Avg('cost_per_mql_plan'),
                Avg('cost_per_sql_plan'),
                Avg('average_sale_plan'),
                Avg('touches_to_mql_conversion_plan'),
                Avg('mql_to_sql_conversion_plan'),
                Avg('sql_to_sale_conversion_plan'),
                Avg('touches_per_contact_plan'),
                Avg('roi_plan'),
            ])
        if 'performance_actuals' in RESOLUTION_VALUES[resolution_to_aggregate]:
            aggregate_fields.extend([
                Sum('mql_actual'),
                Sum('sql_actual'),
                Sum('sales_actual'),
                Sum('sales_revenue_actual'),
                # the rest are calculated
                # todo consider effect of compounding calculations and rounding errors
                # as opposed to calculate once and then sum
            ])

        return qs.aggregate(*aggregate_fields)

    def _get_period_type(self):
        if self.period in MONTHS_3:
            return 'month'
        elif self.period in QUARTERS:
            return 'quarter'
        elif self.period == 'year':
            return 'year'
        raise ValueError('Unknown period: %s' % self.period)

    @cached_property
    def quarter(self):
        if self.period_type != 'month':
            raise AttributeError("Only months have quarters")
        return self.company.get_fiscal_quarter_by_month_name(self.period)

    @cached_property
    def absolute_path(self):
        """
        Returns the dictionary of objects required to resolve this period
        :rtype : dict
        """
        output = OrderedDict()
        for level in ICMO_LEVELS.keys():
            output[level] = getattr(self, level)
        return output

    @cached_property
    def path(self):
        """
        Returns the dictionary of objects that will resolve this period AND all descendants
        :rtype : dict
        """
        path = OrderedDict()
        for level, value in self.absolute_path.items():
            if value:
                path[level] = value
        return path

    @cached_property
    def icmo_fields(self):
        """
        Returns all fields in the period that are of the plan, actual, variance set.
        :return: list
        """
        return [x.replace('_variance', '') for x in self._meta.get_all_field_names()
                if x.endswith('_variance')]

    @property
    def icmo_level(self):
        return self.resolution

    def get_resolution(self):
        for level in ICMO_LEVELS.keys():
            if hasattr(self, "%s_id" % level) and getattr(self, "%s_id" % level):
                return level
        raise ValueError("Could not determine resolution")

    def _generate_unique_id(self):
        # 'company', 'revenue_plan', 'segment', 'program', 'custom_budget_line_item',
        # 'campaign', 'period_type', 'period', 'resolution'

        return ".".join([str(x) for x in [
            self.company_id, self.revenue_plan_id or 0, self.segment_id or 0, self.program_id or 0,
                             self.custom_budget_line_item_id or 0, self.campaign_id or 0,
            self.period_type,
            self.period, self.resolution]]
                        )

    def _get_sort_order(self):
        if self.period_type == PeriodTypes.MONTH:
            return self.company.fiscal_months_by_name.index(self.period)
        elif self.period_type == PeriodTypes.QUARTER:
            return QUARTERS.index(self.period)
        return 0

    def save(self, *args, **kwargs):
        if self.pk and 'period' in self.get_dirty_fields():
            raise AttributeError("Period can not be changed once set.")

        self.period_type = self._get_period_type()
        self.resolution = self.get_resolution()

        # A level (just Company right now) may have no parents, so we don't perform this step then.
        if self.icmo_parent_level:
            # Periods are attached to icmo objects at the same level so they need to manually
            # attach to
            # their immediate parent because it is not necessarily passed in as an argument
            # Ex a Campaign period probably is created with just the Campaign object,
            # not the Program
            #  object as well.
            setattr(self, self.icmo_parent_level,
                    getattr(self.icmo_object, self.icmo_parent_level))

            # Set the rest of the icmo parents
            self.set_icmo_parents()

        # There are two mutually exclusive types of aggregation: aggregation of stats into quarters
        # and years, and aggregation of descendant stats for months.
        if self.period_type in ('quarter', 'year'):
            self.aggregate_smaller_periods()
        elif self.resolution in ('company', 'revenue_plan', 'segment', 'program'):
            # aggregate descendants
            self.aggregate_immediate_descendants()
        self.recalc()
        self.unique_id = self._generate_unique_id()

        # set the sort order
        self.order = self._get_sort_order()
        super(Period, self).save(*args, **kwargs)

    def aggregate_smaller_periods(self):
        qs = Period.objects.filter(resolution=self.resolution, **self.absolute_path)
        if self.period_type == 'quarter':
            months = self.company.fiscal_quarters_by_name[self.period]
            qs = qs.filter(period_type='month', period__in=months)
        elif self.period_type == 'year':
            qs = qs.filter(period_type='quarter')
        self.set_aggregate_values(self.get_aggregate_values(qs, self.resolution))
        return True

    def aggregate_immediate_descendants(self):
        if not self.icmo_child_levels:
            return
        list_of_aggregates = []
        for child in self.icmo_child_levels:
            qs = Period.objects.filter(resolution=child, period=self.period,
                                       **self.path)
            list_of_aggregates.append(self.get_aggregate_values(qs, child))
        aggregates = self.merge_aggregate_values(list_of_aggregates)
        self.set_aggregate_values(aggregates)
        return True

    def __unicode__(self):
        return "%s %s" % (self.icmo_object_type, self.period)
