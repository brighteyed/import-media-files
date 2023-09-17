#!/usr/bin/python

import argparse
import json
import requests


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Mark files as archived in Immich")

    parser.add_argument('--metadata', type=str,
                        help='path to archive metadata file (same format as json for album description)')
    parser.add_argument('--immich-url', type=str,
                        help='Immich server URL')
    parser.add_argument('--api-key', type=str,
                        help='Immich API key')

    args = parser.parse_args()

    immich_url = args.immich_url
    api_key = args.api_key

    with open(args.metadata, encoding='utf-8') as metadata_file:
        data = json.load(metadata_file)
        if not data['files']:
            print("[INFO] Archive metadata file is empty")
            exit(0)

        response = requests.request("GET", f"{immich_url}api/asset",
                                    headers={
                                        'Accept': 'application/json',
                                        "x-api-key": api_key
                                    },
                                    data={})

        assets = {}
        for asset in response.json():
            assets["\\".join(asset["originalPath"].split("/")
                             [-2:])] = asset["id"]

        for file in data['files']:
            if file in assets.keys():
                response = requests.request("PUT", f"{immich_url}api/asset/{assets[file]}",
                                            headers={
                                                'Content-Type': 'application/json',
                                                'Accept': 'application/json',
                                                "x-api-key": api_key
                                            },
                                            data=json.dumps({
                                                "isArchived": True
                                            }))
                if response.status_code != 200:
                    print(
                        f"[ERROR] Can't archive {file}. Status code: {response.status_code}")
            else:
                print(f"[ERROR] Can't archive {file}. File not found")
