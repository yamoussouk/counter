from django.contrib import admin

from .models import Parameter


class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']


admin.site.register(Parameter, ParameterAdmin)
