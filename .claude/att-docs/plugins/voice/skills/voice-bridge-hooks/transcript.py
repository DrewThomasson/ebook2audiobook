"""Reads a Claude Code session transcript: the tool calls with their results, and the ledger
paths the session's commands name.

The ledger tools come from the extension file (see hook_config.py): ledgerTool and its
ledgerSubcommands, dispatchTool and its dispatchLedgerFlag, the drivers with their state
folder arguments, and, for blocked(), the ledgerModule in scriptsDir. Each is optional; a
file that names none finds no ledger and blocks on nothing.
"""
import functools
import importlib
import json
import os
import re
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_config  # noqa: E402

# A command that runs the tool, at its start or after a shell separator, not one that only
# mentions it (a grep of the docs, a commit message).
RUNS = r'(?:^|[;&|(\n])\s*(?:\S*/)?'

# A scratchpad script run with bash, whose dispatch lines carry the ledger path themselves.
BASH_SCRIPT = r'bash\s+(?:-\S+\s+)*["\']?([^\s"\']+\.sh)\b'
SCRIPT = re.compile(RUNS + BASH_SCRIPT)


def alternatives(names):
    return '|'.join(re.escape(name) for name in names)


def ledger_patterns():
    """The patterns the extension file's ledger tools make:

    LEDGER_ARG        a ledgerTool subcommand that takes the ledger as its first argument
    LEDGER_FLAG       a dispatchTool command that names it with dispatchLedgerFlag; a quoted
                      word is skipped whole, so a `|` inside a `-f grep='A-1|A-2'` value does
                      not end the command before the flag
    DRIVER            a driver, which writes its own ledger at <state-dir>/<driverLedger> and
                      runs the other tools itself, so the state folder argument is the only
                      place the ledger shows
    DRIVER_STATE_ARG  each driver's state folder argument, counted from 0
    """
    return built(hook_config.file())


@functools.lru_cache(maxsize=4)
def built(_file):
    """ledger_patterns() for one extension file, built once."""
    never = re.compile(r'(?!)')
    drivers = hook_config.value('drivers') if hook_config.has('drivers') else {}
    arg = flag = never
    if hook_config.has('ledgerTool') or hook_config.has('ledgerSubcommands'):
        arg = re.compile(
            re.escape(hook_config.value('ledgerTool')) + r'\s+(?:'
            + alternatives(hook_config.value('ledgerSubcommands')) + r')\s+'
            r'(?:--\S+\s+)*(\S+)')
    if hook_config.has('dispatchTool') or hook_config.has('dispatchLedgerFlag'):
        flag = re.compile(
            re.escape(hook_config.value('dispatchTool'))
            + r'\b(?:[^\n;&|\'"]|\'[^\'\n]*\'|"[^"\n]*")*?'
            + re.escape(hook_config.value('dispatchLedgerFlag')) + r'[= ](\S+)')
    driver = never
    if drivers:
        driver = re.compile(
            r'(?:^|[;&|(\n])\s*(?:\w+=[\w./~:@%+,-]*\s+|(?:nohup|setsid)\s+)*'
            r'(?:bash\s+(?:-\S+\s+)*)?["\']?(?:\S*/)?(' + alternatives(drivers) + r')["\']?'
            r'(?=[\s;&|)]|$)((?:[^\n;&|\'"]|\'[^\'\n]*\'|"[^"\n]*")*)')
    return {'LEDGER_ARG': arg, 'LEDGER_FLAG': flag, 'DRIVER': driver,
            'DRIVER_STATE_ARG': dict(drivers)}


def __getattr__(name):
    """LEDGER_ARG, LEDGER_FLAG, DRIVER and DRIVER_STATE_ARG, read as module names."""
    found = ledger_patterns().get(name) if name.isupper() else None
    if found is None:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
    return found


SHELL_WORD = re.compile(r'(?:[^\s\'"]|\'[^\']*\'|"[^"]*")+')
REDIRECT = re.compile(r'^\d*(?:>>?|<)&?(\S*)$')

ASSIGN = re.compile(r'(?:^|[;&\n])\s*(?:export\s+)?([A-Za-z_]\w*)=([^\s;&|]+)')
VAR = re.compile(r'\$(?:\{(\w+)\}|(\w+))')


