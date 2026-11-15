#!/usr/bin/env python3
"""Names the background work in a session that will wake it on its own.

usage: background_pending.py [--describe] <transcript.jsonl> [session-pid]

Prints the ids of the pending work, one per line, and exits 0 when there is any, 1 when
there is none. With --describe each line is the id, the kind of work (agent, bash, run,
monitor, wakeup or work), and what it is, separated by tabs. speak-attention.sh asks it at Stop, so a turn that ends while something is
still due to wake the session stays quiet. STOP_AT in the environment is when the Stop hook
started, in epoch ms.

The main thread's tool results name each launch; a subagent's own launches do not wake
the session and are left out:

- a Bash command run in the background, by its backgroundTaskId;
- an Agent or Workflow launched asynchronously, or a skill forked into the background, by
  its agentId or taskId;
- an agent a message resumed, by its resumedAgentId;
- an agent the harness restarted after the previous session process ended, by the id in
  the notice that says so, from when that notice is delivered;
- a Monitor, by its taskId, pending until its timeout runs out unless it is persistent;
- a ScheduleWakeup, by the time it fires; only the latest one counts.

A launch ends at the task notification or task_status row that carries its id with a final
status, or at a TaskStop that stopped it. A notification still in the queue, final or
not, wakes the session when it is delivered, so it is pending until then. A notice or other
event delivered since the Stop hook started has started a turn after this stop, so its task
id, or its tag when it names no task, is printed too.

Background work, its notification queue and its wakeups all live in the session process,
and die with it. Given the session process id, which is the hook's parent, work launched or
queued before that process started was ended by a restart that wrote nothing, so it is not
pending.
"""
import os
import re
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transcript import (  # noqa: E402
    EVENT, EVENT_TAG, REMINDER, prompt_kind, read_transcript)

FINAL = {'completed', 'failed', 'killed', 'stopped'}
NOTICE = re.compile(r'<task-id>([^<]+)</task-id>.*?<status>([a-z_]+)</status>', re.S)
RESTARTED = re.compile(
    r'<task-id>([^<]+)</task-id>\s*<summary>[^<]*was restarted after the previous session ended')
STOPPED = 'Successfully stopped task'
WAKEUP = 'wakeup'
# /proc dates a process start from the clock as it reads now, so a clock step since the start
# moves it. A minute covers the steps a network time sync makes.
CLOCK_SLACK_MS = 60_000
# Room for the clock reading between the stop and the hook's start. The app delivers the
# next event only once the sync Stop hooks finish, and this hook starts beside them, so the
# delivery comes after the start; an event turn takes well over this from event to reply.
STOP_SLACK_MS = 250


def stamp_ms(entry):
    """The entry's timestamp in epoch milliseconds, or None."""
    try:
        when = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
    except (AttributeError, KeyError, TypeError, ValueError):
        return None
    return when.timestamp() * 1000


def launch(result, at):
    """(id, deadline in epoch ms or None) for a tool result that starts background work,
    or None."""
    if result.get('backgroundTaskId'):
        return result['backgroundTaskId'], None
    if result.get('resumedAgentId'):
        return result['resumedAgentId'], None
    status = result.get('status')
    if status == 'async_launched' or (status == 'forked' and result.get('background')):
        ident = result.get('agentId') or result.get('taskId')
        return (ident, None) if ident else None
    if result.get('taskId') and ('timeoutMs' in result or 'persistent' in result):
        if result.get('persistent') or at is None or 'timeoutMs' not in result:
            return result['taskId'], None
        return result['taskId'], at + result['timeoutMs']
    if 'scheduledFor' in result:
        return WAKEUP, result['scheduledFor']
    return None


def stopped(result):
    """The id a TaskStop result says it stopped, or None."""
    message = result.get('message')
    if result.get('task_id') and isinstance(message, str) and message.startswith(STOPPED):
        return result['task_id']
    return None


def delivered_text(entry):
    """The text a row delivers from the notification queue, or None. A queued notification
    is delivered as a queued command, a user message, or the queue's remove."""
    kind = entry.get('type')
    content = None
    if kind == 'queue-operation':
        content = entry.get('content') if entry.get('operation') == 'remove' else None
    elif kind == 'attachment':
        content = (entry.get('attachment') or {}).get('prompt')
    elif kind == 'user':
        content = (entry.get('message') or {}).get('content')
    if isinstance(content, list):
        content = ' '.join(b.get('text', '') for b in content if isinstance(b, dict))
    return content if isinstance(content, str) else None


def notification(text):
    """text when it is a task notification, else an empty string, so a message that only
    quotes one, such as a subagent's report, names no task."""
    return text if isinstance(text, str) and text.lstrip().startswith('<task-notification>') else ''


