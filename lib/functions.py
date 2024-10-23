import argparse
import csv
import ebooklib
import gradio as gr
import nltk
import os
import re
import shutil
import socket
import spacy
import subprocess
import sys
import time
import torch
import torchaudio
import urllib.request
import uuid
import zipfile
import traceback

from bs4 import BeautifulSoup
from pydub import AudioSegment
from datetime import datetime
from ebooklib import epub
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from tqdm import tqdm
from translate import Translator
from urllib.parse import urlparse

import lib.conf as conf
import lib.lang as lang

def inject_configs(target_namespace):
    # Extract variables from both modules and inject them into the target namespace
    for module in (conf, lang):
        target_namespace.update({k: v for k, v in vars(module).items() if not k.startswith("__")})

# Inject configurations into the global namespace of this module
inject_configs(globals())

is_web_process = False
is_web_shared = False
in_docker = False
in_python_env = False

ebook_id = None
tmp_dir = None
ebook_chapters_dir = None
ebook_chapters_audio_dir = None
audiobook_web_dir = None
ebook_file = None
ebook_title = None
final_format = "m4b"

# Base pronouns in English
ebook_pronouns = {
    "male": ["he", "him", "his"],
    "female": ["she", "her", "hers"]
}

client = None

def import_globals(target_namespace):
    target_namespace.update({k: v for k, v in globals().items() if not k.startswith("__")})

def define_props(ebook_src):
    global ebook_file, tmp_dir, audiobook_web_dir, ebook_chapters_dir, ebook_chapters_audio_dir
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        os.makedirs(ebook_chapters_dir, exist_ok=True)
        os.makedirs(ebook_chapters_audio_dir, exist_ok=True)
        ebook_file = os.path.join(tmp_dir, os.path.basename(ebook_src))
        shutil.copy(ebook_src, ebook_file)
        return True
    except Exception as e:
        print(f"Error copying ebook file: {e}")
        return False
    
def is_running_in_docker():
    try:
        with open('/proc/1/cgroup', 'r') as f:
            content = f.read()
            if 'docker' in content or 'containerd' in content:
                return True
    except FileNotFoundError:
        return False
    return False
    
def check_virtual_env():
    if sys.prefix != sys.base_prefix:
        return True

    return False
    
def check_program_installed(program_name, command, options):
    try:
        subprocess.run([command, options], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        print(f"Error: {program_name} is not installed.")
        return False
    except subprocess.CalledProcessError:
        print(f"Error: There was an issue running {program_name}.")
        return False

def get_model_dir_from_url(custom_model_url):
    # Extract the last part of the custom_model_url as the model_dir
    parsed_url = urlparse(custom_model_url)
    model_dir_name = os.path.basename(parsed_url.path)
    model_dir = f"./models/{model_dir_name}"
    
    # Ensure the model directory exists
    os.makedirs(model_dir, exist_ok=True)

    return model_dir
    
def download_and_extract(path_or_url, extract_to='model_root'):
    try:
        # Check if the input is a URL or a local file
        parsed_url = urlparse(path_or_url)
        is_url = parsed_url.scheme in ('http', 'https')

        if is_url:
            zip_path = os.path.join(extract_to, str(uuid.uuid4())+'.zip')

            # Download with progress bar
            with tqdm(unit='B', unit_scale=True, miniters=1, desc="Downloading Model") as t:
                def reporthook(blocknum, blocksize, totalsize):
                    t.total = totalsize
                    t.update(blocknum * blocksize - t.n)

                urllib.request.urlretrieve(path_or_url, zip_path, reporthook=reporthook)
            print(f"Downloaded zip file to {zip_path}")
        else:
            # If it's a local file, use the provided path directly
            zip_path = path_or_url
            print(f"Using local zip file: {zip_path}")

        # Unzipping with progress bar
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            files = zip_ref.namelist()
            with tqdm(total=len(files), unit="file", desc="Extracting Files") as t:
                for file in files:
                    if not file.endswith('/'):  # Skip directories
                        # Extract the file to the target directory
                        extracted_path = zip_ref.extract(file, extract_to)
                        # Move the file to the base directory
                        base_file_path = os.path.join(extract_to, os.path.basename(file))
                        os.rename(extracted_path, base_file_path)
                    t.update(1)

        # Cleanup: Remove the ZIP file if it was downloaded
        if is_url:
            os.remove(zip_path)
        
        # Remove any empty folders
        for root, dirs, files in os.walk(extract_to, topdown=False):
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        print(f"Extracted files to {extract_to}")
        
        # Check if all required files are present
        required_files = ['model.pth', 'config.json', 'vocab.json_']
        missing_files = [file for file in required_files if not os.path.exists(os.path.join(extract_to, file))]
        
        if not missing_files:
            print("All required files (model.pth, config.json, vocab.json_) found.")
        else:
            print(f"Missing files: {', '.join(missing_files)}")
    
    except Exception as e:
        print(f"Failed to download or extract zip file: {e}")



def translate_pronouns(language):
    global ebook_pronouns
    
    translator = Translator(to_lang=language)
   
    # Translate the pronouns to the target language
    translated_pronouns = {
        "male": [translator.translate(pronoun) for pronoun in ebook_pronouns["male"]],
        "female": [translator.translate(pronoun) for pronoun in ebook_pronouns["female"]]
    }

    return translated_pronouns
        
def extract_metadata_and_cover(ebook_filename_noext):
    global  client, ebook_file, tmp_dir
    metadatas = None

    def parse_metadata(metadata_str):
        metadata = {}
        for line in metadata_str.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        return metadata
        
    cover_file = os.path.join(tmp_dir, ebook_filename_noext + '.jpg')

    # Ensure the ebook file and directory exist
    if not os.path.exists(ebook_file):
        print(f"Error: eBook file {ebook_file} not found.")
        return None, None
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)

    # Handle the case when running inside Docker
    if in_docker or not in_python_env:
        try:
            # Extract the cover image
            subprocess.run(['ebook-meta', ebook_file, '--get-cover', cover_file], check=True)

            # Extract metadata without writing to a file
            metadata_result = subprocess.check_output(['ebook-meta', ebook_file], universal_newlines=True)
            metadatas = parse_metadata(metadata_result)

        except subprocess.CalledProcessError as e:
            print(f"An error occurred during metadata extraction: {e}")
            return None, None

    # Handle the case when not running inside Docker (e.g., on the host machine)
    else:
        source_dir = os.path.abspath(os.path.dirname(ebook_file))
        docker_dir = os.path.basename(tmp_dir)
        docker_file_in = os.path.basename(ebook_file)
        docker_file_out = os.path.basename(cover_file)

        try:
            # Run the Docker container to extract metadata and cover image
            if client is None:
                client = docker.from_env()
            metadata_result = client.containers.run(
                docker_utils_image,
                command=f"ebook-meta /files/{docker_dir}/{docker_file_in} --get-cover /files/{docker_dir}/{docker_file_out}",
                volumes={source_dir: {'bind': f'/files/{docker_dir}', 'mode': 'rw'}},
                remove=True,
                detach=False,
                stdout=True,
                stderr=True
            )

            # Parse the metadata from the Docker container output
            metadata_lines = metadata_result.decode('utf-8').split('\n')[1:]  # This omits the first line
            metadata_result_omitted = '\n'.join(metadata_lines)  # Rejoin the remaining lines

            # Parse the metadata without the first line
            metadatas = parse_metadata(metadata_result_omitted)

        except docker.errors.ContainerError as e:
            print(f"An error occurred in Docker container: {e}")
            return None, None
        except docker.errors.ImageNotFound as e:
            print(f"Docker image '{docker_utils_image}' not found: {e}")
            return None, None
        except docker.errors.APIError as e:
            print(f"Docker API error: {e}")
            return None, None

    if os.path.exists(cover_file):
        return metadatas, cover_file
    else:
        return metadatas, None

