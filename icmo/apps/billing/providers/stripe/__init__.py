import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_handler(item):
    from handlers import StripeSubscription, StripeCoupon, StripeSubscriptionPlan

    handler_map = {
        'Subscription': StripeSubscription,
        'SubscriptionPlan': StripeSubscriptionPlan,
        'Coupon': StripeCoupon
    }
    return handler_map[item]
