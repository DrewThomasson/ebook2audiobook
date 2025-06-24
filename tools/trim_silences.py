import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import sys


def trim_silence(audio_path, silence_thresh=-70, min_silence_len=1000):
    audio = AudioSegment.from_file(audio_path)
    nonsilent_ranges = detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    if not nonsilent_ranges:
        return None  # No nonsilent segment found

    start_trim = nonsilent_ranges[0][0]
    end_trim = nonsilent_ranges[-1][1]
    trimmed_audio = audio[start_trim:end_trim]
    return trimmed_audio


def process_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".wav"):
                wav_path = os.path.join(root, file)
                print(f"Trimming: {wav_path}")
                trimmed = trim_silence(wav_path)
                if trimmed:
                    trimmed.export(wav_path, format="wav")
                else:
                    print(f"Warning: only silence found in {wav_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <folder_path>")
        sys.exit(1)

    target_folder = sys.argv[1]
    process_folder(target_folder)
