from django.contrib import admin
from django.core.checks import messages

from billing.providers.paypal_rest.models import PaypalSubscriptionPlanRegistry, \
    PaypalSubscriptionRegistry, PaypalCouponRegistry
from billing.providers.stripe.models import StripeSubscriptionPlanRegistry, StripeCouponRegistry, \
    StripeSubscriptionRegistry
from models import BillingAccount, SubscriptionPlan, Subscription, Coupon, BillingContract


class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    actions = ['activate_subscription', 'deactivate_subscription', 'delete_subscription']

    def get_actions(self, request):
        actions = super(SubscriptionPlanAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def activate_subscription(self, request, queryset):
        [x.activate() for x in queryset]
        self.message_user(request, "Subscription Plans successfully activated.")

    activate_subscription.short_description = "Activate selected subscription plans."

    def deactivate_subscription(self, request, queryset):
        [x.deactivate() for x in queryset]
        self.message_user(request, "Subscription Plans successfully deactivated.")

    deactivate_subscription.short_description = "Deactivate selected subscription plans."

    def delete_subscription(self, request, queryset):
        if queryset.filter(is_active=True):
            self.message_user(request, "You can only delete deactivated subscriptions.",
                              level=messages.WARNING)
        [x.delete() for x in queryset]
        self.message_user(request, "Subscription Plans successfully deleted.")

    delete_subscription.short_description = "Delete selected subscription plans.  Recommend " \
                                            "deactivating instead."

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_live:  # obj is not None, so this is an edit
            fields = SubscriptionPlan._meta.get_all_field_names()
            fields = [x for x in fields if x not in SubscriptionPlan.updateable_fields]
            return fields
        if not obj:
            return ['is_active']
        return []


class CouponAdmin(admin.ModelAdmin):
    list_display = ('is_active', 'code', 'created')
    actions = ['activate_coupon', 'deactivate_coupon', 'delete_coupon']

    def get_actions(self, request):
        actions = super(CouponAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def activate_coupon(self, request, queryset):
        [x.activate() for x in queryset]
        self.message_user(request, "Coupons successfully activated.")

    activate_coupon.short_description = "Activate selected coupons."

    def deactivate_coupon(self, request, queryset):
        [x.deactivate() for x in queryset]
        self.message_user(request, "Coupons successfully deactivated.")

    deactivate_coupon.short_description = "Deactivate selected coupons."

    def delete_coupon(self, request, queryset):
        if queryset.filter(is_active=True):
            self.message_user(request, "You can only delete deactivated coupons.",
                              level=messages.WARNING)
        [x.delete() for x in queryset]
        self.message_user(request, "Coupons successfully deleted.")

    delete_coupon.short_description = "Delete selected coupon.  Recommend deactivating " \
                                      "instead."

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_live:  # obj is not None, so this is an edit
            fields = Coupon._meta.get_all_field_names()
            fields = [x for x in fields if x not in Coupon.updateable_fields]
            return fields
        if not obj:
            return ['is_active']
        return []


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('is_active', 'account', 'plan', 'provider_name', 'status', 'created')


class PaypalSubscriptionPlanRegistryAdmin(admin.ModelAdmin):
    list_display = ('icmo_plan', 'paypal_plan_id', 'icmo_coupon', 'amount', 'setup_fee_amount',
                    'discount_period_interval', 'discount_period_interval_duration',
                    'discount_period_amount')


class BillingContractAdmin(admin.ModelAdmin):
    list_display = ('account', 'signing_user', 'company_name', 'date', 'pdf_url', 'url')


admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(BillingAccount)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(PaypalSubscriptionPlanRegistry, PaypalSubscriptionPlanRegistryAdmin)
admin.site.register(PaypalSubscriptionRegistry)
admin.site.register(PaypalCouponRegistry)
admin.site.register(StripeSubscriptionPlanRegistry)
admin.site.register(StripeSubscriptionRegistry)
admin.site.register(StripeCouponRegistry)
admin.site.register(BillingContract, BillingContractAdmin)
