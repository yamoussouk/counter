from django.template.defaultfilters import register


@register.filter(name='wp')
def wp(i):
    return i.split('.')[0] + '.webp'
