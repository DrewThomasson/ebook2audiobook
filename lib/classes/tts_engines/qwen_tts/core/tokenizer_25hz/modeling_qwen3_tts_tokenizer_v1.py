# coding=utf-8
# Copyright 2026 The Qwen team, Alibaba Group and the HuggingFace Inc. team. All rights reserved.
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
"""PyTorch Qwen3TTSTokenizerV1 model."""

import math
from dataclasses import dataclass
from typing import Optional, Union, List

import numpy as np
import torch
from torch import nn
from torch.nn import Parameter
from torch.nn import functional as F
from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS, PreTrainedModel
from transformers.utils import ModelOutput, auto_docstring, logging
from transformers.utils.hub import cached_file

from torch.nn.utils.rnn import pad_sequence

from .vq.whisper_encoder import get_mel_audio, get_T_after_cnn
from .vq.speech_vq import WhisperEncoderVQ, XVectorExtractor

from .configuration_qwen3_tts_tokenizer_v1 import (
    Qwen3TTSTokenizerV1Config,
    Qwen3TTSTokenizerV1EncoderConfig,
    Qwen3TTSTokenizerV1DecoderConfig,
    Qwen3TTSTokenizerV1DecoderBigVGANConfig,
    Qwen3TTSTokenizerV1DecoderDiTConfig
)

logger = logging.get_logger(__name__)


@dataclass
@auto_docstring
class Qwen3TTSTokenizerV1EncoderOutput(ModelOutput):
    r"""
    audio_codes (`List[torch.LongTensor]`):
        Discret code embeddings computed using `model.encode`, each tensor has shape (codes_length_i,).
    xvectors (`List[torch.FloatTensor]`):
        X-vector embeddings computed using `model.encode`, each tensor has shape (xvector_dim,).
    ref_mels (`List[torch.FloatTensor]`):
        Reference mel spectrogram computed using `model.encode`, each tensor has shape (mel_length_i, mel_dim,).
    """

    audio_codes: List[torch.LongTensor] = None
    xvectors: List[torch.FloatTensor] = None
    ref_mels: List[torch.FloatTensor] = None


@dataclass
@auto_docstring
class Qwen3TTSTokenizerV1DecoderOutput(ModelOutput):
    r"""
    audio_values (`List[torch.FloatTensor]`):
        Decoded audio values, obtained using the decoder part of Qwen3TTSTokenizerV1.
        Each tensor has shape (segment_length_i).
    """

    audio_values: List[torch.FloatTensor] = None


@auto_docstring
class Qwen3TTSTokenizerV1DecoderPreTrainedModel(PreTrainedModel):
    config: Qwen3TTSTokenizerV1DecoderConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _skip_keys_device_placement = "past_key_values"
    _supports_flash_attn = True
    _supports_sdpa = True
    _can_compile_fullgraph = False
    _supports_attention_backend = True


@auto_docstring
class Qwen3TTSTokenizerV1EncoderPreTrainedModel(PreTrainedModel):
    config: Qwen3TTSTokenizerV1EncoderConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _skip_keys_device_placement = "past_key_values"
    _supports_flash_attn = True
    _supports_sdpa = True
    _can_compile_fullgraph = False
    _supports_attention_backend = True


class Qwen3TTSTokenizerV1DecoderDiTRotaryEmbedding(nn.Module):
    inv_freq: torch.Tensor  # fix linting for `register_buffer`

    def __init__(self, dim, base=10000):
        super().__init__()

        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)

    def forward(self, x):
        batch_size, seq_len = x.shape[0], x.shape[1]
        t = torch.arange(seq_len, device=x.device)
        device_type = x.device.type
        device_type = device_type if device_type != "mps" else "cpu"
        with torch.autocast(device_type=device_type, enabled=False):
            freqs = t.unsqueeze(1).float() @ self.inv_freq.unsqueeze(0).float()
            freqs = torch.stack((freqs, freqs), dim=-1)
            freqs = freqs.reshape(*freqs.shape[:-2], -1)
            freqs = freqs.repeat(batch_size, *([1] * freqs.dim()))
            cos = freqs.cos()
            sin = freqs.sin()

        return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)


class TimeDelayNetBlock(nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        dilation,
    ):
        super().__init__()
        self.conv = nn.Conv1d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            dilation=dilation,
            padding="same",
            padding_mode="reflect",
        )
        self.activation = nn.ReLU()

    def forward(self, hidden_states: torch.Tensor):
        return self.activation(self.conv(hidden_states))


class Res2NetBlock(torch.nn.Module):
    def __init__(self, in_channels, out_channels, scale=8, kernel_size=3, dilation=1):
        super().__init__()

        in_channel = in_channels // scale
        hidden_channel = out_channels // scale

        self.blocks = nn.ModuleList(
            [
                TimeDelayNetBlock(
                    in_channel,
                    hidden_channel,
                    kernel_size=kernel_size,
                    dilation=dilation,
                )
                for i in range(scale - 1)
            ]
        )
        self.scale = scale

    def forward(self, hidden_states):
        outputs = []
        for i, hidden_part in enumerate(torch.chunk(hidden_states, self.scale, dim=1)):
            if i == 0:
                output_part = hidden_part
            elif i == 1:
                output_part = self.blocks[i - 1](hidden_part)
            else:
                output_part = self.blocks[i - 1](hidden_part + output_part)
            outputs.append(output_part)
        output = torch.cat(outputs, dim=1)
        return output


class SqueezeExcitationBlock(nn.Module):
    def __init__(self, in_channels, se_channels, out_channels):
        super().__init__()

        self.conv1 = nn.Conv1d(
            in_channels=in_channels,
            out_channels=se_channels,
            kernel_size=1,
            padding="same",
            padding_mode="reflect",
        )
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv1d(
            in_channels=se_channels,
            out_channels=out_channels,
            kernel_size=1,
            padding="same",
            padding_mode="reflect",
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, hidden_states):
        hidden_states_mean = hidden_states.mean(dim=2, keepdim=True)

        hidden_states_mean = self.relu(self.conv1(hidden_states_mean))
        hidden_states_mean = self.sigmoid(self.conv2(hidden_states_mean))

        return hidden_states * hidden_states_mean


