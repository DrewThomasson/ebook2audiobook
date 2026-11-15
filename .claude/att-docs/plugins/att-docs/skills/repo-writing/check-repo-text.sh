#!/usr/bin/env bash
# Scans text that ships to the work repository for references that repository
# cannot resolve: this side's tracker numbers, its CI, and any assistant.
# See the SKILL.md beside this file for the rules and the escape hatch.
#
#   check-repo-text.sh --config <file> [path...]
#
# With no paths it scans the files this branch changed that the config's
# "shipping" pattern matches and its "notShipping" pattern does not, including
# uncommitted ones. With paths it scans exactly the paths given. Either way the
# paths are read from the top of the git work tree the scan runs in.
#
# The config is a JSON file; a path in it is relative to the git toplevel of
# the config file's folder:
#   terms           the banned-terms table
#   trackerScope    the table's scope for rows that apply only to text sent to
#                   the work tracker
#   guide           the page a failing run points the reader at, printed as is
#   verbatimMarker  the marker that lets one quoted line through
#   mainBranch      the branch the changed files are measured from
#   shipping        the pattern a changed path matches to be scanned
#   notShipping     the pattern that keeps a changed path out all the same
#   skipPaths       patterns for paths the rules leave alone, given or not
#   exemptPaths     [{path, except}]: a path under path is left alone unless
#                   it also matches except
#   voiceWords      patterns for the words the owning tester would not use
#
# Exits 1 and prints path:line for every hit, 2 when the scan cannot finish,
# and 64 when the config is missing.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
. "$HERE/config.sh"
config_open check-repo-text "$@" || exit
set -- "${CONFIG_ARGS[@]}"
config_read guide verbatimMarker mainBranch=main shipping notShipping skipPaths \
  exemptPaths voiceWords
if [ "${#CONFIG_VALUES[@]}" -ne 8 ]; then
  echo "check-repo-text: the config does not read" >&2
  exit 2
fi
GUIDE="${CONFIG_VALUES[0]}"
# A line carrying this marker is a verbatim quote whose wording is evidence.
ALLOW_MARKER="${CONFIG_VALUES[1]}"
MAIN_BRANCH="${CONFIG_VALUES[2]}"
SHIPPING="${CONFIG_VALUES[3]}"
NOT_SHIPPING="${CONFIG_VALUES[4]}"
# Paths whose every line is evidence or tooling rather than shipped prose.
SKIP_PATHS="${CONFIG_VALUES[5]}"
EXEMPT=()
[ -n "${CONFIG_VALUES[6]}" ] && mapfile -t EXEMPT <<<"${CONFIG_VALUES[6]}"
VOICE="${CONFIG_VALUES[7]}"
SCAN_CONFIG="$CONFIG_FILE"

cd "$(git rev-parse --show-toplevel)" || exit 1

# Whether the rules leave a path alone: a skipped path, or an exempt one that
# is not one of its exceptions.
skipped() {
  local pair under except
  [ -n "$SKIP_PATHS" ] && [[ "$1" =~ $SKIP_PATHS ]] && return 0
  for pair in "${EXEMPT[@]}"; do
    under="${pair%%$'\t'*}" except="${pair#*$'\t'}"
    [[ "$1" =~ $under ]] || continue
    [ -n "$except" ] && [[ "$1" =~ $except ]] && continue
    return 0
  done
  return 1
}

# A Markdown file holding the text of a Word or Excel document, extracted so it
# can be read and searched here. The wording belongs to whoever wrote the
# document, so every line is evidence.
#
# Two things identify one. It sits beside the document it came from, or it opens
# with the provenance block naming the document it came from. The second is what
# answers for a converted batch, whose sources are not committed. A hand-written
# file has neither and stays in scope. The second argument is the file's head
# flags, per HEAD_FLAGS below.
is_converted_document() {
  local path="$1" flags="$2" base ext
  case "$path" in
    *.md) ;;
    *) return 1 ;;
  esac
  base="${path%.md}"
  for ext in doc docx docm xls xlsx xlsm pdf; do
    [ -e "$base.$ext" ] && return 0
  done
  [[ "$flags" == *P* && "$flags" == *S* ]]
}

