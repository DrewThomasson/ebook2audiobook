#!/usr/bin/env python3
"""Cleans one converted Markdown file and stamps its provenance block.

Reads the Markdown that Pandoc produced plus the source documents it came from,
and writes the finished file. Standard library only: this box has no pip, no
openpyxl and no pandas, so the container formats are read as the zip archives
they are and the PDF properties come from pdftotext's sibling, pdfinfo.

Three jobs, in order. The cleanup pass takes Pandoc's output down to plain
Markdown: heading attributes, images, control characters and the escapes that
render as an em dash all come out, and the document's own headings shift down a
level so the title can occupy the single H1. The provenance pass then walks the
ladder for a revision date and a version, and labels each value with the rung it
came from, so a reader can tell a date the document stated from one the file
system remembers. It also links each source to its document in the SharePoint
library when the library path is known. The page pass, in pages.py, marks where
each page of the original starts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import convert_config  # noqa: E402  the --config reader beside this script
import pages  # noqa: E402  the page layout reader beside this script
from doc_paths import hyphenated  # noqa: E402

# Formats SharePoint downloads unless asked to open them in the browser, which
# `web=1` does. A PDF opens in the browser either way, and keeps the `#page=` its
# page links carry.
OFFICE_SUFFIXES = {
    ".doc", ".docx", ".docm", ".dot", ".xls", ".xlsx", ".xlsm",
    ".ppt", ".pptx", ".pptm",
}

# Container formats that are zip archives holding an OPC properties part.
OPC_SUFFIXES = {".docx", ".docm", ".xlsx", ".xlsm", ".pptx", ".pptm"}

# Pandoc hangs its own identifier and the source document's Word style name off
# every heading it writes, as `# Page Name {#page-name .Style1}`. Neither means
# anything once the document is Markdown.
HEADING_ATTRS = re.compile(r"[ \t]*\{[^{}\n]*\}[ \t]*$")

HEADING = re.compile(r"^(#{1,6})(\s+)(.*)$")

# Pandoc writes an empty span where Word had a bookmark, as `[]{#anchor}`.
EMPTY_ANCHOR = re.compile(r"\[\]\{[^{}\n]*\}")

# A span carrying a Word character style, as `[BCA to Connections]{.underline}`.
# The styling is gone either way once this is Markdown, so the text comes out of
# the wrapper rather than out of the document.
STYLED_SPAN = re.compile(r"\[([^\[\]\n]*)\]\{[^{}\n]*\}")

# LibreOffice fills an empty spreadsheet cell with a lone backslash, which is a
# Markdown line break rather than a value.
EMPTY_CELL = re.compile(r"(?<=\|)(\s*)\\(\s*)(?=\|)")

# A non-breaking space that arrived as its entity name rather than as a
# character, which is how the HTML routes spell an empty paragraph.
HTML_ENTITY = re.compile(r"&nbsp;|&#160;|&#xa0;", re.IGNORECASE)

# The bullet glyph a slide draws at the head of its own list item, left over
# once the item is a Markdown list item that draws its own. A letter `o` is a
# glyph only when it stands alone; otherwise it opens a word such as "open".
LIST_BULLET_GLYPH = re.compile(
    r"^(\s*(?:[-*+]|\d+\.)\s+)(?:[•·▪◦§]\s*|o(?:[ \t]+|$))", re.MULTILINE)

IMAGE_MD = re.compile(r"!\[[^\]]*\]\([^)]*\)")
IMAGE_HTML = re.compile(r"<img\b[^>]*/?>", re.IGNORECASE)

# Everything below the space except tab and newline, plus the BOM wherever it
# landed.
CONTROL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f﻿]")

BLANK_RUN = re.compile(r"\n{3,}")

DATE_PATTERNS = [
    # 7/11/2017 and 07-11-2017, month first, which is how these documents date.
    (re.compile(r"(?<!\d)(\d{1,2})[/-](\d{1,2})[/-](\d{4})(?!\d)"), "mdy"),
    # 2017-07-11, and the leading date of an ISO timestamp. The day is closed
    # with a digit guard rather than a word boundary, which `2025-05-28T16:19`
    # would defeat: the day and the `T` are both word characters, so there is no
    # boundary between them.
    (re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)"), "ymd"),
    # July 11, 2017 and Jul 11 2017.
    (
        re.compile(
            r"\b(January|February|March|April|May|June|July|August|September"
            r"|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep"
            r"|Oct|Nov|Dec)\.?\s+(\d{1,2}),?\s+(\d{4})\b",
            re.IGNORECASE,
        ),
        "mname",
    ),
]

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

# The heading that opens a revision history table, however the author spelled it.
REVISION_HEADING = re.compile(
    r"^#{1,6}\s*\**\s*(document\s+)?(revision|version|change|document)\s*"
    r"(history|log)\b",
    re.IGNORECASE,
)

# A stated update line has to own its line and carry a date. Anchoring it this
# way is what keeps it off `DtLastUpdate`, a field name that appears inside the
# data dictionary tables of the DX documents and is not a date at all.
#
# The separator is optional because these footers use every form of it: a colon
# in `Last saved on: 6/16/2010`, an en dash in `Last Updated - 09/29/2023`, a
# full stop in `Rev. 5/6/2019`, and nothing at all in `Last Updated 09/29/2023`.
STATED_UPDATE = re.compile(
    r"^[>\s*_]*\**\s*(last\s+updat(e|ed)|last\s+revis(ed|ion)|last\s+modified"
    r"|last\s+saved(\s+(on|date))?|date\s+last\s+(updated|revised|modified)"
    r"|revision\s+date|revised|rev)\b\.?\s*\**\s*[:\-\u2013\u2014]?\s*"
    r"(?P<rest>.+)$",
    re.IGNORECASE,
)

# An explicit version marker, which is the only thing a file name is allowed to
# answer with. The leading number in these file names is a screen identifier
# (`AIMS 4.1 - Action History Screen`), so it is read as one and never as a
# document version.
FILENAME_VERSION = re.compile(
    r"(?:^|[\s_\-(])(?:v|ver|version|rev|revision|draft)\.?\s*"
    r"(?P<num>\d+(?:\.\d+)*)\b",
    re.IGNORECASE,
)

# The screen or section identifier these documents lead with, after any suite
# acronym: `AIMS 4.1 - ...`, `CCA 09.2 ...`, `UPL - 5.0 - ...`, `07.3 - MR ...`.
FILENAME_SCREEN = re.compile(
    r"^\s*(?:[A-Z][A-Za-z]{1,9}(?:-[A-Z][A-Za-z]{1,9})?\s*-?\s*)?"
    r"(?P<num>\d{1,2}(?:\.\d{1,2})+)\s*[-\s]"
)

# A tracker comment, as the paste out of one carries it: a name, the author's
# logon in angle brackets, the date, and the text after a colon. A file holding
# such a thread is a transport for something written somewhere else, so the
# thread's last date is what the record was last touched.
TRACKER_COMMENT = re.compile(
    r"^[>\s*_]*[^<>\n]{2,60}<[^<>\s]{2,20}>\s*,\s*(?P<rest>.+)$",
)

NOT_STATED = "not stated"


@dataclass
class Found:
    """One provenance value together with the rung of the ladder it came from."""

    value: str
    source: str

    def render(self) -> str:
        return f"{self.value}, {self.source}"


def iso(year: int, month: int, day: int) -> str | None:
    try:
        return dt.date(year, month, day).isoformat()
    except ValueError:
        return None


def find_date(text: str) -> str | None:
    """Returns the first date in `text` as an ISO day, or None."""
    for pattern, kind in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        if kind == "mdy":
            return iso(int(match.group(3)), int(match.group(1)), int(match.group(2)))
        if kind == "ymd":
            return iso(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        name = match.group(1).lower().rstrip(".")
        month = MONTHS.get(name[:4]) or MONTHS.get(name[:3])
        if month is not None:
            return iso(int(match.group(3)), month, int(match.group(2)))
    return None


def clean(markdown: str) -> str:
    """Takes Pandoc's output down to plain Markdown with one H1 free."""
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    text = CONTROL.sub("", text)
    text = text.replace(" ", " ")
    text = IMAGE_MD.sub("", text)
    text = IMAGE_HTML.sub("", text)
    text = EMPTY_ANCHOR.sub("", text)
    text = STYLED_SPAN.sub(r"\1", text)
    text = EMPTY_CELL.sub(r"\1 \2", text)
    text = HTML_ENTITY.sub(" ", text)
    text = LIST_BULLET_GLYPH.sub(r"\1", text)

    # The em dash is barred from this repository wherever it lands, including in
    # text quoted out of a source document. Pandoc's Markdown writer spells it
    # `---` rather than as the character, so both forms come out. The en dash it
    # writes as `--` is a different character and stays.
    text = text.replace("\u2014", "-")
    text = re.sub(r"(?<!-)---(?!-)", "-", text)

    lines = []
    for line in text.split("\n"):
        match = HEADING.match(line)
        if match:
            body = HEADING_ATTRS.sub("", match.group(3)).rstrip()
            # Shift every heading down one level so the title owns the only H1.
            # A heading already at H6 has nowhere to go and stays put.
            level = match.group(1)
            if len(level) < 6:
                level = "#" + level
            line = f"{level} {body}".rstrip()
        lines.append(line.rstrip())
    text = "\n".join(lines)

    text = BLANK_RUN.sub("\n\n", text)
    return text.strip() + "\n"


