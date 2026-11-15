#!/usr/bin/env bash
# Cases for speechctl and for the state speak-attention.sh keeps for it. Stub players
# stand in for pw-play, piper and spd-say, so nothing is spoken; the stub pw-play plays for
# PLAY seconds and records the text only if it plays to the end.
# usage: bash speechctl_test.sh
set -uo pipefail

for bin in jq python3 flock; do
  command -v "$bin" > /dev/null || { echo "$bin is required"; exit 1; }
done

HERE="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$HERE/test-config.json"
CTL="$HERE/speechctl"
SANDBOX="$(mktemp -d)"
trap 'kill $(jobs -p) 2>/dev/null; rm -rf "$SANDBOX"' EXIT

export HOME="$SANDBOX/home"
mkdir -p "$SANDBOX/bin" "$HOME/.local/bin" "$HOME/.local/share/piper" "$HOME/.claude/projects/p"
printf '%s\n' '#!/bin/sh' 'echo "$*" >> "${PIPER_ARGS:-/dev/null}"' 'sleep "${PIPER_WAIT:-0}"' \
  'while [ $# -gt 0 ] && [ "$1" != -f ]; do shift; done' 'cat > "$2"' \
  > "$HOME/.local/bin/piper"
printf '%s\n' '#!/bin/bash' 'echo "$*" >> "$ARGS"' 'for a in "$@"; do last=$a; done' \
  'sleep "${PLAY:-1}" &' 'wait' 'printf "piper: %s\n" "$(cat "$last")" >> "$SPOKEN"' \
  > "$SANDBOX/bin/pw-play"
printf '%s\n' '#!/bin/sh' '[ "$1" = -O ] && exit 0' '[ "$1" = -C ] && exit 0' \
  'for a in "$@"; do last=$a; done' 'echo "spd: $last" >> "$SPOKEN"' > "$SANDBOX/bin/spd-say"
chmod +x "$HOME/.local/bin/piper" "$SANDBOX/bin/pw-play" "$SANDBOX/bin/spd-say"
# pw-dump lists two PipeWire clients and their stream nodes: client 85 belongs to the process
# in now.json's player_pid, client 86 to an unrelated one. pw-cli records what it is asked.
printf '%s\n' '#!/bin/sh' \
  'pid=$(jq -r ".player_pid // 0" "$XDG_RUNTIME_DIR/speak-attention/now.json" 2>/dev/null)' \
  'jq -n --argjson pid "${pid:-0}" '"'"'[{id:85,type:"PipeWire:Interface:Client",info:{props:{"application.process.id":$pid}}},{id:86,type:"PipeWire:Interface:Client",info:{props:{"application.process.id":1}}},{id:90,type:"PipeWire:Interface:Node",info:{props:{"client.id":85,"media.class":"Stream/Output/Audio"}}},{id:91,type:"PipeWire:Interface:Node",info:{props:{"client.id":86,"media.class":"Stream/Output/Audio"}}},{id:92,type:"PipeWire:Interface:Node",info:{props:{"client.id":85,"media.class":"Audio/Sink"}}}]'"'" \
  > "$SANDBOX/bin/pw-dump"
printf '%s\n' '#!/bin/sh' 'echo "$*" >> "$PWCLI"' > "$SANDBOX/bin/pw-cli"
chmod +x "$SANDBOX/bin/pw-dump" "$SANDBOX/bin/pw-cli"
# a process whose name is spd-say, to stand in for a Speech Dispatcher clip's player
mkdir "$SANDBOX/spd" && cp "$(command -v sleep)" "$SANDBOX/spd/spd-say"
export PATH="$SANDBOX/bin:$PATH"
: > "$HOME/.local/share/piper/en_US-amy-medium.onnx"
: > "$HOME/.local/share/piper/en_US-ryan-high.onnx"
export SPEAK_PIPER_MODEL="$HOME/.local/share/piper/en_US-amy-medium.onnx"
export SPEAK_PIPER_DIR="$HOME/.local/share/piper"
export XDG_RUNTIME_DIR="$SANDBOX/run"
export SPOKEN="$SANDBOX/spoken" ARGS="$SANDBOX/args" STOP_WAIT=0
D="$XDG_RUNTIME_DIR/speak-attention"
TRANSCRIPT="$SANDBOX/s1.jsonl"
fails=0

