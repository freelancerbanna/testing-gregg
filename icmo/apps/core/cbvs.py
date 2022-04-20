from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from ratelimit.mixins import RatelimitMixin
from stronghold.decorators import public

from companies.models import Company
from revenues.models import RevenuePlan


class PublicViewMixin(object):
    @method_decorator(public)
    def dispatch(self, *args, **kwargs):
        return super(PublicViewMixin, self).dispatch(*args, **kwargs)


class ItemRequiredMixin(object):
    item_required = None
    company = None
    plan = None

    def dispatch(self, request, *args, **kwargs):
        if self.item_required not in (Company, RevenuePlan):
            raise ValueError("Unrecognized item_required %s" % self.item_required)
        if self.item_required in (Company, RevenuePlan) and not request.selected_company:
            request.selected_company = None
            return HttpResponseRedirect(reverse('start_redirect'))
        elif self.item_required is RevenuePlan and not request.selected_plan:
            messages.info(request, "Please select a revenue plan first.")
            request.selected_plan = None
            return HttpResponseRedirect(reverse('revenue_plans_list', kwargs=dict(
                company_slug=request.selected_company.slug)))
        return super(ItemRequiredMixin, self).dispatch(request, *args, **kwargs)


class DefaultRateLimitMixin(RatelimitMixin):
    ratelimit_key = 'ip'
    ratelimit_rate = '10/m'
    ratelimit_block = True


class AppMixin(ItemRequiredMixin):
    item_required = RevenuePlan
    app_name = None

    def dispatch(self, request, *args, **kwargs):
        # Check the users VIEW permissions for this app
        if not request.company_user or not request.company_user.can_view(self.app_name):
            return HttpResponseRedirect(reverse('permission_denied'))
        return super(AppMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(AppMixin, self).get_context_data(**kwargs)
        context_data.update(dict(
            app_name=self.app_name,
            show_summary=not self.request.company_user.is_segment_restricted,
            can_change=self.request.company_user.can_change(self.app_name),
        ))
        if self.item_required == RevenuePlan:
            context_data.update(dict(
                segments=self.request.company_user.get_permitted_plan_segments(
                    self.request.selected_plan),
                api_url=reverse('company-plans-segments-list', kwargs=dict(
                    parent_lookup_company__slug=self.request.selected_company.slug,
                    parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
            ))
        return context_data


class HidePlanBarMixin(object):
    def get_context_data(self, **kwargs):
        context = super(HidePlanBarMixin, self).get_context_data(**kwargs)
        context.update(dict(
            hide_plan_bar=True
        ))
        return context
