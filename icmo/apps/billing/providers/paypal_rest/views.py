from urlparse import urljoin, urlsplit

from braces.views import JSONResponseMixin, CsrfExemptMixin, JsonRequestResponseMixin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from vanilla.views import GenericView, TemplateView

from billing.forms import CouponForm
from billing.models import SubscriptionPlan
from billing.providers.paypal_rest.handlers import PaypalSubscription
from billing.providers.paypal_rest.helpers import verify_webhook_request
from billing.providers.paypal_rest.models import AwaitingPaypalAuthorization, PaypalNotification
from billing.views import logger
from core.cbvs import DefaultRateLimitMixin, PublicViewMixin


class AjaxGetPaypalAuthURLView(PublicViewMixin, DefaultRateLimitMixin, JSONResponseMixin, GenericView):
    """
    Retreives a paypal auth url, stores your form data, and will route back to your
    target_url on success, passing the auth token and a uuid which can be used to
    retrieve the form data.
    Get Params:  target_url:  the url to receive the authorization
                 source_url:  the url to return to in the case of failure
                 plan_slug:  the slug of the plan to subscribe to
    Responds:    error:  error message
                 paypal_auth_url:  the auth url to send the user to
    """

    def post(self, request):
        target_url = request.GET.get('target_url')
        source_url = request.GET.get('source_url')
        plan_slug = request.GET.get('plan_slug')
        form_data = request.POST

        if not all([target_url, source_url, plan_slug, form_data]):
            return self.render_json_response({'error': 'incomplete_request'})
        try:
            subscription_plan = SubscriptionPlan.objects.get(slug=plan_slug)
        except SubscriptionPlan.DoesNotExist:
            return self.render_json_response({'error': 'invalid_plan_slug'})

        icmo_coupon_id = None
        coupon_form = CouponForm(request.POST)
        if not coupon_form.is_valid():
            return self.render_json_response({'error': 'invalid_coupon'})
        if coupon_form.coupon:
            icmo_coupon_id = coupon_form.coupon.id

        data = AwaitingPaypalAuthorization.objects.create(form_data=form_data)
        request.session['paypal'] = dict(
            source_url=urlsplit(source_url).path,  # ensure these are just paths
            target_url=urlsplit(target_url).path,
            data_uuid=data.uuid,
        )
        auth_url = PaypalSubscription.paypal_create_subscription_agreement(
            subscription_plan.id,
            subscription_plan.name,
            urlsplit(source_url).path,
            icmo_coupon_id=icmo_coupon_id
        )
        return self.render_json_response({'paypal_auth_url': auth_url})


class PaypalAuthorizedView(PublicViewMixin, GenericView):
    """
    Receives the paypal authorization return and routes it on to its destination if possible
    """
    def get(self, request):
        token = request.GET.get('token')
        paypal_auth_request = request.session.get('paypal', {})
        target_url = paypal_auth_request.get('target_url')
        source_url = paypal_auth_request.get('source_url')
        data_uuid = paypal_auth_request.get('data_uuid')

        if not all([token, target_url, source_url, data_uuid]):
            messages.warning(
                request,
                "Your paypal authorization session has timed out, please try again."
            )
            if not source_url:
                source_url = reverse('signup')
            return redirect(source_url)
        request.session['paypal']['token'] = token
        request.session.modified = True
        return HttpResponseRedirect(urljoin(target_url, "?pp_return=1"))


class PaypalWebhookView(PublicViewMixin, CsrfExemptMixin, JsonRequestResponseMixin, GenericView):
    http_method_names = ['post']
    require_json = True

    def post(self, request):
        if not verify_webhook_request(request):
            logger.warning("Paypal webhook failed verification.")
            return HttpResponse(status=403)
        PaypalNotification.create_from_webhook(self.request_json)

        return HttpResponse(status=200)


class SubscriptionCanceledView(TemplateView):
    template_name = 'billing/subscription_canceled.html'
