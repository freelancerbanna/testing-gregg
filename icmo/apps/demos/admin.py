from django.contrib import admin
from django.contrib import messages

from demos.models import DemoAccount


class DemoAccountAdmin(admin.ModelAdmin):
    list_display = ('company', 'template', 'email', 'password', 'created')
    readonly_fields = ('company',)

    def save_model(self, request, obj, form, change):
        messages.success(request, 'Account has been created.  You may log in now.  '
                                  'The revenue plan you selected is being computed '
                                  'and will be available in a few minutes.')
        super(DemoAccountAdmin, self).save_model(request, obj, form, change)


admin.site.register(DemoAccount, DemoAccountAdmin)
