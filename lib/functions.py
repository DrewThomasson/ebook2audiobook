# NOTE!!NOTE!!!NOTE!!NOTE!!!NOTE!!NOTE!!!NOTE!!NOTE!!!
# THE WORD "CHAPTER" IN THE CODE DOES NOT MEAN
# IT'S THE REAL CHAPTER OF THE EBOOK SINCE NO STANDARDS
# ARE DEFINING A CHAPTER ON .EPUB FORMAT. THE WORD "BLOCK"
# IS USED TO PRINT IT OUT TO THE TERMINAL, AND "CHAPTER" TO THE CODE
# WHICH IS LESS GENERIC FOR THE DEVELOPERS

import argparse, asyncio, csv, fnmatch, hashlib, io, json, math, os, platform, random, shutil, socket, subprocess, sys, tempfile, threading, time, traceback
import unicodedata, urllib.request, uuid, zipfile, ebooklib, gradio as gr, psutil, pymupdf4llm, regex as re, requests, stanza, torch, uvicorn

from soynlp.tokenizer import LTokenizer
from pythainlp.tokenize import word_tokenize
from sudachipy import dictionary, tokenizer
from PIL import Image
from tqdm import tqdm
from bs4 import BeautifulSoup, NavigableString, Tag
from collections import Counter
from collections.abc import Mapping
from collections.abc import MutableMapping
from datetime import datetime
from ebooklib import epub
from glob import glob
from iso639 import languages
from markdown import markdown
from multiprocessing import Pool, cpu_count
from multiprocessing import Manager, Event
from multiprocessing.managers import DictProxy, ListProxy
from num2words import num2words
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import mediainfo
from queue import Queue, Empty
from types import MappingProxyType
from urllib.parse import urlparse
from starlette.requests import ClientDisconnect

from lib import *
from lib.classes.voice_extractor import VoiceExtractor
from lib.classes.tts_manager import TTSManager
#from lib.classes.redirect_console import RedirectConsole
#from lib.classes.argos_translator import ArgosTranslator

context = None
is_gui_process = False
active_sessions = set()

#import logging
#logging.basicConfig(
#    level=logging.INFO, # DEBUG for more verbosity
#    format="%(asctime)s [%(levelname)s] %(message)s"
#)

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
        error = f'Caught DependencyError: {self}'
        print(error)    
        # Exit the script if it's not a web process
        if not is_gui_process:
            sys.exit(1)

class SessionTracker:
    def __init__(self):
        self.lock = threading.Lock()

    def start_session(self, id):
        with self.lock:
            session = context.get_session(id)
            if session['status'] is None:
                session['status'] = 'ready'
                return True
        return False

    def end_session(self, id, socket_hash):
        active_sessions.discard(socket_hash)
        with self.lock:
            session = context.get_session(id)
            session['cancellation_requested'] = True
            session['tab_id'] = None
            session['status'] = None
            session[socket_hash] = None

class SessionContext:
    def __init__(self):
        self.manager = Manager()
        self.sessions = self.manager.dict()
        self.cancellation_events = {}

    def get_session(self, id):
        if id not in self.sessions:
            self.sessions[id] = recursive_proxy({
                "script_mode": NATIVE,
                "id": id,
                "tab_id": None,
                "process_id": None,
                "status": None,
                "event": None,
                "progress": 0,
                "cancellation_requested": False,
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
                "temperature": default_engine_settings[TTS_ENGINES['XTTSv2']]['temperature'],
                "length_penalty": default_engine_settings[TTS_ENGINES['XTTSv2']]['length_penalty'],
                "num_beams": default_engine_settings[TTS_ENGINES['XTTSv2']]['num_beams'],
                "repetition_penalty": default_engine_settings[TTS_ENGINES['XTTSv2']]['repetition_penalty'],
                "top_k": default_engine_settings[TTS_ENGINES['XTTSv2']]['top_k'],
                "top_p": default_engine_settings[TTS_ENGINES['XTTSv2']]['top_p'],
                "speed": default_engine_settings[TTS_ENGINES['XTTSv2']]['speed'],
                "enable_text_splitting": default_engine_settings[TTS_ENGINES['XTTSv2']]['enable_text_splitting'],
                "text_temp": default_engine_settings[TTS_ENGINES['BARK']]['text_temp'],
                "waveform_temp": default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp'],
                "final_name": None,
                "output_format": default_output_format,
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
                "toc": None,
                "chapters": None,
                "cover": None,
                "duration": 0,
                "playback_time": 0
            }, manager=self.manager)
        return self.sessions[id]

    def find_id_by_hash(self, socket_hash):
        for id, session in self.sessions.items():
            if socket_hash in session:
                return session.get('id')
        return None

ctx_tracker = SessionTracker()

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

def convert2epub(id):
    session = context.get_session(id)
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
            msg = 'File input is a PDF. flatten it in MarkDown...'
            print(msg)
            doc = fitz.open(session['ebook'])
            pdf_metadata = doc.metadata
            filename_no_ext = os.path.splitext(os.path.basename(session['ebook']))[0]
            title = pdf_metadata.get('title') or filename_no_ext
            author = pdf_metadata.get('author') or False
            markdown_text = pymupdf4llm.to_markdown(session['ebook'])
            # Remove single asterisks for italics (but not bold **)
            markdown_text = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?!\*)', r'\1', markdown_text)
            # Remove single underscores for italics (but not bold __)
            markdown_text = re.sub(r'(?<!_)_(?!_)(.*?)_(?!_)', r'\1', markdown_text)
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
                '--page-breaks-before', "//*[name()='h1' or name()='h2' or name()='h3' or name()='h4' or name()='h5']",
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
            image.save(cover_path, format='JPEG')
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
        try:
            toc = epubBook.toc  # Extract TOC
            toc_list = [
                    nt for item in toc if hasattr(item, 'title')
                    if (nt := normalize_text(
                        str(item.title),
                        session['language'],
                        session['language_iso1'],
                        session['tts_engine']
                )) is not None
            ]
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
        stanza_nlp = False
        if session['language'] in year_to_decades_languages:
            stanza.download(session['language_iso1'])
            stanza_nlp = stanza.Pipeline(session['language_iso1'], processors='tokenize,ner')
        is_num2words_compat = get_num2words_compat(session['language_iso1'])
        msg = 'Analyzing numbers, maths signs, dates and time to convert in words...'
        print(msg)
        for doc in all_docs:
            sentences_list = filter_chapter(doc, session['language'], session['language_iso1'], session['tts_engine'], stanza_nlp, is_num2words_compat)
            if sentences_list is None:
                break
            elif len(sentences_list) > 0:
                chapters.append(sentences_list)
        if len(chapters) == 0:
            error = 'No chapters found!'
            return None, None
        return toc, chapters
    except Exception as e:
        error = f'Error extracting main content pages: {e}'
        DependencyError(error)
        return None, None

