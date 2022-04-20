# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import RevenuePlan, Segment


class RevenuePlanAdmin(admin.ModelAdmin):
    list_display = (
        'company',
        'plan_year',
        'name',
        'plan_type',
        'created',
        'modified',
        'is_active',
        'modified_by',
        'is_default',
    )
    list_filter = (
        'created',
        'modified',
        'is_active',
        'modified_by',
        'company',
        'is_default',
    )
    search_fields = ('name',)


admin.site.register(RevenuePlan, RevenuePlanAdmin)


class SegmentAdmin(admin.ModelAdmin):
    list_display = (
        'company',
        'revenue_plan',
        'name',
        'average_sale_currency',
        'average_sale',
        'goal_q1_currency',
        'goal_q1',
        'goal_q2_currency',
        'goal_q2',
        'goal_q3_currency',
        'goal_q3',
        'goal_q4_currency',
        'goal_q4',
        'goal_annual_currency',
        'goal_annual',
        'created',
        'modified',
        'is_active',
        'modified_by',
    )
    list_filter = (
        'created',
        'modified',
        'is_active',
        'modified_by',
        'company',
        'revenue_plan',
    )
    search_fields = ('name',)


admin.site.register(Segment, SegmentAdmin)
