from django.template.defaultfilters import register


@register.filter(name='hashtags')
def hashtags(hash_tags: str):
    return ', '.join([f'#{h.upper()}' for h in hash_tags.split(',')])
