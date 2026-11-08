import os, re, sys, glob, shutil, filecmp, argparse, tempfile, subprocess
from pathlib import Path
root_dir = str(Path(__file__).resolve().parents[1])
python_env_dir = os.path.join(root_dir, 'python_env')
python_env_exec = os.path.join(python_env_dir, 'Scripts', 'python.exe') if sys.platform == 'win32' else os.path.join(python_env_dir, 'bin', 'python')
# runs on e2a's python_env (argostranslate, iso639): started by another interpreter, it starts again with python_env's
if os.path.isfile(python_env_exec) and os.path.normcase(os.path.realpath(sys.prefix)) != os.path.normcase(os.path.realpath(python_env_dir)) and not os.environ.get('E2A_TRANSLATE_EBOOK'):
    try:
        sys.exit(subprocess.run([python_env_exec, os.path.abspath(__file__), *sys.argv[1:]], env={**os.environ, 'E2A_TRANSLATE_EBOOK': '1'}).returncode)
    except KeyboardInterrupt:
        sys.exit(130)
examples = '''examples:
  translate_ebook.py book.epub --to fr
  translate_ebook.py book.epub --to fra,ara,spa
  translate_ebook.py book.azw3 --from en --to deu -o /path/to/book_deu.azw3
  translate_ebook.py /path/to/books -r --to es,it --output_dir /path/to/books_translated
  translate_ebook.py book.epub --from eng --to all
  translate_ebook.py @books.txt --to ita --mode bilingual
  translate_ebook.py --list
  translate_ebook.py --list --from eng'''
description = '''Translate ebooks offline, out of e2a, with the Argos Translate calibre plugin
(tools/argostranslate-calibre-plugin.zip). EPUB/AZW3 are translated as they are, the other formats
calibre's ebook-convert reads (PDF, DOCX, MOBI, ...) are converted to EPUB once, before the first
language, and their translations saved as EPUB. It runs on e2a's python_env and argos-translate packages
(models/argos-translate): a language pair e2a already uses is not downloaded again, a missing one is
downloaded on first use (direct or through English). The plugin is installed into e2a's own calibre
profile (run/) on first use, your calibre setup is left untouched.
Translated paths are printed on stdout, progress and logs on stderr.'''
parser = argparse.ArgumentParser(prog='translate_ebook.py', fromfile_prefix_chars='@', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=examples, description=description)
parser.add_argument('books', nargs='*', help='Ebook files (EPUB, AZW3, or PDF, DOCX, MOBI... converted to EPUB first) or folders to translate; @list.txt reads paths from a file, one per line')
parser.add_argument('-t', '--to', dest='dst', metavar='LANG[,LANG...]', help='Target language(s), ISO-639-1 or ISO-639-3 codes, comma separated for several (fr, fra or fra,ara,spa): one translated ebook per language. all: every language the source reaches (see --list --from), installed ones only with --no_download')
parser.add_argument('-f', '--from', dest='src', default='', metavar='LANG', help='Source language, ISO-639-1 or ISO-639-3 code (default: read from each book)')
parser.add_argument('-r', '--recursive', action='store_true', help='Also look for books in the subfolders of the given folders')
parser.add_argument('-o', '--output', help='Output file, single input only, same extension as the input, .epub for a converted one (default: <name>.<lang>.<ext> next to the input)')
parser.add_argument('--output_dir', help='Write the translations into this folder (subfolders are mirrored with -r) instead of next to each book')
parser.add_argument('--overwrite', action='store_true', help='Translate again even if the output file already exists (skipped otherwise)')
parser.add_argument('-m', '--mode', choices=['replace', 'bilingual'], default='replace', help='replace: the translation replaces the text. bilingual: each paragraph is followed by its translation, saved as <name>.<lang>.bilingual.<ext> (default: replace)')
parser.add_argument('--device', choices=['cpu', 'cuda', 'auto'], help='Device argostranslate runs on (default: cpu)')
parser.add_argument('--batch_size', type=int, help='Segments sent to the translation worker per request (default: 16)')
parser.add_argument('--no_cache', action='store_true', help='Neither read nor write the translation cache (run/argos_translate/cache.sqlite), the one that makes a second run of the same book near instant')
parser.add_argument('--no_download', action='store_true', help='Never download a missing argos-translate package, fail instead')
parser.add_argument('--allow_changes', action='store_true', help='Only when argostranslate is missing from python_env: install it even if packages already there would change version')
parser.add_argument('--list', action='store_true', help='List the installed and the downloadable language pairs, then exit. With --from and/or --to: only their pairs, plus the targets a source reaches through English')
args = parser.parse_args()
start_dir = os.getcwd()

