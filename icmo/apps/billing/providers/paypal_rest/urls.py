from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^authorized/$', views.PaypalAuthorizedView.as_view(), name='paypal_authorized'),
    url(r'^canceled/$', views.PaypalAuthorizedView.as_view(), name='paypal_canceled'),

    url(r'^webhook/$', views.PaypalWebhookView.as_view(), name='paypal_webhook'),

    url(r'^get_auth_url/$', views.AjaxGetPaypalAuthURLView.as_view(), name='paypal_get_auth_url'),

]
