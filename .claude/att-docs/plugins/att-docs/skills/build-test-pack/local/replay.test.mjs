// Tests for replaying recorded model calls: the order calls are answered in, what a changed
// prompt does, and how a recorded failure and its retry come back. The runs that replay a
// whole job are in build-pack.test.mjs, which holds the fixture job.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { after, test } from 'node:test';
import { callRecorder } from './calls.mjs';
import { ModelError, modelClient } from './model.mjs';
import { ask } from './phases.mjs';
import { promptDiff, readCalls, replayModel, replaySource, ReplayMiss } from './replay.mjs';
import { jobLogs, readStatusLog } from './status.mjs';
import { streamed } from './fixtures/streamed.mjs';

const SCRATCH_ROOT = fs.mkdtempSync(path.join(os.tmpdir(), 'replay-test-'));
after(() => fs.rmSync(SCRATCH_ROOT, { recursive: true, force: true }));
const scratch = (prefix) => fs.mkdtempSync(path.join(SCRATCH_ROOT, prefix));

const SCHEMA = { type: 'object', properties: { text: { type: 'string' } } };
const T0 = new Date('2026-01-01T00:00:00Z');

/** Records calls into a fresh folder, as a run does; each is `{ step, attempt, user, reply, errorCode }`. */
function recording(calls) {
  const dir = scratch('calls-');
  const recorder = callRecorder(dir);
  for (const call of calls) {
    recorder.record({ attempt: 1, thinking: false, maxTokens: 100, system: 'system text', schema: SCHEMA,
      startedAt: T0, endedAt: new Date(T0.getTime() + 5), usage: { promptTokens: 40, outputTokens: 4, ms: 5 },
      ...call, user: call.user ?? `user text for ${call.step}` });
  }
  return dir;
}

const request = (step, over = {}) => ({ system: 'system text', user: `user text for ${step}`, schema: SCHEMA,
  schemaName: step, attempt: 1, reasoning: false, maxTokens: 100, ...over });

test('calls of one step are answered in the order they were recorded, each attempt from its own', async () => {
  const dir = recording([
    { step: 'phase6_cards', reply: { text: 'first' } },
    { step: 'phase4_impact', reply: { text: 'other step' } },
    { step: 'phase6_cards', reply: { text: 'second' } },
    { step: 'phase6_cards', attempt: 2, reply: { text: 'retry' } },
  ]);
  const model = replayModel({ dir });
  assert.deepEqual((await model.json(request('phase6_cards'))).value, { text: 'first' });
  assert.deepEqual((await model.json(request('phase4_impact'))).value, { text: 'other step' });
  assert.deepEqual((await model.json(request('phase6_cards'))).value, { text: 'second' });
  assert.deepEqual((await model.json(request('phase6_cards', { attempt: 2 }))).value, { text: 'retry' });
  assert.deepEqual(model.report(), { served: 4, live: 0, misses: [] });
});

test('the recorded counts and timings come back with the reply', async () => {
  const model = replayModel({ dir: recording([{ step: 'phase6_cards', reply: { text: 'x' },
    usage: { promptTokens: 321, outputTokens: 12, ms: 987 } }]) });
  assert.deepEqual((await model.json(request('phase6_cards'))).usage, { promptTokens: 321, outputTokens: 12, ms: 987 });
});

test('recorded thinking and timing figures come back with the reply, and a cut call keeps the end of its thinking', async () => {
  const extras = { reasoningTokens: 80, answerTokens: 10, promptMs: 12, genMs: 50, cachedTokens: 4 };
  const model = replayModel({ dir: recording([
    { step: 'phase6_cards', reply: { text: 'x' }, usage: { promptTokens: 40, outputTokens: 4, ms: 5, ...extras } },
    { step: 'phase1_understanding', thinking: true, errorCode: 'length',
      usage: { promptTokens: 40, outputTokens: 90, ms: 5, ...extras }, reasoningTail: 'the last thought' },
  ]) });
  assert.deepEqual((await model.json(request('phase6_cards'))).usage,
    { promptTokens: 40, outputTokens: 4, ms: 5, ...extras });
  await assert.rejects(model.json(request('phase1_understanding', { reasoning: true })),
    (error) => error.code === 'length' && error.reasoningTail === 'the last thought'
      && error.usage.reasoningTokens === 80 && error.usage.promptMs === 12);
});

