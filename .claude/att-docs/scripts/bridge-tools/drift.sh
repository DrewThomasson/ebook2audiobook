#!/usr/bin/env bash
# Warns when bridge-tools.json is behind Code Conductor's main.
#
#   GH_TOKEN=<token that can read Code-Conductor> bash scripts/bridge-tools/drift.sh
#
# The script clones the main branch of merph518/Code-Conductor (depth 1), rebuilds the tool
# list from baton/voice-bridge-tools.mjs with refresh.sh into a scratch file, and compares it
# with the committed bridge-tools.json. A difference prints a warning that names each tool
# and argument that changed. Inside GitHub Actions the warning is also an annotation.
#
# The check is advisory. It exits 0 on every path: a missing token, a failed clone, a
# rebuild that fails, and an unreadable snapshot each print a notice and skip, so a Baton
# release never turns a pull request red.
#
# BRIDGE_TOOLS_JSON overrides the committed snapshot to compare (default bridge-tools.json
# beside this script).
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
committed="${BRIDGE_TOOLS_JSON:-$here/bridge-tools.json}"
repo="merph518/Code-Conductor"
scratch=""
trap '[ -z "$scratch" ] || rm -rf "$scratch"' EXIT

skip() {
  echo "Notice: the Baton tool snapshot was not compared with Code Conductor: $1"
}

# Prints the end of a log, with the token blanked out, indented under a notice.
show_log() {
  local text
  text="$(tail -n 5 "$1")"
  text="${text//"$GH_TOKEN"/***}"
  if [ -n "$text" ]; then
    printf '%s\n' "$text" | sed 's/^/  /'
  fi
}

main() {
  if [ -z "${GH_TOKEN:-}" ]; then
    skip "no token that can read $repo is available."
    return
  fi
  local tool
  for tool in gh git node python3 timeout; do
    command -v "$tool" >/dev/null || { skip "$tool is not installed."; return; }
  done
  scratch="$(mktemp -d)" || { scratch=""; skip "no scratch folder could be made."; return; }

  # The token is for the clone only. The rebuild imports JavaScript from the clone, so it
  # runs without the token.
  if ! GIT_TERMINAL_PROMPT=0 timeout -k 10 120 \
      gh repo clone "$repo" "$scratch/checkout" -- --depth 1 --branch main \
      >"$scratch/clone.log" 2>&1; then
    skip "$repo main could not be fetched."
    show_log "$scratch/clone.log"
    return
  fi
  if ! env -u GH_TOKEN -u GITHUB_TOKEN timeout -k 10 60 \
      bash "$here/refresh.sh" "$scratch/checkout" HEAD "$scratch/fresh.json" \
      >"$scratch/refresh.log" 2>&1; then
    skip "the tool list could not be rebuilt from $repo main."
    show_log "$scratch/refresh.log"
    return
  fi

  local differences status annotation
  differences="$(python3 -I "$here/drift.py" "$committed" "$scratch/fresh.json" 2>&1)"
  status=$?
  case "$status" in
    0)
      echo "The Baton tool snapshot matches $repo main."
      ;;
    1)
      echo "Warning: bridge-tools.json differs from $repo main, so a skill may name a tool" \
        "or an argument that changed:"
      printf '%s\n' "$differences" | sed 's/^/  /'
      echo "To bring it up to date, run bash scripts/bridge-tools/refresh.sh from a fetched" \
        "Code Conductor checkout, commit the new bridge-tools.json, and fix what" \
        "skill_tools.py reports."
      if [ "${GITHUB_ACTIONS:-}" = "true" ]; then
        # An annotation message writes a percent sign as %25 and a newline as %0A.
        annotation="${differences//%/%25}"
        annotation="${annotation//$'\n'/%0A}"
        echo "::warning title=Baton tool snapshot is behind Code Conductor::$annotation"
      fi
      ;;
    *)
      skip "the snapshots could not be read."
      printf '%s\n' "$differences" | sed 's/^/  /'
      ;;
  esac
}

main
exit 0
