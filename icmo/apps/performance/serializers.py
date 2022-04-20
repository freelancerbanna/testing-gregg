from core.helpers import ALL_TIME_PERIODS
from core.serializers import MoneyModelSerializer, IcmoNestedItemMixin, IcmoModelSerializerMixin
from leads.models import Program
from .models import Campaign


class CampaignSerializer(IcmoNestedItemMixin, IcmoModelSerializerMixin, MoneyModelSerializer):
    parent_class = Program

    class Meta:
        model = Campaign
        fields = [
            'slug',
            'name', 'source',
        ]
        read_only_fields = [
            'slug',
            'source',
        ]

    def __init__(self, *args, **kwargs):
        fields = (
            'mql', 'sql', 'sales', 'sales_revenue', 'average_sale',
            'mql_to_sql_conversion', 'sql_to_sale_conversion'
        )
        # read only
        read_only_fields = (
        'average_sale', 'mql_to_sql_conversion', 'sql_to_sale_conversion'
        )
        for time_period in ALL_TIME_PERIODS:
            for field in fields:
                self.Meta.fields.append('%s_%s' % (time_period, field))
                if field in read_only_fields or time_period in (
                        'q1', 'q2', 'q3', 'q4', 'fiscal_year'):
                    self.Meta.read_only_fields.append('%s_%s' % (time_period, field))
        super(CampaignSerializer, self).__init__(*args, **kwargs)
