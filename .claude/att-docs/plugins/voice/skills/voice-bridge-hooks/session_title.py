#!/usr/bin/env python3
"""Sets the title of the Claude session it runs in, without the voice bridge.

usage: session_title.py work "<work name>"
       session_title.py status "<status>"
       session_title.py show
       session_title.py [--config <extension.json>] hook prompt|stop < <hook payload>

A session title reads "<base>", "<base> - <work>", and, when the session has stopped or is
waiting, "<base> - <work> (<status>)". The base is the title the session started with, such
as "Overmind 2". Setting the work name replaces the old work name and takes any status away,
since work has resumed. Setting a status keeps the base and the work name and replaces the old
status. An empty work name or an empty status takes that part away. The status is one of
STATUSES, so a title can always be taken apart again, and the voice bridge strips the same
suffix when it reads a base title.

The session is the nearest ancestor of this process that has a file in ~/.claude/sessions,
which is the Claude Code process whose shell ran this script. The title is changed the way
/rename does it: the same control message the app's session list sends is written to the
session's own inbox socket, then the session's file is read until it shows the new title.

hook is the entry point for a hooks file to call, so the status follows the session without
the session setting it. It reads the hook payload on stdin, never changes the work name, waits at
most RENAME_WAIT_SECONDS for the rename to show so the next hook reads it, and always exits 0
without a word, since a title is never worth a failed turn. `hook prompt` (UserPromptSubmit)
sets "working": the user has answered, so a status is over. `hook stop` (Stop) sets one of:

- "needs you", when the turn leaves the user something to answer: a question in the wrap-up
  box, a last line that ends in a question mark, or the review label added to a pull request.
  A permission prompt blocks inside a turn and is answered before the turn can stop, so a
  stop never sees one;
- "working", when background work is due to wake the session, or an event was delivered
  after the stop;
- "idle", otherwise.

A "stuck", "stopped" or "waiting on CI" already on the title is kept at a stop, since the
prompt set "working" at the start of the turn and the session set it since. A "needs you" or
a "waiting on <partner>" (the session waits on another session, such as "waiting on Data", and
needs nothing from the user) is kept only when a `status` command in the turn that just ended
set it last, so one left from an earlier turn does not stick when a relayed message started
this turn with no prompt hook. While the title says it waits on a partner, a closing question
and the review label are not for the user and change nothing; a question in the wrap-up box is,
and sets "needs you". A prompt the user types sets "working", and naming new work takes any
status away, so either ends it. A prompt that is an automated event leaves a "stuck",
"stopped" or "waiting on CI" and sets "working" over any other status, a partner wait
included, since the partner may have answered. The hook does nothing for a subagent (a
payload with an agent_id), for any event but the one the command names, for a session with no
title, for a stop with no transcript, when another rename changed the title while it ran, or
when the payload's session is not this one. The extension file's review label is read when
--config names one that reads; without one the label check is skipped.

SESSION_TITLE_SESSIONS_DIR, SESSION_TITLE_PROC_DIR and SESSION_TITLE_PID point it at fixtures
in tests. It prints what happened and exits 0, or prints why not to stderr and exits 1.
"""
import contextlib
import io
import json
import os
import re
import socket
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import background_pending  # noqa: E402
import hook_config  # noqa: E402
import stop_attention  # noqa: E402
from transcript import EVENT_TAG, REMINDER, read_transcript  # noqa: E402

STATUSES = ("idle", "waiting on you", "stuck", "stopped", "waiting on CI", "needs you", "working")
SEPARATOR = " - "
# The longest title the sidebar and the bridge take.
MAX_TITLE = 60
# How long to read the session's file for the new title before saying it did not appear.
WAIT_SECONDS = 5.0
POLL_SECONDS = 0.25
# A status with the number Claude Code may add after it to a title another session holds:
# "Merge (idle) 2". Group 1 is the status and group 2 the number, with its space.
NUMBERED_STATUS = re.compile(
    r"\s+\((%s|waiting on [^()]+?)\)(\s+\d+)?$" % "|".join(re.escape(s) for s in STATUSES))
