from django.conf.urls import url, include

from . import views
import billing.providers.paypal_rest.views

urlpatterns = [
    url(r'^contracts/(?P<slug>[\w-]+)/$', views.ContractView.as_view(), name='contract_view'),
    url(r'^subscription/canceled/$',
        billing.providers.paypal_rest.views.SubscriptionCanceledView.as_view(),
        name='subscription_canceled'),
    url(r'^code/check/', views.AjaxCheckCouponView.as_view(), name='ajax_check_code'),
    url(r'^subscription/payment_summary/', views.AjaxUpdatePaymentSummaryView.as_view(),
        name='ajax_update_payment_summary'),

    url(r'^providers/paypal/', include('billing.providers.paypal_rest.urls', namespace='paypal')),
]
