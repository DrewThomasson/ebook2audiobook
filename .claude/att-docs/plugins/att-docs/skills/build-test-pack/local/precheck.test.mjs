// The queue pre-check: `queue check` runs the input gates on every waiting row
// before the nightly run and writes content-free lines to one status file.
//
//   node --test plugins/att-docs/skills/build-test-pack/local/precheck.test.mjs

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { addJob, localStamp, precheckPath, precheckQueue, readQueue } from './build-pack.mjs';
import { loadConfig } from './config.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES = path.join(HERE, 'fixtures');
// The fixtures can sit in a worktree of this repository; the worktree check has its own tests.
process.env.BUILD_PACK_ALLOW_WORKTREE = '1';
const UC01 = 'docs/LIB/UC01-Card-Renewal.md';

/** A config over the fixtures whose output and queue land in a temp folder the test removes. */
function fixtureConfig(t, sources = []) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'build-pack-precheck-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const raw = JSON.parse(fs.readFileSync(path.join(FIXTURES, 'pipeline.json'), 'utf8'));
  Object.assign(raw, { repoRoot: FIXTURES, output: path.join(dir, 'out'),
    queue: { file: path.join(dir, 'queue.json'),
      sources: sources.map((s) => (s.type === 'folder' ? { ...s, path: path.join(dir, s.path) } : s)) } });
  const file = path.join(dir, 'pipeline.json');
  fs.writeFileSync(file, JSON.stringify(raw));
  return { config: loadConfig(file), file, dir };
}

/** Marks the newest row for `id` with `fields`, as a run would. */
function setRow(config, id, fields) {
  const queue = readQueue(config);
  Object.assign(queue.jobs.findLast((row) => row.id === id), fields);
  fs.writeFileSync(config.at(config.queue.file), JSON.stringify(queue));
}

const lockFile = (config) => `${config.at(config.queue.file)}.lock`;

const queueCheck = (file) => spawnSync(process.execPath,
  [path.join(HERE, 'build-pack.mjs'), 'queue', 'check', '--config', file], { encoding: 'utf8' });

test('the pre-check gates every waiting issue row, refuses suites and checks stale rows, changing nothing', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '501', change: '7001', docs: [UC01] });
  addJob(config, { issue: '999' });
  addJob(config, { issue: '501' });
  addJob(config, { suite: 'LIB' });
  addJob(config, { issue: '77' });
  setRow(config, 'issue-77', { status: 'running', started: new Date().toISOString() });
  addJob(config, { issue: '78' });
  setRow(config, 'issue-78', { status: 'passed' });

  const before = fs.readFileSync(config.at(config.queue.file), 'utf8');
  const { lines, code } = await precheckQueue(config);
  assert.equal(code, 1, 'issue 999 has no description');
  assert.equal(lines[0], 'sources  would queue 0 job(s), 0 already known, 0 unreadable line(s)');
  assert.deepEqual(lines.filter((line) => line.startsWith('issue-501-change-7001 ')), [
    'issue-501-change-7001  issue-number  present  issue',
    'issue-501-change-7001  description  present  found',
    'issue-501-change-7001  document-1  present  rules-ok']);
  assert.ok(lines.includes('issue-999  description  missing  no-description'));
  assert.ok(lines.includes('issue-501  rules  unchecked  name-documents-with-doc'));
  assert.ok(lines.includes('suite-LIB  suite  refused'));
  // The nightly run settles a stale row and runs it again, so it is checked too.
  assert.ok(lines.includes('issue-77  running  stale-row'));
  assert.ok(lines.includes('issue-77  issue-number  present  issue'));
  assert.ok(!lines.some((line) => line.startsWith('issue-78 ')), 'a finished row is not checked');
  // The queue is left as it was, and never locked.
  assert.equal(fs.readFileSync(config.at(config.queue.file), 'utf8'), before);
  assert.ok(!fs.existsSync(lockFile(config)));
});

test('the exit code is 3 when rules went unchecked and nothing is missing, 0 when all is present', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '501', change: '7001', docs: [UC01] });
  assert.equal((await precheckQueue(config)).code, 0);
  addJob(config, { issue: '501' });
  assert.equal((await precheckQueue(config)).code, 3);
});

test('a held queue is waited for, and the check is skipped when it stays held', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '501', change: '7001', docs: [UC01] });
  // This process is alive, so it stands in for a run holding the queue.
  fs.writeFileSync(lockFile(config), String(process.pid));
  let now = 0;
  const clock = () => new Date(now);
  let polls = 0;
  const released = await precheckQueue(config, { clock, waitMs: 60000, pollMs: 30000,
    sleep: async (ms) => {
      now += ms;
      polls += 1;
      if (polls === 1) fs.rmSync(lockFile(config));
    } });
  assert.equal(polls, 1);
  assert.equal(released.code, 0);

  fs.writeFileSync(lockFile(config), String(process.pid));
  now = 0;
  polls = 0;
  const held = await precheckQueue(config, { clock, waitMs: 60000, pollMs: 30000,
    sleep: async (ms) => { now += ms; polls += 1; } });
  assert.equal(polls, 2);
  assert.deepEqual([held.lines, held.code], [['queue  held  precheck-skipped'], 1]);
  fs.rmSync(lockFile(config));
});

