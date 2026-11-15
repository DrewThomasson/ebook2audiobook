// The checks of a pack against itself that run before its workbook is written,
// each with a pack that fails it and a pack that passes, then Phase 8 with them.
//
//   node --test plugins/att-docs/skills/build-test-pack/local/pack-checks.test.mjs

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { after, test } from 'node:test';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { confidenceCeiling, draftWorkbook, fixTargets, GateError, holdToCeiling, mergeChecks, phase8, reconcile, REVIEW_SHEETS,
  tidyCard } from './phases.mjs';
import { almStyle } from './compare.mjs';
import { checkPack, derivedSheets } from './pack-checks.mjs';
import { readPack, readSheet } from './pack.mjs';
import { REVALIDATION_CHECKS, REVALIDATION_GROUPS } from './schemas.mjs';
import { statusFields } from './status.mjs';
import { readXlsx } from './xlsx.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES = path.join(HERE, 'fixtures');
const stub = await import(pathToFileURL(path.join(FIXTURES, 'builder-stub.mjs')).href);
// The stub with a `confidenceCeiling` export and a build that fails a rating above it.
const ceilingBuilder = await import(pathToFileURL(path.join(FIXTURES, 'builder-ceiling.mjs')).href);
// Every Draft workbook lands under one root, removed when this file's tests finish.
const SCRATCH_ROOT = fs.mkdtempSync(path.join(os.tmpdir(), 'pack-checks-test-'));
after(() => fs.rmSync(SCRATCH_ROOT, { recursive: true, force: true }));

const rule = (id, extra = {}) => ({ id, name: `Rule ${id}`, module: 'MOD', sourceDocument: 'Doc',
  summary: `${id} summary`, impact: 'Direct Change', risk: 'Medium', ...extra });
const card = (n, rules, objectives) => ({ id: `TC-MOD-501-00${n}`, title: `Card ${n}`, module: 'MOD',
  sourceDocument: 'Doc', mission: 'm', focus: ['f'], expected: 'It works.', rules, objectives,
  derivation: 'Requirement', steps: [{ description: 'Do it', expected: 'It works.', rules }] });

/** A pack every check passes: two cards, a core set and a regression set, one Not Impacted rule. */
function goodPack() {
  const objectives = stub.OBJECTIVES.map((objective) => ({ objective, reason: 'why',
    applicable: ['Core Change Validation', 'Regression Testing'].includes(objective) }));
  return {
    issue: '501', changeDescription: 'A change.', intake: { readiness: 'READY' },
    rules: [rule('BR-1'), rule('BR-2', { impact: 'Regression', risk: 'High' }),
      rule('BR-3', { impact: 'Not Impacted', risk: 'Low' })],
    testCards: [card(1, ['BR-1'], ['Core Change Validation']),
      card(2, ['BR-2'], ['Core Change Validation', 'Regression Testing'])],
    testSets: [
      { number: 1, name: 'TS01 Core Change Validation', objective: 'Core Change Validation',
        cards: ['TC-MOD-501-001', 'TC-MOD-501-002'] },
      { number: 2, name: 'TS02 Regression Testing', objective: 'Regression Testing',
        cards: ['TC-MOD-501-002'] }],
    objectives,
    coverage: [
      { ruleId: 'BR-1', status: 'Covered', strength: 'Strong', gap: 'None identified.', recommendation: 'None needed.' },
      { ruleId: 'BR-2', status: 'Covered', strength: 'Strong', gap: 'None identified.', recommendation: 'None needed.' }],
    assumptions: [], limitations: { Assumptions: 'None were needed.' },
    seniorReview: { a: 'x' }, testerNotes: { a: 'x' },
    confidence: { overall: 'High' }, executiveSummary: { confidence: 'High' },
  };
}

/** Failed sheets by name, as the pipeline would find them: reconcile settles what it can first. */
const problems = (pack, built) => {
  reconcile({}, pack);
  return Object.fromEntries(checkPack(pack, built).failed.map(([sheet, , , , notes]) => [sheet, notes]));
};
/** Warning lines by code, found the same way. */
const warnings = (pack, built) => {
  reconcile({}, pack);
  return Object.fromEntries(checkPack(pack, built).warnings.map(({ code, text }) => [code, text]));
};
const sheetNamed = (sheets, name) => sheets.find((s) => s.name === name);

/** What a builder returns: the derived sheets with `edit` applied. */
const built = (pack, edit = () => {}) => {
  const sheets = derivedSheets(pack);
  edit(sheets);
  return { sheets };
};

test('a pack that disagrees with none of the checks passes them all', () => {
  for (const made of [undefined, built(goodPack())]) {
    const pack = goodPack();
    reconcile({}, pack);
    assert.deepEqual(checkPack(pack, made), { failed: [], warnings: [] });
  }
});

// ---- 1. confidence across sheets ----------------------------------------

