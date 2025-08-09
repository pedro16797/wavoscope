"""
Command-line tool to add or list flags in a .oscope side-car file.

Examples
--------
$ python -m wavoscope.cli.flag_cli song.wav --add 12.5 rhythm "Verse 1"
$ python -m wavoscope.cli.flag_cli song.wav --list
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from wavoscope.session.project import Project


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect / edit Wavoscope flags.")
    parser.add_argument("audio", help="Audio file (.wav, .mp3, .flac)")
    parser.add_argument(
        "--add",
        nargs=3,
        metavar=("TIME", "TYPE", "NAME"),
        help="Add flag at TIME (seconds) with TYPE and NAME",
    )
    parser.add_argument(
        "--list", action="store_true", help="Print flags as JSON to stdout"
    )

    args = parser.parse_args()

    project = Project(Path(args.audio))
    project.open_file(Path(args.audio))

    if args.add:
        time_str, kind, name = args.add
        project.add_flag(float(time_str), kind, name=name)
        print(f"Added flag @ {time_str}")

    if args.list:
        print(json.dumps(project.flags, indent=2))


if __name__ == "__main__":
    main()