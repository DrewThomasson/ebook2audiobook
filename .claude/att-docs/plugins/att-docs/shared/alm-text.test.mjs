// Checks which characters ALM can store and how unstorable ones are reported
// or written as numeric entities.
//
//   node --test plugins/att-docs/shared/alm-text.test.mjs

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { almEntities, unstorableProblem } from './alm-text.mjs';

test('almEntities writes characters outside Windows-1252 as numeric entities', () => {
  assert.equal(almEntities('a \u{1F86A} b \u26AB'), 'a &#129130; b &#9899;');
});

test('almEntities leaves storable text unchanged', () => {
  const text = 'plain \u201Cquotes\u201D \u2014 caf\u00E9 \u20AC <b>x</b>';
  assert.equal(almEntities(text), text);
});

test('almEntities converts C1 controls, which Windows-1252 lacks', () => {
  assert.equal(almEntities('\u0085'), '&#133;');
});

test('unstorableProblem returns null for storable, empty, and missing values', () => {
  assert.equal(unstorableProblem('caf\u00E9 \u2019 ok'), null);
  assert.equal(unstorableProblem(''), null);
  assert.equal(unstorableProblem(undefined), null);
  assert.equal(unstorableProblem(null), null);
});

test('unstorableProblem names the first character ALM would turn into ?', () => {
  assert.equal(unstorableProblem('go \u{1F86A} now \u26AB'),
    'holds \u{1F86A}, which ALM stores as ?');
});
