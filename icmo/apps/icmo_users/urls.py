from django.conf.urls import url
from django.contrib.auth import views as auth_views

from core.decorators import anonymous_required
from icmo_users.forms import IcmoLoginForm, IcmoPasswordResetForm, IcmoSetPasswordForm
from . import views

urlpatterns = [
    # The signup flow
    url(r'^signup/$', views.SignupView.as_view(), name='signup'),
    url(r'^signup/ajax/check_email/$', views.AjaxCheckEmailView.as_view(),
        name='ajax_signup_check_email'),
    url(r'^signup/ajax/store_signup_form/$', views.AjaxStoreSignupFormView.as_view(),
        name='ajax_signup_store_form'),
    url(r'^signup/success/$', views.CreateAccountView.as_view(),
        name='signup_create_account'),

    # admin activation url
    url(r'^dzzVdXIbLK77hCx56CdBnN2x/(?P<token>\w+)/$', views.ActivateUserView.as_view(),
        name='activate_new_user'),

    # invited user activation url
    url(r'^activate/(?P<token>\w+)/$', views.ActivateInvitedUserView.as_view(),
        name='activate_invited_user'),

    # Leveraging built in django views and forms for login and password reset
    url(r'^login/$', anonymous_required(auth_views.login), {'authentication_form': IcmoLoginForm},
        name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^password_change/$', auth_views.password_change, name='password_change'),
    url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset,
        {'password_reset_form': IcmoPasswordResetForm}, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^password_reset/(?P<uidb64>[\w\-]+)/(?P<token>\w{1,13}-\w{1,20})/$',
        auth_views.password_reset_confirm,
        {'set_password_form': IcmoSetPasswordForm},
        name='password_reset_confirm'),
    url(r'^password_reset/complete/$', auth_views.password_reset_complete,
        name='password_reset_complete'),
]
