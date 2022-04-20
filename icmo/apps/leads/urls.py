from django.conf.urls import url
from leads import views
urlpatterns = [
    url(r'^program_mix/$', views.ProgramMixView.as_view(), name='program_mix'),
]
