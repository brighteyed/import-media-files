#!/usr/bin/python

import argparse
import glob
import json
import os
import shutil


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description= \
        '''Copy media files into folders (one folder per album) according to album
        descriptions provided in <UUID>.json files''')
        
    parser.add_argument('--src-dir', type=str,
                        help='directory containing imported photos, videos and albums metadata files')
    parser.add_argument('--out-dir', type=str,
                        help='destination directory for albums')

    args = parser.parse_args()
    out_dir = args.out_dir
    src_dir = args.src_dir

    for album_file in glob.glob(os.path.join(src_dir, '*.json'), recursive=False):
        album_dir_name = os.path.basename(os.path.splitext(album_file)[0])

        with open(album_file, encoding='utf-8') as albumdata_file:
            albumdata = json.load(albumdata_file)
            if not albumdata['files']:
                print("[INFO] Album {0} is empty and therefore will not be created".format(albumdata['title']))
                continue

            album_dir_path = os.path.join(out_dir, album_dir_name)
            os.makedirs(album_dir_path, exist_ok=True)

            print('[INFO] Creating album {0}'.format(albumdata['title']))
            shutil.copy(album_file, album_dir_path)

            for file in albumdata['files']:
                media_file = os.path.join(src_dir, file)
                
                if not os.path.exists(media_file):
                    print("[ERROR] Can't place photo {0} into album. File not found".format(media_file))
                    continue

                shutil.copy(media_file, album_dir_path)
