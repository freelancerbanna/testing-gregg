from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
import stripe
from mock import patch, Mock

from billing.providers.stripe.handlers import StripeSubscriptionPlan, StripeCoupon, \
    StripeSubscription
from billing.providers.stripe.models import StripeSubscriptionPlanRegistry, StripeCouponRegistry, \
    StripeSubscriptionRegistry


class StripeSubscriptionPlanTestCase(TestCase):
    def test_create(self):
        mock_stripe_plan = Mock()
        mock_stripe_plan.id = 'test'
        with patch.object(stripe.Plan, 'create', return_value=mock_stripe_plan) as mock_method:
            StripeSubscriptionPlan.create(
                12, 'Test', 'test', 'statement description', 'short description',
                'month', 3, Decimal('45.25'), 'USD', 'day', 30, Decimal('0.00'), 30, 'setup fee', Decimal('100.00'),
                'setup fee description'
            )

        mock_method.assert_called_once_with(
            amount=4525,
            interval='month',
            name='Test',
            currency='USD',
            id='test-test',
            interval_count=3,
            trial_period_days=30,
            statement_descriptor='statement description',
            metadata=dict(description='short description'),
        )
        self.assertEqual(
            StripeSubscriptionPlanRegistry.objects.filter(icmo_plan_id=12).count(),
            1
        )
        plan_link = StripeSubscriptionPlanRegistry.objects.get(icmo_plan_id=12)
        self.assertEqual(plan_link.stripe_plan_id, 'test')
        self.assertEqual(plan_link.setup_fee_amount, 10000)

    def test_update(self):
        with self.assertRaises(NotImplementedError):
            StripeSubscriptionPlan.update(12)

    def test_delete(self):
        mocked_stripe_plan = Mock()
        StripeSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=12, stripe_plan_id='test'
        )

        with patch.object(stripe.Plan, 'retrieve',
                          return_value=mocked_stripe_plan) as mocked_stripe_retrieve:
            StripeSubscriptionPlan.delete(12)
        mocked_stripe_retrieve.assert_called_once_with('test')
        mocked_stripe_plan.delete.assert_called_once_with()
        self.assertEqual(StripeSubscriptionPlanRegistry.objects.filter(icmo_plan_id=12).count(), 0)

    def test_activate(self):
        self.assertTrue(StripeSubscriptionPlan.activate(12))

    def test_deactivate(self):
        self.assertTrue(StripeSubscriptionPlan.deactivate(12))


class StripeCouponTestCase(TestCase):
    def test_create(self):
        mock_stripe_coupon = Mock()
        mock_stripe_coupon.id = 'stripecouponid'
        with patch.object(stripe.Coupon, 'create',
                          return_value=mock_stripe_coupon) as mocked_stripe_coupon_create:
            StripeCoupon.create(
                5, 'TESTCODE', 'test coupon', 'repeating', Decimal('25.00'), 50, 'USD', 1, 10,
                timezone.datetime(2030, 12, 1), Decimal('32.25'), 10
            )
            mocked_stripe_coupon_create.assert_called_once_with(
                id='test-TESTCODE',
                duration='repeating',
                duration_in_months=1,
                amount_off=2500,
                percent_off=50,
                currency='USD',
                max_redemptions=10,
                redeem_by=1922313600
            )
            self.assertEqual(StripeCouponRegistry.objects.filter(icmo_coupon_id=5).count(), 1)
            coupon_link = StripeCouponRegistry.objects.get(icmo_coupon_id=5)
            self.assertEqual(coupon_link.stripe_coupon_id, 'stripecouponid')
            self.assertEqual(coupon_link.setup_fee_amount_off, 3225)
            self.assertEqual(coupon_link.setup_fee_percent_off, 10)

    def test_activate(self):
        self.assertTrue(StripeCoupon.activate(5))

    def test_deactivate(self):
        self.assertTrue(StripeCoupon.deactivate(5))

    def test_update(self):
        with self.assertRaises(NotImplementedError):
            StripeCoupon.update(5)

    def test_delete(self):
        mocked_stripe_coupon = Mock()
        StripeCouponRegistry.objects.create(
            icmo_coupon_id=5, stripe_coupon_id='stripecouponid'
        )

        with patch.object(stripe.Coupon, 'retrieve',
                          return_value=mocked_stripe_coupon) as mocked_stripe_retrieve:
            StripeCoupon.delete(5)
        mocked_stripe_retrieve.assert_called_once_with('stripecouponid')
        mocked_stripe_coupon.delete.assert_called_once_with()
        self.assertEqual(StripeCouponRegistry.objects.filter(icmo_coupon_id=5).count(), 0)


