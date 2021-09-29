from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>', views.cart_add, name='cart_add'),
    path('add/gift/<int:card_id>', views.cart_add_gift_card, name='cart_add_gift_card'),
    path('remove/<int:item_id>', views.cart_remove, name='cart_remove'),
    path('cart_remove_giftcard/<int:id>', views.cart_remove_giftcard, name='cart_remove_giftcard'),
]
