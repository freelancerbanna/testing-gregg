from dirtyfields import DirtyFieldsMixin
from django.db import models
from django_extensions.db.models import TimeStampedModel

from demos.plan_templates import FourMRevenuePlanTemplate, TenMRevenuePlanTemplate
from .helpers import create_demo_company
from .tasks import task_create_demo_revenue_plan


class REVENUE_PLAN_TEMPLATES:
    TenM = '10M'
    FourM = '4M'


REVENUE_PLAN_TEMPLATE_MAP = {
    REVENUE_PLAN_TEMPLATES.TenM: TenMRevenuePlanTemplate,
    REVENUE_PLAN_TEMPLATES.FourM: FourMRevenuePlanTemplate
}

REVENUE_PLAN_TEMPLATE_CHOICES = (
    (REVENUE_PLAN_TEMPLATES.TenM, '$10 Million Company'),
    (REVENUE_PLAN_TEMPLATES.FourM, '$4 Million Company'),
)


class DemoAccount(DirtyFieldsMixin, TimeStampedModel):
    company_name = models.CharField(max_length=255)
    email = models.EmailField(
        help_text='This should be an email that does not yet exist on the system.')
    password = models.CharField(max_length=255, default='icmo')
    template = models.CharField(max_length=255, choices=REVENUE_PLAN_TEMPLATE_CHOICES,
                                default=REVENUE_PLAN_TEMPLATES.TenM)
    company = models.ForeignKey('companies.Company', editable=False)

    def save(self, *args, **kwargs):
        created = not self.pk
        if created:
            self.company = create_demo_company(self.company_name, self.email, self.password)
        super(DemoAccount, self).save(*args, **kwargs)
        if created:
            task_create_demo_revenue_plan.delay(self.company.id,
                                                REVENUE_PLAN_TEMPLATE_MAP[self.template])