class AttentiveStatisticsPooling(nn.Module):
    """This class implements an attentive statistic pooling layer for each channel.
    It returns the concatenated mean and std of the input tensor.
    """

    def __init__(self, channels, attention_channels=128):
        super().__init__()

        self.eps = 1e-12
        self.tdnn = TimeDelayNetBlock(channels * 3, attention_channels, 1, 1)
        self.tanh = nn.Tanh()
        self.conv = nn.Conv1d(
            in_channels=attention_channels,
            out_channels=channels,
            kernel_size=1,
            padding="same",
            padding_mode="reflect",
        )

    def _length_to_mask(self, length, max_len=None, dtype=None, device=None):
        """Creates a binary mask for each sequence.

        Reference: https://discuss.pytorch.org/t/how-to-generate-variable-length-mask/23397/3

        Arguments
        ---------
        length : torch.LongTensor
            Containing the length of each sequence in the batch. Must be 1D.
        max_len : int
            Max length for the mask, also the size of the second dimension.
        dtype : torch.dtype, default: None
            The dtype of the generated mask.
        device: torch.device, default: None
            The device to put the mask variable.

        Returns
        -------
        mask : tensor
            The binary mask.
        """

        if max_len is None:
            max_len = length.max().long().item()  # using arange to generate mask
        mask = torch.arange(max_len, device=length.device, dtype=length.dtype).expand(
            len(length), max_len
        ) < length.unsqueeze(1)

        mask = torch.as_tensor(mask, dtype=dtype, device=device)
        return mask

    def _compute_statistics(self, x, m, dim=2):
        mean = (m * x).sum(dim)
        std = torch.sqrt((m * (x - mean.unsqueeze(dim)).pow(2)).sum(dim).clamp(self.eps))
        return mean, std

    def forward(self, hidden_states):
        seq_length = hidden_states.shape[-1]
        lengths = torch.ones(hidden_states.shape[0], device=hidden_states.device)

        # Make binary mask of shape [N, 1, L]
        mask = self._length_to_mask(
            lengths * seq_length, max_len=seq_length, dtype=hidden_states.dtype, device=hidden_states.device
        )
        mask = mask.unsqueeze(1)

        # Expand the temporal context of the pooling layer by allowing the
        # self-attention to look at global properties of the utterance.
        total = mask.sum(dim=2, keepdim=True)

        mean, std = self._compute_statistics(hidden_states, mask / total)
        mean = mean.unsqueeze(2).repeat(1, 1, seq_length)
        std = std.unsqueeze(2).repeat(1, 1, seq_length)
        attention = torch.cat([hidden_states, mean, std], dim=1)

        # Apply layers
        attention = self.conv(self.tanh(self.tdnn(attention)))

        # Filter out zero-paddings
        attention = attention.masked_fill(mask == 0, float("-inf"))

        attention = F.softmax(attention, dim=2)
        mean, std = self._compute_statistics(hidden_states, attention)
        # Append mean and std of the batch
        pooled_stats = torch.cat((mean, std), dim=1)
        pooled_stats = pooled_stats.unsqueeze(2)

        return pooled_stats


class SqueezeExcitationRes2NetBlock(nn.Module):
    """An implementation of building block in ECAPA-TDNN, i.e.,
    TDNN-Res2Net-TDNN-SqueezeExcitationBlock.
    """

    def __init__(
        self,
        in_channels,
        out_channels,
        res2net_scale=8,
        se_channels=128,
        kernel_size=1,
        dilation=1,
    ):
        super().__init__()
        self.out_channels = out_channels
        self.tdnn1 = TimeDelayNetBlock(
            in_channels,
            out_channels,
            kernel_size=1,
            dilation=1,
        )
        self.res2net_block = Res2NetBlock(out_channels, out_channels, res2net_scale, kernel_size, dilation)
        self.tdnn2 = TimeDelayNetBlock(
            out_channels,
            out_channels,
            kernel_size=1,
            dilation=1,
        )
        self.se_block = SqueezeExcitationBlock(out_channels, se_channels, out_channels)

    def forward(self, hidden_state):
        residual = hidden_state

        hidden_state = self.tdnn1(hidden_state)
        hidden_state = self.res2net_block(hidden_state)
        hidden_state = self.tdnn2(hidden_state)
        hidden_state = self.se_block(hidden_state)

        return hidden_state + residual


class ECAPA_TimeDelayNet(torch.nn.Module):
    """An implementation of the speaker embedding model in a paper.
    "ECAPA-TDNN: Emphasized Channel Attention, Propagation and Aggregation in
    TDNN Based Speaker Verification" (https://huggingface.co/papers/2005.07143).
    """

    def __init__(self, config: Qwen3TTSTokenizerV1DecoderBigVGANConfig):
        super().__init__()
        if len(config.enc_channels) != len(config.enc_kernel_sizes) or len(config.enc_channels) != len(
            config.enc_dilations
        ):
            raise ValueError("enc_channels, enc_kernel_sizes and enc_dilations should have same length")
        self.channels = config.enc_channels
        self.blocks = nn.ModuleList()

        # The initial TDNN layer
        self.blocks.append(
            TimeDelayNetBlock(
                config.mel_dim,
                config.enc_channels[0],
                config.enc_kernel_sizes[0],
                config.enc_dilations[0],
            )
        )

        # SE-Res2Net layers
        for i in range(1, len(config.enc_channels) - 1):
            self.blocks.append(
                SqueezeExcitationRes2NetBlock(
                    config.enc_channels[i - 1],
                    config.enc_channels[i],
                    res2net_scale=config.enc_res2net_scale,
                    se_channels=config.enc_se_channels,
                    kernel_size=config.enc_kernel_sizes[i],
                    dilation=config.enc_dilations[i],
                )
            )

        # Multi-layer feature aggregation
        self.mfa = TimeDelayNetBlock(
            config.enc_channels[-1],
            config.enc_channels[-1],
            config.enc_kernel_sizes[-1],
            config.enc_dilations[-1],
        )

        # Attentive Statistical Pooling
        self.asp = AttentiveStatisticsPooling(
            config.enc_channels[-1],
            attention_channels=config.enc_attention_channels,
        )

        # Final linear transformation
        self.fc = nn.Conv1d(
            in_channels=config.enc_channels[-1] * 2,
            out_channels=config.enc_dim,
            kernel_size=1,
            padding="same",
            padding_mode="reflect",
        )

    def forward(self, hidden_states):
        # Minimize transpose for efficiency
        hidden_states = hidden_states.transpose(1, 2)

        hidden_states_list = []
        for layer in self.blocks:
            hidden_states = layer(hidden_states)
            hidden_states_list.append(hidden_states)

        # Multi-layer feature aggregation
        hidden_states = torch.cat(hidden_states_list[1:], dim=1)
        hidden_states = self.mfa(hidden_states)

        # Attentive Statistical Pooling
        hidden_states = self.asp(hidden_states)

        # Final linear transformation
        hidden_states = self.fc(hidden_states)

        hidden_states = hidden_states.squeeze(-1)
        return hidden_states


