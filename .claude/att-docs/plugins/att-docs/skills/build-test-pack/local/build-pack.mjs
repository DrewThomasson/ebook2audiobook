#!/usr/bin/env node
// Builds test packs on the local model, one job at a time.
//
//   node build-pack.mjs run --config <pipeline.json> --issue <n> [--change <m>] [--doc <path>]... [--resume]
//   node build-pack.mjs run --config <pipeline.json> --suite <code> [--resume]
//   node build-pack.mjs run --config <pipeline.json> --job <id> --from <phase> [--until <phase>] [--as <label>] [--pause] [--model replay:<source> [--replay-miss fail|live]]
//   node build-pack.mjs step --config <pipeline.json> --job <id> --at <phase|sandbox> <step> [--finding <n>] [--check <names>] [--field <name>] [--as <label>] [--pause] [--model replay:<source> [--replay-miss fail|live]]
//   node build-pack.mjs check --config <pipeline.json> --issue <n> [--change <m>] [--doc <path>]... [--allow-derived-rules] [--resume]
//   node build-pack.mjs check --config <pipeline.json>
//   node build-pack.mjs queue add --config <pipeline.json> (--issue <n> [--change <m>] [--doc <path>]... [--allow-derived-rules] | --suite <code>) [--resume] [--now] [--restore <unit>]... [--restore-paused]
//   node build-pack.mjs queue remove --config <pipeline.json> --job <id>
//   node build-pack.mjs queue fill --config <pipeline.json>
//   node build-pack.mjs queue check --config <pipeline.json>
//   node build-pack.mjs queue run --config <pipeline.json> [--cutoff HH:MM]
//   node build-pack.mjs queue start --config <pipeline.json> --job <id> [--cutoff HH:MM] [--restore <unit>]... [--restore-paused]
//   node build-pack.mjs queue restore --config <pipeline.json>
//   node build-pack.mjs queue cancel --config <pipeline.json> --job <id>
//   node build-pack.mjs queue status --config <pipeline.json> [--job <id>]
//   node build-pack.mjs queue watch --config <pipeline.json> --job <id>
//   node build-pack.mjs queue summary --config <pipeline.json>
//   node build-pack.mjs report --config <pipeline.json> [--period day|week|auto] [--seed <n>]
//   node build-pack.mjs compare --reference <xlsx> --pack <xlsx> --rules <export> --doc <md> [--out <dir>] [--standard <md>] [--config <pipeline.json> [--no-model]]
//
// Console output is the content-free status lines only: phase names, pass or
// fail, reason codes, counts and timings. What the model wrote stays in each
// job's output folder.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { pauseFailures, setupCheck, sudoListing, sudoersRefused } from './check.mjs';
import { runCompare, UsageError } from './compare.mjs';
import { sleepUnlessAborted } from './abort.mjs';
import { countedTries, fill, globFiles, heldRow, holdsRow, loadConfig, MAX_MEMORY_STOPS, MAX_TRIES, MEMORY_STOP,
  memoryStops, rootRelative, worktreeRefusal } from './config.mjs';
import { modelClient } from './model.mjs';
import { createAppCloser } from './close-apps.mjs';
import { createPauser, downUnits, failedStartUnits, markRestoreFile, onPauseList, pendingRestore } from './pause.mjs';
import { documentRules, phase2Verdict, USABLE_RULE_CODES } from './phases.mjs';
import { createReleaser } from './release.mjs';
import { replayModel, replaySource } from './replay.mjs';
import { seededRandom, writeReports } from './report.mjs';
import { jobId, PHASES, readCheckpoint, runJob } from './run.mjs';
import { compareSnapshots, jobParameters, prepareSandbox, prepareStepSandbox, sandboxId, sandboxRun, sliceRange,
  stepStart } from './rerun.mjs';
import { checkStep, runStep, stepUsesModel } from './step-job.mjs';
import { lineArgs, sourceLines } from './sources.mjs';
import { fitCounts, jobLogs, readStatusLog, recordedRuns, repeatedCuts, runCuts, statusFields } from './status.mjs';
import { POLL_MS, touchHeartbeat, WAIT_ENDS } from './supervisor.mjs';

const USAGE = `usage:
  build-pack.mjs run --config <file> (--issue <n> [--change <m>] [--doc <path>]... [--allow-derived-rules] | --suite <code>) [--resume]
  build-pack.mjs run --config <file> --job <id> --from <phase> [--until <phase>] [--as <label>] [--pause] [--model replay:<source> [--replay-miss fail|live]]
  build-pack.mjs step --config <file> --job <id> --at <phase|sandbox> (draft | build | checklist | walk [--check <names>] | repair --finding <n> | confidence [--field <name>]) [--as <label>] [--pause] [--model replay:<source> [--replay-miss fail|live]]
  build-pack.mjs check --config <file> --issue <n> [--change <m>] [--doc <path>]... [--allow-derived-rules] [--resume]
  build-pack.mjs check --config <file>
  build-pack.mjs queue add --config <file> (--issue <n> [--change <m>] [--doc <path>]... [--allow-derived-rules] | --suite <code>) [--resume] [--now] [--restore <unit>]... [--restore-paused]
  build-pack.mjs queue remove --config <file> --job <id>
  build-pack.mjs queue fill --config <file>
  build-pack.mjs queue check --config <file>
  build-pack.mjs queue run --config <file> [--cutoff HH:MM]
  build-pack.mjs queue start --config <file> --job <id> [--cutoff HH:MM] [--restore <unit>]... [--restore-paused]
  build-pack.mjs queue restore --config <file>
  build-pack.mjs queue cancel --config <file> --job <id>
  build-pack.mjs queue status --config <file> [--job <id>]
  build-pack.mjs queue watch --config <file> --job <id>
  build-pack.mjs queue summary --config <file>
  build-pack.mjs report --config <file> [--period day|week|auto] [--seed <n>]
  build-pack.mjs compare --reference <xlsx> --pack <xlsx> --rules <export> --doc <md> [--out <dir>] [--standard <md>] [--config <file> [--no-model]]
exit codes of check and queue check: 0 every input present, 1 an input missing or, for check, a pause unit that fails the setup check (or, for queue check, the queue stayed held, a source could not be read, or a check or the pre-check failed), 3 documents not named, so their rules are unchecked
exit codes of run --job: 0 the slice passed, 1 it stopped (a replayed call the recording could not answer stops it unless --replay-miss live) or the queue is running, 2 bad arguments, a job with no folder, a missing snapshot, or a replay source with no recorded calls
exit codes of step: 0 the step ran and its build passed, 1 it stopped, its build failed a sheet, or the queue is running, 2 bad arguments, a job with no folder, a missing snapshot or step state, or a replay source with no recorded calls
exit codes of queue restore: 0 every unit started, 1 a unit did not start, or the queue is running
exit codes of check --config <file> alone, the setup check: 0 every check passed, 1 any failed, 2 bad config
exit codes of queue cancel: 0 the job stopped, 1 the job is not running, 4 the queue stayed held after the stop request
exit codes of compare: 0 the comparison was written, 1 it failed while running, 2 bad arguments or unreadable input`;

export function parseArgs(argv) {
  const args = { docs: [] };
  // `compare` takes --model as a switch; `run` and `step` give it a value, `replay:<job>`.
  const modelSwitch = argv[0] === 'compare';
  for (let i = 0; i < argv.length; i += 1) {
    const flag = argv[i];
    const value = argv[i + 1];
    if (!flag.startsWith('--')) {
      (args.words ??= []).push(flag);
      continue;
    }
    // --resume, --now, --allow-derived-rules, --restore-paused, --pause, --no-model and compare's --model take no value.
    if (flag === '--resume' || flag === '--now' || flag === '--allow-derived-rules' || (flag === '--model' && modelSwitch)
      || flag === '--no-model' || flag === '--restore-paused' || flag === '--pause') {
      args[flag.slice(2).replace(/-(\w)/g, (_, c) => c.toUpperCase())] = true;
      continue;
    }
    i += 1;
    if (flag === '--doc') args.docs.push(value);
    else if (flag === '--restore') (args.restore ??= []).push(value);
    else args[flag.slice(2).replace(/-(\w)/g, (_, c) => c.toUpperCase())] = value;
  }
  return args;
}

/** The job a command line names, or an error saying what it lacks. */
export function jobFrom(args) {
  if (args.suite && args.issue) throw new Error('a job names an issue or a suite, not both');
  if (args.suite) {
    if (!/^[A-Za-z0-9_-]+$/.test(args.suite)) throw new Error('--suite takes a suite code');
    if (args.allowDerivedRules) throw new Error('--allow-derived-rules does not apply to a suite');
    return { suite: args.suite, ...(args.resume ? { resume: true } : {}) };
  }
  if (!/^\d+$/.test(args.issue ?? '')) throw new Error('--issue takes a number');
  if (args.change !== undefined && !/^[A-Za-z0-9_-]+$/.test(args.change)) {
    throw new Error('--change takes a change number');
  }
  return { issue: args.issue, ...(args.change ? { change: args.change } : {}),
    ...(args.docs.length ? { docs: args.docs } : {}),
    ...(args.descriptionFile ? { descriptionFile: args.descriptionFile } : {}),
    ...(args.allowDerivedRules ? { allowDerivedRules: true } : {}),
    ...(args.resume ? { resume: true } : {}) };
}

