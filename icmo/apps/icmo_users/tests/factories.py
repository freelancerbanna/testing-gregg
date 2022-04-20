import factory
from factory.fuzzy import FuzzyText

from ..models import IcmoUser


class IcmoUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = IcmoUser

    first_name = FuzzyText(prefix='UserFirst')
    last_name = FuzzyText(prefix='UserLast')
    email = factory.Sequence(lambda n: "test+%03d@test.com" % n)
