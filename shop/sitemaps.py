from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from shop.models import Collection, Product


class StaticViewsSitemap(Sitemap):
    def items(self):
        return ['index', 'products_view', 'faq', 'contact', 'data_handling', 'aszf', 'impresszum', 'blog-bejegyzesek']

    def location(self, obj):
        if 'blog' in obj:
            return reverse('blog:' + obj)
        return reverse('shop:' + obj)


class CollectionSitemap(Sitemap):
    def items(self):
        return Collection.objects.filter(available=True).exclude(name='Studio')

    def lastmod(self, obj):
        return obj.updated


class ProductSitemap(Sitemap):
    def items(self):
        return Product.objects.filter(available=True, collection__studio_collection=False)

    def location(self, obj):
        return reverse('shop:product_detail', args=[obj.collection.slug, obj.slug])

    def lastmod(self, obj):
        return obj.updated
