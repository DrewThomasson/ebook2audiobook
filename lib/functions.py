import argparse
import csv
import docker
import ebooklib
import fnmatch
import gradio as gr
import hashlib
import json
import numpy as np
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
from collections import Counter
from collections.abc import MutableMapping
from datetime import datetime
from ebooklib import epub
from glob import glob
from huggingface_hub import hf_hub_download
from iso639 import languages
from multiprocessing import Manager, Event
from pydub import AudioSegment
from tqdm import tqdm
from translate import Translator
from TTS.api import TTS as XTTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from urllib.parse import urlparse

import lib.conf as conf
import lib.lang as lang

def inject_configs(target_namespace):
    # Extract variables from both modules and inject them into the target namespace
    for module in (conf, lang):
        target_namespace.update({k: v for k, v in vars(module).items() if not k.startswith('__')})

# Inject configurations into the global namespace of this module
inject_configs(globals())

def recursive_proxy(data, manager=None):
    """Recursively convert a nested dictionary into Manager.dict proxies."""
    if manager is None:
        manager = Manager()
    if isinstance(data, dict):
        proxy_dict = manager.dict()
        for key, value in data.items():
            proxy_dict[key] = recursive_proxy(value, manager)
        return proxy_dict
    elif isinstance(data, list):
        proxy_list = manager.list()
        for item in data:
            proxy_list.append(recursive_proxy(item, manager))
        return proxy_list
    elif isinstance(data, (str, int, float, bool, type(None))):  # Scalars
        return data
    else:
        raise TypeError(f"Unsupported data type: {type(data)}")

class ConversionContext:
    def __init__(self):
        self.manager = Manager()
        self.sessions = self.manager.dict()  # Store all session-specific contexts
        self.cancellation_events = {}  # Store multiprocessing.Event for each session

    def get_session(self, session_id):
        """Retrieve or initialize session-specific context"""
        if session_id not in self.sessions:
            self.sessions[session_id] = recursive_proxy({
                "script_mode": NATIVE,
                "client": None,
                "language": default_language_code,
                "audiobooks_dir": None,
                "tmp_dir": None,
                "src": None,
                "id": session_id,
                "chapters_dir": None,
                "chapters_dir_sentences": None,
                "epub": None,
                "epub_path": None,
                "filename_noext": None,
                "fine_tuned": None,
                "voice_file": None,
                "custom_model": None,
                "custom_model_dir": None,
                "chapters": None,
                "cover": None,
                "metadata": {
                    "title": None, 
                    "creator": None,
                    "contributor": None,
                    "language": None,
                    "language_iso1": None,
                    "identifier": None,
                    "publisher": None,
                    "date": None,
                    "description": None,
                    "subject": None,
                    "rights": None,
                    "format": None,
                    "type": None,
                    "coverage": None,
                    "relation": None,
                    "Source": None,
                    "Modified": None,
                },
                "status": "Idle",
                "progress": 0,
                "cancellation_requested": False
            }, manager=self.manager)
        return self.sessions[session_id]
        
context = ConversionContext()
is_gui_process = False

class DependencyError(Exception):
    def __init__(self, message=None):
        super().__init__(message)
        # Automatically handle the exception when it's raised
        self.handle_exception()

    def handle_exception(self):
        # Print the full traceback of the exception
        traceback.print_exc()
        
        # Print the exception message
        print(f'Caught DependencyError: {self}')
        
        # Exit the script if it's not a web process
        if not is_gui_process:
            sys.exit(1)
            
def demo_space_check(target_string):
    try:
        space_author_name = os.getenv("SPACE_AUTHOR_NAME", "Unknown")
        space_repo_name = os.getenv("SPACE_REPO_NAME", "Unknown")
        current_space_name = f"{space_author_name}/{space_repo_name}"
        return current_space_name == target_string
    except Exception:
        return False

def get_markdown_for_space(is_demo):
    if is_demo:
        return f'''
        # Ebook2Audiobook v{version}<br/>
        ### 🤨👉⚠️ This is demo space.
        ### Please [duplicate this space](https://huggingface.co/spaces/DrewThomasson/ebook2audiobook?duplicate=true), run it locally, or use the free Google Colab for full functionality.<br/>

        ### Helpful Links:
        [![Discord](https://dcbadge.limes.pink/api/server/https://discord.gg/bg5Kx43c6w)](https://discord.gg/bg5Kx43c6w)  
        [![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/DrewThomasson/ebook2audiobook)  
        [![Free Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrewThomasson/ebook2audiobook/blob/main/Notebooks/colab_ebook2audiobook.ipynb)
        '''
    else:
        return f'''
        # Ebook2Audiobook v{version}<br/>
        https://github.com/DrewThomasson/ebook2audiobook<br/>
        Convert eBooks into immersive audiobooks with realistic voice TTS models.<br/>
        Multiuser, multiprocessing, multithread on a geo cluster to share the conversion to the Grid.
        '''

def prepare_dirs(src, session):
    try:
        resume = False
        os.makedirs(os.path.join(models_dir,'tts'), exist_ok=True)
        os.makedirs(session['tmp_dir'], exist_ok=True)
        os.makedirs(session['custom_model_dir'], exist_ok=True)
        os.makedirs(session['audiobooks_dir'], exist_ok=True)
        session['src'] = os.path.join(session['tmp_dir'], os.path.basename(src))
        if os.path.exists(session['src']):
            if compare_files_by_hash(session['src'], src):
                resume = True
        if not resume:
            shutil.rmtree(session['chapters_dir'], ignore_errors=True)
        os.makedirs(session['chapters_dir'], exist_ok=True)
        os.makedirs(session['chapters_dir_sentences'], exist_ok=True)
        shutil.copy(src, session['src']) 
        return True
    except Exception as e:
        raise DependencyError(e)

