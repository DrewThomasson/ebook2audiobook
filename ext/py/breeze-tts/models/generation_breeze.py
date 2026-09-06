# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
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
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

import numpy as np
import torch
from torch import nn
from transformers.generation import (
    GenerateDecoderOnlyOutput,
    GenerationConfig,
    GenerationMixin,
    GenerationMode,
)
from transformers.generation.logits_process import LogitsProcessorList
from transformers.generation.stopping_criteria import (
    MaxLengthCriteria,
    StoppingCriteriaList,
)
from transformers.generation.utils import GenerateNonBeamOutput
from transformers.utils import logging

from .logits_process import mask_invalid_codec_token_logits

if TYPE_CHECKING:
    from transformers.generation.streamers import BaseStreamer


logger = logging.get_logger(__name__)


def _extract_decoded_audio_tensor(decoded_audio: Any) -> torch.Tensor:
    if hasattr(decoded_audio, "audio_values"):
        decoded_audio = decoded_audio.audio_values

    while isinstance(decoded_audio, (list, tuple)):
        decoded_audio = decoded_audio[0]

    if isinstance(decoded_audio, np.ndarray):
        decoded_audio = torch.as_tensor(decoded_audio)

    if not isinstance(decoded_audio, torch.Tensor):
        raise TypeError(f"Unsupported decoded audio type: {type(decoded_audio)!r}")

    while decoded_audio.dim() > 1:
        decoded_audio = decoded_audio[0]

    return decoded_audio


@dataclass
class BreezeGenerateOutput(GenerateDecoderOnlyOutput):
    """
    Outputs of BreezeForConditionalGeneration.generate.

    Args:
        sequences (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            The generated sequences. The second dimension (sequence_length) is either equal to `max_length` or shorter
            if all batches finished early due to the `eos_token_id`.
        scores (`tuple(torch.FloatTensor)` *optional*, returned when `output_scores=True`):
            Processed prediction scores of the language modeling head (scores for each vocabulary token before SoftMax)
            at each generation step. Tuple of `torch.FloatTensor` with up to `max_new_tokens` elements (one element for
            each generated token), with each tensor of shape `(batch_size, config.vocab_size)`.
        logits (`tuple(torch.FloatTensor)` *optional*, returned when `output_logits=True`):
            Unprocessed prediction scores of the language modeling head (scores for each vocabulary token before SoftMax)
            at each generation step. Tuple of `torch.FloatTensor` with up to `max_new_tokens` elements (one element for
            each generated token), with each tensor of shape `(batch_size, config.vocab_size)`.
        attentions (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_attentions=True`):
            Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
            `torch.FloatTensor` of shape `(batch_size, num_heads, generated_length, sequence_length)`.
        hidden_states (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_hidden_states=True`):
            Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
            `torch.FloatTensor` of shape `(batch_size, generated_length, hidden_size)`.
        past_key_values (`Cache`, *optional*, returned when `use_cache=True`):
            Returns the model cache, used to speed up decoding. Different models have a different cache format, check
        audio (`list(torch.FloatTensor)` of length `batch_size`):
            The generated audio.
    """

    audio: list[torch.Tensor] | None = None


