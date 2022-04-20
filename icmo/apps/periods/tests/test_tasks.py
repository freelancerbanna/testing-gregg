from collections import defaultdict
from decimal import Decimal

from django.db.models import signals
from django.test import TestCase
import factory

from model_mommy import mommy

from budgets.models import BudgetLineItem
from leads.tests.factories import ProgramFactory
from performance.models import Campaign
from periods.models import Period
from periods.tasks import update_or_create_month_periods_from_program, recompute_summary_periods
from revenues.tests.factories import SegmentFactory


class TestPeriodTasks(TestCase):
    parents = dict()
    periods = defaultdict(dict)

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super(TestPeriodTasks, cls).setUpClass()
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
                # sales_revenue = 10000
                # sql = 66
                # mql = 660
                # contacts = 6600
                # touches = 66000
                # budget = 66000
                # cost_per_sql = 1000
                # roi = -84
            )
            cls.parents['custom_budget_line_item'] = mommy.make(BudgetLineItem,
                                                                segment=cls.parents[
                                                                    'segment'],
                                                                program=None,
                                                                item_type='custom')
            cls.parents['campaign'] = mommy.make(Campaign, program=cls.parents['program'])

    def test_basic_update_or_create_month_periods_from_program(self):
        update_or_create_month_periods_from_program(self.parents['program'])
        # Months
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='jan',
                resolution='program'
            ).count(),
            1
        )

        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='feb',
                resolution='program').count(),
            1
        )
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='mar',
                resolution='program').count(),
            1
        )
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='apr',
                resolution='program').count(),
            1
        )
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='may',
                resolution='program').count(),
            1
        )
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='jun',
                resolution='program').count(),
            1
        )
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='jul',
                resolution='program').count(),
            1
        )
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='aug',
                resolution='program').count(),
            1
        )
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='sep',
                resolution='program').count(),
            1
        )
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='oct',
                resolution='program').count(),
            1
        )
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='nov',
                resolution='program').count(),
            1
        )
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='month', period='dec',
                resolution='program').count(),
            1
        )

    def test_values_update_or_create_month_periods_from_program(self):
        # Note that these values are split across the months, so make sure to look
        update_or_create_month_periods_from_program(self.parents['program'])
        # at more than one month AND the sum for the whole year

        # Months
        jan_periods = Period.objects.filter(
            company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
            segment=self.parents['segment'],
            program=self.parents['program'], period_type='month', period='jan',
            resolution='program'
        )

        self.assertEqual(jan_periods.count(), 1)
        self.assertTupleEqual(
            jan_periods.values_list(
                # copied
                'touches_per_contact_plan', 'touches_to_mql_conversion_plan',
                'mql_to_sql_conversion_plan', 'sql_to_sale_conversion_plan',
                'cost_per_mql_plan', 'cost_per_sql_plan', 'roi_plan',

                # divided
                'budget_plan', 'sales_plan', 'sql_plan', 'mql_plan', 'contacts_plan',
                'touches_plan',
            ).first(),
            (
                # copied
                10, Decimal('1.0'),
                Decimal('10.0'), Decimal('15.0'),
                Decimal('100.00'), Decimal('1000.00'), -85,

                # divided (initial * .1 / 3)
                0, 0, 2, 22, 220, 2200
            )
        )

    def test_recompute_summary_periods(self):
        recompute_summary_periods('program', self.parents['program'].id)

        # Quarters
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='quarter', period='q1',
                resolution='program').count(),
            1
        )

        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='quarter', period='q2',
                resolution='program').count(),
            1
        )

        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='quarter', period='q3',
                resolution='program').count(),
            1
        )
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='quarter', period='q4',
                resolution='program').count(),
            1
        )
        # Year
        self.assertEqual(
            Period.objects.filter(
                company=self.parents['company'], revenue_plan=self.parents['revenue_plan'],
                segment=self.parents['segment'],
                program=self.parents['program'], period_type='year', period='year',
                resolution='program').count(),
            1
        )

    def test_values_recompute_summary_periods(self):
        update_or_create_month_periods_from_program(self.parents['program'])
        recompute_summary_periods('program', self.parents['program'].id)

        # Quarters
        period = Period.objects.filter(
            program=self.parents['program'], period_type='year', period='year',
            resolution='program')
        self.assertEqual(
            period.values_list(
                # copied
                'touches_per_contact_plan', 'touches_to_mql_conversion_plan',
                'mql_to_sql_conversion_plan', 'sql_to_sale_conversion_plan',
                'cost_per_mql_plan', 'cost_per_sql_plan', 'roi_plan',

                # divided
                'budget_plan', 'sales_plan', 'sql_plan', 'mql_plan', 'contacts_plan',
                'touches_plan',
            ).first(),
            (
                # copied
                10, Decimal('1.0'),
                Decimal('10.0'), Decimal('15.0'),
                Decimal('100.00'), Decimal('1000.00'), -85,

                # divided (initial * .1 / 3)
                0, 10, 66, 660, 6600, 66000
            )
        )
