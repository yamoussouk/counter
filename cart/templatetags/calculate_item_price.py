from django.template.defaultfilters import register


@register.filter(name='calculate_item_price')
def calculate_item_price(p, q):
    return int(p) * int(q)
