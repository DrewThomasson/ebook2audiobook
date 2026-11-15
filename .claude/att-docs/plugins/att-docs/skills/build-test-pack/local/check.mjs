// The setup check: says whether this host is ready to build test packs, so a
// missing unit or an unreachable model shows up before a job needs it. It reads
// the installed units, the env file, the pause targets, the model server and
// the release command. Every line is `<area>  <name>  pass|fail|warn  <code>` and
// names units, variables, config fields and thinking steps only; no value from
// the env file is ever printed. A `warn` line is advice and never fails the check.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { REASONING_STEPS } from './config.mjs';
import { localEndpoint, localFetch } from './model.mjs';
import { UNIT_NAME } from './pause.mjs';
import { outputCap } from './phases.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REQUIRED_ENV = ['BUILD_PACK_SCRIPT', 'BUILD_PACK_CONFIG'];

/** Runs one command with an argument array, never a shell. */
function defaultExec(command, args) {
  const result = spawnSync(command, args, { encoding: 'utf8', timeout: 15000 });
  return { status: result.error ? null : result.status, stdout: result.stdout ?? '' };
}

/** The NAME=value lines of an env file, as systemd reads them. Values stay in memory. */
export function parseEnvFile(text) {
  const env = new Map();
  for (const raw of text.split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#') || line.startsWith(';')) continue;
    const eq = line.indexOf('=');
    if (eq < 1) continue;
    let value = line.slice(eq + 1).trim();
    if (value.length > 1 && /^(["']).*\1$/.test(value)) value = value.slice(1, -1);
    env.set(line.slice(0, eq).trim(), value);
  }
  return env;
}

const isFile = (file, access) => {
  try {
    access(file);
    return fs.statSync(file).isFile();
  } catch {
    return false;
  }
};

const isExecutable = (file) => isFile(file, (f) => fs.accessSync(f, fs.constants.X_OK));

/** True when `word` names an executable, directly or in a directory of `searchPath`. */
function onPath(word, searchPath) {
  if (word.includes('/')) return isExecutable(word);
  return String(searchPath ?? '').split(':').filter(Boolean)
    .some((dir) => isExecutable(path.join(dir, word)));
}

// A command written without arguments allows any arguments, as in sudoers.
const globToRegExp = (pattern) => new RegExp(`^${pattern.split('*').map((part) => part
  .replace(/[.+?^${}()|[\]\\]/g, '\\$&')).join('.*')}${pattern.includes(' ') ? '' : '( .*)?'}$`);

/**
 * Whether `sudo -l` output lets the user run `command` with no password. Rules
 * are read in order and the last one that matches decides, as sudo does. A
 * `NOPASSWD:` tag holds for the commands after it on the same line until a
 * `PASSWD:` tag, and `!command` takes a command away. `sudo -l <command>` is not
 * used: it succeeds for a command that still asks for a password.
 */
export function sudoersAllows(listing, command) {
  let allowed = false;
  for (const raw of listing.split('\n')) {
    const runas = /^\(([^)]*)\)\s*/.exec(raw.trim());
    // pause.mjs runs the commands as root.
    if (!runas || !runas[1].split(':')[0].split(',').some((u) => ['root', 'ALL'].includes(u.trim()))) continue;
    const line = raw.trim().slice(runas[0].length);
    let noPassword = false;
    for (let token of line.split(',').map((t) => t.trim())) {
      // Options such as CWD=* come before the tags.
      token = token.replace(/^([A-Z_]+=\S+\s+)+/, '');
      for (;;) {
        const tag = /^([A-Z_]+):\s*/.exec(token);
        if (!tag) break;
        if (tag[1] === 'NOPASSWD') noPassword = true;
        else if (tag[1] === 'PASSWD') noPassword = false;
        token = token.slice(tag[0].length);
      }
      const negated = token.startsWith('!');
      const rule = negated ? token.slice(1).trim() : token;
      if (rule === 'ALL' || globToRegExp(rule).test(command)) allowed = !negated && noPassword;
    }
  }
  return allowed;
}

function checkUnits({ unitsDir, home, exec }, out) {
  const installed = path.join(home, '.config', 'systemd', 'user');
  const units = fs.readdirSync(unitsDir).filter((f) => /\.(service|timer)$/.test(f)).sort();
  let reachable = true;
  for (const unit of units) {
    if (!fs.existsSync(path.join(installed, unit))) {
      out('unit', unit, false,
        `missing; copy local/systemd/${unit} to ~/.config/systemd/user/ and run systemctl --user daemon-reload`);
      continue;
    }
    if (!reachable) continue;
    // A template is asked about through an instance of it.
    const name = unit.replace('@.', '@check.');
    const load = exec('systemctl', ['--user', 'show', '-p', 'LoadState', '--value', name]);
    if (load.status !== 0) {
      reachable = false;
      out('unit', unit, false, 'systemd-user-manager-unreachable');
      continue;
    }
    const loaded = load.stdout.trim() === 'loaded';
    out('unit', unit, loaded, loaded ? 'installed' : 'not-loaded; run systemctl --user daemon-reload');
    if (loaded && unit.endsWith('.timer')) {
      const enabled = exec('systemctl', ['--user', 'is-enabled', unit]).stdout.trim() === 'enabled';
      out('timer', unit, enabled, enabled ? 'enabled' : `not-enabled; run systemctl --user enable --now ${unit}`);
    }
  }
}

/** Checks the env file and returns its PATH, or null, for the release check. */
function checkEnv({ home }, out) {
  const file = path.join(home, '.config', 'build-pack', 'env');
  let env;
  try {
    env = parseEnvFile(fs.readFileSync(file, 'utf8'));
  } catch {
    out('env', '~/.config/build-pack/env', false, 'missing');
    return null;
  }
  for (const name of REQUIRED_ENV) {
    if (!env.has(name) || !env.get(name)) out('env', name, false, 'not-set');
    else {
      const found = isFile(env.get(name), fs.accessSync);
      out('env', name, found, found ? 'present' : 'file-not-found');
    }
  }
  if (!env.has('PATH')) out('env', 'PATH', false, 'not-set; systemd does not pass the login PATH');
  return env.get('PATH') ?? null;
}

/** What `sudo -n -l` prints for this user; empty when sudo cannot list. */
export function sudoListing(exec = defaultExec) {
  return exec('sudo', ['-n', '-l']).stdout;
}

/** The verbs of `verbs` that `listing` does not let the user run on `unit` with no password. */
export function sudoersRefused(listing, unit, verbs) {
  return verbs.filter((verb) => !sudoersAllows(listing, `/usr/bin/systemctl ${verb} ${unit}`));
}

/** The verdict a line shows; a `warn` verdict is advice and passes. */
const WARN = 'warn';

const checkLine = (area, name, pass, code) => `${area}  ${name}  ${pass === WARN ? WARN : pass ? 'pass' : 'fail'}  ${code}`;

function checkPause({ exec }, config, out) {
  const { units: patterns, scope } = config.pause;
  const user = scope === 'user';
  let listing;
  for (const pattern of patterns) {
    // A unit that other units refer to but that is not installed lists as `not-found`.
    const names = (result) => [...new Set(result.stdout.split('\n').map((l) => l.trim().split(/\s+/))
      .filter(([u, load]) => UNIT_NAME.test(u ?? '') && load !== 'not-found').map(([u]) => u))];
    const scopeArgs = user ? ['--user'] : [];
    // `--` keeps a pattern from being read as an option. A unit systemd generates has
    // no file, so a pattern with no match among the files is tried among loaded units.
    let listed = exec('systemctl', [...scopeArgs, 'list-unit-files', '--plain', '--no-legend', '--', pattern]);
    let units = listed.status === 0 ? names(listed) : [];
    if (!units.length) {
      listed = exec('systemctl', [...scopeArgs, 'list-units', '--all', '--plain', '--no-legend', '--', pattern]);
      units = listed.status === 0 ? names(listed) : [];
    }
    if (!units.length) {
      out('pause', pattern, false, `missing; scope ${scope}`);
      continue;
    }
    listing ??= user ? '' : sudoListing(exec);
    for (const unit of units) {
      if (user) {
        out('pause', unit, true, 'found; scope user');
        continue;
      }
      const refused = sudoersRefused(listing, unit, ['stop', 'start']);
      out('pause', unit, !refused.length,
        refused.length ? `sudoers-refused ${refused.join(' ')}` : 'found; sudoers allows stop and start');
    }
  }
}

/**
 * The lines of the setup check's pause section that fail, for a check that
 * runs before a job. A host with no `pause.units` reads nothing, and the user
 * scope never calls sudo.
 */
export function pauseFailures(config, { exec = defaultExec } = {}) {
  const lines = [];
  checkPause({ exec }, config, (area, name, pass, code) => {
    if (!pass) lines.push(checkLine(area, name, pass, code));
  });
  // Two patterns can name one unit.
  return [...new Set(lines)];
}

async function checkModel({ fetchImpl }, config, out) {
  const { endpoint, name } = config.model;
  let reply;
  try {
    reply = await fetchImpl(`${localEndpoint(endpoint)}/models`,
      { redirect: 'error', signal: AbortSignal.timeout(5000) });
  } catch {
    out('model', endpoint, false, 'unreachable');
    return;
  }
  if (!reply.ok) {
    out('model', endpoint, false, `answered-${reply.status}`);
    return;
  }
  let listed;
  try {
    listed = (await reply.json()).data?.map((m) => m.id) ?? [];
  } catch {
    out('model', endpoint, false, 'no-model-list');
    return;
  }
  const found = listed.includes(name);
  out('model', name, found, found ? 'listed' : 'not-listed');
  if (found) await checkThinkingBudget({ fetchImpl }, config, out);
}

/**
 * The least room, in tokens, a thinking step's output budget keeps above the thinking
 * budget for its answer before the setup check warns. The largest answer seen after a
 * call used its whole thinking budget was about 2,230 tokens.
 */
export const ANSWER_ROOM = 2300;

/**
 * The server-wide thinking budget in a model's `llamacpp_args`: the value of the last
 * `--reasoning-budget N` or `--reasoning-budget=N`, as the server reads a repeated flag.
 * Quoted text, such as the budget's message, is never read as a flag. Null when the flag
 * is absent or its value is not above zero, since 0 turns thinking off and -1 sets no limit.
 */
export function thinkingBudget(args) {
  const bare = String(args ?? '').replace(/"[^"]*"|'[^']*'/g, ' ');
  const flags = [...bare.matchAll(/(?:^|\s)--reasoning-budget(?:\s+|=)(-?\d+)(?=\s|$)/g)];
  const value = flags.length ? Number(flags.at(-1)[1]) : 0;
  return value > 0 ? value : null;
}

/**
 * Each thinking step whose output budget keeps less than ANSWER_ROOM tokens above
 * `budget`, the thinking budget, as `{ step, outputBudget, room }`. A step's output
 * budget is the one its calls are sent with.
 */
export function shortThinkingSteps(config, budget) {
  return Object.keys(REASONING_STEPS).map((key) => {
    const [phase, step] = key.split('.');
    const outputBudget = outputCap({ config }, phase, true, step);
    return { step: key, outputBudget, room: outputBudget - budget };
  }).filter((entry) => entry.room < ANSWER_ROOM);
}

/**
 * Reads the thinking budget saved for the model and warns when none is set, when it
 * cannot be read, and for each thinking step it leaves too little room to answer.
 * Every line here passes or warns: a host runs without the budget, only slower.
 */
async function checkThinkingBudget({ fetchImpl }, config, out) {
  const { endpoint, name } = config.model;
  let options;
  try {
    const reply = await fetchImpl(`${localEndpoint(endpoint)}/models/${encodeURIComponent(name)}`,
      { redirect: 'error', signal: AbortSignal.timeout(5000) });
    options = reply.ok ? (await reply.json())?.recipe_options : null;
  } catch {
    options = null;
  }
  if (!options || typeof options !== 'object') {
    out('thinking-budget', name, WARN, 'not-read');
    return;
  }
  const budget = thinkingBudget(options.llamacpp_args);
  if (!budget) {
    out('thinking-budget', name, WARN, 'not-set');
    return;
  }
  out('thinking-budget', name, true, `set ${budget}`);
  for (const { step, outputBudget, room } of shortThinkingSteps(config, budget)) {
    out('thinking-budget', step, WARN, `answer-room ${room}; output budget ${outputBudget}, needs ${budget + ANSWER_ROOM}`);
  }
}

function checkRelease(config, envPath, out) {
  const [program] = config.release.command;
  // The unit runs with the env file's PATH, not the login shell's.
  if (!program) {
    out('release', 'off', true, 'command-empty');
    return;
  }
  const found = onPath(program, envPath ?? process.env.PATH);
  out('release', program, found, found ? 'found' : 'not-found-on-PATH');
}

/**
 * Checks this host. Returns the lines and whether every check passed; a `warn`
 * line leaves that true. The release command is looked up, never run: running
 * it would unload a model another job may be using.
 */
export async function setupCheck(config, { exec = defaultExec, fetchImpl = localFetch,
  home = os.homedir(), unitsDir = path.join(HERE, 'systemd') } = {}) {
  const lines = [];
  let ok = true;
  const out = (area, name, pass, code) => {
    ok &&= Boolean(pass);
    lines.push(checkLine(area, name, pass, code));
  };
  checkUnits({ unitsDir, home, exec }, out);
  const envPath = checkEnv({ home }, out);
  checkPause({ exec }, config, out);
  await checkModel({ fetchImpl }, config, out);
  checkRelease(config, envPath, out);
  return { lines, ok };
}