class DiTInputEmbedding(nn.Module):
    def __init__(self, config: Qwen3TTSTokenizerV1DecoderBigVGANConfig):
        super().__init__()
        self.proj = nn.Linear(
            config.mel_dim + config.enc_dim + config.enc_emb_dim + config.emb_dim,
            config.hidden_size,
        )
        self.spk_encoder = ECAPA_TimeDelayNet(config)

    def forward(
        self,
        hidden_states: torch.Tensor,
        speaker_embedding: torch.Tensor,
        condition_vector: torch.Tensor,
        code_embed: torch.Tensor,
        drop_audio_cond: Optional[bool] = False,
        code_embed_uncond: Optional[bool] = None,
        apply_cfg: Optional[bool] = True,
    ):
        if apply_cfg:
            hidden_states = torch.cat([hidden_states, hidden_states], dim=0)
            speaker_embedding = torch.cat([speaker_embedding, torch.zeros_like(speaker_embedding)], dim=0)
            condition_vector = torch.cat([condition_vector, torch.zeros_like(condition_vector)], dim=0)
            code_embed = torch.cat([code_embed, code_embed_uncond], dim=0)
        elif drop_audio_cond:  # cfg for cond audio
            condition_vector = torch.zeros_like(condition_vector)
            speaker_embedding = torch.zeros_like(speaker_embedding)
        condition_vector = self.spk_encoder(condition_vector).unsqueeze(1).repeat(1, hidden_states.size(1), 1)
        hidden_states = self.proj(torch.cat((hidden_states, condition_vector, code_embed, speaker_embedding), dim=-1))

        return hidden_states


# Transformer backbone using DiT blocks
class DiTCodecEmbedding(nn.Module):
    def __init__(self, codec_num_embeds, codec_dim, repeats):
        super().__init__()
        self.repeats = repeats
        self.codec_embed = nn.Embedding(codec_num_embeds + 1, codec_dim)

    def forward(self, code, drop_code=False):
        if drop_code:
            code = torch.zeros_like(code)
        code_embed = self.codec_embed(code)

        code_embed = torch.repeat_interleave(code_embed, repeats=self.repeats, dim=1)
        return code_embed


# AdaLayerNormZero
# return with modulated x for attn input, and params for later mlp modulation
class AdaLayerNormZero(nn.Module):
    def __init__(self, dim):
        super().__init__()

        self.silu = nn.SiLU()
        self.linear = nn.Linear(dim, dim * 6)

        self.norm = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-6)

    def forward(self, hidden_states, emb=None):
        emb = self.linear(self.silu(emb))
        shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = torch.chunk(emb, 6, dim=1)

        hidden_states = self.norm(hidden_states) * (1 + scale_msa[:, None]) + shift_msa[:, None]
        return hidden_states, gate_msa, shift_mlp, scale_mlp, gate_mlp


# AdaLayerNormZero for final layer
# return only with modulated x for attn input, cuz no more mlp modulation
class AdaLayerNormZero_Final(nn.Module):
    def __init__(self, dim):
        super().__init__()

        self.silu = nn.SiLU()
        self.linear = nn.Linear(dim, dim * 2)

        self.norm = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-6)

    def forward(self, hidden_states, emb):
        emb = self.linear(self.silu(emb))
        scale, shift = torch.chunk(emb, 2, dim=1)

        hidden_states = self.norm(hidden_states) * (1 + scale)[:, None, :] + shift[:, None, :]
        return hidden_states


# FeedForward
class DiTMLP(nn.Module):
    def __init__(self, dim, mult=4, dropout=0.0):
        super().__init__()
        inner_dim = int(dim * mult)

        self.ff = nn.ModuleList(
            [
                nn.Linear(dim, inner_dim),
                nn.GELU(approximate="tanh"),
                nn.Dropout(dropout),
                nn.Linear(inner_dim, dim),
            ]
        )

    def forward(self, hidden_states):
        for layer in self.ff:
            hidden_states = layer(hidden_states)
        return hidden_states


# Modified from Llama with a different rotate function, will fixed in next release
def apply_rotary_pos_emb(q, k, cos, sin, position_ids=None, unsqueeze_dim=1):
    """Applies Rotary Position Embedding to the query and key tensors.

    Args:
        q (`torch.Tensor`): The query tensor.
        k (`torch.Tensor`): The key tensor.
        cos (`torch.Tensor`): The cosine part of the rotary embedding.
        sin (`torch.Tensor`): The sine part of the rotary embedding.
        position_ids (`torch.Tensor`, *optional*):
            Deprecated and unused.
        unsqueeze_dim (`int`, *optional*, defaults to 1):
            The 'unsqueeze_dim' argument specifies the dimension along which to unsqueeze cos[position_ids] and
            sin[position_ids] so that they can be properly broadcasted to the dimensions of q and k. For example, note
            that cos[position_ids] and sin[position_ids] have the shape [batch_size, seq_len, head_dim]. Then, if q and
            k have the shape [batch_size, heads, seq_len, head_dim], then setting unsqueeze_dim=1 makes
            cos[position_ids] and sin[position_ids] broadcastable to the shapes of q and k. Similarly, if q and k have
            the shape [batch_size, seq_len, heads, head_dim], then set unsqueeze_dim=2.
    Returns:
        `tuple(torch.Tensor)` comprising of the query and key tensors rotated using the Rotary Position Embedding.
    """

    def rotate_half_codec(x):
        # x = rearrange(x, "... (d r) -> ... d r", r=2)
        x = x.reshape(*x.shape[:-1], -1, 2)
        x1, x2 = x.unbind(dim=-1)
        x = torch.stack((-x2, x1), dim=-1)
        return x.reshape(*x.shape[:-2], -1)

    cos = cos.unsqueeze(unsqueeze_dim)
    sin = sin.unsqueeze(unsqueeze_dim)
    q_embed = (q * cos) + (rotate_half_codec(q) * sin)
    k_embed = (k * cos) + (rotate_half_codec(k) * sin)
    return q_embed, k_embed


