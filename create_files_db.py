#!/usr/bin/python

import argparse
import datetime
import exifread
import glob
import json
import os
import sqlite3
import subprocess
import time

from datetime import datetime


if __name__ == "__main__":
    parser = argparse.ArgumentParser('''Create SQLite database containing info for all media files (*.jpg; *.jpeg; *.mp4; *.mov)''')
    parser.add_argument('--src-dir', type=str,
                        help='directory containing imported photos, videos and albums metadata files')
    parser.add_argument('--db-file', type=str, 
                        help='path to output database file')
    args = parser.parse_args()

    src_dir = args.src_dir
    db_file = args.db_file

    db = sqlite3.connect(db_file)
    c = db.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS Info (path TEXT PRIMARY KEY, creation_time TIMESTAMP)')

    try:
        for src_file in glob.glob(os.path.join(src_dir, '**/*.*'), recursive=True):
            if src_file.lower().endswith('.jpg') or src_file.lower().endswith('.jpeg'):

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
                        dt = datetime.strptime(str(tag), '%Y:%m:%d %H:%M:%S')
                        c.execute("INSERT INTO Info (path, creation_time) VALUES('{0}', '{1}')".format(
                            os.sep.join([os.path.basename(os.path.dirname(src_file)), os.path.basename(src_file)]), 
                            dt.isoformat()))

                    except ValueError:
                        print('[ERROR] Creation time not found in {0}'.format(src_file))
            
            elif src_file.lower().endswith('.mp4') or src_file.lower().endswith('.mov'):
                
                cmnd = ['ffprobe.exe', '-show_format', '-print_format', 'json', '-loglevel', 'quiet', '{0}'.format(src_file)]
                p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, _err = p.communicate()
                
                info = json.loads(out.decode('utf-8'))
                creation_time_found = False

                if 'format' in info and 'tags' in info['format']:
                    tags = info['format']['tags']
                    if 'creation_time' in tags:
                        creation_time_found = True

                        now_timestamp = time.time()
                        utc_offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
                        dt = datetime.strptime(tags['creation_time'], '%Y-%m-%dT%H:%M:%S.%fZ') + utc_offset

                        c.execute("INSERT INTO Info (path, creation_time) VALUES('{0}', '{1}')".format(
                                    os.sep.join([os.path.basename(os.path.dirname(src_file)), os.path.basename(src_file)]), 
                                    dt.isoformat()))

                if not creation_time_found:
                    print('[ERROR] Creation time not found in {0}'.format(src_file))

        db.commit()

    except:
        print('[ERROR] Error while creating database')
        db.rollback()

    db.close()

