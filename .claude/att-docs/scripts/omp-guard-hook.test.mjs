// Run with: node --test scripts/omp-guard-hook.test.mjs
// Builds a throwaway repository with one worktree, copies the guard and the hook into it, and
// feeds the hook the tool_call events such a session emits. Each case says whether the call is
// let through or blocked.
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import {
  chmodSync,
  cpSync,
  mkdirSync,
  mkdtempSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { after, before, describe, it } from 'node:test';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));

let sandbox;
let main;
let tree;
let handler;

const git = (...args) =>
  execFileSync('git', ['-C', main, '-c', 'user.name=t', '-c', 'user.email=t@t', ...args], {
    stdio: 'ignore',
  });

// The handler a copy of the hook in `dir` registers, or undefined when it registers none.
const handlerOf = async dir => {
  const hook = await import(path.join(dir, 'scripts', 'omp-guard-hook.mjs'));
  let registered;
  hook.default({ on: (_event, fn) => (registered = fn) });
  return registered;
};

before(async () => {
  sandbox = mkdtempSync(path.join(tmpdir(), 'omp-guard-'));
  main = path.join(sandbox, 'main');
  tree = path.join(main, '.claude', 'worktrees', 'wt');
  mkdirSync(path.join(main, 'scripts'), { recursive: true });
  mkdirSync(path.join(main, 'node_modules'));
  for (const file of ['guard-main-checkout.sh', 'omp-guard-hook.mjs']) {
    cpSync(path.join(HERE, file), path.join(main, 'scripts', file));
  }
  cpSync(path.join(HERE, 'lib'), path.join(main, 'scripts', 'lib'), { recursive: true });
  git('init', '-q', '-b', 'main');
  git('commit', '-q', '--allow-empty', '-m', 'init');
  git('worktree', 'add', '-q', '-b', 'wt', tree);
  symlinkSync(path.join(main, 'node_modules'), path.join(tree, 'node_modules'));
  handler = await handlerOf(main);
});

after(() => rmSync(sandbox, { recursive: true, force: true }));

// The verdict for one call: 'block' or 'pass'.
const verdict = async (toolName, input, cwd) => {
  const result = await handler({ toolName, input }, { cwd });
  return result?.block ? 'block' : 'pass';
};

describe('file tools from the main checkout', () => {
  it('blocks a write that lands in the checkout', async () => {
    assert.equal(await verdict('write', { path: path.join(main, 'src/a.ts') }, main), 'block');
    assert.equal(await verdict('write', { path: 'src/a.ts' }, main), 'block');
  });

  it('passes a write into the worktree and the internal-URL targets', async () => {
    assert.equal(await verdict('write', { path: path.join(tree, 'src/a.ts') }, main), 'pass');
    assert.equal(await verdict('write', { path: 'xd://ast_edit', content: '{}' }, main), 'pass');
    assert.equal(await verdict('write', { path: 'local://notes.md' }, main), 'pass');
  });

  it('judges the path an edit names', async () => {
    const hashline = file => ({
      input: `[${file}#ABCD]\nPUT 1.=1:\n+x`,
      path: file,
      paths: [file],
    });
    assert.equal(await verdict('edit', hashline('src/a.ts'), main), 'block');
    assert.equal(await verdict('edit', hashline(`${tree}/a.ts`), main), 'pass');
  });

  it('blocks an ast_edit whose paths reach the checkout', async () => {
    assert.equal(await verdict('ast_edit', { paths: ['src/**/*.ts'] }, main), 'block');
    assert.equal(await verdict('ast_edit', { paths: [`${tree}/src/**/*.ts`] }, main), 'pass');
  });
});

describe('a worktree session', () => {
  it('passes a relative path and blocks one that climbs into the checkout', async () => {
    assert.equal(await verdict('write', { path: 'src/a.ts' }, tree), 'pass');
    assert.equal(await verdict('write', { path: '../../../src/a.ts' }, tree), 'block');
    assert.equal(await verdict('write', { path: 'node_modules/x.js' }, tree), 'block');
  });

  it('sees through the wrappers the harness removes from a path', async () => {
    const target = `${main}/src/a.ts`;
    for (const wrapped of [
      `@${target}`,
      `:${target}`,
      `[${target}]`,
      `[${target}#AB12]`,
      `file://${target}`,
    ]) {
      assert.equal(await verdict('write', { path: wrapped }, tree), 'block', wrapped);
    }
    assert.equal(await verdict('write', { path: '[node_modules/x.js]' }, tree), 'block');
    assert.equal(await verdict('write', { path: `@${tree}/src/a.ts` }, tree), 'pass');
  });

  it('passes a wrapped absolute path that resolves outside the checkout', async () => {
    for (const wrapped of [`@${tree}/a.ts`, `[${tree}/a.ts]`, `:${sandbox}/x.md`, `@/tmp/x.md`]) {
      assert.equal(await verdict('write', { path: wrapped }, main), 'pass', wrapped);
    }
  });

  it('expands ~ the way the harness does', async () => {
    const home = process.env.HOME;
    process.env.HOME = sandbox;
    try {
      assert.equal(await verdict('write', { path: '~/main/src/a.ts' }, tree), 'block');
      const call = { command: 'git switch x', cwd: '~/main' };
      assert.equal(await verdict('bash', call, tree), 'block');
      assert.equal(await verdict('write', { path: '~/scratch/a.md' }, tree), 'pass');
    } finally {
      process.env.HOME = home;
    }
  });
});

