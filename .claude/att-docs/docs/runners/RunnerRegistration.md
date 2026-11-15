# Runner registration

All sixteen self-hosted runners register on the `merph518` organization, in its
Default runner group, so `Playwright-Testing` and `Overmind` draw on the same
machines. Labels decide which repository's jobs land where.

## The group and who may use it

`merph518` is on the free plan, which allows the Default group only: no custom
groups, and no limit on which repositories use it. Every private repository in
the organization can run jobs on every runner. Public repositories cannot,
unless the group's public-repository setting is turned on, and it stays off.

Separation is by label alone, an accepted trade-off. A workflow in any
repository that asks for `playwright` reaches the Playwright runners, so the
convention below is the only thing that keeps Overmind jobs off them. Account
leases still hold concurrent Playwright jobs apart whatever else is running,
since a lease is taken by the test, not by the runner.

| Runners | Labels | Used by |
| --- | --- | --- |
| `pw-linux-runner-1` to `-6` | `self-hosted`, `Linux`, `X64`, `playwright`, `overmind` | `Playwright-Testing`, `Overmind` |
| `pw-windows-runner-1` | `self-hosted`, `Windows`, `X64`, `playwright` | `Playwright-Testing` |
| `pw-ci-runner-desktop-1` to `-5` | `self-hosted`, `Windows`, `X64`, `ci`, `overmind` | `Playwright-Testing`, `Overmind` |
| `tablet-runner-1` to `-4` | `self-hosted`, `Linux`, `X64`, `ci`, `static-checks`, `overmind` | `Playwright-Testing`, `Overmind` |

The rules that keep this working:

- `Overmind` workflows target `runs-on: [self-hosted, overmind]` and
  never name `playwright`. A job that needs a POSIX shell, such as `test-all` in
  `ci.yml`, adds `Linux`; a job that needs the desktops, such as `pack-compare`,
  adds `Windows`; the rest run on any `overmind` runner, Windows included.
- The Linux Playwright runners carry `overmind` so the Linux jobs still have a
  runner while the tablet runners are stopped for a test pack build.
- `Playwright-Testing` workflows keep their labels as they are. Every `runs-on` under
  `.github/workflows` resolves against the table above with no edit.
- A new runner for Overmind work gets `overmind`. A new Linux Playwright runner
  gets it too, and a new Windows Playwright runner does not.

## Moving a runner from the repository to the organization

A configured runner cannot be configured again in place, so each one is
removed from `Playwright-Testing` and registered again on the organization under the same
name. The scripts do both halves and reinstall the service under the account
it already used.

1. Mint the two tokens on any machine signed in to `gh`. The organization token
   needs the `admin:org` scope (`gh auth refresh -h github.com -s admin:org`).
   Each lasts about an hour and covers every runner moved in that hour.

   ```bash
   gh api -X POST repos/merph518/Playwright-Testing/actions/runners/remove-token --jq .token
   gh api -X POST orgs/merph518/actions/runners/registration-token --jq .token
   ```

2. On the runner's machine, take the scripts from a fresh clone of `main` in
   the home folder (`git clone https://github.com/merph518/Playwright-Testing`), not from a
   runner's `_work` folder, which every job replaces with whatever branch it
   ran. Set the tokens as `REMOVE_TOKEN` and `REGISTER_TOKEN` in the shell,
   never in a file, and run the script once per runner folder with that
   runner's custom labels from the table. The script refuses a runner that is
   running a job. When a run fails after removing the repository registration,
   such as on an expired token, mint a new registration token and run the same
   command again: a `.move-to-org` file left in the folder lets it pick up at
   the registration. A runner registered under the repository's name before
   its transfer gets 404 from the removal; the script sets its registration
   files aside in `.repo-registration` and registers it anyway, and the
   repository's record of it is deleted by id afterwards:
   `gh api -X DELETE repos/merph518/Playwright-Testing/actions/runners/<id>`.

   ```bash
   scripts/move-runner-to-org.sh ~/actions-runner-1 playwright
   scripts/move-runner-to-org.sh ~/actions-runner ci,static-checks,overmind
   ```

   ```powershell
   scripts/move-runner-to-org.ps1 -Folder C:\actions-runner -Labels ci,overmind
   scripts/move-runner-to-org.ps1 -Folder C:\actions-runner -Labels playwright
   ```

   The Windows script reuses the old service's logon account and asks for its
   password at the prompt when it is not a built-in account.

