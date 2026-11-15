#!/usr/bin/env python3
"""Cases for list-numbers.py: the numbers and nesting Pandoc draws after the rewrite."""
from __future__ import annotations

import importlib.util
import pathlib
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "list-numbers.py"
SPEC = importlib.util.spec_from_file_location("list_numbers", SCRIPT)
LIST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LIST)

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{" + NS + "}"

CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.'
    'relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-'
    'officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-'
    'officedocument.wordprocessingml.numbering+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-'
    'officedocument.wordprocessingml.styles+xml"/>'
    "</Types>"
)
RELS = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
    'relationships/officeDocument" Target="word/document.xml"/></Relationships>'
)
DOCUMENT_RELS = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
    'relationships/numbering" Target="numbering.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
    'relationships/styles" Target="styles.xml"/></Relationships>'
)
STYLES = (
    f'<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="{NS}">'
    '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/></w:style>'
    "</w:styles>"
)


def level(ilvl, fmt="decimal", text=None, left=None, hanging=360, start=1, restart=None):
    text = text or f"%{ilvl + 1}."
    indent = "" if left is None else (
        f'<w:pPr><w:ind w:left="{left}" w:hanging="{hanging}"/></w:pPr>')
    restart = "" if restart is None else f'<w:lvlRestart w:val="{restart}"/>'
    return (f'<w:lvl w:ilvl="{ilvl}"><w:start w:val="{start}"/><w:numFmt w:val="{fmt}"/>'
            f'{restart}<w:lvlText w:val="{text}"/>{indent}</w:lvl>')


def abstract(abstract_id, *levels):
    return f'<w:abstractNum w:abstractNumId="{abstract_id}">{"".join(levels)}</w:abstractNum>'


def num(num_id, abstract_id, overrides=()):
    body = "".join(
        f'<w:lvlOverride w:ilvl="{ilvl}"><w:startOverride w:val="{start}"/></w:lvlOverride>'
        for ilvl, start in overrides
    )
    return f'<w:num w:numId="{num_id}"><w:abstractNumId w:val="{abstract_id}"/>{body}</w:num>'


def para(text, num_id=None, ilvl=0, left=None, hanging=None, style=None):
    ppr = ""
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    if num_id is not None:
        ppr += f'<w:numPr><w:ilvl w:val="{ilvl}"/><w:numId w:val="{num_id}"/></w:numPr>'
    if left is not None:
        hang = "" if hanging is None else f' w:hanging="{hanging}"'
        ppr += f'<w:ind w:left="{left}"{hang}/>'
    ppr = f"<w:pPr>{ppr}</w:pPr>" if ppr else ""
    return f"<w:p>{ppr}<w:r><w:t>{text}</w:t></w:r></w:p>"


def table(*paragraphs):
    return f'<w:tbl><w:tr><w:tc>{"".join(paragraphs)}</w:tc></w:tr></w:tbl>'


def docx(path, body, definitions=None):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", RELS)
        archive.writestr("word/_rels/document.xml.rels", DOCUMENT_RELS)
        archive.writestr("word/styles.xml", STYLES)
        archive.writestr(
            "word/document.xml",
            f'<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="{NS}">'
            f'<w:body>{"".join(body)}</w:body></w:document>',
        )
        if definitions is not None:
            archive.writestr(
                "word/numbering.xml",
                f'<?xml version="1.0" encoding="UTF-8"?><w:numbering xmlns:w="{NS}">'
                f'{"".join(definitions)}</w:numbering>',
            )


