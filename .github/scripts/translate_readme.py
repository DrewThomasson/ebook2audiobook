import os
import re
import difflib
from deep_translator import GoogleTranslator

# Define languages and corresponding output file names
LANGUAGES = {
    "ar": "README_ARA.md",
    "zh": "README_ZHO.md",
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

# Ensure readme directory exists
os.makedirs(TRANSLATION_DIR, exist_ok=True)

# Read original README
with open(README_PATH, "r", encoding="utf-8") as file:
    original_text = file.readlines()

# Check for changes using git diff
diff_output = os.popen("git diff -U0 HEAD~1 -- README.md").read()

changed_lines = []
for line in diff_output.split("\n"):
    if line.startswith("+") and not line.startswith("+++"):
        changed_lines.append(line[1:].strip())

if not changed_lines:
    print("No changes detected, skipping translation.")
    exit(0)

changed_text = "\n".join(changed_lines)

# Translate and update each language file
for lang_code, output_file in LANGUAGES.items():
    translator = GoogleTranslator(source="en", target=lang_code)

    # Translate modified text
    translated_text = translator.translate(changed_text)

    # Read existing translated file or create a new one
    translated_file_path = os.path.join(TRANSLATION_DIR, output_file)
    if os.path.exists(translated_file_path):
        with open(translated_file_path, "r", encoding="utf-8") as f:
            existing_content = f.readlines()
    else:
        existing_content = original_text.copy()

    # Replace modified lines with new translations
    for i, line in enumerate(original_text):
        if any(difflib.get_close_matches(line.strip(), changed_lines, n=1, cutoff=0.8)):
            existing_content[i] = translated_text + "\n"

    # Write updated translation
    with open(translated_file_path, "w", encoding="utf-8") as f:
        f.writelines(existing_content)

    print(f"Updated {output_file}")

print("All translations updated successfully!")
