# NOTE!!NOTE!!!NOTE!!NOTE!!!NOTE!!NOTE!!!NOTE!!NOTE!!!
# THE WORD "CHAPTER" IN THE CODE DOES NOT MEAN
# IT'S THE REAL CHAPTER OF THE EBOOK SINCE NO STANDARDS
# ARE DEFINING A CHAPTER ON .EPUB FORMAT. THE WORD "BLOCK"
# IS USED TO PRINT IT OUT TO THE TERMINAL, AND "CHAPTER" TO THE CODE
# WHICH IS LESS GENERIC FOR THE DEVELOPERS

import argparse, asyncio, csv, fnmatch, hashlib, io, json, math, os, pytesseract, gc
import random, shutil, subprocess, sys, tempfile, threading, time, uvicorn
import traceback, socket, unicodedata, urllib.request, uuid, zipfile, fitz, multiprocessing
import ebooklib, gradio as gr, psutil, regex as re, requests, stanza, importlib, queue

from typing import Any, Generator, Dict
from PIL import Image, ImageSequence
from tqdm import tqdm
from bs4 import BeautifulSoup, NavigableString, Tag
from collections import Counter
from collections.abc import Mapping, MutableMapping
from datetime import datetime
from ebooklib import epub
from ebooklib.epub import EpubBook
from ebooklib.epub import EpubHtml
from glob import glob
from iso639 import Lang
from markdown import markdown
from multiprocessing import Pool, cpu_count
from multiprocessing import Manager, Event
from multiprocessing.managers import DictProxy, ListProxy, SyncManager
from stanza.pipeline.core import Pipeline, DownloadMethod
from num2words import num2words
from pathlib import Path
from PIL import Image
from pydub import AudioSegment
from pydub.utils import mediainfo
from queue import Queue, Empty
from types import MappingProxyType
from langdetect import detect
from unidecode import unidecode
from phonemizer import phonemize

from lib.classes.subprocess_pipe import SubprocessPipe
from lib.classes.vram_detector import VRAMDetector
from lib.classes.voice_extractor import VoiceExtractor
from lib.classes.tts_manager import TTSManager
#from lib.classes.redirect_console import RedirectConsole
#from lib.classes.argos_translator import ArgosTranslator
from lib.classes.tts_engines.common.audio import get_audiolist_duration, get_audio_duration

from lib import *

#import logging
#logging.basicConfig(
#    level=logging.INFO, # DEBUG for more verbosity
#    format="%(asctime)s [%(levelname)s] %(message)s"
#)

context = None
context_tracker = None
active_sessions = None

class DependencyError(Exception):
    def __init__(self, message:str|None):
        super().__init__(message)
        print(message)
        # Automatically handle the exception when it's raised
        self.handle_exception()

    def handle_exception(self)->None:
        # Print the full traceback of the exception
        traceback.print_exc()      
        # Print the exception message
        error = f'Caught DependencyError: {self}'
        print(error)

class SessionTracker:
    def __init__(self):
        self.lock = threading.Lock()

    def start_session(self, session_id:str)->bool:
        with self.lock:
            session = context.get_session(session_id)
            if session['status'] is None:
                session['status'] = 'ready'
                return True
        return False

    def end_session(self, session_id:str, socket_hash:str)->None:
        active_sessions.discard(socket_hash)
        with self.lock:
            context.sessions.pop(session_id, None)

class SessionContext:
    def __init__(self):
        self.manager:Manager = Manager()
        self.sessions:DictProxy[str, DictProxy[str, Any]] = self.manager.dict()
        self.cancellation_events = {}

    def _recursive_proxy(self, data:Any, manager:SyncManager|None)->Any:
        if manager is None:
            manager = self.manager
        if isinstance(data, dict):
            proxy_dict = manager.dict()
            for key, value in data.items():
                proxy_dict[key] = self._recursive_proxy(value, manager)
            return proxy_dict
        elif isinstance(data, list):
            proxy_list = manager.list()
            for item in data:
                proxy_list.append(self._recursive_proxy(item, manager))
            return proxy_list
        elif isinstance(data, (str, int, float, bool, type(None))):
            return data
        else:
            error = f'Unsupported data type: {type(data)}'
            print(error)
            return None

    def set_session(self, session_id:str)->Any:
        self.sessions[session_id] = self._recursive_proxy({
            "id": session_id,
            "script_mode": NATIVE,
            "tab_id": None,
            "is_gui_process": False,
            "free_vram_gb": 0,
            "process_id": None,
            "status": None,
            "event": None,
            "ticker": 0,
            "heartbeat": time.time(),
            "cancellation_requested": False,
            "device": default_device,
            "tts_engine": default_tts_engine,
            "fine_tuned": default_fine_tuned,
            "model_cache": None,
            "model_zs_cache": None,
            "stanza_cache": None,
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
            "chapters_preview": default_chapters_preview,
            "chapters_dir": None,
            "sentences_dir": None,
            "epub_path": None,
            "filename_noext": None,
            "voice": None,
            "voice_dir": None,
            "custom_model": None,
            "custom_model_dir": None,
            "xtts_temperature": default_engine_settings[TTS_ENGINES['XTTSv2']]['temperature'],
            #"xtts_codec_temperature": default_engine_settings[TTS_ENGINES['XTTSv2']]['codec_temperature'],
            "xtts_length_penalty": default_engine_settings[TTS_ENGINES['XTTSv2']]['length_penalty'],
            "xtts_num_beams": default_engine_settings[TTS_ENGINES['XTTSv2']]['num_beams'],
            "xtts_repetition_penalty": default_engine_settings[TTS_ENGINES['XTTSv2']]['repetition_penalty'],
            #"xtts_cvvp_weight": default_engine_settings[TTS_ENGINES['XTTSv2']]['cvvp_weight'],
            "xtts_top_k": default_engine_settings[TTS_ENGINES['XTTSv2']]['top_k'],
            "xtts_top_p": default_engine_settings[TTS_ENGINES['XTTSv2']]['top_p'],
            "xtts_speed": default_engine_settings[TTS_ENGINES['XTTSv2']]['speed'],
            #"xtts_gpt_cond_len": default_engine_settings[TTS_ENGINES['XTTSv2']]['gpt_cond_len'],
            #"xtts_gpt_batch_size": default_engine_settings[TTS_ENGINES['XTTSv2']]['gpt_batch_size'],
            "xtts_enable_text_splitting": default_engine_settings[TTS_ENGINES['XTTSv2']]['enable_text_splitting'],
            "bark_text_temp": default_engine_settings[TTS_ENGINES['BARK']]['text_temp'],
            "bark_waveform_temp": default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp'],
            "final_name": None,
            "output_format": default_output_format,
            "output_channel": default_output_channel,
            "output_split": default_output_split,
            "output_split_hours": default_output_split_hours,
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
            },
            "blocks": [],
            "chapters": [],
            "cover": None,
            "duration": 0,
            "playback_time": 0,
            "playback_volume": 0
        }, manager=self.manager)
        return self.sessions[session_id]

    def get_session(self, session_id:str)->Any:
        if session_id in self.sessions:
            return self.sessions[session_id]
        return {}

    def find_id_by_hash(self, socket_hash: str) -> str | None:
        for session_id, session in list(self.sessions.items()):
            if socket_hash in session:
                return session_id
        return None

class JSONDictProxyEncoder(json.JSONEncoder):
    def default(self, o:Any)->Any:
        if isinstance(o, DictProxy):
            return dict(o)
        elif isinstance(o, ListProxy):
            return list(o)
        return super().default(o)

def prepare_dirs(src:str, session_id:str)->bool:
    try:
        session = context.get_session(session_id)
        if session and session.get('id', False):
            resume = False
            os.makedirs(os.path.join(models_dir,'tts'), exist_ok=True)
            os.makedirs(session['session_dir'], exist_ok=True)
            os.makedirs(session['process_dir'], exist_ok=True)
            os.makedirs(session['custom_model_dir'], exist_ok=True)
            os.makedirs(session['voice_dir'], exist_ok=True)
            os.makedirs(session['audiobooks_dir'], exist_ok=True)
            os.makedirs(session['chapters_dir'], exist_ok=True)
            os.makedirs(session['sentences_dir'], exist_ok=True)
            session['ebook'] = os.path.join(session['process_dir'], os.path.basename(src))
            shutil.copy(src, session['ebook'])
            return True
    except Exception as e:
        DependencyError(e)
        return False

def check_programs(prog_name:str, command:str, options:str)->bool:
    try:
        subprocess.run(
            [command, options],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=True,
            text=True,
            encoding='utf-8'
        )
        return True
    except FileNotFoundError:
        e = f'''********** Error: {prog_name} is not installed! if your OS calibre package version 
        is not compatible you still can run ebook2audiobook.sh (linux/mac) or ebook2audiobook.cmd (windows) **********'''
        DependencyError(e)
    except subprocess.CalledProcessError:
        e = f'Error: There was an issue running {prog_name}.'
        DependencyError(e)
    return False

def analyze_uploaded_file(zip_path:str, required_files:list[str])->bool:
    try:
        if not os.path.exists(zip_path):
            error = f'The file does not exist: {os.path.basename(zip_path)}'
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
            msg = f'Missing required files: {missing_files}'
            print(msg)
        if required_empty_files:
            msg = f'Required files with 0 KB: {required_empty_files}'
            print(msg)
        return not missing_files and not required_empty_files
    except zipfile.BadZipFile:
        error = 'The file is not a valid ZIP archive.'
        print(error)
        return False
    except Exception as e:
        error = f'An error occurred: {e}'
        print(error)
        return False

def extract_custom_model(session_id)->str|None:
    session = context.get_session(session_id)
    if session and session.get('id', False):
        file_src = session['custom_model']
        required_files = default_engine_settings[session['tts_engine']]['files']
        model_path = None
        model_name = re.sub('.zip', '', os.path.basename(file_src), flags=re.IGNORECASE)
        model_name = get_sanitized(model_name)
        if session['is_gui_process']:
            progress_bar = gr.Progress(track_tqdm=False)
        try:
            with zipfile.ZipFile(file_src, 'r') as zip_ref:
                files = zip_ref.namelist()
                files_length = len(files)
                tts_dir = session['tts_engine']
                model_path = os.path.join(session['custom_model_dir'], tts_dir, model_name)
                os.makedirs(model_path, exist_ok=True)
                required_files_lc = set(x.lower() for x in required_files)
                msg = f'Extracting files to {model_path}...'
                with tqdm(total=files_length, unit='files') as t:
                    for f in files:
                        base_f = os.path.basename(f).lower()
                        if base_f in required_files_lc:
                            out_path = os.path.join(model_path, base_f)
                            with zip_ref.open(f) as src, open(out_path, 'wb') as dst:
                                shutil.copyfileobj(src, dst)
                        t.update(1)
                        if session['is_gui_process']:
                            progress_bar((t.n + 1) / files_length, desc=msg)
            if model_path is not None:
                msg = f'Normalizing ref.wav…'
                print(msg)
                voice_ref = os.path.join(model_path, 'ref.wav')
                voice_name = model_name
                final_voice_file = os.path.join(model_path, f'{voice_name}.wav')
                extractor = VoiceExtractor(session, voice_ref, voice_name, final_voice_file)
                status, msg = extractor.extract_voice()
                if status:
                    session['voice'] = final_voice_file
                    if os.path.exists(file_src):
                        os.remove(file_src)
                    if os.path.exists(voice_ref):
                        os.remove(voice_ref)
                    return model_path
                else:
                    error = f'extract_custom_model() VoiceExtractor.extract_voice() error! {msg}'
                    print(error)
            else:
                error = f'An error occurred     when unzip {file_src}'
                print(error)
        except asyncio.exceptions.CancelledError as e:
            DependencyError(e)
            error = f'extract_custom_model asyncio.exceptions.CancelledError: {e}'
            print(error)
        except Exception as e:
            DependencyError(e)
            error = f'extract_custom_model Exception: {e}'
            print(error)
        if session['is_gui_process']:
            if os.path.exists(file_src):
                os.remove(file_src)
        session['custom_model'] = None
    return None
        
def hash_proxy_dict(proxy_dict)->str:
    try:
        data = dict(proxy_dict)
    except Exception:
        data = {}
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode("utf-8")).hexdigest()

