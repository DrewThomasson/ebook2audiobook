// The ALM session the skills share: sign in, carry the cookies, sign out, and
// the reads and writes they make with it.
//
// ALM answers a sign-in with two cookies and wants both on every later call,
// so a session is an object rather than a bare fetch. The username comes from
// the first set variable in usernameEnvs and the password from ALM_PASSWORD,
// which is blank on a server that needs none. Call configure() first.

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import dotenv from 'dotenv';
import { almEntities } from './alm-text.mjs';

// The server, domain and project are set once by configure() before any call;
// the values are live bindings, so a module that imports them sees the update.
export let BASE = '';
export let DOMAIN = '';
export let PROJECT = '';
let usernameEnvs = ['ALM_USERNAME'];

/**
 * Names the ALM server a caller works against.
 *
 * @param options.base The server root, up to and including /qcbin.
 * @param options.domain The ALM domain.
 * @param options.project The ALM project.
 * @param options.usernameEnvs Environment variables that may hold the username,
 *   first match wins; the first is named in the message when none is set.
 */
export function configure(options) {
  BASE = options.base;
  DOMAIN = options.domain;
  PROJECT = options.project;
  if (options.usernameEnvs?.length) usernameEnvs = options.usernameEnvs;
}

/**
 * Exit 2 says the server was never reached, which is a different answer from
 * the ones exit 1 carries: a refused sign-in, a missing username, a number
 * this project does not hold.
 */
export class Unreachable extends Error {
  constructor(url, cause) {
    const reason = cause?.cause?.code ?? cause?.code ?? cause?.message ?? 'no reason given';
    super(`ALM unreachable at ${url} (${reason})`);
    this.name = 'Unreachable';
  }
}

const RETRY_PAUSE_MS = 3000;

function errorCode(error) {
  return error?.cause?.code ?? error?.code;
}

// The first call of a session can time out connecting to a server that answers
// the same call a moment later, so that failure earns one more try. A connect
// timeout means nothing was sent, which makes the retry safe for a write too.
// A reset can land after the server took the request, so only a read retries
// it; a write that resets throws, and the caller reads ALM back before sending
// again.
function retryable(error, method) {
  const code = errorCode(error);
  if (code === 'UND_ERR_CONNECT_TIMEOUT') return true;
  return code === 'ECONNRESET' && (method === 'GET' || method === 'HEAD');
}

// The main checkout holds the one .env. A worktree has a root of its own, so
// the credentials sit a tree away from the script running in it.
function mainCheckoutRoot(repoRoot) {
  try {
    const gitDir = execFileSync(
      'git',
      ['rev-parse', '--path-format=absolute', '--git-common-dir'],
      { cwd: repoRoot, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] },
    ).trim();
    return gitDir ? path.dirname(gitDir) : null;
  } catch {
    return null;
  }
}

/**
 * Loads the .env holding the ALM credentials and says where it looked.
 *
 * @param repoRoot The tree the caller is running in.
 */
export function loadEnv(repoRoot) {
  const candidates = [repoRoot, mainCheckoutRoot(repoRoot)]
    .filter(Boolean)
    .map((root) => path.resolve(root, '.env'));
  const found = candidates.find((candidate) => fs.existsSync(candidate));
  if (found) dotenv.config({ path: found });

  return { candidates, found };
}

export class Session {
  constructor() {
    this.cookies = new Map();
    this.username = null;
  }

  cookieHeader() {
    return [...this.cookies].map(([k, v]) => `${k}=${v}`).join('; ');
  }

  absorb(response) {
    for (const line of response.headers.getSetCookie()) {
      const [pair] = line.split(';');
      const eq = pair.indexOf('=');
      if (eq > 0) this.cookies.set(pair.slice(0, eq).trim(), pair.slice(eq + 1).trim());
    }
  }