def check_programs(prog_name, command, options):
    try:
        subprocess.run([command, options], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, None
    except FileNotFoundError:
        e = f'''********** Error: {prog_name} is not installed! if your OS calibre package version 
        is not compatible you still can run ebook2audiobook.sh (linux/mac) or ebook2audiobook.cmd (windows) **********'''
        raise DependencyError(e)
    except subprocess.CalledProcessError:
        e = f'Error: There was an issue running {prog_name}.'
        raise DependencyError(e)
        
def check_fine_tuned(fine_tuned, language):
    try:
        for parent, children in models.items():
            if fine_tuned in children:
                if language_xtts.get(language):
                    tts = 'xtts'
                else:
                    tts = 'fairseq'
                if parent == tts:
                    return parent
        return False
    except Exception as e:
        raise RuntimeError(e)
        
def analyze_uploaded_file(zip_path, required_files=None):
    if required_files is None:
        required_files = default_model_files
    executable_extensions = {'.exe', '.bat', '.cmd', '.bash', '.bin', '.sh', '.msi', '.dll', '.com'}
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files_in_zip = set()
            executables_found = False
            for file_info in zf.infolist():
                file_name = file_info.filename
                if file_info.is_dir():
                    continue  # Skip directories
                base_name = os.path.basename(file_name)
                files_in_zip.add(base_name)
                _, ext = os.path.splitext(base_name.lower())
                if ext in executable_extensions:
                    executables_found = True
                    break
            missing_files = [f for f in required_files if f not in files_in_zip]
            is_valid = not executables_found and not missing_files
            return is_valid, 
    except zipfile.BadZipFile:
        raise ValueError("error: The file is not a valid ZIP archive.")
    except Exception as e:
        raise RuntimeError(f'analyze_uploaded_file(): {e}')

async def extract_custom_model(file_src, dest=None, session=None, required_files=None):
    try:
        progress_bar = None
        if is_gui_process:
            progress_bar = gr.Progress(track_tqdm=True) 
        if dest is None:
            dest = session['custom_model_dir'] = os.path.join(models_dir, '__sessions', f"model-{session['id']}")
            os.makedirs(dest, exist_ok=True)
        if required_files is None:
            required_files = default_model_files

        dir_src = os.path.dirname(file_src)
        dir_name = os.path.basename(file_src).replace('.zip', '')

        with zipfile.ZipFile(file_src, 'r') as zip_ref:
            files = zip_ref.namelist()
            files_length = len(files)
            dir_tts = 'fairseq'
            xtts_config = 'config.json'

            # Check the model type
            config_data = {}
            if xtts_config in zip_ref.namelist():
                with zip_ref.open(xtts_config) as file:
                    config_data = json.load(file)
            if config_data.get('model') == 'xtts':
                dir_tts = 'xtts'
            
            dir_dest = os.path.join(dest, dir_tts, dir_name)
            os.makedirs(dir_dest, exist_ok=True)

            # Initialize progress bar
            with tqdm(total=100, unit='%') as t:  # Track progress as a percentage
                for i, file in enumerate(files):
                    if file in required_files:
                        zip_ref.extract(file, dir_dest)
                    progress_percentage = ((i + 1) / files_length) * 100
                    t.n = int(progress_percentage)
                    t.refresh()
                    if progress_bar is not None:
                        progress_bar(downloaded / total_size)
                        yield dir_name, progress_bar

        os.remove(file_src)
        print(f'Extracted files to {dir_dest}')
        yield dir_name, progress_bar
        return
    except Exception as e:
        raise DependencyError(e)

def calculate_hash(filepath, hash_algorithm='sha256'):
    hash_func = hashlib.new(hash_algorithm)
    with open(filepath, 'rb') as file:
        while chunk := file.read(8192):  # Read in chunks to handle large files
            hash_func.update(chunk)
    return hash_func.hexdigest()

def compare_files_by_hash(file1, file2, hash_algorithm='sha256'):
    return calculate_hash(file1, hash_algorithm) == calculate_hash(file2, hash_algorithm)

def has_metadata(f):
    try:
        b = epub.read_epub(f)
        metadata = b.get_metadata('DC', '')
        if metadata:
            return True
        else:
            return False
    except Exception as e:
        return False

def convert_to_epub(session):
    if session['cancellation_requested']:
        #stop_and_detach_tts()
        print('Cancel requested')
        return False
    if session['script_mode'] == DOCKER_UTILS:
        try:
            docker_dir = os.path.basename(session['tmp_dir'])
            docker_file_in = os.path.basename(session['src'])
            docker_file_out = os.path.basename(session['epub_path'])
            
            # Check if the input file is already an EPUB
            if docker_file_in.lower().endswith('.epub'):
                shutil.copy(session['src'], session['epub_path'])
                return True

            # Convert the ebook to EPUB format using utils Docker image
            container = session['client'].containers.run(
                docker_utils_image,
                command=f'ebook-convert /files/{docker_dir}/{docker_file_in} /files/{docker_dir}/{docker_file_out}',
                volumes={session['tmp_dir']: {'bind': f'/files/{docker_dir}', 'mode': 'rw'}},
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
            util_app = shutil.which('ebook-convert')
            subprocess.run([util_app, session['src'], session['epub_path']], check=True)
            return True
        except subprocess.CalledProcessError as e:
            raise DependencyError(e)

def get_cover(session):
    try:
        if session['cancellation_requested']:
            #stop_and_detach_tts()
            print('Cancel requested')
            return False
        cover_image = False
        cover_path = os.path.join(session['tmp_dir'], session['filename_noext'] + '.jpg')
        for item in session['epub'].get_items_of_type(ebooklib.ITEM_COVER):
            cover_image = item.get_content()
            break
        if not cover_image:
            for item in session['epub'].get_items_of_type(ebooklib.ITEM_IMAGE):
                if 'cover' in item.file_name.lower() or 'cover' in item.get_id().lower():
                    cover_image = item.get_content()
                    break
        if cover_image:
            with open(cover_path, 'wb') as cover_file:
                cover_file.write(cover_image)
                return cover_path
        return True
    except Exception as e:
        raise DependencyError(e)

def get_chapters(language, session):
    try:
        if session['cancellation_requested']:
            #stop_and_detach_tts()
            print('Cancel requested')
            return False
        all_docs = list(session['epub'].get_items_of_type(ebooklib.ITEM_DOCUMENT))
        if all_docs:
            all_docs = all_docs[1:]
            doc_patterns = [filter_pattern(str(doc)) for doc in all_docs if filter_pattern(str(doc))]
            most_common_pattern = filter_doc(doc_patterns)
            selected_docs = [doc for doc in all_docs if filter_pattern(str(doc)) == most_common_pattern]
            chapters = [filter_chapter(doc, language) for doc in selected_docs]
            if session['metadata'].get('creator'):
                intro = f"{session['metadata']['creator']}, {session['metadata']['title']};\n "
                chapters[0].insert(0, intro)
            return chapters
        return False
    except Exception as e:
        raise DependencyError(f'Error extracting main content pages: {e}')

def filter_doc(doc_patterns):
    pattern_counter = Counter(doc_patterns)
    # Returns a list with one tuple: [(pattern, count)] 
    most_common = pattern_counter.most_common(1)
    return most_common[0][0] if most_common else None

def filter_pattern(doc_identifier):
    parts = doc_identifier.split(':')
    if len(parts) > 2:
        segment = parts[1]
        if re.search(r'[a-zA-Z]', segment) and re.search(r'\d', segment):
            return ''.join([char for char in segment if char.isalpha()])
        elif re.match(r'^[a-zA-Z]+$', segment):
            return segment
        elif re.match(r'^\d+$', segment):
            return 'numbers'
    return None

def filter_chapter(doc, language):
    soup = BeautifulSoup(doc.get_body_content(), 'html.parser')
    # Remove scripts and styles
    for script in soup(["script", "style"]):
        script.decompose()
    # Normalize lines and remove unnecessary spaces
    text = re.sub(r'(\r\n|\r|\n){3,}', '\r\n', soup.get_text().strip())
    text = replace_roman_numbers(text)
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    text = text.replace('»', '"').replace('«', '"')
    # Pattern 1: Add a space between UTF-8 characters and numbers
    text = re.sub(r'(?<=[\p{L}])(?=\d)|(?<=\d)(?=[\p{L}])', ' ', text)
    # Pattern 2: Split numbers into groups of 4
    text = re.sub(r'(\d{4})(?=\d)', r'\1 ', text)
    chapter_sentences = get_sentences(text, language)
    return chapter_sentences

def get_sentences(sentence, language, max_pauses=9):
    max_length = language_mapping[language]['char_limit']
    punctuation = language_mapping[language]['punctuation']
    sentence = sentence.replace(".", ";\n")
    parts = []
    while len(sentence) > max_length or sum(sentence.count(p) for p in punctuation) > max_pauses:
        # Step 1: Look for the last period (.) within max_length
        possible_splits = [i for i, char in enumerate(sentence[:max_length]) if char == '.']    
        # Step 2: If no periods, look for the last comma (,)
        if not possible_splits:
            possible_splits = [i for i, char in enumerate(sentence[:max_length]) if char == ',']    
        # Step 3: If still no splits, look for any other punctuation
        if not possible_splits:
            possible_splits = [i for i, char in enumerate(sentence[:max_length]) if char in punctuation]    
        # Step 4: Determine where to split the sentence
        if possible_splits:
            split_at = possible_splits[-1] + 1  # Split at the last occurrence of punctuation
        else:
            # If no punctuation is found, split at the last space
            last_space = sentence.rfind(' ', 0, max_length)
            if last_space != -1:
                split_at = last_space + 1
            else:
                # If no space is found, force split at max_length
                split_at = max_length   
        # Add the split sentence to parts
        parts.append(sentence[:split_at].strip() + ' ')
        sentence = sentence[split_at:].strip()
    # Add the remaining sentence if any
    if sentence:
        parts.append(sentence.strip() + ' ')
    return parts
    
def normalize_audio_file(voice_file, session):
    output_file = session['filename_noext'].replace('&', 'And').replace(' ', '_') 
    output_file = os.path.join(session['tmp_dir'], output_file) + '_voice.wav'
    ffmpeg_cmd = [
        'ffmpeg', '-i', voice_file,
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
        print(f"Processing file: {voice_file}")
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Processed file saved to: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error processing file {voice_file}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def convert_chapters_to_audio(session):
    try:
        if session['cancellation_requested']:
            #stop_and_detach_tts()
            print('Cancel requested')
            return False
        progress_bar = None
        params = {}
        if is_gui_process:
            progress_bar = gr.Progress(track_tqdm=True)        
        params['tts_model'] = None
        '''
        # List available TTS base models
        print("Available Models:")
        print("=================")
        for index, model in enumerate(XTTS().list_models(), 1):
            print(f"{index}. {model}")
        '''
        if session['metadata']['language'] in language_xtts:
            params['tts_model'] = 'xtts'
            if session['custom_model'] is not None:
                print(f"Loading TTS {params['tts_model']} model from {session['custom_model']}...")
                model_path = os.path.join(session['custom_model'], 'model.pth')
                config_path = os.path.join(session['custom_model'],'config.json')
                vocab_path = os.path.join(session['custom_model'],'vocab.json')
                voice_path = os.path.join(session['custom_model'],'ref.wav')
                config = XttsConfig()
                config.models_dir = os.path.join(models_dir,'tts')
                config.load_json(config_path)
                params['tts'] = Xtts.init_from_config(config)
                params['tts'].load_checkpoint(config, checkpoint_path=model_path, vocab_path=vocab_path, eval=True)
                print('Computing speaker latents...')
                params['voice_file'] = session['voice_file'] if session['voice_file'] is not None else voice_path
                params['voice_file'] = normalize_audio_file(params['voice_file'], session)
                if params['voice_file'] is None:
                    print('Voice file cannot be normalized!')
                    return False
                params['gpt_cond_latent'], params['speaker_embedding'] = params['tts'].get_conditioning_latents(audio_path=[params['voice_file']])
            elif session['fine_tuned'] != 'std':
                print(f"Loading TTS {params['tts_model']} model from {session['fine_tuned']}...")
                hf_repo = models[params['tts_model']][session['fine_tuned']]['repo']
                hf_sub = models[params['tts_model']][session['fine_tuned']]['sub']
                cache_dir = os.path.join(models_dir,'tts')
                model_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}/model.pth", cache_dir=cache_dir)
                config_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}/config.json", cache_dir=cache_dir)
                vocab_path = hf_hub_download(repo_id=hf_repo, filename=f"{hf_sub}/vocab.json", cache_dir=cache_dir)             
                config = XttsConfig()
                config.models_dir = cache_dir
                config.load_json(config_path)
                params['tts'] = Xtts.init_from_config(config)
                params['tts'].load_checkpoint(config, checkpoint_path=model_path, vocab_path=vocab_path, eval=True)
                print('Computing speaker latents...')
                params['voice_file'] = session['voice_file'] if session['voice_file'] is not None else models[params['tts_model']][session['fine_tuned']]['voice']
                params['voice_file'] = normalize_audio_file(params['voice_file'], session)
                if params['voice_file'] is None:
                    print('Voice file cannot be normalized!')
                    return False
                params['gpt_cond_latent'], params['speaker_embedding'] = params['tts'].get_conditioning_latents(audio_path=[params['voice_file']])
            else:
                print(f"Loading TTS {params['tts_model']} model from {models[params['tts_model']][session['fine_tuned']]['repo']}...")
                params['tts'] = XTTS(model_name=models[params['tts_model']][session['fine_tuned']]['repo'])
                params['voice_file'] = session['voice_file'] if session['voice_file'] is not None else models[params['tts_model']][session['fine_tuned']]['voice']
                params['voice_file'] = normalize_audio_file(params['voice_file'], session)
                if params['voice_file'] is None:
                    print('Voice file cannot be normalized!')
                    return False
            params['tts'].to(session['device'])
        else:
            params['tts_model'] = 'fairseq'
            model_repo = models[params['tts_model']][session['fine_tuned']]['repo'].replace("[lang]", session['metadata']['language'])
            print(f"Loading TTS {model_repo} model from {model_repo}...")
            params['tts'] = XTTS(model_repo)
            params['voice_file'] = session['voice_file'] if session['voice_file'] is not None else models[params['tts_model']][session['fine_tuned']]['voice']
            params['tts'].to(session['device'])

        resume_chapter = 0
        resume_sentence = 0

        # Check existing files to resume the process if it was interrupted
        existing_chapters = sorted([f for f in os.listdir(session['chapters_dir']) if f.endswith(f'.{audioproc_format}')])
        existing_sentences = sorted([f for f in os.listdir(session['chapters_dir_sentences']) if f.endswith(f'.{audioproc_format}')])

        if existing_chapters:
            count_chapter_files = len(existing_chapters)
            resume_chapter = count_chapter_files - 1 if count_chapter_files > 0 else 0
            print(f'Resuming from chapter {count_chapter_files}')
        if existing_sentences:
            resume_sentence = len(existing_sentences)
            print(f'Resuming from sentence {resume_sentence}')

        total_chapters = len(session['chapters'])
        total_sentences = sum(len(array) for array in session['chapters'])
        current_sentence = 0

        with tqdm(total=total_sentences, desc='convert_chapters_to_audio 0.00%', bar_format='{desc}: {n_fmt}/{total_fmt} ', unit='step', initial=resume_sentence) as t:
            t.n = resume_sentence
            t.refresh()
            for x in range(resume_chapter, total_chapters):
                chapter_num = x + 1
                chapter_audio_file = f'chapter_{chapter_num}.{audioproc_format}'
                sentences = session['chapters'][x]
                sentences_count = len(sentences)
                start = current_sentence  # Mark the starting sentence of the chapter
                print(f"\nChapter {chapter_num} containing {sentences_count} sentences...")
                for i, sentence in enumerate(sentences):
                    if current_sentence >= resume_sentence:
                        params['sentence_audio_file'] = os.path.join(session['chapters_dir_sentences'], f'{current_sentence}.{audioproc_format}')                       
                        params['sentence'] = sentence
                        if convert_sentence_to_audio(params, session):
                            t.update(1)
                            percentage = (current_sentence / total_sentences) * 100
                            t.set_description(f'Processing {percentage:.2f}%')
                            print(f'Sentence: {sentence}')
                            t.refresh()
                            if progress_bar is not None:
                                progress_bar(current_sentence / total_sentences)
                        else:
                            return False
                    current_sentence += 1
                end = current_sentence - 1
                print(f"\nEnd of Chapter {chapter_num}")
                if start >= resume_sentence:
                    if combine_audio_sentences(chapter_audio_file, start, end, session):
                        print(f'Combining chapter {chapter_num} to audio, sentence {start} to {end}')
                    else:
                        print('combine_audio_sentences() failed!')
                        return False
        return True
    except Exception as e:
        raise DependencyError(e)

def convert_sentence_to_audio(params, session):
    try:
        if session['cancellation_requested']:
            #stop_and_detach_tts(params['tts'])
            print('Cancel requested')
            return False
        generation_params = {
            "temperature": session['temperature'],
            "length_penalty": session["length_penalty"],
            "repetition_penalty": session['repetition_penalty'],
            "num_beams": int(session['length_penalty']) + 1 if session["length_penalty"] > 1 else 1,
            "top_k": session['top_k'],
            "top_p": session['top_p'],
            "speed": session['speed'],
            "enable_text_splitting": session['enable_text_splitting']
        }
        if params['tts_model'] == 'xtts':
            if session['custom_model'] is not None or session['fine_tuned'] != 'std':
                output = params['tts'].inference(
                    text=params['sentence'],
                    language=session['metadata']['language_iso1'],
                    gpt_cond_latent=params['gpt_cond_latent'],
                    speaker_embedding=params['speaker_embedding'],
                    **generation_params
                )
                torchaudio.save(
                    params['sentence_audio_file'], 
                    torch.tensor(output[audioproc_format]).unsqueeze(0), 
                    sample_rate=24000
                )
            else:
                params['tts'].tts_to_file(
                    text=params['sentence'],
                    language=session['metadata']['language_iso1'],
                    file_path=params['sentence_audio_file'],
                    speaker_wav=params['voice_file'],
                    **generation_params
                )
        elif params['tts_model'] == 'fairseq':
            params['tts'].tts_with_vc_to_file(
                text=params['sentence'],
                file_path=params['sentence_audio_file'],
                speaker_wav=params['voice_file'].replace('_24khz','_16khz'),
                split_sentences=session['enable_text_splitting']
            )
        if os.path.exists(params['sentence_audio_file']):
            return True
        print(f"Cannot create {params['sentence_audio_file']}")
        return False
    except Exception as e:
        raise DependencyError(e)
        
def combine_audio_sentences(chapter_audio_file, start, end, session):
    try:
        chapter_audio_file = os.path.join(session['chapters_dir'], chapter_audio_file)
        combined_audio = AudioSegment.empty()  
        # Get all audio sentence files sorted by their numeric indices
        sentence_files = [f for f in os.listdir(session['chapters_dir_sentences']) if f.endswith(".wav")]
        sentences_dir_ordered = sorted(sentence_files, key=lambda x: int(re.search(r'\d+', x).group()))
        # Filter the files in the range [start, end]
        selected_files = [
            file for file in sentences_dir_ordered 
            if start <= int(''.join(filter(str.isdigit, os.path.basename(file)))) <= end
        ]
        for file in selected_files:
            if session['cancellation_requested']:
                #stop_and_detach_tts(params['tts'])
                print('Cancel requested')
                return False
            if session['cancellation_requested']:
                msg = 'Cancel requested'
                raise ValueError(msg)
            audio_segment = AudioSegment.from_file(os.path.join(session['chapters_dir_sentences'],file), format=audioproc_format)
            combined_audio += audio_segment
        combined_audio.export(chapter_audio_file, format=audioproc_format)
        print(f'Combined audio saved to {chapter_audio_file}')
        return True
    except Exception as e:
        raise DependencyError(e)


def combine_audio_chapters(session):
    def sort_key(chapter_file):
        numbers = re.findall(r'\d+', chapter_file)
        return int(numbers[0]) if numbers else 0
        
    def assemble_audio():
        try:
            combined_audio = AudioSegment.empty()
            batch_size = 256
            # Process the chapter files in batches
            for i in range(0, len(chapter_files), batch_size):
                batch_files = chapter_files[i:i + batch_size]
                batch_audio = AudioSegment.empty()  # Initialize an empty AudioSegment for the batch
                # Sequentially append each file in the current batch to the batch_audio
                for chapter_file in batch_files:
                    if session['cancellation_requested']:
                        print('Cancel requested')
                        return False
                    audio_segment = AudioSegment.from_wav(os.path.join(session['chapters_dir'],chapter_file))
                    batch_audio += audio_segment
                combined_audio += batch_audio
            combined_audio.export(assembled_audio, format=audioproc_format)
            print(f'Combined audio saved to {assembled_audio}')
            return True
        except Exception as e:
            raise DependencyError(e)

    def generate_ffmpeg_metadata():
        try:
            if session['cancellation_requested']:
                print('Cancel requested')
                return False
            ffmpeg_metadata = ';FFMETADATA1\n'        
            if session['metadata'].get('title'):
                ffmpeg_metadata += f"title={session['metadata']['title']}\n"            
            if session['metadata'].get('creator'):
                ffmpeg_metadata += f"artist={session['metadata']['creator']}\n"
            if session['metadata'].get('language'):
                ffmpeg_metadata += f"language={session['metadata']['language']}\n\n"
            if session['metadata'].get('publisher'):
                ffmpeg_metadata += f"publisher={session['metadata']['publisher']}\n"              
            if session['metadata'].get('description'):
                ffmpeg_metadata += f"description={session['metadata']['description']}\n"
            if session['metadata'].get('published'):
                # Check if the timestamp contains fractional seconds
                if '.' in session['metadata']['published']:
                    # Parse with fractional seconds
                    year = datetime.strptime(session['metadata']['published'], '%Y-%m-%dT%H:%M:%S.%f%z').year
                else:
                    # Parse without fractional seconds
                    year = datetime.strptime(session['metadata']['published'], '%Y-%m-%dT%H:%M:%S%z').year
            else:
                # If published is not provided, use the current year
                year = datetime.now().year
            ffmpeg_metadata += f'year={year}\n'
            if session['metadata'].get('identifiers') and isinstance(session['metadata'].get('identifiers'), dict):
                isbn = session['metadata']['identifiers'].get('isbn', None)
                if isbn:
                    ffmpeg_metadata += f'isbn={isbn}\n'  # ISBN
                mobi_asin = session['metadata']['identifiers'].get('mobi-asin', None)
                if mobi_asin:
                    ffmpeg_metadata += f'asin={mobi_asin}\n'  # ASIN                   
            start_time = 0
            for index, chapter_file in enumerate(chapter_files):
                if session['cancellation_requested']:
                    msg = 'Cancel requested'
                    raise ValueError(msg)

                duration_ms = len(AudioSegment.from_wav(os.path.join(session['chapters_dir'],chapter_file)))
                ffmpeg_metadata += f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={start_time}\n'
                ffmpeg_metadata += f'END={start_time + duration_ms}\ntitle=Chapter {index + 1}\n'
                start_time += duration_ms
            # Write the metadata to the file
            with open(metadata_file, 'w', encoding='utf-8') as file:
                file.write(ffmpeg_metadata)
            return True
        except Exception as e:
            raise DependencyError(e)

    def export_audio():
        try:
            if session['cancellation_requested']:
                print('Cancel requested')
                return False
            ffmpeg_cover = None
            if session['script_mode'] == DOCKER_UTILS:
                docker_dir = os.path.basename(session['tmp_dir'])
                ffmpeg_combined_audio = f'/files/{docker_dir}/' + os.path.basename(assembled_audio)
                ffmpeg_metadata_file = f'/files/{docker_dir}/' + os.path.basename(metadata_file)
                ffmpeg_final_file = f'/files/{docker_dir}/' + os.path.basename(docker_final_file)           
                if session['cover'] is not None:
                    ffmpeg_cover = f'/files/{docker_dir}/' + os.path.basename(session['cover'])                   
                ffmpeg_cmd = ['ffmpeg', '-i', ffmpeg_combined_audio, '-i', ffmpeg_metadata_file]
            else:
                ffmpeg_combined_audio = assembled_audio
                ffmpeg_metadata_file = metadata_file
                ffmpeg_final_file = final_file
                if session['cover'] is not None:
                    ffmpeg_cover = session['cover']                    
                ffmpeg_cmd = [shutil.which('ffmpeg'), '-i', ffmpeg_combined_audio, '-i', ffmpeg_metadata_file]
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
            if session['script_mode'] == DOCKER_UTILS:
                try:
                    container = session['client'].containers.run(
                        docker_utils_image,
                        command=ffmpeg_cmd,
                        volumes={session['tmp_dir']: {'bind': f'/files/{docker_dir}', 'mode': 'rw'}},
                        remove=True,
                        detach=False,
                        stdout=True,
                        stderr=True
                    )
                    print(container.decode('utf-8'))
                    if shutil.copy(docker_final_file, final_file):
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
        chapter_files = [f for f in os.listdir(session['chapters_dir']) if f.endswith(".wav")]
        chapter_files = sorted(chapter_files, key=lambda x: int(re.search(r'\d+', x).group()))
        assembled_audio = os.path.join(session['tmp_dir'], session['metadata']['title'] + '.' + audioproc_format)
        metadata_file = os.path.join(session['tmp_dir'], 'metadata.txt')
        if assemble_audio():
            if generate_ffmpeg_metadata():
                final_name = session['metadata']['title'] + '.' + audiobook_format
                docker_final_file = os.path.join(session['tmp_dir'], final_name)
                final_file = os.path.join(session['audiobooks_dir'], final_name)       
                if export_audio():
                    return final_file
        return None
    except Exception as e:
        raise DependencyError(e)        

def replace_roman_numbers(text):
    def roman_to_int(s):
        try:
            roman = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000,
                     'IV': 4, 'IX': 9, 'XL': 40, 'XC': 90, 'CD': 400, 'CM': 900}   
            i = 0
            num = 0   
            # Iterate over the string to calculate the integer value
            while i < len(s):
                # Check for two-character numerals (subtractive combinations)
                if i + 1 < len(s) and s[i:i+2] in roman:
                    num += roman[s[i:i+2]]
                    i += 2
                else:
                    # Add the value of the single character
                    num += roman[s[i]]
                    i += 1   
            return num
        except Exception as e:
            return s

    roman_chapter_pattern = re.compile(
        r'\b(chapter|volume|chapitre|tome|capitolo|capítulo|volumen|Kapitel|глава|том|κεφάλαιο|τόμος|capitul|poglavlje)\s'
        r'(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})|[IVXLCDM]+)\b',
        re.IGNORECASE
    )

    roman_numerals_with_period = re.compile(
        r'^(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})|[IVXLCDM])\.+'
    )

    def replace_chapter_match(match):
        chapter_word = match.group(1)
        roman_numeral = match.group(2)
        integer_value = roman_to_int(roman_numeral.upper())
        return f'{chapter_word.capitalize()} {integer_value}'

    def replace_numeral_with_period(match):
        roman_numeral = match.group(1)
        integer_value = roman_to_int(roman_numeral)
        return f'{integer_value}.'

    text = roman_chapter_pattern.sub(replace_chapter_match, text)
    text = roman_numerals_with_period.sub(replace_numeral_with_period, text)
    return text
