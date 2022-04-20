from django.core.urlresolvers import reverse
from django.db.models.aggregates import Sum
from django.template.response import TemplateResponse
from vanilla import TemplateView

from core.cbvs import AppMixin
from dashboards.helpers import get_segment_goal_growth_vs_actual, \
    get_revenue_plan_goal_growth_vs_actual, get_revenue_plan_quarterly_plan_vs_actual_monthly, \
    get_segment_quarterly_plan_vs_actual_monthly
from periods.models import Period


class AvoidEmptyDashboardsMixin(object):
    def get(self, request, *args, **kwargs):
        context_data = self.get_context_data(**kwargs)
        if not self.request.selected_plan.program_set.all() or not context_data['segments']:
            return TemplateResponse(
                request=self.request,
                template='dashboards/not_ready.html',
                context={}
            )
        return super(AvoidEmptyDashboardsMixin, self).get(request, *args, **kwargs)

    def exclude_segments_with_no_period_data(self, segments):
        valid_segment_slugs = Period.objects.filter(
            revenue_plan=self.request.selected_plan,
            resolution='segment').values_list(
            'segment__slug',
            flat=True).distinct()
        return segments.filter(slug__in=valid_segment_slugs)


class DashboardsView(AppMixin, AvoidEmptyDashboardsMixin, TemplateView):
    template_name = 'dashboards/cmo_dashboard.html'
    app_name = 'dashboards'

    def get_context_data(self, **kwargs):
        context_data = super(DashboardsView, self).get_context_data(**kwargs)
        context_data['segments'] = self.exclude_segments_with_no_period_data(
            context_data['segments'])
        if not context_data['segments']:
            return context_data

        # # Gantt Task Statuses
        # task_status = dict(summary=defaultdict(int), segments=dict())
        # for task in GanttTask.objects.select_related().filter(
        #         company=self.request.selected_company, revenue_plan=self.request.selected_plan):
        #     if task.segment.slug not in task_status['segments']:
        #         task_status['segments'][task.segment.slug] = defaultdict(int)
        #     task_status['summary'][task.status] += 1
        #     task_status['segments'][task.segment.slug][task.status] += 1

        # Budgets
        custom_budgets = {
            x['segment__slug']: dict(plan=x['budget_plan__sum'], actual=x['budget_plan__sum'])
            for x in
            Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                resolution='custom_budget_line_item', period='year',
                period_type='year'
            ).values('segment__slug').annotate(Sum('budget_actual'), Sum('budget_plan'))
            }
        program_budgets = {
            x['segment__slug']: dict(plan=x['budget_plan__sum'], actual=x['budget_plan__sum'])
            for x in
            Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                resolution='program', period='year',
                period_type='year'
            ).values('segment__slug').annotate(Sum('budget_actual'), Sum('budget_plan'))
            }

        for idx, segment in enumerate(context_data['segments']):
            context_data['segments'][idx].dash_budgets = dict(
                custom=custom_budgets.get(segment.slug, dict(plan=0, actual=0)),
                program=program_budgets.get(segment.slug, dict(plan=0, actual=0)),
            )
            context_data['segments'][idx].funnel_data = Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                segment=segment,
                resolution='segment', period='year').first()
            context_data['segments'][idx].growth = get_segment_goal_growth_vs_actual(segment)
            # context_data['segments'][idx].task_status = task_status['segments'][segment.slug]
            context_data['segments'][
                idx].mql_planned_vs_actual_monthly = get_segment_quarterly_plan_vs_actual_monthly(
                segment, 'mql')
            context_data['segments'][
                idx].sql_planned_vs_actual_monthly = get_segment_quarterly_plan_vs_actual_monthly(
                segment, 'sql')
            context_data['segments'][idx].sales_planned_vs_actual_monthly = \
                get_segment_quarterly_plan_vs_actual_monthly(
                    segment, 'sales')
            context_data['segments'][idx].revenue_planned_vs_actual_monthly = \
                get_segment_quarterly_plan_vs_actual_monthly(
                    segment, 'sales_revenue')

        company = self.request.selected_company
        company.funnel_data = Period.objects.filter(
            company=self.request.selected_company,
            revenue_plan=self.request.selected_plan,
            resolution='revenue_plan', period='year').first()
        company.dash_budgets = dict(
            custom=Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                resolution='custom_budget_line_item',
                period='year',
                period_type='year'
            ).aggregate(Sum('budget_actual'), Sum('budget_plan')),
            program=Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                resolution='program',
                period='year',
                period_type='year'
            ).aggregate(Sum('budget_actual'), Sum('budget_plan')),
        )
        company.growth = get_revenue_plan_goal_growth_vs_actual(self.request.selected_plan)
        # company.task_status = task_status['summary']
        company.mql_planned_vs_actual_monthly = get_revenue_plan_quarterly_plan_vs_actual_monthly(
            self.request.selected_plan, 'mql')
        company.sql_planned_vs_actual_monthly = get_revenue_plan_quarterly_plan_vs_actual_monthly(
            self.request.selected_plan, 'sql')
        company.sales_planned_vs_actual_monthly = \
            get_revenue_plan_quarterly_plan_vs_actual_monthly(self.request.selected_plan, 'sales')
        company.revenue_planned_vs_actual_monthly = \
            get_revenue_plan_quarterly_plan_vs_actual_monthly(self.request.selected_plan,
                                                              'sales_revenue')
        context_data.update(dict(
            company=company,
            revenue_plan_period_api_url=reverse('company-plans-periods-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
            dashboard='cmo',
            app_segment_content_template='dashboards/dashboards/cmo.html',
            disable_charts=True,
            disable_toolbar=True,
        ))
        return context_data


class DashboardsBudgetView(AppMixin, AvoidEmptyDashboardsMixin, TemplateView):
    template_name = 'dashboards/budget_dashboard.html'
    app_name = 'dashboards'

    def get_context_data(self, **kwargs):
        context_data = super(DashboardsBudgetView, self).get_context_data(**kwargs)
        context_data['segments'] = self.exclude_segments_with_no_period_data(
            context_data['segments'])
        if not context_data['segments']:
            return context_data

        # Budgets
        custom_budgets = {
            x['segment__slug']: dict(budget_plan__sum=x['budget_plan__sum'],
                                     budget_actual__sum=x['budget_actual__sum'])
            for x in
            Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                resolution='custom_budget_line_item', period='year',
                period_type='year'
            ).values('segment__slug').annotate(Sum('budget_actual'), Sum('budget_plan'))
            }
        program_budgets = {
            x['segment__slug']: dict(budget_plan__sum=x['budget_plan__sum'],
                                     budget_actual__sum=x['budget_actual__sum'])
            for x in
            Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                resolution='program', period='year',
                period_type='year'
            ).values('segment__slug').annotate(Sum('budget_actual'), Sum('budget_plan'))
            }

        for idx, segment in enumerate(context_data['segments']):
            context_data['segments'][idx].dash_budgets = dict(
                custom=custom_budgets.get(segment.slug, dict(plan=0, actual=0)),
                program=program_budgets.get(segment.slug, dict(plan=0, actual=0)),
            )
            context_data['segments'][idx].funnel_data = Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                segment=segment,
                resolution='segment', period='year').first()
            context_data['segments'][idx].top_5_over_budget = self.get_top_5_over_budget(segment)
            context_data['segments'][idx].top_5_under_budget = self.get_top_5_under_budget(segment)

        company = self.request.selected_company
        company.funnel_data = Period.objects.filter(
            company=self.request.selected_company,
            revenue_plan=self.request.selected_plan,
            resolution='revenue_plan', period='year').first()
        company.dash_budgets = dict(
            custom=Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                resolution='custom_budget_line_item',
                period='year',
                period_type='year'
            ).aggregate(Sum('budget_actual'), Sum('budget_plan')),
            program=Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                resolution='program',
                period='year',
                period_type='year'
            ).aggregate(Sum('budget_actual'), Sum('budget_plan')),
        )
        company.top_5_over_budget = self.get_top_5_over_budget()
        company.top_5_under_budget = self.get_top_5_under_budget()

        context_data.update(dict(
            company=company,
            revenue_plan_period_api_url=reverse('company-plans-periods-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
            dashboard='budget',
            app_segment_content_template='dashboards/dashboards/budgets.html',
            disable_charts=True,
            disable_toolbar=True,
        ))
        return context_data

    def get_top_5_under_budget(self, segment=None):
        qs = Period.objects.select_related(
            'segment', 'program').filter(
            company=self.request.selected_company,
            revenue_plan=self.request.selected_plan,
            resolution='program',
            period_type='month',
            budget_variance__gt=0
        ).exclude(budget_actual=0).order_by('-budget_variance')
        if segment:
            qs = qs.filter(segment=segment)
        return qs[:5]

    def get_top_5_over_budget(self, segment=None):
        qs = Period.objects.select_related(
            'segment', 'program').filter(
            company=self.request.selected_company,
            revenue_plan=self.request.selected_plan,
            resolution='program',
            period_type='month',
            budget_variance__lt=0
        ).exclude(budget_actual=0).order_by('budget_variance')
        if segment:
            qs = qs.filter(segment=segment)
        return qs[:5]


class DashboardsPerformanceView(AppMixin, AvoidEmptyDashboardsMixin, TemplateView):
    template_name = 'dashboards/performance_dashboard.html'
    app_name = 'dashboards'

    def get_context_data(self, **kwargs):
        context_data = super(DashboardsPerformanceView, self).get_context_data(**kwargs)
        context_data['segments'] = self.exclude_segments_with_no_period_data(
            context_data['segments'])
        if not context_data['segments']:
            return context_data
        for idx, segment in enumerate(context_data['segments']):
            context_data['segments'][idx].funnel_data = Period.objects.filter(
                company=self.request.selected_company,
                revenue_plan=self.request.selected_plan,
                segment=segment,
                resolution='segment', period='year').first()
            context_data['segments'][
                idx].summary_api_url = reverse(
                'companies-plans-segments-horizontal-periods-list', kwargs=dict(
                    parent_lookup_company__slug=self.request.selected_company.slug,
                    parent_lookup_revenue_plan__slug=self.request.selected_plan.slug,
                    parent_lookup_segment__slug=segment.slug
                ))
            context_data['segments'][
                idx].mql_planned_vs_actual_monthly = get_segment_quarterly_plan_vs_actual_monthly(
                segment, 'mql')
            context_data['segments'][
                idx].sql_planned_vs_actual_monthly = get_segment_quarterly_plan_vs_actual_monthly(
                segment, 'sql')
            context_data['segments'][idx].sales_planned_vs_actual_monthly = \
                get_segment_quarterly_plan_vs_actual_monthly(
                    segment, 'sales')
            context_data['segments'][idx].revenue_planned_vs_actual_monthly = \
                get_segment_quarterly_plan_vs_actual_monthly(
                    segment, 'sales_revenue')

        company = self.request.selected_company
        company.funnel_data = Period.objects.filter(
            company=self.request.selected_company,
            revenue_plan=self.request.selected_plan,
            resolution='revenue_plan', period='year').first()
        company.summary_api_url = reverse(
            'companies-plans-horizontal-periods-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug,
            ))
        company.mql_planned_vs_actual_monthly = get_revenue_plan_quarterly_plan_vs_actual_monthly(
            self.request.selected_plan, 'mql')
        company.sql_planned_vs_actual_monthly = get_revenue_plan_quarterly_plan_vs_actual_monthly(
            self.request.selected_plan, 'sql')
        company.sales_planned_vs_actual_monthly = \
            get_revenue_plan_quarterly_plan_vs_actual_monthly(self.request.selected_plan, 'sales')
        company.revenue_planned_vs_actual_monthly = \
            get_revenue_plan_quarterly_plan_vs_actual_monthly(self.request.selected_plan,
                                                              'sales_revenue')
        context_data.update(dict(
            company=company,
            revenue_plan_period_api_url=reverse('company-plans-periods-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
            dashboard='performance',
            app_segment_content_template='dashboards/dashboards/performance.html',
            disable_charts=True,
            disable_toolbar=True,
        ))
        return context_data
