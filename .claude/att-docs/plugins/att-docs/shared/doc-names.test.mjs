// Checks how file and folder names are written under the documents root:
// no spaces, hyphens folded, no hyphen before the extension.
//
//   node --test plugins/att-docs/shared/doc-names.test.mjs

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { hyphenated, hyphenatedPath } from './doc-names.mjs';

test('hyphenated folds spaces and touching hyphens into one hyphen', () => {
  assert.equal(hyphenated('ACT 4.0 - Activity Entry.md'), 'ACT-4.0-Activity-Entry.md');
});

test('hyphenated collapses runs of spaces', () => {
  assert.equal(hyphenated('a   b.md'), 'a-b.md');
});

test('hyphenated drops a hyphen left in front of the extension', () => {
  assert.equal(hyphenated('Name -.md'), 'Name.md');
});

test('hyphenated trims surrounding whitespace', () => {
  assert.equal(hyphenated('  Name one  '), 'Name-one');
});

test('hyphenated leaves names without spaces unchanged', () => {
  assert.equal(hyphenated('already-hyphenated--name.md'), 'already-hyphenated--name.md');
});

test('hyphenatedPath rewrites each part and keeps the slashes', () => {
  assert.equal(hyphenatedPath('My Folder/Sub - Dir/File one.md'),
    'My-Folder/Sub-Dir/File-one.md');
});
