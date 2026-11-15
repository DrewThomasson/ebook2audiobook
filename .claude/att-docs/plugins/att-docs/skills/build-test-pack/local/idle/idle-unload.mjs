// Unloads the local model from Lemonade after it has sat idle. A systemd timer
// runs this once a minute. It has no imports from the rest of the pipeline, so
// the copy installed under /usr/local/lib needs nothing beside it.
//
// Lemonade keeps a model's memory until the model is unloaded and has no idle
// timeout of its own. Each run asks Lemonade which models are loaded, asks the
// llama.cpp server behind each one for its slots, and keeps a saved record of
// when anything last moved. A slot that is processing a request counts as
// activity, so a request that runs longer than the timeout is never cut off.
// The next request loads the model again through Lemonade's auto-load.
//
// Each loaded model is tracked on its own. A model without llama.cpp slots is
// left alone, and the journal gets one line per run naming it and the reason.
//
// IDLE_MINUTES sets the timeout (default 15). LEMONADE_URL sets the API base
// (default http://127.0.0.1:13305/api/v1). LEMONADE_API_KEY, when set, is sent
// as a bearer token to Lemonade (not to the model servers). The record is a
// JSON file in $STATE_DIRECTORY, which systemd sets from StateDirectory=.

import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

/** Hosts the API and the model servers may name. Anything else could be a cloud API. */
export const LOOPBACK_HOSTS = ['localhost', '127.0.0.1', '[::1]', '::1'];

export const DEFAULT_MINUTES = 15;
export const DEFAULT_BASE = 'http://127.0.0.1:13305/api/v1';
const STATE_FILE = 'state.json';

/** The URL without a trailing slash, or an error when it is not on this machine. */
export function loopbackUrl(value, what) {
  let url;
  try {
    url = new URL(value);
  } catch {
    throw new Error(`${what} "${value}" is not a URL`);
  }
  if (!['http:', 'https:'].includes(url.protocol) || !LOOPBACK_HOSTS.includes(url.hostname)) {
    throw new Error(`${what} must be a loopback address (localhost, 127.0.0.1 or ::1)`);
  }
  return url.href.replace(/\/+$/, '');
}

/** The timeout in minutes: the default when unset, an error unless a positive whole number. */
export function parseMinutes(value) {
  if (value === undefined || value === '') return DEFAULT_MINUTES;
  if (!/^[1-9][0-9]*$/.test(String(value).trim())) {
    throw new Error(`IDLE_MINUTES must be a positive whole number, got "${value}"`);
  }
  return Number(String(value).trim());
}

// A read of the server's status: GET only, no redirects, a short timeout. A
// rejected fetch (nothing listening, timed out) passes through unchanged; an
// HTTP status other than ok throws an error carrying it as `status`.
async function getJson(fetchImpl, url, headers = {}) {
  const reply = await fetchImpl(url, { redirect: 'error', headers, signal: AbortSignal.timeout(5000) });
  if (reply.ok === false) throw Object.assign(new Error(`${url} answered ${reply.status}`), { status: reply.status });
  return reply.json();
}

/** True for a loaded-model entry with llama.cpp slots to read. Others are left alone. */
function hasSlots(entry) {
  return entry !== null && typeof entry === 'object' && typeof entry.model_name === 'string' &&
    typeof entry.backend_url === 'string' && (entry.recipe === undefined || entry.recipe === 'llamacpp');
}

/** Why a loaded-model entry has no llama.cpp slots to read, for the journal. */
function skipReason(entry) {
  const name = entry !== null && typeof entry === 'object' && typeof entry.model_name === 'string'
    ? entry.model_name : '(unnamed entry)';
  if (name === '(unnamed entry)') return `${name} skipped: it has no model_name`;
  if (typeof entry.backend_url !== 'string') return `${name} skipped: it has no backend_url`;
  return `${name} skipped: its recipe is ${JSON.stringify(entry.recipe)}, not llamacpp`;
}

// Sets an own property even when the key is "__proto__".
function put(object, key, value) {
  Object.defineProperty(object, key, { value, enumerable: true, writable: true, configurable: true });
}
const has = (object, key) => Object.prototype.hasOwnProperty.call(object, key);

