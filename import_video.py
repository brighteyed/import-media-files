#!/usr/bin/python

import argparse
import datetime
import glob
import json
import os
import shutil
import subprocess
import zipfile


def copy_file(video_file, out_dir):
    """ Copy video file into %Y-%m-%d subfolder of the out_dir """

    cmnd = ['ffprobe.exe', '-show_streams', '-print_format', 'json', '-loglevel', 'quiet', '{0}'.format(video_file)]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _err = p.communicate()
    
    info = json.loads(out.decode('utf-8'))
    creation_time_found = False

    for stream in info['streams']:
        if not 'tags' in stream:
            continue

        tags = stream['tags']

        if 'creation_time' in tags:
            creation_time_found = True

            dt = datetime.datetime.strptime(tags['creation_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
            dst_dir = os.path.join(out_dir, dt.strftime('%Y-%m-%d'))
            
            dst_file = os.path.join(dst_dir, os.path.basename(video_file))
            if os.path.exists(dst_file):
                print('[WARNING] File already exists {0}'.format(dst_file))
                break

            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy(video_file, dst_dir)

            imported.append(os.sep.join(
                [dt.strftime('%Y-%m-%d'), os.path.basename(dst_file)]
                ))

            break

    if not creation_time_found:
        print('[ERROR] Creation time not found in {0}'.format(video_file))


def safe_remove_file(file):
    """ Remove file without exceptions thrown """

    try:
        os.remove(tmp_file)
    except OSError:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import videos into folder')
    parser.add_argument('--src-dir', type=str,
                        help='Directory containing videos (*.mp4; *.mov)')
    parser.add_argument('--out-dir', type=str,
                        help='Destination directory')
    parser.add_argument('--log-file', type=str,
                        help='Output file for imported videos list')

    args = parser.parse_args()
    log_file = args.log_file
    src_dir = args.src_dir
    out_dir = args.out_dir

    tmp_dir = os.path.join(out_dir, '.tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    imported = []

    for video_file in glob.glob(os.path.join(src_dir, '**/*.*'), recursive=True):
        if not video_file.lower().endswith('.mp4') and not video_file.lower().endswith('.mov'):
            continue

        if zipfile.is_zipfile(video_file):
            try:
                tmp_file = os.path.join(tmp_dir, os.path.basename(video_file))

                z = zipfile.ZipFile(video_file)
                name = z.namelist()[0]

                with z.open(name) as source:
                    with open(tmp_file, "wb") as target:
                        shutil.copyfileobj(source, target)

                copy_file(tmp_file, out_dir)

            except zipfile.BadZipFile:
                print("[ERROR] BadZipFile {0}".format(video_file))

            finally:
                safe_remove_file(tmp_file)
        else:
            copy_file(video_file, out_dir)
            
    shutil.rmtree(tmp_dir)

    with open(log_file, 'w', encoding='utf-8') as logfile:
        json.dump({'files': imported}, logfile, ensure_ascii=False, indent=4)