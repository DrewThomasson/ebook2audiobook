// Runs one job, intake through Phase 10, and writes its pack, its workbook and
// its two logs to the job's own output folder. After each phase passes, the
// job's state goes to work/checkpoint.json, so a job run again with `resume`
// starts at the phase that stopped it, and to work/checkpoints/<phase>.json,
// so a later run can start from any phase that passed. With `until`, a run
// stops after that phase and writes no pack and no workbook.

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { fill, globFiles, loadReference, MEMORY_STOP, rootRelative } from './config.mjs';
import { MemoryLow, readMeminfo, waitForMemory } from './meminfo.mjs';
import { Cancelled, ModelError, modelClient } from './model.mjs';
import { ReplayMiss } from './replay.mjs';
import { fitCounts, jobLogs, readStatusLog } from './status.mjs';
import { postNotice, waitForAnswers } from './supervisor.mjs';
import * as P from './phases.mjs';

/** The objective config names for a set, else the usual name if the builder lists it, else none. */
const setObjective = (named, builder, usual) => named ?? (builder.OBJECTIVES.includes(usual) ? usual : null);

const DEFAULTS = {
  IMPACT_CLASSES: ['Direct Change', 'Indirect Impact', 'Regression', 'Not Impacted'],
  COVERAGE_STATUSES: ['Covered', 'Partially Covered', 'Weakly Covered', 'Missing', 'Not Applicable'],
  CONFIDENCE_LEVELS: ['High', 'Medium', 'Low'],
  DERIVATIONS: ['Requirement', 'Quality'],
  INCLUSIONS: ['Included', 'Supporting Context Only', 'Excluded'],
};

/** A job's id: its issue and change, or its suite, plus when it was added. */
export const jobId = (job) => (job.suite ? `suite-${job.suite}` : `issue-${job.issue}`
  + (job.change ? `-change-${job.change}` : ''));

/** The builder's validation lines, counted by status. Its notes stay in detail.log. */
export function countStatuses(stdout) {
  const counts = { pass: 0, limited: 0, fail: 0 };
  for (const line of stdout.split('\n')) {
    if (line.startsWith('PASS WITH LIMITATIONS')) counts.limited += 1;
    else if (line.startsWith('PASS')) counts.pass += 1;
    else if (line.startsWith('FAIL')) counts.fail += 1;
  }
  return counts;
}

/** The phases in the order a job runs them; a checkpoint names the last one passed. */
export const PHASES = ['intake', 'phase1', 'phase2', 'phase3', 'phase4', 'phase5', 'phase6',
  'phase7', 'phase8', 'phase9-checklist', 'phase9-senior', 'phase9-confidence',
  'phase9-revalidate', 'phase10'];

// What a run builds for itself from the config; everything else on ctx is the job's state.
const SETUP = new Set(['config', 'job', 'logs', 'builder', 'suiteMerge', 'model', 'ref', 'private',
  'existingTests', 'riskLevels', 'coreObjective', 'suiteSetOrder', 'suiteRunSets', 'fullCoverageObjective', 'breakItObjective', 'rulesFresh',
  'window', 'windowNoted', 'supervise']);

export const checkpointPath = (outDir) => path.join(outDir, 'work', 'checkpoint.json');

export function readCheckpoint(outDir) {
  try {
    const saved = JSON.parse(fs.readFileSync(checkpointPath(outDir), 'utf8'));
    // The confidence step used to run before the senior review; a job saved after it reruns both.
    if (saved.phase === 'phase9-confidence' && !saved.state?.confidenceSteps) saved.phase = 'phase9-checklist';
    return PHASES.includes(saved.phase) ? saved : null;
  } catch {
    return null;
  }
}

export const snapshotPath = (outDir, phase) => path.join(outDir, 'work', 'checkpoints', `${phase}.json`);

/** The state as `phase` passed, or null when the job has no snapshot for it. */
export function readSnapshot(outDir, phase) {
  try {
    const saved = JSON.parse(fs.readFileSync(snapshotPath(outDir, phase), 'utf8'));
    return saved.phase === phase ? saved : null;
  } catch {
    return null;
  }
}

/**
 * What a run builds for itself from the config, with no phase passed yet: the
 * builder and suite merge modules, the reference documents, and the context the
 * phases share. `job` carries its ID; `outDir` is the folder the job writes to.
 * Throws when the builder module lacks what the pipeline reads.
 */
