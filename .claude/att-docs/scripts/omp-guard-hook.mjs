// Runs guard-main-checkout.sh on the tool calls of a session that loads extensions from
// .omp/settings.json. The shell guard reads the
// payload a PreToolUse hook gets, so each call is rewritten into that shape: a file tool
// becomes one Write payload per path it can write, and the bash tool becomes a Bash payload that
// starts in the directory its own cwd argument names. The guard's exit code 2 blocks the call.
// The harness loads this module through .omp/settings.json.
import { spawn } from 'node:child_process';
import { accessSync, constants } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const GUARD = path.join(path.dirname(fileURLToPath(import.meta.url)), 'guard-main-checkout.sh');
const GUARD_TIMEOUT_MS = 20_000;

const URL_SCHEME = /^([A-Za-z][A-Za-z0-9+.-]*):\/\//;
const UNICODE_SPACES = /[\u00A0\u1680\u2000-\u200A\u202F\u205F\u3000]/g;
// `[PATH]` or `[PATH#TAG]`, the header form a copied read result carries.
const HEADER_PATH = /^\[(.+?)(?:#[0-9A-Fa-f]{4})?\]$/;
// The edit tool's other ways to name a file: a hashline `[PATH#TAG]` or `¶PATH#TAG` header
// line, a hashline `MV DEST` row, and the section headers of its apply_patch and sloppy forms.
// The harness derives a `path` from some of these and not from others, so each is read here.
// The section headers are matched as the harness's sloppy parser matches them: any letter
// case, with the colon optional.
const TAG = '(?:#[0-9A-Fa-f]{4})?';
const HEADER_ROW = new RegExp(`^(?:\\[(.+?)${TAG}\\]|¶(.+?)${TAG})[ \\t]*\\r?$`, 'gm');
const MOVE_ROW = /^[ \t]*MV[ \t]+(.+?)[ \t]*\r?$/gm;
const PATCH_HEADER = new RegExp(
  '^[ \\t]*\\*{3}[ \\t]+(?:(?:Add|Update|Delete|Edit)[ \\t]+File|Move[ \\t]+to)' +
    '(?::|[ \\t]|$)[ \\t]*(.+?)(?: all)?[ \\t]*\\r?$',
  'gim',
);

const list = value => (Array.isArray(value) ? value : []);
const unique = values => [...new Set(values)];
const unquote = text => text.replace(/^(["'])(.*)\1$/, '$2');

// Whether a target names a place other than a file on disk, such as xd://ast_edit. A file://
// URL is a file.
const isInternalUrl = target => {
  const scheme = URL_SCHEME.exec(target)?.[1];
  return scheme !== undefined && scheme.toLowerCase() !== 'file';
};

/**
 * The path the harness resolves a tool's path argument to before it reads the cwd: a copied
 * `[path#TAG]`
 * header unwrapped, a stray leading `:` or an `@` before `/` or `~` dropped, a file:// URL turned
 * into its path, and `~` expanded.
 */
export function normalizeTarget(raw) {
  let target = raw.trim();
  const header = HEADER_PATH.exec(target);
  if (header) target = header[1];
  if (/^:(?=[/\\~]|\.\.?[/\\]|[A-Za-z]:)/.test(target)) target = target.slice(1);
  if (/^@(?:\/|~$|~\/)/.test(target)) target = target.slice(1);
  target = target.replace(UNICODE_SPACES, ' ');
  if (target.toLowerCase().startsWith('file://')) {
    try {
      target = fileURLToPath(target);
    } catch {
      // Left as written: the harness does the same when the URL does not parse.
    }
  }
  if (target === '~') return os.homedir();
  if (target.startsWith('~/')) return path.join(os.homedir(), target.slice(2));
  return target;
}

// A path argument is judged where the harness resolves it: the form normalizeTarget returns.
const targetForms = raw => [normalizeTarget(raw)].filter(t => !isInternalUrl(t));

// The path the harness's hashline parser takes from a header or `MV` row: quotes dropped, and the
// `*** Update File:` style prefix a model sometimes copies into a header removed.
const HEADER_NOISE = new RegExp(
  '^\\*{0,3}\\s*(?:(?:update|add|delete|move)[^A-Za-z0-9]*(?:file|to)?[^A-Za-z0-9]*:)?' +
    '\\s*\\*{0,3}\\s*',
  'i',
);
const headerPath = raw => unquote(raw.trim()).replace(HEADER_NOISE, '');

// The file targets inside an edit's `input` text. Text with `***` sections is an apply_patch or
// sloppy edit, whose context lines can look like a hashline header or an `MV` row.
const textTargets = text => {
  const sections = [...text.matchAll(PATCH_HEADER)].map(([, header]) => unquote(header));
  if (sections.length > 0) return sections;
  const found = [];
  for (const [, bracketed, legacy] of text.matchAll(HEADER_ROW)) {
    found.push(headerPath(bracketed ?? legacy));
  }
  for (const [, row] of text.matchAll(MOVE_ROW)) found.push(headerPath(row));
  return found;
};

// An ast_edit path entry is a list: `;`, `,` and whitespace separate patterns, and `!` marks
// an exclusion.
const patternTargets = entry =>
  [entry, ...entry.split(/[;,\s]+/)].filter(part => part && !part.startsWith('!'));

/** Every path string a tool call names as a file it writes, as the call wrote it. */
export function namedPaths(toolName, input) {
  const named = [];
  if (toolName === 'write') named.push(input.path);
  if (toolName === 'edit') {
    named.push(input.path, ...list(input.paths));
    for (const entry of list(input.edits)) named.push(entry?.path, entry?.rename);
    if (typeof input.input === 'string') named.push(...textTargets(input.input));
  }
  if (toolName === 'ast_edit') {
    for (const entry of list(input.paths)) {
      if (typeof entry === 'string') named.push(...patternTargets(entry));
    }
  }
  if (toolName === 'lsp' && ['rename', 'rename_file', 'code_actions'].includes(input.action)) {
    named.push(input.file);
    if (input.action === 'rename_file') named.push(input.new_name);
  }
  return named.filter(target => typeof target === 'string' && target.trim());
}

/** The paths the guard judges: each named path, where the harness resolves it. */
export function writtenPaths(toolName, input) {
  return unique(namedPaths(toolName, input).flatMap(targetForms));
}

// An edit that names no file is one this module cannot read, so the call is refused.
const unreadableEdit = (toolName, input) =>
  toolName === 'edit' && namedPaths(toolName, input).length === 0;

/**
 * The PreToolUse payloads the guard should judge for one tool call. Calls of a tool the
 * guard does not read give none. `cwd` is the session's working directory.
 */
export function guardPayloads(toolName, input, cwd) {
  if (toolName === 'bash') {
    const dir = typeof input.cwd === 'string' ? normalizeTarget(input.cwd) : '';
    // The harness reads a bare `/` as the session's own directory.
    const startsElsewhere = dir && !/^\/+$/.test(dir) && !isInternalUrl(dir);
    return [
      {
        tool_name: 'Bash',
        tool_input: { command: input.command ?? '' },
        cwd: startsElsewhere ? path.resolve(cwd, dir) : cwd,
      },
    ];
  }
  return writtenPaths(toolName, input).map(file => ({
    tool_name: 'Write',
    tool_input: { file_path: file },
    cwd,
  }));
}

// Runs the guard on one payload and resolves to its exit status and stderr.
const runGuard = payload =>
  new Promise(resolve => {
    const child = spawn(GUARD, { stdio: ['pipe', 'ignore', 'pipe'], timeout: GUARD_TIMEOUT_MS });
    let stderr = '';
    child.stderr.on('data', chunk => (stderr += chunk));
    child.on('error', error => resolve({ status: null, stderr: error.message }));
    child.on('close', status => resolve({ status, stderr }));
    child.stdin.on('error', () => {});
    child.stdin.end(JSON.stringify(payload));
  });

/**
 * The guard's verdict on one payload: `{ block: reason }` for exit code 2, `{ warning }` when the
 * guard itself could not run to a verdict, and an empty object when it lets the call through.
 */
export async function judge(payload) {
  const { status, stderr } = await runGuard(payload);
  const said = stderr.trim();
  if (status === 0) return {};
  if (status === 2) return { block: said };
  return { warning: `guard-main-checkout.sh gave no verdict (status ${status}): ${said}` };
}

export default function ompGuard(pi) {
  // The guard script is optional wiring, as in the PreToolUse command that runs it.
  try {
    accessSync(GUARD, constants.X_OK);
  } catch {
    return;
  }
  pi.on('tool_call', async (event, ctx) => {
    const input = event.input ?? {};
    if (unreadableEdit(event.toolName, input)) {
      const reason = 'Blocked: the guard could not read which file this edit writes.';
      return { block: true, reason };
    }
    const warnings = [];
    for (const payload of guardPayloads(event.toolName, input, ctx.cwd)) {
      const verdict = await judge(payload);
      if (verdict.block !== undefined) return { block: true, reason: verdict.block };
      if (verdict.warning) warnings.push(verdict.warning);
    }
    return warnings.length ? { additionalContext: unique(warnings).join('\n') } : undefined;
  });
}
