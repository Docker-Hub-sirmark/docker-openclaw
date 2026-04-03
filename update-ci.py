#!/usr/bin/env python3

import os
import sys

openclaw_version = "2026.4.2"

openclaw_variants = ["default", "slim"]

debian_codename = "bookworm"

docker_arches = [
    "linux/amd64",
    "linux/arm64",
]

docker_repo = "sirmark/openclaw"

def build_args(variant):
    return [
        f"OPENCLAW_VARIANT={variant}",
    ]

def tags(variant):
    if variant == openclaw_variants[0]:
        return [
            f"{openclaw_version}-{debian_codename}",
            f"{debian_codename}",
        ]
    elif variant == openclaw_variants[1]:
        return [
            "latest",
            f"{openclaw_version}",
            f"{openclaw_version}-{variant}",
            f"{openclaw_version}-{variant}-{debian_codename}",
            f"{variant}-{debian_codename}",
            f"{variant}",
        ]
    else:
        return []

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
    file = ".github/workflows/ci.yaml"
    config = read_file(file)

    versions = ""
    for variant in openclaw_variants:
        platform = []
        for arch in docker_arches:
            platform.append(f"{arch}")
        platform = ",".join(platform)

        versions += f"          - name: openclaw-v{openclaw_version}-"
        versions += (
            f"{debian_codename}\n" if variant == "default"
            else f"{variant}-{debian_codename}\n"
        )
        versions += f"            version: v{openclaw_version}\n"
        versions += f"            context: ./openclaw\n"
        versions += f"            platforms: {platform}\n"
        versions += f"            docker-repo: {docker_repo}\n"
        versions += f"            build-args: |\n"
        for build_arg in build_args(variant):
            versions += f"              {build_arg}\n"
        versions += f"            tags: |\n"
        for tag in tags(variant):
            versions += f"              {tag}\n"

    marker = "#VERSIONS\n"
    split = config.split(marker)
    rendered = split[0] + marker + versions + marker + split[2]
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
