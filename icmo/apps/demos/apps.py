from django.apps import AppConfig


class DemosConfig(AppConfig):
    name = 'demos'
    verbose_name = "Demos"

    def ready(self):
        from . import signals
