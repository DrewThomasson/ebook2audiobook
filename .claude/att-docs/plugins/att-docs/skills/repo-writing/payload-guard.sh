#!/usr/bin/env bash
# PreToolUse guard for text crossing to the work tracker. A shell command that
# sends an op through the tunnel (the tunnel script, or a direct dispatch of its
# workflow) is let through only when the op reads, or when its payload carries
# a stamp from the stamp command and still passes the terms file. A stamp call
# on the same payload earlier in the same command counts as a stamp once the
# guard has run the repository text scan over that payload itself.
# The parser splits the command the way the shell does, reads past the commands
# that run another one (timeout, nice, env, stdbuf, time, nohup, exec, command,
# source, bash -c, eval), and reads the body of every command substitution. A
# command that names the tunnel but yields no call the parser can read is
# blocked, and so is anything it cannot parse. A heredoc body is read as the
# text its command takes in, not as commands, through the hook library's
# heredoc.py: only the substitutions in an unquoted body are parsed, a write op
# fed a heredoc is blocked, and so is a body holding the script, a dispatches
# URL, or a gh line naming the tunnel or an op, whatever command reads it.
# Only the command text is read, so a call made inside a script run by path
# goes unseen.
#
#   payload-guard.sh --config <file>    with the hook payload on stdin
#
# Reads from the config, beside what check-repo-text.sh reads, under
# payloadGuard. readOps and hookLib are relative to the config's toplevel;
# stampDir and lintCommand to the top of the work tree the command runs in:
#   workSide      the tracker's name, as the messages print it
#   tunnel        the tunnel script; a command is matched on its file name
#   workflowName  a word the tunnel workflow's name carries
#   stampCommand  the stamp entry point, matched on its file name
#   stampDir      where the stamps are, and stampDirEnv the environment
#                 variable that names another folder for them
#   readOps       a script defining is_read_op, the ops that only read
#   hookLib       the folder holding hook-tool.sh and heredoc.py
#   lintOp        the op that sends the tree, which lintCommand run with
#                 -c lintConfig over the tree has to pass too
# Wire it up as a PreToolUse hook. Exit 2 blocks the tool call and returns
# stderr to the model. A config that does not load exits 64, which a hook
# runner reports without blocking, so a broken config does not stop every
# shell command in the session.

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=config.sh
. "$HERE/config.sh"
config_open payload-guard "$@" || exit 64
config=$CONFIG_FILE
config_read payloadGuard.workSide payloadGuard.tunnel payloadGuard.workflowName \
  payloadGuard.stampCommand payloadGuard.stampDir payloadGuard.stampDirEnv \
  payloadGuard.readOps payloadGuard.hookLib payloadGuard.lintOp \
  payloadGuard.lintCommand payloadGuard.lintConfig
if [ "${#CONFIG_VALUES[@]}" -ne 11 ]; then
  echo "payload-guard: the config does not read" >&2
  exit 64
fi
work_side="${CONFIG_VALUES[0]}"
tunnel_script="${CONFIG_VALUES[1]}"
workflow_name="${CONFIG_VALUES[2]}"
stamp_command="${CONFIG_VALUES[3]}"
stamp_dir="${CONFIG_VALUES[4]}"
stamp_env="${CONFIG_VALUES[5]}"
read_ops="$CONFIG_ROOT/${CONFIG_VALUES[6]}"
hook_lib="$CONFIG_ROOT/${CONFIG_VALUES[7]}"
lint_op="${CONFIG_VALUES[8]}"
lint_command="${CONFIG_VALUES[9]}"
lint_config="${CONFIG_VALUES[10]}"
if [ -z "$tunnel_script" ] || [ -z "$workflow_name" ] || [ -z "$stamp_command" ]; then
  echo "payload-guard: the config needs payloadGuard tunnel, workflowName and stampCommand" >&2
  exit 64
fi
# shellcheck source=/dev/null
. "$read_ops" || exit 64
# shellcheck source=/dev/null
. "$hook_lib/hook-tool.sh" || exit 64

input=$(cat)
# Bash and the MCP tools that run a shell command or feed one to a running
# process, any of which can reach the tunnel. A terminal tab opened in another
# directory reads its payload files from there.
hook_tool "$input"
[ "$HOOK_KIND" = shell ] || exit 0
cmd="$HOOK_CMD"
cwd="$HOOK_CWD"
grep -qiE -- "$workflow_name|op=|dispatches|workflow" <<<"$cmd" || exit 0

