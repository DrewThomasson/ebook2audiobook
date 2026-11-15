// Runs one part of a job's work on its own, in a sandbox, over the state a phase
// snapshot or an earlier step left. A step that asks the model is one call or a
// few; the builder steps ask none. Each step leaves its state in the sandbox's
// work/step.json, which the next step starts from, and prints what it did as
// content-free lines.

import fs from 'node:fs';
import path from 'node:path';
import { Cancelled, ModelError } from './model.mjs';
import { ReplayMiss } from './replay.mjs';
import { jobLogs } from './status.mjs';
import * as P from './phases.mjs';
import * as S from './schemas.mjs';
import { countStatuses, jobContext, PHASES, restoreState, stateText } from './run.mjs';
import { readStep, stepPath } from './rerun.mjs';

/** The steps. Each takes at most one option, and the model steps ask the model. */
export const STEPS = {
  draft: { model: false },
  build: { model: false },
  checklist: { model: true },
  walk: { model: true, option: 'check' },
  repair: { model: true, option: 'finding' },
  confidence: { model: true, option: 'field' },
};

/**
 * The step a command line names, checked, with its option read: `finding` as a
 * number, `checks` as the exact names of the Revalidation checks (a name, or a
 * prefix of one that no other shares, as many as are comma-separated), `field` as
 * a Confidence Assessment field. Throws, naming the problem, before anything is written.
 */
export function checkStep({ step, finding, check, field }) {
  if (!Object.hasOwn(STEPS, step ?? '')) throw new Error(`a step is one of: ${Object.keys(STEPS).join(', ')}`);
  for (const [flag, value] of [['finding', finding], ['check', check], ['field', field]]) {
    if (value !== undefined && STEPS[step].option !== flag) throw new Error(`--${flag} does not go with ${step}`);
  }
  const request = { step };
  if (step === 'repair') {
    if (!/^\d+$/.test(finding ?? '')) throw new Error('repair takes --finding <n>, a number counted from 0');
    request.finding = Number(finding);
  }
  if (check !== undefined) {
    request.checks = [...new Set(String(check).split(',').map((part) => {
      const wanted = part.trim().toLowerCase();
      const named = S.REVALIDATION_CHECKS.filter((name) => name.toLowerCase() === wanted);
      const found = named.length ? named : S.REVALIDATION_CHECKS.filter((name) => wanted && name.toLowerCase().startsWith(wanted));
      if (found.length !== 1) {
        throw new Error(`--check takes the names of Revalidation checks, or a start of one, comma-separated: ${S.REVALIDATION_CHECKS.join('; ')}`);
      }
      return found[0];
    }))];
  }
  if (field !== undefined) {
    if (!P.CONFIDENCE_STEP_FIELDS.includes(field)) {
      throw new Error(`--field takes one of: ${P.CONFIDENCE_STEP_FIELDS.join(', ')}`);
    }
    request.field = field;
  }
  return request;
}

/** Whether a checked step asks the model: the Coverage field is counted in code. */
export const stepUsesModel = ({ step, field }) => STEPS[step].model && !(step === 'confidence' && field === 'coverage');

const noModel = () => { throw new Error('this step uses no model'); };
/** The model of a step that asks none: any call is a mistake. */
const NO_MODEL = { json: noModel, countTokens: noModel };

const pad = (status) => status.padEnd(22);

const RUNNERS = {
  // The Draft workbook: the builder's own PASS and FAIL lines, and whether it wrote the workbook.
  draft(ctx, pack) {
    const draft = P.draftWorkbook(ctx, pack, 'step');
    ctx.logs.detail('builder draft', draft.lines.join('\n'));
    const counts = countStatuses(draft.lines.join('\n'));
    const report = [...draft.lines];
    if (!draft.workbook) report.push(`no workbook was written (builder exit ${draft.status})`);
    return { report, counts: { sheetsPass: counts.pass, sheetsLimited: counts.limited, sheetsFail: counts.fail },
      failed: counts.fail > 0 || !draft.workbook };
  },

  // The phase 8 build: every sheet's status as it stands after the pipeline's own checks, with no repair.
  // The revalidation's verdict is held back, as every pipeline build does, so the builder reads it as no sheet's failure.
  build(ctx, pack, { phase }) {
    const deferred = PHASES.indexOf(phase) < PHASES.indexOf('phase9-confidence') ? P.REVIEW_SHEETS : [];
    const verdict = pack.revalidation;
    delete pack.revalidation;
    let built;
    try {
      built = P.buildRound(ctx, pack, 'build', 0, deferred);
    } finally {
      if (verdict) pack.revalidation = verdict;
    }
    const failing = new Set(built.failed.map(([sheet]) => sheet));
    const rows = built.validation.map(([sheet, , , status]) => [sheet, failing.has(sheet) ? 'FAIL'
      : deferred.includes(sheet) && status === 'FAIL' ? 'DEFERRED' : status]);
    for (const sheet of failing) if (!rows.some(([name]) => name === sheet)) rows.push([sheet, 'FAIL']);
    const count = (status) => rows.filter(([, row]) => row === status).length;
    return { report: rows.map(([sheet, status]) => `${pad(status)} ${sheet}`),
      counts: { sheetsPass: count('PASS'), sheetsLimited: count('PASS WITH LIMITATIONS'), sheetsFail: count('FAIL') },
      failed: failing.size > 0 };
  },

  async checklist(ctx, pack) {
    const counts = await P.checklistRounds(ctx, pack);
    return { report: [`issues ${counts.issues}  coverageRows ${counts.coverageRows}  fixRounds ${counts.fixRounds}`], counts };
  },

  // One walk; each failed check a repair can act on is a finding, numbered as `repair --finding` counts them.
  async walk(ctx, pack, { checks }) {
    const walked = await P.walkSelected(ctx, pack, checks);
    const findings = P.revalidationFindings(ctx, pack);
    return { report: [...walked.checks.map((row) => `${row.verdict.padEnd(4)} ${row.check}`),
      ...findings.map(({ row }, n) => `finding ${n}  ${row.section}`)],
    counts: { failedChecks: walked.checks.filter((row) => row.verdict === 'fail').length,
      findings: findings.length, open: walked.open } };
  },

  async repair(ctx, pack, { finding }) {
    const { check } = await P.repairFinding(ctx, pack, finding);
    return { report: [`repaired finding ${finding}  ${check}`], counts: { finding } };
  },

  async confidence(ctx, pack, { field }) {
    if (field) {
      await P.confidenceField(ctx, pack, field);
      return { report: [`wrote ${field}`], counts: {} };
    }
    const level = await P.confidenceLevel(ctx, pack);
    return { report: [`overall ${level}`], counts: { confidence: level } };
  },
};

