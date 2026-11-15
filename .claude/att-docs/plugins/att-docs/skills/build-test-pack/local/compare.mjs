// Scores a test pack against a reference pack and against the source, in three
// parts that write compare.json and compare.md:
//
//   Format  the layout, header rows, header names, ID pattern and ALM step
//           style, against the reference and the workbook standard.
//   Truth   every rule row, retired rule, rule wording, citation and Expected
//           Result against the approved rules and the document. Both
//           workbooks are checked the same way.
//   Floor   each reference scenario matched by a pack card, repeats in the
//           pack, and how the test sets hold the cards.
//
// None of it calls a model unless asked to (`model` in runCompare).

import fs from 'node:fs';
import path from 'node:path';
import { consistencyChecks } from './consistency.mjs';
import { controlNames, crosswalkCards, repeatedCards, scenarioModel, setReport, splitGroups } from './floor.mjs';
import { readPack, stepsOf } from './pack.mjs';
import { qualityChecks } from './quality.mjs';
import { fromWire } from './schemas.mjs';
import { impossibleSteps, stepRules, stepSchema, STEP_QUESTION } from './steps.mjs';
import { dice, loadRules, parseDoc, quoteOf, wordSet, words } from './source.mjs';
import { citedIds, citedRules, crosswalkRows, expectedResultChecks, retiredRecord, retiredRules, staleHits,
  struckOnlyWords } from './truth.mjs';

const lc = (text) => String(text).toLowerCase();
const same = (a, b) => lc(a).trim() === lc(b).trim();

// ---- workbook standard -------------------------------------------------

/**
 * What a workbook standard requires, read from its Markdown: the worksheets
 * of its numbered "Required Worksheets" list, and for each worksheet section
 * the bullets under a line ending "Include:", "Columns:", "Required columns:"
 * or "Summarize:". Returns { sheets, items } with `items` keyed by sheet name.
 */
export function parseStandard(markdown) {
  const sections = String(markdown).split(/^## /m).slice(1).map((part) => {
    const [title, ...rest] = part.split('\n');
    return { title: title.trim(), lines: rest };
  });
  const list = sections.find((s) => /^required worksheets$/i.test(s.title));
  const sheets = (list?.lines ?? []).map((l) => /^\d+\.\s+(.+?)\s*$/.exec(l)?.[1]).filter(Boolean);
  const items = {};
  for (const section of sections) {
    if (!sheets.includes(section.title)) continue;
    const at = section.lines.findIndex((l) => /(?:include|columns|summarize)\s*:\s*$/i.test(l.trim()));
    if (at < 0) continue;
    const bullets = [];
    for (const line of section.lines.slice(at + 1)) {
      const bullet = /^\s*-\s+(.+?)\s*$/.exec(line)?.[1];
      if (bullet) bullets.push(bullet);
      else if (line.trim() && bullets.length) break;
    }
    items[section.title] = bullets;
  }
  return { sheets, items };
}

// ---- format ------------------------------------------------------------

/** The shape of a test case ID: letters become A and digits 9, so TC-ABC-1234-001 is AA-AAA-9999-999. */
export const idShape = (id) => String(id).replace(/[A-Za-z]/g, 'A').replace(/\d/g, '9');

/** How a pack writes its ALM steps. */
export function almStyle(pack) {
  const perCard = pack.cards.map((c) => stepsOf(pack, c.id));
  const counts = perCard.map((s) => s.length).filter(Boolean).sort((a, b) => a - b);
  const stepsWith = (test) => perCard.filter((s) => s.length).map((s) => s.map(test));
  const refs = stepsWith((s) => /\brules?\b|[A-Z]{2,}-[A-Z0-9]+-\d+/i.test(s.description));
  const where = refs.every((r) => r.every((x) => !x)) ? 'none'
    : refs.every((r) => r.every(Boolean)) ? 'every step'
      : refs.every((r) => r[0] && r.slice(1).every((x) => !x)) ? 'first step only' : 'some steps';
  const expected = stepsWith((s) => Boolean(s.expected.trim()));
  const finalOnly = expected.every((r) => r.slice(0, -1).every((x) => !x));
  const finalHas = expected.every((r) => r.at(-1));
  const names = pack.steps.map((s) => s.step);
  const cardIds = new Set(pack.cards.map((c) => c.id));
  const form = pack.steps.every((s) => cardIds.has(s.testName)) ? 'card ID only'
    : pack.steps.every((s) => [...cardIds].some((id) => s.testName.startsWith(`${id} - `))) ? 'card ID - title' : 'mixed';
  return {
    steps: pack.steps.length, cards: perCard.filter((s) => s.length).length,
    stepsPerCard: counts.length ? { min: counts[0], median: counts[Math.floor(counts.length / 2)], max: counts.at(-1) } : null,
    stepNames: names.every((n) => /^Step \d+$/.test(n)) ? 'Step N' : 'other',
    expectedOnFinalStepOnly: finalOnly && finalHas, expectedOnFinalStep: Boolean(finalHas),
    expectedOnEveryStep: expected.every((r) => r.every(Boolean)),
    ruleReferencesIn: where, testNameForm: form, types: [...new Set(pack.steps.map((s) => s.type))],
  };
}

/** Header names of one sheet against another's: missing, extra and renamed (a missing name with an extra one that shares its words). */
export function headerDiff(expected, actual) {
  const missing = expected.filter((h) => !actual.some((a) => same(a, h)));
  const extra = actual.filter((a) => !expected.some((h) => same(a, h)));
  const renamed = [];
  for (const from of [...missing]) {
    const best = extra.map((to) => ({ to, s: dice(wordSet(from), wordSet(to)) })).sort((a, b) => b.s - a.s)[0];
    if (best?.s >= 0.4) {
      renamed.push({ from, to: best.to });
      missing.splice(missing.indexOf(from), 1);
      extra.splice(extra.indexOf(best.to), 1);
    }
  }
  return { missing, extra, renamed };
}

