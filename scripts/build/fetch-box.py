#!/usr/bin/env python3
"""Fetch/hash-check pinned builder files. Refuse upstream drift, never re-pin."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    lock = json.loads((ROOT / "image/builder.json").read_text())
    cache = Path(sys.argv[1]) / "universal"
    cache.mkdir(parents=True, exist_ok=True)
    for name, expected in lock["files"].items():
        target = cache / name
        if not target.exists():
            temporary = cache / (name + ".download")
            subprocess.run(["curl", "--fail", "--location", "--proto", "=https",
                            "--proto-redir", "=https", "--retry", "2", "--connect-timeout", "30",
                            "--max-time", "3600", "--output", str(temporary),
                            lock["source"] + "/" + name], check=True)
            if digest(temporary) != expected:
                raise SystemExit(f"Builder input changed: {name}. Preserve the pinned cache or review/re-pin a new builder; refusing to boot it.")
            temporary.rename(target)
        if not target.is_file() or target.is_symlink() or digest(target) != expected:
            raise SystemExit(f"Builder checksum mismatch: {target}; refusing to boot")
        # The boxed plugin expects these sidecars even with update checks off.
        (cache / (name + ".sha256")).write_text(f"{expected}  {name}\n")
        print(f"Builder verified: {name}")


if __name__ == "__main__":
    main()
