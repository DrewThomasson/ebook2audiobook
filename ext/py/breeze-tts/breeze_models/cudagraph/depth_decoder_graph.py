"""
CUDA graph capture for the Breeze depth decoder's decode loop,
using transformers StaticCache.

The depth decoder generates num_codebooks-1 codebook tokens autoregressively
(typically 15 for production models with 16 RVQ codebooks):
- Step 0: prefill with 2 tokens (backbone_hidden placeholder + first_cb_token),
  get logits for codebook[1]
- Steps 1..num_codebooks-2: decode 1 token at a time using previous codebook token's embedding

Strategy:
- Use transformers StaticCache for KV cache management
- Use the depth decoder's inner model forward
- Unroll the full loop for deterministic shapes
- Capture the entire loop as a single CUDA graph
- CFG is baked in: batch=2 (cond + uncond), guidance applied per step
- All tensors pre-allocated — no torch.tensor() calls inside the graph
- Sampling params (temperature, top_k, top_p, do_sample, guidance_scale) are
  per-sample tensor buffers [half, 1] or [half]: update via set_*() methods
  at runtime without recapture. Accepts both scalar (broadcast) and tensor
  (per-sample) values.
- top_k uses a fixed MAX_K workspace; top_k_buf can be set to any value <= _max_k.
- Multi-batch bucket support: pre-capture graphs for multiple batch sizes
  (powers of 2), select the smallest fitting bucket at runtime. No recapture
  needed when batch size changes within the pre-captured range.
"""

import logging
from dataclasses import dataclass

import torch
import torch._dynamo
import torch.nn.functional as F
from transformers import StaticCache
from transformers.masking_utils import create_causal_mask

from ..logits_process import mask_invalid_codec_token_logits

_log = logging.getLogger(__name__)


@dataclass
class _BucketState:
    """Stores all per-bucket-size state needed for CUDA graph replay."""

    batch_size: int
    half: int
    graph: torch.cuda.CUDAGraph
    static_cache: StaticCache
    # I/O buffers
    backbone_hidden_buf: torch.Tensor
    first_cb_token_buf: torch.Tensor
    output_tokens: torch.Tensor
    _tok_buf: torch.Tensor
    prefill_input_ids: torch.Tensor
    # Attention masks
    prefill_attn: torch.Tensor
    decode_attn: list
    # Sampling param buffers
    temperature_buf: torch.Tensor
    top_k_buf: torch.Tensor
    top_p_buf: torch.Tensor
    do_sample_buf: torch.Tensor
    guidance_scale: torch.Tensor
    # Debug buffers (optional)
    debug_logits: torch.Tensor | None = None
    _debug_head_input: torch.Tensor | None = None
    _debug_probs: torch.Tensor | None = None
    _debug_probs_slot: torch.Tensor | None = None