describe('edit forms that name a file in their text', () => {
  const edit = input => ({ input });

  it('blocks a hashline move into the checkout, whatever its spacing', async () => {
    const file = path.join(tree, 'a.ts');
    const move = row => ({ input: `[${file}#ABCD]\n${row}`, path: file, paths: [file] });
    assert.equal(await verdict('edit', move(`MV ${main}/b.ts`), tree), 'block');
    assert.equal(await verdict('edit', move(`MV "${main}/my b.ts"`), tree), 'block');
    assert.equal(await verdict('edit', move(`MV ${main}/my file.ts`), tree), 'block');
    assert.equal(await verdict('edit', move(`  MV\t${main}/b.ts`), tree), 'block');
    assert.equal(await verdict('edit', move(`MV ${tree}/b.ts`), tree), 'pass');
  });

  it('blocks an apply_patch whose sections name the checkout', async () => {
    for (const header of ['Add File', 'Update File', 'Delete File']) {
      const patch = `*** Begin Patch\n*** ${header}: ${main}/src/a.ts\n+x\n*** End Patch`;
      assert.equal(await verdict('edit', edit(patch), tree), 'block', header);
    }
    const move = `*** Update File: ${tree}/a.ts\n*** Move to: ${main}/b.ts`;
    assert.equal(await verdict('edit', edit(move), tree), 'block');
    const inside = `*** Begin Patch\n*** Add File: ${tree}/a.ts\n+x\n*** End Patch`;
    assert.equal(await verdict('edit', edit(inside), tree), 'pass');
  });

  it('does not read a patch context line as a header or a move', async () => {
    const patch = [
      '*** Begin Patch',
      `*** Update File: ${tree}/Cargo.toml`,
      ' [package]',
      ' MV elsewhere',
      '-name = "a"',
      '+name = "b"',
      '*** End Patch',
    ].join('\n');
    assert.equal(await verdict('edit', edit(patch), main), 'pass');
  });

  it('blocks a sloppy edit of a file in the checkout', async () => {
    const sloppy = `*** Edit File: ${main}/src/a.ts\n*** Find\na\n*** Replace\nb`;
    assert.equal(await verdict('edit', edit(sloppy), tree), 'block');
  });

  it('reads the sloppy header in any case, with or without the colon', async () => {
    for (const header of ['*** edit file: ', '*** EDIT  FILE ', '***  Edit File:']) {
      const sloppy = `${header}${main}/src/a.ts\n*** Find\na\n*** Replace\nb`;
      assert.equal(await verdict('edit', edit(sloppy), tree), 'block', header);
    }
    const inside = `*** edit file: ${tree}/a.ts\n*** Find\na\n*** Replace\nb`;
    assert.equal(await verdict('edit', edit(inside), tree), 'pass');
  });

  it('reads a hashline header that has trailing whitespace', async () => {
    const header = (dir, tail) => edit(`${tail}\nPUT 1.=1:\n+x`.replace('DIR', dir));
    assert.equal(await verdict('edit', header(main, '[DIR/a.ts#ABCD] \t'), tree), 'block');
    assert.equal(await verdict('edit', header(main, '¶DIR/a.ts#ABCD'), tree), 'block');
    assert.equal(await verdict('edit', header(tree, '[DIR/a.ts#ABCD] '), tree), 'pass');
  });

  it('reads a quoted header and one that copies a patch prefix', async () => {
    const header = (dir, tail) => edit(`${tail}\nPUT 1.=1:\n+x`.replace('DIR', dir));
    assert.equal(await verdict('edit', header(main, '["DIR/a b.ts"#ABCD] '), tree), 'block');
    const copied = '[*** Update File: DIR/a.ts#ABCD]';
    assert.equal(await verdict('edit', header(main, copied), tree), 'block');
    assert.equal(await verdict('edit', header(tree, '["DIR/a b.ts"#ABCD]'), tree), 'pass');
  });

  it('blocks a patch-mode rename into the checkout', async () => {
    const patch = { path: `${tree}/a.ts`, edits: [{ op: 'update', rename: `${main}/b.ts` }] };
    assert.equal(await verdict('edit', patch, tree), 'block');
    const inside = { path: `${tree}/a.ts`, edits: [{ op: 'update', rename: `${tree}/b.ts` }] };
    assert.equal(await verdict('edit', inside, tree), 'pass');
  });

  it('refuses an edit that names no file, and passes an edit of an internal URL', async () => {
    assert.equal(await verdict('edit', { input: '*** Surprise: a.ts' }, tree), 'block');
    assert.equal(await verdict('edit', {}, tree), 'block');
    assert.equal(await verdict('edit', { path: 'local://notes.md' }, main), 'pass');
  });
});

