import logging

import arrow
from simple_salesforce import Salesforce, SFType, SalesforceExpiredSession

logger = logging.getLogger('icmo.%s' % __name__)

SFDC_CURRENCY_FIELDS = {
    'Opportunity': ['Amount']
}


class WrappedSFType(SFType):
    def __init__(self, *args, **kwargs):
        self.sfc = kwargs.pop('sfc')
        super(WrappedSFType, self).__init__(*args, **kwargs)

    def _call_salesforce(self, method, url, **kwargs):
        try:
            return super(WrappedSFType, self)._call_salesforce(method, url, **kwargs)
        except SalesforceExpiredSession:
            logger.info("Salesforce session was expired, refreshing...")
            if self.sfc.refresh_access_token():
                self.session_id = self.sfc.access_token
                return super(WrappedSFType, self)._call_salesforce(method, url, **kwargs)
            raise


class SalesforceAPIWrapper(Salesforce):
    def __init__(self, *args, **kwargs):
        self.sfc = kwargs.pop('sfc')
        super(SalesforceAPIWrapper, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        # fix to enable serialization (https://github.com/heroku/simple-salesforce/issues/60)
        if name.startswith('__'):
            return super(SalesforceAPIWrapper, self).__getattr__(name)
        return WrappedSFType(name, self.session_id, self.sf_instance, self.sf_version,
                             self.proxies, sfc=self.sfc)


def get_picklist_values(sfc, model, field_name):
    fields = getattr(sfc.api, model).describe()['fields']
    field = [x for x in fields if x['name'] == field_name].pop()
    return [y['value'] for y in field['picklistValues']]


def build_sfdc_query(sfc, q_fields, model_name):
    q_fields = list(q_fields)
    # convert currency fields if required
    if sfc.currency_conversion and model_name in SFDC_CURRENCY_FIELDS:
        for field in SFDC_CURRENCY_FIELDS[model_name]:
            if field in q_fields:
                q_fields[q_fields.index(field)] = "convertCurrency(%s)" % field

    # add the segment field
    segment_field = getattr(sfc, '%s_segment_field' % model_name.lower())
    if segment_field and segment_field not in q_fields:
        q_fields.append(segment_field)

    # add the campaign field
    campaign_field = getattr(sfc, '%s_campaign_field' % model_name.lower())
    if campaign_field and campaign_field not in q_fields:
        q_fields.append(campaign_field)

    return "SELECT %s FROM %s WHERE IsDeleted = False AND CreatedDate >= %s" % (
        ", ".join(q_fields), model_name, arrow.get(sfc.earliest_date)
    )


def aggregate_month_events(month_events):
    output = dict(mql=0, sql=0, sales=0, sales_revenue=0)
    for month_performance in month_events.values():
        for key, val in month_performance.items():
            output[key] += val
    return output


def resolve_segment_value(sfc, lead=None, opportunity=None, account=None):
    text_value = ''
    numeric_value = None

    if lead:
        opportunity = lead.salesforce_opportunity

    if opportunity:
        account = opportunity.salesforce_account

    # The  try the opportunity model
    if sfc.opportunity_segment_field and opportunity:
        text_value = opportunity.segment_field_text_value
        numeric_value = opportunity.segment_field_numeric_value

    # First try the lead model
    if not (text_value or numeric_value) and sfc.lead_segment_field and lead:
        text_value = lead.segment_field_text_value
        numeric_value = lead.segment_field_numeric_value

    # If not, try the account model
    if not (text_value or numeric_value) and sfc.account_segment_field and account:
        text_value = account.segment_field_text_value
        numeric_value = account.segment_field_numeric_value

    return text_value, numeric_value


def resolve_campaign_value(sfc, lead=None, opportunity=None, account=None):
    value = ''

    if lead:
        opportunity = lead.salesforce_opportunity

    if opportunity:
        account = opportunity.salesforce_account

    # Then try the opportunity model
    if sfc.opportunity_campaign_field and opportunity:
        value = opportunity.campaign_field_value

    # Try the lead model
    if not value and sfc.lead_campaign_field and lead:
        value = lead.campaign_field_value

    # try the account model
    if not value and sfc.account_campaign_field and account:
        value = account.campaign_field_value

    return value


def resolve_opportunity_created_date(sfc, opportunity):
    if sfc.take_oldest_opportunity_date and opportunity.sfdc_close_date:
        return min(opportunity.sfdc_close_date, opportunity.sfdc_created_date)
    return opportunity.sfdc_created_date
