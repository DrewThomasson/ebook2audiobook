from openai import OpenAI
import json
from tqdm import tqdm
import os
import time
from pathlib import Path

# Initialize the OpenAI client
client = OpenAI(api_key="key")

# Base sentence to be translated
base_sentence = "This is the test from the result of text file to audiobook conversion."

# Language mapping dictionary
language_mapping = {
    "en": {"name": "English", "native_name": "English", "char_limit": 250, "model": "en_core_web_sm", "iso3": "eng", "punctuation": [".", ",", ":", ";"]},
    "ar": {"name": "Arabic", "native_name": "العربية", "char_limit": 166, "model": "ar_core_news_sm", "iso3": "ara", "punctuation": [".", "،", "؛", ":"]},
    "bn": {"name": "Bengali", "native_name": "বাংলা", "char_limit": 200, "model": "bn_core_news_sm", "iso3": "ben", "punctuation": [".", ",", ":", ";"]}
}

def load_checkpoint():
    """Load the latest checkpoint if it exists."""
    checkpoint_file = "translation_checkpoint.json"
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None
    return None

def save_checkpoint(mapping):
    """Save the current progress to a checkpoint file."""
    checkpoint_file = "translation_checkpoint.json"
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)

def save_output(mapping):
    """Save the current progress to the output file."""
    output_file = "updated_language_mapping.py"
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("# Updated Language Mapping with Translations\n")
        file.write("language_mapping = ")
        file.write(json.dumps(mapping, ensure_ascii=False, indent=4))

def translate_text(base_sentence, target_language):
    """Translate text with error handling and retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",  # Note: Changed from gpt-4o-mini as that's not a valid model
                messages=[
                    {"role": "system", "content": f"You are a professional translator. Translate the following text into {target_language}. Respond with only the translated text, nothing else, even if you are unsure."},
                    {"role": "user", "content": base_sentence}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                return f"Error: {e}"
            time.sleep(1)  # Wait before retrying

def main():
    # Load checkpoint if it exists
    checkpoint = load_checkpoint()
    if checkpoint:
        print("Resuming from checkpoint...")
        language_mapping.update(checkpoint)

    # Create progress bar
    remaining_languages = [lang for lang in language_mapping.keys() 
                         if 'sample_sentence' not in language_mapping[lang]]
    
    if not remaining_languages:
        print("All translations are complete!")
        return

    with tqdm(total=len(remaining_languages), desc="Translating") as pbar:
        for lang_code in remaining_languages:
            lang_data = language_mapping[lang_code]
            target_language = lang_data['name']
            
            # Perform translation
            translation = translate_text(base_sentence, target_language)
            
            # Update mapping
            language_mapping[lang_code]['sample_sentence'] = translation
            
            # Save checkpoint and output after each translation
            save_checkpoint(language_mapping)
            save_output(language_mapping)
            
            # Update progress bar
            pbar.update(1)
            pbar.set_description(f"Translated {target_language}")

    # Clean up checkpoint file after successful completion
    if os.path.exists("translation_checkpoint.json"):
        os.remove("translation_checkpoint.json")
    
    print("\nTranslation completed successfully!")
    print(f"Final output saved to updated_language_mapping.py")

if __name__ == "__main__":
    main()