test('queue check writes a local time stamp and its lines to the status file, content-free', (t) => {
  const { config, file } = fixtureConfig(t);
  addJob(config, { issue: '501', change: '7001', docs: [UC01] });
  const result = queueCheck(file);
  assert.equal(result.status, 0, result.stderr);
  const written = fs.readFileSync(precheckPath(config), 'utf8').trim().split('\n');
  assert.match(written[0], /^checked \d{4}-\d\d-\d\d \d\d:\d\d$/);
  assert.deepEqual(written.slice(1), result.stdout.trim().split('\n'));
  assert.ok(written.includes('issue-501-change-7001  document-1  present  rules-ok'));
  for (const word of ['Patron', 'Renewal', 'BR-LIB', 'renew']) {
    assert.ok(!written.join('\n').includes(word), `status file carries "${word}"`);
  }
});

test('a stale row on its last try is reported as dropped and not checked', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '999' });
  setRow(config, 'issue-999', { status: 'running',
    failures: [{ phase: 'intake', reason: 'gate:rules-not-extracted' }] });
  const { lines, code } = await precheckQueue(config);
  assert.ok(lines.includes('issue-999  running  stale-row-dropped'), lines.join('\n'));
  assert.ok(!lines.some((line) => line.startsWith('issue-999  description')));
  assert.equal(code, 0);
});

test('the result carries when the queue was read, after any wait', async (t) => {
  const { config } = fixtureConfig(t);
  fs.writeFileSync(lockFile(config), String(process.pid));
  let now = 0;
  const { at } = await precheckQueue(config, { clock: () => new Date(now), waitMs: 60000, pollMs: 30000,
    sleep: async (ms) => { now += ms; fs.rmSync(lockFile(config), { force: true }); } });
  assert.equal(at.getTime(), 30000);
});

test('the stamp reads the local clock', () => {
  assert.equal(localStamp(new Date(2026, 9, 30, 18, 5)), '2026-10-30 18:05');
});

test('a job the sources would queue is checked without queueing it, so a fixed line counts tonight', async (t) => {
  const { config, dir } = fixtureConfig(t, [{ type: 'folder', path: 'lists' }, { type: 'folder', path: 'gone' }]);
  fs.mkdirSync(path.join(dir, 'lists'));
  const list = path.join(dir, 'lists', 'tonight.txt');
  fs.writeFileSync(list, '501 7001\n');
  const first = await precheckQueue(config);
  assert.equal(first.lines[0],
    'sources  would queue 1 job(s), 0 already known, 0 unreadable line(s), source problems: folder:source-missing');
  assert.ok(first.lines.includes('issue-501-change-7001  rules  unchecked  name-documents-with-doc'));
  assert.deepEqual(readQueue(config).jobs, []);

  // The line is fixed after the check; the nightly fill reads the new line.
  fs.writeFileSync(list, `--issue 501 --change 7001 --doc ${UC01}\n`);
  const second = await precheckQueue(config);
  assert.equal(second.code, 1, 'the missing source folder still counts');
  assert.ok(second.lines.includes('issue-501-change-7001  document-1  present  rules-ok'));
});

test('a run that takes the queue mid-check stops it', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '501', change: '7001', docs: [UC01] });
  addJob(config, { issue: '502' });
  // The lock appears while the first row's document is read, before the second row.
  const original = fs.readFileSync;
  let checked = 0;
  t.mock.method(fs, 'readFileSync', (file, ...rest) => {
    if (String(file).endsWith('UC01-Card-Renewal.md') && ++checked === 1) {
      fs.writeFileSync(lockFile(config), String(process.pid));
    }
    return original.call(fs, file, ...rest);
  });
  const { lines, code } = await precheckQueue(config);
  fs.rmSync(lockFile(config), { force: true });
  assert.equal(code, 1);
  assert.equal(lines.at(-1), 'queue  held  precheck-stopped');
  assert.ok(!lines.some((line) => line.startsWith('issue-502 ')));
});

test('a row whose check throws is reported by error name and fails the pre-check', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '501' });
  setRow(config, 'issue-501', { docs: [42] });
  const { lines, code } = await precheckQueue(config);
  assert.equal(code, 1);
  assert.ok(lines.includes('issue-501  check  failed  TypeError'), lines.join('\n'));
});

test('a queue file that does not parse still rewrites the status file', (t) => {
  const { config, file } = fixtureConfig(t);
  fs.writeFileSync(config.at(config.queue.file), '{ not json');
  const result = queueCheck(file);
  assert.equal(result.status, 1);
  assert.equal(result.stdout.trim(), 'precheck  failed  SyntaxError');
  assert.equal(fs.readFileSync(precheckPath(config), 'utf8').trim().split('\n')[1],
    'precheck  failed  SyntaxError');
});