def drawn(path):
    """What Pandoc's reader makes of each paragraph: (text, level, number), with
    level None for a paragraph continuing the item above and number None for one
    outside any list. Counts by instance and level as the reader does."""
    with zipfile.ZipFile(path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        numbering = ET.fromstring(archive.read("word/numbering.xml"))
    abstracts = {a.get(W + "abstractNumId"): a for a in numbering.findall(W + "abstractNum")}
    links = {n.get(W + "numId"): n.find(W + "abstractNumId").get(W + "val")
             for n in numbering.findall(W + "num")}
    counts, out = {}, []
    for paragraph in document.iter(W + "p"):
        text = "".join(t.text or "" for t in paragraph.iter(W + "t"))
        num_pr = paragraph.find(f"{W}pPr/{W}numPr")
        if num_pr is None:
            out.append((text, None, None))
            continue
        num_id = num_pr.find(W + "numId").get(W + "val")
        ilvl = int(num_pr.find(W + "ilvl").get(W + "val"))
        lvl = next((x for x in abstracts[links[num_id]].findall(W + "lvl")
                    if int(x.get(W + "ilvl")) == ilvl), None)
        if lvl is None:
            out.append((text, None, "continues"))
            continue
        start = int(lvl.find(W + "start").get(W + "val"))
        number = counts[(num_id, ilvl)] + 1 if (num_id, ilvl) in counts else start
        counts = {k: v for k, v in counts.items() if k[1] <= ilvl}
        counts[(num_id, ilvl)] = number
        out.append((text, ilvl, number))
    return out


class Rewriting(unittest.TestCase):
    def setUp(self):
        self.work = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.work)

    def rewrite(self, body, definitions):
        source, target = self.work / "in.docx", self.work / "out.docx"
        docx(source, body, definitions)
        self.assertEqual(LIST.main(["list-numbers.py", str(source), str(target)]), 0)
        return target

    def items(self, body, definitions):
        return [(t, lvl, n) for t, lvl, n in drawn(self.rewrite(body, definitions))
                if n is not None]


class RewriteTest(Rewriting):
    def test_instances_on_one_definition_share_a_count(self):
        definitions = [abstract(8, level(0)), num(13, 8, [(0, 1)]), num(8, 8)]
        body = [para("first", 13), para("second", 8), para("third", 8)]
        self.assertEqual(self.items(body, definitions),
                         [("first", 0, 1), ("second", 0, 2), ("third", 0, 3)])

    def test_start_override_applies_on_first_use_only(self):
        definitions = [abstract(1, level(0)), num(3, 1, [(0, 5)]), num(4, 1)]
        body = [para("a", 3), para("b", 3), para("c", 4)]
        self.assertEqual([n for _, _, n in self.items(body, definitions)], [5, 6, 7])

    def test_a_deeper_first_item_counts_the_level_above_once(self):
        definitions = [
            abstract(2, level(0, left=720)),
            abstract(1, level(0, left=720), level(1, left=1440), level(2, left=1800)),
            num(5, 2), num(23, 1),
        ]
        body = [para("rule a", 5), para("rule b", 5), para("grid one", 23, 2),
                para("grid two", 23, 2), para("rule c", 23, 0)]
        self.assertEqual(self.items(body, definitions), [
            ("rule a", 0, 1), ("rule b", 0, 2),
            ("grid one", 1, 1), ("grid two", 1, 2),
            ("rule c", 0, 2),
        ])

    def test_another_definition_indented_under_an_item_nests(self):
        definitions = [
            abstract(1, level(0, left=720)),
            abstract(2, level(0, fmt="lowerRoman", text="%1.", left=1620)),
            num(1, 1), num(2, 2),
        ]
        body = [para("one", 1), para("two", 1), para("sub i", 2), para("sub ii", 2),
                para("three", 1)]
        self.assertEqual(self.items(body, definitions), [
            ("one", 0, 1), ("two", 0, 2), ("sub i", 1, 1), ("sub ii", 1, 2), ("three", 0, 3),
        ])

    def test_another_definition_at_the_same_indent_is_a_sibling_list(self):
        definitions = [
            abstract(1, level(0, left=720)), abstract(2, level(0, left=720)),
            num(1, 1), num(2, 2),
        ]
        body = [para("one", 1), para("two", 1), para("other", 2)]
        self.assertEqual(self.items(body, definitions)[-1], ("other", 0, 1))

    def test_an_indented_paragraph_continues_the_item_above(self):
        definitions = [abstract(1, level(0, left=720)), num(1, 1)]
        body = [para("one", 1), para("more about one", left=720), para("two", 1)]
        self.assertEqual(drawn(self.rewrite(body, definitions)), [
            ("one", 0, 1), ("more about one", None, "continues"), ("two", 0, 2),
        ])

    def test_text_at_the_margin_ends_the_nesting(self):
        definitions = [
            abstract(1, level(0, left=720)), abstract(2, level(0, left=1440)),
            num(1, 1), num(2, 2),
        ]
        body = [para("one", 1), para("A paragraph at the margin."), para("indented", 2)]
        self.assertEqual(drawn(self.rewrite(body, definitions))[1:], [
            ("A paragraph at the margin.", None, None), ("indented", 0, 1),
        ])

    def test_level_restart_zero_keeps_counting_across_shallower_items(self):
        definitions = [
            abstract(1, level(0, left=720), level(1, left=1440, restart=0)), num(1, 1),
        ]
        body = [para("top", 1, 0), para("x", 1, 1), para("y", 1, 1), para("next", 1, 0),
                para("z", 1, 1)]
        self.assertEqual(self.items(body, definitions)[-1], ("z", 1, 3))

    def test_text_after_an_unindented_list_stays_at_the_margin(self):
        definitions = [abstract(1, level(0)), num(1, 1)]
        body = [para("step one", 1), para("step two", 1), para("Body text.", left=0),
                para("More body text.", style="Normal")]
        self.assertEqual(drawn(self.rewrite(body, definitions))[2:], [
            ("Body text.", None, None), ("More body text.", None, None),
        ])

    def test_a_heading_ends_the_list(self):
        definitions = [abstract(1, level(0, left=720)), num(1, 1)]
        body = [para("one", 1), para("Next part", style="Heading1"),
                para("indented after the heading", left=720)]
        self.assertEqual(drawn(self.rewrite(body, definitions))[1:], [
            ("Next part", None, None), ("indented after the heading", None, None),
        ])

    def test_tables_and_headings_are_left_as_they_are(self):
        definitions = [abstract(1, level(0, left=720)), num(1, 1)]
        body = [para("Heading", 1, style="Heading1"), table(para("cell", 1)), para("after", 1)]
        out = self.rewrite(body, definitions)
        with zipfile.ZipFile(out) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
        ids = [p.find(f"{W}pPr/{W}numPr/{W}numId").get(W + "val") for p in document.iter(W + "p")]
        self.assertEqual(ids[:2], ["1", "1"])
        self.assertEqual(drawn(out)[-1], ("after", 0, 3))

    def test_a_file_without_numbering_is_copied(self):
        source, target = self.work / "in.docx", self.work / "out.docx"
        docx(source, [para("plain")])
        self.assertEqual(LIST.main(["list-numbers.py", str(source), str(target)]), 0)
        self.assertEqual(source.read_bytes(), target.read_bytes())

    def test_a_file_that_is_not_a_zip_fails(self):
        source = self.work / "in.rtf"
        source.write_text("{\\rtf1 plain}")
        self.assertEqual(LIST.main(["list-numbers.py", str(source), str(self.work / "o")]), 1)


