from django.contrib.sitemaps import Sitemap

from blog.models import BlogCategory, Post


class BlogCategorySitemap(Sitemap):
    def items(self):
        return BlogCategory.objects.all()

    def lastmod(self, obj):
        return obj.updated_on


class PostSitemap(Sitemap):
    def items(self):
        return Post.objects.filter(status=1)

    def lastmod(self, obj):
        return obj.updated_on