test('confidence that differs across the sheets a builder returned is a warning, not a failed sheet', () => {
  const sheets = built(goodPack(), (all) => { sheetNamed(all, 'Confidence Assessment').rows[1][1] = 'Medium'; });
  assert.match(warnings(goodPack(), sheets)['confidence-differs'], /Confidence Assessment: medium/);
  assert.deepEqual(problems(goodPack(), sheets), {});
});

test('a summary whose confidence disagrees with the overall one is settled by reconcile', () => {
  const pack = goodPack();
  pack.executiveSummary.confidence = 'Low';
  assert.deepEqual(warnings(pack), {});
  assert.equal(pack.executiveSummary.confidence, 'High');
});

test('confidence that every sheet states the same passes', () => {
  const pack = goodPack();
  pack.executiveSummary.confidence = 'High. The cards cover every rule.';
  const sheets = built(pack);
  assert.deepEqual(warnings(pack, sheets), {});
});

// ---- 2. dashboard counts --------------------------------------------------

test('a dashboard count that differs from its sheet is a warning', () => {
  const sheets = built(goodPack(), (all) => {
    sheetNamed(all, 'Dashboard').rows.find((r) => /test cards/i.test(r[0]))[1] = 5;
  });
  assert.match(warnings(goodPack(), sheets)['dashboard-count'],
    /Number of Reusable Test Cards reads 5, but the sheet it counts has 2/);
  assert.deepEqual(problems(goodPack(), sheets), {});
});

test('dashboard counts that match their sheets pass', () => {
  assert.deepEqual(warnings(goodPack(), built(goodPack())), {});
});

test('a rule count that leaves Not Impacted rules out passes only when the label says impacted', () => {
  const edit = (label) => built(goodPack(), (all) => {
    sheetNamed(all, 'Dashboard').rows.find((r) => /rules/i.test(r[0]))[0] = label;
  });
  assert.deepEqual(warnings(goodPack(), edit('Number of Impacted Business Rules')), {});
  assert.match(warnings(goodPack(), edit('Number of Business Rules'))['dashboard-count'], /reads 2, but .* has 3/);
});

test('a rule count that reads "N impacted of M" is checked against both counts, and a mismatch says what the sheet holds', () => {
  const edit = (value) => built(goodPack(), (all) => {
    sheetNamed(all, 'Dashboard').rows.find((r) => /rules/i.test(r[0]))[1] = value;
  });
  assert.deepEqual(warnings(goodPack(), edit('2 impacted of 3')), {});
  assert.deepEqual(warnings(goodPack(), edit('2 of 3')), {});
  const sets = built(goodPack(), (all) => {
    sheetNamed(all, 'Dashboard').rows.find((r) => /test sets/i.test(r[0]))[1] = '1 of 2';
  });
  assert.deepEqual(warnings(goodPack(), sets), {});
  assert.match(warnings(goodPack(), edit('3 impacted of 3'))['dashboard-count'],
    /reads 3, but the sheet it counts has 2 \(3 rule rows, 2 of them impacted\)\./);
  assert.match(warnings(goodPack(), edit('2 impacted of 5'))['dashboard-count'],
    /reads 5, but the sheet it counts has 3 \(3 rule rows, 2 of them impacted\)\./);
});

test('sheets with a title and a subtitle above their headers are checked like sheets that lead with them', () => {
  const titled = (edit = () => {}) => {
    const sheets = derivedSheets(goodPack());
    edit(sheets);
    return { sheets: sheets.map(({ name, rows }) => ({ name, rows: [[`${name} title`], ['A subtitle'], [], ...rows] })) };
  };
  assert.deepEqual(warnings(goodPack(), titled()), {});
  const wrong = titled((all) => { sheetNamed(all, 'Dashboard').rows.find((r) => /test cards/i.test(r[0]))[1] = 5; });
  assert.match(warnings(goodPack(), wrong)['dashboard-count'], /Number of Reusable Test Cards reads 5/);
});

test('the stub builder writes the reference pack\'s layout: title, subtitle, headers in row 4, an ID-only Test Name', (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'stub-layout-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const pack = goodPack();
  fs.writeFileSync(path.join(dir, 'pack.json'), JSON.stringify(pack));
  const run = spawnSync(process.execPath, [path.join(HERE, 'fixtures', 'builder-stub.mjs'), path.join(dir, 'pack.json'),
    '--out', dir], { encoding: 'utf8' });
  assert.equal(run.status, 0, run.stderr);
  const book = readPack(path.join(dir, 'ISSUE501_Pack.xlsx'));
  for (const sheet of book.sheets) {
    assert.equal(sheet.headerRow, 4, sheet.name);
    assert.ok(sheet.title && sheet.subtitle, sheet.name);
  }
  assert.deepEqual(book.steps.map((s) => s.testName), ['TC-MOD-501-001', 'TC-MOD-501-002']);
  assert.equal(almStyle(book).testNameForm, 'card ID only');
  assert.ok(book.sheet('dashboard').rows.some((r) => r.cells.Item === 'Number of Impacted Business Rules'));
});

// ---- 3. covered rows ------------------------------------------------------

