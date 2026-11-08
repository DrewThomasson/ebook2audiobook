import argparse
import ast
import html
import json
import os
import re
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LANG_DIR = ROOT / 'lib' / 'lang'
ENG_FILE = LANG_DIR / 'legends_eng.py'
INIT_FILE = LANG_DIR / '__init__.py'
BASELINE = HERE / 'baseline_legends_eng.py'
EMAIL = os.environ.get('MYMEMORY_EMAIL', '')
MAX_CHUNK = 450
THROTTLE = 0.4
MT_CODES = {'zho': 'zh-CN', 'jav': 'jv-ID'}
NO_SPACE_JOIN = ('ja', 'zh-CN')
PROTECT = re.compile(
    r'(\{\{[^\n]*?\}\}'
    r'|\{[^{}\n]*\}'
    r'|"[^"\n]*"'
    r'|<[^>\n]+>'
    r'|\[[^\]\n]*\]'
    r'|https?://\S+'
    r'|&\w+;'
    r'|`[^`\n]+`'
    r'|\*{3,}'
    r'|(?<![\w-])--[A-Za-z][\w-]*'
    r'|(?:\./)?[\w/.-]*\w\.(?:py|json|wav|mp3|epub|zip|cmd|command|sh|txt|vtt|onnx|pth|traineddata)\b'
    r'|\b[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+\b'
    r'|(?<![\w=])[a-z]+=-?\d+(?:\.\d+)?(?:,[a-z]+=-?\d+(?:\.\d+)?)*(?![\w.])'
    r'|(?<![\w.])-?\d+\.\d+(?![\w.])'
    r'|[\u2190-\u21ff\u2300-\u23ff\u25a0-\u27bf])'
)
MARKER = re.compile(r'\u27e6\s*(\d+)(?:\s*\u27e7|(?!\w))|[\u301a\u3010\[]\s*(\d+)\s*[\u27e7\u301b\u3011\]]')
STRAY = re.compile(r'[\u27e6\u27e7\u301a\u301b\u3010\u3011]')
MARKER_MAX_FAILS = 2
marker_fails:dict = {}

class QuotaExceeded(Exception):
    pass

class LangRejected(Exception):
    pass

def load_assign(path:Path, name:str)->dict:
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            if isinstance(node.value, ast.Dict):
                keys:list = [ast.literal_eval(k) for k in node.value.keys]
                dupes:list = sorted({k for k in keys if keys.count(k) > 1})
                if dupes:
                    raise RuntimeError(f'{path.name}: duplicate key(s) {", ".join(dupes)}')
            return ast.literal_eval(node.value)
    raise RuntimeError(f'{path.name}: no "{name}" dict found')

def quote(text:str)->str:
    return "'"+text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')+"'"

def dump_legends(legends:dict)->str:
    lines:list = ['legends = {']
    lines.extend(f"    '{key}': {quote(value)}," for key, value in legends.items())
    lines.append('}')
    return '\n'.join(lines)+'\n'

def write_legends(path:Path, legends:dict)->None:
    text:str = dump_legends(legends)
    if ast.literal_eval(text.split('=', 1)[1].strip()) != legends:
        raise RuntimeError(f'{path.name}: serialization mismatch, file not written')
    tmp:Path = path.with_name(path.name+'.tmp')
    tmp.write_text(text, encoding='utf-8')
    os.replace(tmp, path)

def format_fields(text:str)->Optional[list]:
    try:
        return sorted(f for _, f, _, _ in string.Formatter().parse(text) if f is not None)
    except ValueError:
        return None

def missing_tokens(src:str, dst:str)->list:
    lost:list = []
    for t in set(PROTECT.findall(src)):
        inner:str = t[1:-1] if len(t) > 2 and t[0] == t[-1] == '"' else t
        if dst.count(inner) < src.count(inner):
            lost.append(t)
    return sorted(lost)

def broken_reason(src:str, dst:str)->str:
    if src.strip() and not dst.strip():
        return 'is empty'
    lost:list = missing_tokens(src, dst)
    return f'lacks {" ".join(lost)}' if lost else ''

def protect(text:str)->tuple:
    tokens:list = []
    def repl(m)->str:
        tokens.append(m.group(0))
        return f'\u27e6{len(tokens)-1}\u27e7'
    return PROTECT.sub(repl, text), tokens

def restore(text:str, tokens:list)->Optional[str]:
    seen:list = []
    def repl(m)->str:
        idx:int = int(m.group(1) or m.group(2))
        seen.append(idx)
        return f'\x00{idx}\x00'
    out:str = MARKER.sub(repl, text)
    if sorted(seen) != list(range(len(tokens))):
        return None
    out = re.sub(r' {2,}', ' ', STRAY.sub('', out))
    return re.sub(r'\x00(\d+)\x00', lambda m: tokens[int(m.group(1))], out)