def notices(entry, text):
    """(id, status) for each task notification an entry delivers as text, and for the task
    a task_status row reports on."""
    attachment = entry.get('attachment') or {}
    if entry.get('type') == 'attachment' and attachment.get('type') == 'task_status' \
            and attachment.get('taskId'):
        return [(attachment['taskId'], attachment.get('status'))]
    return NOTICE.findall(notification(text))


def started_ms(pid, proc='/proc', ticks=None):
    """When process pid started, in epoch ms, or None where /proc cannot say, as on
    Windows. ticks is the clock rate /proc counts in, read from the system when None."""
    try:
        ticks = ticks or os.sysconf('SC_CLK_TCK')
        with open(os.path.join(proc, 'stat')) as f:
            boot = next(int(line.split()[1]) for line in f if line.startswith('btime '))
        with open(os.path.join(proc, str(pid), 'stat')) as f:
            # The command name sits in parentheses and may hold spaces.
            start = int(f.read().rsplit(')', 1)[1].split()[19])
        return (boot + start / ticks) * 1000
    except (AttributeError, OSError, StopIteration, ValueError, IndexError):
        return None


def launched(entries):
    """What the entries leave open, as ({id: (deadline, when)} for the work they started and
    did not see end, {text: [(ids, when)]} for the notices still in the queue, the latest
    row's epoch ms). when is the epoch ms of the launch or the enqueue.

    A notice in the queue is matched to its delivery by its whole text, so two events queued
    for one task are each pending until their own delivery. A delivery is written either as
    one user row or as a queued command beside the queue's remove, so the user row or the
    remove takes one copy of the text off the queue and the queued command takes none."""
    open_work, queued, latest = {}, {}, None
    # When each agent a message resumed was resumed, while that run is open.
    resumed = {}
    # When the copy a delivery carries was enqueued, by text, for the second row of a
    # delivery written as a queued command beside the queue's remove.
    sent_at = {}
    for entry in entries:
        at = stamp_ms(entry)
        if at is not None and (latest is None or at > latest):
            latest = at
        result = entry.get('toolUseResult') if entry.get('type') == 'user' else None
        if isinstance(result, dict):
            started = launch(result, at)
            if started:
                open_work.pop(started[0], None)
                open_work[started[0]] = (started[1], at)
                resumed.pop(started[0], None)
                if result.get('resumedAgentId'):
                    resumed[started[0]] = at
            open_work.pop(stopped(result), None)
        if entry.get('type') == 'queue-operation' and entry.get('operation') == 'enqueue':
            text = str(entry.get('content', ''))
            ids = [ident for ident, _ in NOTICE.findall(notification(text))]
            ids += RESTARTED.findall(notification(text))
            if ids:
                queued.setdefault(text, []).append((ids, at))
        text = delivered_text(entry)
        sent = queued[text][0][1] if text in queued else sent_at.get(text)
        if sent is None and entry.get('type') == 'attachment':
            # The queued command is stamped with the time it was enqueued, which also
            # covers a delivery whose remove is written first.
            sent = at
        if text in queued:
            sent_at[text] = sent
        if text in queued and entry.get('type') != 'attachment':
            queued[text].pop(0)
            if not queued[text]:
                del queued[text]
        for ident in RESTARTED.findall(notification(text)):
            open_work.pop(ident, None)
            open_work[ident] = (None, at)
        for ident, status in notices(entry, text):
            if status in FINAL:
                # A notice queued before an agent was resumed is about the run before,
                # so the resumed run goes on. Other work can finish before its launch row
                # is written, so its own notice may be queued first.
                if not (sent is not None and (resumed.get(ident) or 0) > sent):
                    open_work.pop(ident, None)
                    resumed.pop(ident, None)
                # A final status is the task's last word, so older notices for it that
                # never came out of the queue have nothing left to say. A task_status row
                # is no delivery, so the notice it reports on is still to come.
                for waiting in list(queued) if text is not None else []:
                    queued[waiting] = [([i for i in ids if i != ident], when)
                                       for ids, when in queued[waiting]]
                    queued[waiting] = [copy for copy in queued[waiting] if copy[0]]
                    if not queued[waiting]:
                        del queued[waiting]
        if entry.get('type') != 'attachment':
            sent_at.pop(text, None)
    return open_work, queued, latest


