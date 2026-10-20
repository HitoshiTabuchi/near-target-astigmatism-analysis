from __future__ import annotations

import argparse
from pathlib import Path
import shutil


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = Path(args.destination) if args.destination else root.parent / f"{root.name}_v1.0.1"
    archive = shutil.make_archive(str(destination), "zip", root.parent, root.name)
    print(archive)
