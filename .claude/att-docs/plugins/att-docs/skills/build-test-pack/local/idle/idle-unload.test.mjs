// Cases for idle-unload.mjs. A fake fetch stands in for Lemonade and the model
// server, so nothing on the machine is read or changed.
// usage: node --test idle-unload.test.mjs

import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { main, parseMinutes, tick, unloadModel } from './idle-unload.mjs';

const MIN = 60000;
const BASE = 'http://127.0.0.1:13305/api/v1';
const BACKEND = 'http://127.0.0.1:8001/v1';
const NAME = 'Qwen3.8-27B-Q8_0';

const reply = (body, status = 200) => ({ ok: status >= 200 && status < 300, status, json: async () => body });
const loaded = (backend = BACKEND) => ({ all_models_loaded: [{ model_name: NAME, backend_url: backend }] });
const OTHER = 'Llama-3-8B';
const BACKEND2 = 'http://127.0.0.1:8002/v1';
const two = () => ({ all_models_loaded: [
  { model_name: NAME, backend_url: BACKEND },
  { model_name: OTHER, backend_url: BACKEND2 },
] });
const refused = (code = 'ECONNREFUSED') => new TypeError('fetch failed', { cause: Object.assign(new Error(code), { code }) });
const slot = (id_task, is_processing = false) => [{ id: 0, id_task, is_processing }];

// A fake server. `world` is read on every call, so a case can change it between runs.
function fake(world) {
  const calls = [];
  const fetchImpl = async (url, options = {}) => {
    calls.push({ url, options });
    if (url === `${BASE}/health`) return world.health ?? reply(loaded());
    if (url === `${BASE}/unload`) {
      const body = JSON.parse(options.body);
      return world.unloadFor?.[body.model_name] ?? world.unload ?? reply({ status: 'ok' });
    }
    if (url === 'http://127.0.0.1:8001/slots') {
      const slots = typeof world.slots === 'function' ? world.slots() : world.slots;
      return slots ?? reply(slot(5));
    }
    if (url === 'http://127.0.0.1:8002/slots') {
      const slots = typeof world.slots2 === 'function' ? world.slots2() : world.slots2;
      return slots ?? reply(slot(9));
    }
    throw new Error(`unexpected ${url}`);
  };
  return { fetchImpl, calls, posts: () => calls.filter((c) => c.options.method === 'POST') };
}

const run = (server, now, state, minutes = 15, apiKey = '') =>
  tick({ fetchImpl: server.fetchImpl, now, state, minutes, base: BASE, apiKey });

// main, with a real state directory
function setup(world, extraEnv = {}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'idle-unload-'));
  const server = fake(world);
  const lines = [];
  const errors = [];
  const go = (now) => main({ env: { STATE_DIRECTORY: dir, ...extraEnv }, fetchImpl: server.fetchImpl,
    now, log: (l) => lines.push(l), error: (l) => errors.push(l) });
  return { dir, server, lines, errors, go, state: () => path.join(dir, 'state.json') };
}

test('no model loaded clears the record and unloads nothing', async () => {
  const server = fake({ health: reply({ all_models_loaded: [] }) });
  const result = await run(server, 1000, { [NAME]: { signature: 'x', lastActive: 1 } });
  assert.deepEqual(result.state, {});
  assert.deepEqual(result.unload, []);
  assert.equal(server.calls.length, 1);
});

test('Lemonade not answering is a quiet run that keeps the record', async () => {
  const state = { [NAME]: { signature: 'x', lastActive: 1 } };
  const down = { fetchImpl: async () => { throw refused(); } };
  const result = await tick({ ...down, now: 1000, state, minutes: 15, base: BASE });
  assert.equal(result.state, state);
  assert.deepEqual(result.unload, []);
});

test('the first sighting stamps the time and never unloads', async () => {
  const server = fake({});
  const result = await run(server, 5000, null);
  assert.equal(result.state[NAME].lastActive, 5000);
  assert.deepEqual(result.unload, []);
});

test('a busy slot keeps refreshing the time', async () => {
  const server = fake({ slots: reply(slot(5, true)) });
  let state = (await run(server, 0, null)).state;
  const result = await run(server, 60 * MIN, state);
  assert.equal(result.state[NAME].lastActive, 60 * MIN);
  assert.deepEqual(result.unload, []);
});

