// The build, phase by phase, as fixed local-model calls. Each phase writes its
// fields of the pack, its gate runs in code, and a failed gate throws a
// GateError whose code is the only thing the status log records about why.

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { estimateTokens, ModelError } from './model.mjs';
import { USAGE_EXTRAS } from './calls.mjs';
import { noteCode, sheetsField } from './status.mjs';
import { fill, globFiles, REASONING_STEPS, RULE_SHAPE, rootRelative, stepKey } from './config.mjs';
import * as S from './schemas.mjs';
import { revisedDate, rulesStale, shapeProblems, uncitedStruck } from './rules.mjs';
import { readSheet } from './pack.mjs';
import { readXlsx } from './xlsx.mjs';
import { checkPack, failedSheet, FILLED_GAP, NO_REASON_PROBLEM } from './pack-checks.mjs';
import { docControls, dropRepeats, foldFollowUps, mergeRemovedScenarios, repeatsLeft } from './design-tidy.mjs';
import { impossibleSteps, stepRules, stepSchema, STEP_QUESTION, stepsView } from './steps.mjs';
import { ANSWERED_BY } from './supervisor.mjs';

export class GateError extends Error {
  constructor(phase, code, counts = {}) {
    super(`${phase}: ${code}`);
    this.phase = phase;
    this.code = code;
    this.counts = counts;
  }
}

/** A step run on its own was given something its state cannot serve; the message says what. */
export class StepInputError extends Error {}

const SYSTEM = `You are one step of a fixed pipeline that builds a software test pack.
The reference material below is the procedure, the workbook standard and the
rules the pack follows; keep every rule it gives for the step you are asked to do.
Do only this step. Answer with JSON matching the schema and nothing else.
Write your own analysis of the inputs. Never copy reference wording into the answer.
Every rule ID you name must be one the step gives you, written exactly as given.`;

const section = (label, text) => `## ${label}\n\n${String(text).trim()}\n`;
const asLines = (rows) => rows.join('\n');
const list = (value) => (Array.isArray(value) ? value
  : value === undefined || value === null || value === '' ? [] : [value]);
const blank = (value) => list(value).every((item) => String(item ?? '').trim() === '');

/** Splits text on paragraph boundaries into pieces of at most `tokens` estimated tokens. */
export function splitText(text, tokens) {
  if (!(tokens > 0)) throw new ModelError('window-too-small', 'the model server window leaves no room for text');
  const limit = tokens * 3;
  const pieces = [];
  let current = '';
  for (const paragraph of String(text).split(/\n\s*\n/)) {
    // A paragraph longer than a piece is cut on line breaks, then on characters.
    const parts = paragraph.length <= limit ? [paragraph]
      : paragraph.split('\n').flatMap((line) => (line.length <= limit ? [line]
        : line.match(new RegExp(`[\\s\\S]{1,${limit}}`, 'g'))));
    for (const part of parts) {
      if (current && current.length + part.length + 2 > limit) {
        pieces.push(current);
        current = '';
      }
      current = current ? `${current}\n\n${part}` : part;
    }
  }
  if (current) pieces.push(current);
  return pieces;
}

/** Groups items into batches whose rendered text stays under `tokens`, at most `max` each. */
export function batches(items, render, tokens, max = Infinity) {
  const out = [];
  let current = [];
  let size = 0;
  for (const item of items) {
    const cost = estimateTokens(render(item));
    if (current.length && (size + cost > tokens || current.length >= max)) {
      out.push(current);
      current = [];
      size = 0;
    }
    current.push(item);
    size += cost;
  }
  if (current.length) out.push(current);
  return out;
}

/** The window every prompt is budgeted against: the smaller of the config's and the server's. */
const budgetWindow = (ctx) => ctx.window ?? ctx.config.model.context;

/**
 * The least room a prompt must leave for inputs once the core references and the
 * reply are in. Documents are split at `room - 1000`, so a window this small
 * leaves pieces of about a page or more. A split that subtracts more references
 * than the core ones can still come out smaller; a piece with no room is a
 * `window-too-small` error from `splitText`, not a silent failure.
 */
const MIN_INPUT_ROOM = 2000;

/**
 * Reads the model server's context size and sets ctx.window to the smaller of
 * it and `model.context`. Asked again on every call, so a reload at another
 * size is picked up; each distinct smaller size is logged once. A size marked
 * as a guess can only lower the window, never raise it, and never fails the
 * job: one that leaves no room counts as unread. A size that cannot be
 * read keeps the last server-based window in force, and the config's applies
 * until one has been read; it is logged once. A window
 * with no room left for a prompt is a `window-too-small` error.
 */
export async function readWindow(ctx, phase) {
  const configured = ctx.config.model.context;
  if (typeof ctx.model.contextWindow !== 'function') {
    delete ctx.window;
    return;
  }
  const read = await ctx.model.contextWindow();
  const before = ctx.window ?? configured;
  const { reasoningOutput, maxOutput } = ctx.config.model;
  const floor = Math.max(reasoningOutput, maxOutput) + 2048 + estimateTokens(SYSTEM);
  const tooSmall = () => ctx.window - floor <= 0
    || room(ctx, true, ctx.ref?.core ?? []) < MIN_INPUT_ROOM;
  let server = read?.size ?? null;
  // An unreadable size keeps the last server-based window; the config's applies
  // only until one has been read. A guess never raises the window, and a guess
  // that would leave no room is treated as unknown: only a sure size fails a job.
  ctx.window = !server ? before
    : read.guess ? Math.min(before, server) : Math.min(configured, server);
  if (server && read.guess && tooSmall()) {
    ctx.window = before;
    server = null;
  }
  const noted = ctx.windowNoted ?? (ctx.windowNoted = new Set());
  if (!server && !noted.has('unknown')) {
    noted.add('unknown');
    ctx.logs.status({ job: ctx.job.id, phase, event: 'warn', reason: 'server-window-unknown' });
  } else if (server && server < configured && !noted.has(server) && (!read.guess || server < before)) {
    noted.add(server);
    ctx.logs.status({ job: ctx.job.id, phase, event: 'warn', reason: 'server-window',
      context: configured, serverContext: server, ...(read.guess ? { guess: true } : {}) });
  }
  if (tooSmall()) {
    throw new ModelError('window-too-small', 'the model server window leaves no room for a prompt');
  }
}

/** The usage figures a status line carries when the server gave them: thinking and timing. */
const usageFields = (usage) => Object.fromEntries(USAGE_EXTRAS
  .filter((key) => usage?.[key] !== undefined).map((key) => [key, usage[key]]));

/**
 * The pipeline's one way to call the model. Checks the token count first and
 * throws `too-big` rather than truncating, retries a failed call once with
 * thinking off (a thinking call cut off at its output budget gets the smaller `retryOutput`,
 * and a second cut is `runaway`), and logs only counts and timings. Each call that
 * reaches the model, failed ones too, also gets its prompt, reply and timings written
 * to work/calls. While a call runs, a `progress` line says how much of its reply has
 * come every few minutes. A call cut off at its output limit logs its thinking and
 * answer tokens apart and keeps the end of its thinking text in detail.log. A
 * `question` rides last, after every input, so calls that share their
 * inputs and differ only in what they ask also share the start of their prompt.
 * `outcome`, when given, receives `thinking`: whether the call that answered ran
 * with thinking on. `limit`, when given, is the output budget of a call with thinking off,
 * for the first call and any retry, in place of `model.maxOutput`.
 */
export async function ask(ctx, { phase, step, reasoning, refs = [], inputs, schema, task, question, outcome,
  limit }) {
  const system = [SYSTEM, ...refs.filter(Boolean).map((text, i) => section(`Reference ${i + 1}`, text))]
    .join('\n');
  const user = [section('Task', task), ...inputs.filter(([, text]) => !blank(text))
    .map(([label, text]) => section(label, text)),
  ...(question ? [section('Question', question)] : [])].join('\n');
  await readWindow(ctx, phase);
  const promptTokens = await ctx.model.countTokens(`${system}\n${user}`);
  const firstCap = !reasoning && limit !== undefined ? limit : outputCap(ctx, phase, reasoning, step);
  // A retry can ask for more than the first call: the plain cap after a failed thinking
  // call, or the retry cap after a cut. The prompt must leave room for the largest.
  const { maxOutput, retryOutput } = ctx.config.model;
  const plain = limit ?? maxOutput;
  const widestCap = reasoning ? Math.max(firstCap, plain, retryOutput) : firstCap;
  if (promptTokens + widestCap + 512 > budgetWindow(ctx)) {
    throw Object.assign(new ModelError('too-big', 'prompt does not fit the context'),
      { promptTokens });
  }
  let think = reasoning;
  let maxTokens = firstCap;
  let cutThinking = false;
  const schemaName = `${phase}_${step}`.replace(/\W+/g, '_');
  for (let attempt = 1; attempt <= 2; attempt += 1) {
    ctx.calls += 1;
    const startedAt = new Date();
    const recorded = { step: schemaName, attempt, thinking: think, maxTokens, system, user, schema,
      startedAt };
    try {
      const thinking = think;
      const { value, usage, seed } = await ctx.model.json({
        system, user, schema, schemaName, attempt, reasoning: think, maxTokens,
        onProgress: (progress) => ctx.logs.status({ job: ctx.job.id, phase, step, event: 'progress',
          attempt, reasoning: thinking, ...progress }),
      });
      ctx.logs.call({ ...recorded, seed, reply: value, usage, endedAt: new Date() });
      ctx.logs.status({ job: ctx.job.id, phase, step, event: 'call', attempt, reasoning: think,
        promptTokens: usage.promptTokens, outputTokens: usage.outputTokens, ms: usage.ms,
        ...usageFields(usage) });
      ctx.logs.detail(`${phase} ${step} reply`, value);
      ctx.tokens.prompt += usage.promptTokens;
      ctx.tokens.output += usage.outputTokens;
      if (outcome) outcome.thinking = think;
      return S.fromWire(schema, value);
    } catch (caught) {
      if (!(caught instanceof ModelError)) throw caught;
      // A reply cut off at its output budget with thinking off would be cut off again.
      const cut = caught.code === 'length';
      let error = caught;
      if (cut && cutThinking) {
        error = Object.assign(new ModelError('runaway', 'model kept going after thinking was turned off'),
          { usage: caught.usage });
      }
      ctx.logs.call({ ...recorded, seed: caught.seed, errorCode: error.code, usage: error.usage,
        reasoningTail: caught.reasoningTail, endedAt: new Date() });
      if (caught.reasoningTail) ctx.logs.detail(`${phase} ${step} reasoning tail`, caught.reasoningTail);
      // A cut call says how its output split between thinking and answer, when that is known.
      const split = error.usage?.reasoningTokens !== undefined || !think;
      const failed = { reasoning: think, maxTokens, reason: error.code,
        // What a failed connection was, such as ECONNRESET, when the client knows.
        ...(error.causeCode ? { cause: error.causeCode } : {}),
        outputTokens: error.usage?.outputTokens ?? 0, ms: error.usage?.ms ?? 0, ...usageFields(error.usage),
        ...(['length', 'runaway'].includes(error.code) && split ? {
          reasoningTokens: error.usage?.reasoningTokens ?? 0,
          answerTokens: error.usage?.answerTokens ?? error.usage?.outputTokens ?? 0 } : {}) };
      if (attempt === 2 || (cut && !think)) {
        ctx.logs.status({ job: ctx.job.id, phase, step, event: 'call-fail', attempt, ...failed });
        throw error;
      }
      ctx.logs.status({ job: ctx.job.id, phase, step, event: 'retry', attempt, ...failed });
      // A call that failed while thinking most often thought too long. One that ran
      // out the output budget is retried with a small cap, so a model that keeps
      // going after thinking is off fails fast; any other failure answers at the
      // plain cap.
      cutThinking = cut && think;
      maxTokens = cutThinking ? ctx.config.model.retryOutput : plain;
      think = false;
    }
  }
  throw new Error('unreachable');
}

/**
 * The output budget for a call. A thinking call takes the config's budget for its step when
 * there is one; otherwise the smallest of the config's budget for its phase, the built-in
 * budget for its step and `reasoningOutput`. No budget passes `reasoningOutput`.
 */
export function outputCap(ctx, phase, think, step) {
  const { maxOutput, reasoningOutput, reasoningOutputByPhase, reasoningOutputByStep } = ctx.config.model;
  if (!think) return maxOutput;
  const key = `${phase}.${stepKey(step)}`;
  const own = reasoningOutputByStep?.[key];
  if (own !== undefined) return Math.min(own, reasoningOutput);
  return Math.min(reasoningOutputByPhase?.[phase] ?? Infinity, REASONING_STEPS[key] ?? Infinity,
    reasoningOutput);
}

/** Room left for inputs in one call, after the reference and the reply. */
export const room = (ctx, reasoning, refs) => budgetWindow(ctx)
  - (reasoning ? Math.max(ctx.config.model.reasoningOutput, ctx.config.model.maxOutput)
    : ctx.config.model.maxOutput)
  - estimateTokens(SYSTEM + refs.join('\n')) - 2048;

/**
 * Runs a repository command. Returns its output, or null when it fails; `failure`
 * receives the error text and `output` the exit status and the output, for a caller
 * that reads what a failing command printed.
 */
function runCommand(ctx, template, values, { failure, output } = {}) {
  const argv = template.map((part) => fill(part, values));
  const result = spawnSync(argv[0], argv.slice(1), { cwd: ctx.config.root, encoding: 'utf8',
    maxBuffer: 512 * 1024 * 1024 });
  if (output) Object.assign(output, { status: result.status, stdout: result.stdout ?? '' });
  if (result.status !== 0) {
    const why = `${result.stderr ?? ''}${result.error?.message ?? ''}`;
    ctx.logs.detail(`command ${argv[0]} failed`, why);
    if (failure) failure.stderr = why;
    return null;
  }
  return result.stdout;
}

/** The codes whose rules a job can use: exported, derived by choice, or exported but old. */
export const USABLE_RULE_CODES = ['rules-ok', 'rules-derived', 'rules-stale'];
/** The codes that stop intake: the export is missing or not an export. */
const INTAKE_STOPS = ['rule-export-failed', 'rules-malformed'];
/** The codes that stop Phase 2 for an Included document. */
const PHASE2_STOPS = ['document-file', 'rule-export-failed', 'rules-malformed', 'rules-not-extracted'];

/**
 * `document-file` when the path is outside the repository root, missing, or not
 * a file, otherwise null. A path the export cannot map must never read as a
 * document with no rules.
 */
const outsideRoot = (rel) => !rel || path.isAbsolute(rel) || rel === '..' || rel.startsWith(`..${path.sep}`);

export function documentProblem(ctx, file) {
  if (outsideRoot(path.relative(ctx.config.root, file))) return 'document-file';
  try {
    return fs.statSync(file).isFile() ? null : 'document-file';
  } catch {
    return 'document-file';
  }
}

/** The sentence intake records for a document path `documentProblem` refused. */
function missingFileText(ctx, file) {
  const rel = relative(ctx, file);
  if (outsideRoot(path.relative(ctx.config.root, file))) return `Document file is outside the repository: ${rel}`;
  return fs.existsSync(file) ? `Document path is not a file: ${rel}` : `Document file not found: ${rel}`;
}

/**
 * One document's rules from the rule export, as { code, rules }. A path that is
 * outside the root, missing, or not a file is `document-file`, and the export
 * is not run. A failure the config's `noRules` pattern matches is the export
 * saying the document has no rules yet: `rules-not-extracted`, or `rules-derived` when the job or config
 * allows Phase 2 to derive them from the text. Any other failure is
 * `rule-export-failed`, since a pack built from derived rules alone would hide
 * the outage. An export that parses is checked for structure
 * (`rules-malformed`); the values the master holds that the procedure would not
 * write, and an export older than the document (`rules-stale`), are warnings:
 * they go to detail.log, and the stale one also leaves a content-free status
 * line naming the document `number`. Retired rules are kept.
 */
export function documentRules(ctx, file, number) {
  const { inputs, ruleShape } = ctx.config;
  const abs = ctx.config.at(rootRelative(ctx.config, file));
  if (documentProblem(ctx, abs)) {
    ctx.logs.detail('document path',
      `${relative(ctx, abs)} is outside the repository root, missing, or not a file`);
    return { code: 'document-file', rules: [] };
  }
  if (!inputs.ruleExport) return { code: 'rules-ok', rules: [] };
  const doc = relative(ctx, abs);
  const failure = {};
  const raw = runCommand(ctx, inputs.ruleExport, { doc }, { failure });
  if (raw === null) {
    if (!inputs.noRules || !new RegExp(inputs.noRules).test(failure.stderr)) {
      return { code: 'rule-export-failed', rules: [] };
    }
    const allowed = ctx.job.allowDerivedRules ?? ctx.config.allowDerivedRules;
    return { code: allowed ? 'rules-derived' : 'rules-not-extracted', rules: [] };
  }
  const text = fs.readFileSync(abs, 'utf8');
  let json;
  try {
    json = JSON.parse(raw);
  } catch {
    ctx.logs.detail(`rule export of document ${doc}`, 'the export is not JSON');
    return { code: 'rules-malformed', rules: [] };
  }
  const { errors, warnings } = shapeProblems(json, doc, text, ruleShape);
  if (errors.length) {
    ctx.logs.detail(`rule export of document ${doc} is malformed`, errors.join('\n'));
    return { code: 'rules-malformed', rules: [] };
  }
  if (warnings.length) ctx.logs.detail(`rule export of document ${doc}: warnings`, warnings.join('\n'));
  const rules = exportsOf(json).flatMap((entry) => list(entry.rules))
    .filter((rule) => rule.status !== 'superseded');
  if (rulesStale(text, exportsOf(json))) {
    ctx.logs.detail(`rule export of document ${doc} is stale`,
      `revised ${revisedDate(text)}; the rules were last confirmed earlier`);
    if (number) {
      ctx.logs.status({ job: ctx.job.id, phase: 'rules', event: 'warn', reason: 'rules-stale',
        document: number });
    }
    return { code: 'rules-stale', rules };
  }
  return { code: 'rules-ok', rules };
}

