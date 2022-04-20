"""
Django settings for icmo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
import re
from os.path import normpath, join, dirname, abspath, basename
from sys import path

# PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:

DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
# END PATH CONFIGURATION


# DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False
# END DEBUG CONFIGURATION


# MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('Andrew Cordery', 'cordery@gmail.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# END MANAGER CONFIGURATION


# DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}
DATABASES['default'][
    'ATOMIC_REQUESTS'] = False  # If this is true then most period signals wont fire
# END DATABASE CONFIGURATION


# GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'UTC'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# END GENERAL CONFIGURATION


# MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(DJANGO_ROOT, 'media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
# END MEDIA CONFIGURATION


# STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(DJANGO_ROOT, 'static'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    normpath(join(DJANGO_ROOT, 'assets')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

)
# END STATIC FILE CONFIGURATION

# WHITENOISE CONFIG
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = 'pim9gl3*1w9*63#^g(mt$ktjuvywn4$!v#$9mp=5r&%+7m)%#v'
# END SECRET CONFIGURATION


# TEMPLATE CONFIGURATION
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            normpath(join(DJANGO_ROOT, 'templates')),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request'
            ],
            'debug': DEBUG
        },
    },
]

# END TEMPLATE CONFIGURATION


# MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
# END MIDDLEWARE CONFIGURATION


# URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
# END URL CONFIGURATION


# APP CONFIGURATION
DJANGO_APPS = (

    # Default Django apps:
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
)

THIRD_PARTY_APPS = (
    "django_extensions",  # Useful manage.py extensions
    'rest_framework',  # REST API
    # 'simple_salesforce',
    'cloudinary',
    # 'paypal',
    # 'paypal.standard.ipn',
    'localflavor',
    'guardian',  # Object level permissions
    'crispy_forms',  # form layout flexibility
    'menu',  # page menus
    'stronghold',  # sitewide login_required,
    'djmoney',  # currency handling
    'mptt',  # tree handling
    'django_rq',  # RQ Queue support
    'timezone_field',  # model timezone fields
    'djangosecure',  # security checks
    # 'ws4redis',  # django websockets redis
    'compressor',  # minify/concat css/js files
)

LOCAL_APPS = (
    'core',
    'icmo_users',
    'companies',
    'billing',
    'billing.providers.stripe',
    'billing.providers.paypal_rest',
    'leads',
    'salesforce_icmo',
    'revenues',
    'resources',
    'budgets',
    'performance',
    'dashboards',
    'integrations',
    'accounts',
    'periods',
    'notifications',
    'demos',
    'hubspot_icmo',
    'task_boards',
    'reports'
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
# END APP CONFIGURATION


# LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    "formatters": {
        "rq_console": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
        "rq_console": {
            "level": "DEBUG",
            "class": "rq.utils.ColorizingStreamHandler",
            "formatter": "rq_console",
            "exclude": ["%(asctime)s"],
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        "rq.worker": {
            "handlers": ["rq_console"],
            "level": "DEBUG"
        },
        "icmo": {
            "handlers": ["console"],
            "level": "DEBUG"
        }
    }
}
# END LOGGING CONFIGURATION


# AUTH CONFIG
# Use a custom User model
AUTH_USER_MODEL = 'icmo_users.IcmoUser'
LOGIN_REDIRECT_URL = 'start_redirect'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

# PASSWORD HASHER CONFIGURATION
# Adds Bcrypt
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)
# END PASSWORD HASHER CONFIGURATION


# WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
# WSGI_APPLICATION = 'ws4redis.django_runserver.application'
WSGI_APPLICATION = 'wsgi.application'
# END WSGI CONFIGURATION


# TEST CONFIGURATION
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
# END TEST CONFIGURATION


# ICMO CONFIG
# Add the apps folder
SITE_APPS_ROOT = normpath(join(DJANGO_ROOT, 'apps'))
path.append(SITE_APPS_ROOT)

# Default number of items to show on a paginated page
ITEMS_PER_PAGE = 6
# Referral landing page
REFERRAL_LANDING_PAGE = "https://application.intelligentrevenue.com/account/signup"
EXPORTED_FILES_ROOT = os.path.join(DJANGO_ROOT, 'exported')
CURRENT_CONTRACT_VERSION_NUMBER = 1  # If the signup contract changes this should be incremented
ICMO_BILLING_PROVIDERS = ('stripe', 'paypal_rest')
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('core.middleware.AddCompanyPlanMiddleware',
                                           'core.middleware.AddCompanyUserMiddleware',
                                           'core.middleware.PlanBouncerMiddleware')
TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'core.context_processors.add_company_plan',
    'core.context_processors.add_time_periods',
    'core.context_processors.add_js_settings',
    'core.context_processors.add_environment'
]
# Stripe has only one test api key, so this value must be set differently in
# each testing environment to ensure that stripe objects do not collide
PROVIDERS_STRIPE_ID_PREFIX = os.environ.get('PROVIDERS_STRIPE_ID_PREFIX', 'test')
ICMO_DEFAULT_CURRENCY = 'USD'
COUNTERSIGNATURE_B64_URI_FILE = join(DJANGO_ROOT, 'data', 'countersig.b64uri')

NOTIFICATION_TYPES = (
    'notifications.notifications.TaskOverdueNotification',
)

# Stripe configuration
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "sk_test_AIhp9zWKlT5ISeUtZ4XX17WS")
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "pk_test_baTvrj7h1HkJvbNd8K7uzpBq")

# EMAIL CONFIG
DEFAULT_FROM_EMAIL = "no-reply@intelligentrevenue.com"
SERVER_EMAIL = "errors@intelligentrevenue.com"
EMAIL_BACKEND = "sgbackend.SendGridBackend"
ACTIVATION_TEAM_EMAIL = "remy@intelligentrevenue.com"

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY',
                                  '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')

# Support email
SUPPORT_EMAIL = "support@intelligentrevenue.com"

# HYPDF CONFIG
HYPDF_USER = os.environ.get('HYPDF_USER', 'app35782023@heroku.com')
HYPDF_PASSWORD = os.environ.get('HYPDF_PASSWORD', 'nmfzAoPCJapk')
HYPDF_HTMLTOPDF_URL = 'https://www.hypdf.com/htmltopdf'

# RIGHTSIGNATURE CONFIG
# url of the RightSignature form the user needs to fill out
RIGHTSIGNATURE_URL = "https://rightsignature.com/forms/IntelligentCMOOrd-648804/token/066d9b3a1f3"

# PAYPAL CONFIG
# email address associated with the PayPal merchant account
PAYPAL_MODE = None  # sandbox or live
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', None)
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', None)
PAYPAL_WEBHOOK_ID = os.environ.get('PAYPAL_WEBHOOK_ID', None)

# GRAPPELLI CONFIG
# Provides:  Admin retheme
INSTALLED_APPS = ('grappelli',) + INSTALLED_APPS
GRAPPELLI_ADMIN_TITLE = "intelligentRevenue Admin"

# DJANGO GUARDIAN CONFIG
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # this is default
    'guardian.backends.ObjectPermissionBackend',
)
ANONYMOUS_USER_ID = None  # No anonymous user permissions
GUARDIAN_RENDER_403 = True

# DJANGO CRISPY FORMS CONFIG
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# SIGPAD CONFIG
SIGPAD_HEIGHT = 300

# MAILGUN EMAIL VALIDATION CONFIG
MAILGUN_PUBLIC_KEY = os.environ.get('MAILGUN_PUBLIC_KEY',
                                    "pubkey-0f58f16c9257b73d518128141bfc484a")

# STRONGHOLD CONFIG
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('stronghold.middleware.LoginRequiredMiddleware',)
STRONGHOLD_DEFAULTS = True
STRONGHOLD_PUBLIC_NAMED_URLS = (
    'login', 'logout', 'help',
    'activate_new_user', 'activate_invited_user',
)
STRONGHOLD_PUBLIC_URLS = (
    r'^/account/password_reset/.*',
    r'^/admin/.*',
)

# DJANGO REST FRAMEWORK CONFIG
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'api.permissions.IcmoAPIPermissions'
    ),
    'DEFAULT_METADATA_CLASS': 'api.metadata.KendoUIMetadata',
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/minute',
        'user': '100/minute'
    },
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'DEFAULT_EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# DJMONEY CONFIG
CURRENCIES = ('USD',)
from moneyed import USD

DEFAULT_CURRENCY = USD

# DJANGO REDIS
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDISCLOUD_URL', 'redis://127.0.0.1:6379/1'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_KWARGS": {"max_connections": 30}
        }
    },
    "apicache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDISCLOUD_APICACHE_URL', 'redis://127.0.0.1:6379/1'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_KWARGS": {"max_connections": 256}
        }
    }
}
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# DJANGO-RQ CONFIG
RQ_QUEUES = {
    'default': {
        'USE_REDIS_CACHE': 'default',
        'DEFAULT_TIMEOUT': 360,
    },
    'integrations': {
        'USE_REDIS_CACHE': 'default',
        'DEFAULT_TIMEOUT': 360,
    },
    # 'high': {
    # 'URL': os.getenv('REDISTOGO_URL', 'redis://localhost:6379'), # If you're on Heroku
    # 'DB': 0,
    # 'DEFAULT_TIMEOUT': 500,
    # },
    # 'low': {
    #    'HOST': 'localhost',
    #    'PORT': 6379,
    #    'DB': 0,
    # }
}

# ROLLBAR CONFIG
MIDDLEWARE_CLASSES += ('rollbar.contrib.django.middleware.RollbarNotifierMiddleware',)
ROLLBAR = {
    'access_token': os.environ.get('ROLLBAR_ACCESS_TOKEN', ''),
    'environment': os.environ.get("DJANGO_SETTINGS_MODULE", "icmo.settings.dev").split('.').pop(),
    'branch': 'master',
    'root': DJANGO_ROOT,
}
ROLLBAR_PUBLIC_ACCESS_TOKEN = os.environ.get('ROLLBAR_PUBLIC_ACCESS_TOKEN', '')

GOOGLE_ANALYTICS_CODE = ''

# HUBSPOT CONFIG
HUBSPOT_CLIENT_ID = 'e80d3939-7822-11e5-963c-e78f9b100c80'

# DJANGO WEBSOCKET REDIS CONFIG
WEBSOCKET_URL = '/ws/'
WS4REDIS_PREFIX = 'ws4redis'
WS4REDIS_HEARTBEAT = '--heartbeat--'
# TEMPLATE_CONTEXT_PROCESSORS += ('ws4redis.context_processors.default',)

# split the rediscloud/etc urls apart
match = re.match(
    r'^redis://(?:(?P<username>[^:]+):(?P<password>[^@]+)@)?(?P<host>[^:]+):(?P<port>[0-9]+)('
    r'?:/(?P<db>[0-9+]))?$',
    CACHES['default']['LOCATION'])
WS4REDIS_CONNECTION = {
    'host': match.groupdict()['host'],
    'port': match.groupdict()['port'] or 6379,
    'db': match.groupdict()['db'] or 1,
    # 'username': match.groupdict()['username'],  no username accepted!
    'password': match.groupdict()['password'],

}

from django.core.exceptions import PermissionDenied


def get_allowed_channels(request, channels):
    if not request.user.is_authenticated():
        raise PermissionDenied('Not allowed to subscribe nor to publish on the Websocket!')
    return channels


WS4REDIS_ALLOWED_CHANNELS = get_allowed_channels

# SALESFORCE CONFIG
SFDC_CLIENT_ID = os.environ.get('SFDC_CLIENT_ID', '3MVG9uudbyLbNPZPyMTkOL_5eiPEOzcF_do5edkT' \
                                                  '.Y2FSJefqZejDWTKqmDkzYg6Tqg9MJGZdHi2mpvKdTWJs')
SFDC_CLIENT_SECRET = os.environ.get('SFDC_CLIENT_SECRET', '9007782143279615387')
SFDC_REDIRECT_URI = os.environ.get('SFDC_REDIRECT_URI',
                                   'https://localhost:8080/integrations/salesforce/setup/')
SFDC_OAUTH_TOKEN_ENDPOINT = 'https://login.salesforce.com/services/oauth2/token'
SFDC_OAUTH_AUTHORIZE_ENDPOINT = 'https://login.salesforce.com/services/oauth2/authorize'

# BOWER CONFIG
STATICFILES_DIRS += (normpath(join(SITE_ROOT, 'bower_components')),)

# COMPRESSOR CONFIG
STATICFILES_FINDERS = STATICFILES_FINDERS + ('compressor.finders.CompressorFinder',)
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter'
]

# DJANGO EXTENSIONS CONFIG
SHELL_PLUS = "ipython"

# API CACHE
API_CACHE_NAME = 'apicache'  # Cached requests stored here, should be allkeys-lru
API_KEY_CACHE_NAME = 'default'  # Cached keys stored here should not expire the keys!