test('a call the recording lacks is a miss with its own code, and by default stops the run', async () => {
  const model = replayModel({ dir: recording([{ step: 'phase6_cards', reply: { text: 'x' } }]) });
  await model.json(request('phase6_cards'));
  // The step was recorded once; a second call finds nothing left.
  await assert.rejects(model.json(request('phase6_cards')),
    (error) => error instanceof ReplayMiss && !(error instanceof ModelError) && error.code === 'no-record'
      && error.message === 'replay: no recording for phase6_cards');
  await assert.rejects(model.json(request('phase8_repair')), { code: 'no-record', step: 'phase8_repair' });
  assert.deepEqual(model.report().misses.map((m) => [m.step, m.code]),
    [['phase6_cards', 'no-record'], ['phase8_repair', 'no-record']]);
});

test('a changed prompt is reported with the step and the lines that differ, and uses up its recording', async () => {
  const dir = recording([
    { step: 'phase6_cards', user: 'Task\nkeep one\nold line\nkeep two', reply: { text: 'first' } },
    { step: 'phase6_cards', user: 'unchanged second', reply: { text: 'second' } },
  ]);
  const logs = jobLogs(scratch('job-'), { echo: false });
  const model = replayModel({ dir });
  model.bind({ logs, job: 'issue-1', live: () => { throw new Error('no live model was asked for'); } });
  await assert.rejects(model.json(request('phase6_cards', { user: 'Task\nkeep one\nnew line\nkeep two' })),
    { name: 'ReplayMiss', code: 'prompt-changed', message: 'replay: prompt changed for phase6_cards' });
  // The miss took the first recording, so the next call is matched to the second.
  assert.deepEqual((await model.json(request('phase6_cards', { user: 'unchanged second' }))).value, { text: 'second' });
  assert.deepEqual(model.lines(), ['replay  served 1  live 0  missed 1',
    'replay: prompt changed for phase6_cards (2 lines differ; the diff is in detail.log)']);
  const status = readStatusLog(logs.statusPath);
  assert.deepEqual(status.map(({ at, ...fields }) => fields), [{ job: 'issue-1', phase: 'phase6',
    event: 'replay-miss', step: 'phase6_cards', reason: 'prompt-changed', changedLines: 2 }]);
  const detail = fs.readFileSync(logs.detailPath, 'utf8');
  assert.match(detail, /replay diff phase6_cards\nuser, from line 3:\n- old line\n\+ new line\n/);
  // The text of the prompt never reaches the status log.
  assert.ok(!/old line|new line/.test(fs.readFileSync(logs.statusPath, 'utf8')));
});

test('a changed reply schema is a miss of its own, with no diff', async () => {
  const model = replayModel({ dir: recording([{ step: 'phase6_cards', reply: { text: 'x' } }]) });
  await assert.rejects(model.json(request('phase6_cards', { schema: { type: 'object' } })),
    { code: 'schema-changed', message: 'replay: schema changed for phase6_cards' });
  assert.deepEqual(model.lines(), ['replay  served 0  live 0  missed 1', 'replay: schema changed for phase6_cards']);
});

test('a call asked with thinking set the other way is a miss, and a recorded cut does not answer it', async () => {
  const model = replayModel({ dir: recording([
    { step: 'phase1_understanding', thinking: true, errorCode: 'length' },
    { step: 'phase1_understanding', attempt: 2, reply: { text: 'answer' } },
  ]) });
  await assert.rejects(model.json(request('phase1_understanding')),
    { name: 'ReplayMiss', code: 'thinking-changed', message: 'replay: thinking changed for phase1_understanding' });
  // The miss takes the recorded retry with it.
  await assert.rejects(model.json(request('phase1_understanding', { attempt: 2 })), { code: 'no-record' });
});

