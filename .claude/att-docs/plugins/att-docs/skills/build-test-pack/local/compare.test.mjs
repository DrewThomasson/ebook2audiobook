// Tests for the pack comparison: the workbook reader, the source readers, each
// truth check, the scenario crosswalk and the command line. Every workbook and
// document is built here from synthetic text.
//
//   node --test plugins/att-docs/skills/build-test-pack/local/compare.test.mjs

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { after, test } from 'node:test';
import { fileURLToPath } from 'node:url';
import zlib from 'node:zlib';
import { parseArgs } from './build-pack.mjs';
import { compare, formatChecks, gateOf, headerDiff, idShape, modelPass, parseStandard, reportOf, runCompare, truthOf } from './compare.mjs';
import { junkKind, qualityChecks } from './quality.mjs';
import { confidenceValues, dashboardCountMismatches, matrixCardProblems, objectiveCardProblems } from './consistency.mjs';
import { controlNames, crosswalkCards, repeatedCards, scenarioModel, setReport, splitGroups } from './floor.mjs';
import { expandIds, readPack } from './pack.mjs';
import { loadRules, parseDoc } from './source.mjs';
import { citedIds, citedRules, crosswalkRows, expectedResultChecks, matchRuleRow, outcomeOf, retiredRecord,
  retiredRules, staleHits, struckOnlyWords } from './truth.mjs';
import { columnNumber, decodeXml, readXlsx, readZip } from './xlsx.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const BUILD_PACK = path.join(HERE, 'build-pack.mjs');
// One scratch root for the whole file, removed when the last test ends.
const SCRATCH_ROOT = fs.mkdtempSync(path.join(os.tmpdir(), 'compare-test-'));
after(() => fs.rmSync(SCRATCH_ROOT, { recursive: true, force: true }));
const tmp = () => fs.mkdtempSync(path.join(SCRATCH_ROOT, 'compare-'));

// ---- a small zip and xlsx writer ----------------------------------------

const CRC = Array.from({ length: 256 }, (_, n) => {
  let c = n;
  for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});
