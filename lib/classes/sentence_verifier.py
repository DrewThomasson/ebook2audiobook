import os, sys, gc, json, statistics, unicodedata, regex as re

from collections import deque
from pathlib import Path
from typing import Any, Optional

from lib.conf import tts_dir, devices
from lib.conf_lang import language_mapping
from lib.conf_models import SML_TAG_PATTERN, default_verify_settings
from lib.classes.tts_engines.common.hf_download import hf_download
from lib.lang import legends

class SentenceVerifier:
    # --verify_sentences: checks a converted sentence against its text (settings and reasons in conf_models.py).
    # Every take gets the length check, then MMS transcribes it and the letters of both texts, romanized by uroman
    # (pykakasi for Japanese), are compared (CER). A failure here never stops the conversion: speech recognition is turned off, the length check
    # goes on and the take is kept

    def __init__(self, session:Any)->None:
        self.session = session
        self.settings = default_verify_settings
        self.levels = list(self.settings['levels'])
        translated = bool(session.get('translate_enabled') and session.get('translate'))
        self.language = session['translate'] if translated else session['language']
        self.cer_samples:deque = deque(maxlen=self.settings['samples_max'])
        self.burst_samples:deque = deque(maxlen=self.settings['samples_max'])
        self.edge_samples:deque = deque(maxlen=self.settings['samples_max'])
        self.rate_samples:deque = deque(maxlen=self.settings['samples_max'])
        self.flagged:list[dict] = []
        self.stats = dict(checked=0, failed=0, fixed_redraw=0, fixed_light=0, fixed_bare=0, flagged=0)
        self.model = None
        self.processor = None
        self.uroman = None
        self.kakasi = None
        self.device = devices['CPU']['proc']
        self.asr_enabled = True
        self.asr_language = self._asr_language(self.language)
        if self.asr_language is None and self.asr_enabled:
            self.asr_enabled = False
            msg = legends['msg_verify_unsupported'].format(language=language_mapping.get(self.language, {}).get('name', self.language))
            print(msg)

    def _disable_asr(self, error:Any)->None:
        # the length check goes on alone
        self.asr_enabled = False
        self.close()
        msg = legends['msg_verify_failed'].format(error=error)
        print(msg)

    def _asr_language(self, code:str)->Optional[str]:
        # MMS language for an e2a code: the code itself, its script variant (srp-script_cyrillic, ...) matched on the
        # script of language_mapping, or one of the languages of a macrolanguage (aze -> azj-script_latin)
        try:
            vocab_path = hf_download(None, '', repo_id=self.settings['asr_model'], filename='vocab.json', cache_dir=tts_dir)
            with open(vocab_path, 'r', encoding='utf-8') as f:
                mms_languages = list(json.load(f).keys())
        except Exception as e:
            self._disable_asr(e)
            return None
        code = self.settings['lang_alias'].get(code, code)
        if code in mms_languages:
            return code
        candidates = [code]
        try:
            from iso639 import Lang
            candidates += [lang.pt3 for lang in Lang(code).individuals()]
        except Exception:
            pass
        variants = [lang for c in candidates for lang in mms_languages if lang == c or lang.startswith(f'{c}-')]
        if not variants:
            return None
        script = language_mapping.get(self.language, {}).get('script', '')
        return next((lang for lang in variants if script and f'script_{script}' in lang), variants[0])

    def _load(self)->bool:
        if self.model is not None:
            return True
        try:
            import torch
            from transformers import Wav2Vec2ForCTC, AutoProcessor
            progress_bar = getattr(sys.modules.get('lib.gradio'), 'progress_bar', None)
            repo = self.settings['asr_model']
            msg = legends['msg_verify_loading'].format(model=repo)
            print(msg)
            # the weights first, through hf_download for its progress in the GUI, then from the cache
            hf_download(progress_bar, msg, repo_id=repo, filename='model.safetensors', cache_dir=tts_dir)
            self.processor = AutoProcessor.from_pretrained(repo, target_lang=self.asr_language, cache_dir=tts_dir)
            # the head is sized per language, the one in model.safetensors is english: replaced by the adapter's
            self.model = Wav2Vec2ForCTC.from_pretrained(repo, target_lang=self.asr_language, ignore_mismatched_sizes=True, cache_dir=tts_dir)
            self.model.eval()
            if self.session['device'] in (devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']) and torch.cuda.is_available():
                try:
                    self.model = self.model.half().to('cuda')
                    self.device = 'cuda'
                except RuntimeError:
                    # not enough VRAM left next to the TTS model: cpu, slower but the conversion goes on
                    self.model = self.model.float().to(devices['CPU']['proc'])
                    self.device = devices['CPU']['proc']
                    torch.cuda.empty_cache()
            return True
        except Exception as e:
            self._disable_asr(e)
            return False

    def _romanize(self, text:str)->str:
        if self.language == 'jpn':
            # uroman reads kanji with their chinese readings: the bursts of a good take reached the burst limit
            if self.kakasi is None:
                import pykakasi
                self.kakasi = pykakasi.kakasi()
            return ' '.join(item['hepburn'] for item in self.kakasi.convert(text))
        if self.uroman is None:
            import uroman
            self.uroman = uroman.Uroman()
        return self.uroman.romanize_string(text, lcode=self.language)

    def _letters(self, text:str)->str:
        # what both sides are compared on: romanized letters only, lower case, no accents, no spaces
        if not any(c.isalpha() for c in text):
            return ''
        text = unicodedata.normalize('NFKD', self._romanize(text).casefold())
        return re.sub(r'[^\p{L}]+', '', text)

    def _strip_punctuation(self, text:str, level:int)->str:
        # by unicode category, not the punctuation lists: they hold two Lao vowel signs (U+0ECC, U+0ECD). Kept: letters,
        # marks (Indic, Thai, Arabic vowels), digits, ZWNJ/ZWJ (Persian, Indic) and ' or - inside a word (don't, l'homme)
        text = re.sub(r"(?<=\p{L}\p{M}*)['’](?=\p{L})", '\uf8f0', text)
        text = re.sub(r'(?<=\p{L}\p{M}*)[-‐](?=\p{L})', '\uf8f1', text)
        pause = ',' if level == 1 else ' '
        out = []
        for c in text:
            category = unicodedata.category(c)
            if category[0] in 'LMN' or c.isspace() or c in '\u200c\u200d\uf8f0\uf8f1':
                out.append(c)
            elif category[0] == 'P' and category not in ('Ps', 'Pe', 'Pi', 'Pf') and c not in '"\'':
                # a pause stays a pause (commas only), quotes and brackets go
                out.append(pause)
            else:
                out.append(' ')
        text = ''.join(out).replace('\uf8f0', "'").replace('\uf8f1', '-')
        text = re.sub(r'\s*,[\s,]*', ', ', text)
        return re.sub(r'\s+', ' ', text).strip(' ,')

    def _end_mark(self, sentence:str, level:int)->str:
        # a question stays a question at both levels, an exclamation at level 1 only
        text = re.sub(r'[\s"\'»”’)\]]+$', '', SML_TAG_PATTERN.sub(' ', sentence).rstrip())
        ending = re.search(r'[\p{P}\s]*$', text).group(0)
        if any(c in ending for c in ('?', '？', '؟', '፧', '‽')):
            return '?'
        if any(c in ending for c in ('!', '！')) and level == 1:
            return '!'
        return '.'

    def text_variant(self, sentence:str, level:int)->str:
        # the text sent to the engine for a take of this level (see levels in conf_models.py), the check still compares
        # with the sentence itself: only punctuation goes, the letters stay. SML tags are left as they are
        if level <= 0 or not any(c.isalpha() for c in SML_TAG_PATTERN.sub(' ', sentence)):
            return sentence
        parts = []
        last = 0
        for match in SML_TAG_PATTERN.finditer(sentence):
            parts.append([False, self._strip_punctuation(sentence[last:match.start()], level)])
            parts.append([True, match.group(0)])
            last = match.end()
        parts.append([False, self._strip_punctuation(sentence[last:], level)])
        for part in reversed(parts):
            if not part[0] and any(c.isalnum() for c in part[1]):
                part[1] += self._end_mark(sentence, level)
                break
        return ' '.join(text for _, text in parts if text)

    def _distances(self, ref:str, hyp:str)->list:
        # levenshtein table: dist[i][j] between ref[:i] and hyp[:j]
        rows, cols = len(ref), len(hyp)
        dist = [list(range(cols + 1))] + [[i] + [0] * cols for i in range(1, rows + 1)]
        for i in range(1, rows + 1):
            prev, cur, ref_char = dist[i - 1], dist[i], ref[i - 1]
            for j in range(1, cols + 1):
                cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ref_char != hyp[j - 1]))
        return dist

    def _tail_extra(self, last_row:list)->int:
        # extra letters heard after the text ends, as many as an optimal alignment allows: a word said twice at the
        # end ("fourteen fourteen") is aligned either way at the same cost, the repeat counts as extra
        total = last_row[-1]
        return max(k for k in range(len(last_row)) if last_row[len(last_row) - 1 - k] + k == total)

    def _compare(self, ref:str, hyp:str)->tuple[float, int, int]:
        # levenshtein alignment of the letters: the CER (distance over the text length, above 1.0 when the take says
        # more than the text), the longest burst of errors in a row (a single chance match inside not ending it) and
        # the extra letters heard before the text starts or after it ends. A burst is local: babble or a skipped phrase
        # in a long sentence barely moves its CER, and a hard name raises the CER while its burst stays short. Extra
        # letters at an edge can only be speech the text does not have: a misheard name sits inside the text
        if not ref:
            return 0.0, 0, 0
        rows, cols = len(ref), len(hyp)
        dist = self._distances(ref, hyp)
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
        edge = max(self._tail_extra(dist[rows]), self._tail_extra(self._distances(ref[::-1], hyp[::-1])[rows]))
        return dist[rows][cols] / rows, max((len(b.replace('M', '')) for b in bursts), default=0), edge

    def _speech_segments(self, audio:Any, samplerate:int)->list:
        # the take cut at its long silences ([pause], [break]): MMS on the whole take drops a short part followed by a
        # long silence, a chapter title before its [pause] in most languages, while it hears it on its own
        import numpy as np
        frame = int(samplerate * 0.02)
        count = len(audio) // frame
        if count == 0:
            return [audio]
        rms = np.sqrt(np.mean(audio[:count * frame].reshape(count, frame) ** 2, axis=1))
        silent = rms < max(0.002, 0.03 * float(rms.max()))
        gap = int(self.settings['segment_gap'] / 0.02)
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

    def _transcribe(self, audio:Any, samplerate:int, segmented:bool=False)->str:
        import torch
        import torchaudio
        target_sr = self.settings['samplerate']
        wav = torch.from_numpy(audio)
        if samplerate != target_sr:
            wav = torchaudio.functional.resample(wav, samplerate, target_sr)
        texts = []
        for segment in (self._speech_segments(wav.numpy(), target_sr) if segmented else [wav.numpy()]):
            inputs = self.processor(segment, sampling_rate=target_sr, return_tensors='pt')
            values = inputs['input_values'].to(self.device, dtype=next(self.model.parameters()).dtype)
            with torch.inference_mode():
                logits = self.model(values).logits
            texts.append(self.processor.decode(torch.argmax(logits, dim=-1)[0].cpu()))
        return ' '.join(text for text in texts if text)

    def _limit(self, samples:deque, name:str)->float:
        # max(floor, factor * the book's median), the warmup value until the median is known
        if len(samples) < self.settings['warmup']:
            return self.settings[f'{name}_warmup']
        return max(self.settings[f'{name}_floor'], self.settings[f'{name}_factor'] * statistics.median(samples))

    def check(self, sentence_file:str, sentence:str, first_take:bool)->dict:
        # ok, the measures, a reason legend when it fails, and badness to keep the best of the failed takes (lower is
        # better, a length failure ranks below any CER since it is babble or silence most of the time)
        result = dict(ok=True, cer=None, burst=None, edge=None, duration=0.0, limit=0.0, reason=None, badness=0.0)
        try:
            import soundfile as sf
            spoken = SML_TAG_PATTERN.sub(' ', sentence)
            ref = self._letters(spoken)
            if not ref:
                return result
            audio, samplerate = sf.read(sentence_file, dtype='float32', always_2d=True)
            audio = audio.mean(axis=1)
            duration = len(audio) / samplerate
            letters = len(ref)
            # a digit still in the text is read as a word or more: 4 letters for the length limits, kept out of the rate median
            digits = len(re.findall(r'\d', spoken))
            length_letters = letters + 4 * digits
            result['duration'] = duration
            rate_ready = len(self.rate_samples) >= self.settings['warmup']
            median_rate = statistics.median(self.rate_samples) if rate_ready else 0.0
            if rate_ready:
                limit = median_rate * length_letters * self.settings['length_factor'] + self.settings['length_slack']
            else:
                limit = length_letters * self.settings['length_warmup_rate'] + self.settings['length_warmup_slack']
            result['limit'] = limit
            if first_take and not digits and letters >= self.settings['rate_min_letters']:
                self.rate_samples.append(duration / letters)
            if duration > limit:
                reason = legends['msg_verify_reason_long'].format(duration=f'{duration:.1f}', limit=f'{limit:.1f}')
                result.update(ok=False, reason=reason, badness=10.0 + duration / limit)
                return result
            # an empty take (0.1s) is cut whatever the sentence, never sent to MMS
            shortest = 0.1
            if rate_ready and length_letters >= self.settings['rate_min_letters']:
                shortest = max(shortest, median_rate * length_letters * self.settings['short_factor'])
            if duration < shortest:
                reason = legends['msg_verify_reason_short'].format(duration=f'{duration:.1f}', limit=f'{shortest:.1f}')
                result.update(ok=False, reason=reason, badness=10.0 + shortest / max(duration, 0.01))
                return result
            # digits still in the text: normalize_text() could not spell them in this language, how the TTS reads
            # them is not known, the length check is all that is left
            if not self.asr_enabled or letters < self.settings['min_letters'] or digits or not self._load():
                return result
            cer_limit = self._limit(self.cer_samples, 'cer')
            burst_limit = self._limit(self.burst_samples, 'burst')
            edge_limit = self._limit(self.edge_samples, 'edge')
            cer, burst, edge = self._compare(ref, self._letters(self._transcribe(audio, samplerate)))
            # failed on the whole take: again part by part (cut at its long silences), the better of both is kept.
            # Babble is in the audio, both hear it; MMS drops a short part before a long silence (a chapter title
            # before its [pause]) on the whole take only. Cut every time, short parts like "Hm" come out noisier
            if (edge > edge_limit or burst > burst_limit or cer > cer_limit) and len(self._speech_segments(audio, samplerate)) > 1:
                parts = self._compare(ref, self._letters(self._transcribe(audio, samplerate, segmented=True)))
                if parts[0] + (parts[1] + parts[2]) / letters < cer + (burst + edge) / letters:
                    cer, burst, edge = parts
            if first_take:
                self.cer_samples.append(cer)
                self.burst_samples.append(burst)
                self.edge_samples.append(edge)
            result.update(cer=cer, burst=burst, edge=edge, badness=cer + (burst + edge) / letters)
            if edge > edge_limit:
                reason = legends['msg_verify_reason_edge'].format(edge=edge, limit=f'{edge_limit:.0f}')
                result.update(ok=False, reason=reason)
            elif burst > burst_limit:
                reason = legends['msg_verify_reason_burst'].format(burst=burst, limit=f'{burst_limit:.0f}')
                result.update(ok=False, reason=reason)
            elif cer > cer_limit:
                reason = legends['msg_verify_reason_mismatch'].format(cer=f'{cer:.2f}', limit=f'{cer_limit:.2f}')
                result.update(ok=False, reason=reason)
            return result
        except Exception as e:
            self._disable_asr(e)
            return dict(ok=True, cer=None, burst=None, edge=None, duration=0.0, limit=0.0, reason=None, badness=0.0)

    def flag(self, sentence_file:str, sentence:str, result:dict)->None:
        # a sentence still failing after its retries: its best take is kept, listed at the end of the conversion
        stem = Path(sentence_file).stem
        entry = dict(block=os.path.basename(os.path.dirname(sentence_file)), sentence=int(stem) if stem.isdigit() else stem, text=sentence, cer=result.get('cer'), reason=result.get('reason'))
        self.flagged.append(entry)
        self.stats['flagged'] += 1
        msg = legends['msg_verify_flagged'].format(reason=entry['reason'], text=sentence)
        print(msg)

    def close(self)->None:
        cuda = self.device == 'cuda'
        self.model = None
        self.processor = None
        self.device = devices['CPU']['proc']
        gc.collect()
        if cuda:
            try:
                import torch
                torch.cuda.empty_cache()
            except Exception:
                pass
