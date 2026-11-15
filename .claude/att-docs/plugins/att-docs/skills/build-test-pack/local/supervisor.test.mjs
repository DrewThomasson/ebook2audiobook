// The answers file's schema and the heartbeat that says a supervisor is watching.
//
//   node --test plugins/att-docs/skills/build-test-pack/local/supervisor.test.mjs

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { after, test } from 'node:test';

import { answersFault, supervisorPresent, touchHeartbeat } from './supervisor.mjs';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'supervisor-'));
after(() => fs.rmSync(dir, { recursive: true, force: true }));

const config = { at: (file) => path.join(dir, file), queue: { file: 'queue.json' }, supervisor: { staleMinutes: 15 } };
const row = { id: 'Q1', answer: 'Desk renewals take the fix.', confidence: 'settled', citations: ['change description'] };

test('an answers file passes its schema with every question or only some of them', () => {
  assert.equal(answersFault({ answers: [row, { ...row, id: 'Q2', confidence: 'best reading', citations: [] }] },
    ['Q1', 'Q2']), null);
  assert.equal(answersFault({ answers: [] }, ['Q1']), null);
});

test('an answers file that breaks its schema is named by what it breaks', () => {
  for (const [value, reason] of [
    [[row], 'answers-shape'],
    [{ answers: [row], note: 'x' }, 'answers-shape'],
    [{ answers: [{ ...row, extra: 1 }] }, 'answers-shape'],
    [{ answers: [{ id: 'Q1', answer: 'x', confidence: 'settled' }] }, 'answers-shape'],
    [{ answers: [{ ...row, id: 'Q9' }] }, 'answers-unknown-id'],
    [{ answers: [row, row] }, 'answers-duplicate-id'],
    [{ answers: [{ ...row, answer: '  ' }] }, 'answers-blank'],
    [{ answers: [{ ...row, confidence: 'sure' }] }, 'answers-confidence'],
    [{ answers: [{ ...row, citations: 'change description' }] }, 'answers-citations'],
    [{ answers: [{ ...row, citations: [''] }] }, 'answers-citations'],
    // A settled answer rests on a source that states it.
    [{ answers: [{ ...row, citations: [] }] }, 'answers-citations'],
  ]) {
    assert.equal(answersFault(value, ['Q1']), reason, JSON.stringify(value));
  }
});

test('a supervisor is present while its heartbeat is newer than staleMinutes, and a sandbox counts its source job', () => {
  const now = Date.parse('2026-11-04T23:00:00Z');
  assert.equal(supervisorPresent(config, 'issue-1', now), false);
  touchHeartbeat(config, 'issue-1', new Date(now - 14 * 60000));
  assert.equal(supervisorPresent(config, 'issue-1', now), true);
  assert.equal(supervisorPresent(config, 'issue-1~try', now), true);
  assert.equal(supervisorPresent(config, 'issue-1', now + 2 * 60000), false);
  assert.equal(supervisorPresent(config, 'issue-2~try', now), false);
  fs.writeFileSync(path.join(dir, 'queue.json.watch-issue-3'), 'not a time\n');
  assert.equal(supervisorPresent(config, 'issue-3', now), false);
});
