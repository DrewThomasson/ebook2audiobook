// Reads the consuming repository's pipeline config: where its reference
// material, documents, exports, builder and queue are. Every path in it is
// relative to the repository root, which is `repoRoot` relative to the config
// file itself.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { DEFAULT_SEED, DEFAULT_TEMPERATURE, localEndpoint } from './model.mjs';

const REQUIRED_REFERENCES = ['procedure', 'workbookStandard', 'implementationGuide'];

// The shape of a rule export's rows. A consumer whose rule master differs
// overrides any of these under `ruleShape` in its config.
export const RULE_SHAPE = {
  matrixColumns: ['path', 'requirement_type', 'rule_category', 'name', 'description',
    'source_document', 'source_page', 'rule_summary', 'risk_level'],
  categories: ['Validation', 'Workflow', 'State Transition', 'Security', 'Batch', 'Reporting',
    'Event Generation', 'Conditional Display', 'Navigation', 'Integration', 'Data Integrity',
    'Calculation', 'Notification', 'Role Restriction', 'Timing/Temporal'],
  riskLevels: ['High', 'Medium', 'Low'],
  statuses: ['active', 'retired', 'superseded'],
  requirementType: 'Business Rule',
  prefixPattern: '^BR-',
  ruleIdPattern: '\\d{3}',
};

/** The `phase` names a reasoning call carries; `model.reasoningOutputByPhase` is keyed by them. */
export const REASONING_PHASES = ['phase1', 'phase3', 'phase4', 'phase5', 'phase9'];

/**
 * The output budget of each thinking step, in tokens, keyed `<phase>.<step>`: the most
 * one call may produce, its thinking and its answer together, sent as `max_tokens`. A
 * step with an index or a repeat suffix is keyed without it, so `rules-3` is
 * `phase1.rules`. A step that makes one call per part has a budget for each part, such as
 * `phase9.revalidation-traceability`. `model.reasoningOutputByStep` overrides these, and none
 * passes `model.reasoningOutput`. A step not listed here has no budget of its own.
 *
 * On a host with the server's thinking budget set, a step still cut at its output budget
 * gets that budget raised with `model.reasoningOutputByStep`. On a host without the
 * thinking budget, the fallback is that a thinking step cut at its output budget on two
 * or more recorded runs gets thinking off, which is why `phase1.understanding` is not
 * listed: the cut call's answer is lost, and the retry with thinking off answers anyway.
 */
export const REASONING_STEPS = {
  'phase1.rules': 20480,
  'phase3.scope': 20480,
  'phase4.impact': 8192,
  'phase5.objectives': 12288,
  'phase9.senior-review': 12288,
  'phase9.senior-notes': 12288,
  'phase9.confidence-steps': 12288,
  'phase9.confidence-overall': 8192,
  'phase9.revalidation-traceability': 12288,
  'phase9.revalidation-resolution': 8192,
  'phase9.revalidation-readiness': 8192,
};

/** A step's name without the index or repeat suffix its call adds. */
export const stepKey = (step) => String(step ?? '').replace(/-(\d+|again)$/, '');

/** How many times a job is tried before it is flagged and dropped from the queue. */
export const MAX_TRIES = 2;

/**
 * The stops a second try cannot change: the document or its rules have to be fixed by a
 * person first, so the job waits as stopped instead of using its tries on the same checkpoint.
 */
export const HOLD_REASONS = ['gate:rules-not-extracted', 'gate:rules-malformed', 'gate:document-file',
  'gate:duplicate-rule-wording', 'gate:rule-conflict', 'gate:needs-user-review'];

/** The reason a job stops with when the builder still refuses the pack after the last repair. */
export const BUILDER_FAIL = 'gate:builder-fail';

/**
 * True for a stop a second try from the same checkpoint cannot change: one of
 * HOLD_REASONS in any phase, or the builder refusing the pack in a Phase 9 step,
 * where a resume builds the same pack again.
 */
export const holdsRow = ({ reason, phase }) => HOLD_REASONS.includes(reason)
  || (reason === BUILDER_FAIL && String(phase ?? '').startsWith('phase9'));

/** True for a stopped row that waits for a person rather than for a request to resume. */
export const heldRow = (row) => row.status === 'stopped' && holdsRow(row);

