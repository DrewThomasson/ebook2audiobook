from __future__ import annotations

import os

BACKEND_NAME = os.environ.get("QWEN_TTS_STREAM_BACKEND", "official").strip().lower()

if BACKEND_NAME == "official":
    from qwen_tts.core.tokenizer_12hz.modeling_qwen3_tts_tokenizer_v2 import (
        Qwen3TTSTokenizerV2CausalConvNet,
        Qwen3TTSTokenizerV2CausalTransConvNet,
        Qwen3TTSTokenizerV2ConvNeXtBlock,
        Qwen3TTSTokenizerV2Decoder,
        Qwen3TTSTokenizerV2DecoderDecoderBlock,
        Qwen3TTSTokenizerV2DecoderDecoderResidualUnit,
    )
    from qwen_tts.inference.qwen3_tts_tokenizer import Qwen3TTSTokenizer
else:
    raise ImportError(
        "Breeze streaming runtime only supports the official qwen_tts backend. "
        "Set QWEN_TTS_STREAM_BACKEND=official or leave it unset."
    )


__all__ = [
    "BACKEND_NAME",
    "Qwen3TTSTokenizer",
    "Qwen3TTSTokenizerV2CausalConvNet",
    "Qwen3TTSTokenizerV2CausalTransConvNet",
    "Qwen3TTSTokenizerV2ConvNeXtBlock",
    "Qwen3TTSTokenizerV2Decoder",
    "Qwen3TTSTokenizerV2DecoderDecoderBlock",
    "Qwen3TTSTokenizerV2DecoderDecoderResidualUnit",
]
