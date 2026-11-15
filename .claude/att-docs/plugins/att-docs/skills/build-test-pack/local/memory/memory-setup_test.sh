#!/usr/bin/env bash
# Cases for memory-setup.sh. A stub sudo records any call, and status reads fake
# /proc and /sys trees, so nothing on the machine is read or changed.
# usage: bash memory-setup_test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CTL="$HERE/memory-setup.sh"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

# Stubs: sudo logs and runs its arguments; sysctl, apt-get and systemctl log what they get.
# systemctl is-active prints UNIT_STATE (default active) and stop fails when STOP_FAILS=1.
# dpkg-query reports "install ok installed" for each package named in PKGS.
mkdir -p "$SANDBOX/bin"
printf '%s\n' '#!/bin/sh' 'echo "sudo $*" >> "$SUDO_LOG"' 'exec "$@"' > "$SANDBOX/bin/sudo"
for t in sysctl apt-get; do
  printf '%s\n' '#!/bin/sh' "echo \"$t \$*\" >> \"\$SUDO_LOG\"" > "$SANDBOX/bin/$t"
done
printf '%s\n' '#!/bin/sh' \
  '[ "$1" = is-active ] && { echo "${UNIT_STATE:-active}"; [ "${UNIT_STATE:-active}" = active ]; exit $?; }' \
  'echo "systemctl $*" >> "$SUDO_LOG"' \
  '[ "$1" = stop ] && [ "${STOP_FAILS:-0}" = 1 ] && { echo "swapoff failed." >&2; exit 5; }' \
  'exit 0' > "$SANDBOX/bin/systemctl"
printf '%s\n' '#!/bin/sh' 'for p in ${PKGS:-}; do' \
  '  [ "$p" = "$3" ] && { printf "install ok installed"; exit 0; }' 'done' 'exit 1' > "$SANDBOX/bin/dpkg-query"
