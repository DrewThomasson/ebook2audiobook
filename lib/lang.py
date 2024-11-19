import os

language_mapping = {
    "ar": {"name": "Arabic", "native_name": "العربية", "char_limit": 166, "model": "ar_core_news_sm", "iso3": "ara", "punctuation": [".", "،", "؛", ":"]},
    "cs": {"name": "Czech", "native_name": "Čeština", "char_limit": 186, "model": "cs_core_news_sm", "iso3": "ces", "punctuation": [".", ",", ":", ";"]},
    "de": {"name": "German", "native_name": "Deutsch", "char_limit": 253, "model": "de_core_news_sm", "iso3": "deu", "punctuation": [".", ",", ":", ";"]},
    "en": {"name": "English", "native_name": "English", "char_limit": 250, "model": "en_core_web_sm", "iso3": "eng", "punctuation": [".", ",", ":", ";"]},
    "es": {"name": "Spanish", "native_name": "Español", "char_limit": 239, "model": "es_core_news_md", "iso3": "spa", "punctuation": [".", ",", ":", ";"]},
    "fr": {"name": "French", "native_name": "Français", "char_limit": 273, "model": "fr_core_news_sm", "iso3": "fra", "punctuation": [".", ",", ":", ";"]},
    "hi": {"name": "Hindi", "native_name": "हिंदी", "char_limit": 220, "model": "hi_core_news_sm", "iso3": "hin", "punctuation": [".", ",", ":", ";"]},
    "hu": {"name": "Hungarian", "native_name": "Magyar", "char_limit": 210, "model": "custom_hu_model", "iso3": "hun", "punctuation": [".", ",", ":", ";"]},
    "it": {"name": "Italian", "native_name": "Italiano", "char_limit": 213, "model": "it_core_news_sm", "iso3": "ita", "punctuation": [".", ",", ":", ";"]},
    "ja": {"name": "Japanese", "native_name": "日本語", "char_limit": 71, "model": "ja_core_news_sm", "iso3": "jpn", "punctuation": ["。", "、", "："]},
    "ko": {"name": "Korean", "native_name": "한국어", "char_limit": 95, "model": "ko_core_news_sm", "iso3": "kor", "punctuation": [".", ",", ":", ";"]},
    "nl": {"name": "Dutch", "native_name": "Nederlands", "char_limit": 251, "model": "nl_core_news_sm", "iso3": "nld", "punctuation": [".", ",", ":", ";"]},
    "pl": {"name": "Polish", "native_name": "Polski", "char_limit": 224, "model": "pl_core_news_sm", "iso3": "pol", "punctuation": [".", ",", ":", ";"]},
    "pt": {"name": "Portuguese", "native_name": "Português", "char_limit": 203, "model": "pt_core_news_sm", "iso3": "por", "punctuation": [".", ",", ":", ";"]},
    "ru": {"name": "Russian", "native_name": "Русский", "char_limit": 182, "model": "ru_core_news_sm", "iso3": "rus", "punctuation": [".", ",", ":", ";"]},
    "tr": {"name": "Turkish", "native_name": "Türkçe", "char_limit": 200, "model": "tr_core_news_sm", "iso3": "tur", "punctuation": [".", ",", ":", ";"]},
    "zh": {"name": "Chinese", "native_name": "中文", "char_limit": 82, "model": "zh_core_web_sm", "iso3": "zho", "punctuation": ["。", "，", "：", "；"]}
}


default_language_code = "en"
default_target_voice_file = os.path.abspath(os.path.join(".","voices","adult","female",default_language_code,"default_voice.wav"))