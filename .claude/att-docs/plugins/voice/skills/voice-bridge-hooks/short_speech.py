#!/usr/bin/env python3
"""Shortens what speech mode reads aloud, so a long reply is not read out in full.

usage: short_speech.py --config <extension.json> ready   < block as written
       short_speech.py --config <extension.json> brief   < block as spoken

speak-attention.sh asks it for each block it queues, and leaves the block as written to the
transcript and the voice bridge's feed.

`ready` reads a block's Markdown for the ready line and prints the one short line that
says so instead, such as "Pull request 214 is ready for review.", or prints nothing and
exits 1 when the block has no ready line.

`brief` reads a block as the speaker would say it. A block of up to SPOKEN_LIMIT characters
is printed as it is. A longer one is printed as its opening sentence, cut at a word within
OPENING_LIMIT characters when that sentence is itself long, followed by a note that the
rest is on screen. A question the hook composes from a tool call starts with "Question:"
and is always printed whole, since its choices are what the user has to hear.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_config  # noqa: E402

# The most characters of spoken text a block keeps before it is cut down. About a minute of
# speech at the default pace.
SPOKEN_LIMIT = 600
# The most characters of a long block's opening sentence that are read.
OPENING_LIMIT = 300
ON_SCREEN = 'The rest is on screen.'
QUESTION = 'Question:'

# A full stop after one of these does not end a sentence. Neither does one after a bare number:
# it is usually a list marker, and the spoken text has lost the line breaks that set a marker
# apart, so cutting there would read nothing but the marker.
ABBREVIATIONS = {'e.g', 'i.e', 'etc', 'vs', 'mr', 'mrs', 'ms', 'dr', 'st', 'approx'}
SENTENCE_END = re.compile(r'[.!?]+["\')\]]*(?=\s|$)')


def opening_sentence(text):
    """The first sentence of text, ending at its punctuation, or the whole text when no
    sentence ends in it."""
    for end in SENTENCE_END.finditer(text):
        before = text[:end.start()].split()
        token = before[-1].lower().strip('("\'') if before else ''
        if end.group().startswith('.') and (token in ABBREVIATIONS or token.isdigit()):
            continue
        return text[:end.end()]
    return text


def brief(text):
    """text as it is read aloud: whole when short or a question, else its opening sentence
    and a note that the rest is on screen."""
    text = text.strip()
    if len(text) <= SPOKEN_LIMIT or text.startswith(QUESTION):
        return text
    opening = opening_sentence(text)
    if len(opening) > OPENING_LIMIT:
        # Cut at the last word that fits, keeping a word that ends exactly at the limit.
        cut = opening[:OPENING_LIMIT]
        if not opening[OPENING_LIMIT].isspace() and len(cut.split()) > 1:
            cut = cut.rsplit(None, 1)[0]
        opening = (cut.rstrip(',;:-.') or cut) + '.'
    return f'{opening} {ON_SCREEN}'


def say_numbers(numbers):
    """The numbers as a spoken list: "5", "5 and 6", "5, 6 and 7"."""
    if len(numbers) < 2:
        return ''.join(numbers)
    return f'{", ".join(numbers[:-1])} and {numbers[-1]}'


def ready_line(markdown):
    """The line that says the pull requests the block's ready lines name are ready for
    review, or None when it has none. Numbers are listed once, in ascending order."""
    import ready_line as lines  # noqa: E402, built from the extension file named first
    numbers = sorted(set(lines.patterns()['READY'].findall(markdown)), key=int)
    if not numbers:
        return None
    if len(numbers) == 1:
        return f'Pull request {numbers[0]} is ready for review.'
    return f'Pull requests {say_numbers(numbers)} are ready for review.'


def main(argv):
    args = hook_config.take(argv)[1:]
    form = args[0] if args else ''
    if form == 'ready':
        said = ready_line(sys.stdin.read())
        if said is None:
            return 1
        print(said)
        return 0
    if form == 'brief':
        sys.stdout.write(brief(sys.stdin.read()))
        return 0
    print('usage: short_speech.py --config <extension.json> ready|brief', file=sys.stderr)
    return 64


if __name__ == '__main__':
    sys.exit(main(sys.argv))
