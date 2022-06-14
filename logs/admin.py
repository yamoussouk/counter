from django.contrib import admin

from .models import LogFile


class LogFileAdmin(admin.ModelAdmin):
    list_display = ['type', 'message', 'created']
    readonly_fields = ['type', 'message', 'created']
    list_filter = ['type']
    can_delete = False

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save_and_add_another': False,
            'show_save': False,
            'show_save_and_continue': False,
            'show_delete': False
        })
        return super().render_change_form(request, context, add, change, form_url, obj)


admin.site.register(LogFile, LogFileAdmin)
