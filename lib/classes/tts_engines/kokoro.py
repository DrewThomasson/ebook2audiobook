from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets


class Kokoro(TTSUtils, TTSRegistry, name="kokoro"):
    def __init__(self, session: DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speaker = None
            self.tts_key = self.session["model_cache"]
            self.audio_segments = []
            self.models = load_engine_presets(self.session["tts_engine"])
            self.params = {}
            self.language = self.session.get("language")
            self.language_iso1 = self.session.get("language_iso1")
            if self.session.get("translate_enabled"):
                if self.session.get("translate"):
                    self.language = self.session["translate"]
                if self.session.get("translate_iso1"):
                    self.language_iso1 = self.session["translate_iso1"]
            fine_tuned = self.session.get("fine_tuned")
            if fine_tuned not in self.models:
                error = f"Invalid fine_tuned model {fine_tuned}. Available models: {list(self.models.keys())}"
                raise ValueError(error)
            self.params["samplerate"] = self.models[fine_tuned]["samplerate"]
            self.kokoro_lang_code = default_engine_settings[TTS_ENGINES["KOKORO"]][
                "languages"
            ].get(self.language, "a")
            enough_vram = self.session["free_vram_gb"] > 2.0
            self.amp_dtype = self._apply_gpu_policy(enough_vram=enough_vram, seed=0)
            self.device = (
                devices["CUDA"]["proc"]
                if self.session["device"]
                in [
                    devices["CUDA"]["proc"],
                    devices["ROCM"]["proc"],
                    devices["JETSON"]["proc"],
                ]
                else self.session["device"]
            )
            self.engine = self.load_engine()
        except Exception as e:
            error = f"__init__() error: {e}"
            raise ValueError(error)

    def load_engine(self) -> Any:
        try:
            msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient…"
            print(msg)
            self.cleanup_memory()
            engine = loaded_tts.get(self.tts_key)
            if engine:
                return engine
            from kokoro import KPipeline

            engine = KPipeline(lang_code=self.kokoro_lang_code, device=self.device)
            if engine:
                loaded_tts[self.tts_key] = engine
                msg = f"TTS {self.tts_key} Loaded!"
                print(msg)
                return engine
            error = "load_engine(): engine is None"
            raise RuntimeError(error)
        except Exception as e:
            error = f"load_engine() error: {e}"
            raise RuntimeError(error) from e

    def convert(self, sentence_file: str, sentence: str, **kwargs) -> tuple:
        try:
            import torch
            from lib.classes.tts_engines.common.audio import (
                is_audio_data_valid,
                trim_audio,
            )

            if not self.engine:
                error = f"TTS engine {self.session['tts_engine']} failed to load!"
                return False, error
            sentence_parts = self._split_sentence_on_sml(sentence)
            self.params["block_voice"] = kwargs.get(
                "block_voice", self.session["voice"]
            )
            if self.params.get("inline_voice"):
                self.params["current_voice"] = self.params["inline_voice"]
            else:
                self.params["current_voice"], error = self._set_voice(
                    self.params["block_voice"]
                )
                if self.params["current_voice"] is None and error is not None:
                    return False, error
            voice_id = (
                Path(self.params["current_voice"]).stem
                if self.params["current_voice"]
                else "af_heart"
            )
            if voice_id not in default_engine_settings[TTS_ENGINES["KOKORO"]]["voices"]:
                voice_id = "af_heart"
            self.audio_segments = []
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
                try:
                    generator = self.engine(part, voice=voice_id, speed=1)
                    for _, _, audio_part in generator:
                        if audio_part is None or len(audio_part) == 0:
                            error = "audio_part not valid"
                            return False, error
                        if not is_audio_data_valid(audio_part):
                            error = "audio_part not valid"
                            return False, error
                        part_tensor = self._tensor_type(audio_part).unsqueeze(0)
                        part_tensor = trim_audio(
                            part_tensor.squeeze(0),
                            self.params["samplerate"],
                            0.001,
                            0.006,
                        ).unsqueeze(0)
                        self.audio_segments.append(part_tensor)
                except Exception as e:
                    self.cleanup_memory()
                    return False, self.log_exception(
                        f"{self.__class__.__name__}.convert() part loop", e
                    )
            if self.audio_segments:
                segment_tensor = torch.cat(self.audio_segments, dim=-1)
                if not self.audio_save(
                    sentence_file, segment_tensor, self.params["samplerate"]
                ):
                    error = f"audio_save() error: cannot save {sentence_file}"
                    return False, error
                self.audio_segments = []
                if not os.path.exists(sentence_file):
                    error = f"Cannot create {sentence_file}"
                    return False, error
            return True, None
        except Exception as e:
            self.cleanup_memory()
            self.audio_segments = []
            return False, self.log_exception(f"{self.__class__.__name__}.convert()", e)

    def create_vtt(self, all_sentences: list) -> bool:
        return bool(self._build_vtt_file(all_sentences))
