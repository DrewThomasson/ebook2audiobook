# Breeze model implementation adapted from Hugging Face Transformers.
#
# coding=utf-8
# Copyright 2025 Sesame and The HuggingFace Inc. team. All rights reserved.
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

from __future__ import annotations

from collections.abc import Callable

from dataclasses import dataclass

import torch
from torch import nn
from transformers.activations import ACT2FN
from transformers.cache_utils import Cache, DynamicCache
from transformers.generation import GenerationMixin
from transformers.integrations import use_kernel_forward_from_hub
from transformers.masking_utils import create_causal_mask
from transformers.modeling_layers import GradientCheckpointingLayer
from transformers.modeling_outputs import (
    BaseModelOutputWithPast,
    CausalLMOutputWithPast,
)
from transformers.modeling_rope_utils import ROPE_INIT_FUNCTIONS, dynamic_rope_update
from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS, PreTrainedModel
from transformers.models.auto import AutoModel
from transformers.processing_utils import Unpack
from transformers.utils import (
    ModelOutput,
    TransformersKwargs,
    auto_docstring,
    can_return_tuple,
    logging,
)
from transformers.utils.deprecation import deprecate_kwarg

from .breeze_config import BreezeConfig, BreezeDepthDecoderConfig
from .generation_breeze import BreezeGenerationMixin

logger = logging.get_logger(__name__)


def _resolve_text_encoder_attn_implementation(config) -> str:
    """Honor an explicit top-level attention choice before checkpoint preference."""
    caller_attn_implementation = getattr(config, "_attn_implementation", None)
    if caller_attn_implementation is not None:
        return caller_attn_implementation

    preferred_attn_implementation = getattr(
        config.text_encoder_config,
        "preferred_attn_implementation",
        None,
    )
    return preferred_attn_implementation or "flash_attention_2"


@dataclass
@auto_docstring(
    custom_intro="""
    Base class for the model autoregressive outputs.
    """
)
class BreezeOutputWithPast(ModelOutput):
    r"""
    loss (`torch.FloatTensor` of shape `(1,)`, *optional*, returned when `labels` is provided):
        Language modeling loss (for next-token prediction).
    logits (`torch.FloatTensor` of shape `(batch_size, sequence_length, config.vocab_size)`):
        Prediction scores of the language modeling head (scores for each vocabulary token before SoftMax).
    past_key_values (`Cache`, *optional*, returned when `use_cache=True` is passed or when `config.use_cache=True`):
        Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of shape
        `(batch_size, num_heads, sequence_length, embed_size_per_head)`)

        Contains pre-computed hidden-states (key and values in the self-attention blocks) that can be used (see
        `past_key_values` input) to speed up sequential decoding.
    depth_decoder_loss (`torch.FloatTensor` of shape `(1,)`, *optional*, returned when `labels` is provided):
        Language modeling loss (for next-token prediction) of the depth decoder model.
    depth_decoder_logits (`torch.FloatTensor` of shape `(batch_size, sequence_length, config.vocab_size)`):
        Prediction scores of the depth decoder (scores for each vocabulary token before SoftMax).
    depth_decoder_past_key_values (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `use_cache=True` is passed or when `config.use_cache=True`):
        Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of shape
        `(batch_size, num_heads, sequence_length, embed_size_per_head)`)
    depth_decoder_hidden_states (`tuple(torch.FloatTensor)`, *optional*, returned when `output_hidden_states=True` is passed or when `config.output_hidden_states=True`):
        Tuple of `torch.FloatTensor` (one for the output of the embeddings, if the model has an embedding layer, +
        one for the output of each layer) of shape `(batch_size, sequence_length, hidden_size)`.

        Hidden-states of the model at the output of each layer plus the optional initial embedding outputs.
    depth_decoder_attentions (`tuple(torch.FloatTensor)`, *optional*, returned when `output_attentions=True` is passed or when `config.output_attentions=True`):
        Tuple of `torch.FloatTensor` (one for each layer) of shape `(batch_size, num_heads, sequence_length,
        sequence_length)`.
    backbone_loss (`torch.FloatTensor` of shape `(1,)`, *optional*, returned when `labels` is provided):
        Language modeling loss (for next-token prediction) of the backbone model.
    """

    loss: torch.FloatTensor | None = None
    logits: torch.FloatTensor = None
    past_key_values: tuple[tuple[torch.FloatTensor]] | None = None
    hidden_states: tuple[torch.FloatTensor, ...] | None = None
    attentions: tuple[torch.FloatTensor, ...] | None = None
    depth_decoder_loss: torch.FloatTensor | None = None
    depth_decoder_logits: torch.FloatTensor = None
    depth_decoder_past_key_values: tuple[tuple[torch.FloatTensor]] | None = None
    depth_decoder_hidden_states: tuple[torch.FloatTensor, ...] | None = None
    depth_decoder_attentions: tuple[torch.FloatTensor, ...] | None = None
    backbone_loss: torch.FloatTensor | None = None


@use_kernel_forward_from_hub("RMSNorm")
class BreezeRMSNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        """
        BreezeRMSNorm is equivalent to T5LayerNorm
        """
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps

    def forward(self, hidden_states):
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight * hidden_states.to(input_dtype)

    def extra_repr(self):
        return f"{tuple(self.weight.shape)}, eps={self.variance_epsilon}"


class BreezeRotaryEmbedding(nn.Module):
    inv_freq: torch.Tensor  # fix linting for `register_buffer`

    def __init__(self, config: BreezeConfig, device=None):
        super().__init__()
        # BC: "rope_type" was originally "type"
        if hasattr(config, "rope_scaling") and isinstance(config.rope_scaling, dict):
            self.rope_type = config.rope_scaling.get(
                "rope_type", config.rope_scaling.get("type")
            )
        else:
            self.rope_type = "default"
        self.max_seq_len_cached = config.max_position_embeddings
        self.original_max_seq_len = config.max_position_embeddings

        self.config = config
        self.rope_init_fn = ROPE_INIT_FUNCTIONS[self.rope_type]

        inv_freq, self.attention_scaling = self.rope_init_fn(self.config, device)
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        self.original_inv_freq = self.inv_freq

    @torch.no_grad()
    @dynamic_rope_update  # power user: used with advanced RoPE types (e.g. dynamic rope)
    def forward(self, x, position_ids):
        inv_freq_expanded = (
            self.inv_freq[None, :, None]
            .float()
            .expand(position_ids.shape[0], -1, 1)
            .to(x.device)
        )
        position_ids_expanded = position_ids[:, None, :].float()

        device_type = (
            x.device.type
            if isinstance(x.device.type, str) and x.device.type != "mps"
            else "cpu"
        )
        with torch.autocast(device_type=device_type, enabled=False):  # Force float32
            freqs = (
                inv_freq_expanded.float() @ position_ids_expanded.float()
            ).transpose(1, 2)
            emb = torch.cat((freqs, freqs), dim=-1)
            cos = emb.cos() * self.attention_scaling
            sin = emb.sin() * self.attention_scaling

        return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)


class BreezeMLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.intermediate_size = config.intermediate_size
        self.gate_proj = nn.Linear(
            self.hidden_size, self.intermediate_size, bias=config.mlp_bias
        )
        self.up_proj = nn.Linear(
            self.hidden_size, self.intermediate_size, bias=config.mlp_bias
        )
        self.down_proj = nn.Linear(
            self.intermediate_size, self.hidden_size, bias=config.mlp_bias
        )
        self.act_fn = ACT2FN[config.hidden_act]

    def forward(self, x):
        down_proj = self.down_proj(self.act_fn(self.gate_proj(x)) * self.up_proj(x))
        return down_proj


def rotate_half(x):
    """Rotates half the hidden dims of the input."""
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)


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
    cos = cos.unsqueeze(unsqueeze_dim)
    sin = sin.unsqueeze(unsqueeze_dim)
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed


def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    """
    This is the equivalent of torch.repeat_interleave(x, dim=1, repeats=n_rep). The hidden states go from (batch,
    num_key_value_heads, seqlen, head_dim) to (batch, num_attention_heads, seqlen, head_dim)
    """
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1:
        return hidden_states
    hidden_states = hidden_states[:, :, None, :, :].expand(
        batch, num_key_value_heads, n_rep, slen, head_dim
    )
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)


