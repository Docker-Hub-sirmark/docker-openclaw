#!/usr/bin/env python3

import os
import requests
import sys

external_repo = "openclaw/openclaw"
version_file = "openclaw_version"

def read_file(file):
    if not os.path.exists(file):
        return ""
    with open(file, "r") as f:
        return f.read().strip()

def write_file(file, contents):
    directory = os.path.dirname(file)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(file, "w") as f:
        f.write(contents)

def get_latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(url)
    response.raise_for_status()

    tag_name = response.json()["tag_name"]
    version = tag_name.lstrip("v")
    return version

def main():

    try:
        latest_version = get_latest_release(external_repo)
    except Exception as e:
        print(f"Error fetching version: {e}")
        sys.exit(1)

    local_version = read_file(version_file)

    if latest_version == local_version:
        print(f"Versions match: {latest_version}. No update.")
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
                print("should_push=false", file=fh)
    else:
        print(f"New version found: {latest_version} (was: {local_version})")
        write_file(version_file, latest_version)

        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
                print("should_push=true", file=fh)
                print(f"latest_version={latest_version}", file=fh)
                print(f"repo_name={external_repo.split('/')[-1]}", file=fh)

if __name__ == "__main__":
    main()
