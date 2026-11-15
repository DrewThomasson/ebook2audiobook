#!/usr/bin/env bash
# Cases for the Stop path of speak-attention.sh. A stub spd-say records what it would say,
# and each case writes a small transcript, so nothing is spoken.
# usage: bash speak-attention_test.sh
set -uo pipefail

for bin in jq python3; do
  command -v "$bin" > /dev/null || { echo "$bin is required"; exit 1; }
done

HERE="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$HERE/test-config.json"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

# The hook takes Piper from HOME's pipx install alone, so HOME is the sandbox's.
export HOME="$SANDBOX/home"
mkdir -p "$SANDBOX/bin" "$HOME/.local/bin"
# The stub lists no output modules for -O and appends the spoken text to SPOKEN.
# While NOWLOG is set, the stubs also append the now.json the hook published for the clip.
# The spd-say stub can end its first clip as a pause would, naming the clip in requeue, when
# REQUEUE_ONCE names a flag file that does not exist yet.
printf '%s\n' '#!/bin/sh' '[ "$1" = -O ] && exit 0' \
  'for a in "$@"; do last=$a; done' \
  'now=$XDG_RUNTIME_DIR/speak-attention/now.json' \
  'if [ -n "$NOWLOG" ]; then' \
  '  for i in $(seq 50); do [ -n "$(jq -r ".player_pid // empty" "$now" 2>/dev/null)" ] && break;' \
  '    sleep 0.1; done' \
  '  jq -c . "$now" >> "$NOWLOG"' \
  'fi' \
  'if [ -n "$REQUEUE_ONCE" ] && [ ! -e "$REQUEUE_ONCE" ]; then' \
  '  : > "$REQUEUE_ONCE"; jq -r .clip "$now" > "$XDG_RUNTIME_DIR/speak-attention/requeue"; exit 0' \
  'fi' \
  'echo "$last" >> "$SPOKEN"' > "$SANDBOX/bin/spd-say"
# The piper stub writes its input to the -f file, or fails when PIPER_FAIL is set, and
# the pw-play stub appends that file to SPOKEN behind a "piper: " mark. A piper on PATH
# speaks as "path piper: ", which no case expects.
printf '%s\n' '#!/bin/sh' 'echo "$*" >> "${PIPER_ARGS:-/dev/null}"' \
  '[ -n "$PIPER_FAIL" ] && exit 1' \
  'while [ $# -gt 0 ] && [ "$1" != -f ]; do shift; done' 'cat > "$2"' \
  > "$HOME/.local/bin/piper"
printf '%s\n' '#!/bin/sh' 'while [ $# -gt 0 ] && [ "$1" != -f ]; do shift; done' \
  'printf "path " > "$2"' > "$SANDBOX/bin/piper"
printf '%s\n' '#!/bin/sh' 'for a in "$@"; do last=$a; done' \
  'now=$XDG_RUNTIME_DIR/speak-attention/now.json' \
  'if [ -n "$NOWLOG" ]; then' \
  '  for i in $(seq 50); do [ -n "$(jq -r ".player_pid // empty" "$now" 2>/dev/null)" ] && break;' \
  '    sleep 0.1; done' \
  '  jq -c . "$now" >> "$NOWLOG"' \
  'fi' \
  'printf "piper: %s" "$(cat "$last")" >> "$SPOKEN"' > "$SANDBOX/bin/pw-play"
# A date that ignores the width in %3N and writes all nine digits, as some builds do. Nothing here
# or in the hook uses %3N, so this shim only fails a case that starts to.
printf '%s\n' '#!/bin/sh' 'for a in "$@"; do set -- "$@" "$(printf %s "$a" | sed "s/%3N/%N/g")"; shift; done' \
  "exec $(command -v date) \"\$@\"" > "$SANDBOX/bin/date"
chmod +x "$SANDBOX/bin/date"
chmod +x "$SANDBOX/bin/spd-say" "$SANDBOX/bin/piper" "$SANDBOX/bin/pw-play" \
  "$HOME/.local/bin/piper"
export PATH="$SANDBOX/bin:$PATH"
# Cases speak through Speech Dispatcher unless they name a model that exists.
export SPEAK_PIPER_MODEL="$SANDBOX/none.onnx"
export SPOKEN="$SANDBOX/spoken"
export XDG_RUNTIME_DIR="$SANDBOX/run"
# A Stop in speech mode waits for a reply row the transcript lacks; cases do not wait.
export STOP_WAIT=0
TRANSCRIPT="$SANDBOX/session.jsonl"
OWED="$XDG_RUNTIME_DIR/speak-attention/s1.owed"
: > "$TRANSCRIPT"

fails=0
LAST_AT="$(date +%s.%N)"

# usage: check <got> <wanted> <case>
check() {
  # Each line carries the seconds since the last one, so a case that waited out a timeout stands out.
  local now gap
  now="$(date +%s.%N)"
  gap="$(awk -v a="$now" -v b="$LAST_AT" 'BEGIN { printf "%.1f", a - b }')"
  LAST_AT="$now"
  if [ "$1" = "$2" ]; then
    echo "ok   $3 (${gap}s)"
  else
    echo "FAIL $3: got [$1], wanted [$2] (${gap}s)"
    # The clock and the last rows of the transcript, on a FAIL line of their own so the runner
    # lists them, to tell a timing failure from a logic one.
    echo "FAIL   clock $(($(date +%s%N) / 1000000)) ms, last rows $(tail -n 4 "$TRANSCRIPT" |
      jq -c '[.type, .origin.kind, .timestamp]' 2>/dev/null | tr '\n' ' ')"
    fails=$((fails + 1))
  fi
}

# usage: row <json>; appends one transcript row.
row() { printf '%s\n' "$1" >> "$TRANSCRIPT"; }

