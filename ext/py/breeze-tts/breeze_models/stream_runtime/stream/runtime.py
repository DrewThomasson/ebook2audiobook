from __future__ import annotations

import logging
import time
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

import torch

from ..core.compat import Qwen3TTSTokenizer
from .kv_cache import StaticShiftKVCache
from .lane import ExecutionLane, _causal_conv_left_cache_len, _tconv_left_cache_len
from .state import (
    ConvStateBlock,
    RequestStatePool,
    RequestStateSlot,
    TransConvStateBlock,
    reset_request_state,
)
from .workspace import (
    ConvWorkspaceBlock,
    TransConvWorkspaceBlock,
    WorkspacePool,
    WorkspaceSlot,
    reset_workspace,
)

logger = logging.getLogger(__name__)


@dataclass
class QwenStreamRuntimeConfig:
    chunk_frames: int = 1
    # Strategy for a residual tail when len(codes) % chunk_frames != 0 and chunk_frames > 1.
    # - "eager": decode the tail one frame at a time on a dedicated eager lane.
    #            This avoids pad contamination at the tail boundary and is the default.
    # - "pad":   keep the existing fixed-shape path by right-padding the tail to chunk_frames,
    #            decoding it on the main lane, then trimming the wav back to the expected length.
    non_integer_chunk_strategy: str = "eager"
    num_lanes: int = 1
    max_active_reqs: int | None = None
    fast: bool = False
    lifecycle_assert_mode: str = "warn"
    tombstone_capacity: int = 1024
    device: torch.device | None = None
    dtype: torch.dtype = torch.float32


@dataclass
class TombstoneEntry:
    reason: str


def _tensor_bytes(tensor: torch.Tensor) -> int:
    return int(tensor.numel() * tensor.element_size())


def _format_bytes(num_bytes: int) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{num_bytes} B"


def _request_state_bytes(slot: RequestStateSlot) -> int:
    total = 0
    for block in slot.conv1d.values():
        total += _tensor_bytes(block.cache_buf)
    for block in slot.tconv1d.values():
        total += _tensor_bytes(block.cache_buf)
    for layer in slot.kv.layers:
        total += _tensor_bytes(layer.k)
        total += _tensor_bytes(layer.v)
    return total


def _workspace_bytes(slot: WorkspaceSlot) -> int:
    total = 0
    for block in slot.conv1d.values():
        total += _tensor_bytes(block.x_buf)
    for block in slot.tconv1d.values():
        total += _tensor_bytes(block.x_buf)
    return total


def _step_lengths(decoder, chunk_frames: int) -> dict[str, int]:
    lengths: dict[str, int] = {}
    cur = int(chunk_frames)
    lengths["pre_conv"] = cur
    for idx, blocks in enumerate(decoder.upsample):
        lengths[f"upsample_{idx}_tconv"] = cur
        stride = int(blocks[0].conv.stride[0])
        cur = cur * stride
        lengths[f"upsample_{idx}_dwconv"] = cur
    lengths["decoder_pre_conv"] = cur
    for idx, block in enumerate(decoder.decoder[1:-2]):
        lengths[f"decoder_block_{idx}_tconv"] = cur
        stride = int(block.block[1].conv.stride[0])
        cur = cur * stride
        for ridx, _unit in enumerate(block.block[2:]):
            lengths[f"decoder_block_{idx}_residual_{ridx}_conv1"] = cur
    lengths["final_conv"] = cur
    return lengths


