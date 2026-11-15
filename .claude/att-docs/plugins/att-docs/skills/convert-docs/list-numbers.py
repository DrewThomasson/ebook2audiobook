#!/usr/bin/env python3
"""Rewrites a Word file's list numbering so Pandoc draws the numbers Word draws.

Pandoc's docx reader and Word count a list differently, and the difference
reaches the Markdown as a renumbered item or a sub-list at the left margin:

- Word keeps one count per abstract numbering definition, so two numbering
  instances built on the same definition share it. Pandoc keeps one per
  instance, so the second instance starts again at its own start value.
- Word counts an item at a deeper level as though every shallower level above
  it had been used once, so an instance whose first item sits at level three
  draws `2.` on its first level-one item. Pandoc starts that item at 1.
- Word nests a list by where it is drawn: a list of another definition,
  indented past the text of the item above it, reads as that item's sub-list.
  Pandoc nests by level alone, so it lands at the margin. An indented paragraph
  with no number between two items is part of the item above in Word, and a
  block quote that ends the list in Pandoc.

The rewrite walks the body in order, works out the number Word draws on each
numbered paragraph and how deep it sits on the page, and gives the paragraph a
numbering instance of its own making at a level equal to that depth. Each new
instance starts at the number Word draws, and an item keeps the instance
before it only when Pandoc's own count lands on the same number. An indented
paragraph inside a list is given an instance whose definition has no levels,
which is how Pandoc's reader marks a paragraph that continues the item above.

Paragraphs in tables, headings, and levels drawn without a number are counted,
since Word counts them, but left as they are: the table filter flattens a
cell's list to text, and a heading's number is not written to the Markdown.

Usage:
  list-numbers.py IN OUT

Writes OUT and exits 0. A file with no numbering part, such as an OpenDocument
file, is copied as it is. Exits 1 when IN is not a zip archive or a part of it
is not well-formed XML.
"""
from __future__ import annotations

import copy
import io
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

LEVELS = 9

# How far left of the text of the item above, in twentieths of a point, a
# list's number may sit and still read as that item's sub-list. Word steps its
# indents by a quarter or a half inch, 360 or 720, so a sixteenth of an inch is
# the same column drawn by two templates.
NEST_TOLERANCE = 90

# Word's default tab stops, every half inch, in twentieths of a point.
DEFAULT_TAB = 720


def val(element, name="val"):
    return None if element is None else element.get(W + name)


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def keep_prefixes(raw: bytes) -> None:
    # ElementTree writes ns0:, ns1: for every prefix it was not told about.
    # Pandoc reads either, but the rewritten part stays comparable with the
    # original when the names are kept.
    for _, (prefix, uri) in ET.iterparse(io.BytesIO(raw), events=("start-ns",)):
        try:
            ET.register_namespace(prefix, uri)
        except ValueError:
            pass


class Indent:
    """The left edge of a paragraph's text and its hanging indent."""

    def __init__(self, left=None, hanging=None):
        self.left = left
        self.hanging = hanging

    @staticmethod
    def of(ppr):
        ind = None if ppr is None else ppr.find(W + "ind")
        if ind is None:
            return Indent()
        left = val(ind, "left") or val(ind, "start")
        hanging = val(ind, "hanging")
        first = val(ind, "firstLine")
        if hanging is None and first is not None:
            hanging = -to_int(first)
        return Indent(
            None if left is None else to_int(left),
            None if hanging is None else to_int(hanging),
        )

    def over(self, other):
        return Indent(
            other.left if self.left is None else self.left,
            other.hanging if self.hanging is None else self.hanging,
        )


class Styles:
    def __init__(self, root):
        self.by_id = {}
        for style in [] if root is None else root.findall(W + "style"):
            self.by_id[val(style, "styleId")] = style

    def chain(self, style_id):
        seen = set()
        while style_id in self.by_id and style_id not in seen:
            seen.add(style_id)
            style = self.by_id[style_id]
            yield style
            style_id = val(style.find(W + "basedOn"))

    def numbering(self, style_id):
        """The (numId, ilvl) a paragraph style numbers its paragraphs with."""
        for style in self.chain(style_id):
            num_pr = style.find(W + "pPr/" + W + "numPr")
            if num_pr is not None and val(num_pr.find(W + "numId")) is not None:
                return val(num_pr.find(W + "numId")), val(num_pr.find(W + "ilvl"))
        return None

    def indent(self, style_id):
        result = Indent()
        for style in self.chain(style_id):
            result = result.over(Indent.of(style.find(W + "pPr")))
        return result

    def is_heading(self, style_id):
        for style in self.chain(style_id):
            name = (val(style.find(W + "name")) or "").lower()
            if name.startswith("heading") or name == "title":
                return True
        return False


