import logging

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from coupon.forms import CouponApplyForm
from logs.models import LogFile
from parameters.models import Parameter
# from giftcardpayment.forms import GiftCardApplyForm
from shop.models import Product, GiftCard, ProductType, Notification
from .cart import Cart
from .forms import CartAddProductForm, CartAddCustomProductForm, CartAddGiftCardProductForm, CartDeliveryInfoForm

log = logging.getLogger(__name__)

CSOMAGKULDO_PRICE_API_KEY = 'csomagkuldo_price_api_key'
SZEMELYES_ATVETEL_ENABLED = 'szemelyes_atvetel_enabled'
FOXPOST_ENABLED = 'foxpost_enabled'
DELIVERY_ENABLED = 'delivery_enabled'
CSOMAGKULDO_ENABLED = 'csomagkuldo_enabled'
AJANLOTT_ENABLED = 'ajanlott_enabled'
DISCOUNT_SERVICE = 'discount_service'
FOXPOST_PRICE = 'foxpost_price'
DELIVERY_PRICE = 'delivery_price'
CSOMAGKULDO_PRICE = 'csomagkuldo_price'
AJANLOTT_PRICE = 'ajanlott_price'
AJANLOTT_CART_LIMIT = 'ajanlott_cart_limit'


def __validate_stock(cart, product, cd):
    color = cd['color']
    quantity = cd['quantity']
    if len(cart) > 0:
        try:
            p = ProductType.objects.get(product=product, color=color)
            stock = p.stock
            item_quantity_in_cart = 0
            for key, value in cart.items():
                if int(cart[key]['product_id']) == int(product.id) and cart[key]['color'] == color:
                    item_quantity_in_cart += int(cart[key]['quantity'])
            if item_quantity_in_cart + int(quantity) > stock:
                return False, item_quantity_in_cart, stock
            else:
                return True, item_quantity_in_cart, stock
        except ProductType.DoesNotExist:
            stock = product.stock
            item_quantity_in_cart = 0
            for key, value in cart.items():
                if int(cart[key]['product_id']) == int(product.id):
                    item_quantity_in_cart += int(cart[key]['quantity'])
            if item_quantity_in_cart + int(quantity) > stock:
                return False, item_quantity_in_cart, stock
            else:
                return True, item_quantity_in_cart, stock
        except ValueError:
            return True, 0, 0
    else:
        return True, 0, 0


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_http_methods(['POST'])
def cart_add(request, product_id):
    ip_address = get_client_ip(request)
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    redirect_url = 'shop:studio_product_detail' if product.collection.studio_collection \
        else ('shop:custom_product_detail' if product.custom else 'shop:product_detail')
    form = CartAddCustomProductForm(request.POST) if product.custom else CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        if cd.get('color') == '' and product.product_types.all().exists():
            messages.error(request, f'Kérem válasszon színt!')
            return redirect(reverse(redirect_url, args=[product.collection.slug, product.slug]))
        if product.custom:
            status, item_in_cart, stock = True, 0, 0
        else:
            status, item_in_cart, stock = __validate_stock(cart.cart, product, cd)
        if status:
            cart.add(product=product, quantity=cd['quantity'],
                     update_quantity=cd['update'], color=cd['color'], stud=cd['stud'],
                     first_initial=cd['first_initial'] if 'first_initial' in cd else '',
                     second_initial=cd['second_initial'] if 'second_initial' in cd else '',
                     custom_date=cd['custom_date'] if 'custom_date' in cd else '',
                     delivery_size=product.delivery_size)
            LogFile.objects.create(type='INFO',
                                   message=f'Product with the id of {product_id} has been '
                                           f'added to the cart, user: {ip_address}')
            return redirect(reverse(redirect_url, args=[product.collection.slug, product.slug]))
        else:
            LogFile.objects.create(
                type='INFO', message=f'Tried to add product with the id of {product_id} '
                                     f'to the cart but it was out of stock, user: {ip_address}')
            messages.error(request, f'A hozzáadni kívánt, illetve a kosaradban található termék összes mennyisége'
                                    f' meghaladja az elérhető mennyiséget, amely {stock}. A kosaradban az aktuális termék '
                                    f'mennyisége {item_in_cart}.')
            return redirect(reverse(redirect_url, args=[product.collection.slug, product.slug]))
    # messages.error(request, 'Hiba történt, kérlek, próbáld meg újra.')
    messages.error(request, 'Kérem, töltse ki az összes mezőt!')
    return redirect(reverse(redirect_url, args=[product.collection.slug, product.slug]))


