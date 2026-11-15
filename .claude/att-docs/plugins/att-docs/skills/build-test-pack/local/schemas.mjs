// The JSON schemas each phase's model call answers against. llama.cpp turns
// them into a grammar, so a reply can only take these shapes. Lists of allowed
// values (rule IDs, document names, objectives) are passed in per call.

const str = { type: 'string' };
const strs = { type: 'array', items: str };
const obj = (properties, required = Object.keys(properties)) => ({
  type: 'object', properties, required, additionalProperties: false,
});
const oneOf = (values) => ({ type: 'string', enum: [...values] });
const listOf = (items, extra = {}) => ({ type: 'array', items, ...extra });

// A list with one row per known key is asked for as an object with one
// property per key: the grammar then requires every key exactly once, where a
// list of the right length can repeat one row and leave another out. `fromWire`
// turns the reply back into the list, each row carrying its key in `field`.
// `row` builds each row's schema: `obj`, or `ordered` for a row whose fields
// are worked out in order.
const KEYED = new WeakMap();
const keyed = (field, keys, properties, row = obj) => {
  const schema = obj(Object.fromEntries([...keys].map((key) => [key, row(properties)])));
  KEYED.set(schema, field);
  return schema;
};

// A model server may hand an object's properties to the model sorted alphabetically,
// whatever order the schema lists them in, and the model fills them in that order. An
// object whose fields depend on one another (a reason before the verdict it supports, a
// key before the text about it) is therefore built with `ordered`: the properties
// are given in the order they are worked out, and each is asked for as `01_name`,
// `02_name` and so on, so every sort order is the working order. `fromWire` takes the
// numbers off again, so the rest of the pipeline sees the plain names.
const ORDER = new WeakMap();
export const ordered = (properties) => {
  const names = Object.keys(properties);
  const wire = names.map((name, i) => `${String(i + 1).padStart(2, '0')}_${name}`);
  const schema = obj(Object.fromEntries(names.map((name, i) => [wire[i], properties[name]])));
  ORDER.set(schema, names.map((name, i) => [wire[i], name]));
  return schema;
};

/** The schema of the property `name` of an object schema, whether or not the object is `ordered`. */
export function propOf(schema, name) {
  const wire = ORDER.get(schema)?.find(([, plain]) => plain === name)?.[0] ?? name;
  return schema.properties[wire];
}

/**
 * The reply as the pipeline reads it: each `ordered` object's numbered properties under
 * their plain names, every object's properties in the order the schema lists them, and
 * every keyed object turned back into its list of rows. A reply with its keys in any
 * order gives the same value.
 */
export function fromWire(schema, value) {
  if (!schema || !value || typeof value !== 'object') return value;
  if (Array.isArray(value)) return value.map((item) => fromWire(schema.items, item));
  if (!schema.properties) return value;
  const out = {};
  const names = ORDER.get(schema) ?? Object.keys(schema.properties).map((key) => [key, key]);
  for (const [wire, name] of names) {
    if (Object.hasOwn(value, wire)) out[name] = fromProperty(schema.properties[wire], value[wire]);
  }
  for (const key of Object.keys(value)) if (!Object.hasOwn(schema.properties, key)) out[key] = value[key];
  return out;
}

/** One property of an object: a keyed object becomes its rows, in the order the schema lists the keys. */
function fromProperty(property, value) {
  const field = KEYED.get(property);
  if (!field || !value || typeof value !== 'object') return fromWire(property, value);
  const keys = [...Object.keys(property.properties).filter((key) => Object.hasOwn(value, key)),
    ...Object.keys(value).filter((key) => !Object.hasOwn(property.properties, key))];
  return keys.map((key) => ({ [field]: key, ...fromWire(property.properties[key], value[key]) }));
}

export const assumptionSchema = obj({ assumption: str, why: str, impact: str, clarification: str });

export const intakeSchema = obj({
  received: strs,
  secondaryRequests: strs,
  assumptionsToProceed: strs,
  decisionsRequired: strs,
});

/** The documents one batch of candidates holds that the change touches; a batch may hold none. */
export const documentPickSchema = (batch) => obj({ documents: listOf(oneOf(batch)) });

