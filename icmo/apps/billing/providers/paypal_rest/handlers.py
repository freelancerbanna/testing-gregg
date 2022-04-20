import logging

import paypalrestsdk
from paypalrestsdk.exceptions import ConnectionError, MissingConfig, MissingParam, ClientError, \
    Redirection

from ..base import ProviderSubscriptionPlan, ProviderCoupon, ProviderSubscription, \
    ProviderNetworkErrorException, ProviderAPIError
from ...helpers import get_adjusted_fee, get_utc_timestamp
from .models import PaypalSubscriptionPlanRegistry, PaypalSubscriptionRegistry, \
    PaypalCouponRegistry
from core.helpers import full_reverse, full_url_from_path

logger = logging.getLogger(__name__)

"""
Paypal special needs:
    1. Paypal does not internally support coupons so as a workaround, a new
    paypal subscription plan is created for each combination of icmo subscription plan
    and coupon and no coupon.
    2. This means that whenever a new icmo coupon is added, new paypal subscription plan
     objects are created for each existing plan.
    3. This also means that whenever a new icmo subscription plan is added, new paypal
    subscription plan objects are created for each existing coupon.
"""


class PaypalError(Exception):
    pass


def paypal_error_catcher(klass_method):
    """  Catch paypal errors and transform into generic provider exceptions """

    def wrapper(*args, **kwargs):
        try:
            result = klass_method(*args, **kwargs)
        except (Redirection, ClientError, MissingParam, MissingConfig), e:
            logger.warn(e.message)
            raise ProviderAPIError(e.message)
        except ConnectionError, e:
            logger.warn(e.message)
            raise ProviderNetworkErrorException(e.message)
        return result

    wrapper.__name__ = klass_method.__name__
    wrapper.__doc__ = klass_method.__doc__

    return wrapper


