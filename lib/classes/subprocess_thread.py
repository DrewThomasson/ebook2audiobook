import subprocess
import threading
import queue
import os
import timedef export_audio(ffmpeg_combined_audio, ffmpeg_metadata_file, ffmpeg_final_file):
    try:
        if session['cancellation_requested']:
            print("Cancel requested")
            return False

        total_duration = get_audio_duration(ffmpeg_combined_audio)
        print(f"Total duration: {total_duration:.2f} s")

        is_gui = session.get('is_gui_process', False)
        progress_bar = gr.Progress(track_tqdm=False) if is_gui else None
        if is_gui:
            progress_bar(0, desc=f"Exporting → {os.path.basename(ffmpeg_final_file)}")

        ffmpeg_cmd = [shutil.which('ffmpeg'), '-hide_banner', '-y', '-i', ffmpeg_combined_audio]
        if session['output_format'] == 'wav':
            ffmpeg_cmd += ['-map', '0:a', '-ar', '44100', '-sample_fmt', 's16']
        elif session['output_format'] == 'aac':
            ffmpeg_cmd += ['-c:a', 'aac', '-b:a', '192k', '-ar', '44100']
        elif session['output_format'] == 'flac':
            ffmpeg_cmd += ['-c:a', 'flac', '-compression_level', '5', '-ar', '44100', '-sample_fmt', 's16']
        else:
            ffmpeg_cmd += ['-f', 'ffmetadata', '-i', ffmpeg_metadata_file, '-map', '0:a']
            if session['output_format'] in ['m4a', 'm4b', 'mp4', 'mov']:
                ffmpeg_cmd += ['-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-movflags', '+faststart+use_metadata_tags']
            elif session['output_format'] == 'mp3':
                ffmpeg_cmd += ['-c:a', 'libmp3lame', '-b:a', '192k', '-ar', '44100']
            elif session['output_format'] == 'webm':
                ffmpeg_cmd += ['-c:a', 'libopus', '-b:a', '192k', '-ar', '48000']
            elif session['output_format'] == 'ogg':
                ffmpeg_cmd += ['-c:a', 'libopus', '-compression_level', '0', '-b:a', '192k', '-ar', '48000']
            ffmpeg_cmd += ['-map_metadata', '1']
        ffmpeg_cmd += [
            '-af', 'loudnorm=I=-16:LRA=11:TP=-1.5,afftdn=nf=-70',
            '-threads', '1',
            '-progress', 'pipe:1',
            ffmpeg_final_file
        ]

        from lib.classes.subprocess_thread import SubprocessThread
        runner = SubprocessThread(ffmpeg_cmd)
        time_pattern = re.compile(r"out_time_ms=(\d+)")
        last_gui_update = 0.0
        last_print = 0.0

        for _, stderr in runner.start():
            if session['cancellation_requested']:
                print("\nCancel requested → stopping FFmpeg...")
                runner.stop()
                if is_gui and progress_bar:
                    progress_bar(0, desc="Cancelled")
                return False

            if stderr:
                match = time_pattern.search(stderr)
                if match:
                    ms = int(match.group(1))
                    sec = ms / 1_000_000
                    if total_duration > 0:
                        progress_value = min(1.0, sec / total_duration)
                        if progress_value - last_print >= 0.05:
                            print(f"\rExport progress: {progress_value * 100:.1f}%", end='', flush=True)
                            last_print = progress_value
                        if is_gui and progress_bar and progress_value - last_gui_update >= 0.01:
                            progress_bar(progress_value, desc=f"Encoding → {int(progress_value * 100)}%")
                            last_gui_update = progress_value

        print("\rExport progress: 100.0%")
        if is_gui and progress_bar:
            progress_bar(1.0, desc="Completed")

        if runner.return_code and runner.return_code != 0:
            print(f"FFmpeg failed ({runner.return_code})")
            if is_gui and progress_bar:
                progress_bar(0, desc="Error")
            return False

        if session['output_format'] in ['mp3', 'm4a', 'm4b', 'mp4']:
            if session['cover'] is not None:
                cover_path = session['cover']
                msg = f'Adding cover {cover_path} into the final audiobook file...'
                print(msg)
                if session['output_format'] == 'mp3':
                    from mutagen.mp3 import MP3
                    from mutagen.id3 import ID3, APIC, error
                    audio = MP3(ffmpeg_final_file, ID3=ID3)
                    try:
                        audio.add_tags()
                    except error:
                        pass
                    with open(cover_path, 'rb') as img:
                        audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=img.read()))
                elif session['output_format'] in ['mp4', 'm4a', 'm4b']:
                    from mutagen.mp4 import MP4, MP4Cover
                    audio = MP4(ffmpeg_final_file)
                    with open(cover_path, 'rb') as f:
                        cover_data = f.read()
                    audio["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
                if audio:
                    audio.save()

        final_vtt = f"{Path(ffmpeg_final_file).stem}.vtt"
        proc_vtt_path = os.path.join(session['process_dir'], final_vtt)
        final_vtt_path = os.path.join(session['audiobooks_dir'], final_vtt)
        shutil.move(proc_vtt_path, final_vtt_path)
        print("FFmpeg export complete.")
        return True

    except Exception as e:
        print(f"Export failed: {e}")
        if session.get('is_gui_process'):
            gr.Progress()(0, desc="Error")
        return False


class SubprocessThread(object):

    def __init__(self, cmd: []):
        self.cmd = cmd
        self.return_code = None
        self.process = None # type: subprocess.Popen
        self.run_time = 0


    @property
    def _default_popen_kwargs(self):
        return {
            "env": os.environ.copy(),
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "shell": True,
            "universal_newlines": True,
            "bufsize": 1,
        }


    def _watch_output(self, process: subprocess.Popen, queue):
        for line in iter(process.stderr.readline, ""):
            queue.put(line)
            if process.poll() is not None:
                return

    @property
    def stdout(self):
        return self.process.stdout

    @property
    def stderr(self):
        return self.process.stderr


    def start(self, wait_limit = 15):

        start_time = time.time()

        pargs = self._default_popen_kwargs
        if self.cwd is not None:
            pargs['cwd'] = self.cwd

        self.process = subprocess.Popen(self.cmd, **pargs)
        self.returned = None
        last_output = time.time()
        q = queue.Queue()

        t = threading.Thread(target=self._watch_output, args=(self.process, q,))
        t.daemon = True
        t.start()

        while self.returned is None:
            self.returned = self.process.poll()

            delay = last_output-time.time()
            if self.returned is None:
                stdout = f"{last_output-time.time()} waited"
                try:
                    stderr = q.get_nowait()
                except queue.Empty:
                    time.sleep(1)
                else:
                    yield stdout, stderr
                    last_output = time.time()

            if delay > wait_limit:
                print("Waited 15 seconds, breaking")
                break

        self.run_time = time.time() - start_time