  async request(url, init = {}) {
    const headers = { ...(init.headers ?? {}) };
    const cookie = this.cookieHeader();
    if (cookie) headers.Cookie = cookie;

    // A read needs the two session cookies and nothing else. A write is turned
    // down with a 401 unless it also echoes the XSRF cookie back as a header,
    // and the message names the token rather than the request, so the echo
    // belongs here where every write picks it up.
    const method = (init.method ?? 'GET').toUpperCase();
    const xsrf = this.cookies.get('XSRF-TOKEN');
    if (xsrf && method !== 'GET' && method !== 'HEAD') headers['X-XSRF-TOKEN'] = xsrf;

    const send = () => fetch(url, { ...init, headers, redirect: 'manual' });
    let response;
    try {
      try {
        response = await send();
      } catch (error) {
        if (!retryable(error, method)) throw error;
        process.stderr.write(
          `alm-client: ${errorCode(error)} on ${method} ${url}, ` +
            `retrying once in ${RETRY_PAUSE_MS / 1000} s\n`,
        );
        await new Promise((resolve) => setTimeout(resolve, RETRY_PAUSE_MS));
        response = await send();
      }
    } catch (error) {
      // Off the work network the server does not resolve at all. Throwing
      // rather than exiting carries the reason up to the caller, which prints
      // a plain sentence rather than a stack trace, and leaves the logout free
      // to fail quietly.
      throw new Unreachable(url, error);
    }
    this.absorb(response);
    return response;
  }

  /** A path under the project, e.g. `defects/9154`. */
  projectUrl(suffix) {
    return `${BASE}/rest/domains/${DOMAIN}/projects/${PROJECT}/${suffix}`;
  }
}

/**
 * Signs in and leaves the session holding both cookies ALM wants.
 *
 * @param session The session to sign in.
 * @param fail How the caller reports a refusal and stops.
 */
export async function login(session, fail) {
  const username = usernameEnvs.map((name) => process.env[name]).find(Boolean);
  const password = process.env.ALM_PASSWORD ?? '';
  if (!username) fail(`set ${usernameEnvs[0]} in .env`);

  const credentials = Buffer.from(`${username}:${password}`).toString('base64');
  const response = await session.request(`${BASE}/authentication-point/authenticate`, {
    method: 'POST',
    headers: { Authorization: `Basic ${credentials}` },
  });

  if (response.status === 401) {
    fail(
      'ALM refused the username and password (401). If the account signs in through ' +
        'single sign-on, Basic authentication will not work and an API key is needed instead.',
    );
  }
  if (!response.ok) fail(`authenticate returned ${response.status}`);
  if (!session.cookies.has('LWSSO_COOKIE_KEY')) {
    fail(
      'authenticate answered without an LWSSO_COOKIE_KEY cookie, so the sign-in did not ' +
        'take. The server redirects to a port 0 URL when its site URL is misconfigured.',
    );
  }

  const siteSession = await session.request(`${BASE}/rest/site-session`, { method: 'POST' });
  if (siteSession.status !== 201 && !siteSession.ok) {
    fail(`site-session returned ${siteSession.status}`);
  }
  if (!session.cookies.has('QCSession')) fail('site-session answered without a QCSession cookie');

  session.username = username;
  return username;
}

export async function logout(session) {
  try {
    await session.request(`${BASE}/rest/site-session`, { method: 'DELETE' });
    await session.request(`${BASE}/authentication-point/logout`);
  } catch {
    // A session left open times out on its own; a failed logout is not worth a
    // non-zero exit when the work itself succeeded.
  }
}