def compare_checksums(src_path:str, checksum_path:str, hash_algorithm:str='sha256')->tuple[bool, str|None]:
    try:
        hash_func = hashlib.new(hash_algorithm)
        with open(src_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        new_checksum = hash_func.hexdigest()
        if not os.path.exists(checksum_path):
            with open(checksum_path, 'w', encoding='utf-8') as f:
                f.write(new_checksum)
            return False, None
        else:
            with open(checksum_path, 'r', encoding='utf-8') as f:
                saved_checksum = f.read().strip()
            if saved_checksum == new_checksum:
                return True, None
            else:
                with open(checksum_path, 'w', encoding='utf-8') as f:
                    f.write(new_checksum)
                    return False, None
    except Exception as e:
        return False, f'compare_checksums() error: {e}'

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

def ocr2xhtml(img: Image.Image, lang: str)->str:
    try:
        debug = True
        try:
            data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DATAFRAME)
            # Handle silent OCR failures (empty or None result)
            if data is None or data.empty:
                error = f'Tesseract returned empty OCR data for language "{lang}".'
                print(error)
                return False
        except (pytesseract.TesseractError, Exception) as e:
            print(f'The OCR {lang} trained model must be downloaded.')
            try:
                tessdata_dir = os.environ['TESSDATA_PREFIX']
                os.makedirs(tessdata_dir, exist_ok=True)
                url = f'https://github.com/tesseract-ocr/tessdata_best/raw/main/{lang}.traineddata'
                dest_path = os.path.join(tessdata_dir, f'{lang}.traineddata')
                msg = f'Downloading {lang}.traineddata into {tessdata_dir}…'
                print(msg)
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    with open(dest_path, 'wb') as f:
                        f.write(response.content)
                    msg = f'Downloaded and installed {lang}.traineddata successfully.'
                    print(msg)
                    data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DATAFRAME)
                    if data is None or data.empty:
                        error = f'Tesseract returned empty OCR data even after downloading {lang}.traineddata.'
                        print(error)
                        return False
                else:
                    error = f'Failed to download traineddata for {lang} (HTTP {response.status_code})'
                    print(error)
                    return False
            except Exception as e:
                error = f'Automatic download failed: {e}'
                print(error)
                return False
        data = data.dropna(subset=['text'])
        lines = []
        last_block = None
        for _, row in data.iterrows():
            text = row['text'].strip()
            if not text:
                continue
            block = row['block_num']
            if last_block is not None and block != last_block:
                lines.append('')  # blank line between blocks
            lines.append(text)
            last_block = block
        joined = '\n'.join(lines)
        raw_lines = [l.strip() for l in joined.split('\n')]
        # Normalize line breaks
        merged_lines = []
        buffer = ''
        for i, line in enumerate(raw_lines):
            if not line:
                if buffer:
                    merged_lines.append(buffer.strip())
                    buffer = ''
                continue
            if buffer and not buffer.endswith(('.', '?', '!', ':')) and not line[0].isupper():
                buffer += ' ' + line
            else:
                if buffer:
                    merged_lines.append(buffer.strip())
                buffer = line
        if buffer:
            merged_lines.append(buffer.strip())
        # Detect heading-like lines
        xhtml_parts = []
        debug_dump = []
        for i, p in enumerate(merged_lines):
            is_heading = False
            if p.isupper() and len(p.split()) <= 8:
                is_heading = True
            elif len(p.split()) <= 5 and p.istitle():
                is_heading = True
            elif (i == 0 or (i > 0 and merged_lines[i-1] == '')) and len(p.split()) <= 10:
                is_heading = True
            if is_heading:
                xhtml_parts.append(f'<h2>{p}</h2>')
                debug_dump.append(f'[H2] {p}')
            else:
                xhtml_parts.append(f'<p>{p}</p>')
                debug_dump.append(f'[P ] {p}')
        if debug:
            print('=== OCR DEBUG OUTPUT ===')
            for line in debug_dump:
                print(line)
            print('========================')
        return '\n'.join(xhtml_parts)
    except Exception as e:
        DependencyError(e)
        error = f'ocr2xhtml error: {e}'
        print(error)
        return False

def load_json_chapters(filepath:str)->list:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"load_json_chapters() error: {e}")
        return []

def save_json_chapters(session_id:str, filepath:str)->bool:
    try:
        session = context.get_session(session_id)
        if not session:
            print(f"save_json_chapters error: session not found ({session_id})")
            return False
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session['chapters'], f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"save_json_chapters() error: {e}")
        return False

