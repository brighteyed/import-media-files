#!/usr/bin/python

import argparse
import os

from flask import Flask
from flask import abort, render_template, request, send_file, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', 
        folders=[dir for dir in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, dir))])

@app.route('/view/<dirname>')
def viewdir(dirname):
    return render_template('viewdir.html', 
        images=[file for file in os.listdir(os.sep.join([ROOT_DIR, dirname])) if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg')],
        dir=dirname)

@app.route('/<folder>/<file>')
def getfile(folder, file):
    thumb = request.args.get('thumb', 0, type=int)
    if thumb == 1:
        return send_file(os.sep.join([THUMBS_ROOT_DIR, folder, file]), mimetype='image/jpg')

    return send_file(os.sep.join([ROOT_DIR, folder, file]), mimetype='image/jpg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description= \
        '''Simple image gallery server''')
        
    parser.add_argument('--thumbnails-dir', type=str, required=True, help='destination containing thumbnails')
    parser.add_argument('--media-dir', type=str, required=True, help='directory containing images')

    args = parser.parse_args()
    THUMBS_ROOT_DIR = args.thumbnails_dir
    ROOT_DIR = args.media_dir

    app.run()