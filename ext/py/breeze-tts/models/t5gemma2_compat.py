# Local compatibility shim for loading T5Gemma 2 text encoders under
# transformers 4.57.x, which does not ship the t5gemma2 architecture.


import torch
from torch import nn
from transformers import PretrainedConfig
from transformers.activations import ACT2FN
from transformers.modeling_layers import GradientCheckpointingLayer
from transformers.modeling_outputs import BaseModelOutput
from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS, PreTrainedModel


class T5Gemma2TextConfig(PretrainedConfig):
    model_type = "t5gemma2_text"
    keys_to_ignore_at_inference = ["past_key_values"]

    def __init__(
        self,
        vocab_size: int = 262208,
        hidden_size: int = 2304,
        intermediate_size: int = 9216,
        num_hidden_layers: int = 26,
        num_attention_heads: int = 8,
        num_key_value_heads: int = 4,
        head_dim: int = 256,
        hidden_activation: str = "gelu_pytorch_tanh",
        max_position_embeddings: int = 131072,
        initializer_range: float = 0.02,
        rms_norm_eps: float = 1e-6,
        use_cache: bool = True,
        rope_parameters: dict | None = None,
        attention_bias: bool = False,
        attention_dropout: float = 0.0,
        dropout_rate: float = 0.0,
        query_pre_attn_scalar: int = 256,
        sliding_window: int | None = 4096,
        layer_types: list[str] | None = None,
        final_logit_softcapping: float | None = None,
        attn_logit_softcapping: float | None = None,
        eoi_token_index: int = 256000,
        pad_token_id: int | None = 0,
        eos_token_id: int | None = 1,
        bos_token_id: int | None = 2,
        tie_word_embeddings: bool = True,
        **kwargs,
    ):
        sliding_window_pattern = kwargs.pop(
            "_sliding_window_pattern", kwargs.pop("sliding_window_pattern", 6)
        )
        rope_scaling = kwargs.pop("rope_scaling", None)
        super().__init__(
            pad_token_id=pad_token_id,
            eos_token_id=eos_token_id,
            bos_token_id=bos_token_id,
            tie_word_embeddings=tie_word_embeddings,
            **kwargs,
        )

        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads
        self.head_dim = head_dim
        self.hidden_activation = hidden_activation
        self.max_position_embeddings = max_position_embeddings
        self.initializer_range = initializer_range
        self.rms_norm_eps = rms_norm_eps
        self.use_cache = use_cache
        self.attention_bias = attention_bias
        self.attention_dropout = attention_dropout
        self.dropout_rate = dropout_rate
        self.query_pre_attn_scalar = query_pre_attn_scalar
        self.sliding_window = sliding_window
        self.final_logit_softcapping = final_logit_softcapping
        self.attn_logit_softcapping = attn_logit_softcapping
        self.eoi_token_index = eoi_token_index

        if layer_types is None:
            layer_types = [
                "sliding_attention"
                if (i + 1) % sliding_window_pattern
                else "full_attention"
                for i in range(num_hidden_layers)
            ]
        self.layer_types = layer_types
        self.rope_parameters = self._normalize_rope_parameters(
            rope_parameters, rope_scaling
        )

    @staticmethod
    def _normalize_rope_parameters(
        rope_parameters: dict | None, rope_scaling: dict | None
    ) -> dict:
        params = {
            "sliding_attention": {"rope_type": "default", "rope_theta": 10000.0},
            "full_attention": {"rope_type": "default", "rope_theta": 1000000.0},
        }
        if rope_parameters:
            for key, value in rope_parameters.items():
                params[key] = (
                    dict(value) if value is not None else {"rope_type": "default"}
                )
        if rope_scaling:
            params["full_attention"].update(rope_scaling)
        params["sliding_attention"].setdefault("rope_type", "default")
        params["sliding_attention"].setdefault("rope_theta", 10000.0)
        params["full_attention"].setdefault("rope_type", "default")
        params["full_attention"].setdefault("rope_theta", 1000000.0)
        return params


