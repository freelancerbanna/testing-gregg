from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.templatetags.static import static
from django.views.generic import RedirectView

from core import views as core_views
from core.views import KendoProxyView

admin.autodiscover()

prefixed_urls = [
    url(r'^revenue/', include('revenues.urls')),
    url(r'^programs/', include('leads.urls')),
    url(r'^budgets/', include('budgets.urls')),
    url(r'^performance/', include('performance.urls')),
    url(r'^resources/', include('resources.urls')),
    url(r'^dashboards/', include('dashboards.urls')),
    url(r'^account/', include('accounts.urls')),
    url(r'^companies/', include('companies.urls')),
    url(r'^notifications/', include('notifications.urls')),
    url(r'^integrations/', include('integrations.urls')),
    url(r'^task_boards/', include('task_boards.urls')),
    url(r'^reports/', include('reports.urls')),
]

urlpatterns = [
    url(r'^favicon\.ico$',
        RedirectView.as_view(url=static('img/favicon/favicon.ico'), permanent=True),
        name='favicon'),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^django-rq/', include('django_rq.urls')),  # django-rq

    url(r'^api/', include('icmo.api_urls')),  # Rest Framework

    # Safari and older browses cannot save pdf and excel directly from the browser
    # They need this endpoint
    url(r'^k/save/$', KendoProxyView.as_view()),

    # Stripe and Paypal URLs
    # url(r'^payments/signup/paypalipn/', include('paypal.standard.ipn.urls')),
    # url(r'^payments/postbackz', paypal_standard_ipn_views.ipn, name="paypal-ipn"),

    url(r'^', include(prefixed_urls)),
    url(r'^company/(?P<company_slug>[\w-]+)/', include(prefixed_urls)),
    url(r'^company/(?P<company_slug>[\w-]+)/(?P<plan_slug>[\w-]+)/', include(prefixed_urls)),

    # Permission denied views
    url(r'^permission_denied/$', core_views.PermissionDeniedView.as_view(),
        name='permission_denied'),
    url(r'^no_published_plan/$', core_views.NoPublishedPlanView.as_view(),
        name='no_published_plan'),

    # Redirects that set the active Company and RevenuePlan
    url(r'^$', core_views.LoginRedirectView.as_view(), name='start_redirect'),
    url(r'^switch_plan/$', core_views.SwitchPlanRedirectView.as_view(), name='switch_plan'),
    url(r'^switch_company/$', core_views.SwitchCompanyRedirectView.as_view(),
        name='switch_company'),

    url(r'^account/', include('icmo_users.urls')),
    url(r'^pardot/', include('pardot.urls')),
    url(r'^billing/', include('billing.urls', namespace='billing')),

    # url(r'^salesforce/', include('salesforce_icmo.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
