import importlib
legends_langs = ['ara', 'ben', 'zho', 'eng', 'fra', 'deu', 'hin', 'hun', 'ind', 'ita', 'jav', 'jpn', 'kor', 'fas', 'pol', 'por', 'rus', 'spa', 'tam', 'tel', 'tur', 'yor']
legends_all = {lang: importlib.import_module(f'lib.lang.legends_{lang}').legends for lang in legends_langs}
