from __future__ import division

import datetime
import logging
from math import ceil
from random import randint

from django.db import transaction, connection
from django.utils import timezone

from billing.models import BillingAccount
from budgets.models import BudgetLineItem
from companies.models import Company
from core.helpers import MONTHS_3
from icmo_users.models import IcmoUser
from leads.models import Program
from performance.models import Campaign
from periods.helpers import recompute_periods, split_integer_into_segment_months
from resources.models import GanttTask
from revenues.models import RevenuePlan, Segment

logger = logging.getLogger('icmo.%s' % __name__)


def create_demo_company(name, email, password='demo'):
    logger.info("Creating demo company %s for email %s and password %s" % (name, email, password))
    with transaction.atomic():
        # Get or Create the User Account
        user = IcmoUser.get_or_create_user(email, 'Alex', 'Williams', password)

        # Create the Billing Account
        billing_account, created = BillingAccount.objects.get_or_create(
            owner=user
        )
        company = Company.objects.create(
            name=name,
            account=billing_account,
            address1='123 Demo Street',
            city='Demotown',
            state='CA',
            zip='123456'
        )
        # Save the company to the billing account as the contact company
        billing_account.company = company
        billing_account.save()

        # Save the company to the user as his Employer
        user.employer = company.name
        user.save()

        # Add the user as an owner to the new company
        company.assign_owner(user)

        # Create Fake Revenue Plans
        current_year = timezone.now().year
        RevenuePlan.objects.create(company=company, plan_year=current_year, plan_type='draft',
                                   name='Revenue Plan %d Opt A' % (current_year + 1))
        RevenuePlan.objects.create(company=company, plan_year=current_year, plan_type='draft',
                                   name='Revenue Plan %d Opt B' % (current_year + 1))

        RevenuePlan.objects.create(company=company, plan_year=(current_year - 1),
                                   plan_type='archived',
                                   name='Revenue Plan %d' % (current_year - 1))
        RevenuePlan.objects.create(company=company, plan_year=(current_year - 2),
                                   plan_type='archived',
                                   name='Revenue Plan %d' % (current_year - 2))
        # Create the dummy users
        user1 = IcmoUser.get_or_create_user(email.replace('@', '-user1@'), 'John', 'Doe', password)
        user2 = IcmoUser.get_or_create_user(email.replace('@', '-user2@'), 'Jane', 'Smith',
                                            password)
        user3 = IcmoUser.get_or_create_user(email.replace('@', '-user3@'), 'Joe', 'Garcia',
                                            password)
        company.assign_user(user1, 'Admin', title='Marketing Director')
        company.assign_user(user2, 'Planner', title='Marketing Manager')
        company.assign_user(user3, 'Updater', title='Marketing Admin')
    logger.info("Demo company created succesfully")
    return company


CAMPAIGN_FIELDS = (
    'cost', 'contacts', 'mql', 'sql', 'sales', 'sales_revenue', 'touches'
)


