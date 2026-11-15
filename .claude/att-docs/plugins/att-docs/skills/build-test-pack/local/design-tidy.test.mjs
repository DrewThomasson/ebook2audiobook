import test from 'node:test';
import assert from 'node:assert/strict';
import { controlsIn, docControls, dropRepeats, foldFollowUps, mergeRemovedScenarios, repeatsLeft } from './design-tidy.mjs';
import { fromWire } from './schemas.mjs';
import { impossibleSteps, stepRules, stepSchema } from './steps.mjs';

const DOC = { text: 'Selecting Save or Save & Close, the role is stored. Select Ok, the message closes. Select Reset, the saved value returns. '
  + 'Save is enabled only after the dropdown value changes. The sex abuse allegation blocks the role.' };
const RULES = [
  { id: 'R-30', summary: 'Selecting Save stores the role.' },
  { id: 'R-32', summary: 'The Save button is enabled only after the dropdown changes.' },
  { id: 'R-34', summary: 'Retired: selecting Save with a sex abuse allegation shows a warning.' },
  { id: 'R-35', summary: 'Retired: selecting Save & Close with a neglect allegation shows a warning.' },
  { id: 'R-36', summary: 'Retired: selecting Save with a fatality shows a warning.' },
];
const controls = docControls(DOC, RULES);

test('controlsIn finds the longest control first and counts it once', () => {
  assert.deepEqual(controlsIn('Select Save & Close, then Save', controls).sort(), ['Save', 'Save & Close']);
  assert.deepEqual(controlsIn('Select Save & Close', controls), ['Save & Close']);
});

test('absence checks of retired rules merge into one scenario per control', () => {
  const retired = new Set(['R-34', 'R-35', 'R-36']);
  const scenarios = [
    { id: 'S1', rules: ['R-34'], action: 'select Save', population: 'a role with a sex abuse allegation' },
    { id: 'S2', rules: ['R-36'], action: 'select Save', population: 'a role with a fatality' },
    { id: 'S3', rules: ['R-35'], action: 'select Save & Close', population: 'a role with a neglect allegation' },
    { id: 'S4', rules: ['R-30'], action: 'select Save', population: 'a role' },
    { id: 'S5', rules: ['R-34'], action: 'look at the screen', population: 'any role' },
  ];
  const { scenarios: out, merged } = mergeRemovedScenarios(scenarios, retired, controls);
  assert.deepEqual(out.map((s) => s.id), ['S1', 'S3', 'S4', 'S5']);
  assert.deepEqual(out[0].rules, ['R-34', 'R-36']);
  assert.deepEqual(merged, [{ into: 'S1', from: 'S2' }]);
  assert.match(out[0].action, /Save/);
});

const card = (title, first, expected, rules) => ({ title, rules, expected,
  steps: [{ description: first, expected: 'ok', rules }, { description: 'Check the result', expected, rules }] });

test('a card that only answers a message joins the card that raises it', () => {
  const error = card('Role blocked', 'Select the role', 'The error message Role blocked shows', ['R-34']);
  const ok = card('Ok closes it', 'Select Ok', 'The message closes', ['R-34']);
  const other = card('Other', 'Select Save', 'The role saves', ['R-30']);
  const { cards, folded } = foldFollowUps([error, ok, other]);
  assert.deepEqual(cards.map((c) => c.title), ['Role blocked', 'Other']);
  assert.equal(folded.length, 1);
  assert.equal(cards[0].steps.length, 4);
  assert.equal(cards[0].expected, 'The message closes');
});

test('a setup step that merely starts with Yes, No or Reset is not an answer to a message', () => {
  const error = card('Role blocked', 'Select the role', 'The error message Role blocked shows', ['R-34']);
  for (const first of ['Select Yes in the Active dropdown', 'Click the Reset Date field', 'Select No for the flag']) {
    const other = card('Dropdown', first, 'The value shows', ['R-34']);
    assert.equal(foldFollowUps([error, other]).cards.length, 2, first);
  }
  for (const first of ['Select Ok', 'Click the "Ok" button', 'Press Reset.', 'Select Yes on the message']) {
    const other = card('Answer', first, 'The message closes', ['R-34']);
    assert.equal(foldFollowUps([{ ...error }, other]).cards.length, 1, first);
  }
});

test('a card that answers a message with no card raising it shared by rule stays', () => {
  const ok = card('Ok closes it', 'Select Ok', 'The message closes', ['R-99']);
  const error = card('Role blocked', 'Select the role', 'The error message shows', ['R-34']);
  assert.equal(foldFollowUps([error, ok]).cards.length, 2);
});

test('a message is answered on a card of the same kind, BREAK IT or plain', () => {
  const raises = (title, breakIt) => ({ ...card(title, 'Select the role', 'The error message Role blocked shows', ['R-34']), breakIt });
  const ok = (breakIt) => ({ ...card('Ok closes it', 'Select Ok', 'The message closes', ['R-34']), breakIt });
  // The break card comes first and raises the same message, but the plain answer joins the plain card.
  const { cards, folded } = foldFollowUps([raises('Break it', true), raises('Plain', false), ok(false)]);
  assert.deepEqual(folded.map((f) => [f.into.title, f.from.title]), [['Plain', 'Ok closes it']]);
  assert.equal(cards[0].steps.length, 2);
  assert.equal(cards[1].steps.length, 4);
  // With only a card of the other kind raising it, the answer stays a card of its own.
  assert.equal(foldFollowUps([raises('Plain', false), ok(true)]).cards.length, 2);
  assert.equal(foldFollowUps([raises('Break it', true), ok(false)]).cards.length, 2);
  assert.equal(foldFollowUps([raises('Break it', true), ok(true)]).cards.length, 1);
});