test('a Covered row with a blank Gap or Recommendation fails when a builder returns it blank', () => {
  const sheets = built(goodPack(), (all) => {
    const rows = sheetNamed(all, 'Coverage Matrix').rows;
    rows.find((r) => r[0] === 'BR-1')[2] = ' ';
    rows.find((r) => r[0] === 'BR-2')[3] = '';
  });
  const found = problems(goodPack(), sheets)['Coverage Matrix'];
  assert.match(found, /BR-1 is Covered but has a blank Gap \/ Concern\./);
  assert.match(found, /BR-2 is Covered but has a blank Recommendation\./);
});

test('reconcile gives a Covered row the review left blank honest text, and the row then passes', () => {
  const pack = goodPack();
  pack.coverage[0].gap = ' ';
  pack.coverage[1].recommendation = '';
  pack.coverage.pop();
  assert.deepEqual(problems(pack), {});
  const [one, two] = pack.coverage;
  assert.equal(one.gap, 'Not reviewed; coverage rests on the card mapping (TC-MOD-501-001).');
  assert.equal(two.gap, 'Not reviewed; coverage rests on the card mapping (TC-MOD-501-002).');
  assert.equal(two.recommendation, 'Confirm in review that the cards exercise this rule.');
});

test('a Covered row with both fields written passes', () => {
  assert.equal(problems(goodPack())['Coverage Matrix'], undefined);
});

// ---- 4. cards citing rules the matrix lacks -------------------------------

test('a card that cites a rule the Rule-to-Test Matrix has no row for fails', () => {
  const pack = goodPack();
  pack.testCards[0].rules = ['BR-1', 'BR-99'];
  assert.match(problems(pack)['Rule-to-Test Matrix'], /TC-MOD-501-001 cites BR-99/);
});

test('a card citing an unknown rule is left out when the builder already failed that sheet for it', () => {
  const pack = goodPack();
  pack.testCards[0].rules = ['BR-1', 'BR-99'];
  reconcile({}, pack);
  const builderFailed = [['Rule-to-Test Matrix', 'Yes', 'Yes', 'FAIL', 'TC-MOD-501-001 names unknown rule BR-99']];
  assert.deepEqual(checkPack(pack, { failed: builderFailed }).failed, []);
});

test('cards that cite only rules the matrix lists pass', () => {
  assert.equal(problems(goodPack())['Rule-to-Test Matrix'], undefined);
});

// ---- 5. objective matrix cards --------------------------------------------

test('an Objective Matrix row that lists a card its set does not hold fails', () => {
  const sheets = built(goodPack(), (all) => {
    sheetNamed(all, 'Objective Matrix').rows.find((r) => r[0] === 'Regression Testing')[2] += '\nTC-MOD-501-001';
  });
  assert.match(problems(goodPack(), sheets)['Objective Matrix'], /Regression Testing lists TC-MOD-501-001/);
});

test('Objective Matrix rows that list only cards their sets hold pass', () => {
  assert.equal(problems(goodPack(), built(goodPack()))['Objective Matrix'], undefined);
});

// ---- 6. the set column of the rule-to-test matrix -------------------------

test('a Rule-to-Test row whose set column leaves out a set its card is in is a warning', () => {
  const sheets = built(goodPack(), (all) => {
    sheetNamed(all, 'Rule-to-Test Matrix').rows.find((r) => r[0] === 'BR-2')[4] = 'TS01 Core Change Validation';
  });
  assert.match(warnings(goodPack(), sheets)['set-column'],
    /BR-2 lists TC-MOD-501-002, but its test sets leave out TS02 Regression Testing/);
  assert.equal(problems(goodPack(), sheets)['Rule-to-Test Matrix'], undefined);
});

test('a test set with no number in its name is not read as missing from every row', () => {
  const pack = goodPack();
  pack.testSets[1] = { ...pack.testSets[1], number: '', name: 'Regression pass' };
  assert.deepEqual(warnings(pack, built(pack)), {});
});

test('a Rule-to-Test row that names every set its cards are in passes', () => {
  assert.deepEqual(warnings(goodPack(), built(goodPack())), {});
});

// ---- 7. high-risk Not Impacted rules --------------------------------------

test('a High-risk Not Impacted rule with no regression card and no reason fails', () => {
  const pack = goodPack();
  pack.rules[2].risk = 'High';
  assert.match(problems(pack)['Coverage Matrix'], /BR-3 is High risk and Not Impacted, but no regression card/);
});

test('a High-risk Not Impacted rule with a blank or review-filled gap still fails after reconcile', () => {
  for (const gap of ['', 'Not stated by the review.']) {
    const pack = goodPack();
    pack.rules[2].risk = 'High';
    pack.testCards.push(card(3, ['BR-3'], ['Core Change Validation']));
    pack.testSets[0].cards.push('TC-MOD-501-003');
    pack.coverage.push({ ruleId: 'BR-3', status: 'Covered', strength: 'Strong', gap, recommendation: '' });
    const found = problems(pack, built(pack))['Coverage Matrix'];
    assert.match(found, /BR-3 is High risk and Not Impacted, but no regression card/);
    assert.match(found, /keep a covering status \(Covered, Partially Covered or Weakly Covered\) rather than Not Applicable/);
  }
});

