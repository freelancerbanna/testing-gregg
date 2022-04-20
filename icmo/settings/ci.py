from staging import *

DATABASES = {
    'default': {
        'ENGINE': 'transaction_hooks.backends.postgresql_psycopg2',
        'NAME': 'test',
        'USER': os.environ.get('PG_USER'),
        'PASSWORD': os.environ.get('PG_PASSWORD'),
        'HOST': '127.0.0.1',
    }
}

# ICMO CONFIG
# For testing sanity this should be set to the same as the dev.py setting
# This way both local and CI testing can use the same prefix in tests
PROVIDERS_STRIPE_ID_PREFIX = os.environ.get('PROVIDERS_STRIPE_ID_PREFIX', 'test')
