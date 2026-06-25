#!/usr/bin/env bash
# log.sh — append a dated entry under "## Log" in a wiki file (newest on top).
#
# Portable / self-contained: pure bash + awk, no Python or other deps.
# Drop this next to your WIKI.md in any repo.
#
# Usage:
#   ./log.sh "<entry>"                      # appends to WIKI.md next to this script
#   ./log.sh --file path/to/WIKI.md "<entry>"
#
# Conventions:
#   - Append-only. Never edits prior entries.
#   - Newest on top: inserted right below "## Log" (past the intro blockquote),
#     before the first existing "### " entry.
#   - Concreteness rule: every entry should contain a number, step, or sample count.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILE="$SCRIPT_DIR/WIKI.md"

usage() {
    cat >&2 <<'EOF'
usage:
  ./log.sh "<entry>"
  ./log.sh --file path/to/WIKI.md "<entry>"
EOF
    exit 2
}

# Optional --file override.
if [[ "${1:-}" == "--file" ]]; then
    [[ $# -ge 3 ]] || usage
    FILE="$2"
    shift 2
fi

[[ $# -ge 1 && -n "${1:-}" ]] || usage
ENTRY="$1"

if [[ ! -f "$FILE" ]]; then
    echo "log.sh: file not found: $FILE" >&2
    exit 1
fi
if ! grep -q '^## Log' "$FILE"; then
    echo "log.sh: '## Log' heading not found in $FILE" >&2
    exit 1
fi

DATE="$(date +%F)"           # YYYY-MM-DD
TMP="$(mktemp)"

# Insert "### <date>\n\n<entry>\n\n" past the "## Log" heading and any
# blank / blockquote intro lines, before the first content line. Entry is
# passed via the environment so multi-line text and special chars stay literal.
LOG_ENTRY="$ENTRY" LOG_DATE="$DATE" awk '
BEGIN {
    entry = ENVIRON["LOG_ENTRY"]
    date  = ENVIRON["LOG_DATE"]
    sub(/[ \t\r\n]+$/, "", entry)   # rstrip
    inlog = 0; inserted = 0
}
{
    if (!inlog && $0 ~ /^## Log/) { inlog = 1; print; next }
    if (inlog && !inserted) {
        if ($0 ~ /^[[:space:]]*$/ || $0 ~ /^>/) { print; next }   # keep intro lines
        printf "### %s\n\n%s\n\n", date, entry                    # insert before first content
        inserted = 1
        print
        next
    }
    print
}
END {
    if (inlog && !inserted) { printf "### %s\n\n%s\n\n", date, entry }
}
' "$FILE" > "$TMP"

mv "$TMP" "$FILE"
echo "logged → $FILE"
