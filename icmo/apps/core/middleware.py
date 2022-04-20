from __future__ import print_function

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from companies.models import Company, CompanyUser, NoLivePlanException
from revenues.models import RevenuePlan

logger = logging.getLogger('icmo.%s' % __name__)


class AddCompanyPlanMiddleware(object):
    """
    Add the company and plan to the request if they are in the
    view kwargs.  Works with both the web and rest interfaces.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated():
            return None
        request.selected_company = None
        request.selected_plan = None
        company_slug = None
        plan_slug = None
        for key, val in view_kwargs.items():
            if key == 'company_slug' or key.endswith('company__slug'):
                company_slug = val
            elif key == 'plan_slug' or key.endswith('revenue_plan__slug'):
                plan_slug = val

        if company_slug:
            try:
                request.selected_company = Company.objects.get(slug=company_slug)
            except Company.DoesNotExist:
                return HttpResponseRedirect(reverse('companies'))

            if plan_slug:
                try:
                    request.selected_plan = RevenuePlan.objects.get(
                        company=request.selected_company, slug=plan_slug)
                except RevenuePlan.DoesNotExist:
                    return HttpResponseRedirect(reverse('revenue_plans', kwargs=dict(
                        company_slug=request.selected_company.slug)))
                # Save the selected company to the user
                if request.selected_plan.pk != request.user.last_revenue_plan_id:
                    request.user.last_revenue_plan_id = request.selected_plan.id
                    request.user.save()
        elif request.user.is_authenticated() and request.user.owned_companies.count() == 1:
            request.selected_company = request.user.owned_companies.first()
        return None


class AddCompanyUserMiddleware(object):
    """
    Add the company_user to the request and bounce if the user does
    not have access to this company.  Between this and the BouncerMiddleware
    below all company, revenue_plan, and segment access restriction is
    implemented for both the web and rest interfaces.

    Note: Must come after AddCompanyPlanMiddleware
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.company_user = None
        if request.user.is_authenticated() and request.selected_company:
            try:
                request.company_user = CompanyUser.objects.select_related().get(
                    company=request.selected_company,
                    user=request.user)
            except ObjectDoesNotExist:
                logger.debug(
                    'User %s was blocked because no CompanyUser could be found for '
                    'company `%s`' % (request.user, request.selected_company.slug))
                return HttpResponseRedirect(reverse('permission_denied'))
        return None


class PlanBouncerMiddleware(object):
    """
    Check the selected_plan and any segment_slug for access

    Note: Must come after AddCompanyPlanMiddleware
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.company_user:
            if request.selected_plan:
                try:
                    if request.selected_plan.slug not in \
                            request.company_user.permitted_revenue_plans_slugs:
                        logger.debug(
                            'User %s was blocked from accessing a plan other than the live plan'
                            % request.user)
                        return HttpResponseRedirect(reverse('permission_denied'))
                except NoLivePlanException:
                    logger.debug(
                        'User %s was blocked because there is no active plan `%s`' % request.user)
                    return HttpResponseRedirect(reverse('no_published_plan'))
