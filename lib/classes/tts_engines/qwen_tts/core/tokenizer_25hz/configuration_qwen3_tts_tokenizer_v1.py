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
"""Qwen3TTSTokenizerV1 model configuration"""

from transformers.configuration_utils import PretrainedConfig
from transformers.utils import logging


logger = logging.get_logger(__name__)


class Qwen3TTSTokenizerV1DecoderDiTConfig(PretrainedConfig):
    r"""
    This is the configuration class to store the configuration of the Qwen3TTSTokenizerV1DecoderToken2WavDiT.
    It defines the architecture of the DiT model, which is used for generating mel-spectrograms from tokens.

    Args:
        hidden_size (`int`, *optional*, defaults to 1024):
            The dimension of the model.
        num_hidden_layers (`int`, *optional*, defaults to 22):
            The number of transformer blocks in the DiT model.
        num_attention_heads (`int`, *optional*, defaults to 16):
            The number of attention heads in each transformer block.
        ff_mult (`int`, *optional*, defaults to 2):
            The multiplier for the feedforward layer in each transformer block.
        emb_dim (`int`, *optional*, defaults to 512):
            The dimension of the embedding layer.
        head_dim (`int`, *optional*, defaults to 64):
            The dimension of each attention head.
        repeats (`int`, *optional*, defaults to 2):
            The number of times the codec embeddings are repeated.
        num_embeds (`int`, *optional*, defaults to 8193):
            The number of unique embeddings in the codec.
        mel_dim (`int`, *optional*, defaults to 80):
            The dimension of the mel-spectrogram.
        dropout (`float`, *optional*, defaults to 0.1):
            The dropout rate for the transformer blocks.

        enc_emb_dim (`int`, *optional*, defaults to 192):
            The dimension of the pre-trained speaker embedding.
        enc_dim (`int`, *optional*, defaults to 128):
            The dimension of the encoder output.
        enc_channels (`list[int]`, *optional*, defaults to `[256, 256, 256, 256, 768]`):
            A list of output channels for each TDNN/SERes2Net layer in the encoder.
        enc_kernel_sizes (`list[int]`, *optional*, defaults to `[5, 3, 3, 3, 1]`):
            A list of kernel sizes for each layer in the encoder.
        enc_dilations (`list[int]`, *optional*, defaults to `[1, 2, 3, 4, 1]`):
            A list of dilations for each layer in the encoder.
        enc_attention_channels (`int`, *optional*, defaults to 64):
            The number of attention channels in the SqueezeExcitationBlock.
        enc_res2net_scale (`int`, *optional*, defaults to 2):
            The scale of the Res2Net block in the encoder.
        enc_se_channels (`int`, *optional*, defaults to 64):
            The number of output channels after squeeze in the SqueezeExcitationBlock.
    """

    model_type = "qwen3_tts_tokenizer_v1_decoder_dit"

    def __init__(
        self,
        hidden_size=1024,
        num_hidden_layers=22,
        num_attention_heads=16,
        ff_mult=2,
        emb_dim=512,
        head_dim=64,
        rope_theta=10000.0,
        max_position_embeddings=32768,
        block_size=24,
        look_ahead_layers=[10],
        look_backward_layers=[0, 20],
        repeats=2,
        num_embeds=8193,
        mel_dim=80,
        dropout=0.1,
        enc_emb_dim=192,
        enc_dim=128,
        enc_channels=[256, 256, 256, 256, 768],
        enc_kernel_sizes=[5, 3, 3, 3, 1],
        enc_dilations=[1, 2, 3, 4, 1],
        enc_attention_channels=64,
        enc_res2net_scale=2,
        enc_se_channels=64,
        **kwargs,
    ):
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.ff_mult = ff_mult
        self.emb_dim = emb_dim
        self.head_dim = head_dim
        self.rope_theta = rope_theta
        self.max_position_embeddings = max_position_embeddings
        self.block_size = block_size
        self.look_ahead_layers = look_ahead_layers
        self.look_backward_layers = look_backward_layers
        self.repeats = repeats
        self.num_embeds = num_embeds
        self.mel_dim = mel_dim
        self.dropout = dropout
        self.enc_emb_dim = enc_emb_dim
        self.enc_dim = enc_dim
        self.enc_channels = enc_channels
        self.enc_kernel_sizes = enc_kernel_sizes
        self.enc_dilations = enc_dilations
        self.enc_attention_channels = enc_attention_channels
        self.enc_res2net_scale = enc_res2net_scale
        self.enc_se_channels = enc_se_channels
        super().__init__(**kwargs)


