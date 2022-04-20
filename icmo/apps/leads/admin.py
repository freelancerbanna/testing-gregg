from django.contrib import admin
from django.contrib.admin import ModelAdmin

from leads.models import Program


class ProgramAdmin(ModelAdmin):
    list_display = (
        'name', 'budget'
    )


admin.site.register(Program, ProgramAdmin)
