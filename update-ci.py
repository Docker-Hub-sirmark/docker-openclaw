#!/usr/bin/env python3

import os
import sys

openclaw_variants = ("default", "slim")

openclaw_version_file = "openclaw_version"

docker_arches = (
    "linux/amd64",
    "linux/arm64",
)

debian_codename = "bookworm"

docker_repo = "sirmark/openclaw"

def build_args():
    return (
        'OPENCLAW_EXTENSIONS=diagnostics-otel,codex',
        # Optionally install Chromium and Xvfb for browser automation.
        'OPENCLAW_INSTALL_BROWSER=1',
    )

def tags():
    return (
        "latest",
        f"{openclaw_version}",
        f"{openclaw_version}-slim",
        f"{openclaw_version}-slim-{debian_codename}",
        f"slim-{debian_codename}",
        f"slim",
    )

def read_file(file):
    with open(file, "r") as f:
        return f.read()

def write_file(file, contents):
    dir = os.path.dirname(file)
    if dir and not os.path.exists(dir):
        os.makedirs(dir)
    with open(file, "w") as f:
        f.write(contents)

def update_ci():
    file = "ci-matrix.yaml"
    config = read_file(file)

    matrix = ""
    matrix += f"- name: openclaw-v{openclaw_version}-slim-{debian_codename}\n"
    matrix += f"  version: v{openclaw_version}\n"
    matrix += f"  context: ./openclaw\n"
    matrix += f"  platforms: |\n"
    for arch in docker_arches:
        matrix += f"    {arch}\n"
    matrix += f"  docker-repo: {docker_repo}\n"
    matrix += f"  build-args: |\n"
    for build_arg in build_args():
            matrix += f"    {build_arg}\n"
    matrix += f"  tags: |\n"
    for tag in tags():
            matrix += f"    {tag}\n"

    marker = "#MATRIX\n"
    split = config.split(marker)
    rendered = split[0] + marker + matrix + marker + split[2]
    write_file(file, rendered)

def update_readme():
    template = read_file("README.template")

    image_tags = ""
    tag = ",".join([f"`{t}`" for t in tags()])
    image_tags += f" - [{tag}](https://github.com/openclaw/openclaw/blob/main/Dockerfile)\n"

    rendered = template \
        .replace("%%TAGS%%", image_tags)
    write_file(f"README.md", rendered)

def usage():
    print(f"Usage: {sys.argv[0]} update-all|update-ci|update-readme")
    sys.exit(1)

if __name__ == "__main__":
    openclaw_version = read_file(openclaw_version_file).strip()

    if len(sys.argv) != 2:
        usage()

    task = sys.argv[1]
    if task == "update-all":
        update_ci()
        update_readme()
    elif task == "update-ci":
        update_ci()
    elif task == "update-readme":
        update_readme()
    else:
        usage()
