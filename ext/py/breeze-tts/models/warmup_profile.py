from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TextEncoderWarmupGraph:
    batch_size: int
    token_length: int


@dataclass(frozen=True)
class BackbonePrefillWarmupGraph:
    branch_batch_size: int
    sequence_length: int


@dataclass(frozen=True)
class SyntheticWarmupRequest:
    template: str
    text: str
    instruction: str
    speaker: str
    seed: int


@dataclass(frozen=True)
class FastStreamingWarmupProfile:
    schema_version: int
    name: str
    cfg_scales: tuple[float, ...]
    text_encoder_graphs: tuple[TextEncoderWarmupGraph, ...]
    backbone_prefill_graphs: tuple[BackbonePrefillWarmupGraph, ...]
    backbone_decode_branch_batch_sizes: tuple[int, ...]
    depth_decoder_batch_sizes: tuple[int, ...]
    codec_chunk_frames: int
    codec_num_lanes: int
    warmup_request: SyntheticWarmupRequest
    freeze_after_warmup: bool
    source: str | None = None

    @property
    def cfg_modes(self) -> tuple[str, ...]:
        return tuple(
            "single_cfg" if cfg_scale != 1.0 else "no_cfg"
            for cfg_scale in self.cfg_scales
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "service": {
                "concurrency": 1,
                "cfg_scales": list(self.cfg_scales),
                "cfg_modes": list(self.cfg_modes),
                "freeze_after_warmup": self.freeze_after_warmup,
            },
            "stages": {
                "text_encoder": {
                    "graphs": [
                        {
                            "batch_size": graph.batch_size,
                            "token_length": graph.token_length,
                        }
                        for graph in self.text_encoder_graphs
                    ]
                },
                "backbone_prefill": {
                    "graphs": [
                        {
                            "branch_batch_size": graph.branch_batch_size,
                            "sequence_length": graph.sequence_length,
                        }
                        for graph in self.backbone_prefill_graphs
                    ]
                },
                "backbone_decode": {
                    "graphs": [
                        {"branch_batch_size": batch_size}
                        for batch_size in self.backbone_decode_branch_batch_sizes
                    ]
                },
                "depth_decoder": {
                    "graphs": [
                        {"batch_size": batch_size}
                        for batch_size in self.depth_decoder_batch_sizes
                    ]
                },
                "codec": {
                    "graphs": [
                        {
                            "num_lanes": self.codec_num_lanes,
                            "chunk_frames": self.codec_chunk_frames,
                        }
                    ]
                },
            },
            "warmup_request": {
                "template": self.warmup_request.template,
                "text": self.warmup_request.text,
                "instruction": self.warmup_request.instruction,
                "speaker": self.warmup_request.speaker,
                "seed": self.warmup_request.seed,
            },
        }


def _positive_int(value: Any, path: str) -> int:
    value = int(value)
    if value <= 0:
        raise ValueError(f"{path} must be > 0")
    return value


def _graphs(stages: dict[str, Any], stage: str) -> list[dict[str, Any]]:
    value = stages.get(stage)
    if not isinstance(value, dict):
        raise ValueError(f"stages.{stage} must be an object")
    graphs = value.get("graphs")
    if not isinstance(graphs, list) or not graphs:
        raise ValueError(f"stages.{stage}.graphs must be a non-empty list")
    if not all(isinstance(graph, dict) for graph in graphs):
        raise ValueError(f"stages.{stage}.graphs entries must be objects")
    return graphs


