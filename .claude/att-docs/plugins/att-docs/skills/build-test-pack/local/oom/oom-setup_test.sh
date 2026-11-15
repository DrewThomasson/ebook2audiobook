#!/usr/bin/env bash
# Cases for oom-setup.sh. A stub sudo runs its command inside a sandbox, and a stub
# systemctl records what it is asked, so nothing on the machine is read or changed.
# usage: bash oom-setup_test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CTL="$HERE/oom-setup.sh"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

# Stubs: sudo logs and runs its arguments; systemctl logs what it gets, and answers show
# from UNIT_ADJ, UNIT_PREF, SLICE_HIGH and UNIT_SLICE.
mkdir -p "$SANDBOX/bin"
printf '%s\n' '#!/bin/sh' 'echo "sudo $*" >> "$CALL_LOG"' 'exec "$@"' > "$SANDBOX/bin/sudo"
cat > "$SANDBOX/bin/systemctl" <<'STUB'
#!/bin/sh
echo "systemctl $*" >> "$CALL_LOG"
if [ "$1" = --user ]; then shift; user=1; else user=0; fi
if [ "$1" = show ]; then
  case "$3" in
    OOMScoreAdjust) echo "OOMScoreAdjust=${UNIT_ADJ:-0}" ;;
    ManagedOOMPreference) echo "ManagedOOMPreference=${UNIT_PREF:-none}" ;;
    MemoryHigh) echo "MemoryHigh=${SLICE_HIGH:-infinity}" ;;
    Slice) echo "Slice=${UNIT_SLICE:-app.slice}" ;;
  esac
