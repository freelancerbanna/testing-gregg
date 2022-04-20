import factory

from ..models import Period


class PeriodFactory(factory.DjangoModelFactory):
    class Meta:
        model = Period
