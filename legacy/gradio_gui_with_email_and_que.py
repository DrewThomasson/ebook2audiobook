print("starting...")
import ebooklib
from ebooklib import epub

import os
import subprocess
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import csv
import nltk

import os
import subprocess
import sys
import torchaudio

import os
import torch
from TTS.api import TTS
from nltk.tokenize import sent_tokenize
from pydub import AudioSegment

from tqdm import tqdm



import os
import subprocess
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import csv
import nltk

from bs4 import BeautifulSoup
import os
import shutil
import subprocess
import re
from pydub import AudioSegment
import tempfile
import urllib.request
import zipfile
import requests
from tqdm import tqdm
import nltk
from nltk.tokenize import sent_tokenize
import torch
import torchaudio
import gradio as gr
from threading import Lock, Thread
from queue import Queue
import smtplib
from email.mime.text import MIMEText


import os
import shutil
import subprocess
import re
from pydub import AudioSegment
import tempfile
from pydub import AudioSegment
import os
import nltk
from nltk.tokenize import sent_tokenize
import sys
import torch
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from tqdm import tqdm
import gradio as gr
from gradio import Progress
import urllib.request
import zipfile


default_target_voice_path = "default_voice.wav"  # Ensure this is a valid path
default_language_code = "en"


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device selected is: {device}")

nltk.download('punkt')  # Ensure necessary models are downloaded

# Global variables for queue management
queue = Queue()
queue_lock = Lock()

