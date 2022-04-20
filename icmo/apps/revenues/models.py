from __future__ import division  # this line enables currency division

import arrow
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from djmoney.models.fields import MoneyField

from core.calculators import currency_growth
from core.helpers import QUARTERS
from core.models import IcmoModel, DenormalizedIcmoParentsMixin

PLAN_YEAR_CHOICES = [(y, y) for y in range(1900, (arrow.get().year + 101))]
PLAN_TYPE_DRAFT = 'draft'
PLAN_TYPE_PUBLISHED = 'published'
PLAN_TYPE_ARCHIVED = 'archived'
PLAN_TYPE_CHOICES = (
    (PLAN_TYPE_DRAFT, 'Draft'), (PLAN_TYPE_PUBLISHED, 'Published'),
    (PLAN_TYPE_ARCHIVED, 'Archived')
)


class RevenuePlan(DenormalizedIcmoParentsMixin, IcmoModel):
    icmo_level = 'revenue_plan'
    icmo_parent_levels = ('company',)

    class Meta:
        unique_together = (('slug', 'company'),)

    company = models.ForeignKey('companies.Company')
    name = models.CharField(max_length=150, default=_('Revenue Plan ') + str(arrow.get().year))
    slug = AutoSlugField(populate_from='name')

    owner = models.ForeignKey('icmo_users.IcmoUser', blank=True, null=True)
    plan_year = models.IntegerField(choices=PLAN_YEAR_CHOICES, default=arrow.get().year)
    is_default = models.BooleanField(default=False)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default=PLAN_TYPE_DRAFT)

    @property
    def segments(self):
        return self.segment_set.filter(is_active=True)

    @property
    def programs(self):
        return self.program_set.filter(is_active=True)

    def add_segment(self, name):
        segment, created = Segment.objects.get_or_create(revenue_plan=self, name=name)
        return segment

    @cached_property
    def start_date(self):
        return arrow.get(self.plan_year, self.company.fiscal_months[0], 1).date()

    def start_datetime(self, timezone=None):
        """
        Cast the start date into a particular timezone
        :param timezone:
        :return:
        """
        if not timezone:
            timezone = 'UTC'
        return arrow.get(self.start_date, timezone).datetime

    @cached_property
    def end_date(self):
        c_months = self.company.fiscal_months
        year = self.plan_year if c_months[11] > c_months[0] else self.plan_year + 1
        return arrow.get(year, c_months[11], 1).replace(months=+1, days=-1).date()

    def end_datetime(self, timezone=None):
        if not timezone:
            timezone = 'UTC'
        return arrow.get(self.end_date, timezone).ceil('day').datetime

    def __unicode__(self):
        return self.name

    @property
    def is_current_year(self):
        return self.plan_year == arrow.get().year

    @property
    def url(self):
        return self.get_absolute_url()

    def get_absolute_url(self):
        return reverse('revenue_plans_list',
                       kwargs=dict(company_slug=self.company.slug, plan_slug=self.slug))

    @cached_property
    def is_published(self):
        return self.plan_type == PLAN_TYPE_PUBLISHED

    def clone(self, new_name, plan_year, programs, budget_plans, budget_actuals,
              performance_actuals, tasks, task_states):
        new_plan = RevenuePlan.objects.create(name=new_name, company=self.company,
                                              owner=self.owner, plan_year=plan_year)
        from .tasks import clone_plan
        clone_plan.delay(self.pk, new_plan.pk, programs, budget_plans, budget_actuals,
                         performance_actuals,
                         tasks, task_states)