deny() {
  echo "Blocked: $1" >&2
  echo "Text that crosses to $work_side goes through the repo-writing skill first." >&2
  echo "Run its prose pass, then $stamp_command" >&2
  echo "on the exact payload, and send that payload unchanged." >&2
  exit 2
}

# Prints one JSON object per tunnel call in the command: the op, the payload
# argument, whether that argument names a file, the directory it is read from,
# and whether a stamp call earlier in the command covers it. A command it has
# to refuse prints an object whose refuse field says why. Exits 3 when the
# command does not parse.
PARSER='
import json, re, shlex, sys

sys.path.insert(0, sys.argv[1])
from heredoc import Unreadable, bodies, heredoc, opens_heredoc

# The tunnel script and the stamp command as the config names them, each
# matched on its file name, and the word the tunnel workflow name carries.
TUNNEL_PATH, WORKFLOW = sys.argv[2], sys.argv[3].lower()
TUNNEL = TUNNEL_PATH.rsplit("/", 1)[-1]
STAMP = sys.argv[4].rsplit("/", 1)[-1]
MOVES = {"cd", "pushd", "popd"}
# A word that is the tunnel script, or that holds a command line running it.
NAMES_SCRIPT = re.compile(re.escape(TUNNEL) + r"(\s|$)")
DISPATCH_URL = re.compile(r"workflows/([^/\s]+)/dispatches")
ASSIGNMENT = re.compile(r"^[A-Za-z_]\w*\+?=")
REDIRECT = re.compile(r"^(\d+|&)?(<<<|<<-|<<|<>|<&|>&|>>|>\||<|>)(.*)$")
INPUT = re.compile(r"^inputs\[(\w+)\]$")
# Words that open a command without being one.
KEYWORDS = {"!", "{", "if", "then", "else", "elif", "do", "while", "until"}
# Commands that run the command after their own options, with the short and
# long options that take a value and the number of words between those options
# and the command.
PREFIXES = {
    ".": ("", (), 0),
    "command": ("", (), 0),
    "env": ("CSau", ("argv0", "chdir", "split-string", "unset"), 0),
    "exec": ("a", (), 0),
    "nice": ("n", ("adjustment",), 0),
    "nohup": ("", (), 0),
    "source": ("", (), 0),
    "stdbuf": ("eio", ("error", "input", "output"), 0),
    "time": ("fo", ("format", "output"), 0),
    "timeout": ("ks", ("kill-after", "signal"), 1),
}
SHELLS = {"bash", "sh"}
# Commands that take the tunnel script as a file or as text and never run it.
FILE_COMMANDS = {
    "[", "[[", "basename", "cat", "chmod", "cmp", "cp", "diff", "dirname", "echo", "file",
    "grep", "head", "less", "ls", "mv", "printf", "readlink", "realpath", "rm", "sed",
    "sha256sum", "shellcheck", "stat", "tail", "test", "touch", "type", "wc", "which",
}
GIT_FILE_COMMANDS = {
    "add", "blame", "checkout", "commit", "diff", "grep", "log", "ls-files", "mv", "restore",
    "rm", "show", "status",
}
FIND_RUNS = {"-exec", "-execdir", "-ok", "-okdir"}
FIELD_FLAGS = ("-f", "-F", "--field", "--raw-field")
VALUE_FLAGS = {
    "-H", "-R", "-X", "-p", "-q", "-r", "-t", "--cache", "--header", "--hostname", "--jq",
    "--method", "--preview", "--ref", "--repo", "--template",
}
UNPARSED = ("no tunnel call can be read from: {}. Run "
            + TUNNEL_PATH.replace("{", "{{").replace("}", "}}") + " as the "
            "command, on its own or after timeout, nice, env, stdbuf, time, nohup, exec, "
            "command, bash -c, or eval.")
UNREAD = ("this dispatch takes its inputs from stdin or a file, which the guard cannot "
          "read: {}. Pass each input with -f or -F.")
# A heredoc body is text its command reads, so split() keeps it out of the
# words and leaves a marker word holding its place in HEREDOCS.
HEREDOCS = []
MARKER = "\x00heredoc:"
# A gh line that reaches the tunnel workflow, as against one that only
# mentions gh in prose.
GH_TUNNEL = re.compile(r"(^|[^\w-])gh\s.*(" + re.escape(WORKFLOW) + r"|op=)", re.I)
# The script named anywhere in a body, quoted or not, since a body can reach
# it through any language.
BODY_SCRIPT = re.compile(re.escape(TUNNEL) + r"\b")
STDIN_CALL = ("this tunnel call reads a heredoc, which the guard cannot check: {}. "
              "Pass the payload as a file with --payload.")
