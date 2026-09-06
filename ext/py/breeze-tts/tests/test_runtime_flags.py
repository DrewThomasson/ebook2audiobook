from __future__ import annotations

from models.fast_streaming import FastBreezeStreamingRuntime


def test_runtime_fast_properties_return_values_not_methods() -> None:
    runtime = FastBreezeStreamingRuntime.__new__(FastBreezeStreamingRuntime)
    runtime._fast_text_encoder = False
    runtime._fast_backbone_prefill = False
    runtime._fast_backbone_decode = False
    runtime._fast_depth_decoder = False
    runtime._fast_codec = False
    runtime._codec_chunk_frames = 2

    assert runtime.fast_enabled is False
    assert runtime.codec_chunk_frames == 2

    runtime._fast_codec = True
    runtime._codec_chunk_frames = 1

    assert runtime.fast_enabled is True
    assert runtime.codec_chunk_frames == 1
