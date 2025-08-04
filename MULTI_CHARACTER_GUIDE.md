# Multi-Character Voice Support Documentation

## Overview

The multi-character voice support feature allows E2A (ebook2audiobook) to automatically assign different voices to different characters in a story based on their categorization (age, gender, language). This feature works with pre-tagged text scripts and character JSON files.

## Input Files

### 1. Pre-tagged Text Script

A `.txt` file where character names are tagged in the format `<CharacterName>: dialogue text`.

**Example:**
```text
Welcome to our story. This is the narrator speaking.

<Alice>: Hello everyone! I'm so excited to be here today.

<Bob>: Nice to meet you, Alice. I'm Bob, and I'm equally thrilled.

The two characters continued their conversation as the day went on.

<Alice>: I wonder what adventures await us in this new chapter of our lives.

<Bob>: Whatever comes our way, I'm sure we'll handle it together.

And so their friendship began, with promises of many more conversations to come.
```

**Rules:**
- Character dialogue must be tagged as `<CharacterName>: dialogue text`
- Untagged text is treated as narrator/descriptive text
- Empty lines are preserved for pacing
- Character names should match those defined in the character JSON file

### 2. Character JSON File

A JSON file containing character definitions with voice categorization metadata.

**Example:**
```json
[
  {
    "normalized_name": "Alice",
    "inferred_gender": "female", 
    "inferred_age_category": "adult",
    "tts_engine": "XTTSv2",
    "language": "eng",
    "voice": null
  },
  {
    "normalized_name": "Bob",
    "inferred_gender": "male", 
    "inferred_age_category": "adult",
    "tts_engine": "XTTSv2",
    "language": "eng",
    "voice": "SpecificVoiceName"
  }
]
```

**Required Fields:**
- `normalized_name`: Character name (must match tags in script)
- `inferred_gender`: "male", "female", or other gender identifiers
- `inferred_age_category`: "adult", "child", "elder", etc.
- `language`: Language code (e.g., "eng", "spa", "fra")

**Optional Fields:**
- `voice`: Specific voice name to use, or `null` for automatic selection
- `tts_engine`: TTS engine preference (defaults to system default)

## Voice Assignment Logic

### Automatic Voice Selection (when `"voice": null`)

The system automatically selects voices based on the existing voice folder structure:
```
voices_dir/{language}/{age_category}/{gender}/VoiceName_24000.wav
```

**Examples:**
- `voices/eng/adult/male/` - Adult male English voices
- `voices/eng/adult/female/` - Adult female English voices  
- `voices/eng/elder/female/` - Elder female English voices
- `voices/spa/child/male/` - Child male Spanish voices

The system prefers `_24000.wav` files and falls back to any `.wav` file in the appropriate category folder.

### Specific Voice Selection (when `"voice": "VoiceName"`)

When a specific voice is provided, the system searches for voice files matching that name across the voice directory structure.

**Search Pattern:**
1. Look for `VoiceName_24000.wav` anywhere in the voices directory
2. Fall back to `VoiceName.wav` if the above is not found
3. If not found, fall back to automatic selection

## Command Line Usage

### Basic Usage

```bash
# Linux/Mac
./ebook2audiobook.sh --headless --script path/to/script.txt --characters path/to/characters.json --language eng

# Windows
ebook2audiobook.cmd --headless --script path/to/script.txt --characters path/to/characters.json --language eng
```

### Required Arguments

- `--headless`: Run in headless mode
- `--script`: Path to pre-tagged text script file
- `--characters`: Path to character JSON file
- `--language`: Language code for the audiobook

### Optional Arguments

All existing E2A optional arguments work with multi-character mode:

- `--voice`: Default voice for narrator and untagged text
- `--device`: Processing device (cpu, gpu, mps)
- `--tts_engine`: TTS engine to use
- `--output_format`: Audio output format
- `--output_dir`: Output directory for audiobooks
- `--temperature`, `--speed`, etc.: TTS engine specific parameters

### Examples

**Basic conversion:**
```bash
./ebook2audiobook.sh --headless \
  --script my_story.txt \
  --characters my_characters.json \
  --language eng
```