IN_BODY = ("this heredoc carries a tunnel call, which the guard cannot check inside a "
           "body, whatever reads it: {}. Run the call as its own command, stamped, or "
           "write text that names the tunnel to a file with the Write tool.")


def names_tunnel(body):
    # Tells whether a heredoc body holds what could be a tunnel call: the
    # script, a dispatches URL, or a gh command naming the tunnel or an op.
    # Continued lines are joined first, as the shell joins them.
    for line in body.replace("\\\n", " ").splitlines():
        if BODY_SCRIPT.search(line) or DISPATCH_URL.search(line):
            return True
        if GH_TUNNEL.search(line):
            return True
    return False


def expansions(body, depth):
    # Returns the commands in the substitutions of a heredoc body whose
    # delimiter was not quoted, since the shell runs those as it reads the body.
    found, at = [], 0
    while at < len(body):
        if body[at] == "\\":
            at += 2
        elif body[at:at + 2] == "$(" or body[at] == "`":
            inner, at = substitution(body, at)
            found += split(inner, depth + 1)
        else:
            at += 1
    return found


def substitution(text, at):
    # Returns the body of the command substitution opening at text[at], and the
    # index just past its end.
    if text[at] == "`":
        end = at + 1
        while end < len(text) and text[end] != "`":
            end += 2 if text[end] == "\\" else 1
        if end >= len(text):
            raise Unreadable()
        return text[at + 1:end], end + 1
    depth, end, quote, pending = 1, at + 2, "", []
    arithmetic = text[at + 2:at + 3] == "("
    while end < len(text):
        char = text[end]
        if char == "\\" and quote != "\x27":
            end += 1
        elif quote:
            quote = "" if char == quote else quote
        elif char in "\"\x27":
            quote = char
        elif opens_heredoc(text, end) and not arithmetic:
            delimiter, strip, _, end = heredoc(text, end)
            pending.append((delimiter, strip))
            continue
        elif char == "\n" and pending:
            end = bodies(text, end, pending)[1]
            pending = []
            continue
        elif char in "()":
            depth += 1 if char == "(" else -1
            if depth == 0:
                return text[at + 2:end], end + 1
        end += 1
    raise Unreadable()


def split(text, depth):
    # Splits shell text into simple commands, each a list of words. The commands
    # in a command substitution follow the others, and the substitution leaves
    # TUNNEL in its word when its body names the script. A heredoc leaves a
    # MARKER word in its command, and its body goes to HEREDOCS rather than
    # being read as commands.
    if depth > 8:
        raise Unreadable()
    found, inner, words, pending = [], [], [], []
    word, quote, at = None, "", 0

    def flush(ends_command):
        nonlocal word, words
        if word is not None:
            words.append(word)
            word = None
        if ends_command and words:
            found.append(words)
            words = []

    while at < len(text):
        char, pair = text[at], text[at:at + 2]
        if quote == "\x27":
            if char == quote:
                quote = ""
            else:
                word += char
            at += 1
        elif char == "\\":
            escaped = text[at + 1:at + 2]
            if escaped != "\n":
                kept = quote and escaped not in ("$", "`", "\"", "\\")
                word = (word or "") + ("\\" if kept else "") + escaped
            at += 2
        elif pair == "$(" or char == "`":
            body, at = substitution(text, at)
            commands = split(body, depth + 1)
            inner += commands
            named = any(NAMES_SCRIPT.search(w) for c in commands for w in c)
            word = (word or "") + (TUNNEL if named else "$()")
        elif quote:
            if char == quote:
                quote = ""
            else:
                word += char
            at += 1
        elif char in "\"\x27":
            quote, word = char, word or ""
            at += 1
        elif char in " \t\r":
            flush(False)
            at += 1
        elif opens_heredoc(text, at):
            # A number written against the redirection is its descriptor.
            if word is not None and word.isdigit():
                word = None
            flush(False)
            delimiter, strip, quoted, at = heredoc(text, at)
            words.append(MARKER + str(len(HEREDOCS)))
            pending.append((len(HEREDOCS), delimiter, strip, quoted))
            HEREDOCS.append("")
        elif char in "&|" and text[at - 1:at] in ("<", ">") or pair == "&>":
            word = (word or "") + char
            at += 1
        elif char == "\n" and pending:
            flush(True)
            read, at = bodies(text, at, [(d, s) for _, d, s, _ in pending])
            for (slot, _, _, quoted), body in zip(pending, read):
                HEREDOCS[slot] = body
                if not quoted:
                    inner += expansions(body, depth)
            pending = []
        elif char in ";&|()\n":
            flush(True)
            at += 1
        elif char == "#" and word is None:
            end = text.find("\n", at)
            at = len(text) if end < 0 else end
        else:
            word = (word or "") + char
            at += 1
    if quote:
        raise Unreadable()
    flush(True)
    return found + inner