export function xmlEscape(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * An entity body as the XML ALM's create and update read.
 *
 * A read answers in JSON, and a write takes XML: a JSON body reaches the
 * create with no fields on it at all, and it answers that the short
 * description is missing however much of one the body carries. Escaping here
 * is what keeps an angle bracket in a value from reaching ALM as a tag.
 *
 * @param fields Field name to value. A value that is null, undefined or empty
 *   is left out of the body, unless `clear` is set.
 * @param type The entity type, `defect` or `requirement`.
 * @param options.clear An empty value goes in as an empty Value, which an
 *   update reads as clearing the field.
 */
export function entityXml(fields, type = 'defect', { clear = false } = {}) {
  const isEmpty = (value) => value === null || value === undefined || value === '';
  const rows = Object.entries(fields)
    .filter(([, value]) => clear || !isEmpty(value))
    .map(([name, value]) => `<Field Name="${xmlEscape(name)}">`
      + `<Value>${isEmpty(value) ? '' : xmlEscape(value)}</Value></Field>`);

  return '<?xml version="1.0" encoding="UTF-8"?>'
    + `<Entity Type="${xmlEscape(type)}"><Fields>${rows.join('')}</Fields></Entity>`;
}

/** The text of an ALM description, which ALM holds as an HTML fragment. */
export function stripHtml(html) {
  if (!html) return '';
  const entities = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' };
  return html
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<[^>]+>/g, '')
    // One pass, so the text of an entity, such as &amp;#60;, is not decoded twice.
    .replace(/&(?:(amp|lt|gt|quot|apos|nbsp)|#(\d+)|#x([0-9a-f]+));/gi, (_, name, dec, hex) =>
      (name ? entities[name.toLowerCase()]
        : String.fromCodePoint(dec ? Number(dec) : parseInt(hex, 16))))
    .replace(/\s+/g, ' ')
    .trim();
}

export { ALM_UNSTORABLE, almEntities, unstorableProblem } from './alm-text.mjs';

/** Plain text as the HTML fragment an ALM description holds. */
export function htmlDescription(text) {
  return `<html><body>${almEntities(xmlEscape(text ?? ''))}</body></html>`;
}

/** An entity from a JSON read as field name to its list of values, empty values dropped. */
export function entityValues(entity) {
  return new Map((entity.Fields ?? []).map((field) => [
    field.Name,
    (field.values ?? []).map((v) => v.value).filter((v) => v !== undefined && v !== ''),
  ]));
}

/** One value of an entity read by `entityValues`, or '' when it has none. */
export function fieldValue(entity, name) {
  return entity.get(name)?.[0] ?? '';
}

async function failedCall(response, what) {
  const reason = refusalTitle(await response.text(), 200);
  return new Error(`${what} returned ${response.status}: ${reason}`);
}

/** A GET under the project, answered in JSON. */
export async function getJson(session, suffix) {
  const response = await session.request(session.projectUrl(suffix), {
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) throw await failedCall(response, suffix);
  return response.json();
}

// ALM can return fewer rows than the page size asked for, so each page starts
// after the rows read so far.
const QUERY_PAGE_SIZE = 1000;

// Every entity of one collection a query matches, read page by page.
async function queryCollection(session, collection, query, fields) {
  const encoded = encodeURIComponent(`{${query}}`);
  const only = fields ? `&fields=${fields.join(',')}` : '';
  const rows = [];
  for (;;) {
    const page = await getJson(
      session,
      `${collection}?query=${encoded}${only}`
        + `&page-size=${QUERY_PAGE_SIZE}&start-index=${rows.length + 1}`,
    );
    rows.push(...(page.entities ?? []).map(entityValues));
    if (!page.entities?.length || rows.length >= page.TotalResults) return rows;
  }
}

/**
 * Every requirement a query matches.
 *
 * @param query The query without its braces, such as `parent-id[1010]`.
 */
export async function queryRequirements(session, query) {
  return queryCollection(session, 'requirements', query);
}

/**
 * Every defect a query matches, holding only the fields named.
 *
 * @param query The query without its braces, such as `project["RFI"]`.
 * @param fields The field names to read, such as `['id', 'name']`.
 */
export async function queryDefects(session, query, fields) {
  return queryCollection(session, 'defects', query, fields);
}

/**
 * Every entity of one collection a query matches, such as `test-folders`.
 *
 * @param query The query without its braces, such as `parent-id[2]`.
 * @param fields The field names to read, or undefined for every field.
 */
export async function queryEntities(session, collection, query, fields) {
  return queryCollection(session, collection, query, fields);
}

/**
 * Creates an entity and answers its id.
 *
 * @param collection Where it is posted, such as `tests`.
 * @param type The entity type the body names, such as `test`.
 */
export async function createEntity(session, collection, type, fields) {
  const response = await session.request(session.projectUrl(collection), {
    method: 'POST',
    headers: { 'Content-Type': 'application/xml', Accept: 'application/json' },
    body: entityXml(fields, type),
  });
  // A coverage link or a test instance has no name, so its ids say which one it is.
  const label = fields.name ?? Object.entries(fields).filter(([key]) => key.endsWith('-id'))
    .map(([key, value]) => `${key} ${value}`).join(', ');
  const what = `creating ${type} "${label}"`;
  if (!response.ok) throw await failedCall(response, what);
  const id = fieldValue(entityValues(await response.json()), 'id');
  if (!id) throw new Error(`ALM finished ${what} but answered without its id`);
  return Number(id);
}

/**
 * The required fields of an entity type that a create leaves for ALM to fill.
 *
 * @param type The entity type, such as `requirement` or `test`.
 * @param written The fields the create writes.
 */
export async function requiredFieldsLeftEmpty(session, type, written) {
  const body = await getJson(session, `customization/entities/${type}/fields`);
  const filled = new Set(['id', ...written]);
  return [].concat(body?.Fields?.Field ?? body?.Field ?? [])
    .filter((field) => (field.Required ?? field.required) === true)
    .map((field) => field.Name ?? field.name)
    .filter((name) => !filled.has(name));
}

/** One requirement, or null when ALM holds no requirement with that id. */
export async function getRequirement(session, id) {
  const response = await session.request(session.projectUrl(`requirements/${id}`), {
    headers: { Accept: 'application/json' },
  });
  if (response.status === 404) return null;
  if (!response.ok) throw await failedCall(response, `requirements/${id}`);
  return entityValues(await response.json());
}

/**
 * Creates a requirement and answers its id.
 *
 * @param fields The fields to write, `parent-id` and `type-id` among them.
 */
export async function createRequirement(session, fields) {
  const response = await session.request(session.projectUrl('requirements'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/xml', Accept: 'application/json' },
    body: entityXml(fields, 'requirement'),
  });
  if (!response.ok) throw await failedCall(response, `creating requirement "${fields.name}"`);
  const id = fieldValue(entityValues(await response.json()), 'id');
  if (!id) throw new Error(`ALM created "${fields.name}" but answered without its id`);
  return Number(id);
}

/** A requirement folder is a requirement of type 1. */
export const REQUIREMENT_FOLDER_TYPE = 1;

/** Creates a requirement folder under a parent folder and answers its id. */
export async function createRequirementFolder(session, parentId, name) {
  return createRequirement(session, {
    name, 'parent-id': parentId, 'type-id': REQUIREMENT_FOLDER_TYPE,
  });
}

/** Writes fields onto a requirement that already exists; an empty value clears its field. */
export async function putRequirement(session, id, fields) {
  const response = await session.request(session.projectUrl(`requirements/${id}`), {
    method: 'PUT',
    headers: { 'Content-Type': 'application/xml', Accept: 'application/json' },
    body: entityXml(fields, 'requirement', { clear: true }),
  });
  if (!response.ok) throw await failedCall(response, `updating requirement ${id}`);
}

/** The names of the files attached to a requirement, each with its attachment id. */
export async function requirementAttachments(session, id) {
  const body = await getJson(session, `requirements/${id}/attachments`);
  return (body.entities ?? []).map(entityValues).map((entity) => ({
    id: Number(fieldValue(entity, 'id')),
    name: fieldValue(entity, 'name'),
  }));
}

function attachmentUrl(session, id, name) {
  return session.projectUrl(`requirements/${id}/attachments/${encodeURIComponent(name)}`);
}

/** The bytes of a file attached to a requirement. */
export async function downloadRequirementAttachment(session, id, name) {
  const response = await session.request(attachmentUrl(session, id, name), {
    headers: { Accept: 'application/octet-stream' },
  });
  if (!response.ok) throw await failedCall(response, `reading attachment "${name}"`);
  return Buffer.from(await response.arrayBuffer());
}

/**
 * Attaches a file to a requirement. ALM takes the file name from the Slug
 * header and the content as the raw body.
 */
export async function uploadRequirementAttachment(session, id, name, bytes) {
  const response = await session.request(session.projectUrl(`requirements/${id}/attachments`), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/octet-stream', Slug: name, Accept: 'application/json',
    },
    body: bytes,
  });
  if (!response.ok) throw await failedCall(response, `attaching "${name}"`);
}

