from decimal import Decimal
import logging
from random import randint

import re
from dirtyfields import DirtyFieldsMixin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

from core.helpers import generate_pdf
from core.models import IcmoModel, ActiveManager, NoUpdatesModel
from .helpers import get_adjusted_fee, check_provider
from . import providers

logger = logging.getLogger(__name__)

PAYMENT_PROVIDER_STRIPE = 'stripe'
PAYMENT_PROVIDER_PAYPAL = 'paypal_rest'
PERMISSION_NONE = 0
PERMISSION_READ = 1
PERMISSION_WRITE = 2
PERMISSION_OWNER = 3
ACCESS_CHOICES = (
    (PERMISSION_READ, 'Read'), (PERMISSION_WRITE, 'Write'), (PERMISSION_NONE, 'None'))
SUBSCRIPTION_CHOICES = ((PAYMENT_PROVIDER_STRIPE, 'Stripe'), (PAYMENT_PROVIDER_PAYPAL, 'PayPal'))
CURRENCY_CHOICES = (('USD', 'USD'), ('CAD', 'CAD'))
INTERVAL_CHOICES = (('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year'))
SUBSCRIPTION_STATUS_CHOICES = (
    ('active', 'Active'),
    ('trialing', 'Trialing'),
    ('past_due', 'Past Due'),  # payment failed
    ('canceled', 'Canceled'),
    ('unpaid', 'Unpaid'),  # all payment attempts have failed
)

COUPON_TYPE_CHOICES = (
    ('forever', 'Forever'),
    ('once', 'Once'),
    ('repeating', 'Repeating'),
)


class ProviderBackedModel(DirtyFieldsMixin, TimeStampedModel):
    class Meta:
        abstract = True

    updateable_fields = ('is_active',)

    is_active = models.BooleanField(_('active'), default=False)
    is_live = models.BooleanField('live', default=False, editable=False)

    objects = models.Manager()
    active = ActiveManager()

    def _call_all_providers_action(self, action, *args, **kwargs):
        """
        Calls a method in a module for each provider specified in PROVIDERS
        The module is specified through Meta.provider_module
        :param args: The args if any to pass to the callable
        :rtype : dict:  dict of responses returned by the methods
        :param action: the method to call
        """
        for provider_name in settings.ICMO_BILLING_PROVIDERS:
            self._call_provider_action(provider_name, action, *args, **kwargs)
        return True

    def _call_provider_action(self, provider_name, action, *args, **kwargs):
        provider = getattr(providers, provider_name)
        klass = provider.get_handler(self.__class__.__name__)
        method = getattr(klass, action)
        method(self.pk, *args, **kwargs)

    def save(self, *args, **kwargs):
        dirty_fields = self.get_dirty_fields().keys()
        forbidden_changed_fields = set(dirty_fields) - set(self.updateable_fields or [])
        if (self.pk  # existing object
            and self.is_live  # object is currently live
            and 'is_live' not in dirty_fields  # but has not just been switched live
            # and fields have been modified that should be static
            and forbidden_changed_fields):
            raise ValueError(
                "Some fields of this object cannot be changed after creation."
                "These fields had disallowed changes:  %s" % forbidden_changed_fields)
        super(ProviderBackedModel, self).save(*args, **kwargs)


class MultiProviderBackedModel(ProviderBackedModel):
    class Meta:
        abstract = True

    def create_provider_versions(self, *args):
        raise NotImplementedError

    def activate(self):
        self.is_active = True
        # The first time the object is activated we take it live on stripe and paypal
        # creating all the necessary objects.
        if not self.is_live:
            self.is_live = True  # A one way state change to show this plan is now live
            self.create_provider_versions()
            logger.info(
                "%s %s has gone live successfully." % (self._meta.verbose_name.title(), self.pk))

        self._call_all_providers_action('activate')
        logger.info("%s %s has been activated successfully." % (
            self._meta.verbose_name.title(), self.pk))
        self.save()

    def deactivate(self):
        self.is_active = False
        self._call_all_providers_action('deactivate')
        logger.info("%s %s has been deactivated successfully." % (
            self._meta.verbose_name.title(), self.pk))
        self.save()

    def delete(self, using=None):
        self._call_all_providers_action('delete')
        super(MultiProviderBackedModel, self).delete(using=using)


