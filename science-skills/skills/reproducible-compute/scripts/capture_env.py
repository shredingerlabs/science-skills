#!/usr/bin/env python3
"""Capture a provenance record for one analysis run.

  capture_env.py -o results/provenance.json --seed 20261022 --cmd "python analysis/run.py" \
                 [--manifest docs/science/data/manifest.json]

Records: UTC time, command, seed, git commit + whether tracked files are dirty,
Python version/platform, installed packages (pip freeze equivalent), lockfile
hashes found in the working dir, SHA-256 of the data manifest, and thread-related
env vars that change numerical results.

Stdlib only. If something cannot be determined it is recorded as null, never guessed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

LOCKFILES = ["uv.lock", "poetry.lock", "Pipfile.lock", "requirements.txt", "renv.lock",
             "environment.yml", "conda-lock.yml", "package-lock.json", "Dockerfile"]
ENV_VARS = ["OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "PYTHONHASHSEED",
            "CUDA_VISIBLE_DEVICES", "TF_DETERMINISTIC_OPS", "CUBLAS_WORKSPACE_CONFIG"]


def sh(*cmd: str) -> str | None:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def git_info() -> dict:
    commit = sh("git", "rev-parse", "HEAD")
    if commit is None:
        return {"commit": None, "dirty": None, "note": "not a git repo, or git unavailable"}
    # tracked-file changes only; untracked output files must not make every run look dirty
    dirty = bool(sh("git", "status", "--porcelain", "--untracked-files=no"))
    return {"commit": commit, "dirty": dirty, "branch": sh("git", "rev-parse", "--abbrev-ref", "HEAD")}


def packages() -> list[str] | None:
    out = sh(sys.executable, "-m", "pip", "freeze")
    if out is None:
        return None
    return sorted(out.splitlines())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--cmd", help="the command that produced the results")
    ap.add_argument("--manifest", help="data manifest to hash into the record")
    a = ap.parse_args(argv)

    rec = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "command": a.cmd,
        "seed": a.seed,
        "git": git_info(),
        "python": {"version": platform.python_version(), "implementation": platform.python_implementation(),
                   "executable": sys.executable},
        "platform": {"system": platform.system(), "release": platform.release(), "machine": platform.machine()},
        "packages": packages(),
        "lockfiles": {f: sha256_file(f) for f in LOCKFILES if os.path.isfile(f)},
        "data_manifest_sha256": sha256_file(a.manifest) if a.manifest and os.path.isfile(a.manifest) else None,
        "env": {k: os.environ.get(k) for k in ENV_VARS},
    }
    if a.manifest and not os.path.isfile(a.manifest):
        print(f"warning: manifest not found: {a.manifest}", file=sys.stderr)
    if rec["git"].get("dirty"):
        print("warning: working tree has uncommitted changes to tracked files; this run is not reproducible from the commit hash",
              file=sys.stderr)
    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    with open(a.output, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"wrote {a.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
