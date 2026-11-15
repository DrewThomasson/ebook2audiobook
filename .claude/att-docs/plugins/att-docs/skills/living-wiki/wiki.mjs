#!/usr/bin/env node
// Keeps a documents folder publishable as an Azure DevOps code wiki.
//
//   node wiki.mjs --config <file>            check
//   node wiki.mjs --config <file> --write    regenerate the wiki pages
//   node wiki.mjs --config <file> --report   check, and list every name
//                                            the wiki may retitle
//
// The config is a JSON file; a path in it is relative to the git toplevel of
// the config file's folder:
//   docsRoot      the documents folder, default "docs"
//   descriptions  the tab-separated page descriptions file (required)
//   homeTitle     the heading of the generated home page, default "Documentation"
//   rootOrder     root folders pinned after Home, in order, default none
//
// The check reads every page under the documents folder and fails on what the
// wiki cannot carry: a file or folder name with a space, which is written as a
// hyphen, a page or folder name with a character the wiki refuses, a page path
// over the length limit, two names in one folder that map to the same page
// title, and a relative link that leaves the folder or names a file that is not
// there. It also renders the pages it owns and compares them with the tree:
// Home.md, one page beside each folder (the wiki shows a folder with a
// same-named page beside it as that page), and the .order files that pin a
// few pages to the top of their folder. Descriptions come from the
// descriptions file.
//
// Exit codes: 0 clean, 2 a rule is broken, 3 the generated pages are behind
// the tree, 64 an unknown option or a missing config. Nothing is written
// without --write.

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { hyphenated } from '../../shared/doc-names.mjs';

const args = process.argv.slice(2);
const configAt = args.indexOf('--config');
const flags = args.filter((_, i) => i !== configAt && i !== configAt + 1);
for (const arg of flags) {
  if (!['--write', '--report'].includes(arg)) {
    console.error(`wiki: unknown option ${arg}`);
    process.exit(64);
  }
}
if (configAt < 0 || !args[configAt + 1]) {
  console.error('wiki: --config <file> is required');
  process.exit(64);
}
const writing = flags.includes('--write');
const reporting = flags.includes('--report');

const configFile = path.resolve(args[configAt + 1]);
const config = JSON.parse(fs.readFileSync(configFile, 'utf8'));
const REPO_ROOT = execFileSync('git', ['rev-parse', '--show-toplevel'], {
  cwd: path.dirname(configFile), encoding: 'utf8',
}).trim();
const DOCS_NAME = config.docsRoot ?? 'docs';
const DOCS = path.join(REPO_ROOT, DOCS_NAME);
if (!config.descriptions) {
  console.error('wiki: the config needs "descriptions"');
  process.exit(64);
}
const DESCRIPTIONS = path.join(REPO_ROOT, config.descriptions);
const DESCRIPTIONS_NAME = path.basename(config.descriptions);
const HOME_TITLE = config.homeTitle ?? 'Documentation';

// The first line of every page this script writes. A page beside a folder
// without it was written by hand, and the script leaves that page alone.
const MARKER = `<!-- Generated from the folder layout under ${DOCS_NAME}/. `
  + 'Edits here are overwritten. -->';
const HOME = 'Home';
// The home page, then the sections the config names in the order a reader
// needs them. Every other root page follows in the wiki's own alphabetical order.
const ROOT_ORDER = [HOME, ...(config.rootOrder ?? [])];
// A folder that holds an index page opens on it.
const INDEX = 'index';
// The wiki refuses a page path longer than this.
const MAX_PAGE_PATH = 235;

const posix = (rel) => rel.split(path.sep).join('/');
const stem = (name) => name.replace(/\.md$/, '');

// ---- the tree ---------------------------------------------------------------

const walked = [];     // docs-relative folder paths, '' for docs/ itself
const walkedPages = []; // docs-relative .md paths
const walkedFiles = []; // docs-relative paths of every other file
const orderFiles = []; // docs-relative .order paths
// Git carries no empty folder, so a folder with no file anywhere beneath it is
// one the committed tree does not have, and the check leaves it out the same.
const carried = new Set(['']);
function carry(file) {
  for (let dir = path.posix.dirname(file); dir !== '.'; dir = path.posix.dirname(dir)) {
    carried.add(dir);
  }
}
// A dot folder holds no pages, but a file in it is still one git carries.
const holdsFile = (abs) => fs.readdirSync(abs, { withFileTypes: true })
  .some((entry) => !entry.isDirectory() || holdsFile(path.join(abs, entry.name)));
