#!/usr/bin/env bash
# Protects the local model from the out-of-memory killers and throttles desktop apps first.
#
# usage: oom-setup.sh [--dry-run] status
#        oom-setup.sh [--dry-run] apply model [--restart]
#        oom-setup.sh [--dry-run] apply apps --high SIZE
#        oom-setup.sh [--dry-run] revert model|apps|all
#
# status        Prints each installed file, what systemd reports for lemonade-server.service,
#               the OOM score adjustment and control group of every running llama-server, and
#               the memory limit on app.slice. Says "restart needed" when the unit has the
#               setting but a llama-server running in the unit's control group does not. Needs no root.
# apply model   Installs 99-build-pack-oom.conf as a drop-in of lemonade-server.service
#               (OOMScoreAdjust=-500, ManagedOOMPreference=avoid) and reloads systemd. A
#               running llama-server keeps its old value until the unit restarts. A restart
#               unloads the model and ends a running job, so it happens only with --restart.
# apply apps    Installs a user drop-in for app.slice with MemoryHigh=SIZE, the build-pack
#               slice, and a drop-in that moves each build-pack unit into that slice, then
#               reloads the user manager. SIZE is a whole number with an M or G suffix, or a
#               percentage of RAM from 1% to 99%. Units already running keep their slice until
#               they restart.
# revert        Removes the files apply installed, only those that still carry the marker
#               line on their first line, and reloads systemd. Other drop-ins, such as
#               memlock.conf, are never touched.
# --dry-run     Prints each command that changes anything instead of running it.
#
# UNIT_DIR (default /etc/systemd/system) is where the system drop-in goes.
# USER_UNIT_DIR (default ~/.config/systemd/user) is where the user files go.
# PROC_ROOT (default /proc) is where running processes are read.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIT_DIR="${UNIT_DIR:-/etc/systemd/system}"
USER_UNIT_DIR="${USER_UNIT_DIR:-$HOME/.config/systemd/user}"
PROC_ROOT="${PROC_ROOT:-/proc}"
MODEL_UNIT=lemonade-server.service
MODEL_DROPIN="$UNIT_DIR/$MODEL_UNIT.d/99-build-pack-oom.conf"
APPS_DROPIN="$USER_UNIT_DIR/app.slice.d/50-build-pack-apps.conf"
SLICE_FILE="$USER_UNIT_DIR/build-pack.slice"
BUILD_UNITS=(build-pack.service build-pack-now@.service build-pack-check.service build-pack-report.service)
MARKER="# Installed by oom-setup.sh."
DRY=0
TMP=""

usage() {
  sed -n '2,/^set -/{/^set -/!p;}' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' >&2
}

cleanup() { if [ -n "$TMP" ]; then rm -rf "$TMP"; fi; }
trap cleanup EXIT

# usage: run <command> [args]; the one place a changing command runs.
run() {
  if [ "$DRY" -eq 1 ]; then echo "+ $*"; else "$@"; fi
}

# usage: ours <file>; true when the file exists and its first line is the marker.
ours() {
  [ -f "$1" ] && [ "$(head -n 1 "$1")" = "$MARKER" ]
}

# usage: slice_dropin <unit>; where the build-pack slice drop-in for a unit goes.
slice_dropin() { echo "$USER_UNIT_DIR/$1.d/50-build-pack-slice.conf"; }

# Every user file the apps step installs.
APPS_FILES=("$APPS_DROPIN" "$SLICE_FILE")
for _u in "${BUILD_UNITS[@]}"; do APPS_FILES+=("$(slice_dropin "$_u")"); done

show_prop() {
  systemctl "$@" 2>/dev/null | sed -n 's/^[A-Za-z]*=//p' | head -n 1 || true
}

status() {
  local f u pid comm adj cg unit_adj mismatch=0
  for f in "$MODEL_DROPIN" "${APPS_FILES[@]}"; do
    if ours "$f"; then echo "installed: $f"; else echo "missing:   $f"; fi
  done
  unit_adj="$(show_prop show -p OOMScoreAdjust "$MODEL_UNIT")"
  echo "$MODEL_UNIT OOMScoreAdjust: ${unit_adj:-unknown}"
  echo "$MODEL_UNIT ManagedOOMPreference: $(show_prop show -p ManagedOOMPreference "$MODEL_UNIT")"
  for pid in "$PROC_ROOT"/[0-9]*; do
    [ -r "$pid/comm" ] || continue
    comm="$(cat "$pid/comm" 2>/dev/null || true)"
    [ "$comm" = "llama-server" ] || continue
    adj="$(cat "$pid/oom_score_adj" 2>/dev/null || echo unknown)"
    cg="$(cat "$pid/cgroup" 2>/dev/null | head -n 1 || true)"
    echo "llama-server ${pid##*/}: oom_score_adj $adj, cgroup ${cg:-unknown}"
    case "$cg" in
      *"/$MODEL_UNIT") if [ -n "$unit_adj" ] && [ "$unit_adj" != "$adj" ]; then mismatch=1; fi ;;
    esac
  done
  if [ "$mismatch" -eq 1 ]; then echo "restart needed: a running llama-server differs from the unit"; fi
  echo "app.slice MemoryHigh: $(show_prop --user show -p MemoryHigh app.slice)"
  for u in "${BUILD_UNITS[@]}"; do
    case "$u" in *@.service) continue ;; esac
    echo "$u slice: $(show_prop --user show -p Slice "$u")"
  done
}

