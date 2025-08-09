import argparse, json, sys
from pathlib import Path
from wavoscope.session.project import Project

def main():
    p = argparse.ArgumentParser()
    p.add_argument("audio", help="wav/mp3/flac")
    p.add_argument("--add", nargs=3, metavar=("T", "TYPE", "NAME"),
                   help="add flag at time T")
    p.add_argument("--list", action="store_true",
                   help="print flags as json")
    args = p.parse_args()

    proj = Project(Path(args.audio))
    proj.open_file(Path(args.audio))

    if args.add:
        t, typ, name = args.add
        proj.add_flag(float(t), typ, name=name)
        print("added flag @", t)

    if args.list:
        print(json.dumps(proj.flags, indent=2))

if __name__ == "__main__":
    main()