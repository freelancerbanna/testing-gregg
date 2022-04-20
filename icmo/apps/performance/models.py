from __future__ import division  # this line enables currency division

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from core import calculators
from core.fields import DefaultMoneyField, PercentField
from core.helpers import MONTHS_3, ALL_TIME_PERIODS
from core.models import IcmoModel, DenormalizedIcmoParentsMixin


class CampaignSources(object):
    MANUAL = 1
    SALESFORCE = 2
    HUBSPOT = 3
    choices = (
        (MANUAL, 'Manual'),
        (SALESFORCE, 'Salesforce'),
        (HUBSPOT, 'HubSpot'),
    )


class Campaign(DenormalizedIcmoParentsMixin, IcmoModel):
    icmo_level = 'campaign'
    icmo_parent_levels = ('program', 'segment', 'revenue_plan', 'company')

    class Meta:
        unique_together = ('slug', 'program')
        ordering = ('name',)

    company = models.ForeignKey('companies.Company')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan')
    segment = models.ForeignKey('revenues.Segment')
    program = models.ForeignKey('leads.Program')
    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name')

    source = models.IntegerField(_('Source'), default=CampaignSources.MANUAL,
                                 choices=CampaignSources.choices)

    jan_mql = models.IntegerField(default=0)
    jan_sql = models.IntegerField(default=0)
    jan_sales = models.IntegerField(default=0)
    jan_sales_revenue = DefaultMoneyField()

    jan_average_sale = DefaultMoneyField()
    jan_mql_to_sql_conversion = PercentField()
    jan_sql_to_sale_conversion = PercentField()

    feb_mql = models.IntegerField(default=0)
    feb_sql = models.IntegerField(default=0)
    feb_sales = models.IntegerField(default=0)
    feb_sales_revenue = DefaultMoneyField()

    feb_average_sale = DefaultMoneyField()
    feb_mql_to_sql_conversion = PercentField()
    feb_sql_to_sale_conversion = PercentField()

    mar_mql = models.IntegerField(default=0)
    mar_sql = models.IntegerField(default=0)
    mar_sales = models.IntegerField(default=0)
    mar_sales_revenue = DefaultMoneyField()

    mar_average_sale = DefaultMoneyField()
    mar_mql_to_sql_conversion = PercentField()
    mar_sql_to_sale_conversion = PercentField()

    apr_mql = models.IntegerField(default=0)
    apr_sql = models.IntegerField(default=0)
    apr_sales = models.IntegerField(default=0)
    apr_sales_revenue = DefaultMoneyField()

    apr_average_sale = DefaultMoneyField()
    apr_mql_to_sql_conversion = PercentField()
    apr_sql_to_sale_conversion = PercentField()

    may_mql = models.IntegerField(default=0)
    may_sql = models.IntegerField(default=0)
    may_sales = models.IntegerField(default=0)
    may_sales_revenue = DefaultMoneyField()

    may_average_sale = DefaultMoneyField()
    may_mql_to_sql_conversion = PercentField()
    may_sql_to_sale_conversion = PercentField()

    jun_mql = models.IntegerField(default=0)
    jun_sql = models.IntegerField(default=0)
    jun_sales = models.IntegerField(default=0)
    jun_sales_revenue = DefaultMoneyField()

    jun_average_sale = DefaultMoneyField()
    jun_mql_to_sql_conversion = PercentField()
    jun_sql_to_sale_conversion = PercentField()

    jul_mql = models.IntegerField(default=0)
    jul_sql = models.IntegerField(default=0)
    jul_sales = models.IntegerField(default=0)
    jul_sales_revenue = DefaultMoneyField()

    jul_average_sale = DefaultMoneyField()
    jul_mql_to_sql_conversion = PercentField()
    jul_sql_to_sale_conversion = PercentField()

    aug_mql = models.IntegerField(default=0)
    aug_sql = models.IntegerField(default=0)
    aug_sales = models.IntegerField(default=0)
    aug_sales_revenue = DefaultMoneyField()

    aug_average_sale = DefaultMoneyField()
    aug_mql_to_sql_conversion = PercentField()
    aug_sql_to_sale_conversion = PercentField()

    sep_mql = models.IntegerField(default=0)
    sep_sql = models.IntegerField(default=0)
    sep_sales = models.IntegerField(default=0)
    sep_sales_revenue = DefaultMoneyField()

    sep_average_sale = DefaultMoneyField()
    sep_mql_to_sql_conversion = PercentField()
    sep_sql_to_sale_conversion = PercentField()

    oct_mql = models.IntegerField(default=0)
    oct_sql = models.IntegerField(default=0)
    oct_sales = models.IntegerField(default=0)
    oct_sales_revenue = DefaultMoneyField()

    oct_average_sale = DefaultMoneyField()
    oct_mql_to_sql_conversion = PercentField()
    oct_sql_to_sale_conversion = PercentField()

    nov_mql = models.IntegerField(default=0)
    nov_sql = models.IntegerField(default=0)
    nov_sales = models.IntegerField(default=0)
    nov_sales_revenue = DefaultMoneyField()

    nov_average_sale = DefaultMoneyField()
    nov_mql_to_sql_conversion = PercentField()
    nov_sql_to_sale_conversion = PercentField()

    dec_mql = models.IntegerField(default=0)
    dec_sql = models.IntegerField(default=0)
    dec_sales = models.IntegerField(default=0)
    dec_sales_revenue = DefaultMoneyField()

    dec_average_sale = DefaultMoneyField()
    dec_mql_to_sql_conversion = PercentField()
    dec_sql_to_sale_conversion = PercentField()

    q1_mql = models.IntegerField(default=0)
    q1_sql = models.IntegerField(default=0)
    q1_sales = models.IntegerField(default=0)
    q1_sales_revenue = DefaultMoneyField()

    q1_average_sale = DefaultMoneyField()
    q1_mql_to_sql_conversion = PercentField()
    q1_sql_to_sale_conversion = PercentField()

    q2_mql = models.IntegerField(default=0)
    q2_sql = models.IntegerField(default=0)
    q2_sales = models.IntegerField(default=0)
    q2_sales_revenue = DefaultMoneyField()

    q2_average_sale = DefaultMoneyField()
    q2_mql_to_sql_conversion = PercentField()
    q2_sql_to_sale_conversion = PercentField()

    q3_mql = models.IntegerField(default=0)
    q3_sql = models.IntegerField(default=0)
    q3_sales = models.IntegerField(default=0)
    q3_sales_revenue = DefaultMoneyField()

    q3_average_sale = DefaultMoneyField()
    q3_mql_to_sql_conversion = PercentField()
    q3_sql_to_sale_conversion = PercentField()

    q4_mql = models.IntegerField(default=0)
    q4_sql = models.IntegerField(default=0)
    q4_sales = models.IntegerField(default=0)
    q4_sales_revenue = DefaultMoneyField()

    q4_average_sale = DefaultMoneyField()
    q4_mql_to_sql_conversion = PercentField()
    q4_sql_to_sale_conversion = PercentField()

    fiscal_year_mql = models.IntegerField(default=0)
    fiscal_year_sql = models.IntegerField(default=0)
    fiscal_year_sales = models.IntegerField(default=0)
    fiscal_year_sales_revenue = DefaultMoneyField()

    fiscal_year_average_sale = DefaultMoneyField()
    fiscal_year_mql_to_sql_conversion = PercentField()
    fiscal_year_sql_to_sale_conversion = PercentField()

    def get_time_period_field_getter(self, time_period):
        # get time period field
        def _internal(field_name):
            return getattr(self, "%s_%s" % (time_period, field_name))

        return _internal

    def get_time_period_field_setter(self, time_period):
        # set time period field
        def _internal(field_name, value):
            setattr(self, "%s_%s" % (time_period, field_name), value)

        return _internal

    def recalc(self):
        data_fields = (
            'mql', 'sql', 'sales', 'sales_revenue'
        )
        # Create quarter sums
        for quarter, months in self.revenue_plan.company.fiscal_quarters_by_name.items():
            for month in months:
                for field in data_fields:
                    setattr(self, "%s_%s" % (quarter, field),
                            getattr(self, "%s_%s" % (quarter, field)) + getattr(self, "%s_%s" % (
                                month, field)))
        # Create year sums
        for month in MONTHS_3:
            for field in data_fields:
                setattr(self, "fiscal_year_%s" % field,
                        getattr(self, "fiscal_year_%s" % field) + getattr(self, "%s_%s" % (
                            month, field)))

        # Create calculated values
        for time_period in ALL_TIME_PERIODS:
            gf = self.get_time_period_field_getter(time_period)
            sf = self.get_time_period_field_setter(time_period)
            sf('average_sale', calculators.average_sale(gf('sales_revenue'), gf('sales')))
            sf('mql_to_sql_conversion', calculators.mql_to_sql_conversion(gf('sql'), gf('mql')))
            sf('sql_to_sale_conversion',
               calculators.sql_to_sale_conversion(gf('sales'), gf('mql')))

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.recalc()
        super(Campaign, self).save(*args, **kwargs)
