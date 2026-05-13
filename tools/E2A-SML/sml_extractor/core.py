"""Core module for running BookNLP and extracting dialog/character data."""

import json
import os
import re
import tempfile
from collections import Counter
from pathlib import Path


def check_booknlp_installation() -> tuple[bool, str]:
    """Check if BookNLP and its dependencies are properly installed.

    Returns:
        Tuple of (is_ok, message). If not ok, message describes what's missing.
    """
    errors = []

    # Check booknlp package
    try:
        import booknlp  # noqa: F401
    except ImportError:
        errors.append(
            "BookNLP local module is not found. Ensure the 'booknlp' directory "
            "is in the same folder as this script."
        )
        return False, "\n".join(errors)

    # Check key dependencies that commonly fail
    dep_checks = [
        ("torch", "torch", "pip install torch"),
        ("transformers", "transformers", "pip install transformers>=4.30.0"),
        ("spacy", "spacy", "pip install spacy>=3.5.0"),
        ("sentence_transformers", "sentence-transformers", "pip install sentence-transformers"),
        ("numpy", "numpy", "pip install numpy>=1.24.0"),
    ]

    for module_name, pkg_name, install_cmd in dep_checks:
        try:
            __import__(module_name)
        except ImportError:
            errors.append(f"  - {pkg_name} is missing. Fix: {install_cmd}")

    if errors:
        return False, (
            "BookNLP dependencies are missing:\n"
            + "\n".join(errors)
            + "\n\nOr install all at once:\n"
            "  pip install -r requirements.txt\n"
            "  python -m spacy download en_core_web_sm"
        )

    # Check spacy model
    try:
        import spacy
        spacy.load("en_core_web_sm")
    except OSError:
        errors.append(
            "spaCy English model not found. Install it with:\n"
            "  python -m spacy download en_core_web_sm"
        )

    if errors:
        return False, "\n".join(errors)

    # Try the actual BookNLP import that tends to fail
    try:
        from booknlp.booknlp import BookNLP  # noqa: F401
    except (ImportError, ModuleNotFoundError, AttributeError, OSError) as e:
        return False, (
            f"BookNLP failed to initialize: {e}\n\n"
            "This usually means a dependency version conflict.\n"
            "Try reinstalling dependencies in a clean environment:\n"
            "  pip install -r requirements.txt\n"
            "  python -m spacy download en_core_web_sm"
        )

    return True, "BookNLP is ready."


def convert_ebook_to_txt(input_file: str, output_dir: str) -> str:
    """Convert an ebook file to plain text using calibre's ebook-convert if needed.

    Supports: .txt, .epub, .mobi, .pdf, .html, .fb2, .azw, .azw3
    Returns the path to the plain text file.
    """
    ext = Path(input_file).suffix.lower()
    if ext == ".txt":
        return input_file

    txt_path = os.path.join(output_dir, Path(input_file).stem + ".txt")
    try:
        import subprocess

        result = subprocess.run(
            ["ebook-convert", input_file, txt_path],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"ebook-convert failed: {result.stderr}"
            )
        return txt_path
    except FileNotFoundError:
        raise RuntimeError(
            "ebook-convert not found. Install Calibre to convert non-txt ebook formats. "
            "Download from: https://calibre-ebook.com/download"
        )


def run_booknlp(
    input_file: str,
    output_dir: str,
    model: str = "small",
    progress_callback=None,
) -> dict:
    """Run BookNLP pipeline on a text file and return extracted data.

    Args:
        input_file: Path to the input text file.
        output_dir: Directory for BookNLP output files.
        model: BookNLP model size ('small' or 'big').
        progress_callback: Optional callable(message, pct) for progress updates.

    Returns:
        Dict with keys: 'book_id', 'output_dir', 'characters', 'tokens_file',
                        'quotes_file', 'entities_file', 'book_file'

    Raises:
        RuntimeError: If BookNLP or its dependencies are not properly installed.
    """
    # Pre-check installation before attempting import
    ok, msg = check_booknlp_installation()
    if not ok:
        raise RuntimeError(f"BookNLP installation check failed:\n{msg}")

    from booknlp.booknlp import BookNLP

    os.makedirs(output_dir, exist_ok=True)
    book_id = Path(input_file).stem

    if progress_callback:
        progress_callback("Initializing BookNLP...", 5)

    model_params = {
        "pipeline": "entity,quote,supersense,event,coref",
        "model": model,
    }

    booknlp = BookNLP("en", model_params)

    if progress_callback:
        progress_callback(f"Processing book with BookNLP ({model} model)...", 10)

    booknlp.process(input_file, output_dir, book_id)

    if progress_callback:
        progress_callback("BookNLP processing complete.", 60)

    result = {
        "book_id": book_id,
        "output_dir": output_dir,
        "tokens_file": os.path.join(output_dir, f"{book_id}.tokens"),
        "quotes_file": os.path.join(output_dir, f"{book_id}.quotes"),
        "entities_file": os.path.join(output_dir, f"{book_id}.entities"),
        "book_file": os.path.join(output_dir, f"{book_id}.book"),
    }

    # Also check for generated character/book text files
    char_json = os.path.join(output_dir, f"{book_id}.characters_simple.json")
    book_txt = os.path.join(output_dir, f"{book_id}.book.txt")
    if os.path.exists(char_json):
        result["characters_simple_file"] = char_json
    if os.path.exists(book_txt):
        result["book_txt_file"] = book_txt

    return result