fi
exit 0
STUB
chmod +x "$SANDBOX"/bin/*
export PATH="$SANDBOX/bin:$PATH"
export CALL_LOG="$SANDBOX/calls.log"
export UNIT_DIR="$SANDBOX/etc/systemd/system"
export USER_UNIT_DIR="$SANDBOX/home/.config/systemd/user"
export PROC_ROOT="$SANDBOX/proc"
MODEL="$UNIT_DIR/lemonade-server.service.d/99-build-pack-oom.conf"
APPS="$USER_UNIT_DIR/app.slice.d/50-build-pack-apps.conf"
SLICE="$USER_UNIT_DIR/build-pack.slice"
SLICEDROP="$USER_UNIT_DIR/build-pack.service.d/50-build-pack-slice.conf"
: > "$CALL_LOG"
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
calls() { cat "$CALL_LOG"; }

# A fake llama-server and an unrelated process.
mkdir -p "$PROC_ROOT/100" "$PROC_ROOT/200"
echo llama-server > "$PROC_ROOT/100/comm"
echo 0 > "$PROC_ROOT/100/oom_score_adj"
echo "0::/system.slice/lemonade-server.service" > "$PROC_ROOT/100/cgroup"
echo bash > "$PROC_ROOT/200/comm"
echo 0 > "$PROC_ROOT/200/oom_score_adj"

# Nothing installed.
out="$("$CTL" status 2>&1)"; rc=$?
check "$rc" 0 "status exits 0 with nothing installed"
has "$out" "missing:   $MODEL" "status lists the missing model drop-in"
has "$out" "llama-server 100: oom_score_adj 0, cgroup 0::/system.slice/lemonade-server.service" "status lists llama-server"
lacks "$out" "bash" "status ignores other processes"
lacks "$out" "restart needed" "no restart note while the unit has the default"
out="$("$CTL" revert all 2>&1)"; rc=$?
check "$rc" 0 "revert exits 0 with nothing installed"
has "$out" "nothing to revert" "revert with nothing installed says so"

# Dry run changes nothing.
: > "$CALL_LOG"
out="$("$CTL" --dry-run apply model --restart 2>&1)"; rc=$?
check "$rc" 0 "dry-run apply model exits 0"
has "$out" "+ sudo install -m 0644 $HERE/99-build-pack-oom.conf $MODEL" "dry-run installs the drop-in"
has "$out" "+ sudo systemctl restart lemonade-server.service" "dry-run shows the restart"
[ ! -e "$UNIT_DIR" ] && [ ! -s "$CALL_LOG" ]
check "$?" 0 "dry-run wrote nothing and ran nothing"
: > "$CALL_LOG"
out="$("$CTL" --dry-run apply apps --high 24G 2>&1)"; rc=$?
check "$rc" 0 "dry-run apply apps exits 0"
[ ! -e "$USER_UNIT_DIR" ] && [ ! -s "$CALL_LOG" ]
check "$?" 0 "dry-run apps wrote nothing and ran nothing"

# Usage and refusals.
"$CTL" bogus > /dev/null 2>&1; check "$?" 2 "an unknown command is a usage error"
"$CTL" apply > /dev/null 2>&1; check "$?" 2 "apply without a target is a usage error"
"$CTL" apply model --bogus > /dev/null 2>&1; check "$?" 2 "apply model with an unknown option is a usage error"
"$CTL" apply apps > /dev/null 2>&1; check "$?" 2 "apply apps without --high is a usage error"
"$CTL" revert > /dev/null 2>&1; check "$?" 2 "revert without a target is a usage error"
"$CTL" revert bogus > /dev/null 2>&1; check "$?" 2 "revert of an unknown target is a usage error"
for bad in 0 -3 1.5 24 abc 100% 0% 24GB; do
  "$CTL" apply apps --high "$bad" > /dev/null 2>&1
  check "$?" 1 "apply apps refuses --high [$bad]"
done
"$CTL" apply apps --high "" > /dev/null 2>&1; check "$?" 2 "apply apps with an empty --high is a usage error"
[ ! -e "$USER_UNIT_DIR" ] && [ ! -s "$CALL_LOG" ]
check "$?" 0 "refusals changed nothing"

# apply model installs the drop-in and does not restart.
mkdir -p "$UNIT_DIR/lemonade-server.service.d"
echo "[Service]" > "$UNIT_DIR/lemonade-server.service.d/memlock.conf"
out="$("$CTL" apply model 2>&1)"; rc=$?
check "$rc" 0 "apply model exits 0"
check "$(cat "$MODEL")" "$(cat "$HERE/99-build-pack-oom.conf")" "the drop-in has the shipped contents"
has "$(cat "$MODEL")" "OOMScoreAdjust=-500" "the drop-in sets the score"
has "$(cat "$MODEL")" "ManagedOOMPreference=avoid" "the drop-in sets the preference"
has "$(calls)" "systemctl daemon-reload" "apply model reloads systemd"
lacks "$(calls)" "restart" "apply model does not restart"
has "$out" "restart pending" "apply model says a restart is pending"
check "$(cat "$UNIT_DIR/lemonade-server.service.d/memlock.conf")" "[Service]" "memlock.conf is untouched"

# A restart needs the flag.
: > "$CALL_LOG"
"$CTL" apply model --restart > /dev/null 2>&1; check "$?" 0 "apply model --restart exits 0"
has "$(calls)" "systemctl restart lemonade-server.service" "--restart restarts the unit"

# Status flags a running process that differs from the unit.
out="$(UNIT_ADJ=-500 UNIT_PREF=avoid "$CTL" status 2>&1)"
has "$out" "installed: $MODEL" "status shows the installed drop-in"
has "$out" "OOMScoreAdjust: -500" "status shows the unit's score"
has "$out" "restart needed" "status flags a llama-server that still has the old score"
echo -500 > "$PROC_ROOT/100/oom_score_adj"
out="$(UNIT_ADJ=-500 "$CTL" status 2>&1)"
lacks "$out" "restart needed" "no restart note once the process matches"

# A llama-server outside the service's control group is not a restart candidate.
echo 0 > "$PROC_ROOT/100/oom_score_adj"
echo "0::/user.slice/user-1000.slice/app.scope" > "$PROC_ROOT/100/cgroup"
out="$(UNIT_ADJ=-500 "$CTL" status 2>&1)"
lacks "$out" "restart needed" "no restart note for a llama-server outside the unit"
echo -500 > "$PROC_ROOT/100/oom_score_adj"
echo "0::/system.slice/lemonade-server.service" > "$PROC_ROOT/100/cgroup"

# Status skips the template unit, which systemctl cannot show.
out="$("$CTL" status 2>&1)"
has "$out" "build-pack.service slice:" "status shows a plain build-pack unit"
lacks "$out" "build-pack-now@.service slice:" "status skips the template unit"

# A drop-in this script did not write is refused.
rm -f "$MODEL"
echo "[Service]" > "$MODEL"
out="$("$CTL" apply model 2>&1)"; rc=$?
check "$rc" 1 "apply model refuses a drop-in it did not write"
has "$out" "did not write it" "the refusal says why"
check "$(cat "$MODEL")" "[Service]" "the foreign drop-in is untouched"
out="$("$CTL" revert model 2>&1)"
has "$out" "left in place" "revert leaves a foreign drop-in"
[ -e "$MODEL" ]; check "$?" 0 "the foreign drop-in is still there"
rm -f "$MODEL"

# apply apps.
: > "$CALL_LOG"
"$CTL" apply apps --high 24G > /dev/null 2>&1; check "$?" 0 "apply apps exits 0"
has "$(cat "$APPS")" "MemoryHigh=24G" "the app.slice drop-in has the limit"
lacks "$(cat "$APPS")" "MemoryMax" "the limit throttles and never kills"
[ -f "$SLICE" ] && [ -f "$SLICEDROP" ] && [ -f "$USER_UNIT_DIR/build-pack-now@.service.d/50-build-pack-slice.conf" ]
check "$?" 0 "the build-pack slice and unit drop-ins are installed"
has "$(cat "$SLICEDROP")" "Slice=build-pack.slice" "a build-pack unit moves to its slice"
has "$(calls)" "systemctl --user daemon-reload" "apply apps reloads the user manager"
lacks "$(calls)" "sudo" "apply apps needs no root"
"$CTL" apply apps --high 40% > /dev/null 2>&1; check "$?" 0 "apply apps takes a percentage"
has "$(cat "$APPS")" "MemoryHigh=40%" "the new limit replaces the old"
out="$(SLICE_HIGH=25769803776 UNIT_SLICE=build-pack.slice "$CTL" status 2>&1)"
has "$out" "app.slice MemoryHigh: 25769803776" "status shows the app.slice limit"
has "$out" "build-pack.service slice: build-pack.slice" "status shows a build-pack unit's slice"

# revert apps removes only marked files.
echo "[Service]" > "$SLICEDROP"
out="$("$CTL" revert apps 2>&1)"; rc=$?
check "$rc" 0 "revert apps exits 0"
[ ! -e "$APPS" ] && [ ! -e "$SLICE" ] && [ ! -e "$USER_UNIT_DIR/build-pack-now@.service.d" ]
check "$?" 0 "revert apps removes what apply installed"
has "$out" "$SLICEDROP was not written by this script; left in place" "revert apps keeps an edited drop-in"
check "$(cat "$SLICEDROP")" "[Service]" "the edited drop-in is untouched"

# revert all after a model apply.
"$CTL" apply model > /dev/null 2>&1
"$CTL" revert all > /dev/null 2>&1; check "$?" 0 "revert all exits 0"
[ ! -e "$MODEL" ] && [ -e "$UNIT_DIR/lemonade-server.service.d/memlock.conf" ]
check "$?" 0 "revert removes the drop-in and keeps memlock.conf"

# Foreign apps files are refused, and a dry-run revert removes nothing.
rm -f "$SLICEDROP"
mkdir -p "$USER_UNIT_DIR/app.slice.d"
echo "[Slice]" > "$APPS"
out="$("$CTL" apply apps --high 8G 2>&1)"; rc=$?
check "$rc" 1 "apply apps refuses an app.slice drop-in it did not write"
check "$(cat "$APPS")" "[Slice]" "the foreign app.slice drop-in is untouched"
[ ! -e "$SLICE" ]; check "$?" 0 "a refused apply apps installs nothing"
rm -f "$APPS"
"$CTL" apply apps --high 1% > /dev/null 2>&1; check "$?" 0 "apply apps takes 1%"
"$CTL" apply apps --high 99% > /dev/null 2>&1; check "$?" 0 "apply apps takes 99%"
: > "$CALL_LOG"
out="$("$CTL" --dry-run revert all 2>&1)"
[ -f "$APPS" ] && [ ! -s "$CALL_LOG" ]; check "$?" 0 "dry-run revert removes nothing"
out="$("$CTL" revert all 2>&1)"
has "$out" "model: not applied" "revert all with only the apps files says the model is not applied"
has "$out" "keep build-pack.slice until they restart" "revert apps notes running units keep their slice"
[ ! -e "$APPS" ] && [ ! -e "$SLICE" ]; check "$?" 0 "revert all removes the apps files"

if [ "$fails" -ne 0 ]; then echo "$fails failed"; exit 1; fi
echo "all passed"