**With custom output settings:**
```bash
./ebook2audiobook.sh --headless \
  --script my_story.txt \
  --characters my_characters.json \
  --language eng \
  --output_format mp3 \
  --output_dir ./my_audiobooks \
  --device gpu
```

**With custom narrator voice:**
```bash
./ebook2audiobook.sh --headless \
  --script my_story.txt \
  --characters my_characters.json \
  --language eng \
  --voice ./my_narrator_voice.wav
```

## Fallback Behavior

The system includes comprehensive fallback handling:

1. **Character not found in JSON**: Uses default voice
2. **Specific voice file doesn't exist**: Falls back to category-based selection
3. **Category folder doesn't exist**: Uses system default voice
4. **No suitable voice found**: Uses the configured default voice

## Integration with Existing Features

### Compatibility

- ✅ Compatible with all existing TTS engines (XTTSv2, BARK, VITS, etc.)
- ✅ Works with existing voice folder structure
- ✅ Supports all existing output formats
- ✅ Maintains session and resumption capabilities
- ✅ Preserves existing SML (Speech Markup Language) support

### Existing `--voice` Parameter

The `--voice` parameter continues to work and serves as:
- Default voice for narrator/untagged text
- Fallback voice when character-specific voices aren't found
- Override for all voices when no character JSON is used

## File Validation

The system validates input files and provides clear error messages:

### Character JSON Validation
- Checks for required fields
- Validates JSON syntax
- Provides specific error messages for missing or invalid data

### Script File Validation
- Ensures file exists and is readable
- Parses character tags correctly
- Handles various text encoding formats

### Voice File Validation
- Checks if referenced voice files exist
- Validates voice directory structure
- Provides warnings for missing voices with fallback information

## Output

The system generates audiobooks with:
- Multiple character voices based on the character JSON configuration
- Seamless voice transitions between characters
- Existing chapter/sentence structure preservation
- All existing audio quality and processing features
- Support for all existing output formats (M4B, MP3, etc.)

## Troubleshooting

### Common Issues

**"Character missing required field" error:**
- Ensure all characters in the JSON have the required fields: `normalized_name`, `inferred_gender`, `inferred_age_category`, `language`

**"No voice found for character" warnings:**
- Check that the voice directory structure matches the character metadata
- Ensure voice files exist in the expected locations
- Verify the `language`, `inferred_gender`, and `inferred_age_category` values are correct

**"Voice file not found" warnings:**
- Verify specific voice names in the character JSON match actual voice files
- Check voice file naming conventions (prefer `VoiceName_24000.wav`)

### Debug Information

The system provides detailed logging:
- Character-to-voice mapping results
- Voice selection decisions
- Fallback actions taken
- File validation results

Example output:
```
Mapped character 'Alice' to voice: TestFemaleVoice_24000.wav
Mapped character 'Bob' to voice: TestMaleVoice_24000.wav
Warning: No voice found for character 'Charlie', using default voice
Using character voice for 'Alice': TestFemaleVoice_24000.wav
```

## Best Practices

1. **Voice Organization**: Organize voices in the standard directory structure for best automatic selection
2. **Character Naming**: Use consistent character names between script tags and JSON file
3. **Voice Quality**: Use high-quality voice files (prefer 24kHz samples)
4. **Testing**: Test with a small script first to verify character-voice mappings
5. **Backup**: Keep backup copies of your script and character files
6. **Documentation**: Document your character voice choices for consistency across projects

## Advanced Usage

### Custom Voice Directories

While the system uses the standard `voices/` directory structure, you can reference voices from anywhere by providing full paths in the character JSON.

### Multi-Language Support

Different characters can use different languages by setting the `language` field in the character JSON. This allows for multi-lingual audiobooks with appropriate voice selection per language.

### Voice Cloning Integration

The system works with voice cloning by:
1. Placing cloned voice files in the appropriate category directories
2. Referencing specific cloned voices by name in the character JSON
3. Using the existing voice cloning workflow with the `--voice` parameter for narrator

## Migration from Single Voice

To migrate existing single-voice workflows:
1. Create a character JSON file for your story
2. Tag character dialogue in your text
3. Use your existing voice as the default `--voice` parameter
4. Gradually add character-specific voices as desired

The system maintains full backward compatibility with existing single-voice workflows.