/**
 * The counts a gate stop names: how many documents and which, by number. Codes and numbers
 * only, and a long list of numbers is cut to what a status line holds, so a row stored with
 * the full list still prints.
 */
const STOP_FIELDS = ['documents', 'numbers', 'document'];
const stopFields = (from = {}) => fitCounts(Object.fromEntries(
  STOP_FIELDS.filter((key) => from[key] !== undefined).map((key) => [key, from[key]])));

/** The stop fields of the last `fail` line a run wrote for `reason`, for a row that holds none. */
const loggedStop = (entries, reason) => stopFields(
  entries.findLast((e) => e.event === 'fail' && e.phase !== 'release' && e.reason === reason) ?? {});

/** A stopped row's document count and numbers as summary text, or nothing. */
const stopText = (row) => (row.documents !== undefined ? `, documents ${row.documents}${row.numbers !== undefined ? ` (${row.numbers})` : ''}`
  : row.document !== undefined ? `, document ${row.document}` : '');

/**
 * The checkpoint's documents, as the lines a resumed run would earn: Phase 2 reads
 * the rule export again for each Included document that has a file, so those are
 * checked with the same verdict Phase 2 uses. A checkpoint past Phase 2 does not
 * read the export again. Nothing but codes and numbers reaches the lines.
 */
function checkpointDocuments(ctx, saved, add) {
  const { config } = ctx;
  add('checkpoint', true, saved.phase);
  const docs = saved.state?.documents;
  if (!Array.isArray(docs)) {
    add('documents', false, 'no-checkpoint-documents');
    return;
  }
  if (PHASES.indexOf(saved.phase) >= PHASES.indexOf('phase2')) {
    add('documents', true, 'past-phase2');
    return;
  }
  docs.forEach((doc, i) => {
    const input = `document-${doc.number ?? i + 1}`;
    // Inclusion is decided in Phase 1; at intake every document counts as Included.
    if (saved.phase !== 'intake' && doc.inclusion !== 'Included') return add(input, true, 'context-only');
    if (!doc.file) return add(input, true, doc.ruleCode ?? 'rules-held');
    const { code } = documentRules(ctx, config.at(rootRelative(config, doc.file)));
    add(input, !phase2Verdict(doc, code).stop, code);
  });
}

/**
 * The input gates for an issue job, with no model call: one line per input,
 * `<input>  present|missing  <code>`, whether every required input is
 * present, and whether the documents' rules went unchecked. Documents are named by number and nothing from a document or a
 * rule reaches the lines; what was wrong with a rule export goes to the
 * check's own detail.log. Without `--doc`, the model chooses the documents at
 * intake, so their rules are not checked here.
 */
export function checkJob(config, job) {
  const lines = [];
  let unchecked = false;
  const add = (input, present, code) => lines.push(
    { input, present, text: `${input}  ${present ? 'present' : 'missing'}  ${code}` });
  add('issue-number', /^\d+$/.test(job.issue ?? ''), 'issue');
  const descriptionFiles = job.descriptionFile ? [config.at(job.descriptionFile)]
    : config.inputs.description ? globFiles(config.root, fill(config.inputs.description, job)) : [];
  const description = descriptionFiles.filter((f) => fs.existsSync(f))
    .map((f) => fs.readFileSync(f, 'utf8')).join('').trim();
  add('description', Boolean(description), description ? 'found' : 'no-description');
  const saved = job.resume ? readCheckpoint(path.join(config.output, jobId(job))) : null;
  const ctx = saved || job.docs?.length
    ? { config, job, logs: jobLogs(path.join(config.output, `${jobId(job)}.check`), { echo: false }) } : null;
  if (saved) {
    checkpointDocuments(ctx, saved, add);
  } else if (job.docs?.length) {
    job.docs.forEach((doc, i) => {
      const file = config.at(rootRelative(config, doc));
      const { code } = documentRules(ctx, file);
      add(`document-${i + 1}`, USABLE_RULE_CODES.includes(code), code);
    });
  } else {
    const candidates = config.inputs.documentIndex
      ? globFiles(config.root, fill(config.inputs.documentIndex, job)) : [];
    add('documents', candidates.length > 0, candidates.length ? `candidates=${candidates.length}` : 'no-candidates');
    if (candidates.length) unchecked = true;
  }
  if (unchecked) lines.push({ input: 'rules', present: true, text: 'rules  unchecked  name-documents-with-doc' });
  return { lines: lines.map((line) => line.text), ok: lines.every((line) => line.present), unchecked };
}

/**
 * The input gates of `checkJob` plus the pause units that fail the setup
 * check, as the same `pause  <unit>  fail  <code>` lines. A unit the run could
 * not stop or start leaves the machine as it was, so a check that ran only
 * this is where that shows up before the job is queued.
 */
export function checkJobAndHost(config, job, { exec } = {}) {
  const checked = checkJob(config, job);
  const pause = pauseFailures(config, { exec });
  return { ...checked, lines: [...checked.lines, ...pause], ok: checked.ok && !pause.length };
}

// How long a stopped run has to end its own cleanup before the process exits anyway.
const STOP_GRACE_MS = 120000;

const queuePath = (config) => config.at(config.queue.file);

export function readQueue(config) {
  const file = queuePath(config);
  if (!fs.existsSync(file)) return { jobs: [] };
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

/** Writes a whole file at once, so a reader never sees half of it. */
function writeAtomic(file, text) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  // A temp name per process, so two writers never share one.
  const temp = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(temp, text);
  fs.renameSync(temp, file);
}

function writeQueue(config, queue) {
  writeAtomic(queuePath(config), `${JSON.stringify(queue, null, 1)}\n`);
}

/** A job with its document and description paths relative to the root, so a queue row outlives any worktree. */
export function atRoot(config, job) {
  return {
    ...job,
    ...(job.docs ? { docs: job.docs.map((doc) => rootRelative(config, doc)) } : {}),
    ...(job.descriptionFile ? { descriptionFile: rootRelative(config, job.descriptionFile) } : {}),
  };
}

export function addJob(config, given, now = new Date()) {
  const job = atRoot(config, given);
  const queue = readQueue(config);
  const id = jobId(job);
  const open = queue.jobs.find((row) => row.id === id && ['queued', 'running'].includes(row.status));
  if (open) {
    if (open.status === 'running') return { id, added: false, running: true };
    // A request on a row that is waiting for tonight changes what it will run:
    // start-now, resume, derived rules and the named documents ride along.
    const merged = [];
    if (job.now && !open.now) merged.push('now');
    if (job.resume && !open.resume) merged.push('resume');
    if (job.allowDerivedRules && !open.allowDerivedRules) merged.push('allowDerivedRules');
    if (job.docs?.length && JSON.stringify(job.docs) !== JSON.stringify(open.docs)) merged.push('docs');
    for (const field of merged) open[field] = job[field];
    if (merged.length) writeQueue(config, queue);
    if (!merged.length) return { id, added: false, running: false };
    const rest = merged.filter((field) => field !== 'now');
    return { id, added: false, ...(merged.includes('now') ? { marked: true } : {}),
      ...(rest.length ? { merged: rest } : {}) };
  }
  queue.jobs.push({ id, ...job, status: 'queued', added: now.toISOString() });
  writeQueue(config, queue);
  return { id, added: true };
}

/**
 * The units a command line marks to be restored: each `--restore` unit must be
 * on the pause list, and `--restore-paused` adds the pause-list units that are
 * down now. Throws when a unit is not on the list.
 */
export function restoreUnits(config, args, { exec } = {}) {
  const units = [];
  for (const unit of args.restore ?? []) {
    if (!onPauseList(config.pause.units, unit)) throw new Error(`--restore ${unit} is not on pause.units`);
    units.push(unit);
  }
  if (args.restorePaused) units.push(...downUnits(config, { exec }));
  return [...new Set(units)];
}

/**
 * The units a command line asks to restore, less those sudoers will not let
 * the run start. The system scope starts them through `sudo -n`, so a refused
 * unit would be marked and then fail when the run ends. Returns the units to
 * mark and the ones refused.
 */
export function restoreRequest(config, args, { exec } = {}) {
  const wanted = restoreUnits(config, args, { exec });
  if (!wanted.length || config.pause.scope === 'user') return { units: wanted, refused: [] };
  const listing = sudoListing(exec);
  const refused = wanted.filter((unit) => sudoersRefused(listing, unit, ['start']).length);
  return { units: wanted.filter((unit) => !refused.includes(unit)), refused };
}

/**
 * Marks units to start when the job's run ends. A waiting row carries them
 * until the run takes it; for a row that is running, the run already holds the
 * queue, so they go to the state file its pauser reads when it ends. Returns
 * false when the job is neither waiting nor running.
 */
export function markRestore(config, id, units) {
  if (!units.length) return true;
  const queue = readQueue(config);
  const row = queue.jobs.findLast((r) => r.id === id && ['queued', 'running'].includes(r.status));
  if (!row) return false;
  if (row.status === 'running') {
    markRestoreFile(config, units);
    return true;
  }
  row.restore = [...new Set([...(row.restore ?? []), ...units])];
  writeQueue(config, queue);
  return true;
}

