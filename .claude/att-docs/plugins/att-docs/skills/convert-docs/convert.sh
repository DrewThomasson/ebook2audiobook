#!/usr/bin/env bash
# Converts a batch of source documents into stamped Markdown.
#
# Walks the input tree one suite folder at a time, groups the files that are the
# same document in different formats, routes each group by the format of its
# richest member, and writes Markdown to the matching folder under the apps root.
# A source that converts and stamps without error moves to _done, so a rerun
# picks up only what is left. A suite's future folder, which holds the revisions
# the system does not carry yet, is walked as a suite folder of its own and
# lands in the same folder under the suite's output folder.
#
# Usage:
#   convert.sh --config FILE [--in DIR] [--out DIR] [--suite NAME] [--limit N]
#              [--dry-run] [--keep-sources] [--converted 'YYYY-MM-DD HH:MMZ']
#
# FILE is the skill's extension.json (see convert_config.py). --in and --out
# default to its todoRoot and appsRoot, and a relative path is read from the
# top of the repository the file sits in.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CONFIG=""
IN=""
OUT=""
SUITE=""
LIMIT=0
DRY_RUN=0
KEEP_SOURCES=0
CONVERTED="$(date -u +'%F %H:%MZ')"

# The share of a secondary source's vocabulary that may be missing from the
# primary before the group is held back for a merge by hand. Across the thirteen
# docx and pdf pairs in the current batch the worst case is 1.6 per cent, so a
# group that trips this is one where the formats genuinely disagree.
SECONDARY_LOSS_PCT=5

while [ "$#" -gt 0 ]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    --in) IN="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --suite) SUITE="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --converted) CONVERTED="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --keep-sources) KEEP_SOURCES=1; shift ;;
    -h|--help) sed -n '2,18p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "convert-docs: unknown option $1" >&2; exit 2 ;;
  esac
done

for tool in pandoc soffice pdftotext pdfinfo python3 git; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "convert-docs: $tool is not installed" >&2
    exit 1
  }
done

[ -n "$CONFIG" ] || {
  echo "convert-docs: --config <extension.json> is required" >&2
  exit 64
}
[ -f "$CONFIG" ] || { echo "convert-docs: no config at $CONFIG" >&2; exit 64; }
CONFIG="$(cd "$(dirname "$CONFIG")" && pwd)/$(basename "$CONFIG")"

# One field of the config. A field it lacks fails with exit 64 and names it.
config_value() {
  python3 "$HERE/convert_config.py" "$CONFIG" "$1"
}

ROOT="$(git -C "$(dirname "$CONFIG")" rev-parse --show-toplevel 2>/dev/null)" || {
  echo "convert-docs: $CONFIG is not inside a git work tree" >&2
  exit 64
}
cd "$ROOT" || exit 1

[ -n "$IN" ] || IN="$(config_value todoRoot)" || exit 64
[ -n "$OUT" ] || OUT="$(config_value appsRoot)" || exit 64
FUTURE="$(config_value futureFolder)" || exit 64
WORDS="$(config_value words)" || exit 64
COLLISIONS="$(config_value collisions)" || exit 64

# The word list the shifted text check reads. Without it that check cannot
# answer, and a batch converted without it is one nobody scanned.
[ -s "$WORDS" ] || {
  echo "convert-docs: $WORDS is missing, run build-words.py" >&2
  exit 1
}

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

DONE_ROOT="$IN/_done"
STAGE="$IN/_needs_merge"
# Where each downloaded document sits in the SharePoint library, written by the
# doc-watch placement step: a suite, a file name, and the server-relative path.
LIBRARY_PATHS="$IN/library.tsv"

converted=0
skipped=0
held=0
quarantined=0
unmapped=0
renumbered=0

log() { printf '%s\n' "$*"; }

# Pandoc reads the same way for every text format that reaches it, so the
# options live in one place: no images, pipe tables, and a column cap that keeps
# prose readable.
#
# The output is Markdown and nothing else. Left alone, a presentation routed
# through HTML arrives as a stack of `::::` fenced divs wrapped around raw
# `<div>` blocks, which is the page layout of the slide rather than anything the
# document says.
#
# The table syntax is the pipe table, because it is the only one that renders
# outside Pandoc. Reaching it takes the filter beside this script: the writer
# falls back to a raw HTML table whenever a cell holds a list, a second
# paragraph, a line break, or a row or column span, and every one of those is
# ordinary in the control tables these documents are built from.
#
# The writer numbers every list with digits, so a list Word letters a, b, c
# would arrive as 1, 2, 3. The last filter writes Word's letter or roman numeral
# into the item instead. It runs after the table filter, which has already
# turned a cell's list into text.
PANDOC_TO='gfm-raw_html-raw_attribute'

