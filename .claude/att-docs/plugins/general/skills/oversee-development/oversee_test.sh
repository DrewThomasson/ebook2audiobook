#!/usr/bin/env bash
# Cases for oversee.sh. A stub gh reads issues and pull requests from files in the sandbox,
# and the queue and ledger live in a throwaway git repository, so nothing real is touched.
# usage: bash oversee_test.sh
set -uo pipefail

command -v jq > /dev/null || { echo "jq is required"; exit 1; }

HERE="$(cd "$(dirname "$0")" && pwd)"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
mkdir -p "$SANDBOX/bin" "$SANDBOX/repo"
export PATH="$SANDBOX/bin:$PATH"
export FIXTURES="$SANDBOX/fixtures"
mkdir -p "$FIXTURES"

# gh stub: `issue list` and `pr list` read the fixture files, `issue view <n>` one issue, and
# `api` moves labels in a per-issue file. --jq is applied with jq, as gh does. `--version`
# prints GH_VERSION, so a case can run oversee.sh against an older gh.
cat > "$SANDBOX/bin/gh" <<'STUB'
#!/usr/bin/env bash
set -o pipefail
jqx=.
args=("$@")
for ((i = 0; i < ${#args[@]}; i++)); do
  [ "${args[i]}" = --jq ] && jqx=${args[i + 1]}
done
if [ "$1" = --version ]; then
  printf 'gh version %s (2026-01-01)\nhttps://github.com/cli/cli/releases/tag/v%s\n' \
    "${GH_VERSION:-2.94.0}" "${GH_VERSION:-2.94.0}"
  exit 0
fi
case "$1 $2" in
  "issue list")
    if [ -n "${DELAY_ISSUES:-}" ]; then
      : > "$DELAY_ISSUES/entered"
      for ((n = 0; n < 500; n++)); do
        [ -e "$DELAY_ISSUES/release" ] && break
        sleep 0.02
      done
      [ -e "$DELAY_ISSUES/release" ] || exit 1
    fi
    [ "${FAIL_ISSUES:-}" != 1 ] && jq -r "$jqx" "$FIXTURES/issues.json" ;;
  "pr list") [ "${FAIL_PRS:-}" != 1 ] && jq -r "$jqx" "$FIXTURES/prs.json" ;;
  "issue view") [ "${FAIL_VIEW:-}" != 1 ] && jq -c ".[] | select(.number == $3)" "$FIXTURES/issues.json" | jq -r "$jqx" ;;
  "api "*)
    method=GET; for a in "$@"; do [ "$a" = DELETE ] && method=DELETE; [ "$a" = POST ] && method=POST; done
    url=; for a in "$@"; do [[ $a == repos/* ]] && url=$a; done
    n=${url#*/issues/}; n=${n%%/*}
    f="$FIXTURES/labels-$n"; touch "$f"
    if [ "$method" = DELETE ]; then
      name=${url##*/labels/}; name=${name//%20/ }
      grep -vxF "$name" "$f" > "$f.new"; mv "$f.new" "$f"
    else
      for a in "$@"; do [[ $a == labels\[\]=* ]] && echo "${a#'labels[]='}" >> "$f"; done
      jq -Rn '[inputs | {name: .}]' < "$f" | jq -r "$jqx"
    fi ;;
esac
STUB
chmod +x "$SANDBOX/bin/gh"

git -C "$SANDBOX/repo" init -q
cd "$SANDBOX/repo" || exit 1
OS="$HERE/oversee.sh"
LEDGER="$SANDBOX/repo/.claude/oversee/ledger.tsv"
fails=0

check() {
  if [ "$1" = "$2" ]; then echo "ok   $3"; else
    echo "FAIL $3: got [$1], wanted [$2]"; fails=$((fails + 1)); fi
}
# usage: as <session> <pid> <args...>; runs oversee.sh as one conductor session.
as() { local s=$1 p=$2; shift 2; CLAUDE_CODE_SESSION_ID=$s CLAUDE_PID=$p bash "$OS" "$@"; }
first() { head -n 1 | cut -f1-2; }

echo '[
 {"number":5,"title":"voice: first","state":"OPEN","labels":[{"name":"enhancement"},{"name":"ready-for-agent"}]},
 {"number":6,"title":"voice: second","state":"OPEN","labels":[{"name":"ready-for-agent"}]},
 {"number":7,"title":"Install a thing","state":"OPEN","labels":[{"name":"ready-for-agent"}]},
 {"number":8,"title":"voice: waits","state":"OPEN","labels":[{"name":"Blocked"},{"name":"ready-for-agent"}]},
 {"number":9,"title":"att-docs: other area","state":"OPEN","labels":[{"name":"In Progress"},{"name":"ready-for-agent"}]},
 {"number":10,"title":"Tracking","state":"OPEN","labels":[{"name":"Tracker"},{"name":"ready-for-agent"}]},
 {"number":11,"title":"Not yet looked at","state":"OPEN","labels":[{"name":"needs-triage"}]},
 {"number":12,"title":"Waits on the reporter","state":"OPEN","labels":[{"name":"needs-info"}]},
 {"number":13,"title":"Needs a person","state":"OPEN","labels":[{"name":"ready-for-human"}]},
 {"number":14,"title":"Ready for an agent","state":"OPEN","labels":[{"name":"ready-for-agent"}]},
 {"number":15,"title":"Never triaged","state":"OPEN","labels":[{"name":"enhancement"}]},
 {"number":16,"title":"Waits on a blocker","state":"OPEN","labels":[{"name":"ready-for-agent"}],
  "blockedBy":{"nodes":[{"number":99,"state":"OPEN"},{"number":97}],"totalCount":2}},
 {"number":17,"title":"Blocker is closed","state":"OPEN","labels":[{"name":"ready-for-agent"}],
  "blockedBy":{"nodes":[{"number":98,"state":"CLOSED"}],"totalCount":1}}
]' > "$FIXTURES/issues.json"
echo '[]' > "$FIXTURES/prs.json"
LIVE=$$

# --- the queue
as A "$LIVE" init > /dev/null
check "$(cut -f1 "$SANDBOX/repo/.claude/oversee/queue.tsv" | tr '\n' ' ')" "5 6 7 14 16 17 " \
  "the queue holds the issues labeled ready-for-agent, oldest first, and drops excluded labels"
check "$(as A "$LIVE" next | first)" "NEXT	5" "next serves the oldest issue"
check "$(cut -f2 "$SANDBOX/repo/.claude/oversee/queue.tsv" | tr '\n' ' ')" "voice voice - - - - " \
  "an area is the word before the colon in the title"

# --- the gate and blockers
QUEUE="$SANDBOX/repo/.claude/oversee/queue.tsv"
check "$(awk -F'\t' '$1 == 15' "$QUEUE" | wc -l)" 0 "an issue without ready-for-agent is not queued"
check "$(awk -F'\t' '$1 == 16 {print $6}' "$QUEUE")" "#99 #97" \
  "the queue records an open blocker, and a blocker with no state counts as open"
check "$(awk -F'\t' '$1 == 17 {print $6}' "$QUEUE")" "-" "a closed blocker blocks nothing"
as A "$LIVE" init enhancement > /dev/null 2>&1
check "$?" 1 "init refuses to rebuild a queue that already has entries"
OVERSEE_FORCE=1 as A "$LIVE" init enhancement > /dev/null
check "$(cut -f1 "$QUEUE" | tr '\n' ' ')" "5 " \
  "a label argument needs both that label and ready-for-agent"
OVERSEE_FORCE=1 as A "$LIVE" init > /dev/null
check "$(cut -f1 "$QUEUE" | tr '\n' ' ')" "5 6 7 14 16 17 " "an init with no label widens it again"

# --- two sessions
as A "$LIVE" start 5 feat/issue-5-first
check "$?" 0 "start records the issue"
as B "$LIVE" start 5 feat/issue-5-other 2> /dev/null
check "$?" 1 "a second session cannot start an issue held by a live one"
check "$(as A "$LIVE" next | first)" "INFLIGHT	5" "the holder is told to resume its issue"
out=$(as B "$LIVE" next)
check "$(grep -c '^ELSEWHERE	5' <<< "$out")" 1 "another session sees the issue as in flight elsewhere"
check "$(grep -c '^DEFER	6.*area held by issue 5' <<< "$out")" 1 "an issue in the same area is deferred"
check "$(grep -c '^NEXT	7' <<< "$out")" 1 "an issue with no area is served"

# --- finish and an open pull request
as A "$LIVE" finish 5 done 20 "ready"
echo '[{"number":20}]' > "$FIXTURES/prs.json"
out=$(as B "$LIVE" next)
check "$(grep -c '^DEFER	6.*area held by PR #20' <<< "$out")" 1 \
  "a finished issue's open pull request holds its area"
echo '[]' > "$FIXTURES/prs.json"
check "$(as B "$LIVE" next | first)" "NEXT	6" "the area is free once the pull request closes"

# --- a start that is no longer workable
echo '[{"number":6,"title":"voice: second","state":"OPEN","labels":[{"name":"Blocked"},{"name":"ready-for-agent"}]},
 {"number":7,"title":"Install a thing","state":"OPEN","labels":[{"name":"ready-for-agent"}]}]' > "$FIXTURES/issues.json"
