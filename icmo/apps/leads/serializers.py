from rest_framework import serializers

from core.serializers import MoneyModelSerializer, MoneyField, IcmoNestedItemMixin, \
    IcmoModelSerializerMixin, MPTTOrderedObjectSerializerMixin
from leads.models import Program
from revenues.models import Segment


class ProgramSerializer(MPTTOrderedObjectSerializerMixin, IcmoNestedItemMixin,
                        IcmoModelSerializerMixin, MoneyModelSerializer):
    parent_class = Segment

    class Meta:
        model = Program
        fields = [
            'slug',
            'name',
            'item_type',
            # data
            'touches_per_contact', 'touches_to_mql_conversion',
            'mql_to_sql_conversion', 'sql_to_sale_conversion',
            'cost_per_mql', 'marketing_mix', 'marketing_mix_locked', 'fixed_budget',
            'budget',
            # cached
            'sales_revenue', 'sales', 'sql', 'mql', 'contacts', 'touches',
            'cost_per_sql',
            'roi',
            # computed
            'max_cost_per_mql', 'q1_budget', 'q2_budget', 'q3_budget', 'q4_budget',
        ]
        read_only_fields = (
            'slug', 'segment', 'revenue_plan', 'company',
            'sales_revenue', 'sales', 'sql', 'mql', 'contacts', 'touches',
            'cost_per_sql',
            'roi',
            'max_cost_per_mql', 'q1_budget', 'q2_budget', 'q3_budget', 'q4_budget',
        )

    q1_budget = MoneyField(read_only=True, max_digits=10, decimal_places=0)
    q2_budget = MoneyField(read_only=True, max_digits=10, decimal_places=0)
    q3_budget = MoneyField(read_only=True, max_digits=10, decimal_places=0)
    q4_budget = MoneyField(read_only=True, max_digits=10, decimal_places=0)

    def validate(self, validated_data):
        validated_data = super(ProgramSerializer, self).validate(validated_data)
        if not validated_data.get('budget')[0] and validated_data.get('fixed_budget'):
            raise serializers.ValidationError("Budget is required")
        return validated_data

    def create(self, validated_data):
        validated_data = self.validate(validated_data)
        return super(ProgramSerializer, self).create(validated_data)
