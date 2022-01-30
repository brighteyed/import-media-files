#!/usr/bin/python

import argparse
import json
import os


def removeEmptyFolders(path, removeRoot=True):
    """ Recursively remove empty folders """

    if not os.path.isdir(path):
        return

    entries = os.listdir(path)
    for entry in entries:
        fullpath = os.path.join(path, entry)
        if os.path.isdir(fullpath):
            removeEmptyFolders(fullpath)

    if len(entries) == 0 and removeRoot:
        os.rmdir(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Delete previously imported files. It uses log files that was generated while importing")

    parser.add_argument('--files-dir', type=str,
                        help='directory with photo and video files')
    parser.add_argument('--log-files', type=str, nargs='+',
                        help='log files that were generated during import')

    args = parser.parse_args()
    files_dir = args.files_dir
    log_files = args.log_files

    for filename in log_files:
        with open(os.path.join(files_dir, filename), encoding='utf-8') as import_data_file:
            data = json.load(import_data_file)

            for file in data['files']:
                media_file = os.path.join(files_dir, file)

                if not os.path.exists(media_file):
                    print('[WARNING]: File not found {0}'.format(media_file))
                    continue

                os.remove(media_file)

    removeEmptyFolders(files_dir, False)
