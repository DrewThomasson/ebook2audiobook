#!/usr/bin/env python3
"""Cases for hidden-text.py: Word's hidden runs never reach the Markdown."""
from __future__ import annotations

import importlib.util
import pathlib
import shutil
import subprocess
import tempfile
import unittest
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("hidden_text", HERE / "hidden-text.py")
HIDDEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HIDDEN)

# The package parts the list-numbers cases build a Word file from.
PARTS_SPEC = importlib.util.spec_from_file_location("list_numbers_test", HERE / "list-numbers_test.py")
WORD = importlib.util.module_from_spec(PARTS_SPEC)
PARTS_SPEC.loader.exec_module(WORD)

NS = WORD.NS
STYLES = (
    f'<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="{NS}">'
    '<w:style w:type="character" w:styleId="Jump"><w:name w:val="Jump"/>'
    "<w:rPr><w:vanish/></w:rPr></w:style>"
    '<w:style w:type="character" w:styleId="JumpShown"><w:name w:val="Jump Shown"/>'
    '<w:basedOn w:val="Jump"/><w:rPr><w:vanish w:val="0"/></w:rPr></w:style>'
    '<w:style w:type="character" w:styleId="JumpChild"><w:name w:val="Jump Child"/>'
    '<w:basedOn w:val="Jump"/></w:style>'
    '<w:style w:type="paragraph" w:styleId="Hidden"><w:name w:val="Hidden"/>'
    "<w:rPr><w:vanish/></w:rPr></w:style>"
    "</w:styles>"
)


JUMP = '<w:rStyle w:val="Jump"/>'


def run(text, properties=""):
    rpr = f"<w:rPr>{properties}</w:rPr>" if properties else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{text}</w:t></w:r>'


def para(*runs):
    return f'<w:p>{"".join(runs)}</w:p>'


def docx(path, *paragraphs, styles=STYLES):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", WORD.CONTENT_TYPES)
        archive.writestr("_rels/.rels", WORD.RELS)
        archive.writestr("word/_rels/document.xml.rels", WORD.DOCUMENT_RELS)
        archive.writestr("word/styles.xml", styles)
        archive.writestr(
            "word/document.xml",
            f'<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="{NS}">'
            f'<w:body>{"".join(paragraphs)}</w:body></w:document>',
        )


