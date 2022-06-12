from django.template.defaultfilters import register


@register.filter(name='wp')
def wp(i):
    img = i if isinstance(i, str) else i[0]
    return img.split('.')[0] + '.webp'
