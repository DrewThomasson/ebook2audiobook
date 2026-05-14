import os, time, threading, stanza, regex as re
import argostranslate.package, argostranslate.translate

from iso639 import Lang
from lib.conf_lang import language_mapping

# NOTE: argostranslate API requires iso639-1 (2 letters) codes.
# All public methods here accept/return iso639-3 except where explicitly named *_iso1.

class ArgosTranslator:

    _index_lock = threading.Lock()
    _index_updated:bool = False

    _pair_locks:dict[str, threading.Lock] = {}
    _pair_locks_guard = threading.Lock()

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

    @classmethod
    def get_pair_lock(cls, source_iso1:str, target_iso1:str)->threading.Lock:
        key = f'{source_iso1}->{target_iso1}'
        with cls._pair_locks_guard:
            lock = cls._pair_locks.get(key)
            if lock is None:
                lock = threading.Lock()
                cls._pair_locks[key] = lock
            return lock

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
        direct = set(
            p.to_code
            for p in pkgs
            if p.from_code == source_iso1
        )
        reachable = set(direct)
        if source_iso1!='en':
            if 'en' in direct:
                en_targets = set(
                    p.to_code
                    for p in pkgs
                    if p.from_code=='en'
                )
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
            label = (
                f"{details['name']} - {details['native_name']}"
                if details['name']!=details['native_name']
                else details['name']
            )
            options.append((label, iso3))
        options.sort(key=lambda o:o[0])
        return options

    def is_pair_installed(self, from_iso1:str, to_iso1:str)->bool:
        try:
            for pkg in argostranslate.package.get_installed_packages():
                if pkg.from_code == from_iso1 and pkg.to_code == to_iso1:
                    return True
            return False
        except Exception:
            return False

    def build_translation(self, source_iso1:str, target_iso1:str, timeout:float=60.0):
        started = time.monotonic()
        while True:
            try:
                installed = argostranslate.translate.get_installed_languages()
                src = next(
                    (l for l in installed if l.code == source_iso1),
                    None
                )
                tgt = next(
                    (l for l in installed if l.code == target_iso1),
                    None
                )
                if src is not None and tgt is not None:
                    translation = src.get_translation(tgt)
                    if translation is not None:
                        return translation
            except Exception as e:
                print(f'build_translation() retry error: {e}')
            elapsed = time.monotonic() - started
            if elapsed >= timeout:
                break
            time.sleep(1.0)
        return None

    def download_and_install(self, source_iso1:str, target_iso1:str)->tuple[str|None, bool]:
        try:
            pair_lock = self.get_pair_lock(source_iso1, target_iso1)
            with pair_lock:
                self.ensure_index()
                available = argostranslate.package.get_available_packages()
                # direct
                direct_pkg = next(
                    (
                        p for p in available
                        if p.from_code == source_iso1
                        and p.to_code == target_iso1
                    ),
                    None
                )
                if direct_pkg is not None:
                    if not self.is_pair_installed(source_iso1, target_iso1):
                        msg = f'Downloading argos package {source_iso1} -> {target_iso1}...'
                        print(msg)
                        download_path = direct_pkg.download()
                        argostranslate.package.install_from_path(download_path)
                        msg = f'Installed argos package {source_iso1} -> {target_iso1}'
                        print(msg)
                    return None, True
                # english-pivot
                if source_iso1!='en' and target_iso1!='en':
                    src_to_en = next(
                        (
                            p for p in available
                            if p.from_code == source_iso1
                            and p.to_code=='en'
                        ),
                        None
                    )
                    en_to_tgt = next(
                        (
                            p for p in available
                            if p.from_code=='en'
                            and p.to_code == target_iso1
                        ),
                        None
                    )
                    if src_to_en is not None and en_to_tgt is not None:
                        msg = f'No direct {source_iso1}->{target_iso1}; using English pivot.'
                        print(msg)
                        if not self.is_pair_installed(source_iso1,'en'):
                            msg = f'Downloading argos package {source_iso1} -> en...'
                            print(msg)
                            download_path = src_to_en.download()
                            argostranslate.package.install_from_path(download_path)
                            msg = f'Installed argos package {source_iso1} -> en'
                            print(msg)
                        if not self.is_pair_installed('en',target_iso1):
                            msg = f'Downloading argos package en -> {target_iso1}...'
                            print(msg)
                            download_path = en_to_tgt.download()
                            argostranslate.package.install_from_path(download_path)
                            msg = f'Installed argos package en -> {target_iso1}'
                            print(msg)
                        msg = f'English pivot ready: {source_iso1} -> en -> {target_iso1}'
                        print(msg)
                        return None, True
                error = (
                    f'No argos package available for '
                    f'{source_iso1} -> {target_iso1} '
                    f'(direct or English-pivoted)'
                )
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
                stanza.download(
                    source_iso1,
                    processors='tokenize,mwt'
                )
            except Exception:
                pass
            error, ok = self.download_and_install(
                source_iso1,
                target_iso1
            )
            if not ok:
                return error, False
            translation = self.build_translation(
                source_iso1,
                target_iso1,
                timeout=60.0
            )
            if translation is None:
                error = (
                    f'No translation path available: '
                    f'{source_iso1} -> {target_iso1}'
                )
                return error, False
            self.translation = translation
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

    def translate(self, text:str, sml_pattern:re.Pattern)->tuple[str, bool]:
        try:
            if not text or not text.strip():
                return text, True
            if not sml_pattern:
                return self.process(text)
            parts:list[tuple[str, bool]] = []
            last_end = 0
            for m in sml_pattern.finditer(text):
                if m.start() > last_end:
                    parts.append(
                        (text[last_end:m.start()], False)
                    )
                parts.append(
                    (m.group(0), True)
                )
                last_end = m.end()
            if last_end < len(text):
                parts.append(
                    (text[last_end:], False)
                )
            buf:list[str] = []
            for part, is_sml in parts:
                if is_sml:
                    buf.append(part)
                    continue
                translated_part, ok = self.process(part)
                if not ok:
                    return translated_part, False
                buf.append(translated_part)
            out:str = ''.join(buf)
            return out, True
        except Exception as e:
            error = f'ArgosTranslator.translate() error: {e}'
            return error, False