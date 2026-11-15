#!/usr/bin/env python3
"""Hands a stopped session's reply to the voice bridge when the bridge is waiting on it.

usage: voice_bridge_reply.py < <Stop hook payload>
       voice_bridge_reply.py push < <spoken text>
       voice_bridge_reply.py opened < <PostToolUse Bash hook payload>
       voice_bridge_reply.py milestone < <Stop hook payload>
       voice_bridge_reply.py attention < <PermissionRequest, PreToolUse, PostToolUse or
                                          UserPromptSubmit hook payload>
       voice_bridge_reply.py answer < <PermissionRequest hook payload>
       voice_bridge_reply.py ready < <Stop hook payload>

Each form takes `--config <extension.json>` ahead of its name, for the ready line and the
review label it reads through ready_line.py, and a missing one exits 64.

Baton posts a spoken request into a session's inbox socket and leaves a marker named
for that socket in $XDG_RUNTIME_DIR/voice-bridge/pending. When this session stops and its own
socket (CLAUDE_CODE_MESSAGING_SOCKET) has a marker, the turn's last_assistant_message is written
to voice-bridge/replies/<socket name>.json for the bridge's read_reply tool. While the phone
follows the session (a recent voice-bridge/follow/<socket name> marker), every reply is also
added to voice-bridge/feed/<socket name>.json for next_update.

In speech mode (a speak-attention/<session id>.replies marker) speak-attention.sh pushes
the blocks it reads aloud to the feed with the push form, as written and follow or not, so
the phone hears every reply, question and mid-turn note the speaker does. The Stop payload
then leaves the feed to those pushes and only answers a pending request. Outside speech mode,
speak-attention.sh pushes a followed session's mid-turn text the same way, ahead of each tool
call. The Stop payload still adds the final reply.

The attention form keeps voice-bridge/attention/<socket name>.json, which says what the
session waits on the user for, for the bridge's list_sessions and needs_attention tools. A
PermissionRequest writes it as a permission prompt for the named tool, and while a phone
follows the session it also adds a note to the feed, since a prompt never reaches the
transcript text that speak-attention.sh pushes. An AskUserQuestion call writes it as a
question. A call's PostToolUse clears that call's mark and the last stop's question, since
both were answered by then, and leaves a parallel call's prompt marked. A prompt the user
denies has no PostToolUse; the next PermissionRequest or PostToolUse finds its refusal in the
transcript and drops it. A UserPromptSubmit clears every mark. The Stop payload writes it as
a question when the turn leaves the user one, by stop_attention.py's test, and clears it
otherwise. The attention form prints nothing, so it never answers a prompt.

The answer form is the only one that answers a prompt, and it answers only the one
PermissionRequest it runs for, with what the user said in a voice chat. It writes the prompt
to voice-bridge/prompts/<socket name>/<id>.json under an id made for that request, and waits
up to ANSWER_WAIT_SECONDS for the bridge's answer_prompt tool to write
voice-bridge/answers/<socket name>/<id>.json, which the bridge does after reading the
prompt back and hearing a yes. When the user's spoken command ended with "please and thank
you", a deny, or a question's answers that name its options, are written at once. An allow on
a permission prompt always waits for the yes. An answer under the request's id becomes the hook's decision:
allow, deny, or for an AskUserQuestion call allow with the answers, and the hook leaves
answers/<socket name>/<id>.took beside it before removing it, so the bridge knows the
request was still waiting when the answer landed. It never
sends permission updates, so nothing is allowed past this one call. The app's dialog stays
open meanwhile, and whichever answers first decides; once the app has, the wait ends. A
tool that changes the session's mode, a path in a .claude folder, a shell command that names
one or a settings.json file, and input too long to read back in full are left to the app.

A follow in milestones mode (a voice-bridge/follow/<socket name>.mode file) hears only the
feed entries marked as milestones. The prompt note carries milestone: true in either mode.
The rest are kind milestone entries, which only milestones mode hears and which are written
only while a follow is in that mode: an AskUserQuestion call's questions; the opened form's
entry after a `gh pr create` that printed a new pull request's URL; and the milestone form's
copy of a Stop's reply, run as an async Stop hook since its checks read the whole transcript.
That copy is added when the reply carries the ready line, leaves the user
a question, or ends the turn with no background work due to wake the session, by
background_pending.py's test.

A Stop whose reply carries the ready line, the extension file's readyLine, also
starts the ready form in a process of its own, follow or not. It runs the milestone form's
ready test, and for each pull request the line names writes
voice-bridge/ready/<socket name>-<N>.json, which the bridge announces once per pull request
and head.

Anything else, a session with no socket, no marker or no reply text, exits quietly. With its
config read it always exits 0, so a failure here never holds a session's stop.
"""
import fcntl
import json
import os
import re
import secrets
import shlex
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_config  # noqa: E402