run_pandoc() {
  local from="$1" input="$2" output="$3"
  case "$from" in
    # The HTML reader keeps a div or a span as a structural node unless it is
    # told not to, and those are what the writer then has to render.
    html) from='html-native_divs-native_spans' ;;
    # Word never prints its hidden text, and Pandoc writes it as any other
    # text, so the hidden runs come out first. Then, since Pandoc counts and
    # nests a Word list differently from Word, the numbering is rewritten into
    # a form it draws the way Word does. A file a step cannot read, such as an
    # RTF file tried here first, goes on as it is.
    docx)
      if python3 "$HERE/hidden-text.py" "$input" "$WORK/visible.docx" 2>/dev/null; then
        input="$WORK/visible.docx"
      fi
      if python3 "$HERE/list-numbers.py" "$input" "$WORK/numbered.docx" 2>/dev/null; then
        input="$WORK/numbered.docx"
      fi
      ;;
  esac
  pandoc -f "$from" -t "$PANDOC_TO" \
    --columns=100 --wrap=auto \
    --lua-filter="$HERE/drop-images.lua" \
    --lua-filter="$HERE/flatten-tables.lua" \
    --lua-filter="$HERE/list-markers.lua" \
    "$input" -o "$output" 2>>"$WORK/pandoc.err"
}

# LibreOffice writes into a directory rather than to a named file, so the caller
# gets back whatever it produced for that extension.
run_soffice() {
  local filter="$1" input="$2" outdir="$3"
  mkdir -p "$outdir"
  soffice --headless --convert-to "$filter" --outdir "$outdir" "$input" \
    >>"$WORK/soffice.log" 2>&1
}

# A PDF has no heading structure to read, so the only signal left is layout: a
# short line, set off by blank space, that is not a sentence and not part of the
# body flow. Anything less certain than that stays a paragraph.
pdf_to_markdown() {
  local input="$1" output="$2" text="$WORK/pdf.txt"
  pdftotext -layout "$input" "$text" 2>>"$WORK/pdftotext.err" || return 1
  python3 - "$text" "$output" <<'PY'
import collections, re, sys

text, output = sys.argv[1], sys.argv[2]
raw_text = open(text, encoding="utf-8", errors="replace").read()
pages = raw_text.split("\f")
lines = raw_text.replace("\f", "\n").split("\n")

# A running header or footer is the same line on page after page. Anything
# repeating on more than half of a document of several pages is furniture, and
# printing it between every section makes the result unreadable.
furniture = set()
if len(pages) > 2:
    counts = collections.Counter(
        line.strip() for line in lines if len(line.strip()) > 3
    )
    for line, count in counts.items():
        if count > len(pages) / 2:
            furniture.add(line)

out, previous_blank = [], True
for index, raw in enumerate(lines):
    # The leading whitespace is the page margin. Left in place it reads as a
    # Markdown code block, so it comes off every line. The spacing inside the
    # line is what holds a laid-out table together and stays.
    line = raw.strip() if raw[:4].strip() == "" else raw.rstrip()
    stripped = line.strip()
    if stripped in furniture:
        continue
    if not stripped:
        if out and out[-1] != "":
            out.append("")
        previous_blank = True
        continue
    following_blank = index + 1 >= len(lines) or not lines[index + 1].strip()
    # A PDF carries no heading structure, so layout is the only signal left: a
    # short line standing alone that does not read as a sentence. Anything less
    # certain than that stays a paragraph.
    heading = (
        previous_blank
        and following_blank
        and len(stripped) <= 60
        and not stripped.endswith((".", ",", ";", ":"))
        and not stripped[0].islower()
        and not re.match(r"^[\d/.\-]+$", stripped)
        and len(stripped.split()) <= 9
    )
    out.append(f"## {stripped}" if heading else line)
    previous_blank = False

open(output, "w", encoding="utf-8").write("\n".join(out).strip() + "\n")
PY
}

