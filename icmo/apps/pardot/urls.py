from django.conf.urls import patterns, url
from pardot import views
urlpatterns = [
    url(r'campaigns/([0-9]+)/test.html', views.pardot_test),
]
