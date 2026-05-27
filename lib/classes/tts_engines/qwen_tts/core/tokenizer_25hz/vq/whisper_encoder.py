# coding=utf-8
# Copyright 2026 The Alibaba Qwen team.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import math
import torch
import operator

import numpy as np
import torch.nn.functional as F

from functools import lru_cache
from typing import Optional, Union, List
from torch import nn, Tensor
from itertools import accumulate

try:
    from flash_attn.flash_attn_interface import flash_attn_varlen_func as flash_attn_varlen_func
except ImportError:
    try:
        from flash_attn.flash_attn_interface import flash_attn_unpadded_func as flash_attn_varlen_func
    except ImportError:
        print("\n********\nWarning: flash-attn is not installed. Will only run the manual PyTorch version. Please install flash-attn for faster inference.\n********\n ")
        flash_attn_varlen_func = None


N_FFT = 400
HOP_LENGTH = 160


@lru_cache(maxsize=None)
def mel_filters(device, n_mels: int) -> torch.Tensor:
    """
    load the mel filterbank matrix for projecting STFT into a Mel spectrogram.
    Allows decoupling librosa dependency; saved using:

        np.savez_compressed(
            "mel_filters.npz",
            mel_80=librosa.filters.mel(sr=16000, n_fft=400, n_mels=80),
            mel_128=librosa.filters.mel(sr=16000, n_fft=400, n_mels=128),
        )
    """
    assert n_mels in {80, 128}, f"Unsupported n_mels: {n_mels}"

    filters_path = os.path.join(os.path.dirname(__file__), "assets", "mel_filters.npz")
    with np.load(filters_path, allow_pickle=False) as f:
        return torch.from_numpy(f[f"mel_{n_mels}"]).to(device)


def log_mel_spectrogram(
    audio: Union[str, np.ndarray, torch.Tensor],
    n_mels: int = 80,
    padding: int = 0,
    device: Optional[Union[str, torch.device]] = None,
):
    """
    Compute the log-Mel spectrogram of

    Parameters
    ----------
    audio: Union[str, np.ndarray, torch.Tensor], shape = (*)
        The path to audio or either a NumPy array or Tensor containing the audio waveform in 16 kHz

    n_mels: int
        The number of Mel-frequency filters, only 80 is supported

    padding: int
        Number of zero samples to pad to the right

    device: Optional[Union[str, torch.device]]
        If given, the audio tensor is moved to this device before STFT

    Returns
    -------
    torch.Tensor, shape = (80, n_frames)
        A Tensor that contains the Mel spectrogram
    """
    if not torch.is_tensor(audio):
        audio = torch.from_numpy(audio)

    if device is not None:
        audio = audio.to(device)
    if padding > 0:
        audio = F.pad(audio, (0, padding))
    window = torch.hann_window(N_FFT).to(audio.device)
    stft = torch.stft(audio, N_FFT, HOP_LENGTH, window=window, return_complex=True)
    magnitudes = stft[..., :-1].abs() ** 2

    filters = mel_filters(audio.device, n_mels)
    mel_spec = filters @ magnitudes

    log_spec = torch.clamp(mel_spec, min=1e-10).log10()
    log_spec = torch.maximum(log_spec, log_spec.max() - 8.0)
    log_spec = (log_spec + 4.0) / 4.0
    return log_spec


def get_T_after_cnn(L_in, dilation=1):
    for (padding, kernel_size, stride) in eval("[(1,3,1)] + [(1,3,2)] "):
        L_out = L_in + 2 * padding - dilation * (kernel_size - 1) - 1
        L_out = 1 + L_out // stride
        L_in = L_out
    return L_out


def get_mel_audio(audio, padding=False, audio_vq_ds_rate = 1, n_mels = 128):
    audio_len = len(audio)
    if padding:
        reduction = 160 * 2 * audio_vq_ds_rate
        audio_pad = math.ceil(audio_len / reduction) * reduction - audio_len
        mel = log_mel_spectrogram(audio, n_mels=n_mels, padding=audio_pad)
    else:
        mel = log_mel_spectrogram(audio, n_mels=n_mels)  # [F,T]
    return mel


