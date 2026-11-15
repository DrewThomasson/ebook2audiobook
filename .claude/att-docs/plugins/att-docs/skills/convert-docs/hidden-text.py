#!/usr/bin/env python3
"""Removes the runs Word hides from a Word file, so Pandoc never reads them.

Word's hidden text is a run whose run properties set `w:vanish`. Word does not
print it, and Pandoc's docx reader writes it as ordinary text. Help files keep
jump and bookmark names that way, glued to the visible label after them, and
templates leave a hidden paragraph such as `Exi` between tables.

A run is hidden when its own properties set `w:vanish` on, and shown when
they set it off. When they say nothing about it, the styles decide: the
character style and the paragraph's style each resolve through the styles they
are based on, and since `w:vanish` is a toggle property, a style that turns it
on cancels the other when both do. When neither style says, the document
defaults decide. `w:val` of `0`, `false` or `off` turns it off. `w:specVanish`
and `w:webHidden` are left alone.

A run that holds a field character or a field instruction stays even when
hidden, since Word still reads a field whose code is hidden.

The body, the footnotes and the endnotes are rewritten. A paragraph left with
no visible text has nothing for Pandoc to write.

Usage:
  hidden-text.py IN OUT

Writes OUT and exits 0. Exits 1 when IN is not a zip archive or a part of it
is not well-formed XML.
"""
from __future__ import annotations

import io
import sys
import xml.etree.ElementTree as ET
import zipfile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

PARTS = ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml")
OFF = ("0", "false", "off")


def keep_prefixes(raw: bytes) -> None:
    # ElementTree writes ns0:, ns1: for every prefix it was not told about.
    for _, (prefix, uri) in ET.iterparse(io.BytesIO(raw), events=("start-ns",)):
        try:
            ET.register_namespace(prefix, uri)
        except ValueError:
            pass


def vanish(rpr) -> bool | None:
    """On, off, or None when the properties do not say."""
    flag = None if rpr is None else rpr.find(W + "vanish")
    if flag is None:
        return None
    return (flag.get(W + "val") or "true").lower() not in OFF


class Styles:
    def __init__(self, root):
        self.by_id = {}
        for style in [] if root is None else root.findall(W + "style"):
            self.by_id[style.get(W + "styleId")] = style
        defaults = None if root is None else root.find(f"{W}docDefaults/{W}rPrDefault/{W}rPr")
        self.default = bool(vanish(defaults))

    def run_hidden(self, char_style, para_style) -> bool:
        """What the styles and the defaults say for a run that says nothing itself."""
        found = [value for value in (self.hidden(char_style), self.hidden(para_style))
                 if value is not None]
        if not found:
            return self.default
        # A toggle property: each style level that turns it on flips it.
        return sum(found) % 2 == 1

    def hidden(self, style_id) -> bool | None:
        seen = set()
        while style_id in self.by_id and style_id not in seen:
            seen.add(style_id)
            style = self.by_id[style_id]
            found = vanish(style.find(W + "rPr"))
            if found is not None:
                return found
            based = style.find(W + "basedOn")
            style_id = None if based is None else based.get(W + "val")
        return None


def style_of(properties, tag):
    element = None if properties is None else properties.find(W + tag)
    return None if element is None else element.get(W + "val")


def drop_hidden(root, styles: Styles) -> int:
    """Removes every hidden run under root and returns how many went."""
    parents = {child: parent for parent in root.iter() for child in parent}
    dropped = 0
    for run in list(root.iter(W + "r")):
        if run.find(W + "fldChar") is not None or run.find(W + "instrText") is not None:
            continue
        rpr = run.find(W + "rPr")
        hidden = vanish(rpr)
        if hidden is None:
            # The paragraph the run sits in, the nearest one when a text box
            # puts a paragraph inside another.
            paragraph = parents.get(run)
            while paragraph is not None and paragraph.tag != W + "p":
                paragraph = parents.get(paragraph)
            para_style = None if paragraph is None else style_of(
                paragraph.find(W + "pPr"), "pStyle")
            hidden = styles.run_hidden(style_of(rpr, "rStyle"), para_style)
        if hidden:
            parents[run].remove(run)
            dropped += 1
    return dropped


def rewrite(source, target) -> int:
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        parts = {info.filename: archive.read(info) for info in infos}
    for name in PARTS + ("word/styles.xml",):
        if name in parts:
            keep_prefixes(parts[name])
    styles = Styles(ET.fromstring(parts["word/styles.xml"]) if "word/styles.xml" in parts else None)
    dropped = 0
    for name in PARTS:
        if name not in parts:
            continue
        root = ET.fromstring(parts[name])
        count = drop_hidden(root, styles)
        if count:
            dropped += count
            parts[name] = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for info in infos:
            out.writestr(info, parts[info.filename])
    return dropped


def main(argv):
    if len(argv) != 3:
        sys.stderr.write(__doc__)
        return 64
    try:
        rewrite(argv[1], argv[2])
    except (zipfile.BadZipFile, ET.ParseError, KeyError) as error:
        print(f"hidden-text: {argv[1]}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
