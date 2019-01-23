#!/usr/bin/python

import argparse
import glob
import os

from PIL import Image, ImageOps


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description= \
        '''Create image thumbnails''')
        
    parser.add_argument('--src-dir', type=str, required=True,
                        help='directory containing images')
    parser.add_argument('--thumbnails-dir', type=str, required=True,
                        help='destination directory for thumbnails')
    parser.add_argument('--size', type=str, default='300,300',
                        help='size of a thumbnail image (defaults to 300,300)')

    args = parser.parse_args()
    thumbnails_dir = args.thumbnails_dir
    src_dir = args.src_dir
    size = args.size

    parts = size.split(',')
    thumbnail_size = int(parts[0].strip()), int(parts[1].strip()) if parts and len(parts) == 2 else (300, 300)

    for image_file in glob.glob(os.path.join(src_dir, '**/*.*'), recursive=True):
        if not image_file.lower().endswith('.jpg') and not image_file.lower().endswith('.jpeg'):
            continue

        parentdir = os.path.basename(os.path.dirname(image_file))
        basename = os.path.basename(image_file)

        src_image = Image.open(image_file)
        thumb_image = ImageOps.fit(src_image, thumbnail_size, Image.ANTIALIAS)
        
        save_dir = os.sep.join([thumbnails_dir, parentdir])
        os.makedirs(save_dir, exist_ok=True)
        thumb_image.save(os.sep.join([save_dir, basename]), "JPEG")

