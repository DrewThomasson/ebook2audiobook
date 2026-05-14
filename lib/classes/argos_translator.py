import os,  threading, stanza, unicodedata, pykakasi, regex as re
import argostranslate.package,  argostranslate.translate

from unidecode import unidecode
from phonemizer import phonemize
from pypinyin import pinyin, Style

from iso639 import Lang
from lib.conf_lang import language_mapping

# NOTE: argostranslate API requires iso639-1 (2 letters) codes.
# All public methods here accept/return iso639-3 except where explicitly named *_iso1.

class ArgosTranslator:

    _index_lock = threading.Lock()
    _index_updated:bool = False
    _install_lock = threading.Lock()

    def __init__(self, neural_machine:str="argostranslate"):
        self.neural_machine = neural_machine
        self.translation = None
        self.source_lang_iso1 = None
        self.target_lang_iso1 = None
        self._kakasi = None

    @classmethod
    def ensure_index(cls)->None:
        with cls._index_lock:
            if not cls._index_updated:
                argostranslate.package.update_package_index()
                cls._index_updated = True

    def get_language_iso3(self, lang_iso1:str)->str:
        try:
            ld = Lang(lang_iso1)
            if ld:
                return ld.pt3
        except Exception:
            pass
        return lang_iso1

    def get_language_iso1(self, lang_iso3:str)->str|None:
        try:
            ld = Lang(lang_iso3)
            if ld:
                return ld.pt1 or None
        except Exception:
            pass
        return None

    def get_all_sources_iso1(self)->list[str]:
        self.ensure_index()
        pkgs = argostranslate.package.get_available_packages()
        return sorted(set(p.from_code for p in pkgs))

    def get_target_options(self, source_iso3:str)->list[tuple[str, str]]:
        source_iso1 = self.get_language_iso1(source_iso3)
        if not source_iso1:
            return []
        self.ensure_index()
        pkgs = argostranslate.package.get_available_packages()
        direct = set(p.to_code for p in pkgs if p.from_code == source_iso1)
        reachable = set(direct)
        if source_iso1=='en':
            pass
        elif 'en' in direct:
            en_targets = set(p.to_code for p in pkgs if p.from_code=='en')
            reachable|=en_targets
        reachable.discard(source_iso1)
        options:list=[]
        for iso1 in reachable:
            iso3 = self.get_language_iso3(iso1)
            if iso3 == source_iso3:
                continue
            if iso3 not in language_mapping:
                continue
            details = language_mapping[iso3]
            label = f"{details['name']} - {details['native_name']}" if details['name']!=details['native_name'] else details['name']
            options.append((label, iso3))
        options.sort(key=lambda o:o[0])
        return options

    def is_package_installed(self, source_iso1:str, target_iso1:str)->bool:
        try:
            installed = argostranslate.translate.get_installed_languages()
            src = next((l for l in installed if l.code == source_iso1),None)
            tgt = next((l for l in installed if l.code == target_iso1),None)
            return src is not None and tgt is not None
        except Exception as e:
            error = f'ArgosTranslator.is_package_installed() error: {e}'
            print(error)
            return False

    def is_pair_installed(self, from_iso1:str, to_iso1:str)->bool:
        try:
            for pkg in argostranslate.package.get_installed_packages():
                if pkg.from_code == from_iso1 and pkg.to_code == to_iso1:
                    return True
            return False
        except Exception:
            return False

    def download_and_install(self, source_iso1:str, target_iso1:str)->tuple[str|None, bool]:
        try:
            with self._install_lock:
                self.ensure_index()
                available = argostranslate.package.get_available_packages()
                # direct
                direct_pkg = next((p for p in available if p.from_code == source_iso1 and p.to_code == target_iso1),None)
                if direct_pkg is not None:
                    if not self.is_pair_installed(source_iso1, target_iso1):
                        msg = f'Downloading argos package {source_iso1} -> {target_iso1}...'
                        print(msg)
                        argostranslate.package.install_from_path(direct_pkg.download())
                        msg = f'Installed argos package {source_iso1} -> {target_iso1}'
                        print(msg)
                    return None, True
                # english-pivot
                if source_iso1!='en' and target_iso1!='en':
                    src_to_en = next((p for p in available if p.from_code == source_iso1 and p.to_code=='en'),None)
                    en_to_tgt = next((p for p in available if p.from_code=='en' and p.to_code == target_iso1),None)
                    if src_to_en is not None and en_to_tgt is not None:
                        msg = f"No direct {source_iso1}->{target_iso1}; using English pivot."
                        print(msg)
                        if not self.is_pair_installed(source_iso1,'en'):
                            msg = f"Downloading argos package {source_iso1} -> en..."
                            print(msg)
                            argostranslate.package.install_from_path(src_to_en.download())
                        if not self.is_pair_installed('en',target_iso1):
                            msg = f'Downloading argos package en -> {target_iso1}...'
                            print(msg)
                            argostranslate.package.install_from_path(en_to_tgt.download())
                        msg = f'English pivot ready: {source_iso1} -> en -> {target_iso1}'
                        print(msg)
                        return None, True
                error = f'No argos package available for {source_iso1} -> {target_iso1} (direct or English-pivoted)'
                return error, False
        except Exception as e:
            error = f'ArgosTranslator.download_and_install() error: {e}'
            return error, False

    def start(self, source_iso1:str, target_iso1:str)->tuple[str|None, bool]:
        try:
            if self.neural_machine != "argostranslate":
                error = f'Neural machine {self.neural_machine} is not supported.'
                return error, False
            try:
                stanza.download(source_iso1, processors='tokenize,mwt')
            except Exception:
                pass
            error, ok = self.download_and_install(source_iso1, target_iso1)
            if not ok:
                return error, False
            installed = argostranslate.translate.get_installed_languages()
            src = next((l for l in installed if l.code == source_iso1), None)
            tgt = next((l for l in installed if l.code == target_iso1), None)
            if not src or not tgt:
                error = f'Translation languages not installed: {source_iso1} -> {target_iso1}'
                return error, False
            # get_translation() returns a PackageTranslation for direct pairs and a
            # CompositeTranslation when only a pivot path exists (via Bellman-Ford)
            self.translation = src.get_translation(tgt)
            if self.translation is None:
                error = f'No translation path available: {source_iso1} -> {target_iso1}'
                return error, False
            self.source_lang_iso1 = source_iso1
            self.target_lang_iso1 = target_iso1
            return None, True
        except Exception as e:
            error = f'ArgosTranslator.start() error: {e}'
            return error, False

    def process(self, text:str)->tuple[str, bool]:
        try:
            if not text or not text.strip():
                return text, True
            if self.translation is None:
                error = 'ArgosTranslator.process() error: not started'
                return error, False
            return self.translation.translate(text),True
        except Exception as e:
            error = f'ArgosTranslator.process() error: {e}'
            return error, False

    def romanize(self, token:str)->str:

        def _script_of(word:str)->str:
            for ch in word:
                if ch.isalpha():
                    name = unicodedata.name(ch, '')
                    if 'CYRILLIC' in name:
                        return 'cyrillic'
                    if 'LATIN' in name:
                        return 'latin'
                    if 'ARABIC' in name:
                        return 'arabic'
                    if 'HANGUL' in name:
                        return 'hangul'
                    if 'HIRAGANA' in name or 'KATAKANA' in name:
                        return 'japanese'
                    if 'CJK' in name or 'IDEOGRAPH' in name:
                        return 'chinese'
            return 'unknown'

        scr = _script_of(token)
        if scr == 'latin':
            return token
        try:
            if scr == 'chinese':
                return ''.join(x[0] for x in pinyin(token, style=Style.NORMAL))
            if scr == 'japanese':
                if self._kakasi is None:
                    self._kakasi = pykakasi.kakasi()
                    self._kakasi.setMode('H', 'a')
                    self._kakasi.setMode('K', 'a')
                    self._kakasi.setMode('J', 'a')
                    self._kakasi.setMode('r', 'Hepburn')
                return self._kakasi.getConverter().do(token)
            if scr == 'hangul':
                return unidecode(token)
            if scr == 'arabic':
                return unidecode(phonemize(token, language='ar', backend='espeak'))
            if scr == 'cyrillic':
                return unidecode(phonemize(token, language='ru', backend='espeak'))
            return unidecode(token)
        except Exception:
            return unidecode(token)

    def translate(self, text: str, sml_pattern: re.Pattern) -> tuple[str, bool]:
        try:
            if not text or not text.strip():
                return text, True
            protected: dict[str, str] = {}
            masked_text = text
            if sml_pattern:
                matches = list(sml_pattern.finditer(text))
                for i, m in enumerate(reversed(matches)):
                    match_index = len(matches) - 1 - i
                    key = f'SMLTAG{match_index}Z' 
                    protected[key] = m.group(0)
                    masked_text = masked_text[:m.start()] + key + masked_text[m.end():]
            translated_text, ok = self.process(masked_text)
            if not ok:
                return translated_text, False
            tokens: list[str] = re.findall(r"SMLTAG\d+Z|\w+|[^\w\s]", translated_text, re.UNICODE)
            buf: list[str] = []
            for t in tokens:
                is_marker = False
                upper_t = t.upper()
                if upper_t in protected:
                    buf.append(upper_t) # Normalize to uppercase for replacement later
                    is_marker = True
                elif re.match(r"^\w+$", t):
                    buf.append(self.romanize(t)) 
                else:
                    buf.append(t)
            out: str = ''
            for i, t in enumerate(buf):
                if i == 0:
                    out += t
                else:
                    prev_is_word = re.match(r"^\w+$", buf[i - 1]) and buf[i-1] not in protected
                    curr_is_word = re.match(r"^\w+$", t) and t not in protected
                    if prev_is_word and curr_is_word:
                        out += ' ' + t
                    else:
                        out += t
            for key, original_sml in protected.items():
                pattern = re.compile(re.escape(key), re.IGNORECASE)
                out = pattern.sub(original_sml, out)
            return out, True
        except Exception as e:
            error = f'ArgosTranslator.translate() error: {e}'
            return error, False
