from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.NotificationSubscriptionView.as_view(), name='notification_subscriptions'),
]
