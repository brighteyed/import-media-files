#!/usr/bin/python

import argparse
import json
import os
import requests


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Create albums in Immich by their metadata")

    parser.add_argument('--metadata-dir', type=str,
                        help='path to directory with album description metadata files')
    parser.add_argument('--immich-url', type=str,
                        help='Immich server URL')
    parser.add_argument('--api-key', type=str,
                        help='Immich API key')

    args = parser.parse_args()

    immich_url = args.immich_url
    api_key = args.api_key

    # Мap originalPath of all the assets to assetId
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
        
    # Get all existing albums
    response = requests.request("GET", f"{immich_url}api/album",
                            headers={
                                'Accept': 'application/json',
                                "x-api-key": api_key
                            },
                            data={})
    
    albums = {}
    for album in response.json():
        albums[album["albumName"]] = album["id"]

    # Enumerate albums metadata files in the directory
    metadata_files = []
    for file in os.listdir(args.metadata_dir):
        if file.endswith(".json"):
            metadata_files.append(os.path.join(args.metadata_dir, file))

    # For each metadata file create album in Immich
    for metadata_file in metadata_files:
        with open(metadata_file, encoding='utf-8') as metadata_file:
            data = json.load(metadata_file)
            if not data['files']:
                print("[INFO] Metadata file is empty")
                continue

            # Check if album already exists
            album_id = None 
            if data['title'] in albums.keys():
                album_id = albums[data['title']]
            else:
                # Create new album
                response = requests.request("POST", f"{immich_url}api/album",
                                            headers={
                                                'Content-Type': 'application/json',
                                                'Accept': 'applicationa/json',
                                                "x-api-key": api_key
                                            },
                                            data=json.dumps({
                                                "albumName": data['title'],
                                                "description": data['description']
                                            }))
                if response.status_code != 201:
                    print(
                        f"[ERROR] Can't create album {data['title']}. Status code: {response.status_code}")
                    continue

                album_id = response.json()['id']

            # Collect asset ids
            asset_ids = []
            for file in data['files']:
                file_path, file_extension = os.path.splitext(file)
                file = file_path + file_extension.lower()
                
                if file in assets.keys():
                    asset_ids.append(assets[file])
                else:
                    print(f"[ERROR] Can't add {file} to album {data['title']}. File not found on Immich server")

            # Add assets to album
            response = requests.request("PUT", f"{immich_url}api/album/{album_id}/assets",
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Accept': 'application/json',
                                            "x-api-key": api_key
                                        },
                                        data=json.dumps({"ids": asset_ids}))
            if response.status_code != 200:
                print(
                    f"[ERROR] Can't add assets to album {data['title']}. Status code: {response.status_code}")
