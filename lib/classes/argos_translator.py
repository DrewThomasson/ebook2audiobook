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

    def __init__(self, neural_machine:str='argostranslate')->None:
        self.neural_machine = neural_machine
        self.translation = None
        self.source_lang_iso1 = None
        self.target_lang_iso1 = None

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

    @staticmethod
    def get_language_iso3(lang_iso1:str)->str:
        try:
            ld = Lang(lang_iso1)
            if ld:
                return ld.pt3
        except Exception:
            pass
        return lang_iso1

    @staticmethod
    def get_language_iso1(lang_iso3:str)->str|None:
        try:
            ld = Lang(lang_iso3)
            if ld:
                return ld.pt1 or None
        except Exception:
            pass
        return None

    @staticmethod
    def is_pair_installed(from_iso1:str, to_iso1:str)->bool:
        try:
            for pkg in argostranslate.package.get_installed_packages():
                if pkg.from_code == from_iso1 and pkg.to_code == to_iso1:
                    return True
            return False
        except Exception:
            return False

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
        # Direct targets
        direct = {p.to_code for p in pkgs if p.from_code == source_iso1}
        reachable = set(direct)
        # English-pivot: if source->en exists, add all en->* targets
        if source_iso1 != 'en' and 'en' in direct:
            en_targets = {p.to_code for p in pkgs if p.from_code == 'en'}
            reachable |= en_targets
        reachable.discard(source_iso1)
        options:list[tuple[str, str]] = []
        for iso1 in reachable:
            iso3 = self.get_language_iso3(iso1)
            if iso3 == source_iso3 or iso3 not in language_mapping:
                continue
            details = language_mapping[iso3]
            label = (
                f"{details['name']} - {details['native_name']}"
                if details['name'] != details['native_name']
                else details['name']
            )
            options.append((label, iso3))
        options.sort(key=lambda o: o[0])
        return options

    def build_translation(self, source_iso1:str, target_iso1:str, timeout:float = 60.0)->object|None:
        started = time.monotonic()
        while True:
            try:
                installed = argostranslate.translate.get_installed_languages()
                # Map codes to language objects
                src_lang = next((l for l in installed if l.code == source_iso1), None)
                tgt_lang = next((l for l in installed if l.code == target_iso1), None)
                en_lang = next((l for l in installed if l.code == 'en'), None)
                if src_lang is None or tgt_lang is None:
                    pass 
                elif src_lang is not None and tgt_lang is not None:
                    # 1. Try direct translation
                    translation = src_lang.get_translation(tgt_lang)
                    if translation is not None:
                        return translation
                    # 2. Try English Pivot Manually
                    # If direct fails but we have English, check if pivot path exists
                    if en_lang is not None and source_iso1 != 'en' and target_iso1 != 'en':
                        trans_src_en = src_lang.get_translation(en_lang)
                        trans_en_tgt = en_lang.get_translation(tgt_lang)
                        if trans_src_en is not None and trans_en_tgt is not None:
                            # Create a custom pivot translator object
                            class PivotTranslation:
                                def __init__(self, t1, t2):
                                    self.t1 = t1
                                    self.t2 = t2
                                def translate(self, text):
                                    return self.t2.translate(self.t1.translate(text))
                            return PivotTranslation(trans_src_en, trans_en_tgt)
            except Exception as e:
                error = f'build_translation() retry error: {e}'
                print(error)
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
                # Check direct package
                direct_pkg = next(
                    (
                        p
                        for p in available
                        if p.from_code == source_iso1 and p.to_code == target_iso1
                    ),
                    None,
                )
                if direct_pkg is not None:
                    if not self.is_pair_installed(source_iso1, target_iso1):
                        print(f'Downloading argos package {source_iso1} -> {target_iso1}…')
                        download_path = direct_pkg.download()
                        argostranslate.package.install_from_path(download_path)
                        msg = f'Installed argos package {source_iso1} -> {target_iso1}'
                        print(msg)
                    return None, True
                # English-pivot fallback
                if source_iso1 != 'en' and target_iso1 != 'en':
                    src_to_en = next(
                        (
                            p
                            for p in available
                            if p.from_code == source_iso1 and p.to_code == 'en'
                        ),
                        None,
                    )
                    en_to_tgt = next(
                        (
                            p
                            for p in available
                            if p.from_code == 'en' and p.to_code == target_iso1
                        ),
                        None,
                    )
                    if src_to_en is not None and en_to_tgt is not None:
                        print(f'No direct {source_iso1}->{target_iso1}; using English pivot.')
                        if not self.is_pair_installed(source_iso1, 'en'):
                            msg = f'Downloading argos package {source_iso1} -> en…'
                            print(msg)
                            download_path = src_to_en.download()
                            argostranslate.package.install_from_path(download_path)
                            msg = f'Installed argos package {source_iso1} -> en'
                            print(msg)
                        if not self.is_pair_installed('en', target_iso1):
                            msg = f'Downloading argos package en -> {target_iso1}…'
                            print(msg)
                            download_path = en_to_tgt.download()
                            argostranslate.package.install_from_path(download_path)
                            msg = f'Installed argos package en -> {target_iso1}'
                            print(msg)
                        msg = f'English pivot ready: {source_iso1} -> en -> {target_iso1}'
                        print(msg)
                        return None, True

                error = (
                    f'No argos package available for {source_iso1} -> {target_iso1} '
                    f'(direct or English-pivoted)'
                )
                return error, False
        except Exception as e:
            error = f'ArgosTranslator.download_and_install() error: {e}'
            return error, False

    def start(self, source_iso1:str, target_iso1:str)->tuple[str|None, bool]:
        try:
            if self.neural_machine != 'argostranslate':
                return f'Neural machine {self.neural_machine} is not supported.', False
            try:
                stanza.download(source_iso1, processors='tokenize,mwt')
            except Exception:
                pass
            error, ok = self.download_and_install(source_iso1, target_iso1)
            if not ok:
                return error, False
            translation = self.build_translation(source_iso1, target_iso1, timeout=60.0)
            if translation is None:
                error = f'No translation path available: {source_iso1} -> {target_iso1}'
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
                return 'ArgosTranslator.process() error: not started', False
            return self.translation.translate(text), True
        except Exception as e:
            error = f'ArgosTranslator.process() error: {e}'
            return error, False

    def translate(self, text:str, sml_pattern:re.Pattern|None)->tuple[str, bool]:
        try:
            if not text or not text.strip():
                return text, True
            if not sml_pattern:
                return self.process(text)

            parts:list[tuple[str, bool]] = []
            last_end = 0
            for m in sml_pattern.finditer(text):
                if m.start() > last_end:
                    parts.append((text[last_end : m.start()], False))
                parts.append((m.group(0), True))
                last_end = m.end()
            if last_end < len(text):
                parts.append((text[last_end:], False))

            buf:list[str] = []
            for part, is_sml in parts:
                if is_sml:
                    buf.append(part)
                else:
                    translated_part, ok = self.process(part)
                    if not ok:
                        return translated_part, False
                    buf.append(translated_part)

            return ''.join(buf), True
        except Exception as e:
            error = f'ArgosTranslator.translate() error: {e}'
            return error, False
