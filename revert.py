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
    parser = argparse.ArgumentParser(description='Delete all files')
    parser.add_argument('--files-dir', type=str,
                        help='Directory with photo and video files')

    args = parser.parse_args()
    files_dir = args.files_dir

    for filename in ['.imported_photo.json', '.imported_video.json']:
        with open(os.path.join(files_dir, filename), encoding='utf-8') as import_data_file:
            data = json.load(import_data_file)

            for file in data['files']:
                media_file = os.path.join(files_dir, file)
                
                if not os.path.exists(media_file):
                    print('[WARNING]: Файл {0} отсутствует'.format(media_file))
                    continue

                os.remove(media_file)
        
        os.remove(os.path.join(files_dir, filename))

    for json_file in glob.glob(os.path.join(files_dir, '*.json'), recursive=False):
        os.remove(json_file)