test('a High-risk Not Impacted rule passes with a regression card or a stated reason', () => {
  const withCard = goodPack();
  withCard.rules[2].risk = 'High';
  withCard.testCards.push(card(3, ['BR-3'], ['Regression Testing']));
  withCard.testSets[1].cards.push('TC-MOD-501-003');
  withCard.coverage.push({ ruleId: 'BR-3', status: 'Covered', strength: 'Strong',
    gap: 'None identified.', recommendation: 'None needed.' });
  assert.deepEqual(problems(withCard), {});
  const withReason = goodPack();
  withReason.rules[2].risk = 'High';
  withReason.coverage.push({ ruleId: 'BR-3', status: 'Not Applicable', strength: 'None',
    gap: 'The change does not touch it, and the rule has its own suite.', recommendation: 'None.' });
  assert.deepEqual(problems(withReason), {});
});

// ---- Phase 8 ----------------------------------------------------------------

const STUB_COMMAND = ['node', 'builder-stub.mjs', '{pack}', '--out', '{out}'];
/** The stub's command with a ceiling on the assumptions each confidence allows. */
const CEILING_COMMAND = ['node', 'builder-ceiling.mjs', '{pack}', '--out', '{out}'];

/**
 * The parts of the pipeline's context that Phase 8 reads, over a model that answers from
 * `reply`. The Draft workbook is written under a new temporary folder with `command`.
 */
function context(pack, { reply, builder = stub, retries = 2, command = STUB_COMMAND } = {}) {
  const calls = [];
  const output = fs.mkdtempSync(path.join(SCRATCH_ROOT, 'job-'));
  return { calls, ctx: {
    pack, builder, job: { id: 'job' }, repairs: 0, calls: 0, tokens: { prompt: 0, output: 0 },
    logs: { status() {}, detail() {}, call() {} },
    config: { root: FIXTURES, output, builder: { retries, command },
      model: { context: 1e6, maxOutput: 100, reasoningOutput: 100 } },
    ref: { docs: { workbookStandard: '' }, core: [], chapters: () => [] },
    model: {
      countTokens: async () => 1,
      async json(request) {
        calls.push(request);
        return { value: reply(request), usage: { promptTokens: 1, outputTokens: 1, ms: 1 } };
      },
    },
  } };
}
const nothing = () => ({ cards: [], limitations: [], coverage: [] });
const reviewDir = (ctx) => path.join(ctx.config.output, ctx.job.id, 'work', 'review');
/** The pack the Draft workbook was written from. */
const draftJson = (ctx) => JSON.parse(fs.readFileSync(path.join(reviewDir(ctx), 'draft-pack.json'), 'utf8'));
/** A sheet of the Draft workbook as its Field or Item rows, each with its Value. */
function draftFields(ctx, name) {
  const book = fs.readdirSync(reviewDir(ctx)).find((file) => file.endsWith('.xlsx'));
  const sheet = readXlsx(path.join(reviewDir(ctx), book)).map(readSheet).find((s) => s.name === name);
  return Object.fromEntries(sheet.rows.map(({ cells }) => [cells.Field ?? cells.Item, cells.Value]));
}
const assumptions = (count) => Array.from({ length: count }, (_, i) => ({ assumption: `Assumption ${i + 1}.`,
  why: 'The documents leave it open.', impact: 'Cards rest on it.', clarification: 'Confirm it.' }));

test('Phase 8 rebuilds a pack rated Medium under its assumption limit with Medium in the Draft workbook', async () => {
  const pack = goodPack();
  pack.assumptions = assumptions(5);
  pack.confidence = { overall: 'Medium', reason: 'Two cards cover the change.' };
  pack.executiveSummary = { confidence: 'Medium. Two cards cover the change.' };
  const { ctx, calls } = context(pack, { reply: nothing, command: CEILING_COMMAND });
  await phase8(ctx, pack, 'rebuild');
  assert.equal(calls.length, 0);
  assert.equal(draftFields(ctx, 'Confidence Assessment').overall, 'Medium');
  assert.equal(draftFields(ctx, 'Executive Summary').confidence, 'Medium. Two cards cover the change.');
  assert.equal(draftFields(ctx, 'Dashboard')['Overall Confidence'], 'Medium');
  assert.equal(draftJson(ctx).limitations['Confidence Assessment'], undefined);
  assert.deepEqual([pack.confidence.overall, pack.limitations?.['Confidence Assessment']], ['Medium', undefined]);
});

