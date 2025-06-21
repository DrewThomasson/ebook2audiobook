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
		demucs_output_path = os.path.join(output_dir, "htdemucs", "vocals.wav")

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

def normalize_audio_file(input_file, output_file):
    models_dir = os.path.join('..', 'models', 'tts')
    demucs_file = demucs_voice(input_file, root_dir, models_dir)
    ffmpeg_cmd = [
        'ffmpeg', '-i', demucs_file,
        '-af', 'agate=threshold=-25dB:ratio=1.4:attack=10:release=250,'
               'afftdn=nf=-70,'
               'acompressor=threshold=-20dB:ratio=2:attack=80:release=200:makeup=1dB,'
               'loudnorm=I=-16:TP=-3:LRA=7:linear=true,'
               'equalizer=f=250:t=q:w=2:g=-3,'
               'equalizer=f=150:t=q:w=2:g=2,'
               'equalizer=f=3000:t=q:w=2:g=3,'
               'equalizer=f=5500:t=q:w=2:g=-4,'
               'equalizer=f=9000:t=q:w=2:g=-2,'
               'highpass=f=63',
        '-y', output_file
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Processed file saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing file {input_file}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example Usage
root_dir = os.path.join('..', 'voices')
input_file = os.path.join(root_dir, 'eng', 'adult', 'male', 'Jamie.wav')
output_file = os.path.join(root_dir, 'eng', 'adult', 'male', 'Jamie2.wav')
normalize_audio_file(input_file, output_file)