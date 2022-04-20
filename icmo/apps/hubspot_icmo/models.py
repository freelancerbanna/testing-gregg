import logging
import urlparse
from datetime import timedelta
from decimal import Decimal

import arrow
import django_rq
import re
import requests
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.functional import cached_property
from django_extensions.db.models import TimeStampedModel
from hubspot.connection import OAuthKey, PortalConnection
from simplejson import JSONDecodeError

from core.fields import DefaultMoneyField
from core.helpers import icmo_reverse
from hubspot_icmo.helpers import get_offset_iterator, get_all_contacts, \
    get_historied_property_value, get_historied_property_history
from leads.models import Program
from performance.models import Campaign
from revenues.models import Segment

logger = logging.getLogger('icmo.%s' % __name__)


class HubspotStages(object):
    SUBSCRIBER = 'subscriber'
    LEAD = 'lead'
    MQL = 'marketingqualifiedlead'
    SQL = 'salesqualifiedlead'
    OPPORTUNITY = 'opportunity'
    CUSTOMER = 'customer'

    choices = (
        (SUBSCRIBER, SUBSCRIBER.title()),
        (LEAD, LEAD.title()),
        (MQL, MQL.title()),
        (SQL, SQL.title()),
        (OPPORTUNITY, OPPORTUNITY.title()),
        (CUSTOMER, CUSTOMER.title()),
    )

    # This order reflects the way iCMO collapses stages
    order = {
        SUBSCRIBER: 1,
        LEAD: 2,
        MQL: 2,
        SQL: 3,
        OPPORTUNITY: 3,
        CUSTOMER: 4,
    }
    order_lookup = {
        1: SUBSCRIBER,
        2: MQL,
        3: SQL,
        4: CUSTOMER
    }

    icmo_map = {
        SUBSCRIBER: 'contacts',
        LEAD: 'mql',
        MQL: 'mql',
        SQL: 'sql',
        OPPORTUNITY: 'sql',
        CUSTOMER: 'sales',
    }


class SegmentMapFields(object):
    INDUSTRY = 'industry'
    ANNUALREVENUE = 'annualrevenue'
    choices = (
        (INDUSTRY, 'Company Industry'),
        (ANNUALREVENUE, 'Company Annual Revenue'),
    )


class HubspotConnection(DirtyFieldsMixin, TimeStampedModel, models.Model):
    company = models.OneToOneField('companies.Company')
    hub_id = models.CharField(max_length=255,
                              help_text="Log into HubSpot to find your Hub ID in the upper "
                                        "righthand corner of the HubSpot application.")
    access_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField(null=True)
    refresh_token = models.CharField(max_length=255)
    last_sync = models.DateTimeField(auto_now=True, blank=True, null=True)
    contacts_last_modified_date = models.DateTimeField(blank=True, null=True)

    @property
    def connected(self):
        if self.access_token:
            return True

    def refresh_access_token(self):
        # http://developers.hubspot.com/docs/methods/auth/refresh_token
        r = requests.post('https://api.hubapi.com/auth/v1/refresh', data=dict(
                refresh_token=self.refresh_token,
                client_id=settings.HUBSPOT_CLIENT_ID,
                grant_type='refresh_token'
        ))
        if r.status_code != 200:
            logger.warn(
                    "Could not refresh access_token for company %s, status_code %d returned" %
                    (self.company, r.status_code)
            )
            return False
        try:
            data = r.json()
        except JSONDecodeError:
            logger.warn("Could not refresh access_token for company %s, "
                        "invalid json response returned" % self.company)
            return False
        self.connect(data['access_token'], data['refresh_token'], data['expires_in'])
        return True

    def connect(self, access_token, refresh_token, expires_in):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = timezone.now() + timedelta(seconds=int(expires_in))
        self.save()
        self.queue_refresh()

    def disconnect(self):
        self.access_token = ''
        self.expires_at = None
        self.refresh_token = ''
        self.contact_list_id = ''
        self.save()

    def get_connection_url(self, request):
        # http://developers.hubspot.com/docs/methods/auth/initiate-oauth
        if not self.hub_id:
            raise ValueError("Missing HubID!")
        if not settings.HUBSPOT_CLIENT_ID:
            raise ValueError("Missing HUBSPOT_CLIENT_ID in settings!")
        return "https://app.hubspot.com/auth/authenticate/?client_id={client_id}&portalId={" \
               "hub_id}&redirect_uri={redirect_uri}&scope=offline+contacts-ro".format(
                client_id=settings.HUBSPOT_CLIENT_ID, hub_id=self.hub_id,
                redirect_uri=request.build_absolute_uri(icmo_reverse('hubspot_setup', request))
        )

    def get_good_industry_count(self):
        qs = self.contacts.all()
        return qs.exclude(Q(industry='Unknown') | Q(industry='')).count(), qs.count()

    def get_good_campaign_count(self):
        qs = self.contacts.all()
        return qs.exclude(campaign_name_guess='Unknown').count(), qs.count()

    def get_good_contacts_count(self):
        qs = self.contacts.all()
        return qs.exclude(
                Q(campaign_name_guess='Unknown')
        ).count(), qs.count()

    def queue_refresh(self):
        # Ensure the token will be refreshed before it expires
        from .tasks import refresh_access_token
        scheduler = django_rq.get_scheduler('default')
        scheduler.enqueue_at(
                arrow.get(self.expires_at).replace(hours=-1).datetime,
                refresh_access_token,
                self.pk
        )

    def queue_data_sync(self):
        from .tasks import sync_hubspot_data
        sync_hubspot_data.delay(self.pk)