def load_booknlp_output(output_dir: str, book_id: str) -> dict:
    """Load BookNLP output files and return structured data.

    Returns dict with: tokens, quotes, entities, characters, book_data
    """
    data = {"book_id": book_id, "output_dir": output_dir}

    # Load tokens
    tokens_file = os.path.join(output_dir, f"{book_id}.tokens")
    if os.path.exists(tokens_file):
        data["tokens"] = _parse_tokens_file(tokens_file)

    # Load quotes
    quotes_file = os.path.join(output_dir, f"{book_id}.quotes")
    if os.path.exists(quotes_file):
        data["quotes"] = _parse_quotes_file(quotes_file)

    # Load entities
    entities_file = os.path.join(output_dir, f"{book_id}.entities")
    if os.path.exists(entities_file):
        data["entities"] = _parse_entities_file(entities_file)

    # Load book JSON
    book_file = os.path.join(output_dir, f"{book_id}.book")
    if os.path.exists(book_file):
        with open(book_file, "r", encoding="utf-8") as f:
            data["book_data"] = json.load(f)

    # Load characters_simple.json if exists
    char_file = os.path.join(output_dir, f"{book_id}.characters_simple.json")
    if os.path.exists(char_file):
        with open(char_file, "r", encoding="utf-8") as f:
            data["characters_simple"] = json.load(f)

    # Load book.txt if exists
    book_txt = os.path.join(output_dir, f"{book_id}.book.txt")
    if os.path.exists(book_txt):
        with open(book_txt, "r", encoding="utf-8") as f:
            data["book_txt"] = f.read()

    return data


def _parse_tokens_file(filepath: str) -> list:
    """Parse BookNLP tokens file into list of token dicts."""
    tokens = []
    with open(filepath, "r", encoding="utf-8") as f:
        header = f.readline().strip().split("\t")
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= len(header):
                token = dict(zip(header, parts))
                tokens.append(token)
    return tokens


def _parse_quotes_file(filepath: str) -> list:
    """Parse BookNLP quotes file into list of quote dicts."""
    quotes = []
    with open(filepath, "r", encoding="utf-8") as f:
        header = f.readline().strip().split("\t")
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= len(header):
                quote = dict(zip(header, parts))
                quotes.append(quote)
    return quotes


def _parse_entities_file(filepath: str) -> list:
    """Parse BookNLP entities file into list of entity dicts."""
    entities = []
    with open(filepath, "r", encoding="utf-8") as f:
        header = f.readline().strip().split("\t")
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= len(header):
                entity = dict(zip(header, parts))
                entities.append(entity)
    return entities


def extract_characters(booknlp_data: dict) -> list:
    """Extract character information from BookNLP output.

    Returns list of character dicts with:
        normalized_name, inferred_gender, inferred_age_category, voice, language
    """
    # If characters_simple already exists from BookNLP, use that
    if "characters_simple" in booknlp_data:
        return booknlp_data["characters_simple"].get("characters", [])

    # Otherwise, extract from book_data
    characters = []

    # Always add narrator first
    characters.append(
        {
            "normalized_name": "Narrator",
            "inferred_gender": "unknown",
            "inferred_age_category": "unknown",
            "tts_engine": "XTTSv2",
            "language": "eng",
            "voice": None,
        }
    )

    if "book_data" not in booknlp_data:
        return characters

    book_data = booknlp_data["book_data"]
    char_data = book_data.get("characters", [])

    for char in char_data:
        gender = _infer_gender(char)
        age = _infer_age(char)
        proper_names = char.get("names", {}).get("proper", [])
        raw_name = proper_names[0] if proper_names else f"Character{char.get('id', 0)}"
        name = _normalize_name(raw_name)

        characters.append(
            {
                "normalized_name": name,
                "inferred_gender": gender,
                "inferred_age_category": age,
                "tts_engine": "XTTSv2",
                "language": "eng",
                "voice": None,
            }
        )

    return characters


def _infer_gender(char: dict) -> str:
    """Infer gender from character data."""
    gender_data = char.get("g", None)
    if gender_data is None:
        return "unknown"

    if isinstance(gender_data, dict):
        he_count = gender_data.get("he/him/his", 0)
        she_count = gender_data.get("she/her", 0)
        they_count = gender_data.get("they/them/their", 0)

        if he_count > she_count and he_count > they_count:
            return "male"
        elif she_count > he_count and she_count > they_count:
            return "female"
        else:
            return "unknown"
    elif isinstance(gender_data, str):
        if gender_data in ("he/him/his", "male"):
            return "male"
        elif gender_data in ("she/her", "female"):
            return "female"

    return "unknown"


def _infer_age(char: dict) -> str:
    """Infer age category from character data."""
    # Check if age was already inferred
    if "inferred_age_category" in char:
        return char["inferred_age_category"]

    # Look at modifiers and actions for age clues
    modifiers = char.get("modifiers", [])
    mod_text = " ".join(str(m) for m in modifiers).lower() if modifiers else ""

    child_words = {"child", "boy", "girl", "baby", "infant", "toddler", "kid", "little", "young"}
    teen_words = {"teen", "teenager", "adolescent", "youth", "teenage"}
    elder_words = {"old", "elderly", "aged", "ancient", "grandfather", "grandmother", "grandpa", "grandma"}

    for word in child_words:
        if word in mod_text:
            return "child"
    for word in teen_words:
        if word in mod_text:
            return "teen"
    for word in elder_words:
        if word in mod_text:
            return "elder"

    return "adult"


def _normalize_name(name: str) -> str:
    """Normalize a character name to CamelCase."""
    # Remove special characters
    name = re.sub(r"[^a-zA-Z0-9\s]", "", name)
    # Convert to CamelCase
    parts = name.strip().split()
    return "".join(word.capitalize() for word in parts) if parts else "Unknown"