def convert2epub(session_id:str)-> bool:
    session = context.get_session(session_id)
    if session and session.get('id', False):
        if session['cancellation_requested']:
            msg = 'Cancel requested'
            print(msg)
            return False
        try:
            title = False
            author = False
            util_app = shutil.which('ebook-convert')
            if not util_app:
                error = 'ebook-convert utility is not installed or not found.'
                print(error)
                return False
            file_input = session['ebook']
            if os.path.getsize(file_input) == 0:
                error = f'Input file is empty: {file_input}'
                print(error)
                return False
            file_ext = os.path.splitext(file_input)[1].lower()
            if file_ext not in ebook_formats:
                error = f'Unsupported file format: {file_ext}'
                print(error)
                return False
            if file_ext == '.txt':
                with open(file_input, 'r', encoding='utf-8') as f:
                    text = f.read()
                text = text.replace('\r\n', '\n')
                text = re.sub(r'\n{2,}', f".{TTS_SML['pause']['static']}", text)
                with open(file_input, 'w', encoding='utf-8') as f:
                    f.write(text)
            elif file_ext == '.pdf':
                msg = 'File input is a PDF. flatten it in XHTML…'
                print(msg)
                doc = fitz.open(file_input)
                file_meta = doc.metadata
                filename_no_ext = os.path.splitext(os.path.basename(session['ebook']))[0]
                title = file_meta.get('title') or filename_no_ext
                author = file_meta.get('author') or False
                xhtml_pages = []
                for i, page in enumerate(doc):
                    try:
                        text = page.get_text('xhtml').strip()
                    except Exception as e:
                        print(f'Error extracting text from page {i+1}: {e}')
                        text = ''
                    if not text:
                        msg = f'The page {i+1} seems to be image-based. Using OCR…'
                        print(msg)
                        if session['is_gui_process']:
                            show_alert({"type": "warning", "msg": msg})
                        pix = page.get_pixmap(dpi=300)
                        img = Image.open(io.BytesIO(pix.tobytes('png')))
                        xhtml_content = ocr2xhtml(img, session['language'])
                    else:
                        xhtml_content = text
                    if xhtml_content:
                        xhtml_pages.append(xhtml_content)
                if xhtml_pages:
                    xhtml_body = '\n'.join(xhtml_pages)
                    xhtml_text = (
                        '<?xml version="1.0" encoding="utf-8"?>\n'
                        '<html xmlns="http://www.w3.org/1999/xhtml">\n'
                        '<head>\n'
                        f'<meta charset="utf-8"/>\n<title>{title}</title>\n'
                        '</head>\n'
                        '<body>\n'
                        f'{xhtml_body}\n'
                        '</body>\n'
                        '</html>\n'
                    )
                    file_input = os.path.join(session['process_dir'], f'{filename_no_ext}.xhtml')
                    with open(file_input, 'w', encoding='utf-8') as html_file:
                        html_file.write(xhtml_text)
                else:
                    return False
            elif file_ext in ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp']:
                filename_no_ext = os.path.splitext(os.path.basename(session['ebook']))[0]
                msg = f'File input is an image ({file_ext}). Running OCR…'
                print(msg)
                img = Image.open(file_input)
                xhtml_pages = []
                page_count = 0
                for i, frame in enumerate(ImageSequence.Iterator(img)):
                    page_count += 1
                    frame = frame.convert('RGB')
                    xhtml_content = ocr2xhtml(frame, session['language'])
                    xhtml_pages.append(xhtml_content)
                if xhtml_pages:
                    xhtml_body = '\n'.join(xhtml_pages)
                    xhtml_text = (
                        '<?xml version="1.0" encoding="utf-8"?>\n'
                        '<html xmlns="http://www.w3.org/1999/xhtml">\n'
                        '<head>\n'
                        f'<meta charset="utf-8"/>\n<title>{filename_no_ext}</title>\n'
                        '</head>\n'
                        '<body>\n'
                        f'{xhtml_body}\n'
                        '</body>\n'
                        '</html>\n'
                    )
                    file_input = os.path.join(session['process_dir'], f'{filename_no_ext}.xhtml')
                    with open(file_input, 'w', encoding='utf-8') as html_file:
                        html_file.write(xhtml_text)
                    print(f'OCR completed for {page_count} image page(s).')
                else:
                    return False
            msg = f"Running command: {util_app} {file_input} {session['epub_path']}"
            print(msg)
            cmd = [
                    util_app, file_input, session['epub_path'],
                    '--input-encoding=utf-8',
                    '--output-profile=generic_eink',
                    '--epub-version=3',
                    '--flow-size=0',
                    '--chapter-mark=pagebreak',
                    '--page-breaks-before',
                    "//*[name()='h1' or name()='h2' or name()='h3' or name()='h4' or name()='h5']",
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
            DependencyError(e)
            error = f'convert2epub subprocess.CalledProcessError: {e.stderr}'
            print(error)
            return False
        except FileNotFoundError as e:
            DependencyError(e)
            error = f'convert2epub FileNotFoundError: {e}'
            print(error)
            return False
        except Exception as e:
            DependencyError(e)
            error = f'convert2epub error: {e}'
            print(error)
            return False

def get_ebook_title(epubBook:EpubBook,all_docs:list[Any])->str|None:
    # 1. Try metadata (official EPUB title)
    meta_title = epubBook.get_metadata('DC','title')
    if meta_title and meta_title[0][0].strip():
        return meta_title[0][0].strip()
    # 2. Try <title> in the head of the first XHTML document
    if all_docs:
        html = all_docs[0].get_content().decode('utf-8')
        soup = BeautifulSoup(html,'html.parser')
        title_tag = soup.select_one('head > title')
        if title_tag and title_tag.text.strip():
            return title_tag.text.strip()
        # 3. Try <img alt = '…'> if no visible <title>
        img = soup.find('img',alt = True)
        if img:
            alt = img['alt'].strip()
            if alt and 'cover' not in alt.lower():
                return alt
    return None

def get_cover(epubBook:EpubBook, session_id:str)->bool|str:
    try:
        session = context.get_session(session_id)
        if session and session.get('id', False):
            if session['cancellation_requested']:
                msg = 'Cancel requested'
                print(msg)
                return False
            cover_image = None
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
                # Open the image from bytes
                image = Image.open(io.BytesIO(cover_image))
                # Convert to RGB if needed (JPEG doesn't support alpha)
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')
                image.save(cover_path, format = 'JPEG')
                return cover_path
            return True
    except Exception as e:
        DependencyError(e)
        return False

def get_blocks(session_id:str, epubBook:EpubBook)->list:
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
        session = context.get_session(session_id)
        if session and session.get('id', False):
            if session['cancellation_requested']:
                msg = 'Cancel requested'
                print(msg)
                return []
            # Step 1: Extract TOC (Table of Contents)
            try:
                toc = epubBook.toc
                toc_list = [
                        nt for item in toc if hasattr(item, 'title')
                        if (nt := normalize_text(str(item.title), session['language'], session['language_iso1'], session['tts_engine'])) is not None
                ]
            except Exception as toc_error:
                error = f'Error extracting Table of Content: {toc_error}'
                show_alert({"type": "warning", "msg": error})
            # Get spine item IDs
            spine_ids = [item[0] for item in epubBook.spine]
            # Filter only spine documents (i.e., reading order)
            all_docs = [
                item for item in epubBook.get_items_of_type(ebooklib.ITEM_DOCUMENT)
                if item.id in spine_ids
            ]
            if not all_docs:
                error = 'No document body found!'
                print(error)
                return []
            title = get_ebook_title(epubBook, all_docs)
            bloks = []
            stanza_nlp = False
            if session['language'] in year_to_decades_languages:
                try:
                    stanza_model = f"stanza-{session['language_iso1']}"
                    stanza_nlp = loaded_tts.get(stanza_model, False)
                    if stanza_nlp:
                        msg = f"NLP model {stanza_model} loaded!"
                        print(msg)
                    else:
                        use_gpu = True if (
                            (session['device'] == devices['CUDA']['proc'] and not devices['JETSON']['found'] and devices['CUDA']['found']) or
                            (session['device'] == devices['ROCM']['proc'] and devices['ROCM']['found']) or
                            (session['device'] == devices['XPU']['proc'] and devices['XPU']['found'])
                        ) else False
                        stanza_nlp = stanza.Pipeline(session['language_iso1'], processors='tokenize,ner,mwt', use_gpu=use_gpu, download_method=DownloadMethod.REUSE_RESOURCES, dir=os.getenv('STANZA_RESOURCES_DIR'))
                        if stanza_nlp:
                            session['stanza_cache'] = stanza_model
                            loaded_tts[stanza_model] = stanza_nlp
                            msg = f"NLP model {stanza_model} loaded!"
                            print(msg)
                except (ConnectionError, TimeoutError) as e:
                    error = f'Stanza model download connection error: {e}. Retry later'
                    print(error)
                    return []
                except Exception as e:
                    error = f'Stanza model initialization error: {e}'
                    print(error)
                    return []
            is_num2words_compat = get_num2words_compat(session['language_iso1'])
            for doc_idx, doc in enumerate(all_docs):
                text = filter_blocks(doc_idx, doc, session_id, stanza_nlp, is_num2words_compat)
                if text is None:
                    break
                elif text:
                    bloks.append(text)
            if len(bloks) == 0:
                error = 'No bloks found! possible reason: file corrupted or need to convert images to text with OCR'
                print(error)
                return []
            return bloks
        return []
    except Exception as e:
        error = f'Error extracting main content pages: {e}'
        DependencyError(error)
        return []

def filter_blocks(idx:int, doc:EpubHtml, session_id:str, stanza_nlp:Pipeline, is_num2words_compat:bool)->str|None:

    def _tuple_row(node:Any, last_text_char:str|None=None)->Generator[tuple[str, Any], None, None]|None:
        try:
            prev_child_had_data = False
            for idx, child in enumerate(node.children):
                current_child_had_data = False
                if isinstance(child, NavigableString):
                    text = child.strip()
                    if text:
                        if prev_child_had_data:
                            yield ('break', sml_token("break"))
                        yield ('text', text)
                        last_text_char = text[-1]
                        current_child_had_data = True
                elif isinstance(child, Tag):
                    name = child.name.lower()
                    if name in heading_tags:
                        title = child.get_text(strip=True)
                        if title:
                            if prev_child_had_data:
                                yield ('break', sml_token("break"))
                            yield ('heading', title)
                            last_text_char = title[-1]
                            current_child_had_data = True
                    elif name == 'table':
                        if prev_child_had_data:
                            yield ('break', sml_token("break"))
                        yield ('table', child)
                        current_child_had_data = True
                    else:
                        return_data = False
                        if name in proc_tags:
                            is_header = False
                            if prev_child_had_data and name in break_tags:
                                yield ('break', sml_token("break"))
                            for inner in _tuple_row(child, last_text_char):
                                return_data = True
                                yield inner
                                if len(inner) > 1 and isinstance(inner[1], str) and inner[1]:
                                    last_text_char = inner[1][-1]
                                current_child_had_data = True
                                if inner[0] in ('text', 'heading') and isinstance(inner[1], str) and inner[1]:
                                    is_header = True
                            if return_data:
                                if name in break_tags and name != 'span':
                                    if is_header or (last_text_char and not last_text_char.isalnum() and not last_text_char.isspace()):
                                        yield ('break', sml_token("break"))
                                elif name in heading_tags or name in pause_tags:
                                    yield ('pause', sml_token("pause"))
                        else:
                            yield from _tuple_row(child, last_text_char)
                            current_child_had_data = True
                if current_child_had_data:
                    prev_child_had_data = True
        except Exception as e:
            error = f'filter_blocks() _tuple_row() error: {e}'
            DependencyError(error)
            return None

    def _num_repl(m):
        s = m.group(0)
        # leave years alone (already handled above)
        if re.fullmatch(r"\d{4}", s):
            return s
        n = float(s) if '.' in s else int(s)
        if is_num2words_compat:
            return num2words(n, lang=(lang_iso1 or 'en'))
        else:
            return math2words(m, lang, lang_iso1, tts_engine, is_num2words_compat)

    try:
        msg = f'----------\nParsing doc {idx}'
        print(msg)
        session = context.get_session(session_id)
        if session and session.get('id', False):
            lang, lang_iso1, tts_engine = session['language'], session['language_iso1'], session['tts_engine']
            heading_tags = [f'h{i}' for i in range(1, 5)]
            break_tags = ['br', 'p', 'span']
            pause_tags = ['div']
            proc_tags = heading_tags + break_tags + pause_tags
            doc_body = doc.get_body_content()
            raw_html = doc_body.decode('utf-8') if isinstance(doc_body, bytes) else doc_body
            soup = BeautifulSoup(raw_html, 'html.parser')
            body = soup.body
            if not body or not body.get_text(strip=True):
                msg = 'No body found. Skip to next doc…'
                print(msg)
                return ''
            # Skip known non-chapter types
            epub_type = body.get('epub:type', '').lower()
            if not epub_type:
                section_tag = soup.find('section')
                if section_tag:
                    epub_type = section_tag.get('epub:type', '').lower()
            excluded = {
                'frontmatter', 'backmatter', 'toc', 'titlepage', 'colophon',
                'acknowledgments', 'dedication', 'glossary', 'index',
                'appendix', 'bibliography', 'copyright-page', 'landmark'
            }
            if any(part in epub_type for part in excluded):
                msg = 'No body part. Skip to next doc…'
                print(msg)
                return ''
            # remove scripts/styles
            for tag in soup(['script', 'style']):
                tag.decompose()
            tuples_list = list(_tuple_row(body))
            if not tuples_list:
                error = 'No tuples_list from body created!'
                print(error)
                return None
            msg = f'Parsing xhtml markers…'
            print(msg)
            text_list = []
            handled_tables = set()
            prev_typ = None
            for typ, payload in tuples_list:
                if typ == 'heading':
                    text_list.append(payload.strip())
                elif typ in ('break', 'pause'):
                    if prev_typ != typ:
                        text_list.append(sml_token(typ))
                elif typ == 'table':
                    table = payload
                    if table in handled_tables:
                        prev_typ = typ
                        continue
                    handled_tables.add(table)
                    rows = table.find_all('tr')
                    if not rows:
                        prev_typ = typ
                        continue
                    headers = [c.get_text(strip=True) for c in rows[0].find_all(['td', 'th'])]
                    for row in rows[1:]:
                        cells = [c.get_text(strip=True).replace('\xa0', ' ') for c in row.find_all('td')]
                        if not cells:
                            continue
                        if len(cells) == len(headers) and headers:
                            line = ' — '.join(f'{h}: {c}' for h, c in zip(headers, cells))
                        else:
                            line = ' — '.join(cells)
                        if line:
                            text_list.append(line.strip())
                else:
                    text = payload.strip()
                    if text:
                        text_list.append(text)
                prev_typ = typ
            msg = f'Flattening as raw text…'
            print(msg)
            max_chars = int(language_mapping[lang]['max_chars'] / 1.5)
            clean_list = []
            i = 0
            while i < len(text_list):
                current = text_list[i]
                if current in {v['static'] for v in TTS_SML.values() if "static" in v}:
                    if clean_list:
                        prev = clean_list[-1]
                        if prev in {v['static'] for v in TTS_SML.values() if "static" in v}:
                            i += 1
                            continue
                    clean_list.append(current)
                    i += 1
                    continue
                clean_list.append(current)
                i += 1
            text = ' '.join(clean_list)
            if not re.search(r"[^\W_]", text):
                error = 'No valid text found!'
                print(error)
                return None
            # clean SML tags badly coded
            res, text = normalize_sml_tags(text)
            if res is False:
                print(text)
                if session['is_gui_process']:
                    show_alert({"type": "warning", "msg": text})
                return None
            # remove any [break] between words or cutting words
            break_token = re.escape(sml_token('break'))
            strip_break_spaces_re = re.compile(rf'\s*{break_token}\s*')
            break_between_alnum_re = re.compile(rf'(?<=[\w]){break_token}(?=[\w])', flags=re.UNICODE)
            text = strip_break_spaces_re.sub(sml_token('break'), text)
            text = break_between_alnum_re.sub(' ', text)
            # escape all SML tags to not be touched by any text treatment
            text, sml_blocks = escape_sml(text)
            if stanza_nlp:
                msg = 'Converting dates and years to words…'
                print(msg)
                re_ordinal = re.compile(
                    r'(?<!\w)(0?[1-9]|[12][0-9]|3[01])(?:\s|\u00A0)*(?:st|nd|rd|th)(?!\w)',
                    re.IGNORECASE
                )
                re_num = re.compile(r'(?<!\w)[-+]?\d+(?:\.\d+)?(?!\w)')
                text = unicodedata.normalize('NFKC', text).replace('\u00A0', ' ')
                if re_num.search(text) and re_ordinal.search(text):
                    date_spans = get_date_entities(text, stanza_nlp)
                    if date_spans:
                        result = []
                        last_pos = 0
                        for start, end, date_text in date_spans:
                            result.append(text[last_pos:start])
                            # 1) convert 4-digit years (your original behavior)
                            processed = re.sub(
                                r"\b\d{4}\b",
                                lambda m: year2words(m.group(), lang, lang_iso1, is_num2words_compat),
                                date_text
                            )
                            # 2) convert ordinal days like "16th"/"16 th"->"sixteenth"
                            if is_num2words_compat:
                                processed = re_ordinal.sub(
                                    lambda m: num2words(int(m.group(1)), to='ordinal', lang=(lang_iso1 or 'en')),
                                    processed
                                )
                            else:
                                processed = re_ordinal.sub(
                                    lambda m: math2words(m.group(), lang, lang_iso1, tts_engine, is_num2words_compat),
                                    processed
                                )
                            # 3) convert other numbers (skip 4-digit years)
                            processed = re_num.sub(_num_repl, processed)
                            result.append(processed)
                            last_pos = end
                        result.append(text[last_pos:])
                        text = ' '.join(result)
                    else:
                        if is_num2words_compat:
                            text = re_ordinal.sub(
                                lambda m: num2words(int(m.group(1)), to='ordinal', lang=(lang_iso1 or 'en')),
                                text
                            )
                        else:
                            text = re_ordinal.sub(
                                lambda m: math2words(int(m.group(1)), lang, lang_iso1, tts_engine, is_num2words_compat),
                                text
                            )
                        text = re.sub(
                            r"\b\d{4}\b",
                            lambda m: year2words(m.group(), lang, lang_iso1, is_num2words_compat),
                            text
                        )
            msg = 'Convert romans to numbers…'
            print(msg)
            text = roman2number(text)
            msg = 'Convert time to words…'
            print(msg)
            text = clock2words(text, lang, lang_iso1, tts_engine, is_num2words_compat)
            msg = 'Convert numbers, maths signs to words…'
            print(msg)
            text = math2words(text, lang, lang_iso1, tts_engine, is_num2words_compat)
            msg = 'Normalize text…'
            print(msg)
            text = normalize_text(text, lang, lang_iso1, tts_engine)
            text = restore_sml(text, sml_blocks)
            return text
        return None
    except Exception as e:
        error = f'filter_blocks() error: {e}'
        DependencyError(error)
        return None

def get_sentences(text:str, session_id:str)->list|None:

    def split_inclusive(text:str, pattern:re.Pattern[str])->list[str]:
        result = []
        last_end = 0
        for match in pattern.finditer(text):
            result.append(text[last_end:match.end()].strip())
            last_end = match.end()
        if last_end < len(text):
            tail = text[last_end:].strip()
            if tail:
                result.append(tail)
        return result

    def split_sentence_on_sml(sentence:str)->list[str]:
        parts:list[str] = []
        last = 0
        for m in SML_TAG_PATTERN.finditer(sentence):
            start, end = m.span()
            if start > last:
                text = sentence[last:start]
                if text:
                    parts.append(text)
            parts.append(m.group(0))
            last = end
        if last < len(sentence):
            tail = sentence[last:]
            if tail:
                parts.append(tail)
        return parts

    def strip_escaped_sml(s:str)->str:
        return ''.join(c for c in s if ord(c) < sml_escape_tag)

    def clean_len(s:str)->int:
        return len(strip_escaped_sml(s))

    def is_latin_only(s:str)->bool:
        s = strip_escaped_sml(s)
        s = re.sub(r'[^\w\s]', '', s, flags=re.UNICODE)
        has_latin = bool(re.search(r'[A-Za-z]', s))
        has_nonlatin = bool(re.search(r'[^\x00-\x7F]', s))
        return has_latin and not has_nonlatin

    def split_at_space_limit(s:str)->list[str]:
        out = []
        rest = s.strip()
        while rest and len(strip_escaped_sml(rest)) > max_chars:
            cut = rest[:max_chars + 1]
            idx = cut.rfind(' ')
            if idx == -1:
                out.append(rest[:max_chars].strip())
                rest = rest[max_chars:].strip()
            else:
                out.append(rest[:idx].strip())
                rest = rest[idx + 1:].strip()
        if rest:
            out.append(rest.strip())
        return out

    def segment_ideogramms(text:str)->list[str]:
        result = []
        try:
            if lang in ['yue','yue-Hant','yue-Hans','zh-yue','cantonese']:
                import pycantonese as pc
                result.extend([t for t in pc.segment(text) if t.strip()])
            elif lang == 'zho':
                import jieba
                jieba.dt.cache_file = os.path.join(models_dir, 'jieba.cache')
                result.extend([t for t in jieba.cut(text) if t.strip()])
            elif lang == 'jpn':
                import nagisa
                result.extend(nagisa.tagging(text).words)
            elif lang == 'kor':
                from soynlp.tokenizer import LTokenizer
                ltokenizer = LTokenizer()
                result.extend([t for t in ltokenizer.tokenize(text) if t.strip()])
            elif lang in ['tha','lao','mya','khm']:
                from pythainlp.tokenize import word_tokenize
                result.extend([t for t in word_tokenize(text, engine='newmm') if t.strip()])
            else:
                result.append(text.strip())
            return result
        except Exception as e:
            DependencyError(e)
            return [text]

    def join_ideogramms(idg_list:list[str])->str:
        try:
            buffer = ''
            prev_latin = False
            prev_nonlatin = False
            for token in idg_list:
                cur_starts_latin = bool(re.match(r'[A-Za-z0-9]', token))
                cur_starts_nonlatin = bool(re.match(r'[^\x00-\x7F]', token))
                if buffer:
                    if (prev_latin and (cur_starts_latin or cur_starts_nonlatin)) or (prev_nonlatin and cur_starts_latin):
                        buffer += ' '
                    elif len(buffer) + len(token) > max_chars:
                        yield buffer
                        buffer = ''
                buffer += token
                prev_latin = bool(re.search(r'[A-Za-z0-9]$', token))
                prev_nonlatin = bool(re.search(r'[^\x00-\x7F]$', token))
            if buffer:
                yield buffer
        except Exception as e:
            DependencyError(e)
            if buffer:
                yield buffer

    try:
        session = context.get_session(session_id)
        if not session:
            return None

        lang, tts_engine = session['language'], session['tts_engine']
        max_chars = int(language_mapping[lang]['max_chars'] / 2)

        # escape all SML tags to not be touched by any text treatment
        text, sml_blocks = escape_sml(text)

        assert not SML_TAG_PATTERN.search(text)

        # PASS 1 — hard punctuation
        hard_pattern = re.compile(
            rf"(.*?(?:{'|'.join(map(re.escape, punctuation_split_hard_set))}))(?=\s|$)",
            re.DOTALL
        )
        hard_list = split_inclusive(text, hard_pattern)
        if not hard_list:
            hard_list = [text.strip()]
        hard_list = [s.strip() for s in hard_list if s.strip()]

        # PASS 2 — soft punctuation
        soft_pattern = re.compile(
            rf"(.*?(?:{'|'.join(map(re.escape, punctuation_split_soft_set))}))(?=\s|$)",
            re.DOTALL
        )
        soft_list = []
        i = 0
        n = len(hard_list)
        while i < n:
            s = hard_list[i].strip()
            if not s:
                i += 1
                continue
            if i + 1 < n:
                next_s = hard_list[i + 1].strip()
                next_clean = strip_escaped_sml(next_s)
                if next_clean and sum(c.isalnum() for c in next_clean) < 3:
                    s = f"{s} {next_s}"
                    i += 2
                else:
                    i += 1
            else:
                i += 1
            if len(strip_escaped_sml(s)) <= max_chars:
                soft_list.append(s)
                continue
            parts = split_inclusive(s, soft_pattern)
            if parts:
                valid = False
                for p in parts:
                    if len(strip_escaped_sml(p.strip())) <= max_chars:
                        valid = True
                        break
                if valid:
                    soft_list.extend([p.strip() for p in parts if p.strip()])
                else:
                    soft_list.append(s)
            else:
                soft_list.append(s)

        # PASS 3 — space split (last resort)
        last_list = []
        for s in soft_list:
            s = s.strip()
            if not s:
                continue
            rest = s
            while rest:
                current_len = len(strip_escaped_sml(rest))   # ← rename variable
                if current_len <= max_chars:
                    last_list.append(rest.strip())
                    break
                cut = rest[:max_chars + 1]
                idx = cut.rfind(' ')
                if idx > 0:
                    left = rest[:idx].strip()
                    right = rest[idx + 1:].strip()
                else:
                    left = rest[:max_chars].strip()
                    right = rest[max_chars:].strip()
                if not left or right == rest:
                    last_list.append(rest.strip())
                    break
                last_list.append(left)
                rest = right

        # PASS 4 — merge very short rows
        final_list = []
        merge_max_chars = int((max_chars / 2) / 3)
        i = 0
        n = len(last_list)
        while i < n:
            cur = last_list[i].strip()
            if not cur:
                i += 1
                continue
            if i == 0:
                final_list.append(cur)
                i += 1
                continue
            cur_len = clean_len(cur)
            if cur_len <= merge_max_chars:
                j = i + 1
                while j < n:
                    nxt = last_list[j].strip()
                    if not nxt:
                        j += 1
                        continue
                    if cur_len + clean_len(nxt) <= max_chars:
                        cur = cur.rstrip() + ' ' + nxt.lstrip()
                        cur_len = clean_len(cur)
                        j += 1
                        continue
                    break
                if final_list:
                    prev = final_list[-1]
                    if clean_len(prev) + cur_len <= max_chars:
                        final_list[-1] = prev.rstrip() + ' ' + cur.lstrip()
                        i = j
                        continue
                final_list.append(cur)
                i = j
                continue
            final_list.append(cur)
            i += 1

        if lang in ['zho', 'jpn', 'kor', 'tha', 'lao', 'mya', 'khm']:
            result = []
            for s in final_list:
                parts = split_sentence_on_sml(s)
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    if SML_TAG_PATTERN.fullmatch(part):
                        result.append(part)
                        continue
                    tokens = segment_ideogramms(part)
                    if isinstance(tokens, list):
                        result.extend([t for t in tokens if t.strip()])
                    else:
                        tokens = tokens.strip()
                        if tokens:
                            result.append(tokens)
            ideogram_list = []
            for s in join_ideogramms(result):
                if not is_latin_only(s):
                    ideogram_list.append(s)
            if ideogram_list:
                ideogram_list = [restore_sml(s, sml_blocks) for s in ideogram_list]
            return ideogram_list
        if final_list:
            final_list = [restore_sml(s, sml_blocks) for s in final_list]
        return final_list
    except Exception as e:
        print(f'get_sentences() error: {e}')
        return None

def get_sanitized(str:str, replacement:str='_')->str:
    str = str.replace('&', 'And')
    forbidden_chars = r'[<>:"/\\|?*\x00-\x1F ()]'
    sanitized = re.sub(r'\s+', replacement, str)
    sanitized = re.sub(forbidden_chars, replacement, sanitized)
    sanitized = sanitized.strip('_')
    return sanitized
    
def get_date_entities(text:str, stanza_nlp:Pipeline)->list[tuple[int,int,str]]|bool:
    try:
        doc = stanza_nlp(text)
        date_spans = []
        for ent in doc.ents:
            if ent.type == 'DATE':
                date_spans.append((ent.start_char, ent.end_char, ent.text))
        return date_spans
    except Exception as e:
        error = f'get_date_entities() error: {e}'
        print(error)
        return False

def get_num2words_compat(lang_iso1:str)->bool:
    try:
        test = num2words(1, lang=lang_iso1.replace('zh', 'zh_CN'))
        return True
    except NotImplementedError:
        return False
    except Exception as e:
        return False

def set_formatted_number(text:str, lang:str, lang_iso1:str, is_num2words_compat:bool, max_single_value:int=999_999_999_999_999_999)->str:
    # match up to 18 digits, optional “,…” groups (allowing spaces or NBSP after comma), optional decimal of up to 12 digits
    # handle optional range with dash/en dash/em dash between numbers, and allow trailing punctuation
    number_re = re.compile(
        r'(?<!\w)'
        r'(\d{1,18}(?:,\s*\d{1,18})*(?:\.\d{1,12})?)'      # first number
        r'(?:\s*([-–—])\s*'                                # dash type
        r'(\d{1,18}(?:,\s*\d{1,18})*(?:\.\d{1,12})?))?'    # optional second number
        r'([^\w\s]*)',                                     # optional trailing punctuation
        re.UNICODE
    )

    def normalize_commas(num_str:str)->str:
        # ormalize number string to standard comma format: 1,234,567
        tok = num_str.replace('\u00A0', '').replace(' ', '')
        if '.' in tok:
            integer_part, decimal_part = tok.split('.', 1)
            integer_part = integer_part.replace(',', '')
            integer_part = "{:,}".format(int(integer_part))
            return f'{integer_part}.{decimal_part}'
        else:
            integer_part = tok.replace(',', '')
            return "{:,}".format(int(integer_part))

    def clean_single_num(num_str:str)->str:
        tok = unicodedata.normalize('NFKC', num_str)
        if tok.lower() in ('inf', 'infinity', 'nan'):
            return tok
        clean = tok.replace(',', '').replace('\u00A0', '').replace(' ', '')
        try:
            num = float(clean) if '.' in clean else int(clean)
        except (ValueError, OverflowError):
            return tok
        if not math.isfinite(num) or abs(num) > max_single_value:
            return tok

        # Normalize commas before final output
        tok = normalize_commas(tok)

        if is_num2words_compat:
            new_lang_iso1 = lang_iso1.replace('zh', 'zh_CN')
            return num2words(num, lang=new_lang_iso1)
        else:
            phoneme_map = language_math_phonemes.get(
                lang,
                language_math_phonemes.get(default_language_code, language_math_phonemes['eng'])
            )
            return ' '.join(phoneme_map.get(ch, ch) for ch in str(num))

    def clean_match(match:re.Match)->str:
        first_num = clean_single_num(match.group(1))
        dash_char = match.group(2) or ''
        second_num = clean_single_num(match.group(3)) if match.group(3) else ''
        trailing = match.group(4) or ''
        if second_num:
            return f'{first_num}{dash_char}{second_num}{trailing}'
        else:
            return f'{first_num}{trailing}'

    return number_re.sub(clean_match, text)

def year2words(year_str:str, lang:str, lang_iso1:str, is_num2words_compat:bool)->str|bool:
    try:
        year = int(year_str)
        first_two = int(year_str[:2])
        last_two = int(year_str[2:])
        lang_iso1 = lang_iso1 if lang in language_math_phonemes.keys() else default_language_code
        lang_iso1 = lang_iso1.replace('zh', 'zh_CN')
        if not year_str.isdigit() or len(year_str) != 4 or last_two < 10:
            if is_num2words_compat:
                return num2words(year, lang=lang_iso1)
            else:
                return ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in year_str)
        if is_num2words_compat:
            return f'{num2words(first_two, lang=lang_iso1)} {num2words(last_two, lang=lang_iso1)}' 
        else:
            return ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in first_two) + ' ' + ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in last_two)
    except Exception as e:
        error = f'year2words() error: {e}'
        print(error)
        return False

