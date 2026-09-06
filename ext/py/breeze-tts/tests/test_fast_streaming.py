from __future__ import annotations

from types import SimpleNamespace

import pytest
import torch

from breeze_infer.templates import get_template
from models.fast_streaming import (
    FastBreezeStreamingRuntime,
    FastStreamingConfig,
    _get_dtype,
    is_backbone_eos_token,
    is_terminal_pad_frame,
    reject_dual_cfg,
    select_fast_cfg,
    should_decode_codec_frame,
)


def test_runtime_dtype_follows_backbone_after_shared_lm_head_is_cast() -> None:
    class CompositeModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.lm_head = torch.nn.Linear(2, 2, bias=False, dtype=torch.bfloat16)
            self.backbone_model = torch.nn.Linear(
                2, 2, bias=False, dtype=torch.bfloat16
            )

    model = CompositeModel()
    assert _get_dtype(model) == torch.bfloat16

    # BackboneGraph mutates the shared projection in exactly this way.
    model.lm_head.float()

    assert next(model.parameters()).dtype == torch.float32
    assert _get_dtype(model) == torch.bfloat16


def test_fast_streaming_defaults_to_repetition_penalty_1p1() -> None:
    assert FastStreamingConfig().repetition_penalty == 1.1


def test_fast_streaming_exposes_master_and_one_switch_per_stage() -> None:
    config = FastStreamingConfig()
    fast_fields = [
        name for name in config.__dataclass_fields__ if name.startswith("fast_")
    ]

    assert fast_fields == [
        "fast_all",
        "fast_text_encoder",
        "fast_backbone_prefill",
        "fast_backbone_decode",
        "fast_depth_decoder",
        "fast_codec",
    ]
    assert config.fast_all is None
    assert all(getattr(config, name) is False for name in fast_fields[1:])


def test_fast_streaming_master_switch_overrides_stage_switches() -> None:
    all_eager = FastStreamingConfig(fast_all=False)
    all_fast = FastStreamingConfig(fast_all=True, fast_codec=False)

    assert all_eager.stage_fast("text_encoder") is False
    assert all_eager.stage_fast("codec") is False
    assert all_fast.stage_fast("codec") is True
    assert FastStreamingConfig(fast_codec=False).stage_fast("codec") is False


def test_fast_cfg_selects_no_cfg_by_default() -> None:
    cfg = select_fast_cfg({})

    assert cfg.mode == "no_cfg"
    assert cfg.guidance_scale == 1.0
    assert cfg.use_negative_as_main is False


def test_fast_cfg_selects_single_cfg_when_negative_prompt_is_present() -> None:
    cfg = select_fast_cfg(
        {
            "cfg_scale": 2.5,
            "cfg_negative_prompt_ids": torch.ones(1, 2, dtype=torch.long),
        }
    )

    assert cfg.mode == "single_cfg"
    assert cfg.guidance_scale == 2.5
    assert cfg.use_negative_as_main is False


def test_fast_cfg_zero_uses_negative_as_main() -> None:
    cfg = select_fast_cfg(
        {
            "cfg_scale": 0.0,
            "cfg_negative_prompt_ids": torch.ones(1, 2, dtype=torch.long),
        }
    )

    assert cfg.mode == "no_cfg"
    assert cfg.guidance_scale == 1.0
    assert cfg.use_negative_as_main is True


def test_fast_streaming_rejects_dual_cfg_fields() -> None:
    with pytest.raises(ValueError, match="dual CFG"):
        reject_dual_cfg({"cfg_scale_ref": 1.0, "cfg_scale_ins": 2.0})


def test_backbone_eos_and_pad_frame_are_distinct() -> None:
    config = SimpleNamespace(vocab_size=2051, codebook_pad_token_id=2050)

    assert is_backbone_eos_token(torch.tensor(2051), config)
    assert not is_backbone_eos_token(torch.tensor(0), config)
    assert not is_terminal_pad_frame(torch.zeros(16, dtype=torch.long), config)

    pad_frame = torch.full((16,), 2050, dtype=torch.long)
    assert is_terminal_pad_frame(pad_frame, config)
    assert not should_decode_codec_frame(pad_frame, config)


def test_ref_edit_tata_negative_branch_is_clone_without_instruction() -> None:
    template = get_template("ref_edit_tata")
    request = {
        "text": "target",
        "instruction": "speak softly",
        "ref_audio_path": "/tmp/ref.wav",
        "ref_text": "reference",
        "speaker": "S0",
    }

    positive = template.build_segments(request)
    negative = template.build_negative_segments(request)

    assert "<ins_bos>speak softly<ins_eos>target" in positive[-1]["text"]
    assert negative[-1]["text"] == "[S0]target"
    assert "<ins_bos>" not in negative[-1]["text"]


def test_single_cfg_merges_cond_and_uncond_in_one_batched_text_path() -> None:
    class FakeModel:
        def __init__(self) -> None:
            self.calls = []

        def _merge_input_ids_with_input_values(self, **kwargs):
            self.calls.append(kwargs)
            return {"inputs_embeds": kwargs["input_ids"].unsqueeze(-1).float()}

    runtime = object.__new__(FastBreezeStreamingRuntime)
    runtime.model = FakeModel()
    runtime._fast_text_encoder = True
    inputs = {
        "input_ids": torch.tensor([[1, 2, 3]]),
        "attention_mask": torch.ones(1, 3, dtype=torch.long),
        "text_ids_mask": torch.ones(1, 3, dtype=torch.bool),
        "text_ids_len": torch.tensor([3]),
        "input_values": None,
        "cfg_scale": 2.0,
        "cfg_negative_prompt_ids": torch.tensor([[4, 5]]),
        "cfg_negative_prompt_attention_mask": torch.ones(1, 2, dtype=torch.long),
        "cfg_negative_text_ids_mask": torch.ones(1, 2, dtype=torch.bool),
        "cfg_negative_text_ids_len": torch.tensor([2]),
    }

    branch = runtime._build_branch_batch(inputs)

    assert branch.branch_batch_size == 2
    assert len(runtime.model.calls) == 1
    call = runtime.model.calls[0]
    assert call["input_ids"].tolist() == [[1, 2, 3], [0, 4, 5]]
    assert call["attention_mask"].tolist() == [[1, 1, 1], [0, 1, 1]]
    assert call["text_ids_len"].tolist() == [3, 2]
    assert branch.inputs_embeds[..., 0].tolist() == [[1.0, 2.0, 3.0], [0.0, 4.0, 5.0]]

    runtime.model.calls.clear()
    runtime._fast_text_encoder = False
    eager_branch = runtime._build_branch_batch(inputs)

    assert eager_branch.branch_batch_size == 2
    assert len(runtime.model.calls) == 2
