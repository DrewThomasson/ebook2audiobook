import os

language_options = [
    "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko"
]
char_limits = {
    "en": 250,      # English
    "es": 239,      # Spanish
    "fr": 273,      # French
    "de": 253,      # German
    "it": 213,      # Italian
    "pt": 203,      # Portuguese
    "pl": 224,      # Polish
    "tr": 226,      # Turkish
    "ru": 182,      # Russian
    "nl": 251,      # Dutch
    "cs": 186,      # Czech
    "ar": 166,      # Arabic
    "zh-cn": 82,    # Chinese (Simplified)
    "ja": 71,       # Japanese
    "hu": 224,      # Hungarian
    "ko": 95,       # Korean
}

# Mapping of language codes to NLTK's supported language names
language_mapping = {
    "en": "english",
    "de": "german",
    "fr": "french",
    "es": "spanish",
    "it": "italian",
    "pt": "portuguese",
    "nl": "dutch",
    "pl": "polish",  
    "cs": "czech",   
    "ru": "russian",
    "tr": "turkish",
    "el": "greek",
    "et": "estonian",
    "no": "norwegian",
    "ml": "malayalam",
    "sl": "slovene",
    "da": "danish",
    "fi": "finnish",
    "sv": "swedish"
}

default_language_code = "en"
default_target_voice_file = os.path.abspath(os.path.join(".","voices","adult","female",default_language_code,"default_voice.wav"))