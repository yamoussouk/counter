from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from cart.cart import Cart
from logs.models import LogFile
from parameters.models import Parameter
from shop.models import ProductType
from .forms import OrderCreateForm
from .models import Order, OrderItem

prices = dict(FoxPost=int(Parameter.objects.filter(name="foxpost_price")[0].value),
              Csomagkuldo=int(Parameter.objects.filter(name="csomagkuldo_price")[0].value),
              Házhozszállítás=int(Parameter.objects.filter(name="delivery_price")[0].value),
              Személyesátvétel=0,
              Ajanlott=int(Parameter.objects.filter(name="ajanlott_price")[0].value))
delivery_types = {"0": "Személyes átvétel", "1": "Csomagkuldo", "2": "Ajanlott", "3": "FoxPost", "4": "Házhozszállítás"}


def create_log_file(message: str, log_type: str = 'INFO') -> 'None':
    LogFile.objects.create(type=log_type, message=message)


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


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')
        if len(ip):
            return ip[0]
        else:
            return ip
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _create_or_update_order_item(cart, order):
    for item in cart:
        order_item = OrderItem.objects.filter(
            order=order, price=item['price'],
            color=item['color'] if 'color' in item else '',
            stud=item['stud'] if 'stud' in item else '',
            finding=item['findings'] if 'findings' in item else '',
            first_initial=item[
                'first_initial'] if 'first_initial' in item and item[
                'first_initial'] != '--' else '',
            second_initial=item[
                'second_initial'] if 'second_initial' in item and item[
                'second_initial'] != '--' else '',
            custom_date=item['custom_date'] if 'custom_date' in item and
                                               item[
                                                   'custom_date'] != '1899-01-01' else '',
            image=item['image'],
            **({"product": item['product']} if item['type']
                                               in ['product',
                                                   'product_type']
               else {"gift_card": item['product']}))
        if len(order_item):
            order_item[0].quantity = item['quantity']
            order_item[0].save()
        else:
            OrderItem.objects.create(
                order=order, price=item['price'], quantity=item['quantity'],
                color=item['color'] if 'color' in item else '',
                stud=item['stud'] if 'stud' in item else '',
                finding=item['findings'] if 'findings' in item else '',
                first_initial=item[
                    'first_initial'] if 'first_initial' in item and item[
                    'first_initial'] != '--' else '',
                second_initial=item[
                    'second_initial'] if 'second_initial' in item and item[
                    'second_initial'] != '--' else '',
                custom_date=item['custom_date'] if 'custom_date' in item and
                                                   item[
                                                       'custom_date'] != '1899-01-01' else '',
                image=item['image'],
                **({"product": item['product']} if item['type']
                                                   in ['product',
                                                       'product_type']
                   else {"gift_card": item['product']}))


def _append_session_data(request, cd):
    request.session['delivery'] = dict(delivery_type=delivery_types[str(cd['delivery_type_code'])],
                                       delivery_code=str(cd['delivery_type_code']),
                                       address=cd['address'],
                                       postal_code=cd['postal_code'], city=cd['city'], note=cd['note'],
                                       fox_post=cd['fox_post'],
                                       delivery_name=cd['delivery_name'],
                                       first_name=cd['first_name'], last_name=cd['last_name'],
                                       csomagkuldo=cd['csomagkuldo'], address_number=cd['address_number'])
    request.session['mandatory'] = dict(full_name=cd['full_name'], email=cd['email'], phone=cd['phone'])
    request.session['billing'] = dict(billing_address=cd['billing_address'],
                                      billing_address_number=cd['billing_address_number'],
                                      billing_postal_code=cd['billing_postal_code'],
                                      billing_city=cd['billing_city'], product_note=cd['product_note'])
    create_log_file(f'Delivery method: {request.session["delivery"]}, user: {get_client_ip(request)}')
    return request


