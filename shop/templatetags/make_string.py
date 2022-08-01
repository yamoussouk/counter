from django.template.defaultfilters import register


@register.filter(name='make_string')
def make_string(value):
    return str(value)
