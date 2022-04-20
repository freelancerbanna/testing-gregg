from django.contrib import admin

from salesforce_icmo.models import SalesforceConnection, SalesforceEvent, SalesforceRevenuePlan, \
    SalesforceVirtualContact


class SalesforceRevenuePlanAdmin(admin.ModelAdmin):
    list_display = ('connection', 'revenue_plan')
    list_filter = ('connection',)


class SalesforceEventAdmin(admin.ModelAdmin):
    list_display = ('virtual_contact', 'event_stage', 'event_date', 'amount')
    list_filter = ('connection', 'event_stage', 'event_date')


class SalesforceVirtualContactAdmin(admin.ModelAdmin):
    list_display = (
        'created_date', 'salesforce_lead', 'salesforce_opportunity', 'salesforce_account',
        'is_virtual', 'segment_field_text_value', 'segment_field_numeric_value',
        'campaign_field_value')
    list_filter = ('connection', 'segment_field_text_value', 'campaign_field_value')


admin.site.register(SalesforceConnection)
admin.site.register(SalesforceRevenuePlan, SalesforceRevenuePlanAdmin)
admin.site.register(SalesforceVirtualContact, SalesforceVirtualContactAdmin)

admin.site.register(SalesforceEvent, SalesforceEventAdmin)
