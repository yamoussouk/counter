from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from django.conf import settings
import os
import re

from .models import Collection, Product, Image, Notification, ProductType, GiftCard, Message


def delete_image_path(request, obj):
    # in case of clear, remove the file as well
    if "image-clear" in request.POST and request.POST.get("image-clear") == "on":
        pr = Product.objects.get(id=obj.id)
        file_name = pr.image.name.split('.')[0]
        base = settings.BASE_DIR
        media_path = os.path.join(base, 'media')
        for filename in os.listdir(media_path):
            if file_name in filename:
                os.remove(os.path.join(media_path, filename))
    keys = request.POST.keys()
    key = [k for k in keys if "image-clear" in k and 'product_types' in k]
    if len(key):
        indices = [re.findall(r"\d", k)[0] for k in key]
        product_type_id = request.POST['product_types-' + indices[0] + '-id']
        pr = Product.objects.prefetch_related('product_types').filter(id=obj.id)[0]
        types = pr.product_types.all()
        for product_type in types:
            if product_type.id == int(product_type_id):
                file_name = product_type.image.name.split('.')[0]
                base = settings.BASE_DIR
                media_path = os.path.join(base, 'media')
                for filename in os.listdir(media_path):
                    if file_name in filename:
                        os.remove(os.path.join(media_path, filename))


class CollectionAdmin(admin.ModelAdmin):
    error_while_saving = False
    list_display = ['name']
    fields = ('name', 'image', 'available', 'custom', 'show_on_home_page', 'basic_collection',
              'regular_collection', 'studio_collection')

    def save_model(self, request, obj, form, change):
        if change:
            if 'available' in form.changed_data:
                products = Product.objects.filter(collection=obj)
                new_availability = False if not obj.available else True
                for product in products:
                    if product.available is not new_availability:
                        product.available = new_availability
                        product.save()
            delete_image_path(request, obj)
            super().save_model(request, obj, form, change)
        else:
            slug = slugify(obj.name)
            collection = Collection.objects.filter(slug=slug)
            if len(collection):
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
    list_display = ['name', 'collection', 'studs', 'price', 'stock', 'available', 'created', 'updated', 'delivery_size']
    list_filter = ['available', 'created', 'updated', 'collection', 'custom']
    list_editable = ['price', 'available', 'delivery_size']
    fields = ('collection', 'name', 'image', 'description', 'size', 'price', 'custom', 'studs', 'key_ring',
              'custom_date', 'initials', 'available', 'stock', 'price_api_id', 'delivery_size')

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '/static/admin/js/hide_attribute.js'
        )

    def save_model(self, request, obj, form, change):
        if change:
            delete_image_path(request, obj)
            super().save_model(request, obj, form, change)
        else:
            slug = slugify(obj.name)
            product = Product.objects.filter(slug=slug)
            if len(product):
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
    list_display = ['sender', 'name', 'subject', 'email', 'message', 'created', 'sent']


admin.site.register(Message, MessageAdmin)
