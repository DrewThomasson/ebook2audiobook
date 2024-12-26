import os
import subprocess

def normalize_audio_file(input_file, target_folder):
    # Ensure the target folder exists
    os.makedirs(target_folder, exist_ok=True)

    # Extract the filename from the input file
    filename = os.path.basename(input_file)

    # Construct the output file path in the target folder
    output_file = os.path.join(target_folder, filename)

    # FFmpeg command
    ffmpeg_cmd = [
        'ffmpeg', '-i', input_file,
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
        # Run FFmpeg command
        print(f"Processing file: {input_file}")
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Processed file saved to: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing file {input_file}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example Usage
input_file = '../tmp/file.wav'  # Path to the uploaded source file
target_folder = '../tmp/output.wav'  # Target folder to save the output
normalize_audio_file(input_file, target_folder)