@require_http_methods(['POST'])
def cart_add_gift_card(request, card_id):
    cart = Cart(request)
    gift_card = get_object_or_404(GiftCard, id=card_id)
    form = CartAddGiftCardProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=gift_card, color='', stud='', quantity=1, update_quantity=cd['update'])
    return redirect('cart:cart_detail')


def cart_remove(request, item_id):
    cart = Cart(request)
    log.info(f'Requesting to remove an item from the cart with the item id of "{item_id}".\nCart object: {cart}')
    product_id = cart.cart[str(item_id)]["product_id"]
    cart = cart.remove(item_id)
    LogFile.objects.create(type='INFO',
                           message=f'Item with the id of {product_id} was '
                                   f'removed from the cart, user: {get_client_ip(request)}')
    log.info(f'Cart object after item removal: {cart}')
    return redirect(reverse('cart:cart_detail'))


def set_delivery_form(delivery_form, request):
    delivery_form.fields["delivery_name"].initial = request.session["delivery"].get("delivery_name", "")
    delivery_form.fields["address"].initial = request.session["delivery"].get("address", "")
    delivery_form.fields["address_number"].initial = request.session["delivery"].get("address_number", "")
    delivery_form.fields["postal_code"].initial = request.session["delivery"].get("postal_code", "")
    delivery_form.fields["city"].initial = request.session["delivery"].get("city", "")
    delivery_form.fields["note"].initial = request.session["delivery"].get("note", "")


def set_personal_form(delivery_form, request):
    delivery_form.fields["first_name"].required = True
    delivery_form.fields["first_name"].initial = request.session["delivery"].get("first_name", "")
    delivery_form.fields["last_name"].required = True
    delivery_form.fields["last_name"].initial = request.session["delivery"].get("last_name", "")


def initiate_the_cart_delivery_form(request) -> 'CartDeliveryInfoForm':
    delivery_form = CartDeliveryInfoForm()
    if request.session.get('delivery', None) is not None:
        delivery_code = request.session["delivery"].get("delivery_code")
        if delivery_code is not None:
            delivery_form.fields["delivery_type_code"].initial = str(delivery_code)
            if delivery_code == "0":  # szemelyes atvetel
                set_personal_form(delivery_form, request)
            elif delivery_code in ["2", "4"]:  # hazhozszallitas, ajanlott
                set_delivery_form(delivery_form, request)
            elif delivery_code == "1":  # csomagkuldo
                delivery_form.fields["csomagkuldo"].required = True
                delivery_form.fields["csomagkuldo"].initial = request.session["delivery"].get("csomagkuldo", "")
            elif delivery_code == "3":  # foxpost
                delivery_form.fields["fox_post"].required = True
                delivery_form.fields["fox_post"].initial = request.session["delivery"].get("fox_post", "")
    return delivery_form


def is_parameter_enabled(parameters, name: str) -> bool:
    filter_ = [param for param in parameters if param.name == name]
    if len(filter_):
        return filter_[0].value == 'True'
    else:
        LogFile.objects.create(type='WARNING',
                               message=f'There is no such parameter: {name} in the Parameters; '
                                       f'must have returned False')
        return False


