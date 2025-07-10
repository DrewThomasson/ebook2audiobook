import os
import numpy as np
import regex as re
import scipy.fftpack
import soundfile as sf
import subprocess
import shutil
import torch

from io import BytesIO
from pydub import AudioSegment, silence
#from torchvggish import vggish, vggish_input

from lib.conf import voice_formats
from lib.models import TTS_ENGINES, models
from lib.classes.background_detector import BackgroundDetector

class VoiceExtractor:

    def __init__(self, session, models_dir, voice_file, voice_name):
        self.wav_file = None
        self.session = session
        self.voice_file = voice_file
        self.voice_name = voice_name
        self.models_dir = models_dir
        self.voice_track = 'vocals.wav'
        self.samplerate = models[session['tts_engine']][session['fine_tuned']]['samplerate']
        self.output_dir = self.session['voice_dir']
        self.demucs_dir = os.path.join(self.output_dir, 'htdemucs', os.path.splitext(os.path.basename(self.voice_file))[0])
        self.final_files = []
        self.silence_threshold = -60

    def _validate_format(self):
        file_extension = os.path.splitext(self.voice_file)[1].lower()
        if file_extension in voice_formats:
            msg = 'Input file valid'
            return True, msg
        error = f'Unsupported file format: {file_extension}. Supported formats are: {", ".join(voice_formats)}'
        return False, error

    def _convert2wav(self):
        try:
            self.wav_file = os.path.join(self.session['voice_dir'], f'{self.voice_name}.wav')
            ffmpeg_cmd = [
                shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', self.voice_file,
                '-ac', '1',
                '-y', self.wav_file
            ]
            process = subprocess.Popen(
                ffmpeg_cmd,
                env={},
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
                encoding='utf-8'
            )
            for line in process.stdout:
                print(line, end='')  # Print each line of stdout
            process.wait()
            if process.returncode != 0:
                error = f'_convert2wav(): process.returncode: {process.returncode}'
            elif not os.path.exists(self.wav_file) or os.path.getsize(self.wav_file) == 0:
                error = f'_convert2wav output error: {self.wav_file} was not created or is empty.'                
            else:
                msg = 'Conversion to .wav format for processing successful'
                return True, msg
        except subprocess.CalledProcessError as e:
            error = f'convert2wav fmpeg.Error: {e.stderr.decode()}'
            raise ValueError(error)
        except Exception as e:
            error = f'_convert2wav() error: {e}'
            raise ValueError(error)
        return False, error

    def _detect_background(self):
        try:
            msg = 'Detecting any background noise or music...'
            print(msg)
            torch_home = self.models_dir
            torch.hub.set_dir(torch_home)
            detector = BackgroundDetector(wav_file=self.wav_file, models_dir=torch_home)
            status, report = detector.detect(
                frame_s=1.0,               # frame length in seconds
                overlap=0.5,               # 50% overlap between frames
                energy_sigma_mul=1.5,      # threshold = mean + 1.5 * std
                flatness_thresh=0.3,       # spectral flatness cutoff
                zcr_thresh=0.3             # zero-crossing rate cutoff
            )
            print(report)
            if status:
                msg = 'Background noise or music detected. Proceeding voice extraction.'
            else:
                msg = 'No background noise or music detected. Skipping separation.'
            return True, status, msg
        except Exception as e:
            error = f'_detect_background() error: {e}'
            raise ValueError(error)
            return False, False, error

    def _demucs_voice(self):
        try:             
            cmd = [
                "demucs",
                "--verbose",
                "--two-stems=vocals",
                "--out", self.output_dir,
                self.wav_file
            ]
            try:
                torch_home = self.models_dir
                torch.hub.set_dir(torch_home)
                os.environ['TORCH_HOME'] = torch_home
                process = subprocess.run(cmd, check=True)
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

    def _remove_silences(self, audio, silence_threshold, min_silence_len=200, keep_silence=300):
        final_audio = AudioSegment.silent(duration=0)
        chunks = silence.split_on_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_threshold,
            keep_silence=keep_silence
        )
        for chunk in chunks:
            final_audio += chunk
        final_audio.export(self.voice_track, format='wav')
    
    def _trim_and_clean(self,silence_threshold, min_silence_len=200, chunk_size=100):
        try:
            audio = AudioSegment.from_file(self.voice_track)
            total_duration = len(audio)  # Total duration in milliseconds
            min_required_duration = 20000 if self.session['tts_engine'] == TTS_ENGINES['BARK'] else 12000
            msg = f"Removing long pauses..."
            print(msg)
            self._remove_silences(audio, silence_threshold)
            if total_duration <= min_required_duration:
                msg = f"Audio is only {total_duration/1000:.2f}s long; skipping audio trimming..."
                return True, msg
            else:
                if total_duration > (min_required_duration * 2):
                    msg = f"Audio longer than the max allowed. Proceeding to audio trimming..."          
                    # slide with a hop (e.g. quarter-window for a good speed/accuracy tradeoff)
                    window = min_required_duration
                    hop = max(1, window // 4)
                    best_loudness = -float('inf')
                    best_start = 0
                    for start in range(0, total_duration - window + 1, hop):
                        segment    = audio[start:start + window]
                        loudness   = segment.dBFS
                        if loudness > best_loudness:
                            best_loudness = loudness
                            best_start   = start
                    best_end = best_start + window
                    msg = (
                        f"Selected loudest window "
                        f"{best_start/1000:.2f}s–{best_end/1000:.2f}s "
                        f"(@ {best_loudness:.1f} dBFS)"
                    )
                    print(msg)
                else:
                    best_start = 0
                    best_end = total_duration       
            trimmed_audio = audio[best_start:best_end]
            trimmed_audio.export(self.voice_track, format='wav')
            msg = 'Audio trimmed and cleaned!'
            return True, msg
        except Exception as e:
            error = f'_trim_and_clean() error: {e}'
            raise ValueError(error)

    def _normalize_audio(self):
        try:                 
            process_file = os.path.join(self.session['voice_dir'], f'{self.voice_name}.wav')
            ffmpeg_cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', self.voice_track]
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
            ffmpeg_cmd += [
                '-filter_complex', filter_complex,
                '-map', '[audio]',
                '-ar', 'null',
                '-y', process_file
            ]
            error = None
            for rate in ['16000', '24000']:
                ffmpeg_cmd[-3] = rate
                output_file = re.sub(r'\.wav$', f'_{rate}.wav', process_file)
                ffmpeg_cmd[-1] = output_file
                try:
                    process = subprocess.Popen(
                        ffmpeg_cmd,
                        env={},
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        universal_newlines=True,
                        encoding='utf-8'
                    )
                    for line in process.stdout:
                        print(line, end='')  # Print each line of stdout
                    process.wait()
                    if process.returncode != 0:
                        error = f'_normalize_audio(): process.returncode: {process.returncode}'
                        break
                    elif not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                        error = f'_normalize_audio() error: {output_file} was not created or is empty.'
                        break
                    else:
                        self.final_files.append(output_file)
                except subprocess.CalledProcessError as e:
                    error = f'_normalize_audio() ffmpeg.Error: {e.stderr.decode()}'
                    break
            shutil.rmtree(self.demucs_dir, ignore_errors=True)
            if os.path.exists(process_file):
                os.remove(process_file)
            if error is None:
                msg = 'Audio normalization successful!'
                return True, msg
        except FileNotFoundError as e:
            error = '_normalize_audio() FileNotFoundError: {e} Input file or FFmpeg PATH not found!'
            raise ValueError(error)
        except Exception as e:
            error = f'_normalize_audio() error: {e}'
            raise ValueError(error)
        return False, error

    def extract_voice(self):
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
                                success, msg = self._normalize_audio()
                                print(msg)
        except Exception as e:
            msg = f'extract_voice() error: {e}'
            raise ValueError(msg)
        shutil.rmtree(self.demucs_dir, ignore_errors=True)
        torch.hub.set_dir(self.models_dir)
        os.environ['TORCH_HOME'] = self.models_dir
        return success, msg