/**
 * Marks the units of a request on the job and says what it did: the units the
 * run will start when it ends, and each refused unit, which is not marked.
 * Returns false when the job is neither waiting nor running.
 */
export function markRestoreRequest(config, id, { units, refused }, log = console.log) {
  // An empty mark list needs no row, so a request refused in full looks for the job itself.
  const open = readQueue(config).jobs.some((row) => row.id === id && ['queued', 'running'].includes(row.status));
  if (!open && (units.length || refused.length)) return false;
  if (!markRestore(config, id, units)) return false;
  if (units.length) log(`${id} restores ${units.join(' ')} when it ends`);
  for (const unit of refused) {
    log(`restore  ${unit}  refused  sudoers-refused start; not marked. `
      + 'Start it by hand when the run ends, or allow it in sudoers first');
  }
  return true;
}

/**
 * The units waiting to be started: those the state file holds and those a
 * waiting row carries. A unit whose last start failed is listed apart, with
 * the next step.
 */
export function restoreLines(config) {
  const failed = failedStartUnits(config);
  const units = new Set(pendingRestore(config));
  for (const row of readQueue(config).jobs) {
    if (row.status === 'queued') (row.restore ?? []).forEach((unit) => units.add(unit));
  }
  failed.forEach((unit) => units.delete(unit));
  const user = config.pause.scope === 'user';
  const cause = user ? '' : ' once the cause is fixed, such as a missing sudoers rule';
  return [
    ...(units.size ? [`restore pending ${[...units].join(' ')}`] : []),
    ...(failed.length ? [`restore start-failed ${failed.join(' ')}; start each by hand with `
      + `${user ? 'systemctl --user start' : 'sudo systemctl start'}, `
      + 'then remove its name from the .paused file beside the queue file. '
      + `queue restore tries the start again${cause}`] : []),
  ];
}

/**
 * Starts every unit the state file holds and drops the marks from waiting
 * rows. Run it with the queue held. Returns the units that did not start.
 */
export async function restorePaused(config, { pause = (cfg) => createPauser(cfg) } = {}) {
  const queue = readQueue(config);
  // Marks still on waiting rows are recorded first, so the same start covers them.
  markRestoreFile(config, queue.jobs.filter((row) => row.status === 'queued').flatMap((row) => row.restore ?? []));
  const failedStart = await pause(config).resume();
  let changed = false;
  for (const row of queue.jobs) {
    if (row.restore && row.status === 'queued') {
      delete row.restore;
      changed = true;
    }
  }
  if (changed) writeQueue(config, queue);
  return failedStart;
}

/**
 * Takes a waiting job out of the queue. The row stays as `removed`, so a
 * source that still lists the job does not queue it again.
 */
export function removeJob(config, id, now = new Date()) {
  const queue = readQueue(config);
  const row = queue.jobs.findLast((r) => r.id === id && ['queued', 'running'].includes(r.status));
  if (!row) return { id, removed: false, running: false };
  if (row.status === 'running') return { id, removed: false, running: true };
  Object.assign(row, { status: 'removed', finished: now.toISOString() });
  delete row.notBefore;
  writeQueue(config, queue);
  return { id, removed: true };
}

/** The job a source line names, or null for a blank or comment line. */
export function jobFromLine(line) {
  const text = line.trim();
  if (!text || text.startsWith('#')) return null;
  return jobFrom(parseArgs(lineArgs(text)));
}

/**
 * Queues every job the configured sources list that the queue has not seen.
 * A job already in the queue file in any state, queued, passed, failed or
 * removed, is not queued again; `queue add` is how a finished or dropped job
 * is run once more. A source that cannot be read, or a line that is not a
 * job, is counted and skipped so the other sources still fill the queue.
 */
export function fillQueue(config, now = new Date()) {
  const { jobs, ...result } = sourceJobs(config);
  for (const job of jobs) addJob(config, job, now);
  return { added: jobs.map(jobId), ...result };
}

/**
 * The jobs the configured sources list that the queue has not seen, without
 * queueing them, with the counts `fillQueue` reports.
 */
export function sourceJobs(config) {
  const seen = new Set(readQueue(config).jobs.map((row) => row.id));
  const result = { jobs: [], known: 0, invalid: 0, errors: [] };
  for (const source of config.queue.sources) {
    const { lines, error, invalid = 0 } = sourceLines(config, source);
    result.invalid += invalid;
    if (error) result.errors.push(`${source.type}:${error}`);
    for (const line of lines) {
      let job;
      try {
        job = jobFromLine(line);
      } catch {
        result.invalid += 1;
        continue;
      }
      if (!job) continue;
      const id = jobId(job);
      if (seen.has(id)) {
        result.known += 1;
        continue;
      }
      seen.add(id);
      result.jobs.push(job);
    }
  }
  return result;
}

/** The first moment at or after `from` whose clock reads HH:MM. */
export function cutoffAfter(from, hhmm) {
  const time = /^([01]?\d|2[0-3]):([0-5]\d)$/.exec(String(hhmm));
  if (!time) throw new Error('a queue time reads HH:MM');
  const [h, m] = [Number(time[1]), Number(time[2])];
  const at = new Date(from);
  at.setHours(h, m, 0, 0);
  if (at <= from) at.setDate(at.getDate() + 1);
  return at;
}

const lockPath = (config) => `${queuePath(config)}.lock`;

/** The fields of /proc/<pid>/stat after the command name, or null where /proc has none. */
function procFields(pid) {
  try {
    const stat = fs.readFileSync(`/proc/${pid}/stat`, 'utf8');
    // The command name in field 2 may hold spaces, so count from the last ")".
    return stat.slice(stat.lastIndexOf(')') + 2).split(' ');
  } catch {
    return null;
  }
}

/** A process's start time in clock ticks since boot (Linux), or null where /proc has none. */
const processStart = (pid) => procFields(pid)?.[19] ?? null;

/** What a lock file holds: the holder's PID and, where known, its start time. */
const lockText = () => [process.pid, processStart(process.pid)].filter(Boolean).join(' ');

/**
 * True when the lock text names a live process. An empty or malformed file
 * names none. A PID alone proves little once PIDs are reused, so the start
 * time is compared when the file carries one.
 */
function holderAlive(text) {
  const [pid, start] = text.trim().split(/\s+/);
  if (!/^[1-9]\d*$/.test(pid ?? '')) return false;
  try {
    process.kill(Number(pid), 0);
  } catch {
    return false;
  }
  // A process that has exited but not been collected by its parent still answers a signal.
  if (procFields(pid)?.[0] === 'Z') return false;
  return !start || processStart(pid) === start;
}

function readLock(lock) {
  try {
    return fs.readFileSync(lock, 'utf8');
  } catch {
    return null;
  }
}

/** True when a live process holds the queue. */
export function lockHeld(config) {
  const text = readLock(lockPath(config));
  return text !== null && holderAlive(text);
}

/**
 * Removes a lock file that was judged stale from `seen`. The file is renamed
 * away first, so two starters cannot both remove it; if what was renamed is
 * not what was judged, it is put back and the lock stays someone else's.
 */
export function claimStale(lock, seen) {
  const claimed = `${lock}.stale-${process.pid}-${Date.now()}`;
  try {
    fs.renameSync(lock, claimed);
  } catch {
    // Another starter removed it first.
    return true;
  }
  if (fs.readFileSync(claimed, 'utf8') === seen) {
    fs.rmSync(claimed, { force: true });
    return true;
  }
  try {
    fs.linkSync(claimed, lock);
  } catch {
    // A newer lock already stands in its place.
  }
  fs.rmSync(claimed, { force: true });
  return false;
}

/** Holds the queue for this process, or returns null when a live process holds it. */
function lockQueue(config) {
  const lock = lockPath(config);
  fs.mkdirSync(path.dirname(lock), { recursive: true });
  const text = lockText();
  // A lock that vanishes between the failed create and the read was just
  // released, so that pass is retried; the bound only stops a runaway loop.
  for (let tries = 0; tries < 5; tries += 1) {
    // The text is written before the file appears under the lock's name, so no
    // other starter reads an empty lock.
    const temp = `${lock}.${process.pid}.tmp`;
    fs.writeFileSync(temp, text);
    try {
      fs.linkSync(temp, lock);
      // Only this process's own lock is removed; if the file was replaced,
      // it belongs to another holder.
      return () => {
        if (readLock(lock) === text) fs.rmSync(lock, { force: true });
      };
    } catch (error) {
      if (error.code !== 'EEXIST') throw error;
    } finally {
      fs.rmSync(temp, { force: true });
    }
    const seen = readLock(lock);
    if (seen === null) continue;
    if (holderAlive(seen) || !claimStale(lock, seen)) return null;
  }
  return null;
}