def to_iso1(code:str)->str:
    # argos-translate speaks ISO-639-1, e2a ISO-639-3: both are accepted
    if len(code) != 3:
        return code
    try:
        from iso639 import Lang
        return Lang(code).pt1 or code
    except Exception:
        return code

def to_abs(path:str)->str:
    # from where the script was started, also once it runs from e2a's root
    return os.path.abspath(os.path.join(start_dir, os.path.expanduser(path)))

def is_translation(path:str, langs:set)->bool:
    # named after a language of this run, or an earlier run's: <name>.<lang>.bilingual.<ext>, <name>.<lang>.<ext> beside
    # its <name>.<ebook ext>, or <name>.<lang>.<ext> written in <lang> (the plugin sets it), i.e. in another output folder
    folder, name = os.path.split(path)
    stem = os.path.splitext(name)[0]
    if any(stem.endswith(f'.{lang}') or stem.endswith(f'.{lang}.bilingual') for lang in langs):
        return True
    base, dot, code = stem.removesuffix('.bilingual').rpartition('.')
    if not (dot and 2 <= len(code) <= 3 and code.isalpha() and code.islower()):
        return False
    return stem.endswith('.bilingual') or any(os.path.isfile(os.path.join(folder, base + ext)) for ext in book_formats + convert_formats) or book_language(path) == code

def has_epub(path:str)->bool:
    # a book to convert beside its own EPUB/AZW3: the EPUB/AZW3 is the one translated
    base = os.path.splitext(path)[0]
    return os.path.splitext(path)[1].lower() in convert_formats and any(os.path.isfile(base + ext) for ext in book_formats)

def list_books(items:list[str], output_dir:str, langs:set)->list[tuple[str, str]]:
    # folders are listed once, before the first language: the plugin then gets files only, so the translations
    # of a language never become books to translate for the next one. each book comes with its output folder,
    # mirrored from its folder with -r, as the plugin's own --output-dir does
    books:list = []
    seen:set = set()
    for item in (entry.strip() for entry in items):
        if not item:
            continue
        path = to_abs(item)
        if os.path.isdir(path):
            pattern = os.path.join(glob.escape(path), '**', '*') if args.recursive else os.path.join(glob.escape(path), '*')
            # nothing under the output folder is a book, even when it sits inside a scanned folder
            found = [(book, os.path.join(output_dir, os.path.dirname(os.path.relpath(book, path))) if output_dir else '') for book in sorted(glob.glob(pattern, recursive=args.recursive)) if os.path.isfile(book) and os.path.splitext(book)[1].lower() in book_formats + convert_formats and not is_translation(book, langs) and not has_epub(book) and not (output_dir and book.startswith(output_dir + os.sep))]
        else:
            found = [(path, output_dir)]
        for book, out_dir in found:
            if book not in seen:
                seen.add(book)
                books.append((book, out_dir))
    return books

book_formats = ('.epub', '.azw3')
# e2a's ebook formats ebook-convert reads (images, .doc, .pptx and .zip need e2a's own handling)
convert_formats = ('.mobi', '.azw', '.fb2', '.lrf', '.rb', '.snb', '.tcr', '.pdf', '.txt', '.rtf', '.docx', '.html', '.odt')
codes = [code.strip().lower() for code in (args.dst or '').split(',') if code.strip()]
to_all = 'all' in codes
if to_all and len(codes) > 1:
    parser.error('--to all cannot be combined with other languages')
targets = [] if to_all else list(dict.fromkeys(to_iso1(code) for code in codes))
source = to_iso1(args.src.strip().lower()) if args.src else ''
if not args.list and (not args.books or not codes):
    parser.error('give at least one book or folder and --to')
if args.output and not args.list and (len(args.books) > 1 or len(targets) != 1):
    parser.error('--output needs exactly one input book and one --to language')
# paths are taken from where the script was started, the plugin then runs from e2a's root
common_args = []
if args.output:
    common_args += ['--output', to_abs(args.output)]
if args.overwrite:
    common_args.append('--overwrite')
common_args += ['--mode', args.mode]
if args.device:
    common_args += ['--device', args.device]
if args.batch_size:
    common_args += ['--batch-size', str(args.batch_size)]
