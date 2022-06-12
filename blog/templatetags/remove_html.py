import re

from django.template.defaultfilters import register


@register.filter(name='remove_html')
def remove_html(content: str):
    cleared = re.sub('<[^<]+?>', '', content)[:200]
    return f'{cleared}...'
