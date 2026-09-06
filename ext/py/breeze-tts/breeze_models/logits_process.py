from __future__ import annotations

import torch
from transformers.generation.logits_process import LogitsProcessor


def mask_invalid_codec_token_logits(
    scores: torch.Tensor,
    *,
    codebook_size: int,
    token_vocab_size: int,
) -> torch.Tensor:
    """Mask reserved model tokens that are not valid codec codebook entries."""
    if codebook_size <= 0 or token_vocab_size < codebook_size:
        raise ValueError(
            f"Invalid codec token range: codebook_size={codebook_size}, "
            f"token_vocab_size={token_vocab_size}"
        )
    if token_vocab_size > scores.shape[-1]:
        raise ValueError(
            f"token_vocab_size={token_vocab_size} exceeds logits size {scores.shape[-1]}"
        )
    if codebook_size < token_vocab_size:
        scores[..., codebook_size:token_vocab_size] = float("-inf")
    return scores


class GeneratedTokenRepetitionPenaltyLogitsProcessor(LogitsProcessor):
    """Apply HF-style repetition penalty only to generated, in-vocab tokens."""

    def __init__(self, penalty: float) -> None:
        if penalty <= 0:
            raise ValueError("penalty must be > 0")
        self.penalty = float(penalty)

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor
    ) -> torch.FloatTensor:
        # Breeze starts generation with 2D text prompt IDs, then replaces them
        # with 3D generated codec frames after the first decoding step.
        if input_ids.ndim == 2:
            return scores
        if input_ids.ndim != 3:
            raise ValueError(
                f"Expected 2D prompt IDs or 3D codec frames, got {input_ids.ndim}D"
            )

        generated_ids = input_ids[..., 0]
        if self.penalty == 1.0 or generated_ids.numel() == 0:
            return scores

        vocab_size = scores.shape[-1]
        valid = (generated_ids >= 0) & (generated_ids < vocab_size)
        if not torch.any(valid):
            return scores

        # Invalid IDs use token 0 as a temporary gather/scatter target. Restore
        # token 0 explicitly afterward so those placeholders cannot affect it.
        safe_ids = generated_ids.masked_fill(~valid, 0)
        selected_scores = torch.gather(scores, 1, safe_ids)
        penalized_scores = torch.where(
            selected_scores < 0,
            selected_scores * self.penalty,
            selected_scores / self.penalty,
        )

        processed = scores.clone()
        processed.scatter_(1, safe_ids, penalized_scores)

        original_zero = scores[:, 0]
        penalized_zero = torch.where(
            original_zero < 0,
            original_zero * self.penalty,
            original_zero / self.penalty,
        )
        generated_zero = (valid & (generated_ids == 0)).any(dim=1)
        processed[:, 0] = torch.where(generated_zero, penalized_zero, original_zero)
        return processed
