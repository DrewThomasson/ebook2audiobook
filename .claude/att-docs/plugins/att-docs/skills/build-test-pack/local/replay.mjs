// Answers a job's model calls from the calls an earlier run recorded in work/calls, so a
// change to the code around the model is tried against a real job with no model server.
// Each call takes the next recorded call for the same step and attempt, in the order they
// were made. A call whose prompt is not the recorded one is a miss: it is reported, and
// then it stops the run or goes to the live model, as the run was told.

import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { CALLS_VERSION, promptHash, schemaHash, USAGE_EXTRAS } from './calls.mjs';
import { estimateTokens, ModelError } from './model.mjs';

/** Why a call was not answered from the recording. */
export const MISS_REASONS = ['prompt-changed', 'schema-changed', 'thinking-changed', 'no-record'];

/** What a miss is called in a message: the step and what was different about it. */
const MISS_TEXT = { 'prompt-changed': 'prompt', 'schema-changed': 'schema', 'thinking-changed': 'thinking' };
const missText = (code, step) => (code === 'no-record' ? `replay: no recording for ${step}`
  : `replay: ${MISS_TEXT[code]} changed for ${step}`);

/**
 * A call the recording could not answer, and the run was told to stop. Not a ModelError,
 * so no phase retries it. `code` is one of MISS_REASONS and `step` the call's schema name;
 * the message holds only those, never the prompt.
 */
export class ReplayMiss extends Error {
  constructor(code, step) {
    super(missText(code, step));
    this.name = 'ReplayMiss';
    this.code = code;
    this.step = step;
  }
}

/** The most lines of one side of a diff that detail.log keeps, and the longest line it keeps whole. */
const DIFF_LINES = 20;
const LINE_WIDTH = 240;

const clip = (line) => (line.length > LINE_WIDTH ? `${line.slice(0, LINE_WIDTH)}...` : line);

/** The lines that differ between two texts, after the lines they share at the start and the end. */
function changedLines(was, now) {
  const a = was.split('\n');
  const b = now.split('\n');
  let head = 0;
  while (head < a.length && head < b.length && a[head] === b[head]) head += 1;
  let tail = 0;
  while (tail < a.length - head && tail < b.length - head
    && a[a.length - 1 - tail] === b[b.length - 1 - tail]) tail += 1;
  return { at: head + 1, removed: a.slice(head, a.length - tail), added: b.slice(head, b.length - tail) };
}

/**
 * How a call's prompt differs from the recorded one: the text for detail.log, with the
 * differing lines of the system and the user part (each side cut at DIFF_LINES), and
 * how many lines differ.
 */
export function promptDiff(was, now) {
  const out = [];
  let count = 0;
  for (const part of ['system', 'user']) {
    const { at, removed, added } = changedLines(was[part], now[part]);
    if (!removed.length && !added.length) continue;
    count += removed.length + added.length;
    out.push(`${part}, from line ${at}:`);
    for (const [mark, lines] of [['-', removed], ['+', added]]) {
      out.push(...lines.slice(0, DIFF_LINES).map((line) => `${mark} ${clip(line)}`));
      if (lines.length > DIFF_LINES) out.push(`${mark} ... ${lines.length - DIFF_LINES} more lines`);
    }
  }
  return { text: out.join('\n'), count };
}

const sha = (text) => createHash('sha256').update(text).digest('hex');

/** The folder that holds the call records a `replay:` value names. */
export function replaySource(config, value) {
  if (typeof value !== 'string' || !value) throw new Error('--model replay: takes a job or sandbox ID, or a folder');
  const callsIn = (dir) => {
    const own = path.join(dir, 'work', 'calls');
    return fs.existsSync(own) ? own : dir;
  };
  if (value.includes('/')) {
    const dir = callsIn(path.resolve(value));
    if (!fs.existsSync(dir) || !fs.readdirSync(dir).some((name) => /^\d+-.+-\d+\.json$/.test(name))) {
      throw new Error(`${value} holds no call records`);
    }
    return dir;
  }
  if (!/^[A-Za-z0-9_~-]+$/.test(value)) throw new Error('--model replay: takes a job or sandbox ID, or a folder');
  const dir = path.join(config.output, value, 'work', 'calls');
  if (!fs.existsSync(dir)) throw new Error(`${value} has no recorded calls (work/calls)`);
  return dir;
}

/** Every call record in `dir`, in the order the calls were made. */
export function readCalls(dir) {
  const records = fs.readdirSync(dir).filter((name) => /^\d+-.+-\d+\.json$/.test(name)).map((name) => {
    let record;
    try {
      record = JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
    } catch {
      throw new Error(`${name} is not a call record`);
    }
    const shaped = record?.version === CALLS_VERSION && typeof record.step === 'string'
      && Number.isInteger(record.attempt) && Number.isInteger(record.seq)
      && typeof record.promptHash === 'string' && typeof record.schemaHash === 'string'
      && typeof record.prompt?.system === 'string' && typeof record.prompt?.user === 'string';
    if (!shaped) throw new Error(`${name} is not a call record this version reads`);
    return record;
  });
  if (!records.length) throw new Error(`${dir} holds no call records`);
  return records.sort((a, b) => a.seq - b.seq);
}

/**
 * A model that answers from the records in `dir`. `miss` is what a call the recording
 * cannot answer does: `fail` throws ReplayMiss, `live` asks the live model, built from the
 * run's config on the first such call (`live` may be given, as a client or a function that
 * makes one). A missed call always uses up its recorded call, so one changed prompt does
 * not shift the answers of the calls after it. A recorded failure is thrown again as the
 * same ModelError, so the retry that followed it replays too.
 *
 * Built before the job's logs exist; `bind` gives it the logs, the job's ID and the way
 * to make the live model.
 */
