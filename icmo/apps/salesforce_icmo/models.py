import logging
import re
from collections import defaultdict

import arrow
import requests
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.functional import cached_property
from django_extensions.db.models import TimeStampedModel
from pytz import common_timezones
from simple_salesforce import SalesforceExpiredSession

from core.helpers import MONTHS_3
from performance.models import Campaign, CampaignSources
from periods.tasks import update_or_create_month_periods_from_campaign
from salesforce_icmo.helpers import get_picklist_values, SalesforceAPIWrapper, build_sfdc_query, \
    resolve_campaign_value, resolve_segment_value, resolve_opportunity_created_date

logger = logging.getLogger('icmo.%s' % __name__)

RE_SLUG = re.compile(r'[\W\s]+')


class ProgramMapTypes(object):
    SOURCE = 'source'
    CAMPAIGN = 'campaign'
    choices = (
        (SOURCE, 'Source'),
        (CAMPAIGN, 'Campaign')
    )


class SegmentFieldTypes(object):
    TEXT_MATCH = 'text_match'
    NUMERIC = 'numeric'
    choices = (
        (TEXT_MATCH, 'Text Match'),
        (NUMERIC, 'Numeric')
    )


class SalesforceConnection(DirtyFieldsMixin, TimeStampedModel, models.Model):
    company = models.OneToOneField('companies.Company')
    access_token = models.CharField(max_length=255, blank=True)
    expires_at = models.DateTimeField(null=True)
    refresh_token = models.CharField(max_length=255, blank=True)
    id_url = models.URLField(max_length=2048, blank=True)
    instance_url = models.URLField(max_length=2048, blank=True)
    signature = models.CharField(max_length=255, blank=True)
    issued_at = models.CharField(max_length=255, blank=True)
    last_sync = models.DateTimeField(auto_now=True, blank=True, null=True)

    segment_field_type = models.CharField(max_length=255,
                                          choices=SegmentFieldTypes.choices)
    lead_segment_field = models.CharField(max_length=255)
    account_segment_field = models.CharField(max_length=255, blank=True)
    opportunity_segment_field = models.CharField(max_length=255, blank=True)

    lead_campaign_field = models.CharField(max_length=255, blank=True)
    opportunity_campaign_field = models.CharField(max_length=255, blank=True)
    account_campaign_field = models.CharField(max_length=255, blank=True)
    campaign_fallback_to_lead_source = models.BooleanField(default=True)

    sfdc_statuses_to_ignore = ArrayField(models.CharField(max_length=255, blank=True), blank=True,
                                         null=True)
    sfdc_end_statuses = ArrayField(models.CharField(max_length=255, blank=True), blank=True,
                                   null=True)

    is_syncing = models.BooleanField(default=False)

    salesforce_url = models.URLField(
        blank=True,
        help_text="The base URL of your salesforce account. Ex: https://na10.salesforce.com/")

    salesforce_timezone = models.CharField(
        max_length=50,
        choices=[(x, x) for x in common_timezones],
        default='UTC', help_text="Your preferred timezone for viewing "
                                 "Salesforce data.  This should be set "
                                 "to the "
                                 "same master timezone you use in "
                                 "Salesforce "
                                 "so that reports in Salesforce line up "
                                 "with "
                                 "reports in iCMO")
    currency_conversion = models.BooleanField(
        default=False,
        help_text="Enable this if you are using currency conversion in your Salesforce account.")
    take_oldest_opportunity_date = models.BooleanField(
        default=True,
        help_text="Sometimes the close date on an opportunity may be set to a date earlier than "
                  "the create date, for example when recording past sales.  When enabled this "
                  "will ensure that the SQL (and the MQL if virtual) will be set to the same "
                  "date as the Close Date if it is earlier.")

    def mark_syncing(self):
        if not self.is_syncing:
            self.is_syncing = True
            self.save()

    def mark_synced(self):
        if self.is_syncing:
            self.is_syncing = False
            self.save()

    @property
    def setup_complete(self):
        return self.connected and self.lead_segment_field and self.segment_field_type and \
               self.lead_campaign_field and self.sfdc_end_statuses

    @property
    def connected(self):
        if self.access_token:
            return True

    @property
    def api(self):
        if not hasattr(self, '_api'):
            self._api = SalesforceAPIWrapper(instance_url=self.instance_url,
                                             session_id=self.access_token, sfc=self)
        return self._api

    @cached_property
    def lead_field_choices(self):
        response = self.api.Lead.describe()
        return [(f['name'], f['type']) for f in response['fields']]

    @cached_property
    def account_field_choices(self):
        response = self.api.Account.describe()
        return [(f['name'], f['type']) for f in response['fields']]

    @cached_property
    def opportunity_field_choices(self):
        response = self.api.Opportunity.describe()
        return [(f['name'], f['type']) for f in response['fields']]

    @cached_property
    def statuses(self):
        return get_picklist_values(self, 'Lead', 'Status') + \
               get_picklist_values(self, 'Opportunity', 'StageName')

    @cached_property
    def filtered_statuses(self):
        statuses_to_ignore = [x.lower() for x in self.sfdc_statuses_to_ignore] or []
        return [x for x in self.statuses if x.lower() not in statuses_to_ignore]

    def naive_sfdc_date_to_utc(self, sfdc_date_str):
        return arrow.get(sfdc_date_str) \
            .replace(tzinfo=self.salesforce_timezone).to('UTC').datetime

    def query(self, q):
        try:
            return self.api.query(q)
        except SalesforceExpiredSession:
            self.refresh_access_token()
            return self.query(q)

    def refresh_access_token(self):
        logger.info("Salesforce:  refreshing token for sfc id %d" % self.id)
        r = requests.post(settings.SFDC_OAUTH_TOKEN_ENDPOINT, data=dict(
            grant_type='refresh_token',
            client_id=settings.SFDC_CLIENT_ID,
            client_secret=settings.SFDC_CLIENT_SECRET,
            refresh_token=self.refresh_token
        ))
        if r.status_code != 200:
            logger.warning("Salesforce: Could not refresh token for sfc id %d" % self.id)
            self.access_token = ''
            self._api = None
            self.save()
            return False
        data = r.json()
        self._api = None
        self.access_token = data.get('access_token')
        self.id_url = data.get('id')
        self.instance_url = data.get('instance_url')
        self.signature = data.get('signature')
        self.issued_at = data.get('issued_at')
        self.save()
        logger.info("Salesforce:  token refreshed for sfc id %d" % self.id)
        return True

    def connect(self, code):
        r = requests.post(settings.SFDC_OAUTH_TOKEN_ENDPOINT, data=dict(
            grant_type='authorization_code',
            client_id=settings.SFDC_CLIENT_ID,
            client_secret=settings.SFDC_CLIENT_SECRET,
            redirect_uri=settings.SFDC_REDIRECT_URI,
            code=code
        ))
        if r.status_code != 200:
            raise ValueError("Could not connect this Salesforce Account")
        data = r.json()
        self.access_token = data.get('access_token')
        self.refresh_token = data.get('refresh_token')
        self.id_url = data.get('id')
        self.instance_url = data.get('instance_url')
        self.signature = data.get('signature')
        self.issued_at = data.get('issued_at')
        self.save()

    def disconnect(self):
        self.access_token = ''
        self.refresh_token = ''
        self.id_url = ''
        self.instance_url = ''
        self.signature = ''
        self.issued_at = ''
        self.save()

    @staticmethod
    def get_connection_url():
        return "{0:s}?response_type=code&client_id={1:s}&redirect_uri={" \
               "2:s}&display=popup&scope=api%20refresh_token" \
            .format(settings.SFDC_OAUTH_AUTHORIZE_ENDPOINT, settings.SFDC_CLIENT_ID,
                    settings.SFDC_REDIRECT_URI
                    )

    def queue_data_sync(self):
        from .tasks import sync_salesforce_data
        sync_salesforce_data.delay(self.pk)

    @cached_property
    def has_maps(self):
        return any([x.fully_imported for x in self.connected_plans.all()])

    @cached_property
    def earliest_date(self):
        return arrow.get(min([x.start_datetime for x in self.connected_plans.all()])).replace(
            years=-1).datetime

    def __unicode__(self):
        return "%s SFDC Connection" % self.company


