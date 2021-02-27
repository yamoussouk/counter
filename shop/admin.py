from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Collection, Product, Image, Notification, ProductType, GiftCard, Message


class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name']
    fields = ('name', 'image', 'available', 'custom', 'show_on_home_page')


admin.site.register(Collection, CollectionAdmin)


class ProductImageAdmin(admin.StackedInline):
    model = Image
    extra = 0


class ProductTypeInline(admin.StackedInline):
    model = ProductType
    extra = 0


def generate_stripe_product(obj):
    return mark_safe('<span data-id={} style="cursor:pointer;">Generate</span>'.format(obj.id))


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin, ProductTypeInline]
    list_display = ['name', 'collection', 'studs', 'price', 'stock', 'available', 'created', 'updated', 'custom',
                    generate_stripe_product]
    list_filter = ['available', 'created', 'updated', 'collection', 'custom']
    list_editable = ['price', 'available']
    fields = ('collection', 'name', 'image', 'description', 'size', 'price', 'custom', 'studs', 'key_ring',
              'custom_date', 'initials', 'available', 'stock', 'price_api_id')

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '/static/admin/js/hide_attribute.js'
        )


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
