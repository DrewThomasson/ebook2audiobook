#!/usr/bin/env python3
"""Cases for pin_notes.py, which writes the body of a pin-move pull request from the
changelog. The changelog is a fixture written in the test, in release-please's format.

usage: python3 scripts/pin/pin_notes_test.py
"""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "pin_notes.py")

CHANGELOG = """# Changelog

## [0.3.0](https://github.com/acme/skills/compare/v0.2.1...v0.3.0) (2026-03-01)


### ⚠ BREAKING CHANGES

* **general:** the extension folder moved ([#30](https://github.com/acme/skills/issues/30))

### Features

* **general:** move the extension folder ([#30](https://github.com/acme/skills/issues/30)) ([abc1234](https://github.com/acme/skills/commit/abc1234))

## [0.2.1](https://github.com/acme/skills/compare/v0.2.0...v0.2.1) (2026-02-01)


### Bug Fixes

* stop the sync from dropping a file ([#20](https://github.com/acme/skills/issues/20)) (#21) ([def5678](https://github.com/acme/skills/commit/def5678))

## [0.2.0](https://github.com/acme/skills/compare/v0.1.0...v0.2.0) (2026-01-15)


### Features

* add the check script ([#10](https://github.com/acme/skills/issues/10)) ([0123456](https://github.com/acme/skills/commit/0123456))

## [0.1.0](https://github.com/acme/skills/compare/v0.0.1...v0.1.0) (2026-01-01)


### Features

* first cut ([#1](https://github.com/acme/skills/issues/1))
"""

MIXED = """# Changelog

## [0.5.1](https://github.com/acme/skills/compare/v0.5.0...v0.5.1) (2026-05-02)


### Bug Fixes

* fix the thing that the workflow broke ([#61](https://github.com/acme/skills/issues/61))

## [0.5.0](https://github.com/acme/skills/compare/v0.4.0...v0.5.0) (2026-05-01)


### Features

* keep the plain entry ([#50](https://github.com/acme/skills/issues/50))
* **general:** keep the entry with a plain scope
* open a pull request for each consumer ([#51](https://github.com/acme/skills/issues/51))
* teach Claude to rebase
* a longer entry
  * nested detail that names the sessions of an agent
* link to https://example.com/run/12
* see #44 for the reason

### Bug Fixes

* Fixes the thing that the workflow broke
"""

ALL_OMITTED = """# Changelog

## [0.6.0](https://github.com/acme/skills/compare/v0.5.0...v0.6.0) (2026-06-01)


### Features

* fix what the workflow broke ([#70](https://github.com/acme/skills/issues/70))
"""

NO_LINKS = """# Changelog

## 0.2.0 (2026-01-15)

### Features

* add the check script

## 0.1.0 (2026-01-01)

### Features

* first cut
"""


def body(changelog, old, new, repo="acme/skills"):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "CHANGELOG.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(changelog)
        return subprocess.run(
            [sys.executable, "-I", SCRIPT, "--changelog", path, "--from", old, "--to", new, "--repo", repo],
            capture_output=True,
            text=True,
        )