# Overall process of a sync
# Update Companies
# Update Deals
# Update Contacts
# Update Segment Map
# Update Campaign Map
# Resync all events, attempting to reuse the existing campaign objects and removing campaigns
# that are no longer required

class HubspotRevenuePlan(TimeStampedModel, DirtyFieldsMixin, models.Model):
    connection = models.ForeignKey('HubspotConnection', related_name='connected_plans')
    revenue_plan = models.OneToOneField('revenues.RevenuePlan')
    segment_mapping_field = models.CharField(max_length=255, default=SegmentMapFields.INDUSTRY,
                                             choices=SegmentMapFields.choices)

    @cached_property
    def map(self):
        if self.segment_mapping_field == SegmentMapFields.INDUSTRY:
            return {x.hs_value_2: x.segment for x in self.segment_map.all()}
        elif self.segment_mapping_field == SegmentMapFields.ANNUALREVENUE:
            return {x.hs_value_1: x.segment for x in self.segment_map.all()}
        raise ValueError(
                "Unknown segment_mapping_field %s" % self.segment_mapping_field)

    def get_contact_segment(self, contact):
        if self.segment_mapping_field == SegmentMapFields.INDUSTRY:
            return self.map.get(contact.industry)
        elif self.segment_mapping_field == SegmentMapFields.ANNUALREVENUE:
            targets = []
            for key in self.map.keys():
                try:
                    targets.append(int(key))
                except ValueError:
                    pass
            targets.sort(reverse=True)
            for target in targets:
                if contact.annualrevenue >= target:
                    return self.map[str(target)]
            return None
        raise ValueError(
                "Unknown segment_mapping_field %s" % self.segment_mapping_field)

    @cached_property
    def get_mapped_campaigns_count(self):
        return HubspotRevenuePlanCampaign.get_mapped_vs_total(self)

    @cached_property
    def mapped_segments_count(self):
        return HubspotRevenuePlanSegmentMap.get_mapped_vs_total(self)

    def is_fully_synced(self):
        return self.mapped_campaigns_count[0] == \
               self.mapped_campaigns_count[1] and \
               self.mapped_industries_count[0] == \
               self.mapped_industries_count[1] and \
               self.good_contacts_count[0] == \
               self.good_contacts_count[1]

    def update_segment_map(self):
        # Clear the old map
        [x.delete() for x in
         HubspotRevenuePlanSegmentMap.objects.filter(hubspot_revenue_plan=self)]
        if self.segment_mapping_field == SegmentMapFields.INDUSTRY:

            # Ensure all industries are present in the mapping table
            contact_industries = HubspotContact.objects.filter(
                    connection=self.connection).values_list('industry', flat=True).distinct()
            for industry in contact_industries:
                HubspotRevenuePlanSegmentMap.objects.get_or_create(
                        hubspot_revenue_plan=self,
                        revenue_plan=self.revenue_plan,
                        mapping_field=self.segment_mapping_field,
                        hs_value_1=industry,
                        hs_value_2=industry.replace('[\W\s]+', '').lower()
                )
            # clear industries no longer present
            # todo this should be part of an overall resync process, as old industries
            # that were mapped to segments and had contact events need to be removed
            [x.delete() for x in
             HubspotRevenuePlanSegmentMap.objects.filter(hubspot_revenue_plan=self).exclude(
                     hs_value_1__in=contact_industries)]
        elif self.segment_mapping_field == SegmentMapFields.ANNUALREVENUE:
            for segment in self.revenue_plan.segments.all():
                HubspotRevenuePlanSegmentMap.objects.get_or_create(
                        hubspot_revenue_plan=self,
                        revenue_plan=self.revenue_plan,
                        mapping_field=self.segment_mapping_field,
                        segment=segment
                )
        # Trigger a campaign refresh
        from .tasks import refresh_and_map_campaigns
        refresh_and_map_campaigns.delay(self.pk)

    def save(self, *args, **kwargs):
        update_map = not self.pk or 'segment_mapping_field' in self.get_dirty_fields()
        super(HubspotRevenuePlan, self).save(*args, **kwargs)
        if update_map:
            self.update_segment_map()


