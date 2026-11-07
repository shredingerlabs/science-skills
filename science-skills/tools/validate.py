#!/usr/bin/env python3
"""Validate the skill pack against OpenCode's documented SKILL.md rules.

  validate.py [skills_dir] [--agents agents_dir]

Checks per skill:
  * SKILL.md exists and begins with YAML frontmatter
  * name: 1-64 chars, ^[a-z0-9]+(-[a-z0-9]+)*$, equals the directory name
  * description: present, 1-1024 chars
  * optional metadata, if present, is a string map
  * body is non-empty and under 500 lines
  * every `scripts/<file>` or `<skill>/scripts/<file>` reference resolves to a real file
  * every inline `/slash-command` reference has a commands/<name>.md file (OpenCode custom command)
Agent files: frontmatter has a description and mode.

Stdlib only (uses a minimal frontmatter parser; no PyYAML needed).
Exit 0 = valid, 1 = problems found.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def split_frontmatter(text: str) -> tuple[dict, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    block, body = text[4:end], text[end + 5:]
    top: dict = {}
    current: str | None = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith((" ", "\t")):
            if current is None or not isinstance(top.get(current), dict):
                raise ValueError(f"unexpected indentation: {raw!r}")
            k, _, v = raw.strip().partition(":")
            top[current][k.strip()] = v.strip().strip('"').strip("'")
        else:
            k, _, v = raw.partition(":")
            k, v = k.strip(), v.strip()
            if v == "":
                top[k] = {}
                current = k
            else:
                top[k] = v.strip('"').strip("'") if v[:1] in "\"'" else v
                current = None
    return top, body


def validate(skills_dir: str, agents_dir: str | None, commands_dir: str | None = None) -> list[str]:
    problems: list[str] = []
    skills: dict[str, dict] = {}
    bodies: dict[str, str] = {}

    for name in sorted(os.listdir(skills_dir)):
        d = os.path.join(skills_dir, name)
        if not os.path.isdir(d):
            continue
        path = os.path.join(d, "SKILL.md")
        if not os.path.isfile(path):
            problems.append(f"{name}: missing SKILL.md (must be upper case)")
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                parsed = split_frontmatter(fh.read())
        except ValueError as e:
            problems.append(f"{name}: bad frontmatter: {e}")
            continue
        if parsed is None:
            problems.append(f"{name}: SKILL.md does not start with --- frontmatter ---")
            continue
        fm, body = parsed
        skills[name], bodies[name] = fm, body
        n = fm.get("name", "")
        if not isinstance(n, str) or not (1 <= len(n) <= 64) or not NAME_RE.match(n):
            problems.append(f"{name}: invalid name {n!r}")
        if n != name:
            problems.append(f"{name}: frontmatter name {n!r} != directory name")
        desc = fm.get("description", "")
        if not isinstance(desc, str) or not (1 <= len(desc) <= 1024):
            problems.append(f"{name}: description missing or not 1-1024 chars (len={len(desc) if isinstance(desc, str) else '?'})")
        meta = fm.get("metadata", {})
        if meta and not isinstance(meta, dict):
            problems.append(f"{name}: metadata must be a mapping")
        if not body.strip():
            problems.append(f"{name}: empty body")
        if body.count("\n") > 500:
            problems.append(f"{name}: body over 500 lines; move detail to a reference file")

    slash: set[str] = set()
    if commands_dir and os.path.isdir(commands_dir):
        for f in sorted(os.listdir(commands_dir)):
            if not f.endswith(".md"):
                continue
            slash.add(f[:-3])
            with open(os.path.join(commands_dir, f), encoding="utf-8") as fh:
                try:
                    parsed = split_frontmatter(fh.read())
                except ValueError as e:
                    problems.append(f"command {f}: bad frontmatter: {e}")
                    continue
            if parsed is None or not parsed[0].get("description"):
                problems.append(f"command {f}: needs frontmatter with a description")
            elif f[:-3] in skills and f"`{f[:-3]}`" not in parsed[1]:
                problems.append(f"command {f}: body must name the `{f[:-3]}` skill it loads")
    script_re = re.compile(r"(?:<([a-z0-9-]+)>/|<skill-dir>/)?scripts/([\w./-]+\.(?:py|sh))")
    slash_re = re.compile(r"`/([a-z][a-z0-9-]*)`")
    for n, body in bodies.items():
        for m in script_re.finditer(body):
            owner = m.group(1) if m.group(1) not in (None, "skill-dir") else n
            if not os.path.isfile(os.path.join(skills_dir, owner, "scripts", m.group(2))):
                problems.append(f"{n}: references missing script {owner}/scripts/{m.group(2)}")
        for m in slash_re.finditer(body):
            if m.group(1) not in slash:
                problems.append(f"{n}: references `/{m.group(1)}` but commands/{m.group(1)}.md does not exist")
        for ref in re.findall(r"\]\(([^)#]+)\)", body):
            if not ref.startswith(("http", "/")) and not os.path.exists(os.path.join(skills_dir, n, ref)):
                problems.append(f"{n}: broken relative link {ref}")
        for ref in re.findall(r"`(REFERENCE\.md)`", body):
            if not os.path.isfile(os.path.join(skills_dir, n, ref)):
                problems.append(f"{n}: mentions {ref} but it does not exist")

    if agents_dir and os.path.isdir(agents_dir):
        for f in sorted(os.listdir(agents_dir)):
            if not f.endswith(".md"):
                continue
            with open(os.path.join(agents_dir, f), encoding="utf-8") as fh:
                try:
                    parsed = split_frontmatter(fh.read())
                except ValueError as e:
                    problems.append(f"agent {f}: bad frontmatter: {e}")
                    continue
            if parsed is None:
                problems.append(f"agent {f}: no frontmatter")
                continue
            fm, _ = parsed
            for req in ("description", "mode"):
                if not fm.get(req):
                    problems.append(f"agent {f}: missing {req}")
            # OpenCode permission keys are edit/bash/webfetch/...; `shell` is silently ignored.
            if "shell" in (fm.get("permission") or {}):
                problems.append(f"agent {f}: permission key `shell` is not an OpenCode key; use `bash`")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("skills_dir", nargs="?", default=os.path.join(root, "skills"))
    ap.add_argument("--agents", default=os.path.join(root, "agents"))
    ap.add_argument("--commands", default=os.path.join(root, "commands"))
    a = ap.parse_args(argv)
    problems = validate(a.skills_dir, a.agents, a.commands)
    n = len([d for d in os.listdir(a.skills_dir) if os.path.isdir(os.path.join(a.skills_dir, d))])
    if problems:
        print("\n".join(f"FAIL {p}" for p in problems))
        print(f"\n{len(problems)} problem(s) in {n} skill(s)")
        return 1
    print(f"OK: {n} skills valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
