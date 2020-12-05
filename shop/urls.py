from django.urls import path
from django.contrib.sitemaps.views import sitemap

from . import views
from .sitemaps import StaticViewsSitemap, CollectionSitemap, ProductSitemap
from django.views.generic import TemplateView

sitemaps = {
    'static': StaticViewsSitemap,
    'product': ProductSitemap,
    'collection': CollectionSitemap
}

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('termekek/', views.ProductsView.as_view(), name='products_view'),
    path('termekek/<str:slug>', views.ProductsView.as_view(), name='products_view'),
    path('termek/<str:id>/<str:slug>', views.product_detail, name='product_detail'),
    path('gyik', views.faq, name='faq'),
    path('kapcsolat/', views.contact, name='contact'),
    path('aszf/', views.aszf, name='aszf'),
    path('adatvedelem/', views.data_handling, name='data_handling'),
    path('uzenet/', views.contact_message, name='contact_message'),
    path('sikeres-uzenet-kuldes/', views.thank_you, name='thank_you'),
    path('cookie-consent/', views.cookie_consent, name='cookie_consent'),
    path('impresszum/', views.impresszum, name='impresszum'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="shop/robots.txt", content_type='text/plain')),
]
