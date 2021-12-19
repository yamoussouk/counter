import logging

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from coupon.forms import CouponApplyForm
from parameters.models import Parameter
# from giftcardpayment.forms import GiftCardApplyForm
from shop.models import Product, GiftCard, ProductType, Notification
from logs.models import LogFile
from .cart import Cart
from .forms import CartAddProductForm, CartAddCustomProductForm, CartAddGiftCardProductForm, CartDeliveryInfoForm

log = logging.getLogger(__name__)


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
    delivery_form = CartDeliveryInfoForm()
    current_amount = request.session['current_amount'] if 'current_amount' in request.session else 0
    notification = Notification.objects.all()
    api_key = Parameter.objects.filter(name="csomagkuldo_price_api_key")[0].value
    is_szemelyes_atvetel_enabled = Parameter.objects.filter(name="szemelyes_atvetel_enabled")[0].value == 'True'
    is_foxpost_enabled = Parameter.objects.filter(name="foxpost_enabled")[0].value == 'True'
    is_delivery_enabled = Parameter.objects.filter(name="delivery_enabled")[0].value == 'True'
    is_csomagkuldo_enabled = Parameter.objects.filter(name="csomagkuldo_enabled")[0].value == 'True'
    is_ajanlott_enabled = Parameter.objects.filter(name="ajanlott_enabled")[0].value == 'True'
    ajanlott_cart_limit = int(Parameter.objects.filter(name="ajanlott_cart_limit")[0].value)
    is_delivery_size_ok = sum(int(value['delivery_size']) for key, value in cart.cart.items()) <= 10
    context = dict(cart=cart, coupon_apply_form=coupon_apply_form, delivery_form=delivery_form,
                   fox_price=Parameter.objects.filter(name="foxpost_price")[0].value,
                   delivery_price=Parameter.objects.filter(name="delivery_price")[0].value,
                   csomagkuldo_price=Parameter.objects.filter(name="csomagkuldo_price")[0].value,
                   ajanlott_price=Parameter.objects.filter(name="ajanlott_price")[0].value,
                   is_product_in_cart=is_product_in_cart,
                   current_amount=current_amount, session=request.session, notification=notification, api_key=api_key,
                   is_szemelyes_atvetel_enabled=is_szemelyes_atvetel_enabled,
                   is_foxpost_enabled=is_foxpost_enabled, is_delivery_enabled=is_delivery_enabled,
                   is_csomagkuldo_enabled=is_csomagkuldo_enabled, is_ajanlott_enabled=is_ajanlott_enabled,
                   ajanlott_cart_limit=ajanlott_cart_limit,
                   is_delivery_size_ok=is_delivery_size_ok)  # 'gift_card_apply_form': gift_card_apply_form
    log.info(f'Cart details: {context.get("cart")}')
    return render(request, 'cart/detail.html', context)
