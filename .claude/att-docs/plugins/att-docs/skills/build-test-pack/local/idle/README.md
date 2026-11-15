# Idle unload for the local model

Lemonade holds a model's memory from the moment it loads until someone unloads it, and
version 10.2.0 has no idle timeout. On the model host (MTabletPC), Qwen3.8-27B Q8_0 takes
about 32 GiB of the shared 64 GB while loaded: 25.4 GiB of weights, a 6.2 GiB KV cache, and
buffers. Free system memory is 18.0 GiB with the model loaded and 52.2 GiB after
`lemonade unload`. The next request loads the model again through Lemonade's auto-load, which
adds about 12 seconds to that request.

This folder installs a systemd timer that unloads the model after 15 minutes with no
requests.

## How it works

Lemonade 10.2.0 runs as the system unit `lemonade-server.service`, with its API at
`http://127.0.0.1:13305/api/v1`. The timer is a system timer too. Every minute it starts
`lemonade-idle-unload.service`, which runs `idle-unload.mjs` once as a dynamic user with no
privileges. Each run:

1. Reads `/api/v1/health`. If Lemonade is not there to answer (connection refused, reset or
   closed mid-reply, host or network unreachable, name not found, or a timeout), the run ends
   quietly and keeps the saved record. Any other failure of the read exits non-zero and is
   logged, so the service shows as failed: an HTTP status outside 2xx (for example 401 once
   an API key is set, or a 404 or 5xx), a body that is not JSON, a TLS error, a refused
   redirect, or a request Node rejects. If no model is loaded, the saved record is cleared
   and the run ends.
2. For each loaded model, takes its `backend_url` (the llama.cpp server), drops a trailing
   `/v1`, requires a loopback host, and reads `<backend>/slots`. A model without llama.cpp
   slots (no `backend_url`, or a recipe other than llamacpp) is left alone: it is never
   unloaded by this timer and does not hold up the others. Each run logs one line for every
   such model, naming it and the reason, so a mismatch between Lemonade's field names and
   these checks shows in the journal. A model name that appears twice is judged once.
3. Builds a signature for each model from its backend URL and each slot's `id_task` and
   `is_processing`, and compares it with the one saved for that model in
   `/var/lib/lemonade-idle-unload/state.json`, a map of model name to its signature and time
   of last activity. A model's time moves to now when any of its slots is processing, when
   its signature changed since the last run, or when it has no saved entry. A changed
   `id_task` means a request began since the last run, even one that began and finished
   between two runs. A saved time later than the current time (the clock moved back) also
   counts as a change and is reset to now. A model that is no longer loaded drops out of
   the record. A record that is not a map of model entries counts as none.
4. Treats a `/slots` request that fails, answers a non-2xx status, returns a shape other
   than a list of slots with a boolean `is_processing`, or takes longer than the 5 second
   read as busy, and logs one line naming the model and the problem. That includes a long
   prefill, when llama.cpp may answer slowly. The model whose slots cannot be read is never
   unloaded, and the other models are judged on their own.
5. When a model's time since last activity reaches the timeout, the model is due for an
   unload. The unloads run one after another, and immediately before each one the run reads
   that model's slots once more. If they are still idle and unchanged, it sends
   `POST /api/v1/unload` with the JSON body `{"model_name": "<name>"}` and logs one line to
   the journal with the model name and the idle minutes. If they are busy or changed, it
   skips that model, logs one line saying so, and moves its time to now. Because each read
   follows the unload before it,
   a second model is checked after the first unload has finished.

If an unload fails, the run exits non-zero, the service shows as failed, and that model's
entry stays in the record, so the next minute tries again; entries of models that did unload
are removed. A `backend_url` that is not on this machine is refused: the run exits non-zero
and unloads nothing. Every request refuses redirects and stops after 5 seconds (30 seconds
for the unload).

### Limits

- A request that runs longer than the timeout is never cut off. While it runs, its slot is
  processing, so the time of last activity moves to now on every run. A 50k-token prefill that
  takes 5 minutes is covered, and so is one that takes an hour.
- A request that Lemonade has already forwarded to llama-server in the moment of the unload
  can fail. That includes a large prompt that is still being tokenized, before its slot shows
  processing. Only a request that reaches Lemonade after the unload is answered by loading
  the model again, with the load delay. The window is small, and the read of the model's
  slots just before its own unload narrows it further.
