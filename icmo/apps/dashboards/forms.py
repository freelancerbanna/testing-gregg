from django import forms
from django.utils.translation import ugettext as _
from core.forms import DASHBOARD_CHOICES

class DashboardNavigationForm(forms.Form):
    dashboard = forms.ChoiceField(
        label=_('Select a Dashboard View'),
        choices=DASHBOARD_CHOICES,
        required=False,
    )