/** Writes `text` to `file` whole or not at all. */
function writeAtomic(file, text) {
  fs.writeFileSync(`${file}.tmp`, text);
  fs.renameSync(`${file}.tmp`, file);
}

/**
 * A state saved without the revalidation's verdicts, at or after the revalidation, takes
 * them from the file the revalidation wrote beside it, so a step can start from the state
 * of a job that has already run its revalidation.
 */
function seedVerdicts(ctx, outDir, phase) {
  if (ctx.revalidationChecks || PHASES.indexOf(phase) < PHASES.indexOf('phase9-revalidate')) return;
  const file = path.join(outDir, 'work', 'phase9-revalidation.json');
  if (!fs.existsSync(file)) return;
  const { checks } = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (Array.isArray(checks) && checks.length === S.REVALIDATION_CHECKS.length) ctx.revalidationChecks = checks;
}

/**
 * Runs the checked `request` over the state in the sandbox `id`, a copy made by
 * `prepareStepSandbox`. A step that passes writes its state back to
 * work/step.json; one that stops leaves the state as it was, with a `fail` line
 * and the pack as far as it got in work/partial-pack.json. Returns `{ ok, failed,
 * id, outDir, report, lines }`: `ok` is whether the step ran, `failed` whether its
 * result is a failing build, `report` what it found, and `lines` the status lines it wrote.
 * `job` holds the job's options.
 */
export async function runStep(config, { id, job, ...request }, { model, now = Date.now, signal = null } = {}) {
  const outDir = path.join(config.output, id);
  const saved = readStep(outDir);
  if (!saved) throw new Error(`${id} holds no step state (work/step.json)`);
  const logs = jobLogs(outDir, { echo: false });
  const offset = fs.existsSync(logs.statusPath) ? fs.statSync(logs.statusPath).size : 0;
  const written = () => (fs.existsSync(logs.statusPath) ? fs.readFileSync(logs.statusPath).subarray(offset)
    .toString('utf8').split('\n').filter(Boolean) : []);
  const { step } = request;
  const started = now();
  logs.status({ job: id, phase: saved.phase, event: 'begin', step });
  let ctx = null;
  let pack = {};
  // The state carries the job's totals; a step's line holds only what the step spent.
  const base = { calls: 0, prompt: 0, output: 0 };
  try {
    ctx = await jobContext(config, { ...job, id }, { outDir, logs, signal,
      model: stepUsesModel(request) ? model : NO_MODEL });
    pack = restoreState(config, ctx, saved);
    seedVerdicts(ctx, outDir, saved.phase);
    Object.assign(base, { calls: ctx.calls, prompt: ctx.tokens.prompt, output: ctx.tokens.output });
    if (stepUsesModel(request)) await P.readWindow(ctx, saved.phase);
    const out = await RUNNERS[step](ctx, pack, { ...request, phase: saved.phase });
    writeAtomic(stepPath(outDir), stateText(ctx, pack, saved.phase));
    logs.status({ job: id, phase: saved.phase, event: 'step', step, ms: now() - started, calls: ctx.calls - base.calls,
      promptTokens: ctx.tokens.prompt - base.prompt, outputTokens: ctx.tokens.output - base.output, ...out.counts });
    return { ok: true, failed: out.failed === true, id, outDir, report: out.report, lines: written() };
  } catch (error) {
    const reason = error instanceof Cancelled ? 'cancelled' : error instanceof P.GateError ? `gate:${error.code}`
      : error instanceof ModelError ? `model:${error.code}` : error instanceof ReplayMiss ? `replay:${error.code}`
        : error instanceof P.StepInputError ? 'step-input' : 'error';
    logs.detail('stopped', error.stack ?? String(error));
    logs.status({ job: id, phase: saved.phase, event: 'fail', reason, step, ms: now() - started, calls: (ctx?.calls ?? 0) - base.calls,
      ...(error instanceof P.GateError ? error.counts : {}) });
    if (Object.keys(pack).length) writeAtomic(path.join(outDir, 'work', 'partial-pack.json'), `${JSON.stringify(pack, null, 1)}\n`);
    // A refusal of the step's own input says what was wrong; any other message may quote the model or the pack.
    return { ok: false, failed: true, id, outDir, report: error instanceof P.StepInputError ? [error.message] : [],
      lines: written() };
  }
}
