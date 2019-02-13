#!/usr/bin/python

import argparse
import glob
import os
import subprocess

from PIL import Image, ImageOps, ExifTags


def create_thumbnail(input_file, out_file, size):
    image = Image.open(input_file)

    for orientation in ExifTags.TAGS.keys() : 
        if ExifTags.TAGS[orientation] == 'Orientation':
            break

    exif_info = image._getexif()
    if exif_info:
        exif = dict(exif_info.items())

        if exif.get(orientation, 0) == 3: 
            image=image.rotate(180, expand=True)
        elif exif.get(orientation, 0) == 6: 
            image=image.rotate(270, expand=True)
        elif exif.get(orientation, 0) == 8: 
            image=image.rotate(90, expand=True)

    thumbnail = ImageOps.fit(image, size, Image.ANTIALIAS)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    thumbnail.save(out_file, "JPEG")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description= \
        '''Create thumbnails for image and video files (*.jpg; *.jpeg; *.mp4; *.mov)''')
        
    parser.add_argument('--src-dir', type=str, required=True,
                        help='directory containing media files')
    parser.add_argument('--thumbnails-dir', type=str, required=True,
                        help='destination directory for thumbnails')
    parser.add_argument('--size', type=str, default='300,300',
                        help='size of a thumbnail image (defaults to 300,300)')

    args = parser.parse_args()
    thumbnails_dir = args.thumbnails_dir
    src_dir = args.src_dir
    size = args.size

    os.makedirs(thumbnails_dir, exist_ok=True)

    parts = size.split(',')
    thumbnail_size = int(parts[0].strip()), int(parts[1].strip()) if parts and len(parts) == 2 else (300, 300)

    for media_file in glob.glob(os.path.join(src_dir, '**/*.*'), recursive=True):
        if not media_file.lower().endswith('.jpg') and \
            not media_file.lower().endswith('.jpeg') and \
            not media_file.lower().endswith('.mp4') and \
            not media_file.lower().endswith('.mov'):
            continue

        parent_dir = os.path.basename(os.path.dirname(media_file))
        file_name = os.path.basename(media_file)

        if file_name.lower().endswith('.mp4') or file_name.lower().endswith('.mov'):
            tmp_file = os.sep.join([thumbnails_dir, '.video_thumbnail.jpg'])
            cmnd = ['ffmpeg.exe', '-i', media_file, '-ss', '00:00:00', '-vframes', '1', tmp_file]
            p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _out, _err = p.communicate()

            create_thumbnail(tmp_file, os.sep.join([thumbnails_dir, parent_dir,
                '{0}.jpg'.format(os.path.splitext(file_name)[0])]), thumbnail_size)
            os.remove(tmp_file)
        else:
            create_thumbnail(media_file, os.sep.join([thumbnails_dir, parent_dir,
                '{0}.jpg'.format(os.path.splitext(file_name)[0])]), thumbnail_size)
        
