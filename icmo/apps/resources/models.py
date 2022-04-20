import datetime
import re
from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django_extensions.db.fields import ShortUUIDField, AutoSlugField
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from ordered_model.models import OrderedModel

from core.models import IcmoModel

GANTT_DEPENDENCY_TYPE_CHOICES = (
    (0, 'Finish-Finish'),
    (1, 'Finish-Start'),
    (2, 'Start-Finish'),
    (3, 'Start-Start')
)


class GanttTaskManager(TreeManager):
    def past_due(self):
        return self.get_queryset().filter(end_date__lt=timezone.now(), percent_complete__lt=100)

    def at_risk(self):
        return self.get_queryset().filter(end_date__day=timezone.now().day,
                                          end_date__month=timezone.now().month,
                                          end_date__year=timezone.now().year,
                                          percent_complete__lt=50)

    def complete(self):
        return self.get_queryset().filter(percent_complete=100)

    def on_track(self):
        excluded_pks = set(self.at_risk().values_list('pk', flat=True)) | set(
            self.past_due().values_list('pk', flat=True))
        return self.get_queryset().exclude(Q(pk__in=excluded_pks) | Q(percent_complete=100))


class GanttActiveParentsManager(TreeManager):
    # The implementation of Gantt due to the MPTT doesn't support the usual
    # DenormalizedIcmoParentsMixin implementation of this
    def get_queryset(self):
        return super(GanttActiveParentsManager, self).get_queryset().filter(
            Q(budget_line_item=None) | Q(Q(budget_line_item__program=None) |
                                         Q(budget_line_item__program__is_active=True),
                                         budget_line_item__is_active=True),
            Q(segment__is_active=True) | Q(segment=None),
            is_active=True,
        )


