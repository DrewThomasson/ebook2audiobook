// The build supervisor watches a running job and answers the questions the job
// would otherwise stop on. At a question gate the job writes
// work/questions-<phase>.json and, while a supervisor's heartbeat is fresh, waits
// for work/answers-<phase>.json with the model still loaded. No fresh heartbeat,
// no answers in time, or a question left unanswered stops the job with the
// gate's own reason.

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

import { sleepUnlessAborted } from './abort.mjs';
import { Cancelled } from './model.mjs';

/** How sure an answer is: a source states it, or the sources point to it without stating it. */
const SETTLED = 'settled';
const BEST_READING = 'best reading';
const CONFIDENCE = [SETTLED, BEST_READING];

/** Who an answered question's assumption is marked as answered by. */
export const ANSWERED_BY = 'build supervisor';

/** How often a waiting job looks for the answers file and the heartbeat. */
export const POLL_MS = 15000;

/** The status events after a `waiting` line that end the wait. */
export const WAIT_ENDS = ['answers', 'wait-over', 'fail'];

/** How long the notice post may take before it is given up. */
const NOTIFY_MS = 10000;

const ANSWER_KEYS = ['id', 'answer', 'confidence', 'citations'];

const questionsPath = (outDir, phase) => path.join(outDir, 'work', `questions-${phase}.json`);
export const answersPath = (outDir, phase) => path.join(outDir, 'work', `answers-${phase}.json`);

/** The heartbeat `queue watch` keeps fresh for a job, beside the queue file. */
export const heartbeatPath = (config, id) => `${config.at(config.queue.file)}.watch-${id}`;

/** Writes the heartbeat for `id` with the time `at`, all at once. */
export function touchHeartbeat(config, id, at = new Date()) {
  const file = heartbeatPath(config, id);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temp = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(temp, `${at.toISOString()}\n`);
  fs.renameSync(temp, file);
}

/** The time in a heartbeat file, in milliseconds, or null when it is missing or unreadable. */
function heartbeatTime(file) {
  try {
    const at = Date.parse(fs.readFileSync(file, 'utf8').trim());
    return Number.isNaN(at) ? null : at;
  } catch {
    return null;
  }
}

/**
 * True when a supervisor's heartbeat for the job is newer than `staleMinutes` at
 * `now`. A sandbox job, `<source>~<label>`, also counts the heartbeat of its source.
 */
export function supervisorPresent(config, id, now) {
  const ids = id.includes('~') ? [id, id.split('~')[0]] : [id];
  const newest = Math.max(...ids.map((one) => heartbeatTime(heartbeatPath(config, one)) ?? -Infinity));
  return Number.isFinite(newest) && now - newest < config.supervisor.staleMinutes * 60000;
}

const blank = (value) => typeof value !== 'string' || !value.trim();

/**
 * Why an answers file's content fails its schema, as a reason code, or null when
 * it passes. The file is `{ "answers": [{ id, answer, confidence, citations }] }`.
 * A question the file leaves out is not a fault: it is a question the supervisor
 * declined. A settled answer names at least one citation; a best reading with none
 * is an answer that says no source bears on the question.
 */
export function answersFault(value, ids) {
  if (!value || typeof value !== 'object' || Array.isArray(value)
    || Object.keys(value).some((key) => key !== 'answers') || !Array.isArray(value.answers)) {
    return 'answers-shape';
  }
  const seen = new Set();
  for (const row of value.answers) {
    if (!row || typeof row !== 'object' || Array.isArray(row)
      || ANSWER_KEYS.some((key) => !Object.hasOwn(row, key))
      || Object.keys(row).some((key) => !ANSWER_KEYS.includes(key))) return 'answers-shape';
    if (!ids.includes(row.id)) return 'answers-unknown-id';
    if (seen.has(row.id)) return 'answers-duplicate-id';
    seen.add(row.id);
    if (blank(row.answer)) return 'answers-blank';
    if (!CONFIDENCE.includes(row.confidence)) return 'answers-confidence';
    if (!Array.isArray(row.citations) || row.citations.some(blank)
      || (row.confidence === SETTLED && !row.citations.length)) return 'answers-citations';
  }
  return null;
}

