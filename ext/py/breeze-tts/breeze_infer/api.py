"""Thin streaming API over the PyTorch Breeze inference runtime."""

from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
import threading
import uuid
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from breeze_infer.runtime import (
    load_runtime,
    resolve_device,
    set_all_seeds,
    update_generation_config_for_breeze,
)
from breeze_infer.templates import get_template, prepare_inputs
from models.fast_streaming import (
    FastBreezeStreamingRuntime,
    FastStreamingChunk,
    FastStreamingConfig,
)
from models.warmup_profile import load_warmup_profile

REPO_ROOT = Path(__file__).resolve().parents[1]
FAST_CONFIG = REPO_ROOT / "configs" / "fast.json"
DEFAULT_CFG_SCALE = 1.0
MAX_NEW_TOKENS = 1500
MAX_SEQ_LEN = 2048
REPETITION_PENALTY = 1.1
OPTIONAL_AUDIO_FILE = File(None)


@dataclass(frozen=True)
class ApiSettings:
    model: Path
    fast_all: bool | None
    fast_text_encoder: bool
    fast_backbone_prefill: bool
    fast_backbone_decode: bool
    fast_depth_decoder: bool
    fast_codec: bool


_settings: ApiSettings | None = None
_request_lock = threading.Lock()


def _pcm16(audio: np.ndarray) -> bytes:
    audio = np.asarray(audio, dtype=np.float32)
    audio = np.clip(audio, -1.0, 1.0)
    return (audio * 32767.0).astype("<i2", copy=False).tobytes()


def _iter_seeded_audio_chunks(
    runtime: FastBreezeStreamingRuntime,
    inputs: dict[str, object],
    *,
    request_id: str,
    seed: int,
) -> Iterator[FastStreamingChunk]:
    """Start model sampling from the request seed, after all input preparation.

    The response body runs after the endpoint has returned a ``StreamingResponse``.
    Seeding only while preparing the request leaves model sampling vulnerable to
    lazy initialization or unrelated RNG use between preparation and iteration.
    The API is deliberately single-request, so resetting the process generators at
    this boundary gives each request an isolated, reproducible sampling start.
    """
    set_all_seeds(seed)
    token_digest = None
    token_frames = 0
    if os.environ.get("BREEZE_DEBUG_TOKEN_HASH") == "1":
        token_digest = hashlib.sha256()

    def observe_token_frame(frame) -> None:
        nonlocal token_frames
        assert token_digest is not None
        token_digest.update(
            frame.detach().to(device="cpu").contiguous().numpy().tobytes()
        )
        token_frames += 1

    try:
        yield from runtime.iter_audio_chunks(
            inputs,
            request_id=request_id,
            seed=seed,
            token_observer=observe_token_frame if token_digest is not None else None,
        )
    finally:
        if token_digest is not None:
            print(
                "breeze token trace: "
                f"request_id={request_id} seed={seed} frames={token_frames} "
                f"sha256={token_digest.hexdigest()}",
                flush=True,
            )


async def _save_upload(upload: UploadFile) -> Path:
    suffix = Path(upload.filename or "reference.wav").suffix or ".wav"
    with tempfile.NamedTemporaryFile(
        prefix="breeze_ref_", suffix=suffix, delete=False
    ) as temporary:
        path = Path(temporary.name)
        try:
            payload = await upload.read()
            if not payload:
                raise HTTPException(status_code=400, detail="Reference audio is empty.")
            temporary.write(payload)
        except Exception:
            path.unlink(missing_ok=True)
            raise
    return path


def _load_app(app: FastAPI, settings: ApiSettings) -> None:
    tokenizer, model, audio_tokenizer = load_runtime(
        settings.model,
        device=resolve_device(),
        attn_implementation="eager",
    )
    update_generation_config_for_breeze(model)

    config = FastStreamingConfig(
        max_new_tokens=MAX_NEW_TOKENS,
        max_seq_len=MAX_SEQ_LEN,
        fast_all=settings.fast_all,
        fast_text_encoder=settings.fast_text_encoder,
        fast_backbone_prefill=settings.fast_backbone_prefill,
        fast_backbone_decode=settings.fast_backbone_decode,
        fast_depth_decoder=settings.fast_depth_decoder,
        fast_codec=settings.fast_codec,
        repetition_penalty=REPETITION_PENALTY,
    )
    runtime = FastBreezeStreamingRuntime(
        model, audio_tokenizer, config, tokenizer=tokenizer
    )
    if runtime.fast_enabled:
        profile = load_warmup_profile(FAST_CONFIG)
        profile = replace(profile, codec_chunk_frames=runtime.codec_chunk_frames)
        manifest = runtime.warmup_from_profile(profile)
        print(f"fast warmup: {manifest['total_elapsed_ms']:.2f} ms", flush=True)

    app.state.tokenizer = tokenizer
    app.state.model = model
    app.state.audio_tokenizer = audio_tokenizer
    app.state.runtime = runtime


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    if _settings is None:
        raise RuntimeError("API settings are not initialized")
    _load_app(app, _settings)
    yield