# Function to send an email with the download link
def send_email(to_address, download_link):
    from_address = "your_email@example.com"  # Replace with your email
    subject = "Your Audiobook is Ready"
    body = f"Your audiobook has been processed. You can download it from the following link: {download_link}"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address

    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:  # Replace with your SMTP server details
            server.starttls()
            server.login(from_address, "your_password")  # Replace with your email password
            server.sendmail(from_address, [to_address], msg.as_string())
            print(f"Email sent to {to_address}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to download and extract the custom model
def download_and_extract_zip(url, extract_to='.'):
    try:
        os.makedirs(extract_to, exist_ok=True)
        zip_path = os.path.join(extract_to, 'model.zip')
        
        with tqdm(unit='B', unit_scale=True, miniters=1, desc="Downloading Model") as t:
            def reporthook(blocknum, blocksize, totalsize):
                t.total = totalsize
                t.update(blocknum * blocksize - t.n)
            urllib.request.urlretrieve(url, zip_path, reporthook=reporthook)
        print(f"Downloaded zip file to {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            files = zip_ref.namelist()
            with tqdm(total=len(files), unit="file", desc="Extracting Files") as t:
                for file in files:
                    if not file.endswith('/'):
                        extracted_path = zip_ref.extract(file, extract_to)
                        base_file_path = os.path.join(extract_to, os.path.basename(file))
                        os.rename(extracted_path, base_file_path)
                    t.update(1)
        
        os.remove(zip_path)
        for root, dirs, files in os.walk(extract_to, topdown=False):
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        print(f"Extracted files to {extract_to}")
        
        required_files = ['model.pth', 'config.json', 'vocab.json_']
        missing_files = [file for file in required_files if not os.path.exists(os.path.join(extract_to, file))]
        
        if not missing_files:
            print("All required files (model.pth, config.json, vocab.json_) found.")
        else:
            print(f"Missing files: {', '.join(missing_files)}")
    
    except Exception as e:
        print(f"Failed to download or extract zip file: {e}")

# Function to check if a folder is empty
def is_folder_empty(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        return not os.listdir(folder_path)
    else:
        print(f"The path {folder_path} is not a valid folder.")
        return None

# Function to remove a folder and its contents
def remove_folder_with_contents(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Successfully removed {folder_path} and all of its contents.")
    except Exception as e:
        print(f"Error removing {folder_path}: {e}")

# Function to wipe the contents of a folder
def wipe_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
            print(f"Removed file: {item_path}")
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
            print(f"Removed directory and its contents: {item_path}")
    
    print(f"All contents wiped from {folder_path}.")

# Function to create M4B from chapters
def create_m4b_from_chapters(input_dir, ebook_file, output_dir):
    def sort_key(chapter_file):
        numbers = re.findall(r'\d+', chapter_file)
        return int(numbers[0]) if numbers else 0

    def extract_metadata_and_cover(ebook_path):
        try:
            cover_path = ebook_path.rsplit('.', 1)[0] + '.jpg'
            subprocess.run(['ebook-meta', ebook_path, '--get-cover', cover_path], check=True)
            if os.path.exists(cover_path):
                return cover_path
        except Exception as e:
            print(f"Error extracting eBook metadata or cover: {e}")
        return None

    def combine_wav_files(chapter_files, output_path):
        combined_audio = AudioSegment.empty()
        for chapter_file in chapter_files:
            audio_segment = AudioSegment.from_wav(chapter_file)
            combined_audio += audio_segment
        combined_audio.export(output_path, format='wav')
        print(f"Combined audio saved to {output_path}")

    def generate_ffmpeg_metadata(chapter_files, metadata_file):
        with open(metadata_file, 'w') as file:
            file.write(';FFMETADATA1\n')
            start_time = 0
            for index, chapter_file in enumerate(chapter_files):
                duration_ms = len(AudioSegment.from_wav(chapter_file))
                file.write(f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={start_time}\n')
                file.write(f'END={start_time + duration_ms}\ntitle=Chapter {index + 1}\n')
                start_time += duration_ms

    def create_m4b(combined_wav, metadata_file, cover_image, output_m4b):
        os.makedirs(os.path.dirname(output_m4b), exist_ok=True)
        
        ffmpeg_cmd = ['ffmpeg', '-i', combined_wav, '-i', metadata_file]
        if cover_image:
            ffmpeg_cmd += ['-i', cover_image, '-map', '0:a', '-map', '2:v']
        else:
            ffmpeg_cmd += ['-map', '0:a']
        
        ffmpeg_cmd += ['-map_metadata', '1', '-c:a', 'aac', '-b:a', '192k']
        if cover_image:
            ffmpeg_cmd += ['-c:v', 'png', '-disposition:v', 'attached_pic']
        ffmpeg_cmd += [output_m4b]

        subprocess.run(ffmpeg_cmd, check=True)

    chapter_files = sorted([os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.wav')], key=sort_key)
    temp_dir = tempfile.gettempdir()
    temp_combined_wav = os.path.join(temp_dir, 'combined.wav')
    metadata_file = os.path.join(temp_dir, 'metadata.txt')
    cover_image = extract_metadata_and_cover(ebook_file)
    output_m4b = os.path.join(output_dir, os.path.splitext(os.path.basename(ebook_file))[0] + '.m4b')

    combine_wav_files(chapter_files, temp_combined_wav)
    generate_ffmpeg_metadata(chapter_files, metadata_file)
    create_m4b(temp_combined_wav, metadata_file, cover_image, output_m4b)

    if os.path.exists(temp_combined_wav):
        os.remove(temp_combined_wav)
    if os.path.exists(metadata_file):
        os.remove(metadata_file)
    if cover_image and os.path.exists(cover_image):
        os.remove(cover_image)

# Function to create chapter-labeled book
def create_chapter_labeled_book(ebook_file_path):
    def ensure_directory(directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Created directory: {directory_path}")

    ensure_directory(os.path.join(".", 'Working_files', 'Book'))

    def convert_to_epub(input_path, output_path):
        try:
            subprocess.run(['ebook-convert', input_path, output_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while converting the eBook: {e}")
            return False
        return True

    def save_chapters_as_text(epub_path):
        directory = os.path.join(".", "Working_files", "temp_ebook")
        ensure_directory(directory)

        book = epub.read_epub(epub_path)

        previous_chapter_text = ''
        previous_filename = ''
        chapter_counter = 0

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text()

                if text.strip():
                    if len(text) < 2300 and previous_filename:
                        with open(previous_filename, 'a', encoding='utf-8') as file:
                            file.write('\n' + text)
                    else:
                        previous_filename = os.path.join(directory, f"chapter_{chapter_counter}.txt")
                        chapter_counter += 1
                        with open(previous_filename, 'w', encoding='utf-8') as file:
                            file.write(text)
                            print(f"Saved chapter: {previous_filename}")

    input_ebook = ebook_file_path
    output_epub = os.path.join(".", "Working_files", "temp.epub")

    if os.path.exists(output_epub):
        os.remove(output_epub)
        print(f"File {output_epub} has been removed.")
    else:
        print(f"The file {output_epub} does not exist.")

    if convert_to_epub(input_ebook, output_epub):
        save_chapters_as_text(output_epub)

    nltk.download('punkt')

    def process_chapter_files(folder_path, output_csv):
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Text', 'Start Location', 'End Location', 'Is Quote', 'Speaker', 'Chapter'])

            chapter_files = sorted(os.listdir(folder_path), key=lambda x: int(x.split('_')[1].split('.')[0]))
            for filename in chapter_files:
                if filename.startswith('chapter_') and filename.endswith('.txt'):
                    chapter_number = int(filename.split('_')[1].split('.')[0])
                    file_path = os.path.join(folder_path, filename)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            text = file.read()
                            if text:
                                text = "NEWCHAPTERABC" + text
                            sentences = nltk.tokenize.sent_tokenize(text)
                            for sentence in sentences:
                                start_location = text.find(sentence)
                                end_location = start_location + len(sentence)
                                writer.writerow([sentence, start_location, end_location, 'True', 'Narrator', chapter_number])
                    except Exception as e:
                        print(f"Error processing file {filename}: {e}")

    folder_path = os.path.join(".", "Working_files", "temp_ebook")
    output_csv = os.path.join(".", "Working_files", "Book", "Other_book.csv")

    process_chapter_files(folder_path, output_csv)

    def sort_key(filename):
        match = re.search(r'chapter_(\d+)\.txt', filename)
        return int(match.group(1)) if match else 0

    def combine_chapters(input_folder, output_file):
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]
        sorted_files = sorted(files, key=sort_key)

        with open(output_file, 'w', encoding='utf-8') as outfile:
            for i, filename in enumerate(sorted_files):
                with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    if i < len(sorted_files) - 1:
                        outfile.write("\nNEWCHAPTERABC\n")

    input_folder = os.path.join(".", 'Working_files', 'temp_ebook')
    output_file = os.path.join(".", 'Working_files', 'Book', 'Chapter_Book.txt')

    combine_chapters(input_folder, output_file)
    ensure_directory(os.path.join(".", "Working_files", "Book"))

# Function to combine WAV files
def combine_wav_files(input_directory, output_directory, file_name):
    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, file_name)
    combined_audio = AudioSegment.empty()
    input_file_paths = sorted(
        [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.endswith(".wav")],
        key=lambda f: int(''.join(filter(str.isdigit, f)))
    )
    for input_file_path in input_file_paths:
        audio_segment = AudioSegment.from_wav(input_file_path)
        combined_audio += audio_segment
    combined_audio.export(output_file_path, format='wav')
    print(f"Combined audio saved to {output_file_path}")

# Function to split long sentences
def split_long_sentence(sentence, max_length=249, max_pauses=10):
    parts = []
    while len(sentence) > max_length or sentence.count(',') + sentence.count(';') + sentence.count('.') > max_pauses:
        possible_splits = [i for i, char in enumerate(sentence) if char in ',;.' and i < max_length]
        if possible_splits:
            split_at = possible_splits[-1] + 1
        else:
            split_at = max_length
        parts.append(sentence[:split_at].strip())
        sentence = sentence[split_at:].strip()
    parts.append(sentence)
    return parts

# Function to convert chapters to audio using custom model
def convert_chapters_to_audio_custom_model(chapters_dir, output_audio_dir, target_voice_path=None, language=None, custom_model=None):
    if target_voice_path is None:
        target_voice_path = default_target_voice_path
    if custom_model:
        print("Loading custom model...")
        config = XttsConfig()
        config.load_json(custom_model['config'])
        model = Xtts.init_from_config(config)
        model.load_checkpoint(config, checkpoint_path=custom_model['model'], vocab_path=custom_model['vocab'], use_deepspeed=False)
        model.device
        print("Computing speaker latents...")
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=[target_voice_path])
    else:
        selected_tts_model = "tts_models/multilingual/multi-dataset/xtts_v2"
        tts = TTS(selected_tts_model, progress_bar=False).to(device)

    if not os.path.exists(output_audio_dir):
        os.makedirs(output_audio_dir)

    for chapter_file in sorted(os.listdir(chapters_dir)):
        if chapter_file.endswith('.txt'):
            match = re.search(r"chapter_(\d+).txt", chapter_file)
            if match:
                chapter_num = int(match.group(1))
            else:
                print(f"Skipping file {chapter_file} as it does not match the expected format.")
                continue

            chapter_path = os.path.join(chapters_dir, chapter_file)
            output_file_name = f"audio_chapter_{chapter_num}.wav"
            output_file_path = os.path.join(output_audio_dir, output_file_name)
            temp_audio_directory = os.path.join(".", "Working_files", "temp")
            os.makedirs(temp_audio_directory, exist_ok=True)
            temp_count = 0

            with open(chapter_path, 'r', encoding='utf-8') as file:
                chapter_text = file.read()
                sentences = sent_tokenize(chapter_text, language='italian' if language == 'it' else 'english')
                for sentence in tqdm(sentences, desc=f"Chapter {chapter_num}"):
                    fragments = split_long_sentence(sentence, max_length=249 if language == "en" else 213, max_pauses=10)
                    for fragment in fragments:
                        if fragment != "":
                            print(f"Generating fragment: {fragment}...")
                            fragment_file_path = os.path.join(temp_audio_directory, f"{temp_count}.wav")
                            if custom_model:
                                out = model.inference(fragment, language, gpt_cond_latent, speaker_embedding, temperature=0.7)
                                torchaudio.save(fragment_file_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)
                            else:
                                speaker_wav_path = target_voice_path if target_voice_path else default_target_voice_path
                                language_code = language if language else default_language_code
                                tts.tts_to_file(text=fragment, file_path=fragment_file_path, speaker_wav=speaker_wav_path, language=language_code)
                            temp_count += 1

            combine_wav_files(temp_audio_directory, output_audio_dir, output_file_name)
            wipe_folder(temp_audio_directory)
            print(f"Converted chapter {chapter_num} to audio.")

# Function to convert chapters to audio using standard model
def convert_chapters_to_audio_standard_model(chapters_dir, output_audio_dir, target_voice_path=None, language=None):
    selected_tts_model = "tts_models/multilingual/multi-dataset/xtts_v2"
    tts = TTS(selected_tts_model, progress_bar=False).to(device)

    if not os.path.exists(output_audio_dir):
        os.makedirs(output_audio_dir)

    for chapter_file in sorted(os.listdir(chapters_dir)):
        if chapter_file.endswith('.txt'):
            match = re.search(r"chapter_(\d+).txt", chapter_file)
            if match:
                chapter_num = int(match.group(1))
            else:
                print(f"Skipping file {chapter_file} as it does not match the expected format.")
                continue

            chapter_path = os.path.join(chapters_dir, chapter_file)
            output_file_name = f"audio_chapter_{chapter_num}.wav"
            output_file_path = os.path.join(output_audio_dir, output_file_name)
            temp_audio_directory = os.path.join(".", "Working_files", "temp")
            os.makedirs(temp_audio_directory, exist_ok=True)
            temp_count = 0

            with open(chapter_path, 'r', encoding='utf-8') as file:
                chapter_text = file.read()
                sentences = sent_tokenize(chapter_text, language='italian' if language == 'it' else 'english')
                for sentence in tqdm(sentences, desc=f"Chapter {chapter_num}"):
                    fragments = split_long_sentence(sentence, max_length=249 if language == "en" else 213, max_pauses=10)
                    for fragment in fragments:
                        if fragment != "":
                            print(f"Generating fragment: {fragment}...")
                            fragment_file_path = os.path.join(temp_audio_directory, f"{temp_count}.wav")
                            speaker_wav_path = target_voice_path if target_voice_path else default_target_voice_path
                            language_code = language if language else default_language_code
                            tts.tts_to_file(text=fragment, file_path=fragment_file_path, speaker_wav=speaker_wav_path, language=language_code)
                            temp_count += 1

            combine_wav_files(temp_audio_directory, output_audio_dir, output_file_name)
            wipe_folder(temp_audio_directory)
            print(f"Converted chapter {chapter_num} to audio.")

# Function to handle the processing of an eBook to an audiobook
def process_request(ebook_file, target_voice, language, email, use_custom_model, custom_model):
    working_files = os.path.join(".", "Working_files", "temp_ebook")
    full_folder_working_files = os.path.join(".", "Working_files")
    chapters_directory = os.path.join(".", "Working_files", "temp_ebook")
    output_audio_directory = os.path.join(".", 'Chapter_wav_files')
    remove_folder_with_contents(full_folder_working_files)
    remove_folder_with_contents(output_audio_directory)

    create_chapter_labeled_book(ebook_file.name)
    audiobook_output_path = os.path.join(".", "Audiobooks")
    
    if use_custom_model:
        convert_chapters_to_audio_custom_model(chapters_directory, output_audio_directory, target_voice, language, custom_model)
    else:
        convert_chapters_to_audio_standard_model(chapters_directory, output_audio_directory, target_voice, language)
    
    create_m4b_from_chapters(output_audio_directory, ebook_file.name, audiobook_output_path)

    m4b_filepath = os.path.join(audiobook_output_path, os.path.splitext(os.path.basename(ebook_file.name))[0] + '.m4b')
    
    # Upload the final audiobook to file.io
    with open(m4b_filepath, 'rb') as f:
        response = requests.post('https://file.io', files={'file': f})
        download_link = response.json().get('link', '')

    # Send the download link to the user's email
    if email and download_link:
        send_email(email, download_link)

    return download_link

# Function to manage the queue and process each request sequentially
def handle_queue():
    while True:
        ebook_file, target_voice, language, email, use_custom_model, custom_model = queue.get()
        process_request(ebook_file, target_voice, language, email, use_custom_model, custom_model)
        queue.task_done()

# Start the queue handler thread
thread = Thread(target=handle_queue, daemon=True)
thread.start()

# Gradio function to add a request to the queue
def enqueue_request(ebook_file, target_voice_file, language, email, use_custom_model, custom_model_file, custom_config_file, custom_vocab_file, custom_model_url=None):
    target_voice = target_voice_file.name if target_voice_file else None
    custom_model = None

    if use_custom_model and custom_model_file and custom_config_file and custom_vocab_file:
        custom_model = {
            'model': custom_model_file.name,
            'config': custom_config_file.name,
            'vocab': custom_vocab_file.name
        }
    if use_custom_model and custom_model_url:
        download_dir = os.path.join(".", "Working_files", "custom_model")
        download_and_extract_zip(custom_model_url, download_dir)
        custom_model = {
            'model': os.path.join(download_dir, 'model.pth'),
            'config': os.path.join(download_dir, 'config.json'),
            'vocab': os.path.join(download_dir, 'vocab.json_')
        }

    # Add request to the queue
    queue_lock.acquire()
    queue.put((ebook_file, target_voice, language, email, use_custom_model, custom_model))
    position = queue.qsize()
    queue_lock.release()
    return f"Your request has been added to the queue. You are number {position} in line."

# Gradio UI setup
language_options = [
    "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko"
]

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
    """
    )
    
    with gr.Row():
        with gr.Column(scale=3):
            ebook_file = gr.File(label="eBook File")
            target_voice_file = gr.File(label="Target Voice File (Optional)")
            language = gr.Dropdown(label="Language", choices=language_options, value="en")
            email = gr.Textbox(label="Email Address")
        
        with gr.Column(scale=3):
            use_custom_model = gr.Checkbox(label="Use Custom Model")
            custom_model_file = gr.File(label="Custom Model File (Optional)", visible=False)
            custom_config_file = gr.File(label="Custom Config File (Optional)", visible=False)
            custom_vocab_file = gr.File(label="Custom Vocab File (Optional)", visible=False)
            custom_model_url = gr.Textbox(label="Custom Model Zip URL (Optional)", visible=False)

    convert_btn = gr.Button("Convert to Audiobook", variant="primary")
    queue_status = gr.Textbox(label="Queue Status")

    convert_btn.click(
        enqueue_request,
        inputs=[ebook_file, target_voice_file, language, email, use_custom_model, custom_model_file, custom_config_file, custom_vocab_file, custom_model_url],
        outputs=[queue_status]
    )

    use_custom_model.change(
        lambda x: [gr.update(visible=x)] * 4,
        inputs=[use_custom_model],
        outputs=[custom_model_file, custom_config_file, custom_vocab_file, custom_model_url]
    )

demo.launch(share=True)