def concat_audio_chapters(metadatas, cover_file):
    global is_web_process, ebook_title, final_format, ebook_file, tmp_dir, audiobook_web_dir, ebook_chapters_dir, ebook_chapters_audio_dir
    
    # Function to sort chapters based on their numeric order
    def sort_key(chapter_file):
        numbers = re.findall(r'\d+', chapter_file)
        return int(numbers[0]) if numbers else 0
        
    def combine_chapters(chapter_files, combined_wav):
        # Initialize an empty audio segment
        combined_audio = AudioSegment.empty()
        batch_size = 256
        # Process the chapter files in batches
        for i in range(0, len(chapter_files), batch_size):
            batch_files = chapter_files[i:i + batch_size]
            batch_audio = AudioSegment.empty()  # Initialize an empty AudioSegment for the batch
    
            # Sequentially append each file in the current batch to the batch_audio
            for chapter_file in batch_files:
                audio_segment = AudioSegment.from_wav(chapter_file)
                batch_audio += audio_segment
    
            # Combine the batch audio with the overall combined_audio
            combined_audio += batch_audio
    
        # Export the combined audio to the output file path
        combined_audio.export(combined_wav, format='wav')
        print(f"Combined audio saved to {combined_wav}")

    def generate_ffmpeg_metadata(chapter_files, metadata_file, metadatas):
        global client, ebook_title
        
        ffmpeg_metadata = ";FFMETADATA1\n"
        
        # Map metadatas to FFmpeg tags
        if metadatas:
            ebook_title = metadatas.get('Title', None)
            if ebook_title:
                ffmpeg_metadata += f"title={ebook_title}\n"  # Title
                
            author = metadatas.get('Author(s)', None)
            if author:
                ffmpeg_metadata += f"artist={author}\n"
                
            subtitle = metadatas.get('Subtitle', None)
            if subtitle:
                ffmpeg_metadata += f"subtitle={subtitle}\n"  # Subtitle

            publisher = metadatas.get('Publisher', None)
            if publisher:
                ffmpeg_metadata += f"publisher={publisher}\n"
                
            published = metadatas.get('Published', None)
            if published:
                # Check if the timestamp contains fractional seconds
                if '.' in published:
                    # Parse with fractional seconds
                    year = datetime.strptime(published, "%Y-%m-%dT%H:%M:%S.%f%z").year
                else:
                    # Parse without fractional seconds
                    year = datetime.strptime(published, "%Y-%m-%dT%H:%M:%S%z").year
            else:
                # If published is not provided, use the current year
                year = datetime.now().year
            
            ffmpeg_metadata += f"year={year}\n"
                
            description = metadatas.get('Description', None)
            if description:
                ffmpeg_metadata += f"description={description}\n"  # Description

            tags = metadatas.get('Tags', None)
            if tags:
                ffmpeg_metadata += f"genre={tags.replace(', ', ';')}\n"  # Genre

            series = metadatas.get('Series', None)
            if series:
                ffmpeg_metadata += f"series={series}\n"  # Series

            identifiers = metadatas.get('Identifiers', None)
            if identifiers and isinstance(identifiers, dict):
                isbn = identifiers.get("isbn", None)
                if isbn:
                    ffmpeg_metadata += f"isbn={isbn}\n"  # ISBN
                mobi_asin = identifiers.get("mobi-asin", None)
                if mobi_asin:
                    ffmpeg_metadata += f"asin={mobi_asin}\n"  # ASIN
                    
            languages = metadatas.get('Languages', None)
            if languages:
                ffmpeg_metadata += f"language={languages}\n\n"  # Language
            
        else:
            print("Warning: metadatas is None. Skipping metadata generation.")

        # Chapter information
        start_time = 0
        for index, chapter_file in enumerate(chapter_files):
            duration_ms = len(AudioSegment.from_wav(chapter_file))
            ffmpeg_metadata += f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={start_time}\n"
            ffmpeg_metadata += f"END={start_time + duration_ms}\ntitle=Chapter {index + 1}\n"
            start_time += duration_ms

        # Write the metadata to the file
        with open(metadata_file, 'w', encoding='utf-8') as file:
            file.write(ffmpeg_metadata)
         
        return ebook_title

    def convert_wav(tmp_dir,combined_wav, metadata_file, cover_image, final_file):
        docker_dir = os.path.basename(tmp_dir)
            
        ffmpeg_combined_wav = combined_wav if in_docker else f'/files/{docker_dir}/' + os.path.basename(combined_wav)
        ffmpeg_metadata_file = metadata_file if in_docker else f'/files/{docker_dir}/' + os.path.basename(metadata_file)
        ffmpeg_final_file = final_file if in_docker else f'/files/{docker_dir}/' + os.path.basename(final_file)
        ffmpeg_cover_image = None

        if cover_image:
            ffmpeg_cover_image = cover_image if in_docker else f'/files/{docker_dir}/' + os.path.basename(cover_image)
            
        ffmpeg_cmd = ['ffmpeg', '-i', ffmpeg_combined_wav, '-i', ffmpeg_metadata_file]
        
        if ffmpeg_cover_image:
            ffmpeg_cmd += ['-i', ffmpeg_cover_image, '-map', '0:a', '-map', '2:v']
        else:
            ffmpeg_cmd += ['-map', '0:a'] 

        ffmpeg_cmd += ['-map_metadata', '1', '-c:a', 'aac', '-b:a', '128k', '-ar', '44100']
        
        if ffmpeg_cover_image:
            if ffmpeg_cover_image.lower().endswith('.png'):
                ffmpeg_cmd += ['-c:v', 'png', '-disposition:v', 'attached_pic']  # PNG cover
            else:
                ffmpeg_cmd += ['-c:v', 'copy', '-disposition:v', 'attached_pic']  # JPEG cover (no re-encoding needed)
                
        if ffmpeg_cover_image and ffmpeg_cover_image.lower().endswith('.png'):
            ffmpeg_cmd += ['-pix_fmt', 'yuv420p']
            
        ffmpeg_cmd += ['-movflags', '+faststart', ffmpeg_final_file]
        
        if in_docker or not is_in_python_env:
            try:
                subprocess.run(ffmpeg_cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"An error occurred at convert_wav(): {e}")
                return None
        else:
            try:
                # Run the Docker container with FFmpeg command
                if client is None:
                    client = docker.from_env()
                container = client.containers.run(
                    docker_utils_image,
                    command=ffmpeg_cmd,
                    volumes={tmp_dir: {'bind': f'/files/{docker_dir}', 'mode': 'rw'}},
                    remove=True,
                    detach=False,
                    stdout=True,
                    stderr=True
                )
                print(container.decode('utf-8'))
            except docker.errors.ContainerError as e:
                print(f"An error occurred at convert_wav(): {e}")
                return None
            except docker.errors.ImageNotFound as e:
                print(f"The Docker image '{docker_utils_image}' was not found: {e}")
                return None
            except docker.errors.APIError as e:
                print(f"A Docker API error occurred: {e}")
                return None

        return True

    chapter_files = sorted([os.path.join(ebook_chapters_audio_dir, f) for f in os.listdir(ebook_chapters_audio_dir) if f.endswith('.wav')], key=sort_key)
    docker_dir = os.path.basename(tmp_dir)
    combined_wav = os.path.join(tmp_dir, 'combined.wav')
    metadata_file = os.path.join(tmp_dir, 'metadata.txt')
    
    combine_chapters(chapter_files, combined_wav)
    generate_ffmpeg_metadata(chapter_files, metadata_file, metadatas)
    
    if not ebook_title:
        ebook_title = os.path.splitext(os.path.basename(ebook_file))[0]

    concat_file = os.path.join(tmp_dir, ebook_title + '.' + final_format)
    if is_web_process:
        os.makedirs(audiobook_web_dir, exist_ok=True)
        final_file = audiobook_web_dir + '/' + os.path.basename(concat_file);
    else:
        final_file = audiobooks_dir + '/' + os.path.basename(concat_file);
    
    if convert_wav(tmp_dir,combined_wav, metadata_file, cover_file, concat_file):
        if shutil.copy(concat_file, final_file) == final_file:
            shutil.rmtree(tmp_dir)
            return final_file

    return None

