#!/usr/bin/env bash
# Install the science skills for OpenCode (also readable by Claude Code via ~/.claude/skills).
# Installs skills, the read-only reviewer agent, and the slash commands (/red-team etc.).
#
#   ./install.sh                       # project install:  ./.opencode/{skills,agents,commands}
#   ./install.sh --global              # user install:     ~/.config/opencode/{skills,agents,commands}
#   ./install.sh --claude              # skills only, into ~/.claude/skills (Claude Code)
#   ./install.sh --dest DIR            # custom skills dir (agents/commands go to DIR/../agents, DIR/../commands)
#   add --link to symlink instead of copy (updates follow the repo)
#   add --dry-run to print actions only
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST=".opencode/skills"; AGENTS=".opencode/agents"; COMMANDS=".opencode/commands"; MODE="copy"; DRY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --global) DEST="$HOME/.config/opencode/skills"; AGENTS="$HOME/.config/opencode/agents"; COMMANDS="$HOME/.config/opencode/commands" ;;
    --claude) DEST="$HOME/.claude/skills"; AGENTS=""; COMMANDS="" ;;
    --dest)   DEST="$2"; AGENTS="$(dirname "$2")/agents"; COMMANDS="$(dirname "$2")/commands"; shift ;;
    --link)   MODE="link" ;;
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

run() { if [ "$DRY" = 1 ]; then echo "+ $*"; else "$@"; fi; }

python3 "$HERE/tools/validate.py" "$HERE/skills" --agents "$HERE/agents" --commands "$HERE/commands" >/dev/null \
  || { echo "validation failed; run tools/validate.py" >&2; exit 1; }

run mkdir -p "$DEST"
for d in "$HERE"/skills/*/; do
  name="$(basename "$d")"
  target="$DEST/$name"
  if [ -e "$target" ] || [ -L "$target" ]; then
    echo "skip (exists): $target  - remove it first to reinstall" >&2
    continue
  fi
  if [ "$MODE" = link ]; then run ln -s "${d%/}" "$target"; else run cp -R "${d%/}" "$target"; fi
  echo "installed skill: $name"
done

if [ -n "$AGENTS" ]; then
  run mkdir -p "$AGENTS"
  for f in "$HERE"/agents/*.md; do
    t="$AGENTS/$(basename "$f")"
    if [ -e "$t" ]; then echo "skip (exists): $t" >&2; continue; fi
    if [ "$MODE" = link ]; then run ln -s "$f" "$t"; else run cp "$f" "$t"; fi
    echo "installed agent: $(basename "$f")"
  done
fi
if [ -n "$COMMANDS" ]; then
  run mkdir -p "$COMMANDS"
  for f in "$HERE"/commands/*.md; do
    t="$COMMANDS/$(basename "$f")"
    if [ -e "$t" ]; then echo "skip (exists): $t" >&2; continue; fi
    if [ "$MODE" = link ]; then run ln -s "$f" "$t"; else run cp "$f" "$t"; fi
    echo "installed command: /$(basename "$f" .md)"
  done
fi
echo "done. Next: open OpenCode in your project and run /setup-science-skills"
