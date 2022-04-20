from __future__ import division
from __future__ import print_function

import logging

import django_rq
from django.db import transaction
from django_rq import job
from rq import get_current_job

from budgets.models import BudgetTypes
from core.helpers import QUARTERS, MONTHS_3
from leads.models import ProgramTypes
from periods.helpers import get_search_key, key_in_queue, get_object_key, \
    get_key, split_integer_into_segment_months
from periods.models import Period

logger = logging.getLogger("icmo.%s" % __name__)


# Campaigns have no plans, just actuals.  Variances should be therefore ignored.
# The reason for this is there is no way to know how to split the plans over multiple campaigns

# Programs have plans but no actuals.

# Budget Line Items have both plans and actuals


@job
def update_or_create_month_periods_from_program(program):
    from periods.models import Period
    sample_period = None

    if program.item_type == ProgramTypes.CATEGORY:
        # todo support Categories at some point in the future
        return False

    copied_fields = (
        'touches_per_contact', 'touches_to_mql_conversion', 'contacts_to_mql_conversion',
        'mql_to_sql_conversion', 'sql_to_sale_conversion', 'cost_per_mql', 'cost_per_sql',
        'roi'
    )
    divided_fields = (  # Budget is handled in the associated budget object, not here.
        'sales_revenue', 'sales', 'sql', 'mql', 'contacts', 'touches',
    )

    # Plans are set at an annual level, so to break them down to the month we first
    # get the quarter plan by proportioning them according to the quarterly revenue sales_revenue
    # split from the segment and then divide that by 3 to get the months
    divided_fields_values = dict()
    for field in divided_fields:
        field_value = getattr(program, field)
        if field == 'sales_revenue':
            field_value = field_value.amount
        divided_fields_values[field] = split_integer_into_segment_months(
            field_value, program.segment
        )

    values = dict(average_sale_plan=program.segment.average_sale)
    for idx, month in enumerate(program.company.fiscal_months_by_name):
        for field in copied_fields:
            values["%s_plan" % field] = getattr(program, field)

        for field in divided_fields:
            values["%s_plan" % field] = divided_fields_values[field][idx]
        sample_period, created = Period.objects.update_or_create(defaults=values,
                                                                 program=program, period=month,
                                                                 resolution='program')
    # compute the summary periods
    key = get_object_key(sample_period)
    django_rq.enqueue(check_ready_to_process_summaries,
                      'program', program.id,
                      sample_period.icmo_object_type, sample_period.icmo_object_id,
                      job_id='check_recompute_summaries-%s' % key)
    return True


@job
def update_or_create_month_periods_from_budget_line_item(bli):
    """
    If the budget item is custom create a custom budget line item, if its a program budget,
    update the program period instead.
    :param bli:
    :return:
    """
    from periods.models import Period
    sample_period = None

    if bli.item_type == BudgetTypes.CUSTOM:
        icmo_object_type = 'custom_budget_line_item'
        icmo_object_id = bli.id
        parent_kwargs = {'custom_budget_line_item': bli, 'resolution': 'custom_budget_line_item'}
        copied_fields = ['plan', 'actual']
    elif bli.item_type == BudgetTypes.PROGRAM:
        icmo_object_type = 'program'
        icmo_object_id = bli.program.id
        parent_kwargs = {'program': bli.program, 'resolution': 'program'}
        copied_fields = ['plan', 'actual']
    else:
        # todo support Categories at some point in the future
        return False

    for month in MONTHS_3:
        period_values = dict()
        for field in copied_fields:
            period_values["budget_%s" % field] = getattr(bli, "%s_%s" % (month, field))
        sample_period, created = Period.objects.update_or_create(period=month,
                                                                 defaults=period_values,
                                                                 **parent_kwargs)

    # Compute the summary periods
    key = get_object_key(sample_period)
    django_rq.enqueue(check_ready_to_process_summaries,
                      icmo_object_type, icmo_object_id,
                      sample_period.icmo_object_type, sample_period.icmo_object_id,
                      job_id='check_recompute_summaries-%s' % key)
    return True


@job
def update_or_create_month_periods_from_campaign(campaign):
    from periods.models import Period
    sample_period = None
    copied_fields = (
        'mql', 'sql', 'sales', 'sales_revenue',
        'average_sale',
        'mql_to_sql_conversion',
        'sql_to_sale_conversion',
    )

    for month in MONTHS_3:
        period_values = dict()
        for field in copied_fields:
            period_values["%s_actual" % field] = getattr(campaign, "%s_%s" % (month, field))
        sample_period, created = Period.objects.update_or_create(period=month, period_type='month',
                                                                 resolution='campaign',
                                                                 campaign=campaign,
                                                                 defaults=period_values)

    # compute the summary periods
    key = get_object_key(sample_period)
    django_rq.enqueue(check_ready_to_process_summaries,
                      'campaign', campaign.id,
                      campaign.icmo_parent_level, campaign.icmo_parent_id,
                      job_id='check_recompute_summaries-%s' % key)
    return True