def name(word):
    return word.rsplit("/", 1)[-1]


def listed(text):
    try:
        return shlex.split(text)
    except ValueError:
        raise Unreadable()


def options(words, short, long, signs="-"):
    # Skips the options at the front of words. Returns the words after them and
    # the short option letters seen. The string env -S splits is read as words
    # in its place.
    letters = ""
    while words and words[0] not in ("-", "--"):
        word, rest, taker, value = words[0], words[1:], "", ""
        if len(word) < 2 or word[0] not in signs:
            return words, letters
        if word.startswith("--"):
            taker, equals, value = word[2:].partition("=")
            if taker in long and not equals:
                value, rest = (rest or [""])[0], rest[1:]
        else:
            for end, letter in enumerate(word[1:], 2):
                letters += letter
                if letter in short:
                    taker, value = letter, word[end:]
                    if not value:
                        value, rest = (rest or [""])[0], rest[1:]
                    break
        if taker in ("S", "split-string"):
            rest = listed(value) + rest
        words = rest
    return words[1:], letters


def unredirected(words):
    # Drops each redirection, and its target when that is a word of its own.
    kept, target = [], False
    for word in words:
        if word.startswith(MARKER):
            continue
        match = None if target else REDIRECT.match(word)
        if match:
            target = not match.group(3)
        elif target:
            target = False
        else:
            kept.append(word)
    return kept


def tunnel(words):
    op, payload, at = None, None, 1
    while at < len(words):
        word = words[at]
        if word in ("--payload", "--runner", "--ref"):
            if at + 1 >= len(words):
                raise Unreadable()
            if word == "--payload":
                payload = words[at + 1]
            at += 2
            continue
        if word.startswith("--payload="):
            payload = word.split("=", 1)[1]
        elif not word.startswith("-") and op is None:
            op = word
        at += 1
    return {"op": op, "payload": payload, "file": payload is not None}


def dispatch(words):
    # Reads a workflow dispatch sent with gh. Returns None for any other gh
    # command. A dispatch whose inputs come from stdin or a file is refused when
    # it names the tunnel, has no target, or names its workflow by number or
    # through a shell expansion, since the guard cannot read what it sends. Any
    # other dispatch that does not name the tunnel yields no entries; one that
    # does yields its op and payload.
    if words[1:3] == ["workflow", "run"]:
        at = 3
    elif words[1:2] == ["api"] and any("dispatches" in w for w in words):
        at = 2
    else:
        return None
    fields, positional, unread = {}, [], False
    while at < len(words):
        word, value, flag = words[at], None, ""
        if word in FIELD_FLAGS and at + 1 < len(words):
            value, flag = words[at + 1], word
            at += 1
        elif re.match(r"^-[fF]\S", word):
            value, flag = word[2:], word[:2]
        elif re.match(r"^--(raw-)?field=", word):
            flag, value = word.split("=", 1)
        elif word in VALUE_FLAGS:
            at += 1
        elif word == "--json" or word.split("=", 1)[0] == "--input":
            unread = True
            if word == "--input":
                at += 1
        elif not word.startswith("-"):
            positional.append(word)
        if value is not None and "=" in value:
            key, val = value.split("=", 1)
            from_file = flag in ("-F", "--field") and val.startswith("@")
            fields[INPUT.sub(r"\1", key)] = (val[1:] if from_file else val, from_file)
        at += 1
    text = " ".join(words)
    url = DISPATCH_URL.search(text)
    target = url.group(1) if url else (positional or [""])[0]
    # The tunnel is named by its target (file, path, or display name) or by an
    # op input. An input value that carries the workflow word, such as a run
    # folder, leaves a dispatch of another workflow alone.
    named = WORKFLOW in target.lower() or "op" in fields
    # A number or a shell expansion can name any workflow, the tunnel included.
    unknown = not target or target.isdigit() or "$" in target or "`" in target
    if unread and (named or unknown):
        return [{"refuse": UNREAD.format(text[:160])}]
    if not named:
        return []
    payload = fields.get("payload", (None, False))
    return [{"op": fields.get("op", (None,))[0], "payload": payload[0], "file": payload[1]}]