# A sheet is padded out to its used range, so the export carries rows and
# columns that are empty from end to end. They are dropped here rather than in
# the Markdown, where an empty row of a document's own table looks the same and
# is worth keeping: four of the seven upload documents have a revision table
# whose rows the author never filled in, and that is a fact about the document.
trim_csv() {
  python3 - "$1" "$2" <<'PY'
import csv, sys

with open(sys.argv[1], newline="", encoding="utf-8", errors="replace") as handle:
    rows = [row for row in csv.reader(handle)]

rows = [row for row in rows if any(cell.strip() for cell in row)]
if not rows:
    raise SystemExit(1)

width = max(len(row) for row in rows)
rows = [row + [""] * (width - len(row)) for row in rows]
keep = [i for i in range(width) if any(row[i].strip() for row in rows)]

with open(sys.argv[2], "w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    for row in rows:
        writer.writerow([row[i] for i in keep])
PY
}

# Every sheet of a workbook goes to its own csv named for the sheet, which is
# where the sheet names come from. LibreOffice writes a one-byte file for an
# empty sheet, so those are reported rather than rendered as an empty table.
spreadsheet_to_markdown() {
  local input="$1" output="$2" sheets="$WORK/sheets" csv name
  rm -rf "$sheets"
  run_soffice \
    "csv:Text - txt - csv (StarCalc):44,34,76,1,,0,false,true,true,false,false,-1" \
    "$input" "$sheets"

  : >"$output"
  local wrote=0
  for csv in "$sheets"/*.csv; do
    [ -e "$csv" ] || continue
    name="$(basename "$csv" .csv)"
    name="${name#"$(basename "${input%.*}")"-}"
    if [ "$(wc -c <"$csv")" -le 2 ]; then
      log "      sheet '$name' is empty"
      continue
    fi
    trim_csv "$csv" "$WORK/sheet.csv" || continue
    printf '# %s\n\n' "$name" >>"$output"
    run_pandoc csv "$WORK/sheet.csv" "$WORK/sheet.md" || continue
    cat "$WORK/sheet.md" >>"$output"
    printf '\n\n' >>"$output"
    wrote=$((wrote + 1))
  done
  [ "$wrote" -gt 0 ]
}

# Turns one source file into Markdown, whatever it takes to get there. A route
# that produces an intermediate the provenance ladder can read better than the
# original leaves its path in READABLE.
to_markdown() {
  local input="$1" output="$2"
  local extension="${input##*.}"
  local base

  READABLE="$input"

  case "$(printf '%s' "$extension" | tr '[:upper:]' '[:lower:]')" in
    docx|docm|odt|rtf)
      run_pandoc docx "$input" "$output" 2>/dev/null ||
        run_pandoc odt "$input" "$output"
      ;;
    doc|dot)
      # Pandoc cannot read the legacy binary format, so LibreOffice writes the
      # modern one first and Pandoc reads that. That copy is also what the
      # provenance ladder reads: the legacy format is not a zip archive, and
      # LibreOffice carries the original dates and the header and footer parts
      # across intact.
      run_soffice docx "$input" "$WORK/doc"
      base="$(basename "${input%.*}").docx"
      [ -f "$WORK/doc/$base" ] || return 1
      READABLE="$WORK/doc/$base"
      run_pandoc docx "$WORK/doc/$base" "$output"
      ;;
    htm|html)
      run_pandoc html "$input" "$output"
      ;;
    ppt|pptx|pptm|odp)
      # Pandoc reads no presentation format at all, so this one goes through
      # HTML rather than through the container.
      run_soffice html "$input" "$WORK/ppt"
      base="$(basename "${input%.*}").html"
      [ -f "$WORK/ppt/$base" ] || return 1
      run_pandoc html "$WORK/ppt/$base" "$output"
      ;;
    xls|xlsx|xlsm|ods)
      spreadsheet_to_markdown "$input" "$output"
      ;;
    pdf)
      pdf_to_markdown "$input" "$output"
      ;;
    txt|md)
      cp "$input" "$output"
      ;;
    *)
      return 1
      ;;
  esac
}

# Ranks the formats of one document so the richest becomes the body. The order
# is measured rather than assumed: across the docx and pdf pairs in the current
# batch the PDF loses the whole database column of every data dictionary table,
# and gives back one word.
rank_of() {
  case "$(printf '%s' "${1##*.}" | tr '[:upper:]' '[:lower:]')" in
    docx) echo 10 ;;
    docm) echo 9 ;;
    doc|dot) echo 8 ;;
    odt|rtf) echo 7 ;;
    htm|html) echo 6 ;;
    pptx|pptm|ppt|odp) echo 5 ;;
    xlsx|xlsm|xls|ods) echo 4 ;;
    pdf) echo 3 ;;
    md) echo 2 ;;
    txt) echo 1 ;;
    *) echo 0 ;;
  esac
}

# The library name of a file renamed here, or nothing when it carries its own.
# Two library documents under one name convert to one Markdown file, so one of
# them is downloaded under a longer name, and collisions.tsv is where that name
# is written down.
library_name_of() {
  local suite="$1" file="$2" row_suite row_file row_library
  [ -f "$COLLISIONS" ] || return 0
  while IFS=$'\t' read -r row_suite row_file row_library; do
    case "$row_suite" in ''|'#'*) continue ;; esac
    if [ "$row_suite" = "$suite" ] && [ "$row_file" = "$file" ]; then
      printf '%s' "$row_library"
      return 0
    fi
  done <"$COLLISIONS"
}

# A name as it is written under docs/: each run of spaces, with any hyphens
# touching it, becomes one hyphen. doc_paths.hyphenated is the same rule. Its
# other half, dropping a hyphen in front of the extension, needs no line here:
# a stem has no extension, and a trailing hyphen is never written.
hyphenated() {
  case "$1" in
    *[[:space:]]*)
      printf '%s' "$1" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g' \
        | sed -E 's/[[:space:]-]*[[:space:]][[:space:]-]*/-/g'
      ;;
    *) printf '%s' "$1" ;;
  esac
}

