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

def build_args(variant):
    return (
        f"OPENCLAW_VARIANT={variant}",
        # Optionally install Chromium and Xvfb for browser automation.
        'OPENCLAW_INSTALL_BROWSER=1',
    )

def tags(variant):
    if variant == openclaw_variants[0]:
        return (
            f"{openclaw_version}-{debian_codename}",
            f"{debian_codename}",
        )
    else:
        variant == openclaw_variants[1]
        return (
            "latest",
            f"{openclaw_version}",
            f"{openclaw_version}-{variant}",
            f"{openclaw_version}-{variant}-{debian_codename}",
            f"{variant}-{debian_codename}",
            f"{variant}",
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
    for variant in openclaw_variants:
        platform = []
        for arch in docker_arches:
            platform.append(f"{arch}")
        platform = ",".join(platform)

        matrix += f"- name: openclaw-v{openclaw_version}-"
        matrix += (
            f"{debian_codename}\n" if variant == "default"
            else f"{variant}-{debian_codename}\n"
        )
        matrix += f"  version: v{openclaw_version}\n"
        matrix += f"  context: ./openclaw\n"
        matrix += f"  platforms: {platform}\n"
        matrix += f"  docker-repo: {docker_repo}\n"
        matrix += f"  build-args: |\n"
        for build_arg in build_args(variant):
            matrix += f"    {build_arg}\n"
        matrix += f"  tags: |\n"
        for tag in tags(variant):
            matrix += f"    {tag}\n"

    marker = "#MATRIX\n"
    split = config.split(marker)
    rendered = split[0] + marker + matrix + marker + split[2]
    write_file(file, rendered)

def update_readme():
    template = read_file("README.template")

    image_tags = ""
    for variant in openclaw_variants:
      tag = ",".join([f"`{t}`" for t in tags(variant)])
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