class BillingAccount(IcmoModel):
    """ 
        Keeps track of relationships between users, subscriptions, companies,
        etc. An account has one owner and potentially many companies. This
        is distinct from other users having permissions to company data. This
        model deals with account ownership.
    """

    class Meta:
        ordering = ('created',)

    account_number = models.CharField(max_length=11, editable=False, unique=True)
    owner = models.OneToOneField('icmo_users.IcmoUser')

    # null so we can create the object at signup (before the company has been created)
    billing_company = models.ForeignKey('companies.Company', blank=True, null=True)
    active_subscription = models.ForeignKey('Subscription', related_name='active_for_account',
                                            blank=True, null=True)
    limit_max_companies = models.PositiveSmallIntegerField(default=0, blank=True, null=True)

    def set_active_subscription(self, subscription):
        self.active_subscription = subscription
        self.limit_max_companies = subscription.plan.limit_max_companies
        self.save()

    def clear_active_subscription(self, unpublish_companies=True):
        self.active_subscription = None
        self.limit_max_companies = 0
        self.save()

    @staticmethod
    def generate_unique_account_number():
        while True:
            number = "".join([str(randint(0, 9)) for x in range(0, 9)])
            number = re.sub(r'([0-9]{3})(?!$)', '\\1-', number)
            if not BillingAccount.objects.filter(account_number=number).exists():
                return number

    def __unicode__(self):
        return "Account #%s" % self.account_number

    @property
    def slug(self):
        return self.account_number

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = BillingAccount.generate_unique_account_number()
        return super(BillingAccount, self).save(*args, **kwargs)


class Subscription(ProviderBackedModel):
    account = models.ForeignKey('BillingAccount', editable=False)
    plan = models.ForeignKey('SubscriptionPlan', editable=False)
    coupon = models.ForeignKey('Coupon', editable=False, null=True, blank=True)
    provider_name = models.CharField(max_length=30, blank=True,
                                     choices=SUBSCRIPTION_CHOICES, editable=False)
    status = models.CharField(max_length=255, blank=True, choices=SUBSCRIPTION_STATUS_CHOICES)

    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True, editable=False)
    trial_end = models.DateTimeField(null=True, blank=True)

    @property
    def subscription_fee_terms(self):
        if self.coupon:
            return self.coupon.get_applied_recurring_discount_description(self.plan.amount)
        return "$%s %s" % (self.plan.display_price, self.plan.human_interval)

    @property
    def setup_fee_terms(self):
        if self.coupon:
            return self.coupon.get_applied_setup_fee_discount_description(self.plan.amount)
        return "$%s" % self.plan.setup_fee_amount

    @property
    def subscription_fee_coupon_applied(self):
        if self.coupon and self.coupon.has_pricetype_discount('recurring'):
            return True
        return False

    @property
    def setup_fee_coupon_applied(self):
        if self.coupon.has_pricetype_discount('setup_fee'):
            return True
        return False

    @property
    def provider_plan_id(self):
        if self.provider == PAYMENT_PROVIDER_PAYPAL:
            return self.plan.paypal_plan_id
        elif self.provider == PAYMENT_PROVIDER_STRIPE:
            return self.plan.stripe_plan_id
        raise ValueError("Provider is not configured.")

    def subscribe(self, token, coupon=None):
        """
        Begins the subscription with the payment provider, billing any due amounts.
        :param token: The payment token (stripe card token or paypal postauth token)
        :rtype : string: the new subscription id
        """
        icmo_coupon_id = getattr(coupon, 'id', None)
        self._call_provider_action(
            check_provider(self.provider_name), 'create',
            self.plan_id, self.account.owner.email,
            self.account.owner.get_full_name(),
            token, icmo_coupon_id=icmo_coupon_id
        )
        self.is_active = True
        self.is_live = True
        self.save()
        return True

    def cancel(self, at_period_end=True, note="Canceling the subscription."):
        self._call_provider_action(
            check_provider(self.provider_name), 'cancel', at_period_end=at_period_end, note=note
        )
        self.status = 'canceled'
        self.ended_at = timezone.now()
        logger.info(
            "Subscription for account %s (owner %s) has been canceled." % (
                self.account.account_number, self.account.owner.email
            )
        )
        # fixme implement at_period_end handling
        self.save()

    @property
    def active_contract(self):
        return self.billingcontract_set.all().order_by('-date').first()

    @staticmethod
    def start_subscription(account, plan, provider_name, token, coupon=None):
        """
        Starts the subscription with the payment provider and records all ids.
        :param account: The billing account to use
        :param plan: The chosen Subscription Plan (must be live and active)
        :param provider_name: Either paypal or stripe
        :param token: The stripe cc token or the paypal postauth token
        :return:
        """
        # Run some sanity checks on the plan to make sure it is ready to use
        plan.validate_for_subscription()

        subscription = Subscription.objects.create(account=account, plan=plan,
                                                   provider_name=check_provider(provider_name),
                                                   coupon=coupon)
        subscription.subscribe(token, coupon=coupon)
        return subscription

    def __unicode__(self):
        return "%s" % self.plan


