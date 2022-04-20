import logging

import django_rq
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from budgets.models import BudgetLineItem, BudgetTypes
from companies.models import Company
from core.models import icmo_object_deactivated, icmo_object_activated, IcmoModel
from leads.models import Program, ProgramTypes
from performance.models import Campaign
from periods.helpers import periodunique
from periods.models import Period
from revenues.models import RevenuePlan, Segment
from . import tasks

logger = logging.getLogger('icmo.%s' % __name__)


# Handles all data cache recalculations for icmo models, in one place, for clarity
# Makes use of the django-dirtyfields app to try to limit saves to just those
# necessary to propagate all changes and refresh all cached values.  Requires
# that each model have a save method that prevents saves if there are no
# dirty values ex:
# def save(self, *args, **kwargs):
#   if not self.get_dirty_fields():
#       return False
#   super(MyModelName, self).save(*args, **kwargs)


# To prevent both inefficient period recalculation and more importantly calculation
# failures caused by tasks being fired inside of a transaction
# (when the objects they refer to may not exist in the db yet!)
# each handler that needs to fire off a period recallculation task shoudl check
# the `do_not_enqueue` property of the instance first.

@receiver(post_save, sender=Company, dispatch_uid='company_post_save_handler')
def company_post_save_handler(sender, instance, *args, **kwargs):
    if 'fiscal_year_start' in instance.get_dirty_fields():
        # Budget fields use fiscal years to determine monthly planned budget
        [x.save() for x in BudgetLineItem.objects.filter(company=instance)]


@receiver(post_save, sender=RevenuePlan, dispatch_uid='revenue_plan_post_save_handler')
def revenue_plan_post_save_handler(sender, instance, *args, **kwargs):
    if set(instance.get_dirty_fields().keys()) - {'name', 'created', 'modified', 'modified_by'}:
        pass


@receiver(post_save, sender=Segment, dispatch_uid='plan_segment_post_save_handler')
def plan_segment_post_save_handler(sender, instance, *args, **kwargs):
    # Data fields trigger downwards propagation
    if {'average_sale', 'goal_q1', 'goal_q2', 'goal_q3', 'goal_q4'} & set(
            instance.get_dirty_fields()):
        [x.save() for x in instance.programs.all()]


@receiver(post_save, sender=Program, dispatch_uid='program_post_save_handler')
def program_post_save_handler(sender, instance, *args, **kwargs):
    dirty_fields = set(instance.get_dirty_fields(True).keys()) - {'created', 'modified',
                                                                  'modified_by', 'rght', 'lft',
                                                                  'tree_id'}

    if instance.item_type == ProgramTypes.PROGRAM \
            and instance.parent and dirty_fields and 'parent' not in dirty_fields:
        # update channels when children are saved, except when they are moved as that
        # will be handled by the generic move signal (core.signals.post_move_handler)
        instance.parent.save()

    if not hasattr(instance, 'budgetlineitem'):
        BudgetLineItem.objects.create(segment=instance.segment, program=instance,
                                      do_not_enqueue=instance.do_not_enqueue)
    elif instance.item_type == ProgramTypes.CATEGORY and 'name' in dirty_fields:
        # Only save down from a channel when the name changes, nothing else should propagate
        # downwards
        instance.budgetlineitem.name = instance.name
        instance.budgetlineitem.save(update_fields=('name',))
    elif instance.item_type == ProgramTypes.PROGRAM and dirty_fields:
        instance.budgetlineitem.save()
    if not instance.do_not_enqueue and instance.is_active and instance.item_type != \
            ProgramTypes.CATEGORY:  # do not create periods for categories
        periodunique(tasks.update_or_create_month_periods_from_program, instance)


@receiver(post_save, sender=BudgetLineItem, dispatch_uid='budget_line_item_post_save_handler')
def budget_line_item_post_save_handler(sender, instance, *args, **kwargs):
    dirty_fields = set(instance.get_dirty_fields(True).keys()) - {'name', 'created', 'modified',
                                                                  'modified_by'}
    if dirty_fields:
        if not instance.do_not_enqueue and instance.is_active and instance.item_type != \
                BudgetTypes.CATEGORY:  # do not create periods for categories
            django_rq.enqueue(tasks.update_or_create_month_periods_from_budget_line_item, instance)


@receiver(post_save, sender=Campaign, dispatch_uid='campaign_post_save_handler')
def campaign_post_save_handler(sender, instance, *args, **kwargs):
    if set(instance.get_dirty_fields()) - {'name', 'created', 'modified', 'modified_by'}:
        if not instance.do_not_enqueue and instance.is_active:
            periodunique(tasks.update_or_create_month_periods_from_campaign, instance)


@receiver(post_save, sender=Period, dispatch_uid='period_post_save_handler')
def period_post_save_handler(sender, instance, *args, **kwargs):
    pass


@receiver(icmo_object_deactivated, dispatch_uid='post_deactivation_handler')
def post_deactivation_handler(sender, instance, *args, **kwargs):
    logger.info("Clearing Periods for deactivated %s" % instance)
    if hasattr(instance, 'period_set'):
        instance.period_set.all().delete()
    # Company is deactivated then?  nothing, whole tree is already deleted
    # Campaign is deactivated?  recalculate the world
    # Program is deactivated?  Recalculate segment on up
    # So Rule is recalculate parent on up
    if isinstance(instance, IcmoModel) and hasattr(instance, 'icmo_parent_level'):
        if not instance.do_not_enqueue:
            logger.info("Recalculating parent Periods for deactivated %s" % instance)
            django_rq.enqueue(tasks.recompute_month_periods, instance.icmo_parent_level,
                              instance.icmo_parent_id)


@receiver(post_delete, dispatch_uid='post_delete_handler')
def post_delete_handler(sender, instance, *args, **kwargs):
    # Although all related periods will be removed, the period parent still needs to be
    # tasked iwth recomputing or it will be inaccurate
    if isinstance(instance, IcmoModel) and hasattr(instance, 'icmo_parent_level'):
        if not instance.do_not_enqueue:
            logger.info("Recalculating parent Periods for deleted %s" % instance)
            django_rq.enqueue(tasks.recompute_month_periods, instance.icmo_parent_level,
                              instance.icmo_parent_id)


@receiver(icmo_object_activated, dispatch_uid='post_activation_handler')
def post_activation_handler(sender, instance, *args, **kwargs):
    # nothing needs to be done here because when the instance changes it's is_active
    # value the normal post_save handler will fire.
    pass


@receiver(post_save, dispatch_uid='post_save_resave_parents_handler')
def post_save_resave_parents_handler(sender, instance, *args, **kwargs):
    if hasattr(instance, 'parent') and instance.parent:
        instance.parent.save()
