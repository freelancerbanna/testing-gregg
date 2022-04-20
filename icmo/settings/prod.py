import dj_database_url

from .common import *

# DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# END DEBUG CONFIGURATION


ALLOWED_HOSTS = ['app.intelligentrevenue.com']

# DATABASE CONFIGURATION FOR HEROKU
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(conn_max_age=500)
}

DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
DATABASES['default'][
    'ATOMIC_REQUESTS'] = False  # If this is true then most period signals wont fire

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# DJANGO SECURITY SETTINGS
MIDDLEWARE_CLASSES = ('djangosecure.middleware.SecurityMiddleware',) + MIDDLEWARE_CLASSES
SECURE_SSL_REDIRECT = True
SECURE_FRAME_DENY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

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
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        "rq.worker": {
            "handlers": ["console"],
            "level": "INFO"
        },
        "icmo": {
            "handlers": ["console"],
            "level": "INFO"
        }
    }
}
# END LOGGING CONFIGURATION


# PAYPAL CONFIG
PAYPAL_MODE = 'live'
ROOT_URL = "https://app.intelligentrevenue.com"

# ANALYTICS
GOOGLE_ANALYTICS_CODE = 'UA-61446740-2'

# DJANGO COMPRESSOR
COMPRESS_ENABLED = True
