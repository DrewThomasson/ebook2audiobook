# NOTE!!NOTE!!!NOTE!!NOTE!!!NOTE!!NOTE!!!NOTE!!NOTE!!!
# THE WORD "CHAPTER" IN THE CODE DOES NOT MEAN
# IT'S THE REAL CHAPTER OF THE EBOOK SINCE NO STANDARDS
# ARE DEFINING A CHAPTER ON .EPUB FORMAT. THE WORD "BLOCK"
# IS USED TO PRINT IT OUT TO THE TERMINAL, AND "CHAPTER" TO THE CODE
# WHICH IS LESS GENERIC FOR THE DEVELOPERS

#TODO: Make GPU release memory before moving onto FFMPEG file conversion, normalization, and noise reduction process
#TODO: Make this process send a signal to observer before FFMPEG process starts to that observer can start the next book conversion process and use the GPU while the CPU is occupied 

import argparse
import asyncio
import csv
import jieba
import ebooklib
import fnmatch
import gc
import gradio as gr
import hashlib
import json
import multiprocessing
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
import stanza
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import time
import torch
import urllib.request
import uuid
import uvicorn
import zipfile
import traceback
import unicodedata

from soynlp.tokenizer import LTokenizer
from pythainlp.tokenize import word_tokenize
from sudachipy import dictionary, tokenizer
from tqdm import tqdm
from bs4 import BeautifulSoup
from collections import Counter
from collections.abc import Mapping
from collections.abc import MutableMapping
from datetime import datetime
from ebooklib import epub
from glob import glob
from iso639 import languages
from markdown import markdown
from multiprocessing import Manager, Event
from multiprocessing.managers import DictProxy, ListProxy
from num2words import num2words
from pathlib import Path
from pydub import AudioSegment
from queue import Queue, Empty
from types import MappingProxyType
from urllib.parse import urlparse
from starlette.requests import ClientDisconnect

from lib import *
from lib.classes.voice_extractor import VoiceExtractor
from lib.classes.tts_manager import TTSManager
#from lib.classes.redirect_console import RedirectConsole
#from lib.classes.argos_translator import ArgosTranslator

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
                "temperature": default_engine_settings[TTS_ENGINES['XTTSv2']]['temperature'],
                "length_penalty": default_engine_settings[TTS_ENGINES['XTTSv2']]['length_penalty'],
                "num_beams": default_engine_settings[TTS_ENGINES['XTTSv2']]['num_beams'],
                "repetition_penalty": default_engine_settings[TTS_ENGINES['XTTSv2']]['repetition_penalty'],
                "top_k": default_engine_settings[TTS_ENGINES['XTTSv2']]['top_k'],
                "top_p": default_engine_settings[TTS_ENGINES['XTTSv2']]['top_k'],
                "speed": default_engine_settings[TTS_ENGINES['XTTSv2']]['speed'],
                "enable_text_splitting": default_engine_settings[TTS_ENGINES['XTTSv2']]['enable_text_splitting'],
                "text_temp": default_engine_settings[TTS_ENGINES['BARK']]['text_temp'],
                "waveform_temp": default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp'],
                "event": None,
                "final_name": None,
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
			required_files_lc = set(x.lower() for x in required_files)
			with tqdm(total=files_length, unit='files') as t:
				for f in files:
					base_f = os.path.basename(f).lower()
					if base_f in required_files_lc:
						out_path = os.path.join(model_path, base_f)
						with zip_ref.open(f) as src, open(out_path, 'wb') as dst:
							shutil.copyfileobj(src, dst)
					t.update(1)
		if is_gui_process:
			os.remove(file_src)
		if model_path is not None:
			msg = f'Extracted files to {model_path}'
			print(msg)
			return model_path
		else:
			error = f'An error occured when unzip {file_src}'
			return None
	except asyncio.exceptions.CancelledError as e:
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

def proxy2dict(proxy_obj):
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

def check_formatted_number(text, max_single_value=999_999_999_999_999):
	text = text.strip()
	digit_count = sum(c.isdigit() for c in text)
	if digit_count <= 9:
		return text
	try:
		as_number = float(text.replace(",", ""))
		if abs(as_number) <= max_single_value:
			return text
	except ValueError:
		pass
	tokens = re.findall(r'\d*\.\d+|\d+|[^\w\s]|[\w]+|\s+', text)
	result = []
	for token in tokens:
		if re.fullmatch(r'\d*\.\d+', token):
			try:
				num = float(token)
				result.append(num2words(num))
			except:
				result.append(token)
		elif token.isdigit():
			try:
				num = int(token)
				result.append(num2words(num))
			except:
				result.append(token)
		else:
			result.append(token)
	return ''.join(result)

def check_num2words_compat():
    try:
        num2words(1, lang=lang_iso1)
        return True
    except NotImplementedError:
        return False
    except Exception as e:
        return False

def math2word(text, lang, lang_iso1, tts_engine):

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
            error = f"Error converting number: {number}, Error: {e}"
            print(error)
            return f"{number}"

    def replace_ambiguous(match):
        symbol2 = match.group(2)
        symbol3 = match.group(3)
        if symbol2 in ambiguous_replacements: # "num SYMBOL num" case
            return f"{match.group(1)} {ambiguous_replacements[symbol2]} {match.group(3)}"            
        elif symbol3 in ambiguous_replacements: # "SYMBOL num" case
            return f"{ambiguous_replacements[symbol3]} {match.group(4)}"
        return match.group(0)

    def detect_date_entities(text):
        #check if stanza already exists and has the target language
        if os.path.exists(os.path.join(models_dir, 'stanza', lang_iso1)):
            nlp = stanza.Pipeline(lang_iso1, processors='tokenize,ner')
        else:
            stanza.download(lang_iso1)
            nlp = stanza.Pipeline(lang_iso1, processors='tokenize,ner')
        doc = nlp(text)
        date_spans = []
        for ent in doc.ents:
            if ent.type == 'DATE':
                date_spans.append((ent.start_char, ent.end_char, ent.text))
        return date_spans

    def year_to_words(match):
        year = int(match.group())
        year_str = str(year)
        if len(year_str) != 4 or not year_str.isdigit():
            return num2words(year)
        first_two = int(year_str[:2])
        last_two = int(year_str[2:])
        return f"{num2words(first_two)} {num2words(last_two)}"

    if bool(re.search(r'[-+]?\b\d+(\.\d+)?\b', text)):
        is_num2words_compat = check_num2words_compat()  
        # Check if there are positive integers so possible date to convert
        if bool(re.search(r'\b\d+\b', text)):
            if lang in year_to_decades_languages:
                date_spans = detect_date_entities(text)
                result = []
                last_pos = 0
                for start, end, date_text in date_spans:
                    # Append text before this date
                    result.append(text[last_pos:start])
                    processed = re.sub(r"\b\d{4}\b", year_to_words, date_text)
                    result.append(processed)
                    last_pos = end
                # Append remaining text
                result.append(text[last_pos:])
                text = ''.join(result)       
        # Check if it's a serie of small numbers with a separator
        text = check_formatted_number(text)
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
        if tts_engine in [TTS_ENGINES['VITS'], TTS_ENGINES['FAIRSEQ'], TTS_ENGINES['TACOTRON2'], TTS_ENGINES['YOURTTS']]:
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
    # Remove emojis
    emoji_pattern = re.compile(f"[{''.join(emojis_array)}]+", flags=re.UNICODE)
    emoji_pattern.sub('', text)
    if lang in abbreviations_mapping:
        abbr_map = {re.sub(r'\.', '', k).lower(): v for k, v in abbreviations_mapping[lang].items()}
        pattern = re.compile(r'\b(' + '|'.join(re.escape(k).replace('\\.', '') for k in abbreviations_mapping[lang].keys()) + r')\.?\b', re.IGNORECASE)
        text = pattern.sub(lambda m: abbr_map.get(m.group(1).lower(), m.group()), text)
    # This regex matches sequences like a., c.i.a., f.d.a., m.c., etc...
    pattern = re.compile(r'\b(?:[a-zA-Z]\.){1,}[a-zA-Z]?\b\.?')
    # uppercase acronyms
    text = re.sub(r'\b(?:[a-zA-Z]\.){1,}[a-zA-Z]?\b\.?', lambda m: m.group().replace('.', '').upper(), text)
    # Replace ### and [pause] with ‡pause‡ (‡ = double dagger U+2021)
    text = re.sub(r'(###|\[pause\])', '‡pause‡', text)
    # Replace multiple newlines ("\n\n", "\r\r", "\n\r", etc.) with a ‡pause‡ 1.4sec
    pattern = r'(?:\r\n|\r|\n){2,}'
    text = re.sub(pattern, '‡pause‡', text)
    # Replace single newlines ("\n" or "\r") with spaces
    text = re.sub(r'\r\n|\r|\n', ' ', text)
    # Replace punctuations causing hallucinations
    pattern = f"[{''.join(map(re.escape, punctuation_switch.keys()))}]"
    text = re.sub(pattern, lambda match: punctuation_switch.get(match.group(), match.group()), text)
    # Replace NBSP with a normal space
    text = text.replace("\xa0", " ")
    # Replace multiple and spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Replace ok by 'Owkey'
    text = re.sub(r'\bok\b', 'Okay', text, flags=re.IGNORECASE)
    # Replace parentheses with double quotes
    text = re.sub(r'\(([^)]+)\)', r'"\1"', text)
    # Escape special characters in the punctuation list for regex
    pattern = '|'.join(map(re.escape, punctuation_split))
    # Reduce multiple consecutive punctuations
    text = re.sub(rf'(\s*({pattern})\s*)+', r'\2 ', text).strip()
    if tts_engine == TTS_ENGINES['XTTSv2']:
        # Pattern 1: Add a space between UTF-8 characters and numbers
        text = re.sub(r'(?<=[\p{L}])(?=\d)|(?<=\d)(?=[\p{L}])', ' ', text)
        pattern_space = re.escape(''.join(punctuation_list))
        # Ensure space before and after punctuation (excluding `,` and `.`)
        punctuation_pattern_space = r'\s*([{}])\s*'.format(pattern_space.replace(',', '').replace('.', ''))
        text = re.sub(punctuation_pattern_space, r' \1 ', text)
        # Ensure spaces before & after `,` and `.` ONLY when NOT between numbers
        comma_dot_pattern = r'(?<!\d)\s*(\.{3}|[,.])\s*(?!\d)'
        text = re.sub(comma_dot_pattern, r' \1 ', text)
    # Replace special chars with words
    specialchars = specialchars_mapping[lang] if lang in specialchars_mapping else specialchars_mapping['eng']
    for char, word in specialchars.items():
        text = text.replace(char, f" {word} ")
    for char in specialchars_remove:
        text = text.replace(char, ' ')
    text = ' '.join(text.split())
    if text.strip():
        # Add punctuation after numbers or Roman numerals at start of a chapter.
        roman_pattern = r'^(?=[IVXLCDM])((?:M{0,3})(?:CM|CD|D?C{0,3})?(?:XC|XL|L?X{0,3})?(?:IX|IV|V?I{0,3}))(?=\s|$)'
        arabic_pattern = r'^(\d+)(?=\s|$)'
        if re.match(roman_pattern, text, re.IGNORECASE) or re.match(arabic_pattern, text):
            # Add punctuation if not already present (e.g. "II", "4")
            if not re.match(r'^([IVXLCDM\d]+)[\.,:;]', text, re.IGNORECASE):
                text = re.sub(r'^([IVXLCDM\d]+)', r'\1' + ' — ', text, flags=re.IGNORECASE)
        # Replace math symbols with words
        text = math2word(text, lang, lang_iso1, tts_engine)
    return text