test('with miss live, a call the recording cannot answer goes to the live model and the others do not', async () => {
  const dir = recording([
    { step: 'phase6_cards', reply: { text: 'recorded' } },
    { step: 'phase4_impact', reply: { text: 'recorded impact' } },
  ]);
  const asked = [];
  const live = { json: async (call) => { asked.push(call.schemaName); return { value: { text: 'live' }, usage: { promptTokens: 1, outputTokens: 1, ms: 1 } }; } };
  const model = replayModel({ dir, miss: 'live', live });
  assert.deepEqual((await model.json(request('phase6_cards', { user: 'a different prompt' }))).value, { text: 'live' });
  assert.deepEqual((await model.json(request('phase4_impact'))).value, { text: 'recorded impact' });
  assert.deepEqual(asked, ['phase6_cards']);
  assert.deepEqual(model.report(), { served: 1, live: 1, misses: [{ step: 'phase6_cards', code: 'prompt-changed', changed: 2 }] });
});

test('the live model is made only when a call first needs it', async () => {
  const dir = recording([{ step: 'phase6_cards', reply: { text: 'recorded' } }]);
  let made = 0;
  const model = replayModel({ dir, miss: 'live' });
  model.bind({ logs: null, job: 'j', live: () => { made += 1; return { json: async () => ({ value: {}, usage: {} }) }; } });
  await model.json(request('phase6_cards'));
  assert.equal(made, 0);
  await model.json(request('phase6_cards'));
  await model.json(request('phase6_cards'));
  assert.equal(made, 1);
});

test('miss live with no way to reach a live model fails the call', async () => {
  const model = replayModel({ dir: recording([{ step: 'phase6_cards', reply: {} }]), miss: 'live' });
  await assert.rejects(model.json(request('phase8_repair')), /has no model to ask/);
});

test('a recorded failure comes back as the same error, and the retry after it replays too', async () => {
  const dir = scratch('ask-');
  const fetched = (cut) => streamed({ finish: cut ? 'length' : 'stop', content: cut ? '{"a":' : '{"text":"answer"}',
    usage: { prompt_tokens: 30, completion_tokens: 7 } });
  const config = { model: { context: 100000, maxOutput: 4096, retryOutput: 2048, reasoningOutput: 8192 } };
  const context = (model, logs) => ({ config, calls: 0, tokens: { prompt: 0, output: 0 }, job: { id: 'j' }, logs, model });
  const live = modelClient({ endpoint: 'http://localhost:1/v1', name: 'm', seed: 7,
    fetchImpl: async (url, options) => fetched(JSON.parse(options.body).chat_template_kwargs.enable_thinking) });
  const call = (ctx) => ask(ctx, { phase: 'phase9', step: 'walk', reasoning: true, inputs: [['Doc', 'text']],
    schema: SCHEMA, task: 'do it' });

  const recorded = context({ ...live, countTokens: async () => 10 }, jobLogs(dir, { echo: false }));
  const first = await call(recorded);
  const calls = path.join(dir, 'work', 'calls');
  // The failed attempt notes the seed it was sent with, as the answered one does.
  assert.deepEqual(readCalls(calls).map((r) => [r.attempt, r.error?.code ?? null, r.seed]),
    [[1, 'length', 7], [2, null, 7]]);

  const replay = replayModel({ dir: calls });
  const again = scratch('again-');
  const replayed = context(replay, jobLogs(again, { echo: false }));
  assert.deepEqual(await call(replayed), first);
  assert.deepEqual(replayed.tokens, recorded.tokens);
  assert.equal(replayed.calls, 2);
  assert.deepEqual(replay.report(), { served: 2, live: 0, misses: [] });
  // The replay's records note the recorded seed, the one that made the replies it served.
  assert.deepEqual(readCalls(path.join(again, 'work', 'calls')).map((r) => r.seed), [7, 7]);
});

