// Checks of a pack against itself that run before its workbook is written, so
// every repository's builder gets them. They read the sheets the builder
// returned, or, when it returns none, the same sheets worked out from the pack,
// and report each problem as a failed sheet in the shape the builder's own
// failures take, which `failedSheet` builds.

import { cell, expandIds, packFromSheets, readSheet } from './pack.mjs';
import { confidenceValues, dashboardCountMismatches, objectiveCardProblems, setNumbers }
  from './consistency.mjs';

const list = (v) => (Array.isArray(v) ? v : v == null || v === '' ? [] : [v]);
const blank = (v) => list(v).every((x) => String(x ?? '').trim() === '');

/** A failed sheet as the builder's own failures give it: [sheet, 'Yes', 'Yes', 'FAIL', notes]. */
export const failedSheet = (sheet, notes) => [sheet, 'Yes', 'Yes', 'FAIL', notes];

const ids = (text) => String(text ?? '').split(/[;\n,]+/).map((s) => s.trim()).filter(Boolean);

/**
 * Sheets as readSheet reads them from a builder's rows, which lead with the headers; readSheet
 * also reads a sheet with a title and a subtitle above its headers, so a builder that writes
 * them in row 4 is read the same way.
 */
const sheetOf = (name, rows) => readSheet({ name, rows: [[], ...rows.map((r) => ['', ...r])] });

/** The pack's sheets as { name, rows }, worked out from the pack the way a builder lays them out. */
export function derivedSheets(pack) {
  const rules = list(pack.rules);
  const cards = list(pack.testCards);
  const sets = list(pack.testSets);
  const coverage = new Map(list(pack.coverage).map((row) => [row.ruleId, row]));
  const cardsOf = (rule) => cards.filter((card) => list(card.rules).includes(rule.id));
  const setsOf = (card) => sets.filter((set) => list(set.cards).includes(card.id));
  const overall = pack.confidence?.overall ?? '';
  const impacted = rules.filter((rule) => rule.impact !== 'Not Impacted');
  return [
    ['Dashboard', ['Item', 'Value'], [
      ['Number of Impacted Business Rules', impacted.length],
      ['Number of Reusable Test Cards', cards.length],
      ['Number of Applicable Test Sets', sets.length],
      ['Number of Assumptions', list(pack.assumptions).length],
      ['Overall Confidence', overall]]],
    ['Executive Summary', ['Item', 'Value'], [['Confidence', pack.executiveSummary?.confidence ?? '']]],
    ['Confidence Assessment', ['Item', 'Value'], [['Confidence level', overall]]],
    ['Impact Analysis', ['Rule ID', 'Risk Level', 'Impact Classification', 'Status'],
      rules.map((rule) => [rule.id, rule.risk ?? '', rule.impact, rule.status ?? ''])],
    ['Objective Matrix', ['Testing Objective', 'Applicable / Not Applicable', 'Related Test Cards',
      'Related Test Lab Test Set'], [...new Set(sets.map((set) => set.objective))].map((objective) => {
      const held = sets.filter((set) => set.objective === objective);
      return [objective, 'Applicable', [...new Set(held.flatMap((set) => list(set.cards)))].join('\n'),
        held.map((set) => set.name).join('\n')];
    })],
    ['Test Cards Markdown', ['Test Case ID', 'Rules Covered'],
      cards.map((card) => [card.id, list(card.rules).join('\n')])],
    ['Test Lab Markdown', ['Test Set Number', 'Test Set Name', 'Objective', 'Test Cards Covered'],
      sets.map((set) => [String(set.number), set.name, set.objective, list(set.cards).join('\n')])],
    ['Rule-to-Test Matrix', ['Rule ID', 'Risk Level', 'Impact Classification', 'Covered By Test Card(s)',
      'Covered By Test Set(s)'], rules.map((rule) => [rule.id, rule.risk ?? '', rule.impact,
      cardsOf(rule).map((c) => c.id).join('\n'),
      [...new Set(cardsOf(rule).flatMap(setsOf).map((set) => set.name))].join('\n')])],
    ['Coverage Matrix', ['Rule ID', 'Coverage Status', 'Gap / Concern', 'Recommendation'],
      rules.map((rule) => {
        const row = coverage.get(rule.id);
        const held = cardsOf(rule);
        const fallback = held.some((card) => card.derivation !== 'Quality') ? 'Covered'
          : held.length ? 'Weakly Covered' : rule.impact === 'Not Impacted' ? 'Not Applicable' : 'Missing';
        return [rule.id, row?.status || fallback, row?.gap ?? '', row?.recommendation ?? ''];
      })],
    ['Assumptions', ['Assumption ID', 'Assumption'],
      list(pack.assumptions).map((row, i) => [`A-${i + 1}`, row.assumption])],
  ].map(([name, header, rows]) => ({ name, rows: [header, ...rows] }));
}

