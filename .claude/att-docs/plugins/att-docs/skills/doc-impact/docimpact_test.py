#!/usr/bin/env python3
"""Checks the rule diff, the reviewed record, and the citation index behind docimpact.py.

usage: python3 docimpact_test.py

Every case runs on fixtures under the config below, so none reads a repository's history.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docimpact  # noqa: E402

# The layout the fixtures are written in, with issue text of the fixtures' own.
CONFIG = {
    "docsRoot": "docs/apps",
    "testsRoot": "src",
    "planMarker": "TestPlan",
    "notesName": "AutomationNotes.md",
    "specSuffix": ".spec.ts",
    "futureFolder": "Future",
    "legacyRoots": ["documentation"],
    "linkFileParam": "file",
    "mainRef": "origin/main",
    "prRef": "pull/{number}/head",
    "stateName": "doc-impact",
    "numberMentionWord": "letter",
    "ruleId": r"\bBR-[A-Z0-9][A-Z0-9.]*(?:-[A-Z0-9]+)*\b",
    "manualId": r"\bTC-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d+(?:\.\d+)?\b",
    "requirementId": r"^(?:SIR\s*\d+\S*|[A-Z]+-\S+(?:\s+[\d.]+[A-Z]?)?|\d+(?:\.\d+){2,})",
    "windowId": r"\b[A-Z]{4}\d{2}[A-Z]\b",
    "drift": {
        "tool": "TM",
        "title": "[Rules] {prefix}: {title} TM folder differs from the master",
        "marker": "TM drift: {doc} under {prefix} at {fingerprint}",
        "update": "`rules-update {doc}`",
        "resend": "`rules-upload --doc {folder} --folder {staging_id} --send`",
        "resendUnstaged": "`rules-upload --doc {folder} --send` with the staging folder's id",
    },
}


def setUpModule():
    docimpact.configure(CONFIG, None)


HEAD = """# Some Screen

**Document provenance**

- Source: `Some Screen.pdf`
- Revised: 2026-08-01, from a stated update line
- Version: not stated
- Converted: 2026-08-20

## Validations

| # | Rule | Message |
|---|------|---------|
| 1 | Age input must be an integer above 0. | Age must be positive. |