def exempt(words):
    # Tells whether the command takes the tunnel script only as a file or as text.
    command = name(words[0])
    if command == "git":
        at = 1
        while at < len(words) and words[at].startswith("-"):
            at += 2 if words[at] in ("-C", "-c") else 1
        return at < len(words) and words[at] in GIT_FILE_COMMANDS
    if command == "find":
        return not FIND_RUNS & set(words)
    return command == "gh" or command in FILE_COMMANDS


def calls(words, depth):
    # Returns what one simple command sends through the tunnel: a call to check,
    # a refusal, or nothing. A body that could hold a tunnel call is refused
    # whatever reads it, since a pipe or a script flag can run text from any
    # command. A tunnel call fed a heredoc carries a stdin note, which the
    # bash side turns into a refusal for any op that is not a read.
    texts = [HEREDOCS[int(w[len(MARKER):])] for w in words if w.startswith(MARKER)]
    found = command_calls(words, depth)
    if not texts:
        return found
    shown = " ".join(unredirected(words))[:160]
    if any(names_tunnel(text) for text in texts):
        return found + [{"refuse": IN_BODY.format(shown)}]
    return [dict(e, stdin=STDIN_CALL.format(shown)) if "op" in e else e for e in found]


def command_calls(words, depth):
    # Reads the calls in one simple command, apart from its heredocs.
    words = unredirected(words)
    refuse = [{"refuse": UNPARSED.format(" ".join(words)[:160])}]
    rest = words
    while rest:
        word, command = rest[0], name(rest[0])
        if ASSIGNMENT.match(word):
            if NAMES_SCRIPT.search(word):
                return refuse
            rest = rest[1:]
        elif word in KEYWORDS:
            rest = rest[1:]
        elif command in PREFIXES:
            short, long, skip = PREFIXES[command]
            rest, letters = options(rest[1:], short, long)
            if command == "command" and set(letters) & set("vV"):
                return []
            rest = rest[skip:]
        elif command in SHELLS:
            rest, letters = options(rest[1:], "Oo", ("init-file", "rcfile"), "-+")
            if "n" in letters:
                return []
            if "c" in letters:
                named = any(NAMES_SCRIPT.search(w) for w in rest[1:])
                return nested(rest[:1], depth) + (refuse if named else [])
        elif command == "eval":
            return nested([" ".join(rest[1:])], depth)
        else:
            break
    if rest and name(rest[0]) == STAMP:
        return [{"stamp": rest[1] if len(rest) > 1 else None}]
    if rest and rest[0].endswith(TUNNEL):
        return [tunnel(rest)]
    read = dispatch(rest) if rest and name(rest[0]) == "gh" else None
    if read is not None:
        return read
    if rest and exempt(rest):
        return []
    for at, word in enumerate(words):
        if NAMES_SCRIPT.search(word) or DISPATCH_URL.search(word):
            return refuse
        if name(word) == "gh" and dispatch(words[at:]):
            return refuse
    return []


def nested(texts, depth):
    found = []
    for text in texts:
        for words in split(text, depth + 1):
            found += calls(words, depth + 1)
    return found


def chain(commands):
    # Marks each tunnel call whose payload a stamp call earlier in the command
    # names, read from the same directory. split() puts the commands inside a
    # substitution after the rest, so a stamp there never counts as earlier.
    # The chain is off for a payload file any other command names, since that
    # command can rewrite the file between the stamp and the send.
    entries, others, where = [], [], ""
    for words in commands:
        plain = unredirected(words)
        if plain and name(plain[0]) in MOVES:
            target = plain[1] if len(plain) > 1 else ""
            moved = name(plain[0]) == "cd" and target.startswith("/")
            where = target if moved else "?"
        found = calls(words, 0)
        if not any("stamp" in e or "op" in e for e in found):
            others.append(words)
        entries += [dict(e, dir=where) for e in found]
    stamped = []
    for entry in entries:
        if "stamp" in entry:
            stamped.append((entry["stamp"], entry["dir"]))
            continue
        payload = entry.get("payload")
        if not payload or "op" not in entry:
            continue
        absolute = payload.startswith("/")
        path = not payload.lstrip().startswith(("{", "["))
        base = name(payload)
        touched = path and any(base in w for c in others for w in c)
        entry["chained"] = not touched and any(
            arg == payload and (absolute or at == entry["dir"] != "?")
            for arg, at in stamped)
    return [e for e in entries if "stamp" not in e]