class HubspotContact(models.Model):
    connection = models.ForeignKey(HubspotConnection, related_name='contacts')
    company = models.ForeignKey('companies.Company')
    vid = models.PositiveIntegerField()
    associatedcompanyid = models.CharField(max_length=255, blank=True)
    current_lifecyclestage = models.CharField(max_length=255)
    hs_analytics_first_url = models.URLField(max_length=2048)
    hs_first_conversion_event_name = models.URLField(max_length=2048, blank=True)
    hs_recent_conversion_event_name = models.URLField(max_length=2048, blank=True)
    hs_analytics_source = models.CharField(max_length=255)
    hs_analytics_source_data_1 = models.CharField(max_length=2048)
    hs_analytics_source_data_2 = models.CharField(max_length=2048)
    industry = models.CharField(max_length=255)
    annualrevenue = models.PositiveIntegerField(blank=True, null=True)
    original_source = models.CharField(max_length=255, default='Unknown')
    original_campaign = models.CharField(max_length=255, default='Unknown')
    conversion_event_name = models.CharField(max_length=255, blank=True)
    campaign_name_guess = models.CharField(max_length=255, default='Unknown')
    campaign_name_slug = models.CharField(max_length=255)
    remote_timestamp = models.DateTimeField(null=True)

    @classmethod
    def initialize_contacts(cls, hs_connection):
        # todo implement an update_contacts method that uses recently modified
        # todo this refresh method (and maybe others) should retry automatically if failed
        logger.info("Hubspot:  refreshing contacts for company %s" % hs_connection.company.name)
        authentication_key = OAuthKey(hs_connection.access_token)

        # keep a record of live vids so we can find contacts that have been removed
        live_vids = []
        last_modified_date = None

        # Because the task may time out or otherwise fail, keep a record of where we left off
        last_vid = HubspotContact.objects.values_list('vid', flat=True).order_by(
                '-vid').first() or 0
        hubspot_companies = {
            hc.hs_company_id: dict(industry=hc.industry, annualrevenue=hc.annualrevenue) for hc in
            HubspotCompany.objects.filter(connection=hs_connection)
            }
        with PortalConnection(authentication_key, 'client') as connection:
            for contact in get_all_contacts(
                    connection,
                    ('hs_analytics_first_url', 'hs_analytics_source',
                     'lastmodifieddate', 'associatedcompanyid', 'lifecyclestage',
                     'hs_analytics_source_data_1', 'hs_analytics_source_data_2',
                     'industry', 'first_conversion_event_name',
                     'recent_conversion_event_name', 'lifecyclestage'),
                    property_history=True, last_vid=last_vid):
                props = contact['properties']
                associatedcompanyid = get_historied_property_value(
                        props, 'associatedcompanyid')

                if associatedcompanyid in hubspot_companies:
                    # Grab the annual revenue and industry from the associated company
                    annualrevenue = hubspot_companies[associatedcompanyid]['annualrevenue']
                    industry = hubspot_companies[associatedcompanyid]['industry']
                else:
                    annualrevenue = 0
                    industry = get_historied_property_value(
                            props, 'industry', 'Unknown'
                    )
                obj, created = cls.objects.update_or_create(
                        defaults=dict(
                                associatedcompanyid=associatedcompanyid,
                                hs_analytics_first_url=get_historied_property_value(
                                        props, 'hs_analytics_first_url'
                                ),
                                hs_first_conversion_event_name=get_historied_property_value(
                                        props, 'first_conversion_event_name'
                                ),
                                hs_recent_conversion_event_name=get_historied_property_value(
                                        props, 'recent_conversion_event_name'
                                ),
                                remote_timestamp=cls.get_date(
                                        get_historied_property_value(props, 'lastmodifieddate')
                                ),
                                industry=industry,
                                annualrevenue=annualrevenue,
                                hs_analytics_source=get_historied_property_value(
                                        props, 'hs_analytics_source'
                                ),
                                hs_analytics_source_data_1=get_historied_property_value(
                                        props, 'hs_analytics_source_data_1'
                                ),
                                hs_analytics_source_data_2=get_historied_property_value(
                                        props, 'hs_analytics_source_data_2'
                                ),
                        ),
                        connection=hs_connection, company=hs_connection.company, vid=contact['vid']
                )
                # add events
                obj.events.all().delete()
                for event in get_historied_property_history(props, 'lifecyclestage'):
                    HubspotContactEvent.objects.create(
                            connection=hs_connection,
                            company=hs_connection.company,
                            contact=obj,
                            event_date=cls.get_date(event['timestamp']),
                            event_stage=event['value']
                    )
                live_vids.append(obj.vid)
                # record the latest last modified date for use in later updates
                contact_last_modified_date = cls.get_date(props['lastmodifieddate']['value'])
                if not last_modified_date or contact_last_modified_date > last_modified_date:
                    last_modified_date = contact_last_modified_date
                logger.info("   %s contact with vid %s" % (
                    "Created" if created else "Updated", obj.vid))

        # remove vids not found in hubspot
        cls.objects.filter(connection=hs_connection).exclude(vid__in=live_vids).delete()
        hs_connection.contacts_last_modified_date = last_modified_date
        hs_connection.save()
        return

    @staticmethod
    def get_date(date):
        if date:
            return arrow.get(int(date) / 1000).datetime
        return None

    def get_original_source(self):
        if self.hs_analytics_source == 'OFFLINE':
            try:
                return dict(
                        SALES='Offline (Sales)',
                        IMPORT='Offline (Imported into Hubspot)',
                        API='Offline (Hubspot API)',
                        INTEGRATION="Offline (Integration: %s)" %
                                    self.hs_analytics_source_data_2 or 'Offline (Integration: '
                                                                       'Unknown)',
                )[self.hs_analytics_source_data_1]
            except KeyError:
                return 'Offline (Unknown)'
        return self.hs_analytics_source.replace("_", " ").title()

    def get_original_campaign_name(self):
        # These are direct campaign name links
        # http://knowledge.hubspot.com/articles/kcs_article/reports/what-do-the-properties
        # -original-source-data-1-and-2-mean
        try:
            return dict(
                    SOCIAL_MEDIA=self.hs_analytics_source_data_2,
                    EMAIL_MARKETING=self.hs_analytics_source_data_1,
                    PAID_SEARCH=self.hs_analytics_source_data_1,
                    OTHER_CAMPAIGNS=self.hs_analytics_source_data_1,
            )[self.hs_analytics_source]
        except KeyError:
            pass

        # First URLs
        if 'utm_campaign' in self.hs_analytics_first_url:
            url = urlparse.urlparse(self.hs_analytics_first_url)
            query = urlparse.parse_qs(url.query)
            if 'utm_campaign' in query:
                return query['utm_campaign'].pop()

        return 'Unknown'

    @classmethod
    def get_industries(cls):
        return cls.objects.all().values('industry').annotate(num=Count('pk')).order_by('-num')

    @classmethod
    def get_original_sources(cls):
        return cls.objects.all().values('hs_analytics_source').annotate(num=Count('pk')).order_by(
                '-num')

    @classmethod
    def get_campaign_names(cls):
        return cls.objects.all().values('campaign_name_guess').annotate(
                num=Count('pk')).order_by('-num')

    def get_campaign_name_slug(self):
        return re.sub('\W', '', self.campaign_name_guess).lower()

    def save(self, *args, **kwargs):
        # self.campaign_name_guess = self.get_campaign_name().title()
        self.campaign_name_guess = self.get_original_source()
        if self.campaign_name_guess.startswith('Offline') and self.hs_first_conversion_event_name:
            self.campaign_name_guess = "%s - Converted" % self.campaign_name_guess
        self.campaign_name_slug = self.get_campaign_name_slug()
        self.original_source = self.get_original_source()
        self.conversion_event_name = self.hs_first_conversion_event_name
        super(HubspotContact, self).save(*args, **kwargs)


