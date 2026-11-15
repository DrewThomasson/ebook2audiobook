// Tests for wiki.mjs: the check, --write, --report, and the option and config refusals,
// each run against a scratch git repository.
// Run: node --test plugins/att-docs/skills/living-wiki/wiki.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

// No global or system git config reaches the scratch repositories.
const GIT_ENV = { ...process.env, GIT_CONFIG_GLOBAL: '/dev/null', GIT_CONFIG_SYSTEM: '/dev/null' };
const SCRIPT = path.join(path.dirname(fileURLToPath(import.meta.url)), 'wiki.mjs');

// A scratch repository with docs/, a descriptions file and a config.
function repo(files, { config = {}, descriptions } = {}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'wiki-test-'));
  spawnSync('git', ['init', '-q'], { cwd: dir, env: GIT_ENV });
  const put = (rel, text) => {
    fs.mkdirSync(path.dirname(path.join(dir, rel)), { recursive: true });
    fs.writeFileSync(path.join(dir, rel), text);
  };
  for (const [rel, text] of Object.entries(files)) put(rel, text);
  put('descriptions.tsv', descriptions
    ?? '.\tThe docs.\napps\tApp pages.\nglossary.md\tTerms.\n');
  put('wiki.json', JSON.stringify({ descriptions: 'descriptions.tsv', ...config }));
  return {
    dir,
    docs: (rel) => path.join(dir, 'docs', rel),
    run: (...extra) => {
      const r = spawnSync(process.execPath, [SCRIPT, '--config', path.join(dir, 'wiki.json'), ...extra],
        { encoding: 'utf8', env: { ...GIT_ENV, HOME: dir } });
      return { code: r.status, out: r.stdout, err: r.stderr };
    },
    done: () => fs.rmSync(dir, { recursive: true, force: true }),
  };
}

const TREE = {
  'docs/apps/index.md': '# Apps\n',
  'docs/apps/one.md': 'See [two](two.md).\n',
  'docs/apps/two.md': 'Two.\n',
  'docs/glossary.md': 'Terms.\n',
};