const UC09 = 'docs/OTHER/UC09-Unmapped.md';

/** Writes the checkpoint a job saved after `phase`, holding `documents`, as a run would. */
function writeCheckpoint(config, id, phase, documents) {
  const dir = path.join(config.output, id, 'work');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'checkpoint.json'), JSON.stringify({ phase, state: { documents } }));
}

const included = (number, file, ruleCode) => ({ number, file, inclusion: 'Included', ruleCode });

test('a resumed row whose checkpoint names a document with no usable rules is reported missing with its code', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '501', change: '7001', docs: [UC01], resume: true });
  writeCheckpoint(config, 'issue-501-change-7001', 'phase1', [included(1, UC09)]);
  const { lines, code } = await precheckQueue(config);
  assert.equal(code, 1);
  assert.ok(lines.includes('issue-501-change-7001  checkpoint  present  phase1'));
  assert.ok(lines.includes('issue-501-change-7001  document-1  missing  rules-not-extracted'));
  assert.ok(!lines.some((line) => line.includes('rules-ok')), 'the --doc path is not what the run reads');
  assert.ok(!lines.join('\n').includes('Unmapped'), 'no document name reaches the lines');
});

test('a checkpoint holding an absolute worktree path is checked against the root the check has', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '501', change: '7001', resume: true });
  writeCheckpoint(config, 'issue-501-change-7001', 'phase1', [
    included(1, `/elsewhere/.claude/worktrees/w1/${UC09}`),
    included(2, `/elsewhere/.claude/worktrees/w1/${UC01}`),
    included(3, 'docs/LIB/Not-There.md')]);
  const { lines } = await precheckQueue(config);
  assert.ok(lines.includes('issue-501-change-7001  document-1  missing  rules-not-extracted'));
  assert.ok(lines.includes('issue-501-change-7001  document-2  present  rules-ok'));
  assert.ok(lines.includes('issue-501-change-7001  document-3  missing  document-file'));
});

test('a held document whose export now fails is present, as Phase 2 keeps its rules', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '501', change: '7001', resume: true });
  writeCheckpoint(config, 'issue-501-change-7001', 'phase1', [included(1, UC09, 'rules-ok')]);
  const { lines, code } = await precheckQueue(config);
  assert.ok(lines.includes('issue-501-change-7001  document-1  present  rules-not-extracted'));
  assert.equal(code, 0);
});

test('a context-only document and a checkpoint past Phase 2 run no export', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '501', change: '7001', resume: true });
  writeCheckpoint(config, 'issue-501-change-7001', 'phase1',
    [{ ...included(1, UC09), inclusion: 'Supporting Context Only' }]);
  let { lines } = await precheckQueue(config);
  assert.ok(lines.includes('issue-501-change-7001  document-1  present  context-only'));
  writeCheckpoint(config, 'issue-501-change-7001', 'phase3', [included(1, UC09)]);
  ({ lines } = await precheckQueue(config));
  assert.ok(lines.includes('issue-501-change-7001  documents  present  past-phase2'));
});

test('a resumed row with no checkpoint is checked from its --doc as a fresh job is', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '501', change: '7001', docs: [UC01], resume: true });
  const { lines, code } = await precheckQueue(config);
  assert.equal(code, 0);
  assert.ok(lines.includes('issue-501-change-7001  document-1  present  rules-ok'));
  assert.ok(!lines.some((line) => line.includes('checkpoint')));
});

test('check --resume reads the checkpoint and exits 1 for a document with no rules', (t) => {
  const { config, file } = fixtureConfig(t);
  writeCheckpoint(config, 'issue-501-change-7001', 'phase1', [included(1, UC09)]);
  const run = spawnSync(process.execPath, [path.join(HERE, 'build-pack.mjs'), 'check', '--config', file,
    '--issue', '501', '--change', '7001', '--doc', UC01, '--resume'], { encoding: 'utf8' });
  assert.equal(run.status, 1);
  assert.match(run.stdout, /^document-1  missing  rules-not-extracted$/m);
});

test('a stale running row is checked against its checkpoint, as the nightly settle resumes it', async (t) => {
  const { config } = fixtureConfig(t);
  addJob(config, { issue: '501', change: '7001' });
  setRow(config, 'issue-501-change-7001', { status: 'running', started: new Date().toISOString() });
  writeCheckpoint(config, 'issue-501-change-7001', 'phase1', [included(1, UC09)]);
  const { lines, code } = await precheckQueue(config);
  assert.equal(code, 1);
  assert.ok(lines.includes('issue-501-change-7001  running  stale-row'));
  assert.ok(lines.includes('issue-501-change-7001  document-1  missing  rules-not-extracted'));
});
