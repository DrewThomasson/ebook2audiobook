#!/usr/bin/env bash
# Memory setup for the host that runs the local model for test pack builds.
#
# usage: memory-setup.sh [--dry-run] status
#        memory-setup.sh [--dry-run] swappiness
#        memory-setup.sh [--dry-run] zram
#        memory-setup.sh [--dry-run] revert swappiness|zram|all
#
# status      Prints memory counters. Needs no root.
# swappiness  Records the live vm.swappiness, installs the sysctl drop-in, and applies it.
# zram        Writes the zram config, then installs systemd-zram-generator (skipped if
#             already installed) and restarts the zram0 setup so the device has the config's
#             size and algorithm. Refuses, before changing anything, if /dev/zram0 is active
#             swap that this setup did not configure, if systemd-zram-generator is installed
#             but was not installed by this script, if zram-tools or zram-config is
#             installed, if zram-generator.conf.d holds a file, if a different
#             zram-generator.conf exists, or if the swappiness drop-in is installed.
# swappiness  also refuses, before any privileged command, if this setup's zram config is
#             in place or /dev/zram0 is active swap.
# revert      Undoes a step. For swappiness: with a saved value, removes the drop-in and
#             sets the live value back to it; with a drop-in but no saved value, removes the
#             drop-in and runs sysctl --system; with neither, does nothing. A saved value
#             that is not a number is treated like no saved value. For zram: does
#             nothing unless this setup's config is in place or this script installed the
#             package; otherwise stops the swap and its setup unit (a unit that is busy or
#             will not stop is an error), removes the config if it is ours, and removes
#             systemd-zram-generator only if this script installed it.
# --dry-run   Prints each privileged command instead of running it.
#
# PROC_ROOT and SYS_ROOT (default /proc and /sys) set where status reads from.
# ETC_ROOT (default /etc) sets where the drop-in and the zram config are installed.
# STATE_DIR (default /var/lib/build-pack-memory) holds the saved swappiness, the package marker,
# and a copy of the zram config as installed (the reference for "is this config ours").
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROC_ROOT="${PROC_ROOT:-/proc}"
SYS_ROOT="${SYS_ROOT:-/sys}"
ETC_ROOT="${ETC_ROOT:-/etc}"
STATE_DIR="${STATE_DIR:-/var/lib/build-pack-memory}"
PREV_FILE="$STATE_DIR/swappiness.prev"
PKG_MARKER="$STATE_DIR/zram-package-installed"
ZRAM_INSTALLED="$STATE_DIR/zram-generator.conf.installed"
DROPIN_NAME=99-zz-build-pack-swappiness.conf
SYSCTL_FILE="$ETC_ROOT/sysctl.d/$DROPIN_NAME"
ZRAM_CONF="$ETC_ROOT/systemd/zram-generator.conf"
ZRAM_SWAP_UNIT=dev-zram0.swap
ZRAM_SETUP_UNIT=systemd-zram-setup@zram0.service
DRY=0

usage() {
  sed -n '2,/^set -/{/^set -/!p;}' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' >&2
}

# usage: run <command> [args]; the one place a privileged command runs.
run() {
  if [ "$DRY" -eq 1 ]; then echo "+ $*"; else "$@"; fi
}

# usage: read_or <file> <fallback>
read_or() { if [ -r "$1" ]; then tr -d '\n' < "$1"; else echo "$2"; fi; }

# usage: human <bytes>
human() { awk -v b="$1" 'BEGIN { printf "%.1f GiB", b / 1073741824 }'; }

# usage: meminfo_kb <field>
meminfo_kb() { awk -v k="$1:" '$1 == k { print $2 }' "$PROC_ROOT/meminfo" 2>/dev/null || true; }

