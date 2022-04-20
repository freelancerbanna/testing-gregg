from crispy_forms.layout import Layout, Field
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
import re

from billing.forms import BillingContractForm, CouponForm
from companies.forms import CompanyForm
from core.forms import BootstrapFormMixin
from core.widgets import PhoneInput
from .models import IcmoUser

MIN_PASSWORD_LENGTH = 8


class IcmoLoginForm(BootstrapFormMixin, AuthenticationForm):
    icmo_crispy_submit_name = 'Sign In'
    remember_me = forms.BooleanField(label=_('Remember Me'),
                                     required=False)


class IcmoPasswordResetForm(BootstrapFormMixin, PasswordResetForm):
    icmo_crispy_submit_name = "Reset Password"


class IcmoSetPasswordForm(BootstrapFormMixin, SetPasswordForm):
    icmo_crispy_submit_name = "Reset Password"


class ReferAFriendForm(forms.Form):
    refer_a_friend = forms.CharField(widget=forms.HiddenInput(),
                                     initial="whythehellnot")
    email = forms.CharField(label=_('Emails'), max_length=512)
    message = forms.CharField(label=_('Message'), widget=forms.Textarea,
                              required=False)


class SendASuggestionForm(BootstrapFormMixin, forms.Form):
    icmo_crispy_submit_name = 'Send'
    message = forms.CharField(label='Message', widget=forms.Textarea,
                              required=True)


class IcmoUserForm(BootstrapFormMixin, forms.ModelForm):
    icmo_crispy_submit_name = 'Save'

    class Meta:
        model = IcmoUser
        fields = ('first_name', 'last_name', 'email',
                  'phone_number', 'title', 'company', 'timezone')


class SignupAccountOwnerForm(BootstrapFormMixin, forms.Form):
    icmo_crispy_disable_form_tag = True

    error_messages = {
        'duplicate_email': _(
            "A user with that email address already exists, please log in or reset your password "
            "if you have forgotten it."),
        'password_mismatch': _("The two password fields didn't match."),
        'invalid_phone_number': _("Invalid US/CA phone number.")
    }

    email = forms.EmailField(required=True)
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone_number = forms.CharField(widget=PhoneInput)
    title = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(SignupAccountOwnerForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('email', data_fv_remote='true',
                  data_fv_remote_url=reverse("ajax_signup_check_email"),
                  data_fv_remote_message="%s", data_fv_remote_delay='500'),
            'first_name',
            'last_name',
            'phone_number',
            'title'
        )

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not re.match(r'^(?:\+1|1-)?[\-\(\)\[\]\s]*(?:\d[\-\(\)\[\]\s]*){10}$', phone_number):
            raise forms.ValidationError(
                self.error_messages['invalid_phone_number'],
                code='invalid_phone_number'
            )
        phone_number = re.sub(r'[^\d]+', '', phone_number)
        if len(phone_number) == 11 and phone_number[0] == 1:
            phone_number = phone_number[1:]
        return phone_number

    def clean_email(self):
        email = self.cleaned_data['email']
        if IcmoUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                self.error_messages['duplicate_email'],
                code='duplicate_email',
            )
        return email

    def create_user(self):
        data = self.cleaned_data
        return IcmoUser.objects.create_user(
            data['email'],
            IcmoUser.objects.make_random_password(),
            is_active=False,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone_number'],
            title=data['title']
        )


class SignupCompanyForm(CompanyForm):
    icmo_crispy_disable_form_tag = True


class SignupBillingContractForm(BillingContractForm):
    icmo_crispy_disable_form_tag = True


class SignupCouponForm(CouponForm):
    icmo_crispy_disable_form_tag = True


class PasswordUpdateForm(forms.Form):
    password = forms.CharField(label=_('Existing Password'),
                               widget=forms.PasswordInput)
    new_password = forms.CharField(label=_('New Password'),
                                   widget=forms.PasswordInput)
    confirm_password = forms.CharField(label=_('Confirm New Password'),
                                       widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(PasswordUpdateForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        if self.instance and not self.instance.check_password(password):
            # Never send password data back to the browser.
            self.cleaned_data['password'] = ''
            raise forms.ValidationError(_("Existing password is incorrect"))
        return password

    def clean_new_password(self):
        password = self.cleaned_data['new_password']
        if len(password) < MIN_PASSWORD_LENGTH:
            raise forms.ValidationError(_("The password must be at least ") + \
                                        str(MIN_PASSWORD_LENGTH) + _(" characters long."))

        # At least one letter and one non-letter
        first_isalpha = password[0].isalpha()
        if all(c.isalpha() == first_isalpha for c in password):
            raise forms.ValidationError(_("The new password must contain at " \
                                          "least one letter and at least one " \
                                          "digit or punctuation character."))
        return password

    def clean_confirm_password(self):
        try:
            new_password = self.cleaned_data['new_password']
        except:
            new_password = None
        confirm_password = self.cleaned_data['confirm_password']

        if new_password and confirm_password != new_password:
            # Never send password data back to the browser.
            self.cleaned_data['confirm_password'] = ''
            self.cleaned_data['new_password'] = ''
            raise forms.ValidationError(_("Passwords don't match"))
        return confirm_password
