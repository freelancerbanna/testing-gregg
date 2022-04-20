import datetime
from collections import defaultdict

import arrow
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework.reverse import reverse
from vanilla import TemplateView

from core.cbvs import AppMixin
from core.helpers import MONTHS_3, QUARTERS, icmo_reverse
from core.models import ICMO_LEVELS
from periods.models import Period
from salesforce_icmo.models import SalesforceVirtualContactHistory, SalesforceVirtualContact, \
    SalesforceEvent


class ReportIndexView(AppMixin, TemplateView):
    template_name = 'reports/index.html'
    app_name = 'reports'


class BaseReportView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(BaseReportView, self).get_context_data(**kwargs)
        context.update(dict(
            revenue_plan_period_api_url=reverse('company-plans-periods-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
            revenue_plan_horizontal_period_api_url=reverse(
                'companies-plans-horizontal-periods-list', kwargs=dict(
                    parent_lookup_company__slug=self.request.selected_company.slug,
                    parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
        ))
        return context


class ReportPeriodFilterMixin(object):
    period_types = ['month', 'quarter', 'year']

    def get_context_data(self, **kwargs):
        context = super(ReportPeriodFilterMixin, self).get_context_data(**kwargs)
        all_periods = []
        if 'month' in self.period_types:
            all_periods.extend(self.request.selected_company.fiscal_months_by_name)
        if 'quarter' in self.period_types:
            all_periods.extend(QUARTERS)
        if 'year' in self.period_types:
            all_periods.append('year')
        report_period = self.request.GET.get('reportMonth', None) or self.request.POST.get(
            'reportMonth', None)
        if report_period not in all_periods:
            report_period = MONTHS_3[timezone.now().month - 1]
        context.update(dict(
            report_periods=all_periods,
            report_period=report_period
        ))
        return context

    def get_start_month(self, report_period):
        if report_period == 'year':
            return self.request.selected_company.fiscal_months_by_name[0]
        elif report_period in QUARTERS:
            return self.request.selected_company.fiscal_quarters_by_name[report_period][0]
        return report_period

    def get_end_month(self, report_period):
        if report_period == 'year':
            return self.request.selected_company.fiscal_months_by_name[-1]
        elif report_period in QUARTERS:
            return self.request.selected_company.fiscal_quarters_by_name[report_period][-1]
        return report_period


class SalesforceReportMixin(object):
    def get(self, request, *args, **kwargs):
        if not hasattr(request.selected_company, 'salesforceconnection') or not \
                request.selected_company.salesforceconnection or not \
                request.selected_company.salesforceconnection.setup_complete:
            messages.warning(request, "This company is not connected to salesforce")
            return redirect(icmo_reverse('reports_index', request))
        return super(SalesforceReportMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not hasattr(request.selected_company, 'salesforceconnection') or not \
                request.selected_company.salesforceconnection or not \
                request.selected_company.salesforceconnection.setup_complete:
            messages.warning(request, "This company is not connected to salesforce")
            return redirect(icmo_reverse('reports_index', request))
        return super(SalesforceReportMixin, self).post(request, *args, **kwargs)


class ReportMQLAcquiredView(BaseReportView):
    template_name = 'reports/report_mqls_acquired.html'


class ReportMQLsByProgramView(ReportPeriodFilterMixin, BaseReportView):
    template_name = 'reports/report_mqls_by_program.html'

    def get_context_data(self, **kwargs):
        context = super(ReportMQLsByProgramView, self).get_context_data(**kwargs)
        period = Period.objects.filter(revenue_plan=self.request.selected_plan,
                                       period=context['report_period'],
                                       resolution='revenue_plan').first()
        overall_average_cost_per_mql = 0
        if period:
            overall_average_cost_per_mql = period.cost_per_mql_actual

        aggregates = Period.objects.filter(revenue_plan=self.request.selected_plan,
                                           period=context['report_period'],
                                           resolution='program').aggregate(Sum('mql_actual'),
                                                                           Sum('budget_actual'))

        program_average_cost_per_mql = 0
        if aggregates['mql_actual__sum'] and aggregates['budget_actual__sum']:
            program_average_cost_per_mql = aggregates['budget_actual__sum'] / aggregates[
                'mql_actual__sum']
        context.update(dict(
            overall_average_cost_per_mql=overall_average_cost_per_mql,
            program_average_cost_per_mql=program_average_cost_per_mql
        ))
        return context


class ReportCampaignResultsView(ReportPeriodFilterMixin, BaseReportView):
    template_name = 'reports/report_campaign_results.html'


class ReportSFDCLeadTrackingView(SalesforceReportMixin, ReportPeriodFilterMixin, TemplateView):
    template_name = 'reports/report_sfdc_lead_tracking.html'
    period_types = ['month', 'quarter', 'year']

    def get_empty_metrics_dict(self):
        return dict(total=0, nurturing=0, unqualified=0, asked_to_meet=0, met_but_nothing_else=0,
                    converted=0,
                    closed_won=0, closed_lost=0)

    def get_context_data(self, **kwargs):
        context = super(ReportSFDCLeadTrackingView, self).get_context_data(**kwargs)
        sfc = self.request.selected_company.salesforceconnection
        report_source = self.request.GET.get('reportSource', None)
        report_starting_status = self.request.GET.get('reportStartingStatus',
                                                      sfc.filtered_statuses[0])

        sources = defaultdict(self.get_empty_metrics_dict)
        report_period = self.get_start_month(context['report_period'])
        start = arrow.get(datetime.datetime(self.request.selected_plan.plan_year,
                                            MONTHS_3.index(report_period) + 1,
                                            1), sfc.salesforce_timezone)

        end = start.replace(months=1, days=-1).ceil('day')

        qs = SalesforceVirtualContactHistory.objects.select_related('virtual_contact').filter(
            connection=sfc, updated__gte=start.datetime, updated__lte=end.datetime,
            status=report_starting_status)
        if report_source:
            qs = qs.filter(virtual_contact__segment_field_text_value=report_source)
        vcids = qs.distinct().order_by('updated').values_list('virtual_contact_id')
        history = SalesforceVirtualContactHistory.objects.select_related('virtual_contact').filter(
            connection=sfc, updated__gte=start.datetime, virtual_contact_id__in=vcids).order_by(
            'updated')
        vcs = defaultdict(list)
        for item in history:
            item.status_value = sfc.statuses.index(item.status)
            vcs[item.virtual_contact_id].append(item)

        for item in history:
            vid = item.virtual_contact_id
            lead_source = item.virtual_contact.campaign_field_value
            latest_status = vcs[vid][-1].status
            sources[lead_source]['total'] += 1
            if 'unqualified' in latest_status.lower():
                sources[lead_source]['unqualified'] += 1
            if max([x.status_value for x in vcs[vid]]) > vcs[vid][-1].status_value:
                sources[lead_source]['nurturing'] += 1
            if any([x for x in vcs[vid] if 'asked to meet' in x.status.lower()]):
                sources[lead_source]['asked_to_meet'] += 1
            if any([x for x in vcs[vid] if x.status.lower() == 'meeting completed']) and not any(
                    [x for x in vcs[vid] if
                     x.status_value > sfc.statuses.index('Meeting Completed')]):
                sources[lead_source]['met_but_nothing_else'] += 1
            if any([x for x in vcs[vid] if x.status.lower() == 'opportunity conversion']):
                sources[lead_source]['converted'] += 1
            if any([x for x in vcs[vid] if x.status.lower() == 'closed won']):
                sources[lead_source]['closed_won'] += 1
            if any([x for x in vcs[vid] if x.status.lower() == 'closed lost']):
                sources[lead_source]['closed_lost'] += 1
        context.update(dict(
            sources=dict(sources),
            totals=dict(
                total=sum([x['total'] for x in sources.values()]),
                nurturing=sum([x['nurturing'] for x in sources.values()]),
                unqualified=sum([x['unqualified'] for x in sources.values()]),
                asked_to_meet=sum([x['asked_to_meet'] for x in sources.values()]),
                met_but_nothing_else=sum([x['met_but_nothing_else'] for x in sources.values()]),
                converted=sum([x['converted'] for x in sources.values()]),
                closed_won=sum([x['closed_won'] for x in sources.values()]),
                closed_lost=sum([x['closed_lost'] for x in sources.values()]),
            ),
            report_sources=SalesforceVirtualContact.get_segment_text_values_by_connection(sfc),
            report_source=report_source,
            report_period=report_period,
            report_starting_status=report_starting_status,
            report_starting_statuses=sfc.statuses
        ))
        return context


class ReportSFDCLeadFunnelView(SalesforceReportMixin, ReportPeriodFilterMixin, TemplateView):
    template_name = 'reports/report_sfdc_lead_funnel.html'
    http_method_names = ('post', 'get')
    period_types = ['month']
    sfc = None

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ReportSFDCLeadFunnelView, self).get_context_data(**kwargs)
        report_period = context['report_period']
        report_source = None
        report_outcome = 'Closed Won'
        report_inferred = True
        report_data = False
        report_revenue = True

        if self.request.POST:
            report_source = self.request.POST.get('reportSource', None)
            report_outcome = self.request.POST.get('reportOutcome', 'Closed Won')
            report_inferred = self.request.POST.get('reportInferred', False)  # checkboxes are fun
            report_data = self.request.POST.get('reportData', False)  # checkboxes are fun
            report_revenue = self.request.POST.get('reportRevenue', False)  # checkboxes are fun

        self.sfc = self.request.selected_company.salesforceconnection
        chosen_statuses = [x for x in self.sfc.statuses if
                           x in self.request.POST.getlist('statuses')]
        if not chosen_statuses:
            chosen_statuses = self.sfc.filtered_statuses
        current_start = arrow.get(datetime.datetime(self.request.selected_plan.plan_year,
                                                    MONTHS_3.index(report_period) + 1,
                                                    1), self.sfc.salesforce_timezone)
        current_end = current_start.replace(months=1, days=-1).ceil('day')

        last_start = current_start.replace(months=-1)
        last_end = last_start.replace(months=1, days=-1).ceil('day')
        ytd_start = current_start.replace(month=1, day=1)
        ytd_end = ytd_start.replace(years=1, days=-1).ceil('day')
        report_segment = None

        report_outcomes = self.sfc.sfdc_end_statuses or ['Closed Won']

        current_vc_ids = self._get_virtual_contact_ids(report_source, current_start.datetime,
                                                       current_end.datetime)
        last_vc_ids = self._get_virtual_contact_ids(report_source, last_start.datetime,
                                                    last_end.datetime)
        ytd_vc_ids = self._get_virtual_contact_ids(report_source, ytd_start.datetime,
                                                   ytd_end.datetime)

        context.update(dict(
            sfc=self.sfc,
            statuses=self.sfc.statuses,
            chosen_statuses=chosen_statuses,
            current_month=current_start.format('MMM'),
            last_month=last_start.format('MMM'),
            current_leads=self._get_status_history(current_vc_ids, chosen_statuses,
                                                   report_outcome, report_inferred),
            last_leads=self._get_status_history(last_vc_ids, chosen_statuses, report_outcome,
                                                report_inferred),
            ytd_leads=self._get_status_history(ytd_vc_ids, chosen_statuses, report_outcome,
                                               report_inferred),
            current_average_sale=self._get_average_sales(current_vc_ids),
            current_closed_won=SalesforceVirtualContactHistory.objects.filter(
                connection=self.sfc,
                status='Closed Won',
                updated__gte=current_start.datetime,
                updated__lte=current_end.datetime).count(),
            last_closed_won=SalesforceVirtualContactHistory.objects.filter(
                connection=self.sfc,
                status='Closed Won',
                updated__gte=last_start.datetime,
                updated__lte=last_end.datetime).count(),
            ytd_closed_won=SalesforceVirtualContactHistory.objects.filter(
                connection=self.sfc,
                status='Closed Won',
                updated__gte=ytd_start.datetime,
                updated__lte=ytd_end.datetime).count(),
            last_average_sale=self._get_average_sales(last_vc_ids),
            ytd_average_sale=self._get_average_sales(ytd_vc_ids),
            current_total_sale=self._get_total_sales(current_vc_ids),
            last_total_sale=self._get_total_sales(last_vc_ids),
            ytd_total_sale=self._get_total_sales(ytd_vc_ids),
            current_outcomes=self._get_other_outcomes(current_vc_ids, report_outcome),
            last_outcomes=self._get_other_outcomes(last_vc_ids, report_outcome),
            ytd_outcomes=self._get_other_outcomes(ytd_vc_ids, report_outcome),
            report_segments=self.request.selected_plan.segments.all(),
            report_segment=report_segment,
            report_sources=SalesforceVirtualContact.get_segment_text_values_by_connection(
                self.sfc),
            report_source=report_source,
            report_outcome=report_outcome,
            report_outcomes=report_outcomes,
            report_inferred=report_inferred,
            report_data=report_data,
            report_revenue=report_revenue,
            current_history=self._get_all_history(current_vc_ids, report_inferred)
        ))
        return context

    def _get_virtual_contact_ids(self, report_source, start, end=None):
        qs = SalesforceVirtualContact.objects.filter(connection=self.sfc, created_date__gte=start)
        if end:
            qs = qs.filter(created_date__lt=end)
        if report_source:
            qs = qs.filter(segment_field_text_value=report_source)
        return qs.values_list('id', flat=True)

    def _get_status_history(self, vc_ids, statuses, report_outcome, report_inferred=True):
        qs = SalesforceVirtualContactHistory.objects.filter(virtual_contact_id__in=vc_ids)
        if not report_inferred:
            qs = qs.filter(is_virtual=False)
        history = qs.values('status', 'status_source').annotate(count=Count('status'))
        output = []
        history = {x['status']: x['count'] for x in history}
        for status in statuses:
            if status not in self.sfc.sfdc_end_statuses or status == report_outcome:
                output.append(dict(status=status, count=history.get(status, 0)))
        return output

    def _get_other_outcomes(self, vc_ids, report_outcome):
        return SalesforceVirtualContactHistory.objects.filter(
            status__in=[x for x in self.sfc.sfdc_end_statuses if x != report_outcome],
            virtual_contact_id__in=vc_ids).values('status', 'status_source').annotate(
            count=Count('status'))

    def _get_all_history(self, vc_ids, report_inferred=True):
        qs = SalesforceVirtualContactHistory.objects.filter(
            virtual_contact_id__in=vc_ids).select_related('virtual_contact',
                                                          'virtual_contact__salesforce_opportunity',
                                                          'virtual_contact__salesforce_lead')
        if not report_inferred:
            qs = qs.filter(is_virtual=False)
        return qs.all()

    def _get_average_sales(self, vc_ids):
        return SalesforceEvent.objects.filter(virtual_contact_id__in=vc_ids, event_stage='sale') \
            .exclude(amount=None).aggregate(Avg('amount'))['amount__avg']

    def _get_total_sales(self, vc_ids):
        return SalesforceEvent.objects.filter(virtual_contact_id__in=vc_ids, event_stage='sale') \
            .exclude(amount=None).aggregate(Sum('amount'))['amount__sum']


class ReportCustomVerticalView(ReportPeriodFilterMixin, BaseReportView):
    template_name = 'reports/report_custom_vertical.html'

    def get_context_data(self, **kwargs):
        context = super(ReportCustomVerticalView, self).get_context_data(**kwargs)
        fields = self.request.GET.getlist('fields', [])
        parent_fields = []
        resolution = self.request.GET.get('resolution')
        if resolution:
            parent = resolution
            while parent is not None:
                parent = ICMO_LEVELS[parent]['parent']
                if parent and parent not in ('company', 'revenue_plan'):
                    parent_fields.append(parent)
            parent_fields.reverse()
            fields = parent_fields + [resolution] + fields
        context.update(dict(
            fields=fields,
            resolution=resolution,
            groups=parent_fields,
            values_display=self.request.GET.get('valuesDisplay'),
            field_choices=(
                'average_sale',
                'budget',
                'contacts',
                'contacts_to_mql_conversion',
                'cost_per_mql',
                'cost_per_sql',
                'mql',
                'mql_to_sql_conversion',
                'roi',
                'sales',
                'sales_revenue',
                'sql',
                'sql_to_sale_conversion',
            ),
            resolution_choices=(
                'revenue_plan',
                'segment',
                'program',
                'campaign'
            )
        ))
        return context


class ReportCustomHorizontalView(TemplateView):
    pass