test('a record with no seed replays, its replay notes no seed, and a live miss notes the live seed', async () => {
  const config = { model: { context: 100000, maxOutput: 4096, retryOutput: 2048, reasoningOutput: 8192 } };
  const client = (seed, text) => ({ ...modelClient({ endpoint: 'http://localhost:1/v1', name: 'm', seed,
    fetchImpl: async () => streamed({ content: JSON.stringify({ text }) }) }), countTokens: async () => 10 });
  const context = (model, dir) => ({ config, calls: 0, tokens: { prompt: 0, output: 0 }, job: { id: 'j' },
    logs: jobLogs(dir, { echo: false }), model });
  const call = (ctx, task) => ask(ctx, { phase: 'phase9', step: 'walk', reasoning: false, inputs: [], schema: SCHEMA, task });

  const source = scratch('seedless-source-');
  await call(context(client(7, 'recorded'), source), 'first');
  await call(context(client(7, 'recorded'), source), 'second');
  const calls = path.join(source, 'work', 'calls');
  // A record can hold no seed; take it out of each to build such records.
  for (const name of fs.readdirSync(calls)) {
    const { seed, ...seedless } = JSON.parse(fs.readFileSync(path.join(calls, name), 'utf8'));
    fs.writeFileSync(path.join(calls, name), JSON.stringify(seedless));
  }

  const out = scratch('seedless-replay-');
  const ctx = context(replayModel({ dir: calls, miss: 'live', live: client(9, 'live') }), out);
  assert.deepEqual(await call(ctx, 'first'), { text: 'recorded' });
  assert.deepEqual(await call(ctx, 'a prompt the recording lacks'), { text: 'live' });
  assert.deepEqual(readCalls(path.join(out, 'work', 'calls')).map((r) => [r.reply.text, r.seed]),
    [['recorded', null], ['live', 9]]);
});

test('a stop for a changed prompt is not retried by the call that met it', async () => {
  const dir = scratch('ask-miss-');
  const config = { model: { context: 100000, maxOutput: 4096, retryOutput: 2048, reasoningOutput: 8192 } };
  const logs = jobLogs(dir, { echo: false });
  const recorded = callRecorder(path.join(dir, 'work', 'calls'));
  recorded.record({ step: 'phase9_walk', attempt: 1, thinking: false, maxTokens: 4096, system: 'x', user: 'y',
    schema: SCHEMA, reply: { text: 'a' }, usage: { promptTokens: 5, outputTokens: 1, ms: 1 }, startedAt: T0, endedAt: T0 });
  const model = replayModel({ dir: path.join(dir, 'work', 'calls') });
  const ctx = { config, calls: 0, tokens: { prompt: 0, output: 0 }, job: { id: 'j' }, logs, model };
  await assert.rejects(ask(ctx, { phase: 'phase9', step: 'walk', reasoning: false, inputs: [['Doc', 'other text']],
    schema: SCHEMA, task: 'do it' }), { code: 'prompt-changed' });
  assert.equal(ctx.calls, 1);
});

test('a prompt token count the server gave is used again, and an unknown prompt is estimated unless live counts it', async () => {
  const dir = recording([{ step: 'phase6_cards', system: 'S', user: 'U', reply: {}, usage: { promptTokens: 777, outputTokens: 1, ms: 1 } }]);
  const model = replayModel({ dir });
  assert.equal(await model.countTokens('S\nU'), 777);
  assert.equal(await model.countTokens('something else entirely'), Math.ceil('something else entirely'.length / 3));
  const live = replayModel({ dir, miss: 'live', live: { countTokens: async (text) => text.length } });
  assert.equal(await live.countTokens('S\nU'), 777);
  assert.equal(await live.countTokens('something else entirely'), 'something else entirely'.length);
});

