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

    def _compute_vggish_energy(self, log_mel):
        """Return per‐frame L2 norms of VGGish embeddings."""
        energies = []
        with torch.no_grad():
            for mel_chunk in log_mel:
                # Turn into a float Tensor
                if isinstance(mel_chunk, np.ndarray):
                    t = torch.from_numpy(mel_chunk).float()
                elif torch.is_tensor(mel_chunk):
                    t = mel_chunk.float()
                else:
                    raise TypeError(f"Unexpected chunk type: {type(mel_chunk)}")
                # Ensure shape [1,1,96,64]
                if t.dim() == 2:            # (96,64)
                    x = t.unsqueeze(0).unsqueeze(0)
                elif t.dim() == 3:          # (1,96,64)
                    x = t.unsqueeze(0)
                else:
                    raise ValueError(f"Unexpected mel_chunk dims: {t.shape}")
                if torch.cuda.is_available():
                    x = x.cuda()
                # Forward pass
                emb = self.model(x)
                # Compute norm on flattened embedding
                flat = emb.view(-1)        # e.g. [128] or [ ... ] whatever shape
                energy = torch.norm(flat).cpu().item()
                energies.append(energy)
        return np.array(energies)

    def detect(self,
               frame_s: float = 1.0,
               overlap: float = 0.5,
               rms_db_thresh: float = None,
               energy_sigma_mul: float = 1.5,
               flatness_thresh: float = 0.3,
               zcr_thresh: float = 0.3):
        """
        Detect background segments in the audio.
        
        Parameters
        ----------
        frame_s : float
            Frame length in seconds.
        overlap : float
            Fractional overlap between successive frames.
        rms_db_thresh : float, optional
            If provided, use this absolute dB cutoff on RMS instead of mean+σ.
        energy_sigma_mul : float
            Multiplier for RMS σ when using relative threshold.
        flatness_thresh : float
            Spectral flatness cutoff (0–1).
        zcr_thresh : float
            Zero-crossing rate cutoff (0–1).
        """

        # --- load + framing ---
        y, sr = librosa.load(self.wav_file, sr=None, mono=True)
        frame_len = int(frame_s * sr)
        hop_len   = int(frame_len * (1 - overlap))

        # --- extract features per frame ---
        rms      = librosa.feature.rms(y=y, frame_length=frame_len, hop_length=hop_len)[0]
        flatness = librosa.feature.spectral_flatness(y=y, n_fft=frame_len, hop_length=hop_len)[0]
        zcr      = librosa.feature.zero_crossing_rate(y, frame_length=frame_len, hop_length=hop_len)[0]

        # --- RMS-based flag ---
        if rms_db_thresh is not None:
            # absolute dB threshold
            rms_db   = 20 * np.log10(rms + 1e-9)
            rms_flag = (rms_db > rms_db_thresh).mean() > 0.5
        else:
            # legacy relative threshold
            mean_rms = rms.mean()
            std_rms  = rms.std()
            thresh   = mean_rms + energy_sigma_mul * std_rms
            rms_flag = (rms > thresh).mean() > 0.5

        # GGish embeddings over the whole file (in 0.96s hops)
        log_mel = vggish_input.wavfile_to_examples(self.wav_file)  # (N,96,64)
        vgg_energies = self._compute_vggish_energy(log_mel)

        # --- flatness & ZCR flags (unchanged) ---
        flatness_flag = (flatness > flatness_thresh).mean() > 0.3
        zcr_flag = (zcr > zcr_thresh).mean() > 0.3
        vgg_flag = (vgg_energies > vgg_thresh).mean() > 0.3

        # --- final decision & report ---
        status = any([rms_flag, flatness_flag, zcr_flag, vgg_flag])
        report = {
            'rms_flag': rms_flag,
            'flatness_flag': flatness_flag,
            'zcr_flag': zcr_flag,
            'vgg_flag': vgg_flag,
        }
        return status, report