from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

BREEZE_API_HOST = "127.0.0.1"
BREEZE_API_PORT = 7861


class Breeze(TTSUtils, TTSRegistry, name="breeze"):
    def __init__(self, session: DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.tts_key = self.session["model_cache"]
            self.audio_segments = []
            self.models = load_engine_presets(self.session["tts_engine"])
            self.params = {}
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
        # GET /health, not /v1/health - confirmed against the running server
        # (returns {"status":"ok","sample_rate":24000}/200 once ready,
        # {"status":"loading"}/503 while the model is still loading).
        import requests

        try:
            r = requests.get(
                f"http://{BREEZE_API_HOST}:{BREEZE_API_PORT}/health", timeout=2
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
                error = "Breeze-TTS-2 has no supported CPU inference path; a CUDA device is required."
                raise RuntimeError(error)
            if not self._server_is_up():
                import subprocess
                import time

                # breeze-tts's upstream repo has no setup.py/pyproject.toml, so it is
                # not pip-installable as published. This repo instead vendors it at
                # ext/py/breeze-tts (with an authored setup.py) and installs it in
                # editable mode via requirements.txt, same as ./ext/py/demucs. That
                # means `breeze_infer` (and the `models` package it imports from) are
                # on sys.path globally - no cwd/PYTHONPATH juggling needed here.
                weights_dir = os.path.join(self.cache_dir, "breeze-tts-2")
                if not os.path.isdir(weights_dir):
                    from huggingface_hub import snapshot_download

                    snapshot_download(
                        repo_id=self.models[self.session["fine_tuned"]]["repo"],
                        local_dir=weights_dir,
                    )
                # Point Triton at system ptxas: bundled torch/triton's ptxas doesn't
                # support this box's GPU target, needed for --fast-all's compile path.
                env = os.environ.copy()
                env.setdefault("TRITON_PTXAS_PATH", "/usr/local/cuda/bin/ptxas")
                proc = subprocess.Popen(
                    [
                        "python",
                        "-m",
                        "breeze_infer.api",
                        weights_dir,
                        "--host",
                        BREEZE_API_HOST,
                        "--port",
                        str(BREEZE_API_PORT),
                        "--fast-all",
                    ],
                    env=env,
                )
                for _ in range(90):
                    if self._server_is_up():
                        break
                    time.sleep(2)
                else:
                    proc.terminate()
                    error = "Breeze API server did not become healthy within 180s"
                    raise RuntimeError(error)
                loaded_tts[self.tts_key] = {"process": proc, "port": BREEZE_API_PORT}
            else:
                # server already running (e.g. started out-of-band) - reuse it rather than
                # spawning a second one; the server is single-concurrency (see convert()).
                loaded_tts[self.tts_key] = {"process": None, "port": BREEZE_API_PORT}
            msg = f"TTS {self.tts_key} Loaded!"
            print(msg)
            return loaded_tts[self.tts_key]
        except Exception as e:
            error = f"load_engine() error: {e}"
            raise RuntimeError(error) from e

    def convert(self, sentence_file: str, sentence: str, **kwargs) -> tuple:
        try:
            import numpy as np
            import requests
            import torch

            if not self.engine:
                error = f"TTS engine {self.session['tts_engine']} failed to load!"
                return False, error
            sentence_parts = self._split_sentence_on_sml(sentence)
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
                    # NOTE known v1 limitation: the Breeze API server is single-concurrency -
                    # a second request while one is in flight gets HTTP 409. Not handled here
                    # (retry/backoff) since ebook2audiobook does not call convert() concurrently
                    # within one engine instance; flagged for future hardening if that changes.
                    resp = requests.post(
                        f"http://{BREEZE_API_HOST}:{self.engine['port']}/v1/audio/speech",
                        data={
                            "cfg_scale": 4,
                            "text": part,
                            "instruction": default_engine_settings[
                                TTS_ENGINES["BREEZE"]
                            ]["default_instruction"],
                        },
                        timeout=120,
                    )
                    if resp.status_code != 200:
                        error = f"Breeze API returned HTTP {resp.status_code}: {resp.text[:200]}"
                        return False, error
                    # headerless raw PCM, mono, 16-bit little-endian, 24000 Hz (confirmed via
                    # X-Sample-Rate response header, the project README and its _pcm16() source).
                    pcm = (
                        np.frombuffer(resp.content, dtype="<i2").astype(np.float32)
                        / 32768.0
                    )
                    part_tensor = self._tensor_type(pcm).unsqueeze(0)
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