class SalesforceAccount(models.Model):
    connection = models.ForeignKey(SalesforceConnection, related_name='accounts')
    sfdc_id = models.CharField(max_length=255)
    sfdc_name = models.CharField(max_length=255, blank=True)
    sfdc_account_source = models.CharField(max_length=255, blank=True)
    sfdc_created_date = models.DateTimeField()

    segment_field_text_value = models.CharField(max_length=255, blank=True)
    segment_field_numeric_value = models.DecimalField(max_digits=15, decimal_places=2,
                                                      null=True)
    campaign_field_value = models.CharField(max_length=255, blank=True)

    @classmethod
    def refresh_accounts(cls, sfc):
        cls.objects.filter(connection=sfc).delete()
        query = build_sfdc_query(
            sfc,
            ('Id', 'Name', 'AccountSource', 'CreatedDate'),
            'Account'
        )
        data = sfc.api.query_all(query)
        for account in data['records']:
            obj = SalesforceAccount(
                connection=sfc,
                sfdc_id=account['Id'],
                sfdc_account_source=account['AccountSource'] or '',
                sfdc_name=account['Name'],
                sfdc_created_date=account['CreatedDate'],
            )
            if sfc.account_segment_field:
                if sfc.segment_field_type == SegmentFieldTypes.TEXT_MATCH:
                    obj.segment_field_text_value = account[sfc.account_segment_field] or ''
                else:
                    obj.segment_field_numeric_value = account[sfc.account_segment_field]
            if sfc.account_campaign_field:
                obj.campaign_field_value = account[sfc.account_campaign_field] or ''

            # create the new SalesforceAccount
            obj.save()


