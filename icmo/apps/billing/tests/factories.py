import factory

from icmo_users.tests.factories import IcmoUserFactory
from ..models import BillingAccount


class BillingAccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = BillingAccount

    owner = factory.SubFactory(IcmoUserFactory)