test('Phase 8 writes an unrated pack past every assumption limit as a Low Draft workbook and leaves the pack unrated', async () => {
  const pack = goodPack();
  pack.assumptions = assumptions(12);
  pack.confidence = {};
  pack.executiveSummary = { confidence: 'Medium' };
  const { ctx, calls } = context(pack, { reply: nothing, command: CEILING_COMMAND });
  await phase8(ctx, pack, 'build', REVIEW_SHEETS);
  assert.equal(calls.length, 0);
  assert.equal(draftFields(ctx, 'Confidence Assessment').overall, 'Low');
  assert.equal(draftFields(ctx, 'Executive Summary').confidence, 'Low');
  assert.equal(draftJson(ctx).limitations['Confidence Assessment'], 'Pending review.');
  assert.deepEqual([pack.confidence, pack.executiveSummary.confidence, pack.limitations['Confidence Assessment']],
    [{}, 'Medium', undefined]);
});

/** A pack rated `overall` that carries `count` assumptions. */
function ratedPack(overall, count) {
  const pack = goodPack();
  pack.assumptions = assumptions(count);
  pack.limitations = {};
  pack.confidence = { overall, reason: 'Two cards cover the change.' };
  pack.executiveSummary = { confidence: `${overall}. Two cards cover the change.` };
  return pack;
}
const LOWERED = 'Two cards cover the change. The rating was lowered to what the pack supports:';

test('the rebuild lowers a rating above the confidence ceiling in code, and the builder passes the pack', async () => {
  const pack = ratedPack('Medium', 12);
  const { ctx, calls } = context(pack, { reply: nothing, builder: ceilingBuilder, command: CEILING_COMMAND });
  const lines = [];
  ctx.logs.status = (line) => lines.push(statusFields(line));
  await phase8(ctx, pack, 'rebuild');
  assert.equal(calls.length, 0);
  const reason = `${LOWERED} 12 assumptions against a limit of 10.`;
  assert.deepEqual([pack.confidence.overall, pack.confidence.reason, pack.limitations['Confidence Assessment'],
    pack.executiveSummary.confidence], ['Low', reason, reason, `Low. ${reason}`]);
  // One line, with the two levels and the reason code and nothing the builder said.
  assert.deepEqual(lines.filter((line) => line.event === 'confidence-lowered'), [{ job: 'job', phase: 'phase9',
    step: 'confidence-ceiling', event: 'confidence-lowered', overall: 'Low', asked: 'Medium', reason: 'confidence-ceiling' }]);
  assert.deepEqual(lines.filter((line) => line.event === 'builder').map((line) => [line.attempt, line.failed]), [[0, 0]]);
  assert.deepEqual(ceilingBuilder.buildPack(pack).failed, []);
  assert.equal(draftFields(ctx, 'Confidence Assessment').overall, 'Low');
  assert.equal(draftFields(ctx, 'Dashboard')['Overall Confidence'], 'Low');
});

test('a builder with no confidenceCeiling export leaves a rating above the ceiling to the builder, which refuses it', async () => {
  const pack = ratedPack('Medium', 12);
  const { ctx, calls } = context(pack, { reply: nothing, retries: 1, command: CEILING_COMMAND });
  const lines = [];
  ctx.logs.status = (line) => lines.push(line);
  await assert.rejects(phase8(ctx, pack, 'rebuild'), (error) => error instanceof GateError && error.code === 'builder-fail');
  assert.equal(calls.length, 1);
  assert.equal(pack.confidence.overall, 'Medium');
  assert.ok(!lines.some((line) => line.event === 'confidence-lowered'));
  assert.deepEqual(confidenceCeiling(ctx, pack), { level: 'High', allowed: ['High', 'Medium', 'Low'], reasons: [] });
});

test('the confidence ceiling reads the builder\'s level and reasons, and a level the builder does not list sets none', () => {
  const ctx = { builder: ceilingBuilder };
  assert.deepEqual(confidenceCeiling(ctx, ratedPack('High', 5)),
    { level: 'Medium', allowed: ['Medium', 'Low'], reasons: ['5 assumptions against a limit of 3'] });
  assert.deepEqual(confidenceCeiling(ctx, ratedPack('High', 2)),
    { level: 'High', allowed: ['High', 'Medium', 'Low'], reasons: [] });
  const odd = { builder: { ...stub, confidenceCeiling: () => ({ level: 'Moderate', reasons: ['a reason'] }) } };
  assert.deepEqual(confidenceCeiling(odd, ratedPack('High', 5)),
    { level: 'High', allowed: ['High', 'Medium', 'Low'], reasons: [] });
});

test('a rating is lowered only when it is above the ceiling, and a second lowering keeps one sentence for it', () => {
  const ctx = { builder: ceilingBuilder };
  const pack = ratedPack('High', 5);
  holdToCeiling(ctx, pack);
  assert.deepEqual([pack.confidence.overall, pack.confidence.reason, pack.limitations['Confidence Assessment']],
    ['Medium', `${LOWERED} 5 assumptions against a limit of 3.`, undefined]);
  // At its ceiling the pack is left alone.
  const settled = structuredClone(pack);
  holdToCeiling(ctx, pack);
  assert.deepEqual(pack, settled);
  // More assumptions lower the ceiling again; the reason names the ceiling the pack now sits at.
  pack.assumptions = assumptions(12);
  holdToCeiling(ctx, pack);
  assert.deepEqual([pack.confidence.overall, pack.confidence.reason],
    ['Low', `${LOWERED} 12 assumptions against a limit of 10.`]);
  assert.equal(pack.limitations['Confidence Assessment'], pack.confidence.reason);
  // An unrated pack has no level to lower, and a context with no builder sets no ceiling.
  const unrated = { ...ratedPack('High', 12), confidence: {} };
  holdToCeiling(ctx, unrated);
  assert.deepEqual(unrated.confidence, {});
  const bare = ratedPack('High', 12);
  reconcile({}, bare);
  assert.equal(bare.confidence.overall, 'High');
});

