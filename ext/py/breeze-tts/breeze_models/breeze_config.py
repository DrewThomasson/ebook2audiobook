import os

from transformers import AutoConfig, AutoModel
from transformers.models.t5gemma.configuration_t5gemma import T5GemmaModuleConfig
from transformers.models.t5gemma.modeling_t5gemma import T5GemmaEncoder

from .breeze_base_config import BreezeConfig as BreezeConfig_transformers
from .breeze_base_config import BreezeDepthDecoderConfig
from .t5gemma2_compat import T5Gemma2TextConfig, T5Gemma2TextEncoder


class T5GemmaEncoderWrapper(T5GemmaEncoder):
    config_class = T5GemmaModuleConfig


# register T5GemmaModuleConfig
AutoConfig.register("t5_gemma_module", T5GemmaModuleConfig)
AutoModel.register(T5GemmaModuleConfig, T5GemmaEncoderWrapper)
AutoConfig.register("t5gemma2_text", T5Gemma2TextConfig)
AutoModel.register(T5Gemma2TextConfig, T5Gemma2TextEncoder)


# Update BreezeConfig to handle text_encoder_config properly
class BreezeConfig(BreezeConfig_transformers):
    model_type = "breeze"

    sub_configs = {
        "codec_config": AutoConfig,
        "depth_decoder_config": BreezeDepthDecoderConfig,
    }

    def __init__(self, **kwargs):
        text_encoder_config = kwargs.get("text_encoder_config", None)
        super().__init__(**kwargs)

        if text_encoder_config is None:
            self.text_encoder_config = None
        elif isinstance(text_encoder_config, str):
            assert os.path.isdir(text_encoder_config), (
                f"text_encoder_config as str must be a valid directory path: '{text_encoder_config}'"
            )
            self.text_encoder_config = AutoConfig.from_pretrained(text_encoder_config)
        elif isinstance(text_encoder_config, dict):
            self.text_encoder_config = AutoConfig.for_model(**text_encoder_config)
        else:
            raise ValueError(
                f"text_encoder_config must be a str (path), dict, or AutoConfig instance. but got {type(text_encoder_config)}"
            )


AutoConfig.register(
    "breeze_depth_decoder_model", BreezeDepthDecoderConfig, exist_ok=True
)
AutoConfig.register("breeze", BreezeConfig, exist_ok=True)