- The timeout counts from the last run that saw activity, so an unload comes between the
  timeout and the timeout plus one minute after the last request ended.
- Another client on the same Lemonade is treated like this pipeline: any request it makes
  holds the model loaded.

## The timeout

The default is 15 minutes. It lives in `/etc/default/lemonade-idle-unload`, which the service
reads as `IDLE_MINUTES=<n>`, a positive whole number. A value that is not one makes every
run exit with an error and unload nothing. To change it:

    ./idle-setup.sh apply --minutes 30

or edit the file and wait for the next run; the service reads it fresh each minute and
needs no restart. The timeout is 15 minutes only when no settings file exists. The same file
may set `LEMONADE_URL=<url>` if the API is not at `http://127.0.0.1:13305/api/v1` (the host
must be loopback), and `LEMONADE_API_KEY=<key>` if Lemonade requires one. The key is sent as
`Authorization: Bearer <key>` on the health read and the unload, never to the model
servers. The file is readable by everyone (mode 0644), so use a key meant for this timer.

## Install

    ./idle-setup.sh status
    ./idle-setup.sh --dry-run apply
    ./idle-setup.sh apply [--minutes N]

`apply` runs these steps with `sudo`:

1. Copy `idle-unload.mjs` to `/usr/local/lib/lemonade-idle-unload/`.
2. Install `lemonade-idle-unload.service` to `/etc/systemd/system`, with the absolute path of
   the `node` found on the PATH written into `ExecStart`.
3. Install `lemonade-idle-unload.timer` to `/etc/systemd/system`.
4. With `--minutes`, write `/etc/default/lemonade-idle-unload`. A file there that `apply` did
   not write stops the run; set `IDLE_MINUTES` in it by hand. Without `--minutes`, an
   existing settings file and the timeout in it stay as they are.
5. `systemctl daemon-reload`, then `systemctl enable --now lemonade-idle-unload.timer`.

The timer is `WantedBy=timers.target`, so it survives a reboot. The service runs as a dynamic
user, so `apply` refuses, before changing anything, a `node` under `/home` or `/root` or one
that others cannot read and execute, which an apt install is not. It also refuses a path
for `node` (and the real file it resolves to) or `LIB_DIR` that holds a space, `|`, `&`, `%`,
`$`, a backslash, or a newline. `ExecStart` names the resolved real path of `node`, the
file that was checked, and points the script at `LIB_DIR`, so a non-default `LIB_DIR` works.

`ETC_ROOT`, `UNIT_DIR`, `LIB_DIR`, `STATE_DIR`, and `PRIVATE_DIRS` point the script at other
folders; the tests use them.

## Revert

    ./idle-setup.sh revert

This disables the timer (a failing `disable` stops the revert before anything is removed),
then stops the timer and the service (a unit that is not loaded does not stop the revert),
removes the two units and the script, removes `/etc/default/lemonade-idle-unload` if it is
still the file `apply` wrote, and reloads systemd. A settings file you changed stays. The
record `state.json` stays under `/var/lib/private/lemonade-idle-unload` (a few bytes); delete
that folder to remove it.

## Check it

1. Confirm the timer is waiting: `./idle-setup.sh status`, or
   `systemctl list-timers lemonade-idle-unload.timer`.
2. Send a request so the model loads, then leave it alone for the timeout plus a minute.
3. `lemonade status` shows no model loaded, and `free -h` shows available memory back near
   52 GiB.
4. `journalctl -u lemonade-idle-unload.service` shows the line
   `unloaded <model> after <n> minutes idle`.
5. Send another request. It succeeds and takes about 12 seconds longer while the model loads.
6. Start a request that runs past the timeout and confirm `lemonade status` still shows the
   model loaded until it finishes.

One thing is still unconfirmed: the exact body `POST /api/v1/unload` accepts. An empty body
was answered with 400, and `{"model_name": "<name>"}` is the form this sends. On the first
real unload, check that `lemonade status` shows the model gone. If the journal instead shows
`unload of <model> answered 400`, read the endpoint's error text and adjust `unloadModel` in
`idle-unload.mjs`.

## Tests

    node --test idle-unload.test.mjs
    bash idle-setup_test.sh

Both use fakes for Lemonade, `sudo`, and `systemctl`, and change nothing on the machine.