def eager_attention_forward(
    module: nn.Module,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attention_mask: torch.Tensor | None,
    scaling: float,
    dropout: float = 0.0,
    **kwargs: Unpack[TransformersKwargs],
):
    key_states = repeat_kv(key, module.num_key_value_groups)
    value_states = repeat_kv(value, module.num_key_value_groups)

    attn_weights = torch.matmul(query, key_states.transpose(2, 3)) * scaling
    if attention_mask is not None:
        causal_mask = attention_mask[:, :, :, : key_states.shape[-2]]
        attn_weights = attn_weights + causal_mask

    attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(
        query.dtype
    )
    attn_weights = nn.functional.dropout(
        attn_weights, p=dropout, training=module.training
    )
    attn_output = torch.matmul(attn_weights, value_states)
    attn_output = attn_output.transpose(1, 2).contiguous()

    return attn_output, attn_weights


class BreezeAttention(nn.Module):
    """Multi-headed attention from 'Attention Is All You Need' paper"""

    def __init__(self, config: BreezeConfig, layer_idx: int):
        super().__init__()
        self.config = config
        self.layer_idx = layer_idx
        self.head_dim = getattr(
            config, "head_dim", config.hidden_size // config.num_attention_heads
        )
        self.num_key_value_groups = (
            config.num_attention_heads // config.num_key_value_heads
        )
        self.scaling = self.head_dim**-0.5
        self.attention_dropout = config.attention_dropout
        self.is_causal = True

        self.q_proj = nn.Linear(
            config.hidden_size,
            config.num_attention_heads * self.head_dim,
            bias=config.attention_bias,
        )
        self.k_proj = nn.Linear(
            config.hidden_size,
            config.num_key_value_heads * self.head_dim,
            bias=config.attention_bias,
        )
        self.v_proj = nn.Linear(
            config.hidden_size,
            config.num_key_value_heads * self.head_dim,
            bias=config.attention_bias,
        )
        self.o_proj = nn.Linear(
            config.num_attention_heads * self.head_dim,
            config.hidden_size,
            bias=config.attention_bias,
        )

    @deprecate_kwarg("past_key_value", new_name="past_key_values", version="4.58")
    def forward(
        self,
        hidden_states: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        attention_mask: torch.Tensor | None,
        past_key_values: Cache | None = None,
        cache_position: torch.LongTensor | None = None,
        **kwargs: Unpack[TransformersKwargs],
    ) -> tuple[torch.Tensor, torch.Tensor]:
        input_shape = hidden_states.shape[:-1]
        hidden_shape = (*input_shape, -1, self.head_dim)

        query_states = self.q_proj(hidden_states).view(hidden_shape).transpose(1, 2)
        key_states = self.k_proj(hidden_states).view(hidden_shape).transpose(1, 2)
        value_states = self.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)

        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(
            query_states, key_states, cos, sin
        )

        if past_key_values is not None:
            # sin and cos are specific to RoPE models; cache_position needed for the static cache
            cache_kwargs = {"sin": sin, "cos": cos, "cache_position": cache_position}
            key_states, value_states = past_key_values.update(
                key_states, value_states, self.layer_idx, cache_kwargs
            )

        attention_interface: Callable = eager_attention_forward
        if self.config._attn_implementation != "eager":
            attention_interface = ALL_ATTENTION_FUNCTIONS[
                self.config._attn_implementation
            ]

        attn_output, attn_weights = attention_interface(
            self,
            query_states,
            key_states,
            value_states,
            attention_mask,
            dropout=0.0 if not self.training else self.attention_dropout,
            scaling=self.scaling,
            **kwargs,
        )

        attn_output = attn_output.reshape(*input_shape, -1).contiguous()
        attn_output = self.o_proj(attn_output)
        return attn_output, attn_weights


class BreezeDecoderLayer(GradientCheckpointingLayer):
    def __init__(self, config: BreezeConfig, layer_idx: int):
        super().__init__()
        self.hidden_size = config.hidden_size

        self.self_attn = BreezeAttention(config=config, layer_idx=layer_idx)

        self.mlp = BreezeMLP(config)
        self.input_layernorm = BreezeRMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )
        self.post_attention_layernorm = BreezeRMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )

    @deprecate_kwarg("past_key_value", new_name="past_key_values", version="4.58")
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.LongTensor | None = None,
        past_key_values: Cache | None = None,
        use_cache: bool | None = False,
        cache_position: torch.LongTensor | None = None,
        position_embeddings: tuple[torch.Tensor, torch.Tensor] | None = None,  # necessary, but kept here for BC
        **kwargs: Unpack[TransformersKwargs],
    ) -> torch.Tensor:
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        # Self Attention
        hidden_states, _ = self.self_attn(
            hidden_states=hidden_states,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            use_cache=use_cache,
            cache_position=cache_position,
            position_embeddings=position_embeddings,
            **kwargs,
        )
        hidden_states = residual + hidden_states

        # Fully Connected
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states
        return hidden_states


@auto_docstring(
    custom_intro="""
    The bare Breeze Model outputting raw hidden-states without any specific head on top.
    """
)
@auto_docstring
class BreezePreTrainedModel(PreTrainedModel):
    config_class = BreezeConfig
    config: BreezeConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _no_split_modules = ["BreezeDecoderLayer"]
    _skip_keys_device_placement = ["past_key_values"]
    _supports_flash_attn = True
    _supports_sdpa = True
    # does not because of Mimi codec model
    # _supports_flex_attn = True

    _can_compile_fullgraph = True
    _supports_attention_backend = True
    _can_record_outputs = {
        "hidden_states": BreezeDecoderLayer,
        "attentions": BreezeAttention,
    }

    def _init_weights(self, module):
        super()._init_weights(module)
        if isinstance(module, BreezeCodebooksHead):
            num_codebooks = module.num_codebooks
            for i in range(num_codebooks - 1):
                module.weight.data[i].normal_(
                    mean=0.0, std=self.config.initializer_range
                )


@auto_docstring
class BreezeDepthDecoderModel(BreezePreTrainedModel):
    config: BreezeDepthDecoderConfig

    def __init__(self, config):
        super().__init__(config)
        self.padding_idx = config.pad_token_id
        self.vocab_size = config.vocab_size
        if hasattr(config, "audio_embed_size") and config.audio_embed_size:
            self.audio_embed_size = config.audio_embed_size
        else:
            self.audio_embed_size = config.backbone_hidden_size
        self.embed_tokens = nn.Embedding(
            (config.num_codebooks * config.vocab_size), self.audio_embed_size
        )
        self.layers = nn.ModuleList(
            [
                BreezeDecoderLayer(config, layer_idx)
                for layer_idx in range(config.num_hidden_layers)
            ]
        )
        self.norm = BreezeRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.rotary_emb = BreezeRotaryEmbedding(config=config)
        self.gradient_checkpointing = False
        self.inputs_embeds_projector = nn.Linear(
            self.audio_embed_size, config.hidden_size, bias=False
        )

        if config.backbone_hidden_size != self.audio_embed_size:
            self.backbone_hidden_state_projector = nn.Linear(
                config.backbone_hidden_size, self.audio_embed_size, bias=False
            )
        else:
            self.backbone_hidden_state_projector = None

        # Initialize weights and apply final processing
        self.post_init()

    @auto_docstring
    def forward(
        self,
        input_ids: torch.LongTensor = None,
        backbone_last_hidden_state: torch.FloatTensor | None = None,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.LongTensor | None = None,
        past_key_values: Cache | None = None,
        inputs_embeds: torch.FloatTensor | None = None,
        use_cache: bool | None = None,
        cache_position: torch.LongTensor | None = None,
        **kwargs: Unpack[TransformersKwargs],
    ) -> tuple | BaseModelOutputWithPast:
        r"""
        backbone_last_hidden_state (`torch.FloatTensor` of shape `(batch_size, backbone_hidden_size)`, *optional*):
            The last hidden state of the backbone model. Such input is required when the first codebook token (the one generated by the backbone model)
            is provided in the `input_ids` argument.
        """
        if position_ids is not None and not torch.compiler.is_compiling():
            logger.warning_once(
                "Custom `position_ids` were provided but will be ignored. Breeze depth decoder automatically determines position_ids "
                "from `cache_position` and as it requires them to be identical across the batch, the provided position_ids will be ignored."
            )
            position_ids = None
        if (input_ids is None) ^ (inputs_embeds is not None):
            raise ValueError(
                "You must specify exactly one of input_ids or inputs_embeds."
            )

        if use_cache and past_key_values is None:
            past_key_values = DynamicCache(config=self.config)

        if cache_position is None:
            past_seen_tokens = (
                past_key_values.get_seq_length() if past_key_values is not None else 0
            )
            inputs_seq_length = (
                inputs_embeds.shape[1]
                if inputs_embeds is not None
                else input_ids.shape[1]
            )
            device = (
                inputs_embeds.device if inputs_embeds is not None else input_ids.device
            )
            cache_position = torch.arange(
                past_seen_tokens, past_seen_tokens + inputs_seq_length, device=device
            )

        if inputs_embeds is None:
            codebook_idxs = torch.clamp(cache_position - 1, min=0)
            offset = codebook_idxs * self.vocab_size
            inputs_embeds = self.embed_tokens(input_ids + offset)

            input_ids_are_first_codebook = cache_position[0] == 0
            if backbone_last_hidden_state is not None:
                if self.backbone_hidden_state_projector is not None:
                    inputs_embeds[:, 0] = self.backbone_hidden_state_projector(
                        backbone_last_hidden_state
                    )
                else:
                    inputs_embeds[:, 0] = backbone_last_hidden_state
            else:
                if not torch.compiler.is_compiling() and input_ids_are_first_codebook:
                    logger.warning(
                        "When the first codebook token is provided, `backbone_last_hidden_state` should also be provided for correct inference."
                    )

        inputs_embeds = self.inputs_embeds_projector(inputs_embeds)

        causal_mask = create_causal_mask(
            config=self.config,
            input_embeds=inputs_embeds,
            attention_mask=attention_mask,
            cache_position=cache_position,
            past_key_values=past_key_values,
            position_ids=position_ids,
        )

        hidden_states = inputs_embeds

        # create position embeddings to be shared across the decoder layers
        position_ids = cache_position.unsqueeze(0)
        position_embeddings = self.rotary_emb(hidden_states, position_ids)

        for decoder_layer in self.layers[: self.config.num_hidden_layers]:
            hidden_states = decoder_layer(
                hidden_states,
                attention_mask=causal_mask,
                position_ids=position_ids,
                past_key_values=past_key_values,
                use_cache=use_cache,
                cache_position=cache_position,
                position_embeddings=position_embeddings,
                **kwargs,
            )

        hidden_states = self.norm(hidden_states)
        return BaseModelOutputWithPast(
            last_hidden_state=hidden_states,
            past_key_values=past_key_values if use_cache else None,
        )


