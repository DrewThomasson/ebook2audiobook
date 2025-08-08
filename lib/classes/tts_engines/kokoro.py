import os
import shutil
import subprocess
import tempfile
import threading
import uuid

# Conditional imports for Kokoro TTS dependencies
try:
    import numpy as np
    import regex as re
    import soundfile as sf
    import torch
    import torchaudio

    # Common utils with their dependencies
    from lib.classes.tts_engines.common.utils import unload_tts, append_sentence2vtt
    from lib.classes.tts_engines.common.audio_filters import detect_gender, trim_audio, normalize_audio, is_audio_data_valid

    # Kokoro ONNX (optional, robust detection)
    KOKORO_ONNX_AVAILABLE = False
    _kokoro_import_error = None
    try:
        import importlib
        if importlib.util.find_spec("kokoro_onnx") is not None:
            kokoro_onnx = importlib.import_module("kokoro_onnx")
            KOKORO_ONNX_AVAILABLE = True
    except Exception as _e_k:
        _kokoro_import_error = str(_e_k)
        KOKORO_ONNX_AVAILABLE = False

    KOKORO_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    KOKORO_DEPENDENCIES_AVAILABLE = False
    _missing_dependency_error = str(e)

    # Placeholder fallbacks to avoid GUI crashes
    def unload_tts(*args, **kwargs): pass
    def append_sentence2vtt(*args, **kwargs): pass
    def detect_gender(*args, **kwargs): return "unknown"
    def trim_audio(*args, **kwargs): return args[0] if args else None
    def normalize_audio(*args, **kwargs): return args[0] if args else None
    def is_audio_data_valid(*args, **kwargs): return False

from pathlib import Path
from lib import *

lock = threading.Lock()