const FINAL_STEP_CHECK = 'Expected Result only on the final step';
const TEST_NAME_CHECK = 'Test Name form';
/**
 * The format differences the pack makes on purpose, each keyed by its check name and given the
 * pack's ALM style: the reason when the pack is in the intended state, else false. A pack in any
 * other state (a Test Name that is sometimes a title too) is still a plain difference.
 */
export const DELIBERATE = {
  [FINAL_STEP_CHECK]: (style) => style.steps > 0 && style.expectedOnFinalStep && !style.expectedOnFinalStepOnly
    && 'A step before the final one that checks something carries its own Expected Result, so a tester sees what to verify there.',
  [TEST_NAME_CHECK]: (style) => style.steps > 0 && style.testNameForm === 'card ID only'
    && 'The Test Name is the card ID alone, so a "/" in a card title never reaches the ALM import.',
};

const place = (found) => (found ? `row ${found.n}` : 'none');

/** The sheet inventory, layout, header and style checks of a pack against the reference. */
export function formatChecks(reference, pack, standard) {
  const checks = [];
  const add = (area, name, expected, actual, pass = same(expected, actual), style = null) => {
    const deliberate = pass ? false : DELIBERATE[name]?.(style) || false;
    checks.push({ area, name, reference: String(expected), pack: String(actual), pass,
      ...(deliberate ? { deliberate } : {}) });
  };
  const refNames = reference.sheets.map((s) => s.name);
  const names = pack.sheets.map((s) => s.name);
  const inOrder = refNames.filter((n) => names.some((m) => same(m, n)));
  for (const name of refNames) add('inventory', `sheet "${name}"`, 'present', names.some((m) => same(m, name)) ? 'present' : 'missing');
  add('inventory', 'sheet order', inOrder.join(' > '),
    names.filter((n) => refNames.some((m) => same(m, n))).join(' > '));
  for (const sheet of reference.sheets) {
    const mine = pack.sheets.find((s) => same(s.name, sheet.name));
    if (!mine) continue;
    add('layout', `${sheet.name}: title`, place(sheet.title), place(mine.title));
    add('layout', `${sheet.name}: subtitle`, place(sheet.subtitle), place(mine.subtitle));
    add('layout', `${sheet.name}: header row`, `row ${sheet.headerRow}`, `row ${mine.headerRow}`);
    const diff = headerDiff(sheet.headers, mine.headers);
    add('headers', `${sheet.name}: header names`, sheet.headers.join(' | '), mine.headers.join(' | '),
      !diff.missing.length && !diff.extra.length && !diff.renamed.length);
  }
  const ids = (p) => [...new Set(p.cards.map((c) => idShape(c.id)))].join(' / ');
  add('ids', 'test case ID shape', ids(reference), ids(pack));
  const a = almStyle(reference);
  const b = almStyle(pack);
  add('alm', 'step names', a.stepNames, b.stepNames);
  add('alm', FINAL_STEP_CHECK, a.expectedOnFinalStepOnly, b.expectedOnFinalStepOnly,
    undefined, b);
  add('alm', 'rule references in the Description', a.ruleReferencesIn, b.ruleReferencesIn);
  add('alm', TEST_NAME_CHECK, a.testNameForm, b.testNameForm, undefined, b);
  add('alm', 'Type', a.types.join(','), b.types.join(','));
  // How alike the layouts are. It says nothing about whether the pack is right, so it is reported, not scored,
  // whenever a workbook standard is there to score against.
  const referenceSimilarity = checks.length ? checks.filter((c) => c.pass).length / checks.length : 1;
  const against = standard ? standardChecks(pack, standard) : null;
  const score = against ? against.score : referenceSimilarity;
  const scoredAgainst = against ? 'standard' : 'reference layout (no standard given)';
  const deliberate = checks.filter((c) => c.deliberate).length;
  return { score, scoredAgainst, referenceSimilarity, passed: checks.filter((c) => c.pass).length, total: checks.length, checks,
    deliberate, differences: checks.filter((c) => !c.pass && !c.deliberate).length,
    style: { reference: a, pack: b }, standard: standard ? { reference: standardChecks(reference, standard), pack: standardChecks(pack, standard) } : null };
}

/** The standard's worksheets and listed columns or items against a pack. */
export function standardChecks(pack, standard) {
  const names = pack.sheets.map((s) => s.name);
  const missingSheets = standard.sheets.filter((n) => !names.some((m) => same(m, n)));
  const inOrder = standard.sheets.filter((n) => names.some((m) => same(m, n)));
  const orderOk = inOrder.every((n, i) => same(names.filter((m) => inOrder.some((x) => same(x, m)))[i], n));
  const sheets = [];
  for (const [name, wanted] of Object.entries(standard.items)) {
    const sheet = pack.sheets.find((s) => same(s.name, name));
    if (!sheet) continue;
    const labels = new Set([...sheet.headers, ...sheet.rows.map((r) => Object.values(r.cells)[0] ?? '')].map(lc));
    const absent = wanted.filter((item) => !labels.has(lc(item)));
    sheets.push({ sheet: name, required: wanted.length, absent });
  }
  const total = standard.sheets.length + sheets.reduce((n, s) => n + s.required, 0);
  const found = total - missingSheets.length - sheets.reduce((n, s) => n + s.absent.length, 0);
  return { missingSheets, orderOk, sheets, score: total ? found / total : 1 };
}

// ---- truth -------------------------------------------------------------

const level = (text) => lc(text).trim();

