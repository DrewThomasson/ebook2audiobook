// The stub with a confidence ceiling, as a builder module and as a builder command. The
// ceiling comes from the assumptions the pack carries: more than 10 hold it to Low, more
// than 3 to Medium. As a module it has the stub's exports, `confidenceCeiling`, and a
// `buildPack` that fails Confidence Assessment for a rating above the ceiling. The
// command adds a check that the Executive Summary confidence starts with the overall
// one. A pack that breaks either check is refused: every sheet is printed with its
// status, a failing one with its reason indented under it, and no workbook is written.
// Any other pack goes to the stub's command line.
//
//   node builder-ceiling.mjs <pack.json> --out <dir>

import fs from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { buildPack as stubBuild, CONFIDENCE_LEVELS } from './builder-stub.mjs';

export * from './builder-stub.mjs';

/** The most assumptions a pack may carry and still be rated at each level. */
export const CONFIDENCE_CEILINGS = { High: 3, Medium: 10 };

/** The highest overall confidence the pack supports, and what holds it there. */
export function confidenceCeiling(pack) {
  const count = Array.isArray(pack.assumptions) ? pack.assumptions.length : 0;
  const reason = (level) => `${count} assumptions against a limit of ${CONFIDENCE_CEILINGS[level]}`;
  if (count > CONFIDENCE_CEILINGS.Medium) return { level: 'Low', reasons: [reason('Medium')] };
  if (count > CONFIDENCE_CEILINGS.High) return { level: 'Medium', reasons: [reason('High')] };
  return { level: 'High', reasons: [] };
}

/** What is wrong with a rating above the ceiling, or nothing. */
function ceilingProblem(pack) {
  const overall = pack.confidence?.overall;
  const ceiling = confidenceCeiling(pack);
  if (!CONFIDENCE_LEVELS.includes(overall)
    || CONFIDENCE_LEVELS.indexOf(overall) >= CONFIDENCE_LEVELS.indexOf(ceiling.level)) return '';
  return `overall confidence ${overall} is more than the pack supports: ${ceiling.reasons.join('; ')};`
    + ` rate it ${ceiling.level === 'Low' ? 'Low' : `${ceiling.level} or lower`}`;
}

/** The stub's build, with Confidence Assessment failed for a rating above the ceiling. */
export function buildPack(pack) {
  const built = stubBuild(pack);
  const problem = ceilingProblem(pack);
  if (built.stop || !problem) return built;
  const validation = built.validation.map((row) => (row[0] === 'Confidence Assessment'
    ? [row[0], row[1], row[2], 'FAIL', [row[4], problem].filter(Boolean).join('\n')] : row));
  return { ...built, validation, failed: validation.filter((row) => row[3] === 'FAIL') };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const pack = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const overall = pack.confidence?.overall;
  const problems = {};
  if (ceilingProblem(pack)) problems['Confidence Assessment'] = ceilingProblem(pack);
  const summary = String(pack.executiveSummary?.confidence ?? '');
  if (overall && !summary.startsWith(overall)) {
    problems['Executive Summary'] = `confidence starts "${summary.split(/[.\s]/)[0]}", which does not`
      + ` match the overall confidence "${overall}"`;
  }

  if (!Object.keys(problems).length) {
    const stub = fileURLToPath(new URL('./builder-stub.mjs', import.meta.url));
    const result = spawnSync(process.execPath, [stub, ...process.argv.slice(2)], { encoding: 'utf8' });
    process.stdout.write(result.stdout);
    process.stderr.write(result.stderr);
    process.exit(result.status ?? 1);
  }
  for (const [sheet, , , status] of stubBuild(pack).validation ?? []) {
    const failed = Boolean(problems[sheet]) || sheet === 'Workbook Validation';
    console.log(`${(failed ? 'FAIL' : status).padEnd(22)} ${sheet}`);
    if (problems[sheet]) console.log(`    ${problems[sheet]}`);
  }
  process.exit(1);
}
