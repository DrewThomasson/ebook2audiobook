#!/usr/bin/env bash
# How the PreToolUse guards read a tool call. Sourced, never run.
# usage: . "$(dirname "$0")/lib/hook-tool.sh"; hook_tool "$payload"
#
# hook_tool sets three globals from a hook payload:
#   HOOK_KIND  edit (judged by the paths it writes), shell (judged by its
#              command text), or empty for a tool no guard reads
#   HOOK_CMD   the command text of a shell tool
#   HOOK_CWD   where the tool runs, resolved: the session's cwd, or the
#              directory a terminal tab opens in when the call names one
# The desktop-commander tools are matched by name whatever prefix their server
# was registered under, plugin or plain MCP server. The terminal panel's
# run_in_terminal is a shell tool that can open its tab anywhere.

# Where a path actually lands: `..` and symlinks resolved. Where realpath has
# no -m, the path is matched as given rather than not matched at all.
resolve() {
  realpath -m -- "$1" 2>/dev/null || printf '%s\n' "$1"
}

# usage: hook_path <base> <path>. Prints the resolved path, reading a leading
# `~` as the home directory, as the MCP tools expand it, and a relative path
# against <base>. Prints nothing for an empty path.
hook_path() {
  case "$2" in
    "") ;;
    /*) resolve "$2" ;;
    "~"*) resolve "$HOME${2#"~"}" ;;
    *) resolve "$1/$2" ;;
  esac
}

hook_tool() {
  local payload="$1" tool op field tab
  tool=$(jq -r '.tool_name // ""' <<<"$payload")
  HOOK_CWD=$(jq -r '.cwd // ""' <<<"$payload")
  [ -n "$HOOK_CWD" ] && HOOK_CWD="$(resolve "$HOOK_CWD")"
  HOOK_KIND=""
  HOOK_CMD=""
  field=command
  op=""
  case "$tool" in
    mcp__*desktop-commander__*) op="${tool##*desktop-commander__}" ;;
  esac
  case "$tool:$op" in
    Bash: | mcp__terminal__run_in_terminal: | *:start_process) HOOK_KIND=shell ;;
    *:interact_with_process) HOOK_KIND=shell field=input ;;
    Edit: | Write: | NotebookEdit: | *:write_file | *:edit_block | \
      *:create_directory | *:write_pdf | *:move_file) HOOK_KIND=edit ;;
  esac
  [ "$HOOK_KIND" = shell ] || return 0
  HOOK_CMD=$(jq -r --arg f "$field" '.tool_input[$f] // ""' <<<"$payload")
  if [ "$tool" = mcp__terminal__run_in_terminal ]; then
    tab=$(jq -r '.tool_input.cwd // ""' <<<"$payload")
    [ -n "$tab" ] && HOOK_CWD="$(hook_path "$HOOK_CWD" "$tab")"
  fi
  return 0
}
