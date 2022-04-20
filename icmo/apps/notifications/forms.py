from django.forms import ModelForm

from core.forms import BootstrapFormMixin, IncompleteModelFormMixin
from .models import CompanyUserNotificationSubscription


class CompanyUserNotificationSubscriptionForm(BootstrapFormMixin, IncompleteModelFormMixin,
                                              ModelForm):
    class Meta:
        model = CompanyUserNotificationSubscription
        exclude = ('company', 'company_user', 'params', 'params_display')

