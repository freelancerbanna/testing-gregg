import logging

import django_rq
from django.db.models import Model
from django_redis import get_redis_connection

from budgets.models import BudgetTypes
from core.helpers import QUARTERS
from leads.models import ProgramTypes
from periods.models import Period

logger = logging.getLogger("icmo.%s" % __name__)


def unique_enqueue(*args, **kwargs):
    default_q = django_rq.get_queue()
    job_id = kwargs.get('job_id')
    if job_id and job_id in default_q.job_ids:
        logger.warning(" REPEAT JOB_ID %s, SKIPPING" % job_id)
        return False
    django_rq.enqueue(*args, **kwargs)


def periodunique(task, instance):
    key = get_object_key(instance)

    return unique_enqueue(task, instance, job_id='%s-%s' % (str(task), key))


def get_job_id(*args, **kwargs):
    job_id_bits = []
    for arg in args:
        job_id_bits.append(get_arg_str(arg))

    for key, val in kwargs.items():
        job_id_bits.append("%s{@}%s" % (key, get_arg_str(val)))
    return "{@}".join(job_id_bits)


def get_arg_str(arg):
    if isinstance(arg, Model):
        return "%s-%s" % (arg.__class__.__name__, arg.pk)
    return str(arg)


def recompute_periods(revenue_plan):
    Period.objects.filter(revenue_plan=revenue_plan).delete()
    for segment in revenue_plan.segments.filter(is_active=True):
        recompute_segment_periods(segment)
    return True


def recompute_segment_periods(segment):
    from periods import tasks
    Period.objects.filter(segment=segment).delete()
    for c in segment.campaign_set.filter(program__is_active=True, is_active=True):
        periodunique(tasks.update_or_create_month_periods_from_campaign, c)
    for p in segment.programs.filter(is_active=True).exclude(item_type=ProgramTypes.CATEGORY):
        periodunique(tasks.update_or_create_month_periods_from_program, p)
    for b in segment.budgets.exclude(item_type=BudgetTypes.CATEGORY):
        django_rq.enqueue(tasks.update_or_create_month_periods_from_budget_line_item, b)
    return True


def recompute_segments_and_up(revenue_plan):
    from periods import tasks
    for segment in revenue_plan.segments.filter(is_active=True):
        tasks.recompute_month_periods.delay('segment', segment.id)


def get_search_key(key_type, object_type, object_id):
    return "[%s:%s-%s]" % (key_type, object_type, object_id)


def get_object_key(obj):
    return get_key(obj.icmo_object_type, obj.icmo_object_id, obj.icmo_parent_level,
                   obj.icmo_parent_id)


def get_key(obj_type, obj_id, parent_type, parent_id):
    obj_key = "[self:%s-%s]" % (obj_type, obj_id)
    if parent_type:
        parent_key = "[parent:%s-%s]" % (parent_type, parent_id)
    else:
        parent_key = "[parent:NoParent-NoParent]"
    return "%s%s" % (obj_key, parent_key)


def get_all_active_job_ids(queue):
    con = get_redis_connection("default")
    queued_jobs = con.lrange("%s%s" % (queue.redis_queue_namespace_prefix, queue.name), 0, -1)
    wip_jobs = con.zrange('rq:wip:%s' % queue.name, 0, -1)
    return queued_jobs + wip_jobs


def key_in_queue(search_key, my_key, queue):
    return [job_id for job_id in get_all_active_job_ids(django_rq.get_queue())
            if search_key in job_id and job_id != my_key]


def record_period_months(key, months):
    con = get_redis_connection("default")
    con.sadd('icmo:periods:%s' % key, *months)
    return True


def get_period_months(key):
    con = get_redis_connection("default")
    members = con.smembers('icmo:periods:%s' % key)
    con.delete('icmo:periods:%s' % key)
    return members


# split integers by quarter percents into month thirds
def split_integer_into_segment_months(number, segment, by_quarter=False):
    proportions = [segment.get_quarter_goal_percent_of_annual(quarter) for quarter in QUARTERS]
    quarter_amounts = proportion_integer_into_list_of_integers(number, proportions)
    values = [divide_integer_into_list_of_integers(x, 3) for x in quarter_amounts]
    if by_quarter:
        return values
    return [x for sublist in values for x in sublist]


def divide_integer_into_list_of_integers(number, divisor):
    """
    Divides an integer into a list of integers divisor long.
    Adds remainders to the list starting from the end.
    Ex:  divide_integer_into_list_of_integers(3, 4) = [0,1,1,1]
    :param number: the integer to divide
    :param divisor: the number of items to split the integer into
    :return: list of integers
    """
    split = [int(number / divisor) for x in range(0, divisor)]
    remainder = number % divisor
    if remainder > 0:
        for x in range(1, remainder + 1):
            split[-x] += 1
    return split


def proportion_integer_into_list_of_integers(number, proportions):
    """
    Similar to divide_integer_into_list_of_integer but uses a list list of percentages
    instead of a single divisor.
    :param number: The integer to divide
    :param proportions: A list of percentages as floats or decimals
    :return: a list of integers
    """
    split = []
    for idx, proportion in enumerate(proportions):
        split.append(int(number * proportion))
    return [x + y for x, y in zip(
        split, divide_integer_into_list_of_integers(number - sum(split), len(proportions)))]
