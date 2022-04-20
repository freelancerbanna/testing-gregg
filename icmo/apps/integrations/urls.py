from django.conf.urls import url, include

urlpatterns = [
    url(r'^hubspot/', include('hubspot_icmo.urls')),
    url(r'^salesforce/', include('salesforce_icmo.urls')),
]
