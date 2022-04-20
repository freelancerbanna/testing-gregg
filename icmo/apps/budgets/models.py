from django.db import models
from django.db.models import Sum, Q
from django_extensions.db.fields import AutoSlugField
from djmoney.models.fields import Money
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from ordered_model.models import OrderedModel

from core.fields import DecimalMoneyField
from core.helpers import MONTHS_3, round_to_whole_number, QUARTERS
from core.models import IcmoModel
from leads.models import ProgramTypes


class BudgetTypes(object):
    CATEGORY = 'category'
    PROGRAM = 'program'
    CUSTOM = 'custom'

    choices = (
        (CATEGORY, 'Category'),
        (PROGRAM, 'Program'),
        (CUSTOM, 'Custom'),
    )


class BudgetActiveParentsManager(TreeManager):
    # Budgets can have or not have parents as programs so this is custom
    def get_queryset(self):
        return super(BudgetActiveParentsManager, self).get_queryset() \
            .select_related('company', 'revenue_plan', 'program') \
            .filter(Q(program=None) | Q(program__is_active=True),
                    company__is_active=True,
                    revenue_plan__is_active=True,
                    segment__is_active=True,
                    is_active=True,
                    )


class BudgetLineItem(MPTTModel, OrderedModel, IcmoModel):
    class Meta:
        unique_together = ('slug', 'segment')
        ordering = ('order',)

    company = models.ForeignKey('companies.Company')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan')
    segment = models.ForeignKey('revenues.Segment')
    program = models.OneToOneField('leads.Program', blank=True, null=True)
    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name')

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children',
                            db_index=True)
    item_type = models.CharField(max_length=10, default=BudgetTypes.CATEGORY,
                                 choices=BudgetTypes.choices)

    automatic_distribution = models.BooleanField(default=True)

    jan_actual = DecimalMoneyField()
    feb_actual = DecimalMoneyField()
    mar_actual = DecimalMoneyField()
    apr_actual = DecimalMoneyField()
    may_actual = DecimalMoneyField()
    jun_actual = DecimalMoneyField()
    jul_actual = DecimalMoneyField()
    aug_actual = DecimalMoneyField()
    sep_actual = DecimalMoneyField()
    oct_actual = DecimalMoneyField()
    nov_actual = DecimalMoneyField()
    dec_actual = DecimalMoneyField()

    # computed for programs, data (manually entered) for custom line items
    jan_plan = DecimalMoneyField()
    feb_plan = DecimalMoneyField()
    mar_plan = DecimalMoneyField()
    apr_plan = DecimalMoneyField()
    may_plan = DecimalMoneyField()
    jun_plan = DecimalMoneyField()
    jul_plan = DecimalMoneyField()
    aug_plan = DecimalMoneyField()
    sep_plan = DecimalMoneyField()
    oct_plan = DecimalMoneyField()
    nov_plan = DecimalMoneyField()
    dec_plan = DecimalMoneyField()

    # computed
    jan_variance = DecimalMoneyField()
    feb_variance = DecimalMoneyField()
    mar_variance = DecimalMoneyField()
    apr_variance = DecimalMoneyField()
    may_variance = DecimalMoneyField()
    jun_variance = DecimalMoneyField()
    jul_variance = DecimalMoneyField()
    aug_variance = DecimalMoneyField()
    sep_variance = DecimalMoneyField()
    oct_variance = DecimalMoneyField()
    nov_variance = DecimalMoneyField()
    dec_variance = DecimalMoneyField()

    q1_actual = DecimalMoneyField()
    q1_plan = DecimalMoneyField()
    q1_variance = DecimalMoneyField()

    q2_actual = DecimalMoneyField()
    q2_plan = DecimalMoneyField()
    q2_variance = DecimalMoneyField()

    q3_actual = DecimalMoneyField()
    q3_plan = DecimalMoneyField()
    q3_variance = DecimalMoneyField()

    q4_actual = DecimalMoneyField()
    q4_plan = DecimalMoneyField()
    q4_variance = DecimalMoneyField()

    fiscal_year_actual = DecimalMoneyField()
    fiscal_year_plan = DecimalMoneyField()
    fiscal_year_variance = DecimalMoneyField()

    objects = BudgetActiveParentsManager()

    @property
    def parent_slug(self):
        if self.parent:
            return self.parent.slug
        return ''

    @property
    def is_moveable(self):
        # Channel programs cannot be moved
        if self.program and self.parent and self.parent.program:
            return False
        # Channels cannot be moved
        if self.item_type == BudgetTypes.CATEGORY and self.program:
            return False
        return True

    def set_program_quarter_budget_split(self, quarter):
        budget = getattr(self.program, '%s_budget' % quarter)
        split = Money(round_to_whole_number(budget.amount / 3), budget.currency)
        for month in self.revenue_plan.company.fiscal_quarters_by_name[quarter]:
            setattr(self, '%s_plan' % month, split)

    def recalc(self):
        # Program budgets are determined via the lead mix app
        if self.item_type == BudgetTypes.PROGRAM and self.automatic_distribution and \
                self.program:
            for quarter in QUARTERS:
                self.set_program_quarter_budget_split(quarter)
        # Sum the month budget and actuals for all line items under this
        # category.  get_descendants does not work with new items, thus the pk check.
        elif self.item_type == BudgetTypes.CATEGORY and self.pk:
            sums = []
            for month in MONTHS_3:
                sums.append(Sum('%s_actual' % month))
                sums.append(Sum('%s_plan' % month))
            # qs = BudgetLineItem.objects.filter(parent=self)
            if self.get_descendant_count():
                qs = self.get_descendants()
            else:
                qs = self.get_children()
            aggregates = qs.filter(is_active=True).exclude(
                item_type=BudgetTypes.CATEGORY).aggregate(*sums)
            # aggregates = self.get_descendants().aggregate(*sums)
            for month in MONTHS_3:
                setattr(self, '%s_actual' % month, aggregates['%s_actual__sum' % month] or 0)
                setattr(self, '%s_plan' % month, aggregates['%s_plan__sum' % month] or 0)

        # Set the variance for each month
        for month in MONTHS_3:
            actual = getattr(self, '%s_actual' % month)
            plan = getattr(self, '%s_plan' % month)
            setattr(self, '%s_variance' % month, plan - actual)

        # set the fiscal quarters according to the fiscal year start
        for quarter, months in self.revenue_plan.company.fiscal_quarters_by_name.items():
            setattr(self, "%s_actual" % quarter, 0)
            setattr(self, "%s_plan" % quarter, 0)
            setattr(self, "%s_variance" % quarter, 0)

            for month in months:
                setattr(self, "%s_actual" % quarter,
                        getattr(self, "%s_actual" % quarter) + getattr(self,
                                                                       "%s_actual" % month))
                setattr(self, "%s_plan" % quarter,
                        getattr(self, "%s_plan" % quarter) + getattr(self, "%s_plan" % month))
                setattr(self, "%s_variance" % quarter,
                        getattr(self, "%s_variance" % quarter) + getattr(self,
                                                                         "%s_variance" %
                                                                         month))

        # set the fiscal year values (varies between programs and the rest)
        if self.item_type == BudgetTypes.PROGRAM and self.program:
            self.fiscal_year_plan = self.program.budget
        else:
            self.fiscal_year_plan = 0
            for quarter in QUARTERS:
                self.fiscal_year_plan += getattr(self, "%s_plan" % quarter)
        # set fiscal year actuals and variance
        self.fiscal_year_actual = 0
        self.fiscal_year_variance = 0
        for quarter in QUARTERS:
            self.fiscal_year_actual += getattr(self, "%s_actual" % quarter)
        self.fiscal_year_variance = self.fiscal_year_plan - self.fiscal_year_actual

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        # denormalize parents
        self.revenue_plan_id = self.segment.revenue_plan_id
        self.company_id = self.segment.company_id

        self.recalc()

        if self.program:  # as opposed to custom or category
            self.name = self.program.name
            if self.program.item_type == ProgramTypes.CATEGORY:
                self.item_type = BudgetTypes.CATEGORY
            else:
                self.item_type = 'program'

            if not self.parent and 'parent' not in self.get_dirty_fields(True):
                if self.program.parent:
                    self.parent = self.program.parent.budgetlineitem
                else:
                    self.parent = None
        super(BudgetLineItem, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for child in BudgetLineItem.objects.filter(parent=self):
            child.parent = self.parent
            child.save()
        super(BudgetLineItem, self).delete(*args, **kwargs)
