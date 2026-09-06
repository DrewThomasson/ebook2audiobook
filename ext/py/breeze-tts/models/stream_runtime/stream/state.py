from __future__ import annotations

import logging
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

import torch

from .kv_cache import StaticShiftKVCache

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ConvStateBlock:
    cache_buf: torch.Tensor
    left_cache_len: int


@dataclass
class TransConvStateBlock:
    cache_buf: torch.Tensor
    left_cache_len: int


@dataclass
class RequestStateSlot:
    req_id: str | None
    next_step: int
    tail_flushed: bool
    conv1d: dict[str, ConvStateBlock]
    tconv1d: dict[str, TransConvStateBlock]
    kv: StaticShiftKVCache


def reset_request_state(slot: RequestStateSlot) -> None:
    slot.req_id = None
    slot.next_step = 0
    slot.tail_flushed = False
    for block in slot.conv1d.values():
        block.cache_buf.zero_()
    for block in slot.tconv1d.values():
        block.cache_buf.zero_()
    for layer in slot.kv.layers:
        layer.k.zero_()
        layer.v.zero_()


class RequestStatePool(Generic[T]):
    def __init__(
        self,
        create_slot: Callable[[], T],
        reset_slot: Callable[[T], None],
        max_active_reqs: int | None = None,
        on_evict: Callable[[str], None] | None = None,
    ):
        if max_active_reqs is not None and max_active_reqs <= 0:
            raise ValueError(
                f"max_active_reqs must be > 0 or None, got {max_active_reqs}"
            )
        self._create_slot = create_slot
        self._reset_slot = reset_slot
        self.max_active_reqs = max_active_reqs
        self._on_evict = on_evict
        self._req_to_slot: OrderedDict[str, int] = OrderedDict()
        self._slot_to_req: list[str | None] = []
        self._slots: list[T] = []
        self._pinned: set[str] = set()
        self._dynamic: dict[str, T] = {}
        if self.max_active_reqs is not None:
            self._slots = [self._create_slot() for _ in range(self.max_active_reqs)]
            self._slot_to_req = [None for _ in range(self.max_active_reqs)]

    def __len__(self) -> int:
        return (
            len(self._req_to_slot)
            if self.max_active_reqs is not None
            else len(self._dynamic)
        )

    def active_req_ids(self) -> list[str]:
        if self.max_active_reqs is None:
            return list(self._dynamic.keys())
        return list(self._req_to_slot.keys())

    def num_free_slots(self) -> int | None:
        if self.max_active_reqs is None:
            return None
        return sum(1 for req_id in self._slot_to_req if req_id is None)

    def pin(self, req_id: str) -> None:
        self._pinned.add(req_id)

    def unpin(self, req_id: str) -> None:
        self._pinned.discard(req_id)

    def _find_free_slot(self) -> int | None:
        for idx, req_id in enumerate(self._slot_to_req):
            if req_id is None:
                return idx
        return None

    def _evict_lru(self) -> int:
        victim_req_id: str | None = None
        for req_id in self._req_to_slot.keys():
            if req_id not in self._pinned:
                victim_req_id = req_id
                break
        if victim_req_id is None:
            logger.error(
                "RequestStatePool found no evictable request. max_active_reqs=%s active_req_ids=%s pinned=%s",
                self.max_active_reqs,
                list(self._req_to_slot.keys()),
                sorted(self._pinned),
            )
            raise RuntimeError("No evictable request state slot available.")
        slot_idx = self._req_to_slot.pop(victim_req_id)
        self._slot_to_req[slot_idx] = None
        self._reset_slot(self._slots[slot_idx])
        if self._on_evict is not None:
            self._on_evict(victim_req_id)
        logger.info(
            "Evicted request state due to LRU capacity limit: req_id=%s slot_idx=%d",
            victim_req_id,
            slot_idx,
        )
        return slot_idx

    def get(self, req_id: str) -> T:
        if self.max_active_reqs is None:
            value = self._dynamic.get(req_id)
            if value is None:
                value = self._create_slot()
                self._dynamic[req_id] = value
            return value
        slot_idx = self._req_to_slot.get(req_id)
        if slot_idx is None:
            slot_idx = self._find_free_slot()
            if slot_idx is None:
                slot_idx = self._evict_lru()
            self._slot_to_req[slot_idx] = req_id
            self._req_to_slot[req_id] = slot_idx
            self._reset_slot(self._slots[slot_idx])
        self._req_to_slot.move_to_end(req_id)
        return self._slots[slot_idx]

    def pop(self, req_id: str) -> None:
        self._pinned.discard(req_id)
        if self.max_active_reqs is None:
            self._dynamic.pop(req_id, None)
            return
        slot_idx = self._req_to_slot.pop(req_id, None)
        if slot_idx is None:
            return
        self._reset_slot(self._slots[slot_idx])
        self._slot_to_req[slot_idx] = None

    def get_slot_index(self, req_id: str) -> int | None:
        if self.max_active_reqs is None:
            return None
        return self._req_to_slot.get(req_id)
