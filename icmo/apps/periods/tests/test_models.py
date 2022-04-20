from collections import defaultdict
from decimal import Decimal

import factory
from django.db.models import signals
from django.test import SimpleTestCase, TestCase
from model_mommy import mommy
from moneyed import Money

from budgets.models import BudgetLineItem
from companies.models import Company
from core.models import ICMO_LEVELS
from leads.tests.factories import ProgramFactory
from performance.models import Campaign
from periods.models import Period, RESOLUTION_TO_CLASS_MAP
from revenues.tests.factories import SegmentFactory


class TestPeriodSimple(SimpleTestCase):
    def test_recalc(self):
        p = Period(
                period='jan',
                resolution='program',
                budget_plan=5331000,

                contacts_plan=275400,
                mql_plan=27540,
                sql_plan=2754,
                sales_plan=414,
                sales_revenue_plan=10000000,
                touches_plan=2754000,

                cost_per_mql_plan=150,
                cost_per_sql_plan=1500,
                average_sale_plan=24154.59,
                touches_to_mql_conversion_plan=20,
                contacts_to_mql_conversion_plan=20,
                mql_to_sql_conversion_plan=20,
                sql_to_sale_conversion_plan=20,
                touches_per_contact_plan=20,

                budget_actual=5329536,
                contacts_actual=295000,
                mql_actual=30000,
                sql_actual=2500,
                sales_actual=400,
                sales_revenue_actual=8000000,
                touches_actual=3000000,
        )
        p.recalc()
        # calculated
        self.assertEqual(p.roi_actual, 50)
        self.assertEqual(p.cost_per_mql_actual.amount, Money(Decimal('177.65'), 'USD').amount)
        self.assertEqual(p.cost_per_sql_actual.amount, Money(Decimal('2131.81'), 'USD').amount)
        self.assertEqual(p.average_sale_actual.amount, Money(Decimal('20000'), 'USD').amount)
        self.assertEqual(p.touches_to_mql_conversion_actual, 1)
        self.assertEqual(p.mql_to_sql_conversion_actual, Decimal('8.3'))
        self.assertEqual(p.sql_to_sale_conversion_actual, Decimal('16.0'))
        self.assertEqual(p.touches_per_contact_actual, Decimal('11'))

        # variance is simple subtraction
        self.assertEqual(p.budget_variance, Money(1464, 'USD'))
        self.assertEqual(p.sales_revenue_variance, Money(2000000, 'USD'))
        self.assertEqual(p.roi_variance, Decimal('-50'))
        self.assertEqual(p.contacts_variance, -19600)
        self.assertEqual(p.mql_variance, -2460)
        self.assertEqual(p.sql_variance, 254)
        self.assertEqual(p.sales_variance, 14)
        self.assertEqual(p.touches_variance, -246000)
        self.assertEqual(p.cost_per_mql_variance.amount, Money(Decimal('-27.65'), 'USD').amount)
        self.assertEqual(p.cost_per_sql_variance.amount, Money(Decimal('-631.81'), 'USD').amount)
        self.assertEqual(p.average_sale_variance.amount, Money(Decimal('4154.59'), 'USD').amount)
        self.assertEqual(p.touches_to_mql_conversion_variance, Decimal('19.0'))
        self.assertEqual(p.mql_to_sql_conversion_variance, Decimal('11.7'))
        self.assertEqual(p.sql_to_sale_conversion_variance, Decimal('4.0'))
        self.assertEqual(p.touches_per_contact_variance, 9)

    def test__get_period_type(self):
        for period in ('jan', 'feb', 'mar', 'apr', 'may', 'jun',
                       'jul', 'aug', 'sep', 'oct', 'nov', 'dec'):
            p = Period(period=period)
            self.assertEqual(p._get_period_type(), 'month')
        for period in ('q1', 'q2', 'q3', 'q4'):
            p = Period(period=period)
            self.assertEqual(p._get_period_type(), 'quarter')
        p = Period(period='year')
        self.assertEqual(p._get_period_type(), 'year')
        p = Period(period='junk')
        with self.assertRaises(ValueError):
            p._get_period_type()

    def test_quarter(self):
        p = Period(period='jan', period_type='month', company=Company(fiscal_year_start=1))
        self.assertEqual(p.quarter, 'q1')
        p = Period(period='q1', period_type='quarter', company=Company(fiscal_year_start=1))
        with self.assertRaises(AttributeError):
            test = p.quarter

    def test_absolute_path(self):
        levels = reversed(ICMO_LEVELS.keys())
        kwargs = {x: None for x in levels}
        for resolution in levels:
            kwargs[resolution] = mommy.prepare(RESOLUTION_TO_CLASS_MAP[resolution])
            p = Period(period='jan', **kwargs)
            self.assertDictEqual(kwargs, p.path)

    def test_path(self):
        kwargs = dict()
        levels = reversed(ICMO_LEVELS.keys())
        for resolution in levels:
            kwargs[resolution] = mommy.prepare(RESOLUTION_TO_CLASS_MAP[resolution])
            p = Period(period='jan', **kwargs)
            self.assertDictEqual(kwargs, p.path)

    def test_icmo_fields(self):
        p = Period()
        self.assertItemsEqual(
                p.icmo_fields,
                ['average_sale', 'budget',
                 'contacts', 'cost_per_mql',
                 'cost_per_sql', 'mql_to_sql_conversion',
                 'mql', 'roi', 'sales', 'sql_to_sale_conversion',
                 'sql', 'sales_revenue', 'touches_per_contact',
                 'contacts_to_mql_conversion',
                 'touches_to_mql_conversion', 'touches']
        )


class TestPeriodAggregation(TestCase):
    parents = dict()
    periods = defaultdict(dict)

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super(TestPeriodAggregation, cls).setUpClass()
        with factory.django.mute_signals(signals.pre_save, signals.post_save):
            cls.parents['segment'] = SegmentFactory(
                    goal_q1=1000, goal_q2=2000,
                    goal_q3=3000, goal_q4=4000,
                    average_sale=Decimal(1000),
            )
            cls.parents['company'] = cls.parents['segment'].company
            cls.parents['revenue_plan'] = cls.parents['segment'].revenue_plan

            cls.parents['program'] = ProgramFactory(
                    segment=cls.parents['segment'],
                    name='Test Program',
                    touches_per_contact=10,
                    touches_to_mql_conversion=Decimal('1'),
                    mql_to_sql_conversion=Decimal('10'),
                    sql_to_sale_conversion=Decimal('15'),
                    cost_per_mql=Decimal('100'),
                    marketing_mix=100,
                    # computed
                    # sales_revenue = 4000
                    # sql = 26
                    # mql = 260
                    # contacts = 2600
                    # touches = 26000
                    # budget = 26000
                    # cost_per_sql = 1000
                    # roi = -84
            )
            cls.parents['custom_budget_line_item'] = mommy.make(
                    BudgetLineItem,
                    segment=cls.parents['segment'],
                    program=None,
                    item_type='custom'
            )
            cls.parents['campaign'] = mommy.make(Campaign, program=cls.parents['program'])
            # todo write test that tests segment aggregation, including custom + program budget
            # items