def create_sample_revenue_plan(company, template, year, prefix=None, published=False):
    # Note: This will disable enqueing of all tasks for IcmoModels (see signals, IcmoModel)
    # Therefore a manual recompute_periods will have to be called at the end.
    logger.info("Creating sample revenue plan for company %s using template %s for year %s" % (
        company, template, year))
    if not prefix:
        prefix = 'Sample'
    if published:
        plan_type = 'published'
    else:
        plan_type = 'draft'

    with transaction.atomic():
        revenue_plan = RevenuePlan.objects.create(
            company=company,
            name='%s Revenue Plan %s' % (prefix, year),
            plan_year=year,
            is_default=True,
            plan_type=plan_type
        )
        print 'plan created'
        # Create Segments
        for seg_tpl in template.segments:
            segment = Segment.objects.create(
                company=company,
                revenue_plan=revenue_plan,
                name=seg_tpl['name'],
                goal_q1=seg_tpl['target'] * template.quarter_shares[0],
                goal_q2=seg_tpl['target'] * template.quarter_shares[1],
                goal_q3=seg_tpl['target'] * template.quarter_shares[2],
                goal_q4=seg_tpl['target'] * template.quarter_shares[3],
                average_sale=seg_tpl['average_sale'],

                prev_q1=seg_tpl['target'] * template.quarter_shares[0]
                        * template.get_random_growth_multiplier(),
                prev_q2=seg_tpl['target'] * template.quarter_shares[1]
                        * template.get_random_growth_multiplier(),
                prev_q3=seg_tpl['target'] * template.quarter_shares[2]
                        * template.get_random_growth_multiplier(),
                prev_q4=seg_tpl['target'] * template.quarter_shares[3]
                        * template.get_random_growth_multiplier(),
                prev_average_sale=seg_tpl['average_sale'] * template.get_random_growth_multiplier()
            )
            print 'segment created'
            # Create Lead Mix Budget Category
            lead_mix_category = BudgetLineItem.objects.create(
                company=company,
                revenue_plan=revenue_plan,
                segment=segment,
                name='Programs',
                item_type='category',
            )
            print 'lead mix category created'
            # Create other budget categories and custom line items
            for category_name, items in template.custom_budget_line_items.items():
                category = BudgetLineItem.objects.create(
                    company=company,
                    revenue_plan=revenue_plan,
                    segment=segment,
                    name=category_name,
                    item_type='category',
                )
                print 'custom category created'
                for item in items:
                    bli = BudgetLineItem.objects.create(
                        company=company,
                        revenue_plan=revenue_plan,
                        segment=segment,
                        name=item['name'],
                        item_type='custom',
                        parent=category
                    )
                    for month in MONTHS_3:
                        plan_field = "%s_plan" % month
                        actual_field = "%s_actual" % month
                        setattr(bli, plan_field, item['cost_per_month'])
                        setattr(bli, actual_field,
                                item[
                                    'cost_per_month'] *
                                template.get_random_budget_actuals_fuzz_multiplier())
                    bli.save()
                    print 'custom line item created'

            # Create Programs
            seg_progs = template.get_random_program_set()
            for prog_tpl in seg_progs:
                program = Program.objects.create(
                    company=company,
                    revenue_plan=revenue_plan,
                    segment=segment,
                    name=prog_tpl['name'],
                    cost_per_mql=template.cost_per_lead,
                    marketing_mix=prog_tpl['share'],
                    marketing_mix_locked=True
                )
                print 'program created'
                # the program will have created the budget item on save
                for month in MONTHS_3:
                    actual_field = "%s_actual" % month
                    plan_field = "%s_plan" % month
                    plan_value = getattr(program.budgetlineitem, plan_field)
                    actual_value = plan_value * \
                                   template.get_random_budget_actuals_fuzz_multiplier()
                    setattr(program.budgetlineitem, actual_field, actual_value)
                program.budgetlineitem.parent = lead_mix_category
                program.budgetlineitem.save()
                print 'program budget item created'

                # Create Campaigns
                num_campaigns = min(template.get_random_campaigns_per_program(), program.sales)
                program_targets = dict(
                    cost=program.budget,
                    mql=program.mql,
                    sql=program.sql,
                    sales=program.sales,
                    sales_revenue=program.sales_revenue,
                    touches=program.touches,
                    contacts=program.contacts,
                )
                program_targets = {
                    k: v * template.get_random_campaign_actuals_fuzz_multiplier()
                    for k, v in program_targets.items()
                    }
                for i in range(0, num_campaigns):
                    # Fuzz the targets

                    campaign = Campaign.objects.create(
                        company=company,
                        revenue_plan=revenue_plan,
                        segment=segment,
                        program=program,
                        name='Campaign %s' % str(i + 1),
                    )

                    # divy up the fuzzed actual values by weighted month/quarters,
                    # without rounding errors
                    divided_fields_values = dict()
                    for field in CAMPAIGN_FIELDS:
                        field_value = program_targets[field]
                        if field in ('cost', 'sales_revenue'):
                            field_value = field_value.amount
                        field_value = int(ceil(field_value / num_campaigns))
                        divided_fields_values[field] = split_integer_into_segment_months(
                            field_value, program.segment
                        )
                    # Assign the divided values to the campaign month fields
                    for idx, month in enumerate(company.fiscal_months_by_name):
                        for field in CAMPAIGN_FIELDS:
                            actual_field = '%s_%s' % (month, field)
                            setattr(campaign, actual_field, divided_fields_values[field][idx])
                    campaign.save()
                    print 'campaign created'
        # Stagger Gantt Tasks
        days_start = 0
        for task in GanttTask.objects.filter(revenue_plan=revenue_plan):
            rand_length = randint(1, 10)
            task.start_date = task.start_date + datetime.timedelta(days=days_start)
            task.end_date = task.start_date + datetime.timedelta(days=rand_length)
            days_start = rand_length
            task.save()

        # Run tasks once we are no longer in an atomic block
        connection.on_commit(lambda: recompute_periods(revenue_plan))

    logger.info("Sample revenue plan created")
    return revenue_plan
