import { after, test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { DEFAULT_FOLDER, SCRIPT, cleanup, folderProblem, isAllowed, outFolder, readFolder, run, stagedFlags }
  from './pack-compare.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
// One scratch root for the whole file, removed when the last test ends.
const SCRATCH_ROOT = fs.mkdtempSync(path.join(os.tmpdir(), 'pack-compare-test-'));
after(() => fs.rmSync(SCRATCH_ROOT, { recursive: true, force: true }));
const tmp = () => fs.mkdtempSync(path.join(SCRATCH_ROOT, 'case-'));
const touch = (dir, ...names) => names.forEach((name) => fs.writeFileSync(path.join(dir, name), 'x'));
const staged = (dir, rules = 'rules.json') => touch(dir, 'reference.xlsx', 'pack.xlsx', 'doc.md', rules);

// A stand-in for build-pack.mjs: prints what the test file names and exits with a chosen code.
function stub(dir, body) {
  const file = path.join(dir, 'stub.mjs');
  fs.writeFileSync(file, body);
  return file;
}

const COUNTS = [
  'format  3/5 checks matched, 1 deliberate, 1 other',
  'floor   reference cards=4 pack cards=5 repeats=0 unmatched=1',
  'truth   retired-missing=0 untrue-rows=2 contradictions=0 cited-missing=1',
  'truth   reference: untrue-rows=0 contradictions=0 cited-missing=0',
  'model   not run',
  'wrote compare.json and compare.md',
];

test('the folder comes from the event file and falls back to the default', () => {
  const dir = tmp();
  const event = path.join(dir, 'event.json');
  fs.writeFileSync(event, JSON.stringify({ inputs: { folder: ' D:\\staged ' } }));
  assert.equal(readFolder(event), 'D:\\staged');
  fs.writeFileSync(event, JSON.stringify({ inputs: { folder: '' } }));
  assert.equal(readFolder(event), DEFAULT_FOLDER);
  assert.equal(readFolder(path.join(dir, 'missing.json')), DEFAULT_FOLDER);
});

test('a folder that could hold anything but staged files is refused, without naming it', () => {
  const dir = tmp();
  const secret = path.join(dir, 'client-secret-name');
  const reasons = [
    folderProblem('relative/folder'),
    folderProblem(path.parse(dir).root),
    folderProblem(os.homedir()),
    folderProblem(secret),
    folderProblem(dir, { RUNNER_WORKSPACE: dir }),
    folderProblem(path.join(dir, 'inner'), { GITHUB_WORKSPACE: dir }),
  ];
  assert.ok(reasons.every(Boolean));
  assert.ok(reasons.every((reason) => !reason.includes('client-secret-name')));
  assert.equal(folderProblem(dir, {}), '');
});

test('the staged files need the three fixed names and exactly one rules file', () => {
  const dir = tmp();
  assert.match(stagedFlags(dir).problem, /reference\.xlsx is missing/);
  staged(dir);
  assert.ok(stagedFlags(dir).flags.includes(path.join(dir, 'rules.json')));
  touch(dir, 'rules.xlsx');
  assert.match(stagedFlags(dir).problem, /exactly one/);
  fs.rmSync(path.join(dir, 'rules.json'));
  assert.ok(stagedFlags(dir).flags.includes(path.join(dir, 'rules.xlsx')));
  assert.ok(!stagedFlags(dir).flags.includes('--standard'));
  touch(dir, 'standard.md');
  assert.ok(stagedFlags(dir).flags.includes('--standard'));
});

test('only count lines pass the log filter', () => {
  assert.ok(COUNTS.every(isAllowed));
  assert.ok(!isAllowed('format  card "Renew at the desk" differs'));
  assert.ok(!isAllowed('floor   reference cards=4 pack cards=5 repeats=0 unmatched=1 C:\\secret\\pack.xlsx'));
  assert.ok(!isAllowed('Error: ENOENT: no such file, open \'C:\\secret\\pack.xlsx\''));
  assert.ok(isAllowed('--pack is not a file'));
  assert.ok(isAllowed('compare failed (TypeError)'));
});

test('every line shape the compare command prints passes the filter', () => {
  // The same shapes compare.test.mjs pins for the real command, with N for each number.
  const shapes = [
    'format  N/N checks matched, N deliberate, N other',
    'floor   reference cards=N pack cards=N repeats=N unmatched=N',
    'truth   retired-missing=N untrue-rows=N contradictions=N cited-missing=N',
    'truth   reference: untrue-rows=N contradictions=N cited-missing=N',
    'model   not run',
    'model   run',
    'wrote compare.json and compare.md',
  ];
  assert.ok(shapes.every((shape) => isAllowed(shape.replace(/N/g, '12'))));
});

test('run passes the exit code through and logs only allowed lines', () => {
  const dir = tmp();
  staged(dir);
  const env = { RUNNER_TEMP: tmp(), GITHUB_RUN_ID: '7' };
  const lines = [];
  const script = stub(dir, `${COUNTS.map((line) => `console.log(${JSON.stringify(line)});`).join('\n')}
console.log('card: Renew a lapsed card');
console.error('stack at C:\\\\secret\\\\pack.xlsx');
process.exitCode = 0;`);
  assert.equal(run({ folder: dir, env, script, log: (line) => lines.push(line) }), 0);
  assert.deepEqual(lines, [...COUNTS, 'suppressed 2 line(s)', 'compare exit 0']);
  assert.ok(!lines.join('\n').includes('Renew'));
});

test('run fails an exit 0 that wrote no report and passes a failing exit through', () => {
  const dir = tmp();
  staged(dir);
  const env = { RUNNER_TEMP: tmp() };
  const lines = [];
  const silent = stub(dir, '');
  assert.equal(run({ folder: dir, env, script: silent, log: (line) => lines.push(line) }), 1);
  const failing = stub(dir, "console.error('compare failed (Error)'); process.exitCode = 1;");
  assert.equal(run({ folder: dir, env, script: failing, log: (line) => lines.push(line) }), 1);
  const usage = stub(dir, "console.error('--pack is not a file'); process.exitCode = 2;");
  assert.equal(run({ folder: dir, env, script: usage, log: (line) => lines.push(line) }), 2);
});

test('run hands the stub the staged files and an output folder under the temp folder', () => {
  const dir = tmp();
  staged(dir);
  const env = { RUNNER_TEMP: tmp(), GITHUB_RUN_ID: '9' };
  const script = stub(dir, `const a = process.argv.slice(2);
const at = (flag) => a[a.indexOf(flag) + 1];
console.log(at('--out') === ${JSON.stringify(outFolder(env))} ? 'wrote compare.json and compare.md' : 'bad out');
console.log(a[0] === 'compare' && at('--doc').endsWith('doc.md') ? 'model   not run' : 'bad args');`);
  const lines = [];
  assert.equal(run({ folder: dir, env, script, log: (line) => lines.push(line) }), 0);
  assert.deepEqual(lines, ['wrote compare.json and compare.md', 'model   not run', 'compare exit 0']);
});

test('run does not start on an unusable folder', () => {
  const lines = [];
  assert.equal(run({ folder: 'relative', log: (line) => lines.push(line) }), 2);
  assert.match(lines[0], /^compare not started: /);
});

test('cleanup removes the staged names and the report, and keeps an unrelated file', () => {
  const dir = tmp();
  staged(dir, 'rules.xlsx');
  touch(dir, 'notes.txt');
  const env = { RUNNER_TEMP: tmp(), GITHUB_RUN_ID: '3' };
  const out = outFolder(env);
  fs.mkdirSync(out, { recursive: true });
  touch(out, 'compare.md');
  const lines = [];
  assert.equal(cleanup({ folder: dir, env, log: (line) => lines.push(line) }), 0);
  assert.deepEqual(fs.readdirSync(dir), ['notes.txt']);
  assert.ok(!fs.existsSync(out));
  assert.equal(lines[0], 'cleanup: removed 4 staged file(s), 0 left, output folder removed');
  fs.rmSync(path.join(dir, 'notes.txt'));
  assert.equal(cleanup({ folder: dir, env, log: () => {} }), 0);
  assert.ok(!fs.existsSync(dir));
});

test('the command line reads the folder from the event file, masks it, and cleans up', () => {
  const dir = tmp();
  const folder = path.join(dir, 'staged');
  fs.mkdirSync(folder);
  staged(folder);
  const event = path.join(dir, 'event.json');
  fs.writeFileSync(event, JSON.stringify({ inputs: { folder } }));
  const env = { ...process.env, GITHUB_EVENT_PATH: event, GITHUB_ACTIONS: 'true', RUNNER_TEMP: tmp(), GITHUB_RUN_ID: '5' };
  const exec = (mode) => spawnSync(process.execPath, [path.join(here, 'pack-compare.mjs'), mode], { encoding: 'utf8', env, cwd: tmp() });
  const first = exec('run');
  assert.equal(first.status, 2);
  assert.equal(first.stdout.split('\n')[0], `::add-mask::${folder}`);
  assert.match(first.stdout, /--reference could not be read\ncompare exit 2/);
  assert.ok(SCRIPT.endsWith('build-pack.mjs') && fs.existsSync(SCRIPT));
  const second = exec('cleanup');
  assert.equal(second.status, 0, second.stdout);
  assert.ok(!fs.existsSync(folder));
  assert.equal(exec('nonsense').status, 2);
});

test('cleanup deletes nothing in a folder that is refused', () => {
  const dir = tmp();
  staged(dir);
  const lines = [];
  const env = { RUNNER_TEMP: tmp(), GITHUB_RUN_ID: '4', RUNNER_WORKSPACE: dir };
  assert.equal(cleanup({ folder: dir, env, log: (line) => lines.push(line) }), 1);
  assert.equal(fs.readdirSync(dir).length, 4);
  assert.match(lines[0], /^staged files not touched: /);
  assert.ok(folderProblem(`${dir}\nmore`).includes('control characters'));
});

test('the workflow keeps to the runner and logging rules', () => {
  const text = fs.readFileSync(path.join(here, '../workflows/pack-compare.yml'), 'utf8')
    .split('\n').filter((line) => !line.trim().startsWith('#')).join('\n');
  assert.match(text, /runs-on: \[self-hosted, overmind, Windows\]/);
  assert.equal([...text.matchAll(/runs-on:/g)].length, 1);
  for (const banned of ['${{ inputs.', 'github.event.inputs', 'upload-artifact', 'playwright', 'run-name',
    'GITHUB_STEP_SUMMARY', 'secrets.', 'ubuntu-latest', 'windows-latest']) {
    assert.ok(!text.includes(banned), banned);
  }
  assert.match(text, /if: always\(\)[\s\S]*pack-compare\.mjs'[\s\S]*node \$script cleanup/);
  assert.match(text, /on:\n  workflow_dispatch:/);
  assert.ok(!/^  (push|pull_request|schedule)/m.test(text));
});
