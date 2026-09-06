from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn

from ..core.compat import (
    Qwen3TTSTokenizer,
    Qwen3TTSTokenizerV2CausalConvNet,
    Qwen3TTSTokenizerV2CausalTransConvNet,
    Qwen3TTSTokenizerV2ConvNeXtBlock,
    Qwen3TTSTokenizerV2Decoder,
    Qwen3TTSTokenizerV2DecoderDecoderBlock,
    Qwen3TTSTokenizerV2DecoderDecoderResidualUnit,
)
from .kv_cache import StaticShiftKVCache, make_fixed_attention_mask
from .state import ConvStateBlock, RequestStateSlot, TransConvStateBlock
from .workspace import ConvWorkspaceBlock, TransConvWorkspaceBlock, WorkspaceSlot


def _causal_conv_left_cache_len(conv: Qwen3TTSTokenizerV2CausalConvNet) -> int:
    return int(conv.padding)


def _tconv_left_cache_len(conv: Qwen3TTSTokenizerV2CausalTransConvNet) -> int:
    kernel = int(conv.conv.kernel_size[0])
    stride = int(conv.conv.stride[0])
    return int((kernel - 1) // stride)


def _cg_mark() -> None:
    if hasattr(torch, "compiler") and hasattr(
        torch.compiler, "cudagraph_mark_step_begin"
    ):
        torch.compiler.cudagraph_mark_step_begin()


def _ensure_canonical_ncl(x: torch.Tensor) -> torch.Tensor:
    """Materialize canonical contiguous NCL strides before compiled convolutions."""
    x = x.contiguous()
    if x.ndim != 3 or (x.stride(-1) == 1 and x.stride(-2) == x.shape[-1]):
        return x
    y = torch.empty_like(x, memory_format=torch.contiguous_format)
    y.copy_(x)
    return y


@dataclass
class LaneBinding:
    request_slot: RequestStateSlot
    workspace_slot: WorkspaceSlot


class StaticCachedQwenCausalConv1dV2(nn.Module):
    def __init__(
        self, name: str, conv: Qwen3TTSTokenizerV2CausalConvNet, left_cache_len: int
    ):
        super().__init__()
        self.name = name
        self.conv = conv
        self.left_cache_len = int(left_cache_len)

    def forward(
        self,
        x: torch.Tensor,
        state: dict[str, ConvStateBlock],
        workspace: dict[str, ConvWorkspaceBlock],
    ) -> torch.Tensor:
        x = _ensure_canonical_ncl(x)
        if self.left_cache_len <= 0:
            return self.conv(x)
        s = state[self.name]
        w = workspace[self.name]
        if not torch._dynamo.is_compiling():
            if s.cache_buf.shape[-1] != self.left_cache_len:
                raise ValueError(f"{self.name} cache length mismatch.")
            if w.x_buf.shape[-1] != self.left_cache_len + x.shape[-1]:
                raise ValueError(f"{self.name} x_buf length mismatch.")
        w.x_buf[..., : self.left_cache_len].copy_(s.cache_buf)
        w.x_buf[..., self.left_cache_len :].copy_(x)
        conv_input = _ensure_canonical_ncl(w.x_buf)
        y = self.conv(conv_input)
        s.cache_buf.copy_(conv_input[..., -self.left_cache_len :])
        return y[..., -x.shape[-1] :]


class StaticCachedQwenTransposedConv1dV2(nn.Module):
    def __init__(
        self,
        name: str,
        conv: Qwen3TTSTokenizerV2CausalTransConvNet,
        left_cache_len: int,
    ):
        super().__init__()
        self.name = name
        self.conv = conv
        self.left_cache_len = int(left_cache_len)

    def forward(
        self,
        x: torch.Tensor,
        state: dict[str, TransConvStateBlock],
        workspace: dict[str, TransConvWorkspaceBlock],
    ) -> torch.Tensor:
        x = _ensure_canonical_ncl(x)
        if self.left_cache_len <= 0:
            return self.conv(x)
        s = state[self.name]
        w = workspace[self.name]
        if not torch._dynamo.is_compiling():
            if s.cache_buf.shape[-1] != self.left_cache_len:
                raise ValueError(f"{self.name} cache length mismatch.")
            if w.x_buf.shape[-1] != self.left_cache_len + x.shape[-1]:
                raise ValueError(f"{self.name} x_buf length mismatch.")
        w.x_buf[..., : self.left_cache_len].copy_(s.cache_buf)
        w.x_buf[..., self.left_cache_len :].copy_(x)
        conv_input = _ensure_canonical_ncl(w.x_buf)
        y = self.conv(conv_input)
        s.cache_buf.copy_(conv_input[..., -self.left_cache_len :])
        stride = int(self.conv.conv.stride[0])
        prefix = self.left_cache_len * stride
        new_len = x.shape[-1] * stride
        return y[..., prefix : prefix + new_len]


class StaticCachedConvNeXtBlockV2(nn.Module):
    def __init__(self, name: str, block: Qwen3TTSTokenizerV2ConvNeXtBlock):
        super().__init__()
        self.block = block
        self.dwconv = StaticCachedQwenCausalConv1dV2(
            name=name,
            conv=block.dwconv,
            left_cache_len=_causal_conv_left_cache_len(block.dwconv),
        )

    def forward(
        self, hidden_states: torch.Tensor, binding: LaneBinding
    ) -> torch.Tensor:
        residual = hidden_states
        hidden_states = self.dwconv(
            hidden_states, binding.request_slot.conv1d, binding.workspace_slot.conv1d
        )
        hidden_states = hidden_states.permute(0, 2, 1).contiguous()
        hidden_states = self.block.norm(hidden_states)
        hidden_states = self.block.pwconv1(hidden_states)
        hidden_states = self.block.act(hidden_states)
        hidden_states = self.block.pwconv2(hidden_states)
        hidden_states = self.block.gamma * hidden_states
        hidden_states = hidden_states.permute(0, 2, 1).contiguous()
        return residual + hidden_states


class StaticCachedDecoderResidualUnitV2(nn.Module):
    def __init__(self, name: str, unit: Qwen3TTSTokenizerV2DecoderDecoderResidualUnit):
        super().__init__()
        self.unit = unit
        self.conv1 = StaticCachedQwenCausalConv1dV2(
            name=name,
            conv=unit.conv1,
            left_cache_len=_causal_conv_left_cache_len(unit.conv1),
        )

    def forward(self, hidden_state: torch.Tensor, binding: LaneBinding) -> torch.Tensor:
        residual = hidden_state.contiguous()
        hidden_state = self.unit.act1(hidden_state).contiguous()
        hidden_state = self.conv1(
            hidden_state, binding.request_slot.conv1d, binding.workspace_slot.conv1d
        )
        hidden_state = self.unit.act2(hidden_state).contiguous()
        hidden_state = self.unit.conv2(_ensure_canonical_ncl(hidden_state))
        return hidden_state + residual


class StaticCachedDecoderBlockV2(nn.Module):
    def __init__(self, name: str, block: Qwen3TTSTokenizerV2DecoderDecoderBlock):
        super().__init__()
        self.block = block
        self.tconv = StaticCachedQwenTransposedConv1dV2(
            name=f"{name}_tconv",
            conv=block.block[1],
            left_cache_len=_tconv_left_cache_len(block.block[1]),
        )
        self.residual_units = nn.ModuleList(
            [
                StaticCachedDecoderResidualUnitV2(f"{name}_residual_{idx}_conv1", unit)
                for idx, unit in enumerate(block.block[2:])
            ]
        )

    def forward(self, hidden: torch.Tensor, binding: LaneBinding) -> torch.Tensor:
        hidden = self.block.block[0](hidden).contiguous()
        hidden = self.tconv(
            hidden, binding.request_slot.tconv1d, binding.workspace_slot.tconv1d
        )
        for unit in self.residual_units:
            hidden = unit(hidden, binding)
        return hidden


def _copy_conv_state(
    dst: dict[str, ConvStateBlock], src: dict[str, ConvStateBlock]
) -> None:
    for name, block in dst.items():
        block.cache_buf.copy_(src[name].cache_buf)


def _copy_tconv_state(
    dst: dict[str, TransConvStateBlock], src: dict[str, TransConvStateBlock]
) -> None:
    for name, block in dst.items():
        block.cache_buf.copy_(src[name].cache_buf)


def _copy_kv_state(dst: StaticShiftKVCache, src: StaticShiftKVCache) -> None:
    for dst_layer, src_layer in zip(dst.layers, src.layers):
        dst_layer.k.copy_(src_layer.k)
        dst_layer.v.copy_(src_layer.v)


def _reset_request_state_tensors(slot: RequestStateSlot) -> None:
    for block in slot.conv1d.values():
        block.cache_buf.zero_()
    for block in slot.tconv1d.values():
        block.cache_buf.zero_()
    for layer in slot.kv.layers:
        layer.k.zero_()
        layer.v.zero_()


class _LaneCore(nn.Module):
    def __init__(
        self,
        decoder: Qwen3TTSTokenizerV2Decoder,
        chunk_frames: int,
        binding: LaneBinding,
    ):
        super().__init__()
        self.__dict__["decoder_ref"] = decoder
        self.config = decoder.config
        self.chunk_frames = int(chunk_frames)
        self.binding = binding
        self.pre_conv = StaticCachedQwenCausalConv1dV2(
            "pre_conv",
            decoder.pre_conv,
            left_cache_len=_causal_conv_left_cache_len(decoder.pre_conv),
        )
        self.upsample = nn.ModuleList()
        for idx, blocks in enumerate(decoder.upsample):
            self.upsample.append(
                nn.ModuleList(
                    [
                        StaticCachedQwenTransposedConv1dV2(
                            f"upsample_{idx}_tconv",
                            blocks[0],
                            left_cache_len=_tconv_left_cache_len(blocks[0]),
                        ),
                        StaticCachedConvNeXtBlockV2(
                            f"upsample_{idx}_dwconv", blocks[1]
                        ),
                    ]
                )
            )
        self.decoder_pre_conv = StaticCachedQwenCausalConv1dV2(
            "decoder_pre_conv",
            decoder.decoder[0],
            left_cache_len=_causal_conv_left_cache_len(decoder.decoder[0]),
        )
        self.decoder_blocks = nn.ModuleList(
            [
                StaticCachedDecoderBlockV2(f"decoder_block_{idx}", block)
                for idx, block in enumerate(decoder.decoder[1:-2])
            ]
        )
        self.decoder_snake = decoder.decoder[-2]
        self.final_conv = StaticCachedQwenCausalConv1dV2(
            "final_conv",
            decoder.decoder[-1],
            left_cache_len=_causal_conv_left_cache_len(decoder.decoder[-1]),
        )
        self.pre_transformer = decoder.pre_transformer
        self.quantizer = decoder.quantizer

    def forward(
        self, codes: torch.Tensor, cache_position: torch.Tensor
    ) -> torch.Tensor:
        binding = self.binding
        hidden = self.quantizer.decode(codes)
        hidden = (
            self.pre_conv(
                hidden, binding.request_slot.conv1d, binding.workspace_slot.conv1d
            )
            .transpose(1, 2)
            .contiguous()
        )
        attn_mask = make_fixed_attention_mask(
            batch=hidden.shape[0],
            window=self.config.sliding_window,
            cache_position=cache_position,
            device=hidden.device,
            dtype=hidden.dtype,
        )
        hidden = self.pre_transformer(
            inputs_embeds=hidden,
            use_cache=True,
            past_key_values=binding.request_slot.kv,
            cache_position=cache_position,
            attention_mask=attn_mask,
        ).last_hidden_state
        hidden = hidden.permute(0, 2, 1).contiguous()
        for stage in self.upsample:
            hidden = stage[0](
                hidden, binding.request_slot.tconv1d, binding.workspace_slot.tconv1d
            )
            hidden = stage[1](hidden, binding)
        wav = self.decoder_pre_conv(
            hidden, binding.request_slot.conv1d, binding.workspace_slot.conv1d
        )
        for block in self.decoder_blocks:
            wav = block(wav, binding)
        wav = self.decoder_snake(wav).contiguous()
        wav = self.final_conv(
            wav, binding.request_slot.conv1d, binding.workspace_slot.conv1d
        )
        return wav.clamp(min=-1, max=1)


class ExecutionLane:
    def __init__(
        self,
        lane_id: int,
        tokenizer: Qwen3TTSTokenizer,
        chunk_frames: int,
        hot_state: RequestStateSlot,
        workspace: WorkspaceSlot,
        fast: bool = False,
    ):
        if tokenizer.model is None:
            raise ValueError("Tokenizer model is not loaded.")
        self.chunk_frames = int(chunk_frames)
        self.lane_id = int(lane_id)
        self.binding = LaneBinding(request_slot=hot_state, workspace_slot=workspace)
        self.core = _LaneCore(
            tokenizer.model.decoder, chunk_frames=chunk_frames, binding=self.binding
        )
        num_quantizers = int(tokenizer.model.decoder.config.num_quantizers)
        state_device = next(iter(hot_state.conv1d.values())).cache_buf.device
        self.codes_in_buf = torch.zeros(
            (1, num_quantizers, self.chunk_frames),
            device=state_device,
            dtype=torch.long,
        )
        self.cache_position_buf = torch.zeros(
            (self.chunk_frames,), device=state_device, dtype=torch.long
        )
        self._base_cache_position = torch.arange(
            self.chunk_frames, device=state_device, dtype=torch.long
        )
        self.step_model = self.core
        self.fast = bool(fast)
        self.cuda_graph: torch.cuda.CUDAGraph | None = None
        self.cuda_graph_out: torch.Tensor | None = None

    def load_request_state(self, state: RequestStateSlot) -> None:
        self.binding.request_slot.next_step = int(state.next_step)
        self.binding.request_slot.req_id = state.req_id
        self.binding.request_slot.tail_flushed = bool(state.tail_flushed)
        _copy_conv_state(self.binding.request_slot.conv1d, state.conv1d)
        _copy_tconv_state(self.binding.request_slot.tconv1d, state.tconv1d)
        _copy_kv_state(self.binding.request_slot.kv, state.kv)

    def store_request_state(self, state: RequestStateSlot) -> None:
        state.req_id = self.binding.request_slot.req_id
        state.next_step = int(self.binding.request_slot.next_step)
        state.tail_flushed = bool(self.binding.request_slot.tail_flushed)
        _copy_conv_state(state.conv1d, self.binding.request_slot.conv1d)
        _copy_tconv_state(state.tconv1d, self.binding.request_slot.tconv1d)
        _copy_kv_state(state.kv, self.binding.request_slot.kv)

    def reset_hot_state(self) -> None:
        self.binding.request_slot.req_id = None
        self.binding.request_slot.next_step = 0
        self.binding.request_slot.tail_flushed = False
        _reset_request_state_tensors(self.binding.request_slot)
        self.codes_in_buf.zero_()
        self.cache_position_buf.zero_()
        for block in self.binding.workspace_slot.conv1d.values():
            block.x_buf.zero_()
        for block in self.binding.workspace_slot.tconv1d.values():
            block.x_buf.zero_()

    def warmup_cuda_graph(self, warmup_rounds: int = 2) -> None:
        """Capture the stateful fixed-shape codec step after Snake compilation."""
        if not self.fast or self.cuda_graph is not None:
            return
        device = self.codes_in_buf.device
        if device.type != "cuda":
            raise RuntimeError("codec CUDA Graph fast path requires CUDA")
        capture_stream = torch.cuda.Stream(device=device)
        capture_stream.wait_stream(torch.cuda.current_stream(device))
        with torch.cuda.stream(capture_stream):
            for _ in range(max(1, warmup_rounds)):
                self.cuda_graph_out = self.step_model(
                    self.codes_in_buf, self.cache_position_buf
                )
            capture_stream.synchronize()
            self.cuda_graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(
                self.cuda_graph,
                stream=capture_stream,
                capture_error_mode="thread_local",
            ):
                self.cuda_graph_out = self.step_model(
                    self.codes_in_buf, self.cache_position_buf
                )
        torch.cuda.current_stream(device).wait_stream(capture_stream)

    def run_step(self, codes_chunk: torch.Tensor, step_idx: int) -> torch.Tensor:
        t_new = int(codes_chunk.shape[-1])
        if t_new != self.chunk_frames:
            raise ValueError(
                f"ExecutionLane expects fixed chunk_frames={self.chunk_frames}, got step len={t_new}."
            )
        self.codes_in_buf.copy_(codes_chunk)
        self.cache_position_buf.copy_(self._base_cache_position)
        self.cache_position_buf.add_(int(step_idx))
        _cg_mark()
        if self.cuda_graph is None:
            out = self.step_model(self.codes_in_buf, self.cache_position_buf)
        else:
            self.cuda_graph.replay()
            assert self.cuda_graph_out is not None
            out = self.cuda_graph_out
        self.binding.request_slot.next_step = int(step_idx) + t_new
        return out