def sinusoids(length, channels, max_timescale=10000):
    """Returns sinusoids for positional embedding"""
    assert channels % 2 == 0
    log_timescale_increment = np.log(max_timescale) / (channels // 2 - 1)
    inv_timescales = torch.exp(-log_timescale_increment * torch.arange(channels // 2))
    scaled_time = torch.arange(length)[:, np.newaxis] * inv_timescales[np.newaxis, :]
    return torch.cat([torch.sin(scaled_time), torch.cos(scaled_time)], dim=1)


class Conv1d(nn.Conv1d):
    def _conv_forward(
        self, x: Tensor, weight: Tensor, bias: Optional[Tensor]
    ) -> Tensor:
        return super()._conv_forward(
            x, weight.to(x.dtype), None if bias is None else bias.to(x.dtype)
        )


class ConvTranspose1d(nn.ConvTranspose1d):
    def _conv_forward(
        self, x: Tensor, weight: Tensor, bias: Optional[Tensor]
    ) -> Tensor:
        return super()._conv_forward(
            x, weight.to(x.dtype), None if bias is None else bias.to(x.dtype)
        )


class Linear(nn.Linear):
    def forward(self, x: Tensor) -> Tensor:
        return F.linear(x, self.weight.to(x.dtype), None if self.bias is None else self.bias.to(x.dtype) )


class MultiHeadAttention(nn.Module):
    def __init__(self, n_state: int, n_head: int):
        super().__init__()
        self.n_head = n_head
        self.query = Linear(n_state, n_state)
        self.key = Linear(n_state, n_state, bias=False)
        self.value = Linear(n_state, n_state)
        self.out = Linear(n_state, n_state)

        self.use_flash_attention = True

    def forward(
        self,
        x: Tensor,
        cu_seqlens = None,
    ):
        q = self.query(x)
        k = self.key(x)
        v = self.value(x)
        
        if self.use_flash_attention:
            if flash_attn_varlen_func is None:
                x = self.qkv_attention_manual(q, k, v, cu_seqlens=cu_seqlens)
            else:
                if q.dtype not in [torch.float16, torch.bfloat16]:
                    x = self.qkv_attention_manual(q, k, v, cu_seqlens=cu_seqlens)
                    self.use_flash_attention = False
                else:
                    x = self.qkv_flash_attention(q, k, v, cu_seqlens=cu_seqlens)
        else:
            x = self.qkv_attention_manual(q, k, v, cu_seqlens=cu_seqlens)

        output = self.out(x)
        return output

    def qkv_flash_attention(
        self, q: Tensor, k: Tensor, v: Tensor, cu_seqlens=None
    ):
        n_ctx, n_state = q.shape
        # scale = (n_state // self.n_head) ** -0.25
        q = q.view(n_ctx, self.n_head, -1)# (batch_size, seqlen, nheads, headdim)
        k = k.view(n_ctx, self.n_head, -1)
        v = v.view(n_ctx, self.n_head, -1)

        max_seqlen = (cu_seqlens[1:] - cu_seqlens[:-1]).max().item()


        x = flash_attn_varlen_func(
            q, k, v, cu_seqlens, cu_seqlens, max_seqlen, max_seqlen, dropout_p=0.0
        )
        x = x.reshape(n_ctx, n_state)
        return x

    def qkv_attention_manual(
        self, q: Tensor, k: Tensor, v: Tensor, cu_seqlens: Tensor
    ):
        n_ctx, n_state = q.shape
        head_dim = n_state // self.n_head
        scale = head_dim ** -0.5

        q = q.view(n_ctx, self.n_head, head_dim)
        k = k.view(n_ctx, self.n_head, head_dim)
        v = v.view(n_ctx, self.n_head, head_dim)

        seqlens = (cu_seqlens[1:] - cu_seqlens[:-1]).tolist()
        batch_size = len(seqlens)
        max_seqlen = max(seqlens)

        q_padded = torch.zeros(batch_size, max_seqlen, self.n_head, head_dim, dtype=q.dtype, device=q.device)
        k_padded = torch.zeros_like(q_padded)
        v_padded = torch.zeros_like(q_padded)

        for i in range(batch_size):
            start_idx = cu_seqlens[i]
            end_idx = cu_seqlens[i+1]
            seq_len = seqlens[i]
            q_padded[i, :seq_len] = q[start_idx:end_idx]
            k_padded[i, :seq_len] = k[start_idx:end_idx]
            v_padded[i, :seq_len] = v[start_idx:end_idx]
        
        q_padded = q_padded.transpose(1, 2)
        k_padded = k_padded.transpose(1, 2)
        v_padded = v_padded.transpose(1, 2)

        attn_mask = torch.arange(max_seqlen, device=q.device)[None, :] < torch.tensor(seqlens, device=q.device)[:, None]
        attn_mask = attn_mask.unsqueeze(1).unsqueeze(2)

        attn_mask = attn_mask.masked_fill(attn_mask == 0, -torch.finfo(q.dtype).max)

        attn_scores = torch.matmul(q_padded, k_padded.transpose(-2, -1)) * scale
        attn_scores = attn_scores + attn_mask
        attn_weights = F.softmax(attn_scores, dim=-1)

        context = torch.matmul(attn_weights, v_padded)
        
        context = context.transpose(1, 2).contiguous().view(batch_size, max_seqlen, n_state)

        output_packed = torch.cat([context[i, :seqlens[i]] for i in range(batch_size)], dim=0)

        assert output_packed.shape == (n_ctx, n_state)
        
        return output_packed


class ResidualAttentionBlock(nn.Module):
    def __init__(self, n_state: int, n_head: int,
                 enable_mp: bool = False, sequence_parallel: bool = False):
        super().__init__()
        n_mlp = n_state * 4
        self.attn_ln = nn.LayerNorm(n_state)
        self.mlp_ln = nn.LayerNorm(n_state)

        self.attn = MultiHeadAttention(n_state, n_head)
        self.mlp = nn.Sequential(
                Linear(n_state, n_mlp), nn.GELU(), Linear(n_mlp, n_state)
            )

    def forward(
        self,
        x: Tensor,
        cu_seqlens = None
    ):
        x = x + self.attn(self.attn_ln(x), cu_seqlens=cu_seqlens)
        x = x + self.mlp(self.mlp_ln(x))
        return x


class WhisperEncoder(nn.Module):
    def __init__(
            self,
            n_mels: int,
            n_ctx: int,
            n_state: int,
            n_head: int,
            n_layer: int,
            n_window: int = 1500,
            output_dim: int = 512,
            grad_checkpointing: bool = False,
            enable_mp: bool = False,
            audio_sequence_parallel: bool = False,
    ):
        super().__init__()
        self.conv1 = Conv1d(n_mels, n_state, kernel_size=3, padding=1)
        self.conv2 = Conv1d(n_state, n_state, kernel_size=3, stride=2, padding=1)
        self.register_buffer("positional_embedding", sinusoids(n_ctx, n_state))
        self.n_layer = n_layer
        self.n_mels = n_mels

        self.blocks = nn.ModuleList(
            [ResidualAttentionBlock(n_state, n_head, enable_mp=enable_mp, sequence_parallel=audio_sequence_parallel)
             for _ in range(n_layer)]
        )
        self.ln_post = nn.LayerNorm(n_state)
        self.avg_pooler = nn.AvgPool1d(2, stride=2)

        self.proj = torch.nn.Linear(n_state, output_dim)

        self.audio_bos_eos_token = nn.Embedding(2, output_dim)

        self.output_dim = output_dim
        self.grad_checkpointing = grad_checkpointing
        self.enable_mp = enable_mp
        self.n_head = n_head
        self.n_state = n_state
        self.n_window = n_window

        self.audio_sequence_parallel = audio_sequence_parallel

        self.tp_world_size = 1

        self.set_audio_sync()

    def set_audio_sync(self):
        for name, param in self.named_parameters():
            if not name.startswith("blocks"):
                setattr(param, "audio_sync", True)

    def forward(self, x_list: List[Tensor], audio_mellens:List[int], audio_aftercnnlens:List[int], audio_seqlens:List[int]):
        """
        x : torch.Tensor, shape = (n_mels, n_ctx)
            the mel spectrogram of the audio
        """

        aftercnn_x_list = []
        for each_x in x_list:
            each_x_split_list = each_x.split(self.n_window * 2, dim=1)
            for each_x_split in each_x_split_list:
                each_x_split = F.gelu(self.conv1(each_x_split))
                each_x_split = F.gelu(self.conv2(each_x_split))
                each_x_split = each_x_split.permute(1, 0) # L,D
                each_positional_embedding_split = self.positional_embedding[:each_x_split.shape[0]]
                aftercnn_x_list.append(each_x_split+each_positional_embedding_split.to(each_x_split.dtype))

        x = torch.cat(aftercnn_x_list, dim=0)
        src_len = x.size(0)

        output_list = []
        for item in audio_aftercnnlens:
            while item > self.n_window:
                output_list.append(self.n_window)
                item -= self.n_window
            output_list.append(item)

        cu_seqlens = list(accumulate(output_list, func=operator.add,initial=0))
        cu_seqlens = torch.Tensor(cu_seqlens).to(device=x.device, dtype=torch.int32)

        layer_id = 0
        for block in self.blocks:
            layer_id+=1
            x = block(x, cu_seqlens=cu_seqlens)

        if self.avg_pooler:
            x_list = x.split(audio_aftercnnlens, dim=0)
            token_x_list = []
            for x in x_list:
                x = x.permute(1, 0)
                x = self.avg_pooler(x)
                x = x.permute(1, 0)
                token_x_list.append(x)
            x = torch.cat(token_x_list, dim=0)

        x = self.ln_post(x)
        x = self.proj(x)

        output = torch.zeros(
            (x.size(0) + len(audio_seqlens) * 2, x.size(1)),
            device=x.device, dtype=x.dtype
        )

        audio_seqlens_acc = list(accumulate(audio_seqlens, func=operator.add, initial=0))
        start_ids = torch.tensor(audio_seqlens_acc[:-1], device=x.device, dtype=torch.int32)
        end_ids = torch.tensor(audio_seqlens_acc[1:], device=x.device, dtype=torch.int32) - 1

        audio_tokens_mask = torch.ones(output.size(0), device=x.device, dtype=torch.bool)
        audio_tokens_mask[start_ids] = False
        audio_tokens_mask[end_ids] = False
        output[start_ids] = self.audio_bos_eos_token.weight[0].to(x.dtype)
        output[end_ids] = self.audio_bos_eos_token.weight[1].to(x.dtype)
        output[audio_tokens_mask] = x
        return output

    def lock(self, layers: int):
        self.conv1.requires_grad_(False)
        self.conv2.requires_grad_(False)
        for i in range(min(layers, len(self.blocks))):
            self.blocks[i].requires_grad_(False)