app = FastAPI(title="Breeze TTS API", lifespan=_lifespan)


@app.get("/health")
def health() -> JSONResponse:
    if not hasattr(app.state, "runtime"):
        return JSONResponse({"status": "loading"}, status_code=503)
    return JSONResponse({"status": "ok", "sample_rate": app.state.runtime.sample_rate})


@app.post("/v1/audio/speech")
async def speech(
    text: str = Form(...),
    instruction: str = Form("Speak clearly and naturally."),
    cfg_scale: float = Form(DEFAULT_CFG_SCALE),
    ref_audio: UploadFile | None = OPTIONAL_AUDIO_FILE,
    ref_text: str = Form(""),
    seed: int = Form(42),
) -> StreamingResponse:
    if not _request_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409, detail="An inference request is already running."
        )

    reference_path: Path | None = None
    try:
        if not np.isfinite(cfg_scale) or cfg_scale <= 0:
            raise HTTPException(
                status_code=400, detail="cfg_scale must be greater than 0."
            )
        ref_text = ref_text.strip()
        has_reference = ref_audio is not None and bool(ref_audio.filename)
        if has_reference != bool(ref_text):
            raise HTTPException(
                status_code=400,
                detail="ref_audio and ref_text must be provided together or both omitted.",
            )
        if has_reference:
            assert ref_audio is not None
            reference_path = await _save_upload(ref_audio)

        request_id = f"api-{uuid.uuid4().hex}"
        request = {
            "id": request_id,
            "text": text,
            "instruction": instruction,
            "speaker": "S0",
        }
        template_name = "tts_instruction"
        if reference_path is not None:
            request["ref_audio_path"] = str(reference_path)
            request["ref_text"] = ref_text
            template_name = "ref_edit_tata"

        set_all_seeds(seed)
        inputs = prepare_inputs(
            app.state.tokenizer,
            app.state.audio_tokenizer,
            app.state.model,
            [request],
            get_template(template_name),
            guidance_scale=cfg_scale,
            guidance_scale_ref=None,
            guidance_scale_ins=None,
        )
    except Exception:
        if reference_path is not None:
            reference_path.unlink(missing_ok=True)
        _request_lock.release()
        raise

    def body() -> Iterator[bytes]:
        try:
            for chunk in _iter_seeded_audio_chunks(
                app.state.runtime,
                inputs,
                request_id=request_id,
                seed=seed,
            ):
                pcm = _pcm16(chunk.audio)
                if pcm:
                    yield pcm
        finally:
            if reference_path is not None:
                reference_path.unlink(missing_ok=True)
            _request_lock.release()

    return StreamingResponse(
        body(),
        media_type="audio/pcm",
        headers={
            "X-Sample-Rate": str(app.state.runtime.sample_rate),
            "X-Sample-Format": "s16le",
            "Cache-Control": "no-store",
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Serve Breeze TTS 2 streaming inference"
    )
    parser.add_argument("model", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument(
        "--fast-all", action=argparse.BooleanOptionalAction, default=None
    )
    parser.add_argument(
        "--fast-text-encoder", action=argparse.BooleanOptionalAction, default=False
    )
    parser.add_argument(
        "--fast-backbone-prefill", action=argparse.BooleanOptionalAction, default=False
    )
    parser.add_argument(
        "--fast-backbone-decode", action=argparse.BooleanOptionalAction, default=False
    )
    parser.add_argument(
        "--fast-depth-decoder", action=argparse.BooleanOptionalAction, default=False
    )
    parser.add_argument(
        "--fast-codec", action=argparse.BooleanOptionalAction, default=False
    )
    args = parser.parse_args()

    global _settings
    _settings = ApiSettings(
        model=args.model,
        fast_all=args.fast_all,
        fast_text_encoder=args.fast_text_encoder,
        fast_backbone_prefill=args.fast_backbone_prefill,
        fast_backbone_decode=args.fast_backbone_decode,
        fast_depth_decoder=args.fast_depth_decoder,
        fast_codec=args.fast_codec,
    )

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
