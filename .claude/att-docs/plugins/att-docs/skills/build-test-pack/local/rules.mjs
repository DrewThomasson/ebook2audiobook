// Checks a document's rule export before any card is designed. `shapeProblems`
// separates what makes an export unusable (its structure) from what only
// deserves a look (values the master holds that the current procedure would not
// write, such as an older category). `rulesStale` says whether the rules
// predate the document. The caller decides what stops a job.

// A source_page value: one page, a range, or several of either.
const PAGE_REF = /^\d+(?:-\d+)?(?:, \d+(?:-\d+)?)*$/;
// The provenance lines a converted document states its revision date and page
// count on: "- Revised: 2025-10-06, from the revision history table", or
// "not stated"; "- Pages: 42".
const REVISED_LINE = /^- Revised: (\d{4}-\d{2}-\d{2})\b/m;
const PAGES_LINE = /^- Pages: (\d+)\b/m;
const DAY = /^\d{4}-\d{2}-\d{2}$/;

const isText = (value) => typeof value === 'string';
const normal = (text) => String(text).replace(/\s+/g, ' ').trim().toLowerCase();
const escaped = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

/** The ISO day the provenance block gives as the document's revision date, or null. */
export function revisedDate(markdown) {
  return REVISED_LINE.exec(markdown)?.[1] ?? null;
}

/**
 * What is wrong with an export of one document, as { errors, warnings } lines
 * for detail.log. Errors are structural: the top level, `doc`, the prefix, the
 * rule IDs and their uniqueness, the statuses, and an empty rules list. The
 * master also holds rows with older categories, requirement types that name a
 * category, blank columns and pages the document cannot place, so those are
 * warnings. A folder export is `{ exports: [...] }`, and each of its entries is
 * checked the same way.
 */
