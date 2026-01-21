import os, threading, gc, torch, torchaudio, shutil, tempfile, regex as re, soundfile as sf, numpy as np, gradio as gr
from lib.classes.tts_engines.common.audio import is_audio_data_valid

from typing import Any, Union, Dict
from huggingface_hub import hf_hub_download
from safetensors.torch import save_file
from tqdm import tqdm
from pathlib import Path
from torch import Tensor
from torch.nn import Module

from lib.classes.vram_detector import VRAMDetector
from lib.classes.tts_engines.common.audio import normalize_audio, get_audiolist_duration
from lib import *

_lock = threading.Lock()

class TTSUtils:

    def _cleanup_memory(self)->None:
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.synchronize()

    def _loaded_tts_size_gb(self, loaded_tts:Dict[str, Module])->float:
        total_bytes = 0
        for model in loaded_tts.values():
            try:
                total_bytes += model_size_bytes(model)
            except Exception:
                pass
        gb = total_bytes / (1024 ** 3)
        return round(gb, 2)

    def _load_xtts_builtin_list(self)->dict:
        try:
            if len(xtts_builtin_speakers_list) > 0:
                return xtts_builtin_speakers_list
            speakers_path = hf_hub_download(repo_id=default_engine_settings[TTS_ENGINES['XTTSv2']]['repo'], filename='speakers_xtts.pth', cache_dir=tts_dir)
            loaded = torch.load(speakers_path, weights_only=False)
            if not isinstance(loaded, dict):
                raise TypeError(
                    f"Invalid XTTS speakers format: {type(loaded)}"
                )
            for name, data in loaded.items():
                if name not in xtts_builtin_speakers_list:
                    xtts_builtin_speakers_list[name] = data
            return xtts_builtin_speakers_list
        except Exception as error:
            raise RuntimeError(
                "self._load_xtts_builtin_list() failed"
            ) from error

    def _apply_gpu_policy(self, enough_vram: bool, seed: int) -> torch.dtype:
        using_gpu = self.session['device'] != devices['CPU']['proc']
        device = self.session['device']
        torch.manual_seed(seed)
        has_cuda = hasattr(torch, "cuda") and torch.cuda.is_available()
        has_mps = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
        has_xpu = hasattr(torch, "xpu") and torch.xpu.is_available()
        is_rocm = bool(getattr(torch.version, "hip", None))
        is_cuda = bool(getattr(torch.version, "cuda", None)) and not is_rocm
        quality_mode = bool(using_gpu and enough_vram)
        amp_dtype = torch.float32
        # Default matmul precision (PyTorch >= 2.2)
        try:
            torch.set_float32_matmul_precision("high" if quality_mode else "medium")
        except Exception:
            pass
        if not using_gpu:
            return amp_dtype
        # ================= CUDA / Jetson / ROCm =================
        if has_cuda:
            try:
                torch.cuda.manual_seed_all(seed)
            except Exception:
                pass
            # Memory pressure handling
            if hasattr(torch.cuda, "set_per_process_memory_fraction"):
                try:
                    torch.cuda.set_per_process_memory_fraction(0.95 if quality_mode else 0.70)
                except Exception:
                    pass
            # cuDNN base config
            if hasattr(torch.backends, "cudnn"):
                torch.backends.cudnn.enabled = True
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = bool(quality_mode)
            # Detect Jetson (ARM + CUDA)
            is_jetson = False
            try:
                is_jetson = is_cuda and torch.cuda.get_device_properties(0).multi_processor_count < 32
            except Exception:
                is_jetson = False
            # TF32 handling
            tf32_ok = False
            if is_cuda and not is_jetson:
                try:
                    cc_major = torch.cuda.get_device_capability(0)[0]
                    tf32_ok = bool(cc_major >= 8 and quality_mode)
                except Exception:
                    tf32_ok = False
            # Disable TF32 explicitly on Jetson + ROCm
            if is_jetson or is_rocm:
                tf32_ok = False
            # Apply matmul / cuDNN flags
            if hasattr(torch.backends, "cuda") and hasattr(torch.backends.cuda, "matmul"):
                try:
                    torch.backends.cuda.matmul.allow_tf32 = tf32_ok
                    torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction = bool(quality_mode)
                except Exception:
                    pass
            if hasattr(torch.backends, "cudnn"):
                try:
                    torch.backends.cudnn.allow_tf32 = tf32_ok
                except Exception:
                    pass
            # AMP dtype selection
            # Jetson + ROCm → FP16 only (BF16 unstable / slow)
            if is_jetson or is_rocm:
                amp_dtype = torch.float16
            else:
                if quality_mode:
                    try:
                        if hasattr(torch.cuda, "is_bf16_supported") and torch.cuda.is_bf16_supported():
                            #amp_dtype = torch.bfloat16
                            amp_dtype = torch.float16
                        else:
                            amp_dtype = torch.float16
                    except Exception:
                        amp_dtype = torch.float16
                else:
                    amp_dtype = torch.float16

            return amp_dtype
        # ================= Apple MPS =================
        if has_mps:
            try:
                torch.mps.manual_seed(seed)
            except Exception:
                pass
            try:
                if quality_mode and hasattr(torch.backends.mps, "is_bf16_supported") and torch.backends.mps.is_bf16_supported():
                    #amp_dtype = torch.bfloat16
                    amp_dtype = torch.float16
                else:
                    amp_dtype = torch.float16
            except Exception:
                amp_dtype = torch.float16
            return amp_dtype
        # ================= Intel XPU =================
        if has_xpu:
            try:
                torch.xpu.manual_seed_all(seed)
            except Exception:
                try:
                    torch.xpu.manual_seed(seed)
                except Exception:
                    pass
            #return torch.bfloat16
            return torch.float16
        return amp_dtype

    def _load_api(self, key:str, model_path:str)->Any:
        try:
            with _lock:
                from TTS.api import TTS as TTSEngine
                engine = loaded_tts.get(key, False)
                if not engine:
                    engine = TTSEngine(model_path)
                if engine:
                    vram_dict = VRAMDetector().detect_vram(self.session['device'], self.session['script_mode'])
                    self.session['free_vram_gb'] = vram_dict.get('free_vram_gb', 0)
                    models_loaded_size_gb = self._loaded_tts_size_gb(loaded_tts)
                    if self.session['free_vram_gb'] > models_loaded_size_gb:
                        loaded_tts[key] = engine
                return engine
        except Exception as e:
            error = f"_load_api() error: {e}"
            print(error)
            return None

    def _load_checkpoint(self,**kwargs:Any)->Any:
        try:
            with _lock:
                key = kwargs.get('key')
                engine = loaded_tts.get(key, False)
                if not engine:
                    engine_name = kwargs.get('tts_engine', None)
                    from TTS.tts.configs.xtts_config import XttsConfig
                    from TTS.tts.models.xtts import Xtts
                    checkpoint_path = kwargs.get('checkpoint_path')
                    config_path = kwargs.get('config_path',None)
                    vocab_path = kwargs.get('vocab_path',None)
                    if not checkpoint_path or not os.path.exists(checkpoint_path):
                        error = f'Missing or invalid checkpoint_path: {checkpoint_path}'
                        raise FileNotFoundError(error)
                        return False
                    if not config_path or not os.path.exists(config_path):
                        error = f'Missing or invalid config_path: {config_path}'
                        raise FileNotFoundError(error)
                        return False
                    config = XttsConfig()
                    config.models_dir = os.path.join("models","tts")
                    config.load_json(config_path)
                    engine = Xtts.init_from_config(config)
                    engine.load_checkpoint(
                        config,
                        checkpoint_path = checkpoint_path,
                        vocab_path = vocab_path,
                        eval = True
                    ) 
                if engine:
                    vram_dict = VRAMDetector().detect_vram(self.session['device'], self.session['script_mode'])
                    self.session['free_vram_gb'] = vram_dict.get('free_vram_gb', 0)
                    models_loaded_size_gb = self._loaded_tts_size_gb(loaded_tts)
                    if self.session['free_vram_gb'] > models_loaded_size_gb:
                        loaded_tts[key] = engine
                return engine
        except Exception as e:
            error = f'_load_checkpoint() error: {e}'
            print(error)
            return None

    def _load_engine_zs(self)->Any:
        try:
            msg = f"Loading ZeroShot {self.tts_zs_key} model, it takes a while, please be patient..."
            print(msg)
            self._cleanup_memory()
            engine_zs = loaded_tts.get(self.tts_zs_key, False)
            if not engine_zs:
                engine_zs = self._load_api(self.tts_zs_key, default_vc_model)
            if engine_zs:
                self.session['model_zs_cache'] = self.tts_zs_key
                msg = f'ZeroShot {self.tts_zs_key} Loaded!'
                return engine_zs
        except Exception as e:
            error = f'_load_engine_zs() error: {e}'
            raise ValueError(error)

    def _check_xtts_builtin_speakers(self, voice_path:str, speaker:str)->str|bool:
        new_voice_path = ''
        proc_voice_path = ''
        try:
            voice_parts = Path(voice_path).parts
            if (self.session['language'] in voice_parts or speaker in default_engine_settings[TTS_ENGINES['BARK']]['voices'] or self.session['language'] == 'eng'):
                return voice_path
            xtts = TTS_ENGINES['XTTSv2']
            if self.session['language'] in default_engine_settings[xtts].get('languages', {}):
                default_text_file = os.path.join(voices_dir, self.session['language'], 'default.txt')
                if os.path.exists(default_text_file):
                    msg = f"Converting builtin eng voice to {self.session['language']}..."
                    print(msg)
                    key = f"{xtts}-internal"
                    default_text = Path(default_text_file).read_text(encoding="utf-8")
                    self._cleanup_memory()
                    engine = loaded_tts.get(key, False)
                    if not engine:
                        vram_dict = VRAMDetector().detect_vram(self.session['device'], self.session['script_mode'])
                        self.session['free_vram_gb'] = vram_dict.get('free_vram_gb', 0)
                        models_loaded_size_gb = self._loaded_tts_size_gb(loaded_tts)
                        if self.session['free_vram_gb'] <= models_loaded_size_gb:
                            del loaded_tts[self.tts_key]
                        hf_repo = default_engine_settings[xtts]['repo']
                        hf_sub = ''
                        config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{default_engine_settings[xtts]['files'][0]}", cache_dir=self.cache_dir)
                        checkpoint_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{default_engine_settings[xtts]['files'][1]}", cache_dir=self.cache_dir)
                        vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{default_engine_settings[xtts]['files'][2]}", cache_dir=self.cache_dir)
                        engine = self._load_checkpoint(tts_engine=xtts, key=key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path)
                    if engine:
                        device = devices['CUDA']['proc'] if self.session['device'] in ['cuda', 'jetson'] else self.session['device']
                        if speaker in default_engine_settings[xtts]['voices'].keys():
                            gpt_cond_latent, speaker_embedding = self.xtts_speakers[default_engine_settings[xtts]['voices'][speaker]].values()
                        else:
                            gpt_cond_latent, speaker_embedding = engine.get_conditioning_latents(audio_path=[voice_path], librosa_trim_db=30, load_sr=24000, sound_norm_refs=True)
                        fine_tuned_params = {
                            key.removeprefix("xtts_"): cast_type(self.session[key])
                            for key, cast_type in {
                                "xtts_temperature": float,
                                #"xtts_codec_temperature": float,
                                "xtts_length_penalty": float,
                                "xtts_num_beams": int,
                                "xtts_repetition_penalty": float,
                                #"xtts_cvvp_weight": float,
                                "xtts_top_k": int,
                                "xtts_top_p": float,
                                "xtts_speed": float,
                                #"xtts_gpt_cond_len": int,
                                #"xtts_gpt_batch_size": int,
                                "xtts_enable_text_splitting": bool
                            }.items()
                            if self.session.get(key) is not None
                        }
                        with torch.no_grad():
                            engine.to(device)
                            if device == devices['CPU']['proc']:
                                result = engine.inference(
                                    text=default_text.strip(),
                                    language=self.session['language_iso1'],
                                    gpt_cond_latent=gpt_cond_latent,
                                    speaker_embedding=speaker_embedding,
                                    **fine_tuned_params,
                                )
                            else:
                                with torch.autocast(
                                    device_type=device,
                                    dtype=self.amp_dtype
                                ):
                                    result = engine.inference(
                                        text=default_text.strip(),
                                        language=self.session['language_iso1'],
                                        gpt_cond_latent=gpt_cond_latent,
                                        speaker_embedding=speaker_embedding,
                                        **fine_tuned_params,
                                    )
                            engine.to(devices['CPU']['proc'])
                        audio_sentence = result.get('wav')
                        if is_audio_data_valid(audio_sentence):
                            sourceTensor = self._tensor_type(audio_sentence)
                            audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                            if audio_tensor is not None and audio_tensor.numel() > 0:
                                # CON is a reserved name on windows
                                lang_dir = 'con-' if self.session['language'] == 'con' else self.session['language']
                                new_voice_path = re.sub(r'([\\/])eng([\\/])', rf'\1{lang_dir}\2', voice_path)
                                proc_voice_path = new_voice_path.replace('.wav', '_temp.wav')
                                torchaudio.save(proc_voice_path, audio_tensor, default_engine_settings[xtts]['samplerate'], format='wav')
                                if normalize_audio(proc_voice_path, new_voice_path, default_audio_proc_samplerate, self.session['is_gui_process']):
                                    del audio_sentence, sourceTensor, audio_tensor
                                    Path(proc_voice_path).unlink(missing_ok=True)
                                    gc.collect()
                                    self.engine = loaded_tts.get(self.tts_key, False)
                                    if not self.engine:
                                        self._load_engine()
                                    return new_voice_path
                                else:
                                    error = 'normalize_audio() error:'
                            else:
                                error = f'No audio waveform found in _check_xtts_builtin_speakers() result: {result}'
                    else:
                        error = f"_check_xtts_builtin_speakers() error: {xtts} is False"
                else:
                    error = f'The translated {default_text_file} could not be found! Voice cloning file will stay in English.'
                print(error)
            else:
                return voice_path
        except Exception as e:
            error = f'_check_xtts_builtin_speakers() error: {e}'
            if new_voice_path:
                Path(new_voice_path).unlink(missing_ok=True)
            if proc_voice_path:
                Path(proc_voice_path).unlink(missing_ok=True)
            print(error)
            return False
        
    def _tensor_type(self,audio_data:Any)->torch.Tensor:
        if isinstance(audio_data, torch.Tensor):
            return audio_data
        elif isinstance(audio_data,np.ndarray):
            return torch.from_numpy(audio_data).float()
        elif isinstance(audio_data,list):
            return torch.tensor(audio_data,dtype=torch.float32)
        else:
            raise TypeError(f"_tensor_type() error: Unsupported type for audio_data: {type(audio_data)}")
            
    def _get_resampler(self,orig_sr:int,target_sr:int)->torchaudio.transforms.Resample:
        key=(orig_sr,target_sr)
        if key not in self.resampler_cache:
            self.resampler_cache[key]=torchaudio.transforms.Resample(
                orig_freq = orig_sr,new_freq = target_sr
            )
        return self.resampler_cache[key]

    def _resample_wav(self,wav_path:str,expected_sr:int)->str:
        waveform,orig_sr = torchaudio.load(wav_path)
        if orig_sr==expected_sr and waveform.size(0)==1:
            return wav_path
        if waveform.size(0)>1:
            waveform = waveform.mean(dim=0,keepdim=True)
        if orig_sr!=expected_sr:
            resampler = self._get_resampler(orig_sr,expected_sr)
            waveform = resampler(waveform)
        wav_tensor = waveform.squeeze(0)
        wav_numpy = wav_tensor.cpu().numpy()
        resample_tmp = os.path.join(self.session['process_dir'], 'tmp')
        os.makedirs(resample_tmp, exist_ok=True)
        tmp_fh = tempfile.NamedTemporaryFile(dir=resample_tmp, suffix=".wav", delete=False)
        tmp_path = tmp_fh.name
        tmp_fh.close()
        sf.write(tmp_path,wav_numpy,expected_sr,subtype="PCM_16")
        return tmp_path

    def _set_voice(self)->bool:
        self.params['voice_path'] = (
            self.session['voice'] if self.session['voice'] is not None 
            else self.models[self.session['fine_tuned']]['voice']
        )
        if self.params['voice_path'] is not None:
            self.speaker = re.sub(r'\.wav$', '', os.path.basename(self.params['voice_path']))
            if self.params['voice_path'] not in default_engine_settings[TTS_ENGINES['BARK']]['voices'].keys() and self.session['custom_model_dir'] not in self.params['voice_path']:
                self.session['voice'] = self.params['voice_path'] = self._check_xtts_builtin_speakers(self.params['voice_path'], self.speaker)
                if not self.params['voice_path']:
                    msg = f"_set_voice() error: Could not create the builtin speaker selected voice in {self.session['language']}"
                    print(msg)
                    return False
        return True

    def _convert_sml(self, sml:str)->bool:
        m = SML_TAG_PATTERN.fullmatch(sml)
        if not m:
            return False
        if m.group("tag1"):
            tag = m.group("tag1")
            close = bool(m.group("close1"))
            value = m.group("value1")
        elif m.group("tag2"):
            tag = m.group("tag2")
            close = bool(m.group("close2"))
            value = m.group("value2")
        else:
            return False
        assert tag in TTS_SML, f"Unknown SML tag: {tag!r}"
        if tag == "break":
            silence_time = float(int(np.random.uniform(0.3, 0.6) * 100) / 100)
        elif tag == "pause":
            silence_time = float(value) if value else float(int(np.random.uniform(1.0, 1.6) * 100) / 100)
        elif tag == "voice":
            if close:
                return self._set_voice()
            assert value is not None, "voice tag requires a value"
            voice_path = os.path.abspath(value)
            if not os.path.exists(voice_path):
                print(f"_convert_sml() error: voice {voice_path} does not exist!")
                return False
            self.params["voice_path"] = voice_path
            return self._set_voice()
        else:
            return False
        self.audio_segments.append(
            torch.zeros(1, int(self.params["samplerate"] * silence_time)).clone()
        )
        return True

    def _format_timestamp(self, seconds: float) -> str:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02}:{int(m):02}:{s:06.3f}"

    def _build_vtt_file(self, all_sentences: list, audio_dir: str, vtt_path: str) -> bool:
        try:
            msg = 'VTT file creation started...'
            print(msg)
            audio_sentences_dir = Path(audio_dir)
            audio_files = sorted(
                audio_sentences_dir.glob(f"*.{default_audio_proc_format}"),
                key=lambda p: int(p.stem)
            )
            all_sentences_length = len(all_sentences)
            audio_files_length = len(audio_files)
            expected_indices = list(range(audio_files_length))
            actual_indices = [int(p.stem) for p in audio_files]
            if actual_indices != expected_indices:
                missing = sorted(set(expected_indices) - set(actual_indices))
                error = f"Missing audio sentence files: {missing}"
                print(error)
                return False
            if audio_files_length != all_sentences_length:
                error = f"Audio/sentence mismatch: {audio_files_length} audio files vs {all_sentences_length} sentences"
                print(error)
                return False
            sentences_total_time = 0.0
            vtt_blocks = []
            if self.session['is_gui_process']:
                progress_bar = gr.Progress(track_tqdm=False)
            chunks_size = 892
            durations_map = {}
            msg = 'Get duration of each sentence...'
            print(msg)
            for i in range(0, len(audio_files), chunks_size):
                chunk = audio_files[i:i + chunks_size]
                durations_map.update(get_audiolist_duration(list(map(str, chunk))))
            msg = 'Create VTT blocks...'
            print(msg)
            with tqdm(total=audio_files_length, unit='files') as t:
                for idx, file in enumerate(audio_files):
                    start_time = sentences_total_time
                    duration = durations_map.get(str(file), 0.0)
                    end_time = start_time + duration
                    sentences_total_time = end_time
                    start = self._format_timestamp(start_time)
                    end = self._format_timestamp(end_time)
                    text = re.sub(
                        r'\s+',
                        ' ',
                        default_backend_sml_pattern.sub('', str(all_sentences[idx]))
                    ).strip()
                    vtt_blocks.append(f"{start} --> {end}\n{text}\n")
                    if self.session['is_gui_process']:
                        total_progress = (t.n + 1) / audio_files_length
                        progress_bar(
                            progress=total_progress,
                            desc=f'Writing vtt idx {idx}'
                        )
                    t.update(1)
            msg = 'Write VTT blocks into file...'
            print(msg)
            with open(vtt_path, "w", encoding="utf-8") as f:
                f.write("WEBVTT\n\n")
                f.write("\n".join(vtt_blocks))
            return True
        except Exception as e:
            error = f'_build_vtt_file(): {e}'
            print(error)
            return False