# "waiting on <partner>": the session waits on another session, not on the user. The partner is
# a short name; "you" and "CI" are statuses of their own.
PARTNER_WAIT = re.compile(r"waiting on ([^()]+)")
NOT_PARTNERS = ("you", "ci")
MAX_PARTNER = 24


def is_partner_wait(status):
    """Whether status is "waiting on <partner>" with a name that fits a title."""
    found = PARTNER_WAIT.fullmatch(status or "")
    if not found:
        return False
    name = found.group(1)
    return (name == " ".join(name.split()) and len(name) <= MAX_PARTNER
            and name.lower() not in NOT_PARTNERS)


def split_title(title):
    """(base, work, status) for a title; work and status are empty when it has none. The
    last separator ends the base, as in the voice bridge. A number after the status joins the
    base, so "Merge (idle) 2" is ("Merge 2", "", "idle") and a new status goes after it."""
    title = title.strip()
    status = ""
    number = ""
    found = NUMBERED_STATUS.search(title)
    if found:
        status = found.group(1)
        number = found.group(2) or ""
        title = title[:found.start()].strip()
    at = title.rfind(SEPARATOR)
    if at < 0:
        return title + number, "", status
    return title[:at].strip() + number, title[at + len(SEPARATOR):].strip(), status


def clip_to_words(text, room):
    """text cut to at most room characters, on a word when it can be."""
    if len(text) <= room:
        return text
    cut = re.sub(r"\s+\S*$", "", text[:room + 1])[:room].strip()
    return cut or text[:room]


def compose(base, work, status):
    """The title for a base, a work name and a status. The work name gives up characters
    first when the title would pass MAX_TITLE."""
    work = " ".join(work.replace(SEPARATOR, " ").split())
    tail = " (%s)" % status if status else ""
    if work:
        room = MAX_TITLE - len(base) - len(SEPARATOR) - len(tail)
        if room >= 1:
            return base + SEPARATOR + clip_to_words(work, room) + tail
        # A status is worth more than the work name, so a long base keeps the status alone.
        if tail:
            return compose(base, "", status)
        raise ValueError(
            "%r leaves no room for a work name under %d characters" % (base, MAX_TITLE))
    if len(base) + len(tail) > MAX_TITLE:
        raise ValueError("%r leaves no room for a status under %d characters" % (base, MAX_TITLE))
    return base + tail


def new_title(current, command, value):
    """The title after `command` ('work' or 'status') is given `value`."""
    base, work, status = split_title(current)
    if command == "work":
        return compose(base, value, "")
    if value and value not in STATUSES and not is_partner_wait(value):
        raise ValueError("status is one of: %s, waiting on <partner>" % ", ".join(STATUSES))
    return compose(base, work, value)


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _parent_of(pid, proc_dir):
    """The parent process id of pid from /proc, or None where it cannot be read."""
    try:
        with open(os.path.join(proc_dir, str(pid), "stat")) as f:
            # The command name sits in parentheses and may hold spaces.
            return int(f.read().rsplit(")", 1)[1].split()[1])
    except (OSError, IndexError, ValueError):
        return None


def find_own_session(sessions_dir, proc_dir, start):
    """The session file entry of the nearest ancestor of process `start` (itself included)
    that has one with an inbox socket, or None."""
    seen = set()
    pid = start
    while pid and pid > 1 and pid not in seen:
        seen.add(pid)
        entry = _read_json(os.path.join(sessions_dir, "%d.json" % pid))
        if isinstance(entry, dict) and entry.get("messagingSocketPath"):
            # The file is named for the process, so the process id is known even when the
            # file does not carry it.
            entry["pid"] = pid
            return entry
        pid = _parent_of(pid, proc_dir)
    return None


def send_rename(entry, name):
    """Writes the rename control message to the session's inbox socket."""
    message = {"type": "control", "action": "rename", "name": name}
    if entry.get("sessionId"):
        message["session_id"] = entry["sessionId"]
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
        conn.settimeout(5)
        conn.connect(entry["messagingSocketPath"])
        conn.sendall((json.dumps(message) + "\n").encode("utf-8"))


