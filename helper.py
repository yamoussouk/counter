import os
import subprocess
from pathlib import Path

current_path = Path(__name__).parent.resolve()


def convert_file(file_name):
    exe_ = os.path.join(current_path, 'cwebp.exe')
    new_name = file_name.split('.')[0] + '.webp'
    subprocess.check_call([exe_, file_name, '-o', new_name])


def convert():
    media_path = os.path.join(current_path, 'media')
    collections_path = os.path.join(media_path, 'collections')
    images_path = os.path.join(media_path, 'images')
    carousel_path = os.path.join(current_path, 'shop', 'static', 'images', 'home_page_carousel')
    blog_path = os.path.join(media_path, 'images', 'blog')
    test_path = os.path.join(media_path, 'test')

    # for filename in os.listdir(media_path):
    #     if (filename.endswith(".png") or filename.endswith(".jpg")) and \
    #             not os.path.isfile(os.path.join(media_path, filename.split('.')[0] + '.webp')):
    #         convert_file(os.path.join(media_path, filename))
    #         print(filename)
    #
    # for filename in os.listdir(collections_path):
    #     if (filename.endswith(".png") or filename.endswith(".jpg")) and \
    #             not os.path.isfile(os.path.join(collections_path, filename.split('.')[0] + '.webp')):
    #         convert_file(os.path.join(collections_path, filename))
    #         print(filename)
    #
    # for filename in os.listdir(images_path):
    #     if (filename.endswith(".png") or filename.endswith(".jpg")) and \
    #             not os.path.isfile(os.path.join(images_path, filename.split('.')[0] + '.webp')):
    #         convert_file(os.path.join(images_path, filename))
    #         print(filename)
    #
    # for filename in os.listdir(carousel_path):
    #     if (filename.endswith(".png") or filename.endswith(".jpg")) and \
    #             not os.path.isfile(os.path.join(carousel_path, filename.split('.')[0] + '.webp')):
    #         convert_file(os.path.join(carousel_path, filename))
    #         print(filename)

    for filename in os.listdir(test_path):
        if (filename.endswith(".png") or filename.endswith(".jpg")) and \
                not os.path.isfile(os.path.join(test_path, filename.split('.')[0] + '.webp')):
            convert_file(os.path.join(test_path, filename))
            print(filename)

    # for dirpath, dirnames, filenames in os.walk(blog_path):
    #     for filename in [f for f in filenames if
    #                      (f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg")) and not os.path.isfile(
    #                          os.path.join(dirpath, f.split('.')[0] + '.webp'))]:
    #         convert_file(os.path.join(dirpath, filename))
    #         print(filename)


if __name__ == '__main__':
    convert()
