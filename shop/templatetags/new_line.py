from django.template.defaultfilters import register


@register.filter(name='new_line')
def new_line(desc):
    rows = desc.split('\n')
    return rows