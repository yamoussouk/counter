from django.contrib import admin

from .models import BoughtGiftCard


class BoughtGiftCardAdmin(admin.ModelAdmin):
    list_display = ['unique_uuid', 'price', 'active', 'bought', 'email']
    list_editable = ['active']
    # fields = ['name', 'price', 'price_api_id', 'available']


admin.site.register(BoughtGiftCard, BoughtGiftCardAdmin)
