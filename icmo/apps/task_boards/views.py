from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework_extensions.mixins import NestedViewSetMixin
from vanilla import TemplateView

from api.mixins import NestedKwargsMixin
from api.viewsets import IcmoModelViewSet
from companies.models import CompanyUser
from core.cbvs import AppMixin
from revenues.models import Segment
from task_boards.models import TaskBoard, Task, TaskList, TaskStatuses, TaskTypes, \
    TaskPriorities, \
    TaskTag, TaskUserRoles, TaskHistory
from task_boards.serializers import TaskBoardSerializer, TaskSerializer, TaskListSerializer


class TaskBoardListView(AppMixin, TemplateView):
    http_method_names = ('get', 'post')
    template_name = 'task_boards/task_boards_list.html'
    app_name = 'task_boards'

    def get_context_data(self, **kwargs):
        context = super(TaskBoardListView, self).get_context_data(**kwargs)
        context.update(dict(
                task_boards=TaskBoard.objects.filter(company=self.request.selected_company,
                                                     revenue_plan=self.request.selected_plan),
                api_url=reverse('company-plans-task_boards-list', kwargs=dict(
                        parent_lookup_company__slug=self.request.selected_company.slug,
                        parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
        ))
        return context


class TaskBoardView(AppMixin, TemplateView):
    http_method_names = ('get', 'post')
    template_name = 'task_boards/task_board.html'
    app_name = 'task_boards'

    def get_context_data(self, **kwargs):
        context = super(TaskBoardView, self).get_context_data(**kwargs)
        task_board = get_object_or_404(TaskBoard, company=self.request.selected_company,
                                       revenue_plan=self.request.selected_plan,
                                       slug=self.kwargs['task_board_slug'])

        context['filters'] = dict(
                segment=self.request.GET.get('segment'),
                program=self.request.GET.get('program'),
                bli=self.request.GET.get('bli')
        )
        context['filter_args'] = "&".join(
                "%s=%s" % (key, val) for key, val in context['filters'].items() if val)
        if self.request.GET.get('segment'):
            try:
                segment = Segment.objects.get(revenue_plan=self.request.selected_plan,
                                              slug=self.request.GET['segment'])
                context['filter_programs'] = [(x['slug'], x['name']) for x in
                                              segment.programs.values('slug', 'name')]
                context['filter_blis'] = [(x['slug'], x['name']) for x in
                                          segment.budgets.values('slug', 'name')]
            except Segment.DoesNotExist:
                pass

        context.update(dict(
                task_board=task_board,
                tasks_api_url=reverse('company-plans-task_boards-tasks-list', kwargs=dict(
                        parent_lookup_task_list__task_board__company__slug=self.request
                            .selected_company.slug,
                        parent_lookup_task_list__task_board__revenue_plan__slug=self.request
                            .selected_plan.slug,
                        parent_lookup_task_list__task_board__slug=task_board.slug)),
                task_lists_api_url=reverse('company-plans-task_boards-task_lists-list',
                                           kwargs=dict(
                                                   parent_lookup_task_board__company__slug=self.request.selected_company.slug,
                                                   parent_lookup_task_board__revenue_plan__slug=self.request.selected_plan.slug,
                                                   parent_lookup_task_board__slug=task_board.slug
                                           )),
                segments_list_api_url=reverse('company-plans-segments-list', kwargs=dict(
                        parent_lookup_company__slug=self.request.selected_company.slug,
                        parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
                segment_list=[(segment.slug, segment.name) for segment in
                              self.request.company_user.permitted_segments.filter(
                                      revenue_plan=self.request.selected_plan)],
                status_choices=TaskStatuses.choices,
                task_type_choices=TaskTypes.choices,
                priority_choices=TaskPriorities.choices,
                role_choices=TaskUserRoles.choices,
                user_choices=[(x.user.email, x.user.full_name) for x in
                              CompanyUser.objects.filter(company=self.request.selected_company)],
                tag_choices=[(x.uuid, x.name) for x in
                             TaskTag.objects.filter(task_board=task_board)]
        ))
        return context


class TaskBoardViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    lookup_field = 'slug'
    lookup_value_regex = '[\w-]+'
    queryset = TaskBoard.objects.all()
    serializer_class = TaskBoardSerializer


class TaskListViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    lookup_field = 'uuid'
    lookup_value_regex = '[\w-]+'
    queryset = TaskList.objects.all()
    serializer_class = TaskListSerializer


class TaskViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    lookup_field = 'uuid'
    lookup_value_regex = '[\w-]+'
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        """ Optional:  Filter by segment (and program or bli) """
        queryset = super(TaskViewSet, self).get_queryset()
        queryset = queryset.filter(
                Q(private=False) | Q(private=True, users__in=[self.request.user]))
        segment_slug = self.request.query_params.get('segment', None)
        if segment_slug:
            queryset = queryset.filter(segment__slug=segment_slug)
        program_slug = self.request.query_params.get('program', None)
        if program_slug:
            queryset = queryset.filter(program__slug=program_slug)
        bli_sug = self.request.query_params.get('bli', None)
        if bli_sug:
            queryset = queryset.filter(budget_line_item__slug=bli_sug)
        return queryset.distinct()

    def perform_update(self, serializer):
        tracked_fields = ('task_list',
                          'name', 'description', 'task_type', 'status', 'segment', 'program',
                          'budget_line_item', 'priority', 'gantt_task', 'private', 'start_date',
                          'end_date')
        old_obj = self.get_object()
        for key in tracked_fields:
            if getattr(old_obj, key) != serializer.validated_data[key]:
                TaskHistory.objects.create(task=old_obj, actor=self.request.user,
                                           action='modified', target=key.replace('_', ' '))
        serializer.save()
