// Checks a pack's content against the approved rules and the document. None
// of it calls a model: rule rows are matched to rules by ID, then by shared
// words; retired behavior is found from the struck-through text; an Expected
// Result is compared with the last step that tests it.

import { cell, expandIds, stepsOf } from './pack.mjs';
import { containment, dice, idOfName, quoteOf, squash, wordSet, words } from './source.mjs';

// Share of words (Dice) at which a rule row is taken as the wording of an
// approved rule: a paraphrase of one rule keeps well over this share of its
// words, while two rules that only share the window's vocabulary fall below it.
export const TEXT_MATCH = 0.4;
// Share of an approved rule's words that must sit in struck-through text, and
// more than sit in any live paragraph, for the rule to count as retired by the
// document: most of what the rule says is gone.
export const RETIRED_SHARE = 0.5;

const RETIRED_CLASS = /supersed|retire|remov/i;
export const isRetiredRow = (row) => RETIRED_CLASS.test(row.classification)
  || /^\s*retired\b/i.test(row.summary) || /^\s*retired\s*$/i.test(row.status);

/**
 * The approved rules the document has struck through: { id -> { span, struck,
 * live } }. A rule is retired by the document when most of its quoted source
 * text sits in a struck span and the live text holds less of it. A rule whose
 * export status is retired or superseded is included too (with `span` null).
 */
export function retiredRules(rules, doc) {
  const out = new Map();
  const spans = doc.spans.map((span) => ({ span, set: wordSet(span.text) }));
  const live = doc.live.map((p) => wordSet(p.text));
  for (const rule of rules) {
    const own = wordSet(quoteOf(rule.description) || rule.summary);
    let struck = 0;
    let closest = 0;
    let span = null;
    // The span that holds most of the rule's words; of equals, the one that is least else.
    for (const s of spans) {
      const share = containment(own, s.set);
      const like = dice(own, s.set);
      if (share > struck || (share === struck && like > closest)) { struck = share; closest = like; span = s.span; }
    }
    const liveShare = Math.max(0, ...live.map((p) => containment(own, p)));
    if (struck >= RETIRED_SHARE && struck > liveShare) out.set(rule.id, { span, struck, live: liveShare });
    else if (/^(retired|superseded)$/i.test(rule.status)) out.set(rule.id, { span: null, struck: 0, live: liveShare });
  }
  return out;
}

/** A struck span a piece of text mostly says, else null. */
export function struckSpanFor(text, doc) {
  const own = wordSet(text);
  const live = Math.max(0, ...doc.live.map((p) => containment(own, wordSet(p.text))));
  let best = null;
  let bestShare = 0;
  for (const s of doc.spans) {
    const share = containment(own, wordSet(s.text));
    if (share > bestShare) { best = s; bestShare = share; }
  }
  return bestShare >= RETIRED_SHARE && bestShare > live ? best : null;
}

const ruleTexts = (rule) => [rule.summary, rule.name, quoteOf(rule.description)].filter(Boolean).map(wordSet);
const rowTexts = (row) => [row.summary, row.name.replace(/^\S+-\d+\s*[-–—]\s*/, '')].filter(Boolean).map(wordSet);

// A rule a row also covers (beyond the one it matches best) needs this share of
// its words, weighted so that words few rules use count most, to appear in the row:
// all but a stray word, since a sibling rule that only shares the window's wording lacks one.
const COVERS = 0.95;
// ... and the row must read like the rule too, at this Dice share: half the words, since
// a merged row is longer than any one rule it holds.
const MERGED_LIKE = 0.5;
// ... and the row has to say clearly more than the rule does, as a row that
// merges several rules does; this many times its words (a row of two statements is at least this long).
const MERGED_SIZE = 1.5;
// A clause of a merged row matches a rule when the mean of their Dice and containment is this high:
// a clause is short, so it must be mostly inside the rule (containment) and not only share its vocabulary;
// the true clause matches scored 0.76 to 1.0, wrong siblings 0.62 and below.
const CLAUSE_MATCH = 0.7;
// ... and beat the next rule by this much, so a clause that two sibling rules fit equally is not assigned.
const CLAUSE_MARGIN = 0.05;

