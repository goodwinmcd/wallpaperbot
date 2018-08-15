#!/usr/bin/env python3

import io
import os
from pymongo import MongoClient
from PIL import Image

def connect_to_wallpapers():
    return MongoClient('127.0.0.1').wallpapers.wallpapers

def main():
    wallpaper_dir = '/home/goodwin/Pictures/wallpapers/Wallpapers'
    coll = connect_to_wallpapers()
    wallpapers = os.listdir(wallpaper_dir)

    for wallpaper in wallpapers:
        image = Image.open(os.path.join(
            wallpaper_dir, wallpaper
        ))
        image_obj = {
            'name': wallpaper,
            'size_horizontal': image.size[0],
            'size_vertical': image.size[1],
            'posted': False,
        }
        if not coll.find_one({'name': wallpaper}):
            coll.insert_one(image_obj)


if __name__ == "__main__":
    main()
