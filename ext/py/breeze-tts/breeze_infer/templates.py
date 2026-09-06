from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import torch
import torch.nn.functional as F

from .audio import encode_prompt_audio

AUDIO_TAG = "<|AUDIO|>"
AUDIO_EOS = "<|audio_eos|>"
INSTRUCTION_BOS = "<ins_bos>"
INSTRUCTION_EOS = "<ins_eos>"


Segment = dict[str, Any]
Request = dict[str, Any]


@dataclass(frozen=True)
class TemplateSpec:
    name: str
    required_fields: tuple[str, ...]
    build_segments: Callable[[Request], list[Segment]]
    build_negative_segments: Callable[[Request], list[Segment]] | None = None
    build_dual_branches: Callable[[Request], dict[str, list[Segment]]] | None = None


def _speaker_prefix(request: Request) -> str:
    speaker = request.get("speaker", "S0")
    if speaker in (None, ""):
        return ""
    if isinstance(speaker, str) and speaker.startswith("[") and speaker.endswith("]"):
        return speaker
    return f"[{speaker}]"


def _tts_plain_segments(request: Request) -> list[Segment]:
    return [{"type": "text", "text": f"{_speaker_prefix(request)}{request['text']}"}]


def _tts_instruction_segments(request: Request) -> list[Segment]:
    prefix = _speaker_prefix(request)
    return [
        {
            "type": "text",
            "text": f"{prefix}{INSTRUCTION_BOS}{request['instruction']}{INSTRUCTION_EOS}{request['text']}",
        }
    ]


def _tts_instruction_negative_segments(request: Request) -> list[Segment]:
    return _tts_plain_segments(request)


def _ref_audio_segment(
    request: Request,
    *,
    append_eos: bool = True,
    drop_last_frame: bool = False,
) -> Segment:
    segment: Segment = {
        "type": "audio",
        "append_eos": append_eos,
        "drop_last_frame": drop_last_frame,
    }
    if request.get("ref_audio_path"):
        segment["audio_path"] = request["ref_audio_path"]
    return segment


def _ref_clone_tata_segments(request: Request) -> list[Segment]:
    prefix = _speaker_prefix(request)
    return [
        {"type": "text", "text": f"{prefix}{request['ref_text']}"},
        _ref_audio_segment(request),
        {"type": "text", "text": f"{prefix}{request['text']}"},
    ]


def _ref_edit_tata_segments(request: Request) -> list[Segment]:
    prefix = _speaker_prefix(request)
    return [
        {"type": "text", "text": f"{prefix}{request['ref_text']}"},
        _ref_audio_segment(request),
        {
            "type": "text",
            "text": f"{prefix}{INSTRUCTION_BOS}{request['instruction']}{INSTRUCTION_EOS}{request['text']}",
        },
    ]


def _ref_edit_tata_negative_segments(request: Request) -> list[Segment]:
    return _ref_clone_tata_segments(request)


def _ref_edit_tata_dual_branches(request: Request) -> dict[str, list[Segment]]:
    prefix = _speaker_prefix(request)
    return {
        "uncond": [{"type": "text", "text": f"{prefix}{request['text']}"}],
        "ref": _ref_clone_tata_segments(request),
        "ins": _tts_instruction_segments(request),
    }


TEMPLATES: dict[str, TemplateSpec] = {
    "tts_instruction": TemplateSpec(
        name="tts_instruction",
        required_fields=("text", "instruction"),
        build_segments=_tts_instruction_segments,
        build_negative_segments=_tts_instruction_negative_segments,
    ),
    "ref_edit_tata": TemplateSpec(
        name="ref_edit_tata",
        required_fields=("text", "instruction", "ref_audio_path", "ref_text"),
        build_segments=_ref_edit_tata_segments,
        build_negative_segments=_ref_edit_tata_negative_segments,
        build_dual_branches=_ref_edit_tata_dual_branches,
    ),
}


def get_template(name: str) -> TemplateSpec:
    try:
        return TEMPLATES[name]
    except KeyError as exc:
        raise KeyError(
            f"Unknown template '{name}'. Available: {sorted(TEMPLATES)}"
        ) from exc