3. Move one runner per label set at a time, so the pool keeps capacity for
   queued jobs while each one is between registrations.

### The Linux Playwright runners from a workflow

`Runner Move to Org (on demand)` moves `pw-linux-runner-1` to `-6` from a job
on one of them, with no shell on their machine. It reads the tokens from the
`RUNNER_REMOVE_TOKEN` and `RUNNER_REGISTER_TOKEN` repository secrets, so set
both just before the dispatch, piping each token straight into the secret:

```bash
gh api -X POST repos/merph518/Playwright-Testing/actions/runners/remove-token --jq .token |
  gh secret set RUNNER_REMOVE_TOKEN
gh api -X POST orgs/merph518/actions/runners/registration-token --jq .token |
  gh secret set RUNNER_REGISTER_TOKEN
gh workflow run runner-move-to-org.yml
```

The job moves every runner but its own and names that one in a notice.
Dispatch again with `-f runners=<n>` for it. A runner already on the
organization is left alone, so a repeat dispatch only finishes the move.
Delete both secrets once the six show online on the organization.

## Checking the move

- `gh api orgs/merph518/actions/runners --jq '.runners[] | "\(.name) \(.status) \([.labels[].name] | join(","))"'`
  lists all sixteen with their labels, and
  `gh api repos/merph518/Playwright-Testing/actions/runners --jq .total_count` reads `0`.
- `scripts/runner_status.py --text` lists the Linux Playwright runners from both
  lists. Without `admin:org` it shows only the repository's own runners, which
  is none after the move, and warns.
- Dispatch `Runner Service Restart`, `Runner Disk Cleanup`, and
  `Runner Memory Limit` once each. They target `[self-hosted, playwright, Linux]`,
  which the moved Linux runners still carry.
- Run a job in `Overmind` on `[self-hosted, overmind]`, and while it runs,
  dispatch `Playwright Debug (on demand)` on one spec with `workers=1` and
  `retries=1`. It should land on a `playwright` runner, pass, and log no lease
  timeout.

## Registering a new runner

New runners register on the organization from the start: the same
`config.sh --url https://github.com/merph518 --runnergroup Default` call the
scripts make, with an organization registration token and the labels from the
table.

## Pack comparison on the desktop runners

The `Pack comparison` workflow (`.github/workflows/pack-compare.yml`) runs
`build-pack.mjs compare` without a model on a `pw-ci-runner-desktop-*` runner. It runs
only from `main`, by hand, and prints the exit code and the counts the command prints.
It uploads nothing and writes no step summary.

To use it:

1. Install Node 18 or later on the runner, on the PATH of the runner service account.
   The workflow checks for it and fails with a message when it is missing; it installs
   nothing.
2. Copy the files into one folder on the runner, with these names: `reference.xlsx`,
   `pack.xlsx`, `doc.md`, one of `rules.json` or `rules.xlsx`, and optionally
   `standard.md`. The default folder is `C:\pack-compare`. The folder is the workflow's
   one input. Give it a name with no work content in it, because dispatch inputs are
   visible on the run. It cannot be a drive root, the runner account's profile folder, or the runner
   workspace, or inside one. The step deletes any file in it with one of the fixed
   names, so never point it at a folder that holds the only copy of a pack.
3. Dispatch the workflow. The job's `[self-hosted, overmind, Windows]` labels match any
   of the five runners, so the files must be on the machine that picks the job up. This
   works only when the five runners share one machine.
4. The last step deletes the six fixed file names from the folder, removes the folder
   when it is then empty, and deletes the report folder under the runner's temp folder.
   It runs after a failure or a cancel too, but deletes the staged files only when this
   run's checkout succeeded. When the run stops earlier (a ref other than `main`, Node
   missing or too old, a failed checkout), it removes only the report and fails with a
   message, so delete the staged files by hand. The same applies if the machine itself
   is lost mid-run.

