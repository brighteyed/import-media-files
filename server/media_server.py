#!/usr/bin/python

import argparse
import json
import os

from flask import Flask
from flask import render_template, request, send_file, url_for
from flask_sqlalchemy import SQLAlchemy

from models.mediadir import MediaDir
from models.mediafile import MediaFile


app = Flask(__name__)

def is_image_file(filename):
    return filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg')

def is_video_file(filename):
    return filename.lower().endswith('.mp4') or filename.lower().endswith('.mov')

app.jinja_env.globals.update(is_video_file=is_video_file)

@app.route('/')
def index():
    dirs = [(entry.folder_basename, entry.display_name) for entry in db.session.query(MediaDir).order_by(MediaDir.display_name)]
    
    return render_template('index.html', folders=dirs)

@app.route('/<dirname>')
def viewdir(dirname):
    media_dir = db.session.query(MediaDir).filter_by(folder_basename=dirname).first()

    return render_template('viewdir.html', media_files=[] if not media_dir else [f.filename for f in media_dir.media_files], dir=dirname)

@app.route('/<folder>/<file>')
def getfile(folder, file):
    thumb = request.args.get('thumb', 0, type=int)
    if thumb == 1:
        return send_file(os.sep.join([THUMBNAILS_DIR, folder, '{0}.jpg'.format(os.path.splitext(file)[0])]), mimetype='image/jpg')

    return send_file(os.sep.join([ROOT_DIR, folder, file]), mimetype='video/mp4' if is_video_file(file) else 'image/jpg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description= \
        '''Micro media gallery server''')
        
    parser.add_argument('--thumbnails-dir', type=str, required=True, help='destination containing thumbnails')
    parser.add_argument('--media-dir', type=str, required=True, help='directory containing media files (*.jpg; *.jpeg; *.mp4; *.mov')
    parser.add_argument('--db-file', type=str, required=True, help='path to media info database file')

    args = parser.parse_args()
    ROOT_DIR = args.media_dir
    THUMBNAILS_DIR = args.thumbnails_dir

    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{0}".format(args.db_file)
    db = SQLAlchemy(app)

    app.run()