status() {
  echo "vm.swappiness: $(read_or "$PROC_ROOT/sys/vm/swappiness" unknown)"
  echo "swap devices:"
  if [ -r "$PROC_ROOT/swaps" ] && [ "$(wc -l < "$PROC_ROOT/swaps")" -gt 1 ]; then
    awk 'NR > 1 { printf "  %s  size %.1f GiB  used %.1f GiB  priority %s\n", $1, $3 / 1048576, $4 / 1048576, $5 }' \
      "$PROC_ROOT/swaps"
  else
    echo "  none"
  fi
  local z="$SYS_ROOT/block/zram0"
  if [ -r "$z/mm_stat" ]; then
    local disksize orig compr
    disksize="$(read_or "$z/disksize" 0)"
    read -r orig compr _ < "$z/mm_stat"
    echo "zram0:"
    echo "  disksize $(human "$disksize")"
    echo "  orig_data_size $(human "$orig")"
    echo "  compr_data_size $(human "$compr")"
    if [ "$compr" -gt 0 ]; then
      awk -v o="$orig" -v c="$compr" 'BEGIN { printf "  compression ratio %.2f\n", o / c }'
    else
      echo "  compression ratio n/a (nothing stored)"
    fi
  else
    echo "zram0: not present"
  fi
  local avail total free
  avail="$(meminfo_kb MemAvailable)"; total="$(meminfo_kb SwapTotal)"; free="$(meminfo_kb SwapFree)"
  echo "MemAvailable: $(human $(( ${avail:-0} * 1024 )))"
  echo "SwapTotal: $(human $(( ${total:-0} * 1024 )))"
  echo "SwapFree: $(human $(( ${free:-0} * 1024 )))"
  local d found=0
  for d in "$SYS_ROOT"/class/drm/card*/device; do
    [ -r "$d/mem_info_gtt_total" ] || continue
    found=1
    echo "GTT $(basename "$(dirname "$d")"): used $(human "$(read_or "$d/mem_info_gtt_used" 0)") of $(human "$(read_or "$d/mem_info_gtt_total" 0)")"
  done
  [ "$found" -eq 1 ] || echo "GTT: not available"
}

# usage: pkg_installed <package>
pkg_installed() {
  [ "$(dpkg-query -W -f='${Status}' "$1" 2>/dev/null || true)" = "install ok installed" ]
}

# True when /dev/zram0 is active swap.
zram0_active() { grep -q '^/dev/zram0[[:space:]]' "$PROC_ROOT/swaps" 2>/dev/null; }

# True when the zram config in /etc is identical to the copy this script installed or to this
# folder's copy. Either one counts, so a run that wrote /etc but failed before updating the
# installed copy still leaves a config this script recognizes.
config_is_ours() {
  [ -e "$ZRAM_CONF" ] || return 1
  { [ -e "$ZRAM_INSTALLED" ] && cmp -s "$ZRAM_INSTALLED" "$ZRAM_CONF"; } ||
    cmp -s "$HERE/zram-generator.conf" "$ZRAM_CONF"
}

do_swappiness() {
  if config_is_ours || zram0_active; then
    echo "error: zram swap is set up; a low swappiness works against swap in RAM." >&2
    if config_is_ours || [ -e "$PKG_MARKER" ]; then
      echo "Run: ./memory-setup.sh revert zram" >&2
    else
      echo "zram swap is active from another source; this script did not set it up." >&2
    fi
    exit 1
  fi
  # Keep the first value recorded, so a second run does not save our own 10.
  if [ "$DRY" -eq 1 ] || [ ! -e "$PREV_FILE" ]; then
    run sudo install -d "$STATE_DIR"
    if [ "$DRY" -eq 1 ]; then
      [ -e "$PREV_FILE" ] || echo "+ save live vm.swappiness to $PREV_FILE"
    else
      read_or "$PROC_ROOT/sys/vm/swappiness" unknown | run sudo tee "$PREV_FILE" > /dev/null
    fi
  fi
  run sudo install -m 0644 "$HERE/$DROPIN_NAME" "$SYSCTL_FILE"
  run sudo sysctl -p "$SYSCTL_FILE"
}

# usage: stop_unit <unit>
# An inactive, failed or unknown unit is skipped; an active one is stopped (failure is fatal);
# any other state (activating, deactivating, reloading) is busy and fatal.
stop_unit() {
  local state
  state="$(systemctl is-active "$1" 2>/dev/null || true)"
  case "$state" in
    inactive|failed|unknown|"")
      echo "note: $1 is not active; nothing to stop"
      return 0 ;;
    active)
      if ! run sudo systemctl stop "$1"; then
        echo "error: $1 is active and could not be stopped (swapoff can fail under memory pressure)." >&2
        echo "Nothing was removed. Free some memory and run the revert again." >&2
        exit 1
      fi ;;
    *)
      echo "error: $1 is busy ($state). Nothing was removed. Try again in a moment." >&2
      exit 1 ;;
  esac
}

