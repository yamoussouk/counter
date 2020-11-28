from django.template.defaultfilters import register


@register.filter(name='calculate_price')
def calculate_price(v, args):
    function, flag = args.split(',')
    flag = flag == 'True'
    return getattr(v, function)(flag)