def clock2words(text:str, lang:str, lang_iso1:str, tts_engine:str, is_num2words_compat:bool)->str:

    def n2w(n:int)->str:
        key = (n, lang, is_num2words_compat)
        if key in _n2w_cache:
            return _n2w_cache[key]
        if is_num2words_compat:
            word = num2words(n, lang=lang_iso1)
        else:
            word = math2words(n, lang, lang_iso1, tts_engine, is_num2words_compat)
        if not isinstance(word, str):
            word = str(word)
        _n2w_cache[key] = word
        return word

    def repl_num(m:re.Match)->str:
        # Reject enumeration patterns like "(1.2)"
        start, end = m.start(), m.end()
        if (
            start > 0 and end < len(text)
            and text[start - 1] == '('
            and text[end] == ')'
        ):
            return m.group(0)
        # Parse hh[:mm[:ss]]
        try:
            h = int(m.group(1))
            mnt = int(m.group(2))
            sec = m.group(3)
            sec = int(sec) if sec is not None else None
        except Exception:
            return m.group(0)
        # basic validation; if out of range, keep original
        if not (0 <= h <= 23 and 0 <= mnt <= 59 and (sec is None or 0 <= sec <= 59)):
            return m.group(0)
        # If no language clock rules, just say numbers plainly
        if not lc:
            parts = [n2w(h)]
            if mnt != 0:
                parts.append(n2w(mnt))
            if sec is not None and sec > 0:
                parts.append(n2w(sec))
            return ' '.join(parts)
        next_hour = (h + 1) % 24
        special_hours = lc.get('special_hours', {})
        if mnt == 0 and (sec is None or sec == 0):
            if h in special_hours:
                phrase = special_hours[h]
            else:
                phrase = lc['oclock'].format(hour=n2w(h))
        elif mnt == 15:
            phrase = lc['quarter_past'].format(hour=n2w(h))
        elif mnt == 30:
            if lang == 'deu':
                phrase = lc['half_past'].format(next_hour=n2w(next_hour))
            else:
                phrase = lc['half_past'].format(hour=n2w(h))
        elif mnt == 45:
            phrase = lc['quarter_to'].format(next_hour=n2w(next_hour))
        elif mnt < 30:
            phrase = lc['past'].format(hour=n2w(h), minute=n2w(mnt)) if mnt != 0 else lc['oclock'].format(hour=n2w(h))
        else:
            minute_to_hour = 60 - mnt
            phrase = lc['to'].format(
                next_hour=n2w(next_hour),
                minute=n2w(minute_to_hour),
                minute_to_hour=n2w(minute_to_hour)
            )
        if sec is not None and sec > 0:
            second_phrase = lc['second'].format(second=n2w(sec))
            phrase = lc['full'].format(phrase=phrase, second_phrase=second_phrase)
        return phrase

    time_rx = re.compile(
        r'\b([01]?\d|2[0-3]):([0-5]\d)(?::([0-5]\d))?\b'
    )
    lc = language_clock.get(lang) if 'language_clock' in globals() else None
    _n2w_cache = {}
    return time_rx.sub(repl_num, text)

def math2words(text:str, lang:str, lang_iso1:str, tts_engine:str, is_num2words_compat:bool)->str:
    def repl_ambiguous(match:re.Match)->str:
        # handles "num SYMBOL num" and "SYMBOL num"
        if match.group(2) and match.group(2) in ambiguous_replacements:
            return f'{match.group(1)} {ambiguous_replacements[match.group(2)]} {match.group(3)}'
        if match.group(3) and match.group(3) in ambiguous_replacements:
            return f'{ambiguous_replacements[match.group(3)]} {match.group(4)}'
        return match.group(0)

    def _ordinal_to_words(m:re.Match)->str:
        n = int(m.group(1))
        if is_num2words_compat:
            try:
                from num2words import num2words
                return num2words(n, to='ordinal', lang=(lang_iso1 or 'en'))
            except Exception:
                pass
        # If num2words isn't available/compatible, keep original token as-is.
        return m.group(0)

    # Matches any digits + optional space/NBSP + st/nd/rd/th, not glued into words.
    re_ordinal = re.compile(r'(?<!\w)(\d+)(?:\s|\u00A0)*(?:st|nd|rd|th)(?!\w)')
    text = re.sub(r'(\d)\)', r'\1 : ', text)
    text = re_ordinal.sub(_ordinal_to_words, text)
    # Symbol phonemes
    ambiguous_symbols = {"-", "/", "*", "x"}
    phonemes_list = language_math_phonemes.get(lang, language_math_phonemes[default_language_code])
    replacements = {k: v for k, v in phonemes_list.items() if not k.isdigit() and k not in [',', '.']}
    normal_replacements  = {k: v for k, v in replacements.items() if k not in ambiguous_symbols}
    ambiguous_replacements = {k: v for k, v in replacements.items() if k in ambiguous_symbols}
    # Replace unambiguous symbols everywhere
    if normal_replacements:
        sym_pat = r'(' + '|'.join(map(re.escape, normal_replacements.keys())) + r')'
        text = re.sub(sym_pat, lambda m: f' {normal_replacements[m.group(1)]} ', text)
    # Replace ambiguous symbols only in valid equation contexts
    if ambiguous_replacements:
        ambiguous_pattern = (
            r'(?<!\S)'                   # no non-space before
            r'(\d+)\s*([-/*x])\s*(\d+)'  # num SYMBOL num
            r'(?!\S)'                    # no non-space after
            r'|'                         # or
            r'(?<!\S)([-/*x])\s*(\d+)(?!\S)'  # SYMBOL num
        )
        text = re.sub(ambiguous_pattern, repl_ambiguous, text)
    text = set_formatted_number(text, lang, lang_iso1, is_num2words_compat)
    return text