const crc32 = (buffer) => {
  let c = 0xffffffff;
  for (const byte of buffer) c = CRC[(c ^ byte) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
};

/** A zip of { name: text } with entries stored, or deflated when `deflate` is set. */
function zip(files, deflate = false) {
  const locals = [];
  const centrals = [];
  let offset = 0;
  for (const [name, text] of Object.entries(files)) {
    const raw = Buffer.from(text);
    const packed = deflate ? zlib.deflateRawSync(raw) : raw;
    const method = deflate ? 8 : 0;
    const nameBytes = Buffer.from(name);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(method, 8);
    local.writeUInt32LE(crc32(raw), 14);
    local.writeUInt32LE(packed.length, 18);
    local.writeUInt32LE(raw.length, 22);
    local.writeUInt16LE(nameBytes.length, 26);
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(20, 4);
    central.writeUInt16LE(20, 6);
    central.writeUInt16LE(method, 10);
    central.writeUInt32LE(crc32(raw), 16);
    central.writeUInt32LE(packed.length, 20);
    central.writeUInt32LE(raw.length, 24);
    central.writeUInt16LE(nameBytes.length, 28);
    central.writeUInt32LE(offset, 42);
    locals.push(local, nameBytes, packed);
    centrals.push(central, nameBytes);
    offset += 30 + nameBytes.length + packed.length;
  }
  const directory = Buffer.concat(centrals);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(Object.keys(files).length, 8);
  end.writeUInt16LE(Object.keys(files).length, 10);
  end.writeUInt32LE(directory.length, 12);
  end.writeUInt32LE(offset, 16);
  return Buffer.concat([...locals, directory, end]);
}

const escapeXml = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const letters = (n) => { let s = ''; for (let c = n; c > 0; c = Math.floor((c - 1) / 26)) s = String.fromCharCode(65 + ((c - 1) % 26)) + s; return s; };

/**
 * An .xlsx from sheets of { name, rows, merges } where rows[0] is Excel row 1
 * and a row is an array of cell text. Text goes to shared strings unless
 * `inline` is set.
 */
function xlsx(sheets, { deflate = false, inline = false } = {}) {
  const strings = [];
  const files = {};
  sheets.forEach((sheet, i) => {
    const rows = sheet.rows.map((cells, r) => `<row r="${r + 1}">${cells.map((text, c) => {
      if (text === '' || text === undefined) return '';
      const ref = `${letters(c + 1)}${r + 1}`;
      if (inline) return `<c r="${ref}" t="inlineStr"><is><t>${escapeXml(text)}</t></is></c>`;
      strings.push(String(text));
      return `<c r="${ref}" t="s"><v>${strings.length - 1}</v></c>`;
    }).join('')}</row>`).join('');
    const merges = (sheet.merges ?? []).map((m) => `<mergeCell ref="${m}"/>`).join('');
    files[`xl/worksheets/sheet${i + 1}.xml`] = `<worksheet><sheetData>${rows}</sheetData>${merges ? `<mergeCells count="${sheet.merges.length}">${merges}</mergeCells>` : ''}</worksheet>`;
  });
  files['xl/workbook.xml'] = `<workbook><sheets>${sheets.map((s, i) => `<sheet name="${escapeXml(s.name)}" sheetId="${i + 1}" r:id="rId${i + 1}"/>`).join('')}</sheets></workbook>`;
  files['xl/_rels/workbook.xml.rels'] = `<Relationships>${sheets.map((s, i) => `<Relationship Id="rId${i + 1}" Type="x" Target="worksheets/sheet${i + 1}.xml"/>`).join('')}</Relationships>`;
  files['xl/sharedStrings.xml'] = `<sst>${strings.map((t) => `<si><t>${escapeXml(t)}</t></si>`).join('')}</sst>`;
  return zip(files, deflate);
}

function write(dir, name, content) {
  const file = path.join(dir, name);
  fs.writeFileSync(file, content);
  return file;
}

// ---- synthetic source ----------------------------------------------------

const RULES = [
  { rule_id: 'RX-001', name: 'RX-001 - Save the role', status: 'active', rule_summary: 'System saves the selected role when the user selects Save.',
    description: '(Role, Page 1)\n\n"Upon selecting Save, the selected role will be saved."\n\nAtomic Summary:\nSystem saves the role.', source_page: '1', risk_level: 'High', rule_category: 'Workflow' },
  { rule_id: 'RX-002', name: 'RX-002 - Block sex abuse downgrade', status: 'active', rule_summary: 'System blocks a downgrade for a child with a sex abuse allegation.',
    description: '(Role, Page 1)\n\n"A downgrade for a child with a substantiated sex abuse allegation shows an error message."\n\nAtomic Summary:\nSystem blocks it.', source_page: '1', risk_level: 'High', rule_category: 'Validation' },
  { rule_id: 'RX-003', name: 'RX-003 - Warn before a FATL downgrade', status: 'active', rule_summary: 'System shows a warning before a FATL downgrade saves.',
    description: '(Role, Page 2)\n\n"Selecting Save for a FATL child shows a warning message."\n\nAtomic Summary:\nSystem warns.', source_page: '2', risk_level: 'High', rule_category: 'Notification' },
];
const DOC = `<a id="page-1"></a>*Page 1*

1. Upon selecting Save, the selected role will be saved.

2. A downgrade for a child with a substantiated sex abuse allegation shows an error message.

<a id="page-2"></a>*Page 2*

3. ~~Selecting Save for a FATL child shows a warning message~~
   ~~that has Continue and Cancel buttons, and the warning blocks the save.~~
`;
const source = () => {
  const rules = RULES.map((r) => ({ id: r.rule_id, name: r.name.replace(/^\S+ - /, ''), status: r.status, summary: r.rule_summary,
    description: r.description, page: r.source_page, risk: r.risk_level, category: r.rule_category }));
  const doc = parseDoc(DOC);
  return { rules, doc, retired: retiredRules(rules, doc) };
};

const IMPACT = ['Rule ID', 'Rule Name', 'Module', 'Source Document', 'Source Page', 'Rule Summary', 'Risk Level', 'Impact Classification', 'Rationale', 'Status'];
const CARDS = ['Module', 'Source Document', 'Test Case ID', 'Test Case Title', 'Mission', 'Focus', 'Expected Result', 'Rules Covered', 'Generated Markdown'];
const ALM = ['Subject', 'Test Name', 'Type', 'Step Name', 'Description', 'Expected Result'];
const LAB = ['Test Set #', 'Test Set Name', 'Objective', 'Scope', 'Business Rule Summary', 'Test Cards Covered', 'Generated Markdown'];

/** A pack workbook; `titled` puts a title, a subtitle and a gap above each header row. */
function packSheets({ titled = false, impact = [], cards = [], steps = [], sets = [], extra = [] }) {
  const sheet = (name, headers, data) => (titled
    ? { name, rows: [['Title of the pack'], ['A subtitle'], [], headers, ...data], merges: ['A1:C1', 'A2:C2'] }
    : { name, rows: [headers, ...data] });
  return [
    sheet('Impact Analysis', IMPACT, impact.map((r) => [r.id, r.name ?? '', 'RX', 'Role', r.page ?? '1', r.summary, r.risk ?? 'High', r.cls ?? 'Regression', 'why', r.status ?? 'Active'])),
    sheet('Test Cards Markdown', CARDS, cards.map((c) => ['RX', 'Role', c.id, c.title, c.mission ?? '', c.focus, c.expected, c.rules ?? '', ''])),
    sheet('Test Lab Markdown', LAB, sets.map((s) => [s.number, s.name, s.objective ?? s.name, 'scope', 'summary', s.cards, ''])),
    sheet('ALM Upload', ALM, steps.map((s) => ['RX - Role', s.name, 'Manual', s.step, s.description ?? 'do it', s.expected ?? ''])),
    ...extra,
  ];
}

// ---- the workbook reader -------------------------------------------------

test('the zip reader returns stored and deflated entries', () => {
  for (const deflate of [false, true]) {
    const entries = readZip(zip({ 'a.txt': 'hello', 'dir/b.txt': 'x'.repeat(500) }, deflate));
    assert.equal(entries.get('a.txt').toString(), 'hello');
    assert.equal(entries.get('dir/b.txt').length, 500);
  }
  assert.throws(() => readZip(Buffer.from('not a zip')), /not a zip/);
});

test('the reader gives sheets in workbook order with Excel row numbers', () => {
  const sheets = readXlsx(xlsx([{ name: 'First', rows: [['a', 'b'], [], ['c', '', 'd']] }, { name: 'Second & Co', rows: [['x']] }]));
  assert.deepEqual(sheets.map((s) => s.name), ['First', 'Second & Co']);
  assert.deepEqual(sheets[0].rows[1], ['', 'a', 'b']);
  assert.equal(sheets[0].rows[2], undefined);
  assert.equal(sheets[0].rows[3][3], 'd');
  assert.equal(sheets[0].rows[3][2], '');
});

test('the reader handles shared strings, inline strings, entities and deflate', () => {
  for (const options of [{ inline: false }, { inline: true }, { deflate: true }]) {
    const [sheet] = readXlsx(xlsx([{ name: 'S', rows: [['Save & Close', '<b>', 'say "hi"']] }], options));
    assert.deepEqual(sheet.rows[1].slice(1), ['Save & Close', '<b>', 'say "hi"']);
  }
  assert.equal(decodeXml('a &amp; b &lt; &#65; &#x42;'), 'a & b < A B');
  assert.equal(columnNumber('AB'), 28);
});

test('rich text runs in a shared string are joined', () => {
  const files = {
    'xl/workbook.xml': '<workbook><sheets><sheet name="S" sheetId="1" r:id="rId1"/></sheets></workbook>',
    'xl/_rels/workbook.xml.rels': '<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>',
    'xl/sharedStrings.xml': '<sst><si><r><t>Hel</t></r><r><rPr/><t xml:space="preserve">lo </t></r><r><t>there</t></r></si></sst>',
    'xl/worksheets/sheet1.xml': '<worksheet><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1"><v>42</v></c></row></sheetData></worksheet>',
  };
  const [sheet] = readXlsx(zip(files));
  assert.deepEqual(sheet.rows[1].slice(1), ['Hello there', '42']);
});

test('a merged range repeats its top-left value in every cell', () => {
  const [sheet] = readXlsx(xlsx([{ name: 'S', rows: [['Title'], [], ['a', 'b', 'c']], merges: ['A1:C2'] }]));
  assert.deepEqual(sheet.rows[1].slice(1), ['Title', 'Title', 'Title']);
  assert.deepEqual(sheet.rows[2].slice(1), ['Title', 'Title', 'Title']);
  assert.deepEqual(sheet.rows[3].slice(1), ['a', 'b', 'c']);
});

// ---- pack reading --------------------------------------------------------

test('header rows are found under a title and subtitle and in row 1', () => {
  const data = { impact: [{ id: 'RX-001', summary: 's' }], cards: [{ id: 'TC-RX-100-001', title: 't', focus: 'f', expected: 'e' }] };
  const dir = tmp();
  const titled = readPack(write(dir, 'titled.xlsx', xlsx(packSheets({ titled: true, ...data }))));
  const plain = readPack(write(dir, 'plain.xlsx', xlsx(packSheets(data))));
  const impactTitled = titled.sheet('impact analysis');
  assert.equal(impactTitled.headerRow, 4);
  assert.deepEqual([impactTitled.title.n, impactTitled.subtitle.n], [1, 2]);
  assert.equal(impactTitled.rows[0].n, 5);
  assert.equal(plain.sheet('impact analysis').headerRow, 1);
  assert.equal(plain.sheet('impact analysis').title, null);
  assert.equal(plain.cards[0].id, 'TC-RX-100-001');
  assert.equal(plain.cards[0].n, 2);
});

test('card lists and rule citations expand abbreviations, ranges and removed marks', () => {
  assert.deepEqual(expandIds('TC-INV-9415-001; 002; 004').map((c) => c.id), ['TC-INV-9415-001', 'TC-INV-9415-002', 'TC-INV-9415-004']);
  assert.deepEqual(expandIds('TC-INV-9415-001–003').map((c) => c.id), ['TC-INV-9415-001', 'TC-INV-9415-002', 'TC-INV-9415-003']);
  assert.deepEqual(expandIds('TC-INV-9415-001; 003–004').map((c) => c.id).slice(1), ['TC-INV-9415-003', 'TC-INV-9415-004']);
  const rules = expandIds('BR-VSR-010; BR-VSR-043–045 (removed); BR-VSR-054–055; Quality-derived');
  assert.deepEqual(rules.map((r) => r.id), ['BR-VSR-010', 'BR-VSR-043', 'BR-VSR-044', 'BR-VSR-045', 'BR-VSR-054', 'BR-VSR-055']);
  assert.deepEqual(rules.map((r) => r.removed), [false, true, true, true, false, false]);
  assert.deepEqual(expandIds('An ordinary sentence, with commas.'), []);
});

// ---- the source ----------------------------------------------------------

test('rules load from a JSON export, a folder export and a Business Rules workbook', () => {
  const dir = tmp();
  const one = loadRules(write(dir, 'one.json', JSON.stringify({ doc: 'd.md', prefix: 'RX', rules: RULES })));
  assert.deepEqual(one.map((r) => r.id), ['RX-001', 'RX-002', 'RX-003']);
  assert.equal(one[0].name, 'Save the role');
  const many = loadRules(write(dir, 'many.json', JSON.stringify({ exports: [{ rules: RULES.slice(0, 1) }, { rules: RULES.slice(1) }] })));
  assert.equal(many.length, 3);
  assert.throws(() => loadRules(write(dir, 'bad.json', '{"rules": 5}')), /not a rule export/);
  const header = ['Path', 'Requirement Type', 'Rule Category', 'Name', 'Description', 'Source Document', 'Source Page', 'Rule Summary', 'Risk Level'];
  const book = loadRules(write(dir, 'rules.xlsx', xlsx([{ name: 'Business Rules', rows: [header,
    ...RULES.map((r) => ['p', 'Business Rule', r.rule_category, r.name, r.description, 'doc', r.source_page, r.rule_summary, r.risk_level])] }])));
  assert.deepEqual(book.map((r) => [r.id, r.status, r.page, r.risk]), [['RX-001', 'active', '1', 'High'], ['RX-002', 'active', '1', 'High'], ['RX-003', 'active', '2', 'High']]);
  assert.equal(book[1].summary, RULES[1].rule_summary);
});

test('struck-through text is split from live text with line numbers and pages', () => {
  const doc = parseDoc(DOC);
  assert.equal(doc.spans.length, 2);
  assert.equal(doc.spans[0].text, 'Selecting Save for a FATL child shows a warning message');
  assert.equal(doc.spans[0].line, 9);
  assert.equal(doc.spans[1].line, 10);
  assert.ok(doc.live.every((p) => !/warning/.test(p.text)));
  assert.deepEqual(doc.live.map((p) => p.line), [3, 5]);
  assert.equal(doc.pageAt(5), 1);
  assert.equal(doc.pageAt(9), 2);
  const quoted = parseDoc('> *~~A quoted\n> warning~~*\n\n- ~~a list item~~ and live\n');
  assert.deepEqual(quoted.spans.map((s) => [s.text, s.line, s.endLine]), [['A quoted warning', 1, 2], ['a list item', 4, 4]]);
  assert.match(quoted.live.at(-1).text, /and live/);
});

// ---- truth ---------------------------------------------------------------

test('a rule the document struck through is retired even when the export says active', () => {
  const { retired } = source();
  assert.deepEqual([...retired.keys()], ['RX-003']);
  assert.equal(retired.get('RX-003').span.line, 9);
  const exported = source().rules.map((r) => (r.id === 'RX-001' ? { ...r, status: 'retired' } : r));
  assert.deepEqual([...retiredRules(exported, parseDoc(DOC)).keys()], ['RX-001', 'RX-003']);
});

test('rule rows match by ID, then by shared words, and an unrelated row matches nothing', () => {
  const { rules } = source();
  assert.equal(matchRuleRow({ id: 'rx-002', name: '', summary: '' }, rules).how, 'id');
  assert.equal(matchRuleRow({ id: '', name: 'RX-001 - Save the role', summary: '' }, rules).rule.id, 'RX-001');
  const byText = matchRuleRow({ id: 'A sentence', name: 'A downgrade for a child with a substantiated sex abuse allegation shows an error message.', summary: 'ignored words' }, rules);
  assert.deepEqual([byText.rule.id, byText.how], ['RX-002', 'text']);
  assert.equal(matchRuleRow({ id: '', name: 'The printer toner runs out', summary: 'Toner is low.' }, rules), null);
});

test('the crosswalk sorts rows into matched, retired by the document, and not in the source', () => {
  const s = source();
  const pack = readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({ impact: [
    { id: 'RX-001', summary: 'System saves the role.' },
    { id: 'Selecting Save for a FATL child shows a warning message that has Continue and Cancel buttons', summary: 'Shows a warning message with Continue and Cancel buttons.', cls: 'Regression' },
    { id: 'Toner', name: 'The printer toner runs out', summary: 'Toner is low.' },
  ] }))));
  const rows = crosswalkRows(pack, s.rules, s.retired, s.doc);
  assert.deepEqual(rows.map((r) => r.match?.rule.id ?? null), ['RX-001', 'RX-003', null]);
  assert.deepEqual(rows.map((r) => r.outside), [null, null, 'not in the source']);
  assert.equal(rows[1].liveAsRetired, true);
  const orphan = crosswalkRows({ ruleRows: [{ n: 2, id: '', name: 'Selecting Save for a FATL child shows a warning message', summary: '', classification: '' }] },
    s.rules.filter((r) => r.id !== 'RX-003'), s.retired, s.doc);
  assert.equal(orphan[0].outside, 'retired');
  assert.equal(orphan[0].span.line, 9);
});

