from django.template.defaultfilters import register

from parameters.models import Parameter


@register.filter(name='calculate_item_price_with_discount')
def calculate_item_price_with_discount(cart, v: dict):
    if Parameter.objects.filter(name="discount_service")[0].value == 'True':
        if v.get('zero_discount'):
            return v.get('discount_show_price')
        else:
            return int(v.get('quantity')) * int(v.get('price'))
    else:
        return int(v.get('quantity')) * int(v.get('price'))