class PaypalSubscriptionPlan(ProviderSubscriptionPlan):
    @classmethod
    @paypal_error_catcher
    def create(cls, icmo_plan_id, name, slug, statement_description, short_description, interval,
               interval_count, amount, currency, trial_period_interval,
               trial_period_interval_count, trial_period_amount, trial_period_interval_duration,
               setup_fee_name, setup_fee_amount, setup_fee_description):

        # Create the plan on Paypal
        paypal_plan_id = cls.paypal_create_plan(
            icmo_plan_id, name, slug, statement_description,
            short_description, interval,
            interval_count, amount, currency, trial_period_interval,
            trial_period_interval_count, trial_period_amount,
            trial_period_interval_duration,
            setup_fee_name, setup_fee_amount, setup_fee_description
        )
        # Record the plan locally
        paypal_plan = PaypalSubscriptionPlanRegistry.objects.create(
            icmo_plan_id=icmo_plan_id, paypal_plan_id=paypal_plan_id,
            name=name, short_description=short_description, currency=currency,
            interval=interval, interval_count=interval_count, amount=amount,
            discount_period_interval=trial_period_interval,
            discount_period_interval_count=trial_period_interval_count,
            discount_period_interval_duration=trial_period_interval_duration,
            discount_period_amount=trial_period_amount,
            setup_fee_amount=setup_fee_amount,
        )
        # New plans need variants created for each existing coupon
        for paypal_coupon in PaypalCouponRegistry.objects.all():
            PaypalCoupon.paypal_create_coupon_plan(
                paypal_coupon.icmo_coupon_id, paypal_coupon.code,
                paypal_coupon.short_description, paypal_coupon.duration,
                paypal_coupon.amount_off, paypal_coupon.percent_off,
                paypal_coupon.currency,
                paypal_coupon.duration_in_months, None, None,
                paypal_coupon.setup_fee_amount_off,
                paypal_coupon.setup_fee_percent_off, paypal_plan,
            )
        return True

    @classmethod
    @paypal_error_catcher
    def paypal_create_plan(cls, icmo_plan_id, name, slug, statement_description, short_description,
                           interval,
                           interval_count, amount, currency, trial_period_interval,
                           trial_period_interval_count, trial_period_amount,
                           trial_period_interval_duration,
                           setup_fee_name, setup_fee_amount, setup_fee_description,
                           activate=False):
        payment_definitions = [dict(
            name=interval.title(),
            type='REGULAR',
            frequency_interval=str(interval_count),
            frequency=interval,
            cycles='0',
            amount=dict(currency=currency, value=str(amount)),
        )]
        # Free Trial
        if trial_period_interval_count and trial_period_interval:
            payment_definitions.append(dict(
                name="%s %s %s" % (
                    trial_period_interval_duration * trial_period_interval_count,
                    trial_period_interval.title(),
                    "Discounted Rate" if trial_period_amount else "Trial"
                ),
                type='TRIAL',
                frequency_interval=str(trial_period_interval_count),
                frequency=trial_period_interval,
                cycles=str(trial_period_interval_duration),
                amount=dict(currency=currency, value=str(trial_period_amount)),
            ))
        params = dict(
            name=name,
            description=short_description,
            type='INFINITE',  # FIXED or INFINITE
            merchant_preferences=dict(
                auto_bill_amount='YES',
                cancel_url=full_reverse('billing:paypal:paypal_canceled'),
                return_url=full_reverse('billing:paypal:paypal_authorized'),
                max_fail_attempts='3',
                initial_fail_amount_action='CANCEL',
                setup_fee=dict(currency=currency, value=str(setup_fee_amount)),
            ),
            payment_definitions=payment_definitions,
        )
        logger.debug(params)
        billing = paypalrestsdk.BillingPlan(params)
        if not billing.create():
            raise PaypalError(billing.error)
        if activate:
            cls._paypal_change_paypal_plan_state(billing.id, 'ACTIVE')
        return billing.id

    @classmethod
    @paypal_error_catcher
    def update(cls, icmo_plan_id, **kwargs):
        raise NotImplementedError

    @classmethod
    @paypal_error_catcher
    def delete(cls, icmo_plan_id):
        cls.paypal_change_plans_state(icmo_plan_id, 'DELETED')
        return True

    @classmethod
    @paypal_error_catcher
    def activate(cls, icmo_plan_id):
        cls.paypal_change_plans_state(icmo_plan_id, 'ACTIVE')
        return True

    @classmethod
    @paypal_error_catcher
    def deactivate(cls, icmo_plan_id):
        cls.paypal_change_plans_state(icmo_plan_id, 'INACTIVE')
        return True

    @classmethod
    @paypal_error_catcher
    def paypal_change_plans_state(cls, icmo_plan_id, state):
        if state not in ('ACTIVE', 'INACTIVE', 'DELETED'):
            raise ValueError("Unrecognized state '%s', must be either ACTIVE OR INACTIVE" % state)
        for paypal_plan in PaypalSubscriptionPlanRegistry.objects.filter(
                icmo_plan_id=icmo_plan_id):
            cls._paypal_change_paypal_plan_state(paypal_plan.paypal_plan_id, state)
            if state in ('ACTIVE', 'INACTIVE'):
                paypal_plan.is_active = state is 'ACTIVE'
                paypal_plan.save()
            elif state is 'DELETED':
                paypal_plan.delete()
        return True

    @classmethod
    @paypal_error_catcher
    def _paypal_change_paypal_plan_state(cls, paypal_plan_id, state):
        billing_plan = paypalrestsdk.BillingPlan.find(paypal_plan_id)
        update_attributes = [dict(
            op="replace",  # only allowed operation,
            path="/",  # Beats me
            value=dict(
                state=state,
            )
        )]
        if not billing_plan.replace(update_attributes):
            # If the plan is already in the right state for whatever reason, then we continue
            if billing_plan.error['message'] == 'Validation Error.' \
                    and billing_plan.error['details'][0]['issue'] == 'Plan already in same state.':
                return True
            raise PaypalError(billing_plan.error)
        return True