def rows_of_table(lines: list[str], start: int) -> list[list[str]]:
    """Reads the grid or pipe table beginning at or below `start`.

    In a pipe table every line is a whole row. In a grid table one row wraps
    over as many lines as its widest cell needs, and a rule of pluses and dashes
    closes it, so the cells accumulate until that rule arrives. Seeing such a
    rule is what tells the two apart.
    """
    rows: list[list[str]] = []
    current: list[str] = []
    seen_table = False
    grid = False
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("+") and set(stripped) <= set("+-=: "):
            seen_table = True
            grid = True
            if current:
                rows.append(current)
                current = []
            continue
        if stripped.startswith("|"):
            seen_table = True
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if set("".join(cells)) <= set("-=: "):
                continue
            if grid and current and len(cells) == len(current):
                current = [(a + " " + b).strip() for a, b in zip(current, cells)]
            else:
                if current:
                    rows.append(current)
                current = cells
            continue
        if seen_table and not stripped:
            continue
        if seen_table:
            break
    if current:
        rows.append(current)
    return rows


def from_revision_table(markdown: str) -> tuple[Found | None, Found | None]:
    """Rung one: the last dated row of a revision history table."""
    lines = markdown.split("\n")
    label = "from the revision history table"
    for index, line in enumerate(lines):
        if not REVISION_HEADING.match(line):
            continue
        rows = rows_of_table(lines, index + 1)
        if len(rows) < 2:
            continue
        header = [cell.strip("*> ").lower() for cell in rows[0]]
        date_col = next((i for i, cell in enumerate(header) if "date" in cell), None)
        version_col = next(
            (i for i, cell in enumerate(header) if "version" in cell or cell == "#"),
            None,
        )
        date_found: Found | None = None
        version_found: Found | None = None
        for row in rows[1:]:
            if date_col is not None and date_col < len(row):
                candidate = row[date_col]
            else:
                candidate = " ".join(row)
            day = find_date(candidate)
            if not day:
                continue
            # Later rows overwrite earlier ones, so the last dated row wins.
            date_found = Found(day, label)
            version_found = None
            if version_col is not None and version_col < len(row):
                cell = row[version_col].strip("*> ")
                if cell:
                    version_found = Found(cell, label)
        if date_found:
            return date_found, version_found
    return None, None