test('a lowered reason states no level but the ceiling\'s, and a rating with no reason of its own takes the lowering sentence', () => {
  const ctx = { builder: ceilingBuilder };
  const stated = ratedPack('High', 5);
  stated.confidence.reason = 'Confidence is High for BR-1.';
  holdToCeiling(ctx, stated);
  assert.equal(stated.executiveSummary.confidence,
    'Medium. confidence for BR-1. The rating was lowered to what the pack supports: 5 assumptions against a limit of 3.');
  const plain = ratedPack('High', 5);
  plain.confidence = { overall: 'High', reason: 'Overall confidence is High.' };
  holdToCeiling(ctx, plain);
  assert.equal(plain.confidence.reason, 'The rating was lowered to what the pack supports: 5 assumptions against a limit of 3.');
});

test('the Draft workbook of a pack rated above its ceiling reads the ceiling, with no status line and the pack left as it was', () => {
  const pack = ratedPack('Medium', 12);
  const { ctx } = context(pack, { reply: nothing, builder: ceilingBuilder, command: CEILING_COMMAND });
  const lines = [];
  ctx.logs.status = (line) => lines.push(line);
  const before = structuredClone(pack);
  const draft = draftWorkbook(ctx, pack, 'review');
  assert.ok(draft.workbook, draft.text);
  assert.equal(draftJson(ctx).confidence.overall, 'Low');
  assert.deepEqual(lines, []);
  assert.deepEqual(pack, before);
});

test('Phase 8 sends a failed check to repair, and the repaired pack passes', async () => {
  const pack = goodPack();
  pack.rules[2].risk = 'High';
  const { ctx, calls } = context(pack, { reply: () => ({ cards: [], limitations: [], coverage: [
    { ruleId: 'BR-3', status: 'Not Applicable', strength: 'None',
      gap: 'The change does not touch it.', recommendation: 'None.' }] }) });
  await phase8(ctx, pack);
  assert.equal(calls.length, 1);
  assert.match(calls[0].user, /Coverage Matrix:\nBR-3 is High risk and Not Impacted/);
  assert.equal(ctx.repairs, 1);
  assert.deepEqual(checkPack(pack).failed, []);
});

test('Phase 8 states the Phase 3 rationale as the reason for a High-risk Not Impacted rule without asking the model', async () => {
  const pack = goodPack();
  Object.assign(pack.rules[2], { risk: 'High', rationale: 'The change does not touch it.' });
  const { ctx, calls } = context(pack, { reply: () => assert.fail('the model was asked') });
  await phase8(ctx, pack);
  assert.equal(calls.length, 0);
  const row = pack.coverage.find((r) => r.ruleId === 'BR-3');
  assert.equal(row.status, 'Not Applicable');
  assert.match(row.gap, /^The change does not touch it; no regression card is needed\./);
  assert.deepEqual(checkPack(pack).failed, []);
});

test('Phase 8 keeps a covering status when a card covers the rule and states the rationale as the reason', async () => {
  const pack = goodPack();
  Object.assign(pack.rules[2], { risk: 'High', rationale: 'The change does not touch it.' });
  pack.testCards[0].rules.push('BR-3');
  pack.coverage.push({ ruleId: 'BR-3', status: 'Weakly Covered', strength: 'Weak', gap: 'Not stated by the review.', recommendation: 'Confirm it.' });
  const { ctx } = context(pack, { reply: (r) => assert.fail(r.user) });
  await phase8(ctx, pack);
  assert.equal(pack.coverage.find((r) => r.ruleId === 'BR-3').status, 'Weakly Covered');
});

test('Phase 8 leaves other problems to the model and never shows it the reason it filled in code', async () => {
  const pack = goodPack();
  Object.assign(pack.rules[2], { risk: 'High', rationale: 'The change does not touch it.' });
  pack.testCards[0].rules = ['BR-1', 'BR-99'];
  const { ctx, calls } = context(pack, { reply: nothing });
  ctx.description = 'Removes the warning.';
  ctx.summary = { existingBehavior: 'A warning shows today.', newBehavior: 'No warning shows.' };
  await phase8(ctx, pack).catch(() => {});
  assert.ok(calls.length >= 1);
  assert.doesNotMatch(calls[0].user, /BR-3 is High risk/);
  assert.doesNotMatch(calls[0].user, /Coverage Matrix:\s*(\n\n|$)/);
  assert.match(calls[0].user, /Existing behavior[\s\S]*A warning shows today\./);
  assert.match(calls[0].user, /New behavior[\s\S]*No warning shows\./);
  assert.match(calls[0].user, /Change description[\s\S]*Removes the warning\./);
});