FOLLOW_IDLE_SECONDS = 30 * 60
FEED_KEEP = 50
# A Bash call's description can run long; the phone hears this much of it.
DETAIL_CHARS = 80
TAIL_BYTES = 256 * 1024
QUESTION = 'a question'
# The mark a stop that asks leaves, apart from any call's.
STOP = 'stop'
# A feed entry only a follow in milestones mode hears.
MILESTONE = 'milestone'
REFUSED = re.compile(r'a pull request for branch .* already exists')
# How often the answer form looks for an answer, and how long it waits for one. The wait ends
# short of the 600 second timeout its settings.json entry gives it, so it ends on its own.
ANSWER_POLL_SECONDS = 0.5
ANSWER_WAIT_SECONDS = 590
# How often the answer form reads the transcript for a result the app gave the call.
ANSWER_RESULT_SECONDS = 5
# The longest call input a voice chat reads back in full, as JSON text.
READ_BACK_CHARS = 1500
# Tools whose prompt stays in the app: approving either changes the session's mode.
APP_ONLY_TOOLS = ('EnterPlanMode', 'ExitPlanMode')
# A .claude folder named in a text field, as a path part: /repo/.claude/settings.json,
# .claude/hooks, ~/.claude, but not a file such as notes.claude.md.
CLAUDE_FOLDER = re.compile(r'(?:^|[^\w.-])\.claude(?=[/\\]|$|[^\w.-])')
# The path that follows a .claude folder, up to a space or a quote.
PATH_REST = re.compile(r'[^\s\'"]*')
# A worktree checkout under .claude/worktrees/<name>, and a step up out of a folder.
WORKTREE = re.compile(r'[/\\]worktrees[/\\]([^/\\]+)')
PARENT_STEP = re.compile(r'(?:^|[/\\])\.\.(?:[/\\]|$)')
# The input fields whose text a shell or an interpreter runs, which can move between
# folders as it runs.
COMMAND_FIELDS = ('command', 'cmd', 'script', 'shell', 'code')
# A plain worktree checkout path in a command: .claude/worktrees/<name>, not . or ..
COMMAND_WORKTREE = re.compile(
    r'\.claude[/\\]worktrees[/\\](?!\.\.?(?:[/\\\s\'"]|$))[^/\\\s\'"]+'
    r'(?=[/\\\s\'"]|$)')
# How a prompt's feed note says where it can be answered.
ANSWER_IN_APP = 'It has to be answered in the app.'
ANSWER_HERE = 'It can be answered with answer_prompt, or in the app.'
# What Claude reads when a voice chat denies a prompt.
DENIED = 'The user denied this from a voice chat.'
PULL_URL = re.compile(r'https://github\.com/[^/\s]+/[^/\s]+/pull/([0-9]+)')


def runtime_dir():
    return os.environ.get('XDG_RUNTIME_DIR') or '/tmp'


def bridge_dir():
    return os.path.join(runtime_dir(), 'voice-bridge')


def speech_dir():
    return os.path.join(runtime_dir(), 'speak-attention')


def socket_key(socket_path):
    """The socket's file name without .sock, the key the bridge files share."""
    name = os.path.basename(socket_path or '')
    return name[:-len('.sock')] if name.endswith('.sock') else ''


def speaking(session_id, folder):
    """Whether speech mode is on for the session, which speak-attention.sh marks."""
    return bool(session_id) and os.path.exists(os.path.join(folder, session_id + '.replies'))


def write_json(folder, name, value):
    """Writes folder/name through a temporary file, so the bridge never reads half of it."""
    os.makedirs(folder, mode=0o700, exist_ok=True)
    target = os.path.join(folder, name)
    fd, tmp = tempfile.mkstemp(dir=folder)
    with os.fdopen(fd, 'w') as out:
        json.dump(value, out)
    os.replace(tmp, target)
    return target


