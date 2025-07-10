import os
import torch
import numpy as np
import librosa
from torchvggish import vggish, vggish_input
from pyannote.audio import Pipeline

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
        with open(os.environ['HF_TOKEN_PATH']) as f:
            os.environ['HUGGINGFACE_TOKEN'] = f.read().strip()
        self.vad_pipeline = Pipeline.from_pretrained("pyannote/voice-activity-detection", use_auth_token=True)

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
        # … your existing RMS/flatness/ZCR code …

        # --- NEW: run Pyannote VAD on the file ---
        diarization = self.vad_pipeline(self.wav_file)
        # diarization.itertracks(yield_label=True) yields (segment, track_index, label)
        # but for VAD pipeline, it's just speech regions:
        speech_segments = [(seg.start, seg.end) for seg in diarization.get_timeline()]
        total_duration = librosa.get_duration(filename=self.wav_file)

        # compute total speech time
        speech_time = sum((end - start) for start, end in speech_segments)

        # non-speech = background
        non_speech_time = total_duration - speech_time
        vad_flag = non_speech_time > (0.5 * total_duration)
        # └─ True if more than half the recording is non-speech

        # --- combine all flags ---
        status = any([rms_flag, flatness_flag, zcr_flag, vad_flag])
        report = {
            'rms_flag': rms_flag,
            'flatness_flag': flatness_flag,
            'zcr_flag': zcr_flag,
            'vad_non_speech_ratio': non_speech_time/total_duration,
            'vad_flag': vad_flag,
        }
        return status, report