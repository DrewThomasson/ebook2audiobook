from lib.classes.tts_engines.common.headers import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

class Bark(TTSUtils, TTSRegistry, name='bark'):

    def __init__(self, session:DictProxy):
        try:
            self.session = session
            self.cache_dir = tts_dir
            self.speakers_path = None
            self.speaker = None
            self.tts_key = self.session['model_cache']
            #self.pth_voice_file = None
            self.resampler_cache = {}
            self.audio_segments = []
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {}
            self.params['samplerate'] = self.models[self.session['fine_tuned']]['samplerate']
            enough_vram = self.session['free_vram_gb'] > 4.0
            seed = 0
            #random.seed(seed)
            self.amp_dtype = self._apply_gpu_policy(enough_vram=enough_vram, seed=seed)
            self.xtts_speakers = self._load_xtts_builtin_list()
            self.engine = self.load_engine()
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def load_engine(self)->Any:
        msg = f"Loading TTS {self.tts_key} model, it takes a while, please be patient…"
        print(msg)
        self._cleanup_memory()
        engine = loaded_tts.get(self.tts_key)
        if not engine:
            if self.session['custom_model'] is not None:
                error = f"{self.session['tts_engine']} custom model not implemented yet!"
                raise NotImplementedError(error)
            try:
                model_cfg = self.models[self.session['fine_tuned']]
                model_path = model_cfg['repo']
            except KeyError as e:
                error = f"Invalid fine_tuned model '{self.session['fine_tuned']}'"
                raise KeyError(error) from e
            try:
                engine = self._load_api(self.tts_key, model_path)
            except Exception as e:
                error = 'load_engine(): _load_api() failed'
                raise RuntimeError(error) from e
        if engine:
            msg = f'TTS {self.tts_key} Loaded!'
            print(msg)
            return engine
        error = 'load_engine(): engine is None'
        raise RuntimeError(error)

    def convert(self, sentence_index:int, sentence:str)->bool:
        try:
            import torch
            import torchaudio
            import numpy as np
            from lib.classes.tts_engines.common.audio import trim_audio, is_audio_data_valid
            if self.engine:
                final_sentence_file = os.path.join(self.session['sentences_dir'], f'{sentence_index}.{default_audio_proc_format}')
                device = devices['CUDA']['proc'] if self.session['device'] in [devices['CUDA']['proc'], devices['JETSON']['proc']] else self.session['device']
                sentence_parts = self._split_sentence_on_sml(sentence)
                if not self._set_voice():
                    return False
                self.speaker = Path(self.params['current_voice']).stem if self.params['current_voice'] is not None else Path(self.models[self.session['fine_tuned']]['voice']).stem
                if self.speaker in default_engine_settings[self.session['tts_engine']]['voices'].keys():
                    bark_dir = default_engine_settings[self.session['tts_engine']]['speakers_path']
                else:
                    bark_dir = os.path.join(os.path.dirname(self.params['current_voice']), 'bark')
                pth_voice_dir = os.path.join(bark_dir, self.speaker)
                if not os.path.exists(pth_voice_dir):
                    os.makedirs(pth_voice_dir, exist_ok=True)
                #pth_voice_file = os.path.join(bark_dir, self.speaker, f'{self.speaker}.pth')
                self.engine.synthesizer.voice_dir = pth_voice_dir
                speaker_argument = {}
                if self.speaker not in self.engine.speakers:
                    speaker_argument['speaker_wav'] = self.params['current_voice']
                fine_tuned_params = {
                    key.removeprefix("bark_"): cast_type(self.session[key])
                    for key, cast_type in {
                        "bark_text_temp": float,
                        "bark_waveform_temp": float
                    }.items()
                    if self.session.get(key) is not None
                }
                self.audio_segments = []
                for part in sentence_parts:
                    part = part.strip()
                    if not part:
                        continue
                    if SML_TAG_PATTERN.fullmatch(part):
                        res, error = self._convert_sml(part)
                        if not res: 
                            print(error)
                            return False
                        continue
                    if not any(c.isalnum() for c in part):
                        continue
                    else:
                        trim_audio_buffer = 0.002
                        if part.endswith("'"):
                            part = part[:-1]
                        '''
                            [laughter]
                            [laughs]
                            [sighs]
                            [music]
                            [gasps]
                            [clears throat]
                            — or … for hesitations
                            ♪ for song lyrics
                            CAPITALIZATION for emphasis of a word
                            [MAN] and [WOMAN] to bias Bark toward male and female speakers, respectively
                        '''
                        with torch.no_grad():
                            self.engine.to(device)
                            if device == devices['CPU']['proc']:
                                audio_part = self.engine.tts(
                                    text=part,
                                    speaker=self.speaker,
                                    voice_dir=pth_voice_dir,
                                    **fine_tuned_params,
                                    **speaker_argument,
                                )
                            else:
                                with torch.autocast(
                                    device_type=device,
                                    dtype=self.amp_dtype
                                ):
                                    audio_part = self.engine.tts(
                                        text=part,
                                        speaker=self.speaker,
                                        voice_dir=pth_voice_dir,
                                        **speaker_argument,
                                        **fine_tuned_params
                                    )
                            self.engine.to(devices['CPU']['proc'])
                        if is_audio_data_valid(audio_part):
                            src_tensor = self._tensor_type(audio_part)
                            part_tensor = src_tensor.clone().detach().unsqueeze(0).cpu()
                            if part_tensor is not None and part_tensor.numel() > 0:
                                if part[-1].isalnum() or part[-1] == '—':
                                    part_tensor = trim_audio(part_tensor.squeeze(), self.params['samplerate'], 0.001, trim_audio_buffer).unsqueeze(0)
                                self.audio_segments.append(part_tensor)
                                if not re.search(r'\w$', part, flags=re.UNICODE) and part[-1] != '—':
                                    #np.random.seed(seed)
                                    silence_time = int(np.random.uniform(0.3, 0.6) * 100) / 100
                                    break_tensor = torch.zeros(1, int(self.params['samplerate'] * silence_time))
                                    self.audio_segments.append(break_tensor.clone())
                            else:
                                error = f"part_tensor not valid"
                                print(error)
                                return False
                        else:
                            error = f"audio_part not valid"
                            print(error)
                            return False
                if self.audio_segments:
                    segment_tensor = torch.cat(self.audio_segments, dim=-1)
                    torchaudio.save(final_sentence_file, segment_tensor, self.params['samplerate'], format=default_audio_proc_format)
                    del segment_tensor
                    self._cleanup_memory()
                    self.audio_segments = []
                    if not os.path.exists(final_sentence_file):
                        error = f"Cannot create {final_sentence_file}"
                        print(error)
                        return False
                return True
            else:
                error = f"TTS engine {self.session['tts_engine']} failed to load!"
                print(error)
                return False
        except Exception as e:
            error = f'Bark.convert(): {e}'
            raise ValueError(e)
            return False

    def create_vtt(self, all_sentences:list)->bool:
        audio_dir = self.session['sentences_dir']
        vtt_path = os.path.join(self.session['process_dir'],Path(self.session['final_name']).stem+'.vtt')
        if self._build_vtt_file(all_sentences, audio_dir, vtt_path):
            return True
        return False