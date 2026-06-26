#!/usr/bin/env python3

import argparse
import json
import logging
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import onnxruntime

from .vits.utils import audio_float_to_int16

_LOGGER = logging.getLogger("piper_train.infer_onnx")


class SpeechStreamer:
    """
    Stream speech in real time.

    Args:
        encoder_path: path to encoder ONNX model
        decoder_path: path to decoder ONNX model
        sample_rate: output sample rate
        chunk_size: number of mel frames to decode in each steps (time in secs = chunk_size * 256)
        chunk_padding: number of mel frames to be concatinated to the start and end of the current chunk to reduce decoding artifacts
    """

    def __init__(
        self,
        encoder_path,
        decoder_path,
        sample_rate,
        chunk_size=45,
        chunk_padding=10,
    ):
        sess_options = onnxruntime.SessionOptions()
        _LOGGER.debug("Loading encoder model from %s", encoder_path)
        self.encoder = onnxruntime.InferenceSession(
            encoder_path, sess_options=sess_options
        )
        _LOGGER.debug("Loading decoder model from %s", decoder_path)
        self.decoder = onnxruntime.InferenceSession(
            decoder_path, sess_options=sess_options
        )

        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.chunk_padding = chunk_padding

    def encoder_infer(self, enc_input):
        ENC_START = time.perf_counter()
        enc_output = self.encoder.run(None, enc_input)
        ENC_INFER = time.perf_counter() - ENC_START
        _LOGGER.debug(f"Encoder inference {round(ENC_INFER * 1000)}")
        wav_length = enc_output[0].shape[2] * 256
        enc_rtf = round(ENC_INFER / (wav_length / self.sample_rate), 2)
        _LOGGER.debug(f"Encoder RTF {enc_rtf}")
        return enc_output

    def decoder_infer(self, z, y_mask, g=None):
        dec_input = {"z": z, "y_mask": y_mask}
        if g:
            dec_input["g"] = g
        DEC_START = time.perf_counter()
        audio = self.decoder.run(None, dec_input)[0].squeeze()
        DEC_INFER = time.perf_counter() - DEC_START
        _LOGGER.debug(f"Decoder inference {round(DEC_INFER * 1000)}")
        dec_rtf = round(DEC_INFER / (len(audio) / self.sample_rate), 2)
        _LOGGER.debug(f"Decoder RTF {dec_rtf}")
        return audio

    def chunk(self, enc_output):
        z, y_mask, *dec_args = enc_output
        n_frames = z.shape[2]
        if n_frames <= (self.chunk_size + (2 * self.chunk_padding)):
            # Too short to stream
            return self.decoder_infer(z, y_mask, *dec_args)
        split_at = [
            i * self.chunk_size for i in range(1, math.ceil(n_frames / self.chunk_size))
        ]
        chunks = list(
            zip(
                np.split(z, split_at, axis=2),
                np.split(y_mask, split_at, axis=2),
            )
        )
        wav_start_pad = wav_end_pad = None
        for idx, (z_chunk, y_mask_chunk) in enumerate(chunks):
            if idx > 0:
                prev_z, prev_y_mask = chunks[idx - 1]
                start_zpad = prev_z[:, :, -self.chunk_padding :]
                start_ypad = prev_y_mask[:, :, -self.chunk_padding :]
                z_chunk = np.concatenate([start_zpad, z_chunk], axis=2)
                y_mask_chunk = np.concatenate([start_ypad, y_mask_chunk], axis=2)
                wav_start_pad = start_zpad.shape[2] * 256
            if (idx + 1) < len(chunks):
                next_z, next_y_mask = chunks[idx + 1]
                end_zpad = next_z[:, :, : self.chunk_padding]
                end_ypad = next_y_mask[:, :, : self.chunk_padding]
                z_chunk = np.concatenate([z_chunk, end_zpad], axis=2)
                y_mask_chunk = np.concatenate([y_mask_chunk, end_ypad], axis=2)
                wav_end_pad = end_zpad.shape[2] * 256
            audio = self.decoder_infer(z_chunk, y_mask_chunk, *dec_args)
            yield audio[wav_start_pad:-wav_end_pad]

    def stream(self, encoder_input):
        start_time = time.perf_counter()
        has_shown_latency = False
        _LOGGER.debug("Starting synthesis")
        enc_output = self.encoder_infer(encoder_input)
        for wav in self.chunk(enc_output):
            if len(wav) == 0:
                continue
            if not has_shown_latency:
                LATENCY = round((time.perf_counter() - start_time) * 1000)
                _LOGGER.debug(f"Latency {LATENCY}")
                has_shown_latency = True
            audio = audio_float_to_int16(wav)
            yield audio.tobytes()
        _LOGGER.debug("Synthesis done!")


def main():
    """Main entry point"""
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(prog="piper_train.infer_onnx_streaming")
    parser.add_argument(
        "--encoder", required=True, help="Path to encoder model (.onnx)"
    )
    parser.add_argument(
        "--decoder", required=True, help="Path to decoder  model (.onnx)"
    )
    parser.add_argument("--sample-rate", type=int, default=22050)
    parser.add_argument("--noise-scale", type=float, default=0.667)
    parser.add_argument("--noise-scale-w", type=float, default=0.8)
    parser.add_argument("--length-scale", type=float, default=1.0)
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=45,
        help="Number of mel frames to decode at each step"
    )
    parser.add_argument(
        "--chunk-padding",
        type=int,
        default=5,
        help="Number of mel frames to add to the start and end of the current chunk to reduce decoding artifacts"
    )

    args = parser.parse_args()

    streamer = SpeechStreamer(
        encoder_path=os.fspath(args.encoder),
        decoder_path=os.fspath(args.decoder),
        sample_rate=args.sample_rate,
        chunk_size=args.chunk_size,
        chunk_padding=args.chunk_padding,
    )

    output_buffer = sys.stdout.buffer

    for i, line in enumerate(sys.stdin):
        line = line.strip()
        if not line:
            continue

        utt = json.loads(line)
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

        stream = streamer.stream(
            {
                "input": text,
                "input_lengths": text_lengths,
                "scales": scales,
                "sid": sid,
            }
        )
        for wav_chunk in stream:
            output_buffer.write(wav_chunk)
            output_buffer.flush()


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
