import arrow
import django_rq
from django_rq import job

from hubspot_icmo.helpers import map_events_to_icmo_campaigns
from hubspot_icmo.models import HubspotConnection, HubspotCompany, HubspotDeal, HubspotContact, \
    HubspotRevenuePlanCampaign, HubspotRevenuePlan


@job
def refresh_access_token(hubspot_connection_id):
    hc = HubspotConnection.objects.get(id=hubspot_connection_id)
    hc.refresh_access_token()


@job
def sync_hubspot_data(hubspot_connection_id):
    queue = django_rq.get_queue('default')
    job_companies = queue.enqueue(sync_hubspot_companies, hubspot_connection_id, timeout=60 * 60)

    job_contacts = queue.enqueue(sync_hubspot_contacts, hubspot_connection_id, timeout=60 * 60,
                                 depends_on=job_companies)
    job_deals = queue.enqueue(sync_hubspot_deals, hubspot_connection_id, timeout=60 * 60,
                              depends_on=job_contacts)
    job_assignment = queue.enqueue(assign_hubspot_events, hubspot_connection_id, timeout=60 * 60,
                                   depends_on=job_deals)
    # queue.enqueue(schedule_next_sync, hubspot_connection_id, depends_on=job_assignment)


@job('default', timeout=60 * 60)
def sync_hubspot_companies(hubspot_connection_id):
    hc = HubspotConnection.objects.get(id=hubspot_connection_id)
    HubspotCompany.refresh_companies(hc)


@job('default', timeout=60 * 60)
def sync_hubspot_deals(hubspot_connection_id):
    hc = HubspotConnection.objects.get(id=hubspot_connection_id)
    HubspotDeal.refresh_deals(hc)


@job('default', timeout=60 * 60)
def sync_hubspot_contacts(hubspot_connection_id):
    hc = HubspotConnection.objects.get(id=hubspot_connection_id)
    HubspotContact.initialize_contacts(hc)


@job('default', timeout=60 * 60)
def assign_hubspot_events(hubspot_connection_id):
    hc = HubspotConnection.objects.get(id=hubspot_connection_id)
    for hs_plan in hc.connected_plans.all():
        refresh_and_map_campaigns(hs_plan.pk)


@job('default', timeout=60 * 60)
def refresh_and_map_campaigns(hs_plan_id):
    queue = django_rq.get_queue('default')
    hs_plan = HubspotRevenuePlan.objects.get(id=hs_plan_id)
    job_campaigns = refresh_campaigns.delay(hs_plan.pk)
    job_campaigns_performance = queue.enqueue(refresh_campaigns_performance, hs_plan.pk,
                                              depends_on=job_campaigns,
                                              timeout=60 * 60)
    queue.enqueue(map_events, hs_plan.pk, depends_on=job_campaigns_performance, timeout=60 * 60)


@job('default', timeout=60 * 60)
def refresh_campaigns(hs_plan_id):
    hs_plan = HubspotRevenuePlan.objects.get(id=hs_plan_id)
    HubspotRevenuePlanCampaign.refresh_campaigns(hs_plan)


@job('default', timeout=60 * 60)
def refresh_campaigns_performance(hs_plan_id):
    hs_plan = HubspotRevenuePlan.objects.get(id=hs_plan_id)
    HubspotRevenuePlanCampaign.refresh_campaigns_performance(hs_plan)


@job('default', timeout=60 * 60)
def map_events(hs_plan_id):
    hs_plan = HubspotRevenuePlan.objects.get(id=hs_plan_id)
    map_events_to_icmo_campaigns(hs_plan)


@job
def schedule_next_sync(hubspot_connection_id):
    """
    Schedule next sync in 24 hours from now.
    :param hubspot_connection_id:
    """
    scheduler = django_rq.get_scheduler('default')
    scheduler.enqueue_at(
            arrow.get().replace(days=+1).datetime,
            sync_hubspot_data,
            hubspot_connection_id
    )
