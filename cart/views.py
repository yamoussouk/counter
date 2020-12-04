from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from coupon.forms import CouponApplyForm
# from giftcardpayment.forms import GiftCardApplyForm
from shop.models import Product, GiftCard, ProductType, Notification
from .cart import Cart
from .forms import CartAddProductForm, CartAddGiftCardProductForm, CartDeliveryInfoForm
from shop.MessageSender import MessageSender
from django.template import Context


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


@require_http_methods(['POST'])
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        status, item_in_cart, stock = __validate_stock(cart.cart, product, cd)
        if status:
            cart.add(product=product, quantity=cd['quantity'],
                     update_quantity=cd['update'], color=cd['color'], stud=cd['stud'])
            return redirect(reverse('shop:product_detail', args=[product_id, product.slug]))
        else:
            messages.error(request, f'A hozzáadni kívánt, illetve a kosaradban található termék összes mennyisége'
                                    f' meghaladja az elérhető mennyiséget, amely {stock}. A kosaradban az aktuális termék '
                                    f'mennyisége {item_in_cart}.')
            return redirect(reverse('shop:product_detail', args=[product_id, product.slug]))
    messages.error(request, 'Hiba történt, kérlek, próbáld meg újra.')
    return redirect('shop:product_detail')


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
    cart = cart.remove(item_id)
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
    api_key = settings.CSOMAGKULDO_API_KEY
    return render(request, 'cart/detail.html', {'cart': cart,
                                                'coupon_apply_form': coupon_apply_form,
                                                'delivery_form': delivery_form,
                                                'fox_price': settings.FOXPOST_PRICE,
                                                'delivery_price': settings.DELIVERY_PRICE,
                                                'is_product_in_cart': is_product_in_cart,
                                                # 'gift_card_apply_form': gift_card_apply_form,
                                                'current_amount': current_amount,
                                                'session': request.session,
                                                'notification': notification,
                                                'api_key': api_key,
                                                'csomagkuldo_price': settings.CSOMAGKULDO_PRICE})