class SalesforceOpportunity(models.Model):
    connection = models.ForeignKey(SalesforceConnection, related_name='opportunities')
    salesforce_account = models.ForeignKey(SalesforceAccount, blank=True, null=True)
    sfdc_id = models.CharField(max_length=255)
    sfdc_name = models.CharField(max_length=255, blank=True)
    sfdc_account_id = models.CharField(max_length=255, blank=True, null=True)
    sfdc_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    sfdc_close_date = models.DateTimeField(null=True)
    sfdc_stage_name = models.CharField(max_length=255)
    sfdc_created_date = models.DateTimeField()

    segment_field_text_value = models.CharField(max_length=255, blank=True)
    segment_field_numeric_value = models.DecimalField(max_digits=15, decimal_places=2,
                                                      null=True)

    campaign_field_value = models.CharField(max_length=255, blank=True)

    @classmethod
    def refresh_opportunities(cls, sfc):
        cls.objects.filter(connection=sfc).delete()
        accounts = {x.sfdc_id: x for x in SalesforceAccount.objects.filter(connection=sfc)}
        query = build_sfdc_query(
            sfc,
            ('Id', 'AccountId', 'Name', 'Amount', 'CloseDate', 'LeadSource', 'StageName',
             'CreatedDate'),
            'Opportunity'
        )
        data = sfc.api.query_all(query)

        for opportunity in data['records']:
            obj = SalesforceOpportunity(
                connection=sfc,
                sfdc_id=opportunity['Id'],
                sfdc_account_id=opportunity['AccountId'],
                sfdc_name=opportunity['Name'],
                sfdc_amount=opportunity['Amount'],
                # CloseDate is stored as a naive datetime.  Translate it to the company timezone
                sfdc_close_date=sfc.naive_sfdc_date_to_utc(opportunity['CloseDate']),
                sfdc_stage_name=opportunity['StageName'],
                sfdc_created_date=opportunity['CreatedDate'],
                salesforce_account=accounts.get(opportunity['AccountId']),
                campaign_field_value=opportunity['LeadSource'] or ''
            )
            if sfc.opportunity_segment_field:
                if sfc.segment_field_type == SegmentFieldTypes.TEXT_MATCH:
                    obj.segment_field_text_value = opportunity[sfc.opportunity_segment_field] or ''
                else:
                    obj.segment_field_numeric_value = opportunity[sfc.opportunity_segment_field]

            if sfc.opportunity_campaign_field and opportunity[sfc.opportunity_campaign_field]:
                obj.campaign_field_value = opportunity[sfc.opportunity_campaign_field] or ''

            # create the new SalesforceOpportunity
            obj.save()


class SalesforceLead(models.Model):
    connection = models.ForeignKey(SalesforceConnection, related_name='leads')
    salesforce_account = models.ForeignKey(SalesforceAccount, blank=True, null=True,
                                           related_name='salesforce_lead')
    salesforce_opportunity = models.ForeignKey(SalesforceOpportunity, blank=True, null=True,
                                               related_name='salesforce_lead')
    sfdc_id = models.CharField(max_length=255)
    sfdc_name = models.CharField(max_length=255, blank=True)
    sfdc_company = models.CharField(max_length=255, blank=True)
    sfdc_status = models.CharField(max_length=255)
    sfdc_converted_date = models.DateTimeField(null=True)
    sfdc_converted_account_id = models.CharField(max_length=255)
    sfdc_converted_contact_id = models.CharField(max_length=255)
    sfdc_converted_opportunity_id = models.CharField(max_length=255)
    sfdc_created_date = models.DateTimeField()

    segment_field_text_value = models.CharField(max_length=255, blank=True)
    segment_field_numeric_value = models.DecimalField(max_digits=15, decimal_places=2,
                                                      null=True)
    campaign_field_value = models.CharField(max_length=255, blank=True)

    @classmethod
    def refresh_leads(cls, sfc):
        cls.objects.filter(connection=sfc).delete()
        accounts = {x.sfdc_id: x for x in SalesforceAccount.objects.filter(connection=sfc)}
        opportunities = {x.sfdc_id: x for x in
                         SalesforceOpportunity.objects.filter(connection=sfc)}
        query = 'SELECT Id, Name, Company, Status, LeadSource, ConvertedDate, ' \
                'ConvertedAccountId, ConvertedContactId, ConvertedOpportunityId, CreatedDate, ' \
                '%s' % sfc.lead_segment_field
        if sfc.lead_campaign_field and sfc.lead_campaign_field != 'LeadSource':
            query = "%s, %s" % (query, sfc.lead_campaign_field)
        query = "%s FROM Lead WHERE IsDeleted = False AND CreatedDate >= %s" % (
            query, arrow.get(sfc.earliest_date)
        )
        data = sfc.api.query_all(query)
        for lead in data['records']:
            obj = SalesforceLead(
                connection=sfc,
                sfdc_id=lead['Id'],
                sfdc_status=lead['Status'],
                sfdc_name=lead['Name'],
                sfdc_company=lead['Company'],
                sfdc_converted_date=lead['ConvertedDate'],
                sfdc_converted_account_id=lead['ConvertedAccountId'] or '',
                sfdc_converted_contact_id=lead['ConvertedContactId'] or '',
                sfdc_converted_opportunity_id=lead['ConvertedOpportunityId'] or '',
                sfdc_created_date=lead['CreatedDate'],
                salesforce_account=accounts.get(lead['ConvertedAccountId']),
                salesforce_opportunity=opportunities.get(lead['ConvertedOpportunityId']),
                campaign_field_value=lead[sfc.lead_campaign_field] or lead['LeadSource'] or '',
            )
            if sfc.segment_field_type == SegmentFieldTypes.TEXT_MATCH:
                obj.segment_field_text_value = lead[sfc.lead_segment_field] or ''
            else:
                obj.segment_field_numeric_value = lead[sfc.lead_segment_field]

            # create the new SalesforceLead
            obj.save()


