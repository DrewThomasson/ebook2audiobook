import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
README = ROOT / 'README.md'
BASELINE = HERE / 'baseline_README.md'
CACHE_FILE = HERE / 'cache.json'
I18N_DIR = ROOT / 'readme'
EMAIL = ''
MAX_CHUNK = 450
THROTTLE = 0.4
LANGS = {
    'ara': 'ar', 'zho': 'zh-CN', 'spa': 'es', 'fra': 'fr', 'deu': 'de',
    'ita': 'it', 'por': 'pt', 'pol': 'pl', 'tur': 'tr', 'rus': 'ru',
    'nld': 'nl', 'ces': 'cs', 'jpn': 'ja', 'hin': 'hi', 'ben': 'bn',
    'hun': 'hu', 'kor': 'ko', 'vie': 'vi', 'swe': 'sv', 'fas': 'fa',
    'yor': 'yo', 'swa': 'sw', 'ind': 'id', 'slk': 'sk', 'hrv': 'hr',
}
PROTECT = re.compile(
    r'(`[^`\n]+`'
    r'|!\[[^\]]+\]\([^)]+\)'
    r'|\[[^\]]+\]\([^)]+\)'
    r'|https?://\S+'
    r'|<[^>\n]+>'
    r'|{[^}\n]+}'
    r'|\[pause:\d+\]'
    r'|&\w+;)'
)
# names MT translates when they stand alone (Windows -> Fenster/Janelas, Docker -> Sztauer/Acoplagem):
# a text holding no other word is kept as is, never sent to MT
KEEP = re.compile(r'\b(?:Windows|Linux|MacOS|Docker|ARM)\b')
MARKER = re.compile(r'⟦\s*(\d+)\s*⟧')
STRAY = re.compile(r'[⟦⟧]')
LINE_PREFIX = re.compile(r'^(\s*(?:[-*+]\s+|\d+\.\s+|#{1,6}\s+|>\s+)?(?:\[[ x]\]\s+)?)')
FENCE = re.compile(r'```[\s\S]*?```')

def load_cache()->dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
    return {}

def save_cache(cache:dict)->None:
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n')

def split_blocks(text:str)->list:
    lines:list = text.split('\n')
    blocks:list = []
    buf:list = []
    in_fence:bool = False
    for line in lines:
        buf.append(line)
        if line.lstrip().startswith('```'):
            in_fence = not in_fence
            continue
        if line.strip() == '' and not in_fence:
            blocks.append(buf)
            buf = []
    if buf:
        blocks.append(buf)
    return blocks

def join_blocks(blocks:list)->str:
    return '\n'.join(line for block in blocks for line in block)

def block_key(block:list)->str:
    return '\n'.join(block)

def frozen_lines(block:list)->list:
    # the lines kept from English: a whole table, else the code fences and their content only, so the
    # headings, prose and list items of a block holding a fence are translated too
    stripped:list = [l for l in (line.strip() for line in block) if l]
    if stripped and all(l.startswith('|') for l in stripped):
        return [True] * len(block)
    mask:list = []
    in_fence:bool = False
    for line in block:
        fence:bool = line.lstrip().startswith('```')
        mask.append(in_fence or fence)
        if fence:
            in_fence = not in_fence
    return mask

def block_tokens(block:list)->list:
    return sorted(tok for line in block for tok in PROTECT.findall(line))

def protect(text:str)->tuple:
    tokens:list = []
    def repl(m)->str:
        tokens.append(m.group(0))
        return f'\u27e6{len(tokens)-1}\u27e7'
    return PROTECT.sub(repl, text), tokens

def restore(text:str, tokens:list)->Optional[str]:
    # every placeholder back exactly once (MT may pad it with spaces), else None: no marker MT broke or glued to a word
    # is ever left in the text. Callable replacement: a token is literal text, its backslashes (windows paths) are no regex escapes
    if sorted(int(i) for i in MARKER.findall(text)) != list(range(len(tokens))) or STRAY.search(MARKER.sub('', text)):
        return None
    return MARKER.sub(lambda m: tokens[int(m.group(1))], text)

