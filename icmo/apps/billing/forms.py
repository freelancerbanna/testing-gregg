from crispy_forms.layout import Field, Layout
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext as _
from localflavor.ca.ca_provinces import PROVINCE_CHOICES
from localflavor.us.us_states import STATE_CHOICES

from .models import BillingContract, SubscriptionPlan, Coupon
from core.forms import BootstrapFormMixin, IncompleteModelFormMixin
from icmo_users.models import IcmoUser

STATE_AND_PROVINCE_CHOICES = list(STATE_CHOICES) + list(PROVINCE_CHOICES)
SORTED_STATE_AND_PROVINCE = sorted(STATE_AND_PROVINCE_CHOICES, key=lambda x: x[1])
COUNTRY_CHOICES = [
    ('USA', 'United States'),
    ('CA', 'Canada')
]

MIN_PASSWORD_LENGTH = 8


class RemoveUserForm(forms.Form):
    uid = forms.CharField(widget=forms.HiddenInput())


class AccountOwnerEditForm(forms.ModelForm):
    class Meta:
        model = IcmoUser
        fields = ['email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data['email']
        if IcmoUser.objects.filter(email=email) \
                .exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("This email already used"))
        return email


class BillingContractForm(BootstrapFormMixin, IncompleteModelFormMixin, forms.ModelForm):
    class Meta:
        model = BillingContract
        fields = ['name', 'title', 'signature_json', 'signature_uri_b64']

    display_date = forms.DateField(required=False)

    def __init__(self, *args, **kwargs):
        super(BillingContractForm, self).__init__(*args, **kwargs)
        if self.data:
            date = self.data.get('date')
        else:
            date = timezone.now().strftime("%Y-%m-%d")
        self.helper.layout = Layout(
            Field('name', data_phoenix_exclude="true", css_class="sigName",
                  data_fv_field="signature-name"),
            Field('title'),
            Field('display_date', data_phoenix_exclude="true", disabled="true",
                  value=date),
            Field('signature_json', type="hidden", css_class='sigOutput',
                  data_phoenix_exclude="true", template='contracts/sigpad_widget_%s.html'),
            Field('signature_uri_b64', type="hidden")
        )
        self.fields['signature_json'].label = "Signature"
        self.fields['display_date'].label = "Date"
        self.fields['signature_json'].help_text = "Sign the contract on the grey line " \
                                                  "using your mouse."


class SubscriptionChoiceForm(forms.Form):
    error_messages = {
        'plan_not_found': _("Could not find a plan by that id.")
    }
    subscription_plan = None
    plan = forms.CharField(widget=forms.HiddenInput)

    def clean_plan(self):
        plan = self.cleaned_data['plan']
        try:
            self.subscription_plan = SubscriptionPlan.objects.get(slug=plan)
        except SubscriptionPlan.DoesNotExist:
            raise forms.ValidationError(
                self.error_messages['plan_not_found'],
                code='plan_not_found',
            )
        return plan


class CouponForm(BootstrapFormMixin, forms.Form):
    error_messages = {
        'invalid_code': _("Invalid code."),
        'expired': _("Code has expired.")
    }
    coupon = None
    code = forms.CharField(
        required=False, max_length=25,
        widget=forms.TextInput(
            attrs={
                'data-fv-remote': 'true',
                'data-fv-remote-url': reverse_lazy("billing:ajax_check_code"),
                'data-fv-remote-message': "%s",
                'data-fv-remote-delay': '500',
                'class': 'form-control'
            }
        )
    )

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code:
            return code
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise forms.ValidationError(
                self.error_messages['invalid_code'],
                code='invalid_code'
            )
        if coupon.is_valid():
            raise forms.ValidationError(
                self.error_messages['expired'],
                code='expired'
            )
        self.coupon = coupon
        return code
