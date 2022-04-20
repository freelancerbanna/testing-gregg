from django.contrib import admin
from django.contrib.admin import ModelAdmin
from performance.models import Campaign


class CampaignAdmin(ModelAdmin):
    list_display = ('company', 'revenue_plan', 'segment', 'program')

admin.site.register(Campaign, CampaignAdmin)