def filter_chapter(doc, lang, lang_iso1, tts_engine, stanza_nlp, is_num2words_compat):

    def tuple_row(node, last_text_char=None):
        try:
            for child in node.children:
                if isinstance(child, NavigableString):
                    text = child.strip()
                    if text:
                        yield ("text", text)
                        last_text_char = text[-1] if text else last_text_char

                elif isinstance(child, Tag):
                    name = child.name.lower()
                    if name in heading_tags:
                        title = child.get_text(strip=True)
                        if title:
                            yield ("heading", title)
                            last_text_char = title[-1] if title else last_text_char

                    elif name == "table":
                        yield ("table", child)

                    else:
                        return_data = False
                        if name in proc_tags:
                            for inner in tuple_row(child, last_text_char):
                                return_data = True
                                yield inner
                                # Track last char if this is text or heading
                                if inner[0] in ("text", "heading") and inner[1]:
                                    last_text_char = inner[1][-1]

                            if return_data:
                                if name in break_tags:
                                    # Only yield break if last char is NOT alnum or space
                                    if not (last_text_char and (last_text_char.isalnum() or last_text_char.isspace())):
                                        yield ("break", TTS_SML['break'])
                                elif name in heading_tags or name in pause_tags:
                                    yield ("pause", TTS_SML['pause'])

                        else:
                            yield from tuple_row(child, last_text_char)

        except Exception as e:
            error = f'filter_chapter() tuple_row() error: {e}'
            DependencyError(error)
            return None

    try:
        heading_tags = [f'h{i}' for i in range(1, 5)]
        break_tags = ['br', 'p']
        pause_tags = ['div', 'span']
        proc_tags = heading_tags + break_tags + pause_tags
        raw_html = doc.get_body_content().decode("utf-8")
        soup = BeautifulSoup(raw_html, 'html.parser')
        body = soup.body
        if not body or not body.get_text(strip=True):
            return []
        # Skip known non-chapter types
        epub_type = body.get("epub:type", "").lower()
        if not epub_type:
            section_tag = soup.find("section")
            if section_tag:
                epub_type = section_tag.get("epub:type", "").lower()
        excluded = {
            "frontmatter", "backmatter", "toc", "titlepage", "colophon",
            "acknowledgments", "dedication", "glossary", "index",
            "appendix", "bibliography", "copyright-page", "landmark"
        }
        if any(part in epub_type for part in excluded):
            return []
        # remove scripts/styles
        for tag in soup(["script", "style"]):
            tag.decompose()
        tuples_list = list(tuple_row(body))
        if not tuples_list:
            error = 'No tuples_list from body created!'
            print(error)
            return None
        text_list = []
        handled_tables = set()
        prev_typ = None
        for typ, payload in tuples_list:
            if typ == "heading":
                text_list.append(payload.strip())
            elif typ == "break":
                if prev_typ != 'break':
                    text_list.append(TTS_SML['break'])
            elif typ == 'pause':
                if prev_typ != 'pause':
                    text_list.append(TTS_SML['pause'])
            elif typ == "table":
                table = payload
                if table in handled_tables:
                    prev_typ = typ
                    continue
                handled_tables.add(table)
                rows = table.find_all("tr")
                if not rows:
                    prev_typ = typ
                    continue
                headers = [c.get_text(strip=True) for c in rows[0].find_all(["td", "th"])]
                for row in rows[1:]:
                    cells = [c.get_text(strip=True).replace('\xa0', ' ') for c in row.find_all("td")]
                    if not cells:
                        continue
                    if len(cells) == len(headers) and headers:
                        line = " — ".join(f"{h}: {c}" for h, c in zip(headers, cells))
                    else:
                        line = " — ".join(cells)
                    if line:
                        text_list.append(line.strip())
            else:
                text = payload.strip()
                if text:
                    text_list.append(text)
            prev_typ = typ
        max_chars = language_mapping[lang]['max_chars'] - 4
        clean_list = []
        i = 0
        while i < len(text_list):
            current = text_list[i]
            if current == "‡break‡":
                if clean_list:
                    prev = clean_list[-1]
                    if prev in ("‡break‡", "‡pause‡"):
                        i += 1
                        continue
                    if prev and (prev[-1].isalnum() or prev[-1] == ' '):
                        if i + 1 < len(text_list):
                            next_sentence = text_list[i + 1]
                            merged_length = len(prev.rstrip()) + 1 + len(next_sentence.lstrip())
                            if merged_length <= max_chars:
                                # Merge with space handling
                                if not prev.endswith(" ") and not next_sentence.startswith(" "):
                                    clean_list[-1] = prev + " " + next_sentence
                                else:
                                    clean_list[-1] = prev + next_sentence
                                i += 2
                                continue
                            else:
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
        if stanza_nlp:
            # Check if there are positive integers so possible date to convert
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
                        # 2) convert ordinal days like "16th"/"16 th" -> "sixteenth"
                        if is_num2words_compat:
                            processed = re_ordinal.sub(
                                lambda m: num2words(int(m.group(1)), to="ordinal", lang=(lang_iso1 or "en")),
                                processed
                            )
                        else:
                            processed = re_ordinal.sub(
                                lambda m: math2words(m.group(), lang, lang_iso1, tts_engine, is_num2words_compat),
                                processed
                            )
                        # 3) convert other numbers (skip 4-digit years)
                        def _num_repl(m):
                            s = m.group(0)
                            # leave years alone (already handled above)
                            if re.fullmatch(r"\d{4}", s):
                                return s
                            n = float(s) if "." in s else int(s)
                            if is_num2words_compat:
                                return num2words(n, lang=(lang_iso1 or "en"))
                            else:
                                return math2words(m, lang, lang_iso1, tts_engine, is_num2words_compat)

                        processed = re_num.sub(_num_repl, processed)
                        result.append(processed)
                        last_pos = end
                    result.append(text[last_pos:])
                    text = ''.join(result)
                else:
                    if is_num2words_compat:
                        text = re_ordinal.sub(
                            lambda m: num2words(int(m.group(1)), to="ordinal", lang=(lang_iso1 or "en")),
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
        text = roman2number(text)
        text = clock2words(text, lang, lang_iso1, tts_engine, is_num2words_compat)
        text = math2words(text, lang, lang_iso1, tts_engine, is_num2words_compat)
        # build a translation table mapping each bad char to a space
        specialchars_remove_table = str.maketrans({ch: ' ' for ch in specialchars_remove})
        text = text.translate(specialchars_remove_table)
        text = normalize_text(text, lang, lang_iso1, tts_engine)
        # Ensure space before and after punctuation_list
        #pattern_space = re.escape(''.join(punctuation_list))
        #punctuation_pattern_space = r'(?<!\s)([{}])'.format(pattern_space)
        #text = re.sub(punctuation_pattern_space, r' \1', text)
        sentences = get_sentences(text, lang, tts_engine)
        if len(sentences) == 0:
            error = 'No sentences found!'
            print(error)
            return None
        return get_sentences(text, lang, tts_engine)
    except Exception as e:
        error = f'filter_chapter() error: {e}'
        DependencyError(error)
        return None

def get_sentences(text, lang, tts_engine):

    def split_inclusive(text, pattern):
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

    def segment_ideogramms(text):
        sml_pattern = "|".join(re.escape(token) for token in sml_tokens)
        segments = re.split(f"({sml_pattern})", text)
        result = []
        try:
            for segment in segments:
                if not segment:
                    continue
                # If the segment is a SML token, keep as its own
                if re.fullmatch(sml_pattern, segment):
                    result.append(segment)
                else:
                    if lang == 'zho':
                        import jieba
                        result.extend([t for t in jieba.cut(segment) if t.strip()])
                    elif lang == 'jpn':
                        sudachi = dictionary.Dictionary().create()
                        mode = tokenizer.Tokenizer.SplitMode.C
                        result.extend([m.surface() for m in sudachi.tokenize(segment, mode) if m.surface().strip()])
                    elif lang == 'kor':
                        ltokenizer = LTokenizer()
                        result.extend([t for t in ltokenizer.tokenize(segment) if t.strip()])
                    elif lang in ['tha', 'lao', 'mya', 'khm']:
                        result.extend([t for t in word_tokenize(segment, engine='newmm') if t.strip()])
                    else:
                        result.append(segment.strip())
            return result
        except Exception as e:
            DependencyError(e)
            return [text]   

    def join_ideogramms(idg_list):
        try:
            buffer = ''
            for token in idg_list:
             # 1) On sml token: flush & emit buffer, then emit the token
                if token.strip() in sml_tokens:
                    if buffer:
                        yield buffer
                        buffer = ''
                    yield token
                    continue
                # 2) If adding this token would overflow, flush current buffer first
                if buffer and len(buffer) + len(token) > max_chars:
                    yield buffer
                    buffer = ''
                # 3) Append the token (word, punctuation, whatever) unless it's a sml token (already checked)
                buffer += token
            # 4) Flush any trailing text
            if buffer:
                yield buffer
        except Exception as e:
            DependencyError(e)
            if buffer:
                yield buffer

    try:
        max_chars = language_mapping[lang]['max_chars'] - 4
        min_tokens = 5
        # List or tuple of tokens that must never be appended to buffer
        sml_tokens = tuple(TTS_SML.values())
        sml_list = re.split(rf"({'|'.join(map(re.escape, sml_tokens))})", text)
        sml_list = [s for s in sml_list if s.strip() or s in sml_tokens]
        pattern_split = '|'.join(map(re.escape, punctuation_split_hard_set))
        pattern = re.compile(rf"(.*?(?:{pattern_split}){''.join(punctuation_list_set)})(?=\s|$)", re.DOTALL)
        hard_list = []
        for s in sml_list:
            if s in [TTS_SML['break'], TTS_SML['pause']] or len(s) <= max_chars:
                hard_list.append(s)
            else:
                parts = split_inclusive(s, pattern)
                if parts:
                    for text_part in parts:
                        text_part = text_part.strip()
                        if text_part:
                            hard_list.append(text_part)
                else:
                    s = s.strip()
                    if s:
                        hard_list.append(s)
        # Check if some hard_list entries exceed max_chars, so split on soft punctuation
        pattern_split = '|'.join(map(re.escape, punctuation_split_soft_set))
        pattern = re.compile(rf"(.*?(?:{pattern_split}))(?=\s|$)", re.DOTALL)
        soft_list = []
        for s in hard_list:
            if s in [TTS_SML['break'], TTS_SML['pause']] or len(s) <= max_chars:
                soft_list.append(s)
            elif len(s) > max_chars:
                parts = [p for p in split_inclusive(s, pattern) if p]
                if parts:
                    buffer = ''
                    for idx, part in enumerate(parts):
                        # Predict length if we glue this part
                        predicted_length = len(buffer) + (1 if buffer else 0) + len(part)
                        # Peek ahead to see if gluing will exceed max_chars
                        if predicted_length <= max_chars:
                            buffer = (buffer + ' ' + part).strip() if buffer else part
                        else:
                            # If we overshoot, check if buffer ends with punctuation
                            if buffer and not any(buffer.rstrip().endswith(p) for p in punctuation_split_soft_set):
                                # Try to backtrack to last punctuation inside buffer
                                last_punct_idx = max((buffer.rfind(p) for p in punctuation_split_soft_set if p in buffer), default=-1)
                                if last_punct_idx != -1:
                                    soft_list.append(buffer[:last_punct_idx+1].strip())
                                    leftover = buffer[last_punct_idx+1:].strip()
                                    buffer = leftover + ' ' + part if leftover else part
                                else:
                                    # No punctuation, just split as-is
                                    soft_list.append(buffer.strip())
                                    buffer = part
                            else:
                                soft_list.append(buffer.strip())
                                buffer = part
                    if buffer:
                        cleaned = re.sub(r'[^\p{L}\p{N} ]+', '', buffer)
                        if any(ch.isalnum() for ch in cleaned):
                            soft_list.append(buffer.strip())
                else:
                    cleaned = re.sub(r'[^\p{L}\p{N} ]+', '', s)
                    if any(ch.isalnum() for ch in cleaned):
                        soft_list.append(s.strip())
            else:
                cleaned = re.sub(r'[^\p{L}\p{N} ]+', '', s)
                if any(ch.isalnum() for ch in cleaned):
                    soft_list.append(s.strip())

        if lang in ['zho', 'jpn', 'kor', 'tha', 'lao', 'mya', 'khm']:
            result = []
            for s in soft_list:
                if s in [TTS_SML['break'], TTS_SML['pause']]:
                    result.append(s)
                else:
                    tokens = segment_ideogramms(s)
                    if isinstance(tokens, list):
                        result.extend([t for t in tokens if t.strip()])
                    else:
                        tokens = tokens.strip()
                        if tokens:
                            result.append(tokens)
            return list(join_ideogramms(result))
        else:
            sentences = []
            for s in soft_list:
                if s in [TTS_SML['break'], TTS_SML['pause']] or len(s) <= max_chars:
                    sentences.append(s)
                else:
                    words = s.split(' ')
                    text_part = words[0]
                    for w in words[1:]:
                        if len(text_part) + 1 + len(w) <= max_chars:
                            text_part += ' ' + w
                        else:
                            text_part = text_part.strip()
                            if text_part:
                                sentences.append(text_part)
                            text_part = w
                    if text_part:
                        cleaned = re.sub(r'[^\p{L}\p{N} ]+', '', text_part).strip()
                        if not any(ch.isalnum() for ch in cleaned):
                            continue
                        sentences.append(text_part)
            return sentences
    except Exception as e:
        error = f'get_sentences() error: {e}'
        print(error)
        return None
        
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
    
def get_date_entities(text, stanza_nlp):
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

def get_num2words_compat(lang_iso1):
    try:
        test = num2words(1, lang=lang_iso1.replace('zh', 'zh_CN'))
        return True
    except NotImplementedError:
        return False
    except Exception as e:
        return False

def set_formatted_number(text: str, lang, lang_iso1: str, is_num2words_compat: bool, max_single_value: int = 999_999_999_999_999_999):
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

    def normalize_commas(num_str: str) -> str:
        """Normalize number string to standard comma format: 1,234,567"""
        tok = num_str.replace('\u00A0', '').replace(' ', '')
        if '.' in tok:
            integer_part, decimal_part = tok.split('.', 1)
            integer_part = integer_part.replace(',', '')
            integer_part = "{:,}".format(int(integer_part))
            return f"{integer_part}.{decimal_part}"
        else:
            integer_part = tok.replace(',', '')
            return "{:,}".format(int(integer_part))

    def clean_single_num(num_str):
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

    def clean_match(match):
        first_num = clean_single_num(match.group(1))
        dash_char = match.group(2) or ''
        second_num = clean_single_num(match.group(3)) if match.group(3) else ''
        trailing = match.group(4) or ''
        if second_num:
            return f"{first_num}{dash_char}{second_num}{trailing}"
        else:
            return f"{first_num}{trailing}"

    return number_re.sub(clean_match, text)

def year2words(year_str, lang, lang_iso1, is_num2words_compat):
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
            return f"{num2words(first_two, lang=lang_iso1)} {num2words(last_two, lang=lang_iso1)}" 
        else:
            return ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in first_two) + ' ' + ' '.join(language_math_phonemes[lang].get(ch, ch) for ch in last_two)
    except Exception as e:
        error = f'year2words() error: {e}'
        print(error)
        raise
        return False

def clock2words(text, lang, lang_iso1, tts_engine, is_num2words_compat):
    time_rx = re.compile(r'(\d{1,2})[:.](\d{1,2})(?:[:.](\d{1,2}))?')
    lang_lc = (lang or "").lower()
    lc = language_clock.get(lang_lc) if 'language_clock' in globals() else None
    _n2w_cache = {}

    def n2w(n: int) -> str:
        key = (n, lang_lc, is_num2words_compat)
        if key in _n2w_cache:
            return _n2w_cache[key]
        if is_num2words_compat:
            word = num2words(n, lang=lang_lc)
        else:
            word = math2words(n, lang, lang_iso1, tts_engine, is_num2words_compat)
        _n2w_cache[key] = word
        return word

    def repl_num(m: re.Match) -> str:
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
            return " ".join(parts)

        next_hour = (h + 1) % 24
        special_hours = lc.get("special_hours", {})
        # Build main phrase
        if mnt == 0 and (sec is None or sec == 0):
            if h in special_hours:
                phrase = special_hours[h]
            else:
                phrase = lc["oclock"].format(hour=n2w(h))
        elif mnt == 15:
            phrase = lc["quarter_past"].format(hour=n2w(h))
        elif mnt == 30:
            # German "halb drei" (= 2:30) uses next hour
            if lang_lc == "deu":
                phrase = lc["half_past"].format(next_hour=n2w(next_hour))
            else:
                phrase = lc["half_past"].format(hour=n2w(h))
        elif mnt == 45:
            phrase = lc["quarter_to"].format(next_hour=n2w(next_hour))
        elif mnt < 30:
            phrase = lc["past"].format(hour=n2w(h), minute=n2w(mnt)) if mnt != 0 else lc["oclock"].format(hour=n2w(h))
        else:
            minute_to_hour = 60 - mnt
            phrase = lc["to"].format(next_hour=n2w(next_hour), minute=n2w(minute_to_hour))
        # Append seconds if present
        if sec is not None and sec > 0:
            second_phrase = lc["second"].format(second=n2w(sec))
            phrase = lc["full"].format(phrase=phrase, second_phrase=second_phrase)
        return phrase

    return time_rx.sub(repl_num, text)