export const digestSchema = obj({ points: listOf(str, { minItems: 1 }) });

export function understandingSchema({ documents, keys, inclusions, suite }) {
  return obj({
    summary: ordered({
      change: str, purpose: str, modules: str, existingBehavior: str, newBehavior: str,
      rulesIdentified: str, inScope: str, outOfScope: str, missingInformation: str,
      confidenceReason: str,
      confidence: oneOf(['High', 'Medium', 'Low']),
    }),
    ...(suite ? {} : {
      sourceDocuments: keyed('name', documents,
        { authority: str, informationObtained: str, directImpact: { type: 'boolean' },
          reason: str, inclusion: oneOf(inclusions) }, ordered),
    }),
    modules: keyed('document', keys,
      { module: str, abbreviation: { type: 'string', pattern: '^[A-Z0-9]{2,6}$' } }, ordered),
    conflicts: strs,
    blockingMissing: strs,
  });
}

/** One batch of rules read against the documents: which bear on the change, and what they show. */
export const phase1RulesSchema = (ids) => obj({
  rules: keyed('id', ids, { bearsOnChange: { type: 'boolean' } }),
  conflicts: strs,
  blockingMissing: strs,
  notes: str,
});

export const derivedRulesSchema = (risks) => obj({
  rules: listOf(ordered({ statement: str, sourcePage: str, summary: str, risk: oneOf(risks) })),
});

/** Pairs of rules that require different behavior for the same thing. */
export const ruleConflictSchema = (ids) => obj({
  conflicts: listOf(ordered({ rules: listOf(oneOf(ids), { minItems: 2, maxItems: 2 }), conflict: str })),
});

export const scopeSchema = (ids, impacts) => obj({
  rules: keyed('id', ids, { impact: oneOf(impacts), rationale: str }),
  assumptions: listOf(assumptionSchema),
  userReview: strs,
});

/** What a change scope review question comes to once it is read against the change description. */
const REVIEW_RULINGS = ['kept', 'assumption', 'answered'];

/**
 * One row per review question, keyed Q1, Q2 and so on. A server that sorts an object's
 * properties alphabetically still reads the row in the order it is worked out, because
 * the names sort that way: the sentence, the ruling it supports, then the statement and
 * its parts.
 */
export const reviewTriageSchema = (keys) => obj({
  questions: keyed('question', keys, { quote: str, ruling: oneOf(REVIEW_RULINGS), statement: str,
    testImpact: str, toConfirm: str, why: str }),
});

/** The areas the impact analysis covers: the pack key and the label the prompts show. */
export const IMPACT_AREAS = [['windows', 'Windows, pages and tabs'],
  ['businessFunctions', 'Business functions'], ['upstream', 'Upstream'],
  ['downstream', 'Downstream'], ['data', 'Data'], ['security', 'Security and roles'],
  ['batch', 'Batch'], ['notices', 'Notices'], ['reports', 'Reports'],
  ['interfaces', 'Interfaces']];

export const impactSchema = obj({
  executiveSummary: obj({
    scope: str, modules: str, sourceDocuments: str, strategy: str, execution: str, risks: str,
  }),
  impacts: obj(Object.fromEntries(IMPACT_AREAS.map(([key]) => [key, listOf(str, { maxItems: 8 })]))),
});

export const riskSchema = (ids, risks) => obj({
  rules: keyed('id', ids, { risk: oneOf(risks) }),
});

export const objectivesSchema = (objectives, { evidence = [] } = {}) => obj({
  objectives: keyed('objective', objectives, { applicable: { type: 'boolean' }, reason: str }),
  // One row per configured evidence rule: whether the change holds it, and the quote that shows it.
  ...(evidence.length ? { evidence: keyed('id', evidence, { holds: { type: 'boolean' }, quote: str }) } : {}),
});

/** The kinds of scenario the source can support. All ten are asked for in every inventory. */
export const REQUIRED_SCENARIO_KINDS = ['control', 'isolation', 'combined', 'persistence',
  'negative', 'role', 'state-change', 'manual-batch', 'navigation', 're-entry'];