/**
 * Works the queue one job at a time, oldest first, until it is empty or the
 * cutoff passes. A job already running when the cutoff passes finishes. A
 * failed job goes back to waiting, with its phase and reason kept, and the next
 * one starts; a run does not take a job again that failed in it.
 *
 * With `start` set, the queue runs only in the window from start to cutoff: a
 * run that begins outside it, such as a timer catching up after the machine
 * slept through the night, takes no job. A job left running by a run that
 * died counts as a failed try, `interrupted`, and has no wait; a run that works
 * every queued row takes it again at once, while one that works only `now`
 * rows leaves it for the night, since the failed try cleared its mark.
 *
 * With `only` set to a job ID, the run takes that job's queued row first; with
 * no queued row of that ID it takes nothing. With `nowOnly` set, the jobs after
 * it are only rows marked `now`, those a user asked to start in the daytime,
 * and a row waiting for the nightly run stays queued. When a live process
 * holds the queue, a run first waits `settleMs` and tries once more, so a
 * holder that is finishing is not mistaken for a long one. Then, with `wait`
 * set, the run polls every `pollMs` until it gets the queue or the cutoff
 * passes, so a nightly run behind a daytime job still works the night's rows.
 * Without `wait`, `onBusy` is called and the row stays queued. A holder that
 * works every row takes it when it is due and has not failed in that run; a
 * holder that works only `now` rows takes it only if it is marked `now`.
 *
 * A job that fails during the night is queued again for the next nightly run,
 * and one that fails in the daytime for tonight's, resumed from the phase that
 * stopped it either way; one that has failed MAX_TRIES times stays failed and
 * is not taken again. With `refill` set, it is called once the queue is held and
 * before the first job is taken, to add the jobs the configured sources list.
 */
export async function drainQueue(config, { cutoff = config.queue.cutoff, start = null,
  only = null, nowOnly = false, wait = false, onBusy = () => {}, run = runJob, refill = null,
  clock = () => new Date(), sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  settleMs = 2000, pollMs = 30000, pause = (cfg) => createPauser(cfg),
  release = (cfg) => createReleaser(cfg), closeApps = (cfg) => createAppCloser(cfg),
  signal = null } = {}) {
  const stopAt = cutoffAfter(clock(), cutoff);
  if (start && cutoffAfter(clock(), start) < stopAt) return [];
  let unlock = lockQueue(config);
  if (!unlock) {
    await sleepUnlessAborted(sleep, settleMs, signal);
    unlock = signal?.aborted ? null : lockQueue(config);
  }
  // A stop request ends the wait, so the run does not take the queue after it.
  while (!unlock && wait && clock() < stopAt && !signal?.aborted) {
    await sleepUnlessAborted(sleep, pollMs, signal);
    unlock = signal?.aborted ? null : lockQueue(config);
  }
  if (!unlock) {
    onBusy();
    return [];
  }
  try {
    const stale = readQueue(config);
    const interrupted = stale.jobs.filter((row) => row.status === 'running');
    for (const row of interrupted) {
      settleRow(row, { ok: false, phase: 'unknown', reason: 'interrupted', ms: 0 }, clock(), config);
    }
    if (interrupted.length) writeQueue(config, stale);
    if (refill) refill(config);
    return await drainLocked(config, { stopAt, only, nowOnly, run, clock, pause, release, closeApps, signal });
  } finally {
    unlock();
  }
}

async function drainLocked(config, { pause, release, closeApps, run, signal, ...rest }) {
  // Made now so units a dead holder left stopped are found and restored even
  // when no job runs; nothing is stopped until a job is about to start.
  const pauser = pause(config);
  // The model is unloaded once, after the last job and after the units start
  // again, so a normal finish, a failure and the cutoff all end the same way
  // and no model is reloaded between jobs.
  const releaser = release(config);
  const noted = (cfg, job) => {
    releaser.note(job.id);
    return run(cfg, job, { signal });
  };
  try {
    return await drainJobs(config, { ...rest, run: noted, pauser, closer: closeApps(config), signal });
  } finally {
    try {
      await pauser.resume();
    } finally {
      releaser.release();
    }
  }
}

/** True when `at` falls in the nightly window, from the configured start to the cutoff. */
function inNightWindow(config, at) {
  return cutoffAfter(at, config.queue.start) > cutoffAfter(at, config.queue.cutoff);
}

// What a finished attempt does to its row. A first failure puts the job back in
// the queue to resume. One that failed during the night waits until that
// night's cutoff has passed, so only the next nightly run takes it; one that
// failed in the daytime is taken by tonight's run. A row found running after
// its run died has no wait; a run that works every queued row takes it at once,
// and one that works only `now` rows leaves it for the night.
function settleRow(row, result, at, config) {
  recordCuts(config, row);
  const failures = [...(row.failures ?? [])];
  if (result.reason === 'cancelled') {
    // A stop on request says nothing about the job: no failure is counted, and the
    // row keeps its checkpoint, so `queue add --resume` starts at the phase it stopped in.
    for (const field of ['started', 'now', 'ms', 'phase', 'reason', 'workbook', 'outDir', 'notBefore',
      'finished', ...STOP_FIELDS]) delete row[field];
    Object.assign(row, { status: 'stopped', resume: true, phase: result.phase ?? 'unknown',
      reason: 'cancelled', finished: at.toISOString(), ms: result.ms ?? 0,
      ...(failures.length ? { failures } : {}) });
    return;
  }
  if (!result.ok) {
    failures.push({ at: at.toISOString(), phase: result.phase ?? 'unknown',
      reason: result.reason ?? 'error', ms: result.ms ?? 0, ...stopFields(result.counts) });
  }
  for (const field of ['started', 'now', 'finished', 'ms', 'phase', 'reason', 'workbook', 'outDir',
    'notBefore', 'restore', ...STOP_FIELDS]) delete row[field];
  // A stop no retry can change waits for a person; its checkpoint is kept for `queue add --resume`.
  if (!result.ok && holdsRow(result)) {
    Object.assign(row, { status: 'stopped', resume: true, phase: result.phase ?? 'unknown',
      reason: result.reason, finished: at.toISOString(), ms: result.ms ?? 0, failures,
      ...stopFields(result.counts) });
    return;
  }
  // A failed revalidation is the review's verdict on the finished pack; a resume would skip
  // every phase and build the same pack again, so the job is not retried.
  const retry = result.reason !== 'gate:revalidation-failed';
  if (!result.ok && retry && countedTries(failures) < MAX_TRIES && memoryStops(failures) < MAX_MEMORY_STOPS) {
    const wait = result.reason !== 'interrupted' && inNightWindow(config, at);
    Object.assign(row, { status: 'queued', resume: true, failures,
      ...(wait ? { notBefore: cutoffAfter(at, config.queue.cutoff).toISOString() } : {}) });
    return;
  }
  Object.assign(row, {
    status: result.ok ? 'passed' : 'failed', finished: at.toISOString(),
    ms: result.ms, phase: result.ok ? 'done' : result.phase, reason: result.reason ?? null,
    workbook: result.workbook ?? null, outDir: result.outDir ?? null, ...stopFields(result.counts),
    ...(failures.length ? { failures } : {}),
  });
}

/**
 * Adds what the run that just ended did with its thinking steps to the row's `cuts`,
 * one entry per run that asked any, from the status lines it wrote since it started.
 * A job's folder holds only its latest run, so the row is the record that lets
 * `report` and `queue status --job` see a step cut on run after run.
 */
function recordCuts(config, row) {
  if (!row.started) return;
  const entries = readStatusLog(path.join(config.output, row.id, 'status.log'))
    .filter((e) => new Date(e.at) >= new Date(row.started));
  const { asked, cut } = runCuts(entries);
  if (asked.length) row.cuts = [...(row.cuts ?? []), { at: row.started, asked, cut }];
}

async function drainJobs(config, { stopAt, only, nowOnly, run, clock, pauser, closer, signal }) {
  const done = [];
  let first = only;
  let paused = false;
  // A job that failed in this run waits for a later one.
  const tried = new Set();
  for (;;) {
    if (clock() >= stopAt || signal?.aborted) break;
    const queue = readQueue(config);
    // A request to start a job now, by its ID or with --now, ignores the wait for the next nightly run.
    const next = queue.jobs.find((row) => row.status === 'queued' && !tried.has(row.id)
      && (!row.notBefore || clock() >= new Date(row.notBefore)
        || row.id === first || (nowOnly && row.now))
      && (first ? row.id === first : !nowOnly || row.now));
    if (!next) break;
    first = null;
    if (!paused) {
      paused = true;
      // A job started by hand with --now leaves the apps open unless the config says otherwise.
      if (!nowOnly || config.closeApps.onNow) closer.close();
      await pauser.pause({ until: stopAt, signal });
    } else {
      // A unit left busy before an earlier job is stopped now if its worker has finished.
      await pauser.pause({ until: clock(), signal });
    }
    // The wait can run into the cutoff; the units start again when the run ends.
    if (clock() >= stopAt || signal?.aborted) break;
    // Stopping the units can take minutes, so the row is claimed in a fresh read of the
    // queue file, which keeps a job added in the meantime.
    const fresh = readQueue(config);
    const claimed = fresh.jobs.find((row) => row.id === next.id && row.status === 'queued');
    if (!claimed) continue;
    claimed.status = 'running';
    claimed.started = clock().toISOString();
    // The marks go to the state file before the claim is written, so a run that dies
    // between the two does not lose them with the row's settled fields.
    if (claimed.restore?.length) pauser.mark(claimed.restore);
    writeQueue(config, fresh);
    const { id, status, added, started, now: _now, failures, notBefore, restore: _restore, cuts,
      ...job } = claimed;
    let result;
    try {
      result = await run(config, { ...job, id });
    } catch (error) {
      result = { ok: false, phase: 'setup', reason: 'error', ms: 0 };
    }
    const after = readQueue(config);
    let row = after.jobs.find((r) => r.id === id && r.status === 'running');
    if (!row) {
      // The queue file was replaced while the job ran and no longer holds its running row.
      row = { id, ...job, added, started, ...(failures ? { failures } : {}), ...(cuts ? { cuts } : {}) };
      after.jobs.push(row);
    }
    settleRow(row, result, clock(), config);
    tried.add(id);
    writeQueue(config, after);
    done.push(row);
    // The next job would meet the same low memory. A stop on request frees the machine, so
    // the rows still waiting stay queued for the next run.
    if (result.reason === MEMORY_STOP || result.reason === 'cancelled') break;
  }
  return done;
}