def roman2number(text: str)->str:

    def is_valid_roman(s: str)->bool:
        return bool(valid_roman.fullmatch(s))

    def to_int(s: str)->str:
        s = s.upper()
        i = 0
        result = 0
        while i < len(s):
            for roman, value in roman_numbers_tuples:
                if s[i:i + len(roman)] == roman:
                    result += value
                    i += len(roman)
                    break
            else:
                return s
        return str(result)

    def repl_heading(m: re.Match)->str:
        roman = m.group(1)
        if not is_valid_roman(roman):
            return m.group(0)
        return f"{to_int(roman)}{m.group(2)}{m.group(3)}"

    def repl_standalone(m: re.Match)->str:
        roman = m.group(1)
        if not is_valid_roman(roman):
            return m.group(0)
        return f"{to_int(roman)}{m.group(2)}"

    def repl_word(m: re.Match)->str:
        roman = m.group(1)
        if not is_valid_roman(roman):
            return m.group(0)
        return to_int(roman)

    def repl_chapter_single(m: re.Match)->str:
        word = m.group(1)
        roman = m.group(2)
        if not is_valid_roman(roman):
            return m.group(0)
        return f"{word} {to_int(roman)}"

    valid_roman = re.compile(
        r'^(?=.)M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$',
        re.IGNORECASE
    )
    chapter_words = sorted(
        {w for words in chapter_word_mapping.values() for w in words},
        key=len,
        reverse=True
    )
    chapter_words_re = re.compile(
        rf'\b({"|".join(map(re.escape, chapter_words))})\s+([IVXLCDM]+)\b',
        re.IGNORECASE | re.UNICODE
    )
    text = re.sub(
        r'^(?:\s*)([IVXLCDM]+)([.-])(\s+)',
        repl_heading,
        text,
        flags=re.MULTILINE
    )
    text = re.sub(
        r'^(?:\s*)([IVXLCDM]+)([.-])(?:\s*)$',
        repl_standalone,
        text,
        flags=re.MULTILINE
    )
    text = chapter_words_re.sub(repl_chapter_single, text)
    text = re.sub(
        r'(?<!\S)([IVXLCDM]{2,})(?!\S)',
        repl_word,
        text
    )
    return text
    
def is_latin(s:str)->bool:
    return all((u'a' <= ch.lower() <= 'z') or ch.isdigit() or not ch.isalpha() for ch in s)

def foreign2latin(text:str, base_lang:str)->str:

    def script_of(word:str)->str:
        for ch in word:
            if ch.isalpha():
                name = unicodedata.name(ch, '')
                if 'CYRILLIC' in name:
                    return 'cyrillic'
                if 'LATIN' in name:
                    return 'latin'
                if 'ARABIC' in name:
                    return 'arabic'
                if 'HANGUL' in name:
                    return 'hangul'
                if 'HIRAGANA' in name or 'KATAKANA' in name:
                    return 'japanese'
                if 'CJK' in name or 'IDEOGRAPH' in name:
                    return 'chinese'
        return 'unknown'

    def romanize(word:str)->str:
        scr = script_of(word)
        if scr == 'latin':
            return word
        try:
            if scr == 'chinese':
                from pypinyin import pinyin, Style
                return ''.join(x[0] for x in pinyin(word, style=Style.NORMAL))
            if scr == 'japanese':
                import pykakasi
                k = pykakasi.kakasi()
                k.setMode('H', 'a')
                k.setMode('K', 'a')
                k.setMode('J', 'a')
                k.setMode('r', 'Hepburn')
                return k.getConverter().do(word)
            if scr == 'hangul':
                return unidecode(word)
            if scr == 'arabic':
                return unidecode(phonemize(word, language='ar', backend='espeak'))
            if scr == 'cyrillic':
                return unidecode(phonemize(word, language='ru', backend='espeak'))
            return unidecode(word)
        except Exception:
            return unidecode(word)

    # Protect ALL SML tags using the global grammar
    protected: Dict[str, str] = {}
    for i, m in enumerate(SML_TAG_PATTERN.finditer(text)):
        key: str = f'__TTS_MARKER_{i}__'
        protected[key] = m.group(0)
        text = text.replace(m.group(0), key)
    tokens: list[str] = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    buf: list[str] = []
    for t in tokens:
        if t in protected:
            buf.append(t)
        elif re.match(r"^\w+$", t):
            buf.append(romanize(t))
        else:
            buf.append(t)
    out: str = ''
    for i, t in enumerate(buf):
        if i == 0:
            out += t
        else:
            if re.match(r"^\w+$", buf[i - 1]) and re.match(r"^\w+$", t):
                out += ' ' + t
            else:
                out += t
    for k, v in protected.items():
        out = out.replace(k, v)
    return out

def normalize_sml_tags(text:str)->tuple[bool, str]:
    out = []
    stack = []
    last = 0
    for m in SML_TAG_PATTERN.finditer(text):
        start, end = m.span()
        out.append(text[last:start])
        tag = m.group("tag")
        close = bool(m.group("close"))
        value = m.group("value")
        info = TTS_SML.get(tag)
        if not info:
            out.append(m.group(0))
            last = end
            continue
        if info.get("paired"):
            if close:
                if not stack or stack[-1] != tag:
                    error = f'normalize_sml_tags() error: unmatched closing tag [/{tag}]'
                    return False, error
                stack.pop()
                out.append(f"[/{tag}]")
            else:
                stack.append(tag)
                if value is not None:
                    out.append(f"[{tag}:{value.strip()}]")
                else:
                    error = f'normalize_sml_tags() error: paired tag [{tag}] requires a value'
                    return False, error
        else:
            if close:
                error = f'normalize_sml_tags() error: non-paired tag [/{tag}] is invalid'
                return False, error
            out.append(info['static'])
        last = end
    out.append(text[last:])
    if stack:
        error = f"normalize_sml_tags() error: unclosed tag(s): {', '.join(stack)}"
        return False, error
    return True, ''.join(out)

def escape_sml(text:str)->tuple[str, list[str]]:
    sml_blocks:list[str] = []

    def replace(m:re.Match[str])->str:
        sml_blocks.append(m.group(0))
        return chr(sml_escape_tag + len(sml_blocks) - 1)

    return SML_TAG_PATTERN.sub(replace, text), sml_blocks

def restore_sml(text:str, sml_blocks:list[str])->str:
    for i, block in enumerate(sml_blocks):
        text = text.replace(chr(sml_escape_tag + i), block)
    return text

def sml_token(tag:str, value:str|None=None, close:bool=False)->str:
    if close:
        return f"[/{tag}]"
    if value is not None:
        return f"[{tag}:{value}]"
    return f"[{tag}]"

def normalize_text(text:str, lang:str, lang_iso1:str, tts_engine:str)->str:

    def replace(match:re.Match)->str:
        token = match.group(1)
        for k, expansion in mapping.items():
            if token.lower() == k.lower():
                return expansion
        return token  # fallback
            
    # Remove emojis
    emoji_pattern = re.compile(f"[{''.join(emojis_list)}]+", flags=re.UNICODE)
    emoji_pattern.sub('', text)
    if lang in abbreviations_mapping:
        mapping = abbreviations_mapping[lang]
        # Sort keys by descending length so longer ones match first
        keys = sorted(mapping.keys(), key=len, reverse=True)
        # Build a regex that only matches whole “words” (tokens) exactly
        pattern = re.compile(
            r'(?<!\w)(' + '|'.join(re.escape(k) for k in keys) + r')(?!\w)',
            flags=re.IGNORECASE
        )
        text = pattern.sub(replace, text)
    # This regex matches sequences like a., c.i.a., f.d.a., m.c., etc…
    pattern = re.compile(r'\b(?:[a-zA-Z]\.){1,}[a-zA-Z]?\b\.?')
    # uppercase acronyms
    text = re.sub(r'\b(?:[a-zA-Z]\.){1,}[a-zA-Z]?\b\.?', lambda m: m.group().replace('.', '').upper(), text)
    # romanize foreign words
    if language_mapping[lang]['script'] == 'latin':
        text = foreign2latin(text, lang)
    # Replace multiple newlines ("\n\n", "\r\r", "\n\r", etc.) with a [pause] 1.4sec
    pattern = r'(?:\r\n|\r|\n){2,}'
    text = re.sub(pattern, f" {sml_token('pause')} ", text)
    # Replace single newlines ("\n" or "\r") with spaces
    text = re.sub(r'\r\n|\r|\n', ' ', text)
    # Replace punctuations causing hallucinations
    pattern = f"[{''.join(map(re.escape, punctuation_switch.keys()))}]"
    text = re.sub(pattern, lambda match: punctuation_switch.get(match.group(), match.group()), text)
    # remove unwanted chars
    chars_remove_table = str.maketrans({ch: ' ' for ch in chars_remove})
    text = text.translate(chars_remove_table)
    # replace double quotes by a comma if no punctuation precedes it
    text = re.sub(r'\s*"\s*', '"', text)
    text = re.sub(r'(?<=[\p{L}\p{N}])"(?=[\p{L}\p{N}]|$)', ', ', text)
    text = re.sub(r'"', '', text)
    # Replace multiple and spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Replace ok by 'Owkey'
    text = re.sub(r'\bok\b', 'Okay', text, flags=re.IGNORECASE)
    # Escape special characters in the punctuation list for regex
    pattern = '|'.join(map(re.escape, punctuation_split_hard_set))
    # Reduce multiple consecutive punctuations hard
    text = re.sub(rf'(\s*({pattern})\s*)+', r'\2 ', text).strip()
    # Escape special characters in the punctuation list for regex
    pattern = '|'.join(map(re.escape, punctuation_split_soft_set))
    # Reduce multiple consecutive punctuations soft
    text = re.sub(rf'(\s*({pattern})\s*)+', r'\2 ', text).strip()
    # Pattern 1: Add a space between UTF-8 characters and numbers
    text = re.sub(r'(?<=[\p{L}])(?=\d)|(?<=\d)(?=[\p{L}])', ' ', text)
    # Replace special chars with words
    specialchars = specialchars_mapping.get(lang, specialchars_mapping.get(default_language_code, specialchars_mapping['eng']))
    specialchars_table = {ord(char): f" {word} " for char, word in specialchars.items()}
    text = text.translate(specialchars_table)
    text = ' '.join(text.split())
    return text

