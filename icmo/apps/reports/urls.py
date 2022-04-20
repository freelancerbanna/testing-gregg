from django.conf.urls import url

from reports import views

urlpatterns = [
    url(r'^$', views.ReportIndexView.as_view(), name='reports_index'),
    url(r'^mqls_acquired/$', views.ReportMQLAcquiredView.as_view(), name='reports_mqls_acquired'),
    url(r'^mqls_by_program/$', views.ReportMQLsByProgramView.as_view(), name='reports_mqls_by_program'),
    url(r'^campaign_results/$', views.ReportCampaignResultsView.as_view(), name='reports_campaign_results'),
    url(r'^sfdc_lead_funnel/$', views.ReportSFDCLeadFunnelView.as_view(), name='reports_sfdc_lead_funnel'),
    url(r'^sfdc_lead_tracking/$', views.ReportSFDCLeadTrackingView.as_view(), name='reports_sfdc_lead_tracking'),
    url(r'^custom_vertical/$', views.ReportCustomVerticalView.as_view(), name='reports_custom_vertical'),
    url(r'^custom_horizontal/$', views.ReportCustomHorizontalView.as_view(), name='reports_custom_horizontal'),
]