from __future__ import annotations

import torch

from models.cudagraph.sampling import sample_logits
from models.logits_process import (
    GeneratedTokenRepetitionPenaltyLogitsProcessor,
    mask_invalid_codec_token_logits,
)


def test_repetition_penalty_ignores_text_prompt() -> None:
    processor = GeneratedTokenRepetitionPenaltyLogitsProcessor(penalty=2.0)
    input_ids = torch.tensor([[99, 88, 1, 4, -1, 6]])
    scores = torch.tensor([[2.0, -2.0, 3.0, -4.0, 5.0]])

    processed = processor(input_ids, scores)

    torch.testing.assert_close(processed, scores)


def test_repetition_penalty_uses_generated_backbone_tokens_only() -> None:
    processor = GeneratedTokenRepetitionPenaltyLogitsProcessor(penalty=2.0)
    input_ids = torch.tensor(
        [
            [
                [1, 4, 4],
                [0, 2, 2],
                [6, 3, 3],
            ]
        ]
    )
    scores = torch.tensor([[2.0, -2.0, 3.0]])

    processed = processor(input_ids, scores)

    torch.testing.assert_close(processed, torch.tensor([[1.0, -4.0, 3.0]]))


def test_repetition_penalty_rejects_unexpected_input_rank() -> None:
    processor = GeneratedTokenRepetitionPenaltyLogitsProcessor(penalty=2.0)

    try:
        processor(torch.tensor([1, 2]), torch.tensor([[1.0, 2.0]]))
    except ValueError as error:
        assert "1D" in str(error)
    else:
        raise AssertionError("Expected a ValueError for 1D input IDs")


def test_fast_sampling_penalizes_generated_token_history() -> None:
    logits = torch.tensor([[1.0, 0.9, 0.1]])

    token = sample_logits(
        logits,
        temperature=1.0,
        top_k=0,
        top_p=1.0,
        do_sample=False,
        token_history=torch.tensor([0]),
        repetition_penalty=2.0,
    )

    torch.testing.assert_close(token, torch.tensor([1]))


def test_codec_token_mask_preserves_backbone_eos() -> None:
    scores = torch.zeros(1, 2052)

    mask_invalid_codec_token_logits(
        scores,
        codebook_size=2048,
        token_vocab_size=2051,
    )

    assert torch.isfinite(scores[0, 2047])
    assert torch.isneginf(scores[0, 2048:2051]).all()
    assert torch.isfinite(scores[0, 2051])


def test_codec_token_mask_covers_depth_decoder_reserved_tokens() -> None:
    scores = torch.zeros(1, 2051)

    mask_invalid_codec_token_logits(
        scores,
        codebook_size=2048,
        token_vocab_size=2051,
    )

    assert torch.isfinite(scores[0, 2047])
    assert torch.isneginf(scores[0, 2048:]).all()
