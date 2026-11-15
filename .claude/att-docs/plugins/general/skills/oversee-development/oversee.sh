#!/usr/bin/env bash
# Queue and ledger state for the oversee-development skill.
#
# State lives in the main checkout, not in a worktree, so every worktree and
# every session reads the same files. The ledger is the source of truth: a
# session that dies mid-issue is resumed by reading it, not by remembering.
#
# usage:
#   oversee.sh init [--milestone <title>] [label]
#                                          build the queue from the ready open issues
#   oversee.sh refresh [--milestone <title>] [label]
#                                          rebuild it for new issues, same scope
#   oversee.sh next                        what to work, or why nothing is workable
#   oversee.sh start <issue> <branch>
#   oversee.sh adopt <issue>               claim an orphaned in-flight issue
#   oversee.sh withdraw <issue>            take back this session's own start
#   oversee.sh runs <issue>                park this session's issue while its runs go
#   oversee.sh resume <issue>              take a parked issue back
#   oversee.sh finish <issue> <done|stalled|skipped> <pr|-> <note...>
#   oversee.sh swap <issue> <from> <to>    move a label, read back
#   oversee.sh status                      counts and the tail of the ledger
#   oversee.sh blocked                     report blocked issues and deferrals
set -euo pipefail

COMMON=$(git rev-parse --git-common-dir)
MAIN=$(cd "$COMMON/.." && pwd)
DIR="$MAIN/.claude/oversee"
QUEUE="$DIR/queue.tsv"
LEDGER="$DIR/ledger.tsv"
FILTER="$DIR/filter"
OPEN="$DIR/open"

mkdir -p "$DIR"
: >> "$LEDGER"
: >> "$QUEUE"
: >> "$OPEN"

# Labels that mean the issue is not available for unattended work: already
# claimed, waiting on something outside the branch, already delivered, a
# tracker rather than work, a reference copy, or declined.
EXCLUDED='["In Progress","Blocked","Tracker","Already Done","DO NOT MERGE",'
EXCLUDED+='"question","wontfix","duplicate","invalid",'
EXCLUDED+='"needs-triage","needs-info","ready-for-human"]'

# The label an issue needs before an unattended session may take it up.
READY='"ready-for-agent"'
REQUIRED='[]'
BLOCKED_LABELS='["Blocked"]'
CONFIG="$MAIN/.claude/skills/oversee-development/extension.json"

