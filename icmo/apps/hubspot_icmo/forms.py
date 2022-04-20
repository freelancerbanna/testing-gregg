from django import forms

from core.forms import BootstrapFormMixin
from .models import HubspotConnection


class HubSpotConnectionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = HubspotConnection
        fields = ['hub_id']

    icmo_crispy_submit_name = 'Connect to HubSpot'
