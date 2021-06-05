from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.text import slugify

from .models import Collection, Product, Image, Notification, ProductType, GiftCard, Message


class CollectionAdmin(admin.ModelAdmin):
    error_while_saving = False
    list_display = ['name']
    fields = ('name', 'image', 'available', 'custom', 'show_on_home_page', 'basic_collection', 'regular_collection')

    def save_model(self, request, obj, form, change):
        slug = slugify(obj.name)
        collection = Collection.objects.get(slug=slug)
        if collection is not None:
            self.error_while_saving = True
            msg = f"Collection with the given name \"{obj.name}\" already exists."
            self.message_user(request, msg, messages.WARNING)
        else:
            super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        if self.error_while_saving:
            return HttpResponseRedirect("/admin/shop/collection/add/")
        else:
            return super(CollectionAdmin, self).response_add(request, obj, post_url_continue)


admin.site.register(Collection, CollectionAdmin)


class ProductImageAdmin(admin.StackedInline):
    model = Image
    extra = 0


class ProductTypeInline(admin.StackedInline):
    model = ProductType
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    error_while_saving = False
    inlines = [ProductImageAdmin, ProductTypeInline]
    list_display = ['name', 'collection', 'studs', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'collection', 'custom']
    list_editable = ['price', 'available']
    fields = ('collection', 'name', 'image', 'description', 'size', 'price', 'custom', 'studs', 'key_ring',
              'custom_date', 'initials', 'available', 'stock', 'price_api_id')

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '/static/admin/js/hide_attribute.js'
        )

    def save_model(self, request, obj, form, change):
        slug = slugify(obj.name)
        product = Product.objects.get(slug=slug)
        if product is not None:
            self.error_while_saving = True
            msg = f"Product with the given name \"{obj.name}\" already exists."
            self.message_user(request, msg, messages.WARNING)
        else:
            super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        if self.error_while_saving:
            return HttpResponseRedirect("/admin/shop/product/add/")
        else:
            return super(ProductAdmin, self).response_add(request, obj, post_url_continue)


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
