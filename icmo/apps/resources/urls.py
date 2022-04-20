from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^gantt/$', views.ResourcesGanttView.as_view(), name='resources_gantt'),
    url(r'^scheduler/$', views.ResourcesSchedulerView.as_view(), name='resources_scheduler'),
]