const exportsOf = (json) => (Array.isArray(json?.exports) ? json.exports : json ? [json] : []);
const stripId = (rule) => String(rule.name ?? '').replace(`${rule.rule_id} - `, '');
const relative = (ctx, file) => path.relative(ctx.config.root, file);
const firstHeading = (text) => (String(text).match(/^#+\s+(.+)$/m)?.[1] ?? '').slice(0, 120);
const OUTLINE_CHARS = 300;
const NOTE_CHARS = 600;
const filled = (items) => list(items).filter((item) => String(item).trim());

/** One candidate document as an index line: its title, its section headings and its source line. */
export function candidateLine(file, text) {
  const body = String(text).slice(0, 20000);
  const headings = [...body.matchAll(/^#{2,3}\s+(.+)$/gm)].map((m) => m[1].trim());
  const source = body.match(/^\**source\**\s*:\s*(.+)$/im)?.[1]?.trim();
  const outline = [headings.join('; '), source ? `source: ${source}` : ''].filter(Boolean)
    .join('; ').slice(0, OUTLINE_CHARS);
  return `- ${file}: ${firstHeading(body)}${outline ? `; ${outline}` : ''}`;
}

// ---------------------------------------------------------------------------
// Intake

// Labels no ordinary sentence starts with: they end a description in any record.
const ALM_LABELS = new Set(['detected by', 'detected on date', 'detected in release', 'assigned to',
  'closing date', 'closed in release', 'target release', 'defect id', 'priority', 'severity',
  'reproducible', 'attachments', 'history']);
// Words that are also ordinary text: they end a description only when written the way the
// record writes its own Short and Long Description labels, in bold or as headings.
const ALM_WORDS = new Set(['status', 'comments', 'comment', 'summary', 'name', 'id', 'subject',
  'module', 'project', 'owner', 'type']);

/**
 * The ALM short and long descriptions of a defect record, as one text, or the
 * whole record when it labels neither. A field is a heading or a `Label:` line
 * (bold or plain) named "Short Description" or "Long Description"; it runs to
 * the next heading or the next line that opens another ALM field. A label no
 * ordinary sentence starts with (Detected By, Priority and the like) opens one
 * in any record; a common word (Status, Name, Type) opens one only in the
 * record's own label style when that is bold. Other `Word:` lines stay in the field.
 */
export function almDescriptions(record) {
  const lines = String(record ?? '').split('\n');
  const field = /^\s*(?:#+\s*)?(?:\*\*)?([A-Za-z][A-Za-z ]*?)\s*(?:\*\*)?\s*(?::\s*(?:\*\*)?\s*(.*))?$/;
  const styleOf = (line) => (/^\s*#+\s/.test(line) ? 'heading' : line.includes('**') ? 'bold' : 'plain');
  // The style of the label that opened the field being read.
  let style = 'plain';
  const fields = new Map();
  let current = null;
  for (const line of lines) {
    const heading = /^\s*#+\s/.test(line);
    const match = field.exec(line);
    const name = match?.[1].trim().toLowerCase();
    const labeled = match && (heading || match[2] !== undefined);
    const opens = labeled && (name === 'short description' || name === 'long description'
      || ALM_LABELS.has(name) || (ALM_WORDS.has(name) && style !== 'plain' && styleOf(line) === style));
    if (opens && (name === 'short description' || name === 'long description')) {
      current = name.split(' ')[0];
      style = styleOf(line);
      fields.set(current, match[2] ? [match[2]] : []);
    } else if (opens || heading) {
      current = null;
    } else if (current) {
      fields.get(current).push(line);
    }
  }
  const parts = ['short', 'long'].map((key) => (fields.get(key) ?? []).join('\n').trim())
    .filter(Boolean);
  return parts.length ? parts.join('\n\n') : String(record ?? '').trim();
}

const CAMP_DESIGNS = /^CAMP[\s_-]*Designs$/i;
const decoded = (text) => { try { return decodeURIComponent(text); } catch { return text; } };

/**
 * The folders of the SharePoint path a converted document's provenance block
 * gives, outermost first; the file name is not one of them.
 */
function provenanceFolders(text) {
  const block = /\*\*Document provenance\*\*\s*\n((?:\s*-.*\n?)+)/.exec(String(text));
  if (!block) return [];
  return block[1].split('\n').filter((line) => /^\s*-\s*SharePoint\b/i.test(line))
    .flatMap((line) => {
      const url = /^.*\]\(([^)\s]+)/.exec(line)?.[1] ?? '';
      const segments = url.replace(/^(?:[a-z]+:\/\/)?(?:<[^>]*>|[^/]*)/i, '').split('?')[0].split('/').map(decoded);
      return segments.slice(0, -1);
    });
}

/**
 * What intake received from the documents it was given: the inputs it counts
 * as received, and the ones it lacks. A document whose provenance path is under
 * CAMP Designs is the CAMP document, and its revision date is the updated design.
 * Neither is missing unless the record's descriptions name a CAMP design.
 */
export function documentInputs(documents, description = '') {
  const received = [];
  const missing = [];
  const camp = list(documents).filter((doc) => provenanceFolders(doc.text).some((folder) => CAMP_DESIGNS.test(folder.trim())));
  if (camp.length) {
    received.push(...camp.map((doc) => `CAMP document: ${doc.name}`));
    const dated = camp.map((doc) => ({ doc, day: revisedDate(doc.text) })).filter((row) => row.day);
    if (dated.length) {
      received.push(...dated.map(({ doc, day }) => `Updated design: ${doc.name}, revised ${day}`));
    } else {
      missing.push('Updated design: the CAMP document gives no revision date.');
    }
  } else if (/\bCAMP\s+design/i.test(almDescriptions(description))) {
    // The record points at a CAMP design, and no received document comes from there.
    missing.push('CAMP document: the record names one, and no received document comes from CAMP Designs.');
    missing.push('Updated design: no CAMP document was received.');
  }
  for (const doc of list(documents)) {
    if (doc.ruleCode === 'rules-derived') {
      missing.push(`Business rules for ${doc.name}: none in the rule master, so they are derived from its text.`);
    }
  }
  return { received, missing };
}

/** The candidate documents the change touches, chosen batch by batch from their outlines. */
async function pickDocuments(ctx, choices, index) {
  const { ref, pack, config } = ctx;
  const refs = [...ref.core, ref.docs.intake];
  const lineOf = new Map(choices.map((file, i) => [file, index[i]]));
  // A description longer than half the call is cut, so the candidates always have room.
  const half = Math.floor(room(ctx, false, refs) / 2);
  let description = String(pack[config.idFields.description] ?? ctx.description);
  while (description && estimateTokens(description) > half) {
    description = description.slice(0, Math.floor(description.length * 0.8));
  }
  const groups = batches(choices, (file) => lineOf.get(file),
    Math.max(1000, room(ctx, false, refs) - estimateTokens(description) - 1000));
  const picked = [];
  for (const [i, group] of groups.entries()) {
    const answer = await ask(ctx, {
      phase: 'intake', step: `documents-${i + 1}`, reasoning: false, refs,
      task: 'Pick every candidate document the change touches: its process descriptions and'
        + ' design specifications. A batch may hold none.',
      inputs: [['Change description', description],
        ['Candidate documents', asLines(group.map((file) => lineOf.get(file)))]],
      schema: S.documentPickSchema(group),
    });
    picked.push(...list(answer.documents));
  }
  return [...new Set(picked)];
}

export async function intake(ctx) {
  const { job, config, pack, ref } = ctx;
  const ids = config.idFields;
  const codeMissing = [];
  const missingFiles = [];
  let candidates = [];

  if (job.suite) {
    pack.suite = job.suite;
    const raw = runCommand(ctx, config.inputs.folderExport ?? [], { suite: job.suite });
    const exported = raw ? exportsOf(JSON.parse(raw)) : [];
    if (!exported.length) codeMissing.push('folder-export');
    ctx.exportJson = { exports: exported };
    const codeOf = new RegExp(config.suiteMerge?.codePattern ?? '^BR-[A-Z0-9]+\\.');
    ctx.documents = exported.map((doc) => {
      const active = list(doc.rules).filter((rule) => rule.status === 'active');
      const file = doc.doc ? config.at(doc.doc) : null;
      return {
        key: String(doc.prefix).replace(codeOf, ''),
        name: active[0]?.source_document ?? doc.doc,
        text: file && fs.existsSync(file) && fs.statSync(file).isFile()
          ? fs.readFileSync(file, 'utf8') : '',
        rules: active,
      };
    });
    const ruleCount = ctx.documents.reduce((n, doc) => n + doc.rules.length, 0);
    pack.suiteInput = `${config.terms.suiteInput ?? 'folder export of suite'} ${job.suite}`;
    pack[ids.description] = `The approved business rule set of suite ${job.suite}:`
      + ` ${ctx.documents.length} documents, ${ruleCount} active rules.`;
    ctx.description = pack[ids.description];
  } else {
    pack[ids.issue] = job.issue;
    if (job.change) pack[ids.change] = job.change;
    pack[ids.changeApplies] = Boolean(job.change);
    const descriptionFiles = job.descriptionFile ? [config.at(job.descriptionFile)]
      : config.inputs.description
        ? globFiles(config.root, fill(config.inputs.description, job)) : [];
    ctx.description = descriptionFiles.filter((f) => fs.existsSync(f))
      .map((f) => fs.readFileSync(f, 'utf8')).join('\n\n');
    // The model reads the whole record; the pack's change description is the ALM fields.
    pack[ids.description] = almDescriptions(ctx.description);
    if (blank(ctx.description)) codeMissing.push('description');
    if (!job.issue) codeMissing.push('issue-number');
    if (job.docs?.length) {
      ctx.documentPaths = job.docs.map((doc) => rootRelative(config, doc));
    } else {
      candidates = config.inputs.documentIndex
        ? globFiles(config.root, fill(config.inputs.documentIndex, job)).map((f) => relative(ctx, f))
        : [];
    }
  }

  // The model reads the description against the intake procedure; the
  // required-input check above stays in code.
  const choices = candidates;
  const index = choices.map((file) => candidateLine(file,
    fs.readFileSync(config.at(file), 'utf8')));
  const descriptionPieces = splitText(ctx.description, Math.max(2000,
    room(ctx, false, [...ref.core, ref.docs.intake]) - 1000));
  const answers = [];
  for (const [i, piece] of (descriptionPieces.length ? descriptionPieces : ['']).entries()) {
    answers.push(await ask(ctx, {
    phase: 'intake', step: `inventory-${i + 1}`, reasoning: false,
    refs: [...ref.core, ref.docs.intake],
    task: 'Run Job Intake for this request. The primary job is Build Test Pack; list any other'
      + ' request in the record as a secondary request. List the inputs received and the'
      + ' assumptions needed to proceed. List a decision only when the user must make a choice'
      + ' before the build can start; anything the build can get past with a stated assumption'
      + ' is an assumption.',
    inputs: [
      ['Request', job.suite ? `Suite pack for ${job.suite}` : `${config.terms.issue} ${job.issue}`
        + (job.change ? `, ${config.terms.change} ${job.change}` : `, no ${config.terms.change}`)],
      [descriptionPieces.length > 1 ? `Description, part ${i + 1} of ${descriptionPieces.length}`
        : 'Description', piece],
    ],
    schema: S.intakeSchema,
    }));
  }
  const pickedDocuments = choices.length ? await pickDocuments(ctx, choices, index) : [];
  // A description read in parts gives one answer per part; together they are the inventory.
  const union = (key) => [...new Set(answers.flatMap((a) => list(a[key])))];
  const answer = { documents: pickedDocuments, received: union('received'),
    secondaryRequests: union('secondaryRequests'), decisionsRequired: union('decisionsRequired'),
    assumptionsToProceed: union('assumptionsToProceed') };
  if (choices.length) ctx.documentPaths = answer.documents.map((doc) => rootRelative(config, doc));

  if (!job.suite) {
    ctx.documents = [];
    ctx.rulesFresh = true;
    for (const given of ctx.documentPaths ?? []) {
      const file = config.at(given);
      if (documentProblem(ctx, file)) {
        codeMissing.push('document-file');
        missingFiles.push(missingFileText(ctx, file));
        continue;
      }
      const number = ctx.documents.length + 1;
      const { code, rules } = documentRules(ctx, file, number);
      if (INTAKE_STOPS.includes(code)) throw new GateError('intake', code, { document: number });
      ctx.documents.push({
        key: path.basename(file).replace(/\.[^.]+$/, ''),
        file: relative(ctx, file),
        ruleCode: code,
        name: rules[0]?.source_document ?? path.basename(file).replace(/\.[^.]+$/, ''),
        text: fs.readFileSync(file, 'utf8'),
        rules,
      });
    }
    if (!ctx.documents.length) codeMissing.push('documents');
  }

  // Status lines name a document by its number, never by its name.
  (ctx.documents ?? []).forEach((doc, i) => { doc.number = i + 1; });
  const keys = (ctx.documents ?? []).map((doc) => doc.key);
  if (new Set(keys).size !== keys.length) throw new GateError('intake', 'document-key-shared');

  // What is missing is what the documents leave out, never a list of preferred inputs.
  const fromDocuments = job.suite ? { received: [], missing: [] } : documentInputs(ctx.documents, ctx.description);
  const READABLE = { 'folder-export': 'Rule export of the suite folder',
    description: 'Description of the defect or change', 'issue-number': 'Issue number',
    documents: 'Source documents' };
  const missing = [...new Set([...codeMissing.filter((code) => code !== 'document-file')
    .map((code) => READABLE[code] ?? code), ...missingFiles, ...fromDocuments.missing])]
    .map((text) => `${text.replace(/\.$/, '')}.`);
  pack.intake = {
    received: [...new Set([...list(answer.received), ...fromDocuments.received])],
    missing,
    authority: [],
    contextOnly: [],
    secondaryRequests: list(answer.secondaryRequests),
    decisionsRequired: filled(answer.decisionsRequired),
    assumptionsToProceed: list(answer.assumptionsToProceed),
    readiness: codeMissing.length ? 'INSUFFICIENT INPUTS'
      : filled(answer.decisionsRequired).length ? 'USER DECISION REQUIRED'
        : list(answer.assumptionsToProceed).length || missing.length
          ? 'READY WITH ASSUMPTIONS' : 'READY',
  };
  if (missing.length) {
    pack.limitations ??= {};
    pack.limitations['Job Intake'] = `Not received at intake: ${missing.join(' ')}`;
  }
  if (codeMissing.length) {
    throw new GateError('intake', 'missing-inputs', { missing: codeMissing.length });
  }
  // What the user has to decide is theirs to read, in the job's own folder.
  if (pack.intake.decisionsRequired.length) {
    ctx.private('intake-decisions.json', pack.intake.decisionsRequired);
    throw new GateError('intake', 'user-decision-required',
      { decisions: pack.intake.decisionsRequired.length });
  }
  return { documents: ctx.documents.length,
    rules: ctx.documents.reduce((n, doc) => n + doc.rules.length, 0) };
}

// ---------------------------------------------------------------------------
// Phase 1, Project Understanding Gate

/** Each document as text that fits, or as a digest of its pieces when it does not. */
async function documentViews(ctx, refs, reserve) {
  const budget = room(ctx, true, refs) - reserve;
  const whole = ctx.documents.map((doc) => `### ${doc.name}\n\n${doc.text}`);
  if (estimateTokens(whole.join('\n\n')) <= budget) return whole;
  const views = [];
  for (const doc of ctx.documents) views.push(`### ${doc.name} (digest)\n\n${await digestDocument(ctx, doc)}`);
  // A digest set that still does not fit means the documents are too many for one call.
  if (estimateTokens(views.join('\n\n')) > budget) {
    throw new GateError('phase1', 'documents-too-big', { documents: views.length });
  }
  return views;
}

/** A document's digest, made once from every piece of its text. */
async function digestDocument(ctx, doc) {
  if (doc.digest) return doc.digest;
  const pieces = splitText(doc.text, room(ctx, false, []) - 1000);
  const points = [];
  for (const [i, piece] of pieces.entries()) {
    const digest = await ask(ctx, {
      phase: 'phase1', step: `digest-d${doc.number}-${i + 1}`, reasoning: false, refs: [],
      task: 'List the behavior, screens, modules, business rules and data this part of'
        + ' the document describes, one point each, with its page where the text gives one.',
      inputs: [['Document', doc.name], ['Text', piece]],
      schema: S.digestSchema,
    });
    points.push(...digest.points);
  }
  doc.digest = points.map((p) => `- ${p}`).join('\n');
  return doc.digest;
}

/**
 * At a question gate: the build supervisor's answer to each of `questions`, recorded in
 * `pack` and returned as `{ question, answer, confidence, citations }`. When no supervisor
 * is watching, the wait runs out, or a question is left unanswered, the phase stops with
 * `code` and `counts`. `impact` says what the pack rests on the answers for.
 */
async function askSupervisor(ctx, pack, phase, code, questions, counts, impact) {
  const asked = questions.map((question, n) => ({ id: `Q${n + 1}`, question }));
  const outcome = ctx.supervise ? await ctx.supervise(phase, asked) : null;
  const byId = new Map(list(outcome?.answers).map((row) => [row.id, row]));
  if (asked.some((q) => !byId.has(q.id))) throw new GateError(phase, code, counts);
  const answers = asked.map(({ id, question }) => {
    const { answer, confidence, citations } = byId.get(id);
    return { question, answer, confidence, citations };
  });
  recordSupervisorAnswers(pack, answers, impact);
  return answers;
}

/**
 * The pack's assumptions for the supervisor's answers, each marked as answered by the
 * build supervisor with its confidence and citations, and a line for each under Job Intake.
 */
function recordSupervisorAnswers(pack, answers, impact) {
  const by = `Answered by the ${ANSWERED_BY}`;
  pack.assumptions ??= [];
  for (const a of answers) {
    pack.assumptions.push({
      assumption: a.answer,
      why: `${by} (${a.confidence}) from ${a.citations.length
        ? a.citations.join('; ') : 'no source, since none bears on the question'}.`,
      impact,
      clarification: `Confirm with the change owner: ${a.question.trim()}`,
      answeredBy: ANSWERED_BY, confidence: a.confidence, citations: a.citations, question: a.question,
    });
  }
  if (pack.intake && answers.length) {
    pack.intake.assumptionsToProceed = [...list(pack.intake.assumptionsToProceed),
      ...answers.map((a) => `${by} (${a.confidence}): ${a.answer}`)];
    if (pack.intake.readiness === 'READY') pack.intake.readiness = 'READY WITH ASSUMPTIONS';
  }
}

const phase1Tag = (rule) => (rule.status === 'retired' ? '[retired] ' : '');
const phase1Line = (rule, summary = rule.rule_summary ?? rule.summary ?? '') =>
  `- ${phase1Tag(rule)}${rule.rule_id ?? rule.id}: ${rule.name ?? ''} | ${summary}`;
const phase1Id = (rule) => rule.rule_id ?? rule.id;

/** The rules Phase 1 reads as full lines, or null when they do not fit in `budget`. */
function phase1Rules(ctx, budget) {
  const full = asLines(ctx.documents.flatMap((doc) => doc.rules).map((rule) => phase1Line(rule)));
  return estimateTokens(full) <= budget ? full : null;
}

/** A rule line cut to fit `tokens`, so one long rule cannot overflow a call. */
function fitLine(rule, tokens) {
  let summary = String(rule.rule_summary ?? rule.summary ?? '');
  while (summary && estimateTokens(phase1Line(rule, summary)) > tokens) {
    summary = summary.slice(0, Math.floor(summary.length * 0.8));
  }
  return phase1Line(rule, summary);
}

/**
 * Reads the rules against the documents in batches when they do not fit in one
 * call, the way Phase 3 reads them. Returns the rules that bear on the change,
 * what the batches found in conflict or missing, and the reading notes.
 */
async function readRulesInBatches(ctx, refs, views, budget, groups) {
  const relevant = [];
  const conflicts = [];
  const blockingMissing = [];
  const notes = [];
  for (const [i, group] of groups.entries()) {
    const ids = group.map(phase1Id);
    const answer = await ask(ctx, {
      phase: 'phase1', step: `rules-${i + 1}`, reasoning: true, refs,
      task: 'Read these business rules against the change description and the source documents.'
        + ' Mark each rule that bears on the change. A conflict is two authoritative sources that'
        + ' require different behavior for the same thing. A defect record saying the system behaves'
        + ' differently from a document today is the defect under test, not a conflict. A rule marked'
        + ' [retired] describes behavior that was removed; it is not a conflict with the documents.'
        + ' List every conflict the rules show, and any information without which the change cannot be'
        + ' understood or scoped. Write notes of a sentence or two on what the rules show about the change.',
      inputs: [['Change description', ctx.description],
        ['Source documents', views.join('\n\n')],
        ['Business rules', asLines(group.map((rule) => fitLine(rule, budget)))]],
      schema: S.phase1RulesSchema(ids),
    });
    const read = new Map(answer.rules.map((row) => [row.id, row]));
    if (ids.some((id) => !read.has(id))) {
      throw new GateError('phase1', 'rule-unread', { missing: ids.filter((id) => !read.has(id)).length });
    }
    relevant.push(...group.filter((rule) => read.get(phase1Id(rule)).bearsOnChange));
    conflicts.push(...filled(answer.conflicts));
    blockingMissing.push(...filled(answer.blockingMissing));
    if (answer.notes) notes.push(String(answer.notes).slice(0, NOTE_CHARS));
  }
  return { relevant, conflicts, blockingMissing, notes };
}

export async function phase1(ctx) {
  const { pack, ref, job } = ctx;
  const refs = [...ref.core, ref.docs.understandingGate];
  const ruleBudget = Math.floor(room(ctx, true, refs) / 2);
  let ruleText = phase1Rules(ctx, ruleBudget);
  const batchBudget = Math.floor(ruleBudget / 2);
  const groups = ruleText ? [] : batches(ctx.documents.flatMap((doc) => doc.rules),
    (rule) => fitLine(rule, batchBudget), batchBudget, 40);
  const views = await documentViews(ctx, refs,
    estimateTokens(ctx.description) + (ruleText ? estimateTokens(ruleText) : ruleBudget
      + Math.ceil(NOTE_CHARS / 3) * groups.length) + 4000);
  const read = ruleText ? null : await readRulesInBatches(ctx, refs, views, batchBudget, groups);
  const extra = [];
  const earlyConflicts = read ? read.conflicts.filter((c) => String(c).trim()) : [];
  const earlyMissing = read ? read.blockingMissing.filter((c) => String(c).trim()) : [];
  // What the rule batches found stops the gate before the understanding call and its processing,
  // unless the build supervisor answers the conflicts and nothing else is missing.
  const answered = [];
  if (earlyConflicts.length || earlyMissing.length) {
    ctx.private('phase1-conflicts.json', earlyConflicts);
    ctx.private('phase1-missing.json', earlyMissing);
    if (earlyMissing.length && !earlyConflicts.length) {
      throw new GateError('phase1', 'missing-information', { missing: earlyMissing.length });
    }
    if (earlyMissing.length) {
      throw new GateError('phase1', 'source-conflict', { conflicts: earlyConflicts.length });
    }
    answered.push(...await askSupervisor(ctx, pack, 'phase1', 'source-conflict', earlyConflicts,
      { conflicts: earlyConflicts.length },
      'The understanding summary reads the sources this way; later phases read the rules as written.'));
  }
  if (read) {
    // The rules that bear on the change go in whole; if even those are too many, each summary shrinks.
    const share = Math.max(50, Math.floor(ruleBudget / Math.max(1, read.relevant.length)));
    const whole = asLines(read.relevant.map((rule) => phase1Line(rule)));
    const shrunk = asLines(read.relevant.map((rule) => fitLine(rule, share)));
    const named = asLines(read.relevant.map((rule) => `- ${phase1Tag(rule)}${phase1Id(rule)}: ${rule.name ?? ''}`));
    // Whole lines, then shortened summaries, then names, then a count per document.
    ruleText = !read.relevant.length ? 'No rule bears on the change.'
      : [whole, shrunk, named].find((text) => estimateTokens(text) <= ruleBudget)
      ?? ctx.documents.map((doc) => `- ${doc.name}: ${doc.rules.length} rule(s)`).join('\n');
    extra.push(['Rule reading notes', read.notes.join('\n')]);
  }
  if (answered.length) {
    extra.push(['Conflicts the build supervisor answered', asLines(answered.map((a) =>
      `- ${noStop(a.question)}: ${a.answer}`))]);
  }
  const names = ctx.documents.map((doc) => doc.name);
  // Thinking off: the answer is about 540 tokens, and with thinking on the call spends its
  // whole output budget thinking and never reaches it.
  const answer = await ask(ctx, {
    phase: 'phase1', step: 'understanding', reasoning: false, refs,
    task: 'Run the Project Understanding Gate. Write the Project Understanding Summary,'
      + (job.suite ? '' : ' rank every source document by the authority order and decide its'
        + ' inclusion with a reason,')
      + ' name the module each document belongs to with a short upper-case abbreviation that'
      + ' no other module shares, and list every conflict between included sources.'
      + ' A conflict is two authoritative sources that require different behavior for the'
      + ' same thing. A defect record saying the system behaves differently from a document'
      + ' today is the defect under test, not a conflict. A rule marked [retired] describes'
      + ' behavior that was removed; it is not a conflict with the documents.'
      + ' For each source document record the information obtained from it and whether that'
      + ' information directly affects the change. List as blocking missing information only'
      + ' what the change cannot be understood or scoped without; anything else goes in the'
      + ' summary as missing information. Write the reason for the confidence rating first, then'
      + ' rate confidence honestly.'
      + (answered.length ? ' A conflict the build supervisor answered is settled by that answer;'
        + ' do not list it again.' : ''),
    inputs: [['Change description', ctx.description],
      ['Business rules', ruleText],
      ...extra,
      ['Source documents', views.join('\n\n')]],
    schema: S.understandingSchema({
      documents: names, keys: ctx.documents.map((doc) => doc.key),
      inclusions: ctx.builder.INCLUSIONS, suite: Boolean(job.suite),
    }),
  });
  ctx.private('phase1-summary.json', answer.summary);
  const modules = new Map(answer.modules.map((row) => [row.document, row]));
  const abbreviations = new Map();
  const byModule = new Map();
  // In an issue pack, every document of a module takes the abbreviation the config names for any
  // one of them, whatever the order they come in.
  const adopted = new Map();
  // The abbreviations the config names, held back from a suite's other documents whatever the order.
  const reserved = new Set();
  for (const doc of ctx.documents) {
    const row = modules.get(doc.key);
    const named = ctx.config.moduleAbbreviations[doc.key] ?? ctx.config.moduleAbbreviations[row?.module];
    if (named) reserved.add(named);
    if (!job.suite && row && ctx.config.moduleAbbreviations[doc.key]) {
      // Two documents of one module cannot be named different abbreviations.
      if (adopted.has(row.module) && adopted.get(row.module) !== named) {
        throw new GateError('phase1', 'abbreviation-shared');
      }
      adopted.set(row.module, named);
    }
  }
  for (const doc of ctx.documents) {
    const row = modules.get(doc.key);
    if (!row) throw new GateError('phase1', 'module-missing');
    const fixed = ctx.config.moduleAbbreviations[doc.key] ?? ctx.config.moduleAbbreviations[row.module]
      ?? (job.suite ? undefined : adopted.get(row.module));
    if (fixed) {
      // The config names this document's module, so the abbreviation stands for it in every column.
      // A suite numbers its cards per document, so a second document cannot share the abbreviation.
      if (abbreviations.has(fixed) && (job.suite || abbreviations.get(fixed) !== fixed)) {
        throw new GateError('phase1', 'abbreviation-shared');
      }
      doc.module = fixed;
      doc.abbreviation = fixed;
      abbreviations.set(fixed, fixed);
      byModule.set(fixed, fixed);
      continue;
    }
    doc.module = row.module;
    // A suite numbers its cards per document, so each document is its own
    // module with its own abbreviation, made unique by its code when two collide.
    if (job.suite && byModule.has(row.module)) doc.module = `${row.module} ${doc.key}`;
    if (job.suite && (abbreviations.has(row.abbreviation) || reserved.has(row.abbreviation))) {
      doc.abbreviation = `${row.abbreviation}${doc.key}`.replace(/[^A-Z0-9]/gi, '').toUpperCase();
      byModule.set(doc.module, doc.abbreviation);
    }
    // In an issue pack, two documents of one module share its first abbreviation.
    doc.abbreviation = byModule.get(doc.module) ?? row.abbreviation;
    byModule.set(doc.module, doc.abbreviation);
    const owner = abbreviations.get(doc.abbreviation);
    if (owner && owner !== doc.module) throw new GateError('phase1', 'abbreviation-shared');
    abbreviations.set(doc.abbreviation, doc.module);
  }
  if (job.suite) {
    for (const doc of ctx.documents) doc.inclusion = 'Included';
  } else {
    const decided = new Map(answer.sourceDocuments.map((row) => [row.name, row]));
    if (decided.size !== names.length) throw new GateError('phase1', 'inclusion-missing');
    pack.sourceDocuments = names.map((name) => decided.get(name));
    for (const doc of ctx.documents) doc.inclusion = decided.get(doc.name).inclusion;
    pack.intake.authority = pack.sourceDocuments.filter((d) => d.inclusion === 'Included')
      .map((d) => d.name);
    pack.intake.contextOnly = pack.sourceDocuments
      .filter((d) => d.inclusion === 'Supporting Context Only').map((d) => d.name);
    if (!pack.intake.authority.length) throw new GateError('phase1', 'no-included-source');
  }
  ctx.summary = answer.summary;
  // What a stopped gate found is the user's to read, in the job's own folder.
  // A conflict the build supervisor already answered before the understanding call is settled.
  const settled = new Set(answered.map((a) => plainWords(a.question)));
  const conflicts = [...filled(answer.conflicts), ...filled(read?.conflicts)]
    .filter((c) => !settled.has(plainWords(c)));
  const blockingMissing = [...filled(answer.blockingMissing), ...filled(read?.blockingMissing)];
  ctx.private('phase1-conflicts.json', conflicts);
  ctx.private('phase1-missing.json', blockingMissing);
  if (conflicts.length) {
    // The supervisor is asked only when the conflicts are all that stops the phase.
    if (blockingMissing.length) throw new GateError('phase1', 'source-conflict', { conflicts: conflicts.length });
    answered.push(...await askSupervisor(ctx, pack, 'phase1', 'source-conflict', conflicts,
      { conflicts: conflicts.length },
      'The understanding summary was written before this answer; later phases read the rules as written.'));
  }
  if (blockingMissing.length) {
    throw new GateError('phase1', 'missing-information', { missing: blockingMissing.length });
  }
  if (answer.summary.confidence === 'Low') throw new GateError('phase1', 'low-confidence');
  return { included: ctx.documents.filter((d) => d.inclusion === 'Included').length,
    ...(answered.length ? { supervised: answered.length } : {}) };
}

const summaryText = (ctx) => Object.entries(ctx.summary ?? {})
  .map(([key, value]) => `${key}: ${value}`).join('\n');

// ---------------------------------------------------------------------------
// Phase 2, Business Rule / Requirement Intake

/**
 * What Phase 2 does with one document whose rule export came back as `code`:
 * `stop` when the job stops on it, `warn` (a reason code) when it keeps the rules
 * intake held and leaves a warning instead. A document with no held rules stops
 * on any Phase 2 stop code.
 */
export function phase2Verdict(doc, code) {
  const held = USABLE_RULE_CODES.includes(doc.ruleCode);
  const extracted = ['rules-ok', 'rules-stale'].includes(doc.ruleCode);
  // The export's `noRules` answer comes back as `rules-derived` when deriving is allowed.
  const noneNow = code === 'rules-not-extracted' || code === 'rules-derived';
  let warn = null;
  if (held && (code === 'rule-export-failed' || code === 'document-file')) warn = code;
  else if (extracted && noneNow) warn = 'rules-not-extracted';
  return { stop: !warn && PHASE2_STOPS.includes(code), warn };
}

/**
 * Reads each Included document's rule export again, so a job resumed after the
 * user extracted or fixed the rules sees them, and stops when one still has
 * none usable. A run whose intake just exported a document with usable rules
 * keeps those rules, and so does a checkpoint with no file path for the
 * document. An export outage or a path that no longer resolves, after a usable
 * intake, keeps the rules held and leaves a warning. So does a `noRules` answer
 * for a document intake read as `rules-ok` or `rules-stale`: rules in the master
 * do not disappear between two phases. A valid rule list replaces the held
 * rules. Every failing document gets a status line and the stop
 * names them all, under the most basic code among them. A context-only
 * document is not read again.
 */
function refreshRules(ctx) {
  const failing = [];
  for (const doc of ctx.documents) {
    if (doc.inclusion !== 'Included' || !doc.file) continue;
    if (USABLE_RULE_CODES.includes(doc.ruleCode) && ctx.rulesFresh) continue;
    const { code, rules } = documentRules(ctx, doc.file);
    const { stop, warn } = phase2Verdict(doc, code);
    if (warn) {
      ctx.logs.status({ job: ctx.job.id, phase: 'phase2', event: 'warn', reason: warn,
        document: doc.number });
      continue;
    }
    doc.ruleCode = code;
    if (stop) failing.push({ number: doc.number, code });
    else doc.rules = rules;
  }
  if (!failing.length) return;
  for (const { number, code } of failing) {
    ctx.logs.status({ job: ctx.job.id, phase: 'phase2', event: 'stop-doc', document: number,
      reason: code });
  }
  const code = PHASE2_STOPS.find((c) => failing.some((row) => row.code === c));
  throw new GateError('phase2', code,
    { documents: failing.length, numbers: failing.map((row) => row.number).join(' ') });
}

const RETIRED_SUMMARY = 'Retired: this rule was removed from the master.';
const isRetired = (rule) => String(rule.summary ?? '').startsWith('Retired:');

/**
 * Warns for each Included document whose text has struck-through behavior that
 * no retired rule of its export cites (a fragment edit or a restated sentence
 * needs none), and records a limitation
 * under Job Intake. It runs at the start of Phase 2, once inclusion is decided
 * and the rules have been read again, so it judges the rules the pack uses. It
 * is a warning, never a stop: the status line names the document by number, the
 * detail log says where the spans sit.
 */
function warnUnretired(ctx) {
  const named = [];
  for (const doc of ctx.documents) {
    if (doc.inclusion !== 'Included' || !doc.text) continue;
    const spans = uncitedStruck(doc.text, doc.rules);
    if (!spans.length) continue;
    ctx.logs.status({ job: ctx.job.id, phase: 'phase2', event: 'warn', reason: 'retired-rule-missing',
      document: doc.number });
    ctx.logs.detail(`document ${doc.number} has struck-through text no retired rule cites`,
      spans.map((s) => (s.page === null ? `heading "${s.heading ?? 'none'}"` : `page ${s.page}`))
        .join('\n'));
    named.push(doc.name);
  }
  if (!named.length) return;
  const text = `Struck-through text in ${named.join(', ')} has no rule citing it,`
    + ' so removed behavior may be missing from the pack. Extract or update the rules for each of them.';
  ctx.pack.limitations ??= {};
  const held = ctx.pack.limitations['Job Intake'] ?? '';
  if (!held.includes(text)) ctx.pack.limitations['Job Intake'] = `${held} ${text}`.trim();
}

export async function phase2(ctx) {
  const { pack, ref } = ctx;
  const risks = ctx.riskLevels;
  const rules = [];
  let derived = 0;
  if (!ctx.job.suite) {
    refreshRules(ctx);
    warnUnretired(ctx);
  }
  for (const doc of ctx.documents.filter((d) => d.inclusion === 'Included')) {
    if (doc.rules.length) {
      for (const rule of doc.rules) {
        // A retired rule stays in the pack, marked in its summary as removed; Phase 3
        // decides whether the change concerns that removal.
        const retired = rule.status === 'retired';
        rules.push({
          id: rule.rule_id, name: stripId(rule), module: doc.module, sourceDocument: doc.name,
          sourcePage: String(rule.source_page ?? '') || 'N/A',
          requirementType: String(rule.requirement_type ?? '').trim()
            || ctx.config.ruleShape.requirementType,
          summary: retired ? `${RETIRED_SUMMARY} ${rule.rule_summary ?? ''}`.trim() : rule.rule_summary,
          risk: risks.includes(rule.risk_level) ? rule.risk_level : undefined,
          status: retired ? 'Retired' : 'Active',
        });
      }
      continue;
    }
    // A document the master holds no rules for has them derived from its text,
    // each named by its source and statement, never given an invented ID.
    const refs = [...ref.core, ref.docs.ruleIntake];
    for (const [i, piece] of splitText(doc.text, room(ctx, false, refs) - 1000).entries()) {
      const answer = await ask(ctx, {
        phase: 'phase2', step: `derive-d${doc.number}-${i + 1}`, reasoning: false, refs,
        task: 'Extract every business rule this part of the document states. One rule per'
          + ' decision, a short statement naming it, the page it is on (N/A when the text'
          + ' has no pages), a one-sentence summary, and its risk.',
        inputs: [['Document', doc.name], ['Text', piece]],
        schema: S.derivedRulesSchema(risks),
      });
      for (const row of answer.rules) {
        derived += 1;
        ctx.derivedDocuments = [...new Set([...list(ctx.derivedDocuments), doc.name])];
        const page = String(row.sourcePage || 'N/A');
        rules.push({
          id: `${doc.key} ${page === 'N/A' ? '' : `p${page} `}${row.statement}`,
          name: row.statement, module: doc.module, sourceDocument: doc.name, sourcePage: page,
          summary: row.summary, risk: row.risk, status: 'Active',
          requirementType: ctx.config.ruleShape.requirementType,
        });
      }
    }
  }
  const seen = new Set();
  for (const rule of rules) {
    if (seen.has(rule.id)) throw new GateError('phase2', 'duplicate-rule-id');
    seen.add(rule.id);
    if (blank(rule.summary) || blank(rule.name)) throw new GateError('phase2', 'untraceable-rule');
  }
  if (!rules.length) throw new GateError('phase2', 'no-rules');
  stopOnDuplicateWording(ctx, rules);
  const pagesMissing = warnMissingPages(ctx, rules);
  const supervised = ctx.job.suite ? 0 : await settleConflicts(ctx, rules);
  pack.rules = rules;
  return { rules: rules.length, derived, pagesMissing, ...(supervised ? { supervised } : {}) };
}

const wordingKey = (rule) => String(rule.summary ?? '').toLowerCase().replace(/[^a-z0-9.<>%$=+-]+/g, ' ')
  .replace(/\s+/g, ' ').trim().replace(/\.$/, '');
const DUPLICATE_MIN_CHARS = 40;

/**
 * Stops when two live rules of one document say the same thing in the same words. A short
 * statement counts only when the two rules also share a name, so field rules such as
 * "The field is mandatory." do not stop a master. The master has to retire one of the pair.
 */
function stopOnDuplicateWording(ctx, rules) {
  const pairs = [];
  const documents = new Set();
  const held = new Map();
  for (const rule of rules) {
    if (rule.status === 'Retired' || list(ctx.derivedDocuments).includes(rule.sourceDocument)) continue;
    const text = wordingKey(rule);
    const key = `${rule.sourceDocument}\n${text}`;
    const twins = held.get(key) ?? [];
    for (const twin of twins) {
      if (text.length >= DUPLICATE_MIN_CHARS || twin.name === rule.name) {
        pairs.push([twin.id, rule.id]);
        documents.add(rule.sourceDocument);
      }
    }
    held.set(key, [...twins, rule]);
  }
  if (!pairs.length) return;
  const numbers = ctx.documents.filter((d) => documents.has(d.name)).map((d) => d.number);
  for (const number of numbers) {
    ctx.logs.status({ job: ctx.job.id, phase: 'phase2', event: 'stop-doc', document: number,
      reason: 'duplicate-rule-wording' });
  }
  ctx.private('phase2-duplicates.json', pairs);
  throw new GateError('phase2', 'duplicate-rule-wording',
    { documents: numbers.length, numbers: numbers.join(' ') });
}

/**
 * Warns for each document whose live rules lack a source page, and records a limitation under
 * Job Intake. A warning, never a stop; the status line carries counts, the detail log the IDs.
 * Returns how many rules lack a page.
 */
function warnMissingPages(ctx, rules) {
  let total = 0;
  const named = [];
  for (const doc of ctx.documents.filter((d) => d.inclusion === 'Included')) {
    const missing = rules.filter((r) => r.sourceDocument === doc.name && r.status !== 'Retired'
      && r.sourcePage === 'N/A' && !list(ctx.derivedDocuments).includes(r.sourceDocument));
    if (!missing.length) continue;
    total += missing.length;
    ctx.logs.status({ job: ctx.job.id, phase: 'phase2', event: 'warn', reason: 'rule-page-missing',
      document: doc.number, rules: missing.length });
    ctx.logs.detail(`document ${doc.number} has rules without a source page`,
      missing.map((r) => r.id).join('\n'));
    named.push(...missing.map((r) => r.id));
  }
  if (!named.length) return 0;
  const text = `Rules with no source page: ${named.join(', ')}. Their cards cannot cite a page.`;
  ctx.pack.limitations ??= {};
  const held = ctx.pack.limitations['Job Intake'] ?? '';
  if (!held.includes(text)) ctx.pack.limitations['Job Intake'] = `${held} ${text}`.trim();
  return total;
}

/**
 * Asks whether any two live rules require different behavior for the same thing. When they
 * do, the build supervisor is asked how to read each pair, and the run stops when it does
 * not answer. An exception to another rule is not a conflict. Rules are read in batches, so a
 * pair split across two batches is never compared. Returns how many conflicts were answered.
 */
async function settleConflicts(ctx, rules) {
  const refs = [...ctx.ref.core, ctx.ref.docs.ruleIntake];
  const live = rules.filter((r) => r.status !== 'Retired')
    .sort((a, b) => a.sourceDocument.localeCompare(b.sourceDocument));
  const found = [];
  for (const [i, group] of batches(live, ruleLine, room(ctx, false, refs) - 2000).entries()) {
    if (group.length < 2) continue;
    const ids = group.map((r) => r.id);
    const answer = await ask(ctx, {
      phase: 'phase2', step: `conflicts-${i + 1}`, reasoning: false, refs,
      task: 'List each pair of rules that require different behavior for the same thing, with'
        + ' a one-sentence statement of the conflict. A rule that states an exception to another'
        + ' rule, such as an override of a block, is not a conflict. A defect record that'
        + ' disagrees with a rule is not a conflict. Answer with no pairs when none conflict.',
      inputs: [['Rules', asLines(group.map(ruleLine))]],
      schema: S.ruleConflictSchema(ids),
    });
    for (const c of answer.conflicts) {
      const key = [...c.rules].sort().join('\n');
      if (c.rules[0] === c.rules[1] || found.some((f) => [...f.rules].sort().join('\n') === key)) continue;
      found.push(c);
    }
  }
  if (!found.length) return 0;
  ctx.private('phase2-conflicts.json', found);
  const answers = await askSupervisor(ctx, ctx.pack, 'phase2', 'rule-conflict',
    found.map((c) => `Rules ${c.rules.join(' and ')}: ${c.conflict}`), { conflicts: found.length },
    'The cards test both rules as written; this answer says which reading holds.');
  return answers.length;
}

// ---------------------------------------------------------------------------
// Phase 3, Change Scope Analysis

const REVIEW_RULE = ' List under user review each question only the user can settle, such as which'
  + ' of two readings of the change applies; anything an assumption can settle stays an assumption.';

const ruleLine = (rule) => `- ${rule.id} | ${rule.name} | ${rule.module} | ${rule.summary}`;

/** Text as its words alone: lower case, every run of other characters one space. */
const plainWords = (text) => String(text ?? '').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();

/**
 * The fewest words a quote or a settled reading may have: fewer cannot name both the
 * thing and what holds for it, and a lone ruling word copied into the statement is caught.
 */
const MIN_WORDS = 3;
const wordCount = (text) => plainWords(text).split(' ').filter(Boolean).length;

/**
 * Reads each review question the scope calls raised against the change description,
 * with thinking off, and settles it there when it can. An answer becomes an assumption
 * whose why quotes the sentence, when that sentence is found in the description with only
 * the words compared; an answer whose sentence is not found is an ordinary assumption. A
 * question one reading lets the work go on under becomes an assumption too. A question
 * whose statement is blank or too short to stand alone, which a lone ruling word is, or
 * whose assumption talks about how the pipeline ran, is returned in `kept` with the
 * sentence the model quoted and whether that sentence was found. A found quote shows the
 * sentence is in the description, not that it decides the question.
 */
async function triageReview(ctx, refs, questions) {
  const task = 'Each question below was raised while the rules were classified against the change'
    + ' description. Settle each one from the change description alone. In quote, copy the sentence'
    + ' of the change description that bears most on the question, exactly as written, spelling'
    + ' included, or leave it empty when no sentence does. In ruling: answered only when that sentence'
    + ' decides between the readings the question names; assumption when the description leaves the'
    + ' question open, such as a sentence that names one case when the question asks whether others'
    + ' are included, but one reading lets the testing go on; kept only when the description says two'
    + ' things that cannot both hold, or no one reading lets the testing go on. In statement, write'
    + ' the answer or the assumed reading as a full sentence about the application. In testImpact,'
    + ' write what the testing misses if the statement is wrong, in toConfirm the question to ask'
    + ' the change owner, and in why the reason for the ruling. For kept, quote is the sentence'
    + ' that leaves the question open, and statement, testImpact, toConfirm and why stay empty.'
    + ASSUMPTION_RULE;
  const source = ` ${plainWords(ctx.description)} `;
  const found = (quote) => wordCount(quote) >= MIN_WORDS && source.includes(` ${plainWords(quote)} `);
  const usable = (statement) => wordCount(statement) >= MIN_WORDS;
  const out = { assumptions: [], kept: [], answered: 0, assumed: 0 };
  const fixed = estimateTokens(ctx.description) + 2000;
  for (const [i, group] of batches(questions, (q) => q, room(ctx, false, refs) - fixed).entries()) {
    const keys = group.map((_, n) => `Q${n + 1}`);
    const answer = await ask(ctx, {
      phase: 'phase3', step: `review-${i + 1}`, reasoning: false, refs, task,
      inputs: [['Change description', ctx.description],
        ['Questions', asLines(group.map((q, n) => `- ${keys[n]}: ${q}`))]],
      schema: S.reviewTriageSchema(keys),
    });
    const rows = new Map(answer.questions.map((row) => [row.question, row]));
    group.forEach((question, n) => {
      const row = rows.get(keys[n]) ?? {};
      const quote = String(row.quote ?? '').trim();
      const verbatim = found(quote);
      const statement = String(row.statement ?? '').trim();
      let ruling = usable(statement) ? row.ruling : 'kept';
      if (ruling === 'answered' && !verbatim) ruling = 'assumption';
      const [assumed] = ruling === 'kept' ? [] : withoutPipelineTerms(ctx, [{ assumption: statement,
        why: ruling === 'answered' ? `The change description says: "${quote}"` : String(row.why ?? ''),
        impact: String(row.testImpact ?? ''), clarification: String(row.toConfirm ?? '') }]);
      if (assumed) {
        out.assumptions.push(assumed);
        out[ruling === 'answered' ? 'answered' : 'assumed'] += 1;
      } else {
        out.kept.push({ question, quote, verbatim });
      }
      ctx.logs.detail(`phase3 review ${assumed ? ruling : 'kept'}`, `${question}\n${quote}\n${statement}`);
    });
  }
  return out;
}

export async function phase3(ctx) {
  const { pack, ref, job } = ctx;
  if (job.suite) {
    for (const rule of pack.rules) {
      rule.impact = 'Regression';
      rule.rationale = 'Suite baseline: approved rule held in the master';
    }
    pack.changeScope = { downstream: 'READY' };
    return { regression: pack.rules.length, downstream: 'READY' };
  }
  const refs = [...ref.core, ref.docs.scope];
  const fixed = estimateTokens(ctx.description + summaryText(ctx)) + 2000;
  const groups = batches(pack.rules, ruleLine, room(ctx, true, refs) - fixed);
  const byId = new Map(pack.rules.map((rule) => [rule.id, rule]));
  pack.assumptions ??= [];
  const assumedBefore = pack.assumptions.length;
  const reviewQuestions = [];
  for (const [i, group] of groups.entries()) {
    const ids = group.map((rule) => rule.id);
    let answer = await ask(ctx, {
      phase: 'phase3', step: `scope-${i + 1}`, reasoning: true, refs,
      task: 'Classify each rule by the change description: Direct Change, Indirect Impact,'
        + ' Regression or Not Impacted, with a one-sentence rationale. A rule the change does'
        + ' not touch is Not Impacted. A rule whose summary starts with "Retired:" was removed'
        + ' from the master: it is a Direct Change only when the change description concerns'
        + ' that removal, and Not Impacted otherwise; for a Direct Change, the rationale says its'
        + ' removal is to be verified. A retired rule keeps its Status of Retired; never classify'
        + ' it Superseded or Removal Verification. Record each ambiguity as an assumption.'
        + ASSUMPTION_RULE + REVIEW_RULE
        + (groups.length > 1 ? ` The rules come in ${groups.length} parts; this is part ${i + 1} of`
          + ` ${groups.length}. The other rules are classified in the other parts, so never assume`
          + ' a rule is missing or was left out.' : ''),
      inputs: [['Change description', ctx.description], ['Project understanding', summaryText(ctx)],
        ['Rules', asLines(group.map(ruleLine))]],
      schema: S.scopeSchema(ids, ctx.builder.IMPACT_CLASSES),
    });
    const classified = new Map(answer.rules.map((row) => [row.id, row]));
    if (ids.some((id) => !classified.has(id))) {
      throw new GateError('phase3', 'unclassified-rule',
        { missing: ids.filter((id) => !classified.has(id)).length });
    }
    for (const row of answer.rules) {
      Object.assign(byId.get(row.id), { impact: row.impact, rationale: row.rationale });
    }
    pack.assumptions.push(...withoutPipelineTerms(ctx, answer.assumptions));
    reviewQuestions.push(...list(answer.userReview).filter((q) => !blank(q)));
    answer = null;
  }
  const counts = {};
  for (const rule of pack.rules) counts[rule.impact] = (counts[rule.impact] ?? 0) + 1;
  const triage = await triageReview(ctx, refs, reviewQuestions);
  pack.assumptions.push(...triage.assumptions);
  const reviewed = reviewQuestions.length
    ? { raised: reviewQuestions.length, answered: triage.answered, assumed: triage.assumed } : {};
  let supervised = 0;
  if (triage.kept.length) {
    ctx.private('phase3-review.json', triage.kept);
    pack.changeScope = { downstream: 'NEEDS USER REVIEW' };
    // The rules keep the impact they were classified with; the answers stand beside them.
    const answers = await askSupervisor(ctx, pack, 'phase3', 'needs-user-review',
      triage.kept.map((k) => k.question),
      { review: triage.kept.length, ...reviewed, direct: counts['Direct Change'] ?? 0 },
      'The rules were classified before this answer; a different answer can change their impact.');
    supervised = answers.length;
  }
  const downstream = pack.assumptions.length > assumedBefore ? 'READY WITH ASSUMPTIONS' : 'READY';
  pack.changeScope = { downstream };
  return { direct: counts['Direct Change'] ?? 0, indirect: counts['Indirect Impact'] ?? 0,
    regression: counts.Regression ?? 0, notImpacted: counts['Not Impacted'] ?? 0, downstream, ...reviewed,
    ...(supervised ? { supervised } : {}) };
}

// ---------------------------------------------------------------------------
// Phase 4, Impact Analysis

const moduleCounts = (rules) => {
  const counts = new Map();
  for (const rule of rules) counts.set(rule.module, (counts.get(rule.module) ?? 0) + 1);
  return [...counts].map(([module, n]) => `- ${module}: ${n} rule(s)`).join('\n');
};

/**
 * The impact analysis as one line per area, within `tokens`. Items go in round-robin, the
 * first of every area before the second of any, so a long early area never crowds out a later
 * one; an area that loses items ends with how many. Empty when the pack holds no analysis.
 */
export function impactsText(impacts, tokens) {
  if (!impacts || typeof impacts !== 'object') return '';
  const cut = (item) => String(item).slice(0, 300);
  const areas = S.IMPACT_AREAS.map(([key, label]) => ({ label, items: list(impacts[key]).map(cut), kept: 0 }));
  let used = 100;
  for (let round = 0; ; round += 1) {
    let any = false;
    for (const area of areas) {
      if (area.full || round >= area.items.length) continue;
      any = true;
      const cost = estimateTokens(area.items[round]) + 1;
      if (used + cost > tokens) {
        // This area's next item is too long for what is left; a shorter one elsewhere may still fit.
        area.full = true;
        continue;
      }
      used += cost;
      area.kept += 1;
    }
    if (!any) break;
  }
  return renderImpacts(areas);
}

function renderImpacts(areas) {
  return areas.map(({ label, items, kept }) => {
    if (!items.length) return `${label}: none found`;
    const more = items.length - kept;
    return `${label}: ${items.slice(0, kept).join('; ')}${more ? `${kept ? '; ' : ''}${more} more not shown` : ''}`;
  }).join('\n');
}

/** The impact analysis as a prompt input, a tenth of the call's room at most. */
export function impactsInput(ctx, pack, reasoning, refs) {
  const cap = Math.min(1500, Math.floor(room(ctx, reasoning, refs) / 10));
  return ['Impact analysis by area', impactsText(pack.impacts, cap)];
}

export async function phase4(ctx) {
  const { pack, ref } = ctx;
  const refs = [...ref.core, ...ref.chapters('4')];
  const impacted = pack.rules.filter((rule) => rule.impact !== 'Not Impacted');
  const fixed = estimateTokens(ctx.description + summaryText(ctx)) + 2000;
  const ruleText = asLines(impacted.map((rule) => `${ruleLine(rule)} | ${rule.impact}`));
  const answer = await ask(ctx, {
    phase: 'phase4', step: 'impact', reasoning: true, refs,
    task: 'Run the Impact Analysis: modules, windows, business functions, upstream and'
      + ' downstream effects, data, security and roles, batch, notices, reports and interfaces.'
      + ' Fill the executive summary from it. Record what the change reaches under impacts, one'
      + ' short line per item that names a screen, function or output rather than a rule ID; leave'
      + ' an area empty when the change reaches none of it.',
    inputs: [['Change description', ctx.description], ['Project understanding', summaryText(ctx)],
      ['Source documents', ctx.documents.filter((d) => d.inclusion === 'Included')
        .map((d) => d.name).join('\n')],
      estimateTokens(ruleText) <= room(ctx, true, refs) - fixed
        ? ['Impacted rules', ruleText] : ['Impacted rules by module', moduleCounts(impacted)]],
    schema: S.impactSchema,
  });
  pack.executiveSummary = { ...answer.executiveSummary, confidence: '' };
  pack.impacts = Object.fromEntries(S.IMPACT_AREAS.map(([key]) => [key,
    [...new Set(list(answer.impacts?.[key]).map((item) => String(item).trim()).filter(Boolean))]]));

  // Every impacted rule is rated from the impact analysis, with the master's risk as its
  // starting value; a rule the change does not touch keeps the master's, or is rated when
  // the master gave none.
  // A suite has no change to rate against, so it keeps the approved risks and rates only the gaps.
  const toRate = pack.rules.filter((rule) => !rule.risk
    || (!ctx.job.suite && rule.impact !== 'Not Impacted'));
  const rateLine = (rule) => `${ruleLine(rule)} | ${rule.impact} | master risk: ${rule.risk ?? 'none'}`;
  const rateFixed = estimateTokens(ctx.description + JSON.stringify(pack.executiveSummary)) + 2000;
  const groups = batches(toRate, rateLine, room(ctx, false, refs) - rateFixed, 60);
  for (const [i, group] of groups.entries()) {
    const rated = await ask(ctx, {
      phase: 'phase4', step: `risk-${i + 1}`, reasoning: false, refs,
      task: 'Give each rule its risk level from the impact analysis. A rule\'s master risk is'
        + ' where to start; keep it unless the impact analysis says the change makes it higher'
        + ' or lower.',
      inputs: [['Change description', ctx.description],
        ['Impact analysis', JSON.stringify(pack.executiveSummary)],
        ['Rules', asLines(group.map(rateLine))]],
      schema: S.riskSchema(group.map((rule) => rule.id), ctx.riskLevels),
    });
    const byId = new Map(rated.rules.map((row) => [row.id, row.risk]));
    for (const rule of group) {
      if (!byId.has(rule.id)) throw new GateError('phase4', 'unrated-rule');
      rule.risk = byId.get(rule.id);
    }
  }
  // A rule the change itself alters is never rated below the top level, the first of the
  // configured risk levels.
  const top = ctx.riskLevels[0];
  const raised = pack.rules.filter((rule) => rule.impact === 'Direct Change' && rule.risk !== top);
  if (raised.length) {
    ctx.logs.detail('phase4 raised risk', raised.map((rule) => `${rule.id}: ${rule.risk} to ${top}`)
      .join('\n'));
    for (const rule of raised) rule.risk = top;
  }
  return { impacted: impacted.length, rated: toRate.length, raised: raised.length };
}

// ---------------------------------------------------------------------------
// Phase 5, Testing Objective Selection

const squash = (text) => String(text ?? '').replace(/\s+/g, ' ').trim().toLowerCase();
/** Whether a text, with its whitespace squashed, matches every term of an evidence rule. */
const holdsTerms = (text, rule) => rule.terms.every((term) => new RegExp(term, 'i').test(squash(text)));

/**
 * The Direct Change and Indirect Impact rules, as `name. summary` lines, whose
 * text holds all the terms of at least one evidence rule, which are the only rules
 * a quote can come from, as many as fit `budget` tokens. The cap is logged.
 */
function quotableRules(ctx, evidence, budget) {
  const lines = list(ctx.pack.rules)
    .filter((rule) => ['Direct Change', 'Indirect Impact'].includes(rule.impact))
    .map((rule) => `- ${rule.name}. ${rule.summary}`)
    .filter((line) => evidence.some((rule) => holdsTerms(line, rule)));
  const kept = [];
  let used = 0;
  for (const line of lines) {
    used += estimateTokens(line);
    if (used > budget) break;
    kept.push(line);
  }
  if (kept.length < lines.length) {
    ctx.logs.detail('phase 5: rule lines left out to fit the model',
      `${lines.length - kept.length} of ${lines.length} rule lines did not fit`);
  }
  return kept;
}

/**
 * Whether the model's answer for one configured evidence rule holds: the answer
 * says it does, and its quote appears word for word (whitespace and case aside) in
 * the record's ALM descriptions or in a Direct Change or Indirect Impact rule (as
 * `name. summary`), and matches every term of the rule. Returns { ok, why }.
 */
export function evidenceHolds(ctx, rule, row) {
  if (row?.holds !== true) return { ok: false, why: 'not claimed' };
  const quote = squash(row.quote);
  if (!quote) return { ok: false, why: 'no quote' };
  const sources = [almDescriptions(ctx.description), ...list(ctx.pack.rules)
    .filter((r) => ['Direct Change', 'Indirect Impact'].includes(r.impact))
    .flatMap((r) => [r.name, r.summary, `${r.name}. ${r.summary}`])];
  if (!sources.some((source) => squash(source).includes(quote))) {
    return { ok: false, why: 'quote not in the description or an impacted rule' };
  }
  if (!holdsTerms(quote, rule)) return { ok: false, why: 'quote lacks the terms of the rule' };
  return { ok: true, why: 'quoted' };
}

export async function phase5(ctx) {
  const { pack, ref, job } = ctx;
  const objectives = ctx.builder.OBJECTIVES;
  const refs = [...ref.core, ...ref.chapters('5')];
  // The config's evidence rules; a suite pack has no change to hold evidence of.
  // A rule whose objective pattern matches no objective of the builder is logged and left out.
  const named = (rule) => objectives.filter((objective) => new RegExp(rule.objective, 'i').test(objective));
  const evidence = (job.suite ? [] : list(ctx.config?.objectiveEvidence)).filter((rule) => {
    if (named(rule).length) return true;
    ctx.logs.detail(`phase 5: evidence ${rule.id} names no objective`, rule.objective);
    return false;
  });
  const byImpact = Object.entries(pack.rules.reduce((acc, rule) => ({
    ...acc, [rule.impact]: (acc[rule.impact] ?? 0) + 1 }), {}))
    .map(([impact, n]) => `- ${impact}: ${n}`).join('\n');
  const quotable = evidence.length ? quotableRules(ctx, evidence, room(ctx, true, refs)
    - estimateTokens(`${ctx.description}${JSON.stringify(pack.executiveSummary)}${byImpact}`) - 1500) : [];
  const answer = await ask(ctx, {
    phase: 'phase5', step: 'objectives', reasoning: true, refs,
    task: `Decide every one of the ${objectives.length} testing objectives: applicable or not,`
      + ' with a reason each.'
      + (job.suite ? ` This is a suite pack with no change under test, so ${ctx.coreObjective}`
        + ' is not applicable.' : '')
      + evidence.map((rule) => ` ${named(rule).join(' and ')} is applicable when ${rule.claim}. Say in`
        + ` evidence.${rule.id}.holds whether it is and, when it is, quote in evidence.${rule.id}.quote,`
        + ' word for word, the sentence of the description or of a Direct Change or Indirect Impact'
        + ' rule that says so.').join(''),
    // The description is the ALM fields and the rule lines are the rules' own text: the
    // sentences evidenceHolds accepts a quote from.
    inputs: [['Change description', job.suite ? ctx.description : almDescriptions(ctx.description)],
      ...(evidence.length ? [['Direct Change and Indirect Impact rules', quotable.join('\n')]] : []),
      ['Executive summary', JSON.stringify(pack.executiveSummary)],
      ['Rules by impact', byImpact]],
    schema: S.objectivesSchema(objectives, { evidence: evidence.map((rule) => rule.id) }),
  });
  const decided = new Map(answer.objectives.map((row) => [row.objective, row]));
  if (objectives.some((objective) => !decided.has(objective))) {
    throw new GateError('phase5', 'objective-undecided');
  }
  pack.objectives = objectives.map((objective) => decided.get(objective));
  if (job.suite) {
    const core = decided.get(ctx.coreObjective);
    core.applicable = false;
  }
  // Evidence only ever makes an objective applicable; it never takes the model's yes away.
  const rows = new Map(list(answer.evidence).map((row) => [row.id, row]));
  for (const rule of evidence) {
    const row = rows.get(rule.id);
    if (row?.holds !== true) continue;
    const found = evidenceHolds(ctx, rule, row);
    if (!found.ok) {
      ctx.logs.detail(`phase 5: evidence ${rule.id} was rejected`, found.why);
      continue;
    }
    for (const objective of named(rule)) {
      const target = decided.get(objective);
      if (target.applicable) continue;
      target.applicable = true;
      target.reason = rule.reason;
    }
  }
  return { applicable: pack.objectives.filter((row) => row.applicable).length };
}

// ---------------------------------------------------------------------------
// Phase 6, Reusable Test Design

/** Card objectives a document's cards may name. */
function cardObjectives(ctx) {
  if (ctx.job.suite) return ctx.suiteSetOrder;
  return ctx.pack.objectives.filter((row) => row.applicable).map((row) => row.objective);
}

const scenarioLine = (s) => `- ${s.id} | ${s.kind} | rules ${s.rules.join(', ')} | ${s.population} | ${s.action}`
  + ` | ${s.outcome}`;
const cardLine = (card) => `- ${card.title} | ${card.scenario} | rules ${card.rules.join(', ')}`;
const norm = (text) => String(text ?? '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();

/** What makes two scenarios, or two cards for them, the same test: kind, rules, who, and what is done. */
export const scenarioKey = (s) => [s.kind, [...new Set(s.rules)].sort().join(','), norm(s.population),
  norm(s.action)].join('|');

/** The kind of the scenario `id` names; null for a card with no scenario, which Phase 6 never leaves. */
const scenarioKind = (scenarios, id) => scenarios.find((s) => s.id === id)?.kind ?? null;

/**
 * The scenario ID after the highest of S1, S2 and so on that `scenarios` hold,
 * `ahead` more places on. A merge leaves gaps in the numbering.
 */
const nextScenarioId = (scenarios, ahead = 0) => `S${Math.max(0,
  ...scenarios.map((s) => Number(/^S(\d+)$/.exec(s.id)?.[1] ?? 0))) + ahead + 1}`;

/** The document text for a call: whole if it fits beside what the call already carries, else its digest. */
async function documentText(ctx, doc, refs, carried) {
  const budget = room(ctx, false, refs) - estimateTokens(carried + ctx.description) - 3000;
  // A document too long to send whole goes as its digest; the call's own size
  // check refuses anything that still does not fit.
  return estimateTokens(doc.text) <= budget ? doc.text : digestDocument(ctx, doc);
}

/** A retired rule the change concerns: its card verifies the removed behavior is gone. */
const removedBehavior = (rule) => rule.impact === 'Direct Change' && isRetired(rule);
const REMOVED_SCENARIO = ' A rule whose summary starts with "Retired:" was removed: list a scenario'
  + ' that checks its behavior is gone, one per control that triggered the removed behavior (one for'
  + ' Save, one for Save & Close), naming every retired rule it covers.';
const REMOVED_CARD = ' A rule whose summary starts with "Retired:" was removed: its card verifies'
  + ' the behavior is gone, and its expected result, final step included, says the behavior is'
  + ' absent, such as a warning and its buttons not appearing.';

/** True when the pack has a BREAK IT set that its cards can fill. */
const breakItOn = (ctx) => !ctx.job.suite && ctx.breakItObjective != null
  && cardObjectives(ctx).includes(ctx.breakItObjective);

/**
 * True when the card goes in the BREAK IT set: it is flagged `breakIt` and the
 * pack has that set. A flagged card in a pack without it sits with the plain cards.
 */
const breakItCard = (ctx, card) => card.breakIt === true && breakItOn(ctx);

// Rules go to the inventory a quarter of the room at a time; a reply lists at most one scenario per 150 tokens.
const INVENTORY_SHARE = 4;
const SCENARIO_TOKENS = 150;
// A scenario takes 190 to 230 tokens in the replies seen, against the 150 above, so the
// break-only call gets twice the tokens of the scenarios it may list.
const BREAK_ROOM = 2;

/**
 * The distinct scenarios a document's impacted rules call for. Rules that do
 * not fit one call go in batches, each shown the scenarios listed so far. Code
 * numbers the scenarios and drops any that repeats another's kind, rules,
 * population and action. With `only`, just that kind is asked for, `known` are the
 * scenarios already listed, and the call has an output limit of its own: one cut off at it
 * ends the pass with a `warn` line and an assumption, and the job goes on. With `only`
 * the reply may list no scenario.
 * `empty` holds each required kind with no scenario, and the reply's reason for it.
 */
async function scenarioInventory(ctx, doc, rules, { only, known = [] } = {}) {
  const refs = [...ctx.ref.core, ...ctx.ref.chapters('6')];
  const required = only ? [] : [...S.REQUIRED_SCENARIO_KINDS, ...(breakItOn(ctx) ? ['break'] : [])];
  // A break-only reply lists one scenario kind, so it holds one kind's share of the scenarios
  // a full reply holds, and the call gets BREAK_ROOM times the tokens that many scenarios take.
  const { maxOutput } = ctx.config.model;
  const kindShare = Math.max(SCENARIO_TOKENS, Math.floor(maxOutput / S.SCENARIO_KINDS.length));
  const maxItems = Math.max(1, Math.floor((only ? kindShare : maxOutput) / SCENARIO_TOKENS));
  const output = only ? Math.min(maxOutput, maxItems * SCENARIO_TOKENS * BREAK_ROOM) : maxOutput;
  const line = (rule) => `${ruleLine(rule)} | ${rule.impact} | risk ${rule.risk}`;
  const groups = batches(rules, line, Math.max(1000, Math.floor(room(ctx, false, refs) / INVENTORY_SHARE)));
  const seen = new Set(known.map(scenarioKey));
  const scenarios = [];
  const notes = [];
  const checks = new Map();
  let dropped = 0;
  let capped = false;
  let cutOff = false;
  for (const [i, group] of groups.entries()) {
    const lines = asLines(group.map(line));
    const listed = asLines([...known, ...scenarios].map(scenarioLine));
    const [impactLabel, impactText] = impactsInput(ctx, ctx.pack, false, refs);
    const answer = await ask(ctx, {
      phase: 'phase6', reasoning: false, refs, limit: only ? output : undefined,
      step: only ? `scenarios-d${doc.number}-${only}` : groups.length > 1
        ? `scenarios-d${doc.number}-${i + 1}` : `scenarios-d${doc.number}`,
      task: (only ? `List only the ${only} scenarios these rules and the document call for.`
        : 'List the distinct test scenarios these rules and the document call for.')
        + ' A scenario is one population (which records or users), one action, and the expected'
        + ' outcome, and it names the rules it checks. Where the document gives them, a population'
        + ' names the stage under test, how the tester reaches it (for example the left'
        + ' navigation), and the test data: which record, which child, with what values. Never'
        + ' invent a path or data the document does not give. '
        + (only ? 'A break scenario tries to break the change with bad input, a wrong order, a'
          + ' boundary or a repeated action.'
          : 'Cover each of these kinds wherever the document supports it, and mark every other'
          + ' scenario a decision: control is a population the change must not affect: the same'
          + ' action with no blocking condition (such as a downgrade with no special allegation),'
          + ' the plain save, and the adjacent paths the screen keeps, such as Reset restoring'
          + ' values and the buttons enabling again after a change; isolation is another record\'s'
          + ' state that must not leak into this one, and with several children or records the'
          + ' check applies to the selected one only; combined is conditions that overlap;'
          + ' persistence is closing and reopening the record; negative is a record or user the'
          + ' rule excludes, which must not get the behavior; role is another role or population'
          + ' for whom the outcome differs or must stay the same; state-change is a record that'
          + ' moves to another state over time and whose outcome follows the new state;'
          + ' manual-batch is the same change made by hand and by a batch or automatic process;'
          + ' navigation is leaving mid-task (back, cancel, timeout) and returning; re-entry is'
          + ' processing the same record again'
          + (required.includes('break') ? '; break tries to break the change with bad'
          + ' input, a wrong order, a boundary or a repeated action' : '') + '. In the kind checks,'
          + ' say for each of those kinds what its scenario tests, or why the document supports'
          + ' none.') + (group.some(removedBehavior) ? REMOVED_SCENARIO : '')
        + ' Never list a scenario already listed.',
      inputs: [['Change description', ctx.description], ['Document', doc.name], ['Rules', lines],
        ['Scenarios listed so far', listed], [impactLabel, impactText],
        ['Document text', await documentText(ctx, doc, refs, lines + listed + impactText)]],
      schema: S.scenarioInventorySchema({ ids: group.map((rule) => rule.id), maxItems, required,
        // A break-only pass may find no scenario to add.
        minItems: only ? 0 : 1, kinds: only ? [only] : S.SCENARIO_KINDS }),
    }).catch((error) => {
      // A break-only reply is optional: a cut ends the pass and the job goes on.
      if (!only || error.code !== 'length') throw error;
      return null;
    });
    if (!answer) {
      cutOff = true;
      ctx.logs.status({ job: ctx.job.id, phase: 'phase6', step: `scenarios-d${doc.number}-${only}`,
        event: 'warn', reason: 'break-pass-cut', maxTokens: output });
      break;
    }
    if (answer.scenarios.length >= maxItems) capped = true;
    for (const row of answer.scenarios) {
      const key = scenarioKey(row);
      if (seen.has(key)) {
        dropped += 1;
        continue;
      }
      seen.add(key);
      scenarios.push({ ...row, id: nextScenarioId([...known, ...scenarios]),
        rules: [...new Set(row.rules)] });
    }
    for (const check of answer.kindChecks ?? []) {
      checks.set(check.kind, [...(checks.get(check.kind) ?? []), check.note]);
    }
  }
  // The required kinds with no scenario, each with its reasons, for `emptyKindsNote`.
  const empty = required.filter((k) => !scenarios.some((s) => s.kind === k)).map((kind) => ({ kind,
    why: (checks.get(kind) ?? []).filter((note) => !blank(note)).map((note) => `${noStop(note)}.`).join(' ') }));
  if (capped) {
    notes.push({ assumption: `${doc.name}: the scenario list reached its limit of ${maxItems}.`,
      why: 'One reply holds only so many scenarios.', impact: 'Some scenarios may be missing.',
      clarification: 'Check the list against the document by hand.' });
  }
  if (cutOff) {
    notes.push({ assumption: `${doc.name}: the break scenario list was cut off at its output limit.`,
      why: 'The model\'s reply ran to its output limit without finishing.',
      impact: 'Break scenarios for this document may be missing, so '
        + `${ctx.breakItObjective} may have fewer cards or none.`,
      clarification: 'Write the break scenarios by hand.' });
  }
  return { scenarios, notes, dropped, empty };
}

/**
 * One assumption for the kinds a document's inventory left empty, each with its
 * reason; none when every kind has a scenario.
 */
function emptyKindsNote(docName, empty) {
  if (!empty.length) return null;
  if (empty.length === 1) {
    const [{ kind, why }] = empty;
    return { assumption: `${docName}: no ${kind} scenario was listed.`,
      why: blank(why) ? 'No reason was given.' : why,
      impact: `No card tests a ${kind} scenario for this document.`,
      clarification: 'Confirm the document supports none.' };
  }
  const kinds = empty.map(({ kind }) => kind).join(', ');
  return { assumption: `${docName}: no scenario was listed for these kinds: ${kinds}.`,
    why: empty.map(({ kind, why }) => `${kind}: ${blank(why) ? 'no reason was given.' : why}`).join(' '),
    impact: `No card tests these kinds of scenario for this document: ${kinds}.`,
    clarification: 'Confirm the document supports none of them.' };
}

/**
 * One card call. `focus` are the scenarios it is asked for; it may cover any
 * scenario in `open` (those with no card, reuse or skip yet), and no other.
 */
async function designBatch(ctx, doc, { focus, open, written }, objectives, index, extra = '',
  name = 'cards') {
  const refs = [...ctx.ref.core, ...ctx.ref.chapters('6'), ctx.ref.docs.operatingManual]
    .filter(Boolean);
  const byId = new Map(ctx.pack.rules.map((rule) => [rule.id, rule]));
  const group = [...new Set(open.flatMap((s) => s.rules))].map((id) => byId.get(id));
  const ids = group.map((rule) => rule.id);
  const lines = asLines(group.map((rule) => `${ruleLine(rule)} | ${rule.impact} | risk ${rule.risk}`));
  const scenarios = asLines(open.map(scenarioLine));
  const cards = asLines(written.map(cardLine));
  const existing = ctx.existingTests ?? '';
  const [impactLabel, impactText] = impactsInput(ctx, ctx.pack, false, refs);
  const docText = await documentText(ctx, doc, refs,
    [lines, scenarios, cards, existing, impactText].join('\n'));
  return ask(ctx, {
    phase: 'phase6', step: `${name}-d${doc.number}-${index}`, reasoning: false, refs,
    task: `Design reusable test cards for these scenarios: ${focus.map((s) => s.id).join(', ')}.`
      + ' Write one card per scenario, only for scenarios no card written so far covers, and name'
      + ' on each card the scenario it covers. Focus lists the tester\'s actions in order, one'
      + ' item per step, matching the steps. Focus items and steps are actions; expected'
      + ' results are observable business behavior. Every step that checks something has an'
      + ' observable expected result; only a setup step may leave it blank. A card\'s expected'
      + ' result is its final step\'s expected result, in the same words. Name on each card and each step only the'
      + ' rules it checks. Mark cards that come from quality thinking rather than a stated rule'
      + ' as Quality. A step that answers a message or resets belongs on the card that raises the'
      + ' message, and that card also checks the record did not save. Prefer reusing an existing'
      + ' test to writing a new card. A scenario an'
      + ' existing test already covers, or that no card can cover, is'
      + ' named in skipped with how (reused or gap) and the reason; reused names the test. A'
      + ` rule no card can cover goes in uncovered with its gap.`
      + ' Where the scenario\'s population gives them, step 1 opens the stage through its entry'
      + ' path and names the test record and its child data; never invent a path or data the'
      + ' document does not give.'
      + `${group.some(isRetired) ? REMOVED_CARD : ''}${extra}`,
    inputs: [['Change description', ctx.description], ['Document', doc.name],
      ['Scenarios', scenarios], ['Rules', lines], ['Cards written so far', cards],
      [impactLabel, impactText], ['Document text', docText], ['Existing tests', existing]],
    schema: S.cardsSchema({ ids, objectives, derivations: ctx.builder.DERIVATIONS,
      uncoveredStatuses: ['Partially Covered', 'Missing', 'Not Applicable'],
      scenarios: open.map((s) => s.id) }),
  });
}

/** A card with its rule lists cut to what the card may name, and every rule traced by a step. */
export function tidyCard(card, allowed) {
  const rules = [...new Set(card.rules.filter((id) => allowed.has(id)))];
  const steps = card.steps.map((step) => ({ ...step,
    rules: [...new Set(list(step.rules).filter((id) => rules.includes(id)))] }));
  const named = steps.flatMap((step) => step.rules);
  const unnamed = steps.some((step) => !step.rules.length);
  const untraced = rules.filter((id) => !named.includes(id));
  // A step naming no rule traces the rest; without one, the last step takes them.
  if (untraced.length && !unnamed && steps.length) {
    steps[steps.length - 1].rules.push(...untraced);
  }
  // A step before the last that checks nothing is a setup step; the builder wants a result on it.
  steps.forEach((step, i) => {
    if (i < steps.length - 1 && blank(step.expected)) step.expected = SETUP_EXPECTED;
  });
  return { ...card, rules, steps };
}

/** The result written on a setup step the model left blank. */
const SETUP_EXPECTED = 'The step completes with no error shown.';

/**
 * The sets a card sits in: the objectives it names, Full Coverage when it
 * comes from a requirement, and BREAK IT only when the card is a BREAK IT
 * type (`breakIt`, set from its scenario's kind). With `exclusiveSets`, a
 * BREAK IT card sits in no other set. A card left in no set takes the first
 * ordinary objective, else Full Coverage; with neither, it has no set.
 */
export function setsOf(ctx, card) {
  const { fullCoverageObjective: full, breakItObjective: brk } = ctx;
  const applicable = cardObjectives(ctx);
  const breakIt = breakItCard(ctx, card);
  if (breakIt && ctx.config.exclusiveSets) return [brk];
  // A BREAK IT card pushes past the ordinary case, so it stays out of the core set.
  const sets = list(card.objectives).filter((o) => applicable.includes(o) && o !== full && o !== brk
    && !(breakIt && o === ctx.coreObjective));
  if (full != null && applicable.includes(full) && card.derivation !== 'Quality') sets.push(full);
  if (breakIt) sets.push(brk);
  if (!sets.length) {
    const other = applicable.find((o) => o !== full && o !== brk)
      ?? (full != null && applicable.includes(full) ? full : null);
    return other == null ? [] : [other];
  }
  return [...new Set(sets)];
}

/** How a retired rule reads in a pack, as Phase 3 classes it and Phase 6 cards it. */
const RETIRED_RULE = 'A rule whose summary starts with "Retired:" was removed from the master and'
  + ' stays a retired rule whatever its class: its own Status, where the workbook shows one, reads'
  + ' Retired, and its coverage status is a separate column. It is a Direct Change when the change'
  + ' description concerns that removal, and the card for it verifies the behavior is gone, with an'
  + ' expected result that says the behavior is absent. A retired rule that is classed Direct Change'
  + ' and has a card whose expected result says the behavior is absent is consistent as it stands.';

/**
 * The rules the pipeline builds an issue pack by, as sentences a review or repair call is
 * given as fact, so no call faults the pack for following one: which cards the Full
 * Coverage set holds, where a BREAK IT card sits, how an objective no card serves reads,
 * and how a retired rule reads. The objective names come from the context. Each is stated
 * only when it holds for this pack: a set rule, or the clause of one, is left out when the
 * pack's sets do not follow it, as when a repair left a set its last card.
 * A suite pack takes its sets from the suite merge, so none is stated for it.
 */
export function designRules(ctx, pack) {
  if (ctx.job.suite) return [];
  const { fullCoverageObjective: full, breakItObjective: brk, coreObjective: core } = ctx;
  const applicable = cardObjectives(ctx);
  const hasFull = full != null && applicable.includes(full);
  const breakIt = breakItOn(ctx);
  const exclusive = breakIt && ctx.config.exclusiveSets === true;
  const held = (objective) => {
    const ids = list(list(pack.testSets).find((set) => set.objective === objective)?.cards);
    return list(pack.testCards).filter((card) => ids.includes(card.id));
  };
  const breakCards = breakIt ? held(brk) : [];
  const holdsBreakCard = (objective) => held(objective).some((card) => breakCards.includes(card));
  const rules = [];
  const inFull = hasFull ? held(full) : [];
  const fullAsRuled = list(pack.testCards).every((card) => (card.derivation === 'Quality'
    ? !inFull.includes(card) : inFull.includes(card) || (exclusive && breakCards.includes(card))));
  // With no ordinary objective, a quality-derived card no other set takes lands in Full Coverage.
  if (hasFull && applicable.some((o) => o !== full && o !== brk) && fullAsRuled) {
    rules.push(`The ${full} set, and the cards listed for the ${full} objective, hold only`
      + ` requirement-derived cards: every one of them${exclusive ? ` outside the ${brk} set` : ''}.`
      + ' A quality-derived card is left out of both by rule, so its absence there is correct.');
  }
  if (breakIt) {
    const alone = !list(pack.testSets).some((set) => set.objective !== brk && holdsBreakCard(set.objective));
    const others = exclusive
      ? (alone ? ` Such a card sits in no other set${hasFull ? `, the ${full} set included` : ''}.` : '')
      : applicable.includes(core) && core !== brk && !holdsBreakCard(core)
        ? ` Such a card stays out of the ${core} set.` : '';
    rules.push(`The ${brk} set holds only the cards written for break scenarios.${others}`);
  }
  const untested = untestedObjectives(ctx, pack);
  if (untested.length) {
    rules.push(`No test card serves ${untested.join(', ')}, so`
      + ` ${untested.length > 1 ? 'those objectives read' : 'that objective reads'} Not Applicable, with`
      + ' a reason that says no test card serves it. That row is how the pack records the gap, by rule:'
      + ' such an objective applies to the change, no card tests it, a repair cannot change the row,'
      + ' and the workbook need not show a limitation for it.');
  }
  if (list(pack.rules).some(isRetired)) rules.push(RETIRED_RULE);
  return rules;
}

/** The input a call reads the design rules under. */
const DESIGN_RULES_LABEL = 'How this pack is built';

/** The design rules as an input of a call, under `lead`; blank, so left out, when the pack has none. */
const designRulesInput = (ctx, pack, lead) => {
  const rules = designRules(ctx, pack);
  return [DESIGN_RULES_LABEL, rules.length ? `${lead}\n${asLines(rules.map((rule) => `- ${rule}`))}` : ''];
};

// The reason a dropped objective carries. It replaces the reason that argued for testing it, and it
// stays clear of the phrases the quality check reads as "this could be tested".
const DROPPED = 'Not tested in this pack: no test card serves it. The gap is recorded under Limitations.';

/** The objectives dropped for want of a card. A checkpoint from an older run holds a count instead. */
const droppedList = (ctx) => (Array.isArray(ctx.droppedObjectives) ? ctx.droppedObjectives : []);
/** The dropped objectives the pack shows as not applicable: each is applicable, and no card tests it. */
const untestedObjectives = (ctx, pack) => droppedList(ctx).filter((name) => list(pack.objectives)
  .some((row) => row.objective === name && !row.applicable));
const noStop = (text) => String(text).replace(/[.\s]+$/, '');

const docRules = (ctx, doc) => ctx.pack.rules.filter((rule) => rule.sourceDocument === doc.name
  && rule.module === doc.module && rule.impact !== 'Not Impacted');

/**
 * One document's scenarios, then its cards, one batch of scenarios at a time.
 * Given its earlier `designed` and `only`, it adds scenarios of that kind.
 * A scenario is settled by a card, by a skip saying an existing test covers it,
 * or by a skip saying no card can; each records how in its `settled`. `empty`
 * holds the required kinds the inventory listed no scenario for.
 */
async function designDocument(ctx, doc, rules, objectives, { designed, only } = {}) {
  const state = designed
    ?? { cards: [], uncovered: [], reuse: [], assumptions: [], scenarios: [] };
  const count = { retried: 0, duplicates: 0, unsettled: 0 };
  if (!rules.length) return { designed: state, empty: [], ...count };
  const inventory = await scenarioInventory(ctx, doc, rules, { only, known: state.scenarios });
  // Absence checks of retired rules are not break cases and merge by the control they press.
  const retiredIds = new Set(ctx.pack.rules.filter(isRetired).map((rule) => rule.id));
  const joined = mergeRemovedScenarios(inventory.scenarios, retiredIds, docControls(doc, ctx.pack.rules));
  const mine = joined.scenarios;
  count.duplicates += joined.merged.length;
  state.scenarios.push(...mine);
  state.assumptions.push(...inventory.notes);
  count.duplicates += inventory.dropped;
  const byScenario = new Map(mine.map((s) => [s.id, s]));
  const seen = new Set(state.cards.map((card) => card.key));
  const settled = (s) => Boolean(s.settled);
  const take = async (focus, index, extra) => {
    const open = mine.filter((s) => !settled(s));
    const answer = await designBatch(ctx, doc, { focus, open, written: state.cards },
      objectives, index, extra);
    const openIds = new Set(open.map((s) => s.id));
    for (const card of answer.cards) {
      const scenario = byScenario.get(card.scenario);
      if (!scenario || !openIds.has(scenario.id)) continue;
      const tidy = tidyCard(card, new Set(scenario.rules));
      if (!tidy.rules.length) continue;
      const key = scenarioKey(scenario);
      if (seen.has(key)) {
        count.duplicates += 1;
        continue;
      }
      seen.add(key);
      state.cards.push({ ...tidy, key, breakIt: scenario.kind === 'break'
        && !scenario.rules.every((id) => retiredIds.has(id)) });
      scenario.settled ??= { how: 'card' };
    }
    for (const skip of answer.skipped ?? []) {
      const scenario = byScenario.get(skip.scenario);
      if (scenario && openIds.has(scenario.id)) {
        scenario.settled ??= { how: skip.how, reason: skip.reason };
      }
    }
    state.uncovered.push(...answer.uncovered);
    state.reuse.push(...answer.reuse);
    state.assumptions.push(...withoutPipelineTerms(ctx, answer.assumptions));
  };
  const perCall = ctx.config.cardScenariosPerCall ?? 4;
  for (const [i, group] of batches(mine, scenarioLine, 20000, perCall).entries()) {
    const todo = group.filter((s) => !settled(s));
    if (!todo.length) continue;
    await take(todo, only ? `${only}-${i + 1}` : i + 1);
    const left = todo.filter((s) => !settled(s));
    if (!left.length) continue;
    // One more try, told which scenarios it left with no card, reuse entry or skip.
    count.retried += 1;
    await take(left, only ? `${only}-${i + 1}b` : `${i + 1}b`,
      ' Every scenario listed needs a card or a skipped entry.');
  }
  // Every impacted rule is tested by a card. One no card cites and no scenario names, whatever the
  // inventory listed, gets a scenario of its own; a retired rule's card verifies its behavior is gone.
  const cited = () => new Set(state.cards.flatMap((card) => card.rules));
  // A scenario settled by a card that does not cite the rule leaves the rule owed a scenario.
  const named = () => new Set(state.scenarios.filter((s) => s.settled?.how !== 'card')
    .flatMap((s) => s.rules));
  const owed = only ? [] : rules.filter((rule) => !cited().has(rule.id) && !named().has(rule.id));
  if (owed.length) {
    const made = owed.map((rule, i) => ({ id: nextScenarioId(state.scenarios, i), kind: 'decision',
      rules: [rule.id], ...(isRetired(rule)
        ? { population: 'a record the removed behavior used to apply to',
          action: `check that the behavior of ${rule.id} is gone`,
          outcome: 'The removed behavior is absent' }
        : { population: 'a record the rule applies to',
          action: `check that ${rule.id} holds as its summary states`,
          outcome: 'The record behaves as the rule states' }) }));
    state.scenarios.push(...made);
    mine.push(...made);
    for (const s of made) byScenario.set(s.id, s);
    for (const [i, group] of batches(made, scenarioLine, 20000, perCall).entries()) {
      const todo = group.filter((s) => !settled(s));
      if (!todo.length) continue;
      await take(todo, `rule-${i + 1}`);
      const left = todo.filter((s) => !settled(s));
      if (!left.length) continue;
      count.retried += 1;
      await take(left, `rule-${i + 1}b`, ' Every scenario listed needs a card or a skipped entry.');
    }
  }
  for (const s of mine.filter((x) => !settled(x))) {
    count.unsettled += 1;
    state.assumptions.push({
      assumption: `No test card covers scenario ${s.id}: ${s.population}; ${s.action}.`,
      why: 'The local design pass wrote no card and no skipped entry for it after a second try.',
      impact: `Rules ${s.rules.join(', ')} are not tested for this scenario.`,
      clarification: 'Design a card for this scenario by hand.' });
  }
  // Rule rows: none for a rule a card covers, one for any other. A rule only an
  // existing test covers reads Missing and points at that test.
  const covered = new Set(state.cards.flatMap((card) => card.rules));
  const rows = new Map();
  for (const row of state.uncovered) {
    if (!covered.has(row.ruleId) && !rows.has(row.ruleId)) rows.set(row.ruleId, row);
  }
  for (const rule of rules.filter((r) => !covered.has(r.id) && !rows.has(r.id))) {
    const named = state.scenarios.filter((s) => s.rules.includes(rule.id));
    const reused = named.find((s) => s.settled?.how === 'reused');
    const skipped = named.find((s) => s.settled?.how === 'gap');
    rows.set(rule.id, reused ? reuseRow(rule.id, reused.settled.reason)
      : { ruleId: rule.id, status: 'Missing',
        gap: skipped ? `No card can cover this rule: ${noStop(skipped.settled.reason)}.`
          : 'The local design pass wrote no card for this rule.',
        recommendation: 'Design a card for this rule by hand.' });
  }
  state.uncovered = [...rows.values()];
  return { designed: state, empty: inventory.empty, ...count };
}

// Words that reverse or narrow a result. Extra words like these on one side of a
// containment make it a different result: "saved" is not "not saved".
const REVERSING = new Set(['no', 'not', 'never', 'cannot', 'without', 'none', 'nothing', 'unless',
  'until', 'only', 'except']);
// A negated contraction, which `norm` splits into "isn t".
const contractions = (text) => (text.match(/n t(?= |$)/g) ?? []).length;

/**
 * Whether a card's Expected Result and its final step's say the same: equal
 * once case and punctuation are set aside, or one holds the other whole words
 * and all with no word of the longer side that negates or conditions it
 * (no, not, never, cannot, without, none, nothing, n't, unless, until, only,
 * except). Anything else is a mismatch, and so is a blank on either side.
 */
export function resultsAgree(card) {
  const last = list(card.steps).at(-1);
  if (!last) return true;
  const [a, b] = [norm(card.expected), norm(last.expected)];
  if (!a || !b) return false;
  if (a === b) return true;
  const [short, long] = a.length <= b.length ? [a, b] : [b, a];
  if (!` ${long} `.includes(` ${short} `)) return false;
  const extra = long.split(' ');
  for (const word of short.split(' ')) extra.splice(extra.indexOf(word), 1);
  return !extra.some((word) => REVERSING.has(word)) && contractions(long) === contractions(short);
}

/** The cards whose Expected Result disagrees with their final step's, one line each. */
export const expectedProblems = (pack) => list(pack.testCards).filter((card) => !resultsAgree(card))
  .map((card) => `${card.id} Expected Result "${noStop(card.expected ?? '')}" does not agree with`
    + ` its final step's "${noStop(list(card.steps).at(-1).expected ?? '')}". Keep the card's`
    + ' Expected Result and change that step\'s expected result to say the same.');

// The sheet name a mismatch is reported under; the builder has no such sheet.
const EXPECTED_SHEET = 'Test Card Expected Results';

const VERIFY_CARDS = 8;
const VERIFY_RULE = 'precedence: when two rules conflict, a rule that blocks an action outranks one that'
  + ' allows it, so the action stays blocked, unless a cited rule says it is an exception to the block'
  + ' or overrides it; Reset restores the saved value, never the edited one.';

const NO_QUALITY = 'No card in this pack is quality-derived.';
const QUALITY_VERIFY = ' A card marked Quality tests behavior beyond the stated rules: it follows'
  + ' (this replaces the test for a result no cited rule supports) unless its Expected Result contradicts a cited rule, rests on an allowance that a block'
  + ' overrides, or restores a value other than the saved one. Never answer "does not follow" for'
  + ' a Quality card only because no cited rule states its result; say in the reason which rule it'
  + ' contradicts.';

/** A rule's source wording: its summary, and the master's full description when that adds to it. */
function ruleWording(ctx, rule, short) {
  const raw = short ? null : ctx.documents.flatMap((doc) => list(doc.rules))
    .find((row) => (row.rule_id ?? row.id) === rule.id);
  const parts = [rule.summary, raw?.description].filter((text) => !blank(text));
  if (isRetired(rule)) parts.unshift('removed: the card must show this no longer happens');
  return [...new Set(parts)].join(' / ');
}

const cardView = (card) => [`Title: ${card.title}`, `Derivation: ${card.derivation}`,
  `Expected Result: ${card.expected}`,
  ...list(card.steps).map((step, i) => `Step ${i + 1}: ${step.description} => ${step.expected}`
    + ` (rules ${list(step.rules).join(', ')})`)].join('\n');

/**
 * Asks, per card, whether its Expected Result follows from the rules it cites
 * as their source wording states them. Cards go in batches that fit the
 * room. A batch that is too big is split; a card too big alone is asked again
 * with rule summaries only, and if that is too big too it is left unverified.
 * Returns `failed` (the reason for each card that does not follow, by card)
 * and `unverified` (the cards no call could hold). `extra` is a sentence added to
 * what every call of this check is asked.
 */
async function verifyCards(ctx, cards, step, extra = '') {
  const failed = new Map();
  const unverified = [];
  if (!cards.length) return { failed, unverified };
  const refs = [...ctx.ref.core, ...ctx.ref.chapters('6')];
  const byId = new Map(ctx.pack.rules.map((rule) => [rule.id, rule]));
  const wording = (card, short) => list(card.rules).map((id) => byId.get(id)).filter(Boolean)
    .map((rule) => `- ${rule.id} | ${rule.name} | page ${rule.sourcePage}: ${ruleWording(ctx, rule, short)}`);
  const cost = (card) => `${cardView(card)}\n${asLines(wording(card))}`;
  const run = async (group, name, short) => {
    const labeled = group.map((card, n) => ({ card, label: `C${n + 1}` }));
    let answer;
    try {
      answer = await ask(ctx, {
        phase: 'phase6', step: name, reasoning: false, refs,
        task: 'For each card, decide whether its Expected Result follows from the rules the card'
          + ' cites, read as their source wording states them, and from nothing else. Apply this'
          + ` ${VERIFY_RULE} Answer "does not follow" when the Expected Result contradicts a rule,`
          + ' rests on an allowance that a block overrides, restores a value other than the saved one,'
          + ' or states what no cited rule supports; say in the reason what the rules require instead.'
          + ' A rule marked removed was taken out: a card citing it follows when its Expected Result'
          + ' states the behavior is absent, and does not follow when it expects the behavior.'
          + (group.some((card) => card.derivation === 'Quality') ? QUALITY_VERIFY : '') + extra,
        inputs: [['Cards', labeled.map(({ card, label }) => `### ${label}\n${cardView(card)}`).join('\n\n')],
          ['Rules and their source wording',
            asLines([...new Set(group.flatMap((card) => wording(card, short)))])]],
        schema: S.verificationSchema(labeled.map((row) => row.label)),
      });
    } catch (error) {
      if (!(error instanceof ModelError) || error.code !== 'too-big') throw error;
      if (group.length > 1) {
        ctx.logs.status({ job: ctx.job.id, phase: 'phase6', step: name, event: 'split', cards: group.length });
        for (const [n, card] of group.entries()) await run([card], `${name}s${n + 1}`, short);
      } else if (!short) await run(group, `${name}short`, true);
      else unverified.push(group[0]);
      return;
    }
    const verdicts = new Map(answer.cards.map((row) => [row.card, row]));
    for (const { card, label } of labeled) {
      const row = verdicts.get(label);
      if (row?.verdict === 'does not follow') failed.set(card, row.why);
    }
  };
  for (const [i, group] of batches(cards, cost, room(ctx, false, refs) - 1500, VERIFY_CARDS).entries()) {
    await run(group, `${step}-${i + 1}`, false);
  }
  return { failed, unverified };
}

const reuseRow = (ruleId, reason) => ({ ruleId, status: 'Missing',
  gap: `Covered only by the existing test ${noStop(reason)}; confirm it and reuse it.`,
  recommendation: 'Confirm the existing test covers this rule and reuse it, or design a card.' });

/**
 * Takes a card out of a document's design. Its scenario is settled as removed,
 * or by the `skip` a redesign answered with. An assumption says why, and each
 * of its rules no other card covers gets a Missing row: the existing reuse row
 * when an existing test covers it, else one with the reason.
 */
function removeCard(state, card, why, skip) {
  state.cards = state.cards.filter((c) => c !== card);
  const scenario = state.scenarios.find((s) => s.id === card.scenario);
  const given = skip && !blank(skip.reason) ? skip.reason : why;
  if (scenario) scenario.settled = skip ? { how: skip.how, reason: given } : { how: 'removed', reason: why };
  const reason = noStop(blank(given) ? 'its Expected Result does not follow from the rules' : given);
  state.assumptions.push({
    assumption: `The card "${card.title}" was removed${scenario ? ` for scenario ${scenario.id}` : ''}:`
      + (skip ? ' its Expected Result did not follow from its rules, and the redesign wrote no card for it.'
        : ' its Expected Result did not follow from its rules after one redesign.'),
    why: `${reason}.`, impact: `Rules ${card.rules.join(', ')} lose this card.`,
    clarification: 'Design a card for them by hand, checking its Expected Result against the rules.' });
  const covered = new Set(state.cards.flatMap((c) => c.rules));
  const lost = card.rules.filter((id) => !covered.has(id));
  const rowFor = (ruleId) => {
    const reused = state.scenarios.find((s) => s.settled?.how === 'reused' && s.rules.includes(ruleId));
    const kept = state.uncovered.find((row) => row.ruleId === ruleId);
    if (reused) return kept ?? reuseRow(ruleId, reused.settled.reason);
    return { ruleId, status: 'Missing',
      gap: skip?.how === 'gap' ? `No card can cover this rule: ${reason}.`
        : `The card for this rule was removed: ${reason}.`,
      recommendation: 'Design a card for this rule by hand, checking its Expected Result against the rules.' };
  };
  state.uncovered = [...state.uncovered.filter((row) => !lost.includes(row.ruleId)), ...lost.map(rowFor)];
}

/**
 * Verifies the cards of a document that are not yet `verified`. A card that
 * does not follow is designed again once, told why, and verified again; if it still fails, or no
 * card comes back, it is removed. A card no call could hold is kept with an
 * assumption saying it was not verified. Returns the counts.
 */
async function verifyDocument(ctx, doc, objectives, verified, tag = '') {
  const count = { redesigned: 0, removed: 0 };
  const state = ctx.designed[doc.key];
  const pending = state.cards.filter((card) => !verified.has(card));
  const note = (card) => {
    verified.add(card);
    state.assumptions.push({
      assumption: `The card "${card.title}" was not checked against its rules.`,
      why: 'Its steps and rules are too large for one verification call.',
      impact: `Its Expected Result for rules ${card.rules.join(', ')} is unchecked.`,
      clarification: 'Check its Expected Result against the rules by hand.' });
  };
  // A card that follows its rules but whose final step words the result differently has
  // its final step set to the card's Expected Result; only a card that does not follow is redone.
  const align = (card) => {
    const last = list(card.steps).at(-1);
    if (last && !resultsAgree(card)) last.expected = card.expected;
  };
  const first = await verifyCards(ctx, pending, `verify-d${doc.number}${tag}`);
  first.unverified.forEach(note);
  for (const card of pending) {
    if (first.failed.has(card)) continue;
    verified.add(card);
    if (!first.unverified.includes(card)) align(card);
  }
  const byId = new Map(ctx.pack.rules.map((rule) => [rule.id, rule]));
  const redone = [];
  for (const [card, why] of first.failed) {
    const scenario = state.scenarios.find((s) => s.id === card.scenario);
    if (!scenario) {
      removeCard(state, card, why);
      count.removed += 1;
      continue;
    }
    count.redesigned += 1;
    const quality = card.derivation === 'Quality';
    const others = state.cards.filter((c) => c !== card);
    const answer = await designBatch(ctx, doc, { focus: [scenario], open: [scenario], written: others },
      objectives, scenario.id,
      ` An earlier card for scenario ${scenario.id} was rejected because its Expected Result does`
      + ` not ${quality ? 'agree with' : 'follow from'} its rules: ${noStop(why)}. Its Expected Result was "${noStop(card.expected)}". Write the card again for`
      + ` ${scenario.id} only${quality ? ' as a Quality card' : ''}, with an Expected Result that`
      + ` ${quality ? 'does not contradict' : 'follows from'} the rules, repeated`
      + ` as the final step's expected result, applying this ${VERIFY_RULE}`, 'redo');
    const fresh = answer.cards.find((c) => c.scenario === scenario.id);
    const tidy = fresh && tidyCard(fresh, new Set(scenario.rules.filter((id) => byId.has(id))));
    if (!tidy?.rules.length) {
      const skip = (answer.skipped ?? []).find((row) => row.scenario === scenario.id);
      removeCard(state, card, why, skip);
      count.removed += 1;
      continue;
    }
    const next = { ...tidy, key: card.key, breakIt: card.breakIt,
      ...(quality ? { derivation: 'Quality' } : {}) };
    state.cards[state.cards.indexOf(card)] = next;
    redone.push([card, next, why]);
  }
  const again = await verifyCards(ctx, redone.map(([, next]) => next), `reverify-d${doc.number}${tag}`);
  again.unverified.forEach(note);
  for (const [, next, why] of redone) {
    if (again.failed.has(next)) {
      removeCard(state, next, again.failed.get(next) || why);
      count.removed += 1;
    } else {
      verified.add(next);
      if (!again.unverified.includes(next)) align(next);
    }
  }
  return count;
}

/**
 * Tidies a document's cards before they are verified: a card that only answers
 * a message joins the card that raises it, and a card that repeats another is
 * dropped (see design-tidy.mjs). A card whose steps or rules changed is taken
 * out of `verified` so it is checked again. Returns the counts.
 */
export function tidyDocument(ctx, doc, verified, checked = new Set()) {
  const state = ctx.designed[doc.key];
  const count = { folded: 0, repeats: 0 };
  const scenarioOf = (card) => state.scenarios.find((s) => s.id === card.scenario);
  const settle = (card, why) => {
    const scenario = scenarioOf(card);
    if (scenario) scenario.settled = { how: 'card', reason: why };
  };
  // Rules a card takes from another also join its scenario, so a redesign keeps them.
  const takeRules = (card, other) => {
    const scenario = scenarioOf(card);
    if (scenario) scenario.rules = [...new Set([...scenario.rules, ...other.rules])];
    // The sets the other card served stay served.
    card.objectives = [...new Set([...list(card.objectives), ...list(other.objectives)])];
    verified.delete(card);
    checked.delete(card);
  };
  // A BREAK IT card and a plain card go in different sets, so neither joins nor repeats the other.
  const isBreak = (card) => breakItCard(ctx, card);
  const fold = foldFollowUps(state.cards, isBreak);
  state.cards = fold.cards;
  for (const { into, from } of fold.folded) {
    count.folded += 1;
    takeRules(into, from);
    settle(from, `its steps are on "${into.title}"`);
    state.assumptions.push({
      assumption: `The card "${from.title}" was joined to the card "${into.title}".`,
      why: 'Its steps only answer or reset the message that card raises.',
      impact: `Rules ${from.rules.join(', ')} are checked by the joined card.`,
      clarification: 'Split them again if they need to run apart.' });
  }
  const drop = dropRepeats(state.cards, doc, docRules(ctx, doc), isBreak);
  state.cards = drop.cards;
  for (const { kept, dropped } of drop.dropped) {
    count.repeats += 1;
    takeRules(kept, dropped);
    settle(dropped, `it repeats "${kept.title}"`);
    state.assumptions.push({
      assumption: `The card "${dropped.title}" was dropped as a repeat of the card "${kept.title}".`,
      why: 'Both do the same thing to the same kind of record.',
      impact: `Rules ${dropped.rules.join(', ')} are checked by the card that stays.`,
      clarification: 'Confirm the two do not test different populations.' });
  }
  return count;
}

const STEP_CARDS = 8;

/**
 * Asks, per card, whether each step can be done under the rules in force: the
 * rules the card cites plus the rules that govern a control its steps press.
 * Returns the cards with a step that cannot, each with { step, why } rows.
 */
async function flaggedSteps(ctx, doc, cards, step, tooBig = []) {
  const flagged = new Map();
  if (!cards.length) return flagged;
  const refs = [...ctx.ref.core, ...ctx.ref.chapters('6')];
  const controls = docControls(doc, ctx.pack.rules);
  const wording = (card) => stepRules(card, ctx.pack.rules, controls)
    .map((rule) => `- ${rule.id} | ${rule.name} | page ${rule.sourcePage}: ${ruleWording(ctx, rule, false)}`);
  const cost = (card) => `${stepsView(card)}\n${asLines(wording(card))}`;
  const run = async (group, name) => {
    const labeled = group.map((card, n) => ({ card, label: `C${n + 1}` }));
    let answer;
    try {
      answer = await ask(ctx, {
        phase: 'phase6', step: name, reasoning: false, refs, task: STEP_QUESTION,
        inputs: [['Cards', labeled.map(({ card, label }) => `### ${label}\n${stepsView(card)}`).join('\n\n')],
          ['Rules and their source wording', asLines([...new Set(group.flatMap(wording))])]],
        schema: stepSchema(labeled.map((row) => row.label)),
      });
    } catch (error) {
      if (!(error instanceof ModelError) || error.code !== 'too-big') throw error;
      if (group.length > 1) for (const [n, card] of group.entries()) await run([card], `${name}s${n + 1}`);
      else tooBig.push(group[0]);
      return;
    }
    const rows = new Map(answer.cards.map((row) => [row.card, row]));
    for (const { card, label } of labeled) {
      const problems = impossibleSteps(rows.get(label));
      if (problems.length) flagged.set(card, problems);
    }
  };
  for (const [i, group] of batches(cards, cost, room(ctx, false, refs) - 1500, STEP_CARDS).entries()) {
    await run(group, `${step}-${i + 1}`);
  }
  return flagged;
}

/**
 * Checks that every step of the document's cards can be done under the rules.
 * A card with a step that cannot is designed again once, told which step and
 * why; a card still flagged is kept, with an assumption that names the step.
 */
async function checkSteps(ctx, doc, objectives, checked, tag = '') {
  const count = { stepsFlagged: 0 };
  const state = ctx.designed[doc.key];
  const byId = new Map(ctx.pack.rules.map((rule) => [rule.id, rule]));
  const keep = (card, problems) => {
    for (const { step, why } of problems) {
      state.assumptions.push({
        assumption: `Step ${step} of the card "${card.title}" may not be possible under its rules.`,
        why: noStop(blank(why) ? 'A rule it cites blocks it' : why) + '.',
        impact: 'A tester may be unable to run the card as written.',
        clarification: 'Confirm the rules allow the step, and raise any conflict between rules.' });
    }
  };
  const tooBig = [];
  const first = await flaggedSteps(ctx, doc, state.cards.filter((card) => !checked.has(card)),
    `steps-d${doc.number}${tag}`, tooBig);
  for (const card of tooBig) {
    state.assumptions.push({
      assumption: `The steps of the card "${card.title}" were not checked against the rules.`,
      why: 'Its steps and the rules that govern them are too large for one call.',
      impact: 'A step may not be possible under the rules.',
      clarification: 'Check each step against the rules by hand.' });
  }
  const redone = [];
  for (const [card, problems] of first) {
    count.stepsFlagged += 1;
    const scenario = state.scenarios.find((s) => s.id === card.scenario);
    if (!scenario) {
      keep(card, problems);
      continue;
    }
    const said = problems.map(({ step, why }) => `step ${step}: ${noStop(why)}`).join('; ');
    const answer = await designBatch(ctx, doc, { focus: [scenario], open: [scenario],
      written: state.cards.filter((c) => c !== card) }, objectives, scenario.id,
      ` An earlier card for scenario ${scenario.id} had a step the rules do not allow (${said}).`
      + ` Write the card again for ${scenario.id} only, so every step can be done under the rules.`
      + ' When two rules conflict, follow the one that blocks the action and say so in an assumption.',
      'stepfix');
    const fresh = answer.cards.find((c) => c.scenario === scenario.id);
    const tidy = fresh && tidyCard(fresh, new Set(scenario.rules.filter((id) => byId.has(id))));
    if (!tidy?.rules.length) {
      keep(card, problems);
      continue;
    }
    const next = { ...tidy, key: card.key, breakIt: card.breakIt };
    state.cards[state.cards.indexOf(card)] = next;
    state.assumptions.push(...withoutPipelineTerms(ctx, answer.assumptions));
    redone.push([card, next, problems]);
  }
  const again = await flaggedSteps(ctx, doc, redone.map(([, next]) => next), `restep-d${doc.number}${tag}`);
  for (const [, next] of redone) if (again.has(next)) keep(next, again.get(next));
  for (const card of state.cards) checked.add(card);
  return count;
}

export async function phase6(ctx) {
  const { pack, job } = ctx;
  const objectives = cardObjectives(ctx);
  if (!objectives.length) throw new GateError('phase6', 'no-applicable-objective');
  ctx.designed = {};
  ctx.logs.detail('phase6 inputs', `methodology chapters ${(ctx.config.reference.methodology
    ?.byPhase?.['6'] ?? []).join(', ') || 'none'}; operating manual: ${ctx.ref.docs.operatingManual
    ? 'yes' : 'no'}; existing tests: ${ctx.existingTests
    ? `${estimateTokens(ctx.existingTests)} tokens` : 'none'}; impacts: ${ctx.pack.impacts
    ? 'yes' : 'none recorded'}`);
  const total = { retried: 0, duplicates: 0, unsettled: 0, scenarios: 0, redesigned: 0, removed: 0,
    folded: 0, repeats: 0, stepsFlagged: 0 };
  const add = (done) => {
    for (const key of ['retried', 'duplicates', 'unsettled', 'redesigned', 'removed', 'folded',
      'repeats', 'stepsFlagged']) {
      total[key] += done[key] ?? 0;
    }
  };
  // Cards whose Expected Result has been checked against their rules. A card is
  // checked before the objective passes below, so a removal never leaves an
  // objective served by a card that is gone.
  const verified = new Set();
  // Cards whose steps have been checked against the rules.
  const checked = new Set();
  // Tidies a document's cards, then verifies and step-checks the ones not yet checked.
  const settle = async (doc, tag) => {
    for (let pass = 0; pass < 3; pass += 1) {
      const tidied = tidyDocument(ctx, doc, verified, checked);
      add(tidied);
      if (!tidied.folded && !tidied.repeats) break;
    }
    add(await verifyDocument(ctx, doc, objectives, verified, tag));
    add(await checkSteps(ctx, doc, objectives, checked, tag));
    add(await verifyDocument(ctx, doc, objectives, verified, `${tag}-steps`));
  };
  // The required kinds each document's inventory left empty.
  const emptyKinds = new Map();
  for (const doc of ctx.documents.filter((d) => d.inclusion === 'Included')) {
    const done = await designDocument(ctx, doc, docRules(ctx, doc), objectives);
    ctx.designed[doc.key] = done.designed;
    emptyKinds.set(doc.key, done.empty);
    add(done);
    await settle(doc, '');
  }

  if (!job.suite) {
    const drop = (objective) => {
      // No card could serve it, so the decision cannot stand as Applicable.
      const row = pack.objectives.find((r) => r.objective === objective);
      row.applicable = false;
      row.reason = DROPPED;
      ctx.droppedObjectives = [...new Set([...droppedList(ctx), objective])];
    };
    const allCards = () => Object.values(ctx.designed).flatMap((d) => d.cards);
    // An applicable objective no card serves gets one targeted pass.
    for (const [n, objective] of objectives.entries()) {
      const served = () => allCards().some((card) => setsOf(ctx, card).includes(objective));
      if (served()) continue;
      if (objective === ctx.fullCoverageObjective) {
        // It holds every requirement card, so none being there leaves it empty.
        drop(objective);
      } else if (objective === ctx.breakItObjective) {
        // New break scenarios, each with one card, in the first document that has scenarios.
        const doc = ctx.documents.find((d) => ctx.designed[d.key]?.scenarios.length);
        if (doc) {
          const done = await designDocument(ctx, doc, docRules(ctx, doc), objectives,
            { designed: ctx.designed[doc.key], only: 'break' });
          add(done);
          await settle(doc, '-break');
        }
        if (!served()) drop(objective);
      } else {
        // Ask which of the cards already written serve it; none new is written.
        // A card in the BREAK IT set stays out of the core set, so it cannot be named for it. A flagged
        // card in a pack with no BREAK IT set is a plain card.
        const pool = allCards().filter((card) => !(objective === ctx.coreObjective && breakItCard(ctx, card)));
        const refs = pool.map((card, i) => ({ card, ref: `C${i + 1}` }));
        const answer = refs.length ? await ask(ctx, {
          phase: 'phase6', step: `objective-${n + 1}`, reasoning: false,
          refs: [...ctx.ref.core, ...ctx.ref.chapters('6')],
          task: `Name the cards that serve the objective ${objective}. Name none if no card does.`,
          inputs: [['Change description', ctx.description], ['Objective', objective],
            ['Cards', asLines(refs.map(({ card, ref }) => `- ${ref} | ${card.title} | `
              + `${list(card.focus).join('; ')} | ${list(card.objectives).join(', ')}`))]],
          schema: S.objectiveCardsSchema(refs.map((r) => r.ref)),
        }) : { cards: [] };
        const named = new Set(answer.cards);
        for (const { card, ref } of refs) {
          if (named.has(ref)) card.objectives = [...new Set([...list(card.objectives), objective])];
        }
        if (!served()) drop(objective);
      }
    }
  }
  // One note per document for the kinds its inventory left empty. A kind a later pass listed, such as
  // break, is left out, whether or not a card serves its objective.
  for (const doc of ctx.documents.filter((d) => emptyKinds.has(d.key))) {
    const state = ctx.designed[doc.key];
    const note = emptyKindsNote(doc.name, emptyKinds.get(doc.key)
      .filter(({ kind }) => !state.scenarios.some((s) => s.kind === kind)));
    if (note) state.assumptions.unshift(note);
  }
  // A redesign can bring a repeat back; tidy and check once more, then refuse any that stands.
  for (const doc of ctx.documents.filter((d) => d.inclusion === 'Included' && ctx.designed[d.key])) {
    // A redesign in one round can bring a card no check has seen, so settle again, a few rounds at most.
    // The tidy that ends a round can change a card, which the next round checks.
    for (let round = 0; round < 3; round += 1) {
      await settle(doc, '-final');
      const tidied = tidyDocument(ctx, doc, verified, checked);
      add(tidied);
      if (!tidied.folded && !tidied.repeats
        && ctx.designed[doc.key].cards.every((card) => verified.has(card) && checked.has(card))) break;
    }
    // A card the rounds ran out on is kept, and says it was not fully checked.
    for (const card of ctx.designed[doc.key].cards) {
      if (verified.has(card) && checked.has(card)) continue;
      ctx.designed[doc.key].assumptions.push({
        assumption: `The card "${card.title}" was not fully checked after its last change.`,
        why: 'The design passes ran out of rounds while it kept changing.',
        impact: `Its Expected Result and steps for rules ${card.rules.join(', ')} are unchecked.`,
        clarification: 'Check its Expected Result and steps against the rules by hand.' });
    }
    const left = repeatsLeft(ctx.designed[doc.key].cards, doc, docRules(ctx, doc),
      (card) => breakItCard(ctx, card));
    if (left > 0) throw new GateError('phase6', 'repeated-cards', { repeats: left });
  }
  const cards = Object.values(ctx.designed).reduce((n, d) => n + d.cards.length, 0);
  total.scenarios = Object.values(ctx.designed).reduce((n, d) => n + d.scenarios.length, 0);
  return { cards, ...total };
}

// ---------------------------------------------------------------------------
// Phase 7, Test Lab / Execution Design, and the issue pack's assembly

function setSummary(cards) {
  return [...new Set(cards.map((card) => card.module))].map((module) => {
    const mine = cards.filter((card) => card.module === module);
    const ruleCount = new Set(mine.flatMap((card) => card.rules)).size;
    return `${module}: ${ruleCount} rule(s) on ${mine.length} card(s)`;
  });
}

export async function phase7(ctx) {
  const { pack, ref, job } = ctx;
  // An issue pack's cards take their sets first: Full Coverage and BREAK IT by rule.
  if (!job.suite) {
    const full = pack.objectives.find((row) => row.objective === ctx.fullCoverageObjective);
    const designedCards = Object.values(ctx.designed).flatMap((d) => d.cards);
    if (full && !full.applicable && designedCards.some((card) => card.derivation !== 'Quality')) {
      // Only when some card lands in the set; otherwise the old decision stands.
      const before = { ...full };
      full.applicable = true;
      if (designedCards.some((card) => setsOf(ctx, card).includes(full.objective))) {
        full.reason = 'Applicable: this set holds every requirement-derived card.';
        ctx.droppedObjectives = droppedList(ctx).filter((name) => name !== full.objective);
      } else Object.assign(full, before);
    }
    for (const d of Object.values(ctx.designed)) {
      d.cards = d.cards.filter((card) => {
        const sets = setsOf(ctx, card);
        if (sets.length) card.objectives = sets;
        else {
          d.assumptions.push({ assumption: `The card "${card.title}" was left out: no set takes it.`,
            why: 'Its objectives were not applicable and no other set could hold it.',
            impact: `Rules ${card.rules.join(', ')} lose this card.`,
            clarification: 'Design a card for them by hand.' });
        }
        return sets.length > 0;
      });
    }
  }
  // Code states why the pack has no quality-derived card, after the cards no set takes are gone.
  if (!Object.values(ctx.designed).some((d) => d.cards.some((c) => c.derivation === 'Quality'))) {
    pack.assumptions = [...list(pack.assumptions), {
      assumption: NO_QUALITY,
      why: 'No quality-derived card was written, or the ones written contradicted their rules or'
        + ' belonged to no set and were removed.',
      impact: 'No test in this pack goes beyond the stated rules.',
      clarification: 'Add quality-derived cases by hand where the Senior Review recommends them.' }];
  }
  const order = job.suite ? ctx.suiteSetOrder : ctx.builder.OBJECTIVES;
  const inSet = (card, objective) => list(card.objectives).includes(objective)
    || (job.suite && card.derivation !== 'Quality' && ctx.suiteRunSets.includes(objective));
  // The module is attached here: designed cards carry it only once the test cards are built.
  const allCards = ctx.documents.flatMap((doc) => (ctx.designed[doc.key]?.cards ?? [])
    .map((card) => ({ ...card, module: doc.module })));
  const used = order.filter((objective) => allCards.some((card) => inSet(card, objective)));
  const refs = [...ref.core, ...ref.chapters('7'), ref.docs.operatingManual].filter(Boolean);
  const cardsBySet = used.map((o) => `- ${o}: ${setSummary(allCards.filter((c) => inSet(c, o)))
    .join('; ') || 'no cards'}`).join('\n');
  const description = ctx.description;
  const objectivesText = used.map((o) => `- ${o}`).join('\n');
  let existing = ctx.existingTests ?? '';
  if (existing && estimateTokens(existing) > room(ctx, false, refs)
    - estimateTokens([description, objectivesText, cardsBySet].join('\n')) - 1000) {
    ctx.logs.detail('phase7 existing tests left out to fit the model',
      `${estimateTokens(existing)} tokens did not fit with the set information.`);
    existing = '';
  }
  const regression = used.filter((o) => /regression/i.test(o));
  const breakIt = used.includes(ctx.breakItObjective);
  ctx.logs.detail('phase7 inputs', `methodology chapters ${(ctx.config.reference.methodology
    ?.byPhase?.['7'] ?? []).join(', ') || 'none'}; operating manual: ${ref.docs.operatingManual
    ? 'yes' : 'no'}; existing tests: ${existing ? `${estimateTokens(existing)} tokens`
    : ctx.existingTests ? 'left out' : 'none'}`);
  const answer = await ask(ctx, {
    phase: 'phase7', step: 'sets', reasoning: false, refs,
    task: 'Write the scope of the test set for each objective: what it runs and why, in at'
      + ' most four sentences. Give no count of cards or rules in a scope; each set\'s rule'
      + ' summary carries the counts.'
      + `${regression.length ? ` For ${regression.join(' and ')}, give the execution scope: how its`
        + ' run is grouped, which cards run together and in what order, and which existing tests'
        + ' run again beside them.' : ''}`
      + `${breakIt ? ` For ${ctx.breakItObjective}, say what it tries to break (bad input, wrong`
        + ' order, boundaries, repeated actions) and what it leaves out.' : ''}`,
    inputs: [['Change description', description], ['Objectives with test sets', objectivesText],
      ['Cards by set', cardsBySet], ['Existing tests', existing]],
    schema: S.setScopesSchema(used),
  });
  const scopes = Object.fromEntries(answer.sets.map((row) => [row.objective, row.scope]));
  ctx.setScopes = Object.fromEntries(used.map((o) => [o, scopes[o] || `Runs the ${o} cards.`]));
  if (job.suite) return { sets: used.length };

  // Issue pack: number the cards per module, requirement cards first, and
  // build one set per objective in the standard's order.
  const testCards = [];
  const coverage = [];
  const counters = new Map();
  for (const doc of ctx.documents.filter((d) => d.inclusion === 'Included')) {
    const designed = ctx.designed[doc.key];
    if (!designed) continue;
    const ordered = [...designed.cards].sort((a, b) =>
      (a.derivation === 'Quality') - (b.derivation === 'Quality'));
    for (const card of ordered) {
      const n = (counters.get(doc.abbreviation) ?? 0) + 1;
      counters.set(doc.abbreviation, n);
      testCards.push({
        id: `TC-${doc.abbreviation}-${job.issue}-${String(n).padStart(3, '0')}`,
        title: card.title, module: doc.module, sourceDocument: doc.name, mission: card.mission,
        focus: card.focus, expected: card.expected, rules: card.rules,
        objectives: card.objectives, derivation: card.derivation,
        kind: scenarioKind(designed.scenarios, card.scenario), steps: card.steps,
      });
    }
    coverage.push(...designed.uncovered.map((row) => ({ ruleId: row.ruleId, status: row.status,
      strength: row.status === 'Partially Covered' ? 'Partial' : 'None', gap: row.gap,
      recommendation: row.recommendation })));
    pack.assumptions.push(...designed.assumptions);
    ctx.reuse.push(...designed.reuse.map((line) => `${doc.key}: ${line}`));
  }
  pack.testCards = testCards;
  pack.coverage = coverage;
  pack.testSets = used.map((objective, i) => {
    const cards = testCards.filter((card) => card.objectives.includes(objective));
    return { number: i + 1, name: `TS${String(i + 1).padStart(2, '0')} ${objective}`, objective,
      scope: ctx.setScopes[objective], ruleSummary: setSummary(cards), cards: cards.map((c) => c.id) };
  });
  return { sets: pack.testSets.length, cards: testCards.length };
}

/** The suite pack, from the card files and the narrative, through the repository's merge. */
export function mergeSuite(ctx) {
  const { pack } = ctx;
  const narrative = {
    suite: pack.suite, suiteInput: pack.suiteInput, crDescription: pack[ctx.config.idFields.description],
    intake: pack.intake, executiveSummary: pack.executiveSummary, impacts: pack.impacts,
    objectives: pack.objectives, setScopes: ctx.setScopes, seniorReview: pack.seniorReview ?? {}, testerNotes: pack.testerNotes ?? {},
    confidence: pack.confidence ?? {}, limitations: pack.limitations, improvementNotes: pack.improvementNotes,
    assumptions: pack.assumptions ?? [], sourceAuthority: ctx.config.suiteMerge?.sourceAuthority
      ?? 'approved business rules held in the master',
    modules: Object.fromEntries(ctx.documents.map((doc) => [doc.key, [doc.module, doc.abbreviation]])),
  };
  // The merge reads cards as the builder knows them: each with its scenario's kind, without the design pass's marks.
  const designed = Object.fromEntries(Object.entries(ctx.designed).map(([key, d]) => [key,
    { ...d, cards: d.cards.map(({ scenario, breakIt, key, ...card }) =>
      ({ ...card, kind: scenarioKind(d.scenarios, scenario) })) }]));
  const merged = ctx.suiteMerge.mergeSuitePack({ exportJson: ctx.exportJson, designed, narrative });
  // The merge need not carry the impact analysis; Phase 9 reads it from the pack.
  if (pack.impacts) merged.impacts ??= pack.impacts;
  // A suite takes the active rules only.
  for (const rule of merged.rules ?? []) rule.status ??= 'Active';
  // The merge carries the narrative's coverage rows only for uncovered rules;
  // the review's rows ride on top.
  const rows = new Map(merged.coverage.map((row) => [row.ruleId, row]));
  for (const row of pack.reviewCoverage ?? []) rows.set(row.ruleId, row);
  merged.coverage = [...rows.values()];
  // The merge's narrative names the description crDescription; the pack keeps
  // it under the field the repository's builder reads.
  merged[ctx.config.idFields.description] ??= pack[ctx.config.idFields.description];
  return merged;
}

// ---------------------------------------------------------------------------
// Phase 8, the builder, with bounded repairs

/**
 * Drops the assumptions that cite a rule ID the pack does not hold, or a count
 * of rules or cards the pack does not have. A count is checked against the
 * pack's totals, its counts by impact, risk, coverage status, derivation and
 * source document, and its set sizes. An answer from the build supervisor is
 * kept: it cites its own sources. Returns how many were dropped.
 */
export function dropUnfoundedAssumptions(ctx, pack) {
  const rules = list(pack.rules);
  if (!rules.length || !list(pack.assumptions).length) return 0;
  const shape = ctx?.config?.ruleShape ?? RULE_SHAPE;
  const known = new Set([...rules.map((r) => r.id), ...list(pack.coverage).map((r) => r.ruleId),
    ...list(pack.testCards).flatMap((card) => list(card.rules)),
    ...list(ctx?.documents).flatMap((doc) => list(doc.rules).map((r) => r.rule_id))]);
  const idPattern = new RegExp(`\\b${String(shape.prefixPattern).replace(/^\^/, '')}[A-Z0-9.-]*?`
    + `${shape.ruleIdPattern}\\b`, 'g');
  const tally = (items, key) => Object.values(items.reduce((acc, item) => {
    const k = String(key(item)); acc[k] = (acc[k] ?? 0) + 1; return acc;
  }, {}));
  const cards = list(pack.testCards);
  const ruleCounts = new Set([rules.length, ...tally(rules, (r) => r.impact),
    ...tally(rules, (r) => r.risk), ...tally(rules, (r) => r.sourceDocument),
    ...tally(rules, (r) => r.module), ...tally(list(pack.coverage), (r) => r.status),
    rules.filter((r) => !String(r.summary ?? '').startsWith(RETIRED_SUMMARY)).length,
    rules.filter((r) => String(r.summary ?? '').startsWith(RETIRED_SUMMARY)).length]);
  const cardCounts = new Set([cards.length, ...tally(cards, (c) => c.derivation),
    ...tally(cards, (c) => c.module), ...list(pack.testSets).map((set) => list(set.cards).length)]);
  const QUALIFIER = '(?:(?:active|retired|impacted|direct change|indirect impact|regression|not impacted'
    + '|covered|partially covered|weakly covered|missing|uncovered|high|medium|low|new|existing|business)\\s+)*';
  const counted = new RegExp(`\\b(\\d+)\\s+${QUALIFIER}(rules?|BRs?|(?:test )?cards?|test cases?)\\b`, 'gi');
  // A number that names a section, step or page, ends a range, or is a year is not a count.
  const notCount = (text, index, n) => /\b(?:section|sections|step|steps|page|pages|chapter|row|rows)\s*$/i
    .test(text.slice(0, index)) || /\d\s*(?:to|through|-|–)\s*$|\bbetween\s+\d+\s+and\s*$/i.test(text.slice(0, index))
    || (/^(?:19|20)\d\d$/.test(n) && /\b(?:in|since|from|until)\s*$/i.test(text.slice(0, index)));
  const grounded = (text) => {
    for (const id of String(text).match(idPattern) ?? []) if (!known.has(id)) return false;
    for (const { 1: n, 2: noun, index } of String(text).matchAll(counted)) {
      if (Number(n) === 1 || notCount(text, index, n)) continue;
      const allowed = /rule|BR/i.test(noun) ? ruleCounts : cardCounts;
      if (!allowed.has(Number(n))) return false;
    }
    return true;
  };
  const before = pack.assumptions.length;
  pack.assumptions = pack.assumptions.filter((a) => {
    const ok = a.answeredBy === ANSWERED_BY
      || grounded([a.assumption, a.why, a.impact, a.clarification].filter(Boolean).join(' '));
    if (!ok) ctx?.logs?.detail?.('assumption dropped: it cites a rule or count the pack does not hold',
      String(a.assumption));
    return ok;
  });
  return before - pack.assumptions.length;
}

/** Added to every prompt that asks the model for assumptions. */
const ASSUMPTION_RULE = ' An assumption records what the sources leave open. Never mention scenario'
  + ' IDs, parts, batches, redesigns, or what was supplied to you.';

const PIPELINE_TERMS = [/\bscenarios?\s+S\d+\b/i, /\bS\d+\s*(?:[-–]|to|through)\s*S\d+\b/i,
  /\bre-?design(?:ed|s)?\b/i, /\bbatch(?:es)?\b/i, /\bsupplied\s+to\s+(?:me|you|the\s+model)\b/i,
  /(?:\brules?\b|\bBR-[\w-]+(?:\.[\w-]+)*)[^.]*\b(?:(?:was|were)\s+)?(?:not|never)\s+supplied\b/i];

/**
 * Drops the model's assumptions that talk about how the pipeline ran (scenario IDs,
 * redesigns, batches, what was supplied) rather than what the sources leave open.
 * A term the change description or a rule uses itself is kept. Assumptions the
 * code writes are not passed through here. Returns the assumptions kept.
 */
export function withoutPipelineTerms(ctx, assumptions) {
  const source = [ctx?.description, ...list(ctx?.documents).flatMap((doc) => [doc.text,
    ...list(doc.rules).flatMap((rule) => [rule.name, rule.summary])])].filter(Boolean).join('\n');
  return list(assumptions).filter((a) => {
    const text = [a.assumption, a.why, a.impact, a.clarification].filter(Boolean).join(' ');
    const bad = PIPELINE_TERMS.find((re) => re.test(text) && !re.test(source));
    if (bad) ctx?.logs?.detail?.('assumption dropped: it describes how the pipeline ran', String(a.assumption));
    return !bad;
  });
}

const MISSING_RULES = /(?:\brules?\b|\bBR-[\w-]+(?:\.[\w-]+)*)[^.]*\b(?:(?:not|never)\s+(?:supplied|provided|included|listed|given)|(?:was|were)\s+(?:omitted|left out))\b/i;
// A claim about what the source documents hold is a real gap, not a claim about the input.
const ABOUT_SOURCE = /\b(?:spec|specification|documents?|source|export)\b/i;

/**
 * Drops duplicate assumptions (same text once case, punctuation and spacing are
 * ignored; the first stays), and, once every rule has an impact, the ones saying
 * rules were not supplied. The build supervisor's answers always stay, and another
 * assumption with the same text as one of them is the duplicate that goes. Returns
 * how many were dropped.
 */
export function tidyAssumptions(ctx, pack) {
  if (!list(pack.assumptions).length) return 0;
  const allClassified = list(pack.rules).length > 0 && list(pack.rules).every((r) => r.impact);
  const answered = (a) => a.answeredBy === ANSWERED_BY;
  const seen = new Set(pack.assumptions.filter(answered).map((a) => plainWords(a.assumption)));
  const before = pack.assumptions.length;
  pack.assumptions = pack.assumptions.filter((a) => {
    if (answered(a)) return true;
    const key = plainWords(a.assumption);
    if (key && seen.has(key)) {
      ctx?.logs?.detail?.('assumption dropped: duplicate', String(a.assumption));
      return false;
    }
    seen.add(key);
    const said = String(a.assumption ?? '');
    if (allClassified && MISSING_RULES.test(said) && !ABOUT_SOURCE.test(said)) {
      ctx?.logs?.detail?.('assumption dropped: every rule is classified', String(a.assumption));
      return false;
    }
    return true;
  });
  return before - pack.assumptions.length;
}

/**
 * Settles what code can settle before the builder looks: coverage rows that
 * disagree with the cards, assumptions citing rules or counts the pack does not
 * hold, a blank assumptions sheet, Direct Change rules no card covers, and an
 * overall confidence above the confidence ceiling, whose status line `log: false` leaves out.
 */
export function reconcile(ctx, pack, { log = true } = {}) {
  dropUnfoundedAssumptions(ctx, pack);
  tidyAssumptions(ctx, pack);
  const covered = new Map();
  for (const card of list(pack.testCards)) {
    for (const id of list(card.rules)) {
      const entry = covered.get(id) ?? { requirement: false };
      if (card.derivation !== 'Quality') entry.requirement = true;
      covered.set(id, entry);
    }
  }
  const ruleIds = new Set(list(pack.rules).map((rule) => rule.id));
  const reviewed = new Set(list(pack.coverage).map((row) => row.ruleId));
  const seen = new Set();
  const claims = ['Covered', 'Partially Covered', 'Weakly Covered'];
  // A High-risk Not Impacted rule needs a regression card or a stated reason, which only a
  // person or the repair call can give, so its blanks are left for the Phase 8 check.
  const highRisk = new Set(list(pack.rules).filter((rule) => rule.impact === 'Not Impacted'
    && String(rule.risk).toLowerCase() === 'high').map((rule) => rule.id));
  const mapping = (id) => `Not reviewed; coverage rests on the card mapping (${list(pack.testCards)
    .filter((card) => list(card.rules).includes(id)).map((card) => card.id).join(', ')}).`;
  const confirm = 'Confirm in review that the cards exercise this rule.';
  pack.coverage = list(pack.coverage).filter((row) => {
    if (!ruleIds.has(row.ruleId) || seen.has(row.ruleId)) return false;
    const cards = covered.get(row.ruleId);
    // A review row that denies coverage a card gives is kept when it says why, so the builder
    // fails it and the repair call reads the review's own words.
    if (cards && !claims.includes(row.status) && blank(row.gap)) return false;
    if (!cards && claims.includes(row.status)) return false;
    if (row.status === 'Covered' && cards && !cards.requirement) row.status = 'Weakly Covered';
    seen.add(row.ruleId);
    return true;
  }).map((row) => ({ ...row,
    strength: blank(row.strength) ? (row.status === 'Partially Covered' ? 'Partial' : 'Weak') : row.strength,
    gap: blank(row.gap) && !(row.status === 'Covered' && highRisk.has(row.ruleId))
      ? (row.status === 'Covered' ? mapping(row.ruleId) : 'Not stated by the review.') : row.gap,
    recommendation: blank(row.recommendation) && !(row.status === 'Covered' && highRisk.has(row.ruleId))
      ? (row.status === 'Covered' ? confirm : 'Review this rule\'s coverage by hand.')
      : row.recommendation }));
  // A rule with a requirement card and no review row at all reads Covered, as the builder would
  // have it, and says that no one reviewed it.
  for (const rule of list(pack.rules)) {
    if (!covered.get(rule.id)?.requirement || seen.has(rule.id) || reviewed.has(rule.id)
      || highRisk.has(rule.id)) continue;
    pack.coverage.push({ ruleId: rule.id, status: 'Covered', strength: 'Strong',
      gap: mapping(rule.id), recommendation: confirm });
    seen.add(rule.id);
  }
  for (const rule of list(pack.rules)) {
    if (covered.has(rule.id) || seen.has(rule.id) || rule.impact === 'Not Impacted') continue;
    pack.coverage.push({ ruleId: rule.id, status: 'Missing', strength: 'None',
      gap: 'No test card covers this rule.', recommendation: 'Design a card for this rule.' });
  }
  // The Coverage field is a count of the Coverage Matrix, so once written it follows the rows.
  if (!blank(pack.confidence?.coverage)) pack.confidence.coverage = coverageText(ctx, pack);
  const uncoveredDirect = list(pack.rules).filter((rule) => rule.impact === 'Direct Change'
    && !covered.has(rule.id)).map((rule) => rule.id);
  pack.limitations ??= {};
  if (uncoveredDirect.length) {
    pack.limitations['Coverage Matrix'] = `Direct Change rules with no test card: ${uncoveredDirect.join(', ')}.`;
  }
  // A dropped objective is a coverage gap. Written from the context every time, so a repair
  // answer that rewrites the limitations cannot lose it.
  const untested = untestedObjectives(ctx, pack);
  if (untested.length) {
    pack.limitations['Objective Matrix'] = 'Applicable but untested: no test card serves'
      + ` ${untested.join(', ')}. ${untested.length > 1 ? 'These objectives are' : 'This objective is'}`
      + ' a coverage gap in this pack.';
  } else if (String(pack.limitations['Objective Matrix'] ?? '').startsWith('Applicable but untested')) {
    delete pack.limitations['Objective Matrix'];
  }
  if (!list(pack.assumptions).length && blank(pack.limitations.Assumptions)) {
    pack.limitations.Assumptions = 'No assumptions were needed to build this pack.';
  }
  holdToCeiling(ctx, pack, { log });
  const overall = pack.confidence?.overall;
  if (overall && pack.executiveSummary) {
    const reason = String(pack.confidence?.reason ?? '').trim();
    pack.executiveSummary.confidence = reason ? `${overall}. ${reason}` : overall;
  }
  for (const [sheet, text] of Object.entries(pack.limitations)) {
    if (blank(text)) delete pack.limitations[sheet];
  }
  return pack;
}

/** The failed sheets' problems, as text for the model. */
const problemText = (built) => built.failed.map(([sheet, , , , notes]) => `${sheet}:\n${notes}`)
  .join('\n\n');

/** Sheets Phase 9 fills, which the build before the review leaves to it. */
export const REVIEW_SHEETS = ['Senior Tester Review', 'Tester Notes', 'Confidence Assessment',
  'Executive Summary'];

/**
 * One build of the pack: the reconcile, the builder, and the pipeline's own checks of
 * the pack, with the sheets in `deferred` left out of the failures. Writes the builder
 * status line and, when a sheet fails, its problems to detail.log. Throws
 * `builder-stop` when the builder will not read the pack. Returns the builder's result
 * with `failed` as the sheets that count.
 */
export function buildRound(ctx, pack, label = 'build', attempt = 0, deferred = []) {
  const { builder } = ctx;
  reconcile(ctx, pack);
  const whole = builder.buildPack(pack);
  if (whole.stop) throw new GateError('phase8', 'builder-stop');
  // The pipeline's own check of each card's Expected Result against its final step,
  // reported beside the builder's sheets so the repair call reads it the same way.
  const mismatched = expectedProblems(pack);
  // The pipeline's own checks of the pack against itself, run for any builder.
  const { failed: checked, warnings } = checkPack(pack, whole);
  for (const { code, text } of warnings) ctx.logs.detail(`builder warning ${code} ${label} ${attempt}`, text);
  const built = { ...whole, failed: [...whole.failed.filter(([sheet]) => !deferred.includes(sheet)),
    ...checked.filter(([sheet]) => !deferred.includes(sheet)),
    ...(mismatched.length ? [failedSheet(EXPECTED_SHEET, mismatched.join('\n'))] : [])] };
  const statuses = built.validation.map((row) => row[3]);
  ctx.logs.status({ job: ctx.job.id, phase: 'phase8', step: label, event: 'builder', attempt,
    failed: built.failed.length, limited: statuses.filter((s) => s === 'PASS WITH LIMITATIONS').length,
    passed: statuses.filter((s) => s === 'PASS').length });
  if (built.failed.length) ctx.logs.detail(`builder ${label} ${attempt}`, problemText(built));
  return built;
}

/**
 * Why a build was refused, for a status line: the sheets that failed and the first line
 * of the notes of the first failed sheet that has any, reduced to plain words.
 */
function failureWhy(failed) {
  return { failedSheets: sheetsField(failed.map(([sheet]) => sheet)),
    problem: failed.map(([, , , , notes]) => noteCode(notes)).find(Boolean) ?? '' };
}

/**
 * Phase 8: builds the pack, sends what fails to the repair, and ends by writing the
 * Draft workbook to work/review with the repository's builder command. The sheets in
 * `deferred` are left out of the in-memory failures only: the Draft workbook shows
 * them with the review's stand-ins, and every sheet the builder command fails goes to
 * the repair. Throws `builder-fail` when the pack still fails after the last repair, or
 * when the builder command writes no workbook and names no sheet it failed.
 */
export async function phase8(ctx, pack, label = 'build', deferred = []) {
  for (let attempt = 0; ; attempt += 1) {
    let built = buildRound(ctx, pack, label, attempt, deferred);
    if (!built.failed.length) {
      const draft = draftWorkbook(ctx, pack, `${label} ${attempt}`);
      ctx.logs.status({ job: ctx.job.id, phase: 'phase8', step: label, event: 'draft', attempt,
        written: Boolean(draft.workbook), failed: draft.failed.length,
        ...(draft.workbook ? {} : failureWhy(draft.failed)) });
      if (draft.workbook) return pack;
      if (!draft.failed.length) throw new GateError('phase8', 'builder-fail', { sheets: 0 });
      built = { ...built, failed: draft.failed };
    }
    if (attempt >= ctx.config.builder.retries) {
      throw new GateError('phase8', 'builder-fail', { sheets: built.failed.length, ...failureWhy(built.failed) });
    }
    await repair(ctx, pack, built, `${label}-${attempt + 1}`);
  }
}

/**
 * Answers in code the builder problems that name a High-risk Not Impacted rule with no reason:
 * the Coverage Matrix gap takes the rule's Phase 3 rationale, so the repair call never has to
 * invent one. A rule with no usable rationale is left for the model. Returns the builder's
 * failed sheets without the problems it answered, and without a sheet left with none.
 */
function statedReasons(pack, failed) {
  const byId = new Map(list(pack.rules).map((rule) => [rule.id, rule]));
  const rows = new Map(list(pack.coverage).map((row) => [row.ruleId, row]));
  const claims = ['Covered', 'Partially Covered', 'Weakly Covered'];
  const lead = new RegExp(`^(\\S+) ${NO_REASON_PROBLEM}`);
  const left = [];
  for (const [sheet, , , , notes] of failed) {
    const kept = String(notes).split('\n').filter((line) => {
      const rule = byId.get(lead.exec(line)?.[1]);
      const reason = noStop(rule?.rationale ?? '');
      // A thin rationale, or one that reads as the pipeline's own filler, is no reason.
      if (!rule || reason.split(/\s+/).filter(Boolean).length < 4 || FILLED_GAP.test(String(rule?.rationale ?? '').trim())) return true;
      const carded = list(pack.testCards).some((card) => list(card.rules).includes(rule.id));
      const row = rows.get(rule.id) ?? { ruleId: rule.id };
      if (!carded) Object.assign(row, { status: 'Not Applicable', strength: 'None' });
      else if (!claims.includes(row.status)) Object.assign(row, { status: 'Weakly Covered', strength: 'Weak' });
      row.gap = carded ? `${reason}.` : `${reason}; no regression card is needed.`;
      if (blank(row.recommendation)) row.recommendation = 'None.';
      rows.set(rule.id, row);
      return false;
    });
    if (kept.some((line) => line.trim())) left.push([sheet, kept.join('\n')]);
  }
  pack.coverage = [...rows.values()];
  return left.map(([sheet, notes]) => `${sheet}:\n${notes}`).join('\n\n');
}

// A problem that asks for a card the pack does not have yet.
const ASKS_NEW_CARD = /\b(add|create|build|write|new)\b[^\n]{0,60}\bcards?\b/i;

/**
 * A new card from a repair, numbered after the module's last card and put in the sets its
 * objectives name. It covers only rules the findings named. Returns the card, or null when it
 * names none of them or no included document holds their module.
 */
function addRepairCard(ctx, pack, fresh, named) {
  const rules = list(pack.rules).filter((rule) => named.has(rule.id) && fresh.rules.includes(rule.id));
  const doc = ctx.documents.find((d) => d.inclusion === 'Included' && d.module === rules[0]?.module);
  if (!doc) return null;
  const same = new Set(rules.filter((rule) => rule.module === doc.module).map((rule) => rule.id));
  const tidy = tidyCard(fresh, same);
  if (!tidy.rules.length) return null;
  const prefix = `TC-${doc.abbreviation}-${ctx.job.issue}-`;
  const last = Math.max(0, ...list(pack.testCards).filter((card) => card.id.startsWith(prefix))
    .map((card) => Number(card.id.slice(prefix.length)) || 0));
  const card = { id: `${prefix}${String(last + 1).padStart(3, '0')}`, title: tidy.title,
    module: doc.module, sourceDocument: doc.name, mission: tidy.mission, focus: tidy.focus,
    expected: tidy.expected, rules: tidy.rules, objectives: tidy.objectives,
    derivation: tidy.derivation, kind: 'decision', steps: tidy.steps };
  pack.testCards.push(card);
  placeCard(ctx, pack, card);
  summarizeSets(pack);
  return card;
}

/**
 * Puts a card of an issue pack in the sets `setsOf` gives it and takes it out of every
 * other set, so its objectives and the sets agree as they do when Phase 7 builds them.
 * `breakIt` says the card is a BREAK IT card. A set never loses its last card this way:
 * the card stays in it and keeps that objective.
 */
function placeCard(ctx, pack, card, breakIt = false) {
  card.objectives = setsOf(ctx, { ...card, breakIt });
  for (const set of list(pack.testSets)) {
    const held = list(set.cards).includes(card.id);
    const wanted = card.objectives.includes(set.objective);
    if (wanted && !held) set.cards = [...list(set.cards), card.id];
    else if (held && !wanted && set.cards.length > 1) set.cards = set.cards.filter((id) => id !== card.id);
    else if (held && !wanted) card.objectives.push(set.objective);
  }
}

/** Writes each set's rule summary from the cards the set holds. */
function summarizeSets(pack) {
  for (const set of list(pack.testSets)) {
    set.ruleSummary = setSummary(pack.testCards.filter((card) => list(set.cards).includes(card.id)));
  }
}

/** Takes a repair's new card back out of the pack and its sets. */
function dropRepairCard(pack, card) {
  pack.testCards = pack.testCards.filter((c) => c.id !== card.id);
  for (const set of list(pack.testSets)) set.cards = list(set.cards).filter((id) => id !== card.id);
  summarizeSets(pack);
}

/** True when the BREAK IT set holds the card, which is how a card of the pack shows it is one. */
const inBreakIt = (ctx, pack, card) => list(pack.testSets).some((set) =>
  set.objective === ctx.breakItObjective && list(set.cards).includes(card.id));

/** What a repair call is told about the rules of a new card when the pack holds a retired rule. */
const ACTIVE_RULES_CARD = 'A new card for behavior that still happens cites the active rules its'
  + ' expected result exercises, never only rules whose summary starts with "Retired:"; a card that'
  + ' cites only retired rules checks that their behavior is gone.';

/** What the recheck of a new card is told when one cites retired rules alone. */
const RETIRED_ONLY_VERIFY = ' A card whose every cited rule is marked removed checks that the removed'
  + ' behavior is gone and nothing else, whatever its derivation: it does not follow when its'
  + ' Expected Result describes behavior that still happens, which no rule it cites supports; say'
  + ' in the reason that the card needs the active rules for that behavior.';

/** The card text a repair call sees: every field but `kind`, which code writes and no repair changes. */
const repairCardText = ({ kind, ...card }) => JSON.stringify(card);

/** What a repair call that sent nothing returned. */
const NOTHING_RETURNED = { cards: [], newCards: [], keptNewCards: [], coverage: [], limitations: [],
  assumptions: 0, undone: [] };

/** The cards of the pack whose ID a repair's problem text holds: the cards that call is given. */
const namedCards = (pack, text) => list(pack.testCards).filter((card) => text.includes(card.id));

/** Tokens one corrected card takes in a repair reply, steps included. */
const REPAIR_CARD_TOKENS = 2500;

/**
 * The most cards one fix-round repair call is given. Every card comes back in full, so the
 * cards of one call are held to half of the reply's output budget; the rest is room for
 * coverage rows, limitations, new cards and cards longer than most.
 */
export const repairCardsMax = (ctx) => Math.max(1,
  Math.floor(ctx.config.model.maxOutput / 2 / REPAIR_CARD_TOKENS));

/**
 * How many whole objects the list under `key` holds in a JSON reply that was cut off: the
 * items the model finished before its output budget ran out.
 */
export function wholeItems(text, key) {
  const reply = String(text ?? '');
  const at = reply.indexOf(`"${key}"`);
  const from = at < 0 ? -1 : reply.indexOf('[', at);
  if (from < 0) return 0;
  let depth = 0;
  let quoted = false;
  let count = 0;
  for (let i = from + 1; i < reply.length; i += 1) {
    const ch = reply[i];
    if (quoted) {
      if (ch === '\\') i += 1;
      else if (ch === '"') quoted = false;
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === '{' || ch === '[') {
      depth += 1;
    } else if (ch === '}' || ch === ']') {
      if (depth === 0) break;
      depth -= 1;
      if (depth === 0 && ch === '}') count += 1;
    }
  }
  return count;
}

/**
 * One repair call: the builder's FAIL text, the cards and rules it names, and their fixes.
 * The call is given the design rules, and each card it corrects goes back through the set
 * rules, so its objectives and its sets agree whatever the reply names. Returns what came
 * back, for the caller to report: the IDs of the cards it corrected, the new cards it offered
 * and the ones kept, the rules of its coverage rows, the sheets of its limitations, how many
 * assumptions it added, and the corrected cards whose change was undone.
 * `only`, when given, lists the named cards this call corrects; the other named cards belong
 * to calls of their own. With `cutOk`, a reply cut off at its output budget changes nothing
 * and comes back as `cut`, the error, in place of failing the caller.
 */
async function repair(ctx, pack, built, step, { assumptions = false, newCards = false, only = null,
  cutOk = false } = {}) {
  const text = statedReasons(pack, built.failed);
  if (!text) return NOTHING_RETURNED;
  const cards = namedCards(pack, text).filter((card) => !only || only.includes(card.id));
  const ruleIds = list(pack.rules).map((rule) => rule.id);
  const named = list(pack.rules).filter((rule) => text.includes(rule.id)
    || cards.some((card) => card.rules.includes(rule.id)));
  const sheets = (ctx.builder.SHEET_ORDER ?? built.validation.map((row) => row[0]))
    .filter((sheet) => sheet !== 'Workbook Validation');
  const objectives = ctx.job.suite ? ctx.builder.OBJECTIVES
    : pack.objectives.filter((row) => row.applicable).map((row) => row.objective);
  // Only a fix round takes new cards. A new card covers a rule a problem names, never one that
  // only a named card cites. A suite pack takes no new card: its cards come from the suite files.
  const newIds = !newCards || ctx.job.suite ? []
    : named.filter((rule) => citesId(text, rule.id)).map((rule) => rule.id);
  const retired = new Set(list(pack.rules).filter(isRetired).map((rule) => rule.id));
  const request = {
    phase: 'phase8', step: `repair-${step}`, reasoning: false, refs: [ctx.ref.docs.workbookStandard],
    task: 'The workbook builder failed these sheets. Fix each problem: return every named card'
      + ' corrected in full, a coverage row for each rule whose coverage is wrong, and a'
      + ' limitation for a sheet that cannot be completed, saying why.'
      + (newIds.length ? ' When a problem asks for a card that does not exist, return it under'
        + ' newCards, covering only a rule the problem names; the card is numbered for you.'
        + (retired.size ? ` ${ACTIVE_RULES_CARD}` : '') : '')
      + ' A reason comes from the'
      + ' change description, the existing and new behavior, or the rules. Do not call a feature'
      + ' or window new unless the new behavior says so; behavior that exists already is what'
      + ' regression protects.',
    inputs: [['Change description', ctx.description],
      ['Existing behavior', ctx.summary?.existingBehavior], ['New behavior', ctx.summary?.newBehavior],
      ['Builder problems', text],
      designRulesInput(ctx, pack, 'The pipeline builds every pack by these rules and applies them again to'
        + ' what you return. Never change a card or a coverage row to break one, even when a problem'
        + ' asks for it.'),
      ['Cards for this call', only ? 'The problems name more cards than one reply holds. Correct only'
        + ' these cards in this reply; the other named cards are corrected in calls of their own:'
        + ` ${only.join(', ')}` : ''],
      ['Cards named', cards.map(repairCardText).join('\n')],
      ['Rules named', asLines(named.map(ruleLine))]],
    schema: S.repairSchema({ cardIds: cards.map((card) => card.id), ids: ruleIds, objectives,
      derivations: ctx.builder.DERIVATIONS, statuses: ctx.builder.COVERAGE_STATUSES, sheets,
      assumptions, newIds }),
  };
  let answer;
  try {
    answer = await ask(ctx, request);
  } catch (error) {
    if (!cutOk || !(error instanceof ModelError) || error.code !== 'length') throw error;
    return { ...NOTHING_RETURNED, cut: error };
  }
  const fresh = new Set(newIds);
  const added = [];
  for (const card of list(answer.newCards).slice(0, S.NEW_CARDS_MAX)) {
    const made = addRepairCard(ctx, pack, card, fresh);
    if (made) added.push(made);
  }
  // A new card's Expected Result follows from its rules, as a repaired card's does; one that
  // does not is left out. A card on retired rules alone is checked as an absence check.
  const { failed: unsound } = await verifyCards(ctx, added, `recheck-new-${step}`,
    added.some((card) => card.rules.every((id) => retired.has(id))) ? RETIRED_ONLY_VERIFY : '');
  for (const card of unsound.keys()) dropRepairCard(pack, card);
  const corrected = [];
  const before = new Map(cards.map((card) => [card.id, card.expected]));
  for (const fixed of answer.cards) {
    const card = pack.testCards.find((c) => c.id === fixed.id);
    if (!card) continue;
    const tidy = tidyCard(fixed, new Set(ruleIds.filter((id) => pack.rules
      .find((rule) => rule.id === id)?.module === card.module)));
    if (!tidy.rules.length) continue;
    const { objectives } = card;
    Object.assign(card, { ...tidy, id: card.id, module: card.module, sourceDocument: card.sourceDocument });
    // A suite pack's sets come from the suite merge, so its card keeps the objectives the merge gave it.
    if (ctx.job.suite) card.objectives = objectives;
    else corrected.push(card);
  }
  // A corrected card goes back through the set rules, and every set says what it holds now.
  for (const card of corrected) placeCard(ctx, pack, card, inBreakIt(ctx, pack, card));
  if (corrected.length) summarizeSets(pack);
  // A repair that changed a card's Expected Result is checked against the rules again; one
  // that does not follow is undone, final step included.
  const changed = cards.filter((card) => card.expected !== before.get(card.id));
  const { failed } = await verifyCards(ctx, changed, `recheck-${step}`);
  for (const card of failed.keys()) {
    const kept = before.get(card.id);
    card.expected = kept;
    const last = list(card.steps).at(-1);
    if (last) last.expected = kept;
    pack.assumptions ??= [];
    pack.assumptions.push({
      assumption: `The repair of card ${card.id} changed its Expected Result, and the change was undone.`,
      why: `${noStop(failed.get(card))}.`, impact: 'The card keeps the Expected Result checked in Phase 6.',
      clarification: 'Check the card by hand if the builder still reports it.' });
  }
  const rows = new Map(list(pack.coverage).map((row) => [row.ruleId, row]));
  for (const row of answer.coverage) rows.set(row.ruleId, row);
  // A rule a kept new card covers is no longer Missing or Not Applicable, whatever the reply
  // says about it; a card dropped as unsound clears nothing.
  const covers = new Set(added.filter((card) => !unsound.has(card)).flatMap((card) => card.rules));
  pack.coverage = [...rows.values()].filter((row) => !(covers.has(row.ruleId)
    && DENIES_COVERAGE.includes(row.status)));
  for (const { sheet, text: why } of answer.limitations) {
    if (!blank(why)) pack.limitations[sheet] = why;
  }
  if (assumptions) {
    const seen = new Set(list(pack.assumptions).map((row) => row.assumption));
    pack.assumptions = [...list(pack.assumptions), ...withoutPipelineTerms(ctx, answer.assumptions)
      .filter((row) => !seen.has(row.assumption) && seen.add(row.assumption))];
  }
  const offered = list(answer.newCards).slice(0, S.NEW_CARDS_MAX);
  ctx.repairs += 1;
  return {
    cards: answer.cards.map((card) => card.id),
    newCards: offered,
    keptNewCards: added.filter((card) => !unsound.has(card)),
    coverage: answer.coverage.map((row) => row.ruleId),
    limitations: answer.limitations.filter(({ text: why }) => !blank(why)).map(({ sheet }) => sheet),
    assumptions: assumptions ? list(answer.assumptions).length : 0,
    undone: [...failed.keys()].map((card) => card.id),
  };
}

// ---------------------------------------------------------------------------
// Phase 9, Quality Review

function packView(ctx, pack, detail) {
  const coverage = ctx.builder.ruleCoverage ? ctx.builder.ruleCoverage(pack) : [];
  const status = new Map(coverage.map((row) => [row.rule.id, row.status]));
  const rules = list(pack.rules).map((rule) => (detail
    ? `- ${rule.id} | ${rule.name} | ${rule.impact} | risk ${rule.risk} | ${status.get(rule.id) ?? ''}`
    : `- ${rule.id} | ${rule.impact} | ${status.get(rule.id) ?? ''}`));
  const cards = list(pack.testCards).map((card) => (detail
    ? `- ${card.id} | ${card.title} | ${card.derivation} | rules ${card.rules.join(', ')}`
    : `- ${card.id} | ${card.derivation} | ${card.rules.length} rule(s)`));
  const sets = list(pack.testSets).map((set) => `- ${set.name}: ${list(set.cards).length} card(s)`);
  return [['Rules', asLines(rules)], ['Test cards', asLines(cards)], ['Test sets', asLines(sets)],
    ['Executive summary', JSON.stringify(pack.executiveSummary)],
    ['Objectives', asLines(list(pack.objectives).map((row) =>
      `- ${row.objective}: ${row.applicable ? 'Applicable'
        : droppedList(ctx).includes(row.objective) ? 'Applicable, untested (no card)' : 'Not Applicable'}`))]];
}

/** Fix rounds the review runs between the checklist and the revalidation. */
const REVIEW_FIX_ROUNDS = 2;
/** The sheet name the review's findings are reported under to the repair call. */
const REVIEW_SHEET = 'Quality Review';

/**
 * The pack with the sheets Phase 9 has not filled yet standing in, so the
 * builder writes the Draft workbook. Until the overall confidence is rated the
 * draft reads Low, in the Confidence Assessment and the Executive Summary, with a
 * limitation saying the review is pending, so no stand-in claims more than the
 * pack supports. A rated pack keeps its rating.
 */
function draftPack(ctx, pack) {
  const draft = reconcile(ctx, structuredClone(pack), { log: false });
  delete draft.revalidation;
  // A field the review has not written is blank, or an empty object a suite merge leaves.
  const standIn = (current, schema, over = {}) => ({
    ...Object.fromEntries(Object.keys(schema.properties).map((key) => [key, 'Pending review.'])),
    ...Object.fromEntries(Object.entries(current ?? {}).filter(([, value]) => !blank(value))),
    ...over });
  draft.seniorReview = standIn(draft.seniorReview, S.seniorReviewSchema.properties.seniorReview);
  draft.testerNotes = standIn(draft.testerNotes, S.testerNotesSchema.properties.testerNotes);
  const rated = ctx.builder.CONFIDENCE_LEVELS.includes(draft.confidence?.overall);
  draft.confidence = standIn(draft.confidence,
    { properties: Object.fromEntries(['overall', ...CONFIDENCE_FIELDS.map(([field]) => field)].map((key) => [key, 0])) },
    rated ? {} : { overall: 'Low' });
  // A rated pack's summary already carries the rating: reconcile writes it, held to the
  // confidence ceiling. The status line for a lowered rating comes from the build of the pack itself.
  if (!rated && draft.executiveSummary) draft.executiveSummary.confidence = 'Low';
  // A Low rating needs a limitation saying why, or the draft fails the builder's own check.
  if (draft.confidence.overall === 'Low') {
    draft.limitations = { ...draft.limitations };
    draft.limitations['Confidence Assessment'] ||= 'Pending review.';
  }
  return draft;
}

/**
 * The sheets a builder command printed as FAIL, each with the indented lines under
 * it as its notes, in the shape the repair reads. The Workbook Validation line only
 * sums up the other sheets, so it counts only when no other sheet failed.
 */
function builderFailures(stdout) {
  const failed = [];
  let current = null;
  for (const line of stdout.split('\n')) {
    const status = /^(FAIL|PASS WITH LIMITATIONS|PASS)\s+(\S.*?)\s*$/.exec(line);
    if (status) {
      current = status[1] === 'FAIL' ? { sheet: status[2], notes: [] } : null;
      if (current) failed.push(current);
    } else if (current && /^\s+\S/.test(line)) {
      current.notes.push(line.trim());
    } else {
      current = null;
    }
  }
  const sheets = failed.filter(({ sheet }) => sheet !== 'Workbook Validation');
  return (sheets.length ? sheets : failed).map(({ sheet, notes }) => failedSheet(sheet, notes.join('\n')));
}

/**
 * Writes the Draft workbook to work/review, with the builder command the repository
 * gives, and says what the builder did: its exit `status`, its whole output as `text`,
 * the PASS and FAIL `lines` it printed, the sheets it `failed` as the repair reads
 * them, and the `workbook` it wrote, null when it wrote none. When it wrote none, the
 * whole output goes to detail.log as `builder draft <label>`.
 */
export function draftWorkbook(ctx, pack, label) {
  const dir = path.join(ctx.config.output, ctx.job.id, 'work', 'review');
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, 'draft-pack.json');
  fs.writeFileSync(file, JSON.stringify(draftPack(ctx, pack)));
  const output = {};
  runCommand(ctx, ctx.config.builder.command, { pack: file, out: dir }, { output });
  const text = output.stdout ?? '';
  const book = fs.readdirSync(dir).find((name) => name.endsWith('.xlsx'));
  if (!book) ctx.logs.detail(`builder draft ${label}`, text);
  return { dir, status: output.status, text, workbook: book ? path.join(dir, book) : null,
    lines: text.split('\n').filter((line) => /^(PASS|FAIL)/.test(line)), failed: builderFailures(text) };
}

/** The Draft workbook the builder writes for the pack as it stands, read back as sheets. */
function builtSheets(ctx, pack) {
  const draft = draftWorkbook(ctx, pack, 'review');
  if (!draft.workbook) {
    throw new GateError('phase9', 'builder-fail', { sheets: draft.failed.length, ...failureWhy(draft.failed) });
  }
  return readXlsx(draft.workbook).map(readSheet);
}

/**
 * The built workbook as text, one row to a line, in pieces that each fit
 * `tokens`. The sheets Phase 9 writes itself and the validation sheet are left out,
 * unless `review` asks for them: the revalidation reads the finished workbook.
 */
function workbookPieces(ctx, pack, tokens, { review = false } = {}) {
  const skip = new Set(review ? [] : [...REVIEW_SHEETS, 'Workbook Validation']);
  // Until the overall level is rated the draft shows a stand-in; no call reads it as a rating.
  const unrated = !ctx.builder.CONFIDENCE_LEVELS.includes(pack.confidence?.overall);
  const lines = builtSheets(ctx, pack).filter((sheet) => !skip.has(sheet.name)).flatMap((sheet) => [
    ...(sheet.title ? [`[${sheet.name}] ${sheet.title.text}`] : []),
    ...sheet.rows.map((row) => `[${sheet.name} row ${row.n}] ${Object.entries(row.cells)
      .filter(([, value]) => value).map(([header, value]) => `${header}: ${value}`).join(' | ')}`),
  ]).filter((line) => !(unrated && /^\[Dashboard row \d+\].*Overall Confidence/.test(line)))
    .flatMap((line) => splitText(line, tokens));
  return batches(lines, (line) => line, tokens).map((group) => group.join('\n'));
}

/** Room for the workbook text in one review call, after the description and `extra`. */
const reviewBudget = (ctx, refs, extra) => room(ctx, true, refs) - estimateTokens(ctx.description)
  - 2000 - estimateTokens(extra.map(([, text]) => text).join('\n'));

/** Every rule with its impact and the cards that cite it, one line each. */
function rulesIndex(pack) {
  return list(pack.rules).map((rule) => {
    const cards = list(pack.testCards).filter((card) => list(card.rules).includes(rule.id))
      .map((card) => card.id);
    return { id: rule.id, line: `- ${rule.id} | ${rule.impact} | cards: ${cards.join(', ') || 'none'}` };
  });
}

/**
 * What the review calls read: one view per piece of the built workbook. A
 * workbook in several parts opens each part with an index of the rules that part
 * shows and the cards that cite them, so a part that shows a rule but not its
 * cards can still see them; the index takes at most a third of the room.
 */
function reviewViews(ctx, pack, refs, extra = [], { review = false } = {}) {
  const budget = reviewBudget(ctx, refs, extra);
  if (budget < 1000) throw new GateError('phase9', 'pack-too-big-to-review');
  const label = 'Built workbook';
  let pieces = workbookPieces(ctx, pack, budget, { review });
  const index = rulesIndex(pack);
  const cap = Math.floor(budget / 3);
  if (pieces.length > 1) pieces = workbookPieces(ctx, pack, budget - cap, { review });
  if (!pieces.length) throw new GateError('phase9', 'review-workbook-empty');
  if (pieces.length === 1) return [[[label, pieces[0]]]];
  return pieces.map((text, i) => {
    const lines = [];
    let used = 0;
    for (const row of index.filter((rule) => text.includes(rule.id))) {
      used += estimateTokens(row.line);
      if (used > cap) break;
      lines.push(row.line);
    }
    return [...(lines.length ? [['Rules in this part and the cards that cite them', asLines(lines)]] : []),
      [`${label}, part ${i + 1} of ${pieces.length}`, text]];
  });
}

/**
 * The references and workbook text every single-answer review call reads, with
 * the description and any earlier review answers. A workbook too long for one
 * call is summarized by `packView` for these calls; the checklist and the
 * revalidation read it in parts.
 */
function reviewInputs(ctx, pack, extra = []) {
  const { ref } = ctx;
  const refs = [...ref.core, ref.docs.validation, ...ref.chapters('9')];
  const views = reviewViews(ctx, pack, refs, extra);
  let view = views[0];
  if (views.length > 1) {
    const budget = reviewBudget(ctx, refs, extra);
    const size = (rows) => estimateTokens(rows.map(([, text]) => text).join('\n'));
    view = packView(ctx, pack, true);
    if (size(view) > budget) view = packView(ctx, pack, false);
    if (size(view) > budget) throw new GateError('phase9', 'pack-too-big-to-review');
  }
  return { refs, inputs: [['Change description', ctx.description], ...view, ...extra] };
}

/** The checklist findings a change to the pack could settle: those with a fix. */
const openText = (ctx) => list(ctx.reviewFindings)
  .filter((row) => !blank(row.fix) && !PLACEHOLDER_FIX.test(row.fix))
  .map((row) => `- ${row.issue} (fix: ${row.fix})`).join('\n');

const issueText = (ctx) => list(ctx.reviewFindings)
  .map((row) => `- ${row.section ? `[${row.section}] ` : ''}${row.issue} (fix: ${row.fix})`).join('\n');

/**
 * Phase 9 runs as four steps, each a checkpoint of its own, so no one call
 * thinks through the whole review. The first runs the checklist over the built
 * workbook with thinking off, in parts when it is long: issues, the coverage
 * rows for rules not plainly Covered, and assumptions. `again` is a check after
 * a fix round, which replaces the issues and keeps the rest. Every call is given
 * the design rules as facts it lists no issue on.
 */
export async function phase9Checklist(ctx, pack, { again = false } = {}) {
  const refs = [...ctx.ref.core, ctx.ref.docs.validation, ...ctx.ref.chapters('9')];
  const extra = [impactsInput(ctx, pack, false, refs),
    designRulesInput(ctx, pack, 'The pipeline builds every pack by these rules. They are facts about this'
      + ' pack, not issues: never list an issue because the pack follows one, and never give a fix'
      + ' that would break one.')];
  const views = reviewViews(ctx, pack, refs, extra);
  // Rules taken from document text leave the checklist no matrix export to check them against.
  const limited = ctx.derived > 0;
  const noExport = !ctx.config.inputs.ruleExport;
  const derivedFrom = list(ctx.derivedDocuments).join(', ') || 'some documents';
  const answers = [];
  for (const [i, view] of views.entries()) {
    answers.push(await ask(ctx, {
      phase: 'phase9', step: again ? 'checklist-again' : 'checklist', reasoning: false, refs,
      inputs: [['Change description', ctx.description], ...view, ...extra],
      task: 'Run the Validation checklist against this pack. List each issue and its fix. A fix'
        + ' names the card or rule to change and what to change it to; leave it blank for an'
        + ' issue no change to the pack can settle. Give each issue the section of the Validation'
        + ' checklist it falls under. Give a coverage row for every rule that is'
        + ' not plainly Covered, with its strength, gap and recommendation. Add the assumptions'
        + ' the pack still needs.' + ASSUMPTION_RULE
        + (views.length > 1 ? ` The workbook comes in ${views.length} parts; this is part`
          + ` ${i + 1}. Report what this part shows, and judge a rule's coverage only from the`
          + ' cards the rules index lists for it when this part shows them.' : '')
        + (limited ? (noExport
          ? ' The rules were derived from document text because no Requirements Matrix export'
            + ' was available, so run checklist item OPS-009 as limited and say so.'
          : ` The rule export held no rules for ${derivedFrom}, so their rules were derived from`
            + ' the document text; run checklist item OPS-009 as limited for those rules and say'
            + ' so.') : ''),
      schema: S.checklistSchema({ statuses: ctx.builder.COVERAGE_STATUSES }),
    }));
  }
  const issues = answers.flatMap((answer) => answer.issues);
  ctx.private(again ? 'phase9-issues-again.json' : 'phase9-issues.json', issues);
  ctx.reviewFindings = issues;
  if (again) return { issues: issues.length, coverageRows: 0 };
  pack.assumptions = [...list(pack.assumptions),
    ...withoutPipelineTerms(ctx, answers.flatMap((answer) => answer.assumptions)),
    ...(limited ? [{ assumption: noExport
      ? 'Checklist item OPS-009 ran limited: no Requirements Matrix export was available.'
      : `Checklist item OPS-009 ran limited for the rules of ${derivedFrom}: the rule export held`
        + ' none for them.',
    why: 'The rules were derived from document text, so there is no matrix to check them against.',
    impact: 'The matrix check covers only the rules in this pack.',
    clarification: noExport ? 'Export the Requirements Matrix and run the check again.'
      : 'Extract the rules for these documents and run the check again.' }] : [])];
  const ruleIds = new Set(list(pack.rules).map((rule) => rule.id));
  const reviewRows = answers.flatMap((answer) => answer.coverage).filter((row) =>
    ruleIds.has(row.ruleId) && row.status !== 'Covered');
  const rows = new Map(list(pack.coverage).map((row) => [row.ruleId, row]));
  for (const row of reviewRows) rows.set(row.ruleId, row);
  pack.coverage = [...rows.values()];
  pack.reviewCoverage = reviewRows;
  return { issues: issues.length, coverageRows: reviewRows.length };
}

/**
 * The fix loop between the checklist and the revalidation. Each finding that
 * names a card, a rule or a sheet goes through `fixRound`, the pack is rebuilt,
 * and the checklist reads the rebuilt workbook again; at most two rounds.
 * Findings left after the last round stay in `ctx.reviewFindings` for the
 * later calls.
 */
export async function phase9Fix(ctx, pack) {
  ctx.appliedFixes ??= [];
  let rounds = 0;
  while (rounds < REVIEW_FIX_ROUNDS) {
    const findings = fixableFindings(ctx, pack, list(ctx.reviewFindings));
    if (!findings.length) break;
    rounds += 1;
    await fixRound(ctx, pack, findings, `review-${rounds}`, REVIEW_SHEETS);
    await phase9Checklist(ctx, pack, { again: true });
  }
  return { rounds };
}

/** The checklist and the fix rounds after it, as Phase 9's first step runs them. */
export async function checklistRounds(ctx, pack) {
  const counts = await phase9Checklist(ctx, pack);
  ctx.reviewIssues = counts.issues;
  const fixes = await phase9Fix(ctx, pack);
  return { ...counts, fixRounds: fixes.rounds };
}

const PLACEHOLDER_FIX = /^\W*(n\/?a|none|nothing|no change|not applicable|no fix)\b/i;
const escapeRe = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
/** True when `text` names `id` whole, so BR-1 is not found inside BR-10. */
export const citesId = (text, id) => new RegExp(`(?<![A-Za-z0-9.-])${escapeRe(id)}(?![A-Za-z0-9]|[.-][A-Za-z0-9])`).test(text);

/**
 * True when `text` names the sheet: a name of several words as a phrase in any case, a
 * one-word name only as written, so ordinary prose about "rules" names no sheet.
 */
function namesSheet(text, sheet) {
  const found = new RegExp(`(?<![A-Za-z0-9])${escapeRe(sheet)}(?![A-Za-z0-9])`,
    /\s/.test(sheet.trim()) ? 'i' : '');
  return found.test(text);
}

/**
 * What a review finding names that a fix can change, or null when it names none
 * or its fix is a placeholder: the cards and rules of the pack it cites, and
 * the sheets (the Coverage Matrix, Assumptions, and the like) it calls out.
 * The sheets the review writes itself and the validation sheet are not named
 * targets: a later call writes them.
 */
export function fixTargets(ctx, pack, row) {
  if (blank(row.fix) || PLACEHOLDER_FIX.test(row.fix)) return null;
  const text = `${row.issue} ${row.fix}`;
  const cards = list(pack.testCards).filter((card) => citesId(text, card.id)).map((card) => card.id);
  const rules = list(pack.rules).filter((rule) => citesId(text, rule.id)).map((rule) => rule.id);
  const skip = new Set([...REVIEW_SHEETS, 'Workbook Validation']);
  const sheets = (ctx.builder.SHEET_ORDER ?? ['Coverage Matrix', 'Assumptions'])
    .filter((sheet) => !skip.has(sheet) && namesSheet(text, sheet));
  const assumptions = sheets.includes('Assumptions') || /\bassumptions?\b/i.test(text);
  if (!cards.length && !rules.length && !sheets.length && !assumptions) return null;
  return { cards, rules, sheets, assumptions };
}

/** The findings a fix can act on, each with what it names and the text the repair reads. */
function fixableFindings(ctx, pack, rows) {
  return rows.flatMap((row) => {
    const to = fixTargets(ctx, pack, row);
    if (!to) return [];
    // A rule's cards ride in the text, so the repair shows them for a finding that names the rule only.
    const cites = to.rules.flatMap((id) => {
      const ids = list(pack.testCards).filter((card) => list(card.rules).includes(id)
        && !to.cards.includes(card.id)).map((card) => card.id).slice(0, 3);
      return ids.length ? [`  Cards that cite ${id}: ${ids.join(', ')}`] : [];
    });
    const text = [`- ${row.issue}`, ...(row.section ? [`  Section: ${row.section}`] : []),
      `  Fix: ${row.fix}`, ...cites].join('\n');
    return [{ row, to, text }];
  });
}

/**
 * Logs one `repair` line for each finding of a repair call: what the finding asked for
 * (`new-card`, `card`, `coverage`, `assumption` or `sheet`), what the repair returned for
 * it (corrected `cards`, offered `newCards`, `coverageRows` and `limitations`), and
 * whether that was `applied`, `undone` (everything returned was taken back out) or `empty`
 * (nothing came back for it). A finding is matched to the reply by the cards, rules and
 * sheets it names. `check` names the Revalidation check of a finding from the revalidation.
 * `split` holds the `part` and `parts` of a finding split across calls, which gets a line
 * for each part.
 */
function noteRepairs(ctx, group, step, label, returned, firstFinding, split = {}) {
  for (const [i, { row, to, text }] of group.entries()) {
    const asks = to.rules.length > 0 && !to.cards.length && ASKS_NEW_CARD.test(text);
    const ownsRule = (id) => to.rules.includes(id) || to.sheets.includes('Coverage Matrix');
    const cards = returned.cards.filter((id) => to.cards.includes(id));
    const offered = returned.newCards.filter((card) => asks && list(card.rules).some((id) => to.rules.includes(id)));
    const keptNew = returned.keptNewCards.filter((card) => asks && card.rules.some((id) => to.rules.includes(id)));
    const coverageRows = returned.coverage.filter(ownsRule).length;
    const limitations = returned.limitations.filter((sheet) => to.sheets.includes(sheet)).length;
    const undone = returned.undone.filter((id) => to.cards.includes(id)).length;
    const assumptions = to.assumptions ? returned.assumptions : 0;
    const came = cards.length + offered.length + coverageRows + limitations + assumptions;
    const taken = undone + (offered.length - keptNew.length);
    ctx.logs.status({ job: ctx.job.id, phase: 'phase8', step: `repair-${step}`, event: 'repair',
      finding: firstFinding + i + 1, ...split, ...(label === 'revalidation' ? { check: row.section } : {}),
      asked: asks ? 'new-card' : to.cards.length ? 'card' : to.rules.length || to.sheets.includes('Coverage Matrix')
        ? 'coverage' : to.assumptions ? 'assumption' : 'sheet',
      cards: cards.length, newCards: offered.length, coverageRows, limitations, assumptions,
      result: !came ? 'empty' : taken >= cards.length + offered.length && !coverageRows && !limitations && !assumptions
        ? 'undone' : 'applied' });
  }
}

/**
 * Records, for each finding that asks for a new card, whether a rule it names is still
 * without one. The status log says so, and the finding stays open with the reason.
 */
function noteUnapplied(ctx, pack, group, step) {
  ctx.unapplied ??= {};
  for (const { row, to, text } of group) {
    const asks = to.rules.length && !to.cards.length && ASKS_NEW_CARD.test(text);
    const bare = to.rules.some((id) => !list(pack.testCards).some((card) => list(card.rules).includes(id)));
    if (!asks || !bare) {
      delete ctx.unapplied[row.section];
      continue;
    }
    ctx.unapplied[row.section] = ctx.job.suite ? 'a suite pack takes no new card' : 'repair produced no card';
    ctx.logs.status({ job: ctx.job.id, phase: 'phase8', step: `repair-${step}`, event: 'repair-not-applied',
      reason: ctx.job.suite ? 'new-card-refused-suite' : 'no-card' });
  }
}

/** What remains of a finding says this when a repair reply for it was cut off. */
const CUT_REASON = 'a repair reply was cut off at its output budget';

/**
 * One repair of findings: the repair calls, the pack's edits that came from the
 * review kept, the rebuild, and the findings noted as attempted. A coverage row
 * or limitation changes only for a rule or sheet a finding names; every other
 * one stays as the pack had it, so a false finding cannot downgrade a rule or
 * add a limitation.
 *
 * `fixCalls` sets what each call is given, and a `repair-call` line says so before the
 * call: the first finding it holds, how many findings, how many cards, and which part of
 * a finding split across calls. In the revalidation round a reply cut off at its output
 * budget leaves its finding open and logs a `repair-cut` line with the length of the cut
 * reply and the whole cards it held, and the other findings' repairs stand; when no call
 * of the round answered, the cut fails the round. A cut in a checklist round fails it.
 */
async function fixRound(ctx, pack, findings, label, deferred, firstFinding = 0) {
  const kept = structuredClone({ coverage: pack.coverage, limitations: pack.limitations });
  const allow = { rules: new Set(), sheets: new Set() };
  for (const { to } of findings) {
    to.rules.forEach((id) => allow.rules.add(id));
    to.sheets.forEach((sheet) => allow.sheets.add(sheet));
    if (to.sheets.includes('Coverage Matrix')) list(pack.rules).forEach((rule) => allow.rules.add(rule.id));
  }
  const single = label === 'revalidation';
  const answered = new Set();
  const cut = new Map();
  for (const [n, { items, only, cards, part, parts }] of fixCalls(ctx, pack, findings, single).entries()) {
    const step = `${label}-g${n + 1}`;
    const first = firstFinding + findings.indexOf(items[0]);
    const line = { job: ctx.job.id, phase: 'phase8', step: `repair-${step}`, finding: first + 1, cards, part, parts };
    ctx.logs.status({ ...line, event: 'repair-call', findings: items.length });
    // A finding split across calls takes new cards and assumptions in its first call only.
    const returned = await repair(ctx, pack, { failed: [failedSheet(REVIEW_SHEET,
      items.map((item) => item.text).join('\n'))], validation: [] }, step,
    { assumptions: part === 1 && items.some((item) => item.to.assumptions), newCards: part === 1, only,
      cutOk: single });
    if (returned.cut) {
      for (const item of items) cut.set(item, returned.cut);
      const reply = returned.cut.partial;
      ctx.logs.status({ ...line, event: 'repair-cut', ...(typeof reply === 'string'
        ? { replyChars: reply.length, wholeCards: wholeItems(reply, 'cards') } : {}) });
      continue;
    }
    items.forEach((item) => answered.add(item));
    noteRepairs(ctx, items, step, label, returned, first, parts > 1 ? { part, parts } : {});
    // A finding with a cut part keeps the cut as its reason, whatever its other parts returned.
    if (part === parts && !items.some((item) => cut.has(item))) noteUnapplied(ctx, pack, items, step);
  }
  if (cut.size && !answered.size) throw cut.values().next().value;
  ctx.unapplied ??= {};
  for (const { row } of cut.keys()) ctx.unapplied[row.section] = CUT_REASON;
  // The review's prose was written before these repairs, and the pack says so where a person reads it.
  if (single && answered.size) noteNarrativeAge(pack);
  keepReviewEdits(pack, kept, allow);
  await phase8(ctx, pack, label, deferred);
  ctx.appliedFixes ??= [];
  for (const item of findings) {
    if (!answered.has(item)) continue;
    const line = `- ${item.row.issue} (fix: ${item.row.fix})`;
    if (!ctx.appliedFixes.includes(line)) ctx.appliedFixes.push(line);
  }
}

const DENIES_COVERAGE = ['Missing', 'Not Applicable'];

/**
 * Puts back the coverage rows and limitations the review did not ask to change.
 * A row for a rule a finding names stays unless its status contradicts the
 * cards: a Missing row for a rule cards cite, or a covered row for one no card cites.
 */
function keepReviewEdits(pack, kept, allow) {
  const cited = new Set(list(pack.testCards).flatMap((card) => list(card.rules)));
  const impacted = new Set(list(pack.rules).filter((rule) => rule.impact !== 'Not Impacted')
    .map((rule) => rule.id));
  const before = new Map(list(kept.coverage).map((row) => [row.ruleId, row]));
  const contradicting = (row) => impacted.has(row.ruleId)
    && DENIES_COVERAGE.includes(row.status) === cited.has(row.ruleId);
  pack.coverage = list(pack.coverage).map((row) => {
    const old = before.get(row.ruleId);
    if (allow.rules.has(row.ruleId) && !contradicting(row)) return row;
    // An old row that contradicts the cards now is dropped, so the build writes the true one.
    return old && contradicting(old) ? null : (old ?? row);
  }).filter(Boolean);
  const limitations = { ...kept.limitations };
  for (const sheet of allow.sheets) {
    if (!blank(pack.limitations?.[sheet])) limitations[sheet] = pack.limitations[sheet];
  }
  pack.limitations = limitations;
}

/**
 * The repair calls of a fix round, in order: the findings each is given (`items`), how many
 * cards those name (`cards`), and for a finding split across calls the cards of this call
 * (`only`) and which `part` of how many `parts` it is. No call is given more cards than
 * `repairCardsMax`, so its reply fits the output budget: a finding that names more is split
 * into calls of its own. With `single` every finding gets a call of its own, as the
 * revalidation round asks; otherwise findings share a call while their named cards fit
 * the prompt and stay within that count.
 */
function fixCalls(ctx, pack, findings, single) {
  const budget = Math.max(1000, room(ctx, false, [ctx.ref.docs.workbookStandard]) - 3000);
  const max = repairCardsMax(ctx);
  const cost = (item, named) => estimateTokens(item.text) + named
    .reduce((n, card) => n + estimateTokens(repairCardText(card)) + estimateTokens(asLines(
      list(pack.rules).filter((rule) => list(card.rules).includes(rule.id)).map(ruleLine))), 0);
  const calls = [];
  let open = null;
  for (const item of findings) {
    const named = namedCards(pack, item.text);
    const ids = named.map((card) => card.id);
    if (ids.length > max) {
      const parts = Math.ceil(ids.length / max);
      for (let part = 1; part <= parts; part += 1) {
        const only = ids.slice((part - 1) * max, part * max);
        calls.push({ items: [item], only, cards: only.length, part, parts });
      }
      open = null;
      continue;
    }
    const size = cost(item, named);
    if (single || !open || open.size + size > budget || new Set([...open.ids, ...ids]).size > max) {
      open = { items: [], ids: new Set(), size: 0 };
      calls.push(open);
    }
    open.items.push(item);
    ids.forEach((id) => open.ids.add(id));
    open.size += size;
  }
  return calls.map((call) => (call.only ? call
    : { items: call.items, only: null, cards: call.ids.size, part: 1, parts: 1 }));
}

/**
 * The prose fields of the review sheets, as { name, text } rows: the Confidence
 * Assessment fields, the senior review answers and the tester notes.
 */
function reviewProse(pack) {
  const text = (value) => (Array.isArray(value) ? value.join(' ') : String(value ?? '')).trim();
  return [['Confidence Assessment', pack.confidence], ['Senior Tester Review', pack.seniorReview],
    ['Tester Notes', pack.testerNotes]].flatMap(([sheet, fields]) => Object.entries(fields ?? {})
    .filter(([field]) => field !== 'overall')
    .map(([field, value]) => ({ name: `${sheet} ${field}`, text: text(value) })));
}

// A short answer such as "Not applicable." or "None." is the right answer for more than one
// field, so only a text this long counts as one field repeating another.
const TWIN_MIN_CHARS = 40;
const sameText = (a, b) => {
  const flat = (text) => text.toLowerCase().split(/\s+/).join(' ');
  return flat(a).length >= TWIN_MIN_CHARS && flat(a) === flat(b);
};

/** The card and rule IDs a text cites that the pack does not hold, among the ID families it uses. */
function unknownIds(pack, text) {
  const known = new Set([...list(pack.testCards), ...list(pack.rules)].map((item) => item.id));
  const families = [...new Set([...known].map((id) => id.replace(/\d+$/, '')).filter((f) => f && f.endsWith('-')))];
  if (!families.length) return [];
  const escaped = families.map((family) => family.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const cited = String(text).match(new RegExp(`(?<![A-Za-z0-9.-])(?:${escaped.join('|')})\\d+`, 'g')) ?? [];
  return [...new Set(cited.filter((id) => !known.has(id)))];
}

/** What is wrong with one new field's text, or '': it repeats a field already written, or cites what the workbook lacks. */
function fieldProblem(pack, text, earlier) {
  if (!String(text ?? '').trim()) return 'it is blank';
  const twin = earlier.find((row) => row.text && sameText(row.text, String(text)));
  if (twin) return `it repeats the text of ${twin.name}; say something specific to this field`;
  const unknown = unknownIds(pack, text);
  if (unknown.length) return `it cites ${unknown.join(', ')}, which the workbook does not hold`;
  return '';
}

/** The card and rule IDs of the pack that `text` names. */
const citedIds = (pack, text) => [...list(pack.testCards), ...list(pack.rules)]
  .map((item) => item.id).filter((id) => citesId(String(text), id));

/** fieldProblem, plus what a Confidence Assessment field owes: a sentence that names a rule or card. */
function confidenceFieldProblem(pack, text, earlier, { needsId = true } = {}) {
  const problem = fieldProblem(pack, text, earlier);
  if (problem) return problem;
  const flat = String(text).trim();
  if (flat.length < S.CONFIDENCE_FIELD_MIN_CHARS) {
    return `it is too short to be an assessment (under ${S.CONFIDENCE_FIELD_MIN_CHARS} characters)`;
  }
  const hasIds = list(pack.testCards).length + list(pack.rules).length > 0;
  if (needsId && hasIds && !citedIds(pack, flat).length) return 'it names no rule or card of the workbook by ID';
  return '';
}

/** One confidence field, asked for on its own over the finished workbook; a refused text is asked for once more. */
async function writeConfidenceField(ctx, pack, field, task, extra) {
  // An honest answer can name no ID: a pack with no assumptions, or nothing left to check by hand.
  const needsId = !(field === 'manualReview' || (field === 'assumptions' && !list(pack.assumptions).length));
  let refusal = '';
  for (let attempt = 0; attempt < 2; attempt += 1) {
    const earlier = reviewProse(pack);
    // The fields already written ride in `extra`, so the workbook is sized with them in view.
    const input = reviewInputs(ctx, pack, [...extra,
      ['Fields already written', asLines(earlier.map((row) => `- ${row.name}: ${row.text}`))]]);
    const answer = await ask(ctx, {
      phase: 'phase9', step: `confidence-${field}`, reasoning: false,
      ...input,
      task: `${task} Give no count of cards, rules or coverage statuses; the Coverage field carries`
        + ` the counts.${refusal}`,
      schema: S.confidenceFieldSchema(field),
    });
    const problem = confidenceFieldProblem(pack, answer[field], earlier, { needsId });
    if (!problem) return String(answer[field]).trim();
    refusal = ` Your last answer for this field was refused: ${problem}.`;
  }
  throw new GateError('phase9', 'review-field-unsupported');
}

/** What each Confidence Assessment field says, in the order they are written. Coverage is counted in code. */
const CONFIDENCE_FIELDS = [
  ['remainingRisks', 'Name the risks that remain after these cards, each tied to a rule or card ID in the workbook.'],
  ['assumptions', 'Summarize the assumptions this pack rests on, from its Assumptions sheet, naming the rule or card IDs each one touches.'],
  ['regressionScope', 'Say what regression coverage the pack gives: which rule and card IDs guard behavior the change does not touch.'],
  ['breakItScope', 'Say what break-it coverage the pack gives, naming its break-it card IDs, and what it does not try. When the pack has no break-it cards, say so and name the rules left without one.'],
  ['manualReview', 'Say what a person must still check by hand, and why the pack cannot, naming the rule or card IDs concerned.'],
];

const COVERED = 'Covered';
const coverageRows = (ctx, pack) => (ctx.builder?.ruleCoverage
  ? ctx.builder.ruleCoverage(pack).map((row) => ({ id: row.rule.id, status: row.status }))
  : list(pack.coverage).map((row) => ({ id: row.ruleId, status: row.status })));

/**
 * The Coverage field, counted from the Coverage Matrix rather than written by a model:
 * how many rules sit in each status and which rules are not Covered.
 */
export function coverageText(ctx, pack) {
  const rows = coverageRows(ctx, pack);
  if (!rows.length) return 'The Coverage Matrix lists no rules.';
  const byStatus = new Map();
  for (const row of rows) byStatus.set(row.status, [...(byStatus.get(row.status) ?? []), row.id]);
  const parts = [...byStatus.entries()].map(([status, ids]) => (status === COVERED
    ? `${ids.length} ${status}`
    : `${ids.length} ${status} (${ids.join(', ')})`));
  return `Of ${rows.length} rule(s) in the Coverage Matrix: ${parts.join('; ')}.`;
}

/** The coverage step's verdict, from the same counts. */
function coverageVerdict(ctx, pack) {
  const open = coverageRows(ctx, pack)
    .filter((row) => row.status !== COVERED && row.status !== 'Not Applicable');
  if (!open.length) return 'strong';
  return open.some((row) => row.status === 'Missing') ? 'weak' : 'partial';
}

/** An assessment step as it stands: the coverage step takes its verdict and evidence from the counts. */
const coverageStep = (ctx, pack, row) => (row.step === 'coverage'
  ? { ...row, verdict: coverageVerdict(ctx, pack), evidence: coverageText(ctx, pack) } : row);

/** Every card with the rules it cites, one line each, so a field can name them by ID. */
const cardsText = (pack) => asLines(list(pack.testCards)
  .map((card) => `- ${card.id} | ${card.derivation} | ${list(card.rules).join(', ') || 'no rule'}`));

const STEP_NAMES = {
  rules: 'every impacted rule is identified and rated',
  decisions: 'the assumptions and choices the pack rests on are sound',
  coverage: 'the cards cover the rules',
  regression: 'behavior the change does not touch is guarded',
  qualityDerived: 'cards derived from the quality objectives are present',
  breakIt: 'negative and boundary cards are present',
  professionalReview: 'the senior review left nothing unresolved',
  residualRisk: 'what remains is named and acceptable',
};

/**
 * The assessment steps walked in one call, a verdict and evidence for each. The
 * coverage verdict is set from the Coverage Matrix counts, whatever the call says.
 */
async function walkConfidenceSteps(ctx, pack, extra) {
  const answer = await ask(ctx, {
    phase: 'phase9', step: 'confidence-steps', reasoning: true,
    ...reviewInputs(ctx, pack, extra),
    task: 'Walk the confidence assessment steps of the methodology, in order:\n'
      + `${S.CONFIDENCE_STEPS.map((step) => `- ${step}: ${STEP_NAMES[step]}`).join('\n')}\n`
      + 'Give each step a verdict (strong, partial or weak) and its evidence in one sentence'
      + ' that names the rule or card IDs it rests on. Code fills in the coverage step from the'
      + ' Coverage Matrix, so give it a short placeholder.',
    schema: S.confidenceStepsSchema,
  });
  const rows = list(answer.steps).map((row) => coverageStep(ctx, pack, row));
  ctx.private('phase9-confidence.json', { steps: rows });
  return rows;
}

/**
 * Rates `overall` last, from the steps, the checklist, the senior review and any
 * revalidation items still open. Every level carries its reason, which opens the
 * Executive Summary's confidence after the level; a Low rating also writes the limitation.
 * The call is told the confidence ceiling and offered only the levels at or under it, and a
 * level above it is lowered to it in code. A `confidence` line logs what set the level: the
 * level the call gave, what held it lower (untested objectives or the confidence ceiling),
 * and the counts of weak and partial steps, open revalidation items, checklist issues and
 * untested objectives it was rated from. `again` marks the rating after the revalidation repair.
 */
async function rateOverall(ctx, pack, extra, steps, again = false) {
  const ceiling = confidenceCeiling(ctx, pack);
  let refusal = '';
  let overall;
  for (let attempt = 0; attempt < 2; attempt += 1) {
    overall = await askOverall(ctx, pack, extra, steps, refusal, ceiling);
    const [wrong] = otherLevels(overall);
    if (!wrong) break;
    refusal = ` Your last reason was refused: it states "confidence is ${wrong[1]}" and the rating`
      + ` is ${overall.overall}. Leave levels out of the reason.`;
  }
  // An objective left untested caps the rating below the highest level, whatever the call says.
  const untested = droppedList(ctx);
  const [highest, next] = ctx.builder.CONFIDENCE_LEVELS;
  const asked = overall.overall;
  const capped = untested.length > 0 && asked === highest && Boolean(next);
  if (capped) {
    overall.overall = next;
    overall.reason = `${overall.reason} No test card serves ${untested.join(', ')}, so the pack leaves`
      + ` ${untested.length > 1 ? 'those objectives' : 'that objective'} untested.`;
  }
  const held = overCeiling(ctx, ceiling, overall.overall);
  if (held) {
    overall.overall = ceiling.level;
    overall.reason = `${overall.reason} ${ceilingNote(ceiling)}`;
  }
  const cappedBy = held ? CEILING_CODE : capped ? 'untested-objectives' : 'none';
  const verdicts = (verdict) => list(steps).filter((row) => row.verdict === verdict).length;
  ctx.logs.status({ job: ctx.job.id, phase: 'phase9', step: `confidence-overall${again ? '-again' : ''}`,
    event: 'confidence', overall: overall.overall, asked, cappedBy,
    stepsWeak: verdicts('weak'), stepsPartial: verdicts('partial'),
    openItems: list(pack.revalidation?.remaining).length, checklistIssues: ctx.reviewIssues ?? 0,
    untested: untested.length });
  // A reason that still states another level after the second try, or after a lowering, loses those phrases.
  overall.reason = ownLevelOnly(overall);
  return applyRating(pack, overall);
}

const STATED_LEVEL = /\bconfidence\s+(?:level\s+)?(?:is|:)\s*(medium[\s-]high|low[\s-]medium|medium|high|low)\b/gi;

/** The "confidence is <level>" phrases of the reason that name a level other than the rating. */
const otherLevels = ({ reason, overall }) => [...String(reason).matchAll(STATED_LEVEL)]
  .filter((match) => match[1].toLowerCase() !== String(overall).toLowerCase());

/** The reason with each such phrase cut to "confidence", so the text states no level but the rating's. */
const ownLevelOnly = ({ reason, overall }) => otherLevels({ reason, overall })
  .reduce((text, match) => text.replace(match[0], 'confidence'), String(reason));

function askOverall(ctx, pack, extra, steps, refusal, ceiling) {
  const [highest] = ctx.builder.CONFIDENCE_LEVELS;
  const limit = ceiling.level === highest ? ''
    : ` The highest level this pack supports is ${ceiling.level}`
      + `${ceiling.reasons.length ? `, because ${ceiling.reasons.join('; ')}` : ''}. Do not rate it higher.`;
  return ask(ctx, {
    phase: 'phase9', step: 'confidence-overall', reasoning: true,
    ...reviewInputs(ctx, pack, [...extra,
      ['Assessment steps', asLines(steps.map((row) => `- ${row.step}: ${row.verdict}. ${row.evidence}`))]]),
    task: 'Rate overall confidence in this pack from the assessment steps, the criteria for each'
      + ' level in the methodology, the checklist issues, the senior review and any open'
      + ' revalidation items. Give the reason for the rating at every level, in sentences that'
      + ' name the rule or card IDs behind it, and list the criteria of the level you chose that'
      + ' the pack meets. An objective listed as applicable but untested is a coverage gap and rules'
      + ` out the highest level.${limit} Do not state a confidence level in the reason; the rating field holds it.` + refusal,
    schema: S.confidenceOverallSchema({ confidence: ceiling.allowed }),
  });
}

/** The reason code a status line gives when the confidence ceiling set the level. */
const CEILING_CODE = 'confidence-ceiling';

/**
 * The confidence ceiling: the highest overall level the builder accepts for the pack as it
 * stands (`level`), the levels at or under it (`allowed`), and what the builder says holds
 * it there (`reasons`). The builder's optional `confidenceCeiling(pack)` export gives
 * `{ level, reasons }`. A builder without it, or one that names a level outside its own
 * list, sets no ceiling: every level is allowed.
 */
export function confidenceCeiling(ctx, pack) {
  const levels = list(ctx.builder?.CONFIDENCE_LEVELS);
  const found = ctx.builder?.confidenceCeiling?.(pack);
  const at = Math.max(levels.indexOf(found?.level), 0);
  return { level: levels[at], allowed: levels.slice(at),
    reasons: at > 0 ? list(found.reasons).map((reason) => String(reason).trim()).filter(Boolean) : [] };
}

/** True for a level of the builder's list that sits above the ceiling. */
const overCeiling = (ctx, ceiling, level) => list(ctx.builder?.CONFIDENCE_LEVELS).includes(level)
  && !ceiling.allowed.includes(level);

const CEILING_NOTE = 'The rating was lowered to what the pack supports';

/** The sentence a lowered rating's reason ends with, naming what the builder says holds the level down. */
const ceilingNote = (ceiling) => (ceiling.reasons.length
  ? `${CEILING_NOTE}: ${ceiling.reasons.map(noStop).join('; ')}.` : `${CEILING_NOTE}.`);

/**
 * Holds a rated pack to its confidence ceiling without a model call. A level above the
 * ceiling becomes the ceiling, the reason ends with one sentence naming what holds it
 * there, and the Executive Summary and the Low limitation follow. A `confidence-lowered`
 * status line gives the level the pack had (`asked`), the level applied (`overall`) and the
 * reason code; `log: false` leaves it out. An unrated pack, or one at or under its
 * ceiling, is left as it is.
 */
export function holdToCeiling(ctx, pack, { log = true } = {}) {
  const asked = pack.confidence?.overall;
  const ceiling = confidenceCeiling(ctx, pack);
  if (!overCeiling(ctx, ceiling, asked)) return;
  // A reason lowered before keeps one such sentence, the one for the ceiling it sits at, and
  // the reason a rating with none was given names the level it had, so it goes.
  const before = String(pack.confidence.reason ?? '').split(CEILING_NOTE)[0].trim();
  const said = before === plainReason(asked) ? '' : ownLevelOnly({ reason: before, overall: ceiling.level });
  applyRating(pack, { overall: ceiling.level, reason: [said, ceilingNote(ceiling)].filter(Boolean).join(' ') });
  if (log) {
    ctx.logs?.status({ job: ctx.job?.id, phase: 'phase9', step: 'confidence-ceiling', event: 'confidence-lowered',
      overall: ceiling.level, asked, reason: CEILING_CODE });
  }
}

/** The reason a rating carries when it was given none. */
const plainReason = (level) => `Overall confidence is ${level}.`;

/** The rating and its reason on the pack: the Executive Summary line, and the limitation for Low. */
function applyRating(pack, overall) {
  const reason = String(overall.reason ?? '').trim()
    || `Overall confidence is ${overall.overall}.`;
  pack.confidence = { ...pack.confidence, overall: overall.overall, reason };
  pack.limitations ??= {};
  if (overall.overall === 'Low') pack.limitations['Confidence Assessment'] = reason;
  else delete pack.limitations['Confidence Assessment'];
  if (pack.executiveSummary) pack.executiveSummary.confidence = `${overall.overall}. ${reason}`;
  return overall.overall;
}

/** What the confidence calls read beyond the workbook: checklist issues, cards, the senior review. */
const confidenceExtra = (ctx, pack) => [['Checklist issues', issueText(ctx)],
  ['Cards and the rules they cite', cardsText(pack)],
  ['Senior review', JSON.stringify({ seniorReview: pack.seniorReview, testerNotes: pack.testerNotes })],
  ['Revalidation items still open', list(pack.revalidation?.remaining).join('\n')],
  ['Objectives applicable but untested', droppedList(ctx).join('\n') || 'none']];

/**
 * The confidence assessment, written last, after the checklist, the fix rounds and the
 * senior review. The Coverage field is counted in code, each other field is a call of
 * its own, the assessment steps get a verdict each, and the overall level comes last
 * with a reason. The overall level stays unset while the fields are written, so the
 * draft workbook they read builds.
 */
export async function phase9Confidence(ctx, pack) {
  const extra = confidenceExtra(ctx, pack);
  pack.limitations ??= {};
  delete pack.limitations['Confidence Assessment'];
  pack.confidence = { coverage: coverageText(ctx, pack) };
  for (const [field, task] of CONFIDENCE_FIELDS) {
    pack.confidence[field] = await writeConfidenceField(ctx, pack, field, task, extra);
  }
  const steps = await walkConfidenceSteps(ctx, pack, extra);
  ctx.confidenceSteps = steps;
  const level = await rateOverall(ctx, pack, extra, steps);
  return { confidence: level };
}

/**
 * Rates again when revalidation leaves items open; the fields and the senior review stand.
 * The coverage step is counted again first, so the rating reads the Coverage Matrix as the
 * repairs left it.
 */
export async function reRateConfidence(ctx, pack) {
  ctx.confidenceSteps = list(ctx.confidenceSteps).map((row) => coverageStep(ctx, pack, row));
  return rateOverall(ctx, pack, confidenceExtra(ctx, pack), ctx.confidenceSteps, true);
}

/** The two parts of the senior review, each asked in a call of its own. */
const SENIOR_PARTS = [
  { step: 'senior-review', sheet: 'Senior Tester Review', key: 'seniorReview', schema: S.seniorReviewSchema },
  { step: 'senior-notes', sheet: 'Tester Notes', key: 'testerNotes', schema: S.testerNotesSchema },
];

/**
 * One part of the senior review. The fields of the parts before it ride in the input, so the
 * part does not restate them. An answer with a field that repeats another or cites a card or
 * rule the workbook lacks is asked for once more with what was wrong; the accepted fields join
 * `earlier` only when the whole part is accepted.
 */
async function askSeniorPart(ctx, pack, part, shared, earlier) {
  const input = reviewInputs(ctx, pack, [...shared, ...(earlier.length
    ? [['Fields already written', asLines(earlier.map((row) => `- ${row.name}: ${row.text}`))]] : [])]);
  const fieldNames = Object.keys(part.schema.properties[part.key].properties).join(', ');
  let refusal = '';
  for (let attempt = 0; attempt < 2; attempt += 1) {
    const answer = await ask(ctx, {
      phase: 'phase9', step: part.step, reasoning: true, ...input,
      task: 'Answer the senior review questions for this pack and write the tester notes. Each'
        + ' field says something of its own and names only cards and rules in the workbook.',
      question: `Write the ${part.sheet} fields: ${fieldNames}.${refusal}`,
      schema: part.schema,
    });
    const accepted = [...earlier];
    const problems = [];
    for (const [field, text] of Object.entries(answer[part.key])) {
      const name = `${part.sheet} ${field}`;
      const flat = Array.isArray(text) ? text.join(' ') : text;
      const problem = fieldProblem(pack, flat, accepted);
      if (problem) problems.push(`${name}: ${problem}`);
      else accepted.push({ name, text: String(flat).trim() });
    }
    if (!problems.length) {
      earlier.push(...accepted.slice(earlier.length));
      return answer[part.key];
    }
    refusal = ` Your last answer was refused: ${problems.join('; ')}.`;
  }
  throw new GateError('phase9', 'review-field-unsupported');
}

/**
 * The senior review questions and the tester notes, written before the confidence
 * assessment, which reads them, with the checklist's issues in view. Each part is a call
 * of its own, so no one call thinks through both; the pack is written once both are accepted.
 */
export async function phase9SeniorReview(ctx, pack) {
  const shared = [['Checklist issues', issueText(ctx)],
    impactsInput(ctx, pack, true, [...ctx.ref.core, ctx.ref.docs.validation, ...ctx.ref.chapters('9')])];
  const earlier = [];
  const written = {};
  for (const part of SENIOR_PARTS) written[part.key] = await askSeniorPart(ctx, pack, part, shared, earlier);
  pack.seniorReview = written.seniorReview;
  pack.testerNotes = written.testerNotes;
  if (ctx.reuse.length) {
    pack.testerNotes.execution = [...list(pack.testerNotes.execution), ...ctx.reuse];
  }
  return {};
}

/**
 * The answers of every part of the workbook, one verdict per Revalidation check. A
 * check one part fails fails the pack; one a part passes and the others do not show
 * passes; one no part shows fails, as not evidenced.
 */
export function mergeChecks(answers, names = S.REVALIDATION_CHECKS) {
  const checks = names.map((check) => {
    const rows = answers.flatMap((answer) => list(answer.checks).filter((row) => row.check === check));
    const failed = rows.filter((row) => row.verdict === 'fail');
    if (failed.length) {
      return { check, verdict: 'fail', why: failed.map((row) => row.why).join(' '),
        fix: failed.map((row) => row.fix).filter((fix) => !blank(fix)).join(' ') };
    }
    if (rows.some((row) => row.verdict === 'pass')) return { check, verdict: 'pass', why: '', fix: '' };
    return { check, verdict: 'fail', why: 'Not evidenced in any part of the workbook.', fix: '' };
  });
  const remaining = checks.filter((row) => row.verdict === 'fail').map((row) => `${row.check}: ${row.why}`);
  return { passed: !remaining.length, checks, remaining };
}

/** The input a walk reads the open checklist findings under. */
const OPEN_FINDINGS_LABEL = 'Checklist findings still open after the last check';

/** The sheets whose prose the review writes once, before the revalidation. */
const NARRATIVE_SHEETS = [...SENIOR_PARTS.map((part) => part.sheet), 'Confidence Assessment'];

/**
 * The note the pack carries, in its manual review field, once a revalidation repair has
 * changed it after the review's prose was written.
 */
const REPAIRED_NOTE = `The ${NARRATIVE_SHEETS.slice(0, -1).join(', the ')}, the written fields of`
  + ' this assessment, the scope of each test set and the assumptions the pack already held were'
  + ' written before the last corrections to the pack. Check what they say of a card, a rule or a'
  + ' count against the test cards and the Coverage Matrix as they now stand.';

/** True when the pack says a revalidation repair changed it after its prose was written. */
const narrativeAged = (pack) => String(pack.confidence?.manualReview ?? '').includes(REPAIRED_NOTE);

/** Adds that note to the manual review field, once, when the field is written. */
function noteNarrativeAge(pack) {
  if (blank(pack.confidence?.manualReview) || narrativeAged(pack)) return;
  pack.confidence.manualReview = `${String(pack.confidence.manualReview).trim()} ${REPAIRED_NOTE}`;
}

/** What a walk after a repair round is told about the text that round did not write again. */
const AGED_TEXT = 'These were written before the repair round and describe the pack as it stood'
  + ` then: the ${NARRATIVE_SHEETS.slice(0, -1).join(', the ')}, the written fields of the`
  + ` ${NARRATIVE_SHEETS.at(-1)}, the assumptions the pack held before the round, the scope text of`
  + ` each test set, and the findings under "${OPEN_FINDINGS_LABEL}". A card they call missing,`
  + ' vague or wrong, or a count of cards or coverage they give, is not evidence that a finding is'
  + ' still open. Judge the state of the pack from what the repairs can change, as the workbook'
  + ' shows it now: the cards, the rule and coverage matrices, the objectives and the test sets'
  + ' with the cards each holds, and the upload sheet. A gap that an assumption or a limitation'
  + ' documents is still documented, whenever it was written. Never fail a check, or give a fix,'
  + ' only because one of those earlier texts no longer matches the pack.';

/**
 * One walk of the Revalidation checks named in `names` (all seven by default) over the
 * finished workbook, in parts when it is long. Each group of checks that read the same
 * sheets is a call of its own under its own reasoning budget (`revalidation-<group>`, and
 * `-again` after the repair round). Every call of a part carries the same prompt up to its
 * question, which names the group, so the server reads the workbook once for the groups.
 * Every call is given the design rules as facts it fails no check on. A walk after a
 * repair round, `again` or over a pack that carries the repair's note, is also told which
 * text was written before that round and is no evidence of an open finding.
 * Each check's merged verdict is logged as a `check` line, with whether every call that
 * judged it ran with thinking on and whether the verdict came with a fix. With `earlier`,
 * the verdicts of the walk before the repair round, a failed check's line also says
 * whether that walk failed it too (`repeat`).
 */
async function walkChecks(ctx, pack, { again = false, names = S.REVALIDATION_CHECKS, earlier = null } = {}) {
  const refs = [...ctx.ref.core, ctx.ref.docs.revalidation];
  const extra = [['Fixes the review attempted (judge the workbook, not the attempt)',
    list(ctx.appliedFixes).join('\n')],
  [OPEN_FINDINGS_LABEL, openText(ctx) || 'None.'],
  designRulesInput(ctx, pack, 'The pipeline builds every pack by these rules. They are facts about this'
    + ' pack, not findings: never fail a check because the pack follows one, and never give a fix'
    + ' that would break one.'),
  ['Text written before the repair round', again || narrativeAged(pack) ? AGED_TEXT : '']];
  const views = reviewViews(ctx, pack, refs, extra, { review: true });
  const groups = S.REVALIDATION_GROUPS
    .map((group) => ({ ...group, checks: group.checks.filter((check) => names.includes(check)) }))
    .filter((group) => group.checks.length);
  const answers = [];
  const thinking = new Map();
  for (const view of views) {
    for (const group of groups) {
      const outcome = {};
      answers.push(await ask(ctx, {
        phase: 'phase9', step: `revalidation-${group.key}${again ? '-again' : ''}`, reasoning: true, refs, outcome,
        task: 'Revalidate the pack after the review\'s fixes. Give a verdict for each Revalidation'
          + ' check the question names, with the reason first. For a check that fails, give the fix: the'
          + ' card, rule or sheet to change and what to change it to; leave it blank when no change'
          + ' to the pack can settle it.'
          + (views.length > 1 ? ` The workbook comes in ${views.length} parts; judge what this part`
            + ` shows, answer "${S.NOT_SHOWN}" for a check it does not show, and judge a rule's`
            + ' coverage from the cards the rules index lists for it.' : ''),
        inputs: [['Change description', ctx.description], ...extra, ...view],
        question: `Judge ${group.checks.length === 1 ? 'this Revalidation check' : 'these Revalidation checks'},`
          + ` which read mainly ${group.reads}:\n${group.checks.map((check) => `- ${check}`).join('\n')}`,
        schema: S.revalidationSchema({ checks: group.checks, verdicts: views.length > 1
          ? ['pass', 'fail', S.NOT_SHOWN] : ['pass', 'fail'] }),
      }));
      for (const check of group.checks) thinking.set(check, (thinking.get(check) ?? true) && outcome.thinking);
    }
  }
  const merged = mergeChecks(answers, names);
  const failedBefore = new Set(list(earlier).filter((row) => row.verdict === 'fail').map((row) => row.check));
  for (const row of merged.checks) {
    ctx.logs.status({ job: ctx.job.id, phase: 'phase9', event: 'check', walk: `revalidation${again ? '-again' : ''}`,
      check: row.check, verdict: row.verdict, thinking: thinking.get(row.check) ?? false,
      fixGiven: !blank(row.fix),
      ...(earlier && row.verdict === 'fail' ? { repeat: failedBefore.has(row.check) } : {}) });
  }
  return merged;
}

/**
 * Revalidation over the rebuilt workbook, review sheets included: each of the seven
 * Revalidation checks gets a verdict. A failed check whose fix names a card, a rule or
 * a sheet gets one repair round, a repair call for each such check, then the checks are
 * walked once more, with each check that still fails marked as failed before or new; a
 * repair the builder cannot build is undone and the first verdicts
 * stand. A check whose repair reply was cut off stays open and says so in what remains.
 * A pack that does not pass carries `revalidation` with what remains, which the builder
 * shows on its validation sheet as FAIL.
 */
export async function revalidate(ctx, pack) {
  let result = await walkChecks(ctx, pack);
  ctx.revalidationChecks = result.checks;
  let repaired = false;
  if (!result.passed) {
    const findings = revalidationFindings(ctx, pack);
    if (findings.length) {
      const before = structuredClone(pack);
      const appliedFixes = [...list(ctx.appliedFixes)];
      try {
        await fixRound(ctx, pack, findings, 'revalidation', []);
        repaired = true;
        result = await walkChecks(ctx, pack, { again: true, earlier: result.checks });
        ctx.revalidationChecks = result.checks;
        // A check whose repair built no card, or was cut off, carries that reason after its finding.
        result.remaining = result.remaining.map((line) => {
          const check = Object.keys(ctx.unapplied ?? {}).find((name) => line.startsWith(`${name}: `));
          return check ? `${line} (${ctx.unapplied[check]})` : line;
        });
      } catch (error) {
        if (!(error instanceof GateError)) throw error;
        ctx.appliedFixes = appliedFixes;
        for (const key of Object.keys(pack)) delete pack[key];
        Object.assign(pack, before);
        ctx.logs.status({ job: ctx.job.id, phase: 'phase8', step: 'repair-revalidation', event: 'repair-undone',
          reason: error.code, findings: findings.length });
        repaired = false;
      }
    }
  }
  const { passed, checks, remaining } = result;
  ctx.private('phase9-revalidation.json', { passed, checks, remaining, repaired });
  if (passed) delete pack.revalidation;
  else pack.revalidation = { passed: false, remaining };
  return { passed, remaining: remaining.length };
}

// ---------------------------------------------------------------------------
// Single steps: one part of Phase 9 on its own, over a saved state.

/**
 * The failed checks of the last revalidation walk that a repair can act on, in the
 * order the repair reads them: each names a card, a rule or a sheet to change.
 */
export function revalidationFindings(ctx, pack) {
  return fixableFindings(ctx, pack, list(ctx.revalidationChecks).filter((row) => row.verdict === 'fail')
    .map((row) => ({ section: row.check, issue: row.why, fix: row.fix })));
}

/**
 * One walk of the named Revalidation checks (all seven when none are named). The
 * verdicts replace those of the same checks in the last walk, so a state keeps
 * one verdict for each check walked, and `pack.revalidation` follows them once
 * all seven have a verdict.
 */
export async function walkSelected(ctx, pack, names = S.REVALIDATION_CHECKS) {
  const known = S.REVALIDATION_CHECKS;
  if (names.length < known.length && !ctx.revalidationChecks && pack.revalidation) {
    throw new StepInputError('this state holds no verdicts for the other checks; walk all seven first');
  }
  const result = await walkChecks(ctx, pack, { names });
  const checks = known.flatMap((check) => result.checks.find((row) => row.check === check)
    ?? list(ctx.revalidationChecks).filter((row) => row.check === check));
  ctx.revalidationChecks = checks;
  const remaining = checks.filter((row) => row.verdict === 'fail').map((row) => `${row.check}: ${row.why}`);
  if (checks.length === known.length) {
    ctx.private('phase9-revalidation.json', { passed: !remaining.length, checks, remaining, repaired: false });
    if (remaining.length) pack.revalidation = { passed: false, remaining };
    else delete pack.revalidation;
  }
  return { checks: result.checks, findings: revalidationFindings(ctx, pack).length, open: remaining.length };
}

/**
 * One repair round for finding `n` of `revalidationFindings`, then the rebuild. The
 * pack's revalidation result is cleared first, as the revalidation phase clears it
 * before its rebuild, so the builder does not read it as a failing sheet. The round
 * is one repair call, or one for each part of a finding that names more cards than a
 * reply holds.
 */
export async function repairFinding(ctx, pack, n) {
  if (!ctx.revalidationChecks) {
    throw new StepInputError('this state holds no revalidation walk; run the walk step first');
  }
  const findings = revalidationFindings(ctx, pack);
  if (!findings[n]) {
    throw new StepInputError(`--finding ${n} is not one of the ${findings.length} findings a repair can act on`);
  }
  delete pack.revalidation;
  await fixRound(ctx, pack, [findings[n]], 'revalidation', [], n);
  return { check: findings[n].row.section };
}

/** The Confidence Assessment fields a step can write on its own, Coverage included. */
export const CONFIDENCE_STEP_FIELDS = ['coverage', ...CONFIDENCE_FIELDS.map(([field]) => field)];

/**
 * One Confidence Assessment field written again over the pack as it stands. The old
 * text is blanked first, so the call does not read it as a field already written.
 */
export async function confidenceField(ctx, pack, field) {
  if (field === 'coverage') {
    pack.confidence = { ...pack.confidence, coverage: coverageText(ctx, pack) };
    return;
  }
  const entry = CONFIDENCE_FIELDS.find(([name]) => name === field);
  if (!entry) throw new StepInputError(`--field takes one of: ${CONFIDENCE_STEP_FIELDS.join(', ')}`);
  const aged = narrativeAged(pack);
  pack.confidence = { ...pack.confidence, [field]: '' };
  pack.confidence[field] = await writeConfidenceField(ctx, pack, field, entry[1], confidenceExtra(ctx, pack));
  // The rest of the review's prose is still older than the repairs, so the pack goes on saying so.
  if (aged) noteNarrativeAge(pack);
}

/** The overall confidence level rated again from the assessment steps the state holds. */
export async function confidenceLevel(ctx, pack) {
  if (!list(ctx.confidenceSteps).length) {
    throw new StepInputError('this state holds no confidence assessment steps; start at phase9-confidence or later');
  }
  return reRateConfidence(ctx, pack);
}

// ---------------------------------------------------------------------------
// Phase 10, Repository Improvement Notes

export async function phase10(ctx, pack) {
  const answer = await ask(ctx, {
    phase: 'phase10', step: 'notes', reasoning: false, refs: ctx.ref.core,
    task: 'Record what the reference material, the pipeline, or the repository\'s sources'
      + ' lacked during this run: each gap, its impact, a recommendation, and the component.',
    inputs: [['Run facts', [
      `Inputs missing at intake: ${list(pack.intake?.missing).join('; ') || 'none'}`,
      `Rules derived from document text: ${ctx.derived}`,
      `Builder repair calls: ${ctx.repairs}`,
      `Objectives dropped for want of a card: ${droppedList(ctx).length}`,
      `Rules with no card: ${list(pack.coverage).filter((r) => r.status === 'Missing').length}`,
      `Review issues found: ${ctx.reviewIssues}`,
      `Revalidation: ${pack.revalidation ? `failed, ${pack.revalidation.remaining.length} item(s) remain` : 'passed'}`,
    ].join('\n')]],
    schema: S.improvementSchema,
  });
  pack.improvementNotes = answer.improvementNotes;
  return { notes: answer.improvementNotes.length };
}
