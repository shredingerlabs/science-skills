#!/usr/bin/env python3
"""Resolve DOIs against Crossref so a human/agent can compare the registered
metadata with what a citation claims.

This checks that a DOI EXISTS and shows its registered title/year/journal and any
update notices. It does NOT verify that a paper supports a claim: that still
requires opening the paper (see SKILL.md).

Usage:
    check_dois.py references.txt            # extract DOIs from a text/markdown/bib file
    check_dois.py --doi 10.1038/nature12373
    check_dois.py references.txt --offline  # only extract + validate DOI syntax

Exit codes: 0 all resolved, 1 at least one NOT FOUND or RETRACTED, 2 at least one UNCHECKED
(network failure) and none not-found.  Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

# DOI per Crossref guidance: 10.<4-9 digits>/<anything non-whitespace>
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.IGNORECASE)
TRAILING = ".,;:)]}>'\""
API = "https://api.crossref.org/works/"


def extract_dois(text: str) -> list[str]:
    seen: dict[str, None] = {}
    for m in DOI_RE.finditer(text):
        doi = m.group(0).rstrip(TRAILING)
        # balance a trailing ')' only if there is no opening '(' in the DOI
        seen[doi.lower()] = None
    return list(seen)


def is_retraction(notices: list) -> bool:
    """True if any Crossref update notice looks like a retraction or withdrawal."""
    for n in notices:
        if isinstance(n, dict) and re.search(r"retract|withdraw", str(n.get("type", "")), re.I):
            return True
    return False


def lookup(doi: str, timeout: float = 15.0, mailto: str | None = None) -> tuple[str, dict]:
    url = API + urllib.parse.quote(doi, safe="/()")
    ua = "science-skills-check-dois/1.0"
    if mailto:
        ua += f" (mailto:{mailto})"
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "NOT FOUND", {}
        return "UNCHECKED", {"error": f"HTTP {e.code}"}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return "UNCHECKED", {"error": str(e)}
    except json.JSONDecodeError as e:
        return "UNCHECKED", {"error": f"bad JSON: {e}"}
    msg = data.get("message", {})
    year = None
    for key in ("issued", "published-print", "published-online", "created"):
        parts = (msg.get(key) or {}).get("date-parts") or [[None]]
        if parts and parts[0] and parts[0][0]:
            year = parts[0][0]
            break
    info = {
        "title": (msg.get("title") or ["?"])[0],
        "year": year,
        "journal": (msg.get("container-title") or ["?"])[0],
        "type": msg.get("type"),
        "authors": ", ".join(
            (a.get("family") or a.get("name") or "?") for a in (msg.get("author") or [])[:4]
        ),
        # Surfaced verbatim; a human must read them. Absence is NOT proof of no retraction.
        "update_notices": msg.get("updated-by") or msg.get("update-to") or [],
    }
    return "RESOLVED", info


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", nargs="?", help="text/markdown/bib file containing references")
    p.add_argument("--doi", action="append", default=[], help="a DOI to check (repeatable)")
    p.add_argument("--offline", action="store_true", help="extract DOIs only; no network")
    p.add_argument("--mailto", help="contact email for Crossref polite pool (optional)")
    a = p.parse_args(argv)

    dois: list[str] = list(a.doi)
    if a.file:
        with open(a.file, encoding="utf-8", errors="replace") as fh:
            dois += extract_dois(fh.read())
    dois = list(dict.fromkeys(d.lower() for d in dois))
    if not dois:
        print("no DOIs found", file=sys.stderr)
        return 1

    not_found = unchecked = retracted = 0
    for doi in dois:
        if a.offline:
            print(f"EXTRACTED  {doi}")
            continue
        status, info = lookup(doi, mailto=a.mailto)
        if status == "RESOLVED":
            print(f"RESOLVED   {doi}\n           {info['title']} ({info['year']}) - {info['journal']} [{info['authors']}]")
            if info["update_notices"]:
                if is_retraction(info["update_notices"]):
                    retracted += 1
                    print("           RETRACTION NOTICE: do not cite as evidence; read the notice")
                print(f"           UPDATE NOTICES (read them): {json.dumps(info['update_notices'])[:300]}")
        elif status == "NOT FOUND":
            not_found += 1
            print(f"NOT FOUND  {doi}   <- do not cite")
        else:
            unchecked += 1
            print(f"UNCHECKED  {doi}   ({info.get('error')})  <- this is not a pass")
    print(
        "\nReminder: a resolving DOI proves the paper exists, not that it says what the claim says."
        " Open it and find the claim."
    )
    if not_found or retracted:
        return 1
    if unchecked:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