do_apply_model() {
  local restart=0
  while [ $# -gt 0 ]; do
    case "$1" in
      --restart) restart=1; shift ;;
      *) usage; exit 2 ;;
    esac
  done
  if [ -e "$MODEL_DROPIN" ] && ! ours "$MODEL_DROPIN"; then
    echo "error: $MODEL_DROPIN exists and this script did not write it." >&2
    exit 1
  fi
  run sudo install -d "$(dirname "$MODEL_DROPIN")"
  run sudo install -m 0644 "$HERE/99-build-pack-oom.conf" "$MODEL_DROPIN"
  run sudo systemctl daemon-reload
  if [ "$restart" -eq 1 ]; then
    run sudo systemctl restart "$MODEL_UNIT"
  else
    echo "restart pending: run \"apply model --restart\" between jobs to move the running llama-server to the new setting"
  fi
}

do_apply_apps() {
  local high="" u f
  while [ $# -gt 0 ]; do
    case "$1" in
      --high) [ $# -ge 2 ] || { usage; exit 2; }; high="$2"; shift 2 ;;
      *) usage; exit 2 ;;
    esac
  done
  [ -n "$high" ] || { usage; exit 2; }
  if ! [[ "$high" =~ ^[1-9][0-9]*[MG]$ || "$high" =~ ^[1-9][0-9]?%$ ]]; then
    echo "error: --high must be a whole number with an M or G suffix, or a percentage from 1% to 99%, got \"$high\"." >&2
    exit 1
  fi
  for f in "${APPS_FILES[@]}"; do
    if [ -e "$f" ] && ! ours "$f"; then
      echo "error: $f exists and this script did not write it." >&2
      exit 1
    fi
  done
  run install -d "$(dirname "$APPS_DROPIN")"
  if [ "$DRY" -eq 1 ]; then
    echo "+ install -m 0644 <build-pack-apps.conf with MemoryHigh=$high> $APPS_DROPIN"
  else
    TMP="$(mktemp -d)"
    sed "s|@HIGH@|$high|" "$HERE/build-pack-apps.conf" > "$TMP/apps.conf"
    install -m 0644 "$TMP/apps.conf" "$APPS_DROPIN"
  fi
  run install -d "$USER_UNIT_DIR"
  run install -m 0644 "$HERE/build-pack.slice" "$SLICE_FILE"
  for u in "${BUILD_UNITS[@]}"; do
    f="$(slice_dropin "$u")"
    run install -d "$(dirname "$f")"
    run install -m 0644 "$HERE/build-pack-slice.conf" "$f"
  done
  run systemctl --user daemon-reload
  echo "units already running keep their slice until they restart"
}

do_revert() {
  local what="$1" f
  case "$what" in model|apps|all) ;; *) usage; exit 2 ;; esac
  if [ "$what" = model ] || [ "$what" = all ]; then
    if ours "$MODEL_DROPIN"; then
      run sudo rm -f "$MODEL_DROPIN"
      run sudo rmdir --ignore-fail-on-non-empty "$(dirname "$MODEL_DROPIN")"
      run sudo systemctl daemon-reload
      echo "a running llama-server keeps its score until Lemonade restarts"
    elif [ -e "$MODEL_DROPIN" ]; then
      echo "$MODEL_DROPIN was not written by this script; left in place"
    else
      echo "model: not applied; nothing to revert"
    fi
  fi
  if [ "$what" = apps ] || [ "$what" = all ]; then
    local any=0
    for f in "${APPS_FILES[@]}"; do
      if ours "$f"; then
        any=1
        run rm -f "$f"
        run rmdir --ignore-fail-on-non-empty "$(dirname "$f")"
      elif [ -e "$f" ]; then
        echo "$f was not written by this script; left in place"
      fi
    done
    if [ "$any" -eq 1 ]; then
      run systemctl --user daemon-reload
      echo "running build-pack units keep build-pack.slice until they restart"
    else echo "apps: not applied; nothing to revert"; fi
  fi
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
  apply)
    [ "${#args[@]}" -ge 1 ] || { usage; exit 2; }
    sub="${args[0]}"
    case "$sub" in
      model) do_apply_model "${args[@]:1}" ;;
      apps) do_apply_apps "${args[@]:1}" ;;
      *) usage; exit 2 ;;
    esac ;;
  revert) [ "${#args[@]}" -eq 1 ] || { usage; exit 2; }; do_revert "${args[0]}" ;;
  *) usage; exit 2 ;;
esac
