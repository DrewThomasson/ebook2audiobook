"""Batch-1 static CUDA Graph cache for the HF text encoder."""

from __future__ import annotations

import threading
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import torch


@dataclass
class _GraphRecord:
    graph: torch.cuda.CUDAGraph
    stream: torch.cuda.Stream
    input_ids: torch.Tensor
    attention_mask: torch.Tensor
    position_ids: torch.Tensor
    output: torch.Tensor


class TextEncoderGraphCache:
    """Capture fixed padded text-encoder buckets and replay them without CPU dispatch."""

    def __init__(
        self, text_encoder: torch.nn.Module, *, token_granularity: int = 32
    ) -> None:
        if token_granularity <= 0:
            raise ValueError("token_granularity must be > 0")
        self.text_encoder = text_encoder
        self.text_encoder._force_static_attention_mask = True
        self.text_encoder.config._attn_implementation = "sdpa"
        self.token_granularity = int(token_granularity)
        self._records: dict[tuple[int, int], _GraphRecord] = {}
        self._lock = threading.RLock()
        self._graph_pool = torch.cuda.graph_pool_handle()
        self.captures = 0
        self.replays = 0
        self._frozen = False

    def _bucket(self, length: int) -> int:
        return (
            (int(length) + self.token_granularity - 1) // self.token_granularity
        ) * self.token_granularity

    @staticmethod
    def _smallest_fitting_key(
        keys: Sequence[tuple[int, int]],
        *,
        batch_size: int,
        token_length: int,
    ) -> tuple[int, int] | None:
        candidates = [
            key
            for key in keys
            if key[0] == batch_size and key[1] >= token_length
        ]
        return min(candidates, key=lambda key: key[1], default=None)

    @staticmethod
    def _copy_inputs(
        segments: Sequence[torch.Tensor],
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        position_ids: torch.Tensor,
    ) -> None:
        input_ids.zero_()
        attention_mask.zero_()
        position_ids.zero_()
        for row, segment in enumerate(segments):
            length = int(segment.shape[0])
            input_ids[row, :length].copy_(segment)
            attention_mask[row, :length].fill_(1)
            position_ids[row, :length].copy_(
                torch.arange(length, device=segment.device, dtype=torch.long)
            )

    @torch.inference_mode()
    def __call__(
        self, segments: Sequence[torch.Tensor]
    ) -> tuple[list[torch.Tensor], list[Any]]:
        if not segments:
            return [], []
        lengths = [int(segment.shape[0]) for segment in segments]
        if any(length <= 0 for length in lengths):
            raise ValueError("text encoder graph does not support empty segments")
        batch_size = len(segments)
        max_length = self._bucket(max(lengths))
        requested_key = (batch_size, max_length)

        with self._lock:
            key = self._smallest_fitting_key(
                self._records,
                batch_size=batch_size,
                token_length=max_length,
            )
            record = self._records.get(key) if key is not None else None
            if record is None:
                if self._frozen:
                    raise RuntimeError(
                        f"text encoder CUDA graph {requested_key} has no fitting bucket "
                        "in the warmup profile"
                    )
                key = requested_key
                device = segments[0].device
                static_ids = torch.zeros(
                    (batch_size, max_length), dtype=segments[0].dtype, device=device
                )
                static_mask = torch.zeros(
                    (batch_size, max_length), dtype=torch.long, device=device
                )
                static_positions = torch.zeros_like(static_mask)
                self._copy_inputs(segments, static_ids, static_mask, static_positions)

                capture_stream = torch.cuda.Stream(device=device)
                capture_stream.wait_stream(torch.cuda.current_stream(device))
                with torch.cuda.stream(capture_stream):
                    for _ in range(3):
                        static_output = self.text_encoder(
                            input_ids=static_ids,
                            attention_mask=static_mask,
                            position_ids=static_positions,
                            output_hidden_states=False,
                        ).last_hidden_state
                capture_stream.synchronize()

                graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(
                    graph,
                    stream=capture_stream,
                    pool=self._graph_pool,
                    capture_error_mode="thread_local",
                ):
                    static_output = self.text_encoder(
                        input_ids=static_ids,
                        attention_mask=static_mask,
                        position_ids=static_positions,
                        output_hidden_states=False,
                    ).last_hidden_state
                record = _GraphRecord(
                    graph=graph,
                    stream=capture_stream,
                    input_ids=static_ids,
                    attention_mask=static_mask,
                    position_ids=static_positions,
                    output=static_output,
                )
                self._records[key] = record
                self.captures += 1

            self._copy_inputs(
                segments,
                record.input_ids,
                record.attention_mask,
                record.position_ids,
            )
            current_stream = torch.cuda.current_stream(segments[0].device)
            record.stream.wait_stream(current_stream)
            record.graph.replay()
            current_stream.wait_stream(record.stream)
            self.replays += 1
            hidden_states = [
                record.output[row, :length] for row, length in enumerate(lengths)
            ]
            return hidden_states, []

    @property
    def graph_keys(self) -> tuple[tuple[int, int], ...]:
        return tuple(sorted(self._records))

    @torch.inference_mode()
    def warmup_graph(
        self, *, batch_size: int, token_length: int, device: torch.device
    ) -> None:
        if self._frozen:
            raise RuntimeError("text encoder CUDA graph cache is already frozen")
        segments = [
            torch.zeros(token_length, dtype=torch.long, device=device)
            for _ in range(batch_size)
        ]
        self(segments)

    def freeze(self) -> None:
        self._frozen = True
