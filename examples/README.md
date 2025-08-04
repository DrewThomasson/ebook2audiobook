# Multi-Character Voice Examples

This directory contains example files demonstrating how to use the multi-character voice support feature in ebook2audiobook.

## Files

### sample_script.txt
A basic fantasy story with three characters:
- **Elena**: Young princess (female, adult)
- **Merlin**: Wise wizard (male, elder) 
- **Narrator**: Story narrator (male, adult)

### sample_characters.json
Character definitions for the sample script using automatic voice selection.

### alice_characters.json
Example character definitions for an Alice in Wonderland adaptation, showing:
- Mix of automatic and specific voice assignments
- Different age categories (child, adult)
- Custom voice names for unique characters

## Usage Examples

### Basic Usage
```bash
# Linux/Mac
./ebook2audiobook.sh --headless \
  --script examples/sample_script.txt \
  --characters examples/sample_characters.json \
  --language eng

# Windows  
ebook2audiobook.cmd --headless \
  --script examples/sample_script.txt \
  --characters examples/sample_characters.json \
  --language eng
```

### With Custom Output
```bash
./ebook2audiobook.sh --headless \
  --script examples/sample_script.txt \
  --characters examples/sample_characters.json \
  --language eng \
  --output_format mp3 \
  --output_dir ./my_audiobooks
```

## Character JSON Template

Copy and modify this template for your own stories:

```json
[
  {
    "normalized_name": "CharacterName",
    "inferred_gender": "male|female|other", 
    "inferred_age_category": "child|adult|elder",
    "tts_engine": "XTTSv2",
    "language": "eng|spa|fra|etc",
    "voice": null,
    "description": "Optional character description"
  }
]
```

## Script Format

Tag character dialogue using this format:

```text
Untagged text is treated as narration.

<CharacterName>: This is character dialogue.

<AnotherCharacter>: This is another character speaking.

More narration can go here without tags.
```

## Voice Directory Structure

For automatic voice selection, organize voices like this:

```
voices/
├── eng/
│   ├── adult/
│   │   ├── male/
│   │   │   └── MaleVoice_24000.wav
│   │   └── female/
│   │       └── FemaleVoice_24000.wav
│   ├── child/
│   │   └── female/
│   │       └── ChildVoice_24000.wav
│   └── elder/
│       └── male/
│           └── ElderVoice_24000.wav
└── spa/
    └── adult/
        └── female/
            └── SpanishVoice_24000.wav
```

## Tips

1. **Character Names**: Make sure character names in your script exactly match the `normalized_name` in your JSON file.

2. **Voice Selection**: Use `"voice": null` for automatic selection, or specify a voice name for custom assignment.

3. **Testing**: Start with a short script to test your character-voice mappings before processing longer content.

4. **Narrator Voice**: Use the `--voice` parameter to set a default voice for untagged text and fallbacks.

5. **Quality**: Prefer voice files with `_24000.wav` suffix for best quality.

## Troubleshooting

- **"Character not found"**: Check that character names match between script and JSON
- **"Voice not found"**: Verify voice files exist in expected directories
- **"Missing required field"**: Ensure all required JSON fields are present
- **Poor quality**: Use higher sample rate voice files (24kHz recommended)