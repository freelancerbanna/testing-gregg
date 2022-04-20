from rest_framework import serializers

from budgets.models import BudgetLineItem
from core.serializers import IcmoModelSerializerMixin, IcmoNestedItemMixin
from icmo_users.models import IcmoUser
from leads.models import Program
from revenues.models import RevenuePlan, Segment
from .models import TaskBoard, TaskList, Task, TaskCheckListItem, TaskComment, TaskTag, TaskUser, \
    TaskHistory


class TaskBoardSerializer(IcmoNestedItemMixin, IcmoModelSerializerMixin,
                          serializers.ModelSerializer):
    class Meta:
        model = TaskBoard
        fields = ['slug', 'name', 'url']
        read_only_fields = ('slug', 'url')

    parent_class = RevenuePlan
    url = serializers.URLField(read_only=True, source='get_absolute_url')


class TaskListSerializer(IcmoModelSerializerMixin,
                         serializers.ModelSerializer):
    class Meta:
        model = TaskList
        fields = ['uuid', 'name', 'task_board', 'task_board_name', 'move_above']
        read_only_fields = ('uuid', 'task_board', 'task_board_name')

    task_board = serializers.CharField(read_only=True, source='task_board.slug')
    task_board_name = serializers.CharField(read_only=True, source='task_board.name')
    name = serializers.CharField(allow_blank=True, required=False)
    move_above = serializers.CharField(write_only=True, required=False)

    def validate(self, validated_data):
        kwargs = self.context['kwargs']
        validated_data['task_board'] = TaskBoard.objects.get(
            company__slug=kwargs['task_board__company__slug'],
            revenue_plan__slug=kwargs['task_board__revenue_plan__slug'],
            slug=kwargs['task_board__slug'])
        return validated_data

    def update(self, instance, validated_data):
        if 'move_above' in validated_data and validated_data['move_above']:
            if validated_data['move_above'] == 'bottom':
                instance.bottom()
            else:
                instance.above(TaskList.objects.get(uuid=validated_data['move_above']))
        return super(TaskListSerializer, self).update(instance, validated_data)


class TaskUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskUser
        fields = (
            'user', 'user_name', 'user_initials', 'role', 'role_name', 'action')
        read_only_fields = ('user_name', 'role_name', 'user_initials',)

    user = serializers.CharField(source='user.email')
    user_name = serializers.CharField(read_only=True, source='user.full_name')
    user_initials = serializers.CharField(read_only=True, source='user.initials')
    role_name = serializers.CharField(read_only=True, source='get_role_display')
    action = serializers.CharField(write_only=True)


class TaskCheckListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCheckListItem
        fields = (
            'uuid', 'name', 'completed', 'author', 'author_name', 'author_initials', 'action')
        read_only_fields = ('author_name',)

    uuid = serializers.CharField(read_only=False)
    author = serializers.CharField(source='author.email')
    author_name = serializers.CharField(read_only=True, source='author.full_name')
    action = serializers.CharField(write_only=True)
    author_initials = serializers.CharField(read_only=True, source='author.initials')


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComment
        fields = (
            'uuid', 'comment', 'author', 'author_name', 'author_initials', 'created', 'action')
        read_only_fields = ('author_name', 'author_initials', 'created')

    uuid = serializers.CharField(read_only=False)
    author = serializers.CharField(source='author.email')
    author_name = serializers.CharField(read_only=True, source='author.full_name')
    action = serializers.CharField(write_only=True)
    author_initials = serializers.CharField(read_only=True, source='author.initials')


class TaskTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTag
        fields = ('uuid', 'name', 'action')
        read_only_fields = ('uuid', 'created')

    action = serializers.CharField(write_only=True)


