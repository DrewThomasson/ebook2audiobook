// Three records per job. status.log is the one a session may be shown: phase names,
// pass or fail, reason codes, counts and timings, and the first line of a refusing
// builder's notes reduced to a short list of plain words, and nothing else. detail.log
// holds what the model and the builder actually said, and work/calls holds each
// model call's full prompt and reply. The last two stay in the job's output folder
// on this machine.

import fs from 'node:fs';
import path from 'node:path';

import { callRecorder } from './calls.mjs';
import { stepKey } from './config.mjs';

/** Field values a status line may carry: numbers, booleans, and short codes. A sandbox job's ID joins its source and label with `~`. */
export const FIELD_MAX = 80;
const SAFE = new RegExp(`^[A-Za-z0-9 _.:/=+~-]{0,${FIELD_MAX}}$`);

/** The parsed lines of a status.log; a line cut off mid-write is skipped, and a missing log is empty. */
export function readStatusLog(file) {
  let text;
  try {
    text = fs.readFileSync(file, 'utf8');
  } catch {
    return [];
  }
  return text.trim().split('\n').flatMap((line) => {
    try {
      return [JSON.parse(line)];
    } catch {
      return [];
    }
  });
}

/**
 * One status line's fields, checked. A string field has to be a code from the
 * pipeline itself (a phase name, a reason code, a job id), never text that
 * came from a document, a rule, the model or the builder.
 */
export function statusFields(fields) {
  for (const [key, value] of Object.entries(fields)) {
    if (typeof value === 'number' || typeof value === 'boolean' || value === null) continue;
    if (typeof value !== 'string' || !SAFE.test(value)) {
      throw new Error(`status field ${key} is not a short code`);
    }
  }
  return fields;
}

/**
 * A stop's counts cut to fit a status line: a string count longer than a field
 * allows keeps the first space-separated numbers that fit, each whole, and a
 * string with no space to cut at becomes empty. The count beside it, such as
 * `documents`, still holds the full total.
 */
export function fitCounts(counts) {
  const limit = FIELD_MAX;
  const fitted = {};
  for (const [key, value] of Object.entries(counts)) {
    if (typeof value !== 'string' || value.length <= limit) {
      fitted[key] = value;
      continue;
    }
    const cut = value.slice(0, limit + 1).lastIndexOf(' ');
    fitted[key] = cut > 0 ? value.slice(0, cut) : '';
  }
  return fitted;
}

/**
 * The sheet names a builder failed, joined with `+` and cut after the last name that
 * fits a status field, so a name is never cut in the middle. A character a status
 * field does not allow is dropped from a name.
 */
export function sheetsField(sheets) {
  let text = '';
  for (const sheet of sheets) {
    const name = String(sheet).replace(/[^A-Za-z0-9 _.:/=~-]/g, '').trim();
    if (!name) continue;
    const next = text ? `${text}+${name}` : name;
    if (next.length > FIELD_MAX) break;
    text = next;
  }
  return text;
}

/** The plain words a builder note keeps in a status line; every other word is hidden. */
const NOTE_WORDS = new Set(`a an and or but the is are was were be been has have had no not none nor nothing
  anything for from of in on to at by as with without than then that this these those it its each every any all
  some more most less least one two once again already still only also both either neither does do did done can
  cannot could should must may will would whether if when where which who what why how there here into onto
  over under after before between about against own other another same different first last next previous per
  via card cards rule rules step steps sheet sheets row rows column columns cell cells result results expected
  actual final name names id ids number numbers count counts total missing empty blank covered covers cover
  coverage reads read shows show shown match matches agree agrees contradict contradicts cite cites cited list
  lists listed found find unknown unresolved duplicate duplicates repeated appears appear present absent
  required optional invalid valid allowed contain contains contained include includes included exclude excludes
  excluded inclusion reason reasons status type types level levels limit limits limited pass fail failed fails
  failing too many much few long short low high medium test tests review said title titles text matrix applicable
  partial`.split(/\s+/));

/** Capitalized words a note keeps past its first word: the builder's sheet and status words. */
const NOTE_CAPS = new Set(['expected', 'result', 'results', 'coverage', 'matrix', 'missing', 'covered', 'partial',
  'not', 'applicable']);

/**
 * The first line of a builder's notes, made fit for a status line. A line that only gives
 * a sheet's `populated:` state is skipped. Text after `said:` is dropped, since a note puts
 * the reviewer's own words there. A quoted span becomes `_`, and a quote that never closes
 * hides the rest of the line; a span closes only on its own kind of quote, and an apostrophe
 * inside a word opens nothing. A word with a digit in it or a `-` or `.` between letters (an
 * ID, a number, a file name) becomes `ID`. Any other word that is not on a short list of
 * plain words becomes `_`, and so does a capitalized word that does not start a sentence
 * (a sentence starts at the first word and after a word ending in `.`, `:`, `!` or `?`),
 * unless it is one of the builder's sheet and status words. A title is capitalized, so this
 * hides most of one; a lower-case title of plain words still shows. Runs of `_` merge,
 * punctuation is dropped, and the line is cut at a word to a field's length.
 */