def mymemory(text:str, code:str)->str:
    params:dict = {'q': text, 'langpair': f'en|{code}'}
    if EMAIL:
        params['de'] = EMAIL
    url:str = 'https://api.mymemory.translated.net/get?'+urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data:dict = json.loads(resp.read().decode('utf-8'))
            translated:str = (data.get('responseData') or {}).get('translatedText') or ''
            if data.get('quotaFinished') or str(data.get('responseStatus')) == '429' or translated.startswith('MYMEMORY WARNING'):
                raise QuotaExceeded(data.get('responseDetails') or translated or 'MyMemory daily quota reached')
            if str(data.get('responseStatus')) == '403':
                raise LangRejected(data.get('responseDetails') or translated or 'invalid language pair')
            if str(data.get('responseStatus')) == '200' and translated:
                return translated
            print(f'  status {data.get("responseStatus")} for {code}, retry {attempt+1}', file=sys.stderr)
        except (QuotaExceeded, LangRejected):
            raise
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise QuotaExceeded('HTTP 429 from MyMemory') from e
            print(f'  retry {attempt+1} for {code}: {e}', file=sys.stderr)
        except Exception as e:
            print(f'  retry {attempt+1} for {code}: {e}', file=sys.stderr)
        time.sleep(2*(attempt+1))
    raise RuntimeError(f'MyMemory failed for lang={code}')

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

def mt(text:str, code:str)->str:
    parts:list = []
    for chunk in chunk_text(text):
        parts.append(mymemory(chunk, code))
        time.sleep(THROTTLE)
    return html.unescape(('' if code in NO_SPACE_JOIN else ' ').join(parts)).replace('\n', ' ')

def translate_segments(body:str, code:str)->str:
    out:list = []
    pos:int = 0
    for m in [*PROTECT.finditer(body), None]:
        segment:str = body[pos:m.start() if m else len(body)]
        s = re.match(r'^(\s*)(.*?)(\s*)$', segment, re.S)
        if re.search(r'[A-Za-z]', s.group(2)):
            segment = s.group(1)+mt(s.group(2), code).strip()+s.group(3)
        out.append(segment)
        if m:
            out.append(m.group(0))
            pos = m.end()
    return ''.join(out)

def translate_line(line:str, code:str)->tuple:
    m = re.match(r'^(\s*)(.*?)(\s*)$', line, re.S)
    lead, body, trail = m.group(1), m.group(2), m.group(3)
    if not body:
        return line, False
    protected, tokens = protect(body)
    if not re.search(r'[A-Za-z]', MARKER.sub('', protected)):
        return line, False
    if not tokens:
        return lead+mt(protected, code).strip()+trail, False
    restored:Optional[str] = None
    if marker_fails.get(code, 0) < MARKER_MAX_FAILS:
        translated:str = mt(protected, code)
        restored = restore(translated, tokens)
        if restored is None:
            marker_fails[code] = marker_fails.get(code, 0)+1
            print(f'  {code}: markers lost, MT returned: {translated[:120]}', file=sys.stderr)
            if marker_fails[code] == MARKER_MAX_FAILS:
                print(f'  {code}: {MARKER_MAX_FAILS} marker failures in a row, segment mode only for the rest of this run', file=sys.stderr)
        else:
            marker_fails[code] = 0
    if restored is None:
        return lead+translate_segments(body, code).strip()+trail, True
    return lead+restored.strip()+trail, False

def translate_value(text:str, code:str)->tuple:
    out:list = []
    segmented:bool = False
    for line in text.split('\n'):
        translated, seg = translate_line(line, code)
        segmented = segmented or seg
        out.append(translated)
    result:str = '\n'.join(out)
    if text.strip() and not result.strip():
        return None, 'empty translation'
    if format_fields(result) != format_fields(text):
        return None, 'format placeholders differ from English'
    lost:list = missing_tokens(text, result)
    if lost:
        return None, f'reserved token(s) missing: {" ".join(lost)}'
    return result, 'segment mode, review wording' if segmented else ''

