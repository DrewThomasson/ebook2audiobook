from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

# ponytail: directory where cached voice-clone prompts (*.pt) are stored.
# Delete a cached prompt to force re-computation from the reference audio.
QWEN3_CACHE_DIR = os.path.join(tts_dir, 'qwen3_voice_cache')

# ponytail: module-level in-memory cache so prompt data survives engine instances
_prompt_memory_cache: dict[str, list | None] = {}


class Qwen3TTS(TTSUtils, TTSRegistry, name='qwen3tts'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speaker = None
            self.tts_key = self.session['model_cache']
            self.audio_segments = []
            self.tts_engine = self.session['tts_engine']
            self.models = load_engine_presets(self.tts_engine)
            self.language = self.session.get('language')
            self.language_iso1 = self.session.get('language_iso1')
            if self.session.get('translate_enabled'):
                if self.session.get('translate'):
                    self.language = self.session['translate']
                if self.session.get('translate_iso1'):
                    self.language_iso1 = self.session['translate_iso1']
            if self.tts_engine not in default_engine_settings:
                error = f'Invalid tts_engine {self.tts_engine}.'
                raise ValueError(error)
            self.engine_langs = default_engine_settings[self.tts_engine].get('languages', {})
            if self.language not in self.engine_langs:
                error = f'Language {self.language} not supported by engine {self.tts_engine}.'
                raise ValueError(error)
            fine_tuned = self.session.get('fine_tuned')
            if fine_tuned not in self.models:
                error = f'Invalid fine_tuned model {fine_tuned}. Available: {list(self.models.keys())}'
                raise ValueError(error)
            model_cfg = self.models[fine_tuned]
            self.model_path = None
            self.params = {'samplerate': model_cfg['samplerate']}
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 0
            self.amp_dtype = self._apply_gpu_policy(enough_vram=enough_vram, seed=seed)
            self.device = devices['CUDA']['proc'] if self.session['device'] in [
                devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']
            ] else self.session['device']
            self.engine = self.load_engine()

            # ponytail: batch_size from session (auto-calc or user-set)
            free_gb = self.session.get('free_vram_gb', 0)
            suggested = max(4, min(28, int(free_gb * 0.85)))
            current = self.session.get('qwen3_batch_size', suggested)
            if current < 1:
                current = suggested
            self.batch_size = current
            msg = f'  Qwen3 batch_size: {self.batch_size} (VRAM: {free_gb}GB, suggested: {suggested})'
            print(msg)

            # ponytail: generation params from session config
            self.gen_params: dict[str, Any] = {}
            for key, cast in [('temperature', float), ('top_p', float), ('repetition_penalty', float)]:
                val = self.session.get(f'qwen3_{key}')
                if val is not None:
                    self.gen_params[key] = cast(val)

            # ponytail: cross-sentence batch buffer
            self._batch_buffer: list[dict] = []
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        try:
            import torch
            from qwen_tts import Qwen3TTSModel

            msg = f'Loading Qwen3-TTS model, please be patient\u2026'
            print(msg)
            self.cleanup_memory()
            engine = loaded_tts.get(self.tts_key)
            if not engine:
                model_name = default_engine_settings[self.tts_engine].get('repo', '')
                self.tts_key = f'{self.tts_engine}-{model_name}'
                engine = loaded_tts.get(self.tts_key)
                if not engine:
                    # ponytail: try flash-attn, fall back to sdpa (built-in torch), then eager
                    attn_kwargs = dict(attn_implementation='flash_attention_2')
                    try:
                        import flash_attn  # noqa: F401
                    except ImportError:
                        try:
                            # PyTorch >=2.0 has flash attention built-in via SDPA
                            torch.backends.cuda.flash_sdp_enabled()
                            attn_kwargs['attn_implementation'] = 'sdpa'
                        except Exception:
                            attn_kwargs['attn_implementation'] = 'eager'
                    engine = Qwen3TTSModel.from_pretrained(
                        model_name,
                        torch_dtype=torch.bfloat16,
                        device_map=self.device,
                        **attn_kwargs,
                    )
                    # ponytail: device diagnostic (best-effort, don't crash)
                    try:
                        for attr in ('device', 'model.device'):
                            d = engine
                            for a in attr.split('.'):
                                d = getattr(d, a)
                            param_device = d
                            break
                    except Exception:
                        param_device = 'unknown'
                    print(f'  Model device: {param_device} (expected: {self.device})')
                    # ponytail: silence the "Setting pad_token_id" warning
                    if hasattr(engine, 'generation_config') and engine.generation_config is not None:
                        engine.generation_config.pad_token_id = engine.generation_config.eos_token_id
                    loaded_tts[self.tts_key] = engine
            if engine:
                msg = f'Qwen3-TTS {self.tts_key} Loaded!'
                print(msg)
                return engine
            error = 'load_engine(): engine is None'
            raise RuntimeError(error)
        except Exception as e:
            error = f'load_engine() error: {e}'
            raise RuntimeError(error) from e

    # ---- voice-clone prompt caching ----
    # ponytail: module-level _prompt_memory_cache survives engine instances

    def _prompt_cache_path(self, audio_path:str)->str:
        """Unique file name for a cached prompt based on the reference audio."""
        import hashlib
        key = hashlib.sha256(audio_path.encode()).hexdigest()[:16]
        name = Path(audio_path).stem
        return os.path.join(QWEN3_CACHE_DIR, f'{name}_{key}.pt')

    def _load_or_create_prompt(self, audio_path:str)->list|None:
        """Load cached voice-clone prompt, or compute and cache it.

        Uses x_vector_only_mode=True so only the speaker embedding is kept
        (no reference text / ICL required).

        Keeps a hot in-memory cache so a multi-block book only hits disk once per voice.
        """
        global _prompt_memory_cache
        cached = _prompt_memory_cache.get(audio_path)
        if cached is not None:
            return cached

        cache_file = self._prompt_cache_path(audio_path)
        os.makedirs(QWEN3_CACHE_DIR, exist_ok=True)
        # check cache first
        if os.path.exists(cache_file):
            try:
                import torch
                data = torch.load(cache_file, map_location=self.device, weights_only=True)
                print(f'  Loaded cached voice-clone prompt for {Path(audio_path).name}')
                _prompt_memory_cache[audio_path] = data
                return data
            except Exception as e:
                print(f'  Cache read failed ({e}), recomputing\u2026')
        # compute — x_vector_only_mode=True means only speaker embedding, no ref text needed
        try:
            prompt = self.engine.create_voice_clone_prompt(
                ref_audio=audio_path,
                ref_text=None,
                x_vector_only_mode=True,
            )
            # prompt is List[VoiceClonePromptItem]; save as list of dicts
            data = [
                {
                    'ref_code': p.ref_code,
                    'ref_spk_embedding': p.ref_spk_embedding,
                    'x_vector_only_mode': p.x_vector_only_mode,
                    'icl_mode': p.icl_mode,
                    'ref_text': p.ref_text,
                }
                for p in prompt
            ]
            import torch
            torch.save(data, cache_file)
            print(f'  Cached voice-clone prompt to {cache_file}')
            _prompt_memory_cache[audio_path] = data
            return data
        except Exception as e:
            print(f'  create_voice_clone_prompt failed for {audio_path}: {e}')
            _prompt_memory_cache[audio_path] = None
            return None

    # ---- inference ----

    def _prompt_items_to_dict(self, items:list)->dict:
        """Convert list[VoiceClonePromptItem dicts] to the dict format generate_voice_clone expects."""
        return {
            'ref_code': [it['ref_code'] for it in items],
            'ref_spk_embedding': [it['ref_spk_embedding'] for it in items],
            'x_vector_only_mode': [it['x_vector_only_mode'] for it in items],
            'icl_mode': [it['icl_mode'] for it in items],
        }

    def _flush_batch(self)->None:
        """Flush buffered sentences through batched inference."""
        if not self._batch_buffer:
            return
        buf = self._batch_buffer
        self._batch_buffer = []

        try:
            import torch
            from lib.classes.tts_engines.common.audio import is_audio_data_valid

            texts = [b['text'] for b in buf]
            lang_name = buf[0]['lang']  # same for all in block
            voice_prompt = buf[0].get('voice_prompt')
            languages = [lang_name] * len(texts)

            if voice_prompt:
                prompt_dict = self._prompt_items_to_dict(voice_prompt)
                # replicate single prompt to batch size
                prompt_dict = {k: v * len(texts) for k, v in prompt_dict.items()}
                wavs, sr = self.engine.generate_voice_clone(
                    text=texts,
                    language=languages,
                    voice_clone_prompt=prompt_dict,
                    do_sample=True,
                    **self.gen_params,
                )
            else:
                # no prompt — skip (shouldn't happen with Base model)
                return

            for i, audio_part in enumerate(wavs):
                if torch.is_tensor(audio_part):
                    audio_part = audio_part.detach().cpu()
                if not is_audio_data_valid(audio_part):
                    continue
                part_tensor = self._tensor_type(audio_part).unsqueeze(0)
                if part_tensor.numel() == 0:
                    continue
                buf[i]['tensor'] = part_tensor

            # Group by sentence_file and concatenate
            from collections import OrderedDict
            groups: dict[str, list] = OrderedDict()
            for b in buf:
                groups.setdefault(b['file'], []).append(b)
            for sentence_file, items in groups.items():
                tensors = [it['tensor'] for it in items if it.get('tensor') is not None]
                if tensors:
                    seg = torch.cat(tensors, dim=-1)
                    self.audio_save(sentence_file, seg, self.params['samplerate'])
            # ponytail: release cached CUDA allocations after each batch
            import gc
            gc.collect()
            torch.cuda.empty_cache()
        except Exception as e:
            error = f'batch flush error: {e}'
            print(error)
            # fallback: process individually
            for b in buf:
                try:
                    self._convert_one(b['file'], b['text'], b.get('voice_prompt'))
                except Exception:
                    pass

    def _convert_one(self, sentence_file:str, sentence:str, voice_prompt:list|None=None)->tuple:
        """Single-sentence fallback."""
        import torch
        from lib.classes.tts_engines.common.audio import is_audio_data_valid

        if not voice_prompt:
            return False, 'no voice prompt'

        prompt_dict = self._prompt_items_to_dict(voice_prompt)
        wavs, sr = self.engine.generate_voice_clone(
            text=sentence,
            language=self.engine_langs.get(self.language, 'Auto'),
            voice_clone_prompt=prompt_dict,
            do_sample=True,
            **self.gen_params,
        )
        audio_part = wavs[0] if isinstance(wavs, list) else wavs
        if audio_part is None or len(audio_part) == 0:
            return False, 'empty audio'
        if torch.is_tensor(audio_part):
            audio_part = audio_part.detach().cpu()
        if not is_audio_data_valid(audio_part):
            return False, 'invalid audio'
        seg = self._tensor_type(audio_part).unsqueeze(0)
        if seg.numel() == 0:
            return False, 'empty tensor'
        if not self.audio_save(sentence_file, seg, self.params['samplerate']):
            return False, 'save failed'
        return True, None

    def convert(self, sentence_file:str, sentence:str, **kwargs)->tuple:
        try:
            if not self.engine:
                error = f'TTS engine {self.tts_engine} failed to load!'
                return False, error

            self.params['block_voice'] = kwargs.get('block_voice', self.session['voice'])
            if self.params.get('inline_voice'):
                self.params['current_voice'] = self.params['inline_voice']
            else:
                self.params['current_voice'], error = self._set_voice(self.params['block_voice'])
                if self.params['current_voice'] is None and error is not None:
                    return False, error

            # Split SML, collect text parts for batching
            sentence_parts = self._split_sentence_on_sml(sentence)
            lang_name = self.engine_langs.get(self.language, 'Auto')

            # ---- resolve voice-clone prompt from reference audio ----
            voice_prompt_data = None
            raw_voice = self.params.get('current_voice') or ''
            if raw_voice and os.path.isfile(raw_voice):
                voice_prompt_data = self._load_or_create_prompt(raw_voice)
                if not voice_prompt_data:
                    return False, f'Failed to load/create voice-clone prompt for {raw_voice}'

            if not voice_prompt_data:
                return False, 'No voice selected — Qwen3 Base model requires a reference audio voice'

            for part in sentence_parts:
                part = part.strip()
                if not part:
                    continue
                if SML_TAG_PATTERN.fullmatch(part):
                    success, error = self._convert_sml(part)
                    if not success:
                        return False, error
                    continue
                if not any(c.isalnum() for c in part):
                    continue
                # Buffer for batched inference
                self._batch_buffer.append({
                    'file': sentence_file,
                    'text': part,
                    'lang': lang_name,
                    'voice_prompt': voice_prompt_data,
                })

            if len(self._batch_buffer) >= self.batch_size:
                self._flush_batch()

            # Verify file was created (either by batch flush or empty sentence)
            if os.path.exists(sentence_file):
                return True, None
            # Empty sentence — write silence
            import torch
            silence = torch.zeros(1, int(self.params['samplerate'] * 0.3))
            self.audio_save(sentence_file, silence, self.params['samplerate'])
            return True, None
        except Exception as e:
            self.cleanup_memory()
            self.audio_segments = []
            return False, self.log_exception(f'{self.__class__.__name__}.convert()', e)

    def flush(self)->None:
        """Call this after all sentences in a block are processed."""
        self._flush_batch()

    def create_vtt(self, all_sentences:list)->bool:
        if self._build_vtt_file(all_sentences):
            return True
        return False