'''
def stop_and_detach_tts(tts=None):
    if tts is not None:
        if next(tts.parameters()).is_cuda:
            tts.to('cpu')
        del tts
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
'''
def delete_old_web_folders(root_dir):
    try:
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
            print(f'Created missing directory: {root_dir}')
        current_time = time.time()
        age_limit = current_time - interface_shared_expire * 60 * 60  # 24 hours in seconds
        for folder_name in os.listdir(root_dir):
            dir_path = os.path.join(root_dir, folder_name)
            if os.path.isdir(dir_path) and folder_name.startswith('web-'):
                folder_creation_time = os.path.getctime(dir_path)
                if folder_creation_time < age_limit:
                    shutil.rmtree(dir_path)
    except Exception as e:
        raise DependencyError(e)

def compare_file_metadata(f1, f2):
    if os.path.getsize(f1) != os.path.getsize(f2):
        return False
    if os.path.getmtime(f1) != os.path.getmtime(f2):
        return False
    return True

def convert_ebook(args):
    try:
        global is_gui_process
        global context        
        error = None
        try:
            if len(args['language']) == 2:
                lang_array = languages.get(alpha2=args['language'])
                if lang_array and lang_array.part3:
                    args['language'] = lang_array.part3
                else:
                    args['language'] = None
            else:
                lang_array = languages.get(part3=args['language'])               
                if not lang_array:
                    args['language'] = None
        except Exception as e:
            args['language'] = None
            pass

        if args['language'] is not None and args['language'] in language_mapping.keys():
            session_id = args['session'] if args['session'] is not None else str(uuid.uuid4())
            session = context.get_session(session_id)
            session['id'] = session_id
            session['src'] = args['ebook']
            session['script_mode'] = args['script_mode'] if args['script_mode'] is not None else NATIVE       
            session['audiobooks_dir'] = args['audiobooks_dir']
            is_gui_process = args['is_gui_process']
            device = args['device'].lower()
            voice_file = args['voice']
            language = args['language']
            temperature = args['temperature']
            length_penalty = args['length_penalty']
            repetition_penalty = args['repetition_penalty']
            top_k = args['top_k']
            top_p = args['top_p']
            speed = args['speed']
            enable_text_splitting = args['enable_text_splitting'] if args['enable_text_splitting'] is not None else True
            custom_model_file = args['custom_model'] if args['custom_model'] != 'none'  and args['custom_model'] is not None else None
            fine_tuned = args['fine_tuned'] if check_fine_tuned(args['fine_tuned'], args['language']) else None
            
            if not fine_tuned:
                raise ValueError('The fine tuned model does not exist.')

            if not os.path.splitext(args['ebook'])[1]:
                raise ValueError('The selected ebook file has no extension. Please select a valid file.')

            if session['script_mode'] == NATIVE:
                bool, e = check_programs('Calibre', 'calibre', '--version')
                if not bool:
                    raise DependencyError(e)
                bool, e = check_programs('FFmpeg', 'ffmpeg', '-version')
                if not bool:
                    raise DependencyError(e)
            elif session['script_mode'] == DOCKER_UTILS:
                session['client'] = docker.from_env()

            session['tmp_dir'] = os.path.join(processes_dir, f"ebook-{session['id']}")
            session['chapters_dir'] = os.path.join(session['tmp_dir'], f"chapters_{hashlib.md5(args['ebook'].encode()).hexdigest()}")
            session['chapters_dir_sentences'] = os.path.join(session['chapters_dir'], 'sentences')

            if not is_gui_process:
                session['custom_model_dir'] = os.path.join(models_dir,'__sessions',f"model-{session['id']}")
                if custom_model_file:
                    session['custom_model'], progression_status = extract_custom_model(custom_model_file, session['custom_model_dir'])
                    if not session['custom_model']:
                        raise ValueError(f'{custom_model_file} could not be extracted or mandatory files are missing')

            if prepare_dirs(args['ebook'], session):
                session['filename_noext'] = os.path.splitext(os.path.basename(session['src']))[0]
                if not torch.cuda.is_available() or device == 'cpu':
                    if device == 'gpu':
                        print('GPU is not available on your device!')
                    device = 'cpu'
                else:
                    device = 'cuda'
                torch.device(device)
                print(f'Available Processor Unit: {device}')   
                session['epub_path'] = os.path.join(session['tmp_dir'], '__' + session['filename_noext'] + '.epub')
                has_src_metadata = has_metadata(session['src'])
                if convert_to_epub(session):
                    session['epub'] = epub.read_epub(session['epub_path'], {'ignore_ncx': True})       
                    metadata = dict(session['metadata'])
                    for key, value in metadata.items():
                        data = session['epub'].get_metadata('DC', key)
                        if data:
                            for value, attributes in data:
                                if key == 'language' and not has_src_metadata:
                                    session['metadata'][key] = language
                                else:
                                    session['metadata'][key] = value
                    language_array = languages.get(part3=language)
                    if language_array and language_array.part1:
                        session['metadata']['language_iso1'] = language_array.part1
                    if session['metadata']['language'] == language or session['metadata']['language_iso1'] and session['metadata']['language'] == session['metadata']['language_iso1']:
                        session['metadata']['title'] = os.path.splitext(os.path.basename(session['src']))[0] if not session['metadata']['title'] else session['metadata']['title']
                        session['metadata']['creator'] =  False if not session['metadata']['creator'] else session['metadata']['creator']
                        session['cover'] = get_cover(session)
                        if session['cover']:
                            session['chapters'] = get_chapters(language, session)
                            if session['chapters']:
                                session['device'] = device
                                session['temperature'] = temperature
                                session['length_penalty'] = length_penalty
                                session['repetition_penalty'] = repetition_penalty
                                session['top_k'] = top_k
                                session['top_p'] = top_p
                                session['speed'] = speed
                                session['enable_text_splitting'] = enable_text_splitting
                                session['fine_tuned'] = fine_tuned
                                session['voice_file'] = voice_file
                                session['language'] = language
                                if convert_chapters_to_audio(session):
                                    final_file = combine_audio_chapters(session)               
                                    if final_file is not None:
                                        chapters_dirs = [
                                            dir_name for dir_name in os.listdir(session['tmp_dir'])
                                            if fnmatch.fnmatch(dir_name, "chapters_*") and os.path.isdir(os.path.join(session['tmp_dir'], dir_name))
                                        ]
                                        if len(chapters_dirs) > 1:
                                            if os.path.exists(session['chapters_dir']):
                                                shutil.rmtree(session['chapters_dir'])
                                            if os.path.exists(session['epub_path']):
                                                os.remove(session['epub_path'])
                                            if os.path.exists(session['cover']):
                                                os.remove(session['cover'])
                                        else:
                                            if os.path.exists(session['tmp_dir']):
                                                shutil.rmtree(session['tmp_dir'])
                                        progress_status = f'Audiobook {os.path.basename(final_file)} created!'
                                        if not is_gui_process:
                                            print(f'*********** Session: {session_id}', '************* Store it in case of interruption or crash you can resume the conversion')
                                        return progress_status, final_file 
                                    else:
                                        error = 'combine_audio_chapters() error: final_file not created!'
                                else:
                                    error = 'convert_chapters_to_audio() failed!'
                            else:
                                error = 'get_chapters() failed!'
                        else:
                            error = 'get_cover() failed!'
                    else:
                        error = f"WARNING: Ebook language: {session['metadata']['language']}, language selected: {language}"
                else:
                    error = 'convert_to_epub() failed!'
            else:
                error = f"Temporary directory {session['tmp_dir']} not removed due to failure."
        else:
            error = f"Language {args['language']} is not supported."
        if session['cancellation_requested']:
            error = 'Cancelled'
        print(error)
        return error, None
    except Exception as e:
        print(f'convert_ebook() Exception: {e}')
        return e, None

