import os
import tempfile
import threading

# Conditional imports for F5-TTS and dependencies
try:
    import numpy as np
    import regex as re
    import soundfile as sf
    import torch
    import torchaudio

    # Try multiple possible import paths for F5-TTS (PyPI and source installs vary)
    _F5 = None
    _missing_f5_impl = ""
    try:
        # PyPI package name: f5-tts (newer)
        from f5_tts import F5TTS as _F5
    except Exception as _e1:
        _missing_f5_impl = str(_e1)
        try:
            # Alternate path some installs use
            from f5_tts.api import F5TTS as _F5
        except Exception as _e2:
            _missing_f5_impl = f"{_missing_f5_impl} | {str(_e2)}"
            try:
                # Some source/fork layouts
                from F5TTS.api import F5TTS as _F5
            except Exception as _e3:
                _missing_f5_impl = f"{_missing_f5_impl} | {str(_e3)}"
                _F5 = None

    from lib.classes.tts_engines.common.utils import unload_tts, append_sentence2vtt
    from lib.classes.tts_engines.common.audio_filters import (
        trim_audio, is_audio_data_valid
    )
    F5_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    F5_DEPENDENCIES_AVAILABLE = False
    _missing_dependency_error = str(e)
    def unload_tts(*args, **kwargs): pass
    def append_sentence2vtt(*args, **kwargs): return 1
    def trim_audio(*args, **kwargs): return args[0] if args else None
    def is_audio_data_valid(*args, **kwargs): return False
    _F5 = None
    _missing_f5_impl = _missing_dependency_error

from lib import *

lock = threading.Lock()

