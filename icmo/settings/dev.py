import logging
import os
import sys

from .common import *

DEBUG = True

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    "default": {
        # don't use pooled in development as it hides errors
        "ENGINE": 'django.db.backends.postgresql',
        "NAME": "icmo_dev",
        "USER": "icmo_dev",
        "PASSWORD": "icmo_dev",
        "HOST": "localhost",
        "PORT": "",
    },
    #	'salesforce': {
    #		'ENGINE': 'salesforce.backend',
    #		"CONSUMER_KEY" :
    # '3MVG9JZ_r.QzrS7gCkpSn70wvfL9rbfMYi6ZtJaBEvXZlP9VTarJTXkc5XHMk12IZjCAnpYtbpX9bz27JnxPg',
    #		"CONSUMER_SECRET" : '7389110888323623292',
    #		'USER': 'matthew@ragingbits.com',
    #		'PASSWORD': 'Con4mity!',
    #		'HOST': 'https://na10.salesforce.com',
    #	}
}
DATABASES['default']['ATOMIC_REQUESTS'] = False
# CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#    }
# }
## when caches are disabled using the setting above, we should revert to a regular session engine
# SESSION_ENGINE = 'django.contrib.sessions.backends.db'

LOGGING['loggers'] = {
    'django': {
        'handlers': ['console'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
    },
    'icmo': {
        'handlers': ['console'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
    },
}
# WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
# WSGI_APPLICATION = 'ws4redis.django_runserver.application'
WSGI_APPLICATION = 'wsgi.application'
# END WSGI CONFIGURATION

# DEBUG TOOLBAR CONFIG
INTERNAL_IPS = ('10.0.2.2', '127.0.0.1')
DEBUG_TOOLBAR_PATCH_SETTINGS = False

INSTALLED_APPS += ('debug_toolbar', 'template_profiler_panel')
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'template_profiler_panel.panels.template.TemplateProfilerPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'ddt_request_history.panels.request_history.RequestHistoryPanel',
]
DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
    'SHOW_TOOLBAR_CALLBACK': 'ddt_request_history.panels.request_history.allow_ajax',
}
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# ICMO CONFIG
ROOT_URL = "https://icmo-local-hd6by.ngrok.io"

# WHITENOISE CONFIG
WHITENOISE_AUTOREFRESH = True

# DJANGO CRISPY FORMS CONFIG
CRISPY_FAIL_SILENTLY = False

# PAYPAL REST SDK CONFIG
PAYPAL_MODE = 'sandbox'
PAYPAL_OPENID_REDIRECT_URI = "https://icmo-local-hd6by.ngrok.io/billing/paypal_return/"
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID',
                                  'AQLKRHmXnN2OuvvntuOdUmoAYqs5WtLf02f9H1HP0z3PsECLYYe5o2bmXUR1MGx5FrqPyih_pHHaSG8H')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_ID',
                                      'EIfx0OwIefvT3PunM_1iX5df2zx7TW2k_X1rZ2MaumWL0dxP_MLMRn7qzLebNwXxkZxnO6X2NzKanP7H')
PAYPAL_WEBHOOK_ID = os.environ.get('PAYPAL_WEBHOOK_ID',
                                   '11302666V8919402T')  # Also 'WEBHOOK_ID' for sandbox tests


# Disable old_migrations during testing
# https://stackoverflow.com/questions/25161425/disable-old_migrations-when-running-unit-tests-in
# -django-1-7
class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


ACTIVATION_TEAM_EMAIL = "cordery@gmail.com"

TESTS_IN_PROGRESS = False
if 'test' in sys.argv[1:] or 'jenkins' in sys.argv[1:]:
    logging.disable(logging.CRITICAL)
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )
    DEBUG = False
    TESTS_IN_PROGRESS = True
    MIGRATION_MODULES = DisableMigrations()

SUPPORT_EMAIL = "cordery@gmail.com"

# CLOUDINARY DEV CONFIG
import cloudinary

cloudinary.config(
    cloud_name="hwuwmbjeo",
    api_key="883689794681668",
    api_secret="0bF1iYiQbP8dT4n2A8XpTeRu3YI"
)

# SSL DEBUG SERVER
INSTALLED_APPS += ('sslserver',)

# Compressor
COMPRESS_ENABLED = False
