import os, re, sys, json, shutil, argparse, statistics, subprocess, unicodedata
from pathlib import Path
from typing import Any, Optional
root_dir = str(Path(__file__).resolve().parents[1])
python_env_dir = os.path.join(root_dir, 'python_env')
python_env_exec = os.path.join(python_env_dir, 'Scripts', 'python.exe') if sys.platform == 'win32' else os.path.join(python_env_dir, 'bin', 'python')
# runs on e2a's python_env (torch, transformers, uroman, pykakasi): started by another interpreter, it starts again with python_env's
if os.path.isfile(python_env_exec) and os.path.normcase(os.path.realpath(sys.prefix)) != os.path.normcase(os.path.realpath(python_env_dir)) and not os.environ.get('E2A_CHECK_AUDIOBOOK_HALLUCINATIONS'):
    try:
        sys.exit(subprocess.run([python_env_exec, os.path.abspath(__file__), *sys.argv[1:]], env={**os.environ, 'E2A_CHECK_AUDIOBOOK_HALLUCINATIONS': '1'}).returncode)
    except KeyboardInterrupt:
        sys.exit(130)
examples = '''examples:
  check_audiobook_hallucinations.py audiobooks/cli/book.m4b
  check_audiobook_hallucinations.py audiobooks/cli/book.m4b --language fra --device cuda
  check_audiobook_hallucinations.py audiobooks/cli'''
description = '''Report the sentences of an e2a audiobook that do not say their text: babble, a word or a phrase
said twice or skipped, mumble before or after the text, a sentence too long or too short for its text.
Report only: the audiobook is not changed.
It reads the .vtt e2a writes beside each audiobook (one cue per sentence), transcribes each sentence with
facebook/mms-1b-all (1162 languages, downloaded into models/tts on first use) and compares the letters of
both texts, romanized (uroman, pykakasi for Japanese). The limits come from the book itself, from the
medians of all its sentences: names or a hard text raise them for the whole book, a hallucination stands out.
Each flagged sentence is printed as soon as it is found, all of them in a table at the end, by their block and
sentence numbers as in e2a (from 0). Every sentence with its problem, its text, what was heard and its measures
is saved in <audiobook>.hallucinations.json.'''
parser = argparse.ArgumentParser(prog='check_audiobook_hallucinations.py', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=examples, description=description)
parser.add_argument('audiobooks', nargs='+', help='Audiobook files (m4b, mp3, flac...) with their .vtt beside them, or folders holding them')
parser.add_argument('-l', '--language', default='', help="Language spoken, e2a ISO-639-3 code (default: the audiobook's language tag; set it for a translated book, its tag keeps the ebook's language)")
parser.add_argument('--vtt', default='', help='Subtitles of the audiobook, single audiobook only (default: <audiobook>.vtt)')
parser.add_argument('-o', '--output', default='', help='JSON report, single audiobook only (default: <audiobook>.hallucinations.json beside it)')
parser.add_argument('--device', choices=['auto', 'cpu', 'cuda', 'rocm', 'xpu', 'mps', 'jetson'], default='auto', help='Device the speech recognizer runs on, named as in e2a (default: the one e2a was installed for, cpu when it cannot be used)')
args = parser.parse_args()
start_dir = os.getcwd()
os.chdir(root_dir)
sys.path.insert(0, root_dir)