def create_chapter_labeled_book(ebook_filename_noext):
    global client, ebook_title, ebook_file, tmp_dir, ebook_chapters_dir
    
    def convert_to_epub(ebook_file, epub_path):
        if os.path.basename(ebook_file) == os.path.basename(epub_path):
            return True
        else:
            if in_docker or not in_python_env:
                try:
                    subprocess.run(['ebook-convert', ebook_file, epub_path], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"An error occurred at create_chapter_labeled_book(): {e}")
                    return False
                return True
            else:
                # Extract the original filenames
                docker_dir = os.path.basename(tmp_dir)
                docker_file_in = os.path.basename(ebook_file)
                docker_file_out = os.path.basename(epub_path)
                
                # Check if the input file is already an EPUB
                if docker_file_in.lower().endswith('.epub'):
                    shutil.copy(ebook_file, epub_path)
                    return True

                # Convert the ebook to EPUB format using utils Docker image
                try:
                    # Run the Docker container
                    if client is None:
                        client = docker.from_env()
                    container = client.containers.run(
                        docker_utils_image,
                        command=f"ebook-convert /files/{docker_dir}/{docker_file_in} /files/{docker_dir}/{docker_file_out}",
                        volumes={tmp_dir: {'bind': f'/files/{docker_dir}', 'mode': 'rw'}},
                        remove=True,
                        detach=False,
                        stdout=True,
                        stderr=True
                    )

                    # Print container logs for verbose output
                    print(container.decode('utf-8'))

                except docker.errors.ContainerError as e:
                    print(f"An error occurred while converting the eBook: {e}")
                    return False
                except docker.errors.ImageNotFound as e:
                    print(f"The Docker image '{docker_utils_image}' was not found: {e}")
                    return False
                except docker.errors.APIError as e:
                    print(f"A Docker API error occurred: {e}")
                    return False

                return True

    def save_chapters_as_text(epub_path):
        # Open the EPUB file
        ebook = epub.read_epub(epub_path, {'ignore_ncx': False})

        previous_chapter_text = ''
        previous_filename = ''
        chapter_counter = 0

        # Iterate through the items in the EPUB file
        for item in ebook.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Use BeautifulSoup to parse HTML content
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text()

                # Check if the text is not empty
                if text.strip():
                    if len(text) < 2300 and previous_filename:
                        # Append text to the previous chapter if it's short
                        with open(previous_filename, 'a', encoding='utf-8') as file:
                            file.write('\n' + text)
                    else:
                        # Create a new chapter file and increment the counter
                        previous_filename = os.path.join(ebook_chapters_dir , f"chapter_{chapter_counter}.txt")
                        chapter_counter += 1
                        with open(previous_filename, 'w', encoding='utf-8') as file:
                            file.write(text)
                            print(f"Saved chapter: {previous_filename}")
                            
    epub_path = os.path.join(tmp_dir, ebook_filename_noext + '.epub')       
    if convert_to_epub(ebook_file, epub_path):
        save_chapters_as_text(epub_path)

    def process_chapter_files(ebook_chapters_dir, output_csv):
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Text', 'Start Location', 'End Location', 'Is Quote', 'Speaker', 'Chapter'])

            # Process each chapter file
            chapter_files = sorted(
                [f for f in os.listdir(ebook_chapters_dir) if re.match(r'chapter_\d+\.txt$', f)],
                key=lambda x: int(x.split('_')[1].split('.')[0])
            )
            for filename in chapter_files:
                chapter_number = int(filename.split('_')[1].split('.')[0])
                file_path = os.path.join(ebook_chapters_dir, filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()
                        # Insert "NEWCHAPTERABC" at the beginning of each chapter's text
                        if text:
                            text = "NEWCHAPTERABC" + text
                        sentences = nltk.tokenize.sent_tokenize(text)
                        for sentence in sentences:
                            start_location = text.find(sentence)
                            end_location = start_location + len(sentence)
                            writer.writerow([sentence, start_location, end_location, 'True', 'Narrator', chapter_number])
                except Exception as e:
                    print(f"Error processing file {filename}: {e}")

    output_csv = os.path.join(tmp_dir, "chapters.csv")
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    process_chapter_files(ebook_chapters_dir, output_csv)

def check_vocab_file(dir):
    vocab_path = os.path.join(dir, 'vocab.json')
    new_vocab_path = os.path.join(dir, 'vocab.json_')

    # Check if vocab.json exists
    if os.path.exists(vocab_path):
        # Rename the file
        os.rename(vocab_path, new_vocab_path)
        print(f"Renamed {vocab_path} to {new_vocab_path}")
        return True  # Return True if the file was found and renamed

def combine_wav_files(chapters_dir_audio_fragments, ebook_chapters_audio_dir, chapter_wav_file):
    # Specify the output file path
    output_file = os.path.join(ebook_chapters_audio_dir, chapter_wav_file)

    # Initialize an empty audio segment
    combined_audio = AudioSegment.empty()

    # Get a list of all .wav files in the specified input directory and sort them
    fragments_dir_ordered = sorted(
        [os.path.join(chapters_dir_audio_fragments, f) for f in os.listdir(chapters_dir_audio_fragments) if f.endswith(".wav")],
        key=lambda f: int(''.join(filter(str.isdigit, f)))
    )

    # Sequentially append each file to the combined_audio
    for file in fragments_dir_ordered:
        audio_segment = AudioSegment.from_wav(file)
        combined_audio += audio_segment

    # Export the combined audio to the output file path
    combined_audio.export(output_file, format='wav')
    print(f"Combined audio saved to {output_file}")

def split_long_sentence(sentence, language='en', max_pauses=10):
    """
    Splits a sentence into parts based on length or number of pauses without recursion.
    
    :param sentence: The sentence to split.
    :param language: The language of the sentence (default is English).
    :param max_pauses: Maximum allowed number of pauses in a sentence.
    :return: A list of sentence parts that meet the criteria.
    """
    # Get the Max character length for the selected language -2 : with a default of 248 if no language is found
    max_length = (char_limits.get(language, 250)-2)

    # Adjust the pause punctuation symbols based on language
    if language == 'zh-cn':
        punctuation = ['，', '。', '；', '？', '！']  # Chinese-specific pause punctuation including sentence-ending marks
    elif language == 'ja':
        punctuation = ['、', '。', '；', '？', '！']  # Japanese-specific pause punctuation
    elif language == 'ko':
        punctuation = ['，', '。', '；', '？', '！']  # Korean-specific pause punctuation
    elif language == 'ar':
        punctuation = ['،', '؛', '؟', '!', '·', '؛', '.']  # Arabic-specific punctuation
    elif language == 'en':
        punctuation = [',', ';', '.']  # English-specific pause punctuation
    else:
        # Default pause punctuation for other languages (es, fr, de, it, pt, pl, cs, ru, nl, tr, hu)
        punctuation = [',', '.', ';', ':', '?', '!']
   
    parts = []
    while len(sentence) > max_length or sum(sentence.count(p) for p in punctuation) > max_pauses:
        possible_splits = [i for i, char in enumerate(sentence) if char in punctuation and i < max_length]
        if possible_splits:
            # Find the best place to split the sentence, preferring the last possible split to keep parts longer
            split_at = possible_splits[-1] + 1
        else:
            # If no punctuation to split on within max_length, split at max_length
            split_at = max_length
        
        # Split the sentence and add the first part to the list
        parts.append(sentence[:split_at].strip())
        sentence = sentence[split_at:].strip()
    
    # Add the remaining part of the sentence
    parts.append(sentence)
    return parts

def convert_chapters_to_audio(device, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, target_voice_file=None, language="en", custom_model=None):
    global is_web_process, ebook_chapters_dir, ebook_chapters_audio_dir
    
    progress_bar = None
    
    # create gradio progress bar if process come from gradio interface
    if is_web_process == True:
        progress_bar = gr.Progress(track_tqdm=True)
    
    # Set default target voice path if not provided
    if target_voice_file is None:
        target_voice_file = default_target_voice_file
    
    # Handle custom model or use standard TTS model
    if custom_model:
        print("Loading custom model...")
        config = XttsConfig()
        config.load_json(custom_model['config'])
        model = Xtts.init_from_config(config)
        model.load_checkpoint(config, checkpoint_path=custom_model['model'], vocab_path=custom_model['vocab'], use_deepspeed=False, weights_only=True)
        model.to(device)
        print("Computing speaker latents...")
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=[target_voice_file])
    else:
        selected_tts_model = "tts_models/multilingual/multi-dataset/xtts_v2"
        tts = TTS(selected_tts_model, progress_bar=False).to(device)
    
    chapters_dir_audio_fragments = os.path.join(ebook_chapters_audio_dir, "fragments")
    os.makedirs(chapters_dir_audio_fragments, exist_ok=True)

    # Calculate the total number of chapters and segments (fragments) to set progress bar correctly
    total_segments = 0
    total_chapters = len([f for f in os.listdir(ebook_chapters_dir) if f.endswith('.txt')])

    # Pre-calculate total segments (sentences + fragments per chapter)
    for chapter_file in sorted(os.listdir(ebook_chapters_dir)):
        if chapter_file.endswith('.txt'):
            with open(os.path.join(ebook_chapters_dir, chapter_file), 'r', encoding='utf-8') as file:
                chapter_text = file.read()
                nltk_language = language_mapping.get(language)
                if nltk_language:
                    sentences = nltk.tokenize.sent_tokenize(chapter_text, language=nltk_language)
                else:
                    sentences = [chapter_text]
                
                # Calculate total fragments for this chapter
                for sentence in sentences:
                    fragments = split_long_sentence(sentence, language=language)
                    total_segments += len(fragments)

    # Initialize progress tracking
    current_progress = 0
    total_progress = total_segments + total_chapters  # Total is chapters + segments/fragments

    with tqdm(total=total_progress, desc="Processing 0.00%", bar_format='{desc}: {n_fmt}/{total_fmt} ', unit="step") as t:
        for chapter_file in sorted(os.listdir(ebook_chapters_dir)):
            if chapter_file.endswith('.txt'):
                match = re.search(r"chapter_(\d+).txt", chapter_file)
                if match:
                    chapter_num = int(match.group(1))
                else:
                    print(f"Skipping file {chapter_file} as it does not match the expected format.")
                    continue

                chapter_file_path = os.path.join(ebook_chapters_dir, chapter_file)
                chapter_wav_file = f"chapter_{chapter_num}.wav"
                count_fragments = 0

                with open(chapter_file_path, 'r', encoding='utf-8') as file:
                    chapter_text = file.read()
                    nltk_language = language_mapping.get(language)
                    
                    if nltk_language:
                        sentences = nltk.tokenize.sent_tokenize(chapter_text, language=nltk_language)
                    else:
                        sentences = [chapter_text]
                    
                    for sentence in sentences:
                        fragments = split_long_sentence(sentence, language=language)
                        for fragment in fragments:
                            if fragment != "":
                                print(f"Generating fragment: {fragment}...")
                                fragment_file_path = os.path.join(chapters_dir_audio_fragments, f"{count_fragments}.wav")
                                
                                if custom_model:
                                    out = model.inference(
                                        fragment, language, gpt_cond_latent, speaker_embedding, 
                                        temperature=temperature, repetition_penalty=repetition_penalty, 
                                        top_k=top_k, top_p=top_p, speed=speed, enable_text_splitting=enable_text_splitting
                                    )
                                    torchaudio.save(fragment_file_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)
                                else:
                                    speaker_wav_path = target_voice_file if target_voice_file else default_target_voice_file
                                    tts.tts_to_file(
                                        text=fragment, 
                                        file_path=fragment_file_path, 
                                        speaker_wav=speaker_wav_path, 
                                        language=language, 
                                        temperature=temperature, 
                                        length_penalty=length_penalty, 
                                        repetition_penalty=repetition_penalty, 
                                        top_k=top_k, 
                                        top_p=top_p, 
                                        speed=speed, 
                                        enable_text_splitting=enable_text_splitting
                                    )
                                
                                count_fragments += 1
                                current_progress += 1

                                percentage = (current_progress / total_progress) * 100
                                t.set_description(f"Processing {percentage:.2f}%")
                                t.update(1)

                                # Update Gradio progress bar
                                if progress_bar is not None:
                                    progress_bar(current_progress / total_progress)

                # Combine audio fragments
                combine_wav_files(chapters_dir_audio_fragments, ebook_chapters_audio_dir, chapter_wav_file)
                print(f"Converted chapter {chapter_num} to audio.")

                current_progress += 1
                percentage = (current_progress / total_progress) * 100
                t.set_description(f"Processing {percentage:.2f}%")
                t.update(1)

                # Update Gradio progress bar
                if progress_bar is not None:
                    progress_bar(current_progress / total_progress)

    return True

