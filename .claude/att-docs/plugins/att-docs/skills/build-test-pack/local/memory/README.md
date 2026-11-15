# Memory setup for the model host

Two optional changes make swapping cheaper on the machine that runs the local model
(MTabletPC: about 57 GiB RAM, two disk swap files of 8 GiB and 12 GiB, `vm.swappiness` 60,
no zram). On the overnight build of October 29, about 14 GiB sat in swap, but those pages were
cold: swap-in stayed low and speeds held. The expected gain is small, so measure before keeping
anything.

- **Lower swappiness** (`99-zz-build-pack-swappiness.conf`) sets `vm.swappiness` to 10.
  Swappiness weighs reclaiming anonymous memory (written to swap) against reclaiming
  file-backed page cache (dropped and re-read from disk). A low value makes the kernel drop
  page cache before it swaps anonymous pages. On this host `llama-server` runs with
  `--no-mmap` and its weights sit in the GPU's GTT pool, so the model's weights are not
  file-backed page cache that a low value would drop. The `zz` in the file name sorts it after
  the other `/etc/sysctl.d` files, so at boot, in systemd-sysctl's order, it wins over them.
  procps `sysctl --system` applies `/etc/sysctl.conf` last, so a `vm.swappiness` line in that
  file would still override it. On this host no file sets `vm.swappiness`, so the value before
  the change is the kernel default, 60. The script saves the live value before it installs
  the drop-in.
- **zram swap** (`zram-generator.conf`) adds a compressed swap device in RAM, sized at a quarter
  of RAM up to 8 GiB, with priority 100 so it fills before the disk swap files (their priorities
  are negative, both -1 on this host). Swapping to it is much faster than to disk. The Ubuntu package ships its own default
  at `/usr/lib/systemd/zram-generator.conf`, which turns on zram0 at half of RAM up to 4 GiB;
  this folder's config in `/etc` overrides it.

The two are separate experiments. A low swappiness works against a swap device in RAM, so
do not run them together.

## Order

1. Run `./memory-setup.sh status` and save the output.
2. Run `./memory-setup.sh swappiness`, run a build, and compare against an earlier build.
3. Run `./memory-setup.sh revert swappiness`.
4. Only if swap still costs time, run `./memory-setup.sh zram` at the default swappiness,
   build again, and compare. Keep it or run `./memory-setup.sh revert zram`.

Add `--dry-run` to any command to print the privileged commands without running them.

The zram step runs in this order:

1. Check for conflicts (below). Nothing is changed if any check fails.
2. Install this folder's `zram-generator.conf` to `/etc/systemd/zram-generator.conf`.
3. If `systemd-zram-generator` is not installed, run `apt-get update` and
   `apt-get install -y systemd-zram-generator`, and record the install (see State). The
   config is written first so that the first generator run sees it. The
   package is in Ubuntu's universe component, so universe must be enabled.
4. `systemctl daemon-reload`.
5. `systemctl restart systemd-zram-setup@zram0.service`, so the device has this config's
   size and algorithm even if zram0 already existed.
6. `systemctl start dev-zram0.swap`.
7. Print `status`.

The zram step refuses with an error, before any privileged command, if:

- the swappiness drop-in is installed (run `revert swappiness` first);
- `/dev/zram0` is active swap in `/proc/swaps` and `/etc/systemd/zram-generator.conf` is not
  this folder's config (a zram0 device that was reset and is no longer swap does not block);
- `systemd-zram-generator` is installed and this script did not install it, because someone
  else manages it (a re-run after this script installed it is allowed);
- the package `zram-tools` or `zram-config` is installed;
- `/etc/systemd/zram-generator.conf.d/` holds any file;
- `/etc/systemd/zram-generator.conf` exists and differs from this folder's
  `zram-generator.conf`.

The swappiness step refuses the other way round, with exit 1 and before any privileged
command, if this setup's zram config is in place or `/dev/zram0` is active swap. Run
`revert zram` first.

## State

`STATE_DIR` (default `/var/lib/build-pack-memory`) holds three files, written with `sudo` and
read without it, so running the script with or without `sudo` gives the same result:

- `swappiness.prev`: the live `vm.swappiness` before the first swappiness run.
- `zram-package-installed`: written when the zram step runs `apt-get install`, so revert
  knows the script installed the package.
- `zram-generator.conf.installed`: a copy of the config as the zram step installed it. Revert
  and re-runs compare `/etc/systemd/zram-generator.conf` against this copy, so they still
  recognize the config after this folder's copy changes. Without it, they compare against this
  folder's copy.

`ETC_ROOT` (default `/etc`) sets where the drop-in and the zram config are installed. The
test points both variables, and `PROC_ROOT` and `SYS_ROOT`, at a fake tree.

## How to measure

Run `./memory-setup.sh status` before the build and again during or after it. It shows
swappiness, each swap device with its use and priority, zram size and compression ratio, free
memory, and GPU GTT use. For history over the whole build, use `sar` from sysstat:

- `sar -r` for memory use
- `sar -S` for swap use
- `sar -W` for pages swapped in and out per second

Steady swap-in during the build is the sign that swap costs time. Cold pages sitting in swap
are not.

## Trade-off

zram's compressed store lives in RAM, the same pool the GPU's GTT draws on. It trades disk
swap for less free memory. If GTT use in `status` climbs close to its total during a build,
zram is hurting.

## Keep or revert

Keep a change only if a build shows a gain. Otherwise run:

```
./memory-setup.sh revert swappiness   # see below
./memory-setup.sh revert zram         # see below
./memory-setup.sh revert all          # zram first, then swappiness
```

Revert takes exactly one target.

**revert swappiness**

- With a saved value: removes the drop-in, sets the live value back to the saved one with
  `sysctl -w`, and deletes the saved value.
- With the drop-in but no saved value, or a saved value that is not a number: removes the
  drop-in, runs `sysctl --system`, deletes the saved value, and prints the live value. If no config sets `vm.swappiness`, the value stays until reboot
  (the kernel default is 60).
- With neither: prints "swappiness step not applied; nothing to revert" and runs nothing.
  `revert all` after only the zram experiment ends up here.

**revert zram**

- Does nothing, and says so, unless `/etc/systemd/zram-generator.conf` matches this folder's
  copy or the script installed the package.
- Otherwise stops `dev-zram0.swap` and `systemd-zram-setup@zram0.service`, removes the config
  if it matches this folder's copy (a different file is left in place), and reloads systemd.
- Runs `apt-get remove -y systemd-zram-generator` and deletes the marker only if the script
  installed the package. A package installed by someone else stays. Removing the package
  also removes `/usr/lib/systemd/zram-generator.conf`, so no zram0 comes back at the next
  boot.
- A unit that is inactive, failed, or unknown is skipped with a note. A unit that is active
  but will not stop (swapoff can fail under memory pressure) is an error. A unit that is
  activating, deactivating, or reloading is busy, which is also an error. Either way revert
  exits non-zero before it removes any config or package; wait or free some memory, then run
  it again.
- Changing the swap setup moves what a healthy night looks like. The `memory` block's
  `minAvailableMiB` and `maxSwapPercent` in the pipeline config come from a run on the
  earlier setup, so measure a night again after a change and adjust them.
