#!/usr/bin/env python3
# Copyright    2026  Xiaomi Corp.        (authors:  Han Zhu)
#
# See ../../LICENSE for clarification regarding multiple authors
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

"""Data collators for OmniVoice training.

Two strategies are available:

- ``PackingDataCollator``: Concatenates samples into a single long sequence
  (sequence packing). Used with flex_attention. Batch shape is ``[1, C, L]``.
- ``PaddingDataCollator``: Pads samples to the same length and stacks them.
  Used with SDPA/eager attention. Batch shape is ``[B, C, max_len]``.
"""

from typing import Any, Dict, List

import torch


class PaddingDataCollator:
    """Pads a list of processed samples to the same length and stacks them.

    Produces a standard ``[B, C, max_len]`` batch suitable for SDPA/eager
    attention, where B is the number of samples in the batch, C is the number
    of audio codebook layers, and max_len is the longest sequence in the batch.

    A 4D boolean attention mask of shape ``[B, 1, max_len, max_len]`` is included.
    Each query position can attend to all non-padding key positions (bidirectional),
    matching the masked-diffusion training objective. When passed as a 4D tensor,
    HuggingFace models use it directly without adding an additional causal mask.

    No ``document_ids`` are emitted — each sample occupies its own batch row.
    """

    def __init__(self, processor, batch_tokens: int):
        self.batch_tokens = batch_tokens
        self.processor = processor

    def __call__(self, processed_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        pad_id = self.processor.text_tokenizer.pad_token_id
        max_len = max(s["length"] for s in processed_samples)
        B = len(processed_samples)

        padded_input_ids = []
        padded_labels = []
        padded_audio_mask = []
        padded_position_ids = []
        # valid[b, j] = True if position j is a real (non-padding) token for sample b
        valid = torch.zeros(B, max_len, dtype=torch.bool)

        for i, s in enumerate(processed_samples):
            length = s["length"]
            pad = max_len - length

            padded_input_ids.append(
                torch.nn.functional.pad(s["input_ids"], (0, pad), value=pad_id)
            )  # [C, max_len]
            padded_labels.append(
                torch.nn.functional.pad(s["labels"], (0, pad), value=-100)
            )  # [C, max_len]
            padded_audio_mask.append(
                torch.nn.functional.pad(s["audio_mask"], (0, pad), value=False)
            )  # [max_len]
            padded_position_ids.append(
                torch.nn.functional.pad(
                    torch.arange(length, dtype=torch.long), (0, pad), value=0
                )
            )  # [max_len]
            valid[i, :length] = True

        # Stack into [B, C, max_len] / [B, max_len]
        input_ids = torch.stack(padded_input_ids, dim=0)      # [B, C, max_len]
        labels = torch.stack(padded_labels, dim=0)             # [B, C, max_len]
        audio_mask = torch.stack(padded_audio_mask, dim=0)     # [B, max_len]
        position_ids = torch.stack(padded_position_ids, dim=0) # [B, max_len]

        # 4D bidirectional attention mask: mask[b, 0, i, j] = valid[b, j]
        # All query positions attend to all non-padding key positions.
        attention_mask = valid[:, None, None, :].expand(B, 1, max_len, max_len).contiguous()

        return {
            "input_ids": input_ids,           # [B, C, max_len]
            "labels": labels,                  # [B, C, max_len]
            "audio_mask": audio_mask,          # [B, max_len]
            "position_ids": position_ids,      # [B, max_len]
            "attention_mask": attention_mask,  # [B, 1, max_len, max_len]
        }


class PackingDataCollator:
    def __init__(self, processor, batch_tokens: int):
        self.batch_tokens = batch_tokens
        self.processor = processor

    def __call__(self, processed_samples: List[Dict[str, Any]]) -> Dict[str, Any]:

        target_length = self.batch_tokens

        input_ids = torch.cat(
            [s["input_ids"] for s in processed_samples], dim=1
        )  # [C, Total_Len], C is the number of codebook layers of the audio tokenizer
        labels = torch.cat(
            [s["labels"] for s in processed_samples], dim=1
        )  # [C, Total_Len]
        audio_mask = torch.cat(
            [s["audio_mask"] for s in processed_samples], dim=0
        )  # [Total_Len]

        position_ids = torch.cat(
            [torch.arange(s["length"], dtype=torch.long) for s in processed_samples],
            dim=0,
        )  # [Total_Len]

        pad_length = target_length - input_ids.shape[1]

        input_ids = torch.nn.functional.pad(
            input_ids,
            pad=(0, pad_length),
            value=self.processor.text_tokenizer.pad_token_id,
        )

        labels = torch.nn.functional.pad(labels, pad=(0, pad_length), value=-100)

        audio_mask = torch.nn.functional.pad(
            audio_mask, pad=(0, pad_length), value=False
        )

        position_ids = torch.nn.functional.pad(
            position_ids, pad=(0, pad_length), value=0
        )

        return_list = {
            "input_ids": input_ids.unsqueeze(0),  # [1, C, L]
            "labels": labels.unsqueeze(0),  # [1, C, L]
            "audio_mask": audio_mask.unsqueeze(0),  # [1, L]
            "position_ids": position_ids.unsqueeze(0),  # [1, L]
        }

        document_ids_list = []

        for i, s in enumerate(processed_samples):
            seq_len = s["length"]
            document_ids_list.append(torch.full((seq_len,), i, dtype=torch.int32))

        document_ids = torch.cat(document_ids_list, dim=0)

        document_ids = torch.nn.functional.pad(
            document_ids, pad=(0, pad_length), value=-1
        )
        return_list["document_ids"] = document_ids.unsqueeze(0)  # [1, L]

        return return_list
