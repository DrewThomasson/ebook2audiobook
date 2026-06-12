from typing import Optional, Tuple

import numpy as np

from .vad import SileroVoiceActivityDetector


def trim_silence(
    audio_array: np.ndarray,
    detector: SileroVoiceActivityDetector,
    threshold: float = 0.2,
    samples_per_chunk=480,
    sample_rate=16000,
    keep_chunks_before: int = 2,
    keep_chunks_after: int = 2,
) -> Tuple[float, Optional[float]]:
    """Returns the offset/duration of trimmed audio in seconds"""
    offset_sec: float = 0.0
    duration_sec: Optional[float] = None
    first_chunk: Optional[int] = None
    last_chunk: Optional[int] = None
    seconds_per_chunk: float = samples_per_chunk / sample_rate

    chunk = audio_array[:samples_per_chunk]
    audio_array = audio_array[samples_per_chunk:]
    chunk_idx: int = 0

    # Determine main block of speech
    while len(audio_array) > 0:
        prob = detector(chunk, sample_rate=sample_rate)
        is_speech = prob >= threshold

        if is_speech:
            if first_chunk is None:
                # First speech
                first_chunk = chunk_idx
            else:
                # Last speech so far
                last_chunk = chunk_idx

        chunk = audio_array[:samples_per_chunk]
        audio_array = audio_array[samples_per_chunk:]
        chunk_idx += 1

    if (first_chunk is not None) and (last_chunk is not None):
        first_chunk = max(0, first_chunk - keep_chunks_before)
        last_chunk = min(chunk_idx, last_chunk + keep_chunks_after)

        # Compute offset/duration
        offset_sec = first_chunk * seconds_per_chunk
        last_sec = (last_chunk + 1) * seconds_per_chunk
        duration_sec = last_sec - offset_sec

    return offset_sec, duration_sec
