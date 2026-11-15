// The call recorder: the prompt hash, the file names, the sequence across a resumed run.
//
//   node --test plugins/att-docs/skills/build-test-pack/local/calls.test.mjs

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { after, test } from 'node:test';
import { callFileName, callRecorder, promptHash, schemaHash } from './calls.mjs';

// One scratch root for the whole file, removed when the last test ends.
const SCRATCH_ROOT = fs.mkdtempSync(path.join(os.tmpdir(), 'calls-test-'));
after(() => fs.rmSync(SCRATCH_ROOT, { recursive: true, force: true }));
const folder = () => path.join(fs.mkdtempSync(path.join(SCRATCH_ROOT, 'calls-')), 'work', 'calls');
const at = (iso) => new Date(iso);
const call = (extra = {}) => ({ step: 'phase1_rules', attempt: 1, thinking: false, maxTokens: 100,
  system: 'sys', user: 'usr', schema: { type: 'object' }, reply: { ok: true }, usage: { promptTokens: 9, outputTokens: 4, ms: 70 },
  startedAt: at('2026-11-04T10:00:00.000Z'), endedAt: at('2026-11-04T10:00:01.000Z'), ...extra });
const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));

test('the prompt hash is the same for the same text and differs when either part changes', () => {
  assert.equal(promptHash('sys', 'usr'), promptHash('sys', 'usr'));
  assert.match(promptHash('sys', 'usr'), /^sha256:[0-9a-f]{64}$/);
  assert.notEqual(promptHash('sys', 'usr'), promptHash('sys', 'usr '));
  assert.notEqual(promptHash('sys', 'usr'), promptHash('sys ', 'usr'));
  // A line moved from the system text to the user text is a changed prompt.
  assert.notEqual(promptHash('a\nb', 'c'), promptHash('a', 'b\nc'));
});

test('the schema hash changes with the schema and leaves the prompt hash alone', () => {
  const wide = { type: 'object', properties: { id: { enum: ['TC-1', 'TC-2'] } } };
  const narrow = { type: 'object', properties: { id: { enum: ['TC-1'] } } };
  assert.equal(schemaHash(wide), schemaHash(structuredClone(wide)));
  assert.notEqual(schemaHash(wide), schemaHash(narrow));
  const dir = folder();
  const [a, b] = [wide, narrow].map((schema) => read(callRecorder(dir).record(call({ schema }))));
  assert.equal(a.promptHash, b.promptHash);
  assert.notEqual(a.schemaHash, b.schemaHash);
});

test('a record holds the call as made and is named by sequence, step and attempt', () => {
  const dir = folder();
  const file = callRecorder(dir).record(call({ thinking: true, seed: 42 }));
  assert.equal(path.basename(file), '00001-phase1_rules-1.json');
  assert.equal(callFileName(12, 'phase9_walk', 2), '00012-phase9_walk-2.json');
  assert.deepEqual(read(file), {
    version: 1, seq: 1, step: 'phase1_rules', attempt: 1, thinking: true, maxTokens: 100, seed: 42,
    promptHash: promptHash('sys', 'usr'), schemaHash: schemaHash({ type: 'object' }), prompt: { system: 'sys', user: 'usr' },
    reply: { ok: true }, error: null, usage: { promptTokens: 9, outputTokens: 4 },
    startedAt: '2026-11-04T10:00:00.000Z', endedAt: '2026-11-04T10:00:01.000Z', ms: 70,
  });
});

test('a failed call keeps its error code and no reply, and takes its time from the clock when the model gave none', () => {
  const file = callRecorder(folder()).record(call({ reply: undefined, errorCode: 'network', usage: null }));
  const record = read(file);
  assert.equal(record.reply, null);
  // A call recorded with no seed, as a replay of a record that holds none is, notes null.
  assert.equal(record.seed, null);
  assert.deepEqual(record.error, { code: 'network' });
  assert.deepEqual(record.usage, { promptTokens: 0, outputTokens: 0 });
  assert.equal(record.ms, 1000);
});

test('the sequence counts up across calls and carries on from the folder after a resumed run', () => {
  const dir = folder();
  const first = callRecorder(dir);
  first.record(call());
  first.record(call({ step: 'phase2_gaps' }));
  const before = fs.readFileSync(path.join(dir, '00001-phase1_rules-1.json'), 'utf8');
  const resumed = callRecorder(dir);
  resumed.record(call({ step: 'phase3_cards', attempt: 2 }));
  assert.deepEqual(fs.readdirSync(dir).sort(),
    ['00001-phase1_rules-1.json', '00002-phase2_gaps-1.json', '00003-phase3_cards-2.json']);
  assert.equal(fs.readFileSync(path.join(dir, '00001-phase1_rules-1.json'), 'utf8'), before);
});

test('a record never replaces a file that is already there', () => {
  const dir = folder();
  const early = callRecorder(dir);
  const late = callRecorder(dir);
  early.record(call({ user: 'first' }));
  late.record(call({ user: 'second' }));
  // `early` counts 2 next, the number `late` just took for the same step and attempt.
  assert.throws(() => early.record(call({ user: 'third' })), { code: 'EEXIST' });
  assert.equal(read(path.join(dir, '00002-phase1_rules-1.json')).prompt.user, 'second');
});

test('a folder with files that are not call records still gives the next number', () => {
  const dir = folder();
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'notes.txt'), 'x');
  fs.writeFileSync(path.join(dir, '00007-phase1_rules-1.json'), '{}');
  const file = callRecorder(dir).record(call());
  assert.equal(path.basename(file), '00008-phase1_rules-1.json');
});

test('a record keeps the thinking and timing figures the server gave and the end of a cut call\'s thinking', () => {
  const usage = { promptTokens: 9, outputTokens: 90, ms: 70, reasoningTokens: 80, answerTokens: 10, promptMs: 12,
    genMs: 50, cachedTokens: 4 };
  const cut = read(callRecorder(folder()).record(call({ reply: undefined, errorCode: 'length', usage,
    reasoningTail: 'the last thought' })));
  assert.deepEqual(cut.usage, { promptTokens: 9, outputTokens: 90, reasoningTokens: 80, answerTokens: 10,
    promptMs: 12, genMs: 50, cachedTokens: 4 });
  assert.equal(cut.reasoningTail, 'the last thought');
  // A call that has none of them records none, so a record from before they existed reads the same.
  const plain = read(callRecorder(folder()).record(call({ reasoningTail: '' })));
  assert.deepEqual(plain.usage, { promptTokens: 9, outputTokens: 4 });
  assert.ok(!('reasoningTail' in plain));
});