# Word field codes that generate a date when the file is saved or opened. A
# footer built out of one of these restates the file's save date, so it is not
# something the document says about itself.
GENERATED_DATE_FIELD = re.compile(
    r"SAVEDATE|PRINTDATE|CREATEDATE|EDITTIME|\bDATE\b|\bTIME\b"
)

WORD_PARAGRAPH = re.compile(r"<w:p[ >].*?</w:p>", re.DOTALL)
WORD_TEXT = re.compile(r"<w:t[^>]*>([^<]*)</w:t>")
WORD_FIELD = re.compile(r"<w:instrText[^>]*>([^<]*)</w:instrText>")
HEADER_FOOTER_PART = re.compile(r"word/(header|footer)\d*\.xml")


def header_footer_lines(path: Path) -> list[str]:
    """Every literal line of text in a Word document's headers and footers.

    Pandoc drops these parts, and 57 of the 85 modern-format sources put a date
    in one of them. The runs of a paragraph are joined with nothing between
    them, because Word routinely splits a date mid-number: the DX footers store
    `0` and `9/29/2023` as two runs of one date.
    """
    lines: list[str] = []
    try:
        archive = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile):
        return lines
    with archive:
        for name in archive.namelist():
            if not HEADER_FOOTER_PART.fullmatch(name):
                continue
            try:
                part = archive.read(name).decode("utf-8", "replace")
            except (OSError, KeyError):
                continue
            for paragraph in WORD_PARAGRAPH.findall(part):
                if GENERATED_DATE_FIELD.search(" ".join(WORD_FIELD.findall(paragraph))):
                    continue
                text = "".join(WORD_TEXT.findall(paragraph)).strip()
                if text:
                    lines.append(text)
    return lines