check() {
  if [ "$1" = "$2" ]; then echo "ok   $3"; else
    echo "FAIL $3: got [$1], wanted [$2]"; fails=$((fails + 1)); fi
}

# usage: fresh; clears all state and gives the session a transcript and speech on.
fresh() {
  kill $(jobs -p) 2>/dev/null; wait 2>/dev/null
  rm -rf "$D"; mkdir -p "$D"; : > "$SPOKEN"; : > "$ARGS"
  printf '%s\n' '{"type":"user","origin":{"kind":"human"},"message":{"role":"user","content":"hi"}}' \
    > "$TRANSCRIPT"
  : > "$D/s1.replies"
}
# usage: queue <line>...; appends lines to s1's queue.
queue() { printf '%s\n' "$@" >> "$D/s1.queue"; }
# usage: hook; runs a Stop hook for s1 in the background, which reads the queue.
hook() {
  jq -cn --arg t "$TRANSCRIPT" '{hook_event_name:"Stop", session_id:"s1", transcript_path:$t,
    last_assistant_message:"", cwd:"/x/demo"}' | "$HERE/speak-attention.sh" --config "$CONFIG" &
  HOOK=$!
}
# usage: until <seconds> <command...>; polls until the command succeeds.
until_() {
  local n=$(($1 * 10)); shift
  while ! "$@" 2>/dev/null; do ((n-- > 0)) || return 1; sleep 0.1; done
}
playing() { [[ -n $(jq -r '.player_pid // empty' "$D/now.json" 2>/dev/null) ]]; }
gone() { ! kill -0 "$1" 2>/dev/null; }
state() { sed 's/.*) //; s/ .*//' "/proc/$1/stat"; }
spoken() { tr '\n' '|' < "$SPOKEN"; }

# --- skip and next
fresh; queue "one" "two"; export PLAY=1; hook
until_ 5 playing; "$CTL" skip
until_ 10 gone $HOOK
check "$(spoken)" "piper: two|" "skip ends the clip and the next line plays"
check "$([[ -e $D/now.json ]] && echo left || echo clean)" clean "now.json is gone after the last clip"

fresh; queue "one" "two" "three"; hook
until_ 5 playing; "$CTL" next
until_ 10 gone $HOOK
check "$(spoken)" "" "next ends the clip and drops the rest of the session's queue"

fresh; : > "$D/s2.replies"; printf '%s\n' "other" > "$D/s2.queue"; touch -d '1 minute ago' "$D/s2.queue"
queue "one" "two"; hook
until_ 5 playing; "$CTL" next; "$CTL" next
until_ 10 gone $HOOK
check "$(spoken)" "piper: other|" "next goes on to the next session's reply"

fresh; queue "one"; hook
until_ 5 playing
"$CTL" clear; until_ 10 gone $HOOK
check "$(spoken)$(cat "$D"/*.queue 2>/dev/null)" "" "clear empties every queue and ends the clip"

# --- pause and resume
fresh; queue "one" "two"; hook
until_ 5 playing; "$CTL" pause; PID=$(jq -r .player_pid "$D/now.json"); sleep 0.3
check "$(state "$PID")" T "pause stops the player"
check "$("$CTL" status --json | jq -r .paused)" true "status reports paused"
"$CTL" resume
until_ 10 gone $HOOK
check "$(spoken)" "piper: one|piper: two|" "resume continues, each line once and in order"

fresh; touch "$D/paused"; queue "one" "two"; hook
sleep 1.5
check "$(wc -l < "$D/s1.queue")" 2 "a paused voice leaves the queue alone"
rm -f "$D/paused"; until_ 10 gone $HOOK
check "$(spoken)" "piper: one|piper: two|" "lines held by a pause are read after it, once each"