load_filters() {
  local config
  [ -f "$CONFIG" ] || return 0
  config=$(jq -ce '
    if type != "object" or ((.queue // {}) | type != "object") then error("queue must be an object")
    else .queue // {} end
    | if (has("readyLabel") and .readyLabel != null and
          ((.readyLabel | type) != "string" or .readyLabel == "")) then error("invalid readyLabel") else . end
    | if all([.requireLabels, .excludeLabels, .blockedLabels][];
          if . == null then true elif type == "array" then all(.[]; type == "string" and . != "")
          else false end)
      then . else error("invalid label list") end
    | {ready: (if has("readyLabel") then .readyLabel else "ready-for-agent" end),
       required: (.requireLabels // []), excluded: (.excludeLabels // []), blocked: (.blockedLabels // [])}
  ' "$CONFIG") || die "invalid queue configuration: $CONFIG"
  READY=$(jq -c '.ready' <<< "$config")
  REQUIRED=$(jq -c '.required' <<< "$config")
  BLOCKED_LABELS=$(jq -c --argjson defaults "$BLOCKED_LABELS" '$defaults + .blocked | unique' <<< "$config")
  EXCLUDED=$(jq -c --argjson defaults "$EXCLUDED" '$defaults + .excluded + .blocked | unique' <<< "$config")
}

# A failed GitHub read must never be mistaken for an empty list.
read_prs() {
  gh pr list --state open --limit 1000 --json number,headRefName,body |
    jq -ce 'if type == "array" then . else error("invalid pull request list") end'
}

pr_links() {
  jq -r '.[] | .number as $pr |
    ((.headRefName // "" | scan("issue-([0-9]+)(?:-|$)") | .[0]),
     (.body // "" | scan("(?i)\\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\\s+#([0-9]+)\\b") | .[0]))
    | [., ($pr | tostring)] | @tsv'
}

# jq definitions shared by the queue read: `labels`, which lists an issue's label
# names, and the readers a milestone run uses on an issue body, then the
# reachability walk that counts an issue's dependents. Fenced code is dropped
# first. A dependency is the phrase `Depends on` or `Blocked by` anywhere in a
# line, followed by the leading run of issue references (`#5`, `#5, #6`, `#5 and
# #6`), or a line under a heading of that name that starts with an issue
# reference. A priority is a `Priority:` line or the first line under a
# `Priority` heading. References before a slash or a letter, such as
# `owner/repo#5`, name another repository and are skipped. An open native
# blocker counts as a dependency edge when ranking.
BODY_JQ='
def labels: [.labels[].name];
def refs: [match("(^|[^A-Za-z0-9_/#])#([0-9]+)"; "g") | .captures[1].string | tonumber];
def body_lines: (. // "") | gsub("\r"; "") | gsub("(?s)```.*?```"; "") | split("\n");
def prank:
  ascii_downcase
  | if . == "critical" or . == "p0" then 0
    elif . == "high" or . == "p1" then 1
    elif . == "medium" or . == "p2" then 2
    elif . == "low" or . == "p3" then 3
    else null end;
def dep_re:
  "\\b(?:depends on|blocked by)\\b\\**\\s*:?\\s*\\**\\s*"
  + "(?<run>#[0-9]+(?:\\s*(?:,\\s*(?:and\\s+)?|&|and)\\s*#[0-9]+)*)";
def live($self; $open; $trk):
  unique | map(. as $d
    | select($d != $self and any($open[]; . == $d) and (any($trk[]; . == $d) | not)));
def run_re:
  "^\\s*(?:(?:[-*+]|[0-9]+[.)])\\s+)?(?:\\[[ xX]\\]\\s+)?"
  + "(?<run>#[0-9]+(?:\\s*(?:,|&|and)\\s*#[0-9]+)*)";
def pri_re:
  "^\\s*(?:[-*]\\s+)?\\*{0,2}\\s*priority\\s*\\*{0,2}\\s*:\\s*\\*{0,2}\\s*(?<w>[A-Za-z0-9]+)";
def first_re: "^\\s*(?:[-*]\\s+)?\\*{0,2}\\s*(?<w>[A-Za-z0-9]+)";
def parse:
  reduce body_lines[] as $l ({sec: "", deps: [], pri: []};
    if ($l | test("^\\s{0,3}#{1,6}\\s")) then
      .sec = ($l | sub("^\\s*#+\\s+"; "") | sub("\\s+$"; "") | sub(":$"; "") | ascii_downcase
              | if . == "depends on" or . == "blocked by" then "dep"
                elif . == "priority" then "pri" else "" end)
    elif ($l | test("^\\s*$")) then .
    else
      .deps += [$l | match(dep_re; "gi") | .captures[0].string | refs[]]
      | .pri += [$l | capture(pri_re; "i") | .w]
      | if .sec == "dep" then .deps += [$l | capture(run_re; "i") | .run | refs[]]
        elif .sec == "pri" then .pri += [$l | capture(first_re; "i") | .w] | .sec = ""
        else . end
    end);
def tpos:
  body_lines[]
  | capture("^\\s*(?:[-+*]\\s+\\[[ xX]\\]\\s+|[0-9]+[.)]\\s+)#(?<n>[0-9]+)")
  | .n | tonumber;
def go($rev; $seen; $front):
  if ($front | length) == 0 then $seen
  else ([$front[] | ($rev[tostring] // [])[]] | unique) as $next
    | ($next - $seen) as $new
    | go($rev; $seen + $new; $new) end;
def reach($rev): . as $x | go($rev; []; [$x]) | map(select(. != $x)) | length;
'

# The oldest gh whose --json output carries an issue's blockers.
GH_MIN_MAJOR=2
GH_MIN_MINOR=94

die() { echo "$*" >&2; exit 1; }

# A string as a JSON literal, for splicing into a jq program.
jq_str() { jq -n --arg s "$1" '$s'; }

# The queue reads each issue's blockers with `gh issue list --json blockedBy`,
# which older gh versions reject. Check the version up front so an older gh
# stops the command instead.
require_gh() {
  local have
  have=$(gh --version 2>/dev/null | head -n 1) || true
  if [[ $have =~ ^gh\ version\ ([0-9]+)\.([0-9]+) ]] &&
     (( BASH_REMATCH[1] > GH_MIN_MAJOR ||
        (BASH_REMATCH[1] == GH_MIN_MAJOR && BASH_REMATCH[2] >= GH_MIN_MINOR) )); then
    return 0
  fi
  die "oversee.sh needs gh $GH_MIN_MAJOR.$GH_MIN_MINOR or newer to read issue blockers" \
      "(found: ${have:-no gh on PATH}). Install the current gh from GitHub's apt" \
      "repository, https://github.com/cli/cli/blob/trunk/docs/install_linux.md," \
      "then run this again."
}

# Holds the ledger for the rest of this process, so a command that reads the
# ledger and then appends to it cannot interleave with another session doing
# the same. The lock goes with the process.
lock_ledger() {
  exec 9>"$LEDGER.lock"
  flock -w 30 9 || die "the ledger is locked by another session; try again"
}

# The latest row for an issue, whole, or nothing.
latest_row() {
  awk -F'\t' -v i="$1" '$2==i {r=$0} END {if (r != "") print r}' "$LEDGER"
}

# The session id and process id an owner tag names, as "<sid> <pid>", with "-"
# for a part the tag lacks so the pair always reads back in order.
tag_owner() {
  local sid=- pid=-
  [[ $1 =~ session\ ([^ ]+) ]] && sid=${BASH_REMATCH[1]}
  [[ $1 =~ pid\ ([0-9]+) ]] && pid=${BASH_REMATCH[1]}
  printf '%s %s' "$sid" "$pid"
}

# An unreadable or malformed marker holds conservatively. Only a stopped
# marker for this session releases it to the usual process-liveness check.
marker_holds() {
  local sid=$1 path
  [[ $sid =~ ^[A-Za-z0-9][A-Za-z0-9_.-]{0,199}$ ]] || return 1
  path="$DIR/loops/$sid.json"
  [ -e "$path" ] || return 1
  ! jq -e --arg session "$sid" \
    'type == "object" and .session == $session and .state == "stopped"' \
    "$path" > /dev/null 2>&1
}

# The session that owns an in-flight issue. The id survives a worktree switch,
# and the process id says whether that session is still running.
SESSION=${CLAUDE_CODE_SESSION_ID:-}
owner_tag() {
  [ -n "$SESSION" ] || return 0
  printf 'session %s pid %s' "$SESSION" "${CLAUDE_PID:-}"
}

# One ledger row. Tabs and newlines in the note would corrupt the file, so the
# note is flattened before it is written.
row() {
  local issue=$1 status=$2 branch=$3 pr=$4
  shift 4
  local note
  note=$(printf '%s' "$*" | tr '\t\n' '  ')
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$issue" "$status" \
    "${branch:--}" "${pr:--}" "${note:--}" >> "$LEDGER"
}

# Sets label and milestone, in the caller's scope, from the arguments of init
# and refresh: one optional label and an optional --milestone <title>.
parse_scope() {
  while [ $# -gt 0 ]; do
    case $1 in
      --milestone)
        [ $# -ge 2 ] && [ -n "$2" ] || die "--milestone needs a title"
        milestone=$2
        shift 2 ;;
      *)
        [ -z "$label" ] || die "one label at most (got: $label $1)"
        label=$1
        shift ;;
    esac
  done
}

cmd_init() {
  local label= milestone= saved_label saved_milestone
  parse_scope "$@"
  if [ "$loop_scope" = 1 ]; then
    load_scope
    [ "$label" = "$saved_label" ] && [ "$milestone" = "$saved_milestone" ] ||
      die "init scope differs from this session's loop marker"
  fi
  build_queue "$label" "$milestone"
}

build_queue() {
  local label=$1 milestone=$2 expected_label=${3-} expected_milestone=${4-} check_scope=${5-0}
  # Serialize reads for this snapshot without blocking ledger writers.
  flock -u 9
  exec 7>"$QUEUE.lock"
  flock -w 30 7 || die "the queue is being rebuilt by another session; try again"
  lock_ledger
  if [ -s "$QUEUE" ] && [ "${OVERSEE_FORCE:-}" != 1 ]; then
    die "queue already has $(wc -l < "$QUEUE") entries; OVERSEE_FORCE=1 to rebuild"
  fi
  flock -u 9

  local want mile fields=number,title,labels,blockedBy
  want=$(jq_str "$label")
  mile=$(jq_str "$milestone")
  [ -z "$milestone" ] || fields+=,milestone,body

  # A title that opens with `<area>:` names the plugin folder or part of the
  # repository the issue touches, so the area is readable from the title alone.
  # That is what keeps two sessions off the same files without opening any
  # issue body. The fourth column flags an issue carrying an excluded label,
  # the fifth an issue the queue may serve, meaning it carries the ready label
  # and the label the queue was built for, and in a milestone run belongs to
  # it, and the sixth the open issues that block it, or `-`. The read covers
  # every open issue, so next can tell whether the issue a skipped row waited
  # on is still open. A failed read leaves the queue as it was rather than
  # writing an empty one.
  #
  # A milestone run adds three columns. The seventh is the open issues the
  # body says it waits on, or `-`. The eighth is why the issue ranks where it
  # does, or `-`. The ninth is 1 for an issue in the milestone, and init does
  # not write it to the queue. The rows come out in serve order.
  local listed
  listed=$(gh issue list --state open --limit 1000 --json "$fields" --jq "$BODY_JQ"'
    def rowof($w; $m):
      . as $i
      | labels as $have
      | ($have | any(. as $n | '"$EXCLUDED"' | index($n))) as $out
      | (('"$READY"' == null or ($have | index('"$READY"')) != null)
         and all('"$REQUIRED"'[]; . as $n | ($have | index($n)) != null)
         and ($w == "" or (($have | index($w)) != null))) as $in
      | ($i.title | if test("^[A-Za-z][A-Za-z0-9_-]{0,19}\\s*:")
                    then capture("^(?<area>[A-Za-z][A-Za-z0-9_-]{0,19})\\s*:").area
                         | ascii_downcase
                    else "-" end) as $area
      | ($i.blockedBy // {nodes: [], totalCount: 0}) as $b
      | ([$b.nodes[] | select(.state != "CLOSED") | "#\(.number)"]
         + (if $b.totalCount > ($b.nodes | length) then ["more than 50 blockers"] else [] end)
         | if length == 0 then "-" else join(" ") end) as $blockers
      | {number: $i.number, title: $i.title, area: $area, ex: $out, ok: $in,
         blockers: $blockers, trk: (($have | index("Tracker")) != null), body: $i.body,
         bnums: [$b.nodes[] | select(.state != "CLOSED") | .number],
         mem: ($m != "" and ($i.milestone.title // "") == $m)};
    '"$want"' as $w
    | '"$mile"' as $m
    | map(rowof($w; $m)) as $rows
    | if $m == "" then
        $rows[]
        | [.number, .area, .title, (if .ex then 1 else 0 end),
           (if .ok then 1 else 0 end), .blockers]
        | @tsv
      else
        ($rows | map(.number)) as $open
        | ($rows | map(select(.trk) | .number)) as $trk
        | ($rows | map(select(.mem and (.trk | not)))) as $cand
        | ($cand | map(. as $c | (.body | parse) as $p
            | {number: $c.number,
               waits: ($p.deps | live($c.number; $open; $trk)),
               edges: (($p.deps + $c.bnums) | live($c.number; $open; $trk)),
               pri: ($p.pri | map(prank) | map(select(. != null)) | .[0])})) as $info
        | (reduce $info[] as $c ({};
            reduce $c.edges[] as $d (.; .[$d | tostring] += [$c.number]))) as $rev
        | ($info | map({key: (.number | tostring), value: .}) | from_entries) as $byn
        | ($rows | map(select(.mem and .trk)) | sort_by(.number)) as $trs
        | ([$trs[] | .body | [tpos]] | add // []) as $pos
        | $rows
        | map(. as $r
            | $byn[($r.number | tostring)] as $c
            | (.ok and .mem) as $sv
            | if $c == null then
                {number, area, title, ex, sv: $sv, blockers, waits: "-", pick: "-",
                 mem, key: [1, 0, 0, 0, $r.number]}
              else
                ($r.number | reach($rev)) as $dc
                | ([range(0; ($pos | length))] | map(select($pos[.] == $r.number)) | .[0]) as $tp
                | ("unblocks \($dc) open issue" + (if $dc == 1 then "" else "s" end)) as $u
                | (["critical", "high", "medium", "low"][$c.pri // 0]) as $pn
                | ([(if $dc > 0 then $u else empty end),
                    (if $c.pri != null then "priority " + $pn else empty end),
                    (if $tp != null then "tracker position \($tp + 1)" else empty end)]
                   | if length == 0 then "lowest issue number" else join("; ") end) as $why
                | {number, area, title, ex, sv: $sv, blockers, mem,
                   waits: (if ($c.waits | length) == 0 then "-"
                           else ($c.waits | map("#\(.)") | join(" ")) end),
                   pick: ("pick: " + $why),
                   key: [0, -$dc, ($c.pri // 2), ($tp // 1000000), $r.number]}
              end)
        | sort_by(.key)
        | .[]
        | [.number, .area, .title, (if .ex then 1 else 0 end), (if .sv then 1 else 0 end),
           .blockers, .waits, .pick, (if .mem then 1 else 0 end)]
        | @tsv
      end') || return 1

  lock_ledger
  exec 8>"$DIR/loops.lock"
  flock -w 30 8 || die "the loop markers are locked by another session; try again"
  if [ "$loop_scope" = 1 ]; then
    jq -e --arg session "$SESSION" --arg label "$loop_label" --arg milestone "$loop_milestone" \
      '.session == $session and (.state == "active" or .state == "paused") and
       (.label // "") == $label and (.milestone // "") == $milestone' \
      "$marker" > /dev/null || die "loop marker changed; run again"
  elif [ -n "$SESSION" ] && [ -e "$DIR/loops/$SESSION.json" ]; then
    jq -e --arg session "$SESSION" \
      '.session == $session and .state == "stopped"' \
      "$DIR/loops/$SESSION.json" > /dev/null || die "loop marker changed; run again"
  fi
  if [ "$check_scope" = 1 ]; then
    local saved_label saved_milestone
    load_scope
    [ "$saved_label" = "$expected_label" ] && [ "$saved_milestone" = "$expected_milestone" ] ||
      die "queue scope changed during backlog read; run again"
  fi

  if [ -n "$milestone" ] &&
     ! awk -F'\t' '$9 == 1 { found = 1 } END { exit !found }' <<< "$listed"; then
    echo "no open issue in milestone \"$milestone\"" >&2
  fi

  printf '%s\n' "$listed" | awk -F'\t' 'NF { print $1 }' > "$OPEN.tmp.$$"
  mv "$OPEN.tmp.$$" "$OPEN"

  # An issue the ledger already names stays in the queue whatever its labels,
  # flags and all. In Progress drops every issue a session holds, and next
  # finds held areas and in-flight rows only through queue rows. Any other
  # issue is queued only when the queue may serve it.
  printf '%s\n' "$listed" |
  awk -F'\t' -v OFS='\t' -v ledger="$LEDGER" '
    FILENAME == ledger { known[$2]=1; next }
    # A queue file from before milestone runs has no columns 7 and 8.
    NF && (known[$1] || ($5 && !$4)) {
      print $1, $2, $3, $4, $5, $6, ($7 == "" ? "-" : $7), ($8 == "" ? "-" : $8) }' \
    "$LEDGER" - |
  # A milestone run arrives in serve order. Otherwise the oldest issue goes
  # first, so an issue lands before the later ones that build on it. Two
  # issues in one area never run together: next defers the second until the
  # first one's pull request merges.
  { if [ -n "$milestone" ]; then cat; else sort -t$'\t' -k1,1n; fi; } > "$QUEUE.tmp.$$"

  mv "$QUEUE.tmp.$$" "$QUEUE"
  if [ "$loop_scope" != 1 ]; then
    printf '%s\n%s\n' "$label" "$milestone" > "$FILTER"
  fi
  flock -u 8
  flock -u 7
  echo "queued $(wc -l < "$QUEUE") issues -> $QUEUE"
}

# Sets saved_label and saved_milestone, in the caller's scope, to the label and
# milestone the queue was built for: one per line of the filter file. Either
# may be empty.
load_scope() {
  saved_label= saved_milestone=
  if [ "$loop_scope" = 1 ]; then
    saved_label=$loop_label
    saved_milestone=$loop_milestone
  elif [ -f "$FILTER" ]; then
    {
      IFS= read -r saved_label || true
      IFS= read -r saved_milestone || true
    } < "$FILTER"
  fi
}

# A rebuild scoped to the label and milestone the queue was built with. A
# label or milestone given here replaces the saved one; the other is kept.
cmd_refresh() {
  local label= milestone= saved_label saved_milestone
  parse_scope "$@"
  load_scope
  if [ "$loop_scope" = 1 ]; then
    [ -z "$label" ] || [ "$label" = "$saved_label" ] ||
      die "refresh scope differs from this session's loop marker"
    [ -z "$milestone" ] || [ "$milestone" = "$saved_milestone" ] ||
      die "refresh scope differs from this session's loop marker"
  fi
  [ -n "$label" ] || label=$saved_label
  [ -n "$milestone" ] || milestone=$saved_milestone
  OVERSEE_FORCE=1 build_queue "$label" "$milestone" "$saved_label" "$saved_milestone" 1
}

cmd_next() {
  # Selection needs current issues and pull requests; neither failed read can
  # establish that an issue is safe to start.
  local open_prs prs links saved_label saved_milestone scoped=0 scope_name=milestone
  local sid held_sessions=" "
  flock -u 9
  prs=$(read_prs) || die "next: the pull request read failed"
  open_prs=$(jq -r '.[].number' <<< "$prs" | tr '\n' ' ')
  links=$(pr_links <<< "$prs") || die "next: invalid pull request data"
  lock_ledger
  cmd_refresh > /dev/null || die "next: the backlog read failed"
  load_scope
  if [ -n "$saved_milestone" ]; then
    scoped=1
  elif [ -n "$saved_label" ]; then
    scoped=1
    scope_name=label
  fi

  exec 8>"$DIR/loops.lock"
  flock -w 30 8 || die "the loop markers are locked by another session; try again"
  while IFS= read -r sid; do
    if marker_holds "$sid"; then held_sessions+="$sid "; fi
  done < <(awk -F'\t' 'match($6, /session [^ ]+/) {
    print substr($6, RSTART + 8, RLENGTH - 8)
  }' "$LEDGER" | sort -u)

  # The ledger is matched by name rather than by FNR==NR: on the first run it is
  # empty, and an empty first file makes FNR==NR true for every queue row.
  awk -F'\t' -v open_prs=" $open_prs " -v links="$links" -v ledger="$LEDGER" -v openf="$OPEN" \
    -v me="$SESSION" -v scoped="$scoped" -v scope_name="$scope_name" -v held_sessions="$held_sessions" '
    # A skipped row is served again once what stopped it has cleared. A start
    # refused on a label or a closed state has cleared when the queue row is
    # open and carries no excluded label. Any other skip has cleared when every
    # issue or pull request its note names is closed. A name is a number of
    # two to four digits other than the issue itself, so run and process ids
    # are not read as blockers. A skip whose note names nothing stays skipped.
    function cleared(n,   t, m, refs) {
      if (note[n] ~ /^not workable at start:/) return 1
      t = note[n]
      refs = 0
      while (match(t, /[0-9]+/)) {
        m = substr(t, RSTART, RLENGTH)
        t = substr(t, RSTART + RLENGTH)
        if (length(m) < 2 || length(m) > 4 || m == n) continue
        refs++
        if ((m in open) || index(open_prs, " " m " ") > 0) return 0
      }
      return refs > 0
    }
    FILENAME == openf { open[$1]=1; next }
    FILENAME == ledger { status[$2]=$3; branch[$2]=$4; pr[$2]=$5; note[$2]=$6; next }
    {
      line[FNR]=$1 "\t" $2 "\t" $3; num[FNR]=$1; area[FNR]=$2
      excluded[FNR]=($4 == 1); servable[FNR]=($5 == 1); blockers[FNR]=$6
      waits[FNR]=($7 == "" ? "-" : $7); pick[FNR]=($8 == "" ? "-" : $8)
      total=FNR
    }
    END {
      count = split(links, pairs, "\n")
      for (j = 1; j <= count; j++) {
        split(pairs[j], pair, "\t")
        if (pair[1] != "" && !(pair[1] in linked)) linked[pair[1]] = pair[2]
      }
      # Each session works one issue at a time; other sessions hold their own.
      # An in-flight row is mine when it carries my session id, orphaned when
      # its owner process has exited, and live elsewhere otherwise. A row with
      # no owner predates the tags and counts as live elsewhere.
      for (i=1; i<=total; i++) {
        n = num[i]
        if (status[n] != "start" && status[n] != "runs") continue
        sid = ""; pid = ""
        if (match(note[n], /session [^ ]+/)) sid = substr(note[n], RSTART + 8, RLENGTH - 8)
        if (match(note[n], /pid [0-9]+/)) pid = substr(note[n], RSTART + 4, RLENGTH - 4)
        if (sid != "" && sid == me) owner[n] = "mine"
        else if (index(held_sessions, " " sid " ") > 0) owner[n] = "elsewhere"
        else if (pid != "" && system("ps -p " pid " >/dev/null") != 0) owner[n] = "orphan"
        else owner[n] = "elsewhere"
      }

      # My own unfinished start row outranks everything: resume it, never
      # restart it. An orphaned one comes next, for any session to adopt. In a
      # milestone run an orphan is adopted only while it belongs to the
      # milestone, which servable records.
      for (pass = 1; pass <= 2; pass++)
        for (i=1; i<=total; i++) {
          n = num[i]
          if (pass == 2 && scoped && !servable[i]) continue
          if (pass == 1 && status[n] == "runs") continue
          if (owner[n] == (pass == 1 ? "mine" : "orphan")) {
            print "INFLIGHT\t" line[i] "\tbranch " branch[n] "\t" owner[n]
            exit
          }
        }

      # A finished issue whose pull request is still open still owns its area,
      # and so does an issue in flight in another session.
      for (i=1; i<=total; i++) {
        n = num[i]
        if (status[n] == "done" && pr[n] != "-" && index(open_prs, " " pr[n] " ") > 0)
          held[area[i]] = "PR #" pr[n]
        # An orphan a milestone run does not adopt is printed like an issue in
        # flight elsewhere, and holds its area while its branch is open.
        # An issue of mine parked on its runs is printed, and holds its area, so
        # an issue in the same area waits while the runs go.
        if (owner[n] == "mine" && status[n] == "runs") {
          print "RUNS\t" line[i] "\tbranch " branch[n]
          busy++
          if (area[i] != "-") held[area[i]] = "issue " n " waiting on its runs"
        }
        skipped_orphan = (owner[n] == "orphan" && scoped && !servable[i])
        if (owner[n] == "elsewhere" || skipped_orphan) {
          print "ELSEWHERE\t" line[i] "\tbranch " branch[n]
          busy++
          why = skipped_orphan ? " orphaned outside the " scope_name : " in another session"
          if (area[i] != "-") held[area[i]] = "issue " n why
        }
      }

      for (i=1; i<=total; i++) {
        # A withdrawn start leaves the issue as unworked as no row at all, and
        # so does a skip that has cleared.
        n = num[i]
        s = status[n]
        if (s == "skipped" && !excluded[i] && cleared(n)) s = ""
        if (s != "" && s != "withdrawn") continue
        # An issue the queue may not serve is passed over without a line: most
        # of a backlog can be in that state, and a line for each would bury
        # the ones that matter. An open blocker is the exception, since it
        # clears by itself and the reader wants to know what is waited on.
        if (!servable[i] || excluded[i]) continue
        if (n in linked) {
          print "DEFER\t" line[i] "\topen pull request #" linked[n]
          deferred++
          continue
        }
        if (blockers[i] != "-") {
          print "DEFER\t" line[i] "\tblocked by " blockers[i]
          deferred++
          continue
        }
        # An issue whose body says it waits on open issues waits until they
        # close. A dependency whose pull request is still open is named, since
        # the dependency stays open until that pull request merges.
        if (waits[i] != "-") {
          w = "waits on " waits[i]
          prs = ""; npr = 0
          cnt = split(waits[i], parts, " ")
          for (k = 1; k <= cnt; k++) {
            d = substr(parts[k], 2)
            if (status[d] == "done" && pr[d] != "-" && index(open_prs, " " pr[d] " ") > 0) {
              prs = prs (npr++ ? ", " : "") pr[d]
            }
          }
          if (npr > 0) w = w " (pull request" (npr > 1 ? "s " : " ") prs " open)"
          print "DEFER\t" line[i] "\t" w
          deferred++
          continue
        }
        if (area[i] != "-" && area[i] in held) {
          print "DEFER\t" line[i] "\tarea held by " held[area[i]]
          deferred++
          continue
        }
        print "NEXT\t" line[i] (pick[i] != "-" ? "\t" pick[i] : "")
        exit
      }
      print ((deferred || busy) ? "BLOCKED" : "EMPTY")
    }' "$OPEN" "$LEDGER" "$QUEUE"
  flock -u 8
}

cmd_blocked() {
  local saved_label saved_milestone fields=number,title,labels listed next issue title last status note comment label mile
  load_scope
  [ -z "$saved_milestone" ] || fields+=,milestone
  label=$(jq_str "$saved_label")
  mile=$(jq_str "$saved_milestone")
  next=$(cmd_next) || return 1
  flock -u 9
  listed=$(gh issue list --state open --limit 1000 --json "$fields" --jq '
    map([.labels[].name] as $have
      | select(($have | index("Tracker")) == null)
      | select(any('"$BLOCKED_LABELS"'[]; . as $n | ($have | index($n)) != null))
      | select(all('"$EXCLUDED"'[]; . as $n |
          (('"$BLOCKED_LABELS"' | index($n)) != null) or (($have | index($n)) == null)))
      | select('"$READY"' == null or ($have | index('"$READY"')) != null)
      | select(all('"$REQUIRED"'[]; . as $n | ($have | index($n)) != null))
      | select('"$label"' == "" or ($have | index('"$label"')) != null)
      | select('"$mile"' == "" or (.milestone.title // "") == '"$mile"'))
    | .[] | [.number, .title] | @tsv') || die "blocked: the backlog read failed"
  while IFS=$'\t' read -r issue title; do
    [ -n "$issue" ] || continue
    last=$(latest_row "$issue")
    status=$(cut -f3 <<< "$last")
    note=$(cut -f6 <<< "$last")
    if [ "$status" != stalled ] || [ -z "$note" ] || [ "$note" = - ]; then
      comment=$(gh issue view "$issue" --json comments --jq '(.comments[-1].body // "") | split("\n")[0]') ||
        die "blocked: could not read comments for issue $issue"
      note=${comment:-no reason recorded}
    fi
    printf 'BLOCKED\t%s\t%s\t%s\n' "$issue" "$title" "$note"
  done <<< "$listed"
  printf '%s\n' "$next" | awk '/^(DEFER|RUNS)\t/'
}

# The queue is a snapshot from init, and labels move after it: another session
# claims an issue, or the user blocks or closes one. So the labels are read
# again here. An issue no longer workable gets a skipped row, which next passes
# over, and start fails so the caller asks next again.
cmd_start() {
  local issue=$1 branch=$2 why saved_label saved_milestone m label pick note prs linked
  local fields=state,labels,blockedBy
  if [ "$loop_scope" = 1 ]; then
    cmd_refresh > /dev/null || die "start: the backlog read failed"
  fi
  load_scope
  [ -z "$saved_milestone" ] || fields+=,milestone
  m=$(jq_str "$saved_milestone")
  label=$(jq_str "$saved_label")
  pick=$(awk -F'\t' -v i="$issue" '$1 == i { print $8 }' "$QUEUE")
  flock -u 9
  why=$(gh issue view "$issue" --json "$fields" --jq '
    [.labels[].name] as $have
    | ('"$EXCLUDED"' | map(select(. as $n | $have | index($n)))) as $hit
    | ([.blockedBy.nodes[]? | select(.state != "CLOSED") | "#\(.number)"]) as $open
    | '"$m"' as $m
    | if .state != "OPEN" then "state \(.state)"
      elif ($hit | length) > 0 then "labeled \($hit | join(", "))"
      elif '"$READY"' != null and ($have | index('"$READY"')) == null then "not labeled " + '"$READY"'
      elif (['"$REQUIRED"'[] | select(. as $n | ($have | index($n)) == null)] | length) > 0
        then "missing required label"
      elif '"$label"' != "" and ($have | index('"$label"')) == null then "not labeled " + '"$label"'
      elif $m != "" and (.milestone.title // "") != $m then "not in milestone \($m)"
      elif ($open | length) > 0 then "blocked by \($open | join(" "))"
      elif .blockedBy.totalCount > (.blockedBy.nodes | length) then "more than 50 blockers"
      else "" end')
  prs=$(read_prs) || die "start: the pull request read failed"
  linked=$(pr_links <<< "$prs" | awk -F'\t' -v n="$issue" '$1 == n { print $2; exit }')
  [ -z "$linked" ] || die "issue $issue has open pull request #$linked; run next again"
  lock_ledger
  exec 8>"$DIR/loops.lock"
  flock -w 30 8 || die "the loop markers are locked by another session; try again"
  if [ "$loop_scope" = 1 ]; then
    jq -e --arg session "$SESSION" --arg label "$loop_label" --arg milestone "$loop_milestone" \
      '.session == $session and (.state == "active" or .state == "paused") and
       (.label // "") == $label and (.milestone // "") == $milestone' \
      "$marker" > /dev/null || die "loop marker changed; run next again"
  fi

  # The holder check comes first: a holder's own In Progress label must not
  # turn its start row into a skipped one.
  refuse_if_held "$issue"
  if [ -n "$why" ]; then
    row "$issue" skipped - - "not workable at start: $why"
    die "issue $issue is not workable ($why); recorded as skipped, run next again"
  fi
  # The reason the issue ranked first sits in its queue row. It goes into the
  # start row, so a resumed or adopted issue still carries it.
  note=$(owner_tag)
  [ -z "$pick" ] || [ "$pick" = - ] || note+="${note:+; }$pick"
  row "$issue" start "$branch" - "$note"
  flock -u 8
}

# Two sessions can both read NEXT for one issue and both call start. The second
# one finds the first one's row here, under the lock, and stands down. A row
# whose owner process has exited is an orphan, which adopt claims rather than
# start, and a row with no owner tag predates the tags and holds nothing. A row
# naming a session but no process counts as live, the same as next reads it.
refuse_if_held() {
  local issue=$1 last status note sid pid
  last=$(latest_row "$issue")
  [ -n "$last" ] || return 0
  status=$(cut -f3 <<< "$last")
  note=$(cut -f6 <<< "$last")
  [ "$status" = start ] || [ "$status" = runs ] || return 0
  read -r sid pid <<< "$(tag_owner "$note")"
  # A parked issue of this session is taken back with resume, which checks that
  # no other issue is in flight; a start would overwrite the park.
  [ "$status" != runs ] || [ -z "$SESSION" ] || [ "$sid" != "$SESSION" ] ||
    die "issue $issue is parked on its runs; use oversee.sh resume $issue"
  [ "$sid" != - ] && [ "$sid" != "$SESSION" ] || return 0
  ! marker_holds "$sid" || die "issue $issue is held by loop session $sid; run next again"
  [ "$pid" = - ] || ps -p "$pid" > /dev/null || return 0
  die "issue $issue is held by session $sid (pid $pid); run next again"
}

# Claims an orphaned in-flight issue for this session. Its labels are not read
# again: the dead worker left `In Progress` on it, and that label is this
# session's claim now.
cmd_adopt() {
  local issue=$1 branch last pick= sid pid
  lock_ledger
  exec 8>"$DIR/loops.lock"
  flock -w 30 8 || die "the loop markers are locked by another session; try again"
  branch=$(awk -F'\t' -v i="$issue" '$2==i {s=$3; b=$4} END {if (s == "start" || s == "runs") print b}' "$LEDGER")
  [ -n "$branch" ] || die "issue $issue is not in flight; nothing to adopt"
  last=$(latest_row "$issue")
  read -r sid pid <<< "$(tag_owner "$(cut -f6 <<< "$last")")"
  if [ "$sid" != - ] && [ "$sid" != "$SESSION" ]; then
    if marker_holds "$sid" || [ "$pid" = - ] || ps -p "$pid" > /dev/null; then
      die "issue $issue is held by session $sid; cannot adopt"
    fi
  fi
  [[ $(cut -f6 <<< "$last") =~ (pick:\ .*) ]] && pick=${BASH_REMATCH[1]}
  row "$issue" start "$branch" - "$(owner_tag) adopted${pick:+; $pick}"
  flock -u 8
}

# Takes back a start this session wrote, when the session cannot work the
# issue after all, without recording anything about the issue itself. The row
# before the start comes back as it was, owner included, or the issue goes back
# to the queue when the start was its first row.
cmd_withdraw() {
  local issue=$1 last prev sid st branch pr note
  lock_ledger
  last=$(latest_row "$issue")
  [ "$(cut -f3 <<< "$last")" = start ] || die "issue $issue has no start row to withdraw"
  read -r sid _ <<< "$(tag_owner "$(cut -f6 <<< "$last")")"
  [ -n "$SESSION" ] && [ "$sid" = "$SESSION" ] ||
    die "issue $issue was started by session $sid, not this one"
  prev=$(awk -F'\t' -v i="$issue" '$2==i {p=r; r=$0} END {if (p != "") print p}' "$LEDGER")
  if [ -z "$prev" ]; then
    row "$issue" withdrawn - - "$(owner_tag)"
    return
  fi
  IFS=$'\t' read -r _ _ st branch pr note <<< "$prev"
  row "$issue" "$st" "$branch" "$pr" "$note"
}

# Parks this session's in-flight issue while its test runs go, so next serves a
# different issue and the parked one keeps its area held. The row carries the
# branch, the owner and the pick reason of the start row it follows.
cmd_runs() {
  local issue=$1 last sid pid note pick= branch
  lock_ledger
  last=$(latest_row "$issue")
  [ "$(cut -f3 <<< "$last")" = start ] || die "issue $issue is not being worked; nothing to park"
  note=$(cut -f6 <<< "$last")
  read -r sid pid <<< "$(tag_owner "$note")"
  [ -n "$SESSION" ] && [ "$sid" = "$SESSION" ] ||
    die "issue $issue was started by session $sid, not this one"
  branch=$(cut -f4 <<< "$last")
  [[ $note =~ (pick:\ .*) ]] && pick=${BASH_REMATCH[1]}
  row "$issue" runs "$branch" - "$(owner_tag)${pick:+; $pick}"
}

# Takes a parked issue back. One issue is worked at a time per session, so it
# refuses while another issue of this session is in flight.
cmd_resume() {
  local issue=$1 last sid pid note pick= branch other
  lock_ledger
  last=$(latest_row "$issue")
  [ "$(cut -f3 <<< "$last")" = runs ] || die "issue $issue is not waiting on runs"
  note=$(cut -f6 <<< "$last")
  read -r sid pid <<< "$(tag_owner "$note")"
  [ -n "$SESSION" ] && [ "$sid" = "$SESSION" ] ||
    die "issue $issue was parked by session $sid, not this one"
  other=$(awk -F'\t' -v me="$SESSION" '
    { status[$2] = $3; note[$2] = $6 }
    END { for (i in status)
            if (status[i] == "start" && index(note[i], "session " me " ") > 0) { print i; exit } }' \
    "$LEDGER")
  [ -z "$other" ] || die "issue $other is being worked; park or finish it first"
  branch=$(cut -f4 <<< "$last")
  [[ $note =~ (pick:\ .*) ]] && pick=${BASH_REMATCH[1]}
  row "$issue" start "$branch" - "$(owner_tag) resumed${pick:+; $pick}"
}

# Moves a label on an issue through the REST endpoints, since `gh issue edit`
# fails here on the classic projects lookup, and reads the labels back. The
# new label must already exist in the repository; it is never created.
cmd_swap() {
  local issue=$1 from=$2 to=$3 have
  gh api -X DELETE "repos/{owner}/{repo}/issues/$issue/labels/${from// /%20}" > /dev/null ||
    true
  have=$(gh api -X POST "repos/{owner}/{repo}/issues/$issue/labels" -f "labels[]=$to" \
    --jq '[.[].name] | join(",")')
  case ",$have," in
    *",$to,"*) ;;
    *) die "label $to did not land on issue $issue (has: $have)" ;;
  esac
  case ",$have," in
    *",$from,"*) die "label $from is still on issue $issue (has: $have)" ;;
  esac
  echo "$have"
}

cmd_status() {
  local saved_label saved_milestone
  awk -F'\t' '
    { status[$2]=$3 }
    END { for (i in status) n[status[i]]++
          printf "done %d  stalled %d  skipped %d  in-flight %d  on runs %d\n",
                 n["done"], n["stalled"], n["skipped"], n["start"], n["runs"] }' "$LEDGER"
  echo "queued $(wc -l < "$QUEUE") total"
  load_scope
  if [ -n "$saved_milestone" ]; then
    echo "scope: milestone \"$saved_milestone\"${saved_label:+, label $saved_label}"
  elif [ -n "$saved_label" ]; then
    echo "scope: label $saved_label"
  fi
  tail -n 8 "$LEDGER"
}

# Queue snapshots and the ledger use a separate lock from loop markers.
# Each loop keeps its own snapshot; the marker supplies its scope.
loop_scope=0 loop_label= loop_milestone=
case "${1:-}" in
  init|refresh|next|blocked|start|status)
    lock_ledger
    if [ -n "$SESSION" ]; then
      [[ $SESSION =~ ^[A-Za-z0-9][A-Za-z0-9_.-]{0,199}$ ]] ||
        die "invalid session ID"
      exec 8>"$DIR/loops.lock"
      flock -w 30 8 || die "the loop markers are locked by another session; try again"
      marker="$DIR/loops/$SESSION.json"
      if [ -f "$marker" ]; then
        scope=$(jq -ce --arg session "$SESSION" '
          if type != "object" or .session != $session or
             ((.state | IN("active", "paused", "stopped")) | not) or
             ((.label != null and (.label | type != "string")) or
              (.milestone != null and (.milestone | type != "string")))
          then error("invalid loop marker")
          else {state, label: (.label // ""), milestone: (.milestone // "")} end
        ' "$marker") || die "invalid loop marker: $marker"
        if [ "$(jq -r '.state' <<< "$scope")" != stopped ]; then
          loop_scope=1
          loop_label=$(jq -r '.label' <<< "$scope")
          loop_milestone=$(jq -r '.milestone' <<< "$scope")
          QUEUE="$DIR/loops/$SESSION.queue.tsv"
          OPEN="$DIR/loops/$SESSION.open"
          : >> "$QUEUE"
          : >> "$OPEN"
        fi
      fi
      flock -u 8
    fi
    ;;
esac

case "${1:-}" in
  init|refresh|next|start|blocked) require_gh; load_filters ;;
esac

case "${1:-}" in
  init)   shift; cmd_init "$@" ;;
  refresh) shift; cmd_refresh "$@" ;;
  next)   cmd_next ;;
  blocked) cmd_blocked ;;
  start)  [ $# -ge 3 ] || die "usage: oversee.sh start <issue> <branch>"
          cmd_start "$2" "$3" ;;
  adopt)  [ $# -ge 2 ] || die "usage: oversee.sh adopt <issue>"
          cmd_adopt "$2" ;;
  withdraw) [ $# -ge 2 ] || die "usage: oversee.sh withdraw <issue>"
          cmd_withdraw "$2" ;;
  runs)   [ $# -ge 2 ] || die "usage: oversee.sh runs <issue>"
          cmd_runs "$2" ;;
  resume) [ $# -ge 2 ] || die "usage: oversee.sh resume <issue>"
          cmd_resume "$2" ;;
  swap)   [ $# -ge 4 ] || die "usage: oversee.sh swap <issue> <from> <to>"
          cmd_swap "$2" "$3" "$4" ;;
  finish) [ $# -ge 4 ] || die "usage: oversee.sh finish <issue> <status> <pr|-> <note>"
          issue=$2 st=$3 pr=$4; shift 4
          lock_ledger
          # Carry the branch from this issue's start row: a stalled issue is
          # picked up again later, and its branch is the only way back to it.
          branch=$(awk -F'\t' -v i="$issue" '$2==i && $4!="-" {b=$4} END {print (b?b:"-")}' \
                   "$LEDGER")
          row "$issue" "$st" "$branch" "$pr" "$@" ;;
  status) cmd_status ;;
  *)      die "usage: oversee.sh" \
              "init|refresh|next|blocked|start|adopt|withdraw|runs|resume|swap|finish|status" ;;
esac
