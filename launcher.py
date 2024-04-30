#!/usr/bin/env python3

import json
import urllib.request
import argparse
import subprocess

API_ENDPOINT = "https://api.papermc.io/v2/projects/paper"
AIKAR = [
    "-XX:+UseG1GC",
    "-XX:+ParallelRefProcEnabled",
    "-XX:MaxGCPauseMillis=200",
    "-XX:+UnlockExperimentalVMOptions",
    "-XX:+DisableExplicitGC",
    "-XX:+AlwaysPreTouch",
    "-XX:G1NewSizePercent=30",
    "-XX:G1MaxNewSizePercent=40",
    "-XX:G1HeapRegionSize=8M",
    "-XX:G1ReservePercent=20",
    "-XX:G1HeapWastePercent=5",
    "-XX:G1MixedGCCountTarget=4",
    "-XX:InitiatingHeapOccupancyPercent=15",
    "-XX:G1MixedGCLiveThresholdPercent=90",
    "-XX:G1RSetUpdatingPauseTimePercent=5",
    "-XX:SurvivorRatio=32",
    "-XX:+PerfDisableSharedMem",
    "-XX:MaxTenuringThreshold=1",
    "-Dusing.aikars.flags=https://mcflags.emc.gs",
    "-Daikars.new.flags=true",
]


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
parser.add_argument("-e", "--experimental", help="use experimental channel", action="store_true")
parser.add_argument(
    "-f",
    "--filename",
    help="filename of papermc jar (overwritten if not skipping download)",
)
parser.add_argument("-m", "--memory", help="memory to allocate (defaults to 4G)")
parser.add_argument(
    "--skip-download", help="use currently downloaded papermc jar", action="store_true"
)
parser.add_argument(
    "--skip-execution", help="don't run jar after download", action="store_true"
)
parser.add_argument(
    "--skip-aikar",
    help="don't use aikar's flags (https://docs.papermc.io/paper/aikars-flags)",
    action="store_true",
)
parser.add_argument("--gui", help="show the gui", action="store_true")

args = vars(parser.parse_args())
filename = args["filename"] if args["filename"] else "papermc.jar"

if not args["skip_download"]:
    family_info = json.loads(
        fetch(f"{API_ENDPOINT}/version_group/{args['version']}/builds")
    )
    channel = "experimental" if args["experimental"] else "default"
    build_number = args["build"]
    builds_filtered = [x for x in family_info["builds"] if x["channel"] == channel]
    if not build_number:
        build_number = builds_filtered[-1]["build"]

    build_info = [x for x in builds_filtered if x["build"] == build_number][0]
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
    memory = args["memory"] or "4G"
    try:
        subprocess.run(
            ["java"]
            + ([f"-Xms{memory}", f"-Xmx{memory}"])
            + ([] if args["skip_aikar"] else AIKAR)
            + ["-jar", filename]
            + ([] if args["gui"] else ["--nogui"])
        )
    except KeyboardInterrupt:
        print("done!")