test('a tree behind its generated pages fails with 3, then --write makes it clean', () => {
  const r = repo(TREE);
  try {
    const first = r.run();
    assert.equal(first.code, 3);
    assert.match(first.out, /Home\.md: behind the tree/);
    assert.match(first.out, /apps\.md: behind the tree/);
    assert.match(first.out, /apps\/\.order: behind the tree/);
    assert.ok(!fs.existsSync(r.docs('Home.md')), 'check alone writes nothing');

    const wrote = r.run('--write');
    assert.equal(wrote.code, 0);
    assert.match(wrote.out, /wiki: wrote 4 page\(s\), removed 0/);
    const home = fs.readFileSync(r.docs('Home.md'), 'utf8');
    assert.match(home, /^<!-- Generated from the folder layout under docs\//);
    assert.match(home, /# Documentation/);
    assert.match(home, /- \[apps\]\(apps\.md\): App pages\./);
    assert.match(home, /- \[glossary\]\(glossary\.md\): Terms\./);
    assert.equal(fs.readFileSync(r.docs('apps/.order'), 'utf8'), 'index\n');
    assert.equal(fs.readFileSync(r.docs('.order'), 'utf8'), 'Home\n');
    assert.match(fs.readFileSync(r.docs('apps.md'), 'utf8'), /Start with \[index\]\(apps\/index\.md\)\./);

    const again = r.run();
    assert.equal(again.code, 0);
    assert.match(again.out, /wiki: clean \(/);
  } finally { r.done(); }
});

test('homeTitle and rootOrder shape the generated home page and root .order', () => {
  const r = repo({ ...TREE, 'docs/zeta/a.md': 'A.\n' }, {
    config: { homeTitle: 'Handbook', rootOrder: ['zeta', 'apps'] },
    descriptions: '.\tThe docs.\napps\tApp pages.\nzeta\tZ.\nglossary.md\tTerms.\n',
  });
  try {
    assert.equal(r.run('--write').code, 0);
    assert.match(fs.readFileSync(r.docs('Home.md'), 'utf8'), /# Handbook/);
    assert.equal(fs.readFileSync(r.docs('.order'), 'utf8'), 'Home\nzeta\napps\n');
    const home = fs.readFileSync(r.docs('Home.md'), 'utf8');
    assert.ok(home.indexOf('[zeta]') < home.indexOf('[apps]'));
  } finally { r.done(); }
});

test('a name with a space fails with 2 and names the hyphenated rename', () => {
  const r = repo({ ...TREE, 'docs/apps/ACT 4.0 - Entry.md': 'x\n' });
  try {
    const res = r.run('--write');
    assert.equal(res.code, 2);
    assert.match(res.out, /apps\/ACT 4\.0 - Entry\.md: the name holds a space; rename it ACT-4\.0-Entry\.md/);
  } finally { r.done(); }
});

test('a name with # or a trailing period fails with 2', () => {
  const r = repo({ ...TREE, 'docs/apps/a#b.md': 'x\n', 'docs/apps/odd..md': 'x\n' });
  try {
    const res = r.run('--write');
    assert.equal(res.code, 2);
    assert.match(res.out, /apps\/a#b\.md: the name holds \\, # or a control character/);
    assert.match(res.out, /apps\/odd\.\.md: the name starts or ends with a period/);
  } finally { r.done(); }
});

test('a page path over 235 characters fails with 2', () => {
  const long = `${'x'.repeat(240)}.md`;
  const r = repo({ ...TREE, [`docs/apps/${long}`]: 'x\n' });
  try {
    const res = r.run('--write');
    assert.equal(res.code, 2);
    assert.match(res.out, /the page path is \d+ characters, over 235/);
  } finally { r.done(); }
});

test('two names that read as one page title fail with 2', () => {
  const r = repo({ ...TREE, 'docs/apps/My-Page.md': 'x\n', 'docs/apps/My%2DPage.md': 'y\n', 'docs/apps/My Page.md': 'z\n' });
  try {
    const res = r.run('--write');
    assert.equal(res.code, 2);
    assert.match(res.out, /both read as the page "My Page"/);
  } finally { r.done(); }
});

test('broken links fail with 2; URLs, anchors and fenced code do not', () => {
  const r = repo({
    ...TREE,
    'docs/apps/links.md': [
      '[gone](missing.md) [out](../../outside.md) [abs](/apps/one.md) [drive](C:/x.md)',
      '[dir](../apps) [ok](one.md#top) [web](https://example.com/x.md) [frag](#here)',
      '`[inline](nope.md)`',
      '```',
      '[fenced](nope2.md)',
      '```',
      '',
    ].join('\n'),
  });
  try {
    const res = r.run('--write');
    assert.equal(res.code, 2);
    assert.match(res.out, /links\.md: link missing\.md names a file that is not there/);
    assert.match(res.out, /links\.md: link \.\.\/\.\.\/outside\.md leaves docs\//);
    assert.match(res.out, /links\.md: absolute link \/apps\/one\.md/);
    assert.match(res.out, /links\.md: links to a local drive, C:\/x\.md/);
    assert.match(res.out, /links\.md: link \.\.\/apps names a folder; link the page beside it, apps\.md/);
    assert.doesNotMatch(res.out, /nope/);
    assert.doesNotMatch(res.out, /one\.md#top/);
    assert.doesNotMatch(res.out, /example\.com/);
  } finally { r.done(); }
});

test('a folder without a description fails with 2', () => {
  const r = repo({ ...TREE, 'docs/extra/a.md': 'x\n' });
  try {
    const res = r.run('--write');
    assert.equal(res.code, 2);
    assert.match(res.out, /extra: no description in descriptions\.tsv/);
  } finally { r.done(); }
});

test('a wildcard row describes each folder under a path with {name}', () => {
  const r = repo({ ...TREE, 'docs/apps/sub/a.md': 'x\n' }, {
    descriptions: '.\tThe docs.\napps\tApp pages.\napps/*\tThe {name} area.\nglossary.md\tTerms.\n',
  });
  try {
    assert.equal(r.run('--write').code, 0);
    assert.match(fs.readFileSync(r.docs('apps.md'), 'utf8'), /\[sub\]\(apps\/sub\.md\): The sub area\./);
  } finally { r.done(); }
});

test('--write leaves a hand-written page beside a folder alone', () => {
  const r = repo({ ...TREE, 'docs/apps.md': '# My own apps page\n' });
  try {
    assert.equal(r.run('--write').code, 0);
    assert.equal(fs.readFileSync(r.docs('apps.md'), 'utf8'), '# My own apps page\n');
    assert.equal(r.run().code, 0);
  } finally { r.done(); }
});

test('--write removes a generated page whose folder is gone, and the check reports it first', () => {
  const r = repo(TREE);
  try {
    assert.equal(r.run('--write').code, 0);
    fs.rmSync(r.docs('apps'), { recursive: true });
    const before = r.run();
    assert.equal(before.code, 3);
    assert.match(before.out, /apps\.md: behind the tree/);
    const wrote = r.run('--write');
    assert.equal(wrote.code, 0);
    assert.match(wrote.out, /removed 1/);
    assert.ok(!fs.existsSync(r.docs('apps.md')));
  } finally { r.done(); }
});

test('--report lists names with a hyphen or a non-ASCII character without failing', () => {
  const r = repo({ ...TREE, 'docs/apps/two-part.md': 'x\n', 'docs/apps/caf\u00e9.md': 'x\n' });
  try {
    assert.equal(r.run('--write').code, 0);
    const plain = r.run();
    assert.equal(plain.code, 0);
    assert.match(plain.out, /1 name\(s\) with a hyphen the wiki shows as a space, 1 with a character outside ASCII/);
    assert.doesNotMatch(plain.out, /hyphen: apps/);
    const report = r.run('--report');
    assert.equal(report.code, 0);
    assert.match(report.out, /hyphen: apps\/two-part\.md/);
    assert.match(report.out, /nonAscii: apps\/caf\u00e9\.md/);
  } finally { r.done(); }
});

test('an unknown option exits 64', () => {
  const r = repo(TREE);
  try {
    const res = r.run('--bogus');
    assert.equal(res.code, 64);
    assert.match(res.err, /unknown option --bogus/);
  } finally { r.done(); }
});

test('a missing --config exits 64', () => {
  const res = spawnSync(process.execPath, [SCRIPT], { encoding: 'utf8' });
  assert.equal(res.status, 64);
  assert.match(res.stderr, /--config <file> is required/);
});
