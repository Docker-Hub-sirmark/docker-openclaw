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

def get_latest_version(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(url, timeout=(5, 10))
    response.raise_for_status()

    tag_name = response.json()["tag_name"]
    version = tag_name.lstrip("v")
    return version

def check_version(latest_version, previous_version):
    if latest_version == previous_version:
        print(f"Versions match: {latest_version}, No update.")
        return False
    else:
        print(f"New version found: {latest_version} (was: {previous_version})")
        return True

def check_changelog_file(repo, latest_version):
    url = f"https://api.github.com/repos/{repo}/contents/CHANGELOG/{latest_version}.md"
    try:
        response = requests.head(url, allow_redirects=True, timeout=(5, 10))
        if response.status_code == 200:
            print(f"Changelog file found: {latest_version}.md")
            return True
        else:
            print(f"Changelog file not found: HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching changelog file: {e}")
        return False

def push_pr(repo, latest_version, previous_version):
    if check_version(latest_version, previous_version) and check_changelog_file(repo, latest_version):
        write_file(version_file, latest_version)
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
                print("should_push=true", file=fh)
                print(f"previous_version={previous_version}", file=fh)
                print(f"latest_version={latest_version}", file=fh)
                print(f"repo_name={repo}", file=fh)
    else:
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
                print("should_push=false", file=fh)

def main():

    try:
        latest_version = get_latest_version(external_repo)
    except Exception as e:
        print(f"Error fetching version: {e}")
        sys.exit(1)

    previous_version = read_file(version_file)

    push_pr(external_repo, latest_version, previous_version)

if __name__ == "__main__":
    main()