@unittest.skipUnless(shutil.which("pandoc"), "pandoc is not installed")
class PandocTest(Rewriting):
    def markdown(self, body, definitions):
        target = self.rewrite(body, definitions)
        return subprocess.run(["pandoc", "-f", "docx", "-t", "gfm", str(target)],
                              capture_output=True, text=True, check=True).stdout

    def test_pandoc_draws_the_word_numbers(self):
        definitions = [
            abstract(2, level(0, left=720)),
            abstract(1, level(0, left=720), level(1, left=1440), level(2, left=1800)),
            abstract(8, level(0, fmt="lowerRoman", text="%1.", left=1620)),
            num(5, 2), num(23, 1), num(13, 8),
        ]
        body = [para("rule a", 5), para("rule b", 5), para("grid i", 13), para("grid ii", 13),
                para("more", left=720), para("sub", 23, 2), para("rule c", 23, 0)]
        lines = [line for line in self.markdown(body, definitions).splitlines()
                 if line.strip() not in ("", "&nbsp;", "<!-- -->")]
        # Pandoc joins a continuing paragraph to the last item it read, the
        # deepest one open, so the text stays in the list and in order.
        self.assertEqual(lines, [
            "1.  rule a", "2.  rule b", "    1.  grid i", "    2.  grid ii",
            "        more", "    1.  sub", "2.  rule c",
        ])


if __name__ == "__main__":
    unittest.main()