The worker may save the record once every
required field holds a value.
"""


def revise(text: str, old: str, new: str) -> str:
    assert old in text, old
    return text.replace(old, new)


class RuleChanges(unittest.TestCase):
    def test_provenance_only_change_is_unchanged(self):
        new = revise(HEAD, "Converted: 2026-08-20", "Converted: 2026-09-30")
        new = revise(new, "Revised: 2026-08-01, from a stated update line",
                     "Revised: 2026-09-29, from the file's embedded document properties")
        self.assertEqual(docimpact.rule_changes(HEAD, new)["kind"], "unchanged")

    def test_rewrapped_paragraph_is_unchanged(self):
        new = revise(HEAD, "once every\nrequired field", "once every required\nfield")
        self.assertEqual(docimpact.rule_changes(HEAD, new)["kind"], "unchanged")

    def test_padded_table_cells_are_unchanged(self):
        new = revise(HEAD, "| 1 | Age", "|   1   |   Age")
        self.assertEqual(docimpact.rule_changes(HEAD, new)["kind"], "unchanged")

    def test_a_page_marker_inside_a_numbered_rule_changes_no_rule(self):
        old = "## Rules\n\n12. The rule\n\n    1. Its sub-rule\n"
        new = '## Rules\n\n12. The rule\n\n<a id="page-3"></a>*Page 3*\n\n    1. Its sub-rule\n'
        self.assertEqual(docimpact.changed_numbers(old, new), (set(), False))

    def test_paragraph_split_differently_is_layout(self):
        new = revise(HEAD, "once every\nrequired", "once every\n\nrequired")
        self.assertEqual(docimpact.rule_changes(HEAD, new)["kind"], "layout")

    def test_changed_rule_names_its_section(self):
        new = revise(HEAD, "an integer above 0.", "an integer between 1 and 100.")
        result = docimpact.rule_changes(HEAD, new)
        self.assertEqual(result["kind"], "content")
        self.assertEqual(len(result["hunks"]), 1)
        hunk = result["hunks"][0]
        self.assertEqual(hunk["section"], "Validations")
        self.assertIn("above 0", hunk["removed"][0])
        self.assertIn("between 1 and 100", hunk["added"][0])

    def test_added_rule_has_nothing_removed(self):
        new = revise(HEAD, "| Age must be positive. |\n",
                     "| Age must be positive. |\n| 2 | Phone is required. | Enter a phone. |\n")
        hunk = docimpact.rule_changes(HEAD, new)["hunks"][0]
        self.assertEqual(hunk["removed"], [])
        self.assertEqual(hunk["added"], ["| 2 | Phone is required. | Enter a phone. |"])

    def test_body_list_right_after_the_block_is_kept(self):
        """A header design can open its body with a list."""
        old = revise(HEAD, "## Validations", "- The worker opens the note.\n\n## Validations")
        new = revise(old, "opens the note", "copies the note")
        hunk = docimpact.rule_changes(old, new)["hunks"][0]
        self.assertEqual(hunk["added"], ["- The worker copies the note."])

    def test_new_and_removed_documents_carry_no_hunks(self):
        self.assertEqual(docimpact.rule_changes(None, HEAD), {"kind": "added", "hunks": []})
        self.assertEqual(docimpact.rule_changes(HEAD, None), {"kind": "removed", "hunks": []})


def converted(title: str, body: str = "Body text.\n") -> str:
    return (f"# {title}\n\n{docimpact.PROVENANCE}\n\n- Source: `{title}.doc`\n"
            f"- Converted: 2026-09-30\n\n{body}")


class Index(unittest.TestCase):
    """A throwaway repository holding the citation shapes the real plans use."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        files = {
            "docs/apps/AIMS/AIMS 2.0 -  SCR Service Center Toolbar.md":
                converted("AIMS 2.0 -  SCR Service Center Toolbar"),
            "docs/apps/AIMS/295 DB - 3370 Agency Do Not (Eighteen).md":
                converted("295 DB - 3370 Agency Do Not (Eighteen)"),
            "docs/apps/AIMS/447 DB -3370 Agency Do Not (Eighteen).md":
                converted("447 DB -3370 Agency Do Not (Eighteen)"),
            "docs/apps/AIMS/Security.md": converted("Security"),
            "docs/apps/CONNECTIONS/Security.md": converted("Security"),
            "docs/apps/BCR/8 - BCR Portal Appeal Request - Your Contact Information Page.md":
                converted("8 - BCR Portal Appeal Request - Your Contact Information Page"),
            "docs/apps/DX/ReopenClosedFAD.md": converted("ReopenClosedFAD"),
            "docs/apps/CONNECTIONS/ACT-4.0-Activity-Entry.md":
                converted("ACT 4.0 - Activity Entry"),
            "docs/apps/DX/AutomationNotes.md": "# Notes\n\nNot a source document.\n",
            "docs/apps/DX/Rules.md": converted("Rules", (
                "| Name | Description | Document |\n|---|---|---|\n"
                "| BR-FADX-RCF-001 - Reopen only | Closed homes only | ReopenClosedFAD.docx |\n")),
            "docs/apps/DX/Manual.md": converted("Manual", (
                "| Test Name | Description |\n|---|---|\n"
                "| TC-FADX-TBD-001 - Reopen | Rules Covered: BR-FADX-RCF-001 - Reopen only |\n")),
            "src/AIMS/tests/admin/Admin.AIMS.TestPlan.md": (
                "## Documentation Reviewed\n- `documentation/aims/Process Descriptions/"
                "AIMS 2.0 -  SCR Service Center Toolbar.doc File/AIMS 2.0 -  SCR Service\n"
                "  Center Toolbar.md`\n- `documentation/aims/Process Descriptions/"
                "Security.docx File/Security.md`\n"),
            "src/AIMS/tests/admin/admin.AIMS.spec.ts": "",
            "src/AIMS/tests/decision/Decision.AIMS.TestPlan.md": (
                "No document cited.\n| AIMS-DEC-031 | missing 294/295 acceptance |\n"
                "The letter set decides it.\n"),
            "src/BCR/tests/contactInfo/contactInfo.BCR.TestPlan.md": (
                "Source Document: 08 – BCR Portal Appeal Request – Your Contact "
                "Information Page\n- `documentation/BCR/Process Descriptions/"
                "10 - BCR Portal - Your Contact Infomation Page.md`\n"),
            "src/DX/tests/reopen/reopenTestPlan.md": (
                "- `docs/apps/DX/ReopenClosedFAD.md`\n- `docs/apps/DX/AutomationNotes.md`\n"
                "| DX-RFD-001 | Contract | BR-FADX-RCF-001 | TC-FADX-TBD-001 |\n"),
        }
        for rel, text in files.items():
            path = self.repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.snap = docimpact.Snapshot.of_directory(self.repo)
        self.docs = docimpact.converted_docs(self.snap)

    def tearDown(self):
        self.tmp.cleanup()

    def dependents(self, doc):
        index = docimpact.build_index(self.snap)
        return {(d["kind"], d["file"]) for d in index["dependents"].get(doc, [])}

    def test_legacy_path_wrapped_over_two_lines_resolves(self):
        doc = "docs/apps/AIMS/AIMS 2.0 -  SCR Service Center Toolbar.md"
        self.assertIn(("plan", "src/AIMS/tests/admin/Admin.AIMS.TestPlan.md"),
                      self.dependents(doc))

    def test_name_in_two_suites_resolves_to_the_citing_suite(self):
        self.assertEqual(docimpact.resolve(
            "documentation/aims/Security.docx File/Security.md", "AIMS", self.docs),
            ["docs/apps/AIMS/Security.md"])

    def test_spaced_citation_resolves_to_the_hyphenated_file(self):
        self.assertEqual(docimpact.resolve(
            "docs/apps/CONNECTIONS/ACT 4.0 - Activity Entry.md", "CCA", self.docs),
            ["docs/apps/CONNECTIONS/ACT-4.0-Activity-Entry.md"])

    def test_plan_names_its_specs(self):
        index = docimpact.build_index(self.snap)
        dep = index["dependents"]["docs/apps/AIMS/Security.md"][0]
        self.assertEqual(dep["specs"], ["src/AIMS/tests/admin/admin.AIMS.spec.ts"])

    def test_bare_title_with_padding_and_en_dashes_counts(self):
        doc = "docs/apps/BCR/8 - BCR Portal Appeal Request - Your Contact Information Page.md"
        self.assertIn(("title", "src/BCR/tests/contactInfo/contactInfo.BCR.TestPlan.md"),
                      self.dependents(doc))

    def test_notes_beside_the_documents_are_not_sources(self):
        self.assertEqual(self.dependents("docs/apps/DX/AutomationNotes.md"), set())

    def test_renamed_title_is_unresolved_with_a_hint(self):
        index = docimpact.build_index(self.snap)
        misses = {u["cited"]: u for u in index["unresolved"]}
        miss = misses["documentation/BCR/Process Descriptions/"
                      "10 - BCR Portal - Your Contact Infomation Page.md"]
        self.assertEqual(miss["file"], "src/BCR/tests/contactInfo/contactInfo.BCR.TestPlan.md")

    def test_plan_citing_nothing_is_reported(self):
        index = docimpact.build_index(self.snap)
        self.assertIn(("src/AIMS/tests/decision/Decision.AIMS.TestPlan.md",
                       "(no document citation)"),
                      {(u["file"], u["cited"]) for u in index["unresolved"]})

    def test_rule_chain_reaches_manual_cases_and_plan(self):
        rules = docimpact.rule_sources(self.snap, self.docs)
        self.assertEqual(rules, {"docs/apps/DX/ReopenClosedFAD.md": {"BR-FADX-RCF-001"}})
        cases = docimpact.cases_citing(self.snap, {"BR-FADX-RCF-001"})
        found = {(c["kind"], c["file"]): c["cases"] for c in cases}
        self.assertEqual(found[("manual", "docs/apps/DX/Manual.md")], ["TC-FADX-TBD-001"])
        self.assertEqual(found[("plan-rule", "src/DX/tests/reopen/reopenTestPlan.md")],
                         ["TC-FADX-TBD-001"])

    def test_reissued_letter_finds_its_predecessor_and_its_number(self):
        new = "docs/apps/AIMS/447 DB -3370 Agency Do Not (Eighteen).md"
        old = "docs/apps/AIMS/295 DB - 3370 Agency Do Not (Eighteen).md"
        self.assertEqual(docimpact.predecessor(new, self.docs), old)
        mentions = docimpact.number_mentions(self.snap, old)
        self.assertEqual([(m["file"], m["lines"]) for m in mentions],
                         [("src/AIMS/tests/decision/Decision.AIMS.TestPlan.md", [2])])

    def test_plan_still_citing_a_gone_document_is_found(self):
        """A removed or renamed document is absent from the head index, so a plan still
        citing it is found through its unresolved citation."""
        index = docimpact.build_index(self.snap)
        gone = "docs/apps/BCR/10 - BCR Portal - Your Contact Infomation Page.md"
        self.assertEqual([d["file"] for d in docimpact.citing_gone(index, gone)],
                         ["src/BCR/tests/contactInfo/contactInfo.BCR.TestPlan.md"])

    def test_unnumbered_document_has_no_predecessor(self):
        self.assertIsNone(docimpact.predecessor("docs/apps/AIMS/Security.md", self.docs))


