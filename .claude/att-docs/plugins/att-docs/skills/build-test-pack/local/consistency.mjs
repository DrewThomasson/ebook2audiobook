// Checks that need no source and no model: one pack workbook against itself.
// Each takes a workbook read by readPack and returns the places it disagrees
// with itself, so any report can reuse them.

import { cell, expandIds } from './pack.mjs';

const pick = (row, pattern) => {
  const key = Object.keys(row.cells).find((k) => pattern.test(k));
  return key === undefined ? '' : row.cells[key];
};
const hasColumn = (sheet, pattern) => sheet.headers.some((h) => pattern.test(h));

/** Test set numbers in a list such as "01 Core", "TS05 Workflow" or "5", one per line or separated by semicolons. */
export const setNumbers = (text) => String(text).split(/[;\n,]+/)
  .map((p) => /^\s*(?:TS[\s-]*|test[\s-]*set[\s-]*|set[\s-]*)?0*(\d+)/i.exec(p)?.[1]).filter(Boolean);

/** Test sets by number, read from the set's number cell or, failing that, the start of its name. */
function setsByNumber(pack) {
  return new Map(pack.sets.map((s) => [(setNumbers(s.number)[0] ?? setNumbers(s.name)[0]), s]));
}

const SETS_COLUMN = /test\s*(?:lab\s*)?sets?/i;

/** Dashboard values keyed by their label (the first two columns of its rows). */
function dashboardValues(pack) {
  const sheet = pack.sheet('dashboard');
  if (!sheet) return [];
  const [labelKey, valueKey] = sheet.headers;
  return sheet.rows.map((r) => ({ n: r.n, label: r.cells[labelKey] ?? '', value: r.cells[valueKey] ?? '' }));
}

/**
 * Dashboard counts against the sheets they count: test cards, test sets, rule
 * rows and assumptions. Returns [{ label, stated, actual, row }] for each count
 * the Dashboard states that differs from the sheet. A rule count may read
 * "15 impacted of 47": the first number is checked against the impacted rows and
 * the second against all of them. A rule mismatch carries a `note` that gives both
 * counts, so a reader sees what the sheet holds.
 */
export function dashboardCountMismatches(pack) {
  const counted = [
    [/test cards?/i, pack.cards.length],
    [/test sets?/i, pack.sets.length],
    [/rules?/i, pack.ruleRows.length, pack.ruleRows.filter((r) => !/^not impacted$/i.test(r.classification)).length],
    [/assumptions?/i, pack.sheet('assumptions')?.rows.length],
  ];
  const found = [];
  for (const { n, label, value } of dashboardValues(pack)) {
    const target = counted.find(([pattern]) => pattern.test(label));
    // Only a rule count reads "N impacted of M"; any other "N of M" row is not a plain count.
    const split = target?.[2] !== undefined
      ? /^\s*(\d+)\s+impacted\s+of\s+(\d+)\s*$/i.exec(value) : null;
    const stated = split ? split[1] : /^\s*(\d+)\s*$/.exec(value)?.[1];
    if (stated === undefined || !target || target[1] === undefined) continue;
    const note = target[2] === undefined ? undefined
      : `${target[1]} rule rows, ${target[2]} of them impacted`;
    if (split && target[2] !== undefined) {
      // "N impacted of M" states both counts, and each is checked against its own.
      if (Number(split[1]) !== target[2]) {
        found.push({ label, stated: Number(split[1]), actual: target[2], row: n, note });
      }
      if (Number(split[2]) !== target[1]) {
        found.push({ label, stated: Number(split[2]), actual: target[1], row: n, note });
      }
      continue;
    }
    // A count labeled impacted leaves the Not Impacted baseline rules out.
    const actual = target[2] !== undefined && /impacted/i.test(label) ? target[2] : target[1];
    if (Number(stated) !== actual) found.push({ label, stated: Number(stated), actual, row: n, note });
  }
  return found;
}

const LEVEL = '(medium[\\s-]high|low[\\s-]medium|medium|high|low)';
const LABEL = /^\s*(?:overall\s+)?confidence(?:\s+level)?\s*:?\s*$/i;
const STARTS_WITH = new RegExp(`^\\W*${LEVEL}\\b`, 'i');
const STATED = new RegExp(`\\bconfidence\\s+(?:level\\s+)?(?:is|:)\\s*${LEVEL}\\b`, 'i');
const levelName = (text) => text.toLowerCase().replace(/\s+/g, '-');

