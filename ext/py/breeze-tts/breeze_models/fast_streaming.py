from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np
import torch

from .cudagraph.backbone_graph import BackboneGraph
from .cudagraph.backbone_prefill_graph import BackbonePrefillGraphCache
from .cudagraph.depth_decoder_graph import DepthDecoderGraph
from .cudagraph.sampling import sample_logits
from .warmup_profile import FastStreamingWarmupProfile

FastCfgMode = Literal["no_cfg", "single_cfg"]

_DUAL_CFG_KEYS = (
    "cfg_scale_ref",
    "cfg_scale_ins",
    "cfg_uncond_prompt_ids",
    "cfg_ref_prompt_ids",
    "cfg_ins_prompt_ids",
)


@dataclass(frozen=True)
class FastStreamingConfig:
    max_new_tokens: int = 750
    max_seq_len: int = 1024
    collect_timing: bool = False
    fast_all: bool | None = None
    fast_text_encoder: bool = False
    fast_backbone_prefill: bool = False
    fast_backbone_decode: bool = False
    fast_depth_decoder: bool = False
    fast_codec: bool = False
    temperature: float | None = None
    top_k: int | None = None
    top_p: float | None = None
    do_sample: bool | None = None
    repetition_penalty: float = 1.1

    def stage_fast(self, stage: str) -> bool:
        """Resolve the master switch before the per-stage setting."""
        if self.fast_all is not None:
            return self.fast_all
        field_name = f"fast_{stage}"
        if field_name not in self.__dataclass_fields__ or field_name == "fast_all":
            raise ValueError(f"unknown fast path stage: {stage!r}")
        return bool(getattr(self, field_name))


