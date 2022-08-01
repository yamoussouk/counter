from django.template.defaultfilters import register


@register.filter(name='get_finding')
def get_stud(product, finding_value):
    return product.get_finding_value(int(finding_value))
