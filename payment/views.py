import json
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
from logs.models import LogFile
from order.models import Order
from parameters.models import Parameter
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
    cart = Cart(request)
    all_product_types = [value['type'] for key, value in cart.cart.items()]
    delivery = cart.delivery_type is not None
    gift_card = cart.gift_card_ids is not None
    calculated_total_price = cart.calculated_total_price(delivery=delivery, gift_card=gift_card, cart=False)
    return render(request, 'payment/process.html', {'order': order, 'calculated_total_price': calculated_total_price,
                                                    'delivery': delivery})


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
    if hasattr(cart, 'gift_cards') and cart.gift_cards is not None:
        delivery = cart.delivery_type is not None
        total_price = cart.calculated_total_price(cart=False, delivery=delivery)
        items.append(dict(name='Kézműves termék', amount=int(total_price) * 100, quantity=1,
                          currency=Parameter.objects.filter(name="currency")[0].value))
    else:
        discount = order[0].coupon if order[0].coupon is not None else ''
        for k, v in cart.cart.items():
            if v.get('product_id') is not None and v.get('type') != 'gift_card':
                product = Product.objects.filter(id=v.get('product_id'))[0]
                if Parameter.objects.filter(name="discount_service")[0].value == 'True':
                    if v['zero_discount']:
                        if int(v['discount_show_price']) != 0:
                            q = v['discount_quantity']
                            if q > 0:
                                items.append(dict(price=product.price_api_id, quantity=int(q)))
                    else:
                        items.append(dict(price=product.price_api_id, quantity=int(v.get('quantity'))))
                else:
                    items.append(dict(price=product.price_api_id, quantity=int(v.get('quantity'))))
            else:
                gift_card = GiftCard.objects.filter(id=v.get('product').get('id'))[0]
                items.append(dict(name='Kézműves termék', amount=int(gift_card.price) * 100, quantity=1,
                                  currency=Parameter.objects.filter(name="currency")[0].value))
        delivery_type = order[0].delivery_type
        if delivery_type == 'Házhozszállítás':
            items.append(dict(price=Parameter.objects.filter(name="delivery_price_api_key")[0].value, quantity=1))
        elif delivery_type == 'FoxPost':
            items.append(dict(price=Parameter.objects.filter(name="foxpost_price_api_key")[0].value, quantity=1))
        elif delivery_type == 'Csomagkuldo':
            items.append(dict(price=Parameter.objects.filter(name="csomagkuldo_price_api_key")[0].value, quantity=1))
        elif delivery_type == 'Ajanlott':
            items.append(dict(price=Parameter.objects.filter(name="ajanlott_price_api_key")[0].value, quantity=1))
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
    order.paid_time = (datetime.utcfromtimestamp(event['created'])
                       + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    prices = dict(FoxPost=int(Parameter.objects.filter(name="foxpost_price")[0].value),
                  Csomagkuldo=int(Parameter.objects.filter(name="csomagkuldo_price")[0].value),
                  Házhozszállítás=int(Parameter.objects.filter(name="delivery_price")[0].value),
                  Személyesátvétel=0,
                  Ajanlott=int(Parameter.objects.filter(name="ajanlott_price")[0].value))
    order.delivery_cost = prices[order.delivery_type.replace(' ', '')] if order.delivery_type != '' else 0
    order.save()
    if order.used_gift_cards is not None:
        ids = order.used_gift_cards.split(',')
        for i in ids:
            card = BoughtGiftCard.objects.get(id=int(i))
            card.active = False
            card.save()
    # decrease the stock number
    order_items = Order.objects.prefetch_related('items').filter(id=order_id)[0].items.all()
    for o in order_items:
        if o.product is not None and not o.product.custom:
            product = Product.objects.prefetch_related('product_types').filter(id=o.product.id)[0]
            if len(product.product_types.all()) > 0:
                product_type = [pt for pt in product.product_types.all() if pt.color == o.color]
                log = LogFile(type='INFO', message=f'Stock of product with the ID of "{product.id}" '
                                                   f'and the name of "{product.name}" '
                                                   f'and the color of "{product_type[0].color}" was decreased'
                                                   f' with {o.quantity}. Previous stock was "{product_type[0].stock}",'
                                                   f' current stock is ')
                product_type[0].stock = product_type[0].stock - o.quantity
                product_type[0].save()
                log.message += f'"{product_type[0].stock}". Order ID: {order.id}'
                log.save()
            else:
                log = LogFile(type='INFO', message=f'Stock of product with the ID of "{product.id}"'
                                                   f' and the name of "{product.name}" was decreased'
                                                   f' with {o.quantity}. Previous stock was "{product.stock}",'
                                                   f' current stock is ')
                product.stock = product.stock - o.quantity
            product.save()
            if len(product.product_types.all()) == 0:
                log.message += f'"{product.stock}". Order ID: {order.id}'
                log.save()
        if o.gift_card is not None:
            gift_card = GiftCard.objects.get(id=o.gift_card.id)
            bought_card = BoughtGiftCard(price=gift_card.price, bought=datetime.now, email=order.email, active=True)
            bought_card.save()

    # SEND AN ORDER CONFIRMATION MAIL
    o = Order.objects.prefetch_related('items').filter(id=order_id)[0]
    delivery_info = dict(FoxPost={'Átvételi pont': o.fox_post},
                         Csomagkuldo={'Átvételi pont': o.csomagkuldo},
                         Házhozszállítás={'Szállítási név': o.delivery_name, 'Szállítási cím': o.address,
                                          'Postakód': o.postal_code, 'Település': o.city, 'Megjegyzés': o.note},
                         Ajanlott={'Szállítási név': o.delivery_name, 'Szállítási cím': o.address,
                                          'Postakód': o.postal_code, 'Település': o.city, 'Megjegyzés': o.note},
                         Személyesátvétel={'Vezetéknév': o.first_name, 'Keresztnév': o.last_name})
    delivery_data = delivery_info[o.delivery_type.replace(' ', '')]
    order_total = o.total
    result, msg = MessageSender(subject=f'Rendelés megerősítése #{str(o.id)}', to=o.email,
                                sender='www.minervastudio.hu').send_order_confirmation_email(
        {'name': o.full_name, 'order': o,
         'delivery_price': order.delivery_cost,
         'delivery_info': delivery_data,
         'order_total': order_total})
    sent = True if result == 1 else False
    Message.objects.create(subject=f'Rendelés megerősítése #{str(o.id)}', email=o.email, message=msg,
                           sender='System message from Minerva Studio', sent=sent)
    # SEND EMAIL ABOUT THE ORDER
    product = ', '.join([i.product.name for i in order_items])
    msg = f'Új rendelés:\nA rendelés száma: #{str(o.id)}\nA rendelés összege: {str(order_total)} Ft\nTermékek: {product}'
    result = MessageSender(subject=f'Új rendelés #{str(o.id)}', to=settings.EMAIL_HOST_USER,
                           sender='www.minervastudio.hu',
                           message=msg).send_mail()
    sent = True if result == 1 else False
    LogFile.objects.create(type='INFO', message=f'Message is sent to "{o.email}", status: "{result}"')
    Message.objects.create(subject=f'Új rendelés #{str(o.id)}', email=settings.EMAIL_HOST_USER, message=msg,
                           sender='System message from Minerva Studio', sent=sent)


def finalize_gift_card_payment(request):
    if request.method == 'POST':
        cart = Cart(request)
        subtotal = cart.calculated_total_price(gift_card=False, cart=False)
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
    else:
        LogFile(type='INFO', message=f'Checkout failure, {json.dumps(payload)}')

    return HttpResponse(status=200)
