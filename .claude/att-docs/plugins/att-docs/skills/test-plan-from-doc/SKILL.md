---
name: test-plan-from-doc
description: Turn a functional-spec document into a structured test coverage plan before any automated test code is written. Use when asked to plan or propose test coverage for a page or feature from its functional spec.
---

# Test Plan From Doc

Produce a test plan Markdown file from a functional spec document. The plan is a
planning artifact written before or alongside test code. This skill does not
write test code or page-object code.

The consuming repository's extension supplies the values below. Where it names
none, ask the user rather than guessing.

| Placeholder | Meaning |
| --- | --- |
| `<specs-root>` | Where functional spec documents live |
| `<tests-root>` | Where a feature's tests, and so its plan, live |
| `<plan-name>` | File name pattern for a plan |
| `<page-objects>` | Where page objects live |
| `<id-prefixes>` | How existing plans prefix their coverage IDs |
| `<exemplar>` | An existing plan to copy the structure from |

## 1. Locate and read the source doc

- Read the whole functional spec under `<specs-root>`. If it opens with a
  provenance block naming its source and how its revision date was established,
  read that too: a spec whose revision date is not stated is one whose age
  nothing in the file vouches for.
- Read any related process or system descriptions the extension points to. The
  spec says what a page renders; the description behind it often carries the
  rule the page inherits, such as who may see a stage or what an approval
  routes to. List what they contribute under "Documentation Reviewed".
- A source document with no Markdown counterpart has not been converted. Convert
  it with the repository's conversion process rather than reading a binary or
  converting by hand.
- Note every downstream or related page the spec names. They belong in
  "Documentation Reviewed".

## 2. Resolve target locations

- Test folder: under `<tests-root>`, named for the feature. It may not exist yet
  for a new feature; the plan can precede the tests.
- Output file: named by `<plan-name>`, colocated with the tests it plans for.
- Page object: under `<page-objects>`, existing or planned.
- ID prefix: read the sibling plans already under `<tests-root>` and follow the
  prefix convention they use (`<id-prefixes>`) rather than inventing a style.

## 3. Populate the template

Follow this order, matching `<exemplar>`:

1. `# <Title> Automation Test Plan`
2. `## Objective`: a paragraph plus a bullet list of what automation will
   ensure, drawn from the doc's business rules and stated goals.
3. `## Target`: test path(s), requirements doc path, page object path, and a
   one-line functional scope summary.
4. `## Documentation Reviewed`: the source doc(s) plus referenced downstream
   pages.
5. `# Automation Coverage Goals` / `## Primary Objectives`: one bullet per
   validated behavior category.
6. `# In Scope` / `## Functional Coverage` and `# Out of Scope` /
   `## Excluded Areas`: be explicit about what will not be automated (third
   party authentication internals, downstream page internals, browser
   compatibility, accessibility unless separately scoped) and why, mirroring the
   doc's assumptions and caveats.
7. `# Test Data Requirements`: accounts, personas, and environment flags, drawn
   from the doc's access-rights and persona sections. State the conditions each
   data lookup picks on, so the test is written against a query rather than a
   search that walks candidates.
8. `# Automation Strategy`: `## UI Automation Focus`, plus
   `## API / Backend Validation Focus` when the feature has a backend or mapping
   component.
9. `## Coverage Matrix`: table `| ID | Area | Priority | Planned Coverage |`, one
   row per discrete testable business rule. **P0** for access, security,
   core happy path, and required-validation rules. **P1** for secondary flows
   and non-blocking behavior. **P2** for cosmetic details such as styling and
   link-target specifics.
10. `# Page Elements Coverage`: `## Static Content Validation` and
    `## Interactive Controls`, listing every labeled element the doc calls out.
11. `# Business Rules Coverage`: one `## <ID>` subsection per matrix row,
    restating the rule near-verbatim so it traces to source. Mark unautomatable
    rules explicitly, with the reason, rather than dropping them.
12. `# Test Scenarios`: `## TS-<PREFIX>-### <Name>` blocks, each with
    `### Coverage` and `### Assertions` bullets, grouping related matrix rows
    into end-to-end flows.
13. `# Negative Coverage`: one subsection per negative or failure-path rule.
14. `# State Transition Coverage`: for multi-step persistence or navigation
    state, write each as `<state> -> <action> -> <state>`.
15. `# Cross-System Validation`: when the doc references backend or other-system
    mappings, list what must be validated.
16. `# Automation Tags`: group scenario names under `## Regression`, `## Smoke`,
    `## Integration`, and `## Negative`.
17. `# Proposed Spec Organization`: the `describe` block names for the eventual
    test file.
18. `# Proposed Page Object Methods`: grouped by concern (Navigation, Selection,
    Validation, Assertions), following the naming conventions of the existing
    page objects.
19. `# Risks and Special Handling`: likely flakiness sources such as timeouts,
    external links, and browser-specific behavior.
20. `# Exit Criteria`: a checklist of what done means, for example all P0
    automated and stable, P1 automated or explicitly deferred with a rationale.

## 4. Cross-check, do not invent

- Every matrix row and business-rule subsection must trace to something the doc
  states. Do not add scenarios the doc does not support, and do not drop a
  stated rule because it is inconvenient to automate. Mark it invalid or manual
  instead.
- When tests already exist for the feature, this is a retrofit: add a
  "Current Automation Baseline" section that lists existing coverage, then the
  explicit gaps.

## 5. Wrap up

- Run the consuming repository's text and style checks over the finished plan
  before committing it. The extension names them.
- Do not write test or page-object code. Implementing the plan is a separate
  task.