class HubspotContactEvent(models.Model):
    connection = models.ForeignKey(HubspotConnection, related_name='events')
    company = models.ForeignKey('companies.Company')
    contact = models.ForeignKey('HubspotContact', related_name='events')
    event_date = models.DateTimeField()
    event_stage = models.CharField(max_length=50, choices=HubspotStages.choices)

    def __unicode__(self):
        return "%s - %s" % (self.contact.vid, self.event_stage)


class HubspotDeal(models.Model):
    connection = models.ForeignKey(HubspotConnection, related_name='deals')
    company = models.ForeignKey('companies.Company')
    contact = models.ForeignKey(HubspotContact, blank=True, null=True)
    deal_id = models.CharField(max_length=255)
    contact_vid = models.CharField(max_length=255, blank=True)
    hs_company_id = models.CharField(max_length=255, blank=True)
    dealname = models.CharField(max_length=255)
    amount = DefaultMoneyField(decimal_places=2)
    dealstage = models.CharField(max_length=255)
    dealstage_last_modified = models.DateTimeField()
    closedwon_date = models.DateTimeField(blank=True, null=True)

    @classmethod
    def refresh_deals(cls, hs_connection):
        logger.info("Hubspot:  refreshing deals for company %s" % hs_connection.company)

        authentication_key = OAuthKey(hs_connection.access_token)

        with PortalConnection(authentication_key, 'client') as connection:
            for deal in get_offset_iterator(connection, '/deals/v1/deal/recent/modified'):
                if not all([x in deal['properties'] for x in ('amount', 'dealstage')]):
                    continue
                if not deal['properties']['amount']['value'] or not deal['properties'][
                    'dealstage']:
                    continue
                contact_vid = ''
                hs_company_id = ''
                if 'associatedVids' in deal['associations'] \
                        and deal['associations']['associatedVids']:
                    contact_vid = deal['associations']['associatedVids'][0]
                if 'associatedCompanyIds' in deal['associations'] \
                        and deal['associations']['associatedCompanyIds']:
                    hs_company_id = deal['associations']['associatedCompanyIds'][0]

                contact = None
                if contact_vid:
                    contact = HubspotContact.objects.filter(vid=contact_vid).first()
                elif hs_company_id:
                    contact = HubspotContact.objects.order_by('vid').filter(
                            associatedcompanyid=hs_company_id).first()

                if not contact:
                    logger.warning("Could not find a contact for deal id %s" % deal['dealId'])
                    continue
                closedwon_date = None
                for version in deal['properties']['dealstage']['versions']:
                    if version['value'] == 'closedwon':
                        closedwon_date = arrow.get(version['timestamp'] / 1000).datetime

                cls.objects.update_or_create(
                        defaults=dict(
                                contact_vid=contact_vid,
                                hs_company_id=hs_company_id,
                                # dealname=deal['properties']['dealname']['value'],
                                amount=Decimal(deal['properties']['amount']['value']),
                                dealstage=deal['properties']['dealstage']['value'],
                                closedwon_date=closedwon_date,
                                dealstage_last_modified=arrow.get(
                                        deal['properties']['dealstage'][
                                            'timestamp'] / 1000).datetime,
                                contact=contact,
                        ),
                        company=hs_connection.company,
                        connection=hs_connection,
                        deal_id=deal['dealId']
                )