def build_request_state_slot(
    tokenizer: Qwen3TTSTokenizer,
    chunk_frames: int,
    device: torch.device,
    dtype: torch.dtype,
) -> RequestStateSlot:
    decoder = tokenizer.model.decoder  # type: ignore[union-attr]
    config = decoder.config
    conv1d: dict[str, ConvStateBlock] = {}
    tconv1d: dict[str, TransConvStateBlock] = {}

    def add_conv(name: str, channels: int, left: int):
        conv1d[name] = ConvStateBlock(
            cache_buf=torch.zeros((1, channels, left), device=device, dtype=dtype),
            left_cache_len=left,
        )

    def add_tconv(name: str, channels: int, left: int):
        tconv1d[name] = TransConvStateBlock(
            cache_buf=torch.zeros((1, channels, left), device=device, dtype=dtype),
            left_cache_len=left,
        )

    add_conv(
        "pre_conv", config.codebook_dim, _causal_conv_left_cache_len(decoder.pre_conv)
    )
    for idx, blocks in enumerate(decoder.upsample):
        add_tconv(
            f"upsample_{idx}_tconv",
            blocks[0].conv.in_channels,
            _tconv_left_cache_len(blocks[0]),
        )
        add_conv(
            f"upsample_{idx}_dwconv",
            blocks[1].dwconv.conv.in_channels,
            _causal_conv_left_cache_len(blocks[1].dwconv),
        )
    add_conv(
        "decoder_pre_conv",
        config.latent_dim,
        _causal_conv_left_cache_len(decoder.decoder[0]),
    )
    for idx, block in enumerate(decoder.decoder[1:-2]):
        add_tconv(
            f"decoder_block_{idx}_tconv",
            block.block[1].conv.in_channels,
            _tconv_left_cache_len(block.block[1]),
        )
        for ridx, unit in enumerate(block.block[2:]):
            add_conv(
                f"decoder_block_{idx}_residual_{ridx}_conv1",
                unit.conv1.conv.in_channels,
                _causal_conv_left_cache_len(unit.conv1),
            )
    add_conv(
        "final_conv",
        decoder.decoder[-1].conv.in_channels,
        _causal_conv_left_cache_len(decoder.decoder[-1]),
    )
    kv = StaticShiftKVCache(
        num_layers=config.num_hidden_layers,
        window=config.sliding_window,
        batch=1,
        h_kv=config.num_key_value_heads,
        head_dim=getattr(
            config, "head_dim", config.hidden_size // config.num_attention_heads
        ),
        device=device,
        dtype=dtype,
    )
    return RequestStateSlot(
        req_id=None,
        next_step=0,
        tail_flushed=False,
        conv1d=conv1d,
        tconv1d=tconv1d,
        kv=kv,
    )


def build_workspace_slot(
    tokenizer: Qwen3TTSTokenizer,
    chunk_frames: int,
    device: torch.device,
    dtype: torch.dtype,
) -> WorkspaceSlot:
    decoder = tokenizer.model.decoder  # type: ignore[union-attr]
    step_lengths = _step_lengths(decoder, chunk_frames)
    conv1d: dict[str, ConvWorkspaceBlock] = {}
    tconv1d: dict[str, TransConvWorkspaceBlock] = {}

    def add_conv(name: str, channels: int, left: int):
        conv1d[name] = ConvWorkspaceBlock(
            x_buf=torch.zeros(
                (1, channels, left + step_lengths[name]), device=device, dtype=dtype
            )
        )

    def add_tconv(name: str, channels: int, left: int):
        tconv1d[name] = TransConvWorkspaceBlock(
            x_buf=torch.zeros(
                (1, channels, left + step_lengths[name]), device=device, dtype=dtype
            )
        )

    add_conv(
        "pre_conv",
        decoder.config.codebook_dim,
        _causal_conv_left_cache_len(decoder.pre_conv),
    )
    for idx, blocks in enumerate(decoder.upsample):
        add_tconv(
            f"upsample_{idx}_tconv",
            blocks[0].conv.in_channels,
            _tconv_left_cache_len(blocks[0]),
        )
        add_conv(
            f"upsample_{idx}_dwconv",
            blocks[1].dwconv.conv.in_channels,
            _causal_conv_left_cache_len(blocks[1].dwconv),
        )
    add_conv(
        "decoder_pre_conv",
        decoder.config.latent_dim,
        _causal_conv_left_cache_len(decoder.decoder[0]),
    )
    for idx, block in enumerate(decoder.decoder[1:-2]):
        add_tconv(
            f"decoder_block_{idx}_tconv",
            block.block[1].conv.in_channels,
            _tconv_left_cache_len(block.block[1]),
        )
        for ridx, unit in enumerate(block.block[2:]):
            add_conv(
                f"decoder_block_{idx}_residual_{ridx}_conv1",
                unit.conv1.conv.in_channels,
                _causal_conv_left_cache_len(unit.conv1),
            )
    add_conv(
        "final_conv",
        decoder.decoder[-1].conv.in_channels,
        _causal_conv_left_cache_len(decoder.decoder[-1]),
    )
    return WorkspaceSlot(conv1d=conv1d, tconv1d=tconv1d)