def wait_for_title(sessions_dir, pid, name, wait=None, same=None):
    """Whether the session's file shows `name` within `wait` seconds (WAIT_SECONDS by
    default). `same(shown, name)` says whether a title the file shows counts as `name`; the
    default is that they are equal."""
    deadline = time.monotonic() + (WAIT_SECONDS if wait is None else wait)
    while True:
        entry = _read_json(os.path.join(sessions_dir, "%d.json" % pid))
        shown = str(entry.get("name") or "").strip() if isinstance(entry, dict) else None
        if shown is not None and (same(shown, name) if same else shown == name):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(POLL_SECONDS)


HOOK_EVENTS = {"prompt": "UserPromptSubmit", "stop": "Stop"}
# The statuses only the session can know. The hook only ever writes working, needs you and
# idle, so one of these on the title is the session's own, and the hook leaves it. A prompt
# the user types sets working, which ends it; so does the session naming new work.
KEPT_ACROSS_EVENTS = ("stuck", "stopped", "waiting on CI")
# "needs you" and "waiting on <partner>" are the session's too, but the hook writes the first
# itself and a relayed message starts a turn with no prompt hook to end either. At a stop they
# are kept only when the session set them in the turn that just ended (set_this_turn).


def set_this_turn(turn, status):
    """Whether the latest status command of the turn set status."""
    commands = stop_attention.status_commands(turn)
    return bool(commands) and commands[-1] == status


# How long the hook waits for its rename to show in the session's file, so a hook that runs
# right after it reads the title it set. A short turn can end that fast.
RENAME_WAIT_SECONDS = 1.0


def shows_rename(shown, wanted):
    """Whether the title the session's file shows is the rename asked for. Claude Code may add
    a number after the status of a title another session holds, so the work name and the
    status are what must agree."""
    return split_title(shown)[1:] == split_title(wanted)[1:]


def stop_status(payload, entries, pid, proc_dir, stop_ms, labeling=True):
    """The status a stopped session shows: needs you, working or idle, in that order."""
    turn = stop_attention.last_turn(entries)
    asking = stop_attention.asked(turn) \
        or stop_attention.ends_in_question(payload.get("last_assistant_message"))
    if not asking and labeling:
        try:
            asking = stop_attention.labeled(turn)
        except BaseException:  # an unreadable config only skips the label check
            asking = False
    if asking:
        return "needs you"
    started = background_pending.started_ms(pid, proc=proc_dir)
    if background_pending.pending(entries, started_ms=started) \
            or background_pending.unanswered(
                entries, stop_ms - background_pending.STOP_SLACK_MS):
        return "working"
    return "idle"


def hook_main(event, stdin, sessions_dir, proc_dir, start, config=None):
    """The hook for `event` ("prompt" or "stop"). Returns 0 whatever happens, and writes
    nothing, not even the message the extension file reader prints before it gives up."""
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            _hook(event, stdin, sessions_dir, proc_dir, start, config)
        except BaseException:  # a title is never worth a failed turn
            pass
    return 0


def _load_config(config):
    """Whether the extension file read, so the review label can be checked. A file that is
    missing or does not read only skips that check."""
    if not config or not os.path.isfile(config):
        return False
    try:
        hook_config.use(config)
    except SystemExit:
        return False
    # Both fields build the label patterns the check reads.
    return hook_config.has("reviewLabel") and hook_config.has("readyLine")


