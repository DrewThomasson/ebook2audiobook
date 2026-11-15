import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import http from 'node:http';
import { spawn, spawnSync } from 'node:child_process';
import { ANSWER_ROOM, setupCheck, shortThinkingSteps, sudoersAllows, thinkingBudget } from './check.mjs';
import { loadConfig } from './config.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES = path.join(HERE, 'fixtures');
// The fixtures can sit in a worktree of this repository; the worktree check has its own tests.
process.env.BUILD_PACK_ALLOW_WORKTREE = '1';
const UNITS = path.join(HERE, 'systemd');
const SECRET = 'sentinel-token-7731';

/** A host that passes every check; `tweak` changes it before the config loads. */
function host(t, { pause = { units: ['llama*.service'], scope: 'system' }, release, env = {} } = {}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'build-pack-setup-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const home = path.join(dir, 'home');
  const installed = path.join(home, '.config', 'systemd', 'user');
  fs.mkdirSync(installed, { recursive: true });
  for (const unit of fs.readdirSync(UNITS)) fs.copyFileSync(path.join(UNITS, unit), path.join(installed, unit));
  const bin = path.join(dir, 'bin');
  fs.mkdirSync(bin);
  fs.writeFileSync(path.join(bin, 'unloader'), '#!/bin/sh\n', { mode: 0o755 });
  const script = path.join(dir, 'build-pack.mjs');
  const pipeline = path.join(dir, 'pipeline.json');
  fs.writeFileSync(script, '');
  const raw = JSON.parse(fs.readFileSync(path.join(FIXTURES, 'pipeline.json'), 'utf8'));
  Object.assign(raw, { repoRoot: FIXTURES, output: path.join(dir, 'out'),
    queue: { file: path.join(dir, 'queue.json'), sources: [] }, pause,
    release: release ?? { command: ['unloader'] } });
  fs.writeFileSync(pipeline, JSON.stringify(raw));
  const vars = { BUILD_PACK_SCRIPT: script, BUILD_PACK_CONFIG: pipeline, PATH: bin,
    TOKEN: SECRET, ...env };
  fs.mkdirSync(path.join(home, '.config', 'build-pack'));
  const text = Object.entries(vars).filter(([, v]) => v !== null).map(([k, v]) => `${k}=${v}`).join('\n');
  fs.writeFileSync(path.join(home, '.config', 'build-pack', 'env'), `${text}\n`);
  return { config: loadConfig(pipeline), home, dir, installed, envFile: path.join(home, '.config', 'build-pack', 'env') };
}

/** A fake systemctl and sudo keyed on the joined arguments; `overrides` replace answers. */
function fakeExec(overrides = {}) {
  return (command, args) => {
    const key = `${command} ${args.join(' ')}`;
    for (const [pattern, answer] of Object.entries(overrides)) {
      if (key.includes(pattern)) return answer;
    }
    if (key.includes('show -p LoadState')) return { status: 0, stdout: 'loaded\n' };
    if (key.includes('is-enabled')) return { status: 0, stdout: 'enabled\n' };
    if (key.includes('list-unit-files')) return { status: 0, stdout: 'llama-server.service enabled enabled\n' };
    if (command === 'sudo') {
      return { status: 0, stdout: 'User me may run the following commands on host:\n'
        + '    (root) NOPASSWD: /usr/bin/systemctl stop llama-server.service, /usr/bin/systemctl start llama-server.service\n' };
    }
    return { status: 1, stdout: '' };
  };
}

/**
 * A model server: the model list holds `ids`, and the saved model answers with `saved`
 * as its body, or with `savedStatus` when that is not 200.
 */
const modelReply = (ids, ok = true, status = 200, { saved = savedModel('-np 1 --reasoning-budget 5000'),
  savedStatus = 200 } = {}) => async (url) => (/\/models\/[^/]+$/.test(url)
  ? { ok: savedStatus === 200, status: savedStatus, json: async () => saved }
  : { ok, status, json: async () => ({ data: ids.map((id) => ({ id })) }) });

/** The saved model as the server reports it, with `args` as its `llamacpp_args`. */
function savedModel(args) {
  return { id: 'test-model', recipe_options: { ctx_size: 128000, ...(args === undefined ? {} : { llamacpp_args: args }) } };
}

/** A server whose model list is fine and whose saved model has `args`. */
const withArgs = (args) => modelReply(['test-model'], true, 200, { saved: savedModel(args) });

