from django.contrib import admin
from django.contrib.admin import ModelAdmin
from budgets.models import BudgetLineItem


class PeriodAdmin(ModelAdmin):
    list_display = ('company', 'revenue_plan', 'segment', 'item_type', 'name', 'program')
    list_filter = ('company',)

admin.site.register(BudgetLineItem, PeriodAdmin)