as B "$LIVE" start 6 feat/issue-6-second 2> /dev/null
check "$?" 1 "start refuses an issue that picked up an excluded label"
check "$(tail -n 1 "$LEDGER" | cut -f2-3)" "6	skipped" "and records it as skipped"
check "$(as B "$LIVE" next | first)" "NEXT	7" "next passes over it"

# --- withdraw
as B "$LIVE" start 7 feat/issue-7-install
as B "$LIVE" withdraw 7
check "$(as B "$LIVE" next | first)" "NEXT	7" "a withdrawn start puts the issue back in the queue"
as A "$LIVE" withdraw 7 2> /dev/null
check "$?" 1 "withdraw refuses when the issue has no start row"

# --- an orphan
sleep 0 & DEAD=$!; wait "$DEAD"
as C "$DEAD" start 7 feat/issue-7-install
check "$(as A "$LIVE" next | first)" "INFLIGHT	7" "a start whose process has exited is served as an orphan"
check "$(as A "$LIVE" next | cut -f6)" "orphan" "and is marked orphan"
as A "$LIVE" adopt 7
check "$(as A "$LIVE" next | cut -f6)" "mine" "adopt makes the issue the session's own"

# --- label swap
printf 'In Progress\nenhancement\n' > "$FIXTURES/labels-7"
check "$(as A "$LIVE" swap 7 "In Progress" Blocked)" "enhancement,Blocked" \
  "swap moves a label and reads the labels back"
as A "$LIVE" finish 7 done - "ok"
check "$(as A "$LIVE" next | first)" "EMPTY" "next reports EMPTY when nothing is left"

# --- an issue that waits on a blocker, or loses its label
echo '[
 {"number":30,"title":"Waits","state":"OPEN","labels":[{"name":"ready-for-agent"}],
  "blockedBy":{"nodes":[{"number":99,"state":"OPEN"}],"totalCount":1}},
 {"number":31,"title":"Untriaged","state":"OPEN","labels":[]}
]' > "$FIXTURES/issues.json"
out=$(as A "$LIVE" next)
check "$(grep -c '^DEFER	30	-	Waits	blocked by #99' <<< "$out")" 1 \
  "an issue with an open blocker is deferred and the blocker is named"
check "$(grep -c '31' <<< "$out")" 0 "an issue that is not ready-for-agent prints no line"
check "$(tail -n 1 <<< "$out")" "BLOCKED" "next reports BLOCKED when what is left waits on a blocker"
as A "$LIVE" start 30 feat/issue-30-waits 2> /dev/null
check "$?" 1 "start refuses an issue that still has an open blocker"
check "$(tail -n 1 "$LEDGER" | cut -f6)" "not workable at start: blocked by #99" "and records the blocker"
echo '[{"number":30,"title":"Waits","state":"OPEN","labels":[],
  "blockedBy":{"nodes":[{"number":99,"state":"CLOSED"}],"totalCount":1}}]' > "$FIXTURES/issues.json"
as A "$LIVE" start 30 feat/issue-30-waits 2> /dev/null
check "$?" 1 "start refuses an issue that lost ready-for-agent"
check "$(tail -n 1 "$LEDGER" | cut -f6)" "not workable at start: not labeled ready-for-agent" \
  "and records the missing label"
check "$(as A "$LIVE" next)" "EMPTY" "a skipped issue stays out while the label is missing"
echo '[{"number":30,"title":"Waits","state":"OPEN","labels":[{"name":"ready-for-agent"}],
  "blockedBy":{"nodes":[{"number":99,"state":"CLOSED"}],"totalCount":1}}]' > "$FIXTURES/issues.json"
check "$(as A "$LIVE" next | first)" "NEXT	30" "the issue is served again once the label is back and the blocker closed"

# --- the gh version
GH_VERSION=2.93.9 CLAUDE_CODE_SESSION_ID=A CLAUDE_PID=$LIVE bash "$OS" next > /dev/null 2> "$SANDBOX/err"
check "$?" 1 "next stops on a gh older than 2.94"
check "$(grep -c 'needs gh 2.94 or newer' "$SANDBOX/err")" 1 "and says which gh it needs"
GH_VERSION=2.100.1 CLAUDE_CODE_SESSION_ID=A CLAUDE_PID=$LIVE bash "$OS" next > /dev/null 2>&1
check "$?" 0 "a two-digit minor above 94 is accepted"
GH_VERSION=3.0.0 CLAUDE_CODE_SESSION_ID=A CLAUDE_PID=$LIVE bash "$OS" next > /dev/null 2>&1
check "$?" 0 "a newer major is accepted"
GH_VERSION=2.93.9 CLAUDE_CODE_SESSION_ID=A CLAUDE_PID=$LIVE bash "$OS" status > /dev/null 2>&1
check "$?" 0 "an old gh does not stop commands that only read the ledger"

