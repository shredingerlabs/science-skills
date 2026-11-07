#!/usr/bin/env bash
# Create the research docs layout. Idempotent; never overwrites.
# Usage: scaffold.sh [docs-dir] [raw-dir] [outputs-dir]
set -euo pipefail

DOCS="${1:-docs/science}"
RAW="${2:-data/raw}"
OUT="${3:-results}"

for d in questions surveys sources data validation preregistrations deviations reviews reports retro; do
  mkdir -p "$DOCS/$d"
  [ -e "$DOCS/$d/.gitkeep" ] || : > "$DOCS/$d/.gitkeep"
done
mkdir -p "$RAW" "$OUT"
[ -e "$RAW/.gitkeep" ] || : > "$RAW/.gitkeep"
[ -e "$OUT/.gitkeep" ] || : > "$OUT/.gitkeep"

if [ ! -e "$DOCS/LOG.md" ]; then
  printf '# Lab notebook\nAppend only. Newest at the bottom. Correct old entries with a new entry that points back.\n---\n' > "$DOCS/LOG.md"
fi

echo "created: $DOCS/{questions,surveys,sources,data,validation,preregistrations,deviations,reviews,reports,retro,LOG.md} $RAW $OUT"
