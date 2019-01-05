#!/usr/bin/python

import argparse
import datetime
import glob
import json
import os
import re
import shutil
import sys
import uuid

import exifread


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create albums')
    parser.add_argument('--files-dir', type=str,
                        help='Directory photo and video files')
    parser.add_argument('--metadata-dir', type=str,
                        help='Directory albums metadata')
    parser.add_argument('--out-dir', type=str,
                        help='Destination directory for albums')

    args = parser.parse_args()
    metadata_dir = args.metadata_dir
    out_dir = args.out_dir
    files_dir = args.files_dir

    for album_file in glob.glob(os.path.join(metadata_dir, '*.json'), recursive=False):
        album_name = os.path.basename(os.path.splitext(album_file)[0])
        os.makedirs(os.path.join(out_dir, album_name), exist_ok=True)

        with open(album_file, encoding='utf-8') as albumdata_file:
            albumdata = json.load(albumdata_file)

            print('[INFO] Creating album {0}'.format(albumdata['title']))
            for file in albumdata['files']:
                media_file = os.path.join(files_dir, file)
                
                if not os.path.exists(media_file):
                    print('[ERROR]: Не могу поместить фото в альбом. Файл {0} отсутствует'.format(media_file))
                    continue

                shutil.copy(media_file, os.path.join(out_dir, album_name))

            shutil.copy(album_file, os.path.join(out_dir, album_name))