export function replayModel({ dir, miss = 'fail', live = null }) {
  if (!['fail', 'live'].includes(miss)) throw new Error('--replay-miss takes fail or live');
  const queues = new Map();
  const tokens = new Map();
  for (const record of readCalls(dir)) {
    const key = `${record.step}\0${record.attempt}`;
    if (!queues.has(key)) queues.set(key, []);
    queues.get(key).push(record);
    const counted = record.usage?.promptTokens;
    const text = sha(`${record.prompt.system}\n${record.prompt.user}`);
    if (counted > 0 && !tokens.has(text)) tokens.set(text, counted);
  }
  let logs = null;
  let jobId = null;
  let makeLive = typeof live === 'function' ? live : () => live;
  let liveClient = null;
  const report = { served: 0, live: 0, misses: [] };
  let floor = 0;

  const liveModel = () => {
    liveClient ??= makeLive?.();
    if (!liveClient) throw new Error('--replay-miss live has no model to ask');
    return liveClient;
  };

  /** Takes the recorded call a recorded failure's retry belongs to out of the queues. */
  function dropRetry(failed) {
    const queue = queues.get(`${failed.step}\0${failed.attempt + 1}`);
    const at = queue?.findIndex((record) => record.seq === failed.seq + 1) ?? -1;
    if (at >= 0) queue.splice(at, 1);
  }

  /**
   * The next recorded call for this step and attempt. When the first in line holds another
   * prompt but a later one holds this prompt, the ones ahead belong to a phase or batch the
   * run did not reach, so they are skipped. When none holds it, the miss uses up the first
   * record made after the last one taken, so its diff is against a call of the same stretch
   * of the run. A retry that holds no prompt like this one is no record: its first attempt
   * was a miss that used up the recorded retry. A call used up as a miss takes its
   * recorded retry with it.
   */
  function take(key, wanted, attempt) {
    const queue = queues.get(key);
    if (!queue?.length) return null;
    const at = queue.findIndex((record) => record.promptHash === wanted);
    if (at < 0 && attempt > 1) return null;
    const last = at >= 0 ? at : Math.max(0, queue.findIndex((record) => record.seq > floor));
    const taken = queue.splice(0, last + 1);
    for (const record of at >= 0 ? taken.slice(0, -1) : taken) if (record.error) dropRetry(record);
    floor = Math.max(floor, taken.at(-1).seq);
    return taken.at(-1);
  }

  function noted(code, step, changed, diff) {
    report.misses.push({ step, code, changed });
    if (!logs) return;
    logs.status({ job: jobId, phase: step.split('_')[0], event: 'replay-miss', step, reason: code,
      changedLines: changed });
    if (diff) logs.detail(`replay diff ${step}`, diff);
  }

  return {
    /** Gives the model the job's logs, its ID, and a way to make the live model when none was given. */
    bind({ logs: jobLogsOf, job, live: factory }) {
      logs = jobLogsOf;
      jobId = job;
      if (live === null) makeLive = factory;
    },

    /** What the run took from the recording and what it did not: counts, and each miss by step and reason. */
    report: () => ({ served: report.served, live: report.live, misses: [...report.misses] }),

    /** The summary a command prints: content-free, one line of counts and a line for each miss. */
    lines() {
      const { served, live: asked, misses } = report;
      return [`replay  served ${served}  live ${asked}  missed ${misses.length}`,
        ...misses.map(({ step, code, changed }) => missText(code, step) + (changed
          ? ` (${changed} line${changed === 1 ? '' : 's'} differ${changed === 1 ? 's' : ''}; the diff is in detail.log)`
          : '')),
      ];
    },

    async json(request) {
      const { system, user, schema, schemaName, attempt = 1 } = request;
      const record = take(`${schemaName}\0${attempt}`, promptHash(system, user), attempt);
      let code = null;
      let diff = null;
      if (!record) code = 'no-record';
      else if (record.promptHash !== promptHash(system, user)) {
        code = 'prompt-changed';
        diff = promptDiff(record.prompt, { system, user });
      } else if (record.schemaHash !== schemaHash(schema)) {
        code = 'schema-changed';
        if (record.error) dropRetry(record);
      } else if (record.thinking !== Boolean(request.reasoning)) {
        // A call made with thinking on and one made with it off can end differently on the
        // same prompt, such as a cut at the output budget against a short answer.
        code = 'thinking-changed';
        if (record.error) dropRetry(record);
      }
      if (code) {
        noted(code, schemaName, diff?.count ?? 0, diff?.text);
        if (miss === 'fail') throw new ReplayMiss(code, schemaName);
        report.live += 1;
        return liveModel().json(request);
      }
      const usage = { promptTokens: record.usage.promptTokens, outputTokens: record.usage.outputTokens,
        ms: record.ms,
        ...Object.fromEntries(USAGE_EXTRAS.filter((key) => record.usage[key] !== undefined)
          .map((key) => [key, record.usage[key]])) };
      // The seed is not matched: the recording fixes the reply whatever seed the run would send.
      const seed = record.seed ?? null;
      report.served += 1;
      if (record.error) {
        throw Object.assign(new ModelError(record.error.code, `recorded call failed: ${record.error.code}`),
          { usage, seed, reasoningTail: record.reasoningTail ?? '' });
      }
      return { value: record.reply, usage, seed };
    },

    /**
     * The count the server gave for this prompt when it was recorded, which includes the
     * chat template. A prompt the recording does not hold gets the estimate, so one the
     * live run found too big for the window is too big again and the step splits the same
     * way; with `--replay-miss live` the live model counts it.
     */
    async countTokens(text) {
      const known = tokens.get(sha(String(text)));
      if (known !== undefined) return known;
      return miss === 'live' ? liveModel().countTokens(text) : estimateTokens(text);
    },
  };
}