class SubscriptionPlan(MultiProviderBackedModel):
    class Meta:
        ordering = ('interval', 'amount')

    # These are the only fields that can be changed after creation
    updateable_fields = ('is_active', 'full_description')

    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name')
    short_description = models.CharField(max_length=200)
    full_description = models.TextField()
    statement_description = models.CharField(
        max_length=22,
        help_text="This will (may) appear on the bank "
                  "statement, max 22 characters, cannot include <>\"' characters."
    )

    limit_max_companies = models.PositiveSmallIntegerField(blank=True, null=True)

    currency = models.CharField(choices=CURRENCY_CHOICES, default='USD', max_length=3)
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES, default='month')
    interval_count = models.PositiveSmallIntegerField(verbose_name="Intervals between charges",
                                                      default=1, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=7,
                                 verbose_name="Amount (per period)")
    amount_display_interval = models.PositiveSmallIntegerField(
        help_text="If you want the pricing interval display to be different than the billing "
                  "interval (for example show monthly pricing but bill quarterly), then set this "
                  "to the number of intervals you'd like to display.",
        blank=True, null=True)

    free_trial_period_interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES,
                                                  blank=True, null=True)
    free_trial_period_interval_duration = models.PositiveSmallIntegerField(blank=True, null=True)

    setup_fee_name = models.CharField(max_length=100, blank=True)
    setup_fee_amount = models.DecimalField(decimal_places=2, max_digits=7, default=Decimal('0.00'))
    setup_fee_description = models.CharField(max_length=200, blank=True)

    minimum_duration_in_intervals = models.PositiveSmallIntegerField(blank=True, null=True)

    # Future enhancement
    # addons = models.ManyToManyField(SubscriptionAddon, through=SubscriptionPlanAddons)

    @property
    def display_price(self):
        if self.amount_display_interval:
            return self.amount / self.interval_count * self.amount_display_interval
        return self.amount

    @property
    def human_interval(self):
        single_interval = dict(day='daily', week='weekly', month='monthly', year='yearly')
        if self.interval_count == 1:
            return single_interval[self.interval]
        elif self.interval_count == 3 and self.interval == 'month':
            return 'quarterly'
        return 'every %s %ss' % (self.interval_count, self.interval)

    def validate_for_subscription(self):
        if not self.is_active:
            raise ValueError("Plan must be active before it can be used.")
        if not self.is_live:
            raise ValueError("This plan is not live!")
        return True

    def create_provider_versions(self):
        return self._call_all_providers_action(
            'create', self.name, self.slug, self.statement_description,
            self.short_description, self.interval, self.interval_count,
            self.amount, self.currency, self.free_trial_period_interval,
            1, Decimal('0'), self.free_trial_period_interval_duration,
            self.setup_fee_name, self.setup_fee_amount, self.setup_fee_description
        )

    def __unicode__(self):
        return self.name