def realign_tokens(tr_line:str, eng_tokens:list)->Optional[str]:
    # tokens MT kept stay where they are, the ones it altered are swapped in place for the missing English ones
    # (in English order), extra ones are dropped. None when MT lost tokens entirely: no position left to put them back
    pool:list = list(eng_tokens)
    kept:list = []
    for tok in PROTECT.findall(tr_line):
        if tok in pool:
            pool.remove(tok)
            kept.append(True)
        else:
            kept.append(False)
    spare = iter(pool)
    flags = iter(kept)
    removed:bool = False
    def repl(m)->str:
        nonlocal removed
        if next(flags):
            return m.group(0)
        tok:Optional[str] = next(spare, None)
        if tok is None:
            removed = True
            return ''
        return tok
    fixed:str = PROTECT.sub(repl, tr_line)
    if list(spare):
        return None
    if removed:
        fixed = re.sub(r'(?<=\S) {2,}', ' ', fixed).rstrip()
    return fixed

def mymemory(text:str, lang:str)->str:
    params = {
        "q": text,
        "langpair": f"en|{lang}",
    }
    if EMAIL:
        params['de'] = EMAIL
    url:str = 'https://api.mymemory.translated.net/get?' + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            if data.get('responseStatus') == 200:
                return data['responseData']['translatedText']
            print(f'  status {data.get("responseStatus")} for {lang}, retry {attempt+1}', file=sys.stderr)
        except Exception as e:
            print(f'  retry {attempt+1} for {lang}: {e}', file=sys.stderr)
        time.sleep(2*(attempt+1))
    raise RuntimeError(f'MyMemory failed for lang={lang}')

def chunk_text(text:str)->list:
    chunks:list = []
    current:str = ''
    for piece in re.split(r'(?<=[.!?;:]) ', text):
        if len(current)+len(piece)+1 > MAX_CHUNK and current:
            chunks.append(current)
            current = piece
        else:
            current = f'{current} {piece}'.strip()
    if current:
        chunks.append(current)
    return chunks

def translate_segments(text:str, lang:str)->str:
    # tokens never reach MT: only the prose between them is translated, each token stays verbatim in its own place
    out:list = []
    pos:int = 0
    for m in [*PROTECT.finditer(text), None]:
        segment:str = text[pos:m.start() if m else len(text)]
        s = re.match(r'^(\s*)(.*?)(\s*)$', segment, re.S)
        if re.search(r'[A-Za-z]', KEEP.sub('', s.group(2))):
            segment = s.group(1) + ' '.join(mymemory(chunk, lang) for chunk in chunk_text(s.group(2))).strip() + s.group(3)
            time.sleep(THROTTLE)
        out.append(segment)
        if m:
            out.append(m.group(0))
            pos = m.end()
    return ''.join(out).replace('\n', ' ')

def translate_text(text:str, lang:str, cache:dict)->str:
    protected, tokens = protect(text)
    # before the cache: an older run may hold the MT of a name that stands alone
    if not re.search(r'[A-Za-z]', KEEP.sub('', protected)):
        return text
    key:str = f'{lang}|{text}'
    if key in cache and not STRAY.search(cache[key]):
        return cache[key]
    translated:str = ' '.join(mymemory(chunk, lang) for chunk in chunk_text(protected))
    restored:Optional[str] = restore(translated, tokens)
    # markers lost or broken: segment mode, never tokens pushed to the end of the line
    result:str = restored if restored is not None else translate_segments(text, lang)
    result = result.replace('\n', ' ')
    cache[key] = result
    time.sleep(THROTTLE)
    return result

def translate_line(line:str, lang:str, cache:dict)->str:
    m = LINE_PREFIX.match(line)
    prefix:str = m.group(1) if m else ''
    body:str = line[len(prefix):]
    if not body.strip():
        return line
    return prefix + translate_text(body, lang, cache)

def translate_block(block:list, lang:str, cache:dict)->list:
    return [line if frozen else translate_line(line, lang, cache) for line, frozen in zip(block, frozen_lines(block))]

def patch_line(old_line:str, new_line:str, tr_line:str)->Optional[str]:
    old_protected, old_tokens = protect(old_line)
    new_protected, new_tokens = protect(new_line)
    if old_protected != new_protected or len(old_tokens) != len(new_tokens):
        return None
    patched:str = tr_line
    for old_tok, new_tok in zip(old_tokens, new_tokens):
        if old_tok == new_tok:
            continue
        if old_tok not in patched:
            return None
        patched = patched.replace(old_tok, new_tok, 1)
    return patched

