# Runs inside lib/classes/tts_engines/venvs/melotts, never inside e2a's python_env:
# it must not import anything from e2a. Driven by SubprocessPipe(keep_alive=True).
#
# protocol (one JSON object per line):
#   stdout <- {"ready": true, "samplerate": 44100, "device": "...", "speakers": [...], "custom": bool} once loaded
#             {"ready": false, "error": "..."} then exit 1 if loading failed
#   stdin  -> {"op": "tts", "text", "speaker", "file", "speed", "sdp_ratio", "noise_scale", "noise_scale_w"}
#   stdout <- {"ok": true, "file": "...", "samplerate": 44100, "samples": n}
#             {"ok": false, "error": "...", "oom": bool}
#   EOF on stdin -> exit 0 (that is how e2a unloads the model and frees its VRAM)
#
# MeloTTS as upstream's api.TTS runs it: one checkpoint per language speaking with one of its built-in speakers. It has
# no voice cloning: e2a converts the output to a voice file itself (default_vc_model), the worker only speaks
import os, sys, json, types, argparse, importlib.util, importlib.machinery, faulthandler

def main()->int:
    # the protocol owns a private copy of fd 1; fd 1 itself is pointed at stderr so
    # upstream's prints, tqdm and C extensions can never write into the reply stream.
    proto = os.fdopen(os.dup(1), 'w', encoding='utf-8', buffering=1)
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    # same for fd 0, the request stream: fd 0 itself reads nothing, so upstream code reading stdin (melo's japanese
    # frontend opens pdb on a reading it cannot parse) meets EOF instead of eating requests or waiting forever
    requests = os.fdopen(os.dup(0), 'rb')
    null_fd = os.open(os.devnull, os.O_RDONLY)
    os.dup2(null_fd, 0)
    os.close(null_fd)
    # a native crash (SIGSEGV...) prints the python stack to stderr, which e2a shows in its log
    faulthandler.enable()
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default='')
    parser.add_argument('--model_dir', default='')
    parser.add_argument('--custom', default='')
    parser.add_argument('--language', default='EN')
    parser.add_argument('--berts', required=True)
    parser.add_argument('--bert_dir', required=True)
    parser.add_argument('--device', default='cpu')
    args = parser.parse_args()
    # one short sentence per MeloTTS language, spoken once at load
    warmup_texts = {'EN': 'Hello.', 'ES': 'Hola.', 'FR': 'Bonjour.', 'ZH': '你好。', 'JP': 'こんにちは。', 'KR': '안녕하세요.'}
    try:
        from huggingface_hub import snapshot_download, HfApi
        # plain-folder downloads (local_dir): the HF cache layout symlinks, and huggingface_hub's symlink
        # probe races under threaded downloads (WinError 1314 on windows without symlink rights)
        if args.custom:
            # a custom model brings its MeloTTS config and weights
            model_path = args.custom
        else:
            # complete once the marker exists: config.json lands first, so a download cut during the weights
            # would look finished forever; snapshot_download resumes what is missing
            model_path = args.model_dir
            model_marker = os.path.join(model_path, '.e2a_complete')
            if not os.path.exists(model_marker):
                snapshot_download(args.repo, local_dir=model_path, allow_patterns=['config.json', 'checkpoint.pth'])
                open(model_marker, 'w').close()
        # MeloTTS' frontend BERTs: melo loads every language's tokenizer at import and this language's model on its
        # first sentence, by repo id. Each one is a plain folder (tokenizer files, plus the weights for this language:
        # safetensors when the repo has them), and repo ids are pointed at these folders below
        berts = json.loads(args.berts)
        bert_dirs = {}
        for bert_language, bert_repo in berts.items():
            bert_path = os.path.join(args.bert_dir, bert_repo.replace('/', '--'))
            bert_dirs[bert_repo] = bert_path
            with_weights = bert_language == args.language
            if not os.path.exists(os.path.join(bert_path, '.e2a_complete')) or (with_weights and not any(os.path.exists(os.path.join(bert_path, weights)) for weights in ('model.safetensors', 'pytorch_model.bin'))):
                weights = []
                if with_weights:
                    weights = ['model.safetensors'] if 'model.safetensors' in HfApi().list_repo_files(bert_repo) else ['pytorch_model.bin']
                snapshot_download(bert_repo, local_dir=bert_path, allow_patterns=['*.json', '*.txt'] + weights, ignore_patterns=['*/*'])
                open(os.path.join(bert_path, '.e2a_complete'), 'w').close()
        import nltk
        # g2p_en (english frontend) and g2pkk (korean) fetch their nltk data at import into the default folder:
        # fetched once into NLTK_DATA instead (set by e2a, under models/tts/melotts)
        for resource, package in (('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng'), ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'), ('corpora/cmudict', 'cmudict')):
            try:
                nltk.data.find(resource)
            except LookupError:
                nltk.download(package, download_dir=os.environ.get('NLTK_DATA'), quiet=True)
        import numpy as np
        import torch
        import torch.distributed
        if not torch.distributed.is_available():
            # torch built without distributed support (USE_DISTRIBUTED=0: the jetson wheels, e2a's macOS +vulkan
            # builds): single-process inference only needs these to exist for the transformers imports
            for attr, value in (('ReduceOp', types.SimpleNamespace(SUM='sum', AVG='avg', PRODUCT='product', MIN='min', MAX='max')), ('is_initialized', lambda: False), ('get_rank', lambda: 0), ('get_world_size', lambda: 1)):
                if not hasattr(torch.distributed, attr):
                    setattr(torch.distributed, attr, value)
        import soundfile as sf
        from transformers import AutoTokenizer, AutoModelForMaskedLM
        for auto_class in (AutoTokenizer, AutoModelForMaskedLM):
            auto_class.from_pretrained = lambda model_id, *load_args, load=auto_class.from_pretrained, **load_kwargs: load(bert_dirs.get(model_id, model_id), *load_args, **load_kwargs)
        # melo imports cached_path at module level (download_utils), for the downloads done above: config and
        # checkpoint are passed as paths, so it is never called and stays out of the venv
        if importlib.util.find_spec('cached_path') is None:
            cached_path = types.ModuleType('cached_path')
            cached_path.__spec__ = importlib.machinery.ModuleSpec('cached_path', None)
            cached_path.cached_path = None
            sys.modules['cached_path'] = cached_path
        # melo's japanese frontend builds MeCab.Tagger() at import (mecab-python3 on unidic-lite; its speech path reads
        # kana through pykakasi), and its text2kata reads MeCab's classic "surface\tCSV" lines (full unidic's output),
        # the reading in field 6, opening pdb on a line it cannot read. mecab-python3 is not installed: its MeCab folder
        # and python-mecab-ko's mecab folder (korean, below) are the same folder on case-insensitive filesystems (windows,
        # macOS). fugashi, already there for the japanese BERT tokenizer, runs the same libmecab on unidic-lite, whose
        # dicrc sets its own tab layout (output-format-type unidic): cleared, so MeCab writes the classic lines, and an
        # unknown word (6 fields) gets its surface as the 7th. The format is quoted: the argument splitter eats backslashes
        import fugashi, unidic_lite
        mecab_args = f'-r "{os.path.join(unidic_lite.DICDIR, "mecabrc")}" -d "{unidic_lite.DICDIR}" --output-format-type= "--unk-format=%m\\t%H,%m\\n"'
        mecab_ja = types.ModuleType('MeCab')
        mecab_ja.__spec__ = importlib.machinery.ModuleSpec('MeCab', None)
        mecab_ja.Tagger = lambda *tagger_args: fugashi.GenericTagger(mecab_args)
        sys.modules['MeCab'] = mecab_ja
        # g2pkk (korean frontend) wants eunjeon on windows (a cp36 wheel only) and pip-installs it when missing (no
        # pip in a uv venv): python-mecab-ko, installed everywhere, has the same pos() output
        if sys.platform == 'win32' and importlib.util.find_spec('eunjeon') is None:
            import mecab
            eunjeon = types.ModuleType('eunjeon')
            eunjeon.__spec__ = importlib.machinery.ModuleSpec('eunjeon', None)
            eunjeon.Mecab = mecab.MeCab
            sys.modules['eunjeon'] = eunjeon
        device = args.device
        if device == 'cpu' and sys.platform == 'darwin':
            # melo's BERT frontends move to mps whenever it exists and the device is cpu (upstream's demo turns it
            # off the same way)
            torch.backends.mps.is_available = lambda: False
        from melo.api import TTS
        model = TTS(language=args.language, device=device, config_path=os.path.join(model_path, 'config.json'), ckpt_path=os.path.join(model_path, 'checkpoint.pth'))
        spk2id = model.hps.data.spk2id
        # speaker names as the presets write them, and lowercase with _ as - (the preset keys) -> spk2id key
        speakers = {str(name).lower().replace('_', '-'): name for name in spk2id.keys()}
        sampling_rate = int(model.hps.data.sampling_rate)
        # MeloTTS' BERT for this language loads now, and any frontend error shows as a load error instead of
        # failing the first sentence
        model.tts_to_file(warmup_texts.get(args.language, 'Hello.'), spk2id[next(iter(speakers.values()))], None, quiet=True)
    except Exception as e:
        proto.write(json.dumps({'ready': False, 'error': f'{type(e).__name__}: {e}'}) + '\n')
        return 1
    proto.write(json.dumps({'ready': True, 'samplerate': sampling_rate, 'device': device, 'speakers': list(speakers.values()), 'custom': bool(args.custom)}) + '\n')
    while True:
        raw = requests.readline()
        if not raw:
            break
        try:
            req = json.loads(raw)
        except Exception as e:
            proto.write(json.dumps({'ok': False, 'error': f'bad request: {e}', 'oom': False}) + '\n')
            continue
        if req.get('op') != 'tts':
            proto.write(json.dumps({'ok': False, 'error': f"unknown op {req.get('op')!r}", 'oom': False}) + '\n')
            continue
        try:
            text = req['text'].strip()
            # the request's speaker (a preset, or the language's default), a custom model's first one
            speaker = str(req.get('speaker') or next(iter(speakers.values()))).lower().replace('_', '-')
            if speaker not in speakers:
                raise ValueError(f"speaker {req.get('speaker')!r} not in this model: {list(speakers.values())}")
            audio = model.tts_to_file(text, spk2id[speakers[speaker]], None, sdp_ratio=float(req.get('sdp_ratio', 0.2)), noise_scale=float(req.get('noise_scale', 0.6)), noise_scale_w=float(req.get('noise_scale_w', 0.8)), speed=float(req.get('speed', 1.0)), quiet=True)
            audio = np.asarray(audio, dtype=np.float32).reshape(-1)
            if audio.shape[0] == 0:
                raise ValueError(f'no audio generated for: {text[:80]}')
            sf.write(req['file'], audio, sampling_rate, subtype='FLOAT')
            reply = {'ok': True, 'file': req['file'], 'samplerate': sampling_rate, 'samples': int(audio.shape[0])}
        except Exception as e:
            # no retry here: e2a's convert() returns False and core.py unloads the
            # engine, which closes stdin and ends this process.
            error = f'{type(e).__name__}: {e}'
            reply = {'ok': False, 'error': error, 'oom': 'out of memory' in error.lower()}
            try:
                if device == 'cuda':
                    torch.cuda.empty_cache()
                elif device == 'xpu':
                    torch.xpu.empty_cache()
                elif device == 'mps':
                    torch.mps.empty_cache()
            except Exception:
                pass
        proto.write(json.dumps(reply) + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
