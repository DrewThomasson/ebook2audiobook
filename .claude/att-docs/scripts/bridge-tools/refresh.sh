#!/usr/bin/env bash
# Rewrites bridge-tools.json from the tool list in a Code Conductor checkout.
#
#   bash scripts/bridge-tools/refresh.sh [checkout] [ref] [out]
#
# checkout  a Code Conductor repository (default ~/Code/Code-Conductor)
# ref       the commit to read (default origin/main); fetch first for the latest
# out       the file to write (default bridge-tools.json beside this script)
#
# Baton builds its tool list in baton/voice-bridge-tools.mjs. The script unpacks that
# folder from the ref into a scratch folder, imports TOOLS, and writes each tool's name and
# the names of its arguments, sorted, with the commit they came from. A repository's own
# tools, which Baton loads from that repository, are not in the file.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
checkout="${1:-$HOME/Code/Code-Conductor}"
ref="${2:-origin/main}"
out="${3:-$here/bridge-tools.json}"

command -v node >/dev/null || { echo "node is not installed" >&2; exit 1; }
sha="$(git -C "$checkout" rev-parse --verify --quiet "$ref^{commit}")" \
  || { echo "$ref is not a commit in $checkout" >&2; exit 1; }

git -C "$checkout" cat-file -e "$sha:baton/voice-bridge-tools.mjs" 2>/dev/null \
  || { echo "$ref has no baton/voice-bridge-tools.mjs" >&2; exit 1; }

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
git -C "$checkout" archive "$sha" baton | tar -x -C "$scratch"

SOURCE_SHA="$sha" TOOLS_MODULE="$scratch/baton/voice-bridge-tools.mjs" node --input-type=module -e '
import { pathToFileURL } from "node:url";
const { TOOLS } = await import(pathToFileURL(process.env.TOOLS_MODULE).href);
const tools = {};
for (const tool of [...TOOLS].sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0))) {
  tools[tool.name] = Object.keys(tool.inputSchema?.properties ?? {}).sort();
}
process.stdout.write(JSON.stringify({ source: process.env.SOURCE_SHA, tools }, null, 2) + "\n");
' > "$scratch/bridge-tools.json"

mv "$scratch/bridge-tools.json" "$out"
echo "wrote $out from $sha"
