from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from cart.cart import Cart
from parameters.models import Parameter
from shop.models import ProductType
from .forms import OrderCreateForm, OrderCreateFormWithoutDelivery
from .models import Order, OrderItem

prices = dict(FoxPost=int(Parameter.objects.filter(name="foxpost_price")[0].value),
              Csomagkuldo=int(Parameter.objects.filter(name="csomagkuldo_price")[0].value),
              Házhozszállítás=int(Parameter.objects.filter(name="delivery_price")[0].value),
              Személyesátvétel=0,
              Ajanlott=int(Parameter.objects.filter(name="ajanlott_price")[0].value))

delivery_types = {"0": "Személyes átvétel", "1": "Csomagkuldo", "2": "FoxPost", "3": "Házhozszállítás", "4": "Ajanlott"}


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
        all_product_types = [value['type'] for key, value in cart.cart.items()]
        is_gift_card_alone_in_the_cart = all(x == 'gift_card' for x in all_product_types)
        form = OrderCreateFormWithoutDelivery(request.POST) if is_gift_card_alone_in_the_cart \
            else OrderCreateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            for item in cart:
                if hasattr(item['product'], 'custom') and item['product'].custom:
                    status, item_in_cart, stock = True, 0, 0
                else:
                    status, item_in_cart, stock = __validate_stock(cart.cart, item['product'], item)
                if not status:
                    out_of_stock = True
                    messages.error(request,
                                   f'A megvásárolni kívánt, illetve a kosaradban található termék összes mennyisége'
                                   f' meghaladja az elérhető mennyiséget, amely {stock}. A kosaradban az aktuális termék '
                                   f'mennyisége {item_in_cart}.')
            if not out_of_stock:
                if not is_gift_card_alone_in_the_cart:
                    request.session['delivery'] = dict(delivery_type=delivery_types[cd['delivery_type']],
                                                       address=cd['address'],
                                                       postal_code=cd['postal_code'], city=cd['city'], note=cd['note'],
                                                       fox_post=cd['fox_post'], delivery_name=cd['delivery_name'],
                                                       first_name=cd['first_name'], last_name=cd['last_name'],
                                                       csomagkuldo=cd['csomagkuldo'])
                    request.session['mandatory'] = dict(full_name=cd['full_name'], email=cd['email'], phone=cd['phone'])
                    request.session['billing'] = dict(billing_address=cd['billing_address'],
                                                      billing_postal_code=cd['billing_postal_code'],
                                                      billing_city=cd['billing_city'], product_note=cd['product_note'])
                order = cart.order
                if order:
                    order.full_name = request.POST.get('full_name')
                    order.phone = request.POST.get('phone')
                    order.email = request.POST.get('email')
                    order.billing_address = request.POST.get('billing_address')
                    order.billing_postal_code = request.POST.get('billing_postal_code')
                    order.billing_city = request.POST.get('billing_city')
                    order.first_name = request.POST.get('first_name', '')
                    order.last_name = request.POST.get('last_name', '')
                    order.delivery_name = request.POST.get('delivery_name', '')
                    order.address = request.POST.get('address', '')
                    order.postal_code = request.POST.get('postal_code', '')
                    order.city = request.POST.get('city', '')
                    order.note = request.POST.get('note', '')
                    order.delivery_type = delivery_types[cd.get('delivery_type')]
                    order.fox_post = request.POST.get('fox_post', '')
                    order.csomagkuldo = request.POST.get('csomagkuldo', '')
                    order.product_note = request.POST.get('product_note', '')
                    if cart.gift_card_ids:
                        order.used_gift_cards = ','.join([str(c.get('id')) for c in cart.gift_card_ids])
                else:
                    order = form.save(commit=False)
                    order.delivery_type = delivery_types[order.delivery_type]
                    order = form.save(commit=False)
                    if cart.gift_card_ids:
                        order.used_gift_cards = ','.join([str(c.get('id')) for c in cart.gift_card_ids])
                        order = form.save(commit=False)
                order.subtotal = cart.get_total_price_after_discount()  # delivery excluded
                if cart.coupon:
                    order.coupon = cart.coupon
                    order.discount = cart.coupon.discount
                    order.discount_amount = float(cart.get_total_price()) - float(cart.get_total_price_after_discount())
                order.save()
                order_items = Order.objects.prefetch_related('items').filter(id=order.id)[0].items.all()
                # some item was removed from the cart
                if len([i for i in cart]) < len(order_items):
                    for item in order_items:
                        color = item.color
                        stud = item.stud
                        product = item.product
                        found = len([i for i in cart if
                                     int(i.get('product_id')) == int(product.id) and i.get('color') == color and i.get(
                                         'stud') == stud]) > 0
                        if not found:
                            item.delete()
                for item in cart:
                    OrderItem.objects.get_or_create(order=order, price=item['price'], quantity=item['quantity'],
                                                    color=item['color'] if 'color' in item else '',
                                                    stud=item['stud'] if 'stud' in item else '',
                                                    first_initial=item[
                                                        'first_initial'] if 'first_initial' in item and item[
                                                        'first_initial'] != '--' else '',
                                                    second_initial=item[
                                                        'second_initial'] if 'second_initial' in item and item[
                                                        'second_initial'] != '--' else '',
                                                    custom_date=item['custom_date'] if 'custom_date' in item and item[
                                                        'custom_date'] != '1899-01-01' else '',
                                                    image=item['image'],
                                                    **({"product": item['product']} if item['type']
                                                                                       in ['product', 'product_type']
                                                       else {"gift_card": item['product']}))
                order.products_price = cart.get_total_price()
                order.products_price_with_discount = cart.get_total_price() - order.discount_amount \
                    if cart.coupon else cart.get_total_price()
                order.delivery_cost = prices[order.delivery_type.replace(' ', '')] \
                    if not is_gift_card_alone_in_the_cart else 0
                order.total = cart.get_total_price_after_discount() + order.delivery_cost
                order.save()
        else:
            error = form.errors.as_data()
            print('error', error)
        if not out_of_stock:
            for key, value in request.session['cart'].items():
                for key2, value2 in request.session['cart'][key].items():
                    if isinstance(request.session['cart'][key][key2], Decimal):
                        request.session['cart'][key][str(key2)] = str(request.session['cart'][key][key2])
                    if key2 == 'product':
                        try:
                            request.session['cart'][key][str(key2)] = model_to_dict(request.session['cart'][key][key2])
                        except AttributeError as e:
                            request.session['cart'][key][str(key2)] = request.session['cart'][key][key2]
                            # print(e)
                            # messages.error(request, 'Válassza ki a megfelelő szállítási módot!')
                            # return redirect('cart:cart_detail')
                        for key3, value3 in request.session['cart'][key][key2].items():
                            if key3 == 'image':
                                img = request.session['cart'][key][key2][key3]
                                if isinstance(img, str):
                                    value = img if img != '' else ''
                                else:
                                    value = img.path
                                request.session['cart'][key][key2][str(key3)] = value
                            if isinstance(request.session['cart'][key][key2][key3], Decimal):
                                request.session['cart'][key][key2][str(key3)] = str(
                                    request.session['cart'][key][key2][key3])
            request.session['order_id'] = order.id
            request.session['delivery_type'] = order.delivery_type
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return redirect('cart:cart_detail')


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})
