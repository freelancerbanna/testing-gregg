from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.TaskBoardListView.as_view(), name='list_task_boards'),
    url(r'^(?P<task_board_slug>[\w\-]+)/$', views.TaskBoardView.as_view(),
        name='view_task_board'),
]