# limits: max(floor, factor * the book's median), default when the book has fewer than min_samples sentences to measure.
# cer: distance over the text length; burst: longest run of wrong letters (babble or a skipped phrase inside a long
# sentence barely moves its CER); edge: extra letters heard before the text starts or after it ends; length: seconds per
# letter. Sentences under min_letters (one-word lines) or with digits (read in unknown words) get the length check only.
# missing: missing_letters or more letters of the text not heard within missing_window letters (a skipped word), a fixed
# limit, confirmed on a short window of the audio around them (missing_seconds, one after the other): the recognizer drops
# a word at the start or the end of a long sentence it hears in a short one. Measured: every missing word of 5 letters or
# more caught (19/19 XTTS sentences with a word left out, English and German), 0 of 3-4 letters (the recognizer drops
# short words in good audio too), 5 good sentences flagged in 636 (15 languages, 3 of them Japanese)
settings = dict(
    asr_model='facebook/mms-1b-all', samplerate=16000, segment_gap=0.6, window=300.0,
    min_samples=20, min_letters=10, rate_min_letters=20,
    cer_factor=2.5, cer_floor=0.5, cer_default=0.6,
    burst_factor=3.0, burst_floor=9, burst_default=9,
    edge_factor=3.0, edge_floor=3, edge_default=3,
    missing_letters=5, missing_window=8, missing_seconds=(3.0, 5.0),
    length_factor=2.0, length_slack=1.5, length_default_rate=0.25, length_default_slack=4.0, short_factor=0.35,
    lang_alias=dict(zho='cmn', nor='nob'),
)
# e2a device -> torch device: ROCm and Jetson builds of torch run through torch.cuda. Half precision on GPUs but MPS
torch_devices = dict(cpu='cpu', cuda='cuda', rocm='cuda', jetson='cuda', xpu='xpu', mps='mps')
half_devices = ['cuda', 'xpu']
approximate_note = 'no block numbers in these subtitles (audiobook made before e2a wrote them): blocks counted from the chapters, off after a block left out of the conversion'
audio_exts = ['.m4b', '.m4a', '.mp4', '.mp3', '.aac', '.flac', '.wav', '.ogg', '.oga', '.opus', '.webm', '.mka', '.mkv', '.mov']

def to_abs(path:str)->str:
    # from where the script was started, also once it runs from e2a's root
    return os.path.abspath(os.path.join(start_dir, os.path.expanduser(path)))

def find_audiobooks(paths:list[str])->list[tuple[str, str]]:
    # (audiobook, vtt) pairs: a folder gives every audiobook with its .vtt beside it (one per part with output_split)
    found = []
    for path in map(to_abs, paths):
        if os.path.isdir(path):
            for name in sorted(os.listdir(path)):
                file = os.path.join(path, name)
                vtt = os.path.splitext(file)[0] + '.vtt'
                if os.path.splitext(name)[1].lower() in audio_exts and os.path.isfile(vtt):
                    found.append((file, vtt))
        elif os.path.isfile(path):
            vtt = to_abs(args.vtt) if args.vtt else os.path.splitext(path)[0] + '.vtt'
            if not os.path.isfile(vtt):
                print(f'{path}: no subtitles ({vtt}), skipped')
                continue
            found.append((path, vtt))
        else:
            print(f'{path}: not found, skipped')
    return found

def parse_time(stamp:str)->float:
    seconds = 0.0
    for part in stamp.strip().replace(',', '.').split(':'):
        seconds = seconds * 60 + float(part)
    return seconds

def parse_vtt(path:str)->list[dict]:
    # sentence cues, named "block <block index> sentence <sentence index>" by e2a (none in older audiobooks). Interlude
    # cues ("interlude <block index>") are music, left out
    cues = []
    with open(path, encoding='utf-8-sig') as f:
        blocks = f.read().replace('\r\n', '\n').split('\n\n')
    for block in blocks:
        lines = [line for line in block.split('\n') if line.strip()]
        for i, line in enumerate(lines):
            if '-->' in line:
                cue_id = lines[i - 1].strip() if i else ''
                if re.match(r'^interlude \d+$', cue_id):
                    break
                ids = re.match(r'^block (\d+) sentence (\d+)$', cue_id)
                start, end = line.split('-->')[:2]
                cues.append(dict(start=parse_time(start), end=parse_time(end.split()[0]), text=' '.join(lines[i + 1:]).strip(),
                    block=int(ids.group(1)) if ids else None, sentence=int(ids.group(2)) if ids else None))
                break
    return cues

def number_from_chapters(cues:list, chapters:list)->None:
    # older audiobooks: one chapter per block, its cues counted (a line of tags only, [pause] alone, has its own empty
    # cue, so the sentence numbers hold). The block numbers are off after a block e2a skipped (keep unchecked)
    import bisect
    starts = sorted(float(c['start_time']) for c in chapters)
    counts = {}
    for cue in cues:
        block = max(0, bisect.bisect_right(starts, cue['start'] + 0.001) - 1) if starts else 0
        cue['block'], cue['sentence'] = block, counts.get(block, 0)
        counts[block] = cue['sentence'] + 1

def probe(path:str)->dict:
    out = subprocess.run([shutil.which('ffprobe'), '-v', 'error', '-show_chapters', '-show_format', '-show_streams', '-select_streams', 'a:0', '-of', 'json', path], capture_output=True, text=True, check=True).stdout
    return json.loads(out)

