from django.apps import AppConfig


class SalesforceICMOConfig(AppConfig):
    name = 'salesforce_icmo'
    verbose_name = "Salesforce ICMO Integration"

    def ready(self):
        from . import signals
