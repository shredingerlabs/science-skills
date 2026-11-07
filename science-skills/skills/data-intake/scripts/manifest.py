#!/usr/bin/env python3
"""Write a checksum manifest for raw data files.

Usage:
    manifest.py data/raw -o docs/science/data/manifest.json
    manifest.py a.csv b.tsv --verify docs/science/data/manifest.json

--verify exits 1 if any file is missing, added, or its sha256 differs.
Delimited files (.csv/.tsv/.txt) also record row count (excluding header) and header.
Stdlib only. Files are read in binary chunks; nothing is loaded into memory whole.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

DELIMITED = {".csv": ",", ".tsv": "\t"}
SKIP_NAMES = {".gitkeep", ".DS_Store"}


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def describe(path: str) -> dict:
    entry: dict = {"sha256": sha256_of(path), "bytes": os.path.getsize(path)}
    delim = DELIMITED.get(os.path.splitext(path)[1].lower())
    if delim:
        try:
            with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
                reader = csv.reader(fh, delimiter=delim)
                header = next(reader, None)
                n = sum(1 for _ in reader)
            entry["header"] = header
            entry["rows"] = n
        except (OSError, csv.Error) as e:  # keep the hash; note the parse problem
            entry["parse_error"] = str(e)
    return entry


def collect(paths: list[str]) -> dict[str, dict]:
    files: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, names in os.walk(p):
                for n in names:
                    if n not in SKIP_NAMES:
                        files.append(os.path.join(root, n))
        elif os.path.isfile(p):
            files.append(p)
        else:
            raise SystemExit(f"not found: {p}")
    return {os.path.normpath(f).replace(os.sep, "/"): describe(f) for f in sorted(set(files))}


def verify(current: dict[str, dict], manifest_path: str) -> int:
    with open(manifest_path, encoding="utf-8") as fh:
        recorded = json.load(fh)["files"]
    bad = 0
    for f in sorted(set(recorded) | set(current)):
        if f not in current:
            print(f"MISSING   {f}")
            bad += 1
        elif f not in recorded:
            print(f"ADDED     {f}")
            bad += 1
        elif current[f]["sha256"] != recorded[f]["sha256"]:
            print(f"CHANGED   {f}")
            bad += 1
        else:
            print(f"ok        {f}")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("-o", "--output", help="write manifest JSON here")
    ap.add_argument("--verify", metavar="MANIFEST", help="compare against an existing manifest")
    a = ap.parse_args(argv)

    files = collect(a.paths)
    if not files:
        print("no files found", file=sys.stderr)
        return 1
    if a.verify:
        return verify(files, a.verify)
    manifest = {
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files": files,
    }
    text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if a.output:
        os.makedirs(os.path.dirname(a.output) or ".", exist_ok=True)
        with open(a.output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {a.output}: {len(files)} file(s)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
