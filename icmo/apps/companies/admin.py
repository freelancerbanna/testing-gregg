from django.contrib import admin

from .models import CompanyUser, Company, CompanyUserGroup


class CompanyUserInline(admin.TabularInline):
    model = CompanyUser
    extra = 1


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'country')
    list_filter = ('country',)
    inlines = [CompanyUserInline]


class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'company', 'is_active')
    list_filter = ('company', 'is_active')


class CompanyUserGroupAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'is_active')
    list_filter = ('company', 'is_active')


admin.site.register(Company, CompanyAdmin)

admin.site.register(CompanyUser, CompanyUserAdmin)
admin.site.register(CompanyUserGroup, CompanyUserGroupAdmin)
