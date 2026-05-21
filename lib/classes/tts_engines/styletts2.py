import os
import sys
import subprocess
from unittest.mock import MagicMock
import numpy as np
import torch

# 1. Dynamic check & install of requirements
try:
    import munch
    import einops
    import einops_exts
    import nltk
except ImportError:
    print("StyleTTS2 dependencies missing. Installing from requirements2.txt...")
    req_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "requirements2.txt"))
    if os.path.exists(req_path):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
    else:
        # Fallback if requirements2.txt is not found
        subprocess.check_call([sys.executable, "-m", "pip", "install", "munch", "einops", "einops-exts", "nltk"])
    import munch
    import einops
    import einops_exts
    import nltk

# 2. Setup NLTK punkt tokenizers
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

# 3. Mock monotonic_align before importing StyleTTS2 modules to prevent C compilation errors
sys.modules['monotonic_align'] = MagicMock()
sys.modules['monotonic_align.core'] = MagicMock()

# 4. Add StyleTTS2 directory to sys.path
style_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "styletts2_src"))
if style_path not in sys.path:
    sys.path.insert(0, style_path)

from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

class StyleTTS2(TTSUtils, TTSRegistry, name='styletts2'):

    def __init__(self, session: DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.speaker = None
            self.tts_key = self.session['model_cache']
            self.pth_voice_file = None
            self.resampler_cache = {}
            self.resampled_wav_cache = {}
            self.audio_segments = []
            self.style_cache = {}
            
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {}
            
            fine_tuned = self.session.get('fine_tuned')
            if fine_tuned not in self.models:
                error = f'Invalid fine_tuned model {fine_tuned}. Available models: {list(self.models.keys())}'
                raise ValueError(error)
                
            model_cfg = self.models[fine_tuned]
            for required_key in ('repo', 'samplerate'):
                if required_key not in model_cfg:
                    error = f'fine_tuned model {fine_tuned} is missing required key {required_key}.'
                    raise ValueError(error)
                    
            self.params['samplerate'] = model_cfg['samplerate']
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 0
            self.amp_dtype = self._apply_gpu_policy(enough_vram=enough_vram, seed=seed)
            self.device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']] else self.session['device']
            
            # Setup MelSpectrogram transform
            import torchaudio
            self.to_mel = torchaudio.transforms.MelSpectrogram(
                n_mels=80, n_fft=2048, win_length=1200, hop_length=300
            )
            
            self.engine = self.load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self) -> Any:
        msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient…"
        print(msg)
        self.cleanup_memory()
        
        engine = loaded_tts.get(self.tts_key)
        if engine:
            msg = f"TTS {self.tts_key} already loaded"
            print(msg)
            return engine
            
        try:
            from huggingface_hub import hf_hub_download
            import yaml
            import torch
            from munch import Munch
            import phonemizer
            
            # Import StyleTTS2 components
            from models import build_model, load_ASR_models, load_F0_models
            from utils import recursive_munch
            from text_utils import TextCleaner
            from Utils.PLBERT.util import load_plbert
            from Modules.diffusion.sampler import DiffusionSampler, ADPM2Sampler, KarrasSchedule
            
            model_cfg = self.models[self.session['fine_tuned']]
            hf_repo = model_cfg['repo']
            
            config_filename = model_cfg['files'][0]
            checkpoint_filename = model_cfg['files'][1]
            
            print(f"Downloading StyleTTS2 config from {hf_repo}...")
            config_path = hf_hub_download(repo_id=hf_repo, filename=config_filename, cache_dir=self.cache_dir)
            print(f"Downloading StyleTTS2 checkpoint from {hf_repo}...")
            checkpoint_path = hf_hub_download(repo_id=hf_repo, filename=checkpoint_filename, cache_dir=self.cache_dir)
            
            # Load YAML configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # Make auxiliary component paths absolute pointing to the persistent models directory
            import urllib.request
            
            def download_file(url, dest_path):
                # Ensure parent directory exists
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                # Check if it needs download (doesn't exist or is LFS pointer under 1024 bytes)
                if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1024:
                    return
                print(f"Downloading auxiliary model {os.path.basename(dest_path)} from {url}...")
                temp_dest = dest_path + ".tmp"
                try:
                    # Download to temp file
                    with urllib.request.urlopen(url) as response, open(temp_dest, 'wb') as out_file:
                        shutil.copyfileobj(response, out_file)
                    os.replace(temp_dest, dest_path)
                    print(f"Successfully downloaded {os.path.basename(dest_path)}")
                except Exception as e:
                    if os.path.exists(temp_dest):
                        os.remove(temp_dest)
                    raise RuntimeError(f"Failed to download {url}: {e}")

            # Define persistent directory under models/
            styletts2_models_dir = os.path.join(self.cache_dir, "styletts2")
            
            # Setup paths for ASR, JDC (F0), and PLBERT
            asr_models_dir = os.path.join(styletts2_models_dir, "Utils", "ASR")
            asr_config_dest = os.path.join(asr_models_dir, "config.yml")
            asr_path_dest = os.path.join(asr_models_dir, "epoch_00080.pth")
            
            # Copy config file from cloned repository source
            asr_config_src = os.path.join(style_path, "Utils", "ASR", "config.yml")
            if os.path.exists(asr_config_src) and not os.path.exists(asr_config_dest):
                os.makedirs(os.path.dirname(asr_config_dest), exist_ok=True)
                shutil.copy2(asr_config_src, asr_config_dest)
                
            # Download ASR weights
            download_file(
                "https://raw.githubusercontent.com/yl4579/StyleTTS2/main/Utils/ASR/epoch_00080.pth",
                asr_path_dest
            )
            
            jdc_models_dir = os.path.join(styletts2_models_dir, "Utils", "JDC")
            jdc_path_dest = os.path.join(jdc_models_dir, "bst.t7")
            
            # Download JDC weights
            download_file(
                "https://raw.githubusercontent.com/yl4579/StyleTTS2/main/Utils/JDC/bst.t7",
                jdc_path_dest
            )
            
            plbert_models_dir = os.path.join(styletts2_models_dir, "Utils", "PLBERT")
            plbert_config_dest = os.path.join(plbert_models_dir, "config.yml")
            plbert_path_dest = os.path.join(plbert_models_dir, "step_1000000.t7")
            
            # Copy PLBERT config from cloned repository source
            plbert_config_src = os.path.join(style_path, "Utils", "PLBERT", "config.yml")
            if os.path.exists(plbert_config_src) and not os.path.exists(plbert_config_dest):
                os.makedirs(os.path.dirname(plbert_config_dest), exist_ok=True)
                shutil.copy2(plbert_config_src, plbert_config_dest)
                
            # Download PLBERT weights
            download_file(
                "https://raw.githubusercontent.com/yl4579/StyleTTS2/main/Utils/PLBERT/step_1000000.t7",
                plbert_path_dest
            )
            
            # Update configuration with actual downloaded model paths
            config['ASR_config'] = asr_config_dest
            config['ASR_path'] = asr_path_dest
            config['F0_path'] = jdc_path_dest
            config['PLBERT_dir'] = plbert_models_dir
                
            # Load submodules
            print("Loading ASR model...")
            text_aligner = load_ASR_models(config['ASR_path'], config['ASR_config'])
            print("Loading F0 pitch extractor...")
            pitch_extractor = load_F0_models(config['F0_path'])
            print("Loading PL-BERT...")
            plbert = load_plbert(config['PLBERT_dir'])
            
            # Build main model
            model_params = recursive_munch(config['model_params'])
            model = build_model(model_params, text_aligner, pitch_extractor, plbert)
            
            # Load checkpoint weights
            print(f"Loading checkpoint weights from {checkpoint_path}...")
            params_whole = torch.load(checkpoint_path, map_location='cpu')
            params = params_whole['net']
            
            for key in model:
                if key in params:
                    try:
                        model[key].load_state_dict(params[key])
                    except Exception:
                        from collections import OrderedDict
                        state_dict = params[key]
                        new_state_dict = OrderedDict()
                        for k, v in state_dict.items():
                            name = k[7:] # remove `module.`
                            new_state_dict[name] = v
                        model[key].load_state_dict(new_state_dict, strict=False)
                        
            # Move model components to device & evaluation mode
            _ = [model[key].eval() for key in model]
            _ = [model[key].to(self.device) for key in model]
            
            # Setup diffusion sampler
            sampler = DiffusionSampler(
                model.diffusion.diffusion,
                sampler=ADPM2Sampler(),
                sigma_schedule=KarrasSchedule(sigma_min=0.0001, sigma_max=3.0, rho=9.0),
                clamp=False
            )
            
            # Setup tokenizer & EspeakBackend phonemizer
            from phonemizer.backend.espeak.wrapper import EspeakWrapper
            for lib_path in [
                '/opt/homebrew/lib/libespeak-ng.dylib',
                '/opt/homebrew/lib/libespeak.dylib',
                '/usr/local/lib/libespeak-ng.dylib',
                '/usr/local/lib/libespeak.dylib',
            ]:
                if os.path.exists(lib_path):
                    EspeakWrapper.set_library(lib_path)
                    break

            textcleaner = TextCleaner()
            global_phonemizer = phonemizer.backend.EspeakBackend(
                language='en-us', preserve_punctuation=True, with_stress=True
            )
            
            engine = {
                "model": model,
                "model_params": model_params,
                "sampler": sampler,
                "textcleaner": textcleaner,
                "phonemizer": global_phonemizer
            }
            
            loaded_tts[self.tts_key] = engine
            print(f"TTS {self.tts_key} Loaded Successfully!")
            return engine
            
        except Exception as e:
            error = f"load_engine() failure: {e}"
            raise RuntimeError(error) from e

    def preprocess(self, wave: np.ndarray) -> torch.Tensor:
        wave_tensor = torch.from_numpy(wave).float()
        mel_tensor = self.to_mel(wave_tensor)
        mel_tensor = (torch.log(1e-5 + mel_tensor.unsqueeze(0)) - -4) / 4
        return mel_tensor

    def get_style_embedding(self, voice_path: str) -> torch.Tensor:
        if voice_path not in self.style_cache:
            import librosa
            import torch
            
            wave, sr = librosa.load(voice_path, sr=24000)
            audio, index = librosa.effects.trim(wave, top_db=30)
            if sr != 24000:
                audio = librosa.resample(y=audio, orig_sr=sr, target_sr=24000)
                
            mel_tensor = self.preprocess(audio).to(self.device)
            model = self.engine['model']
            
            with torch.no_grad():
                ref_s = model.style_encoder(mel_tensor.unsqueeze(1))
                ref_p = model.predictor_encoder(mel_tensor.unsqueeze(1))
                
            self.style_cache[voice_path] = torch.cat([ref_s, ref_p], dim=1)
            
        return self.style_cache[voice_path]

    def convert(self, sentence_file: str, sentence: str, **kwargs) -> tuple:
        try:
            import torch
            import torchaudio
            import numpy as np
            from nltk.tokenize import word_tokenize
            from lib.classes.tts_engines.common.audio import trim_audio, is_audio_data_valid
            from utils import length_to_mask
            
            if self.engine:
                sentence_parts = self._split_sentence_on_sml(sentence)
                not_supported_punc_pattern = re.compile(r'[—]')
                
                self.params['block_voice'] = kwargs.get('block_voice', self.session['voice'])
                if self.params.get('inline_voice'):
                    self.params['current_voice'] = self.params['inline_voice']
                else:
                    self.params['current_voice'], error = self._set_voice(self.params['block_voice'])
                    if self.params['current_voice'] is None and error is not None:
                        return False, error
                    if self.session['voice'] == self.params['block_voice']:
                        self.session['voice'] = self.params['current_voice']
                    self.params['block_voice'] = self.params['current_voice']
                    
                self.audio_segments = []
                
                # Fetch parameters or use high-quality defaults
                alpha = kwargs.get('alpha', 0.3)
                beta = kwargs.get('beta', 0.7)
                diffusion_steps = kwargs.get('diffusion_steps', 5)
                embedding_scale = kwargs.get('embedding_scale', 1)
                
                model = self.engine['model']
                sampler = self.engine['sampler']
                textcleaner = self.engine['textcleaner']
                phonemizer_backend = self.engine['phonemizer']
                model_params = self.engine['model_params']
                
                for part in sentence_parts:
                    part = part.strip()
                    if not part:
                        continue
                    if SML_TAG_PATTERN.fullmatch(part):
                        success, error = self._convert_sml(part)
                        if not success:
                            return False, error
                        continue
                    if not any(c.isalnum() for c in part):
                        continue
                        
                    # Standard punctuation normalization
                    part = re.sub(not_supported_punc_pattern, ' ', part).strip()
                    
                    # Phonemize & tokenize text
                    ps = phonemizer_backend.phonemize([part])
                    ps = word_tokenize(ps[0])
                    ps = ' '.join(ps)
                    
                    tokens = textcleaner(ps)
                    tokens.insert(0, 0)
                    tokens = torch.LongTensor(tokens).to(self.device).unsqueeze(0)
                    
                    with torch.no_grad():
                        input_lengths = torch.LongTensor([tokens.shape[-1]]).to(self.device)
                        text_mask = length_to_mask(input_lengths).to(self.device)
                        
                        t_en = model.text_encoder(tokens, input_lengths, text_mask)
                        bert_dur = model.bert(tokens, attention_mask=(~text_mask).int())
                        d_en = model.bert_encoder(bert_dur).transpose(-1, -2)
                        
                        noise = torch.randn((1, 256)).unsqueeze(1).to(self.device)
                        
                        if self.session['fine_tuned'] == 'ljspeech':
                            # Single-speaker model (no speaker conditioning)
                            s_pred = sampler(
                                noise=noise,
                                embedding=bert_dur,
                                num_steps=diffusion_steps,
                                embedding_scale=embedding_scale
                            ).squeeze(1)
                            s = s_pred[:, 128:]
                            ref = s_pred[:, :128]
                        else:
                            # Multi-speaker / speaker adaptation model (requires reference voice)
                            ref_s = self.get_style_embedding(self.params['current_voice'])
                            s_pred = sampler(
                                noise=noise,
                                embedding=bert_dur,
                                embedding_scale=embedding_scale,
                                features=ref_s,
                                num_steps=diffusion_steps
                            ).squeeze(1)
                            
                            s = s_pred[:, 128:]
                            ref = s_pred[:, :128]
                            
                            ref = alpha * ref + (1 - alpha) * ref_s[:, :128]
                            s = beta * s + (1 - beta) * ref_s[:, 128:]
                            
                        # Prosody predictor
                        d = model.predictor.text_encoder(d_en, s, input_lengths, text_mask)
                        x, _ = model.predictor.lstm(d)
                        duration = model.predictor.duration_proj(x)
                        duration = torch.sigmoid(duration).sum(axis=-1)
                        
                        pred_dur = torch.round(duration.squeeze()).clamp(min=1)
                        if pred_dur.ndim == 0:
                            pred_dur = pred_dur.unsqueeze(0)
                            
                        if self.session['fine_tuned'] == 'ljspeech':
                            pred_dur[-1] += 5
                            
                        # Build alignment target
                        pred_aln_trg = torch.zeros(int(input_lengths.item()), int(pred_dur.sum().item())).to(self.device)
                        c_frame = 0
                        for i in range(pred_aln_trg.size(0)):
                            pred_aln_trg[i, c_frame:c_frame + int(pred_dur[i].item())] = 1
                            c_frame += int(pred_dur[i].item())
                            
                        en = (d.transpose(-1, -2) @ pred_aln_trg.unsqueeze(0))
                        if model_params.decoder.type == "hifigan":
                            asr_new = torch.zeros_like(en)
                            asr_new[:, :, 0] = en[:, :, 0]
                            asr_new[:, :, 1:] = en[:, :, 0:-1]
                            en = asr_new
                            
                        F0_pred, N_pred = model.predictor.F0Ntrain(en, s)
                        
                        asr = (t_en @ pred_aln_trg.unsqueeze(0))
                        if model_params.decoder.type == "hifigan":
                            asr_new = torch.zeros_like(asr)
                            asr_new[:, :, 0] = asr[:, :, 0]
                            asr_new[:, :, 1:] = asr[:, :, 0:-1]
                            asr = asr_new
                            
                        out = model.decoder(asr, F0_pred, N_pred, ref.squeeze().unsqueeze(0))
                        
                        # weird pulse at the end of the model, trim it
                        audio_part = out.squeeze().cpu()
                        if self.session['fine_tuned'] == 'ljspeech':
                            # no trimming required or trim differently
                            pass
                        else:
                            audio_part = audio_part[..., :-50]
                            
                    if is_audio_data_valid(audio_part):
                        src_tensor = self._tensor_type(audio_part)
                        part_tensor = src_tensor.clone().detach().unsqueeze(0).cpu()
                        if part_tensor is not None and part_tensor.numel() > 0:
                            self.audio_segments.append(part_tensor)
                            del part_tensor
                        else:
                            error = 'part_tensor not valid'
                            return False, error
                    else:
                        error = 'audio_part not valid'
                        return False, error
                        
                if self.audio_segments:
                    segment_tensor = torch.cat(self.audio_segments, dim=-1)
                    if not self.audio_save(sentence_file, segment_tensor, self.params['samplerate']):
                        error = f'audio_save() error: cannot save {sentence_file}'
                        return False, error
                    del segment_tensor
                    self.cleanup_memory()
                    self.audio_segments = []
                    if not os.path.exists(sentence_file):
                        error = f'Cannot create {sentence_file}'
                        return False, error
                return True, None
            else:
                error = f"TTS engine {self.session['tts_engine']} failed to load!"
                return False, error
        except Exception as e:
            self.cleanup_memory()
            return False, self.log_exception(f'{self.__class__.__name__}.convert()', e)

    def create_vtt(self, all_sentences: list) -> bool:
        if self._build_vtt_file(all_sentences):
            return True
        return False
