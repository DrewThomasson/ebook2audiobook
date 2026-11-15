// What a pack is judged against: the approved rules (from a rule export or a
// Business Rules workbook) and the converted document, split into live text
// and struck-through (retired) text. Also the word-level text comparison the
// checks share.

import fs from 'node:fs';
import { readXlsx } from './xlsx.mjs';

// English function words, which carry no meaning for matching one statement to
// another. Words that are common in one domain (child, role, window) are not
// listed: weighting by how many texts hold a word does that job per input.
const STOP = new Set(['the', 'and', 'for', 'with', 'that', 'this', 'from', 'when', 'will', 'are',
  'was', 'has', 'have', 'its', 'not', 'any', 'all', 'can', 'into', 'upon', 'than', 'then', 'their',
  'which', 'who', 'also', 'but', 'per', 'via', 'each', 'both', 'such', 'only', 'they', 'them',
  'been', 'being', 'does', 'did', 'his', 'her', 'she', 'our', 'out', 'too', 'very']);

/** A lowercase word with a plural or verb ending removed, or null for a short word or filler. */
export function stemOf(raw) {
  const word = raw.toLowerCase();
  if (word.length < 3 || STOP.has(word)) return null;
  return word.replace(/(?<=.{3})(ing|ed|es|s)$/, '');
}

/** Lowercase words with a plural or verb ending removed; short words and filler dropped. */
export function words(text) {
  return (String(text).match(/[A-Za-z0-9]+/g) ?? []).map(stemOf).filter(Boolean);
}

export const wordSet = (text) => new Set(words(text));

/** Dice coefficient of two word sets: 2|A and B| / (|A| + |B|). */
export function dice(a, b) {
  if (!a.size || !b.size) return 0;
  let shared = 0;
  for (const word of a) if (b.has(word)) shared += 1;
  return (2 * shared) / (a.size + b.size);
}

/** Share of A's words that B holds: |A and B| / |A|. */
export function containment(a, b) {
  if (!a.size) return 0;
  let shared = 0;
  for (const word of a) if (b.has(word)) shared += 1;
  return shared / a.size;
}

/** The text with whitespace collapsed and case folded, for equality tests. */
export const squash = (text) => String(text).replace(/\s+/g, ' ').trim().toLowerCase();

const RULE_ID = /^(\S+?-\d+)\b/;

/** The ID at the head of an export Name such as "BR-ABC-010 - Allow ...", or ''. */
export const idOfName = (name) => RULE_ID.exec(String(name ?? '').trim())?.[1] ?? '';

/** The quoted source text a rule's Description opens with, else the whole Description. */
export function quoteOf(description) {
  const text = String(description ?? '');
  const quoted = /"([\s\S]*?)"\s*(?:\n\s*)+Atomic Summary/.exec(text);
  if (quoted) return quoted[1];
  return text.replace(/^\([^)]*\)\s*/, '').split(/Atomic Summary:/)[0];
}

function normalizeRule(row) {
  const name = String(row.name ?? '');
  const id = row.rule_id || idOfName(name);
  return {
    id,
    name: name.replace(/^\S+-\d+\s*[-–—]\s*/, '').trim() || name,
    status: row.status || 'active',
    summary: String(row.rule_summary ?? ''),
    description: String(row.description ?? ''),
    page: String(row.source_page ?? '').trim(),
    risk: String(row.risk_level ?? '').trim(),
    category: String(row.rule_category ?? '').trim(),
  };
}

/** Approved rules from a JSON export (one document or a folder export) or a Business Rules workbook. */
export function loadRules(file) {
  if (/\.xlsx$/i.test(file)) {
    const sheet = readXlsx(file).find((s) => s.rows.some((row) => row
      && row.includes('Rule Summary') && row.includes('Name')));
    if (!sheet) throw new Error('--rules workbook has no Name and Rule Summary columns');
    const headerAt = sheet.rows.findIndex((row) => row?.includes('Rule Summary'));
    const header = sheet.rows[headerAt];
    const column = (name) => header.indexOf(name);
    return sheet.rows.slice(headerAt + 1).filter((row) => row?.[column('Name')]).map((row) => normalizeRule({
      name: row[column('Name')], description: row[column('Description')],
      source_page: row[column('Source Page')], rule_summary: row[column('Rule Summary')],
      risk_level: row[column('Risk Level')], rule_category: row[column('Rule Category')],
    }));
  }
  const json = JSON.parse(fs.readFileSync(file, 'utf8'));
  const entries = Array.isArray(json.exports) ? json.exports : [json];
  if (!entries.every((entry) => Array.isArray(entry?.rules))) {
    throw new Error('--rules is not a rule export');
  }
  return entries.flatMap((entry) => entry.rules.map(normalizeRule));
}

/** The prefix part of each rule ID, such as "BR-ABC" for "BR-ABC-010". */
export const idPrefixes = (rules) => [...new Set(rules.map((r) => r.id.replace(/-\d+$/, '')).filter(Boolean))];

const STRUCK = /~~([\s\S]*?)~~/g;

/**
 * The document split into live and struck text. `spans` are the struck-through
 * runs (a run may cross lines, quotes and list items) with the first line each
 * sits on; `live` is the remaining text as paragraphs with their first line.
 * `pageAt(line)` gives the page anchor in force at a line.
 */
export function parseDoc(markdown) {
  const lines = String(markdown).split('\n');
  const starts = [0];
  for (let i = 0; i < markdown.length; i += 1) if (markdown[i] === '\n') starts.push(i + 1);
  const lineOf = (offset) => {
    let lo = 0;
    let hi = starts.length - 1;
    while (lo < hi) {
      const mid = (lo + hi + 1) >> 1;
      if (starts[mid] <= offset) lo = mid; else hi = mid - 1;
    }
    return lo + 1;
  };
  const spans = [];
  for (const m of markdown.matchAll(STRUCK)) {
    const text = m[1].replace(/^\s*[>*]*\s*/gm, '').replace(/\s+/g, ' ').trim();
    if (text) spans.push({ text, line: lineOf(m.index), endLine: lineOf(m.index + m[0].length - 1) });
  }
  // Live text: the markdown with each struck run blanked out, kept line for line.
  const blanked = markdown.replace(STRUCK, (run) => run.replace(/[^\n]/g, ' '));
  const live = [];
  let block = [];
  const flush = (endLine) => {
    const text = block.map((b) => b.text).join(' ').replace(/\s+/g, ' ').trim();
    if (text) live.push({ text, line: block[0].line, endLine });
    block = [];
  };
  blanked.split('\n').forEach((raw, i) => {
    const text = raw.replace(/<a id="[^"]*"><\/a>(?:\*Page \d+\*)?/g, '').replace(/^\s*(?:[>*#-]|\d+\.)+\s*/, '').trim();
    if (!raw.trim()) flush(i);
    else if (text) block.push({ text, line: i + 1 });
  });
  flush(lines.length);
  const pages = [...markdown.matchAll(/<a id="page-(\d+)"><\/a>/g)]
    .map((m) => ({ page: Number(m[1]), line: lineOf(m.index) }));
  const pageAt = (line) => pages.findLast((p) => p.line <= line)?.page ?? null;
  return { spans, live, pageAt, lines };
}