class PaypalSubscription(ProviderSubscription):
    @classmethod
    @paypal_error_catcher
    def create(cls, icmo_subscription_id, icmo_plan_id, customer_email, customer_name,
               payment_token, icmo_coupon_id=None):
        """
        Compatibility wrapper.  Stripe has a 1 step process paypal has a 2 step process.
        :param payment_token: The paypal authorization token returned by the paypal authorization
        url
        :return:
        """
        plan_link = PaypalSubscriptionPlanRegistry.objects.get(icmo_plan_id=icmo_plan_id,
                                                               icmo_coupon_id=icmo_coupon_id)
        paypal_subscription_id = cls.paypal_execute_subscription(payment_token)
        PaypalSubscriptionRegistry.objects.create(
            icmo_subscription_id=icmo_subscription_id,
            paypal_subscription_id=paypal_subscription_id,
            paypal_plan_id=plan_link.paypal_plan_id
        )
        return True

    @classmethod
    @paypal_error_catcher
    def cancel(cls, icmo_subscription_id, at_period_end=True, note=None):

        try:
            billing_agreement = paypalrestsdk.BillingAgreement.find(icmo_subscription_id)
            if not billing_agreement.cancel(dict(note=note)):
                raise PaypalError(billing_agreement.error)
        except paypalrestsdk.ResourceNotFound:
            logger.warning(
                "Paypal agreement id %s was not found, assuming canceled" %
                icmo_subscription_id)
            pass
        return True

    # ========================
    # PAYPAL SPECIFIC METHODS
    # ========================

    @classmethod
    @paypal_error_catcher
    def paypal_execute_subscription(cls, paypal_token):
        """
        Execute/Start the subscription using the approval token generated by the customer
        visiting the approval url returned by create_subscription

        :param paypal_token:
        :return: paypal_agreement_id
        """
        billing_agreement_response = paypalrestsdk.BillingAgreement.execute(paypal_token)
        return billing_agreement_response.id

    @classmethod
    @paypal_error_catcher
    def paypal_create_subscription_agreement(cls, icmo_plan_id, plan_name, cancel_url,
                                             icmo_coupon_id=None):
        plan_link = PaypalSubscriptionPlanRegistry.objects.get(
            icmo_plan_id=icmo_plan_id, icmo_coupon_id=icmo_coupon_id
        )
        billing_agreement = paypalrestsdk.BillingAgreement(dict(
            name="%s Agreement" % plan_name,
            description="%s Agreement" % plan_name,
            # must be in the future and must be in a specific format
            start_date=get_utc_timestamp(),
            plan=dict(
                id=plan_link.paypal_plan_id
            ),
            payer=dict(
                payment_method='paypal'
            ),
            override_merchant_preferences=dict(
                cancel_url=full_url_from_path(cancel_url),
                return_url=full_reverse('billing:paypal:paypal_authorized')
            )
        ))
        if not billing_agreement.create():
            raise PaypalError(billing_agreement.error)

        # pop out the approval url and return it.  the customer must be redirected
        # here to approve the transaction
        return [x['href'] for x in billing_agreement['links'] if x['rel'] == 'approval_url'].pop()


