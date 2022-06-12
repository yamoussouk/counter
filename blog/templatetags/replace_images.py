from django.template.defaultfilters import register


@register.filter(name='replace_images')
def replace_images(content: list, images: list):
    idx = 0
    for c in content:
        if c == '<img></img>':
            if idx <= len(images) - 1:
                url = images[idx].image.url
                url_parts = url.split('.')
                url_without_ext = url_parts[0]
                ext = url_parts[1]
                link = images[idx].url
                link_title = images[idx].url_title
                alt = images[idx].alt
                a = alt if alt != '' else images[idx].post.title
                title = images[idx].title
                t = title if title != '' else images[idx].post.title
                image_part = '<picture>' \
                             f'<source srcset="{url_without_ext}.webp" type="image/webp">' \
                             f'<source srcset="{url}" type="image/{ext}">' \
                             f'<img src="{url}" alt="{a}" title="{t}" class="img-fluid" /> </picture>'
                without_link = f'<div class="content-image-wrapper">{image_part}</div>'
                with_link = f'<div class="content-image-wrapper"><a target="_blank" href="{link}" title={link_title}>' \
                            f'{image_part}</a></div>'
                text = without_link if link == '' else with_link
                content[content.index(c)] = text
                idx += 1
            else:
                content[content.index(c)] = ''
                idx += 1
    return content
