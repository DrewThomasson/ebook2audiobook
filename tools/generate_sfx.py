#!/usr/bin/env python3
import os
import wave
import math
import struct


def make_sine(path: str, duration: float = 0.8, freq: float = 440.0, vol: float = 0.5, sr: int = 22050):
    n = int(sr * duration)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        frames = bytearray()
        for i in range(n):
            t = i / sr
            v = int(max(-32767, min(32767, vol * 32767.0 * math.sin(2 * math.pi * freq * t))))
            frames += struct.pack("<h", v)
        wf.writeframes(frames)


if __name__ == "__main__":
    os.makedirs("run/sfx", exist_ok=True)
    print("Generating SFX in run/sfx/")
    make_sine("run/sfx/trailer_intro.wav", duration=0.9, freq=440.0, vol=0.6)
    make_sine("run/sfx/bed_loop.wav", duration=4.0, freq=220.0, vol=0.25)
    make_sine("run/sfx/outro_hit.wav", duration=0.35, freq=880.0, vol=0.8)
    print("Done")
