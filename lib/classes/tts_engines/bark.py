import threading, torch, torchaudio, random, gc, shutil, subprocess, tempfile, uuid, types

import regex as re
import numpy as np
import soundfile as sf

from multiprocessing.managers import DictProxy
from typing import Any
from pathlib import Path
from huggingface_hub import hf_hub_download

from lib.classes.tts_registry import TTSRegistry
from lib.classes.vram_detector import VRAMDetector
from lib.classes.tts_engines.common.utils import cleanup_memory, append_sentence2vtt, loaded_tts_size_gb, load_xtts_builtin_list #, ensure_safe_checkpoint
from lib.classes.tts_engines.common.audio_filters import detect_gender, trim_audio, normalize_audio, is_audio_data_valid
from lib import *

#import logging
#logging.basicConfig(level=logging.DEBUG)

lock = threading.Lock()

class Bark(TTSRegistry, name='bark'):
    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.tts_key = self.session['model_cache']
            self.engine = None
            self.tts_zs_key = default_vc_model.rsplit('/',1)[-1]
            self.engine_zs = None
            self.pth_voice_file = None
            self.sentences_total_time = 0.0
            self.sentence_idx = 1
            self.params = {}
            self.params['samplerate'] = models[self.session['tts_engine']][self.session['fine_tuned']]['samplerate']
            self.vtt_path = os.path.join(self.session['process_dir'],Path(self.session['final_name']).stem+'.vtt')
            self.resampler_cache = {}
            self.audio_segments = []
            using_gpu = self.session['device'] != devices['CPU']['proc']
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 123456
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            has_cuda = (torch.version.cuda is not None and torch.cuda.is_available())
            if has_cuda:
                if using_gpu and enough_vram:
                    """
                    if devices['JETSON']['found']:
                        if not hasattr(torch, "distributed"):
                            torch.distributed = types.SimpleNamespace()
                        if not hasattr(torch.distributed, "ReduceOp"):
                            class _ReduceOp:
                                SUM = None
                                MAX = None
                                MIN = None
                            torch.distributed.ReduceOp = _ReduceOp
                        if not hasattr(torch.distributed, "all_reduce"):
                            def _all_reduce(*args, **kwargs):
                                return
                            torch.distributed.all_reduce = _all_reduce
                    """
                    torch.cuda.set_per_process_memory_fraction(0.95)
                    torch.backends.cudnn.enabled = True
                    torch.backends.cudnn.benchmark = True
                    torch.backends.cudnn.deterministic = True
                    torch.backends.cudnn.allow_tf32 = True
                    torch.backends.cuda.matmul.allow_tf32 = True
                    torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction = True
                    torch.cuda.manual_seed_all(seed)
                else:
                    torch.cuda.set_per_process_memory_fraction(0.7)
                    torch.backends.cudnn.enabled = True
                    torch.backends.cudnn.benchmark = False
                    torch.backends.cudnn.deterministic = True
                    torch.backends.cudnn.allow_tf32 = False
                    torch.backends.cuda.matmul.allow_tf32 = False
                    torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction = False
                    torch.cuda.manual_seed_all(seed)
            self.xtts_speakers = load_xtts_builtin_list()
            self._load_engine()
            self._load_engine_zs()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def _load_api(self, key:str, model_path:str)->Any:
        global lock
        try:
            with lock:
                from TTS.api import TTS as TTSEngine
                engine = loaded_tts.get(key, False)
                if not engine:
                    engine = TTSEngine(model_path)
                if engine:
                    vram_dict = VRAMDetector().detect_vram(self.session['device'])
                    self.session['free_vram_gb'] = vram_dict.get('free_vram_gb', 0)
                    models_loaded_size_gb = loaded_tts_size_gb(loaded_tts)
                    if self.session['free_vram_gb'] > models_loaded_size_gb:
                        loaded_tts[key] = engine
                return engine
        except Exception as e:
            error = f"_load_api() error: {e}"
            print(error)
            return None

    def _load_checkpoint(self,**kwargs:Any)->Any:
        global lock
        try:
            with lock:
                key = kwargs.get('key')
                engine = loaded_tts.get(key, False)
                if not engine:
                    engine_name = kwargs.get('tts_engine', None)
                    if engine_name == TTS_ENGINES['XTTSv2']:
                        from TTS.tts.configs.xtts_config import XttsConfig
                        from TTS.tts.models.xtts import Xtts
                        checkpoint_path = kwargs.get('checkpoint_path')
                        config_path = kwargs.get('config_path',None)
                        vocab_path = kwargs.get('vocab_path',None)
                        if not checkpoint_path or not os.path.exists(checkpoint_path):
                            error = f'Missing or invalid checkpoint_path: {checkpoint_path}'
                            raise FileNotFoundError(error)
                            return False
                        if not config_path or not os.path.exists(config_path):
                            error = f'Missing or invalid config_path: {config_path}'
                            raise FileNotFoundError(error)
                            return False
                        config = XttsConfig()
                        config.models_dir = os.path.join("models","tts")
                        config.load_json(config_path)
                        engine = Xtts.init_from_config(config)
                        engine.load_checkpoint(
                            config,
                            checkpoint_path = checkpoint_path,
                            vocab_path = vocab_path,
                            eval = True
                        )
                    elif engine_name == TTS_ENGINES['BARK']:
                        from TTS.tts.configs.bark_config import BarkConfig
                        from TTS.tts.models.bark import Bark
                        checkpoint_dir = kwargs.get('checkpoint_dir')
                        if not checkpoint_dir or not os.path.exists(checkpoint_dir):
                            error = f'Missing or invalid checkpoint_dir: {checkpoint_dir}'
                            raise FileNotFoundError(error)
                            return False
                        #check_pth = ensure_safe_checkpoint(checkpoint_dir)
                        #if not check_pth:
                        #    error = f'No valid checkpoint files found or conversion failed in: {checkpoint_dir}'
                        #    raise RuntimeError(error)
                        #    return False
                        config = BarkConfig()
                        config.CACHE_DIR = self.cache_dir
                        config.USE_SMALLER_MODELS = True if os.environ['SUNO_USE_SMALL_MODELS'] == 'True' else False
                        engine = Bark.init_from_config(config)
                        engine.load_checkpoint(
                            config,
                            checkpoint_dir = checkpoint_dir,
                            eval = True
                        )  
                if engine:
                    vram_dict = VRAMDetector().detect_vram(self.session['device'])
                    self.session['free_vram_gb'] = vram_dict.get('free_vram_gb', 0)
                    models_loaded_size_gb = loaded_tts_size_gb(loaded_tts)
                    if self.session['free_vram_gb'] > models_loaded_size_gb:
                        loaded_tts[key] = engine
                return engine
        except Exception as e:
            error = f'_load_checkpoint() error: {e}'
            print(error)
            return None

    def _load_engine(self)->None:
        try:
            msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient..."
            print(msg)
            cleanup_memory()
            self.engine = loaded_tts.get(self.tts_key, False)
            if not self.engine:
                if self.session['custom_model'] is not None:
                    msg = f"{self.session['tts_engine']} custom model not implemented yet!"
                    print(msg)
                else:
                    hf_repo = models[self.session['tts_engine']][self.session['fine_tuned']]['repo']
                    hf_sub = models[self.session['tts_engine']][self.session['fine_tuned']]['sub']
                    text_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][0]}", cache_dir=self.cache_dir)
                    coarse_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][1]}", cache_dir=self.cache_dir)
                    fine_model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[self.session['tts_engine']][self.session['fine_tuned']]['files'][2]}", cache_dir=self.cache_dir)
                    checkpoint_dir = os.path.dirname(text_model_path)
                    self.engine = self._load_checkpoint(tts_engine=self.session['tts_engine'], key=self.tts_key, checkpoint_dir=checkpoint_dir)
            if self.engine:
                msg = f'TTS {key} Loaded!'
        except Exception as e:
            error = f'_load_engine() error: {e}'

    def _load_engine_zs(self)->Any:
        try:
            msg = f"Loading ZeroShot {self.tts_zs_key} model, it takes a while, please be patient..."
            print(msg)
            cleanup_memory()
            self.engine_zs = loaded_tts.get(self.tts_zs_key, False)
            if not self.engine_zs:
                self.engine_zs = self._load_api(self.tts_zs_key, default_vc_model)
            if self.engine_zs:
                self.session['model_zs_cache'] = self.tts_zs_key
                msg = f'ZeroShot {key} Loaded!'
        except Exception as e:
            error = f'_load_engine_zs() error: {e}'

    def _check_xtts_builtin_speakers(self, voice_path:str, speaker:str)->str|bool:
        try:
            voice_parts = Path(voice_path).parts
            if (self.session['language'] in voice_parts or speaker in default_engine_settings[TTS_ENGINES['BARK']]['voices'] or self.session['language'] == 'eng'):
                return voice_path
            if self.session['language'] in language_tts[TTS_ENGINES['XTTSv2']].keys():
                default_text_file = os.path.join(voices_dir, self.session['language'], 'default.txt')
                if os.path.exists(default_text_file):
                    msg = f"Converting builtin eng voice to {self.session['language']}..."
                    print(msg)
                    key = f"{TTS_ENGINES['XTTSv2']}-internal"
                    default_text = Path(default_text_file).read_text(encoding="utf-8")
                    cleanup_memory()
                    engine = loaded_tts.get(key, False)
                    if not engine:
                        vram_dict = VRAMDetector().detect_vram(self.session['device'])
                        self.session['free_vram_gb'] = vram_dict.get('free_vram_gb', 0)
                        models_loaded_size_gb = loaded_tts_size_gb(loaded_tts)
                        if self.session['free_vram_gb'] <= models_loaded_size_gb:
                            del loaded_tts[self.tts_key]
                        hf_repo = models[TTS_ENGINES['XTTSv2']]['internal']['repo']
                        hf_sub = ''
                        config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['XTTSv2']]['internal']['files'][0]}", cache_dir=self.cache_dir)
                        checkpoint_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['XTTSv2']]['internal']['files'][1]}", cache_dir=self.cache_dir)
                        vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}{models[TTS_ENGINES['XTTSv2']]['internal']['files'][2]}", cache_dir=self.cache_dir)
                        engine = self._load_checkpoint(tts_engine=TTS_ENGINES['XTTSv2'], key=key, checkpoint_path=checkpoint_path, config_path=config_path, vocab_path=vocab_path)
                    if engine:
                        if speaker in default_engine_settings[TTS_ENGINES['XTTSv2']]['voices'].keys():
                            gpt_cond_latent, speaker_embedding = self.xtts_speakers[default_engine_settings[TTS_ENGINES['XTTSv2']]['voices'][speaker]].values()
                        else:
                            gpt_cond_latent, speaker_embedding = engine.get_conditioning_latents(audio_path=[voice_path])
                        fine_tuned_params = {
                            key.removeprefix("xtts_"): cast_type(self.session[key])
                            for key, cast_type in {
                                "xtts_temperature": float,
                                #"xtts_codec_temperature": float,
                                "xtts_length_penalty": float,
                                "xtts_num_beams": int,
                                "xtts_repetition_penalty": float,
                                #"xtts_cvvp_weight": float,
                                "xtts_top_k": int,
                                "xtts_top_p": float,
                                "xtts_speed": float,
                                #"xtts_gpt_cond_len": int,
                                #"xtts_gpt_batch_size": int,
                                "xtts_enable_text_splitting": bool
                            }.items()
                            if self.session.get(key) is not None
                        }
                        with torch.no_grad():
                            result = engine.inference(
                                text=default_text.strip(),
                                language=self.session['language_iso1'],
                                gpt_cond_latent=gpt_cond_latent,
                                speaker_embedding=speaker_embedding,
                                **fine_tuned_params,
                            )
                        audio_sentence = result.get('wav') if isinstance(result, dict) else None
                        if audio_sentence is not None:
                            audio_sentence = audio_sentence.tolist()
                            sourceTensor = self._tensor_type(audio_sentence)
                            audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                            # CON is a reserved name on windows
                            lang_dir = 'con-' if self.session['language'] == 'con' else self.session['language']
                            new_voice_path = re.sub(r'([\\/])eng([\\/])', rf'\1{lang_dir}\2', voice_path)
                            proc_voice_path = new_voice_path.replace('.wav', '_temp.wav')
                            torchaudio.save(proc_voice_path, audio_tensor, default_engine_settings[TTS_ENGINES['XTTSv2']]['samplerate'], format='wav')
                            if normalize_audio(proc_voice_path, new_voice_path, default_audio_proc_samplerate, self.session['is_gui_process']):
                                del audio_sentence, sourceTensor, audio_tensor
                                Path(proc_voice_path).unlink(missing_ok=True)
                                gc.collect()
                                self.engine = loaded_tts.get(self.tts_key, False)
                                if not self.engine:
                                    self._load_engine()
                                return new_voice_path
                            else:
                                error = 'normalize_audio() error:'
                        else:
                            error = f'No audio waveform found in _check_xtts_builtin_speakers() result: {result}'
                    else:
                        error = f"_check_xtts_builtin_speakers() error: {TTS_ENGINES['XTTSv2']} is False"
                else:
                    error = f'The translated {default_text_file} could not be found! Voice cloning file will stay in English.'
                print(error)
            else:
                return voice_path
        except Exception as e:
            error = f'_check_xtts_builtin_speakers() error: {e}'
            if new_voice_path:
                Path(new_voice_path).unlink(missing_ok=True)
            if proc_voice_path:
                Path(proc_voice_path).unlink(missing_ok=True)
            print(error)
            return False

    def _check_bark_npz(self, voice_path:str, bark_dir:str, speaker:str)->bool:
        try:
            if self.session['language'] in language_tts[TTS_ENGINES['BARK']].keys():
                pth_voice_dir = os.path.join(bark_dir, speaker)
                pth_voice_file = os.path.join(pth_voice_dir,f'{speaker}.pth')
                if os.path.exists(pth_voice_file):
                    return True
                else:
                    os.makedirs(pth_voice_dir,exist_ok=True)
                    key = f"{TTS_ENGINES['BARK']}-internal"
                    default_text_file = os.path.join(voices_dir, self.session['language'], 'default.txt')
                    default_text = Path(default_text_file).read_text(encoding="utf-8")
                    fine_tuned_params = {
                        key.removeprefix("bark_"):cast_type(self.session[key])
                        for key,cast_type in{
                            "bark_text_temp":float,
                            "bark_waveform_temp":float
                        }.items()
                        if self.session.get(key) is not None
                    }
                    with torch.no_grad():
                        result = self.engine.synthesize(
                            default_text,
                            speaker_wav=voice_path,
                            speaker=speaker,
                            voice_dir=pth_voice_dir,
                            **fine_tuned_params
                        )
                    del result
                    msg = f"Saved file: {pth_voice_file}"
                    print(msg)
                    return True
            else:
                return True
        except Exception as e:
            error = f'_check_bark_npz() error: {e}'
            print(error)
            return False
        
    def _tensor_type(self,audio_data:Any)->torch.Tensor:
        if isinstance(audio_data, torch.Tensor):
            return audio_data
        elif isinstance(audio_data,np.ndarray):
            return torch.from_numpy(audio_data).float()
        elif isinstance(audio_data,list):
            return torch.tensor(audio_data,dtype=torch.float32)
        else:
            raise TypeError(f"Unsupported type for audio_data: {type(audio_data)}")
            
    def _get_resampler(self,orig_sr:int,target_sr:int)->torchaudio.transforms.Resample:
        key=(orig_sr,target_sr)
        if key not in self.resampler_cache:
            self.resampler_cache[key]=torchaudio.transforms.Resample(
                orig_freq = orig_sr,new_freq = target_sr
            )
        return self.resampler_cache[key]

    def _resample_wav(self,wav_path:str,expected_sr:int)->str:
        waveform,orig_sr = torchaudio.load(wav_path)
        if orig_sr==expected_sr and waveform.size(0)==1:
            return wav_path
        if waveform.size(0)>1:
            waveform = waveform.mean(dim=0,keepdim=True)
        if orig_sr!=expected_sr:
            resampler = self._get_resampler(orig_sr,expected_sr)
            waveform = resampler(waveform)
        wav_tensor = waveform.squeeze(0)
        wav_numpy = wav_tensor.cpu().numpy()
        os.path.join(self.session['process_dir'], 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_fh = tempfile.NamedTemporaryFile(dir=tmp_dir, suffix=".wav", delete=False)
        tmp_path = tmp_fh.name
        tmp_fh.close()
        sf.write(tmp_path,wav_numpy,expected_sr,subtype="PCM_16")
        return tmp_path

    def convert(self, sentence_index:int, sentence:str)->bool:
        try:
            speaker = None
            audio_sentence = False
            self.params['voice_path'] = (
                self.session['voice'] if self.session['voice'] is not None 
                else models[self.session['tts_engine']][self.session['fine_tuned']]['voice']
            )
            if self.params['voice_path'] is not None:
                speaker = re.sub(r'\.wav$', '', os.path.basename(self.params['voice_path']))
                if self.params['voice_path'] not in default_engine_settings[TTS_ENGINES['BARK']]['voices'].keys() and self.session['custom_model_dir'] not in self.params['voice_path']:
                    self.session['voice'] = self.params['voice_path'] = self._check_xtts_builtin_speakers(self.params['voice_path'], speaker)
                    if not self.params['voice_path']:
                        msg = f"Could not create the builtin speaker selected voice in {self.session['language']}"
                        print(msg)
                        return False
            if self.engine:
                device = devices['CUDA']['proc'] if self.session['device'] in ['cuda', 'jetson'] else self.session['device']
                self.engine.to(device)
                final_sentence_file = os.path.join(self.session['chapters_dir_sentences'], f'{sentence_index}.{default_audio_proc_format}')
                if sentence == TTS_SML['break']:
                    silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                    break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time)) # 0.4 to 0.7 seconds
                    self.audio_segments.append(break_tensor.clone())
                    return True
                elif not sentence.replace('—', '').strip() or sentence == TTS_SML['pause']:
                    silence_time = int(np.random.uniform(1.0, 1.8) * 100) / 100
                    pause_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time)) # 1.0 to 1.8 seconds
                    self.audio_segments.append(pause_tensor.clone())
                    return True
                else:
                    if sentence.endswith("'"):
                        sentence = sentence[:-1]
                    trim_audio_buffer = 0.002
                    sentence += '…' if sentence[-1].isalnum() else ''
                    '''
                        [laughter]
                        [laughs]
                        [sighs]
                        [music]
                        [gasps]
                        [clears throat]
                        — or ... for hesitations
                        ♪ for song lyrics
                        CAPITALIZATION for emphasis of a word
                        [MAN] and [WOMAN] to bias Bark toward male and female speakers, respectively
                    '''
                    if speaker in default_engine_settings[self.session['tts_engine']]['voices'].keys():
                        bark_dir = default_engine_settings[self.session['tts_engine']]['speakers_path']
                    else:
                        bark_dir = os.path.join(os.path.dirname(self.params['voice_path']), 'bark')       
                        if not self._check_bark_npz(self.params['voice_path'], bark_dir, speaker):
                            error = 'Could not create pth voice file!'
                            print(error)
                            return False
                    pth_voice_dir = os.path.join(bark_dir, speaker)
                    pth_voice_file = os.path.join(bark_dir, speaker, f'{speaker}.pth')
                    fine_tuned_params = {
                        key.removeprefix("bark_"): cast_type(self.session[key])
                        for key, cast_type in {
                            "bark_text_temp": float,
                            "bark_waveform_temp": float
                        }.items()
                        if self.session.get(key) is not None
                    }
                    with torch.no_grad():
                        result = self.engine.synthesize(
                            sentence,
                            #speaker_wav=self.params['voice_path'],
                            speaker=speaker,
                            voice_dir=pth_voice_dir,
                            **fine_tuned_params
                        )
                    audio_sentence = result.get('wav')
                    if is_audio_data_valid(audio_sentence):
                        audio_sentence = audio_sentence.tolist()
                    if is_audio_data_valid(audio_sentence):
                        sourceTensor = self._tensor_type(audio_sentence)
                        audio_tensor = sourceTensor.clone().detach().unsqueeze(0).cpu()
                        if sentence[-1].isalnum() or sentence[-1] == '—':
                            audio_tensor = trim_audio(audio_tensor.squeeze(), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
                        if audio_tensor is not None and audio_tensor.numel() > 0:
                            self.audio_segments.append(audio_tensor)
                            if not re.search(r'\w$', sentence, flags=re.UNICODE) and sentence[-1] != '—':
                                silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                                break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time))
                                self.audio_segments.append(break_tensor.clone())
                            if self.audio_segments:
                                audio_tensor = torch.cat(self.audio_segments, dim=-1)
                                start_time = self.sentences_total_time
                                duration = round((audio_tensor.shape[-1] / self.params['samplerate']), 2)
                                end_time = start_time + duration
                                self.sentences_total_time = end_time
                                sentence_obj = {
                                    "start": start_time,
                                    "end": end_time,
                                    "text": sentence,
                                    "resume_check": self.sentence_idx
                                }
                                self.sentence_idx = append_sentence2vtt(sentence_obj, self.vtt_path)
                                if self.sentence_idx:
                                    torchaudio.save(final_sentence_file, audio_tensor, self.params['samplerate'], format=default_audio_proc_format)
                                    del audio_tensor
                                    cleanup_memory()
                            self.audio_segments = []
                            if os.path.exists(final_sentence_file):
                                return True
                            else:
                                error = f"Cannot create {final_sentence_file}"
                                print(error)
                                return False
                    else:
                        error = f"audio_sentence not valide"
                        print(error)
                        return False
            else:
                error = f"TTS engine {self.session['tts_engine']} could not be loaded!\nPossible reason can be not enough VRAM/RAM memory"
                print(error)
                return False
        except Exception as e:
            error = f'Bark.convert(): {e}'
            raise ValueError(e)
            return False