def _create_order(request, cart, cd, form):
    order = cart.order
    if order:
        order.full_name = cd['full_name']
        order.phone = cd['phone']
        order.email = cd['email']
        order.billing_address = cd['billing_address']
        order.billing_address_number = cd['billing_address_number']
        order.billing_postal_code = cd['billing_postal_code']
        order.billing_city = cd['billing_city']
        order.first_name = cd['first_name']
        order.last_name = cd['last_name']
        order.delivery_name = cd["delivery_name"]
        order.address = cd["address"]
        order.address_number = cd["address_number"]
        order.postal_code = cd["postal_code"]
        order.city = cd["city"]
        order.note = cd["note"]
        order.delivery_type = delivery_types[str(cd['delivery_type_code'])]
        order.fox_post = cd['fox_post']
        order.csomagkuldo = cd['csomagkuldo']
        order.product_note = cd['product_note']
        create_log_file(f'Order "{order.id}" already exists, user: {get_client_ip(request)}')
    else:
        order = form.save(commit=False)
        order.delivery_type = delivery_types[str(cd['delivery_type_code'])]
    order.subtotal = cart.get_total_price_after_discount()  # delivery excluded
    if cart.coupon:
        order.coupon = cart.coupon
        order.discount = cart.coupon.discount
        order.discount_amount = float(cart.get_total_price()) - float(cart.get_total_price_after_discount())
    order.save()
    create_log_file(f'Order "{order.id}" is saved, user: {get_client_ip(request)}')
    return order


def _remove_items_from_the_cart(cart, order_items):
    # some item was removed from the cart
    for item in order_items:
        color = item.color
        stud = item.stud
        finding = item.finding
        product = item.product
        found = len([i for i in cart if
                     int(i.get('product_id')) == int(product.id) and i.get('color') == color and i.get(
                         'stud') == stud and i.get('finding') == finding]) > 0
        if not found:
            item.delete()


def _convert_values(request):
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
                    if key3 == 'collections':
                        collections = request.session['cart'][key][key2][key3]
                        collection_names = [cn.name for cn in collections]
                        value = ', '.join(collection_names)
                        request.session['cart'][key][key2][str(key3)] = value
                    if isinstance(request.session['cart'][key][key2][key3], Decimal):
                        request.session['cart'][key][key2][str(key3)] = str(
                            request.session['cart'][key][key2][key3])
    return request


def _calculate_price(order, cart):
    order.products_price = cart.get_total_price()
    order.products_price_with_discount = cart.get_total_price() - order.discount_amount \
        if cart.coupon else cart.get_total_price()
    order.delivery_cost = prices[order.delivery_type.replace(' ', '')]
    order.total = cart.get_total_price_after_discount() + order.delivery_cost
    if Parameter.objects.filter(name="discount_service")[0].value == 'True' and len(cart) > 2:
        order.coupon = None
        order.discount = 0
        order.discount_amount = 0
    return order


def order_create(request):
    cart = Cart(request)
    out_of_stock = False
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            for item in cart:
                if item['product'].custom:
                    status, item_in_cart, stock = True, 0, 0
                else:
                    status, item_in_cart, stock = __validate_stock(cart.cart, item['product'], item)
                if not status:
                    out_of_stock = True
                    messages.error(request,
                                   f'A megvásárolni kívánt, illetve a kosaradban található termék összes mennyisége'
                                   f' meghaladja az elérhető mennyiséget, amely {stock}. A kosaradban az aktuális termék '
                                   f'mennyisége {item_in_cart}.')
                    print('warning', f'Product is out of stock: {item["product"]}')
                    return redirect('cart:cart_detail')

            create_log_file(f'Valid form, order received, user: {get_client_ip(request)}')
            if not out_of_stock:
                request = _append_session_data(request, cd)
                order = _create_order(request, cart, cd, form)
                order_items = Order.objects.prefetch_related('items').filter(id=order.id)[0].items.all()
                _remove_items_from_the_cart(cart, order_items)
                _create_or_update_order_item(cart, order)
                order = _calculate_price(order, cart)
                create_log_file(f'Order process initiated, items: {", ".join([str(i["product_id"]) for i in cart])},'
                                f' user: {get_client_ip(request)}')
                order.save()
                request = _convert_values(request)
                request.session['order_id'] = order.id
                request.session['delivery_type'] = order.delivery_type
                return redirect(reverse('payment:process'))
        else:
            print('error', form.errors.as_data())
            messages.error(request, form.errors.as_data())
            return redirect('cart:cart_detail')
    else:
        form = OrderCreateForm()
    return redirect('cart:cart_detail')


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})
