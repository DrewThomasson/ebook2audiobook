import os
import shutil
import subprocess
import tempfile
import threading
import uuid
from pathlib import Path

# Try to import core deps and E2A utilities (graceful fallback if missing)
try:
    import numpy as np
    import regex as re
    import soundfile as sf
    import torch
    import torchaudio

    from kokoro import KPipeline

    from lib.models import (
        TTS_ENGINES,
        models,
        loaded_tts,
        default_vc_model,
        TTS_VOICE_CONVERSION,
        TTS_SML,
    )
    from lib.lang import language_tts
    from lib.conf import tts_dir
    from lib import default_audio_proc_format

    from lib.classes.tts_engines.common.utils import unload_tts, append_sentence2vtt
    from lib.classes.tts_engines.common.audio_filters import (
        detect_gender,
        trim_audio,
        normalize_audio,
        is_audio_data_valid,
    )

    KOKORO_DEPENDENCIES_AVAILABLE = True
except Exception as e:
    KOKORO_DEPENDENCIES_AVAILABLE = False
    _missing_dependency_error = str(e)

    def unload_tts(*args, **kwargs): pass
    def append_sentence2vtt(*args, **kwargs): return 1
    def detect_gender(*args, **kwargs): return "unknown"
    def trim_audio(x, *args, **kwargs): return x
    def normalize_audio(x, *args, **kwargs): return x
    def is_audio_data_valid(*args, **kwargs): return False

lock = threading.Lock()


