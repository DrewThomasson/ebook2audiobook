import argparse
import csv
import docker
import ebooklib
import gradio as gr
import os
import re
import shutil
import socket
import spacy
import subprocess
import sys
import nltk
import threading
import time
import torch
import torchaudio
import urllib.request
import uuid
import zipfile
import traceback
import requests

from bs4 import BeautifulSoup
from pydub import AudioSegment
from datetime import datetime
from ebooklib import epub
from spacy.util import is_package
from spacy.cli import download as download_package
from tqdm import tqdm
from translate import Translator
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from urllib.parse import urlparse

import lib.conf as conf
import lib.lang as lang

# Automatically accept the non-commercial license
os.environ["COQUI_TOS_AGREED"] = "1"

def inject_configs(target_namespace):
    # Extract variables from both modules and inject them into the target namespace
    for module in (conf, lang):
        target_namespace.update({k: v for k, v in vars(module).items() if not k.startswith("__")})

# Inject configurations into the global namespace of this module
inject_configs(globals())

script_mode = None
is_gui_process = False
is_gui_shared = False
is_converting = False

interface = None
client = None
ebook_id = None
audiobooks_dir = None
tmp_dir = None
ebook_chapters_dir = None
ebook_chapters_audio_dir = None
ebook_src = None
ebook_title = None
audiobooks_ddn = None

# Base pronouns in English
ebook_pronouns = {
    "male": ["he", "him", "his"],
    "female": ["she", "her", "hers"]
}

# Initialize a threading event to handle cancellation
cancellation_requested = threading.Event()

class DependencyError(Exception):
    def __init__(self, message=None):
        super().__init__(message)
        # Automatically handle the exception when it's raised
        self.handle_exception()

    def handle_exception(self):
        # Print the full traceback of the exception
        traceback.print_exc()
        
        # Print the exception message
        print(f"Caught DependencyError: {self}")
        
        # Exit the script if it's not a web process
        if not is_gui_process:
            sys.exit(1)

def check_files_in_folder(folder_path, file_list):
    if not os.path.exists(folder_path):
        return False, "Folder does not exist", file_list

    # Get the list of files in the folder
    existing_files = os.listdir(folder_path)
    
    # Identify the missing files
    missing_files = [file for file in file_list if file not in existing_files]
    
    if missing_files:
        return False, "Some files are missing", missing_files
    return True, "All files are present", []

