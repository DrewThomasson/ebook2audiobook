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
    # Every take gets the length check, then MMS transcribes it and the letters of both texts, romanized by uroman, are
    # compared (CER). A failure here never stops the conversion: speech recognition is turned off, the length check
    # goes on and the take is kept

    def __init__(self, session:Any)->None:
        self.session = session
        self.settings = default_verify_settings
        self.retries = int(self.settings['retries'])
        translated = bool(session.get('translate_enabled') and session.get('translate'))
        self.language = session['translate'] if translated else session['language']
        self.cer_samples:deque = deque(maxlen=self.settings['samples_max'])
        self.rate_samples:deque = deque(maxlen=self.settings['samples_max'])
        self.flagged:list[dict] = []
        self.model = None
        self.processor = None
        self.uroman = None
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

    def _cer(self, ref:str, hyp:str)->float:
        # levenshtein distance over the reference length: above 1.0 when the take says more than the text
        if not ref:
            return 0.0
        prev = list(range(len(hyp) + 1))
        for i, ref_char in enumerate(ref, 1):
            cur = [i] + [0] * len(hyp)
            for j, hyp_char in enumerate(hyp, 1):
                cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ref_char != hyp_char))
            prev = cur
        return prev[-1] / len(ref)

    def _transcribe(self, audio:Any, samplerate:int)->str:
        import torch
        import torchaudio
        target_sr = self.settings['samplerate']
        wav = torch.from_numpy(audio)
        if samplerate != target_sr:
            wav = torchaudio.functional.resample(wav, samplerate, target_sr)
        inputs = self.processor(wav.numpy(), sampling_rate=target_sr, return_tensors='pt')
        values = inputs['input_values'].to(self.device, dtype=next(self.model.parameters()).dtype)
        with torch.inference_mode():
            logits = self.model(values).logits
        return self.processor.decode(torch.argmax(logits, dim=-1)[0].cpu())

    def _cer_limit(self)->float:
        if len(self.cer_samples) < self.settings['warmup']:
            return self.settings['cer_warmup']
        return max(self.settings['cer_floor'], self.settings['cer_factor'] * statistics.median(self.cer_samples))

    def check(self, sentence_file:str, sentence:str, first_take:bool)->dict:
        # ok, the measures, a reason legend when it fails, and badness to keep the best of the failed takes (lower is
        # better, a length failure ranks below any CER since it is babble or silence most of the time)
        result = dict(ok=True, cer=None, duration=0.0, limit=0.0, reason=None, badness=0.0)
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
            cer = self._cer(ref, self._letters(self._transcribe(audio, samplerate)))
            cer_limit = self._cer_limit()
            if first_take:
                self.cer_samples.append(cer)
            result.update(cer=cer, badness=cer)
            if cer > cer_limit:
                reason = legends['msg_verify_reason_mismatch'].format(cer=f'{cer:.2f}', limit=f'{cer_limit:.2f}')
                result.update(ok=False, reason=reason)
            return result
        except Exception as e:
            self._disable_asr(e)
            return dict(ok=True, cer=None, duration=0.0, limit=0.0, reason=None, badness=0.0)

    def flag(self, sentence_file:str, sentence:str, result:dict)->None:
        # a sentence still failing after its retries: its best take is kept, listed at the end of the conversion
        stem = Path(sentence_file).stem
        entry = dict(block=os.path.basename(os.path.dirname(sentence_file)), sentence=int(stem) if stem.isdigit() else stem, text=sentence, cer=result.get('cer'), reason=result.get('reason'))
        self.flagged.append(entry)
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
