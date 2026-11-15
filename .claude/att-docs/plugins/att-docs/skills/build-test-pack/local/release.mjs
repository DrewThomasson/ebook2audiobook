// Unloads the local model when a queue run ends, so the machine's memory is
// free without anyone stopping the model server by hand. The command comes from
// the config; its output is never read, and the one status line it writes holds
// an outcome code and a duration and nothing else.

import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { jobLogs } from './status.mjs';

/** Runs one command with an argument array, never a shell. */
function defaultExec(command, args, timeoutMs) {
  const result = spawnSync(command, args, { encoding: 'utf8', timeout: timeoutMs, stdio: 'ignore' });
  return { status: result.status, signal: result.signal, error: result.error };
}

/**
 * A releaser for one run. `note(jobId)` records the job that ran last, and
 * `release()` runs the configured command once, however many times it is
 * called, and only after a job was noted: a run that started no job loaded no
 * model, and a model another process holds is not this run's to unload. It
 * never throws; a failed unload is logged and changes nothing else.
 */
export function createReleaser(config, { exec = defaultExec, log = console.log,
  now = Date.now } = {}) {
  const { command, timeoutSeconds } = config.release;
  let last = null;
  let released = false;
  return {
    note(jobId) {
      last = jobId;
    },
    release() {
      if (released || !last || !command.length) return;
      released = true;
      const started = now();
      let outcome = 'pass';
      let reason = null;
      try {
        const result = exec(command[0], command.slice(1), timeoutSeconds * 1000);
        if (result.error?.code === 'ETIMEDOUT') [outcome, reason] = ['fail', 'timeout'];
        else if (result.error) [outcome, reason] = ['fail', 'spawn-error'];
        else if (result.signal) [outcome, reason] = ['fail', 'signal'];
        else if (result.status !== 0) [outcome, reason] = ['fail', `exit-${result.status}`];
      } catch {
        [outcome, reason] = ['fail', 'spawn-error'];
      }
      log(`release: ${outcome === 'pass' ? 'ok' : 'failed'}`);
      try {
        jobLogs(path.join(config.output, last), { echo: false }).status({
          job: last, phase: 'release', event: outcome, ...(reason ? { reason } : {}),
          ms: now() - started,
        });
      } catch {
        // The status log could not be written; the console line above still says what happened.
      }
    },
  };
}
