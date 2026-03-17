import os
import json
import shutil
import tempfile
import subprocess

from typing import Any
from pathlib import Path
from multiprocessing.managers import DictProxy

from lib.classes.tts_registry import TTSRegistry
from lib.classes.tts_engines.common.preset_loader import load_engine_presets
from lib.classes.tts_engines.common.audio import get_audiolist_duration
from lib.conf import default_audio_proc_format
from lib.conf_models import TTS_ENGINES, SML_TAG_PATTERN

try:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
except ImportError:
    pass


MINIMAX_VOICES = {
    "English_Graceful_Lady": "Graceful Lady",
    "English_Insightful_Speaker": "Insightful Speaker",
    "English_radiant_girl": "Radiant Girl",
    "English_Persuasive_Man": "Persuasive Man",
    "English_Lucky_Robot": "Lucky Robot",
    "English_expressive_narrator": "Expressive Narrator",
}


class MiniMax(TTSRegistry, name='minimax'):

    def __init__(self, session: DictProxy):
        try:
            self.session = session
            self.models = load_engine_presets(self.session['tts_engine'])
            self.params = {}
            fine_tuned = self.session.get('fine_tuned')
            if fine_tuned not in self.models:
                error = f'Invalid fine_tuned model {fine_tuned}. Available models: {list(self.models.keys())}'
                raise ValueError(error)
            model_cfg = self.models[fine_tuned]
            for required_key in ('samplerate',):
                if required_key not in model_cfg:
                    error = f'fine_tuned model {fine_tuned} is missing required key {required_key}.'
                    raise ValueError(error)
            self.params['samplerate'] = model_cfg['samplerate']
            self.params['model'] = model_cfg.get('model', 'speech-2.8-hd')
            self.params['default_voice'] = model_cfg.get('voice', 'English_Graceful_Lady')
            self.api_key = os.environ.get('MINIMAX_API_KEY', '')
            self.base_url = os.environ.get('MINIMAX_BASE_URL', 'https://api.minimax.io')
            if not self.api_key:
                error = 'MINIMAX_API_KEY environment variable is required for MiniMax TTS engine'
                raise ValueError(error)
            msg = f'MiniMax TTS engine initialized (model: {self.params["model"]})'
            print(msg)
        except Exception as e:
            error = f'__init__() error: {e}'
            raise ValueError(error)

    def _get_voice_id(self) -> str:
        voice = self.session.get('voice')
        if voice and voice in MINIMAX_VOICES:
            return voice
        return self.params['default_voice']

    def _synthesize(self, text: str, voice_id: str) -> bytes:
        url = f'{self.base_url}/v1/t2a_v2'
        payload = {
            'model': self.params['model'],
            'text': text,
            'stream': False,
            'voice_setting': {
                'voice_id': voice_id,
                'speed': 1,
                'vol': 1,
                'pitch': 0,
            },
            'audio_setting': {
                'sample_rate': self.params['samplerate'],
                'bitrate': 128000,
                'format': 'mp3',
                'channel': 1,
            },
        }
        language = self.session.get('language', '')
        if language:
            iso1 = self.session.get('language_iso1', '')
            if iso1 == 'en':
                payload['language_boost'] = 'English'
            elif iso1 == 'zh' or iso1 == 'zh-cn':
                payload['language_boost'] = 'Chinese'
            else:
                payload['language_boost'] = 'auto'

        req_data = json.dumps(payload).encode('utf-8')
        req = Request(
            url,
            data=req_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
            },
        )
        try:
            resp = urlopen(req, timeout=120)
            result = json.loads(resp.read().decode('utf-8'))
        except HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            error = f'MiniMax TTS API error {e.code}: {body}'
            raise RuntimeError(error) from e
        except URLError as e:
            error = f'MiniMax TTS network error: {e.reason}'
            raise RuntimeError(error) from e

        status_code = result.get('base_resp', {}).get('status_code', -1)
        if status_code != 0:
            status_msg = result.get('base_resp', {}).get('status_msg', 'unknown error')
            error = f'MiniMax TTS error (code {status_code}): {status_msg}'
            raise RuntimeError(error)

        hex_audio = result.get('data', {}).get('audio', '')
        if not hex_audio:
            error = 'MiniMax TTS returned empty audio data'
            raise RuntimeError(error)

        return bytes.fromhex(hex_audio)

    def _mp3_to_target_format(self, mp3_data: bytes, output_path: str) -> bool:
        ffmpeg = shutil.which('ffmpeg')
        if not ffmpeg:
            error = 'ffmpeg not found, required for audio format conversion'
            print(error)
            return False

        tmp_dir = os.path.dirname(output_path)
        with tempfile.NamedTemporaryFile(dir=tmp_dir, suffix='.mp3', delete=False) as tmp:
            tmp.write(mp3_data)
            tmp_mp3 = tmp.name

        try:
            cmd = [
                ffmpeg, '-hide_banner', '-nostats', '-loglevel', 'error',
                '-i', tmp_mp3,
                '-ar', str(self.params['samplerate']),
                '-ac', '1',
                '-y', output_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                error = f'ffmpeg conversion error: {result.stderr}'
                print(error)
                return False
            return os.path.exists(output_path)
        except Exception as e:
            error = f'_mp3_to_target_format() error: {e}'
            print(error)
            return False
        finally:
            Path(tmp_mp3).unlink(missing_ok=True)

    def convert(self, sentence_index: int, sentence: str) -> bool:
        try:
            final_sentence_file = os.path.join(
                self.session['sentences_dir'],
                f'{sentence_index}.{default_audio_proc_format}',
            )
            clean_text = SML_TAG_PATTERN.sub('', sentence).strip()
            if not clean_text or not any(c.isalnum() for c in clean_text):
                clean_text = '...'

            voice_id = self._get_voice_id()
            mp3_data = self._synthesize(clean_text, voice_id)
            if not self._mp3_to_target_format(mp3_data, final_sentence_file):
                error = f'Failed to convert MP3 to {default_audio_proc_format}'
                print(error)
                return False

            if not os.path.exists(final_sentence_file):
                error = f'Cannot create {final_sentence_file}'
                print(error)
                return False

            return True
        except Exception as e:
            error = f'MiniMax.convert(): {e}'
            print(error)
            return False

    def create_vtt(self, all_sentences: list) -> bool:
        try:
            from tqdm import tqdm
            audio_dir = self.session['sentences_dir']
            vtt_path = os.path.join(
                self.session['process_dir'],
                Path(self.session['final_name']).stem + '.vtt',
            )
            audio_sentences_dir = Path(audio_dir)
            audio_files = sorted(
                audio_sentences_dir.glob(f'*.{default_audio_proc_format}'),
                key=lambda p: int(p.stem),
            )
            audio_files_length = len(audio_files)
            all_sentences_length = len(all_sentences)

            expected_indices = list(range(audio_files_length))
            actual_indices = [int(p.stem) for p in audio_files]
            if actual_indices != expected_indices:
                missing = sorted(set(expected_indices) - set(actual_indices))
                error = f'Missing audio sentence files: {missing}'
                print(error)
                return False

            if audio_files_length != all_sentences_length:
                error = f'Audio/sentence mismatch: {audio_files_length} audio files vs {all_sentences_length} sentences'
                print(error)
                return False

            sentences_total_time = 0.0
            vtt_blocks = []

            durations = get_audiolist_duration([str(p) for p in audio_files])

            with tqdm(total=audio_files_length, unit='files') as t:
                for idx, file in enumerate(audio_files):
                    start_time = sentences_total_time
                    duration = durations.get(os.path.realpath(file), 0.0)
                    end_time = start_time + duration
                    sentences_total_time = end_time

                    m, s = divmod(start_time, 60)
                    h, m = divmod(m, 60)
                    start = f'{int(h):02}:{int(m):02}:{s:06.3f}'
                    m, s = divmod(end_time, 60)
                    h, m = divmod(m, 60)
                    end = f'{int(h):02}:{int(m):02}:{s:06.3f}'

                    import regex as re
                    text = re.sub(
                        r'\s+', ' ',
                        SML_TAG_PATTERN.sub('', str(all_sentences[idx])),
                    ).strip()
                    vtt_blocks.append(f'{start} --> {end}\n{text}\n')
                    t.update(1)

            with open(vtt_path, 'w', encoding='utf-8') as f:
                f.write('WEBVTT\n\n')
                f.write('\n'.join(vtt_blocks))
            return True
        except Exception as e:
            error = f'MiniMax.create_vtt(): {e}'
            print(error)
            return False
