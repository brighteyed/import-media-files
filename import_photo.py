#!/usr/bin/python

import argparse
import datetime
import glob
import json
import os
import shutil

import exifread

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import photo files')
    parser.add_argument('--takeout-dir', type=str,
                        help='Directory with photos')
    parser.add_argument('--out-dir', type=str,
                        help='Destination directory')

    args = parser.parse_args()
    out_dir = args.out_dir
    takeout_dir = args.takeout_dir

    copied = []

    for src_file in glob.glob(os.path.join(takeout_dir, '**/*.jpg'), recursive=True):
        try:
            with open(src_file, 'rb') as file:
                tags = exifread.process_file(file, details=False)
                if 'EXIF DateTimeOriginal' not in tags.keys():
                    print('[ERROR] No tag in {0}'.format(src_file))
                    continue

                try:
                    dt = datetime.datetime.strptime(str(tags['EXIF DateTimeOriginal']).split(' ')[0], '%Y:%m:%d')
                    dir = os.path.join(out_dir, dt.strftime('%Y-%m-%d'))
                    os.makedirs(dir, exist_ok=True)

                    dst_file = os.path.join(dir, os.path.basename(src_file))
                    if os.path.exists(dst_file):
                        print('[WARNING] File already exists {0}'.format(dst_file))
                        continue

                    print('{0} -> {1}'.format(src_file, dst_file))
                    shutil.copyfile(src_file, dst_file)

                    copied.append(os.sep.join(os.path.normpath(dst_file).split(os.sep)[-2:]))

                except ValueError:
                    print('[ERROR] Ошибка обработки файла {0}'.format(src_file))

        except PermissionError:
            print('[ERROR] PermissionError {0}'.format(src_file))
    
    with open(os.path.join(out_dir, '.imported_photo.json'), 'w', encoding='utf-8') as importedfile:
        json.dump({'files': copied}, importedfile, ensure_ascii=False, indent=4)