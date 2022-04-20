import base64
from urlparse import urlparse

from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse, resolve, Resolver404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.views.generic import RedirectView, TemplateView
from vanilla import GenericView

from core.cbvs import HidePlanBarMixin
from core.helpers import reverse_strip_empty_kwargs


class LoginRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False
    """
    Redirect the user to a single company view or the company chooser (if they
    have multiple companies).
    """

    def get_redirect_url(self, *args, **kwargs):
        company = self.get_company()
        if self.request.user.last_revenue_plan and self.request.user.last_revenue_plan.is_active:
            return reverse('start', kwargs=dict(
                company_slug=self.request.user.last_revenue_plan.company.slug,
                plan_slug=self.request.user.last_revenue_plan.slug))
        if company and company.is_active:
            return reverse('start', kwargs=dict(company_slug=company.slug))
        messages.info(self.request, "Please select a company to get started.")
        return reverse('companies_list')

    def get_company(self):
        company = None
        user = self.request.user
        if user.last_revenue_plan:
            company = user.last_revenue_plan.company
        elif user.is_account_owner:
            if user.companies.count() == 1:
                company = user.companies.first()
        elif user.permissions.count() == 1:
            company = user.permissions.first().company
        return company


class SwitchPlanRedirectView(RedirectView):
    permanent = False
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        referring_path = urlparse(request.META.get('HTTP_REFERER', ''))[2]
        try:
            match = resolve(referring_path)
        except Resolver404:
            raise Http404

        match.kwargs['plan_slug'] = request.GET.get('plan')
        return HttpResponseRedirect(
            reverse_strip_empty_kwargs(match.url_name, args=match.args, kwargs=match.kwargs))


class SwitchCompanyRedirectView(RedirectView):
    permanent = False
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        referring_path = urlparse(request.META.get('HTTP_REFERER', ''))[2]
        try:
            match = resolve(referring_path)
        except Resolver404:
            raise Http404

        match.kwargs['company_slug'] = request.GET.get('company')
        return HttpResponseRedirect(
            reverse_strip_empty_kwargs(match.url_name, args=match.args, kwargs=match.kwargs))


class PermissionDeniedView(HidePlanBarMixin, TemplateView):
    template_name = 'errors/permission_denied.html'


class NoPublishedPlanView(HidePlanBarMixin, TemplateView):
    template_name = 'errors/no_published_plan.html'


class KendoProxyView(GenericView):
    def post(self, request):
        filename = request.POST.get('fileName')
        content_type = request.POST.get('contentType')
        encoded_data = request.POST.get('base64')

        if not filename and content_type and encoded_data:
            return HttpResponse(status=403)

        try:
            data = base64.b64decode(encoded_data)
        except TypeError:
            return HttpResponse(status=403)

        response = HttpResponse(content=data, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        response['Content-Length'] = len(data)
        return response
