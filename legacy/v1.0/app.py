print("starting...")

import argparse

language_options = [
    "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko"
]
char_limits = {
    "en": 250,      # English
    "es": 239,      # Spanish
    "fr": 273,      # French
    "de": 253,      # German
    "it": 213,      # Italian
    "pt": 203,      # Portuguese
    "pl": 224,      # Polish
    "tr": 226,      # Turkish
    "ru": 182,      # Russian
    "nl": 251,      # Dutch
    "cs": 186,      # Czech
    "ar": 166,      # Arabic
    "zh-cn": 82,    # Chinese (Simplified)
    "ja": 71,       # Japanese
    "hu": 224,      # Hungarian
    "ko": 95,       # Korean
}

# Mapping of language codes to NLTK's supported language names
language_mapping = {
    "en": "english",
    "de": "german",
    "fr": "french",
    "es": "spanish",
    "it": "italian",
    "pt": "portuguese",
    "nl": "dutch",
    "pl": "polish",  
    "cs": "czech",   
    "ru": "russian",
    "tr": "turkish",
    "el": "greek",
    "et": "estonian",
    "no": "norwegian",
    "ml": "malayalam",
    "sl": "slovene",
    "da": "danish",
    "fi": "finnish",
    "sv": "swedish"
}


# Convert the list of languages to a string to display in the help text
language_options_str = ", ".join(language_options)

# Argument parser to handle optional parameters with descriptions
parser = argparse.ArgumentParser(
    description="Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.",
    epilog="Example: python script.py --headless --ebook path_to_ebook --voice path_to_voice --language en --use_custom_model True --custom_model model.pth --custom_config config.json --custom_vocab vocab.json"
)
parser.add_argument("--share", type=bool, default=False, help="Set to True to enable a public shareable Gradio link. Defaults to False.")
parser.add_argument("--headless", type=bool, default=False, help="Set to True to run in headless mode without the Gradio interface. Defaults to False.")
parser.add_argument("--ebook", type=str, help="Path to the ebook file for conversion. Required in headless mode.")
parser.add_argument("--voice", type=str, help="Path to the target voice file for TTS. Optional, uses a default voice if not provided.")
parser.add_argument("--language", type=str, default="en", 
                    help=f"Language for the audiobook conversion. Options: {language_options_str}. Defaults to English (en).")
parser.add_argument("--use_custom_model", type=bool, default=False, 
                    help="Set to True to use a custom TTS model. Defaults to False. Must be True to use custom models, otherwise you'll get an error.")
parser.add_argument("--custom_model", type=str, help="Path to the custom model file (.pth). Required if using a custom model.")
parser.add_argument("--custom_config", type=str, help="Path to the custom config file (config.json). Required if using a custom model.")
parser.add_argument("--custom_vocab", type=str, help="Path to the custom vocab file (vocab.json). Required if using a custom model.")
parser.add_argument("--custom_model_url", type=str, 
                    help=("URL to download the custom model as a zip file. Optional, but will be used if provided. "
                          "Examples include David Attenborough's model: "
                          "'https://huggingface.co/drewThomasson/xtts_David_Attenborough_fine_tune/resolve/main/Finished_model_files.zip?download=true'. "
                          "More XTTS fine-tunes can be found on my Hugging Face at 'https://huggingface.co/drewThomasson'."))
parser.add_argument("--temperature", type=float, default=0.65, help="Temperature for the model. Defaults to 0.65. Higher Tempatures will lead to more creative outputs IE: more Hallucinations. Lower Tempatures will be more monotone outputs IE: less Hallucinations.")
parser.add_argument("--length_penalty", type=float, default=1.0, help="A length penalty applied to the autoregressive decoder. Defaults to 1.0.  Not applied to custom models.")
parser.add_argument("--repetition_penalty", type=float, default=2.0, help="A penalty that prevents the autoregressive decoder from repeating itself. Defaults to 2.0.")
parser.add_argument("--top_k", type=int, default=50, help="Top-k sampling. Lower values mean more likely outputs and increased audio generation speed. Defaults to 50.")
parser.add_argument("--top_p", type=float, default=0.8, help="Top-p sampling. Lower values mean more likely outputs and increased audio generation speed. Defaults to 0.8.")
parser.add_argument("--speed", type=float, default=1.0, help="Speed factor for the speech generation. IE: How fast the Narrerator will speak. Defaults to 1.0.")
parser.add_argument("--enable_text_splitting", type=bool, default=False, help="Enable splitting text into sentences. Defaults to True.")

