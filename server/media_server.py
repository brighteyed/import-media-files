#!/usr/bin/python

import argparse
import json
import os

from flask import session, render_template, request, send_file, url_for

from models.mediadir import MediaDir
from models.mediafile import MediaFile
from utils import file_utils
from app import app, app_db


@app.route('/')
def index():
    """ List all directories with pagination support """

    is_albums_mode = request.args.get('albums', False, type=bool)
    session['is_albums_mode'] = is_albums_mode

    media_dirs_query = app_db.session.query(MediaDir).filter_by(is_album=is_albums_mode).order_by(MediaDir.display_name)
    media_dirs = media_dirs_query.paginate(request.args.get('page', 1, type=int), DIRS_PER_PAGE, False)
    next_url = url_for('index', page=media_dirs.next_num, albums=1 if is_albums_mode else None) if media_dirs.has_next else None
    prev_url = url_for('index', page=media_dirs.prev_num, albums=1 if is_albums_mode else None) if media_dirs.has_prev else None

    return render_template('index.html', 
                folders=[(entry.folder_basename, entry.display_name) for entry in media_dirs.items],
                next_url=next_url,
                prev_url=prev_url,
                is_albums_mode=is_albums_mode)

@app.route('/<dirname>')
def viewdir(dirname):
    """ List all files in directory with pagination support """

    media_dir = app_db.session.query(MediaDir).filter_by(folder_basename=dirname).first()
    media_files = media_dir.media_files.paginate(request.args.get('page', 1, type=int), FILES_PER_PAGE, False)
    next_url = url_for('viewdir', dirname=dirname, page=media_files.next_num) if media_files.has_next else None
    prev_url = url_for('viewdir', dirname=dirname, page=media_files.prev_num) if media_files.has_prev else None

    return render_template('viewdir.html', 
                    media_files=[f.filename for f in media_files.items],
                    dir=dirname,
                    next_url=next_url,
                    prev_url=prev_url)

@app.route('/<folder>/<file>')
def getfile(folder, file):
    thumb = request.args.get('thumb', 0, type=int)
    if thumb == 1:
        return send_file(os.sep.join([THUMBNAILS_DIR, folder, '{0}.jpg'.format(os.path.splitext(file)[0])]), mimetype='image/jpg')

    is_albums_mode = session.get('is_albums_mode', False)
    return send_file(os.sep.join([ROOT_DIR if not is_albums_mode else ALBUMS_DIR, folder, file]), mimetype='video/mp4' if file_utils.is_video_file(file) else 'image/jpg')

@app.route('/favicon.ico')
def favicon():
    return ""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description= \
        '''Micro media gallery server''')
        
    parser.add_argument('--thumbnails-dir', type=str, required=True, help='destination containing thumbnails')
    parser.add_argument('--media-dir', type=str, required=True, help='directory containing media files (*.jpg; *.jpeg; *.mp4; *.mov')
    parser.add_argument('--albums-dir', type=str, required=True, help='directory containing albums')
    parser.add_argument('--db-file', type=str, required=True, help='path to media info database file')
    args = parser.parse_args()

    THUMBNAILS_DIR = args.thumbnails_dir
    ALBUMS_DIR = args.albums_dir
    ROOT_DIR = args.media_dir

    FILES_PER_PAGE=30
    DIRS_PER_PAGE=40

    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{0}".format(args.db_file)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'for-debug-only'
    app_db.init_app(app)

    app.run()