# A status read must not make the ledger look newly modified.
touch -m -t 200001010000 "$LEDGER"
ledger_metadata=$(stat -c '%y|%z|%s|%i' "$LEDGER")
as A "$LIVE" status > /dev/null
check "$?" 0 "status reads the ledger"
check "$(stat -c '%y|%z|%s|%i' "$LEDGER")" "$ledger_metadata" \
  "status leaves ledger metadata unchanged"

# --- a milestone: its own repository, so the state is separate
R2="$SANDBOX/repo2"
mkdir -p "$R2"
git -C "$R2" init -q
cd "$R2" || exit 1
LEDGER2="$R2/.claude/oversee/ledger.tsv"
QUEUE2="$R2/.claude/oversee/queue.tsv"
FILTER2="$R2/.claude/oversee/filter"
M="Wave One"
RA=ready-for-agent
sleep 0 & DEAD2=$!; wait "$DEAD2"

# mk <number> <title> <labels, comma separated> <milestone or -> [body]
mk() {
  jq -n --argjson n "$1" --arg t "$2" --arg l "$3" --arg m "$4" --arg b "${5:-}" '{
    number: $n, title: $t, state: "OPEN", body: $b,
    labels: ($l | split(",") | map(select(. != "") | {name: .})),
    milestone: (if $m == "-" then null else {title: $m} end)}'
}
fixture() { jq -s . > "$FIXTURES/issues.json"; }
fresh() { rm -rf "$R2/.claude/oversee"; echo '[]' > "$FIXTURES/prs.json"; }
order() { cut -f1 "$QUEUE2" | tr '\n' ' '; }