const budgetLines = (lines) => lines.filter((line) => line.startsWith('thinking-budget  '));

const run = (h, { exec = fakeExec(), fetchImpl = modelReply(['test-model']) } = {}) => setupCheck(h.config,
  { exec, fetchImpl, home: h.home, unitsDir: UNITS });

test('a ready host passes every check', async (t) => {
  const h = host(t);
  const { lines, ok } = await run(h);
  assert.equal(ok, true, lines.join('\n'));
  assert.ok(lines.every((line) => line.split('  ')[2] === 'pass'));
  assert.ok(lines.includes('unit  build-pack-now@.service  pass  installed'));
  assert.ok(lines.includes('timer  build-pack.timer  pass  enabled'));
  assert.ok(lines.includes('pause  llama-server.service  pass  found; sudoers allows stop and start'));
  assert.ok(lines.includes('model  test-model  pass  listed'));
  assert.ok(lines.includes('release  unloader  pass  found'));
  assert.ok(lines.includes('thinking-budget  test-model  pass  set 5000'));
});

test('a missing build-pack-now@.service fails and names where to copy it', async (t) => {
  const h = host(t);
  fs.rmSync(path.join(h.installed, 'build-pack-now@.service'));
  const { lines, ok } = await run(h);
  assert.equal(ok, false);
  assert.ok(lines.some((l) => l.startsWith('unit  build-pack-now@.service  fail  missing; copy local/systemd/build-pack-now@.service to ~/.config/systemd/user/')));
});

test('a unit that is not loaded, a disabled timer and an unreachable manager fail', async (t) => {
  const h = host(t);
  let result = await run(h, { exec: fakeExec({ 'LoadState --value build-pack.service': { status: 0, stdout: 'not-found\n' } }) });
  assert.ok(result.lines.some((l) => l.startsWith('unit  build-pack.service  fail  not-loaded')));
  result = await run(h, { exec: fakeExec({ 'is-enabled build-pack.timer': { status: 1, stdout: 'disabled\n' } }) });
  assert.ok(result.lines.some((l) => l.startsWith('timer  build-pack.timer  fail  not-enabled')));
  result = await run(h, { exec: fakeExec({ 'show -p LoadState': { status: 1, stdout: '' } }) });
  assert.equal(result.lines.filter((l) => l.includes('systemd-user-manager-unreachable')).length, 1);
  assert.equal(result.ok, false);
});

test('a missing env file or variable fails, and no env value is ever printed', async (t) => {
  let h = host(t);
  fs.rmSync(h.envFile);
  let result = await run(h);
  assert.ok(result.lines.includes('env  ~/.config/build-pack/env  fail  missing'));

  h = host(t, { env: { BUILD_PACK_SCRIPT: null, BUILD_PACK_CONFIG: path.join(os.tmpdir(), 'no-such-config.json') } });
  result = await run(h);
  assert.ok(result.lines.includes('env  BUILD_PACK_SCRIPT  fail  not-set'));
  assert.ok(result.lines.includes('env  BUILD_PACK_CONFIG  fail  file-not-found'));
  const text = result.lines.join('\n');
  assert.ok(!text.includes(SECRET));
  assert.ok(!text.includes('no-such-config'));
});

test('no value from the env file appears on a passing host', async (t) => {
  const h = host(t);
  const text = (await run(h)).lines.join('\n');
  for (const value of [SECRET, path.join(h.dir, 'build-pack.mjs'), path.join(h.dir, 'pipeline.json')]) {
    assert.ok(!text.includes(value));
  }
});

test('a pause pattern that matches nothing fails in each scope', async (t) => {
  for (const scope of ['system', 'user']) {
    const h = host(t, { pause: { units: ['gone*.service'], scope } });
    const { lines, ok } = await run(h, { exec: fakeExec({ 'list-unit-files': { status: 0, stdout: '' } }) });
    assert.equal(ok, false);
    assert.ok(lines.includes(`pause  gone*.service  fail  missing; scope ${scope}`));
  }
});

