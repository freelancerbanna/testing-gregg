import os
from django.conf import settings
from django.utils import timezone

from core.helpers import MONTHS_3, QUARTERS, ALL_TIME_PERIODS, FISCAL_YEAR


def add_company_plan(request):
    if not request.user.is_authenticated():
        return {}
    return {'selected_company': request.selected_company,
            'selected_plan': request.selected_plan,
            'company_user': request.company_user}


def add_time_periods(request):
    time_periods = dict(
        time_periods_months=MONTHS_3,
        time_periods_quarters=QUARTERS,
        time_periods_all_time_periods=ALL_TIME_PERIODS,
        time_periods_current_month=MONTHS_3[timezone.now().month - 1],
        time_periods_current_year=timezone.now().year,
    )
    if hasattr(request, 'selected_company') and request.selected_company:
        fiscal_periods = tuple(request.selected_company.fiscal_months_by_name)
        time_periods['time_periods_months'] = fiscal_periods
        time_periods['time_periods_all_time_periods'] = fiscal_periods + QUARTERS + FISCAL_YEAR
    return time_periods


def add_environment(request):
    return {
        'ENVIRONMENT': os.environ.get("DJANGO_SETTINGS_MODULE", "icmo.settings.dev").split(
            '.').pop()
    }


def add_js_settings(request):
    return {
        'ROLLBAR_PUBLIC_ACCESS_TOKEN': settings.ROLLBAR_PUBLIC_ACCESS_TOKEN,
        'DEBUG': settings.DEBUG,
        'GOOGLE_ANALYTICS_CODE': settings.GOOGLE_ANALYTICS_CODE
    }
