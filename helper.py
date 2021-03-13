import os
from pathlib import Path

from PIL import Image


def convert_file(file_name):
    im = Image.open(file_name)
    temp = os.path.dirname(file_name)
    f = os.path.basename(file_name)
    p = os.path.join(temp, f.split('.')[0] + '.webp')
    im.save(p, 'webp')


current_path = Path(__name__).parent.resolve()
media_path = os.path.join(current_path, 'media')
collections_path = os.path.join(media_path, 'collections')
images_path = os.path.join(media_path, 'images')

# for filename in os.listdir(media_path):
#     if filename.endswith(".png") and not os.path.isfile(os.path.join(media_path, filename.split('.')[0] + '.webp')):
#         convert_file(os.path.join(media_path, filename))
#         print(filename)
#
# for filename in os.listdir(collections_path):
#     if filename.endswith(".png") and not os.path.isfile(
#             os.path.join(collections_path, filename.split('.')[0] + '.webp')):
#         convert_file(os.path.join(collections_path, filename))
#         print(filename)
#
# for filename in os.listdir(images_path):
#     if filename.endswith(".png") and not os.path.isfile(os.path.join(images_path, filename.split('.')[0] + '.webp')):
#         convert_file(os.path.join(images_path, filename))
#         print(filename)
