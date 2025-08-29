#!/bin/env python3

import glob
import json
import sys
from pathlib import Path

GITHUB_PREFIX = "github:leaphy-robotics/leaphy-micropython/leaphymicropython"


def check_package_json() -> bool:
    """Validate paths in the package.json file"""
    with open("package.json", "r", encoding="utf8") as package_file:
        package = json.load(package_file)
        for url in package["urls"]:
            if not Path(url[0]).exists():
                print(f"Package URL {url[0]}: ❌ does not exist!")
                return False
            if not url[1].startswith(GITHUB_PREFIX):
                print(f"Package Source {url[1]}: ❌ should start with {GITHUB_PREFIX}")
                return False

            print(f"Package URL {url[0]}: 🍰")

        packaged_files = [url[0] for url in package["urls"]]
        for file in glob.glob("leaphymicropython/**", recursive=True):
            if not file.endswith(".py"):
                continue
            if file not in packaged_files:
                print(f"File is missing in package.json: ❌ {file}")
                return False
            print(f"File: {file} 🍰")

    return True


if __name__ == "__main__":
    if not check_package_json():
        sys.exit(1)
