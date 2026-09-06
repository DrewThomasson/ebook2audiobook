"""
Breeze Backbone Factory and Adapter

This module provides:
1. BreezeBackboneFactory: Factory class to create different types of backbones
2. BreezeBackboneAdapter: Adapter to use external pretrained LLMs as Breeze backbone

Usage:
    from models.breeze_backbone_factory import BreezeBackboneFactory

    # In BreezeForConditionalGeneration.__init__:
    self.backbone_model = BreezeBackboneFactory.create_backbone(config)
"""


import torch
from torch import nn
from transformers import AutoConfig
from transformers.cache_utils import Cache, DynamicCache
from transformers.masking_utils import create_causal_mask
from transformers.modeling_outputs import BaseModelOutputWithPast
from transformers.utils import logging

logger = logging.get_logger(__name__)


class BreezeBackboneFactory:
    """Factory class to create Breeze backbone models"""

    SUPPORTED_MODELS = {
        "breeze": "Native Breeze backbone",
        "qwen3": "Qwen3ForCausalLM",
        "llama3": "Llama3ForCausalLM",
        # Add more models as needed
    }

    @staticmethod
    def create_backbone(config):
        """
        Create backbone model based on config.backbone_model_type

        Args:
            config: BreezeConfig instance with backbone_model_type field

        Returns:
            Backbone model with interface compatible with BreezeBackboneModel
        """
        backbone_type = getattr(config, "backbone_model_type", "breeze")

        if backbone_type == "breeze":
            # Import here to avoid circular dependency
            from .breeze import BreezeBackboneModel

            return BreezeBackboneModel(config)
        else:
            # Use adapter for external LLMs
            if backbone_type not in BreezeBackboneFactory.SUPPORTED_MODELS:
                logger.warning(
                    f"Backbone type '{backbone_type}' not in known types. "
                    f"Attempting to create adapter anyway..."
                )
            return BreezeBackboneAdapter.create_from_config(config)