def tag_language(info:dict)->str:
    # e2a tags the audiobook with the ebook's language (ISO-639-3, sometimes ISO-639-1)
    tags = {k.lower(): v for k, v in (info.get('format', {}).get('tags') or {}).items()}
    code = str(tags.get('language') or tags.get('lang') or '').strip().lower()
    if not code:
        # the audio stream's own tag, 'und' when nobody set it
        streams = [str((s.get('tags') or {}).get('language', '')).lower() for s in info.get('streams', [])]
        code = next((c for c in streams if c and c != 'und'), '')
    if len(code) == 2:
        try:
            from iso639 import Lang
            code = Lang(code).pt3
        except Exception:
            pass
    return code

def decode(path:str, start:float, duration:float)->Any:
    # mono float32 at the recognizer's rate, straight from ffmpeg
    import numpy as np
    cmd = [shutil.which('ffmpeg'), '-nostdin', '-v', 'error', '-ss', f'{start:.3f}', '-t', f'{duration:.3f}', '-i', path, '-ac', '1', '-ar', str(settings['samplerate']), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32)

def installed_device()->str:
    # the device e2a's installer set python_env up for, cpu when unknown or vulkan (torch has no vulkan device)
    try:
        with open(os.path.join(root_dir, '.device_info.json'), encoding='utf-8') as f:
            name = str(json.load(f).get('name', 'cpu'))
    except Exception:
        name = 'cpu'
    return name if name in torch_devices else 'cpu'

def device_available(name:str)->bool:
    import torch
    try:
        if torch_devices[name] == 'cuda':
            return torch.cuda.is_available()
        if name == 'xpu':
            # probed only when xpu is asked for or installed: on some Intel GPUs the probe itself crashes
            return hasattr(torch, 'xpu') and torch.xpu.is_available()
        if name == 'mps':
            return torch.backends.mps.is_available()
    except Exception:
        return False
    return True

def pick_device(requested:str)->str:
    name = installed_device() if requested == 'auto' else requested
    if name != 'cpu' and not device_available(name):
        print(f'{name}: not available with this python_env, the speech recognizer runs on cpu')
        return 'cpu'
    return name

