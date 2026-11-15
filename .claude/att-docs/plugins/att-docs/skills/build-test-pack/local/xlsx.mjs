// Reads the cell text of an .xlsx workbook with no dependency: the zip is
// parsed here (stored and deflated entries), then the workbook, its
// relationships, the shared strings and each sheet's XML.

import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const EOCD_SIGNATURE = 0x06054b50;
const CENTRAL_SIGNATURE = 0x02014b50;
const LOCAL_SIGNATURE = 0x04034b50;

/** Every entry of a zip as a Map of name to its uncompressed bytes. */
export function readZip(buffer) {
  let end = -1;
  for (let i = buffer.length - 22; i >= Math.max(0, buffer.length - 22 - 0xffff); i -= 1) {
    if (buffer.readUInt32LE(i) === EOCD_SIGNATURE) { end = i; break; }
  }
  if (end < 0) throw new Error('not a zip file');
  const count = buffer.readUInt16LE(end + 10);
  let at = buffer.readUInt32LE(end + 16);
  if (count === 0xffff || at === 0xffffffff) throw new Error('ZIP64 workbooks are not supported');
  const entries = new Map();
  for (let n = 0; n < count; n += 1) {
    if (buffer.readUInt32LE(at) !== CENTRAL_SIGNATURE) throw new Error('zip directory is damaged');
    const method = buffer.readUInt16LE(at + 10);
    const size = buffer.readUInt32LE(at + 20);
    const nameLength = buffer.readUInt16LE(at + 28);
    const extraLength = buffer.readUInt16LE(at + 30);
    const commentLength = buffer.readUInt16LE(at + 32);
    const local = buffer.readUInt32LE(at + 42);
    if (size === 0xffffffff || local === 0xffffffff) throw new Error('ZIP64 workbooks are not supported');
    const name = buffer.toString('utf8', at + 46, at + 46 + nameLength);
    at += 46 + nameLength + extraLength + commentLength;
    if (buffer.readUInt32LE(local) !== LOCAL_SIGNATURE) throw new Error('zip entry is damaged');
    const start = local + 30 + buffer.readUInt16LE(local + 26) + buffer.readUInt16LE(local + 28);
    const packed = buffer.subarray(start, start + size);
    if (method === 0) entries.set(name, packed);
    else if (method === 8) entries.set(name, zlib.inflateRawSync(packed));
    else throw new Error(`zip entry uses unsupported method ${method}`);
  }
  return entries;
}

const ENTITIES = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" };

/** XML text with its entities decoded. */
export function decodeXml(text) {
  return text.replace(/&(#x[0-9a-fA-F]+|#\d+|[a-z]+);/g, (whole, body) => {
    if (body[0] === '#') {
      const code = body[1] === 'x' ? parseInt(body.slice(2), 16) : Number(body.slice(1));
      const valid = Number.isInteger(code) && code >= 0 && code <= 0x10ffff && !(code >= 0xd800 && code <= 0xdfff);
      return valid ? String.fromCodePoint(code) : whole;
    }
    return ENTITIES[body] ?? whole;
  });
}

const attr = (tag, name) => {
  const match = new RegExp(`\\b${name}="([^"]*)"`).exec(tag);
  return match ? decodeXml(match[1]) : undefined;
};

/** All the <t> text of a fragment, rich text runs joined and phonetic runs left out. */
const textOf = (xml) => [...xml.replace(/<rPh\b[\s\S]*?<\/rPh>/g, '').matchAll(/<t(?:\s[^>]*)?>([\s\S]*?)<\/t>/g)]
  .map((m) => decodeXml(m[1])).join('');

/** "AB" -> 28 (one-based column number). */
export function columnNumber(letters) {
  let n = 0;
  for (const ch of letters) n = n * 26 + ch.charCodeAt(0) - 64;
  return n;
}

function sharedStrings(xml) {
  if (!xml) return [];
  return [...xml.matchAll(/<si\b[^>]*>([\s\S]*?)<\/si>|<si\b[^>]*\/>/g)].map((m) => textOf(m[1] ?? ''));
}

function cellText(tag, body, strings) {
  const type = attr(tag, 't');
  if (type === 'inlineStr') return textOf(body);
  const value = /<v>([\s\S]*?)<\/v>/.exec(body)?.[1];
  if (value === undefined) return '';
  if (type === 's') return strings[Number(value)] ?? '';
  return decodeXml(value);
}

/**
 * One sheet's rows as an array indexed by Excel row (index 0 is unused) of
 * arrays indexed by one-based column (index 0 is unused); a gap is ''. Merged
 * ranges repeat their top-left value in every cell they cover.
 */
export function parseSheet(xml, strings) {
  const rows = [];
  const put = (r, c, text) => {
    (rows[r] ??= [])[c] = text;
  };
  let last = 0;
  for (const row of xml.matchAll(/<row\b([^>]*?)(?:\/>|>([\s\S]*?)<\/row>)/g)) {
    // A row without its r attribute follows the one before it.
    const number = Number(attr(row[1], 'r')) || last + 1;
    last = number;
    let next = 0;
    for (const cell of (row[2] ?? '').matchAll(/<c\b([^>]*?)(?:\/>|>([\s\S]*?)<\/c>)/g)) {
      const ref = /^([A-Z]+)(\d+)$/.exec(attr(cell[1], 'r') ?? '');
      next = ref ? columnNumber(ref[1]) : next + 1;
      put(number, next, cellText(cell[1], cell[2] ?? '', strings));
    }
  }
  for (const merge of xml.matchAll(/<mergeCell\b[^>]*\bref="([A-Z]+)(\d+):([A-Z]+)(\d+)"/g)) {
    const [c1, r1, c2, r2] = [columnNumber(merge[1]), Number(merge[2]),
      columnNumber(merge[3]), Number(merge[4])];
    const value = rows[r1]?.[c1] ?? '';
    for (let r = r1; r <= r2; r += 1) {
      for (let c = c1; c <= c2; c += 1) put(r, c, value);
    }
  }
  return rows.map((row) => Array.from(row ?? [], (cell) => cell ?? ''));
}

/** The workbook's sheets in order: [{ name, rows }] as parseSheet describes rows. */
export function readXlsx(file) {
  const zip = readZip(Buffer.isBuffer(file) ? file : fs.readFileSync(file));
  const text = (name) => (zip.has(name) ? zip.get(name).toString('utf8') : '');
  const workbook = text('xl/workbook.xml');
  const rels = new Map([...text('xl/_rels/workbook.xml.rels').matchAll(/<Relationship\b[^>]*>/g)]
    .map((m) => [attr(m[0], 'Id'), attr(m[0], 'Target')]));
  const strings = sharedStrings(text('xl/sharedStrings.xml'));
  return [...workbook.matchAll(/<sheet\b[^>]*>/g)].map((m) => {
    const target = rels.get(attr(m[0], 'r:id')) ?? '';
    const part = target.startsWith('/') ? target.slice(1) : path.posix.normalize(`xl/${target}`);
    return { name: attr(m[0], 'name'), rows: parseSheet(text(part), strings) };
  });
}
