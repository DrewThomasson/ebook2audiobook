import os, subprocess, shutil, gradio as gr

from typing import Any
from pydub import AudioSegment, silence
from pydub.silence import detect_nonsilent
from pathlib import Path
            
from lib.classes.tts_engines.common.audio import get_audio_duration
from lib.classes.subprocess_pipe import SubprocessPipe
from lib.conf import systems, devices, voice_formats, default_audio_proc_samplerate
from lib.conf_models import TTS_ENGINES
from lib.lang import legends

class VoiceExtractor:

    def __init__(self, session:Any, voice_file:str, voice_name:str, final_voice_file:str|None=None)->None:
        from lib.classes.tts_engines.common.preset_loader import load_engine_presets
        self.wav_file = None
        self.session = session
        self.voice_file = voice_file
        self.voice_name = voice_name
        session_device = str(session.get('device', 'CPU')).upper()
        resolved_device_name = 'CUDA' if session_device in {'CUDA', 'ROCM', 'JETSON'} else session_device
        resolved_device = devices.get(resolved_device_name, devices['CPU'])
        self.device = resolved_device['proc'] if resolved_device.get('found') else devices['CPU']['proc']
        self.output_dir = self.session['voice_dir']
        self.demucs_dir = os.path.join(self.output_dir,'htdemucs', voice_name)
        self.voice_track = os.path.join(self.demucs_dir, 'vocals.wav')
        self.final_voice_file = final_voice_file if final_voice_file is not None else os.path.join(self.session['voice_dir'], f'{self.voice_name}.wav')
        # work files sit next to the final file: no stray voice left in voice_dir, and os.replace() never crosses mounts.
        # the final file is only written by the last os.replace(): never the ffmpeg output of its own input, never a half-processed voice
        self.work_voice_file = os.path.join(os.path.dirname(self.final_voice_file), f'{self.voice_name}_work.wav')
        self.proc_voice_file = os.path.join(os.path.dirname(self.final_voice_file), f'{self.voice_name}_proc.wav')
        self.silence_threshold = -60
        self.is_gui_process = session['is_gui_process']
        if self.is_gui_process:
            self.progress_bar=gr.Progress(track_tqdm=False)
        models = load_engine_presets(session['tts_engine'])
        self.samplerate = models[session['fine_tuned']]['samplerate']
        os.makedirs(self.demucs_dir, exist_ok=True)

    def _validate_format(self)->tuple[bool,str]:
        file_extension = os.path.splitext(self.voice_file)[1].lower()
        if file_extension in voice_formats:
            msg = legends['msg_input_valid']
            return True,msg
        error = legends['error_unsupported_file_format'].format(ext=file_extension)
        return False,error

    def _convert2wav(self)->tuple[bool, str]:
        try:
            msg = legends['msg_convert_wav']
            print(msg)
            if self.is_gui_process:
                self.progress_bar(1, desc=msg)
            self.wav_file = self.work_voice_file
            cmd = [
                shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', self.voice_file,
                '-ac', '1', '-y', self.wav_file
            ]   
            proc_pipe = SubprocessPipe(cmd, is_gui_process=self.is_gui_process, total_duration=get_audio_duration(self.voice_file), msg=legends['msg_demux'])
            if not os.path.exists(self.wav_file) or os.path.getsize(self.wav_file) == 0:
                error = f'_convert2wav output error: {self.wav_file} was not created or is empty.'
            else:
                if proc_pipe.result:
                    msg = legends['msg_wav_ok']
                    return True, msg
                else:
                    error = f'_convert2wav() SubprocessPipe error'
        except subprocess.CalledProcessError as e:
            try:
                stderr_text = e.stderr.decode('utf-8', errors='replace')
            except Exception:
                stderr_text = str(e)
            error = f'_convert2wav ffmpeg.Error: {stderr_text}'
        except Exception as e:
            error = f'_convert2wav() error: {e}'
        return False, error

    def _detect_background(self)->tuple[bool,bool,str]:
        try:
            from lib.classes.background_detector import pyannote_patch, BackgroundDetector
            pyannote_patch()
            msg = legends['msg_detecting_background']
            print(msg)
            if self.is_gui_process:
                self.progress_bar(1, desc=msg)
            detector = BackgroundDetector(wav_file=self.wav_file, device=self.device)
            status, report = detector.detect(vad_ratio_thresh=0.27)
            if report:
                print(report)
                if status:
                    msg = legends['msg_background_detected']
                else:
                    msg = legends['msg_no_background']
                return True, status, msg
            else:
                error = 'detector.detect() could not analyze the audio file'
                return False, False, error
        except Exception as e:
            error = f'_detect_background() error: {e}'
            print(error)
        return False, False, error

    def _demucs_voice(self)->tuple[bool, str]:
        from demucs.pretrained import get_model
        from demucs.apply import apply_model
        from demucs.audio import AudioFile

        def demucs_callback(d: dict):
            nonlocal last_percent
            offset = d.get("segment_offset")
            if offset is not None:
                progress_state["current"] = max(progress_state["current"], offset)
                percent = min(progress_state["current"] / total_length, 1.0)
                if percent - last_percent >= 0.01:
                    last_percent = percent
                    print(f"\r[Demucs] {percent*100:.2f}%", end="", flush=True)
                    if self.is_gui_process:
                        self.progress_bar(percent, desc=msg)

        error = '_demucs_voice() error'
        try:
            system = self.session['system']
            last_percent = 0.0
            msg = legends['msg_extracting_voice']
            if self.is_gui_process:
                self.progress_bar(0.0, desc=msg)
            model = get_model(name="htdemucs")
            model.to(self.device)
            model.eval()
            audio_result = AudioFile(self.wav_file).read(
                streams=0,
                samplerate=model.samplerate,
                channels=model.audio_channels
            )
            if isinstance(audio_result, (tuple, list)):
                wav = audio_result[0]
            else:
                wav = audio_result
            if wav.dim() == 2:
                wav = wav.unsqueeze(0)
            wav = wav.to(self.device)
            total_length = wav.shape[-1]
            progress_state = {"current": 0}
            result = apply_model(
                model,
                wav,
                device=self.device,
                split=True,
                progress=False,
                callback=demucs_callback,
                callback_arg={}
            )
            if self.is_gui_process:
                self.progress_bar(1.0, desc=msg)
            print("\r[Demucs] 100.00%")
            sources = result[0] if isinstance(result, (tuple, list)) else result
            vocals_idx = model.sources.index("vocals")
            vocals = sources[0, vocals_idx]
            if vocals.dim() > 1 and vocals.shape[0] > 1:
                vocals = vocals.mean(dim=0, keepdim=True)
            audio_np = vocals.detach().cpu().numpy()
            audio_np = audio_np.T
            audio_np = (audio_np * 32767.0).clip(-32768, 32767).astype("int16")
            audio_segment = AudioSegment(
                audio_np.tobytes(),
                frame_rate=model.samplerate,
                sample_width=2,
                channels=audio_np.shape[1] if audio_np.ndim > 1 else 1
            )
            audio_segment.export(self.voice_track, format="wav")
            msg = legends['msg_done']
            return True, msg
        except Exception as e:
            error = f'_demucs_voice() error: {str(e)}'
        return False, error


    def _remove_silences(self, audio:AudioSegment, silence_threshold:int, min_silence_len:int=200, keep_silence:int=300)->AudioSegment:
        msg = legends['msg_removing_empty_audio']
        print(msg)
        if self.is_gui_process:
            self.progress_bar(0, desc=msg)
        chunks = silence.split_on_silence(
            audio,
            min_silence_len = min_silence_len,
            silence_thresh = silence_threshold,
            keep_silence = keep_silence
        )
        if not chunks:
            return audio
        final_audio = AudioSegment.silent(duration = 0)
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            final_audio += chunk
            if self.is_gui_process:
                percent = int(i / max(1, total - 1))
                self.progress_bar(percent, desc=msg)
        final_audio.export(self.voice_track, format = "wav")
        return final_audio
    
    def _trim_and_clean(self, silence_threshold:int, min_silence_len:int=200, chunk_size:int=100)->tuple[bool, str]:
        try:
            import numpy as np
            audio = AudioSegment.from_file(self.voice_track)
            audio = self._remove_silences(
                audio,
                silence_threshold,
                min_silence_len = min_silence_len
            )
            total_duration = len(audio)
            min_required_duration = 20000 if self.session["tts_engine"] == TTS_ENGINES["BARK"] else 12000
            msg = legends['msg_removing_long_pauses']
            print(msg)
            if self.is_gui_process:
                self.progress_bar(0, desc=msg)
            if total_duration <= min_required_duration:
                msg = legends['msg_audio_too_short'].format(seconds=f'{total_duration / 1000:.2f}')
                return True, msg
            if total_duration > min_required_duration * 2:
                window = min_required_duration
                hop = max(1, window // 4)
                best_score = -float("inf")
                best_start = 0
                total_steps = ((total_duration - window) // hop) + 1
                min_dbfs = silence_threshold + 10
                for i, start in enumerate(range(0, total_duration - window + 1, hop)):
                    chunk = audio[start:start + window]
                    if chunk.dBFS == float("-inf") or chunk.dBFS < min_dbfs:
                        continue
                    samples = np.array(chunk.get_array_of_samples()).astype(np.float32)
                    if chunk.channels > 1:
                        samples = samples.reshape((-1, chunk.channels)).mean(axis=1)
                    spectrum = np.abs(np.fft.rfft(samples))
                    p = spectrum / (np.sum(spectrum) + 1e-10)
                    entropy = -np.sum(p * np.log2(p + 1e-10))
                    if entropy > best_score:
                        best_score = entropy
                        best_start = start
                    if self.is_gui_process:
                        percent = int(i / max(1, total_steps - 1))
                        self.progress_bar(percent, desc=msg)
                best_end = best_start + window
                nonsilent = detect_nonsilent(
                    audio,
                    min_silence_len = min_silence_len,
                    silence_thresh = silence_threshold
                )
                if nonsilent:
                    best_start = max(best_start, nonsilent[0][0])
                    best_end = min(best_end, nonsilent[-1][1])
            else:
                best_start = 0
                best_end = total_duration
            trimmed_audio = audio[best_start:best_end]
            trimmed_audio.export(self.voice_track, format = "wav")
            msg = legends['msg_audio_trimmed']
            return True, msg
        except Exception as e:
            error = f"_trim_and_clean() error: {e}"
            print(error)
            return False, error

    def normalize_audio(self, src_file:str, proc_file:str, dst_file:str)->tuple[bool, str]:
        try:
            import json, math
            msg = legends['msg_normalize_audio']
            print(msg)
            if self.is_gui_process:
                self.progress_bar(0, desc=msg)
            target_i = -16.0
            target_tp = -1.5
            # pass 1: measure only (no audio written) to get integrated loudness + true peak
            analyze_cmd = [
                shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', src_file,
                '-af', f'loudnorm=I={target_i}:TP={target_tp}:print_format=json',
                '-f', 'null', '-'
            ]
            analyze = subprocess.run(analyze_cmd, capture_output=True, text=True, errors='replace')
            stderr_text = analyze.stderr or ''
            gain_db = 0.0
            try:
                stats = json.loads(stderr_text[stderr_text.rindex('{'):stderr_text.rindex('}') + 1])
                input_i = float(stats['input_i'])
                input_tp = float(stats['input_tp'])
                if math.isfinite(input_i) and math.isfinite(input_tp):
                    # one static gain for the whole file, capped so the true peak stays under target_tp
                    gain_db = min(target_i - input_i, target_tp - input_tp)
            except Exception as e:
                print(f'normalize_audio() loudness analysis failed, keeping original level: {e}')
            # pass 2: linear time-invariant only -> rumble cut below any voice f0 + one constant gain
            cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-progress', 'pipe:2', '-i', src_file]
            filter_complex = (
                'highpass=f=40:poles=2,'
                f'volume={gain_db:.2f}dB[audio]'
            )
            cmd += [
                '-filter_complex', filter_complex,
                '-map', '[audio]',
                '-ar', f'{default_audio_proc_samplerate}',
                '-y', proc_file
            ]
            try:
                proc_pipe = SubprocessPipe(cmd, is_gui_process=self.is_gui_process, total_duration=get_audio_duration(src_file), msg=legends['msg_normalize'])
                if not os.path.exists(proc_file) or os.path.getsize(proc_file) == 0:
                    error = f'normalize_audio() error: {proc_file} was not created or is empty.'
                else:
                    if proc_pipe.result:
                        if proc_file != dst_file:
                            os.replace(proc_file, dst_file)
                            shutil.rmtree(self.demucs_dir, ignore_errors = True)
                        msg = legends['msg_normalization_ok']
                        return True, msg
                    else:
                        error = f'normalize_audio() SubprocessPipe Error.'
            except subprocess.CalledProcessError as e:
                stderr = getattr(e, "stderr", None)
                if isinstance(stderr, (bytes, bytearray)):
                    stderr_msg = stderr.decode(errors="replace")
                else:
                    stderr_msg = str(e)
                error = f'normalize_audio() ffmpeg.Error: {stderr_msg}'
        except FileNotFoundError as e:
            error = f'normalize_audio() FileNotFoundError: {e}. Input file or FFmpeg PATH not found!'
        except Exception as e:
            error = f'normalize_audio() error: {e}'
        return False, error

    def extract_voice(self)->tuple[bool,str|None]:
        result = 0
        msg = None
        try:
            result, msg = self._validate_format()
            print(msg)
            if self.is_gui_process:
                self.progress_bar(int(result), desc=msg)
            if result:
                result, msg = self._convert2wav()
                print(msg)
                if self.is_gui_process:
                    self.progress_bar(int(result), desc=msg)
                self.voice_track = self.wav_file
            if result:
                result, status, msg = self._detect_background()
                print(msg)
                if self.is_gui_process:
                    self.progress_bar(int(result), desc=msg)
                if result and status:
                    self.voice_track = os.path.join(self.demucs_dir, 'vocals.wav')
                    result, msg = self._demucs_voice()
                    print(msg)
                    if self.is_gui_process:
                        self.progress_bar(int(result), desc=msg)
            if result:
                result, msg = self._trim_and_clean(self.silence_threshold)
                print(msg)
                if self.is_gui_process:
                    self.progress_bar(int(result), desc=msg)
            if result:
                result, msg = self.normalize_audio(self.voice_track, self.proc_voice_file, self.final_voice_file)
                print(msg)
                if self.is_gui_process:
                    self.progress_bar(int(result), desc=msg)
                if result:
                    self.voice_track = self.final_voice_file
            if result and os.path.abspath(self.voice_track) != os.path.abspath(self.final_voice_file):
                shutil.copyfile(self.voice_track, self.final_voice_file)
        except Exception as e:
            result = False
            msg = f'extract_voice() error: {e}'
        shutil.rmtree(self.demucs_dir, ignore_errors = True)
        for work_file in (self.work_voice_file, self.proc_voice_file):
            try:
                if os.path.exists(work_file):
                    os.remove(work_file)
            except OSError as e:
                print(f'extract_voice() could not remove {work_file}: {e}')
        return result, msg
