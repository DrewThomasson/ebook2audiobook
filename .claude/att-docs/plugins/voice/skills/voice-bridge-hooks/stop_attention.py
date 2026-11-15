#!/usr/bin/env python3
"""Says what a session that just stopped needs from the user, if anything.

usage: stop_attention.py --config <extension.json> < <Stop hook payload>

Prints the words speak-attention.sh speaks after "<title> session" and exits 0, or prints
nothing and exits 3 when the stop needs no announcement. Any other exit is a failure, and the
caller still speaks. It reads the turn that just ended, from the last row that started one: a
user prompt, or an automated event such as a task notification, a pull request monitor's
report, or another session's message.

- The turn added the review label the extension file names. The label's own announcement
  names the pull request, so the stop stays quiet.
- The turn leaves the user something to answer: the wrap-up box carries a question, or the
  reply's last line ends in a question mark. Prints "is waiting for you".
- The user started the turn, or sent a message during it, and nothing is left to answer.
  Prints "finished", since the user asked for the work and may have stepped away.
- An automated event started the turn and nothing is left to answer. Quiet: the session
  reported on its own work. An announcement an earlier stop held back for background work is
  owed by speak-attention.sh, not read from here.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_config  # noqa: E402
import ready_line  # noqa: E402
from transcript import HUMAN, prompt_kind, read_transcript, starts_turn, text_of  # noqa: E402

QUIET = 3
WRAP_UP = 'mcp__ccd_turn__wrap_up'
# Markdown and closing punctuation that can follow a question's mark on the last line.
TRAILING = re.compile(r'[\s*_`)\]"\']+$')


def message_content(entry):
    message = entry.get('message')
    return message.get('content') if isinstance(message, dict) else None


def tool_uses(entry):
    """The tool_use blocks of an assistant row."""
    content = message_content(entry) if entry.get('type') == 'assistant' else None
    if not isinstance(content, list):
        return []
    return [b for b in content if isinstance(b, dict) and b.get('type') == 'tool_use']


def stdout_of(entry, block):
    """The standard output of a Bash result, which the label announcement reads, or the
    result's whole text when the row does not carry it apart from standard error."""
    result = entry.get('toolUseResult')
    if isinstance(result, dict) and isinstance(result.get('stdout'), str):
        return result['stdout']
    return text_of(block.get('content'))


def labeled(rows):
    """Whether a Bash command in the rows added the review label, by the same output check
    speak-attention.sh makes before it announces the pull request."""
    adds = {use.get('id') for entry in rows for use in tool_uses(entry)
            if use.get('name') == 'Bash' and ready_line.labeled_numbers(
                str((use.get('input') or {}).get('command') or '')) is not None}
    for entry in rows:
        content = message_content(entry) if entry.get('type') == 'user' else None
        for block in content if isinstance(content, list) else []:
            if (isinstance(block, dict) and block.get('type') == 'tool_result'
                    and block.get('tool_use_id') in adds and not block.get('is_error')
                    and ready_line.LABEL_ADDED.search(stdout_of(entry, block))):
                return True
    return False


def asked(rows):
    """Whether the rows leave a question in the wrap-up box."""
    return any(use.get('name') == WRAP_UP and (use.get('input') or {}).get('ask')
               for entry in rows for use in tool_uses(entry))


# `session_title.py status "<status>"` in a Bash command, however the script is reached.
STATUS_COMMAND = re.compile(r"""session_title\.py\s+status\s+(?:--\s+)?(["'])(.*?)\1""")


def status_commands(rows):
    """The statuses the rows' Bash commands set with session_title.py, in order, leaving out
    a command that failed."""
    sets = [(use.get('id'), found.group(2).strip())
            for entry in rows for use in tool_uses(entry) if use.get('name') == 'Bash'
            for found in STATUS_COMMAND.finditer(
                str((use.get('input') or {}).get('command') or ''))]
    failed = set()
    for entry in rows:
        content = message_content(entry) if entry.get('type') == 'user' else None
        for block in content if isinstance(content, list) else []:
            if (isinstance(block, dict) and block.get('type') == 'tool_result'
                    and block.get('is_error')):
                failed.add(block.get('tool_use_id'))
    return [status for ident, status in sets if ident not in failed]


def ends_in_question(reply):
    lines = [line for line in (reply or '').splitlines() if line.strip()]
    return bool(lines) and TRAILING.sub('', lines[-1]).endswith('?')


def last_turn(entries):
    """The rows of the turn that just ended, from the row that started it."""
    for index in range(len(entries) - 1, -1, -1):
        if starts_turn(entries[index]) and not entries[index].get('isCompactSummary'):
            return entries[index:]
    return entries


def announcement(payload, entries):
    """The words to speak for this stop, or None to stay quiet."""
    turn = last_turn(entries)
    if labeled(turn):
        return None
    if asked(turn) or ends_in_question(payload.get('last_assistant_message')):
        return 'is waiting for you'
    if any(prompt_kind(entry) == HUMAN for entry in turn):
        return 'finished'
    return None


def main():
    hook_config.take(sys.argv)
    payload = json.load(sys.stdin)
    path = payload.get('transcript_path') or ''
    entries = read_transcript(path) if os.path.isfile(path) else []
    words = announcement(payload, entries)
    if words is None:
        return QUIET
    print(words)
    return 0


if __name__ == '__main__':
    sys.exit(main())
