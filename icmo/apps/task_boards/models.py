# Create your models here.
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.functional import cached_property
from django_extensions.db.fields import AutoSlugField, ShortUUIDField
from django_extensions.db.models import TimeStampedModel
from ordered_model.models import OrderedModel

from core.models import IcmoModel


class TaskStatuses(object):
    UNSTARTED = 'unstarted'
    STARTED = 'started'
    FINISHED = 'finished'
    DELIVERED = 'delivered'
    REJECTED = 'rejected'
    ACCEPTED = 'accepted'

    choices = (
        (UNSTARTED, UNSTARTED.title()),
        (STARTED, STARTED.title()),
        (FINISHED, FINISHED.title()),
        (DELIVERED, DELIVERED.title()),
        (REJECTED, REJECTED.title()),
        (ACCEPTED, ACCEPTED.title()),
    )


class TaskTypes(object):
    EMAIL = 'email'
    EMAIL_DESIGN = 'email_design'
    EMAIL_CONTENT = 'email_content'
    LANDING_PAGE_DESIGN = 'landing_page_design'
    LANDING_PAGE_CONTENT = 'landing_page_content'
    OTHER_CONTENT = 'content'
    choices = (
        (EMAIL, EMAIL.title()),
        (EMAIL_DESIGN, EMAIL_DESIGN.replace('_', ' ').title()),
        (EMAIL_CONTENT, EMAIL_CONTENT.replace('_', ' ').title()),
        (LANDING_PAGE_DESIGN, LANDING_PAGE_DESIGN.replace('_', ' ').title()),
        (LANDING_PAGE_CONTENT, LANDING_PAGE_CONTENT.replace('_', ' ').title()),
        (OTHER_CONTENT, OTHER_CONTENT.replace('_', ' ').title()),
    )


class TaskPriorities(object):
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    choices = (
        (LOW, LOW.title()),
        (NORMAL, NORMAL.title()),
        (HIGH, HIGH.title()),
    )


class TaskUserRoles(object):
    OWNER = 'owner'
    APPROVER = 'approver'
    REVIEWER = 'reviewer'

    choices = (
        (OWNER, OWNER.title()),
        (APPROVER, APPROVER.title()),
        (REVIEWER, REVIEWER.title()),
    )


class TaskBoard(IcmoModel):
    icmo_parent_levels = ('company','revenue_plan')

    class Meta:
        unique_together = ('slug', 'revenue_plan')
        ordering = ('-name',)

    company = models.ForeignKey('companies.Company')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan')
    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name')

    @property
    def task_lists(self):
        return self.tasklist_set.filter(is_active=True)

    def get_absolute_url(self):
        return reverse('view_task_board', kwargs=dict(company_slug=self.company.slug,
                                                      plan_slug=self.revenue_plan.slug,
                                                      task_board_slug=self.slug))

    def save(self, *args, **kwargs):
        created = not self.pk
        super(TaskBoard, self).save(*args, **kwargs)
        if created:
            TaskList.objects.create(task_board=self, name='Current')
            TaskList.objects.create(task_board=self, name='Backlog')
            TaskList.objects.create(task_board=self, name='Done')

    def __unicode__(self):
        return self.name


class TaskList(OrderedModel, IcmoModel):
    uuid = ShortUUIDField(editable=False, db_index=True)
    task_board = models.ForeignKey(TaskBoard)
    name = models.CharField(max_length=150, default='New Task List')

    def __unicode__(self):
        return self.name


class Task(OrderedModel, IcmoModel):
    order_with_respect_to = 'task_list'

    class Meta(OrderedModel.Meta):
        pass

    uuid = ShortUUIDField(editable=False, db_index=True, unique=True)
    task_board = models.ForeignKey(TaskBoard)
    task_list = models.ForeignKey(TaskList)
    name = models.CharField(max_length=150, blank=True, default='New Task')
    description = models.TextField(blank=True)
    users = models.ManyToManyField('icmo_users.IcmoUser', through='TaskUser')
    segment = models.ForeignKey('revenues.Segment', blank=True, null=True)
    program = models.ForeignKey('leads.Program', blank=True, null=True)
    budget_line_item = models.ForeignKey('budgets.BudgetLineItem', blank=True, null=True)
    task_type = models.CharField(max_length=255, choices=TaskTypes.choices, blank=True, null=True)
    status = models.CharField(max_length=255, choices=TaskStatuses.choices,
                              default=TaskStatuses.UNSTARTED, blank=True)
    priority = models.CharField(max_length=255, choices=TaskPriorities.choices,
                                default=TaskPriorities.NORMAL, blank=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    gantt_task = models.ForeignKey('resources.GanttTask', blank=True, null=True)
    private = models.BooleanField(default=False)
    tags = models.ManyToManyField('TaskTag')

    @cached_property
    def user_emails(self):
        return [x.email for x in self.users.all()]

    @cached_property
    def user_names(self):
        return [x.full_name for x in self.users.all()]

    @cached_property
    def user_initials(self):
        return ", ".join(
            [x.initials for x in self.users.all()])

    @cached_property
    def checklist_status(self):
        total = 0
        complete = 0
        for checklist in self.checklist.all():
            total += 1
            if checklist.completed:
                complete += 1
        return "%s/%s" % (complete, total)

    @cached_property
    def comments_count(self):
        return self.comments.count()

    @cached_property
    def tags_list(self):
        return [x.name for x in self.tags.all()]

    @cached_property
    def history_list(self):
        return [dict(created=x.created, actor=x.actor.full_name, action=x.action, target=x.target)
                for x in self.history.all()]

    def save(self, *args, **kwargs):
        self.task_board = self.task_list.task_board
        super(Task, self).save(*args, **kwargs)

    @classmethod
    def create_task(cls, task_list, user, segment=None, program=None, budget_line_item=None):
        new_task = cls.objects.create(task_list=task_list, segment=segment, program=program,
                                      budget_line_item=budget_line_item)
        TaskUser.objects.create(task=new_task, user=user, role=TaskUserRoles.OWNER)
        return new_task


class TaskUser(models.Model):
    user = models.ForeignKey('icmo_users.IcmoUser', related_name='assigned_tasks')
    task = models.ForeignKey(Task, related_name='assigned_users')
    role = models.CharField(max_length=255, choices=TaskUserRoles.choices)


class TaskTag(models.Model):
    class Meta:
        unique_together = ('task_board', 'name')

    uuid = ShortUUIDField(editable=False, db_index=True, unique=True)
    task_board = models.ForeignKey(TaskBoard)
    name = models.CharField(max_length=255)


class TaskComment(TimeStampedModel):
    class Meta:
        ordering = ('created',)

    uuid = ShortUUIDField(editable=False, db_index=True, unique=True)
    task = models.ForeignKey(Task, related_name='comments')
    comment = models.TextField()
    author = models.ForeignKey('icmo_users.IcmoUser')


class TaskCheckListItem(OrderedModel, TimeStampedModel):
    uuid = ShortUUIDField(editable=False, db_index=True, unique=True)
    task = models.ForeignKey(Task, related_name='checklist')
    name = models.CharField(max_length=2048)
    completed = models.BooleanField(default=False)
    author = models.ForeignKey('icmo_users.IcmoUser')


class TaskHistory(TimeStampedModel):
    class Meta:
        ordering = ('-modified',)

    task = models.ForeignKey(Task, related_name='history')
    action = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    actor = models.ForeignKey('icmo_users.IcmoUser')
