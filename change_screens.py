#!/usr/bin/python
import argparse
import os
import random
import subprocess
from urllib.request import urlopen, Request
from urllib.error import URLError
import json
import sys
from uuid import uuid4
import mimetypes

HOME_DIR = os.environ.get('HOME')
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PLATFORM = sys.platform


def config_loader(file: str) -> dict:
    try:
        with open(file, 'rb') as load_config:
            return json.load(load_config)
    except FileNotFoundError or OSError as e:
        raise e


config = config_loader(os.path.join(BASE_DIR, 'config.json'))
oses = config_loader(os.path.join(BASE_DIR, 'oses.json'))
default_wallpaper_dir = os.path.sep.join(map(str.strip,
                                             config.get('default_wallpapers_dir')
                                             .replace('%home_dir%'.lower(), HOME_DIR)
                                             .replace('%_%', ' ').split('%sep%'.lower())))

try:
    commands = oses[PLATFORM]
    de = os.environ.get('DESKTOP_SESSION')
    if PLATFORM == 'linux':
        commands = commands[de]
except KeyError:
    raise NotImplementedError(f'{PLATFORM} not supported.')


def get_images(dir_path: str):
    for root, dirs, files in os.walk(dir_path):
        return filter(lambda path: path.split('.')[-1] == 'jpg' or 'png' or 'jpeg' or 'bmp',
                      map(lambda path: os.path.join(root, path), files))
    return images


def check_query():
    arguments = sys.argv
    try:
        query_index = arguments.index('--query')
    except ValueError:
        try:
            query_index = arguments.index('-q')
        except ValueError:
            return None
    config.update({'query': arguments[query_index + 1]})


def download_images(resource_url: []):
    retrieve_path = os.path.join(default_wallpaper_dir, 'remote_retrieve')

    def save_image(resource):
        try:
            req = Request(headers=config['headers'], url=resource)
            print(f'Downloading image from {resource}.')
            with urlopen(req) as response:
                if response.status == 200:
                    content = response.read()
                    get_filename = response.info().get_filename()
                    mime_type = response.info().get_content_type()
                    extension = mimetypes.guess_extension(mime_type) if not None else ''
                    filename = get_filename if get_filename else uuid4().hex + extension
                    save_path = os.path.join(retrieve_path, filename)
                    print(f'Writing image as {filename}.')
                    with open(save_path, 'wb') as file_handler:
                        file_handler.write(content)
                        print(f'Wrote image to {retrieve_path}.')
                    return save_path
        except URLError:
            print(f'Failed to get file from {resource}.')
            return None

    try:
        os.makedirs(retrieve_path)
        print(f'Directory created in {retrieve_path}, selected...')
    except FileExistsError:
        print(f'Directory exists {retrieve_path}, selected...')
    files = []
    for url in resource_url:
        files.append(save_image(url))
    return files


def get_photos_link(photos, keys):
    if not keys:
        return photos
    keys.reverse()
    key = keys.pop()
    try:
        photos = photos[key]
    except TypeError:
        keys = key
        keys.reverse()
        key = keys.pop()
        photos = [photo[key] for photo in photos]
    return get_photos_link(photos, keys)


def query_string_validator(url_path: str) -> str:
    return '?' if '?' not in url_path.split('=')[0] else '&'


def request_remote_pictures(site: str):
    screen_height, screen_width = list(map(int, config['resolution'].split('x')))
    site = config['remotes'][site]
    config['headers'].update(site.get('headers'))
    default_query = config.get('default_query')
    search_query = config.get('query', default_query if default_query else '')
    url_path = f"{site.get('query')}{search_query}" if search_query else site.get('curated')
    result = f"{query_string_validator(url_path)}{site.get('count')}{site.get('default_result')}"
    url = site.get('endpoint') + url_path + result
    req = Request(url=url, headers=config['headers'])
    try:
        with urlopen(req) as response:
            load_responses = json.loads(response.read().decode('UTF-8'))
            # filter_with_screen_size = filter(lambda photo: photo['width'] >= screen_width
            # and photo['height'] >= screen_height, load_responses)
            return True, get_photos_link(load_responses, site.get('extract_keys'))
    except URLError:
        return None


def check_image(string: str):
    if os.path.isdir(string):
        local_images = list(get_images(string))
        if not local_images:
            raise argparse.ArgumentTypeError(f'No images found on {string} dir.')
        return False, local_images
    remote_endpoints = config['remotes'].keys()
    if string not in remote_endpoints:
        raise argparse.ArgumentTypeError(f'Please choose one of the remote api, {", ".join(remote_endpoints)}')
    images_urls = request_remote_pictures(string)
    if not images_urls:
        raise argparse.ArgumentTypeError(f'Failed to get image from the {string}')
    return images_urls


def get_random(iterable, length=2):
    pictures = random.sample(tuple(iterable), k=length)
    return pictures[:2]


def set_screen(image: [str]) -> None:
    for i, screen in enumerate(screen_types):
        command = commands.get(screen)
        if not command:
            raise NotImplementedError(f'Commands for {screen} is not defined.')
        print(f'Changing {screen} image.')
        try:
            command[command.index('%image%'.lower())] = image[i]
        except ValueError:
            print(f'Bad configuration for {screen} command.')
            continue
        process = subprocess.run(command,
                                 stderr=subprocess.PIPE, encoding='utf-8')
        exit_code = process.returncode
        if process.returncode == 0:
            print(f'Changed {screen} image successfully.')
            return None
        print(f'Failed to set {screen} image.')
        print(f'Command exited with exit code {exit_code}: %s' % process.stderr.split("\n")[0])


parser = argparse.ArgumentParser(description='Simple screen image changer.', prog='auto_wall')
parser.add_argument('--query', '-q', help='Remote api')
parser.add_argument('--image', '-i', action='store', type=check_image, default=default_wallpaper_dir,
                    help="get random images from.")

parser.add_argument('--no-wall', '-w', action='append_const', dest='screen_types', const='background',
                    help='Do not change wallpaper.')
parser.add_argument('--no-lock-screen', '-s', action='append_const', dest='screen_types', const='screensaver',
                    help='Do not change wallpaper.')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')

check_query()
args = parser.parse_args()
available_screens = ['background', 'screensaver']
query, images, screens = args.__dict__.values()
screen_types = list(filter(lambda screen: screen not in screens if screens else available_screens, available_screens))
is_remote, list_images = images

if not screen_types:
    print('There are no screen to set, at least one screen is required.')
    exit(1)

total_images, total_screens = len(list_images), len(screen_types)

if not total_images >= total_screens:
    message = f'Not sufficient result{f" with {query}" if query else ""} for {"and ".join(screen_types)}'
    print(message)
    print(f'Got {total_images} image{"s" if total_images > 1 else ""} \
    for {total_screens} screen{"s" if total_screens > 1 else ""}.')

received_images = download_images(get_random(list_images, total_screens)) if is_remote else list_images
randomized_images = get_random(received_images, total_screens)

set_screen(randomized_images)