test('a changed id_task stamps the time', async () => {
  const world = { slots: reply(slot(5)) };
  const server = fake(world);
  const state = (await run(server, 0, null)).state;
  world.slots = reply(slot(6));
  const result = await run(server, 20 * MIN, state);
  assert.equal(result.state[NAME].lastActive, 20 * MIN);
  assert.deepEqual(result.unload, []);
});

test('under the timeout nothing is unloaded and the time stays', async () => {
  const server = fake({});
  const state = (await run(server, 0, null)).state;
  const result = await run(server, 14 * MIN, state);
  assert.equal(result.state[NAME].lastActive, 0);
  assert.deepEqual(result.unload, []);
});

test('at the timeout the model is unloaded by name with a JSON body', async () => {
  const server = fake({});
  const state = (await run(server, 0, null)).state;
  const result = await run(server, 15 * MIN, state);
  assert.deepEqual(result.unload, [NAME]);
  await unloadModel({ fetchImpl: server.fetchImpl, base: BASE, name: NAME });
  const [post] = server.posts();
  assert.equal(post.url, `${BASE}/unload`);
  assert.equal(post.options.headers['content-type'], 'application/json');
  assert.deepEqual(JSON.parse(post.options.body), { model_name: NAME });
  assert.equal(post.options.redirect, 'error');
});

test('a slot that turns busy on the recheck skips the unload and stamps the time', async (t) => {
  const reads = [reply(slot(5)), reply(slot(5)), reply(slot(5, true))];
  const s = setup({ slots: () => reads.shift() });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  assert.equal(await s.go(0), 0);
  assert.equal(await s.go(15 * MIN), 0);
  assert.equal(s.server.posts().length, 0);
  assert.equal(JSON.parse(fs.readFileSync(s.state(), 'utf8'))[NAME].lastActive, 15 * MIN);
});

for (const [label, slots] of [
  ['a /slots error', 'throw'],
  ['a /slots 404', reply({}, 404)],
  ['an unknown /slots shape', reply({ slots: [] })],
]) {
  test(`${label} counts as busy and never unloads`, async () => {
    const world = { slots: slots === 'throw' ? () => { throw new Error('refused'); } : slots };
    const server = fake(world);
    let state = null;
    for (const t of [0, 20, 40, 60]) {
      const result = await run(server, t * MIN, state);
      assert.deepEqual(result.unload, []);
      assert.equal(result.state[NAME].lastActive, t * MIN);
      state = result.state;
    }
  });
}

test('a backend_url off this machine is refused before any request to it', async () => {
  const server = fake({ health: reply(loaded('http://example.com:8001/v1')) });
  await assert.rejects(run(server, 0, null), /loopback/);
  assert.equal(server.calls.length, 1);
  assert.equal(server.posts().length, 0);
});

test('every status read refuses redirects and has a timeout', async () => {
  const server = fake({});
  await run(server, 0, null);
  for (const { options } of server.calls) {
    assert.equal(options.redirect, 'error');
    assert.ok(options.signal instanceof AbortSignal);
  }
});

test('IDLE_MINUTES defaults to 15, takes an override, and rejects anything else', () => {
  assert.equal(parseMinutes(undefined), 15);
  assert.equal(parseMinutes(''), 15);
  assert.equal(parseMinutes('30'), 30);
  for (const bad of ['0', '-5', '1.5', 'abc', '15m', ' ']) {
    assert.throws(() => parseMinutes(bad), /IDLE_MINUTES/, bad);
  }
});

test('main walks a model from first sighting to unload and clears the record', async (t) => {
  const s = setup({});
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  assert.equal(await s.go(0), 0);
  assert.ok(fs.existsSync(s.state()));
  assert.equal(await s.go(14 * MIN), 0);
  assert.equal(s.server.posts().length, 0);
  assert.equal(await s.go(15 * MIN), 0);
  assert.equal(s.server.posts().length, 1);
  assert.deepEqual(s.lines, [`unloaded ${NAME} after 15 minutes idle`]);
  assert.equal(fs.existsSync(s.state()), false);
});

test('main honors IDLE_MINUTES', async (t) => {
  const s = setup({}, { IDLE_MINUTES: '5' });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  await s.go(0);
  await s.go(5 * MIN);
  assert.equal(s.server.posts().length, 1);
});

test('main with an invalid IDLE_MINUTES exits 2 and touches nothing', async (t) => {
  const s = setup({}, { IDLE_MINUTES: 'soon' });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  assert.equal(await s.go(0), 2);
  assert.equal(s.server.calls.length, 0);
  assert.match(s.errors[0], /IDLE_MINUTES/);
});

