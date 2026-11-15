// A stand-in for the ALM server, loaded with `node --import` ahead of a SIR
// script so the script runs end to end without the work network.
//
// ALM_STUB picks the failure:
//   timeout-first  the first call fails with UND_ERR_CONNECT_TIMEOUT
//   reset-login    the sign-in POST fails with ECONNRESET, every time
//   reset-put      a defect PUT fails with ECONNRESET, with ALM_STUB_STATE set
//
// Every call is logged to stderr as `alm-stub: <method> <path>` so a test can
// count the attempts.

import fs from 'node:fs';

const mode = process.env.ALM_STUB ?? '';
let calls = 0;

// With ALM_STUB_STATE naming a JSON file of { fields: { name: value } }, the
// stub serves that one defect, applies a PUT to it, and saves it back, so a
// write in one run reads back in the next. It also answers the field metadata,
// the lookup lists, the users and the lock the update path asks for.
const state = process.env.ALM_STUB_STATE;

const FIELDS = [
  { name: 'user-06', type: 'LookupList', listId: 1, editable: true },
  { name: 'owner', type: 'UsersList', editable: true },
  { name: 'name', type: 'String', size: 255, editable: true },
  { name: 'description', type: 'Memo', editable: true },
  { name: 'dev-comments', type: 'Memo', editable: true },
  { name: 'id', type: 'Number', editable: false },
];
const LISTS = [{ id: 1, Name: 'SIR Status', Items: [{ value: 'Draft' }, { value: 'Withdrawn' }] }];
const USERS = { 'stub-user': 'Stub User' };

function unescapeXml(value) {
  return value.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"')
    .replace(/&amp;/g, '&');
}

function stateful(method, pathname, body) {
  const saved = JSON.parse(fs.readFileSync(state, 'utf8'));
  if (pathname.endsWith('/customization/entities/defect/fields')) {
    return reply(200, { Fields: { Field: FIELDS } });
  }
  if (pathname.endsWith('/customization/used-lists')) return reply(200, { lists: LISTS });
  const who = pathname.match(/\/customization\/users\/([^/]+)$/);
  if (who) {
    const login = decodeURIComponent(who[1]).toLowerCase();
    return USERS[login] ? reply(200, { Name: login, FullName: USERS[login] }) : reply(404, {});
  }
  if (/\/defects\/\d+\/lock$/.test(pathname)) {
    return reply(200, { LockStatusEntity: { LockStatus: 'UNLOCKED' } });
  }
  if (!/\/defects\/\d+$/.test(pathname)) return null;

  if (method === 'PUT') {
    if (mode === 'reset-put') throw networkError('ECONNRESET');
    for (const [, name, value] of String(body).matchAll(
      /<Field Name="([^"]+)"><Value>([\s\S]*?)<\/Value><\/Field>/g,
    )) {
      saved.fields[name] = unescapeXml(value);
    }
    saved.fields['ver-stamp'] = String(Number(saved.fields['ver-stamp']) + 1);
    fs.writeFileSync(state, JSON.stringify(saved));
    return reply(200, {});
  }

  return reply(200, {
    Fields: Object.entries(saved.fields).map(([Name, value]) => ({ Name, values: [{ value }] })),
  });
}

function networkError(code) {
  return new TypeError('fetch failed', { cause: Object.assign(new Error(code), { code }) });
}

function reply(status, body, cookies = []) {
  const headers = new Headers({ 'Content-Type': 'application/json' });
  for (const cookie of cookies) headers.append('Set-Cookie', `${cookie}; Path=/`);
  return new Response(body === null ? null : JSON.stringify(body), { status, headers });
}

globalThis.fetch = async (url, init = {}) => {
  calls += 1;
  const method = (init.method ?? 'GET').toUpperCase();
  const { pathname } = new URL(url);
  process.stderr.write(`alm-stub: ${method} ${pathname}\n`);

  if (mode === 'timeout-first' && calls === 1) throw networkError('UND_ERR_CONNECT_TIMEOUT');
  if (mode === 'reset-login' && pathname.endsWith('/authenticate')) {
    throw networkError('ECONNRESET');
  }

  if (pathname.endsWith('/authentication-point/authenticate')) {
    return reply(200, null, ['LWSSO_COOKIE_KEY=stub']);
  }
  if (pathname.endsWith('/rest/site-session') && method === 'POST') {
    return reply(201, null, ['QCSession=stub', 'XSRF-TOKEN=stub']);
  }
  if (state) {
    const answer = stateful(method, pathname, init.body);
    if (answer) return answer;
  }
  const defect = pathname.match(/\/defects\/(\d+)$/);
  if (defect) {
    return reply(200, {
      Fields: [
        { Name: 'id', values: [{ value: defect[1] }] },
        { Name: 'name', values: [{ value: 'Stubbed SIR' }] },
      ],
    });
  }
  return reply(200, {});
};