# The terms a line may not carry, and the identifiers that read like them and
# are allowed, live in the table the config names, which the checks on text
# sent to the work tracker read too. Only the rows scoped to every reader, or
# to a glob the scanned path matches, apply here.
# shellcheck source=terms.sh
. "$HERE/terms.sh"
terms_use_config "$SCAN_CONFIG" || exit 2
read_terms || exit 2
select_terms all

# Rule 3 governs prose, so the voice scan reads neither of the two things on a
# line that is not prose. A test title names the reproduction and a rerun
# filters on it, which makes it an identifier; the coverage matrix and the
# tables of record data quoted beneath it are rows that were read, not written.
VOICE_SKIP='s/^[[:space:]]*\|.*//'
# A block fenced four backticks deep, so the fences inside it survive, is the
# text a record carries to or from the work tracker. It is a copy of text the
# dev team already has, and our copy says what theirs says.
VOICE_SKIP+=';/^````/,/^````/s/.*//'
# A fenced block holds a request, an answer, a query, or the output a run
# printed. All four are read rather than written, and a record that quotes one
# says what the run said.
VOICE_SKIP+=';/^[[:space:]]*```/,/^[[:space:]]*```/s/.*//'
# A line opening on a typographic quote is an application message or a line of
# a functional spec, copied for the wording. A comment marker and the bullet
# the spec numbered the line with sit in front of it in source, so they come
# off before the quote is read.
VOICE_SKIP+=';s%^[[:space:]]*(//)?[[:space:]]*[o·-]?[[:space:]]*“.*%%'
# A heading or list entry that is a matrix id followed by its scenario name, and
# nothing else. A line that carries an id and then says something about it is a
# sentence, so the colon or the period keeps it in scope.
VOICE_SKIP+=';s/^[#[:space:]*-]*(TS-)?[A-Z][A-Z0-9]*(-[A-Z0-9]+)+'
VOICE_SKIP+='[[:space:]][A-Za-z'"'"'()\/[:space:]-]*$//'
VOICE_SKIP+=';s/(describe|test|test\.step|it)[[:space:]]*\([[:space:]]*[`"'"'"'][^`"'"'"']*//g'
# The same title one line down, where the call opens on its own line. Reading
# the next line in keeps both, so the line numbers a hit reports still index
# the file.
VOICE_SKIP+=";/(describe|test|test\\.step|it)[[:space:]]*\\([[:space:]]*\$/"
VOICE_SKIP+="{N;s/\\n([[:space:]]*)[\`\"'][^\`\"']*/\\n\\1/}"

