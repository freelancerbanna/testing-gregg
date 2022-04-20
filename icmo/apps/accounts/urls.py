from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^help/$', views.HelpView.as_view(), name='help'),

    url(r'^refer-a-friend/$', views.refer_a_friend, name='refer_a_friend'),
    url(r'^send-a-suggestion/$', views.SuggestionView.as_view(), name='send_a_suggestion'),
    url(r'^profile/$', views.AccountView.as_view(), name='user_details'),

    url(r'^recycle-bin/$', views.RecycleBinView.as_view(), name='recycle_bin'),
    url(r'^integrations/$', views.ConnectorsView.as_view(), name='integrations'),

]
