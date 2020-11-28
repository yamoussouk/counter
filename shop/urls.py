from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('termekek/', views.ProductsView.as_view(), name='products_view'),
    path('termekek/<str:collection_name>', views.ProductsView.as_view(), name='products_view'),
    path('termek/<int:id>', views.product_detail, name='product_detail'),
    path('gyik', views.faq, name='faq'),
    path('kapcsolat/', views.contact, name='contact'),
    path('aszf/', views.aszf, name='aszf'),
    path('adatvedelem/', views.data_handling, name='data_handling'),
    path('uzenet/', views.contact_message, name='contact_message'),
    path('sikeres-uzenet-kuldes/', views.thank_you, name='thank_you'),
    path('cookie-consent/', views.cookie_consent, name='cookie_consent'),
    path('impresszum/', views.impresszum, name='impresszum')
]
