import logging

from braces.views import JSONResponseMixin, AnonymousRequiredMixin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import redirect
from django.template.loader import render_to_string
from rest_framework_extensions.mixins import NestedViewSetMixin
from vanilla.views import GenericView
from vanilla import TemplateView

from api.mixins import NestedKwargsMixin
from api.viewsets import IcmoModelViewSet
from billing.forms import SubscriptionChoiceForm
from billing.providers.paypal_rest.helpers import paypal_retrieve_form_data_and_token
from companies.models import Company, CompanyUserInvitation
from companies.notifications import send_invited_user_welcome_email
from core.helpers import validate_email_with_mailgun
from billing.models import SubscriptionPlan, PAYMENT_PROVIDER_STRIPE, PAYMENT_PROVIDER_PAYPAL
from icmo_users.forms import SignupAccountOwnerForm, SignupCompanyForm, \
    SignupBillingContractForm, \
    SignupCouponForm
from icmo_users.helpers import create_user
from icmo_users.models import SignupLead
from core.cbvs import DefaultRateLimitMixin, PublicViewMixin
from core.helpers import generate_random_alphanumeric_string
from icmo_users.models import IcmoUser
from icmo_users.notifications import send_account_activation_postactivation_email
from icmo_users.notifications import send_signup_welcome_postactivation_email
from icmo_users.serializers import IcmoUserSerializer

logger = logging.getLogger(__name__)


class SignupView(PublicViewMixin, AnonymousRequiredMixin, TemplateView):
    template_name = 'icmo_users/signup.html'

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        context.update(dict(
            subscription_plans=SubscriptionPlan.objects.all(),
            subscription_plan_form=SubscriptionChoiceForm(),
            coupon_form=SignupCouponForm(),
            contact_form=SignupAccountOwnerForm(),
            company_form=SignupCompanyForm(prefix='company'),
            contract_form=SignupBillingContractForm(prefix='signature'),
            stripe_public_key=settings.STRIPE_PUBLIC_KEY,
            mailgun_public_key=settings.MAILGUN_PUBLIC_KEY,
            contract_template_name="contracts/contract.v%s.html" %
                                   settings.CURRENT_CONTRACT_VERSION_NUMBER,
        ))
        return context


class CreateAccountView(PublicViewMixin, JSONResponseMixin, TemplateView):
    http_method_names = ['post', 'get']
    template_name = 'icmo_users/signup_success.html'

    def post(self, request):
        # This method is for stripe only
        try:
            user = IcmoUser.objects.get(email=request.POST.get('email'))
        except IcmoUser.DoesNotExist:
            user = None

        if user or request.session.get('signup_success'):
            # This page can display as often as required for users who have
            # completed the sign up process but have not yet had their accounts activated
            return self.render_to_response(dict(already_signed_up=True))

        if not request.POST.get('stripe_token'):
            return self.render_to_response(dict(error="Missing Stripe token"))

        try:
            create_user(request, request.POST, PAYMENT_PROVIDER_STRIPE,
                        request.POST.get('stripe_token'))
        except ValueError as error:
            if settings.DEBUG:
                raise error
            return self.render_to_response(dict(error=error.message))

        request.session['signup_success'] = True
        return self.render_to_response(self.get_context_data())

    def get(self, request, *args, **kwargs):
        # This method is for paypal only or users who have already completed the
        # signup and are awaiting activation
        if not request.GET.get('pp_return'):
            if request.session.get('signup_success'):
                # This page can display as often as required for users who have
                # completed the sign up process but have not yet had their accounts activated
                return self.render_to_response(dict(already_signed_up=True))
            return redirect('signup')

        try:
            form_data, token = paypal_retrieve_form_data_and_token(request)
        except ObjectDoesNotExist:
            messages.error(
                request,
                "Your paypal authorization session has timed out, please try again."
            )
            return redirect('signup')

        try:
            create_user(request, form_data, PAYMENT_PROVIDER_PAYPAL, token)
        except ValueError as error:
            # if settings.DEBUG:
            # raise error
            return self.render_to_response(dict(error=error.message))
        request.session['signup_success'] = True
        return self.render_to_response(self.get_context_data())


class AjaxStoreSignupFormView(PublicViewMixin, JSONResponseMixin, GenericView):
    """
    Records the data from the ongoing signup form in a SignupLead model for
    pursuing abandoned signups.
    The SignupLead record is deleted if the user successfully subscribes.
    """
    http_method_names = ['post']

    def post(self, request):
        if not request.POST.get('email'):
            return self.render_json_response(dict(success=False))

        # Store the email address to the session so we can find this data
        # during for example a paypal authorization webhook
        request.session['signup_email'] = request.POST.get('email')

        # Store some values on the table and the rest in a JSONField
        data = self._prep_values()

        SignupLead.objects.update_or_create(email=data['email'], defaults=data)
        return self.render_json_response(dict(success=True))

    def _prep_values(self):
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'title', 'company_name')
        values = {key.replace('-', '_'): val for key, val in self.request.POST.items() if
                  key != 'csrfmiddlewaretoken' or key[0] == '_'}
        data = {field: values.get(field, '') for field in fields}
        data['fields'] = values
        return data


