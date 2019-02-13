#!/usr/bin/python

import argparse
import datetime
import exifread
import glob
import json
import os
import subprocess
import time

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import db_metadata
from models.mediafile import MediaFile
from models.mediadir import MediaDir


if __name__ == "__main__":
    parser = argparse.ArgumentParser('''Create SQLite database containing info for all media files (*.jpg; *.jpeg; *.mp4; *.mov)''')
    parser.add_argument('--src-dir', type=str,
                        help='directory containing imported photos, videos and albums metadata files')
    parser.add_argument('--db-file', type=str, 
                        help='path to output database file')
    args = parser.parse_args()

    src_dir = args.src_dir
    db_file = args.db_file

    engine = create_engine("sqlite:///{0}".format(db_file))
    db_metadata.drop_all(bind=engine, tables=[MediaDir.__table__, MediaFile.__table__])
    db_metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        media_dirs = {}
        for basename in os.listdir(src_dir):
            dirpath = os.path.join(src_dir, basename)
            if os.path.isdir(dirpath):
                metadata_file = os.path.join(dirpath, '{0}.json'.format(basename))
                display_name = basename
                is_album = False
                if os.path.isfile(metadata_file):
                    is_album = True
                    with open(metadata_file, encoding='utf-8') as albumdata:
                        display_name = json.load(albumdata)['title']

                dir_entry = MediaDir(basename, display_name, is_album)
                media_dirs[basename] = dir_entry
                session.add(dir_entry)

        session.flush()

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
                        session.add(MediaFile(media_dirs[os.path.basename(os.path.dirname(src_file))].id,
                                                os.path.basename(src_file),
                                                datetime.strptime(str(tag), '%Y:%m:%d %H:%M:%S')))

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

                        session.add(MediaFile(media_dirs[os.path.basename(os.path.dirname(src_file))].id,
                                                os.path.basename(src_file),
                                                dt))

                if not creation_time_found:
                    print('[ERROR] Creation time not found in {0}'.format(src_file))

        session.commit()

    except:
        print('[ERROR] Error while creating database')
        session.rollback()