class HubspotCompany(models.Model):
    connection = models.ForeignKey(HubspotConnection, related_name='hs_companies')
    company = models.ForeignKey('companies.Company')
    hs_company_id = models.CharField(max_length=255)
    name = models.CharField(max_length=1024)
    annualrevenue = models.IntegerField(blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)

    @classmethod
    def refresh_companies(cls, hs_connection):
        logger.info(
                "Hubspot:  refreshing HubSpot companies for company %s" % hs_connection.company)

        authentication_key = OAuthKey(hs_connection.access_token)

        with PortalConnection(authentication_key, 'client') as connection:
            for company in get_offset_iterator(connection,
                                               '/companies/v2/companies/recent/modified',
                                               query_dict=dict(property=('annualrevenue',))):
                props = company['properties']
                annual_revenue = get_historied_property_value(props, 'annualrevenue')
                if annual_revenue:
                    try:
                        annual_revenue = int(annual_revenue.replace(',', '').strip())
                    except ValueError:
                        annual_revenue = None
                else:
                    annual_revenue = None

                cls.objects.update_or_create(
                        defaults=dict(
                                name=get_historied_property_value(props, 'name'),
                                industry=get_historied_property_value(props, 'industry'),
                                annualrevenue=annual_revenue,
                                state=get_historied_property_value(props, 'state'),
                                city=get_historied_property_value(props, 'city'),
                                country=get_historied_property_value(props, 'country'),
                        ),
                        company=hs_connection.company,
                        connection=hs_connection,
                        hs_company_id=company['companyId']
                )

    @classmethod
    def update_contact_revenue(cls, hs_connection):
        revenues = {x.hs_company_id: x.annualrevenue for x in
                    cls.objects.filter(connection=hs_connection)}
        for contact in HubspotContact.objects.filter(connection=hs_connection):
            contact.annualrevenue = revenues.get(contact.associatedcompanyid)
            contact.save()


