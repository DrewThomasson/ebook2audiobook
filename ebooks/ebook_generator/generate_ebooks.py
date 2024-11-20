import os
from deep_translator import GoogleTranslator
import subprocess
from tqdm import tqdm

# Your language mapping dictionary from lang.py
from lang import language_mapping

# Base text to be translated
base_text = "This is the test from the result of text file to audiobook conversion."

# Output directory
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Path to your base cover image (adjust the path accordingly)
base_cover_image = "base_files/Ebook Base Cover.jpeg"

# List to keep track of languages that failed
failed_languages = []

# Loop over languages with a progress bar
for lang_code, lang_info in tqdm(language_mapping.items(), desc="Processing languages"):
    try:
        # Translate the text
        translated_text = GoogleTranslator(source='en', target=lang_code).translate(base_text)
        print(f"\nTranslated text for {lang_info['name']} ({lang_code}): {translated_text}")

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
        language = lang_code

        command = [
            "ebook-convert",
            txt_filepath,
            azw3_filepath,
            "--cover", base_cover_image,
            "--title", title,
            "--authors", authors,
            "--language", language
        ]

        # Run the ebook-convert command
        subprocess.run(command)
        print(f"Ebook generated for {lang_info['name']} at {azw3_filepath}\n")

    except Exception as e:
        print(f"An error occurred for language {lang_code}: {e}")
        failed_languages.append(lang_code)
        continue

# After processing all languages, output the list of languages that failed
if failed_languages:
    print("\nThe following languages could not be processed:")
    for lang_code in failed_languages:
        lang_name = language_mapping[lang_code]['name']
        print(f"- {lang_name} ({lang_code})")