test('Phase 8 moves a stale covering row to Not Applicable when no card covers the rule', async () => {
  const pack = goodPack();
  Object.assign(pack.rules[2], { risk: 'High', rationale: 'The change does not touch it.' });
  pack.coverage.push({ ruleId: 'BR-3', status: 'Covered', strength: 'Strong', gap: '', recommendation: '' });
  const { ctx } = context(pack, { reply: (r) => assert.fail(r.user) });
  await phase8(ctx, pack);
  const row = pack.coverage.find((r) => r.ruleId === 'BR-3');
  assert.equal(row.status, 'Not Applicable');
  assert.match(row.gap, /^The change does not touch it; no regression card is needed\./);
});

test('a repair sends a High-risk Not Impacted rule with a thin rationale to the model', async () => {
  const pack = goodPack();
  Object.assign(pack.rules[2], { risk: 'High', rationale: 'Not affected.' });
  const { ctx, calls } = context(pack, { reply: () => ({ cards: [], limitations: [], coverage: [] }) });
  await phase8(ctx, pack).catch(() => {});
  assert.match(calls[0].user, /BR-3 is High risk and Not Impacted/);
});

test('tidyCard gives a blank setup step a result and leaves the last step alone', () => {
  const tidy = tidyCard({ rules: ['BR-1'], steps: [
    { description: 'Sign in', expected: '', rules: [] },
    { description: 'Open the page', expected: '  ', rules: [] },
    { description: 'Check the page', expected: 'The page shows the role.', rules: ['BR-1'] }] }, new Set(['BR-1']));
  assert.deepEqual(tidy.steps.map((step) => step.expected), [
    'The step completes with no error shown.', 'The step completes with no error shown.',
    'The page shows the role.']);
  const blankLast = tidyCard({ rules: ['BR-1'], steps: [
    { description: 'Check', expected: '', rules: ['BR-1'] }] }, new Set(['BR-1']));
  assert.equal(blankLast.steps[0].expected, '');
});

test('Phase 8 fails the build when a check still fails after the repairs', async () => {
  const pack = goodPack();
  pack.testCards[0].rules = ['BR-1', 'BR-99'];
  const { ctx, calls } = context(pack, { retries: 1, reply: nothing });
  await assert.rejects(phase8(ctx, pack), (error) => error instanceof GateError && error.code === 'builder-fail');
  assert.equal(calls.length, 1);
});

test('Phase 8 logs a builder sheet that disagrees with the pack as a warning and still builds', async () => {
  const lying = { ...stub, buildPack: (p) => ({ ...stub.buildPack(p),
    sheets: derivedSheets(p).map((sheet) => (sheet.name === 'Dashboard'
      ? { ...sheet, rows: sheet.rows.map((r) => (/test sets/i.test(r[0]) ? [r[0], 9] : r)) } : sheet)) }) };
  const pack = goodPack();
  const { ctx, calls } = context(pack, { builder: lying, reply: nothing });
  const logged = [];
  ctx.logs.detail = (name, text) => logged.push([name, text]);
  await phase8(ctx, pack);
  assert.equal(calls.length, 0);
  const line = logged.find(([name]) => name.startsWith('builder warning dashboard-count'));
  assert.match(line[1], /Number of Applicable Test Sets reads 9, but the sheet it counts has 2/);
});

test('Phase 8 settles confidence, and Covered rows the review left blank, in code without a model call', async () => {
  const pack = goodPack();
  pack.executiveSummary.confidence = 'Low';
  pack.coverage[0].gap = '';
  pack.coverage[0].recommendation = '';
  pack.coverage.pop();
  const { ctx, calls } = context(pack, { reply: () => assert.fail('no model call expected') });
  await phase8(ctx, pack);
  assert.equal(calls.length, 0);
  assert.equal(pack.executiveSummary.confidence, 'High');
  assert.deepEqual(pack.coverage.map((r) => [r.ruleId, r.gap, r.recommendation]).sort(),
    [['BR-1', 'Not reviewed; coverage rests on the card mapping (TC-MOD-501-001).',
      'Confirm in review that the cards exercise this rule.'],
    ['BR-2', 'Not reviewed; coverage rests on the card mapping (TC-MOD-501-002).',
      'Confirm in review that the cards exercise this rule.']]);
});

test('reconcile adds no Covered row beside a review row that said Missing without a gap', () => {
  const pack = goodPack();
  pack.coverage[0] = { ruleId: 'BR-1', status: 'Missing', strength: 'None', gap: '', recommendation: 'x' };
  reconcile({}, pack);
  assert.equal(pack.coverage.find((r) => r.ruleId === 'BR-1'), undefined);
});