class FutureFolder(unittest.TestCase):
    CURRENT = "docs/apps/OCS/1-OCS-Home-Page.md"
    AHEAD = "docs/apps/OCS/Future/1-OCS-Home-Page.md"
    DOCS = {"1-ocs-home-page": f"{CURRENT}\t{AHEAD}"}

    def test_citation_means_the_version_the_web_app_follows(self):
        self.assertEqual(docimpact.resolve("docs/apps/OCS/1-OCS-Home-Page.md", "OCS", self.DOCS),
                         [self.CURRENT])

    def test_future_copy_replaces_the_suite_copy(self):
        self.assertTrue(docimpact.is_future(self.AHEAD))
        self.assertFalse(docimpact.is_future(self.CURRENT))
        self.assertEqual(docimpact.predecessor(self.AHEAD, self.DOCS), self.CURRENT)
        self.assertEqual(docimpact.current_of(self.AHEAD, self.DOCS), self.CURRENT)
        self.assertIsNone(docimpact.current_of(self.CURRENT, self.DOCS))

    def test_suite_copy_never_takes_a_future_copy_as_predecessor(self):
        docs = {"2-home": "docs/apps/OCS/Future/2 Home.md"}
        self.assertIsNone(docimpact.predecessor("docs/apps/OCS/1 Home.md", docs))


