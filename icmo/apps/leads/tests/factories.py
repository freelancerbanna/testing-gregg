from decimal import Decimal

import factory
from factory.fuzzy import FuzzyText, FuzzyDecimal, FuzzyInteger

from ..models import Program
from revenues.tests.factories import SegmentFactory


class ProgramFactory(factory.DjangoModelFactory):
    class Meta:
        model = Program

    segment = factory.SubFactory(SegmentFactory)
    name = FuzzyText(prefix='Test Program')
    touches_per_contact = FuzzyInteger(1, 32767)
    touches_to_mql_conversion = FuzzyDecimal(Decimal('0.1'), 1)
    mql_to_sql_conversion = FuzzyDecimal(Decimal('0.1'), 1)
    sql_to_sale_conversion = FuzzyDecimal(Decimal('0.1'), 100)
    cost_per_mql = FuzzyDecimal(1, 100000)
    marketing_mix = FuzzyInteger(1, 100)