/** Replaces the content of a file already attached to a requirement, keeping its name. */
export async function replaceRequirementAttachment(session, id, name, bytes) {
  const response = await session.request(attachmentUrl(session, id, name), {
    method: 'PUT',
    headers: { 'Content-Type': 'application/octet-stream', Accept: 'application/json' },
    body: bytes,
  });
  if (!response.ok) throw await failedCall(response, `replacing attachment "${name}"`);
}

/**
 * The one line out of an ALM refusal that says what it turned down.
 *
 * ALM answers a refusal with its own stack trace, which buries that line.
 */
export function refusalTitle(text, limit = 400) {
  const title = /"Title":"([^"]+)"/.exec(text) ?? /<Title>([^<]+)<\/Title>/.exec(text);

  return title ? title[1] : text.slice(0, limit);
}

/**
 * Writes fields onto a defect that already exists.
 *
 * @returns null when ALM took it, or the status and ALM's reason when it did
 *   not.
 */
export async function putDefect(session, id, fields) {
  const response = await session.request(session.projectUrl(`defects/${id}`), {
    method: 'PUT',
    headers: { 'Content-Type': 'application/xml', Accept: 'application/xml' },
    body: entityXml(fields),
  });
  if (response.ok) return null;

  return `${response.status}: ${refusalTitle(await response.text(), 200)}`;
}

