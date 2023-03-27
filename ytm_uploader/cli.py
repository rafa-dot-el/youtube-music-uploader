#!/usr/bin/env python3

import click
from loguru import logger as log
from typing import Callable
import os
from ytmusicapi import YTMusic


@click.command()
def login():
    log.info("Logging in")
    YTMusic.setup(filepath="headers_auth.json")
    log.info("Done")


@click.command()
@click.option("--filename", help="File or Folder to upload")
@click.option(
    "--auth-file",
    help="Authentication file (headers_auth.json)",
    default="headers_auth.json",
)
@click.option(
    "--track-file", help="File to keep track of uploaded files", default="uploaded"
)
def upload(filename: str, auth_file: str, track_file: str):
    api = YTMusic(auth_file)
    uploaded = read_uploaded(track_file)
    if not api:
        log.error("Authentication problems, check your configuration or run ytm-login")
    else:
        callbacklmb = lambda f: callback(api, f, uploaded, track_file)
        recurse(filename, callbacklmb)
        write_uploaded(track_file, uploaded)


def callback(api: YTMusic, filename: str, uploaded: set[str], track_file: str):
    upload_file(api, filename, uploaded)
    write_uploaded(track_file, uploaded)


def upload_file(api: YTMusic, filename: str, uploaded: set[str]) -> None:
    try:
        if filename in uploaded:
            log.info("Skipping file {}, already uploaded", filename)
        else:
            log.info("Uploading song {}", filename)
            response = api.upload_song(filename)
            log.info("Upload done {} - {}", filename, response)
            uploaded.add(filename)
    except Exception as e:
        log.error("Error uploading file {} - {}", filename, e)


def recurse(
    root: str,
    callback: Callable[[str], None],
    supported_formats=["mp3", "m4a", "wma", "flac", "ogg"],
) -> None:
    if os.path.isfile(root):
        for format in supported_formats:
            # Only upload if the file format is supported
            if root.lower().endswith(format):
                callback(root)
    elif os.path.isdir(root):
        for filename in os.listdir(root):
            file = os.path.join(root, filename)
            recurse(file, callback)


def write_uploaded(filename: str, content: set[str]) -> None:
    try:
        with open(filename, "w") as file:
            file.writelines("\n".join(content))
    except Exception as e:
        log.error("Error writing uploaded file list {}: {}", filename, e)


def read_uploaded(filename: str) -> set[str]:
    result = set()
    try:
        with open(filename, "r") as file:
            file_contents = file.read()
            lines = file_contents.splitlines()
            for line in lines:
                result.add(line)
    except Exception as e:
        log.error("Error opening state file {}: {}", filename, e)
    return result


if __name__ == "__main__":
    cli()
