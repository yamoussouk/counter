import math
from decimal import Decimal

from django.conf import settings

from coupon.models import Coupon
# from giftcardpayment.models import BoughtGiftCard
from order.models import Order
from shop.models import Product, GiftCard, ProductType


class Cart(object):

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')
        self.gift_card_ids = self.session.get('gift_card_ids')
        self.order_id = self.session.get('order_id')
        self.delivery_type = self.session.get('delivery_type')
        self.prices = dict(FoxPost=settings.FOXPOST_PRICE, Csomagkuldo=settings.CSOMAGKULDO_PRICE,
                           Házhozszállítás=settings.DELIVERY_PRICE, Személyesátvétel=0)

    def get_cart(self):
        temp = self.cart
        return temp

    def add(self, product, color, stud, quantity=1, update_quantity=False):
        item_type = 'product_type'
        try:
            p = ProductType.objects.get(product=product, color=color)
            product_type_id = str(p.id)
        except ProductType.DoesNotExist:
            p = product
            product_type_id = str(p.id)
            item_type = 'product'
        except ValueError:
            p = product
            item_type = 'gift_card'
        is_cart_empty = len(self.cart.keys()) == 0
        new_cart_id = str(max([int(key) for key in self.cart.keys()]) + 1) if not is_cart_empty else '1'
        if is_cart_empty:
            self.cart[new_cart_id] = {'quantity': 0, 'price': str(product.price)}
        else:
            found = False
            for key, value in self.cart.copy().items():
                if self.cart[key]['product_id'] == product.id and self.cart[key]['type'] == item_type and \
                        self.cart[key]['color'] == color and self.cart[key]['stud'] == stud:
                    found = True
                    new_cart_id = key
                    break
            if not found:
                self.cart[new_cart_id] = {'quantity': 0, 'price': str(product.price)}
        if update_quantity:
            self.cart[new_cart_id]['quantity'] = quantity
        else:
            self.cart[new_cart_id]['quantity'] += quantity

        self.cart[new_cart_id]['type'] = item_type
        self.cart[new_cart_id]['color'] = p.color if hasattr(p, 'color') else ''
        self.cart[new_cart_id]['stud'] = stud
        self.cart[new_cart_id]['image'] = p.image.url if hasattr(p, 'image') else ''
        self.cart[new_cart_id]['product_id'] = product.id
        self.cart[new_cart_id]['product_name'] = product.name
        self.cart[new_cart_id]['product_total_price'] = product.price * quantity
        self.cart[new_cart_id]['collection'] = product.collection.name if hasattr(product, 'collection') else ''
        self.save()

    def add_gift_card(self, giftcard, amount, quantity=1, update_quantity=False):
        gift_card_id = str(giftcard.id)
        if gift_card_id not in self.cart:
            self.cart[gift_card_id] = {'quantity': 0, 'price': str(amount)}
        if update_quantity:
            self.cart[gift_card_id]['quantity'] = quantity
        else:
            self.cart[gift_card_id]['quantity'] += quantity
        self.cart[gift_card_id]['type'] = 'giftcard'
        self.cart[gift_card_id]['id'] = gift_card_id
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, item_id):
        if str(item_id) in self.cart:
            del self.cart[str(item_id)]
        if len(self.cart) == 0:
            props = ['coupon_id', 'gift_card_ids', 'delivery', 'mandatory', 'order_id', 'delivery_type']
            for p in props:
                if p in self.session:
                    if p == 'order_id':
                        Order.objects.filter(id=self.session[p])[0].delete()
                    del self.session[p]
        self.save()
        return self.cart

    def __iter__(self):
        product_ids = self.cart.keys()
        type = [self.cart[c] for c in self.cart.keys()]
        products = []
        for t in type:
            if t.get('type') == 'product' or t.get('type') == 'product_type':
                products.append(Product.objects.get(id=t.get('product_id')))
            else:
                products.append(GiftCard.objects.get(id=t.get('product_id')))
        # products = Product.objects.filter(id__in=product_ids)
        for product in products:
            for key, value in self.cart.items():
                if int(self.cart[key].get('product_id')) == int(product.id):
                    self.cart[key]['product'] = product
            # self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        props = ['coupon_id', 'gift_card_ids', 'delivery', 'mandatory', 'order_id', 'delivery_type']
        for p in props:
            if p in self.session:
                del self.session[p]
        self.session.modified = True

    def set_delivery_type(self, delivery_type):
        self.delivery_type = delivery_type

    def get_delivery_type(self):
        if self.session.get('delivery'):
            return self.session.get('delivery')
        return None

    @property
    def order(self):
        if self.order_id:
            return Order.objects.prefetch_related('items').filter(id=self.order_id)[0]
        return None

    @order.setter
    def clear_order(self):
        self.order = None

    @property
    def coupon(self):
        if self.coupon_id:
            return Coupon.objects.get(id=self.coupon_id)
        return None

    @coupon.setter
    def clear_coupon(self):
        self.coupon = None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal('100')) * self.get_total_price()
        return Decimal('0')

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()

    # @property
    # def gift_cards(self):
    #     if self.gift_card_ids:
    #         return [BoughtGiftCard.objects.get(id=gc) for gc in self.gift_card_ids]
    #     return None

    # @gift_cards.setter
    # def clear_gift_card(self):
    #     self.gift_card_ids = []

    # def get_gift_card_amount(self):
    #     amount = Decimal('0')
    #     if self.gift_card_ids:
    #         for gc in self.gift_cards:
    #             amount += gc.price
    #         return amount
    #     return amount

    def calculated_total_price(self, delivery=True, gift_card=True):
        total_price = self.get_total_price_after_discount() if self.coupon else self.get_total_price()
        if delivery:
            delivery_type = self.session.get('delivery').get('delivery_type')
            delivery_amount = self.prices[delivery_type.replace(' ', '')]
        else:
            delivery_amount = 0
        # if gift_card:
        #     amount = self.get_gift_card_amount() if self.gift_cards else 0
        # else:
        #     amount = 0
        amount = 0
        diff = total_price + delivery_amount - amount
        return int(math.ceil(diff)) if diff > 0 else 0