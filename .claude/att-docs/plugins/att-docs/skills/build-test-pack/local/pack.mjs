// Reads a test pack workbook into the pieces the comparison uses: sheets with
// their title, subtitle and header rows, the cards, the ALM steps, the test
// sets, and the rule rows. Works on both layouts a pack comes in: headers in
// row 1, or a title and a subtitle above the headers.

import { readXlsx } from './xlsx.mjs';

// Header cells that only a header row holds.
const KNOWN_HEADERS = new Set(['rule id', 'test case id', 'subject', 'test set #', 'test set number',
  '#', 'item', 'testing objective']);

const clean = (value) => String(value ?? '').trim();
const filled = (row) => (row ?? []).slice(1).filter((cell) => clean(cell));

/** Index of the header row: the first with a known header name, else the first with two different values. */
export function headerRowOf(rows) {
  for (let r = 1; r < rows.length; r += 1) {
    if (filled(rows[r]).some((cell) => KNOWN_HEADERS.has(clean(cell).toLowerCase()))) return r;
  }
  for (let r = 1; r < rows.length; r += 1) {
    if (new Set(filled(rows[r]).map(clean)).size >= 2) return r;
  }
  return 0;
}

/**
 * A sheet as { name, headerRow, title, subtitle, headers, rows }. `title` and
 * `subtitle` are the text of the rows above the headers (null when absent);
 * each data row is { n, cells } with `n` the Excel row and `cells` keyed by header.
 */
export function readSheet({ name, rows }) {
  const headerRow = headerRowOf(rows);
  const above = [];
  for (let r = 1; r < headerRow; r += 1) {
    const first = clean(filled(rows[r])[0]);
    if (first) above.push({ n: r, text: first });
  }
  const headers = headerRow ? (rows[headerRow] ?? []).slice(1).map(clean) : [];
  const data = [];
  for (let r = headerRow + 1; r < rows.length; r += 1) {
    if (!filled(rows[r]).length) continue;
    const cells = {};
    headers.forEach((header, i) => {
      if (header) cells[header] = clean(rows[r][i + 1]);
    });
    data.push({ n: r, cells });
  }
  return { name, headerRow, title: above[0] ?? null, subtitle: above[1] ?? null, headers, rows: data };
}

/**
 * Splits a list cell into items and expands each one. Handles a full ID
 * ("TC-ABC-1234-001"), an abbreviated one ("002", which borrows the prefix of
 * the item before it) and ranges: "TC-ABC-1234-001–005", "TC-ABC-1234-001 –
 * TC-ABC-1234-005", "001 to 005", "002–004", and "TC-ABC-1234-001-005" (a bare
 * hyphen is a range only when the ID already holds a number segment, as this
 * one does; "BR-ABC-043-047" with a bare hyphen reads as one ID, so write it
 * with a dash). Returns [{ id, removed }]; `removed` is set when the item says so.
 */
export function expandIds(text, prefixPattern = '[A-Z][A-Za-z0-9]*(?:-[A-Z][A-Za-z0-9]*)*(?:-\\d+)?') {
  const out = [];
  let prefix = null;
  const full = new RegExp(`(${prefixPattern}-)(\\d+)(?:(\\s*[–—]\\s*|\\s+to\\s+|\\s+-\\s+|-)(?:${prefixPattern}-)?(\\d+))?`, 'g');
  const bare = /^\s*(\d+)(?:\s*(?:[-–—]|\bto\b)\s*(\d+))?\s*(?:\(([^)]*)\))?\s*$/;
  for (const part of String(text ?? '').split(/[;\n,]+/)) {
    const removed = /\bremoved\b|\bretired\b|\bsuperseded\b/i.test(part);
    full.lastIndex = 0;
    let found = false;
    for (let m = full.exec(part); m; m = full.exec(part)) {
      found = true;
      prefix = m[1];
      let to = m[4];
      if (m[3] === '-' && !/-\d+-$/.test(prefix)) {
        // A bare hyphen after an ID without a number segment is part of the ID text, not a range.
        to = undefined;
        full.lastIndex = m.index + prefix.length + m[2].length;
      }
      push(out, prefix, m[2], to, removed);
    }
    if (found) continue;
    const b = bare.exec(part);
    if (b && prefix) push(out, prefix, b[1], b[2], removed || /removed|retired|superseded/i.test(b[3] ?? ''));
  }
  return out;
}

