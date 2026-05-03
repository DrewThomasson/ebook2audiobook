from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

#sys.stderr = StdoutFilter(sys.stdout)

class YourTTS(TTSUtils, TTSRegistry, name='yourtts'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.speaker = None
            self.tts_key = self.session['model_cache']
            self.pth_voice_file = None
            self.resampler_cache = {}
            self.audio_segments = []
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
            self.model_path = model_cfg['repo'].replace("[lang]", self.session['language'])
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 0
            #random.seed(seed)
            self.amp_dtype = self._apply_gpu_policy(enough_vram=enough_vram, seed=seed)
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['ROCM']['proc'], devices['JETSON']['proc']] else self.session['device']
            self.language = self.session['language_iso1'] if self.session['language_iso1'] == 'en' else 'fr-fr' if self.session['language_iso1'] == 'fr' else 'pt-br' if self.session['language_iso1'] == 'pt' else 'en'
            self.engine = self.load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        import torch
        msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient…"
        print(msg)
        self.cleanup_memory()
        engine = loaded_tts.get(self.tts_key)
        if engine:
            msg = f"TTS {self.tts_key} already loaded"
            print(msg)
            return engine
        try:
            model_cfg = self.models[self.session['fine_tuned']]
            model_path = model_cfg['repo']
        except KeyError as e:
            error = f"Invalid fine_tuned model '{self.session['fine_tuned']}'"
            raise KeyError(error) from e
        try:
            engine = self._load_api(self.tts_key, model_path)
            if engine is None:
                error = '_load_api() returned None'
                raise RuntimeError(error)
            msg = f'TTS {self.tts_key} Loaded!'
            print(msg)
            engine.to(self.device)
            with torch.inference_mode():
                samples = [
                    "Short warmup sentence.",
                    "This is a slightly longer warmup sentence to change tensor shapes."
                ]
                for s in samples:
                    _ = engine.tts(
                        text=s,
                        speaker_wav=default_engine_settings[self.session['tts_engine']]['voices']['ElectroMale-2'],
                        language='en',
                    )
            _ = torch.zeros((256, 256), device=self.device)
            return engine
        except Exception as e:
            error = 'load_engine(): engine is None'
            raise RuntimeError(error)

    def convert(self, sentence_file:str, sentence:str, **kwargs)->tuple:
        try:
            import torch
            import torchaudio
            #import numpy as np
            from lib.classes.tts_engines.common.audio import trim_audio, is_audio_data_valid
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
                self.engine.to(self.device)
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
                        else:
                            trim_audio_buffer = 0.002
                            if part.endswith("'"):
                                part = part[:-1]
                            part = re.sub(not_supported_punc_pattern, ' ', part).strip()
                            speaker_argument = {}
                            if self.params['current_voice'] is not None:
                                speaker_wav = self.params['current_voice']
                                speaker_argument = {"speaker_wav": speaker_wav}
                            else:
                                self.speaker = default_engine_settings[self.session['tts_engine']]['voices']['ElectroMale-2']
                                speaker_argument = {"speaker": self.speaker}
                            with torch.inference_mode():
                                with torch.autocast(self.device, dtype=self.amp_dtype, enabled=(self.amp_dtype != torch.float32)):
                                    audio_part = self.engine.tts(
                                        text=part,
                                        language=self.language,
                                        **speaker_argument
                                    )
                            if torch.is_tensor(audio_part):
                                audio_part = audio_part.detach().cpu()
                            if is_audio_data_valid(audio_part):
                                src_tensor = self._tensor_type(audio_part)
                                part_tensor = src_tensor.clone().detach().unsqueeze(0).cpu()
                                if part_tensor is not None and part_tensor.numel() > 0:
                                    if part[-1].isalnum() or part[-1] == '—':
                                        part_tensor = trim_audio(part_tensor.squeeze(), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
                                    self.audio_segments.append(part_tensor)
                                    del part_tensor
                                    """
                                    if not re.search(r'\w$', part, flags=re.UNICODE):
                                        silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                                        break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time))
                                        self.audio_segments.append(break_tensor.clone())
                                    """
                                else:
                                    error = f'part_tensor not valid'
                                    return False, error
                            else:
                                error = f'audio_part not valid'
                                return False, error
                self.engine.to(devices['CPU']['proc'])
                if self.audio_segments:
                    segment_tensor = torch.cat(self.audio_segments, dim=-1)
                    #torchaudio.save(sentence_file, segment_tensor, self.params['samplerate'])
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
            error = f'YourTTS.convert(): {e}'
            return False, error

    def create_vtt(self, all_sentences:list)->bool:
        if self._build_vtt_file(all_sentences):
            return True
        return False