fresh; queue "one"; hook
until_ 5 playing; "$CTL" toggle; check "$([[ -e $D/paused ]] && echo yes)" yes "toggle pauses"
"$CTL" toggle; check "$([[ -e $D/paused ]] && echo yes || echo no)" no "toggle resumes"
until_ 10 gone $HOOK

# --- a queue line carries its Markdown source after a tab
fresh; touch "$D/paused"; queue "$(printf 'one\t"**one**"')" "two"
check "$("$CTL" status --json | jq -c '.queues[0] | [.lines, .next]')" '[2,"one"]' \
  "status shows a queued line's spoken text without its source"
rm -f "$D/paused"; : > "$D/s1.queue"

# --- a killed hook leaves no player and no now.json
fresh; queue "one"; hook
until_ 5 playing; PID=$(jq -r .player_pid "$D/now.json"); kill -TERM $HOOK
until_ 5 gone $HOOK; sleep 0.2
check "$([[ -e $D/now.json ]] && echo left || echo clean)" clean "a killed hook removes now.json"
check "$(gone "$PID" && echo gone || echo running)" gone "a killed hook ends its player"

# --- settings
fresh
check "$("$CTL" volume 0.5)" 0.5 "volume takes a number"
check "$("$CTL" volume up)" 0.6 "volume up steps by a tenth"
"$CTL" volume 3 2>/dev/null; check "$?" 2 "a volume out of range is refused"
"$CTL" volume loud 2>/dev/null; check "$?" 2 "a volume that is no number is refused"
check "$(jq -r .volume "$D/settings.json")" 0.6 "volume is saved in settings.json"

# --- a volume change reaches the clip already playing
export PWCLI="$SANDBOX/pwcli"
fresh; : > "$PWCLI"; queue "one"; PLAY=3 hook
until_ 5 playing; "$CTL" volume 0.5 > /dev/null
check "$(cat "$PWCLI")" "set-param 90 Props { volume: 0.5 }" \
  "volume sets the playing Piper clip's stream and no other"
"$CTL" volume up > /dev/null
check "$(tail -n 1 "$PWCLI")" "set-param 90 Props { volume: 0.6 }" "volume up reaches it too"
check "$(jq -r .volume "$D/settings.json")" 0.6 "the level is saved as well"
"$CTL" clear; until_ 10 gone $HOOK

fresh; : > "$PWCLI"; "$CTL" volume 0.5 > /dev/null
check "$(cat "$PWCLI")" "" "volume with nothing playing touches no stream"
check "$(jq -r .volume "$D/settings.json")" 0.5 "and still saves the level"

fresh; : > "$PWCLI"; queue "one"; PIPER_WAIT=2 PLAY=0.2 hook
until_ 5 test -e "$D/now.json"
check "$(jq -r '.player_pid' "$D/now.json")" null "the clip is still rendering"
"$CTL" volume 0.5 > /dev/null
check "$(cat "$PWCLI")" "" "a clip that is still rendering has no stream to set"
until_ 10 gone $HOOK
check "$(grep -c -- '--volume 0.5' "$ARGS")" 1 "a volume set during the render is the level the clip plays at"

fresh; : > "$PWCLI"
"$SANDBOX/spd/spd-say" 30 & SPD=$!
jq -cn --argjson h $$ --argjson p $SPD '{session:"s1",name:"demo",text:"x",markdown:"x",started:0,clip:"1",
  hook_pid:$h, player_pid:$p, engine:"spd-say"}' > "$D/now.json"
"$CTL" volume 0.5 > /dev/null
check "$(cat "$PWCLI")" "" "a Speech Dispatcher clip keeps its own level"
check "$(jq -r .volume "$D/settings.json")" 0.5 "and the level is saved"
kill $SPD