def text_of(content):
    """The text of a message or tool result, which is a string or a list of blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(text_of(b) for b in content)
    if isinstance(content, dict):
        return text_of(content.get('text', content.get('content', '')))
    return ''


def read_transcript(path):
    entries = []
    try:
        with open(path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if isinstance(entry, dict) and not entry.get('isSidechain'):
                    entries.append(entry)
    except OSError:
        pass
    return entries


HUMAN = 'human'
EVENT = 'event'
# Events the app delivers as plain prompts, with no origin on the row.
EVENT_TAG = re.compile(
    r'^\s*<(ci-monitor-event|side-sessions-event|task-notification|agent-message)\b')
# The app's notices, which open many origin-less rows. Text after them is classed on its own.
REMINDER = re.compile(r'\s*<system-reminder>.*?</system-reminder>', re.S)
# A notice that carries on the user's own request: a session resumed after the app quit, or a
# forked one.
CONTINUATION = re.compile(r'app was quit while you were working|forked from another session')
# A local slash command and its output, and the marker an interrupt leaves, none of which the
# session answers.
LOCAL_COMMAND = re.compile(
    r'^\s*(<(command-name|command-message|local-command-\w+)>|\[Request interrupted by user)')


def prompt_kind(entry):
    """HUMAN or EVENT for a row that starts a turn or joins one mid-turn, else None.

    A user row starts a turn and a queued_command attachment joins one. The origin says who
    sent it when the row has one; an event the app writes without one opens with its tag, and
    a row of nothing but the app's notices is an event unless one resumes the user's request.
    A compact summary carries the turn on rather than starting one, and a local slash command
    is not sent to the session, so both are None here.
    """
    if entry.get('type') == 'attachment':
        attachment = entry.get('attachment')
        if not isinstance(attachment, dict) or attachment.get('type') != 'queued_command':
            return None
        origin, text = attachment.get('origin'), text_of(attachment.get('prompt'))
    elif entry.get('type') == 'user':
        if entry.get('isMeta') or entry.get('isCompactSummary'):
            return None
        content = (entry.get('message') or {}).get('content')
        if isinstance(content, list) and any(
                isinstance(b, dict) and b.get('type') == 'tool_result' for b in content):
            return None
        origin, text = entry.get('origin'), text_of(content)
    else:
        return None
    if isinstance(origin, dict):
        return HUMAN if origin.get('kind') == HUMAN else EVENT
    rest = REMINDER.sub('', text)
    if not rest.strip() and REMINDER.match(text):
        return HUMAN if CONTINUATION.search(text) else EVENT
    if LOCAL_COMMAND.match(rest):
        return None
    return EVENT if EVENT_TAG.match(rest) else HUMAN


def starts_turn(entry):
    """Whether a user row opens a turn: a prompt from the user or an automated event, or a
    compact summary, which opens the rest of a turn after a compaction."""
    if entry.get('type') != 'user' or entry.get('isMeta'):
        return False
    return bool(entry.get('isCompactSummary')) or prompt_kind(entry) is not None


class Call:
    def __init__(self, pos, name, args):
        self.pos = pos
        self.name = name
        self.args = args if isinstance(args, dict) else {}
        self.result = ''
        self.error = False
        self.answered = False

    @property
    def command(self):
        return str(self.args.get('command') or '')


def read_session(entries):
    """The tool calls in order with their results, and the calls by tool use id."""
    calls, by_id = [], {}
    for pos, entry in enumerate(entries):
        content = (entry.get('message') or {}).get('content')
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get('type') == 'tool_use':
                call = Call(pos, block.get('name', ''), block.get('input'))
                calls.append(call)
                by_id[block.get('id')] = call
            elif block.get('type') == 'tool_result' and block.get('tool_use_id') in by_id:
                call = by_id[block['tool_use_id']]
                call.result = text_of(block.get('content'))
                call.error = bool(block.get('is_error'))
                call.answered = True
    return calls, by_id


def expand(word, command):
    """A ledger argument with ~ and the command's own VAR=value assignments filled in."""
    names = {m.group(1): m.group(2) for m in ASSIGN.finditer(command)}
    for _ in range(3):
        word = VAR.sub(lambda m: names.get(m.group(1) or m.group(2), m.group(0)), word)
    try:
        word = shlex.split(word)[0]
    except (ValueError, IndexError):
        pass
    return os.path.expanduser(word)


def script_text(path):
    """The lines of a script a command runs with bash, comments dropped so the prose in them
    (`one <ledger tool> wait watches it`) names no ledger, or '' when it cannot be read."""
    try:
        with open(path) as f:
            return ''.join(line for line in f if not line.lstrip().startswith('#'))
    except OSError:
        return ''


def positional(args):
    """The words of an argument string that are not redirections or their targets."""
    words, skip = [], False
    for word in SHELL_WORD.findall(args):
        if skip:
            skip = False
            continue
        redirect = REDIRECT.match(word)
        if redirect:
            skip = not redirect.group(1)
            continue
        words.append(word)
    return words


