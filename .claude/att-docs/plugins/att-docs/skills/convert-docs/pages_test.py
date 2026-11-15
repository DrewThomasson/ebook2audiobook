#!/usr/bin/env python3
"""Cases for pages.py: where page markers land, and how Word's layout is read."""
from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile
import unittest
import unittest.mock
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pages  # noqa: E402
import stamp  # noqa: E402

BODY = "\n".join([
    "## Brief Description",
    "",
    "The worker opens the report from the home page and picks a county.",
    "",
    "| Field | Value |",
    "|---|---|",
    "| County Name | the county the worker is assigned to |",
    "| Office Code | the office within that county |",
    "",
    "```",
    "SELECT ID_PERSON",
    "FROM PERSON",
    "```",
    "",
    "Closing paragraph that wraps over",
    "two lines of the converted text.",
    "",
])


def layout(*starts: str) -> pages.Layout:
    return pages.Layout(len(starts) + 1, list(starts), "from the PDF")


def markers(markdown: str) -> list[tuple[int, str]]:
    lines = markdown.split("\n")
    return [(i, lines[i + 2]) for i, line in enumerate(lines) if pages.MARKER.match(line)]


class Place(unittest.TestCase):
    def test_page_one_opens_the_body(self):
        placed = pages.place(BODY, layout())
        self.assertEqual(placed.markdown.split("\n")[0], '<a id="page-1"></a>*Page 1*')

    def test_a_page_opening_mid_table_marks_the_whole_table(self):
        placed = pages.place(BODY, layout("Office Code the office within"))
        self.assertEqual(markers(placed.markdown)[1][1], "| Field | Value |")

    def test_a_page_opening_in_a_code_block_marks_the_fence(self):
        placed = pages.place(BODY, layout("FROM PERSON Closing paragraph"))
        self.assertEqual(markers(placed.markdown)[1][1], "```")

    def test_a_page_opening_mid_paragraph_marks_the_paragraph(self):
        placed = pages.place(BODY, layout("two lines of the converted text"))
        self.assertEqual(markers(placed.markdown)[1][1], "Closing paragraph that wraps over")

    def test_pages_land_in_order_and_a_missing_page_is_reported(self):
        placed = pages.place(BODY, layout(
            "The worker opens the report", "text the body never kept at all",
            "Closing paragraph that wraps",
        ))
        self.assertEqual(placed.missed, [3])
        found = [line for line in placed.markdown.split("\n") if pages.MARKER.match(line)]
        self.assertEqual([m.split('"')[1] for m in found], ["page-1", "page-2", "page-4"])

    def test_a_pdf_page_links_to_that_page(self):
        placed = pages.place(BODY, layout("Closing paragraph that wraps"), "https://x/a.pdf")
        self.assertIn(
            '<a id="page-2"></a>*[Page 2](https://x/a.pdf#page=2)*', placed.markdown
        )

    def test_a_later_line_matches_when_the_first_was_not_kept(self):
        start = "Screen Print label\nThe worker opens the report from the home page"
        self.assertEqual(pages.place(BODY, layout(start)).missed, [])

    def test_a_page_opening_in_an_indented_block_marks_its_list_item(self):
        body = "12. The rule text\n\n    1. The first sub-rule of twelve\n\n13. Next rule\n"
        placed = pages.place(body, layout("The first sub-rule of twelve"))
        self.assertEqual(markers(placed.markdown)[1][1], "12. The rule text")

    TABLES = "\n".join([
        "| Field Name | Value Shown |", "| Medical exam is due | a |", "",
        "| Field Name | Value Shown |", "| Medical exam is overdue | b |", "",
    ])

    def test_a_short_piece_in_two_blocks_is_no_match(self):
        start = "Label the body never kept\nField Name Value Shown"
        self.assertEqual(pages.place(self.TABLES, layout(start)).missed, [2])

    def test_the_block_holding_more_of_the_opening_wins(self):
        start = "Label the body never kept\nField Name Value Shown\nMedical exam is overdue"
        placed = pages.place(self.TABLES, layout(start))
        self.assertEqual(placed.missed, [])
        lines = placed.markdown.split("\n")
        at = lines.index('<a id="page-2"></a>*Page 2*')
        self.assertEqual(lines[at + 3], "| Medical exam is overdue | b |")


