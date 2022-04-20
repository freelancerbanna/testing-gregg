from django.apps import AppConfig


class ResourceConfig(AppConfig):
    name = 'resources'
    verbose_name = "Resources"

    def ready(self):
        from . import signals