test('a pack that omits a retired rule is told so, and one that records it is not', () => {
  const s = source();
  const record = (impact) => {
    const pack = readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({ impact }))));
    return retiredRecord(crosswalkRows(pack, s.rules, s.retired, s.doc), s.rules, s.retired, s.doc).rules[0];
  };
  assert.equal(record([{ id: 'RX-001', summary: 'x' }]).status, 'missing');
  assert.equal(record([{ id: 'RX-003', summary: 'x', cls: 'Regression' }]).status, 'unmarked');
  assert.equal(record([{ id: 'RX-003', summary: 'x', cls: 'Superseded / Removal Verification' }]).status, 'recorded');
  assert.equal(record([{ id: 'RX-003', summary: 'Retired: warning', cls: 'Direct Change' }]).status, 'recorded');
  // The Status column alone marks a retired rule: Direct Change, Status Retired, no prefix in the summary.
  assert.equal(record([{ id: 'RX-003', summary: 'x', cls: 'Direct Change', status: 'Retired' }]).status, 'recorded');
  assert.equal(record([{ id: 'RX-003', summary: 'x', cls: 'Direct Change', status: 'Active' }]).status, 'unmarked');
});

test('wording only retired text has marks a live rule row as untrue, with the doc line', () => {
  const s = source();
  const only = struckOnlyWords(s.doc);
  assert.ok(only.has('warn'));
  assert.ok(!only.has('message'));
  assert.ok(!only.has('cancel'), 'a word used once in struck text is not what the retired text is about');
  assert.deepEqual(staleHits('Allowed, subject to the warning flow.', only).map((h) => [h.word, h.span.line]), [['warn', 9]]);
  assert.deepEqual(staleHits('No warning is shown. Without the retired warning.', only), []);
  const pack = readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({ impact: [
    { id: 'RX-001', summary: 'System saves the role, subject to the warning flow.' },
    { id: 'RX-002', summary: 'System blocks a downgrade for a child with a sex abuse allegation.' },
    { id: 'RX-003', summary: 'System shows a warning.', cls: 'Superseded' },
  ] }))));
  const rows = crosswalkRows(pack, s.rules, s.retired, s.doc);
  assert.deepEqual(rows.map((r) => r.stale.length > 0), [true, false, false]);
});

test('a rule ID cited by a card but missing from the rows, matrices and rules is reported', () => {
  const s = source();
  const matrix = { name: 'Rule-to-Test Matrix', rows: [['Rule ID', 'Covered By Test Card(s)'], ['RX-001', 'TC-RX-100-001']] };
  const pack = readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({
    impact: [{ id: 'RX-001', summary: 'x' }],
    cards: [{ id: 'TC-RX-100-001', title: 't', focus: 'f', expected: 'e', rules: 'RX-001; RX-002; RX-009' }], extra: [matrix] }))));
  const rows = crosswalkRows(pack, s.rules, s.retired, s.doc);
  const cited = citedIds(pack, s.rules, rows);
  const flags = Object.fromEntries(cited.map((c) => [c.id, [c.approved, c.impact, c.matrix]]));
  assert.deepEqual(flags, { 'RX-001': [true, true, true], 'RX-002': [true, false, false], 'RX-009': [false, false, false] });
});

test('a card that cites rules by sentence resolves to the pack row and its approved rule', () => {
  const s = source();
  const sentence = 'A downgrade for a child with a substantiated sex abuse allegation shows an error message.';
  const pack = readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({
    impact: [{ id: `Doc ${sentence}`, name: sentence, summary: 'Blocks the downgrade.' }],
    cards: [{ id: 'TC-RX-100-001', title: 't', focus: 'f', expected: 'e', rules: `Doc ${sentence}\nSomething nobody wrote down` }] }))));
  const rows = crosswalkRows(pack, s.rules, s.retired, s.doc);
  const cited = citedRules(pack.cards[0], rows, s.rules);
  assert.deepEqual(cited.ids, ['RX-002']);
  assert.equal(cited.unresolved.length, 1);
});

test('an Expected Result that contradicts its last ALM step is flagged, and one that agrees is not', () => {
  assert.equal(outcomeOf('The role is successfully downgraded. No warning or error message is displayed.'), 'goes through');
  assert.equal(outcomeOf('An error message is displayed. The role is not changed.'), 'stops');
  assert.equal(outcomeOf('A role cannot be downgraded when an allegation exists.'), 'stops');
  assert.equal(outcomeOf('The dropdown shows the previously saved value.'), 'neutral');
  const cards = [
    { id: 'TC-RX-100-001', title: 'a', focus: 'f', expected: 'The role is successfully downgraded. The Verified column updates to Y.' },
    { id: 'TC-RX-100-002', title: 'b', focus: 'f', expected: 'The role is successfully downgraded. The Verified column updates to Y.' },
    { id: 'TC-RX-100-003', title: 'c', focus: 'f', expected: 'Quartz lamps hum quietly overnight.' },
  ];
  const steps = [
    { name: 'TC-RX-100-001', step: 'Step 1', expected: 'An error message is displayed. The role is not changed.' },
    { name: 'TC-RX-100-002 - b', step: 'Step 1', expected: 'The role is saved and the Verified column updates to Y.' },
    { name: 'TC-RX-100-003', step: 'Step 1', expected: 'The grid refreshes with the saved role.' },
  ];
  const pack = readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({ cards, steps }))));
  const found = expectedResultChecks(pack);
  assert.deepEqual(found.map((c) => c.contradicts), [true, false, true]);
  assert.match(found[0].reason, /opposite/);
  assert.match(found[2].reason, /almost no words/);
});

test('ALM rows belong to the card whose ID they start with, not a longer ID', () => {
  const cards = [{ id: 'TC-RX-100-001', title: 'a', focus: 'f', expected: 'The role is saved.' }, { id: 'TC-RX-100-0011', title: 'b', focus: 'f', expected: 'x' }];
  const steps = [{ name: 'TC-RX-100-0011', step: 'Step 1', expected: 'An error is shown.' }];
  const pack = readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({ cards, steps }))));
  assert.equal(expectedResultChecks(pack)[0].checked, false);
});

// ---- the floor -----------------------------------------------------------

const card = (id, title, focus, extra = {}) => ({ id, n: 2, title, mission: '', focus, expected: '', rulesCovered: '', ...extra });

test('control names come from the document and its rules, not from a list', () => {
  const names = controlNames([
    'Upon selecting Save or Save & Close, the window closes.',
    'The Detail section holds Reset and Cancel buttons.',
    'Upon selecting “Ok,” the message closes.',
    'All buttons become enabled when a change is made. Select a row from the grid.',
  ]);
  assert.deepEqual(names.sort(), ['Cancel', 'Ok', 'Reset', 'Save', 'Save & Close']);
  assert.deepEqual(controlNames(['Nothing here names a control.']), []);
});

test('a scenario holds the controls pressed, the words that say what it runs on, and what it rules out', () => {
  const model = scenarioModel([], { controls: ['Save', 'Save & Close', 'Reset', 'Ok'] });
  const s = (c) => model.scenario(c);
  const a = s(card('a', 'Save a flagged account', 'Open a flagged account; select Save & Close; then reopen it.'));
  assert.deepEqual([...a.actions].sort(), ['reopen', 'save', 'save & close']);
  assert.ok([...a.tokens.keys()].some((w) => w.startsWith('flag')));
  const b = s(card('b', 'Reset', 'Use an account with no frozen or flagged hold; press Reset. The value resets.'));
  assert.deepEqual([...b.actions], ['reset']);
  assert.ok([...b.negated.keys()].some((w) => w.startsWith('froz')) && b.tokens.size > 0);
  assert.equal(s(card('c', 'x', 'Save with a different account on the stage.')).other, true);
  assert.equal(s(card('c', 'x', 'Save with the account on the stage.')).other, false);
  assert.ok(s(card('d', 'x', 'The child and the role and the window.')).tokens.has('child'), 'common words still count');
  const lower = s(card('e', 'Results', 'The role saves. The dropdown resets to the saved value.'));
  assert.equal(lower.actions.size, 0, 'a result in lower case is not a button press');
});

test('cards that cite the same rule and open with the same verb match with no vocabulary in common', () => {
  const reference = [
    card('r1', 'Search returns matching providers', 'Search for a provider by surname.', { rulesCovered: 'RULE-1' }),
    card('r2', 'Export a report to PDF', 'Export the monthly report.', { rulesCovered: 'RULE-2' }),
    card('r3', 'Delete a provider', 'Delete the provider.', { rulesCovered: 'RULE-3' }),
  ];
  const pack = [
    card('p1', 'Search finds people by last name', 'Search using a surname.', { rulesCovered: 'RULE-1' }),
    card('p2', 'Export a report to PDF', 'Export the monthly report.', { rulesCovered: 'RULE-2' }),
  ];
  const model = scenarioModel([...reference, ...pack]);
  const ids = (card) => card.rulesCovered.split(';').filter(Boolean);
  const found = crosswalkCards(reference, pack, (_, c) => ids(c), model);
  assert.deepEqual(found.map((r) => r.matches[0]?.card), ['p1', 'p2', undefined]);
  assert.deepEqual([found[1].status, found[2].status], ['covered', 'unmatched']);
  // The same wording with no cited rules still matches, and a different action does not.
  const bare = crosswalkCards([card('r1', 'Search returns matching providers', 'Search for a provider.')],
    [card('p9', 'Search returns matching providers', 'Search for a provider.'), card('p8', 'Export a report', 'Export it.')], () => [], model);
  assert.equal(bare[0].matches[0].card, 'p9');
});

test('repeats are found in a domain with no buttons, and different rules or actions are not repeats', () => {
  const cards = [
    card('c1', 'Search returns matching providers', 'Search for a provider by surname.', { rulesCovered: 'RULE-1' }),
    card('c2', 'Search returns providers', 'Search for a provider by surname.', { rulesCovered: 'RULE-1' }),
    card('c3', 'Search returns matching providers', 'Search for a provider by surname.', { rulesCovered: 'RULE-9' }),
    card('c4', 'Export a report to PDF', 'Export the report.', { rulesCovered: 'RULE-2' }),
    card('c5', 'Search, then export', 'Search for a provider; export the result.', { rulesCovered: 'RULE-1' }),
  ];
  const model = scenarioModel(cards);
  const { groups, repeats } = repeatedCards(cards, model, (c) => c.rulesCovered.split(';'));
  assert.equal(repeats, 2);
  assert.deepEqual(groups.map((g) => g.cards), [['c1', 'c2', 'c3'], ['c4'], ['c5']]);
  const other = [cards[0], card('c6', 'Search finds providers', 'Search for a provider by name.', { rulesCovered: 'RULE-7' })];
  const apart = repeatedCards(other, scenarioModel(other), (c) => c.rulesCovered.split(';'));
  assert.equal(apart.repeats, 0, 'cards citing different rules and worded differently are not repeats');
});