# Refuses, with no privileged call, when zram would collide with something already there.
zram_preflight() {
  local bad=0 d="$ETC_ROOT/systemd/zram-generator.conf.d" p
  if [ -e "$SYSCTL_FILE" ]; then
    echo "error: the swappiness drop-in is installed; a low swappiness works against swap in RAM." >&2
    echo "Run: ./memory-setup.sh revert swappiness" >&2
    bad=1
  fi
  if zram0_active && ! config_is_ours; then
    echo "error: /dev/zram0 is already active swap and was not set up by this script." >&2
    bad=1
  fi
  if pkg_installed systemd-zram-generator && [ ! -e "$PKG_MARKER" ]; then
    echo "error: systemd-zram-generator is installed but not by this script; someone else manages it." >&2
    bad=1
  fi
  for p in zram-tools zram-config; do
    if pkg_installed "$p"; then
      echo "error: package $p is installed and also sets up zram." >&2
      bad=1
    fi
  done
  if [ -d "$d" ] && [ -n "$(ls -A "$d" 2>/dev/null)" ]; then
    echo "error: $d holds files that would change the zram setup." >&2
    bad=1
  fi
  if [ -e "$ZRAM_CONF" ] && ! config_is_ours; then
    echo "error: $ZRAM_CONF already exists and differs from this setup's config." >&2
    echo "Move it aside or merge the settings by hand, then run zram again." >&2
    bad=1
  fi
  [ "$bad" -eq 0 ] || exit 1
}

do_zram() {
  zram_preflight
  # The config goes in first so that the first generator run sees it.
  run sudo install -m 0644 "$HERE/zram-generator.conf" "$ZRAM_CONF"
  run sudo install -d "$STATE_DIR"
  run sudo install -m 0644 "$HERE/zram-generator.conf" "$ZRAM_INSTALLED"
  if pkg_installed systemd-zram-generator; then
    echo "systemd-zram-generator is already installed; skipping apt"
  else
    run sudo apt-get update
    run sudo apt-get install -y systemd-zram-generator
    run sudo install -d "$STATE_DIR"
    run sudo touch "$PKG_MARKER"
  fi
  run sudo systemctl daemon-reload
  run sudo systemctl restart "$ZRAM_SETUP_UNIT"
  run sudo systemctl start "$ZRAM_SWAP_UNIT"
  if [ "$DRY" -eq 1 ]; then echo "+ status"; else status; fi
}

revert_swappiness() {
  if [ ! -e "$SYSCTL_FILE" ] && [ ! -e "$PREV_FILE" ]; then
    echo "swappiness step not applied; nothing to revert"
    return 0
  fi
  run sudo rm -f "$SYSCTL_FILE"
  local prev=""
  if [ -e "$PREV_FILE" ]; then prev="$(tr -d '[:space:]' < "$PREV_FILE")"; fi
  if [[ "$prev" =~ ^[0-9]+$ ]]; then
    run sudo sysctl -w "vm.swappiness=$prev"
    run sudo rm -f "$PREV_FILE"
  else
    run sudo sysctl --system
    run sudo rm -f "$PREV_FILE"
    echo "no usable saved swappiness found; vm.swappiness is now $(read_or "$PROC_ROOT/sys/vm/swappiness" unknown)"
    echo "If no config sets vm.swappiness, the value stays until reboot (the kernel default is 60)."
  fi
}

revert_zram() {
  if ! config_is_ours && [ ! -e "$PKG_MARKER" ]; then
    echo "zram step not applied; nothing to revert"
    return 0
  fi
  stop_unit "$ZRAM_SWAP_UNIT"
  stop_unit "$ZRAM_SETUP_UNIT"
  if [ ! -e "$ZRAM_CONF" ]; then
    echo "$ZRAM_CONF not present; nothing to remove"
  elif config_is_ours; then
    run sudo rm -f "$ZRAM_CONF"
  else
    echo "$ZRAM_CONF differs from this setup's config; left in place"
  fi
  if [ -e "$PKG_MARKER" ]; then
    run sudo apt-get remove -y systemd-zram-generator
    run sudo rm -f "$PKG_MARKER"
  else
    echo "systemd-zram-generator was not installed by this script; left in place"
  fi
  run sudo rm -f "$ZRAM_INSTALLED"
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

# Extra arguments are an error: revert takes exactly one target, the rest take none.
want=0; [ "$cmd" = revert ] && want=1
if [ "${#args[@]}" -ne "$want" ]; then usage; exit 2; fi

case "$cmd" in
  status) status ;;
  swappiness) do_swappiness ;;
  zram) do_zram ;;
  revert)
    case "${args[0]}" in
      swappiness) revert_swappiness ;;
      zram) revert_zram ;;
      all) revert_zram; revert_swappiness ;;
      *) usage; exit 2 ;;
    esac ;;
  *) usage; exit 2 ;;
esac