# usage: prompt <origin kind> <text> [seconds from now]; the row carries a timestamp only
# when it is given one.
prompt() {
  local at=
  if [[ -n "${3:-}" ]]; then
    # Milliseconds are the first three digits of %N, which every date writes in full.
    at=$(date -u -d "$3 seconds" +%Y-%m-%dT%H:%M:%S.%N)
    at="${at:0:23}Z"
  fi
  row "$(jq -cn --arg k "$1" --arg t "$2" --arg at "$at" \
    '{type:"user", origin:{kind:$k}, message:{role:"user", content:$t}}
      + (if $at == "" then {} else {timestamp:$at} end)')"
}

# usage: result <toolUseResult json>; appends a tool result row carrying it.
result() {
  row "$(jq -cn --argjson r "$1" '{type:"user", timestamp:"2026-10-19T13:00:00.000Z",
    toolUseResult:$r, message:{role:"user", content:[{type:"tool_result", content:""}]}}')"
}

# A persistent Monitor stays due to wake the session until it is stopped.
monitor() { result '{"taskId":"m1","persistent":true}'; }
stopped() { result '{"message":"Successfully stopped task: m1","task_id":"m1"}'; }

# usage: stop <reply> [unwritten]; writes the reply row unless told the transcript lags the
# hook, runs the Stop hook and prints what it said, or nothing.
stop() {
  : > "$SPOKEN"
  [[ -n "${2:-}" ]] ||
    row "$(jq -cn --arg r "$1" '{type:"assistant", message:{role:"assistant", content:$r}}')"
  jq -cn --arg t "$TRANSCRIPT" --arg r "$1" \
    '{hook_event_name:"Stop", session_id:"s1", transcript_path:$t,
      last_assistant_message:$r, cwd:"/x/demo"}' | "$HERE/speak-attention.sh" --config "$CONFIG"
  cat "$SPOKEN"
}

prompt human "run the suite"
check "$(stop 'Done.')" "demo session finished" "a user turn says finished"

prompt task-notification "<task-notification>x</task-notification>"
check "$(stop 'Merged.')" "" "an event turn with nothing owed is quiet"

prompt human "watch the run"
monitor
check "$(stop 'Watching.')" "" "a stop held by background work is quiet"
check "$([ -e "$OWED" ] && echo owed)" "owed" "the held stop owes an announcement"

prompt task-notification "<task-notification>x</task-notification>"
stopped
check "$(stop 'The run is green.')" "demo session finished" "the next quiet stop pays the debt"
check "$([ -e "$OWED" ] && echo owed)" "" "paying the debt clears it"

prompt task-notification "<task-notification>y</task-notification>"
check "$(stop 'Still green.')" "" "a later event turn is quiet again"

prompt peer "report"
check "$(stop 'Should I merge it?')" "demo session is waiting for you" "a question waits"

prompt peer "report" -3
check "$(stop 'Merge it now?' unwritten)" "demo session is waiting for you" \
  "a question waits before its reply row is written"
row '{"type":"assistant","message":{"role":"assistant","content":"Merge it now?"}}'

prompt human "start the sweep"
monitor
check "$(stop 'Which suite first?')" "" "a question held by background work is quiet"
prompt task-notification "<task-notification>z</task-notification>"
stopped
check "$(stop 'Sweep is running.')" "demo session is waiting for you" "the held question is repaid"

# An event the app delivers once the hook has started opens the next turn, so an owed
# announcement waits for that turn's stop.
prompt task-notification "<task-notification>v</task-notification>" -3
row '{"type":"assistant","message":{"role":"assistant","content":"Done."}}'
prompt task-notification "<task-notification>w</task-notification>" 5
mkdir -p "${OWED%/*}" && printf 'finished' > "$OWED"
check "$(stop 'Done.' unwritten)" "" "an event delivered after the stop is quiet"
check "$([ -e "$OWED" ] && echo owed)" "owed" "the owed announcement waits for that turn"
rm -f "$OWED"
: > "$TRANSCRIPT"

# usage: label <stdout>; runs the PostToolUse hook for a label add with that output.
label() {
  : > "$SPOKEN"
  printf '%s' "$1" > "$SANDBOX/stdout"
  jq -cn --rawfile o "$SANDBOX/stdout" '{hook_event_name:"PostToolUse", tool_name:"Bash",
    session_id:"s1", cwd:"/x/demo",
    tool_input:{command:"gh pr edit 12 --add-label \"Awaiting Final Review\""},
    tool_response:{stdout:$o}}' | "$HERE/speak-attention.sh" --config "$CONFIG"
  cat "$SPOKEN"
}

check "$(label 'https://github.com/o/r/pull/12')" \
  "demo session has pull request 12 awaiting final review" "a label add that went through speaks"
check "$(label '')" "" "a label add with no output is quiet"
big="$(head -c 200000 /dev/zero | tr '\0' x) https://github.com/o/r/pull/12"
check "$(label "$big")" \
  "demo session has pull request 12 awaiting final review" "a label add with long output speaks"

: > "$SANDBOX/voice.onnx"
prompt human "run the suite"
check "$(SPEAK_PIPER_MODEL="$SANDBOX/voice.onnx" stop 'Done.')" "piper: demo session finished" \
  "Piper speaks when its model is installed"
prompt human "run the suite"
check "$(PIPER_FAIL=1 SPEAK_PIPER_MODEL="$SANDBOX/voice.onnx" stop 'Done.')" \
  "demo session finished" "Speech Dispatcher speaks when Piper fails"
check "$(ls "$XDG_RUNTIME_DIR/speak-attention" | grep -c wav)" "0" "no clip is left behind"

# Piper options come from settings.json and are passed only when set
export PIPER_ARGS="$SANDBOX/piper-args"
settings="$XDG_RUNTIME_DIR/speak-attention/settings.json"
prompt human "run the suite"; : > "$PIPER_ARGS"
SPEAK_PIPER_MODEL="$SANDBOX/voice.onnx" stop 'Done.' > /dev/null
check "$(grep -cE -- '--(speaker|noise-scale|noise-w-scale|sentence-silence)' "$PIPER_ARGS")" 0 \
  "Piper options that are not set are left out"