test('a reference card another card rules out, or that needs another child, is unmatched; one covered in parts says so', () => {
  const controls = ['Save', 'Reset', 'Save & Close'];
  const reference = [
    card('r1', 'Frozen save', 'Select Save for a frozen flagged account.'),
    card('r2', 'Plain save', 'Use an account with no frozen or flagged hold; select Save.'),
    card('r3', 'Other', 'Select Save for a frozen account and a different account that is flagged.'),
    card('r4', 'Workflow', 'Select Save, then Reset, for the account.'),
  ];
  const pack = [card('p1', 'Frozen save', 'Select Save for a frozen flagged account.'), card('p2', 'Reset it', 'Select Reset for the account.')];
  const found = crosswalkCards(reference, pack, () => [], scenarioModel([...reference, ...pack], { controls }));
  assert.equal(found[0].status, 'covered');
  assert.equal(found[1].status, 'unmatched');
  assert.equal(found[2].status, 'unmatched');
  assert.deepEqual(found[3].parts.sort(), ['p1', 'p2']);
  assert.notEqual(found[3].status, 'unmatched');
});

test('the Full Coverage set must hold every requirement-derived card', () => {
  const sets = [{ number: '1', name: 'Core', cards: 'TC-RX-100-001' }, { number: '2', name: 'Full Coverage', cards: 'TC-RX-100-001; 002' }];
  const cards = [1, 2, 3].map((n) => ({ id: `TC-RX-100-00${n}`, title: 't', focus: 'f', expected: 'e', rules: n === 3 ? 'Quality-derived' : 'RX-001' }));
  const report = setReport(readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({ cards, sets })))));
  assert.deepEqual([report.sets, report.cards], [2, 3]);
  assert.deepEqual(report.fullCoverage.missing, []);
  const short = setReport(readPack(write(tmp(), 'q.xlsx', xlsx(packSheets({ cards, sets: [{ number: '2', name: 'Full Coverage', cards: 'TC-RX-100-001' }] })))));
  assert.deepEqual(short.fullCoverage.missing, ['TC-RX-100-002']);
});

// ---- consistency ---------------------------------------------------------

const sheet = (name, headers, ...rows) => ({ name, rows: [headers, ...rows] });

test('the self-consistency checks find counts, confidence, matrix and objective disagreements', () => {
  const cards = [1, 2].map((n) => ({ id: `TC-RX-100-00${n}`, title: 't', focus: 'f', expected: 'e', rules: 'RX-001' }));
  const sets = [{ number: '01', name: 'One', cards: 'TC-RX-100-001' }, { number: '02', name: 'Two', cards: 'TC-RX-100-002' }];
  const pack = readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({ impact: [{ id: 'RX-001', summary: 'x' }], cards, sets, extra: [
    sheet('Dashboard', ['Item', 'Value'], ['Number of Reusable Test Cards', '2'], ['Number of Applicable Test Sets', '5'], ['Number of Business Rules', '1'], ['Overall Confidence', 'Low']),
    sheet('Executive Summary', ['Area', 'Summary'], ['Confidence level', 'Medium']),
    sheet('Confidence Assessment', ['Area', 'Assessment'], ['Overall Confidence', 'Low. Because.'], ['Coverage Confidence', 'High for the rest.']),
    sheet('Rule-to-Test Matrix', ['Rule ID', 'Covered By Test Card(s)', 'Covered By Test Set(s)'], ['RX-001', 'TC-RX-100-001; 002; 009', '01 One']),
    sheet('Objective Matrix', ['#', 'Testing Objective', 'Related Test Cards', 'Related Test Lab Test Set'], ['1', 'Core', 'TC-RX-100-001; 002', '01 One']),
  ] }))));
  assert.deepEqual(dashboardCountMismatches(pack).map((d) => [d.label, d.stated, d.actual]), [['Number of Applicable Test Sets', 5, 2]]);
  const confidence = confidenceValues(pack);
  assert.equal(confidence.consistent, false);
  assert.deepEqual(confidence.values['Confidence Assessment'], ['low']);
  assert.deepEqual(matrixCardProblems(pack).problems.map((p) => [p.card, p.problem]), [['TC-RX-100-002', "not in the row's test sets"], ['TC-RX-100-009', 'no such card']]);
  assert.deepEqual(objectiveCardProblems(pack).problems.map((o) => o.card), ['TC-RX-100-002']);
});

// ---- format --------------------------------------------------------------

test('the format score is the share of reference checks the pack matches', () => {
  const data = { impact: [{ id: 'RX-001', summary: 'x' }], cards: [{ id: 'TC-RX-100-001', title: 't', focus: 'f', expected: 'e' }],
    steps: [{ name: 'TC-RX-100-001', step: 'Step 1', expected: 'e' }] };
  const dir = tmp();
  const reference = readPack(write(dir, 'r.xlsx', xlsx(packSheets({ titled: true, ...data }))));
  const same = readPack(write(dir, 's.xlsx', xlsx(packSheets({ titled: true, ...data }))));
  assert.equal(formatChecks(reference, same).score, 1);
  const plain = readPack(write(dir, 'p.xlsx', xlsx(packSheets(data))));
  const result = formatChecks(reference, plain);
  assert.ok(result.score < 1);
  const failed = result.checks.filter((c) => !c.pass).map((c) => c.name);
  assert.ok(failed.includes('Impact Analysis: title') && failed.includes('Impact Analysis: header row'));
  assert.equal(idShape('TC-INV-9415-001'), 'AA-AAA-9999-999');
  assert.deepEqual(headerDiff(['Test Set #', 'Name'], ['Test Set Number', 'Extra']),
    { missing: ['Name'], extra: ['Extra'], renamed: [{ from: 'Test Set #', to: 'Test Set Number' }] });
});

