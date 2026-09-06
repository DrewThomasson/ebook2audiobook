from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

BREEZE_API_HOST = "127.0.0.1"
BREEZE_API_PORT = 7861
BREEZE_REFERENCE_TEXT = "This is a clear, steady voice reading aloud for narration."


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
            self.batch_size = self._resolve_batch_size()
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
        except (KeyError, OSError, RuntimeError, ValueError) as e:
            # load_engine() already wraps its own failures; anything outside this set
            # is a bug here and should keep its traceback.
            error = f"__init__() error: {e}"
            raise ValueError(error) from e

    # tells lib.core it can call convert_batch() instead of one convert() per sentence
    supports_batching = True

    def _resolve_batch_size(self) -> int:
        default = default_engine_settings[TTS_ENGINES["BREEZE"]]["batch_size"]
        raw = os.environ.get("E2A_BREEZE_BATCH_SIZE")
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError:
            print(
                f"Ignoring E2A_BREEZE_BATCH_SIZE={raw!r}: not an integer, using {default}"
            )
            return default
        if value < 1:
            print(
                f"Ignoring E2A_BREEZE_BATCH_SIZE={value}: must be >= 1, using {default}"
            )
            return default
        return value

    def _server_is_up(self) -> bool:
        # /health returns 503 while the model is still loading, 200 once ready.
        import requests

        try:
            r = requests.get(
                f"http://{BREEZE_API_HOST}:{BREEZE_API_PORT}/health", timeout=2
            )
            return r.status_code == 200
        except requests.RequestException:
            # only network failures mean "not up yet"; a bug here must not masquerade
            # as an unhealthy server and time out the wait loop.
            return False

    def _load_or_create_reference_voice(self) -> tuple:
        # Without a reference, Breeze runs in reference-free "Voice Design" mode and
        # samples a new voice per call. Generate one reference clip once and reuse it
        # (via "Voice Direction" mode) on every request to keep the narrator consistent.
        ref_wav = os.path.join(self.cache_dir, "breeze-tts-2", "reference_voice.wav")
        ref_txt = f"{ref_wav}.txt"
        if os.path.exists(ref_wav) and os.path.exists(ref_txt):
            return ref_wav, Path(ref_txt).read_text(encoding="utf-8")
        import requests

        resp = requests.post(
            f"http://{BREEZE_API_HOST}:{BREEZE_API_PORT}/v1/audio/speech",
            data={
                "cfg_scale": 4,
                "text": BREEZE_REFERENCE_TEXT,
                "instruction": default_engine_settings[TTS_ENGINES["BREEZE"]][
                    "default_instruction"
                ],
            },
            timeout=120,
        )
        if resp.status_code != 200:
            error = f"Breeze API returned HTTP {resp.status_code} generating reference voice: {resp.text[:200]}"
            raise RuntimeError(error)
        os.makedirs(os.path.dirname(ref_wav), exist_ok=True)
        with wave.open(ref_wav, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(self.params["samplerate"])
            f.writeframes(resp.content)
        Path(ref_txt).write_text(BREEZE_REFERENCE_TEXT, encoding="utf-8")
        return ref_wav, BREEZE_REFERENCE_TEXT

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

                # breeze-tts installs editable (see ext/py/breeze-tts/setup.py), so
                # breeze_infer is importable globally - no cwd/PYTHONPATH juggling here.
                weights_dir = os.path.join(self.cache_dir, "breeze-tts-2")
                if not os.path.isdir(weights_dir):
                    from huggingface_hub import snapshot_download

                    snapshot_download(
                        repo_id=self.models[self.session["fine_tuned"]]["repo"],
                        local_dir=weights_dir,
                    )
                # --fast-all's compile path needs Triton's ptxas to support the GPU
                # target; the bundled torch/triton one may not on newer architectures.
                env = os.environ.copy()
                # Respect an already-set TRITON_PTXAS_PATH; only fall back to the
                # system CUDA toolkit's ptxas.
                env.setdefault("TRITON_PTXAS_PATH", "/usr/local/cuda/bin/ptxas")
                # sys.executable, not "python": PATH may point at an interpreter
                # without breeze_infer installed.
                command = [
                    sys.executable,
                    "-m",
                    "breeze_infer.api",
                    weights_dir,
                    "--host",
                    BREEZE_API_HOST,
                    "--port",
                    str(BREEZE_API_PORT),
                ]
                # --fast-all's CUDA-graph batch dimension is consumed by CFG, so the
                # batch endpoint cannot use it and the warmup would be wasted.
                if self.batch_size == 1:
                    command.append("--fast-all")
                proc = subprocess.Popen(command, env=env)
                for _ in range(90):
                    if self._server_is_up():
                        break
                    time.sleep(2)
                else:
                    proc.terminate()
                    error = "Breeze API server did not become healthy within 180s"
                    raise RuntimeError(error)
                entry = {"process": proc, "port": BREEZE_API_PORT}
            else:
                # server already running (e.g. started out-of-band) - reuse it rather than
                # spawning a second one; the server is single-concurrency (see convert()).
                entry = {"process": None, "port": BREEZE_API_PORT}
            entry["ref_audio_path"], entry["ref_text"] = (
                self._load_or_create_reference_voice()
            )
            loaded_tts[self.tts_key] = entry
            msg = f"TTS {self.tts_key} Loaded!"
            print(msg)
            return loaded_tts[self.tts_key]
        except Exception as e:
            error = f"load_engine() error: {e}"
            raise RuntimeError(error) from e

    def convert(self, sentence_file: str, sentence: str, **kwargs) -> tuple:
        import numpy as np
        import requests
        import torch

        try:
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
                    # the server is single-concurrency and answers 409 if busy; no retry
                    # here because convert() is never called concurrently.
                    with open(self.engine["ref_audio_path"], "rb") as ref_audio_file:
                        resp = requests.post(
                            f"http://{BREEZE_API_HOST}:{self.engine['port']}/v1/audio/speech",
                            data={
                                "cfg_scale": 4,
                                "text": part,
                                "instruction": default_engine_settings[
                                    TTS_ENGINES["BREEZE"]
                                ]["default_instruction"],
                                "ref_text": self.engine["ref_text"],
                            },
                            files={"ref_audio": ref_audio_file},
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
                except (
                    OSError,
                    requests.RequestException,
                    RuntimeError,
                    ValueError,
                ) as e:
                    # what one part can legitimately hit: missing reference file,
                    # network, runtime, malformed PCM. Bugs stay unhandled.
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
        except (OSError, requests.RequestException, RuntimeError, ValueError) as e:
            # what the per-part loop does not already handle: SML parsing, torch.cat
            # and audio_save. Bugs stay unhandled.
            self.cleanup_memory()
            self.audio_segments = []
            return False, self.log_exception(f"{self.__class__.__name__}.convert()", e)

    def _request_batch(self, texts: list) -> list:
        # The server answers with every segment's PCM concatenated plus an
        # X-Segment-Bytes header, so the blob is split back apart here.
        import json

        import numpy as np
        import requests

        segments = []
        for start in range(0, len(texts), self.batch_size):
            chunk = texts[start : start + self.batch_size]
            with open(self.engine["ref_audio_path"], "rb") as ref_audio_file:
                resp = requests.post(
                    f"http://{BREEZE_API_HOST}:{self.engine['port']}/v1/audio/speech/batch",
                    data={
                        "cfg_scale": 4,
                        "texts": json.dumps(chunk),
                        "instruction": default_engine_settings[TTS_ENGINES["BREEZE"]][
                            "default_instruction"
                        ],
                        "ref_text": self.engine["ref_text"],
                    },
                    files={"ref_audio": ref_audio_file},
                    # a full batch decodes for minutes, not seconds
                    timeout=1800,
                )
            if resp.status_code != 200:
                error = f"Breeze batch API returned HTTP {resp.status_code}: {resp.text[:200]}"
                raise RuntimeError(error)
            header = resp.headers.get("X-Segment-Bytes", "")
            if not header:
                error = (
                    "Breeze batch API response is missing the X-Segment-Bytes header"
                )
                raise RuntimeError(error)
            sizes = [int(value) for value in header.split(",")]
            if len(sizes) != len(chunk):
                error = (
                    f"Breeze batch API returned {len(sizes)} segments "
                    f"for {len(chunk)} texts"
                )
                raise RuntimeError(error)
            if sum(sizes) != len(resp.content):
                error = (
                    f"Breeze batch API segment sizes sum to {sum(sizes)} "
                    f"but body is {len(resp.content)} bytes"
                )
                raise RuntimeError(error)
            offset = 0
            for size in sizes:
                raw = resp.content[offset : offset + size]
                offset += size
                segments.append(
                    np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
                )
        return segments

    def convert_batch(self, items: list, **kwargs) -> tuple:
        """Synthesize many sentences per inference request.

        ``items`` is a list of ``(sentence_file, sentence)``. A sentence can mix
        speech with SML tags, so parts are flattened into one flat list of texts
        for the model and reassembled per sentence afterwards; SML tags stay
        local and never reach the server.
        """
        # outside the try so the except clause can name requests.RequestException
        import requests
        import torch

        try:
            if not self.engine:
                error = f"TTS engine {self.session['tts_engine']} failed to load!"
                return False, error

            plans = []
            texts = []
            for sentence_file, sentence in items:
                plan = []
                for part in self._split_sentence_on_sml(sentence):
                    part = part.strip()
                    if not part:
                        continue
                    if SML_TAG_PATTERN.fullmatch(part):
                        plan.append(("sml", part))
                        continue
                    if not any(c.isalnum() for c in part):
                        continue
                    plan.append(("tts", len(texts)))
                    texts.append(part)
                plans.append((sentence_file, plan))

            audio_parts = self._request_batch(texts) if texts else []

            for sentence_file, plan in plans:
                self.audio_segments = []
                for kind, payload in plan:
                    if kind == "sml":
                        success, error = self._convert_sml(payload)
                        if not success:
                            return False, error
                        continue
                    part_tensor = self._tensor_type(audio_parts[payload]).unsqueeze(0)
                    self.audio_segments.append(part_tensor)
                if not self.audio_segments:
                    continue
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
        except (OSError, requests.RequestException, RuntimeError, ValueError) as e:
            # _request_batch's HTTP and response-shape failures, plus torch.cat and
            # audio_save. Bugs stay unhandled.
            self.cleanup_memory()
            self.audio_segments = []
            return False, self.log_exception(
                f"{self.__class__.__name__}.convert_batch()", e
            )

    def create_vtt(self, all_sentences: list) -> bool:
        return bool(self._build_vtt_file(all_sentences))