def web_interface(args):
    script_mode = args['script_mode']
    is_gui_process = args['is_gui_process']
    is_gui_shared = args['share']
    is_converting = False
    audiobooks_dir = None
    ebook_src = None
    audiobook_file = None
    language_options = [
        (
            f"{details['name']} - {details['native_name']}" if details['name'] != details['native_name'] else details['name'],
            lang
        )
        for lang, details in language_mapping.items()
    ]
    custom_model_options = None
    fine_tuned_options = list(models['xtts'].keys())
    default_language_name =  next((name for name, key in language_options if key == default_language_code), None)

    theme = gr.themes.Origin(
        primary_hue='amber',
        secondary_hue='green',
        neutral_hue='gray',
        radius_size='lg',
        font_mono=['JetBrains Mono', 'monospace', 'Consolas', 'Menlo', 'Liberation Mono']
    )
    
    with gr.Blocks(theme=theme) as interface:
        gr.HTML(
            '''
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
                #component-7, #component-10, #component-20 {
                    height: 140px !important;
                }
                #component-47, #component-51 {
                    height: 100px !important;
                }
            </style>
            '''
        )
        gr.Markdown(get_markdown_for_space(demo_space_check(conf.demo_huggingface)))
        with gr.Tabs():
            gr_tab_main = gr.TabItem('Input Options')
            with gr_tab_main:
                with gr.Row():
                    with gr.Column(scale=3):
                        with gr.Group():
                            gr_ebook_file = gr.File(label='EBook File (.epub, .mobi, .azw3, fb2, lrf, rb, snb, tcr, .pdf, .txt, .rtf, doc, .docx, .html, .odt, .azw)', file_types=['.epub', '.mobi', '.azw3', 'fb2', 'lrf', 'rb', 'snb', 'tcr', '.pdf', '.txt', '.rtf', 'doc', '.docx', '.html', '.odt', '.azw'])
                        with gr.Group():
                            gr_voice_file = gr.File(label='*Cloning Voice (a .wav 24khz for XTTS base model and 16khz for FAIRSEQ base model, no more than 6 sec)', file_types=['.wav'], visible=interface_component_options['gr_voice_file'])
                            gr.Markdown('<p>&nbsp;&nbsp;* Optional</p>')
                        with gr.Group():
                            gr_device = gr.Radio(label='Processor Unit', choices=['CPU', 'GPU'], value='CPU')
                        with gr.Group():
                            gr_language = gr.Dropdown(label='Language', choices=[name for name, _ in language_options], value=default_language_name)
                    with gr.Column(scale=3):
                        gr_group_custom_model = gr.Group(visible=interface_component_options['gr_group_custom_model'])
                        with gr_group_custom_model:
                            gr_custom_model_file = gr.File(label='*Custom XTTS Model (a .zip containing config.json, vocab.json, model.pth, ref.wav)', file_types=['.zip'])
                            gr_custom_model_list = gr.Dropdown(label='', choices=['none'], interactive=True)
                            gr.Markdown('<p>&nbsp;&nbsp;* Optional</p>')
                        with gr.Group():
                            gr_session_status = gr.Textbox(label='Session')
                        with gr.Group():
                            gr_tts_engine = gr.Dropdown(label='TTS Base', choices=[default_tts_engine], value=default_tts_engine, interactive=True)
                            gr_fine_tuned = gr.Dropdown(label='Fine Tuned Models', choices=fine_tuned_options, value=default_fine_tuned, interactive=True)
            gr_tab_preferences = gr.TabItem('Audio Generation Preferences', visible=interface_component_options['gr_tab_preferences'])
            with gr_tab_preferences:
                gr.Markdown(
                    '''
                    ### Customize Audio Generation Parameters
                    Adjust the settings below to influence how the audio is generated. You can control the creativity, speed, repetition, and more.
                    '''
                )
                gr_temperature = gr.Slider(
                    label='Temperature', 
                    minimum=0.1, 
                    maximum=10.0, 
                    step=0.1, 
                    value=0.65,
                    info='Higher values lead to more creative, unpredictable outputs. Lower values make it more monotone.'
                )
                gr_length_penalty = gr.Slider(
                    label='Length Penalty', 
                    minimum=0.5, 
                    maximum=10.0, 
                    step=0.1, 
                    value=1.0, 
                    info='Penalize longer sequences. Higher values produce shorter outputs. Not applied to custom models.'
                )
                gr_repetition_penalty = gr.Slider(
                    label='Repetition Penalty', 
                    minimum=1.0, 
                    maximum=10.0, 
                    step=0.1, 
                    value=2.5, 
                    info='Penalizes repeated phrases. Higher values reduce repetition.'
                )
                gr_top_k = gr.Slider(
                    label='Top-k Sampling', 
                    minimum=10, 
                    maximum=100, 
                    step=1, 
                    value=50, 
                    info='Lower values restrict outputs to more likely words and increase speed at which audio generates.'
                )
                gr_top_p = gr.Slider(
                    label='Top-p Sampling', 
                    minimum=0.1, 
                    maximum=1.0, 
                    step=.01, 
                    value=0.8, 
                    info='Controls cumulative probability for word selection. Lower values make the output more predictable and increase speed at which audio generates.'
                )
                gr_speed = gr.Slider(
                    label='Speed', 
                    minimum=0.5, 
                    maximum=3.0, 
                    step=0.1, 
                    value=1.0, 
                    info='Adjusts how fast the narrator will speak.'
                )
                gr_enable_text_splitting = gr.Checkbox(
                    label='Enable Text Splitting', 
                    value=True,
                    info='Splits long texts into sentences to generate audio in chunks. Useful for very long inputs.'
                )
                
        gr_state = gr.State(value="")  # Initialize state for each user session
        gr_session = gr.Textbox(label='Session', visible=False)
        gr_conversion_progress = gr.Textbox(label='Progress')
        gr_convert_btn = gr.Button('Convert', variant='primary', interactive=False)
        gr_audio_player = gr.Audio(label='Listen', type='filepath', show_download_button=False, container=True, visible=False)
        gr_audiobooks_ddn = gr.Dropdown(choices=[], label='Audiobooks')
        gr_audiobook_link = gr.File(label='Download')
        gr_write_data = gr.JSON(visible=False)
        gr_read_data = gr.JSON(visible=False)
        gr_data = gr.State({})
        gr_modal_html = gr.HTML()

        def show_modal(message):
            return f'''
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
            '''

        def hide_modal():
            return ''

        def update_interface():
            nonlocal is_converting
            is_converting = False
            return gr.update('Convert', variant='primary', interactive=False), gr.update(value=None), gr.update(value=None), gr.update(value=audiobook_file), update_audiobooks_ddn(), hide_modal()

        def refresh_audiobook_list():
            files = []
            if audiobooks_dir is not None:
                if os.path.exists(audiobooks_dir):
                    files = [f for f in os.listdir(audiobooks_dir)]
                    files.sort(key=lambda x: os.path.getmtime(os.path.join(audiobooks_dir, x)), reverse=True)
            return files

        def change_gr_audiobooks_ddn(audiobook):
            if audiobooks_dir is not None:
                if audiobook:
                    link = os.path.join(audiobooks_dir, audiobook)
                    return link, link, gr.update(visible=True)
            return None, None, gr.update(visible=False)
            
        def update_convert_btn(upload_file=None, custom_model_file=None, session_id=None):
            if demo_space_check(conf.demo_huggingface):
                raise gr.Error("🤨👉⚠️ This is a non-functional GUI Demo, please duplicate this space or run it locally for full functionality, more info on github.", duration=15)
                return
            elif session_id is None:
                yield gr.update(variant='primary', interactive=False)
                return
            else:
                session = context.get_session(session_id)
                if hasattr(upload_file, 'name') and not hasattr(custom_model_file, 'name'):
                    yield gr.update(variant='primary', interactive=True)
                else:
                    yield gr.update(variant='primary', interactive=False)   
                return

        def update_audiobooks_ddn():
            files = refresh_audiobook_list()
            return gr.update(choices=files, label='Audiobooks', value=files[0] if files else None)

        async def change_gr_ebook_file(f, session_id):
            nonlocal is_converting
            if context and session_id:
                session = context.get_session(session_id)
                if f is None:
                    if is_converting:
                        session['cancellation_requested'] = True
                        yield show_modal('Cancellation requested, please wait...')
                        return
            session['cancellation_requested'] = False
            yield hide_modal()
            return
        
        def change_gr_language(selected: str, session_id: str):
            nonlocal custom_model_options
            if selected == 'zzzz':
                new_language_name = default_language_name
                new_language_key = default_language_code
            else:
                new_language_name, new_language_key = next(((name, key) for name, key in language_options if key == selected), (None, None))
            tts_engine_options = ['xtts'] if language_xtts.get(new_language_key, False) else ['fairseq']
            fine_tuned_options = [
                model_name
                for model_name, model_details in models.get(tts_engine_options[0], {}).items()
                if model_details.get('lang') == 'multi' or model_details.get('lang') == new_language_key
            ]
            custom_model_options = ['none']
            if context and session_id:
                session = context.get_session(session_id)
                session['language'] = new_language_key
                custom_model_tts = check_custom_model_tts(session)
                custom_model_tts_dir = os.path.join(session['custom_model_dir'], custom_model_tts)
                if os.path.exists(custom_model_tts_dir):
                    custom_model_options += os.listdir(custom_model_tts_dir)
            return (
                gr.update(value=new_language_name),
                gr.update(choices=tts_engine_options, value=tts_engine_options[0]),
                gr.update(choices=fine_tuned_options, value=fine_tuned_options[0] if fine_tuned_options else 'none'),
                gr.update(choices=custom_model_options, value=custom_model_options[0])
            )

        def check_custom_model_tts(session):
            custom_model_tts = 'xtts'
            if not language_xtts.get(session['language']):
                custom_model_tts = 'fairseq'
            custom_model_tts_dir = os.path.join(session['custom_model_dir'], custom_model_tts)
            if not os.path.isdir(custom_model_tts_dir):
                os.makedirs(custom_model_tts_dir, exist_ok=True)
            return custom_model_tts

        def change_gr_custom_model_list(custom_model_list):
            if custom_model_list == 'none':
                return gr.update(visible=True)
            return gr.update(visible=False)
            
        async def change_gr_custom_model_file(custom_model_file, session_id):
            try:
                nonlocal custom_model_options, gr_custom_model_file, gr_conversion_progress
                if context and session_id:
                    session = context.get_session(session_id)
                    if custom_model_file is not None:
                        if analyze_uploaded_file(custom_model_file):                        
                            session['custom_model'], progress_status = extract_custom_model(custom_model_file, None, session)
                            if session['custom_model']:
                                custom_model_tts_dir = check_custom_model_tts(session)
                                custom_model_options = ['none'] + os.listdir(os.path.join(session['custom_model_dir'], custom_model_tts_dir))
                                yield (
                                    gr.update(visible=False),
                                    gr.update(choices=custom_model_options, value=session['custom_model']),
                                    gr.update(value=f"{session['custom_model']} added to the custom list")
                                )
                                gr_custom_model_file = gr.File(label='*XTTS Model (a .zip containing config.json, vocab.json, model.pth, ref.wav)', value=None, file_types=['.zip'])
                                return
                        yield gr.update(), gr.update(), gr.update(value='Invalid file! Please upload a valid ZIP.')
                        return
            except Exception as e:
                yield gr.update(), gr.update(), gr.update(value=f'Error: {str(e)}')
                return

        def change_gr_tts_engine(engine):
            if engine == 'xtts':
                return gr.update(visible=True)
            else:
                return gr.update(visible=False)
            
        def change_gr_fine_tuned(fine_tuned):
            visible = False
            if fine_tuned == 'std':
                visible = True
            return gr.update(visible=visible)

        def change_gr_data(data):
            data['event'] = 'change_data'
            return data

        def change_gr_read_data(data):
            nonlocal audiobooks_dir
            nonlocal custom_model_options
            warning_text_extra = ''
            if not data:
                data = {'session_id': str(uuid.uuid4())}
                warning_text = f"Session: {data['session_id']}"
            else:
                if 'session_id' not in data:
                    data['session_id'] = str(uuid.uuid4())
                warning_text = data['session_id']
                event = data.get('event', '')
                if event != 'load':
                    return [gr.update(), gr.update(), gr.update(), gr.update(), gr.update()]
            session = context.get_session(data['session_id'])
            session['custom_model_dir'] = os.path.join(models_dir,'__sessions',f"model-{session['id']}")
            os.makedirs(session['custom_model_dir'], exist_ok=True)
            custom_model_tts_dir = check_custom_model_tts(session)
            custom_model_options = ['none'] + os.listdir(os.path.join(session['custom_model_dir'],custom_model_tts_dir))
            if is_gui_shared:
                warning_text_extra = f' Note: access limit time: {interface_shared_expire} hours'
                audiobooks_dir = os.path.join(audiobooks_gradio_dir, f"web-{data['session_id']}")
                delete_old_web_folders(audiobooks_gradio_dir)
            else:
                audiobooks_dir = os.path.join(audiobooks_host_dir, f"web-{data['session_id']}")
            return [data, f'{warning_text}{warning_text_extra}', data['session_id'], update_audiobooks_ddn(), gr.update(choices=custom_model_options, value='none')]

        def submit_convert_btn(
            session, device, ebook_file, voice_file, language, 
            custom_model_file, temperature, length_penalty,
            repetition_penalty, top_k, top_p, speed, enable_text_splitting, fine_tuned
        ):
            nonlocal is_converting

            args = {
                "is_gui_process": is_gui_process,
                "session": session,
                "script_mode": script_mode,
                "device": device.lower(),
                "ebook": ebook_file.name if ebook_file else None,
                "audiobooks_dir": audiobooks_dir,
                "voice": voice_file.name if voice_file else None,
                "language": next((key for name, key in language_options if name == language), None),
                "custom_model": next((key for name, key in language_options if name != 'none'), None),
                "temperature": float(temperature),
                "length_penalty": float(length_penalty),
                "repetition_penalty": float(repetition_penalty),
                "top_k": int(top_k),
                "top_p": float(top_p),
                "speed": float(speed),
                "enable_text_splitting": enable_text_splitting,
                "fine_tuned": fine_tuned
            }

            if args["ebook"] is None:
                yield gr.update(value='Error: a file is required.')
                return

            try:
                is_converting = True
                progress_status, audiobook_file = convert_ebook(args)
                if audiobook_file is None:
                    if is_converting:
                        yield gr.update(value='Conversion cancelled.')
                        return
                    else:
                        yield gr.update(value='Conversion failed.')
                        return
                else:
                    yield progress_status
                    return
            except Exception as e:
                yield DependencyError(e)
                return

        gr_ebook_file.change(
            fn=update_convert_btn,
            inputs=[gr_ebook_file, gr_custom_model_file, gr_session],
            outputs=gr_convert_btn
        ).then(
            fn=change_gr_ebook_file,
            inputs=[gr_ebook_file, gr_session],
            outputs=[gr_modal_html]
        )
        gr_language.change(
            fn=lambda selected, session_id: change_gr_language(dict(language_options).get(selected, 'Unknown'), session_id),
            inputs=[gr_language, gr_session],
            outputs=[gr_language, gr_tts_engine, gr_fine_tuned, gr_custom_model_list]
        )
        gr_audiobooks_ddn.change(
            fn=change_gr_audiobooks_ddn,
            inputs=gr_audiobooks_ddn,
            outputs=[gr_audiobook_link, gr_audio_player, gr_audio_player]
        )
        gr_custom_model_file.change(
            fn=change_gr_custom_model_file,
            inputs=[gr_custom_model_file, gr_session],
            outputs=[gr_fine_tuned, gr_custom_model_list, gr_conversion_progress]
        )
        gr_custom_model_list.change(
            fn=change_gr_custom_model_list,
            inputs=gr_custom_model_list,
            outputs=gr_fine_tuned
        )
        gr_tts_engine.change(
            fn=change_gr_tts_engine,
            inputs=gr_tts_engine,
            outputs=gr_tab_preferences
        )
        gr_fine_tuned.change(
            fn=change_gr_fine_tuned,
            inputs=gr_fine_tuned,
            outputs=gr_group_custom_model
        )
        gr_session.change(
            fn=change_gr_data,
            inputs=gr_data,
            outputs=gr_write_data
        )
        gr_write_data.change(
            fn=None,
            inputs=gr_write_data,
            js='''
            (data) => {
              localStorage.clear();
              console.log(data);
              window.localStorage.setItem('data', JSON.stringify(data));
            }
            '''
        )       
        gr_read_data.change(
            fn=change_gr_read_data,
            inputs=gr_read_data,
            outputs=[gr_data, gr_session_status, gr_session, gr_audiobooks_ddn, gr_custom_model_list]
        )       
        gr_convert_btn.click(
            fn=update_convert_btn,
            inputs=None,
            outputs=gr_convert_btn
        ).then(
            fn=submit_convert_btn,
            inputs=[
                gr_session, gr_device, gr_ebook_file, gr_voice_file, gr_language, 
                gr_custom_model_list, gr_temperature, gr_length_penalty,
                gr_repetition_penalty, gr_top_k, gr_top_p, gr_speed, gr_enable_text_splitting, gr_fine_tuned
            ],
            outputs=gr_conversion_progress
        ).then(
            fn=update_interface,
            inputs=None,
            outputs=[gr_convert_btn, gr_ebook_file, gr_voice_file, gr_audio_player, gr_audiobooks_ddn, gr_modal_html]
        )
        interface.load(
            fn=None,
            js='''
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
            ''',
            outputs=gr_read_data
        )

    try:
        interface.queue(default_concurrency_limit=interface_concurrency_limit).launch(server_name=interface_host, server_port=interface_port, share=is_gui_shared)
    except OSError as e:
        print(f'Connection error: {e}')
    except socket.error as e:
        print(f'Socket error: {e}')
    except KeyboardInterrupt:
        print('Server interrupted by user. Shutting down...')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