function walk(rel) {
  walked.push(rel);
  const abs = path.join(DOCS, rel);
  for (const entry of fs.readdirSync(abs, { withFileTypes: true })) {
    const child = rel ? `${rel}/${entry.name}` : entry.name;
    const dotFolder = entry.isDirectory() && entry.name.startsWith('.');
    if (!entry.isDirectory() || (dotFolder && holdsFile(path.join(abs, entry.name)))) {
      carry(child);
    }
    if (entry.name === '.order') orderFiles.push(child);
    if (entry.name.startsWith('.')) continue;
    if (entry.isDirectory()) walk(child);
    else if (entry.name.endsWith('.md')) walkedPages.push(child);
    else walkedFiles.push(child);
  }
}
walk('');
const folders = walked.filter((folder) => carried.has(folder));
const folderSet = new Set(folders);
const read = (rel) => fs.readFileSync(path.join(DOCS, rel), 'utf8');
// A generated page beside a folder that is gone is removed below. Nothing built
// here counts it, so the pages written in the same pass match the tree it leaves.
const stalePages = walkedPages.filter((p) => p !== `${HOME}.md`
  && !folderSet.has(stem(p)) && read(p).startsWith(MARKER));
const staleSet = new Set(stalePages);
const pages = walkedPages.filter((p) => !staleSet.has(p));
const pageSet = new Set(pages);
const isGenerated = (rel) => pageSet.has(rel) && read(rel).startsWith(MARKER);
const childFolders = (rel) => folders
  .filter((f) => f && path.posix.dirname(f) === (rel || '.'))
  .sort((a, b) => path.posix.basename(a).localeCompare(path.posix.basename(b)));
const peerOf = (folder) => `${folder}.md`;

// ---- descriptions -----------------------------------------------------------

const describedAs = new Map();
for (const line of fs.readFileSync(DESCRIPTIONS, 'utf8').split('\n')) {
  if (!line.trim() || line.startsWith('#')) continue;
  const [key, text] = line.split('\t');
  describedAs.set(key, (text ?? '').trim());
}
function describe(rel) {
  const key = rel || '.';
  if (describedAs.has(key)) return describedAs.get(key);
  const parent = path.posix.dirname(key);
  const wild = describedAs.get(`${parent === '.' ? '' : `${parent}/`}*`);
  return wild?.replaceAll('{name}', path.posix.basename(key));
}

const errors = [];
const warn = { hyphen: [], nonAscii: [] };

// ---- names ------------------------------------------------------------------

