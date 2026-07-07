"""Batch precompile all voice-clone prompts for Qwen3-TTS.

Usage: python tools/precompile_qwen3_voices.py [--voices-dir C:/ebook2audio/voices]

Scans for *.wav files, runs create_voice_clone_prompt() on each,
and caches the result under models/qwen3_voice_cache/.
"""
import argparse, hashlib, os, sys, time, warnings
from pathlib import Path

# ponytail: force UTF-8 for console output (avoids cp1252 encode errors on Unicode filenames)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

warnings.filterwarnings('ignore')

# add project root
PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))
os.chdir(str(PROJECT))

from lib.conf import voices_dir
from lib.conf_models import TTS_ENGINES, default_engine_settings

QWEN3_CACHE = Path(PROJECT) / 'models' / 'qwen3_voice_cache'
QWEN3_REPO = default_engine_settings[TTS_ENGINES['QWEN3TTS']]['repo']


def cache_path(audio_path: str) -> Path:
    key = hashlib.sha256(f'{audio_path}::'.encode()).hexdigest()[:16]
    name = Path(audio_path).stem
    return QWEN3_CACHE / f'{name}_{key}.pt'


def main():
    parser = argparse.ArgumentParser(description='Precompile Qwen3 voice-clone prompts')
    parser.add_argument('--voices-dir', default=str(voices_dir),
                        help=f'Root voices directory (default: {voices_dir})')
    args = parser.parse_args()

    # collect all wav files
    wav_files = sorted(Path(args.voices_dir).rglob('*.wav'))
    if not wav_files:
        print('No .wav files found under', args.voices_dir)
        sys.exit(0)

    # skip already-cached
    todo = []
    for f in wav_files:
        cp = cache_path(str(f))
        if cp.exists():
            try:
                # quick sanity: file is loadable
                import torch
                torch.load(cp, map_location='cpu', weights_only=True)
                print(f'  [SKIP] {f.relative_to(args.voices_dir)} (cached)')
                continue
            except Exception:
                cp.unlink(missing_ok=True)
        todo.append(f)

    if not todo:
        print(f'\nAll {len(wav_files)} voices already cached in {QWEN3_CACHE}')
        return

    print(f'\nLoading Qwen3-TTS model ({QWEN3_REPO}) …')
    import torch
    from qwen_tts import Qwen3TTSModel

    # ponytail: try flash-attn, fall back to sdpa (built-in torch), then eager
    import torch
    kwargs = dict(device_map='auto', dtype=torch.bfloat16)
    try:
        import flash_attn  # noqa: F401
        kwargs['attn_implementation'] = 'flash_attention_2'
    except ImportError:
        try:
            torch.backends.cuda.flash_sdp_enabled()
            kwargs['attn_implementation'] = 'sdpa'
        except Exception:
            kwargs['attn_implementation'] = 'eager'
    model = Qwen3TTSModel.from_pretrained(QWEN3_REPO, **kwargs)
    print('Model loaded.\n')

    QWEN3_CACHE.mkdir(parents=True, exist_ok=True)

    ok = errors = 0
    t0 = time.time()
    for i, f in enumerate(todo, 1):
        audio_path = str(f)
        rel = f.relative_to(args.voices_dir)
        cp = cache_path(audio_path)
        print(f'  [{i}/{len(todo)}] {rel} … ', end='', flush=True)
        try:
            prompt = model.create_voice_clone_prompt(ref_audio=audio_path, ref_text=None, x_vector_only_mode=True)
            data = [
                {
                    'ref_code': p.ref_code,
                    'ref_spk_embedding': p.ref_spk_embedding,
                    'x_vector_only_mode': p.x_vector_only_mode,
                    'icl_mode': p.icl_mode,
                    'ref_text': p.ref_text,
                }
                for p in prompt
            ]
            torch.save(data, cp)
            ok += 1
            print(f'OK ({os.path.getsize(cp) / 1024:.0f} KB)')
        except Exception as e:
            errors += 1
            print(f'FAIL: {e}')

    elapsed = time.time() - t0
    print(f'\nDone: {ok} cached, {errors} failed in {elapsed:.0f}s')
    print(f'Cache: {QWEN3_CACHE}')


if __name__ == '__main__':
    main()