def download_audiobooks():
    global final_format, ebook_file, audiobook_web_dir
    files = []
    
    if os.path.isdir(audiobook_web_dir):
        for filename in os.listdir(audiobook_web_dir):
            if filename.endswith('.'+final_format):
                files.append(os.path.join(audiobook_web_dir, filename))

    return files

def convert_ebook(args, ui_needed):
    global in_docker, in_python_env, audiobooks_dir, is_web_process, ebook_id, ebook_title, final_format, ebook_file, tmp_dir, audiobook_web_dir, ebook_chapters_dir, ebook_chapters_audio_dir

    is_web_process = ui_needed
    device = args.device
    target_voice_file = args.voice
    language = args.language
    use_custom_model = args.use_custom_model
    custom_model_file = args.custom_model
    custom_config_file = args.custom_config
    custom_vocab_file = args.custom_vocab
    temperature = args.temperature
    length_penalty = args.length_penalty
    repetition_penalty = args.repetition_penalty
    top_k = args.top_k
    top_p = args.top_p
    speed = args.speed
    enable_text_splitting = args.enable_text_splitting
    custom_model_url = args.custom_model_url
    
    in_docker = is_running_in_docker();
    in_python_env = check_virtual_env();
    
    if in_python_env:
        import docker
    elif not check_program_installed("Calibre", "calibre", "--version") or not check_program_installed("FFmpeg", "ffmpeg", "-version"):
        sys.exit(1)
                    
    if is_web_process == False:
        ebook_id = str(uuid.uuid4())

    tmp_dir = os.path.join(process_dir, f"ebook-{ebook_id}")
    ebook_chapters_dir = os.path.join(tmp_dir, "chapters")
    ebook_chapters_audio_dir = os.path.join(ebook_chapters_dir, "audio")
    audiobook_web_dir = os.path.join(audiobooks_dir, f"web-{ebook_id}") if is_web_shared else audiobooks_dir
    
    delete_old_web_folders(audiobooks_dir)
            
    if language != "en":
        ebook_pronouns = translate_pronouns(language)
        
    # Load spaCy model for language analysis (you can switch models based on language)
    nlp = spacy.load(language + '_core_web_sm')

    # Prepare tmp dir and properties
    if define_props(args.ebook) : 
        
        # Get the name of the ebook file source without extension
        ebook_filename_noext = os.path.splitext(os.path.basename(ebook_file))[0]

        try:
            # Handle custom model if the user chose to use one
            custom_model = None
            if use_custom_model and custom_model_file and custom_config_file and custom_vocab_file:
                custom_model = {
                    'model': custom_model_file,
                    'config': custom_config_file,
                    'vocab': custom_vocab_file
                }

            # If a custom model URL is provided, download and use it
            if use_custom_model and custom_model_url:
                print(f"Received custom model URL: {custom_model_url}")
                model_dir = get_model_dir_from_url(custom_model_url)
                download_and_extract(custom_model_url, model_dir)

                # Check if vocab.json exists and rename it
                if check_vocab_file(model_dir):
                    print("vocab.json file was found and renamed.")
                
                custom_model = {
                    'model': os.path.join(model_dir, 'model.pth'),
                    'config': os.path.join(model_dir, 'config.json'),
                    'vocab': os.path.join(model_dir, 'vocab.json_')
                }

            create_chapter_labeled_book(ebook_filename_noext)

            if torch.cuda.is_available() == False:
                if device == "gpu":
                    print("GPU is not available on your device!")
                device = "cpu"
                    
            torch.device(device)
            print(f"Available Processor Unit: {device}")
            
            print("Extract Metada and Cover")
            metadatas, cover_file = extract_metadata_and_cover(ebook_filename_noext)

            if convert_chapters_to_audio( device, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, target_voice_file, language, custom_model):
                # Concatenate the audio chapters into a single file
                output_file = concat_audio_chapters(metadatas, cover_file)
                
                if output_file is not None:
                    print(f"Temporary directory {tmp_dir} removed successfully.")
                    gr.update(value=None)
                    return f"Audiobook {os.path.basename(output_file)} created!", output_file 
                else:
                    print("Error concat_audio_chapters()")
            else:
                print("Error convert_chapters_to_audio()")

        except Exception as e:
            print(f"Error in convert_ebook(): {e}")
            traceback.print_exc()
        
    print(f"Temporary directory {tmp_dir} not removed due to failure.")  
    return None, None
    
