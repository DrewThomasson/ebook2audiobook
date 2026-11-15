#!/usr/bin/env bash
# Cases for waydroid-setup.sh. Stub sudo, apt-get, curl and lsb_release record or answer
# every call, and check reads fake /proc and /sys trees, so nothing on the machine is read
# or changed.
# usage: bash waydroid-setup_test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CTL="$HERE/waydroid-setup.sh"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

# sudo logs and runs its arguments; apt-get and systemctl and waydroid only log what they get;
# curl fails for a release listed in NO_RELEASE and otherwise writes a fake key to --output.
mkdir -p "$SANDBOX/bin"
printf '%s\n' '#!/bin/sh' 'echo "sudo $*" >> "$LOG"' 'exec "$@"' > "$SANDBOX/bin/sudo"
printf '%s\n' '#!/bin/sh' 'echo "tee $*" >> "$LOG"; cat >> "$LOG"' > "$SANDBOX/bin/tee"
printf '%s\n' '#!/bin/sh' 'echo "install $*" >> "$LOG"' > "$SANDBOX/bin/install"
for t in apt-get systemctl waydroid; do
  printf '%s\n' '#!/bin/sh' "echo \"$t \$*\" >> \"\$LOG\"" > "$SANDBOX/bin/$t"
done
printf '%s\n' '#!/bin/sh' 'echo "${RELEASE:-resolute}"' > "$SANDBOX/bin/lsb_release"
printf '%s\n' '#!/bin/sh' \
  'for a in "$@"; do case "$a" in */dists/"$NO_RELEASE"/*) exit 22 ;; */waydroid.gpg) [ -n "${KEY_FAIL:-}" ] && exit 22 ;; esac; done' \
  'while [ $# -gt 0 ]; do [ "$1" = --output ] && echo key > "$2"; shift; done; exit 0' \
  > "$SANDBOX/bin/curl"