test('a prompt too big for the window is too big on replay, as it was live, so the step splits the same way', async () => {
  const dir = recording([{ step: 'phase9_walk', reply: { text: 'a' } }]);
  const config = { model: { context: 4000, maxOutput: 1024, retryOutput: 1024, reasoningOutput: 1024 } };
  const ctx = { config, calls: 0, tokens: { prompt: 0, output: 0 }, job: { id: 'j' },
    logs: jobLogs(scratch('big-'), { echo: false }), model: replayModel({ dir }) };
  await assert.rejects(ask(ctx, { phase: 'phase9', step: 'walk', reasoning: false,
    inputs: [['Doc', 'word '.repeat(20000)]], schema: SCHEMA, task: 'do it' }), { code: 'too-big' });
  assert.deepEqual(ctx.model.report(), { served: 0, live: 0, misses: [] });
});

test('records ahead of a later one that holds the prompt are skipped, as a step from an earlier phase would be', async () => {
  const dir = recording([
    { step: 'phase9_confidence_overall', user: 'first phase prompt', reply: { text: 'early' } },
    { step: 'phase9_confidence_overall', user: 'second phase prompt', reply: { text: 'late' } },
  ]);
  const model = replayModel({ dir });
  assert.deepEqual((await model.json(request('phase9_confidence_overall', { user: 'second phase prompt' }))).value,
    { text: 'late' });
  assert.deepEqual(model.report(), { served: 1, live: 0, misses: [] });
  // The skipped record is gone, so a later call for it finds nothing.
  await assert.rejects(model.json(request('phase9_confidence_overall', { user: 'first phase prompt' })),
    { code: 'no-record' });
});

test('a miss that uses up a recorded failure takes its recorded retry with it', async () => {
  const dir = recording([
    { step: 'phase9_walk', user: 'old prompt', reply: null, errorCode: 'length' },
    { step: 'phase9_walk', attempt: 2, user: 'old prompt', reply: { text: 'retried' } },
    { step: 'phase9_walk', user: 'next prompt', reply: { text: 'next' } },
    { step: 'phase9_walk', attempt: 2, user: 'next prompt', reply: { text: 'next retried' } },
  ]);
  const model = replayModel({ dir, miss: 'live', live: { json: async () => ({ value: { text: 'live' }, usage: {} }) } });
  await model.json(request('phase9_walk', { user: 'changed prompt' }));
  // The retry the missed call recorded is gone, so no call can be answered by it.
  await model.json(request('phase9_walk', { user: 'old prompt', attempt: 2 }));
  assert.deepEqual(model.report().misses.map(({ code }) => code), ['prompt-changed', 'no-record']);
  assert.equal(model.report().served, 0);
});

test('a live retry of a missed call is no record, and takes no other call\'s recorded retry', async () => {
  const dir = recording([
    { step: 'phase9_walk', user: 'a prompt', reply: { text: 'a' } },
    { step: 'phase9_walk', user: 'b prompt', reply: null, errorCode: 'length' },
    { step: 'phase9_walk', attempt: 2, user: 'b prompt', reply: { text: 'b retried' } },
  ]);
  const model = replayModel({ dir, miss: 'live', live: { json: async () => ({ value: { text: 'live' }, usage: {} }) } });
  await model.json(request('phase9_walk', { user: 'a changed' }));
  await model.json(request('phase9_walk', { user: 'a changed', attempt: 2 }));
  await assert.rejects(model.json(request('phase9_walk', { user: 'b prompt' })), { code: 'length' });
  assert.deepEqual((await model.json(request('phase9_walk', { user: 'b prompt', attempt: 2 }))).value, { text: 'b retried' });
  assert.deepEqual(model.report().misses.map(({ code }) => code), ['prompt-changed', 'no-record']);
  assert.equal(model.report().served, 2);
});