class HubspotRevenuePlanCampaign(models.Model):
    class Meta:
        ordering = ('name',)

    hubspot_revenue_plan = models.ForeignKey(HubspotRevenuePlan)
    revenue_plan = models.ForeignKey('revenues.RevenuePlan')
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    programs = models.ManyToManyField('leads.Program')

    @cached_property
    def event_count(self):
        return HubspotContactEvent.objects.filter(
                connection=self.hubspot_revenue_plan.connection,
                contact__campaign_name_guess=self.name
        ).exclude(event_stage='').count()

    @cached_property
    def event_breakdown(self):
        events = HubspotContactEvent.objects.filter(
                connection=self.hubspot_revenue_plan.connection,
                contact__campaign_name_guess=self.name
        ).exclude(event_stage='').order_by('event_stage').distinct().values(
                'event_stage').annotate(Count('pk'))
        output = {
            'customer': 0,
            'lead': 0,
            'marketingqualifiedlead': 0,
            'salesqualifiedlead': 0,
            'opportunity': 0,
            'subscriber': 0
        }

        for item in events:
            output[item['event_stage']] = item['pk__count']
        return output

    # create campaigns
    @staticmethod
    def _get_blank_campaign_events_dict():
        return {
            y: dict(contacts=0, mql=0, sql=0, sales=0, sales_revenue=0) for y in range(1, 13)
            }

    @classmethod
    def refresh_campaigns(cls, hubspot_revenue_plan):
        """

        :param hubspot_revenue_plan:
        """
        logger.info(
                "Hubspot:  refreshing campaigns for revenue plan %s" %
                hubspot_revenue_plan.revenue_plan)

        start_year = hubspot_revenue_plan.revenue_plan.plan_year
        start_month = hubspot_revenue_plan.revenue_plan.company.fiscal_year_start
        cutoff_start = arrow.get(start_year, start_month, 1).datetime
        cutoff_end = arrow.get(start_year, start_month, 1).replace(years=+1).datetime

        events_qs = HubspotContactEvent.objects.filter(
                connection=hubspot_revenue_plan.connection, event_date__gte=cutoff_start,
                event_date__lt=cutoff_end).select_related('contact')

        # remove campaigns that no longer appear in the contacts list
        [x.delete() for x in cls.objects.filter(hubspot_revenue_plan=hubspot_revenue_plan).exclude(
                slug__in=events_qs.order_by('contact__campaign_name_slug').values_list(
                        'contact__campaign_name_slug', flat=True).distinct())]
        # cache the list of campaigns
        campaigns = {x.slug: x for x in
                     cls.objects.filter(hubspot_revenue_plan=hubspot_revenue_plan)}

        for event in events_qs.order_by('contact', 'event_date'):
            # Create the Campaign if it doesnt exist yet
            campaign_slug = event.contact.campaign_name_slug
            if campaign_slug not in campaigns:
                hs_campaign = cls.objects.create(
                        hubspot_revenue_plan=hubspot_revenue_plan,
                        revenue_plan=hubspot_revenue_plan.revenue_plan,
                        name=event.contact.campaign_name_guess,
                        slug=event.contact.campaign_name_slug
                )
                campaigns[campaign_slug] = hs_campaign

    @classmethod
    def refresh_campaigns_performance(cls, hubspot_revenue_plan):
        """

        :param hubspot_revenue_plan:
        """
        logger.info(
                "Hubspot:  refreshing campaigns for revenue plan %s" %
                hubspot_revenue_plan.revenue_plan)

        start_year = hubspot_revenue_plan.revenue_plan.plan_year
        start_month = hubspot_revenue_plan.revenue_plan.company.fiscal_year_start
        cutoff_start = arrow.get(start_year, start_month, 1).datetime
        cutoff_end = arrow.get(start_year, start_month, 1).replace(years=+1).datetime

        events_qs = HubspotContactEvent.objects.filter(
                connection=hubspot_revenue_plan.connection, event_date__gte=cutoff_start,
                event_date__lt=cutoff_end).select_related('contact')

        # cache the list of campaigns
        campaigns = {x.slug: x for x in
                     cls.objects.filter(hubspot_revenue_plan=hubspot_revenue_plan)}

        # cache the list of segments
        segments = {x.slug: x for x in hubspot_revenue_plan.revenue_plan.segments.all()}

        # prepare to temporarily store the monthly campaign events
        # cmapaign_events['segmentslug']['campaignslug'][1]['mql']=0 etc
        campaign_events = dict()
        for segment_slug in segments.keys():
            campaign_events[segment_slug] = {
                x: cls._get_blank_campaign_events_dict()
                for x in campaigns.keys()
                }
        last_stage = None
        segment = None
        contact = None
        for event in events_qs.order_by('contact', 'event_date'):
            # Reset the stage when the contact changes
            if event.contact != contact:
                segment = hubspot_revenue_plan.get_contact_segment(event.contact)
                # can't map to unmapped segments
                if not segment:
                    # print 'skipping no segment'
                    continue
                contact = event.contact
                last_stage = None

            # Skip blank event stages
            if not event.event_stage:
                # print 'skipping no event stage'
                continue

            # Handle Stage Progressions & Tally the Event

            # Things to keep in mind when counting events
            # 1.  We treat opportunity and sql the same, and lead and mql.
            # 2.  These should not be double counted
            # 3.  Implicit stages should be counted (ie, subscribe to customer = implicit mql
            # and sql)
            # 4. There is backwards progression, ex:  Subscriber, MQL, SQL, Subscriber
            # 4a. Backwards progression after a Customer stage is a new lifecycle
            # 4b. Backwards progression before a Customer stage should count negatively

            campaign_slug = event.contact.campaign_name_slug
            icmo_stage = HubspotStages.icmo_map[event.event_stage]
            current_stage = event.event_stage
            current_stage_order_num = HubspotStages.order[event.event_stage]
            last_stage_order_num = HubspotStages.order.get(last_stage, 1)

            # skip duplicate stages
            if current_stage == HubspotStages.MQL and last_stage == HubspotStages.LEAD:
                # print 'skipping dupe1'
                continue
            elif current_stage == HubspotStages.OPPORTUNITY and last_stage == \
                    HubspotStages.SQL:
                # print 'skipping dupe2'
                continue

            # handle backwards progression
            if last_stage_order_num > current_stage_order_num:
                # Anything after customer is a new lifecycle
                if last_stage == HubspotStages.CUSTOMER:
                    last_stage = None
                # Anything going backwards before customer counts negative, so cycle back
                # and apply a negative value to all the events we're backtracking, including
                # this one as it will be readded after
                else:
                    backwards_gap = last_stage_order_num - current_stage_order_num
                    for i in range(current_stage_order_num,
                                   current_stage_order_num + backwards_gap + 1):
                        backwards_stage = HubspotStages.icmo_map[HubspotStages.order_lookup[i]]
                        campaign_events[segment.slug][campaign_slug][event.event_date.month][
                            backwards_stage] -= 1

            # We don't actually record the customer stage as a sale, as that is handled by deals
            # Otherwise there would be far more sales than revenue (mulitple customres per deal)
            if current_stage == HubspotStages.CUSTOMER:
                # print 'skipping customer'
                continue

            # record this stage
            campaign_events[segment.slug][campaign_slug][event.event_date.month][icmo_stage] += 1

            # record implicit stages
            for order_num in range(HubspotStages.order.get(last_stage, 1),
                                   HubspotStages.order[event.event_stage]):
                implied_stage = HubspotStages.icmo_map[HubspotStages.order_lookup[order_num]]
                if current_stage == HubspotStages.CUSTOMER:
                    continue
                campaign_events[segment.slug][campaign_slug][event.event_date.month][
                    implied_stage] += 1

        # Calculate sales revenue
        for deal in HubspotDeal.objects.filter(connection=hubspot_revenue_plan.connection,
                                               dealstage='closedwon',
                                               closedwon_date__gte=cutoff_start,
                                               closedwon_date__lt=cutoff_end):
            campaign_slug = deal.contact.campaign_name_slug
            segment = hubspot_revenue_plan.get_contact_segment(deal.contact)
            if not segment:
                continue
            campaign_events[segment.slug][campaign_slug][deal.closedwon_date.month]['sales'] += 1
            campaign_events[segment.slug][campaign_slug][deal.closedwon_date.month][
                'sales_revenue'] += deal.amount

        # Clear old campaign metrics
        HubspotRevenuePlanCampaignMonthPerformance.objects.filter(
                connection=hubspot_revenue_plan.connection)
        # Save all metrics
        for segment_slug, campaign_event_campaigns in campaign_events.items():
            for campaign_slug, campaign_values in campaign_event_campaigns.items():
                for month, month_values in campaign_values.items():
                    HubspotRevenuePlanCampaignMonthPerformance.objects.update_or_create(
                            defaults=dict(
                                    contacts=month_values['contacts'],
                                    mql=month_values['mql'],
                                    sql=month_values['sql'],
                                    sales=month_values['sales'],
                                    sales_revenue=month_values['sales_revenue'],
                            ),
                            connection=hubspot_revenue_plan.connection,
                            hubspot_revenue_plan=hubspot_revenue_plan,
                            hubspot_revenue_plan_campaign=campaigns[campaign_slug],
                            segment=segments[segment_slug],
                            month=month
                    )

    @property
    def segment_program_map(self):
        return {x.segment.slug: x.slug for x in self.programs.all()}

    @classmethod
    def get_mapped_vs_total(cls, revenue_plan):
        qs = cls.objects.filter(revenue_plan=revenue_plan)
        return qs.exclude(hubspotcampaignprogrammap=None).count(), qs.count()

    def __unicode__(self):
        return self.name

    def delete(self, using=None):
        [x.icmo_campaign.delete() for x in self.icmo_campaigns.all()]
        [x.delete() for x in self.icmo_campaigns.all()]
        super(HubspotRevenuePlanCampaign, self).delete(using=None)