/** The sheets to check: the builder's own when it returned any, else the derived ones. */
export function viewOf(pack, built) {
  const given = list(built?.sheets);
  return packFromSheets((given.length ? given : derivedSheets(pack)).map(({ name, rows }) => sheetOf(name, rows)));
}

const rowsOf = (view, name) => view.sheet(name)?.rows ?? [];

/** Gap text the pipeline writes when the review gave none; it is not a reason. */
export const FILLED_GAP = /^(?:Not stated by the review\.|Not reviewed; coverage rests on the card mapping)/;

// Each check adds to `out`: `fail(sheet, text, ...keys)` is a problem the repair call can fix, and
// `warn(code, text)` one it cannot, which the build logs and leaves to the comparison report.
// `keys` are the cards and rules the problem names, so one the builder already failed can be dropped.

/** Dashboard counts that differ from the sheets they count. */
function dashboard(view, out) {
  for (const m of dashboardCountMismatches(view)) {
    out.warn('dashboard-count', `${m.label} reads ${m.stated}, but the sheet it counts has ${m.actual}`
      + `${m.note ? ` (${m.note})` : ''}.`);
  }
}

/** One confidence level across the Executive Summary, Dashboard and Confidence Assessment. */
function confidence(view, out) {
  const { values, consistent } = confidenceValues(view);
  if (consistent) return;
  const stated = Object.entries(values).filter(([, levels]) => levels.length)
    .map(([sheet, levels]) => `${sheet}: ${levels.join(' and ')}`).join('; ');
  out.warn('confidence-differs', `Confidence differs across sheets (${stated}).`);
}

/** Covered rows with no Gap / Concern or no Recommendation. */
function coveredGaps(view, out) {
  for (const row of rowsOf(view, 'Coverage Matrix')) {
    if (!/^covered$/i.test(cell(row, 'Coverage Status'))) continue;
    const missing = [['Gap / Concern', /gap/i], ['Recommendation', /recommendation/i]]
      .filter(([, pattern]) => blank(Object.entries(row.cells).find(([k]) => pattern.test(k))?.[1]));
    if (missing.length) {
      out.fail('Coverage Matrix', `${cell(row, 'Rule ID')} is Covered but has a blank `
        + `${missing.map(([label]) => label).join(' and ')}. State the gap and the recommendation, `
        + 'or write that there is none and why.');
    }
  }
}

/** Coverage rows that read Missing or Not Applicable for a rule the matrix shows a card covering. */
function deniedCoverage(view, out) {
  const carded = new Set(rowsOf(view, 'Rule-to-Test Matrix')
    .filter((row) => expandIds(cell(row, 'Covered By Test Card(s)', 'Covered By Test Cards')).length)
    .map((row) => cell(row, 'Rule ID')));
  for (const row of rowsOf(view, 'Coverage Matrix')) {
    const rule = cell(row, 'Rule ID');
    const status = cell(row, 'Coverage Status');
    if (!/^(?:missing|not applicable)$/i.test(status) || !carded.has(rule)) continue;
    const gap = Object.entries(row.cells).find(([k]) => /gap/i.test(k))?.[1];
    out.fail('Coverage Matrix', `${rule} reads ${status}, but a test card covers it.`
      + `${blank(gap) ? '' : ` The review said: ${gap}`} Set the status to Covered, `
      + 'Partially Covered or Weakly Covered and put the reason in Gap / Concern, or fix the card.');
  }
}

/** Cards that cite a rule the Rule-to-Test Matrix has no row for. */
function cardRules(view, out) {
  const matrix = view.sheet('rule-to-test matrix');
  if (!matrix) return;
  const known = new Set(matrix.rows.map((row) => cell(row, 'Rule ID')));
  for (const row of rowsOf(view, 'Test Cards Markdown')) {
    const unknown = ids(cell(row, 'Rules Covered')).filter((id) => !known.has(id));
    if (unknown.length) {
      out.fail('Rule-to-Test Matrix', `${cell(row, 'Test Case ID')} cites ${unknown.join(', ')}, `
        + 'which the Rule-to-Test Matrix does not list.', cell(row, 'Test Case ID'), ...unknown);
    }
  }
}