args = parser.parse_args()



import os
import shutil
import subprocess
import re
from pydub import AudioSegment
import tempfile
from pydub import AudioSegment
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
import socket
#import MeCab
#import unidic

#nltk.download('punkt_tab')

# Import the locally stored Xtts default model
#import import_locally_stored_tts_model_files

#make the nltk folder point to the nltk folder in the app dir
#nltk.data.path.append('/home/user/app/nltk_data')

# Download UniDic if it's not already installed
#unidic.download()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device selected is: {device}")

#nltk.download('punkt')  # Make sure to download the necessary models


def download_and_extract_zip(url, extract_to='.'):
    try:
        # Ensure the directory exists
        os.makedirs(extract_to, exist_ok=True)
        
        zip_path = os.path.join(extract_to, 'model.zip')
        
        # Download with progress bar
        with tqdm(unit='B', unit_scale=True, miniters=1, desc="Downloading Model") as t:
            def reporthook(blocknum, blocksize, totalsize):
                t.total = totalsize
                t.update(blocknum * blocksize - t.n)

            urllib.request.urlretrieve(url, zip_path, reporthook=reporthook)
        print(f"Downloaded zip file to {zip_path}")
        
        # Unzipping with progress bar
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            files = zip_ref.namelist()
            with tqdm(total=len(files), unit="file", desc="Extracting Files") as t:
                for file in files:
                    if not file.endswith('/'):  # Skip directories
                        # Extract the file to the temporary directory
                        extracted_path = zip_ref.extract(file, extract_to)
                        # Move the file to the base directory
                        base_file_path = os.path.join(extract_to, os.path.basename(file))
                        os.rename(extracted_path, base_file_path)
                    t.update(1)
        
        # Cleanup: Remove the ZIP file and any empty folders
        os.remove(zip_path)
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



