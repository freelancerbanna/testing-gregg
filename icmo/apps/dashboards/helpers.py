from math import ceil

from django.db.models import Sum, Avg

from core.calculators import currency_growth, growth
from core.helpers import QUARTERS, MONTHS_3
from periods.models import Period
from revenues.models import Segment


def get_segment_goal_growth_vs_actual(segment):
    periods = {
        p.period: p
        for p in
        Period.objects.filter(
            segment=segment, resolution='segment',
            period__in=('year', 'q1', 'q2', 'q3', 'q4')
        )
        }
    current_quarter = segment.company.get_current_quarter()
    return dict(
        goal=dict(
            q1=segment.qoq_q1_growth_goal,
            q2=segment.qoq_q2_growth_goal,
            q3=segment.qoq_q3_growth_goal,
            q4=segment.qoq_q4_growth_goal,
            annual=segment.yoy_growth_goal,
            average_sale=segment.yoy_average_sale_growth_goal,
        ),
        actual=dict(
            q1=currency_growth(periods['q1'].sales_revenue_actual, segment.prev_q1),
            q2=currency_growth(periods['q2'].sales_revenue_actual, segment.prev_q2),
            q3=currency_growth(periods['q3'].sales_revenue_actual, segment.prev_q3),
            q4=currency_growth(periods['q4'].sales_revenue_actual, segment.prev_q4),
            annual=currency_growth(periods['year'].sales_revenue_actual, segment.prev_annual),
            average_sale=currency_growth(periods['year'].average_sale_actual,
                                         segment.prev_average_sale),
        ),
        todate=dict(
            annual=dict(
                plan=segment.goal_annual,
                actual=periods['year'].sales_revenue_actual.amount,
                previous=segment.prev_annual
            ),
            quarter=dict(
                plan=getattr(segment, 'goal_%s' % current_quarter),
                actual=periods[current_quarter].sales_revenue_actual.amount,
                previous=getattr(segment, 'prev_%s' % current_quarter)
            ),
        )
    )


def get_revenue_plan_goal_growth_vs_actual(revenue_plan):
    periods = {
        p.period: p
        for p in
        Period.objects.filter(
            revenue_plan=revenue_plan, resolution='revenue_plan',
            period__in=('year', 'q1', 'q2', 'q3', 'q4')
        )
        }
    plan_revenue = Segment.objects.filter(revenue_plan=revenue_plan).aggregate(
        Sum('goal_q1'),
        Sum('goal_q2'),
        Sum('goal_q3'),
        Sum('goal_q4'),
        Sum('goal_annual'),
        Avg('average_sale'),

        Sum('prev_q1'),
        Sum('prev_q2'),
        Sum('prev_q3'),
        Sum('prev_q4'),
        Sum('prev_annual'),
        Avg('prev_average_sale'),
    )
    current_quarter = revenue_plan.company.get_current_quarter()
    return dict(
        goal=dict(
            q1=growth(plan_revenue['goal_q1__sum'], plan_revenue['prev_q1__sum']),
            q2=growth(plan_revenue['goal_q2__sum'], plan_revenue['prev_q2__sum']),
            q3=growth(plan_revenue['goal_q3__sum'], plan_revenue['prev_q3__sum']),
            q4=growth(plan_revenue['goal_q4__sum'], plan_revenue['prev_q4__sum']),
            annual=growth(plan_revenue['goal_annual__sum'],
                          plan_revenue['prev_annual__sum']),
            average_sale=growth(plan_revenue['average_sale__avg'],
                                plan_revenue['prev_average_sale__avg']),
        ),
        actual=dict(
            q1=growth(periods['q1'].sales_revenue_actual.amount,
                      plan_revenue['prev_q1__sum']),
            q2=growth(periods['q2'].sales_revenue_actual.amount,
                      plan_revenue['prev_q2__sum']),
            q3=growth(periods['q3'].sales_revenue_actual.amount,
                      plan_revenue['prev_q3__sum']),
            q4=growth(periods['q4'].sales_revenue_actual.amount,
                      plan_revenue['prev_q4__sum']),
            annual=growth(periods['year'].sales_revenue_actual.amount,
                          plan_revenue['prev_annual__sum']),
            average_sale=growth(periods['year'].average_sale_actual.amount,
                                plan_revenue['prev_average_sale__avg']),
        ),
        todate=dict(
            annual=dict(
                plan=plan_revenue['goal_annual__sum'],
                actual=periods['year'].sales_revenue_actual.amount,
                previous=plan_revenue['prev_annual__sum']
            ),
            quarter=dict(
                plan=plan_revenue['goal_%s__sum' % current_quarter],
                actual=periods[current_quarter].sales_revenue_actual.amount,
                previous=plan_revenue['prev_%s__sum' % current_quarter]
            ),
        )
    )


def get_segment_quarterly_plan_vs_actual_monthly(segment, field):
    values = Period.objects.filter(segment=segment, resolution='segment', period_type='month') \
        .values_list('%s_plan' % field, '%s_actual' % field, 'period')
    plansum = sum([x[0] for x in values])

    quarter_targets = {q: 0 for q in QUARTERS}
    for quarter in QUARTERS:
        quarter_targets[quarter] = int(ceil(
            segment.get_quarter_goal_percent_of_annual(quarter) * plansum))

    output = []
    for value in values:
        q = segment.company.get_fiscal_quarter_by_month_name(value[2])
        output.append(dict(plan=int(ceil(quarter_targets[q]/3)), actual=value[1], month=value[2]))
    return output


def get_revenue_plan_quarterly_plan_vs_actual_monthly(revenue_plan, field):
    output = [dict(actual=0, plan=0, month=month) for month in MONTHS_3]
    for segment in revenue_plan.segments.all():
        for idx, item in enumerate(get_segment_quarterly_plan_vs_actual_monthly(segment, field)):
            output[idx]['plan'] += item['plan']
            output[idx]['actual'] += item['actual']
    return output
