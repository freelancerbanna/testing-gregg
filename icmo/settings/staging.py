from .prod import *


# DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
# END DEBUG CONFIGURATION


ALLOWED_HOSTS = ['intelligentcmo-staging.herokuapp.com']

ACTIVATION_TEAM_EMAIL = "cordery@gmail.com"

# ICMO CONFIG
ROOT_URL = "https://intelligentcmo-staging.herokuapp.com"
PROVIDERS_STRIPE_ID_PREFIX = os.environ.get('PROVIDERS_STRIPE_ID_PREFIX', 'staging')


# DJANGO CRISPY FORMS CONFIG
CRISPY_FAIL_SILENTLY = False


# PAYPAL REST SDK CONFIG
PAYPAL_MODE = 'sandbox'