export async function jobContext(config, job, { outDir, logs, model, signal = null }) {
  const builderModule = await import(pathToFileURL(config.at(config.builder.module)).href);
  if (typeof builderModule.buildPack !== 'function' || !Array.isArray(builderModule.OBJECTIVES)) {
    throw new Error('config builder.module exports no buildPack and OBJECTIVES');
  }
  const suiteMerge = job.suite && config.suiteMerge?.module
    ? await import(pathToFileURL(config.at(config.suiteMerge.module)).href) : null;
  if (job.suite && typeof suiteMerge?.mergeSuitePack !== 'function') {
    throw new Error('a suite job needs suiteMerge.module exporting mergeSuitePack');
  }
  const builder = { ...DEFAULTS, ...builderModule };
  const ctx = {
    config, job, logs, builder, suiteMerge,
    model: model ?? modelClient({ ...config.model, signal }),
    ref: loadReference(config),
    pack: {},
    riskLevels: config.riskLevels ?? ['High', 'Medium', 'Low'],
    coreObjective: config.coreObjective ?? builder.OBJECTIVES[0],
    fullCoverageObjective: setObjective(config.fullCoverageObjective, builder, 'Full Coverage Required Run'),
    breakItObjective: setObjective(config.breakItObjective, builder, 'BREAK IT'),
    suiteSetOrder: suiteMerge?.SUITE_SET_ORDER ?? builder.OBJECTIVES.slice(1),
    suiteRunSets: config.suiteMerge?.runSets ?? ['Regression Testing', 'Full Coverage Required Run'],
    calls: 0, repairs: 0, droppedObjectives: [], derived: 0, reviewIssues: 0, reuse: [],
    tokens: { prompt: 0, output: 0 },
    private(name, value) {
      fs.writeFileSync(path.join(outDir, 'work', name), `${JSON.stringify(value, null, 1)}\n`);
    },
  };
  // A replaying model answers from recorded calls and asks the live model only for a call
  // it was told to send there, so the live client is made when that first happens.
  model?.bind?.({ logs, job: job.id, live: () => modelClient({ ...config.model, signal }) });
  if (config.inputs.existingTests) {
    ctx.existingTests = globFiles(config.root, fill(config.inputs.existingTests, job))
      .map((file) => fs.readFileSync(file, 'utf8')).join('\n\n');
  }
  return ctx;
}

/**
 * Puts a saved state on the context and returns the saved pack. The documents are
 * read from the root this run has, whatever root wrote the state.
 */
export function restoreState(config, ctx, saved) {
  Object.assign(ctx, saved.state);
  for (const doc of ctx.documents ?? []) if (doc.file) doc.file = rootRelative(config, doc.file);
  if (ctx.documentPaths) {
    ctx.documentPaths = ctx.documentPaths.map((file) => rootRelative(config, file));
  }
  return saved.pack ?? ctx.pack;
}

/** A job's state as `phase` leaves it, as the text a snapshot holds: the context without what the run builds for itself. */
export function stateText(ctx, pack, phase) {
  const state = Object.fromEntries(Object.entries(ctx).filter(([key]) => !SETUP.has(key)));
  return JSON.stringify({ phase, state, pack: pack === ctx.pack ? undefined : pack });
}