class SalesforceRevenuePlan(TimeStampedModel, DirtyFieldsMixin, models.Model):
    connection = models.ForeignKey(SalesforceConnection, related_name='connected_plans')
    revenue_plan = models.OneToOneField('revenues.RevenuePlan')

    def get_contact_segment_value(self, contact):
        if self.connection.segment_field_type == SegmentFieldTypes.TEXT_MATCH:
            return self.map.get(contact.segment_field_text_value_slug)
        elif self.connection.segment_field_type == SegmentFieldTypes.NUMERIC:
            targets = []
            for key in self.map.keys():
                try:
                    targets.append(int(key))
                except ValueError:
                    pass
            targets.sort(reverse=True)
            for target in targets:
                if contact.segment_field_numeric_value >= target:
                    return self.map[str(target)]
            return None
        raise ValueError(
            "Unknown segment_mapping_field %s" % self.segment_mapping_field)

    @property
    def fully_imported(self):
        mapped, total = self.mapped_items_count
        return mapped == total

    def get_segment_value_options(self):
        return [(RE_SLUG.sub('', x), x)
                for x in
                SalesforceEvent.get_segment_text_values_by_plan(self)]

    def get_source_value_options(self):
        return [(RE_SLUG.sub('', x), x)
                for x in
                SalesforceEvent.get_sources_by_plan(self)]

    @staticmethod
    def _aggregate_mapped_events(events):
        output = dict(mql=0, sql=0, sales=0, sales_revenue=0)
        for source_events in events.values():
            for month_events in source_events.values():
                for performance in month_events.values():
                    for key, val in performance.items():
                        output[key] += val
        return output

    @cached_property
    def mapped_items_count(self):
        total = SalesforceRevenuePlanMapEntry.objects.filter(salesforce_revenue_plan=self).count()
        mapped = SalesforceRevenuePlanMapEntry.objects.filter(salesforce_revenue_plan=self) \
            .exclude(campaign=None).count()
        return mapped, total

    @cached_property
    def mapped_events_total(self):
        mapped_events, unmapped_events = self.mapped_and_unmapped_events
        return self._aggregate_mapped_events(mapped_events)

    @cached_property
    def unmapped_events_total(self):
        mapped_events, unmapped_events = self.mapped_and_unmapped_events
        return self._aggregate_mapped_events(unmapped_events)

    @cached_property
    def events_total(self):
        a = self.unmapped_events_total
        b = self.mapped_events_total
        return {k: a[k] + b[k] for k in set(b) & set(a)}

    @cached_property
    def mapped_and_unmapped_events(self):
        mapped_events, unmapped_events = \
            SalesforceRevenuePlanMapEntry.get_mapped_and_unmapped_events(self)
        return mapped_events, unmapped_events

    @cached_property
    def start_datetime(self):
        return self.revenue_plan.start_datetime(self.connection.salesforce_timezone)

    @cached_property
    def end_datetime(self):
        return self.revenue_plan.end_datetime(self.connection.salesforce_timezone)

    def all_events(self):
        return SalesforceEvent.objects.filter(
            connection=self.connection,
            event_date__gte=self.start_datetime,
            event_date__lte=self.end_datetime) \
            .select_related('virtual_contact') \
            .order_by('virtual_contact', 'event_date')

    def virtual_contacts(self):
        return SalesforceVirtualContact.objects.filter(
            id__in=self.all_events().distinct().values_list('virtual_contact_id', flat=True))

    def save(self, *args, **kwargs):
        created = not self.pk
        super(SalesforceRevenuePlan, self).save(*args, **kwargs)
        if created:
            SalesforceRevenuePlanMapEntry.refresh_map(self)

    def delete(self, *args, **kwargs):
        [x.delete() for x in Campaign.objects.filter(source=CampaignSources.SALESFORCE,
                                                     revenue_plan_id=self.revenue_plan_id)]
        super(SalesforceRevenuePlan, self).delete(*args, **kwargs)


