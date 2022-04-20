from django.conf.urls import url
from rest_framework import routers
from rest_framework_extensions.routers import ExtendedDefaultRouter

from budgets.views import BudgetLineItemViewSet
from companies.views import CompanyViewSet, CompanyUserGroupViewSet, CompanyUserViewSet
from icmo_users.views import IcmoUserViewSet
from leads.views import ProgramViewSet
from notifications.views import NotificationSubscriptionViewSet
from performance.views import CampaignViewSet
from periods.views import PeriodViewSet, PeriodHorizontalListView
from resources.views import GanttTaskViewSet, GanttDependencyViewSet, UserTaskViewSet, \
    SchedulerEventViewSet, RadiantGanttTaskViewSet
from revenues.views import RevenuePlanViewSet, SegmentViewSet, ClonePlanView, CloneSegmentView
from task_boards.views import TaskBoardViewSet, TaskListViewSet, TaskViewSet

router = routers.DefaultRouter()
router.register(r'plans', RevenuePlanViewSet, base_name='revenue_plans')
router.register(r'segments', SegmentViewSet, base_name='segments')
router.register(r'programs', ProgramViewSet)
router.register(r'budget_line_items', ProgramViewSet)
router.register(r'campaigns', CampaignViewSet)
router.register(r'periods', PeriodViewSet)
urlpatterns = router.urls

router = ExtendedDefaultRouter()
company_router = router.register(
    r'companies',
    CompanyViewSet,
    base_name='company'
)
company_router.register(
    r'periods',
    PeriodViewSet,
    base_name='company-periods',
    parents_query_lookups=['company__slug']
)
users_router = company_router.register(
    r'users', IcmoUserViewSet,
    base_name='company-users',
    parents_query_lookups=['company__slug']
)

company_users_router = company_router.register(
    r'permissions', CompanyUserViewSet,
    base_name='company-company_users',
    parents_query_lookups=['company__slug']
)

company_users_groups_router = company_router.register(
    r'groups', CompanyUserGroupViewSet,
    base_name='company-company_users_groups',
    parents_query_lookups=['company__slug']
)

notifications_router = users_router.register(
    r'notifications', NotificationSubscriptionViewSet,
    base_name='company-users-notifications',
    parents_query_lookups=['company__slug', 'company_user__user__email'],
)

