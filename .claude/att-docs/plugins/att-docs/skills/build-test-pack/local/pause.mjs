// Stops the configured systemd units while a job runs and starts them again
// afterward, so a job has the machine's memory and GPU for the model. Units
// that were not running when a job was about to start are never started,
// except those a dead run left stopped and those a request marked to be
// restored. Output names units from the config and nothing else.

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { sleepUnlessAborted } from './abort.mjs';

/** Runs one command with an argument array, never a shell. */
function defaultExec(command, args) {
  const result = spawnSync(command, args, { encoding: 'utf8' });
  return { status: result.status, stdout: result.stdout ?? '' };
}

// A unit name from systemctl is passed on as an argument, so only plain names go on.
export const UNIT_NAME = /^[A-Za-z0-9][A-Za-z0-9@_.:\\-]*$/;

/** The state file lives beside the queue file, so a later run that takes the queue finds it. */
export const pausedPath = (config) => `${config.at(config.queue.file)}.paused`;

/** The names of `list`, once each, that `stopped` or `restore` still holds. */
const stillHeld = (list, stopped, restore) => [...new Set(list)]
  .filter((u) => stopped.includes(u) || restore.includes(u));

/**
 * The state file holds `{"stopped": [...], "restore": [...], "failedStart": [...]}`:
 * the units a run stopped, the units marked to start when a build ends even
 * though they were not running when it began, and those of the two whose last
 * start failed. `failedStart` is left out of the file when it is empty, and
 * only a name still in `stopped` or `restore` counts. A file that is a bare
 * list of names counts as the stopped units.
 */
export function readPaused(file) {
  const clean = (list) => (Array.isArray(list)
    ? list.filter((u) => typeof u === 'string' && UNIT_NAME.test(u)) : []);
  const held = (stopped, restore, failedStart) => ({ stopped, restore,
    failedStart: stillHeld(failedStart, stopped, restore) });
  try {
    const state = JSON.parse(fs.readFileSync(file, 'utf8'));
    if (Array.isArray(state)) return held(clean(state), [], []);
    return held(clean(state?.stopped), clean(state?.restore), clean(state?.failedStart));
  } catch {
    return held([], [], []);
  }
}

/** Writes the state in one step, and removes the file when nothing is left in it. */
function writePaused(file, { stopped, restore, failedStart = [] }) {
  if (!stopped.length && !restore.length) {
    fs.rmSync(file, { force: true });
    return;
  }
  const failed = stillHeld(failedStart, stopped, restore);
  const state = { stopped, restore, ...(failed.length ? { failedStart: failed } : {}) };
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temp = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(temp, `${JSON.stringify(state)}\n`);
  fs.renameSync(temp, file);
}

/** Adds units to the restore list of the state file beside the queue. */
export function markRestoreFile(config, units) {
  const file = pausedPath(config);
  const state = readPaused(file);
  writePaused(file, { ...state, restore: [...new Set([...state.restore, ...units])] });
}

/** The units the state file still holds to start, stopped or marked. */
export function pendingRestore(config) {
  const state = readPaused(pausedPath(config));
  return [...new Set([...state.stopped, ...state.restore])];
}

/** The held units whose last start failed. */
export function failedStartUnits(config) {
  return readPaused(pausedPath(config)).failedStart;
}

/** A shell-style pattern as a regular expression: `*`, `?`, and `[...]` classes, with `[!...]` or `[^...]` negating. */
function globRegex(pattern) {
  let out = '';
  for (let i = 0; i < pattern.length; i += 1) {
    const c = pattern[i];
    if (c === '*') out += '.*';
    else if (c === '?') out += '.';
    else if (c === '[') {
      const negated = pattern[i + 1] === '!' || pattern[i + 1] === '^';
      const first = i + 1 + (negated ? 1 : 0);
      // A `]` right after the opening bracket is a member of the class, not its end.
      const end = pattern.indexOf(']', first + 1);
      if (end === -1) {
        out += '\\[';
        continue;
      }
      const body = pattern.slice(first, end).replace(/[\\\]^]/g, '\\$&');
      out += `[${negated ? '^' : ''}${body}]`;
      i = end;
    } else out += c.replace(/[.+^${}()|\\\]]/g, '\\$&');
  }
  return new RegExp(`^${out}$`);
}

/** True when `unit` is a plain name that one of the configured pause patterns matches. */
export function onPauseList(patterns, unit) {
  if (!UNIT_NAME.test(unit ?? '')) return false;
  return patterns.some((pattern) => {
    try {
      return globRegex(pattern).test(unit);
    } catch {
      return false;
    }
  });
}

/** The pause-list units systemd has loaded that are not running now. */
export function downUnits(config, { exec = defaultExec } = {}) {
  const { units: patterns, scope } = config.pause;
  if (!patterns.length) return [];
  const result = exec('systemctl', [...(scope === 'user' ? ['--user'] : []), 'list-units', '--plain',
    '--no-legend', '--all', '--state=inactive,failed', ...patterns]);
  if (result.status !== 0) return [];
  return [...new Set(result.stdout.split('\n').map((line) => line.trim().split(/\s+/)[0])
    .filter((unit) => UNIT_NAME.test(unit ?? '')))];
}

