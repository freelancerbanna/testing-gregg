from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.CompaniesListView.as_view(), name='companies_list'),
    url(r'^permissions/$', views.PermissionsView.as_view(), name='permissions'),

]
