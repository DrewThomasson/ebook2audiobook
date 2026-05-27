# coding=utf-8
# Copyright 2026 The Alibaba Qwen team.
# SPDX-License-Identifier: Apache-2.0
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
import base64
import io
import urllib.request
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse

import librosa
import numpy as np
import soundfile as sf
import torch
from torch.nn.utils.rnn import pad_sequence
from transformers import AutoConfig, AutoFeatureExtractor, AutoModel

from ..core import (
    Qwen3TTSTokenizerV1Config,
    Qwen3TTSTokenizerV1Model,
    Qwen3TTSTokenizerV2Config,
    Qwen3TTSTokenizerV2Model,
)

AudioInput = Union[
    str,  # wav path, or base64 string
    np.ndarray,  # 1-D float array
    List[str],
    List[np.ndarray],
]


class Qwen3TTSTokenizer:
    """
    A wrapper for Qwen3 TTS Tokenizer 25Hz/12Hz with HuggingFace-style loading.

    - from_pretrained(): loads speech tokenizer model via AutoModel and feature_extractor via AutoFeatureExtractor.
    - encode(): supports wav path(s), base64 audio string(s), numpy array(s).
    - decode(): accepts either the raw model encode output, or a minimal dict/list-of-dicts.

    Notes:
    - For numpy array input, you must pass `sr` so the audio can be resampled to model sample rate.
    - Returned audio is float32 numpy arrays and the output sample rate.
    """

    def __init__(self):
        self.model = None
        self.feature_extractor = None
        self.config = None
        self.device = None

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: str, **kwargs) -> "Qwen3TTSTokenizer":
        """
        Initialize tokenizer with HuggingFace `from_pretrained` style.

        Args:
            pretrained_model_name_or_path (str):
                HuggingFace repo id or local directory.
            **kwargs (Any):
                Forwarded to `AutoModel.from_pretrained(...)` directly.
                Typical examples: device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="eager".

        Returns:
            Qwen3TTSTokenizer:
                Initialized instance with `model`, `feature_extractor`, `config`.
        """
        inst = cls()

        AutoConfig.register("qwen3_tts_tokenizer_25hz", Qwen3TTSTokenizerV1Config)
        AutoModel.register(Qwen3TTSTokenizerV1Config, Qwen3TTSTokenizerV1Model)

        AutoConfig.register("qwen3_tts_tokenizer_12hz", Qwen3TTSTokenizerV2Config)
        AutoModel.register(Qwen3TTSTokenizerV2Config, Qwen3TTSTokenizerV2Model)

        inst.feature_extractor = AutoFeatureExtractor.from_pretrained(pretrained_model_name_or_path)
        inst.model = AutoModel.from_pretrained(pretrained_model_name_or_path, **kwargs)
        inst.config = inst.model.config

        inst.device = getattr(inst.model, "device", None)
        if inst.device is None:
            # fallback: infer from first parameter device
            try:
                inst.device = next(inst.model.parameters()).device
            except StopIteration:
                inst.device = torch.device("cpu")

        return inst

    def _is_probably_base64(self, s: str) -> bool:
        if s.startswith("data:audio"):
            return True
        # Heuristic: no filesystem path separators and long enough.
        if ("/" not in s and "\\" not in s) and len(s) > 256:
            return True
        return False
    
    def _is_url(self, s: str) -> bool:
        try:
            u = urlparse(s)
            return u.scheme in ("http", "https") and bool(u.netloc)
        except Exception:
            return False

    def _decode_base64_to_wav_bytes(self, b64: str) -> bytes:
        # Accept both "data:audio/wav;base64,...." and raw base64
        if "," in b64 and b64.strip().startswith("data:"):
            b64 = b64.split(",", 1)[1]
        return base64.b64decode(b64)

    def load_audio(
        self,
        x: str,
        target_sr: int,
    ) -> np.ndarray:
        """
        Load audio from wav path or base64 string, then resample to target_sr.

        Args:
            x (str):
                A wav file path, or a base64 audio string (raw or data URL).
            target_sr (int):
                Target sampling rate.

        Returns:
            np.ndarray:
                1-D float32 waveform at target_sr.
        """
        if self._is_url(x):
            with urllib.request.urlopen(x) as resp:
                audio_bytes = resp.read()
            with io.BytesIO(audio_bytes) as f:
                audio, sr = sf.read(f, dtype="float32", always_2d=False)
        elif self._is_probably_base64(x):
            wav_bytes = self._decode_base64_to_wav_bytes(x)
            with io.BytesIO(wav_bytes) as f:
                audio, sr = sf.read(f, dtype="float32", always_2d=False)
        else:
            audio, sr = librosa.load(x, sr=None, mono=True)

        if audio.ndim > 1:
            audio = np.mean(audio, axis=-1)

        if sr != target_sr:
            audio = librosa.resample(y=audio, orig_sr=sr, target_sr=target_sr)

        return audio.astype(np.float32)

    def _normalize_audio_inputs(
        self,
        audios: AudioInput,
        sr: Optional[int],
    ) -> List[np.ndarray]:
        """
        Normalize all supported input types into a list of 1-D numpy float32 waveforms
        at `self.feature_extractor.sampling_rate`.

        Args:
            audios (AudioInput):
                - str: wav path OR base64 audio string
                - np.ndarray: raw waveform (sr must be provided)
                - list[str] / list[np.ndarray]
            sr (Optional[int]):
                Sampling rate for raw numpy input. Required if input is np.ndarray or list[np.ndarray].

        Returns:
            List[np.ndarray]:
                List of float32 waveforms resampled to model input SR.
        """
        target_sr = int(self.feature_extractor.sampling_rate)

        if isinstance(audios, (str, np.ndarray)):
            audios = [audios]

        if len(audios) == 0:
            return []

        if isinstance(audios[0], str):
            # wav path list or base64 list
            return [self.load_audio(x, target_sr=target_sr) for x in audios]  # type: ignore[arg-type]

        # numpy list
        if sr is None:
            raise ValueError("For numpy waveform input, you must provide `sr` (original sampling rate).")

        out: List[np.ndarray] = []
        for a in audios:  # type: ignore[assignment]
            if not isinstance(a, np.ndarray):
                raise TypeError("Mixed input types are not supported. Use all paths/base64 or all numpy arrays.")
            if a.ndim > 1:
                a = np.mean(a, axis=-1)
            if int(sr) != target_sr:
                a = librosa.resample(y=a.astype(np.float32), orig_sr=int(sr), target_sr=target_sr)
            out.append(a.astype(np.float32))
        return out

    def encode(
        self,
        audios: AudioInput,
        sr: Optional[int] = None,
        return_dict: bool = True,
    ):
        """
        Batch-encode audio into discrete codes (and optional conditioning, depending on 25Hz/12Hz).

        Args:
            audios (AudioInput):
                Supported forms:
                - np.ndarray: waveform (requires sr)
                - list[np.ndarray]: waveforms (requires sr)
                - str: wav path OR base64 audio string
                - list[str]: wav paths and/or base64 strings
            sr (Optional[int], default=None):
                Original sampling rate for numpy waveform input.
            return_dict (bool, default=True):
                Forwarded to model.encode(...). If True, returns ModelOutput.

        Returns:
            25Hz:
                Qwen3TTSTokenizerV1EncoderOutput (if return_dict=True) with fields:
                  - audio_codes: List[torch.LongTensor] each (codes_len,)
                  - xvectors:   List[torch.FloatTensor] each (xvector_dim,)
                  - ref_mels:   List[torch.FloatTensor] each (mel_len, mel_dim)
            12Hz:
                Qwen3TTSTokenizerV2EncoderOutput (if return_dict=True) with fields:
                  - audio_codes: List[torch.LongTensor] each (codes_len, num_quantizers)

            If return_dict=False, returns the raw tuple from model.encode.
        """
        wavs = self._normalize_audio_inputs(audios, sr=sr)

        inputs = self.feature_extractor(
            raw_audio=wavs,
            sampling_rate=int(self.feature_extractor.sampling_rate),
            return_tensors="pt",
        )
        inputs = inputs.to(self.device).to(self.model.dtype)

        with torch.inference_mode():
            # model.encode expects (B, T) and (B, T)
            enc = self.model.encode(
                inputs["input_values"].squeeze(1),
                inputs["padding_mask"].squeeze(1),
                return_dict=return_dict,
            )
        return enc

    def decode(
        self,
        encoded,
    ) -> Tuple[List[np.ndarray], int]:
        """
        Decode back to waveform.

        Usage:
        1) Pass the raw output of `encode(...)` directly (recommended).
           - 25Hz: expects fields audio_codes, xvectors, ref_mels
           - 12Hz: expects field audio_codes
        2) Pass a dict or list[dict] (minimal form) for custom pipelines:
           - 25Hz dict keys: {"audio_codes", "xvectors", "ref_mels"}
           - 12Hz dict keys: {"audio_codes"}
           Values can be torch tensors or numpy arrays.

        Args:
            encoded (Any):
                - ModelOutput returned by `encode()`, OR
                - dict, OR
                - list[dict]

        Returns:
            Tuple[List[np.ndarray], int]:
                - wavs: list of 1-D float32 numpy arrays
                - sample_rate: int, model output sampling rate
        """
        model_type = self.model.get_model_type()

        def _to_tensor(x, dtype=None):
            if isinstance(x, torch.Tensor):
                return x
            x = np.asarray(x)
            t = torch.from_numpy(x)
            if dtype is not None:
                t = t.to(dtype)
            return t

        # Normalize `encoded` into the same shapes as the official demo uses.
        if hasattr(encoded, "audio_codes"):
            # ModelOutput from encode()
            audio_codes_list = encoded.audio_codes
            xvectors_list = getattr(encoded, "xvectors", None)
            ref_mels_list = getattr(encoded, "ref_mels", None)
        elif isinstance(encoded, dict):
            audio_codes_list = encoded["audio_codes"]
            xvectors_list = encoded.get("xvectors", None)
            ref_mels_list = encoded.get("ref_mels", None)
        elif isinstance(encoded, list):
            # list of dicts
            audio_codes_list = [e["audio_codes"] for e in encoded]
            xvectors_list = [e["xvectors"] for e in encoded] if ("xvectors" in encoded[0]) else None
            ref_mels_list = [e["ref_mels"] for e in encoded] if ("ref_mels" in encoded[0]) else None
        else:
            raise TypeError("`encoded` must be an encode output, a dict, or a list of dicts.")

        # Ensure list form for per-sample tensors
        if isinstance(audio_codes_list, torch.Tensor):
            # Could be a single sample tensor or an already padded batch tensor.
            t = audio_codes_list
            if t.dim() == 1:
                # 25Hz single sample: (C,) -> (1, C)
                t = t.unsqueeze(0)
            elif t.dim() == 2:
                # 12Hz single sample: (C, Q) -> (1, C, Q)
                t = t.unsqueeze(0)
            audio_codes_padded = t.to(self.device)
        else:
            # List[Tensor/np]
            audio_codes_list = [_to_tensor(c, dtype=torch.long) for c in audio_codes_list]
            audio_codes_padded = pad_sequence(audio_codes_list, batch_first=True, padding_value=-1).to(self.device)

        with torch.inference_mode():
            if model_type == "qwen3_tts_tokenizer_25hz":
                if xvectors_list is None or ref_mels_list is None:
                    raise ValueError("25Hz decode requires `xvectors` and `ref_mels`.")

                if isinstance(xvectors_list, torch.Tensor):
                    xvectors_batch = xvectors_list
                    if xvectors_batch.dim() == 1:  # (D,) -> (1, D)
                        xvectors_batch = xvectors_batch.unsqueeze(0)
                    xvectors_batch = xvectors_batch.to(self.device).to(self.model.dtype)
                else:
                    xvectors_list = [_to_tensor(x, dtype=torch.float32) for x in xvectors_list]
                    xvectors_batch = torch.stack(xvectors_list, dim=0).to(self.device).to(self.model.dtype)

                if isinstance(ref_mels_list, torch.Tensor):
                    ref_mels_padded = ref_mels_list
                    if ref_mels_padded.dim() == 2:  # (T, M) -> (1, T, M)
                        ref_mels_padded = ref_mels_padded.unsqueeze(0)
                    ref_mels_padded = ref_mels_padded.to(self.device).to(self.model.dtype)
                else:
                    ref_mels_list = [_to_tensor(m, dtype=torch.float32) for m in ref_mels_list]
                    ref_mels_padded = pad_sequence(ref_mels_list, batch_first=True, padding_value=0).to(self.device).to(self.model.dtype)

                dec = self.model.decode(audio_codes_padded, xvectors_batch, ref_mels_padded, return_dict=True)
                wav_tensors = dec.audio_values

            elif model_type == "qwen3_tts_tokenizer_12hz":
                dec = self.model.decode(audio_codes_padded, return_dict=True)
                wav_tensors = dec.audio_values

            else:
                raise ValueError(f"Unknown model type: {model_type}")

        wavs = [w.to(torch.float32).detach().cpu().numpy() for w in wav_tensors]
        return wavs, int(self.model.get_output_sample_rate())

    def get_model_type(self) -> str:
        """
        Get the underlying tokenizer model type.

        Returns:
            str: Model type string from `self.model.config.model_type`
                (e.g. "qwen3_tts_tokenizer_25hz" / "qwen3_tts_tokenizer_12hz").
        """
        return self.model.get_model_type()

    def get_input_sample_rate(self) -> int:
        """
        Get the expected input sample rate for encoding.

        Returns:
            int: Input sample rate (Hz).
        """
        return int(self.model.get_input_sample_rate())

    def get_output_sample_rate(self) -> int:
        """
        Get the output sample rate for decoded waveforms.

        Returns:
            int: Output sample rate (Hz).
        """
        return int(self.model.get_output_sample_rate())

    def get_encode_downsample_rate(self) -> int:
        """
        Get the encoder downsample rate (waveform samples per code step).

        Returns:
            int: Encode downsample rate.
        """
        return int(self.model.get_encode_downsample_rate())

    def get_decode_upsample_rate(self) -> int:
        """
        Get the decoder upsample rate (waveform samples per code step).

        Returns:
            int: Decode upsample rate.
        """
        return int(self.model.get_decode_upsample_rate())