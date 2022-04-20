from decimal import Decimal
import logging

import stripe

from stripe.error import InvalidRequestError

from ..base import ProviderSubscriptionPlan, ProviderSubscription, ProviderCoupon
from billing.helpers import convert_interval_to_days, get_utc_unix_timestamp
from billing.providers.stripe.helpers import get_prefixed_stripe_id
from billing.providers.stripe.models import StripeSubscriptionPlanRegistry, \
    StripeSubscriptionRegistry, StripeCouponRegistry

logger = logging.getLogger("icmo.%s" % __name__)

"""
Stripe special needs:
    1. Setup Fee must be charged as a account_balance on the new customer object
    https://support.stripe.com/questions/subscription-setup-fees

    2. To apply a coupon to the setup_fee apply it to the account_balance before it is
    charged in #1 above.  Other coupons are created as stripe.Coupon objects.
"""


class StripeSubscriptionPlan(ProviderSubscriptionPlan):
    @classmethod
    def create(cls, icmo_plan_id, name, slug, statement_description, short_description, interval,
               interval_count, amount, currency, trial_period_interval,
               trial_period_interval_count, trial_period_amount, trial_period_interval_duration,
               setup_fee_name, setup_fee_amount, setup_fee_description):
        trial_period_days = 0
        if trial_period_amount == Decimal(
                '0') and trial_period_interval and trial_period_interval_duration:
            trial_period_days = convert_interval_to_days(trial_period_interval,
                                                         trial_period_interval_duration)
        plan = stripe.Plan.create(
            amount=int(100 * (amount or 0)),  # stripe amount is in cents
            interval=interval,
            name=name,
            currency=currency,
            id=get_prefixed_stripe_id(slug),
            interval_count=interval_count,
            trial_period_days=trial_period_days,
            statement_descriptor=statement_description,
            metadata=dict(description=short_description),
        )
        StripeSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=icmo_plan_id,
            stripe_plan_id=plan.id,
            setup_fee_amount=int(100 * (setup_fee_amount or 0))
        )
        return slug

    @classmethod
    def update(cls, icmo_plan_id, **kwargs):
        # Not used because paypal does not support updating active plans
        """
        Only these fields can be updated

        p = stripe.Plan.retrieve(subscription.stripe_id)
        p.name = subscription.name
        p.statement_descriptor = subscription.statement_description
        p.metadata = None
        p.save()
        """
        raise NotImplementedError

    @classmethod
    def delete(cls, icmo_plan_id):
        """
        '...deleting a plan does not affect any current subscribers to the plan; it merely means
        that new subscribers can't be added to that plan.'

        """
        try:
            plan_link = StripeSubscriptionPlanRegistry.objects.get(icmo_plan_id=icmo_plan_id)
        except StripeSubscriptionPlanRegistry.DoesNotExist:
            logger.warn("The stripe provider had no record of icmo_plan_id %s" % icmo_plan_id)
            return True
        try:
            p = stripe.Plan.retrieve(plan_link.stripe_plan_id)
            p.delete()
        except InvalidRequestError:
            logger.warn(
                "The stripe backend had no record of the stripe id %s "
                "attached to icmo_plan_id %s" % (plan_link.stripe_plan_id, icmo_plan_id))
        plan_link.delete()
        return True

    @classmethod
    def deactivate(cls, plan_id):
        # Stripe does not have this concept
        return True

    @classmethod
    def activate(cls, plan_id):
        # Stripe does not have this concept
        return True


class StripeSubscription(ProviderSubscription):
    @classmethod
    def create(cls, icmo_subscription_id, icmo_plan_id, customer_email, customer_name,
               payment_token, icmo_coupon_id=None):
        # Retrieve the subscription plan
        plan_link = StripeSubscriptionPlanRegistry.objects.get(icmo_plan_id=icmo_plan_id)

        # Retrieve the setup fee
        setup_fee_amount = plan_link.setup_fee_amount

        # Retrieve the coupon if any
        stripe_coupon_id = None
        if icmo_coupon_id:
            coupon_link = StripeCouponRegistry.objects.get(icmo_coupon_id=icmo_coupon_id)
            setup_fee_amount = coupon_link.get_discounted_setup_fee(setup_fee_amount)
            stripe_coupon_id = coupon_link.stripe_coupon_id
            # setup only coupons don't actually get created in stripe
            if not stripe_coupon_id:
                stripe_coupon_id = None

        # Create the customer and add the setup fee (if any)
        # Add any setup fee as an account_balance on the new customer object
        # https://support.stripe.com/questions/subscription-setup-fees
        customer = stripe.Customer.create(
            description="%s <%s>" % (customer_name, customer_email),
            email=customer_email,
            account_balance=setup_fee_amount
        )

        # Create the subscription and store it
        # coupon affecting recurring is added now
        subscription = customer.subscriptions.create(
            plan=plan_link.stripe_plan_id,
            source=payment_token,
            coupon=stripe_coupon_id
        )
        StripeSubscriptionRegistry.objects.create(
            icmo_subscription_id=icmo_subscription_id,
            stripe_subscription_id=subscription.id,
            stripe_customer_id=customer.id
        )

        return True

    @classmethod
    def cancel(cls, icmo_subscription_id, at_period_end=True, note=None):
        sub_link = StripeSubscriptionRegistry.objects.get(
            icmo_subscription_id=icmo_subscription_id)

        customer = stripe.Customer.retrieve(sub_link.stripe_customer_id)
        customer.subscriptions.retrieve(sub_link.stripe_subscription_id).delete(
            at_period_end=at_period_end)
        sub_link.delete()
        return True


class StripeCoupon(ProviderCoupon):
    @classmethod
    def create(cls, icmo_coupon_id, code, short_description, duration, amount_off, percent_off,
               currency, duration_in_months, max_redemptions, redeem_by,
               setup_fee_amount_off, setup_fee_percent_off):
        if redeem_by:
            redeem_by = get_utc_unix_timestamp(redeem_by)
        params = dict(
            id=get_prefixed_stripe_id(code),
            duration=duration,
            duration_in_months=duration_in_months,
            amount_off=int(100 * (amount_off or 0)),
            percent_off=percent_off,
            currency=currency,
            max_redemptions=max_redemptions,
            redeem_by=redeem_by,
        )
        # Remove empty values
        for key in params.keys():
            if not params[key]:
                params.pop(key)

        if amount_off or percent_off:
            coupon = stripe.Coupon.create(**params)
            coupon_id = coupon.id
        else:
            # setup only coupons don't actually get created in stripe
            coupon_id = ''
        StripeCouponRegistry.objects.create(
            icmo_coupon_id=icmo_coupon_id,
            stripe_coupon_id=coupon_id,
            setup_fee_amount_off=int(100 * (setup_fee_amount_off or 0)),
            setup_fee_percent_off=setup_fee_percent_off
        )

        return True

    @classmethod
    def activate(cls, icmo_coupon_id):
        # Stripe does not support this
        return True

    @classmethod
    def update(cls, icmo_coupon_id):
        # Stripe does not support this
        raise NotImplementedError

    @classmethod
    def deactivate(cls, icmo_coupon_id):
        # Stripe does not support this
        return True

    @classmethod
    def delete(cls, icmo_coupon_id):
        coupon_link = StripeCouponRegistry.objects.get(icmo_coupon_id=icmo_coupon_id)
        coupon = stripe.Coupon.retrieve(coupon_link.stripe_coupon_id)
        coupon.delete()
        coupon_link.delete()
        return True
