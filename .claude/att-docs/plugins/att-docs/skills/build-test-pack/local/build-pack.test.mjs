// Runs the local pipeline end to end against the synthetic fixtures, with a
// model that answers every call from its schema and a stub builder.
//
//   node --test plugins/att-docs/skills/build-test-pack/local/build-pack.test.mjs

import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { getEventListeners } from 'node:events';
import http from 'node:http';
import { after, test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { addJob, cancelJob, checkJob, checkJobAndHost, claimStale, cutoffAfter, drainQueue, fillQueue, jobFrom, jobFromLine,
  jobStatus, lockHeld,
  markRestore, markRestoreRequest, parseArgs, queueLines, readQueue, removeJob, rerunJob, restoreLines, restorePaused,
  restoreRequest, restoreUnits, summaryLines, stepJob }
  from './build-pack.mjs';
import { countedTries, HOLD_REASONS, loadConfig, MAX_MEMORY_STOPS, mainCheckout, memoryStops, RULE_SHAPE, rootRelative,
  worktreeRefusal } from './config.mjs';
import { rulesStale, shapeProblems, struckSpans, uncitedStruck } from './rules.mjs';
import { createAppCloser } from './close-apps.mjs';
import { createPauser, markRestoreFile, onPauseList, pausedPath, readPaused } from './pause.mjs';
import { Cancelled, DEFAULT_SEED, ModelError, REASONING_TAIL_CHARS, localEndpoint, modelClient } from './model.mjs';
import * as S from './schemas.mjs';
import { estimateTokens } from './model.mjs';
import { stepSchema } from './steps.mjs';
import { almDescriptions, batches, candidateLine, documentInputs, documentRules, dropUnfoundedAssumptions, expectedProblems, impactsText, phase5,
  citesId, designRules, resultsAgree, setsOf, splitText, tidyDocument } from './phases.mjs';
import { jobId, PHASES, readCheckpoint, runJob } from './run.mjs';
import { compareSnapshots, readStep } from './rerun.mjs';
import { checkStep, runStep } from './step-job.mjs';
import { memoryLow, parseMeminfo, waitForMemory } from './meminfo.mjs';
import { renderReport, reportData, seededRandom, spotChecks, writeReports } from './report.mjs';
import { createReleaser } from './release.mjs';
import { sleepUnlessAborted } from './abort.mjs';
import { callFileName, promptHash, schemaHash } from './calls.mjs';
import { FIELD_MAX, fitCounts, jobLogs, noteCode, readStatusLog, repeatedCuts, runCuts, sheetsField,
  statusFields } from './status.mjs';
import { replayModel, replaySource } from './replay.mjs';
import { readPack } from './pack.mjs';
import { answersPath, heartbeatPath, touchHeartbeat } from './supervisor.mjs';
import { firstEvent, sse, streamed } from './fixtures/streamed.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES = path.join(HERE, 'fixtures');
// The fixtures can sit in a worktree of this repository; the worktree check has its own tests.
process.env.BUILD_PACK_ALLOW_WORKTREE = '1';

// Every scratch folder lives under one root, removed when this file's tests finish, so a run
// leaves nothing in the system temp folder.
const SCRATCH_ROOT = fs.mkdtempSync(path.join(os.tmpdir(), 'build-pack-test-'));
after(() => fs.rmSync(SCRATCH_ROOT, { recursive: true, force: true }));
const scratch = (prefix) => fs.mkdtempSync(path.join(SCRATCH_ROOT, prefix));

const fixtureInputs = () => JSON.parse(fs.readFileSync(path.join(FIXTURES, 'pipeline.json'), 'utf8')).inputs;

/** A config over the fixtures whose output and queue land in a fresh temp folder. */
function fixtureConfig(overrides = {}) {
  const dir = scratch('build-pack-');
  const raw = JSON.parse(fs.readFileSync(path.join(FIXTURES, 'pipeline.json'), 'utf8'));
  // The memory check reads the machine running the tests, so it is off unless a test turns it on.
  // The release step is off too, so no test unloads a real model; the release tests turn it on.
  Object.assign(raw, { repoRoot: FIXTURES, output: path.join(dir, 'out'), memory: { enabled: false },
    queue: { file: path.join(dir, 'queue.json') }, release: { command: [] } }, overrides);
  const file = path.join(dir, 'pipeline.json');
  fs.writeFileSync(file, JSON.stringify(raw));
  return loadConfig(file);
}

/** A value of the schema's shape: every enum value once where a list's length is the enum's. */
function sample(schema, key = 'text') {
  if (schema.enum) return schema.enum[0];
  if (schema.type === 'boolean') return true;
  if (schema.type === 'integer') return 1;
  if (schema.type === 'string') return schema.pattern ? 'MOD' : `${key} value`;
  if (schema.type === 'array') {
    const item = schema.items;
    const keyed = item.type === 'object' && Object.entries(item.properties)
      .find(([, p]) => p.enum && p.enum.length === schema.minItems);
    if (keyed) {
      return keyed[1].enum.map((value) => ({ ...sample(item, key), [keyed[0]]: value }));
    }
    if (item.enum) return [...item.enum];
    return Array.from({ length: Math.max(1, schema.minItems ?? 1) }, () => sample(item, key));
  }
  return Object.fromEntries(Object.entries(schema.properties)
    .map(([k, p]) => [k, sample(p, plainKey(k))]));
}

/** A property's name without the number an ordered object's properties carry (`01_why`). */
const plainKey = (key) => key.replace(/^\d\d_/, '');

/** The value with each numbered property under its plain name, or the other way round. */
function rename(schema, value, toWire) {
  if (!schema || !value || typeof value !== 'object') return value;
  if (Array.isArray(value)) return value.map((item) => rename(schema.items, item, toWire));
  if (!schema.properties) return value;
  return Object.fromEntries(Object.entries(value).map(([key, item]) => {
    const own = toWire ? Object.keys(schema.properties).find((k) => plainKey(k) === key) ?? key : key;
    return [toWire ? own : plainKey(key), rename(schema.properties[own], item, toWire)];
  }));
}
/** A reply written by the plain names, renamed the way the model writes it. */
const wireNames = (schema, value) => rename(schema, value, true);
/** A reply as the model writes it, renamed to the plain names the pipeline reads. */
const plainNames = (schema, value) => rename(schema, value, false);

/** The scenario ids a card schema offers. */
const scenarioEnum = (schema) => S.propOf(S.propOf(schema, 'cards').items, 'scenario').enum;

/**
 * A model that answers from each call's schema. `answers` overrides a reply by
 * the schema name's prefix (the phase and step), as a value or a function of
 * the sampled reply. Every call is recorded.
 */
function fakeModel(answers = {}) {
  const calls = [];
  return {
    calls,
    countTokens: async (text) => Math.ceil(text.length / 3),
    async json(request) {
      calls.push(request);
      let value = plainNames(request.schema, sample(request.schema));
      // Two empty lists keep the gates quiet: no conflicts, nothing missing.
      if ('conflicts' in value) value.conflicts = [];
      if ('missing' in value) value.missing = [];
      if ('blockingMissing' in value) value.blockingMissing = [];
      if ('decisionsRequired' in value) value.decisionsRequired = [];
      if ('userReview' in value) value.userReview = [];
      if ('assumptionsToProceed' in value) value.assumptionsToProceed = [];
      if (Array.isArray(value.uncovered)) value.uncovered = [];
      if (Array.isArray(value.skipped)) value.skipped = [];
      // A repair builds no new card unless a test returns one.
      if (Array.isArray(value.newCards)) value.newCards = [];
      // The checklist finds nothing unless a test plants a finding, so no fix round runs.
      if (request.schemaName.startsWith('phase9_checklist')) value.issues = [];
      // A confidence field is a sentence that names a rule or card, as the call requires.
      const field = /^phase9_confidence_(?!overall|steps)/.test(request.schemaName)
        && Object.keys(request.schema.properties)[0];
      if (field) {
        const id = /\b(?:TC|BR)-[A-Za-z0-9.-]*\d\b/.exec(request.user.split('Cards and the rules they cite')[1] ?? '')?.[0] ?? '';
        value[field] = `The ${field} is covered by ${id} and the cards around it in this pack.`;
      }
      // A card call gets one card for each scenario it is offered.
      const offered = value.cards?.[0]?.scenario !== undefined && scenarioEnum(request.schema);
      if (offered) {
        value.cards = offered.map((id) => ({ ...value.cards[0], scenario: id, title: `title ${id}`,
          mission: `mission ${id}`, focus: [`focus ${id}`] }));
      }
      const [, override] = Object.entries(answers)
        .find(([prefix]) => request.schemaName.startsWith(prefix)) ?? [];
      if (override) value = typeof override === 'function' ? override(value, calls) : override;
      value = wireNames(request.schema, value);
      return { value, usage: { promptTokens: 10, outputTokens: 5, ms: 1 } };
    },
  };
}

const read = (file) => fs.readFileSync(file, 'utf8');
/** True when the job's status log already has a line for the phase and event. */
const statusSeen = (config, job, phase, event) => {
  const log = path.join(config.output, jobId(job), 'status.log');
  return fs.existsSync(log) && statusLines(path.dirname(log)).some((l) => l.phase === phase && l.event === event);
};
const statusLines = (outDir) => read(path.join(outDir, 'status.log')).trim().split('\n')
  .map((line) => JSON.parse(line));

// Text from the fixtures that must never reach the status log or the console.
const CONTENT = ['Patron', 'renew', 'Renewal', 'BR-LIB', 'fines', 'Overdue', 'expiry', 'value'];

function assertContentFree(text) {
  for (const word of CONTENT) assert.ok(!text.includes(word), `status text carries "${word}"`);
}

test('an issue pack builds end to end on the local model alone', async () => {
  const config = fixtureConfig();
  const model = fakeModel({ intake: (value) => ({ ...value,
    documents: ['docs/LIB/UC01-Card-Renewal.md'] }) });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.ok(fs.existsSync(result.workbook));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.issue, '501');
  assert.equal(pack.change, '7001');
  // Intake picked documents from the index; the export gave the master's IDs, the retired one kept.
  assert.deepEqual(pack.rules.map((rule) => rule.id).sort(), [
    'BR-LIB.UC01-001', 'BR-LIB.UC01-002', 'BR-LIB.UC01-003', 'BR-LIB.UC01-004', 'BR-LIB.UC01-005',
    'BR-LIB.UC01-006',
  ]);
  // The retired rule keeps its place, says it was removed, and goes to Phase 3 like any other.
  const retired = pack.rules.find((rule) => rule.id === 'BR-LIB.UC01-006');
  assert.match(retired.summary, /^Retired: this rule was removed/);
  // Its Status says so too, so a builder can show it without reading the summary; every other rule is Active.
  assert.equal(retired.status, 'Retired');
  assert.ok(pack.rules.filter((rule) => rule !== retired).every((rule) => rule.status === 'Active'));
  const scoped = model.calls.filter((call) => call.schemaName.startsWith('phase3'))
    .flatMap((call) => Object.keys(call.schema.properties.rules.properties));
  assert.ok(scoped.includes('BR-LIB.UC01-006'));
  const phase1 = model.calls.find((call) => call.schemaName.startsWith('phase1'));
  assert.match(phase1.user, /\[retired\] BR-LIB\.UC01-006/);
  // The scope and card prompts ask for the retired status, Focus as steps and a result on every checking step.
  assert.match(model.calls.find((call) => call.schemaName.startsWith('phase3')).user, /never classify it Superseded/);
  assert.match(model.calls.find((call) => call.schemaName.startsWith('phase6_cards')).user,
    /Focus lists the tester's actions in order, one item per step[\s\S]*Every step that checks something/);
  assert.match(model.calls.find((call) => call.schemaName.startsWith('phase6_cards')).user,
    /step 1 opens the stage through its entry\s+path[\s\S]*never invent a path/);
  assert.ok(pack.testCards.every((card) => /^TC-MOD-501-\d{3}$/.test(card.id)));
  const phases = statusLines(result.outDir).filter((l) => l.event === 'pass').map((l) => l.phase);
  assert.deepEqual(phases, ['intake', 'phase1', 'phase2', 'phase3', 'phase4', 'phase5', 'phase6',
    'phase7', 'phase8', 'phase9-checklist', 'phase9-senior', 'phase9-confidence',
    'phase9-revalidate', 'phase10', 'done']);
  // Reasoning is on for the judgment phases and off for extraction.
  const thinking = new Map(model.calls.map((c) => [c.schemaName.split('_')[0], c.reasoning]));
  // Phase 4 ends on its risk rating, an extraction; its impact analysis thinks. Phase 1's
  // understanding call is asked once, with thinking off.
  assert.deepEqual(Object.fromEntries(thinking), { intake: false, phase1: false, phase2: false, phase3: true,
    phase4: false, phase5: true, phase6: false, phase7: false, phase9: true, phase10: false });
  assert.equal(model.calls.find((c) => c.schemaName.startsWith('phase4_impact')).reasoning, true);
  assert.deepEqual(model.calls.filter((c) => c.schemaName.startsWith('phase1_understanding'))
    .map((c) => c.reasoning), [false]);
  assert.equal(statusLines(result.outDir).filter((l) => l.event === 'retry').length, 0);
  // Phase 9's checklist is a reading pass with thinking off; its other calls think.
  const checklist = model.calls.filter((c) => c.schemaName.startsWith('phase9_checklist'));
  assert.ok(checklist.length && checklist.every((c) => c.reasoning === false));
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('a document the config names takes its abbreviation as the module of its rules and cards', async () => {
  const config = fixtureConfig({ moduleAbbreviations: { 'UC01-Card-Renewal': 'INV' } });
  const model = fakeModel({ intake: (value) => ({ ...value,
    documents: ['docs/LIB/UC01-Card-Renewal.md'] }) });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.rules.every((rule) => rule.module === 'INV'));
  assert.ok(pack.testCards.every((card) => card.module === 'INV' && /^TC-INV-501-\d{3}$/.test(card.id)));
});

/** A model whose Phase 1 puts every document in one module, `Investigation`, abbreviated INV. */
const oneModule = () => fakeModel({ intake: (value) => ({ ...value,
  documents: ['docs/LIB/UC01-Card-Renewal.md', 'docs/LIB/UC02-Overdue-Fines.md'] }),
phase1_understanding: (value) => {
  for (const row of Object.values(value.modules)) Object.assign(row, { module: 'Investigation', abbreviation: 'INV' });
  return value;
} });

test('a document of a module the config named for another document takes the same abbreviation', async () => {
  const config = fixtureConfig({ moduleAbbreviations: { 'UC01-Card-Renewal': 'INV' } });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model: oneModule(), echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual([...new Set(pack.rules.map((rule) => rule.sourceDocument))].length, 2);
  assert.ok(pack.rules.every((rule) => rule.module === 'INV'));
  assert.ok(pack.testCards.every((card) => card.module === 'INV' && /^TC-INV-501-\d{3}$/.test(card.id)));
});

test('the abbreviation a config names for one document of a module reaches the others whatever their order', async () => {
  const config = fixtureConfig({ moduleAbbreviations: { 'UC02-Overdue-Fines': 'INV' } });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model: oneModule(), echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(new Set(pack.rules.map((rule) => rule.sourceDocument)).size, 2);
  assert.ok(pack.rules.every((rule) => rule.module === 'INV'));
});

test('a suite keeps a configured abbreviation for its document whatever the order, and numbers the others apart', async () => {
  const config = fixtureConfig({ moduleAbbreviations: { UC02: 'INV' } });
  const model = fakeModel({ phase1_understanding: (value) => {
    for (const row of Object.values(value.modules)) Object.assign(row, { module: 'Investigation', abbreviation: 'INV' });
    return value;
  } });
  const result = await runJob(config, { suite: 'LIB' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const ids = JSON.parse(read(result.packPath)).testCards.map((card) => card.id);
  assert.equal(new Set(ids).size, ids.length);
});

test('two documents of one module cannot be named different abbreviations in an issue pack', async () => {
  const config = fixtureConfig({ moduleAbbreviations: { 'UC01-Card-Renewal': 'INV', 'UC02-Overdue-Fines': 'INX' } });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model: oneModule(), echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'gate:abbreviation-shared');
});

test('a suite cannot give two documents one configured abbreviation, since each numbers its own cards', async () => {
  const config = fixtureConfig({ moduleAbbreviations: { Investigation: 'INV' } });
  const model = fakeModel({ phase1_understanding: (value) => {
    for (const row of Object.values(value.modules)) Object.assign(row, { module: 'Investigation', abbreviation: 'INV' });
    return value;
  } });
  const result = await runJob(config, { suite: 'LIB' }, { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'gate:abbreviation-shared');
});

test('every rule carries a status: derived rules and a suite\'s merged rules are Active', async () => {
  const failing = ['node', '-e', 'process.stderr.write("{doc} is not in the doc map"); process.exit(1)'];
  const allowed = fixtureConfig({ allowDerivedRules: true,
    inputs: { ...fixtureInputs(), ruleExport: failing, noRules: 'is not in the doc map' } });
  const derived = await runJob(allowed, { issue: '501', change: '7001' }, { model: fakeModel(), echo: false });
  assert.equal(derived.ok, true, JSON.stringify(derived));
  const pack = JSON.parse(read(derived.packPath));
  assert.ok(pack.rules.length && pack.rules.every((rule) => rule.status === 'Active'));
  const suite = await runJob(fixtureConfig(), { suite: 'LIB' }, { model: fakeModel(), echo: false });
  assert.ok(JSON.parse(read(suite.packPath)).rules.every((rule) => rule.status === 'Active'));
});

test('a configured abbreviation must be 2 to 6 upper-case letters or digits', () => {
  assert.throws(() => fixtureConfig({ moduleAbbreviations: { UC01: 'inv' } }),
    /moduleAbbreviations\.UC01/);
});

test('a suite pack builds through the repository\'s merge', async () => {
  const config = fixtureConfig();
  const result = await runJob(config, { suite: 'LIB' }, { model: fakeModel(), echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.suite, 'LIB');
  assert.equal(pack.rules.length, 8);
  assert.ok(pack.rules.every((rule) => rule.impact === 'Regression'));
  assert.equal(pack.objectives.find((r) => r.objective === 'Core Change Validation').applicable, false);
  // Cards are written one document at a time, each named by its number.
  const cardCalls = statusLines(result.outDir).filter((l) => l.event === 'call' && l.phase === 'phase6');
  assert.deepEqual([...new Set(cardCalls.map((l) => l.step.split('-')[1]))], ['d1', 'd2']);
  // The merge sees cards as the builder knows them, without the design pass's marks.
  assert.ok(pack.testCards.every((card) => !('scenario' in card) && !('breakIt' in card)));
  // Phase 8 writes the suite's Draft workbook under the suite's file name.
  assert.ok(statusLines(result.outDir).some((l) => l.phase === 'phase8' && l.step === 'build'
    && l.event === 'draft' && l.written === true));
  assert.ok(fs.existsSync(path.join(result.outDir, 'work', 'review', 'LIB_Suite_Pack.xlsx')));
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

// Scenario design: the inventory, the card batches, and the sets the cards land in.

const INTAKE = { intake: (value) => ({ ...value, documents: ['docs/LIB/UC01-Card-Renewal.md'] }) };
// The fixture's retired rule is one the change does not concern, so no card is owed for it.
const NOT_REMOVAL = { phase3_scope: (value) => {
  value.rules['BR-LIB.UC01-006'] &&= { ...value.rules['BR-LIB.UC01-006'], impact: 'Not Impacted' };
  return value;
} };
const lib = (extra = {}, overrides = {}) => ({ model: fakeModel({ ...INTAKE, ...NOT_REMOVAL, ...extra }),
  config: fixtureConfig(overrides) });
const runLib = ({ model, config }) => runJob(config, { issue: '501', change: '7001' },
  { model, echo: false });
const phase6Pass = (outDir) => statusLines(outDir).find((l) => l.event === 'pass' && l.phase === 'phase6');

/**
 * An inventory reply of the given scenarios; each takes the rule at its index unless it names a `rule` index.
 * Rules no spec names go on the last scenario, so none is left for the pass that gives a rule its own scenario.
 */
const inventory = (specs) => (value) => {
  const ids = value.scenarios[0].rules;
  const picked = specs.map((spec, i) => spec.rule ?? i % ids.length);
  const rest = ids.filter((_, k) => !picked.includes(k));
  return { ...value, scenarios: specs.map((spec, i) => ({ kind: 'decision', outcome: 'outcome',
    action: `action ${i}`, population: `population ${i}`, ...spec,
    rules: [ids[picked[i]], ...(i === specs.length - 1 ? rest : [])] })) };
};
const BREAK = { kind: 'break' };
const titled = (value) => ({ ...value,
  cards: value.cards.map((card) => ({ ...card, title: `Case ${card.scenario}` })) });
const setCards = (pack, objective) => {
  const set = pack.testSets.find((row) => row.objective === objective);
  return set ? set.cards.map((id) => pack.testCards.find((c) => c.id === id).title).sort() : [];
};
const withMaster = (rules) => {
  const master = JSON.parse(read(path.join(FIXTURES, 'master.json')));
  for (const row of master.exports.find((e) => e.doc === 'docs/LIB/UC01-Card-Renewal.md').rules) rules(row);
  const name = `master-${process.pid}-${Date.now()}.json`;
  fs.writeFileSync(path.join(FIXTURES, name), JSON.stringify(master));
  return name;
};

test('the scenario inventory is asked first and its scenarios and earlier cards reach every card call', async () => {
  const run = lib({
    phase6_scenarios: inventory([{}, {}, {}, {}, BREAK]),
    // Each call writes only two cards, so the next call has cards to be shown.
    phase6_cards: (value) => titled({ ...value, cards: value.cards.slice(0, 2) }),
  }, { cardScenariosPerCall: 2 });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const steps = run.model.calls.map((c) => c.schemaName).filter((n) => n.startsWith('phase6'));
  assert.equal(steps[0], 'phase6_scenarios_d1');
  const cardCalls = run.model.calls.filter((c) => c.schemaName.startsWith('phase6_cards_d1'));
  assert.ok(cardCalls.length >= 3);
  // Each call is shown the inventory's scenarios that are still open.
  assert.match(cardCalls[0].user, /S1 \| decision \| rules \S+ \| population 0 \| action 0 \| outcome/);
  assert.match(cardCalls[1].user, /S3 \| decision \| rules \S+ \| population 2 \| action 2/);
  assert.ok(!cardCalls[1].user.includes('population 0'));
  assert.ok(!cardCalls[0].user.includes('Case S1'));
  assert.match(cardCalls[1].user, /Cards written so far[^]*Case S1 \| S1 \| rules /);
  // A card names a scenario that is still open, and no other.
  assert.deepEqual(scenarioEnum(cardCalls[1].schema), ['S3', 'S4', 'S5']);
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(pack.testCards.map((c) => c.title).sort(), ['Case S1', 'Case S2', 'Case S3',
    'Case S4', 'Case S5']);
  assert.equal(phase6Pass(result.outDir).scenarios, 5);
});

const emptyKindNotes = (pack) => pack.assumptions.filter((a) => /scenario was listed/.test(a.assumption));

test('the inventory asks for control, isolation, combined, persistence and break scenarios', async () => {
  const run = lib();
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const call = run.model.calls.find((c) => c.schemaName === 'phase6_scenarios_d1');
  const kinds = ['control', 'isolation', 'combined', 'persistence', 'negative', 'role',
    'state-change', 'manual-batch', 'navigation', 're-entry'];
  const scenarios = S.propOf(call.schema, 'scenarios');
  const checks = S.propOf(call.schema, 'kindChecks');
  assert.ok([...kinds, 'break'].every((k) => S.propOf(scenarios.items, 'kind').enum.includes(k)));
  assert.deepEqual([...checks.required].sort(), [...kinds, 'break'].sort());
  assert.deepEqual(Object.keys(checks.properties).sort(), [...kinds, 'break'].sort());
  for (const kind of [...kinds, 'break']) assert.ok(call.user.includes(kind), `the task names ${kind}`);
  assert.ok(scenarios.maxItems >= 1);
  assert.match(call.user, /no blocking condition/);
  assert.match(call.user, /Reset restoring/);
  assert.match(call.user, /selected one only/);
  assert.match(call.user, /stage under test[\s\S]*how the tester reaches it[\s\S]*which child/);
  // The fake lists only a control scenario, so one note names the nine other kinds, each with its reason.
  const pack = JSON.parse(read(result.packPath));
  const notes = emptyKindNotes(pack);
  assert.equal(notes.length, 1);
  assert.equal(notes[0].assumption, 'UC01 Patron Card Renewal: no scenario was listed for these kinds: isolation,'
    + ' combined, persistence, negative, role, state-change, manual-batch, navigation, re-entry.');
  for (const kind of kinds.slice(1)) assert.ok(notes[0].why.includes(`${kind}: `), `the why gives ${kind} a reason`);
  assert.equal(notes[0].clarification, 'Confirm the document supports none of them.');
  // The break pass found one, so the note leaves break out.
  assert.ok(run.model.calls.some((c) => c.schemaName === 'phase6_scenarios_d1_break'));
  assert.ok(!/break/.test(`${notes[0].assumption} ${notes[0].impact}`));
  // Every card is a Requirement card, so the pack says why none is quality-derived.
  assert.ok(pack.assumptions.some((a) => a.assumption === 'No card in this pack is quality-derived.'));
});

test('scenarios and cards that repeat the same kind, rules, population and action collapse to one', async () => {
  const run = lib({
    phase6_scenarios: inventory([{ population: 'A patron, renewing!', action: 'Renew', rule: 0 },
      { population: 'a patron renewing', action: 'renew.', rule: 0 },
      { population: 'Another patron', rule: 1 }, { ...BREAK, rule: 2 }]),
    // The first card is written twice.
    phase6_cards: (value) => titled({ ...value, cards: [value.cards[0], ...value.cards] }),
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(pack.testCards.map((c) => c.title).sort(), ['Case S1', 'Case S2', 'Case S3']);
  // One scenario dropped from the inventory, one repeated card.
  const pass = phase6Pass(result.outDir);
  assert.equal(pass.duplicates, 2);
  assert.equal(pass.scenarios, 3);
});

test('the same population and action under another kind is a different scenario', async () => {
  const run = lib({ phase6_scenarios: inventory([{ kind: 'control', population: 'p', action: 'a', rule: 0 },
    { kind: 'isolation', population: 'p', action: 'a', rule: 0 }, { ...BREAK, rule: 1 }]) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(phase6Pass(result.outDir).scenarios, 3);
});

test('each card carries the kind of the scenario it was written for', async () => {
  // S1 and S2 come from the inventory; BR-LIB.UC01-005 is left out, so code adds S3 for it; the break pass adds S4.
  const rule = (n) => `BR-LIB.UC01-00${n}`;
  const run = lib({
    phase6_scenarios_d1_break: inventory([{ ...BREAK, population: 'junk input', action: 'enter junk', rule: 0 }]),
    phase6_scenarios: (value) => ({ ...value, scenarios: [
      { kind: 'control', population: 'p0', action: 'a0', outcome: 'o', rules: [rule(1), rule(2)] },
      { kind: 'isolation', population: 'p1', action: 'a1', outcome: 'o', rules: [rule(3), rule(4)] }] }),
    phase6_cards: titled,
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(pack.testCards.map((c) => [c.title, c.kind]).sort(), [['Case S1', 'control'],
    ['Case S2', 'isolation'], ['Case S3', 'decision'], ['Case S4', 'break']]);
});

test('a suite pack\'s cards reach the merge with their scenario\'s kind and none of the design pass\'s marks', async () => {
  const model = fakeModel({ phase6_scenarios: inventory([{ kind: 'isolation' }, { kind: 'role' }]),
    phase6_cards: titled });
  const result = await runJob(fixtureConfig(), { suite: 'LIB' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const { testCards } = JSON.parse(read(result.packPath));
  assert.ok(testCards.length >= 4);
  assert.ok(testCards.every((card) => !('scenario' in card) && !('breakIt' in card) && !('key' in card)));
  assert.deepEqual([...new Set(testCards.map((card) => `${card.title}: ${card.kind}`))].sort(),
    ['Case S1: isolation', 'Case S2: role']);
});

test('a scenario no card covers is asked for once more, then recorded and its rule gets a gap row', async () => {
  const run = lib({
    phase6_scenarios: inventory([{}, {}, {}]),
    phase6_cards: (value) => titled({ ...value, cards: value.cards.filter((c) => c.scenario === 'S1') }),
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const again = run.model.calls.filter((c) => c.schemaName.startsWith('phase6_cards_d1_1b'));
  assert.equal(again.length, 1);
  assert.deepEqual(scenarioEnum(again[0].schema), ['S2', 'S3']);
  assert.match(again[0].user, /needs a card/);
  const pass = phase6Pass(result.outDir);
  assert.equal(pass.retried, 1);
  assert.equal(pass.unsettled, 2);
  const pack = JSON.parse(read(result.packPath));
  for (const id of ['S2', 'S3']) {
    assert.ok(pack.assumptions.some((a) => a.assumption.startsWith(`No test card covers scenario ${id}:`)
      && /no skipped entry/.test(a.why)));
  }
  const missing = pack.coverage.filter((row) => row.status === 'Missing').map((row) => row.ruleId);
  assert.ok(missing.includes('BR-LIB.UC01-002') && missing.includes('BR-LIB.UC01-003'));
});

test('a gap on a rule in one batch does not settle another scenario on that rule', async () => {
  const gap = { ruleId: 'BR-LIB.UC01-001', status: 'Missing', gap: 'gap', recommendation: 'fix' };
  const run = lib({
    phase6_scenarios: inventory([{ rule: 0 }, { rule: 1 }, { rule: 0 }, { ...BREAK, rule: 2 }]),
    // Batch 1 and its retry write a card for S2 only and report a gap on rule 1.
    phase6_cards: (value, calls) => (calls.at(-1).schemaName.startsWith('phase6_cards_d1_1')
      ? { ...titled(value), cards: titled(value).cards.filter((c) => c.scenario === 'S2'), uncovered: [gap] }
      : titled(value)),
  }, { cardScenariosPerCall: 2 });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const second = run.model.calls.find((c) => c.schemaName === 'phase6_cards_d1_2');
  assert.ok(scenarioEnum(second.schema).includes('S3'));
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.testCards.some((c) => c.title === 'Case S3'));
  // S1 stayed open and a later call covered it; nothing is recorded as lost.
  assert.deepEqual(pack.testCards.map((c) => c.title).sort(), ['Case S1', 'Case S2', 'Case S3', 'Case S4']);
  assert.equal(phase6Pass(result.outDir).unsettled, 0);
});

test('a later card on a rule does not unsettle a scenario already skipped', async () => {
  const run = lib({
    phase6_scenarios: inventory([{ rule: 0 }, { rule: 0, population: 'other' }, { ...BREAK, rule: 1 }]),
    phase6_cards: (value, calls) => (calls.at(-1).schemaName === 'phase6_cards_d1_1'
      ? { ...value, cards: [], skipped: [{ scenario: 'S1', how: 'gap', reason: 'cannot be tested' }] }
      : titled(value)),
  }, { cardScenariosPerCall: 1 });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(phase6Pass(result.outDir).unsettled, 0);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(!pack.assumptions.some((a) => a.assumption.includes('scenario S1')));
  assert.deepEqual(pack.testCards.map((c) => c.title).sort(), ['Case S2', 'Case S3']);
});

test('a rule only an existing test covers says so, and points at the test', async () => {
  const run = lib({
    phase6_scenarios: inventory([{}, {}, {}, { ...BREAK, rule: 3 }]),
    phase6_cards: (value) => titled({ ...value, cards: value.cards.filter((c) => c.scenario !== 'S2'),
      skipped: [{ scenario: 'S2', how: 'reused', reason: 'Existing renewal test' }] }),
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(run.model.calls.filter((c) => c.schemaName.startsWith('phase6_cards_d1_1b')).length, 0);
  assert.equal(phase6Pass(result.outDir).unsettled, 0);
  const pack = JSON.parse(read(result.packPath));
  const row = pack.coverage.find((r) => r.ruleId === 'BR-LIB.UC01-002');
  assert.equal(row.status, 'Missing');
  assert.match(row.gap, /Covered only by the existing test Existing renewal test; confirm it and reuse it/);
});

test('the card call reserves room for the scenarios, the cards so far and the existing tests', async () => {
  const name = `existing-tests-${process.pid}.md`;
  fs.writeFileSync(path.join(FIXTURES, name), 'An existing test of the renewal screen. '.repeat(190));
  try {
    const inputs = { ...fixtureInputs(), existingTests: name };
    const model = { endpoint: 'http://localhost:13305/api/v1', name: 'test-model', context: 9000,
      maxOutput: 800, reasoningOutput: 800 };
    const run = lib({}, { inputs, model });
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    const doc = read(path.join(FIXTURES, 'docs/LIB/UC01-Card-Renewal.md'));
    const phrase = doc.split('\n').find((line) => line.length > 40).slice(0, 40);
    const inventoryCall = run.model.calls.find((c) => c.schemaName === 'phase6_scenarios_d1');
    const cardCall = run.model.calls.find((c) => c.schemaName === 'phase6_cards_d1_1');
    // The inventory carries no existing tests, so the document fits whole; the card call does not.
    assert.ok(inventoryCall.user.includes(phrase));
    assert.ok(!cardCall.user.includes(phrase));
    assert.match(cardCall.user, /Document text\s+- points value/);
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

test('rules too large for one inventory call go in batches, each shown the scenarios so far', async () => {
  const name = withMaster((row) => { row.rule_summary = `${row.rule_summary} ${'x'.repeat(30000)}`; });
  try {
    const inputs = { ...fixtureInputs(), ruleExport: ['node', 'export.mjs', '--doc', '{doc}', '--master', name] };
    const run = lib({}, { inputs });
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    const calls = run.model.calls.filter((c) => /^phase6_scenarios_d1_\d$/.test(c.schemaName));
    assert.ok(calls.length >= 2, `${calls.length} inventory calls`);
    assert.ok(!calls[0].user.includes('population value'));
    assert.match(calls[1].user, /Scenarios listed so far\s+- S1 \| control \| rules .* \| population value/);
    // Each call may name only the rules it was given.
    const first = S.propOf(S.propOf(calls[0].schema, 'scenarios').items, 'rules').items.enum;
    const second = S.propOf(S.propOf(calls[1].schema, 'scenarios').items, 'rules').items.enum;
    assert.ok(first.every((id) => !second.includes(id)));
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

test('the empty-kind note joins each kind\'s reasons from every batch, and says when there is none', async () => {
  const name = withMaster((row) => { row.rule_summary = `${row.rule_summary} ${'x'.repeat(30000)}`; });
  try {
    const inputs = { ...fixtureInputs(), ruleExport: ['node', 'export.mjs', '--doc', '{doc}', '--master', name] };
    // Batch 1 leaves isolation's reason blank and each later batch gives one with no closing period;
    // combined is always blank.
    const run = lib({ phase6_scenarios: (value, calls) => {
      if (!value.kindChecks) return value;
      const part = Number(/\d+$/.exec(calls.at(-1).schemaName)[0]);
      return { ...value, kindChecks: { ...value.kindChecks, combined: { note: '' },
        isolation: { note: part === 1 ? ' ' : `Part ${part} has one record` } } };
    } }, { inputs });
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    const batches = run.model.calls.filter((c) => /^phase6_scenarios_d1_\d+$/.test(c.schemaName)).length;
    assert.ok(batches >= 2, `${batches} inventory calls`);
    const notes = emptyKindNotes(JSON.parse(read(result.packPath)));
    assert.equal(notes.length, 1);
    const parts = Array.from({ length: batches - 1 }, (_, i) => `Part ${i + 2} has one record.`).join(' ');
    assert.ok(notes[0].why.startsWith(`isolation: ${parts} combined: no reason was given. `), notes[0].why);
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

// S1 and S2 are requirement cards, S3 is quality-derived and names both special sets.
const SETS = (value) => ({ ...value, cards: value.cards.map((card) => {
  const base = ['Core Change Validation', 'Workflow Validation', 'Negative / Exclusion', 'Regression Testing'];
  const row = { S1: ['Requirement', base], S2: ['Requirement', base],
    S3: ['Quality', [...base, 'Full Coverage Required Run', 'BREAK IT']] }[card.scenario];
  return { ...card, title: `Case ${card.scenario}`, derivation: row[0], objectives: row[1] };
}) });

test('Full Coverage holds every requirement card and BREAK IT only the break scenarios, in several sets at once', async () => {
  const run = lib({ phase6_scenarios: inventory([{}, BREAK, {}]), phase6_cards: SETS });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  // One card per scenario, and no card twice in a set.
  assert.deepEqual(setCards(pack, 'Full Coverage Required Run'), ['Case S1', 'Case S2']);
  assert.deepEqual(setCards(pack, 'BREAK IT'), ['Case S2']);
  // The BREAK IT card is also in Full Coverage and its other ordinary sets, but not in the core set.
  assert.deepEqual(setCards(pack, 'Core Change Validation'), ['Case S1', 'Case S3']);
  assert.ok(pack.testSets.every((set) => set.cards.length === new Set(set.cards).size));
});

test('exclusiveSets keeps a BREAK IT card in the BREAK IT set alone', async () => {
  const run = lib({ phase6_scenarios: inventory([{}, BREAK, {}]), phase6_cards: SETS },
    { exclusiveSets: true });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(setCards(pack, 'BREAK IT'), ['Case S2']);
  assert.deepEqual(setCards(pack, 'Full Coverage Required Run'), ['Case S1']);
  assert.deepEqual(setCards(pack, 'Core Change Validation'), ['Case S1', 'Case S3']);
});

test('with no break scenario listed, a targeted pass asks for break scenarios only and writes their cards', async () => {
  const run = lib({
    phase6_scenarios_d1_break: inventory([{ ...BREAK, population: 'junk input', action: 'enter junk', rule: 0 }]),
    phase6_scenarios: inventory([{}, {}]),
    phase6_cards: titled,
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pass = run.model.calls.find((c) => c.schemaName === 'phase6_scenarios_d1_break');
  assert.deepEqual(S.propOf(S.propOf(pass.schema, 'scenarios').items, 'kind').enum, ['break']);
  assert.equal(S.propOf(pass.schema, 'kindChecks'), undefined);
  assert.match(pass.user, /Scenarios listed so far[^]*S1 \| decision/);
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(setCards(pack, 'BREAK IT'), ['Case S3']);
  assert.equal(pack.objectives.find((r) => r.objective === 'BREAK IT').applicable, true);
  assert.equal(pack.testCards.length, 3);
});

test('with no break scenario at all, BREAK IT stops being applicable', async () => {
  // The break pass returns only what the document already has.
  const run = lib({ phase6_scenarios: inventory([{}, {}]), phase6_cards: titled });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.objectives.find((r) => r.objective === 'BREAK IT').applicable, false);
  assert.deepEqual(setCards(pack, 'BREAK IT'), []);
  assert.match(emptyKindNotes(pack)[0].assumption, /for these kinds: .*\bbreak\b/);
  // The revalidation walk is told how the dropped objective reads, and no rule of a set the pack lacks.
  const [walk] = callsNamed(run, 'phase9_revalidation');
  assert.match(walk.user, /\n- No test card serves BREAK IT, so that objective reads Not Applicable, with a reason that says no test card serves it\. That row is how the pack records the gap, by rule/);
  assert.doesNotMatch(walk.user, /The BREAK IT set holds only/);
});

test('a break-only reply that lists no scenario ends the pass with no card call, and BREAK IT stops being applicable', async () => {
  const run = lib({
    phase6_scenarios_d1_break: (value) => ({ ...value, scenarios: [] }),
    phase6_scenarios: inventory([{}, {}]), phase6_cards: titled,
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const names = run.model.calls.map((c) => c.schemaName);
  assert.equal(names.filter((name) => name === 'phase6_scenarios_d1_break').length, 1);
  assert.ok(!names.some((name) => name.startsWith('phase6_cards_d1_break')));
  const lines = statusLines(result.outDir).filter((l) => l.step === 'scenarios-d1-break');
  assert.deepEqual(lines.map((l) => l.event), ['call']);
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.objectives.find((r) => r.objective === 'BREAK IT').applicable, false);
  assert.deepEqual(setCards(pack, 'BREAK IT'), []);
  assert.ok(!pack.assumptions.some((a) => /cut off/.test(a.assumption)));
  assert.match(emptyKindNotes(pack)[0].assumption, /for these kinds: .*\bbreak\b/);
});

/** Every list and free text of a schema with no longest length, by its path. */
function unbounded(schema, at = '', found = []) {
  if (schema.type === 'array') {
    if (!Number.isInteger(schema.maxItems)) found.push(`${at}[]`);
    return unbounded(schema.items, `${at}[]`, found);
  }
  if (schema.type === 'string' && !schema.enum && !schema.pattern && !Number.isInteger(schema.maxLength)) found.push(at);
  for (const [key, child] of Object.entries(schema.properties ?? {})) unbounded(child, `${at}.${plainKey(key)}`, found);
  return found;
}

test('nothing in a break-only inventory reply can repeat without end, and the list may be empty', async () => {
  const run = lib({
    phase6_scenarios_d1_break: inventory([{ ...BREAK, population: 'junk input', action: 'enter junk', rule: 0 }]),
    phase6_scenarios: inventory([{}, {}]), phase6_cards: titled,
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pass = run.model.calls.find((c) => c.schemaName === 'phase6_scenarios_d1_break');
  assert.deepEqual(unbounded(pass.schema), []);
  const list = S.propOf(pass.schema, 'scenarios');
  assert.equal(list.minItems, 0);
  const rules = S.propOf(list.items, 'rules');
  assert.deepEqual([rules.minItems, rules.maxItems], [1, rules.items.enum.length]);
  for (const field of ['population', 'action', 'outcome']) {
    assert.equal(S.propOf(list.items, field).maxLength, S.SCENARIO_TEXT_MAX, field);
  }
  // The main inventory has to list a scenario, and its scenarios have the same limits.
  const main = run.model.calls.find((c) => c.schemaName === 'phase6_scenarios_d1');
  const all = S.propOf(main.schema, 'scenarios');
  assert.equal(all.minItems, 1);
  assert.equal(S.propOf(all.items, 'rules').maxItems, S.propOf(all.items, 'rules').items.enum.length);
  for (const field of ['population', 'action', 'outcome']) {
    assert.equal(S.propOf(all.items, field).maxLength, S.SCENARIO_TEXT_MAX, field);
  }
  // The server's grammar refuses a repetition of 2000 or more.
  assert.ok(S.SCENARIO_TEXT_MAX < 2000);
});

// A 16384-token reply holds 109 scenarios of 12 kinds, so one kind's share is 9 scenarios;
// the break-only call gets twice the tokens of those: 9 * 150 * 2.
const BREAK_LIMIT = 2700;

test('a break-only reply cut off at its limit ends the pass with a note, and the job goes on', async () => {
  const run = lib({
    phase6_scenarios_d1_break: () => { throw new ModelError('length', 'cut off'); },
    phase6_scenarios: inventory([{}, {}]), phase6_cards: titled,
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  // One call at the limit, never retried, and its schema holds as many scenarios as the share allows.
  const breakCalls = run.model.calls.filter((c) => c.schemaName === 'phase6_scenarios_d1_break');
  assert.deepEqual(breakCalls.map((c) => c.maxTokens), [BREAK_LIMIT]);
  assert.equal(S.propOf(breakCalls[0].schema, 'scenarios').maxItems, 9);
  const lines = statusLines(result.outDir).filter((l) => l.step === 'scenarios-d1-break');
  assert.deepEqual(lines.map((l) => [l.event, l.reason]),
    [['call-fail', 'length'], ['warn', 'break-pass-cut']]);
  assert.equal(lines[0].maxTokens, BREAK_LIMIT);
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.objectives.find((r) => r.objective === 'BREAK IT').applicable, false);
  assert.deepEqual(setCards(pack, 'BREAK IT'), []);
  assert.equal(pack.assumptions.filter((a) => /break scenario list was cut off/.test(a.assumption)).length, 1);
  assertContentFree(JSON.stringify(lines));
});

test('a break-only call that fails without being cut off is retried at the same limit', async () => {
  let tries = 0;
  const run = lib({
    phase6_scenarios_d1_break: (value) => {
      tries += 1;
      if (tries === 1) throw new ModelError('network', 'refused');
      return inventory([{ ...BREAK, population: 'junk input', action: 'enter junk', rule: 0 }])(value);
    },
    phase6_scenarios: inventory([{}, {}]), phase6_cards: titled,
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const breakCalls = run.model.calls.filter((c) => c.schemaName === 'phase6_scenarios_d1_break');
  assert.deepEqual(breakCalls.map((c) => c.maxTokens), [BREAK_LIMIT, BREAK_LIMIT]);
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(setCards(pack, 'BREAK IT'), ['Case S3']);
  assert.ok(!pack.assumptions.some((a) => /cut off/.test(a.assumption)));
});

test('a break-only call that fails, then is cut off at the same limit, ends the pass', async () => {
  let tries = 0;
  const run = lib({
    phase6_scenarios_d1_break: () => {
      tries += 1;
      throw new ModelError(tries === 1 ? 'network' : 'length', 'failed');
    },
    phase6_scenarios: inventory([{}, {}]), phase6_cards: titled,
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const breakCalls = run.model.calls.filter((c) => c.schemaName === 'phase6_scenarios_d1_break');
  assert.deepEqual(breakCalls.map((c) => c.maxTokens), [BREAK_LIMIT, BREAK_LIMIT]);
  const lines = statusLines(result.outDir).filter((l) => l.step === 'scenarios-d1-break');
  assert.deepEqual(lines.map((l) => [l.event, l.reason]),
    [['retry', 'network'], ['call-fail', 'length'], ['warn', 'break-pass-cut']]);
});

test('a cut in a later batch of the break-only pass keeps the scenarios an earlier batch listed', async () => {
  const name = withMaster((row) => { row.rule_summary = `${row.rule_summary} ${'x'.repeat(30000)}`; });
  try {
    const inputs = { ...fixtureInputs(), ruleExport: ['node', 'export.mjs', '--doc', '{doc}', '--master', name] };
    let tries = 0;
    const run = lib({
      phase6_scenarios_d1_break: (value) => {
        tries += 1;
        if (tries > 1) throw new ModelError('length', 'cut off');
        return inventory([{ ...BREAK, population: 'junk input', action: 'enter junk', rule: 0 }])(value);
      },
      phase6_scenarios: inventory([{}, {}]), phase6_cards: titled,
    }, { inputs });
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    // The first batch lists a break scenario, the second is cut, and no third batch is asked.
    assert.equal(run.model.calls.filter((c) => c.schemaName === 'phase6_scenarios_d1_break').length, 2);
    const pack = JSON.parse(read(result.packPath));
    assert.equal(pack.objectives.find((r) => r.objective === 'BREAK IT').applicable, true);
    assert.equal(setCards(pack, 'BREAK IT').length, 1);
    assert.equal(pack.assumptions.filter((a) => /break scenario list was cut off/.test(a.assumption)).length, 1);
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

test('a break-only batch that lists no scenario does not end the pass; the next batch is still asked', async () => {
  const name = withMaster((row) => { row.rule_summary = `${row.rule_summary} ${'x'.repeat(30000)}`; });
  try {
    const inputs = { ...fixtureInputs(), ruleExport: ['node', 'export.mjs', '--doc', '{doc}', '--master', name] };
    let tries = 0;
    const run = lib({
      phase6_scenarios_d1_break: (value) => {
        tries += 1;
        if (tries === 1) return { ...value, scenarios: [] };
        return inventory([{ ...BREAK, population: `junk input ${tries}`, action: 'enter junk', rule: 0 }])(value);
      },
      phase6_scenarios: inventory([{}, {}]), phase6_cards: titled,
    }, { inputs });
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    // The first batch lists nothing, and each of the two after it lists a break scenario.
    assert.equal(run.model.calls.filter((c) => c.schemaName === 'phase6_scenarios_d1_break').length, 3);
    const lines = statusLines(result.outDir).filter((l) => l.step?.startsWith('scenarios-d1-break'));
    assert.ok(!lines.some((l) => l.event === 'warn'));
    const pack = JSON.parse(read(result.packPath));
    assert.equal(pack.objectives.find((r) => r.objective === 'BREAK IT').applicable, true);
    assert.equal(setCards(pack, 'BREAK IT').length, 2);
    assert.ok(!pack.assumptions.some((a) => /cut off/.test(a.assumption)));
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

test('a break-only reply that fills its list gets an assumption that the list reached its limit', async () => {
  const nine = Array.from({ length: 9 }, (_, i) => ({ ...BREAK, population: `junk input ${i}`, action: `enter junk ${i}` }));
  const limitNotes = (pack) => pack.assumptions.filter((a) => /the scenario list reached its limit of 9/.test(a.assumption));
  const full = lib({ phase6_scenarios_d1_break: inventory(nine), phase6_scenarios: inventory([{}, {}]), phase6_cards: titled });
  const result = await runLib(full);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(limitNotes(JSON.parse(read(result.packPath))).length, 1);
  // One scenario short of the limit, the list is taken as whole.
  const short = lib({ phase6_scenarios_d1_break: inventory(nine.slice(1)), phase6_scenarios: inventory([{}, {}]),
    phase6_cards: titled });
  const under = await runLib(short);
  assert.equal(under.ok, true, JSON.stringify(under));
  assert.equal(limitNotes(JSON.parse(read(under.packPath))).length, 0);
});

test('a reply cut off in the main inventory still fails the job', async () => {
  const run = lib({ phase6_scenarios: () => { throw new ModelError('length', 'cut off'); } });
  const result = await runLib(run);
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'model:length');
});

// The break pass lists a break scenario that an existing test covers, so it writes no card.
const BREAK_REUSED = {
  phase6_scenarios_d1_break: inventory([{ ...BREAK, population: 'junk input', action: 'enter junk', rule: 0 }]),
  phase6_cards: (value, calls) => {
    const call = calls.at(-1);
    if (!call.schemaName.startsWith('phase6_cards_d1_break')) return titled(value);
    const [id] = scenarioEnum(call.schema);
    return { ...value, cards: [], skipped: [{ scenario: id, how: 'reused', reason: 'An existing test covers it.' }] };
  },
};

test('a break scenario an existing test covers takes break out of the note, though BREAK IT is dropped', async () => {
  // The break pass is matched before the inventory, whose name it extends.
  const run = lib({ ...BREAK_REUSED, phase6_scenarios: inventory([{}, {}]) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(phase6Pass(result.outDir).unsettled, 0);
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.objectives.find((r) => r.objective === 'BREAK IT').applicable, false);
  const notes = emptyKindNotes(pack);
  assert.equal(notes.length, 1);
  assert.match(notes[0].assumption, /for these kinds: control, isolation,/);
  assert.ok(!/break/.test(`${notes[0].assumption} ${notes[0].why} ${notes[0].impact}`));
});

// One scenario of every required kind but break.
const ALL_BUT_BREAK = ['control', 'isolation', 'combined', 'persistence', 'negative', 'role', 'state-change',
  'manual-batch', 'navigation', 're-entry'].map((kind) => ({ kind }));
// The pack of a run whose inventory lists ALL_BUT_BREAK unless `extra` gives its own.
const breakOnlyEmpty = async (extra) => {
  const run = lib({ ...extra, phase6_scenarios: extra.phase6_scenarios ?? inventory(ALL_BUT_BREAK) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(phase6Pass(result.outDir).unsettled, 0);
  return JSON.parse(read(result.packPath));
};

test('with break the only kind left empty, a break scenario an existing test covers leaves no note', async () => {
  const pack = await breakOnlyEmpty(BREAK_REUSED);
  assert.equal(pack.objectives.find((r) => r.objective === 'BREAK IT').applicable, false);
  assert.deepEqual(emptyKindNotes(pack), []);
});

test('with break the only kind left empty, a break scenario a card serves leaves no note', async () => {
  const pack = await breakOnlyEmpty({ phase6_scenarios_d1_break: BREAK_REUSED.phase6_scenarios_d1_break,
    phase6_cards: titled });
  assert.equal(pack.objectives.find((r) => r.objective === 'BREAK IT').applicable, true);
  assert.deepEqual(emptyKindNotes(pack), []);
});

test('with break the only kind left empty and no reason given, the note says so', async () => {
  // The break pass lists only what the document already has; the inventory gives break a blank reason.
  const pack = await breakOnlyEmpty({ phase6_scenarios: (value) => {
    const reply = inventory(ALL_BUT_BREAK)(value);
    return value.kindChecks ? { ...reply, kindChecks: { ...value.kindChecks, break: { note: ' ' } } } : reply;
  } });
  const notes = emptyKindNotes(pack);
  assert.deepEqual(notes.map((a) => [a.assumption, a.why]),
    [['UC01 Patron Card Renewal: no break scenario was listed.', 'No reason was given.']]);
});

// No card names Workflow Validation.
const NO_WORKFLOW = (value) => ({ ...titled(value), cards: titled(value).cards.map((card) => ({ ...card,
  objectives: ['Core Change Validation', 'Negative / Exclusion', 'Regression Testing'] })) });

test('an ordinary objective no card names is put to the model against the cards written, and none is added', async () => {
  const run = lib({ phase6_scenarios: inventory([{}, {}, BREAK]), phase6_cards: NO_WORKFLOW });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const asked = run.model.calls.filter((c) => c.schemaName.startsWith('phase6_objective'));
  assert.deepEqual(asked.map((c) => c.schemaName), ['phase6_objective_2']);
  assert.deepEqual(asked[0].schema.properties.cards.items.enum, ['C1', 'C2', 'C3']);
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.testCards.length, 3);
  assert.deepEqual(setCards(pack, 'Workflow Validation'), ['Case S1', 'Case S2', 'Case S3']);
});

test('an ordinary objective no card serves is dropped when the model names none', async () => {
  const run = lib({ phase6_scenarios: inventory([{}, {}, BREAK]), phase6_cards: NO_WORKFLOW,
    phase6_objective: (value) => ({ ...value, cards: [] }) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  const row = pack.objectives.find((r) => r.objective === 'Workflow Validation');
  assert.equal(row.applicable, false);
  assert.deepEqual(setCards(pack, 'Workflow Validation'), []);
});

// No card names Core Change Validation, so its objective pass runs.
const NO_CORE = (value) => ({ ...titled(value), cards: titled(value).cards.map((card) => ({ ...card,
  objectives: ['Workflow Validation', 'Negative / Exclusion', 'Regression Testing'] })) });

test('a flagged break card in a pack with no BREAK IT set is offered to the core objective pass', async () => {
  const run = lib({ phase5: (value) => {
    value.objectives['BREAK IT'].applicable = false;
    return value;
  }, phase6_scenarios: inventory([{}, BREAK]), phase6_cards: NO_CORE });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const asked = run.model.calls.filter((c) => c.schemaName.startsWith('phase6_objective'));
  assert.deepEqual(asked.map((c) => c.schemaName), ['phase6_objective_1']);
  assert.deepEqual(asked[0].schema.properties.cards.items.enum, ['C1', 'C2']);
  assert.match(asked[0].user, /C2 \| Case S2/);
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.objectives.find((r) => r.objective === 'BREAK IT').applicable, false);
  assert.deepEqual(setCards(pack, 'Core Change Validation'), ['Case S1', 'Case S2']);
});

test('a flagged break card in a pack with a BREAK IT set stays out of the core objective pass', async () => {
  const run = lib({ phase6_scenarios: inventory([{}, BREAK]), phase6_cards: NO_CORE });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const asked = run.model.calls.filter((c) => c.schemaName.startsWith('phase6_objective'));
  assert.deepEqual(asked.map((c) => c.schemaName), ['phase6_objective_1']);
  assert.deepEqual(asked[0].schema.properties.cards.items.enum, ['C1']);
  assert.doesNotMatch(asked[0].user, /Case S2/);
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(setCards(pack, 'Core Change Validation'), ['Case S1']);
  assert.deepEqual(setCards(pack, 'BREAK IT'), ['Case S2']);
});

const DROP_RUN = {
  phase6_scenarios: inventory([{}, {}, BREAK]), phase6_cards: NO_WORKFLOW,
  phase6_objective: (value) => ({ ...value, cards: [] }),
};

test('a dropped objective gets a reason of its own and a limitation, not the old reason with a suffix', async () => {
  const run = lib({ ...DROP_RUN });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  const row = pack.objectives.find((r) => r.objective === 'Workflow Validation');
  assert.equal(row.applicable, false);
  assert.doesNotMatch(row.reason, /could be designed|can be designed|could be tested|can be tested|no test card could/i);
  assert.match(row.reason, /^Not tested in this pack: no test card serves it/);
  assert.match(pack.limitations['Objective Matrix'], /Applicable but untested: no test card serves Workflow Validation/);
});

test('a dropped objective keeps the pack from the highest confidence level and the call is told', async () => {
  const run = lib({ ...DROP_RUN,
    phase9_confidence_overall: (value) => ({ ...value, overall: 'High', reason: 'BR-1 is covered.' }) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.confidence.overall, 'Medium');
  assert.match(pack.confidence.reason, /No test card serves Workflow Validation/);
  const call = run.model.calls.find((c) => c.schemaName === 'phase9_confidence_overall');
  assert.match(call.user, /Objectives applicable but untested/);
  assert.match(call.user, /Workflow Validation/);
});

test('a capped rating does not leave a reason that states the level it replaced', async () => {
  const run = lib({ ...DROP_RUN, phase9_confidence_overall: (value) => ({ ...value, overall: 'High',
    reason: 'Overall confidence is High because BR-1 is covered.' }) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.confidence.overall, 'Medium');
  assert.doesNotMatch(pack.confidence.reason, /confidence is High/i);
  assert.doesNotMatch(pack.executiveSummary.confidence, /confidence is High/i);
});

test('a pack with no dropped objective has no objective limitation and keeps a High rating', async () => {
  const run = lib({ phase6_scenarios: inventory([{}, {}, BREAK]), phase6_cards: NO_WORKFLOW,
    phase6_objective: (value) => ({ ...value, cards: ['C1'] }),
    phase9_confidence_overall: (value) => ({ ...value, overall: 'High', reason: 'BR-1 is covered.' }) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.limitations?.['Objective Matrix'], undefined);
  assert.equal(pack.confidence.overall, 'High');
});

test('Full Coverage is applicable whenever a requirement card exists', async () => {
  const run = lib({
    phase5: (value) => {
      value.objectives['Full Coverage Required Run'].applicable = false;
      return value;
    },
    phase6_scenarios: inventory([{}, BREAK]), phase6_cards: titled,
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  const row = pack.objectives.find((r) => r.objective === 'Full Coverage Required Run');
  assert.equal(row.applicable, true);
  assert.equal(row.reason, 'Applicable: this set holds every requirement-derived card.');
  assert.deepEqual(setCards(pack, 'Full Coverage Required Run'), ['Case S1', 'Case S2']);
});

test('Full Coverage stays not applicable when exclusiveSets leaves no card for it', async () => {
  const run = lib({
    phase5: (value) => {
      value.objectives['Full Coverage Required Run'].applicable = false;
      return value;
    },
    phase6_scenarios: inventory([BREAK, { ...BREAK, population: 'other' }]), phase6_cards: titled,
  }, { exclusiveSets: true });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  const row = pack.objectives.find((r) => r.objective === 'Full Coverage Required Run');
  assert.equal(row.applicable, false);
  assert.deepEqual(setCards(pack, 'Full Coverage Required Run'), []);
  assert.deepEqual(setCards(pack, 'BREAK IT'), ['Case S1', 'Case S2']);
});

test('a reason that ends in a period does not double it in a coverage gap', async () => {
  const run = lib({
    phase6_scenarios: inventory([{}, {}, {}, { ...BREAK, rule: 3 }]),
    phase6_cards: (value) => titled({ ...value, cards: value.cards.filter((c) => c.scenario !== 'S2'),
      skipped: [{ scenario: 'S2', how: 'reused', reason: 'Existing renewal test.' }] }),
  });
  const result = await runLib(run);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(!pack.coverage.some((r) => /\.\./.test(r.gap)));
});

test('a card left in no set never lands in BREAK IT', () => {
  const objectives = (...names) => names.map((objective) => ({ objective, applicable: true }));
  const ctx = (...names) => ({ fullCoverageObjective: 'F', breakItObjective: 'B', config: {},
    job: {}, pack: { objectives: objectives(...names) } });
  const quality = { objectives: ['B'], derivation: 'Quality', breakIt: false };
  assert.deepEqual(setsOf(ctx('F', 'B', 'O'), quality), ['O']);
  assert.deepEqual(setsOf(ctx('F', 'B'), quality), ['F']);
  assert.deepEqual(setsOf(ctx('B'), quality), []);
  assert.deepEqual(setsOf(ctx('F', 'B', 'O'), { ...quality, breakIt: true, objectives: ['O'] }), ['O', 'B']);
});

test('the set objectives and the cards per call come from config, with the usual names as defaults', () => {
  const config = fixtureConfig();
  assert.equal(config.cardScenariosPerCall, 4);
  assert.equal(config.exclusiveSets, false);
  assert.equal(config.fullCoverageObjective, null);
  const named = fixtureConfig({ fullCoverageObjective: 'Full Run', breakItObjective: 'Abuse',
    cardScenariosPerCall: 2, exclusiveSets: true });
  assert.deepEqual([named.fullCoverageObjective, named.breakItObjective, named.cardScenariosPerCall,
    named.exclusiveSets], ['Full Run', 'Abuse', 2, true]);
  assert.throws(() => fixtureConfig({ cardScenariosPerCall: 0 }), /cardScenariosPerCall/);
  assert.throws(() => fixtureConfig({ exclusiveSets: 'yes' }), /exclusiveSets/);
  assert.throws(() => fixtureConfig({ cardRulesPerCall: 4 }), /cardScenariosPerCall/);
});

test('objectiveEvidence defaults to no rules and is checked rule by rule', () => {
  assert.deepEqual(fixtureConfig().objectiveEvidence, []);
  const rule = { id: 'closure', objective: '^integration', claim: 'the change closes a stage',
    terms: ['stage'], reason: 'The stage closes.' };
  assert.deepEqual(fixtureConfig({ objectiveEvidence: [rule] }).objectiveEvidence, [rule]);
  const bad = (change, pattern) => assert.throws(
    () => fixtureConfig({ objectiveEvidence: [{ ...rule, ...change }] }), pattern, JSON.stringify(change));
  assert.throws(() => fixtureConfig({ objectiveEvidence: 'x' }), /objectiveEvidence must be a list/);
  bad({ extra: 1 }, /unknown key: extra/);
  bad({ id: '1 bad' }, /objectiveEvidence\[0\]\.id/);
  bad({ objective: '(' }, /objectiveEvidence\[0\]\.objective is not a valid pattern/);
  bad({ claim: '' }, /\.claim/);
  bad({ reason: undefined }, /\.reason/);
  bad({ terms: [] }, /\.terms must be a non-empty list/);
  bad({ terms: ['ok', '['] }, /objectiveEvidence\[0\]\.terms\[1\] is not a valid pattern/);
  assert.throws(() => fixtureConfig({ objectiveEvidence: [rule, rule] }), /repeats closure/);
});

test('a failed gate stops the run with a content-free status line', async () => {
  const config = fixtureConfig();
  const model = fakeModel({ phase1: (value) => ({ ...value,
    conflicts: ['UC01 page 4 and the defect record disagree on the renewal expiry'] }) });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.phase, 'phase1');
  assert.equal(result.reason, 'gate:source-conflict');
  const last = statusLines(result.outDir).at(-1);
  assert.equal(last.event, 'fail');
  assert.equal(last.conflicts, 1);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
  // The conflict's text stays in the local detail log.
  assert.ok(read(path.join(result.outDir, 'detail.log')).includes('renewal expiry'));
  assert.ok(!fs.readdirSync(result.outDir).some((name) => name.endsWith('.xlsx')));
});

test('blocking missing information stops the gate with a content-free status line', async () => {
  const config = fixtureConfig();
  const model = fakeModel({ phase1: (value) => ({ ...value,
    blockingMissing: ['The renewal fee table named on page 7 was not received'] }) });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'gate:missing-information');
  const last = statusLines(result.outDir).at(-1);
  assert.equal(last.missing, 1);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
  assert.ok(read(path.join(result.outDir, 'work', 'phase1-missing.json')).includes('renewal fee table'));
  assert.ok(!fs.readdirSync(result.outDir).some((name) => name.endsWith('.xlsx')));
});

test('phase 1 keeps the confidence reason and each source\'s information and direct impact', async () => {
  const config = fixtureConfig();
  const model = fakeModel();
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  for (const row of pack.sourceDocuments) {
    assert.equal(typeof row.informationObtained, 'string');
    assert.equal(typeof row.directImpact, 'boolean');
  }
  const summary = JSON.parse(read(path.join(result.outDir, 'work', 'phase1-summary.json')));
  assert.equal(typeof summary.confidenceReason, 'string');
});

test('rules too large for one Phase 1 call are read in batches and their findings stop the gate', async () => {
  const name = withMaster((row) => { row.rule_summary = `${row.rule_summary} ${'x'.repeat(30000)}`; });
  try {
    const inputs = { ...fixtureInputs(), ruleExport: ['node', 'export.mjs', '--doc', '{doc}', '--master', name] };
    const run = lib({}, { inputs });
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    const calls = run.model.calls.filter((c) => /^phase1_rules_\d+$/.test(c.schemaName));
    assert.ok(calls.length >= 2, `${calls.length} rule calls`);
    const ids = calls.map((c) => Object.keys(c.schema.properties.rules.properties));
    assert.ok(ids[0].every((id) => !ids[1].includes(id)));
    const final = run.model.calls.find((c) => c.schemaName.startsWith('phase1_understanding'));
    assert.ok(!/rule\(s\)/.test(final.user));
    const stopped = lib({ phase1_rules_1: (value) => ({ ...value, blockingMissing: ['No fee table'] }) },
      { inputs });
    assert.equal((await runLib(stopped)).reason, 'gate:missing-information');
    const conflicted = lib({ phase1_rules_2: (value) => ({ ...value, conflicts: ['A and B disagree'] }) },
      { inputs });
    assert.equal((await runLib(conflicted)).reason, 'gate:source-conflict');
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

test('Phase 3 sends every rule that fits in one call, and tells each batch of a split that it is a part', async () => {
  const one = lib({});
  assert.equal((await runLib(one)).ok, true);
  const single = one.model.calls.filter((c) => c.schemaName.startsWith('phase3'));
  assert.equal(single.length, 1);
  assert.ok(!/The rules come in/.test(single[0].user));
  // The room shrinks once Phase 1 is done, so only the scope calls are split.
  const config = fixtureConfig();
  const shrink = (value) => {
    Object.assign(config.model, { context: 6000, reasoningOutput: 500, maxOutput: 500, retryOutput: 500 });
    return value;
  };
  const model = fakeModel({ ...INTAKE, ...NOT_REMOVAL, phase1_understanding: shrink });
  const name = withMaster((row) => { row.rule_summary = `${row.rule_summary} ${'word '.repeat(400)}`; });
  try {
    config.inputs = { ...config.inputs,
      ruleExport: ['node', 'export.mjs', '--doc', '{doc}', '--master', name] };
    await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
    const calls = model.calls.filter((c) => c.schemaName.startsWith('phase3'));
    assert.ok(calls.length >= 2, `${calls.length} scope calls`);
    calls.forEach((call, i) => {
      assert.match(call.user, new RegExp(`part ${i + 1} of ${calls.length}\\. The other rules are classified`));
      assert.match(call.user, /never assume a rule is missing/);
    });
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

test('a decision the user must make stops intake as USER DECISION REQUIRED', async () => {
  const config = fixtureConfig();
  const model = fakeModel({ intake_inventory: (value) => ({ ...value,
    decisionsRequired: ['Which of two renewal policies applies'] }) });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'gate:user-decision-required');
  const pack = JSON.parse(read(path.join(result.outDir, 'work', 'partial-pack.json')));
  assert.equal(pack.intake.readiness, 'USER DECISION REQUIRED');
  assert.ok(read(path.join(result.outDir, 'work', 'intake-decisions.json')).includes('renewal policies'));
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('secondary requests are kept at intake and do not stop the job', async () => {
  const config = fixtureConfig();
  const model = fakeModel({ intake_inventory: (value) => ({ ...value,
    secondaryRequests: ['Also update the fines wording'] }) });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(pack.intake.secondaryRequests, ['Also update the fines wording']);
});

test('a candidate document line shows its section headings', () => {
  const line = candidateLine('docs/LIB/UC01.md', '# Card Renewal\n\nSource: UC01.docx\n\n## Expiry\n\n### Grace period\n');
  assert.match(line, /Card Renewal; Expiry; Grace period; source: UC01.docx/);
});

test('a missing description stops intake', async () => {
  const config = fixtureConfig();
  const result = await runJob(config, { issue: '999' }, { model: fakeModel(), echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'gate:missing-inputs');
});

test('a builder FAIL goes back to the model and the repair is applied', async () => {
  const config = fixtureConfig();
  const model = fakeModel({
    phase6_cards: (value) => ({ ...value, cards: value.cards.map((card) => ({ ...card, title: 'REJECT' })) }),
    phase8_repair: (value) => ({ ...value, coverage: [], limitations: [],
      cards: value.cards.map((card) => ({ ...card, title: 'Repaired title' })) }),
  });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.ok(result.repairs >= 1);
  const repair = model.calls.find((c) => c.schemaName.startsWith('phase8_repair'));
  assert.ok(repair.user.includes('rejected title'));
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.testCards.every((card) => card.title === 'Repaired title'));
});

test('repairs are bounded: a FAIL the model cannot fix stops the run', async () => {
  const config = fixtureConfig();
  const model = fakeModel({
    phase6_cards: (value) => ({ ...value, cards: value.cards.map((card) => ({ ...card, title: 'REJECT' })) }),
    phase8_repair: (value) => ({ ...value, coverage: [], limitations: [],
      cards: value.cards.map((card) => ({ ...card, title: 'REJECT' })) }),
  });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'gate:builder-fail');
  assert.equal(model.calls.filter((c) => c.schemaName.startsWith('phase8_repair')).length, 2);
});

test('a prompt too big for the context is refused, not truncated', async () => {
  const config = fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    context: 6000, maxOutput: 500, reasoningOutput: 500 } });
  const model = fakeModel();
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, false);
  // Intake fits; the documents do not, even as digests, and nothing is cut to make them.
  assert.equal(result.reason, 'gate:documents-too-big');
});

test('only a loopback endpoint is accepted', () => {
  assert.equal(localEndpoint('http://localhost:13305/api/v1/'), 'http://localhost:13305/api/v1');
  assert.equal(localEndpoint('http://127.0.0.1:8001'), 'http://127.0.0.1:8001');
  for (const url of ['https://api.anthropic.com/v1', 'http://192.168.1.5:13305/v1',
    'http://localhost.example.com/v1', 'not a url']) {
    assert.throws(() => localEndpoint(url));
  }
  assert.throws(() => fixtureConfig({ model: { endpoint: 'https://api.openai.com/v1', name: 'm' } }),
    /loopback/);
});

test('the client contacts only the configured endpoint and the loopback backend', async () => {
  const urls = [];
  const fetchImpl = async (url, options) => {
    urls.push(String(url));
    if (String(url).endsWith('/health')) {
      return { json: async () => ({ all_models_loaded: [{ model_name: 'm',
        backend_url: 'http://127.0.0.1:8001/v1' }] }) };
    }
    if (String(url).endsWith('/tokenize')) return { json: async () => ({ tokens: [1, 2, 3] }) };
    const body = JSON.parse(options.body);
    assert.equal(body.response_format.type, 'json_schema');
    assert.equal(body.chat_template_kwargs.enable_thinking, true);
    // A streamed reply is one the server stops generating when the connection closes.
    assert.deepEqual([body.stream, body.stream_options], [true, { include_usage: true }]);
    return streamed({ content: '{"a":1}', usage: { prompt_tokens: 3, completion_tokens: 2 } });
  };
  const client = modelClient({ endpoint: 'http://localhost:13305/api/v1', name: 'm', fetchImpl });
  assert.equal(await client.countTokens('three tokens here'), 3);
  const { value } = await client.json({ system: 's', user: 'u', schema: { type: 'object' },
    schemaName: 'x', reasoning: true, maxTokens: 10 });
  assert.deepEqual(value, { a: 1 });
  for (const url of urls) {
    assert.ok(/^http:\/\/(localhost:13305|127\.0\.0\.1:8001)\//.test(url), url);
  }
});

test('calls go out at temperature 0 with a fixed seed unless the config sets others, and say which seed', async () => {
  const bodies = [];
  const fetchImpl = async (url, options) => {
    const body = JSON.parse(options.body);
    bodies.push(body);
    return streamed({ finish: body.max_tokens === 1 ? 'length' : 'stop' });
  };
  const request = { system: 's', user: 'u', schema: { type: 'object' }, schemaName: 'x', reasoning: false, maxTokens: 10 };
  const model = (settings) => fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm', ...settings } }).model;
  // Built as a run builds it, from the config's model block.
  const defaults = modelClient({ ...model({}), fetchImpl });
  const replies = [await defaults.json(request), await defaults.json(request)];
  assert.deepEqual(bodies.map((b) => [b.temperature, b.seed]), [[0, DEFAULT_SEED], [0, DEFAULT_SEED]]);
  assert.deepEqual(replies.map((r) => r.seed), [DEFAULT_SEED, DEFAULT_SEED]);
  const configured = modelClient({ ...model({ temperature: 0.2, seed: 7 }), fetchImpl });
  assert.equal((await configured.json(request)).seed, 7);
  assert.deepEqual([bodies.at(-1).temperature, bodies.at(-1).seed], [0.2, 7]);
  // A failed call still says which seed it was sent with.
  await assert.rejects(configured.json({ ...request, maxTokens: 1 }),
    (error) => error.code === 'length' && error.seed === 7);
  // 0 is a seed like any other; -1 and the top 32-bit value mean a random seed to llama.cpp.
  assert.equal(model({ seed: 0 }).seed, 0);
  for (const seed of [-1, 4294967295, 1.5, '7', null]) {
    assert.throws(() => model({ seed }), /model\.seed must be a whole number from 0 to 4294967294/, String(seed));
  }
  assert.throws(() => model({ temperature: 0.3 }), /model\.temperature/);
});

test('no pipeline module reaches the network except the model client and the waiting notice', () => {
  for (const name of fs.readdirSync(HERE).filter((n) => n.endsWith('.mjs') && !n.endsWith('.test.mjs'))) {
    const source = read(path.join(HERE, name));
    if (name === 'model.mjs') continue;
    // The notice posts one content-free line, the job ID and counts, and nothing else.
    const allowed = name === 'supervisor.mjs'
      ? source.replace(/export async function postNotice\(url, text\) \{\n.*\bfetch\(url, \{ method: 'POST', body: text,/, '')
      : source;
    assert.ok(!/\bfetch\(|node:https?|node:net|https?:\/\//.test(allowed), `${name} reaches the network`);
  }
});

/** An ask context over a fake server; `finish(body, n)` gives call n's finish reason. */
async function askOver(finish, { model = {}, phase = 'phase1', step = 's', reasoning = true, tokens = 10 } = {}) {
  const bodies = [];
  const fetchImpl = async (url, options) => {
    const body = JSON.parse(options.body);
    bodies.push(body);
    const how = finish(body, bodies.length);
    if (how === 'no-body') return { ok: true, text: async () => '' };
    if (how === 'reset') throw Object.assign(new Error('socket hang up'), { code: 'ECONNRESET' });
    return streamed({ finish: how, content: '{"ok":true}', usage: { completion_tokens: 7 } });
  };
  const config = fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm', ...model } });
  const { ask } = await import('./phases.mjs');
  const lines = [];
  const ctx = { config, calls: 0, tokens: { prompt: 0, output: 0 }, job: { id: 'j' },
    logs: { status: (fields) => lines.push(fields), detail() {}, call() {} },
    model: { ...modelClient({ endpoint: 'http://localhost:1/v1', name: 'm', fetchImpl }),
      countTokens: async () => tokens, contextWindow: async () => null } };
  const run = () => ask(ctx, { phase, step, reasoning, inputs: [],
    schema: { type: 'object' }, task: 't' });
  return { run, bodies, lines, ctx };
}

test('a thinking reply cut off at length is retried once with thinking off and the smaller retry cap', async () => {
  const { run, bodies, lines } = await askOver((body) => (
    body.chat_template_kwargs.enable_thinking ? 'length' : 'stop'));
  assert.deepEqual(await run(), { ok: true });
  assert.equal(bodies.length, 2);
  assert.deepEqual(bodies.map((body) => body.max_tokens), [40960, 8192]);
  const retry = lines.find((line) => line.event === 'retry');
  assert.equal(retry.reasoning, true);
  assert.equal(retry.maxTokens, 40960);
  assert.equal(retry.reason, 'length');
});

test('a thinking call that fails without being cut off is retried at the plain cap', async () => {
  const { run, bodies } = await askOver((body, n) => (n === 1 ? 'no-body' : 'stop'));
  assert.deepEqual(await run(), { ok: true });
  assert.deepEqual(bodies.map((body) => body.max_tokens), [40960, 16384]);
  assert.equal(bodies[1].chat_template_kwargs.enable_thinking, false);
});

test('the retry line of a call whose connection failed says what the failure was', async () => {
  const { run, lines } = await askOver((body, n) => (n === 1 ? 'reset' : 'stop'));
  assert.deepEqual(await run(), { ok: true });
  const retry = lines.find((line) => line.event === 'retry');
  assert.deepEqual([retry.reason, retry.cause], ['network', 'ECONNRESET']);
  assert.doesNotThrow(() => statusFields(retry));
  // A failure that is not a connection's has no cause to give.
  const cut = await askOver((body) => (body.chat_template_kwargs.enable_thinking ? 'length' : 'stop'));
  await cut.run();
  assert.ok(!('cause' in cut.lines.find((line) => line.event === 'retry')));
});

test('a reply cut off with thinking off is not retried', async () => {
  const { run, bodies, lines } = await askOver(() => 'length', { reasoning: false });
  await assert.rejects(run(), (error) => error.code === 'length');
  assert.equal(bodies.length, 1);
  const fail = lines.find((line) => line.event === 'call-fail');
  assert.equal(fail.reason, 'length');
  assert.equal(fail.reasoning, false);
  assert.equal(fail.maxTokens, 16384);
  assert.ok(!lines.some((line) => line.event === 'retry' || line.event === 'fail'));
});

test('a thinking cut-off whose retry is also cut off fails as runaway', async () => {
  const { run, bodies, lines } = await askOver(() => 'length');
  await assert.rejects(run(), (error) => error.code === 'runaway' && error.usage.outputTokens === 7);
  assert.equal(bodies.length, 2);
  assert.deepEqual(bodies.map((body) => body.max_tokens), [40960, 8192]);
  const fail = lines.find((line) => line.event === 'call-fail');
  assert.equal(fail.reason, 'runaway');
  assert.equal(fail.attempt, 2);
  const config = fixtureConfig();
  const model = fakeModel({ phase1_understanding: () => { throw new ModelError('runaway', 'x'); } });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'model:runaway');
});

test('a per-phase reasoning cap lowers max_tokens for that phase only', async () => {
  const model = { reasoningOutputByPhase: { phase9: 12288 } };
  const capped = await askOver(() => 'stop', { model, phase: 'phase9' });
  await capped.run();
  const other = await askOver(() => 'stop', { model, phase: 'phase1' });
  await other.run();
  assert.deepEqual([capped.bodies[0].max_tokens, other.bodies[0].max_tokens], [12288, 40960]);
  const plain = await askOver(() => 'stop', { model, phase: 'phase9', reasoning: false });
  await plain.run();
  assert.equal(plain.bodies[0].max_tokens, 16384);
});

test('a thinking call that fails without a reply and is then cut off ends as length, not runaway', async () => {
  const { run, bodies, lines } = await askOver((body, n) => (n === 1 ? 'no-body' : 'length'));
  await assert.rejects(run(), (error) => error.code === 'length');
  assert.deepEqual(bodies.map((body) => body.max_tokens), [40960, 16384]);
  assert.equal(lines.find((line) => line.event === 'call-fail').reason, 'length');
});

test('a prompt that fits the first cap but not a retry cap is refused as too-big before any call', async () => {
  // Window 60000: 50000 prompt tokens fit a 2048 phase cap but not the 16384 plain cap a retry can use.
  const model = { context: 60000, reasoningOutput: 20000, reasoningOutputByPhase: { phase9: 2048 } };
  const big = await askOver(() => 'stop', { model, phase: 'phase9', tokens: 50000 });
  await assert.rejects(big.run(), (error) => error.code === 'too-big' && error.promptTokens === 50000);
  assert.equal(big.bodies.length, 0);
  const small = await askOver(() => 'stop', { model, phase: 'phase9', tokens: 40000 });
  assert.deepEqual(await small.run(), { ok: true });
  // With thinking off the first cap is the only one, so the same prompt is sent.
  const plain = await askOver(() => 'stop', { model, phase: 'phase9', reasoning: false, tokens: 40000 });
  assert.deepEqual(await plain.run(), { ok: true });
});

test('a model that runs away through a real client fails the job as model:runaway', async () => {
  const answers = fakeModel({ ...INTAKE });
  const bodies = [];
  const fetchImpl = async (url, options) => {
    const body = JSON.parse(options.body);
    bodies.push(body);
    if (body.chat_template_kwargs.enable_thinking) {
      return streamed({ finish: 'length', content: '{"a":', usage: { completion_tokens: 7 } });
    }
    const { schema, name } = body.response_format.json_schema;
    // Thinking off still runs away once a thinking call has been cut.
    const cutAgain = bodies.some((earlier) => earlier.chat_template_kwargs.enable_thinking);
    const { value } = await answers.json({ schema, schemaName: name });
    return streamed({ finish: cutAgain ? 'length' : 'stop', content: JSON.stringify(value),
      usage: { completion_tokens: 7 } });
  };
  const model = { ...modelClient({ endpoint: 'http://localhost:1/v1', name: 'm', fetchImpl }),
    countTokens: async () => 10, contextWindow: async () => null };
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'model:runaway');
  assert.deepEqual(bodies.slice(-2).map((body) => body.chat_template_kwargs.enable_thinking), [true, false]);
  assert.equal(bodies.at(-1).max_tokens, 8192);
});

test('a built-in step cap applies, with the index of a repeated step left off', async () => {
  const impact = await askOver(() => 'stop', { phase: 'phase4', step: 'impact' });
  await impact.run();
  const rules = await askOver(() => 'stop', { phase: 'phase1', step: 'rules-3' });
  await rules.run();
  const again = await askOver(() => 'stop', { phase: 'phase9', step: 'revalidation-traceability-again' });
  await again.run();
  const unlisted = await askOver(() => 'stop', { phase: 'phase4', step: 'risk-1' });
  await unlisted.run();
  assert.deepEqual([impact, rules, again, unlisted].map((over) => over.bodies[0].max_tokens),
    [8192, 20480, 12288, 40960]);
});

test('each group of the revalidation walk and each part of the senior review has a step cap of its own', async () => {
  const steps = ['revalidation-traceability', 'revalidation-resolution', 'revalidation-readiness',
    'senior-review', 'senior-notes'];
  const asked = [];
  for (const step of steps) {
    const over = await askOver(() => 'stop', { phase: 'phase9', step });
    await over.run();
    asked.push(over.bodies[0].max_tokens);
  }
  assert.deepEqual(asked, [12288, 8192, 8192, 12288, 12288]);
});

test('a step cap from the config beats a phase cap, a phase cap only lowers the built-in step cap, and reasoningOutput caps all', async () => {
  const step = { reasoningOutputByStep: { 'phase4.impact': 2048 }, reasoningOutputByPhase: { phase4: 16384 } };
  const byStep = await askOver(() => 'stop', { model: step, phase: 'phase4', step: 'impact' });
  await byStep.run();
  const phaseOnly = await askOver(() => 'stop',
    { model: { reasoningOutputByPhase: { phase4: 16384 } }, phase: 'phase4', step: 'impact' });
  await phaseOnly.run();
  const lowered = await askOver(() => 'stop',
    { model: { reasoningOutput: 4096 }, phase: 'phase4', step: 'impact' });
  await lowered.run();
  assert.deepEqual([byStep, phaseOnly, lowered].map((over) => over.bodies[0].max_tokens),
    [2048, 8192, 4096]);
  const lower = await askOver(() => 'stop',
    { model: { reasoningOutputByPhase: { phase4: 4096 } }, phase: 'phase4', step: 'impact' });
  await lower.run();
  assert.equal(lower.bodies[0].max_tokens, 4096);
  const stepOverPhase = await askOver(() => 'stop', { model: { reasoningOutput: 3000,
    reasoningOutputByStep: { 'phase4.impact': 2048 } }, phase: 'phase4', step: 'impact' });
  await stepOverPhase.run();
  assert.equal(stepOverPhase.bodies[0].max_tokens, 2048);
  const plain = await askOver(() => 'stop', { phase: 'phase4', step: 'impact', reasoning: false });
  await plain.run();
  assert.equal(plain.bodies[0].max_tokens, 16384);
});

test('a thinking call cut off at its step cap retries with thinking off at the retry cap', async () => {
  const { run, bodies } = await askOver((body) => (body.max_tokens === 8192 && body.chat_template_kwargs
    .enable_thinking ? 'length' : 'stop'), { phase: 'phase4', step: 'impact',
    model: { retryOutput: 4096 } });
  await run();
  assert.deepEqual(bodies.map((body) => body.max_tokens), [8192, 4096]);
  assert.equal(bodies[1].chat_template_kwargs.enable_thinking, false);
});

test('config refuses a bad reasoningOutputByStep', () => {
  const bad = (model) => () => fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    ...model } });
  assert.doesNotThrow(bad({ reasoningOutputByStep: { 'phase4.impact': 4096 } }));
  assert.throws(bad({ reasoningOutputByStep: { 'phase4.risk': 4096 } }), /not a reasoning step/);
  assert.doesNotThrow(bad({ reasoningOutputByStep: { 'phase9.revalidation-resolution': 4096,
    'phase9.senior-notes': 4096 } }));
  // Only each group and each part has a budget, not the whole walk or the whole senior review.
  assert.throws(bad({ reasoningOutputByStep: { 'phase9.revalidation': 4096 } }), /not a reasoning step/);
  assert.throws(bad({ reasoningOutputByStep: { 'phase9.senior': 4096 } }), /not a reasoning step/);
  // The understanding call does not think, so a budget for it would do nothing.
  assert.throws(bad({ reasoningOutputByStep: { 'phase1.understanding': 4096 } }), /not a reasoning step/);
  assert.throws(bad({ reasoningOutputByStep: { 'phase4.impact': 50000 } }), /1024 to model.reasoningOutput/);
  assert.throws(bad({ reasoningOutputByStep: { 'phase4.impact': 0 } }), /1024 to model.reasoningOutput/);
  assert.throws(bad({ reasoningOutputByStep: [4096] }), /must be an object/);
});

test('config refuses a bad reasoningOutputByPhase or retryOutput', () => {
  const bad = (model) => () => fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    ...model } });
  assert.doesNotThrow(bad({ reasoningOutputByPhase: { phase9: 16384 }, retryOutput: 4096 }));
  assert.throws(bad({ reasoningOutputByPhase: { phase2: 4096 } }), /not a reasoning phase/);
  assert.throws(bad({ reasoningOutputByPhase: { phase9: 50000 } }), /1024 to model.reasoningOutput/);
  assert.throws(bad({ reasoningOutputByPhase: { phase9: 0 } }), /1024 to model.reasoningOutput/);
  assert.throws(bad({ reasoningOutputByPhase: [16384] }), /must be an object/);
  assert.throws(bad({ retryOutput: 20000 }), /retryOutput/);
});

test('splitting keeps every character and stays under the limit', () => {
  const text = Array.from({ length: 200 }, (_, i) => `Paragraph ${i} ${'word '.repeat(i % 40)}`)
    .join('\n\n') + `\n\n${'x'.repeat(5000)}`;
  const pieces = splitText(text, 300);
  assert.ok(pieces.length > 1);
  assert.ok(pieces.every((piece) => piece.length <= 900));
  assert.equal(pieces.join('').replace(/\s/g, ''), text.replace(/\s/g, ''));
  const groups = batches(Array.from({ length: 10 }, (_, i) => i), () => 'abc', 100, 4);
  assert.deepEqual(groups.map((g) => g.length), [4, 4, 2]);
});

test('status fields take only short codes', () => {
  assert.doesNotThrow(() => statusFields({ phase: 'phase6', step: 'cards-UC01-1', ms: 4 }));
  assert.throws(() => statusFields({ reason: 'BR-LIB.UC01-004 is a Direct Change, no card covers it' }));
  assert.throws(() => statusFields({ note: 'a "quoted" value' }));
});

test('the queue runs jobs in order, marks failures, and stops at the cutoff', async () => {
  const config = fixtureConfig();
  assert.throws(() => jobFrom(parseArgs(['--issue', 'abc'])));
  assert.deepEqual(jobFrom(parseArgs(['--issue', '501', '--change', '7001'])),
    { issue: '501', change: '7001' });
  addJob(config, { issue: '501', change: '7001' });
  assert.equal(addJob(config, { issue: '501', change: '7001' }).added, false);
  addJob(config, { suite: 'LIB' });
  addJob(config, { issue: '777' });
  let t = new Date('2026-10-27T22:00:00');
  const clock = () => t;
  const ran = [];
  const run = async (_config, job) => {
    ran.push(job.id);
    t = new Date(t.getTime() + 4.5 * 3600000);
    return job.suite ? { ok: false, phase: 'phase3', reason: 'gate:unclassified-rule', ms: 1 }
      : { ok: true, ms: 1, workbook: '/out/w.xlsx' };
  };
  const done = await drainQueue(config, { cutoff: '07:00', run, clock });
  // 22:00 starts the first job, 02:30 the second; 07:00 has passed when it ends.
  assert.deepEqual(ran, ['issue-501-change-7001', 'suite-LIB']);
  assert.equal(done.length, 2);
  const queue = readQueue(config);
  assert.deepEqual(queue.jobs.map((row) => row.status), ['passed', 'queued', 'queued']);
  const lines = summaryLines(queue);
  assert.match(lines[1], /retry after stopping at phase3 \(gate:unclassified-rule\)/);
  assert.equal(cutoffAfter(new Date('2026-10-27T22:00:00'), '07:00').getDate(), 28);
  assert.throws(() => cutoffAfter(new Date(), '7am'), /HH:MM/);
});

test('the nightly queue takes no job outside its window and retries interrupted rows at once', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501' });
  addJob(config, { issue: '777' });
  const queue = readQueue(config);
  queue.jobs[0].status = 'running';
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  const ran = [];
  const run = async (_config, job) => { ran.push(job.id); return { ok: true, ms: 1 }; };
  // A timer catching up at 08:00 is past the cutoff and before the start.
  const morning = () => new Date('2026-10-28T08:00:00');
  assert.deepEqual(await drainQueue(config, { cutoff: '07:00', start: '22:00', run, clock: morning }), []);
  assert.deepEqual(ran, []);
  const night = () => new Date('2026-10-28T23:00:00');
  await drainQueue(config, { cutoff: '07:00', start: '22:00', run, clock: night });
  // An interrupted run counts as a failed try, and the row is taken again by this very run.
  assert.deepEqual(ran, ['issue-501', 'issue-777']);
  const rows = readQueue(config).jobs;
  assert.deepEqual(rows.map((row) => row.status), ['passed', 'passed']);
  assert.deepEqual(rows[0].failures.map((f) => f.reason), ['interrupted']);
  assert.equal(rows[0].notBefore, undefined);
});

test('a job started on request runs first, then other start-now rows, within the configured cutoff', async () => {
  const dir = scratch('build-pack-q-');
  const config = fixtureConfig({ queue: { file: path.join(dir, 'queue.json'), cutoff: '05:30' } });
  addJob(config, { issue: '100' });
  addJob(config, { issue: '200', now: true });
  addJob(config, { issue: '9415', now: true });
  const ran = [];
  let t = new Date('2026-10-28T14:00:00');
  const run = async (_config, job) => {
    ran.push(job.id);
    t = new Date(t.getTime() + 3600000);
    return { ok: true, ms: 1 };
  };
  const done = await drainQueue(config, { only: 'issue-9415', nowOnly: true, run, clock: () => t });
  // issue-100 is queued for the nightly run and stays queued.
  assert.deepEqual(ran, ['issue-9415', 'issue-200']);
  assert.equal(done.length, 2);
  assert.deepEqual(readQueue(config).jobs.map((row) => row.status), ['queued', 'passed', 'passed']);
  // queue add --now marks a row that is waiting for tonight; a run without nowOnly takes it.
  assert.equal(addJob(config, { issue: '100', now: true }).added, false);
  assert.equal(readQueue(config).jobs[0].now, true);
  // A job ID with no queued row takes nothing, and the rest of the queue waits.
  addJob(config, { issue: '77' });
  assert.deepEqual(await drainQueue(config, { only: 'issue-1', nowOnly: true, run, clock: () => t }), []);
  assert.equal(readQueue(config).jobs.at(-1).status, 'queued');
  // The cutoff is the config's 05:30: a clock that reads 04:00 when the cutoff
  // is set and 06:00 when the job would start leaves the job queued.
  addJob(config, { issue: '55' });
  const reads = [new Date('2026-10-29T04:00:00'), new Date('2026-10-29T06:00:00')];
  const clock = () => reads.shift() ?? reads.at(-1) ?? new Date('2026-10-29T06:00:00');
  assert.deepEqual(await drainQueue(config, { only: 'issue-55', nowOnly: true, run, clock }), []);
  assert.equal(readQueue(config).jobs.at(-1).status, 'queued');
});

test('a start request while another run holds the queue leaves the row queued', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '9415' });
  // This process is alive, so it stands in for the holder.
  const lock = `${config.at(config.queue.file)}.lock`;
  fs.writeFileSync(lock, String(process.pid));
  assert.equal(lockHeld(config), true);
  let busy = 0;
  const run = async () => { throw new Error('must not run'); };
  assert.deepEqual(await drainQueue(config, { only: 'issue-9415', onBusy: () => { busy += 1; }, run }), []);
  assert.equal(busy, 1);
  assert.match(jobStatus(config, 'issue-9415')[0], /issue-9415  queued  queue held/);
  fs.rmSync(lock);
});

test('a lock file left by a dead process is not a holder', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '9415' });
  const lock = `${config.at(config.queue.file)}.lock`;
  const run = async () => ({ ok: true, ms: 1 });
  // A dead PID, an empty file, PID 0, junk, and a live PID with another start time.
  for (const text of ['2147483646', '', '0', 'abc', `${process.pid} 1`]) {
    fs.writeFileSync(lock, text);
    assert.equal(lockHeld(config), false, `lock text "${text}"`);
    addJob(config, { issue: '9415' });
    const done = await drainQueue(config, { only: 'issue-9415', run });
    assert.equal(done.length, 1, `lock text "${text}"`);
    assert.equal(fs.existsSync(lock), false);
    assert.deepEqual(fs.readdirSync(path.dirname(lock)).filter((f) => f.includes('.lock')), []);
  }
});

test('a queue run behind a holder waits for the queue, and a start retries once', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '100' });
  const lock = `${config.at(config.queue.file)}.lock`;
  fs.writeFileSync(lock, String(process.pid));
  let t = new Date('2026-10-28T22:00:00');
  const naps = [];
  // Each nap is half an hour on the clock; the holder lets go on the third.
  const sleep = async (ms) => {
    naps.push(ms);
    t = new Date(t.getTime() + 1800000);
    if (naps.length === 3) fs.rmSync(lock);
  };
  const ran = [];
  const run = async (_config, job) => { ran.push(job.id); return { ok: true, ms: 1 }; };
  const done = await drainQueue(config, { wait: true, run, sleep, clock: () => t,
    settleMs: 5, pollMs: 7 });
  assert.deepEqual(naps, [5, 7, 7]);
  assert.deepEqual(ran, ['issue-100']);
  assert.equal(done.length, 1);
  // A holder that never lets go ends the wait at the cutoff, with nothing run.
  addJob(config, { issue: '200' });
  fs.writeFileSync(lock, String(process.pid));
  t = new Date('2026-10-28T22:00:00');
  let busy = 0;
  assert.deepEqual(await drainQueue(config, { wait: true, run, sleep: async () => {
    t = new Date(t.getTime() + 4 * 3600000);
  }, clock: () => t, onBusy: () => { busy += 1; } }), []);
  assert.equal(busy, 1);
  // A start waits once, then reports busy; a holder that finishes in that wait is not busy.
  let napped = 0;
  await drainQueue(config, { only: 'issue-200', nowOnly: true, run, onBusy: () => { busy += 1; },
    sleep: async () => { napped += 1; } });
  assert.equal(napped, 1);
  assert.equal(busy, 2);
  fs.rmSync(lock);
  assert.equal((await drainQueue(config, { run })).length, 1);
});

test('queue add says what it did to a row already open', () => {
  const config = fixtureConfig();
  addJob(config, { issue: '100' });
  assert.deepEqual(addJob(config, { issue: '100' }), { id: 'issue-100', added: false, running: false });
  assert.deepEqual(addJob(config, { issue: '100', now: true, resume: true }),
    { id: 'issue-100', added: false, marked: true, merged: ['resume'] });
  // Derived rules and the named documents are merged into the open row too.
  assert.deepEqual(addJob(config, { issue: '100', allowDerivedRules: true, docs: ['docs/a.md'] }),
    { id: 'issue-100', added: false, merged: ['allowDerivedRules', 'docs'] });
  assert.deepEqual(addJob(config, { issue: '100', allowDerivedRules: true, docs: ['docs/a.md'] }),
    { id: 'issue-100', added: false, running: false });
  const [row] = readQueue(config).jobs;
  assert.equal(row.now, true);
  assert.equal(row.resume, true);
  assert.equal(row.allowDerivedRules, true);
  assert.deepEqual(row.docs, ['docs/a.md']);
  Object.assign(row, { status: 'running' });
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify({ jobs: [row] }));
  assert.equal(addJob(config, { issue: '100', now: true }).running, true);
});

test('a nightly row stays queued after a start, and a plain run still takes every row', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '100' });
  addJob(config, { issue: '9415', now: true });
  const ran = [];
  const run = async (_config, job) => { ran.push([job.id, job.now]); return { ok: true, ms: 1 }; };
  await drainQueue(config, { only: 'issue-9415', nowOnly: true, run });
  assert.deepEqual(ran, [['issue-9415', undefined]]);
  assert.deepEqual(readQueue(config).jobs.map((row) => row.status), ['queued', 'passed']);
  await drainQueue(config, { run });
  assert.deepEqual(readQueue(config).jobs.map((row) => row.status), ['passed', 'passed']);
});

test('queue status and the report name a thinking step cut at its output budget on two queue runs in a row', async () => {
  const config = fixtureConfig();
  // Each run starts a fresh log, as a run that does not resume does, and asks two thinking
  // steps; a step named in `cuts` runs out its budget and the retry with thinking off answers.
  const runWith = (cuts) => async (_config, job) => {
    fs.rmSync(path.join(config.output, job.id), { recursive: true, force: true });
    const logs = jobLogs(path.join(config.output, job.id), { echo: false });
    for (const step of ['understanding', 'rules-1']) {
      const base = { job: job.id, phase: 'phase1', step, attempt: 1, reasoning: true, ms: 1 };
      if (cuts.includes(step)) {
        logs.status({ ...base, event: 'retry', maxTokens: 12288, reason: 'length', outputTokens: 12288 });
        logs.status({ ...base, event: 'call', attempt: 2, reasoning: false, promptTokens: 1, outputTokens: 1 });
      } else logs.status({ ...base, event: 'call', promptTokens: 1, outputTokens: 1 });
    }
    return { ok: true, ms: 1 };
  };
  const drain = async (cuts) => {
    addJob(config, { issue: '9415' });
    await drainQueue(config, { run: runWith(cuts) });
  };
  const flagged = () => jobStatus(config, 'issue-9415').filter((line) => line.startsWith('repeated-cut'));
  const report = () => reportData(config, readQueue(config),
    { now: new Date(Date.now() + 60000), random: seededRandom(1) });
  await drain(['understanding', 'rules-1']);
  // One cut names nothing.
  assert.deepEqual(flagged(), []);
  assert.deepEqual(report().repeatedCuts, []);
  assert.match(renderReport(report()), /## Steps cut at their output budget\n\nNone\./);
  await drain(['understanding']);
  assert.deepEqual(flagged(), ['repeated-cut step=phase1.understanding budget=12288 runs=2']);
  assert.deepEqual(report().repeatedCuts, [{ id: 'issue-9415', step: 'phase1.understanding', budget: 12288, runs: 2 }]);
  const text = renderReport(report());
  assert.ok(text.includes('- issue-9415: phase1.understanding was cut at its output budget of 12288 tokens'
    + ' on its last 2 runs. With the server\'s thinking budget set, raise its output budget with'
    + ' `model.reasoningOutputByStep`; without it, turn its thinking off.\n'), text);
  assertContentFree(text);
  // A run that asks the step and answers ends the streak.
  await drain([]);
  assert.deepEqual(flagged(), []);
  assert.deepEqual(report().repeatedCuts, []);
});

test('a run that never asks a step neither breaks nor extends its streak of cuts, and a cut with thinking off is none', () => {
  const senior = { asked: ['phase9.senior-notes'], cut: [{ step: 'phase9.senior-notes', budget: 12288 }] };
  const resumedPast = { asked: ['phase1.rules'], cut: [] };
  assert.deepEqual(repeatedCuts([senior, resumedPast, senior]), [{ step: 'phase9.senior-notes', budget: 12288, runs: 2 }]);
  assert.deepEqual(repeatedCuts([senior, resumedPast]), []);
  assert.deepEqual(repeatedCuts([senior, senior, senior]), [{ step: 'phase9.senior-notes', budget: 12288, runs: 3 }]);
  const plain = { phase: 'phase9', step: 'checklist-1', event: 'call-fail', attempt: 1, reasoning: false,
    maxTokens: 8192, reason: 'length' };
  const thinking = { phase: 'phase9', step: 'revalidation-traceability-again', event: 'retry', attempt: 1,
    reasoning: true, maxTokens: 12288, reason: 'length' };
  assert.deepEqual(runCuts([plain, thinking]), { asked: ['phase9.revalidation-traceability'],
    cut: [{ step: 'phase9.revalidation-traceability', budget: 12288 }] });
});

test('a run releases only its own lock', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '9415' });
  const lock = `${config.at(config.queue.file)}.lock`;
  // Another holder replaces the lock while the job runs.
  const run = async () => { fs.writeFileSync(lock, `${process.pid} other`); return { ok: true, ms: 1 }; };
  await drainQueue(config, { run });
  assert.equal(fs.readFileSync(lock, 'utf8'), `${process.pid} other`);
});

test('clearing a stale lock never removes a lock another starter just took', () => {
  const dir = scratch('build-pack-lock-');
  const lock = path.join(dir, 'queue.json.lock');
  // The file still holds what was judged stale: it goes.
  fs.writeFileSync(lock, '2147483646');
  assert.equal(claimStale(lock, '2147483646'), true);
  assert.equal(fs.existsSync(lock), false);
  // The file now holds a live holder's text: it stays.
  fs.writeFileSync(lock, `${process.pid}`);
  assert.equal(claimStale(lock, '2147483646'), false);
  assert.equal(fs.readFileSync(lock, 'utf8'), `${process.pid}`);
  assert.deepEqual(fs.readdirSync(dir), ['queue.json.lock']);
  // Nothing to remove counts as cleared.
  fs.rmSync(lock);
  assert.equal(claimStale(lock, 'x'), true);
});

test('job status shows the row and the last status line, and nothing else', async () => {
  const config = fixtureConfig();
  assert.deepEqual(jobStatus(config, 'issue-9415'), ['issue-9415  not queued  queue free']);
  addJob(config, { issue: '9415' });
  const queue = readQueue(config);
  Object.assign(queue.jobs[0], { status: 'running', started: '2026-10-28T10:00:00.000Z' });
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  const dir = path.join(config.output, 'issue-9415');
  fs.mkdirSync(dir, { recursive: true });
  const logPath = path.join(dir, 'status.log');
  // The last line of an earlier attempt is not this attempt's.
  fs.writeFileSync(logPath, `${JSON.stringify({ at: '2026-10-27T10:00:00.000Z', job: 'issue-9415',
    phase: 'phase5', event: 'fail' })}\n`);
  assert.deepEqual(jobStatus(config, 'issue-9415'), ['issue-9415  running  queue free']);
  fs.appendFileSync(logPath,
    `${JSON.stringify({ at: '2026-10-28T10:01:00.000Z', job: 'issue-9415', phase: 'phase2', event: 'start' })}\n`);
  // A line cut off mid-write is skipped.
  fs.appendFileSync(logPath, '{"at":"2026-10-28T10:02:0');
  const clock = () => new Date('2026-10-28T10:01:30.000Z');
  assert.deepEqual(jobStatus(config, 'issue-9415', { clock }),
    ['issue-9415  running  queue free', 'job=issue-9415 phase=phase2 event=start',
      'interrupted phase=phase2 elapsed=30s']);
  fs.appendFileSync(logPath, `\n${JSON.stringify({ at: '2026-10-28T10:03:00.000Z', reason: 'Patron "renewal" text' })}\n`);
  assert.throws(() => jobStatus(config, 'issue-9415', { clock }), /short code/);
});

const logLine = (at, fields) => JSON.stringify({ at, job: 'issue-9415', ...fields });
function seedJob(config, row, lines) {
  addJob(config, { issue: '9415' });
  const queue = readQueue(config);
  Object.assign(queue.jobs[0], row);
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  const dir = path.join(config.output, 'issue-9415');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'status.log'), `${lines.join('\n')}\n`);
}

test('job status shows the running phase, finished phase times and the length cuts', () => {
  const config = fixtureConfig();
  seedJob(config, { status: 'running', added: '2026-11-01T08:00:00.000Z', started: '2026-11-01T08:00:00.000Z' }, [
    logLine('2026-11-01T08:00:01.000Z', { phase: 'phase8', event: 'start' }),
    logLine('2026-11-01T08:10:00.000Z', { phase: 'phase8', event: 'pass', ms: 599000, failed: 0 }),
    logLine('2026-11-01T08:10:01.000Z', { phase: 'phase9', event: 'start' }),
    logLine('2026-11-01T10:10:00.000Z', { phase: 'phase9', step: 'checklist', event: 'retry', attempt: 1,
      reason: 'length', ms: 7200000 }),
    logLine('2026-11-01T12:10:00.000Z', { phase: 'phase9', step: 'checklist', event: 'retry', attempt: 1,
      reason: 'length', ms: 7200000 }),
    logLine('2026-11-01T12:10:01.000Z', { phase: 'phase9', step: 'review-2', event: 'call-fail', attempt: 2,
      reason: 'timeout', ms: 5 }),
  ]);
  const clock = () => new Date('2026-11-01T13:55:01.000Z');
  // With no process holding the queue, the open phase is not progress.
  assert.equal(jobStatus(config, 'issue-9415', { clock })[2], 'interrupted phase=phase9 elapsed=20700s');
  fs.writeFileSync(`${config.at(config.queue.file)}.lock`, `${process.pid}`);
  assert.deepEqual(jobStatus(config, 'issue-9415', { clock }), [
    'issue-9415  running  queue held',
    'job=issue-9415 phase=phase9 step=review-2 event=call-fail attempt=2 reason=timeout ms=5',
    'current phase=phase9 elapsed=20700s',
    'done phase=phase8 ms=599000',
    'retries reason=length count=2',
    'call-fails reason=timeout count=1',
    'cut event=retry phase=phase9 step=checklist reason=length count=2',
  ]);
});

test('job status on a stopped job counts earlier attempts and names where it stopped', () => {
  const config = fixtureConfig();
  seedJob(config, { status: 'queued', resume: true, added: '2026-11-01T08:00:00.000Z',
    failures: [{ at: '2026-11-01T09:00:00.000Z', phase: 'phase9', reason: 'model:length', ms: 1 },
      { at: '2026-11-01T11:00:00.000Z', phase: 'phase9', reason: 'model:runaway', ms: 1 }] }, [
    logLine('2026-11-01T08:00:01.000Z', { phase: 'phase8', event: 'pass', ms: 1000 }),
    logLine('2026-11-01T08:30:00.000Z', { phase: 'phase9', step: 'checklist', event: 'call-fail',
      attempt: 2, reason: 'length', ms: 1 }),
    logLine('2026-11-01T10:30:00.000Z', { phase: 'phase9', step: 'checklist', event: 'call-fail',
      attempt: 2, reason: 'runaway', ms: 1 }),
  ]);
  assert.deepEqual(jobStatus(config, 'issue-9415'), [
    'issue-9415  queued  queue free',
    'stopped phase=phase9 reason=model:runaway',
    'done phase=phase8 ms=1000',
    'call-fails reason=length count=1',
    'call-fails reason=runaway count=1',
    'cut event=call-fail phase=phase9 step=checklist reason=length count=1',
    'cut event=call-fail phase=phase9 step=checklist reason=runaway count=1',
  ]);
});

test('job status on a failed row names its stop and keeps phases finished before a re-add', () => {
  const config = fixtureConfig();
  seedJob(config, { status: 'failed', phase: 'phase9', reason: 'model:length',
    added: '2026-11-02T08:00:00.000Z', finished: '2026-11-02T09:00:00.000Z' }, [
    logLine('2026-11-01T08:00:01.000Z', { phase: 'phase8', event: 'pass', ms: 1000 }),
  ]);
  assert.deepEqual(jobStatus(config, 'issue-9415'), [
    'issue-9415  failed  queue free', 'stopped phase=phase9 reason=model:length', 'done phase=phase8 ms=1000']);
});

test('job status on a queued row added without a resume shows nothing from the old log', () => {
  const config = fixtureConfig();
  seedJob(config, { status: 'queued' }, [
    logLine('2026-11-01T08:00:01.000Z', { phase: 'phase8', event: 'pass', ms: 1000 })]);
  assert.deepEqual(jobStatus(config, 'issue-9415'), ['issue-9415  queued  queue free']);
});

test('queue status without a job lists every row with its phase, reason and last update', () => {
  const config = fixtureConfig();
  assert.deepEqual(queueLines(readQueue(config)), ['queue empty']);
  addJob(config, { issue: '9415' });
  addJob(config, { issue: '9416' });
  addJob(config, { issue: '9417' });
  addJob(config, { issue: '9418' });
  addJob(config, { issue: '9419' });
  const queue = readQueue(config);
  Object.assign(queue.jobs[3], { status: 'passed', phase: 'done', reason: null,
    finished: '2026-11-01T13:00:00.000Z',
    failures: [{ at: '2026-11-01T09:00:00.000Z', phase: 'phase9', reason: 'model:length', ms: 1 }] });
  Object.assign(queue.jobs[4], { status: 'running', started: '2026-11-01T14:00:00.000Z',
    failures: [{ at: '2026-11-01T09:00:00.000Z', phase: 'phase9', reason: 'model:runaway', ms: 1 }] });
  fs.mkdirSync(path.join(config.output, 'issue-9419'), { recursive: true });
  fs.writeFileSync(path.join(config.output, 'issue-9419', 'status.log'),
    `${JSON.stringify({ at: '2026-11-01T14:05:00.000Z', job: 'issue-9419', phase: 'phase3', event: 'start' })}\n`);
  Object.assign(queue.jobs[0], { status: 'failed', phase: 'phase9', reason: 'model:length',
    finished: '2026-11-01T11:00:00.000Z' });
  Object.assign(queue.jobs[1], { status: 'queued', resume: true,
    failures: [{ at: '2026-11-01T09:00:00.000Z', phase: 'phase5', reason: 'interrupted', ms: 1 }] });
  Object.assign(queue.jobs[2], { status: 'removed', finished: '2026-11-01T12:00:00.000Z' });
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  assert.deepEqual(queueLines(readQueue(config), config), [
    'issue-9415  status=failed phase=phase9 reason=model:length updated=2026-11-01T11:00:00.000Z',
    'issue-9416  status=queued phase=phase5 reason=interrupted updated=2026-11-01T09:00:00.000Z',
    'issue-9417  status=removed phase=- reason=- updated=2026-11-01T12:00:00.000Z',
    'issue-9418  status=passed phase=done reason=- updated=2026-11-01T13:00:00.000Z',
    'issue-9419  status=running phase=phase3 reason=- updated=2026-11-01T14:05:00.000Z',
  ]);
});

test('the status of a job a queue run finished shows the release line', async () => {
  const config = releaseConfig();
  const { id } = addJob(config, { issue: '9415' });
  await drainQueue(config, { run: okRun, release: fakeRelease([], { status: 1 }).make });
  assert.deepEqual(jobStatus(config, id), [`${id}  passed  queue free`,
    `job=${id} phase=release event=fail reason=exit-1 ms=${releaseLines(config, id)[0].ms}`]);
});

test('the release line follows the job\'s own last line while the row still runs', () => {
  const config = fixtureConfig();
  addJob(config, { issue: '9415' });
  const queue = readQueue(config);
  Object.assign(queue.jobs[0], { status: 'running', started: '2026-10-28T10:00:00.000Z' });
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  const dir = path.join(config.output, 'issue-9415');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'status.log'), [
    { at: '2026-10-28T10:05:00.000Z', job: 'issue-9415', phase: 'phase5', event: 'start' },
    { at: '2026-10-28T10:06:00.000Z', job: 'issue-9415', phase: 'release', event: 'pass', ms: 900 },
  ].map((line) => `${JSON.stringify(line)}\n`).join(''));
  const clock = () => new Date('2026-10-28T10:10:00.000Z');
  assert.deepEqual(jobStatus(config, 'issue-9415', { clock }), ['issue-9415  running  queue free',
    'job=issue-9415 phase=phase5 event=start', 'job=issue-9415 phase=release event=pass ms=900',
    'interrupted phase=phase5 elapsed=300s']);
});

test('a release failure line does not replace the failed job\'s sheet count in the report', () => {
  const config = fixtureConfig();
  const dir = path.join(config.output, 'issue-300');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'status.log'), [
    { at: '2026-10-28T10:05:00.000Z', job: 'issue-300', phase: 'phase8', event: 'fail', sheets: 3 },
    { at: '2026-10-28T10:06:00.000Z', job: 'issue-300', phase: 'release', event: 'fail', ms: 9 },
  ].map((line) => `${JSON.stringify(line)}\n`).join(''));
  const row = { id: 'issue-300', status: 'failed', phase: 'phase8', reason: 'gate:x', ms: 1,
    finished: '2026-10-28T10:05:30.000Z', failures: [
      { at: '2026-10-28T09:00:00.000Z', phase: 'phase8', reason: 'gate:x', ms: 1 },
      { at: '2026-10-28T10:05:30.000Z', phase: 'phase8', reason: 'gate:x', ms: 1 }] };
  const data = reportData(config, { jobs: [row] }, { period: 'day',
    now: new Date('2026-10-28T12:00:00.000Z'), random: seededRandom(1) });
  assert.equal(data.jobs[0].sheets.fail, 3);
});

test('the client refuses redirects, so a prompt cannot be handed to another host', async () => {
  const seen = [];
  const fetchImpl = async (url, options) => {
    seen.push(options.redirect);
    if (url.endsWith('/health')) return { ok: true, json: async () => ({ all_models_loaded: [] }) };
    return streamed();
  };
  const client = modelClient({ endpoint: 'http://localhost:1/v1', name: 'm', fetchImpl });
  await client.countTokens('x');
  await client.json({ system: 's', user: 'u', schema: {}, schemaName: 'n', maxTokens: 1 });
  assert.ok(seen.length >= 2 && seen.every((value) => value === 'error'));
});

test('one row per key is asked for as an object, so no key repeats or goes missing', async () => {
  const schema = S.understandingSchema({ documents: ['A doc', 'B doc'], keys: ['UC01', 'UC02'],
    inclusions: ['Included'], suite: false });
  assert.deepEqual(schema.properties.modules.required, ['UC01', 'UC02']);
  const reply = S.fromWire(schema, { modules: wireNames(schema.properties.modules,
    { UC01: { module: 'M', abbreviation: 'MA' }, UC02: { module: 'N', abbreviation: 'NA' } }) });
  assert.deepEqual(reply.modules, [{ document: 'UC01', module: 'M', abbreviation: 'MA' },
    { document: 'UC02', module: 'N', abbreviation: 'NA' }]);
});

// Schemas whose objects hold fields that depend on one another are asked for in the order
// they are worked out, whatever order a server hands the properties to the model in.

/** Arguments that build each schema factory, or null for a schema that is a constant. */
const SCHEMA_ARGS = {
  assumptionSchema: null, intakeSchema: null, digestSchema: null, impactSchema: null,
  seniorReviewSchema: null, testerNotesSchema: null, confidenceStepsSchema: null, improvementSchema: null,
  documentPickSchema: [['A doc']],
  understandingSchema: [{ documents: ['A doc'], keys: ['UC01'], inclusions: ['Included'], suite: false }],
  phase1RulesSchema: [['R1']],
  derivedRulesSchema: [['High']],
  ruleConflictSchema: [['R1', 'R2']],
  scopeSchema: [['R1'], ['Direct']],
  reviewTriageSchema: [['Q1']],
  riskSchema: [['R1'], ['High']],
  objectivesSchema: [['O1'], { evidence: ['R1'] }],
  scenarioInventorySchema: [{ ids: ['R1'] }],
  cardSchema: [{ ids: ['R1'], objectives: ['O1'], derivations: ['Requirement'], scenarios: ['S1'] }],
  verificationSchema: [['C1']],
  cardsSchema: [{ ids: ['R1'], objectives: ['O1'], derivations: ['Requirement'],
    uncoveredStatuses: ['Missing'], scenarios: ['S1'] }],
  objectiveCardsSchema: [['C1']],
  setScopesSchema: [['O1']],
  checklistSchema: [{ statuses: ['Covered'] }],
  confidenceOverallSchema: [{ confidence: ['High'] }],
  confidenceFieldSchema: ['rules'],
  revalidationSchema: [{ checks: ['Traceability complete'] }],
  repairSchema: [{ cardIds: ['TC-1'], ids: ['R1'], objectives: ['O1'], derivations: ['Requirement'],
    statuses: ['Covered'], sheets: ['Coverage Matrix'], assumptions: true, newIds: ['R1'] }],
  stepSchema: [['C1']],
};
// The step check's schema lives with the step check, and is held to the same order.
const builtSchemas = () => Object.entries({ ...S, stepSchema }).filter(([name]) => name.endsWith('Schema'))
  .map(([name, schema]) => [name, typeof schema === 'function' ? schema(...(SCHEMA_ARGS[name] ?? [])) : schema]);

/** The order each ordered object is worked out in, by the object's path in its schema. */
const CARD_ORDER = ['title', 'scenario', 'mission', 'focus', 'expected', 'rules', 'objectives', 'derivation', 'steps'];
const COVERAGE_ORDER = ['ruleId', 'status', 'strength', 'gap', 'recommendation'];
const WORKED_OUT = {
  'understandingSchema:.summary': ['change', 'purpose', 'modules', 'existingBehavior', 'newBehavior',
    'rulesIdentified', 'inScope', 'outOfScope', 'missingInformation', 'confidenceReason', 'confidence'],
  'understandingSchema:.sourceDocuments.A doc': ['authority', 'informationObtained', 'directImpact',
    'reason', 'inclusion'],
  'understandingSchema:.modules.UC01': ['module', 'abbreviation'],
  'derivedRulesSchema:.rules[]': ['statement', 'sourcePage', 'summary', 'risk'],
  'ruleConflictSchema:.conflicts[]': ['rules', 'conflict'],
  'scenarioInventorySchema:': ['scenarios', 'kindChecks'],
  'scenarioInventorySchema:.scenarios[]': ['rules', 'kind', 'population', 'action', 'outcome'],
  'cardSchema:': CARD_ORDER,
  'cardsSchema:.cards[]': CARD_ORDER,
  'stepSchema:.cards[].steps[]': ['step', 'possible', 'why'],
  'cardsSchema:.uncovered[]': ['ruleId', 'status', 'gap', 'recommendation'],
  'cardsSchema:.skipped[]': ['scenario', 'how', 'reason'],
  'verificationSchema:.cards.C1': ['why', 'verdict'],
  'checklistSchema:.issues[]': ['section', 'issue', 'fix'],
  'checklistSchema:.coverage[]': COVERAGE_ORDER,
  'confidenceOverallSchema:': ['overall', 'reason', 'criteria'],
  'revalidationSchema:.checks.Traceability complete': ['why', 'verdict', 'fix'],
  'repairSchema:.cards[]': ['id', ...CARD_ORDER.filter((name) => name !== 'scenario')],
  'repairSchema:.newCards[]': CARD_ORDER.filter((name) => name !== 'scenario'),
  'repairSchema:.coverage[]': COVERAGE_ORDER,
};
/** Objects listed in an order that is not their working order, with why it does not matter. */
const ORDER_FREE = [
  [/^assumptionSchema:$|:\.assumptions\[\]$/, 'one statement and independent sentences about it'],
  [/^(cardsSchema|checklistSchema|repairSchema|scopeSchema):$/,
    'each part is answered on its own; the assumptions are a by-product of the rest'],
  ['phase1RulesSchema:', 'the notes and the lists are independent of the rule marks'],
  ['understandingSchema:', 'each part stands on its own'],
  ['intakeSchema:', 'four independent lists'],
  ['objectivesSchema:', 'the evidence rows and the objective rows are independent'],
  ['scenarioInventorySchema:.kindChecks', 'the keys are the scenario kinds, not fields'],
  [/^confidenceStepsSchema:\.steps(\.\w+)?$/,
    'the keys are the assessment steps; a row holds an evidence sentence and a verdict'],
  ['impactSchema:.executiveSummary', 'independent prose fields'],
  ['impactSchema:.impacts', 'independent lists, one per area'],
  ['improvementSchema:.improvementNotes[]', 'independent sentences'],
  ['seniorReviewSchema:.seniorReview', 'independent prose fields'],
  ['testerNotesSchema:.testerNotes', 'independent prose fields'],
];
const orderFree = (id) => ORDER_FREE.some(([match]) => (match instanceof RegExp ? match.test(id) : match === id));

/** Every object of a schema with at least two properties, by its path: `[]` for list items. */
function objectsOf(schema, at = '', found = []) {
  if (schema.type === 'array') return objectsOf(schema.items, `${at}[]`, found);
  if (!schema.properties) return found;
  if (Object.keys(schema.properties).length > 1) found.push([at, schema]);
  for (const [key, child] of Object.entries(schema.properties)) {
    objectsOf(child, `${at}.${plainKey(key)}`, found);
  }
  return found;
}

test('every ordered object reads in the order it is worked out once its properties are sorted', () => {
  const seen = new Set();
  const unlisted = [];
  for (const [name, schema] of builtSchemas()) {
    for (const [at, node] of objectsOf(schema)) {
      const keys = Object.keys(node.properties);
      const sorted = [...keys].sort();
      const id = `${name}:${at}`;
      seen.add(id);
      if (keys.every((key) => plainKey(key) !== key)) {
        assert.deepEqual(sorted.map(plainKey), WORKED_OUT[id], `${id} sorted`);
      } else if (keys.join() !== sorted.join() && !orderFree(id)) {
        unlisted.push(`${id}: ${keys.join(', ')}`);
      }
    }
  }
  // Ask for such an object in the order it is worked out, or say in ORDER_FREE why the order does not matter.
  assert.deepEqual(unlisted, []);
  for (const id of Object.keys(WORKED_OUT)) {
    assert.ok(seen.has(id), `${id} is in WORKED_OUT but no schema has such an object`);
  }
  for (const [match] of ORDER_FREE) {
    assert.ok([...seen].some((id) => (match instanceof RegExp ? match.test(id) : match === id)),
      `${match} is in ORDER_FREE but no schema has such an object`);
  }
});

test('every schema export is built here, so a new one cannot skip the order check', () => {
  for (const [name, schema] of Object.entries(S).filter(([key]) => key.endsWith('Schema'))) {
    assert.ok(name in SCHEMA_ARGS, `${name} is not in SCHEMA_ARGS`);
    assert.equal(typeof schema === 'function', SCHEMA_ARGS[name] !== null, name);
  }
});

test('a reply gives the same value whatever order the server returned its properties in', () => {
  const sortedDeep = (value) => (Array.isArray(value) ? value.map(sortedDeep)
    : value && typeof value === 'object' ? Object.fromEntries(Object.keys(value).sort()
      .map((key) => [key, sortedDeep(value[key])])) : value);
  for (const [name, schema] of builtSchemas()) {
    const reply = sample(schema);
    assert.equal(JSON.stringify(S.fromWire(schema, sortedDeep(reply))), JSON.stringify(S.fromWire(schema, reply)),
      name);
  }
});

test('a reply comes back under the plain names, a keyed object as its rows', () => {
  const verify = S.verificationSchema(['C1', 'C2']);
  const rows = S.fromWire(verify, wireNames(verify, { cards: {
    C1: { why: 'It follows.', verdict: 'follows' },
    C2: { why: 'No rule says so.', verdict: 'does not follow' } } }));
  assert.deepEqual(rows, { cards: [{ card: 'C1', why: 'It follows.', verdict: 'follows' },
    { card: 'C2', why: 'No rule says so.', verdict: 'does not follow' }] });
  assert.deepEqual(Object.keys(rows.cards[0]), ['card', 'why', 'verdict']);
});

test('a reply that ends early is no-reply and quotes none of the body; parse and http stay apart', async () => {
  const request = { system: 's', user: 'u', schema: {}, schemaName: 'n', maxTokens: 1 };
  const over = (reply) => modelClient({ endpoint: 'http://localhost:1/v1', name: 'm', fetchImpl: async () => reply });
  const text = (body) => ({ ok: true, status: 200, text: async () => body });
  const whole = sse({ content: '{"Renewal":1}' });
  // Lemonade answers a request its backend refuses with a 200 holding a bare error object.
  for (const body of ['', '<html>Renewal', '{"error":{"code":400,"message":"Renewal is not allowed"}}',
    'data: {"error":{"message":"Renewal is not allowed"}}\n\n', 'data: Renewal\n\n',
    whole.slice(0, whole.indexOf('data: [DONE]'))]) {
    await assert.rejects(over(text(body)).json(request),
      (error) => error.code === 'no-reply' && !/Renewal/.test(error.message), JSON.stringify(body));
  }
  // A whole stream whose content is not JSON is a parse error, and a refusal by status is http.
  await assert.rejects(over(streamed({ content: 'Renewal' })).json(request),
    (error) => error.code === 'parse' && !/Renewal/.test(error.message));
  await assert.rejects(over({ ok: false, status: 503 }).json(request), (error) => error.code === 'http');
});

test('a failed rule export stops intake unless it says the document has no rules yet', async () => {
  const failing = ['node', '-e', 'process.stderr.write("{doc} is not in the doc map"); process.exit(1)'];
  const outage = fixtureConfig({ inputs: { ...fixtureInputs(), ruleExport: failing } });
  const stopped = await runJob(outage, { issue: '501', change: '7001' },
    { model: fakeModel(), echo: false });
  assert.equal(stopped.ok, false);
  assert.equal(stopped.reason, 'gate:rule-export-failed');
  assertContentFree(read(path.join(stopped.outDir, 'status.log')));

  const noRules = fixtureConfig({ inputs: { ...fixtureInputs(), ruleExport: failing,
    noRules: 'is not in the doc map' } });
  const refused = await runJob(noRules, { issue: '501', change: '7001' },
    { model: fakeModel(), echo: false });
  assert.equal(refused.reason, 'gate:rules-not-extracted');

  const allowed = fixtureConfig({ allowDerivedRules: true, inputs: noRules.inputs });
  const model = fakeModel();
  const derived = await runJob(allowed, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(derived.ok, true);
  assert.ok(model.calls.some((call) => /derive/.test(call.schemaName)));

  // A job can opt in on its own, too.
  const byJob = await runJob(noRules, { issue: '501', change: '7001', allowDerivedRules: true },
    { model: fakeModel(), echo: false });
  assert.equal(byJob.ok, true);
});

const exportFrom = (master) => ['node', 'export.mjs', '--master', master, '--doc', '{doc}'];
const withExport = (master) => fixtureConfig({ inputs: { ...fixtureInputs(), ruleExport: exportFrom(master) } });
const issueJob = (docs) => ({ issue: '501', change: '7001', docs });

/** A model whose Phase 1 marks the named documents as context only. */
const contextOnly = (...names) => fakeModel({ phase1: (value) => {
  for (const name of names) if (value.sourceDocuments) value.sourceDocuments[name].inclusion = 'Supporting Context Only';
  return value;
} });

test('an Included document with no map entry stops Phase 2 with rules-not-extracted', async () => {
  const config = fixtureConfig();
  const model = fakeModel();
  const result = await runJob(config, issueJob(['docs/OTHER/UC09-Unmapped.md']), { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.phase, 'phase2');
  assert.equal(result.reason, 'gate:rules-not-extracted');
  const last = statusLines(result.outDir).at(-1);
  assert.equal(last.documents, 1);
  assert.equal(last.numbers, '1');
  assertContentFree(read(path.join(result.outDir, 'status.log')));
  assert.ok(!model.calls.some((call) => /derive/.test(call.schemaName)));
});

test('a context-only document with no rules does not stop the job', async () => {
  const config = fixtureConfig();
  const model = contextOnly('UC09-Unmapped');
  const result = await runJob(config, issueJob(['docs/LIB/UC01-Card-Renewal.md',
    'docs/OTHER/UC09-Unmapped.md']), { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
});

test('every Included document without rules is reported in one stop', async () => {
  const config = fixtureConfig();
  const result = await runJob(config, issueJob(['docs/OTHER/UC09-Unmapped.md',
    'docs/LIB/UC01-Card-Renewal.md', 'docs/OTHER/UC03-Lost-Cards.md']),
  { model: fakeModel(), echo: false });
  assert.equal(result.reason, 'gate:rules-not-extracted');
  const last = statusLines(result.outDir).at(-1);
  assert.deepEqual([last.documents, last.numbers], [2, '1 3']);
});

test('a Phase 2 stop that names 40 documents still writes its fail line and returns a failed result', async () => {
  const root = scratch('many-docs-');
  fs.cpSync(FIXTURES, root, { recursive: true });
  const docs = Array.from({ length: 40 }, (_, i) => `docs/OTHER/UC${i + 10}-Unmapped.md`);
  for (const doc of docs) {
    fs.copyFileSync(path.join(root, 'docs/OTHER/UC09-Unmapped.md'), path.join(root, doc));
  }
  const result = await runJob(fixtureConfig({ repoRoot: root }), issueJob(docs),
    { model: fakeModel(), echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'gate:rules-not-extracted');
  assert.equal(result.counts.documents, 40);
  const last = statusLines(result.outDir).at(-1);
  assert.equal(last.event, 'fail');
  assert.equal(last.documents, 40);
  assert.ok(last.numbers.length <= FIELD_MAX, last.numbers);
  assert.match(last.numbers, /^1 2 3 /);
  assert.ok(result.counts.numbers.startsWith(last.numbers), 'the cut keeps whole leading numbers');
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('fitCounts keeps a short list whole and cuts a long one at a whole number', () => {
  assert.deepEqual(fitCounts({ documents: 2, numbers: '1 3' }), { documents: 2, numbers: '1 3' });
  const long = Array.from({ length: 40 }, (_, i) => i + 1).join(' ');
  const fitted = fitCounts({ documents: 40, numbers: long });
  assert.equal(fitted.documents, 40);
  assert.ok(fitted.numbers.length <= FIELD_MAX && long.startsWith(`${fitted.numbers} `));
  assert.deepEqual(fitCounts({ numbers: 'x'.repeat(FIELD_MAX + 10) }), { numbers: '' });
});

test('a job resumed after the rules are extracted reads the new export', async () => {
  const config = fixtureConfig();
  const job = issueJob(['docs/OTHER/UC09-Unmapped.md']);
  const stopped = await runJob(config, job, { model: fakeModel(), echo: false });
  assert.equal(stopped.phase, 'phase2');
  config.inputs = { ...config.inputs, ruleExport: exportFrom('exports/fixed.json') };
  const resumed = await runJob(config, { ...job, resume: true }, { model: fakeModel(), echo: false });
  assert.equal(resumed.ok, true, JSON.stringify(resumed));
  assert.deepEqual(JSON.parse(read(resumed.packPath)).rules.map((rule) => rule.id), ['BR-LIB.UC09-001']);
});

/** A rule export that appends each document it is asked for to `log`, then runs the fixture export. */
const loggedExport = (log) => ['node', '-e',
  'const fs = require("fs"); const d = process.argv[2]; fs.appendFileSync(process.argv[1], d + "\\n");'
  + ' const r = require("child_process").spawnSync("node", ["export.mjs", "--doc", d],'
  + ' { stdio: "inherit" }); process.exit(r.status);', log, '{doc}'];

test('queue add --now on a queued row marks it and exits 0', () => {
  const config = fixtureConfig();
  const add = (...args) => spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'queue', 'add',
    '--config', config.file, '--issue', '100', ...args], { encoding: 'utf8' });
  assert.match(add().stdout, /queued issue-100/);
  const again = add('--now');
  assert.equal(again.status, 0, again.stderr);
  assert.match(again.stdout, /marked to start now/);
  const derived = add('--allow-derived-rules');
  assert.equal(derived.status, 0, derived.stderr);
  assert.match(derived.stdout, /updated allowDerivedRules/);
});

test('a run whose intake read usable rules does not export them again in Phase 2', async () => {
  const log = path.join(scratch('exports-'), 'log');
  const config = fixtureConfig();
  config.inputs = { ...config.inputs, ruleExport: loggedExport(log) };
  const model = contextOnly('UC02 Overdue Fines');
  const result = await runJob(config, issueJob(['docs/LIB/UC01-Card-Renewal.md',
    'docs/LIB/UC02-Overdue-Fines.md']), { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.deepEqual(read(log).trim().split('\n').sort(),
    ['docs/LIB/UC01-Card-Renewal.md', 'docs/LIB/UC02-Overdue-Fines.md']);
});

test('Phase 2 names each failing document and stops under the most basic code', async () => {
  const config = fixtureConfig();
  const job = issueJob(['docs/OTHER/UC09-Unmapped.md', 'docs/OTHER/UC03-Lost-Cards.md']);
  const first = await runJob(config, job, { model: fakeModel(), echo: false });
  assert.equal(first.reason, 'gate:rules-not-extracted');
  // The export now fails outright for document 1 while document 2 is still unmapped.
  config.inputs = { ...config.inputs, ruleExport: ['node', '-e',
    'if (process.argv[1].includes("UC09")) { process.stderr.write("boom"); process.exit(1); }'
    + ' const r = require("child_process").spawnSync("node", ["export.mjs", "--doc", process.argv[1]],'
    + ' { stdio: "inherit" }); process.exit(r.status);', '{doc}'] };
  const again = await runJob(config, { ...job, resume: true }, { model: fakeModel(), echo: false });
  assert.equal(again.reason, 'gate:rule-export-failed');
  const lines = statusLines(again.outDir);
  assert.deepEqual(lines.filter((l) => l.event === 'stop-doc').slice(-2).map((l) => [l.document, l.reason]),
    [[1, 'rule-export-failed'], [2, 'rules-not-extracted']]);
  const last = lines.at(-1);
  assert.deepEqual([last.documents, last.numbers], [2, '1 2']);
});

test('an export outage in Phase 2 keeps the rules intake read and warns', async () => {
  const config = fixtureConfig();
  const job = issueJob(['docs/LIB/UC01-Card-Renewal.md', 'docs/OTHER/UC09-Unmapped.md']);
  const first = await runJob(config, job, { model: fakeModel(), echo: false });
  assert.equal(first.reason, 'gate:rules-not-extracted');
  config.inputs = { ...config.inputs, ruleExport: ['node', '-e',
    'const d = process.argv[1]; if (d.includes("UC01")) { process.stderr.write("boom"); process.exit(1); }'
    + ' const r = require("child_process").spawnSync("node", ["export.mjs", "--doc", d,'
    + ' "--master", "exports/fixed.json"], { stdio: "inherit" }); process.exit(r.status);', '{doc}'] };
  const again = await runJob(config, { ...job, resume: true }, { model: fakeModel(), echo: false });
  assert.equal(again.ok, true, JSON.stringify(again));
  assert.ok(statusLines(again.outDir).some((l) => l.event === 'warn' && l.reason === 'rule-export-failed'
    && l.document === 1));
  const ids = JSON.parse(read(again.packPath)).rules.map((rule) => rule.id);
  assert.ok(ids.includes('BR-LIB.UC01-001') && ids.includes('BR-LIB.UC09-001'));
});

test('a document path outside the root gets the path code and no export runs', () => {
  const log = path.join(scratch('exports-'), 'log');
  const config = fixtureConfig();
  config.inputs = { ...config.inputs, ruleExport: ['node', '-e',
    `require("fs").appendFileSync(${JSON.stringify(log)}, process.argv[1]);`, '{doc}'] };
  const ctx = { config, job: { id: 'j' }, logs: { status() {}, detail() {}, call() {} } };
  assert.deepEqual(documentRules(ctx, path.join(FIXTURES, '..', 'phases.mjs')),
    { code: 'document-file', rules: [] });
  assert.deepEqual(documentRules(ctx, path.join(FIXTURES, 'docs')), { code: 'document-file', rules: [] });
  assert.deepEqual(documentRules(ctx, path.join(FIXTURES, 'docs', 'missing.md')),
    { code: 'document-file', rules: [] });
  assert.ok(!fs.existsSync(log), 'the export ran');
});

test('a noRules answer in Phase 2 keeps rules intake read as usable and warns', async () => {
  const config = fixtureConfig();
  const job = issueJob(['docs/LIB/UC01-Card-Renewal.md', 'docs/OTHER/UC09-Unmapped.md']);
  const first = await runJob(config, job, { model: fakeModel(), echo: false });
  assert.equal(first.reason, 'gate:rules-not-extracted');
  config.inputs = { ...config.inputs, ruleExport: ['node', '-e',
    'const d = process.argv[1]; if (d.includes("UC01")) { process.stderr.write(d + " is not in br_doc_map");'
    + ' process.exit(1); }'
    + ' const r = require("child_process").spawnSync("node", ["export.mjs", "--doc", d,'
    + ' "--master", "exports/fixed.json"], { stdio: "inherit" }); process.exit(r.status);', '{doc}'] };
  const again = await runJob(config, { ...job, resume: true }, { model: fakeModel(), echo: false });
  assert.equal(again.ok, true, JSON.stringify(again));
  const lines = statusLines(again.outDir);
  assert.ok(lines.some((l) => l.event === 'warn' && l.reason === 'rules-not-extracted' && l.document === 1));
  assert.ok(!lines.some((l) => l.event === 'stop-doc' && l.document === 1));
  const ids = JSON.parse(read(again.packPath)).rules.map((rule) => rule.id);
  assert.ok(ids.includes('BR-LIB.UC01-001') && ids.includes('BR-LIB.UC09-001'));
});

const noRulesForUc01 = ['node', '-e',
  'const d = process.argv[1]; if (d.includes("UC01")) { process.stderr.write(d + " is not in br_doc_map");'
  + ' process.exit(1); }'
  + ' const r = require("child_process").spawnSync("node", ["export.mjs", "--doc", d,'
  + ' "--master", "exports/fixed.json"], { stdio: "inherit" }); process.exit(r.status);', '{doc}'];

test('a noRules answer keeps the extracted rules when the job allows derived rules', async () => {
  const config = fixtureConfig();
  const job = issueJob(['docs/LIB/UC01-Card-Renewal.md', 'docs/OTHER/UC09-Unmapped.md']);
  const first = await runJob(config, job, { model: fakeModel(), echo: false });
  assert.equal(first.reason, 'gate:rules-not-extracted');
  config.inputs = { ...config.inputs, ruleExport: noRulesForUc01 };
  const model = fakeModel();
  const again = await runJob(config, { ...job, allowDerivedRules: true, resume: true },
    { model, echo: false });
  assert.equal(again.ok, true, JSON.stringify(again));
  assert.ok(statusLines(again.outDir).some((l) => l.event === 'warn' && l.reason === 'rules-not-extracted'
    && l.document === 1));
  assert.ok(!model.calls.some((call) => /derive/.test(call.schemaName)));
  const ids = JSON.parse(read(again.packPath)).rules.map((rule) => rule.id);
  assert.ok(ids.includes('BR-LIB.UC01-001'));
});

test('a held document whose checkpoint path now falls outside the root keeps its rules and warns', async () => {
  const config = fixtureConfig();
  const job = issueJob(['docs/LIB/UC01-Card-Renewal.md', 'docs/OTHER/UC09-Unmapped.md']);
  const first = await runJob(config, job, { model: fakeModel(), echo: false });
  assert.equal(first.reason, 'gate:rules-not-extracted');
  const file = path.join(first.outDir, 'work', 'checkpoint.json');
  const saved = JSON.parse(read(file));
  saved.state.documents[0].file = path.join(FIXTURES, '..', '..', 'SKILL.md');
  fs.writeFileSync(file, JSON.stringify(saved));
  config.inputs = { ...config.inputs, ruleExport: noRulesForUc01 };
  const again = await runJob(config, { ...job, resume: true }, { model: fakeModel(), echo: false });
  assert.equal(again.ok, true, JSON.stringify(again));
  assert.ok(statusLines(again.outDir).some((l) => l.event === 'warn' && l.reason === 'document-file'
    && l.document === 1));
  const ids = JSON.parse(read(again.packPath)).rules.map((rule) => rule.id);
  assert.ok(ids.includes('BR-LIB.UC01-001'));
});

test('a document intake read as rules-not-extracted still stops Phase 2, and a bad checkpoint path does not pass for it', async () => {
  const config = fixtureConfig();
  const job = issueJob(['docs/OTHER/UC09-Unmapped.md']);
  const first = await runJob(config, job, { model: fakeModel(), echo: false });
  assert.equal(first.reason, 'gate:rules-not-extracted');
  const lines = statusLines(first.outDir);
  assert.ok(lines.some((l) => l.event === 'stop-doc' && l.document === 1 && l.reason === 'rules-not-extracted'));
  assert.ok(!lines.some((l) => l.event === 'warn' && l.reason === 'rules-not-extracted'));
  const resumed = await runJob(config, { ...job, resume: true }, { model: fakeModel(), echo: false });
  assert.equal(resumed.reason, 'gate:rules-not-extracted');

  const file = path.join(first.outDir, 'work', 'checkpoint.json');
  const saved = JSON.parse(read(file));
  for (const doc of saved.state.documents) doc.file = path.join(FIXTURES, '..', '..', 'SKILL.md');
  fs.writeFileSync(file, JSON.stringify(saved));
  const outside = await runJob(config, { ...job, resume: true }, { model: fakeModel(), echo: false });
  assert.equal(outside.reason, 'gate:document-file');
});

test('a checkpoint written without document paths resumes without re-reading the export', async () => {
  const config = fixtureConfig();
  const job = issueJob(['docs/OTHER/UC09-Unmapped.md']);
  const first = await runJob(config, job, { model: fakeModel(), echo: false });
  assert.equal(first.phase, 'phase2');
  const file = path.join(first.outDir, 'work', 'checkpoint.json');
  const saved = JSON.parse(read(file));
  for (const doc of saved.state.documents) delete doc.file;
  fs.writeFileSync(file, JSON.stringify(saved));
  // The document keeps the rules it had (none), so Phase 2 derives them rather than crashing.
  const model = fakeModel();
  config.allowDerivedRules = true;
  const resumed = await runJob(config, { ...job, resume: true }, { model, echo: false });
  assert.equal(resumed.ok, true, JSON.stringify(resumed));
  assert.ok(model.calls.some((call) => /derive/.test(call.schemaName)));
});

/** Two roots with the fixtures' files, a config over each, and one output folder both write. */
function twoRoots() {
  const base = scratch('roots-');
  const roots = ['a', 'b'].map((name) => {
    const root = path.join(base, name);
    fs.cpSync(FIXTURES, root, { recursive: true });
    return root;
  });
  const output = path.join(base, 'out');
  const [a, b] = roots.map((repoRoot) => fixtureConfig({ repoRoot, output }));
  return { base, a, b };
}

/** A rule export that reads the master the fixtures' fixed export uses and logs each document. */
const fixedExport = (log) => ['node', '-e',
  'const fs = require("fs"); const d = process.argv[2]; fs.appendFileSync(process.argv[1], d + "\\n");'
  + ' const r = require("child_process").spawnSync("node", ["export.mjs", "--doc", d,'
  + ' "--master", "exports/fixed.json"], { stdio: "inherit" }); process.exit(r.status);', log, '{doc}'];

test('a job checkpointed under one root resumes under another and exports the path relative to it', async () => {
  const { a, b } = twoRoots();
  const job = issueJob(['docs/OTHER/UC09-Unmapped.md']);
  const first = await runJob(a, job, { model: fakeModel(), echo: false });
  assert.equal(first.phase, 'phase2');
  const saved = JSON.parse(read(path.join(first.outDir, 'work', 'checkpoint.json')));
  assert.deepEqual(saved.state.documents.map((doc) => doc.file), ['docs/OTHER/UC09-Unmapped.md']);
  assert.deepEqual(saved.state.documentPaths, ['docs/OTHER/UC09-Unmapped.md']);
  fs.rmSync(a.root, { recursive: true });
  const log = path.join(path.dirname(b.root), 'exports.log');
  b.inputs = { ...b.inputs, ruleExport: fixedExport(log) };
  const resumed = await runJob(b, { ...job, resume: true }, { model: fakeModel(), echo: false });
  assert.equal(resumed.ok, true, JSON.stringify(resumed));
  assert.deepEqual(read(log).trim().split('\n'), ['docs/OTHER/UC09-Unmapped.md']);
});

test('a checkpoint holding an absolute worktree path resumes under the current root', async () => {
  const { a, b } = twoRoots();
  const job = issueJob(['docs/OTHER/UC09-Unmapped.md']);
  const first = await runJob(a, job, { model: fakeModel(), echo: false });
  assert.equal(first.phase, 'phase2');
  const file = path.join(first.outDir, 'work', 'checkpoint.json');
  const saved = JSON.parse(read(file));
  const stale = '/gone/Code/Repo/.claude/worktrees/old-branch/docs/OTHER/UC09-Unmapped.md';
  for (const doc of saved.state.documents) doc.file = stale;
  saved.state.documentPaths = [stale];
  fs.writeFileSync(file, JSON.stringify(saved));
  const log = path.join(path.dirname(b.root), 'exports.log');
  b.inputs = { ...b.inputs, ruleExport: fixedExport(log) };
  const resumed = await runJob(b, { ...job, resume: true }, { model: fakeModel(), echo: false });
  assert.equal(resumed.ok, true, JSON.stringify(resumed));
  assert.deepEqual(read(log).trim().split('\n'), ['docs/OTHER/UC09-Unmapped.md']);
});

test('rootRelative keeps a document path relative to the root whatever it was given as', () => {
  const config = { root: '/repo' };
  assert.equal(rootRelative(config, 'docs/a/B.md'), 'docs/a/B.md');
  assert.equal(rootRelative(config, '/repo/docs/a/B.md'), 'docs/a/B.md');
  assert.equal(rootRelative(config, '/repo/.claude/worktrees/w1/docs/a/B.md'), 'docs/a/B.md');
  assert.equal(rootRelative(config, '/elsewhere/.claude/worktrees/w1/docs/a/B.md'), 'docs/a/B.md');
  assert.equal(rootRelative(config, '/elsewhere/docs/a/B.md'), 'docs/a/B.md');
  assert.equal(rootRelative(config, '/elsewhere/notes.md'), '/elsewhere/notes.md');
  // A path from a worktree whose top folder is above the root is cut to what exists under the root.
  const sub = scratch('sub-');
  fs.mkdirSync(path.join(sub, 'docs'));
  fs.writeFileSync(path.join(sub, 'docs', 'B.md'), '');
  assert.equal(rootRelative({ root: sub }, '/top/.claude/worktrees/w/specs/docs/B.md'), 'docs/B.md');
  assert.equal(rootRelative(config, '/repo/.claude/worktrees/w1'), '.claude/worktrees/w1');
  assert.equal(rootRelative(config, '/repo'), '.');
  // A bare file name never matches an unrelated file, and a relative worktree path is cut too.
  fs.writeFileSync(path.join(sub, 'README.md'), '');
  assert.equal(rootRelative({ root: sub }, `${sub}/.claude/worktrees/w/docs/new/README.md`), 'docs/new/README.md');
  assert.equal(rootRelative({ root: sub }, '.claude/worktrees/w/docs/B.md'), 'docs/B.md');
  // A root that is itself in a worktree still reads its own files as relative.
  assert.equal(rootRelative({ root: '/r/.claude/worktrees/w2/pkg' }, '/r/.claude/worktrees/w2/pkg/docs/B.md'),
    'docs/B.md');
});

/** A git repository holding the fixtures and a pipeline config at its top, and a worktree of it. */
function repoWithWorktree() {
  const base = fs.realpathSync(scratch('wt-'));
  const main = path.join(base, 'main');
  fs.cpSync(FIXTURES, main, { recursive: true });
  const raw = JSON.parse(read(path.join(FIXTURES, 'pipeline.json')));
  Object.assign(raw, { repoRoot: '.', output: path.join(base, 'out'), memory: { enabled: false },
    queue: { file: path.join(base, 'queue.json') }, release: { command: [] } });
  fs.writeFileSync(path.join(main, 'pipeline.json'), JSON.stringify(raw));
  const git = (...args) => {
    const r = spawnSync('git', ['-c', 'user.name=t', '-c', 'user.email=t@t', ...args], { cwd: main, encoding: 'utf8' });
    assert.equal(r.status, 0, r.stderr);
  };
  git('init', '-q', '-b', 'main');
  git('add', '.');
  git('commit', '-q', '-m', 'fixtures');
  const worktree = path.join(base, 'wt');
  git('worktree', 'add', '-q', worktree);
  return { base, main, worktree, queue: path.join(base, 'queue.json') };
}

test('queue add run from a worktree refuses, names the main checkout, and queues nothing', () => {
  const { main, worktree, queue } = repoWithWorktree();
  const env = { ...process.env };
  delete env.BUILD_PACK_ALLOW_WORKTREE;
  const add = (cwd, config) => spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'queue', 'add',
    '--config', path.join(config, 'pipeline.json'), '--issue', '100'], { cwd, env, encoding: 'utf8' });
  const refused = add(worktree, worktree);
  assert.equal(refused.status, 2, refused.stderr);
  assert.ok(refused.stderr.includes(main), refused.stderr);
  assert.ok(refused.stderr.includes(path.join(main, 'pipeline.json')), refused.stderr);
  assert.equal(fs.existsSync(queue), false);
  const ok = add(worktree, main);
  assert.equal(ok.status, 0, ok.stderr);
  assert.match(ok.stdout, /queued issue-100/);
  assert.equal(mainCheckout(main), null);
  assert.equal(mainCheckout(worktree).main, main);
});

test('rootRelative cuts a worktree path by the root folder in its repository, not by guessing a tail', () => {
  const { main } = repoWithWorktree();
  fs.mkdirSync(path.join(main, 'new'), { recursive: true });
  fs.writeFileSync(path.join(main, 'new', 'README.md'), '');
  assert.equal(rootRelative({ root: main }, `${main}/.claude/worktrees/w/docs/new/README.md`), 'docs/new/README.md');
  fs.mkdirSync(path.join(main, 'specs'));
  assert.equal(rootRelative({ root: path.join(main, 'specs') }, `${main}/.claude/worktrees/w/specs/spec/new.md`),
    'spec/new.md');
  assert.equal(rootRelative({ root: main }, '../shared/docs/a.md'), '../shared/docs/a.md');
  // A worktree of another clone is cut by what exists, and a relative path into a worktree is cut too.
  assert.equal(rootRelative({ root: main }, '/old/Other/.claude/worktrees/w/specs/docs/B.md'), 'docs/B.md');
  fs.mkdirSync(path.join(main, 'docs'), { recursive: true });
  fs.writeFileSync(path.join(main, 'docs', 'B.md'), '');
  assert.equal(rootRelative({ root: main }, '/old/Other/.claude/worktrees/w/specs/docs/B.md'), 'docs/B.md');
  assert.equal(rootRelative({ root: path.join(main, 'specs') }, '../.claude/worktrees/w/specs/docs/C.md'), 'docs/C.md');
  // Where the root itself sits never counts as a worktree marker.
  const nested = { root: path.join(main, '.claude', 'worktrees', 'w1', 'proj') };
  assert.equal(rootRelative(nested, '.'), '.');
  assert.equal(rootRelative(nested, path.join(nested.root, 'notes', 'x.md')), 'notes/x.md');
  assert.equal(rootRelative(nested, '../shared/docs/a.md'), '../shared/docs/a.md');
  assert.equal(rootRelative({ root: main }, path.join(main, 'my.claude', 'worktrees', 'z', 'docs', 'q.md')),
    'my.claude/worktrees/z/docs/q.md');
  // An inherited GIT_DIR does not change where the root sits in its repository.
  const was = process.env.GIT_DIR;
  process.env.GIT_DIR = path.join(main, '.git');
  try {
    assert.equal(rootRelative({ root: path.join(main, 'specs') }, `${main}/.claude/worktrees/w/specs/spec/new.md`),
      'spec/new.md');
  } finally {
    if (was === undefined) delete process.env.GIT_DIR; else process.env.GIT_DIR = was;
  }
});

test('queue add stores each document relative to the root', () => {
  const config = fixtureConfig();
  const abs = path.join(config.root, 'docs/LIB/UC01-Card-Renewal.md');
  const add = spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'queue', 'add',
    '--config', config.file, '--issue', '100', '--doc', abs, '--doc', 'docs/LIB/UC02-Overdue-Fines.md'],
  { encoding: 'utf8' });
  assert.equal(add.status, 0, add.stderr);
  assert.deepEqual(JSON.parse(read(config.at(config.queue.file))).jobs[0].docs,
    ['docs/LIB/UC01-Card-Renewal.md', 'docs/LIB/UC02-Overdue-Fines.md']);
});

test('a folder outside a repository is not a worktree', () => {
  const dir = scratch('plain-');
  assert.equal(mainCheckout(dir), null);
  const was = process.env.BUILD_PACK_ALLOW_WORKTREE;
  delete process.env.BUILD_PACK_ALLOW_WORKTREE;
  try {
    assert.equal(worktreeRefusal({ root: dir, file: path.join(dir, 'pipeline.json') }), null);
  } finally {
    process.env.BUILD_PACK_ALLOW_WORKTREE = was;
  }
});

test('a structurally malformed export stops intake, and only detail.log says why', async () => {
  const config = withExport('exports/malformed.json');
  const result = await runJob(config, issueJob(['docs/LIB/UC01-Card-Renewal.md']),
    { model: fakeModel(), echo: false });
  assert.equal(result.phase, 'intake');
  assert.equal(result.reason, 'gate:rules-malformed');
  assert.equal(statusLines(result.outDir).at(-1).document, 1);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
  assert.match(read(path.join(result.outDir, 'detail.log')), /rule_id does not read as/);
});

test('rows the master holds that the procedure would not write are warnings, not a stop', async () => {
  // A legacy category and requirement type, a page with no anchor, and a heading as the page.
  const config = withExport('exports/legacy.json');
  const result = await runJob(config, issueJob(['docs/LIB/UC01-Card-Renewal.md']),
    { model: fakeModel(), echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const detail = read(path.join(result.outDir, 'detail.log'));
  assert.match(detail, /rule_category "Data Entry" is not a current category/);
  assert.match(detail, /requirement_type "Workflow"/);
});

test('every structural and value check on an export is applied', () => {
  const doc = '- Pages: 3\n\n<a id="page-1"></a>\n# T\n## Intro\n';
  const rule = { rule_id: 'BR-X-001', name: 'BR-X-001 - n', status: 'active', path: 'p',
    requirement_type: 'Business Rule', rule_category: 'Validation', description: 'd',
    source_document: 's', source_page: '1', rule_summary: 'r', risk_level: 'High' };
  const check = (entry, text = doc) => shapeProblems({ doc: 'a.md', prefix: 'BR-X', rules: [rule],
    ...entry }, 'a.md', text, RULE_SHAPE);
  const rowWith = (change) => check({ rules: [{ ...rule, ...change }] });
  assert.deepEqual(check({}), { errors: [], warnings: [] });
  // Structure stops the job.
  assert.match(check({ doc: 'b.md' }).errors.join(), /not the requested path/);
  assert.match(check({ prefix: 'X' }).errors.join(), /prefix/);
  assert.match(check({ rules: [] }).errors.join(), /empty/);
  assert.match(rowWith({ rule_id: 'BR-Y-001' }).errors.join(), /rule_id does not read/);
  assert.match(check({ rules: [rule, rule] }).errors.join(), /appears twice/);
  assert.match(rowWith({ status: 'draft' }).errors.join(), /status/);
  assert.deepEqual(shapeProblems({ exports: [] }, 'a.md', doc, RULE_SHAPE).errors,
    ['the export holds no document']);
  // Values only warn.
  for (const [change, pattern] of [[{ description: ' ' }, /description is missing or blank/],
    [{ requirement_type: 'Workflow' }, /requirement_type/], [{ rule_category: 'Data Entry' }, /rule_category/],
    [{ risk_level: 'Severe' }, /risk_level/], [{ name: 'other' }, /name does not start/],
    [{ source_page: '4' }, /outside the document's 3 pages/], [{ source_page: 'Nowhere' }, /not a heading/]]) {
    const found = rowWith(change);
    assert.deepEqual(found.errors, []);
    assert.match(found.warnings.join(), pattern);
  }
  // A page with no anchor, a range inside the count, and a heading in an anchored document pass.
  for (const page of ['2', '1-3', '1, 3', 'Intro']) assert.deepEqual(rowWith({ source_page: page }).warnings, []);
  // With no page count, any page number passes.
  assert.deepEqual(rowWith({ source_page: '40' }).warnings.length, 1);
  assert.deepEqual(check({ rules: [{ ...rule, source_page: '40' }] }, '# T\n').warnings, []);
});

test('an export older than its document is a warning, and a review day outranks created', async () => {
  const config = withExport('exports/stale.json');
  const result = await runJob(config, issueJob(['docs/OTHER/UC03-Lost-Cards.md']),
    { model: fakeModel(), echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const lines = statusLines(result.outDir);
  assert.ok(lines.some((l) => l.event === 'warn' && l.reason === 'rules-stale' && l.document === 1));
  assertContentFree(read(path.join(result.outDir, 'status.log')));
  assert.match(read(path.join(result.outDir, 'detail.log')), /is stale/);
  // No revision date, or no confirming day, gives no answer.
  const dated = '- Revised: 2026-09-01, from the file\n';
  const entry = (extra, created) => [{ ...extra, rules: [{ created }] }];
  assert.equal(rulesStale(dated, entry({}, '2026-08-01')), true);
  assert.equal(rulesStale(dated, entry({}, '2026-09-01')), false);
  assert.equal(rulesStale(dated, entry({ reviewed: '2026-09-02' }, '2026-08-01')), false);
  assert.equal(rulesStale(dated, entry({ last_reviewed: '2026-08-15' }, '2026-09-05')), true);
  assert.equal(rulesStale('- Revised: not stated\n', entry({}, '2026-08-01')), false);
  assert.equal(rulesStale(dated, entry({}, undefined)), false);
});

const STRUCK_DOC = 'docs/OTHER/UC05-Struck-Warning.md';

test('struck-through text no retired rule cites is a warning and a limitation, not a stop', async () => {
  const config = withExport('master-struck.json');
  const result = await runJob(config, issueJob([STRUCK_DOC]), { model: fakeModel(), echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const lines = statusLines(result.outDir);
  const warn = lines.filter((l) => l.event === 'warn' && l.reason === 'retired-rule-missing');
  assert.deepEqual(warn.map((l) => [l.phase, l.document]), [['phase2', 1]]);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
  assert.match(read(path.join(result.outDir, 'detail.log')), /struck-through text[^]*page 2/);
  const pack = JSON.parse(read(result.packPath));
  assert.match(pack.limitations['Job Intake'], /Struck-through text in UC05 Struck Warning has no rule citing it/);
});

test('a retired rule that cites the page of the struck-through text leaves no warning', async () => {
  const config = withExport('master-struck-retired.json');
  const result = await runJob(config, issueJob([STRUCK_DOC]), { model: fakeModel(), echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.ok(!statusLines(result.outDir).some((l) => l.reason === 'retired-rule-missing'));
  assert.ok(!JSON.parse(read(result.packPath)).limitations?.['Job Intake']);
});

const shape = (spans) => spans.map(({ page, heading }) => ({ page, heading }));

test('a struck removal is cited by a retired rule at its page, range or heading', () => {
  const paged = '<a id="page-1"></a>\n\n- ~~Old option one~~\n\n<a id="page-3"></a>\n\n- ~~Old option two~~\n';
  const rule = (extra) => ({ status: 'active', ...extra });
  assert.deepEqual(shape(struckSpans(paged)), [{ page: 1, heading: null }, { page: 3, heading: null }]);
  // An active rule on the page is not a retired one.
  assert.equal(uncitedStruck(paged, [rule({ source_page: '1' })]).length, 2);
  assert.equal(uncitedStruck(paged, [rule({ status: 'retired', source_page: '1' })]).length, 1);
  // A range or list holds the page.
  assert.equal(uncitedStruck(paged, [rule({ status: 'retired', source_page: '1, 3' })]).length, 0);
  assert.equal(uncitedStruck(paged, [rule({ status: 'retired', source_page: '2-4' })]).length, 1);
  // A rule cites the heading the span sits under.
  const flat = '# Doc\n\n## Warning\n\n- ~~Old option~~\n';
  assert.deepEqual(shape(struckSpans(flat)), [{ page: null, heading: 'warning' }]);
  assert.equal(uncitedStruck(flat, [rule({ status: 'retired', source_page: 'Warning' })]).length, 0);
  assert.equal(uncitedStruck(flat, [rule({ status: 'retired', source_page: '1' })]).length, 1);
  assert.equal(uncitedStruck('plain text', []).length, 0);
});

test('a fragment edit or a restated sentence needs no retired rule, and a removal does', () => {
  const active = [{ status: 'active', source_page: '1', rule_summary: 'The loan is saved at once.' }];
  const warns = (text) => uncitedStruck(`<a id="page-1"></a>\n\n${text}\n`, active).length;
  // The issue's own case: the live sentence says something else, so the warning was removed.
  assert.equal(warns('~~A warning appears before the loan is saved.~~ The loan is saved at once.'), 1);
  // The live sentence restates the struck one with a changed value.
  assert.equal(warns('~~A warning appears after 90 days.~~ A warning appears after 120 days.'), 0);
  // Part of a sentence: a value or a word changed.
  assert.equal(warns('The cue shows ~~90~~ 120 days'), 0);
  assert.equal(warns('The page ~~may~~ must show it.'), 0);
  assert.equal(warns('The page is ~~not~~ saved.'), 0);
  // A whole list item or table cell is a removal.
  assert.equal(warns('- ~~Print the receipt~~'), 1);
  assert.equal(warns('1. ~~Print the receipt~~'), 1);
  assert.equal(warns('| Print | ~~Receipt printed~~ | Yes |'), 1);
  // The full stop outside the tildes still ends a sentence.
  assert.equal(warns('~~A warning appears before the loan is saved~~. The loan is saved at once.'), 1);
  // "e.g." does not end the live sentence, so the restatement is read whole.
  assert.equal(warns('~~Show the cue e.g. the warning banner.~~ Show the cue e.g. the warning banner too.'), 0);
  // A sentence that starts with a number is a new sentence.
  assert.equal(warns('~~A warning appears before the loan is saved.~~ The loan is saved. 3 warning appears before loan.'), 1);
  // In a table the live sentence is in the same cell, not in the next row.
  assert.equal(warns('| ~~Print the receipt.~~ | Yes |\n| Print the receipt. | No |'), 1);
  assert.equal(warns('| ~~Print the receipt.~~ Print the receipt now. | Yes |'), 0);
  // A struck sentence followed by another struck one has no live sentence.
  assert.equal(warns('~~Print the receipt.~~ ~~Show the balance.~~'), 2);
});

test('a struck heading is still the heading its spans sit under', () => {
  const text = '## ~~Save Warning~~\n\n- ~~Old item~~\n';
  const retired = [{ status: 'retired', source_page: 'Save Warning' }];
  assert.deepEqual(struckSpans(text).map((s) => s.heading), ['save warning', 'save warning']);
  assert.equal(uncitedStruck(text, retired).length, 0);
  assert.equal(uncitedStruck(text, []).length, 2);
});

test('a span wrapped over a line break is read whole, and a lone mark pairs with nothing', () => {
  const text = '<a id="page-1"></a>\n\nThe ~~warning with Yes and\nNo buttons~~ is gone; ~~second span~~ too.\n\n'
    + 'A ~~left open\n\nblank line~~ is not a span.\n\n'
    + 'approx ~~5 units\nnext ~~real removed~~ end\n';
  assert.deepEqual(struckSpans(text).map((s) => s.text),
    ['warning with Yes and\nNo buttons', 'second span', 'real removed']);
});

test('struck text in code is not read, an unclosed fence hides nothing after it, and headings in code are not headings', () => {
  const text = '<a id="page-1"></a>\n\n## Real\n\n```\n## Fake heading\nx ~~in fence~~ y\n```\n\n'
    + 'Use `~~in code~~` here, ~~a real one~~.\n\n~~~\n~~also fenced~~\n~~~\n';
  assert.deepEqual(struckSpans(text).map(({ page, heading, text: t }) => ({ page, heading, t })),
    [{ page: 1, heading: 'real', t: 'a real one' }]);
  // A fence with no close is not a block.
  const open = '## Real\n\n```\nafter ~~kept~~ here\n';
  assert.deepEqual(struckSpans(open).map((s) => s.text), ['kept']);
});

// A retired rule the change concerns is tested by a card that verifies the behavior is gone.
const RETIRED = 'BR-LIB.UC05-003';
const struckRun = (extra = {}) => lib({
  intake: (value) => ({ ...value, documents: [STRUCK_DOC] }),
  // The inventory names the live rules only.
  phase6_scenarios: (value) => ({ ...value, scenarios: [
    { kind: 'decision', rules: ['BR-LIB.UC05-001'], population: 'p0', action: 'a0', outcome: 'o' },
    { kind: 'decision', rules: ['BR-LIB.UC05-002'], population: 'p1', action: 'a1', outcome: 'o' }] }),
  phase6_cards: titled,
  ...extra,
}, { inputs: { ...fixtureInputs(), ruleExport: exportFrom('master-struck-retired.json') } });

test('a retired Direct Change rule no scenario names gets a scenario and a card that verifies it is gone', async () => {
  const run = struckRun();
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const asked = callsNamed(run, 'phase6_cards_d1_rule');
  assert.equal(asked.length, 1);
  assert.match(asked[0].user, /check that the behavior of BR-LIB\.UC05-003 is gone/);
  assert.match(asked[0].user, /verifies the behavior is gone/);
  assert.match(callsNamed(run, 'phase6_scenarios')[0].user, /list a scenario that checks its behavior is gone/);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.testCards.some((card) => card.rules.includes(RETIRED)));
  assert.ok(!pack.coverage.some((row) => row.ruleId === RETIRED && row.status === 'Missing'));
});

test('a retired Direct Change rule a card already cites needs no further call', async () => {
  const run = struckRun({ phase6_scenarios: (value) => ({ ...value, scenarios: [
    { kind: 'decision', rules: ['BR-LIB.UC05-001', 'BR-LIB.UC05-002', RETIRED], population: 'p0',
      action: 'a0', outcome: 'o' }] }) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(callsNamed(run, 'phase6_cards_d1_rule').length, 0);
});

test('a scenario the inventory made for a retired rule, however it settled, adds no further scenario', async () => {
  const run = struckRun({
    phase6_scenarios: (value) => ({ ...value, scenarios: [
      { kind: 'decision', rules: ['BR-LIB.UC05-001', 'BR-LIB.UC05-002'], population: 'p0', action: 'a0',
        outcome: 'o' },
      { kind: 'decision', rules: [RETIRED], population: 'p1', action: 'a1', outcome: 'o' }] }),
    phase6_cards: (value) => titled({ ...value, cards: value.cards.filter((c) => c.scenario === 'S1'),
      skipped: [{ scenario: 'S2', how: 'reused', reason: 'An existing test covers it.' }] }),
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(callsNamed(run, 'phase6_cards_d1_rule').length, 0);
  assert.equal(phase6Pass(result.outDir).unsettled, 0);
});

test('a scenario for a retired rule that a card settled without citing it still owes a removed scenario', async () => {
  const run = struckRun({
    phase6_scenarios: (value) => ({ ...value, scenarios: [
      { kind: 'decision', rules: ['BR-LIB.UC05-001', RETIRED], population: 'p0', action: 'a0', outcome: 'o' }] }),
    // The card keeps only the live rule.
    phase6_cards: (value) => titled({ ...value, cards: value.cards.map((c) => (c.scenario !== 'S1' ? c : { ...c,
      rules: ['BR-LIB.UC05-001'], steps: c.steps.map((st) => ({ ...st, rules: ['BR-LIB.UC05-001'] })) })) }),
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(callsNamed(run, 'phase6_cards_d1_rule').length, 1);
});

/**
 * Two removal checks that press Save, which merge into S1, then S3 for the
 * live rules `live` names. The break pass, whose name extends the inventory's,
 * lists one break scenario.
 */
const mergedRun = (live) => struckRun({ phase6_scenarios: (value, calls) => ({ ...value,
  scenarios: calls.at(-1).schemaName === 'phase6_scenarios_d1_break'
    ? [{ kind: 'break', rules: ['BR-LIB.UC05-001'], population: 'junk', action: 'enter junk', outcome: 'o' }]
    : [{ kind: 'decision', rules: [RETIRED], population: 'a loan', action: 'press Save', outcome: 'o' },
      { kind: 'decision', rules: [RETIRED], population: 'another loan', action: 'press Save again', outcome: 'o' },
      { kind: 'decision', rules: live, population: 'p', action: 'a', outcome: 'o' }] }) });
const offered = (run, prefix) => scenarioEnum(callsNamed(run, prefix)[0].schema);
const scenarioIds = (outDir) => Object.values(JSON.parse(read(path.join(outDir, 'work', 'checkpoints',
  'phase6.json'))).state.designed).flatMap((d) => d.scenarios.map((s) => s.id));

test('after a merge, a scenario made for a rule no scenario names gets an ID no scenario holds', async () => {
  const run = mergedRun(['BR-LIB.UC05-001']);
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.deepEqual(offered(run, 'phase6_cards_d1_rule'), ['S4']);
  const ids = scenarioIds(result.outDir);
  assert.deepEqual(ids, [...new Set(ids)]);
});

test('after a merge, a scenario the break pass lists gets an ID no scenario holds', async () => {
  const run = mergedRun(['BR-LIB.UC05-001', 'BR-LIB.UC05-002']);
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(callsNamed(run, 'phase6_cards_d1_rule').length, 0);
  assert.deepEqual(offered(run, 'phase6_cards_d1_break'), ['S4']);
  const ids = scenarioIds(result.outDir);
  assert.deepEqual(ids, [...new Set(ids)]);
});

test('verification reads a retired rule as removed, so a card stating the behavior is absent survives', async () => {
  // A verifier that rejects a card citing the retired rule unless its Expected Result says it is gone.
  const judgeRemoved = (value, calls) => {
    const user = calls.at(-1).user;
    const cards = {};
    for (const [, label, body] of user.matchAll(/### (C\d+)\n([\s\S]*?)(?=\n\n### C|\n## |$)/g)) {
      const bad = /BR-LIB\.UC05-003/.test(body) && !/Expected Result: [^\n]*(absent|gone)/.test(body);
      cards[label] = bad ? { why: 'The rule says it happens.', verdict: 'does not follow' }
        : { why: 'It follows.', verdict: 'follows' };
    }
    return { ...value, cards };
  };
  const run = struckRun({
    phase6_cards: (value) => titled({ ...value, cards: value.cards.map((card) => (card.rules.includes(RETIRED)
      ? { ...card, expected: 'The warning is absent',
        steps: card.steps.map((step, i, all) => (i === all.length - 1
          ? { ...step, expected: 'The warning is absent' } : step)) } : card)) }),
    phase6_verify: judgeRemoved,
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const verify = callsNamed(run, 'phase6_verify');
  assert.ok(verify.length > 0);
  assert.ok(verify.some((call) => /removed: the card must show this no longer happens/.test(call.user)));
  assert.match(verify[0].user, /A rule marked removed was taken out/);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.testCards.some((card) => card.rules.includes(RETIRED) && /absent/.test(card.expected)));
});

test('a retired rule no card can cover is asked for twice, then recorded as a gap and a limitation', async () => {
  const run = struckRun({ phase6_cards: (value) => titled({ ...value,
    cards: value.cards.filter((card) => card.scenario !== 'S3') }) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(callsNamed(run, 'phase6_cards_d1_rule').length, 2);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.coverage.some((row) => row.ruleId === RETIRED && row.status === 'Missing'));
  assert.match(pack.limitations['Coverage Matrix'], /BR-LIB\.UC05-003/);
  assert.ok(pack.assumptions.some((a) => a.assumption.startsWith('No test card covers scenario S3:')));
});

// An active impacted rule the inventory leaves out is owed a card as much as a retired one.
const LIVE = 'BR-LIB.UC01-005';
const leaveOut = (extra = {}, overrides = {}) => lib({
  phase6_scenarios: (value) => ({ ...value, scenarios: [{ kind: 'decision', population: 'p0', action: 'a0',
    outcome: 'o', rules: ['BR-LIB.UC01-001', 'BR-LIB.UC01-002', 'BR-LIB.UC01-003', 'BR-LIB.UC01-004'] }] }),
  phase6_cards: titled,
  ...extra,
}, overrides);

test('an active impacted rule no scenario names gets a scenario and a card', async () => {
  const run = leaveOut();
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const asked = callsNamed(run, 'phase6_cards_d1_rule');
  assert.equal(asked.length, 1);
  assert.match(asked[0].user, new RegExp(`check that ${LIVE.replace('.', '\\.')} holds`));
  assert.doesNotMatch(asked[0].user, /verifies the behavior is gone/);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.testCards.some((card) => card.rules.includes(LIVE)));
  assert.ok(!pack.coverage.some((row) => row.ruleId === LIVE && row.status === 'Missing'));
});

test('an active rule no card can cover is asked for twice, then recorded as a gap and a limitation', async () => {
  const run = leaveOut({ phase6_cards: (value) => titled({ ...value,
    cards: value.cards.filter((card) => !card.rules.includes(LIVE)) }) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(callsNamed(run, 'phase6_cards_d1_rule').length, 2);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.coverage.some((row) => row.ruleId === LIVE && row.status === 'Missing'));
  assert.match(pack.limitations['Coverage Matrix'], /BR-LIB\.UC01-005/);
  assert.ok(pack.assumptions.some((a) => a.assumption.startsWith('No test card covers scenario')));
});

test('an active rule whose own scenario was skipped as a gap is not asked about again', async () => {
  const run = leaveOut({
    phase6_scenarios: (value) => ({ ...value, scenarios: [
      { kind: 'decision', population: 'p0', action: 'a0', outcome: 'o',
        rules: ['BR-LIB.UC01-001', 'BR-LIB.UC01-002', 'BR-LIB.UC01-003', 'BR-LIB.UC01-004'] },
      { kind: 'decision', population: 'p1', action: 'a1', outcome: 'o', rules: [LIVE] }] }),
    phase6_cards: (value) => titled({ ...value, cards: value.cards.filter((c) => c.scenario === 'S1'),
      skipped: [{ scenario: 'S2', how: 'gap', reason: 'The document does not say.' }] }),
  });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(callsNamed(run, 'phase6_cards_d1_rule').length, 0);
});

test('the rules owed a scenario go to the card call in batches of cardScenariosPerCall', async () => {
  const run = leaveOut({
    phase6_scenarios: (value) => ({ ...value, scenarios: [{ kind: 'decision', population: 'p0', action: 'a0',
      outcome: 'o', rules: ['BR-LIB.UC01-001', 'BR-LIB.UC01-002', 'BR-LIB.UC01-003'] }] }),
    // Each reply writes the card for the first scenario listed in the call only.
    phase6_cards: (value, calls) => {
      const first = calls.at(-1).user.match(/- (S\d+) \|/)?.[1];
      return titled({ ...value, cards: value.cards.filter((card) => card.scenario === first) });
    } },
  { cardScenariosPerCall: 1 });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const names = callsNamed(run, 'phase6_cards_d1_rule').map((c) => c.schemaName);
  assert.deepEqual(names, ['phase6_cards_d1_rule_1', 'phase6_cards_d1_rule_2']);
});

test('check reports each input by code without a model call, and fails on a missing one', () => {
  const run = (args) => spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'check',
    '--config', path.join(FIXTURES, 'pipeline.json'), ...args], { encoding: 'utf8' });
  const good = run(['--issue', '501', '--change', '7001', '--doc', 'docs/LIB/UC01-Card-Renewal.md']);
  assert.equal(good.status, 0, good.stderr);
  assert.deepEqual(good.stdout.trim().split('\n'), [
    'issue-number  present  issue', 'description  present  found',
    'document-1  present  rules-ok']);

  const bad = run(['--issue', '999', '--doc', 'docs/OTHER/UC09-Unmapped.md',
    '--doc', 'docs/OTHER/UC03-Lost-Cards.md', '--doc', 'docs/none.md']);
  assert.equal(bad.status, 1);
  assert.deepEqual(bad.stdout.trim().split('\n'), [
    'issue-number  present  issue', 'description  missing  no-description',
    'document-1  missing  rules-not-extracted', 'document-2  missing  rules-not-extracted',
    'document-3  missing  document-file']);
  assertContentFree(bad.stdout);

  // The job's own opt-in makes a document with no rules usable.
  const derived = run(['--issue', '501', '--doc', 'docs/OTHER/UC09-Unmapped.md', '--allow-derived-rules']);
  assert.equal(derived.status, 0);
  assert.match(derived.stdout, /document-1  present  rules-derived/);

  // Without --doc the model picks the documents, so their rules are unchecked: exit 3.
  const open = run(['--issue', '501']);
  assert.match(open.stdout, /documents  present  candidates=2/);
  assert.match(open.stdout, /rules  unchecked  name-documents-with-doc/);
  assert.equal(open.status, 3);
  // A missing input outranks an unchecked one.
  assert.equal(run(['--issue', '999']).status, 1);
});

test('the check detail log is kept apart from the job folder a run clears', async () => {
  const config = withExport('exports/legacy.json');
  const job = issueJob(['docs/LIB/UC01-Card-Renewal.md']);
  const { checkJob } = await import('./build-pack.mjs');
  checkJob(config, job);
  const kept = path.join(config.output, 'issue-501-change-7001.check', 'detail.log');
  assert.match(read(kept), /warnings/);
  await runJob(config, job, { model: fakeModel(), echo: false });
  assert.ok(fs.existsSync(kept));
});

test('a resumed job starts at the phase that stopped it and keeps what passed', async (t) => {
  for (const job of [{ issue: '501', change: '7001' }, { suite: 'LIB' }]) {
    await t.test(job.suite ? 'suite' : 'issue', async () => {
      const config = fixtureConfig();
      const pick = { intake: (value) => ({ ...value, documents: ['docs/LIB/UC01-Card-Renewal.md'] }) };
      const failing = fakeModel({ ...pick, phase9_senior_review: () => {
        throw new ModelError('no-reply', 'model endpoint ended the reply early');
      } });
      const first = await runJob(config, job, { model: failing, echo: false });
      assert.equal(first.ok, false);
      assert.equal(first.phase, 'phase9-senior');
      assert.equal(first.reason, 'model:no-reply');

      const model = fakeModel(pick);
      const result = await runJob(config, { ...job, resume: true }, { model, echo: false });
      assert.equal(result.ok, true, JSON.stringify(result));
      // Only the checklist passed before the failure, so only the calls after them run again.
      const stepNames = [...new Set(model.calls.map((c) => c.schemaName))];
      assert.equal(stepNames[0], 'phase9_senior_review');
      assert.deepEqual(stepNames.slice(-2), ['phase9_revalidation_readiness', 'phase10_notes']);
      assert.ok(stepNames.includes('phase9_confidence_overall'));
      const lines = statusLines(result.outDir);
      assert.ok(lines.some((l) => l.event === 'resume' && l.phase === 'phase9-senior'
        && l.after === 'phase9-checklist'));
      assert.deepEqual(lines.filter((l) => l.event === 'pass').map((l) => l.phase).slice(-4),
        ['phase9-confidence', 'phase9-revalidate', 'phase10', 'done']);
      // The pack carries what the first run's phases built.
      const pack = JSON.parse(read(result.packPath));
      assert.ok(pack.testCards.length > 0);
      assert.ok(pack.seniorReview);
      assert.ok(pack.reviewCoverage, 'the checklist\'s coverage rows survive the resume');
      assertContentFree(read(path.join(result.outDir, 'status.log')));
    });
  }
});

test('a job run again without resume starts over from intake', async () => {
  const config = fixtureConfig();
  const pick = { intake: (value) => ({ ...value, documents: ['docs/LIB/UC01-Card-Renewal.md'] }) };
  await runJob(config, { issue: '501' }, { model: fakeModel({ ...pick, phase9_checklist: () => {
    throw new ModelError('no-reply', 'x');
  } }), echo: false });
  const model = fakeModel(pick);
  const result = await runJob(config, { issue: '501' }, { model, echo: false });
  assert.equal(result.ok, true);
  assert.equal(model.calls[0].schemaName.split('_')[0], 'intake');
  assert.ok(!statusLines(result.outDir).some((l) => l.event === 'resume'));
});

test('a reasoning call that fails for any reason is retried once with thinking off', async () => {
  const thinking = [];
  const fetchImpl = async (url, options) => {
    const body = JSON.parse(options.body);
    thinking.push(body.chat_template_kwargs.enable_thinking);
    // A server that gives up at its own time-out ends the reply early.
    if (body.chat_template_kwargs.enable_thinking) {
      return { ok: true, text: async () => '' };
    }
    return streamed({ content: '{"ok":true}' });
  };
  const config = fixtureConfig();
  const { ask } = await import('./phases.mjs');
  const ctx = { config, calls: 0, tokens: { prompt: 0, output: 0 }, logs: { status() {}, detail() {}, call() {} },
    job: { id: 'j' }, model: { ...modelClient({ endpoint: 'http://localhost:1/v1', name: 'm', fetchImpl }),
      countTokens: async () => 10 } };
  const value = await ask(ctx, { phase: 'phase9', step: 's', reasoning: true, inputs: [],
    schema: { type: 'object' }, task: 't' });
  assert.deepEqual(value, { ok: true });
  assert.deepEqual(thinking, [true, false]);
});

test('--resume takes no value and rides on the job', () => {
  assert.deepEqual(jobFrom(parseArgs(['--issue', '501', '--resume', '--change', '7001'])),
    { issue: '501', change: '7001', resume: true });
  assert.deepEqual(jobFrom(parseArgs(['--suite', 'LIB', '--resume'])), { suite: 'LIB', resume: true });
});

/** An exec stub: `active` units answer list-units, every call is recorded, `failing` stops fail. */
function fakeSystemctl(active, failing = []) {
  const calls = [];
  const exec = (command, args) => {
    calls.push([command, ...args]);
    if (args.includes('list-units')) {
      return { status: 0, stdout: active.map((unit) => `${unit} loaded active running Test\n`).join('') };
    }
    const unit = args.at(-1);
    return { status: failing.includes(`${args.at(-2)} ${unit}`) ? 1 : 0, stdout: '' };
  };
  return { calls, exec, verbs: () => calls.filter((c) => !c.includes('list-units')) };
}

/** A fake /proc with one process per [pid, comm, cgroup] row. */
function fakeProc(rows) {
  const root = scratch('build-pack-proc-');
  for (const [pid, comm, cgroup] of rows) {
    fs.mkdirSync(path.join(root, String(pid)));
    fs.writeFileSync(path.join(root, String(pid), 'comm'), `${comm}\n`);
    fs.writeFileSync(path.join(root, String(pid), 'cgroup'), `0::${cgroup}\n`);
  }
  return root;
}

const pauseConfig = (pause = {}) => fixtureConfig({ pause: { units: ['gpu-*.service'], ...pause } });
const okRun = async () => ({ ok: true, ms: 1 });
const quiet = (sys, deps = {}) => (cfg) => createPauser(cfg, { exec: sys.exec, log: () => {}, ...deps });

test('idle units are stopped before the job and started after it', async () => {
  const config = pauseConfig();
  addJob(config, { issue: '1' });
  const sys = fakeSystemctl(['gpu-a.service', 'gpu-b.service']);
  const seen = [];
  const run = async () => { seen.push(sys.verbs().length); return { ok: true, ms: 1 }; };
  await drainQueue(config, { run, pause: quiet(sys) });
  assert.deepEqual(seen, [2]);
  assert.deepEqual(sys.verbs().map((c) => c.slice(-2).join(' ')),
    ['stop gpu-a.service', 'stop gpu-b.service', 'start gpu-a.service', 'start gpu-b.service']);
  // The system scope stops through sudo with the full path and never asks for a password.
  assert.deepEqual(sys.verbs()[0], ['sudo', '-n', '/usr/bin/systemctl', 'stop', 'gpu-a.service']);
  assert.ok(!fs.existsSync(pausedPath(config)));
});

test('the user scope stops and starts through systemctl --user', async () => {
  const config = pauseConfig({ scope: 'user' });
  const sys = fakeSystemctl(['gpu-a.service']);
  const pauser = createPauser(config, { exec: sys.exec, log: () => {} });
  await pauser.pause();
  await pauser.resume();
  assert.deepEqual(sys.calls.map((c) => c.join(' ')), [
    'systemctl --user list-units --plain --no-legend --state=active gpu-*.service',
    'systemctl --user stop gpu-a.service', 'systemctl --user start gpu-a.service']);
});

test('a busy unit is stopped only after its worker exits', async () => {
  const config = pauseConfig({ busyProcess: 'worker', pollSeconds: 5 });
  const proc = fakeProc([[100, 'worker', '/system.slice/gpu-a.service'],
    [101, 'worker', '/system.slice/other-gpu-a.service']]);
  const sys = fakeSystemctl(['gpu-a.service', 'gpu-b.service']);
  const sleeps = [];
  const sleep = async (ms) => {
    sleeps.push(ms);
    // gpu-b was idle and is already stopped; gpu-a's worker now finishes.
    assert.deepEqual(sys.verbs().map((c) => c.at(-1)), ['gpu-b.service']);
    fs.rmSync(path.join(proc, '100'), { recursive: true });
  };
  const pauser = createPauser(config, { exec: sys.exec, log: () => {}, procRoot: proc, sleep });
  await pauser.pause();
  assert.deepEqual(sleeps, [5000]);
  assert.deepEqual(sys.verbs().map((c) => c.slice(-2).join(' ')),
    ['stop gpu-b.service', 'stop gpu-a.service']);
  await pauser.resume();
  assert.equal(sys.verbs().filter((c) => c.includes('start')).length, 2);
});

test('a busy unit is left running once maxWaitMinutes passes', async () => {
  const config = pauseConfig({ busyProcess: 'worker', pollSeconds: 5, maxWaitMinutes: 0.25 });
  const proc = fakeProc([[100, 'worker', '/system.slice/gpu-a.service']]);
  const sys = fakeSystemctl(['gpu-a.service', 'gpu-b.service']);
  let t = new Date('2026-10-27T22:00:00').getTime();
  const sleeps = [];
  const sleep = async (ms) => { sleeps.push(ms); t += ms; };
  const lines = [];
  const pauser = createPauser(config, { exec: sys.exec, log: (l) => lines.push(l), procRoot: proc, sleep,
    clock: () => new Date(t) });
  await pauser.pause();
  assert.deepEqual(sleeps, [5000, 5000, 5000]);
  assert.ok(lines.includes('pause: left running gpu-a.service'));
  assert.deepEqual(sys.verbs().map((c) => c.slice(-2).join(' ')), ['stop gpu-b.service']);
  await pauser.resume();
  assert.deepEqual(sys.verbs().filter((c) => c.includes('start')).map((c) => c.at(-1)), ['gpu-b.service']);
});

test('maxWaitMinutes 0 stops the idle units and never sleeps', async () => {
  const config = pauseConfig({ busyProcess: 'worker', maxWaitMinutes: 0 });
  const proc = fakeProc([[100, 'worker', '/system.slice/gpu-a.service']]);
  const sys = fakeSystemctl(['gpu-a.service', 'gpu-b.service']);
  const lines = [];
  const sleep = async () => assert.fail('slept');
  const pauser = createPauser(config, { exec: sys.exec, log: (l) => lines.push(l), procRoot: proc, sleep });
  await pauser.pause();
  assert.deepEqual(sys.verbs().map((c) => c.at(-1)), ['gpu-b.service']);
  assert.ok(lines.includes('pause: left running gpu-a.service'));
});

test('a wait that runs into the cutoff starts no job and starts the units again', async () => {
  const config = pauseConfig({ busyProcess: 'worker', pollSeconds: 5 });
  addJob(config, { issue: '1' });
  const proc = fakeProc([[100, 'worker', '/system.slice/gpu-a.service']]);
  const sys = fakeSystemctl(['gpu-a.service', 'gpu-b.service']);
  let t = new Date('2026-10-28T06:59:50').getTime();
  const clock = () => new Date(t);
  const sleep = async (ms) => { t += ms; };
  let ran = 0;
  const done = await drainQueue(config, { cutoff: '07:00', clock, run: async () => { ran += 1; return { ok: true, ms: 1 }; },
    pause: quiet(sys, { procRoot: proc, sleep, clock }) });
  assert.equal(ran, 0);
  assert.deepEqual(done, []);
  assert.equal(readQueue(config).jobs[0].status, 'queued');
  assert.deepEqual(sys.verbs().map((c) => c.slice(-2).join(' ')), ['stop gpu-b.service', 'start gpu-b.service']);
});

test('a unit left busy is stopped before a later job once its worker has finished', async () => {
  const config = pauseConfig({ busyProcess: 'worker', maxWaitMinutes: 0 });
  addJob(config, { issue: '1' });
  addJob(config, { issue: '2' });
  const proc = fakeProc([[100, 'worker', '/system.slice/gpu-a.service']]);
  const active = ['gpu-a.service', 'gpu-b.service'];
  const sys = fakeSystemctl(active);
  // A stopped unit drops out of the active list, as it does under systemd.
  const exec = (command, args) => {
    if (args.includes('stop')) active.splice(active.indexOf(args.at(-1)), 1);
    return sys.exec(command, args);
  };
  const clock = () => new Date('2026-10-27T22:00:00');
  const seen = [];
  const run = async () => {
    seen.push(sys.verbs().map((c) => c.slice(-2).join(' ')));
    fs.rmSync(path.join(proc, '100'), { recursive: true, force: true });
    return { ok: true, ms: 1 };
  };
  await drainQueue(config, { cutoff: '07:00', clock, run,
    pause: (cfg) => createPauser(cfg, { exec, log: () => {}, procRoot: proc, clock }) });
  assert.deepEqual(seen, [['stop gpu-b.service'], ['stop gpu-b.service', 'stop gpu-a.service']]);
  assert.deepEqual(sys.verbs().filter((c) => c.includes('start')).map((c) => c.at(-1)),
    ['gpu-b.service', 'gpu-a.service']);
});

test('a unit that would not stop is tried once, and a unit left busy is reported once', async () => {
  const config = pauseConfig({ busyProcess: 'worker', maxWaitMinutes: 0 });
  const proc = fakeProc([[100, 'worker', '/system.slice/gpu-a.service']]);
  const sys = fakeSystemctl(['gpu-a.service', 'gpu-b.service'], ['stop gpu-b.service']);
  const lines = [];
  const pauser = createPauser(config, { exec: sys.exec, log: (l) => lines.push(l), procRoot: proc });
  await pauser.pause();
  await pauser.pause();
  assert.equal(lines.filter((l) => l === 'pause: stop failed gpu-b.service').length, 1);
  assert.equal(lines.filter((l) => l === 'pause: left running gpu-a.service').length, 1);
  assert.equal(sys.verbs().filter((c) => c.includes('stop')).length, 1);
});

test('with no pause config nothing is run', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '1' });
  const sys = fakeSystemctl(['gpu-a.service']);
  await drainQueue(config, { run: okRun, pause: quiet(sys) });
  assert.deepEqual(sys.calls, []);
});

test('a failed stop is logged, the job still runs, and that unit is never started', async () => {
  const config = pauseConfig();
  addJob(config, { issue: '1' });
  const sys = fakeSystemctl(['gpu-a.service', 'gpu-b.service'], ['stop gpu-a.service']);
  const lines = [];
  let ran = 0;
  const done = await drainQueue(config, { run: async () => { ran += 1; return { ok: true, ms: 1 }; },
    pause: quiet(sys, { log: (l) => lines.push(l) }) });
  assert.equal(ran, 1);
  assert.equal(done[0].status, 'passed');
  assert.ok(lines.includes('pause: stop failed gpu-a.service'));
  assert.deepEqual(sys.verbs().filter((c) => c.includes('start')).map((c) => c.at(-1)), ['gpu-b.service']);
});

test('units that were not active are never started', async () => {
  const config = pauseConfig();
  addJob(config, { issue: '1' });
  const sys = fakeSystemctl([]);
  await drainQueue(config, { run: okRun, pause: quiet(sys) });
  assert.deepEqual(sys.verbs(), []);
});

test('an empty queue stops nothing', async () => {
  const config = pauseConfig();
  const sys = fakeSystemctl(['gpu-a.service']);
  await drainQueue(config, { run: okRun, pause: quiet(sys) });
  assert.deepEqual(sys.calls, []);
});

test('units a dead run left stopped are started by the next run, even with no job', async () => {
  const config = pauseConfig();
  fs.writeFileSync(pausedPath(config), JSON.stringify(['gpu-a.service']));
  const sys = fakeSystemctl(['gpu-b.service']);
  await drainQueue(config, { run: okRun, pause: quiet(sys) });
  assert.deepEqual(sys.calls.map((c) => c.slice(-2).join(' ')), ['start gpu-a.service']);
  assert.ok(!fs.existsSync(pausedPath(config)));
});

test('a second resume does nothing, and each stop is recorded as it happens', async () => {
  const config = pauseConfig();
  const sys = fakeSystemctl(['gpu-a.service']);
  const pauser = createPauser(config, { exec: sys.exec, log: () => {} });
  await pauser.pause();
  assert.deepEqual(JSON.parse(fs.readFileSync(pausedPath(config), 'utf8')), { stopped: ['gpu-a.service'], restore: [] });
  await pauser.resume();
  const calls = sys.calls.length;
  await pauser.resume();
  assert.equal(sys.calls.length, calls);
});

test('a unit marked to restore is started when the run ends, though it was down at the start', async () => {
  const config = pauseConfig();
  addJob(config, { issue: '1' });
  assert.ok(markRestore(config, 'issue-1', ['gpu-c.service']));
  const sys = fakeSystemctl(['gpu-a.service']);
  await drainQueue(config, { run: okRun, pause: quiet(sys) });
  assert.deepEqual(sys.verbs().map((c) => c.slice(-2).join(' ')),
    ['stop gpu-a.service', 'start gpu-a.service', 'start gpu-c.service']);
  assert.ok(!fs.existsSync(pausedPath(config)));
  assert.equal(readQueue(config).jobs[0].restore, undefined);
});

test('a marked unit is started after a failed job too', async () => {
  const config = pauseConfig();
  addJob(config, { issue: '1' });
  markRestore(config, 'issue-1', ['gpu-c.service']);
  const sys = fakeSystemctl([]);
  await drainQueue(config, { run: async () => ({ ok: false, phase: 'intake', ms: 1 }), pause: quiet(sys) });
  assert.deepEqual(sys.verbs().map((c) => c.slice(-2).join(' ')), ['start gpu-c.service']);
  assert.equal(readQueue(config).jobs[0].restore, undefined);
});

test('cancel starts a unit marked on the running job', async () => {
  const config = pauseConfig();
  addJob(config, { issue: '501' });
  const queue = readQueue(config);
  Object.assign(queue.jobs[0], { status: 'running', started: '2026-10-28T10:00:00.000Z' });
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  assert.ok(markRestore(config, 'issue-501', ['gpu-c.service']));
  assert.deepEqual(JSON.parse(fs.readFileSync(pausedPath(config), 'utf8')), { stopped: [], restore: ['gpu-c.service'] });
  const sys = fakeSystemctl([]);
  const hooks = { ...countingHooks(), pause: quiet(sys) };
  const result = await cancelJob(config, 'issue-501', hooks);
  assert.equal(result.cancelled, true);
  assert.deepEqual(sys.verbs().map((c) => c.slice(-2).join(' ')), ['start gpu-c.service']);
  assert.ok(!fs.existsSync(pausedPath(config)));
});

test('a mark written while a pauser runs survives, and resume clears only what it started', async () => {
  const config = pauseConfig();
  const sys = fakeSystemctl(['gpu-a.service']);
  const pauser = createPauser(config, { exec: sys.exec, log: () => {} });
  await pauser.pause();
  markRestoreFile(config, ['gpu-c.service']);
  assert.deepEqual(readPaused(pausedPath(config)),
    { stopped: ['gpu-a.service'], restore: ['gpu-c.service'], failedStart: [] });
  assert.deepEqual(await pauser.resume(), []);
  assert.deepEqual(sys.verbs().map((c) => c.slice(-2).join(' ')),
    ['stop gpu-a.service', 'start gpu-a.service', 'start gpu-c.service']);
  assert.ok(!fs.existsSync(pausedPath(config)));
});

test('a run without the queue leaves another run\'s marks alone', async () => {
  const config = pauseConfig();
  markRestoreFile(config, ['gpu-c.service']);
  const sys = fakeSystemctl(['gpu-a.service']);
  const pauser = createPauser(config, { exec: sys.exec, log: () => {}, leftover: false });
  await pauser.pause();
  await pauser.resume();
  assert.deepEqual(sys.verbs().map((c) => c.slice(-2).join(' ')), ['stop gpu-a.service', 'start gpu-a.service']);
  assert.deepEqual(readPaused(pausedPath(config)), { stopped: [], restore: ['gpu-c.service'], failedStart: [] });
});

test('the state file of an earlier version, a bare list, still counts as stopped units', () => {
  const config = pauseConfig();
  fs.writeFileSync(pausedPath(config), JSON.stringify(['gpu-a.service', 'bad name']));
  assert.deepEqual(readPaused(pausedPath(config)), { stopped: ['gpu-a.service'], restore: [], failedStart: [] });
});

test('only a unit on the pause list can be marked', () => {
  const config = pauseConfig({ units: ['gpu-*.service', 'runner?.service', 'tab-[1-4].service', 'x-[!a].service', 'bad['] });
  const units = restoreUnits(config, parseArgs(['--restore', 'gpu-a.service', '--restore', 'runner1.service',
    '--restore', 'tab-3.service', '--restore', 'x-b.service']));
  assert.deepEqual(units, ['gpu-a.service', 'runner1.service', 'tab-3.service', 'x-b.service']);
  assert.throws(() => restoreUnits(config, parseArgs(['--restore', 'tab-5.service'])), /not on pause.units/);
  assert.throws(() => restoreUnits(config, parseArgs(['--restore', 'x-a.service'])), /not on pause.units/);
  // A bracket that opens no class is literal, and `[!]` is not a class that matches anything.
  assert.equal(onPauseList(['a[!].service'], 'ax.service'), false);
  assert.equal(onPauseList(['b[x.service'], 'bx.service'), false);
  assert.equal(onPauseList(['[^a].service'], 'a.service'), false);
  assert.equal(onPauseList(['[^a].service'], 'b.service'), true);
  assert.throws(() => restoreUnits(config, parseArgs(['--restore', 'sshd.service'])),
    /--restore sshd.service is not on pause.units/);
  assert.throws(() => restoreUnits(config, parseArgs(['--restore', 'gpu-a.service; reboot'])), /not on pause.units/);
  assert.ok(onPauseList(['gpu-*'], 'gpu-a.service'));
  assert.ok(!onPauseList(['gpu-*.service'], 'gpu-a.timer'));
});

test('--restore repeats and --restore-paused takes no value', () => {
  const args = parseArgs(['--issue', '5', '--restore', 'a.service', '--restore', 'b.service', '--restore-paused']);
  assert.deepEqual(args.restore, ['a.service', 'b.service']);
  assert.equal(args.restorePaused, true);
  assert.deepEqual(jobFrom(args), { issue: '5' });
});

test('--restore-paused marks the pause-list units that are down', () => {
  const config = pauseConfig({ scope: 'user' });
  const calls = [];
  const exec = (command, args) => {
    calls.push([command, ...args]);
    return { status: 0, stdout: 'gpu-b.service loaded inactive dead Test\ngpu-c.service loaded failed failed Test\n' };
  };
  assert.deepEqual(restoreUnits(config, { restorePaused: true, restore: ['gpu-b.service'] }, { exec }),
    ['gpu-b.service', 'gpu-c.service']);
  assert.deepEqual(calls[0], ['systemctl', '--user', 'list-units', '--plain', '--no-legend', '--all',
    '--state=inactive,failed', 'gpu-*.service']);
});

test('markRestore refuses a job that is not waiting or running', () => {
  const config = pauseConfig();
  assert.equal(markRestore(config, 'issue-9', ['gpu-c.service']), false);
  addJob(config, { issue: '1' });
  markRestore(config, 'issue-1', ['gpu-c.service']);
  markRestore(config, 'issue-1', ['gpu-c.service', 'gpu-d.service']);
  assert.deepEqual(readQueue(config).jobs[0].restore, ['gpu-c.service', 'gpu-d.service']);
});

test('queue status lists the units waiting to be restored, and queue restore starts them', async () => {
  const config = pauseConfig();
  addJob(config, { issue: '1' });
  markRestore(config, 'issue-1', ['gpu-c.service']);
  markRestoreFile(config, ['gpu-d.service']);
  assert.deepEqual(restoreLines(config), ['restore pending gpu-d.service gpu-c.service']);
  const sys = fakeSystemctl([], ['start gpu-d.service']);
  const failedStart = await restorePaused(config, { pause: quiet(sys) });
  assert.deepEqual(failedStart, ['gpu-d.service']);
  assert.deepEqual(sys.verbs().map((c) => c.slice(-2).join(' ')), ['start gpu-d.service', 'start gpu-c.service']);
  // A unit that did not start stays recorded for the next try.
  assert.deepEqual(readPaused(pausedPath(config)),
    { stopped: [], restore: ['gpu-d.service'], failedStart: ['gpu-d.service'] });
  assert.equal(readQueue(config).jobs[0].restore, undefined);
});

test('queue status says a start failed and what to do next, not just that a restore is pending', async () => {
  const config = pauseConfig();
  markRestoreFile(config, ['gpu-d.service']);
  const sys = fakeSystemctl([], ['start gpu-d.service']);
  await restorePaused(config, { pause: quiet(sys) });
  // A later mark and a later stop keep the failure on record.
  markRestoreFile(config, ['gpu-c.service']);
  const lines = restoreLines(config);
  assert.equal(lines[0], 'restore pending gpu-c.service');
  assert.match(lines[1], /^restore start-failed gpu-d\.service; start each by hand/);
  assert.match(lines[1], /remove its name from the \.paused file beside the queue file/);
  assert.match(lines[1], /start each by hand with sudo systemctl start/);
  assert.match(lines[1], /once the cause is fixed, such as a missing sudoers rule$/);
  assert.equal(lines.length, 2);
  // The unit starts the next time, and the record goes with it.
  assert.deepEqual(await restorePaused(config, { pause: quiet(fakeSystemctl([])) }), []);
  assert.deepEqual(restoreLines(config), []);
  assert.ok(!fs.existsSync(pausedPath(config)));
});

test('the next step for a failed start in the user scope names systemctl --user and no sudoers', async () => {
  const config = pauseConfig({ scope: 'user' });
  markRestoreFile(config, ['gpu-d.service']);
  await restorePaused(config, { pause: quiet(fakeSystemctl([], ['start gpu-d.service'])) });
  const [line] = restoreLines(config);
  assert.match(line, /^restore start-failed gpu-d\.service; start each by hand with systemctl --user start, /);
  assert.ok(!line.includes('sudo'));
});

test('a failed start of a unit the run stopped is recorded, and dropping its name from the file drops the record', async () => {
  const config = pauseConfig();
  const sys = fakeSystemctl(['gpu-a.service'], ['start gpu-a.service']);
  const pauser = createPauser(config, { exec: sys.exec, log: () => {} });
  await pauser.pause();
  assert.deepEqual(await pauser.resume(), ['gpu-a.service']);
  assert.deepEqual(JSON.parse(fs.readFileSync(pausedPath(config), 'utf8')),
    { stopped: ['gpu-a.service'], restore: [], failedStart: ['gpu-a.service'] });
  // A name hand-edited out of the lists is not reported as failed.
  fs.writeFileSync(pausedPath(config), JSON.stringify({ stopped: [], restore: ['gpu-b.service'],
    failedStart: ['gpu-a.service', 'gpu-b.service', 'bad name', 7] }));
  assert.deepEqual(readPaused(pausedPath(config)),
    { stopped: [], restore: ['gpu-b.service'], failedStart: ['gpu-b.service'] });
});

test('a run without the queue keeps the failed starts on file and adds only its own', async () => {
  const config = pauseConfig();
  fs.writeFileSync(pausedPath(config), JSON.stringify({ stopped: [], restore: ['gpu-c.service'],
    failedStart: ['gpu-c.service', 'gpu-c.service'] }));
  const sys = fakeSystemctl(['gpu-a.service'], ['start gpu-a.service']);
  const pauser = createPauser(config, { exec: sys.exec, log: () => {}, leftover: false });
  await pauser.pause();
  // The stop is recorded, and the other run's failure stays on file once.
  assert.deepEqual(readPaused(pausedPath(config)),
    { stopped: ['gpu-a.service'], restore: ['gpu-c.service'], failedStart: ['gpu-c.service'] });
  assert.deepEqual(await pauser.resume(), ['gpu-a.service']);
  assert.deepEqual(readPaused(pausedPath(config)), { stopped: ['gpu-a.service'], restore: ['gpu-c.service'],
    failedStart: ['gpu-c.service', 'gpu-a.service'] });
  // A mark of a unit that already failed to start stays one entry.
  markRestoreFile(config, ['gpu-c.service']);
  assert.deepEqual(readPaused(pausedPath(config)).failedStart, ['gpu-c.service', 'gpu-a.service']);
});

/**
 * An exec stub for the system scope. `down` units answer every systemctl
 * listing, and `sudo -n -l` prints the sudoers rule lines in `rules`.
 */
function fakeHost({ down = [], rules = [] } = {}) {
  const calls = [];
  const exec = (command, args) => {
    calls.push([command, ...args]);
    if (command === 'sudo') {
      return { status: 0, stdout: `User me may run the following commands on host:\n${rules.join('\n')}\n` };
    }
    if (args.includes('list-units') || args.includes('list-unit-files')) {
      return { status: 0, stdout: down.map((unit) => `${unit} loaded inactive dead Test\n`).join('') };
    }
    return { status: 0, stdout: '' };
  };
  return { calls, exec, sudoCalls: () => calls.filter((call) => call[0] === 'sudo') };
}

const sudoRule = (...commands) => `    (root) NOPASSWD: ${commands.map((c) => `/usr/bin/systemctl ${c}`).join(', ')}`;

test('a restore request drops the units sudoers will not start, and asks sudo once', () => {
  const config = pauseConfig();
  const host = fakeHost({ down: ['gpu-a.service', 'gpu-b.service'],
    rules: [sudoRule('stop gpu-a.service', 'start gpu-b.service')] });
  const request = restoreRequest(config, { restore: ['gpu-c.service'], restorePaused: true }, { exec: host.exec });
  assert.deepEqual(request, { units: ['gpu-b.service'], refused: ['gpu-c.service', 'gpu-a.service'] });
  assert.deepEqual(host.sudoCalls(), [['sudo', '-n', '-l']]);
  // A sudo that cannot list refuses every unit, as the setup check does.
  const silent = { exec: (command) => ({ status: command === 'sudo' ? 1 : 0, stdout: '' }) };
  assert.deepEqual(restoreRequest(config, { restore: ['gpu-a.service'] }, silent),
    { units: [], refused: ['gpu-a.service'] });
});

test('a restore request asks sudo nothing for the user scope or for no units', () => {
  const host = fakeHost({ down: ['gpu-a.service'] });
  assert.deepEqual(restoreRequest(pauseConfig({ scope: 'user' }), { restorePaused: true }, { exec: host.exec }),
    { units: ['gpu-a.service'], refused: [] });
  assert.deepEqual(restoreRequest(pauseConfig(), {}, { exec: host.exec }), { units: [], refused: [] });
  assert.deepEqual(host.sudoCalls(), []);
  assert.throws(() => restoreRequest(pauseConfig(), { restore: ['sshd.service'] }, { exec: host.exec }),
    /not on pause.units/);
  assert.deepEqual(host.sudoCalls(), []);
});

test('a refused unit is named and not marked on the job; an allowed one still is', () => {
  const config = pauseConfig();
  addJob(config, { issue: '1' });
  const said = [];
  const log = (line) => said.push(line);
  const none = { units: [], refused: ['gpu-a.service', 'gpu-b.service'] };
  assert.ok(markRestoreRequest(config, 'issue-1', none, log));
  assert.equal(said.length, 2);
  assert.match(said[0], /^restore {2}gpu-a\.service {2}refused {2}sudoers-refused start; not marked/);
  assert.ok(said.every((line) => !line.includes('restores')));
  assert.equal(readQueue(config).jobs[0].restore, undefined);
  assert.ok(!fs.existsSync(pausedPath(config)));
  said.length = 0;
  assert.ok(markRestoreRequest(config, 'issue-1', { units: ['gpu-c.service'], refused: ['gpu-a.service'] }, log));
  assert.equal(said[0], 'issue-1 restores gpu-c.service when it ends');
  assert.match(said[1], /gpu-a\.service/);
  assert.deepEqual(readQueue(config).jobs[0].restore, ['gpu-c.service']);
  // A job that is not waiting or running says nothing about its units.
  said.length = 0;
  assert.equal(markRestoreRequest(config, 'issue-9', { units: ['gpu-c.service'], refused: ['gpu-a.service'] }, log), false);
  // A request that was refused in full still needs a job to name.
  assert.equal(markRestoreRequest(config, 'issue-9', { units: [], refused: ['gpu-a.service'] }, log), false);
  assert.deepEqual(said, []);
  assert.equal(markRestoreRequest(config, 'issue-9', { units: [], refused: [] }, log), true);
});

const UC01_JOB = { issue: '501', change: '7001', docs: ['docs/LIB/UC01-Card-Renewal.md'] };

test('the job check prints a pause unit that sudoers refuses, and fails on it', () => {
  const config = pauseConfig();
  const refusing = fakeHost({ down: ['gpu-a.service'], rules: [sudoRule('stop gpu-a.service')] });
  const result = checkJobAndHost(config, UC01_JOB, { exec: refusing.exec });
  assert.deepEqual(result.lines, ['issue-number  present  issue', 'description  present  found',
    'document-1  present  rules-ok', 'pause  gpu-a.service  fail  sudoers-refused start']);
  assert.equal(result.ok, false);
  // A unit that sudoers allows adds no line, and neither does a config with no pause units or the user scope.
  const allowing = fakeHost({ down: ['gpu-a.service'], rules: [sudoRule('stop gpu-a.service', 'start gpu-a.service')] });
  assert.deepEqual(checkJobAndHost(config, UC01_JOB, { exec: allowing.exec }).lines, checkJob(config, UC01_JOB).lines);
  assert.equal(checkJobAndHost(config, UC01_JOB, { exec: allowing.exec }).ok, true);
  const user = fakeHost({ down: ['gpu-a.service'] });
  assert.equal(checkJobAndHost(pauseConfig({ scope: 'user' }), UC01_JOB, { exec: user.exec }).ok, true);
  assert.deepEqual(user.sudoCalls(), []);
  const none = fakeHost();
  assert.equal(checkJobAndHost(fixtureConfig(), UC01_JOB, { exec: none.exec }).ok, true);
  assert.deepEqual(none.calls, []);
  // A pattern that names a unit twice prints it once.
  const twice = fakeHost({ down: ['gpu-a.service'], rules: [] });
  const both = pauseConfig({ units: ['gpu-*.service', 'gpu-a.service'] });
  const lines = checkJobAndHost(both, UC01_JOB, { exec: twice.exec }).lines;
  assert.equal(lines.filter((l) => l.startsWith('pause  ')).length, 1);
});

test('queue add refuses to promise a restore that sudoers will refuse, and the job check says so first', () => {
  const config = pauseConfig();
  const bin = scratch('build-pack-bin-');
  // A sudo that lists a stop rule for one unit and a start rule for another, and a systemctl that lists one
  // stopped unit.
  fs.writeFileSync(path.join(bin, 'sudo'), '#!/bin/sh\nprintf "User me may run the following commands on host:\\n'
    + '    (root) NOPASSWD: /usr/bin/systemctl stop gpu-a.service, /usr/bin/systemctl start gpu-b.service\\n"\n',
  { mode: 0o755 });
  fs.writeFileSync(path.join(bin, 'systemctl'), '#!/bin/sh\nprintf "gpu-a.service loaded inactive dead Test\\n"\n',
    { mode: 0o755 });
  const env = { ...process.env, PATH: `${bin}${path.delimiter}${process.env.PATH}` };
  const cli = (...args) => spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), ...args,
    '--config', config.file], { encoding: 'utf8', env });
  const checked = cli('check', '--issue', '501', '--change', '7001', '--doc', 'docs/LIB/UC01-Card-Renewal.md');
  assert.equal(checked.status, 1, checked.stderr);
  assert.match(checked.stdout, /^pause {2}gpu-a\.service {2}fail {2}sudoers-refused start$/m);
  const added = cli('queue', 'add', '--issue', '100', '--restore-paused');
  assert.equal(added.status, 0, added.stderr);
  assert.match(added.stdout, /^restore {2}gpu-a\.service {2}refused {2}sudoers-refused start; not marked/m);
  assert.match(added.stdout, /queued issue-100/);
  assert.ok(!added.stdout.includes('restores'));
  assert.equal(readQueue(config).jobs[0].restore, undefined);
  assert.ok(!fs.existsSync(pausedPath(config)));
  assert.deepEqual(cli('queue', 'status', '--job', 'issue-100').stdout.split('\n').filter((l) => l.startsWith('restore')), []);
  // One unit refused and one allowed: only the allowed one is marked.
  const mixed = cli('queue', 'add', '--issue', '101', '--restore', 'gpu-b.service', '--restore-paused');
  assert.equal(mixed.status, 0, mixed.stderr);
  assert.match(mixed.stdout, /^issue-101 restores gpu-b\.service when it ends$/m);
  assert.match(mixed.stdout, /^restore {2}gpu-a\.service {2}refused {2}sudoers-refused start; not marked/m);
  assert.deepEqual(readQueue(config).jobs[1].restore, ['gpu-b.service']);
});

test('pause config is validated', () => {
  assert.throws(() => pauseConfig({ scope: 'machine' }), /pause.scope/);
  assert.throws(() => pauseConfig({ units: 'gpu.service' }), /pause.units/);
  assert.throws(() => pauseConfig({ maxWaitMinutes: -1 }), /pause.maxWaitMinutes/);
  assert.throws(() => pauseConfig({ maxWaitMinutes: 'x' }), /pause.maxWaitMinutes/);
  assert.throws(() => pauseConfig({ maxWaitMinutes: NaN }), /pause.maxWaitMinutes/);
  assert.equal(pauseConfig({ maxWaitMinutes: 0 }).pause.maxWaitMinutes, 0);
  assert.deepEqual(fixtureConfig().pause,
    { units: [], scope: 'system', busyProcess: null, pollSeconds: 5, maxWaitMinutes: 60 });
});

const releaseConfig = (release = {}) => fixtureConfig({
  release: { command: ['lemonade', 'unload'], ...release } });

/** A releaser over a fake command: `status` is its exit code, `events` records order. */
function fakeRelease(events, { status = 0, error = null, signal = null } = {}) {
  const lines = [];
  const exec = (command, args, timeoutMs) => {
    events.push(['unload', command, ...args, timeoutMs]);
    return { status, signal, error };
  };
  return { lines, make: (cfg) => createReleaser(cfg, { exec, log: (l) => lines.push(l) }) };
}

const releaseLines = (config, id) => readStatusLog(path.join(config.output, id, 'status.log'))
  .filter((line) => line.phase === 'release');

test('the model is unloaded once, after the last job and the units start again', async () => {
  const config = releaseConfig();
  const first = addJob(config, { issue: '1' });
  const second = addJob(config, { issue: '2' });
  const events = [];
  const fake = fakeRelease(events);
  const sys = fakeSystemctl(['gpu-a.service']);
  const pauseCfg = Object.assign(config, { pause: { ...config.pause, units: ['gpu-*.service'] } });
  const run = async (cfg, job) => { events.push(['run', job.id]); return { ok: true, ms: 1 }; };
  const spy = (cfg) => {
    const pauser = quiet(sys)(cfg);
    return { pause: () => pauser.pause(), resume: async () => { events.push(['resume']); await pauser.resume(); } };
  };
  await drainQueue(pauseCfg, { run, pause: spy, release: fake.make });
  assert.deepEqual(events.map((e) => e[0]), ['run', 'run', 'resume', 'unload']);
  assert.deepEqual(events.at(-1), ['unload', 'lemonade', 'unload', 60000]);
  assert.deepEqual(fake.lines, ['release: ok']);
  const [line] = releaseLines(config, second.id);
  assert.equal(line.event, 'pass');
  assert.equal(line.job, second.id);
  assert.deepEqual(releaseLines(config, first.id), []);
});

test('a failed job and a job that throws still end with the unload', async () => {
  for (const run of [async () => ({ ok: false, phase: 'phase3', reason: 'model', ms: 1 }),
    async () => { throw new Error('boom'); }]) {
    const config = releaseConfig();
    addJob(config, { issue: '1' });
    const events = [];
    const fake = fakeRelease(events);
    const done = await drainQueue(config, { run, release: fake.make });
    assert.equal(events.length, 1);
    assert.equal(done[0].status, 'queued');
    assert.equal(done[0].failures.length, 1);
  }
});

test('the unload runs when the cutoff ends the run', async () => {
  const config = releaseConfig();
  addJob(config, { issue: '1' });
  addJob(config, { issue: '2' });
  let now = new Date('2026-01-01T06:00:00');
  const clock = () => now;
  const events = [];
  const fake = fakeRelease(events);
  const run = async () => { now = new Date('2026-01-01T07:30:00'); return { ok: true, ms: 1 }; };
  const done = await drainQueue(config, { run, clock, release: fake.make });
  assert.equal(done.length, 1);
  assert.equal(events.length, 1);
});

test('a failed unload is logged and leaves the job result alone', async () => {
  for (const failure of [{ status: 1 }, { status: null, error: { code: 'ENOENT' } },
    { status: null, error: { code: 'ETIMEDOUT' } }, { status: null, signal: 'SIGKILL' }]) {
    const config = releaseConfig();
    addJob(config, { issue: '1' });
    const fake = fakeRelease([], failure);
    const done = await drainQueue(config, { run: okRun, release: fake.make });
    assert.equal(done[0].status, 'passed');
    assert.deepEqual(fake.lines, ['release: failed']);
    const [line] = releaseLines(config, done[0].id);
    assert.equal(line.event, 'fail');
    assert.match(line.reason, /^(exit-1|signal|spawn-error|timeout)$/);
  }
});

test('a command that throws is a failed unload, not a failed run', async () => {
  const config = releaseConfig();
  addJob(config, { issue: '1' });
  const release = (cfg) => createReleaser(cfg, { log: () => {}, exec: () => { throw new Error('x'); } });
  const done = await drainQueue(config, { run: okRun, release });
  assert.equal(done[0].status, 'passed');
  assert.equal(releaseLines(config, done[0].id)[0].reason, 'spawn-error');
});

test('the unload still runs when starting the paused units fails', async () => {
  const config = releaseConfig();
  addJob(config, { issue: '1' });
  const events = [];
  const pause = () => ({ pause: async () => {}, resume: async () => { throw new Error('start'); } });
  await assert.rejects(drainQueue(config, { run: okRun, pause, release: fakeRelease(events).make }),
    /start/);
  assert.equal(events.length, 1);
});

test('a cancelling signal unloads once and the run ending does not unload again', async () => {
  const config = releaseConfig();
  const events = [];
  const fake = fakeRelease(events);
  const releaser = fake.make(config);
  releaser.release();
  assert.equal(events.length, 0);
  releaser.note('job-1');
  releaser.release();
  releaser.release();
  assert.equal(events.length, 1);
  assert.equal(releaseLines(config, 'job-1')[0].event, 'pass');
});

test('nothing is unloaded when no job started or the command is empty', async () => {
  const idle = releaseConfig();
  const events = [];
  await drainQueue(idle, { run: okRun, release: fakeRelease(events).make });
  assert.deepEqual(events, []);

  const off = releaseConfig({ command: [] });
  addJob(off, { issue: '1' });
  await drainQueue(off, { run: okRun, release: fakeRelease(events).make });
  assert.deepEqual(events, []);
});

test('release config has defaults and is validated', () => {
  assert.deepEqual(loadDefault().release, { command: ['lemonade', 'unload'], timeoutSeconds: 60 });
  assert.throws(() => releaseConfig({ command: 'lemonade unload' }), /release.command/);
  assert.throws(() => releaseConfig({ command: ['lemonade', ''] }), /release.command/);
  assert.throws(() => releaseConfig({ timeoutSeconds: 0 }), /release.timeoutSeconds/);
  assert.throws(() => fixtureConfig({ release: 'off' }), /release must be an object/);
  assert.throws(() => fixtureConfig({ release: null }), /release must be an object/);
});

/** The config with no release block, so the shipped default shows. */
function loadDefault() {
  const dir = scratch('build-pack-');
  const raw = JSON.parse(fs.readFileSync(path.join(FIXTURES, 'pipeline.json'), 'utf8'));
  Object.assign(raw, { repoRoot: FIXTURES, output: path.join(dir, 'out'),
    queue: { file: path.join(dir, 'queue.json') } });
  const file = path.join(dir, 'pipeline.json');
  fs.writeFileSync(file, JSON.stringify(raw));
  return loadConfig(file);
}

/** A config whose queue has the given sources, over the fixtures. */
function sourcedConfig(sources, report = {}) {
  const dir = scratch('build-pack-src-');
  return fixtureConfig({ queue: { file: path.join(dir, 'queue.json'), sources }, report });
}

test('a job line is a bare number pair, a suite, or the full command-line form', () => {
  assert.deepEqual(jobFromLine('9415'), { issue: '9415' });
  assert.deepEqual(jobFromLine('  9415 7001  '), { issue: '9415', change: '7001' });
  assert.deepEqual(jobFromLine('suite LIB'), { suite: 'LIB' });
  assert.deepEqual(jobFromLine('--issue 9415 --change 7001 --doc docs/LIB/a.md'),
    { issue: '9415', change: '7001', docs: ['docs/LIB/a.md'] });
  assert.equal(jobFromLine('# a note'), null);
  assert.equal(jobFromLine('   '), null);
  assert.throws(() => jobFromLine('9415 7001 extra'));
  assert.throws(() => jobFromLine('hello world'));
});

test('the queue fills itself from a folder of lists, and never queues a known job twice', () => {
  const dir = scratch('build-pack-in-');
  fs.writeFileSync(path.join(dir, 'build-12.txt'), '# build 12\n9415 7001\n501\nnot a job\n\nsuite LIB\n');
  fs.writeFileSync(path.join(dir, 'more.txt'), '501\n777\n');
  fs.writeFileSync(path.join(dir, '.hidden'), '999\n');
  const config = sourcedConfig([{ type: 'folder', path: dir }]);
  const first = fillQueue(config);
  assert.deepEqual(first.added, ['issue-9415-change-7001', 'issue-501', 'suite-LIB', 'issue-777']);
  assert.equal(first.invalid, 1);
  assert.equal(first.known, 1);
  assert.deepEqual(readQueue(config).jobs.map((row) => row.status), Array(4).fill('queued'));
  // A second pass adds nothing, whatever state the jobs are in now.
  const queue = readQueue(config);
  queue.jobs[1].status = 'passed';
  queue.jobs[2].status = 'failed';
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  assert.deepEqual(fillQueue(config).added, []);
  // A job taken out by hand stays out while the folder still lists it.
  assert.equal(removeJob(config, 'issue-777').removed, true);
  assert.deepEqual(fillQueue(config).added, []);
  assert.equal(removeJob(config, 'issue-501').removed, false);
  assert.equal(summaryLines(readQueue(config)).some((line) => line.startsWith('issue-777')), false);
  // `queue add` still brings a removed job back.
  assert.equal(addJob(config, { issue: '777' }).added, true);
});

test('the queue fills from record file names and from a command, and a bad source is counted', () => {
  const config = sourcedConfig([
    { type: 'records', glob: 'issues/ISSUE_*.md' },
    { type: 'records', glob: 'issues/*.md', pattern: '^ISSUE_(\\d+)_(renewal)' },
    { type: 'command', command: ['node', '-e', 'console.log("600 6001"); console.log("suite LIB")'] },
    { type: 'command', command: ['node', '-e', 'process.exit(3)'] },
    { type: 'folder', path: path.join(SCRATCH_ROOT, 'no-such-folder') },
  ]);
  const result = fillQueue(config);
  // The second pattern's second group is read as a change number.
  assert.deepEqual(result.added, ['issue-501', 'issue-501-change-renewal', 'issue-600-change-6001',
    'suite-LIB']);
  assert.deepEqual(result.errors, ['command:source-command-failed', 'folder:source-missing']);
  assert.equal(result.known, 0);
});

test('a queue source is checked when the config loads', () => {
  const bad = (sources) => () => sourcedConfig(sources);
  assert.throws(bad('folder'), /queue.sources must be a list/);
  assert.throws(bad([{ type: 'folder' }]), /queue.sources takes/);
  assert.throws(bad([{ type: 'ftp', path: 'x' }]), /queue.sources takes/);
  assert.throws(bad([{ type: 'command', command: [] }]), /queue.sources takes/);
  assert.deepEqual(fixtureConfig().queue.sources, []);
});

test('a nightly run fills the queue once it holds it, and a run outside the window does not', async () => {
  const dir = scratch('build-pack-in-');
  fs.writeFileSync(path.join(dir, 'list.txt'), '9415\n');
  const config = sourcedConfig([{ type: 'folder', path: dir }]);
  const ran = [];
  const run = async (_config, job) => { ran.push(job.id); return { ok: true, ms: 1 }; };
  const refill = (cfg) => fillQueue(cfg);
  await drainQueue(config, { cutoff: '07:00', start: '22:00', run, refill,
    clock: () => new Date('2026-10-28T08:00:00') });
  assert.deepEqual(readQueue(config).jobs, []);
  await drainQueue(config, { cutoff: '07:00', start: '22:00', run, refill,
    clock: () => new Date('2026-10-28T22:30:00') });
  assert.deepEqual(ran, ['issue-9415']);
});

test('a failed job retries once on the next night, resumed, and is dropped after the second failure', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501', now: true });
  addJob(config, { issue: '777' });
  const ran = [];
  const outcomes = { 'issue-501': { ok: false, phase: 'phase3', reason: 'gate:unclassified-rule', ms: 60000 } };
  const run = async (_config, job) => {
    ran.push({ id: job.id, resume: job.resume === true, keys: Object.keys(job).sort() });
    return outcomes[job.id] ?? { ok: true, ms: 1, workbook: '/out/w.xlsx' };
  };
  const night = (day) => () => new Date(`2026-10-${day}T22:00:00`);
  await drainQueue(config, { cutoff: '07:00', run, clock: night(27) });
  // Night one: the failure is kept, 777 still runs, and 501 waits for the next night.
  assert.deepEqual(ran.map((r) => r.id), ['issue-501', 'issue-777']);
  let [row] = readQueue(config).jobs;
  assert.equal(row.status, 'queued');
  assert.equal(row.resume, true);
  assert.equal(row.now, undefined);
  assert.deepEqual(row.failures.map((f) => [f.phase, f.reason]), [['phase3', 'gate:unclassified-rule']]);
  assert.ok(new Date(row.notBefore) > night(27)());
  assert.match(summaryLines(readQueue(config))[0], /issue-501\s+queued\s+retry after stopping at phase3/);
  // The same night, a second run does not take it again.
  await drainQueue(config, { cutoff: '07:00', run, clock: night(27) });
  assert.equal(ran.length, 2);
  // The next night it runs again, resumed, with none of the queue's own fields on the job.
  outcomes['issue-501'] = { ok: false, phase: 'phase5', reason: 'model:no-reply', ms: 60000 };
  await drainQueue(config, { cutoff: '07:00', run, clock: night(28) });
  assert.equal(ran.length, 3);
  assert.equal(ran[2].resume, true);
  assert.deepEqual(ran[2].keys, ['id', 'issue', 'resume']);
  [row] = readQueue(config).jobs;
  assert.equal(row.status, 'failed');
  assert.deepEqual(row.failures.map((f) => f.reason), ['gate:unclassified-rule', 'model:no-reply']);
  assert.equal(row.notBefore, undefined);
  assert.match(summaryLines(readQueue(config))[0], /stopped at phase5 \(model:no-reply\), dropped after failing 2 times/);
  // A third night takes nothing: the job is out of the queue.
  await drainQueue(config, { cutoff: '07:00', run, clock: night(29) });
  assert.equal(ran.length, 3);
});

test('a job that fails once and then passes is a pass with its failure on record', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501' });
  let attempt = 0;
  const run = async () => {
    attempt += 1;
    return attempt === 1 ? { ok: false, phase: 'phase2', reason: 'error', ms: 1 }
      : { ok: true, ms: 2, workbook: '/out/w.xlsx' };
  };
  await drainQueue(config, { cutoff: '07:00', run, clock: () => new Date('2026-10-27T22:00:00') });
  await drainQueue(config, { cutoff: '07:00', run, clock: () => new Date('2026-10-28T22:00:00') });
  const [row] = readQueue(config).jobs;
  assert.equal(row.status, 'passed');
  assert.equal(row.failures.length, 1);
});

test('queue remove takes a waiting job out and leaves a running one alone', () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501' });
  addJob(config, { issue: '777' });
  const queue = readQueue(config);
  queue.jobs[1].status = 'running';
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  assert.deepEqual(removeJob(config, 'issue-501'), { id: 'issue-501', removed: true });
  assert.deepEqual(removeJob(config, 'issue-777'), { id: 'issue-777', removed: false, running: true });
  assert.deepEqual(removeJob(config, 'issue-1'), { id: 'issue-1', removed: false, running: false });
  assert.deepEqual(readQueue(config).jobs.map((row) => row.status), ['removed', 'running']);
});

const NOW = new Date('2026-10-28T07:30:00');
const hoursAgo = (h) => new Date(NOW.getTime() - h * 3600000).toISOString();

/** A passed row with its status.log, as a run leaves them. */
function passedJob(config, id, { hours, confidence = 'High', pass = 12, limited = 0, ms = 3600000 }) {
  const outDir = path.join(config.output, id);
  fs.mkdirSync(outDir, { recursive: true });
  const line = (fields) => JSON.stringify({ at: hoursAgo(hours), job: id, ...fields });
  fs.writeFileSync(path.join(outDir, 'status.log'), [
    line({ phase: 'phase9-confidence', event: 'pass', confidence }),
    line({ phase: 'done', event: 'pass', sheetsPass: pass, sheetsLimited: limited, calls: 40 }),
  ].join('\n'));
  return { id, status: 'passed', finished: hoursAgo(hours), ms, workbook: `${outDir}/${id}.xlsx`, phase: 'done' };
}

function reportQueue(config) {
  const failLog = (id, fields) => {
    const outDir = path.join(config.output, id);
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(path.join(outDir, 'status.log'),
      `${JSON.stringify({ at: hoursAgo(2), job: id, phase: 'phase3', event: 'fail', ...fields })}\n`);
  };
  failLog('issue-300', { reason: 'gate:unclassified-rule', sheets: 2 });
  failLog('issue-400', { reason: 'model:no-reply' });
  failLog('issue-500', { reason: 'error' });
  return { jobs: [
    passedJob(config, 'issue-100', { hours: 5, confidence: 'Low' }),
    passedJob(config, 'issue-101', { hours: 6, limited: 2 }),
    passedJob(config, 'issue-102', { hours: 7 }),
    passedJob(config, 'issue-103', { hours: 8, confidence: 'Medium' }),
    passedJob(config, 'issue-104', { hours: 9 }),
    passedJob(config, 'issue-105', { hours: 24 * 3 }),
    // Failed once and waiting for tonight.
    { id: 'issue-400', status: 'queued', resume: true, notBefore: hoursAgo(1),
      failures: [{ at: hoursAgo(2), phase: 'phase5', reason: 'model:no-reply', ms: 120000 }] },
    // Failed twice and dropped.
    { id: 'issue-300', status: 'failed', phase: 'phase3', reason: 'gate:unclassified-rule', ms: 60000,
      finished: hoursAgo(2), failures: [
        { at: hoursAgo(26), phase: 'phase3', reason: 'gate:low-coverage', ms: 1 },
        { at: hoursAgo(2), phase: 'phase3', reason: 'gate:unclassified-rule', ms: 60000 }] },
    // Waiting, never tried.
    { id: 'issue-600', status: 'queued' },
    { id: 'issue-700', status: 'removed', finished: hoursAgo(3) },
    { id: 'issue-800', status: 'running' },
  ] };
}

test('the daily report lists each job, the queue depth and the failing jobs', () => {
  const config = fixtureConfig();
  const data = reportData(config, reportQueue(config), { period: 'day', now: NOW, random: seededRandom(1) });
  // Oldest first.
  assert.deepEqual(data.jobs.map((j) => [j.id, j.state]), [
    ['issue-104', 'PASS'], ['issue-103', 'PASS'], ['issue-102', 'PASS'], ['issue-101', 'PASS'],
    ['issue-100', 'PASS'], ['issue-400', 'RETRY'], ['issue-300', 'DROPPED']]);
  assert.deepEqual(data.counts, { pass: 5, fail: 0, retry: 1, dropped: 1, memory: 0, stopped: 0, held: 0 });
  assert.deepEqual(data.queue, { depth: 2, retrying: 1, running: 1 });
  assert.deepEqual(data.failing.map((j) => j.id), ['issue-400', 'issue-300']);
  const text = renderReport(data);
  assert.match(text, /^# Test pack report, daily, 2026-10-28/);
  assert.match(text, /\| issue-100 \| PASS \| - \| 12 \/ 0 \/ 0 \| Low \| 60 min \|/);
  assert.match(text, /\| issue-101 \| PASS WITH LIMITATIONS \| - \| 12 \/ 2 \/ 0 \| High \| 60 min \|/);
  assert.match(text, /\| issue-300 \| DROPPED \| phase3 gate:unclassified-rule \| - \/ - \/ 2 \| - \| 1 min \|/);
  assert.match(text, /\| issue-400 \| RETRY \| phase5 model:no-reply \| - \/ - \/ - \| - \| 2 min \|/);
  assert.match(text, /issue-300: failed 2 times, last at phase3 \(gate:low-coverage, then gate:unclassified-rule\)\. Dropped from the queue; it needs a person\./);
  assert.match(text, /issue-400: failed at phase5 \(model:no-reply\)\. Retries on its next run\./);
  assert.match(text, /Queue depth: 2 waiting \(1 of them retrying\), 1 running/);
  // The job from three days ago and the removed row are not in a daily report.
  assert.ok(!text.includes('issue-105'));
  assert.ok(!text.includes('issue-700'));
});

test('the weekly rollup covers seven days and counts them by day', () => {
  const config = fixtureConfig();
  const data = reportData(config, reportQueue(config), { period: 'week', now: NOW, random: seededRandom(1) });
  assert.equal(data.jobs.length, 8);
  assert.deepEqual(data.counts, { pass: 6, fail: 0, retry: 1, dropped: 1, memory: 0, stopped: 0, held: 0 });
  const text = renderReport(data);
  assert.match(text, /weekly rollup, 2026-10-28/);
  assert.match(text, /\| 2026-10-25 \| 1 \| 0 \|/);
});

test('spot checks put low confidence first, then PASS WITH LIMITATIONS, then a seeded sample', () => {
  const config = fixtureConfig();
  const queue = reportQueue(config);
  const pick = (seed) => reportData(config, queue,
    { period: 'day', now: NOW, random: seededRandom(seed) }).spot.map((s) => [s.id, s.why]);
  const first = pick(7);
  assert.deepEqual(first.slice(0, 2), [['issue-100', 'low-confidence'], ['issue-101', 'pass-with-limitations']]);
  assert.equal(first.length, 4);
  assert.ok(first.slice(2).every(([, why]) => why === 'random-sample'));
  assert.ok(first.slice(2).every(([id]) => ['issue-102', 'issue-103', 'issue-104'].includes(id)));
  // The same seed gives the same sample; the sample never repeats a priority pack.
  assert.deepEqual(pick(7), first);
  assert.equal(new Set(first.map(([id]) => id)).size, first.length);
  const seen = new Set();
  for (let seed = 0; seed < 30; seed += 1) pick(seed).slice(2).forEach(([id]) => seen.add(id));
  assert.ok(seen.size > 2);
  // The priority list is capped, and the sample size is a setting.
  const passed = ['a', 'b', 'c', 'd'].map((id) => ({ id, confidence: 'Low', limited: false, workbook: null }));
  assert.equal(spotChecks(passed, { maxPriority: 2, sample: 1 }, seededRandom(1)).length, 3);
  assert.equal(spotChecks(passed, { maxPriority: 4, sample: 5 }, seededRandom(1)).length, 4);
  assert.deepEqual(spotChecks([], { maxPriority: 4, sample: 5 }, seededRandom(1)), []);
});

test('the report holds codes and counts only, even when a log line carries text', () => {
  const config = fixtureConfig();
  const queue = reportQueue(config);
  const outDir = path.join(config.output, 'issue-101');
  fs.appendFileSync(path.join(outDir, 'status.log'), `\n${JSON.stringify({ at: hoursAgo(5.5), job: 'issue-101',
    phase: 'phase9-confidence', event: 'pass', confidence: 'Patron renewal text' })}\n`);
  queue.jobs[1].workbook = '/out/Patron renewal.xlsx';
  const text = renderReport(reportData(config, queue, { now: NOW, random: seededRandom(1) }));
  assertContentFree(text);
  assert.ok(text.includes('| other |'));
});

test('the report command writes the daily file, and the weekly rollup on the set weekday', () => {
  const config = fixtureConfig();
  const queue = reportQueue(config);
  const tuesday = new Date('2026-10-27T07:30:00');
  const monday = new Date('2026-10-26T07:30:00');
  assert.equal(monday.getDay(), 1);
  const names = (written) => written.map((w) => path.basename(w.file));
  assert.deepEqual(names(writeReports(config, queue, { now: tuesday })), ['daily-2026-10-27.md']);
  assert.deepEqual(names(writeReports(config, queue, { now: monday })),
    ['daily-2026-10-26.md', 'weekly-2026-10-26.md']);
  assert.deepEqual(names(writeReports(config, queue, { now: tuesday, period: 'week' })), ['weekly-2026-10-27.md']);
  assert.ok(fs.existsSync(path.join(config.output, 'reports', 'weekly-2026-10-27.md')));
  assert.throws(() => writeReports(config, queue, { period: 'month' }), /--period/);
  const other = fixtureConfig({ report: { weeklyDay: 2, dir: path.join(scratch('build-pack-reports-'), 'reports') } });
  assert.deepEqual(names(writeReports(other, queue, { now: tuesday })),
    ['daily-2026-10-27.md', 'weekly-2026-10-27.md']);
  assert.throws(() => fixtureConfig({ report: { weeklyDay: 9 } }), /report.weeklyDay/);
  assert.throws(() => fixtureConfig({ report: { sample: -1 } }), /report.sample/);
});

test('the command line fills the queue and writes the report', () => {
  const dir = scratch('build-pack-in-');
  fs.writeFileSync(path.join(dir, 'list.txt'), '9415\n');
  const config = sourcedConfig([{ type: 'folder', path: dir }]);
  const cli = (...args) => spawnSync('node', [path.join(HERE, 'build-pack.mjs'), ...args,
    '--config', config.file], { encoding: 'utf8' });
  const fillRun = cli('queue', 'fill');
  assert.equal(fillRun.status, 0);
  assert.match(fillRun.stdout, /queued issue-9415\nfilled 1 job\(s\), 0 already known, 0 unreadable line\(s\)/);
  assert.equal(cli('queue', 'remove', '--job', 'issue-9415').status, 0);
  assert.equal(cli('queue', 'remove', '--job', 'issue-9415').status, 1);
  const reportRun = cli('report', '--period', 'day', '--seed', '3');
  assert.equal(reportRun.status, 0);
  assert.match(reportRun.stdout, /wrote day report .*daily-\d{4}-\d\d-\d\d\.md\npassed=0 retrying=0 dropped=0 queued=0/);
});

test('a failure during the day is taken by tonight, and one at night waits for the next night', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501', now: true });
  const ran = [];
  const run = async (_config, job) => {
    ran.push(job.id);
    return { ok: false, phase: 'phase4', reason: 'model:http', ms: 1 };
  };
  const at = (text) => () => new Date(text);
  // A start request at 10:00 fails; the run does not take the job again, and it carries no wait.
  await drainQueue(config, { only: 'issue-501', nowOnly: true, run, clock: at('2026-10-28T10:00:00') });
  assert.deepEqual(ran, ['issue-501']);
  let [row] = readQueue(config).jobs;
  assert.equal(row.status, 'queued');
  assert.equal(row.notBefore, undefined);
  // Tonight's run at 22:00 takes it, and its second failure drops it.
  await drainQueue(config, { cutoff: '07:00', start: '22:00', run, clock: at('2026-10-28T22:00:00') });
  assert.equal(ran.length, 2);
  [row] = readQueue(config).jobs;
  assert.equal(row.status, 'failed');
  // A failure at 23:00 waits until after that night's cutoff, then the next run takes it.
  addJob(config, { issue: '777' });
  await drainQueue(config, { cutoff: '07:00', start: '22:00', run, clock: at('2026-10-28T23:00:00') });
  const retry = readQueue(config).jobs.find((r) => r.id === 'issue-777');
  assert.equal(retry.status, 'queued');
  assert.equal(new Date(retry.notBefore).getTime(), new Date('2026-10-29T07:00:00').getTime());
  await drainQueue(config, { cutoff: '07:00', start: '22:00', run, clock: at('2026-10-29T22:00:00') });
  assert.equal(ran.length, 4);
});

test('an explicit start request takes a job that is waiting for the next night', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501' });
  addJob(config, { issue: '777' });
  const queue = readQueue(config);
  for (const row of queue.jobs) {
    Object.assign(row, { resume: true, notBefore: '2026-10-29T07:00:00.000Z',
      failures: [{ at: '2026-10-28T23:00:00.000Z', phase: 'phase4', reason: 'model:http', ms: 1 }] });
  }
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  const ran = [];
  const run = async (_config, job) => { ran.push(job.id); return { ok: true, ms: 1 }; };
  const clock = () => new Date('2026-10-28T10:00:00');
  // Nothing marked now: the waiting rows stay waiting.
  await drainQueue(config, { nowOnly: true, run, clock });
  assert.deepEqual(ran, []);
  addJob(config, { issue: '501', now: true });
  addJob(config, { issue: '777', now: true });
  await drainQueue(config, { only: 'issue-501', nowOnly: true, run, clock });
  // The named job runs first and the other start-now row follows it.
  assert.deepEqual(ran, ['issue-501', 'issue-777']);
});

test('the default record pattern reads a change only when it starts with a digit', () => {
  const dir = scratch('build-pack-rec-');
  for (const name of ['SIR-9415-credit-limit.md', 'SIR-9416-Create-account.md', 'SIR-9417-crash-on-save.md',
    'SIR-9418-change-7001.md', 'ISSUE_9419_CR7002_renewal.md', 'SIR-9421-changes-to-fees.md',
    'SIR-9422-CR-CHG7001.md', 'SIR-9423-CR-7001,7002.md', 'SIR-9424-CR-7001(1).md',
    'SIR-9425-change-password.md', 'notes.md']) {
    fs.writeFileSync(path.join(dir, name), 'x');
  }
  const config = fixtureConfig({ repoRoot: dir, queue: { file: path.join(dir, 'queue.json'),
    sources: [{ type: 'records', glob: '*.md' }] } });
  const result = fillQueue(config);
  assert.deepEqual([...result.added].sort(), ['issue-9415', 'issue-9416', 'issue-9417',
    'issue-9418-change-7001', 'issue-9419-change-7002', 'issue-9421']);
  // A name the pattern does not read, or one with a change word and no valid change number, is
  // counted and not queued as the issue alone.
  assert.equal(result.invalid, 5);
});

test('queue remove and queue fill by hand refuse while a run holds the queue', () => {
  const dir = scratch('build-pack-in-');
  fs.writeFileSync(path.join(dir, 'list.txt'), '9415\n');
  const config = sourcedConfig([{ type: 'folder', path: dir }]);
  addJob(config, { issue: '777' });
  const cli = (...args) => spawnSync('node', [path.join(HERE, 'build-pack.mjs'), 'queue', ...args,
    '--config', config.file], { encoding: 'utf8' });
  const lock = `${config.at(config.queue.file)}.lock`;
  fs.writeFileSync(lock, String(process.pid));
  const fillRun = cli('fill');
  assert.equal(fillRun.status, 1);
  assert.match(fillRun.stderr, /the queue is running/);
  assert.equal(cli('remove', '--job', 'issue-777').status, 1);
  assert.deepEqual(readQueue(config).jobs.map((row) => row.status), ['queued']);
  fs.rmSync(lock);
  assert.equal(cli('fill').status, 0);
  assert.equal(cli('remove', '--job', 'issue-777').status, 0);
  assert.equal(fs.existsSync(lock), false);
});

test('a report seed must be a whole number', () => {
  assert.throws(() => fixtureConfig({ report: { seed: 'abc' } }), /report.seed/);
  assert.doesNotThrow(() => fixtureConfig({ report: { seed: 7 } }));
  assert.throws(() => seededRandom('x'), /--seed/);
});

test('a job added while the units are being stopped is kept', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501' });
  const pause = () => ({
    pause: async () => { addJob(config, { issue: '777' }); },
    resume: async () => {},
  });
  const run = async () => ({ ok: true, ms: 1 });
  await drainQueue(config, { cutoff: '07:00', run, pause, clock: () => new Date('2026-10-28T10:00:00') });
  assert.deepEqual(readQueue(config).jobs.map((row) => [row.id, row.status]),
    [['issue-501', 'passed'], ['issue-777', 'passed']]);
});

test('a start-only run leaves an interrupted row for the night', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501', now: true });
  addJob(config, { issue: '777', now: true });
  const queue = readQueue(config);
  queue.jobs[0].status = 'running';
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  const ran = [];
  const run = async (_config, job) => { ran.push(job.id); return { ok: true, ms: 1 }; };
  await drainQueue(config, { only: 'issue-777', nowOnly: true, run, clock: () => new Date('2026-10-28T10:00:00') });
  assert.deepEqual(ran, ['issue-777']);
  const [interrupted] = readQueue(config).jobs;
  assert.equal(interrupted.status, 'queued');
  assert.equal(interrupted.now, undefined);
});

test('a change token with no separator before it is still read, or counted when its number is bad', () => {
  const dir = scratch('build-pack-rec-');
  for (const name of ['SIR-9415CR7001.md', 'SIR-9416.CR7002.md', 'SIR-9417Create-account.md',
    'SIR-9418credit-limit.md', 'SIR-9419crash-on-save.md', 'SIR-9420changes-to-fees.md',
    'SIR-9421CR-CHG7001.md', 'SIR-9422.change.md']) {
    fs.writeFileSync(path.join(dir, name), 'x');
  }
  const config = fixtureConfig({ repoRoot: dir, queue: { file: path.join(dir, 'queue.json'),
    sources: [{ type: 'records', glob: '*.md' }] } });
  const result = fillQueue(config);
  assert.deepEqual([...result.added].sort(), ['issue-9415-change-7001', 'issue-9416-change-7002',
    'issue-9417', 'issue-9418', 'issue-9419', 'issue-9420']);
  assert.equal(result.invalid, 2);
});

// Expected Results: the check against the final step, and the per-card verification.
// The conflicting-rule fixture: UC03-001 allows a borrow, UC03-002 blocks it, UC03-003 is a Reset,
// and UC03-004 is a supervisor override that is an exception to the block.

const [ALLOW, BLOCK, RESET, OVERRIDE] = ['BR-LIB.UC03-001', 'BR-LIB.UC03-002', 'BR-LIB.UC03-003',
  'BR-LIB.UC03-004'];
const REFUSED = 'The loan is refused with the message Account on hold';
const WRONG_LOAN = 'The loan goes ahead because the card is current';
const SAVED = 'The loan length shows the saved value';
const WRONG_RESET = 'The loan length shows the edited value';
const OVERRIDDEN = 'The loan is made and the supervisor reason code is recorded';

const holdRun = (extra = {}) => {
  const inputs = { ...fixtureInputs(), documentIndex: 'docs/HOLD/*.md',
    description: 'issues-hold/ISSUE_{issue}_*.md',
    ruleExport: ['node', 'export.mjs', '--doc', '{doc}', '--master', 'master-conflict.json'] };
  return lib({
    // The break pass is matched before the inventory, whose name it extends.
    ...(extra.phase6_scenarios_d1_break
      ? { phase6_scenarios_d1_break: extra.phase6_scenarios_d1_break } : {}),
    intake: (value) => ({ ...value, documents: ['docs/HOLD/UC03-Loan-Holds.md'] }),
    phase6_scenarios: (value) => ({ ...value, scenarios: [
      { kind: 'decision', rules: [ALLOW, BLOCK], population: 'a patron with a current card and a hold',
        action: 'borrow an item', outcome: 'refused' },
      { kind: 'decision', rules: [RESET], population: 'a patron editing the loan length',
        action: 'edit, then press Reset', outcome: 'saved value' },
      { kind: 'break', rules: [BLOCK], population: 'a patron with a hold', action: 'borrow again and again',
        outcome: 'refused' },
      { kind: 'decision', rules: [BLOCK, OVERRIDE], population: 'a patron with a hold and a supervisor',
        action: 'borrow with an override', outcome: 'allowed once' }] }),
    // No card is added to an objective after the cards are written.
    phase6_objective: (value) => ({ ...value, cards: [] }),
    ...extra }, { inputs });
};
const runHold = (run, job = {}) => runJob(run.config, { issue: '502', change: '7002', ...job },
  { model: run.model, echo: false });

/** The card for a scenario; `wrong` names the scenarios whose Expected Result is the wrong one. */
const holdCard = (scenario, wrong = []) => {
  // Only the Reset card names Workflow Validation.
  const [rules, right, bad, objectives] = {
    S1: [[ALLOW, BLOCK], REFUSED, WRONG_LOAN, ['Core Change Validation', 'Negative / Exclusion']],
    S2: [[RESET], SAVED, WRONG_RESET, ['Core Change Validation', 'Workflow Validation']],
    S3: [[BLOCK], REFUSED, WRONG_LOAN, ['Core Change Validation', 'Negative / Exclusion']],
    S4: [[BLOCK, OVERRIDE], OVERRIDDEN, REFUSED, ['Core Change Validation', 'Negative / Exclusion']],
  }[scenario];
  const expected = wrong.includes(scenario) ? bad : right;
  return { title: `Run ${scenario}`, scenario, mission: 'mission', focus: ['focus'], expected, rules,
    objectives, derivation: 'Requirement',
    steps: [{ description: 'Act', expected, rules }] };
};
const holdCards = (wrong = []) => (value) => ({ ...value,
  cards: value.cards.map((card) => holdCard(card.scenario, wrong)) });

/** A verification reply that rejects any card whose text carries a wrong Expected Result. */
const judge = (value, calls) => {
  const cards = {};
  for (const [, label, body] of calls.at(-1).user.matchAll(/### (C\d+)\n([\s\S]*?)(?=\n\n### C|\n## |$)/g)) {
    const noException = /supervisor reason code/.test(body)
      && !/unless a cited rule says it is an exception/.test(calls.at(-1).user);
    const bad = noException || /because the card is current|edited value/.test(body);
    cards[label] = bad ? { why: noException ? 'The block wins.' : /current/.test(body)
      ? 'The hold blocks the loan, and a block outranks the allowance for a current card.'
      : 'Reset restores the saved value.', verdict: 'does not follow' }
      : { why: 'It follows.', verdict: 'follows' };
  }
  return { ...value, cards };
};
const callsNamed = (run, prefix) => run.model.calls.filter((c) => c.schemaName.startsWith(prefix));

/**
 * A run whose Phase 8 sees a card the design passes accepted but whose final step then
 * disagrees: the first run stops before Phase 7, its saved cards are changed, and the
 * job resumes into the builder.
 */
async function resumedWithMismatch(repair, answers = {}) {
  const first = holdRun({ phase6_cards: holdCards(), phase6_verify: judge,
    phase7_sets: () => { throw new Error('stop'); } });
  const stopped = await runHold(first);
  assert.equal(stopped.ok, false);
  const file = path.join(stopped.outDir, 'work', 'checkpoint.json');
  const saved = JSON.parse(read(file));
  const [designed] = Object.values(saved.state.designed);
  designed.cards.find((card) => card.scenario === 'S1').steps.at(-1).expected = 'The page shows nothing';
  fs.writeFileSync(file, JSON.stringify(saved));
  const second = { config: first.config, model: fakeModel({ ...INTAKE, phase8_repair: repair, ...answers }) };
  return { second, result: await runHold(second, { resume: true }) };
}

test('a verification group cut off at length fails the job after one call, with no split', async () => {
  const cut = () => { throw new ModelError('length', 'cut off'); };
  const run = holdRun({ phase6_cards: holdCards(), phase6_verify: cut });
  const result = await runHold(run);
  assert.equal(result.ok, false, JSON.stringify(result));
  assert.match(JSON.stringify(result), /model:length/);
  assert.equal(callsNamed(run, 'phase6_verify').length, 1);
  assert.ok(!statusLines(result.outDir).some((l) => l.event === 'split'));
});

test('a card that agrees with its rules and its last step passes untouched, after one verification call', async () => {
  const run = holdRun({ phase6_cards: holdCards(), phase6_verify: judge });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(result.repairs, 0);
  const verify = callsNamed(run, 'phase6_verify');
  assert.equal(verify.length, 1);
  // Never an empty enum: one row per card in the call, two verdicts.
  const rows = verify[0].schema.properties.cards;
  assert.deepEqual(rows.required, ['C1', 'C2', 'C3', 'C4']);
  assert.deepEqual(S.propOf(rows.properties.C1, 'verdict').enum, ['follows', 'does not follow']);
  // The call carries the card, the rules it cites and their wording, and says which rule wins.
  assert.match(verify[0].user, /Expected Result: The loan is refused with the message Account on hold/);
  assert.match(verify[0].user, /BR-LIB\.UC03-001 \|[^\n]*may borrow up to five items/);
  assert.match(verify[0].user, /BR-LIB\.UC03-002 \|[^\n]*blocks every new loan/);
  assert.match(verify[0].user, /blocks an action outranks one that allows it/);
  assert.match(verify[0].user, /Reset restores the saved value/);
  assert.equal(callsNamed(run, 'phase6_redo').length, 0);
  assert.equal(callsNamed(run, 'phase6_reverify').length, 0);
  const pass = phase6Pass(result.outDir);
  assert.equal(pass.redesigned, 0);
  assert.equal(pass.removed, 0);
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(pack.testCards.map((c) => c.expected).sort(), [OVERRIDDEN, REFUSED, REFUSED, SAVED]);
});

test('the prompt makes the precedence a default, and the override card passes only with the exception clause', async () => {
  const run = holdRun({ phase6_cards: holdCards(), phase6_verify: judge });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const verify = callsNamed(run, 'phase6_verify')[0];
  assert.match(verify.user, /unless a cited rule says it is an exception to the block or overrides it/);
  assert.match(verify.user, /BR-LIB\.UC03-004 \|[^\n]*override allows one loan despite a hold/);
  assert.match(verify.user, /Expected Result: The loan is made and the supervisor reason code is recorded/);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.testCards.some((c) => c.expected === OVERRIDDEN && c.rules.includes(OVERRIDE)));
  assert.equal(phase6Pass(result.outDir).redesigned, 0);
});

/** A Quality card in place of the Reset card: its result is one no cited rule states. */
const qualityCards = (value) => ({ ...value, cards: value.cards.map((card) => (
  card.scenario === 'S2' ? { ...holdCard('S2'), derivation: 'Quality' } : holdCard(card.scenario))) });
/** Rejects a Quality card unless the prompt says to judge it on contradiction alone. */
const strictOnQuality = (value, calls) => {
  const { user } = calls.at(-1);
  const cards = {};
  for (const [, label, body] of user.matchAll(/### (C\d+)\n([\s\S]*?)(?=\n\n### C|\n## |$)/g)) {
    const bad = /Derivation: Quality/.test(body) && !/contradicts a cited rule/.test(user);
    cards[label] = bad ? { why: 'No cited rule states this.', verdict: 'does not follow' }
      : { why: 'It does not contradict the rules.', verdict: 'follows' };
  }
  return { ...value, cards };
};

test('a Quality card is judged on contradiction, shown its derivation, and kept', async () => {
  const run = holdRun({ phase6_cards: qualityCards, phase6_verify: strictOnQuality });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const verify = callsNamed(run, 'phase6_verify');
  assert.match(verify[0].user, /Derivation: Quality/);
  assert.match(verify[0].user, /Never answer "does not follow" for a Quality card/);
  assert.equal(callsNamed(run, 'phase6_redo').length, 0);
  assert.equal(phase6Pass(result.outDir).removed, 0);
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.testCards.find((c) => c.title === 'Run S2').derivation, 'Quality');
  assert.ok(!pack.assumptions.some((a) => a.assumption === 'No card in this pack is quality-derived.'));
});

test('a batch of Requirement cards is not told the Quality standard', async () => {
  const run = holdRun({ phase6_cards: holdCards(), phase6_verify: judge });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.doesNotMatch(callsNamed(run, 'phase6_verify')[0].user, /A card marked Quality/);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.assumptions.some((a) => a.assumption === 'No card in this pack is quality-derived.'));
});

test('a redone Quality card stays Quality and is told to avoid contradiction', async () => {
  const rejectAll = (value, calls) => {
    const out = strictOnQuality(value, calls);
    for (const row of Object.values(out.cards)) row.verdict = 'does not follow';
    return out;
  };
  const toRequirement = (value) => ({ ...value, cards: value.cards.map((card) => ({
    ...holdCard(card.scenario), derivation: 'Requirement' })) });
  const run = holdRun({ phase6_cards: qualityCards, phase6_verify: rejectAll,
    phase6_redo: toRequirement, phase6_reverify: strictOnQuality });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const redo = callsNamed(run, 'phase6_redo');
  assert.ok(redo.length >= 1);
  assert.ok(redo.some((call) => /as a Quality card/.test(call.user)
    && /does not contradict the rules/.test(call.user)));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.testCards.find((c) => c.title === 'Run S2').derivation, 'Quality');
});

test('a card whose Expected Result follows the allowance is redesigned once, told why, and kept when it now follows', async () => {
  const run = holdRun({ phase6_cards: holdCards(['S1']), phase6_verify: judge,
    phase6_redo: holdCards(), phase6_reverify: judge });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const redo = callsNamed(run, 'phase6_redo');
  assert.equal(redo.length, 1);
  assert.deepEqual(scenarioEnum(redo[0].schema), ['S1']);
  assert.match(redo[0].user, /a block outranks the allowance for a current card/);
  assert.match(redo[0].user, /The loan goes ahead because the card is current/);
  assert.equal(callsNamed(run, 'phase6_reverify').length, 1);
  const pass = phase6Pass(result.outDir);
  assert.equal(pass.redesigned, 1);
  assert.equal(pass.removed, 0);
  const pack = JSON.parse(read(result.packPath));
  const card = pack.testCards.find((c) => c.title === 'Run S1');
  assert.equal(card.expected, REFUSED);
  assert.equal(card.steps.at(-1).expected, REFUSED);
  assert.equal(pack.testCards.length, 4);
  assert.ok(!pack.coverage.some((row) => row.status === 'Missing'));
});

test('a card that fails twice is removed, its rule reads Missing with the reason, and no set or objective points at it', async () => {
  const run = holdRun({ phase6_cards: holdCards(['S2']), phase6_verify: judge,
    phase6_redo: holdCards(['S2']), phase6_reverify: judge });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pass = phase6Pass(result.outDir);
  assert.equal(pass.redesigned, 1);
  assert.equal(pass.removed, 1);
  assert.equal(callsNamed(run, 'phase6_redo').length, 1);
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(pack.testCards.map((c) => c.title).sort(), ['Run S1', 'Run S3', 'Run S4']);
  const row = pack.coverage.find((r) => r.ruleId === RESET);
  assert.equal(row.status, 'Missing');
  assert.match(row.gap, /was removed: Reset restores the saved value/);
  assert.ok(pack.assumptions.some((a) => /Run S2.*scenario S2/.test(a.assumption)
    && /Reset restores the saved value/.test(a.why)));
  // The rules the other cards cover keep their cards and get no Missing row.
  assert.ok(!pack.coverage.some((r) => [ALLOW, BLOCK].includes(r.ruleId) && r.status === 'Missing'));
  // Only the removed card named Workflow Validation: the objective is off and no set holds it.
  const workflow = pack.objectives.find((r) => r.objective === 'Workflow Validation');
  assert.equal(workflow.applicable, false);
  const ids = new Set(pack.testCards.map((c) => c.id));
  assert.ok(pack.testSets.every((set) => set.cards.every((id) => ids.has(id))));
  assert.ok(!pack.testSets.some((set) => set.objective === 'Workflow Validation'));
});

test('a redesign that comes back with no card removes the card the same way', async () => {
  const run = holdRun({ phase6_cards: holdCards(['S1']), phase6_verify: judge,
    phase6_redo: (value) => ({ ...value, cards: [] }) });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(callsNamed(run, 'phase6_reverify').length, 0);
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(pack.testCards.map((c) => c.title).sort(), ['Run S2', 'Run S3', 'Run S4']);
  assert.equal(pack.coverage.find((r) => r.ruleId === ALLOW).status, 'Missing');
});

test('a skip the redesign answers with settles the scenario and gives the rule its reason', async () => {
  const run = holdRun({ phase6_cards: holdCards(['S2']), phase6_verify: judge,
    phase6_redo: (value) => ({ ...value, cards: [],
      skipped: [{ scenario: 'S2', how: 'gap', reason: 'The page keeps no saved value to restore.' }] }) });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  const row = pack.coverage.find((r) => r.ruleId === RESET);
  assert.equal(row.status, 'Missing');
  assert.match(row.gap, /No card can cover this rule: The page keeps no saved value to restore\./);
  assert.ok(pack.assumptions.some((a) => /Run S2/.test(a.assumption)
    && /keeps no saved value/.test(a.why)));
});

test('a skip with a blank reason falls back to the verifier\'s reason', async () => {
  const run = holdRun({ phase6_cards: holdCards(['S2']), phase6_verify: judge,
    phase6_redo: (value) => ({ ...value, cards: [],
      skipped: [{ scenario: 'S2', how: 'gap', reason: ' ' }] }) });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.match(pack.coverage.find((r) => r.ruleId === RESET).gap, /No card can cover this rule: Reset restores the saved value\./);
});

// The first card also covers the override rule, which the two listed scenarios do not name.
const withOverride = (cards) => (value) => {
  const out = cards(value);
  return { ...out, cards: out.cards.map((card) => (card.scenario !== 'S1' ? card : { ...card,
    rules: [...card.rules, OVERRIDE],
    steps: card.steps.map((st) => ({ ...st, rules: [...st.rules, OVERRIDE] })) })) };
};

test('a wrong card from the BREAK IT pass is checked too, and BREAK IT is dropped when it ends up empty', async () => {
  const run = holdRun({
    phase6_scenarios: (value) => ({ ...value, scenarios: [
      { kind: 'decision', rules: [ALLOW, BLOCK, OVERRIDE], population: 'a patron with a current card and a hold',
        action: 'borrow an item', outcome: 'refused' },
      { kind: 'decision', rules: [RESET], population: 'a patron editing the loan length',
        action: 'edit, then press Reset', outcome: 'saved value' }] }),
    phase6_scenarios_d1_break: (value) => ({ ...value, scenarios: [
      { kind: 'break', rules: [BLOCK], population: 'a patron with a hold', action: 'borrow again and again',
        outcome: 'refused' }] }),
    phase6_cards: withOverride(holdCards(['S3'])), phase6_verify: judge,
    phase6_redo: withOverride(holdCards(['S3'])), phase6_reverify: judge });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  // The break pass's calls carry their own step names.
  const names = run.model.calls.map((c) => c.schemaName);
  assert.ok(names.includes('phase6_verify_d1_1'));
  assert.ok(names.includes('phase6_verify_d1_break_1'));
  assert.ok(names.includes('phase6_reverify_d1_break_1'));
  const pass = phase6Pass(result.outDir);
  assert.equal(pass.redesigned, 1);
  assert.equal(pass.removed, 1);
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(pack.testCards.map((c) => c.title).sort(), ['Run S1', 'Run S2']);
  assert.equal(pack.objectives.find((r) => r.objective === 'BREAK IT').applicable, false);
  assert.ok(!pack.testSets.some((set) => set.objective === 'BREAK IT'));
});

test('a card too big for one verification call is retried with summaries only', async () => {
  const run = holdRun({ phase6_cards: holdCards(), phase6_verify: judge });
  // The master's full description of the block rule is what makes a call too big.
  const count = run.model.countTokens;
  run.model.countTokens = async (text) => (text.includes('Staff clear the hold to lift') ? 1e9 : count(text));
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const names = run.model.calls.map((c) => c.schemaName);
  assert.ok(names.some((name) => /^phase6_verify_d1_1s\d+short$/.test(name)));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.testCards.length, 4);
  assert.ok(!pack.assumptions.some((a) => /was not checked against its rules/.test(a.assumption)));
});

test('a card too big even with summaries only is kept, with an assumption that it was not verified', async () => {
  const run = holdRun({ phase6_cards: holdCards(), phase6_verify: judge });
  const count = run.model.countTokens;
  run.model.countTokens = async (text) => (text.includes('### C') ? 1e9 : count(text));
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.testCards.length, 4);
  assert.ok(pack.assumptions.some((a) => /was not checked against its rules/.test(a.assumption)));
  assert.equal(phase6Pass(result.outDir).removed, 0);
});

test('a card whose final step only words the result differently is kept and its step aligned, not redone', async () => {
  const wordier = (value) => ({ ...value, cards: value.cards.map((card) => {
    const made = holdCard(card.scenario);
    return card.scenario === 'S1' ? { ...made, steps: [{ ...made.steps[0],
      expected: `${REFUSED} and no loan record is created` }] } : made;
  }) });
  const run = holdRun({ phase6_cards: wordier, phase6_verify: judge });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(result.repairs, 0);
  // The card goes to the verification call like any other, and nothing is redone.
  assert.match(callsNamed(run, 'phase6_verify')[0].user, /and no loan record is created/);
  assert.equal(callsNamed(run, 'phase6_redo').length, 0);
  const pass = phase6Pass(result.outDir);
  assert.equal(pass.redesigned, 0);
  assert.equal(pass.removed, 0);
  const pack = JSON.parse(read(result.packPath));
  const card = pack.testCards.find((c) => c.title === 'Run S1');
  assert.equal(card.expected, REFUSED);
  assert.equal(card.steps.at(-1).expected, REFUSED);
});

test('a card that does not follow is redone whether or not its final step agrees', async () => {
  const both = (value) => ({ ...value, cards: value.cards.map((card) => {
    const made = holdCard(card.scenario, ['S1']);
    return card.scenario === 'S1' ? { ...made, steps: [{ ...made.steps[0], expected: 'The page shows nothing' }] }
      : made;
  }) });
  const run = holdRun({ phase6_cards: both, phase6_verify: judge, phase6_redo: holdCards(),
    phase6_reverify: judge });
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(callsNamed(run, 'phase6_redo').length, 1);
  assert.equal(phase6Pass(result.outDir).redesigned, 1);
});

test('a batch too big for one call is split, with one counts-only status line', async () => {
  const run = holdRun({ phase6_cards: holdCards(), phase6_verify: judge });
  const count = run.model.countTokens;
  let first = true;
  run.model.countTokens = async (text) => {
    if (first && text.includes('### C4')) {
      first = false;
      return 1e9;
    }
    return count(text);
  };
  const result = await runHold(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const split = statusLines(result.outDir).filter((l) => l.event === 'split');
  assert.equal(split.length, 1);
  assert.equal(split[0].cards, 4);
  assert.ok(callsNamed(run, 'phase6_verify').length >= 4);
});

test('an Expected Result that disagrees with its last step reaches repair, which is told to keep the card side', async () => {
  const { second, result } = await resumedWithMismatch((value) => ({ ...value, coverage: [], limitations: [],
    cards: value.cards.map((card) => ({ ...card, expected: REFUSED,
      steps: [{ description: 'Act', expected: REFUSED, rules: card.rules }] })) }));
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(result.repairs, 1);
  const repair = callsNamed(second, 'phase8_repair')[0];
  assert.match(repair.user, /Test Card Expected Results:\nTC-\S+ Expected Result "The loan is refused with the message Account on hold" does not agree with its final step's "The page shows nothing"\. Keep the card's Expected Result/);
  assert.match(repair.user, /change that step's expected result to say the same/);
  assert.equal(repair.schema.properties.cards.maxItems, 1);
  assert.deepEqual(expectedProblems(JSON.parse(read(result.packPath))), []);
});

test('a repair that changes an Expected Result is checked again, and undone when it no longer follows', async () => {
  const { second, result } = await resumedWithMismatch((value) => ({ ...value, coverage: [], limitations: [],
    cards: value.cards.map((card) => ({ ...card, expected: WRONG_LOAN,
      steps: [{ description: 'Act', expected: WRONG_LOAN, rules: card.rules }] })) }),
  { phase6_recheck: judge });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(result.repairs, 1);
  assert.equal(callsNamed(second, 'phase6_recheck').length, 1);
  const pack = JSON.parse(read(result.packPath));
  const card = pack.testCards.find((c) => c.expected === REFUSED && c.steps.at(-1).expected === REFUSED
    && pack.assumptions.some((x) => x.assumption.includes(c.id)));
  assert.equal(card.expected, REFUSED);
  assert.equal(card.steps.at(-1).expected, REFUSED);
  assert.equal(pack.testCards.length, 4);
  assert.ok(pack.assumptions.some((a) => /repair of card TC-\S+ changed its Expected Result/.test(a.assumption)));
});

test('an unfixable mismatch stops the run at the builder gate', async () => {
  const { result } = await resumedWithMismatch((value) => ({ ...value, coverage: [], limitations: [],
    cards: value.cards.map((card) => ({ ...card, expected: 'Unchanged' })) }));
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'gate:builder-fail');
});

test('results agree when equal or when one holds the other, after case and punctuation are set aside', () => {
  const card = (expected, last) => ({ expected, steps: [{ expected: 'first' }, { expected: last }] });
  assert.equal(resultsAgree(card('The loan is refused.', 'the loan is REFUSED')), true);
  assert.equal(resultsAgree(card('The loan is refused', 'The loan is refused with Account on hold')), true);
  assert.equal(resultsAgree(card('The loan is refused with Account on hold', 'The loan is refused')), true);
  // Only the last step counts.
  assert.equal(resultsAgree(card('first', 'The loan is refused')), false);
  // Whole words only: "no" is not inside "know".
  assert.equal(resultsAgree(card('no', 'I know')), false);
  assert.equal(resultsAgree(card('The loan goes ahead', 'The loan is refused')), false);
  assert.equal(resultsAgree(card('', 'The loan is refused')), false);
  assert.equal(resultsAgree(card('The loan is refused', ' ')), false);
  assert.equal(resultsAgree({ expected: 'anything', steps: [] }), true);
});

test('a containment that adds a negation or a condition is a mismatch', () => {
  const card = (expected, last) => ({ expected, steps: [{ expected: last }] });
  assert.equal(resultsAgree(card('Saved', 'Not saved')), false);
  assert.equal(resultsAgree(card('Error message is shown', 'No error message is shown')), false);
  assert.equal(resultsAgree(card('The loan is allowed', 'The loan is allowed only when no hold exists')), false);
  assert.equal(resultsAgree(card('The loan is allowed', 'The loan is allowed unless a hold exists')), false);
  assert.equal(resultsAgree(card('The loan is allowed', "The loan isn't allowed")), false);
  assert.equal(resultsAgree(card('The loan is allowed', 'The loan is allowed until the hold is set')), false);
  assert.equal(resultsAgree(card('The loan is refused', 'The loan is refused except for staff')), false);
  assert.equal(resultsAgree(card('The loan is allowed', "The loan is allowed and can't be undone")), false);
  assert.equal(resultsAgree(card("The loan isn't allowed", "The loan isn't allowed with a message")), true);
  // The same negation on both sides is not extra.
  assert.equal(resultsAgree(card('The loan is not allowed', 'The loan is not allowed with a message')), true);
  assert.equal(resultsAgree(card('The loan is refused', 'The loan is refused with the message Account on hold')), true);
});

// ---- Phase 9: the review reads the built workbook, fixes what it finds, and revalidates ----

const DOCS = { intake: (value) => ({ ...value, documents: ['docs/LIB/UC01-Card-Renewal.md'] }) };
const cardIdIn = (text) => /TC-[A-Z0-9]+-501-\d{3}/.exec(text)[0];
const checksFor = (model, name) => model.calls.filter((c) => c.schemaName.startsWith(name));

/** A checklist that flags the first card's step for as long as the dump shows it unfixed. */
const plantedChecklist = () => {
  let planted = null;
  return (value, calls) => {
    const { user } = calls.at(-1);
    planted ??= cardIdIn(user);
    return { ...value, issues: new RegExp(`Test Name: ${planted} [^\\n]*Description: description value`).test(user)
      ? [{ issue: `${planted} has a step that reads wrong`,
        fix: `Change step 1 of ${planted} to read Corrected step` }] : [] };
  };
};
const correctingRepair = (value) => ({ ...value, coverage: [], limitations: [],
  cards: value.cards.map((card) => ({ ...card,
    steps: card.steps.map((step, i) => (i ? step : { ...step, description: 'Corrected step' })) })) });
// A revalidation call holds only the checks of its group, so a check that is not in the reply is left alone.
const failCheck = (value, check, why, fix = '') => (check in value.checks ? { ...value,
  checks: { ...value.checks, [check]: { why, verdict: 'fail', fix } } } : value);
const failsRevalidation = { phase9_revalidation: (value) =>
  failCheck(value, 'All issues resolved', 'Step 1 still reads wrong') };

test('the review reads the built workbook, applies a fix through repair, and rereads the rebuilt one', async () => {
  const config = fixtureConfig();
  const model = fakeModel({ ...DOCS, phase9_checklist: plantedChecklist(), phase8_repair: correctingRepair });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const [first, again] = checksFor(model, 'phase9_checklist');
  // The review input is the built workbook's rows: card Expected Results and ALM steps.
  assert.match(first.user, /\[Test Cards Markdown row \d+\] Test Case ID: TC-\S+ \| Test Case Title: .*Expected Result: expected value/);
  assert.match(first.user, /\[ALM Upload row \d+\] Test Name: TC-\S+ .*Description: description value \| Expected Result: /);
  assert.match(first.user, /\[Impact Analysis row \d+\] Rule ID: BR-LIB\.UC01-001/);
  assert.match(first.user, /\[Coverage Matrix row/);
  // The fix went through repair, and the next read is of the rebuilt workbook.
  assert.equal(checksFor(model, 'phase8_repair').length, 1);
  assert.match(checksFor(model, 'phase8_repair')[0].user, /Quality Review:\n- TC-\S+ has a step that reads wrong/);
  assert.match(again.user, /Description: Corrected step/);
  assert.ok(again.user.split('description value').length < first.user.split('description value').length);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.testCards.some((c) => c.steps[0].description === 'Corrected step'));
  assert.equal(pack.revalidation, undefined);
  // Revalidation reads the rebuilt workbook and the fixes applied.
  const [revalidation] = checksFor(model, 'phase9_revalidation');
  assert.match(revalidation.user, /Fixes the review attempted/);
  assert.match(revalidation.user, /Description: Corrected step/);
  const validation = readPack(result.workbook).sheet('Workbook Validation');
  assert.ok(validation.rows.every((row) => row.cells.Status !== 'FAIL'));
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('the checklist calls run with thinking off; confidence, senior review and revalidation think', async () => {
  const config = fixtureConfig();
  const model = fakeModel({ ...DOCS, phase9_checklist: plantedChecklist(), phase8_repair: correctingRepair });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const checks = checksFor(model, 'phase9_checklist');
  assert.deepEqual(checks.map((c) => c.schemaName), ['phase9_checklist', 'phase9_checklist_again']);
  for (const call of checks) {
    assert.equal(call.reasoning, false);
    assert.equal(call.maxTokens, config.model.maxOutput);
  }
  for (const name of ['phase9_confidence_overall', 'phase9_confidence_steps', 'phase9_senior_review',
    'phase9_senior_notes', 'phase9_revalidation_traceability', 'phase9_revalidation_resolution',
    'phase9_revalidation_readiness']) {
    const calls = checksFor(model, name);
    assert.ok(calls.length, name);
    assert.ok(calls.every((c) => c.reasoning === true), name);
  }
  const fields = ['remainingRisks', 'assumptions', 'regressionScope', 'breakItScope', 'manualReview'];
  for (const field of fields) {
    const calls = checksFor(model, `phase9_confidence_${field}`);
    assert.ok(calls.length, field);
    assert.ok(calls.every((c) => c.reasoning === false && c.maxTokens === config.model.maxOutput), field);
  }
});

test('a finding repair cannot fix gets two rounds, then revalidation fails: Workbook Validation FAIL and a stop code', async () => {
  const config = fixtureConfig();
  const unfixed = (value) => ({ ...value, coverage: [], limitations: [] });
  const model = fakeModel({ ...DOCS, phase9_checklist: plantedChecklist(), phase8_repair: unfixed,
    ...failsRevalidation });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'gate:revalidation-failed');
  assert.equal(result.phase, 'phase9-revalidate');
  // Two fix rounds at most, each followed by a read of the rebuilt workbook.
  assert.equal(checksFor(model, 'phase8_repair').length, 2);
  assert.equal(checksFor(model, 'phase9_checklist').length, 3);
  // The workbook is kept so the reviewer can see what remains, with the FAIL shown, never PASS.
  assert.ok(result.workbook && fs.existsSync(result.workbook));
  const rows = readPack(result.workbook).sheet('Workbook Validation').rows;
  const row = rows.find((r) => r.cells.Sheet === 'Workbook Validation');
  assert.equal(row.cells.Status, 'FAIL');
  assert.match(row.cells.Notes, /Step 1 still reads wrong/);
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.revalidation.passed, false);
  const lines = statusLines(result.outDir);
  assert.equal(lines.findLast((l) => l.event === 'fail').reason, 'gate:revalidation-failed');
  assert.ok(!lines.some((l) => l.phase === 'done'));
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('a builder that does not show the FAIL leaves no workbook that reads PASS', async () => {
  const config = fixtureConfig({ builder: { module: 'builder-stub.mjs', retries: 2,
    command: ['node', 'builder-lax.mjs', '{pack}', '--out', '{out}'] } });
  const result = await runJob(config, { issue: '501', change: '7001' },
    { model: fakeModel({ ...DOCS, ...failsRevalidation }), echo: false });
  assert.equal(result.reason, 'gate:revalidation-failed');
  assert.equal(result.workbook, null);
  assert.ok(!fs.readdirSync(result.outDir).some((name) => name.endsWith('.xlsx')));
});

test('the morning report lists a revalidation-failed job as failing', () => {
  const at = new Date().toISOString();
  const queue = { jobs: [{ id: 'issue-9', status: 'queued', finished: null, ms: 5, phase: 'phase9-revalidate',
    reason: 'gate:revalidation-failed', workbook: '/out/w.xlsx',
    failures: [{ at, phase: 'phase9-revalidate', reason: 'gate:revalidation-failed', ms: 5 }] }] };
  const data = reportData(fixtureConfig(), queue, { now: new Date(Date.now() + 1000) });
  assert.equal(data.failing.length, 1);
  assert.deepEqual(data.failing[0].reasons, ['gate:revalidation-failed']);
});

test('with no Requirements Matrix export the checklist runs OPS-009 limited and the pack says so', async () => {
  const derivedModel = fakeModel({ intake: (value) => ({ ...value, documents: ['docs/OTHER/UC09-Unmapped.md'] }) });
  const derived = await runJob(fixtureConfig(), { issue: '501', change: '7001', allowDerivedRules: true },
    { model: derivedModel, echo: false });
  assert.equal(derived.ok, true, JSON.stringify(derived));
  assert.match(checksFor(derivedModel, 'phase9_checklist')[0].user, /OPS-009 as limited/);
  const pack = JSON.parse(read(derived.packPath));
  assert.ok(pack.assumptions.some((a) => /OPS-009 ran limited for the rules of/.test(a.assumption)));

  const exported = fakeModel(DOCS);
  const ok = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model: exported, echo: false });
  assert.equal(ok.ok, true, JSON.stringify(ok));
  assert.doesNotMatch(checksFor(exported, 'phase9_checklist')[0].user, /OPS-009/);
  assert.ok(!JSON.parse(read(ok.packPath)).assumptions.some((a) => /OPS-009/.test(a.assumption)));
});

test('a workbook too long for one review call is read in parts, and a failing part fails revalidation', async () => {
  const config = fixtureConfig();
  // The room shrinks once the cards are built, so only the review's reads are split.
  const shrink = (value) => {
    Object.assign(config.model, { context: 7700, reasoningOutput: 1000, maxOutput: 500, retryOutput: 500 });
    return value;
  };
  const longer = (value) => ({ ...value, cards: value.cards.map((c) => ({ ...c, title: 'Long title '.repeat(150) })) });
  const model = fakeModel({ ...DOCS, phase6_cards: longer, phase7: shrink, phase9_revalidation: (value, calls) =>
    (/part 2 of/.test(calls.at(-1).user)
      ? failCheck(value, 'Traceability complete', 'A card lost its rule') : value) });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  const parts = checksFor(model, 'phase9_checklist');
  assert.ok(parts.length > 1, `${parts.length} checklist calls: ${JSON.stringify(result)}`);
  assert.match(parts[0].user, /Built workbook, part 1 of \d+/);
  assert.equal(result.reason, 'gate:revalidation-failed');
});

test('a placeholder fix, or one naming no card, rule or sheet, is not handed to repair', async () => {
  const flag = (fix) => () => ({ issues: [{ issue: 'The coverage reads thin', fix }], coverage: [], assumptions: [] });
  for (const fix of ['N/A', 'None needed', 'Review the pack again']) {
    const model = fakeModel({ ...DOCS, phase9_checklist: flag(fix) });
    const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
    assert.equal(result.ok, true, JSON.stringify(result));
    assert.equal(checksFor(model, 'phase8_repair').length, 0, fix);
    assert.equal(checksFor(model, 'phase9_checklist').length, 1, fix);
  }
});

test('a fix round for a finding that names only a card leaves the pack\'s coverage rows and limitations as they were', async () => {
  const model = fakeModel({ ...DOCS, phase9_checklist: plantedChecklist(),
    phase8_repair: (value) => ({ ...correctingRepair(value),
      coverage: [{ ruleId: 'BR-LIB.UC01-001', status: 'Missing', strength: 'Weak', gap: 'x', recommendation: 'y' }],
      limitations: [{ sheet: 'Coverage Matrix', text: 'A repair limitation.' }] }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.ok(!pack.coverage.some((row) => row.ruleId === 'BR-LIB.UC01-001' && row.status === 'Missing'));
  assert.ok(!Object.values(pack.limitations ?? {}).includes('A repair limitation.'));
});

const finding = (issue, fix) => () => ({ issues: [{ section: 'Coverage Completeness', issue, fix }],
  coverage: [], assumptions: [] });
const rowFor = (pack, ruleId) => pack.coverage.find((row) => row.ruleId === ruleId);

test('a checklist finding that names a rule its cards cite goes to repair with those cards', async () => {
  const model = fakeModel({ ...DOCS,
    phase9_checklist: finding('BR-LIB.UC01-001 is covered by one thin card', 'Strengthen the coverage of BR-LIB.UC01-001'),
    phase8_repair: (value) => ({ ...value, coverage: [], limitations: [] }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const repairs = checksFor(model, 'phase8_repair');
  assert.ok(repairs.length >= 1);
  assert.match(repairs[0].user, /Section: Coverage Completeness/);
  assert.match(repairs[0].user, /Cards that cite BR-LIB\.UC01-001: TC-/);
  assert.ok(checksFor(model, 'phase9_checklist').length > 1);
});

test('a finding that names the Coverage Matrix keeps the coverage row and limitation the repair wrote', async () => {
  const model = fakeModel({ ...DOCS,
    phase9_checklist: finding('The Coverage Matrix understates BR-LIB.UC01-001', 'Mark BR-LIB.UC01-001 Partially Covered in the Coverage Matrix'),
    phase8_repair: (value) => ({ ...value,
      coverage: [{ ruleId: 'BR-LIB.UC01-001', status: 'Partially Covered', strength: 'Moderate',
        gap: 'Gap from the review', recommendation: 'Add a card.' }],
      limitations: [{ sheet: 'Coverage Matrix', text: 'Limitation from the review.' }] }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(rowFor(pack, 'BR-LIB.UC01-001').gap, 'Gap from the review');
  assert.equal(pack.limitations['Coverage Matrix'], 'Limitation from the review.');
});

test('a repaired coverage row that denies the coverage a card gives is not kept', async () => {
  const model = fakeModel({ ...DOCS,
    phase9_checklist: finding('BR-LIB.UC01-001 has no coverage', 'Mark BR-LIB.UC01-001 Missing'),
    phase8_repair: (value) => ({ ...value,
      coverage: [{ ruleId: 'BR-LIB.UC01-001', status: 'Missing', strength: 'None', gap: 'x', recommendation: 'y' }],
      limitations: [] }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.notEqual(rowFor(JSON.parse(read(result.packPath)), 'BR-LIB.UC01-001').status, 'Missing');
});

test('a finding that asks for an assumption adds the assumption the repair wrote', async () => {
  const model = fakeModel({ ...DOCS,
    phase9_checklist: finding('The pack does not say which accounts are in scope', 'Add an assumption that only active accounts are in scope'),
    phase8_repair: (value) => ({ ...value, coverage: [], limitations: [],
      ...(value.assumptions ? { assumptions: [{ assumption: 'Only active accounts are in scope.',
        why: 'The review asked.', impact: 'Inactive accounts are not tested.', clarification: 'Confirm.' }] } : {}) }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.ok(JSON.parse(read(result.packPath)).assumptions.some((a) => a.assumption === 'Only active accounts are in scope.'));
});

test('the checklist asks each issue for its Validation section', async () => {
  const model = fakeModel(DOCS);
  await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  const [call] = checksFor(model, 'phase9_checklist');
  assert.deepEqual(S.propOf(call.schema.properties.issues.items, 'section').enum, [
    'Requirements Matrix Integrity', 'Rule Integrity', 'Test Card Structure', 'Coverage Completeness',
    'Traceability', 'Consistency']);
});

test('revalidation reads the review sheets and the validation sheet that the checklist skips', async () => {
  const model = fakeModel(DOCS);
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const [checklist] = checksFor(model, 'phase9_checklist');
  const [revalidation] = checksFor(model, 'phase9_revalidation');
  for (const sheet of ['Executive Summary', 'Senior Tester Review', 'Tester Notes', 'Confidence Assessment',
    'Workbook Validation']) {
    assert.match(revalidation.user, new RegExp(`\\[${sheet} row`), sheet);
    assert.doesNotMatch(checklist.user, new RegExp(`\\[${sheet} row`), sheet);
  }
});

test('revalidation answers one verdict for each Revalidation check, and a failed check is named in what remains', async () => {
  const model = fakeModel({ ...DOCS, ...failsRevalidation });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  const calls = checksFor(model, 'phase9_revalidation');
  const asked = calls.map((call) => Object.keys(call.schema.properties.checks.properties));
  assert.deepEqual(asked, [
    ['Requirement ID references preserved', 'Requirements Matrix integrity preserved', 'Traceability complete',
      'No uncovered Requirement IDs remain unless explicitly documented'],
    ['All issues resolved', 'No regressions introduced'],
    ['Test pack is ready for ALM execution']]);
  assert.equal(result.reason, 'gate:revalidation-failed');
  assert.deepEqual(JSON.parse(read(result.packPath)).revalidation.remaining,
    ['All issues resolved: Step 1 still reads wrong']);
});

test('a revalidation check that fails with a fix gets one repair round and one more revalidation', async () => {
  const model = fakeModel({ ...DOCS, phase8_repair: correctingRepair,
    phase9_revalidation: (value, calls) => (!calls.at(-1).schemaName.endsWith('_again')
      ? failCheck(value, 'Traceability complete', `${cardIdIn(calls.at(-1).user)} reads wrong`,
        `Change step 1 of ${cardIdIn(calls.at(-1).user)} to read Corrected step`) : value) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(checksFor(model, 'phase8_repair_revalidation').length, 1);
  // The fix a group's verdict carried is what the repair round is asked to apply.
  assert.match(checksFor(model, 'phase8_repair_revalidation')[0].user,
    /Section: Traceability complete\n {2}Fix: Change step 1 of TC-\S+ to read Corrected step/);
  assert.deepEqual(checksFor(model, 'phase9_revalidation').map((call) => call.schemaName), [
    'phase9_revalidation_traceability', 'phase9_revalidation_resolution', 'phase9_revalidation_readiness',
    'phase9_revalidation_traceability_again', 'phase9_revalidation_resolution_again',
    'phase9_revalidation_readiness_again']);
  assert.equal(JSON.parse(read(result.packPath)).revalidation, undefined);
});

test('the revalidation calls of one workbook share their prompt up to a last question that names the group, and each thinks under its own limit', async () => {
  const config = fixtureConfig();
  const model = fakeModel(DOCS);
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const calls = checksFor(model, 'phase9_revalidation');
  assert.equal(calls.length, 3);
  assert.deepEqual(calls.map((call) => call.maxTokens), [12288, 8192, 8192]);
  const split = (call) => call.user.split('\n## Question\n');
  const [shared] = split(calls[0]);
  for (const call of calls) {
    assert.equal(call.system, calls[0].system);
    assert.equal(split(call).length, 2);
    assert.equal(split(call)[0], shared);
    assert.ok(split(call)[1].trim().split('\n').length >= 2, 'the question is the last section');
  }
  assert.match(split(calls[0])[1], /- Traceability complete/);
  assert.match(split(calls[1])[1], /- All issues resolved\n- No regressions introduced/);
  assert.match(split(calls[2])[1], /- Test pack is ready for ALM execution/);
  assert.doesNotMatch(shared, /Traceability complete/);
});

test('a workbook read in parts is walked part by part, every group of a part before the next part', async () => {
  const config = fixtureConfig();
  const shrink = (value) => {
    Object.assign(config.model, { context: 7700, reasoningOutput: 1000, maxOutput: 500, retryOutput: 500 });
    return value;
  };
  const longer = (value) => ({ ...value, cards: value.cards.map((c) => ({ ...c, title: 'Long title '.repeat(150) })) });
  const model = fakeModel({ ...DOCS, phase6_cards: longer, phase7: shrink });
  await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  const first = checksFor(model, 'phase9_revalidation').slice(0, 6);
  assert.deepEqual(first.map((call) => /part (\d+) of/.exec(call.user)[1]), ['1', '1', '1', '2', '2', '2']);
  assert.deepEqual(first.slice(0, 3).map((call) => call.schemaName), [
    'phase9_revalidation_traceability', 'phase9_revalidation_resolution', 'phase9_revalidation_readiness']);
  // A part the check is not shown in answers with the verdict that says so.
  assert.ok(first.every((call) => S.propOf(call.schema.properties.checks.properties[Object.keys(
    call.schema.properties.checks.properties)[0]], 'verdict').enum.includes('not shown in this part')));
});

test('a senior review is asked in two calls, the notes seeing the review fields already written', async () => {
  const model = fakeModel(DOCS);
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const [review, notes, ...more] = checksFor(model, 'phase9_senior');
  assert.deepEqual(more, []);
  assert.deepEqual([review.schemaName, notes.schemaName], ['phase9_senior_review', 'phase9_senior_notes']);
  assert.deepEqual([review.maxTokens, notes.maxTokens], [12288, 12288]);
  assert.deepEqual(Object.keys(review.schema.properties), ['seniorReview']);
  assert.deepEqual(Object.keys(notes.schema.properties), ['testerNotes']);
  assert.doesNotMatch(review.user, /Fields already written/);
  assert.match(notes.user, /Fields already written[\s\S]*- Senior Tester Review missed: missed value/);
  // The question comes last and names the part's fields.
  assert.match(review.user, /## Question\n\nWrite the Senior Tester Review fields: missed, businessBehavior[^\n]*\n$/);
  assert.match(notes.user, /## Question\n\nWrite the Tester Notes fields: testData, execution[^\n]*\n$/);
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.seniorReview.missed, 'missed value');
  assert.equal(pack.testerNotes.testData, 'testData value');
});

test('a tester note that repeats a review field is asked for again, and a second refusal fails the senior step whole', async () => {
  const twin = 'The renewal flow was exercised end to end and nothing was missed.';
  const model = fakeModel({ ...DOCS,
    phase9_senior_review: (value) => ({ ...value, seniorReview: { ...value.seniorReview, missed: twin } }),
    phase9_senior_notes: (value) => ({ ...value, testerNotes: { ...value.testerNotes, testData: twin } }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'gate:review-field-unsupported');
  assert.equal(checksFor(model, 'phase9_senior_review').length, 1);
  const notes = checksFor(model, 'phase9_senior_notes');
  assert.equal(notes.length, 2);
  assert.match(notes[1].user, /Your last answer was refused: Tester Notes testData: it repeats the text of Senior Tester Review missed/);
  // The part that passed is not kept on its own: the step fails whole and a resume asks both again.
  assert.equal(result.phase, 'phase9-senior');
  assert.ok(!statusLines(result.outDir).some((l) => l.event === 'pass' && l.phase === 'phase9-senior'));
});

/** A builder command that also refuses a confidence its assumptions do not support. */
const ceilingBuilder = { module: 'builder-stub.mjs', retries: 2,
  command: ['node', 'builder-ceiling.mjs', '{pack}', '--out', '{out}'] };
const reviewDir = (outDir) => path.join(outDir, 'work', 'review');

test('a pack over the Medium assumption limit comes out of Phase 8 with a Draft workbook the review reads', async () => {
  const many = Array.from({ length: 12 }, (_, i) => ({ assumption: `Assumption ${i + 1} holds for this change`,
    basis: 'The document says so' }));
  const model = fakeModel({ ...DOCS, phase3_scope: (value) => ({ ...value, assumptions: many }) });
  const result = await runJob(fixtureConfig({ builder: ceilingBuilder }), { issue: '501', change: '7001' },
    { model, echo: false, until: 'phase9-checklist' });
  assert.equal(result.ok, true, JSON.stringify(result));
  const lines = statusLines(result.outDir);
  assert.ok(lines.some((l) => l.phase === 'phase8' && l.event === 'draft' && l.written === true));
  assert.ok(!lines.some((l) => l.reason === 'review-workbook-missing'));
  assert.ok(fs.readdirSync(reviewDir(result.outDir)).some((name) => name.endsWith('.xlsx')));
  const draft = JSON.parse(read(path.join(reviewDir(result.outDir), 'draft-pack.json')));
  assert.ok(draft.assumptions.length > 10, `${draft.assumptions.length} assumptions`);
  assert.deepEqual([draft.confidence.overall, draft.executiveSummary.confidence,
    draft.limitations['Confidence Assessment']], ['Low', 'Low', 'Pending review.']);
  assert.match(checksFor(model, 'phase9_checklist')[0].user, /\[Test Cards Markdown row/);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

/** The ceiling as a builder module too, so the pipeline can read the confidence ceiling from it. */
const ceilingModule = { ...ceilingBuilder, module: 'builder-ceiling.mjs' };
const manyAssumptions = { phase3_scope: (value) => ({ ...value,
  assumptions: Array.from({ length: 12 }, (_, i) => ({ assumption: `Assumption ${i + 1} holds for this change`,
    basis: 'The document says so' })) }) };
const overallCalls = (model) => model.calls.filter((c) => c.schemaName === 'phase9_confidence_overall');

test('a rating above the confidence ceiling is lowered to it in code, and the builder passes the pack', async () => {
  const model = fakeModel({ ...DOCS, ...manyAssumptions,
    phase9_confidence_overall: (value) => ({ ...value, overall: 'High', reason: 'BR-LIB.UC01-001 is fully covered.' }) });
  const result = await runJob(fixtureConfig({ builder: ceilingModule }), { issue: '501', change: '7001' },
    { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  // The call is told the ceiling with the builder's reason, and offered only the levels under it.
  const [call, ...more] = overallCalls(model);
  assert.equal(more.length, 0);
  assert.match(call.user,
    /The highest level this pack supports is Low, because \d+ assumptions against a limit of 10\. Do not rate it higher\./);
  assert.deepEqual(S.propOf(call.schema, 'overall').enum, ['Low']);
  // The reply rated above it all the same, so code lowers it and says why on the sheet.
  const lines = statusLines(result.outDir);
  const [line, ...others] = lines.filter((l) => l.event === 'confidence');
  assert.equal(others.length, 0);
  assert.deepEqual([line.step, line.overall, line.asked, line.cappedBy],
    ['confidence-overall', 'Low', 'High', 'confidence-ceiling']);
  const pack = JSON.parse(read(result.packPath));
  const lowered = /^BR-LIB\.UC01-001 is fully covered\. The rating was lowered to what the pack supports: \d+ assumptions against a limit of 10\.$/;
  assert.equal(pack.confidence.overall, 'Low');
  assert.match(pack.confidence.reason, lowered);
  assert.match(pack.limitations['Confidence Assessment'], lowered);
  assert.equal(pack.executiveSummary.confidence, `Low. ${pack.confidence.reason}`);
  // The rebuild before revalidation passes on its first build, and nothing is lowered a second time.
  assert.deepEqual(lines.filter((l) => l.step === 'rebuild' && l.event === 'builder').map((l) => [l.attempt, l.failed]),
    [[0, 0]]);
  assert.ok(!lines.some((l) => l.event === 'confidence-lowered' || l.event === 'fail'));
  assert.ok(fs.existsSync(result.workbook));
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('a rating an untested objective and the ceiling both hold down takes the ceiling, and its line names the ceiling', async () => {
  const run = lib({ ...DROP_RUN,
    phase3_scope: (value) => manyAssumptions.phase3_scope(NOT_REMOVAL.phase3_scope(value)),
    phase9_confidence_overall: (value) => ({ ...value, overall: 'High', reason: 'BR-1 is covered.' }) },
  { builder: ceilingModule });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const [line] = statusLines(result.outDir).filter((l) => l.event === 'confidence');
  assert.deepEqual([line.overall, line.asked, line.cappedBy, line.untested], ['Low', 'High', 'confidence-ceiling', 1]);
  const { confidence } = JSON.parse(read(result.packPath));
  assert.match(confidence.reason, /^BR-1 is covered\. No test card serves .+ untested\. The rating was lowered to what the pack supports: \d+ assumptions against a limit of 10\.$/);
});

test('a builder module with no confidenceCeiling export is asked for any level, and its rating stands', async () => {
  const model = fakeModel({ ...DOCS, ...manyAssumptions,
    phase9_confidence_overall: (value) => ({ ...value, overall: 'High', reason: 'BR-LIB.UC01-001 is fully covered.' }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const [call] = overallCalls(model);
  assert.doesNotMatch(call.user, /highest level this pack supports/);
  assert.match(call.user, /rules\s+out the highest level\. Do not state a confidence level in the reason/);
  assert.deepEqual(S.propOf(call.schema, 'overall').enum, ['High', 'Medium', 'Low']);
  const lines = statusLines(result.outDir);
  assert.deepEqual(lines.filter((l) => l.event === 'confidence').map((l) => [l.overall, l.asked, l.cappedBy]),
    [['High', 'High', 'none']]);
  assert.ok(!lines.some((l) => l.event === 'confidence-lowered'));
  assert.equal(JSON.parse(read(result.packPath)).confidence.overall, 'High');
});

test('a rating above the ceiling stops the review of a builder with no confidenceCeiling export', async () => {
  const model = fakeModel({ ...DOCS, ...manyAssumptions,
    phase9_confidence_overall: (value) => ({ ...value, overall: 'High', reason: 'BR-LIB.UC01-001 is fully covered.' }) });
  const result = await runJob(fixtureConfig({ builder: ceilingBuilder }), { issue: '501', change: '7001' },
    { model, echo: false });
  assert.deepEqual([result.ok, result.phase, result.reason], [false, 'phase9-revalidate', 'gate:builder-fail']);
  const fail = statusLines(result.outDir).findLast((l) => l.event === 'fail');
  assert.equal(fail.failedSheets, 'Confidence Assessment');
});

test('a Draft workbook the builder refuses after every repair stops the job at Phase 8', async () => {
  const refuse = 'console.log(["FAIL                   Coverage Matrix", "    planted coverage note",'
    + ' "FAIL                   Workbook Validation", "    1 worksheet fails"].join("\\n")); process.exit(1)';
  const config = fixtureConfig({ builder: { module: 'builder-stub.mjs', retries: 2, command: ['node', '-e', refuse] } });
  const model = fakeModel(DOCS);
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.deepEqual([result.ok, result.phase, result.reason], [false, 'phase8', 'gate:builder-fail']);
  const repairs = checksFor(model, 'phase8_repair');
  assert.equal(repairs.length, 2);
  assert.match(repairs[0].user, /Coverage Matrix:\nplanted coverage note/);
  assert.doesNotMatch(repairs[0].user, /Workbook Validation:\n/);
  const lines = statusLines(result.outDir);
  assert.deepEqual(lines.filter((l) => l.event === 'draft').map((l) => [l.written, l.failed]),
    [[false, 1], [false, 1], [false, 1]]);
  assert.ok(!lines.some((l) => l.phase.startsWith('phase9')));
  assert.ok(!fs.readdirSync(reviewDir(result.outDir)).some((name) => name.endsWith('.xlsx')));
});

test('a builder that writes no Draft workbook and names no failed sheet stops Phase 8 without a repair', async () => {
  const config = fixtureConfig({ builder: { module: 'builder-stub.mjs', retries: 2, command: ['node', '-e', '0'] } });
  const model = fakeModel(DOCS);
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.deepEqual([result.ok, result.phase, result.reason], [false, 'phase8', 'gate:builder-fail']);
  assert.equal(checksFor(model, 'phase8_repair').length, 0);
  assert.deepEqual(statusLines(result.outDir).filter((l) => l.event === 'draft').map((l) => [l.written, l.failed]),
    [[false, 0]]);
});

test('a Draft workbook the builder refuses in Phase 9 stops the job, and the review never reads a summary instead', async () => {
  // Refuses every draft once the senior review is written; the stub writes the ones before it.
  const refuseAfterSenior = 'const fs = require("fs"); const [p, , o] = process.argv.slice(1);'
    + ' if (JSON.parse(fs.readFileSync(p, "utf8")).seniorReview.missed !== "Pending review.") {'
    + ' console.log("FAIL                   Senior Tester Review\\n    planted senior note"); process.exit(1); }'
    + ' process.exit(require("child_process").spawnSync(process.execPath, ["builder-stub.mjs", p, "--out", o],'
    + ' { stdio: "inherit" }).status);';
  const config = fixtureConfig({ builder: { module: 'builder-stub.mjs', retries: 2,
    command: ['node', '-e', refuseAfterSenior, '{pack}', '--out', '{out}'] } });
  const model = fakeModel(DOCS);
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.deepEqual([result.ok, result.phase, result.reason], [false, 'phase9-confidence', 'gate:builder-fail']);
  assert.ok(checksFor(model, 'phase9_senior').length);
  assert.ok(!model.calls.some((call) => /Pack summary/.test(call.user)));
  assert.ok(!statusLines(result.outDir).some((l) => l.event === 'warn' && l.phase === 'phase9'));
  assert.match(read(path.join(result.outDir, 'detail.log')), /planted senior note/);
});

test('every part of a split workbook opens with the rules index, and a job missing rules says which documents', async () => {
  const config = fixtureConfig();
  const shrink = (value) => {
    Object.assign(config.model, { context: 7400, reasoningOutput: 1000, maxOutput: 500, retryOutput: 500 });
    return value;
  };
  const longer = (value) => ({ ...value, cards: value.cards.map((c) => ({ ...c, title: 'Long title '.repeat(150) })) });
  const model = fakeModel({ ...DOCS, phase6_cards: longer, phase7: shrink });
  await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  const parts = checksFor(model, 'phase9_checklist');
  assert.ok(parts.length > 1);
  for (const part of parts) assert.match(part.user, /Rules in this part and the cards that cite them[\s\S]*BR-LIB\.UC01-001 \| [^|]+ \| cards: /);
  const mixed = fakeModel({ intake: (value) => ({ ...value,
    documents: ['docs/LIB/UC01-Card-Renewal.md', 'docs/OTHER/UC09-Unmapped.md'] }) });
  await runJob(fixtureConfig(), { issue: '501', change: '7001', allowDerivedRules: true }, { model: mixed, echo: false });
  assert.match(checksFor(mixed, 'phase9_checklist')[0].user, /rule export held no rules for [^.]*UC09/);
});

test('a job whose revalidation failed is not retried by the queue', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '300', now: true });
  let runs = 0;
  const run = async () => {
    runs += 1;
    return { ok: false, id: 'issue-300', phase: 'phase9-revalidate', reason: 'gate:revalidation-failed',
      ms: 1, workbook: '/out/w.xlsx' };
  };
  const t = new Date('2026-10-28T14:00:00');
  await drainQueue(config, { nowOnly: true, run, clock: () => t });
  const [row] = readQueue(config).jobs;
  assert.equal(runs, 1);
  assert.equal(row.status, 'failed');
  assert.equal(row.workbook, '/out/w.xlsx');
});

test('Phase 4 rates the impacted rules from the impact analysis and raises a Direct Change rule below High', async () => {
  const model = fakeModel({ ...INTAKE, ...NOT_REMOVAL,
    phase3_scope: (value) => {
      value.rules['BR-LIB.UC01-006'] &&= { ...value.rules['BR-LIB.UC01-006'], impact: 'Not Impacted' };
      value.rules['BR-LIB.UC01-001'] = { ...value.rules['BR-LIB.UC01-001'], impact: 'Direct Change' };
      value.rules['BR-LIB.UC01-002'] = { ...value.rules['BR-LIB.UC01-002'], impact: 'Indirect Impact' };
      return value;
    },
    phase4_risk: (value) => {
      for (const id of Object.keys(value.rules)) value.rules[id] = { ...value.rules[id], risk: 'Medium' };
      return value;
    } });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  const risk = (id) => pack.rules.find((rule) => rule.id === id).risk;
  // The Direct Change rule is raised to High; the Indirect one keeps what the analysis gave.
  assert.equal(risk('BR-LIB.UC01-001'), 'High');
  assert.equal(risk('BR-LIB.UC01-002'), 'Medium');
  assert.match(read(path.join(result.outDir, 'detail.log')),
    /phase4 raised risk[\s\S]*BR-LIB\.UC01-001: Medium to High/);
  // The rating call sees the impact and the master's risk, beside the impact analysis.
  const rating = model.calls.find((call) => call.schemaName.startsWith('phase4_risk'));
  assert.match(rating.user, /BR-LIB\.UC01-001 .*\| Direct Change \| master risk: \w+/);
  assert.match(rating.user, /Impact analysis/);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('Phase 4 rates only the impacted rules when every rule carries a master risk', async () => {
  const model = fakeModel({ ...INTAKE, ...NOT_REMOVAL,
    phase3_scope: (value) => {
      for (const id of Object.keys(value.rules)) value.rules[id] = { ...value.rules[id], impact: 'Not Impacted' };
      value.rules['BR-LIB.UC01-001'] = { ...value.rules['BR-LIB.UC01-001'], impact: 'Direct Change' };
      return value;
    } });
  // The pack with one impacted rule stops at the builder, after Phase 4 has rated its rules.
  await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  const rated = model.calls.filter((call) => call.schemaName.startsWith('phase4_risk'))
    .flatMap((call) => Object.keys(call.schema.properties.rules.properties));
  assert.deepEqual(rated, ['BR-LIB.UC01-001']);
});

test('a suite pack keeps the approved risks and rates no rule that has one', async () => {
  const model = fakeModel();
  const result = await runJob(fixtureConfig(), { suite: 'LIB' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const rated = model.calls.filter((call) => call.schemaName.startsWith('phase4_risk'));
  assert.equal(rated.length, 0);
  assert.doesNotMatch(read(path.join(result.outDir, 'detail.log')), /phase4 raised risk/);
});

test('the Phase 4 rating call carries the executive summary its batches are budgeted for', async () => {
  const config = fixtureConfig();
  const long = { phase4_impact: (value) => ({ ...value,
    executiveSummary: { ...value.executiveSummary, summary: 'Long summary. '.repeat(900) } }),
  phase3_scope: (value) => {
    value.rules['BR-LIB.UC01-006'] &&= { ...value.rules['BR-LIB.UC01-006'], impact: 'Not Impacted' };
    value.rules['BR-LIB.UC01-001'] = { ...value.rules['BR-LIB.UC01-001'], impact: 'Direct Change' };
    return value;
  } };
  const model = fakeModel({ ...INTAKE, ...long });
  await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  const rating = model.calls.find((call) => call.schemaName.startsWith('phase4_risk'));
  assert.ok(rating, 'Phase 4 made no rating call');
  assert.match(rating.user, /Long summary\./);
});

// ---- Phase 9: the confidence assessment field by field, and the senior review last ----

test('each Confidence Assessment field is written on its own after the senior review, and the overall level comes last', async () => {
  const model = fakeModel(DOCS);
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const names = [...new Set(model.calls.map((call) => call.schemaName))]
    .filter((name) => /^phase9_(confidence|senior)/.test(name));
  assert.deepEqual(names, ['phase9_senior_review', 'phase9_senior_notes', 'phase9_confidence_remainingRisks',
    'phase9_confidence_assumptions', 'phase9_confidence_regressionScope',
    'phase9_confidence_breakItScope', 'phase9_confidence_manualReview',
    'phase9_confidence_steps', 'phase9_confidence_overall']);
  // A field call asks for that field alone, sees the fields already written, and sees the cards.
  const second = model.calls.find((call) => call.schemaName === 'phase9_confidence_assumptions');
  assert.deepEqual(Object.keys(second.schema.properties), ['assumptions']);
  assert.match(second.user, /Fields already written[\s\S]*Confidence Assessment remainingRisks:/);
  assert.match(second.user, /Cards and the rules they cite[\s\S]*TC-MOD-501-001/);
  assert.match(second.user, /\[Test Cards Markdown row \d+\]/);
  // The senior review no longer sees a confidence assessment; the assessment sees the review.
  for (const part of ['phase9_senior_review', 'phase9_senior_notes']) {
    assert.doesNotMatch(model.calls.find((call) => call.schemaName === part).user, /Confidence assessment/);
  }
  assert.match(second.user, /Senior review/);
  const pack = JSON.parse(read(result.packPath));
  assert.match(pack.confidence.manualReview, /^The manualReview is covered by /);
  assert.equal(pack.confidence.overall, 'High');
});

test('the Coverage field is counted from the Coverage Matrix in code, never asked of the model', async () => {
  const model = fakeModel({ ...DOCS, phase9_confidence_overall: (value) => ({ ...value, overall: 'Medium' }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(model.calls.filter((call) => call.schemaName === 'phase9_confidence_coverage').length, 0);
  const pack = JSON.parse(read(result.packPath));
  assert.match(pack.confidence.coverage, /^Of \d+ rule\(s\) in the Coverage Matrix: \d+ /);
  const steps = model.calls.find((call) => call.schemaName === 'phase9_confidence_steps');
  assert.deepEqual(Object.keys(steps.schema.properties.steps.properties),
    ['rules', 'decisions', 'coverage', 'regression', 'qualityDerived', 'breakIt',
      'professionalReview', 'residualRisk']);
});

test('a Low rating builds the Draft workbook with its own reason, and no stand-in reaches the pack', async () => {
  const model = fakeModel({ ...DOCS, phase9_confidence_overall: (value) => ({ ...value, overall: 'Low',
    reason: 'BR-LIB.UC01-001 has only one card and the criteria for Medium are not met.' }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.ok(fs.readdirSync(reviewDir(result.outDir)).some((name) => name.endsWith('.xlsx')));
  const draft = JSON.parse(read(path.join(reviewDir(result.outDir), 'draft-pack.json')));
  assert.match(draft.limitations['Confidence Assessment'], /only one card/);
  const text = read(result.packPath);
  assert.ok(!text.includes('Pending review.'), 'a stand-in reached the finished pack');
  assert.match(JSON.parse(text).limitations['Confidence Assessment'], /only one card/);
});

test('every level carries its reason, which follows the level in the Executive Summary', async () => {
  const model = fakeModel({ ...DOCS, phase9_confidence_overall: (value) => ({ ...value, overall: 'Medium',
    reason: 'BR-LIB.UC01-002 meets the Medium criteria with two cards.' }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.executiveSummary.confidence, 'Medium. BR-LIB.UC01-002 meets the Medium criteria with two cards.');
  assert.equal(pack.limitations['Confidence Assessment'], undefined);
});

test('a field that repeats another is asked for again with what was wrong', async () => {
  const long = 'Every rule is covered by at least one card, such as TC-MOD-501-001, in this workbook.';
  const model = fakeModel({ ...DOCS,
    'phase9_confidence_remainingRisks': () => ({ remainingRisks: long }),
    'phase9_confidence_assumptions': (value, calls) => {
      const tries = calls.filter((call) => call.schemaName === 'phase9_confidence_assumptions').length;
      return tries === 1 ? { assumptions: long } : value;
    } });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const asks = model.calls.filter((call) => call.schemaName === 'phase9_confidence_assumptions');
  assert.equal(asks.length, 2);
  assert.match(asks[1].user, /refused: it repeats the text of Confidence Assessment remainingRisks/);
  assert.match(JSON.parse(read(result.packPath)).confidence.assumptions, /^The assumptions is covered/);
});

test('a field that cites a card the workbook lacks is refused, and a second refusal stops the job', async () => {
  const cited = () => ({ remainingRisks: 'Card TC-MOD-501-999 covers it, and nothing else remains open.' });
  const once = fakeModel({ ...DOCS, 'phase9_confidence_remainingRisks': (value, calls) =>
    (calls.filter((call) => call.schemaName === 'phase9_confidence_remainingRisks').length === 1 ? cited() : value) });
  const fixed = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model: once, echo: false });
  assert.equal(fixed.ok, true, JSON.stringify(fixed));
  const asks = once.calls.filter((call) => call.schemaName === 'phase9_confidence_remainingRisks');
  assert.match(asks[1].user, /refused: it cites TC-MOD-501-999, which the workbook does not hold/);

  const always = fakeModel({ ...DOCS, 'phase9_confidence_remainingRisks': cited });
  const stopped = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model: always, echo: false });
  assert.equal(stopped.ok, false);
  assert.equal(stopped.reason, 'gate:review-field-unsupported');
  assert.equal(stopped.phase, 'phase9-confidence');
  assertContentFree(read(path.join(stopped.outDir, 'status.log')));
});

test('a field that is too short, or names no rule or card, is refused', async () => {
  for (const [text, why] of [['Nothing remains.', /too short/],
    ['Nothing remains open after these cards were written for the change.', /names no rule or card/]]) {
    const model = fakeModel({ ...DOCS, 'phase9_confidence_remainingRisks': (value, calls) =>
      (calls.filter((call) => call.schemaName === 'phase9_confidence_remainingRisks').length === 1
        ? { remainingRisks: text } : value) });
    const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
    assert.equal(result.ok, true, JSON.stringify(result));
    const asks = model.calls.filter((call) => call.schemaName === 'phase9_confidence_remainingRisks');
    assert.match(asks[1].user, why);
  }
});

test('a manual review answer may name no ID, and an assumptions answer too when the pack has none', async () => {
  const model = fakeModel({ ...DOCS,
    phase9_confidence_manualReview: () => ({ manualReview: 'Nothing needs a hand check beyond the normal execution of the cards.' }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(model.calls.filter((c) => c.schemaName === 'phase9_confidence_manualReview').length, 1);
});

test('the calls that rate confidence never read the stand-in rating as a rating', async () => {
  const model = fakeModel(DOCS);
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  for (const name of ['phase9_confidence_remainingRisks', 'phase9_confidence_steps', 'phase9_confidence_overall']) {
    const call = model.calls.find((c) => c.schemaName === name);
    assert.doesNotMatch(call.user, /\[Dashboard row \d+\][^\n]*Overall Confidence/, name);
  }
});

test('a reason that states a different level is asked for again', async () => {
  const model = fakeModel({ ...DOCS, phase9_confidence_overall: (value, calls) => ({ ...value, overall: 'Medium',
    reason: calls.filter((c) => c.schemaName === 'phase9_confidence_overall').length === 1
      ? 'BR-LIB.UC01-001 holds it down because confidence is low there.'
      : 'BR-LIB.UC01-001 has two cards and meets the Medium criteria.' }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const asks = model.calls.filter((c) => c.schemaName === 'phase9_confidence_overall');
  assert.equal(asks.length, 2);
  assert.match(asks[1].user, /Your last reason was refused/);
  assert.match(JSON.parse(read(result.packPath)).confidence.reason, /two cards/);
});

test('a reason that still states another level after the second try loses that phrase', async () => {
  const model = fakeModel({ ...DOCS, phase9_confidence_overall: (value) => ({ ...value, overall: 'High',
    reason: 'Confidence is High for BR-LIB.UC01-001, though confidence is Medium elsewhere and confidence is Low there.' }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.doesNotMatch(pack.confidence.reason, /confidence is (Medium|Low)/i);
  assert.match(pack.confidence.reason, /^Confidence is High/);
  assert.match(pack.executiveSummary.confidence, /^High\. /);
});

test('a revalidation that leaves items open rates the pack again, with the Low limitation and the report', async () => {
  const model = fakeModel({ ...DOCS,
    phase9_revalidation: (value) => failCheck(value, 'Traceability complete', 'A card lost its rule'),
    phase9_confidence_overall: (value, calls) => (calls.filter((c) => c.schemaName === 'phase9_confidence_overall').length === 1
      ? { ...value, overall: 'High', reason: 'BR-LIB.UC01-001 is fully covered.' }
      : { ...value, overall: 'Low', reason: 'Revalidation left Traceability open on BR-LIB.UC01-001.' }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.reason, 'gate:revalidation-failed');
  assert.equal(model.calls.filter((c) => c.schemaName === 'phase9_confidence_overall').length, 2);
  const again = model.calls.filter((c) => c.schemaName === 'phase9_confidence_overall')[1];
  assert.match(again.user, /Revalidation items still open[\s\S]*Traceability complete/);
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.confidence.overall, 'Low');
  assert.match(pack.limitations['Confidence Assessment'], /Traceability open/);
  assert.match(pack.executiveSummary.confidence, /^Low\. /);
  const line = statusLines(result.outDir).findLast((l) => l.phase === 'phase9-revalidate' && l.event === 'pass');
  assert.equal(line.confidence, 'Low');
});

test('a job saved at the confidence step before the senior review moved reruns both', async () => {
  const { readCheckpoint, checkpointPath } = await import('./run.mjs');
  const dir = scratch('checkpoint-');
  fs.mkdirSync(path.join(dir, 'work'));
  fs.writeFileSync(checkpointPath(dir), JSON.stringify({ phase: 'phase9-confidence', state: {} }));
  assert.equal(readCheckpoint(dir).phase, 'phase9-checklist');
  fs.writeFileSync(checkpointPath(dir), JSON.stringify({ phase: 'phase9-confidence',
    state: { confidenceSteps: [] } }));
  assert.equal(readCheckpoint(dir).phase, 'phase9-confidence');
});

test('a senior review answer with a repeated or unsupported field is asked for again', async () => {
  const model = fakeModel({ ...DOCS, phase9_senior_review: (value, calls) => {
    const tries = calls.filter((call) => call.schemaName === 'phase9_senior_review').length;
    return tries === 1
      ? { ...value, seniorReview: { ...value.seniorReview, missed: 'See BR-LIB.UC01-099.' } } : value;
  } });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const asks = model.calls.filter((call) => call.schemaName === 'phase9_senior_review');
  assert.equal(asks.length, 2);
  assert.match(asks[1].user, /Senior Tester Review missed: it cites BR-LIB\.UC01-099/);
  assert.equal(JSON.parse(read(result.packPath)).seniorReview.missed, 'missed value');
});

// ---------------------------------------------------------------------------
// Intake records only what is missing; the change description is the ALM fields.

const RECORD = [
  '# SIR 501', '', 'Status: Open', 'Short Description: Renewal counts from the wrong day', '',
  '## Long Description', '', 'A card renewed early loses days.', 'Both renewal paths take the fix.', '',
  '## Comments', '', 'Reviewer note that is not a description.', ''].join('\n');

test('the change description holds the ALM short and long descriptions only', () => {
  const text = almDescriptions(RECORD);
  assert.equal(text, 'Renewal counts from the wrong day\n\nA card renewed early loses days.\n'
    + 'Both renewal paths take the fix.');
  assert.ok(!text.includes('Reviewer note'));
  assert.ok(!text.includes('Status'));
});

test('a record that labels neither description is used whole', () => {
  assert.equal(almDescriptions('Plain record text.\n'), 'Plain record text.');
});

test('the pack takes the ALM descriptions while the model reads the whole record', async () => {
  const config = fixtureConfig();
  const file = path.join(path.dirname(config.output), 'record.md');
  fs.writeFileSync(file, RECORD);
  const model = fakeModel({ intake: (value) => ({ ...value, documents: ['docs/LIB/UC01-Card-Renewal.md'] }) });
  const result = await runJob(config, { issue: '501', change: '7001', descriptionFile: file },
    { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.changeDescription, almDescriptions(RECORD));
  assert.match(model.calls.find((c) => c.schemaName.startsWith('intake')).user, /Reviewer note/);
});

const provenance = (lines) => `# Design\n\n**Document provenance**\n\n${lines.join('\n')}\n\nBody.\n`;
const campDoc = (revised) => ({ name: 'Credit Design', text: provenance([
  '- Source: `Credit Design.doc`',
  '- SharePoint: [Credit Design.doc](<host>/sites/x/Shared%20Documents/CAMP%20Designs/Credit%20Design.doc?web=1)',
  `- Revised: ${revised}, from the revision history table`]) });

test('a document whose provenance path is under CAMP Designs is the CAMP document and its date the updated design', () => {
  const found = documentInputs([campDoc('2026-09-30')], 'The CAMP design changed.');
  assert.deepEqual(found.missing, []);
  assert.deepEqual(found.received, ['CAMP document: Credit Design',
    'Updated design: Credit Design, revised 2026-09-30']);
});

test('a CAMP document without a revision date leaves the updated design missing', () => {
  const doc = campDoc('x');
  doc.text = doc.text.replace(/- Revised:.*\n/, '- Revised: not stated\n');
  const found = documentInputs([doc], '');
  assert.equal(found.received.length, 1);
  assert.equal(found.missing.length, 1);
  assert.match(found.missing[0], /^Updated design/);
});

test('a record naming a CAMP design with no CAMP document lists both as missing, and one that does not lists neither', () => {
  const other = { name: 'Other', text: provenance(['- Source: `Other.doc`', '- Revised: 2026-01-01, x']) };
  assert.equal(documentInputs([other], 'See the CAMP design.').missing.length, 2);
  assert.deepEqual(documentInputs([other], 'A plain change.').missing, []);
});

test('a document with derived rules is listed as missing its rules', () => {
  const found = documentInputs([{ name: 'Doc', text: '', ruleCode: 'rules-derived' }], '');
  assert.match(found.missing[0], /^Business rules for Doc/);
});

test('intake lists nothing missing for a job whose inputs all arrived, whatever the model says', async () => {
  const config = fixtureConfig();
  const model = fakeModel({ intake: (value) => ({ ...value, documents: ['docs/LIB/UC01-Card-Renewal.md'],
    missing: ['OPS-008 preferred input'] }) });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(pack.intake.missing, []);
  assert.equal(pack.intake.readiness, 'READY');
  assert.ok(!(pack.limitations ?? {})['Job Intake']);
});

test('assumptions citing rule IDs or counts the pack does not hold are dropped', () => {
  const rules = ['BR-ABC-001', 'BR-ABC-002', 'BR-ABC-003'].map((id, i) => ({ id, sourceDocument: 'Doc',
    module: 'MOD', impact: i ? 'Not Impacted' : 'Direct Change', risk: 'Low', summary: 's' }));
  const keep = (assumption) => ({ assumption, why: 'w', impact: 'i', clarification: 'c' });
  const pack = { rules, testCards: [{ rules: ['BR-ABC-001'], derivation: 'Requirement', module: 'MOD' }],
    coverage: [], assumptions: [
      keep('BR-ABC-001 is read as written.'), keep('BR-ABC-099 is read as written.'),
      keep('The 3 rules of the document are all read.'), keep('The 40 rules of the document are all read.'),
      keep('The 2 impacted rules are read.'), keep('The 7 test cards are read.'),
      keep('The 1 card is read.'), keep('OPS-009 ran limited.')] };
  assert.equal(dropUnfoundedAssumptions({}, pack), 3);
  assert.deepEqual(pack.assumptions.map((a) => a.assumption), [
    'BR-ABC-001 is read as written.', 'The 3 rules of the document are all read.',
    'The 2 impacted rules are read.', 'The 1 card is read.', 'OPS-009 ran limited.']);
});

// An evidence rule as a consumer's config holds it; the pipeline itself names no such rule.
const EVIDENCE_RULE = {
  id: 'stageClosure',
  objective: '^integration\\b',
  claim: 'the change includes the stage closure submit after a FATL downgrade',
  terms: ['\\bFATLs?\\b[^.\\n]{0,80}\\bdowngrad|\\bdowngrad[^.\\n]{0,80}\\bFATLs?\\b',
    '\\bstage[ -]closures?\\b[^.\\n]{0,80}\\bsubmi(?:t|ts|tted|tting|ssion)\\b|\\bsubmi(?:t|ts|tted|tting|ssion)\\b[^.\\n]{0,80}\\bstage[ -]closures?\\b'],
  reason: 'The change includes the stage closure submit after a FATL downgrade,'
    + ' so the window is tested together with the stage it closes.',
};

/**
 * Phase 5 with a model that marks every objective not applicable and answers the
 * evidence rows from `closure`; returns the Integration Testing row and the log.
 * `options.evidence` is the config's evidence rules, `options.suite` runs a suite pack.
 */
async function runPhase5(description, rules, closure, objectives = ['Core Change Validation', 'Integration Testing', 'BREAK IT'], context = 100000, options = {}) {
  const evidence = options.evidence ?? [EVIDENCE_RULE];
  const model = fakeModel({ phase5: (value) => {
    for (const row of Object.values(value.objectives)) row.applicable = false;
    return { ...value, ...closure };
  } });
  const logged = [];
  const ctx = { pack: { rules, executiveSummary: {} }, ref: { core: [], chapters: () => [] },
    job: options.suite ? { suite: 'SUITE' } : {}, builder: { OBJECTIVES: objectives }, coreObjective: 'Core Change Validation',
    description, model, calls: 0, tokens: { prompt: 0, output: 0 },
    config: { model: { context, reasoningOutput: 100, maxOutput: 100 }, objectiveEvidence: evidence },
    logs: { detail: (label, text) => logged.push(`${label}: ${text}`), status() {}, call() {} }, private() {} };
  await phase5(ctx);
  return { row: ctx.pack.objectives.find((row) => row.objective === 'Integration Testing'), logged, model };
}

const SENTENCE = 'The window submits the stage closure after a FATL downgrade.';
const claim = (quote, id = EVIDENCE_RULE.id) => ({ evidence: { [id]: { holds: true, quote } } });
const impacted = (impact, summary = SENTENCE) => ({ impact, name: 'Rule', summary });

test('a quote found in the ALM descriptions marks Integration Testing applicable', async () => {
  const { row, model } = await runPhase5(`Short Description: ${SENTENCE}`, [],
    claim('the window submits the  STAGE closure after a FATL downgrade.'));
  assert.equal(row.applicable, true);
  assert.equal(row.reason, EVIDENCE_RULE.reason);
  const asked = model.calls.find((c) => c.schemaName.startsWith('phase5'));
  assert.ok(asked.schema.properties.evidence);
  assert.match(asked.user, /evidence\.stageClosure\.quote/);
  assert.match(asked.user, /Integration Testing is applicable when the change includes the stage closure/);
});

test('a quote from a Direct Change rule is accepted, one from a Not Impacted rule is not', async () => {
  const ok = await runPhase5('x', [impacted('Direct Change')], claim(SENTENCE));
  assert.equal(ok.row.applicable, true);
  const no = await runPhase5('x', [impacted('Not Impacted')], claim(SENTENCE));
  assert.equal(no.row.applicable, false);
  assert.match(no.logged.join('\n'), /evidence stageClosure was rejected/);
});

test('the prompt lists the impacted rules, and a quote from one is accepted when the description lacks the terms', async () => {
  const rule = { impact: 'Direct Change', name: 'Stage closure', summary: 'Submit the stage closure after a FATL downgrade.' };
  const notes = '**Short Description**: A label changes.\n**Comments**: The window submits the stage closure after a FATL downgrade.';
  const { row, model } = await runPhase5(notes, [rule, impacted('Not Impacted', 'Hidden rule text.')],
    claim('Stage closure. Submit the stage closure after a FATL downgrade.'));
  assert.equal(row.applicable, true);
  const user = model.calls.find((c) => c.schemaName.startsWith('phase5')).user;
  assert.match(user, /- Stage closure\. Submit the stage closure after a FATL downgrade\./);
  assert.ok(!user.includes('Hidden rule text'));
  assert.ok(!user.includes('Comments'));
  // A quote from the comments is outside the description the check reads.
  const rejected = await runPhase5(notes, [], claim('The window submits the stage closure after a FATL downgrade.'));
  assert.equal(rejected.row.applicable, false);
});

test('only the impacted rules that hold both terms reach the prompt, as many as fit', async () => {
  const other = Array.from({ length: 50 }, (_, i) => ({ impact: 'Direct Change', name: `Other ${i}`,
    summary: 'Unrelated behavior of the window.' }));
  const hit = { impact: 'Indirect Impact', name: 'Closure', summary: 'Submit the stage closure after a FATL downgrade.' };
  const small = await runPhase5('x', [...other, hit], claim(SENTENCE));
  const user = small.model.calls.find((c) => c.schemaName.startsWith('phase5')).user;
  assert.match(user, /- Closure\. Submit the stage closure after a FATL downgrade\./);
  assert.ok(!user.includes('Other 0.'));
  assert.ok(!small.logged.some((line) => /left out/.test(line)));
  const many = Array.from({ length: 40 }, (_, i) => ({ impact: 'Direct Change', name: `Closure ${i}`,
    summary: `Submit the stage closure after a FATL downgrade, and ${'check the window. '.repeat(3)}`.replace(/\. /g, ' ') + '.' }));
  const capped = await runPhase5('x', many, claim(SENTENCE), undefined, 5000);
  const cappedUser = capped.model.calls.find((c) => c.schemaName.startsWith('phase5')).user;
  const sent = (cappedUser.match(/^- Closure \d+\./gm) ?? []).length;
  assert.ok(sent > 0 && sent < 40, `sent ${sent}`);
  assert.match(capped.logged.join('\n'), new RegExp(`${40 - sent} of 40 rule lines did not fit`));
});

test('a rule summary with a line break or a long space run is listed and its quote accepted', async () => {
  for (const summary of ['After a FATL is downgraded, the stage closure\nis submitted again.',
    `After a FATL downgrade, the stage closure${' '.repeat(100)}is submitted again.`]) {
    const rule = { impact: 'Direct Change', name: 'Closure', summary };
    const { row, model } = await runPhase5('x', [rule],
      claim(`Closure. ${summary}`.replace(/\s+/g, ' ')));
    const user = model.calls.find((c) => c.schemaName.startsWith('phase5')).user;
    assert.match(user, /- Closure\. After a FATL/, summary);
    assert.equal(row.applicable, true, summary);
  }
});

test('plural FATLs and stage closures are accepted in a quote', async () => {
  for (const text of ['Submitting stage closures after FATL downgrades fails.',
    'After FATLs are downgraded, stage closure submit fails.']) {
    const { row } = await runPhase5(`Short Description: ${text}`, [], claim(text));
    assert.equal(row.applicable, true, text);
  }
});

test('a quote that is not in the record is rejected and logged', async () => {
  const { row, logged } = await runPhase5('A plain change.', [], claim(SENTENCE));
  assert.equal(row.applicable, false);
  assert.match(logged.join('\n'), /evidence stageClosure was rejected: quote not in/);
});

test('a quote that names only one of the downgrade and the submit is rejected', async () => {
  for (const text of ['The window shows a new label after a FATL downgrade.',
    'The window submits the stage closure.']) {
    const { row, logged } = await runPhase5(`Short Description: ${text}`, [], claim(text));
    assert.equal(row.applicable, false, text);
    assert.match(logged.join('\n'), /lacks the terms of the rule/);
  }
});

test('a missing quote or a false answer leaves the model\'s choice', async () => {
  assert.equal((await runPhase5(SENTENCE, [], claim(''))).row.applicable, false);
  const denied = await runPhase5(SENTENCE, [], { evidence: { stageClosure: { holds: false, quote: SENTENCE } } });
  assert.equal(denied.row.applicable, false);
  assert.ok(!denied.logged.some((line) => /rejected/.test(line)));
});

test('with no evidence rules in the config Phase 5 asks for no evidence and keeps the model\'s choice', async () => {
  const { row, model, logged } = await runPhase5(`Short Description: ${SENTENCE}`, [impacted('Direct Change')],
    {}, undefined, undefined, { evidence: [] });
  assert.equal(row.applicable, false);
  const asked = model.calls.find((c) => c.schemaName.startsWith('phase5'));
  assert.equal(asked.schema.properties.evidence, undefined);
  assert.ok(!asked.user.includes('Direct Change and Indirect Impact rules'));
  assert.ok(!/stage closure|FATL/i.test(asked.user.replace(SENTENCE, '')));
  assert.ok(!logged.some((line) => /evidence/.test(line.replace("reply: [object Object]", ""))));
});

const OTHER_RULE = { id: 'batchWindow', objective: '^core\\b', claim: 'the change runs in the batch window',
  terms: ['\\bbatch\\b[^.]{0,40}\\bwindow\\b'], reason: 'The batch window is part of the change.' };

test('with two evidence rules only the one whose terms the quote holds applies', async () => {
  const both = { evidence: { stageClosure: { holds: true, quote: SENTENCE.toLowerCase() },
    batchWindow: { holds: true, quote: SENTENCE } } };
  const run = await runPhase5(`Short Description: ${SENTENCE}`, [], both, undefined, undefined,
    { evidence: [EVIDENCE_RULE, OTHER_RULE] });
  assert.equal(run.row.applicable, true);
  assert.match(run.logged.join('\n'), /evidence batchWindow was rejected: quote lacks the terms/);
  const asked = run.model.calls.find((c) => c.schemaName.startsWith('phase5'));
  assert.ok(asked.schema.properties.evidence);
});

test('an evidence rule whose objective pattern matches nothing is logged and skipped', async () => {
  const none = { ...EVIDENCE_RULE, objective: '^no such objective$' };
  const { row, logged } = await runPhase5(`Short Description: ${SENTENCE}`, [], claim(SENTENCE),
    undefined, undefined, { evidence: [none] });
  assert.equal(row.applicable, false);
  assert.match(logged.join('\n'), /evidence stageClosure names no objective/);
});

test('evidence never turns an applicable objective off, and keeps its reason', async () => {
  const model = fakeModel({ phase5: (value) => {
    for (const row of Object.values(value.objectives)) { row.applicable = true; row.reason = 'The model\'s reason.'; }
    return { ...value, ...claim(SENTENCE) };
  } });
  const ctx = { pack: { rules: [], executiveSummary: {} }, ref: { core: [], chapters: () => [] },
    job: {}, builder: { OBJECTIVES: ['Core Change Validation', 'Integration Testing'] },
    coreObjective: 'Core Change Validation', description: `Short Description: ${SENTENCE}`, model, calls: 0,
    tokens: { prompt: 0, output: 0 },
    config: { model: { context: 100000, reasoningOutput: 100, maxOutput: 100 }, objectiveEvidence: [EVIDENCE_RULE] },
    logs: { detail() {}, status() {}, call() {} }, private() {} };
  await phase5(ctx);
  assert.ok(ctx.pack.objectives.every((row) => row.applicable && row.reason === 'The model\'s reason.'));
});

test('a suite pack asks for no evidence', async () => {
  const { model } = await runPhase5(SENTENCE, [], {}, undefined, undefined, { suite: true });
  const asked = model.calls.find((c) => c.schemaName.startsWith('phase5'));
  assert.equal(asked.schema.properties.evidence, undefined);
});

test('an objective list without Integration Testing is unaffected by a valid claim', async () => {
  const { row } = await runPhase5(SENTENCE, [], claim(SENTENCE), ['Core Change Validation', 'BREAK IT']);
  assert.equal(row, undefined);
});

test('a long description keeps its own Word: lines and ends at the next ALM field', () => {
  const record = ['**Short Description**: Short text', '**Long Description:**', 'Steps to reproduce:',
    '1. Click OK: nothing happens', 'Expected Result: a save', 'Actual Result: none', 'Note: see log',
    '**Status**: Open', 'Comments:', 'Not part of it.'].join('\n');
  const text = almDescriptions(record);
  assert.match(text, /^Short text\n\nSteps to reproduce:/);
  assert.match(text, /Actual Result: none\nNote: see log$/);
  assert.ok(!/Open|Not part/.test(text));
});


test('only counts of rules or cards are checked, and dotted rule IDs and business rules are caught', () => {
  const rules = ['BR-LIB.UC01-001', 'BR-LIB.UC01-002'].map((id) => ({ id, sourceDocument: 'D', module: 'M',
    impact: 'Direct Change', risk: 'Low', summary: 's' }));
  const keep = (assumption) => ({ assumption, why: 'w', impact: 'i', clarification: 'c' });
  const logged = [];
  const pack = { rules, testCards: [], coverage: [], assumptions: [
    keep('Each card covers 1 rule.'), keep('Steps 1 to 3 cards are shared.'), keep('Section 5 rules apply.'),
    keep('In 2026 rules changed.'), keep('The 2 business rules are read.'),
    keep('The 40 business rules are read.'), keep('All 12 BRs are read.'),
    keep('BR-LIB.UC01-099 is read.'), keep('BR-LIB.UC01-002 is read.')] };
  assert.equal(dropUnfoundedAssumptions({ logs: { detail: (label, text) => logged.push(text) } }, pack), 3);
  assert.deepEqual(logged, ['The 40 business rules are read.', 'All 12 BRs are read.', 'BR-LIB.UC01-099 is read.']);
  assert.equal(pack.assumptions.length, 6);
});

test('CAMP Designs counts only as a folder, and only a CAMP design in the descriptions makes it missing', () => {
  const named = { name: 'CAMP Designs.doc', text: provenance(['- Source: `CAMP Designs.doc`',
    '- SharePoint: [x](<host>/sites/x/Other/CAMP%20Designs.doc?web=1)', '- Revised: 2026-01-01, x']) };
  assert.equal(documentInputs([named], '').received.length, 0);
  const other = { name: 'Other', text: provenance(['- Source: `Other.doc`', '- Revised: 2026-01-01, x']) };
  assert.deepEqual(documentInputs([other], 'Short Description: x\nStatus: CAMP only here').missing, []);
  assert.equal(documentInputs([other], 'Short Description: Update the CAMP design.').missing.length, 2);
});

test('an INSUFFICIENT INPUTS partial pack names what code found missing', async () => {
  const config = fixtureConfig();
  const result = await runJob(config, { issue: '999' }, { model: fakeModel(), echo: false });
  assert.equal(result.reason, 'gate:missing-inputs');
  const pack = JSON.parse(read(path.join(result.outDir, 'work', 'partial-pack.json')));
  assert.equal(pack.intake.readiness, 'INSUFFICIENT INPUTS');
  assert.ok(pack.intake.missing.includes('Description of the defect or change.'));
});

test('common words in a long description do not end it, and a bold Status does', () => {
  const plain = 'Long Description:\n1. Open the form\nName: Smith\n2. Save\nType: Rail\n3. Expect error\n'
    + 'Status: Open\nPriority: High\nComments: x';
  assert.equal(almDescriptions(plain), '1. Open the form\nName: Smith\n2. Save\nType: Rail\n3. Expect error\nStatus: Open');
  assert.equal(almDescriptions('Short Description: x\nSummary: the save fails'), 'x\nSummary: the save fails');
  const bold = '**Long Description**: a\nName: Smith\n**Status**: Open\nb';
  assert.equal(almDescriptions(bold), 'a\nName: Smith');
});

test('a number is skipped only as a section, step, page, range end or year', () => {
  const rules = ['BR-A-001', 'BR-A-002'].map((id) => ({ id, sourceDocument: 'D', module: 'M',
    impact: 'Direct Change', risk: 'Low', summary: 's' }));
  const keep = (assumption) => ({ assumption, why: 'w', impact: 'i', clarification: 'c' });
  const pack = { rules, testCards: [], coverage: [], assumptions: [
    keep('The checks apply to 40 rules.'), keep('Covered in 12 rules.'), keep('From 40 rules, 2 apply.'),
    keep('Rules 3 to 40 rules apply.'), keep('See page 9 rules.'), keep('Since 2026 rules changed.')] };
  dropUnfoundedAssumptions({}, pack);
  assert.deepEqual(pack.assumptions.map((a) => a.assumption),
    ['Rules 3 to 40 rules apply.', 'See page 9 rules.', 'Since 2026 rules changed.']);
});

test('intake names a document outside the root or not a file, and check reports it', async () => {
  const config = fixtureConfig();
  const outside = path.relative(FIXTURES, path.join(FIXTURES, '..', 'phases.mjs')).split(path.sep).join('/');
  const result = await runJob(config, { issue: '501', change: '7001', docs: [outside, 'docs/LIB'] },
    { model: fakeModel(), echo: false });
  const pack = JSON.parse(read(path.join(result.outDir, 'work', 'partial-pack.json')));
  assert.deepEqual(pack.intake.missing, ['Source documents.', `Document file is outside the repository: ${outside}.`,
    'Document path is not a file: docs/LIB.']);
  const checked = spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'check',
    '--config', path.join(FIXTURES, 'pipeline.json'), '--issue', '501', '--doc', outside],
  { encoding: 'utf8' });
  assert.equal(checked.status, 1);
  assert.match(checked.stdout, /document-1  missing  document-file/);
});

test('missing inputs read as sentences, name the missing file and list it once', async () => {
  const config = fixtureConfig();
  const result = await runJob(config, { issue: '501', change: '7001',
    docs: ['docs/LIB/gone-1.md', 'docs/LIB/gone-2.md'] }, { model: fakeModel(), echo: false });
  const pack = JSON.parse(read(path.join(result.outDir, 'work', 'partial-pack.json')));
  const files = pack.intake.missing.filter((t) => t.startsWith('Document file not found'));
  assert.deepEqual(files, ['Document file not found: docs/LIB/gone-1.md.',
    'Document file not found: docs/LIB/gone-2.md.']);
  assert.match(pack.limitations['Job Intake'], /gone-1\.md\. Document file not found: docs\/LIB\/gone-2\.md\./);
});

test('an escaped bracket in a file name does not hide the CAMP Designs folder', () => {
  const doc = { name: 'A', text: provenance(['- Source: `A [v2](old).doc`',
    '- SharePoint: [A \\[v2\\](old).doc](<host>/sites/x/CAMP%20Designs/A.doc?web=1)', '- Revised: 2026-01-01, x']) };
  assert.equal(documentInputs([doc], '').received.length, 2);
});

test('the label style comes from the label that opened the current field', () => {
  assert.equal(almDescriptions('Short Description: x\n**Long Description**: a\n**Status**: Open\nb'), 'x\n\na');
  assert.equal(almDescriptions('**Short Description**: x\nLong Description: a\n**Status**: Open\nb'),
    'x\n\na\n**Status**: Open\nb');
  assert.equal(almDescriptions('**Long Description**\nShort Description: x\n**Status**: Open\ny'),
    'x\n**Status**: Open\ny');
});

test('a range with and keeps its number, a list of counts does not', () => {
  const rules = ['BR-A-001', 'BR-A-002'].map((id) => ({ id, sourceDocument: 'D', module: 'M',
    impact: 'Direct Change', risk: 'Low', summary: 's' }));
  const keep = (assumption) => ({ assumption, why: 'w', impact: 'i', clarification: 'c' });
  const pack = { rules, testCards: [], coverage: [], assumptions: [
    keep('Between 2 and 40 rules apply.'), keep('2 rules and 40 rules apply.')] };
  dropUnfoundedAssumptions({}, pack);
  assert.deepEqual(pack.assumptions.map((a) => a.assumption), ['Between 2 and 40 rules apply.']);
  const other = { ...pack, assumptions: ['BR-A-001 and 40 rules apply.', 'Section 4 and 40 rules apply.',
    'In 2025 and 40 rules apply.', 'Version 3 and 40 rules apply.'].map(keep) };
  assert.equal(dropUnfoundedAssumptions({}, other), 4);
});

test('the model defaults to a 128000-token context', () => {
  const { model } = fixtureConfig();
  assert.equal(model.context, 128000);
});

const LOADED = (extra = {}) => ({ all_models_loaded: [{ model_name: 'm a/b',
  backend_url: 'http://127.0.0.1:8001/v1', recipe_options: { ctx_size: 65536 }, ...extra }] });
const NOT_LOADED = { all_models_loaded: [] };
const windowClient = (routes, urls = []) => modelClient({ endpoint: 'http://localhost:13305/api/v1',
  name: 'm a/b', fetchImpl: async (url, options = {}) => {
    urls.push({ url: String(url), method: options.method ?? 'GET' });
    const hit = Object.entries(routes).find(([suffix]) => String(url).endsWith(suffix));
    if (!hit || hit[1] === 'throw') throw new Error('unreachable');
    const { status = 200, body = hit[1] } = typeof hit[1]?.status === 'number' ? hit[1] : {};
    return { ok: status >= 200 && status < 300, status, json: async () => body };
  } });

test('the context window comes from the backend, the loaded entry, or the saved options', async () => {
  assert.deepEqual(await windowClient({ '/health': LOADED(), '/props': 'throw' }).contextWindow(), { size: 65536, guess: false });
  const props = { default_generation_settings: { n_ctx: 32768 } };
  assert.deepEqual(await windowClient({ '/health': LOADED(), '/props': props }).contextWindow(), { size: 32768, guess: false });
  const saved = windowClient({ '/health': NOT_LOADED,
    '/models/m%20a%2Fb': { recipe_options: { ctx_size: 49152 } } });
  assert.deepEqual(await saved.contextWindow(), { size: 49152, guess: false });
});

test('the context window is null when nothing can be read', async () => {
  assert.equal(await windowClient({}).contextWindow(), null);
  assert.equal(await windowClient({ '/health': NOT_LOADED, '/models/m%20a%2Fb': {} }).contextWindow(), null);
});

const SAVED_SIZE = (size) => ({ recipe_options: { ctx_size: size } });

test('a failed health check reads the saved window as a guess', async () => {
  const client = windowClient({ '/health': 'throw', '/models/m%20a%2Fb': SAVED_SIZE(65536) });
  assert.deepEqual(await client.contextWindow(), { size: 65536, guess: true });
});

test('a health check that answers with an error or no loaded list gives a guess', async () => {
  const saved = { '/models/m%20a%2Fb': SAVED_SIZE(65536) };
  const busy = windowClient({ '/health': { status: 500, body: { error: 'busy' } }, ...saved });
  assert.deepEqual(await busy.contextWindow(), { size: 65536, guess: true });
  const noList = windowClient({ '/health': {}, ...saved });
  assert.deepEqual(await noList.contextWindow(), { size: 65536, guess: true });
  // The same body with a loaded model listed would be read as sure.
  const body = { status: 500, body: LOADED() };
  assert.deepEqual(await windowClient({ '/health': body, '/props': 'throw', ...saved }).contextWindow(),
    { size: 65536, guess: true });
});

test('a guess lowers the window but never raises a smaller one', async () => {
  const { readWindow } = await import('./phases.mjs');
  const config = fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    context: 128000, maxOutput: 500, reasoningOutput: 500 } });
  const run = async (health, saved, window) => {
    const ctx = { config, job: { id: 'j' }, logs: { status() {}, detail() {}, call() {} }, window,
      model: windowClient({ '/health': health, '/models/m%20a%2Fb': SAVED_SIZE(saved) }) };
    await readWindow(ctx, 'p');
    return ctx.window;
  };
  assert.equal(await run('throw', 65536, undefined), 65536);
  assert.equal(await run('throw', 128000, 32768), 32768);
  assert.equal(await run({ status: 500, body: { error: 'busy' } }, 65536, undefined), 65536);
  assert.equal(await run({ status: 500, body: { error: 'busy' } }, 128000, 32768), 32768);
  assert.equal(await run({}, 65536, undefined), 65536);
  assert.equal(await run({}, 128000, 32768), 32768);
});

test('the fallback window is per slot', async () => {
  const size = async (args) => (await windowClient({ '/health': LOADED({ recipe_options:
    { ctx_size: 131072, ...(args === undefined ? {} : { llamacpp_args: args }) } }), '/props': 'throw' })
    .contextWindow()).size;
  assert.equal(await size('--jinja -np 2'), 65536);
  assert.equal(await size('--parallel 4 --jinja'), 32768);
  assert.equal(await size('--jinja'), 131072);
  assert.equal(await size('--jinja -np 2 -fa on --cache-type-k q8_0 --cache-type-v q8_0'), 65536);
  assert.equal(await size(undefined), 131072);
  assert.equal(await size('-np x'), 131072);
  const saved = windowClient({ '/health': NOT_LOADED, '/models/m%20a%2Fb':
    { recipe_options: { ctx_size: 131072, llamacpp_args: '-np 2' } } });
  assert.deepEqual(await saved.contextWindow(), { size: 65536, guess: false });
});

const windowReader = async (config, reads) => {
  const { readWindow } = await import('./phases.mjs');
  const warns = [];
  const ctx = { config, job: { id: 'j' }, model: { contextWindow: async () => reads.shift() },
    logs: { status: (fields) => { if (fields.event === 'warn') warns.push(fields); }, detail() {} } };
  return { ctx, warns, read: () => readWindow(ctx, 'p') };
};

test('a sure size after a guess raises the window back', async () => {
  const config = fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    context: 128000, maxOutput: 500, reasoningOutput: 500 } });
  const { ctx, read } = await windowReader(config,
    [{ size: 32768, guess: true }, { size: 65536, guess: false }]);
  await read();
  assert.equal(ctx.window, 32768);
  await read();
  assert.equal(ctx.window, 65536);
});

test('a guess too small never fails a job, but a sure size that small does', async () => {
  const config = fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    context: 20000, maxOutput: 500, reasoningOutput: 500 } });
  const { ctx, warns, read } = await windowReader(config,
    [{ size: 7000, guess: false }, { size: 2800, guess: true }, { size: 2800, guess: true }]);
  await read();
  await read();
  await read();
  assert.equal(ctx.window, 7000);
  assert.deepEqual(warns.map((w) => w.reason), ['server-window', 'server-window-unknown']);
  const first = await windowReader(config, [{ size: 2800, guess: true }]);
  await first.read();
  assert.equal(first.ctx.window, 20000);
  const sure = await windowReader(config, [{ size: 2800, guess: false }]);
  await assert.rejects(sure.read(),
    (error) => error instanceof ModelError && error.code === 'window-too-small');
});

test('a guess is logged only when it lowers the window, and carries the guess marker', async () => {
  const config = fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    context: 20000, maxOutput: 500, reasoningOutput: 500 } });
  const same = await windowReader(config, [{ size: 9000, guess: false }, { size: 12000, guess: true }]);
  await same.read();
  await same.read();
  assert.equal(same.warns.filter((w) => w.reason === 'server-window').length, 1);
  assert.equal(same.warns[0].guess, undefined);
  const lower = await windowReader(config, [{ size: 9000, guess: false }, { size: 8000, guess: true }]);
  await lower.read();
  await lower.read();
  assert.equal(lower.ctx.window, 8000);
  assert.equal(lower.warns[1].reason, 'server-window');
  assert.equal(lower.warns[1].guess, true);
});

test('a loaded entry with no backend and no options reads no saved window', async () => {
  const urls = [];
  const client = windowClient({ '/health': { all_models_loaded: [{ model_name: 'm a/b' }] },
    '/models/m%20a%2Fb': { recipe_options: { ctx_size: 128000 } } }, urls);
  assert.equal(await client.contextWindow(), null);
  assert.ok(!urls.some(({ url }) => url.includes('/models/')), 'the saved route was requested');
});

test('reading the context window calls only loopback addresses, and only with GET', async () => {
  const urls = [];
  await windowClient({ '/health': LOADED(), '/props': 'throw' }, urls).contextWindow();
  await windowClient({ '/health': NOT_LOADED, '/models/m%20a%2Fb': {} }, urls).contextWindow();
  assert.ok(urls.some(({ url }) => url.endsWith('/props')));
  assert.ok(urls.some(({ url }) => url.endsWith('/models/m%20a%2Fb')));
  for (const { url, method } of urls) {
    assert.ok(/^http:\/\/(localhost:13305|127\.0\.0\.1:8001)\//.test(url), url);
    assert.equal(method, 'GET');
  }
});

test('a server window smaller than the config is the budget, and is warned about once', async () => {
  const { ask } = await import('./phases.mjs');
  const config = fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    context: 20000, maxOutput: 500, reasoningOutput: 500 } });
  const warns = [];
  const ctx = { config, calls: 0, tokens: { prompt: 0, output: 0 }, job: { id: 'j' },
    logs: { status: (fields) => { if (fields.event === 'warn') warns.push(fields); }, detail() {} },
    model: { ...fakeModel(), contextWindow: async () => ({ size: 7000, guess: false }) } };
  const options = { phase: 'phase1', step: 's', reasoning: false, inputs: [['Doc', 'x'.repeat(30000)]],
    schema: { type: 'object' }, task: 't' };
  // About 10,000 tokens: fits 20000, not 7000.
  for (let i = 0; i < 2; i += 1) {
    await assert.rejects(ask(ctx, options), (error) => error instanceof ModelError && error.code === 'too-big');
  }
  assert.deepEqual(warns.map(({ reason, context, serverContext }) => ({ reason, context, serverContext })),
    [{ reason: 'server-window', context: 20000, serverContext: 7000 }]);
});

test('a server window with no room for a prompt fails the job', async () => {
  const config = fixtureConfig();
  const model = { ...fakeModel(), contextWindow: async () => ({ size: 1000, guess: false }) };
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'model:window-too-small');
});

test('an unreadable server window falls back to the config and is warned about once', async () => {
  const config = fixtureConfig();
  const model = { ...fakeModel(), contextWindow: async () => null };
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const warns = statusLines(result.outDir).filter((l) => l.reason === 'server-window-unknown');
  assert.equal(warns.length, 1);
});

test('a server window just above the reply and reserve but with no input room fails the job', async () => {
  // 2800 clears the reasoning reply, the 2048 reserve and the system text, with
  // almost nothing left for a document.
  const config = fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    context: 20000, maxOutput: 500, reasoningOutput: 500 } });
  const model = { ...fakeModel(), contextWindow: async () => ({ size: 2800, guess: false }) };
  const { readWindow } = await import('./phases.mjs');
  const ctx = { config, job: { id: 'j' }, model, logs: { status() {}, detail() {}, call() {} } };
  await assert.rejects(readWindow(ctx, 'intake'),
    (error) => error instanceof ModelError && error.code === 'window-too-small');
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'model:window-too-small');
});

test('splitText with no token budget is a window-too-small error', () => {
  for (const tokens of [0, -1, -500]) {
    assert.throws(() => splitText('some text', tokens),
      (error) => error instanceof ModelError && error.code === 'window-too-small');
  }
});

test('an unreadable window after a known smaller one keeps the smaller one', async () => {
  const { readWindow } = await import('./phases.mjs');
  const config = fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    context: 20000, maxOutput: 500, reasoningOutput: 500 } });
  const sizes = [{ size: 7000, guess: false }, null, null];
  const warns = [];
  const ctx = { config, job: { id: 'j' }, model: { contextWindow: async () => sizes.shift() },
    logs: { status: (fields) => { if (fields.event === 'warn') warns.push(fields.reason); }, detail() {} } };
  await readWindow(ctx, 'phase1');
  await readWindow(ctx, 'phase1');
  await readWindow(ctx, 'phase1');
  assert.equal(ctx.window, 7000);
  assert.deepEqual(warns, ['server-window', 'server-window-unknown']);
});

test('the context window is read afresh on every call', async () => {
  const routes = { '/health': LOADED({ recipe_options: { ctx_size: 65536 } }), '/props': 'throw' };
  const client = windowClient(routes);
  assert.deepEqual(await client.contextWindow(), { size: 65536, guess: false });
  routes['/health'] = LOADED({ recipe_options: { ctx_size: 32768 } });
  assert.deepEqual(await client.contextWindow(), { size: 32768, guess: false });
});

test('the loaded entry whose model_name matches is the one used', async () => {
  const other = { model_name: 'other', backend_url: 'http://127.0.0.1:8002/v1',
    recipe_options: { ctx_size: 1111 } };
  const health = { all_models_loaded: [other, ...LOADED().all_models_loaded] };
  assert.deepEqual(await windowClient({ '/health': health, '/props': 'throw' }).contextWindow(), { size: 65536, guess: false });
  const reversed = { all_models_loaded: [...LOADED().all_models_loaded, other] };
  assert.deepEqual(await windowClient({ '/health': reversed, '/props': 'throw' }).contextWindow(), { size: 65536, guess: false });
});

test('a loaded model with no readable size does not fall back to the saved options', async () => {
  const urls = [];
  const client = windowClient({ '/health': LOADED({ recipe_options: {} }), '/props': 'throw',
    '/models/m%20a%2Fb': { recipe_options: { ctx_size: 128000 } } }, urls);
  assert.equal(await client.contextWindow(), null);
  assert.ok(!urls.some(({ url }) => url.endsWith('/models/m%20a%2Fb')));
});

test('the floor uses the larger reply, so a window only that floor rejects fails', async () => {
  const { readWindow } = await import('./phases.mjs');
  const accepts = async (cfg, size) => {
    try {
      await readWindow({ config: cfg, job: { id: 'j' }, model: { contextWindow: async () => ({ size, guess: false }) },
        logs: { status() {}, detail() {}, call() {} } }, 'p');
      return true;
    } catch (error) {
      if (error instanceof ModelError && error.code === 'window-too-small') return false;
      throw error;
    }
  };
  const model = (maxOutput) => fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    context: 20000, maxOutput, reasoningOutput: 500 } });
  // The smallest window that leaves input room when the reasoning reply is the only reserve.
  let least = 3000;
  while (!await accepts(model(500), least)) least += 1;
  // A larger plain reply raises the floor, so a window just above `least` is refused.
  assert.equal(await accepts(model(3000), least + 100), false);
  assert.equal(await accepts(model(3000), least + 3000), true);
});

test('room reserves the widest reply a thinking call may ask for, so a prompt sized to it passes ask', async () => {
  const { ask, room } = await import('./phases.mjs');
  const config = fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    context: 60000, maxOutput: 16384, reasoningOutput: 8192 } });
  const ctx = { config, calls: 0, tokens: { prompt: 0, output: 0 }, job: { id: 'j' },
    logs: { status() {}, detail() {}, call() {} },
    model: { json: async () => ({ value: {}, usage: { promptTokens: 1, outputTokens: 1, ms: 1 } }),
      // A prompt that uses all the room, plus the reference text already counted in it.
      countTokens: async () => room(ctx, true, []) + 100 } };
  assert.deepEqual(await ask(ctx, { phase: 'phase3', step: 's', reasoning: true, inputs: [],
    schema: { type: 'object' }, task: 't' }), {});
});

test('a window that is zero, negative, fractional or text falls through to the next source', async () => {
  for (const bad of [0, -4096, 4096.5, '4096']) {
    const props = { default_generation_settings: { n_ctx: bad } };
    assert.deepEqual(await windowClient({ '/health': LOADED(), '/props': props }).contextWindow(), { size: 65536, guess: false },
      `props ${JSON.stringify(bad)}`);
    const saved = windowClient({ '/health': LOADED({ recipe_options: { ctx_size: bad } }), '/props': props,
      '/models/m%20a%2Fb': { recipe_options: { ctx_size: 49152 } } });
    assert.equal(await saved.contextWindow(), null, `loaded ${JSON.stringify(bad)}`);
    assert.equal(await windowClient({ '/health': NOT_LOADED,
      '/models/m%20a%2Fb': { recipe_options: { ctx_size: bad } } }).contextWindow(), null);
  }
});

const MEMINFO = (availableKiB, swapTotalKiB, swapFreeKiB) => `MemTotal:       65536000 kB
MemAvailable:   ${availableKiB} kB
SwapTotal:      ${swapTotalKiB} kB
SwapFree:       ${swapFreeKiB} kB
`;
const LIMITS = { minAvailableMiB: 3072, maxSwapPercent: 85, pollSeconds: 30, waitMinutes: 20 };
const reading = (availableMiB, swapPercent) => ({ availableMiB, swapPercent });

test('meminfo gives available memory and swap use, and no swap is zero percent', () => {
  assert.deepEqual(parseMeminfo(MEMINFO(4194304, 10485760, 2097152)),
    { availableMiB: 4096, swapTotalMiB: 10240, swapUsedMiB: 8192, swapPercent: 80 });
  assert.equal(parseMeminfo(MEMINFO(2048, 0, 0)).swapPercent, 0);
  assert.equal(parseMeminfo('not meminfo'), null);
});

test('memory is low under the floor or over the swap ceiling, and not at either limit', () => {
  assert.equal(memoryLow(reading(3071, 0), LIMITS), true);
  assert.equal(memoryLow(reading(3072, 85), LIMITS), false);
  // Full swap counts only while free memory is under twice the floor.
  assert.equal(memoryLow(reading(5000, 86), LIMITS), true);
  assert.equal(memoryLow(reading(6144, 99), LIMITS), false);
  assert.equal(memoryLow(reading(5000, 100), { ...LIMITS, maxSwapPercent: 100 }), false);
});

test('waiting for memory polls until it recovers, gives up after the wait, and stops at once at 0 minutes', async () => {
  let t = 0;
  const clock = { now: () => t, sleep: async (ms) => { t += ms; } };
  const run = (readings, limits = LIMITS) => {
    const list = [...readings];
    const waits = [];
    return waitForMemory(limits, { ...clock, read: () => (list.length > 1 ? list.shift() : list[0]),
      onWait: (m) => waits.push(m) }).then((outcome) => ({ outcome, waits }));
  };
  let { outcome, waits } = await run([reading(8000, 10)]);
  assert.deepEqual([outcome.ok, outcome.polls, waits.length], [true, 0, 0]);
  ({ outcome, waits } = await run([reading(1000, 10), reading(2000, 10), reading(5000, 10)]));
  assert.deepEqual([outcome.ok, outcome.polls, waits.length], [true, 2, 1]);
  t = 0;
  ({ outcome } = await run([reading(1000, 90)]));
  assert.deepEqual([outcome.ok, outcome.polls, outcome.waitedMs], [false, 40, 1200000]);
  // A poll longer than the wait sleeps only the time left.
  t = 0;
  ({ outcome } = await run([reading(1000, 90)], { ...LIMITS, waitMinutes: 1, pollSeconds: 90 }));
  assert.deepEqual([outcome.ok, outcome.waitedMs], [false, 60000]);
  ({ outcome } = await run([reading(1000, 90)], { ...LIMITS, waitMinutes: 0 }));
  assert.deepEqual([outcome.ok, outcome.polls], [false, 0]);
  assert.equal((await waitForMemory(LIMITS, { read: () => null })).unreadable, true);
});

test('the memory block has defaults and rejects values it cannot use', () => {
  const config = fixtureConfig({ memory: undefined });
  assert.deepEqual(config.memory, { enabled: true, ...LIMITS });
  for (const bad of ['text', [], { minAvailableMB: 6000 }]) {
    assert.throws(() => fixtureConfig({ memory: bad }), /config memory must be an object/, JSON.stringify(bad));
  }
  for (const bad of [{ enabled: 'yes' }, { minAvailableMiB: 0 }, { minAvailableMiB: 1.5 },
    { maxSwapPercent: 101 }, { pollSeconds: 0 }, { waitMinutes: -1 }, { waitMinutes: 1.5 }]) {
    assert.throws(() => fixtureConfig({ memory: bad }), /config memory\./, JSON.stringify(bad));
  }
});

test('low memory stops a job before a phase at its checkpoint, and a resume carries on from there', async () => {
  const config = fixtureConfig({ memory: { enabled: true, waitMinutes: 1, pollSeconds: 30 } });
  const job = { issue: '501', change: '7001' };
  let low = false;
  const model = fakeModel({ intake: (value) => ({ ...value, description: 'Card renewal sets the expiry from the old date' }) });
  let t = Date.now();
  const readMemory = () => (low ? parseMeminfo(MEMINFO(1048576, 10485760, 1048576))
    : parseMeminfo(MEMINFO(8388608, 10485760, 9437184)));
  // Memory drops once phase 2 has passed.
  const result = await runJob(config, job, { model, echo: false, now: () => t,
    readMemory: () => { if (statusSeen(config, job, 'phase2', 'pass')) low = true; return readMemory(); },
    sleep: async (ms) => { t += ms; } });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'memory:low');
  assert.equal(result.phase, 'phase3');
  const checkpoint = JSON.parse(read(path.join(result.outDir, 'work', 'checkpoint.json')));
  assert.equal(checkpoint.phase, 'phase2');
  const lines = statusLines(result.outDir);
  assert.ok(lines.some((l) => l.event === 'wait' && l.reason === 'memory-low' && l.availableMiB === 1024));
  const last = lines.at(-1);
  assert.deepEqual([last.event, last.reason, last.polls], ['fail', 'memory:low', 2]);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
  low = false;
  const again = await runJob(config, { ...job, resume: true }, { model, echo: false, readMemory });
  assert.equal(again.ok, true);
  assert.ok(statusLines(again.outDir).some((l) => l.event === 'resume' && l.after === 'phase2'));
});

/** A run that stops for low memory before intake passes, so it leaves no checkpoint. */
async function stopBeforeIntake(config, job, model) {
  let t = Date.now();
  const result = await runJob(config, job, { model, echo: false, now: () => t,
    readMemory: () => parseMeminfo(MEMINFO(1048576, 10485760, 1048576)),
    sleep: async (ms) => { t += ms; } });
  assert.equal(result.reason, 'memory:low');
  assert.equal(result.phase, 'intake');
  assert.equal(fs.existsSync(path.join(result.outDir, 'work', 'checkpoint.json')), false);
  return result;
}

test('a resume after a low-memory stop before intake keeps the status log', async () => {
  const config = fixtureConfig({ memory: { enabled: true, waitMinutes: 1, pollSeconds: 30 } });
  const job = { issue: '501', change: '7001' };
  const model = fakeModel({ intake: (value) => ({ ...value, description: 'Card renewal sets the expiry from the old date' }) });
  const first = await stopBeforeIntake(config, job, model);
  const before = statusLines(first.outDir);
  assert.ok(before.some((l) => l.event === 'wait' && l.reason === 'memory-low'));
  // The release line a finished job gets after the stop does not hide the stop.
  jobLogs(first.outDir, { echo: false }).status({ job: first.id, phase: 'release', event: 'pass' });
  const withRelease = statusLines(first.outDir);
  const again = await runJob(config, { ...job, resume: true }, { model, echo: false,
    readMemory: () => parseMeminfo(MEMINFO(8388608, 10485760, 9437184)) });
  assert.equal(again.ok, true);
  const lines = statusLines(again.outDir);
  assert.deepEqual(lines.slice(0, withRelease.length), withRelease);
  assert.ok(lines.length > withRelease.length);
  assert.deepEqual([lines.at(-1).phase, lines.at(-1).event], ['done', 'pass']);
  assertContentFree(read(path.join(again.outDir, 'status.log')));
});

test('a run started over for any other reason starts with an empty status log', async () => {
  const config = fixtureConfig({ memory: { enabled: true, waitMinutes: 1, pollSeconds: 30 } });
  const job = { issue: '501', change: '7001' };
  const model = fakeModel({ intake: (value) => ({ ...value, description: 'Card renewal sets the expiry from the old date' }) });
  const memory = () => parseMeminfo(MEMINFO(8388608, 10485760, 9437184));
  // The same stop, run again without resume.
  const first = await stopBeforeIntake(config, job, model);
  const fresh = await runJob(config, job, { model, echo: false, readMemory: memory });
  assert.equal(fresh.ok, true);
  assert.equal(statusLines(fresh.outDir).some((l) => l.event === 'wait'), false);
  // A resume with no checkpoint whose last stop was something else.
  fs.rmSync(path.join(first.outDir, 'work', 'checkpoint.json'));
  const log = jobLogs(first.outDir, { echo: false });
  log.status({ job: first.id, phase: 'intake', event: 'fail', reason: 'gate:old-failure', ms: 1 });
  const resumed = await runJob(config, { ...job, resume: true }, { model, echo: false, readMemory: memory });
  assert.equal(resumed.ok, true);
  assert.equal(statusLines(resumed.outDir).some((l) => l.reason === 'gate:old-failure'), false);
});

test('an unreadable /proc/meminfo is noted once and the job carries on', async () => {
  const config = fixtureConfig({ memory: { enabled: true } });
  const model = fakeModel({ intake: (value) => ({ ...value, description: 'Card renewal sets the expiry from the old date' }) });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false, readMemory: () => null });
  assert.equal(result.ok, true);
  assert.equal(statusLines(result.outDir).filter((l) => l.reason === 'meminfo-unreadable').length, 1);
});

test('a stop for low memory is not one of the job\'s tries, and the drain stops after it', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501', now: true });
  addJob(config, { issue: '777', now: true });
  const ran = [];
  const run = async (_config, job) => {
    ran.push(job.id);
    return { ok: false, phase: 'phase3', reason: 'memory:low', ms: 1000 };
  };
  const night = (day) => () => new Date(`2026-10-${day}T22:00:00`);
  for (const day of [27, 28]) await drainQueue(config, { cutoff: '07:00', run, clock: night(day) });
  // Two stops, one job each night: neither drops anything, and the second job never runs.
  assert.deepEqual(ran, ['issue-501', 'issue-501']);
  const rows = readQueue(config).jobs;
  assert.deepEqual(rows.map((r) => r.status), ['queued', 'queued']);
  assert.equal(rows[0].failures.length, 2);
  assert.equal(countedTries(rows[0].failures), 0);
  assert.equal(countedTries([...rows[0].failures, { reason: 'model:no-reply' }]), 1);
  assert.match(summaryLines(readQueue(config))[0], /retry after stopping at phase3 \(memory:low\)/);
});

test('the third low-memory stop in a row drops the job, and the next job runs the night after', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501', now: true });
  addJob(config, { issue: '777', now: true });
  const ran = [];
  const run = async (_config, job) => {
    ran.push(job.id);
    return { ok: false, phase: 'phase3', reason: 'memory:low', ms: 1000 };
  };
  const night = (day) => () => new Date(`2026-10-${day}T22:00:00`);
  for (const day of [27, 28, 29, 30]) await drainQueue(config, { cutoff: '07:00', run, clock: night(day) });
  assert.deepEqual(ran, ['issue-501', 'issue-501', 'issue-501', 'issue-777']);
  const rows = readQueue(config).jobs;
  assert.deepEqual(rows.map((r) => r.status), ['failed', 'queued']);
  assert.equal(rows[0].reason, 'memory:low');
  assert.equal(memoryStops(rows[0].failures), MAX_MEMORY_STOPS);
  assert.match(summaryLines(readQueue(config))[0], /dropped after 3 low-memory stops in a row/);
  // A person puts it back with queue add, which starts it with no failures.
  addJob(config, { issue: '501', now: true });
  const again = readQueue(config).jobs.filter((r) => r.id === 'issue-501');
  assert.deepEqual(again.map((r) => r.status), ['failed', 'queued']);
  assert.equal(again[1].failures, undefined);
});

test('a failure of another kind between low-memory stops resets the count', () => {
  const stop = { reason: 'memory:low' };
  assert.equal(memoryStops([stop, stop, { reason: 'model:no-reply' }, stop]), 1);
  assert.equal(memoryStops([{ reason: 'model:no-reply' }, stop, stop]), 2);
  assert.equal(memoryStops([]), 0);
  assert.equal(memoryStops(undefined), 0);
});

test('the report shows a job held by repeated low-memory stops as needing a person', () => {
  const config = fixtureConfig();
  const queue = reportQueue(config);
  const stops = (n) => Array.from({ length: n }, (_, i) => ({ at: hoursAgo(5 - i), phase: 'phase3', reason: 'memory:low', ms: 1 }));
  queue.jobs.push({ id: 'issue-910', status: 'failed', finished: hoursAgo(2), phase: 'phase3',
    reason: 'memory:low', failures: stops(3) });
  queue.jobs.push({ id: 'issue-920', status: 'queued', failures: stops(1) });
  const data = reportData(config, queue, { period: 'day', now: NOW, random: seededRandom(1) });
  const state = (id) => data.jobs.find((j) => j.id === id)?.state;
  assert.equal(state('issue-910'), 'MEMORY');
  assert.equal(state('issue-920'), 'RETRY');
  assert.equal(data.counts.memory, 1);
  const text = renderReport(data);
  assert.match(text, /Stopped 3 times in a row for low memory and dropped from the queue: 1/);
  assert.match(text, /issue-910: stopped for low memory 3 times in a row, last at phase3\. Dropped from the queue; it needs a person/);
});

/** A pauser and a releaser that only count their calls. */
function countingHooks() {
  const calls = { resume: 0, release: 0, noted: [] };
  return {
    calls,
    pause: () => ({ pause: async () => {}, resume: async () => { calls.resume += 1; } }),
    release: () => ({ note: (id) => calls.noted.push(id), release: () => { calls.release += 1; } }),
  };
}

test('a run stopped on request marks its row stopped at the phase, counts no try, and ends the run', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501' });
  addJob(config, { issue: '777' });
  const hooks = countingHooks();
  const stop = new AbortController();
  const ran = [];
  const run = async (_config, job, { signal }) => {
    ran.push(job.id);
    assert.equal(signal, stop.signal);
    stop.abort();
    return { ok: false, phase: 'phase4', reason: 'cancelled', ms: 5 };
  };
  const done = await drainQueue(config, { cutoff: '07:00', run, ...hooks, signal: stop.signal,
    clock: () => new Date('2026-10-28T10:00:00') });
  // The second row waits for the next run, and the units and the model are handled once.
  assert.deepEqual(ran, ['issue-501']);
  assert.equal(done.length, 1);
  assert.deepEqual([hooks.calls.resume, hooks.calls.release, hooks.calls.noted], [1, 1, ['issue-501']]);
  const [first, second] = readQueue(config).jobs;
  assert.deepEqual([first.status, first.phase, first.reason, first.resume], ['stopped', 'phase4', 'cancelled', true]);
  assert.equal(first.failures, undefined);
  assert.equal(second.status, 'queued');
  assert.match(summaryLines(readQueue(config))[0], /stopped at phase4 \(cancelled\), resumable/);
  assert.match(queueLines(readQueue(config))[0], /status=stopped phase=phase4 reason=cancelled/);
  assert.equal(lockHeld(config), false);
  // `queue add --resume --now` queues the job again, and the row's checkpoint is what it resumes from.
  assert.equal(addJob(config, { issue: '501', resume: true, now: true }).added, true);
  const rows = readQueue(config).jobs;
  assert.deepEqual(rows.map((r) => r.status), ['stopped', 'queued', 'queued']);
  assert.deepEqual([rows[2].resume, rows[2].now], [true, true]);
});

test('a stop that arrives while the units are being stopped starts no job', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501' });
  const stop = new AbortController();
  const pause = () => ({ pause: async ({ signal }) => { stop.abort(); assert.equal(signal.aborted, true); },
    resume: async () => {} });
  const run = async () => { throw new Error('no job should start'); };
  const done = await drainQueue(config, { cutoff: '07:00', run, pause, signal: stop.signal,
    clock: () => new Date('2026-10-28T10:00:00') });
  assert.deepEqual(done, []);
  assert.equal(readQueue(config).jobs[0].status, 'queued');
});

test('a pauser wait ends at once when the stop signal aborts', async () => {
  const stop = new AbortController();
  const lines = [];
  const config = fixtureConfig({ pause: { units: ['x.service'], scope: 'user', busyProcess: 'worker',
    pollSeconds: 3600, maxWaitMinutes: 60 } });
  const exec = (command, args) => (args.includes('list-units')
    ? { status: 0, stdout: 'x.service loaded active running\n' } : { status: 0, stdout: '' });
  // A unit with a busy worker inside it is waited for.
  const proc = scratch('proc-');
  fs.mkdirSync(path.join(proc, '42'));
  fs.writeFileSync(path.join(proc, '42', 'comm'), 'worker\n');
  fs.writeFileSync(path.join(proc, '42', 'cgroup'), '0::/system.slice/x.service\n');
  const busy = createPauser(config, { exec, log: (l) => lines.push(l), sleep: () => new Promise(() => {}),
    procRoot: proc });
  const waiting = busy.pause({ signal: stop.signal });
  setTimeout(() => stop.abort(), 20);
  await waiting;
  assert.ok(lines.includes('pause: waiting for x.service'));
});

/**
 * A loopback server that hands each request to `handle(res)` once its body is read.
 * `close` settles when the server has stopped listening.
 */
async function chatServer(handle) {
  const server = http.createServer((req, res) => {
    req.resume();
    req.on('end', () => handle(res));
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  return { endpoint: `http://127.0.0.1:${server.address().port}/v1`,
    close: () => { server.closeAllConnections(); return new Promise((resolve) => { server.close(resolve); }); } };
}

const CHAT_CALL = { system: 's', user: 'u', schema: { type: 'object' }, schemaName: 'n', reasoning: false,
  maxTokens: 10 };

/**
 * Holds a call open: with `start`, it answers with the stream's first event and never ends
 * it; without, it sends nothing. `seen` settles when the client closes the connection.
 */
function openStream({ start = true } = {}) {
  let closed;
  const seen = new Promise((resolve) => { closed = resolve; });
  const handle = (res) => {
    res.on('close', closed);
    if (!start) return;
    res.writeHead(200, { 'content-type': 'text/event-stream' });
    res.write(firstEvent());
  };
  return { handle, seen };
}

test('a model call in flight ends as Cancelled when the signal aborts, and the server sees it close', async () => {
  // Before the reply starts, and partway through a streamed reply.
  for (const start of [false, true]) {
    const stream = openStream({ start });
    const chat = await chatServer(stream.handle);
    try {
      const stop = new AbortController();
      const client = modelClient({ endpoint: chat.endpoint, name: 'm', signal: stop.signal });
      const call = client.json(CHAT_CALL);
      setTimeout(() => stop.abort(), 50);
      await assert.rejects(call, (error) => error instanceof Cancelled && !(error instanceof ModelError));
      await stream.seen;
    } finally {
      chat.close();
    }
  }
});

test('a streamed reply still running at the time-out fails as network, and the server sees it close', async () => {
  const stream = openStream();
  const chat = await chatServer(stream.handle);
  try {
    const client = modelClient({ endpoint: chat.endpoint, name: 'm', timeoutMinutes: 0.001 });
    await assert.rejects(client.json(CHAT_CALL), (error) => error.code === 'network' && error.causeCode === 'timeout');
    await stream.seen;
  } finally {
    chat.close();
  }
});

test('a streamed reply whose connection resets partway through fails as network', async () => {
  const chat = await chatServer((res) => {
    res.writeHead(200, { 'content-type': 'text/event-stream' });
    res.write(firstEvent(), () => res.socket.destroy());
  });
  try {
    const client = modelClient({ endpoint: chat.endpoint, name: 'm' });
    await assert.rejects(client.json(CHAT_CALL), (error) => error.code === 'network' && error.causeCode === 'ECONNRESET');
  } finally {
    chat.close();
  }
});

test('each model call opens a connection of its own, so one the server closed after a reply is never used again', async () => {
  // The server answers once on a connection it says it keeps open, and resets a second request sent on it.
  const answered = new Set();
  const chat = await chatServer((res) => {
    if (answered.has(res.socket)) {
      res.socket.resetAndDestroy();
      return;
    }
    answered.add(res.socket);
    res.writeHead(200, { 'content-type': 'text/event-stream' });
    res.end(sse({ content: '{"ok":true}' }));
  });
  try {
    const client = modelClient({ endpoint: chat.endpoint, name: 'm' });
    for (let call = 1; call <= 3; call += 1) assert.deepEqual((await client.json(CHAT_CALL)).value, { ok: true });
    assert.equal(answered.size, 3);
  } finally {
    chat.close();
  }
});

test('a failed connection carries a short code for its cause and none of the error text', async () => {
  const failing = (error) => modelClient({ endpoint: 'http://localhost:1/v1', name: 'm',
    fetchImpl: async () => { throw error; } });
  const cases = [
    [Object.assign(new Error('socket hang up'), { code: 'ECONNRESET' }), 'ECONNRESET'],
    // Node's own fetch wraps the failure and keeps its code on the cause.
    [Object.assign(new TypeError('fetch failed'), { cause: Object.assign(new Error('connect'), { code: 'ECONNREFUSED' }) }),
      'ECONNREFUSED'],
    [Object.assign(new Error('The operation was aborted'), { name: 'AbortError', code: 'ABORT_ERR',
      cause: new DOMException('timed out', 'TimeoutError') }), 'timeout'],
    [Object.assign(new Error('Renewal'), { code: 'Renewal is due' }), 'unknown'],
    [new Error('Renewal'), 'unknown'],
  ];
  for (const [error, cause] of cases) {
    await assert.rejects(failing(error).json(CHAT_CALL), (caught) => caught.code === 'network'
      && caught.causeCode === cause && !/Renewal/.test(`${caught.message} ${caught.causeCode}`), cause);
  }
  // A port nothing listens on. The short time-out ends the call if another process has taken the port and stays silent.
  const chat = await chatServer(() => {});
  await chat.close();
  await assert.rejects(modelClient({ endpoint: chat.endpoint, name: 'm', timeoutMinutes: 0.01 }).json(CHAT_CALL),
    (caught) => caught.code === 'network' && caught.causeCode === 'ECONNREFUSED');
});

test('a streamed reply is put together from its content deltas, without the thinking, with its usage', async () => {
  for (const finish of ['stop', 'length']) {
    const text = sse({ content: '{"text":"answer"}', reasoning: 'think it over', finish,
      usage: { prompt_tokens: 30, completion_tokens: 7 } });
    const chat = await chatServer((res) => {
      res.writeHead(200, { 'content-type': 'text/event-stream' });
      // Pieces cut across events and lines, as a reply arrives in packets.
      for (let at = 0; at < text.length; at += 7) res.write(text.slice(at, at + 7));
      res.end();
    });
    try {
      const call = modelClient({ endpoint: chat.endpoint, name: 'm' }).json(CHAT_CALL);
      if (finish === 'stop') {
        const { value, usage } = await call;
        assert.deepEqual(value, { text: 'answer' });
        assert.deepEqual([usage.promptTokens, usage.outputTokens], [30, 7]);
      } else {
        await assert.rejects(call, (error) => error.code === 'length' && error.usage.outputTokens === 7);
      }
    } finally {
      chat.close();
    }
  }
});

test('a job stopped during a model call keeps its checkpoint, retries nothing, and resumes at the phase', async () => {
  const config = fixtureConfig();
  const job = { issue: '501', change: '7001' };
  const stop = new AbortController();
  const base = fakeModel({ intake: (value) => ({ ...value, description: 'Card renewal sets the expiry from the old date' }) });
  const model = {
    ...base,
    async json(request) {
      if (request.schemaName.startsWith('phase3')) {
        stop.abort();
        throw new Cancelled();
      }
      return base.json(request);
    },
  };
  const result = await runJob(config, job, { model, echo: false, signal: stop.signal });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'cancelled');
  assert.equal(result.phase, 'phase3');
  const checkpoint = JSON.parse(read(path.join(result.outDir, 'work', 'checkpoint.json')));
  assert.equal(checkpoint.phase, 'phase2');
  const lines = statusLines(result.outDir);
  assert.ok(!lines.some((l) => ['retry', 'call-fail'].includes(l.event)));
  assert.equal(lines.at(-1).reason, 'cancelled');
  assertContentFree(read(path.join(result.outDir, 'status.log')));
  const again = await runJob(config, { ...job, resume: true }, { model: base, echo: false });
  assert.equal(again.ok, true);
  assert.ok(statusLines(again.outDir).some((l) => l.event === 'resume' && l.after === 'phase2'));
});

test('an aborted signal stops a job between phases, at the next phase', async () => {
  const config = fixtureConfig();
  const stop = new AbortController();
  const model = fakeModel({ intake: (value) => ({ ...value, description: 'Card renewal sets the expiry from the old date' }) });
  stop.abort();
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false, signal: stop.signal });
  assert.deepEqual([result.ok, result.reason, result.phase], [false, 'cancelled', 'intake']);
  assert.equal(model.calls.length, 0);
});

test('cancel settles a row a stopped run left running, restarts the units and unloads the model', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501' });
  const queue = readQueue(config);
  Object.assign(queue.jobs[0], { status: 'running', started: '2026-10-28T10:00:00.000Z' });
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  const dir = path.join(config.output, 'issue-501');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'status.log'), [
    { at: '2026-10-28T10:01:00.000Z', job: 'issue-501', phase: 'phase2', event: 'pass', ms: 5 },
    { at: '2026-10-28T10:02:00.000Z', job: 'issue-501', phase: 'phase3', event: 'start' },
  ].map((l) => JSON.stringify(l)).join('\n') + '\n');
  const hooks = countingHooks();
  const result = await cancelJob(config, 'issue-501', hooks);
  assert.deepEqual(result, { id: 'issue-501', cancelled: true, phase: 'phase3' });
  assert.deepEqual([hooks.calls.resume, hooks.calls.release], [1, 1]);
  assert.deepEqual(jobStatus(config, 'issue-501').slice(0, 1), ['issue-501  stopped  queue free']);
  // A job that is not running, or not in the queue, is not cancelled.
  assert.deepEqual(await cancelJob(config, 'issue-501', hooks), { id: 'issue-501', cancelled: false, status: 'stopped' });
  assert.equal((await cancelJob(config, 'issue-9', hooks)).status, 'not queued');
});

test('cancel gives up and says so when the holder keeps the queue', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501' });
  const queue = readQueue(config);
  queue.jobs[0].status = 'running';
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  fs.writeFileSync(`${config.at(config.queue.file)}.lock`, String(process.pid));
  const sent = [];
  let t = 0;
  const result = await cancelJob(config, 'issue-501', { kill: (pid, name) => sent.push([pid, name]),
    clock: () => new Date(t), sleep: async (ms) => { t += ms; }, waitMs: 5000, pollMs: 1000 });
  assert.deepEqual(result, { id: 'issue-501', cancelled: false, timedOut: true });
  assert.deepEqual(sent, [[process.pid, 'SIGTERM']]);
});

test('queue cancel stops a real run during a model call, frees the queue, and leaves a resumable row', async () => {
  // The server acts as Lemonade does: a streamed call stops generating when its connection
  // closes, an unstreamed one runs on to its end, and an unload waits until nothing generates.
  const requests = [];
  const events = [];
  let generating = false;
  const server = http.createServer((req, res) => {
    if (req.url.endsWith('/chat/completions')) {
      const chunks = [];
      req.on('data', (chunk) => chunks.push(chunk));
      req.on('end', () => {
        requests.push(req.url);
        generating = true;
        if (!JSON.parse(Buffer.concat(chunks).toString('utf8')).stream) return;
        res.writeHead(200, { 'content-type': 'text/event-stream' });
        res.write(firstEvent());
        res.on('close', () => {
          generating = false;
          events.push('close');
        });
      });
      return;
    }
    if (req.url.endsWith('/unload')) {
      events.push('unload');
      // The wait ends with the connection too, so a release that gave up leaves no timer behind.
      const answer = () => {
        if (res.destroyed) return;
        if (generating) setTimeout(answer, 20);
        else res.end('{}');
      };
      answer();
      return;
    }
    res.statusCode = 404;
    res.end();
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try {
    const unload = `fetch('http://127.0.0.1:${server.address().port}/api/v1/unload', { method: 'POST' })`
      + '.then((r) => process.exit(r.ok ? 0 : 1), () => process.exit(1))';
    const config = fixtureConfig({
      model: { endpoint: `http://127.0.0.1:${server.address().port}/api/v1`, name: 'test-model' },
      release: { command: [process.execPath, '-e', unload], timeoutSeconds: 5 },
    });
    const script = path.join(HERE, 'build-pack.mjs');
    const cli = (...args) => spawnSync(process.execPath, [script, 'queue', ...args, '--config', config.file],
      { encoding: 'utf8' });
    assert.equal(cli('add', '--issue', '501', '--change', '7001', '--now').status, 0);
    const child = spawn(process.execPath, [script, 'queue', 'start', '--config', config.file,
      '--job', 'issue-501-change-7001'], { stdio: 'ignore' });
    const exited = new Promise((resolve) => child.on('exit', (code, signal) => resolve({ code, signal })));
    for (let i = 0; i < 200 && !requests.length; i += 1) await new Promise((r) => setTimeout(r, 50));
    assert.ok(requests.length, 'the run reached its first model call');
    assert.deepEqual(cli('status', '--job', 'issue-501-change-7001').stdout.split('\n')[0],
      'issue-501-change-7001  running  queue held');
    // Spawned, not run in step, so this process's server answers the unload while cancel waits.
    const cancelled = await new Promise((resolve) => {
      const cancel = spawn(process.execPath, [script, 'queue', 'cancel', '--job', 'issue-501-change-7001',
        '--config', config.file]);
      const out = { stdout: '', stderr: '' };
      cancel.stdout.on('data', (chunk) => { out.stdout += chunk; });
      cancel.stderr.on('data', (chunk) => { out.stderr += chunk; });
      cancel.on('close', (status) => resolve({ ...out, status }));
    });
    assert.equal(cancelled.status, 0, cancelled.stderr);
    assert.match(cancelled.stdout, /^cancelled issue-501-change-7001$/m);
    assert.match(cancelled.stdout, /^issue-501-change-7001  stopped  queue free$/m);
    assert.match(cancelled.stdout, /^stopped phase=intake reason=cancelled$/m);
    const { code } = await exited;
    assert.equal(code, 0);
    // The cancel closed the call, so the server stopped generating before the unload asked.
    assert.deepEqual(events, ['close', 'unload']);
    const released = releaseLines(config, 'issue-501-change-7001');
    assert.deepEqual(released.map((line) => [line.event, line.reason]), [['pass', undefined]]);
    const row = readQueue(config).jobs[0];
    assert.deepEqual([row.status, row.phase, row.resume, row.failures], ['stopped', 'intake', true, undefined]);
    assert.equal(lockHeld(config), false);
    const again = cli('cancel', '--job', 'issue-501-change-7001');
    assert.equal(again.status, 1);
    assert.match(again.stderr, /is not running \(stopped\)/);
    assert.equal(cli('add', '--issue', '501', '--change', '7001', '--resume', '--now').status, 0);
    assert.equal(readQueue(config).jobs.at(-1).status, 'queued');
  } finally {
    server.closeAllConnections();
    server.close();
  }
});

test('waiting on a stop signal leaves no listener behind, and an aborted signal ends the wait', async () => {
  const stop = new AbortController();
  for (let i = 0; i < 30; i += 1) await sleepUnlessAborted(async () => {}, 1, stop.signal);
  // Each wait removes its own listener, so none pile up on the signal.
  assert.equal(getEventListeners(stop.signal, 'abort').length, 0);
  const waiting = sleepUnlessAborted(() => new Promise(() => {}), 1e9, stop.signal);
  stop.abort();
  await waiting;
  assert.equal(await sleepUnlessAborted(() => new Promise(() => {}), 1e9, stop.signal), undefined);
});

test('a stop while a run waits for the queue ends the wait without taking a job', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501' });
  fs.writeFileSync(`${config.at(config.queue.file)}.lock`, String(process.pid));
  const stop = new AbortController();
  let slept = 0;
  const sleep = async () => { slept += 1; if (slept === 2) stop.abort(); };
  const run = async () => { throw new Error('no job should start'); };
  const done = await drainQueue(config, { cutoff: '07:00', wait: true, run, sleep, signal: stop.signal,
    clock: () => new Date('2026-10-28T10:00:00') });
  assert.deepEqual(done, []);
  assert.equal(readQueue(config).jobs[0].status, 'queued');
});

test('a stop during the low-memory wait stops the job at its checkpoint as cancelled', async () => {
  const config = fixtureConfig({ memory: { enabled: true, waitMinutes: 20, pollSeconds: 30 } });
  const job = { issue: '501', change: '7001' };
  const stop = new AbortController();
  const model = fakeModel({ intake: (value) => ({ ...value, description: 'Card renewal sets the expiry from the old date' }) });
  const low = parseMeminfo(MEMINFO(1048576, 10485760, 1048576));
  const result = await runJob(config, job, { model, echo: false, signal: stop.signal, readMemory: () => low,
    sleep: async () => { stop.abort(); } });
  assert.deepEqual([result.ok, result.reason, result.phase], [false, 'cancelled', 'intake']);
  assert.equal(model.calls.length, 0);
});

test('the report counts a stopped job apart from failures', () => {
  const config = fixtureConfig();
  addJob(config, { issue: '501' });
  const queue = readQueue(config);
  Object.assign(queue.jobs[0], { status: 'stopped', phase: 'phase3', reason: 'cancelled', resume: true,
    finished: '2026-10-28T10:00:00.000Z', ms: 5 });
  const data = reportData(config, queue, { now: new Date('2026-10-28T12:00:00.000Z') });
  assert.equal(data.counts.stopped, 1);
  assert.equal(data.counts.fail + data.counts.dropped + data.counts.retry, 0);
  assert.equal(data.failing.length, 0);
  assert.match(renderReport(data), /Stopped on request and waiting to resume: 1/);
});

const APP_SCOPES = ['app-com.google.Chrome-*.scope', 'snap.spotify.spotify-*.scope'];
const closeConfig = (closeApps = {}) => fixtureConfig({ closeApps: { scopes: APP_SCOPES, keepIfRunning: ['sessiond'], ...closeApps } });

/** A closer over a fake systemctl and /proc; `lines` records its log. */
function fakeCloser(active, { failing = [], procs = [], selfCgroup = '0::/user.slice/other.scope\n' } = {}) {
  const sys = fakeSystemctl(active, failing);
  const lines = [];
  const make = (cfg) => createAppCloser(cfg, { exec: sys.exec, log: (l) => lines.push(l),
    procRoot: fakeProc(procs), selfCgroup });
  return { sys, lines, make };
}

test('apps are off unless the config lists scopes', () => {
  const fake = fakeCloser(['app-com.google.Chrome-1.scope']);
  fake.make(fixtureConfig()).close();
  assert.deepEqual(fake.sys.calls, []);
});

test('active app scopes are stopped for the user, once, and never started again', () => {
  const fake = fakeCloser(['app-com.google.Chrome-1.scope', 'snap.spotify.spotify-2.scope']);
  const closer = fake.make(closeConfig());
  closer.close();
  closer.close();
  assert.deepEqual(fake.sys.calls[0].slice(0, 3), ['systemctl', '--user', 'list-units']);
  assert.deepEqual(fake.sys.verbs(), [
    ['systemctl', '--user', 'stop', 'app-com.google.Chrome-1.scope'],
    ['systemctl', '--user', 'stop', 'snap.spotify.spotify-2.scope']]);
  assert.deepEqual(fake.lines, ['close: closed app-com.google.Chrome-1.scope',
    'close: closed snap.spotify.spotify-2.scope']);
});

test('a scope with a kept process or this process in it is left open and sessions are counted', () => {
  const chrome = 'app-com.google.Chrome-1.scope';
  const desktop = 'app-com.example.Editor-3.scope';
  const fake = fakeCloser([chrome, desktop, 'snap.spotify.spotify-2.scope'], {
    procs: [[10, 'sessiond', `/user.slice/${desktop}`], [11, 'sessiond', '/user.slice/term.scope'],
      [12, 'chrome', `/user.slice/${chrome}`]],
    selfCgroup: '0::/user.slice/snap.spotify.spotify-2.scope\n' });
  fake.make(closeConfig({ scopes: ['app-com.*.scope', ...APP_SCOPES] })).close();
  assert.deepEqual(fake.sys.verbs(), [['systemctl', '--user', 'stop', chrome]]);
  assert.deepEqual(fake.lines, [`close: closed ${chrome}`, `close: left open ${desktop}`,
    'close: left open snap.spotify.spotify-2.scope', 'close: sessiond processes open 2']);
});

test("an app's helper scope stays open with the scope that holds a kept process", () => {
  const main = 'app-com.example.Editor-7.scope';
  const helper = 'app-gnome-com.example.Editor-7.scope';
  const other = 'app-gnome-other-8.scope';
  const sameAppOtherPid = 'app-gnome-com.example.Editor-8.scope';
  const fake = fakeCloser([main, helper, other, sameAppOtherPid], { procs: [[10, 'sessiond', `/user.slice/${main}`]] });
  fake.make(closeConfig({ scopes: ['app-com.example.*.scope', 'app-gnome-*.scope'] })).close();
  assert.deepEqual(fake.sys.verbs(), [['systemctl', '--user', 'stop', other],
    ['systemctl', '--user', 'stop', sameAppOtherPid]]);
  assert.deepEqual(fake.lines.slice(0, 2), [`close: left open ${main}`, `close: left open ${helper}`]);
});

test('every close log line carries only a fixed word, a scope or process name and a count', () => {
  const scope = 'app-com.google.Chrome-1.scope';
  const fake = fakeCloser([scope, 'snap.spotify.spotify-2.scope'], { failing: [`stop ${scope}`],
    procs: [[10, 'sessiond', '/user.slice/x.scope']] });
  fake.make(closeConfig()).close();
  assert.ok(fake.lines.length >= 3);
  for (const line of fake.lines) {
    assert.match(line, /^close: (closed|left open|stop failed) \S+\.scope$|^close: sessiond processes open \d+$/, line);
  }
});

test('keepIfRunning can be emptied to close the scope that holds sessions', () => {
  const desktop = 'app-com.example.Editor-3.scope';
  const fake = fakeCloser([desktop], { procs: [[10, 'sessiond', `/user.slice/${desktop}`]] });
  fake.make(closeConfig({ scopes: ['app-com.example.Editor-*.scope'], keepIfRunning: [] })).close();
  assert.deepEqual(fake.sys.verbs(), [['systemctl', '--user', 'stop', desktop]]);
});

test('a failed stop or list is logged and nothing throws', () => {
  const scope = 'app-com.google.Chrome-1.scope';
  const failing = fakeCloser([scope], { failing: [`stop ${scope}`] });
  failing.make(closeConfig()).close();
  assert.deepEqual(failing.lines, [`close: stop failed ${scope}`]);
  const lines = [];
  createAppCloser(closeConfig(), { exec: () => ({ status: 1, stdout: '' }), log: (l) => lines.push(l),
    procRoot: fakeProc([]), selfCgroup: '' }).close();
  assert.deepEqual(lines, ['close: list failed']);
});

test('a name that is not a plain scope name is never passed to systemctl', () => {
  const fake = fakeCloser(['evil.service', '-rf.scope', 'app-ok.scope']);
  fake.make(closeConfig({ scopes: ['app-ok*.scope'] })).close();
  assert.deepEqual(fake.sys.verbs(), [['systemctl', '--user', 'stop', 'app-ok.scope']]);
});

test('a queue run closes apps once, before the first job and before units stop', async () => {
  const config = closeConfig();
  addJob(config, { issue: '1' });
  addJob(config, { issue: '2' });
  const events = [];
  const closer = { close: () => events.push('close') };
  const pause = () => ({ pause: async () => { events.push('pause'); }, resume: async () => {} });
  const run = async (cfg, job) => { events.push(`run ${job.id}`); return { ok: true, ms: 1 }; };
  await drainQueue(config, { run, pause, closeApps: () => closer });
  assert.deepEqual(events.map((e) => e.split(' ')[0]), ['close', 'pause', 'run', 'pause', 'run']);
});

test('an empty queue closes nothing', async () => {
  const closer = { close: () => assert.fail('closed') };
  await drainQueue(closeConfig(), { run: okRun, closeApps: () => closer });
});

test('a job started now leaves apps open unless onNow is set', async () => {
  for (const [onNow, expected] of [[false, 0], [true, 1]]) {
    const config = closeConfig({ onNow });
    addJob(config, { issue: '5', now: true });
    let closed = 0;
    await drainQueue(config, { nowOnly: true, run: okRun, closeApps: () => ({ close: () => { closed += 1; } }) });
    assert.equal(closed, expected, `onNow ${onNow}`);
  }
});

test('closeApps config is checked', () => {
  assert.deepEqual(fixtureConfig().closeApps, { scopes: [], onNow: false, keepIfRunning: ['claude'] });
  for (const bad of [[], 'x', { other: 1 }]) {
    assert.throws(() => fixtureConfig({ closeApps: bad }), /config closeApps must be an object/, JSON.stringify(bad));
  }
  for (const scopes of [['foo.service'], ['app-*.scope'], ['snap.*.scope'], ['app-x.slice'], 'app-x.scope', [3]]) {
    assert.throws(() => fixtureConfig({ closeApps: { scopes } }), /config closeApps\.scopes/, JSON.stringify(scopes));
  }
  assert.throws(() => fixtureConfig({ closeApps: { onNow: 'yes' } }), /closeApps\.onNow/);
  assert.throws(() => fixtureConfig({ closeApps: { keepIfRunning: [''] } }), /closeApps\.keepIfRunning/);
  assert.throws(() => fixtureConfig({ closeApps: { keepIfRunning: ['sixteen-chars-xxx'] } }),
    /up to 15 characters/);
});

const gateStop = (reason, counts) => async (_config, job) => ({ ok: false, id: job.id, phase: 'phase2', reason, ms: 1, counts });

test('queue status shows the count and numbers of a Phase 2 stop', async () => {
  const config = fixtureConfig();
  addJob(config, issueJob(['docs/OTHER/UC09-Unmapped.md']));
  const run = (cfg, job) => runJob(cfg, job, { model: fakeModel(), echo: false });
  await drainQueue(config, { cutoff: '07:00', run, clock: () => new Date('2026-11-01T08:00:00') });
  const lines = jobStatus(config, 'issue-501-change-7001');
  assert.ok(lines.includes('stopped phase=phase2 reason=gate:rules-not-extracted documents=1 numbers=1'), lines.join('\n'));
  assertContentFree(lines.join('\n'));
});

test('queue status and the summary show a Phase 2 stop that names 40 documents', async () => {
  const config = fixtureConfig();
  addJob(config, issueJob(['docs/OTHER/UC09-Unmapped.md']));
  const numbers = Array.from({ length: 40 }, (_, i) => i + 1).join(' ');
  const run = gateStop('gate:rules-not-extracted', { documents: 40, numbers });
  await drainQueue(config, { cutoff: '07:00', run, clock: () => new Date('2026-11-01T08:00:00') });
  const lines = jobStatus(config, 'issue-501-change-7001');
  const stopped = lines.find((line) => line.startsWith('stopped phase=phase2'));
  assert.ok(stopped?.includes('documents=40 numbers=1 2 3 '), lines.join('\n'));
  assert.ok(numbers.startsWith(stopped.split('numbers=')[1]), 'a whole leading run of the numbers');
  assert.match(summaryLines(readQueue(config))[0], /documents 40 \(1 2 3 /);
  // A row that holds the full list still prints, cut.
  const rows = readQueue(config);
  rows.jobs[0].numbers = numbers;
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(rows));
  const again = jobStatus(config, 'issue-501-change-7001').find((line) => line.startsWith('stopped phase=phase2'));
  assert.equal(again, stopped);
});

test('a row with no stored stop fields shows them from its last fail line', () => {
  const config = fixtureConfig();
  seedJob(config, { status: 'stopped', resume: true, phase: 'phase2', reason: 'gate:rules-not-extracted',
    added: '2026-11-01T08:00:00.000Z' }, [
    logLine('2026-11-01T08:00:01.000Z', { phase: 'phase2', event: 'fail', reason: 'gate:rules-not-extracted',
      documents: 2, numbers: '1 3' })]);
  assert.ok(jobStatus(config, 'issue-9415').includes(
    'stopped phase=phase2 reason=gate:rules-not-extracted documents=2 numbers=1 3'));
});

test('a stop no retry can change waits for a person; an outage is still retried', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '1' });
  addJob(config, { issue: '2' });
  const clock = () => new Date('2026-11-01T08:00:00');
  const run = async (cfg, job) => (job.issue === '1'
    ? gateStop('gate:rules-not-extracted', { documents: 1, numbers: '1' })(cfg, job)
    : gateStop('gate:rule-export-failed', { documents: 1, numbers: '1' })(cfg, job));
  await drainQueue(config, { cutoff: '07:00', run, clock });
  let rows = readQueue(config).jobs;
  assert.equal(rows[0].status, 'stopped');
  assert.equal(rows[0].resume, true);
  assert.equal(countedTries(rows[0].failures), 1);
  assert.equal(rows[1].status, 'queued');
  // The stopped row is not taken again, and the summary says who it waits for.
  const ran = [];
  await drainQueue(config, { cutoff: '07:00', run: async (cfg, job) => { ran.push(job.id); return run(cfg, job); }, clock });
  assert.deepEqual(ran, ['issue-2']);
  assert.match(summaryLines(readQueue(config))[0],
    /stopped at phase2 \(gate:rules-not-extracted\), waits for a person, resumable, documents 1 \(1\)/);
  // A person fixes the rules and adds it again with --resume: a fresh queued row.
  assert.equal(addJob(config, { issue: '1', resume: true }).added, true);
  rows = readQueue(config).jobs;
  assert.equal(rows.findLast((row) => row.id === 'issue-1').status, 'queued');
});

test('the report counts a held row apart from a stop on request', () => {
  const config = fixtureConfig();
  const at = '2026-11-01T08:00:00.000Z';
  const queue = { jobs: [{ id: 'issue-1', status: 'stopped', resume: true, phase: 'phase2',
    reason: 'gate:rules-not-extracted', finished: at, failures: [{ at, phase: 'phase2', reason: 'gate:rules-not-extracted', ms: 1 }] }] };
  const text = renderReport(reportData(config, queue, { period: 'day', now: new Date('2026-11-01T09:00:00.000Z') }));
  assert.match(text, /Stopped on a gate a retry cannot change, waiting for a person: 1/);
  assert.match(text, /queue add --resume/);
});

test('every stop in HOLD_REASONS leaves the row stopped for a person', async () => {
  for (const reason of HOLD_REASONS) {
    const config = fixtureConfig();
    addJob(config, { issue: '3' });
    await drainQueue(config, { cutoff: '07:00', clock: () => new Date('2026-11-01T08:00:00'),
      run: gateStop(reason, { documents: 1, numbers: '2' }) });
    const [row] = readQueue(config).jobs;
    assert.equal(row.status, 'stopped', reason);
    assert.equal(row.reason, reason);
    assert.equal(row.numbers, '2');
  }
  assert.deepEqual(HOLD_REASONS, ['gate:rules-not-extracted', 'gate:rules-malformed', 'gate:document-file',
    'gate:duplicate-rule-wording', 'gate:rule-conflict', 'gate:needs-user-review']);
});

const refusedPack = (phase) => async (_config, job) => ({ ok: false, id: job.id, phase,
  reason: 'gate:builder-fail', ms: 1, counts: { sheets: 1, failedSheets: 'Confidence Assessment' } });

test('a pack the builder refuses in a Phase 9 step leaves the row stopped, and one refused in Phase 8 is tried again', async () => {
  const clock = () => new Date('2026-11-01T08:00:00');
  for (const phase of ['phase9-checklist', 'phase9-senior', 'phase9-confidence', 'phase9-revalidate']) {
    const config = fixtureConfig();
    addJob(config, { issue: '3' });
    await drainQueue(config, { cutoff: '07:00', clock, run: refusedPack(phase) });
    const [row] = readQueue(config).jobs;
    assert.deepEqual([row.status, row.resume, row.phase, row.reason, countedTries(row.failures)],
      ['stopped', true, phase, 'gate:builder-fail', 1], phase);
    // No later run takes the row, and the summary says who it waits for.
    const ran = [];
    await drainQueue(config, { cutoff: '07:00', clock, run: async (cfg, job) => { ran.push(job.id); return refusedPack(phase)(cfg, job); } });
    assert.deepEqual(ran, [], phase);
    assert.match(summaryLines(readQueue(config))[0],
      new RegExp(`stopped at ${phase} \\(gate:builder-fail\\), waits for a person, resumable`));
  }
  const config = fixtureConfig();
  addJob(config, { issue: '3' });
  await drainQueue(config, { cutoff: '07:00', clock, run: refusedPack('phase8') });
  assert.equal(readQueue(config).jobs[0].status, 'queued');
});

test('the report says what a row held on a refused Phase 9 pack waits for', () => {
  const config = fixtureConfig();
  const at = '2026-11-01T08:00:00.000Z';
  const queue = { jobs: [{ id: 'issue-1', status: 'stopped', resume: true, phase: 'phase9-revalidate',
    reason: 'gate:builder-fail', finished: at,
    failures: [{ at, phase: 'phase9-revalidate', reason: 'gate:builder-fail', ms: 1 }] }] };
  const text = renderReport(reportData(config, queue, { period: 'day', now: new Date('2026-11-01T09:00:00.000Z') }));
  assert.match(text, /Stopped on a gate a retry cannot change, waiting for a person: 1/);
  assert.match(text, /the builder refuses the pack the review left, so fix what its failed sheets name, then `queue add --resume`/);
  assert.doesNotMatch(text, /fix the document or its rules/);
});

test('the report shows the level a build lowered the rating to, until a later rating step passes', () => {
  const config = fixtureConfig();
  const row = passedJob(config, 'issue-100', { hours: 5, confidence: 'High' });
  const log = path.join(config.output, 'issue-100', 'status.log');
  const add = (fields) => fs.appendFileSync(log, `\n${JSON.stringify({ at: hoursAgo(5), job: 'issue-100', ...fields })}`);
  const shown = () => reportData(config, { jobs: [row] }, { period: 'day', now: NOW }).jobs[0].confidence;
  assert.equal(shown(), 'High');
  add({ phase: 'phase9', step: 'confidence-ceiling', event: 'confidence-lowered', overall: 'Medium', asked: 'High',
    reason: 'confidence-ceiling' });
  assert.equal(shown(), 'Medium');
  add({ phase: 'phase9-revalidate', event: 'pass', confidence: 'Low' });
  assert.equal(shown(), 'Low');
});

test('check without a document or checkpoint writes nothing under the output folder', () => {
  const config = fixtureConfig();
  checkJob(config, { issue: '501', change: '7001', resume: true });
  assert.ok(!fs.existsSync(path.join(config.output, 'issue-501-change-7001.check')));
});

test('a row held on a gate is not reported as cancelled', async () => {
  const config = fixtureConfig();
  addJob(config, { issue: '4' });
  await drainQueue(config, { cutoff: '07:00', clock: () => new Date('2026-11-01T08:00:00'),
    run: gateStop('gate:rules-not-extracted', { documents: 1, numbers: '1' }) });
  const result = await cancelJob(config, 'issue-4');
  assert.equal(result.cancelled, false);
  assert.equal(result.status, 'stopped');
});

/** The first call a run made to one phase step, by schema name. */
const callOf = (run, schemaName) => run.model.calls.find((c) => c.schemaName === schemaName);
/** Everything a call sent the model. */
const sent = (call) => `${call.system}\n${call.user}`;

test('the operating manual reaches the card and set calls and no other phase', async () => {
  const run = lib();
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const manual = /Rule 6: prefer reusing an existing test/;
  assert.match(callOf(run, 'phase6_cards_d1_1').system, manual);
  assert.match(callOf(run, 'phase7_sets').system, manual);
  assert.doesNotMatch(callOf(run, 'phase6_scenarios_d1').system, manual);
  assert.ok(run.model.calls.filter((c) => c.schemaName.startsWith('phase9'))
    .every((c) => !manual.test(c.system)));
});

test('a config without an operating manual builds prompts without one', async () => {
  const raw = JSON.parse(read(path.join(FIXTURES, 'pipeline.json')));
  const { operatingManual, ...reference } = raw.reference;
  assert.ok(operatingManual);
  const run = lib({}, { reference });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.ok(run.model.calls.every((c) => !/Rule 6/.test(c.system)));
});

test('Phase 7 reads its methodology chapters and Phase 6 keeps its own', async () => {
  const run = lib();
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const sets = callOf(run, 'phase7_sets').system;
  assert.match(sets, /Synthetic chapter 11/);
  assert.match(sets, /Synthetic chapter 12/);
  assert.doesNotMatch(sets, /Synthetic chapter 4/);
  const cards = callOf(run, 'phase6_cards_d1_1').system;
  assert.match(cards, /Synthetic chapter 4/);
  assert.doesNotMatch(cards, /Synthetic chapter 11/);
});

test('existing tests reach the card calls and the set call, not the scenario inventory', async () => {
  const name = `existing-tests-${process.pid}.md`;
  fs.writeFileSync(path.join(FIXTURES, name), 'An existing test of the renewal screen.');
  try {
    const inputs = { ...fixtureInputs(), existingTests: name };
    const run = lib({}, { inputs });
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    assert.match(callOf(run, 'phase6_cards_d1_1').user, /Existing tests\s+An existing test/);
    assert.match(callOf(run, 'phase7_sets').user, /Existing tests\s+An existing test/);
    assert.doesNotMatch(callOf(run, 'phase6_scenarios_d1').user, /An existing test/);
    const suite = lib({}, { inputs });
    const suiteResult = await runJob(suite.config, { suite: 'LIB' }, { model: suite.model, echo: false });
    assert.equal(suiteResult.ok, true, JSON.stringify(suiteResult));
    assert.match(callOf(suite, 'phase7_sets').user, /Existing tests\s+An existing test/);
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

test('Phase 7 asks for the regression execution scope and the BREAK IT scope', async () => {
  const run = lib({ phase6_scenarios: inventory([{}, BREAK, {}]), phase6_cards: SETS,
    phase7: (value) => ({ ...value, sets: Object.fromEntries(Object.keys(value.sets)
      .map((objective) => [objective, { scope: `Scope of ${objective}` }])) }) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const call = callOf(run, 'phase7_sets');
  assert.match(call.user, /Cards by set\s+- Core Change Validation: \S.* rule\(s\) on \d+ card\(s\)/);
  assert.doesNotMatch(call.user, /undefined/);
  assert.match(sent(call), /Regression Testing, give the execution scope: how its run is grouped/);
  assert.match(sent(call), /BREAK IT, say what it tries to break/);
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.testSets.find((s) => s.objective === 'BREAK IT').scope, 'Scope of BREAK IT');
});

test('detail.log names the chapters and existing tests the design phases were given', async () => {
  const name = `existing-tests-${process.pid}.md`;
  fs.writeFileSync(path.join(FIXTURES, name), 'An existing test of the renewal screen.');
  try {
    const run = lib({}, { inputs: { ...fixtureInputs(), existingTests: name } });
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    const detail = read(path.join(result.outDir, 'detail.log'));
    assert.match(detail, /chapters 4, 7; operating manual: yes; existing tests: \d+ tokens/);
    assert.match(detail, /chapters 11, 12; operating manual: yes; existing tests: \d+ tokens/);
    assertContentFree(read(path.join(result.outDir, 'status.log')));
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

test('existing tests too large for the set call are left out and logged', async () => {
  const name = `existing-tests-${process.pid}.md`;
  fs.writeFileSync(path.join(FIXTURES, name), 'An existing test of the renewal screen. '.repeat(190));
  try {
    const inputs = { ...fixtureInputs(), existingTests: name };
    const model = { endpoint: 'http://localhost:13305/api/v1', name: 'test-model', context: 9000,
      maxOutput: 800, reasoningOutput: 800 };
    const run = lib({}, { inputs, model });
    // The window shrinks after the card and step calls and returns after the set call, so only that call lacks room.
    const shrink = run.model.json;
    run.model.json = async (request) => {
      if (request.schemaName === 'phase7_sets') run.config.model.context = 9000;
      const answer = await shrink(request);
      if (request.schemaName.startsWith('phase6_steps')) run.config.model.context = 5700;
      return answer;
    };
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    assert.doesNotMatch(callOf(run, 'phase7_sets').user, /An existing test/);
    const detail = read(path.join(result.outDir, 'detail.log'));
    assert.match(detail, /phase7 existing tests left out to fit the model/);
    assert.match(detail, /existing tests: left out/);
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

const MARKED_IMPACTS = (value) => ({ ...value, impacts: {
  ...Object.fromEntries(Object.keys(value.impacts).map((key) => [key, []])),
  windows: ['  Renewal tab  ', 'Renewal tab', ''], upstream: ['Fines batch feeds the due date'] } });

test('the Phase 4 impact analysis is kept on the pack and given to the Phase 6 and Phase 9 calls', async () => {
  const run = lib({ phase4_impact: MARKED_IMPACTS });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(Object.keys(pack.impacts), S.IMPACT_AREAS.map(([key]) => key));
  assert.deepEqual(pack.impacts.windows, ['Renewal tab']);
  assert.deepEqual(pack.impacts.upstream, ['Fines batch feeds the due date']);
  assert.deepEqual(pack.impacts.data, []);
  const section = /Impact analysis by area\s+Windows, pages and tabs: Renewal tab/;
  for (const name of ['phase6_scenarios_d1', 'phase6_cards_d1_1', 'phase9_checklist', 'phase9_senior_review',
    'phase9_senior_notes']) {
    const call = callOf(run, name);
    assert.match(call.user, section, name);
    assert.match(call.user, /Upstream: Fines batch feeds the due date/, name);
    assert.match(call.user, /Data: none found/, name);
  }
  assert.doesNotMatch(callOf(run, 'phase6_verify_d1_1')?.user ?? '', /Impact analysis by area/);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('the impact schema keeps every area as a short list of strings and the executive summary as it was', () => {
  const { properties } = S.impactSchema.properties.impacts;
  assert.deepEqual(Object.keys(properties), S.IMPACT_AREAS.map(([key]) => key));
  for (const area of Object.values(properties)) {
    assert.equal(area.type, 'array');
    assert.equal(area.items.type, 'string');
    assert.ok(area.maxItems > 0);
  }
  assert.deepEqual(Object.keys(S.impactSchema.properties.executiveSummary.properties),
    ['scope', 'modules', 'sourceDocuments', 'strategy', 'execution', 'risks']);
});

test('impactsText is empty without an analysis, says none found for an empty area, and fits its tokens', () => {
  assert.equal(impactsText(undefined, 500), '');
  assert.equal(impactsText(null, 500), '');
  assert.match(impactsText({ windows: [] }, 500), /^Windows, pages and tabs: none found$/m);
  const long = 'x'.repeat(400);
  const crowded = Object.fromEntries(S.IMPACT_AREAS.map(([key]) => [key, Array.from({ length: 8 }, (_, i) => `${key}${i} ${long}`)]));
  const text = impactsText(crowded, 1500);
  assert.ok(estimateTokens(text) <= 1500 + 80, `${estimateTokens(text)} tokens`);
  // The first item of every area goes in before the second of any.
  for (const [key] of S.IMPACT_AREAS) assert.match(text, new RegExp(`${key}0 `));
  assert.match(text, /more not shown/);
});

test('a suite pack keeps the impact analysis when the merge does not carry it', async () => {
  const run = lib({ phase4_impact: MARKED_IMPACTS });
  const result = await runJob(run.config, { suite: 'LIB' }, { model: run.model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(pack.impacts.windows, ['Renewal tab']);
  assert.match(callOf(run, 'phase9_checklist').user, /Windows, pages and tabs: Renewal tab/);
});

test('an oversized impact analysis is cut to a tenth of the call\'s room and never makes a call too big', async () => {
  const model = { endpoint: 'http://localhost:13305/api/v1', name: 'test-model', context: 9000,
    maxOutput: 800, reasoningOutput: 800 };
  const huge = (value) => ({ ...value, impacts: Object.fromEntries(Object.keys(value.impacts)
    .map((key) => [key, Array.from({ length: 8 }, (_, i) => `${key}${i} ${'y'.repeat(300)}`)])) });
  const run = lib({ phase4_impact: huge }, { model });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const call = callOf(run, 'phase6_cards_d1_1');
  const section = /Impact analysis by area\n([\s\S]*?)(\n#|$)/.exec(call.user)?.[1] ?? '';
  assert.ok(section.length > 0);
  assert.ok(estimateTokens(section) <= 900 + 120, `${estimateTokens(section)} tokens`);
  assert.match(section, /more not shown/);
});

// Rule intake and change scope: requirement type, duplicate wording, conflicts, pages, and the
// review stop.

const masterRun = (edit, extra = {}) => {
  const name = withMaster(edit);
  const inputs = { ...fixtureInputs(), ruleExport: ['node', 'export.mjs', '--doc', '{doc}', '--master', name] };
  return { name, run: lib(extra, { inputs }) };
};
const work = (result, file) => JSON.parse(read(path.join(result.outDir, 'work', file)));

test('a conflicting rule pair stops the run at rule intake', async () => {
  const run = lib({ phase2_conflicts: (value) => ({ ...value, conflicts: [
    { rules: ['BR-LIB.UC01-001', 'BR-LIB.UC01-002'], conflict: 'Different renewal windows' }] }) });
  const result = await runLib(run);
  assert.equal(result.ok, false);
  assert.equal(result.phase, 'phase2');
  assert.equal(result.reason, 'gate:rule-conflict');
  assert.equal(statusLines(result.outDir).at(-1).conflicts, 1);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
  assert.deepEqual(work(result, 'phase2-conflicts.json')[0].rules, ['BR-LIB.UC01-001', 'BR-LIB.UC01-002']);
  assert.ok(!run.model.calls.some((c) => c.schemaName.startsWith('phase3')));
});

test('a conflict pair that names one rule twice is dropped', async () => {
  const run = lib({ phase2_conflicts: (value) => ({ ...value, conflicts: [
    { rules: ['BR-LIB.UC01-001', 'BR-LIB.UC01-001'], conflict: 'Same rule' }] }) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
});

test('two live rules of a document with the same wording stop the run, and it holds for a person', async () => {
  const { name, run } = masterRun((row) => {
    if (row.rule_id === 'BR-LIB.UC01-002') {
      row.description = 'Renew is enabled from 30 days before expiry until 90 days after it.';
      row.rule_summary = row.description;
    }
  });
  try {
    const result = await runLib(run);
    assert.equal(result.reason, 'gate:duplicate-rule-wording');
    assert.equal(result.phase, 'phase2');
    assert.ok(statusLines(result.outDir).some((l) => l.event === 'stop-doc' && l.document === 1));
    assert.deepEqual(work(result, 'phase2-duplicates.json'), [['BR-LIB.UC01-001', 'BR-LIB.UC01-002']]);
    assert.ok(!run.model.calls.some((c) => c.schemaName.startsWith('phase2_conflicts')));
    assert.ok(HOLD_REASONS.includes(result.reason));
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

test('short identical wording under different names does not stop the run', async () => {
  const { name, run } = masterRun((row) => {
    if (row.rule_id === 'BR-LIB.UC01-002' || row.rule_id === 'BR-LIB.UC01-003') {
      row.rule_summary = 'Field is mandatory.';
      row.description = row.rule_summary;
    }
  });
  try {
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

// The scope reply raises one question; `triage` is the review call's row for it.
const reviewRun = (triage, overrides = {}) => lib({
  phase3_scope: (value) => ({ ...NOT_REMOVAL.phase3_scope(value), userReview: ['Does the fix apply to desk renewals?'] }),
  phase3_review: { questions: { Q1: { quote: '', ruling: 'kept', statement: '', testImpact: '', toConfirm: '',
    why: '', ...triage } } },
}, overrides);
const phase3Line = (outDir) => statusLines(outDir).find((l) => l.phase === 'phase3' && ['pass', 'fail'].includes(l.event));

test('a review question the change description cannot settle stops change scope before the impact analysis', async () => {
  const run = reviewRun({ quote: 'The fines block and the renewal window are unchanged.',
    statement: 'The fix applies to desk renewals as well as online ones.' });
  const result = await runLib(run);
  assert.equal(result.phase, 'phase3');
  assert.equal(result.reason, 'gate:needs-user-review');
  const line = phase3Line(result.outDir);
  assert.deepEqual([line.review, line.raised, line.answered, line.assumed], [1, 1, 0, 0]);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
  assert.deepEqual(work(result, 'phase3-review.json'), [{ question: 'Does the fix apply to desk renewals?',
    quote: 'The fines block and the renewal window are unchanged.', verbatim: true }]);
  assert.equal(work(result, 'partial-pack.json').changeScope.downstream, 'NEEDS USER REVIEW');
  assert.ok(!run.model.calls.some((c) => c.schemaName.startsWith('phase4')));
  const [review, ...more] = run.model.calls.filter((c) => c.schemaName.startsWith('phase3_review'));
  assert.equal(more.length, 0);
  assert.equal(review.reasoning, false);
  assert.match(review.user, /Online and desk renewals both take the fix\./);
  assert.match(review.user, /- Q1: Does the fix apply to desk renewals\?/);
});

test('a review question the change description answers passes change scope with an assumption that quotes it', async () => {
  // The model's copy breaks the line where the description does not; only the words are compared.
  const result = await runLib(reviewRun({ quote: 'Online and desk\nrenewals both take the fix.', ruling: 'answered',
    statement: 'The fix applies to desk renewals as well as online ones.', testImpact: 'Desk renewals go untested.',
    toConfirm: 'Confirm desk renewals take the fix.' }));
  assert.equal(result.ok, true, JSON.stringify(result));
  const line = phase3Line(result.outDir);
  assert.equal(line.downstream, 'READY WITH ASSUMPTIONS');
  assert.deepEqual([line.raised, line.answered, line.assumed], [1, 1, 0]);
  const pack = JSON.parse(read(result.packPath));
  const held = pack.assumptions.find((a) => a.assumption === 'The fix applies to desk renewals as well as online ones.');
  assert.deepEqual(held, { assumption: 'The fix applies to desk renewals as well as online ones.',
    why: 'The change description says: "Online and desk\nrenewals both take the fix."',
    impact: 'Desk renewals go untested.', clarification: 'Confirm desk renewals take the fix.' });
  assert.ok(!fs.existsSync(path.join(result.outDir, 'work', 'phase3-review.json')));
});

test('a review answer whose sentence is not in the change description, or an assumption ruling, passes as an assumption', async () => {
  for (const triage of [{ quote: 'Desk renewals are covered by the fix.', ruling: 'answered' },
    { quote: 'Online and desk renewals both take the fix.', ruling: 'assumption' }]) {
    const result = await runLib(reviewRun({ ...triage, statement: 'Desk renewals take the fix.',
      why: 'The change names both renewal paths.' }));
    assert.equal(result.ok, true, JSON.stringify(result));
    const line = phase3Line(result.outDir);
    assert.deepEqual([line.raised, line.answered, line.assumed], [1, 0, 1], triage.ruling);
    const held = JSON.parse(read(result.packPath)).assumptions.find((a) => a.assumption === 'Desk renewals take the fix.');
    assert.equal(held.why, 'The change names both renewal paths.');
  }
});

test('a review question whose statement is missing, a ruling word, too short, or about the pipeline still stops change scope', async () => {
  const quote = 'Online and desk renewals both take the fix.';
  for (const triage of [{ ruling: 'answered', quote }, { ruling: 'answered', quote, statement: 'Answered.' },
    { ruling: 'assumption', statement: 'Both apply' },
    { ruling: 'assumption', statement: 'The rules for desk renewals were not supplied, so they are out of scope.' }]) {
    const result = await runLib(reviewRun(triage));
    assert.equal(result.reason, 'gate:needs-user-review', JSON.stringify(triage));
    const [kept] = work(result, 'phase3-review.json');
    assert.equal(kept.verbatim, Boolean(triage.quote));
    assert.equal(kept.quote, triage.quote ?? '');
  }
});

test('change scope ends READY WITH ASSUMPTIONS when it adds assumptions and READY when it adds none', async () => {
  const phase3 = (outDir) => statusLines(outDir).find((l) => l.event === 'pass' && l.phase === 'phase3');
  const first = await runLib(lib({ phase3_scope: (value) => ({ ...value, assumptions: [
    { assumption: 'The renewal window is calendar days', basis: 'The document says days' }] }) }));
  assert.equal(first.ok, true, JSON.stringify(first));
  assert.equal(phase3(first.outDir).downstream, 'READY WITH ASSUMPTIONS');
  const second = await runLib(lib({ phase3_scope: (value) => ({ ...value, assumptions: [] }) }));
  assert.equal(second.ok, true, JSON.stringify(second));
  assert.equal(phase3(second.outDir).downstream, 'READY');
});

// The build supervisor: at a question gate the job waits for answers while the
// supervisor's `queue watch` heartbeat is fresh.

const JOB_501 = 'issue-501-change-7001';
const ANSWER = { id: 'Q1', answer: 'Desk renewals take the fix as well as online ones.', confidence: 'settled',
  citations: ['docs/LIB/UC01-Card-Renewal.md, Renewal', 'change description'] };
const writeAnswers = (run, phase, value) => fs.writeFileSync(answersPath(path.join(run.config.output, JOB_501), phase),
  typeof value === 'string' ? value : JSON.stringify(value));

/**
 * Runs job 501 with a clock only the waits move and a fresh heartbeat. At each of the
 * wait's polls the clock moves by the poll, the heartbeat is touched again, and
 * `onSleep(n, t)` runs. `post` receives the notice line.
 */
async function supervisedRun(run, { onSleep = () => {}, post = async () => true } = {}) {
  let t = Date.now();
  const sleeps = [];
  touchHeartbeat(run.config, JOB_501, new Date(t));
  const result = await runJob(run.config, { issue: '501', change: '7001' }, { model: run.model, echo: false,
    now: () => t, post,
    sleep: async (ms) => {
      t += ms;
      sleeps.push(ms);
      touchHeartbeat(run.config, JOB_501, new Date(t));
      await onSleep(sleeps.length, t);
    } });
  return { result, sleeps };
}

test('a review question the build supervisor answers passes change scope with no further model call', async () => {
  const run = reviewRun({});
  const { result, sleeps } = await supervisedRun(run, {
    onSleep: (n) => n === 1 && writeAnswers(run, 'phase3', { answers: [ANSWER] }) });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(sleeps.length, 1);
  assert.deepEqual(work(result, 'questions-phase3.json').questions,
    [{ id: 'Q1', question: 'Does the fix apply to desk renewals?' }]);
  const lines = statusLines(result.outDir);
  const waiting = lines.find((l) => l.event === 'waiting');
  assert.deepEqual([waiting.phase, waiting.questions, waiting.waitMinutes], ['phase3', 1, 30]);
  const answered = lines.find((l) => l.event === 'answers');
  assert.deepEqual([answered.answered, answered.declined, answered.settled, answered.bestReading], [1, 0, 1, 0]);
  const line = phase3Line(result.outDir);
  assert.deepEqual([line.event, line.supervised, line.downstream], ['pass', 1, 'READY WITH ASSUMPTIONS']);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
  // The scope call and the review call; the answer needs no third.
  assert.equal(run.model.calls.filter((c) => c.schemaName.startsWith('phase3')).length, 2);
  const pack = JSON.parse(read(result.packPath));
  const held = pack.assumptions.find((a) => a.answeredBy === 'build supervisor');
  assert.deepEqual(held, { assumption: ANSWER.answer,
    why: 'Answered by the build supervisor (settled) from docs/LIB/UC01-Card-Renewal.md, Renewal; change description.',
    impact: 'The rules were classified before this answer; a different answer can change their impact.',
    clarification: 'Confirm with the change owner: Does the fix apply to desk renewals?',
    answeredBy: 'build supervisor', confidence: 'settled', citations: ANSWER.citations,
    question: 'Does the fix apply to desk renewals?' });
  assert.ok(pack.intake.assumptionsToProceed.includes(`Answered by the build supervisor (settled): ${ANSWER.answer}`));
});

test('a review question nobody answers holds the job with its usual reason once the wait runs out', async () => {
  const { result, sleeps } = await supervisedRun(reviewRun({}));
  assert.equal(result.reason, 'gate:needs-user-review');
  assert.ok(HOLD_REASONS.includes(result.reason));
  assert.equal(sleeps.reduce((sum, ms) => sum + ms, 0), 30 * 60000);
  const over = statusLines(result.outDir).find((l) => l.event === 'wait-over');
  assert.equal(over.reason, 'timeout');
  assert.equal(phase3Line(result.outDir).review, 1);
});

test('with the wait off, a stale heartbeat or none, a question gate holds at once', async () => {
  for (const [overrides, ageMinutes] of [[{ supervisor: { waitMinutes: 0 } }, 0], [{}, 16], [{}, null]]) {
    const run = reviewRun({}, overrides);
    if (ageMinutes !== null) touchHeartbeat(run.config, JOB_501, new Date(Date.now() - ageMinutes * 60000));
    const result = await runJob(run.config, { issue: '501', change: '7001' }, { model: run.model, echo: false,
      sleep: () => assert.fail('the job waited') });
    assert.equal(result.reason, 'gate:needs-user-review', JSON.stringify(overrides));
    assert.ok(!statusLines(result.outDir).some((l) => l.event === 'waiting'));
    assert.ok(!fs.existsSync(path.join(result.outDir, 'work', 'questions-phase3.json')));
  }
});

test('the wait ends and the job holds when the heartbeat goes stale', async () => {
  const run = reviewRun({});
  let t = Date.now();
  touchHeartbeat(run.config, JOB_501, new Date(t));
  const result = await runJob(run.config, { issue: '501', change: '7001' }, { model: run.model, echo: false,
    now: () => t, sleep: async (ms) => { t += ms; } });
  assert.equal(result.reason, 'gate:needs-user-review');
  assert.equal(statusLines(result.outDir).find((l) => l.event === 'wait-over').reason, 'supervisor-gone');
});

test('an answers file that fails its schema is logged and the wait goes on; one that leaves a question out holds the job', async () => {
  const run = reviewRun({});
  const files = ['{"answers": [', { answers: [{ ...ANSWER, confidence: 'sure' }] }, { answers: [ANSWER] }];
  const { result, sleeps } = await supervisedRun(run, { onSleep: (n) => writeAnswers(run, 'phase3', files[n - 1]) });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(sleeps.length, 3);
  assert.deepEqual(statusLines(result.outDir).filter((l) => l.event === 'answers-rejected').map((l) => l.reason),
    ['answers-not-json', 'answers-confidence']);
  const declined = reviewRun({});
  const held = await supervisedRun(declined, { onSleep: () => writeAnswers(declined, 'phase3', { answers: [] }) });
  assert.equal(held.result.reason, 'gate:needs-user-review');
  const line = statusLines(held.result.outDir).find((l) => l.event === 'answers');
  assert.deepEqual([line.answered, line.declined], [0, 1]);
});

test('queue status shows a job waiting for the build supervisor while its run holds the queue, and the notice goes out once', async () => {
  const run = reviewRun({}, { supervisor: { notifyUrl: 'https://ntfy.example/builds' } });
  const posted = [];
  let dead = null;
  let shown = null;
  const { result } = await supervisedRun(run, {
    post: async (url, text) => { posted.push([url, text]); return true; },
    onSleep: (n, t) => {
      fs.writeFileSync(run.config.at(run.config.queue.file), JSON.stringify({ jobs: [
        { id: JOB_501, issue: '501', change: '7001', status: 'running', started: new Date(t - 3600000).toISOString() }] }));
      // With no live process holding the queue, the run died and nobody waits for an answer.
      dead = jobStatus(run.config, JOB_501, { clock: () => new Date(t) });
      const lock = `${run.config.at(run.config.queue.file)}.lock`;
      fs.writeFileSync(lock, String(process.pid));
      shown = jobStatus(run.config, JOB_501, { clock: () => new Date(t) });
      fs.rmSync(lock);
      writeAnswers(run, 'phase3', { answers: [ANSWER] });
    } });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.ok(dead.some((l) => l.startsWith('interrupted ')) && !dead.some((l) => l.startsWith('waiting')), dead.join('\n'));
  assert.ok(shown.includes('waiting phase=phase3 questions=1 left=30'), shown.join('\n'));
  assert.deepEqual(posted, [['https://ntfy.example/builds', `${JOB_501} waiting phase=phase3 questions=1 left=30`]]);
  const failing = reviewRun({}, { supervisor: { notifyUrl: 'https://ntfy.example/builds' } });
  const again = await supervisedRun(failing, { post: async () => { throw new Error('offline'); },
    onSleep: () => writeAnswers(failing, 'phase3', { answers: [ANSWER] }) });
  assert.equal(again.result.ok, true, JSON.stringify(again.result));
  assert.ok(statusLines(again.result.outDir).some((l) => l.event === 'warn' && l.reason === 'notify-failed'));
});

test('the build supervisor answers a rule conflict and the job goes on past rule intake', async () => {
  const run = lib({ phase2_conflicts: (value) => ({ ...value, conflicts: [
    { rules: ['BR-LIB.UC01-001', 'BR-LIB.UC01-002'], conflict: 'Different renewal windows' }] }) });
  const { result } = await supervisedRun(run, { onSleep: () => writeAnswers(run, 'phase2',
    { answers: [{ ...ANSWER, answer: 'The 30-day window applies.', citations: ['BR-LIB.UC01-001'] }] }) });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.deepEqual(work(result, 'questions-phase2.json').questions,
    [{ id: 'Q1', question: 'Rules BR-LIB.UC01-001 and BR-LIB.UC01-002: Different renewal windows' }]);
  assert.equal(statusLines(result.outDir).find((l) => l.event === 'pass' && l.phase === 'phase2').supervised, 1);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.assumptions.some((a) => a.answeredBy === 'build supervisor' && a.assumption === 'The 30-day window applies.'));
});

test('the build supervisor answers a source conflict and the understanding gate passes', async () => {
  const run = lib({ phase1_understanding: (value) => ({ ...value, conflicts: ['UC01 and the defect record disagree'] }) });
  const { result } = await supervisedRun(run, { onSleep: () => writeAnswers(run, 'phase1', { answers: [ANSWER] }) });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(statusLines(result.outDir).find((l) => l.event === 'pass' && l.phase === 'phase1').supervised, 1);
  assert.equal(run.model.calls.filter((c) => c.schemaName.startsWith('phase1_understanding')).length, 1);
});

test('a conflict the rule batches find is answered before the understanding call, which reads the answer', async () => {
  const name = withMaster((row) => { row.rule_summary = `${row.rule_summary} ${'x'.repeat(30000)}`; });
  try {
    const inputs = { ...fixtureInputs(), ruleExport: ['node', 'export.mjs', '--doc', '{doc}', '--master', name] };
    const run = lib({ phase1_rules_2: (value) => ({ ...value, conflicts: ['A and B disagree'] }) }, { inputs });
    const { result, sleeps } = await supervisedRun(run, { onSleep: () => writeAnswers(run, 'phase1',
      { answers: [{ ...ANSWER, answer: 'A governs.' }] }) });
    assert.equal(result.ok, true, JSON.stringify(result));
    // The batch's conflict comes back with the understanding call's, settled by the first answer.
    assert.equal(sleeps.length, 1);
    const final = run.model.calls.find((c) => c.schemaName.startsWith('phase1_understanding'));
    assert.match(final.user, /- A and B disagree: A governs\./);
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

test('queue watch keeps the heartbeat fresh and shows the job', () => {
  const config = fixtureConfig();
  const watch = (id) => spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'queue', 'watch',
    '--config', config.file, '--job', id], { encoding: 'utf8' });
  const shown = watch(JOB_501);
  assert.equal(shown.status, 0, shown.stderr);
  assert.match(shown.stdout, new RegExp(`^${JOB_501}  not queued`));
  const at = Date.parse(read(heartbeatPath(config, JOB_501)).trim());
  assert.ok(Date.now() - at < 60000);
  assert.notEqual(watch('../x').status, 0);
});

test("a sandbox's wait shows until its end time and the poll after it, with no queue lock", () => {
  const config = fixtureConfig();
  const id = `${JOB_501}~waits`;
  const until = Date.parse('2026-11-05T04:29:17Z');
  const line = (event, extra = {}) => JSON.stringify({ at: '2026-11-05T03:59:17.000Z', job: id, phase: 'phase3', event, ...extra });
  fs.mkdirSync(path.join(config.output, id), { recursive: true });
  fs.writeFileSync(path.join(config.output, id, 'status.log'), `${[line('resume', { after: 'phase2' }), line('start'),
    line('waiting', { questions: 3, until: '2026-11-05T04:29:17Z', waitMinutes: 30 })].join('\n')}\n`);
  const at = (ms) => jobStatus(config, id, { clock: () => new Date(ms) });
  assert.ok(at(until - 60000).includes('waiting phase=phase3 questions=3 left=1'));
  assert.ok(at(until + 15000).includes('waiting phase=phase3 questions=3 left=0'));
  assert.ok(!at(until + 16000).some((l) => l.startsWith('waiting')));
});

test('the supervisor block is checked when the config loads', () => {
  assert.deepEqual(fixtureConfig().supervisor, { waitMinutes: 30, staleMinutes: 15, notifyUrl: null });
  for (const [supervisor, message] of [[{ wait: 1 }, /supervisor must be an object/],
    [{ waitMinutes: -1 }, /waitMinutes/], [{ staleMinutes: 0 }, /staleMinutes/],
    [{ notifyUrl: 'ftp://host/x' }, /notifyUrl/], [{ notifyUrl: 'not a url' }, /notifyUrl/]]) {
    assert.throws(() => fixtureConfig({ supervisor }), message);
  }
});

test('a rule with no source page warns and is named under Job Intake, and every rule carries its requirement type', async () => {
  const { name, run } = masterRun((row) => {
    if (row.rule_id === 'BR-LIB.UC01-003') row.source_page = '';
    if (row.rule_id === 'BR-LIB.UC01-004') row.requirement_type = 'Workflow';
  });
  try {
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    const warn = statusLines(result.outDir).find((l) => l.reason === 'rule-page-missing');
    assert.equal(warn.document, 1);
    assert.equal(warn.rules, 1);
    const pack = JSON.parse(read(result.packPath));
    assert.match(pack.limitations['Job Intake'], /BR-LIB\.UC01-003/);
    assert.ok(!read(path.join(result.outDir, 'status.log')).includes('BR-LIB.UC01-003'));
    const types = Object.fromEntries(pack.rules.map((rule) => [rule.id, rule.requirementType]));
    assert.equal(types['BR-LIB.UC01-004'], 'Workflow');
    assert.equal(types['BR-LIB.UC01-001'], 'Business Rule');
  } finally {
    fs.rmSync(path.join(FIXTURES, name), { force: true });
  }
});

test('a conflict reported in both orders counts once, and a blank review question does not stop change scope', async () => {
  const pair = (a, b) => ({ rules: [a, b], conflict: 'Different renewal windows' });
  const run = lib({ phase2_conflicts: (value) => ({ ...value, conflicts: [
    pair('BR-LIB.UC01-001', 'BR-LIB.UC01-002'), pair('BR-LIB.UC01-002', 'BR-LIB.UC01-001')] }) });
  const result = await runLib(run);
  assert.equal(result.reason, 'gate:rule-conflict');
  assert.equal(statusLines(result.outDir).at(-1).conflicts, 1);
  const blank = lib({ phase3_scope: (value) => ({ ...value, userReview: ['', '  '] }) });
  const passed = await runLib(blank);
  assert.equal(passed.ok, true, JSON.stringify(passed));
  assert.ok(!blank.model.calls.some((c) => c.schemaName.startsWith('phase3_review')));
});

// A step the rules forbid, planted on the first card of the step call.
const forbidStep = (value) => {
  value.cards[0].steps[0] = { step: 1, possible: false, why: 'BR-LIB.UC01-002 disables Save until the value changes' };
  return value;
};

test('a card with a step the rules forbid is designed again once and kept when the new card is possible', async () => {
  const run = lib({ phase6_scenarios: inventory([{}, {}]), phase6_cards: titled, phase6_steps: forbidStep });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const fix = run.model.calls.filter((c) => c.schemaName.startsWith('phase6_stepfix'));
  assert.equal(fix.length, 1);
  assert.match(fix[0].user, /step 1: BR-LIB\.UC01-002 disables Save/);
  assert.equal(run.model.calls.filter((c) => c.schemaName.startsWith('phase6_restep')).length, 1);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(!pack.assumptions.some((a) => /may not be possible/.test(a.assumption)));
  assert.equal(phase6Pass(result.outDir).stepsFlagged, 1);
});

test('a card still flagged after one redesign is kept, with an assumption naming the step and the rule', async () => {
  const run = lib({ phase6_scenarios: inventory([{}, {}]), phase6_cards: titled, phase6_steps: forbidStep,
    phase6_restep: forbidStep });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  const note = pack.assumptions.find((a) => /Step 1 of the card .* may not be possible/.test(a.assumption));
  assert.ok(note, 'assumption written');
  assert.match(note.why, /BR-LIB\.UC01-002 disables Save/);
  assert.equal(pack.testCards.length, 2);
});

test('a card that repeats another is dropped before verification and counted', async () => {
  const same = (value) => ({ ...value, cards: value.cards.map((card) => ({ ...card,
    title: 'Renewal of a card', mission: 'Renewal of a card', focus: ['Renewal of a card'] })) });
  const run = lib({ phase6_scenarios: inventory([{ kind: 'control' }, { kind: 'isolation' }]), phase6_cards: same });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.testCards.length, 1);
  // The card that stays carries its own scenario's kind, not the dropped card's.
  assert.equal(pack.testCards[0].kind, 'control');
  assert.equal(phase6Pass(result.outDir).repeats, 1);
  assert.ok(pack.assumptions.some((a) => /dropped as a repeat/.test(a.assumption)));
});

test('a BREAK IT card and a plain card that read alike both stay, in either order, each in its own sets', async () => {
  const same = (value) => ({ ...value, cards: value.cards.map((card) => ({ ...card,
    title: 'Renewal of a card', mission: 'Renewal of a card', focus: ['Renewal of a card'] })) });
  for (const specs of [[{}, BREAK], [BREAK, {}]]) {
    const order = specs[0] === BREAK ? 'break first' : 'plain first';
    const run = lib({ phase6_scenarios: inventory(specs), phase6_cards: same });
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    const pack = JSON.parse(read(result.packPath));
    assert.equal(pack.testCards.length, 2, order);
    assert.equal(phase6Pass(result.outDir).repeats, 0, order);
    assert.ok(!pack.assumptions.some((a) => /dropped as a repeat/.test(a.assumption)), order);
    // The inventory's break scenario serves BREAK IT, so no pass asks for more.
    assert.ok(!run.model.calls.some((c) => c.schemaName.startsWith('phase6_scenarios_d1_break')), order);
    const setOf = (objective) => {
      assert.equal(pack.objectives.find((r) => r.objective === objective).applicable, true, `${order}: ${objective}`);
      return pack.testSets.find((row) => row.objective === objective).cards;
    };
    const [breakIt, core] = [setOf('BREAK IT'), setOf('Core Change Validation')];
    assert.equal(breakIt.length, 1, order);
    assert.equal(core.length, 1, order);
    assert.notEqual(breakIt[0], core[0], order);
  }
});

test('rules a card takes from a folded or dropped card join its scenario, so a redesign keeps them', () => {
  const rule = (id) => ({ id, sourceDocument: 'D', module: 'M', impact: 'Direct Change', summary: `rule ${id}` });
  const step = (description, expected, rules) => ({ description, expected, rules });
  const raises = { title: 'Blocked', scenario: 'S1', rules: ['R1'], objectives: ['Core'], expected: 'The error message shows',
    steps: [step('Select the role', 'The error message shows', ['R1'])] };
  const answers = { title: 'Ok', scenario: 'S2', rules: ['R1', 'R2'], objectives: ['Flow'], expected: 'The message closes',
    steps: [step('Select Ok', 'The message closes', ['R1', 'R2'])] };
  const scenarios = [{ id: 'S1', kind: 'control', rules: ['R1'] }, { id: 'S2', kind: 'isolation', rules: ['R1', 'R2'] }];
  const ctx = { designed: { k: { cards: [raises, answers], scenarios, assumptions: [] } },
    pack: { rules: [rule('R1'), rule('R2')] } };
  const verified = new Set([raises, answers]);
  const checked = new Set([raises, answers]);
  const done = tidyDocument(ctx, { key: 'k', name: 'D', module: 'M', text: '' }, verified, checked);
  assert.equal(done.folded, 1);
  assert.deepEqual(ctx.designed.k.cards.map((c) => c.title), ['Blocked']);
  assert.deepEqual(scenarios[0].rules, ['R1', 'R2']);
  assert.ok(!verified.has(raises) && !checked.has(raises));
  assert.deepEqual(ctx.designed.k.cards[0].rules, ['R1', 'R2']);
  assert.deepEqual(ctx.designed.k.cards[0].objectives, ['Core', 'Flow']);
  // The card that stays is still written for its own scenario, so it keeps that scenario's kind.
  assert.equal(scenarios.find((s) => s.id === ctx.designed.k.cards[0].scenario).kind, 'control');
});

test('a flagged break card is kept apart from a plain card only while the pack has a BREAK IT set', () => {
  const alike = (scenario, breakIt) => ({ title: 'Renewal of a card', mission: 'Renewal of a card',
    focus: ['Renewal of a card'], scenario, rules: ['R1'], objectives: ['Core'], breakIt,
    steps: [{ description: 'Select Save', expected: 'The card renews', rules: ['R1'] }] });
  const tidied = (applicable) => {
    const ctx = { job: { suite: false }, breakItObjective: 'Break',
      designed: { k: { cards: [alike('S1', false), alike('S2', true)], assumptions: [],
        scenarios: [{ id: 'S1', rules: ['R1'] }, { id: 'S2', rules: ['R1'] }] } },
      pack: { objectives: [{ objective: 'Core', applicable: true }, { objective: 'Break', applicable }],
        rules: [{ id: 'R1', sourceDocument: 'D', module: 'M', impact: 'Direct Change', summary: 'Renewal of a card' }] } };
    const done = tidyDocument(ctx, { key: 'k', name: 'D', module: 'M', text: 'Renewal of a card' }, new Set());
    return [done.repeats, ctx.designed.k.cards.length];
  };
  assert.deepEqual(tidied(true), [0, 2]);
  // Without the set the flagged card would sit in the plain card's sets, so it is a repeat.
  assert.deepEqual(tidied(false), [1, 1]);
});

test('a BREAK IT card stays out of the core set', () => {
  const ctx = { job: { suite: false }, config: {}, coreObjective: 'Core', fullCoverageObjective: 'Full',
    breakItObjective: 'Break', pack: { objectives: ['Core', 'Flow', 'Full', 'Break']
      .map((objective) => ({ objective, applicable: true })) } };
  const card = { derivation: 'Requirement', objectives: ['Core', 'Flow'] };
  assert.deepEqual(setsOf(ctx, { ...card, breakIt: true }).sort(), ['Break', 'Flow', 'Full']);
  assert.deepEqual(setsOf(ctx, { ...card, breakIt: false }).sort(), ['Core', 'Flow', 'Full']);
});

/** The call records of a job, in sequence order. */
const callRecords = (outDir) => {
  const dir = path.join(outDir, 'work', 'calls');
  return fs.readdirSync(dir).sort().map((name) => ({ name, ...JSON.parse(read(path.join(dir, name))) }));
};

test('a run records every model call with its prompt, reply and counts, in the order they were made', async () => {
  const model = fakeModel({ ...INTAKE, ...NOT_REMOVAL });
  const answered = [];
  const answer = model.json;
  model.json = async (request) => {
    const reply = await answer(request);
    answered.push(structuredClone(reply.value));
    return reply;
  };
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const records = callRecords(result.outDir);
  assert.equal(records.length, model.calls.length);
  assert.deepEqual(records.map((r) => r.seq), records.map((_, i) => i + 1));
  records.forEach((record, i) => {
    const sent = model.calls[i];
    assert.equal(record.name, callFileName(i + 1, sent.schemaName, 1));
    assert.equal(record.attempt, 1);
    assert.equal(record.step, sent.schemaName);
    assert.equal(record.thinking, Boolean(sent.reasoning));
    assert.equal(record.maxTokens, sent.maxTokens);
    assert.deepEqual(record.prompt, { system: sent.system, user: sent.user });
    assert.equal(record.promptHash, promptHash(sent.system, sent.user));
    assert.equal(record.schemaHash, schemaHash(sent.schema));
    assert.deepEqual(record.usage, { promptTokens: 10, outputTokens: 5 });
    assert.equal(record.error, null);
    assert.deepEqual(record.reply, answered[i]);
    assert.ok(Date.parse(record.endedAt) >= Date.parse(record.startedAt));
  });
  // Prompt text stays out of the log a session may read.
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('a thinking call that is cut and retried records both attempts, and a second cut records as runaway', async () => {
  const dir = scratch('calls-ask-');
  const reply = (cut) => streamed({ finish: cut ? 'length' : 'stop', content: cut ? '{"a":' : '{"ok":true}',
    usage: { prompt_tokens: 30, completion_tokens: 7 } });
  const { ask } = await import('./phases.mjs');
  const over = (cutOn) => ({ config: fixtureConfig(), calls: 0, tokens: { prompt: 0, output: 0 },
    logs: jobLogs(dir, { echo: false }), job: { id: 'j' },
    model: { ...modelClient({ endpoint: 'http://localhost:1/v1', name: 'm',
      fetchImpl: async (url, options) => reply(cutOn(JSON.parse(options.body).chat_template_kwargs.enable_thinking)) }),
    countTokens: async () => 10 } });
  const call = (ctx, step) => ask(ctx, { phase: 'phase9', step, reasoning: true, inputs: [['Doc', 'text']],
    schema: { type: 'object' }, task: 'do it' });
  // Cut while thinking only: the retry answers.
  assert.deepEqual(await call(over((thinking) => thinking), 'walk'), { ok: true });
  // Cut on both attempts: the second cut is a runaway.
  await assert.rejects(call(over(() => true), 'repair'), { code: 'runaway' });
  const records = callRecords(dir);
  // Every attempt notes the seed, the runaway too, whose error the retry makes anew.
  assert.deepEqual(records.map((r) => [r.step, r.attempt, r.thinking, r.error?.code ?? null, r.seed]), [
    ['phase9_walk', 1, true, 'length', DEFAULT_SEED],
    ['phase9_walk', 2, false, null, DEFAULT_SEED],
    ['phase9_repair', 1, true, 'length', DEFAULT_SEED],
    ['phase9_repair', 2, false, 'runaway', DEFAULT_SEED],
  ]);
  assert.deepEqual(records[1].reply, { ok: true });
  assert.equal(records[0].reply, null);
  assert.equal(records[0].usage.outputTokens, 7);
  assert.equal(records[0].promptHash, records[1].promptHash);
});

test('a resumed job keeps the calls it recorded before the stop and numbers the new ones after them', async () => {
  const config = fixtureConfig();
  const down = { phase9_checklist: () => { throw new ModelError('no-reply', 'x'); } };
  const first = await runJob(config, { issue: '501' },
    { model: fakeModel({ ...INTAKE, ...NOT_REMOVAL, ...down }), echo: false });
  assert.equal(first.ok, false);
  const before = callRecords(first.outDir);
  assert.ok(before.some((r) => r.error?.code === 'no-reply'));
  const model = fakeModel({ ...INTAKE, ...NOT_REMOVAL });
  const again = await runJob(config, { issue: '501', resume: true }, { model, echo: false });
  assert.equal(again.ok, true, JSON.stringify(again));
  const after = callRecords(again.outDir);
  assert.deepEqual(after.slice(0, before.length), before);
  assert.equal(after.length, before.length + model.calls.length);
  assert.deepEqual(after.map((r) => r.seq), after.map((_, i) => i + 1));
});

// A job's slice runs: a snapshot per phase, and a rerun from any phase in a sandbox.

const SOURCE_JOB = 'issue-501-change-7001';

/** Every file under `dir` by relative path, with a hash of its bytes. */
function digest(dir) {
  const files = {};
  const walk = (folder) => {
    for (const entry of fs.readdirSync(folder, { withFileTypes: true })) {
      const file = path.join(folder, entry.name);
      if (entry.isDirectory()) walk(file);
      else files[path.relative(dir, file)] = crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
    }
  };
  walk(dir);
  return files;
}

/** A fixture job that ran end to end, with its queue row, ready to be run again in slices. */
async function finishedJob(overrides = {}) {
  const setup = lib({}, overrides);
  addJob(setup.config, { issue: '501', change: '7001' });
  const result = await runLib(setup);
  assert.equal(result.ok, true, JSON.stringify(result));
  return { ...setup, result };
}

test('every phase that passes leaves a snapshot, and checkpoint.json is the last one', async () => {
  const { result } = await finishedJob();
  const folder = path.join(result.outDir, 'work', 'checkpoints');
  assert.deepEqual(fs.readdirSync(folder).sort(), PHASES.map((phase) => `${phase}.json`).sort());
  for (const phase of PHASES) assert.equal(JSON.parse(read(path.join(folder, `${phase}.json`))).phase, phase);
  // The resume file is what it was before snapshots: the state after the last phase.
  assert.equal(read(path.join(result.outDir, 'work', 'checkpoint.json')), read(path.join(folder, 'phase10.json')));
  assert.deepEqual(readCheckpoint(result.outDir).phase, 'phase10');
});

test('a slice from Phase 9 revalidation runs that phase alone and leaves the job as it was', async () => {
  const marker = path.join(scratch('slice-released-'), 'marker');
  const { config, model, result } = await finishedJob({
    release: { command: [process.execPath, '-e', `require('fs').writeFileSync(${JSON.stringify(marker)}, 'x')`] } });
  // The phase's output is written by the slice, so it is absent from the job's folder before the slice runs.
  fs.rmSync(path.join(result.outDir, 'work', 'phase9-revalidation.json'));
  const before = digest(result.outDir);
  const queueBefore = read(config.at(config.queue.file));
  model.calls.length = 0;
  const slice = await rerunJob(config, { job: SOURCE_JOB, from: 'phase9-revalidate', label: 'try' },
    { model, echo: false });
  assert.equal(slice.result.ok, true, JSON.stringify(slice.result));
  assert.equal(slice.id, `${SOURCE_JOB}~try`);
  // The job's folder, its queue row and its workbook are as they were.
  assert.deepEqual(digest(result.outDir), before);
  assert.equal(read(config.at(config.queue.file)), queueBefore);
  assert.ok(fs.existsSync(result.workbook));
  // Only the revalidation ran, on the model's side and in the log.
  assert.ok(model.calls.length > 0);
  assert.ok(model.calls.every((call) => /^phase(8|9_revalidation)/.test(call.schemaName)),
    model.calls.map((call) => call.schemaName).join(' '));
  const sandbox = path.join(config.output, slice.id);
  const lines = statusLines(sandbox).filter((line) => line.job === slice.id);
  assert.deepEqual(lines.filter((line) => line.event === 'start').map((line) => line.phase), ['phase9-revalidate']);
  assert.deepEqual(lines.filter((line) => line.event === 'pass').map((line) => line.phase), ['phase9-revalidate']);
  assert.equal(lines.find((line) => line.event === 'resume').after, 'phase9-confidence');
  assert.equal(lines.at(-1).event, 'slice');
  // The sandbox holds the phase's outputs and its snapshot, the earlier snapshots, and no pack or workbook.
  assert.ok(fs.existsSync(path.join(sandbox, 'work', 'phase9-revalidation.json')));
  assert.ok(fs.existsSync(path.join(sandbox, 'work', 'checkpoints', 'phase9-revalidate.json')));
  assert.ok(fs.existsSync(path.join(sandbox, 'work', 'checkpoints', 'phase9-confidence.json')));
  assert.ok(!fs.existsSync(path.join(sandbox, 'work', 'checkpoints', 'phase10.json')));
  assert.deepEqual(fs.readdirSync(sandbox).filter((name) => !['work', 'review', 'status.log', 'detail.log'].includes(name)), []);
  // The same model gives the same pack, so the summary shows no change.
  assert.match(slice.lines[0], /^cards  source (\d+)  sandbox \1  added 0  removed 0$/);
  assert.deepEqual(slice.lines.slice(1), ['coverage  unchanged', 'confidence  unchanged High', 'revalidation  open 0 -> 0']);
  // The model was not unloaded, since the slice runs no release step.
  assert.ok(!fs.existsSync(marker));
  assertContentFree(slice.lines.join('\n'));
  // The queue is free again and the sandbox reads like a job.
  assert.equal(lockHeld(config), false);
  assert.match(jobStatus(config, slice.id)[0], new RegExp(`^${slice.id}  passed  queue free$`));
  assert.match(jobStatus(config, slice.id).join('\n'), /done phase=phase9-revalidate/);
  assert.ok(!jobStatus(config, slice.id).join('\n').includes('phase9-checklist'));
});

test('a slice of several phases runs them in order and stops after the last', async () => {
  const { config, model, result } = await finishedJob();
  model.calls.length = 0;
  const slice = await rerunJob(config, { job: SOURCE_JOB, from: 'phase9-senior', until: 'phase9-confidence' },
    { model, echo: false });
  assert.equal(slice.result.ok, true, JSON.stringify(slice.result));
  // With no label the sandbox is named by the time.
  assert.match(slice.id, new RegExp(`^${SOURCE_JOB}~\\d{8}T\\d{6}$`));
  const lines = statusLines(path.join(config.output, slice.id)).filter((line) => line.job === slice.id);
  assert.deepEqual(lines.filter((line) => line.event === 'pass').map((line) => line.phase),
    ['phase9-senior', 'phase9-confidence']);
  assert.ok(!fs.existsSync(path.join(config.output, slice.id, 'work', 'checkpoints', 'phase9-revalidate.json')));
  // Its checkpoint is where the slice ended, so a slice of the sandbox carries on from there.
  assert.equal(readCheckpoint(path.join(config.output, slice.id)).phase, 'phase9-confidence');
  assert.equal(readCheckpoint(result.outDir).phase, 'phase10');
  const next = await rerunJob(config, { job: slice.id, from: 'phase9-revalidate', label: 'next' },
    { model, echo: false });
  assert.equal(next.result.ok, true, JSON.stringify(next.result));
  assert.equal(next.id, `${slice.id}~next`);
});

test('a slice from a phase whose earlier snapshot is missing stops and names it, writing nothing', async () => {
  const { config, result } = await finishedJob();
  fs.rmSync(path.join(result.outDir, 'work', 'checkpoints', 'phase9-checklist.json'));
  const before = digest(result.outDir);
  await assert.rejects(() => rerunJob(config, { job: SOURCE_JOB, from: 'phase9-senior', label: 'gap' },
    { echo: false }), /issue-501-change-7001 has no snapshot for phase9-checklist \(work\/checkpoints\/phase9-checklist\.json\)/);
  assert.equal(fs.existsSync(path.join(config.output, `${SOURCE_JOB}~gap`)), false);
  assert.deepEqual(digest(result.outDir), before);
  assert.equal(lockHeld(config), false);
});

test('a slice refuses a job with no folder, a label already used, a phase that does not exist and a range backwards', async () => {
  const { config } = await finishedJob();
  const run = async () => { throw new Error('must not run'); };
  const attempt = (job) => rerunJob(config, job, { run });
  await assert.rejects(() => attempt({ job: 'issue-9-change-1', from: 'phase3' }), /has no output folder/);
  await assert.rejects(() => attempt({ job: SOURCE_JOB, from: 'phase99' }), /--from takes one of: intake, phase1/);
  await assert.rejects(() => attempt({ job: SOURCE_JOB, from: 'phase3', until: 'phase99' }), /--until takes one of/);
  await assert.rejects(() => attempt({ job: SOURCE_JOB, from: 'phase5', until: 'phase3' }), /--from comes after --until/);
  await assert.rejects(() => attempt({ job: SOURCE_JOB, from: 'phase3', label: 'a/b' }), /--as takes/);
  await rerunJob(config, { job: SOURCE_JOB, from: 'phase9-revalidate', label: 'used' }, { run: async () => ({ ok: true }) });
  await assert.rejects(() => attempt({ job: SOURCE_JOB, from: 'phase9-revalidate', label: 'used' }),
    /already exists; give another --as label/);
});

test('a slice from intake needs no snapshot and starts the job over in the sandbox', async () => {
  const { config, model, result } = await finishedJob();
  fs.rmSync(path.join(result.outDir, 'work', 'checkpoints'), { recursive: true });
  const slice = await rerunJob(config, { job: SOURCE_JOB, from: 'intake', until: 'phase1', label: 'fresh' },
    { model, echo: false });
  assert.equal(slice.result.ok, true, JSON.stringify(slice.result));
  const lines = statusLines(path.join(config.output, slice.id));
  assert.deepEqual(lines.filter((line) => line.event === 'pass').map((line) => line.phase), ['intake', 'phase1']);
  assert.equal(lines.at(-1).event, 'slice');
  // The sandbox's log is its own: nothing of the job's earlier run is in it.
  assert.ok(!lines.some((line) => line.event === 'resume' || line.phase === 'phase2'));
});

test('a slice holds the queue while it runs, leaves a held queue alone, and starts units again only if it stopped them', async () => {
  const { config } = await finishedJob();
  const seen = [];
  const run = async (_config, job, options) => {
    seen.push({ held: lockHeld(config), job, until: options.until });
    return { ok: true };
  };
  await rerunJob(config, { job: SOURCE_JOB, from: 'phase9-revalidate', label: 'one' }, { run });
  // The job's options come from its queue row, and the sandbox is resumed from the snapshot.
  assert.deepEqual(seen, [{ held: true, until: 'phase9-revalidate',
    job: { issue: '501', change: '7001', id: `${SOURCE_JOB}~one`, resume: true } }]);
  assert.equal(lockHeld(config), false);

  const lock = `${config.at(config.queue.file)}.lock`;
  fs.writeFileSync(lock, String(process.pid));
  assert.deepEqual(await rerunJob(config, { job: SOURCE_JOB, from: 'phase9-revalidate', label: 'two' },
    { run: async () => { throw new Error('must not run'); } }), { busy: true });
  assert.equal(fs.existsSync(path.join(config.output, `${SOURCE_JOB}~two`)), false);
  fs.rmSync(lock);

  const calls = [];
  const pauser = { pause: async () => calls.push('pause'), resume: async () => calls.push('resume') };
  await rerunJob(config, { job: SOURCE_JOB, from: 'phase9-revalidate', label: 'three', pauser }, { run });
  assert.deepEqual(calls, ['pause', 'resume']);
  calls.length = 0;
  await assert.rejects(() => rerunJob(config, { job: SOURCE_JOB, from: 'phase9-revalidate', label: 'four', pauser },
    { run: async () => { throw new Error('model down'); } }), /model down/);
  assert.deepEqual(calls, ['pause', 'resume']);
  assert.equal(lockHeld(config), false);
  // A run that threw before it wrote a line leaves the job's copied lines behind; the sandbox still reads as failed
  // and lists none of the phases the job passed.
  assert.equal(jobStatus(config, `${SOURCE_JOB}~four`)[0], `${SOURCE_JOB}~four  failed  queue free`);
  assert.ok(!jobStatus(config, `${SOURCE_JOB}~four`).some((line) => line.startsWith('done phase=')));
});

test('a slice takes its job options from the queue row, else from the job ID, and a sandbox of a sandbox finds the same row', async () => {
  const { config } = await finishedJob();
  const queue = readQueue(config);
  Object.assign(queue.jobs[0], { docs: ['docs/LIB/UC01-Card-Renewal.md'], allowDerivedRules: true, status: 'passed',
    workbook: 'x.xlsx', phase: 'done' });
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
  const seen = [];
  const run = async (_config, job) => { seen.push(job); return { ok: true }; };
  const slice = (job, label) => rerunJob(config, { job, from: 'phase9-revalidate', label }, { run });
  await slice(SOURCE_JOB, 'a');
  assert.deepEqual(seen[0], { issue: '501', change: '7001', docs: ['docs/LIB/UC01-Card-Renewal.md'],
    allowDerivedRules: true, id: `${SOURCE_JOB}~a`, resume: true });
  // A slice of a sandbox reads the folder of the sandbox and the row of the job.
  fs.cpSync(path.join(config.output, SOURCE_JOB), path.join(config.output, `${SOURCE_JOB}~a`), { recursive: true });
  await slice(`${SOURCE_JOB}~a`, 'b');
  assert.equal(seen[1].id, `${SOURCE_JOB}~a~b`);
  assert.equal(seen[1].allowDerivedRules, true);
  // A job with no row, as one run by hand has, is read from its ID.
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify({ jobs: [] }));
  await slice(SOURCE_JOB, 'c');
  assert.deepEqual(seen[2], { issue: '501', change: '7001', id: `${SOURCE_JOB}~c`, resume: true });
  fs.cpSync(path.join(config.output, SOURCE_JOB), path.join(config.output, 'suite-LIB'), { recursive: true });
  await slice('suite-LIB', 'd');
  assert.deepEqual(seen[3], { suite: 'LIB', id: 'suite-LIB~d', resume: true });
});

test('queue status reads a sandbox that failed from its own log, not the job\'s lines before the slice', async () => {
  const { config } = await finishedJob();
  const failing = async (_config, job) => {
    const logs = jobLogs(path.join(config.output, job.id), { echo: false });
    logs.status({ job: job.id, phase: 'phase9-revalidate', event: 'resume', after: 'phase9-confidence' });
    logs.status({ job: job.id, phase: 'phase9-revalidate', event: 'start' });
    logs.status({ job: job.id, phase: 'phase9-revalidate', event: 'fail', reason: 'gate:revalidation-failed', ms: 5 });
    return { ok: false, phase: 'phase9-revalidate' };
  };
  const slice = await rerunJob(config, { job: SOURCE_JOB, from: 'phase9-revalidate', label: 'bad' }, { run: failing });
  assert.equal(slice.result.ok, false);
  assert.deepEqual(slice.lines, []);
  const status = jobStatus(config, slice.id);
  assert.equal(status[0], `${slice.id}  failed  queue free`);
  assert.ok(status.includes('stopped phase=phase9-revalidate reason=gate:revalidation-failed'), status.join('\n'));
  // The source job's phases, copied into the sandbox's log, are not the slice's.
  assert.ok(!status.some((line) => line.startsWith('done phase=phase1 ')), status.join('\n'));
  assert.deepEqual(jobStatus(config, 'issue-9-change-1~nothing'), ['issue-9-change-1~nothing  not queued  queue free']);
  // A stop on request reads stopped, as a queue row does.
  const cancelled = async (_config, job) => {
    jobLogs(path.join(config.output, job.id), { echo: false })
      .status({ job: job.id, phase: 'phase9-revalidate', event: 'fail', reason: 'cancelled', ms: 5 });
    return { ok: false, phase: 'phase9-revalidate', reason: 'cancelled' };
  };
  const stop = await rerunJob(config, { job: SOURCE_JOB, from: 'phase9-revalidate', label: 'stop' }, { run: cancelled });
  assert.equal(jobStatus(config, stop.id)[0], `${stop.id}  stopped  queue free`);
});

test('a slice\'s summary lists what changed against the job\'s snapshot, with counts and codes only', () => {
  const { config } = lib();
  const snapshot = (job, pack) => {
    const folder = path.join(config.output, job, 'work', 'checkpoints');
    fs.mkdirSync(folder, { recursive: true });
    fs.writeFileSync(path.join(folder, 'phase9-revalidate.json'),
      JSON.stringify({ phase: 'phase9-revalidate', state: { pack } }));
  };
  snapshot('src', { testCards: [{ id: 'TC-A-001' }, { id: 'TC-A-002' }, { id: 'TC-A-003' }],
    coverage: [{ status: 'Covered' }, { status: 'Covered' }, { status: 'Missing' }], confidence: { overall: 'High' } });
  snapshot('sbx', { testCards: [{ id: 'TC-A-001' }, { id: 'TC-A-002' }, { id: 'TC-A-004' }, { id: 'TC-A-005' }],
    coverage: [{ status: 'Covered' }, { status: 'Partially Covered' }, { status: 'Covered' }],
    confidence: { overall: 'Low' }, revalidation: { passed: false, remaining: ['Item one', 'Item two'] } });
  const { lines, detail } = compareSnapshots(path.join(config.output, 'src'), path.join(config.output, 'sbx'),
    'phase9-revalidate');
  assert.deepEqual(lines, [
    'cards  source 3  sandbox 4  added 2  removed 1',
    'coverage  Missing 1 -> 0  Partially Covered 0 -> 1',
    'confidence  High -> Low',
    'revalidation  open 0 -> 2',
  ]);
  // The card IDs and the open items stay out of the console lines.
  assert.deepEqual(detail, { phase: 'phase9-revalidate', cardsAdded: ['TC-A-004', 'TC-A-005'],
    cardsRemoved: ['TC-A-003'], openBefore: [], openAfter: ['Item one', 'Item two'] });
  assert.ok(!lines.join('\n').includes('TC-A') && !lines.join('\n').includes('Item'));
  assert.deepEqual(compareSnapshots(path.join(config.output, 'src'), path.join(config.output, 'sbx'), 'phase10').lines,
    ['sandbox has no snapshot at phase10; nothing to compare']);
  fs.rmSync(path.join(config.output, 'src', 'work'), { recursive: true });
  assert.deepEqual(compareSnapshots(path.join(config.output, 'src'), path.join(config.output, 'sbx'),
    'phase9-revalidate').lines, ['source has no snapshot at phase9-revalidate; nothing to compare']);
});

test('the command line runs a slice, and refuses slice options without --job and job options with it', async () => {
  const { config, result } = await finishedJob();
  const cli = (...args) => spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'run', ...args,
    '--config', config.file], { encoding: 'utf8' });
  assert.deepEqual(parseArgs(['run', '--job', 'x', '--from', 'p', '--until', 'q', '--as', 'l', '--pause']),
    { docs: [], words: ['run'], job: 'x', from: 'p', until: 'q', as: 'l', pause: true });
  const sliceOnly = cli('--issue', '501', '--from', 'phase3');
  assert.equal(sliceOnly.status, 2);
  assert.match(sliceOnly.stderr, /--from goes with --job/);
  const both = cli('--job', SOURCE_JOB, '--issue', '501', '--from', 'phase3');
  assert.equal(both.status, 2);
  assert.match(both.stderr, /--job names the job/);
  assert.match(cli('--job', SOURCE_JOB).stderr, /--from takes a phase/);
  assert.match(cli('--job', '../x', '--from', 'phase3').stderr, /--job takes a job ID/);
  const gone = cli('--job', 'issue-9-change-1', '--from', 'phase3');
  assert.equal(gone.status, 2);
  assert.match(gone.stderr, /issue-9-change-1 has no output folder/);
  // A queue held by a live process makes the slice wait for another try, and writes nothing.
  const lock = `${config.at(config.queue.file)}.lock`;
  fs.writeFileSync(lock, String(process.pid));
  const busy = cli('--job', SOURCE_JOB, '--from', 'phase9-senior', '--as', 'cli');
  fs.rmSync(lock);
  assert.equal(busy.status, 1);
  assert.match(busy.stderr, /the queue is running/);
  assert.equal(fs.existsSync(path.join(config.output, `${SOURCE_JOB}~cli`)), false);
  assert.ok(fs.existsSync(result.workbook));
});

// A job's single steps: one part of Phase 9 on its own, in a sandbox, over a snapshot or an earlier step's state.

const slurp = (file) => fs.readFileSync(file, 'utf8');
/** The pack a step state or a snapshot holds. */
const savedPack = (saved) => saved.pack ?? saved.state.pack;
/** Rewrites the job's snapshot of `phase` through `change`, to set a state up. */
const editSnapshot = (outDir, phase, change) => {
  const file = path.join(outDir, 'work', 'checkpoints', `${phase}.json`);
  const saved = JSON.parse(slurp(file));
  change(saved);
  fs.writeFileSync(file, JSON.stringify(saved));
};
const walkFailsOnCard = { phase9_revalidation: (value, calls) => failCheck(value, 'Traceability complete',
  `${cardIdIn(calls.at(-1).user)} reads wrong`, `Change step 1 of ${cardIdIn(calls.at(-1).user)} to read Corrected step`) };
const repairsStepOne = { phase8_repair: (value) => ({ ...correctingRepair(value),
  cards: correctingRepair(value).cards.map((card) => ({ ...card,
    steps: card.steps.map((one, i) => (i ? one : { ...one, description: 'Repaired by the step' })) })) }) };
const step = (config, options, run) => stepJob(config, { job: SOURCE_JOB, ...options }, run);

test('the draft step writes the Draft workbook with no model and prints the builder\'s sheet results', async () => {
  const { config, result } = await finishedJob();
  const before = digest(result.outDir);
  const held = [];
  const done = await step({ ...config, model: undefined }, { at: 'phase9-revalidate', step: 'draft', label: 'draft' },
    { run: (...args) => { held.push(lockHeld(config)); return runStep(...args); } });
  assert.equal(done.id, `${SOURCE_JOB}~draft`);
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  assert.equal(done.result.failed, false);
  assert.match(done.result.report.join('\n'), /^PASS +Dashboard$/m);
  assert.ok(done.result.report.every((line) => /^(PASS|FAIL)/.test(line)));
  const sandbox = path.join(config.output, done.id);
  assert.ok(fs.readdirSync(path.join(sandbox, 'work', 'review')).some((name) => name.endsWith('.xlsx')));
  // No model call was made, so the sandbox holds no call records, and a builder step never takes the queue.
  assert.equal(fs.existsSync(path.join(sandbox, 'work', 'calls')), false);
  assert.deepEqual(held, [false]);
  assert.deepEqual(done.result.lines.map((line) => JSON.parse(line).event), ['begin', 'step']);
  assert.equal(JSON.parse(done.result.lines.at(-1)).calls, 0);
  assertContentFree(done.result.lines.join('\n'));
  assert.equal(jobStatus(config, done.id)[0], `${done.id}  passed  queue free`);
  assert.deepEqual(digest(result.outDir), before);
});

test('the draft step prints the builder\'s lines when a sheet fails and the builder writes no workbook', async () => {
  const { config, result } = await finishedJob();
  editSnapshot(result.outDir, 'phase9-revalidate', (saved) => { savedPack(saved).testCards[0].title = 'REJECT'; });
  const done = await step(config, { at: 'phase9-revalidate', step: 'draft', label: 'draft' });
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  assert.equal(done.result.failed, true);
  assert.match(done.result.report.join('\n'), /^FAIL +Test Cards Markdown$/m);
  assert.match(done.result.report.join('\n'), /^no workbook was written \(builder exit 1\)$/m);
  assert.equal(JSON.parse(done.result.lines.at(-1)).sheetsFail, 1);
});

test('the build step prints every sheet\'s status without repairing, and a failing sheet makes the step fail', async () => {
  const { config, result } = await finishedJob();
  editSnapshot(result.outDir, 'phase9-revalidate', (saved) => { savedPack(saved).testCards[0].title = 'REJECT'; });
  const before = digest(result.outDir);
  const done = await step(config, { at: 'phase9-revalidate', step: 'build', label: 'build' });
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  assert.equal(done.result.failed, true);
  assert.match(done.result.report.join('\n'), /^FAIL +Test Cards Markdown$/m);
  assert.match(done.result.report.join('\n'), /^PASS +Dashboard$/m);
  const sandbox = path.join(config.output, done.id);
  assert.equal(JSON.parse(done.result.lines.at(-1)).sheetsFail, 1);
  // The rejected title is still there: the step asks no model to repair it.
  assert.equal(savedPack(readStep(sandbox)).testCards[0].title, 'REJECT');
  assert.deepEqual(digest(result.outDir), before);
});

test('a build step before the review leaves the review sheets out of the failures, and after it counts them', async () => {
  const { config, result } = await finishedJob();
  const blank = (saved) => { savedPack(saved).testerNotes = ''; };
  for (const phase of ['phase8', 'phase9-checklist', 'phase9-revalidate']) editSnapshot(result.outDir, phase, blank);
  const early = await step(config, { at: 'phase8', step: 'build', label: 'early' });
  assert.equal(early.result.failed, false);
  assert.match(early.result.report.join('\n'), /^DEFERRED +Tester Notes$/m);
  const checked = await step(config, { at: 'phase9-checklist', step: 'build', label: 'checked' });
  assert.equal(checked.result.failed, false);
  assert.match(checked.result.report.join('\n'), /^DEFERRED +Tester Notes$/m);
  const late = await step(config, { at: 'phase9-revalidate', step: 'build', label: 'late' });
  assert.equal(late.result.failed, true);
  assert.match(late.result.report.join('\n'), /^FAIL +Tester Notes$/m);
});

test('a repair step repairs one finding of the snapshot\'s revalidation in the sandbox and leaves the job as it was', async () => {
  const setup = lib({ ...walkFailsOnCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  const failed = await runLib(setup);
  assert.equal(failed.reason, 'gate:revalidation-failed');
  const { config } = setup;
  const before = digest(failed.outDir);
  const model = fakeModel(repairsStepOne);
  const done = await step(config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'fix' }, { model });
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  assert.match(done.result.report[0], /^repaired finding 0 {2}Traceability complete$/);
  const sandbox = path.join(config.output, done.id);
  const repaired = savedPack(readStep(sandbox));
  assert.ok(repaired.testCards.some((card) => card.steps[0].description === 'Repaired by the step'));
  // The repair round's own rebuild passed, so the pack no longer claims a failed revalidation.
  assert.equal(repaired.revalidation, undefined);
  assert.equal(model.calls.filter((c) => c.schemaName.startsWith('phase8_repair')).length, 1);
  assert.ok(!JSON.parse(slurp(path.join(failed.outDir, 'work', 'checkpoints', 'phase9-revalidate.json')))
    .state.pack.testCards.some((card) => card.steps[0].description === 'Repaired by the step'));
  // A repaired card keeps the kind Phase 7 gave it, and the repair is not shown it.
  const fixed = repaired.testCards.find((card) => card.steps[0].description === 'Repaired by the step');
  const snapshot = savedPack(JSON.parse(slurp(path.join(failed.outDir, 'work', 'checkpoints', 'phase9-revalidate.json'))));
  assert.ok(fixed.kind);
  assert.equal(fixed.kind, snapshot.testCards.find((card) => card.id === fixed.id).kind);
  const asked = model.calls.find((c) => c.schemaName.startsWith('phase8_repair')).user;
  assert.ok(asked.includes('"derivation"') && !asked.includes('"kind"'));
  assert.deepEqual(digest(failed.outDir), before);
  assertContentFree(done.result.lines.join('\n'));
});

// A revalidation finding that asks for a new card for a rule no card covers.
const asksNewCard = { phase9_revalidation: (value) => failCheck(value, 'Traceability complete',
  'BR-LIB.UC01-001 has no card', 'Create a new test card for BR-LIB.UC01-001') };
const newCardFor = (value, calls) => {
  const item = S.propOf(calls.at(-1).schema, 'newCards').items;
  return { ...value, coverage: [], limitations: [], cards: [],
    newCards: [{ title: 'New card', mission: 'Cover the rule', focus: ['focus'], expected: 'expected value',
      rules: ['BR-LIB.UC01-001'], objectives: [S.propOf(item, 'objectives').items.enum[0]],
      derivation: S.propOf(item, 'derivation').enum[0],
      steps: [{ description: 'Do it', expected: 'expected value', rules: ['BR-LIB.UC01-001'] }] }] };
};

/** Leaves the rule no card, with the Missing row Phase 7 writes for it, in the snapshot. */
const uncover = (outDir, rule, phase = 'phase9-revalidate') => editSnapshot(outDir, phase, (saved) => {
  const pack = savedPack(saved);
  pack.testCards = pack.testCards.filter((card) => card.rules.some((id) => id !== rule));
  for (const card of pack.testCards) {
    card.rules = card.rules.filter((id) => id !== rule);
    for (const one of card.steps) one.rules = one.rules.filter((id) => id !== rule);
  }
  for (const set of pack.testSets) set.cards = set.cards.filter((id) => pack.testCards.some((c) => c.id === id));
  pack.coverage = [...pack.coverage.filter((row) => row.ruleId !== rule),
    { ruleId: rule, status: 'Missing', strength: 'None', gap: 'No card covers this rule.', recommendation: 'Add a card.' }];
});

test('a repair builds the new card a revalidation finding asks for, so the rule is covered', async () => {
  const setup = lib({ ...asksNewCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  const failed = await runLib(setup);
  const { config } = setup;
  uncover(failed.outDir, 'BR-LIB.UC01-001');
  const before = savedPack(JSON.parse(slurp(path.join(failed.outDir, 'work', 'checkpoints', 'phase9-revalidate.json'))));
  const done = await step(config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'new' },
    { model: fakeModel({ phase8_repair: newCardFor }) });
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  const pack = savedPack(readStep(path.join(config.output, done.id)));
  const added = pack.testCards.filter((card) => !before.testCards.some((old) => old.id === card.id));
  assert.equal(added.length, 1);
  assert.match(added[0].id, /^TC-MOD-501-\d{3}$/);
  assert.deepEqual(added[0].rules, ['BR-LIB.UC01-001']);
  assert.equal(added[0].kind, 'decision');
  assert.ok(pack.testSets.some((set) => set.cards.includes(added[0].id)));
  assert.ok(!pack.coverage.some((row) => row.ruleId === 'BR-LIB.UC01-001' && row.status === 'Missing'));
});

const missingRow = (ruleId) => ({ ruleId, status: 'Missing', strength: 'None', gap: 'No card covers this rule.',
  recommendation: 'Add a card.' });
const rejectsAll = (value) => ({ ...value, cards: Object.fromEntries(Object.keys(value.cards).map((label) => [label,
  { why: 'The Expected Result contradicts the rule.', verdict: 'does not follow' }])) });

test('a new card dropped as unsound is left out and clears no Missing row', async () => {
  const setup = lib({ ...asksNewCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  const failed = await runLib(setup);
  uncover(failed.outDir, 'BR-LIB.UC01-001');
  const before = savedPack(JSON.parse(slurp(path.join(failed.outDir, 'work', 'checkpoints', 'phase9-revalidate.json'))));
  const done = await step(setup.config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'unsound' },
    { model: fakeModel({ phase8_repair: newCardFor, phase6_recheck: rejectsAll }) });
  const pack = savedPack(readStep(path.join(setup.config.output, done.id)));
  const added = pack.testCards.filter((card) => !before.testCards.some((old) => old.id === card.id));
  assert.equal(added.length, 0);
  assert.ok(!pack.testSets.some((set) => set.cards.some((id) => !pack.testCards.some((card) => card.id === id))));
  assert.ok(pack.coverage.some((row) => row.ruleId === 'BR-LIB.UC01-001' && row.status === 'Missing'));
});

test('a new card dropped as unsound clears no Not Applicable row the reply returns for its rule', async () => {
  const setup = lib({ ...asksNewCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  const failed = await runLib(setup);
  const rule = 'BR-LIB.UC01-001';
  uncover(failed.outDir, rule);
  // A limitation lets the rebuilt workbook pass with the rule uncovered.
  editSnapshot(failed.outDir, 'phase9-revalidate', (saved) => {
    savedPack(saved).limitations = { ...savedPack(saved).limitations, 'Coverage Matrix': `${rule} has no card.` };
  });
  const notApplicable = { ruleId: rule, status: 'Not Applicable', strength: 'None',
    gap: 'The change does not touch this rule.', recommendation: 'None.' };
  const reply = (value, calls) => ({ ...newCardFor(value, calls), coverage: [notApplicable] });
  const done = await step(setup.config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'kept' },
    { model: fakeModel({ phase8_repair: reply, phase6_recheck: rejectsAll }) });
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  const pack = savedPack(readStep(path.join(setup.config.output, done.id)));
  assert.ok(!pack.testCards.some((card) => card.id.endsWith('-003')));
  assert.equal(pack.coverage.find((row) => row.ruleId === rule)?.status, 'Not Applicable');
});

test('a reply with a new card and a Missing row for the same rule ends with the row cleared', async () => {
  const setup = lib({ ...asksNewCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  const failed = await runLib(setup);
  const rule = 'BR-LIB.UC01-001';
  uncover(failed.outDir, rule);
  // The fix round takes the new card; the reply still returns the Missing row for its rule.
  const stale = (value, calls) => ({ ...newCardFor(value, calls), coverage: [missingRow(rule)] });
  const done = await step(setup.config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'row' },
    { model: fakeModel({ phase8_repair: stale }) });
  const pack = savedPack(readStep(path.join(setup.config.output, done.id)));
  assert.ok(pack.testCards.some((card) => card.rules.includes(rule) && card.id.endsWith('-003')));
  assert.ok(!pack.coverage.some((row) => row.ruleId === rule && row.status === 'Missing'));
});

test('a Phase 8 builder-failure repair offers no new cards', async () => {
  const setup = lib({ ...asksNewCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  await runLib(setup);
  const rule = 'BR-LIB.UC01-001';
  // A Missing row for a rule the cards cite fails the builder, so Phase 8 repairs the sheet.
  const run = async (cfg, parameters, options) => {
    const file = path.join(cfg.output, parameters.id, 'work', 'checkpoint.json');
    const saved = JSON.parse(slurp(file));
    const pack = savedPack(saved);
    pack.coverage = [...pack.coverage.filter((row) => row.ruleId !== rule), missingRow(rule)];
    fs.writeFileSync(file, JSON.stringify(saved));
    const model = fakeModel({ ...INTAKE, ...NOT_REMOVAL });
    const result = await runJob(cfg, parameters, { ...options, model, echo: false });
    calls.push(...model.calls);
    return result;
  };
  const calls = [];
  await rerunJob(setup.config, { job: 'issue-501-change-7001', from: 'phase9-revalidate', label: 'p8' }, { run });
  const repairs = calls.filter((call) => call.schemaName.startsWith('phase8_repair'));
  assert.ok(repairs.length >= 1);
  assert.ok(repairs.every((call) => call.schema.properties.newCards.maxItems === 0));
});

test('a repair takes no more new cards than the schema allows', async () => {
  const setup = lib({ ...asksNewCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  const failed = await runLib(setup);
  uncover(failed.outDir, 'BR-LIB.UC01-001');
  const before = savedPack(JSON.parse(slurp(path.join(failed.outDir, 'work', 'checkpoints', 'phase9-revalidate.json'))));
  const many = (value, calls) => {
    const one = newCardFor(value, calls);
    return { ...one, newCards: Array.from({ length: S.NEW_CARDS_MAX + 2 }, () => one.newCards[0]) };
  };
  const done = await step(setup.config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'many' },
    { model: fakeModel({ phase8_repair: many }) });
  const pack = savedPack(readStep(path.join(setup.config.output, done.id)));
  assert.equal(pack.testCards.length - before.testCards.length, S.NEW_CARDS_MAX);
});

/** Reruns the revalidation of `job` over a pack with `rule` left without a card, on `model`. */
async function rerunUncovered(config, job, rule, model, limited = true) {
  const run = async (cfg, parameters, options) => {
    const where = path.join(cfg.output, parameters.id);
    // The resume reads work/checkpoint.json; the limitation lets the rebuilt workbook pass with the rule uncovered.
    uncover(where, rule, 'phase9-confidence');
    const file = path.join(where, 'work', 'checkpoint.json');
    fs.copyFileSync(path.join(where, 'work', 'checkpoints', 'phase9-confidence.json'), file);
    const saved = JSON.parse(slurp(file));
    if (limited) savedPack(saved).limitations = { ...savedPack(saved).limitations, 'Coverage Matrix': `${rule} has no card.` };
    fs.writeFileSync(file, JSON.stringify(saved));
    return runJob(cfg, parameters, { ...options, model, echo: false });
  };
  const { id } = await rerunJob(config, { job, from: 'phase9-revalidate', label: 'u' }, { run });
  return path.join(config.output, id);
}

test('a revalidation item whose repair produced no card says so', async () => {
  const setup = lib({ ...asksNewCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  await runLib(setup);
  const sandbox = await rerunUncovered(setup.config, 'issue-501-change-7001', 'BR-LIB.UC01-001', setup.model);
  const { remaining } = JSON.parse(slurp(path.join(sandbox, 'work', 'phase9-revalidation.json')));
  assert.ok(remaining.some((line) => line.endsWith('(repair produced no card)')), remaining.join('\n'));
});

test('a suite pack refuses a new card and logs why', async () => {
  const model = fakeModel({ ...INTAKE, ...NOT_REMOVAL });
  const config = fixtureConfig();
  const first = await runJob(config, { suite: 'LIB' }, { model, echo: false });
  assert.equal(first.ok, true, JSON.stringify(first));
  const pack = JSON.parse(read(first.packPath));
  const rule = pack.rules[0].id;
  const asks = fakeModel({ ...INTAKE, ...NOT_REMOVAL, phase9_revalidation: (value) => failCheck(value,
    'Traceability complete', `${rule} has no card`, `Create a new test card for ${rule}`),
  phase8_repair: correctingRepair });
  const sandbox = await rerunUncovered(config, 'suite-LIB', rule, asks);
  assert.match(slurp(path.join(sandbox, 'status.log')), /new-card-refused-suite/);
});

test('the repair schema offers new cards only for named rules and never in a suite pack', async () => {
  const { repairSchema } = S;
  const base = { cardIds: [], ids: ['R1', 'R2'], objectives: ['O'], derivations: ['Requirement'],
    statuses: ['Covered'], sheets: ['Coverage Matrix'] };
  const open = repairSchema({ ...base, newIds: ['R1'] }).properties.newCards;
  assert.equal(open.maxItems, S.NEW_CARDS_MAX);
  assert.deepEqual(S.propOf(open.items, 'rules').items.enum, ['R1']);
  assert.equal(repairSchema(base).properties.newCards.maxItems, 0);
});

test('a repair that returns no card for a rule left without one is logged as not applied', async () => {
  const setup = lib({ ...asksNewCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  const failed = await runLib(setup);
  uncover(failed.outDir, 'BR-LIB.UC01-001');
  const done = await step(setup.config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'none' },
    { model: fakeModel({ phase8_repair: correctingRepair }) });
  const status = slurp(path.join(setup.config.output, done.id, 'status.log'));
  assert.match(status, /repair-not-applied/);
  assert.match(status, /no-card/);
});

test('a fix that edits an existing card is not reported as a missing new card', async () => {
  const rule = 'BR-LIB.UC01-001';
  const names = { phase9_revalidation: (value, calls) => failCheck(value, 'Traceability complete',
    `${cardIdIn(calls.at(-1).user)} reads wrong`,
    `Add a new step to card ${cardIdIn(calls.at(-1).user)} so it covers ${rule}`) };
  const setup = lib({ ...names, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  const failed = await runLib(setup);
  // The rule has no card, and the fix names a card and the rule: it edits the card.
  uncover(failed.outDir, rule);
  const done = await step(setup.config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'edit' },
    { model: fakeModel({ phase8_repair: (value) => { // the edit leaves the rule uncovered
      const fixed = correctingRepair(value);
      return { ...fixed, cards: fixed.cards.map((card) => ({ ...card,
        rules: card.rules.filter((id) => id !== rule) })) };
    } }) });
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  assert.doesNotMatch(slurp(path.join(setup.config.output, done.id, 'status.log')), /repair-not-applied/);
});

test('a rule ID is matched whole, so BR-1 does not open new cards for BR-10', () => {
  assert.equal(citesId('BR-10 has no card', 'BR-1'), false);
  assert.equal(citesId('BR-1 has no card', 'BR-1'), true);
});

test('a build step at a failed revalidation reads the builder without the verdict, and a state with no verdicts takes them from the revalidation file', async () => {
  const setup = lib({ ...walkFailsOnCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  const failed = await runLib(setup);
  assert.equal(failed.reason, 'gate:revalidation-failed');
  const { config } = setup;
  const built = await step(config, { at: 'phase9-revalidate', step: 'build', label: 'build' });
  assert.equal(built.result.failed, false, built.result.report.join('\n'));
  assert.match(built.result.report.join('\n'), /^PASS +Workbook Validation$/m);
  // The verdict stays in the saved state for the steps after.
  assert.equal(savedPack(readStep(path.join(config.output, built.id))).revalidation.passed, false);
  // A snapshot whose state holds no verdicts takes them from the revalidation's file.
  editSnapshot(failed.outDir, 'phase9-revalidate', (saved) => { delete saved.state.revalidationChecks; });
  const older = await step(config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'older' },
    { model: fakeModel(repairsStepOne) });
  assert.equal(older.result.ok, true, JSON.stringify(older.result));
  assert.ok(savedPack(readStep(path.join(config.output, older.id))).testCards
    .some((card) => card.steps[0].description === 'Repaired by the step'));
  const seeded = await step(config, { at: 'phase9-revalidate', step: 'walk', check: 'traceability', label: 'seeded' },
    { model: fakeModel(walkFailsOnCard) });
  assert.equal(seeded.result.ok, true, JSON.stringify(seeded.result));
  assert.equal(readStep(path.join(config.output, seeded.id)).state.revalidationChecks.length, 7);
  // With no file either, a partial walk cannot say what the other checks read.
  fs.rmSync(path.join(failed.outDir, 'work', 'phase9-revalidation.json'));
  const model = fakeModel();
  const one = await step(config, { at: 'phase9-revalidate', step: 'walk', check: 'traceability', label: 'one' }, { model });
  assert.equal(one.result.ok, false);
  assert.match(one.result.report[0], /walk all seven first/);
  assert.equal(model.calls.length, 0);
});

test('a step that cannot set up its context logs a fail line, so the sandbox does not read as running', async () => {
  const { config } = await finishedJob();
  const broken = { ...config, builder: { ...config.builder, module: 'fixtures/missing-builder.mjs' } };
  const done = await step(broken, { at: 'phase9-revalidate', step: 'draft', label: 'broken' });
  assert.equal(done.result.ok, false);
  assert.equal(statusLines(path.join(config.output, done.id)).at(-1).event, 'fail');
  assert.equal(jobStatus(config, done.id)[0], `${done.id}  failed  queue free`);
});

test('a walk of some checks before any full walk records those verdicts and leaves the pack\'s revalidation alone', async () => {
  const { config, result } = await finishedJob();
  const one = await step(config, { at: 'phase9-confidence', step: 'walk', check: 'traceability', label: 'one' },
    { model: fakeModel(walkFailsOnCard) });
  assert.equal(one.result.ok, true, JSON.stringify(one.result));
  assert.match(one.result.report.join('\n'), /^fail +Traceability complete$/m);
  const saved = readStep(path.join(config.output, one.id));
  assert.deepEqual(saved.state.revalidationChecks.map((row) => row.check), ['Traceability complete']);
  assert.equal(savedPack(saved).revalidation, undefined);
  const file = (dir) => slurp(path.join(dir, 'work', 'phase9-revalidation.json'));
  assert.equal(file(path.join(config.output, one.id)), file(result.outDir));
});

test('a walk step names the findings, and a repair step starts from the sandbox the walk left', async () => {
  const { config, result } = await finishedJob();
  const before = digest(result.outDir);
  const model = fakeModel({ ...walkFailsOnCard, ...repairsStepOne });
  const walked = await step(config, { at: 'phase9-confidence', step: 'walk', label: 'walk' }, { model });
  assert.equal(walked.result.ok, true, JSON.stringify(walked.result));
  const report = walked.result.report.join('\n');
  assert.match(report, /^fail +Traceability complete$/m);
  assert.match(report, /^finding 0 {2}Traceability complete$/m);
  assert.equal(walked.result.report.filter((line) => line.startsWith('pass')).length, 6);
  const repaired = await step(config, { at: walked.id, step: 'repair', finding: '0', label: 'fix' }, { model });
  assert.equal(repaired.id, `${walked.id}~fix`);
  assert.equal(repaired.result.ok, true, JSON.stringify(repaired.result));
  assert.ok(savedPack(readStep(path.join(config.output, repaired.id))).testCards
    .some((card) => card.steps[0].description === 'Repaired by the step'));
  assert.ok(!savedPack(readStep(path.join(config.output, walked.id))).testCards
    .some((card) => card.steps[0].description === 'Repaired by the step'));
  assert.deepEqual(digest(result.outDir), before);
});

test('a walk of named checks asks for those only and keeps the earlier verdicts of the others', async () => {
  const { config } = await finishedJob();
  const full = await step(config, { at: 'phase9-confidence', step: 'walk', label: 'full' },
    { model: fakeModel(walkFailsOnCard) });
  const model = fakeModel();
  const one = await step(config, { at: full.id, step: 'walk', check: 'traceability', label: 'one' }, { model });
  assert.equal(one.result.ok, true, JSON.stringify(one.result));
  assert.deepEqual(Object.keys(model.calls[0].schema.properties.checks.properties), ['Traceability complete']);
  assert.match(one.result.report[0], /^pass +Traceability complete$/);
  // The other six verdicts stand from the full walk, so nothing is open and the pack carries no failed revalidation.
  const saved = readStep(path.join(config.output, one.id));
  assert.deepEqual(saved.state.revalidationChecks.map((row) => row.verdict), Array(7).fill('pass'));
  assert.equal(savedPack(saved).revalidation?.passed ?? true, true);
  const last = JSON.parse(one.result.lines.at(-1));
  assert.deepEqual([last.failedChecks, last.open], [0, 0]);
});

test('the confidence step writes one field or rates the overall level, and counts the Coverage field in code', async () => {
  const { config, result } = await finishedJob();
  const before = digest(result.outDir);
  const model = fakeModel();
  const coverage = await step(config, { at: 'phase9-revalidate', step: 'confidence', field: 'coverage', label: 'cov' }, { model });
  assert.equal(coverage.result.ok, true, JSON.stringify(coverage.result));
  assert.equal(model.calls.length, 0);
  const field = await step(config, { at: 'phase9-revalidate', step: 'confidence', field: 'remainingRisks', label: 'field' },
    { model });
  assert.equal(field.result.ok, true, JSON.stringify(field.result));
  assert.equal(model.calls.length, 1);
  const overall = await step(config, { at: 'phase9-revalidate', step: 'confidence', label: 'overall' }, { model });
  assert.equal(overall.result.ok, true, JSON.stringify(overall.result));
  assert.equal(model.calls.length, 2);
  const level = savedPack(readStep(path.join(config.output, overall.id))).confidence.overall;
  assert.equal(overall.result.report[0], `overall ${level}`);
  assert.deepEqual(digest(result.outDir), before);
});

test('a checklist step reads the built workbook and counts what it found', async () => {
  const { config, result } = await finishedJob();
  const before = digest(result.outDir);
  const model = fakeModel({ phase9_checklist: plantedChecklist(), phase8_repair: correctingRepair });
  const done = await step(config, { at: 'phase8', step: 'checklist', label: 'check' }, { model });
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  assert.match(done.result.report[0], /^issues \d+ {2}coverageRows \d+ {2}fixRounds \d+$/);
  assert.ok(model.calls.some((c) => c.schemaName.startsWith('phase9_checklist')));
  assert.deepEqual(digest(result.outDir), before);
});

test('a step the state cannot serve stops with a fail line and the message, and leaves the state as it was', async () => {
  const { config, result } = await finishedJob();
  const model = fakeModel(walkFailsOnCard);
  const walked = await step(config, { at: 'phase9-confidence', step: 'walk', label: 'walk' }, { model });
  const sandbox = path.join(config.output, walked.id);
  const state = slurp(path.join(sandbox, 'work', 'step.json'));
  const out = await step(config, { at: walked.id, step: 'repair', finding: '5', label: 'range' }, { model });
  assert.equal(out.result.ok, false);
  assert.equal(out.result.report.length, 1);
  assert.match(out.result.report[0], /^--finding 5 /);
  assert.equal(statusLines(path.join(config.output, out.id)).at(-1).reason, 'step-input');
  assert.equal(slurp(path.join(config.output, out.id, 'work', 'step.json')), state);
  assert.equal(jobStatus(config, out.id)[0], `${out.id}  failed  queue free`);
  // A snapshot from before any walk, with no revalidation file beside it, holds no verdicts to repair from.
  editSnapshot(result.outDir, 'phase9-revalidate', (saved) => { delete saved.state.revalidationChecks; });
  fs.rmSync(path.join(result.outDir, 'work', 'phase9-revalidation.json'));
  const none = await step(config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'none' }, { model });
  assert.match(none.result.report[0], /run the walk step first/);
});

test('a step refuses a wrong option, a missing snapshot and a sandbox it cannot start from, writing nothing', async () => {
  const { config, result } = await finishedJob();
  assert.deepEqual(checkStep({ step: 'walk', check: 'all issues, Traceability Complete' }),
    { step: 'walk', checks: ['All issues resolved', 'Traceability complete'] });
  assert.deepEqual(checkStep({ step: 'repair', finding: '0' }), { step: 'repair', finding: 0 });
  assert.throws(() => checkStep({ step: 'nap' }), /a step is one of: draft, build, checklist, walk, repair, confidence/);
  assert.throws(() => checkStep({ step: 'repair' }), /repair takes --finding/);
  assert.throws(() => checkStep({ step: 'repair', finding: 'x' }), /repair takes --finding/);
  assert.throws(() => checkStep({ step: 'draft', finding: '1' }), /--finding does not go with draft/);
  assert.throws(() => checkStep({ step: 'walk', field: 'coverage' }), /--field does not go with walk/);
  assert.throws(() => checkStep({ step: 'walk', check: 'nothing' }), /--check takes the names/);
  assert.throws(() => checkStep({ step: 'confidence', field: 'overall' }), /--field takes one of: coverage, remainingRisks/);
  const attempt = (options) => step(config, { step: 'draft', label: 'x', ...options });
  await assert.rejects(() => attempt({ at: 'phase99' }), /--at takes one of: intake, phase1.*or a sandbox of issue-501-change-7001/);
  await assert.rejects(() => attempt({ at: 'other~x' }), /--at takes one of/);
  await assert.rejects(() => attempt({ at: `${SOURCE_JOB}~none` }), /holds no step state/);
  await assert.rejects(() => stepJob(config, { job: 'issue-9-change-1', at: 'phase8', step: 'draft' }), /has no output folder/);
  fs.rmSync(path.join(result.outDir, 'work', 'checkpoints', 'phase8.json'));
  await assert.rejects(() => attempt({ at: 'phase8' }),
    /issue-501-change-7001 has no snapshot for phase8 \(work\/checkpoints\/phase8\.json\)/);
  await attempt({ at: 'phase9-revalidate', label: 'used' });
  await assert.rejects(() => attempt({ at: 'phase9-revalidate', label: 'used' }), /already exists; give another --as label/);
  assert.equal(fs.readdirSync(config.output).filter((name) => name.includes('~')).length, 1);
});

test('a step that asks the model holds the queue and leaves a held queue alone, as a builder step does neither', async () => {
  const { config } = await finishedJob();
  const seen = [];
  const run = async (_config, job) => { seen.push({ held: lockHeld(config), job }); return { ok: true }; };
  await step(config, { at: 'phase9-revalidate', step: 'checklist', label: 'one' }, { run });
  assert.deepEqual(seen, [{ held: true, job: { id: `${SOURCE_JOB}~one`, job: { issue: '501', change: '7001' }, step: 'checklist' } }]);
  const lock = `${config.at(config.queue.file)}.lock`;
  fs.writeFileSync(lock, String(process.pid));
  assert.deepEqual(await step(config, { at: 'phase9-revalidate', step: 'walk', label: 'two' },
    { run: async () => { throw new Error('must not run'); } }), { busy: true });
  assert.equal(fs.existsSync(path.join(config.output, `${SOURCE_JOB}~two`)), false);
  // A builder step ignores the held queue.
  const built = await step(config, { at: 'phase9-revalidate', step: 'draft', label: 'three' });
  assert.equal(built.result.ok, true, JSON.stringify(built.result));
  fs.rmSync(lock);
  const calls = [];
  const pauser = { pause: async () => calls.push('pause'), resume: async () => calls.push('resume') };
  await step(config, { at: 'phase9-revalidate', step: 'walk', label: 'four', pauser }, { run });
  await assert.rejects(() => step(config, { at: 'phase9-revalidate', step: 'walk', label: 'five', pauser },
    { run: async () => { throw new Error('model down'); } }), /model down/);
  assert.deepEqual(calls, ['pause', 'resume', 'pause', 'resume']);
  assert.equal(lockHeld(config), false);
});

test('the command line runs a step, and refuses job options, a missing --at and an option the step does not take', async () => {
  const { config, result } = await finishedJob();
  const cli = (...args) => spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'step', ...args,
    '--config', config.file], { encoding: 'utf8' });
  const ran = cli('draft', '--job', SOURCE_JOB, '--at', 'phase9-revalidate', '--as', 'cli');
  assert.equal(ran.status, 0, ran.stderr);
  const lines = ran.stdout.trim().split('\n');
  assert.equal(lines[0], `sandbox ${SOURCE_JOB}~cli`);
  assert.match(ran.stdout, /^PASS +Dashboard$/m);
  assert.equal(JSON.parse(lines.at(-1)).event, 'step');
  const bad = cli('build', '--job', SOURCE_JOB, '--at', 'phase9-revalidate', '--issue', '501');
  assert.equal(bad.status, 2);
  assert.match(bad.stderr, /step takes --job and --at/);
  assert.match(cli('draft', '--job', SOURCE_JOB).stderr, /--at takes a phase or a sandbox/);
  assert.match(cli('draft', '--at', 'phase8').stderr, /--job takes a job ID/);
  assert.match(cli('draft', '--job', SOURCE_JOB, '--at', 'phase8', '--finding', '1').stderr, /--finding does not go with draft/);
  assert.ok(fs.existsSync(result.workbook));
  assert.deepEqual(fs.readdirSync(config.output).filter((name) => name.includes('~')), [`${SOURCE_JOB}~cli`]);
});

// Replaying a job's recorded calls: a run answered from work/calls with no model server.

/** The job's recorded calls copied to a scratch folder, so a test can change a record and leave the job alone. */
function copiedCalls(config, job) {
  const dir = scratch('replay-calls-');
  fs.cpSync(path.join(config.output, job, 'work', 'calls'), dir, { recursive: true });
  return dir;
}

/** Rewrites the first record of `step` in a calls folder to a prompt with one more line, as another version of the prompt would have recorded. */
function recordWithChangedPrompt(dir, step) {
  const names = fs.readdirSync(dir).filter((name) => name.includes(`-${step}-`)).sort();
  assert.ok(names.length > 0, `${step} was not recorded`);
  const file = path.join(dir, names[0]);
  const saved = JSON.parse(read(file));
  saved.prompt.user += '\nExtra line the old prompt had';
  saved.promptHash = promptHash(saved.prompt.system, saved.prompt.user);
  fs.writeFileSync(file, JSON.stringify(saved));
}

const replayRun = (config, model, label) => runJob(config,
  { issue: '501', change: '7001', id: `${SOURCE_JOB}~${label}` }, { model, echo: false });

test('a job replayed from its own recording with no model builds the identical pack', async () => {
  const { config, model, result } = await finishedJob();
  const live = { json: async () => { throw new Error('the live model was asked'); } };
  const replay = replayModel({ dir: replaySource(config, SOURCE_JOB), live });
  const again = await replayRun(config, replay, 'same');
  assert.equal(again.ok, true, JSON.stringify(again));
  assert.equal(read(again.packPath), read(result.packPath));
  assert.deepEqual(replay.report(), { served: model.calls.length, live: 0, misses: [] });
  // The replay records its own calls, the same ones, so it can be replayed in turn.
  const asked = (outDir) => callRecords(outDir).map((r) => [r.step, r.attempt, r.promptHash, r.schemaHash, r.reply, r.usage]);
  assert.deepEqual(asked(again.outDir), asked(result.outDir));
  assert.equal(statusLines(again.outDir).some((line) => line.event === 'replay-miss'), false);
});

test('a changed prompt stops the replay at that step alone, naming it, with the lines that differ in detail.log', async () => {
  const { config } = await finishedJob();
  const dir = copiedCalls(config, SOURCE_JOB);
  recordWithChangedPrompt(dir, 'phase9_confidence_overall');
  const replay = replayModel({ dir });
  const again = await replayRun(config, replay, 'changed');
  assert.equal(again.ok, false);
  assert.equal(again.reason, 'replay:prompt-changed');
  assert.equal(again.phase, 'phase9-confidence');
  assert.deepEqual(replay.report().misses, [{ step: 'phase9_confidence_overall', code: 'prompt-changed', changed: 1 }]);
  // Every call before it came from the recording; the phases before it passed.
  assert.equal(replay.report().live, 0);
  const lines = statusLines(again.outDir);
  assert.ok(lines.some((line) => line.phase === 'phase9-senior' && line.event === 'pass'));
  assert.deepEqual(lines.filter((line) => line.event === 'replay-miss').map(({ at, ...fields }) => fields),
    [{ job: `${SOURCE_JOB}~changed`, phase: 'phase9', event: 'replay-miss', step: 'phase9_confidence_overall',
      reason: 'prompt-changed', changedLines: 1 }]);
  assert.equal(lines.at(-1).reason, 'replay:prompt-changed');
  assertContentFree(read(path.join(again.outDir, 'status.log')));
  assert.match(read(path.join(again.outDir, 'detail.log')),
    /replay diff phase9_confidence_overall\nuser, from line \d+:\n- Extra line the old prompt had\n/);
  assert.equal(fs.existsSync(again.packPath), false);
});

test('with miss live the changed step alone goes to the live model and the pack is as it was', async () => {
  const { config, result } = await finishedJob();
  const dir = copiedCalls(config, SOURCE_JOB);
  recordWithChangedPrompt(dir, 'phase9_confidence_overall');
  const live = fakeModel({ ...INTAKE, ...NOT_REMOVAL });
  const replay = replayModel({ dir, miss: 'live', live });
  const again = await replayRun(config, replay, 'live');
  assert.equal(again.ok, true, JSON.stringify(again));
  assert.deepEqual(live.calls.map((call) => call.schemaName), ['phase9_confidence_overall']);
  assert.deepEqual(replay.report().misses, [{ step: 'phase9_confidence_overall', code: 'prompt-changed', changed: 1 }]);
  assert.equal(replay.report().live, 1);
  assert.equal(read(again.packPath), read(result.packPath));
});

test('a slice replayed with no model takes no queue, and a sandbox records only the calls its own run made', async () => {
  const { config, model } = await finishedJob();
  const held = [];
  const replay = replayModel({ dir: replaySource(config, SOURCE_JOB) });
  const slice = (label, from) => rerunJob(config, { job: SOURCE_JOB, from: 'phase9-senior', until: 'phase9-confidence', label },
    { model: from, replayOnly: true, echo: false,
      run: (...args) => { held.push(lockHeld(config)); return runJob(...args); } });
  const one = await slice('one', replay);
  assert.equal(one.result.ok, true, JSON.stringify(one.result));
  assert.deepEqual(held, [false]);
  const records = callRecords(path.join(config.output, one.id));
  assert.ok(records.length > 0 && records.length < model.calls.length);
  assert.equal(records.length, replay.report().served);
  assert.deepEqual(records.map((r) => r.seq), records.map((_, i) => i + 1));
  // The sandbox is a recording of its own: replaying it answers the same slice again.
  const again = await slice('two', replayModel({ dir: replaySource(config, one.id) }));
  assert.equal(again.result.ok, true, JSON.stringify(again.result));
  const snapshot = (id) => read(path.join(config.output, id, 'work', 'checkpoints', 'phase9-confidence.json'));
  assert.equal(snapshot(again.id), snapshot(one.id));
  assert.deepEqual(held, [false, false]);
});

test('a step replayed from a sandbox recording asks no model, takes no queue and leaves the same state', async () => {
  const { config } = await finishedJob();
  const live = fakeModel({ ...INTAKE, ...NOT_REMOVAL });
  const recorded = await step(config, { at: 'phase9-revalidate', step: 'walk', label: 'asked' }, { model: live });
  assert.equal(recorded.result.ok, true, JSON.stringify(recorded.result));
  assert.ok(live.calls.length > 0);
  const held = [];
  const replay = replayModel({ dir: replaySource(config, recorded.id) });
  const done = await step(config, { at: 'phase9-revalidate', step: 'walk', label: 'again' },
    { model: replay, replayOnly: true, run: (...args) => { held.push(lockHeld(config)); return runStep(...args); } });
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  assert.deepEqual(held, [false]);
  assert.deepEqual(replay.report(), { served: live.calls.length, live: 0, misses: [] });
  assert.deepEqual(done.result.report, recorded.result.report);
  assert.equal(slurp(path.join(config.output, done.id, 'work', 'step.json')),
    slurp(path.join(config.output, recorded.id, 'work', 'step.json')));
});

test('a step stopped by a changed prompt fails as replay:prompt-changed and leaves the state it started from', async () => {
  const { config, result } = await finishedJob();
  const live = fakeModel({ ...INTAKE, ...NOT_REMOVAL });
  const recorded = await step(config, { at: 'phase9-revalidate', step: 'walk', label: 'asked' }, { model: live });
  const dir = copiedCalls(config, recorded.id);
  recordWithChangedPrompt(dir, live.calls[0].schemaName);
  const done = await step(config, { at: 'phase9-revalidate', step: 'walk', label: 'miss' },
    { model: replayModel({ dir }), replayOnly: true });
  assert.equal(done.result.ok, false);
  assert.equal(JSON.parse(done.result.lines.at(-1)).reason, 'replay:prompt-changed');
  const sandbox = path.join(config.output, done.id);
  assert.equal(slurp(path.join(sandbox, 'work', 'step.json')),
    slurp(path.join(result.outDir, 'work', 'checkpoints', 'phase9-revalidate.json')));
});

test('--model takes a value only outside compare, and the replay flags go with run --job and step', async () => {
  assert.deepEqual(parseArgs(['run', '--job', 'x', '--from', 'p', '--model', 'replay:x', '--replay-miss', 'live']),
    { docs: [], words: ['run'], job: 'x', from: 'p', model: 'replay:x', replayMiss: 'live' });
  assert.deepEqual(parseArgs(['compare', '--model', '--config', 'c']), { docs: [], words: ['compare'], model: true, config: 'c' });
  const { config } = await finishedJob();
  const cli = (command, ...args) => spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), command,
    '--config', config.file, ...args], { encoding: 'utf8' });
  const slice = (...more) => cli('run', '--job', SOURCE_JOB, '--from', 'phase9-senior', '--as', 'refused', ...more);
  const refused = (result, pattern) => {
    assert.equal(result.status, 2, result.stdout + result.stderr);
    assert.match(result.stderr, pattern);
  };
  refused(cli('queue', 'status', '--model', `replay:${SOURCE_JOB}`), /--model goes with step, or with run --job/);
  refused(cli('run', '--issue', '501', '--replay-miss', 'live'), /--replay-miss goes with step, or with run --job/);
  refused(slice('--replay-miss', 'live'), /--replay-miss goes with --model replay:<source>/);
  refused(slice('--model', 'live'), /--model takes replay:/);
  refused(slice('--model'), /--model takes replay:/);
  refused(slice('--model', `replay:${SOURCE_JOB}`, '--replay-miss', 'maybe'), /--replay-miss takes fail or live/);
  refused(slice('--model', `replay:${SOURCE_JOB}`, '--pause'), /--pause is for a run that can ask the live model/);
  refused(slice('--model', 'replay:issue-9-change-1'), /issue-9-change-1 has no recorded calls/);
  refused(cli('step', 'walk', '--job', SOURCE_JOB, '--at', 'phase9-revalidate', '--model', 'replay:../nowhere'),
    /holds no call records/);
  // Nothing was written for any of them.
  assert.deepEqual(fs.readdirSync(config.output).filter((name) => name.includes('~')), []);
});

test('the command line replays a slice with no model and no queue, prints what was replayed, and stops on a changed prompt', async () => {
  const { config } = await finishedJob();
  const cli = (command, ...args) => spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), command,
    '--config', config.file, ...args], { encoding: 'utf8' });
  const slice = (label, source, ...more) => cli('run', '--job', SOURCE_JOB, '--from', 'phase9-senior', '--until', 'phase9-confidence',
    '--as', label, '--model', source, ...more);
  // A queue held by a live process does not stop a replay that can never ask the model.
  const lock = `${config.at(config.queue.file)}.lock`;
  fs.writeFileSync(lock, String(process.pid));
  const ran = slice('replayed', `replay:${SOURCE_JOB}`);
  const stoppedByQueue = slice('live', `replay:${SOURCE_JOB}`, '--replay-miss', 'live');
  fs.rmSync(lock);
  assert.equal(ran.status, 0, ran.stdout + ran.stderr);
  assert.match(ran.stdout, new RegExp(`^sandbox ${SOURCE_JOB}~replayed$`, 'm'));
  assert.match(ran.stdout, /^replay {2}served [1-9]\d* {2}live 0 {2}missed 0$/m);
  // Where a miss may go to the live model, the queue is needed again.
  assert.equal(stoppedByQueue.status, 1);
  assert.match(stoppedByQueue.stderr, /the queue is running/);
  const dir = copiedCalls(config, SOURCE_JOB);
  recordWithChangedPrompt(dir, 'phase9_confidence_overall');
  const changed = slice('changed', `replay:${dir}`);
  assert.equal(changed.status, 1, changed.stdout + changed.stderr);
  assert.match(changed.stdout, /^replay: prompt changed for phase9_confidence_overall \(1 line differs; the diff is in detail\.log\)$/m);
  assert.match(changed.stdout, /"event":"fail".*"reason":"replay:prompt-changed"/);
  assertContentFree(changed.stdout);
});

// ---- status.log: call progress and usage, check verdicts, repairs, confidence, builder failures ----

/** A clock for the model client that moves only when a test advances it, with its interval timers. */
function fakeClock() {
  let now = 0;
  let next = 1;
  const timers = new Map();
  return {
    now: () => now,
    setInterval: (fn, ms) => { timers.set(next, { fn, ms, due: now + ms }); next += 1; return next - 1; },
    clearInterval: (id) => timers.delete(id),
    timers,
    advance(ms) {
      const end = now + ms;
      for (;;) {
        const [, timer] = [...timers].filter(([, t]) => t.due <= end).sort((a, b) => a[1].due - b[1].due)[0] ?? [];
        if (!timer) break;
        now = timer.due;
        timer.due += timer.ms;
        timer.fn();
      }
      now = end;
    },
  };
}

/** An ask context over `fetchImpl` that keeps the status lines, the detail entries and the call records. */
async function askLogged({ fetchImpl, clock, progressMinutes, phase = 'phase9', step = 'walk', reasoning = true }) {
  const { ask } = await import('./phases.mjs');
  const lines = [];
  const details = [];
  const records = [];
  const config = fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm' } });
  const ctx = { config, calls: 0, tokens: { prompt: 0, output: 0 }, job: { id: 'j' },
    logs: { status: (fields) => lines.push(fields), detail: (label, value) => details.push([label, value]),
      call: (record) => records.push(record) },
    model: { ...modelClient({ endpoint: 'http://localhost:1/v1', name: 'm', fetchImpl,
      ...(clock ? { clock } : {}), ...(progressMinutes ? { progressMinutes } : {}) }),
    countTokens: async () => 10, contextWindow: async () => null } };
  const run = () => ask(ctx, { phase, step, reasoning, inputs: [], schema: { type: 'object' }, task: 't' });
  return { run, lines, details, records };
}

/** A fetch that streams the start of a reply and waits for `release()` before it ends it, or resets. */
function slowReply({ fail = false } = {}) {
  const events = sse({ reasoning: 'thinking', content: '{"ok":true}' }).split('\n\n');
  let release;
  const gate = new Promise((resolve) => { release = resolve; });
  let began;
  const begun = new Promise((resolve) => { began = resolve; });
  const fetchImpl = async (url, options) => {
    // The role chunk, one thinking delta and the first half of the answer.
    options.onData(`${events.slice(0, 3).join('\n\n')}\n\n`);
    began();
    await gate;
    if (fail) throw new Error('connection reset');
    options.onData(events.slice(3).join('\n\n'));
    return { ok: true, status: 200, text: async () => '' };
  };
  return { fetchImpl, begun, release };
}

const progressLines = (over) => over.lines.filter((line) => line.event === 'progress');

test('a call running past five minutes writes a progress line every five minutes until it ends', async () => {
  const clock = fakeClock();
  const slow = slowReply();
  const over = await askLogged({ fetchImpl: slow.fetchImpl, clock });
  const done = over.run();
  await slow.begun;
  clock.advance(299999);
  assert.deepEqual(progressLines(over), []);
  clock.advance(1);
  assert.deepEqual(progressLines(over), [{ job: 'j', phase: 'phase9', step: 'walk', event: 'progress', attempt: 1,
    reasoning: true, reasoningTokens: 1, answerTokens: 1, elapsedMs: 300000 }]);
  clock.advance(300000);
  assert.deepEqual(progressLines(over).map((line) => line.elapsedMs), [300000, 600000]);
  slow.release();
  assert.deepEqual(await done, { ok: true });
  assert.equal(clock.timers.size, 0);
  clock.advance(900000);
  assert.equal(progressLines(over).length, 2);
  assert.equal(over.lines.find((line) => line.event === 'call').ms, 600000);
  assertContentFree(JSON.stringify(over.lines));
});

test('a call that ends before five minutes writes no progress line, and the interval is configurable', async () => {
  const quick = await askLogged({ fetchImpl: async () => streamed({ content: '{"ok":true}' }) });
  await quick.run();
  assert.deepEqual(progressLines(quick), []);
  const clock = fakeClock();
  const slow = slowReply();
  const over = await askLogged({ fetchImpl: slow.fetchImpl, clock, progressMinutes: 1 });
  const done = over.run();
  await slow.begun;
  clock.advance(60000);
  assert.deepEqual(progressLines(over).map((line) => line.elapsedMs), [60000]);
  slow.release();
  await done;
});

test('the progress timer is cleared when the call fails, and a report that cannot be written does not stop the call', async () => {
  const clock = fakeClock();
  const slow = slowReply({ fail: true });
  const over = await askLogged({ fetchImpl: slow.fetchImpl, clock });
  const done = over.run();
  await slow.begun;
  clock.advance(300000);
  slow.release();
  await assert.rejects(done, (error) => error.code === 'network');
  assert.equal(clock.timers.size, 0);
  // A callback that throws is ignored.
  const again = fakeClock();
  const reply = slowReply();
  const client = modelClient({ endpoint: 'http://localhost:1/v1', name: 'm', fetchImpl: reply.fetchImpl, clock: again });
  const call = client.json({ ...CHAT_CALL, onProgress: () => { throw new Error('disk full'); } });
  await reply.begun;
  again.advance(300000);
  reply.release();
  assert.deepEqual((await call).value, { ok: true });
  assert.equal(again.timers.size, 0);
});

test('a streamed reply reaches the progress report in pieces over a real connection', { timeout: 10000 }, async () => {
  const events = sse({ reasoning: 'thinking', content: '{"ok":true}' }).split('\n\n');
  // The server holds the reply open until a report has counted its first pieces, so the
  // report comes before the reply ends on a busy machine too. It gives up after 5 seconds.
  let counted;
  let release;
  const reported = new Promise((resolve) => { release = resolve; });
  const chat = await chatServer(async (res) => {
    res.writeHead(200, { 'content-type': 'text/event-stream' });
    res.write(`${events.slice(0, 3).join('\n\n')}\n\n`);
    const giveUp = setTimeout(release, 5000);
    await reported;
    clearTimeout(giveUp);
    res.end(events.slice(3).join('\n\n'));
  });
  try {
    const client = modelClient({ endpoint: chat.endpoint, name: 'm', progressMinutes: 0.0005 });
    const { value } = await client.json({ ...CHAT_CALL, onProgress: (report) => {
      if (counted || report.reasoningTokens !== 1 || report.answerTokens !== 1) return;
      counted = report;
      release();
    } });
    assert.deepEqual(value, { ok: true });
    assert.deepEqual([counted?.reasoningTokens, counted?.answerTokens], [1, 1]);
  } finally {
    chat.close();
  }
});

test('config takes model.progressMinutes as whole minutes from 1 to 1440', () => {
  const make = (progressMinutes) => () => fixtureConfig({ model: { endpoint: 'http://localhost:1/v1', name: 'm',
    progressMinutes } });
  assert.doesNotThrow(make(2));
  assert.doesNotThrow(make(1440));
  for (const bad of [0, 1.5, '5', -1, 1441]) assert.throws(make(bad), /progressMinutes/);
});

test('a call cut at its limit logs thinking and answer tokens apart, and detail.log keeps the end of the thinking', async () => {
  const thinking = `${'x'.repeat(5000)}the last thought`;
  const fetchImpl = async () => streamed({ finish: 'length', content: '{"a":', reasoning: thinking,
    usage: { prompt_tokens: 30, completion_tokens: 90, completion_tokens_details: { reasoning_tokens: 80 } } });
  const over = await askLogged({ fetchImpl });
  await assert.rejects(over.run(), (error) => error.code === 'runaway');
  const [retry, fail] = over.lines.filter((line) => ['retry', 'call-fail'].includes(line.event));
  assert.deepEqual([retry.event, retry.reason, retry.reasoningTokens, retry.answerTokens, retry.outputTokens],
    ['retry', 'length', 80, 10, 90]);
  assert.deepEqual([fail.event, fail.reason, fail.reasoningTokens, fail.answerTokens, fail.outputTokens],
    ['call-fail', 'runaway', 80, 10, 90]);
  const tails = over.details.filter(([label]) => label === 'phase9 walk reasoning tail');
  assert.equal(tails.length, 2);
  assert.equal(tails[0][1].length, REASONING_TAIL_CHARS);
  assert.ok(tails[0][1].endsWith('the last thought'));
  assert.equal(over.records[0].reasoningTail, tails[0][1]);
  // The thinking itself never reaches the status lines.
  assert.ok(!JSON.stringify(over.lines).includes('the last thought'));
  assertContentFree(JSON.stringify(over.lines));
});

test('a call cut with no thinking counts all of its output as answer', async () => {
  const over = await askLogged({ reasoning: false,
    fetchImpl: async () => streamed({ finish: 'length', content: '{"a":', usage: { completion_tokens: 12 } }) });
  await assert.rejects(over.run(), (error) => error.code === 'length');
  const fail = over.lines.find((line) => line.event === 'call-fail');
  assert.deepEqual([fail.reasoningTokens, fail.answerTokens], [0, 12]);
  assert.equal(over.details.filter(([label]) => label.endsWith('reasoning tail')).length, 0);
});

test('a thinking call cut with no known token split leaves the split out of its lines', async () => {
  const over = await askLogged({
    fetchImpl: async () => streamed({ finish: 'length', content: '{"a":', usage: { completion_tokens: 12 } }) });
  await assert.rejects(over.run(), (error) => error.code === 'runaway');
  const [retry] = over.lines.filter((line) => line.event === 'retry');
  assert.equal(retry.outputTokens, 12);
  assert.ok(!('reasoningTokens' in retry) && !('answerTokens' in retry), JSON.stringify(retry));
});

test('a call logs promptMs, genMs and cachedTokens when the server returns them, and leaves them out when it does not', async () => {
  const timed = await askLogged({ fetchImpl: async () => streamed({ content: '{"ok":true}',
    usage: { prompt_tokens: 30, completion_tokens: 7 },
    timings: { prompt_ms: 120.4, predicted_ms: 900.6, cache_n: 12 } }) });
  await timed.run();
  const call = timed.lines.find((line) => line.event === 'call');
  assert.deepEqual([call.promptMs, call.genMs, call.cachedTokens], [120, 901, 12]);
  assert.deepEqual([timed.records[0].usage.promptMs, timed.records[0].usage.genMs, timed.records[0].usage.cachedTokens],
    [120, 901, 12]);
  // A server that reports cached tokens in the usage block only.
  const cached = await askLogged({ fetchImpl: async () => streamed({ content: '{"ok":true}',
    usage: { prompt_tokens: 30, completion_tokens: 7, prompt_tokens_details: { cached_tokens: 5 } } }) });
  await cached.run();
  const partial = cached.lines.find((line) => line.event === 'call');
  assert.equal(partial.cachedTokens, 5);
  assert.ok(!('promptMs' in partial) && !('genMs' in partial));
  const bare = await askLogged({ fetchImpl: async () => streamed({ content: '{"ok":true}',
    usage: { prompt_tokens: 30, completion_tokens: 7 } }) });
  await bare.run();
  const none = bare.lines.find((line) => line.event === 'call');
  assert.deepEqual(Object.keys(none).filter((key) => ['promptMs', 'genMs', 'cachedTokens', 'reasoningTokens',
    'answerTokens'].includes(key)), []);
});

test('status fields from a builder note: only plain words survive and the line fits a field', () => {
  assert.equal(noteCode('BR-LIB.UC01-001 covered by "Patron renewal" at row 12.\nsecond line'),
    'ID covered by _ at row ID');
  assert.equal(noteCode('\n  \nCoverage Matrix has no row'), 'Coverage Matrix has no row');
  assert.equal(noteCode(undefined), '');
  // The builder's populated line is skipped.
  assert.equal(noteCode('populated: Yes\nBR-1 has no coverage'), 'ID has no coverage');
  assert.equal(noteCode('populated: No'), '');
  // A name from a document is hidden whether or not it sits in quotes.
  assert.equal(noteCode('Patron Services has no reason for its inclusion'), '_ has no reason for its inclusion');
  assert.equal(noteCode('module Patron Services already uses abbreviation LIB'), '_ already _');
  // A title made only of plain words is hidden past its first word, and a stray dash does not split a run.
  assert.equal(noteCode('source document Card Limits appears more than once'), '_ appears more than once');
  assert.equal(noteCode('Card Status Rules has no reason for its inclusion'), 'Card _ has no reason for its inclusion');
  assert.equal(noteCode('Foo - Bar has no row'), '_ has no row');
  // An apostrophe inside a quoted span does not end it, and a word's apostrophe opens nothing.
  assert.equal(noteCode('Expected Result "The customer\'s balance shows Overdraft Protection" does not match'),
    'Expected Result _ does not match');
  assert.equal(noteCode('Title \'Wire Transfer\' is missing, and the card\'s steps are short'),
    'Title _ is missing and the _ steps are short');
  // A quote inside a quoted value pairs wrongly, and the words between the pairs are still hidden.
  assert.ok(!noteCode('Expected Result "The system shows "Card renewed" on screen." does not agree').includes('renewed'));
  // A quote that never closes hides the rest of the line, and a reviewer's words are dropped.
  assert.equal(noteCode('Row 3 shows "Wire transfer limit'), 'Row ID shows _');
  assert.equal(noteCode('BR-ACC-01 reads Missing, but a test card covers it. The review said: Wire Transfer Limits apply'),
    'ID reads Missing but a test card covers it The review said');
  const long = noteCode('has '.repeat(60));
  assert.ok(long.length <= FIELD_MAX && long.startsWith('has has'));
  // Whatever a note holds, the result is a status field.
  for (const note of ['\u00e9\u4e2d\u6587 \u0000 tab\there', '"unclosed quote', 'a'.repeat(300), '%%% ### $$$']) {
    assert.doesNotThrow(() => statusFields({ problem: noteCode(note) }), note);
  }
  assert.equal(sheetsField(['Coverage Matrix', 'Impact Analysis (ALM)', '']), 'Coverage Matrix+Impact Analysis ALM');
  const wide = sheetsField(['a'.repeat(50), 'b'.repeat(50)]);
  assert.equal(wide, 'a'.repeat(50));
  assert.doesNotThrow(() => statusFields({ failedSheets: sheetsField(['x+y', 'z%']) }));
});

const REVALIDATION_NAMES = S.REVALIDATION_CHECKS;
const checkLines = (lines, walk) => lines.filter((line) => line.event === 'check' && line.walk === walk);

test('each revalidation verdict is a check line with its walk, thinking and whether a fix came with it', async () => {
  const traceability = S.REVALIDATION_GROUPS.find((group) => group.key === 'traceability').checks;
  let cut = false;
  const model = fakeModel({ ...DOCS, phase9_checklist: plantedChecklist(), phase8_repair: correctingRepair,
    phase9_revalidation: (value, calls) => {
      // The first traceability call fails and is asked again with thinking off.
      if (!cut && calls.at(-1).schemaName === 'phase9_revalidation_traceability') {
        cut = true;
        throw new ModelError('parse', 'not JSON');
      }
      return walkFailsOnCard.phase9_revalidation(value, calls);
    } });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.reason, 'gate:revalidation-failed');
  const lines = statusLines(result.outDir);
  const first = checkLines(lines, 'revalidation');
  assert.deepEqual(first.map((line) => line.check), REVALIDATION_NAMES);
  assert.deepEqual(first.map((line) => [line.check, line.verdict, line.fixGiven]).filter(([, verdict]) => verdict === 'fail'),
    [['Traceability complete', 'fail', true]]);
  assert.ok(first.filter((line) => line.verdict === 'pass').every((line) => line.fixGiven === false));
  // Only the checks the retried call judged ran without thinking.
  assert.deepEqual(first.filter((line) => !line.thinking).map((line) => line.check), traceability);
  assert.ok(first.every((line) => line.phase === 'phase9' && line.job === result.id));
  const again = checkLines(lines, 'revalidation-again');
  assert.deepEqual(again.map((line) => line.check), REVALIDATION_NAMES);
  assert.ok(again.every((line) => line.thinking === true));
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('each finding of a fix round is a repair line with what it asked for, what came back and what became of it', async () => {
  const model = fakeModel({ ...DOCS, phase9_checklist: plantedChecklist(), phase8_repair: correctingRepair,
    ...walkFailsOnCard });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  const repairs = statusLines(result.outDir).filter((line) => line.event === 'repair');
  const review = repairs.find((line) => line.check === undefined);
  assert.deepEqual([review.phase, review.step, review.finding, review.asked, review.cards, review.newCards,
    review.coverageRows, review.limitations, review.result],
  ['phase8', 'repair-review-1-g1', 1, 'card', 1, 0, 0, 0, 'applied']);
  const revalidation = repairs.find((line) => line.check === 'Traceability complete');
  assert.deepEqual([revalidation.step, revalidation.finding, revalidation.asked, revalidation.cards, revalidation.result],
    ['repair-revalidation-g1', 1, 'card', 1, 'applied']);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('a repair line says new-card, empty or undone for a finding that asks for a card', async () => {
  const outcome = async (label, reply) => {
    const setup = lib({ ...asksNewCard, phase8_repair: correctingRepair });
    addJob(setup.config, { issue: '501', change: '7001' });
    const failed = await runLib(setup);
    uncover(failed.outDir, 'BR-LIB.UC01-001');
    const done = await step(setup.config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label },
      { model: fakeModel(reply) });
    // The sandbox's log starts with the source job's lines, so its own repair line is the last.
    const line = statusLines(path.join(setup.config.output, done.id)).filter((l) => l.event === 'repair').at(-1);
    return line;
  };
  const applied = await outcome('applied', { phase8_repair: newCardFor });
  assert.deepEqual([applied.step, applied.check, applied.finding, applied.asked, applied.cards, applied.newCards,
    applied.coverageRows, applied.limitations, applied.result],
  ['repair-revalidation-g1', 'Traceability complete', 1, 'new-card', 0, 1, 0, 0, 'applied']);
  const undone = await outcome('undone', { phase8_repair: newCardFor, phase6_recheck: rejectsAll });
  assert.deepEqual([undone.asked, undone.newCards, undone.result], ['new-card', 1, 'undone']);
  const empty = await outcome('empty', { phase8_repair: (value) => ({ ...value, cards: [], coverage: [],
    limitations: [], newCards: [] }) });
  assert.deepEqual([empty.asked, empty.newCards, empty.cards, empty.result], ['new-card', 0, 0, 'empty']);
  assertContentFree(JSON.stringify([applied, undone, empty]));
});

test('a Draft workbook the builder refuses in Phase 8 logs the failed sheets and the first reason', async () => {
  const refuse = 'console.log(["FAIL                   Coverage Matrix", "    populated: Yes", "    BR-LIB.UC01-001 covered by nothing",'
    + ' "FAIL                   Workbook Validation", "    1 worksheet fails"].join("\\n")); process.exit(1)';
  const config = fixtureConfig({ builder: { module: 'builder-stub.mjs', retries: 1, command: ['node', '-e', refuse] } });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model: fakeModel(DOCS), echo: false });
  assert.equal(result.reason, 'gate:builder-fail');
  const lines = statusLines(result.outDir);
  const draft = lines.findLast((line) => line.event === 'draft');
  assert.deepEqual([draft.written, draft.failedSheets, draft.problem],
    [false, 'Coverage Matrix', 'ID covered by nothing']);
  const fail = lines.findLast((line) => line.event === 'fail');
  assert.deepEqual([fail.reason, fail.sheets, fail.failedSheets, fail.problem],
    ['gate:builder-fail', 1, 'Coverage Matrix', 'ID covered by nothing']);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('a Draft workbook the builder refuses in Phase 9 logs the failed sheet and the first reason', async () => {
  const refuseAfterSenior = 'const fs = require("fs"); const [p, , o] = process.argv.slice(1);'
    + ' if (JSON.parse(fs.readFileSync(p, "utf8")).seniorReview.missed !== "Pending review.") {'
    + ' console.log("FAIL                   Senior Tester Review\\n    a card has no steps"); process.exit(1); }'
    + ' process.exit(require("child_process").spawnSync(process.execPath, ["builder-stub.mjs", p, "--out", o],'
    + ' { stdio: "inherit" }).status);';
  const config = fixtureConfig({ builder: { module: 'builder-stub.mjs', retries: 2,
    command: ['node', '-e', refuseAfterSenior, '{pack}', '--out', '{out}'] } });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model: fakeModel(DOCS), echo: false });
  assert.deepEqual([result.phase, result.reason], ['phase9-confidence', 'gate:builder-fail']);
  const fail = statusLines(result.outDir).findLast((line) => line.event === 'fail');
  assert.deepEqual([fail.sheets, fail.failedSheets, fail.problem], [1, 'Senior Tester Review', 'a card has no steps']);
});

test('the overall rating logs what set it: the level asked, the cap, and the counts it was rated from', async () => {
  const capped = lib({ ...DROP_RUN,
    phase9_confidence_overall: (value) => ({ ...value, overall: 'High', reason: 'BR-1 is covered.' }) });
  const result = await runLib(capped);
  const [line] = statusLines(result.outDir).filter((l) => l.event === 'confidence');
  assert.deepEqual([line.phase, line.step, line.overall, line.asked, line.cappedBy, line.untested],
    ['phase9', 'confidence-overall', 'Medium', 'High', 'untested-objectives', 1]);
  for (const key of ['stepsWeak', 'stepsPartial', 'openItems', 'checklistIssues']) {
    assert.equal(typeof line[key], 'number', key);
  }
  const plain = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { echo: false,
    model: fakeModel({ ...DOCS, phase9_confidence_overall: (value) => ({ ...value, overall: 'Medium',
      reason: 'BR-LIB.UC01-002 meets the Medium criteria with two cards.' }) }) });
  const [uncapped] = statusLines(plain.outDir).filter((l) => l.event === 'confidence');
  assert.deepEqual([uncapped.overall, uncapped.asked, uncapped.cappedBy, uncapped.untested],
    ['Medium', 'Medium', 'none', 0]);
  assertContentFree(read(path.join(plain.outDir, 'status.log')));
});

test('a rating made again after a failed revalidation logs the open items', async () => {
  const model = fakeModel({ ...DOCS,
    phase9_revalidation: (value) => failCheck(value, 'Traceability complete', 'A card lost its rule'),
    phase9_confidence_overall: (value, calls) => (calls.filter((c) => c.schemaName === 'phase9_confidence_overall').length === 1
      ? { ...value, overall: 'High', reason: 'BR-LIB.UC01-001 is fully covered.' }
      : { ...value, overall: 'Low', reason: 'Revalidation left Traceability open on BR-LIB.UC01-001.' }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  const lines = statusLines(result.outDir).filter((l) => l.event === 'confidence');
  assert.deepEqual(lines.map((l) => [l.step, l.overall, l.openItems]),
    [['confidence-overall', 'High', 0], ['confidence-overall-again', 'Low', 1]]);
});

test('a stop logs the failing phase\'s own time and calls, and the whole job\'s under jobMs and jobCalls', async () => {
  let tick = 0;
  const now = () => { tick += 1000; return tick; };
  const model = fakeModel({ ...DOCS, phase1_understanding: () => { throw new ModelError('network', 'down'); } });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false, now });
  assert.equal(result.reason, 'model:network');
  const lines = statusLines(result.outDir);
  const fail = lines.findLast((line) => line.event === 'fail');
  const attempts = (phase) => lines.filter((line) => line.phase === phase
    && ['call', 'retry', 'call-fail'].includes(line.event)).length;
  assert.equal(fail.phase, 'phase1');
  assert.equal(fail.calls, attempts('phase1'));
  assert.equal(fail.jobCalls, attempts('intake') + attempts('phase1'));
  assert.ok(fail.jobCalls > fail.calls);
  const intake = lines.find((line) => line.event === 'pass' && line.phase === 'intake');
  assert.ok(fail.jobMs >= fail.ms + intake.ms, JSON.stringify([fail, intake]));
  assert.ok(result.ms >= fail.jobMs);
});

test('job status shows the last check and the last repair beside the phase timings', () => {
  const config = fixtureConfig();
  seedJob(config, { status: 'failed', phase: 'phase9', reason: 'gate:revalidation-failed',
    added: '2026-11-02T08:00:00.000Z', finished: '2026-11-02T09:00:00.000Z' }, [
    logLine('2026-11-01T08:00:01.000Z', { phase: 'phase8', event: 'pass', ms: 1000 }),
    logLine('2026-11-01T08:10:00.000Z', { phase: 'phase9', event: 'check', walk: 'revalidation',
      check: 'Traceability complete', verdict: 'fail', thinking: true, fixGiven: true }),
    logLine('2026-11-01T08:11:00.000Z', { phase: 'phase8', event: 'repair', step: 'repair-revalidation-g1', finding: 1,
      check: 'Traceability complete', asked: 'card', cards: 1, newCards: 0, coverageRows: 0, limitations: 0,
      result: 'applied' }),
    logLine('2026-11-01T08:12:00.000Z', { phase: 'phase9', event: 'check', walk: 'revalidation-again',
      check: 'Traceability complete', verdict: 'pass', thinking: true, fixGiven: false }),
    logLine('2026-11-01T08:13:00.000Z', { phase: 'phase9', step: 'walk', event: 'progress', attempt: 1,
      reasoning: true, reasoningTokens: 5, answerTokens: 1, elapsedMs: 300000 }),
  ]);
  assert.deepEqual(jobStatus(config, 'issue-9415'), [
    'issue-9415  failed  queue free',
    'stopped phase=phase9 reason=gate:revalidation-failed',
    'done phase=phase8 ms=1000',
    'last-check phase=phase9 walk=revalidation-again check=Traceability complete verdict=pass thinking=true fixGiven=false',
    'last-repair phase=phase8 step=repair-revalidation-g1 finding=1 check=Traceability complete asked=card cards=1'
      + ' newCards=0 coverageRows=0 limitations=0 result=applied',
  ]);
});

test('a finding that asks for an assumption logs the assumptions the repair added', async () => {
  const model = fakeModel({ ...DOCS,
    phase9_checklist: finding('The pack does not say which accounts are in scope',
      'Add an assumption that only active accounts are in scope'),
    phase8_repair: (value) => ({ ...value, coverage: [], limitations: [],
      ...(value.assumptions ? { assumptions: [{ assumption: 'Only active accounts are in scope.',
        why: 'The review asked.', impact: 'Inactive accounts are not tested.', clarification: 'Confirm.' }] } : {}) }) });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  const [line] = statusLines(result.outDir).filter((l) => l.event === 'repair');
  assert.deepEqual([line.asked, line.assumptions, line.result], ['assumption', 1, 'applied']);
  // A finding that names no card is a call given none.
  const [call] = statusLines(result.outDir).filter((l) => l.event === 'repair-call');
  assert.deepEqual([call.step, call.finding, call.findings, call.cards, call.part, call.parts],
    ['repair-review-1-g1', 1, 1, 0, 1, 1]);
});

test('a repair step for one finding logs that finding\'s own number', async () => {
  const wrong = (why) => (value) => failCheck(failCheck(value, 'Traceability complete', why,
    'Change step 1 of the cards that cite BR-LIB.UC01-001 to read Corrected step'),
  'All issues resolved', why, 'Change step 1 of the cards that cite BR-LIB.UC01-001 to read Corrected step');
  const setup = lib({ phase9_revalidation: wrong('BR-LIB.UC01-001 reads wrong'), phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  await runLib(setup);
  const done = await step(setup.config, { at: 'phase9-revalidate', step: 'repair', finding: '1', label: 'second' },
    { model: fakeModel({ phase8_repair: correctingRepair }) });
  const line = statusLines(path.join(setup.config.output, done.id)).filter((l) => l.event === 'repair').at(-1);
  assert.equal(line.finding, 2);
});

const cardIdsIn = (text) => [...new Set(text.match(/TC-[A-Z0-9]+-501-\d{3}/g))];
/** A walk that fails three checks, each with a reason of its own and a fix that names the first card. */
const failsThree = { phase9_revalidation: (value, calls) => {
  const id = cardIdIn(calls.at(-1).user);
  return ['All issues resolved', 'Traceability complete', 'Test pack is ready for ALM execution']
    .reduce((reply, check) => failCheck(reply, check, `${id} reads wrong (${check})`,
      `Change step 1 of ${id} to read Corrected step`), value);
} };
const repairCalls = (outDir) => statusLines(outDir).filter((line) => line.event === 'repair-call')
  .map((line) => [line.step, line.finding, line.findings, line.cards, line.part, line.parts]);

test('a revalidation repair round makes one repair call for each finding', async () => {
  const model = fakeModel({ ...DOCS, ...failsThree, phase8_repair: correctingRepair });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.reason, 'gate:revalidation-failed', JSON.stringify(result));
  const repairs = checksFor(model, 'phase8_repair_revalidation');
  assert.deepEqual(repairs.map((call) => call.schemaName), ['phase8_repair_revalidation_g1',
    'phase8_repair_revalidation_g2', 'phase8_repair_revalidation_g3']);
  assert.deepEqual(repairs.map((call) => call.user.match(/ {2}Section: [^\n]+/g)), [
    ['  Section: All issues resolved'], ['  Section: Traceability complete'],
    ['  Section: Test pack is ready for ALM execution']]);
  // A card several findings name is read as the call before left it.
  assert.match(repairs[1].user, /## Cards named\n\n[^\n]*Corrected step/);
  assert.deepEqual(repairCalls(result.outDir), [['repair-revalidation-g1', 1, 1, 1, 1, 1],
    ['repair-revalidation-g2', 2, 1, 1, 1, 1], ['repair-revalidation-g3', 3, 1, 1, 1, 1]]);
  assert.deepEqual(statusLines(result.outDir).filter((line) => line.event === 'repair')
    .map((line) => [line.step, line.finding, line.check, line.result]), [
    ['repair-revalidation-g1', 1, 'All issues resolved', 'applied'],
    ['repair-revalidation-g2', 2, 'Traceability complete', 'applied'],
    ['repair-revalidation-g3', 3, 'Test pack is ready for ALM execution', 'applied']]);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('a finding that names more cards than one reply holds is split across repair calls', async () => {
  const config = fixtureConfig();
  // An output budget this size holds one corrected card in a repair reply.
  config.model.maxOutput = 5000;
  const { repairCardsMax } = await import('./phases.mjs');
  assert.equal(repairCardsMax({ config }), 1);
  assert.equal(repairCardsMax({ config: { model: { maxOutput: 16384 } } }), 3);
  let named = [];
  const model = fakeModel({ ...DOCS,
    phase8_repair: (value) => ({ ...correctingRepair(value), ...(value.assumptions ? { assumptions: [] } : {}) }),
    phase9_revalidation: (value, calls) => {
      if (calls.at(-1).schemaName.endsWith('_again') || !('Traceability complete' in value.checks)) return value;
      named = cardIdsIn(calls.at(-1).user).slice(0, 2);
      // The fix cites a rule and asks for an assumption, so the first call may add a card and an assumption.
      return failCheck(value, 'Traceability complete', `${named.join(' and ')} read wrong`,
        `Change step 1 of ${named.join(' and ')} to read Corrected step, with an assumption for BR-LIB.UC01-001`);
    } });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.equal(named.length, 2);
  const repairs = checksFor(model, 'phase8_repair_revalidation');
  // Each call takes one card: every card the fix names, and any the rule's cards line adds.
  const given = repairs.map((call) => S.propOf(S.propOf(call.schema, 'cards').items, 'id').enum);
  assert.ok(given.length >= 2 && given.every((ids) => ids.length === 1), JSON.stringify(given));
  assert.ok(named.every((id) => given.flat().includes(id)), JSON.stringify(given));
  assert.equal(new Set(given.flat()).size, given.length);
  for (const [i, call] of repairs.entries()) {
    assert.match(call.user, new RegExp(`## Cards for this call\\n\\n[^\\n]+calls of their own: ${given[i][0]}\\n`));
  }
  // Only the first call of a split finding may add a card or an assumption.
  assert.deepEqual(repairs.map((call) => S.propOf(call.schema, 'newCards').maxItems),
    [S.NEW_CARDS_MAX, ...given.slice(1).map(() => 0)]);
  assert.deepEqual(repairs.map((call) => 'assumptions' in call.schema.properties),
    [true, ...given.slice(1).map(() => false)]);
  assert.deepEqual(repairCalls(result.outDir),
    given.map((ids, i) => [`repair-revalidation-g${i + 1}`, 1, 1, 1, i + 1, given.length]));
  assert.deepEqual(statusLines(result.outDir).filter((line) => line.event === 'repair')
    .map((line) => [line.finding, line.part, line.parts]), given.map((ids, i) => [1, i + 1, given.length]));
  const pack = JSON.parse(read(result.packPath));
  for (const id of named) {
    assert.equal(pack.testCards.find((card) => card.id === id).steps[0].description, 'Corrected step', id);
  }
});

test('checklist findings share a repair call only while their cards fit one reply', async () => {
  const calls = async (maxOutput) => {
    const config = fixtureConfig();
    config.model.maxOutput = maxOutput;
    let planted = false;
    const model = fakeModel({ ...DOCS, phase8_repair: correctingRepair,
      phase9_checklist: (value, asked) => {
        if (planted) return { ...value, issues: [] };
        planted = true;
        return { ...value, issues: cardIdsIn(asked.at(-1).user).slice(0, 2).map((id) => ({
          section: 'Coverage Completeness', issue: `${id} has a step that reads wrong`,
          fix: `Change step 1 of ${id} to read Corrected step` })) };
      } });
    const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
    assert.equal(result.ok, true, JSON.stringify(result));
    return repairCalls(result.outDir);
  };
  // Two findings of one card each share a call that holds three cards, and not one that holds one.
  assert.deepEqual(await calls(16384), [['repair-review-1-g1', 1, 2, 2, 1, 1]]);
  assert.deepEqual(await calls(5000), [['repair-review-1-g1', 1, 1, 1, 1, 1],
    ['repair-review-1-g2', 2, 1, 1, 1, 1]]);
});

test('a revalidation repair cut off at its output budget leaves its finding open and the others applied', async () => {
  const partial = '{"cards":[{"id":"a","steps":[{"expected":"reads } and ]"}]},{"id":"b","steps":[';
  const model = fakeModel({ ...DOCS, ...failsThree,
    phase8_repair: (value, calls) => {
      if (calls.at(-1).schemaName === 'phase8_repair_revalidation_g2') {
        throw Object.assign(new ModelError('length', 'cut off'), { partial });
      }
      return correctingRepair(value);
    } });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.reason, 'gate:revalidation-failed', JSON.stringify(result));
  assert.equal(checksFor(model, 'phase8_repair_revalidation').length, 3);
  const lines = statusLines(result.outDir);
  assert.deepEqual(lines.filter((line) => line.event === 'repair-cut')
    .map((line) => [line.step, line.finding, line.cards, line.part, line.parts, line.replyChars, line.wholeCards]),
  [['repair-revalidation-g2', 2, 1, 1, 1, partial.length, 1]]);
  assert.deepEqual(lines.filter((line) => line.event === 'repair').map((line) => [line.finding, line.result]),
    [[1, 'applied'], [3, 'applied']]);
  // The round goes on: the rebuild, then the second walk, which is told only of the fixes that were applied.
  const again = checksFor(model, 'phase9_revalidation').filter((call) => call.schemaName.endsWith('_again'));
  assert.equal(again.length, 3);
  const attempted = again[0].user.split('## Fixes the review attempted')[1].split('\n## ')[0];
  assert.deepEqual(['All issues resolved', 'Traceability complete', 'Test pack is ready for ALM execution']
    .map((check) => attempted.includes(`reads wrong (${check})`)), [true, false, true]);
  const pack = JSON.parse(read(result.packPath));
  assert.ok(pack.testCards.some((card) => card.steps[0].description === 'Corrected step'));
  assert.deepEqual(pack.revalidation.remaining.map((line) => line.endsWith('(a repair reply was cut off at its output budget)')),
    [false, true, false]);
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('a revalidation repair round whose every call is cut off stops the job as a cut reply', async () => {
  const model = fakeModel({ ...DOCS, ...walkFailsOnCard,
    phase8_repair: () => { throw new ModelError('length', 'cut off'); } });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.deepEqual([result.ok, result.reason], [false, 'model:length']);
  const [cut] = statusLines(result.outDir).filter((line) => line.event === 'repair-cut');
  assert.deepEqual([cut.step, cut.finding, cut.cards, 'replyChars' in cut], ['repair-revalidation-g1', 1, 1, false]);
});

test('a cut in a checklist fix round stops the job as a cut reply', async () => {
  const model = fakeModel({ ...DOCS, phase9_checklist: plantedChecklist(),
    phase8_repair: () => { throw new ModelError('length', 'cut off'); } });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.deepEqual([result.ok, result.reason], [false, 'model:length']);
});

test('the whole cards of a cut repair reply are counted without reading past the list', async () => {
  const { wholeItems } = await import('./phases.mjs');
  assert.equal(wholeItems('{"cards":[{"id":"a","steps":[{"x":"}]\\""}]},{"id":"b"},{"id":"c","st', 'cards'), 2);
  assert.equal(wholeItems('{"cards":[{"id":"a"}],"newCards":[{"id":"n"},{"id":"m"}],"cov', 'cards'), 1);
  assert.equal(wholeItems('{"cards":[],"coverage":[{"ruleId":"r"}]}', 'cards'), 0);
  assert.equal(wholeItems('{"cov', 'cards'), 0);
  assert.equal(wholeItems(undefined, 'cards'), 0);
});

test('a revalidation repair that the builder cannot build is logged as undone', async () => {
  const refuseRepaired = 'const fs = require("fs"); const [p, , o] = process.argv.slice(1);'
    + ' if (fs.readFileSync(p, "utf8").includes("Corrected step")) {'
    + ' console.log("FAIL                   Coverage Matrix\\n    planted"); process.exit(1); }'
    + ' process.exit(require("child_process").spawnSync(process.execPath, ["builder-stub.mjs", p, "--out", o],'
    + ' { stdio: "inherit" }).status);';
  const config = fixtureConfig({ builder: { module: 'builder-stub.mjs', retries: 2,
    command: ['node', '-e', refuseRepaired, '{pack}', '--out', '{out}'] } });
  const model = fakeModel({ ...DOCS, ...walkFailsOnCard, phase8_repair: correctingRepair });
  const result = await runJob(config, { issue: '501', change: '7001' }, { model, echo: false });
  const undone = statusLines(result.outDir).filter((l) => l.event === 'repair-undone');
  assert.equal(undone.length, 1, JSON.stringify(result));
  assert.deepEqual([undone[0].step, undone[0].reason, undone[0].findings],
    ['repair-revalidation', 'builder-fail', 1]);
  // The pack goes back to what it was, so it carries no note that a repair changed it.
  const pack = JSON.parse(read(result.packPath));
  assert.doesNotMatch(pack.confidence.manualReview, new RegExp(AGED_NOTE));
  assert.ok(!pack.testCards.some((card) => card.steps[0].description === 'Corrected step'));
});

test('a stop for a failed revalidation reports that phase\'s own time and calls', async () => {
  let tick = 0;
  const now = () => { tick += 1000; return tick; };
  const model = fakeModel({ ...DOCS, ...failsRevalidation });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false, now });
  assert.equal(result.reason, 'gate:revalidation-failed');
  const lines = statusLines(result.outDir);
  const fail = lines.findLast((line) => line.event === 'fail');
  const passed = lines.find((line) => line.event === 'pass' && line.phase === 'phase9-revalidate');
  assert.deepEqual([fail.phase, fail.ms], ['phase9-revalidate', passed.ms]);
  assert.ok(fail.calls > 0 && fail.jobCalls > fail.calls);
  assert.ok(fail.jobMs > fail.ms);
});

test('a stop between phases reports no calls of the phase that ended before it', async () => {
  let tick = 0;
  const now = () => { tick += 1000; return tick; };
  const stop = new AbortController();
  const model = fakeModel({ ...DOCS, phase1_understanding: (value) => { stop.abort(); return value; } });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' },
    { model, echo: false, now, signal: stop.signal });
  assert.equal(result.reason, 'cancelled');
  const lines = statusLines(result.outDir);
  const fail = lines.findLast((line) => line.event === 'fail');
  assert.ok(lines.some((line) => line.event === 'pass' && line.phase === 'phase1'));
  assert.notEqual(fail.phase, 'phase1');
  assert.equal(fail.calls, 0);
});

// ---- The design rules, a repaired card's sets, and the walk after the repair round ----

const FULL = 'Full Coverage Required Run';
const AGED_NOTE = 'were written before the last corrections to the pack';

test('the design rules a review or repair call is given come from the context\'s objectives', () => {
  const objectives = (...names) => names.map((objective) => ({ objective, applicable: true }));
  const ctx = (names, extra = {}) => ({ job: { suite: false }, config: {}, coreObjective: 'Core',
    fullCoverageObjective: 'Full', breakItObjective: 'Break', pack: { objectives: objectives(...names) }, ...extra });
  const live = { rules: [{ id: 'R2', summary: 'A live rule.' }] };
  const retired = { rules: [...live.rules, { id: 'R1', summary: 'Retired: this rule was removed from the master.' }] };
  const [full, breakIt, removed, ...rest] = designRules(ctx(['Core', 'Flow', 'Full', 'Break']), retired);
  assert.equal(rest.length, 0);
  assert.equal(full, 'The Full set, and the cards listed for the Full objective, hold only requirement-derived cards:'
    + ' every one of them. A quality-derived card is left out of both by rule, so its absence there is correct.');
  assert.equal(breakIt, 'The Break set holds only the cards written for break scenarios. Such a card stays out of'
    + ' the Core set.');
  assert.match(removed, /summary starts with "Retired:".*stays a retired rule whatever its class: its own Status, where the workbook shows one, reads Retired, and its coverage status is a separate column\..*Direct Change.*verifies the behavior is gone.*a card whose expected result says the behavior is absent is consistent as it stands\.$/);
  // With exclusiveSets a break card sits in the BREAK IT set alone, so Full Coverage leaves it out too.
  const exclusive = designRules(ctx(['Core', 'Flow', 'Full', 'Break'], { config: { exclusiveSets: true } }), live);
  assert.equal(exclusive.length, 2);
  assert.match(exclusive[0], /every one of them outside the Break set\. /);
  assert.match(exclusive[1], /Such a card sits in no other set, the Full set included\.$/);
  // A rule is stated only when it holds: no BREAK IT set, no retired rule, no ordinary objective.
  assert.deepEqual(designRules(ctx(['Core', 'Full']), live), [full]);
  assert.deepEqual(designRules(ctx(['Full', 'Break']), live), ['The Break set holds only the cards written for break scenarios.']);
  assert.deepEqual(designRules(ctx(['Core']), live), []);
  // An objective dropped for want of a card reads Not Applicable with that reason, by rule.
  const dropped = { rules: [], objectives: [{ objective: 'Flow', applicable: false }, { objective: 'Core', applicable: true }] };
  assert.deepEqual(designRules(ctx(['Core'], { droppedObjectives: ['Flow', 'Core'] }), dropped),
    ['No test card serves Flow, so that objective reads Not Applicable, with a reason that says no test card'
      + ' serves it. That row is how the pack records the gap, by rule: such an objective applies to the change,'
      + ' no card tests it, a repair cannot change the row, and the workbook need not show a limitation for it.']);
  // An objective that was never applicable is no gap; two dropped ones are named together.
  const neither = { rules: [], objectives: dropped.objectives.map((row) => ({ ...row, applicable: false })) };
  assert.deepEqual(designRules(ctx([]), neither), []);
  assert.match(designRules(ctx([], { droppedObjectives: ['Flow', 'Core'] }), neither)[0],
    /^No test card serves Flow, Core, so those objectives read Not Applicable, with a reason /);
  // A set rule is stated only while the pack's sets follow it: a repair can leave a set its last card.
  const sets = (cards) => ({ rules: [], testCards: [{ id: 'Q', derivation: 'Quality' }, { id: 'R', derivation: 'Requirement' },
    { id: 'B', derivation: 'Requirement' }], testSets: Object.entries(cards).map(([objective, ids]) => ({ objective, cards: ids })) });
  const every = ctx(['Core', 'Flow', 'Full', 'Break']);
  assert.deepEqual(designRules(every, sets({ Core: ['Q', 'R'], Full: ['R', 'B'], Break: ['B'] })), [full, breakIt]);
  assert.deepEqual(designRules(every, sets({ Core: ['R'], Full: ['R', 'B', 'Q'], Break: ['B'] })), [breakIt]);
  assert.deepEqual(designRules(every, sets({ Core: ['R'], Full: ['B'], Break: ['B'] })), [breakIt]);
  assert.deepEqual(designRules(every, sets({ Core: ['R', 'B'], Full: ['R', 'B'], Break: ['B'] })),
    [full, 'The Break set holds only the cards written for break scenarios.']);
  const only = ctx(['Core', 'Flow', 'Full', 'Break'], { config: { exclusiveSets: true } });
  assert.deepEqual(designRules(only, sets({ Core: ['R'], Full: ['R'], Break: ['B'] })), exclusive);
  assert.deepEqual(designRules(only, sets({ Core: ['R'], Flow: ['B'], Full: ['R'], Break: ['B'] })),
    [exclusive[0], 'The Break set holds only the cards written for break scenarios.']);
  // A suite pack takes its sets from the suite merge.
  assert.deepEqual(designRules(ctx(['Core', 'Flow', 'Full', 'Break'], { job: { suite: 'LIB' } }), retired), []);
  // No rule names a Revalidation check, so the walk's calls can share it ahead of their question.
  const text = [full, breakIt, removed].join(' ');
  assert.ok(S.REVALIDATION_CHECKS.every((check) => !text.includes(check)));
});

test('both walks and the repair between them carry the design rules, and the second walk is told which text is older than the repairs', async () => {
  const model = fakeModel({ ...DOCS, phase8_repair: correctingRepair,
    phase9_revalidation: (value, calls) => {
      const { schemaName, user } = calls.at(-1);
      const id = cardIdIn(user);
      const reply = failCheck(value, 'Traceability complete', `${id} reads wrong`,
        `Change step 1 of ${id} to read Corrected step`);
      // The second walk fails the same check again and one the first walk passed.
      return schemaName.endsWith('_again') ? failCheck(reply, 'No regressions introduced', `${id} lost a step`) : reply;
    } });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.reason, 'gate:revalidation-failed', JSON.stringify(result));
  const walks = checksFor(model, 'phase9_revalidation');
  assert.equal(walks.length, 6);
  const rules = new RegExp(`## How this pack is built\\n\\n[^\\n]*never fail a check because the pack follows one[^\\n]*\\n`
    + `- The ${FULL} set, and the cards listed for the ${FULL} objective, hold only requirement-derived cards[^\\n]*\\n`
    + '(?:- The BREAK IT set holds only[^\\n]*\\n)?(?:- No test card serves[^\\n]*\\n)?'
    + '- A rule whose summary starts with "Retired:"[^\\n]*consistent as it stands\\.\\n');
  for (const call of walks) assert.match(call.user, rules, call.schemaName);
  const [repair] = checksFor(model, 'phase8_repair_revalidation');
  assert.match(repair.user, new RegExp(`## How this pack is built\\n\\n[^\\n]*applies them again to what you return[^\\n]*\\n- The ${FULL} set, `));
  assert.match(repair.user, /- A rule whose summary starts with "Retired:"/);
  // Only the walk after the repair round is told the review's prose is older than the pack.
  const aged = /## Text written before the repair round\n\n[^\n]*the Senior Tester Review, the Tester Notes, the written fields of the Confidence Assessment, the assumptions the pack held before the round, the scope text of each test set, and the findings under "Checklist findings still open after the last check"[^\n]*is not evidence that a finding is still open[^\n]*the upload sheet\. A gap that an assumption or a limitation documents is still documented/;
  for (const call of walks.slice(0, 3)) assert.doesNotMatch(call.user, /Text written before the repair round/, call.schemaName);
  for (const call of walks.slice(3)) assert.match(call.user, aged, call.schemaName);
  // The pack says so once, in a field the builder shows, and the second walk reads it there.
  const pack = JSON.parse(read(result.packPath));
  assert.equal(pack.confidence.manualReview.split(AGED_NOTE).length, 2);
  assert.match(walks[3].user, new RegExp(`\\[Confidence Assessment row \\d+\\] Field: manualReview \\| Value: [^\\n]*${AGED_NOTE}`));
  assert.doesNotMatch(walks[0].user, new RegExp(AGED_NOTE));
  // A check the second walk fails says whether the first walk failed it too.
  const lines = statusLines(result.outDir);
  assert.ok(checkLines(lines, 'revalidation').every((line) => !('repeat' in line)));
  const again = checkLines(lines, 'revalidation-again');
  assert.deepEqual(again.filter((line) => line.verdict === 'fail').map((line) => [line.check, line.repeat]),
    [['No regressions introduced', false], ['Traceability complete', true]]);
  assert.ok(again.filter((line) => line.verdict === 'pass').every((line) => !('repeat' in line)));
  assertContentFree(read(path.join(result.outDir, 'status.log')));
});

test('the set scopes and the written confidence fields are asked for no counts', async () => {
  const model = fakeModel(DOCS);
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  assert.match(checksFor(model, 'phase7_sets')[0].user, /Give no count of cards or rules in a scope; each set's rule\s+summary carries the counts\./);
  for (const field of ['remainingRisks', 'assumptions', 'regressionScope', 'breakItScope', 'manualReview']) {
    assert.match(checksFor(model, `phase9_confidence_${field}`)[0].user,
      /Give no count of cards, rules or coverage statuses; the Coverage field carries\s+the counts\./, field);
  }
  // No repair ran after the review wrote its prose, so the pack carries no note about it.
  assert.doesNotMatch(JSON.parse(read(result.packPath)).confidence.manualReview, new RegExp(AGED_NOTE));
});

/** The ID of the card titled `title`, read from a prompt that shows the built workbook. */
const idOfCase = (user, title) => new RegExp(`Test Case ID: (TC-\\S+) \\| Test Case Title: ${title} \\|`).exec(user)[1];
/** A walk whose first pass fails Traceability with a fix that names the card titled `title`. */
const walkNames = (title) => ({ phase9_revalidation: (value, calls) => {
  const { schemaName, user } = calls.at(-1);
  if (schemaName.endsWith('_again')) return value;
  const id = idOfCase(user, title);
  return failCheck(value, 'Traceability complete', `${id} sits in the wrong sets`, `Move ${id} to the sets it belongs in`);
} });
/** A repair that returns each named card as the call showed it, but for `change`. */
const reworked = (change) => (value, calls) => {
  const shown = calls.at(-1).user.split('## Cards named\n\n')[1].split('\n\n## ')[0].trim().split('\n')
    .map((line) => JSON.parse(line));
  return { ...value, coverage: [], limitations: [],
    cards: shown.map(({ module, sourceDocument, ...card }) => ({ ...card, ...change(card) })) };
};
const cardTitled = (pack, title) => pack.testCards.find((card) => card.title === title);
const setsHolding = (pack, card) => pack.testSets.filter((set) => set.cards.includes(card.id))
  .map((set) => set.objective).sort();
const repairBuilds = (outDir) => statusLines(outDir)
  .filter((line) => line.event === 'builder' && line.step === 'revalidation').map((line) => [line.attempt, line.failed]);

test('a repair that gives a quality-derived card the Full Coverage objective ends with the objective gone and the Objective Matrix passing', async () => {
  const run = lib({ phase6_scenarios: inventory([{}, BREAK, {}]), phase6_cards: SETS, ...walkNames('Case S3'),
    phase8_repair: reworked((card) => ({ objectives: [...card.objectives, FULL] })) });
  const result = await runLib(run);
  assert.equal(result.ok, true, JSON.stringify(result));
  // The one repair call named the objective on the quality-derived card.
  assert.equal(callsNamed(run, 'phase8_repair').length, 1);
  const pack = JSON.parse(read(result.packPath));
  const card = cardTitled(pack, 'Case S3');
  assert.equal(card.derivation, 'Quality');
  assert.ok(!card.objectives.includes(FULL));
  assert.deepEqual(setCards(pack, FULL), ['Case S1', 'Case S2']);
  assert.deepEqual([...card.objectives].sort(), setsHolding(pack, card));
  // The rebuild after the repair passes at its first build: no builder repair had to take the objective off.
  assert.deepEqual(repairBuilds(result.outDir), [[0, 0]]);
  const validation = readPack(result.workbook).sheet('Workbook Validation');
  assert.notEqual(validation.rows.find((row) => row.cells.Sheet === 'Objective Matrix').cells.Status, 'FAIL');
});

test('a repaired BREAK IT card stays in the BREAK IT set and out of the core set, and each set counts its cards again', async () => {
  const repaired = async (overrides) => {
    const run = lib({ phase6_scenarios: inventory([{}, BREAK, {}]), phase6_cards: SETS, ...walkNames('Case S2'),
      phase8_repair: reworked(() => ({ objectives: ['Core Change Validation', 'Workflow Validation'] })) }, overrides);
    const result = await runLib(run);
    assert.equal(result.ok, true, JSON.stringify(result));
    assert.deepEqual(repairBuilds(result.outDir), [[0, 0]]);
    return JSON.parse(read(result.packPath));
  };
  const pack = await repaired({});
  const card = cardTitled(pack, 'Case S2');
  assert.deepEqual([...card.objectives].sort(), ['BREAK IT', FULL, 'Workflow Validation']);
  assert.deepEqual(setsHolding(pack, card), ['BREAK IT', FULL, 'Workflow Validation']);
  assert.deepEqual(setCards(pack, 'Core Change Validation'), ['Case S1', 'Case S3']);
  // The sets the card left hold two cards, and their rule summaries say so.
  for (const objective of ['Negative / Exclusion', 'Regression Testing']) {
    assert.deepEqual(setCards(pack, objective), ['Case S1', 'Case S3']);
    assert.match(pack.testSets.find((set) => set.objective === objective).ruleSummary.join(' '), / on 2 card\(s\)$/);
  }
  const alone = await repaired({ exclusiveSets: true });
  assert.deepEqual(cardTitled(alone, 'Case S2').objectives, ['BREAK IT']);
  assert.deepEqual(setsHolding(alone, cardTitled(alone, 'Case S2')), ['BREAK IT']);
});

test('a repair never takes the last card out of a set: the card stays and keeps that objective', async () => {
  const setup = lib({ ...walkFailsOnCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  const failed = await runLib(setup);
  assert.equal(failed.reason, 'gate:revalidation-failed');
  const file = path.join(failed.outDir, 'work', 'checkpoints', 'phase9-revalidate.json');
  const named = cardIdIn(JSON.parse(slurp(file)).state.revalidationChecks.find((row) => row.verdict === 'fail').fix);
  // The Workflow set holds the named card alone; the Regression set holds it with another card.
  editSnapshot(failed.outDir, 'phase9-revalidate', (saved) => {
    const pack = savedPack(saved);
    const other = pack.testCards.find((card) => card.id !== named).id;
    pack.testSets.find((set) => set.objective === 'Workflow Validation').cards = [named];
    pack.testSets.find((set) => set.objective === 'Regression Testing').cards = [named, other];
  });
  const done = await step(setup.config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'last' },
    { model: fakeModel({ phase8_repair: reworked(() => ({ objectives: ['Core Change Validation'] })) }) });
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  const pack = savedPack(readStep(path.join(setup.config.output, done.id)));
  const card = pack.testCards.find((one) => one.id === named);
  assert.deepEqual(pack.testSets.find((set) => set.objective === 'Workflow Validation').cards, [named]);
  assert.ok(card.objectives.includes('Workflow Validation') && card.objectives.includes('Core Change Validation'));
  assert.ok(!pack.testSets.find((set) => set.objective === 'Regression Testing').cards.includes(named));
  assert.ok(!card.objectives.includes('Regression Testing'));
  assert.deepEqual([...card.objectives].sort(), setsHolding(pack, card));
});

test('a repair in a suite pack leaves the sets the suite merge wrote, and the card keeps its objectives', async () => {
  // A suite's cards are numbered under the suite's name.
  const suiteCard = (text) => /TC-[A-Z0-9]+-LIB-\d{3}/.exec(text)[0];
  const model = fakeModel({ ...INTAKE, ...NOT_REMOVAL, phase8_repair: correctingRepair,
    phase9_revalidation: (value, calls) => {
      const { schemaName, user } = calls.at(-1);
      return schemaName.endsWith('_again') ? value : failCheck(value, 'Traceability complete',
        `${suiteCard(user)} reads wrong`, `Change step 1 of ${suiteCard(user)} to read Corrected step`);
    } });
  const result = await runJob(fixtureConfig(), { suite: 'LIB' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const [repair] = checksFor(model, 'phase8_repair_revalidation');
  const named = suiteCard(repair.user.split('## Builder problems')[1]);
  const before = savedPack(JSON.parse(slurp(path.join(result.outDir, 'work', 'checkpoints', 'phase9-confidence.json'))));
  const pack = JSON.parse(read(result.packPath));
  assert.deepEqual(pack.testSets, before.testSets);
  const card = (from) => from.testCards.find((one) => one.id === named);
  assert.equal(card(pack).steps[0].description, 'Corrected step');
  assert.deepEqual(card(pack).objectives, card(before).objectives);
  // A suite pack is given no design rule: its sets are the merge's.
  assert.doesNotMatch(repair.user, /How this pack is built/);
  assert.ok(checksFor(model, 'phase9_revalidation').every((call) => !/How this pack is built/.test(call.user)));
});

test('the checklist reads and the repair between them carry the design rules, and a suite pack\'s checklist carries none', async () => {
  const model = fakeModel({ ...DOCS, phase9_checklist: plantedChecklist(), phase8_repair: correctingRepair });
  const result = await runJob(fixtureConfig(), { issue: '501', change: '7001' }, { model, echo: false });
  assert.equal(result.ok, true, JSON.stringify(result));
  const reads = checksFor(model, 'phase9_checklist');
  assert.deepEqual(reads.map((call) => call.schemaName), ['phase9_checklist', 'phase9_checklist_again']);
  const rules = new RegExp('## How this pack is built\\n\\n[^\\n]*never list an issue because the pack follows one,'
    + ' and never give a fix that would break one\\.\\n'
    + `- The ${FULL} set, and the cards listed for the ${FULL} objective, hold only requirement-derived cards[^\\n]*\\n`
    + '(?:- The BREAK IT set holds only[^\\n]*\\n)?(?:- No test card serves[^\\n]*\\n)?'
    + '- A rule whose summary starts with "Retired:"[^\\n]*consistent as it stands\\.\\n');
  for (const call of reads) assert.match(call.user, rules, call.schemaName);
  // The fix round's repair goes through the call every repair shares, so it carries them too.
  const [repair] = checksFor(model, 'phase8_repair_review_1');
  assert.match(repair.user, new RegExp(`## How this pack is built\\n\\n[^\\n]*applies them again to what you return[^\\n]*\\n- The ${FULL} set, `));
  // A suite pack is given no design rule: its sets are the merge's.
  const suite = fakeModel({ ...INTAKE, ...NOT_REMOVAL });
  const merged = await runJob(fixtureConfig(), { suite: 'LIB' }, { model: suite, echo: false });
  assert.equal(merged.ok, true, JSON.stringify(merged));
  const suiteReads = checksFor(suite, 'phase9_checklist');
  assert.ok(suiteReads.length > 0);
  for (const call of suiteReads) assert.doesNotMatch(call.user, /How this pack is built/, call.schemaName);
});

test('the Coverage field is counted again when a repair changes the Coverage Matrix', async () => {
  const setup = lib({ ...asksNewCard, phase8_repair: correctingRepair });
  addJob(setup.config, { issue: '501', change: '7001' });
  const failed = await runLib(setup);
  uncover(failed.outDir, 'BR-LIB.UC01-001');
  const stale = 'Of 6 rule(s) in the Coverage Matrix: 5 Covered; 1 Missing (BR-LIB.UC01-001).';
  editSnapshot(failed.outDir, 'phase9-revalidate', (saved) => { savedPack(saved).confidence.coverage = stale; });
  const done = await step(setup.config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label: 'count' },
    { model: fakeModel({ phase8_repair: newCardFor }) });
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  const pack = savedPack(readStep(path.join(setup.config.output, done.id)));
  assert.match(pack.confidence.coverage, /^Of \d+ rule\(s\) in the Coverage Matrix: /);
  assert.doesNotMatch(pack.confidence.coverage, /Missing/);
  // A walk step over the repaired pack is told its prose is older than the repair, under its first-walk step name.
  const model = fakeModel();
  const walked = await step(setup.config, { at: done.id, step: 'walk', label: 'walk' }, { model });
  assert.equal(walked.result.ok, true, JSON.stringify(walked.result));
  const calls = checksFor(model, 'phase9_revalidation');
  assert.deepEqual(calls.map((call) => call.schemaName), ['phase9_revalidation_traceability',
    'phase9_revalidation_resolution', 'phase9_revalidation_readiness']);
  for (const call of calls) assert.match(call.user, /## Text written before the repair round\n/, call.schemaName);
  // A second repair step adds no second note.
  const twice = await step(setup.config, { at: done.id, step: 'repair', finding: '0', label: 'twice' },
    { model: fakeModel({ phase8_repair: correctingRepair }) });
  assert.equal(twice.result.ok, true, JSON.stringify(twice.result));
  assert.equal(savedPack(readStep(path.join(setup.config.output, twice.id))).confidence.manualReview
    .split(AGED_NOTE).length, 2);
  // The manual review field written again still says the rest of the prose is older than the repair.
  const again = await step(setup.config, { at: done.id, step: 'confidence', field: 'manualReview', label: 'field' },
    { model: fakeModel() });
  assert.equal(again.result.ok, true, JSON.stringify(again.result));
  const rewritten = savedPack(readStep(path.join(setup.config.output, again.id))).confidence.manualReview;
  assert.match(rewritten, /^The manualReview is covered by /);
  assert.equal(rewritten.split(AGED_NOTE).length, 2);
});

test('a new repair card that cites only a retired rule is rechecked as an absence check, and dropped when it expects live behavior', async () => {
  const RETIRED_RULE = 'BR-LIB.UC01-006';
  const asks = (rule) => ({ phase9_revalidation: (value) => failCheck(value, 'Traceability complete',
    `${rule} has no card`, `Create a new test card for ${rule}`) });
  const cardFor = (rule) => (value, calls) => {
    const reply = newCardFor(value, calls);
    return { ...reply, newCards: reply.newCards.map((card) => ({ ...card, rules: [rule],
      expected: 'The renewed card is saved', steps: card.steps.map((one) => ({ ...one, rules: [rule] })) })) };
  };
  const offered = async (rule, label, edit = () => {}) => {
    const setup = lib({ ...asks(rule), phase8_repair: correctingRepair });
    addJob(setup.config, { issue: '501', change: '7001' });
    const failed = await runLib(setup);
    uncover(failed.outDir, rule);
    editSnapshot(failed.outDir, 'phase9-revalidate', (saved) => edit(savedPack(saved)));
    const before = savedPack(JSON.parse(slurp(path.join(failed.outDir, 'work', 'checkpoints', 'phase9-revalidate.json'))));
    const model = fakeModel({ phase8_repair: cardFor(rule), phase6_recheck: rejectsAll });
    const done = await step(setup.config, { at: 'phase9-revalidate', step: 'repair', finding: '0', label }, { model });
    const pack = savedPack(readStep(path.join(setup.config.output, done.id)));
    return { model, done, added: pack.testCards.filter((card) => !before.testCards.some((old) => old.id === card.id)) };
  };
  const retired = await offered(RETIRED_RULE, 'retired');
  const [repair] = checksFor(retired.model, 'phase8_repair');
  assert.match(repair.user, /A new card for behavior that still happens cites the active rules its\s+expected result exercises, never only rules whose summary starts with "Retired:"/);
  const [recheck] = checksFor(retired.model, 'phase6_recheck_new');
  assert.match(recheck.user, /A card whose every cited rule is marked removed checks that the removed\s+behavior is gone and nothing else, whatever its derivation/);
  assert.match(recheck.user, new RegExp(`- ${RETIRED_RULE.replace(/\./g, '\\.')} [^\\n]*removed: the card must show this no longer happens`));
  // The recheck answered that the card does not follow, so it is left out and the line says undone.
  assert.equal(retired.added.length, 0);
  const line = retired.done.result.lines.map((text) => JSON.parse(text)).find((one) => one.event === 'repair');
  assert.deepEqual([line.asked, line.newCards, line.result], ['new-card', 1, 'undone']);
  // A new card on an active rule is rechecked without that instruction.
  const active = await offered('BR-LIB.UC01-001', 'active');
  assert.doesNotMatch(checksFor(active.model, 'phase6_recheck_new')[0].user, /every cited rule is marked removed/);
  // The repair is still told which rules a new card cites, because the pack holds a retired rule.
  assert.match(checksFor(active.model, 'phase8_repair')[0].user, /never only rules whose summary starts with "Retired:"/);
  // A pack with no retired rule is told nothing about retired rules.
  const none = await offered('BR-LIB.UC01-001', 'none', (pack) => {
    pack.rules.find((one) => one.id === RETIRED_RULE).summary = 'A card expires after a year.';
  });
  const [plain] = checksFor(none.model, 'phase8_repair');
  assert.match(plain.user, /## How this pack is built\n/);
  assert.doesNotMatch(plain.user, /Retired:/);
});

test('the rating made again counts the coverage step again from the Coverage Matrix', async () => {
  const { config, result } = await finishedJob();
  // The state holds a coverage step counted before a repair changed the matrix.
  editSnapshot(result.outDir, 'phase9-revalidate', (saved) => {
    saved.state.confidenceSteps = saved.state.confidenceSteps.map((row) => (row.step === 'coverage'
      ? { ...row, verdict: 'weak', evidence: 'Of 9 rule(s) in the Coverage Matrix: 9 Missing.' } : row));
  });
  const model = fakeModel();
  const done = await step(config, { at: 'phase9-revalidate', step: 'confidence', label: 'rate' }, { model });
  assert.equal(done.result.ok, true, JSON.stringify(done.result));
  const [call] = overallCalls(model);
  assert.match(call.user, /- coverage: strong\. Of \d+ rule\(s\) in the Coverage Matrix: /);
  assert.doesNotMatch(call.user, /9 Missing/);
  const saved = readStep(path.join(config.output, done.id));
  assert.equal(saved.state.confidenceSteps.find((row) => row.step === 'coverage').verdict, 'strong');
});
