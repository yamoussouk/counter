from django.template.defaultfilters import register
import re


@register.filter(name='split')
def split(content):
    return [l for l in re.findall(r'<[^>].*>.*?</[^>]*>(?:<[^>]*/>)?|[^<>]+', content) if l != '\n']