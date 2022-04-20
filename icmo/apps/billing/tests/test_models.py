from decimal import Decimal

from django.test import TestCase
from mock import patch
from model_mommy import mommy

from billing.models import SubscriptionPlan, Coupon, Subscription


class SubscriptionPlanTestCase(TestCase):
    def setUp(self):
        self.plan = SubscriptionPlan.objects.create(
            name="Test Plan",
            slug="test_plan",
            short_description="short description",
            full_description="full description",
            statement_description="statement description",
            interval='month',
            interval_count=1,
            amount=Decimal('10.00'),
        )
        self.create_args = [
            self.plan.pk, self.plan.name, self.plan.slug,
            self.plan.statement_description, self.plan.short_description,
            self.plan.interval, self.plan.interval_count, self.plan.amount,
            self.plan.currency, self.plan.free_trial_period_interval,
            1, Decimal('0'),
            self.plan.free_trial_period_interval_duration, self.plan.setup_fee_name,
            self.plan.setup_fee_amount, self.plan.setup_fee_description
        ]

    def test_activate_from_live(self):
        self.plan.is_live = True  # skips the create action
        with patch(
                'billing.providers.stripe.handlers.StripeSubscriptionPlan') as mocked_stripe_plan:
            with patch(
                    'billing.providers.paypal_rest.handlers.PaypalSubscriptionPlan') as \
                    mocked_paypal_plan:
                self.plan.activate()
        mocked_stripe_plan.activate.assert_called_once_with(self.plan.pk)
        mocked_paypal_plan.activate.assert_called_once_with(self.plan.pk)
        self.assertTrue(SubscriptionPlan.objects.get(pk=self.plan.pk).is_active)

    def test_deactivate(self):
        with patch(
                'billing.providers.stripe.handlers.StripeSubscriptionPlan') as mocked_stripe_plan:
            with patch(
                    'billing.providers.paypal_rest.handlers.PaypalSubscriptionPlan') as \
                    mocked_paypal_plan:
                self.plan.deactivate()
        mocked_stripe_plan.deactivate.assert_called_once_with(self.plan.pk)
        mocked_paypal_plan.deactivate.assert_called_once_with(self.plan.pk)
        self.assertFalse(SubscriptionPlan.objects.get(pk=self.plan.pk).is_active)

    def test_activate_to_live(self):
        self.plan.is_live = False
        with patch(
                'billing.providers.stripe.handlers.StripeSubscriptionPlan') as mocked_stripe_plan:
            with patch(
                    'billing.providers.paypal_rest.handlers.PaypalSubscriptionPlan') as \
                    mocked_paypal_plan:
                self.plan.activate()
        mocked_stripe_plan.activate.assert_called_once_with(self.plan.pk)
        mocked_stripe_plan.create.assert_called_once_with(*self.create_args)
        mocked_paypal_plan.activate.assert_called_once_with(self.plan.pk)
        mocked_paypal_plan.create.assert_called_once_with(*self.create_args)
        self.assertTrue(SubscriptionPlan.objects.get(pk=self.plan.pk).is_active)
        self.assertTrue(SubscriptionPlan.objects.get(pk=self.plan.pk).is_live)

    def test_delete(self):
        pk = self.plan.pk
        with patch(
                'billing.providers.stripe.handlers.StripeSubscriptionPlan') as mocked_stripe_plan:
            with patch(
                    'billing.providers.paypal_rest.handlers.PaypalSubscriptionPlan') as \
                    mocked_paypal_plan:
                self.plan.delete()
        mocked_stripe_plan.delete.assert_called_once_with(pk)
        mocked_paypal_plan.delete.assert_called_once_with(pk)
        self.assertEqual(SubscriptionPlan.objects.filter(pk=pk).count(), 0)


class SubscriptionTestCase(TestCase):
    def setUp(self):
        self.plan = mommy.make(SubscriptionPlan)
        self.coupon = mommy.make(Coupon)

    def test_subscribe_stripe(self):
        sub = mommy.make(Subscription, provider_name='stripe')
        with patch('billing.providers.stripe.handlers.StripeSubscription') as mocked_sub:
            sub.subscribe('token')
            mocked_sub.create.assert_called_once_with(
                sub.pk, sub.plan.pk, sub.account.owner.email, sub.account.owner.get_full_name(),
                'token', icmo_coupon_id=None
            )
        self.assertTrue(Subscription.objects.get(pk=sub.pk).is_active)
        self.assertTrue(Subscription.objects.get(pk=sub.pk).is_live)

    def test_cancel_stripe(self):
        sub = mommy.make(Subscription, provider_name='stripe')
        with patch('billing.providers.stripe.handlers.StripeSubscription') as mocked_sub:
            sub.cancel(at_period_end=False, note='note')
        mocked_sub.cancel.assert_called_once_with(
            sub.pk, at_period_end=False, note='note'
        )
        self.assertFalse(Subscription.objects.get(pk=sub.pk).is_active)
        self.assertFalse(Subscription.objects.get(pk=sub.pk).is_live)

    def test_subscribe_paypal(self):
        sub = mommy.make(Subscription, provider_name='paypal_rest')
        with patch('billing.providers.paypal_rest.handlers.PaypalSubscription') as mocked_sub:
            sub.subscribe('token')
            mocked_sub.create.assert_called_once_with(
                sub.pk, sub.plan.pk, sub.account.owner.email, sub.account.owner.get_full_name(),
                'token', icmo_coupon_id=None
            )
        self.assertTrue(Subscription.objects.get(pk=sub.pk).is_active)
        self.assertTrue(Subscription.objects.get(pk=sub.pk).is_live)

    def test_cancel_paypal(self):
        sub = mommy.make(Subscription, provider_name='paypal_rest')
        with patch('billing.providers.paypal_rest.handlers.PaypalSubscription') as mocked_sub:
            sub.cancel(at_period_end=False, note='note')
            mocked_sub.cancel.assert_called_once_with(
                sub.pk, at_period_end=False, note='note'
            )
        self.assertFalse(Subscription.objects.get(pk=sub.pk).is_active)
        self.assertFalse(Subscription.objects.get(pk=sub.pk).is_live)

    def test_subscribe_coupon(self):
        sub = mommy.make(Subscription, provider_name='stripe')
        with patch('billing.providers.stripe.handlers.StripeSubscription') as mocked_stripe_sub:
            sub.subscribe('token', coupon=self.coupon)
        mocked_stripe_sub.create.assert_called_once_with(
            sub.pk, sub.plan.pk, sub.account.owner.email, sub.account.owner.get_full_name(),
            'token', icmo_coupon_id=self.coupon.pk
        )
        self.assertTrue(Subscription.objects.get(pk=sub.pk).is_active)
        self.assertTrue(Subscription.objects.get(pk=sub.pk).is_live)
