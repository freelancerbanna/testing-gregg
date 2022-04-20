from django.conf.urls import url

from hubspot_icmo.views import HubspotSetupView, HubspotMapCampaignsView, HubspotMapSegmentsView

urlpatterns = [
    url(r'^setup/$', HubspotSetupView.as_view(), name='hubspot_setup'),
    url(r'^map_campaigns/(?P<campaigns_plan_slug>[\w-]+)/$', HubspotMapCampaignsView.as_view(),
        name='hubspot_map_campaigns'),
    url(r'^map_segments/(?P<segments_map_revenue_plan_slug>[\w-]+)/$', HubspotMapSegmentsView.as_view(),
        name='hubspot_map_segments'),
]