def _encode_prompt_audio(audio_tokenizer: Any, audio_path: str) -> torch.Tensor:
    return encode_prompt_audio(audio_tokenizer, audio_path)


def _resolve_segment_audio_codes(
    audio_tokenizer: Any, segment: Segment
) -> torch.Tensor:
    audio_path = segment.get("audio_path")
    if not audio_path:
        raise ValueError("Audio segment must include audio_path")
    return _encode_prompt_audio(audio_tokenizer, audio_path)


def _prepare_one(
    tokenizer: Any,
    audio_tokenizer: Any,
    model_config: Any,
    segments: list[Segment],
) -> dict[str, torch.Tensor]:
    rendered_segments: list[dict[str, str]] = []
    audio_tokens_list: list[torch.Tensor] = []

    for segment in segments:
        segment_type = segment["type"]
        if segment_type == "text":
            encoded = tokenizer(segment["text"], add_special_tokens=True)
            rendered = tokenizer.decode(encoded["input_ids"], skip_special_tokens=False)
            rendered_segments.append({"type": "text", "value": rendered})
            continue

        if segment_type != "audio":
            raise ValueError(f"Unknown segment type: {segment_type}")

        codes = _resolve_segment_audio_codes(audio_tokenizer, segment)
        if segment.get("drop_last_frame", False):
            if codes.shape[0] <= 1:
                raise ValueError(
                    "Cannot drop the last frame from an audio segment with <= 1 frame"
                )
            codes = codes[:-1].contiguous()
        audio_tokens_list.append(codes)

        placeholders = AUDIO_TAG * codes.shape[0]
        if segment.get("append_eos", False):
            placeholders += AUDIO_EOS
        rendered_segments.append({"type": "audio", "value": placeholders})

    final_text = "".join(segment["value"] for segment in rendered_segments)
    encoded = tokenizer(final_text, add_special_tokens=False, return_tensors="pt")

    text_ids_mask: list[bool] = []
    text_ids_len: list[int] = []
    for segment in rendered_segments:
        segment_len = len(
            tokenizer(segment["value"], add_special_tokens=False)["input_ids"]
        )
        if segment["type"] == "text":
            text_ids_mask.extend([True] * segment_len)
            text_ids_len.append(segment_len)
        else:
            text_ids_mask.extend([False] * segment_len)

    num_codebooks = getattr(model_config, "num_codebooks", 16)
    if audio_tokens_list:
        audio_tokens = torch.cat(audio_tokens_list, dim=0).unsqueeze(0)
    else:
        audio_tokens = torch.zeros((1, 0, num_codebooks), dtype=torch.int16)

    encoded["audio_tokens"] = audio_tokens
    encoded["text_ids_mask"] = torch.tensor([text_ids_mask], dtype=torch.bool)
    encoded["text_ids_len"] = torch.tensor(text_ids_len, dtype=torch.long)
    return encoded


def _collate_inputs(
    tokenizer: Any, inputs_list: list[dict[str, torch.Tensor]], device: str
) -> dict[str, torch.Tensor | None]:
    pad_token_id = tokenizer.pad_token_id
    if pad_token_id is None:
        pad_token_id = tokenizer.eos_token_id
    if pad_token_id is None:
        raise ValueError("Tokenizer has no pad_token_id or eos_token_id")

    audio_tokens = torch.cat([item["audio_tokens"] for item in inputs_list], dim=1)
    max_len = max(item["input_ids"].shape[1] for item in inputs_list)

    input_ids_list = []
    attention_mask_list = []
    text_ids_mask_list = []
    for item in inputs_list:
        input_ids = item["input_ids"]
        attention_mask = item["attention_mask"]
        text_ids_mask = item["text_ids_mask"]
        pad_len = max_len - input_ids.shape[1]
        if pad_len > 0:
            input_ids = F.pad(input_ids, (pad_len, 0), value=pad_token_id)
            attention_mask = F.pad(attention_mask, (pad_len, 0), value=0)
            text_ids_mask = F.pad(text_ids_mask, (pad_len, 0), value=False)
        input_ids_list.append(input_ids)
        attention_mask_list.append(attention_mask)
        text_ids_mask_list.append(text_ids_mask)

    input_values = audio_tokens.to(device) if audio_tokens.shape[1] > 0 else None
    return {
        "input_ids": torch.cat(input_ids_list, dim=0).to(device),
        "attention_mask": torch.cat(attention_mask_list, dim=0).to(device),
        "text_ids_mask": torch.cat(text_ids_mask_list, dim=0).to(device),
        "text_ids_len": torch.cat(
            [item["text_ids_len"] for item in inputs_list], dim=0
        ).to(device),
        "input_values": input_values,
    }


