from django.db import models

from billing.helpers import apply_to_price


class StripeSubscriptionPlanRegistry(models.Model):
    icmo_plan = models.ForeignKey('billing.SubscriptionPlan')
    stripe_plan_id = models.CharField(max_length=255)

    # These aren't captureable in stripe so we record them here separately
    setup_fee_name = models.CharField(max_length=100, blank=True)
    setup_fee_amount = models.PositiveIntegerField(default=0)


class StripeSubscriptionRegistry(models.Model):
    icmo_subscription = models.ForeignKey('billing.Subscription')
    stripe_subscription_id = models.CharField(max_length=255)
    stripe_customer_id = models.CharField(max_length=255)
    card_last_4 = models.CharField(max_length=4, blank=True)
    card_kind = models.CharField(max_length=50, blank=True)
    card_exp_month = models.PositiveIntegerField(blank=True, null=True)
    card_exp_year = models.PositiveIntegerField(blank=True, null=True)


class StripeCouponRegistry(models.Model):
    """
    ICMO coupons affecting both setup fee and recurring fee must be split into two stripe coupons
    This model tracks them.
    """
    icmo_coupon = models.ForeignKey('billing.Coupon')
    stripe_coupon_id = models.CharField(max_length=255, blank=True)

    # These aren't captureable in stripe so we record them here separately
    setup_fee_amount_off = models.DecimalField(max_digits=7, decimal_places=2, blank=True,
                                               null=True)
    setup_fee_percent_off = models.PositiveIntegerField(blank=True, null=True)

    def get_discounted_setup_fee(self, setup_fee_amount):
        if self.setup_fee_amount_off:
            return int(apply_to_price('amount_off', self.setup_fee_amount_off, setup_fee_amount))
        elif self.setup_fee_percent_off:
            return int(apply_to_price('percent_off', self.setup_fee_percent_off, setup_fee_amount))
        return setup_fee_amount
