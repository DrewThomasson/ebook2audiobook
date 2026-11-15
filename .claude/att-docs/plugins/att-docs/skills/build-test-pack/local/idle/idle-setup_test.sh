#!/usr/bin/env bash
# Cases for idle-setup.sh. A stub sudo runs its command inside a sandbox, and a stub
# systemctl records what it is asked, so nothing on the machine is read or changed.
# usage: bash idle-setup_test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CTL="$HERE/idle-setup.sh"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

# Stubs: sudo logs and runs its arguments; systemctl logs what it gets. systemctl is-enabled
# and is-active print UNIT_STATE (default enabled / active).
mkdir -p "$SANDBOX/bin"
printf '%s\n' '#!/bin/sh' 'echo "sudo $*" >> "$SUDO_LOG"' 'exec "$@"' > "$SANDBOX/bin/sudo"
printf '%s\n' '#!/bin/sh' \
  '[ "$1" = is-enabled ] && { echo "${UNIT_STATE:-enabled}"; exit 0; }' \
  '[ "$1" = is-active ] && { echo "${UNIT_STATE:-active}"; exit 0; }' \
  'echo "systemctl $*" >> "$SUDO_LOG"' 'exit 0' > "$SANDBOX/bin/systemctl"
chmod +x "$SANDBOX"/bin/*
export PATH="$SANDBOX/bin:$PATH"
export SUDO_LOG="$SANDBOX/sudo.log"
export ETC_ROOT="$SANDBOX/etc"
export UNIT_DIR="$SANDBOX/etc/systemd/system"
export LIB_DIR="$SANDBOX/lib/lemonade-idle-unload"
export STATE_DIR="$SANDBOX/state"
ENVF="$ETC_ROOT/default/lemonade-idle-unload"
NODE="$(command -v node)"
: > "$SUDO_LOG"
fails=0

check() {
  if [ "$1" = "$2" ]; then echo "ok   $3"; else
    echo "FAIL $3: got [$1], wanted [$2]"; fails=$((fails + 1)); fi
}
has() {
  case "$1" in *"$2"*) echo "ok   $3" ;; *) echo "FAIL $3: [$2] not in [$1]"; fails=$((fails + 1)) ;; esac
}
lacks() {
  case "$1" in *"$2"*) echo "FAIL $3: [$2] found in [$1]"; fails=$((fails + 1)) ;; *) echo "ok   $3" ;; esac
}

# Nothing installed.
out="$("$CTL" status 2>&1)"; rc=$?
check "$rc" 0 "status exits 0 with nothing installed"
has "$out" "missing:   $UNIT_DIR/lemonade-idle-unload.timer" "status lists a missing timer"
has "$out" "idle minutes: 15" "status shows the default timeout"
out="$("$CTL" revert 2>&1)"; rc=$?
check "$rc" 0 "revert exits 0 with nothing installed"
has "$out" "nothing to revert" "revert with nothing installed says so"

# Dry run changes nothing.
out="$("$CTL" --dry-run apply --minutes 30 2>&1)"; rc=$?
check "$rc" 0 "dry-run apply exits 0"
has "$out" "+ sudo install -m 0644 $HERE/idle-unload.mjs $LIB_DIR/idle-unload.mjs" "dry-run installs the script"
has "$out" "+ sudo install -m 0644 $HERE/lemonade-idle-unload.timer $UNIT_DIR/lemonade-idle-unload.timer" "dry-run installs the timer"
has "$out" "$UNIT_DIR/lemonade-idle-unload.service" "dry-run installs the service"
has "$out" "$ENVF" "dry-run installs the settings file"
has "$out" "+ sudo systemctl daemon-reload" "dry-run reloads systemd"
has "$out" "+ sudo systemctl enable --now lemonade-idle-unload.timer" "dry-run enables the timer"
[ ! -e "$UNIT_DIR" ] && [ ! -e "$LIB_DIR" ] && [ ! -s "$SUDO_LOG" ]
check "$?" 0 "dry-run apply wrote nothing and ran nothing"

# Refusals, before any privileged command.
for bad in 0 -3 1.5 abc ""; do
  out="$("$CTL" apply --minutes "$bad" 2>&1)"; rc=$?
  check "$rc" 1 "apply refuses --minutes [$bad]"
done
"$CTL" apply --minutes > /dev/null 2>&1; check "$?" 2 "apply --minutes without a value is a usage error"
"$CTL" apply --bogus > /dev/null 2>&1; check "$?" 2 "apply with an unknown option is a usage error"
"$CTL" bogus > /dev/null 2>&1; check "$?" 2 "an unknown command is a usage error"
"$CTL" status extra > /dev/null 2>&1; check "$?" 2 "status with an argument is a usage error"
mkdir -p "$ETC_ROOT/default"
echo "IDLE_MINUTES=99" > "$ENVF"
out="$("$CTL" apply --minutes 20 2>&1)"; rc=$?
check "$rc" 1 "apply refuses a settings file it did not write"
has "$out" "did not write it" "the refusal says why"
check "$(cat "$ENVF")" "IDLE_MINUTES=99" "the foreign settings file is untouched"
[ ! -s "$SUDO_LOG" ]; check "$?" 0 "refusals ran no privileged command"
rm -f "$ENVF"
out="$(PATH="$SANDBOX/bin:/nonexistent" /bin/bash "$CTL" apply 2>&1)"; rc=$?
check "$rc" 1 "apply refuses without node on the PATH"

# More refusals: a node under a private folder, an unreadable node, characters that break sed.
mkdir -p "$SANDBOX/home/me/bin" "$SANDBOX/fakebin"
chmod 755 "$SANDBOX/home" "$SANDBOX/home/me" "$SANDBOX/home/me/bin" "$SANDBOX/fakebin"
for d in home/me/bin fakebin; do printf '#!/bin/sh\nexit 0\n' > "$SANDBOX/$d/node"; chmod 755 "$SANDBOX/$d/node"; done
: > "$SUDO_LOG"
out="$(PATH="$SANDBOX/home/me/bin:$PATH" PRIVATE_DIRS="$SANDBOX/home" "$CTL" apply 2>&1)"; rc=$?
check "$rc" 1 "apply refuses a node under a home folder"
has "$out" "is under $SANDBOX/home" "the refusal names the folder"
chmod 700 "$SANDBOX/fakebin/node"
out="$(PATH="$SANDBOX/fakebin:$PATH" "$CTL" apply 2>&1)"; rc=$?
check "$rc" 1 "apply refuses a node others cannot run"
has "$out" "not readable and executable by others" "the refusal says why"
chmod 755 "$SANDBOX/fakebin/node"
mkdir -p "$SANDBOX/odd&dir"; chmod 755 "$SANDBOX/odd&dir"
cp "$SANDBOX/fakebin/node" "$SANDBOX/odd&dir/node"
out="$(PATH="$SANDBOX/odd&dir:$PATH" "$CTL" apply 2>&1)"; rc=$?
check "$rc" 1 "apply refuses a node path with & in it"
out="$(LIB_DIR="$SANDBOX/lib dir" "$CTL" apply 2>&1)"; rc=$?
check "$rc" 1 "apply refuses a LIB_DIR with a space in it"
for ch in '%' '$'; do
  out="$(LIB_DIR="$SANDBOX/lib${ch}dir" "$CTL" apply 2>&1)"; rc=$?
  check "$rc" 1 "apply refuses a LIB_DIR with $ch in it"
  mkdir -p "$SANDBOX/odd${ch}bin"; chmod 755 "$SANDBOX/odd${ch}bin"
  cp "$SANDBOX/fakebin/node" "$SANDBOX/odd${ch}bin/node"
  out="$(PATH="$SANDBOX/odd${ch}bin:$PATH" "$CTL" apply 2>&1)"; rc=$?
  check "$rc" 1 "apply refuses a node path with $ch in it"
done
[ ! -s "$SUDO_LOG" ]; check "$?" 0 "these refusals ran no privileged command"

# A symlinked node: ExecStart gets the real path, the one that was checked.
chmod 755 "$SANDBOX"
mkdir -p "$SANDBOX/linkbin"; chmod 755 "$SANDBOX/linkbin"
ln -s "$SANDBOX/fakebin/node" "$SANDBOX/linkbin/node"
REAL_NODE="$(readlink -f "$SANDBOX/fakebin/node")"
out="$(PATH="$SANDBOX/linkbin:$PATH" "$CTL" apply 2>&1)"; rc=$?
check "$rc" 0 "apply accepts a symlinked node whose real file is fine"
check "$(grep -c "^ExecStart=$REAL_NODE $LIB_DIR/idle-unload.mjs\$" "$UNIT_DIR/lemonade-idle-unload.service")" 1 "ExecStart holds the real path of a symlinked node"
lacks "$(cat "$UNIT_DIR/lemonade-idle-unload.service")" "$SANDBOX/linkbin" "ExecStart does not hold the link path"
"$CTL" revert > /dev/null 2>&1
: > "$SUDO_LOG"

# A non-default LIB_DIR lands in ExecStart.
ALT="$SANDBOX/alt/lib"
out="$(LIB_DIR="$ALT" "$CTL" apply 2>&1)"; rc=$?
check "$rc" 0 "apply with another LIB_DIR exits 0"
check "$(grep -c "^ExecStart=$NODE $ALT/idle-unload.mjs\$" "$UNIT_DIR/lemonade-idle-unload.service")" 1 "ExecStart points at the other LIB_DIR"
[ -e "$ALT/idle-unload.mjs" ]; check "$?" 0 "the script was installed there"
LIB_DIR="$ALT" "$CTL" revert > /dev/null 2>&1
rm -rf "$SANDBOX/alt"

# Apply with the default timeout.
out="$("$CTL" apply 2>&1)"; rc=$?
check "$rc" 0 "apply exits 0"
[ -e "$LIB_DIR/idle-unload.mjs" ] && [ -e "$UNIT_DIR/lemonade-idle-unload.timer" ] && [ -e "$UNIT_DIR/lemonade-idle-unload.service" ]
check "$?" 0 "apply installed the script and both units"
[ ! -e "$ENVF" ]; check "$?" 0 "apply without --minutes writes no settings file"
check "$(grep -c "^ExecStart=$NODE $LIB_DIR/idle-unload.mjs\$" "$UNIT_DIR/lemonade-idle-unload.service")" 1 "the service runs node on the installed script"
has "$(cat "$SUDO_LOG")" "systemctl enable --now lemonade-idle-unload.timer" "apply enabled the timer"
has "$out" "timer enabled: enabled" "apply ends with the status"

# Apply with a timeout, twice (the second run may overwrite its own file).
"$CTL" apply --minutes 30 > /dev/null 2>&1; check "$?" 0 "apply --minutes exits 0"
check "$(cat "$ENVF")" "IDLE_MINUTES=30" "apply wrote the settings file"
"$CTL" apply --minutes 45 > /dev/null 2>&1; check "$?" 0 "a second apply --minutes overwrites its own file"
check "$(cat "$ENVF")" "IDLE_MINUTES=45" "the second value is in place"
has "$("$CTL" status)" "idle minutes: 45" "status shows the configured timeout"

# Revert removes what apply installed and nothing else.
echo keep > "$UNIT_DIR/other.service"
: > "$SUDO_LOG"
"$CTL" revert > /dev/null 2>&1; check "$?" 0 "revert exits 0"
has "$(cat "$SUDO_LOG")" "systemctl disable lemonade-idle-unload.timer" "revert disables the timer"
has "$(cat "$SUDO_LOG")" "systemctl stop lemonade-idle-unload.timer" "revert stops the timer"
[ ! -e "$UNIT_DIR/lemonade-idle-unload.timer" ] && [ ! -e "$UNIT_DIR/lemonade-idle-unload.service" ] &&
  [ ! -e "$LIB_DIR/idle-unload.mjs" ] && [ ! -e "$LIB_DIR" ] && [ ! -e "$ENVF" ] && [ ! -e "$STATE_DIR" ]
check "$?" 0 "revert removed the units, the script, the settings file and the record"
check "$(cat "$UNIT_DIR/other.service")" keep "revert left another unit alone"

# systemctl stubs: the normal one, and ones that fail the subcommands named in FAIL_ON.
good_systemctl() {
  printf '%s\n' '#!/bin/sh' \
    '[ "$1" = is-enabled ] && { echo "${UNIT_STATE:-enabled}"; exit 0; }' \
    '[ "$1" = is-active ] && { echo "${UNIT_STATE:-active}"; exit 0; }' \
    'echo "systemctl $*" >> "$SUDO_LOG"' 'exit 0' > "$SANDBOX/bin/systemctl"
}
failing_systemctl() {
  printf '%s\n' '#!/bin/sh' \
    '[ "$1" = is-enabled ] && { echo enabled; exit 0; }' \
    '[ "$1" = is-active ] && { echo active; exit 0; }' \
    "case \" \$1 \" in *\" $1 \"*) echo \"systemctl \$*\" >> \"\$SUDO_LOG\"; echo \"Unit not loaded.\" >&2; exit 5 ;; esac" \
    'echo "systemctl $*" >> "$SUDO_LOG"' 'exit 0' > "$SANDBOX/bin/systemctl"
}

# Revert still removes everything when systemctl cannot stop the unit (it is not loaded).
"$CTL" apply --minutes 30 > /dev/null 2>&1
failing_systemctl stop
: > "$SUDO_LOG"
out="$("$CTL" revert 2>&1)"; rc=$?
check "$rc" 0 "revert exits 0 when stop fails"
has "$(cat "$SUDO_LOG")" "systemctl stop lemonade-idle-unload.service" "revert tried to stop the service"
[ ! -e "$UNIT_DIR/lemonade-idle-unload.timer" ] && [ ! -e "$UNIT_DIR/lemonade-idle-unload.service" ] &&
  [ ! -e "$LIB_DIR/idle-unload.mjs" ] && [ ! -e "$ENVF" ] && [ ! -e "$STATE_DIR" ]
check "$?" 0 "revert still removed the files"
has "$(cat "$SUDO_LOG")" "systemctl daemon-reload" "revert still reloaded systemd"

# A failing disable aborts the revert, with the files still in place.
good_systemctl
"$CTL" apply --minutes 30 > /dev/null 2>&1
failing_systemctl disable
: > "$SUDO_LOG"
out="$("$CTL" revert 2>&1)"; rc=$?
[ "$rc" -ne 0 ]; check "$?" 0 "revert exits non-zero when disable fails"
[ -e "$UNIT_DIR/lemonade-idle-unload.timer" ] && [ -e "$LIB_DIR/idle-unload.mjs" ]
check "$?" 0 "a failed disable leaves the files in place"
lacks "$(cat "$SUDO_LOG")" "daemon-reload" "a failed disable stops before the reload"
good_systemctl
"$CTL" revert > /dev/null 2>&1; check "$?" 0 "revert completes once disable works"

# A settings file the user edited after apply stays.
"$CTL" apply --minutes 30 > /dev/null 2>&1
echo "IDLE_MINUTES=10" > "$ENVF"
out="$("$CTL" revert 2>&1)"
[ -e "$ENVF" ]; check "$?" 0 "revert leaves a settings file changed since apply"
has "$out" "left in place" "revert says it left the settings file"
rm -f "$ENVF"

[ "$fails" -eq 0 ] || { echo "$fails failed"; exit 1; }
echo "all passed"