def convert2epub(session):
    if session['cancellation_requested']:
        print('Cancel requested')
        return False
    try:
        title = False
        author = False
        util_app = shutil.which('ebook-convert')
        if not util_app:
            error = "The 'ebook-convert' utility is not installed or not found."
            print(error)
            return False
        file_input = session['ebook']
        if os.path.getsize(file_input) == 0:
            error = f"Input file is empty: {file_input}"
            print(error)
            return False
        file_ext = os.path.splitext(file_input)[1].lower()
        if file_ext not in ebook_formats:
            error = f'Unsupported file format: {file_ext}'
            print(error)
            return False
        if file_ext == '.pdf':
            import fitz
            msg = 'File input is a PDF. flatten it in MD and HTML...'
            print(msg)
            doc = fitz.open(session['ebook'])
            pdf_metadata = doc.metadata
            filename_no_ext = os.path.splitext(os.path.basename(session['ebook']))[0]
            title = pdf_metadata.get('title') or filename_no_ext
            author = pdf_metadata.get('author') or False
            markdown_text = pymupdf4llm.to_markdown(session['ebook'])
            file_input = os.path.join(session['process_dir'], f'{filename_no_ext}.md')
            with open(file_input, "w", encoding="utf-8") as html_file:
                html_file.write(markdown_text)
        msg = f"Running command: {util_app} {file_input} {session['epub_path']}"
        print(msg)
        cmd = [
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
            ]
        if title:
            cmd += ['--title', title]
        if author:
            cmd += ['--authors', author]
        result = subprocess.run(
            cmd,
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

def get_ebook_title(epubBook, all_docs):
    # 1. Try metadata (official EPUB title)
    meta_title = epubBook.get_metadata("DC", "title")
    if meta_title and meta_title[0][0].strip():
        return meta_title[0][0].strip()
    # 2. Try <title> in the head of the first XHTML document
    if all_docs:
        html = all_docs[0].get_content().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.select_one("head > title")
        if title_tag and title_tag.text.strip():
            return title_tag.text.strip()
        # 3. Try <img alt="..."> if no visible <title>
        img = soup.find("img", alt=True)
        if img:
            alt = img['alt'].strip()
            if alt and "cover" not in alt.lower():
                return alt
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
        msg = r'''
*******************************************************************************
NOTE:
The warning "Character xx not found in the vocabulary."
MEANS THE MODEL CANNOT INTERPRET THE CHARACTER AND WILL MAYBE GENERATE
(AS WELL AS WRONG PUNCTUATION POSITION) AN HALLUCINATION TO IMPROVE THIS MODEL,
IT NEEDS TO ADD THIS CHARACTER INTO A NEW TRAINING MODEL.
YOU CAN IMPROVE IT OR ASK TO A TRAINING MODEL EXPERT.
*******************************************************************************
        '''
        print(msg)
        if session['cancellation_requested']:
            print('Cancel requested')
            return False
        # Step 1: Extract TOC (Table of Contents)
        toc_list = []
        try:
            toc = epubBook.toc  # Extract TOC
            toc_list = [normalize_text(str(item.title), session['language'], session['language_iso1'], session['tts_engine']) for item in toc if hasattr(item, 'title')]
        except Exception as toc_error:
            error = f"Error extracting TOC: {toc_error}"
            print(error)
        # Get spine item IDs
        spine_ids = [item[0] for item in epubBook.spine]
        # Filter only spine documents (i.e., reading order)
        all_docs = [
            item for item in epubBook.get_items_of_type(ebooklib.ITEM_DOCUMENT)
            if item.id in spine_ids
        ]
        if not all_docs:
            return [], []
        title = get_ebook_title(epubBook, all_docs)
        chapters = []
        for doc in all_docs:
            sentences_array = filter_chapter(doc, session['language'], session['language_iso1'], session['tts_engine'])
            if sentences_array is not None:
                chapters.append(sentences_array)
        return toc, chapters
    except Exception as e:
        error = f'Error extracting main content pages: {e}'
        DependencyError(error)
        return None, None

def filter_chapter(doc, lang, lang_iso1, tts_engine):
    try:
        chapter_sentences = None
        raw_html = doc.get_body_content().decode("utf-8")
        soup = BeautifulSoup(raw_html, 'html.parser')

        if not soup.body or not soup.body.get_text(strip=True):
            return None
 
        # Get epub:type from <body> or outermost <section>
        epub_type = soup.body.get("epub:type", "").lower()
        if not epub_type:
            section_tag = soup.find("section")
            if section_tag and section_tag.get("epub:type"):
                epub_type = section_tag.get("epub:type").lower()

        # Skip known non-chapter types
        excluded_types = {
            "frontmatter", "backmatter", "toc", "titlepage", "colophon",
            "acknowledgments", "dedication", "glossary", "index",
            "appendix", "bibliography", "copyright-page", "landmark"
        }
        if any(part in epub_type for part in excluded_types):
            return None
        
        for script in soup(["script", "style"]):
            script.decompose()

        text_array = []
        handled_tables = set()
        for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "table"]):
            if tag.name == "table":
                # Ensure we don't process the same table multiple times
                if tag in handled_tables:
                    continue
                handled_tables.add(tag)
                rows = tag.find_all("tr")
                if not rows:
                    continue
                header_cells = [td.get_text(strip=True) for td in rows[0].find_all(["td", "th"])]
                for row in rows[1:]:
                    cells = [td.get_text(strip=True).replace('\xa0', ' ') for td in row.find_all("td")]
                    if len(cells) == len(header_cells):
                        line = " — ".join(f"{header}: {cell}" for header, cell in zip(header_cells, cells))
                    else:
                        line = " — ".join(cells)
                    if line:
                        text_array.append(line)
            elif tag.name == "p" and tag.find_parent("table"):
                continue  # Already handled in the <table> section
            elif tag.name == "p" and "whitespace" in (tag.get("class") or []):
                if tag.get_text(strip=True) == '\xa0' or not tag.get_text(strip=True):
                    text_array.append("[pause]")
            elif tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                raw_text = tag.get_text(strip=True)
                if raw_text:
                    # replace roman numbers by digits
                    raw_text = replace_roman_numbers(raw_text, lang)
                    text_array.append(f'{raw_text}.[pause]')
            else:
                raw_text = tag.get_text(strip=True)
                if raw_text:
                    text_array.append(raw_text)
        text = "\n".join(text_array)
        if text.strip():
            # Normalize lines and remove unnecessary spaces and switch special chars
            text = normalize_text(text, lang, lang_iso1, tts_engine)
            if text.strip() and len(text.strip()) > 1:
                chapter_sentences = get_sentences(text, lang, tts_engine)
        return chapter_sentences
    except Exception as e:
        DependencyError(e)
        return None

