import json
from datetime import datetime, timedelta
from smtplib import SMTPAuthenticationError

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


def __create_log_file(message: str, type_: str = 'INFO'):
    log = LogFile(type=type_, message=message)
    log.save()


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
    if hasattr(cart, 'gift_cards') and cart.gift_cards is not None:
        total_price = cart.calculated_total_price()
        items.append(dict(name='Ajándékkártya', amount=int(total_price) * 100, quantity=1,
                          currency=Parameter.objects.filter(name="currency")[0].value))
    else:
        discount = order[0].coupon if order[0].coupon is not None else ''
        for k, v in cart.cart.items():
            if v.get('product_id') is not None:
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
                gift_card = GiftCard.objects.filter(id=v.get('gift_card_id'))[0]
                items.append(dict(price=gift_card.price_api_id, quantity=int(v.get('quantity'))))
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


def __save_order(event, order, prices):
    order.paid = True
    order.paid_by = 'Stripe'
    order.paid_time = (datetime.utcfromtimestamp(event['created'])
                       + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    order.delivery_cost = prices[order.delivery_type.replace(' ', '')]
    order.save()


def __save_order_items(order):
    for o in order.items.all():
        if o.product is not None and not o.product.custom:
            product = Product.objects.prefetch_related('product_types').filter(id=o.product.id)[0]
            if len(product.product_types.all()) > 0:
                product_type = [pt for pt in product.product_types.all() if pt.color == o.color]
                msg = f'Stock of product with the ID of "{product.id}" and the name of "{product.name}" and the' \
                      f' color of "{product_type[0].color}" was decreased with {o.quantity}. ' \
                      f'Previous stock was "{product_type[0].stock}", '
                product_type[0].stock = product_type[0].stock - o.quantity
                product_type[0].save()
                msg += f'current stock is "{product_type[0].stock}". Order ID: {order.id}'
                __create_log_file(msg)
            else:
                msg = f'Stock of product with the ID of "{product.id}" and the name of "{product.name}" was ' \
                      f'decreased with {o.quantity}. Previous stock was "{product.stock}", current stock is '
                product.stock = product.stock - o.quantity
                msg += f'"{product.stock}". Order ID: {order.id}'
                __create_log_file(msg)
            product.save()
        if o.gift_card is not None:
            gift_card = GiftCard.objects.get(id=o.gift_card.id)
            bought_card = BoughtGiftCard(price=gift_card.price, bought=datetime.now, email=order.email, active=True)
            bought_card.save()


def __send_order_confirmation_email(o, prices):
    order_data = {'Szállítási név': o.delivery_name, 'Szállítási cím': o.address,
                  'Házszám, emelet, ajtó': o.address_number,
                  'Postakód': o.postal_code, 'Település': o.city, 'Megjegyzés': o.note}
    delivery_info = dict(FoxPost={'Átvételi pont': o.fox_post},
                         Csomagkuldo={'Átvételi pont': o.csomagkuldo},
                         Házhozszállítás=order_data,
                         Ajanlott=order_data,
                         Személyesátvétel={'Vezetéknév': o.first_name, 'Keresztnév': o.last_name})
    delivery_price = prices[o.delivery_type.replace(' ', '')]
    delivery_data = delivery_info[o.delivery_type.replace(' ', '')]
    order_total = o.total
    data = {'name': o.full_name, 'order': o,
            'delivery_price': delivery_price,
            'delivery_info': delivery_data,
            'order_total': order_total}
    subject = f'Rendelés megerősítése #{str(o.id)}'
    sender = 'www.minervastudio.hu'
    try:
        result, msg = MessageSender(subject=subject, to=o.email, sender=sender).send_order_confirmation_email(data)
        sent = True if result == 1 else False
    except SMTPAuthenticationError:
        msg = f'Could not send order confirmation message to the following order id: "{str(o.id)}"'
        __create_log_file(type_='ERROR', message=msg)
        sent = 0
    Message.objects.create(subject=f'Rendelés megerősítése #{str(o.id)}', email=o.email, message=msg,
                           sender='System message from Minerva Studio', sent=sent)


def __send_email_about_the_order(o):
    product = ', '.join([i.product.name for i in o.items.all()])
    msg = f'Új rendelés:\nA rendelés száma: #{str(o.id)}\nA rendelés összege: {str(o.total)} Ft\nTermékek: {product}'
    subject = f'Új rendelés #{str(o.id)}'
    sender = 'www.minervastudio.hu'
    try:
        result = MessageSender(subject=subject, to=settings.EMAIL_HOST_USER, sender=sender, message=msg).send_mail()
        sent = True if result == 1 else False
    except SMTPAuthenticationError:
        msg = f'Could not send email about the order to the following order id: "{str(o.id)}"'
        __create_log_file(type_='ERROR', message=msg)
        sent = 0
    __create_log_file(f'Message is sent to "{o.email}", status: "{sent}"')
    Message.objects.create(subject=f'Új rendelés #{str(o.id)}', email=settings.EMAIL_HOST_USER, message=msg,
                           sender='System message from Minerva Studio', sent=sent)


def __post_payment_process(event):
    prices = dict(FoxPost=int(Parameter.objects.filter(name="foxpost_price")[0].value),
                  Csomagkuldo=int(Parameter.objects.filter(name="csomagkuldo_price")[0].value),
                  Házhozszállítás=int(Parameter.objects.filter(name="delivery_price")[0].value),
                  Személyesátvétel=0,
                  Ajanlott=int(Parameter.objects.filter(name="ajanlott_price")[0].value))
    order_id = event['data']['object']['metadata']['order_id']
    order_with_items = Order.objects.prefetch_related('items').filter(id=order_id)[0]
    if order_with_items.paid_time == '':
        # save the order
        __save_order(event, order_with_items, prices)
        # decrease the stock number
        __save_order_items(order_with_items)
    # SEND AN ORDER CONFIRMATION MAIL
    __send_order_confirmation_email(order_with_items, prices)
    # SEND EMAIL ABOUT THE ORDER
    __send_email_about_the_order(order_with_items)


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
    else:
        LogFile(type='INFO', message=f'Checkout failure, {json.dumps(payload)}')

    return HttpResponse(status=200)