class Qwen3TTSTokenizerV1DecoderBigVGANConfig(PretrainedConfig):
    r"""
    This is the configuration class to store the configuration of the Qwen3TTSTokenizerV1DecoderToken2WavBigVGAN module.
    It defines the architecture of the BigVGAN model, which is used for converting mel-spectrograms to waveforms.

    Args:
        mel_dim (`int`, *optional*, defaults to 80):
            The dimension of the mel-spectrogram.
        upsample_initial_channel (`int`, *optional*, defaults to 1536):
            The number of channels in the initial upsampling layer.
        resblock_kernel_sizes (`list[int]`, *optional*, defaults to `[3, 7, 11]`):
            A list of kernel sizes for each residual block.
        resblock_dilation_sizes (`list[list[int]]`, *optional*, defaults to `[[1, 3, 5], [1, 3, 5], [1, 3, 5]]`):
            A list of dilation sizes for each residual block.
        upsample_rates (`list[int]`, *optional*, defaults to `[5, 3, 2, 2, 2, 2]`):
            A list of upsampling rates for each upsampling layer.
        upsample_kernel_sizes (`list[int]`, *optional*, defaults to `[11, 7, 4, 4, 4, 4]`):
            A list of kernel sizes for each upsampling layer.
    """

    model_type = "qwen3_tts_tokenizer_v1_decoder_bigvgan"

    def __init__(
        self,
        mel_dim=80,
        upsample_initial_channel=1536,
        resblock_kernel_sizes=[3, 7, 11],
        resblock_dilation_sizes=[[1, 3, 5], [1, 3, 5], [1, 3, 5]],
        upsample_rates=[5, 3, 2, 2, 2, 2],
        upsample_kernel_sizes=[11, 7, 4, 4, 4, 4],
        **kwargs,
    ):
        self.mel_dim = mel_dim
        self.upsample_initial_channel = upsample_initial_channel
        self.resblock_kernel_sizes = resblock_kernel_sizes
        self.resblock_dilation_sizes = resblock_dilation_sizes
        self.upsample_rates = upsample_rates
        self.upsample_kernel_sizes = upsample_kernel_sizes
        super().__init__(**kwargs)


class Qwen3TTSTokenizerV1DecoderConfig(PretrainedConfig):
    r"""
    This is the configuration class to store the configuration of a [`Qwen3TTSTokenizerV1DecoderConfig`].

    Configuration objects inherit from [`PretrainedConfig`] and can be used to control the model outputs. Read the
    documentation from [`PretrainedConfig`] for more information.

    Args:
        dit_config ([`DiT_Args`], *optional*):
            Configuration class for the Diffusion Transformer (DiT) module responsible for generating mel-spectrograms.
        bigvgan_config ([`BigVGAN_Args`], *optional*):
            Configuration class for the BigVGAN module responsible for converting mel-spectrograms to waveforms.
    """

    model_type = "qwen3_tts_tokenizer_v1_decoder"
    sub_configs = {
        "dit_config": Qwen3TTSTokenizerV1DecoderDiTConfig,
        "bigvgan_config": Qwen3TTSTokenizerV1DecoderBigVGANConfig,
    }

    def __init__(self, dit_config=None, bigvgan_config=None, **kwargs):
        if dit_config is None:
            dit_config = {}
        if bigvgan_config is None:
            bigvgan_config = {}
        self.dit_config = Qwen3TTSTokenizerV1DecoderDiTConfig(**dit_config)
        self.bigvgan_config = Qwen3TTSTokenizerV1DecoderBigVGANConfig(**bigvgan_config)
        super().__init__(**kwargs)


