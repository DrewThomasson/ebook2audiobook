// Quality checks on one pack workbook: text that should never ship in a
// cell, and rows whose stated reason or strength the rest of the workbook
// contradicts. None calls a model. Each check returns the places it found,
// as { sheet, row, ... } objects with Excel row numbers, so a report can
// name them without quoting a whole cell.

import { cell } from './pack.mjs';
import { FILLED_GAP } from './pack-checks.mjs';

const text = (value) => String(value ?? '').trim();

// A cell that holds only brackets and punctuation, or a value a program printed by mistake.
const JUNK_ONLY = /^[[\]{}(),;:"'\\]+$/;
const JUNK_WORD = /^(?:undefined|null|nan|\[object object\])$/i;
// A JSON fragment where prose belongs.
const JSON_FRAGMENT = /^\s*[[{]\s*"[^"]+"\s*:|^\s*\[\s*\{/;

/** Whether one cell value is junk, and which kind. Returns a short label or null. */
export function junkKind(value) {
  const t = text(value);
  if (!t) return null;
  if (JUNK_ONLY.test(t)) return 'only punctuation';
  if (JUNK_WORD.test(t)) return 'a program value';
  if (JSON_FRAGMENT.test(t)) return 'a JSON fragment';
  return null;
}

/** Cells that hold junk, on every sheet. */
export function junkCells(pack) {
  const found = [];
  for (const sheet of pack.sheets) {
    for (const row of sheet.rows) {
      for (const [column, value] of Object.entries(row.cells)) {
        const kind = junkKind(value);
        if (kind) found.push({ sheet: sheet.name, row: row.n, column, kind });
      }
    }
  }
  return found;
}

// Words of the pipeline that built the pack. A tester reading the workbook has no use for them.
const PIPELINE_WORDS = /\b(?:project understanding|supplied (?:context|documents?|rules)|the builder|rules section|this run|the pipeline|phase \d|checkpoint|the review(?:er)? (?:did|gave|stated|returned)|the model)\b/i;

/** Assumptions and validation notes written in the pipeline's vocabulary. */
export function pipelineVocabulary(pack) {
  const found = [];
  const look = (sheetName, columns) => {
    for (const row of pack.sheet(sheetName)?.rows ?? []) {
      for (const column of columns) {
        const value = text(cell(row, column));
        const hit = PIPELINE_WORDS.exec(value) ?? (FILLED_GAP.test(value) ? [value.slice(0, 40)] : null);
        if (hit) found.push({ sheet: sheetName, row: row.n, column, word: hit[0] });
      }
    }
  };
  look('Assumptions', ['Assumption', 'Why Required', 'Potential Impact', 'Reason']);
  look('Workbook Validation', ['Notes', 'Note', 'Details']);
  return found;
}

const NOT_APPLICABLE = /^not applicable$|^n\/a$/i;
// A reason that says the objective could be tested: it is not a reason to skip it.
const COULD_BE_TESTED = /could be designed|can be designed|could be tested|can be tested|no test card could/i;

/** Objective Matrix rows marked Not Applicable for a reason that says the objective applies. */
export function designableNotApplicable(pack) {
  const found = [];
  for (const row of pack.sheet('Objective Matrix')?.rows ?? []) {
    const status = Object.entries(row.cells).find(([k]) => /status|applicab/i.test(k))?.[1];
    if (!NOT_APPLICABLE.test(text(status))) continue;
    const reason = Object.entries(row.cells).find(([k]) => /reason|rationale|notes?|gap/i.test(k))?.[1];
    if (COULD_BE_TESTED.test(text(reason))) {
      found.push({ sheet: 'Objective Matrix', row: row.n, objective: text(Object.values(row.cells)[0]), reason: text(reason).slice(0, 120) });
    }
  }
  return found;
}

/** Coverage Matrix rows that read Strong while their own Gap / Concern says nothing was reviewed. */
export function unreviewedStrength(pack) {
  const found = [];
  for (const row of pack.sheet('Coverage Matrix')?.rows ?? []) {
    const strength = Object.entries(row.cells).find(([k]) => /strength/i.test(k))?.[1];
    if (!/^strong$/i.test(text(strength))) continue;
    const gap = Object.entries(row.cells).find(([k]) => /gap/i.test(k))?.[1];
    if (FILLED_GAP.test(text(gap))) found.push({ sheet: 'Coverage Matrix', row: row.n, rule: text(cell(row, 'Rule ID')) });
  }
  return found;
}

/** Workbook Validation rows whose status is not PASS. */
export function validationFailures(pack) {
  const found = [];
  for (const row of pack.sheet('Workbook Validation')?.rows ?? []) {
    const status = Object.entries(row.cells).find(([k]) => /status|result|pass/i.test(k))?.[1];
    const values = Object.values(row.cells).map(text);
    const verdict = text(status) || values.find((v) => /^(?:pass|fail|warn\w*)$/i.test(v)) || '';
    if (verdict && !/^(?:pass|passed|ok)$/i.test(verdict)) found.push({ sheet: 'Workbook Validation', row: row.n, status: verdict, check: values[0] });
  }
  return found;
}

const RETIRED_OR_NOT_IMPACTED = /not impacted|supersed|retire|remov/i;

/**
 * Rule rows an impact analysis says are impacted that no card cites, whatever a
 * reference pack does. `truthRows` is the crosswalk of the pack's rule rows and
 * `cited` the set of approved rule IDs any card cites.
 */
export function impactedWithoutCard(pack, truthRows, cited) {
  return truthRows.filter((r) => r.match && !r.marked && !RETIRED_OR_NOT_IMPACTED.test(r.row.classification)
    && !r.match.rules.some((rule) => cited.has(rule.id)) && !(r.match.claimedId && cited.has(r.match.claimedId))).map((r) => ({
    sheet: 'Impact Analysis', row: r.row.n, rule: r.match.rules[0].id, classification: r.row.classification }));
}

/**
 * Cards that cite only rules the document retired: their scenario is gone, so
 * they pad the pack. Returns [{ card, row, rules }].
 */
export function paddingCards(pack, cardRules, retired) {
  return pack.cards.map((card) => ({ card: card.id, row: card.n, rules: cardRules.get(card.id)?.ids ?? [] }))
    .filter((c) => c.rules.length && c.rules.every((id) => retired.has(id)));
}

/** Every quality check on one pack. `truth` is truthOf's result and `retired` the document's retired rules. */
export function qualityChecks(pack, truth, retired) {
  const cited = new Set([...truth.cardRules.values()].flatMap((r) => r.ids));
  return {
    junkCells: junkCells(pack),
    pipelineVocabulary: pipelineVocabulary(pack),
    designableNotApplicable: designableNotApplicable(pack),
    unreviewedStrength: unreviewedStrength(pack),
    impactedWithoutCard: impactedWithoutCard(pack, truth.rows, cited),
    validationFailures: validationFailures(pack),
    paddingCards: paddingCards(pack, truth.cardRules, retired),
  };
}