test('a system unit fails when sudoers refuses stop or start', async (t) => {
  const h = host(t);
  const listing = (rules) => ({ status: 0, stdout: `User me may run the following commands on host:\n${rules}\n` });
  let result = await run(h, { exec: fakeExec({ 'sudo -n -l': listing('    (root) NOPASSWD: /usr/bin/systemctl start llama-server.service') }) });
  assert.ok(result.lines.includes('pause  llama-server.service  fail  sudoers-refused stop'));
  result = await run(h, { exec: fakeExec({ 'sudo -n -l': listing('    (root) NOPASSWD: /usr/bin/systemctl stop llama-server.service') }) });
  assert.ok(result.lines.includes('pause  llama-server.service  fail  sudoers-refused start'));
  // A rule that still asks for a password, or a sudo that cannot list, does not pass.
  result = await run(h, { exec: fakeExec({ 'sudo -n -l': listing('    (ALL : ALL) ALL') }) });
  assert.ok(result.lines.includes('pause  llama-server.service  fail  sudoers-refused stop start'));
  result = await run(h, { exec: fakeExec({ 'sudo -n -l': { status: 1, stdout: '' } }) });
  assert.ok(result.lines.includes('pause  llama-server.service  fail  sudoers-refused stop start'));
});

test('sudoersAllows reads tags, negation, wildcards and the last matching rule', () => {
  const cmd = '/usr/bin/systemctl start a.service';
  const rule = (text) => `    (root) ${text}`;
  assert.equal(sudoersAllows(rule('NOPASSWD: /usr/bin/systemctl start a.service'), cmd), true);
  assert.equal(sudoersAllows(rule('/usr/bin/systemctl start a.service'), cmd), false);
  assert.equal(sudoersAllows(rule('NOPASSWD: /usr/bin/systemctl *'), cmd), true);
  assert.equal(sudoersAllows(rule('NOPASSWD: ALL'), cmd), true);
  assert.equal(sudoersAllows(rule('NOPASSWD: /usr/bin/other, PASSWD: /usr/bin/systemctl start a.service'), cmd), false);
  assert.equal(sudoersAllows(`${rule('NOPASSWD: ALL')}\n${rule('!/usr/bin/systemctl start a.service')}`, cmd), false);
  assert.equal(sudoersAllows(`${rule('NOPASSWD: /usr/bin/systemctl start a.service')}\n    (ALL : ALL) ALL`, cmd), false);
  assert.equal(sudoersAllows(rule('NOPASSWD: /usr/bin/systemctl start b.service'), cmd), false);
  assert.equal(sudoersAllows(rule('NOPASSWD: /usr/bin/systemctl'), cmd), true);
  assert.equal(sudoersAllows('    (postgres) NOPASSWD: ALL', cmd), false);
  assert.equal(sudoersAllows(`${rule('NOPASSWD: ALL')}\n    (postgres) ALL`, cmd), true);
  assert.equal(sudoersAllows('    (ALL : ALL) NOPASSWD: ALL', cmd), true);
  assert.equal(sudoersAllows(rule('CWD=* NOPASSWD: /usr/bin/systemctl start a.service'), cmd), true);
});

test('the env file needs a PATH line and a script that is a file', async (t) => {
  const h = host(t, { env: { PATH: null, BUILD_PACK_SCRIPT: os.tmpdir() } });
  const { lines, ok } = await run(h);
  assert.equal(ok, false);
  assert.ok(lines.includes('env  PATH  fail  not-set; systemd does not pass the login PATH'));
  assert.ok(lines.includes('env  BUILD_PACK_SCRIPT  fail  file-not-found'));
});

test('a model reply without a list, and a failed unit listing, fail', async (t) => {
  const h = host(t);
  let result = await run(h, { fetchImpl: async () => ({ ok: true, status: 200, json: async () => { throw new Error('bad'); } }) });
  assert.ok(result.lines.some((l) => l.endsWith('fail  no-model-list')));
  result = await run(h, { exec: fakeExec({ 'list-unit-files': { status: 1, stdout: '' } }) });
  assert.ok(result.lines.includes('pause  llama*.service  fail  missing; scope system'));
});

test('a user-scope pause unit needs no sudo', async (t) => {
  const h = host(t, { pause: { units: ['llama*.service'], scope: 'user' } });
  const calls = [];
  const exec = (command, args) => {
    calls.push(command);
    return fakeExec()(command, args);
  };
  const { ok } = await run(h, { exec });
  assert.equal(ok, true);
  assert.ok(!calls.includes('sudo'));
});

