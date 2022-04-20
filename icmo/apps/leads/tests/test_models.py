from decimal import Decimal

from django.test import TestCase
from model_mommy import mommy

from leads.models import Program


class ProgramTestCase(TestCase):
    def setUp(self):
        self.p = mommy.make(
            Program,
            segment__average_sale=Decimal('12345'),
            segment__goal_q1=Decimal('6000000'),
            segment__goal_q2=Decimal('0700000'),
            segment__goal_q3=Decimal('0080000'),
            segment__goal_q4=Decimal('0009012'),
            touches_per_contact=10,
            touches_to_mql_conversion=Decimal('5'),
            mql_to_sql_conversion=Decimal('10'),
            sql_to_sale_conversion=Decimal('15'),
            cost_per_mql=Decimal('50'),
            marketing_mix=33
        )

    def test_segment_annual_goal(self):
        # not part of this app, but all these tests will fail if its wrong
        self.assertEqual(self.p.segment.goal_annual.amount, Decimal('6789012'))

    def test_goal_calculation(self):
        self.assertEqual(self.p.sales_revenue.amount, Decimal('2240374'))

    def test_contacts_calculation(self):
        self.assertEqual(self.p.contacts, 24260)

    def test_touches_calculation(self):
        self.assertEqual(self.p.touches, 242600)

    def test_mql_calculation(self):
        self.assertEqual(self.p.mql, 12130)

    def test_sql_calculation(self):
        self.assertEqual(self.p.sql, 1213)

    def test_sales_calculation(self):
        self.assertEqual(self.p.sales, 182)

    def test_budget_calculation(self):
        self.assertEqual(self.p.budget.amount, Decimal('606500'))

    def test_roi_calculation(self):
        self.assertEqual(self.p.roi, 269)
