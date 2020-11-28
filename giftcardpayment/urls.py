from django.urls import path

from . import views

app_name = 'giftcardpayment'

urlpatterns = [
    path('apply/', views.giftcard_apply, name='giftcard_apply'),
]