class T5Gemma2RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.zeros(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        output = x.float() * torch.rsqrt(
            x.float().pow(2).mean(-1, keepdim=True) + self.eps
        )
        output = output * (1.0 + self.weight.float())
        return output.type_as(x)


class T5Gemma2MLP(nn.Module):
    def __init__(self, config: T5Gemma2TextConfig):
        super().__init__()
        self.gate_proj = nn.Linear(
            config.hidden_size, config.intermediate_size, bias=False
        )
        self.up_proj = nn.Linear(
            config.hidden_size, config.intermediate_size, bias=False
        )
        self.down_proj = nn.Linear(
            config.intermediate_size, config.hidden_size, bias=False
        )
        self.act_fn = ACT2FN[config.hidden_activation]
        self.dropout = nn.Dropout(config.dropout_rate)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        hidden_states = self.act_fn(self.gate_proj(x)) * self.up_proj(x)
        hidden_states = self.dropout(hidden_states)
        return self.down_proj(hidden_states)


class T5Gemma2RotaryEmbedding(nn.Module):
    def __init__(self, config: T5Gemma2TextConfig, device=None):
        super().__init__()
        self.config = config
        self.layer_types = sorted(set(config.layer_types))
        for layer_type in self.layer_types:
            inv_freq, attention_scaling = self._compute_inv_freq(
                config, layer_type, device=device
            )
            self.register_buffer(f"{layer_type}_inv_freq", inv_freq, persistent=False)
            setattr(self, f"{layer_type}_attention_scaling", attention_scaling)

    @staticmethod
    def _compute_inv_freq(
        config: T5Gemma2TextConfig, layer_type: str, device=None
    ) -> tuple[torch.Tensor, float]:
        rope_params = config.rope_parameters[layer_type]
        rope_type = rope_params.get("rope_type", "default")
        base = rope_params["rope_theta"]
        dim = (
            getattr(config, "head_dim", None)
            or config.hidden_size // config.num_attention_heads
        )
        inv_freq = 1.0 / (
            base ** (torch.arange(0, dim, 2, device=device, dtype=torch.float32) / dim)
        )
        if rope_type == "linear":
            inv_freq = inv_freq / float(rope_params["factor"])
        elif rope_type != "default":
            raise ValueError(
                f"Unsupported T5Gemma2 rope_type in local compat shim: {rope_type}"
            )
        return inv_freq, 1.0

    def forward(self, x: torch.Tensor, position_ids: torch.LongTensor, layer_type: str):
        inv_freq = getattr(self, f"{layer_type}_inv_freq")
        attention_scaling = getattr(self, f"{layer_type}_attention_scaling")
        inv_freq_expanded = (
            inv_freq[None, :, None]
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
        with torch.autocast(device_type=device_type, enabled=False):
            freqs = (
                inv_freq_expanded.float() @ position_ids_expanded.float()
            ).transpose(1, 2)
            emb = torch.cat((freqs, freqs), dim=-1)
            cos = emb.cos() * attention_scaling
            sin = emb.sin() * attention_scaling

        return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)


def apply_rotary_pos_emb(
    q: torch.Tensor,
    k: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    unsqueeze_dim=1,
):
    cos = cos.unsqueeze(unsqueeze_dim)
    sin = sin.unsqueeze(unsqueeze_dim)
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed


def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
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
    dropout: float = 0.0,
    scaling: float | None = None,
    softcap: float | None = None,
    **kwargs,
):
    if scaling is None:
        scaling = module.head_dim**-0.5
    key_states = repeat_kv(key, module.num_key_value_groups)
    value_states = repeat_kv(value, module.num_key_value_groups)
    attn_weights = torch.matmul(query, key_states.transpose(2, 3)) * scaling
    if softcap is not None:
        attn_weights = torch.tanh(attn_weights / softcap) * softcap
    if attention_mask is not None:
        attn_weights = attn_weights + attention_mask[:, :, :, : key_states.shape[-2]]
    attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(
        query.dtype
    )
    attn_weights = nn.functional.dropout(
        attn_weights, p=dropout, training=module.training
    )
    attn_output = torch.matmul(attn_weights, value_states)
    attn_output = attn_output.transpose(1, 2).contiguous()
    return attn_output, attn_weights


