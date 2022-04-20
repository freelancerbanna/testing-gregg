from django.db import models
from django_extensions.db.fields import ShortUUIDField
from django_extensions.db.fields.json import JSONField
from django_extensions.db.models import TimeStampedModel

from core.models import NoUpdatesModel, PartialUpdatesModel


class PaypalSubscriptionPlanRegistry(PartialUpdatesModel, TimeStampedModel):
    updateable_fields = ['is_active']
    """
    This model compensates for the lack of discount/coupon support in Paypal for
    billing agreements.  Each SubscriptionPlan/Coupon combo (including no coupon)
    will get one of these intermediary models.
    """
    icmo_plan = models.ForeignKey('billing.SubscriptionPlan')
    paypal_plan_id = models.CharField(max_length=100, unique=True)
    icmo_coupon = models.ForeignKey('billing.Coupon', blank=True, null=True)
    variant_of = models.ForeignKey('PaypalSubscriptionPlanRegistry', blank=True, null=True)
    name = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255)
    currency = models.CharField(max_length=3)
    interval = models.CharField(max_length=10)
    interval_count = models.PositiveSmallIntegerField()
    amount = models.DecimalField(decimal_places=2, max_digits=7)

    discount_period_interval = models.CharField(max_length=10, blank=True, null=True)
    discount_period_interval_count = models.PositiveSmallIntegerField(blank=True, null=True)
    discount_period_interval_duration = models.PositiveIntegerField(blank=True, null=True)
    discount_period_amount = models.DecimalField(decimal_places=2, max_digits=7, blank=True,
                                                 null=True)
    setup_fee_amount = models.DecimalField(decimal_places=2, max_digits=7, blank=True, null=True)

    is_active = models.BooleanField(default=False)

    def __unicode__(self):
        return self.paypal_plan_id


class PaypalSubscriptionRegistry(NoUpdatesModel, TimeStampedModel):
    icmo_subscription = models.ForeignKey('billing.Subscription')
    paypal_subscription_id = models.CharField(max_length=255, unique=True)
    paypal_plan_id = models.CharField(max_length=255)


class PaypalCouponRegistry(NoUpdatesModel, TimeStampedModel):
    icmo_coupon = models.ForeignKey('billing.Coupon')
    code = models.CharField(max_length=25)
    short_description = models.CharField(max_length=100)
    duration = models.CharField(max_length=25)
    amount_off = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    percent_off = models.PositiveIntegerField(blank=True, null=True)
    currency = models.CharField(max_length=3)
    duration_in_months = models.PositiveSmallIntegerField(
        blank=True, null=True,
        help_text="If duration is repeating, the number of month this coupon applies."
    )
    setup_fee_amount_off = models.DecimalField(max_digits=7, decimal_places=2, blank=True,
                                               null=True)
    setup_fee_percent_off = models.PositiveIntegerField(blank=True, null=True)


class AwaitingPaypalAuthorization(NoUpdatesModel, TimeStampedModel):
    """
    This model stores form data while we wait for the user to authorize
     a paypal transaction.  The expected use is to set a session var to this uuid
     to identify authorizations to particular requests.
    """
    uuid = ShortUUIDField(editable=False, primary_key=True)
    form_data = JSONField(editable=False)


class PaypalNotification(NoUpdatesModel, TimeStampedModel):
    id = models.CharField(max_length=100, primary_key=True)
    create_time = models.DateField()
    resource_type = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    summary = models.CharField(max_length=200)
    resource_id = models.CharField(max_length=100)
    resource_create_time = models.CharField(max_length=100)
    resource_update_time = models.CharField(max_length=100)
    resource_state = models.CharField(max_length=100)
    resource_amount_total = models.CharField(max_length=100)
    resource_amount_currency = models.CharField(max_length=100)
    resource_amount_details_subtotal = models.CharField(max_length=100)
    resource_parent_payment = models.CharField(max_length=100)
    resource_valid_until = models.CharField(max_length=100)
    resource_links_self = models.URLField(max_length=200)
    resource_links_capture = models.URLField(max_length=200)
    resource_links_void = models.URLField(max_length=200)
    resource_links_parent_payment = models.URLField(max_length=200)
    links_self = models.URLField(max_length=200)
    links_resend = models.URLField(max_length=200)
    request_json = JSONField()

    @staticmethod
    def create_from_json(request_json):
        from billing.providers.paypal_rest.helpers import flatten_webhook_json

        flat_data = flatten_webhook_json(request_json)
        return PaypalNotification.objects.create(request_json=request_json, **flat_data)
