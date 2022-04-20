import paypalrestsdk
from django.conf import settings

paypalrestsdk.configure(
    dict(
        mode=settings.PAYPAL_MODE,
        client_id=settings.PAYPAL_CLIENT_ID,
        client_secret=settings.PAYPAL_CLIENT_SECRET
    )
)


def get_handler(item):
    from handlers import PaypalSubscription, PaypalSubscriptionPlan, PaypalCoupon

    handler_map = {
        'Subscription': PaypalSubscription,
        'SubscriptionPlan': PaypalSubscriptionPlan,
        'Coupon': PaypalCoupon
    }
    return handler_map[item]
