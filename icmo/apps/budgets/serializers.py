from rest_framework import serializers

from core.serializers import MoneyModelSerializer, IcmoModelSerializerMixin, IcmoNestedItemMixin, \
    MPTTOrderedObjectSerializerMixin
from revenues.models import Segment
from .models import BudgetLineItem


class BudgetLineItemSerializer(IcmoNestedItemMixin,
                               MPTTOrderedObjectSerializerMixin,
                               IcmoModelSerializerMixin,
                               MoneyModelSerializer):
    parent_class = Segment

    class Meta:
        model = BudgetLineItem
        fields = (
            'slug', 'program', 'segment', 'revenue_plan', 'company',
            'name', 'item_type', 'is_moveable', 'automatic_distribution',
            # data
            'jan_actual', 'feb_actual', 'mar_actual', 'apr_actual', 'may_actual', 'jun_actual',
            'jul_actual', 'aug_actual', 'sep_actual', 'oct_actual', 'nov_actual', 'dec_actual',
            'jan_plan', 'feb_plan', 'mar_plan', 'apr_plan', 'may_plan', 'jun_plan', 'jul_plan',
            'aug_plan', 'sep_plan', 'oct_plan', 'nov_plan', 'dec_plan',
            # cached
            'jan_variance', 'feb_variance', 'mar_variance', 'apr_variance', 'may_variance',
            'jun_variance', 'jul_variance', 'aug_variance', 'sep_variance', 'oct_variance',
            'nov_variance', 'dec_variance',
            'q1_actual', 'q1_plan', 'q1_variance', 'q2_actual', 'q2_plan', 'q2_variance',
            'q3_actual', 'q3_plan', 'q3_variance', 'q4_actual', 'q4_plan', 'q4_variance',
            'fiscal_year_actual', 'fiscal_year_plan', 'fiscal_year_variance',
            # calculated
        )
        read_only_fields = (
            'slug', 'program', 'segment', 'revenue_plan', 'company', 'is_moveable',
            # cached
            'jan_variance', 'feb_variance', 'mar_variance', 'apr_variance', 'may_variance',
            'jun_variance', 'jul_variance', 'aug_variance', 'sep_variance', 'oct_variance',
            'nov_variance', 'dec_variance',
            'q1_actual', 'q1_plan', 'q1_variance', 'q2_actual', 'q2_plan', 'q2_variance',
            'q3_actual', 'q3_plan', 'q3_variance', 'q4_actual', 'q4_plan', 'q4_variance',
            'fiscal_year_actual', 'fiscal_year_plan', 'fiscal_year_variance',
        )

    program = serializers.CharField(read_only=True, required=False, source='program.slug')