# --- settings, continued
check "$(env -u SPEAK_PIPER_LENGTH "$CTL" pace up)" 0.9 "pace up steps from the 0.85 default by a twentieth"
check "$("$CTL" pace 1.0)" 1.0 "pace takes a number"
check "$("$CTL" pace down)" 0.95 "pace down steps by a twentieth"
check "$("$CTL" pace up)" 1.0 "pace steps without float drift"
check "$("$CTL" pace 1.5)" 1.5 "pace takes the top of its range"
check "$("$CTL" pace up)" 1.5 "pace up stops at 1.5"
check "$("$CTL" pace 0.5)" 0.5 "pace takes the bottom of its range"
check "$("$CTL" pace down)" 0.5 "pace down stops at 0.5"
"$CTL" pace 1.6 2>/dev/null; check "$?" 2 "a pace above the range is refused"
"$CTL" pace 0.4 2>/dev/null; check "$?" 2 "a pace below the range is refused"
"$CTL" pace fast 2>/dev/null; check "$?" 2 "a pace that is no number is refused"
"$CTL" pace nan 2>/dev/null; check "$?" 2 "a pace of nan is refused"
check "$(jq -r .pace "$D/settings.json")" 0.5 "pace is saved in settings.json"
out=$("$CTL" pace 2 2>&1 >/dev/null); code=$?
check "$code:${out:+msg}" "2:msg" "a refused pace exits 2 with a message"
printf '{"pace": "quick"}' > "$D/settings.json"
check "$(env -u SPEAK_PIPER_LENGTH "$CTL" pace down)" 0.8 \
  "pace down from a saved pace that is no number steps from the default"
rm "$D/settings.json"
check "$(SPEAK_PIPER_LENGTH=slow "$CTL" pace up)" 0.9 \
  "pace up from a SPEAK_PIPER_LENGTH that is no number steps from the default"
rm "$D/settings.json"
check "$(SPEAK_PIPER_LENGTH=3 "$CTL" pace down)" 1.5 \
  "pace down from a SPEAK_PIPER_LENGTH above the range clamps to 1.5"
check "$("$CTL" pace 0.9)" 0.9 "pace 0.9 sets the pace"
check "$("$CTL" status --json | jq -r .pace)" 0.9 "status --json reports the saved pace"
check "$("$CTL" voice next)" en_US-ryan-high "voice next cycles the installed models"
check "$("$CTL" voice prev)" en_US-amy-medium "voice prev cycles back"
"$CTL" voice nobody 2>/dev/null; check "$?" 2 "an unknown voice is refused"
check "$("$CTL" voices | tr '\n' '|')" "* en_US-amy-medium|  en_US-ryan-high|" "voices lists them"
"$CTL" voice en_US-ryan-high > /dev/null; "$CTL" volume 0.5 > /dev/null; : > "$SANDBOX/piper-args"
queue "one"; PLAY=0.2 PIPER_ARGS="$SANDBOX/piper-args" hook
until_ 10 gone $HOOK
check "$(grep -c -- '--volume 0.5' "$ARGS")" 1 "the next clip plays at the saved volume"
check "$(grep -c -- '--length-scale 0.9 ' "$SANDBOX/piper-args")" 1 \
  "the next clip uses the saved pace with no restart"

# --- Piper options
fresh
printf '{"num_speakers": 4}' > "$HOME/.local/share/piper/en_US-ryan-high.onnx.json"
check "$("$CTL" voices | tr '\n' '|')" "* en_US-amy-medium|  en_US-ryan-high (4 speakers)|" \
  "voices says how many speakers a multi-speaker model has"
check "$("$CTL" speaker 2)" 2 "speaker takes a number"
check "$(jq -c '[.speaker, (.noise // "none")]' "$D/settings.json")" '[2,"none"]' \
  "speaker is saved and the others stay unset"
