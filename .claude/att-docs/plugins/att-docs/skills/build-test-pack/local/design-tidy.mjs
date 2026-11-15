// Tidies a document's designed cards before they are verified: scenarios that
// only check retired rules are merged by the control they press, a card that
// only answers a message or resets joins the card that raises the message, and
// a card that repeats another is dropped. A BREAK IT card is only ever joined
// to or dropped as a repeat of another BREAK IT card, and a plain card of a
// plain one: the two go in different sets. `isBreak(card)` says which cards go
// in the BREAK IT set; by default the cards flagged `breakIt`. Pure functions
// over the design state; the phase calls them and records what they report.

import { controlNames, repeatedCards, scenarioModel } from './floor.mjs';
import { words } from './source.mjs';

const list = (value) => (Array.isArray(value) ? value
  : value === undefined || value === null || value === '' ? [] : [value]);

const flagged = (card) => card.breakIt === true;

/** The control names a document and its rules mention. */
export function docControls(doc, rules) {
  return controlNames([doc.text ?? '', ...rules.map((rule) => rule.summary ?? '')]);
}

/** The words the source uses, to rate which words of a card say something. */
const vocabOf = (doc, rules) => new Set([doc.text ?? '', ...rules.map((rule) => rule.summary ?? '')]
  .flatMap((text) => words(text)));

/** A card as the scenario model reads it: an id, a title, a mission and a focus line. */
const viewOf = (card, id) => ({ id, card, title: card.title ?? '', mission: card.mission ?? '',
  focus: list(card.focus).join('. '), rules: list(card.rules) });

/**
 * The repeats among a document's cards, found among the BREAK IT cards and
 * among the rest apart, over one scenario model of every card so a word weighs
 * the same in both. Groups and doubtful cards are in document order.
 */
function repeatsOf(cards, doc, rules, isBreak) {
  const views = cards.map((card, i) => viewOf(card, i));
  const model = scenarioModel(views, { controls: docControls(doc, rules), vocab: vocabOf(doc, rules) });
  const found = [true, false].map((kind) => repeatedCards(views.filter((view) => isBreak(view.card) === kind),
    model, (view) => view.rules));
  const inOrder = (rows, at) => rows.sort((a, b) => at(a) - at(b));
  return { groups: inOrder(found.flatMap((f) => f.groups), (g) => g.cards[0]),
    doubtful: inOrder(found.flatMap((f) => f.doubtful), (d) => d.card),
    repeats: found.reduce((n, f) => n + f.repeats, 0) };
}

const escapeRe = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s+')
  .replace(/&/g, '(?:&|and)');

/** The controls named in a text, longest first, each taken out once it is found ("Save & Close" is not a Save). */
export function controlsIn(text, controls) {
  const found = [];
  let rest = String(text ?? '');
  for (const name of [...controls].sort((a, b) => b.length - a.length)) {
    const re = new RegExp(`(?<![\\w&])${escapeRe(name)}(?![\\w&])`, 'i');
    if (re.test(rest)) {
      found.push(name);
      rest = rest.replace(new RegExp(re.source, 'gi'), ' ');
    }
  }
  return found;
}

/**
 * Scenarios that only check retired rules, one per control they press: the
 * absence of every retired behavior behind one Save is one test, and so is the
 * one behind Save & Close. The first scenario of a control keeps its place and
 * takes the others' rules. A scenario naming no control, or a live rule, stays.
 * Returns { scenarios, merged } where `merged` lists { into, from } scenario ids.
 */
export function mergeRemovedScenarios(scenarios, retiredIds, controls) {
  const byControl = new Map();
  const out = [];
  const merged = [];
  for (const scenario of scenarios) {
    const removal = scenario.rules.length > 0 && scenario.rules.every((id) => retiredIds.has(id));
    const [control] = removal ? controlsIn(`${scenario.action} ${scenario.population}`, controls) : [];
    if (!control) {
      out.push(scenario);
      continue;
    }
    const keeper = byControl.get(control);
    if (!keeper) {
      byControl.set(control, scenario);
      out.push(scenario);
      continue;
    }
    keeper.rules = [...new Set([...keeper.rules, ...scenario.rules])];
    // Each population stays named, so the one card still covers every record the checks were for.
    if (!String(keeper.population).includes(String(scenario.population))) {
      keeper.population = `${keeper.population}; ${scenario.population}`;
    }
    merged.push({ into: keeper.id, from: scenario.id });
  }
  for (const [control, keeper] of byControl) {
    if (!merged.some((m) => m.into === keeper.id)) continue;
    keeper.action = `check that ${control} no longer does what ${keeper.rules.join(', ')} used to require`;
    keeper.outcome = 'None of the removed behavior appears';
  }
  return { scenarios: out, merged };
}

