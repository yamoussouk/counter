import os
from pathlib import Path

from PIL import Image


def convert_file(file_name):
    im = Image.open(file_name)
    temp = os.path.dirname(file_name)
    f = os.path.basename(file_name)
    p = os.path.join(temp, f.split('.')[0] + '.webp')
    im.save(p, 'webp')


def convert():
    current_path = Path(__name__).parent.resolve()
    media_path = os.path.join(current_path, 'media')
    collections_path = os.path.join(media_path, 'collections')
    images_path = os.path.join(media_path, 'images')
    blog_path = os.path.join(media_path, 'images', 'blog')

    for filename in os.listdir(media_path):
        if (filename.endswith(".png") or filename.endswith(".jpg")) and \
                not os.path.isfile(os.path.join(media_path, filename.split('.')[0] + '.webp')):
            convert_file(os.path.join(media_path, filename))
            print(filename)

    for dirpath, dirnames, filenames in os.walk(blog_path):
        for filename in [f for f in filenames if
                         (f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg")) and not os.path.isfile(
                                 os.path.join(dirpath, f.split('.')[0] + '.webp'))]:
            convert_file(os.path.join(dirpath, filename))
            print(filename)


if __name__ == '__main__':
    convert()
