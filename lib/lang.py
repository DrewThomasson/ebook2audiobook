import os

language_mapping = {
    "ar": {"name": "Arabic", "native_name": "العربية", "char_limit": 166, "model": "ar_core_news_sm"},
    "cs": {"name": "Czech", "native_name": "Čeština", "char_limit": 186, "model": "cs_core_news_sm"},
    "da": {"name": "Danish", "native_name": "Dansk", "char_limit": 220, "model": "da_core_news_sm"},
    "de": {"name": "German", "native_name": "Deutsch", "char_limit": 253, "model": "de_core_news_sm"},
    "el": {"name": "Greek", "native_name": "Ελληνικά", "char_limit": 200, "model": "el_core_news_sm"},
    "en": {"name": "English", "native_name": "English", "char_limit": 250, "model": "en_core_web_sm"},
    "es": {"name": "Spanish", "native_name": "Español", "char_limit": 239, "model": "es_core_news_md"},
    "fa": {"name": "Persian", "native_name": "فارسی", "char_limit": 150, "model": "???"},
    "fi": {"name": "Finnish", "native_name": "Suomi", "char_limit": 230, "model": "fi_core_news_sm"},
    "fr": {"name": "French", "native_name": "Français", "char_limit": 273, "model": "fr_core_news_sm"},
    "hi": {"name": "Hindi", "native_name": "हिंदी", "char_limit": 220, "model": "???"},
    "hr": {"name": "Croatian", "native_name": "Hrvatski", "char_limit": 210, "model": "hr_core_news_sm"},
    "it": {"name": "Italian", "native_name": "Italiano", "char_limit": 213, "model": "it_core_news_sm"},
    "ja": {"name": "Japanese", "native_name": "日本語", "char_limit": 71, "model": "ja_core_news_sm"},
    "ko": {"name": "Korean", "native_name": "한국어", "char_limit": 95, "model": "ko_core_news_sm"},
    "nb": {"name": "Norwegian", "native_name": "Norsk Bokmål", "char_limit": 225, "model": "nb_core_news_sm"},
    "nl": {"name": "Dutch", "native_name": "Nederlands", "char_limit": 251, "model": "nl_core_news_sm"},
    "pl": {"name": "Polish", "native_name": "Polski", "char_limit": 224, "model": "pl_core_news_sm"},
    "pt": {"name": "Portuguese", "native_name": "Português", "char_limit": 203, "model": "pt_core_news_sm"},
    "ro": {"name": "Romanian", "native_name": "Română", "char_limit": 190, "model": "ro_core_news_sm"},
    "ru": {"name": "Russian", "native_name": "Русский", "char_limit": 182, "model": "ru_core_news_sm"},
    "sl": {"name": "Slovenian", "native_name": "Slovenščina", "char_limit": 210, "model": "sl_core_news_sm"},
    "sv": {"name": "Swedish", "native_name": "Svenska", "char_limit": 215, "model": "sv_core_news_sm"},
    "tr": {"name": "Turkish", "native_name": "Türkçe", "char_limit": 200, "model": "???"},
    "vi": {"name": "Vietnamese", "native_name": "Tiếng Việt", "char_limit": 180, "model": "???"},
    "yo": {"name": "Yoruba", "native_name": "Yorùbá", "char_limit": 180, "model": "???"},
    "zh": {"name": "Chinese", "native_name": "中文", "char_limit": 82, "model": "zh_core_web_sm"}
}

default_language_code = "en"
default_target_voice_file = os.path.abspath(os.path.join(".","voices","adult","female",default_language_code,"default_voice.wav"))