class Numbering:
    def __init__(self, root, styles):
        self.root = root
        self.styles = styles
        self.abstracts = {val(a, "abstractNumId"): a for a in root.findall(W + "abstractNum")}
        self.nums = {val(n, "numId"): n for n in root.findall(W + "num")}

    def abstract(self, num_id):
        """The definition an instance counts with, following a numbering style
        link to the definition that holds the levels."""
        num = self.nums.get(num_id)
        abstract_id = val(num.find(W + "abstractNumId")) if num is not None else None
        for _ in range(LEVELS):
            abstract = self.abstracts.get(abstract_id)
            link = val(abstract.find(W + "numStyleLink")) if abstract is not None else None
            target = self.styles.numbering(link) if link else None
            linked = self.nums.get(target[0]) if target else None
            if linked is None:
                break
            abstract_id = val(linked.find(W + "abstractNumId"))
        return abstract_id, self.abstracts.get(abstract_id)

    def override(self, num_id, ilvl):
        num = self.nums.get(num_id)
        for override in [] if num is None else num.findall(W + "lvlOverride"):
            if to_int(val(override, "ilvl")) == ilvl:
                return override
        return None

    def level(self, num_id, ilvl):
        override = self.override(num_id, ilvl)
        if override is not None and override.find(W + "lvl") is not None:
            return override.find(W + "lvl")
        _, abstract = self.abstract(num_id)
        for lvl in [] if abstract is None else abstract.findall(W + "lvl"):
            if to_int(val(lvl, "ilvl")) == ilvl:
                return lvl
        return None

    def start_override(self, num_id, ilvl):
        override = self.override(num_id, ilvl)
        start = None if override is None else override.find(W + "startOverride")
        return None if start is None else to_int(val(start), 1)


def level_start(lvl):
    return 1 if lvl is None else to_int(val(lvl.find(W + "start")), 1)


def level_format(lvl):
    return "decimal" if lvl is None else (val(lvl.find(W + "numFmt")) or "decimal")


def restarts_after(lvl, used):
    """Whether using the level numbered `used`, counting from 1, restarts this
    level's count. A level restarts after any shallower level unless lvlRestart
    names the deepest one that restarts it, and 0 means never."""
    restart = None if lvl is None else val(lvl.find(W + "lvlRestart"))
    if restart is None:
        return True
    restart = to_int(restart, LEVELS)
    return restart != 0 and used <= restart


class WordCount:
    """The numbers Word draws: one count per definition, with each instance's
    start override applied the first time that instance is used."""

    def __init__(self, numbering):
        self.numbering = numbering
        self.counts = {}
        self.overridden = set()

    def next(self, num_id, ilvl):
        abstract_id, _ = self.numbering.abstract(num_id)
        counts = self.counts.setdefault(abstract_id, [None] * LEVELS)
        override = self.numbering.start_override(num_id, ilvl)
        if override is not None and (num_id, ilvl) not in self.overridden:
            self.overridden.add((num_id, ilvl))
            counts[ilvl] = override - 1
        for shallower in range(ilvl):
            if counts[shallower] is None:
                counts[shallower] = level_start(self.numbering.level(num_id, shallower))
        if counts[ilvl] is None:
            counts[ilvl] = level_start(self.numbering.level(num_id, ilvl)) - 1
        counts[ilvl] += 1
        for deeper in range(ilvl + 1, LEVELS):
            if restarts_after(self.numbering.level(num_id, deeper), ilvl + 1):
                counts[deeper] = None
        return counts[ilvl]