def convert_chapters2audio(session_id:str)->bool:
    session = context.get_session(session_id)
    if session and session.get('id', False):
        try:
            if session['cancellation_requested']:
                msg = 'Cancel requested'
                print(msg)
                return False
            tts_manager = TTSManager(session)
            resume_chapter = 0
            missing_chapters = []
            final_sentences = []
            chapter_re = re.compile(r'^(\d+)\.' + re.escape(default_audio_proc_format) + r'$')
            existing_chapters = [f for f in os.listdir(session['chapters_dir']) if chapter_re.match(f)]
            existing_numbers = sorted(int(chapter_re.match(f).group(1)) for f in existing_chapters)
            if existing_numbers:
                expected = set(range(0, max(existing_numbers) + 1))
                missing_chapters = sorted(expected - set(existing_numbers))
                if not missing_chapters:
                    missing_chapters = [max(existing_numbers) + 1]
                resume_chapter = existing_numbers[-1]
            resume_sentence = 0
            missing_sentences = []
            sentence_re = re.compile(r'^(\d+)\.' + re.escape(default_audio_proc_format) + r'$')
            existing_sentences = [f for f in os.listdir(session['sentences_dir']) if sentence_re.match(f)]
            existing_numbers = sorted(int(sentence_re.match(f).group(1)) for f in existing_sentences)
            if existing_numbers:
                expected = set(range(0, max(existing_numbers) + 1))
                missing_sentences = sorted(expected - set(existing_numbers))
                if not missing_sentences:
                    missing_sentences = [max(existing_numbers) + 1]
                resume_sentence = existing_numbers[-1]
            total_chapters = len(session['chapters'])
            if total_chapters == 0:
                error = 'No chapterrs found!'
                print(error)
                return False
            total_iterations = sum(len(session['chapters'][x]) for x in range(total_chapters))
            total_sentences = sum(sum(1 for row in chapter) for chapter in session['chapters'])
            if total_sentences == 0:
                error = 'No sentences found!'
                print(error)
                return False
            msg = f"--------------------------------------------------\nA total of {total_chapters} {'block' if total_chapters <= 1 else 'blocks'} and {total_sentences} {'sentence' if total_sentences <= 1 else 'sentences'}.\n--------------------------------------------------"
            print(msg)
            if session['is_gui_process']:
                progress_bar = gr.Progress(track_tqdm=False)
            if session['ebook']:
                ebook_name = Path(session['ebook']).name
                with tqdm(total=total_iterations, desc='0.00%', bar_format='{desc}: {n_fmt}/{total_fmt} ', unit='step', initial=0) as t:
                    idx_target = 0
                    for c in range(0, total_chapters):
                        chapter_idx = c
                        sentences = session['chapters'][c]
                        start = idx_target
                        if c in missing_chapters:
                            msg = f'********* Recovering missing block {c} *********'
                            print(msg)
                        elif resume_chapter == c and c > 0:
                            msg = f'********* Resuming from block {resume_chapter} *********'
                            print(msg)
                        msg = f'Block {chapter_idx} containing {len(sentences)} sentences…'
                        print(msg)
                        for idx, sentence in enumerate(sentences):
                            if session['cancellation_requested']:
                                msg = 'Cancel requested'
                                print(msg)
                                return False
                            sentence = sentence.strip()
                            if any(c.isalnum() for c in sentence):
                                is_sml = bool(SML_TAG_PATTERN.fullmatch(sentence))
                                if (not is_sml) or (idx == len(sentences) - 1):
                                    final_sentences.append(sentence)
                                if idx_target in missing_sentences or idx_target >= resume_sentence:
                                    if idx_target in missing_sentences:
                                        msg = f'********* Recovering missing sentence {idx_target} *********'
                                        print(msg)
                                    elif resume_sentence == idx_target and resume_sentence > 0:
                                        msg = f'********* Resuming from sentence {resume_sentence} ********'
                                        print(msg)
                                    success = tts_manager.convert_sentence2audio(idx_target, sentence) if sentence else True
                                    if not success:
                                        return False
                                idx_target += 1
                            total_progress = (t.n + 1) / total_iterations
                            if session['is_gui_process']:
                                progress_bar(progress=total_progress, desc=f'{ebook_name} - {sentence}')
                            percent = total_progress * 100
                            t.set_description(f"{percent:.2f}%")
                            msg = f' : {sentence}'
                            print(msg)
                            t.update(1)
                        end = idx_target - 1
                        msg = f'End of Block {chapter_idx}'
                        print(msg)
                        if chapter_idx in missing_chapters or idx_target >= resume_sentence:
                            msg = f'Combining block {chapter_idx} to audio, sentence {start} to {end}'
                            print(msg)
                            chapter_audio_file = os.path.join(session['chapters_dir'], f'{chapter_idx}.{default_audio_proc_format}')
                            combine_result = combine_audio_sentences(session_id, chapter_audio_file, int(start), int(end))
                            if not combine_result:
                                msg = 'combine_audio_sentences() failed!'
                                print(msg)
                                return False
            return tts_manager.create_sentences2vtt(final_sentences)
        except Exception as e:
            DependencyError(e)
            error = f'convert_chapters2audio() error: {e}'
            print(error)
            return False

def combine_audio_sentences(session_id:str, file:str, start:int, end:int)->bool:
    try:
        session = context.get_session(session_id)
        if session and session.get('id', False):
            base = session['sentences_dir']
            ext = f".{default_audio_proc_format}"
            exists = os.path.exists
            join = os.path.join
            missing = []
            selected_files = []
            for i in range(start, end + 1):
                path = join(base, f"{i}{ext}")
                if exists(path):
                    selected_files.append(path)
                else:
                    missing.append(i)
            if missing:
                error = f"Missing sentence files: {missing}"
                print(error)
                return False
            if not selected_files:
                error = 'No audio files found in the specified range.'
                print(error)
                return False
            concat_dir = session['process_dir']
            concat_list = os.path.join(concat_dir, 'concat_list_sentences.txt')
            with open(concat_list, 'w') as f:
                for path in selected_files:
                    if session['cancellation_requested']:
                        msg = 'Cancel requested'
                        print(msg)
                        return False
                    f.write(f"file '{path.replace(os.sep, '/')}'\n")
            result = assemble_audio_chunks(concat_list, file, session.get('is_gui_process'))
            if not result:
                error = 'combine_audio_sentences() FFmpeg concat failed.'
                print(error)
                return False
            msg = f'********* Combined block audio file saved in {file}'
            print(msg)
            return True
    except Exception as e:
        DependencyError(e)
    return False

def combine_audio_chapters(session_id:str)->list[str]|None:

    def generate_ffmpeg_metadata(part_chapters:list[tuple[str,str]], output_metadata_path:str, default_audio_proc_format:str)->str|bool:
        try:
            out_fmt = session['output_format']
            is_mp4_like = out_fmt in ['mp4', 'm4a', 'm4b', 'mov']
            is_vorbis = out_fmt in ['ogg', 'webm']
            is_mp3 = out_fmt == 'mp3'
            def tag(key):
                return key.upper() if is_vorbis else key
            ffmpeg_metadata = ';FFMETADATA1\n'
            if session['metadata'].get('title'):
                ffmpeg_metadata += f"{tag('title')}={session['metadata']['title']}\n"
            if session['metadata'].get('creator'):
                ffmpeg_metadata += f"{tag('artist')}={session['metadata']['creator']}\n"
            if session['metadata'].get('language'):
                ffmpeg_metadata += f"{tag('language')}={session['metadata']['language']}\n"
            if session['metadata'].get('description'):
                ffmpeg_metadata += f"{tag('description')}={session['metadata']['description']}\n"
            if session['metadata'].get('publisher') and (is_mp4_like or is_mp3):
                ffmpeg_metadata += f"{tag('publisher')}={session['metadata']['publisher']}\n"
            if session['metadata'].get('published'):
                try:
                    if '.' in session['metadata']['published']:
                        year = datetime.strptime(session['metadata']['published'], '%Y-%m-%dT%H:%M:%S.%f%z').year
                    else:
                        year = datetime.strptime(session['metadata']['published'], '%Y-%m-%dT%H:%M:%S%z').year
                except Exception:
                    year = datetime.now().year
            else:
                year = datetime.now().year
            if is_vorbis:
                ffmpeg_metadata += f"{tag('date')}={year}\n"
            else:
                ffmpeg_metadata += f"{tag('year')}={year}\n"
            if session['metadata'].get('identifiers') and isinstance(session['metadata']['identifiers'], dict):
                if is_mp3 or is_mp4_like:
                    isbn = session['metadata']['identifiers'].get('isbn')
                    if isbn:
                        ffmpeg_metadata += f"{tag('isbn')}={isbn}\n"
                    asin = session['metadata']['identifiers'].get('mobi-asin')
                    if asin:
                        ffmpeg_metadata += f"{tag('asin')}={asin}\n"
            start_time = 0
            for filename, chapter_title in part_chapters:
                if session['cancellation_requested']:
                    msg = 'Cancel requested'
                    print(msg)
                    return False
                filepath = os.path.join(session['chapters_dir'], filename)
                duration_ms = len(AudioSegment.from_file(filepath, format=default_audio_proc_format))
                clean_title = re.sub(r'(^#)|[=\\]|(-$)', lambda m: '\\' + (m.group(1) or m.group(0)), sanitize_meta_chapter_title(chapter_title))
                ffmpeg_metadata += '[CHAPTER]\nTIMEBASE=1/1000\n'
                ffmpeg_metadata += f'START={start_time}\nEND={start_time + duration_ms}\n'
                ffmpeg_metadata += f"{tag('title')}={clean_title}\n"
                start_time += duration_ms
            with open(output_metadata_path, 'w', encoding='utf-8') as f:
                f.write(ffmpeg_metadata)
            return output_metadata_path
        except Exception as e:
            error = f'generate_ffmpeg_metadata() Error: Failed to process {txt_file} → {out_file}: {e}'
            print(error)
            return False

    def export_audio(ffmpeg_combined_audio:str, ffmpeg_metadata_file:str, ffmpeg_final_file:str)->bool:
        try:
            if session['cancellation_requested']:
                msg = 'Cancel requested'
                print(msg)
                return False
            cover_path = None
            ffprobe_cmd = [
                shutil.which('ffprobe'), '-v', 'error', '-threads', '0', '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_name,sample_rate,sample_fmt',
                '-of', 'default=nokey=1:noprint_wrappers=1', ffmpeg_combined_audio
            ]
            probe = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
            codec_info = probe.stdout.strip().splitlines()
            input_codec = codec_info[0] if len(codec_info) > 0 else None
            input_rate = codec_info[1] if len(codec_info) > 1 else None
            cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-hwaccel', 'auto', '-thread_queue_size', '1024', '-i', ffmpeg_combined_audio]
            target_codec, target_rate = None, None
            if session['output_format'] == 'wav':
                target_codec = 'pcm_s16le'
                target_rate = '44100'
                cmd += ['-map', '0:a', '-ar', target_rate, '-sample_fmt', 's16']
            elif session['output_format'] == 'aac':
                target_codec = 'aac'
                target_rate = '44100'
                cmd += ['-c:a', 'aac', '-b:a', '192k', '-ar', target_rate, '-movflags', '+faststart']
            elif session['output_format'] == 'flac':
                target_codec = 'flac'
                target_rate = '44100'
                cmd += ['-c:a', 'flac', '-compression_level', '5', '-ar', target_rate]
            else:
                cmd += ['-f', 'ffmetadata', '-i', ffmpeg_metadata_file, '-map', '0:a']
                if session['output_format'] in ['m4a', 'm4b', 'mp4', 'mov']:
                    target_codec = 'aac'
                    target_rate = '44100'
                    cmd += ['-c:a', 'aac', '-b:a', '192k', '-ar', target_rate, '-movflags', '+faststart+use_metadata_tags']
                elif session['output_format'] == 'mp3':
                    target_codec = 'mp3'
                    target_rate = '44100'
                    cmd += ['-c:a', 'libmp3lame', '-b:a', '192k', '-ar', target_rate]
                elif session['output_format'] == 'webm':
                    target_codec = 'opus'
                    target_rate = '48000'
                    cmd += ['-c:a', 'libopus', '-b:a', '192k', '-ar', target_rate]
                elif session['output_format'] == 'ogg':
                    target_codec = 'opus'
                    target_rate = '48000'
                    cmd += ['-c:a', 'libopus', '-compression_level', '0', '-b:a', '192k', '-ar', target_rate]
                cmd += ['-map_metadata', '1'] 
            if session['output_channel'] == 'stereo':
                cmd += ['-ac', '2']
            else:
                cmd += ['-ac', '1']
            if input_codec == target_codec and input_rate == target_rate:
                cmd = [
                    shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-hwaccel', 'auto', '-thread_queue_size', '1024', '-i', ffmpeg_combined_audio,
                    '-threads', '0', '-f', 'ffmetadata', '-i', ffmpeg_metadata_file,
                    '-map', '0:a', '-map_metadata', '1', '-c', 'copy',
                    '-progress', 'pipe:2',
                    '-y', ffmpeg_final_file
                ]
            else:
                cmd += [
                    '-filter_threads', '0',
                    '-filter_complex_threads', '0',
                    '-af', 'loudnorm=I=-16:LRA=11:TP=-1.5:linear=true,afftdn=nf=-70',
                    '-threads', '0',
                    '-progress', 'pipe:2',
                    '-y', ffmpeg_final_file
                ]
            is_gui_process = session['is_gui_process']
            proc_pipe = SubprocessPipe(cmd, is_gui_process=is_gui_process, total_duration=get_audio_duration(ffmpeg_combined_audio), msg='Export')
            if proc_pipe.result:
                if os.path.exists(ffmpeg_final_file) and os.path.getsize(ffmpeg_final_file) > 0:
                    if session['output_format'] in ['mp3', 'm4a', 'm4b', 'mp4']:
                        if session['cover'] is not None:
                            cover_path = session['cover']
                            msg = f'Adding cover {cover_path} into the final audiobook file…'
                            print(msg)
                            if session['output_format'] == 'mp3':
                                from mutagen.mp3 import MP3
                                from mutagen.id3 import ID3, APIC, error
                                audio = MP3(ffmpeg_final_file, ID3=ID3)
                                try:
                                    audio.add_tags()
                                except error:
                                    pass
                                with open(cover_path, 'rb') as img:
                                    audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=img.read()))
                            elif session['output_format'] in ['mp4', 'm4a', 'm4b']:
                                from mutagen.mp4 import MP4, MP4Cover
                                audio = MP4(ffmpeg_final_file)
                                with open(cover_path, 'rb') as f:
                                    cover_data = f.read()
                                audio['covr'] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
                            if audio:
                                audio.save()
                    final_vtt = f"{Path(ffmpeg_final_file).stem}.vtt"
                    proc_vtt_path = os.path.join(session['process_dir'], final_vtt)
                    final_vtt_path = os.path.join(session['audiobooks_dir'], final_vtt)
                    shutil.move(proc_vtt_path, final_vtt_path)
                    return True
                else:
                    error = f"{Path(ffmpeg_final_file).name} is corrupted or does not exist"
                    print(error)
        except Exception as e:
            error = f'Export failed: {e}'
            print(error)
            return False

    try:
        session = context.get_session(session_id)
        if session and session.get('id', False):
            chapter_files = [f for f in os.listdir(session['chapters_dir']) if f.endswith(f'.{default_audio_proc_format}')]
            chapter_files = sorted(chapter_files, key=lambda x: int(re.search(r'\d+', x).group()))
            chapter_titles = [c[0] for c in session['chapters']]
            is_gui_process = session['is_gui_process']
            if len(chapter_files) == 0:
                print('No block files exists!')
                return None
            chunks_size = 892
            total_duration = 0.0
            durations = []
            for i in range(0, len(chapter_files), chunks_size):
                filepaths = [
                    os.path.join(session['chapters_dir'], f)
                    for f in chapter_files[i:i + chunks_size]
                ]
                durations_dict = get_audiolist_duration(filepaths)
                for path in filepaths:
                    dur = durations_dict.get(path, 0.0)
                    durations.append(dur)
                    total_duration += dur
            assert len(durations) == len(chapter_files)
            exported_files = []
            concat_dir = session['process_dir']
            if session['output_split']:
                part_files = []
                part_chapter_indices = []
                cur_part = []
                cur_indices = []
                cur_duration = 0
                max_part_duration = int(session['output_split_hours']) * 3600
                needs_split = total_duration > (int(session['output_split_hours']) * 2) * 3600
                for idx, (file, dur) in enumerate(zip(chapter_files, durations)):
                    if session['cancellation_requested']:
                        msg = 'Cancel requested'
                        print(msg)
                        return None
                    if cur_part and (cur_duration + dur > max_part_duration):
                        part_files.append(cur_part)
                        part_chapter_indices.append(cur_indices)
                        cur_part = []
                        cur_indices = []
                        cur_duration = 0
                    cur_part.append(file)
                    cur_indices.append(idx)
                    cur_duration += dur
                if cur_part:
                    part_files.append(cur_part)
                    part_chapter_indices.append(cur_indices)
                for part_idx, (part_file_list, indices) in enumerate(zip(part_files, part_chapter_indices)):
                    concat_list = os.path.join(concat_dir, f'concat_list_chapters_{part_idx+1:02d}.txt')
                    with open(concat_list, 'w') as f:
                        for file in part_file_list:
                            if session['cancellation_requested']:
                                msg = 'Cancel requested'
                                print(msg)
                                return None
                            path = Path(session['chapters_dir']) / file
                            f.write(f"file '{path.as_posix()}'\n")
                    merged_audio = Path(session['process_dir']) / f"{get_sanitized(session['metadata']['title'])}_part{part_idx+1}.{default_audio_proc_format}"
                    result = assemble_audio_chunks(concat_list, merged_audio, is_gui_process)
                    if not result:
                        error = f'assemble_audio_chunks() Final merge failed for part {part_idx+1}.'
                        print(error)
                        return None
                    metadata_file = Path(session['process_dir']) / f'metadata_part{part_idx+1}.txt'
                    part_chapters = [(chapter_files[i], chapter_titles[i]) for i in indices]
                    generate_ffmpeg_metadata(part_chapters, str(metadata_file), default_audio_proc_format)
                    final_file = Path(session['audiobooks_dir']) / (f"{session['final_name'].rsplit('.', 1)[0]}_part{part_idx+1}.{session['output_format']}" if needs_split else session['final_name'])
                    if export_audio(str(merged_audio), str(metadata_file), str(final_file)):
                        exported_files.append(str(final_file))
            else:
                concat_list = os.path.join(concat_dir, f'concat_list_chapters_1.txt')
                merged_audio = Path(session['process_dir']) / f"{get_sanitized(session['metadata']['title'])}.{default_audio_proc_format}"
                with open(concat_list, 'w') as f:
                    for file in chapter_files:
                        if session['cancellation_requested']:
                            msg = 'Cancel requested'
                            print(msg)
                            return None
                        path = os.path.join(session['chapters_dir'], file).replace("\\", "/")
                        f.write(f"file '{path}'\n")
                if is_gui_process:
                    progress_bar = gr.Progress(track_tqdm=False)
                result = assemble_audio_chunks(concat_list, merged_audio, is_gui_process)
                if not result:
                    print(f'assemble_audio_chunks() Final merge failed for {merged_audio}.')
                    return None
                metadata_file = os.path.join(session['process_dir'], 'metadata.txt')
                chapters_zip = list(zip(chapter_files, chapter_titles))
                generate_ffmpeg_metadata(chapters_zip, metadata_file, default_audio_proc_format)
                final_file = os.path.join(session['audiobooks_dir'], session['final_name'])
                if export_audio(merged_audio, metadata_file, final_file):
                    exported_files.append(final_file)
            return exported_files if exported_files else None
        return None
    except Exception as e:
        DependencyError(e)
        return None