test('an ID-only Test Name and an Expected Result on every checking step are deliberate differences', () => {
  const card = { id: 'TC-RX-100-001', title: 't', focus: 'f', expected: 'e' };
  const book = (name, expected) => readPack(write(tmp(), 'b.xlsx', xlsx(packSheets({ titled: true,
    impact: [{ id: 'RX-001', summary: 'x' }], cards: [card],
    steps: [{ name, step: 'Step 1', expected: expected[0] }, { name, step: 'Step 2', expected: expected[1] }] }))));
  const reference = book('TC-RX-100-001 - t', ['', 'e']);
  const mine = formatChecks(reference, book('TC-RX-100-001', ['saved', 'e']));
  assert.equal(mine.differences, 0);
  assert.equal(mine.deliberate, 2);
  assert.deepEqual(mine.checks.filter((c) => c.deliberate).map((c) => c.name),
    ['Expected Result only on the final step', 'Test Name form']);
  assert.ok(mine.checks.filter((c) => c.deliberate).every((c) => !c.pass && c.deliberate.length > 20));
  assert.ok(mine.score < 1, 'the score still counts a deliberate difference');
  assert.match(reportOf({ ...fakeScorecard(), format: mine }), /### Deliberate differences\n[\s\S]*Test Name form/);
  // A Test Name that is only sometimes the bare ID is a real difference, not a deliberate one.
  const mixed = readPack(write(tmp(), 'm.xlsx', xlsx(packSheets({ titled: true, impact: [{ id: 'RX-001', summary: 'x' }],
    cards: [card], steps: [{ name: 'TC-RX-100-001', step: 'Step 1', expected: 'a' },
      { name: 'TC-RX-100-001 - t', step: 'Step 2', expected: 'e' }] }))));
  const result = formatChecks(reference, mixed);
  assert.deepEqual(result.checks.filter((c) => !c.pass && !c.deliberate).map((c) => c.name), ['Test Name form']);
  assert.equal(result.differences, 1);
  // A pack with no ALM steps has no Test Name form to call deliberate.
  const bare = formatChecks(reference, readPack(write(tmp(), 'n.xlsx', xlsx(packSheets({ titled: true,
    impact: [{ id: 'RX-001', summary: 'x' }], cards: [card] })))));
  assert.equal(bare.deliberate, 0);
});

test('a workbook standard lists its worksheets and the items each must hold', () => {
  const standard = parseStandard(`# Standard

## Required Worksheets

1. Impact Analysis
2. Test Cards Markdown

## Impact Analysis

Include:

- Rule ID
- Risk Level

## Test Cards Markdown

Columns:

- Test Case ID
- Mission
`);
  assert.deepEqual(standard.sheets, ['Impact Analysis', 'Test Cards Markdown']);
  assert.deepEqual(standard.items['Impact Analysis'], ['Rule ID', 'Risk Level']);
  const pack = readPack(write(tmp(), 'p.xlsx', xlsx([{ name: 'Impact Analysis', rows: [['Rule ID', 'Level'], ['RX-001', 'x']] }])));
  const result = formatChecks(pack, pack, standard).standard.pack;
  assert.deepEqual(result.missingSheets, ['Test Cards Markdown']);
  assert.deepEqual(result.sheets[0].absent, ['Risk Level']);
});

// ---- the whole comparison ------------------------------------------------

function fixtureFiles() {
  const dir = tmp();
  const reference = write(dir, 'reference.xlsx', xlsx(packSheets({ titled: true,
    impact: [{ id: 'RX-001', summary: 'System saves the selected role when the user selects Save, subject to the warning flow.', cls: 'Direct Change' },
      { id: 'RX-002', summary: 'System blocks a downgrade for a child with a sex abuse allegation.' },
      { id: 'RX-003', summary: 'System shows a warning before a FATL downgrade saves.', cls: 'Superseded / Removal Verification' }],
    cards: [
      { id: 'TC-RX-100-001', title: 'FATL save', focus: 'Select Save for a FATL child.', expected: 'The role is saved.', rules: 'RX-001; RX-003 (removed)' },
      { id: 'TC-RX-100-002', title: 'Plain save', focus: 'Use a child with no substantiated FATL or Sex Abuse allegation; select Save.', expected: 'The role is saved.', rules: 'RX-001' },
    ], steps: [{ name: 'TC-RX-100-001', step: 'Step 1', expected: 'The role is saved.' }, { name: 'TC-RX-100-002', step: 'Step 1', expected: 'The role is saved.' }],
    sets: [{ number: '01', name: 'Full Coverage', cards: 'TC-RX-100-001; 002' }] })));
  const pack = write(dir, 'pack.xlsx', xlsx(packSheets({
    impact: [{ id: 'RX-001', summary: 'System saves the selected role when the user selects Save.', page: 'N/A', risk: 'Low' }],
    cards: [
      { id: 'TC-RX-100-001', title: 'FATL save', focus: 'Select Save for a child with a substantiated FATL allegation.', expected: 'The role is successfully saved. No error is shown.', rules: 'RX-001' },
      { id: 'TC-RX-100-002', title: 'FATL save again', focus: 'Select Save for a child with a substantiated DOA allegation.', expected: 'The role is saved.', rules: 'RX-001' },
      { id: 'TC-RX-100-003', title: 'FATL save once more', focus: 'Select Save for a child with a substantiated FATL allegation.', expected: 'The role is saved.', rules: 'RX-001' },
    ], steps: [{ name: 'TC-RX-100-001', step: 'Step 1', expected: 'An error message is displayed. The role is not changed.' }],
    sets: [{ number: '1', name: 'Full Coverage', cards: 'TC-RX-100-001' }] })));
  return {
    dir, reference, pack,
    rules: write(dir, 'rules.json', JSON.stringify({ doc: 'd.md', prefix: 'RX', rules: RULES })),
    doc: write(dir, 'doc.md', DOC),
  };
}

test('compare runs the three parts on synthetic packs', async () => {
  const f = fixtureFiles();
  const result = await compare({ reference: readPack(f.reference), pack: readPack(f.pack), rules: loadRules(f.rules), doc: parseDoc(DOC) });
  assert.equal(result.floor.pack.repeats, 2);
  assert.deepEqual(result.floor.unmatched, ['TC-RX-100-002']);
  assert.deepEqual(result.truth.pack.retiredMissing, ['RX-003']);
  assert.deepEqual(result.truth.reference.retiredMissing, []);
  assert.deepEqual(result.truth.reference.untrueRows.map((r) => [r.row, r.words]), [[5, ['warn']]]);
  assert.deepEqual(result.truth.pack.contradictions.map((c) => c.card), ['TC-RX-100-001']);
  assert.deepEqual(result.truth.pack.untrueRows, []);
  assert.deepEqual(result.truth.pack.differences > 0, true);
  assert.equal(result.model.run, false);
  const report = reportOf(result);
  for (const heading of ['## Summary', '## Format', '## Truth', '## Floor', '## Consistency', '## Model pass']) assert.ok(report.includes(heading), heading);
  assert.match(report, /Not run/);
});

test('without --model no model is called, and with it the stub answers the two questions', async () => {
  const f = fixtureFiles();
  const calls = [];
  const client = { json: async (request) => {
    calls.push(request.schemaName);
    return { value: request.schemaName === 'follows' ? { follows: false, reason: 'because' } : { same: true, reason: 'alike' } };
  } };
  const lines = await runCompare({ reference: f.reference, pack: f.pack, rules: f.rules, docs: [f.doc], out: path.join(f.dir, 'out') },
    { makeClient: () => { throw new Error('should not be built'); } });
  assert.ok(lines.some((l) => l.includes('model   not run')));
  assert.deepEqual(calls, []);
  const withModel = await runCompare({ reference: f.reference, pack: f.pack, rules: f.rules, docs: [f.doc], out: path.join(f.dir, 'out2'),
    model: true, config: 'x.json' }, { makeClient: () => client });
  assert.ok(withModel.some((l) => l.includes('model   run')));
  assert.ok(calls.includes('follows') && calls.includes('same'));
  const scorecard = JSON.parse(fs.readFileSync(path.join(f.dir, 'out2', 'compare.json'), 'utf8'));
  assert.equal(scorecard.model.run, true);
  assert.ok(scorecard.model.follows.every((x) => x.follows === false));
});

test('a model reply that cannot be had is counted and the pass goes on', async () => {
  const f = fixtureFiles();
  const reference = readPack(f.reference);
  const pack = readPack(f.pack);
  const rules = loadRules(f.rules);
  const done = await compare({ reference, pack, rules, doc: parseDoc(DOC) });
  const client = { json: async () => { throw Object.assign(new Error('x'), { code: 'network' }); } };
  const out = await modelPass({ client, reference: { pack: reference, truth: { cardRules: new Map(reference.cards.map((c) => [c.id, { ids: ['RX-001'] }])) } },
    pack: { pack, truth: { cardRules: new Map() } }, rules, unmatched: done.floor.crosswalk.filter((r) => !r.matched) });
  assert.equal(out.errors, 3);
  assert.equal(out.follows[0].error, 'network');
});

test('the command writes compare.json and compare.md and prints only counts', () => {
  const f = fixtureFiles();
  const out = path.join(f.dir, 'result');
  const run = spawnSync(process.execPath, [BUILD_PACK, 'compare', '--reference', f.reference, '--pack', f.pack, '--rules', f.rules,
    '--doc', f.doc, '--out', out], { encoding: 'utf8' });
  assert.equal(run.status, 0, run.stderr);
  assert.ok(fs.existsSync(path.join(out, 'compare.json')) && fs.existsSync(path.join(out, 'compare.md')));
  assert.doesNotMatch(run.stdout, /TC-RX|RX-00|FATL|warning/);
  assert.match(run.stdout, /floor   reference cards=2 pack cards=3 repeats=2 unmatched=1/);
  // The console's line shapes are fixed: a log filter outside this folder matches them exactly.
  assert.deepEqual(run.stdout.trim().split('\n').map((line) => line.replace(/\d+/g, 'N')), [
    'format  N/N checks matched, N deliberate, N other',
    'floor   reference cards=N pack cards=N repeats=N unmatched=N',
    'truth   retired-missing=N untrue-rows=N contradictions=N cited-missing=N',
    'truth   reference: untrue-rows=N contradictions=N cited-missing=N',
    'model   not run',
    'wrote compare.json and compare.md',
  ]);
  const defaulted = spawnSync(process.execPath, [BUILD_PACK, 'compare', '--reference', f.reference, '--pack', f.pack, '--rules', f.rules,
    '--doc', f.doc], { encoding: 'utf8' });
  assert.equal(defaulted.status, 0, defaulted.stderr);
  assert.ok(fs.existsSync(path.join(f.dir, 'compare.md')), 'the default folder is the pack\'s');
});

test('bad arguments exit 2 and name the flag, never content', () => {
  const f = fixtureFiles();
  const base = ['compare', '--reference', f.reference, '--pack', f.pack, '--rules', f.rules, '--doc', f.doc];
  const run = (args) => spawnSync(process.execPath, [BUILD_PACK, ...args], { encoding: 'utf8' });
  const cases = [
    [['compare'], /compare needs --reference/],
    [base.slice(0, -2), /compare needs --doc/],
    [[...base, '--model'], /--model needs --config/],
    [[...base, '--standard', path.join(f.dir, 'nope.md')], /--standard is not a file/],
    [[...base, '--doc', f.doc], /compare takes one --doc/],
    [['compare', '--reference', f.rules, '--pack', f.pack, '--rules', f.rules, '--doc', f.doc], /--reference could not be read/],
    [['compare', '--reference', path.join(f.dir, 'missing.xlsx'), '--pack', f.pack, '--rules', f.rules, '--doc', f.doc], /--reference is not a file/],
  ];
  for (const [args, message] of cases) {
    const result = run(args);
    assert.equal(result.status, 2, args.join(' '));
    assert.match(result.stderr, message);
  }
  assert.deepEqual(parseArgs(['compare', '--model', '--config', 'c.json']), { docs: [], words: ['compare'], model: true, config: 'c.json' });
});

// ---- later additions -----------------------------------------------------

test('card lists read every range form', () => {
  const ids = (text) => expandIds(text).map((c) => c.id.slice(-3));
  assert.deepEqual(ids('TC-ABC-1234-001 – TC-ABC-1234-003'), ['001', '002', '003']);
  assert.deepEqual(ids('TC-ABC-1234-001-003'), ['001', '002', '003']);
  assert.deepEqual(ids('TC-ABC-1234-001 - 002'), ['001', '002']);
  assert.deepEqual(ids('TC-ABC-1234-001; 004 to 006'), ['001', '004', '005', '006']);
  assert.deepEqual(ids('TC-ABC-1234-001—002; 004'), ['001', '002', '004']);
  assert.deepEqual(ids('TC-ABC-1234-001 - Save the role'), ['001']);
  assert.deepEqual(expandIds('BR-ABC-043–045 (removed)').map((r) => [r.id, r.removed]),
    [['BR-ABC-043', true], ['BR-ABC-044', true], ['BR-ABC-045', true]]);
});

test('contractions negate and discarding is not a save', () => {
  assert.equal(outcomeOf("The role isn't saved."), 'stops');
  assert.equal(outcomeOf('The role isn’t saved.'), 'stops');
  assert.equal(outcomeOf("The change doesn't update the grid."), 'stops');
  assert.equal(outcomeOf('The pending change is discarded.'), 'stops');
  assert.equal(outcomeOf('The role is saved and the grid updates.'), 'goes through');
});

test('a negation reaches its own clause only, so wording in another clause is still stale', () => {
  const only = struckOnlyWords(source().doc);
  assert.deepEqual(staleHits('No error is shown, but a warning flow runs.', only).map((h) => h.word), ['warn']);
  assert.deepEqual(staleHits('A warning flow runs, and no error is shown.', only).map((h) => h.word), ['warn']);
  assert.deepEqual(staleHits('No confirmation, warning, or prompt appears.', only), []);
  assert.deepEqual(staleHits('Verify there is no prompt, warning or dialog.', only), []);
  assert.deepEqual(staleHits('Nothing is lost. A warning dialog appears.', only).map((h) => h.word), ['warn']);
  assert.deepEqual(staleHits('No error appears, the warning message displays.', only).map((h) => h.word), ['warn']);
  assert.deepEqual(staleHits('Without error, a warning is displayed and the user selects Continue', only).map((h) => h.word), ['warn']);
  assert.deepEqual(staleHits("The warning isn't shown.", only), []);
});

test('a row that merges several rules maps to each one it covers', () => {
  const rules = ['RX-010', 'RX-011', 'RX-012', 'RX-013'].map((id, i) => ({ id, name: `rule ${i}`, status: 'active', page: '1', risk: 'High',
    summary: ['System shows the ledger balance.', 'System exports the audit trail.', 'System archives stale invoices.', 'System prints the receipt.'][i],
    description: `"${['The ledger balance is shown.', 'The audit trail is exported.', 'Stale invoices are archived.', 'The receipt is printed.'][i]}"\n\nAtomic Summary:\nx` }));
  const row = { id: '', name: 'The ledger balance is shown and the audit trail is exported.', summary: '' };
  const match = matchRuleRow(row, rules);
  assert.deepEqual(match.rules.map((r) => r.id).sort(), ['RX-010', 'RX-011']);
  const single = matchRuleRow({ id: '', name: 'The receipt is printed.', summary: '' }, rules);
  assert.deepEqual(single.rules.map((r) => r.id), ['RX-013']);
  const pack = readPack(write(tmp(), 'm.xlsx', xlsx(packSheets({ impact: [{ id: 'merged', name: row.name, summary: '' }] }))));
  const s = { rules, doc: parseDoc('plain'), retired: new Map() };
  const cited = citedRules({ rulesCovered: 'merged' }, crosswalkRows(pack, rules, s.retired, s.doc), rules);
  assert.deepEqual(cited.ids.sort(), ['RX-010', 'RX-011']);
});

test('self-checks read TS-prefixed set names, newline lists and flexible headers, and say when they cannot run', () => {
  const cards = [1, 2, 3].map((n) => ({ id: `TC-RX-100-00${n}`, title: 't', focus: 'f', expected: 'e', rules: 'RX-001' }));
  const sets = [{ number: '1', name: 'TS01 One', cards: 'TC-RX-100-001\nTC-RX-100-002' }, { number: '2', name: 'TS02 Two', cards: 'TC-RX-100-003' }];
  const pack = readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({ cards, sets, extra: [
    sheet('Objective Matrix', ['Testing Objective', 'Applicable / Not Applicable', 'Reason', 'Related Test Cards', 'Related Test Lab Test Set'],
      ['Core', 'Applicable', 'why', 'TC-RX-100-001\nTC-RX-100-003', 'TS01 One'], ['Flow', 'Applicable', 'why', 'TC-RX-100-003', 'TS01 One\nTS02 Two']),
    sheet('Rule-to-Test Matrix', ['Rule ID', 'Covered By Test Card(s)', 'Covered By Test Set(s)'], ['RX-001', 'TC-RX-100-001\nTC-RX-100-003', 'TS01 One']),
  ] }))));
  assert.deepEqual(objectiveCardProblems(pack).problems.map((o) => [o.row, o.card]), [[2, 'TC-RX-100-003']]);
  assert.deepEqual(matrixCardProblems(pack).problems.map((o) => o.card), ['TC-RX-100-003']);
  const bare = readPack(write(tmp(), 'q.xlsx', xlsx(packSheets({ cards, sets, extra: [
    sheet('Objective Matrix', ['Testing Objective', 'Reason'], ['Core', 'why']) ] }))));
  const missing = objectiveCardProblems(bare);
  assert.equal(missing.ran, false);
  assert.match(missing.reason, /no related test cards column/);
  assert.equal(matrixCardProblems(bare).ran, false);
  const report = reportOf({ ...fakeScorecard(), consistency: { reference: { dashboardCounts: [], confidence: { values: {}, consistent: true }, matrixCards: matrixCardProblems(bare), objectiveCards: missing }, pack: { dashboardCounts: [], confidence: { values: {}, consistent: true }, matrixCards: { ran: true, problems: [], reason: null }, objectiveCards: { ran: true, problems: [], reason: null } } } });
  assert.match(report, /not checked, the Objective Matrix sheet has no related test cards column/);
});