class Openings(unittest.TestCase):
    def test_running_header_page_number_and_bullets_come_off(self):
        page = "Process Description\n\nPage {n} of 3\nBody text of page {n}\n"
        lines = pages.opening_lines([page.format(n=n) for n in (1, 2, 3)])
        self.assertEqual(lines[1], ["Body text of page 2"])

    def test_a_two_page_header_comes_off(self):
        page = "Process Description\nDOCUMENTATION\nBody text of page {n}\n"
        lines = pages.opening_lines([page.format(n=n) for n in (1, 2)])
        self.assertEqual(lines[1], ["Body text of page 2"])

    def test_a_missing_tool_costs_the_pages_only(self):
        scratch = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, scratch, ignore_errors=True)
        missing = pathlib.Path(scratch) / "none.pdf"
        with unittest.mock.patch.object(pages.subprocess, "run", side_effect=OSError):
            self.assertEqual(pages.pdf_pages(missing), [])
            self.assertIsNone(pages.render(missing, missing.parent))


class Word(unittest.TestCase):
    def docx(self, body: str) -> pathlib.Path:
        scratch = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, scratch, ignore_errors=True)
        path = pathlib.Path(scratch) / "doc.docx"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(
                "word/document.xml", f"<w:document><w:body>{body}</w:body></w:document>"
            )
        return path

    def test_rendered_breaks_are_the_pages(self):
        path = self.docx(
            "<w:p><w:r><w:t>First page text</w:t></w:r></w:p>"
            '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
            "<w:p><w:r><w:lastRenderedPageBreak/><w:t>Second &amp; page</w:t></w:r></w:p>"
            "<w:p><w:r><w:t>still second</w:t><w:lastRenderedPageBreak/>"
            "<w:t xml:space=\"preserve\"> third</w:t></w:r></w:p>"
        )
        found = pages.from_word(path)
        self.assertEqual(found.pages, 3)
        self.assertTrue(found.starts[0].startswith("Second & page"))
        self.assertEqual(found.starts[1].strip(), "third")

    def test_a_file_word_never_laid_out_has_no_word_layout(self):
        path = self.docx('<w:p><w:r><w:t>a</w:t><w:br w:type="page"/><w:t>b</w:t></w:r></w:p>')
        self.assertIsNone(pages.from_word(path))


class SharePoint(unittest.TestCase):
    HOST = "https://example.test"
    LIB = "/sites/ExampleDocs/Application Development Documentation"

    def test_a_word_file_opens_in_the_browser(self):
        path = f"{self.LIB}/O/A [draft].doc"
        line = stamp.sharepoint_line("A [draft].doc", path, self.HOST)
        self.assertEqual(
            line,
            r"- SharePoint: [A \[draft\].doc](https://example.test/sites/"
            "ExampleDocs/Application%20Development%20Documentation/O/"
            "A%20%5Bdraft%5D.doc?web=1)",
        )

    def test_a_pdf_keeps_a_plain_address(self):
        url = stamp.sharepoint_url(f"{self.LIB}/a.pdf", self.HOST)
        self.assertTrue(url.startswith(f"{self.HOST}/sites/"))
        self.assertTrue(url.endswith("/a.pdf"))


class Title(unittest.TestCase):
    def test_a_source_named_without_spaces_takes_its_library_title(self):
        library = {"ACT-4.0-Activity-Entry.docx": "ACT 4.0 - Activity Entry.docx"}
        title = stamp.title_of([pathlib.Path("ACT-4.0-Activity-Entry.docx")], library)
        self.assertEqual(title, "ACT 4.0 - Activity Entry")

    def test_a_page_keeps_an_h1_that_is_its_own_name(self):
        with tempfile.TemporaryDirectory() as folder:
            page = pathlib.Path(folder, "Office-Detail-On-Line-Help.md")
            page.write_text("# Office Detail - On-Line Help\n\nbody\n", encoding="utf-8")
            self.assertEqual(stamp.page_title(page), "Office Detail - On-Line Help")

    def test_an_h1_naming_the_page_another_way_is_not_kept(self):
        with tempfile.TemporaryDirectory() as folder:
            page = pathlib.Path(folder, "Home-On-Line-Help.md")
            page.write_text("# Home\n", encoding="utf-8")
            self.assertIsNone(stamp.page_title(page))
            self.assertIsNone(stamp.page_title(pathlib.Path(folder, "Missing.md")))


if __name__ == "__main__":
    unittest.main()
