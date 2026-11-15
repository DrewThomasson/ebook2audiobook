// Runs the ALM client's sign-in against the stubbed ALM in alm-stub.mjs.
//
//   node --test plugins/att-docs/shared/alm-client.test.mjs

import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUB = path.join(HERE, 'alm-stub.mjs');
const CLIENT = path.join(HERE, 'alm-client.mjs');

// Signs in through the client the way a skill's script does: configure, make a
// session, log in, and report what happened on stdout.
const SCRIPT = `
import { Session, Unreachable, configure, login, logout } from ${JSON.stringify(CLIENT)};
configure({
  base: 'https://alm.example.test/qcbin',
  domain: 'DOMAIN',
  project: 'PROJECT',
  usernameEnvs: ['TEST_ALM_USERNAME', 'ALM_USERNAME'],
});
const session = new Session();
try {
  await login(session, (message) => { throw new Error(message); });
  console.log('signed in');
  await logout(session);
} catch (error) {
  console.error(error instanceof Unreachable ? 'ALM unreachable: ' + error.message : error.message);
  process.exit(error instanceof Unreachable ? 2 : 1);
}
`;

function signIn(mode, env = {}) {
  return spawnSync(process.execPath, ['--import', STUB, '--input-type=module', '-e', SCRIPT], {
    encoding: 'utf8',
    env: { ...process.env, ALM_STUB: mode, TEST_ALM_USERNAME: 'stub-user', ...env },
  });
}

function attempts(stderr, pattern) {
  return stderr.split('\n').filter((line) => pattern.test(line)).length;
}

test('a first connect timeout is retried once and the sign-in succeeds', () => {
  const run = signIn('timeout-first');
  assert.equal(run.status, 0, run.stderr);
  assert.match(run.stderr, /alm-client: UND_ERR_CONNECT_TIMEOUT on POST .*retrying once/);
  assert.equal(attempts(run.stderr, /alm-stub: POST .*\/authenticate$/), 2);
  assert.match(run.stdout, /signed in/);
});

test('a sign-in that resets is not retried and exits 2', () => {
  const run = signIn('reset-login');
  assert.equal(run.status, 2, run.stderr);
  assert.match(run.stderr, /ECONNRESET/);
  assert.doesNotMatch(run.stderr, /retrying once/);
  assert.equal(attempts(run.stderr, /alm-stub: POST .*\/authenticate$/), 1);
});

test('the first configured username variable is named when none is set', () => {
  const run = signIn('', { TEST_ALM_USERNAME: '', ALM_USERNAME: '' });
  assert.equal(run.status, 1, run.stderr);
  assert.match(run.stderr, /set TEST_ALM_USERNAME in \.env/);
});