test('a review row that says Missing for a rule a card covers keeps its gap text through reconcile, the check and the repair input', async () => {
  const pack = goodPack();
  pack.coverage[0] = { ruleId: 'BR-1', status: 'Missing', strength: 'None',
    gap: 'Card never selects Ok.', recommendation: 'Add the step.' };
  reconcile({}, pack);
  const kept = pack.coverage.find((r) => r.ruleId === 'BR-1');
  assert.deepEqual([kept.status, kept.gap], ['Missing', 'Card never selects Ok.']);
  assert.match(checkPack(pack).failed[0][4],
    /BR-1 reads Missing, but a test card covers it\. The review said: Card never selects Ok\. Set the status to Covered, Partially Covered or Weakly Covered and put the reason in Gap/);
  const { ctx, calls } = context(pack, { reply: () => ({ cards: [], limitations: [], coverage: [
    { ruleId: 'BR-1', status: 'Covered', strength: 'Strong', gap: 'The step was added.', recommendation: 'None.' }] }) });
  await phase8(ctx, pack);
  assert.match(calls[0].user, /Card never selects Ok\./);
  assert.equal(ctx.repairs, 1);
});

test('reconcile leaves a Covered row that states a gap as written', () => {
  const pack = goodPack();
  pack.coverage[0].gap = 'Only the happy path.';
  reconcile({}, pack);
  assert.equal(pack.coverage.find((r) => r.ruleId === 'BR-1').gap, 'Only the happy path.');
});

// ---- Phase 9 fix routing -----------------------------------------------------

test('fixTargets reads whole card IDs, rule IDs and sheet names from a finding', () => {
  const pack = { testCards: [{ id: 'TC-1', rules: ['BR-1'] }], rules: [{ id: 'BR-1' }, { id: 'BR-10' }] };
  const ctx = { builder: stub };
  const to = fixTargets(ctx, pack, { issue: 'BR-10 is thin in the coverage matrix', fix: 'Raise BR-10 on TC-1' });
  assert.deepEqual(to.rules, ['BR-10']);
  assert.deepEqual(to.cards, ['TC-1']);
  assert.ok(to.sheets.includes('Coverage Matrix'));
  assert.equal(fixTargets(ctx, pack, { issue: 'BR-1 is thin', fix: 'N/A' }), null);
  assert.equal(fixTargets(ctx, pack, { issue: 'Something', fix: 'Review everything again' }), null);
});

test('mergeChecks fails a check one part fails, passes one a part shows passing, fails one no part shows', () => {
  const NOT = 'not shown in this part';
  const row = (check, verdict, why = '', fix = '') => ({ check, verdict, why, fix });
  const all = (verdict) => ['All issues resolved', 'No regressions introduced', 'Requirement ID references preserved',
    'Requirements Matrix integrity preserved', 'Traceability complete',
    'No uncovered Requirement IDs remain unless explicitly documented',
    'Test pack is ready for ALM execution'].map((check) => row(check, verdict));
  const one = { checks: all('pass').map((r) => (r.check === 'Traceability complete' ? row(r.check, 'fail', 'Lost', 'Fix it') : r)) };
  const two = { checks: all(NOT) };
  const merged = mergeChecks([one, two]);
  assert.equal(merged.passed, false);
  assert.deepEqual(merged.remaining, ['Traceability complete: Lost']);
  assert.equal(mergeChecks([{ checks: all('pass') }, two]).passed, true);
  const none = mergeChecks([two]);
  assert.equal(none.remaining.length, 7);
  assert.match(none.remaining[0], /Not evidenced/);
});

test('the groups of checks the revalidation walk asks together hold each check once, and their answers merge to one verdict per check', () => {
  const grouped = REVALIDATION_GROUPS.flatMap((group) => group.checks);
  assert.deepEqual([...grouped].sort(), [...REVALIDATION_CHECKS].sort());
  const answer = (group, fail) => ({ checks: group.checks.map((check) => (check === fail
    ? { check, verdict: 'fail', why: 'Lost', fix: 'Add a card for it' } : { check, verdict: 'pass', why: '', fix: '' })) });
  const merged = mergeChecks(REVALIDATION_GROUPS.map((group) => answer(group)));
  assert.equal(merged.passed, true);
  assert.deepEqual(merged.checks.map((row) => row.check), REVALIDATION_CHECKS);
  // One group's failed check fails the pack and keeps its fix for the repair round.
  const failed = mergeChecks(REVALIDATION_GROUPS.map((group) => answer(group, 'Traceability complete')));
  assert.equal(failed.passed, false);
  assert.deepEqual(failed.checks.find((row) => row.check === 'Traceability complete'),
    { check: 'Traceability complete', verdict: 'fail', why: 'Lost', fix: 'Add a card for it' });
  assert.deepEqual(failed.remaining, ['Traceability complete: Lost']);
  // A group left out of the walk leaves its checks unevidenced.
  assert.equal(mergeChecks(REVALIDATION_GROUPS.slice(1).map((group) => answer(group))).remaining.length, 4);
});
