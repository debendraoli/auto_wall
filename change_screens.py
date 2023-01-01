#!/usr/bin/python
from argparse import ArgumentTypeError, ArgumentParser
from json import load, loads
import mimetypes
from os import environ, path, walk, makedirs
import random
import subprocess
from sys import platform
from urllib.error import URLError
from urllib.request import Request, urlopen
from uuid import uuid4
from difflib import get_close_matches

HOME_DIR = environ.get("HOME")
BASE_DIR = path.dirname(path.realpath(__file__))
PLATFORM = platform


def config_loader(file: str) -> dict:
    try:
        with open(file, "rb") as load_config:
            return load(load_config)
    except FileNotFoundError:
        print(f'Failed to read config file.')


config = config_loader(path.join(BASE_DIR, "config.json"))
oses = config_loader(path.join(BASE_DIR, "oses.json"))
wallpaper_dir = config.get("wallpaper_dir").replace("%home%".lower(), HOME_DIR).strip()
try:
    commands = oses[PLATFORM]
    session = environ.get("DESKTOP_SESSION") if environ.get("DESKTOP_SESSION") else environ.get("XDG_CURRENT_DESKTOP")
    if PLATFORM == "linux":
        commands = commands[session]
    elif PLATFORM == "darwin":
        pass
except KeyError:
    print(f"{PLATFORM} not supported.")


def get_images(dir_path: str) -> list[str]:
    extensions = ["jpg", "png", "jpeg", "bmp"]
    for root, dirs, files in walk(dir_path):
        return filter(lambda p: p.split(".")[-1] in extensions, map(lambda p: path.join(root, p), files))
    return images


def check_query(string: str) -> str:
    query = string or config.get("default_query")
    config.update({"query": query})
    return query


def save_image(resource: str, retrieve_path: str) -> str or None:
    try:
        print(f"Downloading image from {resource}.")
        req = Request(headers=config["headers"], url=resource)
        with urlopen(req) as response:
            if response.status == 200:
                content = response.read()
                get_filename = response.info().get_filename()
                mime_type = response.info().get_content_type()
                extension = mimetypes.guess_extension(mime_type) if not None else ""
                filename = get_filename if get_filename else f"{uuid4().hex}{extension}"
                save_path = path.join(retrieve_path, filename)
                print(f"Writing image as {filename} to {save_path}.")
                with open(save_path, "wb") as f:
                    f.write(content)
                    print(f"Wrote image to {retrieve_path}.")
                return save_path
    except URLError:
        print(f"Failed to get file from {resource}.")
        return None


def download_images(resource_urls: list[str]) -> list[str]:
    dest_path = path.join(wallpaper_dir, "remote_retrieve")
    try:
        makedirs(dest_path)
        print(f'Directory created in {dest_path}, selected...')
    except FileExistsError:
        print(f"Directory exists {dest_path}, selected...")
    return [save_image(url, dest_path) for url in resource_urls]


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
    return "?" if "?" not in url_path.split("=")[0] else "&"


def request_remote_pictures(site: str) -> tuple[bool, list[str]] or None:
    screen_height, screen_width = list(map(int, config["resolution"].split("x")))
    site = config["remotes"][site]
    config["headers"].update(site.get("headers", {}))
    search_query = config.get("query")
    url_path = f"{site.get('query')}={search_query}" if search_query else site.get("curated")
    result = f"{query_string_validator(url_path)}{site.get('count')}={site.get('default_result')}"
    url = f"{site.get('endpoint')}{url_path}{result}"
    try:
        req = Request(url=url, headers=config["headers"])
        with urlopen(req) as response:
            load_responses = loads(response.read().decode("UTF-8"))
            return True, get_photos_link(load_responses, site.get("extract_keys"))
    except URLError:
        return None


def check_image(string: str):
    if path.isdir(string):
        local_images = list(get_images(string))
        if not local_images:
            raise ArgumentTypeError(f"No images found on {string} dir.")
        return False, get_close_matches(config.get("query"), local_images)
    remote_endpoints = config["remotes"].keys()
    if string not in remote_endpoints:
        raise ArgumentTypeError(f'Please choose one of the remote api: {", ".join(remote_endpoints)}')
    images_urls = request_remote_pictures(string)
    if not images_urls:
        raise ArgumentTypeError(f"Failed to get image from the {string}")
    return True, images_urls


def get_random(iterable, length=2) -> list[str]:
    pictures = random.sample(tuple(iterable), k=length)
    return pictures[:2]


def set_screen(image: list[str], screens: list[str]) -> None:
    for i, screen in enumerate(screens):
        command = commands.get(screen)
        if not command:
            print(f"Commands for {screen} is not defined.")
            exit(1)
        print(f"Changing {screen} image.")
        try:
            command[command.index("%image%".lower())] = image[i]
        except ValueError:
            print(f"Bad configuration for {screen} command.")
            exit(1)
        process = subprocess.run(command, stderr=subprocess.PIPE, encoding="utf-8")
        exit_code = process.returncode
        if process.returncode == 0:
            print(f"Changed {screen} image successfully.")
            exit()
        print(f"Failed to set {screen} image.")
        print(f"Command exited with exit code {exit_code}: %s" % process.stderr.split("\n")[0])


default_screens = ["background", "screensaver"]
parser = ArgumentParser(description="Simple screen image changer", prog="auto_wall", conflict_handler='resolve')
parser.add_argument("--query", "-q", help="Search against.", type=check_query)
parser.add_argument("--src", "-s", action="store", type=check_image, default=wallpaper_dir, help="Path or remotes.")
parser.add_argument("--screens", choices=default_screens, default=default_screens, nargs='+', help="Screen selections.")
parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0")

args = parser.parse_args()
query, images, screens = args.__dict__.values()
is_remote, list_images = images
received_images = download_images(get_random(list_images, len(screens))) if is_remote else list_images
randomized_images = get_random(received_images, len(screens))
set_screen(randomized_images, screens)