test('a failed unload exits 1 and keeps the record', async (t) => {
  const s = setup({ unload: reply({ error: 'no' }, 400) });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  await s.go(0);
  assert.equal(await s.go(15 * MIN), 1);
  const saved = JSON.parse(fs.readFileSync(s.state(), 'utf8'));
  assert.equal(saved[NAME].lastActive, 0);
  assert.equal(await s.go(16 * MIN), 1);
  assert.equal(s.server.posts().length, 2);
});

test('a backend_url off this machine makes main exit 1 with no unload', async (t) => {
  const s = setup({ health: reply(loaded('http://10.0.0.5:8001/v1')) });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  assert.equal(await s.go(0), 1);
  assert.equal(s.server.posts().length, 0);
});

// Per-model tracking
test('with one model busy and one idle, only the idle one unloads', async () => {
  const server = fake({ health: reply(two()), slots: reply(slot(5, true)), slots2: reply(slot(9)) });
  const state = (await run(server, 0, null)).state;
  const result = await run(server, 20 * MIN, state);
  assert.deepEqual(result.unload, [OTHER]);
  assert.equal(result.state[NAME].lastActive, 20 * MIN);
  assert.equal(result.state[OTHER].lastActive, 0);
});

test('a model that is no longer loaded drops out of the record', async () => {
  const world = { health: reply(two()) };
  const server = fake(world);
  const state = (await run(server, 0, null)).state;
  world.health = reply(loaded());
  const result = await run(server, MIN, state);
  assert.deepEqual(Object.keys(result.state), [NAME]);
});

test('both idle with one unload failing: the failed one keeps its entry and retries', async (t) => {
  const s = setup({ health: reply(two()), unloadFor: { [NAME]: reply({}, 500) } });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  await s.go(0);
  assert.equal(await s.go(15 * MIN), 1);
  const saved = JSON.parse(fs.readFileSync(s.state(), 'utf8'));
  assert.deepEqual(Object.keys(saved), [NAME]);
  assert.equal(saved[NAME].lastActive, 0);
  assert.deepEqual(s.lines, [`unloaded ${OTHER} after 15 minutes idle`]);
  assert.equal(s.server.posts().length, 2);
  assert.equal(await s.go(16 * MIN), 1);
  assert.equal(s.server.posts().length, 3);
  assert.equal(JSON.parse(s.server.posts()[2].options.body).model_name, NAME);
});

test('an entry without backend_url or with another recipe never blocks a llama.cpp model', async () => {
  const health = { all_models_loaded: [
    { model_name: 'embedder' },
    { model_name: 'whisper', backend_url: 'http://127.0.0.1:9000/v1', recipe: 'whispercpp' },
    { model_name: NAME, backend_url: BACKEND, recipe: 'llamacpp' },
  ] };
  const server = fake({ health: reply(health) });
  const state = (await run(server, 0, null)).state;
  assert.deepEqual(Object.keys(state), [NAME]);
  const result = await run(server, 15 * MIN, state);
  assert.deepEqual(result.unload, [NAME]);
  assert.equal(server.calls.some((c) => c.url.includes(':9000')), false);
});

test('a model whose slots are unreadable is busy for itself only', async () => {
  const server = fake({ health: reply(two()), slots: () => { throw new Error('refused'); } });
  const state = (await run(server, 0, null)).state;
  const result = await run(server, 20 * MIN, state);
  assert.deepEqual(result.unload, [OTHER]);
  assert.equal(result.state[NAME].lastActive, 20 * MIN);
});

// Lemonade errors
test('an HTTP status from /health throws, a rejected fetch is quiet', async (t) => {
  for (const status of [401, 404, 503]) {
    const server = fake({ health: reply({}, status) });
    await assert.rejects(run(server, 0, null), new RegExp(String(status)));
  }
  const s = setup({ health: reply({}, 401) });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  assert.equal(await s.go(0), 1);
  assert.match(s.errors[0], /401/);

  const q = setup({});
  t.after(() => fs.rmSync(q.dir, { recursive: true, force: true }));
  const down = () => main({ env: { STATE_DIRECTORY: q.dir }, fetchImpl: async () => { throw refused(); },
    now: 0, log: () => {}, error: (l) => q.errors.push(l) });
  fs.writeFileSync(q.state(), JSON.stringify({ [NAME]: { signature: 'x', lastActive: 1 } }));
  assert.equal(await down(), 0);
  assert.deepEqual(q.errors, []);
  assert.deepEqual(JSON.parse(fs.readFileSync(q.state(), 'utf8')), { [NAME]: { signature: 'x', lastActive: 1 } });
});