test('the model server must answer and list the configured model', async (t) => {
  const h = host(t);
  let result = await run(h, { fetchImpl: async () => { throw new Error('refused'); } });
  assert.ok(result.lines.some((l) => l.endsWith('fail  unreachable')));
  result = await run(h, { fetchImpl: modelReply([], false, 503) });
  assert.ok(result.lines.some((l) => l.endsWith('fail  answered-503')));
  result = await run(h, { fetchImpl: modelReply(['other-model']) });
  assert.ok(result.lines.includes('model  test-model  fail  not-listed'));
});

test('a model with no thinking budget saved warns and still passes', async (t) => {
  const h = host(t);
  for (const args of ['-np 1 -fa on', undefined, '', '--reasoning-budget 0', '--reasoning-budget -1',
    '--reasoning-budget-message "Write the answer now."']) {
    const { lines, ok } = await run(h, { fetchImpl: withArgs(args) });
    assert.equal(ok, true, lines.join('\n'));
    assert.deepEqual(budgetLines(lines), ['thinking-budget  test-model  warn  not-set'], String(args));
  }
});

test('a thinking budget with room under every step passes with no warning', async (t) => {
  const h = host(t);
  const { lines, ok } = await run(h, { fetchImpl: withArgs('-np 1 --reasoning-budget 5000'
    + ' --reasoning-budget-message "Thinking time is up. Write the answer now."') });
  assert.equal(ok, true, lines.join('\n'));
  assert.deepEqual(budgetLines(lines), ['thinking-budget  test-model  pass  set 5000']);
  // The smallest built-in output budget is 8192, so the largest budget with room is 5892.
  assert.equal(ANSWER_ROOM, 2300);
  assert.deepEqual(shortThinkingSteps(h.config, 8192 - ANSWER_ROOM), []);
  assert.equal(shortThinkingSteps(h.config, 8192 - ANSWER_ROOM + 1).length, 4);
});

test('a thinking budget that leaves a step too little room warns and names the step', async (t) => {
  const h = host(t);
  // An 8192 output budget leaves 2192 tokens above a thinking budget of 6000.
  let result = await run(h, { fetchImpl: withArgs('--reasoning-budget 6000') });
  assert.equal(result.ok, true, result.lines.join('\n'));
  assert.deepEqual(budgetLines(result.lines), [
    'thinking-budget  test-model  pass  set 6000',
    'thinking-budget  phase4.impact  warn  answer-room 2192; output budget 8192, needs 8300',
    'thinking-budget  phase9.confidence-overall  warn  answer-room 2192; output budget 8192, needs 8300',
    'thinking-budget  phase9.revalidation-resolution  warn  answer-room 2192; output budget 8192, needs 8300',
    'thinking-budget  phase9.revalidation-readiness  warn  answer-room 2192; output budget 8192, needs 8300',
  ]);
  // A step's own budget in the config comes first, then the phase's, as for a call.
  h.config.model.reasoningOutputByStep = { 'phase4.impact': 10240, 'phase1.rules': 6144 };
  h.config.model.reasoningOutputByPhase = { phase5: 8000 };
  result = await run(h, { fetchImpl: withArgs('--reasoning-budget 7000') });
  assert.equal(result.ok, true);
  assert.deepEqual(budgetLines(result.lines).slice(1).map((line) => line.split('  ')[1]), [
    'phase1.rules', 'phase5.objectives', 'phase9.confidence-overall', 'phase9.revalidation-resolution',
    'phase9.revalidation-readiness']);
  assert.ok(result.lines.includes(
    'thinking-budget  phase1.rules  warn  answer-room -856; output budget 6144, needs 9300'));
  // No budget passes model.reasoningOutput.
  h.config.model.reasoningOutputByStep = undefined;
  h.config.model.reasoningOutputByPhase = undefined;
  h.config.model.reasoningOutput = 8192;
  assert.equal(shortThinkingSteps(h.config, 7000).length, 11);
});

test('an unreachable server adds no thinking budget line, and an unread saved model warns', async (t) => {
  const h = host(t);
  let result = await run(h, { fetchImpl: async () => { throw new Error('refused'); } });
  assert.equal(result.ok, false);
  assert.equal(result.lines.filter((l) => l.startsWith('model  ')).length, 1);
  assert.deepEqual(budgetLines(result.lines), []);
  result = await run(h, { fetchImpl: modelReply(['other-model']) });
  assert.deepEqual(budgetLines(result.lines), []);
  const unread = [
    modelReply(['test-model'], true, 200, { savedStatus: 404 }),
    modelReply(['test-model'], true, 200, { saved: { id: 'test-model' } }),
    modelReply(['test-model'], true, 200, { saved: null }),
    async (url) => {
      if (/\/models\/[^/]+$/.test(url)) throw new Error('reset');
      return { ok: true, status: 200, json: async () => ({ data: [{ id: 'test-model' }] }) };
    },
  ];
  for (const fetchImpl of unread) {
    result = await run(h, { fetchImpl });
    assert.equal(result.ok, true, result.lines.join('\n'));
    assert.deepEqual(budgetLines(result.lines), ['thinking-budget  test-model  warn  not-read']);
  }
});