/** The phase a job was in when its run ended, read from the last line it wrote. */
function stoppedPhase(config, row) {
  const entries = readStatusLog(path.join(config.output, row.id, 'status.log'))
    .filter((e) => PHASES.includes(e.phase) && (!row.started || new Date(e.at) >= new Date(row.started)));
  const last = entries.at(-1);
  if (!last) return 'unknown';
  // A phase that passed leaves the next one as the phase a resume starts at.
  const next = last.event === 'pass' ? PHASES[PHASES.indexOf(last.phase) + 1] : null;
  return next ?? last.phase;
}

/**
 * Stops a running job and waits for its run to end. The lock's holder is sent
 * SIGTERM: it ends the model call, keeps the checkpoint, marks the row
 * `stopped`, starts the paused units again, unloads the model and frees the
 * queue. A row marked running with no live holder, left by a run that was
 * stopped from outside, is settled here the same way. Returns `cancelled` with
 * the row's phase, or the status the row has instead, or `timedOut` when the
 * queue stayed held for `waitMs`.
 */
export async function cancelJob(config, id, { clock = () => new Date(), kill = process.kill,
  sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)), waitMs = 150000, pollMs = 1000,
  pause = (cfg) => createPauser(cfg), release = (cfg) => createReleaser(cfg) } = {}) {
  const current = () => readQueue(config).jobs.findLast((r) => r.id === id);
  const first = current();
  if (first?.status !== 'running') return { id, cancelled: false, status: first?.status ?? 'not queued' };
  const holder = readLock(lockPath(config));
  if (holder !== null && holderAlive(holder)) {
    try {
      kill(Number(holder.trim().split(/\s+/)[0]), 'SIGTERM');
    } catch {
      // The holder ended on its own; the wait below finds the lock free.
    }
    const giveUp = clock().getTime() + waitMs;
    // The signalled process is waited for, not the lock: a run that was waiting for the
    // queue may take it the moment this process lets go.
    while (holderAlive(holder)) {
      if (clock().getTime() >= giveUp) return { id, cancelled: false, timedOut: true };
      await sleep(pollMs);
    }
  }
  let row = current();
  if (row?.status === 'running') {
    const held = withQueue(config, async () => {
      const queue = readQueue(config);
      const stale = queue.jobs.findLast((r) => r.id === id && r.status === 'running');
      if (stale) {
        settleRow(stale, { ok: false, phase: stoppedPhase(config, stale), reason: 'cancelled' }, clock(), config);
        writeQueue(config, queue);
      }
      await pause(config).resume();
      const releaser = release(config);
      releaser.note(id);
      releaser.release();
    });
    if (!held) return { id, cancelled: false, timedOut: true };
    await held.value;
    row = current();
  }
  return row?.status === 'stopped' && row.reason === 'cancelled' ? { id, cancelled: true, phase: row.phase }
    : { id, cancelled: false, status: row?.status ?? 'not queued' };
}

/**
 * Runs the phases `from` through `until` (`from` alone by default) of a job's
 * work in a sandbox, `<job>~<label>` with a time stamp for a label by default,
 * from the job's snapshot of the phase before `from`. The job's own folder,
 * queue row and workbook are only read. The run holds the queue, so the
 * nightly run waits for it; units are stopped only when `pauser` is given. A run
 * that `replayOnly` answers from recorded calls, with no live model, needs neither,
 * and holds nothing. It stops after `until` with no pack, no workbook and no model
 * unload. Returns `{ busy: true }` when a live process holds the queue, else `{ id,
 * result, lines }`, the lines being how the sandbox's pack at `until` differs from
 * the job's. Throws when an argument is wrong, the job has no folder or no
 * snapshot for the phase before `from`, or the sandbox exists; nothing is
 * written then.
 */
export async function rerunJob(config, { job, from, until, label, pauser = null },
  { run = runJob, now = () => new Date(), signal = null, replayOnly = false, ...options } = {}) {
  const range = sliceRange({ from, until });
  const id = sandboxId(job, label, now());
  const go = async () => {
    const parameters = jobParameters(readQueue(config).jobs, job);
    const resumes = prepareSandbox(config, job, id, range.from);
    const logs = jobLogs(path.join(config.output, id), { echo: false });
    // The sandbox's log starts with the job's lines; this one marks where the slice's own begin.
    logs.status({ job: id, phase: range.from, event: 'begin', until: range.until });
    let result;
    try {
      await pauser?.pause({ signal });
      result = await run(config, { ...parameters, id, ...(resumes ? { resume: true } : {}) },
        { ...options, signal, until: range.until });
    } catch (error) {
      // A run that threw before writing a line of its own leaves the slice's last word to this line.
      logs.status({ job: id, phase: range.from, event: 'fail', reason: 'error' });
      throw error;
    } finally {
      await pauser?.resume();
    }
    if (!result.ok) return { id, result, lines: [] };
    const { lines, detail } = compareSnapshots(path.join(config.output, job), path.join(config.output, id),
      range.until);
    if (detail) jobLogs(path.join(config.output, id), { echo: false }).detail('slice summary', detail);
    return { id, result, lines };
  };
  if (replayOnly) return go();
  const held = withQueue(config, go);
  return held ? held.value : { busy: true };
}

/**
 * Runs one step of a job's work on its own in a sandbox, `<source>~<label>` with a
 * time stamp for a label by default, over the job's snapshot of the phase `at` or the
 * state a step left in one of the job's sandboxes (see `runStep`). The job's own
 * folder, queue row and workbook are only read. A step that asks the model holds
 * the queue while it runs, so the nightly run waits for it, and stops units only when
 * `pauser` is given; a builder step, or a step that `replayOnly` answers from recorded
 * calls, holds nothing. Returns `{ busy: true }` when a live process holds the queue,
 * else `{ id, result }`. Throws when an argument is wrong, the job has no folder or no
 * state at `at`, or the sandbox exists; nothing is written then.
 */
export async function stepJob(config, { job, at, label, pauser = null, ...options },
  { run = runStep, now = () => new Date(), signal = null, replayOnly = false, ...runOptions } = {}) {
  const request = checkStep(options);
  const start = stepStart(config, job, at);
  const id = sandboxId(start.source, label, now());
  const go = async () => {
    const parameters = jobParameters(readQueue(config).jobs, job);
    prepareStepSandbox(config, start, id);
    return { id, result: await run(config, { id, job: parameters, ...request }, { ...runOptions, signal }) };
  };
  if (!stepUsesModel(request) || replayOnly) return go();
  const held = withQueue(config, async () => {
    try {
      await pauser?.pause({ signal });
      return await go();
    } finally {
      await pauser?.resume();
    }
  });
  return held ? held.value : { busy: true };
}

/** The morning summary: one content-free line per job. */
export function summaryLines(queue) {
  return queue.jobs.filter((row) => row.status !== 'removed').map((row) => {
    const minutes = row.ms ? `${Math.round(row.ms / 60000)} min` : '';
    const last = row.failures?.at(-1);
    const where = heldRow(row) ? `stopped at ${row.phase} (${row.reason}), waits for a person, resumable`
      + stopText(row)
      : row.status === 'stopped' ? `stopped at ${row.phase} (${row.reason}), resumable`
      : row.status === 'failed' ? `stopped at ${row.phase} (${row.reason})`
      + (countedTries(row.failures) >= MAX_TRIES ? `, dropped after failing ${MAX_TRIES} times` : '')
      + (memoryStops(row.failures) >= MAX_MEMORY_STOPS ? `, dropped after ${MAX_MEMORY_STOPS} low-memory stops in a row` : '')
      : row.status === 'passed' ? row.workbook ?? ''
        : row.status === 'queued' && last ? `retry after stopping at ${last.phase} (${last.reason})` : '';
    return [row.id, row.status, minutes, where].filter(Boolean).join('  ');
  });
}

/** A status line's label and fields as text; statusFields refuses any value that is not a short code. */
const fieldText = (label, fields) =>
  `${label} ${Object.entries(statusFields(fields)).map(([k, v]) => `${k}=${v}`).join(' ')}`;

