from django.conf import settings
from django.template.defaultfilters import register


@register.filter(name='calculate_item_price_with_discount')
def calculate_item_price_with_discount(cart, v: dict):
    if settings.DISCOUNT:
        if v.get('zero_discount'):
            return v.get('discount_show_price')
        else:
            return int(v.get('quantity')) * int(v.get('price'))
    else:
        return int(v.get('quantity')) * int(v.get('price'))