def delete_old_web_folders(root_dir):
    global web_dir_expire
    
    # Ensure the root_dir directory exists
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
        print(f"Created missing directory: {root_dir}")

    current_time = time.time()
    age_limit = current_time - web_dir_expire * 60 * 60  # 24 hours in seconds

    for folder_name in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder_name)

        if os.path.isdir(folder_path) and folder_name.startswith("web-"):
            folder_creation_time = os.path.getctime(folder_path)

            if folder_creation_time < age_limit:
                shutil.rmtree(folder_path)
  
def initialize_session(session_id):
    global ebook_id, is_web_shared
    
    if session_id == "":
        session_id = str(uuid.uuid4())
    
    ebook_id = session_id
    warning_text = str("")
    
    if is_web_shared:
        warning_text = str(f" Note: if the page is reloaded or closed all converted files will be lost. Access limit time: {web_dir_expire} hours")
    return f"Session: {session_id}.{warning_text}", session_id

def web_interface(share, ui_needed):
    global is_web_shared
    
    is_web_shared = share
    
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="blue",
        neutral_hue="blue",
        text_size=gr.themes.sizes.text_md,
    )
    with gr.Blocks(theme=theme) as demo:
        gr.Markdown(
        """
        # eBook to Audiobook Converter

        Transform your eBooks into immersive audiobooks with optional custom TTS models.

        This interface is based on [Ebook2AudioBookXTTS](https://github.com/DrewThomasson/ebook2audiobookXTTS).
        """
        )

        with gr.Tabs():  # Create tabs for better UI organization
            with gr.TabItem("Input Options"):
                with gr.Row():
                    with gr.Column(scale=3):
                        ebook_file = gr.File(label="eBook File")
                        target_voice_file = gr.File(label="Target Voice File (Optional)")
                        language = gr.Dropdown(label="Language", choices=language_options, value="en")
                        device = gr.Radio(label="Processor Unit", choices=["cpu", "gpu"], value="cpu")

                    with gr.Column(scale=3):
                        use_custom_model = gr.Checkbox(label="Use Custom Model")
                        custom_model_file = gr.File(label="Custom Model File (Optional)", visible=False)
                        custom_config_file = gr.File(label="Custom Config File (Optional)", visible=False)
                        custom_vocab_file = gr.File(label="Custom Vocab File (Optional)", visible=False)
                        custom_model_url = gr.Textbox(label="Custom Model Zip URL (Optional)", visible=False)

            with gr.TabItem("Audio Generation Preferences"):  # New tab for preferences
                gr.Markdown(
                """
                ### Customize Audio Generation Parameters
                
                Adjust the settings below to influence how the audio is generated. You can control the creativity, speed, repetition, and more.
                """
                )
                temperature = gr.Slider(
                    label="Temperature", 
                    minimum=0.1, 
                    maximum=10.0, 
                    step=0.1, 
                    value=0.65,
                    info="Higher values lead to more creative, unpredictable outputs. Lower values make it more monotone."
                )
                length_penalty = gr.Slider(
                    label="Length Penalty", 
                    minimum=0.5, 
                    maximum=10.0, 
                    step=0.1, 
                    value=1.0, 
                    info="Penalize longer sequences. Higher values produce shorter outputs. Not applied to custom models."
                )
                repetition_penalty = gr.Slider(
                    label="Repetition Penalty", 
                    minimum=1.0, 
                    maximum=10.0, 
                    step=0.1, 
                    value=2.0, 
                    info="Penalizes repeated phrases. Higher values reduce repetition."
                )
                top_k = gr.Slider(
                    label="Top-k Sampling", 
                    minimum=10, 
                    maximum=100, 
                    step=1, 
                    value=50, 
                    info="Lower values restrict outputs to more likely words and increase speed at which audio generates."
                )
                top_p = gr.Slider(
                    label="Top-p Sampling", 
                    minimum=0.1, 
                    maximum=1.0, 
                    step=.01, 
                    value=0.8, 
                    info="Controls cumulative probability for word selection. Lower values make the output more predictable and increase speed at which audio generates."
                )
                speed = gr.Slider(
                    label="Speed", 
                    minimum=0.5, 
                    maximum=3.0, 
                    step=0.1, 
                    value=1.0, 
                    info="Adjusts how fast the narrator will speak."
                )
                enable_text_splitting = gr.Checkbox(
                    label="Enable Text Splitting", 
                    value=False,
                    info="Splits long texts into sentences to generate audio in chunks. Useful for very long inputs."
                )
                
            session_status = gr.Textbox(label="Session Status")
            session_id = gr.State()  # Persistent session state stored in Gradio
            session_id_input = gr.Textbox(visible=False, label="Session ID from localStorage")  # Hidden Textbox to hold session_id

            # Inject client-side JavaScript for handling localStorage
            session_js = gr.HTML('''
            <script>
                // Ensure the page waits for the session_id to be retrieved from localStorage
                document.addEventListener("DOMContentLoaded", function () {
                    let session_id = localStorage.getItem("session_id");

                    // If the session_id exists in localStorage, set it in the hidden input field
                    if (session_id) {
                        document.querySelector("input[name='session_id_input']").value = session_id;
                    } else {
                        // Create a new session_id and store it in localStorage with a 24-hour expiration
                        session_id = Date.now() + '-' + Math.random().toString(36).substring(2);
                        localStorage.setItem("session_id", session_id);

                        // Set the new session_id in the hidden input field
                        document.querySelector("input[name='session_id_input']").value = session_id;
                    }
                });

                // Listen for session updates and store them in localStorage
                function storeSessionInLocalStorage(new_session_id) {
                    localStorage.setItem("session_id", new_session_id);
                }
            </script>
            ''')

            # Automatically initialize session and run other processes when the page loads
            demo.load(initialize_session, outputs=[session_status, session_id], inputs=[session_id_input])

        convert_btn = gr.Button("Convert to Audiobook", variant="primary")
        output = gr.Textbox(label="Conversion Status")
        audio_player = gr.Audio(label="Audiobook Player", type="filepath")
        download_btn = gr.Button("Download Audiobook Files")
        download_files = gr.File(label="Download Files", interactive=False)

        def process_conversion(device, ebook_file, target_voice_file, language, use_custom_model, custom_model_file, custom_config_file, custom_vocab_file, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, custom_model_url):
            ebook_file = ebook_file.name if ebook_file else None
            target_voice_file = target_voice_file.name if target_voice_file else None
            custom_model_file = custom_model_file.name if custom_model_file else None
            custom_config_file = custom_config_file.name if custom_config_file else None
            custom_vocab_file = custom_vocab_file.name if custom_vocab_file else None

            if not ebook_file:
                return "Error: eBook file is required.", None

            # Call the convert_ebook function with the processed parameters
            args = argparse.Namespace(
                device=device,
                ebook=ebook_file,
                voice=target_voice_file,
                language=language,
                use_custom_model=use_custom_model,
                custom_model=custom_model_file,
                custom_config=custom_config_file,
                custom_vocab=custom_vocab_file,
                custom_model_url=custom_model_url,
                temperature=float(temperature),
                length_penalty=float(length_penalty),
                repetition_penalty=float(repetition_penalty),
                top_k=int(top_k),
                top_p=float(top_p),
                speed=float(speed),
                enable_text_splitting=enable_text_splitting
            )
            status, audiobook_file = convert_ebook(args, ui_needed)
            if audiobook_file is not None:
                return status, audiobook_file
            else:
                return "Conversion failed.", None

        # Trigger the conversion process
        convert_btn.click(
            process_conversion,
            inputs=[
                device, ebook_file, target_voice_file, language, 
                use_custom_model, custom_model_file, custom_config_file, 
                custom_vocab_file, temperature, length_penalty, repetition_penalty, 
                top_k, top_p, speed, enable_text_splitting, custom_model_url
            ],
            outputs=[output, audio_player]
        )

        use_custom_model.change(
            lambda x: [gr.update(visible=x)] * 4,
            inputs=[use_custom_model],
            outputs=[custom_model_file, custom_config_file, custom_vocab_file, custom_model_url]
        )

        download_btn.click(
            download_audiobooks,
            outputs=[download_files]
        )

    # Get the correct local IP or localhost
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
        print(f"Running on local URL: http://{local_ip}:{web_interface_port}")
    except socket.gaierror:
        local_ip = '127.0.0.1'
        print(f"Running on local URL: http://localhost:{web_interface_port}")

    # Launch Gradio app
    demo.launch(server_name="0.0.0.0", server_port=web_interface_port, share=share)