class BreezeBackboneAdapter(nn.Module):
    """
    Adapter to use external pretrained LLM as Breeze Backbone

    Key modifications from original LLM:
    1. Replace LLM's embedding with BreezeBackboneModelEmbeddings (for audio tokens)
    2. Keep LLM's transformer layers
    3. Keep LLM's norm layer
    4. Remove LLM's lm_head (Breeze has its own)

    Interface: Compatible with BreezeBackboneModel's forward signature
    """

    def __init__(self, config, layers, norm, rotary_emb):
        """
        Args:
            config: BreezeConfig (updated with LLM's architecture params)
            layers: nn.ModuleList of transformer layers from LLM
            norm: RMSNorm layer from LLM
            rotary_emb: Rotary embedding layer from LLM
        """
        super().__init__()
        self.config = config

        # Ensure _attn_implementation is set on config
        if not hasattr(config, "_attn_implementation"):
            config._attn_implementation = "eager"

        # Breeze's custom embedding for audio+text tokens
        from .breeze import BreezeBackboneModelEmbeddings

        self.embed_tokens = BreezeBackboneModelEmbeddings(config)

        # Pretrained LLM's transformer components
        self.layers = layers
        self.norm = norm
        self.rotary_emb = rotary_emb
        self.gradient_checkpointing = False

    @classmethod
    def create_from_config(cls, config):
        """
        Create adapter from config (architecture only, no weight loading)

        Weight loading is handled separately by breeze_model_init()

        Args:
            config: BreezeConfig with backbone_model_name_or_path set

        Returns:
            BreezeBackboneAdapter instance with initialized architecture
        """
        backbone_config = getattr(config, "backbone_config", None)
        backbone_path = getattr(config, "backbone_model_name_or_path", None)
        if backbone_config is None and backbone_path is None:
            raise ValueError(
                "config.backbone_config or config.backbone_model_name_or_path must be set"
            )

        backbone_type = config.backbone_model_type
        if backbone_config is not None:
            logger.info(
                f"Creating backbone adapter for {backbone_type} from bundled config"
            )
            llm_config = AutoConfig.for_model(**backbone_config)
        else:
            logger.info(
                f"Creating backbone adapter for {backbone_type} from {backbone_path}"
            )
            llm_config = AutoConfig.from_pretrained(backbone_path)

        # Transfer attention implementation setting from BreezeConfig to LLM config
        if (
            hasattr(config, "_attn_implementation")
            and config._attn_implementation is not None
        ):
            llm_config._attn_implementation = config._attn_implementation
            logger.info(
                f"Set attention implementation to: {config._attn_implementation}"
            )
        else:
            # Default to eager if not specified
            llm_config._attn_implementation = "eager"
            logger.info("Attention implementation not specified, defaulting to: eager")

        # Create layers based on backbone type
        if backbone_type == "qwen3":
            layers, norm, rotary_emb = cls._create_qwen3_layers(llm_config)
        elif backbone_type == "llama3":
            layers, norm, rotary_emb = cls._create_llama3_layers(llm_config)
        else:
            raise ValueError(
                f"Unsupported backbone_model_type: {backbone_type}. "
                f"Supported types: {list(BreezeBackboneFactory.SUPPORTED_MODELS.keys())}"
            )

        return cls(config, layers, norm, rotary_emb)

    @staticmethod
    def _create_qwen3_layers(llm_config):
        """Create Qwen3 layer architecture"""
        from transformers.models.qwen3.modeling_qwen3 import (
            Qwen3DecoderLayer,
            Qwen3RMSNorm,
            Qwen3RotaryEmbedding,
        )

        layers = nn.ModuleList(
            [
                Qwen3DecoderLayer(llm_config, layer_idx)
                for layer_idx in range(llm_config.num_hidden_layers)
            ]
        )
        norm = Qwen3RMSNorm(llm_config.hidden_size, eps=llm_config.rms_norm_eps)
        rotary_emb = Qwen3RotaryEmbedding(config=llm_config)

        return layers, norm, rotary_emb

    @staticmethod
    def _create_llama3_layers(llm_config):
        """Create Llama3 layer architecture"""
        from transformers.models.llama.modeling_llama import (
            LlamaDecoderLayer,
            LlamaRMSNorm,
            LlamaRotaryEmbedding,
        )

        layers = nn.ModuleList(
            [
                LlamaDecoderLayer(llm_config, layer_idx)
                for layer_idx in range(llm_config.num_hidden_layers)
            ]
        )
        norm = LlamaRMSNorm(llm_config.hidden_size, eps=llm_config.rms_norm_eps)
        rotary_emb = LlamaRotaryEmbedding(config=llm_config)

        return layers, norm, rotary_emb

    def forward(
        self,
        input_ids: torch.LongTensor | None = None,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.LongTensor | None = None,
        past_key_values: Cache | None = None,
        inputs_embeds: torch.FloatTensor | None = None,
        cache_position: torch.LongTensor | None = None,
        text_encoder_layer_hidden_states: torch.FloatTensor | None = None,
        text_ids_mask: torch.BoolTensor | None = None,
        use_cache: bool | None = None,
        **kwargs,
    ) -> BaseModelOutputWithPast:
        """
        Forward pass - interface compatible with BreezeBackboneModel

        Args:
            input_ids: (batch_size, seq_len, num_codebooks) or (batch_size, seq_len)
            inputs_embeds: Pre-computed embeddings
            attention_mask: Attention mask
            position_ids: Position IDs
            past_key_values: Cached key/values for generation
            cache_position: Cache position tensor
            use_cache: Whether to use KV cache

        Returns:
            BaseModelOutputWithPast with last_hidden_state
        """
        # Embed tokens if not provided
        if inputs_embeds is None:
            inputs_embeds = self.embed_tokens(input_ids)

        # Initialize cache
        if use_cache and past_key_values is None:
            past_key_values = DynamicCache(config=self.config)

        # Compute cache_position if not provided
        if cache_position is None:
            past_seen_tokens = (
                past_key_values.get_seq_length() if past_key_values is not None else 0
            )
            cache_position = torch.arange(
                past_seen_tokens,
                past_seen_tokens + inputs_embeds.shape[1],
                device=inputs_embeds.device,
            )

        # Compute position_ids if not provided
        if position_ids is None:
            position_ids = cache_position.unsqueeze(0)

        # Create causal mask
        causal_mask = create_causal_mask(
            config=self.config,
            input_embeds=inputs_embeds,
            attention_mask=attention_mask,
            cache_position=cache_position,
            past_key_values=past_key_values,
            position_ids=position_ids,
        )

        # Compute position embeddings (for RoPE)
        hidden_states = inputs_embeds
        position_embeddings = self.rotary_emb(hidden_states, position_ids)

        # Pass through transformer layers
        for layer_idx, decoder_layer in enumerate(self.layers):
            if text_encoder_layer_hidden_states is not None and layer_idx > 0:
                # skip for first layer fusion, cause it may has aleady been done in convert_input_ids_to_embeds() function
                text_layer_hidden_states = text_encoder_layer_hidden_states[layer_idx]
                # hidden_states[text_ids_mask][..., -self.config.hidden_size//2:] = text_layer_hidden_states

                hidden_states_half_first, hidden_states_half_second = (
                    hidden_states.split(self.config.hidden_size // 2, dim=-1)
                )
                if self.training:
                    hidden_states_half_second = hidden_states_half_second.clone()
                hidden_states_half_second[text_ids_mask] = text_layer_hidden_states
                # hidden_states_half_second = torch.where(
                #     text_ids_mask.unsqueeze(-1),
                #     text_layer_hidden_states,
                #     hidden_states_half_second,
                # )
                hidden_states = torch.cat(
                    [hidden_states_half_first, hidden_states_half_second], dim=-1
                )

            hidden_states = decoder_layer(
                hidden_states,
                attention_mask=causal_mask,
                position_ids=position_ids,
                past_key_values=past_key_values,
                cache_position=cache_position,
                position_embeddings=position_embeddings,
                **kwargs,
            )

        # Final norm
        hidden_states = self.norm(hidden_states)

        return BaseModelOutputWithPast(
            last_hidden_state=hidden_states,
            past_key_values=past_key_values,
        )


__all__ = ["BreezeBackboneAdapter", "BreezeBackboneFactory"]