/** How many of the entries share each combination of the given fields, in first-seen order. */
function tally(entries, keys) {
  const counts = new Map();
  for (const entry of entries) {
    const fields = Object.fromEntries(keys.map((key) => [key, entry[key] ?? '-']));
    const key = JSON.stringify(fields);
    counts.set(key, { fields, count: (counts.get(key)?.count ?? 0) + 1 });
  }
  return [...counts.values()];
}

/**
 * One job's state in content-free fields: its row's status, the last status
 * line its run wrote, and whether a live process holds the queue. Under those:
 * the phase now running and how long it has run, where a job that is not
 * running stopped, how long each finished phase took, and how many `retry` and
 * `call-fail` lines the job wrote by reason, with the phase and step of every
 * `length` and `runaway` cut. Then the last `check` and `repair` line the job
 * wrote. Last, every thinking step cut at its output budget
 * on two or more runs in a row, read from all of the job's rows, with its budget.
 * `clock` supplies the current time.
 */
export function jobStatus(config, id, { clock = () => new Date() } = {}) {
  const log = path.join(config.output, id, 'status.log');
  // A line cut off mid-write does not parse and is skipped.
  const logged = fs.existsSync(log) ? readStatusLog(log) : [];
  const queued = readQueue(config).jobs.findLast((r) => r.id === id);
  // A sandbox job has no queue row; its log, from the slice's first line on, says how the slice went.
  const sandbox = !queued && id.includes('~') ? sandboxRun(logged) : null;
  const row = queued ?? sandbox?.row;
  const lines = [`${id}  ${row ? row.status : 'not queued'}  queue ${lockHeld(config) ? 'held' : 'free'}`];
  if (!row) return lines;
  const all = sandbox ? sandbox.entries : logged;
  // The release line is written after the run ends, so it is shown on its own
  // and counts as none of the job's phases.
  const entries = all.filter((entry) => entry.phase !== 'release');
  const failures = row.failures ?? [];
  // Every attempt of a job appends to one log in the job's folder, and a row
  // added again for a resume starts after the phases that already passed, so
  // the finished phases and the counts read the whole log.
  // A queued row added without a resume starts over, and the run clears the
  // old log, so it carries nothing forward.
  const own = row.status === 'queued' && !row.resume ? [] : entries;
  // A resumed job appends to its earlier log, so only a line written since this
  // row started belongs to this attempt.
  const attempt = row.started
    ? entries.filter((entry) => new Date(entry.at) >= new Date(row.started)) : [];
  const last = attempt.at(-1);
  if (last) {
    // statusFields refuses any value that is not a short code, so a line that
    // carried text throws here instead of reaching the console.
    const { at, ...fields } = statusFields(last);
    lines.push(Object.entries(fields).map(([k, v]) => `${k}=${v}`).join(' '));
  }
  // A finished row no longer holds its start, so it has no job line above; the
  // release line follows the job's own last line when there is one.
  const from = row.finished ?? row.started;
  const released = from
    ? all.findLast((entry) => entry.phase === 'release' && new Date(entry.at) >= new Date(from)) : null;
  if (released) {
    const { at, ...fields } = statusFields(released);
    lines.push(Object.entries(fields).map(([k, v]) => `${k}=${v}`).join(' '));
  }
  const lastStart = attempt.findLastIndex((entry) => entry.event === 'start');
  const open = lastStart >= 0 && !attempt.slice(lastStart).some((entry) =>
    entry.event === 'pass' && entry.phase === attempt[lastStart].phase);
  if (row.status === 'running' && open) {
    const seconds = Math.max(0, Math.floor((clock() - new Date(attempt[lastStart].at)) / 1000));
    // A row still marked running with no live process was left by a run that
    // died, so its elapsed time is not progress.
    lines.push(fieldText(lockHeld(config) ? 'current' : 'interrupted',
      { phase: attempt[lastStart].phase, elapsed: `${seconds}s` }));
    // A phase waiting for the build supervisor's answers shows how many and how long it still waits.
    // A queue job's wait is live only while its run holds the queue. A sandbox's wait counts as
    // live until its end time and the poll after it, since a slice replayed with no live model
    // holds no lock and the log does not say which kind of slice ran.
    const waits = attempt.slice(lastStart);
    const waitAt = waits.findLastIndex((entry) => entry.event === 'waiting');
    const ended = waits.slice(waitAt + 1).some((entry) => WAIT_ENDS.includes(entry.event));
    if (waitAt >= 0 && !ended) {
      const { phase, questions, until } = waits[waitAt];
      const live = sandbox ? clock() - new Date(until) <= POLL_MS : lockHeld(config);
      const left = Math.max(0, Math.ceil((new Date(until) - clock()) / 60000));
      if (live) lines.push(fieldText('waiting', { phase, questions, left }));
    }
  } else if (['failed', 'stopped', 'queued'].includes(row.status)) {
    const where = row.status === 'queued' ? failures.at(-1) : row;
    if (where) {
      lines.push(fieldText('stopped', { phase: where.phase ?? '-', reason: where.reason ?? '-',
        ...(Object.keys(stopFields(where)).length ? stopFields(where) : loggedStop(all, where.reason)) }));
    }
  }
  const finished = new Map();
  for (const entry of own) {
    if (entry.event === 'pass' && entry.phase !== 'done') finished.set(entry.phase, entry.ms ?? 0);
  }
  for (const [phase, ms] of finished) lines.push(fieldText('done', { phase, ms }));
  for (const [event, label] of [['retry', 'retries'], ['call-fail', 'call-fails']]) {
    const hits = own.filter((entry) => entry.event === event);
    for (const { fields, count } of tally(hits, ['reason'])) lines.push(fieldText(label, { ...fields, count }));
  }
  const cuts = own.filter((entry) => ['retry', 'call-fail'].includes(entry.event)
    && ['length', 'runaway'].includes(entry.reason));
  for (const { fields, count } of tally(cuts, ['event', 'phase', 'step', 'reason'])) {
    lines.push(fieldText('cut', { ...fields, count }));
  }
  // The last verdict and the last repair the job logged, beside the phase timings.
  for (const [event, label] of [['check', 'last-check'], ['repair', 'last-repair']]) {
    const hit = own.findLast((entry) => entry.event === event);
    if (hit) {
      const { at, job, event: kind, ...fields } = hit;
      lines.push(fieldText(label, fields));
    }
  }
  for (const { step, budget, runs } of repeatedCuts(recordedRuns(readQueue(config), id))) {
    lines.push(fieldText('repeated-cut', { step, budget: budget ?? '-', runs }));
  }
  return lines;
}

/**
 * Every queue row in content-free fields, oldest first: its job ID, status,
 * the phase and reason code it stopped with, and when it last changed, so a
 * job that stopped or can resume shows without its ID being known.
 */
export function queueLines(queue, config) {
  if (!queue.jobs.length) return ['queue empty'];
  return queue.jobs.map((row) => {
    const failed = row.failures?.at(-1);
    let fields;
    if (row.status === 'running') {
      // A running row has no phase of its own; the last line its run wrote has.
      const entries = config ? readStatusLog(path.join(config.output, row.id, 'status.log')) : [];
      const last = entries.filter((e) => e.phase !== 'release'
        && new Date(e.at) >= new Date(row.started)).at(-1);
      fields = { phase: last?.phase ?? '-', reason: '-', updated: last?.at ?? row.started ?? '-' };
    } else if (row.status === 'queued') {
      fields = { phase: failed?.phase ?? '-', reason: failed?.reason ?? '-',
        updated: failed?.at ?? row.added ?? '-' };
    } else {
      fields = { phase: row.phase ?? '-', reason: row.reason ?? '-',
        updated: row.finished ?? row.added ?? '-' };
    }
    fields = { id: row.id, status: row.status, ...fields };
    const { id, ...rest } = statusFields(fields);
    return `${id}  ${Object.entries(rest).map(([k, v]) => `${k}=${v}`).join(' ')}`;
  });
}

/**
 * The queue's pre-check, which changes nothing in the queue. It runs the input
 * gates of `check`, with no model call, on every waiting row and on every job
 * the sources would queue tonight, and returns content-free lines, each
 * starting with a job ID, and an exit code like `check`'s: 1 when the queue
 * stayed held, a source could not be read, an input is missing or a check or
 * the pre-check itself failed, 3 when some rows'
 * rules went unchecked, else 0, and `at`, when the queue was read. The sources are read, not filled, so a line
 * fixed after the check still counts at the nightly fill.
 *
 * It holds no lock. While a run holds the queue it waits, polling every
 * `pollMs` up to `waitMs`, and then skips. With the queue free, a row still marked running was left by a run that died; the
 * nightly run settles it and runs it again, so it is checked too, unless that
 * was its last try and the settle drops it. A run that takes the queue
 * stops the check before its next row; a rule export already going finishes
 * first. A suite row
 * is refused, since `check` takes issue jobs only.
 */