class DepthDecoderGraph:
    """
    Captures the full depth decoder loop as a CUDA graph,
    using the model's forward with transformers StaticCache.

    For CFG: batch=2 (cond=batch[0], uncond=batch[1]).

    Sampling params are per-sample tensor buffers — no recapture needed:
        # Scalar (broadcast to all samples):
        graph.set_temperature(0.5)
        graph.set_guidance_scale(3.0)

        # Per-sample (tensor):
        graph.set_temperature(torch.tensor([0.5, 1.2]))
        graph.set_guidance_scale(torch.tensor([3.0, 1.0]))

        # Or pass directly in run():
        graph.run(backbone_h, first_cb, temperature=torch.tensor([0.5, 1.2]))

    Batch size changes trigger automatic recapture:
        graph.ensure_batch_size(4)
    """

    def __init__(
        self,
        depth_decoder,
        config,
        device="cuda:0",
        dtype=torch.bfloat16,
        do_sample=True,
        top_k=50,
        top_p=1.0,
        temperature=0.9,
        guidance_scale=3.0,
        num_codebooks=None,
        codec_codebook_size=None,
        fast: bool = False,
        debug: bool = False,
        batch_size=2,
        bucket_sizes: list[int] | None = None,
    ):
        self.device = device
        self.dtype = dtype
        self.config = config
        self.debug = debug
        self.no_graph = (
            False  # runtime flag: True = skip graph replay (for layer-diff hooks)
        )
        self.num_layers = config.num_hidden_layers
        self.hidden_size = config.hidden_size
        self.backbone_hidden_size = config.backbone_hidden_size
        self.vocab_size = config.vocab_size
        self.codec_codebook_size = (
            int(codec_codebook_size)
            if codec_codebook_size is not None
            else self.vocab_size
        )
        if not 0 < self.codec_codebook_size <= self.vocab_size:
            raise ValueError(
                f"codec_codebook_size must be in [1, {self.vocab_size}], "
                f"got {self.codec_codebook_size}"
            )
        self.num_codebooks = (
            num_codebooks if num_codebooks is not None else config.num_codebooks
        )
        self.num_decode_codebooks = self.num_codebooks - 1
        self.max_seq = 2 + self.num_decode_codebooks
        self.batch_size = batch_size
        self.half = self._real_batch_size(self.batch_size)

        # Multi-batch bucket support
        self.bucket_sizes = sorted(bucket_sizes) if bucket_sizes else [batch_size]
        self._bucket_graphs: dict[int, _BucketState] = {}

        # Extract model components (references, not copies)
        self.depth_model = depth_decoder.model  # BreezeDepthDecoderModel
        self.codebooks_head = depth_decoder.codebooks_head  # BreezeCodebooksHead
        self._orig_codebooks_head = (
            depth_decoder.codebooks_head
        )  # unwrapped ref for fake forward hooks
        self.embed_tokens = self.depth_model.embed_tokens
        self.inputs_embeds_projector = self.depth_model.inputs_embeds_projector
        self.backbone_hidden_state_projector = getattr(
            self.depth_model, "backbone_hidden_state_projector", None
        )
        self.audio_embed_size = self.depth_model.audio_embed_size

        # Cast codebooks_head weight to fp32 for numerical stability
        # (module forward still fires hooks, and F.linear works with fp32 input)
        self.codebooks_head.weight.data = self.codebooks_head.weight.data.float()
        self.fast = bool(fast)

        # The fast path uses one maintained compile configuration before
        # manual CUDA Graph capture. Compile modes are intentionally not public.
        if self.fast:
            compile_mode = "default"
            _limit = self.num_layers * 4 + 16
            torch._dynamo.config.cache_size_limit = max(
                torch._dynamo.config.cache_size_limit, _limit
            )
            torch._dynamo.config.recompile_limit = max(
                torch._dynamo.config.recompile_limit, _limit
            )
            already_compiled = hasattr(self.depth_model.layers[0], "_orig_mod")
            if already_compiled:
                _log.info("Depth decoder layers already compiled, skipping.")
            else:
                _log.info("Compiling depth decoder with the fast configuration.")
                for index, layer in enumerate(self.depth_model.layers):
                    self.depth_model.layers[index] = torch.compile(
                        layer, mode=compile_mode, fullgraph=True
                    )
                self.depth_model.norm = torch.compile(
                    self.depth_model.norm, mode=compile_mode, fullgraph=True
                )
            if not hasattr(self.codebooks_head, "_orig_mod"):
                self.codebooks_head = torch.compile(
                    self.codebooks_head, mode=compile_mode, fullgraph=True
                )

        # Sampling param defaults — saved for _alloc_buffers / _rebuild_for_batch
        self._default_temperature = temperature
        self._default_top_k = top_k
        self._default_top_p = top_p
        self._default_do_sample = do_sample
        self._default_guidance_scale = guidance_scale

        # Fixed MAX_K workspace for graph-safe top_k.
        # top_k_buf can be set to any value in [1, _max_k] at runtime without recapture.
        # Default 1024 so users can freely adjust top_k up to 1024.
        self._max_k = min(1024, self.vocab_size)
        self._topk_ranks = torch.arange(
            self._max_k, device=device
        )  # pre-alloc, never recreated
        # top_p: always keep the highest-prob token (graph-safe alternative to remove[0]=False)
        self._keep_first = torch.zeros(self.vocab_size, dtype=torch.bool, device=device)
        self._keep_first[0] = True

        # Pre-allocate ALL cache_position tensors (no torch.tensor() inside graph)
        self.prefill_cache_pos = torch.arange(2, device=device)
        self.decode_cache_positions = [
            torch.tensor([2 + i], device=device)
            for i in range(self.num_decode_codebooks - 1)
        ]
        self.head_prefill_pos = torch.tensor([1], device=device)
        self.codebook_offsets = [
            torch.tensor([i * self.vocab_size], dtype=torch.long, device=device)
            for i in range(self.num_decode_codebooks)
        ]

        # Transformers StaticCache
        self.static_cache = StaticCache(
            config=config, max_cache_len=self.max_seq, batch_size=self.batch_size
        )

        self._alloc_buffers()

        self.graph = None
        self.captured = False
        self.prefill_attn = None
        self.decode_attn = None

    @staticmethod
    def _real_batch_size(batch_size: int) -> int:
        if batch_size <= 1:
            return batch_size
        return batch_size // 2

    # ------------------------------------------------------------------
    # Runtime setters — no recapture needed
    # ------------------------------------------------------------------

    def set_temperature(self, v):
        """v: scalar float (broadcast) or [half] / [half,1] tensor (per-sample)."""
        if isinstance(v, (int, float)):
            self.temperature_buf.fill_(v)
        else:
            self.temperature_buf.copy_(v.view(self.half, 1))

    def set_top_k(self, v):
        """v: scalar int (broadcast) or [half] / [half,1] tensor (per-sample)."""
        if isinstance(v, (int, float)):
            assert v <= self._max_k, (
                f"top_k={v} exceeds _max_k={self._max_k}; rebuild graph to increase MAX_K"
            )
            self.top_k_buf.fill_(v)
        else:
            assert v.max().item() <= self._max_k, (
                f"top_k max={v.max().item()} exceeds _max_k={self._max_k}"
            )
            self.top_k_buf.copy_(v.view(self.half, 1))

    def set_top_p(self, v):
        """v: scalar float (broadcast) or [half] / [half,1] tensor (per-sample)."""
        if isinstance(v, (int, float)):
            self.top_p_buf.fill_(v)
        else:
            self.top_p_buf.copy_(v.view(self.half, 1))

    def set_do_sample(self, v):
        """v: scalar bool (broadcast) or [half] long tensor (per-sample, 0/1)."""
        if isinstance(v, (bool, int, float)):
            self.do_sample_buf.fill_(1 if v else 0)
        else:
            self.do_sample_buf.copy_(v.view(self.half))

    def set_guidance_scale(self, v):
        """v: scalar float (broadcast) or [half] / [half,1] tensor (per-sample)."""
        if isinstance(v, (int, float)):
            self.guidance_scale.fill_(v)
        else:
            self.guidance_scale.copy_(v.view(self.half, 1))

    # ------------------------------------------------------------------
    # Buffer allocation (called from __init__ and _rebuild_for_batch)
    # ------------------------------------------------------------------

    def _alloc_buffers(self):
        """Allocate / re-allocate I/O buffers for current batch_size.

        Also (re-)creates per-sample sampling param buffers whose first
        dimension is ``self.half``.  On first call the ``_default_*``
        values are used; on subsequent calls (batch-size change) the
        current first-sample value is preserved as the uniform default.
        """
        self.backbone_hidden_buf = torch.zeros(
            self.batch_size,
            self.backbone_hidden_size,
            dtype=self.dtype,
            device=self.device,
        )
        self.first_cb_token_buf = torch.zeros(
            self.batch_size, dtype=torch.long, device=self.device
        )
        self.output_tokens = torch.zeros(
            self.batch_size,
            self.num_decode_codebooks,
            dtype=torch.long,
            device=self.device,
        )
        self._tok_buf = torch.zeros(
            self.batch_size, dtype=torch.long, device=self.device
        )
        self.prefill_input_ids = torch.zeros(
            self.batch_size, 2, dtype=torch.long, device=self.device
        )

        # --- Per-sample sampling param buffers [half, 1] or [half] ---
        # Preserve current value when resizing, fall back to defaults on first init.
        _temp = (
            float(self.temperature_buf[0, 0])
            if hasattr(self, "temperature_buf") and self.temperature_buf.numel()
            else self._default_temperature
        )
        _top_k = (
            int(self.top_k_buf[0, 0])
            if hasattr(self, "top_k_buf") and self.top_k_buf.numel()
            else self._default_top_k
        )
        _top_p = (
            float(self.top_p_buf[0, 0])
            if hasattr(self, "top_p_buf") and self.top_p_buf.numel()
            else self._default_top_p
        )
        _do_sample = (
            int(self.do_sample_buf[0])
            if hasattr(self, "do_sample_buf") and self.do_sample_buf.numel()
            else (1 if self._default_do_sample else 0)
        )
        _gs = (
            float(self.guidance_scale[0, 0])
            if hasattr(self, "guidance_scale") and self.guidance_scale.numel()
            else self._default_guidance_scale
        )

        self.temperature_buf = torch.full(
            (self.half, 1), _temp, dtype=torch.float32, device=self.device
        )
        self.top_k_buf = torch.full(
            (self.half, 1), _top_k, dtype=torch.long, device=self.device
        )
        self.top_p_buf = torch.full(
            (self.half, 1), _top_p, dtype=torch.float32, device=self.device
        )
        self.do_sample_buf = torch.full(
            (self.half,), _do_sample, dtype=torch.long, device=self.device
        )
        self.guidance_scale = torch.full(
            (self.half, 1), _gs, dtype=torch.float32, device=self.device
        )

        # Debug: per-codebook raw logits [num_decode_codebooks, batch_size, vocab_size]
        if self.debug:
            self.debug_logits = torch.zeros(
                self.num_decode_codebooks,
                self.batch_size,
                self.vocab_size,
                dtype=torch.float32,
                device=self.device,
            )
            # Debug: hidden states before each codebooks_head call (for fake forward hooks)
            self._debug_head_input = torch.zeros(
                self.num_decode_codebooks,
                self.batch_size,
                1,
                self.hidden_size,
                dtype=torch.float32,
                device=self.device,
            )
            # Debug: probs before torch.multinomial (for fake multinomial hooks)
            self._debug_probs = torch.zeros(
                self.num_decode_codebooks,
                self.half,
                self.vocab_size,
                dtype=torch.float32,
                device=self.device,
            )
            # Single-slot buffer written by _cfg_sample, copied per-cb in _full_loop
            self._debug_probs_slot = torch.zeros(
                self.half,
                self.vocab_size,
                dtype=torch.float32,
                device=self.device,
            )
        else:
            self.debug_logits = None
            self._debug_head_input = None
            self._debug_probs = None
            self._debug_probs_slot = None

    # ------------------------------------------------------------------
    # Batch size management — auto-recapture on change
    # ------------------------------------------------------------------

    @torch.inference_mode()
    def ensure_batch_size(self, batch_size: int):
        """No-op if batch_size matches current captured graph; else rebuild and recapture."""
        if batch_size == self.batch_size:
            return
        self._rebuild_for_batch(batch_size)

    @torch.inference_mode()
    def _rebuild_for_batch(self, batch_size: int):
        self.batch_size = batch_size
        self.half = self._real_batch_size(self.batch_size)
        self.static_cache = StaticCache(
            config=self.config, max_cache_len=self.max_seq, batch_size=batch_size
        )
        self._alloc_buffers()
        self.captured = False
        self.graph = None
        self.prefill_attn = None
        self.decode_attn = None
        if self.no_graph:
            self.prepare_eager()
        else:
            self.capture()

    @torch.inference_mode()
    def prepare_eager(self):
        """Initialize the depth loop for native eager execution only."""
        self.no_graph = True
        self._init_cache_layers()
        self._build_attention_masks()
        self.captured = False
        return self

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_cache_layers(self):
        """Force lazy initialization of StaticCache layers before graph capture."""
        config = self.depth_model.config
        num_kv_heads = getattr(
            config, "num_key_value_heads", config.num_attention_heads
        )
        head_dim = getattr(
            config, "head_dim", config.hidden_size // config.num_attention_heads
        )
        dummy_k = torch.zeros(
            self.batch_size,
            num_kv_heads,
            1,
            head_dim,
            dtype=self.dtype,
            device=self.device,
        )
        for layer in self.static_cache.layers:
            if not layer.is_initialized:
                layer.lazy_initialization(dummy_k)

    def _make_attn_mask(self, input_embeds, cache_position):
        return create_causal_mask(
            config=self.depth_model.config,
            input_embeds=input_embeds,
            attention_mask=None,
            cache_position=cache_position,
            past_key_values=self.static_cache,
        )

    def _build_attention_masks(self):
        dummy_prefill = torch.zeros(
            self.batch_size, 2, self.hidden_size, dtype=self.dtype, device=self.device
        )
        dummy_decode = torch.zeros(
            self.batch_size, 1, self.hidden_size, dtype=self.dtype, device=self.device
        )
        self.prefill_attn = self._make_attn_mask(dummy_prefill, self.prefill_cache_pos)
        self.decode_attn = []
        for pos in self.decode_cache_positions:
            self.decode_attn.append(self._make_attn_mask(dummy_decode, pos))

    def _cfg_sample(self, logits):
        """Graph-safe CFG + sampling matching HF transformers order.

        HF order: temperature -> top_k -> top_p -> softmax -> multinomial.
        All filtering on raw logits (not log-space) for parity with
        TemperatureLogitsWarper / TopKLogitsWarper / TopPLogitsWarper.

        Writes sampled tokens into self._tok_buf [batch_size].
        For batch_size=2*N: processes N samples, writes to both halves (cond+uncond).
        """
        # logits: [batch_size, 1, vocab]
        if self.batch_size >= 2:
            cond_logits = logits[: self.half, 0, :]
            uncond_logits = logits[self.half :, 0, :]
            cfg = uncond_logits + self.guidance_scale * (cond_logits - uncond_logits)
        else:
            cfg = logits[: self.half, 0, :]

        mask_invalid_codec_token_logits(
            cfg,
            codebook_size=self.codec_codebook_size,
            token_vocab_size=self.vocab_size,
        )

        # temperature scaling (on raw logits, same as TemperatureLogitsWarper)
        scaled = cfg / self.temperature_buf  # [half, vocab]

        # top_k on raw logits (graph-safe: fixed _max_k workspace)
        effective_k = torch.where(
            self.top_k_buf > 0,
            self.top_k_buf,
            torch.full_like(self.top_k_buf, self._max_k),
        )
        topk_vals, topk_idx = torch.topk(scaled, self._max_k)  # [half, _max_k]
        topk_mask = self._topk_ranks < effective_k  # [_max_k] broadcasts
        topk_vals = torch.where(
            topk_mask, topk_vals, torch.full_like(topk_vals, float("-inf"))
        )
        scaled = torch.full_like(scaled, float("-inf")).scatter_(1, topk_idx, topk_vals)

        # top_p on raw logits (HF-style: softmax -> cumsum -> mask -> apply to raw logits)
        sorted_logits, sorted_idx = torch.sort(scaled, descending=True)  # [half, vocab]
        cumprobs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
        remove = cumprobs > self.top_p_buf
        remove = F.pad(
            remove[..., :-1], (1, 0), value=False
        )  # shift right, first always kept
        sorted_logits = torch.where(
            remove, torch.full_like(sorted_logits, float("-inf")), sorted_logits
        )
        scaled = torch.full_like(scaled, float("-inf")).scatter_(
            1, sorted_idx, sorted_logits
        )

        # softmax -> multinomial (same as HF _sample)
        probs = F.softmax(scaled, dim=-1)

        # Debug: save probs before multinomial for fake forward hooks
        if self._debug_probs_slot is not None:
            self._debug_probs_slot.copy_(probs)

        # do_sample: compute both paths, select via torch.where (no Python branch in graph)
        greedy_toks = torch.argmax(cfg, dim=-1)  # [half]
        sampled_toks = torch.multinomial(probs, 1).squeeze(-1)  # [half]
        toks = torch.where(
            self.do_sample_buf.bool(), sampled_toks, greedy_toks
        )  # [half] per-sample

        # Write to the active slots; duplicate for paired cond/uncond mode.
        self._tok_buf[: self.half] = toks
        if self.batch_size >= 2:
            self._tok_buf[self.half :] = toks

    def _full_loop(self):
        """The full depth decoder loop on static buffers. Graph-safe."""
        # Build [B, 2] input_ids: pos0=0 (placeholder), pos1=first_cb_token
        self.prefill_input_ids[:, 0] = 0
        self.prefill_input_ids[:, 1] = self.first_cb_token_buf

        # Embed full 2-token sequence, then overwrite pos0 with backbone hidden
        # (matches parity baseline: embed placeholder, then replace with backbone_h)
        prefill_embeds = self.embed_tokens(
            self.prefill_input_ids
        )  # [B, 2, audio_embed_size]
        # Project backbone hidden to audio_embed_size if dimensions differ
        backbone_h = self.backbone_hidden_buf  # [B, backbone_hidden_size]
        if self.backbone_hidden_state_projector is not None:
            backbone_h = self.backbone_hidden_state_projector(
                backbone_h
            )  # [B, audio_embed_size]
        prefill_embeds[:, 0] = backbone_h  # overwrite pos0
        prefill_embeds = self.inputs_embeds_projector(prefill_embeds)  # [B, 2, hidden]

        hidden_states = prefill_embeds
        position_ids = self.prefill_cache_pos.unsqueeze(0)  # [1, 2]
        position_embeddings = self.depth_model.rotary_emb(hidden_states, position_ids)

        for decoder_layer in self.depth_model.layers:
            hidden_states = decoder_layer(
                hidden_states,
                attention_mask=self.prefill_attn,
                position_ids=position_ids,
                past_key_values=self.static_cache,
                use_cache=True,
                cache_position=self.prefill_cache_pos,
                position_embeddings=position_embeddings,
            )

        hidden_states = self.depth_model.norm(hidden_states)

        # First codebook logits from position 1 (fp32: weight already cast, input cast here)
        if self._debug_head_input is not None:
            self._debug_head_input[0].copy_(hidden_states[:, 1:, :].float())
        first_logits = self.codebooks_head(
            hidden_states[:, 1:, :].float(),
            cache_position=self.head_prefill_pos,
        )  # [B, 1, vocab] fp32

        if self.debug_logits is not None:
            self.debug_logits[0].copy_(first_logits[:, 0, :])

        self._cfg_sample(first_logits)
        if self._debug_probs is not None:
            self._debug_probs[0].copy_(self._debug_probs_slot)
        self._tok_buf.clamp_(0, self.vocab_size - 1)
        self.output_tokens[:, 0] = self._tok_buf

        # Remaining codebooks: decode one at a time
        for cb_idx in range(1, self.num_decode_codebooks):
            offset_tok = self._tok_buf + self.codebook_offsets[cb_idx]
            emb = self.embed_tokens(
                offset_tok.unsqueeze(1).clamp_(
                    0, self.num_codebooks * self.vocab_size - 1
                )
            )  # [B, 1, backbone_H]
            emb = self.inputs_embeds_projector(emb)  # [B, 1, hidden]

            cache_pos = self.decode_cache_positions[cb_idx - 1]
            pos_ids = cache_pos.unsqueeze(0)
            pos_emb = self.depth_model.rotary_emb(emb, pos_ids)

            hidden_states = emb
            for decoder_layer in self.depth_model.layers:
                hidden_states = decoder_layer(
                    hidden_states,
                    attention_mask=self.decode_attn[cb_idx - 1],
                    position_ids=pos_ids,
                    past_key_values=self.static_cache,
                    use_cache=True,
                    cache_position=cache_pos,
                    position_embeddings=pos_emb,
                )

            hidden_states = self.depth_model.norm(hidden_states)

            if self._debug_head_input is not None:
                self._debug_head_input[cb_idx].copy_(hidden_states.float())
            logits = self.codebooks_head(
                hidden_states.float(),
                cache_position=cache_pos,
            )  # [B, 1, vocab] fp32

            if self.debug_logits is not None:
                self.debug_logits[cb_idx].copy_(logits[:, 0, :])

            self._cfg_sample(logits)
            if self._debug_probs is not None:
                self._debug_probs[cb_idx].copy_(self._debug_probs_slot)
            self._tok_buf.clamp_(0, self.vocab_size - 1)
            self.output_tokens[:, cb_idx] = self._tok_buf

    # ------------------------------------------------------------------
    # Snapshot / restore helpers for multi-bucket capture
    # ------------------------------------------------------------------

    def _snapshot_state(self) -> _BucketState:
        """Snapshot current self.* buffers into a _BucketState."""
        return _BucketState(
            batch_size=self.batch_size,
            half=self.half,
            graph=self.graph,
            static_cache=self.static_cache,
            backbone_hidden_buf=self.backbone_hidden_buf,
            first_cb_token_buf=self.first_cb_token_buf,
            output_tokens=self.output_tokens,
            _tok_buf=self._tok_buf,
            prefill_input_ids=self.prefill_input_ids,
            prefill_attn=self.prefill_attn,
            decode_attn=self.decode_attn,
            temperature_buf=self.temperature_buf,
            top_k_buf=self.top_k_buf,
            top_p_buf=self.top_p_buf,
            do_sample_buf=self.do_sample_buf,
            guidance_scale=self.guidance_scale,
            debug_logits=self.debug_logits,
            _debug_head_input=self._debug_head_input,
            _debug_probs=self._debug_probs,
            _debug_probs_slot=self._debug_probs_slot,
        )

    def _swap_to_bucket(self, state: _BucketState):
        """Point self.* at the given bucket's buffers (for graph replay)."""
        self.batch_size = state.batch_size
        self.half = state.half
        self.graph = state.graph
        self.static_cache = state.static_cache
        self.backbone_hidden_buf = state.backbone_hidden_buf
        self.first_cb_token_buf = state.first_cb_token_buf
        self.output_tokens = state.output_tokens
        self._tok_buf = state._tok_buf
        self.prefill_input_ids = state.prefill_input_ids
        self.prefill_attn = state.prefill_attn
        self.decode_attn = state.decode_attn
        self.temperature_buf = state.temperature_buf
        self.top_k_buf = state.top_k_buf
        self.top_p_buf = state.top_p_buf
        self.do_sample_buf = state.do_sample_buf
        self.guidance_scale = state.guidance_scale
        self.debug_logits = state.debug_logits
        self._debug_head_input = state._debug_head_input
        self._debug_probs = state._debug_probs
        self._debug_probs_slot = state._debug_probs_slot

    # ------------------------------------------------------------------
    # Bucket selection
    # ------------------------------------------------------------------

    def _select_bucket(self, actual_batch: int) -> int | None:
        """Return smallest bucket_size >= actual_batch, or None if none fits."""
        for bsz in self.bucket_sizes:
            if bsz >= actual_batch:
                return bsz
        return None

    @staticmethod
    def _copy_cfg_padded(dst, src, actual_batch: int, bucket_half: int):
        """Copy [cond..., uncond...] rows into a padded CFG bucket.

        ``_cfg_sample`` slices the static bucket as
        ``[:bucket_half]`` for conditional rows and ``[bucket_half:]`` for
        unconditional rows. When an actual batch is padded to a larger bucket,
        real uncond rows must start at ``bucket_half`` rather than immediately
        after the real cond rows.
        """
        actual_half = actual_batch // 2
        bucket_batch = bucket_half * 2

        dst[:actual_half].copy_(src[:actual_half])
        dst[bucket_half : bucket_half + actual_half].copy_(
            src[actual_half:actual_batch]
        )

        if actual_half < bucket_half:
            dst[actual_half:bucket_half].zero_()
            dst[bucket_half + actual_half : bucket_batch].zero_()

    # ------------------------------------------------------------------
    # Padded param setter (for bucket padding)
    # ------------------------------------------------------------------

    def _set_param_padded(self, buf, value, actual_n, bucket_n, is_1d=False):
        """Set a sampling param buffer with padding for bucket size mismatch.

        Args:
            buf: target buffer, shape [bucket_n, 1] or [bucket_n]
            value: scalar or tensor
            actual_n: number of actual samples
            bucket_n: bucket's half size
            is_1d: True if buf is 1D (e.g. do_sample_buf)
        """
        if isinstance(value, (int, float, bool)):
            buf.fill_(int(value) if is_1d else value)
        else:
            t = value.view(actual_n) if is_1d else value.view(actual_n, -1)
            if is_1d:
                buf[:actual_n].copy_(t)
                if actual_n < bucket_n:
                    buf[actual_n:].fill_(t[0].item())
            else:
                buf[:actual_n].copy_(t[:, : buf.shape[-1]])
                if actual_n < bucket_n:
                    buf[actual_n:].fill_(t[0, 0].item())

    # ------------------------------------------------------------------
    # Capture: single bucket + multi-bucket entry point
    # ------------------------------------------------------------------

    @torch.inference_mode()
    def _capture_single_bucket(self, bsz: int, num_warmup: int):
        """Capture a CUDA graph for a single batch size."""
        # Set up state for this bucket size
        self.batch_size = bsz
        self.half = self._real_batch_size(bsz)
        self.static_cache = StaticCache(
            config=self.config, max_cache_len=self.max_seq, batch_size=bsz
        )
        self._alloc_buffers()
        self._init_cache_layers()
        self._build_attention_masks()

        # Warmup
        for _ in range(num_warmup):
            self.static_cache.reset()
            self._full_loop()
        torch.cuda.synchronize(device=self.device)

        # Capture
        s = torch.cuda.Stream(device=self.device)
        s.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(s):
            self.graph = torch.cuda.CUDAGraph()
            self.static_cache.reset()
            self._full_loop()
            torch.cuda.synchronize(device=self.device)

            self.static_cache.reset()
            with torch.cuda.graph(self.graph):
                self._full_loop()

        torch.cuda.current_stream().wait_stream(s)
        torch.cuda.synchronize(device=self.device)

        # Save state for this bucket
        self._bucket_graphs[bsz] = self._snapshot_state()
        print(f"  Depth decoder CUDA graph captured for bucket_size={bsz}")

    @torch.inference_mode()
    def capture(self, num_warmup=3):
        """Warmup and capture CUDA graphs for all bucket sizes."""
        if self.fast:
            num_warmup = max(num_warmup, 8)
        print(
            f"Capturing depth decoder graphs for buckets={self.bucket_sizes} "
            f"({num_warmup} warmup runs, fast={self.fast})..."
        )

        for bsz in self.bucket_sizes:
            self._capture_single_bucket(bsz, num_warmup)

        # Leave self.* pointing at the smallest bucket (default)
        self._swap_to_bucket(self._bucket_graphs[self.bucket_sizes[0]])
        self.captured = True
        print(
            f"Depth decoder CUDA graphs captured for all {len(self.bucket_sizes)} buckets!"
        )
        return self

    # ------------------------------------------------------------------
    # Eager fallback (for batch sizes exceeding all buckets)
    # ------------------------------------------------------------------

    @torch.inference_mode()
    def _run_eager(
        self,
        backbone_hidden,
        first_cb_token,
        temperature=None,
        top_k=None,
        top_p=None,
        do_sample=None,
        guidance_scale=None,
    ):
        """Fallback: ensure_batch_size + _full_loop (no CUDA graph)."""
        actual_batch = backbone_hidden.shape[0]
        self.ensure_batch_size(actual_batch)

        self.backbone_hidden_buf.copy_(backbone_hidden)
        self.first_cb_token_buf.copy_(first_cb_token)

        if temperature is not None:
            self.set_temperature(temperature)
        if top_k is not None:
            self.set_top_k(top_k)
        if top_p is not None:
            self.set_top_p(top_p)
        if do_sample is not None:
            self.set_do_sample(do_sample)
        if guidance_scale is not None:
            self.set_guidance_scale(guidance_scale)

        self.static_cache.reset()
        self._full_loop()
        return self.output_tokens[: self.half].clone()

    # ------------------------------------------------------------------
    # Run: bucket selection + graph replay
    # ------------------------------------------------------------------

    @torch.inference_mode()
    def run(
        self,
        backbone_hidden,
        first_cb_token,
        temperature=None,
        top_k=None,
        top_p=None,
        do_sample=None,
        guidance_scale=None,
    ):
        """
        Run the captured graph with automatic bucket selection.

        backbone_hidden: [batch_size, backbone_hidden_size]
        first_cb_token: [batch_size] long tensor

        Optional per-sample sampling params (applied before graph replay):
          temperature:    float or [half] / [half,1] tensor
          top_k:          int   or [half] / [half,1] tensor
          top_p:          float or [half] / [half,1] tensor
          do_sample:      bool  or [half] long tensor (0/1)
          guidance_scale: float or [half] / [half,1] tensor

        Returns: [actual_half, num_decode_codebooks] long tensor of codebook tokens
        """
        actual_batch = backbone_hidden.shape[0]
        actual_half = self._real_batch_size(actual_batch)

        # Safety guard: single CFG expects paired cond+uncond rows. no-CFG uses
        # batch=1 and is valid.
        if actual_batch != 1 and actual_batch % 2 != 0:
            _log.warning(
                "DepthDecoderGraph.run: invalid CFG actual_batch=%d, "
                "returning zeros to avoid CUDA graph mismatch",
                actual_batch,
            )
            return torch.zeros(
                1,
                self.num_decode_codebooks,
                dtype=torch.long,
                device=self.device,
            )

        # Eager fallback: no_graph flag or no fitting bucket
        bucket_bsz = self._select_bucket(actual_batch)
        if self.no_graph or bucket_bsz is None:
            return self._run_eager(
                backbone_hidden,
                first_cb_token,
                temperature,
                top_k,
                top_p,
                do_sample,
                guidance_scale,
            )

        # Swap to the selected bucket's state
        state = self._bucket_graphs[bucket_bsz]
        self._swap_to_bucket(state)
        bucket_half = self.half

        if actual_batch == 1:
            self.backbone_hidden_buf[:1].copy_(backbone_hidden[:1])
            self.first_cb_token_buf[:1].copy_(first_cb_token[:1])
        else:
            # Preserve the CFG layout expected by _cfg_sample:
            # [cond real][cond pad][uncond real][uncond pad].
            self._copy_cfg_padded(
                self.backbone_hidden_buf, backbone_hidden, actual_batch, bucket_half
            )
            self._copy_cfg_padded(
                self.first_cb_token_buf, first_cb_token, actual_batch, bucket_half
            )

        # Set sampling params with padding
        if temperature is not None:
            self._set_param_padded(
                self.temperature_buf, temperature, actual_half, bucket_half
            )
        if top_k is not None:
            self._set_param_padded(self.top_k_buf, top_k, actual_half, bucket_half)
        if top_p is not None:
            self._set_param_padded(self.top_p_buf, top_p, actual_half, bucket_half)
        if do_sample is not None:
            self._set_param_padded(
                self.do_sample_buf, do_sample, actual_half, bucket_half, is_1d=True
            )
        if guidance_scale is not None:
            self._set_param_padded(
                self.guidance_scale, guidance_scale, actual_half, bucket_half
            )

        # Replay graph
        self.static_cache.reset()
        state.graph.replay()

        if self.debug and self._debug_head_input is not None:
            head = self._orig_codebooks_head
            for cb_idx in range(self.num_decode_codebooks):
                if cb_idx == 0:
                    head(
                        self._debug_head_input[0], cache_position=self.head_prefill_pos
                    )
                else:
                    head(
                        self._debug_head_input[cb_idx],
                        cache_position=self.decode_cache_positions[cb_idx - 1],
                    )
                torch.multinomial(
                    self._debug_probs[cb_idx], 1, _hook_only_for_debug=True
                )

        # Slice output to actual_half (discard padding)
        return self.output_tokens[:actual_half].clone()