chmod +x "$SANDBOX"/bin/*
export PATH="$SANDBOX/bin:$PATH"
export LOG="$SANDBOX/calls.log"
export NO_RELEASE="none"
export REPO_URL="https://repo.example"

pass=0
fail=0
ok() { pass=$((pass + 1)); }
bad() { fail=$((fail + 1)); echo "FAIL: $1"; }
expect_has() { grep -qF -- "$2" <<<"$1" && ok || bad "missing '$2' in: $1"; }
expect_lacks() { grep -qF -- "$2" <<<"$1" && bad "unexpected '$2' in: $1" || ok; }

# A fake /proc and /sys: binder in the filesystems, an AMD card, 4096 MB available.
mkdir -p "$SANDBOX/proc" "$SANDBOX/sys/class/drm/card0/device"
printf 'nodev\tbinder\n' > "$SANDBOX/proc/filesystems"
printf 'MemAvailable:    4194304 kB\n' > "$SANDBOX/proc/meminfo"
echo 0x1002 > "$SANDBOX/sys/class/drm/card0/device/vendor"
export PROC_ROOT="$SANDBOX/proc" SYS_ROOT="$SANDBOX/sys"
export KERNEL_CONFIG="$SANDBOX/kernel-config" WAYDROID_DIR="$SANDBOX/waydroid"

# check on a Wayland session reads everything and changes nothing.
out="$(XDG_SESSION_TYPE=wayland bash "$CTL" check 2>&1)"; status=$?
[ "$status" = 0 ] && ok || bad "check exit $status"
expect_has "$out" "ok: the session is Wayland"
expect_has "$out" "ok: the kernel has binder"
expect_has "$out" "ok: the graphics are AMD"
expect_has "$out" "4096 MB of memory available"
[ ! -e "$LOG" ] && ok || bad "check called a privileged command"

# check on an X11 session fails and says why.
out="$(XDG_SESSION_TYPE=x11 bash "$CTL" check 2>&1)"; status=$?
[ "$status" = 1 ] && ok || bad "x11 check exit $status"
expect_has "$out" "needs a Wayland session"

# --dry-run install prints each privileged command and runs none of them.
rm -f "$LOG"
out="$(bash "$CTL" --dry-run install 2>&1)"; status=$?
[ "$status" = 0 ] && ok || bad "dry-run install exit $status"
expect_has "$out" "+ install -m 644"
expect_has "$out" "deb [signed-by=/usr/share/keyrings/waydroid.gpg] https://repo.example/ resolute main"
expect_has "$out" "+ apt-get install -y waydroid"
[ ! -e "$LOG" ] && ok || bad "dry-run install ran a command"

# install adds the key, the source and the package through sudo.
rm -f "$LOG"
bash "$CTL" install >/dev/null 2>&1; status=$?
[ "$status" = 0 ] && ok || bad "install exit $status"
calls="$(cat "$LOG")"
expect_has "$calls" "sudo install -m 644"
expect_has "$calls" "sudo tee /etc/apt/sources.list.d/waydroid.list"
expect_has "$calls" "sudo apt-get update"
expect_has "$calls" "sudo apt-get install -y waydroid"

# A release the repository has no files for stops install before it changes anything.
rm -f "$LOG"
out="$(RELEASE=future NO_RELEASE=future bash "$CTL" install 2>&1)"; status=$?
[ "$status" = 1 ] && ok || bad "unsupported release exit $status"
expect_has "$out" "Could not reach https://repo.example/dists/future/Release"
expect_has "$out" "Nothing was changed."
[ ! -e "$LOG" ] && ok || bad "unsupported release changed something"

# init uses the Google apps image and enables the container service.
rm -f "$LOG"
out="$(bash "$CTL" init 2>&1)"; status=$?
[ "$status" = 0 ] && ok || bad "init exit $status"
calls="$(cat "$LOG")"
expect_has "$calls" "sudo waydroid init -s GAPPS"
expect_lacks "$calls" " -f"
expect_has "$calls" "sudo systemctl enable waydroid-container"
expect_has "$calls" "sudo systemctl restart waydroid-container"
expect_lacks "$calls" "apt-get"

# With an image in place, init does not download or force another, and still restarts.
mkdir -p "$WAYDROID_DIR/images"
touch "$WAYDROID_DIR/images/system.img"
rm -f "$LOG"
out="$(bash "$CTL" init 2>&1)"; status=$?
[ "$status" = 0 ] && ok || bad "init with an image exit $status"
expect_has "$out" "An image is already in place"
calls="$(cat "$LOG")"
expect_lacks "$calls" "waydroid init"
expect_has "$calls" "sudo systemctl restart waydroid-container"
rm -rf "$WAYDROID_DIR"

# The real install writes the exact source line, and the key is installed first.
rm -f "$LOG"
bash "$CTL" install >/dev/null 2>&1
calls="$(cat "$LOG")"
expect_has "$calls" "deb [signed-by=/usr/share/keyrings/waydroid.gpg] https://repo.example/ resolute main"

# A key download that fails stops install before anything is written.
rm -f "$LOG"
KEY_FAIL=1 bash "$CTL" install >/dev/null 2>&1; status=$?
[ "$status" != 0 ] && ok || bad "failed key fetch exit $status"
[ ! -e "$LOG" ] && ok || bad "failed key fetch changed something"

# check fails without binder anywhere, and passes when the kernel config builds it.
rm -f "$PROC_ROOT/filesystems"
out="$(XDG_SESSION_TYPE=wayland bash "$CTL" check 2>&1)"; status=$?
[ "$status" = 1 ] && ok || bad "no binder exit $status"
expect_has "$out" "problem: the kernel has no binder support"
echo "CONFIG_ANDROID_BINDER_IPC=m" > "$KERNEL_CONFIG"
out="$(XDG_SESSION_TYPE=wayland bash "$CTL" check 2>&1)"; status=$?
[ "$status" = 0 ] && ok || bad "config binder exit $status"
expect_has "$out" "ok: the kernel has binder"

# A card that is not AMD alongside one that is still reads AMD; no AMD card is a note.
mkdir -p "$SYS_ROOT/class/drm/card1/device"
echo 0x8086 > "$SYS_ROOT/class/drm/card0/device/vendor"
echo 0x1002 > "$SYS_ROOT/class/drm/card1/device/vendor"
out="$(XDG_SESSION_TYPE=wayland bash "$CTL" check 2>&1)"
expect_has "$out" "ok: the graphics are AMD"
echo 0x8086 > "$SYS_ROOT/class/drm/card1/device/vendor"
out="$(XDG_SESSION_TYPE=wayland bash "$CTL" check 2>&1)"
expect_has "$out" "note: no AMD graphics device"

# Memory that cannot be read, or is low, is a note and not an ok.
rm -f "$PROC_ROOT/meminfo"
out="$(XDG_SESSION_TYPE=wayland bash "$CTL" check 2>&1)"
expect_has "$out" "note: unknown MB of memory available"

# No subcommand, or an unknown one, prints usage and exits 2.
bash "$CTL" >/dev/null 2>&1; [ "$?" = 2 ] && ok || bad "no subcommand exit"
bash "$CTL" remove >/dev/null 2>&1; [ "$?" = 2 ] && ok || bad "unknown subcommand exit"

echo "waydroid-setup_test: $pass passed, $fail failed"
[ "$fail" = 0 ]