check "$("$CTL" noise 0.3)" 0.3 "noise takes a number"
check "$("$CTL" noise-w 0.9)" 0.9 "noise-w takes a number"
check "$("$CTL" silence 0.5)" 0.5 "silence takes seconds"
check "$(jq -c '[.noise, .noise_w, .silence]' "$D/settings.json")" '[0.3,0.9,0.5]' \
  "noise, noise-w and silence are saved in settings.json"
"$CTL" speaker 2 > /dev/null
for bad in "speaker x" "speaker -1" "noise 3" "noise -0.1" "noise nan" "noise-w loud" "silence 11" "speaker"; do
  # shellcheck disable=SC2086
  out=$("$CTL" $bad 2>&1 >/dev/null); code=$?
  check "$code:${out:+msg}" "2:msg" "'$bad' exits 2 with a message"
done
"$CTL" voice en_US-ryan-high > /dev/null
out=$("$CTL" speaker 4 2>&1 > /dev/null); code=$?
check "$code:${out:+msg}" "2:msg" "a speaker past the model's count exits 2 with a message"
"$CTL" voice en_US-amy-medium > /dev/null
check "$("$CTL" speaker 7)" 7 "a model that reports no speaker count accepts any number"
: > "$SANDBOX/piper-args"
queue "two"; PLAY=0.2 PIPER_ARGS="$SANDBOX/piper-args" hook
until_ 10 gone $HOOK
check "$(grep -c -- '--speaker 7 --noise-scale 0.3 --noise-w-scale 0.9 --sentence-silence 0.5' \
  "$SANDBOX/piper-args")" 1 "the next clip uses the saved options with no restart"
check "$("$CTL" status --json | jq -c '[.speaker, .noise, .noise_w, .silence]')" '[7,0.3,0.9,0.5]' \
  "status --json reports the options that are set"
for c in speaker noise noise-w silence; do "$CTL" $c reset > /dev/null; done
check "$(jq -c 'keys' "$D/settings.json")" '["voice"]' "reset clears each option and keeps the voice"
check "$("$CTL" status --json | jq -c 'has("speaker") or has("noise") or has("noise_w") or has("silence")')" \
  false "status --json leaves out the ones that are not set"
queue "three"; : > "$SANDBOX/piper-args"; PLAY=0.2 PIPER_ARGS="$SANDBOX/piper-args" hook
until_ 10 gone $HOOK
check "$(grep -cE -- '--(speaker|noise-scale|noise-w-scale|sentence-silence)' "$SANDBOX/piper-args")" 0 \
  "after reset the next clip leaves them out"
rm -f "$HOME/.local/share/piper/en_US-ryan-high.onnx.json"

# --- status
fresh; queue "one" "two"; hook
until_ 5 playing
check "$("$CTL" status --json | jq -c '[.playing.text, .queues[0].lines]')" '["one",1]' \
  "status --json shows the clip playing and what is queued behind it"
kill $HOOK 2>/dev/null; wait $HOOK 2>/dev/null

# --- sessions and the three speech settings
fresh
export SPEAK_SESSIONS_DIR="$SANDBOX/sessions" SPEAK_PROC_DIR="$SANDBOX/proc"
mkdir -p "$SPEAK_SESSIONS_DIR" "$SPEAK_PROC_DIR/10" "$SPEAK_PROC_DIR/11"
jq -n '{pid:10,sessionId:"s1",name:"Overmind",cwd:"/x",kind:"interactive",status:"busy",messagingSocketPath:"/s/10.sock"}' > "$SPEAK_SESSIONS_DIR/10.json"
jq -n '{pid:11,sessionId:"s2",name:"Widget",cwd:"/y",kind:"bg",messagingSocketPath:"/s/11.sock"}' > "$SPEAK_SESSIONS_DIR/11.json"
mkfifo "$SPEAK_SESSIONS_DIR/10.key"
queue "one"; : > "$D/s1.managed"
check "$(timeout 5 "$CTL" sessions --json | jq -c '[.[]|[.name,.speech,.managed,.queued,.background]]')" \
  '[["Overmind","on",true,1,false],["Widget","alerts",false,0,true]]' \
  "sessions lists the open sessions with their settings"