const emptyQuality = () => ({ junkCells: [], pipelineVocabulary: [], designableNotApplicable: [], unreviewedStrength: [],
  impactedWithoutCard: [], validationFailures: [], paddingCards: [] });

function fakeScorecard() {
  const side = { cards: 1, sets: 1, groups: [], repeats: 0, perSet: [], fullCoverage: null };
  const truth = { ruleRows: 0, matchedById: 0, matchedByText: 0, renumbered: [], unconfirmedIds: [], matchedAmbiguously: 0, notInSource: 0, retiredRules: 0, retiredMissing: [],
    retiredUnmarked: [], differenceList: [], unmatchedStatements: [], untrueRows: [], untrueCards: [], contradictions: [], citedMissing: [] };
  const detail = { retired: { rules: [], spans: [] }, differences: [], rows: [] };
  const checked = { dashboardCounts: [], confidence: { values: {}, consistent: true },
    matrixCards: { ran: true, problems: [], reason: null }, objectiveCards: { ran: true, problems: [], reason: null } };
  return { consistency: { reference: checked, pack: checked },
    truth: { reference: truth, pack: truth, source: { approvedRules: 0, struckSpans: 0, retiredByDocument: [] } },
    floor: { crosswalk: [], unmatched: [], reference: side, pack: side }, model: { run: false, reason: 'x' },
    format: { passed: 0, total: 0, score: 1, scoredAgainst: 'standard', referenceSimilarity: 1, checks: [], style: { reference: {}, pack: {} }, standard: null },
    quality: { reference: emptyQuality(), pack: emptyQuality() }, gate: { complete: true, reasons: [] },
    detail: { reference: detail, pack: detail } };
}

test('reader guards: out-of-range character references, rows without r, relative targets, phonetic runs, ZIP64', () => {
  assert.equal(decodeXml('a &#1114112; b &#xD800; c &#9731;'), 'a &#1114112; b &#xD800; c ☃');
  const files = {
    'xl/workbook.xml': '<workbook><sheets><sheet name="S" sheetId="1" r:id="rId1"/></sheets></workbook>',
    'xl/_rels/workbook.xml.rels': '<Relationships><Relationship Id="rId1" Target="../xl/worksheets/sheet1.xml"/></Relationships>',
    'xl/sharedStrings.xml': '<sst><si><t>base</t><rPh sb="0" eb="1"><t>PHONETIC</t></rPh></si></sst>',
    'xl/worksheets/sheet1.xml': '<worksheet><sheetData><row><c t="s"><v>0</v></c></row><row><c><v>2</v></c><c><v>3</v></c></row></sheetData></worksheet>',
  };
  const [sheet] = readXlsx(zip(files));
  assert.deepEqual(sheet.rows[1].slice(1), ['base']);
  assert.deepEqual(sheet.rows[2].slice(1), ['2', '3']);
  const big = Buffer.from(zip({ 'a.txt': 'x' }));
  big.writeUInt16LE(0xffff, big.length - 12);
  assert.throws(() => readZip(big), /ZIP64/);
});

test('a failure while comparing exits 1, not 2', () => {
  const f = fixtureFiles();
  const blocker = write(f.dir, 'blocker', 'a file, not a folder');
  const run = spawnSync(process.execPath, [BUILD_PACK, 'compare', '--reference', f.reference, '--pack', f.pack, '--rules', f.rules,
    '--doc', f.doc, '--out', path.join(blocker, 'out')], { encoding: 'utf8' });
  assert.equal(run.status, 1);
  assert.match(run.stderr, /compare failed/);
});

test('a merged row is split into its statements and maps to each rule they match', () => {
  const mk = (id, text) => ({ id, name: id, status: 'active', page: '1', risk: 'High', summary: text,
    description: `"${text}"\n\nAtomic Summary:\nx` });
  const rules = [mk('RX-020', 'System saves the chosen value when the user selects Apply.'),
    mk('RX-021', 'System updates the status field after a successful apply.'),
    mk('RX-022', 'System refreshes the account grid after a successful apply.'),
    mk('RX-023', 'System updates the balance column after a successful apply.'),
    mk('RX-024', 'System prints the receipt after payment.')];
  const row = { id: '', name: 'Selecting Apply saves the chosen value, updates the status field, refreshes the account grid.', summary: '' };
  assert.deepEqual(matchRuleRow(row, rules).rules.map((r) => r.id).sort(), ['RX-020', 'RX-021', 'RX-022']);
  const single = matchRuleRow({ id: '', name: 'The system prints the receipt after payment.', summary: '' }, rules);
  assert.deepEqual(single.rules.map((r) => r.id), ['RX-024']);
});

test('cards citing the same rules repeat across prose, but wording alone is not chained from card to card', () => {
  const c = (id, focus, rules) => card(id, id, focus, { rulesCovered: rules });
  const cards = [c('a1', 'Search for a provider by surname.', 'R1'), c('a2', 'Search quickly for something else entirely.', 'R2'),
    c('a3', 'Search for a provider using a surname.', 'R1'), c('a4', 'Search for tomatoes in the garden shed.', 'R2')];
  const { groups } = repeatedCards(cards, scenarioModel(cards), (x) => [x.rulesCovered]);
  assert.deepEqual(groups.map((g) => g.cards), [['a1', 'a3'], ['a2', 'a4']]);
});

test('one statement that matches a rule adds no rule beyond the whole-row match', () => {
  const mk = (id, text) => ({ id, name: id, status: 'active', page: '1', risk: 'High', summary: text,
    description: `(Rule Set A, Page 1) "${text}"\n\nAtomic Summary:\nx` });
  const rules = [mk('RX-030', 'System saves the chosen value when the user selects Apply.'),
    mk('RX-031', 'System updates the status field after a successful apply.'),
    mk('RX-032', 'System prints the receipt after payment.')];
  const row = { id: '', name: 'Selecting Apply saves the chosen value, and the page looks tidy.', summary: '' };
  assert.deepEqual(matchRuleRow(row, rules).rules.map((r) => r.id), ['RX-030']);
});