test('LEMONADE_API_KEY is sent on health and unload but not on slots', async (t) => {
  const s = setup({}, { LEMONADE_API_KEY: 'k3y' });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  await s.go(0);
  await s.go(15 * MIN);
  for (const { url, options } of s.server.calls) {
    const auth = options.headers?.authorization;
    if (url.endsWith('/slots')) assert.equal(auth, undefined, url);
    else assert.equal(auth, 'Bearer k3y', url);
  }
  assert.equal(s.server.posts().length, 1);
});

test('no Authorization header is sent without LEMONADE_API_KEY', async () => {
  const server = fake({});
  await run(server, 0, null);
  for (const { options } of server.calls) assert.equal(options.headers?.authorization, undefined);
});

// Settings and the record
test('main with STATE_DIRECTORY unset exits 2 and touches nothing', async () => {
  const server = fake({});
  const errors = [];
  const code = await main({ env: {}, fetchImpl: server.fetchImpl, now: 0, log: () => {}, error: (l) => errors.push(l) });
  assert.equal(code, 2);
  assert.equal(server.calls.length, 0);
  assert.match(errors[0], /STATE_DIRECTORY/);
});

test('a record that is not a map of model entries counts as none', async (t) => {
  const s = setup({});
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  fs.writeFileSync(s.state(), JSON.stringify({ signature: 'x', lastActive: 0 }));
  assert.equal(await s.go(60 * MIN), 0);
  assert.equal(s.server.posts().length, 0);
  assert.equal(JSON.parse(fs.readFileSync(s.state(), 'utf8'))[NAME].lastActive, 60 * MIN);
});

// Journal lines for models that are skipped or unreadable
test('skipped models and unreadable slots are named in the journal and the run exits 0', async (t) => {
  const health = { all_models_loaded: [
    { model_name: 'embedder' },
    { model_name: 'whisper', backend_url: 'http://127.0.0.1:9000/v1', recipe: 'whispercpp' },
    { model_name: NAME, backend_url: BACKEND },
    { model_name: OTHER, backend_url: BACKEND2 },
  ] };
  const s = setup({ health: reply(health), slots: reply({ slots: [] }), slots2: () => { throw new Error('refused'); } });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  assert.equal(await s.go(0), 0);
  assert.equal(s.lines.length, 4);
  assert.match(s.lines.find((l) => l.startsWith('embedder')), /no backend_url/);
  assert.match(s.lines.find((l) => l.startsWith('whisper')), /whispercpp.*not llamacpp/);
  assert.match(s.lines.find((l) => l.startsWith(NAME)), /not a list of slots/);
  assert.match(s.lines.find((l) => l.startsWith(OTHER)), /could not be read \(refused\)/);
  assert.deepEqual(s.errors, []);
});

// Rechecks happen right before each model's own unload
test('the second model is rechecked after the first unload and skipped when it turned busy', async (t) => {
  const reads2 = [reply(slot(9)), reply(slot(9)), reply(slot(9, true))];
  const s = setup({ health: reply(two()), slots2: () => reads2.shift() });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  assert.equal(await s.go(0), 0);
  assert.equal(await s.go(15 * MIN), 0);
  assert.deepEqual(s.server.posts().map((c) => JSON.parse(c.options.body).model_name), [NAME]);
  const urls = s.server.calls.map((c) => c.options.method === 'POST' ? 'POST' : c.url);
  const post = urls.indexOf('POST');
  assert.equal(urls.lastIndexOf('http://127.0.0.1:8002/slots') > post, true);
  const saved = JSON.parse(fs.readFileSync(s.state(), 'utf8'));
  assert.deepEqual(Object.keys(saved), [OTHER]);
  assert.equal(saved[OTHER].lastActive, 15 * MIN);
  assert.deepEqual(s.lines, [`unloaded ${NAME} after 15 minutes idle`,
    `${OTHER} was busy or changed on the last look; unload skipped`]);
});

// Names
test('a duplicate model name is judged and unloaded once', async () => {
  const health = { all_models_loaded: [
    { model_name: NAME, backend_url: BACKEND },
    { model_name: NAME, backend_url: BACKEND },
  ] };
  const server = fake({ health: reply(health) });
  const state = (await run(server, 0, null)).state;
  const result = await run(server, 15 * MIN, state);
  assert.deepEqual(result.unload, [NAME]);
  assert.equal(server.calls.filter((c) => c.url.endsWith(':8001/slots')).length, 2);
});

