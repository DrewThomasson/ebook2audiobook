#!/usr/bin/env bash
# Waydroid setup for running GitHub Mobile on a Wayland Ubuntu machine.
#
# usage: waydroid-setup.sh [--dry-run] check
#        waydroid-setup.sh [--dry-run] install
#        waydroid-setup.sh [--dry-run] init
#
# check    Reads the session type, the kernel's binder support, the graphics vendors, the
#          memory and whether Waydroid is installed. Needs no root and changes nothing.
#          Exits 1 when the session is not Wayland or the kernel has no binder.
# install  Adds Waydroid's own apt repository with its signing key, then installs the
#          waydroid package from it. Stops first if the repository cannot be reached for
#          this Ubuntu release. The package comes through apt; the key is the only file
#          fetched directly, from the same vendor host.
# init     Downloads the Android image with Google apps (waydroid does this from its own
#          servers, outside apt) and restarts the container service. If an image is already
#          in place it does nothing, since forcing a new one removes the installed apps and
#          the Google sign-in. The Play Store sign-in and the device registration with Google
#          are done by hand, as docs/waydroid/README.md describes.
# --dry-run  Prints each privileged command instead of running it. install still reaches
#          the repository and fetches the key into a temporary file.
#
# PROC_ROOT and SYS_ROOT (default /proc and /sys) set where check reads from, KERNEL_CONFIG
# the kernel config it reads, and WAYDROID_DIR (default /var/lib/waydroid) where init looks
# for an existing image.
set -euo pipefail

REPO_URL="${REPO_URL:-https://repo.waydro.id}"
KEYRING="/usr/share/keyrings/waydroid.gpg"
SOURCES="/etc/apt/sources.list.d/waydroid.list"
PROC_ROOT="${PROC_ROOT:-/proc}"
SYS_ROOT="${SYS_ROOT:-/sys}"
KERNEL_CONFIG="${KERNEL_CONFIG:-/boot/config-$(uname -r)}"
WAYDROID_DIR="${WAYDROID_DIR:-/var/lib/waydroid}"

dry=0
if [ "${1:-}" = "--dry-run" ]; then
  dry=1
  shift
fi

usage() {
  echo "usage: $0 [--dry-run] check|install|init" >&2
  exit 2
}

# Runs a privileged command, or prints it with --dry-run.
priv() {
  if [ "$dry" = 1 ]; then
    echo "+ $*"
  else
    sudo "$@"
  fi
}

check() {
  local ok=0 session vendor mem found=0
  session="${XDG_SESSION_TYPE:-unknown}"
  if [ "$session" = wayland ]; then
    echo "ok: the session is Wayland"
  else
    echo "problem: the session is $session; Waydroid needs a Wayland session"
    ok=1
  fi
  # Binder is either loaded now or built for this kernel, as a module or in.
  if grep -qs binder "$PROC_ROOT/filesystems" || [ -e "$SYS_ROOT/module/binder_linux" ] \
    || grep -qsE '^CONFIG_ANDROID_BINDER_IPC=(y|m)' "$KERNEL_CONFIG"; then
    echo "ok: the kernel has binder"
  else
    echo "problem: the kernel has no binder support, which Waydroid needs"
    ok=1
  fi
  for vendor in "$SYS_ROOT"/class/drm/card*/device/vendor; do
    [ -r "$vendor" ] && [ "$(cat "$vendor")" = "0x1002" ] && found=1
  done
  if [ "$found" = 1 ]; then
    echo "ok: the graphics are AMD"
  else
    echo "note: no AMD graphics device (vendor 0x1002) was found"
  fi
  mem="$(awk '/^MemAvailable:/ { printf "%d", $2 / 1024 }' "$PROC_ROOT/meminfo" 2>/dev/null || true)"
  if [ -n "$mem" ] && [ "$mem" -ge 2048 ]; then
    echo "ok: $mem MB of memory available; Waydroid uses about 1 to 2 GB while it runs"
  else
    echo "note: ${mem:-unknown} MB of memory available; Waydroid uses about 1 to 2 GB while it runs"
  fi
  if command -v waydroid >/dev/null 2>&1; then
    echo "ok: waydroid is installed"
  else
    echo "note: waydroid is not installed; run install"
  fi
  return "$ok"
}

install_waydroid() {
  local codename
  codename="$(lsb_release -cs)"
  if ! curl -fsSI "$REPO_URL/dists/$codename/Release" >/dev/null 2>&1; then
    echo "Could not reach $REPO_URL/dists/$codename/Release: the repository has no files for" >&2
    echo "the Ubuntu release $codename, or the network is down. Nothing was changed." >&2
    exit 1
  fi
  KEY_FILE="$(mktemp)"
  trap 'rm -f "$KEY_FILE"' EXIT
  curl -fsSL "$REPO_URL/waydroid.gpg" --output "$KEY_FILE"
  priv install -m 644 "$KEY_FILE" "$KEYRING"
  if [ "$dry" = 1 ]; then
    echo "+ write $SOURCES: deb [signed-by=$KEYRING] $REPO_URL/ $codename main"
  else
    echo "deb [signed-by=$KEYRING] $REPO_URL/ $codename main" | sudo tee "$SOURCES" >/dev/null
  fi
  priv apt-get update
  priv apt-get install -y waydroid
}

init_waydroid() {
  if [ -e "$WAYDROID_DIR/images/system.img" ]; then
    echo "An image is already in place in $WAYDROID_DIR/images, so init did nothing."
    echo "Forcing a new one with 'sudo waydroid init -f' removes the installed apps and the"
    echo "Google sign-in."
  else
    priv waydroid init -s GAPPS
  fi
  priv systemctl enable waydroid-container
  priv systemctl restart waydroid-container
  echo "Next: in one terminal run 'waydroid session start', and in a second run"
  echo "'waydroid show-full-ui'. Then register the device with Google and sign in to the"
  echo "Play Store (docs/waydroid/README.md)."
}

case "${1:-}" in
  check) check ;;
  install) install_waydroid ;;
  init) init_waydroid ;;
  *) usage ;;
esac
