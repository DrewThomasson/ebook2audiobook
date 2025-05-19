import os
import tempfile
import argostranslate.package
import argostranslate.translate

from iso639 import languages
from lib.conf import models_dir
from lib.lang import language_mapping

# NOTE: source_lang and target_lang must be iso639-1 (2 letters)

class ArgosTranslator:

    def __init__(self, neural_machine="argostranslate"):
        self.neural_machine = neural_machine
        self.translation = None
        
    def get_language_iso3(self, lang_iso1):
        lang = lang_iso1
        try:  
            lang_array = languages.get(part1=lang_iso1)
            if lang_array:
                lang = lang_array.part3
        except Exception:
            pass
        return lang

    def get_all_sources_lang(self):
        available_packages = argostranslate.package.get_available_packages()
        return sorted(set(pkg.from_code for pkg in available_packages))

    def get_all_targets_lang(self, source_lang):
        available_packages = argostranslate.package.get_available_packages()
        list_iso1 = sorted(set(pkg.to_code for pkg in available_packages if pkg.from_code == source_lang))
        language_translate_mapping = {}
        for iso1 in list_iso1:
            try:
                iso3 = self.get_language_iso3(iso1)
                if iso3 in language_mapping:
                    language_translate_mapping[iso3] = dict(language_mapping[iso3])
                    language_translate_mapping[iso3]["iso1"] = iso1
            except KeyError:
                pass
        language_translate_options = [
            (
                f"{details['name']} - {details['native_name']}" if details['name'] != details['native_name'] else details['name'],
                lang
            )
            for lang, details in language_translate_mapping.items()
        ]
        return language_translate_options
        
    def get_all_target_packages(self, source_lang):
        available_packages = argostranslate.package.get_available_packages()
        return [pkg for pkg in available_packages if pkg.from_code == source_lang]

    def is_package_installed(self, source_lang, target_lang):
        try:
            installed_languages = argostranslate.translate.get_installed_languages()
            source_language = next((lang for lang in installed_languages if lang.code == source_lang), None)
            target_language = next((lang for lang in installed_languages if lang.code == target_lang), None)
            return source_language is not None and target_language is not None
        except Exception as e:
            error = f'is_package_installed() error: {e}'
            return False

    def download_and_install_argos_package(self, source_lang, target_lang):
        try:
            if self.is_package_installed(source_lang, target_lang):
                print(f"Package for translation from {source_lang} to {target_lang} is already installed.")
                print(msg)                
                return msg, True
            available_packages = self.get_all_target_packages(source_lang)
            target_package = None
            for pkg in available_packages:
                if pkg.from_code == source_lang and pkg.to_code == target_lang:
                    target_package = pkg
                    break
            if target_package:
                with tempfile.TemporaryDirectory() as tmpdirname:
                    print(f"Downloading package for translation from {source_lang} to {target_lang}...")
                    package_path = target_package.download()
                    argostranslate.package.install_from_path(package_path)
                    print(f"Package installed for translation from {source_lang} to {target_lang}")
                    return None, True
            else:
                msg = f"No available package found for translation from {source_lang} to {target_lang}."
                return msg, False
        except Exception as e:
            error = f'download_and_install_argos_package() error: {e}'
            return error, False

    def process(self, text):
        try:
            return self.translation.translate(text), True
        except Exception as e:
            error = f'AgrosTranslator.process() error: {e}'
            return error, False

    def start(self, source_lang, target_lang):
        try:
            if self.neural_machine != "argostranslate":
                error = f"Neural machine '{self.neural_machine}' is not supported."
                return error, False
            status = True
            if not self.is_package_installed(source_lang, target_lang):
                error, status = self.download_and_install_argos_package(source_lang, target_lang)
            if status:
                installed_languages = argostranslate.translate.get_installed_languages()
                source_language = next((lang for lang in installed_languages if lang.code == source_lang), None)
                target_language = next((lang for lang in installed_languages if lang.code == target_lang), None)

                if not source_language or not target_language:
                    error = f"Translation languages not installed: {source_lang} to {target_lang}"
                    return error, False

                self.translation = source_language.get_translation(target_language)
                return None, True
            return error, status
        except Exception as e:
            error = f'AgrosTranslator.process() error: {e}'
            return error, False