class DiTAttention(nn.Module):
    def __init__(self, config: Qwen3TTSTokenizerV1DecoderBigVGANConfig):
        super().__init__()

        self.config = config
        self.dim = config.hidden_size
        self.heads = config.num_attention_heads
        self.inner_dim = config.head_dim * config.num_attention_heads
        self.dropout = config.dropout
        self.is_causal = False

        self.to_q = nn.Linear(config.hidden_size, self.inner_dim)
        self.to_k = nn.Linear(config.hidden_size, self.inner_dim)
        self.to_v = nn.Linear(config.hidden_size, self.inner_dim)

        self.to_out = nn.ModuleList([nn.Linear(self.inner_dim, config.hidden_size), nn.Dropout(config.dropout)])

    def forward(
        self,
        hidden_states,  # noised input x
        position_embeddings=None,  # rotary position embedding for x
        attention_mask=None,
    ) -> torch.Tensor:
        batch_size = hidden_states.shape[0]

        # `sample` projections.
        query = self.to_q(hidden_states)
        key = self.to_k(hidden_states)
        value = self.to_v(hidden_states)

        # attention
        inner_dim = key.shape[-1]
        head_dim = inner_dim // self.heads
        query = query.view(batch_size, -1, self.heads, head_dim).transpose(1, 2)
        key = key.view(batch_size, -1, self.heads, head_dim).transpose(1, 2)
        value = value.view(batch_size, -1, self.heads, head_dim).transpose(1, 2)

        # apply rotary position embedding
        # Due to training process, only first head is applied with RoPE, will be fixed at next release
        cos, sin = position_embeddings
        query, key = apply_rotary_pos_emb(query, key, cos, sin)

        attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
        attention_weights, _ = attention_interface(
            self,
            query,
            key,
            value,
            attention_mask=attention_mask,
            is_causal=False,
        )

        # mask. e.g. inference got a batch with different target durations, mask out the padding
        attention_weights = attention_weights.reshape(batch_size, -1, self.heads * head_dim)
        attention_weights = attention_weights.to(query.dtype)

        # linear proj
        attention_output = self.to_out[0](attention_weights)
        attention_output = self.to_out[1](attention_output)

        return attention_output


# time step conditioning embedding
class SinusPositionEmbedding(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, hidden_states, scale=1000):
        device = hidden_states.device
        half_dim = self.dim // 2
        emb = math.log(10000) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, device=device).float() * -emb)
        emb = scale * hidden_states.unsqueeze(1) * emb.unsqueeze(0)
        emb = torch.cat((emb.sin(), emb.cos()), dim=-1)
        return emb.type_as(hidden_states)


class DiTTimestepEmbedding(nn.Module):
    def __init__(self, dim, freq_embed_dim=256):
        super().__init__()
        self.time_embed = SinusPositionEmbedding(freq_embed_dim)
        self.time_mlp = nn.ModuleList([nn.Linear(freq_embed_dim, dim), nn.SiLU(), nn.Linear(dim, dim)])

    def forward(self, timestep):
        time_hidden = self.time_embed(timestep)
        time_hidden = time_hidden.to(timestep.dtype)
        for layer in self.time_mlp:
            time_hidden = layer(time_hidden)  # b d
        return time_hidden


class DiTDecoderLayer(nn.Module):
    def __init__(self, config: Qwen3TTSTokenizerV1DecoderBigVGANConfig, look_ahead_block=0, look_backward_block=0):
        super().__init__()
        self.attn_norm = AdaLayerNormZero(config.hidden_size)

        self.attn = DiTAttention(config)
        self.look_ahead_block = look_ahead_block
        self.look_backward_block = look_backward_block
        self.ff_norm = nn.LayerNorm(config.hidden_size, elementwise_affine=False, eps=1e-6)
        self.ff = DiTMLP(dim=config.hidden_size, mult=config.ff_mult, dropout=config.dropout)

    def forward(
        self, hidden_states, timestep, position_embeddings=None, block_diff=None
    ):  # x: noised input, t: time embedding
        # pre-norm & modulation for attention input
        norm, gate_msa, shift_mlp, scale_mlp, gate_mlp = self.attn_norm(hidden_states, emb=timestep)

        # attention
        attn_output = self.attn(
            hidden_states=norm,
            position_embeddings=position_embeddings,
            attention_mask=(block_diff >= -float(self.look_backward_block))
            & (block_diff <= float(self.look_ahead_block)),
        )

        # process attention output for input x
        hidden_states = hidden_states + gate_msa.unsqueeze(1) * attn_output

        norm = self.ff_norm(hidden_states) * (1 + scale_mlp[:, None]) + shift_mlp[:, None]
        ff_output = self.ff(norm)
        hidden_states = hidden_states + gate_mlp.unsqueeze(1) * ff_output

        return hidden_states


class SnakeBeta(nn.Module):
    """
    A modified Snake function which uses separate parameters for the magnitude of the periodic components
    Shape:
        - Input: (B, C, T)
        - Output: (B, C, T), same shape as the input
    Parameters:
        - alpha - trainable parameter that controls frequency
        - beta - trainable parameter that controls magnitude
    References:
        - This activation function is a modified version based on this paper by Liu Ziyin, Tilman Hartwig, Masahito Ueda:
        https://huggingface.co/papers/2006.08195
    """

    def __init__(self, in_features, alpha=1.0):
        super().__init__()
        self.in_features = in_features

        # initialize alpha
        self.alpha = Parameter(torch.zeros(in_features) * alpha)
        self.beta = Parameter(torch.zeros(in_features) * alpha)

        self.no_div_by_zero = 0.000000001

    def forward(self, hidden_states):
        """
        Forward pass of the function.
        Applies the function to the input elementwise.
        SnakeBeta ∶= x + 1/b * sin^2 (xa)
        """
        alpha = self.alpha.unsqueeze(0).unsqueeze(-1)  # line up with x to [B, C, T]
        beta = self.beta.unsqueeze(0).unsqueeze(-1)
        alpha = torch.exp(alpha)
        beta = torch.exp(beta)
        hidden_states = hidden_states + (1.0 / (beta + self.no_div_by_zero)) * torch.pow(
            torch.sin(hidden_states * alpha), 2
        )

        return hidden_states


def kaiser_sinc_filter1d(cutoff, half_width, kernel_size):
    """Generates a 1D Kaiser-windowed sinc filter.

    Args:
        cutoff (float): Normalized cutoff frequency (0 to 0.5).
        half_width (float): Transition bandwidth.
        kernel_size (int): Number of filter taps.

    Returns:
        torch.Tensor: A tensor of shape (1, 1, kernel_size) representing the filter.
    """
    is_even = kernel_size % 2 == 0
    half_size = kernel_size // 2

    # Compute Kaiser window parameters
    delta_f = 4 * half_width
    attenuation = 2.285 * (half_size - 1) * math.pi * delta_f + 7.95

    if attenuation > 50.0:
        beta = 0.1102 * (attenuation - 8.7)
    elif attenuation >= 21.0:
        beta = 0.5842 * (attenuation - 21) ** 0.4 + 0.07886 * (attenuation - 21.0)
    else:
        beta = 0.0

    kaiser_window = torch.kaiser_window(kernel_size, beta=beta, periodic=False, dtype=torch.float32)

    # Compute time indices
    if is_even:
        time_indices = torch.arange(-half_size, half_size) + 0.5
    else:
        time_indices = torch.arange(kernel_size) - half_size

    # Compute sinc filter
    if cutoff == 0:
        return torch.zeros((1, 1, kernel_size), dtype=torch.float32)  # Ensures correct shape

    sinc_filter = torch.sinc(2 * cutoff * time_indices)
    normalized_filter = 2 * cutoff * kaiser_window * sinc_filter

    # Normalize to ensure sum = 1 (avoid leakage of constant component)
    normalized_filter /= normalized_filter.sum()

    return normalized_filter.view(1, 1, kernel_size)


