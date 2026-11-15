#!/usr/bin/env python3
"""Prints the reply text of the current turn that speech mode has not read aloud yet.

usage: speak_pending.py <transcript.jsonl> <cursor> [stop [reply] | seen]

speak-attention.sh asks it before each tool call and at Stop, so text written ahead of a
tool call is read when the call starts, rather than with the rest of the reply at the end
of the turn. A turn starts at the latest prompt row, from the user or from an event, and
its text is every assistant text block written after it, in order. The transcript holds a
text block before the tool call that follows it, so the hook that runs ahead of that call
finds it there.

A question that waits on the user is read too, as "Question:", the question, and its
choices. An AskUserQuestion call's questions take their place among the blocks, so the
hook ahead of that call reads them after the text written before it. The wrap-up box shows
its question after the closing reply, so Stop reads that question last, with the box's
button labels. A question written into the reply is read as the reply.

The cursor file holds which turn was read, how many of its blocks were, and whether a Stop
has run since. Output is NUL-separated: a first field of 1 when what follows opens a new
stretch of speech and wants the session's name ahead of it, else 0, then one field per
block. Nothing at all is printed when there is nothing new.

The app writes transcript rows in batches, so at Stop the final reply can still be on its
way. The final reply is on disk once the turn's last row is an assistant text row, so Stop waits
up to STOP_WAIT seconds (default 15) for that, then adds the reply the hook payload carries
when it never landed. A Stop marks the cursor, so the next block read, a later turn's or a
test's, opens with the name again.

Given seen, the turn's text so far is marked read and nothing is printed: speech mode
turning on reads what is written from then on.
"""
import json
import os
import sys
import time


def blocks(content):
    """The text blocks of an assistant message, which is a string or a list of blocks."""
    if isinstance(content, str):
        return [content]
    if isinstance(content, list):
        return [b.get('text', '') for b in content
                if isinstance(b, dict) and b.get('type') == 'text']
    return []


ASK = 'AskUserQuestion'
WRAP_UP = 'mcp__ccd_turn__wrap_up'


def spoken_question(question, choices, many=False):
    """A question as the voice reads it: a lead-in, the question, then its choices, joined
    by "and" when several can be picked, else by "or"."""
    said = f'Question: {question.strip()}'
    if said[-1] not in '.?!':
        said += '?'
    names = [c.strip() for c in choices if c and c.strip()]
    if len(names) > 1:
        names[-1] = f'{"and" if many else "or"} {names[-1]}'
    if names:
        lead = 'Pick any of' if many else 'Options'
        said += f' {lead}: {", ".join(names) if len(names) > 2 else " ".join(names)}.'
    return said


def questions(content):
    """What the turn's tool calls ask: each AskUserQuestion question in place, and the
    wrap-up box's question apart, since the box shows after the closing reply. The box is
    None when the content makes no wrap-up call, and an empty list for one with no ask."""
    asked, boxed = [], None
    for block in content if isinstance(content, list) else []:
        if not isinstance(block, dict) or block.get('type') != 'tool_use':
            continue
        given = block.get('input') or {}
        if block.get('name') == ASK:
            for q in given.get('questions') or []:
                if isinstance(q, dict) and str(q.get('question') or '').strip():
                    labels = [str(o.get('label') or '') for o in q.get('options') or []
                              if isinstance(o, dict)]
                    asked.append(spoken_question(str(q['question']), labels,
                                                 bool(q.get('multiSelect'))))
        elif block.get('name') == WRAP_UP:
            boxed = []
            if str(given.get('ask') or '').strip():
                # An app action's button shows the app's own label, so its name stands in.
                labels = [str(a.get('label') or a.get('action') or '').replace('_', ' ')
                          for a in given.get('actions') or [] if isinstance(a, dict)]
                boxed = [spoken_question(str(given['ask']), labels)]
    return asked, boxed


def parsed(line):
    try:
        row = json.loads(line)
    except ValueError:
        return None
    return row if isinstance(row, dict) and not row.get('isSidechain') else None


def is_prompt(row):
    """A prompt row's content is a string; a tool result's is a list of blocks."""
    content = (row.get('message') or {}).get('content')
    return row.get('type') == 'user' and isinstance(content, str)


def turn(path):
    """The current turn's key, its text blocks and questions in order, the last wrap-up
    call's question with that call's line number, and whether the turn's last row is the
    assistant's text. Only the last wrap-up call counts, since its box is the one shown.

    The turn's prompt row is found from the end, testing only the lines that can be one,
    so a long session's transcript is not parsed whole on every tool call.
    """
    try:
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()
    except OSError:
        lines = []
    start, key = 0, None
    for number in range(len(lines) - 1, -1, -1):
        if '"user"' not in lines[number]:
            continue
        row = parsed(lines[number])
        if row and is_prompt(row):
            # A row without a uuid is keyed by its line, since two prompts can carry the
            # same text.
            start, key = number + 1, row.get('uuid') or f'line-{number}'
            break
    texts, box, answered = [], (0, []), False
    for number, line in enumerate(lines[start:], start + 1):
        row = parsed(line)
        if not row or row.get('type') not in ('user', 'assistant'):
            continue
        # A thinking or tool_use row is not the reply, so only a text row answers.
        said, asked = [], []
        if row['type'] == 'assistant':
            content = (row.get('message') or {}).get('content')
            said = [t for t in blocks(content) if t.strip()]
            asked, boxed = questions(content)
            if boxed is not None:
                box = (number, boxed)
        answered = bool(said)
        texts += said + asked
    return key, texts, box, answered


def read_cursor(path):
    try:
        with open(path, encoding='utf-8') as f:
            key, count, stopped, *heard = f.read().split()
        return key, int(count), stopped == '1', int(heard[0]) if heard else 0
    except (OSError, ValueError):
        return '', 0, True, 0


def main(argv):
    transcript, cursor = argv[1], argv[2]
    mode = argv[3] if len(argv) > 3 else ''
    key, texts, box, answered = turn(transcript)
    if mode == 'stop':
        deadline = time.monotonic() + float(os.environ.get('STOP_WAIT', '15'))
        while not answered and time.monotonic() < deadline:
            time.sleep(0.5)
            key, texts, box, answered = turn(transcript)
        if not answered and len(argv) > 4 and argv[4].strip():
            texts.append(argv[4])
    if key is None:
        # No prompt row to key the turn on: the transcript is gone from this path or
        # empty, as when a session moves it into a worktree's folder while a hook still
        # holds the old path. The cursor stays, so the next hook on the new path reads
        # only the blocks not yet read. A Stop still speaks its closing message.
        if mode == 'stop' and texts:
            sys.stdout.write('\0'.join(['1'] + texts))
        return
    was, count, stopped, heard = read_cursor(cursor)
    if was != key:
        count, stopped, heard = 0, True, 0
    new = [] if mode == 'seen' else texts[count:]
    # The box's question stays out of the block count, so a turn that goes on after a
    # refused Stop still reads the blocks written next. The cursor keeps the line of the
    # wrap-up call whose question was read, so it is read once.
    at, boxed = box
    if mode == 'seen':
        heard = at
    elif mode == 'stop' and at != heard:
        new, heard = new + boxed, at
    with open(cursor, 'w', encoding='utf-8') as f:
        mark = 1 if mode == 'stop' or (stopped and not new) else 0
        f.write(f'{key} {max(count, len(texts))} {mark} {heard}')
    if new:
        sys.stdout.write('\0'.join(['1' if stopped or count == 0 else '0'] + new))


if __name__ == '__main__':
    main(sys.argv)