def _prepare_segment_batches(
    tokenizer: Any,
    audio_tokenizer: Any,
    model_config: Any,
    device: str,
    segment_batches: list[list[Segment]],
) -> dict[str, torch.Tensor | None]:
    inputs_list = [
        _prepare_one(tokenizer, audio_tokenizer, model_config, segments)
        for segments in segment_batches
    ]
    return _collate_inputs(tokenizer, inputs_list, device)


def prepare_inputs(
    tokenizer: Any,
    audio_tokenizer: Any,
    model: Any,
    requests: list[Request],
    template: TemplateSpec,
    *,
    guidance_scale: float,
    guidance_scale_ref: float | None,
    guidance_scale_ins: float | None,
) -> dict[str, torch.Tensor | None | float]:
    for request in requests:
        missing = []
        for field in template.required_fields:
            if not request.get(field):
                missing.append(field)
        if missing:
            raise ValueError(
                f"Request {request.get('id')} missing template fields: {missing}"
            )

    positive_segments = [template.build_segments(request) for request in requests]
    inputs = _prepare_segment_batches(
        tokenizer,
        audio_tokenizer,
        model.config,
        model.device,
        positive_segments,
    )

    use_dual_cfg = (
        guidance_scale_ref is not None
        and guidance_scale_ins is not None
        and template.build_dual_branches is not None
    )
    if use_dual_cfg:
        branch_batches = [template.build_dual_branches(request) for request in requests]
        for branch_name, prefix in [
            ("uncond", "cfg_uncond"),
            ("ref", "cfg_ref"),
            ("ins", "cfg_ins"),
        ]:
            branch_inputs = _prepare_segment_batches(
                tokenizer,
                audio_tokenizer,
                model.config,
                model.device,
                [branches[branch_name] for branches in branch_batches],
            )
            inputs[f"{prefix}_prompt_ids"] = branch_inputs["input_ids"]
            inputs[f"{prefix}_prompt_attention_mask"] = branch_inputs["attention_mask"]
            inputs[f"{prefix}_text_ids_mask"] = branch_inputs["text_ids_mask"]
            inputs[f"{prefix}_text_ids_len"] = branch_inputs["text_ids_len"]
        inputs["cfg_scale_ref"] = guidance_scale_ref
        inputs["cfg_scale_ins"] = guidance_scale_ins
        return inputs

    if guidance_scale != 1.0:
        if template.build_negative_segments is None:
            raise ValueError(
                f"Template '{template.name}' does not define a negative prompt but cfg_scale={guidance_scale}"
            )
        negative_inputs = _prepare_segment_batches(
            tokenizer,
            audio_tokenizer,
            model.config,
            model.device,
            [template.build_negative_segments(request) for request in requests],
        )
        inputs["cfg_negative_prompt_ids"] = negative_inputs["input_ids"]
        inputs["cfg_negative_prompt_attention_mask"] = negative_inputs["attention_mask"]
        inputs["cfg_negative_text_ids_mask"] = negative_inputs["text_ids_mask"]
        inputs["cfg_negative_text_ids_len"] = negative_inputs["text_ids_len"]
        if negative_inputs["input_values"] is not None:
            inputs["cfg_negative_input_values"] = negative_inputs["input_values"]
        inputs["cfg_scale"] = guidance_scale

    return inputs