if args.no_cache:
    common_args.append('--no-cache')
if args.no_download:
    common_args.append('--no-download')
if args.allow_changes:
    common_args.append('--allow-changes')
os.chdir(root_dir)
sys.path.insert(0, root_dir)
# lib.conf pins argostranslate to 1 thread in float32 for e2a: kept only when set by the user, before lib.conf
argos_tuning = {key: os.environ[key] for key in ('ARGOS_INTRA_THREADS', 'ARGOS_COMPUTE_TYPE') if key in os.environ}
# e2a's paths and calibre profile: CALIBRE_CONFIG_DIRECTORY, CALIBRE_CACHE_DIRECTORY and CALIBRE_TEMP_DIR on run/
import lib.conf as conf
plugin_name = 'Argos Translate'
plugin_zip = os.path.join(root_dir, 'tools', 'argostranslate-calibre-plugin.zip')

def calibre_env()->dict:
    # as convert2epub() in lib/core.py: calibre must not run with python_env's interpreter or libraries
    env = dict(os.environ)
    for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONSTARTUP', 'PYTHONEXECUTABLE', 'PYTHONNOUSERSITE', 'LD_LIBRARY_PATH', 'LD_PRELOAD', 'DYLD_LIBRARY_PATH', 'DYLD_INSERT_LIBRARIES'):
        env.pop(key, None)
    # argostranslate's own defaults: CTranslate2 picks the threads and the fastest compute type (int8 on CPU)
    for key in ('ARGOS_INTRA_THREADS', 'ARGOS_COMPUTE_TYPE'):
        env.pop(key, None)
    env.update(argos_tuning)
    prefixes = [os.path.normcase(os.path.normpath(p)) for p in (os.environ.get('CONDA_PREFIX'), os.environ.get('VIRTUAL_ENV'), sys.prefix if sys.prefix != sys.base_prefix else None) if p]
    env['PATH'] = os.pathsep.join([p for p in env.get('PATH', '').split(os.pathsep) if p and not any(os.path.normcase(os.path.normpath(p)) == pre or os.path.normcase(os.path.normpath(p)).startswith(pre + os.sep) for pre in prefixes)])
    env.setdefault('LANG', 'C.UTF-8')
    env.setdefault('LC_ALL', 'C.UTF-8')
    if sys.platform.startswith('linux') and not env.get('DISPLAY') and not env.get('WAYLAND_DISPLAY'):
        env.setdefault('QT_QPA_PLATFORM', 'offscreen')
    # the plugin runs argostranslate with the VIRTUAL_ENV interpreter, else ./python_env (missing in docker): this one
    python = os.path.join(sys.prefix, 'Scripts', 'python.exe') if sys.platform == 'win32' else os.path.join(sys.prefix, 'bin', 'python')
    if os.path.isfile(python):
        env['VIRTUAL_ENV'] = sys.prefix
    return env

def calibre_cmd(prog:str, env:dict)->list[str]|None:
    path = env.get('PATH', '')
    exe = shutil.which(prog, path=path)
    if not exe:
        # calibre reached through an ebook-convert link only: its other tools sit beside the real file
        ebook_convert = shutil.which('ebook-convert', path=path)
        if ebook_convert:
            exe = shutil.which(prog, path=os.path.dirname(os.path.realpath(ebook_convert)))
    if not exe:
        return None
    if sys.platform != 'win32':
        try:
            with open(exe, 'rb') as f:
                head = f.readline(256)
            if head.startswith(b'#!'):
                shebang = head[2:].decode('utf-8', 'replace').strip()
                if shebang.startswith('/usr/bin/env') and 'python' in shebang:
                    interpreter = shutil.which(shebang.split()[-1], path=path)
                    if interpreter:
                        return [interpreter, exe]
        except OSError:
            pass
    return [exe]

def ensure_plugin(env:dict)->str|None:
    if not os.path.isfile(plugin_zip):
        return f'{plugin_zip} not found'
    # calibre-customize copies the zip to <config>/plugins/<plugin name>.zip: same bytes, same plugin
    installed = os.path.join(env.get('CALIBRE_CONFIG_DIRECTORY', ''), 'plugins', f'{plugin_name}.zip')
    if env.get('CALIBRE_CONFIG_DIRECTORY') and os.path.isfile(installed) and filecmp.cmp(plugin_zip, installed, shallow=False):
        return None
    cmd = calibre_cmd('calibre-customize', env)
    if cmd is None:
        return 'calibre-customize not found, install calibre (ebook2audiobook installs it)'
    result = subprocess.run(cmd + ['--add-plugin', plugin_zip], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, text=True, encoding='utf-8', errors='replace', env=env)
    if result.returncode != 0:
        return f'calibre-customize could not install {plugin_zip} (exit code {result.returncode}):\n{result.stdout.strip()}'
    return None

