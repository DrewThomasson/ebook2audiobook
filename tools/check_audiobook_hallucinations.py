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
  check_audiobook_hallucinations.py audiobooks/cli --all'''
description = '''Report the sentences of an e2a audiobook that do not say their text: babble, a word or a phrase
said twice or skipped, mumble before or after the text, a sentence too long or too short for its text.
Report only: the audiobook is not changed.
It reads the .vtt e2a writes beside each audiobook (one cue per sentence), transcribes each sentence with
facebook/mms-1b-all (1162 languages, downloaded into models/tts on first use) and compares the letters of
both texts, romanized (uroman, pykakasi for Japanese). The limits come from the book itself, from the
medians of all its sentences: names or a hard text raise them for the whole book, a hallucination stands out.
The report is printed and saved as <audiobook>.check.json.'''
parser = argparse.ArgumentParser(prog='check_audiobook_hallucinations.py', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=examples, description=description)
parser.add_argument('audiobooks', nargs='+', help='Audiobook files (m4b, mp3, flac...) with their .vtt beside them, or folders holding them')
parser.add_argument('-l', '--language', default='', help="Language spoken, e2a ISO-639-3 code (default: the audiobook's language tag; set it for a translated book, its tag keeps the ebook's language)")
parser.add_argument('--vtt', default='', help='Subtitles of the audiobook, single audiobook only (default: <audiobook>.vtt)')
parser.add_argument('-o', '--output', default='', help='Report file, single audiobook only (default: <audiobook>.check.json beside it)')
parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto', help='Device the speech recognizer runs on (default: cuda when there is one)')
parser.add_argument('--all', action='store_true', help='Print every sentence with its measures, not only the flagged ones')
args = parser.parse_args()
start_dir = os.getcwd()
os.chdir(root_dir)
sys.path.insert(0, root_dir)

# limits: max(floor, factor * the book's median), default when the book has fewer than min_samples sentences to measure.
# cer: distance over the text length; burst: longest run of wrong letters (babble or a skipped phrase inside a long
# sentence barely moves its CER); edge: extra letters heard before the text starts or after it ends; length: seconds per
# letter. Sentences under min_letters (one-word lines) or with digits (read in unknown words) get the length check only
settings = dict(
    asr_model='facebook/mms-1b-all', samplerate=16000, segment_gap=0.6, window=300.0,
    min_samples=20, min_letters=10, rate_min_letters=20,
    cer_factor=2.5, cer_floor=0.5, cer_default=0.6,
    burst_factor=3.0, burst_floor=9, burst_default=9,
    edge_factor=3.0, edge_floor=3, edge_default=3,
    length_factor=2.0, length_slack=1.5, length_default_rate=0.25, length_default_slack=4.0, short_factor=0.35,
    lang_alias=dict(zho='cmn', nor='nob'),
)
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
    cues = []
    with open(path, encoding='utf-8-sig') as f:
        blocks = f.read().replace('\r\n', '\n').split('\n\n')
    for block in blocks:
        lines = [line for line in block.split('\n') if line.strip()]
        for i, line in enumerate(lines):
            if '-->' in line:
                start, end = line.split('-->')[:2]
                cues.append(dict(start=parse_time(start), end=parse_time(end.split()[0]), text=' '.join(lines[i + 1:]).strip()))
                break
    return cues

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

def chapter_at(chapters:list, seconds:float)->str:
    for chapter in chapters:
        if float(chapter['start_time']) <= seconds < float(chapter['end_time']):
            # e2a's chapter titles keep their [break] / [pause] tags
            title = re.sub(r'\[\s*/?\s*(?:break|pause|voice|emotion)[^\]]*\]', ' ', str((chapter.get('tags') or {}).get('title', '')))
            title = ' '.join(title.replace(' ;', ';').split())
            return title if len(title) <= 40 else title[:39] + '…'
    return ''

def decode(path:str, start:float, duration:float)->Any:
    # mono float32 at the recognizer's rate, straight from ffmpeg
    import numpy as np
    cmd = [shutil.which('ffmpeg'), '-nostdin', '-v', 'error', '-ss', f'{start:.3f}', '-t', f'{duration:.3f}', '-i', path, '-ac', '1', '-ar', str(settings['samplerate']), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32)

def stamp(seconds:float)->str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f'{int(h):02}:{int(m):02}:{s:06.3f}'

class Checker:

    def __init__(self, device:str)->None:
        self.device = device
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
            if self.device == 'cuda':
                self.model = self.model.half().to('cuda')
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

    def compare(self, ref:str, hyp:str)->tuple[float, int, int]:
        # levenshtein alignment of the letters: the CER (above 1.0 when the take says more than the text), the longest
        # burst of errors in a row (a single chance match inside not ending it) and the extra letters heard before the
        # text starts or after it ends: a misheard name sits inside the text, extra letters at an edge can only be
        # speech the text does not have
        import regex as re
        if not ref:
            return 0.0, 0, 0
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
        return dist[rows][cols] / rows, max((len(b.replace('M', '')) for b in bursts), default=0), edge

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

def limit(values:list, name:str)->float:
    if len(values) < settings['min_samples']:
        return settings[f'{name}_default']
    return max(settings[f'{name}_floor'], settings[f'{name}_factor'] * statistics.median(values))

def badness(r:dict)->float:
    return r['cer'] + (r['burst'] + r['edge']) / r['letters']

def check_audiobook(checker:Checker, audiobook:str, vtt:str)->Optional[dict]:
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
    records = []
    for n, cue in enumerate(cues):
        ref = checker.letters(cue['text'])
        # a digit left in the text is read as a word or more: 4 letters for the length limits, kept out of the rate median
        digits = len(re.findall(r'\d', cue['text']))
        records.append(dict(index=n + 1, start=round(cue['start'], 3), end=round(cue['end'], 3), duration=round(cue['end'] - cue['start'], 3),
            chapter=chapter_at(chapters, cue['start']), text=cue['text'], ref=ref, letters=len(ref), digits=digits,
            asr=asr and len(ref) >= settings['min_letters'] and not digits, heard=None, cer=None, burst=None, edge=None, segments=1, reason=None))
    # first pass: every sentence on its own, a window of the audiobook decoded at a time
    print(f'{audiobook}: {len(records)} sentences, language {language}' + (f' (recognizer {checker.asr_language})' if asr else ''))
    with tqdm(total=len(records), unit='sentence') as bar:
        i = 0
        while i < len(records):
            j = i
            while j + 1 < len(records) and records[j + 1]['end'] - records[i]['start'] <= settings['window']:
                j += 1
            window_start = records[i]['start']
            audio = decode(audiobook, window_start, records[j]['end'] - window_start) if any(r['asr'] for r in records[i:j + 1]) else None
            for r in records[i:j + 1]:
                if r['asr'] and audio is not None:
                    a = round((r['start'] - window_start) * settings['samplerate'])
                    b = round((r['end'] - window_start) * settings['samplerate'])
                    segment = audio[a:b]
                    r['heard'] = checker.transcribe(segment)
                    r['cer'], r['burst'], r['edge'] = checker.compare(r['ref'], checker.letters(r['heard']))
                    r['segments'] = len(checker.speech_segments(segment))
                bar.update(1)
            i = j + 1
    measured = [r for r in records if r['cer'] is not None]
    rates = [r['duration'] / r['letters'] for r in records if r['letters'] >= settings['rate_min_letters'] and not r['digits']]
    limits = dict(cer=limit([r['cer'] for r in measured], 'cer'), burst=limit([r['burst'] for r in measured], 'burst'), edge=limit([r['edge'] for r in measured], 'edge'))
    rate = statistics.median(rates) if len(rates) >= settings['min_samples'] else None
    limits['rate'] = rate

    def failing(r:dict)->bool:
        return r['cer'] is not None and (r['edge'] > limits['edge'] or r['burst'] > limits['burst'] or r['cer'] > limits['cer'])

    # second pass, failing sentences with long silences: again part by part, the better of both is kept. Babble is in
    # the audio, both hear it; MMS drops a short part before a long silence on the whole sentence only
    for r in [r for r in measured if failing(r) and r['segments'] > 1]:
        heard = checker.transcribe(decode(audiobook, r['start'], r['duration']), segmented=True)
        parts = dict(zip(('cer', 'burst', 'edge'), checker.compare(r['ref'], checker.letters(heard))), letters=r['letters'])
        if badness(parts) < badness(r):
            r.update(heard=heard, cer=parts['cer'], burst=parts['burst'], edge=parts['edge'])
    for r in records:
        length_letters = r['letters'] + 4 * r['digits']
        if not length_letters:
            continue
        if rate is not None:
            longest = rate * length_letters * settings['length_factor'] + settings['length_slack']
            shortest = max(0.1, rate * length_letters * settings['short_factor']) if length_letters >= settings['rate_min_letters'] else 0.1
        else:
            longest = length_letters * settings['length_default_rate'] + settings['length_default_slack']
            shortest = 0.1
        if r['duration'] > longest:
            r['reason'] = f"too long for its text ({r['duration']:.1f}s, {longest:.1f}s at most)"
        elif r['duration'] < shortest:
            r['reason'] = f"too short for its text ({r['duration']:.1f}s, {shortest:.1f}s at least)"
        elif r['cer'] is None:
            continue
        elif r['edge'] > limits['edge']:
            r['reason'] = f"extra speech before or after its text ({r['edge']} letters, {limits['edge']:.0f} at most)"
        elif r['burst'] > limits['burst']:
            r['reason'] = f"part of it does not match its text ({r['burst']} letters in a row, {limits['burst']:.0f} at most)"
        elif r['cer'] > limits['cer']:
            r['reason'] = f"does not match its text (CER {r['cer']:.2f}, {limits['cer']:.2f} at most)"
    flagged = [r for r in records if r['reason']]
    for r in records:
        del r['ref']
    return dict(audiobook=audiobook, vtt=vtt, language=language, asr_language=checker.asr_language, limits=limits,
        sentences=len(records), recognized=len(measured), flagged=len(flagged), records=records)

def print_report(report:dict)->None:
    limits = report['limits']
    rate = f"{limits['rate']:.3f}s per letter" if limits['rate'] else 'default'
    print(f"\n{report['audiobook']}\n  {report['sentences']} sentences, {report['recognized']} checked by speech recognition, the others by their length only")
    print(f"  limits: CER {limits['cer']:.2f}, {limits['burst']:.0f} wrong letters in a row, {limits['edge']:.0f} extra letters at an edge, length {rate}")
    for r in report['records']:
        if not (r['reason'] or args.all):
            continue
        measures = f"cer {r['cer']:.2f} burst {r['burst']} edge {r['edge']}" if r['cer'] is not None else 'length only'
        where = f"#{r['index']:<5} {stamp(r['start'])}  {r['chapter']}"
        print(f"  {'FLAGGED ' if r['reason'] else ''}{where}\n    {r['reason'] or measures}\n    text : {r['text']}")
        if r['heard'] is not None:
            print(f"    heard: {r['heard']}")
    print(f"  {report['flagged']} sentence(s) flagged")

def main()->int:
    import torch
    found = find_audiobooks(args.audiobooks)
    if not found:
        return 1
    if len(found) > 1 and (args.vtt or args.output):
        print('--vtt and --output take a single audiobook')
        return 1
    device = 'cuda' if args.device == 'cuda' or (args.device == 'auto' and torch.cuda.is_available()) else 'cpu'
    checker = Checker(device)
    for audiobook, vtt in found:
        report = check_audiobook(checker, audiobook, vtt)
        if report is None:
            continue
        print_report(report)
        output = to_abs(args.output) if args.output else os.path.splitext(audiobook)[0] + '.check.json'
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
        print(f'  report: {output}')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
