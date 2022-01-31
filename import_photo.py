#!/usr/bin/python

import argparse
import datetime
import glob
import json
import os
import shutil
import exifread

from utils import files

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Import photos (*.jpg; *.jpeg) into specified folder organizing them according to EXIF DateTimeOriginal tag")

    parser.add_argument('--src-dir', type=str,
                        help='directory containing photos (*.jpg; *.jpeg)')
    parser.add_argument('--out-dir', type=str,
                        help='destination directory')
    parser.add_argument('--log-file', type=str,
                        help='output file for imported photos list')

    args = parser.parse_args()
    log_file = args.log_file
    out_dir = args.out_dir
    src_dir = args.src_dir

    imported = []

    for src_file in glob.glob(os.path.join(src_dir, '**/*.*'), recursive=True):
        if not src_file.lower().endswith('.jpg') and not src_file.lower().endswith('.jpeg'):
            continue

        try:
            with open(src_file, 'rb') as file:
                tags = exifread.process_file(file, details=False)

                tag = None
                if 'EXIF DateTimeOriginal' in tags.keys():
                    tag = tags['EXIF DateTimeOriginal']
                elif 'EXIF DateTimeDigitized' in tags.keys():
                    tag = tags['EXIF DateTimeDigitized']

                if not tag:
                    print('[ERROR] Creation time not found in {0}'.format(src_file))
                    continue

                try:
                    dt = datetime.datetime.strptime(str(tag).split(' ')[0], '%Y:%m:%d')
                    dst_dir = os.path.join(out_dir, dt.strftime('%Y-%m-%d'))
                    os.makedirs(dst_dir, exist_ok=True)

                    dst_file = os.path.join(dst_dir, os.path.basename(src_file))
                    if os.path.exists(dst_file):
                        if files.equal(src_file, dst_file):
                            continue
                        if os.path.getsize(src_file) < os.path.getsize(dst_file):
                            continue

                    shutil.copy(src_file, dst_dir)

                    imported.append(os.sep.join(
                        [dt.strftime('%Y-%m-%d'), os.path.basename(dst_file)]))

                except ValueError:
                    print('[ERROR] ValueError {0}'.format(src_file))

        except PermissionError:
            print('[ERROR] PermissionError {0}'.format(src_file))

    with open(log_file, 'w', encoding='utf-8') as logfile:
        json.dump({'files': imported}, logfile, ensure_ascii=False, indent=4)
