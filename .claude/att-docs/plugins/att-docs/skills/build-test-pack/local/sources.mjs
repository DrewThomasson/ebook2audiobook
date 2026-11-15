// Reads the places new jobs are listed, so the queue fills itself. A source
// gives job lines, one job per line, in the form `queue add` takes:
//
//   9415            an issue
//   9415 7001       an issue and its change
//   suite LIB       a suite
//   --issue 9415 --change 7001 --doc docs/LIB/a.md     the full command-line form
//
// Blank lines and lines starting with # are skipped. Three kinds of source:
//
//   folder   { "type": "folder", "path": "queue-in" }
//            every file in the folder holds job lines; the maintainer drops a list there.
//   records  { "type": "records", "glob": "docs/SIRs/*.md", "pattern": "^SIR-(\\d+)" }
//            one job per record file; the pattern's first group is the issue number and
//            the optional second group is the change number, both read from the file name.
//   command  { "type": "command", "command": ["node", "list-sirs.mjs"] }
//            a command that prints job lines, such as the build's SIR list from ALM.

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { globFiles } from './config.mjs';

// The change id starts with a digit and ends at a separator or the extension, so
// a word that merely begins with "cr" or "change" is not read as a change.
// A "change" or "CR" word right after the issue number that no valid change id
// follows makes the name unreadable, so it is not queued as the issue alone.
const STRAY_CHANGE = /^(?:SIR|ISSUE)[-_ ]?\d+[-_ .]*(?:change|CR)(?![A-Za-z])/i;
const DEFAULT_PATTERN = '^(?:SIR|ISSUE)[-_ ]?(\\d+)(?:[-_ .]*(?:change|CR)[-_ ]?(\\d[A-Za-z0-9]*?)(?=[-_ .]|$))?';

/** The job lines one source lists, or the code for why it could not be read. */
export function sourceLines(config, source) {
  try {
    if (source.type === 'folder') {
      const dir = config.at(source.path);
      if (!fs.existsSync(dir)) return { lines: [], error: 'source-missing' };
      const files = fs.readdirSync(dir, { withFileTypes: true })
        .filter((entry) => entry.isFile() && !entry.name.startsWith('.')).map((entry) => entry.name).sort();
      return { lines: files.flatMap((name) => fs.readFileSync(path.join(dir, name), 'utf8').split('\n')) };
    }
    if (source.type === 'records') {
      const pattern = new RegExp(source.pattern ?? DEFAULT_PATTERN, 'i');
      let invalid = 0;
      const lines = globFiles(config.root, source.glob).flatMap((file) => {
        const name = path.basename(file);
        const found = pattern.exec(name);
        const stray = !source.pattern && found && !found[2] && STRAY_CHANGE.test(name);
        if (!found?.[1] || stray) invalid += 1;
        return found?.[1] && !stray ? [[found[1], found[2]].filter(Boolean).join(' ')] : [];
      });
      return { lines, invalid };
    }
    const argv = source.command;
    const result = spawnSync(argv[0], argv.slice(1), { cwd: config.root, encoding: 'utf8',
      timeout: (source.timeoutMinutes ?? 5) * 60000 });
    if (result.status !== 0) return { lines: [], error: 'source-command-failed' };
    return { lines: result.stdout.split('\n') };
  } catch {
    return { lines: [], error: 'source-unreadable' };
  }
}

/** Splits a job line into the arguments `queue add` would take. */
export function lineArgs(line) {
  const words = line.trim().split(/\s+/);
  if (/^\d+$/.test(words[0])) {
    if (words.length > 2) throw new Error('a job line takes an issue and an optional change');
    return ['--issue', words[0], ...(words[1] ? ['--change', words[1]] : [])];
  }
  if (words[0] === 'suite') {
    if (words.length !== 2) throw new Error('a suite line takes one suite code');
    return ['--suite', words[1]];
  }
  return words;
}
