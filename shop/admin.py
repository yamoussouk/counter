from django.contrib import admin

from .models import Collection, Product, Image, Notification, ProductType, GiftCard, Message


class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name']
    # prepopulated_fields = {'slug': ('name',)}


admin.site.register(Collection, CollectionAdmin)


class ProductImageAdmin(admin.StackedInline):
    model = Image
    extra = 0


class ProductTypeInline(admin.StackedInline):
    model = ProductType
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin, ProductTypeInline]
    list_display = ['name', 'collection', 'studs', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'collection']
    list_editable = ['price', 'available']
    # prepopulated_fields = {'slug': ('name',)}


admin.site.register(Product, ProductAdmin)


class ImageAdmin(admin.ModelAdmin):
    list_display = ['product']
    extra = 0


admin.site.register(Image, ImageAdmin)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'text']


admin.site.register(Notification, NotificationAdmin)


class GiftCardAdmin(admin.ModelAdmin):
    list_display = ['name', 'available']
    list_editable = ['available']
    fields = ['name', 'price', 'price_api_id', 'available']


admin.site.register(GiftCard, GiftCardAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'subject', 'email', 'message', 'created', 'sent']


admin.site.register(Message, MessageAdmin)
