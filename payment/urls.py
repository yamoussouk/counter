from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('done/', views.payment_done, name='done'),
    # path('cancelled/', views.payment_cancelled, name='cancelled'),
    path('process/config/', views.stripe_config),
    path('process/create-checkout-session/', views.create_checkout_session),
    path('success/', views.SuccessView.as_view()),
    path('cancelled/', views.CancelledView.as_view(), name='cancelled'),
    path('webhook/', views.stripe_webhook),
    path('finalize_gift_card_payment/', views.finalize_gift_card_payment, name='finalize_gift_card_payment'),
]