check "$(timeout 5 "$CTL" sessions | grep -c managed)" 1 "the sessions table flags a managed session"
"$CTL" managed Widget on > /dev/null
check "$([[ -e $D/s2.managed && ! -e $D/s2.replies ]] && echo set)" set "managed on writes .managed and leaves speech alone"
"$CTL" managed Widget off > /dev/null
check "$([[ ! -e $D/s2.managed ]] && echo cleared)" cleared "managed off removes .managed"
"$CTL" managed Widget maybe 2> /dev/null; check "$?" 2 "managed takes only on or off"
"$CTL" full-text Widget on > /dev/null
check "$([[ -e $D/s2.fulltext && ! -e $D/s2.replies && ! -e $D/s2.managed ]] && echo set)" set \
  "full-text on writes .fulltext and leaves speech and managed alone"
"$CTL" full-text Widget off > /dev/null
check "$([[ ! -e $D/s2.fulltext ]] && echo cleared)" cleared "full-text off removes .fulltext"
"$CTL" full-text Widget maybe 2> /dev/null; check "$?" 2 "full-text takes only on or off"
cp "$TRANSCRIPT" "$HOME/.claude/projects/p/s2.jsonl"

"$CTL" speech Widget on > /dev/null
check "$([[ -e $D/s2.replies && -e $D/s2.cursor ]] && echo set)" set "speech on creates .replies and marks the turn read"
"$CTL" speech widget off > /dev/null
check "$([[ -e $D/s2.muted && ! -e $D/s2.replies && -e $D/s2.cursor ]] && echo set)" set \
  "speech off writes .muted, removes .replies and keeps .cursor"
"$CTL" speech Widget on > /dev/null
check "$([[ ! -e $D/s2.muted ]] && echo cleared)" cleared "speech on clears .muted"
"$CTL" speech Widget cycle > /dev/null
check "$([[ ! -e $D/s2.muted && ! -e $D/s2.replies ]] && echo alerts)" alerts "cycle goes on to alerts"
"$CTL" speech Widget cycle > /dev/null
check "$([[ -e $D/s2.muted ]] && echo off)" off "cycle goes on to off"
"$CTL" speech Nobody on 2> /dev/null; check "$?" 2 "an unknown session is refused"
"$CTL" speech Widget on > /dev/null; printf 'x\n' > "$D/s2.queue"
"$CTL" speech Widget alerts > /dev/null
check "$([[ ! -e $D/s2.queue && ! -e $D/s2.replies && -e $D/s2.cursor ]] && echo set)" set \
  "speech alerts drops the queue and .replies and keeps .cursor"
rm -f "$HOME/.claude/projects/p/s2.jsonl"
"$CTL" speech Widget on 2> /dev/null; check "$?" 1 "speech on needs the session's transcript"
check "$([[ ! -e $D/s2.replies ]] && echo none)" none "speech on without a transcript sets nothing"

fresh; queue "one" "two"; hook
until_ 5 playing; "$CTL" speech Overmind off > /dev/null
until_ 10 gone $HOOK
check "$(spoken)" "" "speech off skips the clip of the session that is speaking"

# --- speech on does not read back what was already written
fresh; rm -f "$D/s1.replies"
row='{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Already written."}]}}'
printf '%s\n' "$row" >> "$TRANSCRIPT"; cp "$TRANSCRIPT" "$HOME/.claude/projects/p/s1.jsonl"
"$CTL" speech Overmind on > /dev/null; PLAY=0.2 hook; until_ 10 gone $HOOK
check "$(spoken)$(cat "$D/s1.queue" 2>/dev/null)" "" "speech on queues nothing that was already written"
rm -f "$HOME/.claude/projects/p/s1.jsonl"