class AjaxCheckEmailView(PublicViewMixin, JSONResponseMixin, GenericView):
    """Validates the signup email address"""
    http_method_names = ['get']

    def get(self, request):
        valid = True
        user, message = None, None
        email = request.GET.get('email')

        # First we validate with mailgun
        response = validate_email_with_mailgun(email)
        if not response.json()['is_valid']:
            message = "Invalid email address, please check your spelling."
            if response.json()['did_you_mean']:
                message = "%s Did you mean: <b>%s</b>?" % (
                    message, response.json()['did_you_mean'])
            return self.render_json_response(dict(valid=False, message=message))

        # Then we check if it is an existing account
        try:
            user = IcmoUser.objects.get(email=email)
        except IcmoUser.DoesNotExist:
            pass

        if user:
            valid = False
            if user.is_active:
                message = "An account already exists for this email address.  " \
                          "Please <a href='%s'>sign in</a>." % reverse('login')
            else:
                message = render_to_string('icmo_users/includes/awaiting_activation.html')

        return self.render_json_response(dict(valid=valid, message=message))


class ActivateUserView(PublicViewMixin, DefaultRateLimitMixin, TemplateView):
    """Accessed by admins via a tokenized link to activate a new subscriber account"""
    template_name = 'icmo_users/activate_user.html'

    def get(self, request, *args, **kwargs):
        """Require a post from this page before activation to prevent
        certain automated link visitors (email clients, skype, etc) from activating
        this link"""
        return self.render_to_response(
            self.get_context_data(new_user=self.get_new_user(), activate_button=True))

    def post(self, request, *args, **kwargs):
        password = generate_random_alphanumeric_string(20)
        new_user = self.get_new_user()
        if new_user:
            new_user.is_active = True
            new_user.set_password(password)
            # Note: Rather than remove the token this causes a new one to be generated
            # due to the way the UUIDField works
            new_user.activation_token = ''
            new_user.save()
            send_signup_welcome_postactivation_email(request, new_user)
            send_account_activation_postactivation_email(request, new_user,
                                                         password)  # for the admin

        return self.render_to_response(self.get_context_data(new_user=new_user, password=password))

    def get_new_user(self):
        try:
            new_user = IcmoUser.objects.get(is_active=False, activation_token=self.kwargs['token'])
        except IcmoUser.DoesNotExist:
            new_user = None
        return new_user


class ActivateInvitedUserView(PublicViewMixin, DefaultRateLimitMixin, TemplateView):
    """Accessed by invited users via a tokenized link to activate their accounts"""
    template_name = 'icmo_users/activate_invited_user.html'

    def get(self, request, *args, **kwargs):
        """Require a post from this page before activation to prevent
        certain automated link visitors (email clients, skype, etc) from activating
        this link"""
        invited_user = self.get_invited_user()
        invitation = CompanyUserInvitation.objects.filter(user=invited_user).first()
        return self.render_to_response(
            self.get_context_data(invited_user=invited_user, invitation=invitation))

    def post(self, request, *args, **kwargs):
        password = generate_random_alphanumeric_string(20)
        invited_user = self.get_invited_user()
        if invited_user:
            invited_user.set_password(self.request.POST.get('password'))
            invited_user.first_name = request.POST.get('first_name')
            invited_user.last_name = request.POST.get('last_name')
            invited_user.save()
            for invitation in CompanyUserInvitation.objects.filter(user=invited_user):
                invitation.accepted = True
                invitation.save()
            send_invited_user_welcome_email(request, invited_user)

        return self.render_to_response(
            self.get_context_data(invited_user=invited_user, password=password))

    def get_invited_user(self):
        try:
            invited_user = IcmoUser.objects.get(activation_token=self.kwargs['token'])
        except IcmoUser.DoesNotExist:
            invited_user = None
        return invited_user


class IcmoUserViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    lookup_field = 'email'
    lookup_value_regex = '[^/]+'
    queryset = IcmoUser.objects.all()
    serializer_class = IcmoUserSerializer

    def get_queryset(self):
        parents = self.get_parents_query_dict()
        company = Company.objects.get(slug=parents['company__slug'])
        return company.icmouser_set.filter(is_active=True)