export function noteCode(notes) {
  const line = String(notes ?? '').split('\n').map((text) => text.trim())
    .find((text) => text && !/^populated:/i.test(text)) ?? '';
  const words = line
    .replace(/(\bsaid:).*$/i, '$1')
    .replace(/"[^"]*"|\u201c[^\u201d]*\u201d|`[^`]*`|(?<![A-Za-z0-9])['\u2018][^'\u2019]*['\u2019]/g, ' _ ')
    .replace(/["\u201c`].*$|(?<![A-Za-z0-9])['\u2018].*$/, ' _ ')
    .trim()
    .split(/\s+/)
    .map((word, i, all) => {
      const core = word.replace(/^[^A-Za-z0-9_]+|[^A-Za-z0-9_]+$/g, '');
      if (!core) return '';
      if (core === '_') return '_';
      if (/\d/.test(core) || /[A-Za-z0-9][-.][A-Za-z0-9]/.test(core)) return 'ID';
      const plain = core.toLowerCase();
      if (!/^[A-Za-z]+$/.test(core) || !NOTE_WORDS.has(plain)) return '_';
      const starts = i === 0 || /[.:!?]$/.test(all[i - 1]);
      return /^[A-Z]/.test(core) && !starts && !NOTE_CAPS.has(plain) ? '_' : core;
    })
    .filter(Boolean)
    .filter((word, i, all) => !(word === '_' && all[i - 1] === '_'));
  let text = '';
  for (const word of words) {
    const next = text ? `${text} ${word}` : word;
    if (next.length > FIELD_MAX) break;
    text = next;
  }
  return text;
}

/**
 * What one run did with its thinking steps, from its status lines: the steps it
 * asked with thinking on, keyed `<phase>.<step>` without an index or repeat
 * suffix, and each one cut at its output budget, with that budget.
 */
export function runCuts(entries) {
  const asked = new Set();
  const cut = new Map();
  for (const entry of entries) {
    if (entry.attempt !== 1 || entry.reasoning !== true
      || !['call', 'retry', 'call-fail'].includes(entry.event)) continue;
    const step = `${entry.phase}.${stepKey(entry.step)}`;
    asked.add(step);
    if (entry.reason === 'length') cut.set(step, entry.maxTokens ?? null);
  }
  return { asked: [...asked], cut: [...cut].map(([step, budget]) => ({ step, budget })) };
}

/**
 * The thinking steps cut at their output budget on the last two or more runs that
 * asked them, in a row, from runs oldest first. Each has its latest budget and how
 * many runs in a row cut it. A run that never asked a step, such as one resumed past
 * its phase, neither breaks nor extends the streak.
 */
export function repeatedCuts(runs) {
  const streaks = new Map();
  for (const run of runs) {
    const cut = new Map((run.cut ?? []).map((entry) => [entry.step, entry.budget]));
    for (const step of run.asked ?? []) {
      streaks.set(step, cut.has(step)
        ? { budget: cut.get(step), runs: (streaks.get(step)?.runs ?? 0) + 1 } : { runs: 0 });
    }
  }
  return [...streaks].filter(([, streak]) => streak.runs >= 2)
    .map(([step, { budget, runs }]) => ({ step, budget, runs }));
}

/** A job's recorded runs, oldest first, from the `cuts` each of its queue rows holds. */
export const recordedRuns = (queue, id) => queue.jobs.filter((row) => row.id === id)
  .flatMap((row) => row.cuts ?? []);

export function jobLogs(outDir, { echo = true } = {}) {
  fs.mkdirSync(outDir, { recursive: true });
  const statusPath = path.join(outDir, 'status.log');
  const detailPath = path.join(outDir, 'detail.log');
  const calls = callRecorder(path.join(outDir, 'work', 'calls'));
  return {
    statusPath,
    detailPath,
    /** A content-free line, written to status.log and echoed to the console. */
    status(fields) {
      const line = JSON.stringify({ at: new Date().toISOString(), ...statusFields(fields) });
      fs.appendFileSync(statusPath, `${line}\n`);
      if (echo) console.log(line);
    },
    /** Anything else. Never echoed. */
    detail(label, value) {
      const text = typeof value === 'string' ? value : JSON.stringify(value, null, 1);
      fs.appendFileSync(detailPath, `--- ${new Date().toISOString()} ${label}\n${text}\n`);
    },
    /** One model call's prompt, reply, counts and timings, in work/calls. Never echoed. */
    call: (fields) => calls.record(fields),
  };
}