export async function precheckQueue(config, { clock = () => new Date(),
  sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  waitMs = 60 * 60000, pollMs = 30000 } = {}) {
  const giveUp = clock().getTime() + waitMs;
  while (lockHeld(config)) {
    if (clock().getTime() >= giveUp) return { lines: ['queue  held  precheck-skipped'], code: 1, at: clock() };
    await sleep(pollMs);
  }
  const lines = [];
  const at = clock();
  let missing = false;
  let unchecked = false;
  try {
    const rows = readQueue(config).jobs.filter((row) => ['queued', 'running'].includes(row.status));
    const { jobs, ...fill } = sourceJobs(config);
    lines.push(`sources  ${fillSummary({ added: jobs, ...fill }, 'would queue')}`);
    // A source that cannot be read leaves its jobs out of tonight's queue.
    missing = fill.errors.length > 0;
    for (const job of [...rows, ...jobs]) {
      if (lockHeld(config)) {
        lines.push('queue  held  precheck-stopped');
        missing = true;
        break;
      }
      const id = jobId(job);
      if (job.status === 'running') {
        // Settling counts the interrupted try; on its last try the row is dropped, not run.
        if (countedTries(job.failures) + 1 >= MAX_TRIES) {
          lines.push(`${id}  running  stale-row-dropped`);
          continue;
        }
        lines.push(`${id}  running  stale-row`);
      }
      if (job.suite) {
        lines.push(`${id}  suite  refused`);
        continue;
      }
      let checked;
      try {
        // The nightly settle resumes a stale running row from its checkpoint, so it is checked that way.
        checked = checkJob(config, job.status === 'running' ? { ...job, resume: true } : job);
      } catch (error) {
        // The error's name only: a message could carry a path or a document's text.
        checked = { lines: [`check  failed  ${error.name}`], ok: false, unchecked: false };
      }
      for (const line of checked.lines) lines.push(`${id}  ${line}`);
      missing ||= !checked.ok;
      unchecked ||= checked.unchecked;
    }
  } catch (error) {
    // A queue file that does not parse, say: the lines so far stand.
    lines.push(`precheck  failed  ${error.name}`);
    missing = true;
  }
  return { lines, code: missing ? 1 : unchecked ? 3 : 0, at };
}

/** Where the pre-check writes its lines: the output folder, beside the job folders. */
export const precheckPath = (config) => path.join(config.output, 'precheck.txt');

/** A local clock reading, `YYYY-MM-DD HH:MM`, the time the timers are set in. */
export function localStamp(at) {
  const pad = (n) => String(n).padStart(2, '0');
  return `${at.getFullYear()}-${pad(at.getMonth() + 1)}-${pad(at.getDate())} `
    + `${pad(at.getHours())}:${pad(at.getMinutes())}`;
}

/** The job the command line names, with its documents relative to the root that runs it. */
function jobHere(args, config) {
  return atRoot(config, jobFrom(args));
}

/** The commands that run a job or put one on the queue; a worktree cannot hold a job's documents. */
const MAKES_JOBS = new Set(['run', 'check', 'queue add', 'queue fill', 'queue check', 'queue run',
  'queue start']);

async function main(argv) {
  const args = parseArgs(argv);
  const [command, sub] = args.words ?? [];
  if (command === 'compare') return compareCommand(args);
  if (!args.config || !command) {
    console.error(USAGE);
    return 2;
  }
  const config = loadConfig(args.config);
  // The setup check, `check` with no job named, reads the machine and makes no job.
  const setupOnly = command === 'check' && !args.issue && !args.suite && args.change === undefined
    && !args.docs.length && !args.allowDerivedRules;
  const refusal = !setupOnly && MAKES_JOBS.has(sub && command === 'queue' ? `queue ${sub}` : command)
    ? worktreeRefusal(config) : null;
  if (refusal) {
    console.error(refusal);
    return 2;
  }
  // While units are stopped, a signal starts them again before the process exits.
  const pausers = [];
  const releasers = [];
  const track = (cfg, deps) => {
    const pauser = createPauser(cfg, deps);
    pausers.push(pauser);
    return pauser;
  };
  const trackRelease = (cfg) => {
    const releaser = createReleaser(cfg);
    releasers.push(releaser);
    return releaser;
  };
  const exitNow = (name) => {
    Promise.all(pausers.map((p) => p.resume()))
      .finally(() => {
        for (const releaser of releasers) releaser.release();
        process.exit(128 + os.constants.signals[name]);
      });
  };
  // While a command runs jobs, the first signal stops the job in flight and lets the
  // run finish its own cleanup: the row is settled, the units start again, the model
  // unloads and the queue frees. A second signal, or a run that does not end in time,
  // starts the units and unloads the model here and exits.
  const control = { abort: null };
  let stopSignal = null;
  const onSignal = (name) => {
    if (control.abort && !control.abort.signal.aborted) {
      stopSignal = name;
      control.abort.abort();
      setTimeout(() => exitNow(name), STOP_GRACE_MS).unref();
      return;
    }
    exitNow(name);
  };
  const handlers = ['SIGTERM', 'SIGINT', 'SIGHUP'].map((name) => [name, () => onSignal(name)]);
  for (const [name, handler] of handlers) process.on(name, handler);
  try {
    const code = await dispatch(args, command, sub, config, track, trackRelease, control);
    // A stop that ended the run cleanly exits with the command's own code: 0 for a queue
    // command, 1 for `run`, whose job did not finish. A timer left from an interrupted wait would
    // keep the process alive, so it exits here; the forced path in exitNow exits 128 + signal.
    if (stopSignal) process.exit(code);
    return code;
  } finally {
    for (const [name, handler] of handlers) process.off(name, handler);
  }
}

/** Runs `fn` while this process holds the queue; null when a live process holds it. */
function withQueue(config, fn) {
  const unlock = lockQueue(config);
  if (!unlock) return null;
  let value;
  try {
    value = fn();
  } catch (error) {
    unlock();
    throw error;
  }
  // An async step keeps the lock until it settles.
  if (value instanceof Promise) return { value: value.finally(unlock) };
  unlock();
  return { value };
}

function busyQueue() {
  console.error('the queue is running; try again when the run ends');
  return 1;
}

/** The fill's outcome in content-free counts and codes. */
function printFill(result) {
  for (const id of result.added) console.log(`queued ${id}`);
  console.log(fillSummary(result));
}

function fillSummary({ added, known, invalid, errors }, verb = 'filled') {
  return `${verb} ${added.length} job(s), ${known} already known, ${invalid} unreadable line(s)`
    + (errors.length ? `, source problems: ${errors.join(' ')}` : '');
}

/** The compare command: a job config supplies the model endpoint and the workbook standard. */
async function compareCommand(args) {
  try {
    const lines = await runCompare(args, {
      standardFrom: (configPath) => {
        try {
          const config = loadConfig(configPath);
          const file = config.reference?.workbookStandard;
          return file ? fs.readFileSync(config.at(file), 'utf8') : '';
        } catch {
          throw new UsageError('--config could not be read');
        }
      },
      makeClient: (configPath) => {
        try {
          return modelClient(loadConfig(configPath).model);
        } catch {
          throw new UsageError('--config could not be read');
        }
      },
    });
    for (const line of lines) console.log(line);
    return 0;
  } catch (error) {
    if (error instanceof UsageError) throw error;
    // A failure while comparing is not a bad argument; the message names no content.
    console.error(`compare failed (${error.name})`);
    return 1;
  }
}

/**
 * The replaying model a command line names with `--model replay:<source>`, and whether the
 * run needs no live model at all, or null when it names none. `<source>` is a job or sandbox
 * ID, or a folder of call records. Throws, with nothing written, when the flags do not go
 * together or the source holds no calls.
 */
function replayHere(args, config) {
  if (!Object.hasOwn(args, 'model')) {
    if (Object.hasOwn(args, 'replayMiss')) throw new Error('--replay-miss goes with --model replay:<source>');
    return null;
  }
  const source = /^replay:(.+)$/s.exec(args.model ?? '')?.[1];
  if (!source) throw new Error('--model takes replay:<job or sandbox ID, or folder of call records>');
  const miss = args.replayMiss ?? 'fail';
  if (!['fail', 'live'].includes(miss)) throw new Error('--replay-miss takes fail or live');
  if (miss === 'fail' && args.pause) {
    throw new Error('--pause is for a run that can ask the live model; add --replay-miss live');
  }
  return { model: replayModel({ dir: replaySource(config, source), miss }), replayOnly: miss === 'fail' };
}

/** The options that hand a replaying model to a run, none when the command line names no replay. */
const replayOptions = (replay) => (replay ? { model: replay.model, replayOnly: replay.replayOnly } : {});

