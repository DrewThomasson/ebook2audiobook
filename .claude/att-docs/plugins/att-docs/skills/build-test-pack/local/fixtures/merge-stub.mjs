// A small stand-in for a repository's suite merge, with the export and the
// call shape the pipeline uses: mergeSuitePack({ exportJson, designed, narrative }).

export const SUITE_SET_ORDER = ['Workflow Validation', 'Negative / Exclusion', 'Regression Testing',
  'Full Coverage Required Run', 'BREAK IT'];
const RUN_SETS = ['Regression Testing', 'Full Coverage Required Run'];

export function mergeSuitePack({ exportJson, designed, narrative }) {
  const rules = [];
  const testCards = [];
  const coverage = [];
  const sourceDocuments = [];
  for (const doc of exportJson.exports) {
    const code = doc.prefix.replace(/^BR-[A-Z0-9]+\./, '');
    const [module, abbreviation] = narrative.modules[code];
    const active = doc.rules.filter((rule) => rule.status === 'active');
    const sourceDocument = active[0].source_document;
    sourceDocuments.push({ name: sourceDocument, inclusion: 'Included',
      authority: narrative.sourceAuthority, reason: 'holds the approved rules' });
    for (const rule of active) {
      rules.push({ id: rule.rule_id, name: rule.name, module, sourceDocument,
        sourcePage: rule.source_page, summary: rule.rule_summary, risk: rule.risk_level,
        impact: 'Regression', rationale: 'Suite baseline' });
    }
    designed[code].cards.forEach((card, i) => testCards.push({ ...card,
      id: `TC-${abbreviation}-${narrative.suite}-${String(i + 1).padStart(3, '0')}`,
      module, sourceDocument,
      objectives: card.derivation === 'Quality' ? card.objectives
        : [...new Set([...card.objectives, ...RUN_SETS])] }));
    coverage.push(...designed[code].uncovered);
  }
  const testSets = SUITE_SET_ORDER.map((objective) => ({ objective,
    cards: testCards.filter((card) => card.objectives.includes(objective)) }))
    .filter((set) => set.cards.length).map((set, i) => ({ number: i + 1,
      name: `TS${i + 1} ${set.objective}`, objective: set.objective,
      scope: narrative.setScopes[set.objective], ruleSummary: ['summary'],
      cards: set.cards.map((card) => card.id) }));
  const run = new Set(testSets.map((set) => set.objective));
  return { ...narrative, suite: narrative.suite, sourceDocuments, rules, testCards, testSets, coverage,
    objectives: narrative.objectives.map((row) => ({ ...row, applicable: run.has(row.objective) })) };
}
