# ebook2audiobook for Nix

`package.nix` is the nixpkgs package of ebook2audiobook: in nixpkgs it lives at
`pkgs/by-name/eb/ebook2audiobook/package.nix`. `../flake.nix` builds the same file from this checkout.

- [How it works](#how-it-works)
- [Install Nix](#install-nix)
- [Build and run](#build-and-run)
- [Update to a new release](#update-to-a-new-release)
- [Submit to nixpkgs](#submit-to-nixpkgs)
- [Known limits](#known-limits)

## How it works

ebook2audiobook installs itself at its first start: its launcher installs python with uv, the PyTorch wheels
of the detected GPU and the TTS engines next to `app.py`, which cannot happen in the read-only `/nix/store`.
So the package:

- builds the pip bootstrap (`tools/pip_bootstrap`) with the app files,
- runs it in a `buildFHSEnv` holding every program of the launcher's `HOST_PROGRAMS` (calibre, ffmpeg,
  espeak-ng, tesseract, uv...) and the shared libraries of the PyPI wheels (as in the `Dockerfile`), so the
  launcher never calls a package manager,
- ships the menu entry and the icons, and sets `E2A_NO_DESKTOP_ENTRY=1` so the launcher does not write its
  own entry, which would start it outside the FHS env.

The `ebook2audiobook` command copies the app files to `~/ebook2audiobook` (or `$E2A_HOME`) and starts the
launcher there, exactly as a pip install does: the first start downloads several GB into that folder.

Linux only (x86_64, aarch64): calibre and `buildFHSEnv` are Linux only in nixpkgs.

## Install Nix

**Fedora**: Nix is packaged by Fedora. `nix-daemon` brings the multi-user daemon, `nix-legacy` the classic
commands (`nix-build`, `nix-shell`...):
```bash
sudo dnf install nix nix-daemon nix-legacy
```
```bash
sudo systemctl enable --now nix-daemon.socket
```

**Other distributions**: the official installer (https://nixos.org/download), multi-user with systemd:
```bash
sh <(curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install) --daemon
```
If it stops on `groupadd: GID '30000' already exists`, rerun it with free ids, i.e.
`NIX_BUILD_GROUP_ID=30100 NIX_FIRST_BUILD_UID=30101` in front of `sh`.

**Then**, enable flakes (needed by `nix build`, `nix run` and the flake) and open a new terminal:
```bash
mkdir -p ~/.config/nix && echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

## Build and run

### From this checkout (flake)

Builds `package.nix` from this checkout at the version of `../VERSION.txt`, with the nixpkgs pinned in
`../flake.lock` (`nix flake update` refreshes it). From the repository root:
```bash
nix build
```
```bash
./result/bin/ebook2audiobook --version
```
Or run it straight from GitHub, without cloning:
```bash
nix run github:DrewThomasson/ebook2audiobook
```

### package.nix as nixpkgs builds it (release tag)

From the repository root, with nixpkgs taken from its channel:
```bash
nix-build -I nixpkgs=channel:nixos-unstable -E 'with import <nixpkgs> {}; callPackage ./nix/package.nix {}'
```
Or in a nixpkgs checkout:
```bash
mkdir -p pkgs/by-name/eb/ebook2audiobook
```
```bash
cp ../ebook2audiobook/nix/package.nix pkgs/by-name/eb/ebook2audiobook/package.nix
```
```bash
nix-build -A ebook2audiobook
```

### Test

```bash
./result/bin/ebook2audiobook --version
```
A headless conversion with a test ebook of this repository, from its root: the test ebooks are not copied to
`~/ebook2audiobook`, and a relative path is read from the folder the command is typed in. The first conversion
downloads python, torch and the models:
```bash
./result/bin/ebook2audiobook --headless --ebook ebooks/tests/test_eng.txt --language eng --tts_engine piper
```
The GUI: `./result/bin/ebook2audiobook` then http://localhost:7860.
`ebook2audiobook --uninstall` removes `~/ebook2audiobook` (or `$E2A_HOME`) and everything in it.

## Update to a new release

`package.nix` fetches a release tag of `DrewThomasson/ebook2audiobook` with the hash of its content. A tag
cannot hold the hash of its own content, so the copy in this repository always points at the previous
release: the copy in nixpkgs is the one that counts.

1. Release first: bump `VERSION.txt` and the other version files, merge into `DrewThomasson/ebook2audiobook`
   `main` and tag it there (`v<version>`).
2. In `package.nix`, set the new version and empty the hash:
   ```nix
     version = "26.11.17";
   ```
   ```nix
       hash = "";
   ```
3. Build: it fails on purpose and prints the hash of the tag on its `got:` line.
   ```bash
   nix-build -A ebook2audiobook
   ```
4. Paste that value into `hash = "...";`, build again and test:
   ```bash
   nix-build -A ebook2audiobook && ./result/bin/ebook2audiobook --version
   ```
5. Commit. In nixpkgs: `ebook2audiobook: 26.11.16 -> 26.11.17` (`ebook2audiobook: init at <version>` for the
   first submission). Here: `nix: package.nix at 26.11.17`.

Once the package is in nixpkgs, its `passthru.updateScript` lets the nixpkgs update bot open these update
pull requests by itself: check the version, test it, approve.

## Submit to nixpkgs

1. Sync your nixpkgs fork with `master`, then branch: `git switch -c ebook2audiobook-init`.
2. Add yourself to `maintainers/maintainer-list.nix` (alphabetical order, `githubId` is your numeric
   GitHub id) and commit it alone: `maintainers: add <handle>`.
3. Copy `package.nix` as above, set `maintainers = with lib.maintainers; [ <handle> ];`, build, test and
   commit: `ebook2audiobook: init at <version>`.
4. Optionally, build the change as reviewers will. From the nixpkgs checkout, `-I nixpkgs=.` takes
   nixpkgs-review from the checkout itself, so no channel is needed:
   ```bash
   nix-shell -I nixpkgs=. -p nixpkgs-review --run "nixpkgs-review rev HEAD"
   ```
5. Push the branch to your fork and open a pull request to `NixOS/nixpkgs` `master` titled
   `ebook2audiobook: init at <version>`, with the template filled in (platform built on, basic
   functionality tested). Expect review questions on the downloads of the first start: `unsloth-desktop`
   in nixpkgs is packaged the same way.

## Known limits

- **Folder path**: piper's espeak-ng cannot read its data past 159 bytes, so the path of `~/ebook2audiobook`
  (or `$E2A_HOME`) must be 98 bytes at most (a non-ASCII character takes 2 to 4): the launcher stops in a
  longer one.
- **NVIDIA GPU outside NixOS**: the FHS env hides the system's `/usr`, where other distributions keep the
  NVIDIA driver libraries, so expect CPU conversion. On NixOS the drivers in `/run/opengl-driver` are seen.
- **Ubuntu 24.04 and later**: AppArmor restricts the user namespaces `buildFHSEnv` needs, which can stop
  the FHS env from starting.
- **Crash reports** are on by default (anonymized, sent to the maintainers): `DO_NOT_TRACK=1` turns them off.
