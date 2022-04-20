from rest_framework import serializers

from core.serializers import IcmoNestedItemMixin, MoneyModelSerializer
from .models import Period


class PeriodSerializer(IcmoNestedItemMixin, MoneyModelSerializer):
    parent_class = Period

    class Meta:
        model = Period
        fields = [
            'pk', 'period', 'period_type', 'company', 'revenue_plan', 'segment',
            'program', 'custom_budget_line_item', 'campaign', 'resolution', 'order',

            'company_name', 'revenue_plan_name', 'segment_name',
            'program_name', 'custom_budget_line_item_name', 'campaign_name',

            'budget_actual', 'budget_plan', 'budget_variance', 'roi_plan', 'roi_actual',
            'roi_variance',

            'contacts_plan', 'mql_plan', 'sql_plan', 'sales_plan', 'sales_revenue_plan',
            'touches_plan', 'cost_per_mql_plan', 'cost_per_sql_plan', 'average_sale_plan',
            'touches_to_mql_conversion_plan', 'mql_to_sql_conversion_plan',
            'sql_to_sale_conversion_plan', 'touches_per_contact_plan',

            'contacts_actual', 'mql_actual', 'sql_actual', 'sales_actual',
            'sales_revenue_actual', 'touches_actual', 'cost_per_mql_actual',
            'cost_per_sql_actual', 'average_sale_actual', 'touches_to_mql_conversion_actual',
            'mql_to_sql_conversion_actual', 'sql_to_sale_conversion_actual',
            'touches_per_contact_actual',

            'contacts_variance', 'mql_variance', 'sql_variance', 'sales_variance',
            'sales_revenue_variance', 'touches_variance', 'cost_per_mql_variance',
            'cost_per_sql_variance', 'average_sale_variance', 'touches_to_mql_conversion_variance',
            'mql_to_sql_conversion_variance', 'sql_to_sale_conversion_variance',
            'touches_per_contact_variance',

            # custom
            'plan_year',

        ]
        read_only_fields = [
            'pk', 'period', 'period_type', 'company', 'revenue_plan', 'segment',
            'program', 'custom_budget_line_item', 'campaign', 'resolution', 'order',

            'budget_actual', 'budget_plan', 'budget_variance',  'roi_plan', 'roi_actual',
            'roi_variance',

            'contacts_plan', 'mql_plan', 'sql_plan', 'sales_plan', 'sales_revenue_plan',
            'touches_plan', 'cost_per_mql_plan', 'cost_per_sql_plan', 'average_sale_plan',
            'touches_to_mql_conversion_plan', 'mql_to_sql_conversion_plan',
            'sql_to_sale_conversion_plan', 'touches_per_contact_plan',

            'contacts_actual', 'mql_actual', 'sql_actual', 'sales_actual',
            'sales_revenue_actual', 'touches_actual', 'cost_per_mql_actual',
            'cost_per_sql_actual', 'average_sale_actual', 'touches_to_mql_conversion_actual',
            'mql_to_sql_conversion_actual', 'sql_to_sale_conversion_actual',
            'touches_per_contact_actual',

            'contacts_variance', 'mql_variance', 'sql_variance', 'sales_variance',
            'sales_revenue_variance', 'touches_variance', 'cost_per_mql_variance',
            'cost_per_sql_variance', 'average_sale_variance', 'touches_to_mql_conversion_variance',
            'mql_to_sql_conversion_variance', 'sql_to_sale_conversion_variance',
            'touches_per_contact_variance',

            # custom
            'plan_year',
        ]

    company = serializers.CharField(read_only=True, source='company.slug')
    company_name = serializers.CharField(read_only=True, source='company.name')
    revenue_plan = serializers.CharField(read_only=True, source='revenue_plan.slug')
    revenue_plan_name = serializers.CharField(read_only=True, source='revenue_plan.name')
    segment = serializers.CharField(read_only=True, source='segment.slug')
    segment_name = serializers.CharField(read_only=True, source='segment.name')
    program = serializers.CharField(read_only=True, source='program.slug')
    program_name = serializers.CharField(read_only=True, source='program.name')
    custom_budget_line_item = serializers.CharField(read_only=True,
                                                    source='custom_budget_line_item.slug')
    custom_budget_line_item_name = serializers.CharField(read_only=True,
                                                         source='custom_budget_line_item.name')
    campaign = serializers.CharField(read_only=True, source='campaign.slug')
    campaign_name = serializers.CharField(read_only=True, source='campaign.name')

    plan_year = serializers.IntegerField(read_only=True, source='revenue_plan.plan_year')

