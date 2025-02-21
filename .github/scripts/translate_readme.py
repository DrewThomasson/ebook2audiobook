import os
import re
import subprocess
from deep_translator import GoogleTranslator

# Define translation languages
LANGUAGES = {
    "en": "README_ENG.md",  # Testing by translating English to English
}

README_PATH = "README.md"
TRANSLATION_DIR = "readme"
MAX_CHARS = 5000  # Google Translate's character limit

# Ensure readme directory exists
os.makedirs(TRANSLATION_DIR, exist_ok=True)

# Read original README.md
with open(README_PATH, "r", encoding="utf-8") as file:
    original_text = file.read()

# === Step 1: Extract Text to Translate (Ignore Special Markdown Elements) ===

# Placeholder storage for text replacements
placeholders = []
text_segments = []
placeholder_index = 0

def placeholder(text):
    """Store text segment and return a placeholder."""
    global placeholder_index
    key = f"{{{{PLACEHOLDER_{placeholder_index}}}}}"
    placeholders.append((key, text))
    placeholder_index += 1
    return key

# Regex patterns for elements we should NOT translate
patterns = {
    "code_blocks": r"```[\s\S]*?```",  # Multiline code blocks
    "inline_code": r"`[^`]+`",  # Inline code like `example`
    "links": r"\[.*?\]\(.*?\)",  # Markdown links [text](url)
    "images": r"!\[.*?\]\(.*?\)",  # Markdown images ![alt](url)
    "html_tags": r"<[^>]+>",  # HTML tags like <br>, <img>
    "blockquotes": r"> .*",  # Blockquotes
}

# Replace elements with placeholders
processed_text = original_text
for pattern_name, pattern in patterns.items():
    processed_text = re.sub(pattern, lambda match: placeholder(match.group()), processed_text)

# Extract remaining text (translatable parts)
text_segments = re.split(r"(\n|\s\s+)", processed_text)  # Preserve spacing and line breaks

# === Step 2: Translate Only the Text Segments ===
translator = GoogleTranslator(source="en", target="en")  # Test translation (English to English)
translated_segments = []

for segment in text_segments:
    if segment.strip():  # Skip empty segments
        translated_segments.append(translator.translate(segment) if segment.isalnum() else segment)
    else:
        translated_segments.append(segment)  # Preserve spacing

# === Step 3: Restore Placeholders and Write Translated Markdown ===
translated_text = "".join(translated_segments)

# Replace placeholders with original elements
for placeholder_key, original_text in placeholders:
    translated_text = translated_text.replace(placeholder_key, original_text)

# Write translated file for each language
for lang_code, output_file in LANGUAGES.items():
    translated_file_path = os.path.join(TRANSLATION_DIR, output_file)
    
    with open(translated_file_path, "w", encoding="utf-8") as f:
        f.write(translated_text)

    print(f"Updated {output_file}")

print("✅ Translation completed successfully while preserving Markdown format!")
