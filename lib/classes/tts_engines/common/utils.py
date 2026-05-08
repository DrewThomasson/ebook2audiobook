import os, sys, threading, gc, ctypes, shutil, tempfile, warnings, regex as re

from typing import Any, Union, Dict, TYPE_CHECKING
from cryptography.fernet import Fernet
from pathlib import Path

from lib.classes.vram_detector import VRAMDetector
from lib.classes.tts_engines.common.audio import normalize_audio, get_audiolist_duration, is_audio_data_valid
from lib import *

os.environ['HF_TOKEN'] = Fernet(fernet_key.encode('utf-8')).decrypt(fernet_data).decode('utf-8')

_lock = threading.Lock()

if TYPE_CHECKING:
    import torch
    from torch import Tensor
    from torch.nn import Module
    from torchaudio.transforms import Resample

def _format_timestamp(seconds:float)->str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f'{int(h):02}:{int(m):02}:{s:06.3f}'

def build_vtt_file(session:dict, vtt_path:str=None, block_indices:set=None)->tuple:
    try:
        import gradio as gr
        from tqdm import tqdm
        msg = 'VTT file creation started…'
        print(msg)
        if vtt_path is None:
            vtt_path = os.path.join(session['process_dir'], Path(session['final_name']).stem + '.vtt')
        audio_sentences_dir = Path(session['sentences_dir'])
        blocks = session['blocks_current']['blocks']
        audio_files = []
        sentences_to_use = []
        for i, block in enumerate(blocks):
            if not (block['keep'] and block['text'].strip()):
                continue
            if block_indices is not None and i not in block_indices:
                continue
            block_dir = audio_sentences_dir / str(block['id'])
            if not block_dir.is_dir():
                error = f"Missing audio directory for block {i} (id {block['id']}): {block_dir}"
                return False, error
            block_sentences = block.get('sentences', [])
            for sentence_idx, sentence in enumerate(block_sentences):
                if not any(c.isalnum() for c in str(sentence)):
                    continue
                audio_file = block_dir / f'{sentence_idx}.{default_audio_proc_format}'
                if not audio_file.is_file():
                    error = f"Missing audio file for block {i} (id {block['id']}), sentence {sentence_idx}: {audio_file}"
                    return False, error
                audio_files.append(audio_file)
                sentences_to_use.append(sentence)
        audio_files_length = len(audio_files)
        sentences_total_time = 0.0
        vtt_blocks = []
        if session['is_gui_process']:
            progress_bar = gr.Progress(track_tqdm=False)
        msg = 'Get duration of each sentence…'
        print(msg)
        durations = get_audiolist_duration([str(p) for p in audio_files])
        msg = 'Create VTT blocks…'
        print(msg)
        with tqdm(total=audio_files_length, unit='files') as t:
            for idx, file in enumerate(audio_files):
                start_time = sentences_total_time
                duration = durations.get(os.path.realpath(file), 0.0)
                end_time = start_time + duration
                sentences_total_time = end_time
                start = _format_timestamp(start_time)
                end = _format_timestamp(end_time)
                text = re.sub(
                    r'\s+',
                    ' ',
                    SML_TAG_PATTERN.sub('', str(sentences_to_use[idx]))
                ).strip()
                vtt_blocks.append(f'{start} --> {end}\n{text}\n')
                if session['is_gui_process']:
                    total_progress = (t.n + 1) / audio_files_length
                    progress_bar(
                        progress=total_progress,
                        desc=f'Writing vtt idx {idx}'
                    )
                t.update(1)
        msg = 'Write VTT blocks into file…'
        print(msg)
        with open(vtt_path, 'w', encoding='utf-8') as f:
            f.write('WEBVTT\n\n')
            f.write('\n'.join(vtt_blocks))
        return True, None
    except Exception as e:
        error = f'build_vtt_file(): {e}'
        return False, error