def get_sentences(text, lang, tts_engine):
    def combine_punctuation(tokens):
        if not tokens:
            return tokens
        result = [tokens[0]]
        for token in tokens[1:]:
            if (
                not any(char.isalpha() for char in token)
                and all(char.isspace() or char in punctuation_list_set for char in token)
                and len(result[-1]) + len(token) <= max_chars
            ):
                result[-1] += token
            else:
                result.append(token)
        return result

    def segment_ideogramms(text):
        if lang == 'zho':
            return list(jieba.cut(text))
        elif lang == 'jpn':
            sudachi = dictionary.Dictionary().create()
            mode = tokenizer.Tokenizer.SplitMode.C
            return [m.surface() for m in sudachi.tokenize(text, mode)]
        elif lang == 'kor':
            ltokenizer = LTokenizer()
            return ltokenizer.tokenize(text)
        elif lang in ['tha', 'lao', 'mya', 'khm']:
            return word_tokenize(text, engine='newmm')
        else:
            pattern_split = [re.escape(p) for p in punctuation_split_set]
            pattern = f"({'|'.join(pattern_split)})"
            return re.split(pattern, text)

    def join_ideogramms(idg_list):
        buffer = ''
        for token in idg_list:
            if not token.strip():
                continue
            buffer += token
            if token in punctuation_split_set:
                if len(buffer) > max_chars:
                    for part in [buffer[i:i + max_chars] for i in range(0, len(buffer), max_chars)]:
                        if part.strip() and not all(c in punctuation_split_set for c in part):
                            yield part
                    buffer = ''
                else:
                    if buffer.strip() and not all(c in punctuation_split_set for c in buffer):
                        yield buffer
                    buffer = ''
            elif len(buffer) >= max_chars:
                if buffer.strip() and not all(c in punctuation_split_set for c in buffer):
                    yield buffer
                buffer = ''
        if buffer.strip() and not all(c in punctuation_split_set for c in buffer):
            yield buffer

    def find_best_split_point_prioritize_punct(sentence, max_chars):
        best_index = -1
        min_diff = float('inf')
        punctuation_priority = '.!?,;:'
        space_priority = ' '
        for i in range(1, min(len(sentence), max_chars)):
            if sentence[i] in punctuation_priority:
                left_len = i
                right_len = len(sentence) - i
                diff = abs(left_len - right_len)
                if left_len <= max_chars and right_len <= max_chars and diff < min_diff:
                    best_index = i + 1
                    min_diff = diff
        if best_index == -1:
            for i in range(1, min(len(sentence), max_chars)):
                if sentence[i] in space_priority:
                    left_len = i
                    right_len = len(sentence) - i
                    diff = abs(left_len - right_len)
                    if left_len <= max_chars and right_len <= max_chars and diff < min_diff:
                        best_index = i + 1
                        min_diff = diff
        return best_index

    def split_sentence(sentence):
        sentence = sentence.strip()
        if len(sentence) <= max_chars:
            if lang not in ['zho', 'jpn', 'kor', 'tha', 'lao', 'mya', 'khm']:
                if sentence and sentence[-1].isalpha():
                    return [sentence + ' -']
            return [sentence]
        split_index = find_best_split_point_prioritize_punct(sentence, max_chars)
        if split_index == -1:
            mid = len(sentence) // 2
            before = sentence.rfind(' ', 0, mid)
            after = sentence.find(' ', mid)
            if before == -1 and after == -1:
                split_index = mid
            else:
                if before == -1:
                    split_index = after
                elif after == -1:
                    split_index = before
                else:
                    split_index = before if (mid - before) <= (after - mid) else after
        delim_used = sentence[split_index - 1] if split_index > 0 else None
        end = ''
        if lang not in ['zho', 'jpn', 'kor', 'tha', 'lao', 'mya', 'khm'] and tts_engine != TTS_ENGINES['BARK']:
            end = ' -' if delim_used == ' ' else end
        part1 = sentence[:split_index].rstrip()
        part2 = sentence[split_index:].lstrip(' ,;:')
        result = []
        if len(part1) <= max_chars:
            if part1 and part1[-1].isalpha():
                part1 += end
            result.append(part1)
        else:
            result.extend(split_sentence(part1))
        if part2:
            if len(part2) <= max_chars:
                if part2 and part2[-1].isalpha():
                    if tts_engine != TTS_ENGINES['BARK']:
                        part2 += ' -'
                result.append(part2)
            else:
                result.extend(split_sentence(part2))
        return result

    max_chars = language_mapping[lang]['max_chars'] - 2
    pattern_split = [re.escape(p) for p in punctuation_split_set]
    pattern = f"({'|'.join(pattern_split)})"
    if lang in ['zho', 'jpn', 'kor', 'tha', 'lao', 'mya', 'khm']:
        ideogramm_list = segment_ideogramms(text)
        raw_list = list(join_ideogramms(ideogramm_list))
    else:
        raw_list = re.split(pattern, text)
    raw_list = combine_punctuation(raw_list)
    if len(raw_list) > 1:
        tmp_list = [raw_list[i] + raw_list[i + 1] for i in range(0, len(raw_list) - 1, 2)]
        if len(raw_list) % 2 != 0:
            tmp_list.append(raw_list[-1])
    else:
        tmp_list = raw_list
    if tmp_list and tmp_list[-1] == 'Start':
        tmp_list.pop()
    sentences = []
    for sentence in tmp_list:
        sentences.extend(split_sentence(sentence.strip()))
    return sentences

def get_ram():
    vm = psutil.virtual_memory()
    return vm.total // (1024 ** 3)

