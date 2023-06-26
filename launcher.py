#!/usr/bin/env python3

import json
import urllib.request
import argparse
import subprocess

API_ENDPOINT = "https://api.papermc.io/v2/projects/paper"


def fetch(url, headers={}):
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as f:
        return f.read()


parser = argparse.ArgumentParser(
    prog="papermc helper",
    description="downloads and runs the latest build of a papermc version, or specified build",
)
parser.add_argument(
    "version", help="major version number, e.g. 1.20 instead of 1.20.1", type=str
)
parser.add_argument("-b", "--build", help="papermc build number", type=int)
parser.add_argument(
    "-f",
    "--filename",
    help="filename of papermc jar (overwritten if not skipping download)",
)
parser.add_argument(
    "--skip-download", help="use currently downloaded papermc jar", action="store_true"
)
parser.add_argument(
    "--skip-execution", help="don't run jar after download", action="store_true"
)

args = vars(parser.parse_args())
filename = args["filename"] if args["filename"] else "papermc.jar"

if not args["skip_download"]:
    family_info = json.loads(
        fetch(f"{API_ENDPOINT}/version_group/{args['version']}/builds")
    )
    build_number = args["build"]
    if not build_number:
        build_number = max(family_info["builds"], key=lambda x: x["build"])["build"]

    build_info = [x for x in family_info["builds"] if x["build"] == build_number][0]
    if build_info["channel"] == "experimental":
        print("warning: using experimental build")

    print(
        f"downloading papermc version {build_info['version']}, build #{build_info['build']}..."
    )

    with open(filename, "wb") as f:
        version = build_info["version"]
        build = build_info["build"]
        download = build_info["downloads"]["application"]["name"]
        f.write(
            fetch(
                f"{API_ENDPOINT}/versions/{version}/builds/{build}/downloads/{download}"
            )
        )

with open("eula.txt", "w") as f:
    f.write("eula=true")

if not args["skip_execution"]:
    try:
        subprocess.run(["java", "-jar", filename])
    except KeyboardInterrupt:
        print("done!")
