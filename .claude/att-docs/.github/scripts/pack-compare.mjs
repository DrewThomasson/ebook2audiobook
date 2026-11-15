// Runs the pack comparison for the pack-compare workflow and keeps its log free of
// work content.
//
//   node pack-compare.mjs run       compare the files staged in the folder
//   node pack-compare.mjs cleanup   delete the staged files and the output folder
//
// The folder comes from the workflow's dispatch input (read from the event file, never
// from the command line). It holds these files, and nothing else is ever touched:
//
//   reference.xlsx   the reference pack
//   pack.xlsx        the built pack
//   doc.md           the converted document
//   rules.json or rules.xlsx   the rule export or the Business Rules workbook (one of them)
//   standard.md      optional, the workbook standard
//
// The report is written to a folder under RUNNER_TEMP and deleted by `cleanup`. Only
// lines that match the count patterns below reach the log; anything else is counted
// and dropped.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

export const DEFAULT_FOLDER = 'C:\\pack-compare';
export const FIXED_NAMES = ['reference.xlsx', 'pack.xlsx', 'doc.md', 'rules.json', 'rules.xlsx', 'standard.md'];
export const SCRIPT = path.resolve(path.dirname(fileURLToPath(import.meta.url)),
  '../../plugins/att-docs/skills/build-test-pack/local/build-pack.mjs');

/** The only lines the comparison may print to the log. Each is counts or a flag name. */
const ALLOWED_LINES = [
  /^format {2}\d+\/\d+ checks matched, \d+ deliberate, \d+ other$/,
  /^floor {3}reference cards=\d+ pack cards=\d+ repeats=\d+ unmatched=\d+$/,
  /^truth {3}retired-missing=\d+ untrue-rows=\d+ contradictions=\d+ cited-missing=\d+$/,
  /^truth {3}reference: untrue-rows=\d+ contradictions=\d+ cited-missing=\d+$/,
  /^model {3}(run|not run)$/,
  /^wrote compare\.json and compare\.md$/,
  /^compare failed \(\w+\)$/,
  /^--(reference|pack|rules|doc|standard) (is not a file|could not be read)$/,
  /^compare (needs --\w+|takes one --doc)$/,
];

export const isAllowed = (line) => ALLOWED_LINES.some((pattern) => pattern.test(line));

/** The staging folder from the dispatch event file, or the default when none was typed. */
export function readFolder(eventPath) {
  let typed = '';
  try {
    typed = String(JSON.parse(fs.readFileSync(eventPath, 'utf8'))?.inputs?.folder ?? '').trim();
  } catch {
    // No event file (a run outside a dispatch): use the default.
  }
  return typed || DEFAULT_FOLDER;
}

const inside = (base, dir) => {
  const relative = path.relative(path.resolve(base), path.resolve(dir));
  return relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative));
};

/**
 * Returns the reason a staging folder cannot be used, or '' when it can. A reason
 * never contains the folder's name.
 */
export function folderProblem(dir, env = process.env) {
  if (/[\x00-\x1f]/.test(dir)) return 'the folder name has control characters';
  if (!path.isAbsolute(dir)) return 'the folder is not an absolute path';
  const resolved = path.resolve(dir);
  if (path.parse(resolved).root === resolved) return 'the folder is a drive root';
  const guarded = [os.homedir(), env.RUNNER_WORKSPACE, env.GITHUB_WORKSPACE, process.cwd()].filter(Boolean);
  if (guarded.some((base) => inside(base, resolved))) {
    return 'the folder is the user profile, the runner workspace or the checkout, or inside one';
  }
  let stat;
  try {
    stat = fs.statSync(resolved);
  } catch {
    return 'the folder does not exist';
  }
  return stat.isDirectory() ? '' : 'the folder is not a directory';
}

/** The folder's compare inputs as command-line flags, or a reason string when they are not usable. */
export function stagedFlags(dir) {
  const has = (name) => fs.existsSync(path.join(dir, name)) && fs.statSync(path.join(dir, name)).isFile();
  for (const name of ['reference.xlsx', 'pack.xlsx', 'doc.md']) {
    if (!has(name)) return { problem: `${name} is missing from the folder` };
  }
  const rules = ['rules.json', 'rules.xlsx'].filter(has);
  if (rules.length !== 1) return { problem: 'the folder needs exactly one of rules.json and rules.xlsx' };
  const flags = ['--reference', path.join(dir, 'reference.xlsx'), '--pack', path.join(dir, 'pack.xlsx'),
    '--rules', path.join(dir, rules[0]), '--doc', path.join(dir, 'doc.md')];
  if (has('standard.md')) flags.push('--standard', path.join(dir, 'standard.md'));
  return { flags };
}

