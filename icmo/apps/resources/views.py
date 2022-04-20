from django.core.urlresolvers import reverse
from rest_framework.parsers import JSONParser
from rest_framework_extensions.mixins import NestedViewSetMixin
from vanilla import TemplateView

from api.mixins import NestedKwargsMixin
from api.viewsets import IcmoModelViewSet
from core.cbvs import AppMixin
from resources.models import GanttTask, GanttDependency, UserTask, SchedulerEvent, RadiantGanttTask
from resources.serializers import GanttTaskSerializer, GanttDependencySerializer, \
    UserTaskSerializer, SchedulerEventSerializer, RadiantGanttTaskSerializer

DAYS_PER_1KMS = 1000 * 60 * 60 * 24


class ResourcesGanttView(AppMixin, TemplateView):
    template_name = 'resources/gantt.html'
    app_name = 'resources'

    def get_context_data(self, **kwargs):
        context_data = super(ResourcesGanttView, self).get_context_data(**kwargs)
        context_data.update(dict(
            resources_api_url=reverse(
                'company-users-list',
                kwargs=dict(parent_lookup_company__slug=self.request.selected_company.slug)),
            tasks_api_url=reverse('company-plans-rqgantt-tasks-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
            dependencies_api_url=reverse('company-plans-gantt-dependencies-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
            assignments_api_url=reverse('company-plans-gantt-assignments-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),
            app_segment_content_template='resources/div_gantt.html',
            disable_charts=True,
            disable_toolbar=True
        ))
        return context_data


class ResourcesSchedulerView(AppMixin, TemplateView):
    template_name = 'resources/scheduler.html'
    app_name = 'timeline'

    def get_context_data(self, **kwargs):
        context_data = super(ResourcesSchedulerView, self).get_context_data(**kwargs)
        context_data.update(dict(
            scheduler_api_url=reverse('company-plans-scheduler-list', kwargs=dict(
                parent_lookup_company__slug=self.request.selected_company.slug,
                parent_lookup_revenue_plan__slug=self.request.selected_plan.slug)),

        ))
        return context_data


class GanttTaskViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    lookup_field = 'slug'
    lookup_value_regex = '[\w-]+'
    queryset = GanttTask.objects.select_related(
        'parent', 'company', 'revenue_plan', 'segment',
        'budget_line_item').all()
    serializer_class = GanttTaskSerializer
    app_name = 'resources'

    def get_queryset(self):
        """ Optional:  Filter by segment """
        queryset = super(GanttTaskViewSet, self).get_queryset()
        segment = self.request.query_params.get('segment', None)
        if segment is not None:
            queryset = queryset.filter(segment__slug=segment)
        return queryset


class RadiantGanttTaskViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    lookup_field = 'rq_id'
    lookup_value_regex = '[\w-]+'
    queryset = RadiantGanttTask.objects.select_related(
        'company', 'revenue_plan', 'segment',
    ).all()
    serializer_class = RadiantGanttTaskSerializer
    app_name = 'resources'
    parser_classes = (JSONParser,)

    def get_queryset(self):
        """ Optional:  Filter by segment """
        queryset = super(RadiantGanttTaskViewSet, self).get_queryset()
        segment = self.request.query_params.get('segment', None)
        if segment is not None:
            queryset = queryset.filter(segment__slug=segment)
        return queryset


class GanttDependencyViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    lookup_field = 'dependency_id'
    lookup_value_regex = '[\w-]+'
    queryset = GanttDependency.objects.all()
    serializer_class = GanttDependencySerializer
    app_name = 'resources'

    def get_queryset(self):
        """ Optional:  Filter by segment """
        queryset = super(GanttDependencyViewSet, self).get_queryset()
        queryset.filter(segment__in=self.request.company_user.permitted_segments.all())
        segment = self.request.query_params.get('segment', None)
        if segment is not None:
            queryset = queryset.filter(segment__slug=segment)
        return queryset


class UserTaskViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    lookup_field = 'assignment_id'
    lookup_value_regex = '[\w-]+'
    queryset = UserTask.objects.all()
    serializer_class = UserTaskSerializer
    app_name = 'resources'

    def get_queryset(self):
        queryset = super(UserTaskViewSet, self).get_queryset()
        return queryset.filter(segment__in=self.request.company_user.permitted_segments.all())


class SchedulerEventViewSet(NestedViewSetMixin, NestedKwargsMixin, IcmoModelViewSet):
    """
    API endpoint that allows programs to be viewed or edited.
    """
    lookup_field = 'slug'
    lookup_value_regex = '[\w-]+'
    queryset = SchedulerEvent.objects.select_related('company', 'revenue_plan', 'gantt_task').all()
    serializer_class = SchedulerEventSerializer

    def get_queryset(self):
        queryset = super(SchedulerEventViewSet, self).get_queryset()
        return queryset.filter(
            gantt_task__segment__slug__in=self.request.company_user.permitted_segments_slugs)
