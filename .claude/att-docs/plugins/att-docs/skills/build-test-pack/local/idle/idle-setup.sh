#!/usr/bin/env bash
# Installs the timer that unloads the local model from Lemonade when it is idle.
#
# usage: idle-setup.sh [--dry-run] status
#        idle-setup.sh [--dry-run] apply [--minutes N]
#        idle-setup.sh [--dry-run] revert
#
# status      Prints what is installed, the timeout in effect, and the timer's state.
#             Needs no root.
# apply       Copies idle-unload.mjs to /usr/local/lib/lemonade-idle-unload/, installs the
#             service (with the absolute path of node written in) and the timer into
#             /etc/systemd/system, reloads systemd, and enables the timer. With --minutes N
#             it also writes /etc/default/lemonade-idle-unload with IDLE_MINUTES=N. Without
#             --minutes, an existing settings file (and the timeout in it) stays as it is;
#             the timeout is 15 minutes only when no settings file exists. Refuses, before
#             changing anything, if node is not on the PATH, if node lives under /home or
#             /root or is not readable and executable by others (the service runs as a
#             dynamic user), if the path of node or of LIB_DIR holds a space, |, &, %, $, or a
#             backslash or newline (the real path of node is checked too, and it is the path
#             written into the service), if N is not a positive whole number, or if
#             /etc/default/lemonade-idle-unload exists and this script did not write it.
# revert      Disables and stops the timer, then removes the unit files, the script, the
#             settings file (only if it is unchanged since apply wrote it), and the record
#             of what apply installed. Nothing else is touched. With nothing installed it
#             does nothing.
# --dry-run   Prints each privileged command instead of running it.
#
# ETC_ROOT (default /etc) sets where the settings file and the units' parent are.
# UNIT_DIR (default $ETC_ROOT/systemd/system) sets where the units are installed.
# LIB_DIR (default /usr/local/lib/lemonade-idle-unload) sets where the script is installed;
# the installed service's ExecStart points there.
# PRIVATE_DIRS (default "/home /root") lists the folders node may not live under.
# STATE_DIR (default /var/lib/lemonade-idle-unload-setup) holds the copy of the settings file
# as apply wrote it, the reference for "is this file ours".
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ETC_ROOT="${ETC_ROOT:-/etc}"
UNIT_DIR="${UNIT_DIR:-$ETC_ROOT/systemd/system}"
LIB_DIR="${LIB_DIR:-/usr/local/lib/lemonade-idle-unload}"
STATE_DIR="${STATE_DIR:-/var/lib/lemonade-idle-unload-setup}"
SERVICE=lemonade-idle-unload.service
TIMER=lemonade-idle-unload.timer
SCRIPT=idle-unload.mjs
ENV_FILE="$ETC_ROOT/default/lemonade-idle-unload"
ENV_INSTALLED="$STATE_DIR/env.installed"
DEFAULT_MINUTES=15
PRIVATE_DIRS="${PRIVATE_DIRS:-/home /root}"
DRY=0
TMP=""
NODE_REAL=""

usage() {
  sed -n '2,/^set -/{/^set -/!p;}' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' >&2
}

cleanup() { if [ -n "$TMP" ]; then rm -rf "$TMP"; fi; }
trap cleanup EXIT

# usage: run <command> [args]; the one place a privileged command runs.
run() {
  if [ "$DRY" -eq 1 ]; then echo "+ $*"; else "$@"; fi
}

# usage: run_soft <command> [args]; like run, but a failing command is reported and skipped,
# for stopping a unit that may not be loaded.
run_soft() {
  if [ "$DRY" -eq 1 ]; then echo "+ $*"; else "$@" || echo "note: \"$*\" failed; continuing" >&2; fi
}

# usage: sed_unsafe <path>; true when the path holds a character that breaks the sed below.
sed_unsafe() {
  case "$1" in
    *[' |&\%$']* | *$'\n'*) return 0 ;;
    *) return 1 ;;
  esac
}

