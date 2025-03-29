# NOTE!!NOTE!!!NOTE!!NOTE!!!NOTE!!NOTE!!!NOTE!!NOTE!!!
# THE WORD "CHAPTER" IN THE CODE DOES NOT MEAN
# IT'S THE REAL CHAPTER OF THE EBOOK SINCE NO STANDARDS
# ARE DEFINING A CHAPTER ON .EPUB FORMAT. THE WORD "BLOCK"
# IS USED TO PRINT IT OUT TO THE TERMINAL, AND "CHAPTER" TO THE CODE
# WHICH IS LESS GENERIC FOR THE DEVELOPERS

import argparse
import asyncio
import csv
import ebooklib
import fnmatch
import gc
import gradio as gr
import hashlib
import json
import math
import os
import platform
import psutil
import pymupdf4llm
import random
import regex as re
import requests
import shutil
import socket
import subprocess
import sys
import threading
import time
import torch
import urllib.request
import uuid
import zipfile
import traceback
import unicodedata

import lib.conf as conf
import lib.lang as lang
import lib.models as mod

from bs4 import BeautifulSoup
from collections import Counter
from collections.abc import Mapping
from collections.abc import MutableMapping
from datetime import datetime
from ebooklib import epub
from fastapi import FastAPI
from glob import glob
from iso639 import languages
from multiprocessing import Manager, Event
from multiprocessing.managers import DictProxy, ListProxy
from num2words import num2words
from pathlib import Path
from pydub import AudioSegment
from queue import Queue, Empty
from starlette.requests import ClientDisconnect
from tqdm import tqdm
from types import MappingProxyType
from urllib.parse import urlparse

#from lib.classes.redirect_console import RedirectConsole
from lib.classes.voice_extractor import VoiceExtractor
#from lib.classes.argos_translator import ArgosTranslator
from lib.classes.tts_manager import TTSManager

def inject_configs(target_namespace):
    # Extract variables from both modules and inject them into the target namespace
    for module in (conf, lang, mod):
        target_namespace.update({k: v for k, v in vars(module).items() if not k.startswith('__')})

# Inject configurations into the global namespace of this module
inject_configs(globals())

class DependencyError(Exception):
    def __init__(self, message=None):
        super().__init__(message)
        print(message)
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

def recursive_proxy(data, manager=None):
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
    elif isinstance(data, (str, int, float, bool, type(None))):
        return data
    else:
        error = f"Unsupported data type: {type(data)}"
        print(error)
        return

class SessionContext:
    def __init__(self):
        self.manager = Manager()
        self.sessions = self.manager.dict()  # Store all session-specific contexts
        self.cancellation_events = {}  # Store multiprocessing.Event for each session

    def get_session(self, id):
        if id not in self.sessions:
            self.sessions[id] = recursive_proxy({
                "script_mode": NATIVE,
                "id": id,
                "process_id": None,
                "device": default_device,
                "system": None,
                "client": None,
                "language": default_language_code,
                "language_iso1": None,
                "audiobook": None,
                "audiobooks_dir": None,
                "process_dir": None,
                "ebook": None,
                "ebook_list": None,
                "ebook_mode": "single",
                "chapters_dir": None,
                "chapters_dir_sentences": None,
                "epub_path": None,
                "filename_noext": None,
                "tts_engine": default_tts_engine,
                "fine_tuned": default_fine_tuned,
                "voice": None,
                "voice_dir": None,
                "custom_model": None,
                "custom_model_dir": None,
                "toc": None,
                "chapters": None,
                "cover": None,
                "status": None,
                "progress": 0,
                "time": None,
                "cancellation_requested": False,
                "temperature": default_xtts_settings['temperature'],
                "length_penalty": default_xtts_settings['length_penalty'],
                "num_beams": default_xtts_settings['num_beams'],
                "repetition_penalty": default_xtts_settings['repetition_penalty'],
                "top_k": default_xtts_settings['top_k'],
                "top_p": default_xtts_settings['top_k'],
                "speed": default_xtts_settings['speed'],
                "enable_text_splitting": default_xtts_settings['enable_text_splitting'],
                "event": None,
                "output_format": default_output_format,
                "metadata": {
                    "title": None, 
                    "creator": None,
                    "contributor": None,
                    "language": None,
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
                }
            }, manager=self.manager)
        return self.sessions[id]

app = FastAPI()
lock = threading.Lock()
context = SessionContext()
is_gui_process = False

def prepare_dirs(src, session):
    try:
        resume = False
        os.makedirs(os.path.join(models_dir,'tts'), exist_ok=True)
        os.makedirs(session['session_dir'], exist_ok=True)
        os.makedirs(session['process_dir'], exist_ok=True)
        os.makedirs(session['custom_model_dir'], exist_ok=True)
        os.makedirs(session['voice_dir'], exist_ok=True)
        os.makedirs(session['audiobooks_dir'], exist_ok=True)
        session['ebook'] = os.path.join(session['process_dir'], os.path.basename(src))
        if os.path.exists(session['ebook']):
            if compare_files_by_hash(session['ebook'], src):
                resume = True
        if not resume:
            shutil.rmtree(session['chapters_dir'], ignore_errors=True)
        os.makedirs(session['chapters_dir'], exist_ok=True)
        os.makedirs(session['chapters_dir_sentences'], exist_ok=True)
        shutil.copy(src, session['ebook']) 
        return True
    except Exception as e:
        DependencyError(e)
        return False

def check_programs(prog_name, command, options):
    try:
        subprocess.run(
            [command, options],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=True,
            text=True,
            encoding='utf-8'
        )
        return True, None
    except FileNotFoundError:
        e = f'''********** Error: {prog_name} is not installed! if your OS calibre package version 
        is not compatible you still can run ebook2audiobook.sh (linux/mac) or ebook2audiobook.cmd (windows) **********'''
        DependencyError(e)
        return False, None
    except subprocess.CalledProcessError:
        e = f'Error: There was an issue running {prog_name}.'
        DependencyError(e)
        return False, None

def analyze_uploaded_file(zip_path, required_files):
    try:
        if not os.path.exists(zip_path):
            error = f"The file does not exist: {os.path.basename(zip_path)}"
            print(error)
            return False
        files_in_zip = {}
        empty_files = set()
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for file_info in zf.infolist():
                file_name = file_info.filename
                if file_info.is_dir():
                    continue
                base_name = os.path.basename(file_name)
                files_in_zip[base_name.lower()] = file_info.file_size
                if file_info.file_size == 0:
                    empty_files.add(base_name.lower())
        required_files = [file.lower() for file in required_files]
        missing_files = [f for f in required_files if f not in files_in_zip]
        required_empty_files = [f for f in required_files if f in empty_files]
        if missing_files:
            print(f"Missing required files: {missing_files}")
        if required_empty_files:
            print(f"Required files with 0 KB: {required_empty_files}")
        return not missing_files and not required_empty_files
    except zipfile.BadZipFile:
        error = "The file is not a valid ZIP archive."
        raise ValueError(error)
    except Exception as e:
        error = f"An error occurred: {e}"
        raise RuntimeError(error)

def extract_custom_model(file_src, session, required_files=None):
    try:
        model_path = None
        if required_files is None:
            required_files = models[session['tts_engine']][default_fine_tuned]['files']
        model_name = re.sub('.zip', '', os.path.basename(file_src), flags=re.IGNORECASE)
        model_name = get_sanitized(model_name)
        with zipfile.ZipFile(file_src, 'r') as zip_ref:
            files = zip_ref.namelist()
            files_length = len(files)
            tts_dir = session['tts_engine']    
            model_path = os.path.join(session['custom_model_dir'], tts_dir, model_name)
            if os.path.exists(model_path):
                print(f'{model_path} already exists, bypassing files extraction')
                return model_path
            os.makedirs(model_path, exist_ok=True)
            with tqdm(total=files_length, unit='files') as t:
                for f in files:
                    if f in required_files:
                        zip_ref.extract(f, model_path)
                    t.update(1)
        if is_gui_process:
            os.remove(file_src)
        if model_path is not None:
            msg = f'Extracted files to {model_path}'
            print(msg)
            return model_name
        else:
            error = f'An error occured when unzip {file_src}'
            return None
    except asyncio.exceptions.CancelledError:
        DependencyError(e)
        if is_gui_process:
            os.remove(file_src)
        return None       
    except Exception as e:
        DependencyError(e)
        if is_gui_process:
            os.remove(file_src)
        return None
        
def hash_proxy_dict(proxy_dict):
    return hashlib.md5(str(proxy_dict).encode('utf-8')).hexdigest()

def calculate_hash(filepath, hash_algorithm='sha256'):
    hash_func = hashlib.new(hash_algorithm)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):  # Read in chunks to handle large files
            hash_func.update(chunk)
    return hash_func.hexdigest()

def compare_files_by_hash(file1, file2, hash_algorithm='sha256'):
    return calculate_hash(file1, hash_algorithm) == calculate_hash(file2, hash_algorithm)

def compare_dict_keys(d1, d2):
    if not isinstance(d1, Mapping) or not isinstance(d2, Mapping):
        return d1 == d2
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    missing_in_d2 = d1_keys - d2_keys
    missing_in_d1 = d2_keys - d1_keys
    if missing_in_d2 or missing_in_d1:
        return {
            "missing_in_d2": missing_in_d2,
            "missing_in_d1": missing_in_d1,
        }
    for key in d1_keys.intersection(d2_keys):
        nested_result = compare_keys(d1[key], d2[key])
        if nested_result:
            return {key: nested_result}
    return None

def proxy_to_dict(proxy_obj):
    def recursive_copy(source, visited):
        # Handle circular references by tracking visited objects
        if id(source) in visited:
            return None  # Stop processing circular references
        visited.add(id(source))  # Mark as visited
        if isinstance(source, dict):
            result = {}
            for key, value in source.items():
                result[key] = recursive_copy(value, visited)
            return result
        elif isinstance(source, list):
            return [recursive_copy(item, visited) for item in source]
        elif isinstance(source, set):
            return list(source)
        elif isinstance(source, (int, float, str, bool, type(None))):
            return source
        elif isinstance(source, DictProxy):
            # Explicitly handle DictProxy objects
            return recursive_copy(dict(source), visited)  # Convert DictProxy to dict
        else:
            return str(source)  # Convert non-serializable types to strings
    return recursive_copy(proxy_obj, set())

def math2word(text, lang, lang_iso1, tts_engine):
    def check_compat():
        try:
            num2words(1, lang=lang_iso1)
            return True
        except NotImplementedError:
            return False
        except Exception as e:
            return False

    def rep_num(match):
        number = match.group().strip().replace(",", "")
        try:
            if "." in number or "e" in number or "E" in number:
                number_value = float(number)
            else:
                number_value = int(number)
            number_in_words = num2words(number_value, lang=lang_iso1)
            return f" {number_in_words}"
        except Exception as e:
            print(f"Error converting number: {number}, Error: {e}")
            return f"{number}"

    def replace_ambiguous(match):
        symbol2 = match.group(2)
        symbol3 = match.group(3)
        if symbol2 in ambiguous_replacements: # "num SYMBOL num" case
            return f"{match.group(1)} {ambiguous_replacements[symbol2]} {match.group(3)}"            
        elif symbol3 in ambiguous_replacements: # "SYMBOL num" case
            return f"{ambiguous_replacements[symbol3]} {match.group(4)}"
        return match.group(0)

    is_num2words_compat = check_compat()
    phonemes_list = language_math_phonemes.get(lang, language_math_phonemes[default_language_code])
    # Separate ambiguous and non-ambiguous symbols
    ambiguous_symbols = {"-", "/", "*", "x"}
    replacements = {k: v for k, v in phonemes_list.items() if not k.isdigit()}  # Keep only math symbols
    normal_replacements = {k: v for k, v in replacements.items() if k not in ambiguous_symbols}
    ambiguous_replacements = {k: v for k, v in replacements.items() if k in ambiguous_symbols}
    # Replace unambiguous math symbols normally
    if normal_replacements:
        math_pattern = r'(' + '|'.join(map(re.escape, normal_replacements.keys())) + r')'
        text = re.sub(math_pattern, lambda m: f" {normal_replacements[m.group(0)]} ", text)
    # Regex pattern for ambiguous symbols (match only valid equations)
    ambiguous_pattern = (
        r'(?<!\S)(\d+)\s*([-/*x])\s*(\d+)(?!\S)|'  # Matches "num SYMBOL num" (e.g., "3 + 5", "7-2", "8 * 4")
        r'(?<!\S)([-/*x])\s*(\d+)(?!\S)'           # Matches "SYMBOL num" (e.g., "-4", "/ 9")
    )
    if ambiguous_replacements:
        text = re.sub(ambiguous_pattern, replace_ambiguous, text)
    # Regex pattern for detecting numbers (handles negatives, commas, decimals, scientific notation)
    number_pattern = r'\s*(-?\d{1,3}(?:,\d{3})*(?:\.\d+(?!\s|$))?(?:[eE][-+]?\d+)?)\s*'
    if tts_engine == VITS or tts_engine == FAIRSEQ or tts_engine == YOURTTS:
        if is_num2words_compat:
            # Pattern 2: Split big numbers into groups of 4
            text = re.sub(r'(\d{4})(?=\d{4}(?!\.\d))', r'\1 ', text)
            text = re.sub(number_pattern, rep_num, text)
        else:
            # Pattern 2: Split big numbers into groups of 2
            text = re.sub(r'(\d{2})(?=\d{2}(?!\.\d))', r'\1 ', text)
            # Fallback: Replace numbers using phonemes dictionary
            sorted_numbers = sorted((k for k in phonemes_list if k.isdigit()), key=len, reverse=True)
            if sorted_numbers:
                number_pattern = r'\b(' + '|'.join(map(re.escape, sorted_numbers)) + r')\b'
                text = re.sub(number_pattern, lambda match: phonemes_list[match.group(0)], text)
    return text