def patch_block(old_block:list, new_block:list, tr_block:list, lang:str, cache:dict)->list:
    mask:list = frozen_lines(new_block)
    if all(mask):
        return new_block
    if len(old_block) != len(new_block) or len(tr_block) != len(old_block):
        return translate_block(new_block, lang, cache)
    out:list = []
    for old_line, new_line, tr_line, frozen in zip(old_block, new_block, tr_block, mask):
        if frozen:
            out.append(new_line)
            continue
        if old_line == new_line:
            out.append(tr_line)
            continue
        patched:Optional[str] = patch_line(old_line, new_line, tr_line)
        if patched is not None:
            out.append(patched)
        else:
            out.append(translate_line(new_line, lang, cache))
    return out

def harvest_block(eng_block:list, tr_block:list, lang:str, cache:dict)->None:
    if len(eng_block) != len(tr_block):
        return
    for eng_line, tr_line, frozen in zip(eng_block, tr_block, frozen_lines(eng_block)):
        if frozen:
            continue
        m = LINE_PREFIX.match(eng_line)
        prefix:str = m.group(1) if m else ''
        eng_body:str = eng_line[len(prefix):]
        if not tr_line.startswith(prefix):
            continue
        tr_body:str = tr_line[len(prefix):]
        if not (eng_body.strip() and tr_body.strip() and eng_body != tr_body) or STRAY.search(tr_body):
            continue
        if sorted(PROTECT.findall(eng_body)) != sorted(PROTECT.findall(tr_body)):
            continue
        cache[f'{lang}|{eng_body}'] = tr_body

def audit_and_repair(out_blocks:list, new_blocks:list, lang:str, cache:dict)->tuple:
    repaired:list = []
    notes:list = []
    for idx, (tr_block, eng_block) in enumerate(zip(out_blocks, new_blocks)):
        mask:list = frozen_lines(eng_block)
        if all(mask):
            if block_key(tr_block) != block_key(eng_block):
                notes.append(f'block {idx+1}: frozen content (code/table) restored from English')
            repaired.append(eng_block)
            continue
        if len(tr_block) != len(eng_block):
            notes.append(f'block {idx+1}: line count differs from English, block retranslated')
            repaired.append(translate_block(eng_block, lang, cache))
            continue
        if any(tr_line != eng_line for tr_line, eng_line, frozen in zip(tr_block, eng_block, mask) if frozen):
            notes.append(f'block {idx+1}: code restored from English')
            tr_block = [eng_line if frozen else tr_line for tr_line, eng_line, frozen in zip(tr_block, eng_block, mask)]
        if any(mask):
            # prose beside code, kept in English when a block holding a fence was frozen whole: translated now
            translated:list = [translate_line(eng_line, lang, cache) if not frozen and tr_line == eng_line else tr_line for tr_line, eng_line, frozen in zip(tr_block, eng_block, mask)]
            changed:int = sum(1 for before, after in zip(tr_block, translated) if before != after)
            if changed:
                notes.append(f'block {idx+1}: {changed} line(s) beside code translated')
            tr_block = translated
        fixed_block:list = []
        realigned:int = 0
        retranslated:int = 0
        for tr_line, eng_line, frozen in zip(tr_block, eng_block, mask):
            _, eng_tokens = protect(eng_line)
            stray:bool = bool(STRAY.search(tr_line))
            if frozen or (not stray and sorted(PROTECT.findall(tr_line)) == sorted(eng_tokens)):
                fixed_block.append(tr_line)
                continue
            m = LINE_PREFIX.match(eng_line)
            prefix:str = m.group(1) if m else ''
            eng_body:str = eng_line[len(prefix):]
            fixed_line:Optional[str] = None if stray else realign_tokens(tr_line, eng_tokens)
            if fixed_line is None:
                # a token lost or an MT marker left in the text: retranslated now around its tokens,
                # once written the line has all its tokens and no later run would pick it up again
                fixed_line = prefix + translate_segments(eng_body, lang)
                retranslated += 1
            else:
                realigned += 1
            fixed_block.append(fixed_line)
            tr_body:str = fixed_line[len(prefix):] if fixed_line.startswith(prefix) else fixed_line
            if eng_body.strip():
                cache[f'{lang}|{eng_body}'] = tr_body
        if realigned:
            notes.append(f'block {idx+1}: inline code/links/tags altered by MT on {realigned} line(s), English tokens put back in place')
        if retranslated:
            notes.append(f'block {idx+1}: {retranslated} line(s) lost tokens or kept MT markers, retranslated around their tokens')
        repaired.append(fixed_block)
    return repaired, notes

