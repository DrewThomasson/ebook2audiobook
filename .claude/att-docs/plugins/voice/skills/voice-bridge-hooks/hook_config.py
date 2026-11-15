"""Reads the extension file the voice bridge hook scripts take as `--config`.

The file is JSON. A path in it is relative to the git toplevel of the folder the file sits
in, so the scripts find the consuming repository from the file rather than from where they
are installed. The fields:

  reviewLabel         the label the ready signal adds to a pull request
  reviewAnnouncement  the words spoken after "has pull request <N>" once the label lands
  readyLine           the ready line, with <N> where the pull request number goes
  spokenTerms         words the voice would misread, and how to say them
  fullSpeech          true reads long replies and ready lines aloud in full; absent or false
                      reads them in short
  scriptsDir          the folder that holds the ledger module
  ledgerModule        the module that reads a ledger: read_ledger(path) gives its rows,
                      and STATIC_CHECKS_NAME starts the title of a checks row
  ledgerTool          the script whose commands name a ledger as their first argument
  ledgerSubcommands   the subcommands of ledgerTool that take a ledger
  dispatchTool        the script that names a ledger with a flag
  dispatchLedgerFlag  that flag
  drivers             scripts that keep a ledger in a state folder, each with the index
                      of the argument that names the folder
  driverLedger        the ledger's file name in a driver's state folder

The ledger fields (scriptsDir through driverLedger) are optional: a file without them
makes the scripts treat the session as waiting on no ledger. `defaults.json` beside this
file states the other fields for a repository with no extension file of its own.

A script reads only the fields it needs, when it needs them. Entry points take
`--config <file>` as their first option. A missing option, a missing file, a file that is
not a JSON object, a missing field, or a path field outside a git work tree exits 64.
Importers call use(file) before they call anything that reads a field.
"""
import json
import os
import subprocess
import sys

EXIT_USAGE = 64

_state = {'file': None, 'values': None, 'root': None}


def fail(message):
    print(f'{os.path.basename(sys.argv[0] or "hook")}: {message}', file=sys.stderr)
    sys.exit(EXIT_USAGE)


def use(file):
    """Reads the extension file every later field comes from."""
    if not file:
        fail('--config <extension.json> is required')
    path = os.path.abspath(file)
    try:
        with open(path, encoding='utf-8') as f:
            values = json.load(f)
    except OSError:
        fail(f'no config at {file}')
    except ValueError as error:
        fail(f'{file} does not read as JSON: {error}')
    if not isinstance(values, dict):
        fail(f'{file} does not hold a JSON object')
    _state.update(file=path, values=values, root=None)


def take(argv):
    """argv with a leading `--config <file>` or `--config=<file>` taken off and read. A
    script that needs the file stops with exit 64 when argv has none and no use() came
    first."""
    rest = list(argv[1:])
    if rest and rest[0] == '--config':
        use(rest[1] if len(rest) > 1 else '')
        rest = rest[2:]
    elif rest and rest[0].startswith('--config='):
        use(rest[0].split('=', 1)[1])
        rest = rest[1:]
    elif _state['file'] is None:
        fail('--config <extension.json> is required')
    return [argv[0], *rest]


def file():
    """The extension file in use, for a script that hands it to a process of its own."""
    if _state['file'] is None:
        fail('--config <extension.json> is required')
    return _state['file']


def value(field):
    """A field as the file states it."""
    file()
    found = _state['values'].get(field)
    if found is None or found == '' or found == [] or found == {}:
        fail(f'{_state["file"]} names no {field}')
    return found


def has(field):
    """Whether the file states a field, for one a script can do without."""
    file()
    return _state['values'].get(field) not in (None, '', [], {})


def path(field):
    """A path field, resolved against the repository the file sits in."""
    if _state['root'] is None:
        top = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                             cwd=os.path.dirname(file()), capture_output=True, text=True,
                             check=False)
        if top.returncode != 0 or not top.stdout.strip():
            fail(f'{_state["file"]} is not inside a git work tree')
        _state['root'] = top.stdout.strip()
    return os.path.join(_state['root'], value(field))
