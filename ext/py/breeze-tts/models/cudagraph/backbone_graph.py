"""
CUDA graph capture for the Breeze backbone's single-token decode step,
using transformers StaticCache.

The backbone (BreezeBackboneModel) predicts the first codebook token at each step.
For CFG, we run batch=2 (cond + uncond) and apply the guidance formula inside
the graph so it's captured as a single replay.

Strategy:
- Use transformers StaticCache for KV cache management
- Use the model's forward method (handles mask, RoPE, attention internally)
- Capture single-token decode + lm_head + CFG as a CUDA graph
- Update cache_position buffer between replays
- Batch size changes trigger automatic recapture via ensure_batch_size()
"""

import torch
from transformers import StaticCache
from transformers.masking_utils import create_causal_mask


class BackboneGraph:
    """
    Captures the Breeze backbone's single-token decode step as a CUDA graph,
    using the model's own forward with transformers StaticCache.

    Supports batch=2 for CFG (cond=batch[0], uncond=batch[1]).

    Batch size changes trigger automatic recapture:
        graph.ensure_batch_size(4)

    guidance_scale is runtime-mutable without recapture:
        graph.guidance_scale.fill_(5.0)
    """

    def __init__(
        self,
        backbone_model,
        lm_head,
        embed_tokens,
        config,
        device="cuda:0",
        dtype=torch.bfloat16,
        max_seq_len=512,
        guidance_scale=3.0,
        debug: bool = False,
        batch_size: int = 1,
    ):
        self.device = device
        self.dtype = dtype
        self.debug = debug
        self.no_graph = (
            False  # runtime flag: True = skip graph replay (for layer-diff hooks)
        )
        self.max_seq_len = max_seq_len
        self.hidden_size = config.hidden_size
        self.num_layers = config.num_hidden_layers
        self.vocab_size = getattr(lm_head, "out_features", config.vocab_size)
        self.num_codebooks = config.num_codebooks
        self.config = config
        self.batch_size = batch_size
        self.half = self._real_batch_size(batch_size)

        # Keep references to model components
        self.model = backbone_model  # BreezeBackboneModel
        self.lm_head = lm_head  # nn.Linear(hidden_size, vocab_size)
        self.embed_tokens = embed_tokens  # BreezeBackboneModelEmbeddings

        # Cast lm_head to fp32 for numerical stability (hooks still fire through module forward)
        self.lm_head = self.lm_head.float()

        # Transformers StaticCache — batch=2 for CFG
        self.static_cache = StaticCache(
            config=config, max_cache_len=max_seq_len, batch_size=self.batch_size
        )

        # Cache position buffer — [1] for KV cache slot (shared across batch)
        self.cache_position = torch.zeros(1, dtype=torch.long, device=device)
        # Per-batch position_ids for RoPE — [batch_size, 1]
        self.position_ids = torch.zeros(
            self.batch_size, 1, dtype=torch.long, device=device
        )
        # Base position for each batch (set by set_generation_state from attention_mask)
        self._base_position = torch.zeros(
            self.batch_size, dtype=torch.long, device=device
        )

        # Guidance scale buffer — can be updated at runtime via fill_()
        self.guidance_scale = torch.tensor(
            [guidance_scale], dtype=torch.float32, device=device
        )

        self._alloc_buffers()

        self.graph = None
        self.captured = False
        self.attn_mask = None
        # Per-batch left-padding lengths for vectorized mask construction
        self._pad_lens = torch.zeros(self.batch_size, dtype=torch.long, device=device)
        # Pre-allocated index range [0, 1, ..., max_seq_len-1] for broadcasting
        self._kv_indices = torch.arange(max_seq_len, dtype=torch.long, device=device)

    @staticmethod
    def _real_batch_size(batch_size: int) -> int:
        if batch_size <= 1:
            return batch_size
        return batch_size // 2

    # ------------------------------------------------------------------
    # Buffer allocation (called from __init__ and _rebuild_for_batch)
    # ------------------------------------------------------------------

    def _alloc_buffers(self):
        """Allocate / re-allocate I/O buffers for current batch_size."""
        # Input: codebook IDs [batch, 1, num_codebooks]
        self.input_ids_buf = torch.zeros(
            self.batch_size, 1, self.num_codebooks, dtype=torch.long, device=self.device
        )
        # Hidden states output [batch, 1, hidden_size]
        self.hidden_buf = torch.zeros(
            self.batch_size, 1, self.hidden_size, dtype=self.dtype, device=self.device
        )
        # Raw logits [batch, vocab_size]
        self.logits_buf = torch.zeros(
            self.batch_size, self.vocab_size, dtype=torch.float32, device=self.device
        )
        # CFG-applied logits [half, vocab_size]
        self.cfg_logits_buf = torch.zeros(
            self.half, self.vocab_size, dtype=torch.float32, device=self.device
        )

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
        self.half = self._real_batch_size(batch_size)
        self.static_cache = StaticCache(
            config=self.config, max_cache_len=self.max_seq_len, batch_size=batch_size
        )
        # Re-allocate buffers for new batch_size
        self.cache_position = torch.zeros(1, dtype=torch.long, device=self.device)
        self.position_ids = torch.zeros(
            batch_size, 1, dtype=torch.long, device=self.device
        )
        self._base_position = torch.zeros(
            batch_size, dtype=torch.long, device=self.device
        )
        self._alloc_buffers()
        self.captured = False
        self.graph = None
        self.attn_mask = None
        self._pad_lens = torch.zeros(batch_size, dtype=torch.long, device=self.device)
        self._kv_indices = torch.arange(
            self.max_seq_len, dtype=torch.long, device=self.device
        )
        if self.no_graph:
            self.prepare_eager()
        else:
            self.capture()

    @torch.inference_mode()
    def prepare_eager(self):
        """Initialize fixed eager buffers without compile or CUDA Graph capture."""
        self.no_graph = True
        self._init_cache_layers()
        self._build_initial_attention_mask()
        self.captured = False
        return self

    def _init_cache_layers(self):
        """Force lazy initialization of StaticCache layers before graph capture."""
        config = self.model.config
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

    def _build_initial_attention_mask(self):
        """Build a default causal mask (no padding) for graph capture/warmup.

        Uses create_causal_mask once at position 0 to determine the correct
        shape and dtype, then allocates self.attn_mask as a static buffer.
        """
        dummy = torch.zeros(
            self.batch_size, 1, self.hidden_size, dtype=self.dtype, device=self.device
        )
        pos = torch.tensor([0], device=self.device)
        mask = create_causal_mask(
            config=self.model.config,
            input_embeds=dummy,
            attention_mask=None,
            cache_position=pos,
            past_key_values=self.static_cache,
        )
        # mask shape: [batch, 1, 1, max_seq_len], dtype may be float or bool
        if mask is None or mask.dtype == torch.bool:
            # Some attn implementations return bool or None; allocate float mask
            self.attn_mask = torch.zeros(
                self.batch_size,
                1,
                1,
                self.max_seq_len,
                dtype=self.dtype,
                device=self.device,
            )
        elif self.attn_mask is None:
            self.attn_mask = mask.clone()
        else:
            self.attn_mask.copy_(mask)
        print(
            f"[BackboneGraph] Initial attention mask shape: {self.attn_mask.shape}, dtype: {self.attn_mask.dtype}"
        )

        self._mask_min_val = torch.finfo(self.attn_mask.dtype).min

    def _set_attention_mask(self, position: int):
        """Construct attention mask in-place from pad_lens and cache_position.

        For each batch i, the valid KV range is [pad_lens[i], position].
        Everything outside is masked with -inf. Fully vectorized, no loops.

        attn_mask shape: [batch, 1, 1, max_seq_len]
        """
        # kv_indices: [max_seq_len], pad_lens: [batch, 1], position: scalar
        kv = self._kv_indices  # [S]
        lo = self._pad_lens.unsqueeze(1)  # [B, 1]
        valid = (kv >= lo) & (kv <= position)  # [B, S]
        self.attn_mask.fill_(self._mask_min_val)
        self.attn_mask[:, 0, 0, :].masked_fill_(valid, 0.0)

    def _decode_step(self):
        """Single-token decode: embed → backbone forward → lm_head → CFG."""
        # 1. Embed codebook tokens (sum of num_codebooks embeddings)
        inputs_embeds = self.embed_tokens(self.input_ids_buf)  # [batch, 1, H]

        # 2. Backbone forward with per-batch position_ids and shared cache_position
        # position_ids: [batch_size, 1] — per-batch logical position for RoPE
        # cache_position: [1] — shared KV cache slot for all batches
        out = self.model(
            inputs_embeds=inputs_embeds,
            attention_mask=self.attn_mask,
            past_key_values=self.static_cache,
            position_ids=self.position_ids,
            cache_position=self.cache_position,
            use_cache=True,
        )
        self.hidden_buf.copy_(out.last_hidden_state)

        # 3. lm_head → logits (lm_head is fp32, input cast to fp32)
        logits = self.lm_head(self.hidden_buf[:, -1, :].float())  # [batch, vocab] fp32
        self.logits_buf.copy_(logits)

        # 4. CFG when paired cond/uncond rows are present; otherwise pass through.
        if self.batch_size >= 2:
            cond_logits = self.logits_buf[: self.half]
            uncond_logits = self.logits_buf[self.half :]
            cfg_result = uncond_logits + self.guidance_scale * (
                cond_logits - uncond_logits
            )
        else:
            cfg_result = self.logits_buf[: self.half]
        self.cfg_logits_buf.copy_(cfg_result)

    @torch.inference_mode()
    def capture(self, prefill_len=100, num_warmup=3):
        """Capture CUDA graph for single-token decode."""
        print(f"Warming up backbone graph ({num_warmup} runs)...")

        self._init_cache_layers()
        self._build_initial_attention_mask()

        # Initialize positions for warmup
        self.cache_position[0] = prefill_len
        self.position_ids.fill_(prefill_len)
        self._pad_lens.zero_()
        self._set_attention_mask(prefill_len)

        for _ in range(num_warmup):
            self._decode_step()
        torch.cuda.synchronize(device=self.device)

        print("Capturing CUDA graph for backbone decode...")
        self.graph = torch.cuda.CUDAGraph()

        s = torch.cuda.Stream(device=self.device)
        s.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(s):
            self._decode_step()
            torch.cuda.synchronize(device=self.device)

            with torch.cuda.graph(self.graph):
                self._decode_step()

        torch.cuda.current_stream().wait_stream(s)
        torch.cuda.synchronize(device=self.device)
        self.captured = True
        print("Backbone CUDA graph captured!")

    @torch.inference_mode()
    def reset(self):
        """Reset cache for new sequence."""
        self.static_cache.reset()

    @torch.inference_mode()
    def finish_direct_prefill(self, seq_len: int) -> int:
        self._prefill_len = int(seq_len)
        return self._prefill_len

    @torch.inference_mode()
    def prefill_kv(self, past_key_values):
        """
        Copy HF DynamicCache from prefill into our StaticCache.
        past_key_values: DynamicCache with num_layers layers of [batch, kv_heads, seq_len, head_dim]

        For CFG: the DynamicCache should already have batch=2.
        """
        self.static_cache.reset()
        seq_len = 0
        for li in range(self.num_layers):
            k, v = past_key_values[li]
            seq_len = k.shape[2]
            if seq_len > self.max_seq_len:
                raise RuntimeError(
                    f"Input too long: prefill has {seq_len} tokens but max_seq_len={self.max_seq_len}."
                )
            cache_pos = torch.arange(seq_len, device=self.device)
            self.static_cache.update(k, v, li, {"cache_position": cache_pos})
        self._prefill_len = seq_len  # remember for decode cache_position
        return seq_len

    @torch.inference_mode()
    def set_generation_state(self, attention_mask=None):
        """Initialize per-batch position_ids and pad_lens from attention_mask.

        For left-padded inputs, pad_lens[i] = number of leading zeros in
        attention_mask[i]. The mask is then constructed on-the-fly in
        _set_attention_mask() using pad_lens — no 512-iter table rebuild.
        """
        if attention_mask is not None:
            per_batch_pos = attention_mask.sum(dim=1).long()  # [batch_size]
            self._base_position.copy_(per_batch_pos)
            self.position_ids.copy_(per_batch_pos.unsqueeze(-1))
            self.cache_position[0] = per_batch_pos.max().item()

            # Compute per-batch left-padding length:
            # pad_lens[i] = seq_len - num_valid_tokens[i]
            seq_len = attention_mask.shape[1]
            self._pad_lens.copy_(seq_len - per_batch_pos)
        else:
            self._pad_lens.zero_()

    @torch.inference_mode()
    def run(self, input_ids, step_idx):
        """
        Run one decode step.
        input_ids: [batch, 1, num_codebooks] long tensor
        step_idx: decode step index (0-based), added to per-batch base position
        Returns: (hidden_states [batch, 1, H], cfg_logits [half, vocab])
        """
        self.input_ids_buf.copy_(input_ids)
        # Update per-batch position_ids: base_position + step_idx
        self.position_ids.copy_((self._base_position + step_idx).unsqueeze(-1))
        # KV cache slot: prefill_len + step_idx (append after prefill KV, never overwrite)
        self.cache_position[0] = self._prefill_len + step_idx
        self._set_attention_mask(self.cache_position[0].item())
        if self.no_graph:
            self._decode_step()
        else:
            self.graph.replay()
            if self.debug:
                # Fake forward: trigger lm_head hooks using buffer data from replay.
                # Result is discarded — only hook side-effects matter.
                self.lm_head(self.hidden_buf[:, -1, :].float())
        return self.hidden_buf, self.cfg_logits_buf