class PaypalCoupon(ProviderCoupon):
    # todo Remove max_redemptions and redeem_by to be icmo side, not provider side
    @classmethod
    @paypal_error_catcher
    def create(cls, icmo_coupon_id, code, short_description, duration, amount_off, percent_off,
               currency, duration_in_months, max_redemptions, redeem_by, setup_fee_amount_off,
               setup_fee_percent_off):
        """
        Paypal coupons are not stored on paypal, as paypal does not support
        billing agreement discounts.  Instead we create plan variants which have the discounts
        applied to them.
        """

        # Create a copy of the coupon for future use
        PaypalCouponRegistry.objects.create(
            icmo_coupon_id=icmo_coupon_id, code=code, short_description=short_description,
            duration=duration, amount_off=amount_off, percent_off=percent_off,
            currency=currency, duration_in_months=duration_in_months,
            setup_fee_amount_off=setup_fee_amount_off, setup_fee_percent_off=setup_fee_percent_off,
        )
        # Create the plan variants
        for paypal_plan in PaypalSubscriptionPlanRegistry.objects.filter(icmo_coupon_id=None):
            PaypalCoupon.paypal_create_coupon_plan(
                icmo_coupon_id, code, short_description, duration, amount_off, percent_off,
                currency, duration_in_months, max_redemptions, redeem_by,
                setup_fee_amount_off, setup_fee_percent_off, paypal_plan
            )
        return True

    @classmethod
    @paypal_error_catcher
    def paypal_create_coupon_plan(cls, icmo_coupon_id, code, short_description, duration,
                                  amount_off, percent_off, currency, duration_in_months,
                                  max_redemptions,
                                  redeem_by, setup_fee_amount_off, setup_fee_percent_off,
                                  paypal_plan):
        paypal_plan_id = paypal_plan.pk
        coupon_plan = paypal_plan
        coupon_plan.pk = None  # This will now be a new object on save
        coupon_plan.paypal_plan_id = None

        # Link to the coupon and the original plan
        coupon_plan.icmo_coupon_id = icmo_coupon_id
        coupon_plan.variant_of_id = paypal_plan_id

        # Override the plan settings with the necessary modifications
        coupon_plan.short_description = "%s %s discount applied" % (
            coupon_plan.short_description, code)

        # Setup fee
        coupon_plan.setup_fee_amount = get_adjusted_fee(setup_fee_amount_off,
                                                        setup_fee_percent_off,
                                                        paypal_plan.setup_fee_amount)

        # Time limited recurring discounts are trials in paypal
        if duration == 'repeating' and duration_in_months > 0:
            coupon_plan.discount_period_amount = get_adjusted_fee(amount_off, percent_off,
                                                                  paypal_plan.amount)
            coupon_plan.discount_period_interval = 'month'
            coupon_plan.discount_period_interval_count = 1
            coupon_plan.discount_period_interval_duration = duration_in_months
        # Infinite coupons just affect the regular recurring price
        elif duration == 'forever':
            coupon_plan.amount = get_adjusted_fee(amount_off, percent_off, paypal_plan.amount)

        # Create the new plan on paypal
        coupon_plan.paypal_plan_id = PaypalSubscriptionPlan.paypal_create_plan(
            coupon_plan.icmo_plan_id, coupon_plan.name, None, None,
            coupon_plan.short_description, coupon_plan.interval, coupon_plan.interval_count,
            coupon_plan.amount, coupon_plan.currency, coupon_plan.discount_period_interval,
            coupon_plan.discount_period_interval_count, coupon_plan.discount_period_amount,
            coupon_plan.discount_period_interval_duration,
            None, coupon_plan.setup_fee_amount, None, activate=coupon_plan.is_active
        )
        # save the new coupon plan
        coupon_plan.save()

    @classmethod
    @paypal_error_catcher
    def update(cls, icmo_coupon_id):
        raise NotImplementedError

    @classmethod
    @paypal_error_catcher
    def deactivate(cls, icmo_coupon_id):
        return True

    @classmethod
    @paypal_error_catcher
    def delete(cls, icmo_coupon_id):
        PaypalSubscriptionPlanRegistry.objects.filter(icmo_coupon_id=icmo_coupon_id).delete()
        PaypalCouponRegistry.objects.filter(icmo_coupon_id=icmo_coupon_id).delete()
        return True

    @classmethod
    @paypal_error_catcher
    def activate(cls, icmo_coupon_id):
        return True