# --- a queue is read to its end before another starts
fresh; : > "$D/s2.replies"; printf '%s\n' b1 b2 > "$D/s2.queue"; touch -d '1 minute ago' "$D/s2.queue"
queue a1 a2; PLAY=0.2 hook; until_ 15 gone $HOOK
check "$(spoken)" "piper: a1|piper: a2|piper: b1|piper: b2|" "one session's queue is read to its end before the next"

# --- now.json names the session whose line is playing, not the hook's own
fresh; : > "$D/s2.replies"; printf 'First' > "$D/s1.name"; printf 'Second' > "$D/s2.name"
cp "$TRANSCRIPT" "$SANDBOX/s2.jsonl"; queue "first's line"; touch -d '1 minute ago' "$D/s1.queue"
printf '%s\n' "second's line" > "$D/s2.queue"
jq -cn --arg t "$SANDBOX/s2.jsonl" '{hook_event_name:"Stop", session_id:"s2", transcript_path:$t,
  last_assistant_message:"", cwd:"/x/demo"}' | PLAY=0.5 "$HERE/speak-attention.sh" --config "$CONFIG" &
HOOK=$!
speaking() { [[ $(jq -r .text "$D/now.json" 2>/dev/null) == "$1" ]] && playing; }
until_ 5 speaking "second's line"
check "$(jq -c '[.session, .name]' "$D/now.json")" '["s2","Second"]' "a hook's own line is published as its session's"
until_ 5 speaking "first's line"
check "$(jq -c '[.session, .name]' "$D/now.json")" '["s1","First"]' \
  "a line another session's hook plays is published as its own session's"
until_ 10 gone $HOOK

# --- announcements follow the setting
announce() {
  : > "$SPOKEN"
  jq -cn --arg t "$TRANSCRIPT" '{hook_event_name:"PreToolUse", tool_name:"AskUserQuestion",
    session_id:"s1", transcript_path:$t, cwd:"/x/demo"}' | "$HERE/speak-attention.sh" --config "$CONFIG"
  spoken
}
rm -rf "$D"; mkdir -p "$D"
check "$(announce)" "piper: demo session has a question|" "an alerts-only session announces"
touch "$D/s1.muted"
check "$(announce)" "" "an off session announces nothing"
rm -f "$D/s1.muted"

# --- /implement makes a managed session and leaves speech alone
prompt() {
  jq -cn --arg t "$TRANSCRIPT" --arg p "$1" '{hook_event_name:"UserPromptSubmit", session_id:"s1",
    transcript_path:$t, prompt:$p}' | "$HERE/speak-attention.sh" --config "$CONFIG"
}
skill() {
  jq -cn --arg t "$TRANSCRIPT" --arg s "$1" '{hook_event_name:"PostToolUse", tool_name:"Skill",
    session_id:"s1", transcript_path:$t, tool_input:{skill:$s}}' |
    "$HERE/speak-attention.sh" --config "$CONFIG"
}
rm -rf "$D"; mkdir -p "$D"
prompt "/implement fix it"
check "$([[ -e $D/s1.managed && ! -e $D/s1.replies ]] && echo managed)" managed \
  "/implement makes a managed session and leaves speech at Alerts only"
rm -rf "$D"; mkdir -p "$D"; : > "$D/s1.replies"
prompt "/general:implement 7"
check "$([[ -e $D/s1.managed && -e $D/s1.replies ]] && echo both)" both \
  "/general:implement makes a managed session and leaves speech On"
rm -rf "$D"; mkdir -p "$D"; touch "$D/s1.muted"
skill general:implement
check "$([[ -e $D/s1.managed && -e $D/s1.muted ]] && echo both)" both \
  "a Skill call to implement makes a managed session and leaves Off alone"
rm -rf "$D"; mkdir -p "$D"
skill implement-something; prompt "/implementation 3"; prompt "please /implement 3"
check "$([[ ! -e $D/s1.managed ]] && echo none)" none "only the implement skill itself makes a managed session"

if ((fails)); then echo "$fails failed"; exit 1; fi
echo "all passed"
