#!/usr/bin/env python3

import praw
import io
import os
import random
from PIL import Image
from imgurpython import ImgurClient
import configparser
from pymongo import MongoClient
import requests
import urllib
import base64
import json
import pyimgur
from pprint import pprint

def get_configs():
    config_parser = configparser.RawConfigParser()
    config_file_path = r'./creds.ini'
    config_parser.read(config_file_path)
    reddit_creds = {
        'client_id'       : config_parser.get('reddit_creds', 'client_id'),
        'client_secret'   : config_parser.get('reddit_creds', 'client_secret'),
        'username'        : config_parser.get('reddit_creds', 'username'),
        'password'        : config_parser.get('reddit_creds', 'password'),
        'user_agent'      : config_parser.get('reddit_creds', 'user_agent'),
    }
    imgur_creds = {
        'client_id'       : config_parser.get('imgur_creds', 'client_id'),
        'client_secret'   : config_parser.get('imgur_creds', 'client_secret'),
        'access_token'    : config_parser.get('imgur_creds', 'access_token'),
        'refresh_token'   : config_parser.get('imgur_creds', 'refresh_token'),
    }
    return reddit_creds, imgur_creds

REDDIT_CREDS, IMGUR_CREDS = get_configs()
WALLPAPER_PATH = './Wallpapers'
IMGUR_POST_IMAGE = 'https://api.imgur.com/3/image'

def upload_image_to_imgur(image, title):
    f = open(os.path.join(WALLPAPER_PATH, image), 'rb')
    image_data = f.read()
    b64_image = base64.standard_b64encode(image_data)
    headers = {'Authorization': f"Bearer {IMGUR_CREDS['access_token']}"}
    #headers = {'Authorization': f"Client-ID {IMGUR_CREDS['client_id']}"}
    print(headers)
    data = {'image': b64_image, 'title': title}
    response = requests.post(url=IMGUR_POST_IMAGE,
                             data=urllib.parse.urlencode(data),
                             headers=headers)
    pprint(response.json())

def connect_to_wallpapers():
    return MongoClient('127.0.0.1').wallpapers.wallpapers

#wallpapers subreddit only allows images with a size greater than
#1024x768
def check_resolution(wallpaper):
    if (wallpaper['size_horizontal'] < 1024 or wallpaper['size_vertical'] < 768):
        return False
    else:
        return True

#Keep selecting random images until it gets one that meets
#resolution requirements
def select_image(dir_path):
    image_file = None
    while not image_file:
        image_file = random.choice(os.listdir(dir_path))
        if not get_resolution(image_file):
            image_file = None
        else:
            return image_file

def main():
    collection = connect_to_wallpapers()

    reddit = praw.Reddit(client_id=REDDIT_CREDS['client_id'],
                         client_secret=REDDIT_CREDS['client_secret'],
                         password=REDDIT_CREDS['password'],
                         username=REDDIT_CREDS['username'],
                         user_agent=REDDIT_CREDS['user_agent'])

    imgur = pyimgur.Imgur(IMGUR_CREDS['client_id'],
                          IMGUR_CREDS['client_secret'],
                          IMGUR_CREDS['access_token'],
                          IMGUR_CREDS['refresh_token'])

    count = collection.count()
    wallpaper = collection.find()[random.randrange(count)]
    while wallpaper['posted'] and check_resolution(wallpaper):
        wallpaper = collection.find()[random.randrange(count)]

    title = f"From my collection [{wallpaper['size_horizontal']}x{wallpaper['size_vertical']}]"

    imgur_post = {
        'name': title,
        'title': title,
    }
    #upload_image_to_imgur(image=wallpaper['name'], title=title)
    uploaded_image = imgur.upload_image(os.path.join(WALLPAPER_PATH, wallpaper['name']),
                                     title="Uploaded with PyImgur")
    pprint(uploaded_image.link)
    # image_url = imgur_client.upload_from_path(os.path.join(wallpaper_path, wallpaper['name']),
    #                                           config=imgur_post,
    #                                           anon=False)
    # print(image_url)

    wallpapers_subreddit = reddit.subreddit('wallpapers')
    wallpapers_subreddit.submit(title=title,
                                url=uploaded_image.link,
                                send_replies=True)
    wallpaper['posted'] = True
    collection.update_one({'_id': wallpaper['_id']}, {'$set': wallpaper})
    print(wallpaper)

if __name__ == "__main__":
    main()
