"""
Each method should be idempotent.  Only in case of a true mismatch between expectations
and reality should an error be raised
"""


class ProviderNetworkErrorException(Exception):
    pass


class ProviderInvalidCredentialsException(Exception):
    pass


class ProviderObjectAlreadyExists(Exception):
    pass


class ProviderAPIError(Exception):
    pass


class ProviderSubscriptionPlan(object):
    @classmethod
    def create(cls, icmo_plan_id, name, slug, statement_description, short_description, interval,
               interval_count, amount, currency, trial_period_interval,
               trial_period_interval_count, trial_period_amount, trial_period_interval_duration,
               setup_fee_name, setup_fee_amount, setup_fee_description):
        raise NotImplementedError

    @classmethod
    def update(cls, icmo_plan_id, **kwargs):
        raise NotImplementedError

    @classmethod
    def delete(cls, icmo_plan_id):
        raise NotImplementedError

    @classmethod
    def activate(cls, icmo_plan_id):
        raise NotImplementedError

    @classmethod
    def deactivate(cls, icmo_plan_id):
        raise NotImplementedError


class ProviderSubscription(object):
    @classmethod
    def create(cls, icmo_subscription_id, icmo_plan_id, customer_email, customer_name,
               payment_token, coupon_id=None):
        raise NotImplementedError

    @classmethod
    def cancel(cls, icmo_subscription_id, at_period_end=True, note=None):
        raise NotImplementedError


class ProviderCoupon(object):
    @classmethod
    def create(cls, icmo_coupon_id, code, short_description, duration, amount_off, percent_off,
               currency, duration_in_months, max_redemptions, redeem_by,
               setup_fee_amount_off, setup_fee_percent_off):
        raise NotImplementedError

    @classmethod
    def update(cls, icmo_coupon_id):
        raise NotImplementedError

    @classmethod
    def delete(cls, icmo_coupon_id):
        raise NotImplementedError

    @classmethod
    def activate(cls, icmo_coupon_id):
        raise NotImplementedError

    @classmethod
    def deactivate(cls, icmo_coupon_id):
        raise NotImplementedError
