import os
import re
import subprocess
from deep_translator import GoogleTranslator

# Define translation languages (change to real target languages)
LANGUAGES = {
    "en": "README_ENG.md"
}

README_PATH = "README.md"
TRANSLATION_DIR = "readme"
MAX_CHARS = 5000  # Google Translate's character limit

# Ensure the readme directory exists
os.makedirs(TRANSLATION_DIR, exist_ok=True)

# Read the original README.md
with open(README_PATH, "r", encoding="utf-8") as file:
    original_text = file.read()

# === Step 1: Extract Translatable Text ===

# Store placeholders and extracted text
placeholders = []
translatable_text = []
placeholder_index = 0

def placeholder(text):
    """Stores text segment and returns a placeholder."""
    global placeholder_index
    key = f"{{{{PLACEHOLDER_{placeholder_index}}}}}"
    placeholders.append((key, text))
    placeholder_index += 1
    return key

# Patterns for non-translatable elements
patterns = {
    "code_blocks": r"```[\s\S]*?```",  # Multiline code blocks
    "inline_code": r"`[^`]+`",  # Inline code like `example`
    "links": r"\[.*?\]\(.*?\)",  # Markdown links [text](url)
    "images": r"!\[.*?\]\(.*?\)",  # Markdown images ![alt](url)
    "html_tags": r"<[^>]+>",  # HTML tags like <br>, <img>
    "blockquotes": r"> .*",  # Blockquotes
}

# Replace non-translatable elements with placeholders
processed_text = original_text
for pattern_name, pattern in patterns.items():
    processed_text = re.sub(pattern, lambda match: placeholder(match.group()), processed_text)

# Extract remaining translatable text
segments = re.split(r"(\n|\s\s+)", processed_text)  # Preserve newlines and spaces

# Store translatable text separately
for segment in segments:
    if segment.strip() and not any(placeholder in segment for placeholder, _ in placeholders):
        translatable_text.append(segment)

# === Step 2: Translate Only the Text Segments ===

def translate_text(text, target_lang):
    """Translates text using Google Translator."""
    translator = GoogleTranslator(source="en", target=target_lang)
    translated_segments = []
    for chunk in re.split(r'(?<=[.!?])\s+', text):  # Split into sentences
        if chunk.strip():
            translated_segments.append(translator.translate(chunk))
    return " ".join(translated_segments)

# Translate text for each language
translations = {}
for lang_code, output_file in LANGUAGES.items():
    print(f"Translating to {lang_code}...")

    # Join extracted text into a single block for translation
    text_to_translate = " ".join(translatable_text)
    translated_text = translate_text(text_to_translate, lang_code)

    # Restore placeholders into translated text
    for placeholder_key, original_content in placeholders:
        translated_text = translated_text.replace(placeholder_key, original_content)

    # Write translated file
    translated_file_path = os.path.join(TRANSLATION_DIR, output_file)
    with open(translated_file_path, "w", encoding="utf-8") as f:
        f.write(translated_text)

    print(f"✅ Translated README saved as {output_file}")

print("🎉 Translation completed successfully!")
