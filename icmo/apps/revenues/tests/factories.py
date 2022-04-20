import factory
from factory.fuzzy import FuzzyText, FuzzyDecimal

from companies.tests.factories import CompanyFactory

from ..models import RevenuePlan, Segment


class RevenuePlanFactory(factory.DjangoModelFactory):
    class Meta:
        model = RevenuePlan

    name = FuzzyText(prefix='Test RevenuePlan')
    company = factory.SubFactory(CompanyFactory)


class SegmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Segment

    name = FuzzyText(prefix='Test Segment')
    revenue_plan = factory.SubFactory(RevenuePlanFactory)
    average_sale = FuzzyDecimal(1)
    goal_q1 = FuzzyDecimal(1)
    goal_q2 = FuzzyDecimal(1)
    goal_q3 = FuzzyDecimal(1)
    goal_q4 = FuzzyDecimal(1)