def download_xttsv2_model(destination_dir, zip_link_to_xtts_model):
    # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    zip_path = os.path.join(destination_dir, "xtts_v2_model.zip")

    # Start downloading the file with a loading bar
    print("Downloading the XTTS v2 model...")
    response = requests.get(zip_link_to_xtts_model, stream=True)
    response.raise_for_status()  # Raise an error for bad status codes

    total_size = int(response.headers.get('content-length', 0))
    chunk_size = 1024  # Download in chunks of 1KB

    with open(zip_path, "wb") as file, tqdm(
        total=total_size, unit='B', unit_scale=True, desc="Downloading"
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            file.write(chunk)
            progress_bar.update(len(chunk))

    # Extract the contents of the zip file
    print("Extracting the model files...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(destination_dir)

    # Remove the downloaded zip file
    os.remove(zip_path)
    print("Model downloaded, extracted, and zip file removed successfully.")

def prepare_dirs(src):
    global ebook_src
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        os.makedirs(audiobooks_dir, exist_ok=True)
        os.makedirs(ebook_chapters_dir, exist_ok=True)
        os.makedirs(ebook_chapters_audio_dir, exist_ok=True)
        ebook_src = os.path.join(tmp_dir, os.path.basename(src))
        shutil.copy(src, ebook_src)
        return True
    except Exception as e:
        raise DependencyError(e)

def check_programs(prog_name, command, options):
    try:
        subprocess.run([command, options], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, None
    except FileNotFoundError:
        e = f"""********** Error: {prog_name} is not installed! if your OS calibre package version 
        is not compatible you still can run ebook2audiobook.sh (linux/mac) or ebook2audiobook.cmd (windows) **********"""
        raise DependencyError(e)
    except subprocess.CalledProcessError:
        e = f"Error: There was an issue running {prog_name}."
        raise DependencyError(e)

def remove_conflict_pkg(pkg):
    try:
        result = subprocess.run(["pip", 'show', pkg], env={}, stdout=subprocess.PIPE, text=True, check=True)
        package_location = None
        for line in result.stdout.splitlines():
            if line.startswith('Location'):
                package_location = line.split(': ')[1]
                break
        if package_location is not None:
            try:
                print(f"*** {pkg} is in conflict with an external OS python library, trying to solve it....***")
                result = subprocess.run(["pip", 'uninstall', pkg, '-y'], env={}, stdout=subprocess.PIPE, text=True, check=True)               
            except subprocess.CalledProcessError as e:
                raise DependencyError(e)

    except Exception as e:
        raise DependencyError(e)

def get_model_dir_from_url(custom_model_url):
    try:
        # Extract the last part of the custom_model_url as the model_dir
        parsed_url = urlparse(custom_model_url)
        model_dir_name = os.path.basename(parsed_url.path)
        model_dir = os.path.join(".","models",model_dir_name)
        # Ensure the model directory exists
        os.makedirs(model_dir, exist_ok=True)
        return model_dir
    except Exception as e:
        raise DependencyError(e)
    
def download_and_extract(path_or_url, extract_to=models_dir):
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
                    if cancellation_requested.is_set():
                        msg = "Cancel requested"
                        raise ValueError()

                    if not os.path.isdir(file):
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
            return True
        else:
            print(f"Missing files: {', '.join(missing_files)}")
            return False
    except Exception as e:
        raise DependencyError(e)

#def load_spacy_model(language):
#    lang_pack = language_mapping[language]["model"]
#    try:
#        nlp = spacy.load(lang_pack)
#    except OSError:
#        print("Spacy model not found. Tyring to download it...")
#        try:
#            subprocess.run(["python", "-m", "spacy", "download", lang_pack])
#            nlp = spacy.load(lang_pack)
#        except OSError:
#             raise ValueError(f"Spacy model does not exist for {language_mapping[language]['name']}...")
#    return nlp

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
    metadatas = None
    def parse_metadata(metadata_str):
        metadata = {}
        for line in metadata_str.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        return metadata
        
    cover_file = os.path.join(tmp_dir, ebook_filename_noext + '.jpg')
    if script_mode == DOCKER_UTILS:
        try:
            source_dir = os.path.abspath(os.path.dirname(ebook_src))
            docker_dir = os.path.basename(tmp_dir)
            docker_file_in = os.path.basename(ebook_src)
            docker_file_out = os.path.basename(cover_file)
            metadata_result = client.containers.run(
                docker_utils_image,
                command=f"ebook-meta /files/{docker_dir}/{docker_file_in} --get-cover /files/{docker_dir}/{docker_file_out}",
                volumes={source_dir: {'bind': f'/files/{docker_dir}', 'mode': 'rw'}},
                remove=True,
                detach=False,
                stdout=True,
                stderr=True
            )      
            print(metadata_result.decode('utf-8'))
            metadata_lines = metadata_result.decode('utf-8').split('\n')[1:]  # This omits the first line
            metadata_result_omitted = '\n'.join(metadata_lines)  # Rejoin the remaining lines
            metadatas = parse_metadata(metadata_result_omitted)
            if os.path.exists(cover_file):
                return metadatas, cover_file
            else:
                return metadatas, None
        except docker.errors.ContainerError as e:
            raise DependencyError(e)
        except docker.errors.ImageNotFound as e:
            raise DependencyError(e)
        except docker.errors.APIError as e:
            raise DependencyError(e)
    else:
        try:
            util_app = shutil.which("ebook-meta")
            subprocess.run([util_app, ebook_src, '--get-cover', cover_file], check=True)
            metadata_result = subprocess.check_output([util_app, ebook_src], universal_newlines=True)
            metadatas = parse_metadata(metadata_result)
            if os.path.exists(cover_file):
                return metadatas, cover_file
            else:
                return metadatas, None
        except subprocess.CalledProcessError as e:
            remove_conflict_pkg("lxml")           
            raise DependencyError(e)

def concat_audio_chapters(metadatas, cover_file):
    global ebook_title
 
    # Function to sort chapters based on their numeric order
    def sort_key(chapter_file):
        numbers = re.findall(r'\d+', chapter_file)
        return int(numbers[0]) if numbers else 0
        
    def combine_chapters():
        # Initialize an empty audio segment
        combined_audio = AudioSegment.empty()
        batch_size = 256
        # Process the chapter files in batches
        for i in range(0, len(chapter_files), batch_size):
            if cancellation_requested.is_set():
                msg = "Cancel requested"
                raise ValueError(msg)

            batch_files = chapter_files[i:i + batch_size]
            batch_audio = AudioSegment.empty()  # Initialize an empty AudioSegment for the batch
    
            # Sequentially append each file in the current batch to the batch_audio
            for chapter_file in batch_files:
                if cancellation_requested.is_set():
                    msg = "Cancel requested"
                    raise ValueError(msg)

                audio_segment = AudioSegment.from_wav(chapter_file)
                batch_audio += audio_segment
    
            # Combine the batch audio with the overall combined_audio
            combined_audio += batch_audio
    
        # Export the combined audio to the output file path
        combined_audio.export(combined_wav, format='wav')
        print(f"Combined audio saved to {combined_wav}")
        return True

    def generate_ffmpeg_metadata():
        global ebook_title
        try:
            ffmpeg_metadata = ";FFMETADATA1\n"
            
            # Map metadatas to FFmpeg tags
            if metadatas:
                ebook_title = metadatas.get('Title', None)
                if ebook_title is not None:
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
                    ffmpeg_metadata += f"language={languages}\n\n"
                
            else:
                print("Warning: metadatas is None. Skipping metadata generation.")

            # Chapter information
            start_time = 0
            for index, chapter_file in enumerate(chapter_files):
                if cancellation_requested.is_set():
                    msg = "Cancel requested"
                    raise ValueError(msg)

                duration_ms = len(AudioSegment.from_wav(chapter_file))
                ffmpeg_metadata += f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={start_time}\n"
                ffmpeg_metadata += f"END={start_time + duration_ms}\ntitle=Chapter {index + 1}\n"
                start_time += duration_ms

            # Write the metadata to the file
            with open(metadata_file, 'w', encoding='utf-8') as file:
                file.write(ffmpeg_metadata)
            return True
        except Exception as e:
            raise DependencyError(e)

    def convert_wav():
        try:
            ffmpeg_cover = None
            if script_mode == DOCKER_UTILS:
                docker_dir = os.path.basename(tmp_dir)
                ffmpeg_combined_wav = f'/files/{docker_dir}/' + os.path.basename(combined_wav)
                ffmpeg_metadata_file = f'/files/{docker_dir}/' + os.path.basename(metadata_file)
                ffmpeg_final_file = f'/files/{docker_dir}/' + os.path.basename(final_file)           
                if cover_file is not None:
                    ffmpeg_cover = f'/files/{docker_dir}/' + os.path.basename(cover_file)
                    
                ffmpeg_cmd = ["ffmpeg", '-i', ffmpeg_combined_wav, '-i', ffmpeg_metadata_file]
            else:
                ffmpeg_combined_wav = combined_wav
                ffmpeg_metadata_file = metadata_file
                ffmpeg_final_file = final_file
                if cover_file is not None:
                    ffmpeg_cover = cover_file
                    
                ffmpeg_cmd = [shutil.which("ffmpeg"), '-i', ffmpeg_combined_wav, '-i', ffmpeg_metadata_file]

            if ffmpeg_cover is not None:
                ffmpeg_cmd += ['-i', ffmpeg_cover, '-map', '0:a', '-map', '2:v']
            else:
                ffmpeg_cmd += ['-map', '0:a'] 

            ffmpeg_cmd += ['-map_metadata', '1', '-c:a', 'aac', '-b:a', '128k', '-ar', '44100']
            
            if ffmpeg_cover is not None:
                if ffmpeg_cover.lower().endswith('.png'):
                    ffmpeg_cmd += ['-c:v', 'png', '-disposition:v', 'attached_pic']  # PNG cover
                else:
                    ffmpeg_cmd += ['-c:v', 'copy', '-disposition:v', 'attached_pic']  # JPEG cover (no re-encoding needed)
                    
            if ffmpeg_cover is not None and ffmpeg_cover.lower().endswith('.png'):
                ffmpeg_cmd += ['-pix_fmt', 'yuv420p']
                
            ffmpeg_cmd += ['-movflags', '+faststart', '-y', ffmpeg_final_file]

            if script_mode == DOCKER_UTILS:
                try:
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
                    if shutil.copy(concat_file, final_file):
                        return True

                    return False
                except docker.errors.ContainerError as e:
                    raise DependencyError(e)
                except docker.errors.ImageNotFound as e:
                    raise DependencyError(e)
                except docker.errors.APIError as e:
                    raise DependencyError(e)
            else:
                try:
                    subprocess.run(ffmpeg_cmd, env={}, check=True)
                    return True
                except subprocess.CalledProcessError as e:
                    raise DependencyError(e)
 
        except Exception as e:
            raise DependencyError(e)

    try:
        chapter_files = sorted([os.path.join(ebook_chapters_audio_dir, f) for f in os.listdir(ebook_chapters_audio_dir) if f.endswith('.wav')], key=sort_key)
        combined_wav = os.path.join(tmp_dir, 'combined.wav')
        metadata_file = os.path.join(tmp_dir, 'metadata.txt')

        if combine_chapters():
            if generate_ffmpeg_metadata():
                if ebook_title is None:
                    ebook_title = os.path.splitext(os.path.basename(ebook_src))[0]

                concat_file = os.path.join(tmp_dir, ebook_title + '.' + final_format)
                final_file = os.path.join(audiobooks_dir, os.path.basename(concat_file))       
                if convert_wav():
                    shutil.rmtree(tmp_dir)
                    return final_file
        return None
    except Exception as e:
        raise DependencyError(e)

def create_chapter_labeled_book(ebook_filename_noext):
    global ebook_src, ebook_chapters_dir
    
    def convert_to_epub(ebook_src, epub_path):
        if os.path.basename(ebook_src) == os.path.basename(epub_path):
            return True
        else:
            if script_mode == DOCKER_UTILS:
                try:
                    docker_dir = os.path.basename(tmp_dir)
                    docker_file_in = os.path.basename(ebook_src)
                    docker_file_out = os.path.basename(epub_path)
                    
                    # Check if the input file is already an EPUB
                    if docker_file_in.lower().endswith('.epub'):
                        shutil.copy(ebook_src, epub_path)
                        return True

                    # Convert the ebook to EPUB format using utils Docker image
                    container = client.containers.run(
                        docker_utils_image,
                        command=f"ebook-convert /files/{docker_dir}/{docker_file_in} /files/{docker_dir}/{docker_file_out}",
                        volumes={tmp_dir: {'bind': f'/files/{docker_dir}', 'mode': 'rw'}},
                        remove=True,
                        detach=False,
                        stdout=True,
                        stderr=True
                    )
                    print(container.decode('utf-8'))
                    return True
                except docker.errors.ContainerError as e:
                    raise DependencyError(e)
                except docker.errors.ImageNotFound as e:
                    raise DependencyError(e)
                except docker.errors.APIError as e:
                    raise DependencyError(e)
            else:
                try:
                    util_app = shutil.which("ebook-convert")
                    subprocess.run([util_app, ebook_src, epub_path], check=True)
                    return True
                except subprocess.CalledProcessError as e:
                    remove_conflict_pkg("lxml")
                    raise DependencyError(e)

    def save_chapters_as_text(epub_path):
        try:
            # Open the EPUB file
            ebook = epub.read_epub(epub_path, {'ignore_ncx': False})

            previous_chapter_text = ''
            previous_filename = ''
            chapter_counter = 0

            # Iterate through the items in the EPUB file
            for item in ebook.get_items():
                if cancellation_requested.is_set():
                    msg = "Cancel requested"
                    raise ValueError(msg)

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
            return True
        except Exception as e:
            raise DependencyError(e)

    def process_chapter_files():
        try:
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Text', 'Start Location', 'End Location', 'Is Quote', 'Speaker', 'Chapter'])

                # Process each chapter file
                chapter_files = sorted(
                    [f for f in os.listdir(ebook_chapters_dir) if re.match(r'chapter_\d+\.txt$', f)],
                    key=lambda x: int(x.split('_')[1].split('.')[0])
                )
                for filename in chapter_files:
                    if cancellation_requested.is_set():
                        msg = "Cancel requested"
                        raise ValueError(msg)

                    chapter_number = int(filename.split('_')[1].split('.')[0])
                    file_path = os.path.join(ebook_chapters_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()
                        # Insert "NEWCHAPTERABC" at the beginning of each chapter's text
                        if text:
                            text = "NEWCHAPTERABC" + text
                        sentences = nltk.tokenize.sent_tokenize(text)
                        for sentence in sentences:
                            if cancellation_requested.is_set():
                                msg = "Cancel requested"
                                raise ValueError(msg)
                            start_location = text.find(sentence)
                            end_location = start_location + len(sentence)
                            writer.writerow([sentence, start_location, end_location, 'True', 'Narrator', chapter_number])
            return True
        except Exception as e:
            raise DependencyError(e)

    try:
        epub_path = os.path.join(tmp_dir, ebook_filename_noext + '.epub')       
        if convert_to_epub(ebook_src, epub_path):
            if save_chapters_as_text(epub_path):
                output_csv = os.path.join(tmp_dir, "chapters.csv")
                os.makedirs(os.path.dirname(output_csv), exist_ok=True)
                return process_chapter_files()

        return False
    except Exception as e:
        raise DependencyError(e)

def check_vocab_file(dir):
    vocab_path = os.path.join(dir, 'vocab.json')
    new_vocab_path = os.path.join(dir, 'vocab.json_')
    # Check if vocab.json exists
    if os.path.exists(vocab_path):
        # Rename the file
        os.rename(vocab_path, new_vocab_path)
        print(f"Renamed {vocab_path} to {new_vocab_path}")
        return True

def combine_wav_files(chapters_dir_audio_fragments, ebook_chapters_audio_dir, chapter_wav_file):
    try:
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
            if cancellation_requested.is_set():
                msg = "Cancel requested"
                raise ValueError(msg)
            audio_segment = AudioSegment.from_wav(file)
            combined_audio += audio_segment

        # Export the combined audio to the output file path
        combined_audio.export(output_file, format='wav')
        print(f"Combined audio saved to {output_file}")
    except Exception as e:
        raise DependencyError(e)

def split_long_sentence(sentence, language='en', max_pauses=10):
    """
    Splits a sentence into parts based on length or number of pauses without recursion.
    
    :param sentence: The sentence to split.
    :param language: The language of the sentence (default is English).
    :param max_pauses: Maximum allowed number of pauses in a sentence.
    :return: A list of sentence parts that meet the criteria.
    """
    # Get the Max character length for the selected language -2 : with a default of 248 if no language is found
    char_limits = language_mapping[language]["char_limit"]
    max_length = (char_limits - 2)

    # Adjust the pause punctuation symbols based on language
    if language == 'zh':
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
    try:
        progress_bar = None

        # create gradio progress bar if process come from gradio interface
        if is_gui_process:
            progress_bar = gr.Progress(track_tqdm=True)
        
        # Set default target voice path if not provided
        if target_voice_file is None:
            target_voice_file = default_target_voice_file
        
        # Handle custom model or use standard TTS model
        print("Loading TTS ...")
        if custom_model:
            config_path = custom_model['config']
            model_path = custom_model['model']
            vocab_path = custom_model['vocab']
            config = XttsConfig()
            config.models_dir = models_dir
            config.load_json(config_path)
            tts = Xtts.init_from_config(config)
            tts.load_checkpoint(config, checkpoint_dir=model_path, vocab_path=vocab_path)
        else:
            #selected_tts_model = "tts_models/multilingual/multi-dataset/xtts_v2"
            #tts = TTS(selected_tts_model, progress_bar=False).to(device)
            base_dir = os.path.join(models_dir,"XTTS-v2")
            config_path = os.path.join(base_dir,"config.json")
            config = XttsConfig()
            config.models_dir = models_dir
            config.load_json(config_path)
            tts = Xtts.init_from_config(config)
            tts.load_checkpoint(config, checkpoint_dir=base_dir)
          
        tts.to(device)
        print("Computing speaker latents...")
        gpt_cond_latent, speaker_embedding = tts.get_conditioning_latents(audio_path=[target_voice_file])
        
        chapters_dir_audio_fragments = os.path.join(ebook_chapters_audio_dir, "fragments")
        os.makedirs(chapters_dir_audio_fragments, exist_ok=True)

        # Calculate the total number of chapters and segments (fragments) to set progress bar correctly
        total_segments = 0
        total_chapters = len([f for f in os.listdir(ebook_chapters_dir) if f.endswith('.txt')])
        
        # Check if the language is nltk compatible
        nltk_language = language_mapping[language]["name"].lower() if language_mapping[language] else None

        # Pre-calculate total segments (sentences + fragments per chapter)
        for chapter_file in sorted(os.listdir(ebook_chapters_dir)):
            if cancellation_requested.is_set():
                stop_and_detach_tts(tts)
                msg = "Cancel requested"
                raise ValueError(msg)
            if chapter_file.endswith('.txt'):
                with open(os.path.join(ebook_chapters_dir, chapter_file), 'r', encoding='utf-8') as file:
                    chapter_text = file.read()
                    #if nltk_language is not None:
                        #sentences = nltk.tokenize.sent_tokenize(chapter_text, language=nltk_language)
                        #sentences = nltk.tokenize.word_tokenize(chapter_text, language=nltk_language, preserve_line=False)
                    #else:
                    sentences = [chapter_text]

                    # Calculate total fragments for this chapter
                    for sentence in sentences:
                        fragments = split_long_sentence(sentence, language=language)
                        total_segments += len(fragments)

        current_progress = 0
        total_progress = total_segments + total_chapters  # Total is chapters + segments/fragments

        with tqdm(total=total_progress, desc="Processing 0.00%", bar_format='{desc}: {n_fmt}/{total_fmt} ', unit="step") as t:
            for chapter_file in sorted(os.listdir(ebook_chapters_dir)):
                if cancellation_requested.is_set():
                    stop_and_detach_tts(tts)
                    msg = "Cancel requested"
                    raise ValueError(msg)
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
                        #if nltk_language is not None:
                        #    sentences = nltk.tokenize.sent_tokenize(chapter_text, language=nltk_language)
                            #sentences = nltk.tokenize.word_tokenize(chapter_text, language=nltk_language, preserve_line=False)
                        #else:
                        sentences = [chapter_text]
                        
                        for sentence in sentences:
                            if cancellation_requested.is_set():
                                stop_and_detach_tts(tts)
                                msg = "Cancel requested"
                                raise ValueError(msg)
                            fragments = split_long_sentence(sentence, language=language)
                            for fragment in fragments:
                                if cancellation_requested.is_set():
                                    stop_and_detach_tts(tts)
                                    msg = "Cancel requested"
                                    raise ValueError(msg)
                                if fragment != "":
                                    print(f"Generating fragment: {fragment}...")
                                    fragment_file_path = os.path.join(chapters_dir_audio_fragments, f"{count_fragments}.wav")
                                    
                                    #if custom_tts:
                                    out = tts.inference(
                                        fragment, language, gpt_cond_latent, speaker_embedding, 
                                        temperature=temperature, repetition_penalty=repetition_penalty, 
                                        top_k=top_k, top_p=top_p, speed=speed, enable_text_splitting=enable_text_splitting
                                    )
                                    torchaudio.save(fragment_file_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)
                                    #else:
                                    #    speaker_wav_path = target_voice_file if target_voice_file else default_target_voice_file
                                    #    model.tts_to_file(
                                    #        text=fragment, 
                                    #        file_path=fragment_file_path, 
                                    #        speaker_wav=speaker_wav_path, 
                                    #        language=language, 
                                    #        temperature=temperature, 
                                    #        length_penalty=length_penalty, 
                                    #        repetition_penalty=repetition_penalty, 
                                    #        top_k=top_k, 
                                    #        top_p=top_p, 
                                    #        speed=speed, 
                                    #        enable_text_splitting=enable_text_splitting
                                    #    )
                                    
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
                    if cancellation_requested.is_set():
                        msg = "Cancel requested"
                        raise ValueError(msg)

                    current_progress += 1
                    percentage = (current_progress / total_progress) * 100
                    t.set_description(f"Processing {percentage:.2f}%")
                    t.update(1)

                    # Update Gradio progress bar
                    if progress_bar is not None:
                        progress_bar(current_progress / total_progress)

        return True
    except Exception as e:
        raise DependencyError(e)
    
def stop_and_detach_tts(tts):
    # Move the tts to CPU if on GPU
    if next(tts.parameters()).is_cuda:
        tts.to('cpu')
    del tts
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def delete_old_web_folders(root_dir):
    try:
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
            print(f"Created missing directory: {root_dir}")
        current_time = time.time()
        age_limit = current_time - gradio_shared_expire * 60 * 60  # 24 hours in seconds
        for folder_name in os.listdir(root_dir):
            folder_path = os.path.join(root_dir, folder_name)
            if os.path.isdir(folder_path) and folder_name.startswith("web-"):
                folder_creation_time = os.path.getctime(folder_path)
                if folder_creation_time < age_limit:
                    shutil.rmtree(folder_path)
    except Exception as e:
        raise DependencyError(e)

def convert_ebook(args):
    try:
        global cancellation_requested, client, script_mode, audiobooks_dir, ebook_id, ebook_src, tmp_dir, ebook_chapters_dir, ebook_chapters_audio_dir
        if cancellation_requested.is_set():
            msg = "Cancel requested"
            raise ValueError()
        else:
            ebook_id = args.session if args.session is not None else str(uuid.uuid4())
            script_mode = args.script_mode if args.script_mode is not None else NATIVE
            ebook_src = args.ebook
            device = args.device.lower()
            target_voice_file = args.voice
            language = args.language
            temperature = args.temperature
            length_penalty = args.length_penalty
            repetition_penalty = args.repetition_penalty
            top_k = args.top_k
            top_p = args.top_p
            speed = args.speed
            enable_text_splitting = args.enable_text_splitting
            custom_model_file = args.custom_model
            custom_model_url = args.custom_model_url

            if not os.path.splitext(ebook_src)[1]:
                raise ValueError("The selected ebook file has no extension. Please select a valid file.")

            if script_mode == NATIVE:
                bool, e = check_programs("Calibre", "calibre", "--version")
                if not bool:
                    raise DependencyError(e)
                    
                bool, e = check_programs("FFmpeg", "ffmpeg", "-version")
                if not bool:
                    raise DependencyError(e)
            elif script_mode == DOCKER_UTILS:
                client = docker.from_env()

            tmp_dir = os.path.join(processes_dir, f"ebook-{ebook_id}")
            ebook_chapters_dir = os.path.join(tmp_dir, "chapters")
            ebook_chapters_audio_dir = os.path.join(ebook_chapters_dir, "audio")

            if not is_gui_process:
                audiobooks_dir = audiobooks_cli_dir
                    
            if language != "en":
                ebook_pronouns = translate_pronouns(language)
                
            # Load spaCy model for language analysis (you can switch models based on language)
            #if load_spacy_model(language):
            # Prepare tmp dir and properties
            if prepare_dirs(args.ebook) : 
                
                # Get the name of the ebook file source without extension
                ebook_filename_noext = os.path.splitext(os.path.basename(ebook_src))[0]

                # Handle custom model if the user chose to use one
                custom_model = None
                if custom_model_file and custom_config_file and custom_vocab_file:
                    custom_model = {
                        'model': custom_model_file,
                        'config': custom_config_file,
                        'vocab': custom_vocab_file
                    }

                # If a custom model URL is provided, download and use it
                if custom_model_url:
                    print(f"Received custom model URL: {custom_model_url}")
                    model_dir = get_model_dir_from_url(custom_model_url)
                    if download_and_extract(custom_model_url, model_dir):
                        # Check if vocab.json exists and rename it
                        if check_vocab_file(model_dir):
                            print("vocab.json file was found and renamed.")
                        
                        custom_model = {
                            'model': os.path.join(model_dir, 'model.pth'),
                            'config': os.path.join(model_dir, 'config.json'),
                            'vocab': os.path.join(model_dir, 'vocab.json_')
                        }

                if create_chapter_labeled_book(ebook_filename_noext):
                    if not torch.cuda.is_available() or device == "cpu":
                        if device == "gpu":
                            print("GPU is not available on your device!")
                        device = "cpu"
                            
                    torch.device(device)
                    print(f"Available Processor Unit: {device}")
                    
                    print("Extract Metada and Cover")
                    metadatas, cover_file = extract_metadata_and_cover(ebook_filename_noext)

                    if convert_chapters_to_audio( device, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, target_voice_file, language, custom_model):
                        output_file = concat_audio_chapters(metadatas, cover_file)               
                        if output_file is not None:
                            progress_status = f"Audiobook {os.path.basename(output_file)} created!"
                            print(f"Temporary directory {tmp_dir} removed successfully.")
                            return progress_status, output_file 
                        else:
                            raise DependencyError(f"{output_file} not created!")
                    else:
                        raise DependencyError("convert_chapters_to_audio() failed!")
                else:
                    return None, None
                #else:
                #    return None, None
            else:
                print(f"Temporary directory {tmp_dir} not removed due to failure.")
                return None, None

    except Exception as e:
        print(f"Exception: {e}")
        return None, None

def web_interface(mode, share):
    global ebook_src, is_converting, interface, cancellation_requested, is_gui_process, script_mode, is_gui_shared, audiobooks_ddn

    script_mode = mode
    is_gui_process = True
    is_gui_shared = share
    audiobook_file = None
    language_options = [details["native_name"] for details in language_mapping.values()]
    default_language_native = language_mapping[default_language_code]["native_name"]

    theme = gr.themes.Origin(
        primary_hue="amber",
        secondary_hue="green",
        neutral_hue="gray",
        radius_size="lg",
        font_mono=['JetBrains Mono', 'monospace', 'Consolas', 'Menlo', 'Liberation Mono']
    )

    with gr.Blocks(theme=theme) as interface:
        gr.Markdown(
            f"""
            # Ebook2Audiobook v{version}<br/>
            https://github.com/DrewThomasson/ebook2audiobook<br/>
            Convert eBooks into immersive audiobooks with realistic voice TTS models.
            """
        )
        gr.HTML(
            """
            <style>
                input[type="checkbox"] {
                    border-color: #fafafa !Important;
                }
                .svelte-1xyfx7i.center.boundedheight.flex{
                    height: 120px !important;
                }
                .block.svelte-5y6bt2 {
                    padding: 10px !important;
                    margin: 0 !important;
                    height: auto !important;
                    font-size: 16px !important;
                }
                .wrap.svelte-12ioyct {
                    padding: 0 !important;
                    margin: 0 !important;
                    font-size: 12px !important;
                }
                .block.svelte-5y6bt2.padded {
                    height: auto !important;
                    padding: 10px !important;
                }
                .block.svelte-5y6bt2.padded.hide-container {
                    height: auto !important;
                    padding: 0 !important;
                }
                .waveform-container.svelte-19usgod {
                    padding: 0 !important;
                    margin: 0 !important;
                }
                .component-wrapper.svelte-19usgod {
                    height: 110px !important;
                }
                .timestamps.svelte-19usgod {
                    display: none !important;
                }
                .controls.svelte-ije4bl {
                    padding: 0;
                    margin: 0;
                }
                #component-8, #component-9, #component-34 {
                    height: 119px !important;
                }
            </style>
            """
        )
        with gr.Tabs():
            with gr.TabItem("Input Options"):
                with gr.Row():
                    with gr.Column(scale=3):
                        ebook_file = gr.File(label="eBook File")
                        device = gr.Radio(label="Processor Unit", choices=["CPU", "GPU"], value="CPU")
                        language = gr.Dropdown(label="Language", choices=language_options, value=default_language_native)  
                    with gr.Column(scale=3):
                        with gr.Group():
                            target_voice_file = gr.File(label="Cloning Voice* (a .wav or .mp3 no more than 12sec)")
                            custom_model_file = gr.File(label="Model* (a .zip containing config.json, vocab.json, model.pth)")
                            custom_model_url = gr.Textbox(placeholder="https://www.example.com/model.zip", label="Model from URL*")
                            gr.Markdown('<p>* Optional</p>')
            with gr.TabItem("Audio Generation Preferences"):
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
                
        session_status = gr.Textbox(label="Session")
        session = gr.Textbox(label="Session", visible=False)
        conversion_progress = gr.Textbox(label="Progress")
        convert_btn = gr.Button("Convert", variant="primary", interactive=False)
        audio_player = gr.Audio(label="Listen", type="filepath", visible=False)
        audiobooks_ddn = gr.Dropdown(choices=[], label="Audiobooks")
        audiobook_link = gr.File(label="Download")
        write_data = gr.JSON(visible=False)
        read_data = gr.JSON(visible=False)
        data = gr.State({})
        modal_html = gr.HTML()

        def show_modal(message):
            return f"""
            <style>
                .modal {{
                    display: none; /* Hidden by default */
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.5);
                    z-index: 9999;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                .modal-content {{
                    background-color: #333;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    max-width: 300px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
                    border: 2px solid #FFA500;
                    color: white;
                    font-family: Arial, sans-serif;
                    position: relative;
                }}
                .modal-content p {{
                    margin: 10px 0;
                }}
                /* Spinner */
                .spinner {{
                    margin: 15px auto;
                    border: 4px solid rgba(255, 255, 255, 0.2);
                    border-top: 4px solid #FFA500;
                    border-radius: 50%;
                    width: 30px;
                    height: 30px;
                    animation: spin 1s linear infinite;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
            <div id="custom-modal" class="modal">
                <div class="modal-content">
                    <p>{message}</p>
                    <div class="spinner"></div> <!-- Spinner added here -->
                </div>
            </div>
            """

        def hide_modal():
            return ""

        def update_interface():
            global ebook_src, is_converting
            ebook_src = None
            is_converting = False
            return gr.Button("Convert", variant="primary", interactive=False), None, audiobook_file, update_audiobooks_ddn()

        def refresh_audiobook_list():
            files = []
            if audiobooks_dir is not None:
                if not os.path.isdir(audiobooks_dir):
                    os.makedirs(audiobooks_dir, exist_ok=True)
                files = [f for f in os.listdir(audiobooks_dir)]
                files.sort(key=lambda x: os.path.getmtime(os.path.join(audiobooks_dir, x)), reverse=True)
            return files

        def update_audiobook_link(audiobook):
            if audiobooks_dir is not None:
                if audiobook:
                    link = os.path.join(audiobooks_dir, audiobook)
                    return link, link, gr.update(visible=True)
            return None, None, gr.update(visible=False)
            
        def disable_convert_btn():
            return gr.Button("Convert", variant="primary", interactive=False)

        def update_audiobooks_ddn():
            files = refresh_audiobook_list()
            return gr.Dropdown(choices=files, label="Audiobooks", value=files[0] if files else None)

        def change_ebook_file(btn, f):
            global ebook_src, is_converting, cancellation_requested
            if f is None:
                ebook_src = None
                if is_converting:
                    cancellation_requested.set()
                    yield gr.Button(interactive=False), show_modal("cancellation requested, Please wait...")
                else:
                    cancellation_requested.clear()
                    yield gr.Button(interactive=False), hide_modal()
            else:
                cancellation_requested.clear()
                yield gr.Button(interactive=bool(f)), hide_modal()

        def change_data(data):
            data["event"] = 'change_data'
            return data

        def process_conversion(session, device, ebook_file, target_voice_file, language, custom_model_file, custom_model_url, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting):                             
            global ebook_src, is_converting, audiobook_file

            ebook_src = ebook_file.name if ebook_file else None
            target_voice_file = target_voice_file.name if target_voice_file else None
            custom_model_file = custom_model_file.name if custom_model_file else None
            language = next((code for code, details in language_mapping.items() if details["native_name"] == language), None)

            if not ebook_src:
                return "Error: eBook file is required."

            # Call the convert_ebook function with the processed parameters
            args = argparse.Namespace(
                session=session,
                script_mode=script_mode,
                device=device.lower(),
                ebook=ebook_src,
                voice=target_voice_file,
                language=language,
                custom_model=custom_model_file,
                custom_model_url=custom_model_url,
                temperature=float(temperature),
                length_penalty=float(length_penalty),
                repetition_penalty=float(repetition_penalty),
                top_k=int(top_k),
                top_p=float(top_p),
                speed=float(speed),
                enable_text_splitting=enable_text_splitting
            )
            
            try:
                is_converting = True
                progress_status, audiobook_file = convert_ebook(args)

                if audiobook_file is None:
                    if is_converting:
                        is_converting = False
                        return "Conversion cancelled.", hide_modal()
                    else:
                        return "Conversion failed.", hide_modal()
                else:
                    return progress_status, hide_modal()
            except Exception as e:
                raise DependencyError(e)

        def init_data(data):
            global audiobooks_dir
            warning_text_extra = ""
            if is_gui_shared:
                warning_text_extra = f" Note: access limit time: {gradio_shared_expire} hours"
            if not data:
                data = {"session_id": str(uuid.uuid4())}
                warning_text = f"Session: {data['session_id']}"
            else:
                if "session_id" not in data:
                    data["session_id"] = str(uuid.uuid4())
                warning_text = data["session_id"]
                event = data.get('event', '')
                if event != 'load':
                    return [gr.update(), gr.update(), gr.update()]
            if is_gui_shared:
                audiobooks_dir = os.path.join(audiobooks_gradio_dir, f"web-{data['session_id']}")
                delete_old_web_folders(audiobooks_gradio_dir)
            else:
                audiobooks_dir = os.path.join(audiobooks_host_dir, f"web-{data['session_id']}")
            return [data, f"{warning_text}{warning_text_extra}", data["session_id"], update_audiobooks_ddn()]

        ebook_file.change(
            fn=change_ebook_file,
            inputs=[convert_btn, ebook_file],
            outputs=[convert_btn, modal_html]
        )
        audiobooks_ddn.change(
            fn=update_audiobook_link,
            inputs=audiobooks_ddn,
            outputs=[audiobook_link, audio_player, audio_player]
        )
        session.change(
            fn=change_data,
            inputs=data,
            outputs=write_data
        )
        write_data.change(
            fn=None,
            inputs=write_data,
            js="""
            (data) => {
              localStorage.clear();
              console.log(data);
              window.localStorage.setItem('data', JSON.stringify(data));
            }
            """
        )       
        read_data.change(
            fn=init_data,
            inputs=read_data,
            outputs=[data, session_status, session, audiobooks_ddn]
        )
        convert_btn.click(
           fn=disable_convert_btn,
           inputs=None,
           outputs=convert_btn
        ).then(
            fn=process_conversion,
            inputs=[
                session, device, ebook_file, target_voice_file, language, 
                custom_model_file, custom_model_url, temperature, length_penalty,
                repetition_penalty, top_k, top_p, speed, enable_text_splitting
            ],
            outputs=[conversion_progress, modal_html]           
        ).then(
            fn=update_interface,
            inputs=None,
            outputs=[convert_btn, ebook_file, audio_player, audiobooks_ddn]
        )
        interface.load(
            fn=None,
            js="""
            () => {
              const dataStr = window.localStorage.getItem('data');
              if (dataStr) {
                const obj = JSON.parse(dataStr);
                obj.event = 'load';
                console.log(obj);
                return obj;
              }
              return null;
            }
            """,
            outputs=read_data
        )

    try:
        interface.queue(default_concurrency_limit=concurrency_limit)
        interface.launch(server_name="0.0.0.0", server_port=gradio_interface_port, share=share)
    except OSError as e:
        print(f"Connection error: {e}")
    except socket.error as e:
        print(f"Socket error: {e}")
    except KeyboardInterrupt:
        print("Server interrupted by user. Shutting down...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")