class Coqui:
    """
    F5-TTS engine wrapper following the same interface as other engines.
    Native voice cloning via a reference wav file: session['voice'] points to a wav.

    Models and HF cache are forced into: {tts_dir}/f5tts/
    - HF cache: {tts_dir}/f5tts/hf-cache
    - Model dir passed to F5: {tts_dir}/f5tts/models/{profile}
    """

    def __init__(self, session):
        try:
            if not F5_DEPENDENCIES_AVAILABLE:
                raise ImportError(
                    f"F5-TTS dependencies missing: {_missing_dependency_error}. "
                    "Install torch, torchaudio, numpy, soundfile, regex and the F5-TTS package "
                    "(e.g., pip install f5-tts or clone https://github.com/SWivid/F5-TTS and pip install -e .)."
                )
            if _F5 is None:
                raise ImportError(
                    f"F5-TTS implementation not importable. Tried multiple import paths. Details: {_missing_f5_impl}"
                )

            self.session = session
            self.cache_dir = tts_dir  # Global TTS model root from lib
            self.local_root = os.path.join(self.cache_dir, 'f5tts')
            self.hf_cache = os.path.join(self.local_root, 'hf-cache')
            self.models_root = os.path.join(self.local_root, 'models')

            # Ensure local directories exist
            os.makedirs(self.hf_cache, exist_ok=True)
            os.makedirs(self.models_root, exist_ok=True)

            # Force HF and Transformers caches into our local directory so all downloads live under tts_dir/f5tts
            os.environ.setdefault('HF_HOME', self.hf_cache)
            os.environ.setdefault('HUGGINGFACE_HUB_CACHE', self.hf_cache)
            os.environ.setdefault('TRANSFORMERS_CACHE', self.hf_cache)

            self.tts_key = f"{self.session['tts_engine']}-{self.session['fine_tuned']}"
            self.is_bf16 = True if self.session['device'] == 'cuda' and torch.cuda.is_bf16_supported() else False

            self.sentences_total_time = 0.0
            self.sentence_idx = 1

            # Cache params under engine key
            self.params = {TTS_ENGINES['F5TTS']: {"semitones": {}}}
            self.params[self.session['tts_engine']]['samplerate'] = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']

            # VTT
            self.vtt_path = os.path.join(
                self.session['process_dir'], os.path.splitext(self.session['final_name'])[0] + '.vtt'
            )
            self.resampler_cache = {}
            self._build()
        except Exception as e:
            print(f'__init__() error: {e}')
            return None

    def _build(self):
        try:
            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            if not tts:
                # If a custom/local model directory was specified, honor it; otherwise use our engine-scoped dir.
                model_hint = self.session.get('custom_model')
                if model_hint is None:
                    profile = self.session.get('fine_tuned', 'internal')
                    model_hint = os.path.join(self.models_root, profile)
                    os.makedirs(model_hint, exist_ok=True)

                tts = self._load_api(self.tts_key, model_hint, self.session['device'])
            return (loaded_tts.get(self.tts_key) or {}).get('engine', False)
        except Exception as e:
            print(f'build() error: {e}')
            return False

    def _load_api(self, key, model_dir, device):
        global lock
        try:
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']
            unload_tts(device, [self.tts_key])
            with lock:
                kwargs = {}

                # Device and dtype
                kwargs['device'] = 'cuda' if device == 'cuda' else 'cpu'
                if device == 'cuda' and self.is_bf16:
                    kwargs['dtype'] = 'bfloat16'
                elif device == 'cuda':
                    kwargs['dtype'] = 'float16'
                else:
                    kwargs['dtype'] = 'float32'

                # Force F5-TTS to use our local model area. Different versions accept different kw names.
                # We pass both; unknown keys are commonly ignored by simple constructors.
                kwargs['model_dir'] = model_dir
                kwargs['model'] = model_dir

                # Create/load engine; F5 will either find existing files in model_dir or download into HF cache we set.
                tts = _F5(**kwargs)

                if tts:
                    loaded_tts[key] = {"engine": tts, "config": {"model_dir": model_dir}}
                    print(f'F5-TTS Loaded! Using model_dir: {model_dir}')
                    return tts
                else:
                    print('F5-TTS engine could not be created!')
        except Exception as e:
            print(f'_load_api() error: {e}')
        return False

    def _tensor_type(self, audio_data):
        if isinstance(audio_data, torch.Tensor):
            return audio_data
        elif isinstance(audio_data, np.ndarray):
            return torch.from_numpy(audio_data).float()
        elif isinstance(audio_data, list):
            return torch.tensor(audio_data, dtype=torch.float32)
        else:
            raise TypeError(f"Unsupported type for audio_data: {type(audio_data)}")

    def _get_resampler(self, orig_sr, target_sr):
        key = (orig_sr, target_sr)
        if key not in self.resampler_cache:
            self.resampler_cache[key] = torchaudio.transforms.Resample(
                orig_freq=orig_sr, new_freq=target_sr
            )
        return self.resampler_cache[key]

    def _ensure_mono_sr(self, wav_path, expected_sr):
        waveform, orig_sr = torchaudio.load(wav_path)
        if waveform.size(0) > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if orig_sr != expected_sr:
            resampler = self._get_resampler(orig_sr, expected_sr)
            waveform = resampler(waveform)
        tmp_fh = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp_fh.name
        tmp_fh.close()
        sf.write(tmp_path, waveform.squeeze(0).cpu().numpy(), expected_sr, subtype="PCM_16")
        return tmp_path

    def _synthesize_with_f5(self, tts, text, ref_wav_path=None, target_sr=24000, language_hint=None):
        """
        Call F5-TTS synthesizer. Try a few common signatures across versions.
        Always return a numpy float32 array (mono).
        """
        tried = []
        try:
            tried.append("synthesize(text, ref_wav, sample_rate, language)")
            audio = tts.synthesize(text=text, ref_wav=ref_wav_path, sample_rate=target_sr, language=language_hint)
            if isinstance(audio, tuple) and len(audio) == 2:
                audio, _ = audio
            if isinstance(audio, torch.Tensor):
                audio = audio.detach().cpu().numpy()
            return np.asarray(audio, dtype=np.float32)
        except Exception:
            pass
        try:
            tried.append("tts(text, ref_wav, sr, language)")
            audio = tts.tts(text=text, ref_wav=ref_wav_path, sr=target_sr, language=language_hint)
            if isinstance(audio, tuple) and len(audio) == 2:
                audio, _ = audio
            if isinstance(audio, torch.Tensor):
                audio = audio.detach().cpu().numpy()
            return np.asarray(audio, dtype=np.float32)
        except Exception:
            pass
        try:
            tried.append("infer(text, reference_audio, sample_rate, language)")
            audio = tts.infer(text=text, reference_audio=ref_wav_path, sample_rate=target_sr, language=language_hint)
            if isinstance(audio, tuple) and len(audio) == 2:
                audio, _ = audio
            if isinstance(audio, torch.Tensor):
                audio = audio.detach().cpu().numpy()
            return np.asarray(audio, dtype=np.float32)
        except Exception as e:
            print(f"F5 synth failed. Tried signatures: {tried}. Error: {e}")
            return np.array([], dtype=np.float32)

    def convert(self, sentence_number, sentence):
        try:
            settings = self.params[self.session['tts_engine']]
            final_sentence_file = os.path.join(
                self.session['chapters_dir_sentences'], f'{sentence_number}.{default_audio_proc_format}'
            )
            sentence = sentence.strip()

            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            if not tts:
                print(f"convert() error: {self.session['tts_engine']} is None")
                return False

            # Language hint (2-letter, if available)
            lang_code = self.session.get('language', 'eng')
            language_hint = language_tts.get('f5tts', {}).get(lang_code, None)

            # Encourage final prosody like other engines
            if sentence and sentence[-1].isalnum():
                sentence = f'{sentence} —'

            # Structured Markup Language for breaks and pauses
            if sentence == TTS_SML['break']:
                break_tensor = torch.zeros(1, int(settings['samplerate'] * 0.5))
                torchaudio.save(final_sentence_file, break_tensor, settings['samplerate'], format=default_audio_proc_format)
                return True
            elif sentence == TTS_SML['pause']:
                pause_tensor = torch.zeros(1, int(settings['samplerate'] * 1.4))
                torchaudio.save(final_sentence_file, pause_tensor, settings['samplerate'], format=default_audio_proc_format)
                return True

            # Reference voice: pass through to F5 (native cloning)
            ref_voice = self.session.get('voice', None)
            ref_for_engine = None
            if ref_voice:
                ref_for_engine = self._ensure_mono_sr(ref_voice, settings['samplerate'])

            # Synthesize
            audio_sentence = self._synthesize_with_f5(
                tts=tts,
                text=sentence,
                ref_wav_path=ref_for_engine,
                target_sr=settings['samplerate'],
                language_hint=language_hint
            )

            # cleanup temp ref if we created one
            if ref_for_engine and os.path.exists(ref_for_engine) and ref_for_engine != ref_voice:
                try:
                    os.remove(ref_for_engine)
                except Exception:
                    pass

            if is_audio_data_valid(audio_sentence):
                sourceTensor = self._tensor_type(audio_sentence)
                audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()

                # Trim tail if sentence ends in alnum or em dash
                if sentence[-1].isalnum() or sentence[-1] == '—':
                    audio_tensor = trim_audio(
                        audio_tensor.squeeze(),
                        settings['samplerate'],
                        0.003, 0.004
                    ).unsqueeze(0)

                # Timing + VTT
                start_time = self.sentences_total_time
                duration = audio_tensor.shape[-1] / settings['samplerate']
                end_time = start_time + duration
                self.sentences_total_time = end_time

                sentence_obj = {
                    "start": start_time,
                    "end": end_time,
                    "text": sentence,
                    "resume_check": self.sentence_idx
                }
                self.sentence_idx = append_sentence2vtt(sentence_obj, self.vtt_path)

                if self.sentence_idx:
                    torchaudio.save(final_sentence_file, audio_tensor, settings['samplerate'], format=default_audio_proc_format)

                if os.path.exists(final_sentence_file):
                    return True
                else:
                    print(f"Cannot create {final_sentence_file}")
            else:
                print("F5-TTS produced empty/invalid audio")
        except Exception as e:
            raise ValueError(e)
        return False