def assemble_audio_chunks(txt_file:str, out_file:str, is_gui_process:bool)->bool:

    if is_gui_process:
        progress_bar = gr.Progress(track_tqdm=False)

    def on_progress(p:float)->None:
        if progress_bar:
            progress_bar(p / 100.0, desc='Assemble')

    try:
        total_duration = 0.0
        filepaths = []
        try:
            with open(txt_file, 'r') as f:
                for line in f:
                    if line.strip().startswith('file'):
                        file_path = (
                            line.strip()
                            .split('file ')[1]
                            .strip()
                            .strip("'")
                            .strip('"')
                        )
                        if os.path.exists(file_path):
                            filepaths.append(file_path)
            durations = get_audiolist_duration(filepaths)
            total_duration = sum(durations.values())
        except Exception as e:
            print(f'assemble_audio_chunks() open file {txt_file} Error: {e}')
            return False

        ffmpeg = shutil.which('ffmpeg')
        cmd = [
            ffmpeg,
            '-hide_banner',
            '-nostats',
            '-safe', '0',
            '-f', 'concat',
            '-i', txt_file,
            '-c:a', default_audio_proc_format,
            '-map_metadata', '-1',
            '-threads', '0',
            '-progress', 'pipe:2',
            '-y', out_file
        ]
        proc_pipe = SubprocessPipe(
            cmd=cmd,
            is_gui_process=is_gui_process,
            total_duration=total_duration,
            msg='Assemble',
            on_progress=on_progress
        )
        if proc_pipe.result and os.path.exists(out_file):
            msg = f'Completed → {out_file}'
            print(msg)
            return True
        else:
            error = f'Failed (proc_pipe) → {out_file}'
            print(error)
            return False
    except subprocess.CalledProcessError as e:
        DependencyError(e)
        return False
    except Exception as e:
        error = f'assemble_audio_chunks() Error: Failed to process {txt_file} → {out_file}: {e}'
        print(error)
        return False

def ellipsize_utf8_bytes(s:str, max_bytes:int, ellipsis:str='…')->str:
    s = '' if s is None else str(s)
    if max_bytes <= 0:
        return ''
    raw = s.encode('utf-8')
    e = ellipsis.encode('utf-8')
    if len(raw) <= max_bytes:
        return s
    if len(e) >= max_bytes:
        # return as many bytes of the ellipsis as fit
        return e[:max_bytes].decode('utf-8', errors='ignore')
    budget = max_bytes - len(e)
    out = bytearray()
    for ch in s:
        b = ch.encode('utf-8')
        if len(out) + len(b) > budget:
            break
        out.extend(b)
    return out.decode('utf-8') + ellipsis

def sanitize_meta_chapter_title(title:str, max_bytes:int=140)->str:
    # avoid None and embedded NULs which some muxers accidentally keep
    title = (title or '').replace('\x00', '')
    title = title.replace(sml_token('pause'), '')
    return ellipsize_utf8_bytes(title, max_bytes=max_bytes, ellipsis='…')

