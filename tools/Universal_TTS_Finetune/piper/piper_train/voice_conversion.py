#!/usr/bin/env python3
import argparse
import logging
import time
from pathlib import Path

import librosa
import torch

from .vits.lightning import VitsModel
from .vits.mel_processing import spectrogram_torch
from .vits.wavfile import write as write_wav

_LOGGER = logging.getLogger("piper_train.voice_converstion")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", nargs="+", help="Audio file(s) to convert")
    parser.add_argument("--checkpoint", required=True, help="Path to model checkpoint")
    parser.add_argument(
        "--output-dir",
        help="Directory to write WAV file(s) (default: current directory)",
    )
    parser.add_argument(
        "--from-speaker", required=True, type=int, help="Speaker id number of source"
    )
    parser.add_argument(
        "--to-speaker", required=True, type=int, help="Speaker id number of target"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to the console"
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    _LOGGER.debug(args)

    # -------------------------------------------------------------------------

    args.checkpoint = Path(args.checkpoint)
    args.output_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    args.output_dir.parent.mkdir(parents=True, exist_ok=True)

    model = VitsModel.load_from_checkpoint(args.checkpoint, dataset=None)
    model_g = model.model_g

    # Inference only
    model_g.eval()

    with torch.no_grad():
        model_g.dec.remove_weight_norm()

    try:
        for audio_path_str in args.audio:
            audio_path = Path(audio_path_str)
            wav_path = args.output_dir / f"{audio_path.stem}.wav"

            audio, _sample_rate = librosa.load(path=audio_path_str, sr=22050)

            with torch.no_grad():
                # NOTE: audio is already in [-1, 1] coming from librosa
                audio_norm = torch.FloatTensor(audio).unsqueeze(0)
                spec = spectrogram_torch(
                    y=audio_norm,
                    n_fft=1024,
                    sampling_rate=22050,
                    hop_size=256,
                    win_size=1024,
                    center=False,
                ).squeeze(0)

                specs = spec.unsqueeze(0)
                spec_lengths = torch.LongTensor([specs.shape[2]])
                from_speaker = torch.LongTensor([args.from_speaker])
                to_speaker = torch.LongTensor([args.to_speaker])

                start_time = time.perf_counter()
                audio = (
                    model_g.voice_conversion(
                        specs, spec_lengths, from_speaker, to_speaker
                    )[0][0, 0]
                    .data.cpu()
                    .float()
                    .numpy()
                )
                end_time = time.perf_counter()

                _LOGGER.debug(
                    "Converted audio in %s second(s) (%s, shape=%s)",
                    end_time - start_time,
                    audio_path.stem,
                    list(audio.shape),
                )

                write_wav(str(wav_path), 22050, audio)

                _LOGGER.info("Wrote WAV to %s", wav_path)
    except KeyboardInterrupt:
        pass


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
