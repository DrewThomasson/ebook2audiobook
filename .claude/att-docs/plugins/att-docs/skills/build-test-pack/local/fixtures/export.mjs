// Stands in for a repository's rule export: prints the synthetic master's
// export for one document as one object, or for every document under a folder. A document
// the master does not hold fails the way the real export does.
//
//   node export.mjs --doc <path> [--master <file>]

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const flag = (name) => (process.argv.includes(name)
  ? process.argv[process.argv.indexOf(name) + 1] : undefined);
const master = JSON.parse(fs.readFileSync(path.join(here, flag('--master') ?? 'master.json'), 'utf8'));
const doc = flag('--doc').replace(/\/$/, '');
const exports = master.exports.filter((row) => row.doc === doc || row.doc.startsWith(`${doc}/`));
if (!exports.length) {
  process.stderr.write(`${doc} is not in br_doc_map; a doc with no rules yet is extracted, not updated\n`);
  process.exit(1);
}
// One mapped document prints as exportDoc writes it; a folder prints its documents.
const [only] = exports;
const out = exports.length === 1 && only.doc === doc
  ? { doc: only.doc, prefix: only.prefix, alm_folder_id: null, next_seq: only.rules.length + 1,
    rules: only.rules }
  : { exports };
process.stdout.write(`${JSON.stringify(out)}\n`);
