import os
import re
import difflib
from deep_translator import GoogleTranslator
from markdown_it import MarkdownIt

# Define languages and corresponding output file names
LANGUAGES = {
    "ar": "README_ARA.md",
    "zh-CN": "README_ZHO.md",
    "cs": "README_CES.md",
    "hr": "README_HRV.md",
    "nl": "README_NLD.md",
    "fr": "README_FRA.md",
    "de": "README_DEU.md",
    "hi": "README_HIN.md",
    "hu": "README_HUN.md",
    "it": "README_ITA.md",
    "ja": "README_JPN.md",
    "ko": "README_KOR.md",
    "pl": "README_POL.md",
    "pt": "README_POR.md",
    "ru": "README_RUS.md",
    "es": "README_SPA.md",
    "tr": "README_TUR.md",
    "vi": "README_VIE.md",
}

README_PATH = "README.md"
TRANSLATION_DIR = "readme"
MAX_CHARS = 5000  # Google Translate's character limit

# Ensure readme directory exists
os.makedirs(TRANSLATION_DIR, exist_ok=True)

# Read original README
with open(README_PATH, "r", encoding="utf-8") as file:
    original_text = file.readlines()

# Check if this is the first commit
if os.system("git rev-parse --verify HEAD~1 > /dev/null 2>&1") != 0:
    print("First commit detected. Translating full README...")
    changed_text = "".join(original_text)
else:
    # Get modified lines
    diff_output = os.popen("git diff -U0 HEAD~1 -- README.md").read()
    changed_lines = [
        line[1:].strip() for line in diff_output.split("\n")
        if line.startswith("+") and not line.startswith("+++")
    ]
    
    if not changed_lines:
        print("No changes detected, skipping translation.")
        exit(0)

    changed_text = "\n".join(changed_lines)

# Function to split text into chunks <= 5000 chars for Google Translate
def split_text(text, max_chars=MAX_CHARS):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Split at sentence boundaries
    chunks, current_chunk = [], ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# Function to extract plain text from Markdown while preserving formatting
def extract_text_from_markdown(md_content):
    md = MarkdownIt()
    parsed = md.parse(md_content)
    
    extracted_text = []
    for token in parsed:
        if token.type in ["paragraph_open", "paragraph_close", "inline", "text"]:
            extracted_text.append(token.content)

    return "\n".join(extracted_text)

# Function to replace translated text back into Markdown
def replace_text_in_markdown(original, translated):
    """Replace only the changed lines while preserving Markdown structure."""
    original_lines = original.split("\n")
    translated_lines = translated.split("\n")

    if len(original_lines) == len(translated_lines):
        return "\n".join(translated_lines)
    
    result = []
    for orig, trans in zip(original_lines, translated_lines):
        if orig.strip() and trans.strip():
            result.append(trans)
        else:
            result.append(orig)

    return "\n".join(result)

# Extract text while keeping Markdown intact
plain_text = extract_text_from_markdown(changed_text)

# Translate and update each language file
for lang_code, output_file in LANGUAGES.items():
    translator = GoogleTranslator(source="en", target=lang_code)
    
    translated_chunks = [translator.translate(chunk) for chunk in split_text(plain_text)]
    translated_text = " ".join(translated_chunks)

    # Read existing translated file or create a new one
    translated_file_path = os.path.join(TRANSLATION_DIR, output_file)
    if os.path.exists(translated_file_path):
        with open(translated_file_path, "r", encoding="utf-8") as f:
            existing_content = f.read()
    else:
        existing_content = "".join(original_text)

    # Replace translated text in the Markdown file while keeping structure
    updated_content = replace_text_in_markdown(existing_content, translated_text)

    # Write updated translation
    with open(translated_file_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"Updated {output_file}")

print("All translations updated successfully!")
