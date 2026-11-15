#!/usr/bin/env bash
# usage: speak-attention.sh --config <extension.json> < <hook payload>
# Speaks the session's name and what it needs. Reads the hook payload on
# stdin and handles three events:
#   Stop                           the turn ended with no background work due to
#                                  wake it, and stop_attention.py says what it
#                                  needs from the user, or an earlier stop held
#                                  back by background work owes what it held
#   PreToolUse  AskUserQuestion    the session is about to ask a question
#   PostToolUse Bash               a pull request got the review label
# The extension file names the review label (reviewLabel), the words spoken once it
# lands (reviewAnnouncement), and the words the voice would misread (spokenTerms). A
# missing --config exits 64.
# With speech mode on, the reply is read aloud instead, and the other announcements
# stay quiet. It starts off. Each text block is read as it lands: a PreToolUse for any
# tool reads what was written ahead of that call, and the Stop reads the rest. An
# AskUserQuestion call's question and options are read with the text ahead of it, and
# a wrap-up question with its buttons after the closing reply.
# speechctl and the speech widget turn it on and off; no command a session runs does.
# Every implementation is a managed session: its .managed marker puts it in the session
# management widget, which reads it through speechctl sessions. The implement skill sets
# the marker, typed (UserPromptSubmit) or called through the Skill tool (PostToolUse
# Skill), and leaves speech mode as it was.
# Outside speech mode, a session a phone follows through the voice bridge still sends its
# text to the voice feed ahead of each tool call, and reads none of it aloud.
# A managed session (its .managed marker) also writes every block to <id>.feed, whatever
# its speech setting, so the session management widget can list its replies without
# anything being read aloud.
# Each session's speech is On (its .replies marker), Alerts only (the default: neither
# marker) or Off (its .muted marker, which silences the announcements too). speechctl sets
# it, and reads and drives playback through the files this script keeps in the speak-attention
# folder: now.json while a clip plays, paused while speech is held, skip and requeue for a
# clip speechctl is ending, and settings.json for the voice, volume and pace. A session may
# also have a voice of its own in <id>.voice, which the speech widget writes.
# Anything else exits quietly, as does a machine without jq or python3, or with
# neither Piper nor spd-say to speak.
# The label case asks ready_line.py, which holds the same rules for the ready signal, so
# the two never disagree on what a label add is.

# When the hook started, in epoch ms: an event the app delivers from then on
# starts a turn after this stop.
stop_at=$(($(date +%s%N) / 1000000))

if [[ ${1:-} == --config && -f ${2:-} ]]; then
  config=$2
  shift 2
else
  echo "speak-attention.sh: --config <extension.json> is required" >&2
  exit 64
fi

for bin in jq python3; do
  command -v "$bin" >/dev/null || exit 0
done