class TaskSerializer(IcmoModelSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'task_board', 'task_board_name', 'task_list', 'task_list_name',
            'uuid', 'name', 'description', 'task_type', 'status',
            'segment', 'segment_name', 'program', 'program_name',
            'budget_line_item', 'budget_line_item_name', 'users',
            'user_names', 'user_initials', 'status_name', 'task_type_name', 'priority',
            'priority_name', 'checklist', 'checklist_status', 'comments', 'comments_count', 'tags',
            'tags_list', 'gantt_task', 'assigned_users', 'private', 'start_date', 'end_date',
            'move_above', 'history_list'
        ]
        read_only_fields = ('uuid', 'user_names', 'user_initials', 'history_list')

    name = serializers.CharField(default='New Task', allow_blank=True)
    task_board = serializers.CharField(read_only=True, source='task_board.slug')
    task_board_name = serializers.CharField(read_only=True, source='task_board.name')
    task_list = serializers.CharField(source='task_list.uuid')
    task_list_name = serializers.CharField(read_only=True, source='task_list.name')

    status_name = serializers.CharField(read_only=True, source='get_status_display')
    task_type_name = serializers.CharField(read_only=True, source='get_task_type_display')
    priority_name = serializers.CharField(read_only=True, source='get_priority_display')

    segment = serializers.CharField(source='segment.slug', required=False, allow_blank=True,
                                    allow_null=True)
    segment_name = serializers.CharField(read_only=True, source='segment.name')
    program = serializers.CharField(source='program.slug', required=False,
                                    allow_blank=True, allow_null=True)
    program_name = serializers.CharField(read_only=True, source='program.name')
    budget_line_item = serializers.CharField(source='budget_line_item.slug',
                                             required=False, allow_blank=True, allow_null=True)
    budget_line_item_name = serializers.CharField(read_only=True, source='budget_line_item.name')
    users = serializers.CharField(source='user_emails', required=False)

    checklist = TaskCheckListItemSerializer(many=True, required=False)
    comments = TaskCommentSerializer(many=True, required=False)
    tags = TaskTagSerializer(many=True, read_only=True)
    tags_list = serializers.ListField(child=serializers.CharField(), read_only=False,
                                      required=False)
    assigned_users = TaskUserSerializer(many=True, required=False)
    move_above = serializers.CharField(write_only=True, required=False)

    def validate(self, validated_data):
        kwargs = self.context['kwargs']
        company_slug = kwargs['task_list__task_board__company__slug']
        revenue_plan_slug = kwargs['task_list__task_board__revenue_plan__slug']
        validated_data['task_list'] = TaskList.objects.get(
            task_board__company__slug=company_slug,
            task_board__revenue_plan__slug=revenue_plan_slug,
            task_board__slug=kwargs['task_list__task_board__slug'],
            uuid=validated_data['task_list']['uuid']
        )
        model_keys = dict(segment=Segment, program=Program, budget_line_item=BudgetLineItem)
        for key in ['segment', 'program', 'budget_line_item']:
            model = model_keys[key]
            if key in validated_data and validated_data[key]['slug']:
                qs = model.objects.filter(company__slug=company_slug,
                                          revenue_plan__slug=revenue_plan_slug)
                if model != Segment:
                    qs = qs.filter(segment=validated_data['segment'])
                validated_data[key] = qs.get(slug=validated_data[key]['slug'])
            else:
                validated_data[key] = None
        return validated_data

    def create(self, validated_data):
        task = Task.create_task(
            validated_data['task_list'], self.context['request'].user,
            segment=validated_data['segment'], program=validated_data['program'],
            budget_line_item=validated_data['budget_line_item'],
        )
        TaskHistory.objects.create(task=task, actor=self.context['request'].user,
                                   action='created', target='task')
        return task

    def update(self, instance, validated_data):
        if 'checklist' in validated_data:
            for checklist in validated_data['checklist']:
                if checklist['name'] and 'uuid' not in checklist:
                    TaskCheckListItem.objects.create(task=instance, name=checklist['name'],
                                                     completed=checklist['completed'],
                                                     author=self.context['request'].user)
                    TaskHistory.objects.create(task=instance, actor=self.context['request'].user,
                                               action='created', target='checklist')
                elif 'action' in checklist:
                    if checklist['action'] == 'modify':
                        TaskCheckListItem.objects.filter(uuid=checklist['uuid']).update(
                            name=checklist.get('name', 'New Task'),
                            completed=checklist.get('completed', False))
                        TaskHistory.objects.create(task=instance,
                                                   actor=self.context['request'].user,
                                                   action='modified', target='checklist')
                    elif checklist['action'] == 'delete':
                        TaskCheckListItem.objects.filter(uuid=checklist['uuid']).delete()
                        TaskHistory.objects.create(task=instance,
                                                   actor=self.context['request'].user,
                                                   action='deleted', target='checklist')
        del (validated_data['checklist'])
        # comments
        if 'comments' in validated_data:
            for comment in validated_data['comments']:
                if comment['comment'] and 'uuid' not in comment:
                    TaskComment.objects.create(task=instance, comment=comment['comment'],
                                               author=self.context['request'].user)
                    TaskHistory.objects.create(task=instance, actor=self.context['request'].user,
                                               action='created', target='comment')
                elif 'action' in comment:
                    if comment['action'] == 'modify':
                        TaskComment.objects.filter(uuid=comment['uuid']).update(
                            comment=comment.get('comment'))
                        TaskHistory.objects.create(task=instance,
                                                   actor=self.context['request'].user,
                                                   action='modified', target='comment')
                    elif comment['action'] == 'delete':
                        TaskComment.objects.filter(uuid=comment['uuid']).delete()
                        TaskHistory.objects.create(task=instance,
                                                   actor=self.context['request'].user,
                                                   action='deleted', target='comment')
        del (validated_data['comments'])

        # Tags
        original_tags = instance.tags
        instance.tags.clear()
        for tag_name in validated_data.get('tags_list', []):
            tag, created = TaskTag.objects.get_or_create(task_board=instance.task_board,
                                                         name=tag_name)
            if created:
                TaskHistory.objects.create(task=instance, actor=self.context['request'].user,
                                           action='created', target='tag')
            instance.tags.add(tag)
        if original_tags != instance.tags:
            TaskHistory.objects.create(task=instance, actor=self.context['request'].user,
                                       action='modified', target='task tags')
        del (validated_data['tags_list'])

        # order
        if 'move_above' in validated_data and validated_data['move_above']:
            if validated_data['task_list'] != instance.task_list:
                instance.task_list = validated_data['task_list']
                instance.save()
            if validated_data['move_above'] == 'bottom':
                instance.bottom()
            else:
                instance.above(Task.objects.get(uuid=validated_data['move_above']))
            TaskHistory.objects.create(task=instance,
                                       actor=self.context['request'].user,
                                       action='reordered', target='task')

        # resources
        if 'assigned_users' in validated_data and validated_data['assigned_users']:
            for assigned_user in validated_data['assigned_users']:
                if 'action' in assigned_user:
                    if assigned_user['action'] == 'new':
                        user = IcmoUser.objects.get(email=assigned_user['user']['email'])
                        if instance.task_board.company.slug in user.companies_slugs:
                            TaskUser.objects.update_or_create(task=instance, user=user,
                                                              defaults=dict(
                                                                  role=assigned_user['role']))
                            TaskHistory.objects.create(task=instance,
                                                       actor=self.context['request'].user,
                                                       action='assigned', target='resource')
                    elif assigned_user['action'] == 'delete':
                        TaskUser.objects.filter(task=instance, user__email=assigned_user['user'][
                            'email']).delete()
                        TaskHistory.objects.create(task=instance,
                                                   actor=self.context['request'].user,
                                                   action='removed', target='resource')
                    elif assigned_user['action'] == 'modify':
                        TaskUser.objects.filter(task=instance,
                                                user__email=assigned_user['user']['email']).update(
                            role=assigned_user['role'])
                        TaskHistory.objects.create(task=instance,
                                                   actor=self.context['request'].user,
                                                   action='modified', target='resource')

        del (validated_data['assigned_users'])
        return super(TaskSerializer, self).update(instance, validated_data)
