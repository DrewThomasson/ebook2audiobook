#!/usr/bin/env bash
# usage: run.sh [--default-on] <section> <script> [args...] < <hook payload>
# Runs one repo-hooks script for a session in any repository. hooks.json calls it for
# every hook, so the plugin's hooks work at user scope without the repository carrying a
# hook entry of its own.
#
# The repository's extension file is .claude/skills/repo-hooks/extension.json and each
# hook reads one section of it, named by <section>. A repository without the file, or
# whose file has no such section, gets no hook: this exits 0 and prints nothing. The
# script runs with the repository root as its working directory and takes the file as
# --config.
#
# --default-on marks a hook that runs in every repository, with the script's own defaults,
# whether or not the repository has an extension file or a section for it. A repository
# turns such a hook off with `"<section>": false`. The script is handed --config only when
# the file is valid JSON, so a broken file leaves the defaults in place.
#
# A repository that vendors this plugin registers the vendored run.sh in its own settings.
# A copy of run.sh anywhere else (the plugin installed at user scope) steps aside for such
# a repository, so a hook never fires twice. A hook marked --default-on steps aside only
# when the settings register that hook, so a repository that registered the others still
# gets it from the plugin copy.
here=$(dirname "$(readlink -f "$0")")
default_on=0
if [[ ${1:-} == --default-on ]]; then
  default_on=1
  shift
fi
section=${1:?usage: run.sh [--default-on] <section> <script> [args...]}
script=${2:?usage: run.sh [--default-on] <section> <script> [args...]}
shift 2
project=${CLAUDE_PROJECT_DIR:-$PWD}

# The loop uses the same section for two events. A vendored registration for one
# must not suppress the plugin's registration for the other.
event=
payload=
if [[ $section == implementLoop ]]; then
  payload=$(cat)
  event=$(jq -r '.hook_event_name // empty' <<<"$payload" 2>/dev/null)
fi

vendored=$project/.claude/att-docs/plugins/general/hooks
if [[ $here != "$(readlink -f "$vendored" 2>/dev/null)" ]]; then
  only=
  ((default_on)) && only=$section
  for settings in "$project/.claude/settings.json" "$project/.claude/settings.local.json"; do
    jq -e --arg s "$only" --arg event "$event" '[(if $event == "" then .hooks[]? else .hooks[$event]? end)[]?.hooks[]?.command // empty]
      | any(test("plugins/general/hooks/run\\.sh" + (if $s == "" then ""
          else "[\"'\'']? (--default-on )?" + $s + "([ \"'\'']|$)" end)))' \
      "$settings" >/dev/null 2>&1 && exit 0
  done
fi

config=$project/.claude/skills/repo-hooks/extension.json
if ((default_on)); then
  if jq -e --arg s "$section" '.[$s] == false' "$config" >/dev/null 2>&1; then exit 0; fi
  jq -e . "$config" >/dev/null 2>&1 || config=
else
  [[ -f $config ]] || exit 0
  jq -e --arg s "$section" '.[$s] | type == "object"' "$config" >/dev/null 2>&1 || exit 0
fi

cd "$project" || exit 0
flags=()
[[ -n $config ]] && flags=(--config "$config")
if [[ $section == implementLoop ]]; then
  exec python3 "$here/$script" "${flags[@]}" "$@" <<<"$payload"
fi
case $script in
  *.sh) exec bash "$here/$script" "${flags[@]}" "$@" ;;
  *) exec python3 "$here/$script" "${flags[@]}" "$@" ;;
esac
