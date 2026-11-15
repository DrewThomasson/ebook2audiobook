# GitHub Mobile on the laptop with Waydroid

GitHub Mobile has no desktop version, and its pull request review screens are the ones to
use. Waydroid runs Android in a container on a Wayland session, so GitHub Mobile runs in a
window on the laptop. The container uses about 1 to 2 GB of memory while it runs and almost
nothing when stopped.

`scripts/waydroid-setup.sh` does the steps that can be scripted. Run it from the repository.
Waydroid is not in the default Ubuntu repositories, so the script adds Waydroid's own apt
repository with its signing key.

## Steps

1. Check the machine. It reads only, and changes nothing. It needs a Wayland session and a
   kernel with binder support, and it exits 1 when either is missing:

   ```bash
   bash scripts/waydroid-setup.sh check
   ```

   Run it as yourself, not under sudo, since sudo drops the session type.

2. Add Waydroid's apt repository and install the package. This asks for sudo:

   ```bash
   bash scripts/waydroid-setup.sh install
   ```

   Add `--dry-run` before `install` to print each command without running it; it still
   reaches the repository and fetches the key into a temporary file. The script stops if it
   cannot reach the repository for this Ubuntu release. If `apt-get update` fails after the
   source is written, remove `/etc/apt/sources.list.d/waydroid.list` so later updates work.

3. Download the image with Google apps and restart the container service. This asks for
   sudo. Waydroid downloads the Android images from its own servers, which is a download
   outside apt, so run it only if that is acceptable:

   ```bash
   bash scripts/waydroid-setup.sh init
   ```

   If an image is already in place it does nothing, because forcing a new one removes the
   installed apps and the Google sign-in.

4. Start the session and show the window, as your own user. `waydroid session start` stays
   in the foreground, so run each command in its own terminal:

   ```bash
   waydroid session start
   ```

   ```bash
   waydroid show-full-ui
   ```

5. Register the device with Google so the Play Store lets it sign in. In a third terminal,
   print the device id:

   ```bash
   sudo waydroid shell -- sh -c "sqlite3 /data/data/*/*/gservices.db 'select value from main where name = \"android_id\";'"
   ```

   It prints only the number. If it prints nothing, the Google services have not started
   yet: open the Play Store in the Waydroid window once, then try again. Open
   <https://www.google.com/android/uncertified>, sign in, and paste the number. After a few
   minutes, run `waydroid session stop` and start the session again.

6. Open the Play Store in the Waydroid window, sign in, and install GitHub Mobile.

## Day to day

- Start with `waydroid session start` and `waydroid show-full-ui`, and stop with
  `waydroid session stop`. Stopping frees the memory.
- `sudo systemctl disable --now waydroid-container` stops the service from starting at boot.

## If it does not work

- Waydroid needs the kernel's binder support. `check` reports what it finds; the packaged
  Ubuntu kernel builds it as a module.
- Try the Files changed view on github.com (Feature preview), or the GitHub Pull Requests
  extension for VS Code.