def ledger_paths(text, command):
    """The ledger arguments in text, expanded with the assignments anywhere in command."""
    found = ledger_patterns()
    for pattern in (found['LEDGER_ARG'], found['LEDGER_FLAG']):
        for m in pattern.finditer(text):
            yield expand(m.group(1), command)
    for m in found['DRIVER'].finditer(text):
        words = positional(m.group(2))
        index = found['DRIVER_STATE_ARG'][m.group(1)]
        state = expand(words[index], command).rstrip('/') if len(words) > index else ''
        if state:
            yield os.path.join(state, hook_config.value('driverLedger'))


def call_ledgers(call, cwd=''):
    """The ledger arguments one Bash call and the scripts it runs name, a relative script
    path opened against cwd, the directory the call ran in, when one is given."""
    if call.name != 'Bash':
        return
    yield from ledger_paths(call.command, call.command)
    for m in SCRIPT.finditer(call.command):
        # A script sees the variables its caller set as well as its own.
        text = script_text(os.path.join(cwd, expand(m.group(1), call.command)))
        yield from ledger_paths(text, call.command + '\n' + text)


def ledger_args(calls):
    """Every ledger argument the session's commands and scripts name, expanded as far as the
    command allows."""
    for call in calls:
        yield from call_ledgers(call)


def ledgers(calls):
    found = []
    for path in ledger_args(calls):
        if '$' not in path and path not in found:
            found.append(path)
    return found


def ledger_module():
    """The extension file's ledgerModule, imported from its scriptsDir."""
    folder = hook_config.path('scriptsDir')
    if folder not in sys.path:
        sys.path.insert(0, folder)
    return importlib.import_module(hook_config.value('ledgerModule'))


# A pull request URL a `gh pr create` call prints.
CREATED_PULL = re.compile(r'/pull/(\d+)\b')
def blocked(entries):
    """What the session waits on, from the rows still open in the ledgers its commands name:
    {'ledgers': [...], 'issues': [...], 'pulls': [...]}. A relative ledger path is resolved
    against the working directory of the call that named it, or the latest one before it when
    the call's row names none. An issue row is an issue the
    session waits on. A pull request row is another session's pull request it waits to merge,
    unless it is the session's own: one a `gh pr create` call of the session opened, one its
    ledger holds a checks row for, which the ledger tool records only for a pull request the
    session pushes to, or one from a branch the session was on."""
    if not hook_config.has('ledgerModule'):
        return {'ledgers': [], 'issues': [], 'pulls': []}
    ledger = ledger_module()
    # The title the ledger module gives the checks row of a pull request.
    checks_title = re.compile(rf'^{re.escape(ledger.STATIC_CHECKS_NAME)} on pull request (\d+)$')
    calls, _ = read_session(entries)
    # The working directory each entry ran in: its own, else the latest one before it.
    cwds, cwd = [], ''
    for entry in entries:
        cwd = str(entry.get('cwd') or cwd)
        cwds.append(cwd)
    found = []
    for call in calls:
        cwd = cwds[call.pos]
        for path in call_ledgers(call, cwd):
            path = os.path.normpath(os.path.join(cwd, path)) if cwd else path
            if '$' not in path and path not in found:
                found.append(path)
    own = {m.group(1) for call in calls if call.name == 'Bash'
           and 'gh pr create' in call.command for m in CREATED_PULL.finditer(call.result)}
    branches = {str(entry.get('gitBranch')) for entry in entries if entry.get('gitBranch')}
    issues, pulls = set(), set()
    for path in found:
        rows = ledger.read_ledger(path)
        checked = own | {m.group(1) for m in (checks_title.match(r['title']) for r in rows) if m}
        for row in rows:
            kind, _, number = row['run'].partition(':')
            if row['state'] == 'done' or not number.isdigit():
                continue
            if kind == 'issue':
                issues.add(int(number))
            elif kind == 'pr' and row['branch'] and number not in checked \
                    and row['branch'] not in branches:
                pulls.add(int(number))
    return {'ledgers': found, 'issues': sorted(issues), 'pulls': sorted(pulls)}


def main(argv):
    """usage: transcript.py --config <extension.json> blocked <transcript.jsonl>
    Prints what blocked() reads from the transcript's main thread, as JSON.
    """
    argv = hook_config.take(argv)
    if len(argv) != 3 or argv[1] != 'blocked':
        print(main.__doc__.strip().splitlines()[0], file=sys.stderr)
        return 2
    print(json.dumps(blocked(read_transcript(argv[2]))))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