def parse_warmup_profile(
    payload: dict[str, Any], *, source: str | None = None
) -> FastStreamingWarmupProfile:
    if int(payload.get("schema_version", 0)) != 1:
        raise ValueError("warmup profile schema_version must be 1")
    name = str(payload.get("name", "")).strip()
    if not name:
        raise ValueError("warmup profile name must not be empty")

    service = payload.get("service")
    if not isinstance(service, dict):
        raise ValueError("service must be an object")
    concurrency = _positive_int(service.get("concurrency", 0), "service.concurrency")
    if concurrency != 1:
        raise ValueError("fast streaming warmup supports only service.concurrency=1")
    raw_cfg_scales = service.get("cfg_scales")
    if not isinstance(raw_cfg_scales, list) or not raw_cfg_scales:
        raise ValueError("service.cfg_scales must be a non-empty list")
    cfg_scales = tuple(sorted({float(value) for value in raw_cfg_scales}))
    if any(cfg_scale < 1.0 for cfg_scale in cfg_scales):
        raise ValueError("warmup profiles require service.cfg_scales values >= 1")
    expected_branch_batches = tuple(
        sorted({1 if cfg_scale == 1.0 else 2 for cfg_scale in cfg_scales})
    )
    freeze_after_warmup = bool(service.get("freeze_after_warmup", True))

    stages = payload.get("stages")
    if not isinstance(stages, dict):
        raise ValueError("stages must be an object")

    text_graphs = tuple(
        TextEncoderWarmupGraph(
            batch_size=_positive_int(
                graph.get("batch_size"), "text_encoder.batch_size"
            ),
            token_length=_positive_int(
                graph.get("token_length"), "text_encoder.token_length"
            ),
        )
        for graph in _graphs(stages, "text_encoder")
    )
    if any(graph.token_length % 32 for graph in text_graphs):
        raise ValueError("text_encoder token_length values must be multiples of 32")
    prefill_graphs = tuple(
        BackbonePrefillWarmupGraph(
            branch_batch_size=_positive_int(
                graph.get("branch_batch_size"), "backbone_prefill.branch_batch_size"
            ),
            sequence_length=_positive_int(
                graph.get("sequence_length"), "backbone_prefill.sequence_length"
            ),
        )
        for graph in _graphs(stages, "backbone_prefill")
    )
    if any(graph.sequence_length % 32 for graph in prefill_graphs):
        raise ValueError(
            "backbone_prefill sequence_length values must be multiples of 32"
        )

    decode_batches = tuple(
        sorted(
            {
                _positive_int(
                    graph.get("branch_batch_size"),
                    "backbone_decode.branch_batch_size",
                )
                for graph in _graphs(stages, "backbone_decode")
            }
        )
    )
    if decode_batches != expected_branch_batches:
        raise ValueError(
            "backbone_decode branch batches must match cfg_scales; "
            f"expected {expected_branch_batches}, got {decode_batches}"
        )
    if {graph.branch_batch_size for graph in prefill_graphs} != set(decode_batches):
        raise ValueError(
            "backbone_prefill must declare graphs for every backbone_decode branch batch"
        )

    depth_batches = tuple(
        _positive_int(graph.get("batch_size"), "depth_decoder.batch_size")
        for graph in _graphs(stages, "depth_decoder")
    )
    if tuple(sorted(set(depth_batches))) != expected_branch_batches:
        raise ValueError(
            "depth_decoder batch sizes must match cfg_scales; "
            f"expected {expected_branch_batches}"
        )

    codec_graphs = _graphs(stages, "codec")
    if len(codec_graphs) != 1:
        raise ValueError("codec must declare exactly one graph")
    codec_num_lanes = _positive_int(codec_graphs[0].get("num_lanes"), "codec.num_lanes")
    codec_chunk_frames = _positive_int(
        codec_graphs[0].get("chunk_frames"), "codec.chunk_frames"
    )
    if codec_num_lanes != 1:
        raise ValueError("single-concurrency service requires codec.num_lanes=1")

    warmup_request_payload = payload.get("warmup_request")
    if not isinstance(warmup_request_payload, dict):
        raise ValueError("warmup_request must be an object")
    warmup_request = SyntheticWarmupRequest(
        template=str(warmup_request_payload.get("template", "")).strip(),
        text=str(warmup_request_payload.get("text", "")).strip(),
        instruction=str(warmup_request_payload.get("instruction", "")).strip(),
        speaker=str(warmup_request_payload.get("speaker", "S0")).strip(),
        seed=int(warmup_request_payload.get("seed", 42)),
    )
    if not warmup_request.template or not warmup_request.text:
        raise ValueError(
            "warmup_request.template and warmup_request.text must not be empty"
        )

    return FastStreamingWarmupProfile(
        schema_version=1,
        name=name,
        cfg_scales=cfg_scales,
        text_encoder_graphs=tuple(
            sorted(
                set(text_graphs),
                key=lambda graph: (graph.batch_size, graph.token_length),
            )
        ),
        backbone_prefill_graphs=tuple(
            sorted(
                set(prefill_graphs),
                key=lambda graph: (graph.branch_batch_size, graph.sequence_length),
            )
        ),
        backbone_decode_branch_batch_sizes=decode_batches,
        depth_decoder_batch_sizes=depth_batches,
        codec_chunk_frames=codec_chunk_frames,
        codec_num_lanes=codec_num_lanes,
        warmup_request=warmup_request,
        freeze_after_warmup=freeze_after_warmup,
        source=source,
    )


def load_warmup_profile(path: str | Path) -> FastStreamingWarmupProfile:
    path = Path(path).resolve()
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("warmup profile root must be an object")
    return parse_warmup_profile(payload, source=str(path))