/**
 * The confidence level each of the Dashboard, Executive Summary and Confidence
 * Assessment states: in a row labeled Confidence (the value cell opens with
 * the level), or in a sentence "confidence is <level>". Returns
 * { values: { sheet: [levels] }, consistent }.
 */
export function confidenceValues(pack) {
  const values = {};
  for (const name of ['dashboard', 'executive summary', 'confidence assessment']) {
    const sheet = pack.sheet(name);
    if (!sheet) continue;
    const found = [];
    for (const row of sheet.rows) {
      const cells = Object.values(row.cells);
      if (LABEL.test(cells[0] ?? '')) {
        const level = cells.slice(1).map((c) => STARTS_WITH.exec(c)?.[1]).find(Boolean);
        if (level) found.push(levelName(level));
      }
      for (const text of cells) {
        const level = STATED.exec(text)?.[1];
        if (level) found.push(levelName(level));
      }
    }
    values[sheet.name] = [...new Set(found)];
  }
  const all = new Set(Object.values(values).flat());
  return { values, consistent: all.size <= 1 };
}

const notRun = (sheet, what) => ({ ran: false, problems: [], reason: sheet ? `the ${sheet.name} sheet has no ${what} column` : 'the sheet is missing' });

/**
 * Rule-to-Test rows that cite a card the pack has no row for, or a card that
 * none of the row's own test sets holds. Returns { ran, reason, problems }
 * with problems as [{ row, rule, card, problem }]; `ran` is false when the
 * sheet or a column it needs is missing.
 */
export function matrixCardProblems(pack) {
  const sheet = pack.sheet('rule-to-test matrix');
  const cardsPattern = /covered by test cards?|cards?/i;
  if (!sheet || !hasColumn(sheet, cardsPattern)) return notRun(sheet, 'test card');
  const known = new Set(pack.cards.map((c) => c.id));
  const byNumber = setsByNumber(pack);
  const checkSets = hasColumn(sheet, SETS_COLUMN);
  const problems = [];
  for (const row of sheet.rows) {
    const rule = cell(row, 'Rule ID');
    const listed = checkSets ? setNumbers(pick(row, SETS_COLUMN)).map((n) => byNumber.get(n)).filter(Boolean) : [];
    for (const { id } of expandIds(pick(row, cardsPattern))) {
      if (!known.has(id)) problems.push({ row: row.n, rule, card: id, problem: 'no such card' });
      else if (listed.length && !listed.some((s) => s.cards.includes(id))) {
        problems.push({ row: row.n, rule, card: id, problem: "not in the row's test sets" });
      }
    }
  }
  return { ran: true, problems, reason: checkSets ? null : 'the sheet has no test set column, so only the cards were checked' };
}

/**
 * Objective Matrix rows that list a card the row's own test sets do not hold.
 * Returns { ran, reason, problems } with problems as [{ row, objective, card }].
 */
export function objectiveCardProblems(pack) {
  const sheet = pack.sheet('objective matrix');
  if (!sheet || !hasColumn(sheet, /related\s*test\s*cards?/i)) return notRun(sheet, 'related test cards');
  if (!hasColumn(sheet, SETS_COLUMN)) return notRun(sheet, 'test set');
  const byNumber = setsByNumber(pack);
  const problems = [];
  for (const row of sheet.rows) {
    const held = new Set(setNumbers(pick(row, SETS_COLUMN)).flatMap((n) => byNumber.get(n)?.cards ?? []));
    if (!held.size) continue;
    for (const { id } of expandIds(pick(row, /related\s*test\s*cards?/i))) {
      if (!held.has(id)) problems.push({ row: row.n, objective: pick(row, /objective$/i), card: id });
    }
  }
  return { ran: true, problems, reason: null };
}

/** All the self-consistency checks of one pack. */
export function consistencyChecks(pack) {
  return {
    dashboardCounts: dashboardCountMismatches(pack),
    confidence: confidenceValues(pack),
    matrixCards: matrixCardProblems(pack),
    objectiveCards: objectiveCardProblems(pack),
  };
}