class Checker:

    def __init__(self, device:str)->None:
        import torch
        self.device = torch_devices[device]
        self.dtype = torch.float16 if self.device in half_devices else torch.float32
        self.language = None
        self.asr_language = None
        self.model = None
        self.processor = None
        self.uroman = None
        self.kakasi = None
        self.mms_languages = None

    def find_asr_language(self, code:str)->Optional[str]:
        # MMS language for an e2a code: the code itself, its script variant (srp-script_cyrillic, ...) matched on the
        # script of language_mapping, or one of the languages of a macrolanguage (aze -> azj-script_latin)
        if self.mms_languages is None:
            from huggingface_hub import hf_hub_download
            from lib.conf import tts_dir
            with open(hf_hub_download(settings['asr_model'], 'vocab.json', cache_dir=tts_dir), encoding='utf-8') as f:
                self.mms_languages = list(json.load(f).keys())
        alias = settings['lang_alias'].get(code, code)
        if alias in self.mms_languages:
            return alias
        candidates = [alias]
        try:
            from iso639 import Lang
            candidates += [lang.pt3 for lang in Lang(alias).individuals()]
        except Exception:
            pass
        variants = [lang for c in candidates for lang in self.mms_languages if lang == c or lang.startswith(f'{c}-')]
        if not variants:
            return None
        from lib.conf_lang import language_mapping
        script = language_mapping.get(code, {}).get('script', '')
        return next((lang for lang in variants if script and f'script_{script}' in lang), variants[0])

    def set_language(self, code:str)->None:
        self.language = code
        self.asr_language = self.find_asr_language(code)
        if self.asr_language is None:
            return
        import torch
        from transformers import Wav2Vec2ForCTC, AutoProcessor
        from lib.conf import tts_dir
        if self.model is None:
            print(f"Loading {settings['asr_model']}…")
            self.processor = AutoProcessor.from_pretrained(settings['asr_model'], target_lang=self.asr_language, cache_dir=tts_dir)
            # the head is sized per language, the one in model.safetensors is english: replaced by the adapter's
            self.model = Wav2Vec2ForCTC.from_pretrained(settings['asr_model'], target_lang=self.asr_language, ignore_mismatched_sizes=True, cache_dir=tts_dir)
            self.model.eval()
            if self.device != 'cpu':
                try:
                    self.model = self.model.to(self.device, dtype=self.dtype)
                except RuntimeError as e:
                    # not enough memory on the GPU most of the time: slower, but the check goes on
                    print(f'{self.device}: {e}, the speech recognizer runs on cpu')
                    self.device, self.dtype = 'cpu', torch.float32
                    self.model = self.model.float().to('cpu')
            print(f'Speech recognizer on {self.device} ({str(self.dtype).removeprefix("torch.")})')
        else:
            self.processor.tokenizer.set_target_lang(self.asr_language)
            self.model.load_adapter(self.asr_language)

    def romanize(self, text:str)->str:
        if self.language == 'jpn':
            # uroman reads kanji with their chinese readings
            if self.kakasi is None:
                import pykakasi
                self.kakasi = pykakasi.kakasi()
            return ' '.join(item['hepburn'] for item in self.kakasi.convert(text))
        if self.uroman is None:
            import uroman
            self.uroman = uroman.Uroman()
        return self.uroman.romanize_string(text, lcode=self.language)

    def letters(self, text:str)->str:
        # what both sides are compared on: romanized letters only, lower case, no accents, no spaces
        import regex as re
        if not any(c.isalpha() for c in text):
            return ''
        return re.sub(r'[^\p{L}]+', '', unicodedata.normalize('NFKD', self.romanize(text).casefold()))

    def distances(self, ref:str, hyp:str)->list:
        # levenshtein table: dist[i][j] between ref[:i] and hyp[:j]
        rows, cols = len(ref), len(hyp)
        dist = [list(range(cols + 1))] + [[i] + [0] * cols for i in range(1, rows + 1)]
        for i in range(1, rows + 1):
            prev, cur, ref_char = dist[i - 1], dist[i], ref[i - 1]
            for j in range(1, cols + 1):
                cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ref_char != hyp[j - 1]))
        return dist

    def tail_extra(self, last_row:list)->int:
        # extra letters heard after the text ends, as many as an optimal alignment allows: a word said twice at the
        # end ("fourteen fourteen") is aligned either way at the same cost, the repeat counts as extra
        total = last_row[-1]
        return max(k for k in range(len(last_row)) if last_row[len(last_row) - 1 - k] + k == total)

    def compare(self, ref:str, hyp:str)->dict:
        # levenshtein alignment of the letters: the CER (above 1.0 when the take says more than the text), the longest
        # burst of errors in a row (a single chance match inside not ending it), the extra letters heard before the
        # text starts or after it ends (a misheard name sits inside the text, extra letters at an edge can only be
        # speech the text does not have) and the window of the text with the most letters not heard (a skipped word:
        # missing letters, where a misheard word has wrong ones)
        import regex as re
        if not ref:
            return dict(cer=0.0, burst=0, edge=0, missing=0, missing_letters='')
        rows, cols = len(ref), len(hyp)
        dist = self.distances(ref, hyp)
        ops = []
        i, j = rows, cols
        while i > 0 or j > 0:
            if i > 0 and j > 0 and dist[i][j] == dist[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]):
                ops.append('M' if ref[i - 1] == hyp[j - 1] else 'S')
                i, j = i - 1, j - 1
            elif j > 0 and dist[i][j] == dist[i][j - 1] + 1:
                ops.append('I')
                j -= 1
            else:
                ops.append('D')
                i -= 1
        bursts = re.findall(r'[SID](?:[SID]|M(?=[SID]))*', ''.join(reversed(ops)))
        # leading extra letters: the same on both texts reversed
        edge = max(self.tail_extra(dist[rows]), self.tail_extra(self.distances(ref[::-1], hyp[::-1])[rows]))
        marks = [op == 'D' for op in reversed(ops) if op != 'I']
        window = settings['missing_window']
        missing, start = 0, 0
        for k in range(max(1, len(marks) - window + 1)):
            count = sum(marks[k:k + window])
            if count > missing:
                missing, start = count, k
        spots = [k for k in range(start, min(len(marks), start + window)) if marks[k]]
        return dict(cer=dist[rows][cols] / rows, burst=max((len(b.replace('M', '')) for b in bursts), default=0), edge=edge,
            missing=missing, missing_letters=ref[spots[0]:spots[-1] + 1] if spots else '', missing_at=(spots[0] + spots[-1] + 1) / 2 / rows if spots else 0.0)

    def heard_in(self, pattern:str, text:str)->bool:
        # pattern found in text, a few letters off at most: edit distance to its best matching part of text
        prev = [0] * (len(text) + 1)
        for i, p in enumerate(pattern, 1):
            cur = [i] + [0] * len(text)
            for j, t in enumerate(text, 1):
                cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (p != t))
            prev = cur
        return min(prev) <= max(1, len(pattern) // 4)

    def missing_heard(self, audio:Any, at:float, letters:str)->bool:
        # the letters the whole sentence missed, looked for in a short window of the audio around their place
        samplerate = settings['samplerate']
        duration = len(audio) / samplerate
        for seconds in settings['missing_seconds']:
            start = max(0.0, min(at * duration - seconds / 2, duration - seconds))
            heard = self.transcribe(audio[int(start * samplerate):int((start + seconds) * samplerate)])
            if self.heard_in(letters, self.letters(heard)):
                return True
        return False

    def speech_segments(self, audio:Any)->list:
        # the sentence cut at its long silences ([pause], [break]): MMS on the whole sentence drops a short part followed
        # by a long silence, a chapter title before its [pause] in most languages, while it hears it on its own
        import numpy as np
        frame = int(settings['samplerate'] * 0.02)
        count = len(audio) // frame
        if count == 0:
            return [audio]
        rms = np.sqrt(np.mean(audio[:count * frame].reshape(count, frame) ** 2, axis=1))
        silent = rms < max(0.002, 0.03 * float(rms.max()))
        gap = int(settings['segment_gap'] / 0.02)
        pad = int(0.1 / 0.02)
        segments = []
        start = None
        run = 0
        for i, quiet in enumerate(silent):
            if not quiet:
                if start is None:
                    start = i
                run = 0
            elif start is not None:
                run += 1
                if run >= gap:
                    segments.append((max(0, start - pad), i - run + 1 + pad))
                    start = None
                    run = 0
        if start is not None:
            segments.append((max(0, start - pad), count))
        return [audio[a * frame:b * frame] for a, b in segments] or [audio]

    def transcribe(self, audio:Any, segmented:bool=False)->str:
        import torch
        texts = []
        for segment in (self.speech_segments(audio) if segmented else [audio]):
            if len(segment) < settings['samplerate'] // 10:
                continue
            inputs = self.processor(segment, sampling_rate=settings['samplerate'], return_tensors='pt')
            values = inputs['input_values'].to(next(self.model.parameters()).device, dtype=next(self.model.parameters()).dtype)
            with torch.inference_mode():
                logits = self.model(values).logits
            texts.append(self.processor.decode(torch.argmax(logits, dim=-1)[0].cpu()))
        return ' '.join(text for text in texts if text)

def median_sorted(values:list)->float:
    middle = len(values) // 2
    return values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2

def limit(values:list, name:str)->float:
    # values kept sorted (bisect.insort): the median of a growing book stays cheap
    if len(values) < settings['min_samples']:
        return settings[f'{name}_default']
    return max(settings[f'{name}_floor'], settings[f'{name}_factor'] * median_sorted(values))

def current_limits(samples:dict)->dict:
    return dict(cer=limit(samples['cer'], 'cer'), burst=limit(samples['burst'], 'burst'), edge=limit(samples['edge'], 'edge'),
        rate=median_sorted(samples['rate']) if len(samples['rate']) >= settings['min_samples'] else None)

def badness(r:dict)->float:
    return r['cer'] + (r['burst'] + r['edge'] + r['missing']) / r['letters']

def missing_suspect(r:dict)->bool:
    # letters not heard, not yet found in a short window either
    return r['cer'] is not None and r['missing'] >= settings['missing_letters'] and r.get('missing_confirmed') is not False

def asr_failing(r:dict, limits:dict)->bool:
    return r['cer'] is not None and (r['edge'] > limits['edge'] or r['burst'] > limits['burst'] or r['cer'] > limits['cer'] or missing_suspect(r))

def measure(r:dict, heard:str, measures:dict)->None:
    r.update(heard=heard, missing_confirmed=None, **measures)

def retry_segmented(checker:Checker, r:dict, audio:Any)->None:
    # a failing sentence with long silences, again part by part, the better of both kept. Babble is in the audio, both
    # hear it; MMS drops a short part before a long silence (a chapter title before its [pause]) on the whole one only
    heard = checker.transcribe(audio, segmented=True)
    parts = dict(checker.compare(r['ref'], checker.letters(heard)), letters=r['letters'])
    if badness(parts) < badness(r):
        measure(r, heard, {k: v for k, v in parts.items() if k != 'letters'})
    r['segmented'] = True

def confirm_missing(checker:Checker, r:dict, audio:Any)->None:
    if missing_suspect(r) and r.get('missing_confirmed') is None:
        r['missing_confirmed'] = not checker.missing_heard(audio, r['missing_at'], r['missing_letters'])

def verdict(r:dict, limits:dict)->Optional[str]:
    # the reason a sentence is flagged, None when it is fine
    length_letters = r['letters'] + 4 * r['digits']
    if not length_letters:
        return None
    if limits['rate'] is not None:
        longest = limits['rate'] * length_letters * settings['length_factor'] + settings['length_slack']
        shortest = max(0.1, limits['rate'] * length_letters * settings['short_factor']) if length_letters >= settings['rate_min_letters'] else 0.1
    else:
        longest = length_letters * settings['length_default_rate'] + settings['length_default_slack']
        shortest = 0.1
    if r['duration'] > longest:
        return f"too long for its text ({r['duration']:.1f}s, {longest:.1f}s at most)"
    if r['duration'] < shortest:
        return f"too short for its text ({r['duration']:.1f}s, {shortest:.1f}s at least)"
    if r['cer'] is None:
        return None
    if r['edge'] > limits['edge']:
        return f"extra speech before or after its text ({r['edge']} letters, {limits['edge']:.0f} at most)"
    if r['burst'] > limits['burst']:
        return f"part of it does not match its text ({r['burst']} letters in a row, {limits['burst']:.0f} at most)"
    if r['missing'] >= settings['missing_letters'] and r.get('missing_confirmed'):
        return f"words missing from the audio ({r['missing']} letters not heard: {r['missing_letters']})"
    if r['cer'] > limits['cer']:
        return f"does not match its text (CER {r['cer']:.2f}, {limits['cer']:.2f} at most)"
    return None

def live_line(r:dict)->str:
    return f"  hallucination: block {r['block']}, sentence {r['sentence']}"

def check_audiobook(checker:Checker, audiobook:str, vtt:str)->Optional[dict]:
    import bisect
    import regex as re
    from tqdm import tqdm
    cues = parse_vtt(vtt)
    if not cues:
        print(f'{vtt}: no cues, skipped')
        return None
    info = probe(audiobook)
    chapters = info.get('chapters') or []
    language = args.language or tag_language(info)
    if not language:
        print(f'{audiobook}: no language tag, set it with --language')
        return None
    if language != checker.language:
        checker.set_language(language)
    asr = checker.asr_language is not None
    if not asr:
        print(f'{audiobook}: the speech recognizer does not know {language}, only the length of each sentence is checked')
    exact = all(cue['block'] is not None for cue in cues)
    if not exact:
        number_from_chapters(cues, chapters)
    records = []
    for cue in cues:
        ref = checker.letters(cue['text'])
        # a digit left in the text is read as a word or more: 4 letters for the length limits, kept out of the rate median
        digits = len(re.findall(r'\d', cue['text']))
        records.append(dict(block=cue['block'], sentence=cue['sentence'], start=round(cue['start'], 3), end=round(cue['end'], 3), duration=round(cue['end'] - cue['start'], 3),
            text=cue['text'], ref=ref, letters=len(ref), digits=digits,
            asr=asr and len(ref) >= settings['min_letters'] and not digits, heard=None, cer=None, burst=None, edge=None, missing=None,
            missing_letters=None, missing_confirmed=None, segments=1, reason=None))
    print(f'\n{audiobook}: {len(records)} sentences, language {language}' + (f' (recognizer {checker.asr_language})' if asr else ''))
    if not exact:
        print(f'  {approximate_note}')
    # every sentence on its own, a window of the audiobook decoded at a time. Each one is judged at once on the medians of
    # the sentences before it (printed), then all again on the medians of the whole book (the table at the end)
    samples = dict(cer=[], burst=[], edge=[], rate=[])
    with tqdm(total=len(records), unit='sentence', dynamic_ncols=True) as bar:
        i = 0
        while i < len(records):
            j = i
            while j + 1 < len(records) and records[j + 1]['end'] - records[i]['start'] <= settings['window']:
                j += 1
            window_start = records[i]['start']
            audio = decode(audiobook, window_start, records[j]['end'] - window_start) if any(r['asr'] for r in records[i:j + 1]) else None
            for r in records[i:j + 1]:
                limits = current_limits(samples)
                if r['asr'] and audio is not None:
                    segment = audio[round((r['start'] - window_start) * settings['samplerate']):round((r['end'] - window_start) * settings['samplerate'])]
                    heard = checker.transcribe(segment)
                    measure(r, heard, checker.compare(r['ref'], checker.letters(heard)))
                    r['segments'] = len(checker.speech_segments(segment))
                    # the medians are made of the whole-sentence measures
                    for key in ('cer', 'burst', 'edge'):
                        bisect.insort(samples[key], r[key])
                    if asr_failing(r, limits) and r['segments'] > 1:
                        retry_segmented(checker, r, segment)
                    confirm_missing(checker, r, segment)
                if r['letters'] >= settings['rate_min_letters'] and not r['digits']:
                    bisect.insort(samples['rate'], r['duration'] / r['letters'])
                reason = verdict(r, limits)
                if reason:
                    r['live'] = True
                    bar.write(live_line(r))
                bar.update(1)
            i = j + 1
    limits = current_limits(samples)
    for r in records:
        if not r.get('segmented') and r['segments'] > 1 and asr_failing(r, limits):
            audio = decode(audiobook, r['start'], r['duration'])
            retry_segmented(checker, r, audio)
            confirm_missing(checker, r, audio)
        r['reason'] = verdict(r, limits)
    cleared = sum(1 for r in records if r.get('live') and not r['reason'])
    for r in records:
        for key in ('ref', 'live', 'segmented', 'missing_at'):
            r.pop(key, None)
    return dict(audiobook=audiobook, vtt=vtt, language=language, asr_language=checker.asr_language, exact_numbers=exact, limits=limits,
        sentences=len(records), recognized=sum(1 for r in records if r['cer'] is not None),
        flagged=sum(1 for r in records if r['reason']), cleared=cleared, records=records)

def table(headers:list[str], rows:list[list[str]])->list[str]:
    widths = [max(len(str(cell)) for cell in column) for column in zip(headers, *rows)]

    def rule(left:str, middle:str, right:str)->str:
        return left + middle.join('─' * (w + 2) for w in widths) + right

    def line(cells:list)->str:
        return '│' + '│'.join(f' {str(cell):>{w}} ' for cell, w in zip(cells, widths)) + '│'

    return [rule('┌', '┬', '┐'), line(headers), rule('├', '┼', '┤')] + [line(row) for row in rows] + [rule('└', '┴', '┘')]

def print_report(report:dict)->None:
    limits = report['limits']
    rate = f"{limits['rate']:.3f}s per letter" if limits['rate'] else 'default'
    print(f"\n{report['audiobook']}")
    print(f"  {report['sentences']} sentences, {report['recognized']} checked by speech recognition, the others by their length only")
    print(f"  limits: CER {limits['cer']:.2f}, {limits['burst']:.0f} wrong letters in a row, {limits['edge']:.0f} extra letters at an edge, length {rate}")
    if not report['exact_numbers']:
        print(f'  {approximate_note}')
    # block and sentence as e2a numbers them (from 0); the problem, the text and what was heard are in the JSON
    rows = [[r['block'], r['sentence']] for r in report['records'] if r['reason']]
    if rows:
        print('\n'.join('  ' + line for line in table(['Block', 'Sentence'], rows)))
    flagged = f"  {report['flagged']} sentence{'s' if report['flagged'] != 1 else ''} flagged" if report['flagged'] else '  No sentence flagged'
    if report['cleared']:
        flagged += f" ({report['cleared']} printed during the check cleared by the limits of the whole book)"
    print(flagged)

def main()->int:
    found = find_audiobooks(args.audiobooks)
    if not found:
        return 1
    if len(found) > 1 and (args.vtt or args.output):
        print('--vtt and --output take a single audiobook')
        return 1
    checker = Checker(pick_device(args.device))
    for audiobook, vtt in found:
        report = check_audiobook(checker, audiobook, vtt)
        if report is None:
            continue
        print_report(report)
        output = to_abs(args.output) if args.output else os.path.splitext(audiobook)[0] + '.hallucinations.json'
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
        print(f'  report: {output}')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