class RadiantGanttTask(IcmoModel):
    class Meta:
        ordering = ('company_id', 'revenue_plan_id', 'rq_sort_order')

    company = models.ForeignKey('companies.Company')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan')
    segment = models.ForeignKey('revenues.Segment', blank=True, null=True)
    past_due = models.BooleanField(default=False)
    completed_date = models.DateTimeField(blank=True, null=True)

    rq_id = models.CharField(max_length=255)
    rq_sort_order = models.SmallIntegerField(blank=True, default=0)
    rq_name = models.CharField(max_length=512, blank=True)
    rq_start_time = models.DateTimeField(blank=True)
    rq_end_time = models.DateTimeField(blank=True)
    rq_effort = models.CharField(blank=True, max_length=255)
    effort_in_seconds = models.IntegerField(blank=True, default=0)
    rq_preferred_start_time = models.DateTimeField(blank=True, null=True)
    rq_indent_level = models.SmallIntegerField(default=0)
    rq_predecessor_indices = models.TextField(blank=True)
    rq_progress_percent = models.DecimalField(blank=True, default=0, max_digits=5,
                                              decimal_places=2)
    rq_resources = models.TextField(blank=True)

    @staticmethod
    def convert_rq_effort_to_seconds(rq_effort):
        # > 24 hours the format is days.hours:minutes:seconds
        # less than 24 hours the format is hours:minutes:seconds

        matches = re.match(
            '((?P<days>[0-9]+)\.)?(?P<hours>[0-9]+):(?P<minutes>[0-9]+):(?P<seconds>[0-9]+)',
            rq_effort)
        if matches:
            bits = matches.groupdict()
            return (int(bits['days'] or 0) * 24 * 60 * 60) + \
                   (int(bits['hours']) * 60 * 60) + \
                   (int(bits['minutes']) * 60) + \
                   int(bits['seconds'])

        return 0

    @property
    def title(self):
        return self.name

    @property
    def is_past_due(self):
        if timezone.now() > self.rq_end_time and self.rq_progress_percent < Decimal('100'):
            return True
        return False

    @property
    def is_at_risk(self):
        if timezone.now().date() == self.rq_end_time.date() and self.rq_progress_percent < Decimal(
                '50'):
            return True
        return False

    @property
    def status(self):
        if self.is_past_due:
            return 'PAST_DUE'
        elif self.is_at_risk:
            return 'AT_RISK'
        elif self.is_complete:
            return 'COMPLETE'
        return 'ON_TRACK'

    @property
    def is_complete(self):
        return self.rq_progress_percent == Decimal('100')

    def save(self, *args, **kwargs):
        self.company = self.revenue_plan.company
        self.effort_in_seconds = self.convert_rq_effort_to_seconds(self.rq_effort)
        self.rq_end_time = self.rq_start_time + datetime.timedelta(seconds=self.effort_in_seconds)
        self.past_due = self.is_past_due

        if self.is_complete:
            self.completed_date = timezone.now()
        else:
            self.completed_date = None
        super(RadiantGanttTask, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s (%s - %s)" % (self.rq_name, self.rq_start_time.date(), self.rq_end_time.date())


class GanttTask(MPTTModel, OrderedModel, IcmoModel):
    class Meta:
        ordering = ('order',)
        unique_together = ('revenue_plan', 'slug')

    slug = AutoSlugField(populate_from='name')
    company = models.ForeignKey('companies.Company')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan')
    segment = models.ForeignKey('revenues.Segment', blank=True, null=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    expanded = models.BooleanField(default=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    percent_complete = models.SmallIntegerField(default=0)
    summary = models.BooleanField(default=False)
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)
    budget_line_item = models.OneToOneField('budgets.BudgetLineItem', blank=True, null=True)
    past_due = models.BooleanField(default=False)
    completed_date = models.DateTimeField(blank=True, null=True)

    objects = GanttTaskManager()
    active_parents = GanttActiveParentsManager()

    @property
    def title(self):
        if hasattr(self, 'budget_line_item') and self.budget_line_item:
            return self.budget_line_item.name
        return self.name

    @property
    def status(self):
        if self.is_past_due:
            return 'PAST_DUE'
        elif self.is_at_risk:
            return 'AT_RISK'
        elif self.is_complete:
            return 'COMPLETE'
        return 'ON_TRACK'

    @property
    def is_past_due(self):
        if timezone.now() > self.end_date and self.percent_complete < 100:
            return True
        return False

    @property
    def is_at_risk(self):
        if timezone.now().date() == self.end_date.date() and self.percent_complete < 50:
            return True
        return False

    @property
    def is_complete(self):
        return self.percent_complete == 100

    @staticmethod
    def get_or_create_task_by_budget_line_item(bli):
        if not bli:
            raise ValueError("Provided Budget Line Item argument must not be None")
        try:
            return GanttTask.objects.get(budget_line_item=bli)
        except GanttTask.DoesNotExist:
            return GanttTask.create_from_budget_line_item(bli)

    def update_order_by_budget_line_item(self, bli):
        if not bli:
            raise ValueError("Provided Budget Line Item argument must not be None")
        if bli.order > 0:
            self.above(GanttTask.objects.filter(order__lt=bli.order).first())
        else:
            self.below(GanttTask.objects.filter(order__gt=bli.order).first())

    def update_parent_by_budget_line_item(self, bli):
        if not bli:
            raise ValueError("Provided Budget Line Item argument must not be None")
        if bli.parent:
            parent_task = self.get_or_create_task_by_budget_line_item(bli.parent)
        else:
            parent_task = None  # Item has been moved to root
        self.parent = parent_task

    @staticmethod
    def create_from_budget_line_item(bli):
        parent_task = None
        summary = False
        if bli.parent:
            parent_task = GanttTask.get_or_create_task_by_budget_line_item(bli.parent)
        if bli.get_children():
            summary = True
        return GanttTask.objects.create(
            segment=bli.segment,
            parent=parent_task,
            summary=summary,
            budget_line_item=bli,
        )

    def save(self, *args, **kwargs):
        self.company = self.revenue_plan.company

        # For sanity, do not allow budget line item tasks to have a different name
        if self.budget_line_item:
            self.name = self.budget_line_item.name

        # Set the start date for imported items to the currency day at midnight (UTC).
        if not self.start_date:
            self.start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if not self.end_date:
            self.end_date = self.start_date + datetime.timedelta(days=1)
        self.past_due = self.is_past_due
        if self.pk and not self.summary:
            self.summary = self.get_children().count() > 0
        if self.budget_line_item:
            self.update_parent_by_budget_line_item(self.budget_line_item)

        if self.is_complete:
            self.completed_date = timezone.now()
        else:
            self.completed_date = None
        super(GanttTask, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete all subtasks when the parent is deleted
        # DIFFERS from budget line items!
        for child in self.get_children():
            child.delete()
        super(GanttTask, self).delete(*args, **kwargs)

    def __unicode__(self):
        return "%s (%s - %s)" % (self.name, self.start_date.date(), self.end_date.date())


class UserTask(models.Model):
    company = models.ForeignKey('companies.Company')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan')
    segment = models.ForeignKey('revenues.Segment', blank=True, null=True)
    assignment_id = ShortUUIDField(unique=True)

    task = models.ForeignKey(GanttTask)
    resource = models.ForeignKey('icmo_users.IcmoUser')
    value = models.PositiveSmallIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.revenue_plan = self.task.revenue_plan
        self.company = self.task.company
        super(UserTask, self).save(*args, **kwargs)


class GanttDependency(models.Model):
    company = models.ForeignKey('companies.Company')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan')
    segment = models.ForeignKey('revenues.Segment', blank=True, null=True)
    dependency_id = ShortUUIDField(unique=True)

    predecessor = models.ForeignKey(GanttTask, related_name='successors',
                                    blank=True, null=True)
    successor = models.ForeignKey(GanttTask, related_name='predecessors',
                                  blank=True, null=True)
    item_type = models.PositiveSmallIntegerField(choices=GANTT_DEPENDENCY_TYPE_CHOICES)

    def save(self, *args, **kwargs):
        self.company = self.revenue_plan.company
        super(GanttDependency, self).save(*args, **kwargs)


class SchedulerEvent(models.Model):
    company = models.ForeignKey('companies.Company')
    revenue_plan = models.ForeignKey('revenues.RevenuePlan', blank=True, null=True)
    gantt_task = models.OneToOneField('GanttTask', blank=True, null=True)

    icmo_user = models.ForeignKey('icmo_users.IcmoUser', blank=True, null=True)
    slug = ShortUUIDField(unique=True)

    name = models.TextField()
    description = models.TextField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)
    recurrence_exception = models.TextField(blank=True)
    recurrence = models.ForeignKey('self', blank=True, null=True)
    recurrence_rule = models.TextField(blank=True)

    @staticmethod
    def create_from_gantt_task(task):
        # todo make one for each resource
        return SchedulerEvent.objects.create(
            company=task.company,
            revenue_plan=task.revenue_plan,
            gantt_task=task,
            start_datetime=task.start_date,
            end_datetime=task.end_date,
            is_all_day=True,
        )

    def save(self, *args, **kwargs):
        # For sanity, do not allow gantt tasks to have a different name
        if self.gantt_task:
            self.name = self.gantt_task.name
            self.start_datetime = self.gantt_task.start_date
            self.end_datetime = self.gantt_task.end_date
        super(SchedulerEvent, self).save(*args, **kwargs)
