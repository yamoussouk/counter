from django.template.defaultfilters import register


@register.filter(name='is_stock')
def is_stock(items, product_id):
    is_stock = False
    for item in items:
        if product_id == item[0]:
            if item[1] > 0:
                is_stock = True
    return is_stock