from django.template.defaultfilters import register


@register.filter(name='get_key_ring')
def get_key_ring(product, stud_value):
    return product.get_key_ring_value(int(stud_value))