def get_vram():
    os_name = platform.system()
    # NVIDIA (Cross-Platform: Windows, Linux, macOS)
    try:
        from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(0)  # First GPU
        info = nvmlDeviceGetMemoryInfo(handle)
        vram = info.total
        return int(vram // (1024 ** 3))  # Convert to GB
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
                return int(vram_values[0] // (1024 ** 3))
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
    msg = 'Could not detect GPU VRAM Capacity!'
    return 0

def get_sanitized(str, replacement="_"):
    str = str.replace('&', 'And')
    forbidden_chars = r'[<>:"/\\|?*\x00-\x1F ()]'
    sanitized = re.sub(r'\s+', replacement, str)
    sanitized = re.sub(forbidden_chars, replacement, sanitized)
    sanitized = sanitized.strip("_")
    return sanitized

tts_manager = None

def init_worker_process(session_data):
    """Initializes a TTSManager for each worker process."""
    global tts_manager
    session = recursive_proxy(session_data)
    tts_manager = TTSManager(session)

def process_sentence_chunk(chunk):
    """
    Processes a chunk of sentences in a single worker process.
    `chunk` is a list of tuples: [(sentence_number, sentence_text), ...]
    """
    global tts_manager
    if tts_manager is None:
        # Worker not initialized, return empty success
        return (0, [])
    results = []
    for sentence_number, sentence in chunk:
        result = tts_manager.convert_sentence2audio(sentence_number, sentence)
        results.append(result)
    # Return the number of processed items for the progress bar
    return (len(chunk), results)

def convert_chapters2audio(session):
    try:
        if session.get('cancellation_requested'):
            print('Cancel requested')
            return False

        progress_bar = gr.Progress(track_tqdm=True) if is_gui_process else None
        num_workers = session.get('num_workers', 5)
        print(f"Starting TTS conversion with {num_workers} processes.")

        # --- Sentence Preparation & Resume Logic ---
        all_sentences = []
        for sentences in session['chapters']:
            all_sentences.extend(sentences)
        
        total_sentences = len(all_sentences)
        all_sentences_with_indices = list(enumerate(all_sentences))

        existing_sentence_files = os.listdir(session['chapters_dir_sentences'])
        existing_sentence_numbers = {
            int(re.search(r'\d+', f).group())
            for f in existing_sentence_files
            if f.endswith(f'.{default_audio_proc_format}')
        }
        
        sentences_to_process = [s for s in all_sentences_with_indices if s[0] not in existing_sentence_numbers]
        
        if not sentences_to_process:
            print("All sentences have already been converted. Proceeding to combine chapters.")
        else:
            print(f"Found {len(existing_sentence_numbers)} existing sentences. Processing {len(sentences_to_process)} new sentences...")

            # --- TTS Conversion with Chunking ---
            chunk_size = 20
            chunks = [sentences_to_process[i:i + chunk_size] for i in range(0, len(sentences_to_process), chunk_size)]
            session_data = dict(session)

            with tqdm(total=len(sentences_to_process), desc='Converting Sentences', unit='sentence') as pbar:
                # Ensure spawn method is used for multiprocessing to be GPU-safe
                with ProcessPoolExecutor(max_workers=num_workers, mp_context=multiprocessing.get_context('spawn'), initializer=init_worker_process, initargs=(session_data,)) as executor:
                    futures = [executor.submit(process_sentence_chunk, chunk) for chunk in chunks]
                    
                    for future in as_completed(futures):
                        if session.get('cancellation_requested'):
                            executor.shutdown(wait=False, cancel_futures=True)
                            print("Cancellation requested, stopping sentence conversion.")
                            break
                        
                        try:
                            processed_count, results = future.result()
                            if processed_count > 0:
                                pbar.update(processed_count)
                                if progress_bar:
                                    overall_progress = (len(existing_sentence_numbers) + pbar.n) / total_sentences
                                    progress_bar(overall_progress)
                        except Exception as e:
                            print(f"A sentence chunk failed to process: {e}")
                            traceback.print_exc()
                            executor.shutdown(wait=False, cancel_futures=True)
                            return False

        if session.get('cancellation_requested'):
            print("Conversion cancelled. Skipping chapter combination.")
            return False

        # --- Combine Sentences into Chapters ---
        print("All sentences converted. Combining into chapter files...")
        sentence_number = 0
        for x, sentences in enumerate(session['chapters']):
            chapter_num = x + 1
            chapter_audio_file = f'chapter_{chapter_num}.{default_audio_proc_format}'
            start_sentence = sentence_number
            end_sentence = sentence_number + len(sentences) - 1

            if os.path.exists(os.path.join(session['chapters_dir'], chapter_audio_file)):
                print(f"Chapter {chapter_num} already exists. Skipping combination.")
                sentence_number = end_sentence + 1
                continue

            print(f'Combining block {chapter_num} from sentences {start_sentence} to {end_sentence}...')
            if not combine_audio_sentences(chapter_audio_file, start_sentence, end_sentence, session):
                print(f'Failed to combine block {chapter_num}. Aborting.')
                return False
            
            sentence_number = end_sentence + 1

        print("Successfully created all chapter audio files.")
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
                encoding='utf-8',
                errors='ignore'
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
                    encoding='utf-8',
                    errors='ignore'
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
            if session.get('cancellation_requested'):
                print('Cancel requested')
                return False

            num_workers = max(1, os.cpu_count() - 1)
            
            def get_duration(file_path):
                try:
                    ffprobe_cmd = [shutil.which('ffprobe'), '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
                    result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True, encoding='utf-8')
                    return float(result.stdout.strip())
                except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
                    print(f"Could not get duration of {file_path}, processing with single thread. Error: {e}")
                    return None

            duration = get_duration(combined_chapters_file)

            # Fallback to single-threaded if we can't process in parallel
            if num_workers <= 1 or duration is None:
                print("Processing with a single thread...")
                ffmpeg_cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', combined_chapters_file, '-i', metadata_file]
                if session['output_format'] == 'wav':
                    ffmpeg_cmd += ['-map', '0:a']
                elif session['output_format'] == 'aac':
                    ffmpeg_cmd += ['-c:a', 'aac', '-b:a', '128k', '-ar', '44100']
                else:
                    ffmpeg_cmd += ['-map', '0:a']
                    if session['output_format'] in ['m4a', 'm4b', 'mp4']:
                        ffmpeg_cmd += ['-c:a', 'aac', '-b:a', '128k', '-ar', '44100', '-movflags', '+faststart']
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

                ffmpeg_cmd += ['-strict', 'experimental', '-map_metadata', '1', '-threads', '1', '-y', final_file]
                
                process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', errors='ignore')
                for line in process.stdout:
                    print(line, end='')
                process.wait()
                return process.returncode == 0

            # --- Parallel Processing Logic ---
            print(f"Processing in parallel with {num_workers} threads...")
            segment_dir = os.path.join(session['process_dir'], 'segments')
            os.makedirs(segment_dir, exist_ok=True)
            
            processed_segments = [None] * num_workers

            # --- Pre-split the audio file into raw segments --- 
            print("Splitting the combined audio into raw segments to avoid seeking issues...")
            raw_segment_dir = os.path.join(session['process_dir'], 'raw_segments')
            os.makedirs(raw_segment_dir, exist_ok=True)
            raw_segment_files = []

            for i in range(num_workers):
                start_time = i * (duration / num_workers)
                end_time_arg = ['-to', str(start_time + (duration / num_workers))] if i < num_workers - 1 else []
                raw_segment_path = os.path.join(raw_segment_dir, f'raw_segment_{i}.{default_audio_proc_format}')
                raw_segment_files.append(raw_segment_path)
                
                # Use fast input seeking for splitting, as no complex filters are applied here.
                split_cmd = [shutil.which('ffmpeg'), '-ss', str(start_time), '-i', combined_chapters_file] + end_time_arg + ['-c', 'copy', '-y', raw_segment_path]
                
                try:
                    subprocess.run(split_cmd, check=True, capture_output=True, text=True, encoding='utf-8')
                except subprocess.CalledProcessError as e:
                    print(f"Error splitting audio file for segment {i}:\nCMD: {' '.join(e.cmd)}\nSTDERR: {e.stderr}")
                    shutil.rmtree(raw_segment_dir, ignore_errors=True)
                    return False
            
            print("Successfully split audio into raw segments.")

            def process_segment(raw_segment_path):
                segment_index = int(re.search(r'_(\d+)\.', os.path.basename(raw_segment_path)).group(1))
                segment_output_path = os.path.join(segment_dir, f"segment_{segment_index}.{session['output_format']}")
                
                # Command now uses the pre-split raw segment as input, no seeking needed.
                ffmpeg_cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', raw_segment_path]

                if session['output_format'] == 'wav': pass
                elif session['output_format'] == 'aac': ffmpeg_cmd += ['-c:a', 'aac', '-b:a', '128k', '-ar', '44100']
                else:
                    if session['output_format'] in ['m4a', 'm4b', 'mp4']: ffmpeg_cmd += ['-c:a', 'aac', '-b:a', '128k', '-ar', '44100']
                    elif session['output_format'] == 'webm': ffmpeg_cmd += ['-c:a', 'libopus', '-b:a', '64k']
                    elif session['output_format'] == 'ogg': ffmpeg_cmd += ['-c:a', 'libopus', '-b:a', '128k', '-compression_level', '0']
                    elif session['output_format'] == 'flac': ffmpeg_cmd += ['-c:a', 'flac', '-compression_level', '4']
                    elif session['output_format'] == 'mp3': ffmpeg_cmd += ['-c:a', 'libmp3lame', '-b:a', '128k', '-ar', '44100']
                    if session['output_format'] != 'ogg': ffmpeg_cmd += ['-af', 'loudnorm=I=-16:LRA=11:TP=-1.5,afftdn=nf=-70']

                ffmpeg_cmd += ['-y', segment_output_path]

                try:
                    subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True, encoding='utf-8')
                    return segment_output_path
                except subprocess.CalledProcessError as e:
                    print(f"Error processing segment {segment_index}:\nCMD: {' '.join(e.cmd)}\nSTDERR: {e.stderr}")
                    return None

            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                processed_segment_paths = list(executor.map(process_segment, raw_segment_files))

            # Clean up the raw segments directory as it's no longer needed
            shutil.rmtree(raw_segment_dir, ignore_errors=True)

            if any(p is None for p in processed_segment_paths):
                print("One or more segments failed to process. Aborting.")
                shutil.rmtree(segment_dir, ignore_errors=True)
                return False

            concat_file_path = os.path.join(segment_dir, 'concat.txt')
            with open(concat_file_path, 'w', encoding='utf-8') as f:
                # Sort using a key that extracts the number from the filename to ensure correct order
                for seg_path in sorted(processed_segment_paths, key=lambda p: int(re.search(r'_(\d+)\.', os.path.basename(p)).group(1))):
                    f.write(f"file '{seg_path.replace(os.sep, '/')}'\n")

            temp_final_file = os.path.join(session['process_dir'], f"temp_final.{session['output_format']}")
            concat_cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-f', 'concat', '-safe', '0', '-i', concat_file_path, '-c', 'copy', '-y', temp_final_file]
            
            try:
                subprocess.run(concat_cmd, check=True, capture_output=True, text=True, encoding='utf-8')
            except subprocess.CalledProcessError as e:
                print(f"Error concatenating segments:\nCMD: {' '.join(e.cmd)}\nSTDERR: {e.stderr}")
                shutil.rmtree(segment_dir, ignore_errors=True)
                return False

            metadata_cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', temp_final_file, '-i', metadata_file, '-map', '0:a', '-map_metadata', '1', '-c', 'copy']
            if session['output_format'] in ['m4a', 'm4b', 'mp4']:
                 metadata_cmd += ['-movflags', '+faststart']
            
            metadata_cmd += ['-y', final_file]
            
            process = subprocess.Popen(metadata_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', errors='ignore')
            for line in process.stdout:
                print(line, end='')
            process.wait()

            shutil.rmtree(segment_dir, ignore_errors=True)
            if os.path.exists(temp_final_file):
                os.remove(temp_final_file)

            if process.returncode != 0:
                print(f"Error adding metadata. FFmpeg exit code: {process.returncode}")
                return False
            
            return True

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
                    final_file = os.path.join(session['audiobooks_dir'], session['final_name'])                       
                    if export_audio():
                        return final_file
        else:
            error = 'No block files exists!'
            print(error)
        return None
    except Exception as e:
        DependencyError(e)
        return False

def replace_roman_numbers(text, lang):
    def roman2int(s):
        try:
            roman = {
                'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000,
                'IV': 4, 'IX': 9, 'XL': 40, 'XC': 90, 'CD': 400, 'CM': 900
            }
            i = 0
            num = 0
            while i < len(s):
                if i + 1 < len(s) and s[i:i+2] in roman:
                    num += roman[s[i:i+2]]
                    i += 2
                else:
                    num += roman.get(s[i], 0)
                    i += 1
            return num if num > 0 else s
        except Exception:
            return s

    def replace_chapter_match(match):
        chapter_word = match.group(1)
        roman_numeral = match.group(2)
        if not roman_numeral:
            return match.group(0)
        integer_value = roman2int(roman_numeral.upper())
        if isinstance(integer_value, int):
            return f'{chapter_word.capitalize()} {integer_value}; '
        return match.group(0)

    def replace_numeral_with_period(match):
        roman_numeral = match.group(1)
        integer_value = roman2int(roman_numeral.upper())
        if isinstance(integer_value, int):
            return f'{integer_value}. '
        return match.group(0)

    # Get language-specific chapter words
    chapter_words = chapter_word_mapping.get(lang, [])
    # Escape and join to form regex pattern
    escaped_words = [re.escape(word) for word in chapter_words]
    word_pattern = "|".join(escaped_words)
    # Now build the full regex
    roman_chapter_pattern = re.compile(
        rf'\b({word_pattern})\s+'
        r'(?=[IVXLCDM])'
        r'((?:M{0,3})(?:CM|CD|D?C{0,3})?(?:XC|XL|L?X{0,3})?(?:IX|IV|V?I{0,3}))\b',
        re.IGNORECASE
    )
    # Roman numeral with trailing period
    roman_numerals_with_period = re.compile(
        r'^(?=[IVXLCDM])((?:M{0,3})(?:CM|CD|D?C{0,3})?(?:XC|XL|L?X{0,3})?(?:IX|IV|V?I{0,3}))\.+',
        re.IGNORECASE
    )
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
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            for dir in os.listdir(dir_path):
                if dir in current_user_dirs:        
                    full_dir_path = os.path.join(dir_path, dir)
                    if os.path.isdir(full_dir_path):
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
                error = f"{args['ebook']} needs a format extension."
                print(error)
                return error, false
            if not os.path.exists(args['ebook']):
                error = 'File does not exist or Directory empty.'
                print(error)
                return error, false
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
                return error, false

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
            session['num_workers'] = args['num_workers']
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
            session['text_temp'] =  args['text_temp']
            session['waveform_temp'] =  args['waveform_temp']
            session['audiobooks_dir'] = args['audiobooks_dir']
            session['voice'] = args['voice']
            
            info_session = f"\n*********** Session: {id} **************\nStore it in case of interruption, crash, reuse of custom model or custom voice,\nyou can resume the conversion with --session option"

            if not is_gui_process:
                session['voice_dir'] = os.path.join(voices_dir, '__sessions', f"voice-{session['id']}", session['language'])
                os.makedirs(session['voice_dir'], exist_ok=True)
                # As now uploaded voice files are in their respective language folder so check if no wav and bark folder are on the voice_dir root from previous versions
                [shutil.move(src, os.path.join(session['voice_dir'], os.path.basename(src))) for src in glob(os.path.join(os.path.dirname(session['voice_dir']), '*.wav')) + ([os.path.join(os.path.dirname(session['voice_dir']), 'bark')] if os.path.isdir(os.path.join(os.path.dirname(session['voice_dir']), 'bark')) and not os.path.exists(os.path.join(session['voice_dir'], 'bark')) else [])]
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
                        msg = ''
                        msg_extra = ''
                        vram_avail = get_vram()
                        if vram_avail <= 4:
                            msg_extra += 'VRAM capacity could not be detected. -' if vram_avail == 0 else 'VRAM under 4GB - '
                            if session['tts_engine'] == TTS_ENGINES['BARK']:
                                os.environ['SUNO_USE_SMALL_MODELS'] = 'True'
                                msg_extra += f"Switching BARK to SMALL models - "
                        else:
                            if session['tts_engine'] == TTS_ENGINES['BARK']:
                                os.environ['SUNO_USE_SMALL_MODELS'] = 'False'                        
                        if session['device'] == 'cuda':
                            session['device'] = session['device'] if torch.cuda.is_available() else 'cpu'
                            if session['device'] == 'cpu':
                                msg += f"GPU not recognized by torch! Read {default_gpu_wiki} - Switching to CPU - "
                        elif session['device'] == 'mps':
                            session['device'] = session['device'] if torch.backends.mps.is_available() else 'cpu'
                            if session['device'] == 'cpu':
                                msg += f"MPS not recognized by torch! Read {default_gpu_wiki} - Switching to CPU - "
                        if session['device'] == 'cpu':
                            if session['tts_engine'] == TTS_ENGINES['BARK']:
                                os.environ['SUNO_OFFLOAD_CPU'] = 'True'
                        if default_engine_settings[TTS_ENGINES['XTTSv2']]['use_deepspeed'] == True:
                            try:
                                import deepspeed
                            except:
                                default_engine_settings[TTS_ENGINES['XTTSv2']]['use_deepspeed'] = False
                                msg_extra += 'deepseed not installed or package is broken. set to False - '
                            else: 
                                msg_extra += 'deepspeed detected and ready!'
                        if msg == '':
                            msg = f"Using {session['device'].upper()} - "
                        msg += msg_extra
                        if is_gui_process:
                            show_alert({"type": "warning", "msg": msg})
                        print(msg)
                        session['epub_path'] = os.path.join(session['process_dir'], '__' + session['filename_noext'] + '.epub')
                        if convert2epub(session):
                            epubBook = epub.read_epub(session['epub_path'], {'ignore_ncx': True})       
                            metadata = dict(session['metadata'])
                            for key, value in metadata.items():
                                data = epubBook.get_metadata('DC', key)
                                if data:
                                    for value, attributes in data:
                                        metadata[key] = value
                            metadata['language'] = session['language']
                            metadata['title'] = metadata['title'] if metadata['title'] else os.path.splitext(os.path.basename(session['ebook']))[0].replace('_',' ')
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
                                session['final_name'] = get_sanitized(session['metadata']['title'] + '.' + session['output_format'])
                                if session['chapters'] is not None:
                                    if convert_chapters2audio(session):
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
                                        error = 'convert_chapters2audio() failed!'
                                else:
                                    error = 'get_chapters() failed!'
                            else:
                                error = 'get_cover() failed!'
                        else:
                            error = 'convert2epub() failed!'
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
    
    visible_gr_tab_xtts_params = interface_component_options['gr_tab_xtts_params']
    visible_gr_tab_bark_params = interface_component_options['gr_tab_bark_params']
    visible_gr_group_custom_model = interface_component_options['gr_group_custom_model']
    visible_gr_group_voice_file = interface_component_options['gr_group_voice_file']
    
    # Buffer for real-time log streaming
    log_buffer = Queue()
    
    # Event to signal when the process should stop
    thread = None
    stop_event = threading.Event()

    theme = gr.themes.Origin(
        primary_hue='green',
        secondary_hue='amber',
        neutral_hue='gray',
        radius_size='lg',
        font_mono=['JetBrains Mono', 'monospace', 'Consolas', 'Menlo', 'Liberation Mono']
    )

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
                .selected {
                    color: orange !important;
                }
                .progress-bar.svelte-ls20lj {
                    background: orange !important;
                }
                #gr_logo_markdown {
                    position:absolute; 
                    text-align:center;
                }
                #gr_ebook_file, #gr_custom_model_file, #gr_voice_file {
                    height: 140px !important !important;
                }
                #gr_custom_model_file [aria-label="Clear"], #gr_voice_file [aria-label="Clear"] {
                    display: none !important;
                }               
                #gr_tts_engine_list, #gr_fine_tuned_list, #gr_session, #gr_output_format_list {
                    height: 95px !important;
                }
                #gr_voice_list {
                    height: 60px !important;
                }
                #gr_voice_list span[data-testid="block-info"], 
                #gr_audiobook_list span[data-testid="block-info"] {
                    display: none !important;
                }
                ///////////////
                #gr_voice_player {
                    margin: 0 !important;
                    padding: 0 !important;
                    width: 60px !important;
                    height: 60px !important;
                }
                #gr_row_voice_player {
                    height: 60px !important;
                }
                #gr_voice_player :is(#waveform, .rewind, .skip, .playback, label, .volume, .empty) {
                    display: none !important;
                }
                #gr_voice_player .controls {
                    display: block !important;
                    position: absolute !important;
                    left: 15px !important;
                    top: 0 !important;
                }
                ///////////
                #gr_audiobook_player :is(.volume, .empty, .source-selection, .control-wrapper, .settings-wrapper) {
                    display: none !important;
                }
                #gr_audiobook_player label{
                    display: none !important;
                }
                #gr_audiobook_player audio {
                    width: 100% !important;
                    padding-top: 10px !important;
                    padding-bottom: 10px !important;
                    border-radius: 0px !important;
                    background-color: #ebedf0 !important;
                    color: #ffffff !important;
                }
                #gr_audiobook_player audio::-webkit-media-controls-panel {
                    width: 100% !important;
                    padding-top: 10px !important;
                    padding-bottom: 10px !important;
                    border-radius: 0px !important;
                    background-color: #ebedf0 !important;
                    color: #ffffff !important;
                }
            '''
        )
        gr_logo_markdown = gr.Markdown(elem_id='gr_logo_markdown', value=f'''
            <div style="right:0;margin:0;padding:0;text-align:right"><h3 style="display:inline;line-height:0.6">Ebook2Audiobook</h3>&nbsp;&nbsp;&nbsp;<a href="https://github.com/DrewThomasson/ebook2audiobook" style="text-decoration:none;font-size:14px" target="_blank">v{prog_version}</a></div>
            '''
        )
        with gr.Tabs():
            gr_tab_main = gr.TabItem('Main Parameters', elem_classes='tab_item')
            with gr_tab_main:
                with gr.Row():
                    with gr.Column(scale=3):
                        with gr.Group():
                            gr_ebook_file = gr.File(label=src_label_file, elem_id='gr_ebook_file', file_types=ebook_formats, file_count='single', allow_reordering=True, height=140)
                            gr_ebook_mode = gr.Radio(label='', elem_id='gr_ebook_mode', choices=[('File','single'), ('Directory','directory')], value='single', interactive=True)
                        with gr.Group():
                            gr_language = gr.Dropdown(label='Language', elem_id='gr_language', choices=language_options, value=default_language_code, type='value', interactive=True)
                        gr_group_voice_file = gr.Group(elem_id='gr_group_voice_file', visible=visible_gr_group_voice_file)
                        with gr_group_voice_file:
                            gr_voice_file = gr.File(label='*Cloning Voice Audio Fiie', elem_id='gr_voice_file', file_types=voice_formats, value=None, height=140)
                            gr_row_voice_player = gr.Row(elem_id='gr_row_voice_player')
                            with gr_row_voice_player:
                                gr_voice_player = gr.Audio(elem_id='gr_voice_player', type='filepath', interactive=False, show_download_button=False, container=False, visible=False, show_share_button=False, show_label=False, waveform_options=gr.WaveformOptions(show_controls=False), scale=0, min_width=60)
                                gr_voice_list = gr.Dropdown(label='', elem_id='gr_voice_list', choices=voice_options, type='value', interactive=True, scale=2)
                                gr_voice_del_btn = gr.Button('🗑', elem_id='gr_voice_del_btn', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                            gr.Markdown('<p>&nbsp;&nbsp;* Optional</p>')
                        with gr.Group():
                            gr_device = gr.Radio(label='Processor Unit', elem_id='gr_device', choices=[('CPU','cpu'), ('GPU','cuda'), ('MPS','mps')], value=default_device)
                    with gr.Column(scale=3):
                        with gr.Group():
                            gr_tts_engine_list = gr.Dropdown(label='TTS Engine', elem_id='gr_tts_engine_list', choices=tts_engine_options, type='value', interactive=True)
                            gr_tts_rating = gr.HTML()
                            gr_fine_tuned_list = gr.Dropdown(label='Fine Tuned Models (Presets)', elem_id='gr_fine_tuned_list', choices=fine_tuned_options, type='value', interactive=True)
                            gr_group_custom_model = gr.Group(visible=visible_gr_group_custom_model)
                            with gr_group_custom_model:
                                gr_custom_model_file = gr.File(label=f"Upload Fine Tuned Model", elem_id='gr_custom_model_file', value=None, file_types=['.zip'], height=140)
                                with gr.Row():
                                    gr_custom_model_list = gr.Dropdown(label='', elem_id='gr_custom_model_list', choices=custom_model_options, type='value', interactive=True, scale=2)
                                    gr_custom_model_del_btn = gr.Button('🗑', elem_id='gr_custom_model_del_btn', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                                gr_custom_model_markdown = gr.Markdown('<p>&nbsp;&nbsp;* Optional</p>')
                        with gr.Group():
                            gr_session = gr.Textbox(label='Session', elem_id='gr_session', interactive=False)
                        gr_output_format_list = gr.Dropdown(label='Output format', elem_id='gr_output_format_list', choices=output_formats, type='value', value=default_output_format, interactive=True)
            gr_tab_xtts_params = gr.TabItem('XTTSv2 Fine Tuned Parameters', elem_classes='tab_item', visible=visible_gr_tab_xtts_params)           
            with gr_tab_xtts_params:
                gr.Markdown(
                    '''
                    ### Customize XTTSv2 Parameters
                    Adjust the settings below to influence how the audio is generated. You can control the creativity, speed, repetition, and more.
                    '''
                )
                gr_xtts_temperature = gr.Slider(
                    label='Temperature',
                    minimum=0.1,
                    maximum=10.0,
                    step=0.1,
                    value=float(default_engine_settings[TTS_ENGINES['XTTSv2']]['temperature']),
                    elem_id='gr_xtts_temperature',
                    info='Higher values lead to more creative, unpredictable outputs. Lower values make it more monotone.'
                )
                gr_xtts_length_penalty = gr.Slider(
                    label='Length Penalty',
                    minimum=0.3,
                    maximum=5.0,
                    step=0.1,
                    value=float(default_engine_settings[TTS_ENGINES['XTTSv2']]['length_penalty']),
                    elem_id='gr_xtts_length_penalty',
                    info='Adjusts how much longer sequences are preferred. Higher values encourage the model to produce longer and more natural speech.',
                    visible=False
                )
                gr_xtts_num_beams = gr.Slider(
                    label='Number Beams',
                    minimum=1,
                    maximum=10,
                    step=1,
                    value=int(default_engine_settings[TTS_ENGINES['XTTSv2']]['num_beams']),
                    elem_id='gr_xtts_num_beams',
                    info='Controls how many alternative sequences the model explores. Higher values improve speech coherence and pronunciation but increase inference time.',
                    visible=False
                )
                gr_xtts_repetition_penalty = gr.Slider(
                    label='Repetition Penalty',
                    minimum=1.0,
                    maximum=10.0,
                    step=0.1,
                    value=float(default_engine_settings[TTS_ENGINES['XTTSv2']]['repetition_penalty']),
                    elem_id='gr_xtts_repetition_penalty',
                    info='Penalizes repeated phrases. Higher values reduce repetition.'
                )
                gr_xtts_top_k = gr.Slider(
                    label='Top-k Sampling',
                    minimum=10,
                    maximum=100,
                    step=1,
                    value=int(default_engine_settings[TTS_ENGINES['XTTSv2']]['top_k']),
                    elem_id='gr_xtts_top_k',
                    info='Lower values restrict outputs to more likely words and increase speed at which audio generates.'
                )
                gr_xtts_top_p = gr.Slider(
                    label='Top-p Sampling',
                    minimum=0.1,
                    maximum=1.0, 
                    step=0.01,
                    value=float(default_engine_settings[TTS_ENGINES['XTTSv2']]['top_p']),
                    elem_id='gr_xtts_top_p',
                    info='Controls cumulative probability for word selection. Lower values make the output more predictable and increase speed at which audio generates.'
                )
                gr_xtts_speed = gr.Slider(
                    label='Speed', 
                    minimum=0.5, 
                    maximum=3.0, 
                    step=0.1, 
                    value=float(default_engine_settings[TTS_ENGINES['XTTSv2']]['speed']),
                    elem_id='gr_xtts_speed',
                    info='Adjusts how fast the narrator will speak.'
                )
                gr_xtts_enable_text_splitting = gr.Checkbox(
                    label='Enable Text Splitting', 
                    value=default_engine_settings[TTS_ENGINES['XTTSv2']]['enable_text_splitting'],
                    elem_id='gr_xtts_enable_text_splitting',
                    info='Coqui-tts builtin text splitting. Can help against hallucinations bu can also be worse.',
                    visible=False
                )
            gr_tab_bark_params = gr.TabItem('BARK fine Tuned Parameters', elem_classes='tab_item', visible=visible_gr_tab_bark_params)           
            with gr_tab_bark_params:
                gr.Markdown(
                    '''
                    ### Customize BARK Parameters
                    Adjust the settings below to influence how the audio is generated, emotional and voice behavior random or more conservative
                    '''
                )
                gr_bark_text_temp = gr.Slider(
                    label='Text Temperature', 
                    minimum=0.0,
                    maximum=1.0,
                    step=0.01,
                    value=float(default_engine_settings[TTS_ENGINES['BARK']]['text_temp']),
                    elem_id='gr_bark_text_temp',
                    info='Higher values lead to more creative, unpredictable outputs. Lower values make it more conservative.'
                )
                gr_bark_waveform_temp = gr.Slider(
                    label='Waveform Temperature', 
                    minimum=0.0,
                    maximum=1.0,
                    step=0.01,
                    value=float(default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp']),
                    elem_id='gr_bark_waveform_temp',
                    info='Higher values lead to more creative, unpredictable outputs. Lower values make it more conservative.'
                )
        gr_state = gr.State(value={"hash": None})
        gr_state_alert = gr.State(value={"type": None,"msg": None})
        gr_read_data = gr.JSON(visible=False)
        gr_write_data = gr.JSON(visible=False)
        gr_conversion_progress = gr.Textbox(label='Progress', elem_id="conversion_progress_bar")
        gr_group_audiobook_list = gr.Group(visible=False)
        with gr_group_audiobook_list:
            gr_audiobook_text = gr.Textbox(label='Audiobook', elem_id='gr_audiobook_text', interactive=False, visible=True)
            gr_audiobook_player = gr.Audio(label='', elem_id='gr_audiobook_player', type='filepath', waveform_options=gr.WaveformOptions(show_recording_waveform=False), show_download_button=False, show_share_button=False, container=True, interactive=False, visible=True)
            with gr.Row():
                gr_audiobook_download_btn = gr.DownloadButton('↧', elem_id='gr_audiobook_download_btn', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=True, scale=0, min_width=60)
                gr_audiobook_list = gr.Dropdown(label='', elem_id='gr_audiobook_list', choices=audiobook_options, type='value', interactive=True, visible=True, scale=2)
                gr_audiobook_del_btn = gr.Button('🗑', elem_id='gr_audiobook_del_btn', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=True, scale=0, min_width=60)
        gr_convert_btn = gr.Button('📚', elem_id='gr_convert_btn', elem_classes='icon-btn', variant='primary', interactive=False)
        
        gr_modal = gr.HTML(visible=False)
        gr_confirm_field_hidden = gr.Textbox(elem_id='confirm_hidden', visible=False)
        gr_confirm_yes_btn_hidden = gr.Button('', elem_id='confirm_yes_btn_hidden', visible=False)
        gr_confirm_no_btn_hidden = gr.Button('', elem_id='confirm_no_btn_hidden', visible=False)

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

        def show_rating(tts_engine):
            if tts_engine == TTS_ENGINES['XTTSv2']:
                rating = default_engine_settings[TTS_ENGINES['XTTSv2']]['rating']
            elif tts_engine == TTS_ENGINES['BARK']:
                rating = default_engine_settings[TTS_ENGINES['BARK']]['rating']
            elif tts_engine == TTS_ENGINES['VITS']:
                rating = default_engine_settings[TTS_ENGINES['VITS']]['rating']
            elif tts_engine == TTS_ENGINES['FAIRSEQ']:
                rating = default_engine_settings[TTS_ENGINES['FAIRSEQ']]['rating']
            elif tts_engine == TTS_ENGINES['TACOTRON2']:
                rating = default_engine_settings[TTS_ENGINES['TACOTRON2']]['rating']
            elif tts_engine == TTS_ENGINES['YOURTTS']:
                rating = default_engine_settings[TTS_ENGINES['YOURTTS']]['rating']
            def yellow_stars(n):
                return "".join(
                    "<span style='color:#FFD700;font-size:12px'>★</span>" for _ in range(n)
                )
            def color_box(value):
                if value <= 4:
                    color = "#4CAF50"  # Green = low
                elif value <= 8:
                    color = "#FF9800"  # Orange = medium
                else:
                    color = "#F44336"  # Red = high
                return f"<span style='background:{color};color:white;padding:1px 5px;border-radius:3px;font-size:11px'>{value} GB</span>"
            return f"""
            <div style='margin:0; padding:0; font-size:12px; line-height:0; height:auto; display:inline; border: none; gap:0px; align-items:center'>
                <span style='padding:0 10px'><b>GPU VRAM:</b> {color_box(rating["GPU VRAM"])}</span>
                <span style='padding:0 10px'><b>CPU:</b> {yellow_stars(rating["CPU"])}</span>
                <span style='padding:0 10px'><b>RAM:</b> {color_box(rating["RAM"])}</span>
                <span style='padding:0 10px'><b>Realism:</b> {yellow_stars(rating["Realism"])}</span>
            </div>
            """

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
            ### XTTSv2 Params
            session['temperature'] = session['temperature'] if session['temperature'] else default_engine_settings[TTS_ENGINES['XTTSv2']]['temperature']
            session['length_penalty'] = default_engine_settings[TTS_ENGINES['XTTSv2']]['length_penalty']
            session['num_beams'] = default_engine_settings[TTS_ENGINES['XTTSv2']]['num_beams']
            session['repetition_penalty'] = session['repetition_penalty'] if session['repetition_penalty'] else default_engine_settings[TTS_ENGINES['XTTSv2']]['repetition_penalty']
            session['top_k'] = session['top_k'] if session['top_k'] else default_engine_settings[TTS_ENGINES['XTTSv2']]['top_k']
            session['top_p'] = session['top_p'] if session['top_p'] else default_engine_settings[TTS_ENGINES['XTTSv2']]['top_p']
            session['speed'] = session['speed'] if session['speed'] else default_engine_settings[TTS_ENGINES['XTTSv2']]['speed']
            session['enable_text_splitting'] = default_engine_settings[TTS_ENGINES['XTTSv2']]['enable_text_splitting']
            ### BARK Params
            session['text_temp'] = session['text_temp'] if session['text_temp'] else default_engine_settings[TTS_ENGINES['BARK']]['text_temp']
            session['waveform_temp'] = session['waveform_temp'] if session['waveform_temp'] else default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp']
            return (
                gr.update(value=ebook_data), gr.update(value=session['ebook_mode']), gr.update(value=session['device']),
                gr.update(value=session['language']), update_gr_voice_list(id), update_gr_tts_engine_list(id), update_gr_custom_model_list(id),
                update_gr_fine_tuned_list(id), gr.update(value=session['output_format']), update_gr_audiobook_list(id),
                gr.update(value=float(session['temperature'])), gr.update(value=float(session['length_penalty'])), gr.update(value=int(session['num_beams'])),
                gr.update(value=float(session['repetition_penalty'])), gr.update(value=int(session['top_k'])), gr.update(value=float(session['top_p'])), gr.update(value=float(session['speed'])), 
                gr.update(value=bool(session['enable_text_splitting'])), gr.update(value=float(session['text_temp'])), gr.update(value=float(session['waveform_temp'])), gr.update(active=True)
            )

        def refresh_interface(id):
            session = context.get_session(id)
            session['status'] = None
            return gr.update(interactive=False), gr.update(value=None), update_gr_voice_list(id), update_gr_audiobook_list(id), gr.update(value=session['audiobook']), gr.update(visible=False)

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
                    final_voice_file = os.path.join(session['voice_dir'], f'{voice_name}_24000.wav')
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
                    speaker = re.sub(r'_(24000|16000)\.wav$|\.npz$', '', os.path.basename(selected))
                    if speaker in default_engine_settings[TTS_ENGINES['XTTSv2']]['voices'].keys() or speaker in default_engine_settings[TTS_ENGINES['BARK']]['voices'].keys() or speaker in default_engine_settings[TTS_ENGINES['YOURTTS']]['voices'].keys():
                        error = f'Voice file {speaker} is a builtin voice and cannot be deleted.'
                        show_alert({"type": "warning", "msg": error})
                    else:
                        try:
                            session = context.get_session(id)
                            selected_path = Path(selected).resolve()
                            parent_path = Path(session['voice_dir']).parent.resolve()
                            if parent_path in selected_path.parents:
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

        def confirm_deletion(voice_path, custom_model, audiobook, id, method=None):
            try:
                if method is not None:
                    session = context.get_session(id)
                    if method == 'confirm_voice_del':
                        selected_name = os.path.basename(voice_path)
                        pattern = re.sub(r'_(24000|16000)\.wav$', '_*.wav', voice_path)
                        files2remove = glob(pattern)
                        for file in files2remove:
                            os.remove(file)
                        shutil.rmtree(os.path.join(os.path.dirname(voice_path), 'bark', selected_name), ignore_errors=True)
                        msg = f"Voice file {re.sub(r'_(24000|16000).wav$', '', selected_name)} deleted!"
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
                lang_dir = session['language'] if session['language'] != 'con' else 'con-'  # Bypass Windows CON reserved name
                file_pattern = "*_24000.wav"
                eng_options = []
                bark_options = []
                builtin_options = [
                    (os.path.splitext(re.sub(r'_24000\.wav$', '', f.name))[0], str(f))
                    for f in Path(os.path.join(voices_dir, lang_dir)).rglob(file_pattern)
                ]
                if session['language'] in language_tts[TTS_ENGINES['XTTSv2']]:
                    eng_options = [
                        (os.path.splitext(re.sub(r'_24000\.wav$', '', f.name))[0], str(f))
                        for f in Path(os.path.join(voices_dir, 'eng')).rglob(file_pattern)
                    ]
                if session['tts_engine'] == TTS_ENGINES['BARK']:
                    lang_array = languages.get(part3=session['language'])
                    if lang_array:
                        lang_iso1 = lang_array.part1 
                        lang = lang_iso1.lower()
                        speakers_path = Path(default_engine_settings[TTS_ENGINES['BARK']]['speakers_path'])
                        bark_options = [
                            (
                                re.sub(r"^.*?_speaker_(\d+)$", r"Speaker \1", f.stem),
                                str(f.with_suffix(".wav"))
                            )
                            for f in speakers_path.rglob(f"{lang}_speaker_*.npz")
                        ]
                keys = {key for key, _ in builtin_options}
                voice_options = builtin_options + [row for row in eng_options if row[0] not in keys]
                voice_options += bark_options
                if session['voice_dir'] is not None:
                    parent_dir = Path(session['voice_dir']).parent
                    voice_options += [
                        (
                            os.path.splitext(re.sub(r'_24000\.wav$', '', f.name))[0],
                            str(f)
                        )
                        for f in parent_dir.rglob(file_pattern)
                        if f.is_file()
                    ]
                if session['tts_engine'] in [TTS_ENGINES['VITS'], TTS_ENGINES['FAIRSEQ'], TTS_ENGINES['TACOTRON2'], TTS_ENGINES['YOURTTS']]:
                    voice_options = [('Default', None)] + sorted(voice_options, key=lambda x: x[0].lower())
                else:
                    if session['voice'] is None:
                        session['voice'] = models[session['tts_engine']][session['fine_tuned']]['voice']
                    voice_options = sorted(voice_options, key=lambda x: x[0].lower())
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
                    (
                        str(dir),
                        os.path.join(custom_model_tts_dir, dir)
                    )
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
            previous = session['language']
            new = default_language_code if selected == 'zzz' else selected
            session['voice_dir'] = re.sub(rf'([\\/]){re.escape(previous)}$', rf'\1{new}', session['voice_dir'])
            session['language'] = new
            os.makedirs(session['voice_dir'], exist_ok=True)
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
            bark_visible = False
            if session['tts_engine'] == TTS_ENGINES['XTTSv2']:
                visible_custom_model = True
                if session['fine_tuned'] != 'internal':
                    visible_custom_model = False
                return (
                       gr.update(value=show_rating(session['tts_engine'])), 
                       gr.update(visible=visible_gr_tab_xtts_params), gr.update(visible=False), update_gr_voice_list(id), gr.update(visible=visible_custom_model), update_gr_fine_tuned_list(id),
                       gr.update(label=f"*Upload {session['tts_engine']} Model (Should be a ZIP file with {', '.join(models[session['tts_engine']][default_fine_tuned]['files'])})"),
                       gr.update(label=f"My {session['tts_engine']} custom models")
                )
            else:
                if session['tts_engine'] == TTS_ENGINES['BARK']:
                    bark_visible = visible_gr_tab_bark_params
                return gr.update(value=show_rating(session['tts_engine'])), gr.update(visible=False), gr.update(visible=bark_visible), update_gr_voice_list(id), gr.update(visible=False), update_gr_fine_tuned_list(id), gr.update(label=f"*Upload Fine Tuned Model not available for {session['tts_engine']}"), gr.update(label='')
                
        def change_gr_fine_tuned_list(selected, id):
            session = context.get_session(id)
            visible = False
            if session['tts_engine'] == TTS_ENGINES['XTTSv2']:
                if selected == 'internal':
                    visible = visible_gr_group_custom_model
            session['fine_tuned'] = selected
            session['voice'] = models[session['tts_engine']][session['fine_tuned']]['voice']
            return update_gr_voice_list(id), gr.update(visible=visible)

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

        def submit_convert_btn(id, device, ebook_file, tts_engine, voice, language, custom_model, fine_tuned, output_format, temperature, length_penalty, num_beams, repetition_penalty, top_k, top_p, speed, enable_text_splitting, text_temp, waveform_temp):
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
                    "num_beams": session['num_beams'],
                    "repetition_penalty": float(repetition_penalty),
                    "top_k": int(top_k),
                    "top_p": float(top_p),
                    "speed": float(speed),
                    "enable_text_splitting": enable_text_splitting,
                    "text_temp": float(text_temp),
                    "waveform_temp": float(waveform_temp),
                    "fine_tuned": fine_tuned
                }
                error = None
                if args['ebook'] is None and args['ebook_list'] is None:
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
                session['voice_dir'] = os.path.join(voices_dir, '__sessions', f"voice-{session['id']}", session['language'])
                os.makedirs(session['custom_model_dir'], exist_ok=True)
                os.makedirs(session['voice_dir'], exist_ok=True)
                # As now uploaded voice files are in their respective language folder so check if no wav and bark folder are on the voice_dir root from previous versions
                [shutil.move(src, os.path.join(session['voice_dir'], os.path.basename(src))) for src in glob(os.path.join(os.path.dirname(session['voice_dir']), '*.wav')) + ([os.path.join(os.path.dirname(session['voice_dir']), 'bark')] if os.path.isdir(os.path.join(os.path.dirname(session['voice_dir']), 'bark')) and not os.path.exists(os.path.join(session['voice_dir'], 'bark')) else [])]                
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
                session_dict = proxy2dict(session)
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
                                    session_dict = proxy2dict(session)
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
            outputs=[gr_tts_rating, gr_tab_xtts_params, gr_tab_bark_params, gr_voice_list, gr_group_custom_model, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list] 
        )
        gr_fine_tuned_list.change(
            fn=change_gr_fine_tuned_list,
            inputs=[gr_fine_tuned_list, gr_session],
            outputs=[gr_voice_list, gr_group_custom_model]
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
        ).then(
            fn=None,
            js="()=>window.redraw_audiobook_player()"
        )
        gr_audiobook_del_btn.click(
            fn=click_gr_audiobook_del_btn,
            inputs=[gr_audiobook_list, gr_session],
            outputs=[gr_confirm_field_hidden, gr_modal]
        )
        ########### XTTSv2 Params
        gr_xtts_temperature.change(
            fn=lambda val, id: change_param('temperature', val, id),
            inputs=[gr_xtts_temperature, gr_session],
            outputs=None
        )
        gr_xtts_length_penalty.change(
            fn=lambda val, id, val2: change_param('length_penalty', val, id, val2),
            inputs=[gr_xtts_length_penalty, gr_session, gr_xtts_num_beams],
            outputs=None,
        )
        gr_xtts_num_beams.change(
            fn=lambda val, id, val2: change_param('num_beams', val, id, val2),
            inputs=[gr_xtts_num_beams, gr_session, gr_xtts_length_penalty],
            outputs=None,
        )
        gr_xtts_repetition_penalty.change(
            fn=lambda val, id: change_param('repetition_penalty', val, id),
            inputs=[gr_xtts_repetition_penalty, gr_session],
            outputs=None
        )
        gr_xtts_top_k.change(
            fn=lambda val, id: change_param('top_k', val, id),
            inputs=[gr_xtts_top_k, gr_session],
            outputs=None
        )
        gr_xtts_top_p.change(
            fn=lambda val, id: change_param('top_p', val, id),
            inputs=[gr_xtts_top_p, gr_session],
            outputs=None
        )
        gr_xtts_speed.change(
            fn=lambda val, id: change_param('speed', val, id),
            inputs=[gr_xtts_speed, gr_session],
            outputs=None
        )
        gr_xtts_enable_text_splitting.change(
            fn=lambda val, id: change_param('enable_text_splitting', val, id),
            inputs=[gr_xtts_enable_text_splitting, gr_session],
            outputs=None
        )
        ########### BARK Params
        gr_bark_text_temp.change(
            fn=lambda val, id: change_param('text_temp', val, id),
            inputs=[gr_bark_text_temp, gr_session],
            outputs=None
        )
        gr_bark_waveform_temp.change(
            fn=lambda val, id: change_param('waveform_temp', val, id),
            inputs=[gr_bark_waveform_temp, gr_session],
            outputs=None
        )
        ############ Timer to save session to localStorage
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
                gr_custom_model_list, gr_fine_tuned_list, gr_output_format_list, 
                gr_xtts_temperature, gr_xtts_length_penalty, gr_xtts_num_beams, gr_xtts_repetition_penalty, gr_xtts_top_k, gr_xtts_top_p, gr_xtts_speed, gr_xtts_enable_text_splitting,
                gr_bark_text_temp, gr_bark_waveform_temp
            ],
            outputs=[gr_conversion_progress]
        ).then(
            fn=refresh_interface,
            inputs=[gr_session],
            outputs=[gr_convert_btn, gr_ebook_file, gr_voice_list, gr_audiobook_list, gr_audiobook_player, gr_modal]
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
                gr_xtts_temperature, gr_xtts_length_penalty, gr_xtts_num_beams, gr_xtts_repetition_penalty,
                gr_xtts_top_k, gr_xtts_top_p, gr_xtts_speed, gr_xtts_enable_text_splitting, gr_bark_text_temp, gr_bark_waveform_temp, gr_timer
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
            js="""
            () => {
                // Define the global function ONCE
                if (typeof window.redraw_audiobook_player !== 'function') {
                    window.redraw_audiobook_player = () => {
                        try {
                            const audio = document.querySelector('#gr_audiobook_player audio');
                            if (audio) {
                                const url = new URL(window.location);
                                const theme = url.searchParams.get('__theme');
                                let osTheme;
                                let audioFilter = '';
                                if (theme) {
                                    if (theme === 'dark') {
                                        audioFilter = 'invert(1) hue-rotate(180deg)';
                                    } 
                                } else {
                                    osTheme = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
                                    if (osTheme) {
                                        audioFilter = 'invert(1) hue-rotate(180deg)';
                                    }
                                }
                                if (!audio.style.transition) {
                                    audio.style.transition = 'filter 1s ease';
                                }
                                audio.style.filter = audioFilter;
                            }
                        } catch (e) {
                            console.log('redraw_audiobook_player error:', e);
                        }
                    };
                }

                // Now safely call it after the audio element is available
                const tryRun = () => {
                    const audio = document.querySelector('#gr_audiobook_player audio');
                    if (audio && typeof window.redraw_audiobook_player === 'function') {
                        window.redraw_audiobook_player();
                    } else {
                        setTimeout(tryRun, 100);
                    }
                };
                tryRun();

                // Return localStorage data if needed
                try {
                    const data = window.localStorage.getItem('data');
                    if (data) return JSON.parse(data);
                } catch (e) {
                    console.log("JSON parse error:", e);
                }

                return null;
            }
            """,
            outputs=[gr_read_data]
        )
    try:
        all_ips = get_all_ip_addresses()
        msg = f'IPs available for connection:\n{all_ips}\nNote: 0.0.0.0 is not the IP to connect. Instead use an IP above to connect.'
        show_alert({"type": "info", "msg": msg})
        os.environ['no_proxy'] = ' ,'.join(all_ips)
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
