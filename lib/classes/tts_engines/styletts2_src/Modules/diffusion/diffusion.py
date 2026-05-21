from math import pi
from random import randint
from typing import Any, Optional, Sequence, Tuple, Union

import torch
from einops import rearrange
from torch import Tensor, nn
from tqdm import tqdm

from .utils import *
from .sampler import *

"""
Diffusion Classes (generic for 1d data)
"""


class Model1d(nn.Module):
    def __init__(self, unet_type: str = "base", **kwargs):
        super().__init__()
        diffusion_kwargs, kwargs = groupby("diffusion_", kwargs)
        self.unet = None
        self.diffusion = None

    def forward(self, x: Tensor, **kwargs) -> Tensor:
        return self.diffusion(x, **kwargs)

    def sample(self, *args, **kwargs) -> Tensor:
        return self.diffusion.sample(*args, **kwargs)


"""
Audio Diffusion Classes (specific for 1d audio data)
"""


def get_default_model_kwargs():
    return dict(
        channels=128,
        patch_size=16,
        multipliers=[1, 2, 4, 4, 4, 4, 4],
        factors=[4, 4, 4, 2, 2, 2],
        num_blocks=[2, 2, 2, 2, 2, 2],
        attentions=[0, 0, 0, 1, 1, 1, 1],
        attention_heads=8,
        attention_features=64,
        attention_multiplier=2,
        attention_use_rel_pos=False,
        diffusion_type="v",
        diffusion_sigma_distribution=UniformDistribution(),
    )


def get_default_sampling_kwargs():
    return dict(sigma_schedule=LinearSchedule(), sampler=VSampler(), clamp=True)


class AudioDiffusionModel(Model1d):
    def __init__(self, **kwargs):
        super().__init__(**{**get_default_model_kwargs(), **kwargs})

    def sample(self, *args, **kwargs):
        return super().sample(*args, **{**get_default_sampling_kwargs(), **kwargs})


class AudioDiffusionConditional(Model1d):
    def __init__(
        self,
        embedding_features: int,
        embedding_max_length: int,
        embedding_mask_proba: float = 0.1,
        **kwargs,
    ):
        self.embedding_mask_proba = embedding_mask_proba
        default_kwargs = dict(
            **get_default_model_kwargs(),
            unet_type="cfg",
            context_embedding_features=embedding_features,
            context_embedding_max_length=embedding_max_length,
        )
        super().__init__(**{**default_kwargs, **kwargs})

    def forward(self, *args, **kwargs):
        default_kwargs = dict(embedding_mask_proba=self.embedding_mask_proba)
        return super().forward(*args, **{**default_kwargs, **kwargs})

    def sample(self, *args, **kwargs):
        default_kwargs = dict(
            **get_default_sampling_kwargs(),
            embedding_scale=5.0,
        )
        return super().sample(*args, **{**default_kwargs, **kwargs})