# Text that narrates what the code used to do instead of describing how it works
# now. "Previously" and "no longer" are ordinary words in the business rules
# these files quote, so the softer markers only count next to code vocabulary.
SUBJECT='(test|tests|spec|specs|suite|describe|block|helper|helpers|rule|glob'
SUBJECT+='|method|function|locator|selector|assertion|constant|fixture|class'
SUBJECT+='|file|comment|variable|check|call|code|flag|step|wait|import|config'
SUBJECT+='|query|column|table|page|column)'
HISTORY="\\b${SUBJECT}s?[[:space:]]+(used to|previously|no longer|was removed"
HISTORY+='|were removed|was renamed|were renamed)\b'
HISTORY+='|\b(we|this|these|it)[[:space:]]+(used to|previously)\b'
# "has been deleted" is an application message these documents quote, so the
# passive forms only count next to code vocabulary
HISTORY+="|\\b${SUBJECT}s?[[:space:]]+(was|were|has been|have been|had been)"
HISTORY+='[[:space:]]+(removed|renamed|replaced|deleted|dropped|reverted)\b'
HISTORY+='|\brenamed[[:space:]]+(from|to)\b'
HISTORY+='|\bused to[[:space:]]+(be|live|exist|sit|hold|carry)\b'
HISTORY+='|\b(was|were)[[:space:]]+formerly\b'
HISTORY+='|\bformerly[[:space:]]+(named|called|known as)\b'
HISTORY+='|\b(instead of|rather than)[[:space:]]+(the[[:space:]]+)?(old|previous|former)\b'
HISTORY+='|\bthe[[:space:]]+(old|previous|former)[[:space:]]+(name|behavior|behaviour'
HISTORY+='|approach|version|implementation|locator|helper|selector|glob|rule'
HISTORY+='|constant|assertion)\b'
HISTORY+='|\b(the|its|a)[[:space:]]+(first|original|initial)[[:space:]]+version\b'
# "predates" stays out of this list. It is ordinary in these files: a worker
# record older than a business function, a stage older than a template, a date
# of birth before 1850. The one shape that does narrate history, a sampling run
# that predates a rule the branch later tightened, wraps across two lines as
# often as not, so a line scan cannot see it and section 2 of SKILL.md owns it.

# Words that give the author away, from the config's voiceWords. A tester
# writing up what an application did does not reach for these, so a line
# carrying one reads as though nobody typed it. Only the words that have
# actually landed belong there. The broader prose tells are judgment calls a
# scan gets wrong on quoted text, so section 4 of SKILL.md carries them and the
# humanizer pass applies them.

# British spellings. The reader on the work side writes American English, so a
# word carrying the other spelling reads the same way a word out of his
# vocabulary does, and rule 3 covers both. Each family is spelled out by its
# endings rather than closed with [a-z]*, so a camel-case identifier that opens
# on one of them stays clean: authorIsWorker is a method, not authorisation.
#
# Acknowledgement is not here: an application under test can spell it that way
# on its own screens, and a test quoting the screen says what the screen says.
# A screen's own spelling of a word that is here goes in the terms table as a
# kept identifier.
SPELLING='\b(behaviour|colour|favour|honour|labour|neighbour|rumour|endeavour'
SPELLING+='|humour|odour|vapour|savour|flavour)(s|ed|ing|al|ally|able|ably|ful'
SPELLING+='|less|ite|ites|hood|hoods|ly|ous)?\b'
SPELLING+='|\b(centre|theatre|fibre|calibre|sombre|spectre)(s|d)?\b'
SPELLING+='|\b(licence|defence|offence|pretence)(s|d)?\b'
SPELLING+='|\bpractis(e|es|ed|ing)\b'
SPELLING+='|\b(organis|realis|recognis|normalis|initialis|serialis|finalis'
SPELLING+='|authoris|categoris|prioritis|summaris|minimis|maximis|utilis'
SPELLING+='|standardis)(e|es|ed|ing|ation|ations|ational|able)\b'
SPELLING+='|\b(analys|paralys)(e|es|ed|ing)\b'
SPELLING+='|\bcatalogue(s|d)?\b|\bprogramme(s)?\b'
SPELLING+='|\bgrey(s|ed|ing|ish|scale)?\b|\bstorey(s)?\b'
SPELLING+='|\bsceptic(al|ally|ism)?\b|\bmould(s|ed|ing|y)?\b'
SPELLING+='|\bdraught(s|y)?\b|\bageing\b|\bjudgement(s)?\b'
SPELLING+='|\btravell(ed|ing)\b|\blabell(ed|ing)\b'
SPELLING+='|\bmodell(ed|ing)\b|\bsignalling\b|\bmarvellous\b'
SPELLING+='|\bfuelled\b|\blevelled\b|\btotalled\b'
SPELLING+='|\benrolment(s)?\b|\bfulfil\b|\bfulfils\b|\bfulfilment(s)?\b'
SPELLING+='|\bskilful(ly)?\b|\binstalment(s)?\b'
SPELLING+='|\bwhilst\b|\bamongst\b'

