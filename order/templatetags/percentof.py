from django.template.defaultfilters import register


@register.filter(name='percentof')
def percentof(a, b):
    try:
        return round((int(a) / int(b)) * 100, 2)
    except ZeroDivisionError:
        return 0.0
