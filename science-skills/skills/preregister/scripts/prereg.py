#!/usr/bin/env python3
"""Freeze and audit a preregistration using git history.

  prereg.py freeze PLAN [--data DIR_OR_FILE ...] [--outputs DIR ...]
  prereg.py audit  PLAN [--data DIR_OR_FILE ...] [--outputs DIR ...]

freeze:
  * refuses if PLAN was already frozen, or if any output file already exists
    under --outputs (a plan frozen after results is not a preregistration)
  * writes PLAN.checksums.json (sha256 of every raw data file)
  * commits ONLY those two paths, message "prereg-freeze: <PLAN>"

audit (exit 0 = pass, 1 = fail) verifies from git history alone:
  1. PLAN has exactly one commit and it is a "prereg-freeze:" commit
  2. PLAN has no uncommitted edits
  3. no file under --outputs was committed at or before the freeze commit
  4. recorded data checksums still match the files on disk

Not detectable: results you looked at but never committed, or a rewritten
history. For high stakes, push the freeze commit to a remote you do not control
or register externally (e.g. OSF). Stdlib + git only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

PREFIX = "prereg-freeze: "
SKIP = {".gitkeep", ".DS_Store"}


class Fail(Exception):
    pass


def git(top: str, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", "-C", top, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise Fail(f"git {' '.join(args)} failed: {r.stderr.strip() or r.stdout.strip()}")
    return r.stdout


def toplevel() -> str:
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if r.returncode != 0:
        raise Fail("not inside a git repository (freeze/audit need git; see SKILL.md for alternatives)")
    return r.stdout.strip()


def rel(top: str, path: str) -> str:
    return os.path.relpath(os.path.abspath(path), top).replace(os.sep, "/")


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_files(top: str, paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        ap = os.path.abspath(p)
        if os.path.isfile(ap):
            out.append(rel(top, ap))
        elif os.path.isdir(ap):
            for root, _d, names in os.walk(ap):
                if os.sep + ".git" in root + os.sep:
                    continue
                for n in names:
                    if n not in SKIP:
                        out.append(rel(top, os.path.join(root, n)))
        # a non-existent path simply contributes nothing (e.g. outputs dir not created yet)
    return sorted(set(out))


def plan_commits(top: str, plan_rel: str) -> list[tuple[str, str]]:
    out = git(top, "log", "--follow", "--format=%H%x09%s", "--", plan_rel, check=False)
    rows = []
    for line in out.splitlines():
        h, _, s = line.partition("\t")
        rows.append((h, s))
    return rows


def checks_path(plan_rel: str) -> str:
    return plan_rel + ".checksums.json"


def cmd_freeze(a: argparse.Namespace) -> int:
    top = toplevel()
    plan_rel = rel(top, a.plan)
    if not os.path.isfile(os.path.join(top, plan_rel)):
        raise Fail(f"plan not found: {a.plan}")
    if plan_commits(top, plan_rel):
        raise Fail(f"{plan_rel} already has commits: it cannot be frozen again. Write a new, dated plan instead.")

    existing = [f for f in walk_files(top, a.outputs) ]
    if existing:
        raise Fail(
            "output files already exist, so this cannot be a preregistration:\n  "
            + "\n  ".join(existing[:10])
            + "\nRelabel the analysis exploratory, or preregister against fresh data."
        )

    data_files = walk_files(top, a.data)
    sums = {f: sha256_of(os.path.join(top, f)) for f in data_files}
    cpath = checks_path(plan_rel)
    with open(os.path.join(top, cpath), "w", encoding="utf-8") as fh:
        json.dump(
            {"frozen_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "files": sums},
            fh, indent=2, sort_keys=True,
        )
        fh.write("\n")

    git(top, "add", "--", plan_rel, cpath)
    # pathspec after "--" => commit ONLY these paths, ignoring anything else staged
    git(top, "commit", "-m", PREFIX + plan_rel, "--", plan_rel, cpath)
    head = git(top, "rev-parse", "--short", "HEAD").strip()
    print(f"FROZEN {plan_rel} at {head}; {len(sums)} data file(s) checksummed")
    print("Now run: prereg.py audit ... (before any confirmatory claim). Consider pushing this commit to a remote.")
    return 0


def cmd_audit(a: argparse.Namespace) -> int:
    top = toplevel()
    plan_rel = rel(top, a.plan)
    problems: list[str] = []
    notes: list[str] = []

    commits = plan_commits(top, plan_rel)
    freeze = None
    if not commits:
        problems.append("plan has no commits: it was never frozen")
    elif len(commits) > 1:
        problems.append(f"plan was edited after the freeze ({len(commits)} commits touch it). Frozen means unchanged since.")
        freeze = commits[-1][0]  # earliest, for the later checks
    else:
        freeze = commits[0][0]
    if commits:
        first_subject = commits[-1][1]
        if not first_subject.startswith(PREFIX):
            problems.append(f"first commit of the plan is not a '{PREFIX}' commit (subject: {first_subject!r})")
    if git(top, "status", "--porcelain", "--", plan_rel, check=False).strip():
        problems.append("plan has uncommitted changes")

    if freeze:
        # outputs committed at or before the freeze
        listing = git(top, "log", "--name-only", "--format=@@%H", "--", *a.outputs, check=False) if a.outputs else ""
        cur = None
        offenders: list[tuple[str, str]] = []
        for line in listing.splitlines():
            if line.startswith("@@"):
                cur = line[2:]
            elif line.strip() and cur and os.path.basename(line) not in SKIP:
                offenders.append((cur, line.strip()))
        for c, f in offenders:
            r = subprocess.run(["git", "-C", top, "merge-base", "--is-ancestor", c, freeze])
            if r.returncode == 0:
                problems.append(f"output committed at or before freeze: {f} (commit {c[:8]})")

        # data checksums
        cp = os.path.join(top, checks_path(plan_rel))
        if not os.path.isfile(cp):
            problems.append(f"missing checksum file {checks_path(plan_rel)}")
        else:
            with open(cp, encoding="utf-8") as fh:
                recorded = json.load(fh)["files"]
            for f, h in recorded.items():
                p = os.path.join(top, f)
                if not os.path.isfile(p):
                    problems.append(f"frozen data file missing: {f}")
                elif sha256_of(p) != h:
                    problems.append(f"frozen data file CHANGED since freeze: {f}")
            for f in walk_files(top, a.data):
                if f not in recorded:
                    notes.append(f"data file added after freeze (not covered by checksums): {f}")
            if not recorded:
                notes.append("no data files were checksummed at freeze")

    for n in notes:
        print(f"note: {n}")
    if problems:
        for p in problems:
            print(f"FAIL: {p}")
        print("\nAUDIT FAILED: do not report confirmatory claims from this plan. Relabel affected results exploratory.")
        return 1
    print(f"AUDIT PASSED: {plan_rel} frozen at {freeze[:8]}, unedited, no earlier outputs, data checksums match.")
    print("Reminder: this cannot detect unrecorded peeking or rewritten history.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("freeze", "audit"):
        sp = sub.add_parser(name)
        sp.add_argument("plan")
        sp.add_argument("--data", nargs="*", default=[], help="raw data files/dirs to checksum or verify")
        sp.add_argument("--outputs", nargs="*", default=[], help="output dirs that must be empty at freeze")
    a = ap.parse_args(argv)
    try:
        return cmd_freeze(a) if a.cmd == "freeze" else cmd_audit(a)
    except Fail as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
