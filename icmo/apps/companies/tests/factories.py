import factory
from factory.fuzzy import FuzzyText
from billing.tests.factories import BillingAccountFactory

from ..models import Company


class CompanyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Company

    name = FuzzyText(prefix='Test Company')
    account = factory.SubFactory(BillingAccountFactory)