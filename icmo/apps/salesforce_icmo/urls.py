from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^setup/$', views.SalesforceSetupView.as_view(), name='sfdc_setup'),
    url(r'^settings/$', views.SalesforceSettingsView.as_view(), name='sfdc_settings'),
    url(r'^manage/$', views.SalesforceManageView.as_view(), name='sfdc_manage'),
    url(r'^selected_plan/(?P<map_plan_slug>[\w-]+)/$', views.SalesforceMapView.as_view(),
        name='sfdc_map'),
    url(r'^virtual_contacts/(?P<vc_plan_slug>[\w-]+)/$',
        views.SalesforceVirtualContactsView.as_view(),
        name='sfdc_virtual_contacts'),
    url(r'^virtual_events/(?P<events_plan_slug>[\w-]+)/$',
        views.SalesforceEventsView.as_view(),
        name='sfdc_events'),
    url(r'^breakdown/(?P<breakdown_plan_slug>[\w-]+)/$',
        views.SalesforcePlanBreakdownView.as_view(),
        name='sfdc_breakdown'),
    url(r'^issues/(?P<issues_plan_slug>[\w-]+)/$',
        views.SalesforceIssuesView.as_view(),
        name='sfdc_issues'),
]
