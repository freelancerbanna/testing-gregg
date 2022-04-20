from django.apps import AppConfig


class PeriodConfig(AppConfig):
    name = 'periods'
    verbose_name = "Periods"

    def ready(self):
        from . import signals
