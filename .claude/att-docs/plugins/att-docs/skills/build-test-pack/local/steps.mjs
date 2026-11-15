// The step check: whether each step of a card can be done under the rules the
// card cites, and under any rule that governs a control the steps press. Shared
// by the phase 6 design and the comparison's model pass.

import { controlsIn } from './design-tidy.mjs';
import { ordered } from './schemas.mjs';

const list = (value) => (Array.isArray(value) ? value
  : value === undefined || value === null || value === '' ? [] : [value]);

export const STEP_QUESTION = 'For each step of each card, say whether a tester can do it as written,'
  + ' with the screen in the state the earlier steps leave and the rules given in force. A step is not'
  + ' possible when a rule forbids it, or when the control it uses is disabled, hidden or absent under'
  + ' the rules, such as pressing Save when no value has changed and a rule enables Save only after a'
  + ' change. Name the rule in the reason, and say when two rules conflict.';

const MOST_RULES = 8;
const UNCHANGED = /\b(?:unchanged|without (?:changing|selecting|editing)|no change|leave[sd]? (?:it|the)|same (?:value|selection))\b/i;

/**
 * One reply row per card, by label; each lists its steps by number with
 * whether the step is possible and why. A step row is `ordered`, so the step's
 * number comes before the decision about it, whatever order a server hands the
 * properties to the model in.
 */
export function stepSchema(labels) {
  const row = ordered({ step: { type: 'integer' }, possible: { type: 'boolean' }, why: { type: 'string' } });
  const card = { type: 'object', additionalProperties: false, required: ['card', 'steps'],
    properties: { card: { enum: labels }, steps: { type: 'array', minItems: 1, items: row } } };
  return { type: 'object', additionalProperties: false, required: ['cards'],
    properties: { cards: { type: 'array', minItems: labels.length, maxItems: labels.length, items: card } } };
}

const ruleText = (rule) => `${rule.summary ?? ''} ${rule.description ?? ''}`;

/**
 * The rules to show for a card: those it cites, and any other rule that names
 * a control one of its steps presses, or, when a step leaves a value as it is,
 * any rule about a change. A card that cites no rule about Save is still held
 * to the rule that enables Save.
 */
export function stepRules(card, rules, controls) {
  const cited = new Set(list(card.rules));
  const text = list(card.steps).map((step) => step.description ?? '').join(' ');
  const pressed = controlsIn(text, controls);
  const unchanged = UNCHANGED.test(text);
  // A rule names a control as a whole word ("Save", not "saved"), as controlsIn reads it.
  const related = rules.filter((rule) => !cited.has(rule.id)).filter((rule) => {
    const t = ruleText(rule);
    return controlsIn(t, pressed).length > 0 || (unchanged && /\bchang/i.test(t));
  });
  return [...rules.filter((rule) => cited.has(rule.id)), ...related.slice(0, MOST_RULES)];
}

/** A card's steps in order, as the check reads them. */
export const stepsView = (card) => list(card.steps)
  .map((step, i) => `Step ${i + 1}: ${step.description} => ${step.expected}`).join('\n');

/** The steps a reply marks not possible: [{ step, why }]. */
export const impossibleSteps = (row) => list(row?.steps).filter((s) => s.possible === false)
  .map((s) => ({ step: s.step, why: s.why }));