// A '-' in a file name reads as a space in the page title and '%2D' as a
// hyphen, so two names can land on one title.
const titleOf = (name) => {
  const spaced = name.replace(/-/g, ' ');
  try {
    return decodeURIComponent(spaced);
  } catch {
    return spaced;
  }
};
function checkSpace(rel) {
  const name = path.posix.basename(rel);
  if (/\s/.test(name)) {
    errors.push(`${rel}: the name holds a space; rename it ${hyphenated(name)}`);
  }
}
function checkName(rel, name) {
  checkSpace(rel);
  // The wiki refuses control characters, '/', '\' and '#', and a name that
  // starts or ends with a period.
  if (/[\u0000-\u001f\u007f\\#]/.test(name)) {
    errors.push(`${rel}: the name holds \\, # or a control character`);
  }
  if (/^\.|\.$/.test(name)) errors.push(`${rel}: the name starts or ends with a period`);
  if (name.includes('-')) warn.hyphen.push(rel);
  if (/[^ -~]/.test(name)) warn.nonAscii.push(rel);
}
for (const file of walkedFiles) checkSpace(file);
for (const folder of folders.filter(Boolean)) checkName(folder, path.posix.basename(folder));
for (const page of pages) {
  checkName(page, stem(path.posix.basename(page)));
  const pagePath = `/${stem(page)}`;
  if (pagePath.length > MAX_PAGE_PATH) {
    errors.push(`${page}: the page path is ${pagePath.length} characters, over ${MAX_PAGE_PATH}`);
  }
}
for (const folder of folders) {
  // A folder and the page beside it are one wiki entry, so the pair counts once.
  const entries = new Set([
    ...pages.filter((p) => path.posix.dirname(p) === (folder || '.'))
      .map((p) => stem(path.posix.basename(p))),
    ...childFolders(folder).map((f) => path.posix.basename(f)),
  ]);
  const seen = new Map();
  for (const name of entries) {
    const title = titleOf(name);
    if (seen.has(title)) {
      errors.push(`${folder || DOCS_NAME}: "${seen.get(title)}" and "${name}" `
        + `both read as the page "${title}"`);
    } else seen.set(title, name);
  }
}

// ---- links ------------------------------------------------------------------

// Fenced blocks and inline code hold examples, not links.
const prose = (text) => text
  .replace(/^(```|~~~)[^\n]*\n[\s\S]*?^\1[^\n]*$/gm, '')
  .replace(/`[^`\n]*`/g, '');
const INLINE = /!?\[(?:[^\]\\]|\\.)*\]\(\s*(<[^>\n]*>|[^)\s]+)(?:\s+(?:"[^"]*"|'[^']*'))?\s*\)/g;
// A footnote, [^1]: text, has the same shape and is not a link.
const REFERENCE = /^ {0,3}\[(?!\^)[^\]]+\]:\s*(<[^>\n]*>|\S+)/gm;
function linkTargets(text) {
  const body = prose(text);
  return [...body.matchAll(INLINE), ...body.matchAll(REFERENCE)].map((m) => m[1]);
}
function checkLink(page, raw) {
  const target = raw.replace(/^<|>$/g, '');
  // A scheme of two letters or more is a URL. A single letter is a drive.
  if (/^[a-z][a-z0-9+.-]+:/i.test(target) || target.startsWith('#')) return;
  const where = target.split('#')[0].split('?')[0];
  if (!where) return;
  if (/^[a-z]:/i.test(where)) return errors.push(`${page}: links to a local drive, ${raw}`);
  if (where.startsWith('/')) {
    return errors.push(`${page}: absolute link ${raw}; the wiki reads it as a page path`);
  }
  let decoded = where;
  try {
    decoded = decodeURIComponent(where);
  } catch {
    return errors.push(`${page}: link ${raw} is not valid percent-encoding`);
  }
  const resolved = path.posix.normalize(path.posix.join(path.posix.dirname(page), decoded));
  if (resolved.startsWith('..')) return errors.push(`${page}: link ${raw} leaves ${DOCS_NAME}/`);
  const abs = path.join(DOCS, resolved);
  if (staleSet.has(resolved)) {
    return errors.push(`${page}: link ${raw} names a generated page whose folder is gone`);
  }
  if (expected.has(resolved)) return;
  if (!fs.existsSync(abs)) {
    return errors.push(`${page}: link ${raw} names a file that is not there`);
  }
  if (fs.statSync(abs).isDirectory()) {
    errors.push(`${page}: link ${raw} names a folder; link the page beside it, ${resolved}.md`);
  }
}

// ---- generated pages --------------------------------------------------------

const encodePath = (rel) => rel.split('/')
  .map((part) => encodeURIComponent(part).replace(/\(/g, '%28').replace(/\)/g, '%29'))
  .join('/');
const linkTo = (fromFolder, rel) => encodePath(path.posix.relative(fromFolder || '.', rel));

function needDescription(rel) {
  const text = describe(rel);
  if (!text) errors.push(`${rel || DOCS_NAME}: no description in ${DESCRIPTIONS_NAME}`);
  return text ?? '';
}

function folderList(fromFolder, folder) {
  const subs = childFolders(folder);
  if (!subs.length) return [];
  const item = (sub) => `- [${path.posix.basename(sub)}](${linkTo(fromFolder, peerOf(sub))}): `
    + needDescription(sub);
  return ['## Folders', '', ...subs.map(item), ''];
}

function homePage() {
  const roots = childFolders('').map((f) => path.posix.basename(f));
  const ordered = [
    ...ROOT_ORDER.filter((name) => roots.includes(name)),
    ...roots.filter((name) => !ROOT_ORDER.includes(name)),
  ];
  const reference = pages
    .filter((p) => !p.includes('/') && stem(p) !== HOME && !folderSet.has(stem(p)))
    .sort((a, b) => a.localeCompare(b));
  return [
    MARKER, '', `# ${HOME_TITLE}`, '', needDescription(''), '',
    '## Sections', '',
    ...ordered.map((name) => `- [${name}](${linkTo('', peerOf(name))}): ${needDescription(name)}`),
    '', '## Reference pages', '',
    ...reference.map((p) => `- [${stem(p)}](${linkTo('', p)}): ${needDescription(p)}`),
    '',
  ].join('\n');
}

function folderPage(folder) {
  const parent = path.posix.dirname(folder) === '.' ? '' : path.posix.dirname(folder);
  const lines = [MARKER, '', `# ${path.posix.basename(folder)}`, '', needDescription(folder), ''];
  const index = `${folder}/${INDEX}.md`;
  if (pageSet.has(index)) lines.push(`Start with [${INDEX}](${linkTo(parent, index)}).`, '');
  lines.push(...folderList(parent, folder));
  // The pages beside its subfolders are those folders, not pages of its own.
  const own = (p) => path.posix.dirname(p) === folder && !folderSet.has(stem(p));
  if (pages.some(own)) {
    lines.push('Its pages are listed under it in the navigation tree.', '');
  }
  return lines.join('\n');
}

const expected = new Map();
expected.set(`${HOME}.md`, homePage());
for (const folder of folders.filter(Boolean)) {
  const peer = peerOf(folder);
  if (pageSet.has(peer) && !isGenerated(peer)) continue;
  expected.set(peer, folderPage(folder));
}
for (const folder of folders) {
  const order = folder ? `${folder}/.order` : '.order';
  if (!folder) {
    const roots = new Set([...childFolders('').map((f) => path.posix.basename(f)), HOME]);
    expected.set(order, `${ROOT_ORDER.filter((name) => roots.has(name)).join('\n')}\n`);
  } else if (pageSet.has(`${folder}/${INDEX}.md`)) {
    expected.set(order, `${INDEX}\n`);
  }
}

// Generated pages a folder no longer backs, and .order files no rule writes.
const orphans = [
  ...stalePages,
  ...orderFiles.filter((o) => !expected.has(o)),
];

// The pages about to be written are checked like any other.
for (const page of pages) {
  const text = expected.has(page) ? expected.get(page) : read(page);
  for (const target of linkTargets(text)) checkLink(page, target);
}
for (const [rel, text] of expected) {
  if (pageSet.has(rel) || !rel.endsWith('.md')) continue;
  for (const target of linkTargets(text)) checkLink(rel, target);
}

const stale = [...expected].filter(([rel, text]) => {
  const abs = path.join(DOCS, rel);
  return !fs.existsSync(abs) || fs.readFileSync(abs, 'utf8') !== text;
}).map(([rel]) => rel);

// ---- report -----------------------------------------------------------------

if (writing) {
  for (const rel of stale) fs.writeFileSync(path.join(DOCS, rel), expected.get(rel));
  for (const rel of orphans) fs.rmSync(path.join(DOCS, rel));
  console.log(`wiki: wrote ${stale.length} page(s), removed ${orphans.length}`);
}

for (const error of errors) console.log(error);
const behind = writing ? [] : [...stale, ...orphans];
for (const rel of behind) console.log(`${rel}: behind the tree`);

console.log(`wiki: ${warn.hyphen.length} name(s) with a hyphen the wiki shows as a space, `
  + `${warn.nonAscii.length} with a character outside ASCII`);
if (reporting) {
  for (const [kind, list] of Object.entries(warn)) {
    for (const rel of list) console.log(`  ${kind}: ${rel}`);
  }
}

if (errors.length) {
  console.log(`wiki: ${errors.length} problem(s) the wiki cannot carry. `
    + 'See the living-wiki skill.');
  process.exit(2);
}
if (behind.length) {
  console.log('wiki: the generated pages are behind the tree. '
    + 'Run with --write and commit the result.');
  process.exit(3);
}
console.log(`wiki: clean (${pages.length} page(s), ${folders.length} folder(s))`);