class MultiRequestStreamRuntime:
    def __init__(self, tokenizer: Qwen3TTSTokenizer, config: QwenStreamRuntimeConfig):
        if tokenizer.model is None:
            raise ValueError("Tokenizer model is not loaded.")
        if config.device is None:
            try:
                config.device = next(tokenizer.model.parameters()).device
            except StopIteration:
                config.device = torch.device("cpu")
        self.tokenizer = tokenizer
        self.config = config
        if self.config.lifecycle_assert_mode not in {"off", "warn", "raise"}:
            raise ValueError(
                f"lifecycle_assert_mode must be one of off/warn/raise, got {self.config.lifecycle_assert_mode}"
            )
        if self.config.tombstone_capacity < 0:
            raise ValueError(
                f"tombstone_capacity must be >= 0, got {self.config.tombstone_capacity}"
            )
        if self.config.non_integer_chunk_strategy not in {"eager", "pad"}:
            raise ValueError(
                "non_integer_chunk_strategy must be one of {'eager', 'pad'}, "
                f"got {self.config.non_integer_chunk_strategy!r}"
            )
        if self.config.fast and (
            self.config.num_lanes != 1 or self.config.max_active_reqs not in {None, 1}
        ):
            raise ValueError("fast codec requires num_lanes=1 and max_active_reqs<=1")
        if (
            self.config.fast
            and self.config.device is not None
            and self.config.device.type == "cuda"
        ):
            torch.backends.cudnn.benchmark = True
        self._compile_snakes()
        self._req_tombstones: OrderedDict[str, TombstoneEntry] = OrderedDict()
        self._enforce_compile_attention_backend()
        self.request_pool = RequestStatePool(
            create_slot=lambda: build_request_state_slot(
                self.tokenizer,
                self.config.chunk_frames,
                self.config.device,
                self.config.dtype,
            ),
            reset_slot=reset_request_state,
            max_active_reqs=self.config.max_active_reqs,
            on_evict=self._on_request_evicted,
        )
        self.workspace_pool = WorkspacePool(
            create_slot=lambda: build_workspace_slot(
                self.tokenizer,
                self.config.chunk_frames,
                self.config.device,
                self.config.dtype,
            ),
            reset_slot=reset_workspace,
            size=self.config.num_lanes,
        )
        self.lanes: list[ExecutionLane] = []
        self.tail_eager_lanes: list[ExecutionLane] = []
        self.req_to_lane: dict[str, int] = {}
        self._single_lane_req_id: str | None = None
        for lane_id in range(self.config.num_lanes):
            workspace_idx, workspace_slot = self.workspace_pool.acquire()
            if workspace_idx != lane_id:
                raise RuntimeError(
                    "Workspace pool returned unexpected lane slot order."
                )
            hot_state = build_request_state_slot(
                self.tokenizer,
                self.config.chunk_frames,
                self.config.device,
                self.config.dtype,
            )
            self.lanes.append(
                ExecutionLane(
                    lane_id=lane_id,
                    tokenizer=self.tokenizer,
                    chunk_frames=self.config.chunk_frames,
                    hot_state=hot_state,
                    workspace=workspace_slot,
                    fast=self.config.fast,
                )
            )
            if (
                self.config.chunk_frames > 1
                and self.config.non_integer_chunk_strategy == "eager"
            ):
                eager_tail_hot_state = build_request_state_slot(
                    self.tokenizer,
                    chunk_frames=1,
                    device=self.config.device,
                    dtype=self.config.dtype,
                )
                eager_tail_workspace = build_workspace_slot(
                    self.tokenizer,
                    chunk_frames=1,
                    device=self.config.device,
                    dtype=self.config.dtype,
                )
                # Residual tails are rare and only happen at request shutdown. Keep this fallback
                # eager so the default path avoids padding a future code into the tail boundary.
                self.tail_eager_lanes.append(
                    ExecutionLane(
                        lane_id=lane_id,
                        tokenizer=self.tokenizer,
                        chunk_frames=1,
                        hot_state=eager_tail_hot_state,
                        workspace=eager_tail_workspace,
                        fast=False,
                    )
                )
        self.samples_per_code = self._validate_and_get_samples_per_code()
        self._log_runtime_config()
        self._maybe_warmup_fast_codec()

    def _validate_and_get_samples_per_code(self) -> int:
        theoretical_chunk_out = _step_lengths(
            self.tokenizer.model.decoder, self.config.chunk_frames
        )["final_conv"]  # type: ignore[union-attr]
        if theoretical_chunk_out % self.config.chunk_frames != 0:
            logger.error(
                "breeze_codec invalid chunk->wav ratio: theoretical_chunk_out=%d chunk_frames=%d is not divisible",
                theoretical_chunk_out,
                self.config.chunk_frames,
            )
        theoretical_spc = theoretical_chunk_out // self.config.chunk_frames
        num_quantizers = int(self.tokenizer.model.decoder.config.num_quantizers)  # type: ignore[union-attr]
        dummy_codes = torch.zeros(
            (1, num_quantizers, self.config.chunk_frames),
            device=self.config.device,
            dtype=torch.long,
        )
        with torch.inference_mode():
            observed = self.tokenizer.model.decoder(dummy_codes)  # type: ignore[union-attr]
        observed_chunk_out = int(observed.shape[-1])
        if observed_chunk_out % self.config.chunk_frames != 0:
            logger.error(
                "breeze_codec observed non-integer chunk->wav ratio: observed_chunk_out=%d chunk_frames=%d",
                observed_chunk_out,
                self.config.chunk_frames,
            )
        observed_spc = observed_chunk_out // self.config.chunk_frames
        if observed_spc != theoretical_spc:
            logger.error(
                "breeze_codec chunk->wav ratio mismatch: theoretical=%d observed=%d",
                theoretical_spc,
                observed_spc,
            )
        else:
            logger.info(
                "breeze_codec chunk->wav ratio verified: chunk_frames=%d chunk_output=%d samples_per_code=%d",
                self.config.chunk_frames,
                observed_chunk_out,
                observed_spc,
            )
        return int(observed_spc)

    def _compile_snakes(self) -> None:
        if not self.config.fast:
            return
        torch._dynamo.config.recompile_limit = max(
            int(torch._dynamo.config.recompile_limit), 64
        )
        torch._dynamo.config.accumulated_recompile_limit = max(
            int(torch._dynamo.config.accumulated_recompile_limit), 256
        )
        compiled = 0
        for module in self.tokenizer.model.decoder.modules():
            if module.__class__.__name__ != "SnakeBeta":
                continue
            module.forward = torch.compile(
                module.forward,
                mode="max-autotune-no-cudagraphs",
                fullgraph=True,
                dynamic=True,
            )
            compiled += 1
        logger.info("breeze_codec compiled %d SnakeBeta modules", compiled)

    def _enforce_compile_attention_backend(self) -> None:
        if not self.config.fast:
            return
        decoder = self.tokenizer.model.decoder  # type: ignore[union-attr]
        pre_transformer = getattr(decoder, "pre_transformer", None)
        if pre_transformer is None or not hasattr(pre_transformer, "config"):
            return
        current_impl = getattr(pre_transformer.config, "_attn_implementation", None)
        if current_impl != "eager":
            logger.warning(
                "breeze_codec forcing pre_transformer attention backend to eager for fast codec. previous=%s",
                current_impl,
            )
            pre_transformer.config._attn_implementation = "eager"
        else:
            logger.info(
                "breeze_codec pre_transformer attention backend already eager for fast codec."
            )

    def _log_runtime_config(self) -> None:
        sample_request_state = build_request_state_slot(
            self.tokenizer,
            self.config.chunk_frames,
            self.config.device,
            self.config.dtype,
        )
        sample_workspace = build_workspace_slot(
            self.tokenizer,
            self.config.chunk_frames,
            self.config.device,
            self.config.dtype,
        )
        current_impl = getattr(
            self.tokenizer.model.decoder.pre_transformer.config,
            "_attn_implementation",
            "unknown",
        )  # type: ignore[union-attr]
        logger.info(
            "breeze_codec runtime init: chunk_frames=%d num_lanes=%d device=%s dtype=%s fast=%s attn_impl=%s non_integer_chunk_strategy=%s lifecycle_assert_mode=%s tombstone_capacity=%d max_active_reqs=%s",
            self.config.chunk_frames,
            self.config.num_lanes,
            self.config.device,
            self.config.dtype,
            self.config.fast,
            current_impl,
            self.config.non_integer_chunk_strategy,
            self.config.lifecycle_assert_mode,
            self.config.tombstone_capacity,
            self.config.max_active_reqs,
        )
        logger.info(
            "breeze_codec memory: per_request_state=%s per_workspace=%s total_request_capacity=%s total_workspace_capacity=%s samples_per_code=%s",
            _format_bytes(_request_state_bytes(sample_request_state)),
            _format_bytes(_workspace_bytes(sample_workspace)),
            _format_bytes(
                _request_state_bytes(sample_request_state)
                * (self.config.max_active_reqs or 1)
            ),
            _format_bytes(_workspace_bytes(sample_workspace) * self.config.num_lanes),
            self.samples_per_code,
        )

    def _sync_device(self) -> None:
        if self.config.device is not None and self.config.device.type == "cuda":
            torch.cuda.synchronize(self.config.device)

    def _handle_lifecycle_assert(self, message: str) -> None:
        mode = self.config.lifecycle_assert_mode
        if mode == "off":
            return
        if mode == "warn":
            logger.warning(message)
            return
        raise RuntimeError(message)

    def _record_tombstone(self, req_id: str, reason: str) -> None:
        if self.config.tombstone_capacity == 0:
            return
        self._req_tombstones.pop(req_id, None)
        self._req_tombstones[req_id] = TombstoneEntry(reason=reason)
        while len(self._req_tombstones) > self.config.tombstone_capacity:
            self._req_tombstones.popitem(last=False)

    def _clear_tombstone(self, req_id: str) -> None:
        self._req_tombstones.pop(req_id, None)

    def _on_request_evicted(self, req_id: str) -> None:
        self.req_to_lane.pop(req_id, None)
        if self._single_lane_req_id == req_id:
            self._single_lane_req_id = None
        self._record_tombstone(req_id, "evicted_lru")

    def _maybe_warmup_fast_codec(self) -> None:
        if not self.config.fast:
            return
        self._sync_device()
        t0 = time.perf_counter()
        with torch.inference_mode():
            for lane in self.lanes:
                lane.reset_hot_state()
                lane.warmup_cuda_graph(warmup_rounds=2)
                lane.reset_hot_state()
        self._sync_device()
        logger.info(
            "breeze_codec fast codec warmup done: elapsed_ms=%.3f",
            (time.perf_counter() - t0) * 1000.0,
        )

    def create_request(self, req_id: str, reset: bool = True) -> RequestStateSlot:
        slot = self.request_pool.get(req_id)
        if reset:
            reset_request_state(slot)
            slot.req_id = req_id
        elif slot.req_id is None:
            slot.req_id = req_id
        return slot

    def reset_request(self, req_id: str) -> RequestStateSlot:
        return self.create_request(req_id, reset=True)

    def release_request(self, req_id: str) -> None:
        was_active = req_id in self.request_pool.active_req_ids()
        self.req_to_lane.pop(req_id, None)
        if self._single_lane_req_id == req_id:
            self._single_lane_req_id = None
        self.request_pool.pop(req_id)
        if was_active:
            self._record_tombstone(req_id, "closed")

    # Public request-centric API
    def open_request(
        self, req_id: str, reset: bool = True, is_first_decode: bool | None = None
    ) -> RequestStateSlot:
        is_active = req_id in self.request_pool.active_req_ids()
        tombstone = self._req_tombstones.get(req_id)
        if is_first_decode is True and is_active:
            self._handle_lifecycle_assert(
                f"open_request received is_first_decode=True for an already active request: req_id={req_id}"
            )
        if is_first_decode is False and not is_active:
            reason = tombstone.reason if tombstone is not None else "missing"
            self._handle_lifecycle_assert(
                f"open_request received is_first_decode=False for a non-active request: req_id={req_id} tombstone_reason={reason}"
            )
        self._clear_tombstone(req_id)
        return self.create_request(req_id=req_id, reset=reset)

    def close_request(self, req_id: str) -> None:
        self.release_request(req_id)

    def _select_lane(self, req_id: str) -> ExecutionLane:
        lane_idx = self.req_to_lane.get(req_id)
        if lane_idx is None:
            lane_idx = len(self.req_to_lane) % self.config.num_lanes
            self.req_to_lane[req_id] = lane_idx
        return self.lanes[lane_idx]

    def _select_tail_eager_lane(self, req_id: str) -> ExecutionLane:
        lane_idx = self.req_to_lane.get(req_id)
        if lane_idx is None:
            raise RuntimeError(
                f"tail eager lane requested before main lane selection: req_id={req_id}"
            )
        return self.tail_eager_lanes[lane_idx]

    def _normalize_codes(self, codes_chunk: torch.Tensor) -> torch.Tensor:
        if codes_chunk.ndim != 3:
            raise ValueError(
                f"Expected codes chunk shape [B, Q, T], got {tuple(codes_chunk.shape)}"
            )
        if codes_chunk.shape[0] != 1:
            raise ValueError(
                f"Only batch_size=1 is supported, got {codes_chunk.shape[0]}"
            )
        if codes_chunk.device != self.config.device:
            codes_chunk = codes_chunk.to(self.config.device)
        if codes_chunk.dtype != torch.long:
            codes_chunk = codes_chunk.to(torch.long)
        return codes_chunk.contiguous()

    def decode_request_chunk(
        self, req_id: str, codes_chunk: torch.Tensor, reset: bool = False
    ) -> torch.Tensor:
        state = self.create_request(req_id, reset=reset)
        codes_chunk = self._normalize_codes(codes_chunk)
        if codes_chunk.shape[-1] == 0:
            return torch.zeros(
                (1, 1, 0), device=self.config.device, dtype=self.config.dtype
            )
        if state.tail_flushed:
            logger.error(
                "decode() called after residual tail flush; request must be reset or closed before reuse. req_id=%s",
                req_id,
            )
            return torch.zeros(
                (1, 1, 0), device=self.config.device, dtype=self.config.dtype
            )
        lane = self._select_lane(req_id)
        self.request_pool.pin(req_id)
        try:
            sticky_lane = self.config.fast
            if reset or not sticky_lane or self._single_lane_req_id != req_id:
                lane.load_request_state(state)
                if sticky_lane:
                    self._single_lane_req_id = req_id
            outs = []
            state_stored = False
            with torch.inference_mode():
                full_len = (
                    codes_chunk.shape[-1] // self.config.chunk_frames
                ) * self.config.chunk_frames
                for offset in range(0, full_len, self.config.chunk_frames):
                    step_codes = codes_chunk[
                        ..., offset : offset + self.config.chunk_frames
                    ]
                    outs.append(lane.run_step(step_codes, state.next_step).clone())
                    state.next_step += int(step_codes.shape[-1])
                    lane.binding.request_slot.next_step = state.next_step
                tail = codes_chunk.shape[-1] - full_len
                if tail > 0:
                    tail_codes = codes_chunk[..., full_len:]
                    if self.config.non_integer_chunk_strategy == "eager":
                        # Persist the fixed-chunk lane state first, then finish the residual tail
                        # on a dedicated eager chunk=1 lane. This keeps the default strategy free
                        # of future-code padding at the tail boundary.
                        lane.store_request_state(state)
                        state_stored = True
                        tail_lane = self._select_tail_eager_lane(req_id)
                        tail_lane.load_request_state(state)
                        for offset in range(tail):
                            step_codes = tail_codes[..., offset : offset + 1]
                            outs.append(
                                tail_lane.run_step(step_codes, state.next_step).clone()
                            )
                            state.next_step += 1
                            tail_lane.binding.request_slot.next_step = state.next_step
                        state.tail_flushed = True
                        tail_lane.binding.request_slot.tail_flushed = True
                        tail_lane.store_request_state(state)
                    else:
                        pad = torch.zeros(
                            (
                                tail_codes.shape[0],
                                tail_codes.shape[1],
                                self.config.chunk_frames - tail,
                            ),
                            device=tail_codes.device,
                            dtype=tail_codes.dtype,
                        )
                        padded = torch.cat([tail_codes, pad], dim=-1)
                        padded_wav = lane.run_step(padded, state.next_step).clone()
                        trim_len = int(tail * self.samples_per_code)
                        outs.append(padded_wav[..., :trim_len])
                        state.next_step += tail
                        state.tail_flushed = True
                        lane.binding.request_slot.next_step = state.next_step
                        lane.binding.request_slot.tail_flushed = True
                    logger.warning(
                        "Residual tail decode detected; request must be reset or closed after this call. req_id=%s tail_frames=%d strategy=%s",
                        req_id,
                        tail,
                        self.config.non_integer_chunk_strategy,
                    )
            if not state_stored and not sticky_lane:
                lane.store_request_state(state)
            if not outs:
                return torch.zeros(
                    (1, 1, 0), device=self.config.device, dtype=self.config.dtype
                )
            return torch.cat(outs, dim=-1)
        finally:
            self.request_pool.unpin(req_id)

    def decode_request_sequence(
        self, req_id: str, codes: torch.Tensor, reset: bool = True
    ) -> torch.Tensor:
        return self.decode_request_chunk(req_id=req_id, codes_chunk=codes, reset=reset)

    def get_request_step(self, req_id: str) -> int:
        slot = self.request_pool.get(req_id)
        return int(slot.next_step)

    def decode(
        self, req_id: str, codes_chunk: torch.Tensor, reset: bool = False
    ) -> torch.Tensor:
        return self.decode_request_chunk(
            req_id=req_id, codes_chunk=codes_chunk, reset=reset
        )

    def decode_sequence(
        self, req_id: str, codes: torch.Tensor, reset: bool = True
    ) -> torch.Tensor:
        return self.decode_request_sequence(req_id=req_id, codes=codes, reset=reset)

    def get_step(self, req_id: str) -> int:
        return self.get_request_step(req_id)


def load_tokenizer(model_path: str | Path) -> Qwen3TTSTokenizer:
    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"model path not found: {model_path}")
    tok = Qwen3TTSTokenizer.from_pretrained(
        str(model_path),
        torch_dtype=torch.float32,
        load_feature_extractor=False,
    )
    if tok.model is None:
        raise RuntimeError("Tokenizer model failed to load.")
    tok.model.eval()
    return tok