def parse_pairs(listing:str)->tuple[list, dict]:
    # the plugin's --list: its sections (title, [(src, dst), ...]) and the language names
    sections:list = []
    names:dict = {}
    for line in listing.splitlines():
        match = re.match(r'^\s+(\S+) -> (\S+)\t(.*) -> (.*)$', line)
        if match and sections:
            names[match.group(1)], names[match.group(2)] = match.group(3), match.group(4)
            sections[-1][1].append((match.group(1), match.group(2)))
        elif line.strip() and line.strip() != '(none)':
            sections.append((line.rstrip(), []))
    return sections, names

def reachable(sections:list, src:str)->list[str]:
    # every target of a source: its pairs (installed ones only with --no_download), and through English when it reaches English
    known = [pair for _, pairs in (sections[:1] if args.no_download else sections) for pair in pairs]
    dsts = {dst for pair_src, dst in known if pair_src == src}
    if src != 'en' and 'en' in dsts:
        dsts |= {dst for pair_src, dst in known if pair_src == 'en' and dst != src}
    return sorted(dsts)

def show_pairs(listing:str)->None:
    # the plugin lists every pair: --from and --to keep theirs, and a source other than English gets the targets
    # it reaches through English, fetched on first use like the direct ones
    if not source and not targets:
        print(listing, end='')
        return
    sections, names = parse_pairs(listing)
    known = [pair for _, pairs in sections for pair in pairs]
    if source and source != 'en' and (source, 'en') in known:
        sections.append((f'Reachable through English ({source} -> en -> ...), fetched automatically on first use:', sorted({(source, dst) for src, dst in known if src == 'en' and dst != source}, key=lambda pair: pair[1])))
    shown:set = set()
    for title, pairs in sections:
        kept = [pair for pair in pairs if (not source or pair[0] == source) and (not targets or pair[1] in targets) and pair not in shown]
        shown.update(kept)
        print(title)
        for src, dst in kept:
            print(f'  {src} -> {dst}\t{names.get(src, src)} -> {names.get(dst, dst)}')
        if not kept:
            print('  (none)')

def run_plugin(plugin_args:list[str], capture:bool=False)->subprocess.CompletedProcess:
    # from the folder holding models/: the plugin takes ./models/argos-translate, e2a's packages folder
    return subprocess.run(cmd + ['-r', plugin_name, '--'] + plugin_args, cwd=os.path.dirname(conf.models_dir), env={**env, 'CALIBRE_TEMP_DIR': run_tmp}, stdout=subprocess.PIPE if capture else None, text=True, encoding='utf-8', errors='replace')

def book_language(path:str)->str:
    # as the plugin does without --from: the book's own language, read here by calibre's ebook-meta
    meta = calibre_cmd('ebook-meta', env)
    if meta is None or not os.path.isfile(path):
        return ''
    result = subprocess.run(meta + [path], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, text=True, encoding='utf-8', errors='replace', env=env)
    match = re.search(r'^Languages\s*:\s*([^,\s]+)', result.stdout, re.M)
    return to_iso1(match.group(1).lower()) if match else ''

def convert_book(path:str)->str|None:
    # once per book, with calibre's ebook-convert, into an EPUB named as the book: its translations are <name>.<lang>.epub
    convert = calibre_cmd('ebook-convert', env)
    if convert is None:
        print('ebook-convert not found, install calibre (ebook2audiobook installs it)', file=sys.stderr)
        return None
    epub = os.path.join(tempfile.mkdtemp(prefix='convert_', dir=run_tmp), f'{os.path.splitext(os.path.basename(path))[0]}.epub')
    print(f'{path}: converting to EPUB', file=sys.stderr, flush=True)
    # PDF, TXT... seldom carry a language: --from becomes the EPUB's, the one the plugin reads
    result = subprocess.run(convert + [path, epub] + (['--language', source] if source else []), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, text=True, encoding='utf-8', errors='replace', env={**env, 'CALIBRE_TEMP_DIR': run_tmp})
    if result.returncode != 0 or not os.path.isfile(epub):
        print(f'{path}: ebook-convert failed (exit code {result.returncode}):\n{result.stdout.strip()[-2000:]}', file=sys.stderr)
        return None
    return epub

