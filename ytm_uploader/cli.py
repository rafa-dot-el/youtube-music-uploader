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
@click.option("--file", help="File or Folder to upload")
def upload(file: str):
    api = YTMusic("headers_auth.json")
    if not api:
        log.error("Authentication problems, check your configuration or run ytm-login")
    else:
        callback = lambda file: upload_file(api, file)
        recurse(file, callback)


def upload_file(api: YTMusic, file: str) -> None:
    try:
        log.info("Uploading song {}", file)
        response = api.upload_song(file)
        log.info("Upload done {} - {}", file, response)
    except Exception as e:
        log.error("Error uploading file {} - {}", file, e)


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


if __name__ == "__main__":
    cli()