export function shapeProblems(json, docPath, markdown, shape) {
  const entries = Array.isArray(json?.exports) ? json.exports : [json];
  if (!entries.length) return { errors: ['the export holds no document'], warnings: [] };
  const context = {
    docPath, shape,
    pages: Number(PAGES_LINE.exec(markdown)?.[1] ?? 0),
    headings: new Set([...markdown.matchAll(/^#+\s+(.+)$/gm)].map((m) => normal(m[1]))),
  };
  const found = { errors: [], warnings: [] };
  for (const entry of entries) entryProblems(entry, context, found);
  return found;
}

function entryProblems(entry, { docPath, shape, pages, headings }, { errors, warnings }) {
  if (!entry || typeof entry !== 'object' || Array.isArray(entry)) {
    errors.push('the export is not an object');
    return;
  }
  if (entry.doc !== docPath) errors.push(`doc "${entry.doc}" is not the requested path`);
  const prefixOk = isText(entry.prefix) && new RegExp(shape.prefixPattern).test(entry.prefix);
  if (!prefixOk) errors.push(`prefix "${entry.prefix}" does not match ${shape.prefixPattern}`);
  if (!Array.isArray(entry.rules) || !entry.rules.length) {
    errors.push('rules is missing or empty');
    return;
  }
  const idPattern = prefixOk
    ? new RegExp(`^${escaped(entry.prefix)}-${shape.ruleIdPattern}$`) : null;
  const seen = new Set();
  entry.rules.forEach((rule, i) => {
    const where = `rule ${i + 1} (${rule?.rule_id ?? 'no rule_id'})`;
    const fail = (text) => errors.push(`${where}: ${text}`);
    const warn = (text) => warnings.push(`${where}: ${text}`);
    if (idPattern && !idPattern.test(rule?.rule_id ?? '')) fail('rule_id does not read as <prefix>-NNN');
    if (seen.has(rule?.rule_id)) fail('rule_id appears twice');
    seen.add(rule?.rule_id);
    if (!shape.statuses.includes(rule?.status)) {
      fail(`status "${rule?.status}" is not one of ${shape.statuses.join(', ')}`);
    }
    for (const column of shape.matrixColumns) {
      if (!isText(rule?.[column]) || !rule[column].trim()) warn(`${column} is missing or blank`);
    }
    if (isText(rule?.requirement_type) && rule.requirement_type !== shape.requirementType) {
      warn(`requirement_type "${rule.requirement_type}" is not "${shape.requirementType}"`);
    }
    if (isText(rule?.rule_category) && !shape.categories.includes(rule.rule_category)) {
      warn(`rule_category "${rule.rule_category}" is not a current category`);
    }
    if (isText(rule?.risk_level) && !shape.riskLevels.includes(rule.risk_level)) {
      warn(`risk_level "${rule.risk_level}" is not one of ${shape.riskLevels.join(', ')}`);
    }
    if (isText(rule?.name) && !rule.name.startsWith(`${rule.rule_id} - `)) {
      warn(`name does not start with "${rule.rule_id} - "`);
    }
    if (isText(rule?.source_page) && rule.source_page.trim()) {
      const problem = pageProblem(rule.source_page.trim(), pages, headings);
      if (problem) warn(problem);
    }
  });
}

/**
 * Why a source_page is unlikely to be a place in the document, or null. A page
 * reference is checked against the page count when the document states one,
 * 1 through N, since a page whose anchor the conversion could not place still
 * exists. Anything else has to be a heading.
 */
function pageProblem(value, pages, headings) {
  if (PAGE_REF.test(value)) {
    const numbers = value.split(/[-,] ?/).map(Number);
    return pages && numbers.some((n) => n < 1 || n > pages)
      ? `source_page "${value}" is outside the document's ${pages} pages` : null;
  }
  return headings.has(normal(value)) ? null : `source_page "${value}" is not a heading in the document`;
}

/**
 * Whether the document was revised after its rules were last confirmed. The
 * confirmation is the export's document-level `reviewed` (or `last_reviewed`)
 * day when it carries one, else the newest `created` day on its rules. A
 * document that states no revision date, or an export with neither day, gives
 * no answer, and the check passes.
 */
export function rulesStale(markdown, entries) {
  const revised = revisedDate(markdown);
  const reviewed = entries.map((entry) => entry.reviewed ?? entry.last_reviewed)
    .filter((day) => DAY.test(day)).sort().at(-1);
  const created = entries.flatMap((entry) => entry.rules ?? []).map((rule) => rule.created)
    .filter((day) => DAY.test(day)).sort().at(-1);
  const confirmed = reviewed ?? created;
  return Boolean(revised && confirmed && revised > confirmed);
}

// A struck-through mark: two tildes, not part of a longer run.
const MARK = /(?<!~)~~(?!~)/g;
const PAGE_MARKER = /<a id="page-(\d+)"><\/a>/g;
// A fence line, as the conversion's page script reads one.
const FENCE = /^\s*(```|~~~)/;
const STOPWORDS = new Set(['that', 'this', 'with', 'from', 'when', 'then', 'than', 'have', 'will',
  'shall', 'must', 'been', 'into', 'only', 'also', 'which', 'their', 'there', 'after', 'before']);
// A sentence ends in . ! ? or :, then perhaps a closing quote or bracket.
const SENTENCE_END = /[.!?:]["')\]”’]*$/;

/**
 * The text with fenced code blocks and inline code blanked out, every offset
 * kept. A fence that never closes is not a block: the text from it on is kept.
 */
function withoutCode(markdown) {
  const lines = markdown.split('\n');
  let opened = null;
  const fenced = new Set();
  lines.forEach((line, i) => {
    if (FENCE.test(line)) {
      opened = opened === null ? i : null;
      fenced.add(i);
    } else if (opened !== null) {
      fenced.add(i);
    }
  });
  // An open fence at the end ran to the end of the file; keep that text.
  if (opened !== null) for (let i = opened; i < lines.length; i += 1) fenced.delete(i);
  const blank = (line) => line.replace(/[^\n]/g, ' ');
  return lines.map((line, i) => (fenced.has(i) ? blank(line) : line.replace(/`[^`\n]*`/g, blank)))
    .join('\n');
}

const words = (text) => new Set((String(text).toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? [])
  .filter((word) => word.length >= 4 && !STOPWORDS.has(word)));

/**
 * The [open, close] offsets of each struck span. A mark pairs with the next
 * mark on its line. A mark left over on a line, with no close on it, may wrap
 * to the lines below in the same paragraph, and only when the next line with
 * marks has an odd number of them, so its first mark closes the wrap; if not,
 * the lone mark is no span. A blank line ends a wrap.
 */
function spanOffsets(text) {
  const spans = [];
  let open = null;
  let at = 0;
  for (const line of text.split('\n')) {
    const marks = [...line.matchAll(MARK)].map((m) => at + m.index);
    at += line.length + 1;
    if (!line.trim()) {
      open = null;
      continue;
    }
    if (open !== null && marks.length) {
      if (marks.length % 2) spans.push([open, marks.shift()]);
      open = null;
    }
    while (marks.length > 1) spans.push([marks.shift(), marks.shift()]);
    if (marks.length) open = marks[0];
  }
  return spans;
}

/**
 * What a struck span is. A fragment is part of a sentence: it does not end a
 * sentence and does not fill its line, list item or table cell (`~~90~~ 120
 * days`, `~~not~~`). A restated sentence is followed in its paragraph by a live
 * sentence holding at least two thirds of its significant words. Anything else
 * is a removal.
 */
function spanKind(text, start, end) {
  const struck = text.slice(start + 2, end);
  const lineStart = text.lastIndexOf('\n', start) + 1;
  const lineEnd = text.indexOf('\n', end);
  const before = text.slice(lineStart, start).replace(/^\s*(?:(?:[-*+]|\d+[.)]|>|#+)\s+)*/, '').trim();
  const after = text.slice(end + 2, lineEnd < 0 ? undefined : lineEnd).trim();
  const wholeLine = (!before || before.endsWith('|')) && (!after || after.startsWith('|'));
  // A span that starts a sentence and has its full stop outside the tildes is a sentence too.
  const starts = !before || before.endsWith('|') || /[.!?:]["')\]”’]*$/.test(before);
  const sentence = SENTENCE_END.test(struck.trim()) || (starts && /^[.!?:]/.test(after));
  const significant = words(struck);
  if ((!sentence && !wholeLine) || !significant.size) return 'fragment';
  // In a table the live sentence is in the same cell; elsewhere it is in the same paragraph.
  const table = before.endsWith('|') || after.startsWith('|');
  const paragraph = (table ? after.split('|')[0] : text.slice(end + 2).split(/\n[ \t]*\n/)[0])
    .trim().replace(/^[.!?:]+["')\]”’]*\s*/, '');
  // A sentence ends at a stop before a capital letter, so "e.g. the" does not end one.
  const next = /^[\s\S]+?[.!?:]["')\]”’]*(?=\s+[\p{Lu}\p{N}"'(\[~]|\s*$)/u.exec(paragraph)?.[0]
    ?? paragraph;
  if (next && !next.startsWith('~~')) {
    const live = words(next);
    if ([...significant].filter((w) => live.has(w)).length * 3 >= significant.size * 2) {
      return 'restated';
    }
  }
  return 'removal';
}

/**
 * The struck-through spans of a converted document that state something, as
 * { page, heading, text, kind } where each sits: `page` is the number of the
 * nearest page marker above it (null when the file has none above), `heading`
 * the normal form of the nearest heading above it (null when none), `kind` one
 * of fragment, restated or removal. Code blocks and inline code are not read.
 * A span with no letter or digit in it is empty and is left out.
 */
export function struckSpans(markdown) {
  const visible = withoutCode(markdown);
  const marks = (pattern, value) => [...visible.matchAll(pattern)]
    .map((m) => ({ at: m.index, value: value(m) }));
  const pages = marks(PAGE_MARKER, (m) => Number(m[1]));
  const headings = marks(/^#+\s+(.+)$/gm, (m) => normal(m[1].replace(/~~/g, '')));
  const above = (found, at) => found.filter((m) => m.at < at).at(-1)?.value ?? null;
  return spanOffsets(visible).filter(([start, end]) => /[\p{L}\p{N}]/u.test(visible.slice(start, end)))
    .map(([start, end]) => ({ page: above(pages, start), heading: above(headings, start),
      text: visible.slice(start + 2, end), kind: spanKind(visible, start, end) }));
}

/**
 * The struck-through spans of a document that nothing cites. A fragment or a
 * restated sentence is a change to live text and needs no retired rule. A
 * removal is cited by a retired rule at its place: the rule's `source_page` is
 * the span's page, a range or list holding it, or the heading above the span.
 */
export function uncitedStruck(markdown, rules) {
  const at = (rule, span) => {
    const cited = isText(rule?.source_page) ? rule.source_page.trim() : '';
    if (PAGE_REF.test(cited)) {
      return span.page !== null && cited.split(', ').some((part) => {
        const [from, to = from] = part.split('-').map(Number);
        return span.page >= from && span.page <= to;
      });
    }
    return Boolean(cited) && span.heading !== null && normal(cited) === span.heading;
  };
  return struckSpans(markdown).filter((span) => span.kind === 'removal'
    && !rules.some((rule) => rule?.status === 'retired' && at(rule, span)));
}