test('a negation in an Expected Result carries through a list but not into a new statement', () => {
  assert.equal(outcomeOf('No warning, role saved.'), 'goes through');
  assert.equal(outcomeOf('No warning, error, or prompt appears.'), 'neutral');
  assert.equal(outcomeOf('No warning message role saved.'), 'goes through');
});

test('Yes, No and screen sections are not controls unless an instruction names them', () => {
  assert.deepEqual(controlNames(['The Role Detail section shows the role. Choose Save or Reset.']).sort(), ['Reset', 'Save']);
  assert.deepEqual(controlNames(['Answer Yes or No in the dialog. The Save and Reset buttons close it.']).sort(), ['Reset', 'Save']);
  assert.deepEqual(controlNames(['Select No.']), ['No']);
});

test('the "does it follow" prompt marks retired rules, gives stale rules the document\'s live text, and says the document wins', async () => {
  const mk = (id, summary) => ({ id, summary, name: id, status: 'active', page: '1', risk: 'High', description: summary });
  const rules = [mk('RX-040', 'System shows a warning before saving.'), mk('RX-041', 'System asks for confirmation before saving.'),
    mk('RX-042', 'System saves the role.')];
  const cards = [{ id: 'TC-ABC-1234-001', title: 't', mission: 'm', focus: 'f', expected: 'The role saves with no warning.' }];
  const prompts = [];
  const client = { json: async (request) => { prompts.push(request); return { value: { follows: true, reason: 'ok' } }; } };
  const truth = (stale) => ({ cardRules: new Map([['TC-ABC-1234-001', { ids: ['RX-040', 'RX-041', 'RX-042'] }]]), stale });
  const doc = { lines: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', '- ~~a confirmation prompt appears~~ Saving the role shows no warning.', '* ', '- ~~a lone deleted bullet~~', '*'] };
  const struck = { text: 'a confirmation prompt appears', line: 10, endLine: 10 };
  const deleted = { text: 'a lone deleted bullet', line: 12, endLine: 12 };
  const out = await modelPass({ client, rules, doc, unmatched: [], retired: new Map([['RX-040', { span: { text: 'a warning shows before saving', line: 9, endLine: 9 } }]]),
    stale: new Map([['RX-041', struck], ['RX-042', deleted]]),
    reference: { pack: { cards }, truth: truth([]) },
    pack: { pack: { cards: cards.map((c) => ({ ...c, id: 'TC-ABC-1234-002' })) }, truth: { cardRules: new Map([['TC-ABC-1234-002', { ids: ['RX-041'] }]]) } } });
  assert.equal(out.follows.length, 2);
  assert.match(prompts[1].user, /RX-041: .*\n  STALE\..*"Saving the role shows no warning\."/s);
  const asked = prompts[0];
  assert.match(asked.system, /document wins/);
  assert.match(asked.user, /RX-040: RETIRED\. The document strikes this behavior out/);
  assert.match(asked.user, /RX-041: System asks for confirmation before saving\.\n  STALE\..*"Saving the role shows no warning\."/s);
  assert.match(asked.user, /RX-042: System saves the role\.\n  STALE\..*puts nothing in its place/s);
});

test('a "no" about a card that joined a repeat group by its rules takes it out of the group', async () => {
  const c = (id, focus) => card(id, id, focus, { rulesCovered: 'R1' });
  const cards = [c('a1', 'Search for a provider by surname.'), c('a2', 'Search for a provider by surname again.'),
    c('a3', 'Search for a provider by surname, then review every provider listed in the result grid.')];
  const model = scenarioModel(cards);
  const found = repeatedCards(cards, model, (x) => [x.rulesCovered]);
  assert.deepEqual(found.groups.map((g) => g.cards), [['a1', 'a2', 'a3']]);
  assert.deepEqual(found.doubtful.map((d) => d.card), ['a3']);
  const asked = [];
  const client = { json: async (request) => { asked.push(request.user); return { value: { same: false, reason: 'differs' } }; } };
  const out = await modelPass({ client, rules: [], unmatched: [], reference: { pack: { cards: [] }, truth: { cardRules: new Map() } },
    pack: { pack: { cards: cards.map((x) => ({ ...x, title: x.id, mission: '', expected: '' })) }, truth: { cardRules: new Map() } },
    doubtful: { pack: found.doubtful } });
  assert.equal(asked.length, 1);
  assert.deepEqual(out.grouped.map((g) => [g.card, g.first, g.same]), [['a3', 'a1', false]]);
  const split = splitGroups(found.groups, new Set(['a3']), cards.length);
  assert.deepEqual(split.groups.map((g) => g.cards), [['a1', 'a2'], ['a3']]);
  assert.equal(split.repeats, 1);
});

test('control names stop at a clause break and drop a screen section only where the section word follows', () => {
  const text = 'Upon selecting "Ok," the error message will close, and the "Verified Role" dropdown shows. The Role Detail section opens. Select Role Detail.';
  assert.deepEqual(controlNames([text]).sort(), ['Ok', 'Role Detail']);
  assert.deepEqual(controlNames(['Select Save, Reset and Save & Close.']).sort(), ['Reset', 'Save', 'Save & Close']);
});

// ---- wording before ID, the standard, the gate and the quality checks ----------

test('a row whose ID the wording does not back is renumbered or unconfirmed, and only then is risk and page left alone', () => {
  const { rules, doc, retired } = source();
  const own = { id: 'RX-001', name: '', summary: 'System saves the selected role when the user selects Save.' };
  assert.equal(matchRuleRow(own, rules).how, 'id');
  // The wording is RX-002's; the number is an old one.
  const old = { id: 'RX-001', name: '', summary: 'System blocks a downgrade for a child with a substantiated sex abuse allegation.' };
  const renumbered = matchRuleRow(old, rules);
  assert.deepEqual([renumbered.how, renumbered.rule.id, renumbered.claimedId], ['renumbered', 'RX-002', 'RX-001']);
  // No rule reads like it: the ID stays, and says it is unconfirmed.
  const odd = { id: 'RX-001', name: '', summary: 'The printer toner runs out.' };
  const unconfirmed = matchRuleRow(odd, rules);
  assert.deepEqual([unconfirmed.how, unconfirmed.rule.id], ['id-unconfirmed', 'RX-001']);
  const pack = readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({ impact: [
    { id: 'RX-001', summary: old.summary, risk: 'Low', page: '9' }, { id: 'RX-001', summary: odd.summary, risk: 'Low', page: '9' }] }))));
  const truth = truthOf(pack, { rules, doc, retired });
  // The renumbered row is held to RX-002's risk and page; the unconfirmed row is held to nothing.
  assert.deepEqual(truth.differences.map((d) => [d.row, d.rule, d.field]), [[2, 'RX-002', 'risk'], [2, 'RX-002', 'page']]);
});

test('a renumbered row with the right risk and page makes no difference', () => {
  const { rules, doc, retired } = source();
  const pack = readPack(write(tmp(), 'p.xlsx', xlsx(packSheets({ impact: [
    { id: 'RX-001', summary: 'System blocks a downgrade for a child with a substantiated sex abuse allegation.', risk: 'High', page: '1' }] }))));
  assert.deepEqual(truthOf(pack, { rules, doc, retired }).differences, []);
});

test('the format score is against the standard, and matching the reference layout does not raise it', () => {
  const data = { impact: [{ id: 'RX-001', summary: 'x' }], cards: [{ id: 'TC-RX-100-001', title: 't', focus: 'f', expected: 'e' }],
    steps: [{ name: 'TC-RX-100-001', step: 'Step 1', expected: 'e' }] };
  const dir = tmp();
  const reference = readPack(write(dir, 'r.xlsx', xlsx(packSheets({ titled: true, ...data }))));
  const lookalike = readPack(write(dir, 's.xlsx', xlsx(packSheets({ titled: true, ...data }))));
  const plain = readPack(write(dir, 'p.xlsx', xlsx(packSheets(data))));
  const standard = parseStandard('## Required Worksheets\n\n1. Impact Analysis\n2. Gate Sheet\n');
  const copy = formatChecks(reference, lookalike, standard);
  assert.equal(copy.referenceSimilarity, 1);
  assert.equal(copy.scoredAgainst, 'standard');
  assert.equal(copy.score, 0.5, 'the copy lacks a sheet the standard requires');
  const other = formatChecks(reference, plain, parseStandard('## Required Worksheets\n\n1. Impact Analysis\n2. Test Cards Markdown\n'));
  assert.ok(other.referenceSimilarity < 1);
  assert.equal(other.score, 1, 'the layout differs from the reference, but the standard is met');
  assert.equal(formatChecks(reference, plain).scoredAgainst, 'reference layout (no standard given)');
});

test('a config turns the model pass and the config standard on, --no-model turns the model off, and the gate says what is missing', async () => {
  const f = fixtureFiles();
  const client = { json: async (r) => ({ value: r.schemaName === 'follows' ? { follows: true, reason: 'ok' } : { same: true, reason: 'ok' } }) };
  const base = { reference: f.reference, pack: f.pack, rules: f.rules, docs: [f.doc] };
  const standard = '## Required Worksheets\n\n1. Impact Analysis\n';
  const on = await runCompare({ ...base, out: path.join(f.dir, 'o1'), config: 'x.json' }, { makeClient: () => client, standardFrom: () => standard });
  assert.ok(on.some((l) => l.includes('model   run')));
  const scorecard = JSON.parse(fs.readFileSync(path.join(f.dir, 'o1', 'compare.json'), 'utf8'));
  assert.equal(scorecard.format.scoredAgainst, 'standard');
  assert.deepEqual(scorecard.gate, { complete: true, reasons: [] });
  const off = await runCompare({ ...base, out: path.join(f.dir, 'o2'), config: 'x.json', noModel: true },
    { makeClient: () => { throw new Error('no client'); }, standardFrom: () => standard });
  assert.ok(off.some((l) => l.includes('model   not run')));
  const gate = JSON.parse(fs.readFileSync(path.join(f.dir, 'o2', 'compare.json'), 'utf8')).gate;
  assert.equal(gate.complete, false);
  assert.match(gate.reasons.join(' '), /model pass was not run/);
  await assert.rejects(runCompare({ ...base, out: path.join(f.dir, 'o3'), config: 'x.json', model: true, noModel: true },
    { makeClient: () => client }), /cannot both be given/);
  assert.deepEqual(parseArgs(['compare', '--no-model']).noModel, true);
  assert.equal(gateOf({ standard: {}, model: { run: true, errors: 2 } }).complete, false);
  assert.match(gateOf({ standard: null, model: { run: true, errors: 0 } }).reasons[0], /no workbook standard/);
});