class Coupon(MultiProviderBackedModel):
    updateable_fields = ['times_redeemed']

    """
    An implementation of the Stripe coupon model, modified to add setup fee discounts
    """
    code = models.CharField(max_length=25)
    short_description = models.CharField(max_length=100)
    duration = models.CharField(max_length=25, choices=COUPON_TYPE_CHOICES, default='once')
    amount_off = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    percent_off = models.PositiveIntegerField(blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    duration_in_months = models.PositiveSmallIntegerField(
        blank=True, null=True,
        help_text="If duration is repeating, the number of month this coupon applies."
    )
    max_redemptions = models.PositiveIntegerField(blank=True, null=True)
    times_redeemed = models.PositiveIntegerField(default=0, editable=False)
    redeem_by = models.DateTimeField(blank=True, null=True)

    setup_fee_amount_off = models.DecimalField(max_digits=7, decimal_places=2, blank=True,
                                               null=True)
    setup_fee_percent_off = models.PositiveIntegerField(blank=True, null=True)

    def increment(self):
        self.times_redeemed += 1
        self.save()

    def is_valid(self):
        if self.max_redemptions != 0 and self.times_redeemed >= self.max_redemptions:
            return False
        if self.redeem_by and timezone.now() >= self.redeem_by:
            return False
        return True

    def get_human_price(self, price_type, amount):
        price = self.apply_to_price(price_type, amount)
        if price:
            return "$%.2f" % price
        return "Free"

    def get_applied_recurring_discount_description(self, amount):
        description = "%s" % self.get_human_price('recurring', amount)
        if self.amount_off or self.percent_off:
            description += " (%s)" % self.get_discount_description('recurring')
            description += " %s" % self.human_duration
            if self.duration != 'infinite':
                description += ", after that $%s per period." % amount
        return description

    def get_applied_setup_fee_discount_description(self, amount):
        description = "%s" % self.get_human_price('setup_fee', amount)
        if self.setup_fee_amount_off or self.setup_fee_percent_off:
            description += " (%s)" % self.get_discount_description('setup_fee')
        return description

    def has_pricetype_discount(self, pricetype):
        if pricetype == 'setup_fee' and (self.setup_fee_amount_off or self.setup_fee_percent_off):
            return True
        elif pricetype == 'recurring' and (self.amount_off or self.percent_off):
            return True
        return False

    @property
    def human_duration(self):
        description = ""
        if self.duration == 'repeating':
            description += "every billing period for the first %s months" % self.duration_in_months
        elif self.duration == 'once':
            description += "for the first billing period"
        return description

    def get_discounts_for_price_type(self, price_type):
        if price_type == 'setup_fee':
            discount_amount_off = self.setup_fee_amount_off
            discount_percent_off = self.setup_fee_percent_off
        elif price_type == 'recurring':
            discount_amount_off = self.amount_off
            discount_percent_off = self.percent_off
        else:
            raise ValueError("Unrecognized price type, should be one of:  setup_fee, recurring")
        return discount_amount_off, discount_percent_off

    def get_discount_description(self, price_type):
        amount_off, percent_off = self.get_discounts_for_price_type(price_type)
        if amount_off:
            return "$%s off" % amount_off
        elif percent_off:
            return "%s%% off" % percent_off
        raise ValueError("No discount set!")

    @property
    def discount_description(self):
        description = []
        if self.amount_off or self.percent_off:
            description.append("%s of the recurring fee %s." % (
                self.get_discount_description('recurring'), self.human_duration))
        if self.setup_fee_amount_off or self.setup_fee_percent_off:
            description.append(
                "%s off of the setup fee." % self.get_discount_description('setup_fee'))
        return "  ".join(description)

    def create_provider_versions(self):
        return self._call_all_providers_action(
            'create', self.code, self.short_description, self.duration, self.amount_off,
            self.percent_off, self.currency, self.duration_in_months, self.max_redemptions,
            self.redeem_by, self.setup_fee_amount_off, self.setup_fee_percent_off
        )

    def apply_to_price(self, price_type, amount):
        if price_type == 'setup_fee':
            return get_adjusted_fee(self.setup_fee_amount_off, self.setup_fee_percent_off, amount)
        elif price_type == 'recurring':
            return get_adjusted_fee(self.amount_off, self.percent_off, amount)
        raise ValueError("Unrecognized price type, should be one of:  setup_fee, recurring")

    def save(self, *args, **kwargs):
        if self.percent_off and self.amount_off:
            raise ValueError("You cannot set both percent_off AND amount_off")
        if self.setup_fee_amount_off and self.setup_fee_percent_off:
            raise ValueError("You cannot set both setup_fee_percent_off and setup_fee_amount_off")
        if self.duration == 'repeating' and not self.duration_in_months:
            raise ValueError("You must set a duration in months for a repeating type coupon.")
        super(Coupon, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.code


class BillingContract(NoUpdatesModel):
    account = models.ForeignKey('BillingAccount')
    signing_user = models.ForeignKey('icmo_users.IcmoUser')
    subscription = models.ForeignKey('Subscription')
    slug = AutoSlugField(populate_from=['account', 'version', 'date'])
    name = models.CharField(verbose_name="Print your name", max_length=255)
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True, editable=False)

    signature_json = models.TextField(blank=True)
    signature_uri_b64 = models.TextField(blank=True)
    version = models.CharField(max_length=255, editable=False,
                               default=settings.CURRENT_CONTRACT_VERSION_NUMBER)
    pdf_url = models.URLField(blank=True)

    @property
    def template_name(self):
        return "contracts/contract.v%s.html" % self.version

    @property
    def url(self):
        return reverse('billing:contract_view', kwargs=dict(slug=self.slug))

    def generate_pdf(self):
        with open(settings.COUNTERSIGNATURE_B64_URI_FILE) as fp:
            countersignature_uri = fp.read()
        return generate_pdf(
            'contracts/pdf_contract.html',
            dict(object=self, countersignature_uri=countersignature_uri)
        )


"""
Future enhancements
class SubscriptionAddon(SubscriptionBase):
    amount = models.DecimalField(decimal_places=2, max_digits=7)


class SubscriptionPlanAddons(models.Model):
    plan = models.ForeignKey(SubscriptionPlan)
    addon = models.ForeignKey(SubscriptionAddon)
    max_number_allowed = models.PositiveSmallIntegerField(default=1)
    required = models.BooleanField(default=False)
    one_time = models.BooleanField(default=True,
                                   help_text="If true, then only bills once, otherwise
 bills every interval period.")
"""