class SalesforceVirtualContact(models.Model):
    class Meta:
        ordering = ('created_date',)

    # Can't rely on all opportunities to have leads, so we have to fake this sometimes
    connection = models.ForeignKey(SalesforceConnection, related_name='virtual_contacts')
    created_date = models.DateTimeField(blank=True, null=True)
    campaign_field_value = models.CharField(max_length=255)
    campaign_field_value_slug = models.CharField(max_length=255)
    segment_field_text_value = models.CharField(max_length=255, blank=True)
    segment_field_text_value_slug = models.CharField(max_length=255, blank=True)
    segment_field_numeric_value = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    salesforce_lead = models.OneToOneField(SalesforceLead, null=True,
                                           related_name='virtual_contact')
    salesforce_account = models.ForeignKey(SalesforceAccount, null=True,
                                           related_name='virtual_contact')
    # only to be used when actually sourced from an opportunity (as opposed to a lead),
    # ie is virtual
    salesforce_opportunity = models.ForeignKey(SalesforceOpportunity, null=True,
                                               related_name='virtual_contact')
    is_virtual = models.BooleanField(default=False)

    @classmethod
    def get_sources_by_connection(cls, sfc):
        return cls.objects.filter(connection_id=sfc.id).order_by(
            'campaign_field_value').values_list(
            'campaign_field_value', flat=True).distinct()

    @classmethod
    def get_segment_text_values_by_connection(cls, sfc):
        return cls.objects.filter(connection=sfc).order_by('segment_field_text_value').values_list(
            'segment_field_text_value', flat=True).distinct()

    @classmethod
    def refresh_virtual_contacts_and_events(cls, sfc):
        cls.objects.filter(connection=sfc).delete()
        SalesforceEvent.objects.filter(connection=sfc).delete()
        vcontact_lookup_by_lead = {}
        vcontact_lookup_by_opportunity = {}
        for lead in SalesforceLead.objects \
                .select_related('salesforce_opportunity', 'salesforce_account') \
                .filter(connection=sfc):
            salesforce_account_id = lead.salesforce_account_id
            if lead.salesforce_opportunity and not salesforce_account_id:
                salesforce_account_id = lead.salesforce_opportunity.salesforce_account_id

            # resolve mapping values, checking Lead -> Opportunity -> Account
            campaign_field_value = resolve_campaign_value(sfc, lead=lead)
            segment_field_text_value, segment_field_numeric_value = resolve_segment_value(
                sfc, lead=lead
            )
            vcontact = cls.objects.create(
                connection=sfc,
                campaign_field_value=campaign_field_value,
                segment_field_text_value=segment_field_text_value,
                segment_field_numeric_value=segment_field_numeric_value,
                salesforce_lead=lead,
                created_date=lead.sfdc_created_date,
                salesforce_opportunity=lead.salesforce_opportunity,
                salesforce_account_id=salesforce_account_id
            )
            # keep track of opportunity ids for filtering
            if lead.salesforce_opportunity_id:
                vcontact_lookup_by_opportunity[lead.salesforce_opportunity_id] = vcontact
            vcontact_lookup_by_lead[lead.id] = vcontact

            # Create the MQL unless we have been told to ignore this status
            if lead.sfdc_status.lower() not in [x.lower() for x in sfc.sfdc_statuses_to_ignore]:
                SalesforceEvent.objects.create(
                    connection=sfc,
                    virtual_contact=vcontact,
                    event_stage='mql',
                    event_date=lead.sfdc_created_date
                )

        for opportunity in SalesforceOpportunity.objects.filter(connection=sfc):
            # If the opportunity does not have any contacts its an orphan so we create a virtual
            # contact using the account info
            if opportunity.id not in vcontact_lookup_by_opportunity:
                vcontact = cls._generate_orphan_vcontact(sfc, opportunity)
            else:
                vcontact = vcontact_lookup_by_opportunity[opportunity.id]

            # Create the SQL event
            SalesforceEvent.objects.create(
                connection=sfc,
                virtual_contact=vcontact,
                event_stage='sql',
                event_date=resolve_opportunity_created_date(sfc, opportunity)
            )
            # Also generate a sale event if this is a sale
            if opportunity.sfdc_stage_name == 'Closed Won':
                SalesforceEvent.objects.create(
                    connection=sfc,
                    virtual_contact=vcontact,
                    event_stage='sale',
                    event_date=opportunity.sfdc_close_date,
                    amount=opportunity.sfdc_amount
                )

    @classmethod
    def _generate_orphan_vcontact(cls, sfc, opportunity):
        segment_field_text_value, segment_field_numeric_value = resolve_segment_value(
            sfc, opportunity=opportunity
        )

        campaign_field_value = resolve_campaign_value(sfc, opportunity=opportunity)

        # sometimes close dates are set to predate the opportunity date
        vcontact = cls.objects.create(
            connection=sfc,
            segment_field_text_value=segment_field_text_value,
            segment_field_numeric_value=segment_field_numeric_value,
            campaign_field_value=campaign_field_value,
            salesforce_opportunity=opportunity,
            is_virtual=True,
            created_date=resolve_opportunity_created_date(sfc, opportunity),
            salesforce_account_id=opportunity.salesforce_account_id,
        )
        # create the implied MQL that would have existed had this Opportunity been converted from
        # a lead
        SalesforceEvent.objects.create(
            connection=sfc,
            virtual_contact=vcontact,
            event_stage='mql',
            event_date=resolve_opportunity_created_date(sfc, opportunity),
        )
        return vcontact

    def save(self, *args, **kwargs):
        self.is_virtual = not self.salesforce_lead
        self.campaign_field_value_slug = RE_SLUG.sub('', self.campaign_field_value).lower()
        self.segment_field_text_value_slug = RE_SLUG.sub('', self.segment_field_text_value).lower()
        super(SalesforceVirtualContact, self).save(*args, **kwargs)

        # double check that the lead seg field matches the opp seg field, and if not record
        # because this will cause confusion in salesforce reports
        if self.salesforce_lead and self.salesforce_opportunity:
            lead_seg_field = self.connection.lead_segment_field
            lead_seg_value = self.salesforce_lead.segment_field_text_value
            opp_seg_field = self.connection.opportunity_segment_field
            opp_seg_value = self.salesforce_opportunity.segment_field_text_value
            if lead_seg_field and opp_seg_field and lead_seg_value != opp_seg_value:
                SalesforceDataIssue.objects.update_or_create(
                    defaults=dict(
                        level=SalesforceDataIssue.Levels.WARNING,
                        message="Lead.%s: %s != Opportunity.%s: %s" % (
                            lead_seg_field, lead_seg_value, opp_seg_field, opp_seg_value
                        )
                    ),
                    connection=self.connection,
                    virtual_contact=self,
                    salesforce_lead=self.salesforce_lead,
                    salesforce_opportunity=self.salesforce_opportunity,
                )