def _padding_mask_to_additive_mask(
    attention_mask: torch.Tensor | None,
    query: torch.Tensor,
    layer_type: str,
    sliding_window: int | None,
) -> torch.Tensor | None:
    batch_size, _, seq_len, _ = query.shape
    device = query.device
    dtype = query.dtype

    has_padding = attention_mask is not None and not bool(
        attention_mask.to(torch.bool).all()
    )
    if layer_type == "full_attention" and not has_padding:
        return None

    if attention_mask is None:
        valid_kv = torch.ones(batch_size, seq_len, device=device, dtype=torch.bool)
    else:
        valid_kv = attention_mask.to(device=device, dtype=torch.bool)
    allowed = valid_kv[:, None, None, :].expand(batch_size, 1, seq_len, seq_len)

    if layer_type == "sliding_attention":
        if sliding_window is None:
            raise ValueError(
                "T5Gemma2 sliding_attention requires config.sliding_window"
            )
        q_idx = torch.arange(seq_len, device=device)[:, None]
        kv_idx = torch.arange(seq_len, device=device)[None, :]
        left_window_size = (sliding_window + 1) // 2
        right_window_size = sliding_window // 2 + 1
        dist = q_idx - kv_idx
        local = ((dist >= 0) & (dist < left_window_size)) | (
            (dist < 0) & (-dist < right_window_size)
        )
        allowed = allowed & local[None, None, :, :]

    additive_mask = torch.zeros(
        (batch_size, 1, seq_len, seq_len), device=device, dtype=dtype
    )
    additive_mask.masked_fill_(~allowed, torch.finfo(dtype).min)
    return additive_mask


def t5gemma2_flash_attention_forward(
    module: nn.Module,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attention_mask: torch.Tensor | None,
    dropout: float = 0.0,
    scaling: float | None = None,
    sliding_window: int | None = None,
    softcap: float | None = None,
    **kwargs,
):
    if query.device.type != "cuda" or query.dtype not in (
        torch.float16,
        torch.bfloat16,
    ):
        additive_mask = _padding_mask_to_additive_mask(
            attention_mask,
            query,
            module.layer_type,
            module.config.sliding_window,
        )
        return eager_attention_forward(
            module,
            query,
            key,
            value,
            additive_mask,
            dropout=dropout,
            scaling=scaling,
            softcap=softcap,
            **kwargs,
        )

    try:
        from flash_attn import flash_attn_func, flash_attn_varlen_func
        from flash_attn.bert_padding import pad_input, unpad_input
    except ImportError as exc:
        raise ImportError(
            "flash_attn is required for T5Gemma2 flash_attention_2"
        ) from exc

    query = query.transpose(1, 2).contiguous()
    key = key.transpose(1, 2).contiguous()
    value = value.transpose(1, 2).contiguous()
    batch_size, seq_len = query.shape[:2]
    dropout_p = dropout if module.training else 0.0
    softcap_value = 0.0 if softcap is None else softcap

    window_size = (-1, -1)
    if module.layer_type == "sliding_attention":
        if sliding_window is None:
            raise ValueError(
                "T5Gemma2 sliding_attention requires config.sliding_window"
            )
        left_window_size = (sliding_window + 1) // 2
        right_window_size = sliding_window // 2 + 1
        window_size = (left_window_size - 1, right_window_size - 1)

    has_padding = attention_mask is not None and not bool(
        attention_mask.to(torch.bool).all()
    )
    if has_padding:
        attention_mask = attention_mask.to(device=query.device, dtype=torch.bool)
        query_unpad, indices_q, cu_seqlens_q, max_seqlen_q, _ = unpad_input(
            query, attention_mask
        )
        key_unpad, _, cu_seqlens_k, max_seqlen_k, _ = unpad_input(key, attention_mask)
        value_unpad, _, _, _, _ = unpad_input(value, attention_mask)
        attn_output_unpad = flash_attn_varlen_func(
            query_unpad,
            key_unpad,
            value_unpad,
            cu_seqlens_q,
            cu_seqlens_k,
            max_seqlen_q,
            max_seqlen_k,
            dropout_p=dropout_p,
            softmax_scale=scaling,
            causal=False,
            window_size=window_size,
            softcap=softcap_value,
        )
        attn_output = pad_input(attn_output_unpad, indices_q, batch_size, seq_len)
    else:
        attn_output = flash_attn_func(
            query,
            key,
            value,
            dropout_p=dropout_p,
            softmax_scale=scaling,
            causal=False,
            window_size=window_size,
            softcap=softcap_value,
        )

    return attn_output, None