class Qwen3TTSTokenizerV1EncoderConfig(PretrainedConfig):
    r"""
    This is the configuration class to store the configuration of the Qwen3TTSTokenizerV1 Encoder.

    The encoder typically takes mel-spectrogram features and produces high-level audio representations, then (optionally)
    applies an Audio-VQ module (e.g., GRVQ) to discretize continuous representations into codes.

    Args:
        n_mels (`int`, *optional*, defaults to 128):
            Number of mel bins in the input mel-spectrogram.
        n_ctx (`int`, *optional*, defaults to 1500):
            Maximum input sequence length (in frames/tokens) for the encoder.
        n_state (`int`, *optional*, defaults to 1280):
            Hidden size (model dimension) of the encoder transformer.
        n_head (`int`, *optional*, defaults to 20):
            Number of attention heads in each transformer layer.
        n_layer (`int`, *optional*, defaults to 32):
            Number of transformer layers.
        n_window (`int`, *optional*, defaults to 100):
            Window size used by the model for local attention / chunking (implementation-dependent).
        output_dim (`int`, *optional*, defaults to 3584):
            Output feature dimension produced by the encoder head (before/after projection, implementation-dependent).

        grad_checkpointing (`bool`, *optional*, defaults to `False`):
            Whether to enable gradient checkpointing to reduce memory usage during training.
        enable_mp (`bool`, *optional*, defaults to `False`):
            Whether to enable model parallel features (implementation-dependent).
        audio_sequence_parallel (`bool`, *optional*, defaults to `False`):
            Whether to enable sequence parallelism for audio branch (implementation-dependent).

        audio_vq_type (`str`, *optional*, defaults to `"GRVQ"`):
            Type of audio vector-quantization module. Common choices: `"GRVQ"`, `"RVQ"`, etc.
        audio_vq_layers (`int`, *optional*, defaults to 6):
            Number of VQ layers / quantizers (e.g., number of residual quantizers for RVQ/GRVQ-like designs).
        audio_vq_codebook_size (`int`, *optional*, defaults to 32768):
            Size of each codebook (number of entries).
        audio_vq_codebook_dim (`int`, *optional*, defaults to 1280):
            Dimension of codebook vectors (often equals encoder hidden size).
        audio_vq_pe (`bool`, *optional*, defaults to `True`):
            Whether to use positional encoding (or position embeddings) inside the VQ module.
        audio_vq_ds_rate (`int`, *optional*, defaults to 2):
            Downsampling rate applied before VQ (e.g., temporal downsample factor).
    """

    model_type = "qwen3_tts_tokenizer_v1_encoder"

    def __init__(
        self,
        n_mels=128,
        n_ctx=1500,
        n_state=1280,
        n_head=20,
        n_layer=32,
        n_window=100,
        output_dim=3584,
        grad_checkpointing=False,
        enable_mp=False,
        audio_sequence_parallel=False,
        audio_vq_type="GRVQ",
        audio_vq_layers=6,
        audio_vq_codebook_size=32768,
        audio_vq_codebook_dim=1280,
        audio_vq_pe=True,
        audio_vq_ds_rate=2,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.n_mels = n_mels
        self.n_ctx = n_ctx
        self.n_state = n_state
        self.n_head = n_head
        self.n_layer = n_layer
        self.n_window = n_window
        self.output_dim = output_dim
        self.grad_checkpointing = grad_checkpointing
        self.enable_mp = enable_mp
        self.audio_sequence_parallel = audio_sequence_parallel
        self.audio_vq_type = audio_vq_type
        self.audio_vq_layers = audio_vq_layers
        self.audio_vq_codebook_size = audio_vq_codebook_size
        self.audio_vq_codebook_dim = audio_vq_codebook_dim
        self.audio_vq_pe = audio_vq_pe
        self.audio_vq_ds_rate = audio_vq_ds_rate


class Qwen3TTSTokenizerV1Config(PretrainedConfig):
    """
    This is the configuration class to store the configuration of a [`Qwen3TTSTokenizerV1Config`]. It is used to instantiate a Qwen3TTSTokenizerV1Model
    model according to the specified sub-models configurations, defining the model architecture.

    Configuration objects inherit from [`PretrainedConfig`] and can be used to control the model outputs. Read the
    documentation from [`PretrainedConfig`] for more information.

    Args:
        encoder_config (`dict`, *optional*): Configuration of the underlying encoder sub-model.
        decoder_config (`dict`, *optional*): Configuration of the underlying decoder sub-model.
    """

    model_type = "qwen3_tts_tokenizer_25hz"
    sub_configs = {
        "encoder_config": Qwen3TTSTokenizerV1EncoderConfig,
        "decoder_config": Qwen3TTSTokenizerV1DecoderConfig,
    }

    def __init__(
        self,
        encoder_config=None,
        decoder_config=None,
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

        self.encoder_config = Qwen3TTSTokenizerV1EncoderConfig(**encoder_config)
        self.decoder_config = Qwen3TTSTokenizerV1DecoderConfig(**decoder_config)

        self.input_sample_rate = input_sample_rate
        self.output_sample_rate = output_sample_rate
        self.decode_upsample_rate = decode_upsample_rate
        self.encode_downsample_rate = encode_downsample_rate


__all__ = [
    "Qwen3TTSTokenizerV1Config", 
    "Qwen3TTSTokenizerV1EncoderConfig",
    "Qwen3TTSTokenizerV1DecoderConfig", 
    "Qwen3TTSTokenizerV1DecoderBigVGANConfig",
    "Qwen3TTSTokenizerV1DecoderDiTConfig"
]