# What a line scan cannot see on one line: a test or describe title written as
# a template literal runs across several lines, and the sed rules above reach
# only the first of them. A title names the reproduction and a rerun filters on
# it, so all of its lines are an identifier.
#
# One pass writes two copies of every file, each line for line with the file on
# disk: dir/a/<idx> for the reference and history scans, and dir/b/<idx> for
# the voice and spelling scans. idx is set per file by an assignment operand
# ahead of each path.
PROSE='function blank() { print "" > a; print "" > b }
FNR == 1 {
  if (a != "") { close(a); close(b) }
  a = dir "/a/" idx; b = dir "/b/" idx
  title = 0
}
{
  line = $0
  if (title) { blank(); if (gsub(/`/, "`") % 2 == 1) title = 0; next }
  if (line ~ /(describe|test|test\.step|it)[[:space:]]*\(/ &&
      gsub(/`/, "`") % 2 == 1) { title = 1; blank(); next }
  print line > a
  print line > b
}'

# The flags the head of a file sets, one line per flag, as idx and a letter:
# P and S are the two lines of a converted document's provenance block.
HEAD_FLAGS='FNR > 20 { nextfile }
FNR <= 20 && $0 == "**Document provenance**" { print idx "\tP" }
FNR <= 20 && index($0, "- Source: `") == 1 { print idx "\tS" }'

# An operand awk would read as an assignment or as standard input.
AWK_NOT_A_PATH='^(-|[A-Za-z_][A-Za-z0-9_]*=.*)$'

# Keeps the paths on stdin that ship: those the shipping pattern matches and
# the notShipping pattern does not. An empty shipping pattern keeps them all.
ships() {
  if [ -n "$NOT_SHIPPING" ]; then
    grep -E -- "$SHIPPING" | grep -vE -- "$NOT_SHIPPING"
  else
    grep -E -- "$SHIPPING"
  fi
}

files=()
if [ "$#" -gt 0 ]; then
  files=("$@")
else
  base="$(git merge-base HEAD "origin/$MAIN_BRANCH" 2>/dev/null ||
    git merge-base HEAD "$MAIN_BRANCH")"
  exact='--find-renames=100% --diff-filter=ACMT'
  while IFS= read -r path; do
    [ -n "$path" ] && [ -f "$path" ] && files+=("$path")
  done < <(
    {
      # A file moved without an edit brings no new text, so an exact rename is
      # left out; one moved and edited reads as added and is scanned.
      [ -n "$base" ] && git -c core.quotepath=off diff --name-only $exact "$base"...HEAD
      git -c core.quotepath=off diff --name-only $exact HEAD
      git -c core.quotepath=off ls-files --others --exclude-standard
    } | sort -u | ships
  )
fi

if [ "${#files[@]}" -eq 0 ]; then
  echo "check-repo-text: nothing to scan"
  exit 0
fi

LABELS=("[reference]" "[history]  " "[voice]    " "[spelling] ")
counts=(0 0 0 0)

work="$(mktemp -d)" || exit 2
trap 'rm -rf "$work"' EXIT

# awk reads each file with the operands set ahead of it: idx, its index into
# files, and whatever else the caller passes. A path awk would read as an
# assignment or as standard input goes in from the current directory.
operands=()
add_operands() {
  local path="${files[$1]}"
  [[ "$path" =~ $AWK_NOT_A_PATH ]] && path="./$path"
  operands+=("idx=$1" "${@:2}" "$path")
}

# The files the rules apply to. A path that is not a file has nothing to read.
operands=()
for i in "${!files[@]}"; do
  skipped "${files[$i]}" && continue
  [ -f "${files[$i]}" ] && add_operands "$i"
done
declare -A flags=()
if [ "${#operands[@]}" -gt 0 ]; then
  while IFS=$'\t' read -r i flag; do
    flags[$i]+="$flag"
  done < <(awk "$HEAD_FLAGS" "${operands[@]}" 2>/dev/null || : >"$work/failed")
fi

# The files to scan, grouped by the terms rows that apply to them, which differ
# only when a row is scoped to a glob. Each group is scanned in one pass.
declare -A group_of=()
group_ban=() group_ban_cs=() group_keep=() group_members=()
for i in "${!files[@]}"; do
  path="${files[$i]}"
  skipped "$path" && continue
  [ -f "$path" ] || continue
  is_converted_document "$path" "${flags[$i]:-}" && continue
  terms_have_globs && select_terms all "$path"
  key="$TERMS_BAN"$'\001'"$TERMS_BAN_CS"$'\001'"$TERMS_KEEP"
  if [ -z "${group_of[$key]:-}" ]; then
    group_of[$key]="${#group_members[@]}"
    group_ban+=("$TERMS_BAN") group_ban_cs+=("$TERMS_BAN_CS")
    group_keep+=("$TERMS_KEEP") group_members+=("")
  fi
  g="${group_of[$key]}"
  group_members[g]+="$i "
done

# Prints idx, category and line for every line of the copies in one folder
# that carries a selected ban, minus the lines whose only match is an
# identifier the work side resolves. Run from the shard's folder.
hits_in() {
  local category="$1" folder="$2"
  terms_hit_files "$folder"/* |
    awk -F: -v category="$category" '{ sub(/^[ab]\//, "", $1)
      print $1 "\t" category "\t" $2 }'
}

# Scans one shard of a group in its own folder: scan_shard <group> <folder>
# <idx>... and prints its hits.
#
# One awk pass copies the files, one sed pass blanks the marked lines and cuts
# the identifiers the work side resolves, and one more blanks what the voice
# rules do not read, so the greps that follow see only text the rules apply
# to. sed -i reads each copy on its own, so no range or joined line carries
# from one file into the next, and every copy is line for line with its file
# on disk: the line numbers the greps report index the file the report names.
# The last pass drops NUL bytes, so a text file carrying one is still read,
# while grep -I passes over a file whose encoding it cannot read.
scan_shard() {
  local g="$1" dir="$2" i
  shift 2
  TERMS_BAN="${group_ban[$g]}" TERMS_BAN_CS="${group_ban_cs[$g]}"
  TERMS_KEEP="${group_keep[$g]}"
  mkdir -p "$dir/a" "$dir/b" && cd "$dir" || return 2
  operands=()
  for i in "$@"; do
    add_operands "$i"
  done
  # awk reads the paths from the top of the repository.
  (cd "$OLDPWD" && awk -v dir="$dir" "$PROSE" "${operands[@]}" 2>/dev/null) || return 2
  # Every file in the shard can be empty, which leaves no copies to read.
  compgen -G "a/*" >/dev/null || return 0

  # The two folders are read by different scans, so each is prepared and
  # scanned alongside the other, and each scan runs alongside its sibling.
  # The marked lines go first, then the kept identifiers, and NUL bytes last.
  local sep=$'\001' nul='s/\x00//g'
  # The first expression changes nothing; it keeps the list from being empty
  # when the config sets no marker and the table keeps no identifier.
  local -a cut=(-e 's/^$//')
  [ -n "$ALLOW_MARKER" ] && cut+=(-e "s/.*${ALLOW_MARKER}.*//")
  [ -n "$TERMS_KEEP" ] && cut+=(-e "s${sep}${TERMS_KEEP}${sep}${sep}Ig")
  (
    sed -i -E "${cut[@]}" -e "$nul" -- a/* || exit 2
    hits_in 0 a >hits.0 &
    TERMS_BAN="$HISTORY" TERMS_BAN_CS='' hits_in 1 a >hits.1 &
    wait
  ) || : >"$work/failed" &
  (
    sed -i -E "${cut[@]}" -- b/* && sed -i -E -e "$VOICE_SKIP" -e "$nul" -- b/* ||
      exit 2
    TERMS_BAN="$VOICE" TERMS_BAN_CS='' hits_in 2 b >hits.2 &
    TERMS_BAN="$SPELLING" TERMS_BAN_CS='' hits_in 3 b >hits.3 &
    wait
  ) || : >"$work/failed" &
  wait
  cat hits.[0-3] 2>/dev/null
}

# A group is cut into this many shards, each scanned alongside the others.
SHARDS="$(nproc 2>/dev/null || echo 1)"
[ "$SHARDS" -gt 4 ] && SHARDS=4

# Each hit is printed with the line as it stands on disk, file by file in the
# order given, and category by category within a file.
while IFS=$'\t' read -r i category lineno; do
  path="${files[$i]}"
  echo "${LABELS[category]} $path:$lineno:$(sed -n "${lineno}p" "$path")"
  counts[category]=$((counts[category] + 1))
done < <(
  shard=0
  for g in "${!group_members[@]}"; do
    # The shards are cut by bytes rather than by file count, since the time a
    # scan takes follows the text it reads and one file can outweigh the rest:
    # the largest file goes first, and each file joins the lightest shard.
    read -r -a ids <<<"${group_members[$g]}"
    shard_ids=() shard_bytes=()
    for ((s = 0; s < SHARDS; s++)); do shard_ids+=("") shard_bytes+=(0); done
    while read -r bytes i; do
      lightest=0
      for ((s = 1; s < SHARDS; s++)); do
        ((shard_bytes[s] < shard_bytes[lightest])) && lightest=$s
      done
      shard_ids[lightest]+="$i "
      shard_bytes[lightest]=$((shard_bytes[lightest] + bytes))
    done < <(for i in "${ids[@]}"; do printf '%s\0' "${files[$i]}"; done |
      xargs -0 stat -c '%s' -- | paste - <(printf '%s\n' "${ids[@]}") | sort -rn)
    for ((s = 0; s < SHARDS; s++)); do
      [ -n "${shard_ids[s]}" ] || continue
      shard=$((shard + 1))
      # shellcheck disable=SC2086
      (scan_shard "$g" "$work/$shard" ${shard_ids[s]} >"$work/$shard.hits" ||
        : >"$work/failed") &
    done
  done
  wait
  cat "$work"/*.hits 2>/dev/null | sort -t$'\t' -k1,1n -k2,2n -k3,3n -u
)
if [ -e "$work/failed" ]; then
  echo "check-repo-text: a pass over the copies failed, so the scan is incomplete" >&2
  exit 2
fi
references=${counts[0]}
history=${counts[1]}
voice=${counts[2]}
spelling=${counts[3]}

if [ "$references" -gt 0 ] || [ "$history" -gt 0 ] || [ "$voice" -gt 0 ] ||
   [ "$spelling" -gt 0 ]; then
  echo
  if [ "$references" -gt 0 ]; then
    echo "$references line(s) name a record the work repository does not have."
    echo "Say the fact instead of pointing at where it was written down."
  fi
  if [ "$history" -gt 0 ]; then
    echo "$history line(s) narrate what the code used to do."
    echo "State the current behavior and drop the contrast."
  fi
  if [ "$voice" -gt 0 ]; then
    echo "$voice line(s) use a word the tester writing this would not reach for."
    echo "Name the thing the word stands in for."
  fi
  if [ "$spelling" -gt 0 ]; then
    echo "$spelling line(s) spell a word the British way."
    echo "The reader on the work side writes behavior, labeled, license, gray."
  fi
  [ -z "$GUIDE" ] || echo "See $GUIDE."
  exit 1
fi

echo "check-repo-text: clean (${#files[@]} file(s))"
