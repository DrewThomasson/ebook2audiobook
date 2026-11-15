// Closes the desktop apps the config lists before a queue run starts, so the
// model has their memory. Apps run as transient user scopes, which a stop ends
// and nothing here starts again. A scope that holds this process, or a process
// named in `keepIfRunning`, is left open. Output carries scope names the config
// matched, counts and fixed words, never anything an app held.

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { unitBusy } from './pause.mjs';

/** Runs one command with an argument array, never a shell. */
function defaultExec(command, args) {
  const result = spawnSync(command, args, { encoding: 'utf8' });
  return { status: result.status, stdout: result.stdout ?? '' };
}

// A scope name from systemctl is passed on as an argument, so only plain scope names go on.
const SCOPE_NAME = /^[A-Za-z0-9][A-Za-z0-9@_.:\\-]*\.scope$/;

/** How many processes named `name` run, for the warning about sessions that stay open. */
function countProcesses(procRoot, name) {
  let pids;
  try {
    pids = fs.readdirSync(procRoot).filter((entry) => /^\d+$/.test(entry));
  } catch {
    return 0;
  }
  let count = 0;
  for (const pid of pids) {
    try {
      if (fs.readFileSync(path.join(procRoot, pid, 'comm'), 'utf8').trim() === name) count += 1;
    } catch {
      // The process exited while it was read.
    }
  }
  return count;
}

/** The app a scope belongs to: the desktop session names an app's two scopes (app- and app-gnome-) with the same ID and PID. */
const appKey = (scope) => scope.replace(/^(app-(gnome-|flatpak-)?|snap\.)/, '').replace(/\.scope$/, '');

/** True when this process runs inside the scope's cgroup. */
function holdsSelf(selfCgroup, scope) {
  return selfCgroup.split('\n').some((line) => line.endsWith(`/${scope}`) || line.includes(`/${scope}/`));
}

function readSelfCgroup() {
  try {
    return fs.readFileSync('/proc/self/cgroup', 'utf8');
  } catch {
    return '';
  }
}

/**
 * A closer for one run. `close()` stops each active scope the config's patterns
 * match, once per run, and never throws: a failed stop is logged and the run
 * carries on. A scope that holds this process, or one with a process named in
 * `keepIfRunning`, is logged as left open.
 */
export function createAppCloser(config, { exec = defaultExec, log = console.log, procRoot = '/proc',
  selfCgroup = readSelfCgroup() } = {}) {
  const { scopes, keepIfRunning } = config.closeApps;
  let done = false;

  return {
    close() {
      if (!scopes.length || done) return;
      done = true;
      // Listing is read-only.
      const listed = exec('systemctl', ['--user', 'list-units', '--plain', '--no-legend',
        '--state=active', ...scopes]);
      if (listed.status !== 0) {
        log('close: list failed');
        return;
      }
      const active = [...new Set(listed.stdout.split('\n').map((line) => line.trim().split(/\s+/)[0])
        .filter((scope) => SCOPE_NAME.test(scope ?? '')))];
      const kept = new Set(active.filter((scope) => holdsSelf(selfCgroup, scope)
        || keepIfRunning.some((name) => unitBusy(procRoot, scope, name))));
      // An app's helper scope stays open with the scope that holds a kept process, since the
      // helpers serve it.
      const keptApps = new Set([...kept].map(appKey));
      for (const scope of active) {
        if (keptApps.has(appKey(scope))) kept.add(scope);
      }
      for (const scope of active) {
        if (kept.has(scope)) {
          log(`close: left open ${scope}`);
          continue;
        }
        // A stop sends SIGTERM to the scope's processes and waits before it ends them.
        const stopped = exec('systemctl', ['--user', 'stop', scope]);
        log(stopped.status === 0 ? `close: closed ${scope}` : `close: stop failed ${scope}`);
      }
      for (const name of keepIfRunning) {
        const open = countProcesses(procRoot, name);
        if (open) log(`close: ${name} processes open ${open}`);
      }
    },
  };
}