try:
    for entry in chain(split(sys.stdin.read(), 0)):
        print(json.dumps(entry))
except Unreadable:
    sys.exit(3)
'

parsed=$(python3 -c "$PARSER" "$hook_lib" "$tunnel_script" "$workflow_name" "$stamp_command" \
  <<<"$cmd")
case "$?" in
  0) ;;
  *) deny "a command the guard could not parse" ;;
esac
[ -n "$parsed" ] || exit 0
refused=$(jq -r '.refuse // empty' <<<"$parsed" | head -n 1)
[ -z "$refused" ] || deny "$refused"

# shellcheck source=terms.sh
. "$HERE/terms.sh"
terms_use_config "$config" || deny "the terms table the config names does not load"
read_terms || deny "${TERMS_FILE##*/} does not load"
select_terms all "$TERMS_TRACKER"
# The work tree the command runs in, which holds its stamps and the tree a
# push sends.
root=$(git -C "${cwd:-.}" rev-parse --show-toplevel 2>/dev/null || echo "${CLAUDE_PROJECT_DIR:-.}")
stamps="$root/$stamp_dir"
[ -n "$stamp_env" ] && [ -n "${!stamp_env:-}" ] && stamps="${!stamp_env}"

while IFS= read -r entry; do
  op=$(jq -r '.op // ""' <<<"$entry")
  [ -n "$op" ] || deny "a tunnel dispatch whose op could not be read"
  is_read_op "$op" && continue
  stdin=$(jq -r '.stdin // ""' <<<"$entry")
  [ -z "$stdin" ] || deny "$stdin"
  payload=$(jq -r '.payload // ""' <<<"$entry")
  from_file=$(jq -r '.file' <<<"$entry")
  chained=$(jq -r '.chained // false' <<<"$entry")
  # The directory a cd to an absolute path earlier in the command moved to.
  dir=$(jq -r '.dir // ""' <<<"$entry")
  case "$dir" in /*) ;; *) dir="${cwd:-.}" ;; esac
  [ -n "$payload" ] || deny "$op writes and names no payload"
  file=""
  if [ "$from_file" = true ]; then
    case "$payload" in /*) file="$payload" ;; *) file="$dir/$payload" ;; esac
    # The tunnel reads --payload as a file when one exists and as JSON otherwise.
    [ -f "$file" ] || file=""
  fi
  if [ -n "$file" ]; then
    sha=$(sha256sum "$file" | cut -d' ' -f1)
    text=$(cat "$file")
  else
    sha=$(printf '%s' "$payload" | sha256sum | cut -d' ' -f1)
    text="$payload"
  fi
  if [ ! -f "$stamps/$sha" ]; then
    [ "$chained" = true ] || deny "$op payload $sha has no repo-writing stamp"
    # The chained stamp has not run yet, so the payload is read as it stands
    # now. A name no file answers to yet reads as literal text here, while the
    # send would carry whatever the command writes there first.
    [ -n "$file" ] || jq -e . >/dev/null 2>&1 <<<"$payload" ||
      deny "$op payload $payload is neither a file that exists yet nor JSON"
    scan_dir=$(mktemp -d)
    printf '%s\n' "$text" >"$scan_dir/payload.md"
    scan=$("$HERE/check-repo-text.sh" --config "$config" "$scan_dir/payload.md" 2>&1)
    status=$?
    rm -rf "$scan_dir"
    [ "$status" = 0 ] ||
      deny "$op payload $sha fails the repository text scan: $(head -c 800 <<<"$scan")"
  fi
  hits=$(cut_kept <<<"$text" | terms_hit_lines)
  [ -z "$hits" ] || deny "$op payload $sha carries a banned term on line(s) $hits"
  [ -n "$lint_op" ] && [ "$op" = "$lint_op" ] || continue
  # A push sends the tree, so the comments and strings in it are read too, by
  # the boundary lint that stays on this side. --quiet drops the notes about
  # disable comments the shipped config owns, which this config does not carry.
  boundary="$root/$lint_command"
  [ -x "$boundary" ] || deny "the boundary lint needs ${lint_command##*/} installed: npm ci"
  lint=$(cd "$root" && "$boundary" -c "$lint_config" . --quiet 2>&1)
  status=$?
  [ "$status" = 0 ] || deny "the boundary lint reports: $(head -c 800 <<<"$lint")"
done <<<"$parsed"
exit 0