def add_to_feed(root, key, text, now, **fields):
    """Adds text to the session's feed, keeping the latest FEED_KEEP, with any fields given
    beside it. Returns the feed path."""
    folder = os.path.join(root, 'feed')
    os.makedirs(folder, mode=0o700, exist_ok=True)
    # Two hooks can add to one feed together, so the read and the write hold a lock. The
    # lock file stays when a follow stops, so a waiting hook never locks a second inode.
    with open(os.path.join(folder, key + '.lock'), 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            with open(os.path.join(folder, key + '.json')) as current:
                entries = json.load(current)
        except (OSError, ValueError):
            entries = []
        seq = entries[-1]['seq'] + 1 if entries else 1
        entry = {'seq': seq, 'at': now, 'text': text, **fields}
        entries = (entries + [entry])[-FEED_KEEP:]
        return write_json(folder, key + '.json', entries)


def followed(key, root, now=None):
    """Whether a phone follows the session with this key. The bridge touches follow/<key>
    each time the phone asks for the next update, so a follow nobody has polled for
    FOLLOW_IDLE_SECONDS no longer counts."""
    if not key:
        return False
    try:
        idle = (time.time() if now is None else now) - os.path.getmtime(
            os.path.join(root, 'follow', key))
    except OSError:
        return False
    return idle <= FOLLOW_IDLE_SECONDS


def append_feed(root, key, text, now, **fields):
    """Adds the reply to the session's feed while a phone follows it. Returns the feed path."""
    if not followed(key, root, now):
        return None
    return add_to_feed(root, key, text, now, **fields)


def milestones_followed(key, root, now=None):
    """Whether a phone follows the session in milestones mode."""
    if not followed(key, root, now):
        return False
    try:
        with open(os.path.join(root, 'follow', key + '.mode')) as mode:
            return mode.read().strip() == 'milestones'
    except OSError:
        return False


def stop_milestone(payload, session_pid=None, stop_ms=None):
    """Whether a stop is a milestone: its reply carries the ready line, it leaves the user a
    question, or no background work is due to wake the session, which is how a finished
    session's stop reads. session_pid and stop_ms are what background_pending.py takes as the
    session process and STOP_AT."""
    import background_pending as background  # noqa: E402, loaded only by the milestone form
    import ready_line  # noqa: E402
    import stop_attention as stops  # noqa: E402
    from transcript import read_transcript  # noqa: E402
    reply = payload.get('last_assistant_message') or ''
    entries = read_transcript(payload.get('transcript_path') or '')
    if ready_line.ready_numbers(payload, entries):
        return True
    # The question test stop_waiting marks the stop by, over the same closing rows.
    turn = stops.last_turn(tail_rows(payload.get('transcript_path')))
    if stops.asked(turn) or stops.ends_in_question(reply):
        return True
    started = background.started_ms(session_pid) if session_pid else None
    if background.pending(entries, started_ms=started):
        return False
    return stop_ms is None or not background.unanswered(entries,
                                                        stop_ms - background.STOP_SLACK_MS)


def pr_number(payload):
    """The pull request a successful `gh pr create` call printed, or None. gh prints the new
    pull request's URL on a line of its own, where a chained command's output names it inside
    a longer line. A create refused because the branch already has one prints that one's URL
    after its error, which is not an opening."""
    command = str((payload.get('tool_input') or {}).get('command') or '')
    if 'gh pr create' not in command:
        return None
    response = payload.get('tool_response')
    # gh prints its refusal, "a pull request for branch ... already exists:", on standard
    # error.
    stderr = response.get('stderr') if isinstance(response, dict) else None
    if REFUSED.search(str(stderr or '')):
        return None
    if isinstance(response, dict):
        response = response.get('stdout')
    # A refusal sent to standard output by 2>&1 puts the existing pull request's URL on the
    # line after it.
    lines = [line.strip() for line in str(response or '').splitlines()]
    for index, line in enumerate(lines):
        found = PULL_URL.fullmatch(line)
        if found and not (index and REFUSED.search(lines[index - 1])):
            return found.group(1)
    return None


# The shell words that end one command in a chain.
COMMAND_ENDS = {'&&', '||', ';', '|', '&', ';;'}


def pr_title(command):
    """The --title the `gh pr create` in a command passes, or ''. Only that command's own
    words are read, up to the end of its line, so another command in the chain never lends
    it a -t. A title built by the shell, from a variable or a substitution, reads as ''
    since only the shell knows its value; one in single quotes is literal and kept."""
    start = command.find('gh pr create')
    rest = command[start + len('gh pr create'):].replace('\\\n', ' ').split('\n', 1)[0]
    lexer = shlex.shlex(rest, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    words = []
    try:
        for word in lexer:
            if word in COMMAND_ENDS:
                break
            words.append(word)
    except ValueError:
        return ''
    title = ''
    for index, word in enumerate(words):
        if word in ('--title', '-t') and index + 1 < len(words):
            title = words[index + 1].strip()
            break
        if word.startswith('--title='):
            title = word[len('--title='):].strip()
            break
    if ('$' in title or '`' in title) and f"'{title}'" not in rest:
        return ''
    return title


def opened(payload, socket_path, root, now=None):
    """Adds a milestone for the pull request a followed session just opened. Returns the
    feed path, or None."""
    key = socket_key(socket_path)
    number = pr_number(payload)
    now = time.time() if now is None else now
    if not number or not milestones_followed(key, root, now):
        return None
    title = pr_title(str((payload.get('tool_input') or {}).get('command') or ''))
    text = f'Opened pull request {number}' + (f': {title}' if title else '') + '.'
    return add_to_feed(root, key, text, now, kind=MILESTONE)


def questions_text(payload):
    """The questions an AskUserQuestion call asks, run together."""
    tool_input = payload.get('tool_input')
    asks = tool_input.get('questions') if isinstance(tool_input, dict) else None
    return ' '.join(' '.join(str(ask.get('question') or '').split())
                    for ask in asks if isinstance(ask, dict)) if isinstance(asks, list) else ''


def push(text, socket_path, root, now=None):
    """Adds one spoken block to the session's feed, follow or not. Returns the feed path."""
    key = socket_key(socket_path)
    text = (text or '').strip()
    if not key or not text:
        return None
    return add_to_feed(root, key, text, time.time() if now is None else now)


def spoken_tool(name):
    """The tool's name as it reads aloud: mcp__ccd_host__sync_with_base reads as sync with
    base."""
    parts = name.split('__')
    if parts[0] == 'mcp' and len(parts) > 2:
        name = '__'.join(parts[2:])
    return name.replace('_', ' ').strip()


def waiting_reason(payload):
    """What a PermissionRequest or AskUserQuestion payload waits on, in a few words."""
    tool = str(payload.get('tool_name') or '')
    if tool == 'AskUserQuestion':
        return QUESTION
    if not spoken_tool(tool):
        return None
    tool_input = payload.get('tool_input')
    detail = tool_input.get('description') if isinstance(tool_input, dict) else None
    detail = ' '.join(str(detail or '').split())
    if len(detail) > DETAIL_CHARS:
        detail = detail[:DETAIL_CHARS].rsplit(' ', 1)[0] + '...'
    reason = f'a permission prompt for {spoken_tool(tool)}'
    return f'{reason}, {detail}' if detail else reason


def call_of(payload):
    """The call a prompt belongs to. A PermissionRequest carries no tool_use_id, so the tool
    and its input name the call, which its PostToolUse repeats."""
    tool_input = json.dumps(payload.get('tool_input'), sort_keys=True)
    return f"{payload.get('tool_name') or ''} {tool_input}"


def tail_rows(path, sidechains=False):
    """The transcript's main-thread rows within its last TAIL_BYTES, and with sidechains the
    rows of the subagents it holds too. A turn's closing rows, its wrap-up call and the
    results of its recent calls, sit well inside that."""
    try:
        with open(path, 'rb') as transcript:
            size = transcript.seek(0, os.SEEK_END)
            transcript.seek(max(0, size - TAIL_BYTES))
            lines = transcript.read().split(b'\n')
    except (OSError, TypeError):
        return []
    rows = []
    for line in lines[1:] if size > TAIL_BYTES else lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and (sidechains or not row.get('isSidechain')):
            rows.append(row)
    return rows


def row_time(row):
    """A transcript row's timestamp in epoch seconds, or None."""
    try:
        return datetime.fromisoformat(str(row.get('timestamp'))).timestamp()
    except ValueError:
        return None


def progress_ids(rows):
    """The toolUseID of every progress row in the rows."""
    return {row.get('toolUseID') for row in rows if row.get('type') == 'progress'}


def answered_calls(rows, started=False, known=()):
    """When each call in the rows last got a result, a denied prompt's refusal included, as
    {call: epoch seconds}, with calls named as call_of names them. With started, a progress
    row a running call writes counts too, since a call that runs was already allowed, unless
    its toolUseID is in known, the progress rows already there for an earlier run."""
    uses, answered = {}, {}
    for row in rows:
        if (started and row.get('type') == 'progress'
                and row.get('toolUseID') not in known):
            at = row_time(row)
            for use in (row.get('toolUseID'), row.get('parentToolUseID')):
                if use in uses and at is not None:
                    answered[uses[use]] = at
        content = (row.get('message') or {}).get('content')
        for block in content if isinstance(content, list) else []:
            if not isinstance(block, dict):
                continue
            if block.get('type') == 'tool_use':
                uses[block.get('id')] = call_of({'tool_name': block.get('name'),
                                                 'tool_input': block.get('input')})
            elif block.get('type') == 'tool_result' and block.get('tool_use_id') in uses:
                at = row_time(row)
                if at is not None:
                    answered[uses[block['tool_use_id']]] = at
    return answered


def drop_answered(root, key, payload):
    """Drops the marks whose call got a result after the mark, so an earlier run of the same
    command never answers the prompt open now."""
    answered = answered_calls(tail_rows(payload.get('transcript_path')))
    if answered:
        update_waiting(root, key, lambda calls: {
            name: entry for name, entry in calls.items()
            if answered.get(name, float('-inf')) < entry['at']})


def update_waiting(root, key, change):
    """Applies change to the session's open calls, {call: {'at', 'reason'}}, under a lock,
    since parallel calls and subagents run these hooks together. The file's own at and reason
    are the newest open call's, which the bridge reads; no open call removes the file."""
    folder = os.path.join(root, 'attention')
    os.makedirs(folder, mode=0o700, exist_ok=True)
    target = os.path.join(folder, key + '.json')
    with open(os.path.join(folder, key + '.lock'), 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            with open(target) as current:
                calls = json.load(current).get('calls') or {}
        except (OSError, ValueError, AttributeError):
            calls = {}
        calls = change(calls)
        if not calls:
            try:
                os.remove(target)
            except FileNotFoundError:
                pass
            return
        newest = max(calls.values(), key=lambda entry: entry['at'])
        write_json(folder, key + '.json', {**newest, 'calls': calls})


def mark_waiting(root, key, call, reason, now):
    update_waiting(root, key, lambda calls: {**calls, call: {'at': now, 'reason': reason}})


def clear_waiting(root, key):
    update_waiting(root, key, lambda calls: {})


def attention(payload, socket_path, root, now=None):
    """Marks what the session waits on the user for, or clears it once the session moves on.
    Returns the reason marked, or None."""
    key = socket_key(socket_path)
    if not key:
        return None
    now = time.time() if now is None else now
    event = payload.get('hook_event_name')
    tool = payload.get('tool_name')
    if event in ('PermissionRequest', 'PostToolUse'):
        # A denied prompt never gets a PostToolUse, but its refusal lands in the transcript
        # as the call's result, so the session's next prompt or finished call drops its mark.
        drop_answered(root, key, payload)
    if event == 'PermissionRequest' or (event == 'PreToolUse' and tool == 'AskUserQuestion'):
        reason = waiting_reason(payload)
        if reason:
            mark_waiting(root, key, call_of(payload), reason, now)
            # The question's own text reaches the feed through speak-attention.sh, as a
            # note milestones mode holds back, so that mode gets it here.
            where = ANSWER_IN_APP if app_only(payload) else ANSWER_HERE
            if event == 'PermissionRequest' and reason != QUESTION:
                append_feed(root, key, f'Waiting on you: {reason}. {where}', now,
                            milestone=True)
            elif event == 'PreToolUse' and milestones_followed(key, root, now):
                asks = questions_text(payload)
                add_to_feed(root, key, 'Waiting on you: a question. ' + (asks + ' ' if asks
                            else '') + where, now, kind=MILESTONE, copy=True)
        return reason
    # A finished call answers only its own prompt; another call's prompt can still be open.
    # It also means a turn is running, so the last stop's question no longer holds, even for
    # a turn an automated event started without a UserPromptSubmit.
    if event == 'PostToolUse':
        done = call_of(payload)
        update_waiting(root, key, lambda calls: {
            name: entry for name, entry in calls.items() if name not in (done, STOP)})
    elif event == 'UserPromptSubmit':
        clear_waiting(root, key)
    return None


def text_values(value, field=None):
    """Every string in a call's input, however deep in its lists and objects, as
    (field, text), with the name of the nearest field that holds it, or of the command field
    it sits anywhere under."""
    if isinstance(value, str):
        yield field, value
    elif isinstance(value, dict):
        for name, item in value.items():
            yield from text_values(item, field if field in COMMAND_FIELDS else name)
    elif isinstance(value, list):
        for item in value:
            yield from text_values(item, field)


def command_names_settings(text):
    """Whether a shell command can reach settings or hooks. A command can change folder as
    it runs, so a path in it cannot be read one word at a time: any settings.json, any
    .claude that is not a plain .claude/worktrees/<name> checkout path, and any .. in a
    command that names .claude at all keep the prompt in the app."""
    if 'settings.json' in text:
        return True
    if '.claude' not in text:
        return False
    return '..' in text or '.claude' in COMMAND_WORKTREE.sub('', text)


def names_claude_folder(text):
    """Whether the text names a path in a .claude folder. A worktree checkout under
    .claude/worktrees/<name>/ is ordinary source, so the folder that holds it does not
    count, unless the path steps back up out of it; the worktree's own .claude folder
    does count."""
    for found in CLAUDE_FOLDER.finditer(text):
        rest = PATH_REST.match(text, found.end()).group()
        tree = WORKTREE.match(rest)
        if (tree and tree.group(1) not in ('.', '..')
                and not PARENT_STEP.search(rest[tree.end():])):
            continue
        return True
    return False


def app_only(payload):
    """Whether the prompt has to be answered in the app: a tool that changes the session's
    mode, a path in a .claude folder, where settings and hooks live, or input too long for a
    voice chat to read back in full."""
    tool_input = payload.get('tool_input')
    if payload.get('tool_name') in APP_ONLY_TOOLS or not isinstance(tool_input, dict):
        return True
    # Every text in the input is checked for a path in a .claude folder, so a shell command
    # that writes into one stays in the app as an edit to a file there does. A field that
    # runs as a command is also held to the command rule, since a command can change folder.
    for field, value in text_values(tool_input):
        if names_claude_folder(value):
            return True
        if field in COMMAND_FIELDS and command_names_settings(value):
            return True
    return len(json.dumps(tool_input)) > READ_BACK_CHARS


def decision_for(payload, answer):
    """The PermissionRequest decision an answer asks for, or None for one that asks for
    nothing this prompt can take. A question's answer echoes the questions back with the
    answers beside them, the way AskUserQuestion takes them."""
    behavior = answer.get('behavior')
    if behavior == 'deny':
        return {'behavior': 'deny', 'message': DENIED}
    if behavior != 'allow':
        return None
    if payload.get('tool_name') != 'AskUserQuestion':
        return {'behavior': 'allow'}
    answers = answer.get('answers')
    if not isinstance(answers, dict) or not answers:
        return None
    return {'behavior': 'allow', 'updatedInput': {**payload['tool_input'], 'answers': answers}}


def read_json(path):
    """The file's object, or None when there is none or it does not parse."""
    try:
        with open(path) as current:
            value = json.load(current)
    except (OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def claim(path, claimed):
    """Renames the file to claimed and returns its object, or None when there is no file,
    the bridge cancelled it first, or it does not parse. A claimed file that does not parse
    is an empty object, so it is refused rather than left unanswered."""
    try:
        os.rename(path, claimed)
    except OSError:
        return None
    return read_json(claimed) or {}


def remove(path):
    """Removes the file, if it is there."""
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def open_calls(root, key):
    """The calls the attention form has marked open for the session."""
    try:
        with open(os.path.join(root, 'attention', key + '.json')) as current:
            return json.load(current).get('calls') or {}
    except (OSError, ValueError, AttributeError):
        return {}


def await_answer(payload, socket_path, root, clock=time.time, sleep=time.sleep,
                 wait=ANSWER_WAIT_SECONDS):
    """Offers a PermissionRequest to the voice bridge and waits for its answer. Returns the
    decision to print, or None to leave the prompt to the app.

    The prompt goes in prompts/<key>/<id>.json under an id made for this one request, with
    this process's id. The bridge writes answers/<key>/<id>.json only for a prompt it read
    back, so an answer reaches the one request it was read back for, and a stale or replayed
    one finds no hook waiting under its id. The hook claims an answer by renaming it to
    <id>.reading, so the bridge, which cancels by renaming it too, never cancels one the
    hook acts on. A claimed answer leaves <id>.took when it decides, or <id>.refused when
    it asks for nothing this prompt can take, before the claimed file goes. The wait ends
    early once the app has answered: the call's attention mark, seen once, is gone, or the
    transcript, a subagent's rows included, holds a result for the call or a new progress
    row of it running, newer than the prompt."""
    key = socket_key(socket_path)
    if not key or app_only(payload):
        return None
    prompt_id = secrets.token_hex(16)
    call = call_of(payload)
    started = clock()
    prompts = os.path.join(root, 'prompts', key)
    answers = os.path.join(root, 'answers', key)
    answer_path = os.path.join(answers, prompt_id + '.json')
    claimed = os.path.join(answers, prompt_id + '.reading')
    write_json(prompts, prompt_id + '.json', {
        'id': prompt_id, 'at': started, 'pid': os.getpid(),
        'tool': payload.get('tool_name'), 'input': payload.get('tool_input')})
    # Read once the prompt is offered, so a row written as it went up is counted as old.
    known = progress_ids(tail_rows(payload.get('transcript_path'), sidechains=True))
    try:
        seen = False
        read_at = started
        while clock() - started < wait:
            answer = claim(answer_path, claimed)
            if answer is not None:
                decision = answer.get('id') == prompt_id and decision_for(payload, answer)
                write_json(answers, prompt_id + ('.took' if decision else '.refused'),
                           {'at': clock()})
                remove(claimed)
                if decision:
                    return decision
            marked = call in open_calls(root, key)
            if seen and not marked:
                return None
            seen = seen or marked
            if clock() - read_at >= ANSWER_RESULT_SECONDS:
                read_at = clock()
                rows = tail_rows(payload.get('transcript_path'), sidechains=True)
                if answered_calls(rows, started=True, known=known).get(
                        call, float('-inf')) > started:
                    return None
            sleep(ANSWER_POLL_SECONDS)
        return None
    finally:
        for path in (os.path.join(prompts, prompt_id + '.json'), answer_path, claimed):
            remove(path)


def stop_waiting(payload, socket_path, root, now=None):
    """Marks a stop that leaves the user something to answer as a question, and clears the
    mark on any other stop. Returns the reason marked, or None."""
    key = socket_key(socket_path)
    if not key:
        return None
    import stop_attention as stops  # noqa: E402, loaded only on a Stop
    # The same question test stop_attention.py speaks by, over the turn's closing rows only.
    turn = stops.last_turn(tail_rows(payload.get('transcript_path')))
    if stops.asked(turn) or stops.ends_in_question(payload.get('last_assistant_message')):
        now = time.time() if now is None else now
        update_waiting(root, key, lambda calls: {STOP: {'at': now, 'reason': QUESTION}})
        return QUESTION
    clear_waiting(root, key)
    return None


def handle(payload, socket_path, root, now=None, speech=None):
    """Feeds a followed session's reply, marked reply, and writes the reply file when a
    request is pending.

    In speech mode the feed already holds the reply from speak-attention.sh's pushes, so only
    the reply file is written. Returns the reply file's path, or None."""
    key = socket_key(socket_path)
    text = (payload.get('last_assistant_message') or '').strip()
    if not key or not text:
        return None
    now = time.time() if now is None else now
    if not speaking(payload.get('session_id'), speech or speech_dir()):
        append_feed(root, key, text, now, reply=True)
    if not os.path.exists(os.path.join(root, 'pending', key)):
        return None
    return write_json(os.path.join(root, 'replies'), key + '.json', {'at': now, 'text': text})


def milestone_stop(payload, socket_path, root, now=None, check=stop_milestone):
    """Adds a kind milestone copy of the stop's reply, marked reply, while a follow is in
    milestones mode and check(payload) says the stop is one. Returns the feed path, or None."""
    key = socket_key(socket_path)
    text = (payload.get('last_assistant_message') or '').strip()
    now = time.time() if now is None else now
    if not key or not text or not milestones_followed(key, root, now) or not check(payload):
        return None
    # The check can run for a while; a follow stopped meanwhile gets no feed back.
    if not milestones_followed(key, root):
        return None
    # Stamped when it lands, after the check, so the feed's times follow its order.
    return add_to_feed(root, key, text, time.time(), kind=MILESTONE, copy=True, reply=True)


def ready_numbers(payload):
    """The pull requests the stop's ready line names, by the test the milestone form marks a
    ready stop with."""
    import ready_line  # noqa: E402, loaded only by the ready form
    from transcript import read_transcript  # noqa: E402
    entries = read_transcript(payload.get('transcript_path') or '')
    return ready_line.ready_numbers(payload, entries)


def carries_ready_line(payload):
    """Whether the stop's final reply, read as ready_numbers reads it, holds a ready line:
    the quick test that decides whether the ready form runs at all. The final reply sits at
    the transcript's end, so the tail holds all of it."""
    import ready_line  # noqa: E402
    reply = ready_line.final_reply(payload, tail_rows(payload.get('transcript_path')))
    return bool(ready_line.READY.search(reply))


def ready(payload, socket_path, root, now=None, check=ready_numbers):
    """Records each pull request a stop's ready line names that check lets through, as
    ready/<key>-<number>.json, for the bridge to announce whether or not a phone follows the
    session. Returns the paths written."""
    key = socket_key(socket_path)
    if not key or not carries_ready_line(payload):
        return []
    numbers = check(payload)
    # Stamped when it lands, after the check, so a later ready line always reads as newer.
    now = time.time() if now is None else now
    return [write_json(os.path.join(root, 'ready'), f'{key}-{number}.json',
                       {'number': int(number), 'at': now,
                        'session': payload.get('session_id') or '',
                        'cwd': payload.get('cwd') or ''})
            for number in numbers]


def spawn_ready(payload):
    """Runs the ready form in a process of its own, apart from the Stop hook, since its check
    reads the whole transcript."""
    child = subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), '--config', hook_config.file(), 'ready'],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    child.stdin.write(json.dumps(payload).encode())
    child.stdin.close()


def start_ready(payload, spawn=spawn_ready):
    """Starts the ready form for a stop whose reply carries a ready line. Returns whether it
    did."""
    if not carries_ready_line(payload):
        return False
    spawn(payload)
    return True


def answer_main(socket_path):
    """Runs the answer form and prints the decision it returns, if any."""
    # Claude Code can end the hook once the app answers, and a SIGTERM that exits through
    # SystemExit still runs await_answer's cleanup.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        decision = await_answer(json.load(sys.stdin), socket_path, bridge_dir())
    except Exception as error:  # noqa: BLE001
        print(f'voice_bridge_reply: {error}', file=sys.stderr)
        return 0
    if decision:
        print(json.dumps({'hookSpecificOutput': {
            'hookEventName': 'PermissionRequest', 'decision': decision}}))
    return 0


def main():
    # When the hook started, in epoch ms, for background_pending.py's STOP_AT.
    stop_ms = time.time() * 1000
    args = hook_config.take(sys.argv)[1:]
    socket_path = os.environ.get('CLAUDE_CODE_MESSAGING_SOCKET')
    if args == ['answer']:
        return answer_main(socket_path)
    try:
        if args == ['push']:
            steps = [lambda text: push(text, socket_path, bridge_dir())]
            payload = sys.stdin.read()
        elif args == ['ready']:
            payload = json.load(sys.stdin)
            steps = [lambda p: ready(p, socket_path, bridge_dir())]
        elif args == ['opened']:
            payload = json.load(sys.stdin)
            steps = [lambda p: opened(p, socket_path, bridge_dir())]
        elif args == ['milestone']:
            payload = json.load(sys.stdin)
            # The hook command execs this script, so its parent is the session process.
            steps = [lambda p: milestone_stop(p, socket_path, bridge_dir(), check=lambda q:
                                              stop_milestone(q, os.getppid(), stop_ms))]
        elif args == ['attention']:
            payload = json.load(sys.stdin)
            steps = [lambda p: attention(p, socket_path, bridge_dir())]
        elif args == []:
            payload = json.load(sys.stdin)
            steps = [lambda p: handle(p, socket_path, bridge_dir()),
                     lambda p: stop_waiting(p, socket_path, bridge_dir()),
                     start_ready]
        else:
            # Any other form does nothing. Hook entries copied from an earlier release can
            # still pass `spoken`, which no longer exists, and a payload that is not a Stop
            # must never reach the Stop handlers.
            return 0
    except Exception as error:  # noqa: BLE001
        print(f'voice_bridge_reply: {error}', file=sys.stderr)
        return 0
    # A Stop's reply and its attention mark are separate writes, so one failing leaves the
    # other to run.
    for step in steps:
        try:
            step(payload)
        except Exception as error:  # noqa: BLE001
            print(f'voice_bridge_reply: {error}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
