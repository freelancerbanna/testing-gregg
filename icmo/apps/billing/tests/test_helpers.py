from decimal import Decimal

from django.test import SimpleTestCase

from billing.helpers import apply_to_price, round_money


class TestHelpers(SimpleTestCase):
    def test_apply_to_price_percent(self):
        self.assertEqual(
            apply_to_price('percent_off', 25, 100),
            75
        )

    def test_apply_to_price_percent_decimal(self):
        self.assertEqual(
            apply_to_price('percent_off', 25, Decimal('90')),
            Decimal('67.50')
        )

    def test_apply_to_price_percent_decimal_rounding(self):
        self.assertEqual(
            apply_to_price('percent_off', 25, Decimal('90.50')),
            Decimal('67.87')
        )

    def test_apply_to_price_amount(self):
        self.assertEqual(apply_to_price('amount_off', 25, 100), 75)

    def test_apply_to_price_amount_decimal(self):
        self.assertEqual(apply_to_price('amount_off', Decimal('25.25'), 100), Decimal('74.75'))

    def test_apply_to_price_amount_min(self):
        self.assertEqual(apply_to_price('amount_off', 25, 20), 0)

    def test_apply_to_price_unknown(self):
        with self.assertRaises(ValueError):
            apply_to_price('invalid', 25, 25)

    def test_round_money(self):
        self.assertEqual(round_money(Decimal('123.999')), Decimal('123.99'))


