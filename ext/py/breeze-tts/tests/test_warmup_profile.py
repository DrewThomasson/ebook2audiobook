from __future__ import annotations

import json
from pathlib import Path

import pytest

from models.warmup_profile import load_warmup_profile, parse_warmup_profile

REPO_ROOT = Path(__file__).resolve().parents[1]


def _payload() -> dict:
    return json.loads((REPO_ROOT / "configs" / "fast.json").read_text())


def test_bundled_config_covers_cfg1_cfg4_and_voice_direction() -> None:
    profile = load_warmup_profile(REPO_ROOT / "configs" / "fast.json")

    assert profile.cfg_scales == (1.0, 4.0)
    assert profile.cfg_modes == ("no_cfg", "single_cfg")
    assert profile.backbone_decode_branch_batch_sizes == (1, 2)
    assert profile.depth_decoder_batch_sizes == (1, 2)
    assert profile.codec_num_lanes == 1
    assert profile.codec_chunk_frames == 1
    assert profile.freeze_after_warmup is True
    assert {graph.branch_batch_size for graph in profile.backbone_prefill_graphs} == {
        1,
        2,
    }
    assert {graph.batch_size for graph in profile.text_encoder_graphs} == {1, 2, 4}
    cfg1_text_lengths = [
        graph.token_length
        for graph in profile.text_encoder_graphs
        if graph.batch_size == 1
    ]
    cfg_guided_text_lengths = [
        graph.token_length
        for graph in profile.text_encoder_graphs
        if graph.batch_size == 2
    ]
    voice_direction_text_lengths = [
        graph.token_length
        for graph in profile.text_encoder_graphs
        if graph.batch_size == 4
    ]
    assert cfg1_text_lengths == list(range(32, 257, 32))
    assert cfg_guided_text_lengths == list(range(32, 513, 32))
    # ref_edit_tata merges the positive and negative branches' two text
    # segments each, so fast CFG-4 voice direction reaches batch size 4.
    assert voice_direction_text_lengths == [32, 64, 96, 128, 160, 256]


def test_config_requires_decode_graph_for_each_cfg_shape() -> None:
    payload = _payload()
    payload["stages"]["backbone_decode"]["graphs"] = [{"branch_batch_size": 2}]

    with pytest.raises(ValueError, match="must match cfg_scales"):
        parse_warmup_profile(payload)


def test_config_requires_prefill_graphs_for_each_cfg_shape() -> None:
    payload = _payload()
    payload["stages"]["backbone_prefill"]["graphs"] = [
        graph
        for graph in payload["stages"]["backbone_prefill"]["graphs"]
        if graph["branch_batch_size"] == 2
    ]

    with pytest.raises(ValueError, match="every backbone_decode"):
        parse_warmup_profile(payload)


def test_config_rejects_unaligned_bucket() -> None:
    payload = _payload()
    payload["stages"]["text_encoder"]["graphs"][0]["token_length"] = 33

    with pytest.raises(ValueError, match="multiples of 32"):
        parse_warmup_profile(payload)


def test_config_requires_synthetic_request() -> None:
    payload = _payload()
    del payload["warmup_request"]

    with pytest.raises(ValueError, match="warmup_request"):
        parse_warmup_profile(payload)