const view = (title, focus, rules, mission = 'Check the sex abuse allegation blocks the role') => ({ title, mission, focus: [focus], rules,
  steps: [{ description: 'Select the role', expected: 'ok', rules }, { description: 'Select Save', expected: 'no save', rules }] });

test('a card that repeats another is dropped and its rules join the card that stays', () => {
  const cards = [
    view('Sex abuse allegation blocks the role', 'Select Save with a sex abuse allegation', ['R-34']),
    view('Sex abuse allegation blocks the role', 'Select Save with a sex abuse allegation', ['R-34', 'R-30']),
    view('Fatality warning', 'Select Save & Close with a fatality', ['R-36'], 'Check the fatality warning is gone'),
  ];
  const { cards: kept, dropped } = dropRepeats(cards, DOC, RULES);
  assert.equal(dropped.length, 1);
  assert.equal(kept.length, 2);
  assert.deepEqual(kept[0].rules, ['R-34', 'R-30']);
  assert.equal(repeatsLeft(kept, DOC, RULES), 0);
});

test('repeatsLeft counts a repeat that stands', () => {
  const cards = [view('Sex abuse allegation blocks the role', 'Select Save with a sex abuse allegation', ['R-34']),
    view('Sex abuse allegation blocks the role', 'Select Save with a sex abuse allegation', ['R-34'])];
  assert.equal(repeatsLeft(cards, DOC, RULES), 1);
});

test('a BREAK IT card is a repeat only of another BREAK IT card, and a plain card only of a plain one', () => {
  const alike = (breakIt) => ({ ...view('Sex abuse allegation blocks the role',
    'Select Save with a sex abuse allegation', ['R-34']), breakIt });
  for (const pair of [[alike(false), alike(true)], [alike(true), alike(false)]]) {
    assert.equal(dropRepeats(pair, DOC, RULES).dropped.length, 0);
    assert.equal(repeatsLeft(pair, DOC, RULES), 0);
  }
  const breaks = [alike(true), alike(true)];
  assert.equal(dropRepeats(breaks, DOC, RULES).cards.length, 1);
  // With the kinds interleaved, each later card is a repeat of the first of its own kind, in document order.
  const named = ['P0', 'B1', 'P2', 'B3'].map((name) => ({ ...alike(name[0] === 'B'), name }));
  const { cards: kept, dropped } = dropRepeats(named, DOC, RULES);
  assert.deepEqual(dropped.map((d) => [d.kept.name, d.dropped.name]), [['P0', 'P2'], ['B1', 'B3']]);
  assert.deepEqual(kept.map((c) => c.name), ['P0', 'B1']);
  assert.equal(repeatsLeft(kept, DOC, RULES), 0);
  // The caller's test of which cards go in the BREAK IT set decides the kinds.
  assert.equal(repeatsLeft([alike(false), alike(true)], DOC, RULES, () => false), 1);
});

test('stepRules adds a rule that governs a control the steps press, even when the card does not cite it', () => {
  const tc10 = { rules: ['R-30'], steps: [{ description: 'Leave the dropdown unchanged' }, { description: 'Select Save' }] };
  const shown = stepRules(tc10, RULES, controls).map((r) => r.id);
  assert.ok(shown.includes('R-30') && shown.includes('R-32'), shown.join());
});

test('stepSchema asks for one row per card with its steps, and impossibleSteps reads the no answers', () => {
  const schema = stepSchema(['C1', 'C2']);
  assert.deepEqual(schema.properties.cards.items.properties.card.enum, ['C1', 'C2']);
  assert.equal(schema.properties.cards.minItems, 2);
  const row = { card: 'C1', steps: [{ step: 1, possible: true, why: 'fine' }, { step: 2, possible: false, why: 'R-32 disables Save' }] };
  assert.deepEqual(impossibleSteps(row), [{ step: 2, why: 'R-32 disables Save' }]);
  assert.deepEqual(impossibleSteps(undefined), []);
});

test('a step row is asked for number first, then the decision, then the reason, however its properties are sorted', () => {
  const schema = stepSchema(['C1']);
  const row = schema.properties.cards.items.properties.steps.items;
  assert.deepEqual(Object.keys(row.properties).sort(), ['01_step', '02_possible', '03_why']);
  assert.deepEqual(row.required, ['01_step', '02_possible', '03_why']);
  // A reply as a server that sorts the properties sends it reads back under the plain names.
  const reply = { cards: [{ card: 'C1', steps: [{ '01_step': 1, '02_possible': true, '03_why': 'fine' },
    { '01_step': 2, '02_possible': false, '03_why': 'R-32 disables Save' }] }] };
  const read = fromWire(schema, reply);
  assert.deepEqual(read.cards[0].steps[0], { step: 1, possible: true, why: 'fine' });
  assert.deepEqual(impossibleSteps(read.cards[0]), [{ step: 2, why: 'R-32 disables Save' }]);
});

test('a step row with no decision is taken as possible, and one with no reason is still flagged', () => {
  const schema = stepSchema(['C1']);
  const reply = { cards: [{ card: 'C1', steps: [{ '01_step': 1, '03_why': 'R-32 disables Save' },
    { '01_step': 2, '02_possible': false }] }] };
  const read = fromWire(schema, reply);
  assert.deepEqual(read.cards[0].steps, [{ step: 1, why: 'R-32 disables Save' }, { step: 2, possible: false }]);
  assert.deepEqual(impossibleSteps(read.cards[0]), [{ step: 2, why: undefined }]);
});
