#!/usr/bin/env python3
import argparse
import json
import logging
import math
import sys
import time
from pathlib import Path

import numpy as np
import onnxruntime

from .vits.utils import audio_float_to_int16
from .vits.wavfile import write as write_wav

_LOGGER = logging.getLogger("piper_train.infer_onnx")


def main():
    """Main entry point"""
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(prog="piper_train.infer_onnx")
    parser.add_argument("--model", required=True, help="Path to model (.onnx)")
    parser.add_argument("--output-dir", required=True, help="Path to write WAV files")
    parser.add_argument("--sample-rate", type=int, default=22050)
    parser.add_argument("--noise-scale", type=float, default=0.667)
    parser.add_argument("--noise-scale-w", type=float, default=0.8)
    parser.add_argument("--length-scale", type=float, default=1.0)
    args = parser.parse_args()

    args.output_dir = Path(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    sess_options = onnxruntime.SessionOptions()
    _LOGGER.debug("Loading model from %s", args.model)
    model = onnxruntime.InferenceSession(str(args.model), sess_options=sess_options)
    _LOGGER.info("Loaded model from %s", args.model)

    # text_empty = np.zeros((1, 300), dtype=np.int64)
    # text_lengths_empty = np.array([text_empty.shape[1]], dtype=np.int64)
    # scales = np.array(
    #     [args.noise_scale, args.length_scale, args.noise_scale_w],
    #     dtype=np.float32,
    # )
    # bias_audio = model.run(
    #     None,
    #     {"input": text_empty, "input_lengths": text_lengths_empty, "scales": scales},
    # )[0].squeeze((0, 1))
    # bias_spec, _ = transform(bias_audio)

    for i, line in enumerate(sys.stdin):
        line = line.strip()
        if not line:
            continue

        utt = json.loads(line)
        # utt_id = utt["id"]
        utt_id = str(i)
        phoneme_ids = utt["phoneme_ids"]
        speaker_id = utt.get("speaker_id")

        text = np.expand_dims(np.array(phoneme_ids, dtype=np.int64), 0)
        text_lengths = np.array([text.shape[1]], dtype=np.int64)
        scales = np.array(
            [args.noise_scale, args.length_scale, args.noise_scale_w],
            dtype=np.float32,
        )
        sid = None

        if speaker_id is not None:
            sid = np.array([speaker_id], dtype=np.int64)

        start_time = time.perf_counter()
        audio = model.run(
            None,
            {
                "input": text,
                "input_lengths": text_lengths,
                "scales": scales,
                "sid": sid,
            },
        )[0].squeeze((0, 1))
        # audio = denoise(audio, bias_spec, 10)
        audio = audio_float_to_int16(audio.squeeze())
        end_time = time.perf_counter()

        audio_duration_sec = audio.shape[-1] / args.sample_rate
        infer_sec = end_time - start_time
        real_time_factor = (
            infer_sec / audio_duration_sec if audio_duration_sec > 0 else 0.0
        )

        _LOGGER.debug(
            "Real-time factor for %s: %0.2f (infer=%0.2f sec, audio=%0.2f sec)",
            i + 1,
            real_time_factor,
            infer_sec,
            audio_duration_sec,
        )

        output_path = args.output_dir / f"{utt_id}.wav"
        write_wav(str(output_path), args.sample_rate, audio)


def denoise(
    audio: np.ndarray, bias_spec: np.ndarray, denoiser_strength: float
) -> np.ndarray:
    audio_spec, audio_angles = transform(audio)

    a = bias_spec.shape[-1]
    b = audio_spec.shape[-1]
    repeats = max(1, math.ceil(b / a))
    bias_spec_repeat = np.repeat(bias_spec, repeats, axis=-1)[..., :b]

    audio_spec_denoised = audio_spec - (bias_spec_repeat * denoiser_strength)
    audio_spec_denoised = np.clip(audio_spec_denoised, a_min=0.0, a_max=None)
    audio_denoised = inverse(audio_spec_denoised, audio_angles)

    return audio_denoised


def stft(x, fft_size, hopsamp):
    """Compute and return the STFT of the supplied time domain signal x.
    Args:
        x (1-dim Numpy array): A time domain signal.
        fft_size (int): FFT size. Should be a power of 2, otherwise DFT will be used.
        hopsamp (int):
    Returns:
        The STFT. The rows are the time slices and columns are the frequency bins.
    """
    window = np.hanning(fft_size)
    fft_size = int(fft_size)
    hopsamp = int(hopsamp)
    return np.array(
        [
            np.fft.rfft(window * x[i : i + fft_size])
            for i in range(0, len(x) - fft_size, hopsamp)
        ]
    )


def istft(X, fft_size, hopsamp):
    """Invert a STFT into a time domain signal.
    Args:
        X (2-dim Numpy array): Input spectrogram. The rows are the time slices and columns are the frequency bins.
        fft_size (int):
        hopsamp (int): The hop size, in samples.
    Returns:
        The inverse STFT.
    """
    fft_size = int(fft_size)
    hopsamp = int(hopsamp)
    window = np.hanning(fft_size)
    time_slices = X.shape[0]
    len_samples = int(time_slices * hopsamp + fft_size)
    x = np.zeros(len_samples)
    for n, i in enumerate(range(0, len(x) - fft_size, hopsamp)):
        x[i : i + fft_size] += window * np.real(np.fft.irfft(X[n]))
    return x


def inverse(magnitude, phase):
    recombine_magnitude_phase = np.concatenate(
        [magnitude * np.cos(phase), magnitude * np.sin(phase)], axis=1
    )

    x_org = recombine_magnitude_phase
    n_b, n_f, n_t = x_org.shape  # pylint: disable=unpacking-non-sequence
    x = np.empty([n_b, n_f // 2, n_t], dtype=np.complex64)
    x.real = x_org[:, : n_f // 2]
    x.imag = x_org[:, n_f // 2 :]
    inverse_transform = []
    for y in x:
        y_ = istft(y.T, fft_size=1024, hopsamp=256)
        inverse_transform.append(y_[None, :])

    inverse_transform = np.concatenate(inverse_transform, 0)

    return inverse_transform


def transform(input_data):
    x = input_data
    real_part = []
    imag_part = []
    for y in x:
        y_ = stft(y, fft_size=1024, hopsamp=256).T
        real_part.append(y_.real[None, :, :])  # pylint: disable=unsubscriptable-object
        imag_part.append(y_.imag[None, :, :])  # pylint: disable=unsubscriptable-object
    real_part = np.concatenate(real_part, 0)
    imag_part = np.concatenate(imag_part, 0)

    magnitude = np.sqrt(real_part**2 + imag_part**2)
    phase = np.arctan2(imag_part.data, real_part.data)

    return magnitude, phase


if __name__ == "__main__":
    main()
