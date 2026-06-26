"""SML output generator - converts BookNLP output to SML format for ebook2audiobook."""

import json
import os
import re


def generate_sml_output(
    booknlp_data: dict,
    characters: list,
    output_path: str,
    voice_assignments: dict | None = None,
    use_macros: bool = True,
) -> str:
    """Generate SML-formatted text from BookNLP token-level and quote data.

    Uses the .tokens and .quotes files directly (token-level granularity)
    instead of the sentence-level .book.txt, so that dialog and narration
    are properly separated at exact quote boundaries.

    Falls back to the sentence-level .book.txt approach if token/quote data
    is not available.

    Args:
        booknlp_data: Dict returned by load_booknlp_output() containing
            tokens, quotes, book_data, and optionally book_txt.
        characters: List of character dicts with voice assignments.
        output_path: Path to write the SML output file.
        voice_assignments: Optional dict mapping character names to voice file paths.
        use_macros: If True, voice tags use character names as macro references
            instead of raw file paths. Defaults to True (macro-based output is
            the recommended mode for use with ebook2audiobook).

    Returns:
        Path to the generated SML file.
    """
    char_voice_map = _build_voice_map(characters, voice_assignments)

    tokens = booknlp_data.get("tokens")
    quotes = booknlp_data.get("quotes")
    book_data = booknlp_data.get("book_data")

    if tokens and quotes is not None:
        sml_content = _generate_from_tokens(
            tokens, quotes, book_data, char_voice_map, use_macros=use_macros
        )
    elif "book_txt" in booknlp_data:
        sml_content = _generate_from_book_txt(
            booknlp_data["book_txt"], char_voice_map, use_macros=use_macros
        )
    else:
        raise ValueError(
            "No token/quote data or book.txt found in BookNLP output."
        )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sml_content)

    return output_path


def _generate_from_tokens(
    tokens: list,
    quotes: list,
    book_data: dict | None,
    char_voice_map: dict,
    use_macros: bool = True,
) -> str:
    """Build SML using token-level quote boundaries.

    This gives exact narrator/character voice switches at quote boundaries
    instead of the sentence-level approximation from .book.txt.
    """
    # Build coref_id -> normalized character name mapping
    coref_to_name = _build_coref_name_map(book_data)

    # Build a set of (token_id -> speaker_name) from quotes data
    token_speaker = {}
    for q in quotes:
        try:
            q_start = int(q.get("quote_start", -1))
            q_end = int(q.get("quote_end", -1))
        except (ValueError, TypeError):
            continue

        char_id = q.get("char_id")
        if char_id is None or char_id == "None" or char_id == "":
            speaker_name = "Narrator"
        else:
            try:
                char_id = int(char_id)
            except (ValueError, TypeError):
                char_id = str(char_id)
            speaker_name = coref_to_name.get(char_id, coref_to_name.get(str(char_id), "Narrator"))

        for tid in range(q_start, q_end + 1):
            token_speaker[tid] = speaker_name

    # Walk through tokens and build segments of consecutive same-speaker text
    segments = []
    current_speaker = None
    current_words = []
    current_para = None

    for tok in tokens:
        try:
            tid = int(tok.get("token_ID_within_document", -1))
        except (ValueError, TypeError):
            continue

        word = tok.get("word", "")
        para_id = tok.get("paragraph_ID")

        speaker = token_speaker.get(tid, "Narrator")

        # Paragraph break → flush current segment and insert blank line
        if current_para is not None and para_id != current_para and current_words:
            segments.append((current_speaker, _join_tokens(current_words)))
            current_words = []
            current_speaker = None
            segments.append((None, ""))  # paragraph break marker

        # Speaker change → flush segment
        if speaker != current_speaker and current_words:
            segments.append((current_speaker, _join_tokens(current_words)))
            current_words = []

        current_speaker = speaker
        current_words.append(word)
        current_para = para_id

    # Flush remaining
    if current_words:
        segments.append((current_speaker, _join_tokens(current_words)))

    # Build SML output with voice tags
    sml_lines = []
    active_voice_tag = None

    for speaker, text in segments:
        if speaker is None:
            # Paragraph break
            sml_lines.append("")
            continue

        text = clean_tts_text(text)
        if not text:
            continue

        voice_path = char_voice_map.get(speaker)
        voice_tag_val = speaker if use_macros else voice_path

        if voice_tag_val and voice_tag_val != active_voice_tag:
            if active_voice_tag is not None:
                sml_lines.append("[/voice]")
            sml_lines.append(f"[voice:{voice_tag_val}]")
            active_voice_tag = voice_tag_val
        elif not voice_tag_val and active_voice_tag is not None:
            # No voice for this speaker but we have an open tag — keep it
            pass

        sml_lines.append(text)

    if active_voice_tag is not None:
        sml_lines.append("[/voice]")

    return "\n".join(sml_lines)


def _generate_from_book_txt(book_txt_content: str, char_voice_map: dict, use_macros: bool = True) -> str:
    """Fallback: generate SML from sentence-level .book.txt."""
    lines = book_txt_content.strip().split("\n")
    sml_lines = []
    current_voice = None

    for line in lines:
        line = line.strip()
        if not line:
            sml_lines.append("")
            continue

        match = re.match(r"^\[([^\]]+)\]\s*(.*?)\s*\[/\]$", line)
        if match:
            char_name = match.group(1)
            text = clean_tts_text(match.group(2).strip())
            if not text:
                continue

            voice_path = char_voice_map.get(char_name)
            voice_tag_val = char_name if use_macros else voice_path
            if voice_tag_val and voice_tag_val != current_voice:
                if current_voice is not None:
                    sml_lines.append("[/voice]")
                sml_lines.append(f"[voice:{voice_tag_val}]")
                current_voice = voice_tag_val

            sml_lines.append(text)
        else:
            sml_lines.append(line)

    if current_voice is not None:
        sml_lines.append("[/voice]")

    return "\n".join(sml_lines)