// A break scenario tries to break the change; it is asked for when a BREAK IT set is in play.
export const SCENARIO_KINDS = [...REQUIRED_SCENARIO_KINDS, 'break', 'decision'];

// The limit is twice the longest population, action or outcome measured in inventory
// replies, 337 characters. The grammar the model server builds from a schema refuses a
// repetition of 2000 or more, and the text limit is far under that.
export const SCENARIO_TEXT_MAX = 674;
const scenarioText = { type: 'string', maxLength: SCENARIO_TEXT_MAX };

// Each scenario is a population, an action and an expected outcome. `kindChecks`
// makes the reply answer for every required kind: what its scenario tests, or
// why the source supports none. A scenario has no use for more rule items than the rules
// given, so its rule list is limited to that many. Its texts have a longest length.
// No part of a scenario can therefore repeat without end. `minItems` is 0 for a pass
// that may find nothing to add.
export const scenarioInventorySchema = ({ ids, kinds = SCENARIO_KINDS,
  required = REQUIRED_SCENARIO_KINDS, minItems = 1, maxItems }) => ordered({
  scenarios: listOf(ordered({
    rules: listOf(oneOf(ids), { minItems: 1, maxItems: ids.length }),
    kind: oneOf(kinds),
    population: scenarioText,
    action: scenarioText,
    outcome: scenarioText,
  }), { minItems, ...(maxItems ? { maxItems } : {}) }),
  ...(required.length ? { kindChecks: keyed('kind', required, { note: str }) } : {}),
});

// `scenarios` names the scenario ids a card may cover.
const cardFields = ({ ids, objectives, derivations, scenarios }) => ({
  title: str,
  ...(scenarios ? { scenario: oneOf(scenarios) } : {}),
  mission: str,
  focus: listOf(str, { minItems: 1 }),
  expected: str,
  rules: listOf(oneOf(ids), { minItems: 1 }),
  objectives: listOf(oneOf(objectives), { minItems: 1 }),
  derivation: oneOf(derivations),
  steps: listOf(obj({ description: str, expected: str, rules: listOf(oneOf(ids)) }), { minItems: 1 }),
});
export const cardSchema = (options) => ordered(cardFields(options));

// The two answers to whether a card's Expected Result follows from its rules.
export const VERDICTS = ['follows', 'does not follow'];

// One row per card in the call; the reason comes first, so the verdict follows from it.
export const verificationSchema = (refs) => obj({
  cards: keyed('card', refs, { why: str, verdict: oneOf(VERDICTS) }, ordered),
});

// A scenario no card is written for is skipped: an existing test covers it, or no card can.
export const SKIP_REASONS = ['reused', 'gap'];

export const cardsSchema = ({ ids, objectives, derivations, uncoveredStatuses, scenarios }) => obj({
  cards: listOf(cardSchema({ ids, objectives, derivations, scenarios })),
  uncovered: listOf(ordered({
    ruleId: oneOf(ids), status: oneOf(uncoveredStatuses), gap: str, recommendation: str,
  })),
  ...(scenarios ? { skipped: listOf(ordered({
    scenario: oneOf(scenarios), how: oneOf(SKIP_REASONS), reason: str })) } : {}),
  reuse: strs,
  assumptions: listOf(assumptionSchema),
});

/** The existing cards that serve an objective, by reference. */
export const objectiveCardsSchema = (refs) => obj({ cards: listOf(oneOf(refs)) });

export const setScopesSchema = (objectives) => obj({
  sets: keyed('objective', objectives, { scope: str }),
});

// The sections of the Validation checklist; each issue the checklist raises names one.
export const VALIDATION_SECTIONS = ['Requirements Matrix Integrity', 'Rule Integrity',
  'Test Card Structure', 'Coverage Completeness', 'Traceability', 'Consistency'];

export const checklistSchema = ({ statuses }) => obj({
  issues: listOf(ordered({ section: oneOf(VALIDATION_SECTIONS), issue: str, fix: str })),
  coverage: listOf(ordered({
    ruleId: str, status: oneOf(statuses), strength: str, gap: str, recommendation: str,
  })),
  assumptions: listOf(assumptionSchema),
});