def math2words(text, lang, lang_iso1, tts_engine, is_num2words_compat):

    def repl_ambiguous(match):
        # handles "num SYMBOL num" and "SYMBOL num"
        if match.group(2) and match.group(2) in ambiguous_replacements:
            return f"{match.group(1)} {ambiguous_replacements[match.group(2)]} {match.group(3)}"
        if match.group(3) and match.group(3) in ambiguous_replacements:
            return f"{ambiguous_replacements[match.group(3)]} {match.group(4)}"
        return match.group(0)

    def _ordinal_to_words(m):
        n = int(m.group(1))
        if is_num2words_compat:
            try:
                from num2words import num2words
                return num2words(n, to="ordinal", lang=(lang_iso1 or "en"))
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
        text = re.sub(sym_pat, lambda m: f" {normal_replacements[m.group(1)]} ", text)
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

def roman2number(text):

    def is_valid_roman(s):
        return bool(valid_roman.fullmatch(s))

    def to_int(s):
        s = s.upper()
        i, result = 0, 0
        while i < len(s):
            for roman, value in roman_numbers_tuples:
                if s[i:i+len(roman)] == roman:
                    result += value
                    i += len(roman)
                    break
            else:
                return s  # Not even a sequence of roman letters
        return result

    def repl_heading(m):
        roman = m.group(1)
        if not is_valid_roman(roman):
            return m.group(0)
        val = to_int(roman)
        return f"{val}{m.group(2)}{m.group(3)}"

    def repl_standalone(m):
        roman = m.group(1)
        if not is_valid_roman(roman):
            return m.group(0)
        val = to_int(roman)
        return f"{val}{m.group(2)}"

    def repl_word(m):
        roman = m.group(1)
        if not is_valid_roman(roman):
            return m.group(0)
        val = to_int(roman)
        return str(val)

    # Well-formed Romans up to 3999
    valid_roman = re.compile(
        r'^(?=.)M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$',
        re.IGNORECASE
    )

    # Your heading/standalone rules stay
    text = re.sub(r'^(?:\s*)([IVXLCDM]+)([.-])(\s+)', repl_heading, text, flags=re.MULTILINE)
    text = re.sub(r'^(?:\s*)([IVXLCDM]+)([.-])(?:\s*)$', repl_standalone, text, flags=re.MULTILINE)

    # NEW: only convert whitespace-delimited tokens of length >= 2
    # This avoids: 19C, 19°C, °C, AC/DC, CD-ROM, single-letter "I"
    text = re.sub(r'(?<!\S)([IVXLCDM]{2,})(?!\S)', repl_word, text)

    return text

def filter_sml(text):
    for key, value in TTS_SML.items():
        pattern = re.escape(key) if key == '###' else r'\[' + re.escape(key) + r'\]'
        text = re.sub(pattern, f" {value} ", text)
    return text

def normalize_text(text, lang, lang_iso1, tts_engine):
    # Remove emojis
    emoji_pattern = re.compile(f"[{''.join(emojis_list)}]+", flags=re.UNICODE)
    emoji_pattern.sub('', text)
    if lang in abbreviations_mapping:
        def repl_abbreviations(match: re.Match) -> str:
            token = match.group(1)
            for k, expansion in mapping.items():
                if token.lower() == k.lower():
                    return expansion
            return token  # fallback
        mapping = abbreviations_mapping[lang]
        # Sort keys by descending length so longer ones match first
        keys = sorted(mapping.keys(), key=len, reverse=True)
        # Build a regex that only matches whole “words” (tokens) exactly
        pattern = re.compile(
            r'(?<!\w)(' + '|'.join(re.escape(k) for k in keys) + r')(?!\w)',
            flags=re.IGNORECASE
        )
        text = pattern.sub(repl_abbreviations, text)
    # This regex matches sequences like a., c.i.a., f.d.a., m.c., etc...
    pattern = re.compile(r'\b(?:[a-zA-Z]\.){1,}[a-zA-Z]?\b\.?')
    # uppercase acronyms
    text = re.sub(r'\b(?:[a-zA-Z]\.){1,}[a-zA-Z]?\b\.?', lambda m: m.group().replace('.', '').upper(), text)
    # Prepare SML tags
    text = filter_sml(text)
    # Replace multiple newlines ("\n\n", "\r\r", "\n\r", etc.) with a ‡pause‡ 1.4sec
    pattern = r'(?:\r\n|\r|\n){2,}'
    text = re.sub(pattern, f" {TTS_SML['pause']} ", text)
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
    pattern = '|'.join(map(re.escape, punctuation_split_hard_set))
    # Reduce multiple consecutive punctuations
    text = re.sub(rf'(\s*({pattern})\s*)+', r'\2 ', text).strip()
    # Escape special characters in the punctuation list for regex
    pattern = '|'.join(map(re.escape, punctuation_split_soft_set))
    # Reduce multiple consecutive punctuations
    text = re.sub(rf'(\s*({pattern})\s*)+', r'\2 ', text).strip()
    # Pattern 1: Add a space between UTF-8 characters and numbers
    text = re.sub(r'(?<=[\p{L}])(?=\d)|(?<=\d)(?=[\p{L}])', ' ', text)
    # Replace special chars with words
    specialchars = specialchars_mapping.get(lang, specialchars_mapping.get(default_language_code, specialchars_mapping['eng']))
    specialchars_table = {ord(char): f" {word} " for char, word in specialchars.items()}
    text = text.translate(specialchars_table)
    text = ' '.join(text.split())
    return text

def convert_chapters2audio(id):
    session = context.get_session(id)
    try:
        if session['cancellation_requested']:
            print('Cancel requested')
            return False
        tts_manager = TTSManager(session)
        if not tts_manager:
            error = f"TTS engine {session['tts_engine']} could not be loaded!\nPossible reason can be not enough VRAM/RAM memory.\nTry to lower max_tts_in_memory in ./lib/models.py"
            print(error)
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
        if total_chapters == 0:
            error = 'No chapterrs found!'
            print(error)
            return False
        total_iterations = sum(len(session['chapters'][x]) for x in range(total_chapters))
        total_sentences = sum(sum(1 for row in chapter if row.strip() not in TTS_SML.values()) for chapter in session['chapters'])
        if total_sentences == 0:
            error = 'No sentences found!'
            print(error)
            return False           
        sentence_number = 0
        msg = f"--------------------------------------------------\nA total of {total_chapters} {'block' if total_chapters <= 1 else 'blocks'} and {total_sentences} {'sentence' if total_sentences <= 1 else 'sentences'}.\n--------------------------------------------------"
        print(msg)
        progress_bar = gr.Progress(track_tqdm=False)
        with tqdm(total=total_iterations, desc='0.00%', bar_format='{desc}: {n_fmt}/{total_fmt} ', unit='step', initial=0) as t:
            for x in range(0, total_chapters):
                chapter_num = x + 1
                chapter_audio_file = f'chapter_{chapter_num}.{default_audio_proc_format}'
                sentences = session['chapters'][x]
                sentences_count = sum(1 for row in sentences if row.strip() not in TTS_SML.values())
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
                        sentence = sentence.strip()
                        success = tts_manager.convert_sentence2audio(sentence_number, sentence) if sentence else True
                        if success:
                            total_progress = (t.n + 1) / total_iterations
                            progress_bar(total_progress)
                            is_sentence = sentence.strip() not in TTS_SML.values()
                            percentage = total_progress * 100
                            t.set_description(f'{percentage:.2f}%')
                            msg = f" | {sentence}" if is_sentence else f" | {sentence}"
                            print(msg)
                        else:
                            return False
                    if sentence.strip() not in TTS_SML.values():
                        sentence_number += 1
                    t.update(1)  # advance for every iteration, including SML
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

def assemble_chunks(txt_file, out_file):
    try:
        ffmpeg_cmd = [
            shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-y',
            '-safe', '0', '-f', 'concat', '-i', txt_file,
            '-c:a', default_audio_proc_format, '-map_metadata', '-1', '-threads', '1', out_file
        ]
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
            return True
        else:
            error = process.returncode
            print(error, ffmpeg_cmd)
            return False
    except subprocess.CalledProcessError as e:
        DependencyError(e)
        return False
    except Exception as e:
        error = f"assemble_chanks() Error: Failed to process {txt_file} → {out_file}: {e}"
        print(error)
        return False

def combine_audio_sentences(chapter_audio_file, start, end, session):
    try:
        chapter_audio_file = os.path.join(session['chapters_dir'], chapter_audio_file)
        chapters_dir_sentences = session['chapters_dir_sentences']
        batch_size = 1024
        sentence_files = [
            f for f in os.listdir(chapters_dir_sentences)
            if f.endswith(f'.{default_audio_proc_format}')
        ]
        sentences_ordered = sorted(
            sentence_files, key=lambda x: int(os.path.splitext(x)[0])
        )
        selected_files = [
            os.path.join(chapters_dir_sentences, f)
            for f in sentences_ordered
            if start <= int(os.path.splitext(f)[0]) <= end
        ]
        if not selected_files:
            print('No audio files found in the specified range.')
            return False
        with tempfile.TemporaryDirectory() as tmpdir:
            chunk_list = []
            for i in range(0, len(selected_files), batch_size):
                batch = selected_files[i:i + batch_size]
                txt = os.path.join(tmpdir, f'chunk_{i:04d}.txt')
                out = os.path.join(tmpdir, f'chunk_{i:04d}.{default_audio_proc_format}')
                with open(txt, 'w') as f:
                    for file in batch:
                        f.write(f"file '{file.replace(os.sep, '/')}'\n")
                chunk_list.append((txt, out))
            try:
                with Pool(cpu_count()) as pool:
                    results = pool.starmap(assemble_chunks, chunk_list)
            except Exception as e:
                error = f"combine_audio_sentences() multiprocessing error: {e}"
                print(error)
                return False
            if not all(results):
                error = "combine_audio_sentences() One or more chunks failed."
                print(error)
                return False
            # Final merge
            final_list = os.path.join(tmpdir, 'sentences_final.txt')
            with open(final_list, 'w') as f:
                for _, chunk_path in chunk_list:
                    f.write(f"file '{chunk_path.replace(os.sep, '/')}'\n")
            if assemble_chunks(final_list, chapter_audio_file):
                msg = f'********* Combined block audio file saved in {chapter_audio_file}'
                print(msg)
                return True
            else:
                error = "combine_audio_sentences() Final merge failed."
                print(error)
                return False
    except Exception as e:
        DependencyError(e)
        return False

