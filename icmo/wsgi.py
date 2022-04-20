import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "icmo.settings.dev")

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

# Whitenoise enables serving of static apps even in production
# warning:  may be slow to start with thousands of staticfiles
application = get_wsgi_application()
application = DjangoWhiteNoise(application)