class UpSample1d(nn.Module):
    def __init__(self, ratio=2, kernel_size=None):
        super().__init__()
        self.ratio = ratio
        self.kernel_size = int(6 * ratio // 2) * 2 if kernel_size is None else kernel_size
        self.stride = ratio
        self.pad = self.kernel_size // ratio - 1
        self.pad_left = self.pad * self.stride + (self.kernel_size - self.stride) // 2
        self.pad_right = self.pad * self.stride + (self.kernel_size - self.stride + 1) // 2

        filter = kaiser_sinc_filter1d(cutoff=0.5 / ratio, half_width=0.6 / ratio, kernel_size=self.kernel_size)
        self.register_buffer("filter", filter, persistent=False)

    def forward(self, hidden_states):
        channels = hidden_states.shape[1]

        hidden_states = F.pad(hidden_states, (self.pad, self.pad), mode="replicate")
        hidden_states = self.ratio * F.conv_transpose1d(
            hidden_states, self.filter.expand(channels, -1, -1), stride=self.stride, groups=channels
        )
        hidden_states = hidden_states[..., self.pad_left : -self.pad_right]

        return hidden_states


class DownSample1d(nn.Module):
    def __init__(self, ratio=2, kernel_size=None):
        super().__init__()
        cutoff = 0.5 / ratio
        half_width = 0.6 / ratio

        if cutoff < 0.0:
            raise ValueError("Minimum cutoff must be larger than zero.")
        if cutoff > 0.5:
            raise ValueError("A cutoff above 0.5 does not make sense.")

        self.even = kernel_size % 2 == 0
        self.pad_left = kernel_size // 2 - int(self.even)
        self.pad_right = kernel_size // 2
        self.stride = ratio
        filter = kaiser_sinc_filter1d(cutoff, half_width, kernel_size)
        self.register_buffer("filter", filter, persistent=False)

    def forward(self, hidden_states):
        channels = hidden_states.shape[1]
        hidden_states = F.pad(hidden_states, (self.pad_left, self.pad_right), mode="replicate")
        out = F.conv1d(hidden_states, self.filter.expand(channels, -1, -1), stride=self.stride, groups=channels)
        return out


class TorchActivation1d(nn.Module):
    def __init__(
        self,
        activation,
        up_ratio: int = 2,
        down_ratio: int = 2,
        up_kernel_size: int = 12,
        down_kernel_size: int = 12,
    ):
        super().__init__()
        if not callable(activation):
            raise TypeError("Activation function must be callable")
        self.act = activation
        self.upsample = UpSample1d(up_ratio, up_kernel_size)
        self.downsample = DownSample1d(down_ratio, down_kernel_size)

    def forward(self, hidden_states):
        hidden_states = self.upsample(hidden_states)
        hidden_states = self.act(hidden_states)
        hidden_states = self.downsample(hidden_states)

        return hidden_states


class CausalConv1d(nn.Conv1d):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.causal_padding = self.dilation[0] * (self.kernel_size[0] - 1)

    def forward(self, x):
        return self._conv_forward(F.pad(x, [self.causal_padding, 0]), self.weight, self.bias)


class AMPBlock(torch.nn.Module):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3, 5),
        causal_type='1',
    ):
        super().__init__()

        self.convs1 = nn.ModuleList(
            [
                CausalConv1d(
                    channels,
                    channels,
                    kernel_size,
                    1,
                    dilation=dilation[0],
                ),
                CausalConv1d(
                    channels,
                    channels,
                    kernel_size,
                    1,
                    dilation=dilation[1],
                ),
                CausalConv1d(
                    channels,
                    channels,
                    kernel_size,
                    1,
                    dilation=dilation[2],
                ),
            ]
        )

        if causal_type == '1':
            self.convs2 = nn.ModuleList(
                [
                    nn.Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=1,
                        padding=self._get_padding(kernel_size, 1),
                    ),
                    nn.Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=1,
                        padding=self._get_padding(kernel_size, 1),
                    ),
                    nn.Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=1,
                        padding=self._get_padding(kernel_size, 1),
                    ),
                ]
            )
        else:
            self.convs2 = nn.ModuleList(
                [
                    CausalConv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=1,
                    ),
                    CausalConv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=1,
                    ),
                    CausalConv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=1,
                    ),
                ]
            )

        self.num_layers = len(self.convs1) + len(self.convs2)  # total number of conv layers

        self.activations = nn.ModuleList(
            [TorchActivation1d(activation=SnakeBeta(channels)) for _ in range(self.num_layers)]
        )

        if causal_type == '2':
            self.pre_conv = nn.Conv1d(
                                channels,
                                channels,
                                kernel_size,
                                stride=1,
                                padding=self._get_padding(kernel_size, 1),
                            )
            self.pre_act = TorchActivation1d(activation=SnakeBeta(channels))
        else:
            self.pre_conv = nn.Identity()
            self.pre_act = nn.Identity()

    def _get_padding(self, kernel_size, dilation=1):
        return int((kernel_size * dilation - dilation) / 2)

    def forward(self, x):
        hidden_states = self.pre_conv(x)
        hidden_states = self.pre_act(hidden_states)
        acts1, acts2 = self.activations[::2], self.activations[1::2]
        for conv1, conv2, act1, act2 in zip(self.convs1, self.convs2, acts1, acts2):
            hidden_states = act1(hidden_states)
            hidden_states = conv1(hidden_states)
            hidden_states = act2(hidden_states)
            hidden_states = conv2(hidden_states)
            x = x + hidden_states
        return x


