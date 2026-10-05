import os, locale, importlib
from contextvars import ContextVar
legends_langs = ['ara', 'ben', 'zho', 'eng', 'fra', 'deu', 'hin', 'hun', 'ind', 'ita', 'jav', 'jpn', 'kor', 'fas', 'pol', 'por', 'rus', 'spa', 'tam', 'tel', 'tur', 'yor']
legends_iso1 = {'ar': 'ara', 'bn': 'ben', 'zh': 'zho', 'en': 'eng', 'fr': 'fra', 'de': 'deu', 'hi': 'hin', 'hu': 'hun', 'id': 'ind', 'it': 'ita', 'jv': 'jav', 'ja': 'jpn', 'ko': 'kor', 'fa': 'fas', 'pl': 'pol', 'pt': 'por', 'ru': 'rus', 'es': 'spa', 'ta': 'tam', 'te': 'tel', 'tr': 'tur', 'yo': 'yor'}
legends_all = {lang: importlib.import_module(f'lib.lang.legends_{lang}').legends for lang in legends_langs}
system_language = os.environ.get('ISO3_LANG', '').strip().lower()
if system_language not in legends_all:
    system_locale = os.environ.get('LC_ALL') or os.environ.get('LC_MESSAGES') or os.environ.get('LANG') or ''
    if not system_locale and os.name == 'nt':
        try:
            import ctypes
            system_locale = locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(), '')
        except Exception:
            system_locale = ''
    if not system_locale:
        try:
            system_locale = locale.getlocale()[0] or ''
        except Exception:
            system_locale = ''
    system_language = legends_iso1.get(system_locale.replace('-', '_').split('_')[0].split('.')[0].lower(), 'eng')
ui_language = ContextVar('ui_language', default=system_language)
class Legends(dict):
    def __getitem__(self, key:str)->str:
        table = legends_all.get(ui_language.get(), legends_all['eng'])
        return table[key] if key in table else legends_all['eng'].get(key, key)
legends = Legends(legends_all['eng'])