/** True when a process named `busyProcess` runs inside the unit's cgroup. */
export function unitBusy(procRoot, unit, busyProcess) {
  let pids;
  try {
    pids = fs.readdirSync(procRoot).filter((name) => /^\d+$/.test(name));
  } catch {
    return false;
  }
  for (const pid of pids) {
    try {
      if (fs.readFileSync(path.join(procRoot, pid, 'comm'), 'utf8').trim() !== busyProcess) continue;
      const groups = fs.readFileSync(path.join(procRoot, pid, 'cgroup'), 'utf8').split('\n');
      // The unit's cgroup path ends in its name; a longer name that merely ends the same way is not it.
      if (groups.some((line) => line.endsWith(`/${unit}`) || line.includes(`/${unit}/`))) return true;
    } catch {
      // The process exited while it was read.
    }
  }
  return false;
}

/**
 * A pauser for one run. `pause()` stops the active units the config names,
 * waiting for a busy one to go idle first, for at most `maxWaitMinutes`,
 * never past `until`, and never past a `signal` that aborts; a unit still
 * busy then is left running until a later `pause()` finds its worker finished. `resume()` starts every unit this
 * run stopped or was told to restore, plus those a run that died left in the
 * state file. Neither
 * throws: a failed stop or start is logged and the run carries on.
 *
 * `leftover` is true for a run that holds the queue lock, the only run that
 * may restore what a dead holder stopped.
 */
export function createPauser(config, { exec = defaultExec, log = console.log, procRoot = '/proc',
  sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)), clock = () => new Date(),
  leftover = true } = {}) {
  const { units: patterns, scope, busyProcess, pollSeconds, maxWaitMinutes } = config.pause;
  const user = scope === 'user';
  const file = pausedPath(config);
  const systemctl = (...args) => (user ? exec('systemctl', ['--user', ...args])
    : exec('sudo', ['-n', '/usr/bin/systemctl', ...args]));
  const stopped = [];
  // A unit that would not stop is not tried again, and a busy one is reported once.
  const failed = new Set();
  const reported = new Set();
  const marked = new Set();
  let cancelled = false;
  let resumed = false;

  // Merged with what the file holds, so a mark written meanwhile is not lost.
  const record = () => {
    const state = readPaused(file);
    writePaused(file, { stopped: [...new Set([...state.stopped, ...stopped])],
      restore: [...new Set([...state.restore, ...marked])], failedStart: state.failedStart });
  };

  const stopOne = (unit) => {
    const result = systemctl('stop', unit);
    if (result.status !== 0) {
      log(`pause: stop failed ${unit}`);
      failed.add(unit);
      return;
    }
    stopped.push(unit);
    record();
    log(`pause: stopped ${unit}`);
  };

  const activeUnits = () => {
    // Listing is read-only, so it needs no sudo.
    const result = exec('systemctl', [...(user ? ['--user'] : []), 'list-units', '--plain',
      '--no-legend', '--state=active', ...patterns]);
    if (result.status !== 0) {
      log('pause: list failed');
      return [];
    }
    return [...new Set(result.stdout.split('\n').map((line) => line.trim().split(/\s+/)[0])
      .filter((unit) => UNIT_NAME.test(unit ?? '')))];
  };

  return {
    async pause({ until = null, signal = null } = {}) {
      if (!patterns.length || cancelled || resumed || signal?.aborted) return;
      const limit = clock().getTime() + maxWaitMinutes * 60000;
      const deadline = until ? Math.min(limit, until.getTime()) : limit;
      let waiting = activeUnits().filter((unit) => !failed.has(unit));
      while (waiting.length && !cancelled && !signal?.aborted) {
        const busy = [];
        for (const unit of waiting) {
          if (busyProcess && unitBusy(procRoot, unit, busyProcess)) busy.push(unit);
          else stopOne(unit);
        }
        waiting = busy;
        if (!waiting.length) break;
        const left = deadline - clock().getTime();
        if (left <= 0) {
          const fresh = waiting.filter((unit) => !reported.has(unit));
          fresh.forEach((unit) => reported.add(unit));
          if (fresh.length) log(`pause: left running ${fresh.join(' ')}`);
          return;
        }
        log(`pause: waiting for ${waiting.join(' ')}`);
        // A stop request ends the wait at once.
        await sleepUnlessAborted(sleep, Math.min(pollSeconds * 1000, left), signal);
      }
    },
    /** Units to start when the run ends, though they were not running when it began. */
    mark(units) {
      if (!units.length || resumed) return;
      units.forEach((unit) => marked.add(unit));
      record();
    },
    /** Starts every unit this run stopped or marked, plus, for the queue holder, those the file holds. Returns the units that did not start. */
    async resume() {
      if (resumed) return [];
      resumed = true;
      cancelled = true;
      const state = readPaused(file);
      const targets = new Set([...stopped, ...marked,
        ...(leftover ? [...state.stopped, ...state.restore] : [])]);
      const failedStart = [];
      for (const unit of targets) {
        const result = systemctl('start', unit);
        if (result.status !== 0) failedStart.push(unit);
        log(result.status === 0 ? `pause: started ${unit}` : `pause: start failed ${unit}`);
      }
      if (targets.size) {
        const left = readPaused(file);
        // A unit that did not start stays recorded, so a later run or `queue restore` tries it again.
        const done = (u) => targets.has(u) && !failedStart.includes(u);
        writePaused(file, { stopped: left.stopped.filter((u) => !done(u)),
          restore: left.restore.filter((u) => !done(u)),
          failedStart: [...left.failedStart.filter((u) => !targets.has(u)), ...failedStart] });
      }
      return failedStart;
    },
  };
}