class Coqui:
    """
    Kokoro TTS engine wrapper using kokoro-onnx (if available) and the same
    VC-based cloning methodology implemented for Piper (voice conversion + optional pitch adaptation).
    """

    def __init__(self, session):
        try:
            if not KOKORO_DEPENDENCIES_AVAILABLE:
                raise ImportError(f"Kokoro TTS dependencies not available: {_missing_dependency_error}. "
                                  f"Please install: pip install numpy soundfile regex torch torchaudio kokoro-onnx onnxruntime")

            if not KOKORO_ONNX_AVAILABLE:
                msg = "kokoro-onnx module not found. Please install: pip install kokoro-onnx onnxruntime"
                print(msg)

            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.tts_key = f"{self.session['tts_engine']}-{self.session['fine_tuned']}"
            self.tts_vc_key = default_vc_model.rsplit('/', 1)[-1]

            # Kokoro commonly outputs at 24 kHz (configured via models/defaults)
            self.is_bf16 = True if self.session['device'] == 'cuda' and torch.cuda.is_bf16_supported() == True else False
            self.npz_path = None
            self.npz_data = None
            self.sentences_total_time = 0.0
            self.sentence_idx = 1

            # Cache params, including semitones for cloning
            self.params = {TTS_ENGINES['KOKORO']: {"semitones": {}}}
            self.params[self.session['tts_engine']]['samplerate'] = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']

            self.vtt_path = os.path.join(self.session['process_dir'], os.path.splitext(self.session['final_name'])[0] + '.vtt')
            self.resampler_cache = {}
            self.audio_segments = []

            self._build()
        except Exception as e:
            print(f"__init__() error: {e}")
            return None

    def _build(self):
        try:
            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            if not tts:
                if self.session['tts_engine'] == TTS_ENGINES['KOKORO']:
                    if self.session['custom_model'] is not None:
                        print(f"{self.session['tts_engine']} custom model not implemented yet!")
                        return False
                    else:
                        # Build/Load Kokoro runtime
                        tts = self._load_api(self.tts_key, self.session['device'])

            # If a reference voice is provided, attempt to load the VC engine (for cloning)
            if self.session.get('voice'):
                tts_vc = (loaded_tts.get(self.tts_vc_key) or {}).get('engine', False)
                if not tts_vc:
                    tts_vc = self._load_vc_engine(self.tts_vc_key, default_vc_model, self.session['device'])

            return (loaded_tts.get(self.tts_key) or {}).get('engine', False)
        except Exception as e:
            print(f'_build() error: {e}')
            return False

    def _default_voice_by_lang(self):
        """
        Return a reasonable default voice identifier by session language.
        These IDs depend on installed Kokoro voicepacks. Adjust as needed.
        """
        lang_code = self.session.get('language', 'eng')
        kokoro_lang = language_tts.get('kokoro', {}).get(lang_code, 'en')

        # Provide a conservative set of defaults (safe placeholders).
        # Users can select specific voices/voicepacks externally when kokoro-onnx provides them.
        defaults = {
            'en': 'en-US',  # generic English (US) voice
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'it': 'it-IT',
            'pt': 'pt-PT',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'zh': 'zh-CN',
        }
        return defaults.get(kokoro_lang, 'en-US')

    def _load_api(self, key, device):
        """
        Kokoro-ONNX model loader (high-level). We rely on kokoro-onnx to manage
        model/voicepack assets. If missing, we load a stub to fail gracefully.
        """
        global lock
        try:
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']

            unload_tts(device, [self.tts_key, self.tts_vc_key])

            with lock:
                if not KOKORO_ONNX_AVAILABLE:
                    print("kokoro-onnx is not installed. Please install: pip install kokoro-onnx onnxruntime")
                    loaded_tts[key] = {"engine": None, "config": None}
                    return None

                # Instantiate kokoro engine - try common APIs from kokoro-onnx variants
                engine = None
                init_errors = []

                # Common constructors across community wrappers
                for ctor_name in ("Kokoro", "TTS", "KokoroTTS", "Engine"):
                    try:
                        ctor = getattr(kokoro_onnx, ctor_name, None)
                        if callable(ctor):
                            engine = ctor()
                            break
                    except Exception as e:
                        init_errors.append(f"{ctor_name}: {e}")

                # If no constructor found, try module-as-engine usage
                if engine is None:
                    engine = kokoro_onnx

                if engine is not None:
                    # Device handling if supported (many ONNX pipelines are CPU-oriented; keep simple)
                    loaded_tts[key] = {"engine": engine, "config": {"init_errors": init_errors} if init_errors else None}
                    print('KOKORO Loaded!')
                    return engine
                else:
                    print('KOKORO engine could not be created!')
        except Exception as e:
            print(f'_load_api() error: {e}')

        return False

    def _load_vc_engine(self, key, model_path, device):
        """
        Load the generic VC engine (same path as used by piper.py).
        """
        global lock
        try:
            if key in loaded_tts.keys():
                return loaded_tts[key]['engine']
            unload_tts(device, [self.tts_vc_key])
            with lock:
                try:
                    from TTS.api import TTS as CoquiAPI  # Lazy import
                except Exception as e:
                    print(f"Voice conversion dependencies not available: {e}. Install Coqui TTS to enable cloning.")
                    return False
                tts = CoquiAPI(model_path)
                if tts:
                    if device == 'cuda':
                        tts.cuda()
                    else:
                        tts.to(device)
                    loaded_tts[key] = {"engine": tts, "config": None}
                    print(f'{model_path} (VC) Loaded!')
                    return tts
                else:
                    print('VC engine could not be created!')
        except Exception as e:
            print(f'_load_vc_engine() error: {e}')
        return False

    def _get_resampler(self, orig_sr, target_sr):
        key = (orig_sr, target_sr)
        if not hasattr(self, 'resampler_cache'):
            self.resampler_cache = {}
        if key not in self.resampler_cache:
            self.resampler_cache[key] = torchaudio.transforms.Resample(
                orig_freq=orig_sr, new_freq=target_sr
            )
        return self.resampler_cache[key]

    def _resample_wav(self, wav_path, expected_sr):
        waveform, orig_sr = torchaudio.load(wav_path)
        if orig_sr == expected_sr and waveform.size(0) == 1:
            return wav_path
        if waveform.size(0) > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if orig_sr != expected_sr:
            resampler = self._get_resampler(orig_sr, expected_sr)
            waveform = resampler(waveform)
        wav_tensor = waveform.squeeze(0)
        wav_numpy = wav_tensor.cpu().numpy()
        tmp_fh = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp_fh.name
        tmp_fh.close()
        sf.write(tmp_path, wav_numpy, expected_sr, subtype="PCM_16")
        return tmp_path

    def _synthesize_with_kokoro(self, engine, sentence, voice_id):
        """
        Synthesize a sentence with Kokoro (kokoro-onnx wrappers).
        Try a few common method names used by community wrappers.
        Must return a 1D numpy float array.
        """
        if engine is None:
            return np.array([])

        trial_errors = []

        # Try engine.tts(text, voice=...)
        for fn_name in ("tts", "synthesize", "speak", "generate", "__call__"):
            try:
                fn = getattr(engine, fn_name, None)
                if callable(fn):
                    # Try calling with named args
                    try:
                        out = fn(text=sentence, voice=voice_id)
                    except TypeError:
                        try:
                            out = fn(sentence, voice_id)  # positional
                        except TypeError:
                            out = fn(sentence)  # fallback

                    # Normalize output: expect (audio, sr) or audio
                    sr = models[TTS_ENGINES['KOKORO']][self.session['fine_tuned']]['samplerate']
                    if isinstance(out, tuple) and len(out) >= 1:
                        audio = out[0]
                        if len(out) >= 2 and isinstance(out[1], (int, float)):
                            sr = int(out[1])
                    else:
                        audio = out

                    # Convert to numpy float 1D
                    if isinstance(audio, torch.Tensor):
                        audio = audio.detach().cpu().float().numpy()
                    elif isinstance(audio, list):
                        audio = np.array(audio, dtype=np.float32)
                    elif isinstance(audio, np.ndarray):
                        audio = audio.astype(np.float32, copy=False)

                    # resample if needed and ensure mono
                    if audio is not None and audio.size > 0:
                        if audio.ndim > 1:
                            audio = np.mean(audio, axis=0).astype(np.float32)
                        target_sr = models[TTS_ENGINES['KOKORO']][self.session['fine_tuned']]['samplerate']
                        if sr != target_sr:
                            # Save to temp with original sr -> resample via torchaudio
                            tmp_fh = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                            tmp_in = tmp_fh.name
                            tmp_fh.close()
                            sf.write(tmp_in, audio, sr, subtype="PCM_16")
                            tmp_out = self._resample_wav(tmp_in, target_sr)
                            # load resampled
                            wav, _ = torchaudio.load(tmp_out)
                            os.remove(tmp_in)
                            if os.path.exists(tmp_out):
                                os.remove(tmp_out)
                            audio = wav.squeeze(0).cpu().numpy().astype(np.float32)
                        return audio
            except Exception as e:
                trial_errors.append(f"{fn_name}: {e}")

        if trial_errors:
            print("Kokoro synthesis attempts failed:", "; ".join(trial_errors))
        return np.array([])

    def convert(self, sentence_number, sentence):
        try:
            audio_data = False
            trim_audio_buffer = 0.004
            settings = self.params[self.session['tts_engine']]
            final_sentence_file = os.path.join(self.session['chapters_dir_sentences'], f'{sentence_number}.{default_audio_proc_format}')
            sentence = sentence.strip()

            # Reference voice path for VC-based cloning (same as Piper flow)
            settings['voice_path'] = self.session.get('voice', None)

            tts = (loaded_tts.get(self.tts_key) or {}).get('engine', False)
            if tts:
                # SML handling
                if sentence and sentence[-1].isalnum():
                    sentence = f'{sentence} —'
                if sentence == TTS_SML['break']:
                    break_tensor = torch.zeros(1, int(settings['samplerate'] * (int(np.random.uniform(0.3, 0.6) * 100) / 100)))
                    self.audio_segments.append(break_tensor.clone())
                    return True
                elif sentence == TTS_SML['pause']:
                    pause_tensor = torch.zeros(1, int(settings['samplerate'] * (int(np.random.uniform(1.0, 1.8) * 100) / 100)))
                    self.audio_segments.append(pause_tensor.clone())
                    return True
                else:
                    # Pick a reasonable default Kokoro voice id by language
                    voice_id = self._default_voice_by_lang()

                    # 1) Synthesize with Kokoro
                    audio_sentence = self._synthesize_with_kokoro(tts, sentence, voice_id)

                    # 2) If a reference voice is provided, perform VC-based cloning (as in Piper)
                    if settings.get('voice_path'):
                        try:
                            proc_dir = os.path.join(self.session['voice_dir'], 'proc')
                            os.makedirs(proc_dir, exist_ok=True)
                            tmp_in_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")
                            tmp_out_wav = os.path.join(proc_dir, f"{uuid.uuid4()}.wav")

                            # Save Kokoro output to tmp
                            if is_audio_data_valid(audio_sentence):
                                sf.write(tmp_in_wav, audio_sentence, settings['samplerate'], subtype="PCM_16")
                            else:
                                sf.write(tmp_in_wav, np.zeros(int(settings['samplerate'] * 0.1), dtype=np.float32), settings['samplerate'], subtype="PCM_16")

                            # Cache semitones based on gender detection
                            if settings['voice_path'] in settings['semitones'].keys():
                                semitones = settings['semitones'][settings['voice_path']]
                            else:
                                voice_path_gender = detect_gender(settings['voice_path'])
                                voice_builtin_gender = detect_gender(tmp_in_wav)
                                print(f"Cloned voice seems to be {voice_path_gender}\nBuiltin voice seems to be {voice_builtin_gender}")
                                if voice_builtin_gender != voice_path_gender and voice_path_gender in ['male', 'female'] and voice_builtin_gender in ['male', 'female']:
                                    semitones = -4 if voice_path_gender == 'male' else 4
                                    print("Adapting builtin voice frequencies from the clone voice...")
                                else:
                                    semitones = 0
                                settings['semitones'][settings['voice_path']] = semitones

                            # Pitch shift (if needed) using sox
                            if semitones != 0:
                                try:
                                    cmd = [
                                        shutil.which('sox'), tmp_in_wav,
                                        "-r", str(settings['samplerate']), tmp_out_wav,
                                        "pitch", str(semitones * 100)
                                    ]
                                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                                except Exception as e:
                                    print(f"Pitch shift failed: {e}")
                                    tmp_out_wav = tmp_in_wav
                            else:
                                tmp_out_wav = tmp_in_wav

                            # Load VC engine and perform conversion
                            tts_vc = (loaded_tts.get(self.tts_vc_key) or {}).get('engine', False)
                            if not tts_vc:
                                tts_vc = self._load_vc_engine(self.tts_vc_key, default_vc_model, self.session['device'])
                            if tts_vc:
                                # Use VC samplerate
                                settings['samplerate'] = TTS_VOICE_CONVERSION[self.tts_vc_key]['samplerate']
                                source_wav = self._resample_wav(tmp_out_wav, settings['samplerate'])
                                target_wav = self._resample_wav(settings['voice_path'], settings['samplerate'])
                                audio_sentence = tts_vc.voice_conversion(
                                    source_wav=source_wav,
                                    target_wav=target_wav
                                )
                                if os.path.exists(source_wav) and source_wav != tmp_out_wav:
                                    os.remove(source_wav)
                            else:
                                print(f'Engine {self.tts_vc_key} is None; skipping voice cloning.')

                            # Cleanup temp files
                            if os.path.exists(tmp_in_wav):
                                os.remove(tmp_in_wav)
                            if os.path.exists(tmp_out_wav) and tmp_out_wav != tmp_in_wav:
                                os.remove(tmp_out_wav)
                        except Exception as e:
                            print(f"Kokoro VC cloning path failed, proceeding with Kokoro voice only. Error: {e}")

                    # 3) Post-processing, timing, and save
                    if is_audio_data_valid(audio_sentence):
                        sourceTensor = torch.tensor(audio_sentence, dtype=torch.float32)
                        audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                        if sentence[-1].isalnum() or sentence[-1] == '—':
                            audio_tensor = trim_audio(audio_tensor.squeeze(), settings['samplerate'], 0.003, trim_audio_buffer).unsqueeze(0)
                        self.audio_segments.append(audio_tensor)

                        if not re.search(r'\w$', sentence, flags=re.UNICODE):
                            break_tensor = torch.zeros(1, int(settings['samplerate'] * (int(np.random.uniform(0.3, 0.6) * 100) / 100)))
                            self.audio_segments.append(break_tensor.clone())

                        if self.audio_segments:
                            audio_tensor = torch.cat(self.audio_segments, dim=-1)
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
                                del audio_tensor

                        # Reset aggregated segments
                        self.audio_segments = []

                        if os.path.exists(final_sentence_file):
                            return True
                        else:
                            print(f"Cannot create {final_sentence_file}")
            else:
                print(f"convert() error: {self.session['tts_engine']} is None")
        except Exception as e:
            raise ValueError(f'Kokoro.convert(): {e}')
        return False