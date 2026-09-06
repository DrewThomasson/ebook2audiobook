"""Static-shape CUDA Graph buckets for batch-1 backbone prefill."""

from __future__ import annotations

import threading
from dataclasses import dataclass

import torch


@dataclass
class BackbonePrefillOutput:
    hidden_states: torch.Tensor
    logits: torch.Tensor
    attention_mask: torch.Tensor
    prefill_len: int


@dataclass
class _PrefillRecord:
    graph: torch.cuda.CUDAGraph
    stream: torch.cuda.Stream
    inputs_embeds: torch.Tensor
    attention_mask: torch.Tensor
    position_ids: torch.Tensor
    causal_mask: torch.Tensor
    cache_position: torch.Tensor
    hidden_states: torch.Tensor
    logits: torch.Tensor


class BackbonePrefillGraphCache:
    """Capture backbone prefill + lm_head while writing the decode StaticCache."""

    def __init__(self, backbone_graph, *, token_granularity: int = 32) -> None:
        if token_granularity <= 0:
            raise ValueError("token_granularity must be > 0")
        self.backbone_graph = backbone_graph
        self.model = backbone_graph.model
        self.lm_head = backbone_graph.lm_head
        self.device = torch.device(backbone_graph.device)
        self.dtype = backbone_graph.dtype
        self.token_granularity = int(token_granularity)
        self._records: dict[tuple[int, int], _PrefillRecord] = {}
        self._graph_pool = torch.cuda.graph_pool_handle()
        self._lock = threading.RLock()
        self.captures = 0
        self.replays = 0
        self._frozen = False

    def _bucket(self, length: int) -> int:
        return (
            (int(length) + self.token_granularity - 1) // self.token_granularity
        ) * self.token_granularity

    @staticmethod
    def _copy_inputs(
        inputs_embeds: torch.Tensor,
        attention_mask: torch.Tensor,
        static_embeds: torch.Tensor,
        static_mask: torch.Tensor,
        static_positions: torch.Tensor,
    ) -> None:
        seq_len = int(inputs_embeds.shape[1])
        pad_len = int(static_embeds.shape[1]) - seq_len
        static_embeds.zero_()
        static_mask.zero_()
        static_positions.fill_(1)
        static_embeds[:, pad_len:].copy_(inputs_embeds)
        static_mask[:, pad_len:].copy_(attention_mask)
        positions = static_mask.long().cumsum(-1) - 1
        positions.masked_fill_(static_mask == 0, 1)
        static_positions.copy_(positions)

    @staticmethod
    def _update_causal_mask(
        attention_mask: torch.Tensor, causal_mask: torch.Tensor
    ) -> None:
        batch_size, query_len = attention_mask.shape
        key_len = causal_mask.shape[-1]
        query_idx = torch.arange(query_len, device=attention_mask.device).view(
            1, query_len, 1
        )
        key_idx = torch.arange(key_len, device=attention_mask.device).view(
            1, 1, key_len
        )
        valid_keys = torch.zeros(
            (batch_size, key_len), dtype=torch.bool, device=attention_mask.device
        )
        valid_keys[:, :query_len].copy_(attention_mask.to(torch.bool))
        allowed = (key_idx <= query_idx) & valid_keys[:, None, :]
        causal_mask.fill_(torch.finfo(causal_mask.dtype).min)
        causal_mask[:, 0].masked_fill_(allowed, 0.0)

    def _forward(
        self,
        inputs_embeds: torch.Tensor,
        attention_mask: torch.Tensor,
        position_ids: torch.Tensor,
        cache_position: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        output = self.model(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=self.backbone_graph.static_cache,
            cache_position=cache_position,
            use_cache=True,
        )
        hidden_states = output.last_hidden_state
        logits = self.lm_head(hidden_states[:, -1, :].float()).float()
        return hidden_states, logits

    @torch.inference_mode()
    def __call__(
        self,
        inputs_embeds: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> BackbonePrefillOutput:
        batch_size, seq_len, hidden_size = inputs_embeds.shape
        if batch_size != self.backbone_graph.batch_size:
            raise ValueError(
                f"prefill batch={batch_size} does not match decode graph "
                f"batch={self.backbone_graph.batch_size}"
            )
        bucket_len = self._bucket(int(seq_len))
        if bucket_len > self.backbone_graph.max_seq_len:
            raise RuntimeError(
                f"prefill bucket {bucket_len} exceeds max_seq_len "
                f"{self.backbone_graph.max_seq_len}"
            )
        key = (int(batch_size), bucket_len)

        with self._lock:
            record = self._records.get(key)
            if record is None:
                if self._frozen:
                    raise RuntimeError(
                        f"backbone prefill CUDA graph {key} was not declared in the warmup profile"
                    )
                static_embeds = torch.zeros(
                    (batch_size, bucket_len, hidden_size),
                    dtype=inputs_embeds.dtype,
                    device=inputs_embeds.device,
                )
                static_mask = torch.zeros(
                    (batch_size, bucket_len),
                    dtype=attention_mask.dtype,
                    device=attention_mask.device,
                )
                static_positions = torch.ones_like(static_mask, dtype=torch.long)
                static_causal_mask = torch.empty(
                    (batch_size, 1, bucket_len, self.backbone_graph.max_seq_len),
                    dtype=inputs_embeds.dtype,
                    device=inputs_embeds.device,
                )
                cache_position = torch.arange(
                    bucket_len, device=inputs_embeds.device, dtype=torch.long
                )
                self._copy_inputs(
                    inputs_embeds,
                    attention_mask,
                    static_embeds,
                    static_mask,
                    static_positions,
                )
                self._update_causal_mask(static_mask, static_causal_mask)

                capture_stream = torch.cuda.Stream(device=inputs_embeds.device)
                capture_stream.wait_stream(
                    torch.cuda.current_stream(inputs_embeds.device)
                )
                with torch.cuda.stream(capture_stream):
                    for _ in range(3):
                        hidden_states, logits = self._forward(
                            static_embeds,
                            static_causal_mask,
                            static_positions,
                            cache_position,
                        )
                capture_stream.synchronize()

                graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(
                    graph,
                    stream=capture_stream,
                    pool=self._graph_pool,
                    capture_error_mode="thread_local",
                ):
                    hidden_states, logits = self._forward(
                        static_embeds,
                        static_causal_mask,
                        static_positions,
                        cache_position,
                    )
                record = _PrefillRecord(
                    graph=graph,
                    stream=capture_stream,
                    inputs_embeds=static_embeds,
                    attention_mask=static_mask,
                    position_ids=static_positions,
                    causal_mask=static_causal_mask,
                    cache_position=cache_position,
                    hidden_states=hidden_states,
                    logits=logits,
                )
                self._records[key] = record
                self.captures += 1

            self._copy_inputs(
                inputs_embeds,
                attention_mask,
                record.inputs_embeds,
                record.attention_mask,
                record.position_ids,
            )
            self._update_causal_mask(record.attention_mask, record.causal_mask)
            current_stream = torch.cuda.current_stream(inputs_embeds.device)
            record.stream.wait_stream(current_stream)
            record.graph.replay()
            current_stream.wait_stream(record.stream)
            self.backbone_graph.finish_direct_prefill(bucket_len)
            self.replays += 1
            return BackbonePrefillOutput(
                hidden_states=record.hidden_states,
                logits=record.logits,
                attention_mask=record.attention_mask,
                prefill_len=bucket_len,
            )

    @property
    def graph_keys(self) -> tuple[tuple[int, int], ...]:
        return tuple(sorted(self._records))

    @torch.inference_mode()
    def warmup_graph(self, *, branch_batch_size: int, sequence_length: int) -> None:
        if self._frozen:
            raise RuntimeError("backbone prefill CUDA graph cache is already frozen")
        inputs_embeds = torch.zeros(
            branch_batch_size,
            sequence_length,
            int(self.backbone_graph.hidden_size),
            dtype=self.dtype,
            device=self.device,
        )
        attention_mask = torch.ones(
            branch_batch_size,
            sequence_length,
            dtype=torch.long,
            device=self.device,
        )
        self(inputs_embeds, attention_mask)

    def freeze(self) -> None:
        self._frozen = True
