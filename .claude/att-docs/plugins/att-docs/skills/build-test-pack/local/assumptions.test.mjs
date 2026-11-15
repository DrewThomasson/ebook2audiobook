// What the pack keeps on its Assumptions sheet: duplicates, claims that rules were
// missing, and pipeline vocabulary are dropped; phase 3 batches know they are parts.
//
//   node --test plugins/att-docs/skills/build-test-pack/local/assumptions.test.mjs

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { reconcile, tidyAssumptions, withoutPipelineTerms } from './phases.mjs';

const asm = (assumption) => ({ assumption, why: 'w', impact: 'i', clarification: 'c' });
const text = (pack) => pack.assumptions.map((a) => a.assumption);
const packWith = (assumptions, impact = 'Direct Change') => ({
  rules: [{ id: 'BR-1', name: 'Rule', module: 'MOD', summary: 's', impact }],
  assumptions, limitations: {},
});

test('assumptions with the same text once case and punctuation are ignored collapse to the first', () => {
  const pack = packWith([asm('The role list is final.'), asm('the role list is  final'), asm('Dates are UTC.')]);
  assert.equal(tidyAssumptions({}, pack), 1);
  assert.deepEqual(text(pack), ['The role list is final.', 'Dates are UTC.']);
});

test('an assumption that rules were not supplied goes once every rule is classified, and stays until then', () => {
  const claim = 'Business rules BR-9 to BR-12 were not supplied.';
  const done = packWith([asm(claim), asm('Dates are UTC.')]);
  assert.equal(tidyAssumptions({}, done), 1);
  assert.deepEqual(text(done), ['Dates are UTC.']);
  const open = packWith([asm(claim)], null);
  assert.equal(tidyAssumptions({}, open), 0);
  assert.equal(open.assumptions.length, 1);
});

test("the build supervisor's answers stay, and a model assumption with the same text is the duplicate that goes", () => {
  const answer = { ...asm('The role list is final.'), answeredBy: 'build supervisor' };
  const claim = { ...asm('Rules BR-9 to BR-12 were not supplied.'), answeredBy: 'build supervisor' };
  const pack = packWith([asm('the role list is final'), answer, claim]);
  assert.equal(tidyAssumptions({}, pack), 1);
  assert.deepEqual(pack.assumptions, [answer, claim]);
});

test('reconcile removes duplicates and leaves a note when no assumption is left', () => {
  const pack = packWith([asm('Business rules were not supplied.')]);
  reconcile({}, pack);
  assert.equal(pack.assumptions.length, 0);
  assert.match(pack.limitations.Assumptions, /No assumptions were needed/);
});

test('model assumptions that describe the pipeline are dropped, unless the change uses the word itself', () => {
  const given = [asm('Scenarios S1-S4 cover the role change.'), asm('The card was removed after one redesign.'),
    asm('Rules were not supplied for the batch.'), asm('The value supplied by the user is final.'),
    asm('Current Role is separate from the Verified Role dropdown.')];
  assert.deepEqual(withoutPipelineTerms({}, given).map((a) => a.assumption),
    ['The value supplied by the user is final.', 'Current Role is separate from the Verified Role dropdown.']);
  assert.equal(withoutPipelineTerms({ description: 'Redesign of the role screen.' },
    [asm('The redesign keeps the old labels.')]).length, 1);
});

test('claims that rules were not supplied or were omitted go, and claims about the source documents stay', () => {
  const pack = packWith([asm('BR-VSR-041 to 047 were not supplied.'), asm('The retired DOA/FATL rules were omitted.'),
    asm('The rules list is not provided in the spec.'), asm('Dates are UTC.')]);
  tidyAssumptions({}, pack);
  assert.deepEqual(text(pack), ['The rules list is not provided in the spec.', 'Dates are UTC.']);
});

test('the pipeline filter keeps domain wording, and reads the source documents for words they use', () => {
  const kept = withoutPipelineTerms({}, [asm('The account number was not supplied by the caller.')]);
  assert.equal(kept.length, 1);
  assert.equal(withoutPipelineTerms({}, [asm('Per BR-12. The account number was not supplied by the caller.'),
    asm('The rule threshold was supplied by the caller.')]).length, 2);
  const doc = { text: 'The nightly batch upload runs first.', rules: [] };
  assert.equal(withoutPipelineTerms({ documents: [doc] },
    [asm('The nightly batch upload runs before the role sync.')]).length, 1);
  assert.equal(withoutPipelineTerms({}, [asm('The nightly batch upload runs before the role sync.')]).length, 0);
});

test('reconcile leaves assumptions the code wrote alone; only the model-facing filter judges vocabulary', () => {
  const pack = packWith([asm('The card "Old" was removed for scenario S3: it covered no rule.')]);
  reconcile({}, pack);
  assert.equal(pack.assumptions.length, 1);
});
