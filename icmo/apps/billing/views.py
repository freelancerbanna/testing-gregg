import logging

from braces.views import JSONResponseMixin
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from vanilla import DetailView
from vanilla.views import GenericView

from core.cbvs import DefaultRateLimitMixin, PublicViewMixin
from core.helpers import generate_pdf
from .forms import CouponForm
from .models import SubscriptionPlan, Coupon, BillingContract

logger = logging.getLogger(__name__)


class AjaxCheckCouponView(PublicViewMixin, JSONResponseMixin, DefaultRateLimitMixin, GenericView):
    http_method_names = ['get']

    def get(self, request):
        form = CouponForm(request.GET)
        if form.is_valid():
            return self.render_json_response(dict(
                valid=True,
                success_message="%s code accepted.  %s" % (
                    form.coupon.code, form.coupon.short_description)
            ))
        return self.render_json_response(dict(
            valid=False,
            message=str(form.errors['code'][0])
        ))


class AjaxUpdatePaymentSummaryView(PublicViewMixin, JSONResponseMixin, DefaultRateLimitMixin,
                                   GenericView):
    http_method_names = ['get']

    def get(self, request):
        plan = get_object_or_404(SubscriptionPlan, slug=request.GET.get('plan'))

        context = dict(
            plan_name=plan.name,
            plan_interval=plan.human_interval,
            plan_subfee=plan.amount,
            plan_setupfee=plan.setup_fee_amount,
            plan_subfee_coupon_applied=False,
            plan_setupfee_coupon_applied=False
        )
        try:
            coupon = Coupon.objects.get(code=request.GET.get('code'))
        except Coupon.DoesNotExist:
            coupon = None
        if coupon:
            context.update(dict(
                plan_subfee=coupon.get_applied_recurring_discount_description(plan.amount),
                plan_setupfee=coupon.get_applied_setup_fee_discount_description(plan.amount),
                plan_subfee_coupon_applied=coupon.has_pricetype_discount('recurring'),
                plan_setupfee_coupon_applied=coupon.has_pricetype_discount('setup_fee')
            ))
        return self.render_json_response(context)


class ContractView(DetailView):  # todo secure this view
    model = BillingContract
    lookup_field = 'slug'
    template_name = 'contracts/pdf_contract.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        with open(settings.COUNTERSIGNATURE_B64_URI_FILE) as fp:
            countersignature_uri = fp.read()
        context = self.get_context_data(countersignature_uri=countersignature_uri)
        if request.GET.get('pdf'):
            return HttpResponse(content=generate_pdf(self.template_name, context),
                                content_type='application/pdf')
        return self.render_to_response(context)