class T5Gemma2SelfAttention(nn.Module):
    def __init__(self, config: T5Gemma2TextConfig, layer_idx: int):
        super().__init__()
        self.config = config
        self.layer_idx = layer_idx
        self.layer_type = config.layer_types[layer_idx]
        self.head_dim = getattr(
            config, "head_dim", config.hidden_size // config.num_attention_heads
        )
        self.num_key_value_groups = (
            config.num_attention_heads // config.num_key_value_heads
        )
        self.scaling = config.query_pre_attn_scalar**-0.5
        self.attention_dropout = config.attention_dropout
        self.is_causal = False
        self.sliding_window = (
            config.sliding_window if self.layer_type == "sliding_attention" else None
        )

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
        self.q_norm = T5Gemma2RMSNorm(dim=self.head_dim, eps=config.rms_norm_eps)
        self.k_norm = T5Gemma2RMSNorm(dim=self.head_dim, eps=config.rms_norm_eps)

    def forward(
        self,
        hidden_states: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        attention_mask: torch.Tensor | None = None,
        **kwargs,
    ):
        input_shape = hidden_states.shape[:-1]
        hidden_shape = (*input_shape, -1, self.head_dim)

        query_states = self.q_proj(hidden_states).view(hidden_shape).transpose(1, 2)
        key_states = self.k_proj(hidden_states).view(hidden_shape).transpose(1, 2)
        value_states = self.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)

        query_states = self.q_norm(query_states)
        key_states = self.k_norm(key_states)

        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(
            query_states, key_states, cos, sin
        )

        attn_impl = getattr(self.config, "_attn_implementation", None) or getattr(
            self.config,
            "preferred_attn_implementation",
            "flash_attention_2",
        )
        if attn_impl == "flash_attention_2":
            attention_interface = t5gemma2_flash_attention_forward
        else:
            attention_interface = (
                eager_attention_forward
                if attn_impl == "eager"
                else ALL_ATTENTION_FUNCTIONS[attn_impl]
            )
        attn_output, attn_weights = attention_interface(
            self,
            query_states,
            key_states,
            value_states,
            attention_mask,
            dropout=self.attention_dropout if self.training else 0.0,
            scaling=self.scaling,
            sliding_window=self.sliding_window,
            softcap=self.config.attn_logit_softcapping,
            **kwargs,
        )

        attn_output = attn_output.reshape(*input_shape, -1).contiguous()
        attn_output = self.o_proj(attn_output)
        return attn_output, attn_weights


class T5Gemma2EncoderLayer(GradientCheckpointingLayer):
    def __init__(self, config: T5Gemma2TextConfig, layer_idx: int):
        super().__init__()
        self.attention_type = config.layer_types[layer_idx]
        self.self_attn = T5Gemma2SelfAttention(config=config, layer_idx=layer_idx)
        self.pre_self_attn_layernorm = T5Gemma2RMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )
        self.post_self_attn_layernorm = T5Gemma2RMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )
        self.mlp = T5Gemma2MLP(config)
        self.pre_feedforward_layernorm = T5Gemma2RMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )
        self.post_feedforward_layernorm = T5Gemma2RMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )
        self.dropout = nn.Dropout(config.dropout_rate)

    def forward(
        self,
        hidden_states: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        attention_mask: torch.Tensor | None = None,
        **kwargs,
    ) -> torch.Tensor:
        residual = hidden_states
        hidden_states = self.pre_self_attn_layernorm(hidden_states)
        hidden_states, _ = self.self_attn(
            hidden_states=hidden_states,
            position_embeddings=position_embeddings,
            attention_mask=attention_mask,
            **kwargs,
        )
        hidden_states = self.post_self_attn_layernorm(hidden_states)
        hidden_states = residual + self.dropout(hidden_states)

        residual = hidden_states
        hidden_states = self.pre_feedforward_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = self.post_feedforward_layernorm(hidden_states)
        hidden_states = residual + self.dropout(hidden_states)
        return hidden_states


