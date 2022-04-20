from __future__ import division  # this line enables currency division

from decimal import Decimal, ROUND_HALF_DOWN
from math import ceil, floor

from django.db import models
from django.db.models import Sum, Avg
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from djmoney.models.fields import MoneyField, Money
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from ordered_model.models import OrderedModel

from core import calculators
from core.fields import PercentField
from core.helpers import round_to_whole_number
from core.models import IcmoModel, DenormalizedIcmoParentsMixin, ActiveRelatedTreeManager


class ProgramTypes(object):
    CATEGORY = 'category'
    PROGRAM = 'program'

    choices = (
        (CATEGORY, 'Category'),
        (PROGRAM, 'Program')
    )


class Program(MPTTModel, OrderedModel, DenormalizedIcmoParentsMixin, IcmoModel):
    class Meta:
        unique_together = ('slug', 'segment')

    icmo_level = 'program'
    icmo_parent_levels = ('company', 'segment', 'revenue_plan')

    company = models.ForeignKey('companies.Company')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan')
    segment = models.ForeignKey('revenues.Segment', related_name='programs', blank=False)
    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name')

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    item_type = models.CharField(max_length=10, default=ProgramTypes.PROGRAM,
                                 choices=ProgramTypes.choices)

    touches_per_contact = models.PositiveSmallIntegerField(default=10)
    touches_to_mql_conversion = models.DecimalField(
        _('Touches to MQL Conversion'), max_digits=4, decimal_places=1, default=Decimal('1'))
    mql_to_sql_conversion = models.DecimalField(
        _('MQL to SQL Conversion'), max_digits=4, decimal_places=1, default=Decimal('10'))
    sql_to_sale_conversion = models.DecimalField(
        _('SQL to Sale Conversion'), max_digits=4, decimal_places=1, default=Decimal('15'))
    cost_per_mql = MoneyField(max_digits=10, decimal_places=2, default_currency='USD',
                              default=Decimal(100))
    marketing_mix = models.PositiveSmallIntegerField(default=0)
    marketing_mix_locked = models.BooleanField(default=False)

    # cached computed
    sales_revenue = MoneyField('Sales Goal', max_digits=10, decimal_places=0,
                               default_currency='USD',
                               default=0, editable=False)
    sales = models.PositiveIntegerField(default=0, editable=False)
    sql = models.PositiveIntegerField(default=0, editable=False)
    mql = models.PositiveIntegerField(default=0, editable=False)
    contacts = models.PositiveIntegerField(default=0, editable=False)
    touches = models.PositiveIntegerField(default=0, editable=False)
    budget = MoneyField(max_digits=10, decimal_places=0, default_currency='USD', default=0)
    fixed_budget = models.BooleanField(default=False)
    cost_per_sql = MoneyField(max_digits=10, decimal_places=2, default_currency='USD', default=0,
                              editable=False)
    roi = models.IntegerField(default=0, editable=False)
    contacts_to_mql_conversion = PercentField('Contacts to MQL Conversion')

    objects = ActiveRelatedTreeManager()

    @property
    def campaigns(self):
        return self.campaign_set.filter(is_active=True)

    @property
    def q1_budget(self):
        budget = round_to_whole_number(
            self.budget.amount * self.segment.goal_q1_percent_of_annual)
        return Money(budget, self.budget.currency)

    @property
    def q2_budget(self):
        budget = round_to_whole_number(
            self.budget.amount * self.segment.goal_q2_percent_of_annual)
        return Money(budget, self.budget.currency)

    @property
    def q3_budget(self):
        budget = round_to_whole_number(
            self.budget.amount * self.segment.goal_q3_percent_of_annual)
        return Money(budget, self.budget.currency)

    @property
    def q4_budget(self):
        budget = round_to_whole_number(
            self.budget.amount * self.segment.goal_q4_percent_of_annual)
        return Money(budget, self.budget.currency)

    @property
    def max_cost_per_mql(self):
        # budget cannot exceed sales_revenue
        if self.sales_revenue.amount and self.mql:
            max_cost = self.sales_revenue.amount / self.mql
            return Decimal(max_cost.quantize(Decimal('.01'), rounding=ROUND_HALF_DOWN))
        return Decimal('0')

    def recalc(self):
        # Enforce sanity only on programs not channels
        self.touches_per_contact = max(self.touches_per_contact, 1)
        self.touches_to_mql_conversion = max(self.touches_to_mql_conversion, Decimal('0.1'))
        self.mql_to_sql_conversion = max(self.mql_to_sql_conversion, Decimal('0.1'))
        self.sql_to_sale_conversion = max(self.sql_to_sale_conversion, Decimal('0.1'))
        self.cost_per_mql = max(self.cost_per_mql.amount, Decimal('0.001'))

        for field_name in ('roi', 'contacts', 'mql',
                           'sql', 'cost_per_sql', 'sales', 'sales_revenue'):
            setattr(self, field_name, Decimal(0))
        if not self.fixed_budget:
            self.budget = Decimal(0)

        # Cascading calculation dependencies, order matters.
        if self.marketing_mix and self.segment.goal_annual.amount:
            self.sales_revenue = int(
                ceil(Decimal(self.marketing_mix) / 100 * self.segment.goal_annual.amount))

        if self.sales_revenue and self.segment.average_sale.amount:
            self.sales = int(ceil(self.sales_revenue.amount / self.segment.average_sale.amount))

        if self.sql_to_sale_conversion and self.sales:
            self.sql = int(floor(self.sales / (Decimal(self.sql_to_sale_conversion) / 100)))

        if self.mql_to_sql_conversion and self.sql:
            self.mql = int(floor(self.sql / (Decimal(self.mql_to_sql_conversion) / 100)))

        if self.touches_to_mql_conversion and self.mql:
            self.touches = int(ceil(self.mql / (Decimal(self.touches_to_mql_conversion) / 100)))

        if self.touches and self.touches_per_contact:
            self.contacts = int(ceil(self.touches / self.touches_per_contact))

        if self.fixed_budget:
            if self.mql:
                self.cost_per_mql = self.budget.amount / self.mql
        else:
            if self.cost_per_mql.amount and self.mql:
                self.budget = self.mql * self.cost_per_mql

        self.contacts_to_mql_conversion = calculators.contacts_to_mql_conversion(self.mql,
                                                                                 self.contacts)
        self.cost_per_sql = calculators.cost_per_sql(self.budget, self.sql)
        self.roi = calculators.roi(self.sales_revenue, self.budget)

    def recalc_category(self):
        # Sum the month budget and actuals for all line items under this
        # category.  get_descendants does not work with new items, thus the pk check.

        sum_fields = ['budget', 'contacts', 'touches', 'mql', 'sql', 'sales', 'sales_revenue',
                      'marketing_mix']
        avg_fields = ['touches_per_contact', 'touches_to_mql_conversion', 'mql_to_sql_conversion',
                      'sql_to_sale_conversion', 'cost_per_mql']
        for field in sum_fields + avg_fields:
            setattr(self, field, 0)

        sums = [Sum(field) for field in sum_fields]
        averages = [Avg(field) for field in avg_fields]
        # workaround for bug in mptt
        # qs = Program.objects.filter(parent=self)
        if self.get_descendant_count():
            qs = self.get_descendants()
        else:
            qs = self.get_children()

        sum_aggregates = qs.filter(is_active=True).exclude(
            item_type=ProgramTypes.CATEGORY).aggregate(*sums)
        for field in sum_fields:
            setattr(self, '%s' % field, sum_aggregates['%s__sum' % field] or 0)

        avg_aggregates = qs.aggregate(*averages)
        for field in avg_fields:
            setattr(self, '%s' % field, avg_aggregates['%s__avg' % field] or 0)

        self.roi = calculators.roi(self.sales_revenue, self.budget)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.item_type == ProgramTypes.PROGRAM:
            self.recalc()
        elif self.item_type == ProgramTypes.CATEGORY and self.pk:
            self.recalc_category()
        created = not self.pk
        super(Program, self).save(*args, **kwargs)
        if created and self.item_type == ProgramTypes.CATEGORY:
            self.save()

            # redis_publisher = RedisPublisher(facility='programs', broadcast=True)
            # payload = ProgramSerializer(self).data
            # payload['kendo_action'] = 'push-create' if created else 'push-update'
            # message = RedisMessage(JSONRenderer().render(payload))
            # redis_publisher.publish_message(message)

    def delete(self, *args, **kwargs):
        for child in Program.objects.filter(parent=self):
            child.parent = self.parent
            child.save()
        super(Program, self).delete(*args, **kwargs)
