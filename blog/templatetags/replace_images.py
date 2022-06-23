import re

from django.template.defaultfilters import register


@register.filter(name='replace_images')
def replace_images(content: str, images: list):
    content = content.replace('\r\n', '<br />')
    for image in images:
        url = image.image.url
        url_parts = url.split('.')
        url_without_ext = url_parts[0]
        ext = url_parts[1]
        link = image.url
        link_title = image.url_title
        alt = image.alt
        a = alt if alt != '' else image.post.title
        title = image.title
        t = title if title != '' else image.post.title
        image_part = '<picture>' \
                     f'<source srcset="{url_without_ext}.webp" type="image/webp">' \
                     f'<source srcset="{url}" type="image/{ext}">' \
                     f'<img src="{url}" alt="{a}" title="{t}" class="img-fluid" /> </picture>'
        without_link = f'<div class="content-image-wrapper">{image_part}</div>'
        with_link = f'<div class="content-image-wrapper"><a target="_blank" href="{link}" title={link_title}>' \
                    f'{image_part}</a></div>'
        text = without_link if link == '' else with_link
        content = re.sub('<img></img>', text, content, 1)
    return content
