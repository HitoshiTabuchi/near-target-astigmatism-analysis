from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-config", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = Path(args.output) if args.output else root / "outputs" / "raw_verification"
    command = [
        sys.executable,
        "-m",
        "near_target_pipeline.cli",
        "--repo-root",
        str(root),
        "raw",
        "--raw-config",
        args.raw_config,
        "--output",
        str(output),
    ]
    raise SystemExit(subprocess.call(command))