@dataclass(frozen=True)
class FastStreamingChunk:
    audio: np.ndarray
    sample_rate: int
    codec_frames: int
    is_final: bool
    timing: dict[str, float | int | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class FastCfgSelection:
    mode: FastCfgMode
    guidance_scale: float
    use_negative_as_main: bool


@dataclass
class _BranchBatch:
    inputs_embeds: torch.Tensor
    attention_mask: torch.Tensor
    branch_batch_size: int
    cfg: FastCfgSelection


def reject_dual_cfg(inputs: dict[str, Any]) -> None:
    present = [key for key in _DUAL_CFG_KEYS if inputs.get(key) is not None]
    if present:
        raise ValueError(
            "fast streaming supports only no_cfg and single_cfg; "
            f"dual CFG fields are not supported: {present}"
        )


def select_fast_cfg(inputs: dict[str, Any]) -> FastCfgSelection:
    reject_dual_cfg(inputs)
    cfg_scale = float(inputs.get("cfg_scale", 1.0))
    has_negative = inputs.get("cfg_negative_prompt_ids") is not None
    if cfg_scale == 0.0 and has_negative:
        return FastCfgSelection(
            mode="no_cfg", guidance_scale=1.0, use_negative_as_main=True
        )
    if cfg_scale != 1.0:
        if not has_negative:
            raise ValueError(
                "single_cfg requires cfg_negative_prompt_ids when cfg_scale != 1.0"
            )
        return FastCfgSelection(
            mode="single_cfg", guidance_scale=cfg_scale, use_negative_as_main=False
        )
    return FastCfgSelection(
        mode="no_cfg", guidance_scale=1.0, use_negative_as_main=False
    )


def is_backbone_eos_token(token: torch.Tensor | int, config: Any) -> bool:
    token_id = int(token.item() if isinstance(token, torch.Tensor) else token)
    return token_id == int(config.vocab_size)


def is_terminal_pad_frame(frame: torch.Tensor, config: Any) -> bool:
    return bool((frame == int(config.codebook_pad_token_id)).all().item())


def should_decode_codec_frame(frame: torch.Tensor, config: Any) -> bool:
    return not is_terminal_pad_frame(frame, config)


def _get_device(model: torch.nn.Module) -> torch.device:
    try:
        return next(model.parameters()).device
    except StopIteration:
        return torch.device("cpu")


def _get_dtype(model: torch.nn.Module) -> torch.dtype:
    # The composite model registers lm_head before the semantic backbone. CUDA
    # graph setup intentionally casts that shared projection head to float32,
    # so using the first composite parameter makes a later runtime select an
    # FP32 KV cache for an otherwise BF16 backbone.
    backbone_model = getattr(model, "backbone_model", None)
    if isinstance(backbone_model, torch.nn.Module):
        try:
            return next(backbone_model.parameters()).dtype
        except StopIteration:
            pass
    try:
        return next(model.parameters()).dtype
    except StopIteration:
        return torch.bfloat16


def _left_pad_tensor(
    tensor: torch.Tensor, target_len: int, value: float = 0
) -> torch.Tensor:
    pad_len = target_len - tensor.shape[1]
    if pad_len <= 0:
        return tensor
    pad_shape = (tensor.shape[0], pad_len, *tensor.shape[2:])
    pad = torch.full(pad_shape, value, dtype=tensor.dtype, device=tensor.device)
    return torch.cat([pad, tensor], dim=1)


def _extract_audio_np(audio: torch.Tensor) -> np.ndarray:
    while audio.dim() > 1:
        audio = audio[0]
    return audio.detach().float().cpu().numpy()


class FastBreezeStreamingRuntime:
    def __init__(
        self,
        model: torch.nn.Module,
        audio_tokenizer: Any,
        config: FastStreamingConfig | None = None,
        *,
        tokenizer: Any | None = None,
    ) -> None:
        self.model = model
        self.audio_tokenizer = audio_tokenizer
        self.tokenizer = tokenizer
        self.config = config or FastStreamingConfig()
        self._fast_text_encoder = self.config.stage_fast("text_encoder")
        self._fast_backbone_prefill = self.config.stage_fast("backbone_prefill")
        self._fast_backbone_decode = self.config.stage_fast("backbone_decode")
        self._fast_depth_decoder = self.config.stage_fast("depth_decoder")
        self._fast_codec = self.config.stage_fast("codec")
        self.model._fast_text_encoder_cudagraph = self._fast_text_encoder
        self._codec_chunk_frames = 1 if self._fast_codec else 2
        self.device = _get_device(model)
        self.dtype = _get_dtype(model)
        self._backbone_graph: BackboneGraph | None = None
        self._backbone_graphs: dict[int, BackboneGraph] = {}
        self._backbone_prefill_graph: BackbonePrefillGraphCache | None = None
        self._backbone_prefill_graphs: dict[int, BackbonePrefillGraphCache] = {}
        self._depth_decoder_graph: DepthDecoderGraph | None = None
        self._codec_runtime = None
        self._warmup_profile: FastStreamingWarmupProfile | None = None
        self._warmup_manifest: dict[str, Any] | None = None
        self._frozen_branch_batch_sizes: frozenset[int] | None = None
        self._codec_codebook_size = int(self.model.config.codec_config.codebook_size)
        self._reserved_codec_token_ids = tuple(
            range(self._codec_codebook_size, int(self.model.config.vocab_size))
        )

        if self.device.type != "cuda":
            raise RuntimeError("fast streaming requires a CUDA device")
        if self.config.repetition_penalty <= 0:
            raise ValueError("repetition_penalty must be > 0")

    @property
    def sample_rate(self) -> int:
        return int(self.model.config.codec_config.sampling_rate)

    def _sampling_params(self, generation_config: Any) -> dict[str, Any]:
        def _value(name: str, override: Any, default: Any) -> Any:
            if override is not None:
                return override
            value = getattr(generation_config, name, default)
            return default if value is None else value

        return {
            "temperature": float(_value("temperature", self.config.temperature, 1.0)),
            "top_k": int(_value("top_k", self.config.top_k, 0)),
            "top_p": float(_value("top_p", self.config.top_p, 1.0)),
            "do_sample": bool(_value("do_sample", self.config.do_sample, True)),
        }

    def _ensure_graphs(
        self,
        branch_batch_size: int,
        guidance_scale: float,
        *,
        depth_bucket_sizes: list[int] | None = None,
    ) -> None:
        if (
            self._frozen_branch_batch_sizes is not None
            and branch_batch_size not in self._frozen_branch_batch_sizes
        ):
            raise RuntimeError(
                "request branch batch size "
                f"{branch_batch_size} is not declared by the frozen warmup config; "
                f"expected one of {sorted(self._frozen_branch_batch_sizes)}"
            )

        backbone_graph = self._backbone_graphs.get(branch_batch_size)
        if backbone_graph is None:
            backbone_graph = BackboneGraph(
                backbone_model=self.model.backbone_model,
                lm_head=self.model.lm_head,
                embed_tokens=self.model.backbone_model.embed_tokens,
                config=self.model.config,
                device=str(self.device),
                dtype=self.dtype,
                max_seq_len=self.config.max_seq_len,
                guidance_scale=guidance_scale,
                batch_size=branch_batch_size,
            )
            if self._fast_backbone_decode:
                backbone_graph.capture()
            else:
                backbone_graph.prepare_eager()
            self._backbone_graphs[branch_batch_size] = backbone_graph
        else:
            backbone_graph.guidance_scale.fill_(guidance_scale)
        self._backbone_graph = backbone_graph
        self._backbone_prefill_graph = self._backbone_prefill_graphs.get(
            branch_batch_size
        )

        if self._depth_decoder_graph is None:
            depth_gen = self.model.depth_decoder.generation_config
            depth_params = self._sampling_params(depth_gen)
            depth_bucket_sizes = depth_bucket_sizes or [1, 2]
            self._depth_decoder_graph = DepthDecoderGraph(
                depth_decoder=self.model.depth_decoder,
                config=self.model.config.depth_decoder_config,
                device=str(self.device),
                dtype=self.dtype,
                guidance_scale=guidance_scale,
                num_codebooks=self.model.config.num_codebooks,
                codec_codebook_size=self._codec_codebook_size,
                fast=self._fast_depth_decoder,
                batch_size=depth_bucket_sizes[0],
                bucket_sizes=depth_bucket_sizes,
                **depth_params,
            )
            if self._fast_depth_decoder:
                self._depth_decoder_graph.capture()
            else:
                self._depth_decoder_graph.prepare_eager()
        else:
            self._depth_decoder_graph.set_guidance_scale(guidance_scale)

    def _codec(self):
        if self._codec_runtime is not None:
            return self._codec_runtime
        from .stream_runtime import MultiRequestStreamRuntime, QwenStreamRuntimeConfig

        if getattr(self.audio_tokenizer, "model", None) is None:
            raise RuntimeError(
                "audio_tokenizer.model is required for fast streaming codec decode"
            )
        try:
            codec_dtype = next(self.audio_tokenizer.model.parameters()).dtype
        except StopIteration:
            codec_dtype = torch.float32
        runtime_config = QwenStreamRuntimeConfig(
            chunk_frames=self._codec_chunk_frames,
            num_lanes=1,
            max_active_reqs=1,
            fast=self._fast_codec,
            device=self.device,
            dtype=codec_dtype,
        )
        self._codec_runtime = MultiRequestStreamRuntime(
            self.audio_tokenizer, runtime_config
        )
        return self._codec_runtime

    def _merge_branch(
        self,
        *,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        text_ids_mask: torch.Tensor,
        text_ids_len: torch.Tensor,
        input_values: torch.Tensor | None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        merged = self.model._merge_input_ids_with_input_values(
            input_ids=input_ids,
            attention_mask=attention_mask,
            text_ids_mask=text_ids_mask,
            text_ids_len=text_ids_len,
            input_values=input_values,
        )
        return merged["inputs_embeds"], attention_mask

    def _merge_cfg_branches(
        self, inputs: dict[str, Any]
    ) -> tuple[torch.Tensor, torch.Tensor] | None:
        """Merge cond/uncond together so their text segments use one batched graph."""
        cond_values = inputs.get("input_values")
        uncond_values = inputs.get("cfg_negative_input_values")
        if (cond_values is None) != (uncond_values is None):
            return None
        if cond_values is not None and tuple(cond_values.shape[1:]) != tuple(
            uncond_values.shape[1:]
        ):
            return None

        cond_ids = inputs["input_ids"]
        uncond_ids = inputs["cfg_negative_prompt_ids"]
        if cond_ids.shape[0] != 1 or uncond_ids.shape[0] != 1:
            return None
        max_len = max(cond_ids.shape[1], uncond_ids.shape[1])
        input_ids = torch.cat(
            [
                _left_pad_tensor(cond_ids, max_len, 0),
                _left_pad_tensor(uncond_ids, max_len, 0),
            ],
            dim=0,
        )
        attention_mask = torch.cat(
            [
                _left_pad_tensor(inputs["attention_mask"], max_len, 0),
                _left_pad_tensor(
                    inputs["cfg_negative_prompt_attention_mask"], max_len, 0
                ),
            ],
            dim=0,
        )
        text_ids_mask = torch.cat(
            [
                _left_pad_tensor(inputs["text_ids_mask"], max_len, False),
                _left_pad_tensor(inputs["cfg_negative_text_ids_mask"], max_len, False),
            ],
            dim=0,
        )
        text_ids_len = torch.cat(
            [inputs["text_ids_len"], inputs["cfg_negative_text_ids_len"]], dim=0
        )
        input_values = (
            None
            if cond_values is None
            else torch.cat([cond_values, uncond_values], dim=0)
        )
        merged = self.model._merge_input_ids_with_input_values(
            input_ids=input_ids,
            attention_mask=attention_mask,
            text_ids_mask=text_ids_mask,
            text_ids_len=text_ids_len,
            input_values=input_values,
        )
        return merged["inputs_embeds"].contiguous(), attention_mask.contiguous()

    def _build_branch_batch(self, inputs: dict[str, Any]) -> _BranchBatch:
        cfg = select_fast_cfg(inputs)
        if cfg.use_negative_as_main:
            embeds, mask = self._merge_branch(
                input_ids=inputs["cfg_negative_prompt_ids"],
                attention_mask=inputs["cfg_negative_prompt_attention_mask"],
                text_ids_mask=inputs["cfg_negative_text_ids_mask"],
                text_ids_len=inputs["cfg_negative_text_ids_len"],
                input_values=inputs.get("cfg_negative_input_values"),
            )
            return _BranchBatch(embeds.contiguous(), mask.contiguous(), 1, cfg)

        if cfg.mode == "no_cfg":
            cond_embeds, cond_mask = self._merge_branch(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                text_ids_mask=inputs["text_ids_mask"],
                text_ids_len=inputs["text_ids_len"],
                input_values=inputs.get("input_values"),
            )
            return _BranchBatch(
                cond_embeds.contiguous(), cond_mask.contiguous(), 1, cfg
            )

        joint = self._merge_cfg_branches(inputs) if self._fast_text_encoder else None
        if joint is not None:
            inputs_embeds, attention_mask = joint
            return _BranchBatch(inputs_embeds, attention_mask, 2, cfg)

        cond_embeds, cond_mask = self._merge_branch(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            text_ids_mask=inputs["text_ids_mask"],
            text_ids_len=inputs["text_ids_len"],
            input_values=inputs.get("input_values"),
        )
        uncond_embeds, uncond_mask = self._merge_branch(
            input_ids=inputs["cfg_negative_prompt_ids"],
            attention_mask=inputs["cfg_negative_prompt_attention_mask"],
            text_ids_mask=inputs["cfg_negative_text_ids_mask"],
            text_ids_len=inputs["cfg_negative_text_ids_len"],
            input_values=inputs.get("cfg_negative_input_values"),
        )
        max_len = max(cond_embeds.shape[1], uncond_embeds.shape[1])
        inputs_embeds = torch.cat(
            [
                _left_pad_tensor(cond_embeds, max_len, 0),
                _left_pad_tensor(uncond_embeds, max_len, 0),
            ],
            dim=0,
        ).contiguous()
        attention_mask = torch.cat(
            [
                _left_pad_tensor(cond_mask, max_len, 0),
                _left_pad_tensor(uncond_mask, max_len, 0),
            ],
            dim=0,
        ).contiguous()
        return _BranchBatch(inputs_embeds, attention_mask, 2, cfg)

    def _decode_codec_frames(
        self,
        *,
        frames: list[torch.Tensor],
        request_id: str,
        reset: bool,
        is_final: bool,
        timing: dict[str, float | int | bool],
    ) -> FastStreamingChunk:
        frame_tensor = torch.stack(frames).to(self.device, dtype=torch.long)
        codes = frame_tensor.transpose(0, 1).unsqueeze(0).contiguous()
        codec_started = time.perf_counter()
        audio = self._codec().decode_request_chunk(request_id, codes, reset=reset)
        codec_launch_ms = (time.perf_counter() - codec_started) * 1000.0
        d2h_started = time.perf_counter()
        audio_np = _extract_audio_np(audio)
        d2h_ms = (time.perf_counter() - d2h_started) * 1000.0
        timing = {
            **timing,
            "codec_launch_ms": codec_launch_ms,
            "audio_d2h_ms": d2h_ms,
        }
        return FastStreamingChunk(
            audio=audio_np,
            sample_rate=self.sample_rate,
            codec_frames=len(frames),
            is_final=is_final,
            timing=timing,
        )

    @property
    def fast_enabled(self) -> bool:
        return any(
            (
                self._fast_text_encoder,
                self._fast_backbone_prefill,
                self._fast_backbone_decode,
                self._fast_depth_decoder,
                self._fast_codec,
            )
        )

    @property
    def codec_chunk_frames(self) -> int:
        return self._codec_chunk_frames

    @torch.inference_mode()
    def warmup_from_profile(
        self,
        profile: FastStreamingWarmupProfile,
        *,
        manifest_path: str | Path | None = None,
    ) -> dict[str, Any]:
        """Deterministically create every graph declared by a serving profile."""
        if self._warmup_manifest is not None:
            raise RuntimeError("runtime has already completed profile warmup")
        if self.tokenizer is None:
            raise ValueError(
                "profile warmup requires FastBreezeStreamingRuntime(tokenizer=...)"
            )
        if profile.codec_chunk_frames != self._codec_chunk_frames:
            raise ValueError(
                f"profile codec chunk_frames={profile.codec_chunk_frames} does not match "
                f"runtime chunk_frames={self._codec_chunk_frames}"
            )
        if profile.codec_num_lanes != 1:
            raise ValueError("fast streaming runtime supports exactly one codec lane")
        if any(
            graph.sequence_length > self.config.max_seq_len
            for graph in profile.backbone_prefill_graphs
        ):
            raise ValueError(
                "profile prefill sequence_length exceeds runtime max_seq_len"
            )

        total_started = time.perf_counter()
        stages: dict[str, Any] = {}

        graph_started = time.perf_counter()
        cfg_scale_by_batch = {
            1 if cfg_scale == 1.0 else 2: cfg_scale for cfg_scale in profile.cfg_scales
        }
        for branch_batch_size in profile.backbone_decode_branch_batch_sizes:
            self._ensure_graphs(
                branch_batch_size,
                cfg_scale_by_batch[branch_batch_size],
                depth_bucket_sizes=list(profile.depth_decoder_batch_sizes),
            )
        assert self._depth_decoder_graph is not None
        torch.cuda.synchronize(self.device)
        graph_elapsed_ms = (time.perf_counter() - graph_started) * 1000.0
        stages["backbone_decode"] = {
            "fast": self._fast_backbone_decode,
            "graphs": [
                {"branch_batch_size": batch_size}
                for batch_size in sorted(self._backbone_graphs)
            ],
            "elapsed_ms_with_depth_decoder": graph_elapsed_ms,
        }
        stages["depth_decoder"] = {
            "fast": self._fast_depth_decoder,
            "graphs": [
                {"batch_size": int(batch_size)}
                for batch_size in sorted(self._depth_decoder_graph._bucket_graphs)
            ],
            "elapsed_ms_with_backbone_decode": graph_elapsed_ms,
        }

        sampling_started = time.perf_counter()
        backbone_params = self._sampling_params(self.model.generation_config)
        sampling_logits = torch.zeros(
            1,
            int(self.model.config.vocab_size) + 1,
            dtype=torch.float32,
            device=self.device,
        )
        for _ in range(2):
            sample_logits(
                sampling_logits,
                suppress_tokens=self._reserved_codec_token_ids,
                **backbone_params,
            )
        torch.cuda.synchronize(self.device)
        stages["backbone_decode"]["sampling_warmup_ms"] = (
            time.perf_counter() - sampling_started
        ) * 1000.0

        text_started = time.perf_counter()
        text_graph_keys: tuple[tuple[int, int], ...] = ()
        if self._fast_text_encoder:
            from .text_encoder_graph import TextEncoderGraphCache

            text_cache = getattr(self.model, "_fast_text_encoder_graph_cache", None)
            if text_cache is None:
                text_cache = TextEncoderGraphCache(
                    self.model.text_encoder, token_granularity=32
                )
                self.model._fast_text_encoder_graph_cache = text_cache
            for graph in profile.text_encoder_graphs:
                text_cache.warmup_graph(
                    batch_size=graph.batch_size,
                    token_length=graph.token_length,
                    device=self.device,
                )
            text_graph_keys = text_cache.graph_keys
            if profile.freeze_after_warmup:
                text_cache.freeze()
        torch.cuda.synchronize(self.device)
        stages["text_encoder"] = {
            "fast": self._fast_text_encoder,
            "graphs": [
                {"batch_size": batch_size, "token_length": token_length}
                for batch_size, token_length in text_graph_keys
            ],
            "elapsed_ms": (time.perf_counter() - text_started) * 1000.0,
        }

        prefill_started = time.perf_counter()
        prefill_graph_keys: list[tuple[int, int]] = []
        if self._fast_backbone_prefill:
            for branch_batch_size in profile.backbone_decode_branch_batch_sizes:
                backbone_graph = self._backbone_graphs[branch_batch_size]
                prefill_cache = BackbonePrefillGraphCache(
                    backbone_graph, token_granularity=32
                )
                for graph in profile.backbone_prefill_graphs:
                    if graph.branch_batch_size == branch_batch_size:
                        prefill_cache.warmup_graph(
                            branch_batch_size=graph.branch_batch_size,
                            sequence_length=graph.sequence_length,
                        )
                if profile.freeze_after_warmup:
                    prefill_cache.freeze()
                self._backbone_prefill_graphs[branch_batch_size] = prefill_cache
                prefill_graph_keys.extend(prefill_cache.graph_keys)
            if self._backbone_graph is not None:
                self._backbone_prefill_graph = self._backbone_prefill_graphs.get(
                    self._backbone_graph.batch_size
                )
        torch.cuda.synchronize(self.device)
        stages["backbone_prefill"] = {
            "fast": self._fast_backbone_prefill,
            "graphs": [
                {"branch_batch_size": batch_size, "sequence_length": sequence_length}
                for batch_size, sequence_length in prefill_graph_keys
            ],
            "elapsed_ms": (time.perf_counter() - prefill_started) * 1000.0,
        }

        codec_started = time.perf_counter()
        codec = self._codec()
        codec_request_id = "profile-codec-warmup"
        codec.open_request(codec_request_id, reset=True, is_first_decode=True)
        codec_codes = torch.zeros(
            1,
            int(self.model.config.num_codebooks),
            self._codec_chunk_frames,
            dtype=torch.long,
            device=self.device,
        )
        codec_audio = codec.decode_request_chunk(
            codec_request_id,
            codec_codes,
            reset=True,
        )
        _extract_audio_np(codec_audio)
        codec.close_request(codec_request_id)
        torch.cuda.synchronize(self.device)
        stages["codec"] = {
            "fast": self._fast_codec,
            "graphs": [
                {
                    "num_lanes": len(codec.lanes),
                    "chunk_frames": self._codec_chunk_frames,
                    "captured": all(lane.cuda_graph is not None for lane in codec.lanes)
                    if self._fast_codec
                    else False,
                }
            ],
            "elapsed_ms": (time.perf_counter() - codec_started) * 1000.0,
        }

        if profile.freeze_after_warmup:
            self._frozen_branch_batch_sizes = frozenset(
                profile.backbone_decode_branch_batch_sizes
            )
        self._warmup_profile = profile

        from breeze_infer.templates import get_template, prepare_inputs

        request_spec = profile.warmup_request
        synthetic_results: list[dict[str, Any]] = []
        for cfg_scale in profile.cfg_scales:
            synthetic_started = time.perf_counter()
            request_id = f"profile-first-frame-cfg{cfg_scale:g}"
            torch.manual_seed(request_spec.seed)
            torch.cuda.manual_seed_all(request_spec.seed)
            synthetic_inputs = prepare_inputs(
                self.tokenizer,
                self.audio_tokenizer,
                self.model,
                [
                    {
                        "id": request_id,
                        "text": request_spec.text,
                        "instruction": request_spec.instruction,
                        "speaker": request_spec.speaker,
                    }
                ],
                get_template(request_spec.template),
                guidance_scale=cfg_scale,
                guidance_scale_ref=None,
                guidance_scale_ins=None,
            )
            synthetic_iterator = self.iter_audio_chunks(
                synthetic_inputs, request_id=request_id
            )
            try:
                try:
                    synthetic_chunk = next(synthetic_iterator)
                except StopIteration as exc:
                    raise RuntimeError(
                        "warmup request completed without producing an audio frame"
                    ) from exc
            finally:
                synthetic_iterator.close()
            torch.cuda.synchronize(self.device)
            synthetic_results.append(
                {
                    "template": request_spec.template,
                    "cfg_scale": cfg_scale,
                    "cfg_mode": "no_cfg" if cfg_scale == 1.0 else "single_cfg",
                    "audio_samples": int(synthetic_chunk.audio.size),
                    "ttfa_internal_ms": synthetic_chunk.timing.get("ttfa_internal_ms"),
                    "elapsed_ms": (time.perf_counter() - synthetic_started) * 1000.0,
                }
            )
        stages["synthetic_first_frames"] = synthetic_results

        manifest = {
            "schema_version": 1,
            "status": "ready",
            "profile_source": profile.source,
            "profile": profile.to_dict(),
            "stages": stages,
            "frozen": profile.freeze_after_warmup,
            "total_elapsed_ms": (time.perf_counter() - total_started) * 1000.0,
        }
        self._warmup_manifest = manifest
        if manifest_path is not None:
            path = Path(manifest_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        return manifest

    @torch.inference_mode()
    def iter_audio_chunks(
        self,
        inputs: dict[str, Any],
        *,
        request_id: str | None = None,
        seed: int | None = None,
        token_observer: Callable[[torch.Tensor], None] | None = None,
    ) -> Iterator[FastStreamingChunk]:
        cfg = select_fast_cfg(inputs)
        branch_batch_size = 2 if cfg.mode == "single_cfg" else 1
        self._ensure_graphs(branch_batch_size, cfg.guidance_scale)
        assert self._backbone_graph is not None
        assert self._depth_decoder_graph is not None

        codec = self._codec()
        branch = self._build_branch_batch(inputs)
        request_id = request_id or f"local-{uuid.uuid4().hex}"
        codec.open_request(request_id, reset=True, is_first_decode=True)

        backbone_params = self._sampling_params(self.model.generation_config)
        depth_params = self._sampling_params(self.model.depth_decoder.generation_config)
        chunk_buffer: list[torch.Tensor] = []
        chunk_index = 0
        total_frames = 0
        backbone_token_history = torch.empty(
            self.config.max_new_tokens,
            dtype=torch.long,
            device=self.device,
        )
        # All lazy request setup must precede the reset. In particular, the
        # first request may allocate caches and initialize the streaming codec.
        # A request seed is a sampling contract, so those one-time operations
        # must not be allowed to shift the backbone/depth multinomial streams.
        if seed is not None:
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
        first_decode = True
        t_start = time.perf_counter()
        t_chunk = t_start
        prefill_start_event = None
        prefill_end_event = None
        if self.config.collect_timing:
            prefill_start_event = torch.cuda.Event(enable_timing=True)
            prefill_end_event = torch.cuda.Event(enable_timing=True)
            prefill_start_event.record()

        try:
            attention_mask = branch.attention_mask
            if self._fast_backbone_prefill:
                if self._backbone_prefill_graph is None:
                    self._backbone_prefill_graph = BackbonePrefillGraphCache(
                        self._backbone_graph, token_granularity=32
                    )
                prefill_output = self._backbone_prefill_graph(
                    branch.inputs_embeds, attention_mask
                )
                hidden = prefill_output.hidden_states
                logits = prefill_output.logits
                prefill_len = prefill_output.prefill_len
                generation_attention_mask = prefill_output.attention_mask
            else:
                position_ids = attention_mask.long().cumsum(-1) - 1
                position_ids.masked_fill_(attention_mask == 0, 1)
                prefill_cache = None
                cache_position = None
                backbone_out = self.model.backbone_model(
                    inputs_embeds=branch.inputs_embeds,
                    attention_mask=attention_mask,
                    position_ids=position_ids,
                    past_key_values=prefill_cache,
                    cache_position=cache_position,
                    use_cache=True,
                )
                hidden = backbone_out.last_hidden_state
                logits = self.model.lm_head(hidden[:, -1, :].float()).float()
                prefill_len = self._backbone_graph.prefill_kv(
                    backbone_out.past_key_values
                )
                generation_attention_mask = attention_mask

            if branch.branch_batch_size == 2:
                cond_logits = logits[:1]
                uncond_logits = logits[1:]
                logits = uncond_logits + branch.cfg.guidance_scale * (
                    cond_logits - uncond_logits
                )
            else:
                logits = logits[:1]
            token = sample_logits(
                logits,
                suppress_tokens=self._reserved_codec_token_ids,
                **backbone_params,
            ).view(1)
            self._backbone_graph.set_generation_state(generation_attention_mask)
            if prefill_end_event is not None:
                prefill_end_event.record()

            for step_idx in range(self.config.max_new_tokens):
                if is_backbone_eos_token(token, self.model.config):
                    break

                if prefill_len + step_idx >= self.config.max_seq_len - 1:
                    break

                if branch.branch_batch_size == 2:
                    token_batch = token.repeat(2)
                    depth_hidden = hidden[:, -1, :]
                else:
                    token_batch = token
                    depth_hidden = hidden[:1, -1, :]

                depth_tokens = self._depth_decoder_graph.run(
                    depth_hidden,
                    token_batch,
                    guidance_scale=branch.cfg.guidance_scale,
                    **depth_params,
                )
                frame = torch.cat([token.view(1), depth_tokens[0]], dim=0)
                if token_observer is not None:
                    token_observer(frame)
                if should_decode_codec_frame(frame, self.model.config):
                    chunk_buffer.append(frame.detach())

                # A complete codec frame can be decoded immediately. Emit it
                # before computing the next backbone token so that one full
                # backbone decode step is no longer on the TTFA critical path.
                reached_limit = step_idx == self.config.max_new_tokens - 1
                chunk_ready = len(chunk_buffer) >= self._codec_chunk_frames
                if chunk_ready or reached_limit:
                    if chunk_buffer:
                        decode_started = time.perf_counter()
                        frames = chunk_buffer
                        chunk_buffer = []
                        total_frames += len(frames)
                        timing: dict[str, float | int | bool] = {
                            "chunk_index": chunk_index,
                            "codec_frames": len(frames),
                            "decode_launch_ms": (decode_started - t_chunk) * 1000.0,
                            "total_frames": total_frames,
                            "is_final": reached_limit,
                        }
                        chunk = self._decode_codec_frames(
                            frames=frames,
                            request_id=request_id,
                            reset=first_decode,
                            is_final=reached_limit,
                            timing=timing,
                        )
                        if chunk_index == 0:
                            first_timing = {
                                **chunk.timing,
                                "ttfa_internal_ms": (time.perf_counter() - t_start)
                                * 1000.0,
                            }
                            if (
                                prefill_start_event is not None
                                and prefill_end_event is not None
                            ):
                                first_timing["prefill_gpu_ms"] = (
                                    prefill_start_event.elapsed_time(prefill_end_event)
                                )
                            chunk = FastStreamingChunk(
                                audio=chunk.audio,
                                sample_rate=chunk.sample_rate,
                                codec_frames=chunk.codec_frames,
                                is_final=chunk.is_final,
                                timing=first_timing,
                            )
                        yield chunk
                        first_decode = False
                        chunk_index += 1
                        t_chunk = time.perf_counter()
                    if reached_limit:
                        break

                frame_for_backbone = frame.view(1, 1, -1)
                if branch.branch_batch_size == 2:
                    frame_for_backbone = frame_for_backbone.repeat(2, 1, 1)

                hidden, logits = self._backbone_graph.run(
                    frame_for_backbone, step_idx=step_idx
                )
                logits = logits.float()
                backbone_token_history[step_idx] = token[0]
                token = sample_logits(
                    logits,
                    token_history=backbone_token_history[: step_idx + 1],
                    repetition_penalty=self.config.repetition_penalty,
                    suppress_tokens=self._reserved_codec_token_ids,
                    **backbone_params,
                ).view(1)

                if is_backbone_eos_token(token, self.model.config):
                    break

            if chunk_buffer:
                frames = chunk_buffer
                total_frames += len(frames)
                yield self._decode_codec_frames(
                    frames=frames,
                    request_id=request_id,
                    reset=first_decode,
                    is_final=True,
                    timing={
                        "chunk_index": chunk_index,
                        "codec_frames": len(frames),
                        "decode_launch_ms": (time.perf_counter() - t_chunk) * 1000.0,
                        "total_frames": total_frames,
                        "is_final": True,
                    },
                )
        finally:
            codec.close_request(request_id)