class BreezeCodebooksHead(nn.Module):
    def __init__(self, hidden_size, num_codebooks, vocab_size):
        super().__init__()
        self.num_codebooks = num_codebooks
        self.weight = nn.Parameter(
            torch.empty(self.num_codebooks - 1, hidden_size, vocab_size)
        )

    def forward(self, hidden_states, cache_position=None):
        if cache_position is None:
            seq_length = hidden_states.shape[1]
            codebook_weight = self.weight[torch.arange(seq_length)]
        else:
            codebook_idxs = cache_position - 1
            codebook_weight = self.weight[codebook_idxs]

        hidden_states = [
            nn.functional.linear(
                hidden_states[:, codebook_idx, :], codebook_weight[codebook_idx].T
            )
            for codebook_idx in range(codebook_weight.shape[0])
        ]
        hidden_states = torch.stack(hidden_states, dim=1)

        return hidden_states

    # 重写 extra_repr 方法以显示参数细节
    def extra_repr(self):
        return f"weight_shape={list(self.weight.shape)}, num_codebooks={self.num_codebooks}"


@auto_docstring(
    custom_intro="""
    The BreezeDepthDecoder Model transformer, with a [`BreezeCodebooksHead`] on top,
    which can be seen a position-specific language modeling head, allowing to use a different linear layer for each codebook
    (e.g. position 0 is the first codebook and uses the first codebook head, etc.)
    """
)
class BreezeDepthDecoderForCausalLM(BreezePreTrainedModel, GenerationMixin):
    _tied_weights_keys = None
    _tp_plan = None
    _pp_plan = None

    def __init__(self, config):
        super().__init__(config)
        self.model = BreezeDepthDecoderModel(config)
        self.vocab_size = config.vocab_size
        self.codebooks_head = BreezeCodebooksHead(
            config.hidden_size, config.num_codebooks, config.vocab_size
        )

        # Compute per-codebook loss weights
        # The depth decoder predicts num_codebooks-1 codebooks (31 for default config)
        # We distribute weights by prepending a virtual codebook to make division even
        codebook_loss_weights_list = getattr(config, "codebook_loss_weights", [1.0])
        num_depth_codebooks = config.num_codebooks - 1  # 31 for default 32 codebooks
        num_weights = len(codebook_loss_weights_list)
        num_codebooks_with_virtual = num_depth_codebooks + 1
        codebooks_per_weight = num_codebooks_with_virtual // num_weights
        weights_expanded = []
        for weight in codebook_loss_weights_list:
            weights_expanded.extend([weight] * codebooks_per_weight)
        weights_expanded = weights_expanded[1:]
        self.codebook_loss_weights = weights_expanded

        # Initialize weights and apply final processing
        self.post_init()

    @can_return_tuple
    @auto_docstring
    def forward(
        self,
        input_ids: torch.LongTensor = None,
        backbone_last_hidden_state: torch.FloatTensor | None = None,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.LongTensor | None = None,
        past_key_values: Cache | list[torch.FloatTensor] | None = None,
        inputs_embeds: torch.FloatTensor | None = None,
        labels: torch.LongTensor | None = None,
        use_cache: bool | None = None,
        cache_position: torch.LongTensor | None = None,
        logits_to_keep: int | torch.Tensor = 0,
        **kwargs: Unpack[TransformersKwargs],
    ) -> tuple | CausalLMOutputWithPast:
        r"""
        backbone_last_hidden_state (`torch.FloatTensor` of shape `(batch_size, backbone_hidden_size)`, *optional*):
            The last hidden state of the backbone model. Such input is required when the first codebook token (the one generated by the backbone model)
            is provided in the `input_ids` argument.
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for computing the masked language modeling loss. Indices should either be in `[0, ...,
            config.vocab_size]` or -100 (see `input_ids` docstring). Tokens with indices set to `-100` are ignored
            (masked), the loss is only computed for the tokens with labels in `[0, ..., config.vocab_size]`.
        """
        outputs = self.model(
            input_ids=input_ids,
            backbone_last_hidden_state=backbone_last_hidden_state,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            cache_position=cache_position,
            **kwargs,
        )

        hidden_states = outputs[0]
        # Only compute necessary logits, and do not upcast them to float if we are not computing the loss
        if isinstance(logits_to_keep, int):
            if logits_to_keep == 0:
                # skip idx 0 logits since it's for the concatenated backbone last hidden state
                slice_indices = slice(1, None)
            else:
                slice_indices = slice(-logits_to_keep, None)
        else:
            slice_indices = logits_to_keep

        loss = None
        logits = None

        logits = self.codebooks_head(
            hidden_states[:, slice_indices, :],
            cache_position[slice_indices] if cache_position is not None else None,
        )
        logits = logits.contiguous()

        if labels is not None:
            shift_labels = labels[..., 1:].contiguous()
            loss = self.loss_function(
                logits=logits,
                labels=None,
                vocab_size=self.config.vocab_size,
                shift_labels=shift_labels,
                **kwargs,
            )

        return CausalLMOutputWithPast(
            loss=loss,
            logits=logits,
            past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )

    def prepare_inputs_for_generation(
        self,
        input_ids: torch.LongTensor,
        past_key_values: Cache | None = None,
        attention_mask: torch.LongTensor | None = None,
        inputs_embeds: torch.FloatTensor | None = None,
        cache_position: torch.LongTensor | None = None,
        **kwargs,
    ):
        model_inputs = super().prepare_inputs_for_generation(
            input_ids,
            past_key_values,
            attention_mask,
            inputs_embeds,
            cache_position,
            **kwargs,
        )

        is_first_generation_step = model_inputs["cache_position"][0] == 0
        if not is_first_generation_step:
            model_inputs.pop("backbone_last_hidden_state")

        # breeze depth decoder does not use position_ids
        model_inputs.pop("position_ids")

        return model_inputs


class BreezeBackboneModelEmbeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.hidden_size = config.hidden_size
        if hasattr(config, "audio_embed_size") and config.audio_embed_size:
            self.audio_embed_size = config.audio_embed_size
        else:
            self.audio_embed_size = self.hidden_size
        self.embed_audio_tokens = nn.Embedding(
            (config.num_codebooks * config.vocab_size), self.hidden_size
        )
        if self.audio_embed_size != self.hidden_size:
            self.audio_embeds_projector = nn.Linear(
                self.audio_embed_size, self.hidden_size, bias=False
            )
        else:
            self.audio_embeds_projector = None
        self.register_buffer(
            "audio_tokens_offsets",
            torch.arange(config.num_codebooks) * config.vocab_size,
            persistent=False,
        )

    def forward(self, input_ids):
        input_embeds = self.embed_audio_tokens(input_ids + self.audio_tokens_offsets)
        if self.audio_embeds_projector:
            input_embeds = self.audio_embeds_projector(input_embeds)
        input_embeds = input_embeds.sum(dim=2)
        return input_embeds


@auto_docstring
class BreezeBackboneModel(BreezePreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.padding_idx = config.pad_token_id
        self.vocab_size = config.vocab_size
        self.embed_tokens = BreezeBackboneModelEmbeddings(config)
        self.layers = nn.ModuleList(
            [
                BreezeDecoderLayer(config, layer_idx)
                for layer_idx in range(config.num_hidden_layers)
            ]
        )
        self.norm = BreezeRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.rotary_emb = BreezeRotaryEmbedding(config=config)
        self.gradient_checkpointing = False

        # Initialize weights and apply final processing
        self.post_init()

    @auto_docstring
    def forward(
        self,
        input_ids: torch.LongTensor | None = None,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.LongTensor | None = None,
        past_key_values: Cache | None = None,
        inputs_embeds: torch.FloatTensor | None = None,
        cache_position: torch.LongTensor | None = None,
        use_cache: bool | None = None,
        **kwargs: Unpack[TransformersKwargs],
    ) -> BaseModelOutputWithPast:
        r"""
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length, num_codebooks) or (batch_size, sequence_length)`):
            1. (batch_size, sequence_length): corresponds to the input sequence prepared with the processor from the text prompt. Such input
            requires `input_values` to be provided so that audio can be encoded in codebook tokens and then merged with the text tokens.

            2. (batch_size, sequence_length, num_codebooks): codebook tokens generated during the autoregressive decoding. Such input is not meant to be used by end users.

            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.

            [What are input IDs?](../glossary#input-ids)
        """
        if (input_ids is None) ^ (inputs_embeds is not None):
            raise ValueError(
                "You must specify exactly one of input_ids or inputs_embeds"
            )

        if inputs_embeds is None:
            inputs_embeds: torch.Tensor = self.embed_tokens(input_ids)

        if use_cache and past_key_values is None:
            past_key_values = DynamicCache(config=self.config)

        if cache_position is None:
            past_seen_tokens = (
                past_key_values.get_seq_length() if past_key_values is not None else 0
            )
            cache_position: torch.Tensor = torch.arange(
                past_seen_tokens,
                past_seen_tokens + inputs_embeds.shape[1],
                device=inputs_embeds.device,
            )

        if position_ids is None:
            position_ids = cache_position.unsqueeze(0)

        causal_mask = create_causal_mask(
            config=self.config,
            input_embeds=inputs_embeds,
            attention_mask=attention_mask,
            cache_position=cache_position,
            past_key_values=past_key_values,
            position_ids=position_ids,
        )

        hidden_states = inputs_embeds
        position_embeddings = self.rotary_emb(hidden_states, position_ids)

        for decoder_layer in self.layers[: self.config.num_hidden_layers]:
            hidden_states = decoder_layer(
                hidden_states,
                attention_mask=causal_mask,
                position_ids=position_ids,
                past_key_values=past_key_values,
                cache_position=cache_position,
                position_embeddings=position_embeddings,
                **kwargs,
            )

        hidden_states = self.norm(hidden_states)
        return BaseModelOutputWithPast(
            last_hidden_state=hidden_states,
            past_key_values=past_key_values,
        )


from transformers import AutoConfig, PretrainedConfig


@auto_docstring(
    custom_intro="""
    The Breeze model consists of two llama-like auto-regressive transformer models: a backbone model that predicts the first codebook token and a depth decoder that predicts the other codebook tokens.
    """
)
class BreezeForConditionalGeneration(BreezePreTrainedModel, BreezeGenerationMixin):
    _tied_weights_keys = [
        "backbone_model.embed_tokens.embed_audio_tokens.weight",
        "depth_decoder.model.embed_tokens.weight",
    ]

    def __init__(self, config):
        super().__init__(config)
        self.vocab_size = config.vocab_size
        # Extra backbone EOS class at index vocab_size; audio codebook ids remain [0, vocab_size).
        self.backbone_eos_token_id = config.vocab_size
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size + 1, bias=False)

        # embed_text_tokens needs to include audio special tokens (audio_token_id, audio_eos_token_id)
        # since they appear in input_ids before being replaced with audio embeddings
        # text_vocab_size already includes these tokens after tokenizer extension
        self.embed_text_tokens = nn.Embedding(
            config.text_vocab_size, config.hidden_size
        )

        # Use factory to create backbone (supports breeze/qwen3/llama etc.)
        from .breeze_backbone_factory import BreezeBackboneFactory

        self.backbone_model = BreezeBackboneFactory.create_backbone(config)

        self.depth_decoder = BreezeDepthDecoderForCausalLM._from_config(
            config.depth_decoder_config
        )

        self.codec_model = AutoModel.from_config(config.codec_config)
        # Codec model is always in eval mode (not trainable)
        self.codec_model.eval()
        for param in self.codec_model.parameters():
            param.requires_grad = False

        self.text_encoder_trainable = False
        text_encoder_config = getattr(config, "text_encoder_config", None)
        if text_encoder_config is None:
            self.text_encoder = None
            self.text_encoder_proj = None
        elif isinstance(text_encoder_config, dict):
            config.text_encoder_config = AutoConfig.for_model(**text_encoder_config)
        elif isinstance(config.text_encoder_config, PretrainedConfig):
            config.text_encoder_config = text_encoder_config
        else:
            raise ValueError(
                "text_encoder_config must be None, dict or PretrainedConfig instance"
            )
        if getattr(config, "text_encoder_config", None) is not None:
            self.text_encoder_layer_projs = None
            self.text_encoder_dimfusion_layer_start_idx = getattr(
                config, "text_encoder_dimfusion_layer_start_idx", 1
            )  # 1 feature indicates from layer 1, feature 0 is embedding result
            self.text_encoder_dimfusion_layer_end_idx = getattr(
                config, "text_encoder_dimfusion_layer_end_idx", None
            )  # None indicates up to last layer
            self.text_encoder_dimfusion_fuse_first_layer = getattr(
                config, "text_encoder_dimfusion_fuse_first_layer", False
            )

            self.text_encoder_feature_layer_idx = getattr(
                config, "text_encoder_feature_layer_idx", -1
            )
            if isinstance(self.text_encoder_feature_layer_idx, int):
                self.text_encoder_feature_layer_idx = (
                    self.text_encoder_feature_layer_idx,
                )
            if self.text_encoder_feature_layer_idx != (-1,):
                print(
                    f"  - [BreezeForConditionalGeneration] Text encoder feature layer idx: {self.text_encoder_feature_layer_idx}"
                )

            text_encoder_attn_implementation = (
                _resolve_text_encoder_attn_implementation(config)
            )
            config.text_encoder_config._attn_implementation = (
                text_encoder_attn_implementation
            )
            # Skip random weight initialization since we'll load pretrained weights later
            from transformers.modeling_utils import no_init_weights

            with no_init_weights():
                self.text_encoder = AutoModel.from_config(
                    config.text_encoder_config,
                    attn_implementation=text_encoder_attn_implementation,
                    dtype=torch.bfloat16,
                )

            text_encoder_proj_type = getattr(config, "text_encoder_proj_type", "linear")
            if text_encoder_proj_type == "linear":
                self.text_encoder_proj = nn.Linear(
                    config.text_encoder_config.hidden_size,
                    config.hidden_size,
                    bias=False,
                )
            elif text_encoder_proj_type == "mlp":
                self.text_encoder_proj = nn.Sequential(
                    nn.Linear(
                        config.text_encoder_config.hidden_size,
                        config.hidden_size * 2,
                        bias=False,
                    ),
                    nn.GELU(),
                    nn.Linear(config.hidden_size * 2, config.hidden_size, bias=False),
                )
            elif text_encoder_proj_type == "breeze_text_encoder_adapter":
                from .t5_adapter import BreezeTextEncoderAdapter

                self.text_encoder_proj = BreezeTextEncoderAdapter(config=config)
            elif text_encoder_proj_type == "breeze_dimfusion":
                proj_out_hidden_size = config.hidden_size
                if self.text_encoder_dimfusion_fuse_first_layer:
                    proj_out_hidden_size //= 2
                self.text_encoder_proj = nn.Linear(
                    config.text_encoder_config.hidden_size
                    * len(self.text_encoder_feature_layer_idx),
                    proj_out_hidden_size,
                    bias=True,  # bias=True, follow DimFusion design： https://github.com/huggingface/diffusers/blob/d0ae34d3136f7cb119a66fe0b9d526202343674c/src/diffusers/models/transformers/transformer_bria_fibo.py#L477
                )
                self.text_encoder_layer_projs = nn.ModuleList(
                    [
                        nn.Linear(
                            config.text_encoder_config.hidden_size,
                            config.hidden_size // 2,
                            bias=False,
                        )
                        for _ in range(self.config.num_hidden_layers)
                    ]
                )

                dimfusion_kwargs = {
                    "text_encoder_dimfusion_layer_start_idx": self.text_encoder_dimfusion_layer_start_idx,
                    "text_encoder_dimfusion_layer_end_idx": self.text_encoder_dimfusion_layer_end_idx,
                    "text_encoder_dimfusion_fuse_first_layer": self.text_encoder_dimfusion_fuse_first_layer,
                }
                print(
                    "  - [BreezeForConditionalGeneration] Text encoder DimFusion layer projections created."
                )
                for k, v in dimfusion_kwargs.items():
                    print(f"    - {k}: {v}")
            else:
                raise ValueError(
                    f"Unsupported text_encoder_proj_type: {text_encoder_proj_type}"
                )
            print(
                "  - [BreezeForConditionalGeneration] Text encoder projection type:",
                text_encoder_proj_type,
            )

            requires_grad = getattr(config.text_encoder_config, "requires_grad", False)
            self.text_encoder_trainable = bool(requires_grad)
            if not self.text_encoder_trainable:
                nonzero_dropout_fields = self._get_nonzero_text_encoder_dropout_fields(
                    config.text_encoder_config
                )
                if nonzero_dropout_fields:
                    formatted_fields = ", ".join(
                        f"{name}={value}" for name, value in nonzero_dropout_fields
                    )
                    raise ValueError(
                        "Frozen text_encoder must be deterministic, but its config has non-zero dropout fields: "
                        f"{formatted_fields}. Set train_text_encoder=true or use a text encoder config with dropout=0."
                    )
                self.text_encoder.eval()
            for param in self.text_encoder.parameters():
                param.requires_grad = requires_grad
            import os

            if os.environ.get("RANK", "0") == "0":
                logger.info(
                    f"model.text_encoder initialized with requires_grad={requires_grad}"
                )

        # Disable num_items_in_batch to avoid incorrect loss normalization
        # for depth decoder (which operates on different token counts than backbone)
        self.accepts_loss_kwargs = False

        # Temporarily remove text_encoder before post_init to avoid slow re-initialization
        # (text_encoder weights will be loaded from pretrained checkpoint later)
        _text_encoder = self.text_encoder
        self.text_encoder = None
        self.post_init()
        self.text_encoder = _text_encoder

    def get_input_embeddings(self):
        return self.backbone_model.embed_tokens

    def set_input_embeddings(self, value):
        self.backbone_model.embed_tokens = value

    def _tie_weights(self):
        if self.config.tie_codebooks_embeddings:
            self._tie_or_clone_weights(
                self.backbone_model.embed_tokens.embed_audio_tokens,
                self.depth_decoder.model.embed_tokens,
            )

    @staticmethod
    def _get_nonzero_text_encoder_dropout_fields(text_encoder_config):
        dropout_field_names = (
            "dropout",
            "dropout_rate",
            "attention_dropout",
            "hidden_dropout",
            "hidden_dropout_prob",
            "activation_dropout",
            "classifier_dropout",
            "classifier_dropout_rate",
            "embd_pdrop",
            "resid_pdrop",
        )
        nonzero_fields = []
        for field_name in dropout_field_names:
            value = getattr(text_encoder_config, field_name, None)
            if value is None:
                continue
            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                continue
            if numeric_value != 0.0:
                nonzero_fields.append((field_name, value))
        return nonzero_fields

    def train(self, mode: bool = True):
        """Override train() to keep non-trainable submodules in eval mode."""
        super().train(mode)
        # Always keep codec_model in eval mode
        self.codec_model.eval()
        if getattr(self, "text_encoder", None) is not None and not getattr(
            self, "text_encoder_trainable", False
        ):
            self.text_encoder.eval()
        return self

    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        if kwargs.get("output_loading_info", False):
            model, loading_info = super().from_pretrained(*args, **kwargs)
        else:
            model = super().from_pretrained(*args, **kwargs)

        # copy depth decoder generation conf attr to the depth decoder generation config
        prefix = "depth_decoder_"
        prefix_len = len(prefix)
        depth_decoder_attrs = {
            attr[prefix_len:]: value
            for attr, value in vars(model.generation_config).items()
            if attr.startswith(prefix)
        }

        vars(model.depth_decoder.generation_config).update(
            {"_from_model_config": False, **depth_decoder_attrs}
        )

        # remove the depth decoder generation conf attr from the model generation config
        for attr in depth_decoder_attrs:
            delattr(model.generation_config, prefix + attr)

        if "output_loading_info" in kwargs:
            return model, loading_info
        else:
            return model

    def save_pretrained(self, *args, **kwargs):
        # copy the depth decoder generation config attributes to the model generation config
        prefix = "depth_decoder_"
        depth_decoder_attrs = self.depth_decoder.generation_config.to_diff_dict()
        depth_decoder_attrs.pop("transformers_version", None)
        for attr, value in depth_decoder_attrs.items():
            setattr(self.generation_config, prefix + attr, value)

        super().save_pretrained(*args, **kwargs)

    def gradient_checkpointing_enable(self, *args, **kwargs):
        gradient_checkpointing_kwargs = kwargs.pop("gradient_checkpointing_kwargs", {})
        sub_modules_to_disable_default = [
            # 'codec_model',
            # # 'backbone_model',
            # 'text_encoder',
            # 'text_encoder_proj',
            # 'depth_decoder'
        ]

        if gradient_checkpointing_kwargs is None:
            gradient_checkpointing_kwargs = {}
        sub_modules_to_disable = gradient_checkpointing_kwargs.pop(
            "sub_modules_to_disable", sub_modules_to_disable_default
        )

        # call super first to enable gradient checkpointing
        ret = super().gradient_checkpointing_enable(*args, **kwargs)

        # override sub-modules to disable gradient checkpointing
        sub_modules_to_disable = gradient_checkpointing_kwargs.get(
            "sub_modules_to_disable", sub_modules_to_disable
        )

        # 1. disable gradient checkpointing for specified sub-modules
        import os

        rank = int(os.environ.get("RANK", "0"))
        print0 = lambda *args, **kwargs: print(*args, **kwargs) if rank == 0 else None
        for module_name in sub_modules_to_disable:
            module = getattr(self, module_name, None)
            module_layers = (
                [
                    (name, mod)
                    for name, mod in module.named_modules()
                    if isinstance(mod, GradientCheckpointingLayer)
                ]
                if module is not None
                else []
            )

            if not module_layers:
                print0(
                    f"  - [BreezeForConditionalGeneration] gradient_checkpointing_disable skipped for sub-module: {module_name}"
                )
                continue

            print0(
                f"  - [BreezeForConditionalGeneration] gradient_checkpointing_disable applied for sub-module: {module_name}"
            )
            for layer_name, layer in module_layers:
                layer.gradient_checkpointing = False
                print0(
                    f"    - Disabled gradient checkpointing for layer: {module_name}.{layer_name}"
                )
        return ret

    def _batched_text_encoder_forward(self, segments, output_hidden_states=False):
        """Run text encoder on a list of variable-length token ID tensors using padded batching.

        Args:
            segments: list of 1D tensors, each (seg_len,)

        Returns:
            hidden_states: list of 2D tensors, each (seg_len, hidden) with padding removed
            layer_hidden_states: list of lists, per-segment layer hidden states (each (seg_len, hidden)),
                or None when not requested.
        """
        if not segments:
            return [], []

        if (
            getattr(self, "_fast_text_encoder_cudagraph", False)
            and not output_hidden_states
        ):
            from .text_encoder_graph import TextEncoderGraphCache

            cache = getattr(self, "_fast_text_encoder_graph_cache", None)
            if cache is None:
                cache = TextEncoderGraphCache(self.text_encoder, token_granularity=32)
                self._fast_text_encoder_graph_cache = cache
            return cache(segments)

        device = segments[0].device
        lengths = [s.shape[0] for s in segments]
        feature_layer_idx = self.text_encoder_feature_layer_idx
        if isinstance(feature_layer_idx, int):
            feature_layer_idx = (feature_layer_idx,)
        elif isinstance(feature_layer_idx, list):
            feature_layer_idx = tuple(feature_layer_idx)

        sorted_indices = sorted(range(len(segments)), key=lambda i: lengths[i])
        buckets = []
        current_bucket = []
        current_min_len = None
        for idx in sorted_indices:
            length = lengths[idx]
            if not current_bucket:
                current_bucket = [idx]
                current_min_len = length
            elif length / max(current_min_len, 1) <= 2:
                current_bucket.append(idx)
            else:
                buckets.append(current_bucket)
                current_bucket = [idx]
                current_min_len = length
        if current_bucket:
            buckets.append(current_bucket)

        hidden_states = [None] * len(segments)
        layer_hidden_states = [None] * len(segments) if output_hidden_states else None

        for bucket_indices in buckets:
            bucket_lengths = [lengths[i] for i in bucket_indices]
            max_len = max(bucket_lengths)

            padded_ids = torch.zeros(
                len(bucket_indices), max_len, dtype=segments[0].dtype, device=device
            )
            attn_mask = torch.zeros(
                len(bucket_indices), max_len, dtype=torch.long, device=device
            )
            pos_ids = torch.zeros(
                len(bucket_indices), max_len, dtype=torch.long, device=device
            )
            for bucket_pos, idx in enumerate(bucket_indices):
                length = lengths[idx]
                padded_ids[bucket_pos, :length] = segments[idx]
                attn_mask[bucket_pos, :length] = 1
                pos_ids[bucket_pos, :length] = torch.arange(length, device=device)

            output = self.text_encoder(
                input_ids=padded_ids,
                attention_mask=attn_mask,
                position_ids=pos_ids,
                output_hidden_states=output_hidden_states,
            )

            if feature_layer_idx == (-1,):
                full_hs = output.last_hidden_state
            elif isinstance(feature_layer_idx, tuple):
                if output.hidden_states is None:
                    raise ValueError(
                        "output_hidden_states must be enabled when selecting non-final text encoder layers"
                    )
                full_hs = torch.concat(
                    [output.hidden_states[li] for li in feature_layer_idx], dim=-1
                )
            else:
                raise ValueError(
                    f"Unsupported text_encoder_feature_layer_idx: {feature_layer_idx}"
                )

            for bucket_pos, idx in enumerate(bucket_indices):
                hidden_states[idx] = full_hs[bucket_pos, : lengths[idx]]
            if output.hidden_states is not None:
                all_layer_hs = list(output.hidden_states)
                if layer_hidden_states is None:
                    layer_hidden_states = [None] * len(segments)
                for bucket_pos, idx in enumerate(bucket_indices):
                    layer_hidden_states[idx] = [
                        lhs[bucket_pos, : lengths[idx]] for lhs in all_layer_hs
                    ]

        return hidden_states, layer_hidden_states

    def convert_input_ids_to_embeds(
        self,
        input_ids: torch.Tensor | None = None,
        text_ids_mask: torch.Tensor | None = None,
        text_ids_len: torch.Tensor | None = None,
        attention_mask: torch.Tensor | None = None,
    ):
        assert self.text_encoder is not None, (
            "text_encoder is None, cannot convert input_ids to embeds"
        )
        assert text_ids_mask is not None, (
            "text_ids_mask is None, cannot convert input_ids to embeds"
        )
        assert text_ids_len is not None, (
            "text_ids_len is None, cannot convert input_ids to embeds"
        )

        # Ensure text_ids_len matches mask-derived count (helps catch bad batching)
        total_text_tokens = int(text_ids_mask.sum().item())
        assert total_text_tokens == int(text_ids_len.sum().item()), (
            f"text_ids_mask sum {total_text_tokens} does not match text_ids_len sum {int(text_ids_len.sum().item())}"
        )

        text_ids_len_list = [int(x) for x in text_ids_len.reshape(-1).tolist()]
        text_ids_len_idx = 0

        # == Phase 1: Parse all samples and collect segments ==
        # Keep row-major order so the projected embeddings line up with
        # boolean assignment into inputs_embeds[text_ids_mask].
        all_segment_lengths = []
        all_seg_token_ids = []
        for batch_idx in range(input_ids.shape[0]):
            mask_row = text_ids_mask[batch_idx]
            sample_text_tokens = int(mask_row.sum().item())
            if sample_text_tokens == 0:
                continue

            text_ids = input_ids[batch_idx][mask_row]  # (total_text_len,)
            segment_lengths = []
            running = 0
            while running < sample_text_tokens:
                if text_ids_len_idx >= len(text_ids_len_list):
                    raise ValueError(
                        "text_ids_len exhausted before covering all text tokens in the batch"
                    )
                seg_len = text_ids_len_list[text_ids_len_idx]
                text_ids_len_idx += 1
                if seg_len <= 0:
                    continue
                segment_lengths.append(seg_len)
                running += seg_len
            if running != sample_text_tokens:
                raise ValueError(
                    f"text_ids_len segments sum {running} does not match text_ids_mask sum {sample_text_tokens} for batch index {batch_idx}"
                )

            seg_token_ids = text_ids.split(segment_lengths, dim=0)  # list of 1D tensors
            all_segment_lengths.extend(segment_lengths)
            all_seg_token_ids.extend(seg_token_ids)

        if text_ids_len_idx != len(text_ids_len_list):
            raise ValueError(
                f"Unused text_ids_len entries detected: consumed {text_ids_len_idx} of {len(text_ids_len_list)}"
            )

        # == Phase 2: Text encoder forward ==
        # Batched independent encoding: each text segment is its own row in
        # the padded text-encoder batch. This prevents cross-sample and
        # cross-segment attention contamination under the flattening collator.
        if all_seg_token_ids:
            feature_layer_idx = self.text_encoder_feature_layer_idx
            if isinstance(feature_layer_idx, int):
                feature_layer_idx = (feature_layer_idx,)
            elif isinstance(feature_layer_idx, list):
                feature_layer_idx = tuple(feature_layer_idx)
            needs_layer_hidden_states = (
                self.text_encoder_layer_projs is not None or feature_layer_idx != (-1,)
            )
            seg_hidden_states, seg_layer_hidden_states = (
                self._batched_text_encoder_forward(
                    all_seg_token_ids,
                    output_hidden_states=needs_layer_hidden_states,
                )
            )
            seg_hidden_states = [hs.unsqueeze(0) for hs in seg_hidden_states]
            text_embeds, text_encoder_layer_hidden_states = self._project_segments(
                all_segment_lengths,
                seg_hidden_states,
                seg_layer_hidden_states,
                is_separate=True,
            )
        else:
            text_embeds = torch.empty(
                (0, self.config.hidden_size),
                device=input_ids.device,
                dtype=self.embed_text_tokens.weight.dtype,
            )
            text_encoder_layer_hidden_states = None

        # == Phase 3: Assemble final outputs ==
        # Create inputs_embeds tensor
        inputs_embeds = torch.zeros(
            (input_ids.shape[0], input_ids.shape[1], self.config.hidden_size),
            dtype=text_embeds.dtype,
            device=text_embeds.device,
        )
        inputs_embeds[text_ids_mask] = text_embeds

        return inputs_embeds, text_encoder_layer_hidden_states

    def _project_segments(
        self, segment_lengths, seg_hidden_states, seg_layer_hidden_states, is_separate
    ):
        """Project text encoder hidden states per segment and handle layer projections.

        Args:
            segment_lengths: list of int, length of each segment
            seg_hidden_states: list of (1, seg_len, hidden) tensors
            seg_layer_hidden_states: list of layer hidden state lists per segment.
                - If is_separate=True: each entry is a list of (seg_len, hidden) tensors (one per layer).
                - If is_separate=False: each entry is a list of (1, total_len, hidden) tensors (shared across segments).
            is_separate: whether segments were encoded separately

        Returns:
            text_embeds: (total_text_len, hidden) projected embeddings
            text_encoder_layer_hidden_states: list of (total_text_len, hidden) or None
        """
        projected_segments = []
        for seg_idx, seg_hs in enumerate(seg_hidden_states):
            proj = self.text_encoder_proj
            if isinstance(proj, (nn.Linear, nn.Sequential)):
                projected_segments.append(proj(seg_hs).squeeze(0))
            else:
                seg_pos = torch.arange(seg_hs.shape[1], device=seg_hs.device).unsqueeze(
                    0
                )
                projected_segments.append(
                    proj(inputs_embeds=seg_hs, position_ids=seg_pos).squeeze(0)
                )
        text_embeds = torch.cat(projected_segments, dim=0)

        if self.text_encoder_layer_projs is not None:
            num_layers = len(self.text_encoder_layer_projs)
            projected_layer_hidden_states = []

            for layer_idx in range(num_layers):
                layer_parts = []
                for seg_idx, seg_layer_hs_list in enumerate(seg_layer_hidden_states):
                    selected = seg_layer_hs_list[
                        self.text_encoder_dimfusion_layer_start_idx : self.text_encoder_dimfusion_layer_end_idx
                    ]
                    if len(selected) < num_layers:
                        selected = selected + [selected[-1]] * (
                            num_layers - len(selected)
                        )
                    elif len(selected) > num_layers:
                        selected = selected[-num_layers:]

                    seg_layer_hs = selected[layer_idx]
                    if is_separate:
                        # Already per-segment: (seg_len, hidden) -> (1, seg_len, hidden)
                        seg_layer_hs = seg_layer_hs.unsqueeze(0)
                    else:
                        # Joint encoding: (1, total_len, hidden) -> split -> (1, seg_len, hidden)
                        seg_layer_hs = (
                            seg_layer_hs.squeeze(0)
                            .split(segment_lengths, dim=0)[seg_idx]
                            .unsqueeze(0)
                        )

                    layer_proj = self.text_encoder_layer_projs[layer_idx]
                    layer_parts.append(layer_proj(seg_layer_hs).squeeze(0))
                projected_layer_hidden_states.append(torch.cat(layer_parts, dim=0))

            text_encoder_layer_hidden_states = projected_layer_hidden_states
        else:
            text_encoder_layer_hidden_states = None

        if self.text_encoder_dimfusion_fuse_first_layer:
            assert text_encoder_layer_hidden_states is not None, (
                "text_encoder_layer_hidden_states is None, cannot fuse first layer hidden states"
            )
            layer0_hidden_states = text_encoder_layer_hidden_states[0]
            assert (
                layer0_hidden_states.shape[-1] + text_embeds.shape[-1]
            ) == self.config.hidden_size, (
                f"Dimension mismatch when fusing layer 0 hidden states with text embeddings, but got {layer0_hidden_states.shape[-1]} + {text_embeds.shape[-1]} != {self.config.hidden_size}"
            )
            text_embeds = torch.cat([text_embeds, layer0_hidden_states], dim=-1)

        return text_embeds, text_encoder_layer_hidden_states

    def _merge_input_ids_with_input_values(
        self,
        input_ids: torch.Tensor | None = None,
        input_values: torch.Tensor | None = None,
        labels: torch.Tensor | None = None,
        text_ids_mask: torch.Tensor | None = None,
        text_ids_len: torch.Tensor | None = None,
        attention_mask: torch.Tensor | None = None,
    ) -> torch.Tensor | None:
        """
        Merges the input_ids and input_values to produce a single inputs_embeds tensor:
        1 - Uses pre-encoded codebook tokens from input_values (no codec inference needed).
        2 - Embeds codebook tokens and places them at the correct positions in the inputs_embeds tensor.
        3 - If labels are provided, expands them to match codebook dimensions and position the target codebook tokens in the inputs_embeds tensor.

        Args:
            input_ids (`torch.Tensor` of shape `(batch_size, sequence_length)`):
                The input ids to embed.
            input_values (`torch.Tensor` of shape `(batch_size, audio_sequence_length, num_codebooks)`):
                The pre-encoded audio tokens (RVQ codebook indices).
            labels (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
                Labels for computing the loss.
        """
        text_encoder_layer_hidden_states = None
        if self.text_encoder is not None:
            inputs_embeds, text_encoder_layer_hidden_states = (
                self.convert_input_ids_to_embeds(
                    input_ids,
                    text_ids_mask,
                    text_ids_len,
                    attention_mask=attention_mask,
                )
            )
        else:
            inputs_embeds = self.embed_text_tokens(input_ids)

        if input_values is not None:
            # input_values are already pre-encoded tokens: (batch_size, audio_seq_len, num_codebooks)
            batched_audio_token_ids = input_values

            # Get mask for audio token positions in input_ids
            audio_token_id = self.config.audio_token_id
            audio_token_mask = input_ids == audio_token_id

            # Debug: check if audio tokens are found
            num_audio_tokens = audio_token_mask.sum().item()
            if num_audio_tokens == 0 and input_values is not None:
                # This should not happen - we have audio data but no audio token markers
                unique_ids = torch.unique(input_ids)
                raise RuntimeError(
                    f"Audio token mismatch: Expected audio_token_id={audio_token_id} in input_ids, "
                    f"but found 0 matches. input_values shape: {input_values.shape}. "
                    f"Unique input_ids: {unique_ids.tolist()[:20]}... (showing first 20)"
                )

            # Convert patches tokens to embeddings
            audio_embeds = self.backbone_model.embed_tokens(batched_audio_token_ids)

            # Flatten audio_embeds for assignment to masked positions
            # audio_embeds shape: (batch_size, audio_seq_len, hidden_size)
            # Need to flatten to match the flattened audio_token_mask
            audio_embeds_flat = audio_embeds.reshape(-1, audio_embeds.shape[-1])
            # Ensure dtype matches
            audio_embeds_flat = audio_embeds_flat.to(inputs_embeds.dtype)
            inputs_embeds[audio_token_mask] = audio_embeds_flat

            # same for the audio eos token.
            audio_eos_frame_ids = (
                torch.ones(
                    (1, 1, self.config.num_codebooks),
                    device=input_ids.device,
                    dtype=torch.long,
                )
                * self.config.codebook_eos_token_id
            )
            audio_eos_embeds = self.backbone_model.embed_tokens(
                audio_eos_frame_ids
            ).squeeze(1)
            # Ensure dtype matches
            audio_eos_embeds = audio_eos_embeds.to(inputs_embeds.dtype)

            audio_eos_token_mask = input_ids == self.config.audio_eos_token_id
            inputs_embeds[audio_eos_token_mask] = audio_eos_embeds.repeat(
                audio_eos_token_mask.sum(), 1
            )

            # if the labels are provided, we need to expand the labels to (batch_size, seq_length, num_codebooks)
            if labels is not None:
                labels_expanded = labels.unsqueeze(-1).repeat(
                    1, 1, self.config.num_codebooks
                )
                # Flatten batched_audio_token_ids for assignment to masked positions
                batched_audio_token_ids_flat = batched_audio_token_ids.reshape(
                    -1, batched_audio_token_ids.shape[-1]
                )
                labels_expanded[audio_token_mask] = batched_audio_token_ids_flat
                labels_expanded[audio_eos_token_mask] = -100
                eos_positions = audio_eos_token_mask.nonzero(as_tuple=True)
                labels_expanded[eos_positions[0], eos_positions[1], 0] = (
                    self.backbone_eos_token_id
                )
                # mask depth decoder
                depth_decoder_ignore_frames_mask = labels == -101
                depth_decoder_ignore_frames_mask &= ~audio_eos_token_mask
                depth_decoder_ignore_frames_idxs = (
                    depth_decoder_ignore_frames_mask.nonzero(as_tuple=True)
                )
                # set the first codebook patch to -100 to ignore
                labels_expanded[
                    depth_decoder_ignore_frames_idxs[0],
                    depth_decoder_ignore_frames_idxs[1],
                    1 : self.config.num_codebooks,
                ] = -100
                labels = labels_expanded

        return {
            "inputs_embeds": inputs_embeds,
            "labels": labels,
            "text_encoder_layer_hidden_states": text_encoder_layer_hidden_states,
            "text_ids_mask": text_ids_mask,
        }

    def _get_audio_token_from_batch(self, audio_batch):
        with torch.no_grad():
            print("Encoding audio batch of shape:", audio_batch.shape)
            codec_outputs = self.codec_model.encode(audio_batch.unsqueeze(0))
            codebook_ids = codec_outputs.audio_codes.transpose(1, -1)[0]
        return codebook_ids

    def prepare_inputs_for_generation(
        self,
        input_ids: torch.LongTensor,
        past_key_values: Cache | None = None,
        attention_mask: torch.LongTensor | None = None,
        inputs_embeds: torch.FloatTensor | None = None,
        cache_position: torch.LongTensor | None = None,
        **kwargs,
    ):
        model_inputs = super().prepare_inputs_for_generation(
            input_ids=input_ids,
            past_key_values=past_key_values,
            attention_mask=attention_mask,
            inputs_embeds=inputs_embeds,
            cache_position=cache_position,
            **kwargs,
        )

        # if input_ids is not None and input_ids.ndim == 2 and model_inputs.get("inputs_embeds") is None:
        #     print("------- Merging input_ids with input_values for generation...")
        #     merged_inputs = self._merge_input_ids_with_input_values(
        #         input_ids=input_ids,
        #         input_values=kwargs.get("input_values"),
        #         labels=kwargs.get("labels"),
        #     )
        #     model_inputs.update(
        #         {"inputs_embeds": merged_inputs["inputs_embeds"], "labels": merged_inputs["labels"], "input_ids": None}
        #     )

        # cache_position = model_inputs["cache_position"]
        # is_prefill = cache_position is not None and cache_position[0] == 0
        # if is_prefill:
        #     pass
        # else:
        #     # Remove text_encoder_layer_hidden_states to indicate no fusion needed during decoding
        #     model_inputs.pop("text_encoder_layer_hidden_states", None)

        return model_inputs

    @can_return_tuple
    @auto_docstring
    def forward(
        self,
        input_ids: torch.LongTensor = None,
        input_values: torch.Tensor | None = None,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.LongTensor | None = None,
        past_key_values: Cache | list[torch.FloatTensor] | None = None,
        inputs_embeds: torch.FloatTensor | None = None,
        labels: torch.LongTensor | None = None,
        use_cache: bool | None = None,
        cache_position: torch.LongTensor | None = None,
        logits_to_keep: int | torch.Tensor = 0,
        text_ids_mask: torch.Tensor | None = None,
        text_ids_len: torch.Tensor | None = None,
        **kwargs: Unpack[TransformersKwargs],
    ) -> tuple | BreezeOutputWithPast:
        r"""
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length, num_codebooks) or (batch_size, sequence_length)`):
            1. (batch_size, sequence_length): corresponds to the input sequence prepared with the processor from the text prompt. Such input
            requires `input_values` to be provided so that audio can be encoded in codebook tokens and then merged with the text tokens.

            2. (batch_size, sequence_length, num_codebooks): codebook tokens generated during the autoregressive decoding. Such input is not meant to be used by end users.

            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.

            [What are input IDs?](../glossary#input-ids)
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for computing the masked language modeling loss. Indices should be in `[config.audio_token_id, -100, -101]`.
            Requires targeted `input_values` to be provided as audio tokens will be inferred from it using the `codec_model`.
            - `config.audio_token_id` indicates an audio frames (considering sequence length elements as frames)
            - `-100` will be ignored in the loss computation
            - `-101` indicates the audio frame will be used only for the backbone model (using the first codebook token as labels)

            Such labels can be prepared using `output_labels=True` when calling [`the repository input preparation utilities`].
        logits_to_keep (`int` or `torch.Tensor`, *optional*):
            Kept for compatibility. Does not support another value than:
            1. `0`, which is equivalent to keeping all logits, used in the training regime
            2. `1`, which is equivalent to keeping only the last logit, used in the generation regime

        text_ids_mask (`torch.BoolTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Marks text-token positions consumed by the text encoder.
        text_ids_len (`torch.LongTensor` of shape `(batch_size,)`, *optional*):
            Number of valid text tokens for each item in the batch.
        """
        text_encoder_layer_hidden_states = None
        if input_ids is not None and input_ids.ndim == 2:
            merged_inputs = self._merge_input_ids_with_input_values(
                input_ids,
                input_values,
                labels,
                text_ids_mask=text_ids_mask,
                text_ids_len=text_ids_len,
                attention_mask=attention_mask,
            )
            inputs_embeds = merged_inputs["inputs_embeds"]
            labels = merged_inputs["labels"]
            input_ids = None
            text_encoder_layer_hidden_states = merged_inputs.get(
                "text_encoder_layer_hidden_states", None
            )

        backbone_outputs = self.backbone_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            cache_position=cache_position,
            text_encoder_layer_hidden_states=text_encoder_layer_hidden_states,
            text_ids_mask=text_ids_mask,
            **kwargs,
        )

        backbone_hidden_states = backbone_outputs[0]
        backbone_hidden_states_for_depth_decoder = backbone_hidden_states

        backbone_all_hidden_states = backbone_outputs.hidden_states

        if backbone_all_hidden_states is None:
            backbone_all_hidden_states = (backbone_hidden_states_for_depth_decoder,)
        # Only compute necessary logits, and do not upcast them to float if we are not computing the loss
        slice_indices = (
            slice(-logits_to_keep, None)
            if isinstance(logits_to_keep, int)
            else logits_to_keep
        )

        loss = None
        backbone_loss = None
        backbone_logits = None
        depth_decoder_loss = None
        depth_decoder_outputs = None

        if labels is not None:
            # Filter out num_items_in_batch from kwargs to ensure reduction='mean' is used
            # This prevents incorrect loss normalization when backbone and depth decoder
            # operate on different numbers of tokens
            loss_kwargs = {k: v for k, v in kwargs.items() if k != "num_items_in_batch"}

            # select first codebook as labels for the backbone model
            backbone_labels = labels[:, :, 0]

            backbone_logits = self.lm_head(backbone_hidden_states[:, slice_indices, :])
            backbone_loss = self.loss_function(
                logits=backbone_logits,
                labels=backbone_labels,
                vocab_size=self.lm_head.out_features,
                **loss_kwargs,
            )

        # Compute logits only when actually needed
        if backbone_logits is None and labels is None:
            backbone_logits = self.lm_head(backbone_hidden_states[:, slice_indices, :])

        if labels is not None:
            # for the depth decoder, we need to select the frames to train on
            # those are frames where the label is not uniformly `ignore_index` along the codebook dimension
            train_mask = ~(labels[:, :, 1:] == -100).all(dim=-1)
            depth_decoder_input_ids = labels[train_mask][
                ..., : self.config.num_codebooks - 1
            ]
            # add place holder in position 0 that will be replaced by the backbone_last_hidden_state
            depth_decoder_input_ids = nn.functional.pad(
                depth_decoder_input_ids, (1, 0), value=0
            )

            train_idxs = train_mask.nonzero(as_tuple=True)
            backbone_last_hidden_states = backbone_hidden_states_for_depth_decoder[
                train_idxs[0], train_idxs[1] - 1, :
            ]
            depth_decoder_labels = labels[train_mask]

            depth_decoder_outputs = self.depth_decoder(
                input_ids=depth_decoder_input_ids,
                backbone_last_hidden_state=backbone_last_hidden_states,
                use_cache=use_cache,
                return_dict=True,
                labels=depth_decoder_labels,
                **loss_kwargs,
            )

            depth_decoder_loss = depth_decoder_outputs.loss
            if self.training:
                loss = (
                    backbone_loss
                    + depth_decoder_loss * self.config.depth_header_loss_weight
                )
            else:
                loss = backbone_loss + depth_decoder_loss
        depth_decoder_hidden_states = None
        if depth_decoder_outputs is not None:
            depth_decoder_hidden_states = depth_decoder_outputs.hidden_states

        return BreezeOutputWithPast(
            loss=loss,
            backbone_loss=backbone_loss,
            depth_decoder_loss=depth_decoder_loss,
            logits=backbone_logits,
            past_key_values=backbone_outputs.past_key_values,
            hidden_states=backbone_all_hidden_states,
            attentions=backbone_outputs.attentions,
            depth_decoder_logits=depth_decoder_outputs.logits
            if depth_decoder_outputs is not None
            else None,
            depth_decoder_past_key_values=depth_decoder_outputs.past_key_values
            if depth_decoder_outputs is not None
            else None,
            depth_decoder_hidden_states=depth_decoder_hidden_states,
            depth_decoder_attentions=depth_decoder_outputs.attentions
            if depth_decoder_outputs is not None
            else None,
        )


__all__ = [
    "BreezeBackboneModel",
    "BreezeDepthDecoderForCausalLM",
    "BreezeDepthDecoderModel",
    "BreezeForConditionalGeneration",
    "BreezePreTrainedModel",
]

AutoModel.register(BreezeConfig, BreezeForConditionalGeneration, exist_ok=True)
