import os, subprocess, shutil, tempfile, gradio as gr

from typing import Any
from pydub import AudioSegment, silence
from pydub.silence import detect_nonsilent
from pathlib import Path
            
from lib.classes.tts_engines.common.audio import get_audio_duration
from lib.classes.tts_engines.common.hf_download import hf_download
from lib.classes.subprocess_pipe import SubprocessPipe
from lib.conf import systems, devices, voice_formats, default_audio_proc_samplerate, tts_dir
from lib.conf_models import TTS_ENGINES, default_voice_separation_model
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
        # demucs and pyannote are torch models and torch has no Vulkan device: moving one there segfaults in Module.to()
        # (+vulkan wheel, macOS MoltenVK). Only torch devices pass, as in InterludeGenerator; anything else runs on CPU
        is_torch_device = resolved_device_name in {'CUDA', 'MPS', 'XPU'}
        self.device = resolved_device['proc'] if is_torch_device and resolved_device.get('found') else devices['CPU']['proc']
        self.output_dir = self.session['voice_dir']
        self.final_voice_file = final_voice_file if final_voice_file is not None else os.path.join(self.session['voice_dir'], f'{self.voice_name}.wav')
        self.silence_threshold = -60
        self.is_gui_process = session['is_gui_process']
        if self.is_gui_process:
            self.progress_bar=gr.Progress(track_tqdm=False)
        models = load_engine_presets(session['tts_engine'])
        self.samplerate = models[session['fine_tuned']]['samplerate']
        # one private scratch dir per run beside the final file: work files never share a name with an existing voice
        # or a concurrent run, and os.replace() into the final file never crosses mounts. The final file is only written
        # by that last os.replace(): never the ffmpeg output of its own input, never a half-processed voice
        final_dir = os.path.dirname(self.final_voice_file)
        os.makedirs(final_dir, exist_ok=True)
        # fixed short prefix: the dir name never grows with voice_name (NAME_MAX, windows MAX_PATH)
        self.work_dir = tempfile.mkdtemp(prefix='.e2a_voice_', dir=final_dir)
        self.demucs_dir = os.path.join(self.work_dir, 'htdemucs')
        self.voice_track = os.path.join(self.demucs_dir, 'vocals.wav')
        self.work_voice_file = os.path.join(self.work_dir, 'work.wav')
        self.proc_voice_file = os.path.join(self.work_dir, 'proc.wav')
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
            status, report = detector.detect()
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

    def _load_demucs(self)->Any:
        import torch
        from demucs.pretrained import get_model, REMOTE_ROOT, LocalRepo, BagOnlyRepo, AnyModelRepo
        name = default_voice_separation_model['name']
        file = default_voice_separation_model['file']
        repo_id = default_voice_separation_model['repo']
        # already in torch.hub's cache from an earlier run on the official host: no download at all
        if os.path.isfile(os.path.join(torch.hub.get_dir(), 'checkpoints', file)):
            return get_model(name=name)
        try:
            model_path = hf_download(self.progress_bar if self.is_gui_process else None, legends['msg_extracting_voice'], repo_id=repo_id, filename=file, cache_dir=tts_dir)
            # LocalRepo checks the sha256 prefix carried by the file name, the bag yaml (signatures, weights, segment)
            # ships with demucs itself: same model as get_model(name), only the checkpoint comes from the HF mirror
            model_repo = LocalRepo(Path(model_path).parent)
            return AnyModelRepo(model_repo, BagOnlyRepo(REMOTE_ROOT, model_repo)).get_model(name)
        except Exception as e:
            print(f'_load_demucs() {repo_id} error: {e}, trying the official demucs host')
        return get_model(name=name)

    def _demucs_voice(self)->tuple[bool, str]:
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
            model = self._load_demucs()
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

    def _sentence_bounds(self, audio:AudioSegment, silence_threshold:int, start:int, end:int, reach:int, min_pause_len:int=150, sentence_pause_len:int=600, break_ratio:float=0.75, edge_pad:int=200)->tuple[int, int]:
        # moves [start, end] onto sentence breaks so the clip never starts or ends inside a sentence: start up to
        # 2 * reach earlier or reach later, end up to reach earlier or 2 * reach later, the clip never shorter than
        # end - start nor longer by more than 2 * reach. There is no text here, so a sentence break is a long pause:
        # at least break_ratio of the longest pause around, or of sentence_pause_len when that is shorter
        # (_remove_silences keeps at most 2 * 300 ms of any silence, so those are the pauses it shortened).
        # Each edge is ranked: sentence break or audio edge 2, shorter pause 1, quietest 50 ms (a gap between words) 0.
        # The pair ranked best wins, the end first on a tie, then the pair moved the least
        import numpy as np
        window = end - start
        total_duration = len(audio)
        samples = np.array(audio.get_array_of_samples()).astype(np.float32)
        if audio.channels > 1:
            samples = samples.reshape((-1, audio.channels)).mean(axis=1)
        frame_len = max(1, audio.frame_rate // 100)
        frame_ms = frame_len * 1000.0 / audio.frame_rate
        total_frames = len(samples) // frame_len
        if total_frames == 0 or reach <= 0:
            return start, end
        frames = samples[:total_frames * frame_len].reshape(total_frames, frame_len)
        full_scale = float(1 << (8 * audio.sample_width - 1))
        rms = np.sqrt(np.mean(np.square(frames), axis=1)) / full_scale
        # floored at -100 dBFS: digital silence (demucs vocals) would drag the noise floor percentile down to -inf
        frames_db = 20.0 * np.log10(np.maximum(rms, 1e-5))
        floor_db = float(np.percentile(frames_db, 10))
        peak_db = float(np.percentile(frames_db, 95))
        # a quarter of the way from the noise floor to the speech peaks, never under silence_threshold: a voice that
        # did not go through demucs keeps its room noise, often above silence_threshold, between its sentences
        pause_db = max(float(silence_threshold), floor_db + (peak_db - floor_db) * 0.25)
        is_pause = np.concatenate(([False], frames_db < pause_db, [False]))
        edges = np.flatnonzero(np.diff(is_pause.astype(np.int8)))
        min_frames = int(np.ceil(min_pause_len / frame_ms))
        search_lo = max(0, start - 2 * reach)
        search_hi = min(total_duration, end + 2 * reach)
        pauses = []
        for first, last in zip(edges[0::2], edges[1::2]):
            pause_start = int(first * frame_ms)
            pause_end = int(last * frame_ms)
            if last - first >= min_frames and pause_end >= search_lo and pause_start <= search_hi:
                pauses.append((pause_start, pause_end))
        break_len = break_ratio * min(max((pause_end - pause_start for pause_start, pause_end in pauses), default=0), sentence_pause_len)

        def quietest(lo:int, hi:int, default:int)->int:
            lo_frame = max(0, int(lo / frame_ms))
            hi_frame = min(total_frames, int(hi / frame_ms) + 1)
            if hi_frame - lo_frame < 5:
                return default
            smoothed = np.convolve(frames_db[lo_frame:hi_frame], np.ones(5) / 5, mode='valid')
            return min(max(int((lo_frame + int(np.argmin(smoothed)) + 2.5) * frame_ms), lo), hi)

        def cuts(lo:int, hi:int, is_start:bool)->list[tuple[int, int]]:
            # (position, rank) in [lo, hi]. A clip starting in a pause keeps edge_pad ms of it before its first word,
            # a clip ending in one edge_pad ms after its last word. The quietest 50 ms within reach of the window, on
            # its outer side, always makes a valid pair with the other edge's
            if is_start:
                result = [(quietest(max(0, start - reach), start, start), 0)]
                if lo == 0:
                    result.append((0, 2))
            else:
                result = [(quietest(end, min(total_duration, end + reach), end), 0)]
                if hi == total_duration:
                    result.append((total_duration, 2))
            for pause_start, pause_end in pauses:
                if pause_end >= lo and pause_start <= hi:
                    pos = max(pause_start, pause_end - edge_pad) if is_start else min(pause_end, pause_start + edge_pad)
                    result.append((min(max(pos, lo), hi), 2 if pause_end - pause_start >= break_len else 1))
            return result

        start_cuts = cuts(search_lo, min(total_duration, start + reach), True)
        end_cuts = cuts(max(0, end - reach), search_hi, False)
        best = (-1, -1, 0), start, end
        for new_start, start_rank in start_cuts:
            for new_end, end_rank in end_cuts:
                if window <= new_end - new_start <= window + 2 * reach:
                    key = (start_rank + end_rank, end_rank, -abs(new_start - start) - abs(new_end - end))
                    if key > best[0]:
                        best = key, new_start, new_end
        return best[1], best[2]
    
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
                # the window is cut at fixed hops, often inside a word: both edges move to the nearest sentence break
                best_start, best_end = self._sentence_bounds(audio, silence_threshold, best_start, best_end, hop)
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
        shutil.rmtree(self.work_dir, ignore_errors = True)
        return result, msg