# Not just a mirror of the Salesforce model, this infers the missing stages.
class SalesforceVirtualContactHistory(models.Model):
    connection = models.ForeignKey(SalesforceConnection, related_name='virtual_contacts_history')
    virtual_contact = models.ForeignKey(SalesforceVirtualContact, related_name='history')
    status = models.CharField(max_length=255)
    status_source = models.CharField(max_length=255,
                                     choices=(('lead', 'Lead'), ('opportunity', 'Opportunity')))
    updated = models.DateTimeField()
    is_virtual = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0, blank=True, null=True)

    @classmethod
    def refresh_history(cls, sfc):
        cls.objects.filter(connection=sfc).delete()
        available_statuses = cls._get_available_statuses(sfc)
        cls._refresh_lead_history(sfc, available_statuses)
        cls._refresh_opportunity_history(sfc, available_statuses)
        cls._generate_missing_statuses(sfc, available_statuses)

    @classmethod
    def _refresh_lead_history(cls, sfc, available_statuses):
        lead_status_initial = get_picklist_values(sfc, 'Lead', 'Status')[0]
        vc_by_lead = {
            x.salesforce_lead.sfdc_id: x for x in
            SalesforceVirtualContact.objects.select_related(
                'salesforce_lead').filter(
                connection=sfc).exclude(salesforce_lead=None)
            }

        # refresh lead history
        data = sfc.api.query_all(
            "SELECT Id, CreatedDate, LeadId, Field, OldValue, NewValue FROM "
            "LeadHistory WHERE Field IN ('Status', 'created') AND IsDeleted=FALSE "
            "AND CreatedDate >= %s "
            "ORDER BY LeadId, CreatedDate" % arrow.get(sfc.earliest_date)
        )
        last_vc = None
        last_status = None
        for lead_history in data['records']:
            vc = vc_by_lead.get(lead_history['LeadId'])

            if not vc:
                logger.info(
                    "SFDC VirtualContact LeadHistory Refresh:  Could not find LeadId %s for "
                    "company %s" % (
                        lead_history['LeadId'], sfc.company)
                )
                continue
            if lead_history['Field'] == 'Status':
                status = lead_history['NewValue']
            else:
                status = lead_status_initial
            if vc == last_vc and status == last_status:
                # skip consecutive duplicates
                continue
            last_vc = vc
            last_status = status
            cls.objects.update_or_create(
                defaults=dict(
                    updated=lead_history['CreatedDate'],
                ),
                connection=sfc,
                virtual_contact=vc,
                status=status,
                status_source='lead',
                order=cls._get_order(available_statuses, status, 'lead')
            )

    @classmethod
    def _refresh_opportunity_history(cls, sfc, available_statuses):
        vc_by_opportunity = {
            x.salesforce_lead.salesforce_opportunity.sfdc_id: x for x in
            SalesforceVirtualContact.objects.select_related(
                'salesforce_lead', 'salesforce_lead__salesforce_opportunity').filter(
                connection=sfc).exclude(salesforce_lead=None)
            if x.salesforce_lead.salesforce_opportunity
            }
        # virtual (orphan)
        vc_by_opportunity.update(
            {
                x.salesforce_opportunity.sfdc_id: x for x in
                SalesforceVirtualContact.objects.select_related(
                    'salesforce_opportunity').filter(
                    connection=sfc).exclude(salesforce_opportunity=None, is_virtual=False)
                }
        )

        # refresh lead history
        data = sfc.api.query_all(
            "SELECT Id, CreatedDate, OpportunityId, StageName FROM OpportunityHistory "
            "WHERE IsDeleted=FALSE AND CreatedDate >= %s "
            "ORDER BY OpportunityId, CreatedDate" % arrow.get(sfc.earliest_date)
        )
        last_vc = None
        last_status = None
        for opportunity_history in data['records']:
            vc = vc_by_opportunity.get(opportunity_history['OpportunityId'])
            if not vc:
                logger.info(
                    "SFDC VirtualContact Opportunity History Refresh:  Could not find LeadId %s "
                    "for company %s" % (opportunity_history['OpportunityId'], sfc.company)
                )
                continue
            status = opportunity_history['StageName']
            if vc == last_vc and status == last_status:
                # skip consecutive duplicates
                continue
            last_vc = vc
            last_status = status
            cls.objects.update_or_create(
                defaults=dict(
                    updated=opportunity_history['CreatedDate'],
                ),
                connection=sfc,
                virtual_contact=vc,
                status=status,
                status_source='opportunity',
                order=cls._get_order(available_statuses, opportunity_history['StageName'],
                                     'opportunity')
            )

    @classmethod
    def _generate_missing_statuses(cls, sfc, available_statuses):
        items = cls.objects.filter(connection=sfc).order_by('virtual_contact_id').exclude(
            order=None).values(
            'virtual_contact_id', 'updated', 'status', 'status_source', 'order'
        )
        # build a structured list of current statuses
        real_statuses = defaultdict(list)
        for item in items:
            real_statuses[item['virtual_contact_id']].append(item)
        # fill in virtual statuses
        for vcid, vc_statuses in real_statuses.items():
            vc_statuses = sorted(vc_statuses, key=lambda k: k['order'])
            last_order = -1
            for idx, status in enumerate(vc_statuses):
                for i in range(last_order + 1, status['order']):
                    if not available_statuses[i]['end']:
                        cls.objects.create(
                            connection=sfc,
                            virtual_contact_id=vcid,
                            status=available_statuses[i]['status'],
                            status_source=available_statuses[i]['source'],
                            updated=status['updated'],
                            is_virtual=True,
                            order=i
                        )
                last_order = status['order']

    @classmethod
    def _get_available_statuses(cls, sfc):
        return [
                   dict(status=x, source='lead', end=x in sfc.sfdc_end_statuses)
                   for x in get_picklist_values(sfc, 'Lead', 'Status')
                   ] + [
                   dict(status=x, source='opportunity',
                        end=x in sfc.sfdc_end_statuses)
                   for x in get_picklist_values(sfc, 'Opportunity', 'StageName')
                   ]

    @staticmethod
    def _get_order(available_statuses, status, source):
        for order, data in enumerate(available_statuses):
            if data['status'] == status and data['source'] == source:
                return order
        return None