# usage: check_node <path>; exits 1 unless the dynamic user could run this node. Sets NODE_REAL
# to the resolved path, the one the service runs.
check_node() {
  local p real dir mode d under=0
  p="$1"
  case "$p" in /*) ;; *) echo "error: node resolved to \"$p\", not an absolute path." >&2; exit 1 ;; esac
  real="$(readlink -f "$p")"
  if sed_unsafe "$real"; then
    echo "error: the real path of node ($real) holds a space, |, &, %, \$, backslash or newline." >&2
    exit 1
  fi
  NODE_REAL="$real"
  for d in $PRIVATE_DIRS; do
    under=0
    case "$p/" in "$d/"*) under=1 ;; *) case "$real/" in "$d/"*) under=1 ;; esac ;; esac
    case "$under" in
      1) echo "error: node is under $d ($p); the service's dynamic user cannot run it." >&2
         echo "Install node with apt, which puts it in /usr/bin." >&2
         exit 1 ;;
    esac
  done
  mode="$(stat -c %a "$real")"
  if [ $(( 0${mode: -1} & 5 )) -ne 5 ]; then
    echo "error: $real (mode $mode) is not readable and executable by others." >&2
    exit 1
  fi
  dir="$(dirname "$real")"
  while [ "$dir" != "/" ]; do
    mode="$(stat -c %a "$dir")"
    if [ $(( 0${mode: -1} & 1 )) -ne 1 ]; then
      echo "error: $dir (mode $mode) cannot be entered by others." >&2
      exit 1
    fi
    dir="$(dirname "$dir")"
  done
}

# usage: state_of <unit>; the unit's is-enabled or is-active answer, "unknown" if none.
state_of() { systemctl "$1" "$2" 2>/dev/null || true; }

# True when the settings file is the one apply wrote and nobody has changed it.
env_is_ours() {
  [ -e "$ENV_FILE" ] && [ -e "$ENV_INSTALLED" ] && cmp -s "$ENV_INSTALLED" "$ENV_FILE"
}

# usage: configured_minutes; the timeout the service will use.
configured_minutes() {
  local v=""
  if [ -r "$ENV_FILE" ]; then
    v="$(sed -n 's/^IDLE_MINUTES=//p' "$ENV_FILE" | tail -n 1 | tr -d '[:space:]"')"
  fi
  echo "${v:-$DEFAULT_MINUTES}"
}

status() {
  local f
  for f in "$UNIT_DIR/$SERVICE" "$UNIT_DIR/$TIMER" "$LIB_DIR/$SCRIPT"; do
    if [ -e "$f" ]; then echo "installed: $f"; else echo "missing:   $f"; fi
  done
  if [ -e "$ENV_FILE" ]; then echo "settings:  $ENV_FILE"; else echo "settings:  none (defaults)"; fi
  echo "idle minutes: $(configured_minutes)"
  echo "timer enabled: $(state_of is-enabled $TIMER)"
  echo "timer active: $(state_of is-active $TIMER)"
}

do_apply() {
  local minutes="" given=0 node
  while [ $# -gt 0 ]; do
    case "$1" in
      --minutes)
        [ $# -ge 2 ] || { usage; exit 2; }
        minutes="$2"; given=1; shift 2 ;;
      *) usage; exit 2 ;;
    esac
  done
  if [ "$given" -eq 1 ] && ! [[ "$minutes" =~ ^[1-9][0-9]*$ ]]; then
    echo "error: --minutes must be a positive whole number, got \"$minutes\"." >&2
    exit 1
  fi
  node="$(command -v node || true)"
  if [ -z "$node" ]; then
    echo "error: node is not on the PATH; the service needs its absolute path." >&2
    exit 1
  fi
  if sed_unsafe "$node" || sed_unsafe "$LIB_DIR"; then
    echo "error: the path of node ($node) or LIB_DIR ($LIB_DIR) holds a space, |, &, %, \$, backslash or newline." >&2
    exit 1
  fi
  check_node "$node"
  if [ "$given" -eq 1 ] && [ -e "$ENV_FILE" ] && ! env_is_ours; then
    echo "error: $ENV_FILE exists and this script did not write it." >&2
    echo "Set IDLE_MINUTES in it by hand, or move it aside and run apply again." >&2
    exit 1
  fi

  TMP="$(mktemp -d)"
  sed "s|^ExecStart=/usr/bin/node .*\$|ExecStart=$NODE_REAL $LIB_DIR/$SCRIPT|" "$HERE/$SERVICE" > "$TMP/$SERVICE"
  run sudo install -d "$LIB_DIR"
  run sudo install -m 0644 "$HERE/$SCRIPT" "$LIB_DIR/$SCRIPT"
  run sudo install -d "$UNIT_DIR"
  run sudo install -m 0644 "$TMP/$SERVICE" "$UNIT_DIR/$SERVICE"
  run sudo install -m 0644 "$HERE/$TIMER" "$UNIT_DIR/$TIMER"
  if [ "$given" -eq 1 ]; then
    printf 'IDLE_MINUTES=%s\n' "$minutes" > "$TMP/env"
    run sudo install -d "$(dirname "$ENV_FILE")"
    run sudo install -m 0644 "$TMP/env" "$ENV_FILE"
    run sudo install -d "$STATE_DIR"
    run sudo install -m 0644 "$TMP/env" "$ENV_INSTALLED"
  fi
  run sudo systemctl daemon-reload
  run sudo systemctl enable --now "$TIMER"
  if [ "$DRY" -eq 1 ]; then echo "+ status"; else status; fi
}

do_revert() {
  if [ ! -e "$UNIT_DIR/$TIMER" ] && [ ! -e "$UNIT_DIR/$SERVICE" ] && [ ! -e "$LIB_DIR/$SCRIPT" ] &&
     ! env_is_ours; then
    echo "not applied; nothing to revert"
    return 0
  fi
  if [ -e "$UNIT_DIR/$TIMER" ]; then
    run sudo systemctl disable "$TIMER"
    run_soft sudo systemctl stop "$TIMER"
  fi
  if [ -e "$UNIT_DIR/$SERVICE" ]; then
    run_soft sudo systemctl stop "$SERVICE"
  fi
  run sudo rm -f "$UNIT_DIR/$TIMER" "$UNIT_DIR/$SERVICE"
  run sudo rm -f "$LIB_DIR/$SCRIPT"
  run sudo rmdir --ignore-fail-on-non-empty "$LIB_DIR"
  if env_is_ours; then
    run sudo rm -f "$ENV_FILE"
  elif [ -e "$ENV_FILE" ]; then
    echo "$ENV_FILE was not written by this script or has changed; left in place"
  fi
  run sudo rm -f "$ENV_INSTALLED"
  run sudo rmdir --ignore-fail-on-non-empty "$STATE_DIR"
  run sudo systemctl daemon-reload
}

cmd=""
args=()
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    *) if [ -z "$cmd" ]; then cmd="$a"; else args+=("$a"); fi ;;
  esac
done

case "$cmd" in
  status) [ "${#args[@]}" -eq 0 ] || { usage; exit 2; }; status ;;
  apply) do_apply ${args[@]+"${args[@]}"} ;;
  revert) [ "${#args[@]}" -eq 0 ] || { usage; exit 2; }; do_revert ;;
  *) usage; exit 2 ;;
esac