@auto_docstring
class Qwen3TTSTokenizerV1DecoderBigVGANModel(Qwen3TTSTokenizerV1DecoderPreTrainedModel):
    config: Qwen3TTSTokenizerV1DecoderBigVGANConfig

    def __init__(self, config: Qwen3TTSTokenizerV1DecoderBigVGANConfig):
        super().__init__(config)
        self.num_residual_blocks = len(config.resblock_kernel_sizes)
        self.num_upsample_layers = len(config.upsample_rates)

        self.conv_pre = nn.Conv1d(config.mel_dim, config.upsample_initial_channel, 5, 1, padding=2)

        # Removing extra ModuleList breaks official state dict
        ups = [
            nn.ModuleList(
                [
                    nn.ConvTranspose1d(
                        config.upsample_initial_channel // (2**layer_idx),
                        config.upsample_initial_channel // (2 ** (layer_idx + 1)),
                        kernel_size,
                        stride,
                        padding=(kernel_size - stride) // 2,
                    )
                ]
            )
            for layer_idx, (stride, kernel_size) in enumerate(zip(config.upsample_rates, config.upsample_kernel_sizes))
        ]
        self.ups = nn.ModuleList(ups)

        self.resblocks = nn.ModuleList(
            [
                AMPBlock(config.upsample_initial_channel // (2 ** (layer_idx + 1)), kernel_size, dilation, '1' if layer_idx > 1 else '2')
                for layer_idx in range(self.num_upsample_layers)
                for kernel_size, dilation in zip(config.resblock_kernel_sizes, config.resblock_dilation_sizes)
            ]
        )

        self.activation_post = TorchActivation1d(
            activation=SnakeBeta(config.upsample_initial_channel // (2**self.num_upsample_layers))
        )
        self.conv_post = nn.Conv1d(
            config.upsample_initial_channel // (2**self.num_upsample_layers), 1, 7, 1, padding=3, bias=False
        )

    def normalize_spectrogram(self, spectrogram, max_value, min_db):
        return torch.clamp((2 * max_value) * ((spectrogram - min_db) / (-min_db)) - max_value, -max_value, max_value)

    def amplitude_to_db(self, amplitude, min_db_level):
        min_level = torch.exp(
            torch.tensor(min_db_level / 20.0 * np.log(10), device=amplitude.device, dtype=amplitude.dtype)
        )
        return 20 * torch.log10(torch.clamp(amplitude, min=min_level))

    def process_mel_spectrogram(self, mel_spectrogram):
        amplitude_spectrum = torch.exp(mel_spectrogram)
        decibel_spectrum = self.amplitude_to_db(amplitude_spectrum, -115) - 20
        return self.normalize_spectrogram(decibel_spectrum, 1, -115)

    def forward(self, mel_spectrogram):
        processed_spectrogram = self.process_mel_spectrogram(mel_spectrogram)
        hidden_representation = self.conv_pre(processed_spectrogram)

        for layer_index in range(self.num_upsample_layers):
            hidden_representation = self.ups[layer_index][0](hidden_representation)
            residual_output = sum(
                self.resblocks[layer_index * self.num_residual_blocks + block_index](hidden_representation)
                for block_index in range(self.num_residual_blocks)
            )
            residual_output = residual_output / self.num_residual_blocks
            hidden_representation = residual_output

        hidden_representation = self.activation_post(hidden_representation)
        output_waveform = self.conv_post(hidden_representation)
        return torch.clamp(output_waveform, min=-1.0, max=1.0).squeeze(1)


@auto_docstring
class Qwen3TTSTokenizerV1DecoderDiTModel(Qwen3TTSTokenizerV1DecoderPreTrainedModel):
    config: Qwen3TTSTokenizerV1DecoderDiTConfig
    _no_split_modules = ["DiTDecoderLayer"]

    def __init__(self, config: Qwen3TTSTokenizerV1DecoderDiTConfig):
        super().__init__(config)
        self.mel_dim = config.mel_dim
        self.repeats = config.repeats
        self.time_embed = DiTTimestepEmbedding(config.hidden_size)

        self.text_embed = DiTCodecEmbedding(config.num_embeds, config.emb_dim, config.repeats)
        self.input_embed = DiTInputEmbedding(config)

        self.rotary_embed = Qwen3TTSTokenizerV1DecoderDiTRotaryEmbedding(config.head_dim)

        self.hidden_size = config.hidden_size
        self.layers = config.num_hidden_layers
        self.block_size = config.block_size
        self.num_attention_heads = config.num_attention_heads

        self.transformer_blocks = nn.ModuleList()
        for i in range(config.num_hidden_layers):
            self.transformer_blocks.append(
                DiTDecoderLayer(
                    config,
                    look_ahead_block=1 if i in config.look_ahead_layers else 0,
                    look_backward_block=1 if i in config.look_backward_layers else 0,
                )
            )

        self.norm_out = AdaLayerNormZero_Final(config.hidden_size)  # final modulation
        self.proj_out = nn.Linear(config.hidden_size, config.mel_dim)

    def _create_block_diff(self, hidden_states):
        batch, seq_len = hidden_states.shape[0], hidden_states.shape[1]
        block_indices = torch.arange(seq_len, device=hidden_states.device) // self.block_size  # [seq_length]

        block_i = block_indices.unsqueeze(1)  # [seq_length, 1]
        block_j = block_indices.unsqueeze(0)  # [1, seq_length]
        block_diff = block_j - block_i  # (n, n)

        return block_diff.expand(batch, self.num_attention_heads, seq_len, seq_len)

    def forward(
        self,
        hidden_states,
        condition_vector,
        speaker_embedding,
        quantized_code,
        time_step,
        drop_audio_conditioning=False,
        drop_code=False,
        apply_cfg=True,
    ):
        batch_size = hidden_states.shape[0] * 2
        if time_step.ndim == 0:
            time_step = time_step.repeat(batch_size)

        # Compute embeddings
        time_embedding = self.time_embed(time_step)
        text_embedding = self.text_embed(quantized_code, drop_code=False if apply_cfg else drop_code)
        text_embedding_unconditioned = self.text_embed(quantized_code, drop_code=True) if apply_cfg else None

        hidden_states = self.input_embed(
            hidden_states,
            speaker_embedding,
            condition_vector,
            text_embedding,
            drop_audio_cond=drop_audio_conditioning,
            code_embed_uncond=text_embedding_unconditioned,
            apply_cfg=apply_cfg,
        )

        # Compute positional encodings
        position_embeddings = self.rotary_embed(hidden_states)
        blockwise_difference = self._create_block_diff(hidden_states)

        # Transformer blocks
        for transformer_block in self.transformer_blocks:
            hidden_states = transformer_block(
                hidden_states,
                time_embedding,
                position_embeddings=position_embeddings,
                block_diff=blockwise_difference,
            )

        hidden_states = self.norm_out(hidden_states, time_embedding)
        output = self.proj_out(hidden_states)

        return output

    def optimized_scale(self, positive_flat, negative_flat):
        # Calculate dot production
        dot_product = torch.sum(positive_flat * negative_flat, dim=1, keepdim=True)
        # Squared norm of uncondition
        squared_norm = torch.sum(negative_flat ** 2, dim=1, keepdim=True) + 1e-8
        # st_star = v_cond^T * v_uncond / ||v_uncond||^2
        st_star = dot_product / squared_norm
        return st_star

    @torch.no_grad()
    def sample(
        self,
        conditioning_vector,
        reference_mel_spectrogram,
        quantized_code,
        num_steps=10,
        guidance_scale=0.5,
        sway_coefficient=-1.0,
    ):
        noise_initialization = torch.randn([quantized_code.shape[0], 30000, self.mel_dim], dtype=reference_mel_spectrogram.dtype)
        maximum_duration = quantized_code.shape[1] * self.repeats
        initial_state = noise_initialization[:, :maximum_duration].to(quantized_code.device)
        conditioning_vector = conditioning_vector.unsqueeze(1).repeat(1, maximum_duration, 1)

        def ode_function(time_step, hidden_states):
            if guidance_scale < 1e-5:
                prediction = self(
                    hidden_states=hidden_states,
                    speaker_embedding=conditioning_vector,
                    condition_vector=reference_mel_spectrogram,
                    quantized_code=quantized_code,
                    time_step=time_step,
                    drop_audio_conditioning=False,
                    drop_code=False,
                )
                return prediction

            model_output = self(
                hidden_states=hidden_states,
                quantized_code=quantized_code,
                speaker_embedding=conditioning_vector,
                condition_vector=reference_mel_spectrogram,
                time_step=time_step,
                apply_cfg=True,
            )
            guided_prediction, null_prediction = torch.chunk(model_output, 2, dim=0)

            return guided_prediction + (guided_prediction - null_prediction) * guidance_scale

        initial_time = 0
        time_embedding = torch.linspace(
            initial_time, 1, num_steps, device=quantized_code.device, dtype=conditioning_vector.dtype
        )

        if sway_coefficient is not None:
            time_embedding += sway_coefficient * (torch.cos(torch.pi / 2 * time_embedding) - 1 + time_embedding)

        values = initial_state.clone()
        for t0, t1 in zip(time_embedding[:-1], time_embedding[1:]):
            dt = t1 - t0
            vt = ode_function(t0, values)
            values = values + vt * dt

        generated_mel_spectrogram = values.permute(0, 2, 1)
        return generated_mel_spectrogram


@auto_docstring
class Qwen3TTSTokenizerV1Decoder(Qwen3TTSTokenizerV1DecoderPreTrainedModel):
    config: Qwen3TTSTokenizerV1DecoderConfig
    base_model_prefix = "model"
    _no_split_modules = ["Qwen3TTSTokenizerV1DecoderDiTModel", "Qwen3TTSTokenizerV1DecoderBigVGANModel"]

    def __init__(self, config: Qwen3TTSTokenizerV1DecoderConfig):
        super().__init__(config)
        attn_impl = config._attn_implementation
        if config._attn_implementation == "flash_attention_2":
            logger.warning_once(
                "Qwen3TTSTokenizerV1Decoder must inference with fp32, but flash_attention_2 only supports fp16 and bf16, "
                "attention implementation of Qwen3TTSTokenizerV1Decoder will fallback to sdpa."
            )
            attn_impl = "sdpa"
        elif config._attn_implementation == "eager":
            logger.warning_once(
                "Qwen3TTSTokenizerV1Decoder does not support eager attention implementation, fall back to sdpa"
            )
            attn_impl = "sdpa"
        self.dit = Qwen3TTSTokenizerV1DecoderDiTModel._from_config(
            config.dit_config, attn_implementation=attn_impl
        )
        self.bigvgan = Qwen3TTSTokenizerV1DecoderBigVGANModel._from_config(
            config.bigvgan_config, attn_implementation=attn_impl
        )

    def forward(
        self,
        code,
        conditioning,
        reference_mel,
        num_steps=10,
        guidance_scale=0.5,
        sway_coefficient=-1.0,
        **kwargs,
    ):
        """Generates a waveform from input code and conditioning parameters."""

        mel_spectrogram = self.dit.sample(
            conditioning,
            reference_mel,
            code,
            num_steps=num_steps,
            guidance_scale=guidance_scale,
            sway_coefficient=sway_coefficient,
        )

        waveform = self.bigvgan(mel_spectrogram)

        return waveform


class Qwen3TTSTokenizerV1Encoder(Qwen3TTSTokenizerV1EncoderPreTrainedModel):
    config: Qwen3TTSTokenizerV1EncoderConfig
    def __init__(self, config: Qwen3TTSTokenizerV1EncoderConfig):
        super().__init__(config)

        self.tokenizer = WhisperEncoderVQ(
            n_mels=config.n_mels,
            n_ctx=config.n_ctx,
            n_state=config.n_state,
            n_head=config.n_head,
            n_layer=config.n_layer,
            n_window=config.n_window,
            output_dim=config.output_dim,
            grad_checkpointing=config.grad_checkpointing,
            enable_mp=config.enable_mp,
            audio_sequence_parallel=config.audio_sequence_parallel,
            audio_vq_type=config.audio_vq_type,
            audio_vq_layers=config.audio_vq_layers,
            audio_vq_codebook_size=config.audio_vq_codebook_size,
            audio_vq_codebook_dim=config.audio_vq_codebook_dim,
            audio_vq_pe=config.audio_vq_pe,
            audio_vq_ds_rate=config.audio_vq_ds_rate,
        )

        self.padding = True
        self.audio_vq_ds_rate = self.tokenizer.audio_vq_ds_rate

    def speech2mel(self, speechs):
        mels = [
            get_mel_audio(
                speech, padding = self.padding, audio_vq_ds_rate = self.audio_vq_ds_rate
            ).to(speech.dtype).to(self.tokenizer.conv1.weight.device)
            for speech in speechs
        ]
        return mels

    def mel2code(self, mels):
        audio_mellens = [mel.size(-1) for mel in mels]
        audio_aftercnnlens = [get_T_after_cnn(T) for T in audio_mellens]
        audio_seqlens = [T + 2 for T in audio_aftercnnlens]

        with torch.no_grad():
            _, indices = self.tokenizer(
                x_list = mels, 
                audio_mellens = audio_mellens, 
                audio_aftercnnlens = audio_aftercnnlens, 
                audio_seqlens = audio_seqlens, 
                return_indices=True,
            )
        
        indice_lens = [T // self.tokenizer.audio_vq_ds_rate for T in audio_aftercnnlens]
        indices  = pad_sequence(torch.split(indices, indice_lens), batch_first=True, padding_value=0)

        return indices, indice_lens

    def quantize_speech(self, speechs):
        mels = self.speech2mel(speechs)
        indices, indice_lens = self.mel2code(mels)
        return indices, indice_lens


@auto_docstring
class Qwen3TTSTokenizerV1PreTrainedModel(PreTrainedModel):
    config: Qwen3TTSTokenizerV1Config
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _skip_keys_device_placement = "past_key_values"
    _supports_flash_attn = True
    _supports_sdpa = True
    _can_compile_fullgraph = False
    _supports_attention_backend = True


@auto_docstring(
    custom_intro="""
    The Qwen3TTSTokenizerV1 model.
    """
)
class Qwen3TTSTokenizerV1Model(Qwen3TTSTokenizerV1PreTrainedModel):
    def __init__(self, config: Qwen3TTSTokenizerV1Config):
        super().__init__(config)
        self.config = config

        self.input_sample_rate = config.input_sample_rate
        self.output_sample_rate = config.output_sample_rate

        self.decode_upsample_rate = config.decode_upsample_rate
        self.encode_downsample_rate = config.encode_downsample_rate

        self.encoder = Qwen3TTSTokenizerV1Encoder._from_config(self.config.encoder_config)
        self.decoder = Qwen3TTSTokenizerV1Decoder._from_config(self.config.decoder_config)

        self.encoder_xvector_extractor = None

        self.post_init()
    
    def load_encoder_xvector_extractor(self, model_path):
        self.encoder_xvector_extractor = XVectorExtractor(model_path)
    
    def get_model_type(self):
        return self.config.model_type
    
    def get_input_sample_rate(self):
        return self.input_sample_rate
    
    def get_output_sample_rate(self):
        return self.output_sample_rate
    
    def get_encode_downsample_rate(self):
        return self.encode_downsample_rate
    
    def get_decode_upsample_rate(self):
        return self.decode_upsample_rate
    
    @classmethod
    def from_pretrained(
        cls,
        pretrained_model_name_or_path,
        *model_args,
        config=None,
        cache_dir=None,
        ignore_mismatched_sizes=False,
        force_download=False,
        local_files_only=False,
        token=None,
        revision="main",
        use_safetensors=None,
        weights_only=True,
        **kwargs,
    ):
        model = super().from_pretrained(
            pretrained_model_name_or_path,
            *model_args,
            config=config,
            cache_dir=cache_dir,
            ignore_mismatched_sizes=ignore_mismatched_sizes,
            force_download=force_download,
            local_files_only=local_files_only,
            token=token,
            revision=revision,
            use_safetensors=use_safetensors,
            weights_only=weights_only,
            **kwargs,
        )
        encoder_xvector_extractor_path = cached_file(
            pretrained_model_name_or_path,
            "campplus.onnx",
            subfolder=kwargs.pop("subfolder", None),
            cache_dir=kwargs.pop("cache_dir", cache_dir),
            force_download=kwargs.pop("force_download", force_download),
            proxies=kwargs.pop("proxies", None),
            resume_download=kwargs.pop("resume_download", None),
            local_files_only=kwargs.pop("local_files_only", local_files_only),
            token=kwargs.pop("use_auth_token", token),
            revision=kwargs.pop("revision", revision),
        )
        if encoder_xvector_extractor_path is None:
            raise ValueError(f"""{pretrained_model_name_or_path}/{encoder_xvector_extractor_path} not exists""")
        model.load_encoder_xvector_extractor(encoder_xvector_extractor_path)

        return model

    def encode(     
        self,
        input_values: torch.Tensor,
        padding_mask: Optional[torch.Tensor] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[tuple[torch.Tensor, Optional[torch.Tensor]], Qwen3TTSTokenizerV1EncoderOutput]:
        """
        Encodes the input audio waveform into discrete codes.

        Args:
            input_values (`torch.Tensor` of shape `(batch_size, sequence_length)`):
                Float values of the input audio waveform.
            padding_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`):
                Indicates which inputs are to be ignored due to padding, where elements are either 1 for *not masked* or 0
                for *masked*.
            return_dict (`bool`, *optional*):
                Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
        """
        return_dict = return_dict if return_dict is not None else self.config.return_dict

        wavs = [value[:mask.sum()] for value, mask in zip(input_values, padding_mask)]

        codes, codes_lens = self.encoder.quantize_speech(wavs)
        codes = [c[:l] for c, l in zip(codes, codes_lens)]

        xvectors = []
        ref_mels = []
        for wav in wavs:
            xvector, ref_mel = self.encoder_xvector_extractor.extract_code(wav.cpu().numpy())
            xvector = torch.tensor(xvector).to(wav.dtype).to(wav.device)
            ref_mel = torch.tensor(ref_mel).to(wav.dtype).to(wav.device)
            xvectors.append(xvector)
            ref_mels.append(ref_mel)

        if not return_dict:
            return (
                codes,
                xvectors,
                ref_mels
            )

        return Qwen3TTSTokenizerV1EncoderOutput(codes, xvectors, ref_mels)

    def decode(
        self,
        audio_codes: torch.Tensor,
        xvectors: torch.Tensor,
        ref_mels: torch.Tensor,
        return_dict: Optional[bool] = None,
    ) -> Union[tuple[torch.Tensor, torch.Tensor], Qwen3TTSTokenizerV1DecoderOutput]:
        """
        Decodes the given frames into an output audio waveform.

        Note that the output might be a bit bigger than the input. In that case, any extra steps at the end can be
        trimmed.

        Args:
            audio_codes (`torch.LongTensor`  of shape `(batch_size, codes_length)`, *optional*):
                Discret code embeddings computed using `model.encode`.
            xvectors (`torch.FloatTensor` of shape `(batch_size, xvector_dim)`, *optional*):
                X-vector embeddings computed using `model.encode`.
            ref_mels (`torch.FloatTensor` of shape `(batch_size, mel_length, mel_dim)`, *optional*):
                Reference mel spectrogram computed using `model.encode`.
            return_dict (`bool`, *optional*):
                Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.

        """
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        audio_lengths = (audio_codes > -1).sum(1) * self.decode_upsample_rate

        audio_codes = torch.clamp(audio_codes, min=0)
        audio_values = self.decoder(code=audio_codes,
                                    reference_mel=ref_mels,
                                    conditioning=xvectors)
        
        audio_values = [a[:l] for a, l in zip(audio_values, audio_lengths)]

        if not return_dict:
            return (
                audio_values,
            )

        return Qwen3TTSTokenizerV1DecoderOutput(audio_values)


__all__ = ["Qwen3TTSTokenizerV1Model", "Qwen3TTSTokenizerV1PreTrainedModel"]
