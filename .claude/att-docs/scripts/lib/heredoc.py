"""Heredoc reading for the PreToolUse guards.

The guards read a Bash command as text before it runs. A heredoc body is text
the command takes in rather than more commands, so a guard reads the body
apart from the command lines around it. guard-main-checkout.sh runs this file
to print a command with its bodies taken out:

    python3 scripts/lib/heredoc.py <<<"$cmd"
"""

import sys


class Unreadable(Exception):
    pass


def opens_heredoc(text, at):
    # Tells whether a heredoc redirection opens at text[at], as against a
    # here-string, which carries its text on the same line.
    return (text[at:at + 2] == "<<" and text[at + 2:at + 3] != "<"
            and text[at - 1:at] != "<")


def heredoc(text, at):
    # Reads the heredoc redirection opening at text[at]. Returns its delimiter,
    # whether the body drops leading tabs, whether any of the delimiter was
    # quoted, which keeps the body from being expanded, and the index past it.
    at += 2
    strip = text[at:at + 1] == "-"
    at += strip
    while text[at:at + 1] in (" ", "\t"):
        at += 1
    delimiter, quoted, quote = "", False, ""
    while at < len(text):
        char = text[at]
        if quote:
            if char == quote:
                quote = ""
            else:
                delimiter += char
        elif char in "\"'":
            quote, quoted = char, True
        elif char == "\\":
            quoted = True
            delimiter += text[at + 1:at + 2]
            at += 1
        elif char in " \t\n;&|()<>":
            break
        else:
            delimiter += char
        at += 1
    if quote or not delimiter:
        raise Unreadable()
    return delimiter, strip, quoted, at


def bodies(text, at, pending):
    # Reads the heredoc bodies that follow the newline at text[at], one for each
    # (delimiter, strip) pair in the order the redirections opened. Returns the
    # bodies and the index past the last one. A body the text ends inside runs
    # to the end, as the shell reads it.
    found = []
    at += 1
    for delimiter, strip in pending:
        lines = []
        while at < len(text):
            end = text.find("\n", at)
            end = len(text) if end < 0 else end
            line, at = text[at:end], end + 1
            if (line.lstrip("\t") if strip else line) == delimiter:
                break
            lines.append(line)
        found.append("\n".join(lines))
    return found, min(at, len(text))


def command_lines(text):
    # Returns text with each heredoc body and its delimiter line taken out.
    # Quotes, comments, substitutions and arithmetic are followed, so a `<<`
    # inside a string or a shift opens no heredoc. A redirection with no
    # readable delimiter is left in place, body and all.
    kept, pending, stack, at, start = [], [], [""], 0, 0
    while at < len(text):
        char, top, pair = text[at], stack[-1], text[at:at + 2]
        if top == "'":
            if char == "'":
                stack.pop()
        elif char == "\\":
            at += 1
        elif top == "\"":
            if char == "\"":
                stack.pop()
            elif text.startswith("$((", at):
                stack.append("((")
                at += 2
            elif pair == "$(":
                stack.append("$(")
                at += 1
            elif char == "`":
                stack.append("`")
        elif top in ("((", "a("):
            if top == "((" and pair == "))":
                stack.pop()
                at += 1
            elif char == "(":
                stack.append("a(")
            elif char == ")" and top == "a(":
                stack.pop()
        elif char in "\"'":
            stack.append(char)
        elif char == "`":
            if top == "`":
                stack.pop()
            else:
                stack.append("`")
        elif text.startswith("$((", at) or pair == "((":
            stack.append("((")
            at += 2 if char == "$" else 1
        elif pair == "$(" or char == "(":
            stack.append("$(")
            at += 1 if char == "$" else 0
        elif char == ")" and top == "$(":
            stack.pop()
        elif char == "#" and text[at - 1:at] in ("", " ", "\t", "\n", ";", "&", "|", "("):
            end = text.find("\n", at)
            at = len(text) if end < 0 else end
            continue
        elif opens_heredoc(text, at):
            try:
                delimiter, strip, _, end = heredoc(text, at)
            except Unreadable:
                at += 2
                continue
            pending.append((delimiter, strip))
            at = end
            continue
        elif char == "\n" and pending:
            kept.append(text[start:at + 1])
            at = bodies(text, at, pending)[1]
            start, pending = at, []
            continue
        at += 1
    kept.append(text[start:])
    return "".join(kept)


if __name__ == "__main__":
    sys.stdout.write(command_lines(sys.stdin.read()))
