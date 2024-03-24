#!/bin/env python3

import json
from pathlib import Path

import sys

GITHUB_PREFIX="github:leaphy-robotics/leaphy-micropython/leaphymicropython"

def check_package_json() -> bool:
    """ Validate paths in the package.json file """
    with open('package.json', "r", encoding="utf8") as package_file:
        package = json.load(package_file)
        for url in package["urls"]:
            if not Path(url[0]).exists():
                print(f"Package URL {url[0]}: ❌ does not exist!")
                return False
            if not url[1].startswith(GITHUB_PREFIX):
                print(f"Package Source {url[1]}: ❌ should start with {GITHUB_PREFIX}")
                return False

            print(f"Package URL {url[0]}: 👍")
    return True


if __name__ == "__main__":
    if not check_package_json():
        sys.exit(1)