class PinNotes(unittest.TestCase):
    def test_lists_only_versions_after_the_pin_up_to_the_target(self):
        r = body(CHANGELOG, "v0.2.0", "v0.2.1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("0.2.1", r.stdout)
        self.assertIn("stop the sync from dropping a file", r.stdout)
        self.assertNotIn("add the check script", r.stdout)
        self.assertNotIn("move the extension folder", r.stdout)

    def test_spans_every_version_between_the_pin_and_the_target(self):
        r = body(CHANGELOG, "v0.1.0", "v0.3.0")
        for text in ("0.3.0", "0.2.1", "0.2.0", "add the check script"):
            self.assertIn(text, r.stdout)
        self.assertNotIn("first cut", r.stdout)

    def test_names_both_versions_and_links_nothing(self):
        r = body(CHANGELOG, "v0.2.0", "v0.2.1")
        self.assertIn("from v0.2.0 to v0.2.1", r.stdout)
        self.assertNotIn("http", r.stdout)
        self.assertNotIn("releases/tag", r.stdout)
        self.assertNotIn("acme", r.stdout)

    def test_drops_issue_and_commit_references(self):
        r = body(CHANGELOG, "v0.1.0", "v0.3.0")
        self.assertNotIn("/issues/", r.stdout)
        self.assertNotIn("/commit/", r.stdout)
        self.assertNotRegex(r.stdout, r"#\d+")

    def test_a_minor_version_move_adds_the_contract_note(self):
        r = body(CHANGELOG, "v0.2.1", "v0.3.0")
        self.assertIn("extension contract changed", r.stdout)

    def test_a_patch_only_move_has_no_contract_note(self):
        r = body(CHANGELOG, "v0.2.0", "v0.2.1")
        self.assertNotIn("contract", r.stdout)

    def test_a_move_across_several_minors_has_the_note(self):
        r = body(CHANGELOG, "v0.1.0", "v0.2.1")
        self.assertIn("extension contract changed", r.stdout)

    def test_a_pin_missing_from_the_changelog_still_selects_by_number(self):
        r = body(CHANGELOG, "v0.1.5", "v0.2.1")
        self.assertIn("0.2.1", r.stdout)
        self.assertIn("add the check script", r.stdout)
        self.assertNotIn("first cut", r.stdout)

    def test_leaves_out_entries_that_name_the_tracker_or_builds_or_an_assistant(self):
        r = body(MIXED, "v0.4.0", "v0.5.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("keep the plain entry", r.stdout)
        self.assertIn("keep the entry with a plain scope", r.stdout)
        for text in ("pull request", "workflow", "Claude", "see #44", "link to", "Fixes"):
            self.assertNotIn(text, r.stdout)
        # A multi-line entry goes whole, nested lines included.
        self.assertNotIn("nested detail", r.stdout)
        self.assertNotIn("sessions", r.stdout)

    def test_counts_the_entries_it_left_out(self):
        r = body(MIXED, "v0.4.0", "v0.5.0")
        self.assertIn("6 changelog entries are left out", r.stdout)
        one = body(MIXED, "v0.5.0", "v0.5.1")
        # The count is what matters, not the sentence around it.
        self.assertRegex(one.stdout, r"\b1 changelog entry\b")
        self.assertNotRegex(one.stdout, r"\b[2-9] changelog entr")

    def test_no_omission_note_when_nothing_was_left_out(self):
        r = body(CHANGELOG, "v0.1.0", "v0.3.0")
        self.assertNotIn("left out", r.stdout)

    def test_drops_a_heading_whose_entries_were_all_left_out(self):
        r = body(MIXED, "v0.4.0", "v0.5.0")
        self.assertNotIn("Bug Fixes", r.stdout)
        self.assertIn("#### Features", r.stdout)

    def test_suppresses_a_version_heading_when_all_its_entries_were_left_out(self):
        r = body(MIXED, "v0.4.0", "v0.5.1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("### v0.5.1", r.stdout)
        self.assertIn("### v0.5.0", r.stdout)
        self.assertIn("7 changelog entries are left out", r.stdout)

    def test_counts_omissions_when_every_version_is_suppressed(self):
        r = body(MIXED, "v0.5.0", "v0.5.1")
        self.assertNotIn("### v0.5.1", r.stdout)
        self.assertNotIn("No changelog entries", r.stdout)
        self.assertIn("1 changelog entry cannot be shown here, so none are listed.", r.stdout)
        self.assertNotIn("left out of this list", r.stdout)

    def test_contract_note_does_not_point_to_entries_when_none_are_shown(self):
        r = body(ALL_OMITTED, "v0.5.0", "v0.6.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("extension contract changed", r.stdout)
        self.assertNotIn("entries below", r.stdout)
        self.assertNotIn("###", r.stdout.replace("## Changes since", ""))
        self.assertIn("1 changelog entry cannot be shown here", r.stdout)

    def test_contract_note_points_to_entries_when_some_are_shown(self):
        r = body(CHANGELOG, "v0.2.1", "v0.3.0")
        self.assertIn("against the entries below", r.stdout)

    def test_no_start_note_when_the_earliest_section_follows_the_pin(self):
        r = body(CHANGELOG, "v0.0.1", "v0.2.1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("first cut", r.stdout)
        self.assertNotIn("changelog starts", r.stdout)

    def test_says_where_the_changelog_starts_when_the_pin_is_older(self):
        r = body(CHANGELOG, "v0.0.0", "v0.2.1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("The changelog starts at v0.1.0; it cannot show anything older.", r.stdout)

    def test_says_where_the_changelog_starts_when_headings_have_no_compare_link(self):
        r = body(NO_LINKS, "v0.0.1", "v0.2.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("The changelog starts at v0.1.0;", r.stdout)

    def test_no_start_note_when_the_pin_is_inside_the_changelog(self):
        r = body(CHANGELOG, "v0.1.0", "v0.3.0")
        self.assertNotIn("changelog starts", r.stdout)

    def test_a_changelog_without_the_target_section_is_an_error(self):
        r = body(CHANGELOG, "v0.2.0", "v0.9.0")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("No changelog entries", r.stdout)
        self.assertIn("no section for v0.9.0", r.stderr)

    def test_an_empty_changelog_is_an_error(self):
        for text in ("", "# Changelog\n"):
            r = body(text, "v0.2.0", "v0.2.1")
            self.assertNotEqual(r.returncode, 0)
            self.assertNotIn("No changelog entries", r.stdout)
            self.assertIn("no release sections", r.stderr)

    def test_says_so_when_the_changelog_has_nothing_in_range(self):
        r = body(CHANGELOG, "v0.3.0", "v0.3.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("No changelog entries", r.stdout)

    def test_never_names_the_tracker_or_an_assistant(self):
        r = body(CHANGELOG, "v0.1.0", "v0.3.0").stdout.lower()
        for word in ("issue", "claude", "anthropic", "github actions", "workflow"):
            self.assertNotIn(word, r)

    def test_refuses_a_tag_that_is_not_a_plain_version(self):
        for bad in ("v0.3", "0.3.0", "v0.3.0-rc1", "v1.2.3.4"):
            r = body(CHANGELOG, "v0.2.0", bad)
            self.assertNotEqual(r.returncode, 0, bad)


if __name__ == "__main__":
    unittest.main()
