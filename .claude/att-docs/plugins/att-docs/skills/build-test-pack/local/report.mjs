// Writes the maintainer's report: one Markdown file a day and a weekly rollup.
// Like the status lines it carries no content, only job IDs, reason codes,
// counts, confidence ratings and run times, so it can be opened or sent
// anywhere. It reads the queue's rows, with the cut records each run left on
// its row, and each job's status.log, never the pack, the workbook or detail.log.

import fs from 'node:fs';
import path from 'node:path';
import { BUILDER_FAIL, countedTries, heldRow, MAX_MEMORY_STOPS, MAX_TRIES, memoryStops } from './config.mjs';
import { readStatusLog, recordedRuns, repeatedCuts } from './status.mjs';

const DAY = 86400000;
const DAYS = { day: 1, week: 7 };

/** A repeatable random source for the spot-check sample: a function giving numbers in [0, 1). */
export function seededRandom(seed) {
  if (!/^-?\d+$/.test(String(seed))) throw new Error('--seed takes a whole number');
  let state = Number(seed) >>> 0;
  return () => {
    state = (state + 0x6D2B79F5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const dateOf = (when) => {
  const pad = (n) => String(n).padStart(2, '0');
  return `${when.getFullYear()}-${pad(when.getMonth() + 1)}-${pad(when.getDate())}`;
};

const isCode = (value) => typeof value === 'string' && /^[A-Za-z0-9_.:+-]{1,80}$/.test(value);

/** A value that is a short code, or `other` so nothing else can reach the file. */
const code = (value) => (isCode(value) ? value : 'other');

/** When a row's latest attempt ended: its finish, or its last failure while it waits to retry. */
const endedAt = (row) => row.finished ?? row.failures?.at(-1)?.at ?? null;

/** What one row says about its job, from the row and the job's status.log. */
function jobEntry(config, row) {
  const failures = row.failures ?? [];
  const passed = row.status === 'passed';
  const state = passed ? 'PASS' : row.status === 'queued' ? 'RETRY' : row.status === 'stopped' ? (heldRow(row) ? 'HELD' : 'STOPPED')
    : memoryStops(failures) >= MAX_MEMORY_STOPS ? 'MEMORY'
      : countedTries(failures) >= MAX_TRIES ? 'DROPPED' : 'FAIL';
  const entries = readStatusLog(path.join(config.output, row.id, 'status.log'));
  const done = entries.findLast((e) => e.phase === 'done' && e.event === 'pass');
  // The release line is written after the job settles and says nothing about its sheets.
  const failed = entries.findLast((e) => e.event === 'fail' && e.phase !== 'release');
  // The level a rating step passed with, or the level a later build lowered it to.
  const rated = entries.findLast((e) => e.event === 'confidence-lowered'
    || (['phase9-confidence', 'phase9-revalidate'].includes(e.phase) && e.event === 'pass' && e.confidence));
  const confidence = rated?.event === 'confidence-lowered' ? rated.overall : rated?.confidence;
  const last = failures.at(-1);
  const sheets = passed ? { pass: done?.sheetsPass ?? 0, limited: done?.sheetsLimited ?? 0, fail: 0 }
    : { pass: null, limited: null, fail: failed?.sheets ?? null };
  const workbook = row.workbook ? path.basename(row.workbook) : null;
  return {
    id: row.id, state, at: endedAt(row), ms: passed ? row.ms : last?.ms ?? row.ms ?? null,
    phase: passed ? null : last?.phase ?? row.phase ?? null,
    reason: passed ? null : last?.reason ?? row.reason ?? null,
    reasons: failures.map((f) => f.reason), sheets,
    confidence: confidence ?? null, limited: passed && sheets.limited > 0,
    workbook: workbook && isCode(workbook) ? workbook : null,
  };
}

/** A shuffled copy, from `random`. */
function shuffled(list, random) {
  const out = [...list];
  for (let i = out.length - 1; i > 0; i -= 1) {
    const j = Math.floor(random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

/**
 * The packs worth a person's time: Low confidence first, then PASS WITH
 * LIMITATIONS, up to `maxPriority`, then `sample` more drawn at random from
 * the passed packs left over.
 */
export function spotChecks(passed, { maxPriority, sample }, random) {
  const low = passed.filter((job) => job.confidence === 'Low')
    .map((job) => ({ job, why: 'low-confidence' }));
  const limited = passed.filter((job) => job.confidence !== 'Low' && job.limited)
    .map((job) => ({ job, why: 'pass-with-limitations' }));
  const priority = [...low, ...limited].slice(0, maxPriority);
  const taken = new Set(priority.map((pick) => pick.job.id));
  const rest = shuffled(passed.filter((job) => !taken.has(job.id)), random).slice(0, sample)
    .map((job) => ({ job, why: 'random-sample' }));
  return [...priority, ...rest].map(({ job, why }) => ({ id: job.id, why, workbook: job.workbook }));
}

/** The report's numbers for one period, ending at `now`. */
export function reportData(config, queue, { period = 'day', now = new Date(), random = Math.random } = {}) {
  const since = now.getTime() - DAYS[period] * DAY;
  const rows = queue.jobs.filter((row) => row.status !== 'removed');
  const jobs = rows.filter((row) => {
    const at = endedAt(row);
    return at && new Date(at).getTime() >= since && new Date(at).getTime() <= now.getTime();
  }).map((row) => jobEntry(config, row))
    .sort((a, b) => new Date(a.at) - new Date(b.at));
  const count = (state) => jobs.filter((job) => job.state === state).length;
  const waiting = rows.filter((row) => row.status === 'queued');
  // A step cut on run after run is named for each job that finished in the period,
  // from every row the job has had, removed ones too.
  const repeated = [...new Set(jobs.map((job) => job.id))]
    .flatMap((id) => repeatedCuts(recordedRuns(queue, id)).map((step) => ({ id, ...step })));
  return {
    period, since: new Date(since), now, jobs,
    counts: { pass: count('PASS'), fail: count('FAIL'), retry: count('RETRY'), dropped: count('DROPPED'),
      memory: count('MEMORY'), stopped: count('STOPPED'), held: count('HELD') },
    queue: { depth: waiting.length, retrying: waiting.filter((row) => countedTries(row.failures) > 0).length,
      running: rows.filter((row) => row.status === 'running').length },
    failing: jobs.filter((job) => !['PASS', 'STOPPED'].includes(job.state)),
    repeatedCuts: repeated,
    spot: spotChecks(jobs.filter((job) => job.state === 'PASS'), config.report, random),
  };
}

const minutes = (ms) => (ms ? `${Math.max(1, Math.round(ms / 60000))} min` : '-');
const cell = (value) => (value === null || value === undefined ? '-' : code(String(value)));

/**
 * What to do about a thinking step cut at its output budget on its last runs. The report
 * does not read the server, so the line names both hosts.
 */
const CUT_ADVICE = 'With the server\'s thinking budget set, raise its output budget with'
  + ' `model.reasoningOutputByStep`; without it, turn its thinking off.';

/** The report as Markdown. */
export function renderReport(data) {
  const { counts } = data;
  const lines = [
    `# Test pack report, ${data.period === 'week' ? 'weekly rollup' : 'daily'}, ${dateOf(data.now)}`,
    '',
    `Covers ${dateOf(data.since)} to ${dateOf(data.now)}. No job content is in this report; open `
      + 'the workbooks listed under Spot check to judge the packs themselves.',
    '',
    '## Summary',
    '',
    `- Passed: ${counts.pass}`,
    `- Failed once and waiting to retry: ${counts.retry}`,
    `- Failed ${MAX_TRIES} times and dropped from the queue: ${counts.dropped}`,
    `- Stopped ${MAX_MEMORY_STOPS} times in a row for low memory and dropped from the queue: ${counts.memory}`,
    ...(counts.fail ? [`- Failed with no retry left: ${counts.fail}`] : []),
    ...(counts.held ? [`- Stopped on a gate a retry cannot change, waiting for a person: ${counts.held}`] : []),
    ...(counts.stopped ? [`- Stopped on request and waiting to resume: ${counts.stopped}`] : []),
    `- Queue depth: ${data.queue.depth} waiting (${data.queue.retrying} of them retrying), `
      + `${data.queue.running} running`,
    '',
  ];
  if (data.period === 'week') {
    const byDay = new Map();
    for (const job of data.jobs) {
      const day = dateOf(new Date(job.at));
      const row = byDay.get(day) ?? { pass: 0, other: 0 };
      if (job.state === 'PASS') row.pass += 1;
      else row.other += 1;
      byDay.set(day, row);
    }
    lines.push('## By day', '', '| Day | Passed | Failed |', '| --- | --- | --- |',
      ...[...byDay].map(([day, row]) => `| ${day} | ${row.pass} | ${row.other} |`), '');
  }
  lines.push('## Jobs', '');
  if (!data.jobs.length) lines.push('No job finished in this period.', '');
  else {
    lines.push('| Job | Result | Failed gate | Sheets pass / limited / fail | Confidence | Run time |',
      '| --- | --- | --- | --- | --- | --- |');
    for (const job of data.jobs) {
      const result = job.state === 'PASS' && job.limited ? 'PASS WITH LIMITATIONS' : job.state;
      const gate = job.state === 'PASS' ? '-' : `${cell(job.phase)} ${cell(job.reason)}`;
      const { pass, limited, fail } = job.sheets;
      const sheets = [pass, limited, fail].map(cell).join(' / ');
      lines.push(`| ${code(job.id)} | ${result} | ${gate} | ${sheets} | ${cell(job.confidence)} | ${minutes(job.ms)} |`);
    }
    lines.push('');
  }
  lines.push('## Jobs that keep failing', '');
  if (!data.failing.length) lines.push('None.', '');
  for (const job of data.failing) {
    const history = (job.reasons.length ? job.reasons : [job.reason]).map(cell).join(', then ');
    const where = `at ${cell(job.phase)} (${history})`;
    lines.push(job.state === 'MEMORY'
      ? `- ${code(job.id)}: stopped for low memory ${memoryStops(job.reasons.map((reason) => ({ reason })))} times in a row, last at ${cell(job.phase)}. `
        + 'Dropped from the queue; it needs a person to free memory or split the job, then `queue add` it again.'
      : job.state === 'DROPPED'
      ? `- ${code(job.id)}: failed ${job.reasons.length} times, last ${where}. Dropped from the queue; `
        + 'it needs a person.'
      : job.state === 'HELD'
      ? `- ${code(job.id)}: stopped ${where}. A retry cannot change it; ${job.reason === BUILDER_FAIL
        ? 'the builder refuses the pack the review left, so fix what its failed sheets name'
        : 'fix the document or its rules'}, then \`queue add --resume\`.`
      : job.state === 'RETRY' ? `- ${code(job.id)}: failed ${where}. Retries on its next run.`
        : `- ${code(job.id)}: failed ${where}. Not retried.`);
  }
  if (data.failing.length) lines.push('');
  lines.push('## Steps cut at their output budget', '');
  if (!data.repeatedCuts.length) lines.push('None.', '');
  for (const step of data.repeatedCuts) {
    lines.push(`- ${code(step.id)}: ${code(step.step)} was cut at its output budget of ${cell(step.budget)}`
      + ` tokens on its last ${cell(step.runs)} runs. ${CUT_ADVICE}`);
  }
  if (data.repeatedCuts.length) lines.push('');
  lines.push('## Spot check', '');
  if (!data.spot.length) lines.push('No passed pack to check in this period.', '');
  for (const pick of data.spot) {
    lines.push(`- ${code(pick.id)}: ${pick.why}${pick.workbook ? `, ${pick.workbook}` : ''}`);
  }
  if (data.spot.length) lines.push('');
  return `${lines.join('\n')}`;
}

/**
 * Writes the daily report, and on the configured weekday the weekly rollup
 * too (`auto`), or just the period named. Returns the files written.
 */
export function writeReports(config, queue, { period = 'auto', now = new Date(), random = Math.random } = {}) {
  if (!['auto', 'day', 'week'].includes(period)) throw new Error('--period takes day, week or auto');
  const periods = period === 'auto'
    ? ['day', ...(now.getDay() === config.report.weeklyDay ? ['week'] : [])] : [period];
  fs.mkdirSync(config.report.dir, { recursive: true });
  return periods.map((each) => {
    const data = reportData(config, queue, { period: each, now, random });
    const file = path.join(config.report.dir, `${each === 'week' ? 'weekly' : 'daily'}-${dateOf(now)}.md`);
    fs.writeFileSync(file, renderReport(data));
    return { period: each, file, counts: data.counts, queue: data.queue };
  });
}
