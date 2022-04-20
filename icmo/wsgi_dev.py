import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "icmo.settings.dev")

# We don't use whitenoise during dev because thousands of static files
# makes for a slow startup time, not ideal for seeing quick changes.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()