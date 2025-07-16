import os
import sys
import subprocess
import argparse
import torch
import shutil

def demucs_voice(wav_file, output_dir, models_dir):
	try:
		# Set TORCH_HOME for demucs
		torch.hub.set_dir(models_dir)
		os.environ['TORCH_HOME'] = models_dir
		# Run demucs subprocess
		cmd = [
			os.path.join('..', 'python_env', 'bin', 'demucs'),
			"--verbose",
			"--two-stems=vocals",
			"--out", output_dir,
			wav_file
		]
		print(f"🔄 Running: {' '.join(cmd)}")
		subprocess.run(cmd, check=True)
		# Output folder name is based on input filename
		base_name = os.path.splitext(os.path.basename(wav_file))[0]
		demucs_output_path = os.path.join(output_dir, "htdemucs", base_name, "vocals.wav")
		if os.path.exists(demucs_output_path):
			print(f"✅ Voice track saved to: {demucs_output_path}")
			return demucs_output_path
		else:
			raise FileNotFoundError(f"Expected output not found: {demucs_output_path}")
	except subprocess.CalledProcessError as e:
		raise RuntimeError(
			f"demucs failed with exit code {e.returncode}.\n"
			f"stdout: {getattr(e, 'output', 'N/A')}\n"
			f"stderr: {getattr(e, 'stderr', 'N/A')}"
		)
	except FileNotFoundError as e:
		raise RuntimeError(f"FileNotFoundError: {e}")
	except Exception as e:
		raise RuntimeError(f"Unexpected error: {e}")

def normalize_audio_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.wav'):
                input_file = os.path.join(root, file)
                models_dir = os.path.join('..', 'models', 'tts')
                #demucs_file = demucs_voice(input_file, folder_path, models_dir)
                process_file = os.path.join(root, 'temp_output.wav')  # Temporary file to avoid overwriting during processing
                ffmpeg_cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', input_file]
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
                    '-ar', '24000',
                    '-y', process_file
                ]
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
                        error = f'normalize_audio(): process.returncode: {process.returncode}'
                        break
                    elif not os.path.exists(process_file) or os.path.getsize(process_file) == 0:
                        error = f'normalize_audio() error: {process_file} was not created or is empty.'
                        break
                    else:
                        os.replace(process_file, input_file)
                        print(f"File processed and replaced: {input_file}")
                except subprocess.CalledProcessError as e:
                    error = f'_normalize_audio() ffmpeg.Error: {e.stderr.decode()}'
                    break
                except subprocess.CalledProcessError as e:
                    print(f"Error processing file {input_file}: {e}")
                    break
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    break

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print(f"Usage: python {os.path.basename(__file__)} <folder_path>")
		sys.exit(1)
	folder_path = os.path.abspath(sys.argv[1])
	normalize_audio_folder(folder_path)