// The senior review is asked in two parts, each a call of its own: the review questions and the
// tester notes. Each part's answer holds its own key.
export const seniorReviewSchema = obj({
  seniorReview: obj({
    missed: str, businessBehavior: str, upstreamDownstream: str, obviousFirst: str,
    qualityDerived: str,
  }),
});
export const testerNotesSchema = obj({
  testerNotes: obj({
    testData: str, execution: str, regressionTargets: str, breakIt: str, screenshots: str,
    sqlValidation: str, knownRisks: str, cautions: str,
  }),
});

/** The overall confidence level, with the reason for every level and the criteria it meets. */
export const confidenceOverallSchema = ({ confidence }) => ordered({
  overall: oneOf(confidence), reason: str, criteria: strs,
});

/** The least a confidence field says: shorter than this is a label, not a sentence. */
export const CONFIDENCE_FIELD_MIN_CHARS = 60;

/** One prose field of the Confidence Assessment, written on its own. */
export const confidenceFieldSchema = (field) => obj({
  [field]: { type: 'string', minLength: CONFIDENCE_FIELD_MIN_CHARS },
});

// The assessment steps of the confidence procedure, in the order they are walked.
export const CONFIDENCE_STEPS = ['rules', 'decisions', 'coverage', 'regression', 'qualityDerived',
  'breakIt', 'professionalReview', 'residualRisk'];
export const CONFIDENCE_VERDICTS = ['strong', 'partial', 'weak'];

/** One verdict and its evidence for each assessment step. */
export const confidenceStepsSchema = obj({
  steps: keyed('step', CONFIDENCE_STEPS, { verdict: oneOf(CONFIDENCE_VERDICTS), evidence: str }),
});

// The seven checks of the Revalidation procedure; revalidation gives one verdict for each.
export const REVALIDATION_CHECKS = ['All issues resolved', 'No regressions introduced',
  'Requirement ID references preserved', 'Requirements Matrix integrity preserved',
  'Traceability complete',
  'No uncovered Requirement IDs remain unless explicitly documented',
  'Test pack is ready for ALM execution'];
// The checks grouped by the sheets they read; the revalidation walk makes one call per group.
export const REVALIDATION_GROUPS = [
  { key: 'traceability', reads: 'the rules index and the matrices',
    checks: ['Requirement ID references preserved', 'Requirements Matrix integrity preserved',
      'Traceability complete', 'No uncovered Requirement IDs remain unless explicitly documented'] },
  { key: 'resolution', reads: 'the open findings, the fixes applied and the cards',
    checks: ['All issues resolved', 'No regressions introduced'] },
  { key: 'readiness', reads: 'the whole workbook',
    checks: ['Test pack is ready for ALM execution'] },
];
// The verdict for a check the part of the workbook in view does not show.
export const NOT_SHOWN = 'not shown in this part';

export const revalidationSchema = ({ verdicts = ['pass', 'fail'], checks = REVALIDATION_CHECKS } = {}) => obj({
  checks: keyed('check', checks, { why: str, verdict: oneOf(verdicts), fix: str }, ordered),
});

/** The most new cards one repair call may return. */
export const NEW_CARDS_MAX = 3;

// `newIds` are the rules a new card may cover: those the findings name, none in a suite pack.
export const repairSchema = ({ cardIds, ids, objectives, derivations, statuses, sheets,
  assumptions, newIds = [] }) => obj({
  cards: listOf(ordered({
    id: oneOf(cardIds.length ? cardIds : ['none']),
    ...cardFields({ ids, objectives, derivations }),
  }), { minItems: cardIds.length, maxItems: cardIds.length }),
  newCards: listOf(cardSchema({ ids: newIds.length ? newIds : ['none'], objectives, derivations }),
    { maxItems: newIds.length ? NEW_CARDS_MAX : 0 }),
  coverage: listOf(ordered({
    ruleId: oneOf(ids), status: oneOf(statuses), strength: str, gap: str, recommendation: str,
  })),
  limitations: listOf(obj({ sheet: oneOf(sheets), text: str })),
  ...(assumptions ? { assumptions: listOf(assumptionSchema) } : {}),
});

export const improvementSchema = obj({
  improvementNotes: listOf(obj({ gap: str, impact: str, recommendation: str, component: str })),
});