class Coqui:
    """
    Kokoro engine using hexgrad/kokoro KPipeline + VC-based cloning (same methodology as Piper).
    """

    def __init__(self, session):
        try:
            if not KOKORO_DEPENDENCIES_AVAILABLE:
                raise ImportError(
                    f"Kokoro dependencies not available: {_missing_dependency_error}. "
                    f"Install: pip install 'kokoro>=0.9.4' soundfile numpy"
                )

            self.session = session
            self.cache_dir = tts_dir
            self.tts_key = f"{self.session['tts_engine']}-{self.session['fine_tuned']}"
            self.tts_vc_key = default_vc_model.rsplit("/", 1)[-1]

            # defaults/samplerate
            self.params = {TTS_ENGINES['KOKORO']: {"semitones": {}}}
            self.params[self.session['tts_engine']]['samplerate'] = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']

            # running state
            self.vtt_path = os.path.join(self.session['process_dir'], os.path.splitext(self.session['final_name'])[0] + '.vtt')
            self.audio_segments = []
            self.sentences_total_time = 0.0
            self.sentence_idx = 1
            self.resampler_cache = {}

            self._build()
        except Exception as e:
            print(f"Kokoro.__init__ error: {e}")

    def _build(self):
        try:
            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            if not tts:
                if self.session['tts_engine'] == TTS_ENGINES['KOKORO']:
                    if self.session.get('custom_model'):
                        print("Custom Kokoro models are not supported yet.")
                        return False
                    tts = self._load_api(self.tts_key)

            if self.session.get('voice'):
                tts_vc = (loaded_tts.get(self.tts_vc_key) or {}).get('engine', False)
                if not tts_vc:
                    tts_vc = self._load_vc_engine(self.tts_vc_key, default_vc_model)

            return (loaded_tts.get(self.tts_key) or {}).get('engine', False)
        except Exception as e:
            print(f"Kokoro._build error: {e}")
            return False

    def _kokoro_lang(self):
        # Map ISO-639-3 to Kokoro letter code via language_tts['kokoro']
        iso3 = self.session.get('language', 'eng')
        return language_tts.get('kokoro', {}).get(iso3, 'a')  # default to American English

    def _load_api(self, key):
        global lock
        try:
            if key in loaded_tts:
                return loaded_tts[key]['engine']

            unload_tts(self.session.get('device', 'cpu'), [self.tts_key, self.tts_vc_key])

            with lock:
                lang_code = self._kokoro_lang()
                engine = KPipeline(lang_code=lang_code)
                loaded_tts[key] = {"engine": engine, "config": {"lang_code": lang_code}}
                print("KOKORO Loaded!")
                return engine
        except Exception as e:
            print(f"_load_api error: {e}")
            loaded_tts[key] = {"engine": None, "config": None}
            return None

    def _load_vc_engine(self, key, model_path):
        global lock
        try:
            if key in loaded_tts:
                return loaded_tts[key]['engine']
            unload_tts(self.session.get('device', 'cpu'), [self.tts_vc_key])
            with lock:
                from TTS.api import TTS as CoquiAPI
                tts = CoquiAPI(model_path)
                device = self.session.get('device', 'cpu')
                if device == 'cuda':
                    tts.cuda()
                else:
                    tts.to(device)
                loaded_tts[key] = {"engine": tts, "config": None}
                print(f"{model_path} (VC) Loaded!")
                return tts
        except Exception as e:
            print(f"_load_vc_engine error: {e}")
            return None

    def _get_resampler(self, orig_sr, target_sr):
        if not hasattr(self, 'resampler_cache'):
            self.resampler_cache = {}
        key = (orig_sr, target_sr)
        if key not in self.resampler_cache:
            self.resampler_cache[key] = torchaudio.transforms.Resample(
                orig_freq=orig_sr, new_freq=target_sr
            )
        return self.resampler_cache[key]

    def _resample_wav_path(self, wav_path, expected_sr):
        waveform, orig_sr = torchaudio.load(wav_path)
        if waveform.size(0) > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if orig_sr != expected_sr:
            resampler = self._get_resampler(orig_sr, expected_sr)
            waveform = resampler(waveform)
        out_tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        torchaudio.save(out_tmp, waveform, expected_sr)
        return out_tmp

    def _synthesize(self, engine, text, voice):
        # hexgrad/kokoro: generator yields (graphemes, phonemes, audio)
        try:
            # Ensure pipeline language matches session; recreate if needed
            cfg = (loaded_tts.get(self.tts_key) or {}).get('config') or {}
            current_lang = cfg.get('lang_code')
            desired_lang = self._kokoro_lang()
            if current_lang != desired_lang:
                # reload pipeline in desired language
                loaded_tts.pop(self.tts_key, None)
                engine = self._load_api(self.tts_key)

            gen = engine(text, voice=voice, speed=1, split_pattern=r'\n+')
            chunks = []
            for _, _, audio in gen:
                if isinstance(audio, np.ndarray):
                    a = audio.astype(np.float32, copy=False)
                elif isinstance(audio, torch.Tensor):
                    a = audio.detach().cpu().float().numpy()
                else:
                    a = np.array(audio, dtype=np.float32)
                if a.ndim > 1:
                    a = np.mean(a, axis=0).astype(np.float32)
                chunks.append(a)
            if not chunks:
                return np.zeros(1, dtype=np.float32)
            return np.concatenate(chunks).astype(np.float32)
        except Exception as e:
            print(f"Kokoro synth error: {e}")
            return np.zeros(1, dtype=np.float32)

    def _default_voice(self, lang_letter):
        # Safe default that exists in model cards; works across languages too
        return "af_heart"

    def convert(self, sentence_number, sentence):
        try:
            settings = self.params[self.session['tts_engine']]
            sr = settings['samplerate']
            final_sentence_file = os.path.join(self.session['chapters_dir_sentences'], f"{sentence_number}.{default_audio_proc_format}")
            sentence = (sentence or "").strip()

            # SML control tokens
            if sentence == TTS_SML['break']:
                self.audio_segments.append(torch.zeros(1, int(sr * 0.45)))
                return True
            if sentence == TTS_SML['pause']:
                self.audio_segments.append(torch.zeros(1, int(sr * 1.4)))
                return True

            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            if not tts:
                print("convert(): KOKORO engine not loaded")
                return False

            if sentence and sentence[-1].isalnum():
                sentence = f"{sentence} —"

            # 1) Kokoro TTS
            lang_letter = self._kokoro_lang()
            voice_id = self._default_voice(lang_letter)
            kokoro_audio = self._synthesize(tts, sentence, voice_id)

            # 2) Optional VC-based cloning (same methodology as Piper)
            ref_voice_path = self.session.get('voice')
            if ref_voice_path:
                try:
                    proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                    os.makedirs(proc_dir, exist_ok=True)
                    tmp_in = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                    tmp_pitch = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")

                    # Save Kokoro output
                    sf.write(tmp_in, kokoro_audio if is_audio_data_valid(kokoro_audio) else np.zeros(int(sr*0.1), dtype=np.float32), sr, subtype="PCM_16")

                    # Cache semitones based on gender adaptation
                    if ref_voice_path in settings['semitones']:
                        semitones = settings['semitones'][ref_voice_path]
                    else:
                        ref_gender = detect_gender(ref_voice_path)
                        base_gender = detect_gender(tmp_in)
                        if ref_gender in ['male','female'] and base_gender in ['male','female'] and ref_gender != base_gender:
                            semitones = -4 if ref_gender == 'male' else 4
                            print("Adapting builtin voice frequencies from the clone voice...")
                        else:
                            semitones = 0
                        settings['semitones'][ref_voice_path] = semitones

                    # Pitch shift with sox when helpful
                    if semitones != 0 and shutil.which('sox'):
                        try:
                            subprocess.run(
                                [shutil.which('sox'), tmp_in, "-r", str(sr), tmp_pitch, "pitch", str(semitones * 100)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
                            )
                            src_for_vc = tmp_pitch
                        except Exception as e:
                            print(f"Pitch shift failed: {e}")
                            src_for_vc = tmp_in
                    else:
                        src_for_vc = tmp_in

                    # VC conversion at its native samplerate
                    tts_vc = (loaded_tts.get(self.tts_vc_key) or {}).get('engine', False)
                    if not tts_vc:
                        tts_vc = self._load_vc_engine(self.tts_vc_key, default_vc_model)

                    if tts_vc:
                        vc_sr = TTS_VOICE_CONVERSION[self.tts_vc_key]['samplerate']
                        src_wav = self._resample_wav_path(src_for_vc, vc_sr)
                        tgt_wav = self._resample_wav_path(ref_voice_path, vc_sr)
                        out = tts_vc.voice_conversion(source_wav=src_wav, target_wav=tgt_wav)
                        if isinstance(out, torch.Tensor):
                            kokoro_audio = out.detach().cpu().float().numpy()
                        elif isinstance(out, np.ndarray):
                            kokoro_audio = out.astype(np.float32, copy=False)
                        else:
                            kokoro_audio = np.array(out, dtype=np.float32)

                        # Resample VC output back to session sr if needed
                        if vc_sr != sr and kokoro_audio.size > 0:
                            wav = torch.tensor(kokoro_audio).unsqueeze(0)
                            res = self._get_resampler(vc_sr, sr)(wav)
                            kokoro_audio = res.squeeze(0).cpu().numpy().astype(np.float32)
                        try:
                            if os.path.exists(src_wav): os.remove(src_wav)
                            if os.path.exists(tgt_wav): os.remove(tgt_wav)
                        except: pass
                    else:
                        print("VC engine not available; skipping cloning.")

                    # Cleanup temps
                    try:
                        if os.path.exists(tmp_in): os.remove(tmp_in)
                        if os.path.exists(tmp_pitch): os.remove(tmp_pitch)
                    except: pass
                except Exception as e:
                    print(f"Kokoro VC path failed: {e}")

            # 3) Post-process, segment timing, save
            if is_audio_data_valid(kokoro_audio):
                audio_tensor = torch.tensor(kokoro_audio, dtype=torch.float32).unsqueeze(0)
                audio_tensor = normalize_audio(audio=audio_tensor, samplerate=sr)
                # trim slight tail if sentence ended mid-token
                if sentence and (sentence[-1].isalnum() or sentence[-1] == '—'):
                    audio_tensor = trim_audio(audio_tensor.squeeze(0), sr, 0.003, 0.004).unsqueeze(0)

                self.audio_segments.append(audio_tensor)

                # heuristic short break after non-word terminal punctuation
                if not re.search(r'\w$', sentence, flags=re.UNICODE):
                    self.audio_segments.append(torch.zeros(1, int(sr * 0.45)))

                if self.audio_segments:
                    audio_tensor = torch.cat(self.audio_segments, dim=-1)
                    start_time = self.sentences_total_time
                    duration = audio_tensor.shape[-1] / sr
                    end_time = start_time + duration
                    self.sentences_total_time = end_time

                    sentence_obj = {
                        "start": start_time,
                        "end": end_time,
                        "text": sentence,
                        "resume_check": self.sentence_idx,
                    }
                    self.sentence_idx = append_sentence2vtt(sentence_obj, self.vtt_path)

                    if self.sentence_idx:
                        torchaudio.save(final_sentence_file, audio_tensor, sr, format=default_audio_proc_format)
                        del audio_tensor

                self.audio_segments = []

                return os.path.exists(final_sentence_file)

            print("Kokoro produced empty audio.")
            return False
        except Exception as e:
            raise ValueError(f"Kokoro.convert(): {e}")