class Open:
    """An item on the page whose sub-lists are still open."""

    def __init__(self, abstract_id, ilvl, text_pos, depth):
        self.abstract_id = abstract_id
        self.ilvl = ilvl
        self.text_pos = text_pos
        self.depth = depth

    def holds(self, abstract_id, ilvl, number_pos):
        if abstract_id == self.abstract_id:
            return ilvl > self.ilvl
        return number_pos >= self.text_pos - NEST_TOLERANCE


def has_text(paragraph):
    return any((t.text or "").strip() for t in paragraph.iter(W + "t"))


class Rewriter:
    def __init__(self, numbering, styles):
        self.numbering = numbering
        self.styles = styles
        self.word = WordCount(numbering)
        self.open = []
        # Pandoc's count, kept the way its reader keeps it: by instance and
        # level, forgetting every deeper level whenever it reads an item.
        self.pandoc = {}
        # The instance last used at each depth: (numId, format and level text,
        # the number it starts at).
        self.current = {}
        self.continuation_id = None
        self.next_abstract = 1 + max([to_int(k) for k in numbering.abstracts] or [0])
        self.next_num = 1 + max([to_int(k) for k in numbering.nums] or [0])

    def walk(self, parent, in_table=False):
        for child in parent:
            if child.tag == W + "p":
                self.paragraph(child, in_table)
            elif child.tag == W + "tbl":
                if not in_table:
                    self.open.clear()
                self.walk(child, True)
            elif child.tag != W + "sectPr":
                self.walk(child, in_table)

    def numbering_of(self, ppr, style_id):
        num_pr = None if ppr is None else ppr.find(W + "numPr")
        num_id = None if num_pr is None else val(num_pr.find(W + "numId"))
        ilvl = None if num_pr is None else val(num_pr.find(W + "ilvl"))
        from_style = self.styles.numbering(style_id)
        if from_style:
            num_id = from_style[0] if num_id is None else num_id
            ilvl = from_style[1] if ilvl is None else ilvl
        if num_id not in self.numbering.nums:
            return None
        return num_id, min(max(to_int(ilvl), 0), LEVELS - 1)

    def positions(self, ppr, style_id, lvl=None):
        """Where a paragraph's number and its text start. The paragraph's own
        indent wins over its numbering level's, which wins over its style's."""
        from_level = Indent.of(None if lvl is None else lvl.find(W + "pPr"))
        indent = Indent.of(ppr).over(from_level).over(self.styles.indent(style_id))
        left = indent.left or 0
        return left - (indent.hanging or 0), left

    def paragraph(self, paragraph, in_table):
        ppr = paragraph.find(W + "pPr")
        style_id = val(ppr.find(W + "pStyle")) if ppr is not None else None
        found = self.numbering_of(ppr, style_id)
        if found is None:
            if not in_table and has_text(paragraph):
                self.text(paragraph, ppr, style_id)
            return
        num_id, ilvl = found
        number = self.word.next(num_id, ilvl)
        lvl = self.numbering.level(num_id, ilvl)
        fmt = level_format(lvl)
        if in_table or fmt == "none" or self.styles.is_heading(style_id):
            # Pandoc still reads these as numbered, and forgets its deeper
            # counts on each one.
            self.forget_below(ilvl)
            if not in_table and fmt != "none":
                self.open.clear()
            return
        abstract_id, _ = self.numbering.abstract(num_id)
        number_pos, text_pos = self.positions(ppr, style_id, lvl)
        if text_pos <= number_pos:
            # With no hanging indent, Word sets the text at the next default
            # tab stop after the number.
            text_pos = (max(number_pos, 0) // DEFAULT_TAB + 1) * DEFAULT_TAB
        while self.open and not self.open[-1].holds(abstract_id, ilvl, number_pos):
            self.open.pop()
        depth = len(self.open)
        self.open.append(Open(abstract_id, ilvl, text_pos, depth))
        self.number(ppr, lvl, fmt, number, depth)

    def text(self, paragraph, ppr, style_id):
        if self.styles.is_heading(style_id):
            self.open.clear()
            return
        _, left = self.positions(ppr, style_id)
        while self.open and left < self.open[-1].text_pos - NEST_TOLERANCE:
            self.open.pop()
        if self.open:
            if ppr is None:
                ppr = ET.Element(W + "pPr")
                paragraph.insert(0, ppr)
            set_numbering(ppr, self.continuation(), self.open[-1].depth)

    def number(self, ppr, lvl, fmt, number, depth):
        text = val(lvl.find(W + "lvlText")) if lvl is not None else None
        kind = (fmt, None if fmt == "bullet" else text)
        current = self.current.get(depth)
        reuse = current is not None and current[1] == kind
        if reuse and fmt != "bullet":
            last = self.pandoc.get((current[0], depth))
            reuse = (current[2] if last is None else last + 1) == number
        if reuse:
            num_id = current[0]
        else:
            num_id = self.instance(lvl, fmt, text, number, depth)
            self.current[depth] = (num_id, kind, number)
        self.forget_below(depth)
        self.pandoc[(num_id, depth)] = number
        set_numbering(ppr, num_id, depth)

    def forget_below(self, ilvl):
        self.pandoc = {key: n for key, n in self.pandoc.items() if key[1] <= ilvl}

    def instance(self, lvl, fmt, text, number, depth):
        abstract = ET.Element(W + "abstractNum")
        new = ET.SubElement(abstract, W + "lvl")
        new.set(W + "ilvl", str(depth))
        ET.SubElement(new, W + "start").set(W + "val", str(number))
        ET.SubElement(new, W + "numFmt").set(W + "val", fmt)
        ET.SubElement(new, W + "lvlText").set(W + "val", text or "%1.")
        if lvl is not None and lvl.find(W + "pPr") is not None:
            new.append(copy.deepcopy(lvl.find(W + "pPr")))
        return self.define(abstract)

    def continuation(self):
        if self.continuation_id is None:
            self.continuation_id = self.define(ET.Element(W + "abstractNum"))
        return self.continuation_id

    def define(self, abstract):
        root = self.numbering.root
        abstract_id, num_id = str(self.next_abstract), str(self.next_num)
        self.next_abstract += 1
        self.next_num += 1
        abstract.set(W + "abstractNumId", abstract_id)
        # Every definition comes ahead of every instance in the part.
        existing = root.findall(W + "abstractNum")
        root.insert(list(root).index(existing[-1]) + 1 if existing else 0, abstract)
        num = ET.SubElement(root, W + "num")
        num.set(W + "numId", num_id)
        ET.SubElement(num, W + "abstractNumId").set(W + "val", abstract_id)
        return num_id


def set_numbering(ppr, num_id, ilvl):
    num_pr = ppr.find(W + "numPr")
    if num_pr is None:
        num_pr = ET.SubElement(ppr, W + "numPr")
    for child in list(num_pr):
        if child.tag in (W + "ilvl", W + "numId"):
            num_pr.remove(child)
    ET.SubElement(num_pr, W + "ilvl").set(W + "val", str(ilvl))
    ET.SubElement(num_pr, W + "numId").set(W + "val", num_id)


def rewrite(source, target):
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        parts = {info.filename: archive.read(info) for info in infos}
    if "word/document.xml" not in parts or "word/numbering.xml" not in parts:
        shutil.copyfile(source, target)
        return
    for name in ("word/document.xml", "word/numbering.xml", "word/styles.xml"):
        if name in parts:
            keep_prefixes(parts[name])
    document = ET.fromstring(parts["word/document.xml"])
    numbering = ET.fromstring(parts["word/numbering.xml"])
    styles = Styles(ET.fromstring(parts["word/styles.xml"]) if "word/styles.xml" in parts else None)
    body = document.find(W + "body")
    if body is not None:
        Rewriter(Numbering(numbering, styles), styles).walk(body)
    parts["word/document.xml"] = ET.tostring(document, encoding="UTF-8", xml_declaration=True)
    parts["word/numbering.xml"] = ET.tostring(numbering, encoding="UTF-8", xml_declaration=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for info in infos:
            out.writestr(info, parts[info.filename])


def main(argv):
    if len(argv) != 3:
        sys.stderr.write(__doc__)
        return 64
    try:
        rewrite(argv[1], argv[2])
    except (zipfile.BadZipFile, ET.ParseError) as error:
        print(f"list-numbers: {argv[1]}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
