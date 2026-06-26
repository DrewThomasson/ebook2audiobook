"""Voice matcher for auto-assigning voices from ebook2audiobook voice library."""

import os
import random
from pathlib import Path


# Voice directory structure in ebook2audiobook:
# voices/{lang}/{age_category}/{gender}/{VoiceName}.wav
# e.g. voices/eng/adult/female/AlexandraHisakawa.wav

VOICE_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg"}
AGE_CATEGORIES = {"child", "teen", "adult", "elder"}
GENDERS = {"male", "female"}


def scan_voice_library(ebook2audiobook_path: str, language: str = "eng") -> dict:
    """Scan the ebook2audiobook voice library and return available voices.

    Args:
        ebook2audiobook_path: Path to the ebook2audiobook repository root.
        language: Language code (default: 'eng').

    Returns:
        Dict organized as:
        {
            "adult": {"male": [path1, ...], "female": [path1, ...]},
            "child": {"male": [...], "female": [...]},
            "teen": {"male": [...], "female": [...]},
            "elder": {"male": [...], "female": [...]},
        }
    """
    voices_dir = os.path.join(ebook2audiobook_path, "voices", language)
    library = {}

    if not os.path.isdir(voices_dir):
        return library

    for age_cat in AGE_CATEGORIES:
        age_dir = os.path.join(voices_dir, age_cat)
        if not os.path.isdir(age_dir):
            continue

        library[age_cat] = {}
        for gender in GENDERS:
            gender_dir = os.path.join(age_dir, gender)
            if not os.path.isdir(gender_dir):
                library[age_cat][gender] = []
                continue

            voices = []
            for f in sorted(os.listdir(gender_dir)):
                if Path(f).suffix.lower() in VOICE_EXTENSIONS:
                    voices.append(os.path.join("voices", language, age_cat, gender, f))
            library[age_cat][gender] = voices

    return library


def scan_custom_voices(voices_dir: str) -> list:
    """Scan a custom directory for voice files.

    Args:
        voices_dir: Path to directory containing voice files.

    Returns:
        List of absolute paths to voice files.
    """
    voices = []
    if not os.path.isdir(voices_dir):
        return voices

    for root, _dirs, files in os.walk(voices_dir):
        for f in sorted(files):
            if Path(f).suffix.lower() in VOICE_EXTENSIONS:
                voices.append(os.path.join(root, f))

    return voices


def auto_assign_voices(
    characters: list,
    voice_library: dict,
    custom_voices: list | None = None,
) -> dict:
    """Automatically assign voices to characters based on gender and age.

    Characters with known genders (male/female) are assigned first so they
    get matching voices.  Characters with unknown gender are assigned
    afterward, alternating between male and female pools to avoid exhausting
    one gender's voice supply.

    Args:
        characters: List of character dicts with inferred_gender and inferred_age_category.
        voice_library: Voice library from scan_voice_library().
        custom_voices: Optional list of custom voice file paths.

    Returns:
        Dict mapping character normalized_name to voice file path.
    """
    assignments = {}
    used_voices = set()

    # Split into known-gender vs unknown-gender characters, preserving order
    known_gender_chars = []
    unknown_gender_chars = []
    for char in characters:
        gender = char.get("inferred_gender", "unknown")
        if gender in GENDERS:
            known_gender_chars.append(char)
        else:
            unknown_gender_chars.append(char)

    # Assign known-gender characters first so they always get matching voices
    for char in known_gender_chars:
        name = char.get("normalized_name", "")
        gender = char.get("inferred_gender", "unknown")
        age = char.get("inferred_age_category", "adult")

        voice = _find_best_voice(
            gender, age, voice_library, used_voices, custom_voices
        )
        if voice:
            assignments[name] = voice
            used_voices.add(voice)

    # Assign unknown-gender characters, alternating male/female
    alternate_genders = ["female", "male"]
    for i, char in enumerate(unknown_gender_chars):
        name = char.get("normalized_name", "")
        age = char.get("inferred_age_category", "adult")
        gender = alternate_genders[i % 2]

        voice = _find_best_voice(
            gender, age, voice_library, used_voices, custom_voices
        )
        if voice:
            assignments[name] = voice
            used_voices.add(voice)

    return assignments


def _find_best_voice(
    gender: str,
    age: str,
    voice_library: dict,
    used_voices: set,
    custom_voices: list | None = None,
) -> str | None:
    """Find the best available voice for given gender and age.

    Priority:
    1. Exact age+gender match
    2. Same gender, different age (prefer adult)
    3. Any available voice
    """
    # Normalize inputs
    if gender not in GENDERS:
        gender = "female"  # Default
    if age not in AGE_CATEGORIES:
        age = "adult"

    # Strategy 1: Exact match
    voice = _pick_unused_voice(voice_library, age, gender, used_voices)
    if voice:
        return voice

    # Strategy 2: Same gender, different age (prefer adult > teen > elder > child)
    age_fallback = ["adult", "teen", "elder", "child"]
    for fallback_age in age_fallback:
        if fallback_age == age:
            continue
        voice = _pick_unused_voice(voice_library, fallback_age, gender, used_voices)
        if voice:
            return voice

    # Strategy 3: Any available voice
    other_gender = "male" if gender == "female" else "female"
    for fallback_age in age_fallback:
        voice = _pick_unused_voice(
            voice_library, fallback_age, other_gender, used_voices
        )
        if voice:
            return voice

    # Strategy 4: Try custom voices
    if custom_voices:
        for v in custom_voices:
            if v not in used_voices:
                return v

    return None


def _pick_unused_voice(
    voice_library: dict, age: str, gender: str, used_voices: set
) -> str | None:
    """Pick a random unused voice from the library for given age and gender."""
    if age not in voice_library:
        return None
    if gender not in voice_library.get(age, {}):
        return None

    available = [
        v for v in voice_library[age][gender] if v not in used_voices
    ]
    if not available:
        return None

    return random.choice(available)


def get_voice_display_name(voice_path: str) -> str:
    """Get a human-readable display name for a voice file."""
    return Path(voice_path).stem


def get_voice_category_info(voice_path: str) -> dict:
    """Extract category info from a voice path in ebook2audiobook structure.

    Returns dict with keys: name, age, gender, language
    """
    parts = Path(voice_path).parts
    name = Path(voice_path).stem

    info = {"name": name, "age": "unknown", "gender": "unknown", "language": "unknown"}

    # Try to detect from path structure: voices/{lang}/{age}/{gender}/{file}
    for i, part in enumerate(parts):
        if part in AGE_CATEGORIES:
            info["age"] = part
            if i > 0:
                info["language"] = parts[i - 1]
            if i + 1 < len(parts) - 1 and parts[i + 1] in GENDERS:
                info["gender"] = parts[i + 1]
            break

    return info
