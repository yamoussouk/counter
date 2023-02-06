import os
import re

from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from unidecode import unidecode

from .models import Collection, Product, Image, Notification, ProductType, GiftCard, Message, Tag

"""
    Since we are trying to get better seo rank we change how the images are named. The logic is the following:
    It takes the Product model's product_name property, concatenate it by hyphens in a lower case mode with their
    original extension. In case of the main image and the product types, saving the object creates the webp as well.
    We delete the original webps.
"""


def change_image(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    for obj in queryset:
        field = [f for f in fields if f.name == 'product_name'][0]
        value = getattr(obj, field.name)
        if value not in ['', ' ']:
            new_value = unidecode(value, "utf-8").lower().replace(' ', '-').replace("'", "")
            main_image = [f for f in fields if f.name == 'image'][0]
            file_name = getattr(obj, main_image.name).name.split('.')[0]
            if new_value != file_name:
                base = settings.BASE_DIR
                media_path = os.path.join(base, 'media')
                for filename in os.listdir(media_path):
                    if file_name in filename:
                        if 'webp' in filename:
                            os.remove(os.path.join(media_path, filename))
                        else:
                            new_name = f'{new_value}.png' if 'png' in filename.lower() else f'{new_value}.jpg'
                            os.rename(os.path.join(media_path, filename), os.path.join(media_path, new_name))
                            obj.image = new_name
                            obj.save()

                # save and rename extra images
                extra_images = obj.images.all()
                for idx, extra_image in enumerate(extra_images):
                    extra_image_name = extra_image.image.name
                    temp = extra_image_name.split('/')[1].split('.')
                    extra_image_name_ = temp[0]
                    ext_ = temp[1]
                    new_image_name = f'{new_value}{idx + 2}'
                    extra_image.image.name = f'images/{new_image_name}.{ext_}'
                    extra_image.save()
                    images_path = os.path.join(media_path, 'images')
                    for filename in os.listdir(images_path):
                        if extra_image_name_ in filename:
                            new_name = f'{new_image_name}.png' if 'png' in filename.lower() \
                                else (f'{new_image_name}.webp' if 'webp' in filename.lower()
                                      else f'{new_image_name}.jpg')
                            os.rename(os.path.join(images_path, filename), os.path.join(images_path, new_name))

                # save and rename product types
                product_types = obj.product_types.all()
                for product_type in product_types:
                    product_type_name = product_type.image.name
                    color = product_type.color
                    color_ = unidecode(color, "utf-8").lower().replace(' ', '-')
                    temp = product_type_name.split('.')
                    product_type_name_ = temp[0]
                    new_image_name = f'{color_}-{new_value}'
                    for filename in os.listdir(media_path):
                        if product_type_name_ in filename:
                            if 'webp' in filename:
                                os.remove(os.path.join(media_path, filename))
                            else:
                                new_name = f'{new_image_name}.png' if 'png' in filename.lower() else f'{new_image_name}.jpg'
                                try:
                                    os.rename(os.path.join(media_path, filename), os.path.join(media_path, new_name))
                                except FileExistsError:
                                    print(f'Tried to rename {filename} to {new_name} but it failed')
                                product_type.image.name = new_name
                                product_type.save()


change_image.short_description = 'Change image'


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
              'regular_collection', 'studio_collection', 'best_seller_collection', 'seo_title', 'seo_description',
              'seo_image_alt')

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
            return HttpResponseRedirect("/admin/shop/collection/add/", obj)
        else:
            return super(CollectionAdmin, self).response_add(request, obj, post_url_continue)


admin.site.register(Collection, CollectionAdmin)


class ProductImageAdmin(admin.StackedInline):
    model = Image
    extra = 0


class ProductTypeInline(admin.StackedInline):
    model = ProductType
    extra = 0


class ProductTagInline(admin.StackedInline):
    model = Tag
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    error_while_saving = False
    # save_as = True
    inlines = [ProductImageAdmin, ProductTypeInline, ProductTagInline]
    list_display = ['name', 'collection', 'studs', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'collection', 'custom']
    list_editable = ['price', 'available']
    fieldsets = (
        ("Kötelező mezők", {
            "fields": (
                'collection', 'name', 'product_name', 'description', 'size',
            )
        }),
        ("Ár", {
            "fields": (
                "price", "price_api_id",
            )
        }),
        ("Státusz", {
            "fields": (
                'available', 'stock',
            )
        }),
        ("Főkép", {
            "fields": (
                'image',
            )
        }),
        ("Szállítás", {
            "fields": (
                'delivery_size',
            )
        }),
        ("Karikák", {
            "fields": (
                'findings', 'findings_type', 'default_finding_type',
            )
        }),
        ("Beszúrók", {
            "fields": (
                'custom', 'studs', 'key_ring', 'custom_date', 'initials',
            )
        }),
        ("SEO", {
            "fields": (
                'seo_title', 'seo_description', 'seo_image_alt', 'og_description',
            )
        })
    )
    actions = [change_image]

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
            '/static/admin/js/hide_attribute.js'
        )

    def save_model(self, request, obj, form, change):
        try:
            if change:
                delete_image_path(request, obj)
                super().save_model(request, obj, form, change)
            else:
                # obj_id = obj.id
                # if obj_id is None:  # save as
                #     previous_product_id = request.resolver_match.kwargs["object_id"]
                #     pr = Product.objects.prefetch_related('product_types').get(id=int(previous_product_id))
                #     types_ = pr.product_types.all()
                #     if len(types_):
                #         _mutable = form.data._mutable
                #         form.data._mutable = True
                #         for idx, type_ in enumerate(types_):
                #             i = type_.image
                #             form.data.__setitem__(f'product_types-{idx}-image', i)
                #         form.data._mutable = _mutable
                #     if obj.image is None or obj.image.name == '':
                #         image_url = pr.image
                #         obj.image = image_url
                slug = slugify(obj.name)
                product = Product.objects.filter(slug=slug)
                if len(product):
                    self.error_while_saving = True
                    msg = f"Product with the given name \"{obj.name}\" already exists."
                    self.message_user(request, msg, messages.WARNING)
                else:
                    super().save_model(request, obj, form, change)
        except ValueError:
            return HttpResponseRedirect("/admin/shop/product/add/")

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
