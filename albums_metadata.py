#!/usr/bin/python

import argparse
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
import zipfile

import exifread


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create albums description')
    parser.add_argument('--takeout-dir', type=str,
                        help='Directory with files')
    parser.add_argument('--out-dir', type=str,
                        help='Destination directory')

    args = parser.parse_args()
    out_dir = args.out_dir
    takeout_dir = args.takeout_dir

    tmp_dir = os.path.join(out_dir, '.tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    for src_file in glob.glob(os.path.join(takeout_dir, '**/metadata.json'), recursive=True):
        folder = os.path.dirname(src_file)
        
        # Если '12-7-10' или '12.07.10' или '2012-07-10 -' или '2012-07-10 #2' или '2013-03-22-23',
        # то не подходит
        if re.match(r'^\d{1,4}(.|-)\d{1,2}(.|-)\d{2}$', os.path.basename(folder)) \
            or re.match(r'^\d{1,4}-\d{1,2}-\d{2}\s?-$', os.path.basename(folder)) \
            or re.match(r'^\d{1,4}-\d{1,2}-\d{2}-\d{2}$', os.path.basename(folder)) \
            or re.match(r'^\d{1,4}-\d{1,2}-\d{2}\s{1}#\d{1}$', os.path.basename(folder)):
            continue

        print('Found album: {0}'.format(os.path.basename(folder)))

        with open(src_file, encoding='utf-8') as metadata_file:
            metadata = json.load(metadata_file)['albumData']

            albumdata = {}
            albumdata['title'] = metadata['title']
            albumdata['date'] = metadata['date']
            albumdata['files'] = []

            for photo_file in glob.glob(os.path.join(folder, '*.jpg')):
                with open(photo_file, 'rb') as file:
                    try:
                        tags = exifread.process_file(file, details=False)
                        if 'EXIF DateTimeOriginal' not in tags.keys():
                            print('[ERROR] Не могу поместить фото в альбом {0}: no tags in {1}'.format(albumdata['title'], photo_file))
                            continue

                        dt = datetime.datetime.strptime(str(tags['EXIF DateTimeOriginal']).split(' ')[0], '%Y:%m:%d')

                        albumdata['files'].append('{0}/{1}'.format(dt.strftime('%Y-%m-%d'), os.path.basename(photo_file)))

                    except PermissionError:
                        print('[ERROR] Не могу поместить фото в альбом {0}: permission error for {1}'.format(albumdata['title'], photo_file))

            for video_file in glob.glob(os.path.join(folder, '*.mp4')):
                if zipfile.is_zipfile(video_file):
                    z = zipfile.ZipFile(video_file)

                    try:
                        name = z.namelist()[0]
                    
                        tmp_file = os.path.join(tmp_dir, 'extracted_{0}'.format(os.path.basename(name)))
                        target = open(tmp_file, "wb")
                        source = z.open(name)
                        with source, target:
                            shutil.copyfileobj(source, target)

                        cmnd = ['ffprobe.exe', '-show_streams', '-print_format', 'json', '-loglevel', 'quiet', '{0}'.format(tmp_file)]
                        p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        out, err = p.communicate()
                        
                        info = json.loads(out.decode('utf-8'))
                        tags_found = False

                        for stream in info['streams']:
                            if not 'tags' in stream:
                                continue

                            tags = stream['tags']

                            if 'creation_time' in tags:
                                dt = datetime.datetime.strptime(tags['creation_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
                                albumdata['files'].append('{0}/{1}'.format(dt.strftime('%Y-%m-%d'), os.path.basename(video_file)))
                                tags_found = True
                                break

                        if not tags_found:
                            print('[ERROR] No tags found in {0}'.format(video_file))
                        
                        os.remove(tmp_file)
                    
                    except zipfile.BadZipFile:
                        print("[ERROR] Bad zip file {0}".format(video_file))    
                else:
                    print("[ERROR] {0} is not zip archive".format(video_file))

            with open(os.path.join(out_dir, str(uuid.uuid4()) + '.json'), 'w', encoding='utf-8') as outfile:
                json.dump(albumdata, outfile, ensure_ascii=False, indent=4)

    shutil.rmtree(tmp_dir)