class T5Gemma2TextScaledWordEmbedding(nn.Embedding):
    def __init__(
        self,
        num_embeddings: int,
        embedding_dim: int,
        padding_idx: int | None,
        embed_scale: float = 1.0,
        eoi_token_index: int = 256000,
        device=None,
        dtype=None,
    ):
        super().__init__(
            num_embeddings, embedding_dim, padding_idx, device=device, dtype=dtype
        )
        self.scalar_embed_scale = embed_scale
        self.register_buffer("embed_scale", torch.tensor(embed_scale), persistent=False)
        self.eoi_token_index = eoi_token_index
        self.eoi_embedding = nn.Parameter(
            torch.zeros(self.embedding_dim, device=device, dtype=dtype)
        )

    def forward(self, input_ids: torch.Tensor):
        input_embeddings = super().forward(input_ids) * self.embed_scale.to(
            self.weight.dtype
        )
        eoi_mask = input_ids == self.eoi_token_index
        return torch.where(
            eoi_mask.unsqueeze(-1),
            self.eoi_embedding.to(input_embeddings.dtype),
            input_embeddings,
        )


class T5Gemma2TextEncoder(PreTrainedModel):
    config_class = T5Gemma2TextConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _no_split_modules = ["T5Gemma2EncoderLayer"]
    _supports_flash_attn = True
    _supports_sdpa = True
    _supports_attention_backend = True

    def __init__(self, config: T5Gemma2TextConfig):
        super().__init__(config)
        self.padding_idx = config.pad_token_id
        self.vocab_size = config.vocab_size
        self.embed_tokens = T5Gemma2TextScaledWordEmbedding(
            config.vocab_size,
            config.hidden_size,
            self.padding_idx,
            embed_scale=config.hidden_size**0.5,
            eoi_token_index=config.eoi_token_index,
        )
        self.norm = T5Gemma2RMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.layers = nn.ModuleList(
            [
                T5Gemma2EncoderLayer(config, layer_idx)
                for layer_idx in range(config.num_hidden_layers)
            ]
        )
        self.dropout = nn.Dropout(config.dropout_rate)
        self.rotary_emb = T5Gemma2RotaryEmbedding(config)
        self.gradient_checkpointing = False
        self.post_init()

    def get_input_embeddings(self):
        return self.embed_tokens

    def set_input_embeddings(self, new_embeddings):
        self.embed_tokens = new_embeddings
        self.vocab_size = new_embeddings.num_embeddings

    def _get_resized_embeddings(
        self,
        old_embeddings: nn.Embedding,
        new_num_tokens: int | None = None,
        pad_to_multiple_of: int | None = None,
        mean_resizing: bool = True,
    ) -> nn.Embedding:
        if new_num_tokens is None:
            return old_embeddings
        if pad_to_multiple_of is not None:
            new_num_tokens = (
                (new_num_tokens + pad_to_multiple_of - 1) // pad_to_multiple_of
            ) * pad_to_multiple_of

        old_num_tokens, old_embedding_dim = old_embeddings.weight.shape
        if old_num_tokens == new_num_tokens:
            return old_embeddings
        padding_idx = old_embeddings.padding_idx
        if padding_idx is not None and padding_idx >= new_num_tokens:
            padding_idx = None
        new_embeddings = T5Gemma2TextScaledWordEmbedding(
            new_num_tokens,
            old_embedding_dim,
            padding_idx,
            embed_scale=getattr(
                old_embeddings, "scalar_embed_scale", self.config.hidden_size**0.5
            ),
            eoi_token_index=getattr(
                old_embeddings, "eoi_token_index", self.config.eoi_token_index
            ),
            device=old_embeddings.weight.device,
            dtype=old_embeddings.weight.dtype,
        )
        self._init_weights(new_embeddings)
        num_tokens_to_copy = min(old_num_tokens, new_num_tokens)
        new_embeddings.weight.data[:num_tokens_to_copy] = old_embeddings.weight.data[
            :num_tokens_to_copy
        ]
        if hasattr(old_embeddings, "eoi_embedding"):
            new_embeddings.eoi_embedding.data.copy_(old_embeddings.eoi_embedding.data)
        return new_embeddings

    def _init_weights(self, module):
        std = self.config.initializer_range
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, T5Gemma2TextScaledWordEmbedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
            module.eoi_embedding.data.zero_()
            module.embed_scale.fill_(module.scalar_embed_scale)
        elif isinstance(module, T5Gemma2RMSNorm):
            module.weight.data.zero_()

    @staticmethod
    def _build_additive_attention_mask(
        attention_mask: torch.Tensor | None,
        inputs_embeds: torch.Tensor,
        layer_type: str,
        sliding_window: int | None,
    ) -> torch.Tensor | None:
        batch_size, seq_len = inputs_embeds.shape[:2]
        device = inputs_embeds.device

        has_padding = attention_mask is not None
        if layer_type == "full_attention" and not has_padding:
            return None

        if attention_mask is None:
            valid_kv = torch.ones(batch_size, seq_len, device=device, dtype=torch.bool)
        else:
            valid_kv = attention_mask.to(device=device, dtype=torch.bool)
        allowed = valid_kv[:, None, None, :].expand(batch_size, 1, seq_len, seq_len)

        if layer_type == "sliding_attention":
            if sliding_window is None:
                raise ValueError(
                    "T5Gemma2 sliding_attention requires config.sliding_window"
                )
            q_idx = torch.arange(seq_len, device=device)[:, None]
            kv_idx = torch.arange(seq_len, device=device)[None, :]
            left_window_size = (sliding_window + 1) // 2
            right_window_size = sliding_window // 2 + 1
            dist = q_idx - kv_idx
            local = ((dist >= 0) & (dist < left_window_size)) | (
                (dist < 0) & (-dist < right_window_size)
            )
            allowed = allowed & local[None, None, :, :]

        min_value = torch.finfo(inputs_embeds.dtype).min
        additive_mask = torch.zeros(
            (batch_size, 1, seq_len, seq_len), device=device, dtype=inputs_embeds.dtype
        )
        additive_mask.masked_fill_(~allowed, min_value)
        return additive_mask

    def forward(
        self,
        input_ids: torch.LongTensor | None = None,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.LongTensor | None = None,
        inputs_embeds: torch.FloatTensor | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        token_type_ids: torch.Tensor | None = None,
        **kwargs,
    ) -> BaseModelOutput:
        if (input_ids is None) == (inputs_embeds is None):
            raise ValueError(
                "You must specify exactly one of input_ids or inputs_embeds"
            )
        kwargs.pop("past_key_values", None)
        kwargs.pop("use_cache", None)

        output_hidden_states = (
            output_hidden_states
            if output_hidden_states is not None
            else self.config.output_hidden_states
        )
        return_dict = (
            return_dict if return_dict is not None else self.config.use_return_dict
        )

        if inputs_embeds is None:
            inputs_embeds = self.embed_tokens(input_ids)
        if position_ids is None:
            position_ids = torch.arange(
                0, inputs_embeds.shape[1], device=inputs_embeds.device
            ).unsqueeze(0)

        hidden_states = self.dropout(inputs_embeds)
        all_hidden_states = () if output_hidden_states else None

        position_embeddings = {
            layer_type: self.rotary_emb(hidden_states, position_ids, layer_type)
            for layer_type in set(self.config.layer_types)
        }
        attn_impl = getattr(self.config, "_attn_implementation", None) or getattr(
            self.config,
            "preferred_attn_implementation",
            "flash_attention_2",
        )
        if attn_impl == "flash_attention_2":
            padding_mask = None
            if getattr(self, "_force_static_attention_mask", False) or attention_mask is not None and not bool(
                attention_mask.to(torch.bool).all()
            ):
                padding_mask = attention_mask
            attn_masks = {
                layer_type: padding_mask for layer_type in set(self.config.layer_types)
            }
        else:
            attn_masks = {
                layer_type: self._build_additive_attention_mask(
                    attention_mask,
                    inputs_embeds,
                    layer_type,
                    self.config.sliding_window,
                )
                for layer_type in set(self.config.layer_types)
            }

        for layer_module in self.layers[: self.config.num_hidden_layers]:
            if output_hidden_states:
                all_hidden_states += (hidden_states,)
            hidden_states = layer_module(
                hidden_states,
                position_embeddings[layer_module.attention_type],
                attn_masks[layer_module.attention_type],
                output_attentions=False,
                **kwargs,
            )

        hidden_states = self.norm(hidden_states)
        hidden_states = self.dropout(hidden_states)
        if output_hidden_states:
            all_hidden_states += (hidden_states,)

        if not return_dict:
            return tuple(v for v in [hidden_states, all_hidden_states] if v is not None)
        return BaseModelOutput(
            last_hidden_state=hidden_states, hidden_states=all_hidden_states
        )