/** Everything the truth checks find in one workbook. */
export function truthOf(pack, source) {
  const { rules, doc, retired } = source;
  const rows = crosswalkRows(pack, rules, retired, doc);
  const struckOnly = struckOnlyWords(doc);
  // A row whose ID no rule's wording backs has nothing sound to compare risk and page against.
  const differences = rows.filter((r) => r.match && r.match.how !== 'id-unconfirmed').flatMap((r) => {
    const rule = r.match.rule;
    const found = [];
    if (rule.risk && r.row.risk && level(rule.risk) !== level(r.row.risk)) found.push({ field: 'risk', pack: r.row.risk, approved: rule.risk });
    if (rule.page && level(rule.page) !== level(r.row.page)) found.push({ field: 'page', pack: r.row.page || 'none', approved: rule.page });
    return found.map((f) => ({ row: r.row.n, rule: rule.id, ...f }));
  });
  const cardRules = new Map(pack.cards.map((c) => [c.id, citedRules(c, rows, rules)]));
  const cardStale = pack.cards.map((card) => ({ card: card.id, row: card.n,
    hits: staleHits([card.title, card.mission, card.focus, card.expected].join('. '), struckOnly) }))
    .filter((c) => c.hits.length);
  return {
    rows, differences, retired: retiredRecord(rows, rules, retired, doc),
    notInSource: rows.filter((r) => r.outside === 'not in the source').map((r) => r.row.n),
    stale: rows.filter((r) => r.stale.length || r.liveAsRetired),
    cited: citedIds(pack, rules, rows), cardRules, cardStale,
    expected: expectedResultChecks(pack),
  };
}

// ---- model pass --------------------------------------------------------

const FOLLOWS_SCHEMA = { type: 'object', additionalProperties: false, required: ['follows', 'reason'],
  properties: { follows: { type: 'boolean' }, reason: { type: 'string' } } };
const SAME_SCHEMA = { type: 'object', additionalProperties: false, required: ['same', 'reason'],
  properties: { same: { type: 'boolean' }, reason: { type: 'string' } } };

const cardText = (c) => `Title: ${c.title}\nMission: ${c.mission}\nFocus: ${c.focus}\nExpected Result: ${c.expected}`;

/**
 * The optional model questions. Does each card's Expected Result follow from
 * the rules it cites, with the document's authority put first: a rule the
 * document retired is given as retired, a rule a row has stale wording for is
 * given with the live text that follows the struck passage, and the document
 * wins where it and a rule differ. Is each unmatched reference card the same
 * scenario as the nearest pack card, and is each card that joined a repeat
 * group by its rules the same scenario as the group's first card (a "no"
 * takes it out of the group; see `splits`). `client` is a model client; a reply
 * that cannot be had is recorded by its error code and the pass goes on.
 */