env = calibre_env()
error = ensure_plugin(env)
if error is not None:
    print(error, file=sys.stderr)
    sys.exit(1)
cmd = calibre_cmd('calibre-debug', env)
if cmd is None:
    print('calibre-debug not found, install calibre (ebook2audiobook installs it)', file=sys.stderr)
    sys.exit(1)
# a calibre temp folder of its own, removed even when ctrl-c leaves calibre no time to clean it
os.makedirs(env.get('CALIBRE_TEMP_DIR') or conf.run_dir, exist_ok=True)
run_tmp = tempfile.mkdtemp(prefix='e2a_calibre_', dir=env.get('CALIBRE_TEMP_DIR') or conf.run_dir)
runs:dict[str, list] = {}
failed:set = set()
code = 0
try:
    sections:list = []
    if args.list or to_all:
        listing = run_plugin(['--list'] + common_args, capture=True)
        if listing.returncode != 0:
            print(listing.stdout, end='')
            sys.exit(1)
        if args.list:
            show_pairs(listing.stdout)
            sys.exit(0)
        sections, _ = parse_pairs(listing.stdout)
    books = list_books(args.books, to_abs(args.output_dir) if args.output_dir else '', {lang for _, pairs in sections for pair in pairs for lang in pair} if to_all else set(targets))
    if not books:
        parser.error('no ebook found in the given paths')
    # checked, and converted when needed, once before the first language: the plugin reads EPUB/AZW3 only.
    # --to all and a converted book need the source now: --from, else the book's own language
    groups:dict = {}
    for book, out_dir in books:
        ext = os.path.splitext(book)[1].lower()
        if not os.path.isfile(book):
            print(f'{book}: not found', file=sys.stderr)
            code = 1
            continue
        if ext in convert_formats:
            # every translation already there (and no --overwrite): skipped, not converted for nothing
            dsts = (reachable(sections, source) if to_all else targets) if source or not to_all else []
            suffix = '.bilingual' if args.mode == 'bilingual' else ''
            if dsts and not args.overwrite and all(os.path.exists(to_abs(args.output) if args.output else os.path.join(out_dir or os.path.dirname(book), f'{os.path.splitext(os.path.basename(book))[0]}.{dst}{suffix}.epub')) for dst in dsts):
                print(f'{book}: skipped, its translations already exist (use --overwrite)', file=sys.stderr)
                continue
            epub = convert_book(book)
            if epub is None:
                code = 1
                continue
            src = source or book_language(epub)
            # its translations go beside the book (or into --output_dir), not beside the converted EPUB
            out_dir = out_dir or os.path.dirname(book)
        elif ext in book_formats:
            epub = book
            src = source or (book_language(book) if to_all else '')
        else:
            print(f"{book}: {ext or 'no extension'} not supported (EPUB, AZW3, {', '.join(fmt[1:].upper() for fmt in convert_formats)})", file=sys.stderr)
            code = 1
            continue
        if not src and (to_all or ext in convert_formats):
            print(f'{book}: book language unknown, set it with --from', file=sys.stderr)
            code = 1
            continue
        groups.setdefault((src, out_dir), []).append(epub)
    # one plugin run per language (and source, output folder): it translates into one language at a time
    for (src, out_dir), group in groups.items():
        dsts = reachable(sections, src) if to_all else targets
        if not dsts:
            print(f"{', '.join(group)}: no language pair from {src}", file=sys.stderr)
            code = 1
        for dst in dsts:
            runs.setdefault(f'{src} -> {dst}' if to_all else dst, []).append(group + (['--from', src] if src else []) + ['--to', dst] + (['--output-dir', out_dir] if out_dir else []) + common_args)
    for index, (label, label_runs) in enumerate(runs.items(), 1):
        if len(runs) > 1:
            print(f'=== {label} ({index}/{len(runs)})', file=sys.stderr, flush=True)
        for plugin_args in label_runs:
            if run_plugin(plugin_args).returncode != 0:
                code = 1
                failed.add(label)
except KeyboardInterrupt:
    code = 130
finally:
    shutil.rmtree(run_tmp, ignore_errors=True)
if len(runs) > 1 and code != 130:
    print(f"Languages done: {', '.join(f'{label} failed' if label in failed else f'{label} ok' for label in runs)}", file=sys.stderr)
sys.exit(code)
