#!/usr/bin/env python3
"""Test for _time_stretch_with_formant_preserve in render_yaml_chunks.
Creates a synthetic stereo WAV, runs the time-stretch, and reports durations.
"""
import tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
import math
import sys

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))
from tools.render_yaml_chunks import _time_stretch_with_formant_preserve


def make_stereo(path: Path, dur_s: float = 2.0, sr: int = 22050):
    t = np.linspace(0, dur_s, int(sr * dur_s), endpoint=False)
    a = 0.4 * np.sin(2 * np.pi * 440.0 * t)
    b = 0.4 * np.sin(2 * np.pi * 660.0 * t)
    stereo = np.stack([a, b], axis=1)
    sf.write(str(path), stereo, sr)


def duration_of(path: Path):
    data, sr = sf.read(str(path))
    return data.shape[0] / float(sr)


def run_test():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "stereo_test.wav"
        make_stereo(p, dur_s=2.0)
        orig_dur = duration_of(p)
        print("orig dur:", orig_dur)
        # slow down (factor <1 -> longer); our API uses factor: >1 speeds up, <1 slows down
        factor = 0.8
        _time_stretch_with_formant_preserve(p, factor)
        new_dur = duration_of(p)
        print(f"after factor {factor} -> dur {new_dur}")
        # expect approx orig/factor
        expected = orig_dur / factor
        print("expected approx:", expected)
        # revert by speeding up
        _time_stretch_with_formant_preserve(p, 1.25)
        re_dur = duration_of(p)
        print("after speed-up 1.25 -> dur", re_dur)


if __name__ == '__main__':
    run_test()
