#!/usr/bin/python

import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import uuid
import exifread


def process_photo(photo_file):
    with open(photo_file, 'rb') as file:
        try:
            tags = exifread.process_file(file, details=False)
            if 'EXIF DateTimeOriginal' not in tags.keys():
                print("[ERROR] Missing EXIF info. Can't place photo {0} into album {1}".format(photo_file, albumdata['title']))
                return ''

            dt = datetime.datetime.strptime(str(tags['EXIF DateTimeOriginal']).split(' ')[0], '%Y:%m:%d')
            return os.sep.join([dt.strftime('%Y-%m-%d'), os.path.basename(photo_file)])

        except PermissionError:
            print("[ERROR] PermissionError. Can't place photo {0} into album {1}".format(photo_file, albumdata['title']))

    return ''


def process_video(video_file):
    cmnd = ['ffprobe.exe', '-show_streams', '-print_format', 'json', '-loglevel', 'quiet', '{0}'.format(video_file)]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _err = p.communicate()

    info = json.loads(out.decode('utf-8'))
    creation_time_found = False

    for stream in info['streams']:
        if 'tags' not in stream:
            continue

        tags = stream['tags']

        if 'creation_time' in tags:
            creation_time_found = True

            dt = datetime.datetime.strptime(tags['creation_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
            return os.sep.join([dt.strftime('%Y-%m-%d'), os.path.basename(video_file)])

    if not creation_time_found:
        print('[ERROR] Creation time not found in {0}'.format(video_file))

    return ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create <UUID>.json file for each album with title, date and time, list of files, etc. As an input it takes metadata.json that is generated by Google Photos")

    parser.add_argument('--takeout-dir', type=str,
                        help='Google Photos takeout directory')
    parser.add_argument('--out-dir', type=str,
                        help='destination directory')

    args = parser.parse_args()
    out_dir = args.out_dir
    takeout_dir = args.takeout_dir

    for json_file in glob.glob(os.path.join(takeout_dir, '**/metadata.json'), recursive=True):
        album_dir_name = os.path.basename(os.path.dirname(json_file))

        # If '12-7-10' or '12.07.10' or '2012-07-10 -' or '2012-07-10 #2' or '2013-03-22-23'
        # then skip
        if re.match(r'^\d{1,4}(.|-)\d{1,2}(.|-)\d{2}$', album_dir_name) \
                or re.match(r'^\d{1,4}-\d{1,2}-\d{2}\s?-$', album_dir_name) \
                or re.match(r'^\d{1,4}-\d{1,2}-\d{2}-\d{2}$', album_dir_name) \
                or re.match(r'^\d{1,4}-\d{1,2}-\d{2}\s{1}#\d{1}$', album_dir_name):
            continue

        print('Found album directory {0}'.format(album_dir_name))

        with open(json_file, encoding='utf-8') as metadata_file:
            metadata = json.load(metadata_file)

            albumdata = {}
            albumdata['title'] = metadata['title']
            albumdata['date'] = metadata['date']
            albumdata['description'] = metadata['description']
            albumdata['enrichments'] = metadata['enrichments'] if 'enrichments' in metadata else []
            albumdata['files'] = []

            for media_file in glob.glob(os.path.join(os.path.dirname(json_file), '*.*')):
                if media_file.lower().endswith('.jpg') or media_file.lower().endswith('.jpeg'):
                    albumdata['files'].append(process_photo(media_file))
                if media_file.lower().endswith('.mp4') or media_file.lower().endswith('.mov') or media_file.lower().endswith('.mpg'):
                    albumdata['files'].append(process_video(media_file))

            with open(os.path.join(out_dir, str(uuid.uuid4()) + '.json'), 'w', encoding='utf-8') as outfile:
                albumdata['files'] = list(filter(None, albumdata['files']))
                json.dump(albumdata, outfile, ensure_ascii=False, indent=4)