/**
 * The values each lookup field will accept, keyed by the field's own name.
 *
 * A create refuses a value the project's list does not hold, and answers with
 * a message that names neither the field nor the value, so the check belongs
 * here where it can say both.
 *
 * @param session A signed-in session.
 */
export async function lookupValues(session) {
  const fields = await session.request(
    session.projectUrl('customization/entities/defect/fields'),
    { headers: { Accept: 'application/json' } },
  );
  const fieldBody = await fields.json();
  const listIdByField = new Map();
  const requiredFields = [];
  for (const field of [].concat(fieldBody?.Fields?.Field ?? fieldBody?.Field ?? [])) {
    const name = field?.Name ?? field?.name;
    const listId = field?.['List-Id'] ?? field?.listId;
    if (name && listId) listIdByField.set(name, String(listId));
    if (name && (field?.Required ?? field?.required) === true) requiredFields.push(name);
  }

  const lists = await session.request(session.projectUrl('customization/used-lists'), {
    headers: { Accept: 'application/json' },
  });
  const listBody = await lists.json();
  const valuesByList = new Map();
  for (const list of [].concat(listBody?.lists ?? listBody?.Lists?.List ?? listBody?.List ?? [])) {
    const id = String(list?.id ?? list?.Id ?? '');
    const items = [].concat(list?.Items ?? list?.items ?? []);
    valuesByList.set(id, items.map((item) => item?.value ?? item?.Value).filter(Boolean));
  }

  const byField = new Map();
  for (const [name, listId] of listIdByField) {
    const values = valuesByList.get(listId);
    if (values && values.length > 0) byField.set(name, values);
  }

  return { byField, requiredFields };
}