def from_comment_thread(lines: list[str]) -> Found | None:
    """The last dated comment in a tracker thread the document carries.

    Only read for a document whose origin is stated rather than found, because
    a comment is a date about the record rather than about the file, and a
    file that is its own document is answered by the rungs above.
    """
    latest = None
    for line in lines:
        match = TRACKER_COMMENT.match(line.strip())
        if not match:
            continue
        day = find_date(match.group("rest"))
        if day and (latest is None or day > latest):
            latest = day
    if latest is None:
        return None
    return Found(latest, "from the last dated comment in the thread")


def from_stated_line(lines: list[str]) -> Found | None:
    """Rung two: a `Last Updated` line the document states about itself."""
    for line in lines:
        stripped = line.strip()
        # A table row is data the document tabulates, not a statement about the
        # document, so the ladder does not read one.
        if stripped.startswith(("|", "+")):
            continue
        match = STATED_UPDATE.match(stripped)
        if not match:
            continue
        day = find_date(match.group("rest"))
        if day:
            return Found(day, "from a stated update line")
    return None


def from_file_name(name: str) -> Found | None:
    """Rung three: an explicit version marker in the file name."""
    match = FILENAME_VERSION.search(name)
    return Found(match.group("num"), "from the file name") if match else None


def screen_of(name: str) -> str | None:
    """The screen or section identifier the file name leads with."""
    match = FILENAME_SCREEN.match(name)
    return match.group("num") if match else None


def opc_properties(path: Path) -> str | None:
    """Reads the last-saved date out of an OPC container.

    `cp:revision` sits beside it and looks like a version, but it is Word's
    count of how many times the file has been saved. The Copy Note document
    reads 57 there, so it is left alone.
    """
    try:
        with zipfile.ZipFile(path) as archive:
            core = archive.read("docProps/core.xml").decode("utf-8", "replace")
    except (OSError, KeyError, zipfile.BadZipFile):
        return None

    def tag(name: str) -> str | None:
        match = re.search(rf"<{name}[^>]*>([^<]*)</{name}>", core)
        return match.group(1).strip() if match and match.group(1).strip() else None

    modified = tag("dcterms:modified") or tag("dcterms:created")
    return find_date(modified) if modified else None


