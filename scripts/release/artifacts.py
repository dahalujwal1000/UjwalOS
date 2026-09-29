#!/usr/bin/env python3
"""Local engineering artifact integrity checks, not signing or release approval."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

MANIFEST = "artifact-manifest.json"


def filename(value):
    if (not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,199}", value)
            or value == MANIFEST):
        raise ValueError("Invalid artifact filename")
    return value


def fingerprint(directory, name):
    filename(name)
    descriptor = os.open(directory / name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as source:
        before = os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("Artifact must be a regular file")
        digest = hashlib.sha256()
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
        after = os.fstat(source.fileno())
        current = (directory / name).lstat()
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if identity(before) != identity(after) or identity(after) != identity(current):
            raise ValueError("Artifact changed while hashing")
    return {"name": name, "size": after.st_size, "sha256": digest.hexdigest()}


def validate(document):
    if not isinstance(document, dict) or set(document) != {
            "schema", "classification", "source_revision", "artifacts"}:
        raise ValueError("Invalid manifest fields")
    if type(document["schema"]) is not int or document["schema"] != 1:
        raise ValueError("Unsupported manifest schema")
    if document["classification"] != "engineering-unsigned":
        raise ValueError("Unsupported artifact classification")
    revision = document["source_revision"]
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Expected full source commit identifier")
    rows = document["artifacts"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 64:
        raise ValueError("Expected 1 to 64 artifacts")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"name", "size", "sha256"}:
            raise ValueError("Invalid artifact fields")
        name = filename(row["name"])
        if name in seen:
            raise ValueError("Duplicate artifact")
        seen.add(name)
        if type(row["size"]) is not int or row["size"] < 0:
            raise ValueError("Invalid artifact size")
        if not isinstance(row["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
            raise ValueError("Invalid SHA-256")


def create(directory, names, revision):
    document = {"schema": 1, "classification": "engineering-unsigned",
                "source_revision": revision,
                "artifacts": [{"name": name, "size": 0, "sha256": "0" * 64} for name in names]}
    validate(document)
    document["artifacts"] = [fingerprint(directory, name) for name in sorted(names)]
    # Exclusive creation preserves an existing manifest, including a symlink.
    with (directory / MANIFEST).open("x", encoding="utf-8") as output:
        json.dump(document, output, indent=2, sort_keys=True)
        output.write("\n")
    return document


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def verify(directory):
    descriptor = os.open(directory / MANIFEST, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > 65536:
            raise ValueError("Invalid manifest file")
        content = source.read(65537)
        if len(content) > 65536:
            raise ValueError("Manifest too large")
    document = json.loads(content, object_pairs_hook=unique_fields)
    validate(document)
    for expected in document["artifacts"]:
        if fingerprint(directory, expected["name"]) != expected:
            raise ValueError("Artifact integrity mismatch: " + expected["name"])
    return document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("create")
    make.add_argument("directory", type=Path)
    make.add_argument("--revision", required=True)
    make.add_argument("--artifact", action="append", required=True)
    check = commands.add_parser("verify")
    check.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "create":
            create(args.directory, args.artifact, args.revision)
        else:
            verify(args.directory)
    except (OSError, ValueError, RecursionError) as error:
        print(f"Artifact check failed: {error}", file=sys.stderr)
        return 1
    print("Integrity check complete. Unsigned engineering artifacts; not release approval.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
