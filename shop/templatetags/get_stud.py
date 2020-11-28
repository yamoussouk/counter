from django.template.defaultfilters import register


@register.filter(name='get_stud')
def get_stud(product, stud_value):
    return product.get_stud_value(int(stud_value))