echo '{"speaker":3,"noise":0.4,"noise_w":0.5,"silence":0.2}' > "$settings"
prompt human "run the suite"; : > "$PIPER_ARGS"
SPEAK_PIPER_MODEL="$SANDBOX/voice.onnx" stop 'Done.' > /dev/null
for opt in '--speaker 3' '--noise-scale 0.4' '--noise-w-scale 0.5' '--sentence-silence 0.2'; do
  check "$(grep -c -- "$opt" "$PIPER_ARGS")" 1 "Piper gets $opt when it is set"
done
echo '{"speaker":0}' > "$settings"
prompt human "run the suite"; : > "$PIPER_ARGS"
SPEAK_PIPER_MODEL="$SANDBOX/voice.onnx" stop 'Done.' > /dev/null
check "$(grep -c -- '--speaker 0' "$PIPER_ARGS")" 1 "speaker 0 is passed, not mistaken for unset"
check "$(grep -c -- '--noise-scale' "$PIPER_ARGS")" 0 "the options still unset stay out"
rm -f "$settings"

# A session's own voice, <id>.voice, wins over settings.json's for its lines alone.
piper_dir="$HOME/.local/share/piper"
mkdir -p "$piper_dir"
: > "$piper_dir/global.onnx"; : > "$piper_dir/own.onnx"; : > "$piper_dir/other.onnx"
echo '{"voice":"global"}' > "$settings"
run_dir="$XDG_RUNTIME_DIR/speak-attention"
# usage: model_used <extra env assignment...>; the model Piper was given for a stop.
model_used() {
  prompt human "run the suite"; : > "$PIPER_ARGS"
  stop 'Done.' > /dev/null
  grep -o -- '-m [^ ]*' "$PIPER_ARGS" | sed 's|.*/||'
}
check "$(model_used)" "global.onnx" "with no .voice file the global voice speaks"
printf %s own > "$run_dir/s1.voice"
check "$(model_used)" "own.onnx" "the session's .voice wins over the global voice"
printf %s other > "$run_dir/s2.voice"
check "$(model_used)" "own.onnx" "another session's .voice file is not used"
rm -f "$run_dir/s1.voice"
check "$(model_used)" "global.onnx" "another session's .voice file leaves this session on the global voice"
: > "$run_dir/s1.voice"
check "$(model_used)" "global.onnx" "an empty .voice file uses the global voice"
printf %s nosuchvoice > "$run_dir/s1.voice"
check "$(model_used)" "global.onnx" "an unknown voice falls back to the global voice"
check "$(stop 'Done.')" "piper: demo session finished" "an unknown voice still speaks the line"
printf %s ../piper/own > "$run_dir/s1.voice"
check "$(model_used)" "global.onnx" "a voice name with a slash is not used"
rm -f "$run_dir/s1.voice" "$run_dir/s2.voice" "$settings"
printf %s own > "$run_dir/s1.voice"
check "$(model_used)" "own.onnx" "the session's voice speaks with no global voice set"
rm -f "$run_dir/s1.voice"
unset PIPER_ARGS

# usage: ask <question> [cwd]; runs the PreToolUse hook for an AskUserQuestion call.
ask() {
  : > "$SPOKEN"
  jq -cn --arg q "$1" --arg c "${2:-/x/demo}" '{hook_event_name:"PreToolUse",
    tool_name:"AskUserQuestion", session_id:"s1", cwd:$c,
    tool_input:{questions:[{question:$q}]}}' |
    "$HERE/speak-attention.sh" --config "$CONFIG"
  cat "$SPOKEN"
}

row '{"type":"custom-title","customTitle":"Voice Session"}'
check "$(stop 'Done?')" "Voice session is waiting for you" \
  "a title ending in session says it once"
row '{"type":"custom-title","customTitle":"session "}'
check "$(stop 'Done?')" "session is waiting for you" "a bare session title says it once"
row '{"type":"custom-title","customTitle":"[UI] copy note"}'
check "$(stop 'Done?')" "U I copy note session is waiting for you" \
  "a session title says the spoken terms as configured"
: > "$TRANSCRIPT"
check "$(ask q /x/voice-session)" "voice session has a question" \
  "a folder name ending in -session says it once"
check "$(ask 'Which suite first?')" "demo session has a question" \
  "a question is announced, not read aloud"

# usage: typed <prompt>; runs the UserPromptSubmit hook for that prompt.
typed() {
  jq -cn --arg p "$1" --arg t "$TRANSCRIPT" '{hook_event_name:"UserPromptSubmit",
    session_id:"s1", prompt:$p, transcript_path:$t, cwd:"/x/demo"}' |
    "$HERE/speak-attention.sh" --config "$CONFIG"
}

# usage: skill <name> <args>; runs the PostToolUse hook for a Skill call.
skill() {
  jq -cn --arg s "$1" --arg a "$2" --arg t "$TRANSCRIPT" '{hook_event_name:"PostToolUse",
    tool_name:"Skill", session_id:"s1", transcript_path:$t, cwd:"/x/demo",
    tool_input:{skill:$s, args:$a}}' |
    "$HERE/speak-attention.sh" --config "$CONFIG"
}

# usage: speech_on; turns speech mode on as speechctl does, with the turn so far marked read.
speech_on() {
  mkdir -p "${OWED%/*}" && : > "${OWED%.owed}.replies" &&
    python3 "$HERE/speak_pending.py" "$TRANSCRIPT" "${OWED%.owed}.cursor" seen
}
# usage: speech_alerts; takes speech mode back to Alerts only, as speechctl does.
speech_alerts() { rm -f "${OWED%.owed}".{replies,queue}; }
# usage: managed; prints managed while the session is a managed session.
managed() { [[ -e ${OWED%.owed}.managed ]] && echo managed; }

: > "$TRANSCRIPT"
reply='## Status