def _hook(event, stdin, sessions_dir, proc_dir, start, config):
    # This process started just after the stop it answers, and an event delivered from then on
    # has started a turn after it. The clock is the fallback where /proc cannot say.
    stop_ms = background_pending.started_ms(os.getpid()) or time.time() * 1000
    payload = json.loads(stdin.read())
    if not isinstance(payload, dict) or payload.get("agent_id") \
            or payload.get("hook_event_name") != HOOK_EVENTS[event]:
        return
    entry = find_own_session(sessions_dir, proc_dir, start)
    if entry is None:
        return
    if payload.get("session_id") and entry.get("sessionId") \
            and payload["session_id"] != entry["sessionId"]:
        return
    current = str(entry.get("name") or "").strip()
    if not current:
        # A session with no title has no base to keep, and a bare status is not a title.
        return
    if event == "prompt":
        # An event the app delivers as a prompt is not the user answering, so a status only
        # the session can know stays. The turn it starts is work, so any other status goes.
        if EVENT_TAG.match(REMINDER.sub("", str(payload.get("prompt") or ""))) \
                and split_title(current)[2] in KEPT_ACROSS_EVENTS:
            return
        status = "working"
    else:
        shown = split_title(current)[2]
        if shown in KEPT_ACROSS_EVENTS:
            return
        path = payload.get("transcript_path") or ""
        entries = read_transcript(path) if os.path.isfile(path) else []
        if not entries:
            # With no transcript to read, the turn's work is unknown, so the title stays.
            return
        turn = stop_attention.last_turn(entries)
        held = (shown == "needs you" or is_partner_wait(shown)) and set_this_turn(turn, shown)
        # A closing question or the review label is not for the user while the session waits
        # on a partner. A question in the wrap-up box is, by construction.
        if held and (shown == "needs you" or not stop_attention.asked(turn)):
            return
        if held:
            status = "needs you"
        else:
            status = stop_status(payload, entries, int(entry["pid"]), proc_dir, stop_ms,
                                 _load_config(config))
    name = new_title(current, "status", status)
    if name == current:
        return
    shown = _read_json(os.path.join(sessions_dir, "%d.json" % int(entry["pid"])))
    if not isinstance(shown, dict) or str(shown.get("name") or "").strip() != current:
        # Another hook or the user renamed the session while this one read the transcript.
        return
    send_rename(entry, name)
    wait_for_title(sessions_dir, int(entry["pid"]), name, wait=RENAME_WAIT_SECONDS,
                   same=shows_rename)


def main(argv, out=None, err=None, stdin=None):
    out = out or sys.stdout
    err = err or sys.stderr
    args = argv[1:]
    config = None
    # run.sh puts --config <extension.json> ahead of the script's own arguments.
    if args and args[0] == "--config":
        config = args[1] if len(args) > 1 else None
        args = args[2:]
    elif args and args[0].startswith("--config="):
        config = args[0].split("=", 1)[1]
        args = args[1:]
    if args and args[0] == "hook":
        given = os.environ.get("SESSION_TITLE_PID") or str(os.getppid())
        if len(args) != 2 or args[1] not in HOOK_EVENTS or not re.fullmatch(r"[0-9]+", given):
            return 0
        return hook_main(
            args[1], stdin or sys.stdin,
            os.environ.get("SESSION_TITLE_SESSIONS_DIR", os.path.expanduser("~/.claude/sessions")),
            os.environ.get("SESSION_TITLE_PROC_DIR", "/proc"), int(given), config)
    if not args or args[0] not in ("work", "status", "show") \
            or (args[0] != "show" and len(args) != 2) or (args[0] == "show" and len(args) != 1):
        print(__doc__.strip().splitlines()[2], file=err)
        return 1
    sessions_dir = os.environ.get(
        "SESSION_TITLE_SESSIONS_DIR", os.path.expanduser("~/.claude/sessions"))
    proc_dir = os.environ.get("SESSION_TITLE_PROC_DIR", "/proc")
    given = os.environ.get("SESSION_TITLE_PID") or str(os.getppid())
    if not re.fullmatch(r"[0-9]+", given):
        print("SESSION_TITLE_PID must be a process id, not %r." % given, file=err)
        return 1
    start = int(given)
    entry = find_own_session(sessions_dir, proc_dir, start)
    if entry is None:
        print("This process has no Claude session above it, so there is no title to set.",
              file=err)
        return 1
    current = str(entry.get("name") or "").strip()
    if args[0] == "show":
        print(current, file=out)
        return 0
    try:
        name = new_title(current, args[0], " ".join(args[1].split()))
    except ValueError as error:
        print(str(error), file=err)
        return 1
    if name == current:
        print("The session is already called %s." % current, file=out)
        return 0
    try:
        send_rename(entry, name)
    except OSError as error:
        print("Could not reach the session's inbox: %s" % error, file=err)
        return 1
    if wait_for_title(sessions_dir, int(entry["pid"]), name):
        print("Renamed %s to %s." % (current, name), file=out)
    else:
        print("Asked the session to rename itself to %s, but its title did not change within "
              "%g seconds." % (name, WAIT_SECONDS), file=out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