def is_folder_empty(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # List directory contents
        if not os.listdir(folder_path):
            return True  # The folder is empty
        else:
            return False  # The folder is not empty
    else:
        print(f"The path {folder_path} is not a valid folder.")
        return None  # The path is not a valid folder

def remove_folder_with_contents(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Successfully removed {folder_path} and all of its contents.")
    except Exception as e:
        print(f"Error removing {folder_path}: {e}")




def wipe_folder(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    # Iterate over all the items in the given folder
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        # If it's a file, remove it and print a message
        if os.path.isfile(item_path):
            os.remove(item_path)
            print(f"Removed file: {item_path}")
        # If it's a directory, remove it recursively and print a message
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
            print(f"Removed directory and its contents: {item_path}")
    
    print(f"All contents wiped from {folder_path}.")


# Example usage
# folder_to_wipe = 'path_to_your_folder'
# wipe_folder(folder_to_wipe)


def create_m4b_from_chapters(input_dir, ebook_file, output_dir):
    # Function to sort chapters based on their numeric order
    def sort_key(chapter_file):
        numbers = re.findall(r'\d+', chapter_file)
        return int(numbers[0]) if numbers else 0

    # Extract metadata and cover image from the eBook file
    def extract_metadata_and_cover(ebook_path):
        try:
            cover_path = ebook_path.rsplit('.', 1)[0] + '.jpg'
            subprocess.run(['ebook-meta', ebook_path, '--get-cover', cover_path], check=True)
            if os.path.exists(cover_path):
                return cover_path
        except Exception as e:
            print(f"Error extracting eBook metadata or cover: {e}")
        return None
        # Combine WAV files into a single file
    def combine_wav_files(chapter_files, output_path, batch_size=256):
        # Initialize an empty audio segment
        combined_audio = AudioSegment.empty()
    
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
        combined_audio.export(output_path, format='wav')
        print(f"Combined audio saved to {output_path}")

    # Function to generate metadata for M4B chapters
    def generate_ffmpeg_metadata(chapter_files, metadata_file):
        with open(metadata_file, 'w') as file:
            file.write(';FFMETADATA1\n')
            start_time = 0
            for index, chapter_file in enumerate(chapter_files):
                duration_ms = len(AudioSegment.from_wav(chapter_file))
                file.write(f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={start_time}\n')
                file.write(f'END={start_time + duration_ms}\ntitle=Chapter {index + 1}\n')
                start_time += duration_ms

    # Generate the final M4B file using ffmpeg
    def create_m4b(combined_wav, metadata_file, cover_image, output_m4b):
        # Ensure the output directory exists
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



    # Main logic
    chapter_files = sorted([os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.wav')], key=sort_key)
    temp_dir = tempfile.gettempdir()
    temp_combined_wav = os.path.join(temp_dir, 'combined.wav')
    metadata_file = os.path.join(temp_dir, 'metadata.txt')
    cover_image = extract_metadata_and_cover(ebook_file)
    output_m4b = os.path.join(output_dir, os.path.splitext(os.path.basename(ebook_file))[0] + '.m4b')

    combine_wav_files(chapter_files, temp_combined_wav)
    generate_ffmpeg_metadata(chapter_files, metadata_file)
    create_m4b(temp_combined_wav, metadata_file, cover_image, output_m4b)

    # Cleanup
    if os.path.exists(temp_combined_wav):
        os.remove(temp_combined_wav)
    if os.path.exists(metadata_file):
        os.remove(metadata_file)
    if cover_image and os.path.exists(cover_image):
        os.remove(cover_image)

# Example usage
# create_m4b_from_chapters('path_to_chapter_wavs', 'path_to_ebook_file', 'path_to_output_dir')






#this code right here isnt the book grabbing thing but its before to refrence in order to create the sepecial chapter labeled book thing with calibre idk some systems cant seem to get it so just in case but the next bit of code after this is the book grabbing code with booknlp 
import os
import subprocess
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
import csv
import nltk

# Only run the main script if Value is True
def create_chapter_labeled_book(ebook_file_path):
    # Function to ensure the existence of a directory
    def ensure_directory(directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Created directory: {directory_path}")

    ensure_directory(os.path.join(".", 'Working_files', 'Book'))

    def convert_to_epub(input_path, output_path):
        # Convert the ebook to EPUB format using Calibre's ebook-convert
        try:
            subprocess.run(['ebook-convert', input_path, output_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while converting the eBook: {e}")
            return False
        return True

    def save_chapters_as_text(epub_path):
        # Create the directory if it doesn't exist
        directory = os.path.join(".", "Working_files", "temp_ebook")
        ensure_directory(directory)

        # Open the EPUB file
        book = epub.read_epub(epub_path)

        previous_chapter_text = ''
        previous_filename = ''
        chapter_counter = 0

        # Iterate through the items in the EPUB file
        for item in book.get_items():
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
                        previous_filename = os.path.join(directory, f"chapter_{chapter_counter}.txt")
                        chapter_counter += 1
                        with open(previous_filename, 'w', encoding='utf-8') as file:
                            file.write(text)
                            print(f"Saved chapter: {previous_filename}")

    # Example usage
    input_ebook = ebook_file_path  # Replace with your eBook file path
    output_epub = os.path.join(".", "Working_files", "temp.epub")


    if os.path.exists(output_epub):
        os.remove(output_epub)
        print(f"File {output_epub} has been removed.")
    else:
        print(f"The file {output_epub} does not exist.")

    if convert_to_epub(input_ebook, output_epub):
        save_chapters_as_text(output_epub)

    # Download the necessary NLTK data (if not already present)
    #nltk.download('punkt')

    def process_chapter_files(folder_path, output_csv):
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write the header row
            writer.writerow(['Text', 'Start Location', 'End Location', 'Is Quote', 'Speaker', 'Chapter'])

            # Process each chapter file
            chapter_files = sorted(os.listdir(folder_path), key=lambda x: int(x.split('_')[1].split('.')[0]))
            for filename in chapter_files:
                if filename.startswith('chapter_') and filename.endswith('.txt'):
                    chapter_number = int(filename.split('_')[1].split('.')[0])
                    file_path = os.path.join(folder_path, filename)

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

    # Example usage
    folder_path = os.path.join(".", "Working_files", "temp_ebook")
    output_csv = os.path.join(".", "Working_files", "Book", "Other_book.csv")

    process_chapter_files(folder_path, output_csv)

    def sort_key(filename):
        """Extract chapter number for sorting."""
        match = re.search(r'chapter_(\d+)\.txt', filename)
        return int(match.group(1)) if match else 0

    def combine_chapters(input_folder, output_file):
        # Create the output folder if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # List all txt files and sort them by chapter number
        files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]
        sorted_files = sorted(files, key=sort_key)

        with open(output_file, 'w', encoding='utf-8') as outfile:  # Specify UTF-8 encoding here
            for i, filename in enumerate(sorted_files):
                with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as infile:  # And here
                    outfile.write(infile.read())
                    # Add the marker unless it's the last file
                    if i < len(sorted_files) - 1:
                        outfile.write("\nNEWCHAPTERABC\n")

    # Paths
    input_folder = os.path.join(".", 'Working_files', 'temp_ebook')
    output_file = os.path.join(".", 'Working_files', 'Book', 'Chapter_Book.txt')


    # Combine the chapters
    combine_chapters(input_folder, output_file)

    ensure_directory(os.path.join(".", "Working_files", "Book"))


#create_chapter_labeled_book()




import os
import subprocess
import sys
import torchaudio

# Check if Calibre's ebook-convert tool is installed
def calibre_installed():
    try:
        subprocess.run(['ebook-convert', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        print("Calibre is not installed. Please install Calibre for this functionality.")
        return False


import os
import torch
from TTS.api import TTS
from nltk.tokenize import sent_tokenize
from pydub import AudioSegment

default_target_voice_path = "default_voice.wav"  # Ensure this is a valid path
default_language_code = "en"


# Function to check if vocab.json exists and rename it
def rename_vocab_file_if_exists(directory):
    vocab_path = os.path.join(directory, 'vocab.json')
    new_vocab_path = os.path.join(directory, 'vocab.json_')

    # Check if vocab.json exists
    if os.path.exists(vocab_path):
        # Rename the file
        os.rename(vocab_path, new_vocab_path)
        print(f"Renamed {vocab_path} to {new_vocab_path}")
        return True  # Return True if the file was found and renamed


def combine_wav_files(input_directory, output_directory, file_name):
    # Ensure that the output directory exists, create it if necessary
    os.makedirs(output_directory, exist_ok=True)

    # Specify the output file path
    output_file_path = os.path.join(output_directory, file_name)

    # Initialize an empty audio segment
    combined_audio = AudioSegment.empty()

    # Get a list of all .wav files in the specified input directory and sort them
    input_file_paths = sorted(
        [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.endswith(".wav")],
        key=lambda f: int(''.join(filter(str.isdigit, f)))
    )

    # Sequentially append each file to the combined_audio
    for input_file_path in input_file_paths:
        audio_segment = AudioSegment.from_wav(input_file_path)
        combined_audio += audio_segment

    # Export the combined audio to the output file path
    combined_audio.export(output_file_path, format='wav')

    print(f"Combined audio saved to {output_file_path}")

# Function to split long strings into parts
# Modify the function to handle special cases for Chinese, Italian, and default for others
def split_long_sentence(sentence, language='en', max_pauses=10):
    """
    Splits a sentence into parts based on length or number of pauses without recursion.
    
    :param sentence: The sentence to split.
    :param language: The language of the sentence (default is English).
    :param max_pauses: Maximum allowed number of pauses in a sentence.
    :return: A list of sentence parts that meet the criteria.
    """
    #Get the Max character length for the selected language -2 : with a default of 248 if no language is found
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

"""
if 'tts' not in locals():
    tts = TTS(selected_tts_model, progress_bar=True).to(device)
"""
from tqdm import tqdm

# Convert chapters to audio using XTTS

def convert_chapters_to_audio_custom_model(chapters_dir, output_audio_dir, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, target_voice_path=None, language=None, custom_model=None):

    if target_voice_path==None:
        target_voice_path = default_target_voice_path

    if custom_model:
        print("Loading custom model...")
        config = XttsConfig()
        config.load_json(custom_model['config'])
        model = Xtts.init_from_config(config)
        model.load_checkpoint(config, checkpoint_path=custom_model['model'], vocab_path=custom_model['vocab'], use_deepspeed=False)
        model.to(device)
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
                # Check if the language code is supported
                nltk_language = language_mapping.get(language)
                if nltk_language:
                    # If the language is supported, tokenize using sent_tokenize
                    sentences = sent_tokenize(chapter_text, language=nltk_language)
                else:
                    # If the language is not supported, handle it (e.g., return the text unchanged)
                    sentences = [chapter_text]  # No tokenization, just wrap the text in a list
                #sentences = sent_tokenize(chapter_text, language='italian' if language == 'it' else 'english')
                for sentence in tqdm(sentences, desc=f"Chapter {chapter_num}"):
                    fragments = split_long_sentence(sentence, language=language)
                    for fragment in fragments:
                        if fragment != "":
                            print(f"Generating fragment: {fragment}...")
                            fragment_file_path = os.path.join(temp_audio_directory, f"{temp_count}.wav")
                            if custom_model:
                                # length penalty will not apply for custome models, its just too much of a headache perhaps if someone else can do it for me lol, im just one man :(
                                out = model.inference(fragment, language, gpt_cond_latent, speaker_embedding, temperature=temperature, repetition_penalty=repetition_penalty, top_k=top_k, top_p=top_p, speed=speed, enable_text_splitting=enable_text_splitting)
                                #out = model.inference(fragment, language, gpt_cond_latent, speaker_embedding, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting)
                                torchaudio.save(fragment_file_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)
                            else:
                                speaker_wav_path = target_voice_path if target_voice_path else default_target_voice_path
                                language_code = language if language else default_language_code
                                tts.tts_to_file(text=fragment, file_path=fragment_file_path, speaker_wav=speaker_wav_path, language=language_code, temperature=temperature, length_penalty=length_penalty, repetition_penalty=repetition_penalty, top_k=top_k, top_p=top_p, speed=speed, enable_text_splitting=enable_text_splitting)

                            temp_count += 1

            combine_wav_files(temp_audio_directory, output_audio_dir, output_file_name)
            wipe_folder(temp_audio_directory)
            print(f"Converted chapter {chapter_num} to audio.")



def convert_chapters_to_audio_standard_model(chapters_dir, output_audio_dir, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, target_voice_path=None, language="en"):
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
                # Check if the language code is supported
                nltk_language = language_mapping.get(language)
                if nltk_language:
                    # If the language is supported, tokenize using sent_tokenize
                    sentences = sent_tokenize(chapter_text, language=nltk_language)
                else:
                    # If the language is not supported, handle it (e.g., return the text unchanged)
                    sentences = [chapter_text]  # No tokenization, just wrap the text in a list
                #sentences = sent_tokenize(chapter_text, language='italian' if language == 'it' else 'english')
                for sentence in tqdm(sentences, desc=f"Chapter {chapter_num}"):
                    fragments = split_long_sentence(sentence, language=language)
                    for fragment in fragments:
                        if fragment != "":
                            print(f"Generating fragment: {fragment}...")
                            fragment_file_path = os.path.join(temp_audio_directory, f"{temp_count}.wav")
                            speaker_wav_path = target_voice_path if target_voice_path else default_target_voice_path
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

                            temp_count += 1

            combine_wav_files(temp_audio_directory, output_audio_dir, output_file_name)
            wipe_folder(temp_audio_directory)
            print(f"Converted chapter {chapter_num} to audio.")



# Define the functions to be used in the Gradio interface
def convert_ebook_to_audio(ebook_file, target_voice_file, language, use_custom_model, custom_model_file, custom_config_file, custom_vocab_file, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, custom_model_url=None, progress=gr.Progress()):

    ebook_file_path = args.ebook if args.ebook else ebook_file.name
    target_voice = args.voice if args.voice else target_voice_file.name if target_voice_file else None
    custom_model = None


    working_files = os.path.join(".", "Working_files", "temp_ebook")
    full_folder_working_files = os.path.join(".", "Working_files")
    chapters_directory = os.path.join(".", "Working_files", "temp_ebook")
    output_audio_directory = os.path.join(".", 'Chapter_wav_files')
    remove_folder_with_contents(full_folder_working_files)
    remove_folder_with_contents(output_audio_directory)

    # If running in headless mode, use the language from args
    if args.headless and args.language:
        language = args.language
    else:
        language = language  # Gradio dropdown value

    # If headless is used with the custom model arguments
    if args.use_custom_model and args.custom_model and args.custom_config and args.custom_vocab:
        custom_model = {
            'model': args.custom_model,
            'config': args.custom_config,
            'vocab': args.custom_vocab
        }

    elif use_custom_model and custom_model_file and custom_config_file and custom_vocab_file:
        custom_model = {
            'model': custom_model_file.name,
            'config': custom_config_file.name,
            'vocab': custom_vocab_file.name
        }
    if (use_custom_model and custom_model_url) or (args.use_custom_model and custom_model_url):
        print(f"Received custom model URL: {custom_model_url}")
        download_dir = os.path.join(".", "Working_files", "custom_model")
        download_and_extract_zip(custom_model_url, download_dir)

        # Check if vocab.json exists and rename it
        if rename_vocab_file_if_exists(download_dir):
            print("vocab.json file was found and renamed.")
        
        custom_model = {
            'model': os.path.join(download_dir, 'model.pth'),
            'config': os.path.join(download_dir, 'config.json'),
            'vocab': os.path.join(download_dir, 'vocab.json_')
        }
    
    try:
        progress(0, desc="Starting conversion")
    except Exception as e:
        print(f"Error updating progress: {e}")
    
    if not calibre_installed():
        return "Calibre is not installed."
    
    
    try:
        progress(0.1, desc="Creating chapter-labeled book")
    except Exception as e:
        print(f"Error updating progress: {e}")
    
    create_chapter_labeled_book(ebook_file_path)
    audiobook_output_path = os.path.join(".", "Audiobooks")
    
    try:
        progress(0.3, desc="Converting chapters to audio")
    except Exception as e:
        print(f"Error updating progress: {e}")
    
    if use_custom_model:
        convert_chapters_to_audio_custom_model(chapters_directory, output_audio_directory, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, target_voice, language, custom_model)
    else:
        convert_chapters_to_audio_standard_model(chapters_directory, output_audio_directory, temperature, length_penalty, repetition_penalty, top_k, top_p, speed, enable_text_splitting, target_voice, language)
    
    try:
        progress(0.9, desc="Creating M4B from chapters")
    except Exception as e:
        print(f"Error updating progress: {e}")
    
    create_m4b_from_chapters(output_audio_directory, ebook_file_path, audiobook_output_path)
    
    # Get the name of the created M4B file
    m4b_filename = os.path.splitext(os.path.basename(ebook_file_path))[0] + '.m4b'
    m4b_filepath = os.path.join(audiobook_output_path, m4b_filename)

    try:
        progress(1.0, desc="Conversion complete")
    except Exception as e:
        print(f"Error updating progress: {e}")
    print(f"Audiobook created at {m4b_filepath}")
    return f"Audiobook created at {m4b_filepath}", m4b_filepath


def list_audiobook_files(audiobook_folder):
    # List all files in the audiobook folder
    files = []
    for filename in os.listdir(audiobook_folder):
        if filename.endswith('.m4b'):  # Adjust the file extension as needed
            files.append(os.path.join(audiobook_folder, filename))
    return files

def download_audiobooks():
    audiobook_output_path = os.path.join(".", "Audiobooks")
    return list_audiobook_files(audiobook_output_path)


# Gradio UI setup
def run_gradio_interface():
    language_options = [
        "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko"
    ]

    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="blue",
        neutral_hue="blue",
        text_size=gr.themes.sizes.text_md,
    )

# Gradio UI setup
def run_gradio_interface():
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
                    info="Lower values restrict outputs to more likely words and increase speed at which audio generates. "
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
                    info="Adjusts How fast the narrator will speak."
                )
                enable_text_splitting = gr.Checkbox(
                    label="Enable Text Splitting", 
                    value=False,
                    info="Splits long texts into sentences to generate audio in chunks. Useful for very long inputs."
                )

        convert_btn = gr.Button("Convert to Audiobook", variant="primary")
        output = gr.Textbox(label="Conversion Status")
        audio_player = gr.Audio(label="Audiobook Player", type="filepath")
        download_btn = gr.Button("Download Audiobook Files")
        download_files = gr.File(label="Download Files", interactive=False)

        convert_btn.click(
            lambda *args: convert_ebook_to_audio(
                *args[:7], 
                float(args[7]),  # Ensure temperature is float
                float(args[8]),  # Ensure length_penalty is float
                float(args[9]),  # Ensure repetition_penalty is float
                int(args[10]),   # Ensure top_k is int
                float(args[11]), # Ensure top_p is float
                float(args[12]), # Ensure speed is float
                *args[13:]
            ),
            inputs=[
                ebook_file, target_voice_file, language, use_custom_model, custom_model_file, custom_config_file, 
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
    local_ip = socket.gethostbyname(hostname)

    # Ensure Gradio runs and prints the correct local IP
    print(f"Running on local URL: http://{local_ip}:7860")
    print(f"Running on local URL: http://localhost:7860")

    # Launch Gradio app
    demo.launch(server_name="0.0.0.0", server_port=7860, share=args.share)





# Check if running in headless mode
if args.headless:
    # If the arg.custom_model_url exists then use it as the custom_model_url lol
    custom_model_url = args.custom_model_url if args.custom_model_url else None
    
    if not args.ebook:
        print("Error: In headless mode, you must specify an ebook file using --ebook.")
        exit(1)

    ebook_file_path = args.ebook
    target_voice = args.voice if args.voice else None
    custom_model = None

    if args.use_custom_model:
        # Check if custom_model_url is provided
        if args.custom_model_url:
            # Download the custom model from the provided URL
            custom_model_url = args.custom_model_url
        else:
            # If no URL is provided, ensure all custom model files are provided
            if not args.custom_model or not args.custom_config or not args.custom_vocab:
                print("Error: You must provide either a --custom_model_url or all of the following arguments:")
                print("--custom_model, --custom_config, and --custom_vocab")
                exit(1)
            else:
                # Assign the custom model files
                custom_model = {
                    'model': args.custom_model,
                    'config': args.custom_config,
                    'vocab': args.custom_vocab
                }



    # Example headless execution
    convert_ebook_to_audio(ebook_file_path, target_voice, args.language, args.use_custom_model, args.custom_model, args.custom_config, args.custom_vocab, args.temperature, args.length_penalty, args.repetition_penalty, args.top_k, args.top_p, args.speed, args.enable_text_splitting, custom_model_url)


else:
    # Launch Gradio UI
    run_gradio_interface()