class HubspotRevenuePlanCampaignMonthPerformance(TimeStampedModel, models.Model):
    class Meta:
        ordering = ('hubspot_revenue_plan_campaign', 'month')

    connection = models.ForeignKey(HubspotConnection)
    hubspot_revenue_plan = models.ForeignKey(HubspotRevenuePlan)
    hubspot_revenue_plan_campaign = models.ForeignKey(HubspotRevenuePlanCampaign)
    segment = models.ForeignKey('revenues.Segment')
    month = models.PositiveSmallIntegerField()
    contacts = models.PositiveSmallIntegerField(default=0)
    mql = models.PositiveSmallIntegerField(default=0)
    sql = models.PositiveSmallIntegerField(default=0)
    sales = models.PositiveSmallIntegerField(default=0)
    sales_revenue = DefaultMoneyField(default=0)


class HubspotRevenuePlanSegmentMap(models.Model):
    class Meta:
        ordering = ('hs_value_1',)

    hubspot_revenue_plan = models.ForeignKey(HubspotRevenuePlan, related_name='segment_map')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan')
    mapping_field = models.CharField(max_length=255, choices=SegmentMapFields.choices)
    hs_value_1 = models.CharField(max_length=255, blank=True)  # 1000, Financial Services
    hs_value_2 = models.CharField(max_length=255, blank=True)  # financialservices
    segment = models.ForeignKey('revenues.Segment', blank=True, null=True)

    @classmethod
    def get_mapped_vs_total(cls, hs_revenue_plan):
        qs = cls.objects.filter(hubspot_revenue_plan=hs_revenue_plan)
        unmapped, total = 0, 0
        if hs_revenue_plan.segment_mapping_field == SegmentMapFields.INDUSTRY:
            unmapped, total = qs.exclude(segment=None).count(), qs.count()
        elif hs_revenue_plan.segment_mapping_field == SegmentMapFields.ANNUALREVENUE:
            unmapped, total = qs.exclude(hs_value_1='').count(), qs.count()
        return unmapped, total


class HubspotCampaignToICMOCampaign(models.Model):
    hubspot_campaign = models.ForeignKey(HubspotRevenuePlanCampaign, related_name='icmo_campaigns')
    icmo_campaign = models.ForeignKey('performance.Campaign', related_name='hubspot_campaigns')
