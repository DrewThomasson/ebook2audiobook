import os
import subprocess
import ffmpeg
import shutil
import torch

from io import BytesIO
from pydub import AudioSegment
from torchvggish import vggish, vggish_input

from lib.conf import voice_formats
from lib.models import models

class VoiceExtractor:

    def __init__(self, session, models_dir, input_file, voice_name):
        self.wav_file = None
        self.session = session
        self.input_file = input_file
        self.voice_name = voice_name
        self.models_dir = models_dir
        self.voice_track = 'vocals.wav'
        self.samplerate = models[session['tts_engine']]['samplerate']
        self.output_dir = self.session['voice_dir']
        self.demucs_dir = os.path.join(self.output_dir, 'htdemucs', os.path.splitext(os.path.basename(self.input_file))[0])

    def _validate_format(self):
        file_extension = os.path.splitext(self.input_file)[1].lower()
        if file_extension in voice_formats:
            msg = 'Input file valid'
            return True, msg
        error = f'Unsupported file format: {file_extension}. Supported formats are: {", ".join(voice_formats)}'
        return False, error

    def _convert_to_wav(self):
        try:
            if not self.input_file.lower().endswith(f'_{self.samplerate}.wav'):
                self.wav_file = os.path.join(os.path.dirname(self.input_file), os.path.basename(self.input_file).replace(os.path.splitext(self.input_file)[1], '.wav'))
                process = (
                    ffmpeg
                    .input(self.input_file)
                    .output(self.wav_file, format='wav', ar=self.samplerate, ac=1)
                    .run(overwrite_output=True)
                )
                msg = 'Conversion to .wav format for processing successful'
            else:
                self.wav_file = self.input_file
                msg = 'File is already a .wav format'
            return True, msg
        except ffmpeg.Error as e:
            error = f'convert_to_wav fmpeg.Error: {e.stderr.decode()}'
            raise ValueError(error)
        except Exception as e:
            error = f'_validate_format() error: {e}'
            raise ValueError(error)
        return False, error

    def _detect_background(self):
        try:
            torch_home = os.path.join(self.models_dir, 'hub')
            torch.hub.set_dir(torch_home)
            os.environ['TORCH_HOME'] = torch_home
            energy_threshold = 8800 # to tune if not enough accurate (higher = less sensitive)
            model = vggish()
            model.eval()
            # Preprocess audio to log mel spectrogram
            log_mel_spectrogram = vggish_input.wavfile_to_examples(self.wav_file)
            audio_tensor = log_mel_spectrogram.clone().detach()
            with torch.no_grad():
                embeddings = model(audio_tensor)
            # Calculate total energy
            energy_score = torch.norm(embeddings).item()           
            status = energy_score > energy_threshold
            msg = f'Noise Score: {energy_score:.2f}'
            if status:
                msg = f'{msg}\nBackground noise or music detected. Proceeding voice extraction.'
            else:
                msg = f'{msg}\nNo background noise or music detected. Skipping separation.'
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
            
    def _remove_silences(self):
        try:
            audio = AudioSegment.from_file(self.voice_track)
            trimmed_audio = AudioSegment.silent(duration=0)
            for chunk in audio[::100]:
                if chunk.dBFS > -50:
                    trimmed_audio += chunk
            trimmed_audio.export(self.voice_track, format='wav')
            msg = 'Silences removed'
            return True, msg
        except Exception as e:
            error = f'_remove_silence() error: {e}'
            raise ValueError(e)
            return False, error

    def _normalize_audio(self):
        try:
            error = None
            filter_chain = (
                '[0:a]agate=threshold=-25dB:ratio=1.4:attack=10:release=250,'
                'afftdn=nf=-70,'
                'acompressor=threshold=-20dB:ratio=2:attack=80:release=200:makeup=1dB,'
                'loudnorm=I=-14:TP=-3:LRA=7:linear=true,'
                'equalizer=f=150:t=q:w=2:g=1,'
                'equalizer=f=250:t=q:w=2:g=-3,'
                'equalizer=f=3000:t=q:w=2:g=2,'
                'equalizer=f=5500:t=q:w=2:g=-4,'
                'equalizer=f=9000:t=q:w=2:g=-2,'
                'equalizer=f=12000:t=q:w=2:g=1,'
                'equalizer=f=14000:t=q:w=2:g=2,'
                'equalizer=f=16000:t=q:w=2:g=3,'
                'highpass=f=63,pan=mono|c0=0.5*FL+0.5*FR[audio]'
            )
            for rate in [16000, 24000]:
                output_file = os.path.join(self.session['voice_dir'], f'{self.voice_name}_{rate}.wav')
                try:
                    ffmpeg.input(self.voice_track).output(
                        output_file,
                        acodec='pcm_s16le', ar=rate, ac=1,
                        af=filter_chain
                    ).run(overwrite_output=True)   
                except ffmpeg.Error as e:
                    error = f'_normalize_audio ffmpeg.Error: {e.stderr.decode()}'
                    raise ValueError(error)
                    break
                if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                    error = f'_normalize_audio output error: {output_file} was not created or is empty.'
                    raise ValueError(error)
                    break
            if error is None:
                msg = 'Audio normalization successful!'
                return True, msg
        except FileNotFoundError:
            error = '_normalize_audio() FileNotFoundError: Error: Input file or FFmpeg binary is missing!'
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
            if success:
                print(msg)
                success, msg = self._convert_to_wav()
                if success:
                    print(msg)
                    success, status, msg = self._detect_background()
                    if success:
                        print(msg)
                        if status:
                            print(msg)
                            success, msg = self._demucs_voice()
                        else:
                            self.voice_track = self.wav_file
                        if success:
                            print(msg)
                            success, msg = self._remove_silences()
                            if success:
                                print(msg)
                                success, msg = self._normalize_audio() 
        except Exception as e:
            msg = f'extract_voice() error: {e}'
            raise ValueError(msg)
        shutil.rmtree(self.demucs_dir, ignore_errors=True)
        torch.hub.set_dir(self.models_dir)
        os.environ['TORCH_HOME'] = self.models_dir
        return success, msg