test('junk cells are found by kind, and ordinary text is not junk', () => {
  for (const [value, kind] of [['[', 'only punctuation'], [' ]; ', 'only punctuation'], ['undefined', 'a program value'],
    ['[object Object]', 'a program value'], ['{"level": "High"}', 'a JSON fragment']]) assert.equal(junkKind(value), kind, value);
  for (const value of ['', 'High', 'Role (see page 2)', '- not a junk cell, it has words', 'null pointer handling is out of scope']) {
    assert.equal(junkKind(value), null, value);
  }
});

test('the quality checks find each problem the shipped workbook had, and a clean workbook has none', () => {
  const sheets = (extra) => packSheets({ impact: [
    { id: 'RX-001', summary: 'System saves the selected role when the user selects Save.' },
    { id: 'RX-002', summary: 'System blocks a downgrade for a child with a sex abuse allegation.' }],
  cards: [{ id: 'TC-RX-100-001', title: 'Save', focus: 'Select Save.', expected: 'Saved.', rules: 'RX-001' },
    { id: 'TC-RX-100-002', title: 'Old warning', focus: 'Select Save.', expected: 'A warning shows.', rules: 'RX-003' }], extra });
  const { rules, doc, retired } = source();
  const run = (extra) => {
    const pack = readPack(write(tmp(), 'q.xlsx', xlsx(sheets(extra))));
    return qualityChecks(pack, truthOf(pack, { rules, doc, retired }), retired);
  };
  const dirty = run([
    sheet('Confidence Assessment', ['Item', 'Detail'], ['Overall', '[']),
    sheet('Assumptions', ['Assumption ID', 'Assumption', 'Why Required'], ['A-1', 'The project understanding says the role saves.', 'Needed'],
      ['A-2', 'Roles are unique.', 'Not stated by the review.']),
    sheet('Objective Matrix', ['Testing Objective', 'Status', 'Reason'], ['Role / Population', 'Not Applicable', 'No test card could be designed in this run.'],
      ['Audit', 'Not Applicable', 'The page has no audit trail.']),
    sheet('Coverage Matrix', ['Rule ID', 'Coverage Status', 'Coverage Strength', 'Gap / Concern'], ['RX-001', 'Covered', 'Strong', 'Not reviewed; coverage rests on the card mapping.'],
      ['RX-002', 'Covered', 'Strong', 'Checked against the page.']),
    sheet('Workbook Validation', ['Check', 'Status', 'Notes'], ['Cards', 'PASS', ''], ['Sets', 'FAIL', 'One set is empty.']),
  ]);
  assert.deepEqual(dirty.junkCells.map((x) => [x.sheet, x.row]), [['Confidence Assessment', 2]]);
  assert.deepEqual(dirty.pipelineVocabulary.map((x) => [x.sheet, x.row, x.column]), [['Assumptions', 2, 'Assumption'], ['Assumptions', 3, 'Why Required']]);
  assert.deepEqual(dirty.designableNotApplicable.map((x) => x.objective), ['Role / Population']);
  assert.deepEqual(dirty.unreviewedStrength.map((x) => x.rule), ['RX-001']);
  assert.deepEqual(dirty.validationFailures.map((x) => [x.check, x.status]), [['Sets', 'FAIL']]);
  assert.deepEqual(dirty.impactedWithoutCard.map((x) => x.rule), ['RX-002']);
  assert.deepEqual(dirty.paddingCards.map((x) => [x.card, x.rules]), [['TC-RX-100-002', ['RX-003']]]);
  const clean = run([
    sheet('Assumptions', ['Assumption ID', 'Assumption', 'Why Required'], ['A-1', 'Roles are unique.', 'The page lists one role per child.']),
    sheet('Objective Matrix', ['Testing Objective', 'Status', 'Reason'], ['Audit', 'Not Applicable', 'The page has no audit trail.']),
    sheet('Coverage Matrix', ['Rule ID', 'Coverage Status', 'Coverage Strength', 'Gap / Concern'], ['RX-001', 'Covered', 'Strong', 'Checked against the page.']),
    sheet('Workbook Validation', ['Check', 'Status', 'Notes'], ['Cards', 'PASS', '']),
  ]);
  for (const key of ['junkCells', 'pipelineVocabulary', 'designableNotApplicable', 'unreviewedStrength', 'validationFailures']) {
    assert.deepEqual(clean[key], [], key);
  }
});

test('a card about removing a warning, or asserting it is absent, does not use the retired warning', () => {
  const struckOnly = struckOnlyWords(source().doc);
  assert.ok(struckOnly.has('warn'), 'the struck text makes "warning" retired wording');
  assert.deepEqual(staleHits('FATL Downgrade Warning Removal - Save', struckOnly), []);
  assert.deepEqual(staleHits('The warning is suppressed and the role saves.', struckOnly), []);
  assert.deepEqual(staleHits('The role saves and does not display the warning.', struckOnly), []);
  assert.equal(staleHits('A warning shows before the role saves.', struckOnly).length, 1);
});

test('cards that only share an action with a reference card never make it covered', () => {
  const controls = ['Save', 'Reset'];
  const reference = [card('r1', 'Save then reset', 'Select Save, then select Reset for the account.')];
  const pack = [card('p1', 'Reset only', 'Select Reset for the account.')];
  const found = crosswalkCards(reference, pack, () => [], scenarioModel([...reference, ...pack], { controls }));
  assert.notEqual(found[0].status, 'covered');
  assert.notEqual(found[0].status, 'unmatched');
  // Two cards that each do one action do not add up to a card that does both.
  const split = [card('p2', 'Save it', 'Select Save for the account.'), card('p3', 'Reset it', 'Select Reset for the account.')];
  const parts = crosswalkCards(reference, split, () => [], scenarioModel([...reference, ...split], { controls }));
  assert.notEqual(parts[0].status, 'covered');
  // A strong card that does it all is still covered when a weaker card was combined first.
  const both = [card('p4', 'Save then reset', 'Select Save, then select Reset for the account.'), ...split];
  assert.equal(crosswalkCards(reference, both, () => [], scenarioModel([...reference, ...both], { controls }))[0].status, 'covered');
});

test('a placeholder dash, a passed row and a rule that applies elsewhere are not quality problems', () => {
  assert.equal(junkKind('-'), null);
  assert.equal(junkKind('.'), null);
  assert.equal(junkKind('The label "Role": "shows" the name'), null);
  const pack = readPack(write(tmp(), 'v.xlsx', xlsx([
    sheet('Workbook Validation', ['Check', 'Status', 'Notes'], ['Cards', 'Passed', '']),
    sheet('Objective Matrix', ['Testing Objective', 'Status', 'Reason'], ['Adults', 'Not Applicable', 'The rule only applies to adults.'])])));
  const found = qualityChecks(pack, { rows: [], cardRules: new Map() }, new Map());
  assert.deepEqual([found.validationFailures, found.designableNotApplicable], [[], []]);
});

test('the model pass flags a step a rule forbids, including a rule the card does not cite', async () => {
  const rules = [{ id: 'VS-030', summary: 'Selecting Save stores the role.' },
    { id: 'VS-032', summary: 'The Save button is enabled only after the dropdown value changes.' }];
  const mkPack = () => ({ cards: [{ id: 'TC-001', title: 't', mission: 'm', focus: 'f', expected: 'The role saves.' }],
    steps: [{ testName: 'TC-001-01', description: 'Leave the dropdown unchanged', expected: 'No change' },
      { testName: 'TC-001-02', description: 'Select Save', expected: 'The role saves' }] });
  const prompts = [];
  const client = { json: async (request) => {
    prompts.push(request);
    if (request.schemaName !== 'steps') return { value: { follows: true, reason: 'ok', same: true } };
    // The reply as the server sends it: a step row's properties carry their numbers.
    return { value: { cards: [{ card: 'C1', steps: [{ '01_step': 1, '02_possible': true, '03_why': 'fine' },
      { '01_step': 2, '02_possible': false, '03_why': 'VS-032 keeps Save disabled until a change' }] }] } };
  } };
  const truth = { cardRules: new Map([['TC-001', { ids: ['VS-030'] }]]) };
  const out = await modelPass({ client, rules, unmatched: [], controls: ['Save'],
    reference: { pack: { cards: [], steps: [] }, truth: { cardRules: new Map() } }, pack: { pack: mkPack(), truth } });
  assert.deepEqual(out.steps.map((s) => [s.workbook, s.card, s.flagged]),
    [['pack', 'TC-001', [{ step: 2, why: 'VS-032 keeps Save disabled until a change' }]]]);
  const asked = prompts.find((p) => p.schemaName === 'steps');
  assert.match(asked.user, /VS-032: The Save button is enabled only after/);
  assert.deepEqual(Object.keys(asked.schema.properties.cards.items.properties.steps.items.properties).sort(),
    ['01_step', '02_possible', '03_why']);
  assert.equal(out.errors, 0);
});

test('without control names the model pass asks no step question', async () => {
  const asked = [];
  const client = { json: async (request) => { asked.push(request.schemaName); return { value: { follows: true, reason: '' } }; } };
  const out = await modelPass({ client, rules: [], unmatched: [], reference: { pack: { cards: [], steps: [] }, truth: { cardRules: new Map() } },
    pack: { pack: { cards: [], steps: [] }, truth: { cardRules: new Map() } } });
  assert.deepEqual(out.steps, []);
  assert.ok(!asked.includes('steps'));
});