class GitRange(unittest.TestCase):
    """A throwaway repository with two commits, read the way a range review reads one."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        docimpact.configure(CONFIG, self.repo)
        self.git("init", "-q")
        self.commit("docs/apps/DX/Home.md", converted("Home", "Age must be above 0.\n"))
        self.base = docimpact.rev_parse("HEAD")
        self.commit("docs/apps/DX/Home.md", converted("Home", "Age must be above 1.\n"))
        self.head = docimpact.rev_parse("HEAD")

    def tearDown(self):
        docimpact.configure(CONFIG, None)
        self.tmp.cleanup()

    def git(self, *args):
        docimpact.git("-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                      *args)

    def commit(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", rel)

    def test_empty_range_changes_nothing(self):
        self.assertEqual(docimpact.changed_docs(self.head, self.head), [])

    def test_revised_document_reads_as_content(self):
        [doc] = docimpact.changed_docs(self.base, self.head)
        self.assertEqual((doc["path"], doc["status"], doc["kind"]),
                         ("docs/apps/DX/Home.md", "M", "content"))
        self.assertEqual(docimpact.Snapshot.at(self.head).app_docs(), ["docs/apps/DX/Home.md"])


class Record(unittest.TestCase):
    def test_state_round_trips_and_starts_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc-impact" / "state.json"
            state = docimpact.load_state(path)
            self.assertEqual(state, {"watermark": None, "reviewed": {}})
            state["reviewed"]["docs/apps/AIMS/x.md"] = ["abc"]
            docimpact.save_state(path, state)
            self.assertEqual(docimpact.load_state(path)["reviewed"],
                             {"docs/apps/AIMS/x.md": ["abc"]})

    def result(self, pr):
        return {"pr": pr, "head": "f" * 40,
                "documents": [
                    {"path": "docs/apps/AIMS/x.md", "blob": "abc", "key": "abc"},
                    {"path": "docs/apps/AIMS/gone.md", "blob": None, "key": "removed-def"}]}

    def test_pull_request_review_marks_keys_and_keeps_the_watermark(self):
        state = docimpact.record(self.result(3234), {"watermark": "a" * 40, "reviewed": {}})
        self.assertEqual(state["watermark"], "a" * 40)
        self.assertEqual(state["reviewed"], {"docs/apps/AIMS/x.md": ["abc"],
                                             "docs/apps/AIMS/gone.md": ["removed-def"]})

    def test_main_review_moves_the_watermark_and_records_once(self):
        state = {"watermark": "a" * 40, "reviewed": {"docs/apps/AIMS/x.md": ["abc"]}}
        state = docimpact.record(self.result(None), state)
        self.assertEqual(state["watermark"], "f" * 40)
        self.assertEqual(state["reviewed"]["docs/apps/AIMS/x.md"], ["abc"])


RULE_DOC = """# Activity Entry