chmod +x "$SANDBOX"/bin/*
export PATH="$SANDBOX/bin:$PATH"
export SUDO_LOG="$SANDBOX/sudo.log"
export STATE_DIR="$SANDBOX/state"
MARKER="$STATE_DIR/zram-package-installed"
unset PKGS STOP_FAILS UNIT_STATE
: > "$SUDO_LOG"
fails=0

check() {
  if [ "$1" = "$2" ]; then echo "ok   $3"; else
    echo "FAIL $3: got [$1], wanted [$2]"; fails=$((fails + 1)); fi
}
# usage: has <text> <needle> <name>
has() {
  case "$1" in *"$2"*) echo "ok   $3" ;; *) echo "FAIL $3: [$2] not in [$1]"; fails=$((fails + 1)) ;; esac
}

# usage: lacks <text> <needle> <name>
lacks() {
  case "$1" in *"$2"*) echo "FAIL $3: [$2] found in [$1]"; fails=$((fails + 1)) ;; *) echo "ok   $3" ;; esac
}

P="$SANDBOX/proc"; S="$SANDBOX/sys"
mkdir -p "$P/sys/vm" "$S/class/drm/card1/device"
echo 10 > "$P/sys/vm/swappiness"
printf '%s\n' 'Filename Type Size Used Priority' \
  '/swap.img file 8388604 1048576 -2' '/dev/zram0 partition 8388604 2097152 100' > "$P/swaps"
printf '%s\n' 'MemAvailable:   20971520 kB' 'SwapTotal:   16777208 kB' 'SwapFree:   13631480 kB' > "$P/meminfo"
echo 4294967296 > "$S/class/drm/card1/device/mem_info_gtt_total"
echo 2147483648 > "$S/class/drm/card1/device/mem_info_gtt_used"
export PROC_ROOT="$P" SYS_ROOT="$S"

out="$("$CTL" status 2>&1)"; rc=$?
check "$rc" 0 "status exits 0 without zram"
has "$out" "vm.swappiness: 10" "status shows swappiness"
has "$out" "/swap.img  size 8.0 GiB  used 1.0 GiB  priority -2" "status shows a swap device"
has "$out" "zram0: not present" "status without zram0"
has "$out" "MemAvailable: 20.0 GiB" "status shows MemAvailable"
has "$out" "SwapFree: 13.0 GiB" "status shows SwapFree"
has "$out" "used 2.0 GiB of 4.0 GiB" "status shows GTT"

mkdir -p "$S/block/zram0"
echo 8589934592 > "$S/block/zram0/disksize"
echo "4294967296 1073741824 1100000000 0 0 0 0 0 0" > "$S/block/zram0/mm_stat"
out="$("$CTL" status 2>&1)"
has "$out" "disksize 8.0 GiB" "status shows zram disksize"
has "$out" "orig_data_size 4.0 GiB" "status shows orig_data_size"
has "$out" "compr_data_size 1.0 GiB" "status shows compr_data_size"
has "$out" "compression ratio 4.00" "status shows ratio"

rm -rf "$S/class"
out="$("$CTL" status 2>&1)"
has "$out" "GTT: not available" "status without GTT"

E="$SANDBOX/etc"
mkdir -p "$E/sysctl.d" "$E/systemd"
export ETC_ROOT="$E"
DROP=99-zz-build-pack-swappiness.conf

# From here the fake host has no zram0.
rm -rf "$S/block"
printf '%s\n' 'Filename Type Size Used Priority' '/swap.img file 8388604 1048576 -2' > "$P/swaps"

out="$("$CTL" --dry-run swappiness)"
has "$out" "+ sudo install -m 0644 $HERE/$DROP $E/sysctl.d/$DROP" "dry-run swappiness install"
has "$out" "+ sudo sysctl -p $E/sysctl.d/$DROP" "dry-run swappiness apply"

out="$("$CTL" zram --dry-run)"
has "$out" "+ sudo apt-get update" "dry-run zram apt update"
has "$out" "+ sudo apt-get install -y systemd-zram-generator" "dry-run zram apt"
has "$out" "$E/systemd/zram-generator.conf" "dry-run zram conf"
has "$out" "+ sudo systemctl daemon-reload" "dry-run zram reload"
has "$out" "+ sudo systemctl restart systemd-zram-setup@zram0.service" "dry-run zram restarts the setup unit"
has "$out" "+ sudo systemctl start dev-zram0.swap" "dry-run zram start"
has "$out" "+ sudo touch $MARKER" "dry-run zram records the package install"

out="$("$CTL" --dry-run revert swappiness)"
has "$out" "swappiness step not applied; nothing to revert" "dry-run revert swappiness with nothing applied"
out="$("$CTL" --dry-run revert zram)"
has "$out" "zram step not applied; nothing to revert" "dry-run revert zram with nothing applied"
mkdir -p "$STATE_DIR"
echo 60 > "$STATE_DIR/swappiness.prev"
out="$("$CTL" --dry-run revert swappiness)"
has "$out" "+ sudo rm -f $E/sysctl.d/$DROP" "dry-run revert swappiness file"
has "$out" "+ sudo sysctl -w vm.swappiness=60" "dry-run revert swappiness sets the saved value"
cp "$HERE/zram-generator.conf" "$E/systemd/zram-generator.conf"
touch "$MARKER"
out="$("$CTL" --dry-run revert zram)"
has "$out" "+ sudo systemctl stop dev-zram0.swap" "dry-run revert zram stops swap"
has "$out" "+ sudo systemctl stop systemd-zram-setup@zram0.service" "dry-run revert zram stops setup"
has "$out" "+ sudo rm -f $E/systemd/zram-generator.conf" "dry-run revert zram conf"
has "$out" "+ sudo apt-get remove -y systemd-zram-generator" "dry-run revert zram apt remove"
has "$out" "+ sudo rm -f $MARKER" "dry-run revert zram removes the marker"
out="$("$CTL" --dry-run revert all)"
has "$out" "sysctl -w vm.swappiness=60" "dry-run revert all swappiness"
has "$out" "systemd-zram-setup@zram0.service" "dry-run revert all zram"
rm -f "$E/systemd/zram-generator.conf" "$MARKER" "$STATE_DIR/swappiness.prev"

check "$(wc -c < "$SUDO_LOG" | tr -d ' ')" 0 "dry-run never called sudo"

"$CTL" revert swappiness zram > /dev/null 2>&1; check "$?" 2 "revert with two targets exits 2"
"$CTL" status zram > /dev/null 2>&1; check "$?" 2 "status with an extra argument exits 2"
"$CTL" swappiness zram > /dev/null 2>&1; check "$?" 2 "swappiness with an extra argument exits 2"
"$CTL" bogus > /dev/null 2>&1; check "$?" 2 "unknown subcommand exits 2"
"$CTL" > /dev/null 2>&1; check "$?" 2 "no subcommand exits 2"
"$CTL" revert bogus > /dev/null 2>&1; check "$?" 2 "revert with bad target exits 2"
"$CTL" revert > /dev/null 2>&1; check "$?" 2 "revert without target exits 2"
check "$(wc -c < "$SUDO_LOG" | tr -d ' ')" 0 "bad input never called sudo"
out="$("$CTL" bogus 2>&1)"
has "$out" "STATE_DIR (default /var/lib/build-pack-memory)" "usage shows the STATE_DIR line"
has "$out" "usage: memory-setup.sh" "usage shows the header start"

# Real runs against the fake etc, with stubs.
echo 37 > "$P/sys/vm/swappiness"
: > "$SUDO_LOG"
"$CTL" swappiness > /dev/null 2>&1; check "$?" 0 "swappiness runs"
[ -f "$E/sysctl.d/$DROP" ]; check "$?" 0 "swappiness installed the drop-in"
check "$(cat "$STATE_DIR/swappiness.prev")" 37 "swappiness saved the live value"
has "$(cat "$SUDO_LOG")" "sudo tee $STATE_DIR/swappiness.prev" "swappiness wrote its state through sudo"
echo 10 > "$P/sys/vm/swappiness"
"$CTL" swappiness > /dev/null 2>&1
check "$(cat "$STATE_DIR/swappiness.prev")" 37 "a second swappiness run keeps the first saved value"

# zram refuses while our drop-in is installed, before any sudo call.
: > "$SUDO_LOG"
out="$("$CTL" zram 2>&1)"; rc=$?
check "$rc" 1 "zram refuses while the swappiness drop-in is installed"
has "$out" "revert swappiness" "zram refusal names revert swappiness"
check "$(wc -c < "$SUDO_LOG" | tr -d ' ')" 0 "drop-in refusal never called sudo"

# revert all after only the swappiness step: zram is a no-op.
: > "$SUDO_LOG"
out="$("$CTL" revert all 2>&1)"; rc=$?
check "$rc" 0 "revert all succeeds"
log="$(cat "$SUDO_LOG")"
has "$out" "zram step not applied; nothing to revert" "revert all says zram was not applied"
lacks "$log" "systemctl" "revert all touched no unit when zram was not applied"
lacks "$log" "apt-get" "revert all ran no apt when zram was not applied"
has "$log" "sysctl -w vm.swappiness=37" "revert all restored the saved swappiness"
[ ! -e "$E/sysctl.d/$DROP" ]; check "$?" 0 "revert all removed the drop-in"
[ ! -e "$STATE_DIR/swappiness.prev" ]; check "$?" 0 "revert removed the state file"

# With no drop-in and no state, revert swappiness runs nothing.
: > "$SUDO_LOG"
out="$("$CTL" revert swappiness 2>&1)"; rc=$?
check "$rc" 0 "revert swappiness with nothing applied exits 0"
has "$out" "swappiness step not applied; nothing to revert" "revert swappiness no-op message"
check "$(wc -c < "$SUDO_LOG" | tr -d ' ')" 0 "revert swappiness with nothing applied ran nothing"
# ... which also covers revert all after only the zram experiment.
cp "$HERE/zram-generator.conf" "$E/systemd/zram-generator.conf"
touch "$MARKER"
: > "$SUDO_LOG"
"$CTL" revert all > /dev/null 2>&1; check "$?" 0 "revert all after only zram exits 0"
lacks "$(cat "$SUDO_LOG")" "sysctl" "revert all after only zram left swappiness alone"
has "$(cat "$SUDO_LOG")" "apt-get remove -y systemd-zram-generator" "revert all after only zram removed the package"

# A drop-in with no saved value: remove it and re-read the system config.
cp "$HERE/$DROP" "$E/sysctl.d/$DROP"
: > "$SUDO_LOG"
out="$("$CTL" revert swappiness 2>&1)"; rc=$?
check "$rc" 0 "revert swappiness with a drop-in and no state exits 0"
log="$(cat "$SUDO_LOG")"
has "$log" "sysctl --system" "revert swappiness ran sysctl --system"
lacks "$log" "sysctl -w" "revert swappiness set no value it did not save"
has "$out" "vm.swappiness is now 10" "revert swappiness printed the live value"
has "$out" "kernel default is 60" "revert swappiness explained the value stays until reboot"
[ ! -e "$E/sysctl.d/$DROP" ]; check "$?" 0 "revert swappiness removed the drop-in"

# A saved value that is not a number: no sysctl -w; remove the drop-in, re-read the config, drop the state.
for bad in unknown ""; do
  echo "$bad" > "$STATE_DIR/swappiness.prev"
  cp "$HERE/$DROP" "$E/sysctl.d/$DROP"
  : > "$SUDO_LOG"
  out="$("$CTL" revert swappiness 2>&1)"; rc=$?
  check "$rc" 0 "revert swappiness with saved value [$bad] exits 0"
  log="$(cat "$SUDO_LOG")"
  lacks "$log" "sysctl -w" "revert swappiness with saved value [$bad] set no value"
  has "$log" "sysctl --system" "revert swappiness with saved value [$bad] ran sysctl --system"
  has "$out" "vm.swappiness is now 10" "revert swappiness with saved value [$bad] printed the live value"
  has "$out" "kernel default is 60" "revert swappiness with saved value [$bad] printed the note"
  [ ! -e "$E/sysctl.d/$DROP" ] && [ ! -e "$STATE_DIR/swappiness.prev" ]; check "$?" 0 "revert swappiness with saved value [$bad] removed the drop-in and state"
done

# An active unit that will not stop stops the revert before anything is removed.
cp "$HERE/zram-generator.conf" "$E/systemd/zram-generator.conf"
touch "$MARKER"
: > "$SUDO_LOG"
out="$(STOP_FAILS=1 "$CTL" revert zram 2>&1)"; rc=$?
check "$rc" 1 "revert zram exits 1 when an active unit will not stop"
has "$out" "dev-zram0.swap is active and could not be stopped" "stop failure names the unit"
case "$(cat "$SUDO_LOG")" in *"rm -f"*|*"apt-get remove"*) echo "FAIL stop failure still removed things"; fails=$((fails + 1)) ;; *) echo "ok   stop failure removed nothing" ;; esac
[ -f "$E/systemd/zram-generator.conf" ]; check "$?" 0 "stop failure left the config"
[ -f "$MARKER" ]; check "$?" 0 "stop failure left the marker"
# Recreate the swappiness state so a revert that went on to swappiness would visibly act on it.
echo 60 > "$STATE_DIR/swappiness.prev"
cp "$HERE/$DROP" "$E/sysctl.d/$DROP"
: > "$SUDO_LOG"
STOP_FAILS=1 "$CTL" revert all > /dev/null 2>&1; check "$?" 1 "revert all exits 1 when a stop fails"
case "$(cat "$SUDO_LOG")" in *"sysctl -w"*) echo "FAIL revert all went on to swappiness"; fails=$((fails + 1)) ;; *) echo "ok   revert all stopped before swappiness" ;; esac
[ -f "$STATE_DIR/swappiness.prev" ] && [ -f "$E/sysctl.d/$DROP" ]; check "$?" 0 "revert all left the swappiness state alone after a stop failure"
rm -f "$STATE_DIR/swappiness.prev" "$E/sysctl.d/$DROP"

# Transitional states are busy: error, nonzero, nothing removed.
for st in activating deactivating reloading; do
  : > "$SUDO_LOG"
  out="$(UNIT_STATE=$st "$CTL" revert zram 2>&1)"; rc=$?
  check "$rc" 1 "revert zram exits 1 when a unit is $st"
  has "$out" "is busy ($st)" "busy message for $st"
  log="$(cat "$SUDO_LOG")"
  lacks "$log" "rm -f" "no rm when a unit is $st"
  lacks "$log" "apt-get remove" "no apt remove when a unit is $st"
  lacks "$log" "systemctl stop" "no stop attempted when a unit is $st"
  [ -f "$E/systemd/zram-generator.conf" ] && [ -f "$MARKER" ]; check "$?" 0 "config and marker kept when a unit is $st"
done

# Inactive, failed and unknown units are skipped.
for st in inactive failed unknown; do
  : > "$SUDO_LOG"
  cp "$HERE/zram-generator.conf" "$E/systemd/zram-generator.conf"
  touch "$MARKER"
  out="$(UNIT_STATE=$st STOP_FAILS=1 "$CTL" revert zram 2>&1)"; rc=$?
  check "$rc" 0 "revert zram skips $st units"
  has "$out" "dev-zram0.swap is not active" "$st unit note"
  lacks "$(cat "$SUDO_LOG")" "systemctl stop" "$st unit not stopped"
  has "$(cat "$SUDO_LOG")" "apt-get remove -y systemd-zram-generator" "revert zram removed the package after skipping $st"
done
[ ! -e "$MARKER" ]; check "$?" 0 "revert zram removed the marker"
[ ! -e "$E/systemd/zram-generator.conf" ]; check "$?" 0 "revert zram removed our config"

# Nothing applied: revert zram changes nothing.
: > "$SUDO_LOG"
out="$("$CTL" revert zram 2>&1)"; rc=$?
check "$rc" 0 "revert zram with nothing applied exits 0"
has "$out" "zram step not applied; nothing to revert" "revert zram no-op message"
check "$(wc -c < "$SUDO_LOG" | tr -d ' ')" 0 "revert zram with nothing applied ran nothing"

# Our config but no marker: stop and remove the config, leave a package we did not install.
cp "$HERE/zram-generator.conf" "$E/systemd/zram-generator.conf"
: > "$SUDO_LOG"
"$CTL" revert zram > /dev/null 2>&1; check "$?" 0 "revert zram with our config and no marker exits 0"
log="$(cat "$SUDO_LOG")"
has "$log" "systemctl stop dev-zram0.swap" "revert zram stopped the swap"
has "$log" "rm -f $E/systemd/zram-generator.conf" "revert zram removed our config"
lacks "$log" "apt-get remove" "revert zram did not remove a package the script did not install"

# Preflight refusals: each exits 1 with no sudo call.
refuses() { # usage: refuses <name> <needle>
  : > "$SUDO_LOG"
  out="$("$CTL" zram 2>&1)"; rc=$?
  check "$rc" 1 "zram refuses: $1"
  has "$out" "$2" "zram refusal message: $1"
  check "$(wc -c < "$SUDO_LOG" | tr -d ' ')" 0 "zram refusal never called sudo: $1"
}
printf '%s\n' 'Filename Type Size Used Priority' '/dev/zram0 partition 8388604 0 100' > "$P/swaps"
refuses "/dev/zram0 is active swap" "/dev/zram0 is already active swap"
printf '%s\n' 'Filename Type Size Used Priority' '/swap.img file 8388604 1048576 -2' > "$P/swaps"
# A zram0 block device that was reset (in /sys, not in swaps) does not block.
mkdir -p "$S/block/zram0"
: > "$SUDO_LOG"
out="$("$CTL" --dry-run zram 2>&1)"; rc=$?
check "$rc" 0 "a reset zram0 in /sys does not block zram"
lacks "$out" "already active" "reset zram0 message"
rmdir "$S/block/zram0"
PKGS="zram-tools" refuses "zram-tools installed" "zram-tools is installed"
PKGS="zram-config" refuses "zram-config installed" "zram-config is installed"
PKGS="systemd-zram-generator" refuses "package installed without our marker" "someone else manages it"
mkdir -p "$E/systemd/zram-generator.conf.d"
touch "$E/systemd/zram-generator.conf.d/local.conf"
refuses "drop-in directory has a file" "zram-generator.conf.d"
rm -rf "$E/systemd/zram-generator.conf.d"

echo "[zram0]" > "$E/systemd/zram-generator.conf"
echo "zram-size = 1" >> "$E/systemd/zram-generator.conf"
refuses "a different existing config" "already exists and differs"
: > "$SUDO_LOG"
out="$("$CTL" revert zram 2>&1)"
has "$out" "zram step not applied; nothing to revert" "revert zram leaves a different config alone with no marker"
check "$(wc -c < "$SUDO_LOG" | tr -d ' ')" 0 "revert zram with a different config and no marker ran nothing"
touch "$MARKER"
: > "$SUDO_LOG"
"$CTL" revert zram > /dev/null 2>&1; check "$?" 0 "revert zram with a different config and a marker exits 0"
[ -f "$E/systemd/zram-generator.conf" ]; check "$?" 0 "revert zram left a different config"
has "$(cat "$SUDO_LOG")" "systemctl stop dev-zram0.swap" "revert zram still tried the stop"
has "$(cat "$SUDO_LOG")" "apt-get remove -y systemd-zram-generator" "revert zram removed the package it installed"
case "$(cat "$SUDO_LOG")" in *"rm -f $E"*) echo "FAIL revert removed a different config"; fails=$((fails + 1)) ;; *) echo "ok   revert did not rm a different config" ;; esac
rm -f "$E/systemd/zram-generator.conf" "$MARKER"

# Fresh zram run: config is written before apt, marker recorded, setup restarted before start.
: > "$SUDO_LOG"
"$CTL" zram > /dev/null 2>&1; check "$?" 0 "zram runs on a clean host"
log="$(cat "$SUDO_LOG")"
cmp -s "$HERE/zram-generator.conf" "$E/systemd/zram-generator.conf"; check "$?" 0 "zram installed our config"
[ -f "$MARKER" ]; check "$?" 0 "zram recorded that it installed the package"
line() { grep -n -m1 -- "$1" "$SUDO_LOG" | cut -d: -f1; }
inst="$(line "install -m 0644 $HERE/zram-generator.conf")"; upd="$(line "apt-get update")"
reload="$(line "systemctl daemon-reload")"; rest="$(line "systemctl restart systemd-zram-setup@zram0.service")"
strt="$(line "systemctl start dev-zram0.swap")"
[ -n "$inst" ] && [ -n "$upd" ] && [ "$inst" -lt "$upd" ]; check "$?" 0 "config written before apt update"
[ "$upd" -lt "$reload" ] && [ "$reload" -lt "$rest" ] && [ "$rest" -lt "$strt" ]; check "$?" 0 "reload, restart, start run in order after apt"

# swappiness refuses while our zram config is in place, before any sudo call.
: > "$SUDO_LOG"
out="$("$CTL" swappiness 2>&1)"; rc=$?
check "$rc" 1 "swappiness refuses while our zram config is present"
has "$out" "revert zram" "swappiness refusal names revert zram"
check "$(wc -c < "$SUDO_LOG" | tr -d ' ')" 0 "swappiness refusal never called sudo"
rm -f "$E/systemd/zram-generator.conf"
printf '%s\n' 'Filename Type Size Used Priority' '/dev/zram0 partition 8388604 0 100' > "$P/swaps"
out="$("$CTL" swappiness 2>&1)"; rc=$?
check "$rc" 1 "swappiness refuses while /dev/zram0 is active swap"
check "$(wc -c < "$SUDO_LOG" | tr -d ' ')" 0 "swappiness swap refusal never called sudo"
printf '%s\n' 'Filename Type Size Used Priority' '/swap.img file 8388604 1048576 -2' > "$P/swaps"

# A re-run is allowed: our config in place, our marker, the package installed, zram0 active.
cp "$HERE/zram-generator.conf" "$E/systemd/zram-generator.conf"
printf '%s\n' 'Filename Type Size Used Priority' '/dev/zram0 partition 8388604 0 100' > "$P/swaps"
: > "$SUDO_LOG"
PKGS="systemd-zram-generator" "$CTL" zram > /dev/null 2>&1; check "$?" 0 "zram re-runs with the package, marker and config in place"
lacks "$(cat "$SUDO_LOG")" "apt-get" "apt skipped when the package is installed"
has "$(cat "$SUDO_LOG")" "systemctl start dev-zram0.swap" "zram still started the swap with apt skipped"
printf '%s\n' 'Filename Type Size Used Priority' '/swap.img file 8388604 1048576 -2' > "$P/swaps"
"$CTL" revert zram > /dev/null 2>&1
[ ! -e "$E/systemd/zram-generator.conf" ]; check "$?" 0 "revert zram removed an identical config"
[ ! -e "$MARKER" ]; check "$?" 0 "revert zram removed the marker"

# The installed copy is the ownership reference: a later change to this folder's config does not
# orphan the config in /etc.
rm -f "$E/systemd/zram-generator.conf" "$MARKER" "$STATE_DIR/zram-generator.conf.installed"
COPY="$SANDBOX/memcopy"
mkdir -p "$COPY"
cp "$HERE"/memory-setup.sh "$HERE"/zram-generator.conf "$HERE/$DROP" "$COPY/"
: > "$SUDO_LOG"
"$COPY/memory-setup.sh" zram > /dev/null 2>&1; check "$?" 0 "zram runs from a temp copy of the folder"
[ -f "$STATE_DIR/zram-generator.conf.installed" ]; check "$?" 0 "zram saved the installed copy"
has "$(cat "$SUDO_LOG")" "install -m 0644 $COPY/zram-generator.conf $STATE_DIR/zram-generator.conf.installed" "the installed copy is written through sudo"
echo "# changed after the apply" >> "$COPY/zram-generator.conf"
printf '%s\n' 'Filename Type Size Used Priority' '/dev/zram0 partition 8388604 0 100' > "$P/swaps"
: > "$SUDO_LOG"
PKGS="systemd-zram-generator" "$COPY/memory-setup.sh" zram > /dev/null 2>&1; check "$?" 0 "re-apply treats the installed config as ours after the repo copy changed"
printf '%s\n' 'Filename Type Size Used Priority' '/swap.img file 8388604 1048576 -2' > "$P/swaps"
# A run that wrote /etc but not the installed copy: /etc matches the folder, the copy is stale.
cp "$E/systemd/zram-generator.conf" "$SANDBOX/etc-conf.saved"
cp "$COPY/zram-generator.conf" "$E/systemd/zram-generator.conf"
echo "# stale" > "$STATE_DIR/zram-generator.conf.installed"
: > "$SUDO_LOG"
"$COPY/memory-setup.sh" revert zram > /dev/null 2>&1; check "$?" 0 "revert zram exits 0 with a stale installed copy"
has "$(cat "$SUDO_LOG")" "rm -f $E/systemd/zram-generator.conf" "revert zram treats a config matching the folder as ours when the installed copy is stale"
# Put back the applied state for the revert case below.
mkdir -p "$E/systemd" && cp "$SANDBOX/etc-conf.saved" "$E/systemd/zram-generator.conf"
cp "$SANDBOX/etc-conf.saved" "$STATE_DIR/zram-generator.conf.installed"
: > "$MARKER"
: > "$SUDO_LOG"
"$COPY/memory-setup.sh" revert zram > /dev/null 2>&1; check "$?" 0 "revert zram exits 0 after the repo copy changed"
has "$(cat "$SUDO_LOG")" "rm -f $E/systemd/zram-generator.conf" "revert zram removed the config after the repo copy changed"
[ ! -e "$E/systemd/zram-generator.conf" ] && [ ! -e "$STATE_DIR/zram-generator.conf.installed" ] && [ ! -e "$MARKER" ]
check "$?" 0 "revert zram removed the config, the installed copy and the marker"

# With zram0 active from another source, the swappiness refusal does not advise revert zram.
printf '%s\n' 'Filename Type Size Used Priority' '/dev/zram0 partition 8388604 0 100' > "$P/swaps"
out="$("$CTL" swappiness 2>&1)"; rc=$?
check "$rc" 1 "swappiness refuses for zram0 from another source"
lacks "$out" "revert zram" "swappiness refusal does not advise revert zram for another source"
has "$out" "active from another source" "swappiness refusal says zram is from another source"
printf '%s\n' 'Filename Type Size Used Priority' '/swap.img file 8388604 1048576 -2' > "$P/swaps"

# Dry-run prints the save line only when nothing is saved yet.
out="$("$CTL" --dry-run swappiness)"
has "$out" "save live vm.swappiness" "dry-run swappiness prints the save line with no saved value"
echo 60 > "$STATE_DIR/swappiness.prev"
out="$("$CTL" --dry-run swappiness)"
lacks "$out" "save live vm.swappiness" "dry-run swappiness omits the save line when a value is saved"
rm -f "$STATE_DIR/swappiness.prev"

[ "$fails" -eq 0 ] || { echo "$fails failed"; exit 1; }
echo "all passed"