function push(out, prefix, from, to, removed) {
  const width = from.length;
  const last = to ? Number(to) : Number(from);
  for (let n = Number(from); n <= Math.max(last, Number(from)); n += 1) {
    out.push({ id: `${prefix}${String(n).padStart(width, '0')}`, removed });
  }
}

const find = (sheets, ...names) => sheets.find((s) => names.includes(s.name.toLowerCase()));
const cell = (row, ...names) => {
  for (const name of names) {
    const key = Object.keys(row.cells).find((k) => k.toLowerCase() === name.toLowerCase());
    if (key !== undefined) return row.cells[key];
  }
  return '';
};
export { cell };

/** A pack workbook read into { sheets, cards, steps, sets, ruleRows, ... } (see each key below). */
export function readPack(file) {
  return packFromSheets(readXlsx(file).map(readSheet));
}

/** The same pieces, from sheets already read by readSheet. */
export function packFromSheets(sheets) {
  const cardSheet = find(sheets, 'test cards markdown', 'test cards');
  const almSheet = find(sheets, 'alm upload');
  const labSheet = find(sheets, 'test lab markdown', 'test lab');
  const impactSheet = find(sheets, 'impact analysis');
  const cards = (cardSheet?.rows ?? []).filter((r) => cell(r, 'Test Case ID')).map((r) => ({
    n: r.n, id: cell(r, 'Test Case ID'), title: cell(r, 'Test Case Title'), mission: cell(r, 'Mission'),
    focus: cell(r, 'Focus'), expected: cell(r, 'Expected Result'), rulesCovered: cell(r, 'Rules Covered'),
  }));
  const steps = (almSheet?.rows ?? []).filter((r) => cell(r, 'Test Name')).map((r) => ({
    n: r.n, testName: cell(r, 'Test Name'), subject: cell(r, 'Subject'), type: cell(r, 'Type'),
    step: cell(r, 'Step Name'), description: cell(r, 'Description'), expected: cell(r, 'Expected Result'),
  }));
  const sets = (labSheet?.rows ?? []).filter((r) => cell(r, 'Test Set Name')).map((r) => ({
    n: r.n, number: cell(r, 'Test Set #', 'Test Set Number'), name: cell(r, 'Test Set Name'),
    objective: cell(r, 'Objective'), cardsText: cell(r, 'Test Cards Covered'),
    cards: expandIds(cell(r, 'Test Cards Covered')).map((c) => c.id),
  }));
  const ruleRows = (impactSheet?.rows ?? []).filter((r) => cell(r, 'Rule ID') || cell(r, 'Rule Name')).map((r) => ({
    n: r.n, id: cell(r, 'Rule ID'), name: cell(r, 'Rule Name'), summary: cell(r, 'Rule Summary'),
    page: cell(r, 'Source Page'), risk: cell(r, 'Risk Level'), classification: cell(r, 'Impact Classification'),
    status: cell(r, 'Status', 'Rule Status'),
  }));
  return { sheets, cards, steps, sets, ruleRows, sheet: (name) => find(sheets, name.toLowerCase()) };
}

/** The ALM steps of one card: the rows whose Test Name starts with the card's ID (not a longer ID). */
export function stepsOf(pack, cardId) {
  return pack.steps.filter((s) => s.testName.startsWith(cardId)
    && !/\d/.test(s.testName.charAt(cardId.length)));
}