**Document provenance**

- Source: `Activity Entry.docx`
- Converted: 2026-08-20

## Business Rules

1. The worker must enter a start date.
2. The end date may not precede the start date.
   It may equal the start date.
3. Requirement # CPRS-5.2.3.1 applies to every activity.

## Navigation

The Save button returns to the activity list.

## Screen Print (if applicable):

An image of the window.
"""

MAPPED = "docs/apps/CONNECTIONS/Activity Entry.md"
UNMAPPED = "docs/apps/CONNECTIONS/Something Else.md"
RULE_MAP = {"documents": [{"doc": MAPPED, "prefix": "BR-ACT4", "rules": [
    {"rule_id": "BR-ACT4-001", "anchor": "Rule 1, Page 2", "section": "4"},
    {"rule_id": "BR-ACT4-002", "anchor": "Business Rule 2.a, Page 2", "section": "4"},
    {"rule_id": "BR-ACT4-003", "anchor": "Requirement # CPRS-5.2.3.1, Page 2", "section": "4"},
    {"rule_id": "BR-ACT4-004", "anchor": "Bullet Item - Save", "section": "Navigation"},
    {"rule_id": "BR-ACT4-005", "anchor": "Section - Screen Print. Page 3", "section": "5"},
    {"rule_id": "BR-ACT4-006", "anchor": "Page 6", "section": "6"},
]}]}


class RuleRefresh(unittest.TestCase):
    def review(self, path, new):
        doc = {"path": path, "old_path": None, "predecessor": None, "status": "M",
               "key": "b" * 40, **docimpact.rule_changes(RULE_DOC, new)}
        result = {"base": "base", "head": "head", "documents": [doc]}
        texts = {"base": RULE_DOC, "head": new}
        return docimpact.rule_refresh(result, RULE_MAP, read=lambda rev, _: texts[rev])

    def test_anchors_read_number_requirement_and_section(self):
        anchors = [docimpact.anchor_of(r) for r in RULE_MAP["documents"][0]["rules"]]
        self.assertEqual(anchors, [("number", 1), ("number", 2),
                                   ("requirement", "CPRS-5.2.3.1"), ("section", "Navigation"),
                                   ("section", "Screen Print"), None])

    def test_anchors_in_the_other_shapes_the_store_holds(self):
        def anchor(text):
            return docimpact.anchor_of({"anchor": text, "section": "12"})
        self.assertEqual(anchor('Section "Navigation", Page 4'), ("section", "Navigation"))
        self.assertEqual(anchor("Screen Print, Page 9"), ("section", "Screen Print"))
        self.assertEqual(anchor("Business Rules, Page 3"), ("section", "Business Rules"))
        self.assertEqual(anchor("Rule SIR 8554, Page 2"), ("requirement", "SIR 8554"))
        self.assertEqual(anchor("Requirement # II-2 3.1.1, Page 5"),
                         ("requirement", "II-2 3.1.1"))
        self.assertEqual(anchor("Rule 5.2.3.1, Page 5"), ("requirement", "5.2.3.1"))
        self.assertEqual(anchor("(42.iv, Page 18)".strip("()")), ("number", 42))
        self.assertIsNone(anchor("Bullet Item - Caller Restrictions, Page 2"))
        self.assertIsNone(anchor("Page 4, Bullet 2"))
        self.assertIsNone(anchor(""))

    def test_revised_mapped_document_names_its_prefix_and_the_rules_it_reached(self):
        new = revise(RULE_DOC, "   It may equal", "   It may not equal")
        new = revise(new, "returns to the activity list", "returns to the home page")
        items = self.review(MAPPED, new)
        self.assertEqual(len(items), 1)
        self.assertEqual((items[0]["prefix"], items[0]["rules"], items[0]["kind"]),
                         ("BR-ACT4", 6, "content"))
        self.assertEqual([c["rule_id"] for c in items[0]["changed"]],
                         ["BR-ACT4-002", "BR-ACT4-004"])

    def test_a_web_app_document_the_map_holds_is_flagged_like_a_connections_one(self):
        upl = "docs/apps/UPL/UPL-1.0-My-Uploads.md"
        entry = {**RULE_MAP["documents"][0], "doc": upl, "prefix": "BR-UPL1"}
        new = revise(RULE_DOC, "   It may equal", "   It may not equal")
        doc = {"path": upl, "old_path": None, "predecessor": None, "status": "M",
               "key": "b" * 40, **docimpact.rule_changes(RULE_DOC, new)}
        texts = {"base": RULE_DOC, "head": new}
        items = docimpact.rule_refresh({"base": "base", "head": "head", "documents": [doc]},
                                       {"documents": [entry]}, read=lambda rev, _: texts[rev])
        self.assertEqual([(i["doc"], i["prefix"]) for i in items], [(upl, "BR-UPL1")])
        self.assertEqual([c["rule_id"] for c in items[0]["changed"]], ["BR-ACT4-002"])

    def test_requirement_number_in_changed_text_reaches_its_rule(self):
        new = revise(RULE_DOC, "applies to every activity", "applies to closed activities")
        self.assertEqual([c["rule_id"] for c in self.review(MAPPED, new)[0]["changed"]],
                         ["BR-ACT4-003"])

    def test_change_the_anchors_cannot_place_still_files_the_item(self):
        new = revise(RULE_DOC, "# Activity Entry\n", "# Activity Entry\n\nA new preface.\n")
        items = self.review(MAPPED, new)
        self.assertEqual((len(items), items[0]["changed"]), (1, []))

    def test_layout_only_change_files_nothing(self):
        new = revise(RULE_DOC, "The Save button returns", "The Save button\nreturns")
        self.assertEqual(self.review(MAPPED, new), [])

    def test_revised_unmapped_document_files_nothing(self):
        new = revise(RULE_DOC, "   It may equal", "   It may not equal")
        self.assertEqual(self.review(UNMAPPED, new), [])

    def test_removed_mapped_document_puts_every_rule_up_for_retiring(self):
        doc = {"path": MAPPED, "old_path": None, "predecessor": None, "status": "D",
               "key": "removed-" + "c" * 40, **docimpact.rule_changes(RULE_DOC, None)}
        items = docimpact.rule_refresh({"base": "b", "head": "h", "documents": [doc]}, RULE_MAP)
        self.assertEqual(len(items[0]["changed"]), 6)

    def test_restarted_numbering_is_reported(self):
        new = revise(RULE_DOC, "## Navigation\n", "## Navigation\n\n1. Save is always shown.\n")
        self.assertTrue(self.review(MAPPED, new)[0]["restarts"])

    def changed(self, items):
        return [c["rule_id"] for c in items[0]["changed"]]

    def test_requirement_number_followed_by_punctuation_is_found(self):
        new = revise(RULE_DOC, "applies to every activity.",
                     "applies to every activity (see CPRS-5.2.3.1).")
        self.assertEqual(self.changed(self.review(MAPPED, new)), ["BR-ACT4-003"])

    def test_heading_with_a_qualifier_matches_its_bare_anchor(self):
        new = revise(RULE_DOC, "An image of the window.", "An image of the new window.")
        self.assertEqual(self.changed(self.review(MAPPED, new)), ["BR-ACT4-005"])

    def test_hunk_that_crosses_a_heading_reaches_both_sections(self):
        new = revise(RULE_DOC, "The Save button returns to the activity list.\n\n"
                     "## Screen Print (if applicable):\n\nAn image of the window.",
                     "Save returns home.\n\n## Screen Print (if applicable):\n\nNo image.")
        self.assertEqual(self.changed(self.review(MAPPED, new)),
                         ["BR-ACT4-004", "BR-ACT4-005"])

    def test_section_with_a_number_is_a_numbered_rule(self):
        self.assertEqual(docimpact.anchor_of({"anchor": "Section 42.iv, Page 18"}),
                         ("number", 42))

    def test_renamed_document_reads_its_old_text_and_reports_the_old_map_path(self):
        new = revise(RULE_DOC, "   It may equal", "   It may not equal")
        moved = "docs/apps/CONNECTIONS/Activity Entry Window.md"
        doc = {"path": moved, "old_path": MAPPED, "predecessor": None, "status": "R",
               "key": "b" * 40, **docimpact.rule_changes(RULE_DOC, new)}
        texts = {("base", MAPPED): RULE_DOC, ("head", moved): new}
        items = docimpact.rule_refresh({"base": "base", "head": "head", "documents": [doc]},
                                       RULE_MAP, read=lambda rev, p: texts[(rev, p)])
        self.assertEqual((items[0]["doc"], items[0]["map_doc"]), (moved, MAPPED))
        self.assertEqual(self.changed(items), ["BR-ACT4-002"])

    def test_reissued_document_is_compared_with_the_one_it_replaces(self):
        new = revise(RULE_DOC, "   It may equal", "   It may not equal")
        reissue = "docs/apps/CONNECTIONS/2 Activity Entry.md"
        doc = {"path": reissue, "old_path": None, "predecessor": MAPPED, "status": "A",
               "key": "b" * 40, **docimpact.rule_changes(RULE_DOC, new)}
        texts = {("head", MAPPED): RULE_DOC, ("head", reissue): new}
        items = docimpact.rule_refresh({"base": "base", "head": "head", "documents": [doc]},
                                       RULE_MAP, read=lambda rev, p: texts[(rev, p)])
        self.assertEqual(self.changed(items), ["BR-ACT4-002"])

    def test_future_revision_is_marked_against_the_suite_copy_rules(self):
        new = revise(RULE_DOC, "   It may equal", "   It may not equal")
        ahead = MAPPED.replace("/CONNECTIONS/", "/CONNECTIONS/Future/")
        texts = {("base", ahead): RULE_DOC, ("head", ahead): new}
        doc = {"path": ahead, "old_path": None, "predecessor": None, "current": MAPPED,
               "future": True, "status": "M", "key": "b" * 40,
               **docimpact.rule_changes(RULE_DOC, new)}
        items = docimpact.rule_refresh({"base": "base", "head": "head", "documents": [doc]},
                                       RULE_MAP, read=lambda rev, p: texts[(rev, p)])
        self.assertEqual((items[0]["map_doc"], items[0]["future"]), (MAPPED, True))
        self.assertEqual(self.changed(items), ["BR-ACT4-002"])


def drift_report(**drift) -> dict:
    """One document's report the way a drift read prints it, clean unless drift is given."""
    body = {"folder": None, "missing": [], "changed": [], "moved": [], "extra": [],
            "attachments": [], "other_attachments": [], **drift}
    return {"doc": "docs/apps/UPL/UPL-1.0-My-Uploads.md", "title": "UPL - 1.0 My Uploads",
            "prefix": "BR-UPL1", "rules": 74, "staging_id": 21146,
            "folder": {"id": 22013, "in_staging": True, "promoted_on": None,
                       "newly_promoted": False},
            "clean": not drift, "drift": body,
            "waiting": [{"uploaded_on": "2026-10-13", "rules": ["BR-UPL1-001", "BR-UPL1-002"]}],
            "promoted": []}


