import logging
from collections import defaultdict

from hubspot.contacts.lists import CONTACTS_API_SCRIPT_NAME, PaginatedDataRetriever

from core.helpers import MONTHS_3

logger = logging.getLogger('icmo.%s' % __name__)


def get_offset_iterator(connection, url, query_dict=None, has_more_key=None, results_key=None):
    retrieve = True
    if not query_dict:
        query_dict = dict()
    if not has_more_key:
        has_more_key = 'hasMore'
    if not results_key:
        results_key = 'results'
    query_dict['count'] = 1000  # max it out to get the most
    query_dict['offset'] = 0
    while retrieve:
        results = connection.send_get_request(url, query_dict)
        retrieve = results[has_more_key]
        if not retrieve:
            print results
        query_dict['offset'] = results['offset']
        for result in results[results_key]:
            yield result


def get_all_contacts(connection, property_names, property_history=False, last_vid=0):
    """
    # The hubspot.contacts package does not support property histories, so we replace it.
    :param connection:
    :param property_names:
    :param property_history:
    :param last_vid:
    :return:
    """
    property_mode = 'value_only'
    if property_history:
        property_mode = 'value_and_history'

    query_string_args = {'propertyMode': property_mode}
    if last_vid:
        query_string_args['vidOffset'] = last_vid
    if property_names:
        query_string_args['property'] = property_names
    print query_string_args

    data_retriever = PaginatedDataRetriever('contacts', ['vid-offset'])
    url_path = CONTACTS_API_SCRIPT_NAME + '/lists/all/contacts/all'
    contacts_data = data_retriever.get_data(connection, url_path, query_string_args)
    return contacts_data


def get_historied_property_value(data, key, default=None):
    try:
        return data[key]['value']
    except KeyError:
        return default or ''


def get_historied_property_history(data, key, default=None):
    try:
        return data[key]['versions']
    except KeyError:
        return default or []


def map_events_to_icmo_campaigns(hubspot_revenue_plan):
    logger.info("Hubspot:  mapping events for revenue plan %s" % hubspot_revenue_plan.revenue_plan)
    # clear existing Campaigns

    from hubspot_icmo.models import HubspotRevenuePlanCampaignMonthPerformance, \
        HubspotCampaignToICMOCampaign, HubspotRevenuePlanCampaign
    from performance.models import Campaign, CampaignSources

    campaigns = Campaign.objects.filter(revenue_plan=hubspot_revenue_plan.revenue_plan,
                                        source=CampaignSources.HUBSPOT).select_related('segment')
    campaigns_map = defaultdict(dict)
    for campaign in campaigns:
        campaigns_map[campaign.segment.slug][campaign.name] = campaign

    hs_campaigns = HubspotRevenuePlanCampaign.objects.filter(
            hubspot_revenue_plan=hubspot_revenue_plan)
    hs_campaigns_programs = defaultdict(dict)
    for hs_campaign in hs_campaigns:
        hs_campaigns_programs[hs_campaign] = {x.segment.slug: x for x in
                                              hs_campaign.programs.all()}

    hs_to_icmo_map = {x.hubspot_campaign: x.icmo_campaign for x in
                      HubspotCampaignToICMOCampaign.objects.filter(
                              hubspot_campaign__in=hs_campaigns)}

    for hcmp in HubspotRevenuePlanCampaignMonthPerformance.objects.filter(
            hubspot_revenue_plan=hubspot_revenue_plan):
        campaign = hs_to_icmo_map.get(hcmp.hubspot_revenue_plan_campaign)

        # create the iCMO campaign if it doesnt yet exist
        if not campaign:
            program = hs_campaigns_programs[hcmp.hubspot_revenue_plan_campaign].get(
                    hcmp.segment.slug)
            if not program:
                # No map setup
                continue
            campaign = Campaign.objects.create(
                    name=hcmp.hubspot_revenue_plan_campaign.name,
                    source=CampaignSources.HUBSPOT,
                    program=program,
                    revenue_plan=program.revenue_plan,
            )
            HubspotCampaignToICMOCampaign.objects.create(
                    hubspot_campaign=hcmp.hubspot_revenue_plan_campaign, icmo_campaign=campaign)
            hs_to_icmo_map[hcmp.hubspot_revenue_plan_campaign] = campaign

        # set the campaign value
        for field in ('contacts', 'mql', 'sql', 'sales', 'sales_revenue'):
            setattr(campaign, '%s_%s' % (MONTHS_3[hcmp.month - 1], field), getattr(hcmp, field))
    # save all the campaigns
    [campaign.save() for campaign in hs_to_icmo_map.values()]