def pdf_properties(path: Path) -> str | None:
    """Reads ModDate out of a PDF through pdfinfo."""
    try:
        out = subprocess.run(
            ["pdfinfo", str(path)],
            capture_output=True, text=True, timeout=60, check=False,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    for line in out.split("\n"):
        if line.lower().startswith(("moddate:", "creationdate:")):
            day = find_date(line.split(":", 1)[1])
            if day:
                return day
    return None


def from_embedded(sources: list[Path]) -> Found | None:
    """Rung four: the properties the source file carries about itself.

    These record when the file was last saved, which is not the same claim as a
    date the document makes in its own text. A document written in 2009 and
    re-saved in 2025 carries 2025 here, so the label says where the value came
    from and leaves the reader to weigh it.
    """
    for source in sources:
        suffix = source.suffix.lower()
        if suffix in OPC_SUFFIXES:
            day = opc_properties(source)
        elif suffix == ".pdf":
            day = pdf_properties(source)
        else:
            continue
        if day:
            return Found(day, "from the file's embedded document properties")
    return None


def sharepoint_url(path: str, host: str) -> str:
    """The address that opens a library document.

    `path` is the document's server-relative path, as `/sites/Docs/Library/A.doc`.
    `host` is the scheme and host the library lives on, as `https://example.test`,
    with no trailing slash: the `sharePointHost` field of the extension file.
    """
    url = host + quote(path, safe="/")
    return url + "?web=1" if Path(path).suffix.lower() in OFFICE_SUFFIXES else url


def sharepoint_line(name: str, path: str, host: str) -> str:
    """The provenance line linking one source to its library document on `host`."""
    text = re.sub(r"([\[\]\\])", r"\\\1", name)
    return f"- SharePoint: [{text}]({sharepoint_url(path, host)})"


def pages_line(layout: pages.Layout, missed: list[int]) -> str:
    line = f"- Pages: {layout.pages}, {layout.label}"
    if missed:
        listed = ", ".join(str(page) for page in missed)
        noun = "page" if len(missed) == 1 else "pages"
        line += f", no marker for {noun} {listed}, whose opening text was not found"
    return line


def provenance(
    markdown: str,
    sources: list[Path],
    converted: str,
    readable: list[Path] | None = None,
    origin: str | None = None,
    library: dict[str, str] | None = None,
    sharepoint: dict[str, str] | None = None,
    paged: str | None = None,
    host: str = "",
) -> str:
    """Walks the ladder and renders the provenance block.

    `sources` are the files the block names. `readable` are the files the ladder
    may read for headers, footers and embedded properties, which is not always
    the same set: the legacy Word format is not a zip archive, so a document
    that arrived as one is read through the modern copy the conversion made of
    it. LibreOffice carries the original dates and the header and footer parts
    across, so that copy answers for the original without inventing anything.

    `library` maps a source file name to the name it carries in the document
    library, for the files renamed here because two library documents share one
    name and for the files whose library name holds spaces. The watch keys a
    converted document on the last name the Source line backticks, so that name
    has to be the library one or the library document reads as never converted.

    `sharepoint` maps a source file name to its server-relative path in the library,
    and each one found gets a line linking to it on `host`. `paged` is the rendered
    Pages line.
    """
    readable = readable or sources
    revised, version = from_revision_table(markdown)
    if revised is None and origin:
        revised = from_comment_thread(markdown.split("\n"))
    if revised is None:
        stated = markdown.split("\n")
        for source in readable:
            if source.suffix.lower() in OPC_SUFFIXES:
                stated.extend(header_footer_lines(source))
        revised = from_stated_line(stated)
    if version is None:
        version = from_file_name(sources[0].name)

    if revised is None:
        revised = from_embedded(readable)

    library = library or {}
    lines = ["**Document provenance**", ""]
    for source in sources:
        if origin:
            lines.append(f"- Source: {origin}, by way of `{source.name}`")
        elif spaced_off(source.name, library):
            lines.append(
                f"- Source: `{source.name}`, named here without spaces,"
                f" by way of `{library[source.name]}`"
            )
        elif source.name in library:
            lines.append(
                f"- Source: `{source.name}`, renamed here off a shared library"
                f" name, by way of `{library[source.name]}`"
            )
        else:
            lines.append(f"- Source: `{source.name}`")
    for source in sources:
        if source.name in (sharepoint or {}):
            name = library.get(source.name, source.name)
            lines.append(sharepoint_line(name, sharepoint[source.name], host))
    lines.append(f"- Revised: {revised.render() if revised else NOT_STATED}")
    lines.append(f"- Version: {version.render() if version else NOT_STATED}")
    screen = screen_of(sources[0].name)
    if screen:
        lines.append(f"- Screen: {screen}, from the file name")
    if paged:
        lines.append(paged)
    lines.append(f"- Converted: {converted}")
    return "\n".join(lines)


def spaced_off(name: str, library: dict[str, str]) -> bool:
    """Whether a source carries its library name with the spaces written as hyphens."""
    return name in library and library[name] != name and hyphenated(library[name]) == name


def title_of(sources: list[Path], library: dict[str, str] | None = None) -> str:
    """The document title, taken from the source file name.

    A source named without spaces takes the title from its library name, so the
    title keeps the spaces and punctuation the document is known by.
    """
    name = sources[0].name
    if spaced_off(name, library or {}):
        name = library[name]
    return re.sub(r"\s{2,}", " ", Path(name).stem.strip())


def page_title(out: Path) -> str | None:
    """The title a converted page already carries, when its H1 is its own file name.

    A file name under docs/ writes spaces as hyphens, so the H1 is what keeps the
    spaces and punctuation of a name this script was handed without them.
    """
    try:
        with out.open(encoding="utf-8") as page:
            first = page.readline()
    except (OSError, UnicodeDecodeError):
        return None
    heading = re.match(r"# (.+?)\s*$", first)
    if heading and hyphenated(heading.group(1)) == out.stem:
        return heading.group(1)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean and stamp one document.")
    parser.add_argument(
        "--config", help="the skill's extension.json, which names the library host",
    )
    parser.add_argument("--markdown", required=True, help="Pandoc output to clean")
    parser.add_argument("--out", required=True, help="finished Markdown to write")
    parser.add_argument(
        "--source", action="append", default=[], required=True,
        help="a source document this Markdown came from, repeatable",
    )
    parser.add_argument(
        "--converted", default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
        help="the run date and time to the minute, in Zulu time (a trailing Z), the only value this script originates",
    )
    parser.add_argument("--title", help="override the title taken from the file name")
    parser.add_argument(
        "--origin",
        help="where the content was written, for a file that only transports it",
    )
    parser.add_argument(
        "--properties-from", action="append", default=[],
        help="a file the ladder may read in place of the source, repeatable",
    )
    parser.add_argument(
        "--library", action="append", default=[], metavar="LOCAL=LIBRARY",
        help="the library name of a source renamed here, repeatable",
    )
    parser.add_argument(
        "--sharepoint", action="append", default=[], metavar="FILE=PATH",
        help="the server-relative library path of a source, repeatable",
    )
    parser.add_argument(
        "--pages-from", help="the file the document's pages are counted from",
    )
    parser.add_argument(
        "--pages-renderable",
        help="a copy of --pages-from that LibreOffice and the Word reader can open",
    )
    args = parser.parse_args()
    host = convert_config.load(args.config, "stamp").value("sharePointHost")

    library = dict(pair.split("=", 1) for pair in args.library)
    # A name may hold `=` but never `/`, and a library path opens with `/`, so a value
    # without `=/` names no path and gets no line.
    sharepoint = {
        name: "/" + path
        for name, _, path in (pair.partition("=/") for pair in args.sharepoint)
        if path
    }

    sources = [Path(value) for value in args.source]
    readable = [Path(value) for value in args.properties_from] or sources
    body = clean(Path(args.markdown).read_text(encoding="utf-8", errors="replace"))
    title = args.title or page_title(Path(args.out)) or title_of(sources, library)

    # The revision table and the stated update line are read from the body before
    # the page markers go in, so a marker never sits between a heading and its table.
    paged = None
    marked = body
    if args.pages_from:
        renderable = Path(args.pages_renderable) if args.pages_renderable else None
        layout = pages.layout_of(Path(args.pages_from), renderable)
        if layout:
            # A page link reaches the page only in a PDF the library holds.
            pdf = layout.from_pdf.name if layout.from_pdf else None
            link = sharepoint_url(sharepoint[pdf], host) if pdf in sharepoint else None
            placed = pages.place(body, layout, link)
            marked = placed.markdown
            paged = pages_line(layout, placed.missed)
            print(f"     {layout.pages} page(s) {layout.label},"
                  f" {len(placed.missed)} not found in the text")
    block = provenance(
        body, sources, args.converted, readable, args.origin, library, sharepoint,
        paged, host,
    )

    Path(args.out).write_text(f"# {title}\n\n{block}\n\n{marked}", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
