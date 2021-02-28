from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from coupon.models import Coupon
from shop.models import Product, GiftCard


class Order(models.Model):
    full_name = models.CharField(max_length=200, default='')
    email = models.EmailField()
    billing_address = models.CharField(max_length=250, default='', blank=True)
    billing_postal_code = models.CharField(max_length=20, default='', blank=True)
    billing_city = models.CharField(max_length=100, default='', blank=True)
    delivery_type = models.CharField(max_length=50, default='')
    first_name = models.CharField(max_length=50, default='', blank=True)
    last_name = models.CharField(max_length=50, default='', blank=True)
    delivery_name = models.CharField(max_length=250, default='', blank=True)
    address = models.CharField(max_length=250, default='', blank=True)
    postal_code = models.CharField(max_length=20, default='', blank=True)
    city = models.CharField(max_length=100, default='', blank=True)
    note = models.CharField(max_length=250, default='', blank=True)
    fox_post = models.CharField(max_length=250, default='', blank=True)
    csomagkuldo = models.CharField(max_length=250, default='', blank=True)
    products_price = models.IntegerField(default=0)
    products_price_with_discount = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    paid_by = models.CharField(max_length=50, default='', blank=True)
    coupon = models.ForeignKey(Coupon, related_name='orders', null=True, blank=True, on_delete=models.CASCADE)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    # discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.IntegerField(default=0, validators=[MinValueValidator(0)], null=True, blank=True)
    # subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    subtotal = models.IntegerField(default=0, validators=[MinValueValidator(0)], null=True, blank=True)
    # total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.IntegerField(default=0, validators=[MinValueValidator(0)], null=True, blank=True)
    delivery_cost = models.IntegerField(default=0, validators=[MinValueValidator(0)], null=True, blank=True)
    paid_time = models.CharField(default='', max_length=50, blank=True)
    phone = models.CharField(max_length=25, default='', blank=True)
    shipped = models.BooleanField(default=False)
    product_note = models.CharField(max_length=250, default='', blank=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        total_cost = sum(item.get_cost() for item in self.items.all())
        return total_cost - (total_cost * (self.discount / Decimal('100')))

    def get_coupon_code(self):
        return self.coupon.code

    def get_discount_amount(self):
        total_cost = sum(item.get_cost() for item in self.items.all())
        return total_cost * (self.discount / Decimal('100'))


class OrderSummary(Order):
    class Meta:
        proxy = True
        verbose_name = 'Order summary'
        verbose_name_plural = 'Orders summary'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, blank=True, null=True)
    gift_card = models.ForeignKey(GiftCard, related_name='order_giftcard_items', on_delete=models.CASCADE,
                                  default='', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, default='', blank=True, null=True)
    stud = models.CharField(max_length=100, default='', blank=True, null=True)
    image = models.CharField(max_length=250, null=True, default='', blank=True)
    first_initial = models.CharField(max_length=3, null=True, default='', blank=True)
    second_initial = models.CharField(max_length=3, null=True, default='', blank=True)
    custom_date = models.CharField(max_length=10, null=True, default='', blank=True)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity


class OrderItemSummary(OrderItem):
    class Meta:
        proxy = True
        verbose_name = 'Order item summary'
        verbose_name_plural = 'Order items summary'
