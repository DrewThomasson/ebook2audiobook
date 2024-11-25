import argparse
import csv
import docker
import ebooklib
import gradio as gr
import os
import regex as re
import requests
import shutil
import socket
import subprocess
import sys
import threading
import time
import torch
import torchaudio
import urllib.request
import uuid
import zipfile
import traceback

from bs4 import BeautifulSoup
from ebooklib import epub
from iso639 import languages
from pydub import AudioSegment
from datetime import datetime
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
audiobooks_dir = None
tmp_dir = None
ebook = {}
metadata_fields = [
    'title', 'creator', 'contributor', 'language', 'identifier', 
    'publisher', 'date', 'description', 'subject', 'rights', 
    'format', 'type', 'coverage', 'relation', 'Source', 'Modified'
]

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

def check_missing_files(folder_path, file_list):
    if not os.path.exists(folder_path):
        return False, "Folder does not exist", file_list
    existing_files = os.listdir(folder_path)
    missing_files = [file for file in file_list if file not in existing_files]
    if missing_files:
        return False, "Some files are missing", missing_files
    return True, "All files are present", []

def download_model(dest_dir, url):
    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        zip_path = os.path.join(dest_dir, models["xtts"]["sip"])
        print("Downloading the XTTS v2 model...")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 1024  # Download in chunks of 1KB
        with open(zip_path, "wb") as file, tqdm(
            total=total_size, unit='B', unit_scale=True, desc="Downloading"
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)
                progress_bar.update(len(chunk))
        print("Extracting the model files...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(dest_dir)
        os.remove(zip_path)
        print("Model downloaded, extracted, and zip file removed successfully.")
    except Exception as e:
        raise DependencyError(e)

def prepare_dirs(src):
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        os.makedirs(audiobooks_dir, exist_ok=True)
        os.makedirs(ebook["chapters_dir"], exist_ok=True)
        os.makedirs(ebook["chapters_audio_dir"], exist_ok=True)
        ebook["src"] = os.path.join(tmp_dir, os.path.basename(src))
        shutil.copy(src, ebook["src"])
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

def get_model_dir_from_url(url):
    try:
        parsed_url = urlparse(url)
        model_dir_name = os.path.basename(parsed_url.path)
        model_dir = os.path.join(".","models",model_dir_name)
        os.makedirs(model_dir, exist_ok=True)
        return model_dir
    except Exception as e:
        raise DependencyError(e)
    
def get_custom_model(path_or_url, extract_to=models_dir):
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

def convert_to_epub():
    if script_mode == DOCKER_UTILS:
        try:
            docker_dir = os.path.basename(tmp_dir)
            docker_file_in = os.path.basename(ebook["src"])
            docker_file_out = os.path.basename(ebook["epub_path"])
            
            # Check if the input file is already an EPUB
            if docker_file_in.lower().endswith('.epub'):
                shutil.copy(ebook["src"], ebook["epub_path"])
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
            subprocess.run([util_app, ebook["src"], ebook["epub_path"]], check=True)
            return True
        except subprocess.CalledProcessError as e:
            remove_conflict_pkg("lxml")
            raise DependencyError(e)

def get_cover():
    try:
        cover_image = None
        cover_path = os.path.join(tmp_dir, ebook["filename_noext"] + '.jpg')
        cover_file = None
        for item in ebook["epub"].get_items_of_type(ebooklib.ITEM_COVER):
            cover_image = item.get_content()
            break
        if cover_image is None:
            for item in ebook["epub"].get_items_of_type(ebooklib.ITEM_IMAGE):
                if 'cover' in item.file_name.lower() or 'cover' in item.get_id().lower():
                    cover_image = item.get_content()
                    break
        if cover_image:
            with open(cover_path, 'wb') as cover_file:
                cover_file.write(cover_image)
        return cover_path
    except Exception as e:
        raise DependencyError(e)

def concat_audio_chapters():
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
        try:
            ffmpeg_metadata = ";FFMETADATA1\n"        
            if ebook["metadata"].get("title"):
                ffmpeg_metadata += f"title={ebook["metadata"]["title"]}\n"              
            if ebook["metadata"].get("creator"):
                ffmpeg_metadata += f"artist={ebook["metadata"]["creator"]}\n"
            if ebook["metadata"].get("language"):
                ffmpeg_metadata += f"language={ebook["metadata"]["language"]}\n\n"
            if ebook["metadata"].get("publisher"):
                ffmpeg_metadata += f"publisher={ebook["metadata"]["publisher"]}\n"              
            if ebook["metadata"].get("description"):
                ffmpeg_metadata += f"description={ebook["metadata"]["description"]}\n"  # Description
            if ebook["metadata"].get("published"):
                # Check if the timestamp contains fractional seconds
                if '.' in ebook["metadata"]["published"]:
                    # Parse with fractional seconds
                    year = datetime.strptime(ebook["metadata"]["published"], "%Y-%m-%dT%H:%M:%S.%f%z").year
                else:
                    # Parse without fractional seconds
                    year = datetime.strptime(ebook["metadata"]["published"], "%Y-%m-%dT%H:%M:%S%z").year
            else:
                # If published is not provided, use the current year
                year = datetime.now().year
            ffmpeg_metadata += f"year={year}\n"
            if ebook["metadata"].get("identifiers") and isinstance(ebook["metadata"].get("identifiers"), dict):
                isbn = ebook["metadata"]["identifiers"].get("isbn", None)
                if isbn:
                    ffmpeg_metadata += f"isbn={isbn}\n"  # ISBN
                mobi_asin = ebook["metadata"]["identifiers"].get("mobi-asin", None)
                if mobi_asin:
                    ffmpeg_metadata += f"asin={mobi_asin}\n"  # ASIN                   

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
                if ebook["cover"] is not None:
                    ffmpeg_cover = f'/files/{docker_dir}/' + os.path.basename(ebook["cover"])
                    
                ffmpeg_cmd = ["ffmpeg", '-i', ffmpeg_combined_wav, '-i', ffmpeg_metadata_file]
            else:
                ffmpeg_combined_wav = combined_wav
                ffmpeg_metadata_file = metadata_file
                ffmpeg_final_file = final_file
                if ebook["cover"] is not None:
                    ffmpeg_cover = ebook["cover"]
                    
                ffmpeg_cmd = [shutil.which("ffmpeg"), '-i', ffmpeg_combined_wav, '-i', ffmpeg_metadata_file]

            if ffmpeg_cover is not None:
                ffmpeg_cmd += ['-i', ffmpeg_cover, '-map', '0:a', '-map', '2:v']
            else:
                ffmpeg_cmd += ['-map', '0:a'] 

            ffmpeg_cmd += ['-map_metadata', '1', '-c:a', 'aac', '-b:a', '128k', '-ar', '44100']
            
            if ffmpeg_cover is not None:
                if ffmpeg_cover.endswith('.png'):
                    ffmpeg_cmd += ['-c:v', 'png', '-disposition:v', 'attached_pic']  # PNG cover
                else:
                    ffmpeg_cmd += ['-c:v', 'copy', '-disposition:v', 'attached_pic']  # JPEG cover (no re-encoding needed)
                    
            if ffmpeg_cover is not None and ffmpeg_cover.endswith('.png'):
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
        chapter_files = sorted([os.path.join(ebook["chapters_audio_dir"], f) for f in os.listdir(ebook["chapters_audio_dir"]) if f.endswith('.wav')], key=sort_key)
        combined_wav = os.path.join(tmp_dir, 'combined.wav')
        metadata_file = os.path.join(tmp_dir, 'metadata.txt')

        if combine_chapters():
            if generate_ffmpeg_metadata():
                if not ebook["metadata"].get("title"):
                    ebook["metadata"]["title"] = os.path.splitext(os.path.basename(ebook["src"]))[0]

                concat_file = os.path.join(tmp_dir, ebook["metadata"]["title"] + '.' + audiobook_format)
                final_file = os.path.join(audiobooks_dir, os.path.basename(concat_file))       
                if convert_wav():
                    shutil.rmtree(tmp_dir)
                    return final_file
        return None
    except Exception as e:
        raise DependencyError(e)

def get_chapters(language):
    def save_chapter_files():
        try:
            previous_chapter_text = ''
            previous_filename = ''
            chapter_counter = 1
            for item in ebook["epub"].get_items():
                if cancellation_requested.is_set():
                    msg = "Cancel requested"
                    raise ValueError(msg)
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = soup.get_text()
                    text = re.sub(r'\[.*?\]', '', text)
                    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
                    text = re.sub(r'\n{4,}', '\n\n\n', text)
                    text = text.strip()
                    if text:
                        if len(text) < 2300 and previous_filename:
                            # Append text to the previous chapter if it's short
                            with open(previous_filename, 'a', encoding='utf-8') as file:
                                file.write('\n' + text)
                        else:
                            # Create a new chapter file and increment the counter
                            previous_filename = os.path.join(ebook["chapters_dir"] , f"chapter_{chapter_counter}.txt")
                            chapter_counter += 1
                            with open(previous_filename, 'w', encoding='utf-8') as file:
                                file.write(text)
                                print(f"Saved chapter: {previous_filename}")
            return True
        except Exception as e:
            raise DependencyError(e)

    def save_csv():
        try:
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Text', 'Start Location', 'End Location', 'Is Quote', 'Speaker', 'Chapter'])
                chapter_files = sorted(
                    [f for f in os.listdir(ebook["chapters_dir"]) if re.match(r'chapter_\d+\.txt$', f)],
                    key=lambda x: int(x.split('_')[1].split('.')[0])
                )
                for filename in chapter_files:
                    if cancellation_requested.is_set():
                        msg = "Cancel requested"
                        raise ValueError(msg)
                    chapter_number = int(filename.split('_')[1].split('.')[0])
                    file_path = os.path.join(ebook["chapters_dir"], filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()
                        # Insert "NEWCHAPTERABC" at the beginning of each chapter's text
                        if text:
                            text = "NEWCHAPTERABC" + text
                        sentences = get_sentences(text, language)
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
        if save_chapter_files():
            output_csv = os.path.join(tmp_dir, "chapters.csv")
            os.makedirs(os.path.dirname(output_csv), exist_ok=True)
            return save_csv()
        return False
    except Exception as e:
        raise DependencyError(e)

def check_vocab_file(dir):
    vocab_path = os.path.join(dir, 'vocab.json')
    new_vocab_path = os.path.join(dir, 'vocab.json_')
    if os.path.exists(vocab_path):
        os.rename(vocab_path, new_vocab_path)
        print(f"Renamed {vocab_path} to {new_vocab_path}")
        return True

def combine_wav_files(chapters_dir_audio_sentences, chapter_wav_file):
    try:
        output_file = os.path.join(ebook["chapters_audio_dir"], chapter_wav_file)
        combined_audio = AudioSegment.empty()
        sentences_dir_ordered = sorted(
            [os.path.join(chapters_dir_audio_sentences, f) for f in os.listdir(chapters_dir_audio_sentences) if f.endswith(".wav")],
            key=lambda f: int(''.join(filter(str.isdigit, f)))
        )
        for file in sentences_dir_ordered:
            if cancellation_requested.is_set():
                msg = "Cancel requested"
                raise ValueError(msg)
            audio_segment = AudioSegment.from_wav(file)
            combined_audio += audio_segment
        combined_audio.export(output_file, format='wav')
        print(f"Combined audio saved to {output_file}")
    except Exception as e:
        raise DependencyError(e)

def get_sentences(sentence, language, max_pauses=4):
    max_length = language_mapping[language]["char_limit"]
    punctuation = language_mapping[language]["punctuation"]
    parts = []
    while len(sentence) > max_length or sum(sentence.count(p) for p in punctuation) > max_pauses:
        possible_splits = [i for i, char in enumerate(sentence[:max_length]) if char in punctuation]     
        if possible_splits:
            split_at = possible_splits[-1] + 1
        else:
            last_space = sentence.rfind(' ', 0, max_length)
            if last_space != -1:
                split_at = last_space + 1
            else:
                split_at = max_length
        parts.append(sentence[:split_at].strip())
        sentence = sentence[split_at:].strip()
    if sentence:
        parts.append(sentence)
    return parts

def convert_chapters_to_audio(device, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, target_voice_file=None, language=default_language_code, custom_model=None):
    try:
        progress_bar = None

        # create gradio progress bar if process come from gradio interface
        if is_gui_process:
            progress_bar = gr.Progress(track_tqdm=True)
        
        # Set default target voice path if not provided
        if target_voice_file is None:
            target_voice_file = default_target_voice_file
        
        # Handle custom model or use standard TTS model
        print("Loading TTS model ...")
        if custom_model:
            try:
                config_path = custom_model['config']
                model_path = custom_model['model']
                vocab_path = custom_model['vocab']
                config = XttsConfig()
                config.models_dir = models_dir
                config.load_json(config_path)
                tts = Xtts.init_from_config(config)
                tts.to(device)
                tts.load_checkpoint(config, checkpoint_dir=model_path, vocab_path=vocab_path)
                print("Computing speaker latents...")
                gpt_cond_latent, speaker_embedding = tts.get_conditioning_latents(audio_path=[target_voice_file])
            except Exception as e:
                print("Custom model not compatible with TTS")
                raise DependencyError(e)
        else:
            which_tts = None
            try:
                if language in language_xtts:
                    which_tts = "xtts"
                    base_dir = models["xtts"]["local"]
                    config_path = os.path.join(base_dir,"config.json")
                    config = XttsConfig()
                    config.models_dir = models_dir
                    config.load_json(config_path)
                    tts = Xtts.init_from_config(config)
                    tts.to(device)
                    tts.load_checkpoint(config, checkpoint_dir=base_dir)
                    language_iso1 = language_xtts[language]
                    print("Computing speaker latents...")
                    gpt_cond_latent, speaker_embedding = tts.get_conditioning_latents(audio_path=[target_voice_file])
                else:
                    which_tts = "mms"
                    mms_dir = os.path.join(models_dir,"mms")
                    local_model_path = os.path.join(mms_dir, f"tts_models/{language}/fairseq/vits")
                    if os.path.isdir(local_model_path):
                        tts = TTS(local_model_path)
                    else:
                        tts = TTS(f"tts_models/{language}/fairseq/vits")
                    tts.to(device)
            except Exception as e:
                print("Model cannot be loaded!")
                raise DependencyError(e)           
 
        chapters_dir_audio_sentences = os.path.join(ebook["chapters_audio_dir"], "sentences")
        os.makedirs(chapters_dir_audio_sentences, exist_ok=True)
        
        # Chapters array
        chapters_mapping = {}
        
        # Calculate the total number of chapters and segments (sentences) to set progress bar correctly
        chapters_file_array = sorted([f for f in os.listdir(ebook["chapters_dir"]) if f.endswith('.txt')])
        total_chapters = len(chapters_file_array)
        total_sentences = 0

        # Pre-calculate total segments (sentences + sentences per chapter)
        for x in range(total_chapters):            
            chapter_file = chapters_file_array[x]
            with open(os.path.join(ebook["chapters_dir"], chapter_file), 'r', encoding='utf-8') as file:
                chapter_text = file.read()
                sentences = get_sentences(chapter_text, language)
                total_sentences += len(sentences)
                chapters_mapping[x] = {"file": chapter_file, "sentences": sentences}

        current_progress = 0
        total_progress = total_sentences

        with tqdm(total=total_progress, desc="Processing 0.00%", bar_format='{desc}: {n_fmt}/{total_fmt} ', unit="step") as t:
            for x in range(total_chapters):
                if cancellation_requested.is_set():
                    stop_and_detach_tts(tts)
                    msg = "Cancel requested"
                    raise ValueError(msg)

                chapter_file_path = os.path.join(ebook["chapters_dir"], chapters_mapping[x]["file"])
                chapter_num = (x + 1)
                chapter_wav_file = f"chapter_{chapter_num}.wav"
                current_sentence = 1
                with open(chapter_file_path, 'r', encoding='utf-8') as file:
                    chapter_text = file.read()
                    sentences = chapters_mapping[x]["sentences"]
                    for sentence in sentences:
                        if cancellation_requested.is_set():
                            stop_and_detach_tts(tts)
                            msg = "Cancel requested"
                            raise ValueError(msg)
                        print(f"Generating sentence: {sentence}...")
                        sentence_file_path = os.path.join(chapters_dir_audio_sentences, f"{current_sentence}.wav")
                        if which_tts == "xtts":
                            output = tts.inference(
                                text=sentence, language=language_iso1, gpt_cond_latent=gpt_cond_latent, speaker_embedding=speaker_embedding, 
                                temperature=temperature, repetition_penalty=repetition_penalty, top_k=top_k, top_p=top_p, 
                                speed=speed, enable_text_splitting=enable_text_splitting, prosody=None
                            )
                            torchaudio.save(sentence_file_path, torch.tensor(output["wav"]).unsqueeze(0), 24000)
                        else:
                            tts.tts_with_vc_to_file(
                                text=sentence,
                                #language=language, # can be used only if multilingual model
                                speaker_wav=target_voice_file,
                                file_path=sentence_file_path,
                                split_sentences=True
                            )
                        current_progress += 1
                        percentage = (current_progress / total_progress) * 100
                        t.set_description(f"Processing {percentage:.2f}%")
                        t.update(1)
                        if progress_bar is not None:
                            progress_bar(current_progress / total_progress)
                        current_sentence += 1

                # Combine audio sentences
                combine_wav_files(chapters_dir_audio_sentences, chapter_wav_file)
                print(f"Converted chapter {chapter_num} to audio.")
        return True
    except Exception as e:
        raise DependencyError(e)
        
def roman_to_int(roman):
    roman_numerals = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    total = 0
    prev_value = 0

    for char in reversed(roman):
        value = roman_numerals[char]
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value

    return total
    
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
        global cancellation_requested, client, script_mode, audiobooks_dir, tmp_dir
        if cancellation_requested.is_set():
            msg = "Cancel requested"
            raise ValueError()
        else:
            error = None
            try:
                if len(args.language) == 2:
                    lang_array = languages.get(alpha2=args.language)
                    if lang_array and lang_array.part3:
                        args.language = lang_array.part3
                    else:
                        args.language = None
                else:
                    lang_array = languages.get(part3=args.language)               
                    if not lang_array:
                        args.language = None
            except Exception as e:
                args.language = None
                pass

            if args.language is not None and args.language in language_mapping.keys():
                ebook["src"] = args.ebook
                ebook["id"] = args.session if args.session is not None else str(uuid.uuid4())
                script_mode = args.script_mode if args.script_mode is not None else NATIVE        
                device = args.device.lower()
                target_voice_file = args.voice
                language = args.language
                temperature = args.temperature
                length_penalty = args.length_penalty
                repetition_penalty = args.repetition_penalty
                top_k = args.top_k
                top_p = args.top_p
                speed = args.speed
                enable_text_splitting = args.enable_text_splitting if args.enable_text_splitting is not None else True
                custom_model_file = args.custom_model
                custom_model_url = args.custom_model_url if custom_model_file is None else None

                if not os.path.splitext(ebook["src"])[1]:
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

                tmp_dir = os.path.join(processes_dir, f"ebook-{ebook["id"]}")
                ebook["chapters_dir"] = os.path.join(tmp_dir, "chapters")
                ebook["chapters_audio_dir"] = os.path.join(ebook["chapters_dir"], "audio")

                if not is_gui_process:
                    audiobooks_dir = audiobooks_cli_dir

                if prepare_dirs(args.ebook) :             
                    ebook["filename_noext"] = os.path.splitext(os.path.basename(ebook["src"]))[0]
                    custom_model = None
                    if custom_model_file and custom_config_file and custom_vocab_file:
                        custom_model = {
                            'model': custom_model_file,
                            'config': custom_config_file,
                            'vocab': custom_vocab_file
                        }

                    if custom_model_url:
                        print(f"Received custom model URL: {custom_model_url}")
                        model_dir = get_model_dir_from_url(custom_model_url)
                        if get_custom_model(custom_model_url, model_dir):
                            # Check if vocab.json exists and rename it
                            if check_vocab_file(model_dir):
                                print("vocab.json file was found and renamed.")
                            
                            custom_model = {
                                'model': os.path.join(model_dir, 'model.pth'),
                                'config': os.path.join(model_dir, 'config.json'),
                                'vocab': os.path.join(model_dir, 'vocab.json_')
                            }
                    if not torch.cuda.is_available() or device == "cpu":
                        if device == "gpu":
                            print("GPU is not available on your device!")
                        device = "cpu"
                            
                    torch.device(device)
                    print(f"Available Processor Unit: {device}")   
                    ebook["epub_path"] = os.path.join(tmp_dir, ebook["filename_noext"] + '.epub')
                    if convert_to_epub():
                        ebook["epub"] = epub.read_epub(ebook["epub_path"], {'ignore_ncx': False})
                        ebook["metadata"] = {}
                        for field in metadata_fields:
                            data = ebook["epub"].get_metadata("DC", field)
                            if data:
                                for value, attributes in data:
                                    ebook["metadata"][field] = value
                        language_iso1 = None      
                        language_array = languages.get(part3=language)
                        if language_array and language_array.part1:
                            language_iso1 = language_array.part1
                        if ebook["metadata"]["language"] == language or ebook["metadata"]["language"] == language_iso1:
                            ebook["metadata"]["creator"] = ", ".join(creator[0] for creator in ebook["metadata"]["creator"])
                            ebook["cover"] = get_cover()
                            if get_chapters(language):
                                if convert_chapters_to_audio( device, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, target_voice_file, language, custom_model):
                                    output_file = concat_audio_chapters()               
                                    if output_file is not None:
                                        progress_status = f"Audiobook {os.path.basename(output_file)} created!"
                                        print(f"Temporary directory {tmp_dir} removed successfully.")
                                        return progress_status, output_file 
                                    else:
                                        error = f"{output_file} not created!"
                                        print(error)
                                else:
                                    error = "convert_chapters_to_audio() failed!"
                                    print(error)
                            else:
                                error = "get_chapters() failed!"
                                print(error)
                        else:
                            error = f'Ebook language: {ebook["metadata"]["language"]}, language selected: {language}'
                            print(error)
                    else:
                        error = "get_chapters() failed!"
                        print(error)
                else:
                    error = f"Temporary directory {tmp_dir} not removed due to failure."
                    print(error)
            else:
                error = f"Language {args.language} is not supported."
                print(error)
            return error, None
    except Exception as e:
        print(f"Exception: {e}")
        return e, None
        
def normalize_string(s):
    return re.sub(r"[^\p{L}\p{N}]", "", s).lower()

def web_interface(mode, share):
    global is_converting, interface, cancellation_requested, is_gui_process, script_mode, is_gui_shared

    script_mode = mode
    is_gui_process = True
    is_gui_shared = share
    audiobook_file = None
    language_options = [
        (
            f'{details["name"]} - {details["native_name"]}' if details["name"] != details["native_name"] else details["name"],
            lang
        )
        for lang, details in language_mapping.items()
    ]
    default_language_name =  next((name for name, key in language_options if key == default_language_code), None)

    theme = gr.themes.Origin(
        primary_hue="amber",
        secondary_hue="green",
        neutral_hue="gray",
        radius_size="lg",
        font_mono=['JetBrains Mono', 'monospace', 'Consolas', 'Menlo', 'Liberation Mono']
    )

    with gr.Blocks(theme=theme) as interface:
        gr.HTML(
            """
            <style>
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
                    height: 58px !important;
                    overflow: hidden !important;
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
                    padding: 0 !important;
                    margin: 0 !important;
                }
                #component-7, #component-13, #component-14 {
                    height: 130px !important;
                }
            </style>
            """
        )
        gr.Markdown(
            f"""
            # Ebook2Audiobook v{version}<br/>
            https://github.com/DrewThomasson/ebook2audiobook<br/>
            Convert eBooks into immersive audiobooks with realistic voice TTS models.
            """
        )
        with gr.Tabs():
            with gr.TabItem("Input Options"):
                with gr.Row():
                    with gr.Column(scale=3):
                        gr_ebook_file = gr.File(label="eBook File")
                        gr_device = gr.Radio(label="Processor Unit", choices=["CPU", "GPU"], value="CPU")
                        gr_language = gr.Dropdown(label="Language", choices=[name for name, _ in language_options], value=default_language_name)  
                    with gr.Column(scale=3):
                        with gr.Group():
                            gr_target_voice_file = gr.File(label="Cloning Voice* (a .wav or .mp3 no more than 12sec)", file_types=[".wav", ".mp3"])
                            gr_custom_model_file = gr.File(label="Model* (a .zip containing config.json, vocab.json, model.pth)", file_types=[".zip"], visible=True)
                            gr_custom_model_url = gr.Textbox(placeholder="https://www.example.com/model.zip", label="Model from URL*", visible=True)
                            gr.Markdown('<p>&nbsp;&nbsp;* Optional</p>')
            with gr.TabItem("Audio Generation Preferences"):
                gr.Markdown(
                    """
                    ### Customize Audio Generation Parameters
                    Adjust the settings below to influence how the audio is generated. You can control the creativity, speed, repetition, and more.
                    """
                )
                gr_temperature = gr.Slider(
                    label="Temperature", 
                    minimum=0.1, 
                    maximum=10.0, 
                    step=0.1, 
                    value=0.65,
                    info="Higher values lead to more creative, unpredictable outputs. Lower values make it more monotone."
                )
                gr_length_penalty = gr.Slider(
                    label="Length Penalty", 
                    minimum=0.5, 
                    maximum=10.0, 
                    step=0.1, 
                    value=1.0, 
                    info="Penalize longer sequences. Higher values produce shorter outputs. Not applied to custom models."
                )
                gr_repetition_penalty = gr.Slider(
                    label="Repetition Penalty", 
                    minimum=1.0, 
                    maximum=10.0, 
                    step=0.1, 
                    value=3.0, 
                    info="Penalizes repeated phrases. Higher values reduce repetition."
                )
                gr_top_k = gr.Slider(
                    label="Top-k Sampling", 
                    minimum=10, 
                    maximum=100, 
                    step=1, 
                    value=50, 
                    info="Lower values restrict outputs to more likely words and increase speed at which audio generates."
                )
                gr_top_p = gr.Slider(
                    label="Top-p Sampling", 
                    minimum=0.1, 
                    maximum=1.0, 
                    step=.01, 
                    value=0.8, 
                    info="Controls cumulative probability for word selection. Lower values make the output more predictable and increase speed at which audio generates."
                )
                gr_speed = gr.Slider(
                    label="Speed", 
                    minimum=0.5, 
                    maximum=3.0, 
                    step=0.1, 
                    value=1.0, 
                    info="Adjusts how fast the narrator will speak."
                )
                gr_enable_text_splitting = gr.Checkbox(
                    label="Enable Text Splitting", 
                    value=True,
                    info="Splits long texts into sentences to generate audio in chunks. Useful for very long inputs."
                )
                
        gr_session_status = gr.Textbox(label="Session")
        gr_session = gr.Textbox(label="Session", visible=False)
        gr_conversion_progress = gr.Textbox(label="Progress")
        gr_convert_btn = gr.Button("Convert", variant="primary", interactive=False)
        gr_audio_player = gr.Audio(label="Listen", type="filepath", show_download_button=False, container=True, visible=False)
        gr_audiobooks_ddn = gr.Dropdown(choices=[], label="Audiobooks")
        gr_audiobook_link = gr.File(label="Download")
        gr_write_data = gr.JSON(visible=False)
        gr_read_data = gr.JSON(visible=False)
        gr_data = gr.State({})
        gr_modal_html = gr.HTML()

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
            global is_converting
            ebook["src"] = None
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

        def change_gr_audiobooks_ddn(audiobook):
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

        def change_gr_ebook_file(btn, f):
            global is_converting, cancellation_requested
            if f is None:
                ebook["src"] = None
                if is_converting:
                    cancellation_requested.set()
                    yield gr.Button(interactive=False), show_modal("cancellation requested, Please wait...")
                else:
                    cancellation_requested.clear()
                    yield gr.Button(interactive=False), hide_modal()
            else:
                cancellation_requested.clear()
                yield gr.Button(interactive=bool(f)), hide_modal()
        
        def change_gr_language(selected: str) -> str:
            if selected == "zzzz":
                return gr.Dropdown(label="Language", choices=[name for name, _ in language_options], value=default_language_name)
            new_value = next((name for name, key in language_options if key == selected), None)
            return gr.Dropdown(label="Language", choices=[name for name, _ in language_options], value=new_value)

        def change_gr_custom_model_file(f):
            if f is not None:
                return gr.Textbox(placeholder="https://www.example.com/model.zip", label="Model from URL*", visible=False)
            return gr.Textbox(placeholder="https://www.example.com/model.zip", label="Model from URL*", visible=True)

        def change_gr_data(data):
            data["event"] = 'change_data'
            return data

        def process_conversion(session, device, ebook_file, target_voice_file, language, custom_model_file, custom_model_url, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting):                             
            global is_converting, audiobook_file

            ebook["src"] = ebook_file.name if ebook_file else None
            target_voice_file = target_voice_file.name if target_voice_file else None
            custom_model_file = custom_model_file.name if custom_model_file else None
            custom_model_url = custom_model_url if custom_model_file is None else None
            language = next((key for name, key in language_options if name == language), None)
            

            if not ebook["src"]:
                return "Error: eBook file is required."

            # Call the convert_ebook function with the processed parameters
            args = argparse.Namespace(
                session=session,
                script_mode=script_mode,
                device=device.lower(),
                ebook=ebook["src"],
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

        def change_gr_read_data(data):
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

        gr_ebook_file.change(
            fn=change_gr_ebook_file,
            inputs=[gr_convert_btn, gr_ebook_file],
            outputs=[gr_convert_btn, gr_modal_html]
        )
        gr_language.change(
            lambda selected: change_gr_language(dict(language_options).get(selected, "Unknown")),
            inputs=gr_language,
            outputs=gr_language
        )
        gr_audiobooks_ddn.change(
            fn=change_gr_audiobooks_ddn,
            inputs=gr_audiobooks_ddn,
            outputs=[gr_audiobook_link, gr_audio_player, gr_audio_player]
        )
        gr_custom_model_file.change(
            fn=change_gr_custom_model_file,
            inputs=gr_custom_model_file,
            outputs=gr_custom_model_url
        )
        gr_session.change(
            fn=change_gr_data,
            inputs=gr_data,
            outputs=gr_write_data
        )
        gr_write_data.change(
            fn=None,
            inputs=gr_write_data,
            js="""
            (data) => {
              localStorage.clear();
              console.log(data);
              window.localStorage.setItem('data', JSON.stringify(data));
            }
            """
        )       
        gr_read_data.change(
            fn=change_gr_read_data,
            inputs=gr_read_data,
            outputs=[gr_data, gr_session_status, gr_session, gr_audiobooks_ddn]
        )
        gr_convert_btn.click(
           fn=disable_convert_btn,
           inputs=None,
           outputs=gr_convert_btn
        ).then(
            fn=process_conversion,
            inputs=[
                gr_session, gr_device, gr_ebook_file, gr_target_voice_file, gr_language, 
                gr_custom_model_file, gr_custom_model_url, gr_temperature, gr_length_penalty,
                gr_repetition_penalty, gr_top_k, gr_top_p, gr_speed, gr_enable_text_splitting
            ],
            outputs=[gr_conversion_progress, gr_modal_html]           
        ).then(
            fn=update_interface,
            inputs=None,
            outputs=[gr_convert_btn, gr_ebook_file, gr_audio_player, gr_audiobooks_ddn]
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
            outputs=gr_read_data
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