def main()->int:
    parser = argparse.ArgumentParser(description='Add and translate keys of lib/lang/legends_eng.py missing from the other legends_<iso3>.py files')
    parser.add_argument('--check', action='store_true', help='only report out-of-sync files, no network, no write, exit 1 if any')
    parser.add_argument('--langs', nargs='+', metavar='ISO3', help='translate only these languages (default: all)')
    parser.add_argument('--redo', nargs='+', metavar='KEY', default=[], help='retranslate these keys in the selected languages')
    parser.add_argument('--fix', action='store_true', help='retranslate existing keys that are empty or whose reserved tokens differ from English in the selected languages')
    args = parser.parse_args()
    eng:dict = load_assign(ENG_FILE, 'legends')
    baseline:Optional[dict] = load_assign(BASELINE, 'legends') if BASELINE.exists() else None
    changed:set = {k for k, v in eng.items() if baseline is not None and k in baseline and baseline[k] != v}
    iso1:dict = load_assign(INIT_FILE, 'legends_iso1')
    targets:dict = {iso3: MT_CODES.get(iso3, code) for code, iso3 in iso1.items() if iso3 != 'eng'}
    for path in sorted(LANG_DIR.glob('legends_*.py')):
        iso3:str = path.stem.split('_', 1)[1]
        if iso3 != 'eng' and iso3 not in targets:
            print(f'[{iso3}] {path.name} not declared in legends_iso1, skipped')
    selected:list = list(targets)
    if args.langs:
        unknown:list = [l for l in args.langs if l not in targets]
        if unknown:
            print(f'unknown language(s): {", ".join(unknown)} (known: {", ".join(targets)})', file=sys.stderr)
            return 2
        selected = [l for l in targets if l in args.langs]
    unknown_keys:list = [k for k in args.redo if k not in eng]
    if unknown_keys:
        print(f'unknown key(s): {", ".join(unknown_keys)}', file=sys.stderr)
        return 2
    if baseline is None:
        print(f'{len(eng)} English key(s), no baseline yet: changed English values cannot be detected on this run')
    else:
        print(f'{len(eng)} English key(s), {len(changed)} changed since baseline')
    state:dict = {}
    out_of_sync:int = 0
    for iso3 in targets:
        path:Path = LANG_DIR / f'legends_{iso3}.py'
        tr:dict = load_assign(path, 'legends') if path.exists() else {}
        orphans:list = [k for k in tr if k not in eng]
        broken:list = [k for k in eng if k in tr and broken_reason(eng[k], tr[k])]
        stale:list = [k for k in eng if k in tr and (k in changed or (iso3 in selected and (k in args.redo or (args.fix and k in broken))) or format_fields(tr[k]) != format_fields(eng[k]))]
        broken = [k for k in broken if k not in stale]
        missing:list = [k for k in eng if k not in tr]
        state[iso3] = dict(path=path, tr=tr, orphans=orphans, stale=stale, missing=missing, broken=broken, exists=path.exists())
        if (orphans or stale or missing or broken or not path.exists()) and iso3 in selected:
            out_of_sync += 1
            print(f'[{iso3}] {"file missing, " if not path.exists() else ""}{len(missing)} missing, {len(stale)} stale, {len(broken)} broken, {len(orphans)} orphan(s)')
            if args.check:
                for label, keys in (('missing', missing), ('stale', stale), ('orphan', orphans)):
                    if keys and path.exists():
                        print(f'[{iso3}]   {label}: {", ".join(keys)}')
                for k in broken:
                    print(f'[{iso3}]   broken: {k} {broken_reason(eng[k], tr[k])}')
    if args.check:
        print('all legends files in sync' if not out_of_sync else f'{out_of_sync} file(s) out of sync')
        return 1 if out_of_sync else 0
    for iso3, s in state.items():
        if s['orphans'] or s['stale']:
            drop:set = set(s['orphans']) | set(s['stale'])
            s['tr'] = {k: v for k, v in s['tr'].items() if k not in drop}
            s['missing'] = [k for k in eng if k not in s['tr']]
            write_legends(s['path'], s['tr'])
            print(f'[{iso3}] removed {len(s["orphans"])} orphan(s), {len(s["stale"])} stale key(s) queued for retranslation')
    if baseline != eng:
        BASELINE.write_text(dump_legends(eng), encoding='utf-8')
        print('baseline updated')
    failed:dict = {}
    aborted:Optional[str] = None
    for iso3 in selected:
        s:dict = state[iso3]
        if not s['missing'] and s['exists']:
            continue
        code:str = targets[iso3]
        known:dict = {eng[k]: v for k, v in s['tr'].items() if k in eng and not broken_reason(eng[k], v)}
        done:int = 0
        rejected:Optional[str] = None
        for key in s['missing']:
            value:str = eng[key]
            translated:Optional[str] = known.get(value)
            reason:str = ''
            if translated is None:
                try:
                    translated, reason = translate_value(value, code)
                except QuotaExceeded as e:
                    aborted = str(e)
                    break
                except LangRejected as e:
                    rejected = str(e)
                    break
                except RuntimeError as e:
                    translated, reason = None, str(e)
            if translated is None:
                failed.setdefault(iso3, []).append(key)
                print(f'[{iso3}] ! {key}: {reason}')
                continue
            s['tr'][key] = translated
            known[value] = translated
            done += 1
            print(f'[{iso3}] + {key}'+(f' ({reason})' if reason else ''))
        write_legends(s['path'], {k: s['tr'][k] for k in eng if k in s['tr']})
        print(f'[{iso3}] {done} key(s) added')
        if rejected:
            failed[iso3] = [k for k in s['missing'] if k not in s['tr']]
            print(f'[{iso3}] skipped, MyMemory rejected "{code}": {rejected} (map {iso3} to another code in MT_CODES)')
        if aborted:
            break
    if aborted:
        print(f'stopped: {aborted}. Run again later (or set MYMEMORY_EMAIL for a higher quota), remaining keys stay missing and fall back to English', file=sys.stderr)
        return 1
    if failed:
        for iso3, keys in failed.items():
            print(f'[{iso3}] not translated: {", ".join(keys)}', file=sys.stderr)
        return 1
    broken_left:int = sum(len(state[iso3]['broken']) for iso3 in selected)
    if broken_left:
        print(f'{broken_left} existing translation(s) are empty or lack reserved tokens from English, list them with --check, retranslate with --fix', file=sys.stderr)
        return 1
    print('legends files in sync')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except RuntimeError as e:
        print(f'error: {e}', file=sys.stderr)
        sys.exit(2)