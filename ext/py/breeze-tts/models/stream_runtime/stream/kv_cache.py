from __future__ import annotations

from typing import Any

import torch
from torch import nn


class _LayerKV(nn.Module):
    def __init__(self, k: torch.Tensor, v: torch.Tensor):
        super().__init__()
        self.register_buffer("k", k, persistent=False)
        self.register_buffer("v", v, persistent=False)


class StaticShiftKVCache(nn.Module):
    def __init__(
        self,
        num_layers: int,
        window: int,
        batch: int,
        h_kv: int,
        head_dim: int,
        device,
        dtype,
    ):
        super().__init__()
        self.window = int(window)
        self.layers = nn.ModuleList(
            [
                _LayerKV(
                    k=torch.zeros(
                        (batch, h_kv, self.window, head_dim), device=device, dtype=dtype
                    ),
                    v=torch.zeros(
                        (batch, h_kv, self.window, head_dim), device=device, dtype=dtype
                    ),
                )
                for _ in range(num_layers)
            ]
        )
        self.is_sliding = [True] * num_layers

    def get_seq_length(self) -> int:
        return int(self.window)

    def get_mask_sizes(self, cache_position: torch.Tensor, layer_idx: int):
        q_len = int(cache_position.numel()) if cache_position is not None else 1
        if cache_position is None or cache_position.numel() == 0:
            return self.window, 0
        cur_pos = int(cache_position.reshape(-1)[-1].item())
        kv_length = min(cur_pos + 1, self.window)
        kv_offset = max(cur_pos + 1 - kv_length, 0)
        return kv_length, kv_offset

    def update(
        self,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        layer_idx: int,
        cache_kwargs: Any,
    ):
        layer = self.layers[layer_idx]
        t_new = key_states.shape[-2]
        if not torch._dynamo.is_compiling() and t_new > self.window:
            raise ValueError(
                f"StaticShiftKVCache assumes T_new <= window={self.window}, got {t_new}."
            )
        shift = min(int(t_new), self.window)
        if shift < self.window:
            layer.k[..., :-shift, :].copy_(layer.k[..., shift:, :])
            layer.v[..., :-shift, :].copy_(layer.v[..., shift:, :])
            layer.k[..., -shift:, :].copy_(key_states[..., -shift:, :])
            layer.v[..., -shift:, :].copy_(value_states[..., -shift:, :])
        else:
            layer.k.copy_(key_states[..., -self.window :, :])
            layer.v.copy_(value_states[..., -self.window :, :])
        return layer.k, layer.v


def make_fixed_attention_mask(
    batch: int,
    window: int,
    cache_position: torch.Tensor,
    device: torch.device,
    dtype: torch.dtype,
) -> torch.Tensor:
    positions = cache_position.reshape(-1)
    end_pos = positions[-1]
    # Column j corresponds to the absolute key position:
    #   abs_key(j) = end_pos - window + 1 + j
    # We keep the column index static so torch.compile sees a fixed-size buffer.
    cols = torch.arange(window, device=device, dtype=positions.dtype).view(1, window)
    min_valid_col = torch.clamp((window - 1) - end_pos, min=0)
    max_valid_col = positions.view(-1, 1) - end_pos + (window - 1)
    valid = (cols >= min_valid_col) & (cols <= max_valid_col)
    zeros = torch.zeros((positions.numel(), window), device=device, dtype=dtype)
    neg_inf = torch.full(
        (positions.numel(), window), torch.finfo(dtype).min, device=device, dtype=dtype
    )
    mask = torch.where(valid, zeros, neg_inf)
    return mask.view(1, 1, positions.numel(), window).expand(
        batch, 1, positions.numel(), window
    )