/** Posts one line to `url`; resolves to true when the server accepted it. */
export async function postNotice(url, text) {
  const response = await fetch(url, { method: 'POST', body: text, signal: AbortSignal.timeout(NOTIFY_MS) });
  return response.ok;
}

/** The status line's counts for a set of answers to `total` questions. */
const answerCounts = (answers, total) => ({
  answered: answers.length,
  declined: total - answers.length,
  settled: answers.filter((a) => a.confidence === SETTLED).length,
  bestReading: answers.filter((a) => a.confidence === BEST_READING).length,
});

/**
 * Waits at a question gate for the build supervisor's answers. `questions` is a list of
 * `{ id, question }`. Returns `{ answers }`, the rows of a file that passed its schema, or
 * `{ held }` with why the job stops instead: `no-wait` when the wait is off, `no-supervisor`
 * when no heartbeat is fresh, `supervisor-gone` when it goes stale during the wait, or
 * `timeout`. A file that fails its schema is logged once per version and the wait goes on.
 * A stop request ends the wait with Cancelled. Status lines carry counts and codes only.
 */
export async function waitForAnswers({ config, id, outDir, phase, questions, logs,
  now = Date.now, sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  signal = null, post = postNotice }) {
  const { waitMinutes, notifyUrl } = config.supervisor;
  if (!waitMinutes) return { held: 'no-wait' };
  if (!supervisorPresent(config, id, now())) return { held: 'no-supervisor' };
  const answers = answersPath(outDir, phase);
  // An answers file left from an earlier run is not an answer to these questions.
  fs.rmSync(answers, { force: true });
  const until = now() + waitMinutes * 60000;
  const file = questionsPath(outDir, phase);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(`${file}.tmp`, `${JSON.stringify({ job: id, phase, until: new Date(until).toISOString(),
    questions }, null, 1)}\n`);
  fs.renameSync(`${file}.tmp`, file);
  logs.status({ job: id, phase, event: 'waiting', questions: questions.length,
    until: new Date(until).toISOString().replace(/\.\d+Z$/, 'Z'), waitMinutes });
  if (notifyUrl) {
    const line = `${id} waiting phase=${phase} questions=${questions.length} left=${waitMinutes}`;
    const sent = await Promise.resolve().then(() => post(notifyUrl, line)).catch(() => false);
    if (!sent) logs.status({ job: id, phase, event: 'warn', reason: 'notify-failed' });
  }
  const ids = questions.map((q) => q.id);
  let seen = null;
  for (;;) {
    let text = null;
    try {
      text = fs.readFileSync(answers, 'utf8');
    } catch {
      // Not written yet.
    }
    const hash = text === null ? null : crypto.createHash('sha256').update(text).digest('hex');
    if (hash !== null && hash !== seen) {
      seen = hash;
      let value;
      let fault;
      try {
        value = JSON.parse(text);
        fault = answersFault(value, ids);
      } catch {
        fault = 'answers-not-json';
      }
      if (!fault) {
        logs.status({ job: id, phase, event: 'answers', ...answerCounts(value.answers, ids.length) });
        return { answers: value.answers };
      }
      logs.status({ job: id, phase, event: 'answers-rejected', reason: fault });
      logs.detail(`answers-${phase}.json rejected`, fault);
    }
    if (now() >= until) {
      logs.status({ job: id, phase, event: 'wait-over', reason: 'timeout' });
      return { held: 'timeout' };
    }
    if (!supervisorPresent(config, id, now())) {
      logs.status({ job: id, phase, event: 'wait-over', reason: 'supervisor-gone' });
      return { held: 'supervisor-gone' };
    }
    await sleepUnlessAborted(sleep, Math.min(POLL_MS, until - now()), signal);
    if (signal?.aborted) throw new Cancelled();
  }
}
