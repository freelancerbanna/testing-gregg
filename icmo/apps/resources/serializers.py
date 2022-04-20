from rest_framework import serializers

from core.serializers import get_validated_data_object_or_none, PercentField, \
    IcmoNestedItemMixin, IcmoModelSerializerMixin, MPTTOrderedObjectSerializerMixin
from icmo_users.models import IcmoUser
from revenues.models import RevenuePlan
from .models import GanttTask, GanttDependency, UserTask, SchedulerEvent, RadiantGanttTask


class GanttTaskSerializer(IcmoNestedItemMixin, IcmoModelSerializerMixin,
                          MPTTOrderedObjectSerializerMixin,
                          serializers.ModelSerializer):
    parent_class = RevenuePlan

    class Meta:
        model = GanttTask
        fields = [
            'slug',
            'start_date', 'end_date', 'expanded',
            'percent_complete', 'summary', 'title', 'description',
            'budget_line_item', 'full_title',
            'original_title', 'locked', 'past_due', 'at_risk',
        ]
        read_only_fields = [
            'slug',
            'budget_line_item', 'original_title',
            'full_title',
            'locked', 'past_due', 'at_risk'
        ]

    percent_complete = PercentField()
    at_risk = serializers.BooleanField(read_only=True, required=False, source='is_at_risk')
    start_date = serializers.DateTimeField(required=False, format="%Y-%m-%d")
    end_date = serializers.DateTimeField(required=False, format="%Y-%m-%d")

    original_title = serializers.CharField(read_only=True, required=False, allow_null=True,
                                           source='title')
    locked = serializers.BooleanField(read_only=True, required=False, source='budget_line_item')

    title = serializers.CharField(default="New Task")
    full_title = serializers.CharField(read_only=True, required=False)
    budget_line_item = serializers.CharField(read_only=True, source='budget_line_item.slug')

    def validate(self, validated_data):
        validated_data = super(GanttTaskSerializer, self).validate(validated_data)
        if 'title' in validated_data:
            validated_data['name'] = validated_data['title']
            del validated_data['title']
        return validated_data


class GanttDependencySerializer(IcmoNestedItemMixin, serializers.ModelSerializer):
    parent_class = RevenuePlan

    class Meta:
        model = GanttDependency
        fields = [
            'dependency_id', 'predecessor', 'successor', 'item_type',
        ]
        read_only_fields = [
        ]

    predecessor = serializers.CharField(read_only=False, source='predecessor.slug')
    successor = serializers.CharField(read_only=False, source='successor.slug')

    def update(self, instance, validated_data):
        validated_data = self.get_extra_data(validated_data)
        return super(GanttDependencySerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        validated_data = self.get_extra_data(validated_data)
        return super(GanttDependencySerializer, self).create(validated_data)

    def get_extra_data(self, validated_data):
        kwargs = self.context['kwargs']
        validated_data = get_validated_data_object_or_none(
            validated_data, 'predecessor',
            'slug', GanttTask,
            company__slug=kwargs['company__slug'])

        validated_data = get_validated_data_object_or_none(
            validated_data, 'successor',
            'slug', GanttTask,
            company__slug=kwargs['company__slug'])
        validated_data['revenue_plan'] = RevenuePlan.objects.get(slug=kwargs['revenue_plan__slug'])
        return validated_data


class UserTaskSerializer(IcmoNestedItemMixin, serializers.ModelSerializer):
    parent_class = RevenuePlan

    class Meta:
        model = UserTask
        fields = [
            'assignment_id', 'task', 'resource', 'value',
        ]
        read_only_fields = [
            'assignment_id'
        ]

    resource = serializers.CharField(read_only=False, source='resource.email')
    task = serializers.CharField(read_only=False, source='task.slug')

    def validate(self, validated_data):
        validated_data = super(UserTaskSerializer, self).validate(validated_data)
        validated_data['resource'] = IcmoUser.objects.get(
            email=validated_data['resource'].get('email')
        )
        validated_data['task'] = GanttTask.objects.get(
            revenue_plan__slug=self.context['kwargs']['revenue_plan__slug'],
            slug=validated_data['task'].get('slug')
        )

        return validated_data


class SchedulerEventSerializer(IcmoNestedItemMixin, IcmoModelSerializerMixin,
                               serializers.ModelSerializer):
    parent_class = RevenuePlan

    class Meta:
        model = SchedulerEvent
        fields = [
            'slug', 'gantt_task',
            'title', 'description',
            'start_datetime', 'end_datetime',
            'is_all_day', 'recurrence_exception', 'recurrence', 'recurrence_rule',
        ]
        read_only_fields = [
            'slug',
            'gantt_task',
        ]

    gantt_task = serializers.CharField(read_only=True, source='gantt_task.slug')
    recurrence = serializers.CharField(read_only=True, source='recurrence.slug')
    title = serializers.CharField(source='name')


class RadiantGanttTaskSerializer(IcmoNestedItemMixin, IcmoModelSerializerMixin,
                                 serializers.ModelSerializer):
    parent_class = RevenuePlan

    class Meta:
        model = RadiantGanttTask
        fields = [
            'rq_id',
            'rq_sort_order',
            'rq_name',
            'rq_start_time',
            'rq_end_time',
            'rq_effort',
            'rq_preferred_start_time',
            'rq_indent_level',
            'rq_predecessor_indices',
            'rq_progress_percent',
            'rq_resources',
            'past_due', 'at_risk',
        ]
        read_only_fields = [
            'past_due', 'at_risk', 'rq_end_time'
        ]

    at_risk = serializers.BooleanField(read_only=True, required=False, source='is_at_risk')
    rq_start_time = serializers.DateTimeField(required=False, format="%Y-%m-%dT%H:%M:%S.%fZ")
    rq_end_time = serializers.DateTimeField(required=False, format="%Y-%m-%dT%H:%M:%S.%fZ")