plan_router = company_router.register(
    r'plans',
    RevenuePlanViewSet,
    base_name='company-plans',
    parents_query_lookups=['company__slug']
)
plan_router.register(
    r'periods',
    PeriodViewSet,
    base_name='company-plans-periods',
    parents_query_lookups=['company__slug', 'revenue_plan__slug']
)
scheduler_router = plan_router.register(
    r'scheduler', SchedulerEventViewSet,
    base_name='company-plans-scheduler',
    parents_query_lookups=['company__slug',
                           'revenue_plan__slug']
)
plan_gantt_task_router = plan_router.register(
    r'gantt/tasks', GanttTaskViewSet,
    base_name='company-plans-gantt-tasks',
    parents_query_lookups=['company__slug',
                           'revenue_plan__slug']
)
plan_rqgantt_task_router = plan_router.register(
    r'rqgantt/tasks', RadiantGanttTaskViewSet,
    base_name='company-plans-rqgantt-tasks',
    parents_query_lookups=['company__slug',
                           'revenue_plan__slug']
)
plan_gantt_dependency_router = plan_router.register(
    r'gantt/dependencies',
    GanttDependencyViewSet,
    base_name='company-plans-gantt-dependencies',
    parents_query_lookups=['company__slug',
                           'revenue_plan__slug']
)
plan_gantt_assignments_router = plan_router.register(
    r'gantt/assignments', UserTaskViewSet,
    base_name='company-plans-gantt-assignments',
    parents_query_lookups=['company__slug',
                           'revenue_plan__slug']
)
segment_router = plan_router.register(
    r'segments',
    SegmentViewSet,
    base_name='company-plans-segments',
    parents_query_lookups=[
        'company__slug',
        'revenue_plan__slug']
)
task_board_router = plan_router.register(
    r'task_boards', TaskBoardViewSet,
    base_name='company-plans-task_boards',
    parents_query_lookups=['company__slug',
                           'revenue_plan__slug']
)
task_list_router = task_board_router.register(
    r'task_lists', TaskListViewSet,
    base_name='company-plans-task_boards-task_lists',
    parents_query_lookups=['task_board__company__slug',
                           'task_board__revenue_plan__slug',
                           'task_board__slug']
)
task_router = task_list_router.register(
    r'tasks', TaskViewSet,
    base_name='company-plans-task_boards-task_lists-tasks',
    parents_query_lookups=['task_list__task_board__company__slug',
                           'task_list__task_board__revenue_plan__slug',
                           'task_list__task_board__slug',
                           'task_list__uuid']
)
task_router2 = task_board_router.register(
    r'tasks', TaskViewSet,
    base_name='company-plans-task_boards-tasks',
    parents_query_lookups=['task_list__task_board__company__slug',
                           'task_list__task_board__revenue_plan__slug',
                           'task_list__task_board__slug']
)
segment_router.register(
    r'periods',
    PeriodViewSet,
    base_name='company-plans-segments-periods',
    parents_query_lookups=['company__slug',
                           'revenue_plan__slug', 'segment__slug']
)
program_router = segment_router.register(
    r'programs',
    ProgramViewSet,
    base_name='company-plans-segments-programs',
    parents_query_lookups=[
        'company__slug',
        'revenue_plan__slug', 'segment__slug']
)
program_router.register(
    r'periods',
    PeriodViewSet,
    base_name='company-plans-segments-programs-periods',
    parents_query_lookups=['company__slug',
                           'revenue_plan__slug', 'segment__slug',
                           'program__slug']
)
campaign_router = program_router.register(
    r'campaigns',
    CampaignViewSet,
    base_name='company-plans-segments-programs-campaigns',
    parents_query_lookups=[
        'company__slug',
        'revenue_plan__slug',
        'segment__slug',
        'program__slug']
)
budget_router = segment_router.register(
    r'budget_line_items',
    BudgetLineItemViewSet,
    base_name='company-plans-segments-budgets',
    parents_query_lookups=[
        'company__slug',
        'revenue_plan__slug', 'segment__slug']
)
segment_gantt_task_router = segment_router.register(
    r'gantt/tasks', GanttTaskViewSet,
    base_name='company-plans-segments-gantt-tasks',
    parents_query_lookups=['company__slug',
                           'revenue_plan__slug', 'segment__slug']
)
segment_gantt_dependency_router = segment_router.register(
    r'gantt/dependencies',
    GanttDependencyViewSet,
    base_name='company-plans-segments-gantt-dependencies',
    parents_query_lookups=['company__slug',
                           'revenue_plan__slug', 'segment__slug']
)
segment_gantt_assignments_router = segment_router.register(
    r'gantt/assignments', UserTaskViewSet,
    base_name='company-plans-segments-gantt-assignments',
    parents_query_lookups=['company__slug',
                           'revenue_plan__slug', 'segment__slug']
)

urlpatterns += router.urls

urlpatterns += [
    url(
        '^companies/(?P<parent_lookup_company__slug>[\w\-]+)/plans/('
        '?P<parent_lookup_revenue_plan__slug>[\w\-]+)/horizontal_periods/$',
        PeriodHorizontalListView.as_view(),
        name='companies-plans-horizontal-periods-list'
    ),
    url(
        '^companies/(?P<parent_lookup_company__slug>[\w\-]+)/plans/('
        '?P<parent_lookup_revenue_plan__slug>[\w\-]+)/segments/('
        '?P<parent_lookup_segment__slug>[\w\-]+)/horizontal_periods/$',
        PeriodHorizontalListView.as_view(),
        name='companies-plans-segments-horizontal-periods-list'
    ),
    url(
        '^companies/(?P<parent_lookup_company__slug>[\w\-]+)/plans/('
        '?P<parent_lookup_revenue_plan__slug>[\w\-]+)/clone/$',
        ClonePlanView.as_view(),
        name='companies-plans-clone'
    ),
    url(
        '^companies/(?P<parent_lookup_company__slug>[\w\-]+)/plans/('
        '?P<parent_lookup_revenue_plan__slug>[\w\-]+)/segments/('
        '?P<parent_lookup_segment__slug>[\w\-]+)/clone/$',
        CloneSegmentView.as_view(),
        name='companies-plans-segments-clone'
    ),
]
