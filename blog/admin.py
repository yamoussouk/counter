from django.contrib import admin
from django.contrib import messages
from django.utils.text import slugify

from .models import Post, BlogCategory, PostImage


class BlogCategoryAdmin(admin.ModelAdmin):
    error_while_saving = False
    list_display = ['title']
    fields = ('title',)

    def save_model(self, request, obj, form, change):
        slug = slugify(obj.title)
        category = BlogCategory.objects.filter(slug=slug)
        if len(category):
            self.error_while_saving = True
            msg = f"Collection with the given name \"{obj.title}\" already exists."
            self.message_user(request, msg, messages.WARNING)
        else:
            super().save_model(request, obj, form, change)


admin.site.register(BlogCategory, BlogCategoryAdmin)


class PostImageAdmin(admin.StackedInline):
    model = PostImage
    extra = 0


class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageAdmin]
    error_while_saving = False
    list_display = ['title']
    fields = ('title', 'category', 'cover_image', 'cover_image_alt', 'cover_image_title', 'banner_image',
              'banner_image_alt', 'banner_image_title', 'short_description', 'content', 'status', 'time_to_read',
              'template', 'hashtags',)


admin.site.register(Post, PostAdmin)
