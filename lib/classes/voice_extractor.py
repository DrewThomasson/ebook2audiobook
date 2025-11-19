import os
import numpy as np
import regex as re
import scipy.fftpack
import soundfile as sf
import subprocess
import shutil
import json

from typing import Any
from io import BytesIO
from pydub import AudioSegment, silence
from pydub.silence import detect_silence

from lib.conf import voice_formats, default_audio_proc_samplerate
from lib.models import TTS_ENGINES, models
from lib.classes.background_detector import BackgroundDetector
from lib.classes.subprocess_pipe import SubprocessPipe

class VoiceExtractor:
    def __init__(self, session:Any, voice_file:str, voice_name:str):
        self.wav_file = None
        self.session = session
        self.voice_file = voice_file
        self.voice_name = voice_name
        self.voice_track = 'vocals.wav'
        self.samplerate = models[session['tts_engine']][session['fine_tuned']]['samplerate']
        self.output_dir = self.session['voice_dir']
        self.demucs_dir = os.path.join(self.output_dir,'htdemucs',voice_name)
        self.proc_voice_file = os.path.join(self.session['voice_dir'], f'{self.voice_name}_proc.wav')
        self.final_voice_file = os.path.join(self.session['voice_dir'], f'{self.voice_name}.wav')
        self.silence_threshold = -60

    def _validate_format(self)->tuple[bool,str]:
        file_extension = os.path.splitext(self.voice_file)[1].lower()
        if file_extension in voice_formats:
            msg = 'Input file is valid'
            return True,msg
        error = f'Unsupported file format: {file_extension}. Supported formats are: {", ".join(voice_formats)}'
        return False,error

    def _convert2wav(self)->tuple[bool, str]:
        try:
            self.wav_file = os.path.join(self.session['voice_dir'], f'{self.voice_name}.wav')
            cmd = [
                shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', self.voice_file,
                '-ac', '1', '-y', self.wav_file
            ]   
            proc_pipe = SubprocessPipe(cmd, is_gui_process=self.session['is_gui_process'], total_duration=self._get_audio_duration(self.voice_file), msg='Convert')
            if proc_pipe:
                if not os.path.exists(self.wav_file) or os.path.getsize(self.wav_file) == 0:
                    error = f'_convert2wav output error: {self.wav_file} was not created or is empty.'
                    return False, error
                else:
                    msg = 'Conversion to .wav format for processing successful'
                    return True, msg
            else:
                error = f'_convert2wav() error:: {self.wav_file}'
                return False, error
        except subprocess.CalledProcessError as e:
            try:
                stderr_text = e.stderr.decode('utf-8', errors='replace')
            except Exception:
                stderr_text = str(e)
            error = f'_convert2wav ffmpeg.Error: {stderr_text}'
            raise ValueError(error)
        except Exception as e:
            error = f'_convert2wav() error: {e}'
            raise ValueError(error)
        return False, error

    def _detect_background(self)->tuple[bool,bool,str]:
        try:
            msg = 'Detecting any background noise or music...'
            print(msg)
            detector = BackgroundDetector(wav_file = self.wav_file)
            status,report = detector.detect(vad_ratio_thresh = 0.15)
            print(report)
            if status:
                msg = 'Background noise or music detected. Proceeding voice extraction...'
            else:
                msg = 'No background noise or music detected. Skipping separation...'
            return True,status,msg
        except Exception as e:
            error = f'_detect_background() error: {e}'
            raise ValueError(error)
            return False,False,error

    def _demucs_voice(self)->tuple[bool, str]:
        try:
            cmd = [
                "demucs",
                "--verbose",
                "--two-stems=vocals",
                "--out", self.output_dir,
                self.wav_file
            ]
            try:
                process = subprocess.run(cmd, check = True)
                self.voice_track = os.path.join(self.demucs_dir, self.voice_track)
                msg = 'Voice track isolation successful'
                return True, msg
            except subprocess.CalledProcessError as e:
                error = (
                    f'_demucs_voice() subprocess CalledProcessError error: {e.returncode}\n\n'
                    f'stdout: {e.output}\n\n'
                    f'stderr: {e.stderr}'
                )
                raise ValueError(error)
            except FileNotFoundError:
                error = f'_demucs_voice() subprocess FileNotFoundError error: The "demucs" command was not found. Ensure it is installed and in PATH.'
                raise ValueError(error)
            except Exception as e:
                error = f'_demucs_voice() subprocess Exception error: {str(e)}'
                raise ValueError(error)
        except Exception as e:
            error = f'_demucs_voice() error: {e}'
            raise ValueError(error)
        return False, error

    def _remove_silences(self, audio:AudioSegment, silence_threshold:int, min_silence_len:int = 200, keep_silence:int = 300)->None:
        final_audio = AudioSegment.silent(duration = 0)
        chunks = silence.split_on_silence(
            audio,
            min_silence_len = min_silence_len,
            silence_thresh = silence_threshold,
            keep_silence = keep_silence
        )
        for chunk in chunks:
            final_audio += chunk
        final_audio.export(self.voice_track, format = 'wav')
    
    def _trim_and_clean(self, silence_threshold:int, min_silence_len:int = 200, chunk_size:int = 100)->tuple[bool, str]:
        try:
            audio = AudioSegment.from_file(self.voice_track)
            total_duration = len(audio)
            min_required_duration = 20000 if self.session['tts_engine'] == TTS_ENGINES['BARK'] else 12000
            msg = f"Removing long pauses..."
            print(msg)
            self._remove_silences(audio, silence_threshold)
            if total_duration <= min_required_duration:
                msg = f"Audio is only {total_duration / 1000:.2f}s long; skipping audio trimming..."
                return True, msg
            else:
                if total_duration > (min_required_duration * 2):
                    msg = f"Audio longer than the max allowed. Proceeding to audio trimming..."
                    print(msg)
                    window = min_required_duration
                    hop = max(1, window // 4)
                    best_var = -float("inf")
                    best_start = 0
                    sr = audio.frame_rate
                    for start in range(0, total_duration - window + 1, hop):
                        chunk = audio[start : start + window]
                        samples = np.array(chunk.get_array_of_samples()).astype(float)
                        spectrum = np.abs(scipy.fftpack.fft(samples))
                        p = spectrum / (np.sum(spectrum) + 1e-10)
                        entropy = -np.sum(p * np.log2(p + 1e-10))
                        if entropy > best_var:
                            best_var = entropy
                            best_start = start
                    best_end = best_start + window
                    msg = (
                        f"Selected most‐diverse‐spectrum window "
                        f"{best_start / 1000:.2f}s–{best_end / 1000:.2f}s "
                        f"(@ entropy {best_var:.2f} bits)"
                    )
                    print(msg)
                    silence_spans = detect_silence(
                        audio,
                        min_silence_len = min_silence_len,
                        silence_thresh = silence_threshold
                    )
                    prev_ends = [end for (start, end) in silence_spans if end <= best_start]
                    if prev_ends:
                        new_start = max(prev_ends)
                    else:
                        new_start = 0
                    next_starts = [start for (start, end) in silence_spans if start >= best_end]
                    if next_starts:
                        new_end = min(next_starts)
                    else:
                        new_end = total_duration
                    best_start, best_end = new_start, new_end
                else:
                    best_start = 0
                    best_end = total_duration
            trimmed_audio = audio[best_start:best_end]
            trimmed_audio.export(self.voice_track, format = 'wav')
            msg = 'Audio trimmed and cleaned!'
            return True, msg
        except Exception as e:
            error = f'_trim_and_clean() error: {e}'
            raise ValueError(error)

    def _get_audio_duration(self, filepath:str)->float:
        try:
            cmd = [
                shutil.which('ffprobe'),
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            try:
                duration = json.loads(result.stdout)['format']['duration']
                return float(duration)
            except Exception:
                return 0
        except subprocess.CalledProcessError as e:
            DependencyError(e)
            return 0
        except Exception as e:
            error = f"get_audio_duration() Error: Failed to process {filepath}: {e}"
            print(error)
            return 0

    def normalize_audio(self, src_file:str=None, proc_file:str=None, dst_file:str=None)->tuple[bool, str]:
        error = ''
        try:
            src_file = src_file or self.voice_track
            proc_file = proc_file or self.proc_voice_file
            dst_file = dst_file or self.final_voice_file
            cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', src_file]
            filter_complex = (
                'agate=threshold=-25dB:ratio=1.4:attack=10:release=250,'
                'afftdn=nf=-70,'
                'acompressor=threshold=-20dB:ratio=2:attack=80:release=200:makeup=1dB,'
                'loudnorm=I=-14:TP=-3:LRA=7:linear=true,'
                'equalizer=f=150:t=q:w=2:g=1,'
                'equalizer=f=250:t=q:w=2:g=-3,'
                'equalizer=f=3000:t=q:w=2:g=2,'
                'equalizer=f=5500:t=q:w=2:g=-4,'
                'equalizer=f=9000:t=q:w=2:g=-2,'
                'highpass=f=63[audio]'
            )
            cmd += [
                '-filter_complex', filter_complex,
                '-map', '[audio]',
                '-ar', f'{default_audio_proc_samplerate}',
                '-y', proc_file
            ]
            try:
                proc_pipe = SubprocessPipe(cmd, is_gui_process=self.session['is_gui_process'], total_duration=self._get_audio_duration(src_file), msg='Normalize')
                if proc_pipe:
                    if not os.path.exists(proc_file) or os.path.getsize(proc_file) == 0:
                        error = f'normalize_audio() error: {proc_file} was not created or is empty.'
                        return False, error
                    else:
                        if proc_file != dst_file:
                            os.replace(proc_file, dst_file)
                            shutil.rmtree(self.demucs_dir, ignore_errors = True)
                        msg = 'Audio normalization successful!'
                        return True, msg
                else:
                    error = f'normalize_audio() error: {dst_file}'
                    return False, error
            except subprocess.CalledProcessError as e:
                error = f'normalize_audio() ffmpeg.Error: {e.stderr.decode()}'
        except FileNotFoundError as e:
            error = 'normalize_audio() FileNotFoundError: {e} Input file or FFmpeg PATH not found!'
        except Exception as e:
            error = f'normalize_audio() error: {e}'
        return False, error

    def extract_voice(self)->tuple[bool,str|None]:
        success = False
        msg = None
        try:
            success, msg = self._validate_format()
            print(msg)
            if success:
                success, msg = self._convert2wav()
                print(msg)
                if success:
                    success, status, msg = self._detect_background()
                    print(msg)
                    if success:
                        if status:
                            success, msg = self._demucs_voice()
                            print(msg)
                        else:
                            self.voice_track = self.wav_file
                        if success:
                            success, msg = self._trim_and_clean(self.silence_threshold)
                            print(msg)
                            if success:
                                success, msg = self.normalize_audio()
                                print(msg)
        except Exception as e:
            msg = f'extract_voice() error: {e}'
            raise ValueError(msg)
        shutil.rmtree(self.demucs_dir, ignore_errors = True)
        return success, msg