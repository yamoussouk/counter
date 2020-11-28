import re

from django.template.defaultfilters import register


@register.filter(name='convert_date')
def convert_date(d):
    months = dict(January='Január', February='Február', March='Március', April='Április', May='Május', June='Június',
                  July='Június', August='Augusztus', September='Szeptember', October='Október', November='November',
                  December='December')
    month = months[d.strftime('%B')]
    fine_format = d.strftime('%Y. %B %d.')
    fixed_date = re.sub('[a-zA-Z]{1,}', month.lower(), fine_format, count=1)
    return fixed_date