// What one loaded model is doing: busy when a slot is processing, or when the
// slots cannot be read or are not in a shape this understands. The signature
// changes whenever a slot takes a new task, which catches a request that began
// and ended between two runs. A slow /slots answer (for example during a long
// prefill) counts as unreadable, so as busy. `problem` says why the slots could
// not be understood.
export async function look(fetchImpl, entry) {
  const name = entry.model_name;
  const backend = loopbackUrl(entry.backend_url, `backend_url of ${name}`).replace(/\/v1$/, '');
  let slots;
  try {
    slots = await getJson(fetchImpl, `${backend}/slots`);
  } catch (e) {
    return { name, busy: true, signature: `${backend}|unreadable`, problem: `/slots could not be read (${e.message})` };
  }
  const known = Array.isArray(slots) && slots.length > 0 && slots.every((s) =>
    s !== null && typeof s === 'object' && typeof s.is_processing === 'boolean');
  if (!known) {
    return { name, busy: true, signature: `${backend}|unknown`, problem: '/slots is not a list of slots with is_processing' };
  }
  const signature = [backend, ...slots.map((s) => `${s.id}:${s.id_task}:${s.is_processing}`)].join('|');
  return { name, busy: slots.some((s) => s.is_processing), signature };
}

// Errors that mean Lemonade is not there to answer: nothing listening, the host
// or network unreachable, a connection closed partway through a reply, a name
// lookup that failed for now, or no reply in time.
const QUIET_CODES = ['ECONNREFUSED', 'ECONNRESET', 'EHOSTUNREACH', 'ENOTFOUND', 'ENETUNREACH',
  'EAI_AGAIN', 'UND_ERR_SOCKET'];
function lemonadeAbsent(error) {
  return QUIET_CODES.includes(error?.cause?.code) || ['TimeoutError', 'AbortError'].includes(error?.name);
}

/**
 * One run's decision. `state` is the saved record, a map of model name to
 * { signature, lastActive } (or null), and `now` is a time in milliseconds.
 * Each loaded model is judged on its own. Returns { state, unload, idle, targets,
 * notes }: the record to save, the names of the models due for an unload, for
 * each model the reason it is not being unloaded or how long it has been idle,
 * a Map from each name due for an unload to its entry and signature (for the
 * read of its slots just before its own unload), and lines for the journal about
 * models that are skipped or whose slots cannot be understood. A model name that
 * appears twice is judged once. A model that is no longer loaded drops out of
 * the record; a model without llama.cpp slots is never tracked or unloaded.
 * Lemonade being absent (see lemonadeAbsent) leaves the record as it was; any
 * other failure to read /health, an HTTP error from it, or a backend_url off
 * this machine throws.
 */
export async function tick({ fetchImpl = fetch, now, state = null, minutes = DEFAULT_MINUTES,
  base = DEFAULT_BASE, apiKey = '' }) {
  const root = loopbackUrl(base, 'Lemonade URL');
  const headers = apiKey ? { authorization: `Bearer ${apiKey}` } : {};
  let health;
  try {
    const reply = await fetchImpl(`${root}/health`,
      { redirect: 'error', headers, signal: AbortSignal.timeout(5000) });
    if (reply.ok === false) {
      throw Object.assign(new Error(`${root}/health answered ${reply.status}`), { status: reply.status });
    }
    health = await reply.json();
  } catch (error) {
    if (lemonadeAbsent(error)) return { state, unload: [], idle: {}, targets: new Map(), notes: [] };
    throw error;
  }
  const entries = health?.all_models_loaded;
  if (!Array.isArray(entries)) return { state, unload: [], idle: {}, targets: new Map(), notes: [] };

  const previous = state ?? {};
  const next = {};
  const unload = [];
  const idle = {};
  const targets = new Map();
  const notes = [];
  const seen = new Set();
  for (const entry of entries) {
    if (!hasSlots(entry)) {
      notes.push(skipReason(entry));
      continue;
    }
    if (seen.has(entry.model_name)) continue;
    seen.add(entry.model_name);
    const first = await look(fetchImpl, entry);
    const name = first.name;
    if (first.problem) notes.push(`${name}: ${first.problem}; counted as busy`);
    const before = has(previous, name) ? previous[name] : undefined;
    const changed = !before || before.signature !== first.signature || before.lastActive > now;
    if (first.busy || changed) {
      put(next, name, { signature: first.signature, lastActive: now });
      put(idle, name, first.busy ? 'busy' : 'changed');
      continue;
    }
    put(next, name, before);
    const idleMinutes = (now - before.lastActive) / 60000;
    if (idleMinutes < minutes) {
      put(idle, name, 'under timeout');
      continue;
    }
    unload.push(name);
    targets.set(name, { entry, signature: first.signature });
    put(idle, name, `${Math.floor(idleMinutes)} minutes`);
  }
  return { state: next, unload, idle, targets, notes };
}

