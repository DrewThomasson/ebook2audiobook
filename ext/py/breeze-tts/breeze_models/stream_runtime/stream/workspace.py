from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

import torch

W = TypeVar("W")


@dataclass
class ConvWorkspaceBlock:
    x_buf: torch.Tensor


@dataclass
class TransConvWorkspaceBlock:
    x_buf: torch.Tensor


@dataclass
class WorkspaceSlot:
    conv1d: dict[str, ConvWorkspaceBlock]
    tconv1d: dict[str, TransConvWorkspaceBlock]


def reset_workspace(slot: WorkspaceSlot) -> None:
    for block in slot.conv1d.values():
        block.x_buf.zero_()
    for block in slot.tconv1d.values():
        block.x_buf.zero_()


class WorkspacePool(Generic[W]):
    def __init__(
        self, create_slot: Callable[[], W], reset_slot: Callable[[W], None], size: int
    ):
        if size <= 0:
            raise ValueError(f"workspace pool size must be > 0, got {size}")
        self._reset_slot = reset_slot
        self._slots: list[W] = [create_slot() for _ in range(size)]
        self._free: list[int] = list(range(size))

    def __len__(self) -> int:
        return len(self._slots)

    def num_free_slots(self) -> int:
        return len(self._free)

    def acquire(self) -> tuple[int, W]:
        if not self._free:
            raise RuntimeError("No free workspace slot available.")
        slot_idx = self._free.pop(0)
        slot = self._slots[slot_idx]
        self._reset_slot(slot)
        return slot_idx, slot

    def release(self, slot_idx: int) -> None:
        if slot_idx in self._free:
            return
        self._reset_slot(self._slots[slot_idx])
        self._free.append(slot_idx)
        self._free.sort()

    def get_slot(self, slot_idx: int) -> W:
        return self._slots[slot_idx]