// A first step that answers a message or resets, with no setup before it.
// The whole step is the answer, with at most "button" or "on the message" after it, so
// "Select Yes in the Active dropdown" and "Click the Reset Date field" are not answers.
const ANSWER = /^\s*(?:select|click|press|choose|hit|tap)\s+(?:the\s+)?["'“‘]?(?:ok|yes|no|cancel|reset)["'”’]?(?:\s+button)?(?:\s+(?:on|in)\s+the\s+(?:message|dialog|prompt|warning|alert|error)\b[^.]*)?\s*[.,;]?\s*$/i;
// A last result that raises a message the next card answers.
const RAISES = /\b(?:message|error|warning|prompt|dialog|alert)\b/i;

/**
 * Folds each card whose first step only answers a message (Ok, Yes, No,
 * Cancel) or resets into a card of the same kind that raises a message and
 * shares a rule with it. The answering steps follow the target's, the rules
 * join, and the target's Expected Result is the new last step's. Returns
 * { cards, folded } where `folded` lists { into, from } cards.
 */
export function foldFollowUps(cards, isBreak = flagged) {
  const folded = [];
  const gone = new Set();
  for (const card of cards) {
    const steps = list(card.steps);
    if (steps.length === 0 || !ANSWER.test(steps[0].description ?? '')) continue;
    const mine = new Set(list(card.rules));
    const target = cards.find((other) => other !== card && !gone.has(other)
      && isBreak(other) === isBreak(card)
      && list(other.steps).length > 0
      && RAISES.test(list(other.steps).at(-1).expected ?? '')
      && list(other.rules).some((id) => mine.has(id)));
    if (!target) continue;
    target.steps = [...list(target.steps), ...steps];
    target.rules = [...new Set([...list(target.rules), ...mine])];
    target.expected = steps.at(-1).expected ?? target.expected;
    gone.add(card);
    folded.push({ into: target, from: card });
  }
  return { cards: cards.filter((card) => !gone.has(card)), folded };
}

/**
 * Drops each card that repeats an earlier card of the same kind in the
 * document, by the same detector `compare` reports with. A card that joined
 * its group only by its rules, reading unlike the first, is kept: a reader
 * decides. Rules a dropped card cited that the kept card does not go onto the
 * kept card's last step.
 * Returns { cards, dropped, doubtful, left } with `left` the repeats still
 * standing (the doubtful ones).
 */
export function dropRepeats(cards, doc, rules, isBreak = flagged) {
  const found = repeatsOf(cards, doc, rules, isBreak);
  const doubtful = new Set(found.doubtful.map((d) => d.card));
  const dropped = [];
  const gone = new Set();
  for (const group of found.groups) {
    const [first, ...rest] = group.cards;
    for (const id of rest) {
      if (doubtful.has(id)) continue;
      const [keeper, repeat] = [cards[first], cards[id]];
      const extra = list(repeat.rules).filter((rule) => !list(keeper.rules).includes(rule));
      if (extra.length) {
        keeper.rules = [...list(keeper.rules), ...extra];
        const last = list(keeper.steps).at(-1);
        if (last) last.rules = [...new Set([...list(last.rules), ...extra])];
      }
      gone.add(repeat);
      dropped.push({ kept: keeper, dropped: repeat });
    }
  }
  return { cards: cards.filter((card) => !gone.has(card)), dropped,
    doubtful: found.doubtful, left: found.doubtful.length };
}

/** How many repeats the cards still hold, not counting the doubtful ones a reader decides. */
export function repeatsLeft(cards, doc, rules, isBreak = flagged) {
  const found = repeatsOf(cards, doc, rules, isBreak);
  return found.repeats - found.doubtful.length;
}
