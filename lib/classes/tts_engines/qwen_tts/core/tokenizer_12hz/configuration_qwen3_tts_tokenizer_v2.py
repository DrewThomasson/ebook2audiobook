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
"""Qwen3TTSTokenizerV2 model configuration"""

from transformers.configuration_utils import PretrainedConfig
from transformers.utils import logging

from transformers import MimiConfig


logger = logging.get_logger(__name__)


class Qwen3TTSTokenizerV2DecoderConfig(PretrainedConfig):
    r"""
    This is the configuration class to store the configuration of a [`Qwen3TTSTokenizerV2DecoderConfig`].

    Configuration objects inherit from [`PretrainedConfig`] and can be used to control the model outputs. Read the
    documentation from [`PretrainedConfig`] for more information.

    Args:
        codebook_size (`int`, *optional*, defaults to 2048):
            Number of entries in each residual codebook used for acoustic token quantization.
        hidden_size (`int`, *optional*, defaults to 1024):
            Dimensionality of the hidden states and embeddings in the autoregressive transformer decoder.
        max_position_embeddings (`int`, *optional*, defaults to 8000):
            Maximum sequence length that the autoregressive decoder can handle. Determines positional embedding size.
        rope_theta (`float`, *optional*, defaults to 10000.0):
            The base period for rotary position embeddings (RoPE) applied to attention layers.
        num_attention_heads (`int`, *optional*, defaults to 16):
            Number of attention heads for each attention layer in the decoder.
        num_key_value_heads (`int`, *optional*, defaults to 16):
            Number of key and value attention heads used in grouped-query attention (if applicable).
        attention_bias (`bool`, *optional*, defaults to `False`):
            Whether to use bias in the attention projection layers.
        sliding_window (`int`, *optional*, defaults to 72):
            Window size for local attention mechanism, limiting attention context to improve efficiency.
        intermediate_size (`int`, *optional*, defaults to 3072):
            Dimensionality of the feed-forward (intermediate) layer in each transformer block.
        hidden_act (`str` or `function`, *optional*, defaults to `"silu"`):
            The non-linear activation function used in the feed-forward layers. Supports `"silu"`, `"relu"`, `"gelu"`, etc.
        layer_scale_initial_scale (`float`, *optional*, defaults to 0.01):
            Initial value for LayerScale applied in transformer blocks, helping stabilize training.
        rms_norm_eps (`float`, *optional*, defaults to 1e-5):
            Epsilon value for RMS normalization layers to prevent division by zero.
        num_hidden_layers (`int`, *optional*, defaults to 8):
            Number of transformer blocks in the autoregressive decoder.
        num_quantizers (`int`, *optional*, defaults to 16):
            Number of residual vector quantizers used in the vocoder for fine-grained audio reconstruction.
        upsample_rates (`Tuple[int]`, *optional*, defaults to `(8, 5, 4, 3)`):
            Rate at which features are upsampled in the final waveform synthesis stage.
        upsampling_ratios (`Tuple[int]`, *optional*, defaults to `(2, 2)`):
            Ratios used in transposed convolutional layers to progressively upsample feature maps to waveform.
        decoder_dim (`int`, *optional*, defaults to 1536):
            Final dimensionality of the decoder's output before waveform generation.
        attention_dropout (`float`, *optional*, defaults to 0.0):
            Dropout probability applied to attention weights in the decoder.
    """

    def __init__(
        self,
        codebook_size=2048,
        hidden_size=1024,
        latent_dim=1024,
        max_position_embeddings=8000,
        rope_theta=10000,
        num_attention_heads=16,
        num_key_value_heads=16,
        attention_bias=False,
        sliding_window=72,
        intermediate_size=3072,
        hidden_act="silu",
        layer_scale_initial_scale=0.01,
        rms_norm_eps=1e-5,
        num_hidden_layers=8,
        num_quantizers=16,
        upsample_rates=(8, 5, 4, 3),
        upsampling_ratios=(2, 2),
        decoder_dim=1536,
        attention_dropout=0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.codebook_size = codebook_size
        self.hidden_size = hidden_size
        self.latent_dim = latent_dim
        self.max_position_embeddings = max_position_embeddings
        self.rope_theta = rope_theta
        self.num_attention_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads
        self.attention_bias = attention_bias
        self.sliding_window = sliding_window
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.layer_scale_initial_scale = layer_scale_initial_scale
        self.rms_norm_eps = rms_norm_eps
        self.num_hidden_layers = num_hidden_layers
        self.num_quantizers = num_quantizers
        self.upsample_rates = upsample_rates
        self.upsampling_ratios = upsampling_ratios
        self.decoder_dim = decoder_dim
        self.attention_dropout = attention_dropout

    @property
    def layer_types(self):
        """
        All layer in code2wav should be sliding attention
        """
        return ["sliding_attention"] * self.num_hidden_layers


class Qwen3TTSTokenizerV2Config(PretrainedConfig):
    """
    This is the configuration class to store the configuration of a [`Qwen3TTSTokenizerV2Config`]. It is used to instantiate a Qwen3TTSTokenizerV2Model
    model according to the specified sub-models configurations, defining the model architecture.

    Configuration objects inherit from [`PretrainedConfig`] and can be used to control the model outputs. Read the
    documentation from [`PretrainedConfig`] for more information.

    Args:
        encoder_config (`dict`, *optional*): Configuration of the underlying encoder sub-model.
        decoder_config (`dict`, *optional*): Configuration of the underlying decoder sub-model.
    """

    model_type = "qwen3_tts_tokenizer_12hz"
    sub_configs = {
        "encoder_config": MimiConfig,
        "decoder_config": Qwen3TTSTokenizerV2DecoderConfig,
    }

    def __init__(
        self,
        encoder_config=None,
        decoder_config=None,
        encoder_valid_num_quantizers=16,
        input_sample_rate=24000,
        output_sample_rate=24000,
        decode_upsample_rate=1920,
        encode_downsample_rate=1920,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if encoder_config is None:
            encoder_config = {}
            logger.info("encoder_config is None. Initializing encoder with default values")
        if decoder_config is None:
            decoder_config = {}
            logger.info("decoder_config is None. Initializing decoder with default values")

        self.encoder_config = MimiConfig(**encoder_config)
        self.decoder_config = Qwen3TTSTokenizerV2DecoderConfig(**decoder_config)

        self.encoder_valid_num_quantizers = encoder_valid_num_quantizers
        self.input_sample_rate = input_sample_rate
        self.output_sample_rate = output_sample_rate
        self.decode_upsample_rate = decode_upsample_rate
        self.encode_downsample_rate = encode_downsample_rate


__all__ = ["Qwen3TTSTokenizerV2Config", "Qwen3TTSTokenizerV2DecoderConfig"]