def drift_result(*reports: dict) -> dict:
    return {"today": "2026-10-14", "notes": [], "recorded": {"rules": 0, "docs": 0},
            "suites": [{"suite": "UPL", "folder": "docs/apps/UPL", "docs": list(reports)}]}


EDITED = {"rule_id": "BR-UPL1-004", "alm_req_id": 22017,
          "fields": [{"field": "description", "column": "description",
                      "alm": "Edited | by hand", "master": "As extracted"}]}


class AlmDrift(unittest.TestCase):
    def test_a_clean_run_files_nothing_and_lists_what_waits(self):
        review = docimpact.drift_review(drift_result(drift_report()))
        self.assertEqual(review["items"], [])
        self.assertEqual(review["clean"], 1)
        self.assertEqual(review["waiting"][0]["count"], 2)
        self.assertEqual(review["waiting"][0]["by_day"][0]["uploaded_on"], "2026-10-13")

    def test_a_changed_field_files_one_issue_naming_both_values(self):
        review = docimpact.drift_review(drift_result(drift_report(changed=[EDITED])))
        [item] = review["items"]
        self.assertEqual(item["title"], "[Rules] BR-UPL1: UPL - 1.0 My Uploads TM folder "
                                        "differs from the master")
        self.assertIn("| BR-UPL1-004 | 22017 | description (`description`) | "
                      "Edited \\| by hand | As extracted |", item["body"])
        self.assertIn("`rules-update docs/apps/UPL/UPL-1.0-My-Uploads.md`", item["body"])
        self.assertIn("`rules-upload --doc docs/apps/UPL --folder 21146 --send`", item["body"])
        self.assertTrue(item["body"].endswith(
            f"TM drift: docs/apps/UPL/UPL-1.0-My-Uploads.md under BR-UPL1 at "
            f"{item['fingerprint']}"))

    def test_an_unstaged_folder_names_the_resend_without_a_folder(self):
        report = drift_report(missing=[{"rule_id": "BR-UPL1-009", "alm_req_id": None,
                                        "reason": "never uploaded"}])
        report["staging_id"] = None
        [item] = docimpact.drift_review(drift_result(report))["items"]
        self.assertIn("- BR-UPL1-009: never uploaded", item["body"])
        self.assertIn("`rules-upload --doc docs/apps/UPL --send` with the staging folder's id",
                      item["body"])

    def test_the_same_drift_gives_the_same_marker_and_new_drift_a_new_one(self):
        first = docimpact.drift_review(drift_result(drift_report(changed=[EDITED])))
        again = docimpact.drift_review(drift_result(drift_report(changed=[EDITED])))
        more = docimpact.drift_review(drift_result(drift_report(
            changed=[EDITED], missing=[{"rule_id": "BR-UPL1-009", "alm_req_id": 22030,
                                        "reason": "TM no longer holds the requirement"}])))
        self.assertEqual(first["items"][0]["fingerprint"], again["items"][0]["fingerprint"])
        self.assertNotEqual(first["items"][0]["fingerprint"], more["items"][0]["fingerprint"])

    def test_attachment_drift_carries_both_hashes_and_points_at_a_resend(self):
        changed = {"file": "UPL - 1.0 My Uploads.xlsx", "state": "changed",
                   "alm_sha": "c" * 64, "master_sha": "a" * 64}
        [item] = docimpact.drift_review(drift_result(drift_report(attachments=[changed])))["items"]
        self.assertIn(f"| UPL - 1.0 My Uploads.xlsx | changed | {'c' * 64} | {'a' * 64} |",
                      item["body"])
        self.assertIn("Missing rules, attachments, or folder: resend", item["body"])

    def test_promotions_are_listed_and_never_filed(self):
        report = drift_report()
        report["promoted"] = [{"rule_id": "BR-UPL1-001", "alm_req_id": 22014, "folder": 5000,
                               "promoted_on": "2026-10-14"}]
        report["folder"] = {"id": 22013, "in_staging": False, "promoted_on": "2026-10-14",
                            "newly_promoted": True}
        review = docimpact.drift_review(drift_result(report))
        self.assertEqual(review["items"], [])
        self.assertEqual(review["promoted"][0]["rule_id"], "BR-UPL1-001")
        self.assertEqual(review["folders_promoted"],
                         [{"doc": report["doc"], "folder": 22013, "promoted_on": "2026-10-14"}])


if __name__ == "__main__":
    unittest.main()
