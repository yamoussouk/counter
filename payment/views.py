from datetime import datetime, timedelta

import stripe
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from cart.cart import Cart
from giftcardpayment.models import BoughtGiftCard
from order.models import Order
from shop.MessageSender import MessageSender
from shop.models import Notification, Product, GiftCard, Message


@csrf_exempt
def payment_done(request):
    cart = Cart(request)
    cart.clear()
    notification = Notification.objects.all()
    return render(request, 'payment/done.html', {'notification': notification})


@csrf_exempt
def payment_cancelled(request):
    notification = Notification.objects.all()
    return render(request, 'payment/cancelled.html', {'notification': notification})


def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payment/process.html', {'order': order})


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    order_id = request.session.get('order_id')
    cart = Cart(request)
    items = []
    order = Order.objects.prefetch_related('items').filter(id=order_id)
    discount = ''
    metadata = dict(order_id=order_id)
    # if any gift card is applied an add hoc payment is created
    # this sucks since 175ft is the minimum limit for a purchase
    if cart.gift_cards is not None:
        total_price = cart.calculated_total_price()
        items.append(dict(name='valami', amount=int(total_price) * 100, quantity=1, currency=settings.CURRENCY))
    else:
        discount = order[0].coupon if order[0].coupon is not None else ''
        for o in order:
            item = o.items.all().values()
            for i in item:
                if i.get('product_id') is not None:
                    product = Product.objects.filter(id=i.get('product_id'))[0]
                    items.append(dict(price=product.price_api_id, quantity=int(i.get('quantity'))))
                else:
                    gift_card = GiftCard.objects.filter(id=i.get('gift_card_id'))[0]
                    items.append(dict(price=gift_card.price_api_id, quantity=int(i.get('quantity'))))
        delivery_type = order[0].delivery_type
        if delivery_type == 'Házhozszállítás':
            items.append(dict(price='price_1Hmeu4EDD83OtAN44aAs4EUy', quantity=1))
        elif delivery_type == 'FoxPost':
            items.append(dict(price='price_1HmessEDD83OtAN4NAeiAbQ8', quantity=1))
        elif delivery_type == 'Csomagkuldo':
            items.append(dict(price='price_1HsDMmEDD83OtAN47Sr3RXUT', quantity=1))
        if cart.gift_card_ids:
            if len(cart.gift_card_ids) > 0:
                pass

    if request.method == 'GET':
        domain_url = settings.BASE_URL
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + reverse('payment:done') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + reverse('payment:cancelled'),
                payment_method_types=['card'],
                mode='payment',
                metadata=metadata,
                line_items=items,
                **({"discounts": [dict(coupon=discount)]} if discount != '' else {}),
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


class SuccessView(TemplateView):
    template_name = 'payment/success.html'


class CancelledView(TemplateView):
    template_name = 'payment/cancelled.html'


def __post_payment_process(event):
    # save the order
    order_id = event['data']['object']['metadata']['order_id']
    order = get_object_or_404(Order, id=order_id)
    order.paid = True
    order.paid_by = 'Stripe'
    order.subtotal = event['data']['object']['amount_subtotal'] / 100
    order.total = event['data']['object']['amount_total'] / 100
    order.discount_amount = order.total - order.subtotal
    order.paid_time = (datetime.utcfromtimestamp(event['created'])
                       + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    prices = dict(FoxPost=settings.FOXPOST_PRICE, Csomagkuldo=settings.CSOMAGKULDO_PRICE,
                  Házhozszállítás=settings.DELIVERY_PRICE, Személyesátvétel=0)
    order.delivery_cost = prices[order.delivery_type.replace(' ', '')]
    order.save()
    # decrease the stock number
    order_items = Order.objects.prefetch_related('items').filter(id=order_id)[0].items.all()
    for o in order_items:
        if o.product is not None:
            product = Product.objects.prefetch_related('product_types').filter(id=o.product.id)[0]
            if len(product.product_types.all()) > 0:
                product_type = [pt for pt in product.product_types.all() if pt.color == o.color]
                product_type[0].stock = product_type[0].stock - o.quantity
                product_type[0].save()
            else:
                product.stock = product.stock - o.quantity
            product.save()
        if o.gift_card is not None:
            gift_card = GiftCard.objects.get(id=o.gift_card.id)
            bought_card = BoughtGiftCard(price=gift_card.price, bought=datetime.now, email=order.email, active=True)
            bought_card.save()

    # SEND AN ORDER CONFIRMATION MAIL
    o = Order.objects.prefetch_related('items').filter(id=order_id)[0]
    prices = dict(FoxPost=settings.FOXPOST_PRICE, Csomagkuldo=settings.CSOMAGKULDO_PRICE,
                  Házhozszállítás=settings.DELIVERY_PRICE, Személyesátvétel=0)
    delivery_info = dict(FoxPost={'Átvételi pont': o.fox_post},
                         Csomagkuldo={'Átvételi pont': o.csomagkuldo},
                         Házhozszállítás={'Szállítási név': o.delivery_name, 'Szállítási cím': o.address,
                                          'Postakód': o.postal_code, 'Település': o.city, 'Megjegyzés': o.note},
                         Személyesátvétel={'Vezetéknév': o.first_name, 'Keresztnév': o.last_name})
    delivery_price = prices[o.delivery_type.replace(' ', '')]
    delivery_data = delivery_info[o.delivery_type.replace(' ', '')]
    order_total = o.subtotal + delivery_price
    result, msg = MessageSender(subject=f'Rendelés megerősítése #{str(o.id)}', to=o.email,
                                sender='www.minervastudio.hu').send_order_confirmation_email(
        {'name': o.full_name, 'order': o,
         'delivery_price': delivery_price,
         'delivery_info': delivery_data,
         'order_total': order_total})
    sent = True if result == 1 else False
    Message.objects.create(subject=f'Rendelés megerősítése #{str(o.id)}', email=o.email, message=msg,
                           sender='System message from Minerva Studio', sent=sent)


def finalize_gift_card_payment(request):
    if request.method == 'POST':
        cart = Cart(request)
        subtotal = cart.calculated_total_price(gift_card=False)
        order = get_object_or_404(Order, id=request.POST.get('order_id'))
        order.paid = True
        order.paid_by = 'Ajándékkártya'
        order.paid_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        order.subtotal = float(subtotal)
        order.total = float(0)
        order.save()
        for card in cart.gift_cards:
            card.active = False
            card.save()
        cart.clear()
    return redirect(reverse('shop:thank_you'))


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        __post_payment_process(event)

    return HttpResponse(status=200)