input=$(cat)
# Every tool call runs this hook, and outside speech mode only a question says anything,
# and a followed or managed session's text goes to a feed, so a call leaves before the
# payload is parsed when no session has speech mode on or is managed, and no phone follows one.
# The bridge touches voice-bridge/follow/<socket name> as the phone polls; a marker idle
# longer than FOLLOW_IDLE_SECONDS in voice_bridge_reply.py no longer counts.
follow_dir=${XDG_RUNTIME_DIR:-/tmp}/voice-bridge/follow
# usage: followed; succeeds while a phone follows this session.
followed() {
  local key=${CLAUDE_CODE_MESSAGING_SOCKET:-}
  [[ $key == *.sock ]] || return 1
  key=${key##*/}
  [[ -e "$follow_dir/${key%.sock}" && -n $(find "$follow_dir/${key%.sock}" -mmin -30 -print -quit \
    2>/dev/null) ]]
}
if [[ $input == *'"hook_event_name":"PreToolUse"'* &&
  $input != *'"tool_name":"AskUserQuestion"'* ]] &&
  ! compgen -G "${XDG_RUNTIME_DIR:-/tmp}/speak-attention/*.replies" >/dev/null &&
  ! compgen -G "${XDG_RUNTIME_DIR:-/tmp}/speak-attention/*.managed" >/dev/null &&
  ! followed; then
  exit 0
fi
field() { jq -r "$1 // empty" <<<"$input"; }
here=$(dirname "$(readlink -f "$0")")
ready_line() {
  python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import hook_config
hook_config.use(sys.argv.pop(2)); import ready_line as e
'"$1" "$here" "$config" "${@:2}"
}

event=$(field .hook_event_name)
tool=$(field .tool_name)
transcript=$(field .transcript_path)
[[ -f "$transcript" ]] || transcript=/dev/null

# A stop held quiet by background work owes the user the announcement it
# skipped. The marker carries that debt to the next stop that would otherwise
# stay quiet, and any announcement pays it.
session=$(field .session_id)
owed=${XDG_RUNTIME_DIR:-/tmp}/speak-attention/${session:-none}.owed
# The marker that holds speech mode on for this session.
replies=${owed%.owed}.replies
# The marker that makes this a managed session, which the session management widget lists.
managed=${owed%.owed}.managed

# usage: is_implement <skill or command>; succeeds for the implement skill, by its own name
# or with its plugin's, as a skill name or a slash command.
is_implement() {
  [[ ${1#/} =~ ^([A-Za-z0-9_-]+:)?implement$ ]]
}

# usage: manage; marks this session a managed session.
manage() {
  [[ -n "$session" ]] || return 0
  mkdir -p "${managed%/*}" && : > "$managed"
}

# usage: command_of <prompt>; prints the slash command the prompt opens with, from
# its first word or, for a command the app expanded, its command-name tag.
command_of() {
  local flat tags
  flat=$(tr '\n' ' ' <<<"$1")
  tags='^[[:space:]]*(<command-message>[^<]*</command-message>[[:space:]]*)?'
  tags+='<command-name>([^<]*)</command-name>'
  if [[ $flat =~ $tags ]]; then
    printf '%s' "${BASH_REMATCH[2]}"
  elif [[ $flat =~ ^[[:space:]]*(/[^[:space:]]+) ]]; then
    printf '%s' "${BASH_REMATCH[1]}"
  fi
}

# usage: speakable; reads Markdown on stdin and prints it as plain sentences. Code
# blocks and file links say nothing worth hearing, so they go, and a bare URL is
# read as "the following link" so its sentence still ends. A link whose
# text is words, such as a session title, keeps its text, and an owner/repo#N
# link is read as its number. A link to a workflow run says only the words of its
# text, a bare run URL says nothing, and run and job ids are dropped. A duration
# such as 7.0s, 30 min or 1h30m is read with its units spelled out, and the words in
# the extension file's spokenTerms are read as it says them aloud.
speakable() {
  python3 -c '
import json, re, sys
EXT = "ts|js|mjs|md|sh|py|json|ya?ml|tsv|csv|sql|txt|html|css|xlsx"
RUN_URL = r"https?://\S*/actions/runs/\S*"
def link(m):
    text = m.group(1).strip("`")
    if re.fullmatch(RUN_URL, m.group(2)):
        return " " if re.fullmatch(r"[\d\s#-]*", text) else text
    ref = re.fullmatch(r"[\w.-]+/[\w.-]+#(\d+)", text)
    if ref:
        return ref.group(1)
    if "/" in text or re.fullmatch(r"(?![A-Z][a-z]+\.)\S+\.(" + EXT + r")(:\d+)?", text):
        return " "
    return m.group(1)
UNITS = {"h": "hour", "hr": "hour", "hrs": "hour", "m": "minute", "min": "minute",
         "mins": "minute", "s": "second", "sec": "second", "secs": "second"}
# a one-letter unit has to touch its number, so "option 1 m" is left alone, and
# an m ahead of a plural noun, as in "3m rows", is a million rather than minutes.
# Short words and ones ending in -is, -as, -us or -ss, such as "is" or "plus",
# are not plural nouns.
PLURAL = r" [a-z]{2,}[^\Waiusx]s\b"
PART = r"(\d+(?:\.\d+)?)(?:(h|m(?!" + PLURAL + r")|s)|\s?(hrs|hr|mins|min|secs|sec))"
def duration(m):
    text = m.group(0)
    # "the 1990s" is a decade, while "the 30s cap" is still seconds
    if m.string.endswith("the ", 0, m.start()) and re.fullmatch(r"\d{3}0s", text):
        return text
    # "1000s of rows" is a count, while "30s of idle time" is still seconds
    if m.string.startswith(" of ", m.end()) and re.fullmatch(r"\d+00s", text):
        return text
    words = []
    for n, letter, word in re.findall(PART, text):
        words.append(n + " " + UNITS[letter or word] + ("" if n == "1" else "s"))
    return " ".join(words)
DURATION = r"\b(?:" + PART + r")+\b"
# words the voice would otherwise misread, and how they are said
with open(sys.argv[1], encoding="utf-8") as f:
    SAID = json.load(f).get("spokenTerms") or {}
t = sys.stdin.read()
t = re.sub(r"```.*?(```|$)", " ", t, flags=re.S)
t = re.sub(r"\[([^\]]*)\]\(([^)]*)\)", link, t)
t = re.sub(r"<?" + RUN_URL + r"[^\s.,;:!?)]>?", " ", t)
t = re.sub(r"<?https?://\S*[^\s.,;:!?)]>?", "the following link", t)
# run and job ids carry nothing worth hearing: "run 39694323023" is read as "run".
# Three digits or more, so a count such as "run 2 minutes apart" stays.
t = re.sub(r"\b([Rr]uns?|[Jj]obs?) #?\d{3,}(?:-\d+)?\b", r"\1", t)
t = re.sub(r"\b\d{8,}(?:-\d+)?\b", " ", t)
t = re.sub(DURATION, duration, t)
if SAID:
    t = re.sub(r"\b(" + "|".join(map(re.escape, SAID)) + r")\b", lambda m: SAID[m.group(1)], t)
t = re.sub(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", " ", t, flags=re.M)
t = re.sub(r"[`*#>|\[\]]", " ", t)
print(re.sub(r" ([.,;:!?])", r"\1", " ".join(t.split())))' "$config"
}

# usage: session_name; prints the name the voice gives the session: its latest title,
# the one set by hand first, else the folder, then "session" said once.
session_name() {
  local title
  title=$(tac "$transcript" | grep -m1 '"type":"custom-title"' |
    jq -r '.customTitle // empty' 2>/dev/null)
  [[ -z "$title" ]] && title=$(tac "$transcript" | grep -m1 '"type":"ai-title"' |
    jq -r '.aiTitle // empty' 2>/dev/null)
  [[ -z "$title" ]] && title=$(basename "$(field .cwd)")
  shopt -s nocasematch
  [[ $title =~ ^((.*[^[:space:]_-])[[:space:]_-]+)?session[[:space:]]*$ ]] &&
    title=${BASH_REMATCH[2]}
  shopt -u nocasematch
  printf '%s' "${title:+$title }session" | speakable
}

dir=${XDG_RUNTIME_DIR:-/tmp}/speak-attention
wav=$dir/$$.wav
now=$dir/now.json
settings=$dir/settings.json
# Past this moment, in epoch seconds, a held clip or line is given up on, so a forgotten
# pause never keeps a hook alive past its timeout. The queue keeps what was not read.
deadline=$((stop_at / 1000 + 1100))
player=
clip=
# The queue line being read and the queue it came from, so a hook ended mid-clip puts the
# line back rather than losing it.
held_line=
held_q=
# usage: cleanup; ends the clip this hook started and removes what it published, so a hook
# that is killed mid-clip leaves no player behind to talk over the next one.
cleanup() {
  if [[ -n $player ]]; then
    kill -CONT "$player" 2>/dev/null
    kill -TERM "$player" 2>/dev/null
    [[ -n $held_line && -n $held_q ]] && put_back "$held_line" "$held_q"
  fi
  rm -f "$wav" "$now.$$.tmp" "$dir/$session.name.tmp.$$"
  [[ -f $now && $(jq -r '.hook_pid // empty' "$now" 2>/dev/null) == "$$" ]] && rm -f "$now"
  return 0
}
trap cleanup EXIT
trap 'exit 143' TERM INT HUP

# usage: put_back <line> <queue>; puts a line back at the head of its queue.
put_back() {
  { flock -w 30 8 && { printf '%s\n' "$1"; cat "$2" 2>/dev/null; } > "$2.tmp.$$" &&
    mv -f "$2.tmp.$$" "$2"; } 8>"${2%.queue}.cursor.lock"
}

# usage: setting <key>; prints the value speechctl saved, or nothing.
setting() { jq -r --arg k "$1" '.[$k] // empty' "$settings" 2>/dev/null; }

# usage: alive <pid>; a process that is stopped is alive, one that has exited is not.
alive() {
  local state
  state=$(sed 's/.*) //; s/ .*//' "/proc/$1/stat" 2>/dev/null)
  [[ -n $state && $state != Z ]]
}

# usage: publish_now <text> <engine> <player pid or empty> <speaker> [markdown]; writes
# now.json atomically. The speaker is the session whose line is playing, which is not this
# hook's own when it reads another session's queue. The markdown is the line as the
# assistant wrote it, for a widget that draws it formatted; a line the hook composes itself
# has none, and publishes an empty string.
publish_now() {
  local speaker=${4:-$session}
  mkdir -p "$dir"
  jq -n --arg session "$speaker" --arg name "$(cat "$dir/$speaker.name" 2>/dev/null)" \
    --arg text "$1" --arg engine "$2" --arg pid "$3" --arg clip "$clip" --argjson hook "$$" \
    --arg markdown "${5:-}" \
    '{session:$session, name:$name, text:$text, markdown:$markdown, started:(now|floor),
      clip:$clip, hook_pid:$hook,
      player_pid:(if $pid == "" then null else ($pid|tonumber) end), engine:$engine}' \
    > "$now.$$.tmp" 2>/dev/null && mv -f "$now.$$.tmp" "$now"
}

# usage: wait_unpaused; waits while speech is paused. Returns 1 once the deadline passes.
wait_unpaused() {
  while [[ -e $dir/paused ]]; do
    (($(date +%s) >= deadline)) && return 1
    sleep 0.5
  done
}

# usage: await_player <pid> <text> <engine> <speaker> [markdown]; publishes the clip and waits
# for the player to end. speechctl pauses a Piper clip by stopping the player, which this
# keeps waiting on until the deadline; then the clip is ended and 75 asks the caller to put
# its line back.
# A Speech Dispatcher clip is paused by speechctl cancelling it with a requeue marker
# naming this clip, which also gets 75.
await_player() {
  local rc=0
  player=$1
  publish_now "$2" "$3" "$player" "$4" "${5:-}"
  while alive "$player"; do
    # a skip or pause that came before the player's pid was published is met here
    if [[ -e $dir/skip ]]; then
      rm -f "$dir/skip"
      kill -TERM "$player" 2>/dev/null
      kill -CONT "$player" 2>/dev/null
    elif [[ -e $dir/paused ]]; then
      if [[ $3 == piper && $(sed 's/.*) //; s/ .*//' "/proc/$player/stat" 2>/dev/null) == S ]]; then
        kill -STOP "$player" 2>/dev/null
      elif [[ $3 == spd-say && ! -e $dir/requeue ]]; then
        printf '%s' "$clip" > "$dir/requeue"
        spd-say -C >/dev/null 2>&1 8>&- 9>&-
      fi
    fi
    if [[ -e $dir/paused && $(date +%s) -ge $deadline ]]; then
      kill -CONT "$player" 2>/dev/null
      kill -TERM "$player" 2>/dev/null
      rc=75
      break
    fi
    sleep 0.2
  done
  wait "$player" 2>/dev/null
  player=
  if [[ $(cat "$dir/requeue" 2>/dev/null) == "$clip" ]]; then
    rm -f "$dir/requeue"
    rc=75
  fi
  [[ $(jq -r '.hook_pid // empty' "$now" 2>/dev/null) == "$$" ]] && rm -f "$now"
  return $rc
}

# usage: say <text> [speaker] [markdown]; speaks it for the speaker's session, this hook's
# own when none is named, and returns once it has played, or 75 when the clip was paused away
# and the text still has to be read. The markdown is what now.json carries beside the text.
# Piper speaks when it and its voice model are installed; SPEAK_PIPER_MODEL names the
# model, and SPEAK_PIPER_LENGTH its pace, faster below 1. settings.json, which speechctl
# writes, overrides both, and sets the volume. Its speaker, noise, noise_w and silence go to
# Piper only when set, so an unset one keeps the model's own default. Only the pipx install counts,
# since the apt package named piper is an unrelated GTK app. pw-play plays with the
# Speech role, since a role's saved volume applies to every stream that carries it.
# Piper renders at 0.8 volume, below where its peaks clip, and the stream plays at 1.2
# to make up the level. Once Piper has rendered, pw-play's exit status is not checked,
# so a clip that played and then failed is never spoken a second time, and neither is one
# that speechctl skipped. A speaker's <id>.voice file, written by the speech widget, overrides
# the voice for that session's lines alone.
say() {
  local speaker=${2:-$session} piper=$HOME/.local/bin/piper args voice volume pace opts=() v
  local model=${SPEAK_PIPER_MODEL:-$HOME/.local/share/piper/en_US-amy-medium.onnx}
  # The speaker's own voice, a name in <speaker>.voice, wins over settings.json's; a name
  # with no model installed falls through to it.
  for voice in "$([[ -n $speaker ]] && cat "$dir/$speaker.voice" 2>/dev/null)" "$(setting voice)"; do
    [[ -n $voice && $voice != */* && -f "$HOME/.local/share/piper/$voice.onnx" ]] &&
      { model=$HOME/.local/share/piper/$voice.onnx; break; }
  done
  pace=$(setting pace)
  pace=${pace:-${SPEAK_PIPER_LENGTH:-0.85}}
  volume=$(setting volume)
  for v in "speaker --speaker" "noise --noise-scale" "noise_w --noise-w-scale" \
    "silence --sentence-silence"; do
    [[ -n $(setting "${v%% *}") ]] && opts+=("${v#* }" "$(setting "${v%% *}")")
  done
  clip=$(date +%s%N)
  rm -f "$dir/skip" "$dir/requeue"
  if [[ -x "$piper" && -f "$model" ]] && command -v pw-play >/dev/null; then
    # now.json is up while Piper renders, so a skip in that time leaves a token for below
    publish_now "$1" piper "" "$speaker" "${3:-}"
    if "$piper" -m "$model" --length-scale "$pace" "${opts[@]}" --volume 0.8 -f "$wav" \
      <<<"$1" >/dev/null 2>&1 8>&- 9>&-; then
      wait_unpaused || { rm -f "$now"; return 75; }
      if [[ -e $dir/skip ]]; then
        rm -f "$dir/skip" "$now"
        return 0
      fi
      # a volume set while Piper rendered is read here, since the stream does not exist for
      # speechctl to change until pw-play starts
      volume=$(setting volume)
      pw-play --media-role=Speech --volume "${volume:-1.2}" "$wav" >/dev/null 2>&1 8>&- 9>&- &
      await_player $! "$1" piper "$speaker" "${3:-}"
      return $?
    fi
    rm -f "$now"
  fi
  # Speech Dispatcher speaks when Piper cannot: RHVoice when its module is installed,
  # else the default. SPEAK_VOICE picks one of its voices (spd-say -o rhvoice -L lists
  # them).
  command -v spd-say >/dev/null || return 0
  args=(--wait)
  if spd-say -O 2>/dev/null 8>&- 9>&- | grep -qx rhvoice; then
    args+=(-o rhvoice -l en -y "${SPEAK_VOICE:-Slt}")
  else
    args+=(-r -10)
  fi
  [[ -n $volume ]] && args+=(-i "$(awk -v v="$volume" 'BEGIN { x = (v - 1) * 100;
    print (x < -100 ? -100 : x > 100 ? 100 : int(x)) }')")
  wait_unpaused || return 75
  # The text goes as one argument, which the kernel caps at 128 KiB, so a longer reply
  # is cut short rather than not spoken at all. The cap counts characters, up to four
  # bytes each.
  spd-say "${args[@]}" -- "${1:0:30000}" >/dev/null 2>&1 8>&- 9>&- &
  await_player $! "$1" spd-say "$speaker" "${3:-}"
}

# One clip plays at a time: hooks that fire together wait on this lock. An announcement
# that waits two minutes stays quiet rather than talk over the clip still playing; a
# reply waits fifteen, since the reply ahead of it can run for several.
# usage: hold_voice <seconds>; returns 1 when the wait runs out.
hold_voice() {
  if { mkdir -p "$dir" && exec 9>"$dir/speak.lock"; } 2>/dev/null; then
    flock -w "$1" 9 || return 1
  fi
}

# In speech mode the reply text goes on a queue, one line per block, and whichever hook
# holds the voice reads the queue in order, so blocks that land while one is playing are
# read after it and never out of turn. The cursor lock keeps two hooks that fire
# together from queueing the same block twice. The same blocks, as written, go to the
# voice bridge's feed for this session as one entry per hook, and the bridge makes them
# speakable for a phone following it. A followed session outside speech mode takes the same
# path with nothing queued or spoken. A block the speaker finds nothing to say in still
# goes, and the bridge decides what of it the phone hears.
# A queue line is the spoken text, then a tab and the block as written, as a JSON string
# (newlines escaped, so it stays one line). The source travels with the line, so a line put
# back or read by another session's hook still publishes the Markdown it was made from. A
# line with no tab, such as one queued before this field existed, has none.
queue=${replies%.replies}.queue
cursor=${replies%.replies}.cursor
# A managed session's blocks also go to its feed, one JSON object per line: session, name,
# text (the spoken form, with no name ahead of it), markdown (as markdown_source makes it)
# and at (epoch seconds). It is written whatever the speech setting, plays nothing, and keeps
# the last FEED_KEEP blocks, far more than a widget that lists each session's latest lines
# draws, so a long-running session's file stays small.
feed=${replies%.replies}.feed
feed_cursor=${replies%.replies}.feed-cursor
FEED_KEEP=200

# The most characters of a block's Markdown the queue keeps for now.json; a widget draws a
# few lines, and a longer source is cut at a line boundary and ends with an ellipsis.
MARKDOWN_CAP=2000

# usage: markdown_source; reads a block on stdin and prints it as a JSON string: leading blank
# lines and trailing space trimmed, and cut to MARKDOWN_CAP characters at the last line
# boundary within them (mid-line when they hold no newline), ending with an ellipsis. Only
# text past the cap that is more than space counts as past it. The cut comes before the
# trailing trim, so the regex never scans a long block. --rawfile reads the block whole,
# since -R splits a multibyte character that straddles a read.
markdown_source() {
  jq -nc --rawfile s /dev/stdin --argjson cap "$MARKDOWN_CAP" '
    $s | sub("\\A\\s*\\n"; "") | . as $all
    | if length > $cap and ($all[$cap:] | test("\\S")) then
        (.[0:$cap] | if $all[$cap:$cap + 1] == "\n" then . else sub("\\n[^\\n]*\\z"; "") end
          | sub("\\s+\\z"; "")) + "…"
      else sub("\\s+\\z"; "") end'
}

# usage: await_text_row; the app writes transcript rows in batches, so a tool call can
# start before the text ahead of it is on disk. The call's own row lands with or after
# that text, so the hook, which runs async, waits up to fifteen seconds for it.
await_text_row() {
  local id
  id=$(field .tool_use_id)
  if [[ $event == PreToolUse && -n "$id" && -f "$transcript" ]]; then
    for _ in {1..30}; do
      grep -qF "\"$id\"" "$transcript" && break
      sleep 0.5
    done
  fi
}

# usage: feed_block <block>; appends the block to a managed session's feed, under the
# cursor lock the caller holds, and drops what is past the last FEED_KEEP blocks.
feed_block() {
  local md
  md=$(markdown_source <<<"$1")
  [[ $md != '""' ]] || return 0
  jq -nc --arg session "$session" --arg name "$(cat "$dir/$session.name" 2>/dev/null)" \
    --arg text "$(speakable <<<"$1")" --argjson markdown "$md" \
    '{session:$session, name:$name, text:$text, markdown:$markdown, at:(now|floor)}' \
    >> "$feed" 2>/dev/null || return 0
  (($(wc -l < "$feed") > FEED_KEEP)) &&
    tail -n "$FEED_KEEP" "$feed" > "$feed.tmp.$$" && mv -f "$feed.tmp.$$" "$feed"
  return 0
}

# Long text is read in short: short_speech.py cuts a block's spoken text to one line for a
# ready line, and to its opening sentence for any other block past its limit. The queue's
# source and the voice bridge get the block as written, whole. The
# <session>.fulltext marker (speechctl full-text) or "fullSpeech": true in the extension
# file reads every block in full instead.
fulltext=${replies%.replies}.fulltext

# usage: spoken <block>; prints the text read aloud for a block written in Markdown.
spoken() {
  local said
  said=$(speakable <<<"$1")
  if [[ -z $said || -e $fulltext ]] || jq -e '.fullSpeech == true' "$config" >/dev/null 2>&1; then
    printf '%s' "$said"
    return 0
  fi
  python3 "$here/short_speech.py" --config "$config" ready <<<"$1" 2>/dev/null && return 0
  python3 "$here/short_speech.py" --config "$config" brief <<<"$said" 2>/dev/null ||
    printf '%s' "$said"
}

# usage: read_aloud; queues the turn's unread text and reads the queue. Outside speech mode
# nothing is queued or spoken: a managed session's feed gets the text, and so does the voice
# feed ahead of a tool call while a phone follows the session.
read_aloud() {
  local fields name='' chunk text line
  local args=("$here/speak_pending.py" "$transcript" "$cursor")
  [[ $event == Stop ]] && args+=(stop "$(field .last_assistant_message)")
  await_text_row
  mkdir -p "$dir"
  {
    flock -w 30 8 || return 0
    mapfile -d '' fields < <(python3 "${args[@]}" 2>/dev/null)
    if [[ ${fields[0]:-0} == 1 ]]; then
      name="$(session_name) says: "
      printf '%s' "${name% says: }" > "$dir/$session.name.tmp.$$" &&
        mv -f "$dir/$session.name.tmp.$$" "$dir/$session.name"
    fi
    # The feed reads the turn through a cursor of its own, so speech turning on, which marks
    # the speech cursor read, never drops a block the feed has not had. Stop has already
    # waited on the reply row above, so this read does not wait again.
    if [[ -e "$managed" ]]; then
      [[ -s "$dir/$session.name" ]] || { session_name > "$dir/$session.name.tmp.$$" &&
        mv -f "$dir/$session.name.tmp.$$" "$dir/$session.name"; }
      local fed
      mapfile -d '' fed < <(STOP_WAIT=0 python3 "$here/speak_pending.py" "$transcript" \
        "$feed_cursor" "${args[@]:3}" 2>/dev/null)
      for chunk in "${fed[@]:1}"; do feed_block "$chunk"; done
    fi
    local pushed=$name
    for chunk in "${fields[@]:1}"; do
      pushed+=$chunk$'\n\n'
      [[ -e "$replies" ]] || continue
      text=$(spoken "$chunk")
      [[ -n "$text" ]] || continue
      printf '%s\t%s\n' "$name$text" "$(markdown_source <<<"$chunk")" >> "$queue"
      name=
    done
    # outside speech mode the bridge's own Stop hook feeds the final reply, and a session
    # no phone follows feeds the voice bridge nothing
    [[ ${#fields[@]} -gt 1 ]] &&
      { [[ -e "$replies" ]] || { [[ $event != Stop ]] && followed; }; } &&
      python3 "$here/voice_bridge_reply.py" --config "$config" push <<<"$pushed" 2>/dev/null
  } 8>"$cursor.lock"
  [[ -e "$replies" ]] || return 0
  rm -f "$owed"
  [[ -s "$queue" ]] || return 0
  hold_voice 900 || return 0
  # This hook reads its own session's queue first, then any other session's with lines
  # left, oldest first, so a "next" reply plays even when its own hook is gone. A paused
  # voice holds before a line is taken, so a held line stays queued.
  local q rc cur= markdown
  while wait_unpaused; do
    # leave a margin before the hook's own timeout, so no clip is cut off mid-line
    (($(date +%s) >= deadline - 120)) && break
    line=
    # the queue being read is read to its end before another is started
    for q in "$cur" "$queue" $(ls -tr "$dir"/*.queue 2>/dev/null); do
      [[ -n $q ]] || continue
      line=$( {
        flock -w 30 8 && [[ -s "$q" ]] && head -n 1 "$q" && sed -i 1d "$q"
      } 8>"${q%.queue}.cursor.lock") && [[ -n $line ]] && break
      line=
    done
    [[ -n $line ]] || break
    cur=$q
    held_line=$line held_q=$q
    markdown=
    [[ $line == *$'\t'* ]] && markdown=$(jq -r . <<<"${line#*$'\t'}" 2>/dev/null)
    say "${line%%$'\t'*}" "$(basename "$q" .queue)" "$markdown"
    rc=$?
    held_line= held_q=
    # a clip paused away puts its line back at the head of the queue it came from
    [[ $rc == 75 ]] && put_back "$line" "$q"
  done
}

# In speech mode the replies are the only voice, and the announcements stay quiet,
# since the replies say what they would. Text with nothing left to say once its code
# and URLs are gone is quiet too. The events that set the mode still run.
if [[ -n "$session" && -e "$replies" ]]; then
  [[ $event == Stop || $event == PreToolUse ]] && { read_aloud; exit 0; }
  [[ $event:$tool =~ ^(UserPromptSubmit:|PostToolUse:Skill)$ ]] || exit 0
fi

# Outside speech mode a followed session still sends its mid-turn text to the voice feed,
# ahead of each tool call. The bridge's Stop hook feeds the final reply, so the Stop only
# marks the turn's text as sent. A managed session writes every block to its own feed,
# the final reply included. A question is announced aloud after its text goes, and a Stop
# goes on to its announcement.
if [[ -n "$session" && ($event == PreToolUse || $event == Stop) ]] &&
  { [[ -e "$managed" ]] || followed; }; then
  read_aloud
  [[ $event == PreToolUse && $tool != AskUserQuestion ]] && exit 0
fi

case "$event:$tool" in
  UserPromptSubmit:)
    is_implement "$(command_of "$(field .prompt)")" && manage
    exit 0
    ;;
  PostToolUse:Skill)
    is_implement "$(field .tool_input.skill)" && manage
    exit 0
    ;;
  Stop:)
    # stop_attention.py says what this turn needs from the user. Exit 3 is
    # quiet: the label already spoke, or an automated event started the turn
    # and nothing waits on the user. A crash still speaks.
    what=$(python3 "$here/stop_attention.py" --config "$config" <<<"$input" 2>/dev/null)
    case $? in
      0) ;;
      3) what= ;;
      *) what="finished" ;;
    esac
    # Quiet while background work is due to wake the session, since the turn
    # goes on when it does, and an announcement it holds back is owed. The hook
    # command execs this script, so its parent is the session process, whose
    # start time marks work a restart ended.
    if STOP_AT=$stop_at python3 "$here/background_pending.py" "$transcript" "$PPID" \
      >/dev/null 2>&1; then
      [[ -n "$what" && -n "$session" ]] && mkdir -p "${owed%/*}" &&
        printf '%s' "$what" > "$owed"
      exit 0
    fi
    if [[ -z "$what" ]]; then
      [[ -n "$session" && -s "$owed" ]] || exit 0
      what=$(cat "$owed")
    fi
    ;;
  PreToolUse:AskUserQuestion)
    what="has a question"
    ;;
  PostToolUse:Bash)
    cmd=$(field .tool_input.command)
    { IFS= read -r label; IFS= read -r announced; } < <(
      jq -r '.reviewLabel // "", .reviewAnnouncement // ""' "$config" 2>/dev/null)
    [[ -n $label && -n $announced ]] || exit 0
    # A quick look for the label's words, however the command spaces them, before the
    # full check.
    grep -qiE "${label// /'(\s|%20|\+)+'}" <<<"$cmd" || exit 0
    # The command adds the label, and its output shows the add went through.
    out=$(field .tool_response.stdout)
    pr=$(ready_line 'n = e.labeled_numbers(sys.argv[2])
added = e.LABEL_ADDED.search(sys.stdin.read())
sys.exit(1) if n is None or not added else print(" ".join(n))' "$cmd" <<<"$out" 2>/dev/null) ||
      exit 0
    what="has pull request ${pr:+$pr }$announced"
    ;;
  *)
    exit 0
    ;;
esac

[[ -n "$session" ]] && rm -f "$owed"

# A session set to Off says nothing at all, announcements included.
[[ -n "$session" && -e "${replies%.replies}.muted" ]] && exit 0

# Outside speech mode the voice only draws the user to the session, which carries the
# detail in text. An announcement is not queued, so one that meets a pause waits only as
# long as it would for the voice, then goes quiet.
hold_voice 120 || exit 0
if [[ -n "$session" ]]; then
  mkdir -p "$dir"
  session_name > "$dir/$session.name.tmp.$$" && mv -f "$dir/$session.name.tmp.$$" "$dir/$session.name"
fi
for _ in {1..240}; do [[ -e "$dir/paused" ]] || break; sleep 0.5; done
[[ -e "$dir/paused" ]] && exit 0
say "$(session_name) $what" || true