async function dispatch(args, command, sub, config, track, trackRelease, control) {
  const pause = (cfg) => track(cfg);
  const release = (cfg) => trackRelease(cfg);
  const replayFlag = [['model', '--model'], ['replayMiss', '--replay-miss']].find(([key]) => Object.hasOwn(args, key));
  if (replayFlag && command !== 'step' && !(command === 'run' && args.job !== undefined)) {
    throw new Error(`${replayFlag[1]} goes with step, or with run --job`);
  }
  if (command === 'step') {
    const stray = ['issue', 'suite', 'change', 'resume', 'allowDerivedRules', 'descriptionFile', 'now',
      'restore', 'restorePaused', 'from', 'until'].find((key) => args[key] !== undefined);
    if (stray || args.docs.length) throw new Error('step takes --job and --at; it takes no other job option');
    if (!/^[A-Za-z0-9_~-]+$/.test(args.job ?? '')) throw new Error('--job takes a job ID');
    if (args.at === undefined) throw new Error('--at takes a phase or a sandbox');
    const replay = replayHere(args, config);
    const pauser = args.pause ? track(config, { leftover: false }) : null;
    control.abort = new AbortController();
    const done = await stepJob(config, { job: args.job, at: args.at, step: sub, finding: args.finding,
      check: args.check, field: args.field, label: args.as, pauser },
    { signal: control.abort.signal, ...replayOptions(replay) });
    if (done.busy) return busyQueue();
    console.log(`sandbox ${done.id}`);
    for (const line of [...done.result.report, ...done.result.lines, ...(replay?.model.lines() ?? [])]) console.log(line);
    return done.result.ok && !done.result.failed ? 0 : 1;
  }
  if (command === 'run' && args.job !== undefined) {
    const stray = ['issue', 'suite', 'change', 'resume', 'allowDerivedRules', 'descriptionFile', 'now',
      'restore', 'restorePaused'].find((key) => args[key] !== undefined);
    if (stray || args.docs.length) throw new Error('--job names the job; it takes no other job option');
    if (!/^[A-Za-z0-9_~-]+$/.test(args.job)) throw new Error('--job takes a job ID');
    if (args.from === undefined) throw new Error('--from takes a phase');
    const replay = replayHere(args, config);
    const pauser = args.pause ? track(config, { leftover: false }) : null;
    control.abort = new AbortController();
    const done = await rerunJob(config, { job: args.job, from: args.from, until: args.until, label: args.as,
      pauser }, { signal: control.abort.signal, ...replayOptions(replay) });
    if (done.busy) return busyQueue();
    console.log(`sandbox ${done.id}`);
    for (const line of [...done.lines, ...(replay?.model.lines() ?? [])]) console.log(line);
    return done.result.ok ? 0 : 1;
  }
  const sliceFlag = ['from', 'until', 'as', 'pause'].find((key) => args[key] !== undefined);
  if (command === 'run' && sliceFlag) throw new Error(`--${sliceFlag} goes with --job`);
  if (command === 'run') {
    // No queue lock is held here, so this run leaves another holder's stopped units alone.
    const pauser = track(config, { leftover: false });
    control.abort = new AbortController();
    const { signal } = control.abort;
    try {
      await pauser.pause({ signal });
      const result = await runJob(config, jobHere(args, config), { signal });
      return result.ok ? 0 : 1;
    } finally {
      await pauser.resume();
    }
  }
  if (command === 'check' && !args.issue && !args.suite && args.change === undefined
    && !args.docs.length && !args.allowDerivedRules) {
    const { lines, ok } = await setupCheck(config);
    for (const line of lines) console.log(line);
    return ok ? 0 : 1;
  }
  if (command === 'check') {
    const job = jobHere(args, config);
    if (job.suite) throw new Error('check takes an issue job');
    const { lines, ok, unchecked } = checkJobAndHost(config, job);
    for (const line of lines) console.log(line);
    return !ok ? 1 : unchecked ? 3 : 0;
  }
  if (command === 'queue' && sub === 'add') {
    const request = restoreRequest(config, args);
    const { id, added, marked, merged, running } = addJob(config,
      { ...jobHere(args, config), ...(args.now ? { now: true } : {}) });
    markRestoreRequest(config, id, request);
    if (added) console.log(`queued ${id}`);
    else if (marked || merged?.length) {
      if (marked) console.log(`${id} is marked to start now`);
      if (merged?.length) console.log(`${id} is already queued; updated ${merged.join(', ')}`);
    } else console.log(running ? `${id} is already running` : `${id} is already queued`);
    return 0;
  }
  if (command === 'queue' && sub === 'remove') {
    if (!args.job) throw new Error('--job takes a job ID');
    const held = withQueue(config, () => removeJob(config, args.job));
    if (!held) return busyQueue();
    const { removed, running } = held.value;
    console.log(removed ? `removed ${args.job}` : running ? `${args.job} is marked running; it cannot be removed`
      : `${args.job} is not waiting in the queue`);
    return removed ? 0 : 1;
  }
  if (command === 'queue' && sub === 'fill') {
    const held = withQueue(config, () => fillQueue(config));
    if (!held) return busyQueue();
    printFill(held.value);
    return 0;
  }
  if (command === 'queue' && sub === 'check') {
    // The file reads `running` until the check ends, so a check stopped part
    // way, by the unit's timeout say, does not leave yesterday's lines standing.
    const write = (at, lines) => writeAtomic(precheckPath(config),
      `${[`checked ${localStamp(at)}`, ...lines].join('\n')}\n`);
    write(new Date(), ['precheck  running']);
    const { lines, code, at } = await precheckQueue(config);
    for (const line of lines) console.log(line);
    write(at, lines);
    return code;
  }
  if (command === 'queue' && sub === 'run') {
    const fillFirst = (cfg) => printFill(fillQueue(cfg));
    control.abort = new AbortController();
    const { signal } = control.abort;
    // A cutoff given on the command line is a deliberate run, outside the nightly window.
    const done = await drainQueue(config, args.cutoff
      ? { cutoff: args.cutoff, wait: true, pause, release, refill: fillFirst, signal }
      : { cutoff: config.queue.cutoff, start: config.queue.start, wait: true, pause, release,
        refill: fillFirst, signal });
    console.log(`ran ${done.length} job(s)`);
    for (const line of summaryLines(readQueue(config))) console.log(line);
    return 0;
  }
  if (command === 'queue' && sub === 'start') {
    if (!args.job) throw new Error('--job takes a job ID');
    const request = restoreRequest(config, args);
    if (!markRestoreRequest(config, args.job, request)) throw new Error(`${args.job} is not queued or running`);
    let busy = false;
    control.abort = new AbortController();
    // The cutoff is the configured one unless the command line gives another;
    // the nightly window does not apply to a job started on request.
    const done = await drainQueue(config, { cutoff: args.cutoff ?? config.queue.cutoff,
      only: args.job, nowOnly: true, pause, release, signal: control.abort.signal,
      onBusy: () => { busy = true; } });
    if (busy) {
      const row = readQueue(config).jobs.findLast((r) => r.id === args.job);
      console.log(row?.status === 'running' ? `${args.job} is already running`
        : `the queue is running; ${args.job} stays queued. A run that works every row takes it `
          + 'when it is due; one that works only start-now rows takes it only if it is marked now');
    } else {
      console.log(`ran ${done.length} job(s)`);
    }
    for (const line of jobStatus(config, args.job)) console.log(line);
    return 0;
  }
  if (command === 'queue' && sub === 'cancel') {
    if (!args.job) throw new Error('--job takes a job ID');
    const result = await cancelJob(config, args.job);
    if (result.cancelled) {
      console.log(`cancelled ${args.job}`);
      for (const line of jobStatus(config, args.job)) console.log(line);
      return 0;
    }
    if (result.timedOut) {
      console.error(`${args.job} did not stop in time; the queue is still held`);
      return 4;
    }
    console.error(result.status === 'running' ? `${args.job} is running`
      : `${args.job} is not running (${result.status})`);
    return 1;
  }
  if (command === 'queue' && sub === 'status') {
    const lines = args.job ? jobStatus(config, args.job) : queueLines(readQueue(config), config);
    for (const line of [...lines, ...restoreLines(config)]) console.log(line);
    return 0;
  }
  if (command === 'queue' && sub === 'watch') {
    // The build supervisor's check: the job's status, and a fresh heartbeat that tells the
    // job someone is there to answer its questions.
    if (!/^[A-Za-z0-9_~-]+$/.test(args.job ?? '')) throw new Error('--job takes a job ID');
    touchHeartbeat(config, args.job);
    for (const line of [...jobStatus(config, args.job), ...restoreLines(config)]) console.log(line);
    return 0;
  }
  if (command === 'queue' && sub === 'restore') {
    const held = withQueue(config, () => restorePaused(config, { pause }));
    if (!held) return busyQueue();
    const failedStart = await held.value;
    console.log(failedStart.length ? `could not start ${failedStart.join(' ')}` : 'restored the paused units');
    return failedStart.length ? 1 : 0;
  }
  if (command === 'queue' && sub === 'summary') {
    for (const line of summaryLines(readQueue(config))) console.log(line);
    return 0;
  }
  if (command === 'report') {
    const seed = args.seed ?? config.report.seed;
    const random = seed === undefined ? Math.random : seededRandom(seed);
    for (const { period, file, counts, queue } of writeReports(config, readQueue(config),
      { period: args.period, random })) {
      console.log(`wrote ${period} report ${file}`);
      console.log(`passed=${counts.pass} retrying=${counts.retry} dropped=${counts.dropped} `
        + `queued=${queue.depth}`);
    }
    return 0;
  }
  console.error(USAGE);
  return 2;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main(process.argv.slice(2)).then((code) => { process.exitCode = code; }, (error) => {
    // A setup error names the config field at fault, never document content.
    console.error(error.message);
    process.exitCode = 2;
  });
}