# The server-relative library path of a source, or nothing when the batch did
# not come through doc-watch and no path was recorded for it.
library_path_of() {
  local suite="$1" file="$2" row_suite row_file row_path
  [ -f "$LIBRARY_PATHS" ] || return 0
  while IFS=$'\t' read -r row_suite row_file row_path; do
    case "$row_suite" in ''|'#'*) continue ;; esac
    if [ "$row_suite" = "$suite" ] && [ "$row_file" = "$file" ]; then
      printf '%s' "$row_path"
      return 0
    fi
  done <"$LIBRARY_PATHS"
}

# The file a document's pages are counted from: a PDF of it when the group has
# one, since its pages are the pages, and otherwise the body's own source.
pages_source_of() {
  local path
  for path in "$@"; do
    case "$(printf '%s' "${path##*.}" | tr '[:upper:]' '[:lower:]')" in
      pdf) printf '%s' "$path"; return 0 ;;
    esac
  done
  printf '%s' "$primary"
}

# A file that failed to download is a stub explaining the failure, not a
# document. Converting one produces a Markdown file that reads like a document
# and holds an error message.
is_download_stub() {
  local path="$1"
  case "$(basename "$path")" in
    *_Error.txt|___All_Errors.txt) return 0 ;;
  esac
  grep -qlE 'cannot be downloaded|RemoteItemNotFound|have not been downloaded' \
    "$path" 2>/dev/null
}