def clear_folder(folder_path:str)->None:
    for name in os.listdir(folder_path):
        path = os.path.join(folder_path, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
        else:
            shutil.rmtree(path)

def delete_unused_tmp_dirs(web_dir:str, days:int, session_id:str)->None:
    session = context.get_session(session_id)
    if session and session.get('id', False):
        dir_array = [
            tmp_dir,
            web_dir,
            os.path.join(models_dir, '__sessions'),
            os.path.join(voices_dir, '__sessions')
        ]
        current_user_dirs = {
            f"proc-{session['id']}",
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
                                    msg = f'Deleted expired session: {full_dir_path}'
                                    print(msg)
                            except Exception as e:
                                error = f'Error deleting {full_dir_path}: {e}'
                                print(error)

def get_compatible_tts_engines(language:str)->list[str]:
    return [
        engine
        for engine, cfg in default_engine_settings.items()
        if language in cfg.get('languages', {})
    ]

def convert_ebook_batch(args:dict)->tuple:
    if isinstance(args['ebook_list'], list):
        ebook_list = args['ebook_list'][:]
        for file in ebook_list: # Use a shallow copy
            if any(file.endswith(ext) for ext in ebook_formats):
                args['ebook'] = file
                print(f'Processing eBook file: {os.path.basename(file)}')
                progress_status, passed = convert_ebook(args)
                if passed is False:
                    msg = f'Conversion failed: {progress_status}'
                    print(msg)
                    if not args['is_gui_process']:
                        sys.exit(1)
                args['ebook_list'].remove(file) 
        reset_session(args['id'])
        return progress_status, passed
    else:
        error = f'the ebooks source is not a list!'
        print(error)
        if not args['is_gui_process']:
            sys.exit(1)       

def convert_ebook(args:dict)->tuple:
    try:
        if args.get('event') == 'blocks_confirmed':
            if args.get('id', False):
                progress_status, passed = finalize_audiobook(args['id'])
                return progress_status, passed
            else:
                error = f"convert_ebook() error: args['id'] is False"
                print(error)
                return error, False
        else:
            global context        
            error = None
            session_id = None
            info_session = None
            if args['language'] is not None:
                if not os.path.splitext(args['ebook'])[1]:
                    error = f"{args['ebook']} needs a format extension."
                    print(error)
                    return error, False
                if not os.path.exists(args['ebook']):
                    error = 'File does not exist or Directory empty.'
                    print(error)
                    return error, False
                try:
                    if len(args['language']) in (2, 3):
                        lang_dict = Lang(args['language'])
                        if lang_dict:
                            args['language'] = lang_dict.pt3
                            args['language_iso1'] = lang_dict.pt1
                    else:
                        args['language_iso1'] = None
                except Exception as e:
                    pass
                if args['language'] not in language_mapping.keys():
                    error = 'The language you provided is not (yet) supported'
                    print(error)
                    return error, False
                if args['id'] is not None:
                    session_id = str(args['id'])
                    session = context.get_session(session_id)
                    if not session:
                        session = context.set_session(session_id)
                else:
                    session_id = str(uuid.uuid4())
                    session = context.set_session(session_id)
                    if not context_tracker.start_session(session_id):
                        error = 'convert_ebook() error: Session initialization failed!'
                        print(error)
                        return error, False
                session['custom_model_dir'] = os.path.join(models_dir, '__sessions',f"model-{session_id}")
                session['script_mode'] = str(args['script_mode']) if args.get('script_mode') is not None else NATIVE
                session['is_gui_process'] = bool(args['is_gui_process'])
                session['ebook'] = str(args['ebook']) if args.get('ebook') else None
                session['ebook_list'] = list(args['ebook_list']) if args.get('ebook_list') else None
                session['chapters_preview'] = bool(args['chapters_preview']) if args.get('chapters_preview') else False
                session['device'] = str(args['device'])
                session['language'] = str(args['language'])
                session['language_iso1'] = str(args['language_iso1'])
                session['tts_engine'] = str(args['tts_engine']) if args['tts_engine'] is not None else str(get_compatible_tts_engines(args['language'])[0])
                session['custom_model'] =  os.path.join(session['custom_model_dir'], args['custom_model']) if args['custom_model'] is not None else None
                session['fine_tuned'] = str(args['fine_tuned'])
                session['voice'] = str(args['voice']) if args['voice'] is not None else None
                session['xtts_temperature'] =  float(args['xtts_temperature'])
                session['xtts_length_penalty'] = float(args['xtts_length_penalty'])
                session['xtts_num_beams'] = int(args['xtts_num_beams'])
                session['xtts_repetition_penalty'] = float(args['xtts_repetition_penalty'])
                session['xtts_top_k'] =  int(args['xtts_top_k'])
                session['xtts_top_p'] = float(args['xtts_top_p'])
                session['xtts_speed'] = float(args['xtts_speed'])
                session['xtts_enable_text_splitting'] = bool(args['xtts_enable_text_splitting'])
                session['bark_text_temp'] =  float(args['bark_text_temp'])
                session['bark_waveform_temp'] =  float(args['bark_waveform_temp'])
                session['audiobooks_dir'] = str(args['audiobooks_dir']) if args['audiobooks_dir'] else None
                session['output_format'] = str(args['output_format'])
                session['output_channel'] = str(args['output_channel'])
                session['output_split'] = bool(args['output_split'])
                session['output_split_hours'] = args['output_split_hours']if args['output_split_hours'] is not None else default_output_split_hours
                session['model_cache'] = f"{session['tts_engine']}-{session['fine_tuned']}"
                cleanup_models_cache()
                if not session['is_gui_process']:
                    session['system'] = sys.platform
                    session['session_dir'] = os.path.join(tmp_dir, f"proc-{session['id']}")
                    session['voice_dir'] = os.path.join(voices_dir, '__sessions', f"voice-{session['id']}", session['language'])
                    os.makedirs(session['voice_dir'], exist_ok=True)
                    if session['custom_model'] is not None:
                        if not os.path.exists(session['custom_model_dir']):
                            os.makedirs(session['custom_model_dir'], exist_ok=True)
                        custom_src_path = Path(session['custom_model'])
                        custom_src_name = custom_src_path.stem
                        if not os.path.exists(os.path.join(session['custom_model_dir'], custom_src_name)):
                            try:
                                if analyze_uploaded_file(session['custom_model'], default_engine_settings[session['tts_engine']]['files']):
                                    model = extract_custom_model(session_id)
                                    if model is not None:
                                        session['custom_model'] = model
                                    else:
                                        error = f"{model} could not be extracted or mandatory files are missing"
                                else:
                                    error = f'{os.path.basename(f)} is not a valid model or some required files are missing'
                            except ModuleNotFoundError as e:
                                error = f"No presets module for TTS engine '{session['tts_engine']}': {e}"
                                print(error)
                    if session['voice'] is not None:
                        voice_name = os.path.splitext(os.path.basename(session['voice']))[0].replace('&', 'And')
                        voice_name = get_sanitized(voice_name)
                        final_voice_file = os.path.join(session['voice_dir'], f'{voice_name}.wav')
                        if not os.path.exists(final_voice_file):
                            extractor = VoiceExtractor(session, session['voice'], voice_name)
                            status, msg = extractor.extract_voice()
                            if status:
                                session['voice'] = final_voice_file
                            else:
                                error = f'VoiceExtractor.extract_voice() failed! {msg}'
                                print(error)
                if error is None:
                    if session['script_mode'] == NATIVE:
                        is_installed = check_programs('Calibre', 'ebook-convert', '--version')
                        if not is_installed:
                            error = f'check_programs() Calibre failed: {e}'
                        is_installed = check_programs('FFmpeg', 'ffmpeg', '-version')
                        if not is_installed:
                            error = f'check_programs() FFMPEG failed: {e}'
                    if error is None:
                        old_session_dir = os.path.join(tmp_dir, f"ebook-{session['id']}")
                        if os.path.isdir(old_session_dir):
                            os.rename(old_session_dir, session['session_dir'])
                        session['final_name'] = get_sanitized(Path(session['ebook']).stem + '.' + session['output_format'])
                        session['process_dir'] = os.path.join(session['session_dir'], f"{hashlib.md5(os.path.join(session['audiobooks_dir'], session['final_name']).encode()).hexdigest()}")
                        session['chapters_dir'] = os.path.join(session['process_dir'], "chapters")
                        session['sentences_dir'] = os.path.join(session['chapters_dir'], 'sentences')
                        if prepare_dirs(args['ebook'], session_id):
                            session['filename_noext'] = os.path.splitext(os.path.basename(session['ebook']))[0]
                            msg = ''
                            msg_extra = ''
                            vram_dict = VRAMDetector().detect_vram(session['device'], session['script_mode'])
                            print(f'vram_dict: {vram_dict}')
                            total_vram_gb = vram_dict.get('total_vram_gb', 0)
                            session['free_vram_gb'] = vram_dict.get('free_vram_gb', 0)
                            if session['free_vram_gb'] == 0:
                                session['free_vram_gb'] = 1.0
                                msg_extra += '<br/>Memory capacity not detected! restrict to 1GB max' if session['free_vram_gb'] == 0 else f"<br/>Memory detected with {session['free_vram_gb']}GB"
                            else:
                                msg_extra += f"<br/>Free Memory available: {session['free_vram_gb']}GB"
                                if session['free_vram_gb'] > 4.0:
                                    if session['tts_engine'] == TTS_ENGINES['BARK']:
                                        os.environ['SUNO_USE_SMALL_MODELS'] = 'False'                        
                            if session['device'] == devices['CUDA']['proc'] or session['device'] == devices['JETSON']['proc']:
                                if not devices['CUDA']['found']:
                                    session['device'] = devices['CPU']['proc']
                                    msg += f'CUDA not supported by the Torch installed!<br/>Read {default_gpu_wiki}<br/>Switching to CPU'
                            elif session['device'] == devices['MPS']['proc']:
                                if not devices['MPS']['found']:
                                    session['device'] = devices['CPU']['proc']
                                    msg += f'MPS not supported by the Torch installed!<br/>Read {default_gpu_wiki}<br/>Switching to CPU'
                            elif session['device'] == devices['ROCM']['proc']:
                                if not devices['ROCM']['found']:
                                    session['device'] = devices['CPU']['proc']
                                    msg += f'ROCM not supported by the Torch installed!<br/>Read {default_gpu_wiki}<br/>Switching to CPU'
                            elif session['device'] == devices['XPU']['proc']:
                                if not devices['XPU']['found']:
                                    session['device'] = devices['CPU']['proc']
                                    msg += f"XPU not supported by the Torch installed!<br/>Read {default_gpu_wiki}<br/>Switching to CPU"
                            if session['tts_engine'] == TTS_ENGINES['BARK']:
                                if session['free_vram_gb'] < 12.0:
                                    os.environ['SUNO_OFFLOAD_CPU'] = "True"
                                    os.environ['SUNO_USE_SMALL_MODELS'] = "True"
                                    msg_extra += f"<br/>Switching BARK to SMALL models"  
                                else:
                                    os.environ['SUNO_OFFLOAD_CPU'] = "False"
                                    os.environ['SUNO_USE_SMALL_MODELS'] = "False"
                            if msg == '':
                                msg = f"Using {session['device'].upper()}"
                            msg += msg_extra;
                            device_vram_required = default_engine_settings[session['tts_engine']]['rating']['RAM'] if session['device'] == devices['CPU']['proc'] else default_engine_settings[session['tts_engine']]['rating']['VRAM']
                            if float(total_vram_gb) >= float(device_vram_required):
                                if session['is_gui_process']:
                                    show_alert({"type": "warning", "msg": msg})
                                print(msg.replace('<br/>','\n'))
                                session['epub_path'] = os.path.join(session['process_dir'], f"__{session['filename_noext']}.epub")
                                checksum_path = os.path.join(session['process_dir'], 'checksum')
                                checksum, error = compare_checksums(session['ebook'], checksum_path)
                                if error is None:
                                    if not checksum:
                                        session['blocks'] = []
                                        session['chapters'] = []
                                        result_epub = convert2epub(session_id)
                                        if not result_epub:
                                            error = 'convert2epub() failed!'
                                    else:
                                        json_chapters_file = os.path.join(session['process_dir'], f"__{session['filename_noext']}.json")
                                        if os.path.exists(json_chapters_file):
                                            session['chapters'] = load_json_chapters(json_chapters_file)
                                    if error is None:
                                        epubBook = epub.read_epub(session['epub_path'], {'ignore_ncx': True})
                                        if epubBook:
                                            metadata = dict(session['metadata'])
                                            for key, value in metadata.items():
                                                data = epubBook.get_metadata('DC', key)
                                                if data:
                                                    for value, attributes in data:
                                                        metadata[key] = value
                                            metadata['language'] = session['language']
                                            metadata['title'] = metadata['title'] = metadata['title'] or Path(session['ebook']).stem.replace('_',' ')
                                            metadata['creator'] =  False if not metadata['creator'] or metadata['creator'] == 'Unknown' else metadata['creator']
                                            session['metadata'] = metadata                  
                                            try:
                                                if len(session['metadata']['language']) == 2:
                                                    lang_dict = Lang(session['language'])
                                                    if lang_dict:
                                                        session['metadata']['language'] = lang_dict.pt3
                                            except Exception as e:
                                                pass                         
                                            if session['metadata']['language'] != session['language']:
                                                error = f"WARNING!!! language selected {session['language']} differs from the EPUB file language {session['metadata']['language']}"
                                                print(error)
                                                if session['is_gui_process']:
                                                    show_alert({"type": "warning", "msg": error})
                                            is_lang_in_tts_engine = (
                                                session.get('tts_engine') in default_engine_settings and
                                                session.get('language') in default_engine_settings[session['tts_engine']].get('languages', {})
                                            )
                                            if is_lang_in_tts_engine:
                                                session['cover'] = get_cover(epubBook, session_id)
                                                if session['cover']:
                                                    if not session['blocks']:
                                                        session['blocks'] = get_blocks(session_id, epubBook)
                                                    if session['blocks']:
                                                        if session['chapters_preview']:
                                                           return 'confirm_blocks', True
                                                        else:
                                                            progress_status, passed = finalize_audiobook(session_id)
                                                        return progress_status, passed
                                                    else:
                                                        error = f"get_blocks() failed! {session['blocks']}"
                                                else:
                                                    error = 'get_cover() failed!'
                                            else:
                                                 error = f"language {session['language']} not supported by {session['tts_engine']}!"
                                        else:
                                            error = 'epubBook.read_epub failed!'
                            else:
                                error = f"Your device has not enough memory ({total_vram_gb}GB) to run {session['tts_engine']} engine ({device_vram_required}GB)"
                        else:
                            error = f"Temporary directory {session['process_dir']} not removed due to failure."
            else:
                error = f"Language {args['language']} is not supported."
        if session['cancellation_requested']:
            error = 'Cancelled' if error is None else error + '. Cancelled'
        print(error)
        if session['is_gui_process']:
            show_alert({"type": "warning", "msg": error})
        return error, False
    except Exception as e:
        print(f'convert_ebook() Exception: {e}')
        return e, False

def finalize_audiobook(session_id:str)->tuple:
    session = context.get_session(session_id)
    if session and session.get('id', False):
        if session['blocks']:
            chapters = []
            msg = f'Get sentences…'
            print(msg)
            for text in session['blocks']:
                if text:
                    sentences_list = get_sentences(text, session_id)
                    if sentences_list is None:
                        error = 'No sentences found!'
                        print(error)
                        return error, False
                    if sentences_list:
                        chapters.append(sentences_list)
            session['chapters'] = chapters
            json_chapters = os.path.join(session['process_dir'], f"__{session['filename_noext']}.json")
            save_json_chapters(session_id, json_chapters)
            if convert_chapters2audio(session_id):
                msg = 'Conversion successful. Combining sentences and chapters…'
                show_alert({"type": "info", "msg": msg})
                exported_files = combine_audio_chapters(session['id'])               
                if exported_files is not None:
                    progress_status = f'Audiobook {", ".join(os.path.basename(f) for f in exported_files)} created!'
                    session['audiobook'] = exported_files[-1]
                    if not session['is_gui_process']:
                        process_dir = os.path.join(session['session_dir'], f"{hashlib.md5(os.path.join(session['audiobooks_dir'], session['audiobook']).encode()).hexdigest()}")
                        shutil.rmtree(process_dir, ignore_errors=True)
                    info_session = f"\n*********** Session: {session_id} **************\nIn headless mode, store it in case of interruption, crash, or reuse of a custom model or custom voice.\nYou can resume the conversion with the --session option."
                    print(info_session)
                    return progress_status, True
                else:
                    error = 'combine_audio_chapters() error: exported_files not created!'
            else:
                error = 'convert_chapters2audio() failed!'
        else:
            error = 'finalize_audiobook() failed!'
    return error, False

def restore_session_from_data(data:dict, session:dict)->None:
    try:
        for key, value in data.items():
            if key in session:
                if isinstance(value, dict) and isinstance(session[key], dict):
                    restore_session_from_data(value, session[key])
                else:
                    if value is None and session[key] is not None:
                        continue
                    session[key] = value
    except Exception as e:
        DependencyError(e)

def cleanup_session(req:gr.Request)->None:
    socket_hash = req.session_hash
    if any(socket_hash in session for session in context.sessions.values()):
        session_id = context.find_id_by_hash(socket_hash)
        context_tracker.end_session(session_id, socket_hash)

def reset_session(session_id:str)->None:
    session = context.get_session(session_id)
    data = {
        "process_id": None,
        "event": None,
        "ticker": 0,
        "process_dir": None,
        "ebook": None,
        "ebook_list": None,
        "epub_path": None,
        "filename_noext": None,
        "final_name": None,
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
        },
        "chapters": [],
        "cover": None,
        "duration": 0,
        "playback_time": 0,
        "playback_volume": 0
    }
    restore_session_from_data(data, session)

def cleanup_models_cache()->None:
    try:
        active_models = {
            cache
            for session in context.sessions.values()
            for cache in (session.get('model_cache'), session.get('model_zs_cache'), session.get('stanza_cache'))
            if cache is not None
        }
        for key in list(loaded_tts.keys()):
            if key not in active_models:
                del loaded_tts[key]
        gc.collect()
    except Exception as e:
        error = f"cleanup_models_cache() error: {e}"
        print(error)

def show_alert(state:dict)->None:
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

def alert_exception(error:str, session_id:str|None)->None:
    if session_id is not None:
        session = context.get_session(session_id)
        if session and session.get('id', False):
            session['status'] = 'ready'
    print(error)
    gr.Error(error)
    DependencyError(error)

def get_all_ip_addresses()->list:
    ip_addresses = []
    for interface, addresses in psutil.net_if_addrs().items():
        for address in addresses:
            if address.family in [socket.AF_INET, socket.AF_INET6]:
                ip_addresses.append(address.address) 
    return ip_addresses