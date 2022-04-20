from django.utils import timezone
from django_rq import job

from companies.models import Company
from demos.helpers import create_sample_revenue_plan
from demos.plan_templates import SampleRevenuePlanTemplate


@job
def task_create_demo_revenue_plan(company_id, template):
    company = Company.objects.get(id=company_id)
    create_sample_revenue_plan(company, template, timezone.now().year, prefix='Demo',
                               published=True)


@job
def task_create_sample_revenue_plan(company_id):
    company = Company.objects.get(id=company_id)
    create_sample_revenue_plan(company, SampleRevenuePlanTemplate, timezone.now().year,
                               prefix='Sample', published=False)
