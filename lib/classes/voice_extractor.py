import os
import numpy as np
import regex as re
import scipy.fftpack
import soundfile as sf
import subprocess
import shutil
import torch

from io import BytesIO
from pydub import AudioSegment
from torchvggish import vggish, vggish_input

from lib.conf import voice_formats
from lib.models import XTTSv2, models

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
        
    def _wav2npz(self):
        try:
            npz_dir = os.path.join(self.output_dir, 'bark', self.voice_name)
            os.makedirs(npz_dir, exist_ok=True)
            npz_file = os.path.join(npz_dir, f'{self.voice_name}.npz')
            audio, sr = sf.read(self.final_files[1]) # final_file a 24000hz
            np.savez(npz_file, audio=audio, sample_rate=self.samplerate)
            msg = f"Saved NPZ file: {npz_file}"
            if os.path.exists(npz_file):
                return True, msg
        except Exception as e:
            error = f'_wav2npz() error: {e}'
            raise ValueError(error)   
        return False, error

    def _detect_background(self):
        try:
            torch_home = os.path.join(self.models_dir, 'hub')
            torch.hub.set_dir(torch_home)
            os.environ['TORCH_HOME'] = torch_home
            energy_threshold = 15000 # to tune if not enough accurate (higher = less sensitive)
            model = vggish()
            model.eval()
            # Preprocess audio to log mel spectrogram
            log_mel_spectrogram = vggish_input.wavfile_to_examples(self.wav_file)
            audio_tensor = log_mel_spectrogram.clone().detach()
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

    def _remove_silences(self, audio, silence_threshold):
        final_audio = AudioSegment.silent(duration=0)
        for chunk in audio[::100]:
            if chunk.dBFS > silence_threshold:
                final_audio += chunk
        final_audio.export(self.voice_track, format='wav')
    
    def _trim_and_clean(self):
        try:
            silence_threshold = -60
            audio = AudioSegment.from_file(self.voice_track)
            total_duration = len(audio)  # Total duration in milliseconds
            min_required_duration = 12000
            if total_duration <= min_required_duration:
                msg = f"Audio is only {total_duration/1000:.2f}s long; skipping trimming."
                self._remove_silences(audio, silence_threshold)
                return True, msg
            sample_rate = audio.frame_rate
            chunk_size = 100  # Analyze in 100ms chunks
            # Step 1: Compute Amplitude and Frequency Variation
            amplitude_variations = []
            frequency_variations = []
            time_stamps = []
            for i in range(0, total_duration - chunk_size, chunk_size):
                chunk = audio[i:i + chunk_size]
                if chunk.dBFS > silence_threshold:  # Ignore silence
                    amplitude_variations.append(chunk.dBFS)
                    # FFT to analyze frequency spectrum
                    samples = np.array(chunk.get_array_of_samples())
                    spectrum = np.abs(scipy.fftpack.fft(samples))
                    frequency_variations.append(np.std(spectrum))  # Measure frequency spread
                    time_stamps.append(i)
            # If no significant speech was detected, return an error
            if not amplitude_variations:
                raise ValueError("_trim_and_clean(): No speech detected!")
            # Normalize values for fair weighting
            amplitude_variations = np.array(amplitude_variations)
            frequency_variations = np.array(frequency_variations)
            if len(amplitude_variations) > 1:  # Avoid division errors
                amplitude_variations = (amplitude_variations - np.min(amplitude_variations)) / np.ptp(amplitude_variations)
            else:
                amplitude_variations = np.zeros_like(amplitude_variations)

            if len(frequency_variations) > 1:
                frequency_variations = (frequency_variations - np.min(frequency_variations)) / np.ptp(frequency_variations)
            else:
                frequency_variations = np.zeros_like(frequency_variations)
            # Step 2: Score each segment using combined variation
            score = amplitude_variations + frequency_variations  # Weight both factors equally
            # Find the best segments
            best_index = np.argmax(score)  # Find the chunk with max variation
            best_start = time_stamps[best_index]  # Start time in ms
            best_end = min(best_start + min_required_duration, total_duration)  # End time in ms
            # Step 3: Ensure Trim Happens at Silence Boundaries
            start_adjusted = best_start
            end_adjusted = best_end
            # Adjust start to the nearest silence before it
            for i in range(best_start, max(0, best_start - 2000), -chunk_size):
                if audio[i:i + chunk_size].dBFS < silence_threshold:
                    start_adjusted = i
                    break
            # Adjust end to the nearest silence after it
            for i in range(best_end, min(total_duration, best_end + 2000), chunk_size):
                if audio[i:i + chunk_size].dBFS < silence_threshold:
                    end_adjusted = i
                    break
            # Trim to the adjusted start and end times
            trimmed_audio = audio[start_adjusted:end_adjusted]
            # Step 5: remove silences
            self._remove_silences(trimmed_audio, silence_threshold)
            msg = f"Silences removed, best section extracted from {start_adjusted/1000:.2f}s to {end_adjusted/1000:.2f}s"
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
                            success, msg = self._trim_and_clean()
                            print(msg)
                            if success:
                                success, msg = self._normalize_audio()
                                print(msg)
                                if success:
                                    success, msg = self._wav2npz()
                                    print(msg)
        except Exception as e:
            msg = f'extract_voice() error: {e}'
            raise ValueError(msg)
        shutil.rmtree(self.demucs_dir, ignore_errors=True)
        torch.hub.set_dir(self.models_dir)
        os.environ['TORCH_HOME'] = self.models_dir
        return success, msg