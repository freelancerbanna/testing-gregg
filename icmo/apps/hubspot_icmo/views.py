from collections import defaultdict

import re
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from vanilla import UpdateView, TemplateView

from companies.models import Company
from core.cbvs import ItemRequiredMixin, HidePlanBarMixin
from core.helpers import icmo_reverse
from hubspot_icmo.forms import HubSpotConnectionForm
from hubspot_icmo.models import HubspotConnection, HubspotContact, HubspotRevenuePlan, \
    HubspotStages, HubspotRevenuePlanSegmentMap, SegmentMapFields, HubspotRevenuePlanCampaign
from leads.models import Program
from revenues.models import RevenuePlan, Segment
from .tasks import refresh_and_map_campaigns


class HubspotSetupView(ItemRequiredMixin, HidePlanBarMixin, UpdateView):
    template_name = 'accounts/integrations/hubspot/hubspot_setup.html'
    item_required = Company
    form_class = HubSpotConnectionForm
    model = HubspotConnection

    def get_object(self):
        connection, created = HubspotConnection.objects.get_or_create(
                company=self.request.selected_company)
        return connection

    def get_context_data(self, **kwargs):
        context = super(HubspotSetupView, self).get_context_data(**kwargs)
        context.update(dict(
                hubspot=self.object,
                unconnected_plans=RevenuePlan.objects.filter(
                        company=self.object.company,
                ).exclude(pk__in=self.object.connected_plans.values_list('pk', flat=True)),
                campaigns_count=HubspotContact.objects.filter(connection=self.object).values(
                        'campaign_name_guess').distinct().count(),
                connected_plans=self.object.connected_plans.filter(revenue_plan__is_active=True),
                campaign_names=HubspotContact.get_campaign_names(),
                good_campaign_name_count=self.object.get_good_campaign_count(),
                good_industry_count=self.object.get_good_industry_count(),
                good_contacts_count=self.object.get_good_contacts_count(),
                deals_count=self.object.deals.count(),
                sales_count=self.object.deals.filter(dealstage='closedwon').count(),
                events_subscriber_count=self.object.events.filter(
                        event_stage=HubspotStages.SUBSCRIBER).count(),
                events_lead_count=self.object.events.filter(
                        event_stage=HubspotStages.LEAD).count(),
                events_opportunity_count=self.object.events.filter(
                        event_stage=HubspotStages.OPPORTUNITY).count(),
                events_mql_count=self.object.events.filter(event_stage=HubspotStages.MQL).count(),
                events_sql_count=self.object.events.filter(event_stage=HubspotStages.SQL).count(),
                events_customer_count=self.object.events.filter(
                        event_stage=HubspotStages.CUSTOMER).count(),
        ))
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Hubspot Connection granted, redirected to by the hubspot auth screen
        if 'access_token' in request.GET and 'refresh_token' in request.GET and 'expires_in' in \
                request.GET:
            self.object.connect(request.GET['access_token'], request.GET['refresh_token'],
                                request.GET['expires_in'])
            # Start the first data sync
            self.object.queue_data_sync()
            messages.success(request,
                             "HubSpot successfully connected. Data is now syncing, this may take "
                             "up to one or more hours to complete depending on the size of your "
                             "HubSpot account")
            return redirect(icmo_reverse('hubspot_setup', request))

        elif 'connect_plan' in request.GET:
            revenue_plan = get_object_or_404(RevenuePlan, company=self.request.selected_company,
                                             slug=request.GET['connect_plan'])
            HubspotRevenuePlan.objects.get_or_create(connection=self.object,
                                                     revenue_plan=revenue_plan)
            messages.success(request, "Revenue Plan connected successfully")
            return redirect(icmo_reverse('hubspot_setup', request))
        return super(HubspotSetupView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.POST.get('action') == 'disconnect_hubspot':
            self.object.delete()
            messages.success(request, "HubSpot successfully disconnected")
            return self.get(request)
        elif request.POST.get('action') == 'disconnect_revenue_plan' and request.POST.get(
                'revenue_plan_slug'):
            hs_plan = get_object_or_404(HubspotRevenuePlan, connection=self.object,
                                        revenue_plan__slug=request.POST.get('revenue_plan_slug'))
            hs_plan.delete()
            messages.success(request,
                             "Revenue Plan %s successfully disconnected." % hs_plan.revenue_plan)
            return self.get(request)
        else:
            form = self.get_form(data=request.POST, files=request.FILES, instance=self.object)
            if form.is_valid():
                return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        connection = form.save()
        return redirect(connection.get_connection_url(self.request))


class HubspotMapCampaignsView(ItemRequiredMixin, HidePlanBarMixin, TemplateView):
    template_name = 'accounts/integrations/hubspot/hubspot_map_campaigns.html'
    item_required = Company
    http_method_names = ('post', 'get')

    def get_context_data(self, **kwargs):
        context = super(HubspotMapCampaignsView, self).get_context_data(**kwargs)
        hubspot = get_object_or_404(HubspotConnection, company=self.request.selected_company)
        campaign_revenue_plan = get_object_or_404(RevenuePlan,
                                                  company=self.request.selected_company,
                                                  slug=self.kwargs['campaigns_plan_slug'])
        hubspot_revenue_plan = hubspot.connected_plans.get(revenue_plan=campaign_revenue_plan)
        program_names = set(Program.objects.filter(
                revenue_plan=campaign_revenue_plan).order_by(
                'segment', 'name').values_list('name', flat=True))
        program_names = list(program_names)
        program_names.sort()
        context.update(dict(
                hubspot=hubspot,
                hubspot_revenue_plan=hubspot_revenue_plan,
                campaign_revenue_plan=campaign_revenue_plan,
                campaign_maps=HubspotRevenuePlanCampaign.objects.filter(
                        hubspot_revenue_plan=hubspot_revenue_plan),
                program_names=program_names,
                segments=Segment.objects.filter(revenue_plan=campaign_revenue_plan)
        ))
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        campaign_revenue_plan = context['campaign_revenue_plan']
        hubspot_revenue_plan = context['hubspot_revenue_plan']
        campaign_map = defaultdict(dict)
        hubspot_campaigns = {
            x.slug: x for x in
            HubspotRevenuePlanCampaign.objects.filter(hubspot_revenue_plan=hubspot_revenue_plan)
            }
        programs = defaultdict(dict)
        for program in Program.objects.filter(revenue_plan=campaign_revenue_plan):
            programs[program.segment.slug][program.slug] = program

        for key, val in request.POST.items():
            matches = re.match(r'^campaign-([^-]+)-program_name$', key)
            if matches:
                campaign_map[matches.groups()[0]]['program_name'] = val
            matches = re.match(r'^campaign-([^-]+)-segment-(.+)-program$', key)
            if matches:
                if 'segments' not in campaign_map[matches.groups()[0]]:
                    campaign_map[matches.groups()[0]]['segments'] = dict()
                campaign_map[matches.groups()[0]]['segments'][matches.groups()[1]] = val
        for campaign_slug, value in campaign_map.items():
            hubspot_campaigns[campaign_slug].programs.clear()
            for segment_slug, program_slug in value['segments'].items():
                if program_slug:
                    hubspot_campaigns[campaign_slug].programs.add(
                            programs[segment_slug][program_slug])

        # Queue the campaign refresh and map
        refresh_and_map_campaigns.delay(hubspot_revenue_plan.pk)
        messages.success(request,
                         "Hubspot -> iCMO Campaign Map updated successfully. Recalculating "
                         "Campaigns imported from HubSpot.  This may take a few minutes.")
        return self.render_to_response(context)


class HubspotMapSegmentsView(ItemRequiredMixin, HidePlanBarMixin, TemplateView):
    template_name = 'accounts/integrations/hubspot/hubspot_map_segments.html'
    item_required = Company
    http_method_names = ('post', 'get')

    def get_context_data(self, **kwargs):
        context = super(HubspotMapSegmentsView, self).get_context_data(**kwargs)
        hubspot = get_object_or_404(HubspotConnection, company=self.request.selected_company)
        hubspot_revenue_plan = get_object_or_404(HubspotRevenuePlan,
                                                 connection=hubspot,
                                                 revenue_plan__slug=self.kwargs[
                                                     'segments_map_revenue_plan_slug'])
        context.update(dict(
                hubspot=hubspot,
                hubspot_revenue_plan=hubspot_revenue_plan,
                map_revenue_plan=hubspot_revenue_plan.revenue_plan,
                segments_map=HubspotRevenuePlanSegmentMap.objects.filter(
                        revenue_plan=hubspot_revenue_plan.revenue_plan),
                segments=Segment.objects.filter(revenue_plan=hubspot_revenue_plan.revenue_plan)
        ))
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        hs_plan = context['hubspot_revenue_plan']
        if request.POST.get('segment_map_mode') and request.POST.get(
                'segment_map_mode') in [x[0] for x in SegmentMapFields.choices]:
            hs_plan.segment_mapping_field = request.POST.get('segment_map_mode')
            hs_plan.save()
            messages.success(request,
                             "Mapping mode changed successfully, please set up your segment map "
                             "again.")
        else:

            if hs_plan.segment_mapping_field == SegmentMapFields.INDUSTRY:
                industries_map = {x.hs_value_2: x for x in
                                  HubspotRevenuePlanSegmentMap.objects.filter(
                                          hubspot_revenue_plan=hs_plan)}
                segments = {x.slug: x for x in
                            Segment.objects.filter(revenue_plan=hs_plan.revenue_plan)}

                for key, segment_slug in request.POST.items():
                    matches = re.match(r'^industry-([^-]+)$', key)
                    if matches:
                        industry_slug = matches.groups()[0]
                        if segment_slug:
                            industries_map[industry_slug].segment = segments[segment_slug]
                        else:
                            industries_map[industry_slug].segment = None
                        industries_map[industry_slug].save()
            elif hs_plan.segment_mapping_field == SegmentMapFields.ANNUALREVENUE:
                for revenue_segment_map in HubspotRevenuePlanSegmentMap.objects.filter(
                        hubspot_revenue_plan=hs_plan):
                    revenue_segment_map.hs_value_1 = request.POST.get(
                            'revenue-value-%s' % revenue_segment_map.pk, '')
                    revenue_segment_map.save()

            # Queue the campaign refresh and map
            refresh_and_map_campaigns.delay(hs_plan.pk)
            messages.success(request,
                             "Hubspot -> iCMO Segment Map updated successfully. Recalculating "
                             "Campaigns imported from HubSpot.  This may take a few minutes.")
        return self.render_to_response(context)
