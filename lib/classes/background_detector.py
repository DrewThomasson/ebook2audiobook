import os
import torch
import numpy as np
import librosa
from torchvggish import vggish, vggish_input

class BackgroundDetector:
    def __init__(self, wav_file: str, models_dir: str):
        self.wav_file   = wav_file
        self.models_dir = models_dir

        # configure torch cache
        torch_home = os.path.join(self.models_dir, 'hub')
        os.makedirs(torch_home, exist_ok=True)
        torch.hub.set_dir(torch_home)
        os.environ['TORCH_HOME'] = torch_home

        # load VGGish once
        self.model = vggish()
        self.model.eval()
        if torch.cuda.is_available():
            self.model.cuda()

    def _compute_vggish_energy(self, log_mel: np.ndarray) -> np.ndarray:
        """Return per‐frame L2 norms of VGGish embeddings."""
        energies = []
        with torch.no_grad():
            for mel_chunk in log_mel:
                # mel_chunk: (96, 64) → add batch+channel dims
                x = torch.from_numpy(mel_chunk).unsqueeze(0).unsqueeze(0).float()
                if torch.cuda.is_available():
                    x = x.cuda()
                emb = self.model(x)               # (1, 128)
                energies.append(torch.norm(emb, dim=1).cpu().item())
        return np.array(energies)

    def detect(self,
               frame_s: float                = 1.0,
               overlap: float                = 0.5,
               energy_sigma_mul: float       = 1.5,
               flatness_thresh: float        = 0.3,
               zcr_thresh: float             = 0.1
              ) -> (bool, str):
        """
        Returns (status, message) where status is True if background music/noise
        is detected.
        """

        # 1) Load raw audio (mono @16kHz) for spectral features
        y, sr = librosa.load(self.wav_file, sr=16000, mono=True)

        # frame params
        frame_len = int(frame_s * sr)
        hop_len   = int(frame_len * (1 - overlap))

        # 2) Compute spectral features per frame
        rms      = librosa.feature.rms(
                       y=y,
                       frame_length=frame_len,
                       hop_length=hop_len
                   )[0]

        # ← patched here ↓
        flatness = librosa.feature.spectral_flatness(
                       y=y,
                       n_fft=frame_len,
                       hop_length=hop_len
                   )[0]

        zcr      = librosa.feature.zero_crossing_rate(
                       y,
                       frame_length=frame_len,
                       hop_length=hop_len
                   )[0]

        # frame‐level decisions
        rms_mean, rms_std = rms.mean(), rms.std()
        energy_thresh     = rms_mean + energy_sigma_mul * rms_std

        rms_flag      = (rms > energy_thresh).mean() > 0.5
        flatness_flag = (flatness > flatness_thresh).mean() > 0.3
        zcr_flag      = (zcr > zcr_thresh).mean() > 0.3

        # 3) VGGish embeddings over the whole file (in 0.96s hops)
        log_mel = vggish_input.wavfile_to_examples(self.wav_file)  # (N,96,64)
        vgg_energies = self._compute_vggish_energy(log_mel)
        vgg_mean     = vgg_energies.mean()
        vgg_std      = vgg_energies.std()
        vgg_thresh   = vgg_mean + energy_sigma_mul * vgg_std
        vgg_flag     = (vgg_energies > vgg_thresh).mean() > 0.3

        # 4) Final decision: any indicator tripped → background detected
        status = any([rms_flag, flatness_flag, zcr_flag, vgg_flag])

        # 5) Build report
        msg = []
        msg.append(f"RMS mean/std:      {rms_mean:.1f} / {rms_std:.1f}  (>{energy_sigma_mul}σ → {energy_thresh:.1f})")
        msg.append(f"Flatness > {flatness_thresh}: {flatness_flag!s}")
        msg.append(f"ZCR > {zcr_thresh}:           {zcr_flag!s}")
        msg.append(f"VGGish mean/std:    {vgg_mean:.1f} / {vgg_std:.1f}  (thresh {vgg_thresh:.1f})")
        msg.append(f"VGGish flag:        {vgg_flag!s}")

        msg.append("\n▶ Background detected; proceeding with separation." 
                   if status 
                   else "\n✔ No significant background; skipping separation.")

        return status, "\n".join(msg)