def normalize_text(text, lang, lang_iso1, tts_engine):
    # Replace punctuations causing hallucinations
    pattern = f"[{''.join(map(re.escape, punctuation_switch.keys()))}]"
    text = re.sub(pattern, lambda match: punctuation_switch.get(match.group(), match.group()), text)
    # Replace NBSP with a normal space
    text = text.replace("\xa0", " ")
    if lang in abbreviations_mapping:
        pattern = r'\b(' + '|'.join(re.escape(k) for k in abbreviations_mapping[lang]) + r')\b'
        text = re.sub(pattern, lambda match: abbreviations_mapping[lang].get(match.group(0), match.group(0)), text)
    # Replace multiple newlines ("\n\n", "\r\r", "\n\r") with " . " as many times as they occur
    #text = re.sub('(\r\n|\n\n|\r\r|\n\r)+', lambda m: ' . ' * (m.group().count("\n") // 2 + m.group().count("\r") // 2), text)
    # Replace multiple newlines ("\n\n", "\r\r", "\n\r", etc.) with a single "\n"
    text = re.sub(r'(\r\n|\r|\n)+', '\n', text)
    # Replace single newlines ("\n" or "\r") with spaces
    text = re.sub(r'[\r\n]', ' ', text)
    # Replace multiple  and spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)
    # replace roman numbers by digits
    text = replace_roman_numbers(text)
    # Escape special characters in the punctuation list for regex
    pattern = '|'.join(map(re.escape, punctuation_split))
    # Reduce multiple consecutive punctuations
    text = re.sub(rf'(\s*({pattern})\s*)+', r'\2 ', text).strip()
    if tts_engine == XTTSv2:
        # Pattern 1: Add a space between UTF-8 characters and numbers
        text = re.sub(r'(?<=[\p{L}])(?=\d)|(?<=\d)(?=[\p{L}])', ' ', text)
    # Replace math symbols with words
    text = math2word(text, lang, lang_iso1, tts_engine)
    return text