class StripeSubscriptionCreateTestCase(TestCase):
    def setUp(self):
        StripeSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=12,
            stripe_plan_id='test'
        )
        StripeSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=15,
            stripe_plan_id='test-setupfee',
            setup_fee_amount=5000
        )
        StripeCouponRegistry.objects.create(
            icmo_coupon_id=5,
            stripe_coupon_id='basiccoupon'
        )
        StripeCouponRegistry.objects.create(
            icmo_coupon_id=7,
            stripe_coupon_id='setupfeeamountcoupon',
            setup_fee_amount_off=2500,
        )
        StripeCouponRegistry.objects.create(
            icmo_coupon_id=9,
            stripe_coupon_id='setupfeepercentcoupon',
            setup_fee_percent_off=25,
        )
        patch('stripe.Customer.create')
        patch('stripe.Customer.retrieve')
        self.stripe_customer, self.stripe_subscription = Mock(), Mock()
        self.stripe_customer.id = '200'
        self.stripe_subscription.id = '3000'
        stripe.Customer.create = Mock(return_value=self.stripe_customer)
        stripe.Customer.retrieve = Mock(return_value=self.stripe_customer)
        self.stripe_customer.subscriptions.create = Mock(return_value=self.stripe_subscription)

    def tearDown(self):
        StripeSubscriptionRegistry.objects.all().delete()

    def test_create_basic_no_fee_no_coupon(self):
        StripeSubscription.create(
            100, 12, 'test@test.com', 'Test Testerson', 'token123', None
        )
        stripe.Customer.create.assert_called_once_with(
            description="Test Testerson <test@test.com>",
            email="test@test.com",
            account_balance=0
        )

        self.stripe_customer.subscriptions.create.assert_called_once_with(
            plan='test',
            source='token123',
            coupon=None
        )

        self.assertEqual(
            StripeSubscriptionRegistry.objects.filter(icmo_subscription_id=100).count(), 1)

        subscription_link = StripeSubscriptionRegistry.objects.get(icmo_subscription_id=100)
        self.assertEqual(subscription_link.stripe_subscription_id, '3000')
        self.assertEqual(subscription_link.stripe_customer_id, '200')

    def test_create_fee_no_coupon(self):
        StripeSubscription.create(
            100, 15, 'test@test.com', 'Test Testerson', 'token123', None
        )
        stripe.Customer.create.assert_called_once_with(
            description="Test Testerson <test@test.com>",
            email="test@test.com",
            account_balance=5000
        )

        self.stripe_customer.subscriptions.create.assert_called_once_with(
            plan='test-setupfee',
            source='token123',
            coupon=None
        )

    def test_create_basic_coupon(self):
        StripeSubscription.create(
            100, 12, 'test@test.com', 'Test Testerson', 'token123', 5
        )
        stripe.Customer.create.assert_called_once_with(
            description="Test Testerson <test@test.com>",
            email="test@test.com",
            account_balance=0
        )

        self.stripe_customer.subscriptions.create.assert_called_once_with(
            plan='test',
            source='token123',
            coupon='basiccoupon'
        )

    def test_create_fee_with_fee_coupon_percent(self):
        StripeSubscription.create(
            100, 15, 'test@test.com', 'Test Testerson', 'token123', 9
        )
        stripe.Customer.create.assert_called_once_with(
            description="Test Testerson <test@test.com>",
            email="test@test.com",
            account_balance=3750
        )

        self.stripe_customer.subscriptions.create.assert_called_once_with(
            plan='test-setupfee',
            source='token123',
            coupon='setupfeepercentcoupon'
        )

    def test_create_fee_with_fee_coupon_amount(self):
        StripeSubscription.create(
            100, 15, 'test@test.com', 'Test Testerson', 'token123', 7
        )
        stripe.Customer.create.assert_called_once_with(
            description="Test Testerson <test@test.com>",
            email="test@test.com",
            account_balance=2500
        )

        self.stripe_customer.subscriptions.create.assert_called_once_with(
            plan='test-setupfee',
            source='token123',
            coupon='setupfeeamountcoupon'
        )


class StripeSubscriptionCancelTestCase(TestCase):
    def setUp(self):
        StripeSubscriptionRegistry.objects.create(
            icmo_subscription_id=100,
            stripe_subscription_id='3000',
            stripe_customer_id='5',
        )
        patch('stripe.Customer.retrieve')
        self.stripe_customer, self.stripe_subscription = Mock(), Mock()
        self.stripe_customer.id = '200'
        self.stripe_subscription.id = '3000'
        stripe.Customer.create = Mock(return_value=self.stripe_customer)
        stripe.Customer.retrieve = Mock(return_value=self.stripe_customer)
        self.stripe_customer.subscriptions.retrieve = Mock(return_value=self.stripe_subscription)

    def test_cancel(self):
        StripeSubscription.cancel(100, at_period_end=False)
        stripe.Customer.retrieve.assert_called_once_with('5')
        self.stripe_customer.subscriptions.retrieve.assert_called_once_with('3000')
        self.stripe_subscription.delete.assert_called_once_with(at_period_end=False)
        self.assertEqual(
            StripeSubscriptionRegistry.objects.filter(icmo_subscription_id=100).count(),
            0
        )
