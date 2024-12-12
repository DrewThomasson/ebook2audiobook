import os
import sys
import subprocess

from iso639 import languages
from deep_translator import GoogleTranslator
from tqdm import tqdm

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

# Your language mapping dictionary from lang.py
from lib.lang import language_mapping

env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8";
env["LANG"] = "en_US.UTF-8"

# Base text to be translated
base_text = "This is a test from the result of text file to audiobook conversion."

# Output directory
output_dir = "../ebooks/tests"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Path to your base cover image (adjust the path accordingly)
base_cover_image = "../ebooks/tests/__cover.jpg"

# List to keep track of languages that failed
failed_languages = []

# Loop over languages with a progress bar
for lang_code, lang_info in tqdm(language_mapping.items(), desc="Processing languages"):
    try:
        lang_iso = lang_code
        language_array = languages.get(part3=lang_code)
        if language_array and language_array.part1:
            lang_iso = language_array.part1
            if lang_iso == "zh":
                lang_iso = "zh-CN"
        # Translate the text
        translated_text = GoogleTranslator(source='en', target=lang_iso).translate(base_text)
        print(f"\nTranslated text for {lang_info['name']} ({lang_iso}): {translated_text}")

        # Write the translated text to a txt file
        txt_filename = f"test_{lang_code}.txt"
        txt_filepath = os.path.join(output_dir, txt_filename)
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write(translated_text)

        # Prepare the ebook-convert command
        azw3_filename = f"test_{lang_code}.azw3"
        azw3_filepath = os.path.join(output_dir, azw3_filename)

        title = f"Ebook {lang_info['name']} Test"
        authors = "Dev Team"
        language = lang_iso

        command = [
            "ebook-convert",
            txt_filepath,
            azw3_filepath,
            "--cover", base_cover_image,
            "--title", title,
            "--authors", authors,
            "--language", language,
            "--input-encoding", "utf-8"
        ]

        result = subprocess.run(command, env=env, text=True, encoding="utf-8")
        print(f"Ebook generated for {lang_info['name']} at {azw3_filepath}\n")

    except Exception as e:
        print(f"Erro: language {lang_code} not supported!")
        failed_languages.append(lang_code)
        continue

# After processing all languages, output the list of languages that failed
if failed_languages:
    print("\nThe following languages could not be processed:")
    for lang_code in failed_languages:
        lang_name = language_mapping[lang_code]['name']
        print(f"- {lang_name} ({lang_code})")