/** Where the report goes: a folder under RUNNER_TEMP named for the run. */
export const outFolder = (env = process.env) => path.join(env.RUNNER_TEMP || os.tmpdir(), `pack-compare-${env.GITHUB_RUN_ID || 'local'}`);

/**
 * Runs the comparison and prints its count lines. Returns the exit code: the
 * command's own, or 1 when it exited 0 without writing its report.
 */
export function run({ folder, env = process.env, script = SCRIPT, log = console.log } = {}) {
  const problem = folderProblem(folder, env);
  if (problem) {
    log(`compare not started: ${problem}`);
    return 2;
  }
  const staged = stagedFlags(folder);
  if (staged.problem) {
    log(`compare not started: ${staged.problem}`);
    return 2;
  }
  const out = outFolder(env);
  const result = spawnSync(process.execPath, [script, 'compare', ...staged.flags, '--out', out], {
    encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true,
  });
  let suppressed = 0;
  let wrote = false;
  for (const line of `${result.stdout ?? ''}\n${result.stderr ?? ''}`.split(/\r?\n/)) {
    if (!line.trim()) continue;
    if (isAllowed(line)) {
      log(line);
      if (line.startsWith('wrote ')) wrote = true;
    } else {
      suppressed += 1;
    }
  }
  if (suppressed) log(`suppressed ${suppressed} line(s)`);
  let code = result.status ?? 1;
  // A command that ends without running (the script's own start guard) exits 0 and prints nothing.
  if (code === 0 && !wrote) code = 1;
  log(`compare exit ${code}`);
  return code;
}

/** Deletes the staged files by their fixed names and the output folder. Prints counts only. */
export function cleanup({ folder, env = process.env, log = console.log } = {}) {
  let removed = 0;
  const problem = folderProblem(folder, env);
  if (problem) {
    log(`staged files not touched: ${problem}`);
  } else {
    for (const name of FIXED_NAMES) {
      const file = path.join(folder, name);
      if (!fs.existsSync(file)) continue;
      try {
        fs.rmSync(file, { force: true });
        removed += 1;
      } catch {
        // A file that cannot be removed shows in the count of files left below.
      }
    }
    // Only an empty folder goes; an unrelated file keeps it.
    try {
      fs.rmdirSync(folder);
    } catch {
      // Not empty, or still in use.
    }
  }
  const out = outFolder(env);
  try {
    // A scanner reading the fresh report can hold it for a moment on Windows.
    fs.rmSync(out, { recursive: true, force: true, maxRetries: 5, retryDelay: 500 });
  } catch {
    // The count below decides the exit code.
  }
  const left = FIXED_NAMES.filter((name) => fs.existsSync(path.join(folder, name))).length;
  log(`cleanup: removed ${removed} staged file(s), ${left} left, `
    + `output folder ${fs.existsSync(out) ? 'left' : 'removed'}`);
  return left || fs.existsSync(out) ? 1 : 0;
}

const realpath = (file) => {
  try {
    return fs.realpathSync(file);
  } catch {
    return path.resolve(file);
  }
};
// A junction in the path changes one side only, and Windows file names ignore case.
const same = (a, b) => (process.platform === 'win32' ? a.toLowerCase() === b.toLowerCase() : a === b);

if (process.argv[1] && same(realpath(process.argv[1]), realpath(fileURLToPath(import.meta.url)))) {
  const mode = process.argv[2];
  const folder = readFolder(process.env.GITHUB_EVENT_PATH ?? '');
  // The folder's name is typed by a person and sits in the run's inputs, so keep it out of the log.
  if (process.env.GITHUB_ACTIONS) {
    // The runner ends a line at any control character, so mask each piece on its own.
    for (const part of folder.split(/[\x00-\x1f]+/).filter(Boolean)) console.log(`::add-mask::${part}`);
  }
  if (mode === 'run') process.exitCode = run({ folder });
  else if (mode === 'cleanup') process.exitCode = cleanup({ folder });
  else {
    console.error('usage: pack-compare.mjs run | cleanup');
    process.exitCode = 2;
  }
}