test('the saved model is read by its URL-encoded name', async (t) => {
  const h = host(t);
  h.config.model.name = 'user/My Model';
  const urls = [];
  const { lines } = await run(h, { fetchImpl: async (url) => {
    urls.push(url);
    return /\/models$/.test(url) ? { ok: true, status: 200, json: async () => ({ data: [{ id: 'user/My Model' }] }) }
      : { ok: true, status: 200, json: async () => savedModel('--reasoning-budget=5000') };
  } });
  assert.ok(urls[1].endsWith('/models/user%2FMy%20Model'), urls[1]);
  assert.ok(lines.includes('thinking-budget  user/My Model  pass  set 5000'));
});

test('thinkingBudget reads both flag forms and the last of a repeated flag', () => {
  assert.equal(thinkingBudget('-np 1 --reasoning-budget 6000'), 6000);
  assert.equal(thinkingBudget('--reasoning-budget=4096 -fa on'), 4096);
  assert.equal(thinkingBudget('--reasoning-budget 6000 --reasoning-budget 2000'), 2000);
  assert.equal(thinkingBudget('--reasoning-budget 6000 --reasoning-budget 0'), null);
  assert.equal(thinkingBudget('--reasoning-budget -1'), null);
  assert.equal(thinkingBudget('--reasoning-budget many'), null);
  assert.equal(thinkingBudget('--reasoning-budget-message "Stop."'), null);
  assert.equal(thinkingBudget('--no-reasoning-budget 5'), null);
  assert.equal(thinkingBudget('--reasoning-budget 6000 --reasoning-budget-message "Not --reasoning-budget 5 more."'), 6000);
  assert.equal(thinkingBudget(undefined), null);
});

/** Runs `check --config` against an HTTP server on this machine that answers with `reply(url)`. */
async function checkAgainst(t, h, reply) {
  const server = http.createServer((request, response) => {
    const { status = 200, body } = reply(request.url);
    response.writeHead(status, { 'content-type': 'application/json' });
    response.end(JSON.stringify(body));
  });
  await new Promise((resolve) => { server.listen(0, '127.0.0.1', resolve); });
  t.after(() => server.close());
  const pipeline = path.join(h.dir, 'pipeline.json');
  const raw = JSON.parse(fs.readFileSync(pipeline, 'utf8'));
  raw.model.endpoint = `http://127.0.0.1:${server.address().port}/api/v1`;
  fs.writeFileSync(pipeline, JSON.stringify(raw));
  const child = spawn(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'check', '--config', pipeline],
    { env: { ...process.env, HOME: h.home }, timeout: 60000 });
  let stdout = '';
  child.stdout.setEncoding('utf8').on('data', (chunk) => { stdout += chunk; });
  await new Promise((resolve) => { child.on('close', resolve); });
  return stdout.split('\n').filter((line) => /^(model|thinking-budget) {2}/.test(line));
}

test('check --config prints the thinking budget lines a server calls for', async (t) => {
  const h = host(t, { pause: { units: [], scope: 'system' } });
  const serving = (args) => (url) => (url === '/api/v1/models' ? { body: { data: [{ id: 'test-model' }] } }
    : url === '/api/v1/models/test-model' ? { body: savedModel(args) } : { status: 404, body: {} });
  assert.deepEqual(await checkAgainst(t, h, serving('-np 1')), [
    'model  test-model  pass  listed', 'thinking-budget  test-model  warn  not-set']);
  assert.deepEqual(await checkAgainst(t, h, serving('-np 1 --reasoning-budget 5000 --reasoning-budget-message "Answer now."')), [
    'model  test-model  pass  listed', 'thinking-budget  test-model  pass  set 5000']);
  const short = await checkAgainst(t, h, serving('--reasoning-budget 6000'));
  assert.equal(short.length, 6, short.join('\n'));
  assert.ok(short.includes('thinking-budget  phase4.impact  warn  answer-room 2192; output budget 8192, needs 8300'));
  const down = await checkAgainst(t, h, () => ({ status: 503, body: {} }));
  assert.equal(down.length, 1);
  assert.match(down[0], /^model {2}http:\/\/127\.0\.0\.1:\d+\/api\/v1 {2}fail {2}answered-503$/);
});

