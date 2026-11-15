# Out-of-memory protection for the model host

On the model host (MTabletPC, about 57 GiB RAM), if memory runs out during a build, the kernel
or `systemd-oomd` should end a desktop app, not the local model in the middle of a job. Two
separate changes do that. Both are optional, and `oom-setup.sh` installs and removes them.

- **Protect the model** (`99-build-pack-oom.conf`) is a drop-in for `lemonade-server.service`
  that sets `OOMScoreAdjust=-500` and `ManagedOOMPreference=avoid`. `llama-server` runs as a
  child of that service and inherits the score. The kernel's killer picks the highest score
  first. A score is the memory a process holds, in thousandths of RAM plus swap, plus the
  adjustment, so -500 takes off the equivalent of half of RAM plus swap. That moves the model well down the list but
  does not exempt it: a model holding most of RAM can still outscore a pile of small apps. `systemd-oomd` reads the
  preference from the service's control group and skips an `avoid` group while any other
  candidate exists. Without the drop-in the unit has `OOMScoreAdjust=0` and
  `ManagedOOMPreference=none`. The score is set by systemd before the service drops to its own
  user, so the unit needs no extra capability. A `llama-server` started outside the service's
  control group gets nothing from it, which is why `status` prints each one's control group.
- **Throttle the desktop apps** (`build-pack-apps.conf`) sets `MemoryHigh` on the user
  manager's `app.slice`. GNOME starts each app as a transient scope under that slice, so one
  limit covers Chrome, Discord and the rest together. Past the limit the kernel reclaims the
  apps' memory hard, so they slow down first. `MemoryHigh` itself never kills and no
  `MemoryMax` is set, but the pressure from throttling counts toward `systemd-oomd`'s pressure
  limit on the user manager, which can end an app or a build-pack unit under the user manager.
  The build-pack units are user services and would also sit in `app.slice`, so this step also
  installs `build-pack.slice` (`build-pack.slice`) and a drop-in per unit
  (`build-pack-slice.conf`) that moves `build-pack.service`, `build-pack-now@.service`,
  `build-pack-check.service` and `build-pack-report.service` into it. A unit that is already
  running keeps its old slice until it restarts.
  Terminal windows, and anything started from them, such as a build run by hand, also sit in
  `app.slice` and share the limit.

## Where the files live

| File | Installed at |
| --- | --- |
| `99-build-pack-oom.conf` | `/etc/systemd/system/lemonade-server.service.d/99-build-pack-oom.conf` |
| `build-pack-apps.conf` | `~/.config/systemd/user/app.slice.d/50-build-pack-apps.conf`, with `@HIGH@` replaced |
| `build-pack.slice` | `~/.config/systemd/user/build-pack.slice` |
| `build-pack-slice.conf` | `~/.config/systemd/user/<unit>.d/50-build-pack-slice.conf`, one per build-pack unit |

A Lemonade package upgrade replaces `/usr/lib/systemd/system/lemonade-server.service` and the
drop-ins under `/usr/lib`, and never touches `/etc/systemd/system`, so the drop-in survives an
upgrade. The `99-` prefix sorts it last, so if a later package ships a drop-in of its own that
sets the same keys, this one still wins. The existing `memlock.conf` drop-in is left alone.
After an upgrade, run `./oom-setup.sh status` to confirm.

## Use

```bash
./oom-setup.sh status
./oom-setup.sh apply model
./oom-setup.sh apply apps --high 24G
./oom-setup.sh revert all
```

`apply model` reloads systemd but does not restart Lemonade, because a restart unloads the model
and ends a running job. A running `llama-server` keeps its old score until then, and `status`
says "restart needed" while they differ. Run `./oom-setup.sh apply model --restart` between jobs.
Then check:

```bash
systemctl show lemonade-server.service -p OOMScoreAdjust -p ManagedOOMPreference
./oom-setup.sh status
```

`status` prints `oom_score_adj` for each running `llama-server`, and it should read `-500`.

`--high` takes a whole number with an `M` or `G` suffix, or a percentage of RAM from 1% to 99%.
Pick a value from what the apps hold in a normal day; apps over it are slowed, and under sustained pressure `systemd-oomd` can still end one.

`revert model`, `revert apps` and `revert all` remove only files that still start with the line
`# Installed by oom-setup.sh.` and reload systemd. A file that someone edited is left in place.
Add `--dry-run` to any command to print the commands that change anything without running them.
