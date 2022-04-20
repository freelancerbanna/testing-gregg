from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.BudgetsView.as_view(), name='budgets'),
]
