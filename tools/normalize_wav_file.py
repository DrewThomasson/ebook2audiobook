import os
import sys
import subprocess
import argparse
import shutil
import torch

def demucs_voice(wav_file, output_dir, models_dir):
    try:
        # Set TORCH_HOME for demucs
        torch.hub.set_dir(models_dir)
        os.environ['TORCH_HOME'] = models_dir
        demucs_app = shutil.which('demucs')
        if not demucs_app:
            demucs_app = os.path.join('..', 'python_env', 'Scripts', 'demucs')
        # Run demucs subprocess
        cmd = [
            demucs_app,
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
    output_dir = os.path.dirname(output_file)
    #demucs_file = demucs_voice(input_file, output_dir, models_dir)
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
        '-y', output_file
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
        elif not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            error = f'normalize_audio() error: {output_file} was not created or is empty.'
        else:
            print(f"File denoised and normalized!: {output_file}")
    except subprocess.CalledProcessError as e:
        error = f'_normalize_audio() ffmpeg.Error: {e.stderr.decode()}'
    except subprocess.CalledProcessError as e:
        print(f"Error processing file {input_file}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {os.path.basename(__file__)} <input_file> <output_file>")
        sys.exit(1)
    input_file = os.path.abspath(sys.argv[1])
    output_file = os.path.abspath(sys.argv[2])
    normalize_audio_file(input_file, output_file)
