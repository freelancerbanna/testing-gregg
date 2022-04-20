from django.conf import settings


def get_prefixed_stripe_id(stripe_id):
    return "%s-%s" % (settings.PROVIDERS_STRIPE_ID_PREFIX, stripe_id)
