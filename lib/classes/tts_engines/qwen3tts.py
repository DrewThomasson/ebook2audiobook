from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

# ponytail: batch size for GPU-parallel inference. 8 works well on 24GB+ VRAM.
# Tune down to 4 if you hit OOM.
BATCH_SIZE = 8


class Qwen3TTS(TTSUtils, TTSRegistry, name='qwen3tts'):

    def __init__(self, session: DictProxy):
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
            self.engine_zs = self._load_engine_zs(self.device)

            # ponytail: cross-sentence batch buffer
            self._batch_buffer: list[dict] = []
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self) -> Any:
        try:
            import torch
            from qwen_tts import Qwen3TTSModel

            msg = f'Loading Qwen3-TTS model, please be patient…'
            print(msg)
            self.cleanup_memory()
            engine = loaded_tts.get(self.tts_key)
            if not engine:
                model_name = default_engine_settings[self.tts_engine].get('repo', '')
                self.tts_key = f'{self.tts_engine}-{model_name}'
                engine = loaded_tts.get(self.tts_key)
                if not engine:
                    engine = Qwen3TTSModel.from_pretrained(
                        model_name,
                        device_map=self.device,
                        dtype=torch.bfloat16,
                        attn_implementation='flash_attention_2',
                    )
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

    def _get_speakers(self) -> list:
        try:
            return self.engine.get_supported_speakers() if hasattr(self.engine, 'get_supported_speakers') else []
        except Exception:
            return []

    def _flush_batch(self) -> None:
        """Flush buffered sentences through batched inference."""
        if not self._batch_buffer:
            return
        buf = self._batch_buffer
        self._batch_buffer = []

        try:
            import torch
            from lib.classes.tts_engines.common.audio import is_audio_data_valid

            speaker_names = [b['speaker'] for b in buf]
            lang_name = buf[0]['lang']  # same for all in block
            texts = [b['text'] for b in buf]

            wavs, sr = self.engine.generate_custom_voice(
                text=texts,
                language=[lang_name] * len(texts),
                speaker=[s if s in self._get_speakers() else None for s in speaker_names],
            )

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
        except Exception as e:
            error = f'batch flush error: {e}'
            print(error)
            # fallback: process individually
            for b in buf:
                try:
                    self._convert_one(b['file'], b['text'], b['speaker'], b['lang'])
                except Exception:
                    pass

    def _convert_one(self, sentence_file: str, sentence: str, speaker: str | None, lang: str) -> tuple:
        """Single-sentence fallback."""
        import torch
        from lib.classes.tts_engines.common.audio import is_audio_data_valid

        wavs, sr = self.engine.generate_custom_voice(
            text=sentence,
            language=lang,
            speaker=speaker if speaker in self._get_speakers() else None,
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

    def convert(self, sentence_file: str, sentence: str, **kwargs) -> tuple:
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
            # ponytail: Qwen3-TTS has model-internal speakers; voice path is just a stub
            speaker_name = None
            if self.params.get('current_voice'):
                stem = Path(self.params['current_voice']).stem
                if stem in default_engine_settings.get(self.tts_engine, {}).get('voices', {}):
                    speaker_name = stem
            lang_name = self.engine_langs.get(self.language, 'Auto')

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
                    'speaker': speaker_name,
                    'lang': lang_name,
                })

            if len(self._batch_buffer) >= BATCH_SIZE:
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

    def flush(self) -> None:
        """Call this after all sentences in a block are processed."""
        self._flush_batch()

    def create_vtt(self, all_sentences: list) -> bool:
        if self._build_vtt_file(all_sentences):
            return True
        return False