class HiddenTextTest(unittest.TestCase):
    def setUp(self):
        self.work = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.work)

    def visible(self, *paragraphs, styles=STYLES):
        source, target = self.work / "in.docx", self.work / "out.docx"
        docx(source, *paragraphs, styles=styles)
        self.assertEqual(HIDDEN.main(["hidden-text.py", str(source), str(target)]), 0)
        with zipfile.ZipFile(target) as archive:
            document = archive.read("word/document.xml").decode("utf-8")
        return target, document

    def test_a_run_hidden_directly_goes(self):
        _, document = self.visible(para(run("Contents"), run("Contents_2", "<w:vanish/>")))
        self.assertIn("Contents<", document)
        self.assertNotIn("Contents_2", document)

    def test_a_run_hidden_through_its_character_style_goes(self):
        _, document = self.visible(para(
            run("Call Entry Window"), run("Call_Entry_Window", '<w:rStyle w:val="JumpChild"/>')))
        self.assertNotIn("Call_Entry_Window", document)

    def test_a_run_shown_by_its_own_value_or_its_style_stays(self):
        _, document = self.visible(para(
            run("shown", '<w:vanish w:val="false"/>'),
            run("styled", '<w:rStyle w:val="JumpShown"/>'),
            run("direct wins", '<w:rStyle w:val="Jump"/><w:vanish w:val="0"/>')))
        for text in ("shown", "styled", "direct wins"):
            self.assertIn(text, document)

    def test_a_run_hidden_through_its_paragraph_style_goes(self):
        _, document = self.visible(
            '<w:p><w:pPr><w:pStyle w:val="Hidden"/></w:pPr>'
            f'{run("Exi")}</w:p>', para(run("After")))
        self.assertNotIn("Exi", document)
        self.assertIn("After", document)

    def test_paragraph_and_character_styles_that_both_hide_cancel(self):
        _, document = self.visible(
            '<w:p><w:pPr><w:pStyle w:val="Hidden"/></w:pPr>'
            f'{run("both", JUMP)}'
            f'{run("paragraph only")}</w:p>')
        self.assertIn("both", document)
        self.assertNotIn("paragraph only", document)

    def test_the_document_defaults_hide_a_run_no_style_speaks_for(self):
        styles = STYLES.replace(
            f'xmlns:w="{NS}">',
            f'xmlns:w="{NS}"><w:docDefaults><w:rPrDefault><w:rPr><w:vanish/>'
            "</w:rPr></w:rPrDefault></w:docDefaults>", 1)
        _, document = self.visible(
            para(run("default"), run("shown", '<w:vanish w:val="0"/>')), styles=styles)
        self.assertNotIn("default", document)
        self.assertIn("shown", document)

    def test_spec_vanish_alone_stays(self):
        _, document = self.visible(para(run("Heading text", "<w:specVanish/>")))
        self.assertIn("Heading text", document)

    def test_a_hidden_run_in_a_table_goes(self):
        cell = f'<w:tc>{para(run("cell"), run("Jump_Name", "<w:vanish/>"))}</w:tc>'
        _, document = self.visible(f"<w:tbl><w:tr>{cell}</w:tr></w:tbl>", para(run("end")))
        self.assertIn("cell", document)
        self.assertNotIn("Jump_Name", document)

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is not installed")
    def test_a_field_whose_code_is_hidden_keeps_working(self):
        def field(kind, hidden=""):
            rpr = "<w:rPr><w:vanish/></w:rPr>" if hidden else ""
            return f'<w:r>{rpr}<w:fldChar w:fldCharType="{kind}"/></w:r>'
        code = ('<w:r><w:rPr><w:vanish/></w:rPr><w:instrText xml:space="preserve">'
                ' HYPERLINK "http://x.y" </w:instrText></w:r>')
        target, document = self.visible(para(
            run("See "), field("begin", "hidden"), code, field("separate", "hidden"),
            run("link"), field("end"), run(" now")))
        self.assertEqual(document.count("<w:fldChar "), 3)
        self.assertIn("HYPERLINK", document)
        out = subprocess.run(["pandoc", "-f", "docx", "-t", "gfm", str(target)],
                             capture_output=True, text=True, check=True).stdout
        self.assertEqual(out.strip(), "See [link](http://x.y) now")

    def test_convert_runs_it_before_the_list_numbers_and_pandoc(self):
        script = (HERE / "convert.sh").read_text()
        hidden = script.index('"$HERE/hidden-text.py" "$input" "$WORK/visible.docx"')
        numbers = script.index('"$HERE/list-numbers.py"')
        markers = script.index('--lua-filter="$HERE/list-markers.lua"')
        self.assertLess(hidden, numbers)
        self.assertLess(numbers, markers)

    def test_a_file_that_is_not_a_zip_fails(self):
        source = self.work / "in.rtf"
        source.write_text("{\\rtf1 plain}")
        self.assertEqual(HIDDEN.main(["hidden-text.py", str(source), str(self.work / "o")]), 1)

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is not installed")
    def test_a_hidden_paragraph_writes_no_line(self):
        target, _ = self.visible(
            para(run("Before the table.")),
            para(run("Exi", '<w:rFonts w:cs="Arial"/><w:vanish/>')),
            para(run("By selecting "), run("omeHome", "<w:vanish/>"), run("the button.")))
        out = subprocess.run(["pandoc", "-f", "docx", "-t", "gfm", str(target)],
                             capture_output=True, text=True, check=True).stdout
        self.assertEqual([line for line in out.splitlines() if line.strip()],
                         ["Before the table.", "By selecting the button."])


if __name__ == "__main__":
    unittest.main()