The report is never kept. If a run's counts need a look at the report, run `compare` on
the desktop instead.

## Stopping the tablet runners for a test pack build

A test pack build needs the memory the model uses, so the nightly queue run
stops the four tablet runner units while a job runs and starts them again after.
The work repository's pipeline config (`.claude/skills/build-test-pack/pipeline.json`)
already lists the units, with `"scope": "system"` and `"busyProcess": "Runner.Worker"`.
A runner with a CI job in progress is waited for, at most `pause.maxWaitMinutes`
(60 by default) and never past the queue cutoff. `ci.yml` and `release.yml` wait
until the queue run ends.

The one host step is a sudoers file for the user that runs the queue. Create it
with `sudo visudo -f /etc/sudoers.d/build-pack-runners` and mode 0440:

```
Cmnd_Alias BUILD_PACK_RUNNERS = \
  /usr/bin/systemctl stop actions.runner.MRF-ORG.tablet-runner-1.service, \
  /usr/bin/systemctl start actions.runner.MRF-ORG.tablet-runner-1.service, \
  /usr/bin/systemctl stop actions.runner.MRF-ORG.tablet-runner-2.service, \
  /usr/bin/systemctl start actions.runner.MRF-ORG.tablet-runner-2.service, \
  /usr/bin/systemctl stop actions.runner.MRF-ORG.tablet-runner-3.service, \
  /usr/bin/systemctl start actions.runner.MRF-ORG.tablet-runner-3.service, \
  /usr/bin/systemctl stop actions.runner.MRF-ORG.tablet-runner-4.service, \
  /usr/bin/systemctl start actions.runner.MRF-ORG.tablet-runner-4.service
michael ALL=(root) NOPASSWD: BUILD_PACK_RUNNERS
```

Check one rule with
`sudo -n -l /usr/bin/systemctl stop actions.runner.MRF-ORG.tablet-runner-1.service`,
which prints the command when the rule allows it. After the next nightly run,
`journalctl --user -u build-pack.service | grep 'pause:'` shows `stopped` and
`started` lines, not `stop failed`.

A runner can take a job between the busy check and the stop. The unit files use
`KillMode=process`, so the stop ends the listener and the new `Runner.Worker`
keeps running until it finishes. This is rare and is not handled.

### Limiting runner memory

A `MemoryHigh` limit throttles a runner instead of stopping it. It matters when a
runner is left running at the timeout, or when the pause is off. Measure first
with `systemctl show -p MemoryPeak actions.runner.MRF-ORG.tablet-runner-1.service`
after a `test-all` run, then set the limits from the peak. The values below are
starting points, not measurements, and apply without a restart:

```bash
for n in 1 2 3 4; do sudo systemctl set-property actions.runner.MRF-ORG.tablet-runner-$n.service MemoryHigh=4G MemoryMax=6G; done
```

This writes drop-ins under `/etc/systemd/system.control/`. Revert with
`MemoryHigh=infinity MemoryMax=infinity`.

## Docker on the tablet runners

A tablet runner needs Docker from the `docker.io` apt package
(`sudo apt install docker.io` when it is missing) for a job that builds or runs
a container. A job reaches the daemon through `/var/run/docker.sock`, which
only root and the `docker` group may open, so the runner's service account has
to be in that group.

Membership in the `docker` group is root-equivalent on the runner. For that
reason a workflow that uses Docker must skip pull requests from forks of a
private repository; nothing here enforces it, so each workflow does, for
example with
`if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.full_name == github.repository`
on the job.

On each tablet runner:

1. Add the account the runner service runs as (`michael`) to the group:
   `sudo usermod -aG docker michael`.
2. Restart the runner service from its folder:
   `sudo ./svc.sh stop && sudo ./svc.sh start`. A running service keeps the
   groups it started with, so a job fails with `permission denied` on the
   socket until it restarts.
3. Check it as that account: `docker info` should print the server details
   rather than a permission error. Do this on all four runners, not only one.
