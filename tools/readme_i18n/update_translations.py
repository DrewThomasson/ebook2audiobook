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
    r'|!\[[^\]]*\]\([^)]+\)'
    r'|\]\([^)]+\)'
    r'|https?://\S+'
    r'|<[^>\n]+>'
    r'|\{[^}\n]*\}'
    r'|\[pause:\d+\]'
    r'|&\w+;)'
)
LINE_PREFIX = re.compile(r'^(\s*(?:[-*+]\s+|\d+\.\s+|#{1,6}\s+|>\s+)?(?:\[[ x]\]\s+)?)')
FENCE = re.compile(r'```[\s\S]*?```')

def load_cache()->dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
    return {}

def save_cache(cache:dict)->None:
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding='utf-8')

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

def is_frozen_block(block:list)->bool:
    text:str = block_key(block)
    if '```' in text:
        return True
    stripped:list = [l for l in (line.strip() for line in block) if l]
    if stripped and all(l.startswith('|') for l in stripped):
        return True
    return False

def protect(text:str)->tuple:
    tokens:list = []
    def repl(m)->str:
        tokens.append(m.group(0))
        return f'\u27e6{len(tokens)-1}\u27e7'
    return PROTECT.sub(repl, text), tokens

def restore(text:str, tokens:list)->Optional[str]:
    for i, tok in enumerate(tokens):
        ph:str = f'\u27e6{i}\u27e7'
        if ph not in text:
            return None
        text = text.replace(ph, tok)
    return text

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

def translate_text(text:str, lang:str, cache:dict)->str:
    key:str = f'{lang}|{text}'
    if key in cache:
        return cache[key]
    protected, tokens = protect(text)
    if not re.search(r'[A-Za-z]', protected):
        return text
    translated:str = ' '.join(mymemory(chunk, lang) for chunk in chunk_text(protected))
    restored:Optional[str] = restore(translated, tokens)
    result:str = restored if restored is not None else text
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
    if is_frozen_block(block):
        return block
    return [translate_line(line, lang, cache) for line in block]

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
    if is_frozen_block(new_block):
        return new_block
    if len(old_block) != len(new_block) or len(tr_block) != len(old_block):
        return translate_block(new_block, lang, cache)
    out:list = []
    for old_line, new_line, tr_line in zip(old_block, new_block, tr_block):
        if old_line == new_line:
            out.append(tr_line)
            continue
        patched:Optional[str] = patch_line(old_line, new_line, tr_line)
        if patched is not None:
            out.append(patched)
        else:
            out.append(translate_line(new_line, lang, cache))
    return out

def verify(lang_text:str, eng_text:str)->list:
    problems:list = []
    if FENCE.findall(lang_text) != FENCE.findall(eng_text):
        problems.append('code fences differ from English source')
    if lang_text.count('\n') != eng_text.count('\n'):
        problems.append(f'line count {lang_text.count(chr(10))} != English {eng_text.count(chr(10))}')
    return problems

def rebuild(new_blocks:list, lang:str, cache:dict)->list:
    return [translate_block(b, lang, cache) for b in new_blocks]

def main()->int:
    new_src:str = README.read_text(encoding='utf-8')
    if not BASELINE.exists():
        BASELINE.write_text(new_src, encoding='utf-8')
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
                        out_blocks.extend(tr_blocks[i1:i2])
                    elif tag == 'replace' and (i2-i1) == (j2-j1):
                        for k in range(i2-i1):
                            out_blocks.append(patch_block(old_blocks[i1+k], new_blocks[j1+k], tr_blocks[i1+k], mm_code, cache))
                    elif tag in ('replace', 'insert'):
                        out_blocks.extend(translate_block(b, mm_code, cache) for b in new_blocks[j1:j2])
        out_text:str = join_blocks(out_blocks)
        problems:list = verify(out_text, new_src)
        if problems:
            print(f'[{iso3}] integrity check failed ({"; ".join(problems)}), rebuilding from English')
            out_text = join_blocks(rebuild(new_blocks, mm_code, cache))
            problems = verify(out_text, new_src)
            if problems:
                raise RuntimeError(f'[{iso3}] still inconsistent after rebuild: {"; ".join(problems)}')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(out_text, encoding='utf-8')
        save_cache(cache)
        print(f'[{iso3}] updated')
    BASELINE.write_text(new_src, encoding='utf-8')
    print('baseline updated')
    return 0

if __name__ == '__main__':
    sys.exit(main())