/** The reason a run stops when memory stays low; such a stop is not one of a job's tries. */
export const MEMORY_STOP = 'memory:low';

/** The failures that count toward MAX_TRIES: a stop for low memory says nothing about the job. */
export const countedTries = (failures = []) => failures.filter((f) => f.reason !== MEMORY_STOP).length;

/** How many low-memory stops in a row a job gets before it is dropped for a person to look at. */
export const MAX_MEMORY_STOPS = 3;

/** The low-memory stops at the end of a job's failures; a failure of any other kind resets the count. */
export const memoryStops = (failures = []) => {
  let stops = 0;
  for (let i = failures.length - 1; i >= 0 && failures[i].reason === MEMORY_STOP; i -= 1) stops += 1;
  return stops;
};

const fill = (template, values) => String(template).replace(/\{(\w+)\}/g, (whole, key) =>
  (values[key] === undefined ? whole : String(values[key])));
export { fill };

// Git run for a path must not read the repository a hook or a parent git command pointed it at.
const gitEnv = () => {
  const env = { ...process.env };
  for (const key of ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_PREFIX', 'GIT_COMMON_DIR']) delete env[key];
  return env;
};

const realOr = (p) => { try { return fs.realpathSync(p); } catch { return path.resolve(p); } };

/** { prefix, top } for `root`: its folder inside its repository, with a trailing slash, and the top folder. */
function gitPlace(root) {
  const run = spawnSync('git', ['rev-parse', '--show-prefix', '--show-toplevel'],
    { cwd: root, encoding: 'utf8', env: gitEnv() });
  if (run.status !== 0) return null;
  const lines = run.stdout.replace(/\n$/, '').split('\n');
  return lines.length === 2 ? { prefix: lines[0], top: realOr(lines[1]) } : null;
}

/**
 * A document path as the job holds it: relative to the repository root, with
 * forward slashes. The part of a path after a `.claude/worktrees/<name>/` folder is
 * relative to that worktree's top folder. When the worktree belongs to the root's
 * own repository, the root's folder in that repository is cut off it. Otherwise it
 * is cut down to the longest tail of a folder and a file that exists under the
 * root, then to the tail from `docs/` on, then left whole. Any other path inside
 * the root is made relative; an absolute one outside it is read from its `docs/`
 * folder on, or returned as given, and a relative one outside it is only normalized.
 */
export function rootRelative(config, file) {
  const given = file;
  const posix = (p) => p.split(path.sep).join('/');
  const absolute = path.isAbsolute(given);
  const worktree = /^(.*?)(?:^|\/)\.claude\/worktrees\/[^/]+\/(.+)$/;
  const docs = /(?:^|\/)(docs\/.+)$/;
  const rel = absolute ? path.relative(config.root, given) : path.normalize(given);
  const inside = !rel.startsWith('..') && !path.isAbsolute(rel);
  // Only the part below the root is matched, so where the root itself sits never counts.
  const found = absolute && !inside ? worktree.exec(posix(given))
    : /^((?:\.\.\/)*)\.claude\/worktrees\/[^/]+\/(.+)$/.exec(posix(rel));
  if (!found) {
    if (inside) return posix(rel) || '.';
    return absolute ? docs.exec(posix(given))?.[1] ?? given : posix(rel);
  }
  const base = absolute && !inside ? found[1] : path.resolve(config.root, found[1]);
  const rest = found[2];
  const place = gitPlace(config.root);
  if (place && realOr(base || '/') === place.top && rest.startsWith(place.prefix)
    && rest.length > place.prefix.length) {
    return rest.slice(place.prefix.length);
  }
  // A tail of at least a folder and a file, so a bare file name never matches an unrelated file.
  const parts = rest.split('/');
  for (let i = 0; i < parts.length - 1; i += 1) {
    const tail = parts.slice(i).join('/');
    const at = path.resolve(config.root, tail);
    if (fs.existsSync(at) && fs.statSync(at).isFile()) return tail;
  }
  return docs.exec(rest)?.[1] ?? rest;
}

/**
 * The main checkout when `root` is inside a linked worktree of it, as
 * { main, top }: the main checkout's folder and the worktree's top folder. Null
 * for the main checkout itself, a folder outside a repository, or no git.
 */
export function mainCheckout(root) {
  const run = spawnSync('git', ['rev-parse', '--git-dir', '--git-common-dir', '--show-toplevel'],
    { cwd: root, encoding: 'utf8', env: gitEnv() });
  if (run.status !== 0) return null;
  const lines = run.stdout.trim().split('\n');
  if (lines.length !== 3) return null;
  const real = (p) => { try { return fs.realpathSync(path.resolve(root, p)); } catch { return path.resolve(root, p); } };
  const [dir, common, top] = lines.map(real);
  if (dir === common) return null;
  return { main: path.basename(common) === '.git' ? path.dirname(common) : common, top };
}

/**
 * The message that refuses a run from a worktree, or null. The job's documents
 * live in the main checkout, because a worktree is removed when its branch
 * merges. `BUILD_PACK_ALLOW_WORKTREE=1` skips the check for tests that run
 * over fixtures inside a worktree.
 */
export function worktreeRefusal(config) {
  if (process.env.BUILD_PACK_ALLOW_WORKTREE === '1') return null;
  const found = mainCheckout(config.root);
  if (!found) return null;
  let file = config.file;
  try { file = fs.realpathSync(file); } catch { /* the path as given */ }
  const inside = path.relative(found.top, file);
  const suggestion = inside.startsWith('..') ? '' : ` --config ${path.join(found.main, inside)}`;
  return `${config.root} is in a worktree of ${found.main}; a job's documents live in the main checkout,`
    + ` so run from there${suggestion ? ` with${suggestion}` : ''}.`;
}

export function loadConfig(configPath) {
  const file = path.resolve(configPath);
  const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
  const root = path.resolve(path.dirname(file), raw.repoRoot ?? '.');
  const at = (relative) => (relative ? path.resolve(root, relative) : undefined);
  // A reasoning call can think for 40k tokens, about 100 minutes at the 7 tokens a
  // second a 27B model makes on a single GPU, and reading a prompt that fills the
  // rest of a 128,000-token context adds up to a quarter hour, so a call waits up
  // to two and a half hours. The pipeline budgets each prompt against the smaller
  // of `context` (128000 by default) and the model server's own window; the
  // server's request time-out has to be at least as long as the call waits.
  const model = {
    temperature: DEFAULT_TEMPERATURE, seed: DEFAULT_SEED, context: 128000, maxOutput: 16384,
    reasoningOutput: 40960, timeoutMinutes: 150, ...raw.model,
  };
  // The reply cap for the retry of a thinking call that ran out its output budget; it
  // answers with thinking off, so it never needs more than a plain call's maxOutput.
  if (raw.model?.retryOutput === undefined) model.retryOutput = Math.min(8192, model.maxOutput);
  localEndpoint(model.endpoint);
  if (!model.name) throw new Error('config model.name is missing');
  if (!Number.isFinite(model.temperature) || model.temperature < 0 || model.temperature > 0.2) {
    throw new Error('config model.temperature must be between 0 and 0.2');
  }
  // llama.cpp reads the seed as an unsigned 32-bit number and takes its top value,
  // which -1 also becomes, as "pick a random seed", so neither is accepted.
  if (!Number.isInteger(model.seed) || model.seed < 0 || model.seed > 4294967294) {
    throw new Error('config model.seed must be a whole number from 0 to 4294967294');
  }
  if (raw.model?.retryOutput !== undefined && (!Number.isInteger(model.retryOutput)
    || model.retryOutput < 1024 || model.retryOutput > model.maxOutput)) {
    throw new Error('config model.retryOutput must be a whole number from 1024 to model.maxOutput');
  }
  // Minutes between the `progress` lines of a running call; the client's default applies when unset.
  if (raw.model?.progressMinutes !== undefined
    && (!Number.isInteger(model.progressMinutes) || model.progressMinutes < 1 || model.progressMinutes > 1440)) {
    throw new Error('config model.progressMinutes must be a whole number of minutes from 1 to 1440');
  }
  if (raw.model?.reasoningOutputByPhase !== undefined) {
    const byPhase = model.reasoningOutputByPhase;
    if (!byPhase || typeof byPhase !== 'object' || Array.isArray(byPhase)) {
      throw new Error('config model.reasoningOutputByPhase must be an object of phase caps');
    }
    for (const [phase, cap] of Object.entries(byPhase)) {
      if (!REASONING_PHASES.includes(phase)) {
        throw new Error(`config model.reasoningOutputByPhase.${phase} is not a reasoning phase`
          + ` (${REASONING_PHASES.join(', ')})`);
      }
      if (!Number.isInteger(cap) || cap < 1024 || cap > model.reasoningOutput) {
        throw new Error(`config model.reasoningOutputByPhase.${phase} must be a whole number`
          + ' from 1024 to model.reasoningOutput');
      }
    }
  }
  if (raw.model?.reasoningOutputByStep !== undefined) {
    const byStep = model.reasoningOutputByStep;
    if (!byStep || typeof byStep !== 'object' || Array.isArray(byStep)) {
      throw new Error('config model.reasoningOutputByStep must be an object of step caps');
    }
    for (const [step, cap] of Object.entries(byStep)) {
      if (!(step in REASONING_STEPS)) {
        throw new Error(`config model.reasoningOutputByStep.${step} is not a reasoning step`
          + ` (${Object.keys(REASONING_STEPS).join(', ')})`);
      }
      if (!Number.isInteger(cap) || cap < 1024 || cap > model.reasoningOutput) {
        throw new Error(`config model.reasoningOutputByStep.${step} must be a whole number`
          + ' from 1024 to model.reasoningOutput');
      }
    }
  }
  for (const key of REQUIRED_REFERENCES) {
    if (!raw.reference?.[key]) throw new Error(`config reference.${key} is missing`);
  }
  for (const key of ['module', 'command']) {
    if (!raw.builder?.[key]) throw new Error(`config builder.${key} is missing`);
  }
  const pause = { units: [], scope: 'system', busyProcess: null, pollSeconds: 5, maxWaitMinutes: 60, ...raw.pause };
  if (!Array.isArray(pause.units) || pause.units.some((unit) => typeof unit !== 'string' || !unit)) {
    throw new Error('config pause.units must be a list of unit names');
  }
  if (!['system', 'user'].includes(pause.scope)) {
    throw new Error("config pause.scope must be 'system' or 'user'");
  }
  if (!Number.isFinite(pause.pollSeconds) || pause.pollSeconds <= 0) {
    throw new Error('config pause.pollSeconds must be a positive number');
  }
  // Run once when a queue run ends, to unload the model; an empty command turns it off.
  if (raw.release !== undefined
    && (!raw.release || typeof raw.release !== 'object' || Array.isArray(raw.release))) {
    throw new Error('config release must be an object');
  }
  const release = { command: ['lemonade', 'unload'], timeoutSeconds: 60, ...raw.release };
  if (!Array.isArray(release.command)
    || release.command.some((word) => typeof word !== 'string' || !word)) {
    throw new Error('config release.command must be a list of words');
  }
  if (!Number.isFinite(release.timeoutSeconds) || release.timeoutSeconds <= 0) {
    throw new Error('config release.timeoutSeconds must be a positive number');
  }
  if (!Number.isFinite(pause.maxWaitMinutes) || pause.maxWaitMinutes < 0) {
    throw new Error('config pause.maxWaitMinutes must be a number of minutes, 0 or more');
  }
  // Desktop apps closed before a queue run. Scope patterns must start with a literal app- or
  // snap. prefix and end in .scope, so a pattern can never match a service or a system unit.
  const closeAppsKeys = ['scopes', 'onNow', 'keepIfRunning'];
  if (raw.closeApps !== undefined && (!raw.closeApps || typeof raw.closeApps !== 'object'
    || Array.isArray(raw.closeApps) || Object.keys(raw.closeApps).some((key) => !closeAppsKeys.includes(key)))) {
    throw new Error(`config closeApps must be an object with only ${closeAppsKeys.join(', ')}`);
  }
  const closeApps = { scopes: [], onNow: false, keepIfRunning: ['claude'], ...raw.closeApps };
  const scopePattern = /^(app-|snap\.)(?=[^*?]*[A-Za-z0-9])[A-Za-z0-9@_.:\\*?-]+\.scope$/;
  if (!Array.isArray(closeApps.scopes)
    || closeApps.scopes.some((scope) => typeof scope !== 'string' || !scopePattern.test(scope))) {
    throw new Error('config closeApps.scopes must be a list of app-*.scope or snap.*.scope patterns with a literal part');
  }
  if (typeof closeApps.onNow !== 'boolean') throw new Error('config closeApps.onNow must be true or false');
  if (!Array.isArray(closeApps.keepIfRunning)
    || closeApps.keepIfRunning.some((name) => typeof name !== 'string' || !name || Buffer.byteLength(name) > 15)) {
    // The kernel cuts a process name to 15 characters, so a longer one could never match.
    throw new Error('config closeApps.keepIfRunning must be a list of process names of up to 15 characters');
  }
  // The floor and ceiling come from the measured night in docs/runners/TestPackOffloadPlan.md:
  // available memory fell to 4.6 GiB and swap held about 68% (cold, speeds steady) all night,
  // so both defaults sit just past a healthy run. Measure again after changing the swap setup.
  const memoryKeys = ['enabled', 'minAvailableMiB', 'maxSwapPercent', 'pollSeconds', 'waitMinutes'];
  if (raw.memory !== undefined && (!raw.memory || typeof raw.memory !== 'object' || Array.isArray(raw.memory)
    || Object.keys(raw.memory).some((key) => !memoryKeys.includes(key)))) {
    throw new Error(`config memory must be an object with only ${memoryKeys.join(', ')}`);
  }
  const memory = { enabled: true, minAvailableMiB: 3072, maxSwapPercent: 85, pollSeconds: 30,
    waitMinutes: 20, ...raw.memory };
  if (typeof memory.enabled !== 'boolean') throw new Error('config memory.enabled must be true or false');
  if (!Number.isInteger(memory.minAvailableMiB) || memory.minAvailableMiB < 1) {
    throw new Error('config memory.minAvailableMiB must be a positive whole number');
  }
  if (!Number.isFinite(memory.maxSwapPercent) || memory.maxSwapPercent < 0 || memory.maxSwapPercent > 100) {
    throw new Error('config memory.maxSwapPercent must be a number from 0 to 100');
  }
  if (!Number.isFinite(memory.pollSeconds) || memory.pollSeconds <= 0) {
    throw new Error('config memory.pollSeconds must be a positive number');
  }
  if (!Number.isInteger(memory.waitMinutes) || memory.waitMinutes < 0) {
    throw new Error('config memory.waitMinutes must be a whole number of 0 or more');
  }
  // How long a job waits at a question gate for the build supervisor's answers, and how
  // recent the supervisor's `queue watch` heartbeat has to be for the job to wait at all.
  const supervisorKeys = ['waitMinutes', 'staleMinutes', 'notifyUrl'];
  if (raw.supervisor !== undefined && (!raw.supervisor || typeof raw.supervisor !== 'object'
    || Array.isArray(raw.supervisor) || Object.keys(raw.supervisor).some((key) => !supervisorKeys.includes(key)))) {
    throw new Error(`config supervisor must be an object with only ${supervisorKeys.join(', ')}`);
  }
  const supervisor = { waitMinutes: 30, staleMinutes: 15, notifyUrl: null, ...raw.supervisor };
  if (!Number.isInteger(supervisor.waitMinutes) || supervisor.waitMinutes < 0) {
    throw new Error('config supervisor.waitMinutes must be a whole number of 0 or more');
  }
  if (!Number.isInteger(supervisor.staleMinutes) || supervisor.staleMinutes < 1) {
    throw new Error('config supervisor.staleMinutes must be a positive whole number');
  }
  if (supervisor.notifyUrl !== null) {
    let url = null;
    try { url = new URL(supervisor.notifyUrl); } catch { /* checked below */ }
    if (!url || !['http:', 'https:'].includes(url.protocol)) {
      throw new Error('config supervisor.notifyUrl must be an http or https URL, or null');
    }
  }
  if (raw.cardRulesPerCall !== undefined) {
    throw new Error('config cardRulesPerCall is replaced by cardScenariosPerCall');
  }
  if (!Number.isInteger(raw.cardScenariosPerCall ?? 4) || (raw.cardScenariosPerCall ?? 4) < 1) {
    throw new Error('config cardScenariosPerCall must be a positive whole number');
  }
  if (raw.exclusiveSets !== undefined && typeof raw.exclusiveSets !== 'boolean') {
    throw new Error('config exclusiveSets must be true or false');
  }
  const objectiveEvidence = raw.objectiveEvidence ?? [];
  if (!Array.isArray(objectiveEvidence)) throw new Error('config objectiveEvidence must be a list');
  const evidenceKeys = ['id', 'objective', 'claim', 'terms', 'reason'];
  const validPattern = (source) => {
    try { new RegExp(source, 'i'); return true; } catch { return false; }
  };
  const nonEmpty = (value) => typeof value === 'string' && value.trim() !== '';
  const evidenceIds = new Set();
  objectiveEvidence.forEach((rule, i) => {
    const where = `config objectiveEvidence[${i}]`;
    if (!rule || typeof rule !== 'object' || Array.isArray(rule)) throw new Error(`${where} must be an object`);
    const extra = Object.keys(rule).find((key) => !evidenceKeys.includes(key));
    if (extra) throw new Error(`${where} has an unknown key: ${extra}`);
    if (typeof rule.id !== 'string' || !/^[A-Za-z][\w-]*$/.test(rule.id)) {
      throw new Error(`${where}.id must be a name of letters, digits, _ and -, starting with a letter`);
    }
    if (evidenceIds.has(rule.id)) throw new Error(`${where}.id repeats ${rule.id}`);
    evidenceIds.add(rule.id);
    if (!nonEmpty(rule.objective) || !validPattern(rule.objective)) {
      throw new Error(`${where}.objective is not a valid pattern`);
    }
    for (const key of ['claim', 'reason']) {
      if (!nonEmpty(rule[key])) throw new Error(`${where}.${key} must be a non-empty string`);
    }
    if (!Array.isArray(rule.terms) || !rule.terms.length) {
      throw new Error(`${where}.terms must be a non-empty list`);
    }
    rule.terms.forEach((term, j) => {
      if (!nonEmpty(term) || !validPattern(term)) throw new Error(`${where}.terms[${j}] is not a valid pattern`);
    });
  });
  const moduleAbbreviations = raw.moduleAbbreviations ?? {};
  for (const [name, abbreviation] of Object.entries(moduleAbbreviations)) {
    if (!/^[A-Z0-9]{2,6}$/.test(abbreviation)) {
      throw new Error(`config moduleAbbreviations.${name} must be 2 to 6 upper-case letters or digits`);
    }
  }
  const output = raw.output ?? path.join(os.homedir(), '.local/share/build-pack');
  const outputDir = path.resolve(root, output.replace(/^~(?=\/)/, os.homedir()));
  // Where new jobs are listed; each source is read before the nightly run takes a job.
  const queue = { file: '.build-pack-queue.json', start: '22:00', cutoff: '07:00', sources: [],
    ...raw.queue };
  if (!Array.isArray(queue.sources)) throw new Error('config queue.sources must be a list');
  for (const source of queue.sources) {
    if (source?.type === 'folder' && source.path) continue;
    if (source?.type === 'records' && source.glob) continue;
    if (source?.type === 'command' && Array.isArray(source.command) && source.command.length) continue;
    throw new Error('config queue.sources takes folder (path), records (glob) or command (command list)');
  }
  const report = { weeklyDay: 1, sample: 2, maxPriority: 6, ...raw.report };
  if (!Number.isInteger(report.weeklyDay) || report.weeklyDay < 0 || report.weeklyDay > 6) {
    throw new Error('config report.weeklyDay must be a day number from 0 (Sunday) to 6');
  }
  for (const key of ['sample', 'maxPriority']) {
    if (!Number.isInteger(report[key]) || report[key] < 0) {
      throw new Error(`config report.${key} must be a whole number`);
    }
  }
  if (report.seed !== undefined && !/^-?\d+$/.test(String(report.seed))) {
    throw new Error('config report.seed must be a whole number');
  }
  report.dir = path.resolve(root, (report.dir ?? path.join(outputDir, 'reports'))
    .replace(/^~(?=\/)/, os.homedir()));
  return {
    file,
    root,
    at,
    model,
    reference: raw.reference,
    terms: { issue: 'issue', change: 'change', ...raw.terms },
    idFields: {
      issue: 'issue', change: 'change', changeApplies: 'changeApplies',
      description: 'changeDescription', ...raw.idFields,
    },
    packFile: raw.packFile ?? '{issue}_pack.json',
    suitePackFile: raw.suitePackFile ?? '{suite}_pack.json',
    inputs: raw.inputs ?? {},
    // Off unless the config or a job opts in: a document with no extracted rules
    // stops intake instead of having rules derived from its text.
    allowDerivedRules: raw.allowDerivedRules === true,
    ruleShape: { ...RULE_SHAPE, ...raw.ruleShape },
    builder: { retries: 3, ...raw.builder },
    // A document's code or module name to the abbreviation its cards and rules carry as their
    // module, such as INV; a document not listed takes the module and abbreviation Phase 1 names.
    moduleAbbreviations,
    suiteMerge: raw.suiteMerge,
    // Scenarios written per card call.
    cardScenariosPerCall: raw.cardScenariosPerCall ?? 4,
    // The sets an issue pack's cards are assigned to; null finds the objective
    // by its usual name in the builder's list, if it has one.
    fullCoverageObjective: raw.fullCoverageObjective ?? null,
    breakItObjective: raw.breakItObjective ?? null,
    // false: a card may sit in several sets. true: a BREAK IT card sits only in the BREAK IT set.
    exclusiveSets: raw.exclusiveSets === true,
    // Evidence a change can hold that makes an objective applicable; see Phase 5.
    objectiveEvidence,
    output: outputDir,
    pause,
    closeApps,
    release,
    memory,
    supervisor,
    queue,
    report,
  };
}

/** Files under the root that match a pattern with `*` and `**`, sorted. */
export function globFiles(root, pattern) {
  const parts = pattern.split('/');
  const toRegex = (part) => new RegExp(`^${part.replace(/[.+^${}()|[\]\\]/g, '\\$&')
    .replace(/\*/g, '[^/]*').replace(/\?/g, '[^/]')}$`);
  const found = [];
  const walk = (dir, rest) => {
    if (!rest.length) return;
    const [head, ...tail] = rest;
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    if (head === '**') {
      walk(dir, tail);
      for (const entry of entries) {
        if (entry.isDirectory()) walk(path.join(dir, entry.name), rest);
      }
      return;
    }
    const match = toRegex(head);
    for (const entry of entries) {
      if (!match.test(entry.name)) continue;
      const full = path.join(dir, entry.name);
      if (!tail.length && entry.isFile()) found.push(full);
      else if (tail.length && entry.isDirectory()) walk(full, tail);
    }
  };
  walk(root, parts);
  return [...new Set(found)].sort();
}

/**
 * The reference documents, read once. `chapters(phase)` gives the methodology
 * chapters config names for a phase, each cut from its heading to the next.
 * `docs.operatingManual` holds the operating rules. It stays out of `core`, so only
 * the design phases that name it carry it.
 */
export function loadReference(config) {
  const read = (key) => (config.reference[key]
    ? fs.readFileSync(config.at(config.reference[key]), 'utf8') : '');
  const docs = {};
  for (const key of ['procedure', 'workbookStandard', 'implementationGuide', 'glossary',
    'intake', 'understandingGate', 'ruleIntake', 'scope', 'validation', 'revalidation',
    'operatingManual']) {
    docs[key] = read(key);
  }
  const methodology = config.reference.methodology;
  let methodologyLines = [];
  if (methodology?.file) {
    methodologyLines = fs.readFileSync(config.at(methodology.file), 'utf8').split('\n');
  }
  const heading = new RegExp(methodology?.heading ?? '^# Chapter (\\d+)');
  const skipBefore = methodology?.skipBefore ?? 0;

  /** Chapter n's text: its first heading past skipBefore, up to the next heading. */
  function chapter(n) {
    const start = methodologyLines.findIndex((line, i) => i >= skipBefore
      && heading.exec(line)?.[1] === String(n));
    if (start < 0) throw new Error(`methodology chapter ${n} not found`);
    let end = methodologyLines.findIndex((line, i) => i > start && heading.test(line));
    if (end < 0) end = methodologyLines.length;
    return methodologyLines.slice(start, end).join('\n');
  }

  return {
    docs,
    /** The procedure, standard and implementation guide, which every phase keeps. */
    core: [docs.procedure, docs.workbookStandard, docs.implementationGuide, docs.glossary]
      .filter(Boolean),
    chapters(phase) {
      return (methodology?.byPhase?.[phase] ?? []).map(chapter);
    },
  };
}
