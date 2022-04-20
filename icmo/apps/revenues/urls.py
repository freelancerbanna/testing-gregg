from django.conf.urls import url

from revenues import views

urlpatterns = [
    url(r'^plans/$', views.RevenuePlanListView.as_view(), name='revenue_plans_list'),
    url(r'^start/$', views.StartView.as_view(), name='start'),
]
