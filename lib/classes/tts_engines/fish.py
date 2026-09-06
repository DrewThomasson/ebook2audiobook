from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

# Vendored at ext/py/fish-speech (see that dir's pyproject.toml header for why:
# no clean pip-installable single-file path exists for tools/api_server.py, and
# a couple of upstream pins needed relaxing for this repo's shared venv). Kept
# out of models_dir/tts_dir since it is source, not a downloaded model.
FISH_SPEECH_REPO_DIR = os.path.abspath(os.path.join("ext", "py", "fish-speech"))
FISH_API_HOST = "127.0.0.1"
FISH_API_PORT = 8090


class Fish(TTSUtils, TTSRegistry, name="fish"):
    def __init__(self, session: DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
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

    def _server_is_up(self) -> bool:
        import requests

        try:
            r = requests.get(
                f"http://{FISH_API_HOST}:{FISH_API_PORT}/v1/health", timeout=2
            )
            return r.status_code == 200
        except Exception:
            return False

    def load_engine(self) -> Any:
        try:
            msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient…"
            print(msg)
            engine = loaded_tts.get(self.tts_key)
            if engine:
                return engine
            if self.device == devices["CPU"]["proc"]:
                error = "Fish-Speech (s2-pro) has no supported CPU inference path; a CUDA device is required."
                raise RuntimeError(error)
            if not self._server_is_up():
                checkpoint_dir = os.path.join(self.cache_dir, "fish-s2-pro")
                if not os.path.isdir(checkpoint_dir):
                    from huggingface_hub import snapshot_download

                    snapshot_download(
                        repo_id=self.models[self.session["fine_tuned"]]["repo"],
                        local_dir=checkpoint_dir,
                    )
                # Same interpreter/venv as the running app (sys.executable, not a
                # bare 'python' looked up on PATH) so the subprocess shares
                # whatever torch/transformers this repo's device_installer
                # already resolved for this device — confirmed compatible with a
                # live spike against the real s2-pro checkpoint (see PR notes).
                proc = subprocess.Popen(
                    [
                        sys.executable,
                        os.path.join(FISH_SPEECH_REPO_DIR, "tools", "api_server.py"),
                        "--listen",
                        f"{FISH_API_HOST}:{FISH_API_PORT}",
                        "--llama-checkpoint-path",
                        checkpoint_dir,
                    ],
                    cwd=FISH_SPEECH_REPO_DIR,
                )
                import time

                for _ in range(60):
                    if self._server_is_up():
                        break
                    time.sleep(2)
                else:
                    proc.terminate()
                    error = "Fish-Speech API server did not become healthy within 120s"
                    raise RuntimeError(error)
                loaded_tts[self.tts_key] = {"process": proc, "port": FISH_API_PORT}
            else:
                loaded_tts[self.tts_key] = {"process": None, "port": FISH_API_PORT}
            msg = f"TTS {self.tts_key} Loaded!"
            print(msg)
            return loaded_tts[self.tts_key]
        except Exception as e:
            error = f"load_engine() error: {e}"
            raise RuntimeError(error) from e

    def convert(self, sentence_file: str, sentence: str, **kwargs) -> tuple:
        try:
            import requests, ormsgpack
            from fish_speech.utils.schema import ServeTTSRequest
            from fish_speech.utils.file import audio_to_bytes

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
            references = []
            if self.params["current_voice"] and os.path.exists(
                self.params["current_voice"]
            ):
                ref_text_file = (
                    os.path.splitext(self.params["current_voice"])[0] + ".txt"
                )
                ref_text = (
                    Path(ref_text_file).read_text(encoding="utf-8").strip()
                    if os.path.exists(ref_text_file)
                    else ""
                )
                references = [
                    {
                        "audio": audio_to_bytes(self.params["current_voice"]),
                        "text": ref_text,
                    }
                ]
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
                    req = ServeTTSRequest(
                        text=part,
                        references=references,
                        reference_id=None,
                        format="wav",
                        streaming=False,
                        use_memory_cache="on",
                    )
                    resp = requests.post(
                        f"http://{FISH_API_HOST}:{self.engine['port']}/v1/tts",
                        params={"format": "msgpack"},
                        data=ormsgpack.packb(
                            req, option=ormsgpack.OPT_SERIALIZE_PYDANTIC
                        ),
                        headers={"content-type": "application/msgpack"},
                        timeout=120,
                    )
                    if resp.status_code != 200:
                        error = f"Fish API returned HTTP {resp.status_code}: {resp.text[:200]}"
                        return False, error
                    tmp_wav = os.path.join(
                        self.session["process_dir"], "tmp", f"{uuid.uuid4().hex}.wav"
                    )
                    os.makedirs(os.path.dirname(tmp_wav), exist_ok=True)
                    with open(tmp_wav, "wb") as f:
                        f.write(resp.content)
                    import soundfile as sf

                    audio_np, sr = sf.read(tmp_wav, dtype="float32")
                    Path(tmp_wav).unlink(missing_ok=True)
                    if sr != self.params["samplerate"]:
                        audio_np = self._resample_audiodata(
                            audio_np, sr, self.params["samplerate"]
                        )
                    part_tensor = self._tensor_type(audio_np).unsqueeze(0)
                    self.audio_segments.append(part_tensor)
                except Exception as e:
                    self.cleanup_memory()
                    return False, self.log_exception(
                        f"{self.__class__.__name__}.convert() part loop", e
                    )
            if self.audio_segments:
                import torch

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
