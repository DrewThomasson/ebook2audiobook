import os,  threading
import argostranslate.package,  argostranslate.translate

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

    @classmethod
    def _ensure_index(cls)->None:
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
        self._ensure_index()
        pkgs = argostranslate.package.get_available_packages()
        return sorted(set(p.from_code for p in pkgs))

    def get_target_options(self, source_iso3:str)->list[tuple[str, str]]:
        source_iso1 = self.get_language_iso1(source_iso3)
        if not source_iso1:
            return []
        self._ensure_index()
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
            print(f'ArgosTranslator.is_package_installed() error: {e}')
            return False

    def _is_pair_installed(self, from_iso1:str, to_iso1:str)->bool:
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
                self._ensure_index()
                available = argostranslate.package.get_available_packages()
                # direct
                direct_pkg = next((p for p in available if p.from_code == source_iso1 and p.to_code == target_iso1),None)
                if direct_pkg is not None:
                    if not self._is_pair_installed(source_iso1, target_iso1):
                        print(f"Downloading argos package {source_iso1} -> {target_iso1}...")
                        argostranslate.package.install_from_path(direct_pkg.download())
                        print(f"Installed argos package {source_iso1} -> {target_iso1}")
                    return None, True
                # english-pivot
                if source_iso1!='en' and target_iso1!='en':
                    src_to_en = next((p for p in available if p.from_code == source_iso1 and p.to_code=='en'),None)
                    en_to_tgt = next((p for p in available if p.from_code=='en' and p.to_code == target_iso1),None)
                    if src_to_en is not None and en_to_tgt is not None:
                        print(f"No direct {source_iso1}->{target_iso1}; using English pivot.")
                        if not self._is_pair_installed(source_iso1,'en'):
                            print(f"Downloading argos package {source_iso1} -> en...")
                            argostranslate.package.install_from_path(src_to_en.download())
                        if not self._is_pair_installed('en',target_iso1):
                            print(f"Downloading argos package en -> {target_iso1}...")
                            argostranslate.package.install_from_path(en_to_tgt.download())
                        print(f"English pivot ready: {source_iso1} -> en -> {target_iso1}")
                        return None, True
                error = f"No argos package available for {source_iso1} -> {target_iso1} (direct or English-pivoted)"
                return error, False
        except Exception as e:
            error = f'ArgosTranslator.download_and_install() error: {e}'
            return error, False

    def start(self, source_iso1:str, target_iso1:str)->tuple[str|None, bool]:
        try:
            if self.neural_machine!="argostranslate":
                return f"Neural machine '{self.neural_machine}' is not supported.",False
            err, ok = self.download_and_install(source_iso1, target_iso1)
            if not ok:
                return err, False
            installed = argostranslate.translate.get_installed_languages()
            src = next((l for l in installed if l.code == source_iso1),None)
            tgt = next((l for l in installed if l.code == target_iso1),None)
            if not src or not tgt:
                return f"Translation languages not installed: {source_iso1} -> {target_iso1}",False
            # get_translation() returns a PackageTranslation for direct pairs and a
            # CompositeTranslation when only a pivot path exists (via Bellman-Ford)
            self.translation = src.get_translation(tgt)
            if self.translation is None:
                return f"No translation path available: {source_iso1} -> {target_iso1}",False
            self.source_lang_iso1 = source_iso1
            self.target_lang_iso1 = target_iso1
            return None, True
        except Exception as e:
            return f'ArgosTranslator.start() error: {e}',False

    def process(self, text:str)->tuple[str, bool]:
        try:
            if not text or not text.strip():
                return text, True
            if self.translation is None:
                return 'ArgosTranslator.process() error: not started',False
            return self.translation.translate(text),True
        except Exception as e:
            return f'ArgosTranslator.process() error: {e}',False

    def translate_with_sml(self, text:str, sml_pattern)->tuple:

        def _stash(m):
            key = f"SMLZZ{len(placeholders)}ZZSML"
            placeholders[key]=m.group(0)
            return f" {key} "

        try:
            if not text or not text.strip():
                return text, True
            placeholders = {}
            masked = sml_pattern.sub(_stash, text) if sml_pattern is not None else text
            out, ok = self.process(masked)
            if not ok:
                return out, False
            for key, original in placeholders.items():
                out = out.replace(key, original)
            return out, True
        except Exception as e:
            error = f'translate_with_sml() error: {e}'
            return None, False