# --- the milestone filter
fresh
{ mk 1 "In the milestone" "$RA" "$M"
  mk 2 "No milestone" "$RA" -
  mk 3 "Another milestone" "$RA" "Wave Two"
  mk 4 "Blocked one" "$RA,Blocked" "$M"
  mk 5 "Held one" "$RA,In Progress" "$M"
  mk 6 "Tracking" "$RA,Tracker" "$M"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(order)" "1 " "a milestone queues only its ready issues"
check "$(wc -l < "$R2/.claude/oversee/open" | tr -d ' ')" 6 "the open list still holds every open issue"
check "$(as A "$LIVE" next | first)" "NEXT	1" "next serves the issue in the milestone"
as A "$LIVE" start 1 feat/issue-1 2> /dev/null
as A "$LIVE" finish 1 done - "ok"
check "$(as A "$LIVE" next | first)" "EMPTY" "issues outside the milestone are never served"

fresh
mk 1 "Titled apart" "$RA" "Voice Bridge" | fixture
as A "$LIVE" init --milestone Voice > /dev/null 2> "$SANDBOX/err"
check "$(order)" "" "a milestone title matches whole, not as a prefix"
check "$(grep -c 'no open issue in milestone "Voice"' "$SANDBOX/err")" 1 \
  "an empty milestone warns on stderr"
check "$(as A "$LIVE" next 2> /dev/null | first)" "EMPTY" "and next ends at EMPTY"

fresh
{ mk 1 "Plain" "$RA" -; mk 2 "voice: second" "$RA" -; } | fixture
as A "$LIVE" init > /dev/null
check "$(awk -F'\t' '{print NF, $7, $8}' "$QUEUE2" | sort -u)" "8 - -" \
  "without a milestone the queue has eight columns and no waits or pick"
check "$(as A "$LIVE" next | head -n 1 | awk -F'\t' '{print NF}')" 4 "and NEXT has no pick column"
check "$(sed -n 2p "$FILTER2")" "" "and the filter has no milestone line"

fresh
{ mk 1 "voice: both" "$RA,voice" "$M"
  mk 2 "Only the milestone" "$RA" "$M"
  mk 3 "voice: only the label" "$RA,voice" "Wave Two"; } | fixture
as A "$LIVE" init voice --milestone "$M" > /dev/null
check "$(order)" "1 " "a label and a milestone are both required"
as A "$LIVE" init --milestone > /dev/null 2>&1
check "$?" 1 "--milestone without a value exits 1"
OVERSEE_FORCE=1 as A "$LIVE" init one two > /dev/null 2>&1
check "$?" 1 "a second label exits 1"

# --- dependencies in the issue body
fresh
{ mk 40 "Dependent" "$RA" "$M" $'## Depends on\n\n- #42 for the data. The rest is free.\n'
  mk 41 "Independent" "$RA" "$M"
  mk 42 "Dependency" "$RA" "$M"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(order)" "42 40 41 " "an issue others wait on is queued ahead of them"
check "$(as A "$LIVE" next | first)" "NEXT	42" "next serves the dependency first"
as A "$LIVE" start 42 feat/issue-42 2> /dev/null
as A "$LIVE" finish 42 done 20 "ready"
echo '[{"number":20}]' > "$FIXTURES/prs.json"
out=$(as A "$LIVE" next)
check "$(grep -c '^DEFER	40.*waits on #42 (pull request 20 open)' <<< "$out")" 1 \
  "a dependent waits while its dependency's pull request is open"
check "$(grep -c '^NEXT	41' <<< "$out")" 1 "and the independent issue is served"
{ mk 40 "Dependent" "$RA" "$M" $'## Depends on\n\n- #42 for the data.\n'
  mk 41 "Independent" "$RA" "$M"; } | fixture
check "$(as A "$LIVE" next | first)" "NEXT	40" "the dependent is served once the dependency closes"

fresh
{ mk 50 "Waits" "$RA" "$M" $'Depends on #60\nDepends on #61\nDepends on owner/repo#63\nDepends on #64\n'
  mk 60 "Open outside" "needs-triage" "Wave Two"
  mk 64 "Tracking" "Tracker" "$M"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(awk -F'\t' '$1 == 50 {print $7}' "$QUEUE2")" "#60" \
  "only an open dependency waits; closed, cross-repository and tracker references do not"
out=$(as A "$LIVE" next)
check "$(grep -c '^DEFER	50.*waits on #60$' <<< "$out")" 1 "next names the open dependency"
check "$(tail -n 1 <<< "$out")" "BLOCKED" "and ends at BLOCKED"

fresh
body=$'Depends on: #1, #2\n- Blocked by #3 and #4\n**Depends on** #5\n## Blocked by\n- #6\n'
body+=$'## Notes\nRelated to #7 for later.\n- #9 is related\n```\nDepends on #8\n```\n'
{ for n in 1 2 3 4 5 6 7 8 9; do mk "$n" "Dep $n" "needs-triage" "$M"; done
  mk 10 "Many" "$RA" "$M" "$body"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(awk -F'\t' '$1 == 10 {print $7}' "$QUEUE2")" "#1 #2 #3 #4 #5 #6" \
  "dependency lines are read in line, list and section forms, and prose and code are not"

fresh
{ mk 80 "Root" "$RA" "$M"
  mk 81 "Chain 1" "$RA" "$M" "Depends on #80"
  mk 82 "Chain 2" "$RA" "$M" "Depends on #81"
  mk 83 "Chain 3" "$RA" "$M" "Depends on #82"
  mk 90 "Fan root" "$RA" "$M"
  mk 91 "Fan 1" "$RA" "$M" "Depends on #90"
  mk 92 "Fan 2" "$RA" "$M" "Depends on #90"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(order)" "80 81 90 82 83 91 92 " "dependents are counted through the whole chain"

fresh
{ mk 70 "Cycle a" "$RA" "$M" "Depends on #71"
  mk 71 "Cycle b" "$RA" "$M" "Depends on #70"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
out=$(as A "$LIVE" next)
check "$(grep -c '^DEFER' <<< "$out")" 2 "a dependency cycle defers both issues"
check "$(tail -n 1 <<< "$out")" "BLOCKED" "and ends at BLOCKED"

# --- ranking
fresh
{ mk 1 "Low" "$RA" "$M" "Priority: low"
  mk 2 "Unstated" "$RA" "$M"
  mk 3 "Critical" "$RA" "$M" "- **Priority:** P0"
  mk 4 "High" "$RA" "$M" "Priority: high"
  mk 5 "High by heading" "$RA" "$M" $'## Priority\n\nHigh\n'
  mk 6 "First word wins" "$RA" "$M" $'Priority: low\nPriority: critical'; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(order)" "3 4 5 2 1 6 " "stated priority orders the queue, and none ranks as medium"

fresh
{ mk 1 "High" "$RA" "$M" "Priority: high"
  mk 2 "Low root" "$RA" "$M" "Priority: low"
  mk 3 "Unstated" "$RA" "$M" "Depends on #2"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(order)" "2 1 3 " "an issue others wait on is served ahead of a higher priority"

fresh
{ mk 100 "Tracking" "Tracker" "$M" $'- [ ] #112\n- [ ] #111\n3. #113\n- #114\n'
  for n in 111 112 113 114 115; do mk "$n" "Item $n" "$RA" "$M"; done; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(order)" "112 111 113 114 115 " "a tracker lists the order, plain bullets excepted"
{ mk 100 "Tracking" "Tracker" "$M" $'- [ ] #112\n- [ ] #111\n3. #113\n- #114\n'
  for n in 111 112 113 114; do mk "$n" "Item $n" "$RA" "$M"; done
  mk 115 "Item 115" "$RA" "$M" "Priority: high"; } | fixture
OVERSEE_FORCE=1 as A "$LIVE" init --milestone "$M" > /dev/null
check "$(order)" "115 112 111 113 114 " "stated priority ranks above tracker order"
{ mk 100 "Tracking" "Tracker" "$M" $'- [ ] #112\n- [ ] #111\n'
  mk 111 "Item 111" "$RA" "$M"
  mk 112 "Item 112" "$RA,Blocked" "$M"; } | fixture
check "$(as A "$LIVE" next | first)" "NEXT	111" "tracker order ranks and never gates"

# --- the pick reason, resume, and the ledger
fresh
{ mk 1 "Root" "$RA" "$M"; mk 2 "Leaf" "$RA" "$M" "Depends on #1"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(as A "$LIVE" next | head -n 1 | cut -f5)" "pick: unblocks 1 open issue" \
  "next gives the reason for the pick"
as A "$LIVE" start 1 feat/issue-1-root
check "$(tail -n 1 "$LEDGER2" | cut -f6)" "session A pid $LIVE; pick: unblocks 1 open issue" \
  "start records the owner and the reason without being told"
check "$(as A "$LIVE" status | grep -c 'pick: unblocks')" 1 "status shows the reason"
fresh
{ mk 1 "Root" "$RA" -; } | fixture
as A "$LIVE" init > /dev/null
as A "$LIVE" start 1 feat/issue-1-root
check "$(tail -n 1 "$LEDGER2" | cut -f6)" "session A pid $LIVE" \
  "without a milestone the note is the owner tag alone"

fresh
{ mk 1 "Root" "$RA" "$M"; mk 2 "Leaf" "$RA" "$M" "Depends on #1"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
as C "$DEAD2" start 1 feat/issue-1-root
as A "$LIVE" adopt 1
check "$(tail -n 1 "$LEDGER2" | cut -f6 | grep -c 'adopted; pick: unblocks 1 open issue')" 1 \
  "adopt keeps the reason"

fresh
{ mk 1 "voice: one" "$RA,voice" "$M"
  mk 2 "Two" "$RA" "$M"
  mk 3 "Three" "$RA" -; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
as B "$LIVE" refresh > /dev/null
check "$(order)" "1 2 " "a bare refresh keeps the milestone"
check "$(as B "$LIVE" status | grep -c '^scope: milestone "Wave One"')" 1 "status shows the scope"
as B "$LIVE" refresh voice > /dev/null
check "$(order)" "1 " "a refresh with a label keeps the milestone"
check "$(sed -n 1,2p "$FILTER2" | tr '\n' '|')" "voice|Wave One|" "and the filter holds both"
OVERSEE_FORCE=1 as B "$LIVE" init > /dev/null
check "$(order)" "1 2 3 " "a forced bare init drops the milestone"

fresh
{ mk 40 "In flight" "$RA" "$M"; mk 41 "Outside" "$RA" -; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
as A "$LIVE" start 40 feat/issue-40
{ mk 40 "In flight" "In Progress" "Wave Two"; mk 41 "Outside" "$RA" -; } | fixture
check "$(as A "$LIVE" next | first)" "INFLIGHT	40" "an issue the ledger names stays in flight when it leaves the milestone"
check "$(as B "$LIVE" next | grep -c '^NEXT')" 0 "and nothing outside the milestone is served"

fresh
{ mk 40 "Moved" "$RA" "$M"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
mk 40 "Moved" "$RA" "Wave Two" | fixture
as A "$LIVE" start 40 feat/issue-40 2> /dev/null
check "$?" 1 "start refuses an issue that left the milestone"
check "$(tail -n 1 "$LEDGER2" | cut -f6)" "not workable at start: not in milestone Wave One" \
  "and records the milestone"

fresh
{ mk 1 "voice: first" "$RA" "$M"; mk 2 "voice: second" "$RA" "$M"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
as A "$LIVE" start 1 feat/issue-1
as A "$LIVE" finish 1 done 20 "ready"
echo '[{"number":20}]' > "$FIXTURES/prs.json"
check "$(as A "$LIVE" next | grep -c '^DEFER	2.*area held by PR #20')" 1 \
  "a milestone issue waits for an open pull request in its area"

fresh
{ mk 1 "In" "$RA" "$M"; mk 2 "Out" "$RA" -; } | fixture
as A "$LIVE" refresh --milestone "$M" > /dev/null
check "$(as A "$LIVE" next | first)" "NEXT	1" "refresh --milestone on empty state scopes the first next"
as A "$LIVE" finish 1 done - "ok"
check "$(as A "$LIVE" next | first)" "EMPTY" "and nothing outside the milestone is served after"

fresh
{ for n in 1 2 3 4 5; do mk "$n" "Dep $n" "needs-triage" "$M"; done
  mk 10 "Markers" "$RA" "$M" $'+ Depends on #1\n1. Depends on #2\n2) Blocked by #3\n* Depends on #4\n'
  mk 11 "Plain bullet" "$RA" "$M" $'- Blocked by #5\n'; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(awk -F'\t' '$1 == 10 {print $7}' "$QUEUE2")" "#1 #2 #3 #4" \
  "plus, numbered and star markers open a dependency line"
check "$(awk -F'\t' '$1 == 11 {print $7}' "$QUEUE2")" "#5" "and so does a dash"

fresh
{ mk 40 "Moved" "$RA" "$M"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
mk 40 "Moved" "$RA" "Wave Two" | fixture
as A "$LIVE" start 40 feat/issue-40 2> /dev/null
mk 40 "Moved" "$RA" "$M" | fixture
check "$(as A "$LIVE" next | first)" "NEXT	40" "an issue skipped for leaving the milestone returns with it"

fresh
{ mk 2 "Milestone only" "$RA" "$M"; mk 3 "Label only" "$RA,voice" -; } | fixture
as A "$LIVE" refresh voice > /dev/null
OVERSEE_FORCE=1 as A "$LIVE" init --milestone "$M" > /dev/null
check "$(as A "$LIVE" next | first)" "NEXT	2" "a forced init with a milestone drops a saved label"
OVERSEE_FORCE=1 as A "$LIVE" init voice > /dev/null
check "$(as A "$LIVE" next | first)" "NEXT	3" "a forced init with a label drops a saved milestone"
check "$(as A "$LIVE" status | grep -c '^scope: label voice$')" 1 \
  "status shows a scope that is a label alone"

fresh
{ mk 2 "Outside orphan" "$RA" -; mk 3 "Inside" "$RA" "$M"; mk 4 "Inside orphan" "$RA" "$M"; } |
  fixture
as A "$LIVE" init > /dev/null
as C "$DEAD2" start 2 feat/issue-2
as C "$DEAD2" start 4 feat/issue-4
OVERSEE_FORCE=1 as A "$LIVE" init --milestone "$M" > /dev/null
check "$(as A "$LIVE" next | first)" "INFLIGHT	4" "a milestone run adopts an orphan inside the milestone"
as A "$LIVE" finish 4 done - "ok"
check "$(as A "$LIVE" next | grep -v '^ELSEWHERE' | first)" "NEXT	3" "and never one outside it"
fresh
{ mk 2 "Outside orphan" "$RA" -; } | fixture
as A "$LIVE" init > /dev/null
as C "$DEAD2" start 2 feat/issue-2
check "$(as A "$LIVE" next | first)" "INFLIGHT	2" "without a milestone an orphan is served"

fresh
{ mk 2 "voice: outside orphan" "$RA" -; mk 3 "voice: inside" "$RA" "$M"; } | fixture
as A "$LIVE" init > /dev/null
as C "$DEAD2" start 2 feat/issue-2
OVERSEE_FORCE=1 as A "$LIVE" init --milestone "$M" > /dev/null
out=$(as A "$LIVE" next)
check "$(grep -c '^ELSEWHERE	2' <<< "$out")" 1 "an orphan outside the milestone is printed"
check "$(grep -c '^DEFER	3.*area held by issue 2 orphaned outside the milestone' <<< "$out")" 1 \
  "and holds its area against an issue inside the milestone"
check "$(tail -n 1 <<< "$out")" "BLOCKED" "and counts as busy"


fresh
{ for n in 21 22 23 24 25; do mk "$n" "Dep $n" "needs-triage" "$M"; done
  mk 20 "Prose" "$RA" "$M" \
    $'Intro. Depends on #21 but see #22 for context. **Blocked by**: #23 and #24.\nOther: #25\n'
  mk 26 "Cross" "$RA" "$M" "Depends on owner/repo#25 later"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(awk -F'\t' '$1 == 20 {print $7}' "$QUEUE2")" "#21 #23 #24" \
  "a dependency phrase mid-paragraph takes only the references that follow it"
check "$(awk -F'\t' '$1 == 26 {print $7}' "$QUEUE2")" "-" "a cross-repository reference stays skipped"

fresh
{ mk 31 "Unrelated" "$RA" "$M"
  mk 32 "Blocked natively" "$RA" "$M" |
    jq '.blockedBy = {nodes: [{number: 33, state: "OPEN"}], totalCount: 1}'
  mk 33 "Native blocker" "$RA" "$M"; } | fixture
as A "$LIVE" init --milestone "$M" > /dev/null
check "$(order)" "33 31 32 " "a native blocker ranks ahead of unrelated issues"
check "$(as A "$LIVE" next | head -n 1 | cut -f5)" "pick: unblocks 1 open issue" \
  "and the reason counts the issue it blocks"
fresh
mkdir -p "$R2/.claude/skills/oversee-development"
CONFIG="$R2/.claude/skills/oversee-development/extension.json"
echo '{"queue":{"readyLabel":null,"requireLabels":["allowed"],"excludeLabels":["new feature"],"blockedLabels":["Blocked on API"]}}' > "$CONFIG"
{ mk 7 "Candidate" "allowed" -; mk 14 "Other" "allowed" -
  mk 15 "Excluded" "allowed,new feature" -; mk 16 "Missing" "" -
  mk 17 "API wait" "allowed,Blocked on API" -; } | fixture
as A "$LIVE" init > /dev/null
out=$(as A "$LIVE" blocked)
check "$(grep -c '^BLOCKED	17	API wait	' <<< "$out")" 1 "configured blocked labels appear in the report"
check "$(order)" "7 14 " "repository filters apply together and null removes the ready gate"
echo '[{"number":80,"headRefName":"feat/issue-71-x","body":"Closes #14"}]' > "$FIXTURES/prs.json"
out=$(as A "$LIVE" next)
check "$(grep -c '^NEXT	7' <<< "$out")" 1 "a longer issue number in a branch does not match"
as A "$LIVE" start 14 feat/issue-14-test 2> /dev/null
check "$?" 1 "start refuses an issue already linked to an open pull request"
echo '[{"number":80,"headRefName":"feat/issue-7-x","body":"Closes #14"}]' > "$FIXTURES/prs.json"
out=$(as A "$LIVE" next)
check "$(grep -c '^DEFER	7.*open pull request #80' <<< "$out")" 1 "branch-linked pull requests defer their issue"
check "$(tail -n 1 <<< "$out")" "BLOCKED" "open pull requests leave the queue blocked"
echo '[]' > "$FIXTURES/prs.json"
mk 7 "Candidate" "allowed,new feature" - | fixture
as A "$LIVE" start 7 feat/issue-7-test 2> /dev/null
check "$?" 1 "start rechecks configured exclusions"
rm "$CONFIG"
FAIL_PRS=1 as A "$LIVE" next > /dev/null 2>&1
check "$?" 1 "next fails closed when the pull request read fails"
FAIL_PRS=1 as A "$LIVE" start 7 feat/issue-7-test > /dev/null 2>&1
check "$?" 1 "start fails closed when the pull request read fails"
FAIL_ISSUES=1 as A "$LIVE" next > /dev/null 2>&1
check "$?" 1 "next does not select from a stale backlog"

fresh
echo '[{"number":1,"title":"Waiting","state":"OPEN","labels":[{"name":"Blocked"},{"name":"ready-for-agent"}],"comments":[{"body":"Old"},{"body":"Latest reason\nMore"}]},
 {"number":2,"title":"Stalled","state":"OPEN","labels":[{"name":"Blocked"},{"name":"ready-for-agent"}],"comments":[{"body":"Comment"}]},
 {"number":3,"title":"Track","state":"OPEN","labels":[{"name":"Blocked"},{"name":"Tracker"},{"name":"ready-for-agent"}]}]' > "$FIXTURES/issues.json"
as A "$LIVE" init > /dev/null
as A "$LIVE" finish 2 stalled - "ledger reason"
out=$(as A "$LIVE" blocked)
check "$(grep -c '^BLOCKED	1	Waiting	Latest reason$' <<< "$out")" 1 "blocked reports the latest comment first line"
check "$(grep -c '^BLOCKED	2	Stalled	ledger reason$' <<< "$out")" 1 "a stalled ledger reason takes precedence"
check "$(grep -c '^BLOCKED	3	' <<< "$out")" 0 "blocked excludes trackers"

fresh
echo '{"queue":{"readyLabel":"ready","requireLabels":["allowed","reviewed"],"excludeLabels":["custom exclusion","Blocked on API"],"blockedLabels":["Blocked on API"]}}' > "$CONFIG"
{ mk 10 "Default blocked" "ready,allowed,reviewed,scope,Blocked" "$M"
  mk 11 "Custom blocked" "ready,allowed,reviewed,scope,Blocked on API" "$M"
  mk 12 "Missing ready" "allowed,reviewed,scope,Blocked" "$M"
  mk 13 "Missing required" "ready,allowed,scope,Blocked" "$M"
  mk 14 "Default exclusion" "ready,allowed,reviewed,scope,Blocked,needs-info" "$M"
  mk 15 "Custom exclusion" "ready,allowed,reviewed,scope,Blocked,custom exclusion" "$M"
  mk 16 "Wrong label" "ready,allowed,reviewed,Blocked" "$M"
  mk 17 "Wrong milestone" "ready,allowed,reviewed,scope,Blocked" "Wave Two"
  mk 18 "Tracker" "ready,allowed,reviewed,scope,Blocked,Tracker" "$M"
  mk 19 "Multiple blocked labels" "ready,allowed,reviewed,scope,Blocked,Blocked on API" "$M"; } | fixture
as A "$LIVE" init --milestone "$M" scope > /dev/null
out=$(as A "$LIVE" blocked)
check "$(printf '%s\n' "$out" | cut -f2 | sort -n | tr '\n' ' ')" "10 11 19 " \
  "blocked reports only blocked issues satisfying all other queue and run filters"
rm "$CONFIG"

fresh
{ mk 1 "First scope" "$RA,alpha" "$M"
  mk 2 "Second scope" "$RA,beta" "Wave Two"; } | fixture
LOOP="$HERE/loop.py"
python3 "$LOOP" --session A start --milestone "$M" alpha > /dev/null
python3 "$LOOP" --session B start --milestone "Wave Two" beta > /dev/null
OVERSEE_FORCE=1 as A "$LIVE" init --milestone "$M" alpha > /dev/null
OVERSEE_FORCE=1 as B "$LIVE" init --milestone "Wave Two" beta > /dev/null
check "$(as A "$LIVE" next | first)" "NEXT	1" "a loop selects from its marker after another session changes the shared queue"
check "$(as B "$LIVE" next | first)" "NEXT	2" "each loop restores its own scope on selection"
check "$(as A "$LIVE" status | grep -c '^scope: milestone "Wave One", label alpha$')" 1 \
  "status reports the loop scope rather than the last shared filter"
as A "$LIVE" start 2 feat/issue-2 > /dev/null 2>&1
check "$?" 1 "start checks the marker scope after another session changed the queue"
OVERSEE_FORCE=1 as A "$LIVE" init beta > /dev/null 2>&1
check "$?" 1 "init cannot replace a live loop's marker scope"
as A "$LIVE" refresh beta > /dev/null 2>&1
check "$?" 1 "refresh cannot replace a live loop's marker scope"
python3 "$LOOP" --session A stop done > /dev/null
python3 "$LOOP" --session B stop done > /dev/null

fresh
{ mk 2 "voice: outside orphan" "$RA,beta" -
  mk 3 "voice: inside" "$RA,alpha" -; } | fixture
as A "$LIVE" init > /dev/null
as C "$DEAD2" start 2 feat/issue-2
python3 "$LOOP" --session A start alpha > /dev/null
out=$(as A "$LIVE" next)
check "$(grep -c '^ELSEWHERE	2' <<< "$out")" 1 "a label-scoped loop does not adopt an orphan outside its label"
check "$(grep -c '^DEFER	3.*area held by issue 2 orphaned outside the label' <<< "$out")" 1 \
  "an out-of-scope orphan still holds its area"
python3 "$LOOP" --session A stop done > /dev/null

fresh
{ mk 1 "Milestone candidate" "$RA,alpha" "$M"
  mk 2 "Loop candidate" "$RA,beta" "Wave Two"
  mk 3 "Loop candidate two" "$RA,beta" "Wave Two"; } | fixture
as C "$LIVE" init --milestone "$M" alpha > /dev/null
python3 "$LOOP" --session A start --milestone "Wave Two" beta > /dev/null
as A "$LIVE" next > /dev/null
check "$(as A "$LIVE" status | grep '^queued ')" "queued 2 total" \
  "loop status counts its own snapshot"
check "$(as C "$LIVE" status | grep '^queued ')" "queued 1 total" \
  "non-loop status keeps its own snapshot"
check "$(as C "$LIVE" next | first)" "NEXT	1" \
  "a loop refresh does not overwrite a non-loop milestone and label"
check "$(sed -n 1,2p "$FILTER2" | tr '\n' '|')" "alpha|Wave One|" \
  "the saved non-loop scope is unchanged"

fresh
{ mk 7 "Owned work" "$RA,alpha" -; } | fixture
python3 "$LOOP" --session A start alpha > /dev/null
as A "$DEAD2" start 7 feat/issue-7-owned
out=$(as B "$LIVE" next)
check "$(grep -c '^ELSEWHERE	7' <<< "$out")" 1 \
  "an active marker protects an issue even after its owner process exits"
as B "$LIVE" start 7 feat/issue-7-other > /dev/null 2>&1
check "$?" 1 "start refuses an issue protected by an active marker"
as B "$LIVE" adopt 7 > /dev/null 2>&1
check "$?" 1 "adoption refuses an issue protected by an active marker"
MARKER="$R2/.claude/oversee/loops/A.json"
jq '.state = "paused"' "$MARKER" > "$MARKER.tmp" && mv "$MARKER.tmp" "$MARKER"
out=$(as B "$LIVE" next)
check "$(grep -c '^ELSEWHERE	7' <<< "$out")" 1 "a paused marker protects its issue"
as B "$LIVE" start 7 feat/issue-7-other > /dev/null 2>&1
check "$?" 1 "start refuses an issue protected by a paused marker"
as B "$LIVE" adopt 7 > /dev/null 2>&1
check "$?" 1 "adoption refuses an issue protected by a paused marker"
python3 "$LOOP" --session A stop done > /dev/null
check "$(as B "$LIVE" next | first)" "INFLIGHT	7" \
  "a stopped marker allows a dead owner's issue to be selected"
check "$(as B "$LIVE" next | cut -f6)" "orphan" "the stopped owner's issue is an orphan"
as B "$LIVE" adopt 7
check "$(as B "$LIVE" next | cut -f6)" "mine" "ordinary adoption claims the orphan"
check "$(tail -n 1 "$LEDGER2" | cut -f4)" "feat/issue-7-owned" \
  "ordinary adoption preserves the in-flight branch"

fresh
{ mk 7 "Live owned work" "$RA,alpha" -; } | fixture
python3 "$LOOP" --session A start alpha > /dev/null
as A "$LIVE" start 7 feat/issue-7-owned
python3 "$LOOP" --session A stop done > /dev/null
python3 "$LOOP" --session B start alpha > /dev/null
out=$(as B "$LIVE" next)
check "$(grep -c '^ELSEWHERE	7' <<< "$out")" 1 \
  "a stopped marker falls back to the live owner's PID"
as B "$LIVE" adopt 7 > /dev/null 2>&1
check "$?" 1 "ordinary adoption refuses a stopped marker's live owner"
as B "$LIVE" start 7 feat/issue-7-other > /dev/null 2>&1
check "$?" 1 "start refuses a stopped marker's live owner"

fresh
{ mk 7 "Unknown PID work" "$RA,alpha" -; } | fixture
python3 "$LOOP" --session A start alpha > /dev/null
as A "" start 7 feat/issue-7-owned
python3 "$LOOP" --session A stop done > /dev/null
out=$(as B "$LIVE" next)
check "$(grep -c '^ELSEWHERE	7' <<< "$out")" 1 "a stopped marker with no owner PID remains held"
as B "$LIVE" adopt 7 > /dev/null 2>&1
check "$?" 1 "ordinary adoption refuses an unknown owner PID"

fresh
{ mk 7 "Stopped owner" "$RA,alpha" -; } | fixture
python3 "$LOOP" --session A start alpha > /dev/null
as A "$DEAD2" start 7 feat/issue-7-owned
python3 "$LOOP" --session A stop done > /dev/null
as B "$LIVE" start 7 feat/issue-7-new > /dev/null 2>&1
check "$?" 0 "start applies normal dead-PID liveness after a marker stops"

fresh
{ mk 7 "Unreadable marker owner" "$RA,alpha" -; } | fixture
python3 "$LOOP" --session A start alpha > /dev/null
as A "$DEAD2" start 7 feat/issue-7-owned
printf '{' > "$R2/.claude/oversee/loops/A.json"
out=$(as B "$LIVE" next)
check "$(grep -c '^ELSEWHERE	7' <<< "$out")" 1 "a malformed marker holds conservatively"
as B "$LIVE" adopt 7 > /dev/null 2>&1
check "$?" 1 "adoption refuses an owner with a malformed marker"

fresh
{ mk 8 "Live non-loop owner" "$RA" -; } | fixture
as A "$LIVE" init > /dev/null
as A "$LIVE" start 8 feat/issue-8-owned
as B "$LIVE" adopt 8 > /dev/null 2>&1
check "$?" 1 "ordinary adoption refuses a live non-loop owner"

wait_for_file() {
  local path=$1 n
  for ((n = 0; n < 250; n++)); do
    [ -e "$path" ] && return
    sleep 0.02
  done
  return 1
}

# Ledger writers must finish while a backlog read is still waiting.
for operation in init refresh next loop-start; do
  fresh
  { mk 7 "Owned work" "$RA,alpha" -; mk 8 "Other work" "$RA,alpha" -; } | fixture
  if [ "$operation" != init ]; then
    as A "$LIVE" init > /dev/null
  fi
  if [ "$operation" = loop-start ]; then
    python3 "$LOOP" --session A start alpha > /dev/null
  fi
  delay="$SANDBOX/delay-$operation"
  mkdir -p "$delay"
  case $operation in
    init) set -- init ;;
    refresh) set -- refresh ;;
    next) set -- next ;;
    loop-start) set -- start 7 feat/issue-7-a ;;
  esac
  DELAY_ISSUES="$delay" as A "$LIVE" "$@" > "$delay/out" 2>&1 &
  reader=$!
  wait_for_file "$delay/entered" || true
  check "$([ -e "$delay/entered" ] && echo yes || echo no)" yes "$operation reaches the backlog read"
  (as B "$LIVE" start 7 feat/issue-7-b > "$delay/writer-out" 2>&1
   echo "$?" > "$delay/writer-status") &
  writer=$!
  wait_for_file "$delay/writer-status" || true
  check "$([ -e "$delay/writer-status" ] && echo yes || echo no)" yes \
    "$operation leaves the ledger available during the backlog read"
  : > "$delay/release"
  wait "$writer"
  check "$(cat "$delay/writer-status")" 0 "$operation permits the other session to claim work"
  wait "$reader"
  result=$?
  if [ "$operation" = loop-start ]; then
    check "$result" 1 "loop start refuses an issue claimed during its backlog read"
    check "$(tail -n 1 "$LEDGER2" | cut -f4)" "feat/issue-7-b" \
      "loop start preserves the other session's ownership"
  else
    check "$result" 0 "$operation completes after the backlog read"
    if [ "$operation" = next ]; then
      check "$(grep -c '^ELSEWHERE	7' "$delay/out")" 1 \
        "next observes the claim made during the backlog read"
    fi
  fi
done

fresh
{ mk 7 "Claimed work" "$RA,In Progress" -; mk 8 "Ready work" "$RA" -; } | fixture
delay="$SANDBOX/delay-known"
mkdir -p "$delay"
DELAY_ISSUES="$delay" as A "$LIVE" init > "$delay/out" 2>&1 &
reader=$!
wait_for_file "$delay/entered" || true
as B "$LIVE" finish 7 stalled - "waiting" > /dev/null &
writer=$!
for ((n = 0; n < 250; n++)); do
  [ -s "$LEDGER2" ] && break
  sleep 0.02
done
check "$([ -s "$LEDGER2" ] && echo yes || echo no)" yes "finish writes during a backlog read"
: > "$delay/release"
wait "$writer"
wait "$reader"
check "$(awk -F'\t' '$1 == 7 {print $1}' "$QUEUE2")" 7 \
  "the published snapshot includes an issue recorded during the backlog read"

fresh
mk 7 "Ready work" "$RA,alpha" - | fixture
delay="$SANDBOX/delay-inits"
mkdir -p "$delay"
DELAY_ISSUES="$delay" as A "$LIVE" init alpha > "$delay/out" 2>&1 &
reader=$!
wait_for_file "$delay/entered" || true
as B "$LIVE" init > "$delay/second" 2>&1 &
writer=$!
: > "$delay/release"
wait "$reader"
check "$?" 0 "the first concurrent init publishes its snapshot"
wait "$writer"
check "$?" 1 "a concurrent init cannot replace a populated snapshot without force"
check "$(cat "$FILTER2")" alpha "the first init retains its scope"

fresh
mk 7 "Ready work" "$RA,alpha" - | fixture
python3 "$LOOP" --session A start alpha > /dev/null
delay="$SANDBOX/delay-stopped"
mkdir -p "$delay"
DELAY_ISSUES="$delay" as A "$LIVE" next > "$delay/out" 2>&1 &
reader=$!
wait_for_file "$delay/entered" || true
python3 "$LOOP" --session A stop done > /dev/null
: > "$delay/release"
wait "$reader"
check "$?" 1 "next refuses to publish after its loop stops during the backlog read"
check "$([ -s "$R2/.claude/oversee/loops/A.queue.tsv" ] && echo yes || echo no)" no \
  "a stopped loop does not publish the pending snapshot"

cd "$SANDBOX/repo" || exit 1

# --- runs and resume: park an issue while its runs go, then take it back
R3="$SANDBOX/repo3"
mkdir -p "$R3"
git -C "$R3" init -q
cd "$R3" || exit 1
LEDGER3="$R3/.claude/oversee/ledger.tsv"
echo '[
 {"number":1,"title":"voice: first","state":"OPEN","labels":[{"name":"ready-for-agent"}]},
 {"number":2,"title":"voice: second","state":"OPEN","labels":[{"name":"ready-for-agent"}]},
 {"number":3,"title":"att-docs: third","state":"OPEN","labels":[{"name":"ready-for-agent"}]}
]' > "$FIXTURES/issues.json"
echo '[]' > "$FIXTURES/prs.json"
as A "$LIVE" init > /dev/null
as A "$LIVE" runs 1 2> /dev/null
check "$?" 1 "runs refuses an issue that is not being worked"
as A "$LIVE" resume 1 2> /dev/null
check "$?" 1 "resume refuses an issue that is not waiting on runs"
as A "$LIVE" start 1 feat/issue-1-first
as B "$LIVE" runs 1 2> /dev/null
check "$?" 1 "runs refuses an issue another session started"
as A "$LIVE" runs 1
check "$(tail -n 1 "$LEDGER3" | cut -f2-4)" "1	runs	feat/issue-1-first" \
  "runs appends a runs row on the same branch"
check "$(tail -n 1 "$LEDGER3" | cut -f6 | grep -c "session A pid $LIVE")" 1 "the runs row carries the owner tag"
out=$(as A "$LIVE" next)
check "$(grep -c '^RUNS	1' <<< "$out")" 1 "next prints a parked issue as RUNS"
check "$(grep -c '^INFLIGHT' <<< "$out")" 0 "a parked issue is not served as in flight"
check "$(grep -c '^DEFER	2.*area held by issue 1 waiting on its runs' <<< "$out")" 1 \
  "a parked issue holds its area"
check "$(grep -c '^NEXT	3' <<< "$out")" 1 "next serves a different issue while one is parked"
before=$(wc -l < "$LEDGER3")
as A "$LIVE" start 1 feat/issue-1-first 2> /dev/null
check "$?" 1 "start refuses the session's own parked issue"
check "$(wc -l < "$LEDGER3")" "$before" "and writes no row over the park"
check "$(as A "$LIVE" blocked | grep -c '^RUNS	1')" 1 "blocked reports a parked issue"
cp "$FIXTURES/issues.json" "$FIXTURES/issues.full.json"
jq '[.[] | select(.number != 3 and .number != 2)]' "$FIXTURES/issues.full.json" > "$FIXTURES/issues.json"
check "$(as A "$LIVE" next | tail -n 1)" "BLOCKED" \
  "next is BLOCKED, not EMPTY, while a parked issue is the only work left"
cp "$FIXTURES/issues.full.json" "$FIXTURES/issues.json"
out=$(as B "$LIVE" next)
check "$(grep -c '^ELSEWHERE	1' <<< "$out")" 1 "another session sees the parked issue as in flight elsewhere"
as B "$LIVE" start 1 feat/issue-1-other 2> /dev/null
check "$?" 1 "a second session cannot start a parked issue held by a live one"
check "$(as A "$LIVE" status | head -n 1 | grep -c 'on runs 1')" 1 "status counts the issue on runs"
as A "$LIVE" start 3 feat/issue-3-third
as A "$LIVE" resume 1 2> /dev/null
check "$?" 1 "resume refuses while another issue of the session is in flight"
as A "$LIVE" finish 3 done - "ok"
as B "$LIVE" resume 1 2> /dev/null
check "$?" 1 "resume refuses an issue another session parked"
as A "$LIVE" resume 1
check "$(tail -n 1 "$LEDGER3" | cut -f2-4)" "1	start	feat/issue-1-first" \
  "resume appends a start row on the same branch"
check "$(tail -n 1 "$LEDGER3" | cut -f6 | grep -c 'resumed')" 1 "and says it was resumed"
check "$(as A "$LIVE" next | first)" "INFLIGHT	1" "a resumed issue is served as in flight again"
as A "$LIVE" runs 1
sleep 0 & DEAD3=$!; wait "$DEAD3"
as C "$DEAD3" start 3 feat/issue-3-third 2> /dev/null
echo "$(printf '2026-01-01T00:00:00Z\t2\truns\tfeat/issue-2-second\t-\tsession Z pid %s' "$DEAD3")" >> "$LEDGER3"
check "$(as A "$LIVE" next | first)" "INFLIGHT	2" "an orphaned runs row is offered as an in-flight orphan"
as A "$LIVE" adopt 2
check "$(tail -n 1 "$LEDGER3" | cut -f2-3)" "2	start" "adopt claims an orphaned runs row"

cd "$SANDBOX/repo" || exit 1

if ((fails)); then echo "$fails failed"; exit 1; fi
echo "all passed"