/** The rules' word sets, and how rare each word is among the rules (0 for a word in all of them). */
export function prepareRules(rules) {
  const texts = new Map(rules.map((r) => [r.id, ruleTexts(r)]));
  const count = new Map();
  for (const sets of texts.values()) for (const w of new Set(sets.flatMap((x) => [...x]))) count.set(w, (count.get(w) ?? 0) + 1);
  const rare = (w) => Math.log((rules.length + 1) / ((count.get(w) ?? 0) + 1));
  return { texts, rare };
}

function coverage(row, rule, rare) {
  let total = 0;
  let held = 0;
  for (const w of rule) {
    total += rare(w);
    if (row.has(w)) held += rare(w);
  }
  return total ? held / total : 0;
}

/**
 * Which approved rules a rule row is: by the ID in its Rule ID or Rule Name,
 * else by the shared words of its summary or name with a rule's summary, name
 * or quoted source text. Returns { rule, rules, how, score, close } or null:
 * `rule` is the best match, `rules` all the rules the row covers (the best one
 * first; a row that merges several rules covers each one whose words it holds),
 * and `close` lists other rules that scored within a hundredth of the best.
 */
export function matchRuleRow(row, rules, prepared = prepareRules(rules)) {
  const { texts } = prepared;
  const id = [row.id, idOfName(row.name)].map((s) => s.trim().toUpperCase())
    .find((s) => rules.some((r) => r.id.toUpperCase() === s));
  if (!id) return textMatch(row, rules, prepared);
  const rule = rules.find((r) => r.id.toUpperCase() === id);
  const mine = rowTexts(row);
  const own = Math.max(0, ...mine.flatMap((a) => texts.get(rule.id).map((b) => dice(a, b))));
  // A row with no wording of its own has nothing to check an ID against.
  if (!mine.length || own >= TEXT_MATCH) return { rule, rules: [rule], how: 'id', score: 1, close: [] };
  // The ID names a rule the row does not read like. A rule it does read like, clearly better, is
  // what the row is: the workbook was numbered against an older rule set. Otherwise the ID stands, unconfirmed.
  const text = textMatch(row, rules, prepared);
  if (text && text.rule.id !== rule.id && text.score - own >= ID_MISMATCH_MARGIN) {
    return { ...text, how: 'renumbered', claimedId: rule.id };
  }
  return { rule, rules: [rule], how: 'id-unconfirmed', score: own, close: [] };
}

// A row whose ID names a rule it does not read like is taken as renumbered when another rule reads
// this much more like it (Dice).
export const ID_MISMATCH_MARGIN = 0.1;

/** The wording half of matchRuleRow: the rules a row reads like, whatever ID it carries. */
function textMatch(row, rules, prepared) {
  const { texts, rare } = prepared;
  const mine = rowTexts(row);
  const scored = rules.map((rule) => {
    let score = 0;
    let covers = 0;
    for (const a of mine) {
      for (const b of texts.get(rule.id)) {
        const like = dice(a, b);
        if (like < TEXT_MATCH) continue;
        const held = coverage(a, b, rare);
        score = Math.max(score, like);
        if (like >= MERGED_LIKE && held >= COVERS && a.size >= MERGED_SIZE * b.size) covers = Math.max(covers, held);
      }
    }
    return { rule, score, covers };
  }).sort((a, b) => b.score - a.score);
  if (!scored.length || scored[0].score < TEXT_MATCH) return null;
  const close = scored.slice(1).filter((s) => scored[0].score - s.score < 0.01).map((s) => s.rule.id);
  // A row of several statements (split at commas, semicolons and "and") is also matched clause by
  // clause; the rules its clauses pick are the rules it merges.
  const clause = clauseMatches(row, rules, texts);
  // A row can only merge as many rules as it has statements (parts split at commas, semicolons and "and").
  const parts = Math.max(...[row.summary, row.name].map((t) => String(t).split(/[,;]|\band\b/i).filter((x) => words(x).length >= 2).length));
  const also = scored.slice(1).filter((s) => s.covers > 0).slice(0, Math.max(0, parts - 1)).map((s) => s.rule);
  const best = scored[0].rule;
  let listed = [best, ...also];
  if (clause.rules.length) {
    // Two or more statements picked rules, so they say what the row merges; the whole-row best stays only if one picked it too.
    listed = clause.rules.some((r) => r.id === best.id) ? [best, ...clause.rules.filter((r) => r.id !== best.id)] : [...clause.rules];
    for (const r of also) if (!listed.includes(r)) listed.push(r);
  }
  return { rule: listed[0], rules: listed, how: 'text', score: scored[0].score, close, unmatched: clause.unmatched };
}