export async function runJob(config, job, { model, echo = true, now = Date.now, readMemory = readMeminfo,
  sleep, signal = null, until = null, post = postNotice } = {}) {
  const id = job.id ?? jobId(job);
  const outDir = path.join(config.output, id);
  const saved = job.resume ? readCheckpoint(outDir) : null;
  // A job run again from the start begins with an empty folder, so no file from
  // the last run is read as this one's. A resumed job keeps its folder and logs.
  // A job that stopped for low memory before any phase passed has no checkpoint,
  // but its status.log keeps the wait and fail lines that show the host ran short,
  // so that log carries over into the new run.
  if (!saved) {
    const statusFile = path.join(outDir, 'status.log');
    const stop = job.resume
      ? readStatusLog(statusFile).filter((e) => e.phase !== 'release').at(-1) : null;
    const kept = stop?.event === 'fail' && stop.reason === MEMORY_STOP
      ? fs.readFileSync(statusFile, 'utf8') : null;
    fs.rmSync(outDir, { recursive: true, force: true });
    if (kept) {
      fs.mkdirSync(outDir, { recursive: true });
      fs.writeFileSync(statusFile, kept.endsWith('\n') ? kept : `${kept}\n`);
    }
  }
  fs.mkdirSync(path.join(outDir, 'work'), { recursive: true });
  const logs = jobLogs(outDir, { echo });
  const started = now();
  const ctx = await jobContext(config, { ...job, id }, { outDir, logs, model, signal });
  // At a question gate, a phase waits here for the build supervisor's answers.
  ctx.supervise = (name, questions) => waitForAnswers({ config, id, outDir, phase: name, questions, logs,
    now, ...(sleep ? { sleep } : {}), signal, post });

  // The merged suite pack is a separate object from ctx.pack once Phase 7 passes.
  let pack = ctx.pack;
  const done = saved ? PHASES.indexOf(saved.phase) : -1;
  if (saved) {
    pack = restoreState(config, ctx, saved);
    logs.status({ job: id, phase: PHASES[done + 1] ?? 'done', event: 'resume', after: saved.phase });
  }
  // The snapshot is written before checkpoint.json, so the latest checkpoint always has its snapshot.
  const checkpoint = (name) => {
    const text = stateText(ctx, pack, name);
    const snapshot = snapshotPath(outDir, name);
    fs.mkdirSync(path.dirname(snapshot), { recursive: true });
    for (const file of [snapshot, checkpointPath(outDir)]) {
      fs.writeFileSync(`${file}.tmp`, text);
      fs.renameSync(`${file}.tmp`, file);
    }
  };

  let phase = 'intake';
  // When the running phase began, in time and in calls, so a stop reports the phase's own
  // figures; `ownStats` holds them for a stop that is named for a phase already finished,
  // and is empty when that phase passed in an earlier run.
  let began = { t: started, calls: 0 };
  let ownStats = null;
  const passedStats = new Map();
  let warned = false;
  // Before a phase starts, the work so far is checkpointed, so this is where a stop loses nothing.
  const checkMemory = async (name) => {
    if (!config.memory.enabled) return;
    const outcome = await waitForMemory(config.memory, { read: readMemory, now, sleep, signal,
      onWait: (m) => logs.status({ job: id, phase: name, event: 'wait', reason: 'memory-low',
        availableMiB: m.availableMiB, swapPercent: m.swapPercent }) });
    // A stop during the wait ends it; nothing has started in this phase.
    if (signal?.aborted) throw new Cancelled();
    if (outcome.unreadable) {
      if (!warned) logs.status({ job: id, phase: name, event: 'warn', reason: 'meminfo-unreadable' });
      warned = true;
    } else if (outcome.polls > 0 && outcome.ok) {
      logs.status({ job: id, phase: name, event: 'memory-ok', polls: outcome.polls, waitedMs: outcome.waitedMs });
    } else if (!outcome.ok) {
      throw new MemoryLow({ polls: outcome.polls, waitedMs: outcome.waitedMs,
        availableMiB: outcome.availableMiB, swapPercent: outcome.swapPercent });
    }
  };
  const step = async (name, fn) => {
    phase = name;
    if (PHASES.indexOf(name) <= done || (until && PHASES.indexOf(name) > PHASES.indexOf(until))) return {};
    // A stop between phases loses nothing: the last phase that passed is checkpointed.
    began = { t: now(), calls: ctx.calls };
    if (signal?.aborted) throw new Cancelled();
    await checkMemory(name);
    const t = now();
    began = { t, calls: ctx.calls };
    logs.status({ job: id, phase: name, event: 'start' });
    const counts = await fn();
    const ms = now() - t;
    logs.status({ job: id, phase: name, event: 'pass', ms, ...counts });
    passedStats.set(name, { ms, calls: ctx.calls - began.calls });
    checkpoint(name);
    return counts;
  };
  const packName = fill(job.suite ? config.suitePackFile : config.packFile, job);
  const packPath = path.join(outDir, packName);
  let written = null;
  try {
    await P.readWindow(ctx, PHASES[done + 1] ?? 'done');
    await step('intake', () => P.intake(ctx));
    await step('phase1', () => P.phase1(ctx));
    await step('phase2', async () => {
      const counts = await P.phase2(ctx);
      ctx.derived = counts.derived;
      return counts;
    });
    await step('phase3', () => P.phase3(ctx));
    await step('phase4', () => P.phase4(ctx));
    await step('phase5', () => P.phase5(ctx));
    await step('phase6', () => P.phase6(ctx));
    await step('phase7', async () => {
      const counts = await P.phase7(ctx);
      if (job.suite) pack = P.mergeSuite(ctx);
      return counts;
    });
    // The first build checks everything Phase 9 does not fill; the review's sheets wait for
    // it. It ends by writing the Draft workbook the review starts from.
    await step('phase8', async () => {
      await P.phase8(ctx, pack, 'build', P.REVIEW_SHEETS);
      return { repairs: ctx.repairs };
    });
    await step('phase9-checklist', () => P.checklistRounds(ctx, pack));
    await step('phase9-senior', () => P.phase9SeniorReview(ctx, pack));
    await step('phase9-confidence', () => P.phase9Confidence(ctx, pack));
    await step('phase9-revalidate', async () => {
      delete pack.revalidation;
      // The rebuild writes the Draft workbook again, with the rating the review gave, held to
      // the confidence ceiling of the pack as it now stands.
      await P.phase8(ctx, pack, 'rebuild');
      const again = await P.revalidate(ctx, pack);
      // Items still open lower what the pack can claim, so the rating is made again with them in view.
      if (!again.passed) {
        return { revalidated: false, remaining: again.remaining,
          confidence: await P.reRateConfidence(ctx, pack) };
      }
      return { revalidated: again.passed, remaining: again.remaining };
    });
    await step('phase10', () => P.phase10(ctx, pack));
    if (until) {
      const summary = { job: id, phase: 'done', event: 'slice', until, ms: now() - started,
        calls: ctx.calls, promptTokens: ctx.tokens.prompt, outputTokens: ctx.tokens.output };
      logs.status(summary);
      return { ok: true, id, outDir, ...summary };
    }
    pack = P.reconcile(ctx, pack);
    fs.writeFileSync(packPath, `${JSON.stringify(pack, null, 1)}\n`);

    // The final write goes through the repository's own builder command, as the skill runs it.
    phase = 'phase8';
    began = { t: now(), calls: ctx.calls };
    const argv = config.builder.command.map((part) => fill(part, { pack: packPath, out: outDir }));
    const result = spawnSync(argv[0], argv.slice(1), { cwd: config.root, encoding: 'utf8' });
    logs.detail('builder final', `${result.stdout}\n${result.stderr}`);
    const counts = countStatuses(result.stdout);
    // A pack whose revalidation failed builds with Workbook Validation FAIL, and the
    // workbook is written so the reviewer can see what remains; any other FAIL is a build failure.
    const failLines = result.stdout.split('\n').filter((line) => line.startsWith('FAIL'));
    const revalidationFailed = pack.revalidation?.passed === false;
    const onlyValidation = failLines.length > 0
      && failLines.every((line) => /Workbook Validation\s*$/.test(line));
    if (result.status !== 0 && !(revalidationFailed && onlyValidation)) {
      throw new P.GateError('phase8', 'builder-final-fail', { sheets: counts.fail });
    }
    const workbook = fs.readdirSync(outDir).find((name) => name.endsWith('.xlsx')) ?? null;
    if (revalidationFailed) {
      // A workbook that does not show the FAIL is removed rather than left reading PASS.
      if (workbook && !onlyValidation) fs.rmSync(path.join(outDir, workbook));
      else if (workbook) written = path.join(outDir, workbook);
      phase = 'phase9-revalidate';
      ownStats = passedStats.get(phase) ?? {};
      throw new P.GateError('phase9', 'revalidation-failed', { remaining: pack.revalidation.remaining.length });
    }
    const summary = { job: id, phase: 'done', event: 'pass', ms: now() - started,
      calls: ctx.calls, promptTokens: ctx.tokens.prompt, outputTokens: ctx.tokens.output,
      sheetsPass: counts.pass, sheetsLimited: counts.limited, repairs: ctx.repairs };
    logs.status(summary);
    return { ok: true, id, outDir, packPath, workbook: workbook && path.join(outDir, workbook),
      ...summary };
  } catch (error) {
    const reason = error instanceof Cancelled ? 'cancelled' : error instanceof P.GateError ? `gate:${error.code}`
      : error instanceof ModelError ? `model:${error.code}`
        : error instanceof ReplayMiss ? `replay:${error.code}`
          : error instanceof MemoryLow ? `memory:${error.code}` : 'error';
    logs.detail('stopped', error.stack ?? String(error));
    const counts = error instanceof P.GateError || error instanceof MemoryLow ? error.counts : {};
    const own = ownStats ?? { ms: now() - began.t, calls: ctx.calls - began.calls };
    logs.status({ job: id, phase, event: 'fail', reason, ...own,
      jobMs: now() - started, jobCalls: ctx.calls, ...fitCounts(counts) });
    if (Object.keys(ctx.pack).length) {
      fs.writeFileSync(path.join(outDir, 'work', 'partial-pack.json'),
        `${JSON.stringify(ctx.pack, null, 1)}\n`);
    }
    return { ok: false, id, outDir, phase, reason, ms: now() - started, packPath, workbook: written,
      ...(error instanceof P.GateError ? { counts: error.counts } : {}) };
  }
}
