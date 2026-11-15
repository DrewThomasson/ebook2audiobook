#!/usr/bin/env python3
"""Read, narrow and check a blocks file written by --export_blocks.

usage:
  blocks.py list  <blocks.json>                    one line per block: index, keep, words, first words
  blocks.py show  <blocks.json> <index>            the text of one block
  blocks.py only  <blocks.json> <index>[,<index>]  keep these blocks, set "keep" to false on the others
  blocks.py check <original.json> <edited.json> [--only <index>[,<index>]]

check exits 1 unless the edited file is the original with SML tags added and nothing else:
the same blocks in the same order, every word and every tag of the original still there in
the same order, the paired tags closed, and each [direct:...] note under ten words. With
--only, a block outside the list must not have changed at all. It prints the tags added to
each block, which is the summary to show before converting, and a note for each added tag
that falls inside a sentence.

Indexes count from 0, as the app's own messages do.
"""
import json
import re
import sys

# the tag grammar of SML_TAG_PATTERN in lib/conf_models.py
TAG = re.compile(r'\[\s*(?P<close>/)?\s*(?P<tag>break|pause|voice|emotion|direct)(?:\s*:\s*(?P<value>.*?))?\s*\]', re.DOTALL)
DIRECT_MAX_WORDS = 9
SENTENCE_END = re.compile(r'[.!?…]["\'”’»)\]]*$')

def load(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get('blocks'), list):
        sys.exit(f'{path}: not a blocks file, it has no "blocks" list')
    return data

def indexes(arg, count):
    try:
        chosen = sorted({int(part) for part in arg.split(',')})
    except ValueError:
        sys.exit(f'{arg}: block indexes are whole numbers separated by commas')
    for i in chosen:
        if not 0 <= i < count:
            sys.exit(f'block {i} does not exist, the file has blocks 0 to {count - 1}')
    return chosen

def tokens(text):
    # words and tags in reading order; a tag is ('tag', closing, name, value)
    out, pos = [], 0
    for m in TAG.finditer(text):
        out.extend(text[pos:m.start()].split())
        out.append(('tag', bool(m.group('close')), m.group('tag'), (m.group('value') or '').strip()))
        pos = m.end()
    out.extend(text[pos:].split())
    return out

def written(token):
    if isinstance(token, str):
        return token
    _, close, name, value = token
    return f'[{"/" if close else ""}{name}{":" + value if value else ""}]'

def added_tags(original, edited):
    # the tags the edited text adds, each with the word before it and the words after it, or an error string.
    # The original must be what is left of the edited text once some of its tags are taken out.
    want, have = tokens(original), tokens(edited)
    added, i = [], 0
    for j, token in enumerate(have):
        if i < len(want) and token == want[i]:
            i += 1
        elif isinstance(token, tuple):
            before = next((t for t in reversed(have[:j]) if isinstance(t, str)), None)
            added.append((token, before, [t for t in have[j + 1:j + 60] if isinstance(t, str)]))
        else:
            expected = written(want[i]) if i < len(want) else 'the end of the block'
            before = ' '.join(written(t) for t in have[max(0, j - 6):j])
            return f'after "{before}" the original has {expected!r}, the edited text has {token!r}'
    if i < len(want):
        rest = ' '.join(written(t) for t in want[i:i + 8])
        return f'the edited text ends before the original does, missing from "{rest}"'
    return added

def tag_errors(text):
    errors, open_tags = [], []
    for token in tokens(text):
        if isinstance(token, str):
            continue
        _, close, name, value = token
        if name == 'pause':
            if close or (value and not re.fullmatch(r'\d+(\.\d+)?', value)):
                errors.append(f'{written(token)} is not [pause] or [pause:N] with N in seconds')
        elif name == 'break':
            if close or value:
                errors.append(f'{written(token)} is not [break]')
        elif close:
            if not open_tags or open_tags[-1] != name:
                errors.append(f'[/{name}] closes nothing' if name not in open_tags else f'[/{name}] closes before [/{open_tags[-1]}]')
            if name in open_tags:
                del open_tags[len(open_tags) - 1 - open_tags[::-1].index(name):]
        else:
            if name in open_tags:
                errors.append(f'{written(token)} opens inside another [{name}] passage')
            if not value:
                errors.append(f'[{name}] has no value')
            elif name == 'direct' and len(value.split()) > DIRECT_MAX_WORDS:
                errors.append(f'{written(token)} is {len(value.split())} words, a direction is under ten')
            open_tags.append(name)
    errors.extend(f'[{name}:...] is never closed' for name in open_tags)
    return errors

def cmd_list(path):
    for i, block in enumerate(load(path)['blocks']):
        words = block['text'].split()
        print(f'{i:>4}  {"keep" if block.get("keep", True) else "skip"}  {len(words):>6} words  {" ".join(words[:12])}')

def cmd_show(path, index):
    blocks = load(path)['blocks']
    print(blocks[indexes(index, len(blocks))[0]]['text'])

def cmd_only(path, chosen):
    data = load(path)
    chosen = indexes(chosen, len(data['blocks']))
    for i, block in enumerate(data['blocks']):
        block['keep'] = i in chosen
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'{path}: blocks {", ".join(map(str, chosen))} kept, {len(data["blocks"]) - len(chosen)} set to skip')

def cmd_check(original_path, edited_path, only=None):
    original, edited = load(original_path)['blocks'], load(edited_path)['blocks']
    if len(original) != len(edited):
        sys.exit(f'FAIL: {edited_path} has {len(edited)} blocks, {original_path} has {len(original)}')
    chosen = indexes(only, len(original)) if only else None
    failed = False
    for i, (before, after) in enumerate(zip(original, edited)):
        problems = []
        if before.get('id') != after.get('id'):
            problems.append(f'its id is {after.get("id")}, the original is {before.get("id")}')
        if chosen is not None and i not in chosen:
            if before['text'] != after['text']:
                problems.append('its text changed and it is not one of the chosen blocks')
            added = []
        else:
            added = added_tags(before['text'], after['text'])
            if isinstance(added, str):
                problems.append(added)
                added = []
            problems.extend(tag_errors(after['text']))
        if problems:
            failed = True
            for problem in problems:
                print(f'FAIL block {i}: {problem}')
        if added:
            print(f'block {i}, tags added:')
            for token, prev, following in added:
                if not token[1]:
                    print(f'    {written(token):<44} {" ".join(following[:8])}')
            # the engines that read a tag render the text on each side of it as a request of its own
            for token, prev, following in added:
                if prev and following and not SENTENCE_END.search(prev):
                    print(f'    note: {written(token)} falls inside a sentence, after "{prev}"')
    if failed:
        sys.exit(1)
    skipped = sum(1 for block in edited if not block.get('keep', True))
    print(f'OK: {len(edited)} blocks, {skipped} set to skip; apart from the added tags the text is the original\'s')

def main(argv):
    if len(argv) == 3 and argv[1] == 'list':
        cmd_list(argv[2])
    elif len(argv) == 4 and argv[1] == 'show':
        cmd_show(argv[2], argv[3])
    elif len(argv) == 4 and argv[1] == 'only':
        cmd_only(argv[2], argv[3])
    elif len(argv) == 4 and argv[1] == 'check':
        cmd_check(argv[2], argv[3])
    elif len(argv) == 6 and argv[1] == 'check' and argv[4] == '--only':
        cmd_check(argv[2], argv[3], argv[5])
    else:
        sys.exit(__doc__)

if __name__ == '__main__':
    main(sys.argv)
