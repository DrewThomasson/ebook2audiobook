#!/usr/bin/env python3
"""Reads the ready line and the review label out of a session's text.

Shared by stop_attention.py, speak-attention.sh and voice_bridge_reply.py, so they agree on
what a ready stop and a label add are. The ready line and the label come from the
extension file: readyLine, with <N> where the number goes, and reviewLabel. Their patterns
are built the first time they are read, after the caller has named the file.
"""
import functools
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_config  # noqa: E402
import transcript  # noqa: E402

# Emphasis a reader would still take the ready line's number through: a `#` before it,
# markdown emphasis around it.
NUMBER = r'[*_`]*#?(\d+)[*_`]*'
# What may stand between the label's words, however a command quotes or encodes its spaces.
LABEL_SPACE = r'(?:\s|%20|\+)+'
# What a label add's output shows when the add went through: the labels the issues endpoint
# answers with, or the /pull/<n> link the edit command prints. Output without either means a
# later command in the line ran after the add failed.
PULL_LINK = r'/pull/[0-9]+'
EDIT_TARGET = re.compile(r'\bgh\s+(?:pr|issue)\s+edit\s+#?(\d+)')
# The issues endpoint the label goes on through. The call adds only when it sends a field;
# without one it reads the labels, and a DELETE takes one off.
ENDPOINT_TARGET = re.compile(r'\bissues/(\d+)/labels\b')
API_FIELD = re.compile(r'(?:^|\s)(?:-f|-F|--field|--raw-field|--input)(?=[\s=])')
API_DELETE = re.compile(r'-X\s*DELETE\b|--method[\s=]+DELETE\b', re.I)


def words(text):
    return r'\s+'.join(re.escape(word) for word in text.split())


def patterns():
    """The patterns the extension file's ready line and label make:

    READY        the ready line in any case, with the emphasis NUMBER allows
    LABEL        the label's words, as a pattern to build on
    READY_LABEL  the label anywhere in a command
    LABEL_ADDED  output that shows a label add went through
    EDIT_ADD     `gh pr edit` or `gh issue edit` adding it, alone or in a comma list,
                 quoted or not; a --remove-label beside it, or one that names it, does not
                 match
    """
    return built(hook_config.file())


@functools.lru_cache(maxsize=4)
def built(_file):
    """patterns() for one extension file, built once."""
    before, _, after = hook_config.value('readyLine').partition('<N>')
    ready = (words(before) + (r'\s+' if before[-1:].isspace() else '') + NUMBER
             + (r'\s+' if after[:1].isspace() else '') + words(after))
    label = LABEL_SPACE.join(re.escape(word) for word in hook_config.value(
        'reviewLabel').split())
    return {
        'READY': re.compile(ready, re.I),
        'LABEL': label,
        'READY_LABEL': re.compile(label, re.I),
        'LABEL_ADDED': re.compile(label + '|' + PULL_LINK, re.I),
        'EDIT_ADD': re.compile(r'--add-label[\s=]+(?:"[^"]*?|\'[^\']*?|[^\s"\']*?)' + label,
                               re.I),
    }


def __getattr__(name):
    """READY, LABEL, READY_LABEL, LABEL_ADDED and EDIT_ADD, read as module names."""
    found = patterns().get(name) if name.isupper() else None
    if found is None:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
    return found


def final_reply(hook, entries):
    """The text of the reply the turn ends on: the hook's own copy together with the
    assistant text in the transcript after the turn's last tool call, so a ready line in
    either one is checked."""
    said = []
    for entry in reversed(entries):
        content = (entry.get('message') or {}).get('content')
        blocks = content if isinstance(content, list) else []
        if transcript.starts_turn(entry) or any(
                isinstance(b, dict) and b.get('type') in ('tool_use', 'tool_result')
                for b in blocks):
            break
        if entry.get('type') == 'assistant':
            said.append(transcript.text_of(content))
    own = hook.get('last_assistant_message')
    return '\n'.join(([own] if isinstance(own, str) else []) + said[::-1])


def ready_numbers(hook, entries):
    """The pull request numbers the turn's final reply names in a ready line, ascending."""
    return sorted(set(patterns()['READY'].findall(final_reply(hook, entries))), key=int)


def labeled_numbers(command):
    """None when a shell command does not add the review label, else the pull request
    numbers it adds it to, which can be none when the command does not say."""
    found = patterns()
    numbers = set()
    adds = False
    if found['EDIT_ADD'].search(command):
        adds = True
        numbers.update(EDIT_TARGET.findall(command))
    if (found['READY_LABEL'].search(command) and ENDPOINT_TARGET.search(command)
            and API_FIELD.search(command) and not API_DELETE.search(command)):
        adds = True
        numbers.update(ENDPOINT_TARGET.findall(command))
    return sorted(numbers, key=int) if adds else None
