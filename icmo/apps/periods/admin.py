from django.contrib import admin
from django.contrib.admin import ModelAdmin

from periods.models import Period


class PeriodAdmin(ModelAdmin):
    list_display = (
        'period', 'period_type',
        'company', 'revenue_plan', 'segment',  # 'category',
        'program', 'custom_budget_line_item', 'campaign',
        'resolution', 'budget_plan', 'budget_actual', 'budget_variance',
        'sql_plan', 'sql_actual', 'sql_variance', 'mql_to_sql_conversion_plan'
    )
    list_filter = ('company', 'revenue_plan', 'segment',  # 'category',
        'program', 'custom_budget_line_item', 'campaign',
        'resolution', 'period')


admin.site.register(Period, PeriodAdmin)
