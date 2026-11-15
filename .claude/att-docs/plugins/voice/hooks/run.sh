#!/usr/bin/env bash
# usage: run.sh <script> [args...] < <hook payload>
# Runs one voice-bridge-hooks script for a session in any repository. hooks.json calls it
# for every voice hook, so the plugin's hooks work at user scope without the
# repository carrying a hook entry of its own.
#
# The repository's extension file is .claude/skills/voice-bridge-hooks/extension.json; a
# repository without one gets defaults.json. A repository whose own settings still
# register these scripts keeps them, and this runner steps aside so a hook never fires
# twice.
here=$(dirname "$(readlink -f "$0")")

# A Baton run from a checkout names the voice plugin folder it runs from in voice-bridge/plugin. Claude
# Code refreshes its installed copy of this plugin only when the version changes, so the
# runner hands the hook to that folder's runner instead, and the hooks run the same code as
# Baton. With no folder named, or one without a runner, the installed copy runs.
# The file and the runner it names must be this user's own, since without XDG_RUNTIME_DIR
# the folder sits in /tmp, where anyone could write one.
pointer=${XDG_RUNTIME_DIR:-/tmp}/voice-bridge/plugin
if [[ -z ${VOICE_HOOKS_LIVE:-} && -f $pointer && -O $pointer ]]; then
  live=$(head -n 1 "$pointer" 2>/dev/null)
  [[ -n $live ]] && live=$(readlink -f "$live")
  if [[ -n $live && $live != "$(readlink -f "$here/..")" && -f $live/hooks/run.sh
    && -O $live/hooks/run.sh && -d $live/skills/voice-bridge-hooks ]]; then
    VOICE_HOOKS_LIVE=1 exec bash "$live/hooks/run.sh" "$@"
  fi
fi

skill=$(cd "$here/../skills/voice-bridge-hooks" && pwd) || exit 0
script=${1:?usage: run.sh <script> [args...]}
shift
project=${CLAUDE_PROJECT_DIR:-$PWD}

# usage: registers <settings file>; succeeds when a hook command in it runs a voice script.
registers() {
  jq -e '[.hooks[]?[]?.hooks[]?.command // empty]
    | any(test("voice_bridge_reply|speak-attention|session_title"))' "$1" >/dev/null 2>&1
}
for settings in "$project/.claude/settings.json" "$project/.claude/settings.local.json" \
  "$HOME/.claude/settings.json"; do
  registers "$settings" && exit 0
done

config=$project/.claude/skills/voice-bridge-hooks/extension.json
[[ -f $config ]] || config=$skill/defaults.json

case $script in
  *.sh) exec bash "$skill/$script" --config "$config" "$@" ;;
  *) exec python3 "$skill/$script" --config "$config" "$@" ;;
esac
