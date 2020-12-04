from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from cart.cart import Cart
from shop.models import ProductType
from .forms import OrderCreateForm
from .models import Order, OrderItem


def __validate_stock(cart, product, cd):
    color = cd['color']
    if len(cart) > 0:
        try:
            p = ProductType.objects.get(product=product, color=color)
            stock = p.stock
            item_quantity_in_cart = 0
            for key, value in cart.items():
                if int(cart[key]['product_id']) == int(product.id) and cart[key]['color'] == color:
                    item_quantity_in_cart += int(cart[key]['quantity'])
            if item_quantity_in_cart > stock:
                return False, item_quantity_in_cart, stock
            else:
                return True, item_quantity_in_cart, stock
        except ProductType.DoesNotExist:
            stock = product.stock
            item_quantity_in_cart = 0
            for key, value in cart.items():
                if int(cart[key]['product_id']) == int(product.id):
                    item_quantity_in_cart += int(cart[key]['quantity'])
            if item_quantity_in_cart > stock:
                return False, item_quantity_in_cart, stock
            else:
                return True, item_quantity_in_cart, stock
        except ValueError:
            return True, 0, 0
    else:
        return True, 0, 0


def order_create(request):
    cart = Cart(request)
    out_of_stock = False
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            for item in cart:
                status, item_in_cart, stock = __validate_stock(cart.cart, item['product'], item)
                if not status:
                    out_of_stock = True
                    messages.error(request,
                                   f'A megvásárolni kívánt, illetve a kosaradban található termék összes mennyisége'
                                   f' meghaladja az elérhető mennyiséget, amely {stock}. A kosaradban az aktuális termék '
                                   f'mennyisége {item_in_cart}.')
            if not out_of_stock:
                request.session['delivery'] = dict(delivery_type=cd['delivery_type'], address=cd['address'],
                                                   postal_code=cd['postal_code'], city=cd['city'], note=cd['note'],
                                                   fox_post=cd['fox_post'], delivery_name=cd['delivery_name'],
                                                   first_name=cd['first_name'], last_name=cd['last_name'],
                                                   csomagkuldo=cd['csomagkuldo'])
                request.session['mandatory'] = dict(full_name=cd['full_name'], email=cd['email'], phone=cd['phone'])
                request.session['billing'] = dict(billing_address=cd['billing_address'],
                                                  billing_postal_code=cd['billing_postal_code'],
                                                  billing_city=cd['billing_city'])
                if cart.order:
                    order = cart.order
                    order.full_name = request.POST.get('full_name')
                    order.phone = request.POST.get('phone_number')
                    order.email = request.POST.get('email_address')
                    order.billing_address = request.POST.get('billing_address')
                    order.billing_postal_code = request.POST.get('billing_postal_code')
                    order.billing_city = request.POST.get('billing_city')
                    order.first_name = request.POST.get('first_name')
                    order.last_name = request.POST.get('last_name')
                    order.delivery_name = request.POST.get('delivery_full_name')
                    order.address = request.POST.get('d_address')
                    order.postal_code = request.POST.get('d_zip')
                    order.city = request.POST.get('d_city')
                    order.note = request.POST.get('note')
                    order.delivery_type = request.POST.get('delivery_type')
                    order.fox_post = request.POST.get('fox_post')
                    order.csomagkuldo = request.POST.get('csomagkuldo')
                else:
                    order = form.save(commit=False)
                order.subtotal = cart.get_total_price()
                order.total = cart.get_total_price()
                if cart.coupon:
                    order.coupon = cart.coupon
                    order.discount = cart.coupon.discount
                    order.discount_amount = cart.get_total_price() - cart.get_total_price_after_discount()
                    order.subtotal = cart.get_total_price_after_discount()
                    order.total = cart.get_total_price()
                order.save()
                order_items = Order.objects.prefetch_related('items').filter(id=order.id)[0].items.all()
                # some item was removed from the cart
                if len([i for i in cart]) < len(order_items):
                    for item in order_items:
                        color = item.color
                        stud = item.stud
                        product = item.product
                        found = len([i for i in cart if int(i.get('product_id')) == int(product.id) and i.get('color') == color and i.get('stud') == stud]) > 0
                        if not found:
                            item.delete()
                product_price = 0
                for item in cart:
                    OrderItem.objects.get_or_create(order=order, price=item['price'], quantity=item['quantity'],
                                                    color=item['color'] if 'color' in item else '',
                                                    stud=item['stud'] if 'stud' in item else '',
                                                    image=item['image'],
                                                    **({"product": item['product']} if item['type']
                                                                                       in ['product', 'product_type']
                                                       else {"gift_card": item['product']}))
                    product_price += int(item['price'])
                order.products_price = product_price
                if cart.coupon:
                    order.products_price_with_discount = product_price - order.discount_amount
                order.save()
        else:
            print('error', form.errors.as_data())
        if not out_of_stock:
            for key, value in request.session['cart'].items():
                for key2, value2 in request.session['cart'][key].items():
                    if isinstance(request.session['cart'][key][key2], Decimal):
                        request.session['cart'][key][str(key2)] = str(request.session['cart'][key][key2])
                    if key2 == 'product':
                        try:
                            request.session['cart'][key][str(key2)] = model_to_dict(request.session['cart'][key][key2])
                        except AttributeError:
                            messages.error(request, 'Válassza ki a megfelelő szállítási módot!')
                            return redirect('cart:cart_detail')
                        for key3, value3 in request.session['cart'][key][key2].items():
                            if key3 == 'image':
                                value = request.session['cart'][key][key2][key3].path \
                                    if request.session['cart'][key][key2][key3] != '' else ''
                                request.session['cart'][key][key2][str(key3)] = value
                            if isinstance(request.session['cart'][key][key2][key3], Decimal):
                                request.session['cart'][key][key2][str(key3)] = str(
                                    request.session['cart'][key][key2][key3])
            request.session['order_id'] = order.id
            request.session['delivery_type'] = order.delivery_type
            # o = Order.objects.prefetch_related('items').filter(id=order.id)[0]
            # prices = dict(FoxPost=settings.FOXPOST_PRICE, Csomagkuldo=settings.CSOMAGKULDO_PRICE,
            #               Házhozszállítás=settings.DELIVERY_PRICE, Személyesátvétel=0)
            # delivery_info = dict(FoxPost={'Átvételi pont': o.fox_post},
            #                      Csomagkuldo={'Átvételi pont': o.csomagkuldo},
            #                      Házhozszállítás={'Szállítási név': o.delivery_name, 'Szállítási cím': o.address,
            #                                       'Postakód': o.postal_code, 'Település': o.city, 'Megjegyzés': o.note},
            #                      Személyesátvétel={'Vezetéknév': o.first_name, 'Keresztnév': o.last_name})
            # delivery_price = prices[o.delivery_type.replace(' ', '')]
            # delivery_data = delivery_info[o.delivery_type.replace(' ', '')]
            # order_total = o.total
            # result, msg = MessageSender(subject=f'Rendelés megerősítése #{str(o.id)}', to=o.email,
            #                             sender='www.minervastudio.hu').send_order_confirmation_email(
            #     {'name': o.full_name, 'order': o,
            #      'delivery_price': delivery_price,
            #      'delivery_info': delivery_data,
            #      'order_total': order_total})
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return redirect('cart:cart_detail')


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})