class TTSUtils:

    def cleanup_memory(self)->None:
        import torch
        gc.collect()
        if hasattr(torch, 'clear_autocast_cache'):
            torch.clear_autocast_cache()
        if sys.platform == systems['LINUX']:
            try:
                libc = ctypes.CDLL('libc.so.6')
                libc.malloc_trim(0)
            except Exception:
                pass
        elif sys.platform == systems['WINDOWS']:
            try:
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.GetCurrentProcess()
                kernel32.SetProcessWorkingSetSize(
                    handle, ctypes.c_size_t(-1), ctypes.c_size_t(-1)
                )
            except Exception:
                pass
        if torch.cuda.is_available():
            torch.cuda.ipc_collect()
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
        if hasattr(torch, 'xpu') and torch.xpu.is_available():
            torch.xpu.synchronize()
            torch.xpu.empty_cache()

    def _model_size_bytes(self, model:Any)->int:
        total = 0
        try:
            for p in model.parameters():
                total += p.numel() * p.element_size()
        except Exception:
            pass
        try:
            for b in model.buffers():
                total += b.numel() * b.element_size()
        except Exception:
            pass
        return total

    def _loaded_tts_size_gb(self, loaded_tts:Dict[str, 'Module'])->float:
        total_bytes = 0
        for model in loaded_tts.values():
            try:
                total_bytes += self.model_size_bytes(model)
            except Exception:
                pass
        gb = total_bytes / (1024 ** 3)
        return round(gb, 2)

    def _load_xtts_builtin_list(self)->dict:
        try:
            import torch
            from huggingface_hub import hf_hub_download
            if len(xtts_builtin_speakers_list) > 0:
                return xtts_builtin_speakers_list
            speakers_path = hf_hub_download(repo_id=default_engine_settings[TTS_ENGINES['XTTSv2']]['repo'], filename='speakers_xtts.pth', cache_dir=tts_dir)
            loaded = torch.load(speakers_path, weights_only=False)
            if not isinstance(loaded, dict):
                error = f'Invalid XTTS speakers format: {type(loaded)}'
                raise TypeError(error)
            for name, data in loaded.items():
                if name not in xtts_builtin_speakers_list:
                    xtts_builtin_speakers_list[name] = data
            return xtts_builtin_speakers_list
        except Exception as e:
            error = f'self._load_xtts_builtin_list() failed: {e}'
            raise RuntimeError(error)

    def _apply_gpu_policy(self, enough_vram:bool, seed:int)->'torch.dtype':
        import torch
        using_gpu = self.session['device'] != devices['CPU']['proc']
        device = self.session['device']
        torch.manual_seed(seed)
        has_cuda = hasattr(torch, 'cuda') and torch.cuda.is_available()
        has_mps = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
        has_xpu = hasattr(torch, 'xpu') and torch.xpu.is_available()
        is_rocm = bool(getattr(torch.version, 'hip', None))
        is_cuda = bool(getattr(torch.version, 'cuda', None)) and not is_rocm
        quality_mode = bool(using_gpu and enough_vram)
        amp_dtype = torch.float32  # float32 means: caller should NOT wrap in autocast
        # Default matmul precision (PyTorch >= 2.2)
        try:
            torch.set_float32_matmul_precision('high' if quality_mode else 'medium')
        except Exception:
            pass
        if not using_gpu:
            return amp_dtype
        if has_cuda:
            amp_dtype = torch.float16
            # --- CUDA health check: fail fast instead of configuring a broken context ---
            try:
                torch.cuda.manual_seed_all(seed)
            except Exception as e:
                error = f'[_apply_gpu_policy] CUDA init failed ({e!r}), falling back to FP32'
                print(error)
                return torch.float32
            # --- Device info (fetched once) ---
            try:
                cc = torch.cuda.get_device_capability(0)
                cc_major = cc[0]
            except Exception:
                cc = (0, 0)
                cc_major = 0
            # Detect Jetson (ARM + CUDA)
            is_jetson = False
            try:
                import platform
                is_jetson = is_cuda and platform.machine() in ('aarch64', 'arm64')
            except Exception:
                is_jetson = False
            # Memory pressure handling — only throttle on cards with headroom
            if hasattr(torch.cuda, 'set_per_process_memory_fraction'):
                try:
                    total_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
                    if total_gb >= 10:
                        torch.cuda.set_per_process_memory_fraction(0.90 if quality_mode else 0.80)
                    # else: let the caching allocator breathe on 6–8 GB cards
                except Exception:
                    pass
            # cuDNN base config — benchmark=True is bad for TTS (variable-length inputs)
            if hasattr(torch.backends, 'cudnn'):
                try:
                    torch.backends.cudnn.enabled = True
                    torch.backends.cudnn.benchmark = False
                    torch.backends.cudnn.deterministic = not quality_mode
                except Exception:
                    pass
            # TF32 — Ampere+, non-Jetson, non-ROCm, quality mode only
            tf32_ok = bool(
                is_cuda and not is_jetson and not is_rocm
                and cc_major >= 8 and quality_mode
            )
            # SDP attention — flash + mem-efficient are Ampere+ only; math kernel always on
            if hasattr(torch.backends, 'cuda'):
                try:
                    torch.backends.cuda.enable_flash_sdp(cc_major >= 8)
                    torch.backends.cuda.enable_mem_efficient_sdp(cc_major >= 8)
                    torch.backends.cuda.enable_math_sdp(True)
                except Exception:
                    pass
            # Matmul / cuDNN flags
            if hasattr(torch.backends, 'cuda') and hasattr(torch.backends.cuda, 'matmul'):
                try:
                    torch.backends.cuda.matmul.allow_tf32 = tf32_ok
                    # Reduced-precision reduction is only safe on Ampere+ tensor cores.
                    torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction = (
                        bool(quality_mode) and cc_major >= 8
                    )
                except Exception:
                    pass
            if hasattr(torch.backends, 'cudnn'):
                try:
                    torch.backends.cudnn.allow_tf32 = tf32_ok
                except Exception:
                    pass
            return amp_dtype
        # ================= Apple MPS =================
        if has_mps:
            torch.mps.manual_seed(seed)
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

    def _load_api(self, key:str, model_path:str, device:str)->Any:
        try:
            with _lock:
                from TTS.api import TTS as TTSEngine
                import torch
                import torch.nn as nn
                engine = loaded_tts.get(key)
                target_dev = torch.device(device)
                is_accel = target_dev.type != 'cpu'
                if not engine:
                    engine = TTSEngine(model_path).to(device)
                if not engine:
                    raise RuntimeError('TTSEngine returned None')
                for syn_attr in ('synthesizer', 'voice_converter'):
                    syn = getattr(engine, syn_attr, None)
                    if syn is None:
                        continue
                    syn.use_cuda = is_accel
                    for _, m in syn.named_modules():
                        m.to(device)
                        m.eval()
                        for pname, p in list(m.named_parameters(recurse=False)):
                            if p.device != target_dev:
                                with torch.no_grad():
                                    new_p = nn.Parameter(p.data.to(device), requires_grad=p.requires_grad)
                                setattr(m, pname, new_p)
                        for bname, b in list(m.named_buffers(recurse=False)):
                            if b.device != target_dev:
                                persistent = bname not in m._non_persistent_buffers_set
                                m.register_buffer(bname, b.to(device), persistent=persistent)
                vram_dict = VRAMDetector().detect_vram(self.session['device'], self.session['script_mode'])
                self.session['free_vram_gb'] = vram_dict.get('free_vram_gb', 0)
                models_loaded_size_gb = self._loaded_tts_size_gb(loaded_tts)
                if self.session['free_vram_gb'] > models_loaded_size_gb:
                    loaded_tts[key] = engine
                return engine
        except Exception as e:
            error = f'_load_api() error: {e}'
            print(error)
            raise

    def _load_checkpoint(self,**kwargs:Any)->Any:
        try:
            with _lock:
                import torch
                import torch.nn as nn
                key = kwargs.get('key')
                engine = loaded_tts.get(key, False)
                device = kwargs.get('device', 'cpu')
                target_dev = torch.device(device)
                if not engine:
                    engine_name = kwargs.get('tts_engine', None)
                    from TTS.tts.configs.xtts_config import XttsConfig
                    from TTS.tts.models.xtts import Xtts
                    checkpoint_path = kwargs.get('checkpoint_path')
                    config_path = kwargs.get('config_path', None)
                    vocab_path = kwargs.get('vocab_path', None)
                    if not checkpoint_path or not os.path.exists(checkpoint_path):
                        error = f'Missing or invalid checkpoint_path: {checkpoint_path}'
                        raise FileNotFoundError(error)
                    if not config_path or not os.path.exists(config_path):
                        error = f'Missing or invalid config_path: {config_path}'
                        raise FileNotFoundError(error)
                    config = XttsConfig()
                    config.models_dir = os.path.join('models','tts')
                    config.load_json(config_path)
                    engine = Xtts.init_from_config(config)
                    engine.load_checkpoint(
                        config,
                        checkpoint_path = checkpoint_path,
                        vocab_path = vocab_path,
                        eval = True
                    )
                if engine:
                    engine.to(device)
                    engine.eval()
                    for _, m in engine.named_modules():
                        m.to(device)
                        m.eval()
                        for pname, p in list(m.named_parameters(recurse=False)):
                            if p.device != target_dev:
                                with torch.no_grad():
                                    new_p = nn.Parameter(p.data.to(device), requires_grad=p.requires_grad)
                                setattr(m, pname, new_p)
                        for bname, b in list(m.named_buffers(recurse=False)):
                            if b.device != target_dev:
                                persistent = bname not in m._non_persistent_buffers_set
                                m.register_buffer(bname, b.to(device), persistent=persistent)
                    vram_dict = VRAMDetector().detect_vram(self.session['device'], self.session['script_mode'])
                    self.session['free_vram_gb'] = vram_dict.get('free_vram_gb', 0)
                    models_loaded_size_gb = self._loaded_tts_size_gb(loaded_tts)
                    if self.session['free_vram_gb'] > models_loaded_size_gb:
                        loaded_tts[key] = engine
                return engine
        except Exception as e:
            error = f'_load_checkpoint() error: {e}'
            print(error)
            raise

    def _load_engine_zs(self, device:str)->Any:
        try:
            msg = f'Loading ZeroShot {self.tts_zs_key} model, it takes a while, please be patient…'
            print(msg)
            self.cleanup_memory()
            engine_zs = loaded_tts.get(self.tts_zs_key, False)
            if not engine_zs:
                engine_zs = self._load_api(self.tts_zs_key, default_vc_model, device)
            if engine_zs:
                self.session['model_zs_cache'] = self.tts_zs_key
                msg = f'ZeroShot {self.tts_zs_key} Loaded!'
                return engine_zs
        except Exception as e:
            error = f'_load_engine_zs() error: {e}'
            raise ValueError(error)

    def _check_xtts_builtin_speakers(self, current_voice:str, speaker:str)->str|bool:
        new_current_voice = ''
        proc_current_voice = ''
        try:
            import torch
            import torchaudio
            import numpy as np
            from huggingface_hub import hf_hub_download
            voice_parts = Path(current_voice).parts
            if (self.session['language'] in voice_parts or speaker in default_engine_settings[TTS_ENGINES['BARK']]['voices'] or self.session['language'] == 'eng'):
                if os.path.exists(current_voice):
                    return current_voice
            xtts = TTS_ENGINES['XTTSv2']
            if self.session['language'] in default_engine_settings[xtts].get('languages', {}):
                default_text_file = os.path.join(voices_dir, self.session['language'], 'default.txt')
                if os.path.exists(default_text_file):
                    msg = f"Converting builtin eng voice to {self.session['language']}…"
                    print(msg)
                    key = f'{xtts}-internal'
                    default_text = Path(default_text_file).read_text(encoding='utf-8')
                    self.cleanup_memory()
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
                        device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']] else self.session['device']
                        if speaker in default_engine_settings[xtts]['voices'].keys():
                            gpt_cond_latent, speaker_embedding = self.xtts_speakers[default_engine_settings[xtts]['voices'][speaker]].values()
                        else:
                            gpt_cond_latent, speaker_embedding = engine.get_conditioning_latents(audio_path=[current_voice], load_sr=24000, sound_norm_refs=True)
                        fine_tuned_params = {
                            key.removeprefix('xtts_'): cast_type(self.session[key])
                            for key, cast_type in {
                                'xtts_temperature': float,
                                #'xtts_codec_temperature': float,
                                'xtts_length_penalty': float,
                                'xtts_num_beams': int,
                                'xtts_repetition_penalty': float,
                                #'xtts_cvvp_weight': float,
                                'xtts_top_k': int,
                                'xtts_top_p': float,
                                'xtts_speed': float,
                                #'xtts_gpt_cond_len': int,
                                #'xtts_gpt_batch_size': int,
                                'xtts_enable_text_splitting': bool
                            }.items()
                            if self.session.get(key) is not None
                        }
                        engine.to(device)
                        with torch.no_grad():
                            with torch.autocast(device, dtype=self.amp_dtype, enabled=(self.amp_dtype != torch.float32)):
                                result = engine.inference(
                                    text=default_text.strip(),
                                    language=self.session['language_iso1'],
                                    gpt_cond_latent=gpt_cond_latent,
                                    speaker_embedding=speaker_embedding,
                                    **fine_tuned_params,
                                )
                        engine.to(devices['CPU']['proc'])
                        audio_sentence = result.get('wav')
                        if torch.is_tensor(audio_sentence):
                            audio_sentence = audio_sentence.detach().cpu()
                        if is_audio_data_valid(audio_sentence):
                            sourceTensor = self._tensor_type(audio_sentence)
                            audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                            if audio_tensor is not None and audio_tensor.numel() > 0:
                                # CON is a reserved name on windows
                                lang_dir = 'con-' if self.session['language'] == 'con' else self.session['language']
                                # Rebuild the path under the new language folder.
                                # Works for any old-language → any new-language swap (eng→fra, zho→fra, …),
                                # not just eng→X. xtts voices are always absolute paths under voices_dir.
                                voices_root = Path(voices_dir)
                                try:
                                    rel = Path(current_voice).relative_to(voices_root)
                                except ValueError:
                                    error = f'_check_xtts_builtin_speakers() error: {current_voice} is not under {voices_dir}'
                                    print(error)
                                    return False
                                if len(rel.parts) < 2:
                                    error = f'_check_xtts_builtin_speakers() error: unexpected voice layout for {current_voice}'
                                    print(error)
                                    return False
                                new_current_voice = str(voices_root.joinpath(lang_dir, *rel.parts[1:]))
                                os.makedirs(os.path.dirname(new_current_voice), exist_ok=True)
                                proc_current_voice = new_current_voice.replace('.wav', '_temp.wav')
                                #torchaudio.save(proc_current_voice, audio_tensor, default_engine_settings[xtts]['samplerate'])
                                if not self.audio_save(proc_current_voice, audio_tensor, default_engine_settings[xtts]['samplerate']):
                                    error = f'audio_save() error: cannot save {proc_current_voice}'
                                    print(error)
                                    Path(proc_current_voice).unlink(missing_ok=True)
                                    return False
                                if normalize_audio(proc_current_voice, new_current_voice, default_audio_proc_samplerate, self.session['is_gui_process']):
                                    del audio_sentence, sourceTensor, audio_tensor
                                    Path(proc_current_voice).unlink(missing_ok=True)
                                    gc.collect()
                                    self.engine = loaded_tts.get(self.tts_key, False)
                                    if not self.engine:
                                        self._load_engine()
                                    return new_current_voice
                                else:
                                    error = 'normalize_audio() error:'
                            else:
                                error = f'No audio waveform found in _check_xtts_builtin_speakers() result: {result}'
                    else:
                        error = f'_check_xtts_builtin_speakers() error: {xtts} is False'
                else:
                    error = f'The translated {default_text_file} could not be found! Voice cloning file will stay in English.'
                print(error)
            else:
                return current_voice
        except Exception as e:
            error = f'_check_xtts_builtin_speakers() error: {e}'
            if new_current_voice:
                Path(new_current_voice).unlink(missing_ok=True)
            if proc_current_voice:
                Path(proc_current_voice).unlink(missing_ok=True)
            print(error)
            return False
        
    def _tensor_type(self,audio_data:Any)->'Tensor':
        import torch
        import numpy as np
        if isinstance(audio_data, torch.Tensor):
            return audio_data
        elif isinstance(audio_data,np.ndarray):
            return torch.from_numpy(audio_data).float()
        elif isinstance(audio_data,list):
            return torch.tensor(audio_data,dtype=torch.float32)
        else:
            raise TypeError(f'_tensor_type() error: Unsupported type for audio_data: {type(audio_data)}')
            
    def _get_resampler(self, orig_sr:int, target_sr:int, device:'torch.device|str'='cpu')->'Resample':
        import torch
        import torchaudio
        dev = torch.device(device) if not isinstance(device, torch.device) else device
        key = (orig_sr, target_sr, str(dev))
        if key not in self.resampler_cache:
            resampler = torchaudio.transforms.Resample(
                orig_freq = orig_sr, new_freq = target_sr
            ).to(dev)
            resampler.eval()
            self.resampler_cache[key] = resampler
        return self.resampler_cache[key]

    def _resample_wav(self, wav_path:str, expected_sr:int)->str:
        import soundfile as sf
        import torch
        data, orig_sr = sf.read(wav_path, dtype='float32', always_2d=True)
        waveform = torch.from_numpy(data.T).contiguous()
        if orig_sr==expected_sr and waveform.size(0)==1:
            return wav_path
        if waveform.size(0)>1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if orig_sr!=expected_sr:
            resampler = self._get_resampler(orig_sr, expected_sr, waveform.device)
            waveform = resampler(waveform)
        wav_tensor = waveform.squeeze(0)
        wav_numpy = wav_tensor.cpu().numpy()
        resample_tmp = os.path.join(self.session['process_dir'],  'tmp')
        os.makedirs(resample_tmp,  exist_ok=True)
        tmp_fh = tempfile.NamedTemporaryFile(dir=resample_tmp,  suffix='.wav',  delete=False)
        tmp_path = tmp_fh.name
        tmp_fh.close()
        sf.write(tmp_path, wav_numpy, expected_sr, subtype='PCM_16')
        return tmp_path

    def _resample_audiodata(self, wav_data, source_sr:int, expected_sr:int)->Any:
        import torch
        import numpy as np
        if isinstance(wav_data, list):
            wav_data = np.asarray(wav_data, dtype=np.float32)
        if isinstance(wav_data, np.ndarray):
            waveform = torch.from_numpy(wav_data).float()
        elif isinstance(wav_data, torch.Tensor):
            waveform = wav_data.float()
        else:
            raise TypeError(f'unsupported wav_data type: {type(wav_data)}')
        if waveform.ndim==1:
            waveform = waveform.unsqueeze(0)
        if waveform.size(0)>1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if source_sr!=expected_sr:
            resampler = self._get_resampler(source_sr, expected_sr, waveform.device)
            waveform = resampler(waveform)
        return waveform.squeeze(0).cpu().numpy()

    def _set_voice(self, voice:str|None)->tuple:
        current_voice = (voice if voice is not None else self.models[self.session['fine_tuned']]['voice'])
        if current_voice is not None:
            speaker = re.sub(r'\.wav$', '', os.path.basename(current_voice))
            if current_voice not in default_engine_settings[TTS_ENGINES['BARK']]['voices'].keys() and self.session['custom_model_dir'] not in current_voice:
                current_voice = self._check_xtts_builtin_speakers(current_voice, speaker)
                if not current_voice:
                    error = f"_set_voice() error: Could not create the builtin speaker selected voice in {self.session['language']}"
                    return None, error
        return current_voice, None
        
    def _split_sentence_on_sml(self, sentence:str)->list[str]:
        parts:list[str] = []
        last = 0
        for m in SML_TAG_PATTERN.finditer(sentence):
            start, end = m.span()
            if start > last:
                text = sentence[last:start]
                if text:
                    parts.append(text)
            parts.append(m.group(0))
            last = end
        if last < len(sentence):
            tail = sentence[last:]
            if tail:
                parts.append(tail)
        return parts

    def _convert_sml(self, sml:str)->tuple:
        import torch
        import numpy as np
        m = SML_TAG_PATTERN.fullmatch(sml)
        if not m:
            error = '_convert_sml SML_TAG_PATTERN error: m is empty'
            return False, error
        tag = m.group('tag')
        close = bool(m.group('close'))
        value = m.group('value')
        assert tag in TTS_SML, f'Unknown SML tag: {tag!r}'
        if tag == 'break':
            silence_time = 0.5
            self.audio_segments.append(torch.zeros(1, int(self.params['samplerate'] * silence_time)).clone())
            return True, None
        elif tag == 'pause':
            silence_time = float(value) if value else 1.5
            self.audio_segments.append(torch.zeros(1, int(self.params['samplerate'] * silence_time)).clone())
            return True, None
        elif tag == 'voice':
            if close:
                self.params['inline_voice'] = None
                voice_orig, error = self._set_voice(self.params['block_voice'])
                if voice_orig is None and error is not None:
                    return False, error
                self.params['block_voice'] = self.params['current_voice'] = voice_orig
                return True, None
            if not value:
                error = '_convert_sml() error: voice tag must specify a voice path value'
                return False, error
            inline_voice = os.path.abspath(value)
            if not os.path.exists(inline_voice):
                error = f'_convert_sml() error: voice {inline_voice} does not exist!'
                return False, error
            self.params['inline_voice'] = self.params['current_voice'] = inline_voice
            return True, None
        elif tag == 'ipa':
            if close:
                value = '' # TODO: get the value between tag [ipa] and close [/ipa]
            return True, None
        else:
            error = 'This SML is not recognized'
            return False, error
            
    def audio_save(self, sentence_file, segment_tensor:any, samplerate:int)->bool:
        import soundfile as sf
        formats = {"wav": "FLOAT", "flac": "PCM_24", "ogg": "VORBIS"}
        path = os.fspath(sentence_file)
        fmt = os.path.splitext(path)[1].lstrip('.').lower()
        if fmt not in formats:
            raise ValueError(f'audio_save: format {fmt!r} not in {tuple(formats)}')
        audio_np = segment_tensor.detach().cpu().numpy().squeeze(0)
        try:
            sf.write(path, audio_np, samplerate, subtype=formats[fmt])
        except Exception as e:
            # remove any partial file from a failed write
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
            raise RuntimeError(f'audio_save({path}): {e}') from e
        return True

    def log_exception(self,where:str, e:Exception)->str:
        import traceback
        traceback.print_exc()
        return f'{where}: {e}'