def pending(entries, now_ms=None, started_ms=None):
    """The ids of the work still due to wake the session, in launch order, then the ids
    of notices still in the queue. started_ms is when the session process started, None
    when it cannot be found.

    The session process wrote the transcript's latest row, so a process that started after
    that row is some other one, and its start time says nothing about a restart. A launch
    with no timestamp cannot be placed after the start, so it counts as before it. The start
    is read against the clock as it is now, so a launch within CLOCK_SLACK_MS before it still
    counts, in case the clock stepped since; the harness ends work a restart left behind
    with a stopped notice of its own."""
    now_ms = time.time() * 1000 if now_ms is None else now_ms
    open_work, queued, latest = launched(entries)
    if started_ms is not None and latest is not None and started_ms > latest:
        started_ms = None

    def before_start(at):
        return started_ms is not None and (at is None or at < started_ms - CLOCK_SLACK_MS)

    ids = [i for i, (due, at) in open_work.items()
           if (due is None or due > now_ms) and not before_start(at)]
    for copies in queued.values():
        for waiting, at in copies:
            ids += [i for i in waiting if i not in ids and not before_start(at)]
    return ids


def unanswered(entries, stop_ms):
    """What the app delivered from stop_ms on: the ids a task notification names, or the tag
    of any other event. A delivered event starts a turn, and the Stop hook runs beside the
    session rather than before it, so it can read the transcript after the delivery. The
    session has moved on to that turn, and the work it may launch is not written yet.

    stop_ms is when the Stop hook started, less STOP_SLACK_MS for the time the hook takes to
    launch. The event that started the stopping turn is older than that by the whole turn,
    so it is left out whether or not the turn's reply row is written yet. A prompt the user
    typed is left out, since the user is already there.

    An event delivered after a stop is written as a user row. A queued command joins a turn
    that is still running and carries the time it was enqueued, and the queue's remove can
    take a notice off the queue without delivering it, so neither marks a new turn."""
    ids = []
    for entry in reversed(entries):
        at = stamp_ms(entry)
        if at is not None and at < stop_ms and entry.get('type') in ('user', 'assistant'):
            break
        if at is None or at < stop_ms or entry.get('type') != 'user' \
                or prompt_kind(entry) != EVENT:
            continue
        text = REMINDER.sub('', delivered_text(entry) or '')
        tag = EVENT_TAG.match(text)
        named = [i for i, _ in notices(entry, text)] or [tag.group(1) if tag else EVENT]
        ids = [i for i in named if i not in ids] + ids
    return ids


KINDS = {'Agent': 'agent', 'Task': 'agent', 'Workflow': 'agent', 'Bash': 'bash',
         'Monitor': 'monitor', 'ScheduleWakeup': 'wakeup'}
# What a description says at most, so a long command stays one short line.
WHAT_LIMIT = 80


def describe(entries, ids):
    """(id, kind, what) for each pending id, from the tool call that launched it. kind is
    agent, bash, run (a Bash or Monitor command that watches a CI run), monitor, wakeup, or
    work when the launch is not found; what is the call's description or command on one
    line, or empty."""
    calls, launches = {}, {}
    for entry in entries:
        content = (entry.get('message') or {}).get('content')
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get('type') == 'tool_use':
                calls[block.get('id')] = block
            elif block.get('type') == 'tool_result' and isinstance(entry.get('toolUseResult'), dict):
                started = launch(entry['toolUseResult'], None)
                if started:
                    launches[started[0]] = block.get('tool_use_id')
    rows = []
    for ident in ids:
        call = calls.get(launches.get(ident)) or {}
        given = call.get('input') if isinstance(call.get('input'), dict) else {}
        kind = KINDS.get(call.get('name'), 'work')
        said = given.get('description') or given.get('command') or given.get('prompt') or ''
        said = ' '.join(str(said).split())
        if kind in ('bash', 'monitor') and re.search(r'\bgh run watch\b', given.get('command') or ''):
            kind = 'run'
        if len(said) > WHAT_LIMIT:
            said = said[:WHAT_LIMIT - 1].rstrip() + '\u2026'
        rows.append((ident, kind, said))
    return rows


def main(argv):
    flags = [a for a in argv[1:] if a == '--describe']
    argv = [argv[0]] + [a for a in argv[1:] if a != '--describe']
    if len(argv) not in (2, 3) or (len(argv) == 3 and not re.fullmatch(r'[0-9]+', argv[2])):
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    path = argv[1]
    if not os.path.isfile(path):
        return 1
    session = started_ms(int(argv[2])) if len(argv) == 3 else None
    entries = read_transcript(path)
    ids = pending(entries, started_ms=session)
    stop_at = os.environ.get('STOP_AT', '')
    if re.fullmatch(r'[0-9]+', stop_at):
        moved_on = unanswered(entries, int(stop_at) - STOP_SLACK_MS)
        ids += [i for i in moved_on if i not in ids]
    if flags:
        for row in describe(entries, ids):
            print('\t'.join(row))
    else:
        for ident in ids:
            print(ident)
    return 0 if ids else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