def get_parameter_value(parameters, name: str):
    filter_ = [param for param in parameters if param.name == name]
    if len(filter_):
        return filter_[0].value
    else:
        LogFile.objects.create(type='WARNING',
                               message=f'There is no such parameter: {name} in the Parameters; '
                                       f'must have returned empty string')
        return ''


def cart_detail(request):
    cart = Cart(request)
    is_product_in_cart = False
    for key, value in cart.cart.items():
        cart.cart[key]['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': cart.cart[key]['quantity'], 'update': True})
        if cart.cart[key]['type'] in ['product', 'product_type']:
            is_product_in_cart = True
    coupon_apply_form = CouponApplyForm()
    # gift_card_apply_form = GiftCardApplyForm()
    delivery_form = initiate_the_cart_delivery_form(request)
    current_amount = request.session.get('current_amount', 0)
    notification = Notification.objects.all()
    parameters = Parameter.objects.filter(Q(name=CSOMAGKULDO_PRICE_API_KEY) |
                                          Q(name=SZEMELYES_ATVETEL_ENABLED) |
                                          Q(name=FOXPOST_ENABLED) |
                                          Q(name=DELIVERY_ENABLED) |
                                          Q(name=CSOMAGKULDO_ENABLED) |
                                          Q(name=AJANLOTT_ENABLED) |
                                          Q(name=AJANLOTT_CART_LIMIT) |
                                          Q(name=DISCOUNT_SERVICE) |
                                          Q(name=FOXPOST_PRICE) |
                                          Q(name=DELIVERY_PRICE) |
                                          Q(name=CSOMAGKULDO_PRICE) |
                                          Q(name=AJANLOTT_PRICE))
    api_key = [param for param in parameters if param.name == CSOMAGKULDO_PRICE_API_KEY][0].value
    is_szemelyes_atvetel_enabled = is_parameter_enabled(parameters, SZEMELYES_ATVETEL_ENABLED)
    is_foxpost_enabled = is_parameter_enabled(parameters, FOXPOST_ENABLED)
    is_delivery_enabled = is_parameter_enabled(parameters, DELIVERY_ENABLED)
    is_csomagkuldo_enabled = is_parameter_enabled(parameters, CSOMAGKULDO_ENABLED)
    is_ajanlott_enabled = is_parameter_enabled(parameters, AJANLOTT_ENABLED)
    ajanlott_cart_limit = int([param for param in parameters if param.name == AJANLOTT_CART_LIMIT][0].value)
    is_delivery_size_ok = sum(int(value['delivery_size']) for key, value in cart.cart.items()) <= 10
    is_discount_enabled = is_parameter_enabled(parameters, DISCOUNT_SERVICE)  # 3/2
    context = dict(cart=cart, coupon_apply_form=coupon_apply_form, delivery_form=delivery_form,
                   fox_price=get_parameter_value(parameters, FOXPOST_PRICE),
                   delivery_price=get_parameter_value(parameters, DELIVERY_PRICE),
                   csomagkuldo_price=get_parameter_value(parameters, CSOMAGKULDO_PRICE),
                   ajanlott_price=get_parameter_value(parameters, AJANLOTT_PRICE),
                   is_product_in_cart=is_product_in_cart,
                   current_amount=current_amount, session=request.session, notification=notification, api_key=api_key,
                   is_szemelyes_atvetel_enabled=is_szemelyes_atvetel_enabled,
                   is_foxpost_enabled=is_foxpost_enabled, is_delivery_enabled=is_delivery_enabled,
                   is_csomagkuldo_enabled=is_csomagkuldo_enabled, is_ajanlott_enabled=is_ajanlott_enabled,
                   ajanlott_cart_limit=ajanlott_cart_limit,
                   is_discount_enabled=is_discount_enabled,
                   is_delivery_size_ok=is_delivery_size_ok)  # 'gift_card_apply_form': gift_card_apply_form
    log.info(f'Cart details: {context.get("cart")}')
    return render(request, 'cart/detail.html', context)
