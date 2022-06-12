from django.template.defaultfilters import register
from typing import Any


@register.filter(name='is_object')
def is_object(element: Any):
    return not isinstance(element, str)