def convert_to_epub(session):
    if session['cancellation_requested']:
        print('Cancel requested')
        return False
    try:
        util_app = shutil.which('ebook-convert')
        if not util_app:
            error = "The 'ebook-convert' utility is not installed or not found."
            print(error)
            return False
        file_input = session['ebook']
        file_ext = os.path.splitext(file_input)[1].lower()
        if file_ext not in ebook_formats:
            error = f'Unsupported file format: {file_ext}'
            print(error)
            return False
        if file_ext == '.pdf':
            msg = 'File input is a PDF. flatten it in MD format...'
            print(msg)
            file_input = f"{os.path.splitext(session['epub_path'])[0]}.md"
            markdown_text = pymupdf4llm.to_markdown(session['ebook'])
            with open(file_input, "w", encoding="utf-8") as md_file:
                md_file.write(markdown_text)
        msg = f"Running command: {util_app} {file_input} {session['epub_path']}"
        print(msg)
        result = subprocess.run(
            [
                util_app, file_input, session['epub_path'],
                '--input-encoding=utf-8',
                '--output-profile=generic_eink',
                '--epub-version=3',
                '--flow-size=0',
                '--chapter-mark=pagebreak',
                '--page-breaks-before', "//*[name()='h1' or name()='h2']",
                '--disable-font-rescaling',
                '--pretty-print',
                '--smarten-punctuation',
                '--verbose'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e.stderr}")
        DependencyError(e)
        return False
    except FileNotFoundError as e:
        print(f"Utility not found: {e}")
        DependencyError(e)
        return False

def filter_chapter(doc, lang, lang_iso1, tts_engine):
    soup = BeautifulSoup(doc.get_body_content(), 'html.parser')
    # Remove scripts and styles
    for script in soup(["script", "style"]):
        script.decompose()
    # Normalize lines and remove unnecessary spaces and switch special chars
    text = normalize_text(soup.get_text().strip(), lang, lang_iso1, tts_engine)
    if tts_engine == XTTSv2:
        # Ensure spaces before & after punctuation
        pattern_space = re.escape(''.join(punctuation_list))
        # Ensure space before and after punctuation (excluding `,` and `.`)
        punctuation_pattern_space = r'\s*([{}])\s*'.format(pattern_space.replace(',', '').replace('.', ''))
        text = re.sub(punctuation_pattern_space, r' \1 ', text)
        # Ensure spaces before & after `,` and `.` ONLY when NOT between numbers
        comma_dot_pattern = r'(?<!\d)\s*(\.{3}|[,.])\s*(?!\d)'
        text = re.sub(comma_dot_pattern, r' \1 ', text)
    if not text.strip():
        chapter_sentences = []
    else:
        chapter_sentences = get_sentences(text, lang)
    return chapter_sentences

def filter_doc(doc_patterns):
    pattern_counter = Counter(doc_patterns)
    # Returns a list with one tuple: [(pattern, count)]
    most_common = pattern_counter.most_common(1)
    return most_common[0][0] if most_common else None

def filter_pattern(doc_identifier):
    docs = doc_identifier.split(':')
    if len(docs) > 2:
        segment = docs[1]
        if re.search(r'[a-zA-Z]', segment) and re.search(r'\d', segment):
            return ''.join([char for char in segment if char.isalpha()])
        elif re.match(r'^[a-zA-Z]+$', segment):
            return segment
        elif re.match(r'^\d+$', segment):
            return 'numbers'
    return None

def get_cover(epubBook, session):
    try:
        if session['cancellation_requested']:
            print('Cancel requested')
            return False
        cover_image = False
        cover_path = os.path.join(session['process_dir'], session['filename_noext'] + '.jpg')
        for item in epubBook.get_items_of_type(ebooklib.ITEM_COVER):
            cover_image = item.get_content()
            break
        if not cover_image:
            for item in epubBook.get_items_of_type(ebooklib.ITEM_IMAGE):
                if 'cover' in item.file_name.lower() or 'cover' in item.get_id().lower():
                    cover_image = item.get_content()
                    break
        if cover_image:
            with open(cover_path, 'wb') as cover_file:
                cover_file.write(cover_image)
                return cover_path
        return True
    except Exception as e:
        DependencyError(e)
        return False

def get_chapters(epubBook, session):
    try:
        if session['cancellation_requested']:
            print('Cancel requested')
            return False
        # Step 1: Extract TOC (Table of Contents)
        toc_list = []
        try:
            toc = epubBook.toc  # Extract TOC
            toc_list = [normalize_text(str(item.title), session['language'], session['language_iso1'], session['tts_engine']) 
                        for item in toc if hasattr(item, 'title')]  # Normalize TOC entries
        except Exception as toc_error:
            error = f"Error extracting TOC: {toc_error}"
            print(error)
        all_docs = list(epubBook.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        if not all_docs:
            return [], []        
        all_docs = all_docs[1:]  # Exclude the first document if needed
        doc_cache = {}
        msg = r'''
            ***************************************************************************************
                                            NOTE: THE WARNING
                                "Character xx not found in the vocabulary."
            MEANS THE MODEL CANNOT INTERPRET THE CHARACTER AND WILL MAYBE GENERATE AN HALLUCINATION
            TO IMPROVE THIS MODEL IT NEEDS TO ADD THIS CHARACTER INTO A NEW TRAINING MODEL.
            YOU CAN IMPROVE IT OR ASK TO A MODEL TRAINING DEVELOPER.
            ***************************************************************************************
        '''
        print(msg)
        for doc in all_docs:
            doc_cache[doc] = filter_chapter(doc, session['language'], session['language_iso1'], session['tts_engine'])
        # Step 4: Determine the most common pattern
        doc_patterns = [filter_pattern(str(doc)) for doc in all_docs if filter_pattern(str(doc))]
        most_common_pattern = filter_doc(doc_patterns)
        # Step 5: Calculate average character length
        char_length = [len(content) for content in doc_cache.values()]
        average_char_length = sum(char_length) / len(char_length) if char_length else 0
        # Step 6: Filter docs based on character length or pattern
        final_selected_docs = [
            doc for doc in all_docs
            if doc in doc_cache and doc_cache[doc]
            and (len(doc_cache[doc]) >= average_char_length or filter_pattern(str(doc)) == most_common_pattern)
        ]
        # Step 7: Extract parts from the final selected docs
        chapters = [doc_cache[doc] for doc in final_selected_docs]
        # Step 8: Return both TOC and Chapters separately
        return toc, chapters
    except Exception as e:
        error = f'Error extracting main content pages: {e}'
        DependencyError(error)
        return None, None

def get_sentences(text, lang):
    max_tokens = language_mapping[lang]['max_tokens']
    max_chars = max_tokens * 10
    pattern_split = [re.escape(p) for p in punctuation_split]
    pattern = f"({'|'.join(pattern_split)})"

    def segment_ideogramms():
        if lang == 'zho':
            import jieba
            return list(jieba.cut(text))
        elif lang == 'jpn':
            import MeCab
            mecab = MeCab.Tagger()
            return mecab.parse(text).split()
        elif lang == 'kor':
            from konlpy.tag import Kkma
            kkma = Kkma()
            return kkma.morphs(text)
        elif lang in ['tha', 'lao', 'mya', 'khm']:
            from pythainlp.tokenize import word_tokenize
            return word_tokenize(text, engine='newmm')

    def split_sentence(sentence):
        end = ''
        if len(sentence) <= max_chars:
            if not sentence:
                return []
            if sentence[-1].isalpha():
                end = '–'
            return [sentence + end]
        if ',' in sentence:
            mid_index = len(sentence) // 2
            left_split = sentence.rfind(",", 0, mid_index)
            right_split = sentence.find(",", mid_index)
            if left_split != -1 and (right_split == -1 or mid_index - left_split < right_split - mid_index):
                split_index = left_split + 1
            else:
                split_index = right_split + 1 if right_split != -1 else mid_index
        elif ';' in sentence:
            mid_index = len(sentence) // 2
            left_split = sentence.rfind(";", 0, mid_index)
            right_split = sentence.find(";", mid_index)
            if left_split != -1 and (right_split == -1 or mid_index - left_split < right_split - mid_index):
                split_index = left_split + 1
            else:
                split_index = right_split + 1 if right_split != -1 else mid_index
        elif ':' in sentence:
            mid_index = len(sentence) // 2
            left_split = sentence.rfind(":", 0, mid_index)
            right_split = sentence.find(":", mid_index)
            if left_split != -1 and (right_split == -1 or mid_index - left_split < right_split - mid_index):
                split_index = left_split + 1
            else:
                split_index = right_split + 1 if right_split != -1 else mid_index
        elif ' ' in sentence:
            mid_index = len(sentence) // 2
            left_split = sentence.rfind(" ", 0, mid_index)
            right_split = sentence.find(" ", mid_index)
            if left_split != -1 and (right_split == -1 or mid_index - left_split < right_split - mid_index):
                split_index = left_split
            else:
                split_index = right_split if right_split != -1 else mid_index
            end = '–'
        else:
            split_index = len(sentence) // 2
            end = '–'
        if split_index == len(sentence):
            if sentence[-1].isalpha():
                end = '–'
            return [sentence + end]
        part1 = sentence[:split_index]
        part2 = sentence[split_index + 1:] if sentence[split_index] in [' ', ',', ';', ':'] else sentence[split_index:]
        return split_sentence(part1.strip()) + split_sentence(part2.strip())     

    if lang in ['zho', 'jpn', 'kor', 'tha', 'lao', 'mya', 'khm']:
        raw_list = segment_ideogramms()
    else:
        raw_list = re.split(pattern, text)

    if len(raw_list) > 1:
        tmp_list = [raw_list[i] + raw_list[i + 1] for i in range(0, len(raw_list) - 1, 2)]
    else:
        tmp_list = raw_list
        
    if tmp_list[-1] == 'Start':
        tmp_list.pop()
    sentences = []
    for sentence in tmp_list:
        sentences.extend(split_sentence(sentence.strip()))  
    #print(json.dumps(sentences, indent=4, ensure_ascii=False))
    return sentences

def get_vram():
    os_name = platform.system()
    # NVIDIA (Cross-Platform: Windows, Linux, macOS)
    try:
        from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(0)  # First GPU
        info = nvmlDeviceGetMemoryInfo(handle)
        vram = info.total
        return int(vram / (1024 ** 3))  # Convert to GB
    except ImportError:
        pass
    except Exception as e:
        pass
    # AMD (Windows)
    if os_name == "Windows":
        try:
            cmd = 'wmic path Win32_VideoController get AdapterRAM'
            output = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            lines = output.stdout.splitlines()
            vram_values = [int(line.strip()) for line in lines if line.strip().isdigit()]
            if vram_values:
                return int(vram_values[0] / (1024 ** 3))
        except Exception as e:
            pass
    # AMD (Linux)
    if os_name == "Linux":
        try:
            cmd = "lspci -v | grep -i 'VGA' -A 12 | grep -i 'preallocated' | awk '{print $2}'"
            output = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if output.stdout.strip().isdigit():
                return int(output.stdout.strip()) // 1024
        except Exception as e:
            pass
    # Intel (Linux Only)
    intel_vram_paths = [
        "/sys/kernel/debug/dri/0/i915_vram_total",  # Intel dedicated GPUs
        "/sys/class/drm/card0/device/resource0"  # Some integrated GPUs
    ]
    for path in intel_vram_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    vram = int(f.read().strip()) // (1024 ** 3)
                    return vram
            except Exception as e:
                pass
    # macOS (OpenGL Alternative)
    if os_name == "Darwin":
        try:
            from OpenGL.GL import glGetIntegerv
            from OpenGL.GLX import GLX_RENDERER_VIDEO_MEMORY_MB_MESA
            vram = int(glGetIntegerv(GLX_RENDERER_VIDEO_MEMORY_MB_MESA) // 1024)
            return vram
        except ImportError:
            pass
        except Exception as e:
            pass
    return 0

def get_sanitized(str, replacement="_"):
    str = str.replace('&', 'And')
    forbidden_chars = r'[<>:"/\\|?*\x00-\x1F ()]'
    sanitized = re.sub(r'\s+', replacement, str)
    sanitized = re.sub(forbidden_chars, replacement, sanitized)
    sanitized = sanitized.strip("_")
    return sanitized

def convert_chapters_to_audio(session):
    try:
        if session['cancellation_requested']:
            print('Cancel requested')
            return False
        progress_bar = None
        if is_gui_process:
            progress_bar = gr.Progress(track_tqdm=True)        
        tts_manager = TTSManager(session, is_gui_process)
        if tts_manager.params['tts'] is None:
            return False
        resume_chapter = 0
        missing_chapters = []
        resume_sentence = 0
        missing_sentences = []
        existing_chapters = sorted(
            [f for f in os.listdir(session['chapters_dir']) if f.endswith(f'.{default_audio_proc_format}')],
            key=lambda x: int(re.search(r'\d+', x).group())
        )
        if existing_chapters:
            resume_chapter = max(int(re.search(r'\d+', f).group()) for f in existing_chapters) 
            msg = f'Resuming from block {resume_chapter}'
            print(msg)
            existing_chapter_numbers = {int(re.search(r'\d+', f).group()) for f in existing_chapters}
            missing_chapters = [
                i for i in range(1, resume_chapter) if i not in existing_chapter_numbers
            ]
            if resume_chapter not in missing_chapters:
                missing_chapters.append(resume_chapter)
        existing_sentences = sorted(
            [f for f in os.listdir(session['chapters_dir_sentences']) if f.endswith(f'.{default_audio_proc_format}')],
            key=lambda x: int(re.search(r'\d+', x).group())
        )
        if existing_sentences:
            resume_sentence = max(int(re.search(r'\d+', f).group()) for f in existing_sentences)
            msg = f"Resuming from sentence {resume_sentence}"
            print(msg)
            existing_sentence_numbers = {int(re.search(r'\d+', f).group()) for f in existing_sentences}
            missing_sentences = [
                i for i in range(1, resume_sentence) if i not in existing_sentence_numbers
            ]
            if resume_sentence not in missing_sentences:
                missing_sentences.append(resume_sentence)
        total_chapters = len(session['chapters'])
        total_sentences = sum(len(array) for array in session['chapters'])
        sentence_number = 0
        with tqdm(total=total_sentences, desc='convertsion 0.00%', bar_format='{desc}: {n_fmt}/{total_fmt} ', unit='step', initial=resume_sentence) as t:
            msg = f'A total of {total_chapters} blocks and {total_sentences} sentences...'
            for x in range(0, total_chapters):
                chapter_num = x + 1
                chapter_audio_file = f'chapter_{chapter_num}.{default_audio_proc_format}'
                sentences = session['chapters'][x]
                sentences_count = len(sentences)
                start = sentence_number
                msg = f'Block {chapter_num} containing {sentences_count} sentences...'
                print(msg)
                for i, sentence in enumerate(sentences):
                    if session['cancellation_requested']:
                        msg = 'Cancel requested'
                        print(msg)
                        return False
                    if sentence_number in missing_sentences or sentence_number > resume_sentence or (sentence_number == 0 and resume_sentence == 0):
                        if sentence_number <= resume_sentence and sentence_number > 0:
                            msg = f'**Recovering missing file sentence {sentence_number}'
                            print(msg)
                        tts_manager.params['sentence_audio_file'] = os.path.join(session['chapters_dir_sentences'], f'{sentence_number}.{default_audio_proc_format}')      
                        if session['tts_engine'] == XTTSv2 or session['tts_engine'] == FAIRSEQ:
                            tts_manager.params['sentence'] = sentence.replace('.', '…')
                        else:
                            tts_manager.params['sentence'] = sentence
                        if tts_manager.params['sentence'] != "":
                            if tts_manager.convert_sentence_to_audio():                           
                                percentage = (sentence_number / total_sentences) * 100
                                t.set_description(f'Converting {percentage:.2f}%')
                                msg = f'\nSentence: {sentence}'
                                print(msg)
                            else:
                                return False
                        t.update(1)
                    if progress_bar is not None:
                        progress_bar(sentence_number / total_sentences)
                    sentence_number += 1
                if progress_bar is not None:
                    progress_bar(sentence_number / total_sentences)
                end = sentence_number - 1 if sentence_number > 1 else sentence_number
                msg = f"End of Block {chapter_num}"
                print(msg)
                if chapter_num in missing_chapters or sentence_number > resume_sentence:
                    if chapter_num <= resume_chapter:
                        msg = f'**Recovering missing file block {chapter_num}'
                        print(msg)
                    if combine_audio_sentences(chapter_audio_file, start, end, session):
                        msg = f'Combining block {chapter_num} to audio, sentence {start} to {end}'
                        print(msg)
                    else:
                        msg = 'combine_audio_sentences() failed!'
                        print(msg)
                        return False
        return True
    except Exception as e:
        DependencyError(e)
        return False

def combine_audio_sentences(chapter_audio_file, start, end, session):
    try:
        chapter_audio_file = os.path.join(session['chapters_dir'], chapter_audio_file)
        file_list = os.path.join(session['chapters_dir_sentences'], 'sentences.txt')
        sentence_files = [f for f in os.listdir(session['chapters_dir_sentences']) if f.endswith(f'.{default_audio_proc_format}')]
        sentences_dir_ordered = sorted(sentence_files, key=lambda x: int(re.search(r'\d+', x).group()))
        selected_files = [
            os.path.join(session['chapters_dir_sentences'], f)
            for f in sentences_dir_ordered
            if start <= int(''.join(filter(str.isdigit, os.path.basename(f)))) <= end
        ]
        if not selected_files:
            error = 'No audio files found in the specified range.'
            print(error)
            return False
        with open(file_list, 'w') as f:
            for file in selected_files:
                file = file.replace("\\", "/")
                f.write(f'file {file}\n')
        ffmpeg_cmd = [
            shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-y', '-safe', '0', '-f', 'concat', '-i', file_list,
            '-c:a', default_audio_proc_format, '-map_metadata', '-1', chapter_audio_file
        ]
        try:
            process = subprocess.Popen(
                ffmpeg_cmd,
                env={},
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='utf-8'
            )
            for line in process.stdout:
                print(line, end='')  # Print each line of stdout
            process.wait()
            if process.returncode == 0:
                os.remove(file_list)
                msg = f'********* Combined block audio file saved to {chapter_audio_file}'
                print(msg)
                return True
            else:
                error = process.returncode
                print(error, ffmpeg_cmd)
                return False
        except subprocess.CalledProcessError as e:
            DependencyError(e)
            return False
    except Exception as e:
        DependencyError(e)
        return False

def combine_audio_chapters(session):
    def assemble_segments():
        try:
            file_list = os.path.join(session['chapters_dir'], 'chapters.txt')
            chapter_files_ordered = sorted(chapter_files, key=lambda x: int(re.search(r'\d+', x).group()))
            if not chapter_files_ordered:
                error = 'No block files found.'
                print(error)
                return False
            with open(file_list, "w") as f:
                for file in chapter_files_ordered:
                    file = file.replace("\\", "/")
                    f.write(f"file '{file}'\n")
            ffmpeg_cmd = [
                shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-y', '-safe', '0', '-f', 'concat', '-i', file_list,
                '-c:a', default_audio_proc_format, '-map_metadata', '-1', combined_chapters_file
            ]
            try:
                process = subprocess.Popen(
                    ffmpeg_cmd,
                    env={},
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    encoding='utf-8'
                )
                for line in process.stdout:
                    print(line, end='')  # Print each line of stdout
                process.wait()
                if process.returncode == 0:
                    os.remove(file_list)
                    msg = f'********* total audio blocks saved to {combined_chapters_file}'
                    print(msg)
                    return True
                else:
                    error = process.returncode
                    print(error, ffmpeg_cmd)
                    return False
            except subprocess.CalledProcessError as e:
                DependencyError(e)
                return False
        except Exception as e:
            DependencyError(e)
            return False

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
                    print(msg)
                    return False
                duration_ms = len(AudioSegment.from_file(os.path.join(session['chapters_dir'],chapter_file), format=default_audio_proc_format))
                ffmpeg_metadata += f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={start_time}\n'
                ffmpeg_metadata += f'END={start_time + duration_ms}\ntitle=Part {index + 1}\n'
                start_time += duration_ms
            # Write the metadata to the file
            with open(metadata_file, 'w', encoding='utf-8') as f:
                f.write(ffmpeg_metadata)
            return True
        except Exception as e:
            DependencyError(e)
            return False

    def export_audio():
        try:
            if session['cancellation_requested']:
                print('Cancel requested')
                return False
            ffmpeg_cover = None
            ffmpeg_combined_audio = combined_chapters_file
            ffmpeg_metadata_file = metadata_file
            ffmpeg_final_file = final_file
            if session['cover'] is not None:
                ffmpeg_cover = session['cover']                    
            ffmpeg_cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', ffmpeg_combined_audio, '-i', ffmpeg_metadata_file]
            if session['output_format'] == 'wav':
                ffmpeg_cmd += ['-map', '0:a']
            elif session['output_format'] ==  'aac':
                ffmpeg_cmd += ['-c:a', 'aac', '-b:a', '128k', '-ar', '44100']
            else:
                if ffmpeg_cover is not None:
                    if session['output_format'] == 'mp3' or session['output_format'] == 'm4a' or session['output_format'] == 'm4b' or session['output_format'] == 'mp4' or session['output_format'] == 'flac':
                        ffmpeg_cmd += ['-i', ffmpeg_cover]
                        ffmpeg_cmd += ['-map', '0:a', '-map', '2:v']
                        if ffmpeg_cover.endswith('.png'):
                            ffmpeg_cmd += ['-c:v', 'png', '-disposition:v', 'attached_pic']  # PNG cover
                        else:
                            ffmpeg_cmd += ['-c:v', 'copy', '-disposition:v', 'attached_pic']  # JPEG cover (no re-encoding needed)
                    elif session['output_format'] == 'mov':
                        ffmpeg_cmd += ['-framerate', '1', '-loop', '1', '-i', ffmpeg_cover]
                        ffmpeg_cmd += ['-map', '0:a', '-map', '2:v', '-shortest']
                    elif session['output_format'] == 'webm':
                        ffmpeg_cmd += ['-framerate', '1', '-loop', '1', '-i', ffmpeg_cover]
                        ffmpeg_cmd += ['-map', '0:a', '-map', '2:v']
                        ffmpeg_cmd += ['-c:v', 'libvpx-vp9', '-crf', '40', '-speed', '8', '-shortest']
                    elif session['output_format'] == 'ogg':
                        ffmpeg_cmd += ['-framerate', '1', '-loop', '1', '-i', ffmpeg_cover]
                        ffmpeg_cmd += ['-filter_complex', '[2:v:0][0:a:0]concat=n=1:v=1:a=1[outv][rawa];[rawa]loudnorm=I=-16:LRA=11:TP=-1.5,afftdn=nf=-70[outa]', '-map', '[outv]', '-map', '[outa]', '-shortest']
                    if ffmpeg_cover.endswith('.png'):
                        ffmpeg_cmd += ['-pix_fmt', 'yuv420p']
                else:
                    ffmpeg_cmd += ['-map', '0:a']
                if session['output_format'] == 'm4a' or session['output_format'] == 'm4b' or session['output_format'] == 'mp4':
                    ffmpeg_cmd += ['-c:a', 'aac', '-b:a', '128k', '-ar', '44100']
                    ffmpeg_cmd += ['-movflags', '+faststart']
                elif session['output_format'] == 'webm':
                    ffmpeg_cmd += ['-c:a', 'libopus', '-b:a', '64k']
                elif session['output_format'] == 'ogg':
                    ffmpeg_cmd += ['-c:a', 'libopus', '-b:a', '128k', '-compression_level', '0']
                elif session['output_format'] == 'flac':
                    ffmpeg_cmd += ['-c:a', 'flac', '-compression_level', '4']
                elif session['output_format'] == 'mp3':
                    ffmpeg_cmd += ['-c:a', 'libmp3lame', '-b:a', '128k', '-ar', '44100']
                if session['output_format'] != 'ogg':
                    ffmpeg_cmd += ['-af', 'loudnorm=I=-16:LRA=11:TP=-1.5,afftdn=nf=-70']
            ffmpeg_cmd += ['-strict', 'experimental', '-map_metadata', '1']
            ffmpeg_cmd += ['-threads', '8', '-y', ffmpeg_final_file]
            try:
                process = subprocess.Popen(
                    ffmpeg_cmd,
                    env={},
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    encoding='utf-8'
                )
                for line in process.stdout:
                    print(line, end='')  # Print each line of stdout
                process.wait()
                if process.returncode == 0:
                    return True
                else:
                    error = process.returncode
                    print(error, ffmpeg_cmd)
                    return False
            except subprocess.CalledProcessError as e:
                DependencyError(e)
                return False
 
        except Exception as e:
            DependencyError(e)
            return False
    try:
        chapter_files = [f for f in os.listdir(session['chapters_dir']) if f.endswith(f'.{default_audio_proc_format}')]
        chapter_files = sorted(chapter_files, key=lambda x: int(re.search(r'\d+', x).group()))
        if len(chapter_files) > 0:
            combined_chapters_file = os.path.join(session['process_dir'], get_sanitized(session['metadata']['title']) + '.' + default_audio_proc_format)
            metadata_file = os.path.join(session['process_dir'], 'metadata.txt')
            if assemble_segments():
                if generate_ffmpeg_metadata():
                    final_name = get_sanitized(session['metadata']['title'] + '.' + session['output_format'])
                    final_file = os.path.join(session['audiobooks_dir'], final_name)                       
                    if export_audio():
                        return final_file
        else:
            error = 'No block files exists!'
            print(error)
        return None
    except Exception as e:
        DependencyError(e)
        return False

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
        return f'{chapter_word.capitalize()} {integer_value}; '

    def replace_numeral_with_period(match):
        roman_numeral = match.group(1)
        integer_value = roman_to_int(roman_numeral)
        return f'{integer_value}. '

    text = roman_chapter_pattern.sub(replace_chapter_match, text)
    text = roman_numerals_with_period.sub(replace_numeral_with_period, text)
    return text

def delete_unused_tmp_dirs(web_dir, days, session):
    dir_array = [
        tmp_dir,
        web_dir,
        os.path.join(models_dir, '__sessions'),
        os.path.join(voices_dir, '__sessions')
    ]
    current_user_dirs = {
        f"ebook-{session['id']}",
        f"web-{session['id']}",
        f"voice-{session['id']}",
        f"model-{session['id']}"
    }
    current_time = time.time()
    threshold_time = current_time - (days * 24 * 60 * 60)  # Convert days to seconds
    for dir_path in dir_array:
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            continue  
        for dir in os.listdir(dir_path):
            if dir in current_user_dirs:
                continue           
            full_dir_path = os.path.join(dir_path, dir)  # Use a new variable
            if not os.path.isdir(full_dir_path):
                continue
            try:
                dir_mtime = os.path.getmtime(full_dir_path)
                dir_ctime = os.path.getctime(full_dir_path)
                if dir_mtime < threshold_time and dir_ctime < threshold_time:
                    shutil.rmtree(full_dir_path, ignore_errors=True)
                    print(f"Deleted expired session: {full_dir_path}")
            except Exception as e:
                print(f"Error deleting {full_dir_path}: {e}")

def compare_file_metadata(f1, f2):
    if os.path.getsize(f1) != os.path.getsize(f2):
        return False
    if os.path.getmtime(f1) != os.path.getmtime(f2):
        return False
    return True
    
def get_compatible_tts_engines(language):
    compatible_engines = [
        tts for tts in models.keys()
        #if language in language_tts.get(tts, {}) and tts != BARK
        if language in language_tts.get(tts, {})
    ]
    return compatible_engines

def convert_ebook_batch(args):
    if isinstance(args['ebook_list'], list):
        ebook_list = args['ebook_list'][:]
        for file in ebook_list: # Use a shallow copy
            if any(file.endswith(ext) for ext in ebook_formats):
                args['ebook'] = file
                print(f'Processing eBook file: {os.path.basename(file)}')
                progress_status, passed = convert_ebook(args)
                if passed is False:
                    print(f'Conversion failed: {progress_status}')
                    sys.exit(1)
                args['ebook_list'].remove(file) 
        reset_ebook_session(args['session'])
        return progress_status, passed
    else:
        print(f'the ebooks source is not a list!')
        sys.exit(1)       

def convert_ebook(args):
    try:
        global is_gui_process, context        
        error = None
        id = None
        info_session = None
        if args['language'] is not None:

            if not os.path.splitext(args['ebook'])[1]:
                error = 'The selected ebook file has no extension. Please select a valid file.'
                print(error)
                return error

            if not os.path.exists(args['ebook']):
                error = 'The ebook path you provided does not exist'
                print(error)
                return error

            try:
                if len(args['language']) == 2:
                    lang_array = languages.get(part1=args['language'])
                    if lang_array:
                        args['language'] = lang_array.part3
                        args['language_iso1'] = lang_array.part1
                elif len(args['language']) == 3:
                    lang_array = languages.get(part3=args['language'])
                    if lang_array:
                        args['language'] = lang_array.part3
                        args['language_iso1'] = lang_array.part1 
                else:
                    args['language_iso1'] = None
            except Exception as e:
                pass

            if args['language'] not in language_mapping.keys():
                error = 'The language you provided is not (yet) supported'
                print(error)
                return error

            is_gui_process = args['is_gui_process']
            id = args['session'] if args['session'] is not None else str(uuid.uuid4())
            session = context.get_session(id)
            session['script_mode'] = args['script_mode'] if args['script_mode'] is not None else NATIVE   
            session['ebook'] = args['ebook']
            session['ebook_list'] = args['ebook_list']
            session['device'] = args['device']
            session['language'] = args['language']
            session['language_iso1'] = args['language_iso1']
            session['tts_engine'] = args['tts_engine'] if args['tts_engine'] is not None else get_compatible_tts_engines(args['language'])[0]
            session['custom_model'] = args['custom_model'] if not is_gui_process or args['custom_model'] is None else os.path.join(session['custom_model_dir'], args['custom_model'])
            session['fine_tuned'] = args['fine_tuned']
            session['output_format'] = args['output_format']
            session['temperature'] =  args['temperature']
            session['length_penalty'] = args['length_penalty']
            session['num_beams'] = args['num_beams']
            session['repetition_penalty'] = args['repetition_penalty']
            session['top_k'] =  args['top_k']
            session['top_p'] = args['top_p']
            session['speed'] = args['speed']
            session['enable_text_splitting'] = args['enable_text_splitting']
            session['audiobooks_dir'] = args['audiobooks_dir']
            session['voice'] = args['voice']
            
            info_session = f"\n*********** Session: {id} **************\nStore it in case of interruption, crash, reuse of custom model or custom voice,\nyou can resume the conversion with --session option"

            if not is_gui_process:
                session['voice_dir'] = os.path.join(voices_dir, '__sessions',f"voice-{session['id']}")
                session['custom_model_dir'] = os.path.join(models_dir, '__sessions',f"model-{session['id']}")
                if session['custom_model'] is not None:
                    if not os.path.exists(session['custom_model_dir']):
                        os.makedirs(session['custom_model_dir'], exist_ok=True)
                    src_path = Path(session['custom_model'])
                    src_name = src_path.stem
                    if not os.path.exists(os.path.join(session['custom_model_dir'], src_name)):
                        required_files = models[session['tts_engine']]['internal']['files']
                        if analyze_uploaded_file(session['custom_model'], required_files):
                            model = extract_custom_model(session['custom_model'], session)
                            if model is not None:
                                session['custom_model'] = model
                            else:
                                error = f"{model} could not be extracted or mandatory files are missing"
                        else:
                            error = f'{os.path.basename(f)} is not a valid model or some required files are missing'
                if session['voice'] is not None:
                    os.makedirs(session['voice_dir'], exist_ok=True)
                    voice_name = get_sanitized(os.path.splitext(os.path.basename(session['voice']))[0])
                    final_voice_file = os.path.join(session['voice_dir'],f'{voice_name}_24000.wav')
                    if not os.path.exists(final_voice_file):
                        extractor = VoiceExtractor(session, models_dir, session['voice'], voice_name)
                        status, msg = extractor.extract_voice()
                        if status:
                            session['voice'] = final_voice_file
                        else:
                            error = 'extractor.extract_voice()() failed! Check if you audio file is compatible.'
                            print(error)
            if error is None:
                if session['script_mode'] == NATIVE:
                    bool, e = check_programs('Calibre', 'ebook-convert', '--version')
                    if not bool:
                        error = f'check_programs() Calibre failed: {e}'
                    bool, e = check_programs('FFmpeg', 'ffmpeg', '-version')
                    if not bool:
                        error = f'check_programs() FFMPEG failed: {e}'
                if error is None:
                    session['session_dir'] = os.path.join(tmp_dir, f"ebook-{session['id']}")
                    session['process_dir'] = os.path.join(session['session_dir'], f"{hashlib.md5(session['ebook'].encode()).hexdigest()}")
                    session['chapters_dir'] = os.path.join(session['process_dir'], "chapters")
                    session['chapters_dir_sentences'] = os.path.join(session['chapters_dir'], 'sentences')       
                    if prepare_dirs(args['ebook'], session):
                        session['filename_noext'] = os.path.splitext(os.path.basename(session['ebook']))[0]
                        if session['device'] == 'cuda':
                            session['device'] = session['device'] if torch.cuda.is_available() else 'cpu'
                            if session['device'] == 'cpu':
                                os.environ["SUNO_OFFLOAD_CPU"] = 'True'
                                msg = 'GPU is not available on your device!'
                                print(msg)
                        elif session['device'] == 'mps':
                            session['device'] = session['device'] if torch.backends.mps.is_available() else 'cpu'
                            if session['device'] == 'cpu':
                                os.environ["SUNO_OFFLOAD_CPU"] = 'True'
                                msg = 'MPS is not available on your device!'
                                print(msg)
                        else:
                            os.environ["SUNO_OFFLOAD_CPU"] = 'True'
                        if get_vram() <= 4:
                            os.environ["SUNO_USE_SMALL_MODELS"] = 'True'
                        msg = f"Available Processor Unit: {session['device']}"
                        print(msg)
                        if default_xtts_settings['use_deepspeed'] == True:
                            try:
                                import deepspeed
                            except:
                                default_xtts_settings['use_deepspeed'] = False
                                msg = 'deepseed not installed or package is broken. set to False'
                                print(msg)
                            else: 
                                msg = 'deepspeed is detected!'
                                print(msg)
                        session['epub_path'] = os.path.join(session['process_dir'], '__' + session['filename_noext'] + '.epub')
                        if convert_to_epub(session):
                            epubBook = epub.read_epub(session['epub_path'], {'ignore_ncx': True})       
                            metadata = dict(session['metadata'])
                            for key, value in metadata.items():
                                data = epubBook.get_metadata('DC', key)
                                if data:
                                    for value, attributes in data:
                                        metadata[key] = value
                            metadata['language'] = session['language']
                            metadata['title'] = os.path.splitext(os.path.basename(session['ebook']))[0].replace('_',' ') if not metadata['title'] else metadata['title']
                            metadata['creator'] =  False if not metadata['creator'] or metadata['creator'] == 'Unknown' else metadata['creator']
                            session['metadata'] = metadata
                            
                            try:
                                if len(session['metadata']['language']) == 2:
                                    lang_array = languages.get(part1=session['language'])
                                    if lang_array:
                                        session['metadata']['language'] = lang_array.part3     
                            except Exception as e:
                                pass
                           
                            if session['metadata']['language'] != session['language']:
                                error = f"WARNING!!! language selected {session['language']} differs from the EPUB file language {session['metadata']['language']}"
                                print(error)
                            session['cover'] = get_cover(epubBook, session)
                            if session['cover']:
                                session['toc'], session['chapters'] = get_chapters(epubBook, session)
                                if session['chapters'] is not None:
                                    if convert_chapters_to_audio(session):
                                        final_file = combine_audio_chapters(session)               
                                        if final_file is not None:
                                            chapters_dirs = [
                                                dir_name for dir_name in os.listdir(session['process_dir'])
                                                if fnmatch.fnmatch(dir_name, "chapters_*") and os.path.isdir(os.path.join(session['process_dir'], dir_name))
                                            ]
                                            shutil.rmtree(os.path.join(session['voice_dir'], 'proc'), ignore_errors=True)
                                            if is_gui_process:
                                                if len(chapters_dirs) > 1:
                                                    if os.path.exists(session['chapters_dir']):
                                                        shutil.rmtree(session['chapters_dir'], ignore_errors=True)
                                                    if os.path.exists(session['epub_path']):
                                                        os.remove(session['epub_path'])
                                                    if os.path.exists(session['cover']):
                                                        os.remove(session['cover'])
                                                else:
                                                    if os.path.exists(session['process_dir']):
                                                        shutil.rmtree(session['process_dir'], ignore_errors=True)
                                            else:
                                                if os.path.exists(session['voice_dir']):
                                                    if not any(os.scandir(session['voice_dir'])):
                                                        shutil.rmtree(session['voice_dir'], ignore_errors=True)
                                                if os.path.exists(session['custom_model_dir']):
                                                    if not any(os.scandir(session['custom_model_dir'])):
                                                        shutil.rmtree(session['custom_model_dir'], ignore_errors=True)
                                                if os.path.exists(session['session_dir']):
                                                    shutil.rmtree(session['session_dir'], ignore_errors=True)
                                            progress_status = f'Audiobook {os.path.basename(final_file)} created!'
                                            session['audiobook'] = final_file
                                            print(info_session)
                                            return progress_status, True
                                        else:
                                            error = 'combine_audio_chapters() error: final_file not created!'
                                    else:
                                        error = 'convert_chapters_to_audio() failed!'
                                else:
                                    error = 'get_chapters() failed!'
                            else:
                                error = 'get_cover() failed!'
                        else:
                            error = 'convert_to_epub() failed!'
                    else:
                        error = f"Temporary directory {session['process_dir']} not removed due to failure."
        else:
            error = f"Language {args['language']} is not supported."
        if session['cancellation_requested']:
            error = 'Cancelled'
        else:
            if not is_gui_process and id is not None:
                error += info_session
        print(error)
        return error, False
    except Exception as e:
        print(f'convert_ebook() Exception: {e}')
        return e, False

def restore_session_from_data(data, session):
    try:
        for key, value in data.items():
            if key in session:  # Check if the key exists in session
                if isinstance(value, dict) and isinstance(session[key], dict):
                    restore_session_from_data(value, session[key])
                else:
                    session[key] = value
    except Exception as e:
        alert_exception(e)

def reset_ebook_session(id):
    session = context.get_session(id)
    data = {
        "ebook": None,
        "chapters_dir": None,
        "chapters_dir_sentences": None,
        "epub_path": None,
        "filename_noext": None,
        "chapters": None,
        "cover": None,
        "status": None,
        "progress": 0,
        "time": None,
        "cancellation_requested": False,
        "event": None,
        "metadata": {
            "title": None, 
            "creator": None,
            "contributor": None,
            "language": None,
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
            "Modified": None
        }
    }
    restore_session_from_data(data, session)

def get_all_ip_addresses():
    ip_addresses = []
    for interface, addresses in psutil.net_if_addrs().items():
        for address in addresses:
            if address.family == socket.AF_INET:
                ip_addresses.append(address.address)
            elif address.family == socket.AF_INET6:
                ip_addresses.append(address.address)  
    return ip_addresses

def web_interface(args):
    script_mode = args['script_mode']
    is_gui_process = args['is_gui_process']
    is_gui_shared = args['share']
    ebook_src = None
    language_options = [
        (
            f"{details['name']} - {details['native_name']}" if details['name'] != details['native_name'] else details['name'],
            lang
        )
        for lang, details in language_mapping.items()
    ]
    voice_options = []
    tts_engine_options = []
    custom_model_options = []
    fine_tuned_options = []
    audiobook_options = []
    
    src_label_file = 'Select a File'
    src_label_dir = 'Select a Directory'
    
    visible_gr_tab_preferences = interface_component_options['gr_tab_preferences']
    visible_gr_group_custom_model = interface_component_options['gr_group_custom_model']
    visible_gr_group_voice_file = interface_component_options['gr_group_voice_file']
    
    # Buffer for real-time log streaming
    log_buffer = Queue()
    
    # Event to signal when the process should stop
    thread = None
    stop_event = threading.Event()

    theme = gr.themes.Origin(
        primary_hue='amber',
        secondary_hue='green',
        neutral_hue='gray',
        radius_size='lg',
        font_mono=['JetBrains Mono', 'monospace', 'Consolas', 'Menlo', 'Liberation Mono']
    )
    """
    def process_cleanup(state):
        try:
            print('***************PROCESS CLEANING REQUESTED*****************')
            if state['id'] in context.sessions:
                del context.sessions[state['id']]
        except Exception as e:
            error = f'process_cleanup(): {e}'
            alert_exception(error)
    """
    with gr.Blocks(theme=theme, delete_cache=(86400, 86400)) as interface:
        main_html = gr.HTML(
            '''
            <style>
                /* Global Scrollbar Customization */
                /* The entire scrollbar */
                ::-webkit-scrollbar {
                    width: 6px !important;
                    height: 6px !important;
                    cursor: pointer !important;;
                }
                /* The scrollbar track (background) */
                ::-webkit-scrollbar-track {
                    background: none transparent !important;
                    border-radius: 6px !important;
                }
                /* The scrollbar thumb (scroll handle) */
                ::-webkit-scrollbar-thumb {
                    background: #c09340 !important;
                    border-radius: 6px !important;
                }
                /* The scrollbar thumb on hover */
                ::-webkit-scrollbar-thumb:hover {
                    background: #ff8c00 !important;
                }
                /* Firefox scrollbar styling */
                html {
                    scrollbar-width: thin !important;
                    scrollbar-color: #c09340 none !important;
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
                .icon-btn {
                    font-size: 30px !important;
                }
                .small-btn {
                    font-size: 22px !important;
                    width: 60px !important;
                    height: 60px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                .file-preview-holder {
                    height: 116px !important;
                    overflow: auto !important;
                }
                #component-8, #component-31, #component-15 {
                    height: 140px !important;
                }
                #component-31 [aria-label="Clear"], #component-15 [aria-label="Clear"] {
                    display: none !important;
                }               
                #component-27, #component-28 {
                    height: 95px !important;
                }
                #component-56 {
                    height: 80px !important;
                }
                #component-64 {
                    height: 60px !important;
                }
                #component-9 span[data-testid="block-info"], #component-14 span[data-testid="block-info"],
                #component-33 span[data-testid="block-info"], #component-61 span[data-testid="block-info"] {
                    display: none !important;
                }
                #voice_player {
                    display: block !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    width: 60px !important;
                    height: 60px !important;
                }
                #voice_player :is(#waveform, .rewind, .skip, .playback, label, .volume, .empty) {
                    display: none !important;
                }
                #voice_player .controls {
                    display: block !important;
                    position: absolute !important;
                    left: 15px !important;
                    top: 0 !important;
                }
                #audiobook_player :is(.volume, .empty, .source-selection, .control-wrapper, .settings-wrapper) {
                    display: none !important;
                }
            </style>
            <script>
            setInterval(() => {
                const data = window.localStorage.getItem('data');
                if(data){
                    const obj = JSON.parse(data);
                    if(typeof(obj.id) != 'undefined'){
                        if(obj.id != null && obj.id != ""){
                            fetch('/api/heartbeat', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ 'id': obj.id })
                            });
                        }
                    }
                }
            }, 5000);
            </script>
            '''
        )
        main_markdown = gr.Markdown(
            f'''
            <h1 style="line-height: 0.7">Ebook2Audiobook v{prog_version}</h1>
            <a href="https://github.com/DrewThomasson/ebook2audiobook" target="_blank" style="line-height:0">https://github.com/DrewThomasson/ebook2audiobook</a>
            <div style="line-height: 1.3;">
                Multiuser, multiprocessing tasks on a geo cluster to share the conversion to the Grid<br/>
                Convert eBooks into immersive audiobooks with realistic TTS model voices.<br/>
            </div>
            '''
        )
        with gr.Tabs():
            gr_tab_main = gr.TabItem('Main Parameters')
            
            with gr_tab_main:
                with gr.Row():
                    with gr.Column(scale=3):
                        with gr.Group():
                            gr_ebook_file = gr.File(label=src_label_file, file_types=ebook_formats, file_count='single', allow_reordering=True, height=140)
                            gr_ebook_mode = gr.Radio(label='', choices=[('File','single'), ('Directory','directory')], value='single', interactive=True)
                        with gr.Group():
                            gr_language = gr.Dropdown(label='Language', choices=language_options, value=default_language_code, type='value', interactive=True)
                        gr_group_voice_file = gr.Group(visible=visible_gr_group_voice_file)
                        with gr_group_voice_file:
                            gr_voice_file = gr.File(label='*Cloning Voice Audio Fiie', file_types=voice_formats, value=None, height=140)
                            with gr.Row():
                                gr_voice_player = gr.Audio(elem_id='voice_player', type='filepath', interactive=False, show_download_button=False, container=False, visible=False, show_share_button=False, show_label=False, waveform_options=gr.WaveformOptions(show_controls=False), scale=0, min_width=60)
                                gr_voice_list = gr.Dropdown(label='', choices=voice_options, type='value', interactive=True, scale=2)
                                gr_voice_del_btn = gr.Button('🗑', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                            gr.Markdown('<p>&nbsp;&nbsp;* Optional</p>')
                        with gr.Group():
                            gr_device = gr.Radio(label='Processor Unit', choices=[('CPU','cpu'), ('GPU','cuda'), ('MPS','mps')], value=default_device)
                    with gr.Column(scale=3):
                        with gr.Group():
                            gr_tts_engine_list = gr.Dropdown(label='TTS Base', choices=tts_engine_options, type='value', interactive=True)
                            gr_fine_tuned_list = gr.Dropdown(label='Fine Tuned Models', choices=fine_tuned_options, type='value', interactive=True)
                        gr_group_custom_model = gr.Group(visible=visible_gr_group_custom_model)
                        with gr_group_custom_model:
                            gr_custom_model_file = gr.File(label=f"*Custom Model Zip File", value=None, file_types=['.zip'], height=140)
                            with gr.Row():
                                gr_custom_model_list = gr.Dropdown(label='', choices=custom_model_options, type='value', interactive=True, scale=2)
                                gr_custom_model_del_btn = gr.Button('🗑', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                            gr.Markdown('<p>&nbsp;&nbsp;* Optional</p>')
                        with gr.Group():
                            gr_session = gr.Textbox(label='Session', interactive=False)
                        gr_output_format_list = gr.Dropdown(label='Output format', choices=output_formats, type='value', value=default_output_format, interactive=True)
            gr_tab_preferences = gr.TabItem('Fine Tuned Parameters', visible=visible_gr_tab_preferences)
            
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
                    value=float(default_xtts_settings['temperature']),
                    info='Higher values lead to more creative, unpredictable outputs. Lower values make it more monotone.'
                )
                gr_length_penalty = gr.Slider(
                    label='Length Penalty', 
                    minimum=0.3, 
                    maximum=5.0, 
                    step=0.1,
                    value=float(default_xtts_settings['length_penalty']),
                    info='Adjusts how much longer sequences are preferred. Higher values encourage the model to produce longer and more natural speech.',
                    visible=False
                )
                gr_num_beams = gr.Slider(
                    label='Number Beams', 
                    minimum=1, 
                    maximum=10, 
                    step=1, 
                    value=int(default_xtts_settings['num_beams']),
                    info='Controls how many alternative sequences the model explores. Higher values improve speech coherence and pronunciation but increase inference time.',
                    visible=False
                )
                gr_repetition_penalty = gr.Slider(
                    label='Repetition Penalty', 
                    minimum=1.0, 
                    maximum=10.0, 
                    step=0.1, 
                    value=float(default_xtts_settings['repetition_penalty']), 
                    info='Penalizes repeated phrases. Higher values reduce repetition.'
                )
                gr_top_k = gr.Slider(
                    label='Top-k Sampling', 
                    minimum=10, 
                    maximum=100, 
                    step=1, 
                    value=int(default_xtts_settings['top_k']), 
                    info='Lower values restrict outputs to more likely words and increase speed at which audio generates.'
                )
                gr_top_p = gr.Slider(
                    label='Top-p Sampling', 
                    minimum=0.1, 
                    maximum=1.0, 
                    step=0.01, 
                    value=float(default_xtts_settings['top_p']), 
                    info='Controls cumulative probability for word selection. Lower values make the output more predictable and increase speed at which audio generates.'
                )
                gr_speed = gr.Slider(
                    label='Speed', 
                    minimum=0.5, 
                    maximum=3.0, 
                    step=0.1, 
                    value=float(default_xtts_settings['speed']), 
                    info='Adjusts how fast the narrator will speak.'
                )
                gr_enable_text_splitting = gr.Checkbox(
                    label='Enable Text Splitting', 
                    value=default_xtts_settings['enable_text_splitting'],
                    info='Coqui-tts builtin text splitting. Can help against hallucinations bu can also be worse.',
                    visible=False
                )
    
        gr_state = gr.State(value={"hash": None})
        gr_state_alert = gr.State(value={"type": None,"msg": None})
        gr_read_data = gr.JSON(visible=False)
        gr_write_data = gr.JSON(visible=False)
        gr_conversion_progress = gr.Textbox(label='Progress')
        gr_group_audiobook_list = gr.Group(visible=False)
        with gr_group_audiobook_list:
            gr_audiobook_player = gr.Audio(label='Audiobook', elem_id='audiobook_player', type='filepath', show_download_button=False, show_share_button=False, container=True, interactive=False, visible=True)
            with gr.Row():
                gr_audiobook_download_btn = gr.DownloadButton('↧', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=True, scale=0, min_width=60)
                gr_audiobook_list = gr.Dropdown(label='', choices=audiobook_options, type='value', interactive=True, scale=2)
                gr_audiobook_del_btn = gr.Button('🗑', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=True, scale=0, min_width=60)
        gr_convert_btn = gr.Button('📚', elem_classes='icon-btn', variant='primary', interactive=False)
        
        gr_modal = gr.HTML(visible=False)
        gr_confirm_field_hidden = gr.Textbox(elem_id='confirm_hidden', visible=False)
        gr_confirm_yes_btn_hidden = gr.Button('', elem_id='confirm_yes_btn_hidden', visible=False)
        gr_confirm_no_btn_hidden = gr.Button('', elem_id='confirm_no_btn_hidden', visible=False)

        def show_alert(state):
            if isinstance(state, dict):
                if state['type'] is not None:
                    if state['type'] == 'error':
                        gr.Error(state['msg'])
                    elif state['type'] == 'warning':
                        gr.Warning(state['msg'])
                    elif state['type'] == 'info':
                        gr.Info(state['msg'])
                    elif state['type'] == 'success':
                        gr.Success(state['msg'])

        def show_modal(type, msg):
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
                .confirm-buttons {{
                    display: flex;
                    justify-content: space-evenly;
                    margin-top: 20px;
                }}
                .confirm-buttons button {{
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                    font-weight: bold;
                }}
                .confirm-buttons .confirm_yes_btn {{
                    background-color: #28a745;
                    color: white;
                }}
                .confirm-buttons .confirm_no_btn {{
                    background-color: #dc3545;
                    color: white;
                }}
                .confirm-buttons .confirm_yes_btn:hover {{
                    background-color: #34d058;
                }}
                .confirm-buttons .confirm_no_btn:hover {{
                    background-color: #ff6f71;
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
                    <p style="color:#ffffff">{msg}</p>            
                    {show_confirm() if type == 'confirm' else '<div class="spinner"></div>'}
                </div>
            </div>
            '''
          
        def show_confirm():
            return '''
            <div class="confirm-buttons">
                <button class="confirm_yes_btn" onclick="document.querySelector('#confirm_yes_btn_hidden').click()">✔</button>
                <button class="confirm_no_btn" onclick="document.querySelector('#confirm_no_btn_hidden').click()">⨉</button>
            </div>
            '''

        def alert_exception(error):
            gr.Error(error)
            DependencyError(error)

        def restore_interface(id):
            session = context.get_session(id)              
            ebook_data = None
            file_count = session['ebook_mode']
            if isinstance(session['ebook_list'], list) and file_count == 'directory':
                #ebook_data = session['ebook_list']
                ebook_data = None
            elif isinstance(session['ebook'], str) and file_count == 'single':
                ebook_data = session['ebook']
            else:
                ebook_data = None
            session['temperature'] = default_xtts_settings['temperature']
            session['length_penalty'] = default_xtts_settings['length_penalty']
            session['num_beams'] = default_xtts_settings['num_beams']
            session['repetition_penalty'] = default_xtts_settings['repetition_penalty']
            session['top_k'] = default_xtts_settings['top_k']
            session['top_p'] = default_xtts_settings['top_p']
            session['speed'] = default_xtts_settings['speed']
            session['enable_text_splitting'] = default_xtts_settings['enable_text_splitting']
            return (
                gr.update(value=ebook_data), gr.update(value=session['ebook_mode']), gr.update(value=session['device']),
                gr.update(value=session['language']), update_gr_voice_list(id), update_gr_tts_engine_list(id), update_gr_custom_model_list(id),
                update_gr_fine_tuned_list(id), gr.update(value=session['output_format']), update_gr_audiobook_list(id),
                gr.update(value=float(session['temperature'])), gr.update(value=float(session['length_penalty'])), gr.update(value=int(session['num_beams'])),
                gr.update(value=float(session['repetition_penalty'])), gr.update(value=int(session['top_k'])), gr.update(value=float(session['top_p'])), gr.update(value=float(session['speed'])), 
                gr.update(value=bool(session['enable_text_splitting'])), gr.update(active=True)
            )

        def refresh_interface(id):
            session = context.get_session(id)
            session['status'] = None
            return gr.update(interactive=False), gr.update(value=None), update_gr_audiobook_list(id), gr.update(value=session['audiobook']), gr.update(visible=False)

        def change_gr_audiobook_list(selected, id):
            session = context.get_session(id)
            session['audiobook'] = selected
            visible = True if len(audiobook_options) else False
            return gr.update(value=selected), gr.update(value=selected), gr.update(visible=visible)

        def update_convert_btn(upload_file=None, upload_file_mode=None, custom_model_file=None, session=None):
            try:
                if session is None:
                    return gr.update(variant='primary', interactive=False)
                else:
                    if hasattr(upload_file, 'name') and not hasattr(custom_model_file, 'name'):
                        return gr.update(variant='primary', interactive=True)
                    elif isinstance(upload_file, list) and len(upload_file) > 0 and upload_file_mode == 'directory' and not hasattr(custom_model_file, 'name'):
                        return gr.update(variant='primary', interactive=True)
                    else:
                        return gr.update(variant='primary', interactive=False)
            except Exception as e:
                error = f'update_convert_btn(): {e}'
                alert_exception(error)               

        def change_gr_ebook_file(data, id):
            try:
                session = context.get_session(id)
                session['ebook'] = None
                session['ebook_list'] = None
                if data is None:
                    if session['status'] == 'converting':
                        session['cancellation_requested'] = True
                        msg = 'Cancellation requested, please wait...'
                        yield gr.update(value=show_modal('wait', msg),visible=True)
                        return
                if isinstance(data, list):
                    session['ebook_list'] = data
                else:
                    session['ebook'] = data
                session['cancellation_requested'] = False
            except Exception as e:
                error = f'change_gr_ebook_file(): {e}'
                alert_exception(error)
            return gr.update(visible=False)
            
        def change_gr_ebook_mode(val, id):
            session = context.get_session(id)
            session['ebook_mode'] = val
            if val == 'single':
                return gr.update(label=src_label_file, value=None, file_count='single')
            else:
                return gr.update(label=src_label_dir, value=None, file_count='directory')

        def change_gr_voice_file(f, id):
            if f is not None:
                state = {}
                if len(voice_options) > max_custom_voices:
                    error = f'You are allowed to upload a max of {max_custom_voices} voices'
                    state['type'] = 'warning'
                    state['msg'] = error
                elif os.path.splitext(f.name)[1] not in voice_formats:
                    error = f'The audio file format selected is not valid.'
                    state['type'] = 'warning'
                    state['msg'] = error
                else:                  
                    session = context.get_session(id)
                    voice_name = os.path.splitext(os.path.basename(f))[0].replace('&', 'And')
                    voice_name = get_sanitized(voice_name)
                    final_voice_file = os.path.join(session['voice_dir'],f'{voice_name}_24000.wav')
                    extractor = VoiceExtractor(session, models_dir, f, voice_name)
                    status, msg = extractor.extract_voice()
                    if status:
                        session['voice'] = final_voice_file
                        msg = f"Voice {voice_name} added to the voices list"
                        state['type'] = 'success'
                        state['msg'] = msg
                    else:
                        error = 'failed! Check if you audio file is compatible.'
                        state['type'] = 'warning'
                        state['msg'] = error
                show_alert(state)
                return gr.update(value=None)
            return gr.update()

        def change_gr_voice_list(selected, id):
            session = context.get_session(id)
            session['voice'] = next((value for label, value in voice_options if value == selected), None)
            visible = True if session['voice'] is not None else False
            min_width = 60 if session['voice'] is not None else 0
            return gr.update(value=session['voice'], visible=visible, min_width=min_width), gr.update(visible=visible)

        def click_gr_voice_del_btn(selected, id):          
            try:
                if selected is not None:
                    voice_name = re.sub(r'_(24000|16000)\.wav$', '', os.path.basename(selected))
                    if voice_name in default_xtts_settings['voices'].keys() or voice_name in default_yourtts_settings['voices'].keys():
                        error = f'Voice file {voice_name} is a builtin voice and cannot be deleted.'
                        show_alert({"type": "warning", "msg": error})
                    else:                   
                        try:
                            session = context.get_session(id)
                            if selected.find(session['voice_dir']) > -1:
                                msg = f'Are you sure to delete {voice_name}...'
                                return gr.update(value='confirm_voice_del'), gr.update(value=show_modal('confirm', msg),visible=True)
                            else:
                                error = f'{voice_name} is part of the global voices directory. Only your own custom uploaded voices can be deleted!'
                                show_alert({"type": "warning", "msg": error})
                        except Exception as e:
                            error = f'Could not delete the voice file {voice_name}!'
                            alert_exception(error)
                return gr.update(), gr.update(visible=False)
            except Exception as e:
                error = f'click_gr_voice_del_btn(): {e}'
                alert_exception(error)
            return gr.update(), gr.update(visible=False)

        def click_gr_custom_model_del_btn(selected, id):
            try:
                if selected is not None:
                    session = context.get_session(id)
                    selected_name = os.path.basename(selected)
                    msg = f'Are you sure to delete {selected_name}...'
                    return gr.update(value='confirm_custom_model_del'), gr.update(value=show_modal('confirm', msg),visible=True)
            except Exception as e:
                error = f'Could not delete the custom model {selected_name}!'
                alert_exception(error)
            return gr.update(), gr.update(visible=False)

        def click_gr_audiobook_del_btn(selected, id):
            try:
                if selected is not None:
                    session = context.get_session(id)
                    selected_name = os.path.basename(selected)
                    msg = f'Are you sure to delete {selected_name}...'
                    return gr.update(value='confirm_audiobook_del'), gr.update(value=show_modal('confirm', msg),visible=True)
            except Exception as e:
                error = f'Could not delete the audiobook {selected_name}!'
                alert_exception(error)
            return gr.update(), gr.update(visible=False)

        def confirm_deletion(voice, custom_model, audiobook, id, method=None):
            try:
                if method is not None:
                    session = context.get_session(id)
                    if method == 'confirm_voice_del':
                        selected_name = os.path.basename(voice)
                        pattern = re.sub(r'_(24000|16000)\.wav$', '_*.wav', voice)
                        files_to_remove = glob(pattern)
                        for file in files_to_remove:
                            os.remove(file)                           
                        msg = f'Voice file {re.sub(r'_(24000|16000)\.wav$', '', selected_name)} deleted!'
                        session['voice'] = None
                        show_alert({"type": "warning", "msg": msg})
                        return update_gr_voice_list(id), gr.update(), gr.update(), gr.update(visible=False)
                    elif method == 'confirm_custom_model_del':
                        selected_name = os.path.basename(custom_model)
                        shutil.rmtree(custom_model, ignore_errors=True)                           
                        msg = f'Custom model {selected_name} deleted!'
                        session['custom_model'] = None
                        show_alert({"type": "warning", "msg": msg})
                        return gr.update(), update_gr_custom_model_list(id), gr.update(), gr.update(visible=False)
                    elif method == 'confirm_audiobook_del':
                        selected_name = os.path.basename(audiobook)
                        if os.path.isdir(audiobook):
                            shutil.rmtree(selected, ignore_errors=True)
                        elif os.path.exists(audiobook):
                            os.remove(audiobook)
                        msg = f'Audiobook {selected_name} deleted!'
                        session['audiobook'] = None
                        show_alert({"type": "warning", "msg": msg})
                        return gr.update(), gr.update(), update_gr_audiobook_list(id), gr.update(visible=False)
            except Exception as e:
                error = f'confirm_deletion(): {e}!'
                alert_exception(error)
            return gr.update(), gr.update(), gr.update(), gr.update(visible=False)
                
        def prepare_audiobook_download(selected):
            if os.path.exists(selected):
                return selected
            return None           

        def update_gr_voice_list(id):
            try:
                nonlocal voice_options
                session = context.get_session(id)
                voice_lang_dir = session['language'] if session['language'] != 'con' else 'con-'  # Bypass Windows CON reserved name
                voice_lang_eng_dir = 'eng'
                voice_file_pattern = "*_24000.wav"
                voice_builtin_options = [
                    (os.path.splitext(re.sub(r'_24000\.wav$', '', f.name))[0], str(f))
                    for f in Path(os.path.join(voices_dir, voice_lang_dir)).rglob(voice_file_pattern)
                ]
                if session['language'] in language_tts[XTTSv2]:
                    voice_eng_options = [
                        (os.path.splitext(re.sub(r'_24000\.wav$', '', f.name))[0], str(f))
                        for f in Path(os.path.join(voices_dir, voice_lang_eng_dir)).rglob(voice_file_pattern)
                    ]
                else:
                    voice_eng_options = []
                voice_keys = {key for key, _ in voice_builtin_options}
                voice_options = voice_builtin_options + [row for row in voice_eng_options if row[0] not in voice_keys]
                voice_options += [
                    (os.path.splitext(re.sub(r'_24000\.wav$', '', f.name))[0], str(f))
                    for f in Path(session['voice_dir']).rglob(voice_file_pattern)
                ]
                voice_options = [('None', None)] + sorted(voice_options, key=lambda x: x[0].lower())
                session['voice'] = session['voice'] if session['voice'] in [option[1] for option in voice_options] else voice_options[0][1]
                return gr.update(choices=voice_options, value=session['voice'])
            except Exception as e:
                error = f'update_gr_voice_list(): {e}!'
                alert_exception(error)              
                return gr.update()

        def update_gr_tts_engine_list(id):
            try:
                nonlocal tts_engine_options
                session = context.get_session(id)
                tts_engine_options = get_compatible_tts_engines(session['language'])
                session['tts_engine'] = session['tts_engine'] if session['tts_engine'] in tts_engine_options else tts_engine_options[0]
                return gr.update(choices=tts_engine_options, value=session['tts_engine'])
            except Exception as e:
                error = f'update_gr_tts_engine_list(): {e}!'
                alert_exception(error)              
                return gr.update()

        def update_gr_custom_model_list(id):
            try:
                nonlocal custom_model_options
                session = context.get_session(id)
                custom_model_tts_dir = check_custom_model_tts(session['custom_model_dir'], session['tts_engine'])
                custom_model_options = [('None', None)] + [
                    (os.path.basename(os.path.join(custom_model_tts_dir, dir)), os.path.join(custom_model_tts_dir, dir))
                    for dir in os.listdir(custom_model_tts_dir)
                    if os.path.isdir(os.path.join(custom_model_tts_dir, dir))
                ]
                session['custom_model'] = session['custom_model'] if session['custom_model'] in [option[1] for option in custom_model_options] else custom_model_options[0][1]
                return gr.update(choices=custom_model_options, value=session['custom_model'])
            except Exception as e:
                error = f'update_gr_custom_model_list(): {e}!'
                alert_exception(error)              
                return gr.update()

        def update_gr_fine_tuned_list(id):
            try:
                nonlocal fine_tuned_options
                session = context.get_session(id)
                fine_tuned_options = [
                    name for name, details in models.get(session['tts_engine'],{}).items()
                    if details.get('lang') == 'multi' or details.get('lang') == session['language']
                ]
                session['fine_tuned'] = session['fine_tuned'] if session['fine_tuned'] in fine_tuned_options else default_fine_tuned
                return gr.update(choices=fine_tuned_options, value=session['fine_tuned'])
            except Exception as e:
                error = f'update_gr_fine_tuned_list(): {e}!'
                alert_exception(error)              
                return gr.update()

        def change_gr_device(device, id):
            session = context.get_session(id)
            session['device'] = device

        def change_gr_language(selected, id):
            session = context.get_session(id)
            if selected == 'zzz':
                new_language_code = default_language_code
            else:
                new_language_code = selected
            session['language'] = new_language_code
            return[
                gr.update(value=session['language']),
                update_gr_voice_list(id),
                update_gr_tts_engine_list(id),
                update_gr_custom_model_list(id),
                update_gr_fine_tuned_list(id)
            ]

        def check_custom_model_tts(custom_model_dir, tts_engine):
            dir_path = os.path.join(custom_model_dir, tts_engine)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            return dir_path

        def change_gr_custom_model_file(f, t, id):
            if f is not None:
                state = {}
                try:
                    if len(custom_model_options) > max_custom_model:
                        error = f'You are allowed to upload a max of {max_custom_models} models'   
                        state['type'] = 'warning'
                        state['msg'] = error
                    else:
                        session = context.get_session(id)
                        session['tts_engine'] = t
                        required_files = models[session['tts_engine']]['internal']['files']
                        if analyze_uploaded_file(f, required_files):
                            model = extract_custom_model(f, session)
                            if model is None:
                                error = f'Cannot extract custom model zip file {os.path.basename(f)}'
                                state['type'] = 'warning'
                                state['msg'] = error
                            else:
                                session['custom_model'] = model
                                msg = f'{os.path.basename(model)} added to the custom models list'
                                state['type'] = 'success'
                                state['msg'] = msg
                        else:
                            error = f'{os.path.basename(f)} is not a valid model or some required files are missing'
                            state['type'] = 'warning'
                            state['msg'] = error
                except ClientDisconnect:
                    error = 'Client disconnected during upload. Operation aborted.'
                    state['type'] = 'error'
                    state['msg'] = error
                except Exception as e:
                    error = f'change_gr_custom_model_file() exception: {str(e)}'
                    state['type'] = 'error'
                    state['msg'] = error
                show_alert(state)
                return gr.update(value=None)
            return gr.update()

        def change_gr_tts_engine_list(engine, id):
            session = context.get_session(id)
            session['tts_engine'] = engine
            if session['tts_engine'] == XTTSv2:
                visible = True
                if session['fine_tuned'] != 'internal':
                    visible = False
                return gr.update(visible=visible_gr_tab_preferences), gr.update(visible=visible), update_gr_fine_tuned_list(id), gr.update(label=f"*Custom Model Zip File (Mandatory files {models[session['tts_engine']][default_fine_tuned]['files']})")
            else:
                return gr.update(visible=False), gr.update(visible=False), update_gr_fine_tuned_list(id), gr.update(label=f"*Custom Model Zip File (Mandatory files {models[session['tts_engine']][default_fine_tuned]['files']})")
                
        def change_gr_fine_tuned_list(selected, id):
            session = context.get_session(id)
            visible = False
            if session['tts_engine'] == XTTSv2:
                if selected == 'internal':
                    visible = visible_gr_group_custom_model
            session['fine_tuned'] = selected
            return gr.update(visible=visible)

        def change_gr_custom_model_list(selected, id):
            session = context.get_session(id)
            session['custom_model'] = next((value for label, value in custom_model_options if value == selected), None)
            visible = True if session['custom_model'] is not None else False
            return gr.update(visible=not visible), gr.update(visible=visible)
        
        def change_gr_output_format_list(val, id):
            session = context.get_session(id)
            session['output_format'] = val
            return

        def change_param(key, val, id, val2=None):
            session = context.get_session(id)
            session[key] = val
            state = {}
            if key == 'length_penalty':
                if val2 is not None:
                    if float(val) > float(val2):
                        error = 'Length penalty must be always lower than num beams if greater than 1.0 or equal if 1.0'   
                        state['type'] = 'warning'
                        state['msg'] = error
                        show_alert(state)
            elif key == 'num_beams':
                if val2 is not None:
                    if float(val) < float(val2):
                        error = 'Num beams must be always higher than length penalty or equal if its value is 1.0'   
                        state['type'] = 'warning'
                        state['msg'] = error
                        show_alert(state)
            return

        def submit_convert_btn(id, device, ebook_file, tts_engine, voice, language, custom_model, fine_tuned, output_format, temperature, length_penalty, num_beams, repetition_penalty, top_k, top_p, speed, enable_text_splitting):
            try:
                session = context.get_session(id)
                args = {
                    "is_gui_process": is_gui_process,
                    "session": id,
                    "script_mode": script_mode,
                    "device": device.lower(),
                    "tts_engine": tts_engine,
                    "ebook": ebook_file if isinstance(ebook_file, str) else None,
                    "ebook_list": ebook_file if isinstance(ebook_file, list) else None,
                    "audiobooks_dir": session['audiobooks_dir'],
                    "voice": voice,
                    "language": language,
                    "custom_model": custom_model,
                    "output_format": output_format,
                    "temperature": float(temperature),
                    "length_penalty": float(length_penalty),
                    "num_beams": int(num_beams),
                    "repetition_penalty": float(repetition_penalty),
                    "top_k": int(top_k),
                    "top_p": float(top_p),
                    "speed": float(speed),
                    "enable_text_splitting": enable_text_splitting,
                    "fine_tuned": fine_tuned
                }
                error = None
                if args["ebook"] is None and args['ebook_list'] is None:
                    error = 'Error: a file or directory is required.'
                    show_alert({"type": "warning", "msg": error})
                elif args['num_beams'] < args['length_penalty']:
                    error = 'Error: num beams must be greater or equal than length penalty.'
                    show_alert({"type": "warning", "msg": error})                   
                else:
                    session['status'] = 'converting'
                    session['progress'] = len(audiobook_options)
                    if isinstance(args['ebook_list'], list):
                        ebook_list = args['ebook_list'][:]
                        for file in ebook_list:
                            if any(file.endswith(ext) for ext in ebook_formats):
                                print(f'Processing eBook file: {os.path.basename(file)}')
                                args['ebook'] = file
                                progress_status, passed = convert_ebook(args)
                                if passed is False:
                                    if session['status'] == 'converting':
                                        error = 'Conversion cancelled.'
                                        session['status'] = None
                                        break
                                    else:
                                        error = 'Conversion failed.'
                                        session['status'] = None
                                        break
                                else:
                                    show_alert({"type": "success", "msg": progress_status})
                                    args['ebook_list'].remove(file)
                                    reset_ebook_session(args['session'])
                                    count_file = len(args['ebook_list'])
                                    if count_file > 0:
                                        msg = f"{len(args['ebook_list'])} remaining..."
                                    else: 
                                        msg = 'Conversion successful!'
                                    yield gr.update(value=msg)
                        session['status'] = None
                    else:
                        print(f"Processing eBook file: {os.path.basename(args['ebook'])}")
                        progress_status, passed = convert_ebook(args)
                        if passed is False:
                            if session['status'] == 'converting':
                                session['status'] = None
                                error = 'Conversion cancelled.'
                            else:
                                session['status'] = None
                                error = 'Conversion failed.'
                        else:
                            show_alert({"type": "success", "msg": progress_status})
                            reset_ebook_session(args['session'])
                            msg = 'Conversion successful!'
                            return gr.update(value=msg)
                if error is not None:
                    show_alert({"type": "warning", "msg": error})
            except Exception as e:
                error = f'submit_convert_btn(): {e}'
                alert_exception(error)
            return gr.update(value='')

        def update_gr_audiobook_list(id):
            try:
                nonlocal audiobook_options
                session = context.get_session(id)
                audiobook_options = [
                    (f, os.path.join(session['audiobooks_dir'], str(f)))
                    for f in os.listdir(session['audiobooks_dir'])
                ]
                audiobook_options.sort(
                    key=lambda x: os.path.getmtime(x[1]),
                    reverse=True
                )
                session['audiobook'] = session['audiobook'] if session['audiobook'] in [option[1] for option in audiobook_options] else None
                if len(audiobook_options) > 0:
                    if session['audiobook'] is not None:
                        return gr.update(choices=audiobook_options, value=session['audiobook'])
                    else:
                        return gr.update(choices=audiobook_options, value=audiobook_options[0][1])
                gr.update(choices=audiobook_options)
            except Exception as e:
                error = f'update_gr_audiobook_list(): {e}!'
                alert_exception(error)              
                return gr.update()

        def change_gr_read_data(data, state):
            msg = 'Error while loading saved session. Please try to delete your cookies and refresh the page'
            try:
                if data is None:
                    session = context.get_session(str(uuid.uuid4()))
                else:
                    try:
                        if 'id' not in data:
                            data['id'] = str(uuid.uuid4())
                        session = context.get_session(data['id'])
                        restore_session_from_data(data, session)
                        session['cancellation_requested'] = False
                        if isinstance(session['ebook'], str):
                            if not os.path.exists(session['ebook']):
                                session['ebook'] = None
                        if session['voice'] is not None:
                            if not os.path.exists(session['voice']):
                                session['voice'] = None
                        if session['custom_model'] is not None:
                            if not os.path.exists(session['custom_model_dir']):
                                session['custom_model'] = None 
                        if session['fine_tuned'] is not None:
                            if session['tts_engine'] is not None:
                                if session['tts_engine'] in models.keys():
                                    if session['fine_tuned'] not in models[session['tts_engine']].keys():
                                        session['fine_tuned'] = default_fine_tuned
                                else:
                                    session['tts_engine'] = default_tts_engine
                                    session['fine_tuned'] = default_fine_tuned
                        if session['audiobook'] is not None:
                            if not os.path.exists(session['audiobook']):
                                session['audiobook'] = None
                        if session['status'] == 'converting':
                            session['status'] = None
                    except Exception as e:
                        error = f'change_gr_read_data(): {e}'
                        alert_exception(error)
                        return gr.update(), gr.update(), gr.update()
                session['system'] = (f"{platform.system()}-{platform.release()}").lower()
                session['custom_model_dir'] = os.path.join(models_dir, '__sessions', f"model-{session['id']}")
                session['voice_dir'] = os.path.join(voices_dir, '__sessions', f"voice-{session['id']}")
                os.makedirs(session['custom_model_dir'], exist_ok=True)
                os.makedirs(session['voice_dir'], exist_ok=True)             
                if is_gui_shared:
                    msg = f' Note: access limit time: {interface_shared_tmp_expire} days'
                    session['audiobooks_dir'] = os.path.join(audiobooks_gradio_dir, f"web-{session['id']}")
                    delete_unused_tmp_dirs(audiobooks_gradio_dir, interface_shared_tmp_expire, session)
                else:
                    msg = f' Note: if no activity is detected after {tmp_expire} days, your session will be cleaned up.'
                    session['audiobooks_dir'] = os.path.join(audiobooks_host_dir, f"web-{session['id']}")
                    delete_unused_tmp_dirs(audiobooks_host_dir, tmp_expire, session)
                if not os.path.exists(session['audiobooks_dir']):
                    os.makedirs(session['audiobooks_dir'], exist_ok=True)
                previous_hash = state['hash']
                new_hash = hash_proxy_dict(MappingProxyType(session))
                state['hash'] = new_hash
                session_dict = proxy_to_dict(session)
                show_alert({"type": "info", "msg": msg})
                return gr.update(value=session_dict), gr.update(value=state), gr.update(value=session['id'])
            except Exception as e:
                error = f'change_gr_read_data(): {e}'
                alert_exception(error)
                return gr.update(), gr.update(), gr.update()

        def save_session(id, state):
            try:
                if id:
                    if id in context.sessions:
                        session = context.get_session(id)
                        if session:
                            if session['event'] == 'clear':
                                session_dict = session
                            else:
                                previous_hash = state['hash']
                                new_hash = hash_proxy_dict(MappingProxyType(session))
                                if previous_hash == new_hash:
                                    return gr.update(), gr.update(), gr.update()
                                else:
                                    state['hash'] = new_hash
                                    session_dict = proxy_to_dict(session)
                            if session['status'] == 'converting':
                                if session['progress'] != len(audiobook_options):
                                    session['progress'] = len(audiobook_options)
                                    return gr.update(value=json.dumps(session_dict, indent=4)), gr.update(value=state), update_gr_audiobook_list(id)
                            return gr.update(value=json.dumps(session_dict, indent=4)), gr.update(value=state), gr.update()
                return gr.update(), gr.update(), gr.update()
            except Exception as e:
                error = f'save_session(): {e}!'
                alert_exception(error)              
                return gr.update(), gr.update(value=e), gr.update()
        
        def clear_event(id):
            session = context.get_session(id)
            if session['event'] is not None:
                session['event'] = None

        gr_ebook_file.change(
            fn=update_convert_btn,
            inputs=[gr_ebook_file, gr_ebook_mode, gr_custom_model_file, gr_session],
            outputs=[gr_convert_btn]
        ).then(
            fn=change_gr_ebook_file,
            inputs=[gr_ebook_file, gr_session],
            outputs=[gr_modal]
        )
        gr_ebook_mode.change(
            fn=change_gr_ebook_mode,
            inputs=[gr_ebook_mode, gr_session],
            outputs=[gr_ebook_file]
        )
        gr_voice_file.upload(
            fn=change_gr_voice_file,
            inputs=[gr_voice_file, gr_session],
            outputs=[gr_voice_file]
        ).then(
            fn=update_gr_voice_list,
            inputs=[gr_session],
            outputs=[gr_voice_list]
        )
        gr_voice_list.change(
            fn=change_gr_voice_list,
            inputs=[gr_voice_list, gr_session],
            outputs=[gr_voice_player, gr_voice_del_btn]
        )
        gr_voice_del_btn.click(
            fn=click_gr_voice_del_btn,
            inputs=[gr_voice_list, gr_session],
            outputs=[gr_confirm_field_hidden, gr_modal]
        )
        gr_device.change(
            fn=change_gr_device,
            inputs=[gr_device, gr_session],
            outputs=None
        )
        gr_language.change(
            fn=change_gr_language,
            inputs=[gr_language, gr_session],
            outputs=[gr_language, gr_voice_list, gr_tts_engine_list, gr_custom_model_list, gr_fine_tuned_list]
        )
        gr_tts_engine_list.change(
            fn=change_gr_tts_engine_list,
            inputs=[gr_tts_engine_list, gr_session],
            outputs=[gr_tab_preferences, gr_group_custom_model, gr_fine_tuned_list, gr_custom_model_file] 
        )
        gr_fine_tuned_list.change(
            fn=change_gr_fine_tuned_list,
            inputs=[gr_fine_tuned_list, gr_session],
            outputs=[gr_group_custom_model]
        )
        gr_custom_model_file.upload(
            fn=change_gr_custom_model_file,
            inputs=[gr_custom_model_file, gr_tts_engine_list, gr_session],
            outputs=[gr_custom_model_file]
        ).then(
            fn=update_gr_custom_model_list,
            inputs=[gr_session],
            outputs=[gr_custom_model_list]
        )
        gr_custom_model_list.change(
            fn=change_gr_custom_model_list,
            inputs=[gr_custom_model_list, gr_session],
            outputs=[gr_fine_tuned_list, gr_custom_model_del_btn]
        )
        gr_custom_model_del_btn.click(
            fn=click_gr_custom_model_del_btn,
            inputs=[gr_custom_model_list, gr_session],
            outputs=[gr_confirm_field_hidden, gr_modal]
        )
        gr_output_format_list.change(
            fn=change_gr_output_format_list,
            inputs=[gr_output_format_list, gr_session],
            outputs=None
        )
        gr_audiobook_download_btn.click(
            fn=lambda audiobook: show_alert({"type": "info", "msg": f'Downloading {os.path.basename(audiobook)}'}),
            inputs=[gr_audiobook_list],
            outputs=None,
            show_progress='minimal'
        )
        gr_audiobook_list.change(
            fn=change_gr_audiobook_list,
            inputs=[gr_audiobook_list, gr_session],
            outputs=[gr_audiobook_download_btn, gr_audiobook_player, gr_group_audiobook_list]
        )
        gr_audiobook_del_btn.click(
            fn=click_gr_audiobook_del_btn,
            inputs=[gr_audiobook_list, gr_session],
            outputs=[gr_confirm_field_hidden, gr_modal]
        )
        ########## Parameters
        gr_temperature.change(
            fn=lambda val, id: change_param('temperature', val, id),
            inputs=[gr_temperature, gr_session],
            outputs=None
        )
        gr_length_penalty.change(
            fn=lambda val, id, val2: change_param('length_penalty', val, id, val2),
            inputs=[gr_length_penalty, gr_session, gr_num_beams],
            outputs=None,
        )
        gr_num_beams.change(
            fn=lambda val, id, val2: change_param('num_beams', val, id, val2),
            inputs=[gr_num_beams, gr_session, gr_length_penalty],
            outputs=None,
        )
        gr_repetition_penalty.change(
            fn=lambda val, id: change_param('repetition_penalty', val, id),
            inputs=[gr_repetition_penalty, gr_session],
            outputs=None
        )
        gr_top_k.change(
            fn=lambda val, id: change_param('top_k', val, id),
            inputs=[gr_top_k, gr_session],
            outputs=None
        )
        gr_top_p.change(
            fn=lambda val, id: change_param('top_p', val, id),
            inputs=[gr_top_p, gr_session],
            outputs=None
        )
        gr_speed.change(
            fn=lambda val, id: change_param('speed', val, id),
            inputs=[gr_speed, gr_session],
            outputs=None
        )
        gr_enable_text_splitting.change(
            fn=lambda val, id: change_param('enable_text_splitting', val, id),
            inputs=[gr_enable_text_splitting, gr_session],
            outputs=None
        )
        ##########
        # Timer to save session to localStorage
        gr_timer = gr.Timer(10, active=False)
        gr_timer.tick(
            fn=save_session,
            inputs=[gr_session, gr_state],
            outputs=[gr_write_data, gr_state, gr_audiobook_list],
        ).then(
            fn=clear_event,
            inputs=[gr_session],
            outputs=None
        )
        gr_convert_btn.click(
            fn=update_convert_btn,
            inputs=None,
            outputs=[gr_convert_btn]
        ).then(
            fn=submit_convert_btn,
            inputs=[
                gr_session, gr_device, gr_ebook_file, gr_tts_engine_list, gr_voice_list, gr_language, 
                gr_custom_model_list, gr_fine_tuned_list, gr_output_format_list, gr_temperature, gr_length_penalty,
                gr_num_beams, gr_repetition_penalty, gr_top_k, gr_top_p, gr_speed, gr_enable_text_splitting
            ],
            outputs=[gr_conversion_progress]
        ).then(
            fn=refresh_interface,
            inputs=[gr_session],
            outputs=[gr_convert_btn, gr_ebook_file, gr_audiobook_list, gr_audiobook_player, gr_modal]
        )
        gr_write_data.change(
            fn=None,
            inputs=[gr_write_data],
            js='''
                (data)=>{
                    if(data){
                        localStorage.clear();
                        if(data['event'] != 'clear'){
                            console.log('save: ', data);
                            window.localStorage.setItem("data", JSON.stringify(data));
                        }
                    }
                }
            '''
        )       
        gr_read_data.change(
            fn=change_gr_read_data,
            inputs=[gr_read_data, gr_state],
            outputs=[gr_write_data, gr_state, gr_session]
        ).then(
            fn=restore_interface,
            inputs=[gr_session],
            outputs=[
                gr_ebook_file, gr_ebook_mode, gr_device, gr_language, gr_voice_list,
                gr_tts_engine_list, gr_custom_model_list, gr_fine_tuned_list,
                gr_output_format_list, gr_audiobook_list,
                gr_temperature, gr_length_penalty, gr_num_beams, gr_repetition_penalty,
                gr_top_k, gr_top_p, gr_speed, gr_enable_text_splitting, gr_timer
            ]
        )
        gr_confirm_yes_btn_hidden.click(
            fn=confirm_deletion,
            inputs=[gr_voice_list, gr_custom_model_list, gr_audiobook_list, gr_session, gr_confirm_field_hidden],
            outputs=[gr_voice_list, gr_custom_model_list, gr_audiobook_list, gr_modal]
        )
        gr_confirm_no_btn_hidden.click(
            fn=confirm_deletion,
            inputs=[gr_voice_list, gr_custom_model_list, gr_audiobook_list, gr_session],
            outputs=[gr_voice_list, gr_custom_model_list, gr_audiobook_list, gr_modal]
        )
        interface.load(
            fn=None,
            js='''
            () => {
                try{
                    const data = window.localStorage.getItem('data');
                    if(data){
                        const obj = JSON.parse(data);
                        console.log(obj);
                        return obj;
                    }
                }catch(e){
                    console.log('error: ',e)
                }
                return null;
            }
            ''',
            outputs=[gr_read_data]
        )
    try:
        all_ips = get_all_ip_addresses()
        msg = f'IPs available for connection:\n{all_ips}\nNote: 0.0.0.0 is not the IP to connect. Instead use an IP above to connect.'
        show_alert({"type": "info", "msg": msg})
        interface.queue(default_concurrency_limit=interface_concurrency_limit).launch(show_error=debug_mode, server_name=interface_host, server_port=interface_port, share=is_gui_shared, max_file_size=max_upload_size)
    except OSError as e:
        error = f'Connection error: {e}'
        alert_exception(error)
    except socket.error as e:
        error = f'Socket error: {e}'
        alert_exception(error)
    except KeyboardInterrupt:
        error = 'Server interrupted by user. Shutting down...'
        alert_exception(error)
    except Exception as e:
        error = f'An unexpected error occurred: {e}'
        alert_exception(error)
