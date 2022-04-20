from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.DashboardsView.as_view(), name='dashboards'),
    url(r'^budget/$', views.DashboardsBudgetView.as_view(), name='dashboards_budget'),
    url(r'^performance/$', views.DashboardsPerformanceView.as_view(), name='dashboards_performance'),
]