# Reports how much of a secondary source's vocabulary the chosen body lost.
secondary_loss() {
  python3 - "$1" "$2" <<'PY'
import re, sys


def tokens(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return set(re.findall(r"[A-Za-z0-9_]{3,}", handle.read()))


primary, secondary = tokens(sys.argv[1]), tokens(sys.argv[2])
missing = secondary - primary
print(round(100 * len(missing) / len(secondary), 1) if secondary else 0.0)
PY
}

suites=()
if [ -n "$SUITE" ]; then
  suites=("$IN/$SUITE")
else
  for candidate in "$IN"/*/; do
    case "$(basename "$candidate")" in
      _done|_needs_merge) continue ;;
    esac
    [ -d "$candidate" ] && suites+=("$candidate")
    [ -d "${candidate}$FUTURE" ] && suites+=("${candidate}$FUTURE/")
  done
fi

for suite_dir in "${suites[@]}"; do
  # The folder under the input tree, OCS or OCS/Future, which the output mirrors.
  suite="${suite_dir%/}"
  suite="${suite#"$IN"/}"
  [ -d "$suite_dir" ] || { log "convert-docs: no such suite folder: $suite_dir"; continue; }
  log ""
  log "== $suite"

  # Group the suite's files by the name they share, so that a document held in
  # more than one format is converted once.
  stems="$WORK/stems.${suite//\//_}"
  : >"$stems"
  while IFS= read -r path; do
    [ -n "$path" ] || continue
    printf '%s\n' "${path%.*}"
  # Byte ordering, because a locale collation folds away spaces and punctuation
  # and would treat two names that differ only in those as one document.
  done < <(find "$suite_dir" -maxdepth 1 -type f | LC_ALL=C sort) \
    | LC_ALL=C sort -u >"$stems"

  while IFS= read -r stem; do
    [ -n "$stem" ] || continue
    if [ "$LIMIT" -gt 0 ] && [ "$converted" -ge "$LIMIT" ]; then
      break 2
    fi

    sources=()
    while IFS= read -r path; do
      # A name may carry a dot of its own, as `FA Home License.rev 1.2.doc`
      # does, and the glob reaches that from the shorter `FA Home License`.
      # Only a candidate whose own stem is this stem is this document.
      [ "${path%.*}" = "$stem" ] || continue
      [ -f "$path" ] && sources+=("$path")
    done < <(find "$(dirname "$stem")" -maxdepth 1 -type f \
      -name "$(basename "$stem").*" | sort)
    [ "${#sources[@]}" -gt 0 ] || continue

    name="$(basename "$stem")"
    page="$(hyphenated "$name")"

    if is_download_stub "${sources[0]}" && [ "${#sources[@]}" -eq 1 ]; then
      log "  -- $name: a download failure stub, not a document"
      quarantined=$((quarantined + 1))
      continue
    fi

    # The richest format carries the body. Every other format still gets named
    # in the provenance block and read for what the body may have lost.
    primary="${sources[0]}"
    for path in "${sources[@]}"; do
      [ "$(rank_of "$path")" -gt "$(rank_of "$primary")" ] && primary="$path"
    done

    if [ "$(rank_of "$primary")" -eq 0 ]; then
      log "  -- $name: no route for .${primary##*.}"
      skipped=$((skipped + 1))
      continue
    fi

    log "  -> $name (${#sources[@]} source(s), body from .${primary##*.})"
    if [ "$DRY_RUN" -eq 1 ]; then
      converted=$((converted + 1))
      continue
    fi

    body="$WORK/body.md"
    : >"$body"
    READABLE="$primary"
    if ! to_markdown "$primary" "$body" || [ ! -s "$body" ]; then
      log "     conversion produced nothing, left in place"
      skipped=$((skipped + 1))
      continue
    fi
    # Held before the secondary check below, which calls the same routes and
    # would otherwise leave its own intermediate here.
    primary_readable="$READABLE"

    # A PDF whose font carries no map back to characters reaches here as the
    # glyph codes themselves, which read as text to every other check. The
    # document is held rather than decoded: the offset between a code and the
    # character it draws belongs to the font rather than being a constant, and
    # the spaces and the punctuation are gone whichever way it is read.
    shifted="$(python3 "$HERE/check-shifted-text.py" --config "$CONFIG" \
      --label="$name" -- "$body" 2>&1)"
    case "$?" in
      0) ;;
      2)
        printf '%s\n' "$shifted" | sed 's/^/     /'
        log "     held for a reader, sources left in place"
        unmapped=$((unmapped + 1))
        continue
        ;;
      *)
        # The check itself could not run, which says nothing about the
        # document, so it stops the batch rather than holding everything.
        printf '%s\n' "$shifted" | sed 's/^/     /'
        echo "convert-docs: the shifted text check failed to run" >&2
        exit 1
        ;;
    esac

    # A second format of the same document is a check on the first. When it
    # holds substantially more than the body does, the two disagree by enough
    # that a person should decide what the document says.
    hold=0
    for path in "${sources[@]}"; do
      [ "$path" = "$primary" ] && continue
      secondary="$WORK/secondary.md"
      : >"$secondary"
      to_markdown "$path" "$secondary" 2>/dev/null || continue
      [ -s "$secondary" ] || continue
      loss="$(secondary_loss "$body" "$secondary")"
      log "     .${path##*.} holds ${loss}% the body does not"
      if [ "$(printf '%s\n' "$loss $SECONDARY_LOSS_PCT" | awk \
        '{print ($1 > $2) ? 1 : 0}')" -eq 1 ]; then
        mkdir -p "$STAGE/$suite"
        cp "$body" "$STAGE/$suite/$page.from-${primary##*.}.md"
        cp "$secondary" "$STAGE/$suite/$page.from-${path##*.}.md"
        hold=1
      fi
    done

    if [ "$hold" -eq 1 ]; then
      log "     the formats disagree, staged for a merge by hand"
      held=$((held + 1))
      continue
    fi

    mkdir -p "$OUT/$suite"
    args=()
    for path in "${sources[@]}"; do
      args+=(--source "$path")
      lib="$(library_name_of "$suite" "$(basename "$path")")"
      [ -n "$lib" ] && args+=(--library "$(basename "$path")=$lib")
      # A file renamed here off a shared library name was downloaded, and its
      # path recorded, under the library name.
      where="$(library_path_of "$suite" "$(basename "$path")")"
      [ -z "$where" ] && [ -n "$lib" ] && where="$(library_path_of "$suite" "$lib")"
      [ -n "$where" ] && args+=(--sharepoint "$(basename "$path")=$where")
      # A file downloaded without the spaces of its library name keeps that name
      # for the Source line and the title.
      if [ -z "$lib" ] && [ -n "$where" ] && [ "${where##*/}" != "$(basename "$path")" ]; then
        args+=(--library "$(basename "$path")=${where##*/}")
      fi
      # A source the ladder can read as it stands is offered as it stands. The
      # one the primary route rewrote is offered as the rewrite.
      if [ "$path" = "$primary" ]; then
        args+=(--properties-from "$primary_readable")
      else
        args+=(--properties-from "$path")
      fi
    done
    paged="$(pages_source_of "${sources[@]}")"
    args+=(--pages-from "$paged")
    [ "$paged" = "$primary" ] && args+=(--pages-renderable "$primary_readable")
    if ! python3 "$HERE/stamp.py" --config "$CONFIG" --markdown "$body" \
      --out "$OUT/$suite/$page.md" --converted "$CONVERTED" "${args[@]}"; then
      log "     stamping failed, left in place"
      skipped=$((skipped + 1))
      continue
    fi

    # A rule cites the source's list numbers, so a converted list that counts
    # differently is reported. The document is still written: the numbers are a
    # thing to correct in the Markdown, not a reason to doubt the rest of it.
    case "$(printf '%s' "${primary##*.}" | tr '[:upper:]' '[:lower:]')" in
      docx|docm|doc|dot)
        status=0
        listed="$(python3 "$HERE/check-list-numbers.py" "$OUT/$suite/$page.md" "$primary" \
          2>&1)" || status=$?
        if [ "$status" -eq 2 ]; then
          printf '%s\n' "$listed" | sed 's/^/     /'
          log "     list numbers differ from the source"
          renumbered=$((renumbered + 1))
        elif [ "$status" -ne 0 ]; then
          printf '%s\n' "$listed" | sed 's/^/     /'
        fi
        ;;
    esac

    if [ "$KEEP_SOURCES" -eq 0 ]; then
      mkdir -p "$DONE_ROOT/$suite"
      for path in "${sources[@]}"; do
        mv "$path" "$DONE_ROOT/$suite/"
      done
    fi
    converted=$((converted + 1))
  done <"$stems"

  # Git carries no empty folder, so one left behind here is a folder the
  # living-wiki check still writes a todo page for and the committed tree does
  # not have. rmdir refuses a folder that still holds anything, and a run
  # keeping its sources leaves the folder as it found it.
  if [ "$KEEP_SOURCES" -eq 0 ] && [ -z "$(ls -A "$suite_dir")" ]; then
    rmdir "$suite_dir" && log "     $suite emptied, folder removed"
    # A Future folder is walked after its suite folder, so the suite folder is
    # removed here once the Future folder was all it still held.
    parent="$IN/${suite%/*}"
    if [ "$parent" != "$IN/$suite" ] && [ -z "$(ls -A "$parent")" ]; then
      rmdir "$parent" && log "     ${suite%/*} emptied, folder removed"
    fi
  fi
done

log ""
log "converted $converted, staged for merge $held, skipped $skipped," \
    "quarantined $quarantined, in an unmapped font $unmapped," \
    "with list numbers off the source $renumbered"
[ -s "$WORK/pandoc.err" ] && log "pandoc reported warnings, see the run output"
exit 0