/** Asks Lemonade to unload one model. Throws when it does not answer ok. */
export async function unloadModel({ fetchImpl = fetch, base = DEFAULT_BASE, name, apiKey = '' }) {
  const url = `${loopbackUrl(base, 'Lemonade URL')}/unload`;
  const headers = { 'content-type': 'application/json' };
  if (apiKey) headers.authorization = `Bearer ${apiKey}`;
  const reply = await fetchImpl(url, {
    method: 'POST',
    headers,
    body: JSON.stringify({ model_name: name }),
    redirect: 'error',
    signal: AbortSignal.timeout(30000),
  });
  if (reply.ok === false) throw new Error(`unload of ${name} answered ${reply.status}`);
}

// The saved record: a map of model name to { signature, lastActive }. A record
// that is not a map of model entries counts as none.
function readState(file) {
  try {
    const saved = JSON.parse(fs.readFileSync(file, 'utf8'));
    if (saved === null || typeof saved !== 'object' || Array.isArray(saved)) return null;
    const entries = Object.entries(saved).filter(([, v]) =>
      v !== null && typeof v === 'object' && typeof v.signature === 'string' && Number.isFinite(v.lastActive));
    return entries.length > 0 ? Object.fromEntries(entries) : null;
  } catch { /* no record, or one that cannot be read, starts fresh */ }
  return null;
}

function writeState(file, state) {
  if (state === null || Object.keys(state).length === 0) {
    fs.rmSync(file, { force: true });
    return;
  }
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(`${file}.tmp`, JSON.stringify(state));
  fs.renameSync(`${file}.tmp`, file);
}

/**
 * One timer run. Returns the exit code: 0 for a normal run, 1 when an unload
 * failed, /health failed in a way other than Lemonade being absent, or a model
 * server was off this machine (the record is kept), 2 for a setting that cannot be used (nothing
 * is unloaded).
 */
export async function main({ env = process.env, fetchImpl = fetch, now = Date.now(),
  log = console.log, error = console.error } = {}) {
  let minutes;
  try {
    minutes = parseMinutes(env.IDLE_MINUTES);
  } catch (e) {
    error(e.message);
    return 2;
  }
  if (!env.STATE_DIRECTORY) {
    error('STATE_DIRECTORY is not set; the service sets it from StateDirectory=');
    return 2;
  }
  const base = env.LEMONADE_URL || DEFAULT_BASE;
  const apiKey = env.LEMONADE_API_KEY || '';
  const file = path.join(env.STATE_DIRECTORY, STATE_FILE);
  let result;
  try {
    result = await tick({ fetchImpl, now, state: readState(file), minutes, base, apiKey });
  } catch (e) {
    error(e.message);
    return 1;
  }
  writeState(file, result.state);
  for (const note of result.notes) log(note);
  let code = 0;
  const kept = { ...result.state };
  for (const name of result.unload) {
    try {
      // This model's slots are read once more right before its own unload, after
      // any earlier unload has finished, which narrows the window in which a
      // request can arrive after the check.
      const target = result.targets.get(name);
      const again = await look(fetchImpl, target.entry);
      if (again.busy || again.signature !== target.signature) {
        log(`${name} was busy or changed on the last look; unload skipped`);
        put(kept, name, { signature: again.signature, lastActive: now });
        writeState(file, kept);
        continue;
      }
      await unloadModel({ fetchImpl, base, name, apiKey });
      log(`unloaded ${name} after ${result.idle[name]} idle`);
      delete kept[name];
      writeState(file, kept);
    } catch (e) {
      error(e.message);
      code = 1;
    }
  }
  return code;
}

// True when this file is the script node was started with, also when it was
// started through a symbolic link.
function isMainModule() {
  try {
    return Boolean(process.argv[1]) &&
      import.meta.url === pathToFileURL(fs.realpathSync(process.argv[1])).href;
  } catch {
    return false;
  }
}

if (isMainModule()) {
  process.exitCode = await main();
}
