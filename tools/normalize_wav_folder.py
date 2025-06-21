import os
import subprocess
import argparse
import torch

def demucs_voice(wav_file, output_dir, models_dir):
	try:
		# Set TORCH_HOME for demucs
		torch.hub.set_dir(models_dir)
		os.environ['TORCH_HOME'] = models_dir

		# Run demucs subprocess
		cmd = [
			os.path.join('python_env', 'bin', 'demucs'),
			"--verbose",
			"--two-stems=vocals",
			"--out", output_dir,
			wav_file
		]

		print(f"🔄 Running: {' '.join(cmd)}")
		subprocess.run(cmd, check=True)

		# Output folder name is based on input filename
		base_name = os.path.splitext(os.path.basename(wav_file))[0]
		demucs_output_path = os.path.join(output_dir, "demucs", base_name, "vocals.wav")

		if os.path.exists(demucs_output_path):
			print(f"✅ Voice track saved to: {demucs_output_path}")
			return demucs_output_path
		else:
			raise FileNotFoundError(f"Expected output not found: {demucs_output_path}")

	except subprocess.CalledProcessError as e:
		raise RuntimeError(
			f"❌ demucs failed with exit code {e.returncode}.\n"
			f"stdout: {getattr(e, 'output', 'N/A')}\n"
			f"stderr: {getattr(e, 'stderr', 'N/A')}"
		)
	except FileNotFoundError as e:
		raise RuntimeError("❌ 'demucs' command not found. Ensure it is installed and in PATH.") from e
	except Exception as e:
		raise RuntimeError(f"❌ Unexpected error: {e}") from e

def normalize_audio_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.wav'):
                input_file = os.path.join(root, file)
                temp_file = os.path.join(root, 'temp_output.wav')  # Temporary file to avoid overwriting during processing
                models_dir = os.path.join('..', 'models', 'tts')
                demucs_file = demucs_voice(input_file, folder_path, models_dir)
                ffmpeg_cmd = [
                    'ffmpeg', '-i', demucs_file,
                    '-af', 'agate=threshold=-25dB:ratio=1.4:attack=10:release=250,'
                           'afftdn=nf=-70,'
                           'acompressor=threshold=-20dB:ratio=2:attack=80:release=200:makeup=1dB,'
                           'loudnorm=I=-16:TP=-3:LRA=7:linear=true,'
                           'equalizer=f=150:t=q:w=2:g=1,'
                           'equalizer=f=250:t=q:w=2:g=-3,'
                           'equalizer=f=3000:t=q:w=2:g=2,'
                           'equalizer=f=5500:t=q:w=2:g=-4,'
                           'equalizer=f=9000:t=q:w=2:g=-2,'
                           'highpass=f=63',
                    '-y', temp_file
                ]

                try:
                    print(f"Processing file: {input_file}")
                    subprocess.run(ffmpeg_cmd, check=True)
                    os.replace(temp_file, input_file)
                    print(f"File processed and replaced: {input_file}")
                except subprocess.CalledProcessError as e:
                    print(f"Error processing file {input_file}: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")
                finally:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

folder_path = '../assets/bark'
normalize_audio_folder(folder_path)