test('a changed prompt is diffed against the call made nearest after the last one taken, not an earlier phase\'s', async () => {
  const dir = recording([
    { step: 'phase9_confidence_overall', user: 'early phase prompt', reply: { text: 'early' } },
    { step: 'phase9_walk', user: 'walk prompt', reply: { text: 'w' } },
    { step: 'phase9_confidence_overall', user: 'late phase prompt', reply: { text: 'late' } },
  ]);
  const diffs = [];
  const model = replayModel({ dir });
  model.bind({ logs: { status() {}, detail: (name, text) => diffs.push(text) }, job: 'j' });
  await model.json(request('phase9_walk', { user: 'walk prompt' }));
  await assert.rejects(model.json(request('phase9_confidence_overall', { user: 'late phase edited' })),
    { code: 'prompt-changed' });
  assert.match(diffs.join('\n'), /late phase prompt/);
  assert.doesNotMatch(diffs.join('\n'), /early phase prompt/);
});

test('a changed reply schema on a recorded failure takes its retry with it', async () => {
  const dir = recording([
    { step: 'phase9_walk', reply: null, errorCode: 'length' },
    { step: 'phase9_walk', attempt: 2, reply: { text: 'retried' } },
  ]);
  const model = replayModel({ dir, miss: 'live', live: { json: async () => ({ value: { text: 'live' }, usage: {} }) } });
  await model.json(request('phase9_walk', { schema: { type: 'object' } }));
  await model.json(request('phase9_walk', { attempt: 2 }));
  assert.deepEqual(model.report().misses.map(({ code }) => code), ['schema-changed', 'no-record']);
});

test('a prompt diff keeps the lines that differ, cuts each side at twenty and clips a long line', () => {
  const many = (prefix) => Array.from({ length: 25 }, (_, i) => `${prefix} ${i}`).join('\n');
  const { text, count } = promptDiff({ system: 'same', user: `head\n${many('old')}\ntail` },
    { system: 'same', user: `head\n${many('new')}\ntail` });
  assert.equal(count, 50);
  assert.match(text, /^user, from line 2:\n- old 0\n/);
  assert.match(text, /- old 19\n- \.\.\. 5 more lines\n\+ new 0\n/);
  assert.match(text, /\+ \.\.\. 5 more lines$/);
  assert.ok(!text.includes('same'));
  const clipped = promptDiff({ system: '', user: 'a' }, { system: '', user: 'b'.repeat(300) }).text;
  assert.ok(clipped.split('\n').every((line) => line.length < 260));
});

test('a source is a job or sandbox ID under the output folder, or a folder of calls', () => {
  const output = scratch('out-');
  const config = { output };
  const calls = path.join(output, 'issue-7', 'work', 'calls');
  fs.mkdirSync(calls, { recursive: true });
  fs.writeFileSync(path.join(calls, '00001-phase6_cards-1.json'), '{}');
  assert.equal(replaySource(config, 'issue-7'), calls);
  // A folder path takes the job folder, its work/calls, or the calls themselves.
  assert.equal(replaySource(config, path.join(output, 'issue-7')), calls);
  assert.equal(replaySource(config, calls), calls);
  assert.throws(() => replaySource(config, 'issue-8'), /issue-8 has no recorded calls/);
  assert.throws(() => replaySource(config, '../issue-7'), /holds no call records/);
  assert.throws(() => replaySource(config, 'a b'), /takes a job or sandbox ID/);
  assert.throws(() => replaySource(config, ''), /takes a job or sandbox ID/);
  const empty = path.join(output, 'empty');
  fs.mkdirSync(empty);
  assert.throws(() => replaySource(config, `${empty}/`), /holds no call records/);
});

test('a folder with a file that is not a call record is refused, naming the file', () => {
  const dir = recording([{ step: 'phase6_cards', reply: {} }]);
  fs.writeFileSync(path.join(dir, '00002-phase6_cards-1.json'), '{"version":1}');
  assert.throws(() => readCalls(dir), /00002-phase6_cards-1\.json is not a call record this version reads/);
  fs.writeFileSync(path.join(dir, '00002-phase6_cards-1.json'), 'not json');
  assert.throws(() => readCalls(dir), /00002-phase6_cards-1\.json is not a call record/);
});

test('miss takes fail or live', () => {
  assert.throws(() => replayModel({ dir: recording([{ step: 's', reply: {} }]), miss: 'skip' }), /fail or live/);
});
