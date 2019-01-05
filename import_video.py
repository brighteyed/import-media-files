#!/usr/bin/python

import argparse
import datetime
import glob
import json
import os
import shutil
import subprocess
import zipfile

import exifread


def process_file(sourcefile, tempfile, out_dir):
    """ Copy video file into %Y-%m-%d subfolder in the out_dir """

    cmnd = ['ffprobe.exe', '-show_streams', '-print_format', 'json', '-loglevel', 'quiet', '{0}'.format(tempfile)]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _err = p.communicate()
    
    info = json.loads(out.decode('utf-8'))
    tags_found = False

    for stream in info['streams']:
        if not 'tags' in stream:
            continue

        tags = stream['tags']

        if 'creation_time' in tags:
            dt = datetime.datetime.strptime(tags['creation_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
            dir = os.path.join(out_dir, dt.strftime('%Y-%m-%d'))
            os.makedirs(dir, exist_ok=True)

            tags_found = True

            dst_file = os.path.join(dir, os.path.basename(sourcefile))
            if os.path.exists(dst_file):
                print('[WARNING] File already exists {0}'.format(dst_file))
                break

            copied.append(os.sep.join(os.path.normpath(dst_file).split(os.sep)[-2:]))
            print('{0} -> {1}'.format(sourcefile, dst_file))
            shutil.copy(sourcefile, dir)
            break

    if not tags_found:
        print('[ERROR] No tags found in {0}'.format(video_file))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import video files')
    parser.add_argument('--takeout-dir', type=str,
                        help='Directory with videos')
    parser.add_argument('--out-dir', type=str,
                        help='Destination directory')

    args = parser.parse_args()

    takeout_dir = args.takeout_dir
    out_dir = args.out_dir

    tmp_dir = os.path.join(out_dir, '.tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    copied = []

    for video_file in glob.glob(os.path.join(takeout_dir, '**/*.mp4'), recursive=True):
        if zipfile.is_zipfile(video_file):
            try:
                z = zipfile.ZipFile(video_file)
                name = z.namelist()[0]
            
                tmp_file = os.path.join(tmp_dir, 'extracted_{0}'.format(os.path.basename(video_file)))
                with z.open(name) as source:
                    with open(tmp_file, "wb") as target:
                        shutil.copyfileobj(source, target)

                process_file(video_file, tmp_file, out_dir)

            except zipfile.BadZipFile:
                print("[ERROR] Bad zip file {0}".format(video_file))

            finally:
                try:
                    os.remove(tmp_file)
                except OSError:
                    pass
        else:
            process_file(video_file, video_file, out_dir)
            
    shutil.rmtree(tmp_dir)

    with open(os.path.join(out_dir, '.imported_video.json'), 'w', encoding='utf-8') as importedfile:
        json.dump({'files': copied}, importedfile, ensure_ascii=False, indent=4)