class BreezeGenerationMixin(GenerationMixin):
    # CFG kwargs that should bypass validation (Breeze requires custom CFG implementation
    # because transformers' UnbatchedClassifierFreeGuidanceLogitsProcessor doesn't pass
    # text_ids_mask and text_ids_len which Breeze model requires)
    # Note: we use 'cfg_*' names to avoid triggering transformers' built-in CFG handling
    _cfg_kwargs = {
        "cfg_scale",
        "cfg_negative_prompt_ids",
        "cfg_negative_prompt_attention_mask",
        "cfg_negative_text_ids_mask",
        "cfg_negative_text_ids_len",
        "cfg_negative_input_values",
        # Dual CFG kwargs
        "cfg_scale_ref",
        "cfg_scale_ins",
        "cfg_uncond_prompt_ids",
        "cfg_uncond_prompt_attention_mask",
        "cfg_uncond_text_ids_mask",
        "cfg_uncond_text_ids_len",
        "cfg_ref_prompt_ids",
        "cfg_ref_prompt_attention_mask",
        "cfg_ref_text_ids_mask",
        "cfg_ref_text_ids_len",
        "cfg_ins_prompt_ids",
        "cfg_ins_prompt_attention_mask",
        "cfg_ins_text_ids_mask",
        "cfg_ins_text_ids_len",
    }

    def _mask_reserved_codec_logits(self, scores: torch.Tensor) -> torch.Tensor:
        return mask_invalid_codec_token_logits(
            scores,
            codebook_size=int(self.config.codec_config.codebook_size),
            token_vocab_size=int(self.config.vocab_size),
        )

    def _reserved_codec_token_ids(self) -> list[int]:
        return list(
            range(
                int(self.config.codec_config.codebook_size),
                int(self.config.vocab_size),
            )
        )

    def _validate_model_kwargs(self, model_kwargs: dict[str, Any]):
        """Override to allow CFG-related kwargs."""
        cfg_kwargs = {
            k: model_kwargs.pop(k)
            for k in list(model_kwargs.keys())
            if k in self._cfg_kwargs
        }
        super()._validate_model_kwargs(model_kwargs)
        model_kwargs.update(cfg_kwargs)

    def _depth_decoder_generate_with_cfg(
        self,
        depth_decoder_input_ids: torch.LongTensor,
        cond_backbone_hidden_state: torch.FloatTensor,
        uncond_backbone_hidden_state: torch.FloatTensor,
        cfg_scale: float,
    ) -> torch.LongTensor:
        """
        Custom depth decoder generation with CFG.

        At each step, we run the depth decoder twice (cond and uncond) and apply CFG to the logits.
        """
        depth_decoder = self.depth_decoder
        generation_config = depth_decoder.generation_config
        num_codebooks = self.config.num_codebooks

        # Get generation params from depth decoder config
        do_sample = generation_config.do_sample
        temperature = generation_config.temperature
        top_p = generation_config.top_p
        top_k = generation_config.top_k

        batch_size = depth_decoder_input_ids.shape[0]
        device = depth_decoder_input_ids.device

        # Initialize sequences with input_ids (which contains placeholder + token0)
        sequences = depth_decoder_input_ids  # [batch_size, 2]

        # Generate tokens 1 to num_codebooks-1 (31 tokens for 32 codebooks)
        for step in range(num_codebooks - 1):
            # Cond forward pass
            cond_outputs = depth_decoder(
                input_ids=sequences,
                backbone_last_hidden_state=cond_backbone_hidden_state,
                use_cache=False,
                return_dict=True,
            )
            cond_logits = cond_outputs.logits[:, -1, :].float()

            # Uncond forward pass
            uncond_outputs = depth_decoder(
                input_ids=sequences,
                backbone_last_hidden_state=uncond_backbone_hidden_state,
                use_cache=False,
                return_dict=True,
            )
            uncond_logits = uncond_outputs.logits[:, -1, :].float()

            # Apply CFG
            next_token_logits = uncond_logits + cfg_scale * (
                cond_logits - uncond_logits
            )
            self._mask_reserved_codec_logits(next_token_logits)

            # Apply temperature
            if temperature is not None and temperature != 1.0:
                next_token_logits = next_token_logits / temperature

            # Sample or argmax
            if do_sample:
                probs = nn.functional.softmax(next_token_logits, dim=-1)

                # Apply top_k
                if top_k is not None and top_k > 0:
                    top_k_probs, top_k_indices = torch.topk(
                        probs, min(top_k, probs.size(-1))
                    )
                    probs = torch.zeros_like(probs).scatter_(
                        -1, top_k_indices, top_k_probs
                    )
                    probs = probs / probs.sum(dim=-1, keepdim=True)

                # Apply top_p
                if top_p is not None and top_p < 1.0:
                    sorted_probs, sorted_indices = torch.sort(probs, descending=True)
                    cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[
                        ..., :-1
                    ].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    indices_to_remove = sorted_indices_to_remove.scatter(
                        -1, sorted_indices, sorted_indices_to_remove
                    )
                    probs = probs.masked_fill(indices_to_remove, 0.0)
                    probs = probs / probs.sum(dim=-1, keepdim=True)

                next_tokens = torch.multinomial(probs, num_samples=1)
            else:
                next_tokens = torch.argmax(next_token_logits, dim=-1, keepdim=True)

            # Append to sequences
            sequences = torch.cat([sequences, next_tokens], dim=-1)

        return sequences

    def _depth_decoder_generate_with_dual_cfg(
        self,
        depth_decoder_input_ids: torch.LongTensor,
        uncond_backbone_hidden_state: torch.FloatTensor,
        ref_backbone_hidden_state: torch.FloatTensor,
        ins_backbone_hidden_state: torch.FloatTensor,
        cfg_scale_ref: float,
        cfg_scale_ins: float,
    ) -> torch.LongTensor:
        """
        Custom depth decoder generation with dual CFG.

        At each step, we run the depth decoder three times (uncond, ref, ins) and apply dual CFG to the logits:
        logits = uncond + cfg_ref * (ref - uncond) + cfg_ins * (ins - uncond)
        """
        depth_decoder = self.depth_decoder
        generation_config = depth_decoder.generation_config
        num_codebooks = self.config.num_codebooks

        do_sample = generation_config.do_sample
        temperature = generation_config.temperature
        top_p = generation_config.top_p
        top_k = generation_config.top_k

        batch_size = depth_decoder_input_ids.shape[0]
        device = depth_decoder_input_ids.device

        sequences = depth_decoder_input_ids  # [batch_size, 2]

        for step in range(num_codebooks - 1):
            # Uncond forward pass
            uncond_outputs = depth_decoder(
                input_ids=sequences,
                backbone_last_hidden_state=uncond_backbone_hidden_state,
                use_cache=False,
                return_dict=True,
            )
            uncond_logits = uncond_outputs.logits[:, -1, :].float()

            # Ref-only forward pass
            ref_outputs = depth_decoder(
                input_ids=sequences,
                backbone_last_hidden_state=ref_backbone_hidden_state,
                use_cache=False,
                return_dict=True,
            )
            ref_logits = ref_outputs.logits[:, -1, :].float()

            # Ins-only forward pass
            ins_outputs = depth_decoder(
                input_ids=sequences,
                backbone_last_hidden_state=ins_backbone_hidden_state,
                use_cache=False,
                return_dict=True,
            )
            ins_logits = ins_outputs.logits[:, -1, :].float()

            # Apply dual CFG
            next_token_logits = (
                uncond_logits
                + cfg_scale_ref * (ref_logits - uncond_logits)
                + cfg_scale_ins * (ins_logits - uncond_logits)
            )
            self._mask_reserved_codec_logits(next_token_logits)

            # Apply temperature
            if temperature is not None and temperature != 1.0:
                next_token_logits = next_token_logits / temperature

            # Sample or argmax
            if do_sample:
                probs = nn.functional.softmax(next_token_logits, dim=-1)

                if top_k is not None and top_k > 0:
                    top_k_probs, top_k_indices = torch.topk(
                        probs, min(top_k, probs.size(-1))
                    )
                    probs = torch.zeros_like(probs).scatter_(
                        -1, top_k_indices, top_k_probs
                    )
                    probs = probs / probs.sum(dim=-1, keepdim=True)

                if top_p is not None and top_p < 1.0:
                    sorted_probs, sorted_indices = torch.sort(probs, descending=True)
                    cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[
                        ..., :-1
                    ].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    indices_to_remove = sorted_indices_to_remove.scatter(
                        -1, sorted_indices, sorted_indices_to_remove
                    )
                    probs = probs.masked_fill(indices_to_remove, 0.0)
                    probs = probs / probs.sum(dim=-1, keepdim=True)

                next_tokens = torch.multinomial(probs, num_samples=1)
            else:
                next_tokens = torch.argmax(next_token_logits, dim=-1, keepdim=True)

            sequences = torch.cat([sequences, next_tokens], dim=-1)

        return sequences

    def _get_stopping_criteria(
        self,
        *args,
        **kwargs,
    ) -> StoppingCriteriaList:
        criteria = super()._get_stopping_criteria(*args, **kwargs)

        kept_criteria = StoppingCriteriaList()
        for criterion in criteria:
            if not isinstance(criterion, MaxLengthCriteria):
                # logger.warning(
                #     f"Breeze does not support {criterion.__class__.__name__} stopping criteria, it will be ignored."
                # )
                pass
            else:
                kept_criteria.append(criterion)
        return kept_criteria

    def _prepare_generation_config(
        self,
        generation_config: GenerationConfig | None,
        use_model_defaults: bool | None = None,
        **kwargs: Any,
    ) -> tuple[GenerationConfig, dict]:
        """
        This method overrides [~generation.utils.GenerationMixin._prepare_generation_config].
        It ensures that the depth decoder generation config is initialized and that passed args as depth_decoder_* are properly handled.
        """
        # Extract CFG kwargs before passing to super() to preserve them
        cfg_kwargs = {
            k: kwargs.pop(k) for k in list(kwargs.keys()) if k in self._cfg_kwargs
        }

        # extract depth decoder kwargs and remove them from the main kwargs
        depth_decoder_kwargs = {
            k[len("depth_decoder_") :]: v
            for k, v in kwargs.items()
            if k.startswith("depth_decoder_")
        }

        # remove the depth decoder keys from the original kwargs
        kwargs = {k: v for k, v in kwargs.items() if not k.startswith("depth_decoder_")}

        # initialize the generation config
        generation_config, model_kwargs = super()._prepare_generation_config(
            generation_config, use_model_defaults, **kwargs
        )

        # Restore CFG kwargs to model_kwargs
        model_kwargs.update(cfg_kwargs)

        self.depth_decoder.generation_config.update(**depth_decoder_kwargs)

        # ensure the depth decoder generation config is valid
        depth_decoder_min_new_tokens = self.depth_decoder.generation_config.min_new_tokens or (self.config.num_codebooks - 1)
        depth_decoder_max_new_tokens = self.depth_decoder.generation_config.max_new_tokens or (self.config.num_codebooks - 1)

        if {depth_decoder_min_new_tokens, depth_decoder_max_new_tokens} != {
            self.config.num_codebooks - 1
        }:
            raise ValueError(
                f"depth_decoder_generation_config's min_new_tokens ({depth_decoder_min_new_tokens}) and max_new_tokens ({depth_decoder_max_new_tokens}) must be equal to self.config.num_codebooks - 1 ({self.config.num_codebooks - 1})"
            )
        elif self.depth_decoder.generation_config.return_dict_in_generate:
            logger.warning(
                "depth_decoder_generation_config.return_dict_in_generate is set to True, but this will be ignored as the depth decoder model does not return a dictionary in generate"
            )
            self.depth_decoder.generation_config.return_dict_in_generate = False

        self.depth_decoder.generation_config.min_new_tokens = (
            depth_decoder_min_new_tokens
        )
        self.depth_decoder.generation_config.max_new_tokens = (
            depth_decoder_max_new_tokens
        )

        # Monkey patch the get_generation_mode method to support Breeze model
        original_get_generation_mode = generation_config.get_generation_mode

        def patched_get_generation_mode(assistant_model=None):
            generation_mode = original_get_generation_mode(assistant_model)
            if generation_mode not in [
                GenerationMode.GREEDY_SEARCH,
                GenerationMode.SAMPLE,
            ]:
                raise ValueError(
                    f"Generation mode {generation_mode} is not supported for Breeze model. Please set generation parameters to use greedy or sampling generation."
                )

            return generation_mode

        generation_config.get_generation_mode = patched_get_generation_mode

        return generation_config, model_kwargs

    def _sample(
        self,
        input_ids: torch.LongTensor,
        logits_processor: LogitsProcessorList,
        stopping_criteria: StoppingCriteriaList,
        generation_config: GenerationConfig,
        synced_gpus: bool = False,
        streamer: Optional["BaseStreamer"] = None,
        **model_kwargs,
    ) -> GenerateNonBeamOutput | torch.LongTensor:
        """
        This method overrides [~generation.utils.GenerationMixin._sample].
        To ease maintenance, modifications are marked with the comment "Breeze specific".

        Indeed, Breeze model requires a custom generation sampling step:
        1. Infer the backbone model to sample the first codebook token
        2. Call generate on the depth decoder with the first codebook token as input_ids to sample the next codebook tokens
        3. Use these generated codebook tokens as input_ids to sample the next first codebook token using the backbone model
        4. Repeat until stopping criteria is met

        Breeze supports two stopping criteria:
        - stop when the generated sequence is at max_length
        - stop when all the generated codebook tokens are the codebook_eos_token_id
        """
        # init values
        # *************** Breeze specific ***************
        pad_token_id = self.config.codebook_pad_token_id
        has_eos_stopping_criteria = generation_config._eos_token_tensor is not None
        # ============================================
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        do_sample = generation_config.do_sample

        # *************** CFG specific ***************
        # Breeze requires custom CFG because transformers' UnbatchedClassifierFreeGuidanceLogitsProcessor
        # doesn't pass text_ids_mask/text_ids_len which Breeze model requires
        # We use 'cfg_scale' instead of 'guidance_scale' to avoid triggering transformers' CFG
        # cfg_scale=1.0: pure cond (normal generation with description)
        # cfg_scale=0.0: pure uncond (generation without description)
        # cfg_scale>1.0: enhance description influence
        cfg_scale = model_kwargs.pop("cfg_scale", 1.0)
        negative_prompt_ids = model_kwargs.pop("cfg_negative_prompt_ids", None)
        negative_prompt_attention_mask = model_kwargs.pop(
            "cfg_negative_prompt_attention_mask", None
        )
        negative_text_ids_mask = model_kwargs.pop("cfg_negative_text_ids_mask", None)
        negative_text_ids_len = model_kwargs.pop("cfg_negative_text_ids_len", None)
        negative_input_values = model_kwargs.pop("cfg_negative_input_values", None)
        use_cfg = cfg_scale != 1.0 and negative_prompt_ids is not None

        # cfg_scale=0 means pure unconditional: swap in the negative prompt as the main input
        # so we only run a single forward pass instead of a wasteful dual pass
        if cfg_scale == 0.0 and negative_prompt_ids is not None:
            input_ids = negative_prompt_ids
            model_kwargs["attention_mask"] = negative_prompt_attention_mask
            if negative_text_ids_mask is not None:
                model_kwargs["text_ids_mask"] = negative_text_ids_mask
            else:
                model_kwargs["text_ids_mask"] = negative_prompt_attention_mask.bool()
            if negative_text_ids_len is not None:
                model_kwargs["text_ids_len"] = negative_text_ids_len
            else:
                model_kwargs["text_ids_len"] = negative_prompt_attention_mask.sum(
                    dim=1
                ).long()
            use_cfg = False
        # ============================================

        # *************** Dual CFG specific ***************
        # Dual CFG: separate scales for reference audio and instruction/performance
        # Formula: logits = uncond + cfg_ref * (ref - uncond) + cfg_ins * (ins - uncond)
        cfg_scale_ref = model_kwargs.pop("cfg_scale_ref", None)
        cfg_scale_ins = model_kwargs.pop("cfg_scale_ins", None)
        uncond_prompt_ids = model_kwargs.pop("cfg_uncond_prompt_ids", None)
        uncond_prompt_attention_mask = model_kwargs.pop(
            "cfg_uncond_prompt_attention_mask", None
        )
        uncond_text_ids_mask = model_kwargs.pop("cfg_uncond_text_ids_mask", None)
        uncond_text_ids_len = model_kwargs.pop("cfg_uncond_text_ids_len", None)
        ref_prompt_ids = model_kwargs.pop("cfg_ref_prompt_ids", None)
        ref_prompt_attention_mask = model_kwargs.pop(
            "cfg_ref_prompt_attention_mask", None
        )
        ref_text_ids_mask = model_kwargs.pop("cfg_ref_text_ids_mask", None)
        ref_text_ids_len = model_kwargs.pop("cfg_ref_text_ids_len", None)
        ins_prompt_ids = model_kwargs.pop("cfg_ins_prompt_ids", None)
        ins_prompt_attention_mask = model_kwargs.pop(
            "cfg_ins_prompt_attention_mask", None
        )
        ins_text_ids_mask = model_kwargs.pop("cfg_ins_text_ids_mask", None)
        ins_text_ids_len = model_kwargs.pop("cfg_ins_text_ids_len", None)
        use_dual_cfg = (
            cfg_scale_ref is not None
            and cfg_scale_ins is not None
            and uncond_prompt_ids is not None
            and ref_prompt_ids is not None
            and ins_prompt_ids is not None
        )
        if use_dual_cfg:
            use_cfg = False  # disable single CFG when dual CFG is active
        # ============================================

        # init attention / hidden states / scores tuples
        scores = () if (return_dict_in_generate and output_scores) else None
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        decoder_attentions = (
            () if (return_dict_in_generate and output_attentions) else None
        )
        decoder_hidden_states = (
            () if (return_dict_in_generate and output_hidden_states) else None
        )

        # keep track of which sequences are already finished
        batch_size, cur_len = input_ids.shape[:2]
        this_peer_finished = False
        unfinished_sequences = torch.ones(
            batch_size, dtype=torch.long, device=input_ids.device
        )
        model_kwargs = self._get_initial_cache_position(
            cur_len, input_ids.device, model_kwargs
        )

        # *************** CFG specific ***************
        if use_cfg:
            # Start with a copy of model_kwargs to get use_cache and other necessary params
            # but exclude attention_mask, text_ids_mask, text_ids_len, cache_position which need to be recomputed
            negative_model_kwargs = {
                k: v
                for k, v in model_kwargs.items()
                if k
                not in [
                    "attention_mask",
                    "text_ids_mask",
                    "text_ids_len",
                    "cache_position",
                    "past_key_values",
                ]
            }
            negative_model_kwargs["attention_mask"] = negative_prompt_attention_mask
            # Override input_values for negative prompt if provided (e.g. prompt audio for ref audio mode)
            if negative_input_values is not None:
                negative_model_kwargs["input_values"] = negative_input_values
            # Use pre-computed text_ids_mask and text_ids_len if provided, otherwise fall back to computing from attention_mask
            # Pre-computed values ensure correct position_ids generation in text encoder (one segment per sample)
            if negative_text_ids_mask is not None:
                negative_model_kwargs["text_ids_mask"] = negative_text_ids_mask
            else:
                negative_model_kwargs["text_ids_mask"] = (
                    negative_prompt_attention_mask.bool()
                )
            if negative_text_ids_len is not None:
                negative_model_kwargs["text_ids_len"] = negative_text_ids_len
            else:
                negative_model_kwargs["text_ids_len"] = (
                    negative_prompt_attention_mask.sum(dim=1).long()
                )
            negative_model_kwargs = self._get_initial_cache_position(
                negative_prompt_ids.shape[1],
                negative_prompt_ids.device,
                negative_model_kwargs,
            )
        # ============================================

        # *************** Dual CFG init ***************
        if use_dual_cfg:
            _exclude_keys = {
                "attention_mask",
                "text_ids_mask",
                "text_ids_len",
                "cache_position",
                "past_key_values",
            }

            def _make_branch_kwargs(
                prompt_ids, attn_mask, text_mask, text_len, include_input_values
            ):
                kw = {k: v for k, v in model_kwargs.items() if k not in _exclude_keys}
                kw["attention_mask"] = attn_mask
                kw["text_ids_mask"] = text_mask
                kw["text_ids_len"] = text_len
                if not include_input_values:
                    kw.pop("input_values", None)
                return self._get_initial_cache_position(
                    prompt_ids.shape[1], prompt_ids.device, kw
                )

            # uncond: text only (no ref audio, no instruction)
            uncond_model_kwargs = _make_branch_kwargs(
                uncond_prompt_ids,
                uncond_prompt_attention_mask,
                uncond_text_ids_mask,
                uncond_text_ids_len,
                include_input_values=False,
            )
            # ref_cond: ref audio + text (no instruction) — inherits input_values from model_kwargs
            ref_model_kwargs = _make_branch_kwargs(
                ref_prompt_ids,
                ref_prompt_attention_mask,
                ref_text_ids_mask,
                ref_text_ids_len,
                include_input_values=True,
            )
            # ins_cond: instruction + text (no ref audio)
            ins_model_kwargs = _make_branch_kwargs(
                ins_prompt_ids,
                ins_prompt_attention_mask,
                ins_text_ids_mask,
                ins_text_ids_len,
                include_input_values=False,
            )
        # ============================================

        # *************** Breeze specific ***************
        if input_ids.ndim == 2 and model_kwargs.get("inputs_embeds") is None:
            # in the case where the passed input_ids correspond to text tokens, i.e. don't have a third dimension for codebook ids,
            # we need to remove the input length to the MaxLengthCriteria stopping criteria has such input are not returned
            for criterion in stopping_criteria:
                if isinstance(criterion, MaxLengthCriteria):
                    criterion.max_length -= cur_len
        # ============================================

        model_forward = self.__call__
        compile_forward = self._valid_auto_compile_criteria(
            model_kwargs, generation_config
        )
        if compile_forward:
            os.environ["TOKENIZERS_PARALLELISM"] = "0"
            model_forward = self.get_compiled_call(generation_config.compile_config)

        is_prefill = True
        while self._has_unfinished_sequences(
            this_peer_finished,
            synced_gpus,
            device=input_ids.device,
        ):
            # *************** Dual CFG specific ***************
            # In dual CFG mode, skip the main forward pass entirely — only run the 3 branches.
            # We reuse ref_outputs as `outputs` for model_kwargs update and hidden_states
            # (backbone_last_hidden_state from `outputs` is unused since dual CFG computes its own).
            if use_dual_cfg:
                if is_prefill:

                    def _run_branch(prompt_ids, branch_kwargs):
                        mi = self.prepare_inputs_for_generation(
                            prompt_ids, **branch_kwargs
                        )
                        mi.update({"output_hidden_states": True})
                        out = self(**mi, return_dict=True)
                        return out, self._update_model_kwargs_for_generation(
                            out, branch_kwargs
                        )

                    uncond_outputs, uncond_model_kwargs = _run_branch(
                        uncond_prompt_ids, uncond_model_kwargs
                    )
                    ref_outputs, ref_model_kwargs = _run_branch(
                        ref_prompt_ids, ref_model_kwargs
                    )
                    ins_outputs, ins_model_kwargs = _run_branch(
                        ins_prompt_ids, ins_model_kwargs
                    )
                    is_prefill = False
                else:

                    def _run_branch_decode(prompt_ids, branch_kwargs):
                        mi = self.prepare_inputs_for_generation(
                            prompt_ids, **branch_kwargs
                        )
                        mi.update({"output_hidden_states": True})
                        out = model_forward(**mi, return_dict=True)
                        return out, self._update_model_kwargs_for_generation(
                            out, branch_kwargs
                        )

                    uncond_outputs, uncond_model_kwargs = _run_branch_decode(
                        uncond_prompt_ids, uncond_model_kwargs
                    )
                    ref_outputs, ref_model_kwargs = _run_branch_decode(
                        ref_prompt_ids, ref_model_kwargs
                    )
                    ins_outputs, ins_model_kwargs = _run_branch_decode(
                        ins_prompt_ids, ins_model_kwargs
                    )

                # Use ref_outputs as the dummy `outputs` for the rest of the loop
                outputs = ref_outputs
            else:
                # ============================================
                # prepare model inputs
                model_inputs = self.prepare_inputs_for_generation(
                    input_ids, **model_kwargs
                )

                # prepare variable output controls (note: some models won't accept all output controls)
                model_inputs.update(
                    {"output_attentions": output_attentions}
                    if output_attentions
                    else {}
                )
                # *************** Breeze specific ***************
                model_inputs.update({"output_hidden_states": True})
                # ============================================

                if is_prefill:
                    outputs = self(**model_inputs, return_dict=True)
                    # *************** CFG specific ***************
                    if use_cfg:
                        negative_model_inputs = self.prepare_inputs_for_generation(
                            negative_prompt_ids, **negative_model_kwargs
                        )
                        negative_model_inputs.update({"output_hidden_states": True})
                        negative_outputs = self(
                            **negative_model_inputs, return_dict=True
                        )
                        negative_model_kwargs = (
                            self._update_model_kwargs_for_generation(
                                negative_outputs, negative_model_kwargs
                            )
                        )
                    # ============================================
                    is_prefill = False
                else:
                    outputs = model_forward(**model_inputs, return_dict=True)
                    # *************** CFG specific ***************
                    if use_cfg:
                        negative_model_inputs = self.prepare_inputs_for_generation(
                            negative_prompt_ids, **negative_model_kwargs
                        )
                        negative_model_inputs.update({"output_hidden_states": True})
                        negative_outputs = model_forward(
                            **negative_model_inputs, return_dict=True
                        )
                        negative_model_kwargs = (
                            self._update_model_kwargs_for_generation(
                                negative_outputs, negative_model_kwargs
                            )
                        )
                    # ============================================

            # synced_gpus: don't waste resources running the code we don't need; kwargs must be updated before skipping
            model_kwargs = self._update_model_kwargs_for_generation(
                outputs,
                model_kwargs,
            )
            if synced_gpus and this_peer_finished:
                continue

            # Clone is needed to avoid keeping a hanging ref to outputs.logits which may be very large for first iteration
            # (the clone itself is always small)
            next_token_logits = outputs.logits[:, -1, :].clone().float()
            next_token_logits = next_token_logits.to(input_ids.device)

            # *************** CFG specific ***************
            if use_cfg:
                negative_logits = negative_outputs.logits[:, -1, :].clone().float()
                negative_logits = negative_logits.to(input_ids.device)
                # CFG formula: logits = uncond_logits + cfg_scale * (cond_logits - uncond_logits)
                next_token_logits = negative_logits + cfg_scale * (
                    next_token_logits - negative_logits
                )
            # ============================================
            # *************** Dual CFG specific ***************
            if use_dual_cfg:
                uncond_logits = (
                    uncond_outputs.logits[:, -1, :].clone().float().to(input_ids.device)
                )
                ref_logits = (
                    ref_outputs.logits[:, -1, :].clone().float().to(input_ids.device)
                )
                ins_logits = (
                    ins_outputs.logits[:, -1, :].clone().float().to(input_ids.device)
                )
                # Dual CFG: logits = uncond + cfg_ref * (ref - uncond) + cfg_ins * (ins - uncond)
                # Note: next_token_logits from backbone is not used — we don't run a full-cond forward
                next_token_logits = (
                    uncond_logits
                    + cfg_scale_ref * (ref_logits - uncond_logits)
                    + cfg_scale_ins * (ins_logits - uncond_logits)
                )
            # ============================================

            # pre-process distribution
            next_token_scores = logits_processor(input_ids, next_token_logits)
            self._mask_reserved_codec_logits(next_token_scores)

            # Store scores, attentions and hidden_states when required
            if return_dict_in_generate:
                if output_scores:
                    scores += (next_token_scores,)
                if output_logits:
                    raw_logits += (next_token_logits,)
                if output_attentions:
                    decoder_attentions += (outputs.attentions,)

                if output_hidden_states:
                    decoder_hidden_states += (outputs.hidden_states,)

            # token selection
            if do_sample:
                probs = nn.functional.softmax(next_token_scores, dim=-1)
                # TODO (joao): this OP throws "skipping cudagraphs due to ['incompatible ops']", find solution
                # next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)

                def multinomial(probs, num_samples=1):
                    ori_shape = probs.shape[:-1]
                    probs = probs.reshape(-1, probs.shape[-1])
                    samples = torch.multinomial(probs, num_samples=num_samples)
                    samples = samples.reshape([*ori_shape, -1])
                    return samples

                next_tokens = multinomial(probs, num_samples=1).squeeze(-1)
            else:
                next_tokens = torch.argmax(next_token_scores, dim=-1)

            # *************** Breeze specific ***************
            # Detect backbone EOS: backbone predicts token at index vocab_size
            backbone_eos_token_id = self.config.vocab_size
            backbone_eos_mask = next_tokens == backbone_eos_token_id  # (batch_size,)

            # infer the depth decoder only for non-EOS rows
            backbone_last_hidden_state = outputs.hidden_states[-1][:, -1, :]

            # *************** CFG specific for depth decoder ***************
            if use_cfg:
                uncond_backbone_last_hidden_state = negative_outputs.hidden_states[-1][
                    :, -1, :
                ]
            # ============================================
            # *************** Dual CFG specific for depth decoder ***************
            if use_dual_cfg:
                uncond_backbone_last_hidden_state = uncond_outputs.hidden_states[-1][
                    :, -1, :
                ]
                ref_backbone_last_hidden_state = ref_outputs.hidden_states[-1][:, -1, :]
                ins_backbone_last_hidden_state = ins_outputs.hidden_states[-1][:, -1, :]
            # ============================================

            if backbone_last_hidden_state.ndim == 3:
                # patched generate
                (b, patch_size, hidden_size) = backbone_last_hidden_state.shape
                backbone_last_hidden_state = backbone_last_hidden_state.reshape(
                    b * patch_size, hidden_size
                )
                if use_cfg:
                    uncond_backbone_last_hidden_state = (
                        uncond_backbone_last_hidden_state.reshape(
                            b * patch_size, hidden_size
                        )
                    )
                if use_dual_cfg:
                    uncond_backbone_last_hidden_state = (
                        uncond_backbone_last_hidden_state.reshape(
                            b * patch_size, hidden_size
                        )
                    )
                    ref_backbone_last_hidden_state = (
                        ref_backbone_last_hidden_state.reshape(
                            b * patch_size, hidden_size
                        )
                    )
                    ins_backbone_last_hidden_state = (
                        ins_backbone_last_hidden_state.reshape(
                            b * patch_size, hidden_size
                        )
                    )
            else:
                patch_size = 1

            # Preallocate full codebook output with pad tokens.
            # Newer checkpoints return the complete audio frame from the depth decoder,
            # while older ones return only the continuation after the backbone's first codebook.
            num_codebooks = self.config.num_codebooks
            total_rows = batch_size * patch_size if patch_size > 1 else batch_size
            codebook_ids = torch.full(
                (total_rows, num_codebooks),
                pad_token_id,
                device=input_ids.device,
                dtype=input_ids.dtype,
            )

            # Determine which rows need depth decoder (non-EOS and unfinished)
            if patch_size > 1:
                non_eos_mask = ~backbone_eos_mask.reshape(total_rows)
            else:
                non_eos_mask = ~backbone_eos_mask

            # Clamp EOS rows to 0 so they are valid codebook ids for depth decoder input
            first_codebook_ids_clamped = next_tokens.clone()
            first_codebook_ids_clamped[backbone_eos_mask] = 0

            if non_eos_mask.any():
                if patch_size > 1:
                    first_codebook_ids_flat = first_codebook_ids_clamped.reshape(
                        total_rows, 1
                    )
                else:
                    first_codebook_ids_flat = first_codebook_ids_clamped[..., None]

                depth_decoder_input_ids = nn.functional.pad(
                    first_codebook_ids_flat[non_eos_mask], (1, 0), value=0
                )
                bhs = backbone_last_hidden_state[non_eos_mask]

                # *************** Dual CFG specific for depth decoder ***************
                if use_dual_cfg:
                    active_codebook_ids = self._depth_decoder_generate_with_dual_cfg(
                        depth_decoder_input_ids=depth_decoder_input_ids,
                        uncond_backbone_hidden_state=uncond_backbone_last_hidden_state[
                            non_eos_mask
                        ].clone(),
                        ref_backbone_hidden_state=ref_backbone_last_hidden_state[
                            non_eos_mask
                        ].clone(),
                        ins_backbone_hidden_state=ins_backbone_last_hidden_state[
                            non_eos_mask
                        ].clone(),
                        cfg_scale_ref=cfg_scale_ref,
                        cfg_scale_ins=cfg_scale_ins,
                    )
                elif use_cfg:
                    active_codebook_ids = self._depth_decoder_generate_with_cfg(
                        depth_decoder_input_ids=depth_decoder_input_ids,
                        cond_backbone_hidden_state=bhs.clone(),
                        uncond_backbone_hidden_state=uncond_backbone_last_hidden_state[
                            non_eos_mask
                        ].clone(),
                        cfg_scale=cfg_scale,
                    )
                else:
                    depth_decoder_outputs = self.depth_decoder.generate(
                        input_ids=depth_decoder_input_ids,
                        backbone_last_hidden_state=bhs.clone(),
                        suppress_tokens=self._reserved_codec_token_ids(),
                    )
                    active_codebook_ids = (
                        depth_decoder_outputs
                        if isinstance(depth_decoder_outputs, torch.Tensor)
                        else depth_decoder_outputs.sequences
                    )
                # ============================================
                # Remove the placeholder in position 0. Depending on checkpoint vintage,
                # the depth decoder may now return either the full frame or only the
                # continuation after the backbone's first codebook.
                active_codebook_ids = active_codebook_ids[:, 1:]
                if active_codebook_ids.shape[-1] == num_codebooks:
                    normalized_codebook_ids = active_codebook_ids
                elif active_codebook_ids.shape[-1] == num_codebooks - 1:
                    normalized_codebook_ids = torch.cat(
                        [first_codebook_ids_flat[non_eos_mask], active_codebook_ids],
                        dim=-1,
                    )
                else:
                    raise ValueError(
                        "Unexpected depth decoder output width "
                        f"{active_codebook_ids.shape[-1]} after placeholder removal; "
                        f"expected {num_codebooks} or {num_codebooks - 1}."
                    )
                codebook_ids[non_eos_mask] = normalized_codebook_ids

            next_tokens = codebook_ids  # (total_rows, num_codebooks)

            # add sequence dimension
            next_tokens_3d = next_tokens.reshape(
                batch_size, 1, patch_size * next_tokens.shape[-1]
            )

            # finished sentences should have their next token be a padding token
            next_tokens_3d = next_tokens_3d * unfinished_sequences.view(
                batch_size, 1, 1
            ) + pad_token_id * (1 - unfinished_sequences.view(batch_size, 1, 1))

            # update generated ids, model inputs, and length for next step
            if input_ids.ndim == 2:
                input_ids = next_tokens_3d
            else:
                input_ids = torch.cat([input_ids, next_tokens_3d], dim=1)
            # ============================================

            if streamer is not None:
                streamer.put(next_tokens.cpu())

            # *************** Breeze specific ***************
            # Stop sequences where backbone predicted EOS
            unfinished_sequences = unfinished_sequences & ~backbone_eos_mask
            # ============================================
            unfinished_sequences = unfinished_sequences & ~stopping_criteria(
                input_ids, scores
            )
            this_peer_finished = unfinished_sequences.max() == 0
            cur_len += 1

            # This is needed to properly delete outputs.logits which may be very large for first iteration
            # Otherwise a reference to outputs is kept which keeps the logits alive in the next iteration
            del outputs

            # *************** Breeze specific ***************
            if not use_cfg and not use_dual_cfg:
                depth_decoder_outputs = None
            # ============================================

            # *************** CFG specific ***************
            if use_cfg:
                # negative_prompt_ids starts as 2D (batch, seq_len), convert to 3D after first iteration
                if negative_prompt_ids.ndim == 2:
                    negative_prompt_ids = next_tokens_3d
                else:
                    negative_prompt_ids = torch.cat(
                        [negative_prompt_ids, next_tokens_3d], dim=1
                    )
                del negative_outputs
            # ============================================

            # *************** Dual CFG specific ***************
            if use_dual_cfg:

                def _update_branch_ids(prompt_ids):
                    if prompt_ids.ndim == 2:
                        return next_tokens_3d
                    return torch.cat([prompt_ids, next_tokens_3d], dim=1)

                uncond_prompt_ids = _update_branch_ids(uncond_prompt_ids)
                ref_prompt_ids = _update_branch_ids(ref_prompt_ids)
                ins_prompt_ids = _update_branch_ids(ins_prompt_ids)
                del uncond_outputs, ref_outputs, ins_outputs
            # ============================================

        if streamer is not None:
            streamer.end()

        if return_dict_in_generate:
            return GenerateDecoderOnlyOutput(
                sequences=input_ids,
                scores=scores,
                logits=raw_logits,
                attentions=decoder_attentions,
                hidden_states=decoder_hidden_states,
                past_key_values=model_kwargs.get("past_key_values"),
            )
        else:
            return input_ids

    def generate(
        self,
        input_ids: torch.Tensor | None = None,
        input_values: torch.Tensor | None = None,
        input_values_cutoffs: torch.Tensor | None = None,
        generation_config: GenerationConfig | None = None,
        logits_processor: LogitsProcessorList | None = None,
        stopping_criteria: StoppingCriteriaList | None = None,
        synced_gpus: bool | None = None,
        streamer: Optional["BaseStreamer"] = None,
        output_audio: bool | None = False,
        audio_tokenizer=None,
        **kwargs,
    ) -> GenerateNonBeamOutput | torch.LongTensor:
        r"""
        This method overrides [`~generation.utils.GenerationMixin.generate`] to match the specifics of the Breeze model.
        Indeed, Breeze model requires a custom generation sampling step:
        1. Infer the backbone model to sample the first codebook token
        2. Call generate on the depth decoder with the first codebook token as `input_ids` to sample the next codebook tokens
        3. Use these generated codebook tokens as `input_ids` to sample the next first codebook token using the backbone model
        4. Repeat until stopping criteria is met

        <Tip warning={true}>

        Most generation-controlling parameters are set in `generation_config` which, if not passed, will be set to the
        model's default generation configuration. You can override any `generation_config` by passing the corresponding
        parameters to generate(), e.g. `.generate(inputs, do_sample=True)`.
        </Tip>

        Parameters:
            inputs_ids (`torch.Tensor` of shape (batch_size, seq_length), *optional*):
                The sequence used as a prompt for the backbone model.
            input_values (`torch.Tensor` of shape (batch_size, channels, max_concatenated_audio_length), *optional*):
                The batched audio input values, where each batch entry contains the concatenation of all audio segments for that entry.
                These values will be encoded into codebook tokens using the codec model and merged with the text input ids provided in `input_ids`.
            input_values_cutoffs (`torch.Tensor` of shape (batch_size, max_num_audio), *optional*):
                Specify the end positions of audio segments within each batch entry, relative to the concatenated audio input.
                If a batch entry has fewer segments than the maximum, it is padded with -1. For example, in a batch of 2 sequences
                where the first contains 2 audio segments of length l1, and the second contains 1 audio segment of length l2,
                the input_values_cutoffs would be: [[l1, 2 * l1], [l2, -1]].
            generation_config ([`~generation.GenerationConfig`], *optional*):
                The generation configuration to be used as base parametrization for the generation call. `**kwargs`
                passed to generate matching the attributes of `generation_config` will override them. If
                `generation_config` is not provided, the default will be used, which has the following loading
                priority: 1) from the `generation_config.json` model file, if it exists; 2) from the model
                configuration. Please note that unspecified parameters will inherit [`~generation.GenerationConfig`]'s
                default values, whose documentation should be checked to parameterize generation.
            logits_processor (`LogitsProcessorList`, *optional*):
                Custom logits processors that complement the default logits processors built from arguments and
                generation config. If a logit processor is passed that is already created with the arguments or a
                generation config an error is thrown. This feature is intended for advanced users.
            stopping_criteria (`StoppingCriteriaList`, *optional*):
                Custom stopping criteria that complements the default stopping criteria built from arguments and a
                generation config. If a stopping criteria is passed that is already created with the arguments or a
                generation config an error is thrown. If your stopping criteria depends on the `scores` input, make
                sure you pass `return_dict_in_generate=True, output_scores=True` to `generate`. This feature is
                intended for advanced users.
            synced_gpus (`bool`, *optional*):
                Whether to continue running the while loop until max_length. Unless overridden, this flag will be set
                to `True` if using `FullyShardedDataParallel` or DeepSpeed ZeRO Stage 3 with multiple GPUs to avoid
                deadlocking if one GPU finishes generating before other GPUs. Otherwise, defaults to `False`.
            streamer (`BaseStreamer`, *optional*):
                Streamer object that will be used to stream the generated sequences. Generated tokens are passed
                through `streamer.put(token_ids)` and the streamer is responsible for any further processing.
            output_audio (`bool`, *optional*):
                Whether to return the generated audio.
            kwargs (`dict[str, Any]`, *optional*):
                Ad hoc parametrization of `generation_config` and/or additional model-specific kwargs that will be
                forwarded to the `forward` function of the model. Depth decoder specific kwargs should be prefixed with *depth_decoder_*.

        Return:
            [`BreezeGenerateOutput`] or `torch.LongTensor` or `list[torch.FloatTensor]`: A [`BreezeGenerateOutput`]
            (if `return_dict_in_generate=True` or when `config.return_dict_in_generate=True`) or a `torch.LongTensor` when `output_audio=False`
            or a `list[torch.FloatTensor]` otherwise.

        Example:

        ```python
        >>> from models.breeze import BreezeForConditionalGeneration
        from transformers import AutoTokenizer
        >>> from datasets import load_dataset, Audio

        >>> model_id = "/path/to/breeze-model"
        >>> torch_device = "cuda" if torch.cuda.is_available() else "cpu"

        >>> processor = AutoProcessor.from_pretrained(model_id)

        >>> ds = load_dataset("hf-internal-testing/dailytalk-dummy", split="train")
        >>> # ensure the audio is 24kHz
        >>> ds = ds.cast_column("audio", Audio(sampling_rate=24000))

        >>> conversation = []
        >>> # prepare a conversation with text and corresponding audio
        >>> for text, audio, speaker_id in zip(ds[:4]["text"], ds[:4]["audio"], ds[:4]["speaker_id"]):
        ...     conversation.append(
        ...         {
        ...             "role": f"{speaker_id}",
        ...             "content": [{"type": "text", "text": text}, {"type": "audio", "path": audio["array"]}],
        ...         }
        ...     )

        >>> # text prompt
        >>> conversation.append({"role": f"{ds[4]['speaker_id']}", "content": [{"type": "text", "text": ds[4]["text"]}]})

        >>> inputs = processor.apply_chat_template(
        ...     conversation,
        ...     tokenize=True,
        ...     return_dict=True,
        ... ).to(torch_device)

        >>> model = BreezeForConditionalGeneration.from_pretrained(model_id, device_map=torch_device)
        >>> audio = model.generate(**inputs, output_audio=True)
        >>> processor.save_audio(audio, "output.wav")
        ```
        """
        generate_output = super().generate(
            input_ids=input_ids,
            input_values=input_values,
            input_values_cutoffs=input_values_cutoffs,
            generation_config=generation_config,
            logits_processor=logits_processor,
            stopping_criteria=stopping_criteria,
            synced_gpus=synced_gpus,
            streamer=streamer,
            **kwargs,
        )

        generate_returned_dict = not isinstance(generate_output, torch.Tensor)
        audio = None
        if output_audio:
            generated_audio_codes = (
                generate_output.sequences if generate_returned_dict else generate_output
            )

            # reshape for patched audio tokens, if patch size == 1, this does nothing
            patch_size = generated_audio_codes.shape[-1] // self.config.num_codebooks
            generated_audio_codes = generated_audio_codes.reshape(
                generated_audio_codes.shape[0],
                generated_audio_codes.shape[1] * patch_size,
                generated_audio_codes.shape[2] // patch_size,
            )

            # infer the codec model
            audio = []
            with torch.no_grad():
                # =======================================
                # TODO: @eustlb, this should be batched !!!
                # but requires making sure batched inference of the codec model works as intended
                for sample_index, audio_codes_batch in enumerate(generated_audio_codes):
                    # Truncate at first pad frame (EOS rows are stored as all-pad)
                    is_pad_frame = (
                        audio_codes_batch == self.config.codebook_pad_token_id
                    ).all(dim=-1)
                    eos_idxs = is_pad_frame.nonzero()
                    if eos_idxs.numel() != 0:
                        cutoff_idx = eos_idxs.min()
                    else:
                        cutoff_idx = audio_codes_batch.shape[0]

                    audio_codes_batch = audio_codes_batch[:cutoff_idx]

                    if cutoff_idx == 0:
                        # write log to file
                        with open(
                            "/tmp/breeze_generation_warnings.log", "a"
                        ) as log_file:
                            log_file.write(
                                "[no-code] No codebook tokens were generated, generating silent audio.\n"
                            )

                        # generate silent audio if no codebook tokens were generated
                        num_codebooks = getattr(
                            self.codec_model,
                            "num_codebooks",
                            getattr(
                                self.config,
                                "num_codebooks",
                                audio_codes_batch.shape[-1],
                            ),
                        )
                        dummy_codes = torch.ones(
                            1,
                            num_codebooks,
                            device=audio_codes_batch.device,
                            dtype=audio_codes_batch.dtype,
                        )
                        logger.warning(
                            "No codebook tokens were generated, generating silent audio."
                        )
                        if audio_tokenizer is not None:
                            codec_decode_output = audio_tokenizer.decode(
                                {"audio_codes": dummy_codes}
                            )
                            decode_audio = _extract_decoded_audio_tensor(
                                codec_decode_output
                            )
                        else:
                            codec_decode_output = self.codec_model.decode(
                                dummy_codes.transpose(0, 1).unsqueeze(0)
                            )
                            decode_audio = _extract_decoded_audio_tensor(
                                codec_decode_output
                            )
                    else:
                        codebook_size = int(self.config.codec_config.codebook_size)
                        invalid_codes = (audio_codes_batch < 0) | (
                            audio_codes_batch >= codebook_size
                        )
                        if invalid_codes.any():
                            frame_index, codebook_index = invalid_codes.nonzero()[
                                0
                            ].tolist()
                            token_id = int(
                                audio_codes_batch[frame_index, codebook_index]
                            )
                            raise ValueError(
                                "Generated codec token is outside the decoder codebook range: "
                                f"sample={sample_index}, frame={frame_index}, "
                                f"codebook={codebook_index}, token={token_id}, "
                                f"valid=[0, {codebook_size - 1}]"
                            )

                        if (
                            audio_tokenizer is None
                        ):  # 兼容qwen3, 因为qwen3 tokenizer没有cardinality属性
                            if (
                                audio_codes_batch.max().item()
                                >= self.codec_model.quantizer.cardinality
                            ):
                                audio_codes_batch = torch.clamp(
                                    audio_codes_batch,
                                    0,
                                    self.codec_model.quantizer.cardinality - 1,
                                )

                        if audio_tokenizer is not None:
                            codec_decode_output = audio_tokenizer.decode(
                                {"audio_codes": [audio_codes_batch]}
                            )
                            decode_audio = _extract_decoded_audio_tensor(
                                codec_decode_output
                            )
                        else:
                            codec_decode_output = self.codec_model.decode(
                                audio_codes_batch.transpose(0, 1).unsqueeze(0)
                            )
                            decode_audio = _extract_decoded_audio_tensor(
                                codec_decode_output
                            )

                        codes_min_max = (
                            audio_codes_batch.min().item(),
                            audio_codes_batch.max().item(),
                        )
                        # logger.info(f"Decoded audio codes with min/max values: {codes_min_max}")
                    audio.append(decode_audio)
                # =======================================

        if generate_returned_dict:
            return BreezeGenerateOutput(audio=audio, **generate_output)
        elif output_audio:
            return audio
        else:
            return generate_output