class SalesforceEvent(models.Model):
    class Meta:
        ordering = ('event_date',)

    connection = models.ForeignKey(SalesforceConnection)
    virtual_contact = models.ForeignKey(SalesforceVirtualContact, related_name='events')
    event_stage = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)

    @classmethod
    def get_sources_by_plan(cls, sf_plan):
        return cls.objects.select_related('virtual_contact') \
            .filter(connection_id=sf_plan.connection_id,
                    event_date__gte=sf_plan.start_datetime,
                    event_date__lte=sf_plan.end_datetime) \
            .order_by('virtual_contact__campaign_field_value') \
            .values_list('virtual_contact__campaign_field_value', flat=True).distinct()

    @classmethod
    def get_segment_text_values_by_plan(cls, sf_plan):
        return cls.objects.select_related('virtual_contact') \
            .filter(connection_id=sf_plan.connection_id,
                    event_date__gte=sf_plan.start_datetime,
                    event_date__lte=sf_plan.end_datetime) \
            .order_by('virtual_contact__segment_field_text_value') \
            .values_list('virtual_contact__segment_field_text_value', flat=True).distinct()


class SalesforceRevenuePlanMapEntry(DirtyFieldsMixin, models.Model):
    class Meta:
        ordering = ('revenue_plan', 'segment_value', 'source_value')
        unique_together = (
            'connection', 'salesforce_revenue_plan', 'segment_value', 'source_value')

    connection = models.ForeignKey(SalesforceConnection)
    salesforce_revenue_plan = models.ForeignKey(SalesforceRevenuePlan, related_name='map_entries')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan')
    segment_value = models.CharField(max_length=255)  # number or slug
    source_value = models.CharField(max_length=255)  # slug
    segment = models.ForeignKey('revenues.Segment', blank=True, null=True,
                                on_delete=models.SET_NULL)
    program = models.ForeignKey('leads.Program', blank=True, null=True,
                                on_delete=models.SET_NULL)
    campaign = models.ForeignKey('performance.Campaign', blank=True, null=True,
                                 on_delete=models.SET_NULL)

    def map_to_program(self, program):
        if not program:
            return self.unmap()
        self._clear_campaign()
        self.program = program
        self.segment = program.segment
        self.save()
        return self

    def unmap(self):
        self._clear_campaign()
        self.program = None
        self.segment = None
        self.save()
        return self

    def _clear_campaign(self):
        if self.campaign:
            campaign = self.campaign
            self.campaign = None
            campaign.delete()

    @classmethod
    def refresh_map(cls, sf_plan):
        """
        Create an entry for each segment/source combo, and remove any entries for
        sources or segments that don't exist anymore.
        :param sf_plan:
        """
        segment_values = SalesforceEvent.get_segment_text_values_by_plan(sf_plan)
        source_values = SalesforceEvent.get_sources_by_plan(sf_plan)
        for segment_value in segment_values:
            for source_value in source_values:
                cls.objects.update_or_create(
                    connection_id=sf_plan.connection_id,
                    salesforce_revenue_plan=sf_plan,
                    revenue_plan_id=sf_plan.revenue_plan_id,
                    segment_value=segment_value,
                    source_value=source_value
                )
        # remove unused maps
        entries_to_delete = cls.objects.filter(salesforce_revenue_plan=sf_plan) \
            .exclude(source_value__in=source_values, segment_value__in=segment_values)

        for entry in entries_to_delete:
            # remove campaigns
            if entry.campaign:
                entry.campaign.delete()
            entry.delete()

    @staticmethod
    def generate_blank_events_dict(sf_map):
        output = defaultdict(dict)
        segment_values = sf_map.keys()
        source_values = []
        [source_values.extend(x.keys()) for x in sf_map.values()]

        for segment_value in segment_values:
            for source_value in source_values:
                output[segment_value][source_value] = {
                    y: dict(mql=0, sql=0, sales=0, sales_revenue=0) for y in
                    range(1, 13)
                    }
        return output

    @classmethod
    def get_mapped_and_unmapped_events(cls, sf_plan, sf_map=None):
        if not sf_map:
            sf_map = cls.as_map_dict(sf_plan)
        sfc = sf_plan.connection
        mapped_events = cls.generate_blank_events_dict(sf_map)
        unmapped_events = cls.generate_blank_events_dict(sf_map)

        for event in sf_plan.all_events():
            segment_value = event.virtual_contact.segment_field_text_value
            source_value = event.virtual_contact.campaign_field_value

            # can't map to unmapped combos
            if sf_map[segment_value][source_value]:
                target = mapped_events
            else:
                target = unmapped_events

            # record this stage
            stage = event.event_stage if event.event_stage != 'sale' else 'sales'
            month = arrow.get(event.event_date).to(sfc.salesforce_timezone).month
            target[segment_value][source_value][month][stage] += 1
            if event.amount:
                target[segment_value][source_value][month]['sales_revenue'] += event.amount

        return mapped_events, unmapped_events

    @classmethod
    def refresh_campaign_performance_data(cls, sf_plan):
        """
        Maps performance data into ICMO Campaigns from the Salesforce Events table
        Triggers periods refresh after completion.
        :param sf_plan:
        """
        logger.info("Refreshing Campaign Performance for SF Plan %s" % sf_plan)
        campaigns = set()
        sf_map = cls.as_map_dict(sf_plan)
        mapped_events, unmapped_events = cls.get_mapped_and_unmapped_events(sf_plan, sf_map)
        # Save all metrics
        for segment_value, source_event_campaigns in mapped_events.items():
            for source_value, performance_months in source_event_campaigns.items():
                for month, performance in performance_months.items():
                    campaign = sf_map[segment_value][source_value]
                    if not campaign:
                        # can't map unmapped combos
                        continue

                    # update the ICMO Campaign
                    for field in ('mql', 'sql', 'sales', 'sales_revenue'):
                        setattr(campaign, '%s_%s' % (MONTHS_3[month - 1], field),
                                performance[field])

                    campaign.do_not_enqueue = True  # stop signals from firing
                    campaign.save()
                    campaigns.add(campaign)

        # trigger periods refresh
        for campaign in campaigns:
            update_or_create_month_periods_from_campaign.delay(campaign)
        logger.info("Campaign Performance refresh complete, %d campaigns queued for update" % len(
            campaigns))

    @classmethod
    def as_map_dict(cls, sf_plan):
        output = defaultdict(dict)
        for entry in cls.objects.filter(salesforce_revenue_plan=sf_plan):
            output[entry.segment_value][entry.source_value] = entry.campaign
        return output

    def save(self, *args, **kwargs):
        if self.program:
            self.segment = self.program.segment
            # create campaigns if a program is set
            if not self.campaign:
                if self.segment_value != self.segment.name:
                    name = "%s - %s" % (self.segment_value, self.source_value)
                else:
                    name = self.source_value
                self.campaign = Campaign.objects.create(
                    name=name,
                    source=CampaignSources.SALESFORCE,
                    program=self.program,
                    revenue_plan=self.revenue_plan,
                )
        super(SalesforceRevenuePlanMapEntry, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.campaign and self.campaign.id:
            self.campaign.delete()
        super(SalesforceRevenuePlanMapEntry, self).delete(*args, **kwargs)


class SalesforceDataIssue(models.Model):
    class Levels(object):
        INFO = 'info'
        WARNING = 'warning'
        ERROR = 'error'
        choices = (
            (INFO, 'Info'),
            (INFO, 'Warning'),
            (INFO, 'Error'),
        )

    connection = models.ForeignKey('SalesforceConnection')
    virtual_contact = models.ForeignKey('SalesforceVirtualContact', blank=True, null=True)
    salesforce_lead = models.ForeignKey('SalesforceLead', blank=True, null=True)
    salesforce_opportunity = models.ForeignKey('SalesforceOpportunity', blank=True, null=True)
    salesforce_account = models.ForeignKey('SalesforceAccount', blank=True, null=True)
    level = models.CharField(max_length=50, choices=Levels.choices)
    message = models.TextField()