export async function modelPass({ client, reference, pack, rules, unmatched, retired = new Map(), stale = new Map(), doc = null, doubtful = {}, controls = null, maxTokens = 2048 }) {
  const out = { run: true, follows: [], same: [], grouped: [], steps: [], errors: 0 };
  const ask = async (schemaName, schema, system, user) => {
    try {
      return fromWire(schema, (await client.json({ system, user, schema, schemaName, maxTokens })).value);
    } catch (error) {
      out.errors += 1;
      return { error: error.code ?? 'error' };
    }
  };
  const byId = new Map(rules.map((r) => [r.id, r]));
  // What the document puts in place of a struck span: the live words on the same lines, none for a plain deletion.
  const replacement = (span) => {
    const kept = (doc?.lines ?? []).slice(span.line - 1, span.endLine).join('\n').replace(/~~[\s\S]*?~~/g, ' ')
      .replace(/^\s*(?:[>*#-]|\d+\.)+\s*/gm, '').replace(/[*_`]/g, '').replace(/\s+/g, ' ').trim();
    return (kept.match(/[A-Za-z]{2,}/g) ?? []).length >= 2 ? kept : null;
  };
  // Decided once from the approved rule against the document, the same for both workbooks.
  const line = (rule) => {
    const gone = retired.get(rule.id);
    if (gone) {
      return `- ${rule.id}: RETIRED. The document strikes this behavior out${gone.span ? ` ("${gone.span.text}")` : ''}; it no longer applies.`;
    }
    const span = stale.get(rule.id);
    if (!span) return `- ${rule.id}: ${rule.summary}`;
    const live = replacement(span);
    return `- ${rule.id}: ${rule.summary}\n  STALE. The document no longer says this. `
      + (live ? `Its current text: "${live}"` : `The document strikes this wording out ("${span.text}") and puts nothing in its place.`);
  };
  for (const [label, workbook] of [['reference', reference], ['pack', pack]]) {
    for (const card of workbook.pack.cards) {
      const cited = (workbook.truth.cardRules.get(card.id)?.ids ?? []).map((id) => byId.get(id)).filter(Boolean);
      if (!cited.length) continue;
      const answer = await ask('follows', FOLLOWS_SCHEMA,
        'You check a test card against the business rules it cites. The document is the authority: where a rule is marked retired or stale, '
        + 'the document wins, and the card should follow the document, not that rule. Answer only from the text given.',
        `Rules:\n${cited.map(line).join('\n')}\n\nCard:\n${cardText(card)}\n\n`
        + 'Does the card\'s Expected Result follow from these rules, where retired rules do not apply and stale rules are replaced by the document\'s text?');
      out.follows.push({ workbook: label, card: card.id, ...answer });
    }
  }
  // With the source's control names, each card's steps are checked against the rules that govern them.
  if (controls) {
    for (const [label, workbook] of [['reference', reference], ['pack', pack]]) {
      for (const card of workbook.pack.cards) {
        const steps = stepsOf(workbook.pack, card.id).map((s) => ({ description: s.description, expected: s.expected }));
        const shown = stepRules({ rules: workbook.truth.cardRules.get(card.id)?.ids ?? [], steps }, rules, controls);
        if (!steps.length || !shown.length) continue;
        const answer = await ask('steps', stepSchema(['C1']),
          'You check a test card\'s steps against business rules. The document is the authority. Answer only from the text given.',
          `Rules:\n${shown.map(line).join('\n')}\n\nCard ${card.id}:\n${steps.map((s, i) => `Step ${i + 1}: ${s.description} => ${s.expected}`).join('\n')}\n\n${STEP_QUESTION}`);
        out.steps.push({ workbook: label, card: card.id, flagged: answer.error ? [] : impossibleSteps(answer.cards?.[0]),
          ...(answer.error ? { error: answer.error } : {}) });
      }
    }
  }
  for (const miss of unmatched) {
    const card = reference.pack.cards.find((c) => c.id === miss.card);
    const mine = wordSet(`${card.title} ${card.mission} ${card.focus}`);
    const near = [...pack.pack.cards].sort((a, b) => dice(mine, wordSet(`${b.title} ${b.mission} ${b.focus}`))
      - dice(mine, wordSet(`${a.title} ${a.mission} ${a.focus}`)))[0];
    if (!near) continue;
    const answer = await ask('same', SAME_SCHEMA,
      'You compare two test cards. Answer only from the text given.',
      `Card A:\n${cardText(card)}\n\nCard B:\n${cardText(near)}\n\nDo they test the same scenario?`);
    out.same.push({ reference: card.id, pack: near.id, ...answer });
  }
  for (const [label, workbook] of [['reference', reference], ['pack', pack]]) {
    const cards = new Map(workbook.pack.cards.map((c) => [c.id, c]));
    for (const d of doubtful[label] ?? []) {
      const answer = await ask('same', SAME_SCHEMA,
        'You compare two test cards. Answer only from the text given.',
        `Card A:\n${cardText(cards.get(d.first))}\n\nCard B:\n${cardText(cards.get(d.card))}\n\nDo they test the same scenario?`);
      out.grouped.push({ workbook: label, card: d.card, first: d.first, ...answer });
    }
  }
  return out;
}

/** Rules the document no longer supports: those that use wording only struck text has. Map of rule ID -> the struck span. */
function staleRules(rules, doc, retired) {
  const struckOnly = struckOnlyWords(doc);
  const out = new Map();
  for (const rule of rules) {
    if (retired.has(rule.id)) continue;
    const [hit] = staleHits(`${quoteOf(rule.description) || ''}. ${rule.summary}`, struckOnly);
    if (hit) out.set(rule.id, hit.span);
  }
  return out;
}

// ---- the comparison ----------------------------------------------------

/** The whole comparison as a scorecard object. */
export async function compare({ reference, pack, rules, doc, standard, client }) {
  const source = { rules, doc, retired: retiredRules(rules, doc) };
  const ref = { pack: reference, truth: truthOf(reference, source) };
  const mine = { pack: pack, truth: truthOf(pack, source) };
  const rulesOf = (which, card) => (which === 'reference' ? ref : mine).truth.cardRules.get(card.id)?.ids ?? [];
  // What the source names: its controls, and the words it uses.
  const sourceTexts = [...doc.live.map((p) => p.text), ...rules.flatMap((r) => [quoteOf(r.description), r.summary])];
  const scenarios = scenarioModel([...reference.cards, ...pack.cards],
    { controls: controlNames(sourceTexts), vocab: new Set(sourceTexts.flatMap((t) => words(t))) });
  const crosswalk = crosswalkCards(reference.cards, pack.cards, rulesOf, scenarios);
  const stale = (card) => ref.truth.cardStale.find((c) => c.card === card);
  for (const row of crosswalk) {
    if (row.matched) continue;
    const hit = stale(row.card);
    row.referenceError = hit ? { word: hit.hits[0].word, line: hit.hits[0].span.line } : null;
  }
  const repeats = (workbook, which) => repeatedCards(workbook.cards, scenarios, (c) => rulesOf(which, c));
  const floor = {
    crosswalk, reference: { ...setReport(reference), ...repeats(reference, 'reference') },
    pack: { ...setReport(pack), ...repeats(pack, 'pack') },
    unmatched: crosswalk.filter((r) => !r.matched).map((r) => r.card),
  };
  const model = client ? await modelPass({ client, reference: ref, pack: mine, rules, doc, retired: source.retired, stale: staleRules(rules, doc, source.retired),
    unmatched: crosswalk.filter((r) => !r.matched), controls: controlNames(sourceTexts),
    doubtful: { reference: floor.reference.doubtful, pack: floor.pack.doubtful } })
    : { run: false, reason: 'not requested; no model was called' };
  if (model.run) {
    // A "no" takes the card out of its repeat group.
    for (const [label, workbook] of [['reference', reference], ['pack', pack]]) {
      const split = new Set(model.grouped.filter((g) => g.workbook === label && g.same === false).map((g) => g.card));
      if (!split.size) continue;
      Object.assign(floor[label], splitGroups(floor[label].groups, split, workbook.cards.length));
      floor[label].doubtful = floor[label].doubtful.filter((d) => !split.has(d.card));
    }
  }
  return {
    format: formatChecks(reference, pack, standard),
    truth: { reference: summarizeTruth(ref.truth), pack: summarizeTruth(mine.truth), source: {
      approvedRules: rules.length, retiredByDocument: [...source.retired.keys()], struckSpans: doc.spans.length },
    },
    floor,
    consistency: { reference: consistencyChecks(reference), pack: consistencyChecks(pack) },
    quality: { reference: qualityChecks(reference, ref.truth, source.retired), pack: qualityChecks(pack, mine.truth, source.retired) },
    model,
    // The pack was scored with every check a gate relies on: the standard, and the model's answers with none lost.
    gate: gateOf({ standard, model }),
    detail: { reference: ref.truth, pack: mine.truth, source },
  };
}

/** Whether the scorecard is complete enough for a gate to rely on, and what is missing when it is not. */
export function gateOf({ standard, model }) {
  const reasons = [];
  if (!standard) reasons.push('no workbook standard, so the format was not scored against one');
  if (!model.run) reasons.push('the model pass was not run');
  else if (model.errors) reasons.push(`${model.errors} model question(s) could not be answered`);
  return { complete: reasons.length === 0, reasons };
}

function summarizeTruth(t) {
  const missing = t.retired.rules.filter((r) => r.status === 'missing');
  return {
    ruleRows: t.rows.length,
    matchedById: t.rows.filter((r) => r.match?.how === 'id').length,
    matchedByText: t.rows.filter((r) => r.match?.how === 'text').length,
    renumbered: t.rows.filter((r) => r.match?.how === 'renumbered').map((r) => ({ row: r.row.n,
      claimed: r.match.claimedId, matched: r.match.rule.id })),
    unconfirmedIds: t.rows.filter((r) => r.match?.how === 'id-unconfirmed').map((r) => ({ row: r.row.n, id: r.match.rule.id })),
    matchedAmbiguously: t.rows.filter((r) => r.match?.close.length).length,
    notInSource: t.notInSource.length,
    retiredRules: t.retired.rules.length, retiredMissing: missing.map((r) => r.id),
    retiredUnmarked: t.retired.rules.filter((r) => r.status === 'unmarked').map((r) => r.id),
    differences: t.differences.length, differenceList: t.differences,
    unmatchedStatements: t.rows.filter((r) => r.match?.unmatched?.length).map((r) => ({ row: r.row.n, statements: r.match.unmatched })),
    untrueRows: t.stale.map((r) => ({ row: r.row.n, words: r.stale.map((s) => s.word),
      line: r.stale[0]?.span.line ?? r.retiredRule?.span?.line ?? null,
      reason: r.liveAsRetired && !r.stale.length ? 'matches a rule the document retired' : 'uses wording only retired text has' })),
    untrueCards: t.cardStale.map((c) => ({ card: c.card, row: c.row, words: c.hits.map((h) => h.word), line: c.hits[0].span.line })),
    citedMissing: t.cited.filter((c) => !c.approved || !c.impact || !c.matrix).map((c) => ({ id: c.id,
      cards: c.cards, approved: c.approved, impactRow: c.impact, matrix: c.matrix })),
    unresolvedCitations: [...t.cardRules].filter(([, r]) => r.unresolved.length).map(([card, r]) => ({ card, count: r.unresolved.length })),
    contradictions: t.expected.filter((e) => e.contradicts).map((e) => ({ card: e.card, row: e.row, stepRow: e.stepRow,
      card_outcome: e.cardOutcome, step_outcome: e.stepOutcome, reason: e.reason })),
    expectedChecked: t.expected.filter((e) => e.checked).length,
  };
}

// ---- report ------------------------------------------------------------

const cellText = (v) => String(v ?? '').replace(/\|/g, '\\|').replace(/\s*\n\s*/g, ' ').trim();
const table = (headers, rows) => (rows.length ? [`| ${headers.join(' | ')} |`, `|${headers.map(() => '---').join('|')}|`,
  ...rows.map((r) => `| ${r.map(cellText).join(' | ')} |`)].join('\n') : '_none_');
const pct = (n) => `${Math.round(n * 100)}%`;
const list = (items, max = 6) => (items.length > max ? `${items.slice(0, max).join(', ')} and ${items.length - max} more` : items.join(', ') || 'none');

/** The scorecard as the Markdown report. */
export function reportOf(card, names = { reference: 'Reference', pack: 'Pack' }) {
  const t = card.truth;
  const f = card.floor;
  const out = [];
  const h = (text) => out.push('', text, '');
  const p = (text) => out.push(text);
  out.push('# Pack comparison');
  h('## Summary');
  p(table(['Measure', names.reference, names.pack], [
    ['Cards', f.reference.cards, f.pack.cards],
    ['Test sets', f.reference.sets, f.pack.sets],
    ['Distinct scenarios', f.reference.groups.length, f.pack.groups.length],
    ['Cards repeating an earlier card\'s scenario', f.reference.repeats, f.pack.repeats],
    ['Rule rows', t.reference.ruleRows, t.pack.ruleRows],
    ['Rule rows matched by ID / by wording / not in the source',
      `${t.reference.matchedById} / ${t.reference.matchedByText} / ${t.reference.notInSource}`,
      `${t.pack.matchedById} / ${t.pack.matchedByText} / ${t.pack.notInSource}`],
    [`Retired rules missing (of ${t.reference.retiredRules})`, t.reference.retiredMissing.length, t.pack.retiredMissing.length],
    ['Rule rows untrue to the source', t.reference.untrueRows.length, t.pack.untrueRows.length],
    ['Cards whose Expected Result contradicts their ALM step', t.reference.contradictions.length, t.pack.contradictions.length],
    ['Cited rule IDs missing from a sheet or the rules', t.reference.citedMissing.length, t.pack.citedMissing.length],
  ]));
  p('');
  p(`- Format: ${pct(card.format.score)} against the ${card.format.scoredAgainst}. Layout like the reference: ${card.format.passed} of ${card.format.total} checks (${pct(card.format.referenceSimilarity)}), reported only; ${card.format.deliberate} deliberate, ${card.format.differences} other.`);
  const matched = f.crosswalk.filter((r) => r.matched).length;
  p(`- Floor: ${matched} of ${f.crosswalk.length} reference cards are matched by a pack card; unmatched: ${list(f.unmatched)}.`);
  p(`- Truth: retired rules the pack does not record: ${list(t.pack.retiredMissing)}.`);
  p(`- Model pass: ${card.model.run ? 'run' : 'not run'}.`);

  h('## Format');
  p(`Score: ${pct(card.format.score)} against the ${card.format.scoredAgainst}. Layout likeness to the reference, ${card.format.passed} of ${card.format.total} checks (${pct(card.format.referenceSimilarity)}), is not part of the score. Rows are Excel rows.`);
  const failed = card.format.checks.filter((c) => !c.pass && !c.deliberate);
  h('### Checks that differ from the reference');
  p(table(['Area', 'Check', names.reference, names.pack], failed.map((c) => [c.area, c.name, c.reference, c.pack])));
  h('### Deliberate differences');
  p(table(['Area', 'Check', names.reference, names.pack, 'Why'],
    card.format.checks.filter((c) => c.deliberate).map((c) => [c.area, c.name, c.reference, c.pack, c.deliberate])));
  h('### ALM step style');
  const [a, b] = [card.format.style.reference, card.format.style.pack];
  const range = (s) => (s ? `${s.min} to ${s.max} (median ${s.median})` : 'none');
  p(table(['Style', names.reference, names.pack], [
    ['Steps per card', range(a.stepsPerCard), range(b.stepsPerCard)],
    ['Step names', a.stepNames, b.stepNames], ['Test Name', a.testNameForm, b.testNameForm],
    ['Expected Result only on the final step', a.expectedOnFinalStepOnly, b.expectedOnFinalStepOnly],
    ['Expected Result on every step', a.expectedOnEveryStep, b.expectedOnEveryStep],
    ['Rule references in Description', a.ruleReferencesIn, b.ruleReferencesIn],
  ]));
  if (card.format.standard) {
    h('### Workbook standard');
    for (const [key, label] of [['reference', names.reference], ['pack', names.pack]]) {
      const s = card.format.standard[key];
      p(`**${label}**: ${pct(s.score)} of the standard's worksheets and listed items are present. Missing sheets: ${list(s.missingSheets)}. Sheets in the standard's order: ${s.orderOk ? 'yes' : 'no'}.`);
      p('');
      p(table(['Sheet', 'Listed items the sheet lacks'], s.sheets.filter((x) => x.absent.length).map((x) => [x.sheet, x.absent.join('; ')])));
      p('');
    }
  }

  h('## Truth');
  p(`The approved rules number ${t.source.approvedRules}. The document has ${t.source.struckSpans} struck-through spans. Approved rules the document has struck through: ${list(t.source.retiredByDocument)}.`);
  for (const [key, label] of [['reference', names.reference], ['pack', names.pack]]) {
    const w = card.detail[key];
    h(`### ${label}`);
    p(`- ${t[key].ruleRows} rule rows: ${t[key].matchedById} matched by ID, ${t[key].matchedByText} by wording (${t[key].matchedAmbiguously} with a close second), ${t[key].renumbered.length} renumbered, ${t[key].unconfirmedIds.length} with an unconfirmed ID, ${t[key].notInSource} not in the source.`);
    p(`- Rule IDs the wording does not back: ${t[key].renumbered.length} rows are renumbered (matched by wording to a different rule: ${list(t[key].renumbered.map((r) => `row ${r.row} writes ${r.claimed}, reads like ${r.matched}`))}); ${t[key].unconfirmedIds.length} rows keep an ID no rule's wording confirms (${list(t[key].unconfirmedIds.map((r) => `row ${r.row} ${r.id}`))}), so their risk and page are not compared.`);
    p(`- Retired rules (${t[key].retiredRules}): ${t[key].retiredMissing.length} not recorded${t[key].retiredMissing.length ? ` (${list(t[key].retiredMissing)})` : ''}, ${t[key].retiredUnmarked.length} present but not marked retired.`);
    h('Rule rows untrue to the source');
    p(table(['Row', 'Words', 'Doc line', 'Why'], t[key].untrueRows.map((r) => [r.row, r.words.join(', '), r.line, r.reason])));
    h('Cards whose own text uses retired wording');
    p(table(['Card', 'Row', 'Words', 'Doc line'], t[key].untrueCards.map((c) => [c.card, c.row, c.words.join(', '), c.line])));
    h('Expected Result against the last ALM step');
    p(table(['Card', 'Card row', 'Step row', 'Card expects', 'Step expects', 'Why'],
      t[key].contradictions.map((c) => [c.card, c.row, c.stepRow, c.card_outcome, c.step_outcome, c.reason])));
    h('Cited rule IDs missing from a sheet or the rules');
    p(table(['Rule', 'Cited by', 'Approved rule', 'Impact Analysis row', 'Matrix'],
      t[key].citedMissing.map((c) => [c.id, c.cards.join(', '), c.approved ? 'yes' : 'no', c.impactRow ? 'yes' : 'no', c.matrix ? 'yes' : 'no'])));
    if (w.retired.spans.length) {
      h('Struck-through text no approved rule covers');
      p(table(['Doc line', 'Text', 'Status'], w.retired.spans.map((s) => [s.line, s.text.slice(0, 120), s.status])));
    }
    h('Retired rules');
    p(table(['Rule', 'Summary', 'Doc line', 'Status'], w.retired.rules.map((r) => [r.id, r.summary, r.line, r.status])));
  }
  h('### Rule wording that differs from the approved rule (risk and page)');
  for (const [key, label] of [['reference', names.reference], ['pack', names.pack]]) {
    const rows = t[key].differenceList;
    p(`**${label}**: ${rows.length} differences`);
    p(table(['Row', 'Rule', 'Field', label, 'Approved'], rows.slice(0, 40).map((d) => [d.row, d.rule, d.field, d.pack, d.approved])));
    if (rows.length > 40) p(`and ${rows.length - 40} more in compare.json`);
    p('');
  }
  for (const [key, label] of [['reference', names.reference], ['pack', names.pack]]) {
    const rows = t[key].unmatchedStatements;
    if (!rows.length) continue;
    p(`**${label}**: statements of merged rule rows that match no rule (the rule may be covered in other words, not absent)`);
    p(table(['Row', 'Statement'], rows.flatMap((r) => r.statements.map((x) => [r.row, x]))));
    p('');
  }
  h('### Classification, risk and page, reference against pack');
  p(table(['Rule', `${names.reference} class / risk / page`, `${names.pack} class / risk / page`],
    crosswalkRules(card.detail.reference.rows, card.detail.pack.rows)));

  h('## Floor');
  p(table(['Reference card', 'Scenario', 'Status', 'Closest pack cards', 'Combined to cover', 'Reference error'], f.crosswalk.map((r) => [r.card, r.scenario,
    `${r.status} (${pct(r.share)} of its features)`, list(r.matches.map((m) => m.card), 5), list(r.parts, 5),
    r.referenceError ? `uses "${r.referenceError.word}" (doc line ${r.referenceError.line})` : ''])));
  h('### Scenarios and repeats');
  p(`${names.reference}: ${f.reference.cards} cards, ${f.reference.groups.length} distinct scenarios, ${f.reference.repeats} repeats. ${names.pack}: ${f.pack.cards} cards, ${f.pack.groups.length} distinct scenarios, ${f.pack.repeats} repeats.`);
  p('');
  p(table(['Scenario', 'Cards'], f.pack.groups.filter((g) => g.cards.length > 1).map((g) => [g.signature, g.cards.join(', ')])));
  h('### Test sets');
  for (const [key, label] of [['reference', names.reference], ['pack', names.pack]]) {
    const s = f[key];
    p(`**${label}**: ${s.sets} sets, ${s.cards} cards. Cards per set: ${s.perSet.map((x) => `${x.number} ${x.cards}`).join(', ')}.`);
    if (s.fullCoverage) {
      p(`Full Coverage set "${s.fullCoverage.set}" holds ${s.fullCoverage.holds} of ${s.fullCoverage.requirementCards} requirement-derived cards${s.fullCoverage.missing.length ? `; missing ${list(s.fullCoverage.missing)}` : ''}.`);
    } else p('No Full Coverage set found.');
    p('');
  }

  h('## Consistency');
  for (const [key, label] of [['reference', names.reference], ['pack', names.pack]]) {
    const c = card.consistency[key];
    p(`**${label}**`);
    p(`- Dashboard counts that differ from their sheets: ${c.dashboardCounts.map((d) => `${d.label} says ${d.stated}, the sheet has ${d.actual}`).join('; ') || 'none'}.`);
    p(`- Confidence: ${Object.entries(c.confidence.values).map(([sheet, v]) => `${sheet} ${v.join('/') || 'none'}`).join('; ')} (${c.confidence.consistent ? 'consistent' : 'inconsistent'}).`);
    const ran = (check, text, detail) => (check.ran
      ? `${text}: ${check.problems.length}${check.problems.length ? ` (${detail(check.problems)})` : ''}.${check.reason ? ` Note: ${check.reason}.` : ''}`
      : `${text}: not checked, ${check.reason}.`);
    p(`- ${ran(c.matrixCards, "Matrix rows citing a card the sheet lacks or the row's sets do not hold", (x) => list(x.map((m) => `row ${m.row} ${m.card}`)))}`);
    p(`- ${ran(c.objectiveCards, 'Objective Matrix rows listing a card their set lacks', (x) => list(x.map((o) => `row ${o.row} ${o.card}`)))}`);
    p('');
  }

  h('## Quality');
  const quality = [
    ['junkCells', 'Cells holding only punctuation, a program value or a JSON fragment', (x) => `${x.sheet} row ${x.row}, ${x.column}: ${x.kind}`],
    ['pipelineVocabulary', 'Assumptions and notes written in the pipeline\'s words', (x) => `${x.sheet} row ${x.row}, ${x.column}: "${x.word}"`],
    ['designableNotApplicable', 'Objectives marked Not Applicable for a reason that says they apply', (x) => `row ${x.row} ${x.objective}: ${x.reason}`],
    ['unreviewedStrength', 'Coverage rows rated Strong that were not reviewed', (x) => `row ${x.row} ${x.rule}`],
    ['impactedWithoutCard', 'Impacted rules no card cites', (x) => `row ${x.row} ${x.rule} (${x.classification})`],
    ['validationFailures', 'Workbook Validation rows that are not PASS', (x) => `row ${x.row} ${x.check}: ${x.status}`],
    ['paddingCards', 'Cards that cite only rules the document retired', (x) => `${x.card} (row ${x.row}): ${x.rules.join(', ')}`],
  ];
  for (const [key, label] of [['reference', names.reference], ['pack', names.pack]]) {
    p(`**${label}**`);
    for (const [check, text, show] of quality) {
      const found = card.quality[key][check];
      p(`- ${text}: ${found.length}${found.length ? ` (${list(found.map(show), 4)})` : ''}.`);
    }
    p('');
  }

  h('## Gate');
  p(card.gate.complete ? 'Complete: the format was scored against the standard and the model pass ran with every question answered.'
    : `Incomplete, so a gate must not rely on this scorecard: ${card.gate.reasons.join('; ')}.`);

  h('## Model pass');
  if (!card.model.run) p(`Not run: ${card.model.reason}. "Does the Expected Result follow from the cited rules?" and "same scenario?" were not asked.`);
  else {
    const no = card.model.follows.filter((x) => x.follows === false);
    const regrouped = (card.model.grouped ?? []).filter((x) => x.same === false);
    p(`Asked ${card.model.grouped?.length ?? 0} "same scenario" questions about cards grouped as repeats by their rules (${regrouped.length} answered no and were taken out of their group).`);
    p('');
    p(`Asked ${card.model.follows.length} "does it follow" questions (${no.length} answered no) and ${card.model.same.length} "same scenario" questions (${card.model.same.filter((x) => x.same).length} answered yes); ${card.model.errors} could not be answered.`);
    p('');
    p(table(['Workbook', 'Card', 'Follows', 'Reason'], no.map((x) => [x.workbook, x.card, 'no', x.reason])));
    p('');
    const flagged = (card.model.steps ?? []).filter((x) => x.flagged.length);
    const answered = (card.model.steps ?? []).filter((x) => !x.error);
    p(`Asked ${answered.length} "can each step be done" questions (${flagged.length} cards have a step the rules forbid); ${(card.model.steps ?? []).length - answered.length} could not be answered.`);
    p('');
    if (flagged.length) {
      p(table(['Workbook', 'Card', 'Step', 'Reason'], flagged.flatMap((x) => x.flagged.map((f) => [x.workbook, x.card, f.step, f.why]))));
      p('');
    }
    p(table(['Reference card', 'Nearest pack card', 'Same scenario', 'Reason'], card.model.same.map((x) => [x.reference, x.pack, x.same ? 'yes' : 'no', x.reason])));
  }
  return `${out.join('\n')}\n`;
}

function crosswalkRules(refRows, packRows) {
  const byRule = (rows) => {
    const map = new Map();
    for (const r of rows) for (const rule of r.match?.rules ?? []) if (!map.has(rule.id)) map.set(rule.id, r.row);
    return map;
  };
  const [a, b] = [byRule(refRows), byRule(packRows)];
  const fmt = (r) => (r ? `${r.classification || 'none'} / ${r.risk || 'none'} / ${r.page || 'none'} (row ${r.n})` : 'absent');
  return [...new Set([...a.keys(), ...b.keys()])].sort().filter((id) => {
    const x = a.get(id);
    const y = b.get(id);
    return !x || !y || !same(x.classification, y.classification) || !same(x.risk, y.risk) || !same(x.page, y.page);
  }).map((id) => [id, fmt(a.get(id)), fmt(b.get(id))]);
}

// ---- command -----------------------------------------------------------

/** A bad argument or an input that cannot be read: the command line's fault, exit code 2. */
export class UsageError extends Error {}

/**
 * Reads the inputs a compare command names. Throws an Error naming the flag at
 * fault, never any content.
 */
export function inputsFrom(given) {
  // parseArgs collects every --doc into a list; a comparison reads one document.
  if (given.docs?.length > 1) throw new UsageError('compare takes one --doc');
  const args = { ...given, doc: given.doc ?? given.docs?.[0] };
  for (const flag of ['reference', 'pack', 'rules', 'doc']) {
    if (!args[flag]) throw new UsageError(`compare needs --${flag}`);
    if (!fs.existsSync(args[flag]) || !fs.statSync(args[flag]).isFile()) throw new UsageError(`--${flag} is not a file`);
  }
  if (args.standard && !fs.existsSync(args.standard)) throw new UsageError('--standard is not a file');
  if (args.model && !args.config) throw new UsageError('--model needs --config');
  const load = (flag, fn) => {
    try {
      return fn(args[flag]);
    } catch {
      throw new UsageError(`--${flag} could not be read`);
    }
  };
  return {
    reference: load('reference', readPack), pack: load('pack', readPack),
    rules: load('rules', loadRules), doc: load('doc', (f) => parseDoc(fs.readFileSync(f, 'utf8'))),
    standard: args.standard ? load('standard', (f) => parseStandard(fs.readFileSync(f, 'utf8'))) : null,
  };
}

/**
 * Runs the comparison a command line names and writes compare.json and
 * compare.md. `makeClient(config)` builds the model client when `--model` is
 * given. Returns the content-free count lines for the console.
 */
export async function runCompare(args, { makeClient, standardFrom } = {}) {
  const inputs = inputsFrom(args);
  // With no --standard, the job config's own workbook standard is the one to score against.
  if (!inputs.standard && args.config && standardFrom) {
    const text = standardFrom(args.config);
    if (text) inputs.standard = parseStandard(text);
  }
  // The model pass runs whenever a config says where the model is, so a gate that scores a pack never
  // reads a floor and truth score the model did not check. --no-model turns it off.
  if (args.noModel && args.model) throw new UsageError('--model and --no-model cannot both be given');
  const useModel = !args.noModel && Boolean(args.config);
  const client = useModel ? makeClient(args.config) : null;
  const card = await compare({ ...inputs, client });
  const out = args.out ?? path.dirname(path.resolve(args.pack));
  fs.mkdirSync(out, { recursive: true });
  const { detail, ...scorecard } = card;
  fs.writeFileSync(path.join(out, 'compare.json'), `${JSON.stringify(scorecard, null, 1)}\n`);
  fs.writeFileSync(path.join(out, 'compare.md'), reportOf(card));
  const t = card.truth;
  return [
    `format  ${card.format.passed}/${card.format.total} checks matched, ${card.format.deliberate} deliberate, ${card.format.differences} other`,
    `floor   reference cards=${card.floor.reference.cards} pack cards=${card.floor.pack.cards} `
      + `repeats=${card.floor.pack.repeats} unmatched=${card.floor.unmatched.length}`,
    `truth   retired-missing=${t.pack.retiredMissing.length} untrue-rows=${t.pack.untrueRows.length} `
      + `contradictions=${t.pack.contradictions.length} cited-missing=${t.pack.citedMissing.length}`,
    `truth   reference: untrue-rows=${t.reference.untrueRows.length} contradictions=${t.reference.contradictions.length} `
      + `cited-missing=${t.reference.citedMissing.length}`,
    `model   ${card.model.run ? 'run' : 'not run'}`,
    'wrote compare.json and compare.md',
  ];
}
