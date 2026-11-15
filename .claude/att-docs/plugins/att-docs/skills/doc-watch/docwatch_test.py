#!/usr/bin/env python3
"""Cases for docwatch.py, run against a fixture repository and config: where a scan folder's
files sit in their library, the Future folder a revision the web app does not carry yet
converts into, and the config check."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "docwatch.py"
SHIFTED = HERE.parent / "convert-docs" / "check-shifted-text.py"
SPEC = importlib.util.spec_from_file_location("docwatch", SCRIPT)
DOCWATCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DOCWATCH)

LIBRARIES = {
    "": ["/sites/Main", "Main Documentation"],
    "Team": ["/sites/Group/Team", "Shared Documents"],
    "Spec": ["/sites/Group/Spec", "Design"],
}
FOLDERS = "Process Description\tALPHA\nTeam:Requirements\tTEAM\nSpec:\tSPEC\nOld\tskip\n"


def fixture(root: pathlib.Path, folders: str = FOLDERS) -> pathlib.Path:
    """A git repository holding both configs and the tables; returns the doc-watch config."""
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    # A first commit, so the issue body's commit-day lookup has a history to read.
    subprocess.run(["git", "-C", str(root), "-c", "user.name=fixture",
                    "-c", "user.email=fixture@example.test",
                    "commit", "-q", "--allow-empty", "-m", "fixture"], check=True)
    ext = root / "ext"
    ext.mkdir()
    (ext / "words.txt").write_text("plain\ntext\nprogress\n", encoding="utf-8")
    (ext / "folders.tsv").write_text(folders, encoding="utf-8")
    (ext / "convert.json").write_text(json.dumps({
        "todoRoot": "inbox", "appsRoot": "converted", "futureFolder": "Future",
        "words": "ext/words.txt", "sharePointHost": "https://example.test",
    }), encoding="utf-8")
    config = ext / "doc-watch.json"
    config.write_text(json.dumps({
        "convert": "ext/convert.json", "libraries": LIBRARIES,
        "suites": {"A": "ALPHA", "T": "TEAM", "S": "SPEC"},
        "folders": "ext/folders.tsv", "sources": "ext/sources.tsv",
        "ignored": "ext/ignored.tsv", "notFromLibrary": r"^Export \d+\.txt$",
    }), encoding="utf-8")
    return config


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, check=False)


class Configured(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.folder.name)
        self.config = fixture(self.repo)
        DOCWATCH.configure(str(self.config))

    def tearDown(self) -> None:
        self.folder.cleanup()


class LibraryPath(Configured):
    def test_default_folder_sits_in_the_default_library(self) -> None:
        self.assertEqual(
            DOCWATCH.library_path("Process Description/ACT", "ACT 4.0.doc"),
            "/sites/Main/Main Documentation/Process Description/ACT/ACT 4.0.doc",
        )

    def test_qualified_folder_sits_in_its_own_library(self) -> None:
        self.assertEqual(
            DOCWATCH.library_path("Team:Requirements and Processes/Testing", "Plan.docx"),
            "/sites/Group/Team/Shared Documents/Requirements and Processes/Testing/Plan.docx",
        )

    def test_library_root_takes_no_slash(self) -> None:
        self.assertEqual(
            DOCWATCH.library_path("Spec:", "8 - Search Page.doc"),
            "/sites/Group/Spec/Design/8 - Search Page.doc",
        )
        self.assertEqual(DOCWATCH.file_in("Spec:", "a.doc"), "Spec:a.doc")
        self.assertEqual(DOCWATCH.file_in("Spec:Use Cases", "a.ppt"), "Spec:Use Cases/a.ppt")

    def test_library_root_holds_its_folders_and_no_other_library(self) -> None:
        self.assertTrue(DOCWATCH.under("Spec:", "Spec:"))
        self.assertTrue(DOCWATCH.under("Spec:Use Cases", "Spec:"))
        self.assertFalse(DOCWATCH.under("Team:Testing", "Spec:"))
        self.assertFalse(DOCWATCH.under("Process Descriptions", "Process Description"))

    def test_root_source_row_means_the_files_at_the_root(self) -> None:
        self.assertTrue(DOCWATCH.from_source("Spec:", "Spec:"))
        self.assertFalse(DOCWATCH.from_source("Spec:Electronic Payment", "Spec:"))
        self.assertTrue(DOCWATCH.from_source("ALPHA/Process Descriptions/x", "ALPHA"))


def converted(path: pathlib.Path, source: str, day: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Title\n\n**Document provenance**\n\n- Source: `{source}`\n- Converted: {day}\n",
        encoding="utf-8",
    )


class Lookup(Configured):
    def report(self, *rows: tuple[str, ...]) -> str:
        lines = ["|".join(("LOOKUP", *row)) for row in rows]
        return "\n".join(["DOCWATCH-BEGIN", *lines, "WALKED|1|1", "DOCWATCH-END"])

    def test_a_same_day_edit_after_the_conversion_minute_is_stale(self) -> None:
        converted(self.repo / "converted" / "ALPHA" / "1-Home.md", "1 - Home.doc",
                  "2026-10-13 10:04Z")
        text = self.report(("Process%20Description", "1%20-%20Home.doc",
                            "2026-10-13T14%3A31%3A00Z", "100", "ALPHA"))
        out = DOCWATCH.lookup(text, ["1 - Home.doc"])
        self.assertEqual([c["replaces"] for c in out["changed"]], ["converted/ALPHA/1-Home.md"])

    def test_an_edit_before_the_conversion_minute_is_current(self) -> None:
        converted(self.repo / "converted" / "ALPHA" / "1-Home.md", "1 - Home.doc",
                  "2026-10-13 10:04Z")
        text = self.report(("Process%20Description", "1%20-%20Home.doc",
                            "2026-10-13T10%3A03%3A00Z", "100", "ALPHA"))
        out = DOCWATCH.lookup(text, ["1 - Home.doc"])
        self.assertEqual((out["changed"], out["current"]), ([], ["1 - Home.doc"]))

    def test_a_date_only_conversion_is_stale_on_the_day_it_was_edited(self) -> None:
        converted(self.repo / "converted" / "ALPHA" / "1-Home.md", "1 - Home.doc", "2026-10-13")
        text = self.report(("Process%20Description", "1%20-%20Home.doc",
                            "2026-10-13T08%3A00%3A00Z", "100", "ALPHA"))
        self.assertEqual(len(DOCWATCH.lookup(text, ["1 - Home.doc"])["changed"]), 1)

    def test_a_document_with_no_converted_copy_is_new_and_a_missing_one_not_found(self) -> None:
        text = self.report(("Process%20Description", "2%20-%20Other.doc",
                            "2026-10-13T08%3A00%3A00Z", "100", "ALPHA"))
        out = DOCWATCH.lookup(text, ["2 - Other.doc", "3 - Gone.doc"])
        self.assertEqual([n["suite"] for n in out["new"]], ["ALPHA"])
        self.assertEqual(out["not_found"], ["3 - Gone.doc"])

    def test_a_walk_that_did_not_finish_is_not_read_as_not_found(self) -> None:
        out = DOCWATCH.lookup("DOCWATCH-BEGIN\nSESSION|expired\nDOCWATCH-END", ["1 - Home.doc"])
        self.assertEqual((out["readable"], out["not_found"], out["session"]),
                         (False, [], "expired"))

    def test_an_edit_in_the_conversion_minute_is_stale(self) -> None:
        converted(self.repo / "converted" / "ALPHA" / "1-Home.md", "1 - Home.doc",
                  "2026-10-13 10:04Z")
        text = self.report(("Process%20Description", "1%20-%20Home.doc",
                            "2026-10-13T10%3A04%3A40Z", "100", "ALPHA"))
        self.assertEqual(len(DOCWATCH.lookup(text, ["1 - Home.doc"])["changed"]), 1)

    def test_a_new_document_in_a_folder_with_no_suite_needs_one(self) -> None:
        text = self.report(("Process%20Description", "2%20-%20Other.doc",
                            "2026-10-13T08%3A00%3A00Z", "100", "track"))
        out = DOCWATCH.lookup(text, ["2 - Other.doc"])
        self.assertEqual((out["new"], len(out["no_suite"])), ([], 1))

    def test_a_revision_copy_is_not_weighed_against_the_current_one(self) -> None:
        converted(self.repo / "converted" / "ALPHA" / "1-Home.md", "1 - Home.doc",
                  "2026-10-13 10:04Z")
        text = self.report(
            ("Process%20Description", "1%20-%20Home.doc", "2026-10-13T10%3A03%3A00Z", "100",
             "ALPHA", ""),
            ("Process%20Description/Revision%20History", "1%20-%20Home.doc",
             "2026-10-01T09%3A00%3A00Z", "90", "ALPHA", "side"))
        out = DOCWATCH.lookup(text, ["1 - Home.doc"])
        self.assertEqual((out["held"], out["current"]), ([], ["1 - Home.doc"]))

    def test_the_payload_asks_for_the_named_documents(self) -> None:
        script = DOCWATCH.payload("lookup", False, ("2 - Other.doc",))
        self.assertIn(DOCWATCH.fnv("2 - Other"), script)


class FutureFolder(Configured):
    def test_future_copy_shadows_the_suite_copy(self) -> None:
        apps = self.repo / "converted"
        converted(apps / "SPEC" / "1-Home.md", "1 - Home.doc", "2026-01-01")
        converted(apps / "SPEC" / "Future" / "1-Home.md", "1 - Home.doc", "2026-10-26")
        converted(apps / "SPEC" / "2-Agency.md", "2 - Agency.doc", "2026-01-01")
        converted(apps / "SPEC" / "3-Export.md", "Export 12.txt", "2026-01-01")
        index = DOCWATCH.build_index()
        self.assertEqual(
            [(c["path"], c["future"]) for c in index["1 - Home.doc"]],
            [("converted/SPEC/Future/1-Home.md", True)],
        )
        self.assertFalse(index["2 - Agency.doc"][0]["future"])
        self.assertNotIn("Export 12.txt", index)
        every = DOCWATCH.build_index(follow=False)
        self.assertEqual(len(every["1 - Home.doc"]), 2)

    def test_place_puts_a_named_revision_in_the_future_folder(self) -> None:
        downloads = self.repo / "downloads"
        downloads.mkdir()
        for name in ("1 - Home.doc", "2 - Agency.doc"):
            (downloads / name).write_bytes(b"doc")
        item = {"suite": "SPEC", "folder": "Spec:", "modified": "2026-10-20T00:00:00Z",
                "converted": "2026-01-01"}
        result = {"changed": [
            {**item, "name": "1 - Home.doc", "url": "/x/1 - Home.doc",
             "replaces": "converted/SPEC/1-Home.md"},
            {**item, "name": "2 - Agency.doc", "url": "/x/2 - Agency.doc",
             "replaces": "converted/SPEC/2-Agency.md"},
        ], "new": []}
        DOCWATCH.place(result, downloads, True, self.repo, future=frozenset({"1 - Home.doc"}))
        todo = self.repo / "inbox"
        self.assertTrue((todo / "SPEC" / "Future" / "1-Home.doc").exists())
        self.assertTrue((todo / "SPEC" / "2-Agency.doc").exists())
        rows = (todo / "library.tsv").read_text(encoding="utf-8").splitlines()[1:]
        self.assertEqual(rows, [
            "SPEC\t2-Agency.doc\t/x/2 - Agency.doc",
            "SPEC/Future\t1-Home.doc\t/x/1 - Home.doc",
        ])

    def test_place_refuses_a_future_name_outside_the_batch(self) -> None:
        with self.assertRaises(SystemExit):
            DOCWATCH.place({"changed": [], "new": []}, self.repo, False, self.repo,
                           future=frozenset({"missing.doc"}))

    def test_issue_body_names_the_configured_roots(self) -> None:
        converted(self.repo / "converted" / "SPEC" / "1-Home.md", "1 - Home.doc", "2026-01-01")
        waiting = self.repo / "inbox" / "SPEC" / "Future" / "1-Home.doc"
        waiting.parent.mkdir(parents=True)
        waiting.write_bytes(b"doc")
        (self.repo / "inbox" / "library.tsv").write_text(
            "SPEC/Future\t1-Home.doc\t/sites/Group/Spec/Design/1 - Home.doc\n",
            encoding="utf-8",
        )
        (self.repo / "inbox" / "_done").mkdir()
        (self.repo / "inbox" / "_done" / "old.doc").write_bytes(b"doc")
        body = DOCWATCH.issue_body(None, self.repo)
        self.assertIn(
            "- [ ] SPEC: `1-Home.doc`, modified not recorded, **not migrated, converts into"
            " `converted/SPEC/Future/`**, beside `converted/SPEC/1-Home.md`",
            body,
        )
        self.assertNotIn("old.doc", body)


class CheckConfig(unittest.TestCase):
    def test_every_folder_row_names_a_listed_library(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            config = fixture(pathlib.Path(folder))
            done = run("--config", str(config), "check-config")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("3 libraries, 3 suites, 4 folder rows", done.stdout)

    def test_a_row_naming_no_listed_library_fails(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            config = fixture(pathlib.Path(folder), FOLDERS + "Other:Docs\tALPHA\n")
            done = run("--config", str(config), "check-config")
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("'Other:Docs' names no library the config lists", done.stderr)

    def test_a_missing_config_exits_64(self) -> None:
        self.assertEqual(run("check-config").returncode, 64)
        self.assertEqual(run("--config", "/nonexistent/x.json", "index").returncode, 64)


class ShiftedTextLabel(unittest.TestCase):
    def test_label_starting_with_a_hyphen_is_not_read_as_an_option(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            fixture(root)
            body = root / "-PROGRESS-IN-CRM.md"
            body.write_text("# Progress\n\nPlain text.\n", encoding="utf-8")
            done = subprocess.run(
                [sys.executable, str(SHIFTED), "--config", str(root / "ext" / "convert.json"),
                 "--label=-PROGRESS-IN-CRM", "--", str(body)],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(done.returncode, 0, done.stderr)


if __name__ == "__main__":
    unittest.main()
