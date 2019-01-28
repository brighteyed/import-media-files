#!/usr/bin/python

import argparse
import json
import os

from flask import Flask
from flask import abort, render_template, request, send_file, url_for


app = Flask(__name__)

def is_image_file(filename):
    return filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg')

def is_video_file(filename):
    return filename.lower().endswith('.mp4') or filename.lower().endswith('.mov')

app.jinja_env.globals.update(is_video_file=is_video_file)

@app.route('/')
def index():
    dirs=[]
    for dir in os.listdir(ROOT_DIR):
        dirpath = os.path.join(ROOT_DIR, dir)
        if os.path.isdir(dirpath):
            metadata_file = os.path.join(dirpath, '{0}.json'.format(dir))
            title = dir
            if os.path.isfile(metadata_file):
                with open(metadata_file, encoding='utf-8') as albumdata:
                    title = json.load(albumdata)['title']

            dirs.append((dir, title))

    return render_template('index.html', folders=sorted(dirs, key=lambda tup: tup[1]))

@app.route('/<dirname>')
def viewdir(dirname):
    return render_template('viewdir.html', 
        media_files=[file for file in os.listdir(os.sep.join([ROOT_DIR, dirname])) if is_image_file(file) or is_video_file(file)],
        dir=dirname)

@app.route('/<folder>/<file>')
def getfile(folder, file):
    thumb = request.args.get('thumb', 0, type=int)
    if thumb == 1:
        return send_file(os.sep.join([THUMBS_ROOT_DIR, folder, '{0}.jpg'.format(os.path.splitext(file)[0])]), mimetype='image/jpg')

    return send_file(os.sep.join([ROOT_DIR, folder, file]), mimetype='video/mp4' if is_video_file(file) else 'image/jpg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description= \
        '''Micro media gallery server''')
        
    parser.add_argument('--thumbnails-dir', type=str, required=True, help='destination containing thumbnails')
    parser.add_argument('--media-dir', type=str, required=True, help='directory containing media files (*.jpg; *.jpeg; *.mp4; *.mov')

    args = parser.parse_args()
    ROOT_DIR = args.media_dir
    THUMBS_ROOT_DIR = args.thumbnails_dir

    app.run()