def combine_audio_chapters(id):

    def get_audio_duration(filepath):
        try:
            ffprobe_cmd = [
                shutil.which('ffprobe'),
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                filepath
            ]
            result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
            try:
                return float(json.loads(result.stdout)['format']['duration'])
            except Exception:
                return 0
        except subprocess.CalledProcessError as e:
            DependencyError(e)
            return 0
        except Exception as e:
            error = f"get_audio_duration() Error: Failed to process {txt_file} → {out_file}: {e}"
            print(error)
            return 0

    def generate_ffmpeg_metadata(part_chapters, session, output_metadata_path, default_audio_proc_format):
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
                filepath = os.path.join(session['chapters_dir'], filename)
                duration_ms = len(AudioSegment.from_file(filepath, format=default_audio_proc_format))
                clean_title = re.sub(r'(^#)|[=\\]|(-$)', lambda m: '\\' + (m.group(1) or m.group(0)), chapter_title.replace(TTS_SML['pause'], ''))
                ffmpeg_metadata += '[CHAPTER]\nTIMEBASE=1/1000\n'
                ffmpeg_metadata += f'START={start_time}\nEND={start_time + duration_ms}\n'
                ffmpeg_metadata += f"{tag('title')}={clean_title}\n"
                start_time += duration_ms
            with open(output_metadata_path, 'w', encoding='utf-8') as f:
                f.write(ffmpeg_metadata)
            return output_metadata_path
        except Exception as e:
            error = f"generate_ffmpeg_metadata() Error: Failed to process {txt_file} → {out_file}: {e}"
            print(error)
            return False

    def export_audio(ffmpeg_combined_audio, ffmpeg_metadata_file, ffmpeg_final_file):
        try:
            if session['cancellation_requested']:
                print('Cancel requested')
                return False
            cover_path = None
            ffmpeg_cmd = [shutil.which('ffmpeg'), '-hide_banner', '-nostats', '-i', ffmpeg_combined_audio]
            if session['output_format'] == 'wav':
                ffmpeg_cmd += ['-map', '0:a', '-ar', '44100', '-sample_fmt', 's16']
            elif session['output_format'] ==  'aac':
                ffmpeg_cmd += ['-c:a', 'aac', '-b:a', '192k', '-ar', '44100']
            elif session['output_format'] == 'flac':
                ffmpeg_cmd += ['-c:a', 'flac', '-compression_level', '5', '-ar', '44100', '-sample_fmt', 's16']
            else:
                ffmpeg_cmd += ['-f', 'ffmetadata', '-i', ffmpeg_metadata_file, '-map', '0:a']
                if session['output_format'] in ['m4a', 'm4b', 'mp4', 'mov']:
                    ffmpeg_cmd += ['-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-movflags', '+faststart+use_metadata_tags']
                elif session['output_format'] == 'mp3':
                    ffmpeg_cmd += ['-c:a', 'libmp3lame', '-b:a', '192k', '-ar', '44100']
                elif session['output_format'] == 'webm':
                    ffmpeg_cmd += ['-c:a', 'libopus', '-b:a', '192k', '-ar', '48000']
                elif session['output_format'] == 'ogg':
                    ffmpeg_cmd += ['-c:a', 'libopus', '-compression_level', '0', '-b:a', '192k', '-ar', '48000']
                ffmpeg_cmd += ['-map_metadata', '1']
            ffmpeg_cmd += ['-af', 'loudnorm=I=-16:LRA=11:TP=-1.5,afftdn=nf=-70', '-strict', 'experimental', '-threads', '1', '-y', ffmpeg_final_file]
            process = subprocess.Popen(
                ffmpeg_cmd,
                env={},
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='utf-8',
                errors='ignore'
            )
            for line in process.stdout:
                print(line, end='')
            process.wait()
            if process.returncode == 0:
                if session['output_format'] in ['mp3', 'm4a', 'm4b', 'mp4']:
                    if session['cover'] is not None:
                        cover_path = session['cover']
                        msg = f'Adding cover {cover_path} into the final audiobook file...'
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
                                audio.tags.add(
                                    APIC(
                                        encoding=3,
                                        mime='image/jpeg',
                                        type=3,
                                        desc='Cover',
                                        data=img.read()
                                    )
                                )
                        elif session['output_format'] in ['mp4', 'm4a', 'm4b']:
                            from mutagen.mp4 import MP4, MP4Cover
                            audio = MP4(ffmpeg_final_file)
                            with open(cover_path, 'rb') as f:
                                cover_data = f.read()
                            audio["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
                        if audio:
                            audio.save()
                final_vtt = f"{Path(ffmpeg_final_file).stem}.vtt"
                proc_vtt_path = os.path.join(session['process_dir'], final_vtt)
                final_vtt_path = os.path.join(session['audiobooks_dir'], final_vtt)
                shutil.move(proc_vtt_path, final_vtt_path)
                return True
            else:
                error = process.returncode
                print(error, ffmpeg_cmd)
                return False
        except Exception as e:
            DependencyError(e)
            return False

    try:
        session = context.get_session(id)
        chapter_files = [f for f in os.listdir(session['chapters_dir']) if f.endswith(f'.{default_audio_proc_format}')]
        chapter_files = sorted(chapter_files, key=lambda x: int(re.search(r'\d+', x).group()))
        chapter_titles = [c[0] for c in session['chapters']]
        if len(chapter_files) == 0:
            print('No block files exists!')
            return None
        # Calculate total duration
        durations = []
        for file in chapter_files:
            filepath = os.path.join(session['chapters_dir'], file)
            durations.append(get_audio_duration(filepath))
        total_duration = sum(durations)
        exported_files = []
        if session.get('output_split'):
            part_files = []
            part_chapter_indices = []
            cur_part = []
            cur_indices = []
            cur_duration = 0
            max_part_duration = session['output_split_hours'] * 3600
            needs_split = total_duration > (int(session['output_split_hours']) * 2) * 3600
            for idx, (file, dur) in enumerate(zip(chapter_files, durations)):
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
                with tempfile.TemporaryDirectory() as tmpdir:
                    batch_size = 1024
                    chunk_list = []
                    for i in range(0, len(part_file_list), batch_size):
                        batch = part_file_list[i:i + batch_size]
                        txt = os.path.join(tmpdir, f'chunk_{i:04d}.txt')
                        out = os.path.join(tmpdir, f'chunk_{i:04d}.{default_audio_proc_format}')
                        with open(txt, 'w') as f:
                            for file in batch:
                                path = os.path.join(session['chapters_dir'], file).replace("\\", "/")
                                f.write(f"file '{path}'\n")
                        chunk_list.append((txt, out))
                    with Pool(cpu_count()) as pool:
                        results = pool.starmap(assemble_chunks, chunk_list)
                    if not all(results):
                        print(f"assemble_segments() One or more chunks failed for part {part_idx+1}.")
                        return None
                    # Final merge for this part
                    combined_chapters_file = os.path.join(
                        session['process_dir'],
                        f"{get_sanitized(session['metadata']['title'])}_part{part_idx+1}.{default_audio_proc_format}" if needs_split else f"{get_sanitized(session['metadata']['title'])}.{default_audio_proc_format}"
                    )
                    final_list = os.path.join(tmpdir, f'part_{part_idx+1:02d}_final.txt')
                    with open(final_list, 'w') as f:
                        for _, chunk_path in chunk_list:
                            f.write(f"file '{chunk_path.replace(os.sep, '/')}'\n")
                    if not assemble_chunks(final_list, combined_chapters_file):
                        print(f"assemble_segments() Final merge failed for part {part_idx+1}.")
                        return None

                    metadata_file = os.path.join(session['process_dir'], f'metadata_part{part_idx+1}.txt')
                    part_chapters = [(chapter_files[i], chapter_titles[i]) for i in indices]
                    generate_ffmpeg_metadata(part_chapters, session, metadata_file, default_audio_proc_format)

                    final_file = os.path.join(
                        session['audiobooks_dir'],
                        f"{session['final_name'].rsplit('.', 1)[0]}_part{part_idx+1}.{session['output_format']}" if needs_split else session['final_name']
                    )
                    if export_audio(combined_chapters_file, metadata_file, final_file):
                        exported_files.append(final_file)
        else:
            with tempfile.TemporaryDirectory() as tmpdir:
                # 1) build a single ffmpeg file list
                txt = os.path.join(tmpdir, 'all_chapters.txt')
                merged_tmp = os.path.join(tmpdir, f'all.{default_audio_proc_format}')
                with open(txt, 'w') as f:
                    for file in chapter_files:
                        path = os.path.join(session['chapters_dir'], file).replace("\\", "/")
                        f.write(f"file '{path}'\n")

                # 2) merge into one temp file
                if not assemble_chunks(txt, merged_tmp):
                    print("assemble_segments() Final merge failed.")
                    return None

                # 3) generate metadata for entire book
                metadata_file = os.path.join(session['process_dir'], 'metadata.txt')
                all_chapters = list(zip(chapter_files, chapter_titles))
                generate_ffmpeg_metadata(all_chapters, session, metadata_file, default_audio_proc_format)

                # 4) export in one go
                final_file = os.path.join(
                    session['audiobooks_dir'],
                    session['final_name']
                )
                if export_audio(merged_tmp, metadata_file, final_file):
                    exported_files.append(final_file)
        return exported_files if exported_files else None
    except Exception as e:
        DependencyError(e)
        return False

def delete_unused_tmp_dirs(web_dir, days, session):
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
                                msg = f"Deleted expired session: {full_dir_path}"
                                print(msg)
                        except Exception as e:
                            error = f"Error deleting {full_dir_path}: {e}"
                            print(error)

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

def convert_ebook_batch(args, ctx=None):
    if isinstance(args['ebook_list'], list):
        ebook_list = args['ebook_list'][:]
        for file in ebook_list: # Use a shallow copy
            if any(file.endswith(ext) for ext in ebook_formats):
                args['ebook'] = file
                print(f'Processing eBook file: {os.path.basename(file)}')
                progress_status, passed = convert_ebook(args, ctx)
                if passed is False:
                    print(f'Conversion failed: {progress_status}')
                    sys.exit(1)
                args['ebook_list'].remove(file) 
        reset_ebook_session(args['session'])
        return progress_status, passed
    else:
        print(f'the ebooks source is not a list!')
        sys.exit(1)       

def convert_ebook(args, ctx=None):
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

            if ctx is not None:
                context = ctx

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
            session['voice'] = args['voice']
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
            session['output_format'] = args['output_format']
            session['output_split'] = args['output_split']    
            session['output_split_hours'] = args['output_split_hours'] if args['output_split_hours'] is not None else default_output_split_hours

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
                    bool, e = check_programs('Calibre', 'ebook-convert', '--version')
                    if not bool:
                        error = f'check_programs() Calibre failed: {e}'
                    bool, e = check_programs('FFmpeg', 'ffmpeg', '-version')
                    if not bool:
                        error = f'check_programs() FFMPEG failed: {e}'
                if error is None:
                    old_session_dir = os.path.join(tmp_dir, f"ebook-{session['id']}")
                    session['session_dir'] = os.path.join(tmp_dir, f"proc-{session['id']}")
                    if os.path.isdir(old_session_dir):
                        os.rename(old_session_dir, session['session_dir'])
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
                        if convert2epub(id):
                            epubBook = epub.read_epub(session['epub_path'], {'ignore_ncx': True})       
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
                                    if convert_chapters2audio(id):
                                        msg = 'Conversion successful. Combining sentences and chapters...'
                                        show_alert({"type": "info", "msg": msg})
                                        exported_files = combine_audio_chapters(id)               
                                        if exported_files is not None:
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
                                            progress_status = f'Audiobook(s) {", ".join(os.path.basename(f) for f in exported_files)} created!'
                                            session['audiobook'] = exported_files[-1]
                                            print(info_session)
                                            return progress_status, True
                                        else:
                                            error = 'combine_audio_chapters() error: exported_files not created!'
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
        DependencyError(e)

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
        "duration": 0,
        "playback_time": 0,
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

def web_interface(args, ctx):
    global context, is_gui_process
    context = ctx
    script_mode = args['script_mode']
    is_gui_process = args['is_gui_process']
    is_gui_shared = args['share']
    title = 'Ebook2Audiobook'
    glass_mask_msg = 'Initialization, please wait...'
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
    options_output_split_hours = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    
    src_label_file = 'Select a File'
    src_label_dir = 'Select a Directory'
    
    visible_gr_tab_xtts_params = interface_component_options['gr_tab_xtts_params']
    visible_gr_tab_bark_params = interface_component_options['gr_tab_bark_params']
    visible_gr_group_custom_model = interface_component_options['gr_group_custom_model']
    visible_gr_group_voice_file = interface_component_options['gr_group_voice_file']

    theme = gr.themes.Origin(
        primary_hue='green',
        secondary_hue='amber',
        neutral_hue='gray',
        radius_size='lg',
        font_mono=['JetBrains Mono', 'monospace', 'Consolas', 'Menlo', 'Liberation Mono']
    )

    header_css = '''
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
            .wrap-inner {
                border: 1px solid #666666;
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
            #glass-mask {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important; 
                height: 100vh !important;
                background: rgba(0,0,0,0.6) !important;
                display: flex !important;
                text-align: center;
                align-items: center !important;
                justify-content: center !important;
                font-size: 1.2rem !important;
                color: #fff !important;
                z-index: 9999 !important;
                transition: opacity 2s ease-out 2s !important;
                pointer-events: all !important;
            }
            #glass-mask.hide {
                opacity: 0 !important;
                pointer-events: none !important;
            }
            #gr_markdown_logo {
                position: absolute !important; 
                text-align: right !important;
            }
            #gr_ebook_file, #gr_custom_model_file, #gr_voice_file {
                height: 140px !important;
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
            #gr_audiobook_list span[data-testid="block-info"]{
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
            ////////////
            .fade-in {
                animation: fadeIn 1s ease-in;
                display: inline-block;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        </style>
    '''
    
    with gr.Blocks(theme=theme, title=title, css=header_css, delete_cache=(86400, 86400)) as app:
        with gr.Tabs(elem_id='gr_tabs'):
            gr_tab_main = gr.TabItem('Main Parameters', elem_id='gr_tab_main', elem_classes='tab_item')
            with gr_tab_main:
                with gr.Row(elem_id='gr_row_tab_main'):
                    with gr.Column(elem_id='gr_col_1', scale=3):
                        with gr.Group(elem_id='gr1'):
                            gr_ebook_file = gr.File(label=src_label_file, elem_id='gr_ebook_file', file_types=ebook_formats, file_count='single', allow_reordering=True, height=140)
                            gr_ebook_mode = gr.Radio(label='', elem_id='gr_ebook_mode', choices=[('File','single'), ('Directory','directory')], value='single', interactive=True)
                        with gr.Group(elem_id='gr_group_language'):
                            gr_language = gr.Dropdown(label='Language', elem_id='gr_language', choices=language_options, value=default_language_code, type='value', interactive=True)
                        gr_group_voice_file = gr.Group(elem_id='gr_group_voice_file', visible=visible_gr_group_voice_file)
                        with gr_group_voice_file:
                            gr_voice_file = gr.File(label='*Cloning Voice Audio Fiie', elem_id='gr_voice_file', file_types=voice_formats, value=None, height=140)
                            gr_row_voice_player = gr.Row(elem_id='gr_row_voice_player')
                            with gr_row_voice_player:
                                gr_voice_player = gr.Audio(elem_id='gr_voice_player', type='filepath', interactive=False, show_download_button=False, container=False, visible=False, show_share_button=False, show_label=False, waveform_options=gr.WaveformOptions(show_controls=False), scale=0, min_width=60)
                                gr_voice_list = gr.Dropdown(label='', elem_id='gr_voice_list', choices=voice_options, type='value', interactive=True, scale=2)
                                gr_voice_del_btn = gr.Button('🗑', elem_id='gr_voice_del_btn', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                            gr_optional_markdown = gr.Markdown(elem_id='gr_markdown_optional', value='<p>&nbsp;&nbsp;* Optional</p>')
                        with gr.Group(elem_id='gr_group_device'):
                            gr_device = gr.Dropdown(label='Processor Unit', elem_id='gr_device', choices=[('CPU','cpu'), ('GPU','cuda'), ('MPS','mps')], type='value', value=default_device, interactive=True)
                            gr_logo_markdown = gr.Markdown(elem_id='gr_logo_markdown', value=f'''
                                <div style="right:0;margin:auto;padding:10px;text-align:right">
                                    <a href="https://github.com/DrewThomasson/ebook2audiobook" style="text-decoration:none;font-size:14px" target="_blank">
                                    <b>{title}</b>&nbsp;<b style="color:orange">{prog_version}</b></a>
                                </div>
                                '''
                            )
                    with gr.Column(elem_id='gr_col_2', scale=3):
                        with gr.Group(elem_id='gr_group_engine'):
                            gr_tts_engine_list = gr.Dropdown(label='TTS Engine', elem_id='gr_tts_engine_list', choices=tts_engine_options, type='value', interactive=True)
                            gr_tts_rating = gr.HTML()
                            gr_fine_tuned_list = gr.Dropdown(label='Fine Tuned Models (Presets)', elem_id='gr_fine_tuned_list', choices=fine_tuned_options, type='value', interactive=True)
                            gr_group_custom_model = gr.Group(visible=visible_gr_group_custom_model)
                            with gr_group_custom_model:
                                gr_custom_model_file = gr.File(label=f"Upload Fine Tuned Model", elem_id='gr_custom_model_file', value=None, file_types=['.zip'], height=140)
                                with gr.Row(elem_id='gr_row_custom_model'):
                                    gr_custom_model_list = gr.Dropdown(label='', elem_id='gr_custom_model_list', choices=custom_model_options, type='value', interactive=True, scale=2)
                                    gr_custom_model_del_btn = gr.Button('🗑', elem_id='gr_custom_model_del_btn', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                                gr_custom_model_markdown = gr.Markdown(elem_id='gr_markdown_custom_model', value='<p>&nbsp;&nbsp;* Optional</p>')
                        with gr.Group(elem_id='gr_group_output_format'):
                            with gr.Row(elem_id='gr_row_output_format'):
                                gr_output_format_list = gr.Dropdown(label='Output Format', elem_id='gr_output_format_list', choices=output_formats, type='value', value=default_output_format, interactive=True, scale=2)
                                gr_output_split = gr.Checkbox(label='Split Output File', elem_id='gr_output_split', value=default_output_split, interactive=True, scale=1)
                                gr_output_split_hours = gr.Dropdown(label='Max hours / part', elem_id='gr_output_split_hours', choices=options_output_split_hours, type='value', value=default_output_split_hours, interactive=True, visible=False, scale=2)
                        gr_session = gr.Textbox(label='Session', elem_id='gr_session', interactive=False)
            gr_tab_xtts_params = gr.TabItem('XTTSv2 Fine Tuned Parameters', elem_id='gr_tab_xtts_params', elem_classes='tab_item', visible=visible_gr_tab_xtts_params)           
            with gr_tab_xtts_params:
                gr.Markdown(
                    elem_id='gr_markdown_tab_xtts_params',
                    value='''
                    ### Customize XTTSv2 Parameters
                    Adjust the settings below to influence how the audio is generated. You can control the creativity, speed, repetition, and more.
                    '''
                )
                gr_xtts_temperature = gr.Slider(
                    label='Temperature',
                    minimum=0.05,
                    maximum=10.0,
                    step=0.05,
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
            gr_tab_bark_params = gr.TabItem('BARK fine Tuned Parameters', elem_id='gr_tab_bark_params', elem_classes='tab_item', visible=visible_gr_tab_bark_params)           
            with gr_tab_bark_params:
                gr.Markdown(
                    elem_id='gr_markdown_tab_bark_params',
                    value='''
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
        gr_state_update = gr.State(value={"hash": None})
        gr_read_data = gr.JSON(visible=False, elem_id='gr_read_data')
        gr_write_data = gr.JSON(visible=False, elem_id='gr_write_data')
        gr_tab_progress = gr.Textbox(elem_id='gr_tab_progress', label='Progress', interactive=False)
        gr_group_audiobook_list = gr.Group(elem_id='gr_group_audiobook_list', visible=False)
        with gr_group_audiobook_list:
            gr_audiobook_vtt = gr.Textbox(elem_id='gr_audiobook_vtt', label='', interactive=False, visible=False)
            gr_audiobook_sentence = gr.Textbox(elem_id='gr_audiobook_sentence', label='Audiobook', value='...', interactive=False, visible=True, lines=3, max_lines=3)
            gr_audiobook_player = gr.Audio(elem_id='gr_audiobook_player', label='',type='filepath', autoplay=False, waveform_options=gr.WaveformOptions(show_recording_waveform=False), show_download_button=False, show_share_button=False, container=True, interactive=False, visible=True)
            gr_audiobook_player_playback_time = gr.Number(label='', interactive=False, visible=True, elem_id="gr_audiobook_player_playback_time", value=0.0)
            with gr.Row(elem_id='gr_row_audiobook_list'):
                gr_audiobook_download_btn = gr.DownloadButton(elem_id='gr_audiobook_download_btn', label='↧', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=True, scale=0, min_width=60)
                gr_audiobook_list = gr.Dropdown(elem_id='gr_audiobook_list', label='', choices=audiobook_options, type='value', interactive=True, visible=True, scale=2)
                gr_audiobook_del_btn = gr.Button(elem_id='gr_audiobook_del_btn', value='🗑', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=True, scale=0, min_width=60)
        gr_convert_btn = gr.Button(elem_id='gr_convert_btn', value='📚', elem_classes='icon-btn', variant='primary', interactive=False)
        
        gr_modal = gr.HTML(visible=False)
        gr_glass_mask = gr.HTML(f'<div id="glass-mask">{glass_mask_msg}</div>')
        gr_confirm_field_hidden = gr.Textbox(elem_id='confirm_hidden', visible=False)
        gr_confirm_yes_btn = gr.Button(elem_id='confirm_yes_btn', value='', visible=False)
        gr_confirm_no_btn = gr.Button(elem_id='confirm_no_btn', value='', visible=False)

        def cleanup_session(req: gr.Request):
            socket_hash = req.session_hash
            if any(socket_hash in session for session in context.sessions.values()):
                session_id = context.find_id_by_hash(socket_hash)
                ctx_tracker.end_session(session_id, socket_hash)

        def load_vtt_data(path):
            if not path or not os.path.exists(path):
                return None
            try:
                vtt_path = Path(path).with_suffix('.vtt')
                if not os.path.exists(vtt_path):
                    return None
                with open(vtt_path, "r", encoding="utf-8-sig", errors="replace") as f:
                    content = f.read()
                return content
            except Exception:
                return None

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
                <button class="confirm_yes_btn" onclick="document.querySelector('#confirm_yes_btn').click()">✔</button>
                <button class="confirm_no_btn" onclick="document.querySelector('#confirm_no_btn').click()">⨉</button>
            </div>
            '''

        def show_rating(tts_engine):

            def yellow_stars(n):
                return "".join(
                    "<span style='color:#f0bc00; font-size:12px'>★</span>" for _ in range(n)
                )

            def color_box(value):
                if value <= 4:
                    color = "#4CAF50"  # Green = low
                elif value <= 8:
                    color = "#FF9800"  # Orange = medium
                else:
                    color = "#F44336"  # Red = high
                return f"<span style='background:{color};color:white;padding:1px 5px;border-radius:3px;font-size:11px'>{value} GB</span>"
            
            rating = default_engine_settings[tts_engine]['rating']

            return f"""
            <div style='margin:0; padding:0; font-size:12px; line-height:1.2; height:auto; display:flex; flex-wrap:wrap; align-items:center; gap:6px 12px;'>
              <span style='display:inline-flex; white-space:nowrap; padding:0 10px'><b>GPU VRAM:</b> {color_box(rating["GPU VRAM"])}</span>
              <span style='display:inline-flex; white-space:nowrap; padding:0 10px'><b>CPU:</b> {yellow_stars(rating["CPU"])}</span>
              <span style='display:inline-flex; white-space:nowrap; padding:0 10px'><b>RAM:</b> {color_box(rating["RAM"])}</span>
              <span style='display:inline-flex; white-space:nowrap; padding:0 10px'><b>Realism:</b> {yellow_stars(rating["Realism"])}</span>
            </div>
            """

        def alert_exception(error):
            gr.Error(error)
            DependencyError(error)

        def restore_interface(id, req: gr.Request):
            try:
                session = context.get_session(id)
                socket_hash = req.session_hash
                if not session.get(socket_hash):
                    outputs = tuple([gr.update() for _ in range(24)])
                    return outputs
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
                    gr.update(value=session['language']), update_gr_tts_engine_list(id), update_gr_custom_model_list(id),
                    update_gr_fine_tuned_list(id), gr.update(value=session['output_format']), update_gr_audiobook_list(id), gr.update(value=load_vtt_data(session['audiobook'])),
                    gr.update(value=float(session['temperature'])), gr.update(value=float(session['length_penalty'])), gr.update(value=int(session['num_beams'])),
                    gr.update(value=float(session['repetition_penalty'])), gr.update(value=int(session['top_k'])), gr.update(value=float(session['top_p'])), gr.update(value=float(session['speed'])), 
                    gr.update(value=bool(session['enable_text_splitting'])), gr.update(value=float(session['text_temp'])), gr.update(value=float(session['waveform_temp'])), update_gr_voice_list(id),
                    gr.update(value=session['output_split']), gr.update(value=session['output_split_hours']), gr.update(active=True)
                )
            except Exception as e:
                error = f'restore_interface(): {e}'
                alert_exception(error)
                outputs = tuple([gr.update() for _ in range(24)])
                return outputs

        def refresh_interface(id):
            session = context.get_session(id)
            return (
                    gr.update(interactive=False), gr.update(value=None), update_gr_audiobook_list(id), 
                    gr.update(value=session['audiobook']), gr.update(visible=False), update_gr_voice_list(id)
            )

        def change_gr_audiobook_list(selected, id):
            session = context.get_session(id)
            session['audiobook'] = selected
            if selected is not None:
                audio_info = mediainfo(selected)
                session['duration'] = float(audio_info['duration'])
            visible = True if len(audiobook_options) else False
            return gr.update(value=selected), gr.update(value=selected), gr.update(value=load_vtt_data(selected)), gr.update(visible=visible)
        
        def update_gr_glass_mask(str=glass_mask_msg, attr=''):
            return gr.update(value=f'<div id="glass-mask" {attr}>{str}</div>')
        
        def state_convert_btn(upload_file=None, upload_file_mode=None, custom_model_file=None, session=None):
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
                error = f'state_convert_btn(): {e}'
                alert_exception(error)
        
        def disable_components():
            outputs = tuple([gr.update(interactive=False) for _ in range(9)])
            return outputs
        
        def enable_components():
            outputs = tuple([gr.update(interactive=True) for _ in range(9)])
            return outputs

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
                    final_voice_file = os.path.join(session['voice_dir'], f'{voice_name}.wav')
                    extractor = VoiceExtractor(session, f, voice_name)
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
                    session = context.get_session(id)
                    speaker_path = os.path.abspath(selected)
                    speaker = re.sub(r'\.wav$|\.npz$', '', os.path.basename(selected))
                    builtin_root = os.path.join(voices_dir, session['language'])
                    sessions_root = os.path.join(voices_dir, '__sessions')
                    is_in_sessions = os.path.commonpath([speaker_path, os.path.abspath(sessions_root)]) == os.path.abspath(sessions_root)
                    is_in_builtin = os.path.commonpath([speaker_path, os.path.abspath(builtin_root)]) == os.path.abspath(builtin_root)
                    # Check if voice is built-in
                    is_builtin = any(
                        speaker in settings.get('voices', {})
                        for settings in (default_engine_settings[engine] for engine in TTS_ENGINES.values())
                    )
                    if is_builtin and is_in_builtin:
                        error = f'Voice file {speaker} is a builtin voice and cannot be deleted.'
                        show_alert({"type": "warning", "msg": error})
                        return gr.update(), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
                    try:
                        selected_path = Path(selected).resolve()
                        parent_path = Path(session['voice_dir']).parent.resolve()
                        if parent_path in selected_path.parents:
                            msg = f'Are you sure to delete {speaker}...'
                            return (
                                gr.update(value='confirm_voice_del'),
                                gr.update(value=show_modal('confirm', msg), visible=True),
                                gr.update(visible=True),
                                gr.update(visible=True)
                            )
                        else:
                            error = f'{speaker} is part of the global voices directory. Only your own custom uploaded voices can be deleted!'
                            show_alert({"type": "warning", "msg": error})
                            return gr.update(), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
                    except Exception as e:
                        error = f'Could not delete the voice file {selected}!\n{e}'
                        alert_exception(error)
                        return gr.update(), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
                # Fallback/default return if not selected or after errors
                return gr.update(), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
            except Exception as e:
                error = f'click_gr_voice_del_btn(): {e}'
                alert_exception(error)
                return gr.update(), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

        def click_gr_custom_model_del_btn(selected, id):
            try:
                if selected is not None:
                    session = context.get_session(id)
                    selected_name = os.path.basename(selected)
                    msg = f'Are you sure to delete {selected_name}...'
                    return gr.update(value='confirm_custom_model_del'), gr.update(value=show_modal('confirm', msg),visible=True), gr.update(visible=True), gr.update(visible=True)
            except Exception as e:
                error = f'Could not delete the custom model {selected_name}!'
                alert_exception(error)
            return gr.update(), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

        def click_gr_audiobook_del_btn(selected, id):
            try:
                if selected is not None:
                    session = context.get_session(id)
                    selected_name = Path(selected).stem
                    msg = f'Are you sure to delete {selected_name}...'
                    return gr.update(value='confirm_audiobook_del'), gr.update(value=show_modal('confirm', msg),visible=True), gr.update(visible=True), gr.update(visible=True)
            except Exception as e:
                error = f'Could not delete the audiobook {selected_name}!'
                alert_exception(error)
            return gr.update(), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

        def confirm_deletion(voice_path, custom_model, audiobook, id, method=None):
            try:
                if method is not None:
                    session = context.get_session(id)
                    if method == 'confirm_voice_del':
                        selected_name = Path(voice_path).stem
                        pattern = re.sub(r'\.wav$', '*.wav', voice_path)
                        files2remove = glob(pattern)
                        for file in files2remove:
                            os.remove(file)
                        shutil.rmtree(os.path.join(os.path.dirname(voice_path), 'bark', selected_name), ignore_errors=True)
                        msg = f"Voice file {re.sub(r'.wav$', '', selected_name)} deleted!"
                        session['voice'] = None
                        show_alert({"type": "warning", "msg": msg})
                        return gr.update(), gr.update(), gr.update(visible=False), update_gr_voice_list(id), gr.update(visible=False), gr.update(visible=False)
                    elif method == 'confirm_custom_model_del':
                        selected_name = os.path.basename(custom_model)
                        shutil.rmtree(custom_model, ignore_errors=True)                           
                        msg = f'Custom model {selected_name} deleted!'
                        session['custom_model'] = None
                        show_alert({"type": "warning", "msg": msg})
                        return update_gr_custom_model_list(id), gr.update(), gr.update(visible=False), gr.update(), gr.update(visible=False), gr.update(visible=False)
                    elif method == 'confirm_audiobook_del':
                        selected_name = Path(audiobook).stem
                        if os.path.isdir(audiobook):
                            shutil.rmtree(selected, ignore_errors=True)
                        elif os.path.exists(audiobook):
                            os.remove(audiobook)
                        vtt_path = Path(audiobook).with_suffix('.vtt')
                        if os.path.exists(vtt_path):
                            os.remove(vtt_path)
                        msg = f'Audiobook {selected_name} deleted!'
                        session['audiobook'] = None
                        show_alert({"type": "warning", "msg": msg})
                        return gr.update(), update_gr_audiobook_list(id), gr.update(visible=False), gr.update(), gr.update(visible=False), gr.update(visible=False)
                return gr.update(), gr.update(), gr.update(visible=False), gr.update(), gr.update(visible=False), gr.update(visible=False)
            except Exception as e:
                error = f'confirm_deletion(): {e}!'
                alert_exception(error)
            return gr.update(), gr.update(), gr.update(visible=False), gr.update(), gr.update(visible=False), gr.update(visible=False)
                
        def prepare_audiobook_download(selected):
            if os.path.exists(selected):
                return selected
            return None           

        def update_gr_voice_list(id):
            try:
                nonlocal voice_options
                session = context.get_session(id)
                lang_dir = session['language'] if session['language'] != 'con' else 'con-'  # Bypass Windows CON reserved name
                file_pattern = "*.wav"
                eng_options = []
                bark_options = []
                builtin_options = [
                    (os.path.splitext(f.name)[0], str(f))
                    for f in Path(os.path.join(voices_dir, lang_dir)).rglob(file_pattern)
                ]
                if session['language'] in language_tts[TTS_ENGINES['XTTSv2']]:
                    builtin_names = {t[0]: None for t in builtin_options}
                    eng_dir = Path(os.path.join(voices_dir, "eng"))
                    eng_options = [
                        (base, str(f))
                        for f in eng_dir.rglob(file_pattern)
                        for base in [os.path.splitext(f.name)[0]]
                        if base not in builtin_names
                    ]
                if session['tts_engine'] == TTS_ENGINES['BARK']:
                    lang_array = languages.get(part3=session['language'])
                    if lang_array:
                        lang_iso1 = lang_array.part1 
                        lang = lang_iso1.lower()
                        speakers_path = Path(default_engine_settings[TTS_ENGINES['BARK']]['speakers_path'])
                        pattern_speaker = re.compile(r"^.*?_speaker_(\d+)$")
                        bark_options = [
                            (pattern_speaker.sub(r"Speaker \1", f.stem), str(f.with_suffix(".wav")))
                            for f in speakers_path.rglob(f"{lang}_speaker_*.npz")
                        ]
                voice_options = builtin_options + eng_options + bark_options
                session['voice_dir'] = os.path.join(voices_dir, '__sessions', f"voice-{session['id']}", session['language'])
                os.makedirs(session['voice_dir'], exist_ok=True)
                if session['voice_dir'] is not None:
                    parent_dir = Path(session['voice_dir']).parent
                    voice_options += [
                        (os.path.splitext(f.name)[0], str(f))
                        for f in parent_dir.rglob(file_pattern)
                        if f.is_file()
                    ]
                if session['tts_engine'] in [TTS_ENGINES['VITS'], TTS_ENGINES['FAIRSEQ'], TTS_ENGINES['TACOTRON2'], TTS_ENGINES['YOURTTS']]:
                    voice_options = [('Default', None)] + sorted(voice_options, key=lambda x: x[0].lower())
                else:
                    voice_options = sorted(voice_options, key=lambda x: x[0].lower())                           
                default_voice_path = models[session['tts_engine']][session['fine_tuned']]['voice']
                if session['voice'] is None:
                    if voice_options[0][1] is not None:
                        default_name = Path(default_voice_path).stem
                        for name, value in voice_options:
                            if name == default_name:
                                session['voice'] = value
                                break
                        else:
                            values = [v for _, v in voice_options]
                            if default_voice_path in values:
                                session['voice'] = default_voice_path
                            else:
                                session['voice'] = voice_options[0][1]
                else:
                    current_voice_name = Path(session['voice']).stem
                    current_voice_path = next(
                        (path for name, path in voice_options if name == current_voice_name and path == session['voice']), False
                    )
                    if current_voice_path:
                        session['voice'] = current_voice_path
                    else:
                        session['voice'] = default_voice_path
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
            if selected:
                session = context.get_session(id)
                prev = session['language']      
                session['language'] = selected
                return[
                    gr.update(value=session['language']),
                    update_gr_tts_engine_list(id),
                    update_gr_custom_model_list(id),
                    update_gr_fine_tuned_list(id)
                ]
            return (gr.update(), gr.update(), gr.update(), gr.update())

        def check_custom_model_tts(custom_model_dir, tts_engine):
            dir_path = None
            if custom_model_dir is not None and tts_engine is not None:
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
            default_voice_path = models[session['tts_engine']][session['fine_tuned']]['voice']
            if default_voice_path is None:
                session['voice'] = default_voice_path
            bark_visible = False
            if session['tts_engine'] == TTS_ENGINES['XTTSv2']:
                visible_custom_model = True
                if session['fine_tuned'] != 'internal':
                    visible_custom_model = False
                return (
                       gr.update(value=show_rating(session['tts_engine'])), 
                       gr.update(visible=visible_gr_tab_xtts_params), gr.update(visible=False), gr.update(visible=visible_custom_model), update_gr_fine_tuned_list(id),
                       gr.update(label=f"*Upload {session['tts_engine']} Model (Should be a ZIP file with {', '.join(models[session['tts_engine']][default_fine_tuned]['files'])})"),
                       gr.update(label=f"My {session['tts_engine']} custom models")
                )
            else:
                if session['tts_engine'] == TTS_ENGINES['BARK']:
                    bark_visible = visible_gr_tab_bark_params
                return (
                        gr.update(value=show_rating(session['tts_engine'])), gr.update(visible=False), gr.update(visible=bark_visible), 
                        gr.update(visible=False), update_gr_fine_tuned_list(id), gr.update(label=f"*Upload Fine Tuned Model not available for {session['tts_engine']}"), gr.update(label='')
                )
                
        def change_gr_fine_tuned_list(selected, id):
            if selected:
                session = context.get_session(id)
                visible = False
                if session['tts_engine'] == TTS_ENGINES['XTTSv2']:
                    if selected == 'internal':
                        visible = visible_gr_group_custom_model
                session['fine_tuned'] = selected
                return gr.update(visible=visible)
            return gr.update()

        def change_gr_custom_model_list(selected, id):
            session = context.get_session(id)
            session['custom_model'] = next((value for label, value in custom_model_options if value == selected), None)
            visible = True if session['custom_model'] is not None else False
            return gr.update(visible=not visible), gr.update(visible=visible)
        
        def change_gr_output_format_list(val, id):
            session = context.get_session(id)
            session['output_format'] = val
            return
            
        def change_gr_output_split(bool, id):
            session = context.get_session(id)
            session['output_split'] = bool
            return gr.update(visible=bool)

        def change_gr_output_split_hours(selected, id):
            session = context.get_session(id)
            session['output_split_hours'] = selected
            return

        def change_gr_audiobook_player_playback_time(str, id):
            session = context.get_session(id)
            session['playback_time'] = float(str)
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

        def submit_convert_btn(
                id, device, ebook_file, tts_engine, language, voice, custom_model, fine_tuned, output_format, temperature, 
                length_penalty, num_beams, repetition_penalty, top_k, top_p, speed, enable_text_splitting, text_temp, waveform_temp,
                output_split, output_split_hours
            ):
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
                    "fine_tuned": fine_tuned,
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
                    "output_split": output_split,
                    "output_split_hours": output_split_hours
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
                                        break
                                    else:
                                        error = 'Conversion failed.'
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
                        session['status'] = 'ready'
                    else:
                        print(f"Processing eBook file: {os.path.basename(args['ebook'])}")
                        progress_status, passed = convert_ebook(args)
                        if passed is False:
                            if session['status'] == 'converting':
                                error = 'Conversion cancelled.'
                            else:
                                error = 'Conversion failed.'
                            session['status'] = 'ready'
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
                    if not f.lower().endswith(".vtt")  # exclude VTT files
                ]
                audiobook_options.sort(
                    key=lambda x: os.path.getmtime(x[1]),
                    reverse=True
                )
                session['audiobook'] = (
                    session['audiobook']
                    if session['audiobook'] in [option[1] for option in audiobook_options]
                    else None
                )
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

        def change_gr_read_data(data, state, req: gr.Request):
            try:
                msg = 'Error while loading saved session. Please try to delete your cookies and refresh the page'
                if data is None:
                    data = context.get_session(str(uuid.uuid4()))
                session = context.get_session(data['id'])
                if data.get('tab_id') == session.get('tab_id') or len(active_sessions) == 0:
                    restore_session_from_data(data, session)
                    session['status'] = None
                if not ctx_tracker.start_session(session['id']):
                    error = "Your session is already active.<br>If it's not the case please close your browser and relaunch it."
                    return gr.update(), gr.update(), gr.update(value=''), update_gr_glass_mask(str=error)
                else:
                    active_sessions.add(req.session_hash)
                    session[req.session_hash] = req.session_hash
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
                    session['status'] = 'ready'
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
                return gr.update(value=session_dict), gr.update(value=state), gr.update(value=session['id']), gr.update()
            except Exception as e:
                error = f'change_gr_read_data(): {e}'
                alert_exception(error)
                return gr.update(), gr.update(), gr.update(), gr.update()

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
            if id:
                session = context.get_session(id)
                if session['event'] is not None:
                    session['event'] = None

        gr_ebook_file.change(
            fn=state_convert_btn,
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
            outputs=[gr_confirm_field_hidden, gr_modal, gr_confirm_yes_btn, gr_confirm_no_btn]
        )
        gr_device.change(
            fn=change_gr_device,
            inputs=[gr_device, gr_session],
            outputs=None
        )
        gr_language.change(
            fn=change_gr_language,
            inputs=[gr_language, gr_session],
            outputs=[gr_language, gr_tts_engine_list, gr_custom_model_list, gr_fine_tuned_list]
        ).then(
            fn=update_gr_voice_list,
            inputs=[gr_session],
            outputs=[gr_voice_list]
        )
        gr_tts_engine_list.change(
            fn=change_gr_tts_engine_list,
            inputs=[gr_tts_engine_list, gr_session],
            outputs=[gr_tts_rating, gr_tab_xtts_params, gr_tab_bark_params, gr_group_custom_model, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list] 
        ).then(
            fn=update_gr_voice_list,
            inputs=[gr_session],
            outputs=[gr_voice_list]        
        )
        gr_fine_tuned_list.change(
            fn=change_gr_fine_tuned_list,
            inputs=[gr_fine_tuned_list, gr_session],
            outputs=[gr_group_custom_model]
        ).then(
            fn=update_gr_voice_list,
            inputs=[gr_session],
            outputs=[gr_voice_list]        
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
            outputs=[gr_confirm_field_hidden, gr_modal, gr_confirm_yes_btn, gr_confirm_no_btn]
        )
        gr_output_format_list.change(
            fn=change_gr_output_format_list,
            inputs=[gr_output_format_list, gr_session],
            outputs=None
        )
        gr_output_split.change(
            fn=change_gr_output_split,
            inputs=[gr_output_split, gr_session],
            outputs=gr_output_split_hours
        )
        gr_output_split_hours.change(
            fn=change_gr_output_split_hours,
            inputs=[gr_output_split_hours, gr_session],
            outputs=None
        )
        gr_audiobook_vtt.change(
            fn=lambda: gr.update(value=''),
            inputs=[],
            outputs=[gr_audiobook_sentence]
        ).then(
            fn=None,
            inputs=[gr_audiobook_vtt],
            js='(data)=>{window.load_vtt?.(URL.createObjectURL(new Blob([data],{type: "text/vtt"})));}'         
        )
        gr_tab_progress.change(
            fn=None,
            inputs=[gr_tab_progress],
            outputs=[],
            js=f'() => {{ document.title = "{title}"; }}'
        )
        gr_audiobook_player_playback_time.change(
            fn=change_gr_audiobook_player_playback_time,
            inputs=[gr_audiobook_player_playback_time, gr_session],
            outputs=[]
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
            outputs=[gr_audiobook_download_btn, gr_audiobook_player, gr_audiobook_vtt, gr_group_audiobook_list]
        )#.then(
        #    fn=None,
        #    inputs=[],
        #    outputs=[],
        #    js="()=>{window.init_elements?.();}"
        #)
        gr_audiobook_del_btn.click(
            fn=click_gr_audiobook_del_btn,
            inputs=[gr_audiobook_list, gr_session],
            outputs=[gr_confirm_field_hidden, gr_modal, gr_confirm_yes_btn, gr_confirm_no_btn]
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
        gr_timer = gr.Timer(9, active=False)
        gr_timer.tick(
            fn=save_session,
            inputs=[gr_session, gr_state_update],
            outputs=[gr_write_data, gr_state_update, gr_audiobook_list]
        ).then(
            fn=clear_event,
            inputs=[gr_session],
            outputs=None
        )
        gr_convert_btn.click(
            fn=state_convert_btn,
            inputs=None,
            outputs=[gr_convert_btn]
        ).then(
            fn=disable_components,
            inputs=[],
            outputs=[gr_ebook_mode, gr_language, gr_voice_file, gr_voice_list, gr_device, gr_tts_engine_list, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list]
        ).then(
            fn=submit_convert_btn,
            inputs=[
                gr_session, gr_device, gr_ebook_file, gr_tts_engine_list, gr_language, gr_voice_list,
                gr_custom_model_list, gr_fine_tuned_list, gr_output_format_list,
                gr_xtts_temperature, gr_xtts_length_penalty, gr_xtts_num_beams, gr_xtts_repetition_penalty, gr_xtts_top_k, gr_xtts_top_p, gr_xtts_speed, gr_xtts_enable_text_splitting,
                gr_bark_text_temp, gr_bark_waveform_temp, gr_output_split, gr_output_split_hours
            ],
            outputs=[gr_tab_progress]
        ).then(
            fn=enable_components,
            inputs=[],
            outputs=[gr_ebook_mode, gr_language, gr_voice_file, gr_voice_list, gr_device, gr_tts_engine_list, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list]
        ).then(
            fn=refresh_interface,
            inputs=[gr_session],
            outputs=[gr_convert_btn, gr_ebook_file, gr_audiobook_list, gr_audiobook_player, gr_modal, gr_voice_list]
        )
        gr_write_data.change(
            fn=None,
            inputs=[gr_write_data],
            js="""
                (data)=>{
                    try{
                        if(data){
                            localStorage.clear();
                            if(data['event'] != 'clear'){
                                console.log('save: ', data);
                                window.localStorage.setItem('data', JSON.stringify(data));
                            }
                        }
                    }catch(e){
                        console.log('gr_write_data.change error: '+e)
                    }
                }
            """
        )       
        gr_read_data.change(
            fn=change_gr_read_data,
            inputs=[gr_read_data, gr_state_update],
            outputs=[gr_write_data, gr_state_update, gr_session, gr_glass_mask]
        ).then(
            fn=restore_interface,
            inputs=[gr_session],
            outputs=[
                gr_ebook_file, gr_ebook_mode, gr_device, gr_language,
                gr_tts_engine_list, gr_custom_model_list, gr_fine_tuned_list,
                gr_output_format_list, gr_audiobook_list, gr_audiobook_vtt,
                gr_xtts_temperature, gr_xtts_length_penalty, gr_xtts_num_beams, gr_xtts_repetition_penalty,
                gr_xtts_top_k, gr_xtts_top_p, gr_xtts_speed, gr_xtts_enable_text_splitting, gr_bark_text_temp,
                gr_bark_waveform_temp, gr_voice_list, gr_output_split, gr_output_split_hours, gr_timer
            ]
        ).then(
            fn=lambda session: update_gr_glass_mask(attr='class="hide"') if session else gr.update(),
            inputs=[gr_session],
            outputs=[gr_glass_mask]
        )
        gr_confirm_yes_btn.click(
            fn=confirm_deletion,
            inputs=[gr_voice_list, gr_custom_model_list, gr_audiobook_list, gr_session, gr_confirm_field_hidden],
            outputs=[gr_custom_model_list, gr_audiobook_list, gr_modal, gr_voice_list, gr_confirm_yes_btn, gr_confirm_no_btn]
        )
        gr_confirm_no_btn.click(
            fn=confirm_deletion,
            inputs=[gr_voice_list, gr_custom_model_list, gr_audiobook_list, gr_session],
            outputs=[gr_custom_model_list, gr_audiobook_list, gr_modal, gr_voice_list, gr_confirm_yes_btn, gr_confirm_no_btn]
        )
        app.load(
            fn=None,
            js=r'''
                ()=>{
                    try {
                        if (typeof(window.init_elements) !== "function") {
                            window.init_elements = () => {
                                console.log('window.init_elements called');
                                try {
                                    let lastCue = null;
                                    let fade_timeout = null;
                                    let last_time = 0;
                                    if (gr_root && gr_checkboxes && gr_radios && gr_audiobook_player_playback_time && gr_audiobook_sentence && gr_tab_progress) {
                                        console.log('components exist!');
                                        gr_audiobook_player.addEventListener("canplay", () => {
                                            console.log("canplay:", window.playback_time);
                                            if (Number.isFinite(window.playback_time) && window.playback_time > 0) {
                                                gr_audiobook_player.currentTime = window.playback_time;
                                            }
                                        }, { once: true });
                                        gr_audiobook_player.addEventListener("timeupdate", () => {
                                            window.playback_time = gr_audiobook_player.currentTime;
                                            const cue = findCue(window.playback_time);
                                            if (cue && cue !== lastCue) {
                                                if (fade_timeout) {
                                                    gr_audiobook_sentence.style.opacity = "1";
                                                } else {
                                                    gr_audiobook_sentence.style.opacity = "0";
                                                }
                                                gr_audiobook_sentence.style.transition = "none";
                                                gr_audiobook_sentence.value = cue.text;
                                                clearTimeout(fade_timeout);
                                                fade_timeout = setTimeout(() => {
                                                    gr_audiobook_sentence.style.transition = "opacity 0.1s ease-in";
                                                    gr_audiobook_sentence.style.opacity = "1";
                                                    fade_timeout = null;
                                                }, 33);
                                                lastCue = cue;
                                            } else if (!cue && lastCue !== null) {
                                                gr_audiobook_sentence.value = "...";
                                                lastCue = null;
                                            }
                                            const now = performance.now();
                                            if (now - last_time > 1000) {
                                                console.log("timeupdate", window.playback_time);
                                                gr_audiobook_player_playback_time.value = String(window.playback_time);
                                                gr_audiobook_player_playback_time.dispatchEvent(new Event("input", { bubbles: true }));
                                                last_time = now;
                                            }
                                        });
                                        gr_audiobook_player.addEventListener("ended", () => {
                                            gr_audiobook_sentence.value = "...";
                                            lastCue = null;
                                        });
                                        
                                        ///////////////
                                        
                                        // Observe programmatic changes
                                        new MutationObserver(tab_progress).observe(gr_tab_progress, { attributes: true, childList: true, subtree: true, characterData: true });
                                        // Also catch user edits
                                        gr_tab_progress.addEventListener("input", tab_progress);
                                        
                                        ///////////////
                                        
                                        const url = new URL(window.location);
                                        const theme = url.searchParams.get("__theme");
                                        let osTheme;
                                        let audioFilter = "";
                                        let elColor = "#666666";
                                        if (theme) {
                                            if (theme === "dark") {
                                                if (gr_audiobook_player) {
                                                    audioFilter = "invert(1) hue-rotate(180deg)";
                                                }
                                                elColor = "#fff";
                                            }
                                            gr_checkboxes.forEach(cb => { cb.style.border = "1px solid " + elColor; });
                                            gr_radios.forEach(cb => { cb.style.border = "1px solid " + elColor; });
                                        } else {
                                            osTheme = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
                                            if (osTheme) {
                                                if (gr_audiobook_player) {
                                                    audioFilter = "invert(1) hue-rotate(180deg)";
                                                }
                                                elColor = "#fff";
                                            }
                                            gr_checkboxes.forEach(cb => { cb.style.border = "1px solid " + elColor; });
                                            gr_radios.forEach(cb => { cb.style.border = "1px solid " + elColor; });
                                        }
                                        if (!gr_audiobook_player.style.transition) {
                                            gr_audiobook_player.style.transition = "filter 1s ease";
                                        }
                                        gr_audiobook_player.style.filter = audioFilter;
                                    }
                                } catch (e) {
                                    console.log("init_elements error:", e);
                                }
                            };
                        }
                        if (typeof(window.load_vtt) !== "function") {
                            window.load_vtt_timeout = null;
                            window.load_vtt = (path) => {
                                try {
                                    if (gr_audiobook_player && gr_audiobook_player_playback_time && gr_audiobook_sentence) {
                                        // Remove any <track> to bypass browser subtitle engine
                                        let existing = gr_root.querySelector("#gr_audiobook_track");
                                        if (existing) {
                                            existing.remove();
                                        }
                                        gr_audiobook_sentence.style.fontSize = "14px";
                                        gr_audiobook_sentence.style.fontWeight = "bold";
                                        gr_audiobook_sentence.style.width = "100%";
                                        gr_audiobook_sentence.style.height = "auto";
                                        gr_audiobook_sentence.style.textAlign = "center";
                                        gr_audiobook_sentence.style.margin = "0";
                                        gr_audiobook_sentence.style.padding = "7px 0 7px 0";
                                        gr_audiobook_sentence.style.lineHeight = "14px";
                                        gr_audiobook_sentence.value = "...";
                                        if (path) {
                                            fetch(path).then(res => res.text()).then(vttText => {
                                                parseVTTFast(vttText);
                                            });
                                        }
                                        gr_audiobook_player.load();
                                    } else {
                                        clearTimeout(window.load_vtt_timeout);
                                        window.load_vtt_timeout = setTimeout(window.load_vtt, 500, path);
                                    }
                                } catch (e) {
                                    console.log("load_vtt error:", e);
                                }
                            };
                        }
                        if (typeof(window.tab_progress) !== "function") {
                            window.tab_progress = () => {
                                const val = gr_tab_progress?.value || gr_tab_progress?.textContent || "";
                                const prct = val.trim().split(" ")[4];
                                if (prct && /^\d+(\.\d+)?%$/.test(prct)) {
                                    document.title = "Ebook2Audiobook: " + prct;
                                }
                            };
                        }
                        function parseVTTFast(vtt) {
                            const lines = vtt.split(/\r?\n/);
                            const timePattern = /(\d{2}:)?\d{2}:\d{2}\.\d{3}/;
                            let start = null, end = null, textBuffer = [];
                            cues = [];

                            function pushCue() {
                                if (start !== null && end !== null && textBuffer.length) {
                                    cues.push({ start, end, text: textBuffer.join("\n") });
                                }
                                start = end = null;
                                textBuffer.length = 0;
                            }

                            for (let i = 0, len = lines.length; i < len; i++) {
                                const line = lines[i];
                                if (!line.trim()) { pushCue(); continue; }
                                if (line.includes("-->")) {
                                    const [s, e] = line.split("-->").map(l => l.trim().split(" ")[0]);
                                    if (timePattern.test(s) && timePattern.test(e)) {
                                        start = toSeconds(s);
                                        end = toSeconds(e);
                                    }
                                } else if (!timePattern.test(line)) {
                                    textBuffer.push(line);
                                }
                            }
                            pushCue();
                        }
                        
                        function toSeconds(ts) {
                            const parts = ts.split(":");
                            if (parts.length === 3) {
                                return parseInt(parts[0], 10) * 3600 +
                                       parseInt(parts[1], 10) * 60 +
                                       parseFloat(parts[2]);
                            }
                            return parseInt(parts[0], 10) * 60 + parseFloat(parts[1]);
                        }

                        function findCue(time) {
                            let lo = 0, hi = cues.length - 1;
                            while (lo <= hi) {
                                const mid = (lo + hi) >> 1;
                                const cue = cues[mid];
                                if (time < cue.start) {
                                    hi = mid - 1;
                                } else if (time >= cue.end) {
                                    lo = mid + 1;
                                } else {
                                    return cue;
                                }
                            }
                            return null;
                        }
                        
                        //////////////////////
                        
                        let gr_root;
                        let gr_checkboxes;
                        let gr_radios;
                        let gr_audiobook_player_playback_time;
                        let gr_audiobook_sentence;
                        let gr_audiobook_player;
                        let gr_tab_progress;
                        let load_timeout;
                        let cues = [];

                        function init() {
                            try {
                                gr_root = (window.gradioApp && window.gradioApp()) || document;
                                if (!gr_root) {
                                    clearTimeout(load_timeout);
                                    load_timeout = setTimeout(init, 1000);
                                    return;
                                }
                                gr_audiobook_player = gr_root.querySelector("#gr_audiobook_player");
                                gr_audiobook_player_playback_time = gr_root.querySelector("#gr_audiobook_player_playback_time input");
                                gr_audiobook_sentence = gr_root.querySelector("#gr_audiobook_sentence textarea");
                                gr_tab_progress = gr_root.querySelector("#gr_tab_progress");
                                gr_checkboxes = gr_root.querySelectorAll("input[type='checkbox']");
                                gr_radios = gr_root.querySelectorAll("input[type='radio']");
                                // If key elements aren’t mounted yet, retry
                                if (!gr_audiobook_player || !gr_audiobook_player_playback_time) {
                                    clearTimeout(load_timeout);
                                    console.log("Componenents not ready... retrying");
                                    load_timeout = setTimeout(init, 1000);
                                    return;
                                }
                                // if container, get inner <audio>/<video>
                                if (gr_audiobook_player && !gr_audiobook_player.matches?.("audio,video")) {
                                    const real = gr_audiobook_player.querySelector?.("audio,video");
                                    if (real) gr_audiobook_player = real;
                                }
                                console.log("Componenents ready!");
                                window.init_elements();
                            } catch (e) {
                                console.log("init error:", e);
                                clearTimeout(load_timeout);
                                load_timeout = setTimeout(init, 1000);
                            }
                        }
                        
                        init();

                        window.addEventListener("beforeunload", () => {
                            try {
                                const saved = JSON.parse(localStorage.getItem("data") || "{}");
                                if (saved.tab_id == window.tab_id || !saved.tab_id) {
                                    saved.tab_id = undefined;
                                    saved.status = undefined;
                                    localStorage.setItem("data", JSON.stringify(saved));
                                }
                            } catch (e) {
                                console.log("Error updating status on unload:", e);
                            }
                        });

                        window.playback_time = 0;
                        const stored = window.localStorage.getItem("data");
                        if (stored) {
                            const parsed = JSON.parse(stored);
                            parsed.tab_id = "tab-" + performance.now().toString(36) + "-" + Math.random().toString(36).substring(2, 10);
                            window.playback_time = parsed.playback_time;
                            console.log("window.playback_time = null;: ", window.playback_time);
                            return parsed;
                        }
                    } catch (e) {
                        console.log("gr_raed_data js error:", e);
                    }
                    return null;
                }
            ''',
            outputs=[gr_read_data],
        )
        app.unload(cleanup_session)
    try:
        all_ips = get_all_ip_addresses()
        msg = f'IPs available for connection:\n{all_ips}\nNote: 0.0.0.0 is not the IP to connect. Instead use an IP above to connect.'
        show_alert({"type": "info", "msg": msg})
        os.environ['no_proxy'] = ' ,'.join(all_ips)
        app.queue(default_concurrency_limit=interface_concurrency_limit).launch(debug=bool(int(os.environ.get('GRADIO_DEBUG', '0'))),show_error=debug_mode, favicon_path='./favicon.ico', server_name=interface_host, server_port=interface_port, share=is_gui_shared, max_file_size=max_upload_size)
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