// A statement may take a rule from the section of a rule its row already matched at this lower bar:
// siblings in one section share the window's wording, so only the section (not the words) vouches for them.
const CLAUSE_SIBLING = 0.5;
const sectionOf = (rule) => /^\(([^)]*)\)/.exec(rule.description)?.[1] ?? null;

/**
 * The rules the statements of a row each match (see CLAUSE_MATCH), best first, and the statements
 * that matched none. A row needs two statements that each pick a rule before any counts.
 */
function clauseMatches(row, rules, texts) {
  const best = { rules: [], unmatched: [], picks: 0 };
  for (const text of [row.name, row.summary]) {
    const clauses = String(text).split(/[,;]|\band\b/i).map((raw) => ({ raw: raw.trim(), set: wordSet(raw) })).filter((c) => c.set.size >= 2);
    if (clauses.length < 2) continue;
    const score = (clause, pool) => pool.map((rule) => ({ rule, score: Math.max(...texts.get(rule.id).map((t) => (dice(clause.set, t) + containment(clause.set, t)) / 2)) }))
      .sort((a, b) => b.score - a.score);
    const picked = new Map();
    const open = [];
    for (const clause of clauses) {
      const [first, second] = score(clause, rules);
      if (first.score >= CLAUSE_MATCH && first.score - (second?.score ?? 0) >= CLAUSE_MARGIN) {
        picked.set(first.rule, Math.max(picked.get(first.rule) ?? 0, first.score));
      } else open.push(clause);
    }
    if (picked.size < 2 && clauses.length - open.length < 2) continue;
    const sections = new Set([...picked.keys()].map(sectionOf).filter(Boolean));
    const unmatched = [];
    for (const clause of open) {
      const pool = rules.filter((r) => sections.has(sectionOf(r)) && !picked.has(r));
      const [first, second] = score(clause, pool);
      if (first && first.score >= CLAUSE_SIBLING && first.score - (second?.score ?? 0) >= CLAUSE_MARGIN) picked.set(first.rule, first.score);
      else unmatched.push(clause.raw);
    }
    if (picked.size > best.picks) {
      best.picks = picked.size;
      best.rules = [...picked].sort((a, b) => b[1] - a[1]).map(([rule]) => rule);
      best.unmatched = unmatched;
    }
  }
  return best;
}

/**
 * Words the document uses only inside struck text, never in live text, and
 * more than once there: what the retired behavior is about, not a word that
 * happens to occur in a single struck sentence. Map of stem -> the first struck
 * span that holds it.
 */
export function struckOnlyWords(doc) {
  const live = new Set(doc.live.flatMap((p) => words(p.text)));
  const count = new Map();
  const first = new Map();
  for (const span of doc.spans) {
    for (const word of words(span.text)) {
      if (live.has(word)) continue;
      count.set(word, (count.get(word) ?? 0) + 1);
      if (!first.has(word)) first.set(word, span);
    }
  }
  return new Map([...first].filter(([word]) => count.get(word) > 1));
}