def _build_coref_name_map(book_data: dict | None) -> dict:
    """Build mapping from coref cluster ID to normalized character name.

    Uses the .book JSON which contains character IDs and their proper-name
    mentions (the same data used by BookNLP to generate book.txt).
    """
    name_map = {}
    if not book_data:
        return name_map

    for character in book_data.get("characters", []):
        char_id = character.get("id")
        if char_id is None:
            continue

        mentions = character.get("mentions", {})
        proper = mentions.get("proper", [])
        common = mentions.get("common", [])

        # Pick the most common proper name, falling back to common noun
        canonical = None
        if proper:
            canonical = proper[0].get("n", "")
        elif common:
            canonical = common[0].get("n", "")

        if canonical:
            normalized = _normalize_name(canonical.title())
        else:
            normalized = f"Character{char_id}"

        name_map[char_id] = normalized
        name_map[str(char_id)] = normalized

    # Narrator is a special case (coref_id=0 is often the first-person narrator)
    if 0 not in name_map:
        name_map[0] = "Narrator"
        name_map["0"] = "Narrator"

    return name_map


def _normalize_name(name: str) -> str:
    """Normalize a name to CamelCase (matching core.py's normalization)."""
    name = re.sub(r"[^a-zA-Z0-9\s]", "", name)
    parts = name.strip().split()
    return "".join(word.capitalize() for word in parts) if parts else "Unknown"


def clean_tts_text(text: str) -> str:
    """Remove non-standard characters that may cause issues with TTS engines.

    Keeps alphanumeric characters (including accented letters via \\w), spaces,
    and standard punctuation. Specifically retains:
    - ASCII and Unicode word characters (letters, digits, underscore)
    - Whitespace
    - Common punctuation: . , ! ? ; : " ' ( ) [ ] { } - — – and curly quotes " " ' '
    """
    if not text:
        return ""

    # Replace non-breaking space with normal space
    text = text.replace('\u00A0', ' ')
    # Retain word chars, whitespace, and the explicitly listed punctuation variants
    # (both ASCII and Unicode curly/typographic equivalents)
    text = re.sub(r'[^\w\s\.,!\?;:\"\'\u2018\u2019()\[\]\{\}\-\u2014\u2013\u201C\u201D]', '', text)
    # Collapse multiple spaces into one
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def _join_tokens(words: list) -> str:
    """Join tokens into readable text with proper punctuation, contraction, and dialect spacing."""
    if not words:
        return ""

    text = " ".join(words)

    # 1. Fix "n't" contractions with both straight and curly apostrophes
    text = re.sub(r"\b(\w+)\s+(n['’]t)\b", r"\1\2", text, flags=re.IGNORECASE)

    # 2. Fix standard contractions with both straight and curly apostrophes
    text = re.sub(r"\b(\w+)\s+(['’](?:s|re|ve|ll|d|m|t))\b", r"\1\2", text, flags=re.IGNORECASE)

    # 3. Fix dropped 'g' dialect (e.g., "swarmin ’" -> "swarmin'")
    text = re.sub(r"\b(\w+in)\s+(['’])(?!\w)", r"\1\2", text, flags=re.IGNORECASE)

    # 4. Fix spacing around punctuation (UPDATED FOR CURLY QUOTES)
    # Removes space BEFORE closing punctuation, including curly closing quotes/apostrophes
    text = re.sub(r"\s+([,.!?;:\"')\]}’”])", r"\1", text)
    # Removes space AFTER opening punctuation, including curly opening quotes
    text = re.sub(r"([(\[{“‘])\s+", r"\1", text)

    # 5. Fix double spaces and cleanup
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()


def generate_characters_json(
    characters: list,
    output_path: str,
    voice_assignments: dict | None = None,
) -> str:
    """Generate characters_simple.json with voice assignments.

    Args:
        characters: List of character dicts.
        output_path: Path to write the JSON file.
        voice_assignments: Optional dict mapping character names to voice paths.

    Returns:
        Path to the generated JSON file.
    """
    if voice_assignments:
        for char in characters:
            name = char.get("normalized_name", "")
            if name in voice_assignments:
                char["voice"] = voice_assignments[name]

    result = {"characters": characters}

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return output_path


def generate_sml_macros(
    characters: list,
    output_path: str,
    voice_assignments: dict | None = None,
) -> str:
    """Generate the macro JSON file mapping character names to voice paths.

    Args:
        characters: List of character dicts.
        output_path: Path to write the JSON file.
        voice_assignments: Optional dict mapping character names to voice paths.

    Returns:
        Path to the generated JSON file.
    """
    voice_map = _build_voice_map(characters, voice_assignments)

    macros_data = {
        "macros": {
            "voices": voice_map
        }
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(macros_data, f, indent=4, ensure_ascii=False)

    return output_path


def _build_voice_map(
    characters: list, voice_assignments: dict | None = None
) -> dict:
    """Build a mapping of character names to voice file paths.

    Args:
        characters: List of character dicts with potential voice fields.
        voice_assignments: Optional override dict mapping names to voice paths.

    Returns:
        Dict mapping character normalized_name to voice file path.
    """
    voice_map = {}

    # First, collect from character data
    for char in characters:
        name = char.get("normalized_name", "")
        voice = char.get("voice")
        if name and voice:
            voice_map[name] = voice

    # Override with explicit assignments
    if voice_assignments:
        voice_map.update(voice_assignments)

    return voice_map
