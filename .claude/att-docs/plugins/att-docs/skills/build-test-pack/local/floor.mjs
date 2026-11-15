// Compares the scenarios two packs test. A card's scenario is the actions it
// takes (the controls it presses and the verbs it opens with), the words that
// say what it runs on, what it rules out ("no substantiated ... allegation"),
// and whether another one of the same thing is involved. Nothing about the product is built
// in: the control names come from the document and the rules, and how much a
// word counts comes from how many cards use it.

import { stemOf } from './source.mjs';

// Verbs that name an action on their own when a step opens with one.
const VERBS = new Set(['search', 'export', 'import', 'print', 'upload', 'download', 'filter', 'sort',
  'submit', 'cancel', 'delete', 'add', 'edit', 'create', 'close', 'reopen', 'reset', 'save', 'login',
  'logout', 'approve', 'reject']);
const INSTRUCTION = '(?:select|click|choose|press|hit|tap)\\s+(?:the\\s+)?[\'"\u201c\u2018]?';
// Capitalized words that open a phrase without naming a control.
const NOT_CONTROLS = new Set(['all', 'both', 'each', 'every', 'any', 'the', 'these', 'those', 'other', 'one']);
// Single words that are answers or negations, not controls, unless an instruction names them ("select No").
const ANSWER_WORDS = new Set(['yes', 'no', 'not', 'none', 'nor', 'without', 'neither', 'true', 'false']);
// A name the source follows with one of these is a part of the screen, not a control ("the Role Detail section").
const SCREEN_PARTS = '(?:section|panel|area|tab|dialog|grid|window|field|label|column|list|page|screen)';
const LIST_SPLIT = /\s*(?:,|\bor\b|\band\b)\s*/i;
const UI_TERM = /^["“'‘]?([A-Z][\w&]*(?:\s+[A-Z&][\w&]*){0,2})["”'’,]?$/;

/**
 * Control names a document and its rules mention: capitalized terms that follow
 * an instruction ("selecting Save or Save & Close", "select “Ok”") and the
 * names listed before the word "buttons" ("Save, Reset and Close buttons").
 */
export function controlNames(texts) {
  const found = new Set();
  const take = (clause) => {
    for (const item of clause.split(LIST_SPLIT)) {
      const m = UI_TERM.exec(item.trim());
      if (m && !NOT_CONTROLS.has(m[1].trim().toLowerCase())) found.add(m[1].trim());
    }
  };
  // A clause break: a comma, an optional closing quote, then a lowercase word that is not "and" or "or" ("Ok," the message closes).
  const BREAK = /,["\u201d'\u2019]?\s+(?:(?:and|or)\s+)?(?!and\b|or\b)[a-z]/;
  const screen = new RegExp(`(${'[A-Z][\\w&]*(?:\\s+[A-Z&][\\w&]*)*'})\\s+${SCREEN_PARTS}\\b`, 'g');
  for (const raw of texts) {
    // A name followed by a section word is a part of the screen at that place only: "the Role Detail section".
    const text = String(raw).replace(/\*+/g, "").replace(screen, (all, name) => all.slice(name.length).trim());
    for (const m of text.matchAll(/\b(?:select(?:ing|s)?|click(?:ing|s)?|press(?:ing)?|choos(?:e|ing)|hit)\s+(?:the\s+)?([^.;:\n]{1,60})/gi)) {
      const cut = BREAK.exec(m[1]);
      take(cut ? m[1].slice(0, cut.index) : m[1]);
    }
    // The run of capitalized names right before "buttons": "Save & Close, Save, and Reset buttons".
    const name = '[A-Z][\\w&]*(?:\\s+[A-Z&][\\w&]*)*';
    const listed = new RegExp(`(\\bthe\\s+)?((?:${name}\\s*(?:,|\\band\\b|\\bor\\b)\\s*)*${name})\\s+(?:push)?(buttons?)\\b`, 'g');
    for (const m of text.matchAll(listed)) {
      // "the Role Detail buttons" is the buttons of a part of the screen, not a button named Role Detail.
      if (m[1] && m[3] === 'buttons' && !/,|\band\b|\bor\b/.test(m[2])) continue;
      take(m[2].replace(/^The\s+/, ''));
    }
  }
  return [...found];
}

const escaped = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s+')
  .replace(/&/g, '(?:&|and)');
const controlPatterns = (names) => [...names].sort((a, b) => b.length - a.length).map((name) => ({
  name: name.toLowerCase().replace(/\s+and\s+/, ' & '),
  exact: ANSWER_WORDS.has(name.toLowerCase()) ? /(?!)/g
    : new RegExp(`(?<![\\w&])(?:${escaped(name)}|${escaped(name.toUpperCase())})(?![\\w&])`, 'g'),
  said: new RegExp(`${INSTRUCTION}(?<![\\w&])${escaped(name)}(?![\\w&])`, 'gi'),
}));

const NEGATOR = /\b(?:no|without|neither|nor)\b|\bnon-/gi;
// What ends a negator's reach: the end of the clause, or a word that starts a
// new instruction or turns from the subject to the behavior (warning, message).
const SCOPE_END = /[;.]|\b(?:select|click|choose|then|use|open|prepare|navigate|warning|message|prompt|error|dialog|displaying)\b/i;
// Another one of whatever the card is about: "another child", "a different account", "multiple records".
const OTHER_ONE = /\b(?:another|a different|a second|other|multiple|several|more than one)\s+(?:[A-Za-z]+\s+)?[A-Za-z]{3,}/i;

/** Character ranges a negation reaches: "no substantiated X, Y, or Z allegation". */
function negatedRanges(text) {
  const ranges = [];
  for (const m of text.matchAll(NEGATOR)) {
    const rest = text.slice(m.index + m[0].length);
    const end = m[0].toLowerCase() === 'non-' ? rest.search(/[\s,;.]/) : rest.search(SCOPE_END);
    ranges.push([m.index, m.index + m[0].length + (end < 0 ? rest.length : end)]);
  }
  return ranges;
}

// An action counts for more than a word: it says what the card does.
const ACTION_WEIGHT = 2;
// The mission says why; the title and focus say what is done and to whom.
const MISSION_WEIGHT = 0.5;

/**
 * A model of how scenarios compare, built over every card that will be
 * compared. `controls` are the control names from the source; `vocab` is the
 * set of word stems the source uses (to pick out what a card must cover).
 */
export function scenarioModel(cards, { controls = [], vocab = null } = {}) {
  const patterns = controlPatterns(controls);
  const cache = new Map();

  const build = (card) => {
    const parts = [[`${card.title}\n${card.focus}`, 1], [card.mission, MISSION_WEIGHT]];
    const actions = new Set();
    const tokens = new Map();
    const negated = new Map();
    let text = parts[0][0];
    // Controls first, so "Save & Close" is not also a Save.
    for (const p of patterns) {
      for (const re of [p.exact, p.said]) {
        re.lastIndex = 0;
        if (re.test(text)) {
          actions.add(p.name);
          re.lastIndex = 0;
          text = text.replace(re, ' ');
        }
      }
    }
    for (const clause of text.split(/[.;\n•]|(?:^|\s)-\s|\bthen\b/i)) {
      const first = /[A-Za-z]+/.exec(clause)?.[0];
      const stem = first && stemOf(first);
      if (stem && VERBS.has(first.toLowerCase())) actions.add(first.toLowerCase());
      else if (stem && VERBS.has(stem)) actions.add(stem);
    }
    parts[0][0] = text;
    for (const [source, weight] of parts) {
      const ranges = negatedRanges(source);
      for (const m of source.matchAll(/[A-Za-z0-9]+/g)) {
        const stem = stemOf(m[0]);
        if (!stem || (actions.has(stem) && weight === 1)) continue;
        const into = ranges.some(([a, b]) => m.index >= a && m.index < b) ? negated : tokens;
        into.set(stem, Math.max(into.get(stem) ?? 0, weight));
      }
    }
    return { actions, tokens, negated, other: OTHER_ONE.test(`${card.title} ${card.mission} ${card.focus}`) };
  };

  const scenario = (card) => {
    if (!cache.has(card)) cache.set(card, build(card));
    return cache.get(card);
  };

  // How many cards use each word: the fewer, the more it says about a card.
  const df = new Map();
  for (const card of cards) {
    const s = scenario(card);
    for (const w of new Set([...s.tokens.keys(), ...s.negated.keys()])) df.set(w, (df.get(w) ?? 0) + 1);
  }
  // Rare words count disproportionately: the square of how rare a word is.
  const weigh = (word, base) => base * (1 + Math.log((cards.length + 1) / ((df.get(word) ?? 0) + 1))) ** 2;

  /** The scenario's features with their weights; `only` limits the words to those the source uses. */
  const features = (s, only = false) => {
    const out = new Map();
    for (const a of s.actions) out.set(`do:${a}`, ACTION_WEIGHT);
    for (const [w, base] of s.tokens) if (!only || !vocab || vocab.has(w)) out.set(`on:${w}`, weigh(w, base));
    for (const [w, base] of s.negated) if (!only || !vocab || vocab.has(w)) out.set(`no:${w}`, weigh(w, base));
    if (s.other) out.set('another one', ACTION_WEIGHT);
    return out;
  };

  /** Whether two cards can stand for each other: the same kind of subject, and nothing one rules out is the other's subject. */
  const compatible = (a, b) => {
    if (a.other !== b.other) return false;
    // A card rules out a population when two of its words (all of them, if it has fewer) are
    // words the other card runs on; one shared word ("allegation") is too little to say so.
    const rulesOut = (x, y) => {
      const out = [...x.negated.keys()].filter((w) => !x.tokens.has(w));
      return out.length > 0 && out.filter((w) => y.tokens.has(w)).length >= Math.min(2, out.length);
    };
    return !rulesOut(a, b) && !rulesOut(b, a);
  };

  /**
   * How alike two scenarios are, 0 to 1 (weighted shared features, counting only the words the
   * source uses), or 0 when they cannot stand for each other.
   */
  const similarity = (a, b) => {
    if (!compatible(a, b)) return 0;
    const [fa, fb] = [features(a, true), features(b, true)];
    let shared = 0;
    let total = 0;
    for (const [k, w] of fa) { total += w; if (fb.has(k)) shared += w + fb.get(k); }
    for (const w of fb.values()) total += w;
    return total ? shared / total : 0;
  };

  return { scenario, features, compatible, similarity };
}

// Cited rules count for as much as the wording: a pair that cites the same
// rules and reads alike is the same scenario. Citing different rules never
// lowers a score, since two packs split the same rule into different pieces.
const jaccard = (a, b) => {
  const union = new Set([...a, ...b]);
  return union.size ? [...a].filter((x) => b.has(x)).length / union.size : 0;
};
const withRules = (sim, a, b) => (sim && a.size && b.size ? Math.max(sim, (jaccard(a, b) + sim) / 2) : sim);

// Smallest scenario score at which a pack card counts as testing a reference card's
// scenario: matched pairs scored 0.3 to 0.7 on wording alone, pairs with nothing in common 0.2 and below.
export const MATCH_FLOOR = 0.3;
// Scenario score at which two cards of one pack are the same test when they do not cite the same
// rules: near-identical wording scores 0.7 and above, cards on different populations well below.
export const REPEAT_SCORE = 0.7;
// Share of a reference card's source-vocabulary features the matching cards
// must hold together (a majority: one card with half its features is a real part of it) for it to count as covered rather than partly covered.
export const COVERED_SHARE = 0.5;

/**
 * Cards whose scenario repeats an earlier card's: the same actions, and either
 * the same cited rules (whatever the wording) or a score of REPEAT_SCORE or more.
 * `rulesOf(card)` gives a card's approved rule IDs. Returns { groups,
 * repeats, doubtful }: one group per distinct scenario (its cards in order), the number
 * of cards beyond the first of each, and the cards that joined a group by their
 * cited rules though they read unlike its first card.
 */
export function repeatedCards(cards, model, rulesOf = () => []) {
  const groups = [];
  const doubtful = [];
  for (const card of cards) {
    const s = model.scenario(card);
    const rules = new Set(rulesOf(card));
    // A card joins a group when it cites the same rules as any card in it (same actions, compatible wording),
    // or reads like the group's first card; wording alone is not chained from card to card.
    const sameActions = (other) => other.actions.size === s.actions.size && [...other.actions].every((a) => s.actions.has(a));
    const like = (g) => model.similarity(model.scenario(g.members[0]), s);
    const same = groups.find((g) => sameActions(model.scenario(g.members[0]))
      && (like(g) >= REPEAT_SCORE
        || (rules.size > 0 && g.members.some((member) => jaccard(rules, new Set(rulesOf(member))) === 1
          && model.compatible(model.scenario(member), s)))));
    if (same) {
      // A card that joined by its rules while reading unlike the group's first card is one a reader should confirm.
      if (like(same) < REPEAT_SCORE) doubtful.push({ card: card.id, first: same.members[0].id, });
      same.cards.push(card.id);
      same.members.push(card);
    } else groups.push({ members: [card], signature: describe(s), cards: [card.id] });
  }
  return { groups: groups.map(({ signature, cards: ids }) => ({ signature, cards: ids })), repeats: cards.length - groups.length, doubtful };
}

/** Takes the cards `splitIds` out of their groups, each into a group of its own; returns the groups and repeat count. */
export function splitGroups(groups, splitIds, total) {
  const out = [];
  for (const g of groups) {
    const keep = g.cards.filter((id) => !splitIds.has(id) || id === g.cards[0]);
    out.push({ ...g, cards: keep });
    for (const id of g.cards) if (splitIds.has(id) && id !== g.cards[0]) out.push({ signature: g.signature, cards: [id] });
  }
  return { groups: out, repeats: total - out.length };
}

/** A scenario in words for a report: its actions and the words that set it apart. */
function describe(s) {
  const top = [...s.tokens].sort((a, b) => b[1] - a[1]).map(([w]) => w).slice(0, 4);
  const out = [...s.actions].join('+') || 'no action';
  const no = [...s.negated.keys()].filter((w) => !s.tokens.has(w)).slice(0, 3);
  return [out, top.join(' '), s.other ? 'another one' : '', no.length ? `not ${no.join(' ')}` : ''].filter(Boolean).join(' | ');
}

/**
 * Each reference card's pack cards by scenario, the cited rules counting as
 * much as the wording. `rulesOf(which, card)` gives a card's approved rule IDs.
 * Pack cards that score `floor` or above, and compatible cards that share an
 * action with the reference card, are combined greedily, each adding the
 * features of the reference card (its actions and the words the source uses)
 * the others lack. The card is covered when at least one card scores `floor`
 * and together they hold COVERED_SHARE of the features; it is partly covered
 * when only some do; it is unmatched when no card qualifies. A card with no
 * features is reported as such.
 */
export function crosswalkCards(reference, pack, rulesOf, model, floor = MATCH_FLOOR) {
  return reference.map((card) => {
    const s = model.scenario(card);
    const mine = new Set(rulesOf('reference', card));
    const all = pack.map((p) => ({ card: p, id: p.id, sim: model.similarity(s, model.scenario(p)),
      score: withRules(model.similarity(s, model.scenario(p)), mine, new Set(rulesOf('pack', p))) }))
      .filter((x) => x.sim > 0).sort((a, b) => b.score - a.score);
    // A card that does the same thing, and any compatible card that shares an action (it may cover a part).
    const strong = all.filter((x) => x.score >= floor);
    const sharesAction = (x) => [...model.scenario(x.card).actions].some((a) => s.actions.has(a));
    const scored = [...new Set([...strong, ...all.filter(sharesAction)])];
    const wanted = model.features(s, true);
    const wantedTotal = [...wanted.values()].reduce((n, w) => n + w, 0);
    const held = new Set();
    const parts = [];
    for (;;) {
      let best = null;
      let gain = 0;
      for (const x of scored) {
        if (parts.includes(x)) continue;
        const have = model.features(model.scenario(x.card), true);
        const add = [...wanted].filter(([k]) => have.has(k) && !held.has(k)).reduce((n, [, w]) => n + w, 0);
        if (add > gain) { gain = add; best = x; }
      }
      if (!best) break;
      parts.push(best);
      for (const k of model.features(model.scenario(best.card), true).keys()) if (wanted.has(k)) held.add(k);
    }
    const share = wantedTotal ? [...held].reduce((n, k) => n + wanted.get(k), 0) / wantedTotal : 0;
    const top = strong.filter((x) => x.score >= strong[0].score - 0.05);
    // Covered takes cards that do the same thing. Cards that only share an action with the reference card
    // fill in a part of it and cannot, however many join, make it covered. And everything the card does
    // (each action it takes) has to be done by one strong card.
    const strongHeld = new Set();
    for (const x of strong) {
      for (const k of model.features(model.scenario(x.card), true).keys()) if (wanted.has(k)) strongHeld.add(k);
    }
    const strongShare = wantedTotal ? [...strongHeld].reduce((n, k) => n + wanted.get(k), 0) / wantedTotal : 0;
    const actions = [...wanted.keys()].filter((k) => k.startsWith('do:'));
    const doneByOne = strong.some((x) => {
      const have = model.features(model.scenario(x.card), true);
      return actions.every((k) => have.has(k));
    });
    return { card: card.id, row: card.n, scenario: describe(s), matched: scored.length > 0,
      status: !wantedTotal ? 'no features' : !scored.length ? 'unmatched'
        : strong.length && strongShare >= COVERED_SHARE && doneByOne ? 'covered' : 'partly covered',
      share, matches: top.map((x) => ({ card: x.id, score: x.score })),
      parts: parts.map((x) => x.id), candidates: scored.length };
  });
}

/** Sets and the cards each holds, and whether the Full Coverage set holds every requirement-derived card. */
export function setReport(pack) {
  const requirement = pack.cards.filter((c) => !/quality-derived/i.test(c.rulesCovered)).map((c) => c.id);
  const full = pack.sets.find((s) => /full coverage/i.test(`${s.name} ${s.objective}`));
  return {
    sets: pack.sets.length, cards: pack.cards.length,
    perSet: pack.sets.map((s) => ({ number: s.number, name: s.name, cards: s.cards.length })),
    fullCoverage: full ? { set: full.name, holds: full.cards.length, requirementCards: requirement.length,
      missing: requirement.filter((id) => !full.cards.includes(id)) } : null,
  };
}