def verify(lang_text:str, eng_text:str)->list:
    problems:list = []
    if FENCE.findall(lang_text) != FENCE.findall(eng_text):
        problems.append('code fences differ from English source')
    lang_count:int = len(split_blocks(lang_text))
    eng_count:int = len(split_blocks(eng_text))
    if lang_count != eng_count:
        problems.append(f'block count {lang_count} != English {eng_count}')
    return problems

def rebuild(new_blocks:list, lang:str, cache:dict)->list:
    return [translate_block(b, lang, cache) for b in new_blocks]

def main()->int:
    new_src:str = README.read_text(encoding='utf-8')
    if not BASELINE.exists():
        BASELINE.write_text(new_src, encoding='utf-8', newline='\n')
        print('baseline seeded from current README.md, translations assumed in sync')
        return 0
    old_src:str = BASELINE.read_text(encoding='utf-8')
    cache:dict = load_cache()
    old_blocks:list = split_blocks(old_src)
    new_blocks:list = split_blocks(new_src)
    sm = difflib.SequenceMatcher(None, [block_key(b) for b in old_blocks], [block_key(b) for b in new_blocks], autojunk=False)
    opcodes:list = sm.get_opcodes()
    changed:int = sum(1 for tag, *_ in opcodes if tag != 'equal')
    print(f'{changed} changed region(s) detected in README.md')
    for iso3, mm_code in LANGS.items():
        target:Path = I18N_DIR / f'README_{iso3}.md'
        if not target.exists():
            print(f'[{iso3}] missing, retranslating whole file')
            out_blocks:list = rebuild(new_blocks, mm_code, cache)
        else:
            tr_blocks:list = split_blocks(target.read_text(encoding='utf-8'))
            if len(tr_blocks) != len(old_blocks):
                print(f'[{iso3}] structure drift ({len(tr_blocks)} vs {len(old_blocks)} blocks), retranslating whole file')
                out_blocks = rebuild(new_blocks, mm_code, cache)
            else:
                out_blocks = []
                for tag, i1, i2, j1, j2 in opcodes:
                    if tag == 'equal':
                        for k in range(i1, i2):
                            harvest_block(old_blocks[k], tr_blocks[k], mm_code, cache)
                        out_blocks.extend(tr_blocks[i1:i2])
                    elif tag == 'replace' and (i2-i1) == (j2-j1):
                        for k in range(i2-i1):
                            out_blocks.append(patch_block(old_blocks[i1+k], new_blocks[j1+k], tr_blocks[i1+k], mm_code, cache))
                    elif tag in ('replace', 'insert'):
                        out_blocks.extend(translate_block(b, mm_code, cache) for b in new_blocks[j1:j2])
        if len(out_blocks) != len(new_blocks):
            print(f'[{iso3}] block alignment lost, rebuilding from English')
            out_blocks = rebuild(new_blocks, mm_code, cache)
        out_blocks, notes = audit_and_repair(out_blocks, new_blocks, mm_code, cache)
        for note in notes:
            print(f'[{iso3}] {note}')
        out_text:str = join_blocks(out_blocks)
        problems:list = verify(out_text, new_src)
        if problems:
            print(f'[{iso3}] integrity check failed ({"; ".join(problems)}), rebuilding from English')
            out_blocks = rebuild(new_blocks, mm_code, cache)
            out_text = join_blocks(out_blocks)
            problems = verify(out_text, new_src)
            if problems:
                raise RuntimeError(f'[{iso3}] still inconsistent after rebuild: {"; ".join(problems)}')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(out_text, encoding='utf-8', newline='\n')
        save_cache(cache)
        print(f'[{iso3}] updated')
    BASELINE.write_text(new_src, encoding='utf-8', newline='\n')
    print('baseline updated')
    return 0

if __name__ == '__main__':
    sys.exit(main())