/** Objective Matrix rows listing a card the row's own test sets do not hold. */
function objectiveCards(view, out) {
  for (const p of objectiveCardProblems(view).problems) {
    out.fail('Objective Matrix', `${p.objective || `Row ${p.row}`} lists ${p.card}, `
      + 'which none of its test sets holds.', p.card, p.objective);
  }
}

/** Rule-to-Test rows whose test set column misses a set one of their cards is in. */
function ruleSets(view, out) {
  const matrix = view.sheet('rule-to-test matrix');
  const setsHeader = matrix?.headers.find((h) => /test\s*sets?/i.test(h));
  if (!setsHeader) return;
  for (const row of matrix.rows) {
    const listed = new Set(setNumbers(row.cells[setsHeader]));
    for (const { id } of expandIds(cell(row, 'Covered By Test Card(s)', 'Covered By Test Cards'))) {
      const missing = view.sets.filter((set) => {
        const number = setNumbers(set.number)[0] ?? setNumbers(set.name)[0];
        return number !== undefined && set.cards.includes(id) && !listed.has(number);
      }).map((set) => set.name);
      if (missing.length) {
        out.warn('set-column', `${cell(row, 'Rule ID')} lists ${id}, but its test sets leave out `
          + `${missing.join(', ')}.`);
      }
    }
  }
}

/** How the problem for a High-risk Not Impacted rule with no card and no reason reads after the rule ID. */
export const NO_REASON_PROBLEM = 'is High risk and Not Impacted, but no regression card covers it and no reason is stated';

/** High-risk Not Impacted rules with no regression card and no reason in the Coverage Matrix. */
function regressionRules(view, out) {
  const regression = new Set(view.sets.filter((set) => /regression/i.test(set.objective))
    .flatMap((set) => set.cards));
  const gaps = new Map(rowsOf(view, 'Coverage Matrix').map((row) => [cell(row, 'Rule ID'),
    Object.entries(row.cells).find(([k]) => /gap/i.test(k))?.[1]]));
  for (const row of rowsOf(view, 'Rule-to-Test Matrix')) {
    if (!/^high$/i.test(cell(row, 'Risk Level')) || !/^not impacted$/i.test(cell(row, 'Impact Classification'))) continue;
    const rule = cell(row, 'Rule ID');
    const cards = expandIds(cell(row, 'Covered By Test Card(s)', 'Covered By Test Cards')).map((c) => c.id);
    const reason = gaps.get(rule);
    if (!cards.some((id) => regression.has(id)) && (blank(reason) || FILLED_GAP.test(String(reason).trim()))) {
      out.fail('Coverage Matrix', `${rule} ${NO_REASON_PROBLEM}. Add a regression card, or state in its Gap / Concern why none is needed`
        + `${cards.length ? '; a card covers it, so keep a covering status (Covered, Partially Covered or '
          + 'Weakly Covered) rather than Not Applicable' : ''}.`);
    }
  }
}

/**
 * The problems of one pack: { failed, warnings }. `failed` holds failed sheets,
 * [[sheet, 'Yes', 'Yes', 'FAIL', notes]], for problems a repair can fix, leaving out any the
 * builder's own failed sheets already name. `warnings` holds [{ code, text }] for problems the
 * builder's layout guarantees or a repair cannot change. `built` is what the builder returned;
 * its sheets are checked when it has any.
 */
export function checkPack(pack, built) {
  const view = viewOf(pack, built);
  const found = [];
  const warnings = [];
  const out = { fail: (sheet, text, ...keys) => found.push({ sheet, text, keys: keys.filter(Boolean) }),
    warn: (code, text) => warnings.push({ code, text }) };
  for (const check of [dashboard, confidence, coveredGaps, deniedCoverage, cardRules, objectiveCards, ruleSets, regressionRules]) {
    check(view, out);
  }
  const named = new Map(list(built?.failed).map((row) => [row[0], String(row[4] ?? '')]));
  const fresh = found.filter(({ sheet, keys }) => !keys.length
    || !keys.every((key) => (named.get(sheet) ?? '').includes(key)));
  const sheets = [...new Set(fresh.map((f) => f.sheet))];
  return { failed: sheets.map((sheet) => failedSheet(sheet,
    fresh.filter((f) => f.sheet === sheet).map((f) => f.text).join('\n'))), warnings };
}
