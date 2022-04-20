from django.contrib import messages
from django.db.models import Sum
from django.db.models.query_utils import Q
from django.shortcuts import redirect, get_object_or_404
from vanilla import UpdateView, TemplateView, DetailView

from companies.models import Company
from core.cbvs import ItemRequiredMixin, HidePlanBarMixin
from core.helpers import icmo_reverse
from leads.models import ProgramTypes
from periods.helpers import recompute_periods, recompute_segments_and_up
from revenues.models import RevenuePlan
from salesforce_icmo.helpers import aggregate_month_events
from .forms import SalesforceConnectionForm, SalesforceSettingsForm
from .models import SalesforceConnection, SalesforceVirtualContact, \
    SalesforceRevenuePlan, SalesforceRevenuePlanMapEntry, SalesforceEvent, SalesforceLead, \
    SalesforceOpportunity, SalesforceDataIssue


class SalesforceSetupView(ItemRequiredMixin, HidePlanBarMixin, UpdateView):
    template_name = 'accounts/integrations/salesforce/salesforce_setup.html'
    item_required = Company
    form_class = SalesforceConnectionForm
    model = SalesforceConnection

    def get_object(self):
        connection, created = self.model.objects.get_or_create(
            company=self.request.selected_company)
        return connection

    def get(self, request, *args, **kwargs):
        sfc = self.get_object()

        # Salesforce Connection granted, redirected to by the salesforce auth screen
        if 'code' in request.GET:
            try:
                sfc.connect(request.GET['code'])
            except ValueError:
                messages.error(request, "Could not connect to Salesforce, please try again later.")
                return redirect(icmo_reverse('sfdc_setup', request))

        if sfc.setup_complete:
            return redirect(icmo_reverse('sfdc_manage', self.request))
        elif sfc.connected:
            return redirect(icmo_reverse('sfdc_settings', self.request))

        return super(SalesforceSetupView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        return redirect(self.object.get_connection_url())


class SalesforceSettingsView(UpdateView):
    model = SalesforceConnection
    template_name = 'accounts/integrations/salesforce/salesforce_settings.html'
    item_required = Company
    form_class = SalesforceSettingsForm

    def get_object(self):
        return SalesforceConnection.objects.get(company=self.request.selected_company)

    def get_success_url(self):
        sfc = self.get_object()
        if sfc.setup_complete:
            # Start the first data sync
            sfc.queue_data_sync()
            messages.success(self.request,
                             "Salesforce successfully connected. Data is now syncing, "
                             "this may take "
                             "up to one hour to complete depending on the size of your "
                             "Salesforce account")
            return icmo_reverse('sfdc_manage', self.request)
        messages.warning(self.request,
                         "Salesforce not successfully connected, please try again, or contact "
                         "iCMO support.")
        return icmo_reverse('sfdc_settings', self.request)


class SalesforceManageView(ItemRequiredMixin, HidePlanBarMixin, DetailView):
    template_name = 'accounts/integrations/salesforce/salesforce_manage.html'
    item_required = Company
    model = SalesforceConnection

    def get_object(self):
        try:
            return self.model.objects.get(company=self.request.selected_company)
        except self.model.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super(SalesforceManageView, self).get_context_data(**kwargs)
        context.update(dict(
            salesforce=self.object,
            unconnected_plans=RevenuePlan.objects.filter(
                company=self.object.company,
            ).exclude(pk__in=self.object.connected_plans.values_list('pk', flat=True)),
            sources=SalesforceVirtualContact.get_sources_by_connection(self.object),
            connected_plans=self.object.connected_plans.filter(revenue_plan__is_active=True),
            sales_count=self.object.opportunities.filter(sfdc_stage_name='Closed Won').count(),
            sales_total=self.object.opportunities.filter(sfdc_stage_name='Closed Won').aggregate(
                Sum('sfdc_amount'))['sfdc_amount__sum'],
            orphan_opportunities_count=self.object.virtual_contacts.filter(is_virtual=True).count()
        ))
        return context

    def get(self, request, *args, **kwargs):
        sfc = self.get_object()
        if not sfc or not sfc.setup_complete:
            return redirect(icmo_reverse('sfdc_setup', self.request))

        if 'connect_plan' in request.GET:
            revenue_plan = get_object_or_404(RevenuePlan, company=self.request.selected_company,
                                             slug=request.GET['connect_plan'])
            SalesforceRevenuePlan.objects.get_or_create(connection=sfc,
                                                        revenue_plan=revenue_plan)
            messages.success(request, "Revenue Plan connected successfully")
            return redirect(icmo_reverse('sfdc_setup', request))
        return super(SalesforceManageView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        sfc = self.get_object()
        if request.POST.get('action') == 'disconnect_salesforce':
            # cascade delete won't trigger post_delete signals so need to force period
            # recomputation
            connected_plans = sfc.connected_plans.all()
            sfc.delete()
            [recompute_periods(x) for x in connected_plans]
            messages.success(request, "Salesforce successfully disconnected")
            return self.get(request)
        elif request.POST.get('action') == 'sync':
            from .tasks import sync_salesforce_data
            sync_salesforce_data.delay(sfc.id)
            messages.success(request, "Salesforce sync started.")
            return redirect(icmo_reverse('sfdc_manage', request))
        elif request.POST.get('action') == 'disconnect_revenue_plan' and request.POST.get(
                'revenue_plan_slug'):
            sfdc_plan = get_object_or_404(SalesforceRevenuePlan, connection=sfc,
                                          revenue_plan__slug=request.POST.get('revenue_plan_slug'))
            sfdc_plan.delete()
            messages.success(request,
                             "Revenue Plan %s successfully disconnected." % sfdc_plan.revenue_plan)
            return self.get(request)
        return super(SalesforceManageView, self).get(request, *args, **kwargs)


class SalesforceMapView(ItemRequiredMixin, HidePlanBarMixin, TemplateView):
    template_name = 'accounts/integrations/salesforce/salesforce_map.html'
    item_required = Company
    http_method_names = ('post', 'get')
    sfc = None
    map_plan = None
    sf_plan = None

    def dispatch(self, request, *args, **kwargs):
        self.sfc = get_object_or_404(SalesforceConnection, company=self.request.selected_company)
        self.map_plan = get_object_or_404(RevenuePlan,
                                          company=self.request.selected_company,
                                          slug=self.kwargs['map_plan_slug'])
        self.sf_plan = self.sfc.connected_plans.get(revenue_plan=self.map_plan)
        return super(SalesforceMapView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.items():
            requested_mapping = dict()
            for key, program_id in request.POST.items():
                if key.startswith('map_entry_program_'):
                    requested_mapping[int(key.replace('map_entry_program_', ''))] = int(program_id)

            if requested_mapping:
                programs = self.sf_plan.revenue_plan.programs.in_bulk(requested_mapping.values())
                programs[0] = None

                for entry in SalesforceRevenuePlanMapEntry.objects.filter(
                        id__in=requested_mapping.keys()):
                    entry.map_to_program(programs[requested_mapping[entry.id]])

            from .tasks import refresh_map_and_campaigns
            refresh_map_and_campaigns.delay(self.sf_plan.id)
            # trigger an extra recompute segments phase
            recompute_segments_and_up(self.map_plan)
            messages.success(request,
                             "Salesforce -> iCMO Map updated successfully. Recalculating "
                             "Campaigns imported from Salesforce.  This may take a few minutes.")
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(SalesforceMapView, self).get_context_data(**kwargs)
        context.update(dict(
            sfc=self.sfc,
            map_plan=self.map_plan,
            sf_plan=self.sf_plan,
            map_entries=self.get_map_entries_annotated_with_stats(),
            programs=self.map_plan.programs.exclude(item_type=ProgramTypes.CATEGORY) \
                .select_related('segment').all().order_by('segment__name', 'name'),
        ))
        return context

    def get_map_entries_annotated_with_stats(self):
        map_entries = self.sf_plan.map_entries.all()
        mapped_events, unmapped_events = \
            SalesforceRevenuePlanMapEntry.get_mapped_and_unmapped_events(self.sf_plan)
        for entry in map_entries:
            if entry.campaign:
                entry.stats = aggregate_month_events(
                    mapped_events[entry.segment_value][entry.source_value]
                )
            else:
                entry.stats = aggregate_month_events(
                    unmapped_events[entry.segment_value][entry.source_value]
                )
            entry.has_events = any(entry.stats.values())
        return map_entries


class SalesforceEventsView(ItemRequiredMixin, HidePlanBarMixin, TemplateView):
    template_name = 'accounts/integrations/salesforce/salesforce_events.html'
    item_required = Company
    http_method_names = ('get',)

    def get_context_data(self, **kwargs):
        context = super(SalesforceEventsView, self).get_context_data(**kwargs)
        sfc = get_object_or_404(SalesforceConnection, company=self.request.selected_company)
        vc_plan = get_object_or_404(RevenuePlan,
                                    company=self.request.selected_company,
                                    slug=self.kwargs['events_plan_slug'])

        sf_plan = sfc.connected_plans.get(revenue_plan=vc_plan)
        events = SalesforceEvent.objects.filter(
            connection=sf_plan.connection,
            event_date__gte=sf_plan.start_datetime,
            event_date__lte=sf_plan.end_datetime) \
            .select_related('virtual_contact',
                            'virtual_contact__salesforce_lead',
                            'virtual_contact__salesforce_account',
                            'virtual_contact__salesforce_opportunity') \
            .order_by('virtual_contact', 'event_date')

        context.update(dict(
            sfc=sfc,
            vc_plan=vc_plan,
            sf_plan=sf_plan,
            events=events
        ))
        return context


class SalesforceVirtualContactsView(ItemRequiredMixin, HidePlanBarMixin, TemplateView):
    template_name = 'accounts/integrations/salesforce/salesforce_virtual_contacts.html'
    item_required = Company
    http_method_names = ('get',)

    def get_context_data(self, **kwargs):
        context = super(SalesforceVirtualContactsView, self).get_context_data(**kwargs)
        sfc = get_object_or_404(SalesforceConnection, company=self.request.selected_company)
        vc_plan = get_object_or_404(RevenuePlan,
                                    company=self.request.selected_company,
                                    slug=self.kwargs['vc_plan_slug'])
        sf_plan = sfc.connected_plans.get(revenue_plan=vc_plan)
        vc_ids = SalesforceEvent.objects.filter(connection=sfc,
                                                event_date__gte=sf_plan.start_datetime,
                                                event_date__lte=sf_plan.end_datetime
                                                ).values_list('virtual_contact_id', flat=True)
        virtual_contacts = SalesforceVirtualContact.objects \
            .prefetch_related('events') \
            .select_related('salesforce_lead',
                            'salesforce_account',
                            'salesforce_opportunity') \
            .filter(connection=sfc, id__in=vc_ids)

        context.update(dict(
            sfc=sfc,
            vc_plan=vc_plan,
            sf_plan=sf_plan,
            virtual_contacts=virtual_contacts
        ))
        return context


class SalesforcePlanBreakdownView(ItemRequiredMixin, HidePlanBarMixin, TemplateView):
    template_name = 'accounts/integrations/salesforce/salesforce_breakdown.html'
    item_required = Company
    http_method_names = ('get',)

    def get_context_data(self, **kwargs):
        context = super(SalesforcePlanBreakdownView, self).get_context_data(**kwargs)
        sfc = get_object_or_404(SalesforceConnection, company=self.request.selected_company)
        breakdown_plan = get_object_or_404(RevenuePlan,
                                           company=self.request.selected_company,
                                           slug=self.kwargs['breakdown_plan_slug'])
        sf_plan = sfc.connected_plans.get(revenue_plan=breakdown_plan)

        leads = SalesforceLead.objects.filter(
            connection=sfc,
            sfdc_created_date__gte=sf_plan.start_datetime,
            sfdc_created_date__lte=sf_plan.end_datetime)
        opportunities = SalesforceOpportunity.objects.filter(
            connection=sfc,
            sfdc_created_date__gte=sf_plan.start_datetime,
            sfdc_created_date__lte=sf_plan.end_datetime)
        mqls_total_1 = leads.count()
        status_filter = Q()
        for x in sfc.sfdc_statuses_to_ignore:
            status_filter |= Q(sfdc_status__iexact=x)
        mqls_leads_excluded = leads.filter(status_filter).count()
        mqls_total_2 = leads.exclude(status_filter).count()
        orphans = SalesforceOpportunity.objects.filter(
            connection=sfc,
            sfdc_created_date__gte=sf_plan.start_datetime,
            sfdc_created_date__lte=sf_plan.end_datetime,
            salesforce_lead=None

        )
        # leads may have been CREATED in a previous time period, do not filter by sfdc_created_date
        converted_leads = SalesforceLead.objects.filter(
            connection=sfc,
            sfdc_converted_date__gte=sf_plan.start_datetime,
            sfdc_converted_date__lte=sf_plan.end_datetime
        ).exclude(salesforce_opportunity=None).count()
        mql_orphans = orphans.count()
        mql_total_3 = mqls_total_2 + mql_orphans
        context.update(dict(
            sfc=sfc,
            breakdown_plan=breakdown_plan,
            sf_plan=sf_plan,
            mqls_total_1=mqls_total_1,
            mqls_leads_excluded=mqls_leads_excluded,
            mqls_total_2=mqls_total_2,
            mqls_orphan=orphans.count(),
            mqls_total_3=mql_total_3,
            opportunities_total=opportunities.count(),
            leads_total=leads.count(),
            converted_leads=converted_leads
        ))
        return context


class SalesforceIssuesView(ItemRequiredMixin, HidePlanBarMixin, TemplateView):
    template_name = 'accounts/integrations/salesforce/salesforce_issues.html'
    item_required = Company
    http_method_names = ('get',)

    def get_context_data(self, **kwargs):
        context = super(SalesforceIssuesView, self).get_context_data(**kwargs)
        sfc = get_object_or_404(SalesforceConnection, company=self.request.selected_company)
        issues_plan = get_object_or_404(RevenuePlan,
                                        company=self.request.selected_company,
                                        slug=self.kwargs['issues_plan_slug'])
        sf_plan = sfc.connected_plans.get(revenue_plan=issues_plan)
        context.update(dict(
            sfc=sfc,
            breakdown_plan=issues_plan,
            sf_plan=sf_plan,
            issues=SalesforceDataIssue.objects.filter(
                virtual_contact_id__in=sf_plan.all_events().distinct().values_list(
                    'virtual_contact_id', flat=True))
        ))
        return context
