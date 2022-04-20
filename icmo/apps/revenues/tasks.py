import logging
from copy import deepcopy
from decimal import Decimal

from django.db import transaction, connection
from django.db.models import Q
from django_rq import job

from periods.helpers import recompute_periods, recompute_segment_periods
from resources.models import GanttDependency
from revenues.models import RevenuePlan, Segment

logger = logging.getLogger('icmo.%s' % __name__)

COMMON_EXCLUDED_FIELDS = ('id', 'slug', 'created', 'modified', 'modified_by_id', 'revenue_plan',
                          'segment', 'revenue_plan_id', 'segment_id', 'budgetlineitem',
                          'budget_line_item_id', 'budgetlineitem_id', 'program', 'program_id',
                          'gantttask', 'gantttask_id')


@job
def clone_plan(source_plan_id, target_plan_id,
               programs, budget_plans, budget_actuals, performance_actuals,
               tasks, task_states):
    source_plan = RevenuePlan.objects.get(id=source_plan_id)
    target_plan = RevenuePlan.objects.get(id=target_plan_id)
    logger.info("Cloning plan %s to plan %s" % (source_plan, target_plan))

    with transaction.atomic():
        # Copy segments
        for source_segment in source_plan.segments.filter(is_active=True):
            new_segment = deepcopy(source_segment)
            new_segment.id = None
            new_segment.slug = ''
            new_segment.revenue_plan = target_plan
            new_segment.save()
            clone_segment(source_segment.id, new_segment.id, programs, budget_plans,
                          budget_actuals, performance_actuals,
                          tasks, task_states, trigger_recompute=False)

        # Run tasks once we are no longer in an atomic block
        connection.on_commit(lambda: recompute_periods(target_plan))
    logger.info("Plan cloned successfully.")


@job
def clone_segment(source_segment_id, target_segment_id,
                  programs, budget_plans, budget_actuals, performance_actuals,
                  tasks, task_states, trigger_recompute=True):
    source_segment = Segment.objects.get(id=source_segment_id)
    target_segment = Segment.objects.get(id=target_segment_id)
    logger.info("Cloning segment %s to segment %s" % (source_segment, target_segment))

    # We keep a mapping of the old object ids to the new ones so we can reestablish
    # relationships and nesting
    budgetlineitem_map = dict()
    program_map = dict()
    gantttask_map = dict()

    # We approach objects in a variety of ways because some objects create other objects on
    # save, for example programs create budget line items which create ganttasks.

    with transaction.atomic():
        # Copy programs as deep as required
        if programs:
            for source_program in source_segment.programs.filter(is_active=True):
                new_program = deepcopy(source_program)
                new_program.id = None
                new_program.slug = ''
                new_program.segment = target_segment
                # budgetlineitem doesn't copy over anyway, so null it out so the normal signal will
                # create a new budget line item
                new_program.save()
                # reload the obj to get the new budgetlineitem
                new_program.refresh_from_db()
                program_map[source_program.id] = new_program
                budgetlineitem_map[
                    source_program.budgetlineitem.id] = new_program.budgetlineitem
                gantttask_map[
                    source_program.budgetlineitem.gantttask.id] = \
                    new_program.budgetlineitem.gantttask

                if budget_plans:
                    # Copy the plan and optionally actual values over to the new budget item
                    for attr, value in source_program.budgetlineitem.__dict__.iteritems():
                        if '_plan' in attr or (budget_actuals and '_actual' in attr):
                            setattr(new_program.budgetlineitem, attr, value)
                    new_program.budgetlineitem.save()

                # Copy the program->budgetlinitem tasks
                if tasks:
                    new_gantttask = new_program.budgetlineitem.gantttask
                    source_gantttask = source_program.budgetlineitem.gantttask
                    new_gantttask.start_date = source_gantttask.end_date
                    new_gantttask.end_date = source_gantttask.end_date
                    new_gantttask.expanded = source_gantttask.expanded
                    if task_states:
                        new_gantttask.past_due = source_gantttask.past_due
                        new_gantttask.percent_complete = source_gantttask.percent_complete
                        new_gantttask.completed_date = source_gantttask.completed_date
                    new_gantttask.save()

                # Create the program campaigns
                if performance_actuals:
                    for source_campaign in source_program.campaigns.all():
                        new_campaign = deepcopy(source_campaign)
                        new_campaign.id = None
                        new_campaign.slug = ''
                        new_campaign.segment = target_segment
                        new_campaign.program = new_program
                        new_campaign.save()

            # Restore the program parents
            for source_program in source_segment.programs.all():
                if source_program.parent_id and source_program.id in \
                        program_map:
                    program_map[source_program.id].parent = program_map[
                        source_program.parent_id]
                    program_map[source_program.id].save()

        # Copy category and custom budget line items
        if budget_plans:
            for source_budget_line_item in source_segment.budgets.all():
                new_budget_line_item = deepcopy(source_budget_line_item)
                new_budget_line_item.id = None
                new_budget_line_item.slug = ''
                new_budget_line_item.segment = target_segment
                if not budget_actuals:
                    # Null out of the actuals if we aren't copying them
                    for attr in new_budget_line_item.__dict__.keys():
                        if '_actual' in attr:
                            setattr(new_budget_line_item, attr, Decimal(0))
                new_budget_line_item.save()
                budgetlineitem_map[source_budget_line_item.id] = new_budget_line_item
                gantttask_map[
                    source_budget_line_item.gantttask.id] = new_budget_line_item.gantttask

            # Restore the budget parents
            for source_budget_line_item in source_segment.budgets.all():
                if source_budget_line_item.parent_id and source_budget_line_item.id in \
                        budgetlineitem_map:
                    budgetlineitem_map[source_budget_line_item.id].parent = budgetlineitem_map[
                        source_budget_line_item.parent_id]
                    budgetlineitem_map[source_budget_line_item.id].save()

        # Copy custom tasks
        if tasks:
            for source_task in source_segment.gantttask_set.filter(is_active=True,
                                                                   budget_line_item=None):
                new_task = deepcopy(source_task)
                new_task.id = None
                new_task.slug = ''
                new_task.segment = target_segment
                new_task.expanded = source_task.expanded
                if not task_states:
                    new_gantttask.past_due = False
                    new_gantttask.percent_complete = 0
                    new_gantttask.completed_date = None
                new_task.save()
                gantttask_map[source_task.id] = new_gantttask

            # Restore task parents (done automatically for budgetlineitem tasks)
            for source_task in source_segment.gantttask_set.filter(is_active=True,
                                                                   budget_line_item=None):
                if source_task.parent:
                    gantttask_map[source_task.id].parent = gantttask_map.get(source_task.parent_id)
                    gantttask_map[source_task.id].save()

            # Create task dependencies.
            for source_dep in source_segment.ganttdependency_set.filter(
                            Q(predecessor=None) | Q(predecessor__is_active=True),
                            Q(successor=None) | Q(successor__is_active=True)):
                predecessor = gantttask_map[
                    source_dep.predecessor_id] if source_dep.predescessor else None
                successor = gantttask_map[
                    source_dep.successor_id] if source_dep.successor else None

                GanttDependency.objects.create(
                    segment=target_segment,
                    predecessor=predecessor,
                    successor=successor,
                    item_type=source_dep.item_type
                )
        # Run tasks once we are no longer in an atomic block
        if trigger_recompute:
            connection.on_commit(lambda: recompute_segment_periods(target_segment))
    logger.info("Segment cloned successfully.")