test('check --config against a closed port prints the unreachable line alone', async (t) => {
  const h = host(t, { pause: { units: [], scope: 'system' } });
  const server = http.createServer();
  await new Promise((resolve) => { server.listen(0, '127.0.0.1', resolve); });
  const { port } = server.address();
  await new Promise((resolve) => { server.close(resolve); });
  const pipeline = path.join(h.dir, 'pipeline.json');
  const raw = JSON.parse(fs.readFileSync(pipeline, 'utf8'));
  raw.model.endpoint = `http://127.0.0.1:${port}/api/v1`;
  fs.writeFileSync(pipeline, JSON.stringify(raw));
  const result = spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'check', '--config', pipeline],
    { encoding: 'utf8', env: { ...process.env, HOME: h.home } });
  const lines = result.stdout.split('\n').filter((line) => /^(model|thinking-budget) {2}/.test(line));
  assert.deepEqual(lines, [`model  http://127.0.0.1:${port}/api/v1  fail  unreachable`]);
});

test('the release command must be on the env file PATH, and an empty one is off', async (t) => {
  let h = host(t, { release: { command: ['no-such-unloader'] } });
  let result = await run(h);
  assert.ok(result.lines.includes('release  no-such-unloader  fail  not-found-on-PATH'));
  h = host(t, { release: { command: [] } });
  result = await run(h);
  assert.ok(result.lines.includes('release  off  pass  command-empty'));
  assert.equal(result.ok, true);
});

test('check without --issue runs the setup check and exits 1 on a bare host', (t) => {
  const h = host(t, { pause: { units: [], scope: 'system' } });
  const bare = fs.mkdtempSync(path.join(os.tmpdir(), 'build-pack-bare-'));
  t.after(() => fs.rmSync(bare, { recursive: true, force: true }));
  const result = spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'check', '--config',
    path.join(h.dir, 'pipeline.json')], { encoding: 'utf8', env: { ...process.env, HOME: bare } });
  assert.equal(result.status, 1);
  assert.match(result.stdout, /^unit {2}build-pack-now@\.service {2}fail {2}missing; copy local\/systemd\//m);
  assert.doesNotMatch(result.stdout, new RegExp(SECRET));
});

test('check with --issue still runs the input gate', (t) => {
  // No pause units, so the job check reads nothing from the machine running the test.
  const h = host(t, { pause: { units: [], scope: 'system' } });
  const result = spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'check', '--config',
    path.join(h.dir, 'pipeline.json'), '--issue', '999'], { encoding: 'utf8' });
  assert.match(result.stdout, /issue-number {2}present/);
  assert.doesNotMatch(result.stdout, /^unit /m);
});

test('a pause unit with no file is found among the loaded units', async (t) => {
  const h = host(t);
  const exec = fakeExec({ 'list-unit-files': { status: 0, stdout: '' },
    'list-units --all': { status: 0, stdout: 'llama-server.service loaded active running\n' } });
  const { lines, ok } = await run(h, { exec });
  assert.equal(ok, true, lines.join('\n'));
  assert.ok(lines.includes('pause  llama-server.service  pass  found; sudoers allows stop and start'));
});

test('check with --change but no --issue is refused, not run as the setup check', (t) => {
  const h = host(t);
  const result = spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'check', '--config',
    path.join(h.dir, 'pipeline.json'), '--change', '5'], { encoding: 'utf8' });
  assert.notEqual(result.status, 0);
  assert.doesNotMatch(result.stdout, /^unit /m);
});

test('a not-found unit among the loaded units does not count as found', async (t) => {
  const h = host(t);
  const exec = fakeExec({ 'list-unit-files': { status: 0, stdout: '' },
    'list-units --all': { status: 0, stdout: 'llama-server.service not-found inactive dead\n' } });
  const { lines, ok } = await run(h, { exec });
  assert.equal(ok, false);
  assert.ok(lines.includes('pause  llama*.service  fail  missing; scope system'));
});