test('a model named __proto__ is tracked and unloaded like any other', async (t) => {
  const health = { all_models_loaded: [
    { model_name: '__proto__', backend_url: BACKEND },
    { model_name: NAME, backend_url: BACKEND2 },
  ] };
  const s = setup({ health: reply(health), slots2: reply(slot(9, true)) });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  assert.equal(await s.go(0), 0);
  assert.deepEqual(Object.keys(JSON.parse(fs.readFileSync(s.state(), 'utf8'))).sort(), ['__proto__', NAME].sort());
  assert.equal(await s.go(15 * MIN), 0);
  assert.deepEqual(s.server.posts().map((c) => JSON.parse(c.options.body).model_name), ['__proto__']);
  assert.deepEqual(s.lines, ['unloaded __proto__ after 15 minutes idle']);
  assert.equal(({}).signature, undefined);
  assert.equal(Object.keys(JSON.parse(fs.readFileSync(s.state(), 'utf8'))).join(), NAME);
});

test('a lastActive in the future counts as changed and resets to now', async () => {
  const server = fake({});
  const state = (await run(server, 100 * MIN, null)).state;
  const result = await run(server, 20 * MIN, state);
  assert.equal(result.state[NAME].lastActive, 20 * MIN);
  assert.deepEqual(result.unload, []);
});

// Errors from /health
test('only connection errors and timeouts on /health are quiet', async (t) => {
  const quiet = [refused(), refused('ECONNRESET'), refused('EHOSTUNREACH'), refused('ENOTFOUND'),
    refused('UND_ERR_SOCKET'), refused('EAI_AGAIN'), refused('ENETUNREACH'), new DOMException('timed out', 'TimeoutError'), new DOMException('aborted', 'AbortError')];
  for (const failure of quiet) {
    const q = setup({});
    t.after(() => fs.rmSync(q.dir, { recursive: true, force: true }));
    fs.writeFileSync(q.state(), JSON.stringify({ [NAME]: { signature: 'x', lastActive: 1 } }));
    const code = await main({ env: { STATE_DIRECTORY: q.dir }, fetchImpl: async () => { throw failure; },
      now: 0, log: () => {}, error: (l) => q.errors.push(l) });
    assert.equal(code, 0, failure.message);
    assert.deepEqual(q.errors, []);
    assert.equal(JSON.parse(fs.readFileSync(q.state(), 'utf8'))[NAME].lastActive, 1);
  }
  const loud = [new TypeError('Headers.append: invalid header value'), refused('CERT_HAS_EXPIRED'),
    new TypeError('redirect mode is set to error')];
  for (const failure of loud) {
    const q = setup({});
    t.after(() => fs.rmSync(q.dir, { recursive: true, force: true }));
    fs.writeFileSync(q.state(), JSON.stringify({ [NAME]: { signature: 'x', lastActive: 1 } }));
    const code = await main({ env: { STATE_DIRECTORY: q.dir }, fetchImpl: async () => { throw failure; },
      now: 0, log: () => {}, error: (l) => q.errors.push(l) });
    assert.equal(code, 1, failure.message);
    assert.equal(q.errors.length, 1);
    assert.equal(JSON.parse(fs.readFileSync(q.state(), 'utf8'))[NAME].lastActive, 1);
  }
});

test('a 200 /health with a body that is not JSON exits 1', async (t) => {
  const bad = { ok: true, status: 200, json: async () => JSON.parse('<html>') };
  const s = setup({ health: bad });
  t.after(() => fs.rmSync(s.dir, { recursive: true, force: true }));
  assert.equal(await s.go(0), 1);
  assert.equal(s.errors.length, 1);
  assert.equal(s.server.posts().length, 0);
});

// Started through a symbolic link
test('the script runs when started through a symbolic link', (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'idle-unload-link-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const link = path.join(dir, 'link.mjs');
  fs.symlinkSync(fileURLToPath(new URL('./idle-unload.mjs', import.meta.url)), link);
  const env = { PATH: process.env.PATH };
  const result = spawnSync(process.execPath, [link], { env, encoding: 'utf8' });
  assert.equal(result.status, 2);
  assert.match(result.stderr, /STATE_DIRECTORY/);
});
