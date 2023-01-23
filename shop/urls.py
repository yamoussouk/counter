from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import TemplateView

from blog.sitemaps import BlogCategorySitemap, PostSitemap
from parameters.models import Parameter
from . import views
from .sitemaps import StaticViewsSitemap, CollectionSitemap, ProductSitemap

sitemaps = {
    'static': StaticViewsSitemap,
    'product': ProductSitemap,
    'collection': CollectionSitemap,
    'blog-category': BlogCategorySitemap,
    'post': PostSitemap
}

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('termekek/', views.ProductsView.as_view(), name='products_view'),
    path('slowstudio/', views.StudioProductsView.as_view(), name='studio_products_view'),
    path('termekek/<str:slug>', views.ProductsView.as_view(), name='products_view'),
    path('termek/<str:id>/<str:slug>', views.product_detail, name='product_detail'),
    path('slowstudiotermek/<str:id>/<str:slug>', views.studio_product_detail, name='studio_product_detail'),
    path('gyik', views.faq, name='faq'),
    path('kapcsolat/', views.contact, name='contact'),
    path('aszf/', views.aszf, name='aszf'),
    path('adatvedelem/', views.data_handling, name='data_handling'),
    path('uzenet/', views.contact_message, name='contact_message'),
    path('sikeres-uzenet-kuldes/', views.thank_you, name='thank_you'),
    path('impresszum/', views.impresszum, name='impresszum'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="shop/robots.txt", content_type='text/plain')),
    path('icon/', views.get_icon, name='get_icon'),
    path('generate_stripe_product/<str:id>', views.generate_stripe_product, name='generate_stripe_product'),
    path('termekek/kereses/', views.SearchProductsView.as_view(), name='products_view_search'),
]

if Parameter.objects.filter(name="custom_service")[0].value == 'True':
    urlpatterns.extend([
        path('egyedi-rendelés/', views.CustomProductsView.as_view(), name='custom_products_view'),
        path('egyedi-rendelés/<str:slug>', views.CustomProductsView.as_view(), name='custom_products_view'),
        path('egyedi-termek/<str:id>/<str:slug>', views.custom_product_detail, name='custom_product_detail')
    ])