class Segment(DenormalizedIcmoParentsMixin, IcmoModel):
    icmo_level = 'segment'
    icmo_parent_levels = ('revenue_plan', 'company')

    class Meta:
        unique_together = ('slug', 'revenue_plan')
        ordering = ('-goal_annual',)

    company = models.ForeignKey('companies.Company')
    revenue_plan = models.ForeignKey(RevenuePlan)
    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name')

    average_sale = MoneyField(max_digits=10, decimal_places=0, default_currency='USD', default=0)
    goal_q1 = MoneyField('Q1 Sales Goal', max_digits=10, decimal_places=0, default_currency='USD',
                         default=0)
    goal_q2 = MoneyField('Q2 Sales Goal', max_digits=10, decimal_places=0, default_currency='USD',
                         default=0)
    goal_q3 = MoneyField('Q3 Sales Goal', max_digits=10, decimal_places=0, default_currency='USD',
                         default=0)
    goal_q4 = MoneyField('Q4 Sales Goal', max_digits=10, decimal_places=0, default_currency='USD',
                         default=0)

    # computed
    goal_annual = MoneyField(_('Annual Sales Goal'), max_digits=10, decimal_places=0,
                             default_currency='USD', default=0, editable=False)

    # previous year
    prev_average_sale = MoneyField('Last Years Average Sale', max_digits=10, decimal_places=0,
                                   default_currency='USD', default=0)
    prev_q1 = MoneyField('Last Years Q1 Sales', max_digits=10, decimal_places=0,
                         default_currency='USD',
                         default=0)
    prev_q2 = MoneyField('Last Years Q2 Sales', max_digits=10, decimal_places=0,
                         default_currency='USD',
                         default=0)
    prev_q3 = MoneyField('Last Years Q3 Sales', max_digits=10, decimal_places=0,
                         default_currency='USD',
                         default=0)
    prev_q4 = MoneyField('Last Years Q4 Sales', max_digits=10, decimal_places=0,
                         default_currency='USD',
                         default=0)

    # computed
    prev_annual = MoneyField('Last Years Annual Sales', max_digits=10, decimal_places=0,
                             default_currency='USD', default=0, editable=False)

    def get_quarter_goal(self, quarter):
        if quarter not in QUARTERS:
            raise ValueError("%s is not a valid quarter" % quarter)
        return getattr(self, "goal_%s" % quarter)

    def get_quarter_goal_percent_of_annual(self, quarter):
        if quarter not in QUARTERS:
            raise ValueError("%s is not a valid quarter" % quarter)
        if not self.goal_annual.amount:
            return 0
        return getattr(self, "goal_%s" % quarter).amount / self.goal_annual.amount

    @property
    def goal_q1_percent_of_annual(self):
        if not self.goal_q1 or not self.goal_annual:
            return 0
        return self.goal_q1 / self.goal_annual

    @property
    def goal_q2_percent_of_annual(self):
        if not self.goal_q2 or not self.goal_annual:
            return 0
        return self.goal_q2 / self.goal_annual

    @property
    def goal_q3_percent_of_annual(self):
        if not self.goal_q3 or not self.goal_annual:
            return 0
        return self.goal_q3 / self.goal_annual

    @property
    def goal_q4_percent_of_annual(self):
        if not self.goal_q4 or not self.goal_annual:
            return 0
        return self.goal_q4 / self.goal_annual

    @property
    def qoq_q1_growth_goal(self):
        return currency_growth(self.goal_q1, self.prev_q1)

    @property
    def qoq_q2_growth_goal(self):
        return currency_growth(self.goal_q2, self.prev_q2)

    @property
    def qoq_q3_growth_goal(self):
        return currency_growth(self.goal_q3, self.prev_q3)

    @property
    def qoq_q4_growth_goal(self):
        return currency_growth(self.goal_q4, self.prev_q4)

    @property
    def yoy_growth_goal(self):
        return currency_growth(self.goal_annual, self.prev_annual)

    @property
    def yoy_average_sale_growth_goal(self):
        return currency_growth(self.average_sale, self.prev_average_sale)

    def clone(self, target, programs, budget_plans, budget_actuals, performance_actuals, tasks,
              task_states):
        if type(target) in (str, unicode):  # new segment
            target = Segment.objects.create(name=target, company=self.company,
                                            revenue_plan=self.revenue_plan)
        from .tasks import clone_segment
        clone_segment.delay(self.pk, target.pk, programs, budget_plans, budget_actuals,
                            performance_actuals,
                            tasks, task_states)

    @property
    def budgets(self):
        return self.budgetlineitem_set.select_related('program').filter(
            Q(program=None) | Q(program__is_active=True),
            is_active=True)

    @property
    def programs(self):
        return self.program_set.filter(is_active=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.goal_annual = self.goal_q1 + self.goal_q2 + self.goal_q3 + self.goal_q4
        self.prev_annual = self.prev_q1 + self.prev_q2 + self.prev_q3 + self.prev_q4
        super(Segment, self).save(*args, **kwargs)
