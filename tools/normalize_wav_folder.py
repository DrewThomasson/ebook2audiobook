import os
import subprocess

def normalize_audio_folder(folder_path):
    # Iterate through all files and directories recursively
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.wav'):
                input_file = os.path.join(root, file)
                temp_file = os.path.join(root, 'temp_output.wav')  # Temporary file to avoid overwriting during processing

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
                    '-y', temp_file
                ]

                try:
                    # Run FFmpeg command
                    print(f"Processing file: {input_file}")
                    subprocess.run(ffmpeg_cmd, check=True)

                    # Replace the original file with the processed file
                    os.replace(temp_file, input_file)
                    print(f"File processed and replaced: {input_file}")
                except subprocess.CalledProcessError as e:
                    print(f"Error processing file {input_file}: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")
                finally:
                    # Clean up temporary file if it exists
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

# Specify the folder to search
folder_path = '../voices'
normalize_audio_folder(folder_path)