describe('tools that list paths', () => {
  it('reads every pattern of an ast_edit entry', async () => {
    const joined = `${tree}/src/a.ts;${main}/src/**/*.ts`;
    assert.equal(await verdict('ast_edit', { paths: [joined] }, tree), 'block');
    assert.equal(await verdict('ast_edit', { paths: [`${tree}/**;!${main}/**`] }, tree), 'pass');
  });

  it('judges the files an lsp rename touches', async () => {
    const move = { action: 'rename_file', file: `${tree}/a.ts`, new_name: `${main}/b.ts` };
    assert.equal(await verdict('lsp', move, tree), 'block');
    assert.equal(await verdict('lsp', { action: 'rename', file: `${main}/a.ts` }, tree), 'block');
    assert.equal(await verdict('lsp', { action: 'rename', file: `${tree}/a.ts` }, tree), 'pass');
    assert.equal(await verdict('lsp', { action: 'hover', file: `${main}/a.ts` }, tree), 'pass');
  });
});

describe('bash', () => {
  it('blocks branch-changing git that acts on the checkout', async () => {
    assert.equal(await verdict('bash', { command: 'git checkout main' }, main), 'block');
    assert.equal(await verdict('bash', { command: `git -C ${main} pull` }, tree), 'block');
  });

  it('reads the cwd argument as where the command starts', async () => {
    assert.equal(await verdict('bash', { command: 'git switch x', cwd: tree }, main), 'pass');
    assert.equal(await verdict('bash', { command: 'git switch x', cwd: main }, tree), 'block');
  });

  it('reads a bare / cwd as the session directory, as the harness does', async () => {
    assert.equal(await verdict('bash', { command: 'git switch x', cwd: '/' }, main), 'block');
    assert.equal(await verdict('bash', { command: 'git switch x', cwd: '/' }, tree), 'pass');
  });

  it('passes a command the guard does not read', async () => {
    assert.equal(await verdict('bash', { command: 'ls' }, main), 'pass');
  });
});

describe('tools the guard does not read', () => {
  it('passes a read and an eval', async () => {
    assert.equal(await verdict('read', { path: path.join(main, 'src/a.ts') }, main), 'pass');
    assert.equal(await verdict('eval', { language: 'js', code: '1' }, main), 'pass');
  });
});

describe('a guard that cannot give a verdict', () => {
  // A second copy of the hook beside a guard script the case controls.
  const copyWith = (name, guard, mode) => {
    const dir = path.join(sandbox, name);
    mkdirSync(path.join(dir, 'scripts'), { recursive: true });
    cpSync(path.join(HERE, 'omp-guard-hook.mjs'), path.join(dir, 'scripts/omp-guard-hook.mjs'));
    writeFileSync(path.join(dir, 'scripts/guard-main-checkout.sh'), guard);
    chmodSync(path.join(dir, 'scripts/guard-main-checkout.sh'), mode);
    return dir;
  };

  it('registers nothing when the guard is not executable', async () => {
    const dir = copyWith('no-exec', '#!/bin/sh\nexit 2\n', 0o644);
    assert.equal(await handlerOf(dir), undefined);
  });

  it('lets the call through and says so when the guard crashes', async () => {
    const dir = copyWith('crashing', '#!/bin/sh\necho jq missing >&2\nexit 1\n', 0o755);
    const result = await (await handlerOf(dir))(
      { toolName: 'write', input: { path: 'a.ts' } },
      { cwd: dir },
    );
    assert.equal(result.block, undefined);
    assert.match(result.additionalContext, /no verdict \(status 1\): jq missing/);
  });
});