// A comma part that opens with one of these and runs on is a statement of its own, not a list item.
const NEW_SUBJECT = /^(?:the|a|an|this|that|these|those|each|it|they|he|she|there|then|user|users|system)$/;
const NEGATING = /^(no|not|without|never|retired|removed|absent|longer|neither|nor|cannot)$|n't$/;
// A word that follows the behavior it takes away ("Warning Removal", "warning suppressed"), and how far back it reaches.
const REMOVAL = /^(?:removal|removed|suppress\w*|absence|absent)$/;
const REMOVAL_REACH = 2;

/**
 * Struck-only words a piece of text uses as live behavior. A negation reaches
 * the rest of its sentence (not the parts before it), across a list ("no confirmation, warning, or
 * prompt"), up to a "but", "then", "however", "while" or semicolon that starts
 * a new statement; words in that stretch say the behavior is gone and are not
 * counted. Returns [{ word, span }].
 */
export function staleHits(text, struckOnly) {
  const hits = new Map();
  const statements = String(text).replace(/[\u2019\u2018]/g, "'").split(/(?<=[.;!?])\s+|\n+|[,;]?\s+\b(?:but|then|however|while|although)\b\s+/i);
  for (const statement of statements) {
    // A negation reaches the comma parts after it until one starts a new statement of its own.
    let negated = false;
    for (const part of statement.split(',')) {
      const tokens = part.toLowerCase().match(/[a-z']+/g) ?? [];
      const own = tokens.filter((t) => !/^(?:and|or)$/.test(t));
      if (negated && own.length >= 3 && NEW_SUBJECT.test(own[0])) negated = false;
      if (!negated && tokens.some((t) => NEGATING.test(t))) {
        negated = true;
        continue;
      }
      if (negated) continue;
      // "Warning Removal": a word followed within a few words by a removal says the behavior is gone.
      const gone = new Set();
      tokens.forEach((t, i) => {
        if (!REMOVAL.test(t)) return;
        for (const before of tokens.slice(Math.max(0, i - REMOVAL_REACH), i)) for (const w of words(before)) gone.add(w);
      });
      for (const word of words(part)) {
        if (struckOnly.has(word) && !hits.has(word) && !gone.has(word)) hits.set(word, struckOnly.get(word));
      }
    }
  }
  return [...hits].map(([word, span]) => ({ word, span }));
}

/**
 * Every rule row of a pack: its match, and what it says about retired
 * behavior. `outside` is 'retired' when the row matches no rule but says what
 * a struck span says, 'not in the source' when it matches nothing.
 */
export function crosswalkRows(pack, rules, retired, doc) {
  const prepared = prepareRules(rules);
  const struckOnly = struckOnlyWords(doc);
  return pack.ruleRows.map((row) => {
    const match = matchRuleRow(row, rules, prepared);
    const marked = isRetiredRow(row);
    let outside = null;
    let span = null;
    if (!match) {
      span = struckSpanFor(`${row.name} ${row.summary}`, doc);
      outside = span ? 'retired' : 'not in the source';
    }
    const retiredRule = match ? match.rules.map((r) => retired.get(r.id)).find(Boolean) ?? null : null;
    const stale = marked || outside === 'retired' ? [] : staleHits(`${row.name}. ${row.summary}`, struckOnly);
    return { row, match, marked, outside, span, retiredRule, stale,
      liveAsRetired: Boolean(retiredRule) && !marked };
  });
}

/**
 * Whether a pack records each rule the document retired: 'recorded' (a row
 * for it marked superseded or retired), 'unmarked' (a row for it that does not
 * say so), or 'missing'. Struck spans no approved rule covers are listed too.
 */
export function retiredRecord(rows, rules, retired, doc) {
  const byId = new Map(rules.map((r) => [r.id, r]));
  const listed = [...retired].map(([id, info]) => {
    const mine = rows.filter((r) => r.match?.rules.some((x) => x.id === id));
    const status = mine.some((r) => r.marked) ? 'recorded' : mine.length ? 'unmarked' : 'missing';
    return { id, summary: byId.get(id).summary, line: info.span?.line ?? null, status,
      rows: mine.map((r) => r.row.n) };
  });
  // A struck span is covered when a retired rule says most of what it says.
  const retiredWords = [...retired.keys()].map((id) => wordSet(`${quoteOf(byId.get(id).description)} ${byId.get(id).summary}`));
  const spans = doc.spans.filter((s) => !retiredWords.some((w) => containment(wordSet(s.text), w) >= RETIRED_SHARE)).map((s) => {
    const mine = rows.filter((r) => r.span === s);
    return { line: s.line, text: s.text, status: mine.some((r) => r.marked) ? 'recorded' : 'no rule' };
  });
  return { rules: listed, spans };
}

/**
 * A card's cited rules as approved rule IDs. Explicit IDs (ranges and
 * abbreviations expanded) are kept; a citation written as a sentence is
 * resolved to the pack's own rule row by its words, then to its approved rule.
 * Returns { ids, cited, sentences, unresolved }.
 */
export function citedRules(card, rows, rules) {
  const cited = expandIds(card.rulesCovered);
  const ids = new Set();
  const byId = new Map(rules.map((r) => [r.id.toUpperCase(), r.id]));
  for (const { id } of cited) if (byId.has(id.toUpperCase())) ids.add(byId.get(id.toUpperCase()));
  const sentences = cited.length ? [] : card.rulesCovered.split('\n').map((s) => s.trim()).filter(Boolean);
  const unresolved = [];
  for (const text of sentences) {
    const key = squash(text);
    let hit = rows.find((r) => squash(r.row.id) === key || squash(r.row.name) === key);
    if (!hit) {
      const mine = wordSet(text);
      const scored = rows.map((r) => ({ r, s: Math.max(dice(mine, wordSet(r.row.id)), dice(mine, wordSet(r.row.name))) }))
        .sort((a, b) => b.s - a.s);
      if (scored[0]?.s >= TEXT_MATCH) hit = scored[0].r;
    }
    if (hit?.match) for (const r of hit.match.rules) ids.add(r.id);
    else unresolved.push(text);
  }
  return { ids: [...ids], cited, sentences, unresolved };
}

/**
 * Rule IDs the cards cite, and where each one is listed: an approved rule, an
 * Impact Analysis row, a matrix. Returns [{ id, cards, approved, impact,
 * matrix }] for every cited ID.
 */
export function citedIds(pack, rules, rows) {
  const approved = new Set(rules.map((r) => r.id.toUpperCase()));
  const inImpact = new Set(rows.flatMap((r) => [r.row.id, idOfName(r.row.name)]).filter(Boolean)
    .map((s) => s.toUpperCase()));
  const matrix = new Set();
  for (const name of ['rule-to-test matrix', 'coverage matrix', 'objective matrix']) {
    for (const row of pack.sheet(name)?.rows ?? []) {
      for (const { id } of expandIds(cell(row, 'Rule ID'))) matrix.add(id.toUpperCase());
    }
  }
  const cards = new Map();
  for (const card of pack.cards) {
    for (const { id } of expandIds(card.rulesCovered)) {
      if (!cards.has(id)) cards.set(id, []);
      cards.get(id).push(card.id);
    }
  }
  return [...cards].map(([id, by]) => ({ id, cards: [...new Set(by)], approved: approved.has(id.toUpperCase()),
    impact: inImpact.has(id.toUpperCase()), matrix: matrix.has(id.toUpperCase()) }));
}

// Words that say what an Expected Result shows. A card that expects the change
// to go through uses the first group; one that expects a stop or an undo, the second.
const GOES_THROUGH = /^(success\w*|saves?|saved|chang\w*|updates?|updated|refresh\w*|persist\w*|enabled?|allow\w*|permit\w*)$/;
const STOPS = /^(error|errors|block\w*|prevent\w*|cannot|reject\w*|denied|disabled?|fails?|failed|unchanged|reset|resets|restor\w*|revert\w*|remains?|discard\w*|cancel\w*|abort\w*|undo\w*|undone|lost)$/;
const NOT = /^(not|no|never|without)$|n't$/;
// A negator reaches the next few words of its sentence ("no warning or error").
const NEGATION_REACH = 3;

/**
 * Whether an Expected Result expects the change to go through ('goes through'),
 * to be stopped or undone ('stops'), shows both in different sentences
 * ('mixed') or neither ('neutral'). A sentence with a stop in it is a stop
 * ("a role cannot be downgraded"); "not saved" reads as a stop; "no error"
 * removes the stop; "the previously saved value" is not a save.
 */
export function outcomeOf(text) {
  let through = 0;
  let stops = 0;
  const plain = String(text).toLowerCase().replace(/[\u2019\u2018]/g, "'").replace(/\b(?:previously|last)[\s-]+saved\b/g, ' ');
  for (const sentence of plain.split(/(?<=[.;!?])\s+|\n+/)) {
    // Words and commas. A comma starts a new statement when what follows has a subject before its
    // cue ("no warning, role saved"), and continues a list when the cue comes first ("no warning, error, or prompt").
    const tokens = sentence.match(/[a-z']+|,/g) ?? [];
    const cue = (t) => GOES_THROUGH.test(t) || STOPS.test(t);
    let goes = false;
    let stopped = false;
    let lastNot = -Infinity;
    let distance = 0;
    tokens.forEach((token, i) => {
      if (token === ',') {
        const next = [];
        for (let j = i + 1; j < tokens.length && tokens[j] !== ','; j += 1) if (!/^(?:and|or)$/.test(tokens[j])) next.push(tokens[j]);
        if (next.findIndex(cue) >= 1) lastNot = -Infinity;
        else if (distance - lastNot <= NEGATION_REACH) lastNot = distance; // a bare list item keeps the negation going
        return;
      }
      distance += 1;
      if (NOT.test(token)) { lastNot = distance; return; }
      const negated = distance - lastNot <= NEGATION_REACH && lastNot > 0;
      if (GOES_THROUGH.test(token)) {
        if (negated) stopped = true; else goes = true;
      } else if (STOPS.test(token) && !negated) stopped = true;
    });
    if (stopped) stops += 1; else if (goes) through += 1;
  }
  if (through && stops) return 'mixed';
  return through ? 'goes through' : stops ? 'stops' : 'neutral';
}

/**
 * Each card's Expected Result against the Expected Result of the last ALM step
 * that tests it. A card contradicts its step when one expects the change to go
 * through and the other expects it stopped, or when they share almost no words.
 */
export function expectedResultChecks(pack) {
  return pack.cards.map((card) => {
    const steps = stepsOf(pack, card.id);
    const last = [...steps].reverse().find((s) => s.expected.trim());
    if (!last) return { card: card.id, row: card.n, steps: steps.length, checked: false };
    const cardOutcome = outcomeOf(card.expected);
    const stepOutcome = outcomeOf(last.expected);
    const similarity = dice(wordSet(card.expected), wordSet(last.expected));
    const opposed = (cardOutcome === 'goes through' && stepOutcome === 'stops')
      || (cardOutcome === 'stops' && stepOutcome === 'goes through');
    return { card: card.id, row: card.n, stepRow: last.n, steps: steps.length, checked: true, cardOutcome,
      stepOutcome, similarity, contradicts: opposed || similarity < LOW_SIMILARITY,
      reason: opposed ? 'the card and its last step expect opposite outcomes' : 'almost no words in common' };
  });
}

// Expected Results below this Dice share of words describe different things.
export const LOW_SIMILARITY = 0.1;