Run [4638](https://github.com/o/r/issues/4638) is **green** at https://x.test/run.
See [`speak-attention.sh`](scripts/speak-attention.sh:90), [Worker](#local_1),
[o/r#12](https://github.com/o/r/pull/12), [Node.js](https://nodejs.org) and <https://x.test>.

| Spec | Result |
|------|--------|
| `a.spec.ts` | pass |

```bash
gh run list
```'
prompt human "run the suite"
check "$(stop 'Done.')" "demo session finished" "speech mode starts off"
speech_on
prompt human "run the suite"
said="demo session says: Status Run is green at the following link."
said+=" See, Worker, 12, Node.js and the following link."
check "$(stop "$reply")" "$said Spec Result a.spec.ts pass" \
  "speech mode reads the reply as plain text"
prompt human "time it"
said="demo session says: Took 7.0 seconds, the 30 seconds cap, 5 minutes, 2 hours,"
said+=" 1 hour 30 minutes and 1 minute; 3e4s, 10ms, option 1 m, the 1990s"
said+=", 1000s of rows and 3m rows stay; 5 minutes is fine after 30 seconds of idle."
spoken='Took 7.0s, the 30s cap, 5 min, 2 hrs, 1h30m and 1m; 3e4s, 10ms, option 1 m,'
spoken+=' the 1990s, 1000s of rows and 3m rows stay; 5m is fine after 30s of idle.'
check "$(stop "$spoken")" "$said" \
  "speech mode reads durations with their units spelled out"
prompt human "report the runs"
said="demo session says: U I passed, see the job; sequel and U I wait on the sign-ins;"
said+=" run red, run green; ui.chromium, passed 19 of 19 and each run"
said+=" 2 minutes apart stay."
spoken='[UI passed](https://github.com/o/r/actions/runs/39694/job/1195), see the'
spoken+=' [job 39694323023](https://github.com/o/r/actions/runs/39694323023/job/1); SQL and'
spoken+=' UI wait on the sign-ins; run 39694323023-1 red,'
spoken+=' run 4638 green https://github.com/o/r/actions/runs/4638; ui.chromium,'
spoken+=' [passed 19 of 19](https://github.com/o/r/actions/runs/1/job/2) and each run'
spoken+=' 2 min apart stay.'
check "$(stop "$spoken")" "$said" \
  "speech mode says the spoken terms and drops run links and ids"
prompt human "watch the run"
monitor
check "$(stop 'Watching.')" "demo session says: Watching." \
  "speech mode reads a reply held by background work"
stopped
typed "please /implement the next one"
check "$(stop 'Next.')$(managed)" "demo session says: Next." \
  "a prompt not opening with /implement leaves it on and makes no managed session"
skill implement "4638"
check "$(stop 'Working.')$(managed)" "demo session says: Working.managed" \
  "a Skill call to implement leaves it on and makes a managed session"
check "$(label 'https://github.com/o/r/pull/12')" "" "speech mode leaves the label to the reply"
rm -f "${OWED%.owed}.managed"
typed "/implement 4639"
check "$(stop 'Done.')$(managed)" "demo session says: Done.managed" \
  "a typed /implement leaves it on and makes a managed session"
speech_alerts; rm -f "${OWED%.owed}.managed"
typed "<command-message>implement</command-message>
<command-name>/general:implement</command-name>
<command-args>214</command-args>"
prompt human "go"
check "$(stop 'Done.')$(managed)" "demo session finishedmanaged" \
  "an expanded /general:implement leaves Alerts only and makes a managed session"
speech_on
prompt human "show the command"
check "$(stop '```bash
gh run list
```')" "" "a reply that is only code is quiet"
check "$(ask 'Which suite first?')" "" "speech mode drops the has-a-question announcement"
typed "/implementation 1"
check "$(stop 'Still.')" "demo session says: Still." "another command leaves the mode alone"

# usage: text <text>; appends an assistant row holding one text block, as the app writes
# a block ahead of the tool call that follows it.
text() {
  row "$(jq -cn --arg t "$1" '{type:"assistant",
    message:{role:"assistant", content:[{type:"text", text:$t}]}}')"
}

# usage: call [tool] [tool use id]; runs the PreToolUse hook for a tool call and prints
# what it said.
call() {
  : > "$SPOKEN"
  jq -cn --arg t "$TRANSCRIPT" --arg n "${1:-Bash}" --arg i "${2:-}" '{
    hook_event_name:"PreToolUse", tool_name:$n, session_id:"s1", transcript_path:$t,
    cwd:"/x/demo"} + (if $i == "" then {} else {tool_use_id:$i} end)' |
    "$HERE/speak-attention.sh" --config "$CONFIG"
  cat "$SPOKEN"
}

prompt human "run the sweep"
text "Cutting the branch now."
row '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use"}]}}'
check "$(call)" "demo session says: Cutting the branch now." \
  "text ahead of a tool call is read when the call starts"
check "$(call Read)" "" "a second call in the same message reads nothing again"
result '{}'
text "Dispatching **39** specs."
check "$(call)" "Dispatching 39 specs." "a later block is read without the name"
check "$(call)" "" "a call with no new text is quiet"
# The session moves its transcript when it enters a worktree, while a hook that began
# before the move still holds the old path.
check "$(TRANSCRIPT="$SANDBOX/moved/session.jsonl" call)" "" \
  "a call on a transcript that moved reads nothing"
check "$(TRANSCRIPT="$SANDBOX/moved/session.jsonl" stop 'Closing.' unwritten)" \
  "demo session says: Closing." "a stop on a transcript that moved still speaks its message"
text "Entered the worktree."
check "$(call)" "Entered the worktree." \
  "the next call on the new path reads only the block after the move"
text "The sweep is running."
check "$(stop 'The sweep is running.' unwritten)" "The sweep is running." \
  "the stop reads only the block no call has read"
prompt human "status?"
check "$(stop 'Half done.' unwritten)" "demo session says: Half done." \
  "the stop reads a reply the transcript has not written yet"
text "Half done."
check "$(call)" "" "the reply row written after the stop is not read twice"
prompt human "summarize"
text "Part one."
text "Part two."
check "$(stop 'Part one.

Part two.' unwritten)" "demo session says: Part one.
Part two." "a written reply of several blocks is read once"
prompt human "again"
text "Done."
result '{}'
check "$(stop 'Done.' unwritten)" "demo session says: Done.
Done." "a reply that repeats the block before it is still read"
prompt human "one more"
result '{}'
( sleep 1; text "Landed late." ) &
check "$(STOP_WAIT=5 stop 'Landed late.' unwritten)" "demo session says: Landed late." \
  "the stop waits for a reply the app writes late"
wait
prompt human "think first"
row '{"type":"assistant","message":{"role":"assistant","content":[{"type":"thinking"}]}}'
check "$(stop 'Thought it through.' unwritten)" "demo session says: Thought it through." \
  "a thinking row on disk does not stand in for the reply"
prompt human "run it"
text "First."
text "Second."
check "$(call)" "demo session says: First.
Second." "blocks that land together are read in order"
check "$([ -s "$XDG_RUNTIME_DIR/speak-attention/s1.queue" ] && echo queued)" "" \
  "nothing is left on the queue"
( sleep 1; text "Written late."
  row '{"type":"assistant","message":{"content":[{"type":"tool_use","id":"tu_9"}]}}' ) &
check "$(call Bash tu_9)" "Written late." "the call waits for a batch the app writes late"
wait
mkdir -p "$XDG_RUNTIME_DIR/speak-attention" && printf 'Queued earlier.\n' > \
  "$XDG_RUNTIME_DIR/speak-attention/s1.queue"
text "Next."
check "$(call)" "Queued earlier.
Next." "a block waiting on the queue is read before a newer one"
# a line another session queued is read in that session's voice, not the reading hook's
export PIPER_ARGS="$SANDBOX/piper-args"; : > "$PIPER_ARGS"
printf 'From s2.\n' > "$XDG_RUNTIME_DIR/speak-attention/s2.queue"
printf %s other > "$XDG_RUNTIME_DIR/speak-attention/s2.voice"
text "Mine."
printf %s own > "$XDG_RUNTIME_DIR/speak-attention/s1.voice"
check "$(call)" "piper: Mine.piper: From s2." \
  "another session's queued line is read in its own voice"
check "$(grep -o -- '-m [^ ]*' "$PIPER_ARGS" | sed 's|.*/||' | paste -sd,)" "own.onnx,other.onnx" \
  "each line is rendered with its own session's model"
unset PIPER_ARGS
rm -f "$XDG_RUNTIME_DIR/speak-attention"/s[12].voice "$XDG_RUNTIME_DIR/speak-attention"/s2.queue
prompt human "pick one"
text "Two ways to go."
row "$(jq -cn '{type:"assistant", message:{role:"assistant", content:[{type:"tool_use",
  id:"tu_q", name:"AskUserQuestion", input:{questions:[{question:"Which fix first?",
  options:[{label:"Fix 1"}, {label:"Fix 2"}, {label:"Neither"}]}]}}]}}')"
check "$(call AskUserQuestion tu_q)" "demo session says: Two ways to go.
Question: Which fix first? Options: Fix 1, Fix 2, or Neither." \
  "a question call is read with its options after the text ahead of it"
result '{}'
text "Merged the fix."
row "$(jq -cn '{type:"assistant", message:{role:"assistant", content:[{type:"tool_use",
  id:"tu_w", name:"mcp__ccd_turn__wrap_up", input:{recap:"Fixed.", ask:"Open the PR?",
  actions:[{action:"create_pr"}, {label:"Not now"}]}}]}}')"
check "$(call mcp__ccd_turn__wrap_up tu_w)" "Merged the fix." \
  "a wrap-up call holds its question back"
text "All green."
check "$(stop 'All green.' unwritten)" "All green.
Question: Open the PR? Options: create pr or Not now." \
  "the stop reads the wrap-up question after the closing reply"
text "One more fix."
check "$(call)" "demo session says: One more fix." \
  "a turn that goes on after its stop reads the next block"
text "Still green."
check "$(stop 'Still green.' unwritten)" "Still green." \
  "the wrap-up question already read is not read again"
row "$(jq -cn '{type:"assistant", message:{role:"assistant", content:[{type:"tool_use",
  id:"tu_m", name:"AskUserQuestion", input:{questions:[{question:"Pick the suites",
  multiSelect:true, options:[{label:"UI"}, {label:"SQL"}]}]}}]}}')"
said="demo session says: Question: Pick the suites? Pick any of: U I and sequel."
check "$(call AskUserQuestion tu_m)" "$said" \
  "a multi-select question says any of them can be picked"
row "$(jq -cn '{type:"assistant", message:{role:"assistant", content:[{type:"tool_use",
  id:"tu_x", name:"mcp__ccd_turn__wrap_up", input:{recap:"Done.", ask:"Push it?"}}]}}')"
row "$(jq -cn '{type:"assistant", message:{role:"assistant", content:[{type:"tool_use",
  id:"tu_y", name:"mcp__ccd_turn__wrap_up", input:{recap:"Done."}}]}}')"
text "Pushed."
check "$(stop 'Pushed.' unwritten)" "Pushed." "only the last wrap-up call's question is read"
prompt human "and now"
row "$(jq -cn '{type:"assistant", message:{role:"assistant", content:[{type:"tool_use",
  id:"tu_r", name:"mcp__ccd_turn__wrap_up", input:{recap:"Done."}}]}}')"
text "Nothing left."
check "$(stop 'Nothing left.' unwritten)" "demo session says: Nothing left." \
  "a wrap-up with no question reads only the reply"
prompt human "push it"
text "Pushed."
text "Then this."
check "$(CLAUDE_CODE_MESSAGING_SOCKET=/x/77.sock call)" "demo session says: Pushed.
Then this." "a socket session still reads aloud"
check "$(jq -c '[.[].text]' "$XDG_RUNTIME_DIR/voice-bridge/feed/77.json")" \
  '["demo session says: Pushed.\n\nThen this."]' "the blocks reach the voice feed as one entry"
speech_alerts
prompt human "run it"
text "Quiet."
check "$(call)" "" "a tool call outside speech mode is quiet"
prompt human "followed run"
text "Cutting the branch."
FOLLOW_DIR="$XDG_RUNTIME_DIR/voice-bridge/follow"
mkdir -p "$FOLLOW_DIR" && : > "$FOLLOW_DIR/88"
check "$(CLAUDE_CODE_MESSAGING_SOCKET=/x/88.sock call)" "" \
  "a followed session outside speech mode says nothing aloud"
check "$(jq -c '[.[].text]' "$XDG_RUNTIME_DIR/voice-bridge/feed/88.json")" \
  '["demo session says: Cutting the branch."]' \
  "mid-turn text reaches the feed of a followed session"
text "Dispatching."
CLAUDE_CODE_MESSAGING_SOCKET=/x/88.sock call > /dev/null
check "$(jq -c '[.[].text]' "$XDG_RUNTIME_DIR/voice-bridge/feed/88.json")" \
  '["demo session says: Cutting the branch.","Dispatching."]' \
  "a later block is added once"
result '{}'
CLAUDE_CODE_MESSAGING_SOCKET=/x/88.sock stop 'Final reply.' unwritten > /dev/null
check "$(jq 'length' "$XDG_RUNTIME_DIR/voice-bridge/feed/88.json")" "2" \
  "the stop leaves the final reply to the bridge's own hook"
text "Final reply."
CLAUDE_CODE_MESSAGING_SOCKET=/x/88.sock call > /dev/null
check "$(jq 'length' "$XDG_RUNTIME_DIR/voice-bridge/feed/88.json")" "2" \
  "a stop that goes on does not send the final reply later"
prompt human "ask me"
row "$(jq -cn '{type:"assistant", message:{role:"assistant", content:[{type:"tool_use",
  id:"tu_f", name:"AskUserQuestion", input:{questions:[{question:"Ship it?",
  options:[{label:"Yes"}, {label:"No"}]}]}}]}}')"
check "$(CLAUDE_CODE_MESSAGING_SOCKET=/x/88.sock call AskUserQuestion tu_f)" \
  "demo session has a question" "a followed question is still announced aloud"
check "$(jq -r '.[-1].text' "$XDG_RUNTIME_DIR/voice-bridge/feed/88.json" | head -1)" \
  "demo session says: Question: Ship it? Options: Yes or No." \
  "a followed question reaches the feed"
prompt human "wrap up"
text "Late note."
result '{}'
CLAUDE_CODE_MESSAGING_SOCKET=/x/88.sock stop 'Final two.' > /dev/null
check "$(jq 'length' "$XDG_RUNTIME_DIR/voice-bridge/feed/88.json")" "3" \
  "the stop leaves the feed to the bridge's own hook"
text "After the stop."
CLAUDE_CODE_MESSAGING_SOCKET=/x/88.sock call > /dev/null
check "$(jq -r '.[-1].text' "$XDG_RUNTIME_DIR/voice-bridge/feed/88.json")" \
  "demo session says: After the stop." "a turn that goes on after its stop is fed again"
touch -d '2 hours ago' "$FOLLOW_DIR/88"
text "Stale follow."
CLAUDE_CODE_MESSAGING_SOCKET=/x/88.sock call > /dev/null
check "$(jq 'length' "$XDG_RUNTIME_DIR/voice-bridge/feed/88.json")" "4" \
  "a follow nobody has polled lately feeds nothing"
rm -f "$FOLLOW_DIR/88"
text "Unfollowed."
CLAUDE_CODE_MESSAGING_SOCKET=/x/88.sock call > /dev/null
check "$(jq 'length' "$XDG_RUNTIME_DIR/voice-bridge/feed/88.json")" "4" \
  "an unfollowed session feeds nothing"
# now.json carries the Markdown of the line playing, beside the spoken text.
export NOWLOG="$SANDBOX/now-log"
QUEUES="$XDG_RUNTIME_DIR/speak-attention"
# usage: now <jq filter>; the filter applied to every now.json the stubs logged, as an array.
now() { jq -sc "map($1)" "$NOWLOG"; }
speech_on
prompt human "write it up"
: > "$NOWLOG"
text "Cutting the branch now."
check "$(call)" "demo session says: Cutting the branch now." "a plain line is read as before"
check "$(now '[.session, .name, .text, .markdown]')" \
  '[["s1","demo session","demo session says: Cutting the branch now.","Cutting the branch now."]]' \
  "a plain line publishes its source without the name prefix"
check "$(now 'keys | join(",")')" \
  '["clip,engine,hook_pid,markdown,name,player_pid,session,started,text"]' \
  "now.json keeps its other fields beside markdown"

md='Two things changed:

- **Spacing**: the gap is now `12px`.
- Avatar alignment: see [the PR](https://github.com/o/r/pull/9).

```bash
make test
```

Done.'
: > "$NOWLOG"
text "$md"
call > /dev/null
check "$(now '.markdown')" "$(jq -cn --arg m "$md" '[$m]')" \
  "a multi-paragraph line keeps its list, bold, code span, fence and newlines"
check "$(now '.text | contains("**") or contains("`") or contains("\n")')" "[false]" \
  "the same line's text is still the flat spoken form"

: > "$NOWLOG"
text "$(printf '\n\n  Indented first line.\n\n\n')"
call > /dev/null
check "$(now '.markdown')" '["  Indented first line."]' \
  "blank lines around a block are trimmed, its indentation kept"

# a source past the cap is cut at a line boundary and ends in an ellipsis
long=$(for i in $(seq 1 400); do echo "line $i of a long reply"; done)
: > "$NOWLOG"
: > "$QUEUES/s1.fulltext"
text "$long"
call > /dev/null
check "$(now '.markdown | [length <= 2001, endswith("…"), (split("\n") | length > 3),
  (split("\n") | .[-1] | test("^line [0-9]+ of a long reply…$"))] | all')" "[true]" \
  "a long source is cut at a line boundary and marked"
check "$(now '.text | length > 4000')" "[true]" "the cap leaves the spoken text whole"
rm -f "$QUEUES/s1.fulltext"

# the cut falls after a complete line, not before it, and a long run of space is quick
exact="$(head -c 1990 /dev/zero | tr '\0' x)
tail line
after the cap"
: > "$NOWLOG"
text "$exact"
call > /dev/null
check "$(now '.markdown | endswith("tail line…")')" "[true]" \
  "a source cut exactly at the end of a line keeps that line"
: > "$NOWLOG"
text "start$(head -c 60000 /dev/zero | tr '\0' ' ')end"
began=$(date +%s)
call > /dev/null
check "$(( $(date +%s) - began < 10 ))" "1" \
  "a block with a long run of spaces queues quickly"

# trailing space past the cap is not content, and a multibyte source survives the read
: > "$NOWLOG"
text "$(head -c 1990 /dev/zero | tr '\0' x)$(printf ' %.0s' $(seq 1 50))"
call > /dev/null
check "$(now '.markdown | [length, endswith("…")]')" "[[1990,false]]" \
  "space past the cap does not cut the line before it"
cjk="x$(printf '日%.0s' $(seq 1 3000))"
: > "$NOWLOG"
text "$cjk"
call > /dev/null
check "$(now '.markdown | [length, (explode | any(. == 65533)), endswith("…")]')" \
  "[[2001,false,true]]" "a multibyte source over 4 KB is cut whole, with no replacement characters"

# Long text is read in short. The queue keeps the block as written; the voice feed gets it whole.
filler=$(for i in $(seq 1 60); do printf 'Detail %s of the run. ' "$i"; done)
ready_reply="PULL REQUEST 214 IS READY FOR YOUR REVIEW

Checks passed. $filler"
full_text() { [[ $1 == *"Detail 60 of the run."* ]] && echo whole || echo short; }
prompt human "finish up"
check "$(stop "$ready_reply")" "demo session says: Pull request 214 is ready for review." \
  "a ready reply is read as one short line"
prompt human "finish up again"
: > "$NOWLOG"
text "**PULL REQUEST #215** IS READY FOR YOUR REVIEW. $filler"
check "$(call)" "demo session says: Pull request 215 is ready for review." \
  "a ready line with emphasis around its number is read as one short line"
check "$(now '.markdown | startswith("**PULL REQUEST #215** IS READY")')" "[true]" \
  "the ready line's queue source is the reply as written"
prompt human "explain"
: > "$NOWLOG"
text "The suite passed after one fix. $filler"
check "$(call)" "demo session says: The suite passed after one fix. The rest is on screen." \
  "a long reply is read as its opening sentence"
check "$(now '.markdown | startswith("The suite passed after one fix. Detail 1 of")')" "[true]" \
  "the long reply's queue source is the reply as written"
prompt human "list"
text "$(printf '## Summary\n\n1. Fixed the parser.\n2. Added tests.\n\n%s' "$filler")"
check "$(call)" "demo session says: Summary 1. Fixed the parser. The rest is on screen." \
  "a long reply that opens with a heading and a list is cut after the first item, not at its marker"
prompt human "short one"
text "Two files changed. Tests pass."
check "$(call)" "demo session says: Two files changed. Tests pass." "a short reply is read whole"
prompt human "followed"
text "$ready_reply"
CLAUDE_CODE_MESSAGING_SOCKET=/x/79.sock call > /dev/null
check "$(full_text "$(jq -r '.[-1].text' "$XDG_RUNTIME_DIR/voice-bridge/feed/79.json")")" whole \
  "the voice feed still gets the ready reply whole"
: > "$QUEUES/s1.fulltext"
prompt human "full ready"
text "$ready_reply"
check "$(full_text "$(call)")" whole "the full-text marker reads a ready reply whole"
prompt human "full long"
text "The suite passed after one fix. $filler"
check "$(full_text "$(call)")" whole "the full-text marker reads a long reply whole"
rm -f "$QUEUES/s1.fulltext"
jq '.fullSpeech = true' "$CONFIG" > "$SANDBOX/full.json"
prompt human "config full"
text "$ready_reply"
check "$(full_text "$(CONFIG="$SANDBOX/full.json" call)")" whole \
  "fullSpeech in the extension file reads a ready reply whole"
prompt human "default again"
text "$ready_reply"
check "$(call)" "demo session says: Pull request 214 is ready for review." \
  "with neither opt-out set, a ready reply is read as one short line again"

# another session's queue: its line plays with its own source, after this session's own
printf 'Other session.' > "$QUEUES/s2.name"
printf '%s\t%s\n' "other session says: Merged it." \
  "$(jq -cn '"Merged **it**.\n\n- one\n- two"')" > "$QUEUES/s2.queue"
: > "$NOWLOG"
text "Own line."
call > /dev/null
check "$(now '[.session, .text, .markdown]')" \
  '[["s1","Own line.","Own line."],["s2","other session says: Merged it.","Merged **it**.\n\n- one\n- two"]]' \
  "a line read from another session's queue publishes that session and its own source"
rm -f "$QUEUES/s2.queue" "$QUEUES/s2.name"

# a line paused away is put back with its source and published again
: > "$NOWLOG"
rm -f "$SANDBOX/requeued"
text "Requeued **line**."
check "$(REQUEUE_ONCE="$SANDBOX/requeued" call)" "Requeued line." \
  "a line whose clip was paused away is read again"
check "$(now '[.text, .markdown]')" \
  '[["Requeued line.","Requeued **line**."],["Requeued line.","Requeued **line**."]]' \
  "a requeued line publishes the same text and source both times"

# Piper publishes it too, in the publish that stays up while the clip plays
: > "$NOWLOG"
text "Piper **line**."
SPEAK_PIPER_MODEL="$SANDBOX/voice.onnx" call > /dev/null
check "$(now '[.engine, .player_pid != null, .markdown]')" '[["piper",true,"Piper **line**."]]' \
  "Piper publishes the source"

# a line with no source: a queue line from before the field, and one the hook composes
: > "$NOWLOG"
printf 'Queued earlier.\n' > "$QUEUES/s1.queue"
call > /dev/null
check "$(now '[.text, .markdown]')" '[["Queued earlier.",""]]' \
  "a queue line with no source publishes an empty markdown"
speech_alerts
prompt human "run the suite"
: > "$NOWLOG"
stop 'Done.' > /dev/null
check "$(now '[.text, .markdown]')" '[["demo session finished",""]]' \
  "an announcement the hook composes publishes an empty markdown"
unset NOWLOG

# A managed session writes every block to its feed, whatever its speech setting.
speech_alerts
: > "$TRANSCRIPT"
FEED="$QUEUES/s1.feed"
# usage: fed <jq filter>; the filter applied to every feed entry, as an array.
fed() { jq -sc "map($1)" "$FEED" 2>/dev/null; }
# the /implement cases above made this session managed; start from an unmanaged one
rm -f "$QUEUES/s1.managed" "$FEED" "$QUEUES/s1.feed-cursor"
prompt human "unmanaged"
text "Not fed."
call > /dev/null
check "$([ -e "$FEED" ] && echo fed)" "" "a session that is not managed has no feed"
: > "$QUEUES/s1.managed"
export NOWLOG="$SANDBOX/now-log"
: > "$NOWLOG"
prompt human "managed alerts"
text 'Cutting **the** branch.'
check "$(call)" "" "a managed session on Alerts reads nothing aloud"
check "$(fed '[.session, .name, .text, .markdown, (.at | type)]')" \
  '[["s1","demo session","Cutting the branch.","Cutting **the** branch.","number"]]' \
  "its block reaches the feed with its name, spoken text and Markdown"
check "$([ -s "$QUEUES/s1.queue" ] && echo queued)$(cat "$NOWLOG")" "" \
  "a fed block is not queued and publishes no now.json"
check "$(call)" "" "a call with no new text is quiet"
check "$(fed .text | jq length)" "1" "the block is fed once"
result '{}'
check "$(stop 'All green.' unwritten)" "demo session finished" \
  "a managed session on Alerts still announces its stop"
check "$(fed .text)" '["Cutting the branch.","All green."]' "the final reply reaches the feed"
prompt human "code only"
text '```bash
gh run list
```'
call > /dev/null
check "$(fed .markdown | jq -r '.[-1]')" '```bash
gh run list
```' "a block with nothing to say aloud is still fed"
check "$(fed .text | jq -r '.[-1]')" "" "and its spoken text is empty"
: > "$QUEUES/s1.muted"
prompt human "managed off"
text "Muted line."
check "$(call)" "" "a managed session set to Off reads nothing aloud"
result '{}'
check "$(stop 'Muted reply.' unwritten)" "" "and announces nothing"
check "$(fed .text | jq -c '.[-2:]')" '["Muted line.","Muted reply."]' \
  "a managed session set to Off still feeds every block"
check "$(jq -sc "map(.text)" "$NOWLOG")" '["demo session finished"]' \
  "the only clip while it was Off or on Alerts was the stop's announcement"
: > "$NOWLOG"
speech_on
prompt human "managed on"
text "Spoken line."
check "$(call)" "demo session says: Spoken line." "a managed session set to On still reads aloud"
check "$(jq -r .text "$NOWLOG")" "demo session says: Spoken line." "and publishes now.json"
check "$(fed .text | jq -r '.[-1]')" "Spoken line." "and feeds the block too"
speech_alerts
unset NOWLOG
FOLLOW_DIR="$XDG_RUNTIME_DIR/voice-bridge/follow"
: > "$FOLLOW_DIR/88"
prompt human "managed and followed"
text "Followed line."
CLAUDE_CODE_MESSAGING_SOCKET=/x/88.sock call > /dev/null
bridge_feed="$XDG_RUNTIME_DIR/voice-bridge/feed/88.json"
fed_before=$(jq length "$bridge_feed")
check "$(jq -r '.[-1].text' "$bridge_feed")" "demo session says: Followed line." \
  "a managed, followed call still sends its text to the voice feed"
result '{}'
CLAUDE_CODE_MESSAGING_SOCKET=/x/88.sock stop 'Followed reply.' unwritten > /dev/null
check "$(jq length "$bridge_feed")" "$fed_before" \
  "a managed, followed stop still leaves the final reply to the bridge's own hook"
check "$(fed .text | jq -c '.[-2:]')" '["Followed line.","Followed reply."]' \
  "while the session's feed gets both blocks"
rm -f "$FOLLOW_DIR/88"
# speechctl turning speech on marks the speech cursor read before the hook takes the lock
prompt human "speech turns on mid-turn"
text "Written before speech turned on."
python3 "$HERE/speak_pending.py" "$TRANSCRIPT" "$QUEUES/s1.cursor" seen
: > "$QUEUES/s1.replies"
check "$(call)" "" "speech turned on reads nothing already written"
check "$(fed .text | jq -r '.[-1]')" "Written before speech turned on." \
  "but the feed still gets the block speech skipped"
rm -f "$QUEUES/s1.replies"
for i in $(seq 200); do printf '{"text":"old %s"}\n' "$i"; done > "$FEED"
prompt human "long session"
text "Newest."
call > /dev/null
check "$(fed .text | jq -c '[length, .[0], .[-1]]')" '[200,"old 2","Newest."]' \
  "the feed keeps the last 200 blocks"
rm -f "$QUEUES/s1.managed" "$FEED" "$QUEUES/s1.feed-cursor"
call > /dev/null

speech_alerts
: > "$TRANSCRIPT"

[ "$fails" -eq 0 ] || { echo "$fails failed"; exit 1; }
echo "all passed"