@job
def recompute_summary_periods(icmo_object_type, icmo_object_id, months=None, quarters=None):
    """
    Given a list of month periods, this task will first trigger a save on all affected quarters
    (those quarters that contain the given months) and the year.  Once these items have been
    updated
    this task will then call itself with the same set of month periods for the next level up.
    Ex:  recompute_parents([Campaign Jan]) would trigger saves on Q1 (assuming normal fiscal year)
    and the year.  it would then call recompute_parents([Program Jan]) and so on until it ran out
    parent levels.
    :type icmo_object_type: string representing the
    :type icmo_object_id: int
    :type months: list of affected months
    :type quarters: list of affected quarters

    """
    sample_period = None

    # if not months:
    months = MONTHS_3
    # if not quarters:
    quarters = QUARTERS
    # determine the summary periods to recompute
    summary_periods = quarters
    # The year is always computed, because the quarters have changed
    summary_periods += ('year',)

    # Recompute (by resaving or creating) each affected quarter and the year.
    for summary_period in summary_periods:
        sample_period, created = Period.objects.update_or_create(
            period=summary_period,
            resolution=icmo_object_type,
            **{"%s_id" % icmo_object_type: icmo_object_id}
        )

    # Now queue the icmo parent periods for a recomp.
    if sample_period.icmo_parent_level:
        # Record the affected months
        django_rq.enqueue(check_ready_to_process_parent, sample_period.icmo_parent_level,
                          sample_period.icmo_parent_id)

    return True


@job
def recompute_month_periods(icmo_object_type, icmo_object_id, months=None, quarters=None):
    """
    Given a list of month periods, this task will first trigger a save on all affected quarters
    (those quarters that contain the given months) and the year.  Once these items have been
    updated
    this task will then call itself with the same set of month periods for the next level up.
    Ex:  recompute_parents([Campaign Jan]) would trigger saves on Q1 (assuming normal fiscal year)
    and the year.  it would then call recompute_parents([Program Jan]) and so on until it ran out
    parent levels.
    :type icmo_object_type: string representing the
    :type icmo_object_id: int
    :type months: list of affected months
    :type quarters: list of affected quarters

    """
    from periods.models import Period
    sample_period = None

    if not months:
        months = MONTHS_3
    with transaction.atomic():
        # Recompute (by saving or creating) each affected month.
        parent_kwargs = {"%s_id" % icmo_object_type: icmo_object_id}
        for month in months:
            sample_period, created = Period.objects.update_or_create(
                period=month, resolution=icmo_object_type, **parent_kwargs
            )

    # Now queue the summary periods for a recomp
    # compute the summary periods
    django_rq.enqueue(check_ready_to_process_summaries,
                      icmo_object_type, icmo_object_id,
                      sample_period.icmo_object_type, sample_period.icmo_object_id,
                      job_id='check_recompute_summaries-%s' % get_object_key(sample_period))
    return True


@job
def check_ready_to_process_parent(parent_object_type, parent_id):
    search_key = get_search_key('parent', parent_object_type, parent_id)
    if key_in_queue(search_key, get_current_job().id, django_rq.get_queue()):
        print('not ready yet, other items in queue, skipping')
        return False

    print('ready, lets go higher')

    django_rq.enqueue(
        recompute_month_periods, parent_object_type, parent_id,
        months=None,
        job_id='recompute_month_periods-%s' % search_key
    )


@job
def check_ready_to_process_summaries(icmo_object_type, icmo_object_id,
                                     parent_object_type, parent_id):
    search_key = get_search_key('self', icmo_object_type, icmo_object_id)
    if key_in_queue(search_key, get_current_job().id, django_rq.get_queue()):
        print("%s is still in the queue!" % search_key)
        print('not ready yet, other items in queue, skipping')
        return False

    print('ready, lets do summaries')

    job_key = get_key(icmo_object_type, icmo_object_id, parent_object_type, parent_id)
    django_rq.enqueue(
        recompute_summary_periods, icmo_object_type, icmo_object_id,
        months=None,
        job_id='recompute_summaries-%s' % job_key
    )
