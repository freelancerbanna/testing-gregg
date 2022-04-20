import arrow
import django_rq
from django_rq import job

from .models import SalesforceConnection, SalesforceRevenuePlan, \
    SalesforceAccount, SalesforceOpportunity, SalesforceLead, SalesforceVirtualContact, \
    SalesforceVirtualContactHistory, SalesforceRevenuePlanMapEntry, SalesforceDataIssue


@job('integrations')
def sync_salesforce_data(salesforce_connection_id):
    queue = django_rq.get_queue('integrations')
    sfc = SalesforceConnection.objects.get(id=salesforce_connection_id)
    SalesforceDataIssue.objects.filter(connection=sfc).delete()
    sfc.refresh_access_token()
    sfc = SalesforceConnection.objects.get(id=salesforce_connection_id)
    sfc.mark_syncing()
    job_accounts = queue.enqueue(sync_salesforce_accounts, salesforce_connection_id,
                                 timeout=60 * 60)
    job_opportunities = queue.enqueue(sync_salesforce_opportunities, salesforce_connection_id,
                                      timeout=60 * 60,
                                      depends_on=job_accounts)
    job_leads = queue.enqueue(sync_salesforce_leads, salesforce_connection_id, timeout=60 * 60,
                              depends_on=job_opportunities)
    job_virtual = queue.enqueue(refresh_salesforce_virtual_contacts, salesforce_connection_id,
                                timeout=60 * 60,
                                depends_on=job_leads)

    job_assignment = queue.enqueue(assign_salesforce_events, salesforce_connection_id,
                                   timeout=60 * 60,
                                   depends_on=job_virtual)
    queue.enqueue(schedule_next_sync, salesforce_connection_id, depends_on=job_assignment)


@job('integrations', timeout=60 * 60)
def sync_salesforce_accounts(salesforce_connection_id):
    sfc = SalesforceConnection.objects.get(id=salesforce_connection_id)
    SalesforceAccount.refresh_accounts(sfc)


@job('integrations', timeout=60 * 60)
def sync_salesforce_opportunities(salesforce_connection_id):
    sfc = SalesforceConnection.objects.get(id=salesforce_connection_id)
    SalesforceOpportunity.refresh_opportunities(sfc)


@job('integrations', timeout=60 * 60)
def sync_salesforce_leads(salesforce_connection_id):
    sfc = SalesforceConnection.objects.get(id=salesforce_connection_id)
    SalesforceLead.refresh_leads(sfc)


@job('integrations', timeout=60 * 60)
def refresh_salesforce_virtual_contacts(salesforce_connection_id):
    sfc = SalesforceConnection.objects.get(id=salesforce_connection_id)
    SalesforceVirtualContact.refresh_virtual_contacts_and_events(sfc)
    SalesforceVirtualContactHistory.refresh_history(sfc)


@job('integrations', timeout=60 * 60)
def assign_salesforce_events(salesforce_connection_id):
    sfc = SalesforceConnection.objects.get(id=salesforce_connection_id)
    if not sfc.connected_plans.count():
        sfc.mark_synced()
    else:
        for sf_plan in sfc.connected_plans.all():
            refresh_map_and_campaigns(sf_plan.pk)


@job('integrations', timeout=60 * 60)
def refresh_map_and_campaigns(sf_plan_id):
    sf_plan = SalesforceRevenuePlan.objects.get(id=sf_plan_id)
    sf_plan.connection.mark_syncing()
    SalesforceRevenuePlanMapEntry.refresh_map(sf_plan)
    SalesforceRevenuePlanMapEntry.refresh_campaign_performance_data(sf_plan)
    sf_plan.connection.mark_synced()


@job('integrations')
def schedule_next_sync(salesforce_connection_id):
    """
    Schedule next sync in 24 hours from now.
    :param salesforce_connection_id:
    """
    scheduler = django_rq.get_scheduler('default')
    scheduler.enqueue_at(
        arrow.get().replace(days=+1).datetime,
        sync_salesforce_data,
        salesforce_connection_id
    )
